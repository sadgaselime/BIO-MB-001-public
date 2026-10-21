"""D8 limma runner: version pins, refusal, and agreement with independent reference calculations.

SYNTHETIC DATA ONLY. Reference values are computed in Python from the design matrix (least squares,
unscaled SEs), limma's reported hyperparameters (s2.prior, df.prior) and the project's own Student-t
and BH implementations. The estimation of the hyperparameters themselves (squeezeVar/fitFDist with a
trend) is not re-implemented here; their properties are checked instead.
"""
from __future__ import annotations

import json
import shutil

import numpy as np
import pandas as pd
import pytest

from biomarker_project import limma_backend
from biomarker_project.differential_expression import (RESULT_COLUMNS, benjamini_hochberg, build_design,
                                                       fit_feature_ols, t_quantile, t_two_sided_p)
from biomarker_project.limma_backend import APPROVED_PINS, LimmaEnvironmentError, check_environment, fit_feature_limma
from biomarker_project.synthetic_data import SyntheticSpec, generate_synthetic_cohort
from biomarker_project.synthetic_pipeline import run_synthetic_pipeline

pytestmark = pytest.mark.skipif(shutil.which("Rscript") is None, reason="R 4.6.1 (D8) not installed")


@pytest.fixture(scope="module")
def fitted():
    c = generate_synthetic_cohort(SyntheticSpec(seed=21, n_ad=12, n_ctl=12, n_mci=0, n_features=300,
                                                n_up=10, n_down=10, n_age=5, n_sex=5))
    s = c.samples.set_index("sample_id").loc[list(c.expression.columns)].reset_index()
    design = build_design(s, group_col="group", case="AD", control="CTL", covariates=["age", "sex"])
    values = c.expression.to_numpy()
    run = fit_feature_limma(values, list(c.expression.index), list(s["sample_id"]), design)
    ols = fit_feature_ols(values, list(c.expression.index), design)
    return run, ols, design, values


# ------------------------------------------------------------------ environment
def test_exact_pinned_versions_are_installed():
    info = check_environment()
    for k, v in APPROVED_PINS.items():
        assert info[f"found_{k}"] == v
    assert "/renv/library/" in info["limma_path"]               # limma comes from the project renv library
    assert info["platform"] == "aarch64-apple-darwin23"


@pytest.mark.parametrize("key, wrong", [("limma", "3.68.4"), ("R", "4.6.0"), ("bioc", "3.22"), ("statmod", "1.5.1")])
def test_version_mismatch_is_refused(key, wrong):
    with pytest.raises(LimmaEnvironmentError, match="approved D8 pins"):
        check_environment({**APPROVED_PINS, key: wrong})


def test_fit_refuses_on_mismatch(fitted):
    _, _, design, values = fitted
    with pytest.raises(LimmaEnvironmentError):
        fit_feature_limma(values[:20], [f"f{i}" for i in range(20)], [f"s{i}" for i in range(values.shape[1])],
                          design, pins={**APPROVED_PINS, "limma": "9.9.9"})


def test_missing_rscript_is_reported(monkeypatch):
    monkeypatch.setattr(limma_backend.shutil, "which", lambda name: None)
    with pytest.raises(LimmaEnvironmentError, match="Rscript not found"):
        check_environment()


# ------------------------------------------------------------------ agreement with references
def test_schema_unchanged(fitted):
    run, *_ = fitted
    assert list(run.results.columns) == RESULT_COLUMNS
    assert run.results["estimable"].all()
    assert sorted(run.results["rank"]) == list(range(1, len(run.results) + 1))


def test_coefficients_match_least_squares(fitted):
    run, ols, design, values = fitted
    np.testing.assert_allclose(run.results["estimate"], ols["estimate"], rtol=0, atol=1e-10)
    beta, *_ = np.linalg.lstsq(design.matrix, values.T, rcond=None)
    np.testing.assert_allclose(run.results["estimate"], beta[design.coef_index], rtol=0, atol=1e-10)


