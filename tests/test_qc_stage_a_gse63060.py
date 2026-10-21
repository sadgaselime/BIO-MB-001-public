"""GSE63060 QC Stage A runner (synthetic): fake Series Matrix with XIST and Y probes, accepted fake prerequisite
outputs, in a temporary git repository. No project data are read."""
from __future__ import annotations

import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from biomarker_project import code_identity as ci
from biomarker_project.qc_r8 import XIST_PROBE, Y_PROBES
from test_annotation_lifecycle_integration import TrackedStub
from test_run_identity_lifecycle import make_repo

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qcg", PROJECT / "scripts/qc_stage_a_gse63060.py")
qcg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qcg)

N = 24


def build(root: Path, dup_status="complete: no C1 candidates; no reviewer decision required", drop_gsm=False):
    rng = np.random.default_rng(7)
    gsms = [f"GSM{i:03d}" for i in range(N)]
    sexes = ["Female" if i % 2 == 0 else "Male" for i in range(N)]
    probes = [XIST_PROBE] + list(Y_PROBES)[:4] + [f"P{j}" for j in range(60)]
    rows = []
    for p in probes:
        if p == XIST_PROBE:
            v = [12.0 + rng.normal(0, 0.2) if s == "Female" else 6.0 + rng.normal(0, 0.2) for s in sexes]
        elif p in Y_PROBES:
            v = [5.0 + rng.normal(0, 0.2) if s == "Female" else 11.0 + rng.normal(0, 0.2) for s in sexes]
        else:
            v = list(8.0 + rng.normal(0, 1.0, N))
        rows.append(f'"{p}"\t' + "\t".join(f"{x:.6f}" for x in v))
    header_gsms = gsms[:-1] if drop_gsm else gsms
    if drop_gsm:
        rows = ["\t".join(r.split("\t")[:-1]) for r in rows]
    lines = ['!Sample_geo_accession\t' + "\t".join(f'"{g}"' for g in header_gsms), "!series_matrix_table_begin",
             '"ID_REF"\t' + "\t".join(f'"{g}"' for g in header_gsms), *rows, "!series_matrix_table_end"]
    b = gzip.compress(("\n".join(lines) + "\n").encode())
    raw = root / "data/raw/GSE63060"
    raw.mkdir(parents=True)
    (raw / qcg.SM_NAME).write_bytes(b)
    (raw / "download_manifest.json").write_text(json.dumps({"files": {qcg.SM_NAME: {"current": {"sha256": hashlib.sha256(b).hexdigest()}}}}))
    log = "gsm\tgroup\tgender\n" + "".join(f"{g}\t{'AD' if i % 3 else 'CTL'}\t{s}\n" for i, (g, s) in enumerate(zip(gsms, sexes)))
    stub = TrackedStub()
    ci.run_with_identity(root, root / qcg.PIN_REL, lambda s: ({"annotation_pin_record.json": b"{}\n"}, {}), executed_code=stub)
    ci.run_with_identity(root, root / qcg.ELIG_REL, lambda s: ({"eligibility_log.tsv": log.encode()}, {}), executed_code=stub)
    ci.run_with_identity(root, root / qcg.DUP_REL, lambda s: ({"duplicate_review_log_c1.json": json.dumps({"status": dup_status}).encode()}, {}),
                         executed_code=stub)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    monkeypatch.setattr(qcg, "ROOT", root)
    monkeypatch.setattr(qcg, "REQUIRE_VENV", False)
    monkeypatch.setattr(qcg, "REQUIRE_EXECUTED_CODE", False)
    monkeypatch.setattr(qcg, "EXPECTED_SHAPE", (65, N))
    return root


def out(root):
    return root / qcg.OUT_REL / "v1"


def test_end_to_end_records_candidates_only(repo):
    build(repo)
    assert qcg.main(["--version", "v1"]) == 0
    d = out(repo)
    assert ci.is_accepted(d)
    m = json.loads((d / "manifest.json").read_text())
    assert all(c["pass"] for c in m["validation"]) and m["authorization"] == qcg.AUTHORIZATION
    assert m["cohort_status"]["stage_a_outputs_usable_downstream"] is False
    assert m["cohort_status"]["r8_status"] == "completed — informative"
    audit = list(csv.DictReader(open(d / "qc_audit.tsv"), delimiter="\t"))
    assert len(audit) == N and {r["exclusion_applied"] for r in audit} == {"False"}
    assert not qcg.DIAGNOSIS_COLUMNS & set(audit[0]) and "AD" not in (d / "qc_audit.tsv").read_text().split()


def test_requires_complete_duplicate_review(repo):
    build(repo, dup_status="C1 candidates found: review pending")
    assert qcg.main(["--version", "v1"]) == 1 and not out(repo).exists()


def test_universe_mismatch_fails(repo):
    build(repo, drop_gsm=True)
    assert qcg.main(["--version", "v1"]) == 1 and not out(repo).exists()
