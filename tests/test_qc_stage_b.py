"""QC Stage B for GSE63060 (synthetic): tier assignment, counts and the rule-applied exclusion list."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

from biomarker_project import code_identity as ci
from test_annotation_lifecycle_integration import TrackedStub
from test_run_identity_lifecycle import make_repo

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qcb", PROJECT / "scripts/qc_stage_b_gse63060.py")
qcb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qcb)

ELIG = pd.DataFrame({"gsm": ["G1", "G2", "G3", "G4", "G5"], "array_barcode": ["C1_A", "C1_B", "C2_A", "C2_B", "C2_C"],
                     "group": ["AD", "CTL", "MCI", "AD", "CTL"], "r5_category": ["mapped"] * 5,
                     "eligible_in_dataset_preqc": ["True"] * 5})
AUDIT = pd.DataFrame({"array_id": ["G1", "G2", "G3", "G4", "G5"],
                      "r8_category": ["discordant_two_axis", "concordant_two_axis", "discordant_two_axis", "ambiguous", "concordant_two_axis"],
                      "r9_outcome": ["passed", "flagged", "passed", "passed", "numerical_failure"],
                      "flags": ["", "F1(k=3)", "", "F3", ""]})


def test_tiers_follow_the_approved_policies():
    t = qcb.build(ELIG, AUDIT, "completed — informative")
    ex = t["exclusion_list"].set_index("gsm")
    assert ex.loc["G1", "exclusion_tiers"] == "Q1" and ex.loc["G3", "exclusion_tiers"] == "P1;Q1"
    assert ex.loc["G5", "exclusion_tiers"] == "P3" and set(ex.index) == {"G1", "G3", "G5"}
    assert (ex["status"] == qcb.STATUS).all()
    s = dict(zip(t["summary"]["quantity"], t["summary"]["n"]))
    assert s["primary population AD (proposed, pending approval)"] == 1 and s["primary population CTL (proposed, pending approval)"] == 1
    assert set(t["retained_flags"]["gsm"]) == {"G2", "G4"}  # flags retained, never exclusions


def test_q1_requires_informative_r8():
    t = qcb.build(ELIG, AUDIT, "completed — uninformative")
    assert not t["exclusion_list"]["exclusion_tiers"].str.contains("Q1").any()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    monkeypatch.setattr(qcb, "ROOT", root)
    monkeypatch.setattr(qcb, "REQUIRE_VENV", False)
    monkeypatch.setattr(qcb, "REQUIRE_EXECUTED_CODE", False)
    return root


def build_inputs(root, with_qc=True):
    stub = TrackedStub()
    ci.run_with_identity(root, root / qcb.ELIG_REL, lambda s: ({"eligibility_log.tsv": ELIG.to_csv(sep="\t", index=False).encode()}, {}),
                         executed_code=stub)
    ci.run_with_identity(root, root / qcb.DUP_REL, lambda s: ({"duplicate_review_log_c1.json": b"{}"}, {}), executed_code=stub)
    if with_qc:
        ci.run_with_identity(root, root / qcb.QC_REL, lambda s: ({"qc_audit.tsv": AUDIT.to_csv(sep="\t", index=False).encode()},
                                                                 {"cohort_status": {"r8_status": "completed — informative"}}),
                             executed_code=stub)


def test_end_to_end_and_determinism(repo):
    build_inputs(repo)
    assert qcb.main(["--version", "v1"]) == 0
    d = repo / qcb.OUT_REL / "v1"
    assert ci.is_accepted(d)
    m = json.loads((d / "manifest.json").read_text())
    assert m["summary"]["Q1"] == 2 and m["summary"]["P3"] == 1 and "AWAITING PI" in m["status"]


def test_requires_qc_stage_a(repo):
    build_inputs(repo, with_qc=False)
    assert qcb.main(["--version", "v1"]) == 1 and not (repo / qcb.OUT_REL / "v1").exists()
