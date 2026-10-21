"""Lifecycle integration of the annotation generators and the future pin builder (synthetic only).

Each script's real computation (``produce``) is replaced by a synthetic stand-in and every path points into a
temporary git repository, so no Series Matrix, annotation archive or other study input is read.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from biomarker_project import code_identity as ci
from test_run_identity_lifecycle import ENV, git, make_repo

PROJECT = Path(__file__).resolve().parents[1]


def load_script(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, PROJECT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCRIPTS = {  # key -> (script, module name, artifact base, manifest name, tables, validation shape)
    "gpl570_option_a": ("scripts/annotation_gpl570_option_a_counts.py", "gpl570_lc", "reports/annotation_audit/gpl570_option_a",
                        "counts_manifest.json", ("probe_set_classification.tsv",), {"status": "OK"}),
    "illumina_a0": ("scripts/annotation_illumina_a0_classification.py", "a0_lc", "reports/annotation_audit/illumina_a0",
                    "manifest.json", ("a0_probe_classification.tsv", "a0_counts.tsv", "a0_discordant_probes.tsv"),
                    [{"check": "synthetic", "pass": True}]),
    "c15_cohort_probe_presence": ("scripts/c15_cohort_probe_presence.py", "c15_lc", "reports/annotation_audit/c15_cohort_probe_presence",
                                  "manifest.json", ("probe_presence.tsv", "presence_counts.tsv"), [{"check": "synthetic", "pass": True}]),
}


def table_bytes(key, t):
    return f"synthetic\t{key}\t{t}\n1\t2\n".encode()


def write_v1(repo, key):
    _, _, base, _, tables, _ = SCRIPTS[key]
    d = repo / base / "v1"
    d.mkdir(parents=True)
    for t in tables:
        (d / t).write_bytes(table_bytes(key, t))


def patched(monkeypatch, repo, key, produce):
    script, modname, base, *_ = SCRIPTS[key]
    mod = load_script(script, modname)
    monkeypatch.setattr(mod, "ROOT", repo)
    monkeypatch.setattr(mod, "OUT", repo / base)
    monkeypatch.setattr(mod, "REQUIRE_VENV", False)
    monkeypatch.setattr(mod, "produce", produce)
    return mod


def synthetic_produce(key, override=None):
    _, _, _, _, tables, validation = SCRIPTS[key]

    def produce(version):
        files = {t: table_bytes(key, t) for t in tables}
        if key == "c15_cohort_probe_presence":
            files["REPORT.md"] = f"synthetic report {version}\n".encode()
        files.update(override or {})
        return files, {"status": "synthetic", "validation": validation}
    return produce


@pytest.fixture
def repo(tmp_path):
    return make_repo(tmp_path / "repo")


@pytest.mark.parametrize("key", list(SCRIPTS))
def test_generator_v2_equivalent_to_v1_is_accepted(repo, monkeypatch, key):
    write_v1(repo, key)
    mod = patched(monkeypatch, repo, key, synthetic_produce(key))
    assert mod.main(["--version", "v2"]) == 0
    _, _, base, mname, tables, _ = SCRIPTS[key]
    out = repo / base / "v2"
    m = json.loads((out / mname).read_text())
    assert ci.is_accepted(out, mname, require_equivalence=True)
    assert m["equivalence"]["reference"] == f"{base}/v1" and set(m["equivalence"]["tables"]) == set(tables)
    for t in tables:
        assert (out / t).read_bytes() == (repo / base / "v1" / t).read_bytes()


@pytest.mark.parametrize("key", list(SCRIPTS))
def test_generator_v2_differing_from_v1_fails_closed(repo, monkeypatch, key):
    write_v1(repo, key)
    first_table = SCRIPTS[key][4][0]
    mod = patched(monkeypatch, repo, key, synthetic_produce(key, {first_table: b"different\n"}))
    assert mod.main(["--version", "v2"]) == 1
    base = repo / SCRIPTS[key][2]
    assert not (base / "v2").exists()
    failed = [p for p in base.iterdir() if p.name.startswith("v2.FAILED-")]
    assert len(failed) == 1 and (failed[0] / ci.FAILED_FILENAME).exists()


@pytest.mark.parametrize("key", list(SCRIPTS))
def test_generator_refuses_existing_version_and_requires_venv(repo, monkeypatch, key):
    write_v1(repo, key)
    mod = patched(monkeypatch, repo, key, synthetic_produce(key))
    assert mod.main(["--version", "v1"]) == 1  # v1 exists: never overwritten
    monkeypatch.setattr(mod, "REQUIRE_VENV", True)
    assert mod.main(["--version", "v3"]) == 1  # the tmp repo has no .venv
    assert not any(p.name.startswith("v3") for p in (repo / SCRIPTS[key][2]).iterdir())


# ----------------------------------------------------------------------------- future pin builder (synthetic)

ARCHIVE_NAMES = ["hgu133plus2.db_3.13.0.tar.gz", "illuminaHumanv3.db_1.26.0.tar.gz",
                 "illuminaHumanv4.db_1.26.0.tar.gz", "org.Hs.eg.db_3.23.1.tar.gz"]


def build_pin_tree(repo, monkeypatch, equivalence=True):
    """Synthetic upstream v1/v2 artifacts, archives, frozen gene-history input and SAP stand-in."""
    for key, (script, *_rest) in SCRIPTS.items():
        p = repo / script
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# synthetic stand-in for {script}\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "synthetic scripts")
    ref = repo / "reference/bioconductor_3.23"
    ref.mkdir(parents=True)
    entries = []
    for n in ARCHIVE_NAMES:
        (ref / n).write_bytes(f"synthetic archive {n}".encode())
        entries.append({"file": n, "sha256": hashlib.sha256((ref / n).read_bytes()).hexdigest()})
    (ref / "download_manifest.json").write_text(json.dumps({"files": entries}))
    gh = repo / "reports/annotation_audit/ncbi_gene_history/v1"
    gh.mkdir(parents=True)
    (gh / "gene_history_reconciliation.tsv").write_bytes(b"synthetic gene history\n")
    (gh / "reconciliation_manifest.json").write_text(json.dumps({"determinism": {"output_sha256": {
        "gene_history_reconciliation.tsv": hashlib.sha256(b"synthetic gene history\n").hexdigest()}}}))
    sap = repo / "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
    sap.parent.mkdir(parents=True)
    sap.write_text("# SAP\n\n**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen.**\n")
    expected = {}
    for key, (_, _, base, mname, tables, validation) in SCRIPTS.items():
        write_v1(repo, key)
        ci.run_with_identity(repo, repo / base / "v2", lambda s, k=key: (synthetic_produce(k)("v2")[0], {"validation": SCRIPTS[k][5]}),
                             manifest_name=mname, equivalent_to=(repo / base / "v1") if equivalence else None,
                             equivalent_files=list(tables))
        if key != "c15_cohort_probe_presence":
            for t in tables:
                expected[f"{key}/{t}"] = hashlib.sha256(table_bytes(key, t)).hexdigest()
    pin = load_script("scripts/annotation_pin.py", "pin_lc")
    monkeypatch.setattr(pin, "ROOT", repo)
    monkeypatch.setattr(pin, "REQUIRE_VENV", False)
    monkeypatch.setattr(pin, "EXPECTED_TABLE_SHA256", expected)
    return pin


def pin_dir(repo):
    return repo / "reports/annotation_audit/annotation_pin"


def test_pin_builder_end_to_end_synthetic(repo, monkeypatch):
    pin = build_pin_tree(repo, monkeypatch)
    assert pin.main(["--version", "v1", "--authorization", "synthetic test only"]) == 0
    out = pin_dir(repo) / "v1"
    assert ci.is_accepted(out)
    rec = json.loads((out / "annotation_pin_record.json").read_text())
    assert set(rec["upstream"]) == set(SCRIPTS) and set(rec["archives"]) == set(ARCHIVE_NAMES)
    assert rec["authorization"] == "synthetic test only"
    assert rec["sap"]["status_line"] == "**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen.**"
    assert "cannot be rebuilt" in rec["frozen_inputs"]["gene_history_v1"]["note"]
    assert set(rec["mapping_rules"]) == {"D6-F", "D6-G"}
    assert all(v for v in rec["d8_environment_records"].values())
    for key, u in rec["upstream"].items():
        base, mname = SCRIPTS[key][2], SCRIPTS[key][3]
        m = json.loads((repo / base / "v2" / mname).read_text())
        assert u["identity_record_sha256"] == m["identity"]["record_sha256"]
        assert u["manifest_sha256"] == hashlib.sha256((repo / base / "v2" / mname).read_bytes()).hexdigest()
        assert u["generating_script_sha256"] and u["equivalence_reference"] == f"{base}/v1"
    pm = json.loads((out / "manifest.json").read_text())
    assert pm["output_sha256"]["annotation_pin_record.json"] == hashlib.sha256(
        (out / "annotation_pin_record.json").read_bytes()).hexdigest()


def test_pin_builder_requires_authorization(repo, monkeypatch):
    pin = build_pin_tree(repo, monkeypatch)
    with pytest.raises(SystemExit):
        pin.main(["--version", "v1"])
    assert pin.main(["--version", "v1", "--authorization", "  "]) == 2
    assert not pin_dir(repo).exists()


@pytest.mark.parametrize("damage", ["missing", "tampered", "failed_only", "no_equivalence"])
def test_pin_builder_rejects_unaccepted_upstream(repo, monkeypatch, damage):
    pin = build_pin_tree(repo, monkeypatch, equivalence=(damage != "no_equivalence"))
    a0 = repo / SCRIPTS["illumina_a0"][2] / "v2"
    if damage == "missing":
        for p in sorted(a0.iterdir()):
            p.unlink()
        a0.rmdir()
    elif damage == "tampered":
        (a0 / "a0_counts.tsv").write_bytes(b"tampered\n")
    elif damage == "failed_only":
        a0.rename(a0.with_name("v2.FAILED-synthetic"))
    assert pin.main(["--version", "v1", "--authorization", "synthetic"]) == 1
    assert not pin_dir(repo).exists()  # refused before anything was created


def test_pin_builder_rejects_unexpected_table_hash_and_archive_mismatch(repo, monkeypatch):
    pin = build_pin_tree(repo, monkeypatch)
    monkeypatch.setattr(pin, "EXPECTED_TABLE_SHA256", {**pin.EXPECTED_TABLE_SHA256,
                                                       "gpl570_option_a/probe_set_classification.tsv": "0" * 64})
    assert pin.main(["--version", "v1", "--authorization", "synthetic"]) == 1
    pin2 = build_pin_tree(make_repo(repo.parent / "repo2"), monkeypatch)
    (repo.parent / "repo2/reference/bioconductor_3.23" / ARCHIVE_NAMES[0]).write_bytes(b"changed")
    assert pin2.main(["--version", "v1", "--authorization", "synthetic"]) == 1
    assert not pin_dir(repo).exists() and not pin_dir(repo.parent / "repo2").exists()


def test_pin_builder_rejects_environment_change_since_upstream(repo, monkeypatch):
    pin = build_pin_tree(repo, monkeypatch)
    (repo / ENV[0]).write_text("@EXPLICIT changed\n")
    assert pin.main(["--version", "v1", "--authorization", "synthetic"]) == 1
    assert not pin_dir(repo).exists()


def test_pin_builder_refuses_overwrite(repo, monkeypatch):
    pin = build_pin_tree(repo, monkeypatch)
    assert pin.main(["--version", "v1", "--authorization", "synthetic"]) == 0
    assert pin.main(["--version", "v1", "--authorization", "synthetic"]) == 1
    assert sorted(p.name for p in pin_dir(repo).iterdir()) == ["v1"]