def test_residual_variance_and_unscaled_se_match_least_squares(fitted):
    run, ols, design, values = fitted
    X = design.matrix
    n, p = X.shape
    unscaled = np.sqrt(np.linalg.inv(X.T @ X)[design.coef_index, design.coef_index])
    m = run.moderation
    np.testing.assert_allclose(m["stdev_unscaled"], unscaled, rtol=1e-12)
    assert (m["df_residual"] == n - p).all()
    sigma2_ols = (ols["std_error"] / unscaled) ** 2
    np.testing.assert_allclose(m["sigma"] ** 2, sigma2_ols, rtol=1e-10)
    np.testing.assert_allclose(m["ave_expr"], values.mean(axis=1), rtol=1e-12)   # trend covariate (Amean)


def test_moderated_statistics_follow_the_posterior_formulas(fitted):
    run, ols, design, values = fitted
    r, m = run.results, run.moderation
    df_res = m["df_residual"].to_numpy()
    s2_post = (m["df_prior"] * m["s2_prior"] + df_res * m["sigma"] ** 2) / (m["df_prior"] + df_res)
    np.testing.assert_allclose(m["s2_post"], s2_post, rtol=1e-10)
    se = np.sqrt(m["s2_post"]) * m["stdev_unscaled"]
    np.testing.assert_allclose(r["std_error"], se, rtol=1e-12)
    np.testing.assert_allclose(r["t_statistic"], r["estimate"] / se, rtol=1e-10)
    df_pooled = df_res.sum()
    np.testing.assert_allclose(r["df"], np.minimum(df_res + m["df_prior"], df_pooled), rtol=1e-12)
    p_ref = np.array([float(t_two_sided_p(t, d)) for t, d in zip(r["t_statistic"], r["df"])])
    np.testing.assert_allclose(r["p_value"], p_ref, rtol=1e-8, atol=1e-300)


def test_trend_prior_properties(fitted):
    run, *_ = fitted
    m = run.moderation
    assert np.isfinite(m["df_prior"]).all() and (m["df_prior"] > 0).all()
    assert m["df_prior"].nunique() == 1                  # robust = FALSE: one prior df
    assert m["s2_prior"].nunique() > 1                   # trend = TRUE: prior variance varies with Amean


def test_confidence_interval_uses_moderated_se_and_df_total(fitted):
    run, ols, *_ = fitted
    r = run.results
    half = np.array([t_quantile(0.975, d) for d in r["df"]]) * r["std_error"]
    np.testing.assert_allclose(r["ci_low"], r["estimate"] - half, rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(r["ci_high"], r["estimate"] + half, rtol=1e-9, atol=1e-12)
    # It is NOT the ordinary-least-squares interval (different SE and df).
    assert not np.allclose(r["ci_high"] - r["ci_low"], ols["ci_high"] - ols["ci_low"], rtol=1e-6)


def test_bh_matches_independent_and_hand_calculation(fitted):
    run, *_ = fitted
    np.testing.assert_allclose(run.results["q_value_bh"], benjamini_hochberg(run.results["p_value"]), rtol=1e-12)
    np.testing.assert_allclose(benjamini_hochberg([0.01, 0.04, 0.03, 0.005]), [0.02, 0.04, 0.04, 0.02])


def test_session_info_and_method_recorded(fitted):
    run, *_ = fitted
    assert any("limma_3.68.5" in line for line in run.session_info)
    assert "eBayes(trend = TRUE, robust = FALSE)" in run.info["method"]


# ------------------------------------------------------------------ pipeline
def test_pipeline_with_limma_is_deterministic(tmp_path):
    cfg = {"run_name": "t", "synthetic": {"seed": 8, "n_ad": 15, "n_ctl": 15, "n_mci": 5, "n_features": 200,
                                          "n_up": 5, "n_down": 5, "n_age": 5, "n_sex": 5},
           "analysis": {"method": "limma"}}
    a = run_synthetic_pipeline(cfg, tmp_path / "a")
    b = run_synthetic_pipeline(cfg, tmp_path / "b")
    assert a["output_sha256"] == b["output_sha256"]
    assert "de_limma_moderation.csv" in a["output_sha256"]
    res = pd.read_csv(tmp_path / "a" / "de_results.csv")
    assert list(res.columns) == RESULT_COLUMNS and (res["data_origin"] == "SYNTHETIC").all()
    prov = json.loads((tmp_path / "a" / "provenance.json").read_text())
    assert prov["de_method"] == "limma" and prov["r_environment"]["info"]["found_limma"] == "3.68.5"
    assert "eBayes(trend = TRUE, robust = FALSE)" in (tmp_path / "a" / "report.md").read_text()
