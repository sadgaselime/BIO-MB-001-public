"""GSE63061 consistency runner (synthetic): measurability, coverage, W1 score, C-c / C-a statistics and the approval gate."""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[1]


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


val = load("scripts/validation_gse63061.py", "val63061")
prep = load("scripts/discovery_prep_gse63060.py", "dprep_val")
fit = load("scripts/discovery_fit_gse63060.py", "dfit_val")
needs_r = pytest.mark.skipif(shutil.which("Rscript") is None, reason="R 4.6.1 (D8) not installed")


def signature(n_up, n_down):
    ids = [str(100 + i) for i in range(n_up + n_down)]
    return pd.DataFrame({"lock_rank": range(1, len(ids) + 1), "entrez_gene_id": ids, "symbol": [f"S{i}" for i in ids],
                         "direction": ["up_in_AD"] * n_up + ["down_in_AD"] * n_down,
                         "beta_AD_minus_CTL": [0.5] * n_up + [-0.5] * n_down})


def a0_rows(cohort, entries):
    return pd.DataFrame([{"cohort": cohort, "probe_id": p, "a0_class": "eligible", "a0_gene_id": g, "in_series_matrix": sm}
                         for p, g, sm in entries])


def test_measurability_categories():
    sig = signature(2, 2)                                   # genes 100, 101, 102, 103
    a0 = pd.concat([a0_rows("GSE63061", [("p0", "100", "yes"), ("p1", "101", "no"), ("p2", "102", "yes")]),
                    a0_rows("GSE63060", [("q3", "103", "yes")])])  # 103 mapped only in the other cohort
    genes = pd.DataFrame({"A": [1.0, 5.0], "B": [2.0, 5.0]}, index=["100", "102"])
    m = val.measurability(sig, a0, "GSE63061", genes)
    assert list(m["category"]) == ["4_measurable", "2_no_eligible_probe_in_series_matrix", "3_constant_in_cohort", "1_unmapped"]


@pytest.mark.parametrize("n_lock,n_meas,met", [(28, 14, True), (28, 13, False), (4, 4, True), (4, 3, False),
                                               (8, 5, True), (8, 4, False), (0, 0, True)])
def test_coverage_rule_half_and_min5(n_lock, n_meas, met):
    meas = pd.DataFrame({"direction": ["up_in_AD"] * n_lock + ["down_in_AD"] * 10,
                         "measurable": [True] * n_meas + [False] * (n_lock - n_meas) + [True] * 10})
    cov = val.coverage(meas)
    assert cov["up_in_AD"]["met"] is met and cov["down_in_AD"]["met"] and cov["score_assessable"] is met


def test_w1_score_is_diagnosis_blind_mean_up_minus_mean_down():
    rng = np.random.default_rng(3)
    genes = pd.DataFrame(rng.normal(size=(4, 9)), index=["1", "2", "3", "4"], columns=[f"s{i}" for i in range(9)])
    meas = pd.DataFrame({"entrez_gene_id": ["1", "2", "3", "4"], "direction": ["up_in_AD", "up_in_AD", "down_in_AD", "down_in_AD"],
                         "measurable": [True, True, True, False]})
    z = (genes - genes.mean(axis=1).to_numpy()[:, None]) / genes.std(axis=1, ddof=1).to_numpy()[:, None]
    expect = (z.loc["1"] + z.loc["2"]) / 2 - z.loc["3"]
    assert np.allclose(val.w1_score(genes, meas).to_numpy(), expect.to_numpy())


def population(n_chips=5, per=8, seed=1):
    rng = np.random.default_rng(seed)
    rows = [(f"G{c}_{i}", "AD" if i % 3 else "CTL", f"C{c}", 70 + rng.normal(0, 5), int(rng.integers(0, 2)))
            for c in range(n_chips) for i in range(per)]
    df = pd.DataFrame(rows, columns=["gsm", "group", "chip", "age", "sex_male"])
    df["case_AD"] = (df["group"] == "AD").astype(int)
    return df


