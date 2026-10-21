"""R8/R9 QC Stage A on synthetic fixtures: rule boundaries, reason codes, gating and blocking."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from biomarker_project import qc_r8, qc_r9
from biomarker_project.qc_fixtures import build_fixtures
from biomarker_project.qc_stage_a import (CandidateQCExclusions, QCCohortInput, QCStageABlocked, run_qc_stage_a)
from biomarker_project.sample_policy import UnapprovedRuleError, apply_rules
from biomarker_project.synthetic_pipeline import run_synthetic_pipeline

SEED = 99


@pytest.fixture(scope="module")
def qc():
    return run_qc_stage_a(build_fixtures(SEED))


def arrays(qc, cohort):
    return qc.audit[qc.audit["cohort_id"] == cohort].set_index("array_id")


def status(qc, cohort):
    return qc.cohorts.set_index("cohort_id").loc[cohort]


# ------------------------------------------------------------------ R9: A3 branches (pure)
@pytest.mark.parametrize("m, branch", [
    (1.0 - 1e-8, "referred_d18"),                              # exactly at the D22 median threshold
    (np.nextafter(1.0 - 1e-8, 0.0), "scored"),                 # just below it
    (1.0, "referred_d18"),
    (1.0000000000000002, "referred_d18"),                      # computed m > 1
    (-1.0, "failure_median_le_minus1"),
    (-1.0000000000000002, "failure_median_le_minus1"),         # computed m < -1
    (np.nextafter(-1.0, 0.0), "scored"),                       # just above -1: finite z
    (0.3, "scored"),
    (float("nan"), "failure_nonfinite_z"),
])
def test_classify_median_branches(m, branch):
    b, z = qc_r9.classify_median(m)
    assert b == branch
    assert np.isfinite(z) == (branch == "scored")


# ------------------------------------------------------------------ R9: fixtures
def test_zero_variance_is_a0_failure_and_nonfinite_probe_dropped(qc):
    a = arrays(qc, "FX-R9-ZERO-VARIANCE")
    assert a.loc["FX-R9-ZERO-VARIANCE-A01", "r9_reason_code"] == "R9_A0_ZERO_VARIANCE"
    assert (a["r9_outcome"] == "numerical_failure").sum() == 1
    assert qc.r9_summaries["FX-R9-ZERO-VARIANCE"]["n_probes_dropped_nonfinite"] == 1
    assert status(qc, "FX-R9-ZERO-VARIANCE")["r9_status"] == "completed"


def test_minimum_array_count_boundaries(qc):
    assert status(qc, "FX-R9-MIN-ARRAYS-10")["r9_status"] == "completed"           # exactly 10 remain
    assert qc.r9_summaries["FX-R9-MIN-ARRAYS-10"]["n_scored"] == 10                 # A3b boundary met
    s9 = status(qc, "FX-R9-MIN-ARRAYS-9")
    assert (s9["r9_status"], s9["r9_stop_stage"]) == ("not applicable", "A0")
    a = arrays(qc, "FX-R9-MIN-ARRAYS-9")
    assert a.loc["FX-R9-MIN-ARRAYS-9-A01", "r9_outcome"] == "numerical_failure"     # A0 failure retained
    assert set(a.drop("FX-R9-MIN-ARRAYS-9-A01")["r9_reason_code"]) == {"R9_NOT_APPLICABLE_A0"}
    assert a["a1_pairs"].isna().all()                                                # A1 never ran: nothing inferred


def test_a1_nonfinite_majority_and_fixed_matrix(qc):
    a = arrays(qc, "FX-R9-NONFINITE-A1")
    failed = [f"FX-R9-NONFINITE-A1-A{i:02d}" for i in range(1, 13)]
    assert (a.loc[failed, "r9_reason_code"] == "R9_A1_NONFINITE_MAJORITY").all()
    assert (a.loc[failed, "a1_nonfinite_pairs"] == 11).all() and (a.loc[failed, "a1_pairs"] == 21).all()
    assert a.loc[failed, "m_i"].isna().all()                                          # no m_i for A1 failures
    others = a.drop(failed)
    # D-c: the failed arrays' finite r_ij (= 0) still enter the other arrays' medians ...
    assert (others["m_i"] == 0.0).all()
    # ... whereas a recomputation without them would give the ordinary (high) medians.
    fx = next(c for c in build_fixtures(SEED) if c.cohort_id == "FX-R9-NONFINITE-A1")
    R = qc_r9.correlation_matrix(fx.expression.iloc[:, 12:].to_numpy())
    assert np.median(R[0][np.arange(10) != 0]) > 0.5
    s = status(qc, "FX-R9-NONFINITE-A1")
    assert (s["r9_status"], s["r9_stop_stage"]) == ("not applicable", "A4")
    assert (a.loc[failed, "r9_outcome"] == "numerical_failure").all()                # retained after the A4 stop


def test_option_c_referral_is_not_a_numerical_failure(qc):
    a = arrays(qc, "FX-R9-NEAR-IDENTICAL")
    clones = [f"FX-R9-NEAR-IDENTICAL-A{i:02d}" for i in range(1, 17)]
    assert (a.loc[clones, "r9_outcome"] == "referred_d18").all()
    assert (a.loc[clones, "r9_reason_code"] == "R9_A3_NEAR_IDENTICAL_REFERRED_D18").all()
    assert a.loc[clones, "failure_stage"].isna().all()
    assert (a.loc[clones, "candidate_tiers"] == "").all()                             # never P3
    assert a.loc[clones, "z_i"].isna().all() and (a.loc[clones, "m_i"] >= 1 - 1e-8).all()
    assert a.loc[clones, "d18_review"].all()
    assert status(qc, "FX-R9-NEAR-IDENTICAL")["r9_status"] == "completed"
    assert qc.r9_summaries["FX-R9-NEAR-IDENTICAL"]["n_scored"] == 14                 # referrals not in A3b/A4


def test_pairwise_a2_flags_are_distinct_from_median_referrals(qc):
    a = arrays(qc, "FX-R9-NEAR-IDENTICAL")
    pair = ["FX-R9-NEAR-IDENTICAL-A17", "FX-R9-NEAR-IDENTICAL-A18"]
    assert (a.loc[pair, "a2_partner_count"] == 1).all()
    assert (a.loc[pair, "r9_outcome"] == "passed").all() and a.loc[pair, "d18_review"].all()
    p = qc.a2_pairs[qc.a2_pairs["cohort_id"] == "FX-R9-NEAR-IDENTICAL"]
    assert ((p["array_i"] == pair[0]) & (p["array_j"] == pair[1])).any()
    assert len(p) == 16 * 15 // 2 + 1 and (p["r_ij"] >= 1 - 1e-8).all()
    # Identical arrays whose *medians* are ordinary are A2-listed but scored, not referred.
    n = arrays(qc, "FX-R9-NEGATIVE-MEDIAN")
    ident = [f"FX-R9-NEGATIVE-MEDIAN-A{i:02d}" for i in range(1, 12)]
    assert (n.loc[ident, "a2_partner_count"] == 10).all()
    assert (n.loc[ident, "a3_branch"] == "scored").all()


def test_median_at_minus_one_is_a3_failure_and_retained(qc):
    a = arrays(qc, "FX-R9-NEGATIVE-MEDIAN")
    neg = a.loc["FX-R9-NEGATIVE-MEDIAN-A12"]
    assert neg["m_i"] == -1.0
    assert (neg["r9_outcome"], neg["failure_stage"], neg["r9_reason_code"]) == \
           ("numerical_failure", "A3", "R9_A3_MEDIAN_LE_MINUS1")
    assert neg["candidate_tiers"] == "P3"
    assert status(qc, "FX-R9-NEGATIVE-MEDIAN")["r9_stop_stage"] == "A4"


def test_a3b_stop_keeps_referrals(qc):
    a = arrays(qc, "FX-R9-A3B-STOP")
    s = status(qc, "FX-R9-A3B-STOP")
    assert (s["r9_status"], s["r9_stop_stage"]) == ("not applicable", "A3b")
    assert (a["r9_outcome"] == "referred_d18").sum() == 10
    assert (a["r9_outcome"] == "not_applicable").sum() == 2
    assert not (a["r9_outcome"] == "numerical_failure").any()


def test_k3_flag_is_a_flag_not_an_exclusion(qc):
    a = arrays(qc, "FX-R9-CLEAN")
    assert a.loc["FX-R9-CLEAN-A20", "r9_outcome"] == "flagged"
    assert a.loc["FX-R9-CLEAN-A20", "flags"] == "F1(k=3)"
    assert a.loc["FX-R9-CLEAN-A20", "candidate_tiers"] == ""


def test_numerical_failures_are_never_reinstated(qc):
    fails = qc.audit[qc.audit["r9_outcome"] == "numerical_failure"]
    assert len(fails) == 16
    assert (fails["candidate_tiers"].str.contains("P3")).all()
    assert not fails["exclusion_applied"].any()
    with pytest.raises(UnapprovedRuleError):
        apply_rules(pd.DataFrame({"sample_id": fails["array_id"]}), [CandidateQCExclusions(qc.audit)])


def test_r9_is_per_cohort(qc):
    fx = {c.cohort_id: c for c in build_fixtures(SEED)}
    alone = qc_r9.run_r9(fx["FX-R9-CLEAN"].expression, "FX-R9-CLEAN").arrays.set_index("array_id")
    joint = arrays(qc, "FX-R9-CLEAN")
    pd.testing.assert_series_equal(alone["z_i"], joint["z_i"], check_names=False)


def test_r9_no_probe_after_a0_is_reported_not_guessed():
    v = np.ones((5, 12))
    v[np.arange(5), np.arange(5)] = np.nan
    with pytest.raises(qc_r9.R9UndocumentedCase):
        qc_r9.run_r9(pd.DataFrame(v), "X")


# ------------------------------------------------------------------ R8
def test_split_never_splits_ties_and_needs_two_n_min():
    assert qc_r8.split_axis(np.arange(9.0)).degenerate                    # n < 2·n_min
    assert qc_r8.split_axis(np.r_[np.zeros(6), np.ones(4)]).degenerate    # only split would leave 4 < n_min
    s = qc_r8.split_axis(np.r_[np.zeros(5), np.ones(5)])
    assert not s.degenerate and s.low_size == 5 and s.threshold == 0.5
    assert s.d_descriptive == float("inf")                                # both SDs 0, means differ


def test_split_chooses_smallest_s_within_tie_tolerance():
    v = np.r_[np.zeros(5), [0.5], np.ones(5)]        # s = 5 and s = 6 give identical W
    s = qc_r8.split_axis(v)
    assert s.low_size == 5 and s.threshold == 0.25


def test_r8_category_fixture(qc):
    a = arrays(qc, "FX-R8-CATEGORIES")
    p = "FX-R8-CATEGORIES-A"
    assert status(qc, "FX-R8-CATEGORIES")["r8_status"] == "completed — informative"
    expected = {f"{p}01": "ambiguous", f"{p}06": "discordant_two_axis", f"{p}04": "discordant_single_axis",
                f"{p}03": "concordant_single_axis", f"{p}07": "unassessable", f"{p}21": "unassessable",
                f"{p}02": "concordant_two_axis"}
    for aid, cat in expected.items():
        assert a.loc[aid, "r8_category"] == cat, aid
    assert a.loc[f"{p}07", "r8_reason_code"] == "R8_UNASSESSABLE_NONFINITE"
    assert a.loc[f"{p}21", "r8_reason_code"] == "R8_UNASSESSABLE_RECORDED_MISSING"
    assert a.loc[f"{p}06", "candidate_tiers"] == "Q1"
    assert a.loc[f"{p}04", "flags"] == "F2" and a.loc[f"{p}01", "flags"] == "F3"
    assert a.loc[f"{p}04", "candidate_tiers"] == "" and a.loc[f"{p}01", "candidate_tiers"] == ""


def test_r8_cohort_statuses_and_va_gate(qc):
    u = status(qc, "FX-R8-UNINFORMATIVE")
    assert u["r8_status"] == "completed — uninformative" and not u["va_gate_open"]
    assert u["gated_analyses"] == "not assessable — R8"
    assert (arrays(qc, "FX-R8-UNINFORMATIVE")["r8_category"] == "unassessable").all()
    n = status(qc, "FX-R8-NOT-APPLICABLE")
    assert n["r8_status"] == "not applicable" and n["va_gate_open"]
    assert "primary-population log not started" in n["gated_analyses"]      # open gate is not sufficient
    assert not qc.cohorts["stage_a_outputs_usable_downstream"].any()
    assert n["sex_consistency_label"] == "sex consistency not verified"
    b = status(qc, "FX-R8-BLOCKED")
    assert b["r8_status"] == "blocked" and not b["va_gate_open"]
    assert b["gated_analyses"] == "not assessable — blocked by R8 dependency"
    assert b["r9_status"] == "completed" and not b["stage_a_outputs_usable_downstream"]


def test_r8_xist_absent_is_not_applicable():
    fx = next(c for c in build_fixtures(SEED) if c.cohort_id == "FX-R8-CATEGORIES")
    expr = fx.expression.drop(index=qc_r8.XIST_PROBE)
    r = qc_r8.run_r8(expr, fx.samples.set_index("sample_id")["sex"], "X")
    assert r.status == "not applicable" and set(r.arrays["r8_reason_code"]) == {"R8_NOT_APPLICABLE_A0"}


def test_r8_ambiguous_with_missing_recorded_sex_is_reported_as_undocumented():
    fx = next(c for c in build_fixtures(SEED) if c.cohort_id == "FX-R8-CATEGORIES")
    rec = fx.samples.set_index("sample_id")["sex"].copy()
    rec.iloc[0] = None                                   # A01 is ambiguous
    r = qc_r8.run_r8(fx.expression, rec, "X").arrays.set_index("array_id")
    assert r.iloc[0]["r8_category"] == qc_r8.UNDOCUMENTED
    fx.samples.loc[fx.samples.index[0], "sex"] = None
    audit = run_qc_stage_a([fx]).audit.set_index("array_id").iloc[0]
    assert audit["flags"] == "F3-undetermined" and audit["candidate_tiers"] == ""   # retained; not silently resolved


# ------------------------------------------------------------------ blocking and pipeline
def test_qc_stage_a_refuses_real_cohorts():
    fx = build_fixtures(SEED)[0]
    real = QCCohortInput("GSE-LIKE", fx.expression, fx.samples.assign(data_origin="GEO"))
    with pytest.raises(QCStageABlocked, match="blocked for real cohorts"):
        run_qc_stage_a([fx, real])
    with pytest.raises(QCStageABlocked):
        run_qc_stage_a([QCCohortInput("NO-ORIGIN", fx.expression, fx.samples.drop(columns="data_origin"))])


SMALL = {"n_ad": 15, "n_ctl": 15, "n_mci": 5, "n_features": 200, "n_up": 5, "n_down": 5, "n_age": 5, "n_sex": 5,
         "include_sex_probes": True, "n_recorded_sex_swaps": 2}


def test_pipeline_qc_outputs_deterministic_and_not_applied(tmp_path):
    cfg = {"run_name": "t", "synthetic": dict(SMALL, seed=5), "qc": {"enabled": True}}
    a = run_synthetic_pipeline(cfg, tmp_path / "a")
    b = run_synthetic_pipeline(cfg, tmp_path / "b")
    assert a["output_sha256"] == b["output_sha256"]
    assert any(k.startswith("qc/") for k in a["output_sha256"])
    flow = pd.read_csv(tmp_path / "a" / "sample_flow.csv")
    assert flow["analysed"].sum() == 30                       # QC results do not change the analysed set
    assert not flow["exclusion_applied"].any()
    swapped = pd.read_csv(tmp_path / "a" / "inputs" / "synthetic_samples.csv")
    swapped = set(swapped.loc[swapped["synthetic_truth_recorded_sex_swapped"], "sample_id"])
    assert set(flow.loc[flow["r8_category"] == "discordant_two_axis", "sample_id"]) == swapped
    pop = __import__("json").loads((tmp_path / "a" / "de_population.json").read_text())
    analysed_swaps = swapped & set(flow.loc[flow["analysed"], "sample_id"])   # swapped MCI arrays are not analysed
    assert pop["is_primary_population"] is False and set(pop["q1_candidates_included"]) == analysed_swaps
    assert "not the primary population" in (tmp_path / "a" / "report.md").read_text()


def test_pipeline_va_gate_closed_skips_de(tmp_path):
    cfg = {"run_name": "t", "synthetic": dict(SMALL, n_ad=4, n_ctl=4, n_mci=0, n_recorded_sex_swaps=0, seed=5),
           "qc": {"enabled": True, "boundary_fixtures": False}}
    out = tmp_path / "gate"
    s = run_synthetic_pipeline(cfg, out)
    assert not (out / "de_results.csv").exists() and (out / "de_not_assessable.json").exists()
    assert s["n_q_below_level"] is None
    assert "not assessable — R8" in (out / "report.md").read_text()
