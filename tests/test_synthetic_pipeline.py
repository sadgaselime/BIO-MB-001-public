"""Synthetic pipeline: generator, input validation, statistics, sample-set rules, end-to-end run."""
from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import pytest

from biomarker_project.differential_expression import (
    RESULT_COLUMNS, DesignError, benjamini_hochberg, build_design, fit_feature_ols, t_quantile, t_two_sided_p)
from biomarker_project.input_validation import InputValidationError, validate_inputs
from biomarker_project.sample_policy import ContrastLabelRestriction, UnapprovedRuleError, apply_rules
from biomarker_project.synthetic_data import SyntheticSpec, generate_synthetic_cohort
from biomarker_project.synthetic_pipeline import run_synthetic_pipeline

SMALL = {"n_ad": 15, "n_ctl": 15, "n_mci": 5, "n_features": 200, "n_up": 5, "n_down": 5,
         "n_age": 5, "n_sex": 5, "effect_log2": 1.5}
VALIDATE_KW = dict(allowed_groups=["AD", "CTL", "MCI"], contrast=("AD", "CTL"), covariates=["age", "sex"],
                   covariate_levels={"sex": ["F", "M"]})


def _with_nan(e: pd.DataFrame) -> pd.DataFrame:
    e = e.copy()
    e.iloc[3, 2] = np.nan
    return e


@pytest.fixture
def cohort():
    return generate_synthetic_cohort(SyntheticSpec(seed=7, **SMALL))


# ------------------------------------------------------------------ generator
def test_generator_is_deterministic_for_a_seed():
    a = generate_synthetic_cohort(SyntheticSpec(seed=11, **SMALL))
    b = generate_synthetic_cohort(SyntheticSpec(seed=11, **SMALL))
    pd.testing.assert_frame_equal(a.expression, b.expression)
    pd.testing.assert_frame_equal(a.samples, b.samples)
    pd.testing.assert_frame_equal(a.truth, b.truth)
    c = generate_synthetic_cohort(SyntheticSpec(seed=12, **SMALL))
    assert not np.allclose(a.expression.to_numpy(), c.expression.to_numpy())


def test_generator_shapes_labels_and_planted_blocks(cohort):
    assert cohort.expression.shape == (200, 35)
    assert cohort.samples["group"].value_counts().to_dict() == {"AD": 15, "CTL": 15, "MCI": 5}
    assert set(cohort.samples["sample_id"]) == set(cohort.expression.columns)
    assert list(cohort.samples["sample_id"]) != list(cohort.expression.columns)  # shuffled on purpose
    t = cohort.truth
    assert (t["planted_group_effect_ad_minus_ctl"] == 1.5).sum() == 5
    assert (t["planted_group_effect_ad_minus_ctl"] == -1.5).sum() == 5
    assert (t["planted_age_effect_per_year"] != 0).sum() == 5
    assert (t["planted_sex_effect_male"] != 0).sum() == 5
    blocks = [t["planted_group_effect_ad_minus_ctl"] != 0, t["planted_age_effect_per_year"] != 0,
              t["planted_sex_effect_male"] != 0]
    assert int(sum(b.astype(int) for b in blocks).max()) == 1   # planted blocks do not overlap
    assert (cohort.samples["data_origin"] == "SYNTHETIC").all()


def test_generator_rejects_oversized_planted_blocks():
    with pytest.raises(ValueError):
        SyntheticSpec(n_features=10, n_up=5, n_down=5, n_age=1, n_sex=0)


# ------------------------------------------------------------------ validation
def test_validation_aligns_metadata_to_matrix_order(cohort):
    aligned, rep = validate_inputs(cohort.expression, cohort.samples, **VALIDATE_KW)
    assert rep.ok
    assert list(aligned["sample_id"]) == list(cohort.expression.columns)


