"""Pipeline-level tests: report generation, failure handling and repeat-run safety (all offline)."""
import hashlib
import json
import os
from pathlib import Path

import pytest

from biomarker_project.audit_pipeline import AuditOptions, ProjectPaths, run_audits
from biomarker_project.config import load_config
from biomarker_project.geo_client import GeoClient
from biomarker_project.reporting import AUDIT_FAILED, AUDIT_INCOMPLETE, AUDIT_REVIEW, determine_audit_status

from conftest import ACC, FIXTURES, FakeSession


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _run(root, accessions, offline=True, session=None):
    cfg = load_config(root / "config" / "datasets.yaml")
    client = GeoClient(cfg.settings, offline=offline, session=session, sleep=lambda s: None)
    return run_audits(cfg, accessions, ProjectPaths(root), AuditOptions(offline=offline), argv=["test"], client=client)


def test_offline_audit_produces_truthful_reports(mini_project):
    out = _run(mini_project, [ACC])
    r = out["results"][ACC]
    rep = mini_project / "reports" / "dataset_audit" / ACC
    assert (rep / "audit_report.json").exists() and (rep / "audit_report.md").exists()
    assert r["audit_status"] == AUDIT_REVIEW  # issues exist: S5 missing label, S6 expression-only, ...
    assert r["network_used"] is False
    recon = {x["file"]: x["summary"] for x in r["reconciliation"]}
    sm = recon[f"{ACC}_series_matrix.txt.gz"]
    assert sm["n_matched"] == 5 and sm["exact_one_to_one"]
    sup = recon[f"{ACC}_normalized.txt.gz"]
    assert sup["left_only"] == ["S6"] and sup["right_only"] == ["S5"]
    assert sup["group_counts_matched"] == {"AD": 2, "AMBIGUOUS": 1, "HC": 1}
    conc = r["concordance"][0]
    assert conc["status"] == "IDENTICAL_VALUES" and conc["n_shared_samples"] == 4
    statuses = {f["status"] for f in r["findings"]}
    assert statuses <= {"VERIFIED", "REPORTED", "UNRESOLVED", "FAILED"}
    assert "REPORTED" in statuses and "UNRESOLVED" in statuses
    lead = r["reported_leads"][0]
    assert lead["checked_ids"][0] == {"id": "S6", "found_in_phenotype_fields": [],
                                      "found_in_expression_files": [f"{ACC}_normalized.txt.gz"]}
    assert r["run"]["config_path"] == "config/datasets.yaml"
    assert not Path(r["run"]["cwd"]).is_absolute(), "report must not embed absolute local paths"
    raw_manifest = json.loads((mini_project / "data" / "raw" / ACC / "download_manifest.json").read_text())
    assert all(not e["current"]["path"].startswith("/") for e in raw_manifest["files"].values())
    md = (rep / "audit_report.md").read_text()
    assert "PASS" not in md.replace("PASS status", "")
    for section in ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6.", "## 7.", "## 8.", "## 9.", "## 10.", "## 11."):
        assert section in md
    # proposed exclusions are recorded separately and never applied
    prop = (rep / "proposed_exclusions.csv").read_text()
    assert "PROPOSED_FOR_REVIEW_NOT_APPLIED" in prop
    ph = (mini_project / "data" / "processed" / ACC / "phenotype_table.tsv").read_text().splitlines()
    assert len(ph) == 1 + 5


def test_repeated_runs_do_not_overwrite_or_duplicate(mini_project):
    raw = mini_project / "data" / "raw" / ACC
    meta = mini_project / "data" / "metadata" / ACC
    files = sorted(raw.glob("*.gz")) + sorted(meta.glob("*.soft.txt"))
    before = {p: (_sha(p), p.stat().st_mtime_ns) for p in files}
    _run(mini_project, [ACC])
    first_listing = sorted(p.name for p in raw.iterdir())
    first_report = json.loads((mini_project / "reports" / "dataset_audit" / ACC / "audit_report.json").read_text())
    _run(mini_project, [ACC])
    after = {p: (_sha(p), p.stat().st_mtime_ns) for p in files}
    assert before == after, "raw inputs must be byte-identical and untouched after repeat runs"
    assert sorted(p.name for p in raw.iterdir()) == first_listing, "no duplicate or temporary files"
    manifest = json.loads((raw / "download_manifest.json").read_text())
    for name, entry in manifest["files"].items():
        assert len(entry["history"]) == 2 and entry["current"]["sha256"] == _sha(raw / name)
    assert entry["current"]["status"] == "REUSED_VERIFIED_AGAINST_MANIFEST"
    second = json.loads((mini_project / "reports" / "dataset_audit" / ACC / "audit_report.json").read_text())
    assert second["run"]["run_id"] != first_report["run"]["run_id"]
    hist = [json.loads(x) for x in (mini_project / "reports" / "logs" / "run_history.jsonl").read_text().strip().splitlines()]
    assert [h["event"] for h in hist] == ["STARTED", "FINISHED", "STARTED", "FINISHED"]


