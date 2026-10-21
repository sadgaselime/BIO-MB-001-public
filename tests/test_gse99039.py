"""GSE99039 (synthetic): E-99 eligibility, C1 subject_id and title rule, R8-570a probe lists, Stage B contrast groups."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from biomarker_project import qc_r8

PROJECT = Path(__file__).resolve().parents[1]


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


el = load("scripts/eligibility_gse99039.py", "elig99039")
c1 = load("scripts/duplicate_review_c1_gse63060.py", "c1_99039")
qa = load("scripts/qc_stage_a_gse63060.py", "qca_99039")
qb = load("scripts/qc_stage_b_gse63060.py", "qcb_99039")


def _s(gsm, title, label, subject="S", sex="Female", age="NA"):
    return {"gsm": gsm, "title": title, "label": label, "sex": sex, "batch": "b1", "age": age, "subject_id": subject}


def test_eligibility_labels_as_deposited_and_identifier_rules():
    sm = {"table_columns": ["G1", "G2", "G3", "G4"],
          "samples": [_s("G1", "t1", "IPD", "L1", age="70"), _s("G2", "t2", "CONTROL", "L1"),
                      _s("G3", "t2", "HD_HD_BATCH", ""), _s("G4", "t4", "GENETIC_UNAFFECTED", "L4", sex="")]}
    rows = {r["gsm"]: r for r in el.classify(sm)["rows"]}
    assert rows["G1"]["primary_contrast_preqc"] == "case:IPD" and rows["G1"]["age"] == "70" and rows["G2"]["age"] == ""
    assert rows["G2"]["group"] == "CONTROL" and "subject_id:duplicate(C1 candidate)" in rows["G2"]["rules"]
    assert "title:duplicate(C1 candidate; title rule)" in rows["G3"]["rules"] and rows["G3"]["eligible_in_dataset_preqc"] == "True"
    assert "P1:outside_specificity_contrasts(descriptive)" in rows["G3"]["rules"] and "subject_id:missing(recorded)" in rows["G3"]["rules"]
    assert rows["G4"]["gender"] == "" and rows["G4"]["primary_contrast_preqc"] == "case:GENETIC_UNAFFECTED"


def test_c1_gse99039_categories_and_missing_identifier():
    c1.use("GSE99039")
    meta = {"identity": {"gsm": ["G1", "G2", "G3", "G4"], "array_barcode": ["t1", "t1", "t3", "t4"],
                         "participant_code": ["L1", "L1", "", ""]}, "replicate_mentions": []}
    cats = {o["link"]: o["category"] for o in c1.find_candidates(meta)}
    assert cats == {"identical array_barcode": "unresolved duplicate-review candidate (GSE99039 title rule)",
                    "identical participant_code": "D-1 candidate (identical subject_id; E-99)"}


def test_r8_multi_probe_xist_and_custom_y_list():
    rng = np.random.default_rng(1)
    sex = np.array(["F", "M"] * 10)
    x = np.where(sex == "F", 10.0, 4.0) + rng.normal(0, 0.1, 20)
    y = np.where(sex == "M", 9.0, 3.0) + rng.normal(0, 0.1, 20)
    expr = pd.DataFrame([x, x + 0.5, y, y + 0.2], index=["xa", "xb", "ya", "yb"], columns=[f"A{i}" for i in range(20)])
    rec = pd.Series(sex, index=expr.columns)
    rec.iloc[0] = "M"                                      # one discordant array
    r = qc_r8.run_r8(expr, rec, "T", xist_probes=("xa", "xb"), y_probes={"ya": "G1", "yb": "G2"})
    assert r.status == qc_r8.INFORMATIVE and r.axes["x_probes"] == ["xa", "xb"]
    assert np.allclose(r.arrays["xist_value"], (x + x + 0.5) / 2)
    assert r.arrays.set_index("array_id").loc["A0", "r8_category"] == "discordant_two_axis"
    assert qc_r8.run_r8(expr, rec, "T", xist_probes=("xa", "missing"), y_probes={"ya": "G1", "yb": "G2"}).status == qc_r8.NOT_APPLICABLE


def test_qc_configuration_for_gse99039():
    cfg = qa.CONFIG["GSE99039"]
    assert cfg["EXPECTED_SHAPE"] == (54675, 558) and len(cfg["R8_XIST"]) == 6 and len(cfg["R8_Y"]) == 18
    assert not any(p.endswith("_x_at") for p in (*cfg["R8_XIST"], *cfg["R8_Y"])) and len(set(cfg["R8_Y"].values())) == 8


def test_stage_b_uses_the_specificity_groups():
    qb.use("GSE99039")
    elig = pd.DataFrame({"gsm": ["G1", "G2", "G3"], "array_barcode": ["t1", "t2", "t3"], "group": ["IPD", "CONTROL", "MSA"],
                         "eligible_in_dataset_preqc": "True", "r5_category": "mapped", "batch": "b1"})
    audit = pd.DataFrame({"array_id": ["G1", "G2", "G3"], "r9_outcome": "passed", "r8_category": "concordant_two_axis", "flags": ""})
    out = qb.build(elig, audit, "completed — informative")
    s = dict(zip(out["summary"]["quantity"], out["summary"]["n"]))
    assert list(out["exclusion_list"]["gsm"]) == ["G3"] and s["primary population IPD (proposed, pending approval)"] == 1
    assert s["primary population CONTROL (proposed, pending approval)"] == 1 and "Q1 among IPD/GPD/GENETIC_UNAFFECTED/CONTROL" in s
