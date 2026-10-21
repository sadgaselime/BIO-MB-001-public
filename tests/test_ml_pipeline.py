"""Exploratory ML pipeline (synthetic only): the protocol's leakage tests (ML protocol M1), DeLong, apply mode and gates."""
from __future__ import annotations

import importlib.util
import io
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ml63060", PROJECT / "scripts/ml_gse63060.py")
ml = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ml)
needs_r = pytest.mark.skipif(shutil.which("Rscript") is None, reason="R 4.6.1 (D8) not installed")
FAST = {"seed": 11, "n_outer": 4, "n_inner": 3, "n_repeats": 3, "kgrid": "5,10,20", "alpha_en": 0.5, "b2_genes": 20,
        "n_lambda": 30, "use_sex": "true", "n_perm": 0}


def cohort(n_chips=14, per=10, genes=150, signal=0.0, chip_confound=0.0, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for c in range(n_chips):
        frac = 0.35 + 0.5 * (c % 2)                    # chips alternate low / high AD fraction
        for i in range(per):
            rows.append((f"A{c}_{i}", f"C{c:02d}", int(rng.random() < frac), 70 + rng.normal(0, 5), int(rng.integers(0, 2))))
    P = pd.DataFrame(rows, columns=["array", "chip", "y", "age", "sex_male"])
    E = rng.normal(0, 1, (genes, len(P)))
    E[:8] += signal * P["y"].to_numpy()                # within-chip AD effect in 8 genes
    chip_frac = P.groupby("chip")["y"].transform("mean").to_numpy()
    E += chip_confound * chip_frac                     # chip offset correlated with the chip's AD fraction (batch confound)
    return pd.DataFrame(E, index=[str(1000 + g) for g in range(genes)], columns=P["array"]), P


def tab(b):
    return pd.read_csv(io.BytesIO(b), sep="\t")


def ridge_auc(files):
    m = tab(files["repeat_metrics.tsv"])
    return float(m.loc[m["model"] == "ridge", "auroc"].mean())


@needs_r
def test_random_labels_give_chance_auc():
    E, P = cohort(seed=1)
    assert 0.3 < ridge_auc(ml.engine("cv", E, P, FAST)) < 0.7


@needs_r
def test_chip_label_confound_is_not_exploited():
    E, P = cohort(chip_confound=3.0, seed=2)          # strong batch-by-label confound, no within-chip signal
    assert ridge_auc(ml.engine("cv", E, P, FAST)) < 0.7


@needs_r
def test_planted_signal_is_found():
    E, P = cohort(signal=1.2, seed=3)
    f = ml.engine("cv", E, P, FAST)
    m = tab(f["repeat_metrics.tsv"]).groupby("model")["auroc"].mean()
    assert m["ridge"] > 0.8 and m["B2_equal_weight"] > 0.6 and np.isnan(m["B0_prevalence"])


@needs_r
def test_test_fold_expression_never_reaches_training_choices():
    E, P = cohort(signal=0.8, seed=4)
    a = tab(ml.engine("cv", E, P, FAST)["fold_choices.tsv"])
    row = a[(a.repeat_id == 1) & (a.fold == 1)].iloc[0]
    test_chips = row["test_chips"].split(";")
    E2 = E.copy()
    cols = P.loc[P["chip"].isin(test_chips), "array"]
    E2[cols] = E2[cols] * 3 + np.random.default_rng(9).normal(0, 2, (E.shape[0], len(cols)))
    b = tab(ml.engine("cv", E2, P, FAST)["fold_choices.tsv"])
    rowb = b[(b.repeat_id == 1) & (b.fold == 1)].iloc[0]
    for c in ("k", "lambda", "threshold", "inner_deviance", "en_lambda", "n_train"):
        assert row[c] == rowb[c], c


def _delong_py(y, s):
    X, Y = s[y == 1], s[y == 0]
    psi = (X[:, None] > Y[None, :]) + 0.5 * (X[:, None] == Y[None, :])
    v10, v01 = psi.mean(axis=1), psi.mean(axis=0)
    return v10.mean(), np.sqrt(v10.var(ddof=1) / len(X) + v01.var(ddof=1) / len(Y))


@needs_r
def test_delong_matches_independent_implementation_and_permutation_null_runs():
    E, P = cohort(signal=0.8, seed=5)
    f = ml.engine("cv", E, P, {**FAST, "n_perm": 2}, cores=2)
    avg = tab(f["oof_predictions_averaged.tsv"])
    dl = tab(f["delong_auc_averaged.tsv"]).set_index("model")
    a, se = _delong_py(avg["y"].to_numpy(), avg["ridge"].to_numpy())
    assert abs(dl.loc["ridge", "auc"] - a) < 1e-12 and abs(dl.loc["ridge", "se"] - se) < 1e-12
    perm = tab(f["permutation_null.tsv"])
    assert list(perm["permutation"]) == [1, 2] and perm["mean_auroc"].between(0, 1).all()


@needs_r
def test_final_model_and_apply_once_semantics():
    E, P = cohort(signal=1.0, seed=6)
    fin = ml.engine("final", E, P, FAST)
    coef = tab(fin["final_model_coefficients.tsv"])
    assert coef["feature_id"].iloc[0] == "(Intercept)" and len(coef) - 1 in (5, 10, 20)
    E2, P2 = cohort(signal=1.0, seed=7)
    E2 = E2.drop(index=str(coef["feature_id"].iloc[1]))           # one model gene missing in the external cohort
    out = ml.engine("apply", E2, P2, {}, {"model": fin["final_model_coefficients.tsv"], "settings": fin["final_model_settings.tsv"]})
    cov = tab(out["external_gene_coverage.tsv"]).iloc[0]
    assert cov["n_missing"] == 1 and cov["n_present"] == len(coef) - 2
    pred = tab(out["external_predictions.tsv"])
    assert pred["ridge"].between(0, 1).all() and len(pred) == len(P2)
    assert tab(out["external_metrics.tsv"]).set_index("model").loc["ridge", "auc"] > 0.6


def test_sex_chromosome_genes_come_from_the_r8_probe_set():
    a0 = pd.DataFrame([{"cohort": "GSE63060", "probe_id": ml.XIST_PROBE, "a0_class": "eligible", "a0_gene_id": "7503"},
                       {"cohort": "GSE63060", "probe_id": "ILMN_1783142", "a0_class": "eligible", "a0_gene_id": "6192"},
                       {"cohort": "GSE63060", "probe_id": "ILMN_0000001", "a0_class": "eligible", "a0_gene_id": "1"},
                       {"cohort": "GSE63061", "probe_id": "ILMN_1732039", "a0_class": "eligible", "a0_gene_id": "8653"}])
    assert ml.sex_chromosome_genes(a0, "GSE63060") == ["6192", "7503"]


def test_gate_refuses_without_recorded_approvals(tmp_path, monkeypatch):
    monkeypatch.setattr(ml, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="PRECONDITIONS NOT MET"):
        ml.produce("v_test")


@needs_r
def test_threshold_metrics_are_consistent():
    E, P = cohort(signal=1.0, seed=8)
    m = tab(ml.engine("cv", E, P, FAST)["repeat_metrics.tsv"])
    r = m[m["model"] == "ridge"]
    assert np.allclose(r["balanced_accuracy"], (r["sensitivity"] + r["specificity"]) / 2)
    assert r[["sensitivity", "specificity", "ppv"]].apply(lambda c: c.between(0, 1)).all().all()
    assert m.loc[m["model"] == "B1_age", "sensitivity"].isna().all()


@needs_r
def test_results_do_not_depend_on_worker_count():
    E, P = cohort(signal=0.8, seed=10)
    a = ml.engine("cv", E, P, {**FAST, "n_perm": 2}, cores=1)
    b = ml.engine("cv", E, P, {**FAST, "n_perm": 2}, cores=2)
    assert a == b