@needs_r
def test_c_c_matches_ols_and_bound_agrees_with_test():
    pop = population()
    design = fit.full_rank_design(pop, prep.nuisance_matrix, prep.identifiability(pop)["descriptive"]["r_N"])
    y = np.random.default_rng(4).normal(size=len(pop)) + 0.8 * pop["case_AD"].to_numpy()
    r = val.c_c(pd.Series(y, index=pop["gsm"]), design)
    X = design.matrix
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    df = len(y) - X.shape[1]
    se = np.sqrt(resid @ resid / df * np.linalg.inv(X.T @ X)[-1, -1])
    assert abs(r["estimate"] - beta[-1]) < 1e-10 and abs(r["std_error"] - se) < 1e-10 and r["df"] == df
    assert r["bound_agrees_with_test"] and r["lower_bound_one_sided_95"] < r["estimate"] < r["ci_high_two_sided_95"]


@needs_r
def test_c_a_one_sided_in_locked_direction():
    meas = pd.DataFrame({"lock_rank": [1, 2], "entrez_gene_id": ["1", "2"], "symbol": ["A", "B"],
                         "direction": ["up_in_AD", "down_in_AD"], "category": "4_measurable", "measurable": True})
    fitres = pd.DataFrame({"feature_id": ["1", "2"], "estimate": [0.4, 0.4], "std_error": [0.1, 0.1],
                           "t_statistic": [4.0, 4.0], "df": [100.0, 100.0]})
    ca = val.c_a(fitres, meas)
    # gene 1 is in its locked direction (small p); gene 2 is opposite to its locked direction (p near 1)
    assert ca.loc[0, "p_one_sided"] < 1e-3 and ca.loc[1, "p_one_sided"] > 0.999
    assert list(ca["concordant_sign"]) == [True, False] and list(ca["bound_side"]) == ["lower", "upper"]
    assert ca.loc[0, "bound_one_sided_95_unadjusted"] < 0.4 < ca.loc[1, "bound_one_sided_95_unadjusted"]


def test_gate_refuses_without_recorded_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(val, "ROOT", tmp_path)
    (tmp_path / "reports/phase3b/v7").mkdir(parents=True)
    (tmp_path / val.SAP_REL).write_text("PROPOSED DRAFT FOR REVIEW. Not approved, not frozen.\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="approvals not found in the SAP"):
        val.produce("v_test")


def test_c_b_counts_and_proportions_without_interval():
    ca = pd.DataFrame({"direction": ["up_in_AD", "up_in_AD", "down_in_AD", "down_in_AD", "down_in_AD"],
                       "concordant_sign": [True, False, True, True, False]})
    meas = pd.DataFrame({"measurable": [True] * 5})
    out = val.c_b(ca, meas, {"score_assessable": True})
    assert out["up_in_AD"] == {"measurable": 2, "concordant": 1, "discordant": 1, "proportion_concordant": 0.5}
    assert out["overall"]["concordant"] == 3 and abs(out["overall"]["proportion_concordant"] - 0.6) < 1e-12
    assert out["inferential"] is False and not any("ci" in k for d in ("up_in_AD", "down_in_AD", "overall") for k in out[d])


@needs_r
def test_pearson_fisher_z_interval_matches_closed_form():
    rng = np.random.default_rng(7)
    x = rng.normal(size=60)
    y = 0.6 * x + rng.normal(size=60)
    r = val.r_stats(["--cor"], {"input": pd.DataFrame({"x": x, "y": y})}).iloc[0]
    rr = np.corrcoef(x, y)[0, 1]
    z, se = np.arctanh(rr), 1 / np.sqrt(60 - 3)
    assert abs(r["pearson_r"] - rr) < 1e-12
    assert abs(r["ci_low"] - np.tanh(z - 1.959963984540054 * se)) < 1e-9 and abs(r["ci_high"] - np.tanh(z + 1.959963984540054 * se)) < 1e-9


def test_runner_has_no_binomial_interval_and_requires_recorded_markers():
    src = (PROJECT / "scripts/validation_gse63061.py").read_text(encoding="utf-8")
    assert "--binom" not in src and "clopper" not in src.lower()
    assert "GSE63061 descriptive methods § (2026-10-19, explicit PI instruction" in val.APPROVAL_MARKERS