@pytest.mark.parametrize("mutate, failing_check", [
    (lambda e, s: (e, pd.concat([s, s.iloc[[0]]], ignore_index=True)), "metadata_ids_unique"),
    (lambda e, s: (e.drop(columns=e.columns[0]), s), "sample_id_sets_match"),
    (lambda e, s: (e, s.assign(sample_id=s["sample_id"].where(s.index != 0, "SYN-X9999"))), "sample_id_sets_match"),
    (lambda e, s: (_with_nan(e), s), "matrix_missing_values"),
    (lambda e, s: (e, s.assign(group=s["group"].where(s.index != 0, "Alzheimer"))), "group_labels_allowed"),
    (lambda e, s: (e, s.assign(sex=s["sex"].where(s.index != 0, "U"))), "covariate_sex"),
    (lambda e, s: (e, s.drop(columns="age")), "covariate_age"),
])
def test_validation_failures_stop_the_run(cohort, mutate, failing_check):
    expr, samples = mutate(cohort.expression.copy(), cohort.samples.copy())
    with pytest.raises(InputValidationError) as exc:
        validate_inputs(expr, samples, **VALIDATE_KW)
    failed = {c["check"] for c in exc.value.report.checks if c["status"] == "FAILED"}
    assert failing_check in failed


def test_validation_requires_minimum_contrast_group_size(cohort):
    samples = cohort.samples[~((cohort.samples["group"] == "CTL"))]
    expr = cohort.expression[list(samples["sample_id"])]
    with pytest.raises(InputValidationError):
        validate_inputs(expr, samples, **VALIDATE_KW)


# ------------------------------------------------------------------ statistics
@pytest.mark.parametrize("t, df, expected", [
    (2.2281388519649385, 10, 0.05),        # t_{0.975,10}
    (2.0638985616280205, 24, 0.05),        # t_{0.975,24}
    (1.0, 1, 0.5),                         # Cauchy: P(|T|>=1) = 1/2
    (0.0, 5, 1.0),
    (math.inf, 5, 0.0),
])
def test_t_two_sided_p_known_values(t, df, expected):
    assert float(t_two_sided_p(t, df)) == pytest.approx(expected, abs=1e-10)


def test_t_two_sided_p_large_df_matches_normal():
    z = 1.959963984540054
    assert float(t_two_sided_p(z, 1e7)) == pytest.approx(0.05, abs=1e-6)


def test_t_quantile_inverts_p():
    assert t_quantile(0.975, 10) == pytest.approx(2.2281388519649385, abs=1e-9)


def test_benjamini_hochberg_hand_example_and_nan():
    p = np.array([0.01, 0.04, 0.03, 0.005, np.nan])
    q = benjamini_hochberg(p)
    assert np.allclose(q[:4], [0.02, 0.04, 0.04, 0.02])
    assert np.isnan(q[4])


def test_ols_matches_lstsq_and_textbook_se():
    rng = np.random.default_rng(0)
    samples = pd.DataFrame({"group": ["AD"] * 6 + ["CTL"] * 6, "age": rng.normal(70, 5, 12)})
    design = build_design(samples, group_col="group", case="AD", control="CTL", covariates=["age"])
    Y = rng.normal(size=(3, 12))
    res = fit_feature_ols(Y, ["a", "b", "c"], design)
    X = design.matrix
    for i in range(3):
        b, rss, *_ = np.linalg.lstsq(X, Y[i], rcond=None)
        se = math.sqrt(rss[0] / (12 - 3) * np.linalg.inv(X.T @ X)[1, 1])
        row = res.loc[res["feature_id"] == ["a", "b", "c"][i]].iloc[0]
        assert row["estimate"] == pytest.approx(b[1])
        assert row["std_error"] == pytest.approx(se)
        assert row["df"] == 9


def test_design_rejects_rank_deficiency_and_extra_labels():
    s = pd.DataFrame({"group": ["AD", "AD", "CTL", "CTL"], "x": [1.0, 1.0, 0.0, 0.0]})
    with pytest.raises(DesignError):
        build_design(s, group_col="group", case="AD", control="CTL", covariates=["x"])
    with pytest.raises(DesignError):
        build_design(s.assign(group=["AD", "MCI", "CTL", "CTL"]), group_col="group", case="AD",
                     control="CTL", covariates=[])


