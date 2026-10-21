"""GSE99039 specificity (synthetic): Holm, two-sided Q1, per-gene categories, complete case, identifiability, gate."""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("spec99039", PROJECT / "scripts/specificity_gse99039.py")
sp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sp)
needs_r = pytest.mark.skipif(shutil.which("Rscript") is None, reason="R 4.6.1 (D8) not installed")


def test_holm():
    adj = sp.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == pytest.approx({"a": 0.03, "c": 0.06, "b": 0.06})
    assert sp.holm({"a": 0.5, "b": 0.9})["b"] == 1.0


def test_contrast_samples_complete_case_and_exclusions():
    elig = pd.DataFrame({"gsm": ["G1", "G2", "G3", "G4", "G5"], "group": ["IPD", "CONTROL", "CONTROL", "IPD", "MSA"],
                         "gender": ["Male", "", "Female", "Female", "Male"], "batch": "b1", "age": ["70", "", "60", "65", "50"]})
    s, c = sp.contrast_samples(elig, {"G4"}, "IPD", False)
    assert list(s["gsm"]) == ["G1", "G3"] and c["removed_R2_COV"] == {"disease": 0, "CONTROL": 1}
    s15, _ = sp.contrast_samples(elig, set(), "IPD", True)
    assert list(s15["gsm"]) == ["G1", "G3", "G4"]


def _samples(n_batch=6, per=10, seed=0):
    rng = np.random.default_rng(seed)
    rows = [(f"G{b}_{i}", f"b{b}", int(i % 2 == 0), int(rng.integers(0, 2)), 60 + rng.normal(0, 8))
            for b in range(n_batch) for i in range(per)]
    return pd.DataFrame(rows, columns=["gsm", "batch", "case", "sex_male", "age"])


def test_identifiability_and_design_without_age():
    s = _samples()
    ident = sp.identifiability(s, False)
    assert ident["decision"] == "PROCEED" and ident["decision_checks"]["M2"]["mixed_units"] == 6
    N, names = sp.nuisance(s, False)
    assert "age_scaled" not in names and sp.nuisance(s, True)[1][1] == "age_scaled"
    d = sp.design(s, False, ident["descriptive"]["r_N"])
    assert d.coefficient == sp.COEF and d.matrix.shape[1] == ident["descriptive"]["r_N"] + 1
    one_group = s.assign(case=(s["batch"] == "b0").astype(int))           # case only on one batch: not estimable
    assert sp.identifiability(one_group, False)["decision"] == "STOP"


@needs_r
def test_q1_is_two_sided_and_signed():
    s = _samples(seed=3)
    ident = sp.identifiability(s, False)
    d = sp.design(s, False, ident["descriptive"]["r_N"])
    y = np.random.default_rng(4).normal(size=len(s)) - 0.9 * s["case"].to_numpy()   # opposite to the AD direction
    r = sp.q1(pd.Series(y, index=s["gsm"]), d)
    assert r["estimate"] < 0 and r["sign_relative_to_AD_signature"] == "opposite direction"
    assert r["p_two_sided"] < 0.05 and r["ci_high_two_sided_95"] < 0


def test_per_gene_categories():
    meas = pd.DataFrame({"lock_rank": [1, 2, 3], "entrez_gene_id": ["1", "2", "3"], "symbol": list("ABC"),
                         "direction": ["up_in_AD", "down_in_AD", "up_in_AD"], "category": "4_measurable", "measurable": True})
    fitres = pd.DataFrame({"feature_id": ["1", "2", "3"], "estimate": [0.5, 0.5, 0.01], "std_error": 0.1, "ci_low": 0, "ci_high": 1,
                           "t_statistic": [5, 5, 0.1], "df": 100.0, "p_value": [1e-6, 1e-6, 0.9]})
    pg = sp.per_gene(fitres, meas)
    assert list(pg["category"]) == ["association — same direction as AD", "association — opposite direction",
                                    "association not demonstrated"]


def test_gate_refuses_without_recorded_approvals(tmp_path, monkeypatch):
    monkeypatch.setattr(sp, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="PRECONDITIONS NOT MET"):
        sp.produce("v_test")
