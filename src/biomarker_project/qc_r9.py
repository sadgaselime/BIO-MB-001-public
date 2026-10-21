"""R9 array-outlier check and numerical-failure classification (QC Stage A), as approved.

Sources: v5:242-260 (A0-A5) as overridden by the D22 P3 definition (v7:351, approved
2026-10-11); conventions approved under D5 (v7:608): k = 3, minimum 10 arrays, near-identical
tolerance r >= 1 - 1e-8. Run separately within each cohort on that cohort's arrays.

  A0  drop probes with any non-finite value; an array with zero variance (all remaining values
      identical) is a numerical failure; fewer than 10 remaining arrays -> R9 not applicable.
  A1  one fixed Pearson matrix over the arrays remaining after A0; an array with more than half of
      its pairs non-finite is a numerical failure (no m_i / z_i), but its finite r_ij still enter
      other arrays' medians. A1/A3 outcomes never change another array's median.
  A2  pairs with r_ij >= 1 - 1e-8 are listed for D18 review and retained (pairwise, D5 convention).
  A3  m_i = median of array i's finite r_ij. m_i >= 1 - 1e-8 -> "referred to D18" (D22 median-level
      rule; not a failure, not flagged, retained, not scored); m_i <= -1 -> numerical failure;
      otherwise z_i = atanh(m_i), a non-finite z_i -> numerical failure.
  A3b fewer than 10 arrays with finite z_i -> R9 not applicable.
  A4  M, S over arrays with finite z_i; S = 0 or non-finite -> R9 not applicable.
  A5  flag if z_i < M - k·S (k = 3; one-sided). k = 2.5 and 4 (S5b/S5c) are not approved and not computed.
When R9 stops as not applicable, failures classified at stages that ran remain numerical failures
(Tier P3) and no failure is inferred for a stage that did not run.

Undocumented case (raises R9UndocumentedCase): every probe has a non-finite value in some array,
so no probe remains after A0 and array variance is undefined.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

K = 3.0
MIN_ARRAYS = 10
NEAR_IDENTICAL = 1.0 - 1e-8
MAD_CONSTANT = 1.4826

COMPLETED = "completed"
NOT_APPLICABLE = "not applicable"
BLOCKED = "blocked"

PASSED, FLAGGED, FAILURE, REFERRED, NA_OUT = "passed", "flagged", "numerical_failure", "referred_d18", "not_applicable"


class R9UndocumentedCase(RuntimeError):
    pass


def classify_median(m: float) -> tuple[str, float]:
    """A3 branch for one finite or non-finite median. Returns (branch, z)."""
    if not np.isfinite(m):
        return "failure_nonfinite_z", float("nan")
    if m >= NEAR_IDENTICAL:
        return "referred_d18", float("nan")
    if m <= -1.0:
        return "failure_median_le_minus1", float("nan")
    z = float(np.arctanh(m))
    if not np.isfinite(z):
        return "failure_nonfinite_z", float("nan")   # defensive; unreachable for -1 < m < 1 - 1e-8
    return "scored", z


@dataclass
class R9Result:
    cohort_id: str
    status: str
    stop_stage: str | None
    arrays: pd.DataFrame
    a2_pairs: pd.DataFrame
    summary: dict


def correlation_matrix(values: np.ndarray) -> np.ndarray:
    """Pearson r between columns (arrays); non-finite where undefined or on overflow."""
    with np.errstate(all="ignore"):
        xc = values - values.mean(axis=0)
        norm = np.sqrt((xc ** 2).sum(axis=0))
        return (xc.T @ xc) / np.outer(norm, norm)


def run_r9(expression: pd.DataFrame, cohort_id: str, blocked_reason: str | None = None,
           k: float = K, min_arrays: int = MIN_ARRAYS) -> R9Result:
    ids = list(map(str, expression.columns))
    n = len(ids)
    base = pd.DataFrame({"cohort_id": cohort_id, "array_id": ids, "a0_zero_variance": False,
                         "a1_nonfinite_pairs": np.nan, "a1_pairs": np.nan, "m_i": np.nan, "z_i": np.nan,
                         "a3_branch": None, "a2_partner_count": 0, "r9_outcome": NA_OUT,
                         "failure_stage": None, "r9_reason_code": None})
    empty_pairs = pd.DataFrame(columns=["cohort_id", "array_i", "array_j", "r_ij"])
    if blocked_reason:
        base["r9_outcome"], base["r9_reason_code"] = BLOCKED, "R9_BLOCKED"
        return R9Result(cohort_id, BLOCKED, None, base, empty_pairs, {"reason": blocked_reason})

    X = expression.to_numpy(dtype=float)
    keep_probe = np.isfinite(X).all(axis=1)
    if not keep_probe.any():
        raise R9UndocumentedCase(f"{cohort_id}: no probe remains after A0 (every probe has a non-finite value)")
    Xf = X[keep_probe]
    zero_var = Xf.max(axis=0) == Xf.min(axis=0)
    base.loc[zero_var, ["a0_zero_variance", "r9_outcome", "failure_stage", "r9_reason_code"]] = \
        [True, FAILURE, "A0", "R9_A0_ZERO_VARIANCE"]
    summary = {"n_arrays": n, "n_probes": int(X.shape[0]), "n_probes_dropped_nonfinite": int((~keep_probe).sum()),
               "n_a0_failures": int(zero_var.sum()), "k": k, "min_arrays": min_arrays,
               "near_identical_tolerance": "1 - 1e-8"}
    remaining = np.flatnonzero(~zero_var)

    def stop(stage: str, code: str) -> R9Result:
        undecided = base["failure_stage"].isna() & (base["r9_outcome"] != REFERRED)
        base.loc[undecided, ["r9_outcome", "r9_reason_code"]] = [NA_OUT, code]
        summary["stop_reason"] = code
        return R9Result(cohort_id, NOT_APPLICABLE, stage, base, pairs, summary)

    pairs = empty_pairs
    if remaining.size < min_arrays:
        return stop("A0", "R9_NOT_APPLICABLE_A0")

    R = correlation_matrix(Xf[:, remaining])
    nr = remaining.size
    off = ~np.eye(nr, dtype=bool)
    finite = np.isfinite(R) & off
    nonfinite_pairs = (off & ~finite).sum(axis=1)
    a1_fail = nonfinite_pairs > (nr - 1) / 2.0
    base.loc[remaining, "a1_nonfinite_pairs"] = nonfinite_pairs
    base.loc[remaining, "a1_pairs"] = nr - 1
    idx_a1 = remaining[a1_fail]
    base.loc[idx_a1, ["r9_outcome", "failure_stage", "r9_reason_code"]] = [FAILURE, "A1", "R9_A1_NONFINITE_MAJORITY"]

    iu, ju = np.triu_indices(nr, 1)
    near = np.isfinite(R[iu, ju]) & (R[iu, ju] >= NEAR_IDENTICAL)
    pairs = pd.DataFrame({"cohort_id": cohort_id, "array_i": [ids[remaining[i]] for i in iu[near]],
                          "array_j": [ids[remaining[j]] for j in ju[near]], "r_ij": R[iu, ju][near]})
    partner = np.zeros(nr, dtype=int)
    np.add.at(partner, iu[near], 1)
    np.add.at(partner, ju[near], 1)
    base.loc[remaining, "a2_partner_count"] = partner

    for row in range(nr):
        if a1_fail[row]:
            continue
        i = remaining[row]
        m = float(np.median(R[row][finite[row]]))
        branch, z = classify_median(m)
        base.loc[i, ["m_i", "z_i", "a3_branch"]] = [m, z, branch]
        if branch == "referred_d18":
            base.loc[i, ["r9_outcome", "r9_reason_code"]] = [REFERRED, "R9_A3_NEAR_IDENTICAL_REFERRED_D18"]
        elif branch.startswith("failure"):
            code = "R9_A3_MEDIAN_LE_MINUS1" if branch == "failure_median_le_minus1" else "R9_A3_NONFINITE_Z"
            base.loc[i, ["r9_outcome", "failure_stage", "r9_reason_code"]] = [FAILURE, "A3", code]

    scored = base["a3_branch"] == "scored"
    z = base.loc[scored, "z_i"].to_numpy(dtype=float)
    summary.update({"n_a1_failures": int(a1_fail.sum()),
                    "n_a3_failures": int((base["failure_stage"] == "A3").sum()),
                    "n_referred_d18": int((base["r9_outcome"] == REFERRED).sum()),
                    "n_a2_pairs": int(len(pairs)), "n_scored": int(z.size)})
    if z.size < min_arrays:
        return stop("A3b", "R9_NOT_APPLICABLE_A3B")
    M = float(np.median(z))
    S = float(MAD_CONSTANT * np.median(np.abs(z - M)))
    summary.update({"M": M, "S": S})
    if not np.isfinite(S) or S == 0.0:
        return stop("A4", "R9_NOT_APPLICABLE_A4")
    cut = M - k * S
    summary["flag_threshold_z"] = cut
    flagged = scored & (base["z_i"] < cut)
    base.loc[flagged, ["r9_outcome", "r9_reason_code"]] = [FLAGGED, "R9_A5_FLAG_K3"]
    base.loc[scored & ~flagged, ["r9_outcome", "r9_reason_code"]] = [PASSED, "R9_PASSED"]
    summary["n_flagged"] = int(flagged.sum())
    return R9Result(cohort_id, COMPLETED, None, base, pairs, summary)