def test_zero_variance_feature_is_marked_not_estimable():
    s = pd.DataFrame({"group": ["AD"] * 3 + ["CTL"] * 3})
    design = build_design(s, group_col="group", case="AD", control="CTL", covariates=[])
    res = fit_feature_ols(np.vstack([np.ones(6), np.arange(6.0)]), ["flat", "ramp"], design)
    flat = res.set_index("feature_id").loc["flat"]
    assert not flat["estimable"] and np.isnan(flat["p_value"]) and np.isnan(flat["q_value_bh"])


# ------------------------------------------------------------------ sample-set rules
def test_contrast_rule_removes_only_non_contrast_labels(cohort):
    kept, removed, summary = apply_rules(cohort.samples, [ContrastLabelRestriction("AD", "CTL")])
    assert set(kept["group"]) == {"AD", "CTL"} and len(kept) == 30
    assert set(removed["group"]) == {"MCI"} and len(removed) == 5
    assert summary[0]["approval"] == "approved"


def test_unapproved_rule_cannot_run(cohort):
    class PretendR9:
        name, approval, source = "r9_outliers", "proposed", "v7:351"

        def apply(self, samples):  # pragma: no cover - must never be reached
            raise AssertionError("unapproved rule executed")

    with pytest.raises(UnapprovedRuleError):
        apply_rules(cohort.samples, [PretendR9()])


# ------------------------------------------------------------------ end to end
@pytest.fixture
def small_config():
    return {"run_name": "test", "synthetic": dict(SMALL, seed=3)}


def test_end_to_end_outputs_schema_and_warnings(tmp_path, small_config):
    out = tmp_path / "run"
    summary = run_synthetic_pipeline(small_config, out)
    for name in ["inputs/synthetic_expression.csv", "inputs/synthetic_samples.csv", "inputs/synthetic_planted_truth.csv",
                 "validation.json", "sample_flow.csv", "de_results.csv", "planted_signal_recovery.json",
                 "report.md", "provenance.json"]:
        assert (out / name).is_file(), name
    res = pd.read_csv(out / "de_results.csv")
    assert list(res.columns) == RESULT_COLUMNS
    assert len(res) == 200 and res["feature_id"].is_unique
    assert (res["data_origin"] == "SYNTHETIC").all()
    assert ((res["q_value_bh"] >= res["p_value"]) | res["p_value"].isna()).all()
    assert (res["ci_low"] <= res["estimate"]).all() and (res["estimate"] <= res["ci_high"]).all()
    assert list(res["rank"]) == list(range(1, 201))
    flow = pd.read_csv(out / "sample_flow.csv")
    assert flow["analysed"].sum() == 30 and set(flow.loc[~flow["analysed"], "group"]) == {"MCI"}
    report = (out / "report.md").read_text()
    assert report.count("SYNTHETIC DATA — NOT BIOLOGICAL EVIDENCE") >= 2
    assert "Deferred pending scientific approval" in report
    prov = json.loads((out / "provenance.json").read_text())
    assert prov["seed"] == 3 and "numpy" in prov["software"] and prov["output_sha256"]
    assert summary["recovery"]["true_positives"] >= 8   # strong planted effects are recovered


def test_end_to_end_is_repeatable_with_same_seed(tmp_path, small_config):
    a = run_synthetic_pipeline(small_config, tmp_path / "a")
    b = run_synthetic_pipeline(small_config, tmp_path / "b")
    assert a["output_sha256"] == b["output_sha256"]
    c = run_synthetic_pipeline(small_config, tmp_path / "c", seed=4)
    assert c["output_sha256"]["de_results.csv"] != a["output_sha256"]["de_results.csv"]


def test_rerun_into_same_directory_starts_clean(tmp_path, small_config):
    out = tmp_path / "run"
    first = run_synthetic_pipeline(small_config, out)
    (out / "stale.txt").write_text("left over")
    second = run_synthetic_pipeline(small_config, out)
    assert not (out / "stale.txt").exists()
    assert first["output_sha256"] == second["output_sha256"]


def test_refuses_to_clear_a_foreign_directory(tmp_path, small_config):
    out = tmp_path / "precious"
    out.mkdir()
    (out / "data.txt").write_text("keep")
    with pytest.raises(FileExistsError):
        run_synthetic_pipeline(small_config, out)
    assert (out / "data.txt").read_text() == "keep"