def test_tampered_raw_file_is_flagged_not_overwritten(mini_project):
    _run(mini_project, [ACC])
    target = mini_project / "data" / "raw" / ACC / f"{ACC}_normalized.txt.gz"
    os.chmod(target, 0o644)
    target.write_bytes(target.read_bytes() + b"")  # same content -> still fine
    import gzip
    with gzip.open(FIXTURES / "normalized.txt.gz", "rt") as fh:
        text = fh.read().replace("6.0", "6.5")
    with gzip.open(target, "wt") as fh:
        fh.write(text)
    tampered_sha = _sha(target)
    r = _run(mini_project, [ACC])["results"][ACC]
    f = next(x for x in r["files"] if x["name"] == target.name)
    assert f["retrieval"]["status"] == "CONFLICT_EXISTING_FILE_DIFFERS"
    assert _sha(target) == tampered_sha
    assert r["audit_status"] == AUDIT_INCOMPLETE


def test_report_generated_when_download_fails(mini_project):
    # Online run where every request fails (simulated): metadata cache removed so nothing is available.
    for p in (mini_project / "data" / "metadata" / ACC).iterdir():
        p.unlink()
    out = _run(mini_project, [ACC], offline=False, session=FakeSession(raise_all=True))
    r = out["results"][ACC]
    assert r["audit_status"] == AUDIT_FAILED
    rep = mini_project / "reports" / "dataset_audit" / ACC
    data = json.loads((rep / "audit_report.json").read_text())
    assert data["audit_status"] == AUDIT_FAILED
    assert any(f["status"] == "FAILED" for f in data["findings"])
    assert "FAILED" in (rep / "audit_report.md").read_text()
    summary = (mini_project / "reports" / "dataset_audit" / "audit_summary.md").read_text()
    assert ACC in summary and "FAILED" in summary


def test_one_failed_dataset_does_not_block_others(mini_project):
    cfg = load_config(mini_project / "config" / "datasets.yaml")
    client = GeoClient(cfg.settings, offline=False, session=None)
    # Serve GSE1000002 fully from fake routes; GSE1000001 metadata is cached locally, its files 404.
    acc2 = "GSE1000002"
    samples = "\n".join(f"^SAMPLE = GSM80000{i}\n!Sample_title = A{i}\n!Sample_geo_accession = GSM80000{i}\n"
                        f"!Sample_characteristics_ch1 = status: {'AD' if i % 2 else 'CTL'}\n!Sample_description = Q0{i}\n"
                        f"!Sample_platform_id = GPL11154" for i in range(1, 4)) + "\n"
    series = (f"^SERIES = {acc2}\n!Series_title = Synthetic RNA-seq\n!Series_type = Expression profiling by high throughput "
              f"sequencing\n!Series_platform_id = GPL11154\n" + "".join(f"!Series_sample_id = GSM80000{i}\n" for i in range(1, 4)))
    routes = {
        client.query_url(acc2, "self"): series.encode(),
        client.query_url(acc2, "gsm"): samples.encode(),
        client.query_url("GPL11154", "self"): b"^PLATFORM = GPL11154\n!Platform_title = Synthetic sequencer\n",
        client.file_url(acc2, "suppl", "GSE1000002_counts.txt.gz"): (FIXTURES / "counts.txt.gz").read_bytes(),
    }
    # Remove GSE1000001 raw files so its downloads are attempted and fail (404).
    for p in (mini_project / "data" / "raw" / ACC).iterdir():
        p.unlink()
    out = _run(mini_project, [ACC, acc2], offline=False, session=FakeSession(routes))
    assert out["results"][ACC]["audit_status"] == AUDIT_INCOMPLETE
    r2 = out["results"][acc2]
    assert r2["audit_status"] in (AUDIT_REVIEW, "COMPLETE_NO_ISSUES_DETECTED")
    f2 = r2["files"][0]
    assert f2["retrieval"]["status"] == "DOWNLOADED" and f2["processing"]["state"] == "NON_NORMALIZED"
    assert r2["reconciliation"][0]["summary"]["n_matched"] == 3
    downloaded = mini_project / "data" / "raw" / acc2 / "GSE1000002_counts.txt.gz"
    assert not os.access(downloaded, os.W_OK), "completed raw downloads are read-only"
    overlap = json.loads((mini_project / "reports" / "dataset_audit" / "overlap_checks.json").read_text())
    assert overlap["checks"][0]["status"] == "NO_SHARED_IDENTIFIERS_FOUND"
    assert "does NOT establish" in overlap["checks"][0]["detail"]


def test_status_never_pass_and_incomplete_when_file_missing():
    base = {"metadata": {"sample_records_available": True}, "steps": [], "issues": []}
    st, _ = determine_audit_status(dict(base, files=[{"name": "x", "requested": True,
                                                       "retrieval": {"available_locally": False, "status": "SKIPPED_TOO_LARGE"}}]))
    assert st == AUDIT_INCOMPLETE
    st, _ = determine_audit_status(dict(base, files=[{"name": "x", "requested": True,
                                                       "retrieval": {"available_locally": True},
                                                       "inspection": {"status": "MALFORMED"}}]))
    assert st == AUDIT_INCOMPLETE
    st, _ = determine_audit_status({"metadata": {"sample_records_available": False}})
    assert st == AUDIT_FAILED
    assert "PASS" not in {AUDIT_FAILED, AUDIT_INCOMPLETE, AUDIT_REVIEW}


def test_offline_mode_never_touches_network(mini_project):
    session = FakeSession(raise_all=True)
    cfg = load_config(mini_project / "config" / "datasets.yaml")
    client = GeoClient(cfg.settings, offline=True, session=session)
    run_audits(cfg, [ACC], ProjectPaths(mini_project), AuditOptions(offline=True), argv=["t"], client=client)
    assert session.calls == []
