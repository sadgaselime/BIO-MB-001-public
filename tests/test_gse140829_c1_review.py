"""GSE140829 C1 review consumption (synthetic): D-2 option (c) becomes Q3 in Stage B; the review record is verified."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


qb = load("scripts/qc_stage_b_gse63060.py", "qcb_c1r")


def test_q3_excludes_only_the_named_arrays_from_the_primary_population():
    elig = pd.DataFrame({"gsm": ["G1", "G2", "G3"], "array_barcode": ["1_A", "1_B", "1_C"], "group": ["AD", "CTL", "AD"],
                         "eligible_in_dataset_preqc": "True", "r5_category": "mapped", "batch": "20"})
    audit = pd.DataFrame({"array_id": ["G1", "G2", "G3"], "r9_outcome": "passed", "r8_category": "concordant_two_axis", "flags": ""})
    out = qb.build(elig, audit, "completed — informative", frozenset({"G3"}))
    ex = out["exclusion_list"]
    assert list(ex["gsm"]) == ["G3"] and ex.iloc[0]["exclusion_tiers"] == "Q3"
    s = dict(zip(out["summary"]["quantity"], out["summary"]["n"]))
    assert s["Q3 (D-2 option (c))"] == 1 and s["primary population AD (proposed, pending approval)"] == 1
    assert "Q3 (D-2 option (c))" not in dict(zip(*qb.build(elig, audit, "completed — informative")["summary"].T.values))


def _repo(tmp, sap_text, manifest=b"{}"):
    (tmp / "reports/phase3b/v7").mkdir(parents=True)
    (tmp / "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md").write_text(sap_text, encoding="utf-8")
    dup = tmp / "reports/duplicate_review/GSE140829/c1_v1"
    dup.mkdir(parents=True)
    (dup / "manifest.json").write_bytes(manifest)
    rev = tmp / qb.REVIEW_REL
    rev.mkdir(parents=True)
    rec = {"c1_manifest_sha256": hashlib.sha256(manifest).hexdigest(), "status": "complete: C1 review recorded",
           "decisions": {"D-2_option_c_Q3": {"gsms": ["G3"]}}}
    b = (json.dumps(rec) + "\n").encode()
    (rev / "c1_review_decision.json").write_bytes(b)
    (rev / "SHA256SUMS").write_text(f"{hashlib.sha256(b).hexdigest()}  c1_review_decision.json\n")
    return "reports/duplicate_review/GSE140829/c1_v1"


def test_review_record_is_verified(tmp_path):
    rel = _repo(tmp_path, "… GSE140829 C1 review § …")
    rec, probs = qb.c1_review(tmp_path, rel)
    assert probs == [] and rec["decisions"]["D-2_option_c_Q3"]["gsms"] == ["G3"]
    (tmp_path / rel / "manifest.json").write_bytes(b'{"changed": 1}')            # C1 output no longer the reviewed one
    assert qb.c1_review(tmp_path, rel)[1]


def test_review_record_requires_the_sap_record(tmp_path):
    rel = _repo(tmp_path, "no review recorded")
    assert qb.c1_review(tmp_path, rel)[1]
