"""R8 sex-consistency check (QC Stage A), as approved: D5 option (b) with the D5 conventions.

Sources (v7 SAP is authoritative; v5 text retained where v7 does not replace it):
  * algorithm: v5:149-202 (A0, A0b, A1, A2, A3, A4, A5);
  * D5 option (b): v7:133 - an axis is separating iff it is non-degenerate (v5:163, 170-171);
    D (v5:173) is computed and reported descriptively only and never determines anything;
  * conventions approved under D5 (v7:608; unvalidated, no source): n_min = 5, tie tolerance 1e-12,
    >= 2 distinct Y genes, XIST ILMN_1764573 and the 13 Y probes listed below;
  * cohort status vocabulary: v7:165-177.

Interpretation note (documented, not a new rule): W_total in the tie tolerance (v5:166) is read as
the total sum of squares of the axis values about their mean.

Undocumented case (stops nothing, reported): an array whose two usable axes disagree
("ambiguous") while its recorded sex is missing matches two rows of the comparison table
(v5:201-202). It is given category "undocumented_ambiguous_recorded_missing"; both candidate
categories are retained in the primary analysis (approved D22 rows 3 and 4), so no primary
decision depends on it.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

XIST_PROBE = "ILMN_1764573"
Y_PROBES = {  # probe -> gene (v7:608; v2:175-176)
    "ILMN_1783142": "RPS4Y1", "ILMN_1732039": "DDX3Y", "ILMN_1685690": "KDM5D",
    "ILMN_1739587": "UTY", "ILMN_2264634": "UTY", "ILMN_1755537": "EIF1AY", "ILMN_2228976": "EIF1AY",
    "ILMN_2056795": "USP9Y", "ILMN_1804958": "ZFY", "ILMN_2090059": "ZFY", "ILMN_1670821": "CYorf15A",
    "ILMN_1756506": "CYorf15B", "ILMN_2094332": "CYorf15B",
}
N_MIN = 5
TIE_TOLERANCE = 1e-12
MIN_Y_GENES = 2

# Cohort statuses (v7:165-173)
INFORMATIVE = "completed — informative"
UNINFORMATIVE = "completed — uninformative"
NOT_APPLICABLE = "not applicable"
NOT_PERFORMED = "not performed"
BLOCKED = "blocked"

# Array categories (v5:195-202, v5:156)
CONC_2, DISC_2 = "concordant_two_axis", "discordant_two_axis"
CONC_1, DISC_1 = "concordant_single_axis", "discordant_single_axis"
AMBIGUOUS, UNASSESSABLE = "ambiguous", "unassessable"
UNDOCUMENTED = "undocumented_ambiguous_recorded_missing"


class R8UndocumentedCase(RuntimeError):
    pass


@dataclass
class AxisSplit:
    n: int
    degenerate: bool
    reason: str
    low_size: int | None = None
    threshold: float | None = None
    mean_low: float | None = None
    mean_high: float | None = None
    sd_low: float | None = None
    sd_high: float | None = None
    d_descriptive: float | None = None


def split_axis(values: np.ndarray, n_min: int = N_MIN, tol: float = TIE_TOLERANCE) -> AxisSplit:
    """A2 per-axis split on the finite values of one axis (v5:161-171), plus descriptive D (v5:173-174)."""
    v = np.sort(np.asarray(values, dtype=float))
    n = v.size
    if n < 2 * n_min:
        return AxisSplit(n, True, f"degenerate: n = {n} < 2·n_min = {2 * n_min}")
    if np.unique(v).size < 2:
        return AxisSplit(n, True, "degenerate: fewer than 2 distinct values")
    cands = [s for s in range(n_min, n - n_min + 1) if v[s - 1] < v[s]]   # s = size of the low class
    if not cands:
        return AxisSplit(n, True, "degenerate: no admissible split (ties)")
    w_total = float(((v - v.mean()) ** 2).sum())
    w = {s: float(((v[:s] - v[:s].mean()) ** 2).sum() + ((v[s:] - v[s:].mean()) ** 2).sum()) for s in cands}
    w_min = min(w.values())
    s_star = min(s for s in cands if w[s] <= w_min + tol * w_total)
    t = (v[s_star - 1] + v[s_star]) / 2.0
    if np.any(v == t):
        raise R8UndocumentedCase("split threshold equals an observed value (adjacent floating-point values)")
    low, high = v[:s_star], v[s_star:]
    sd_l, sd_h = float(low.std(ddof=1)), float(high.std(ddof=1))
    diff = abs(float(high.mean() - low.mean()))
    if sd_l == 0 and sd_h == 0:
        d = float("inf") if diff > 0 else float("nan")
    else:
        d = diff / float(np.sqrt((sd_l ** 2 + sd_h ** 2) / 2.0))
    return AxisSplit(n, False, "non-degenerate (separating under D5 option (b))", s_star, float(t),
                     float(low.mean()), float(high.mean()), sd_l, sd_h, d)


@dataclass
class R8Result:
    cohort_id: str
    status: str
    reason: str
    arrays: pd.DataFrame
    axes: dict


def _empty_arrays(cohort_id: str, array_ids: list[str], recorded: pd.Series, category: str, code: str) -> pd.DataFrame:
    return pd.DataFrame({"cohort_id": cohort_id, "array_id": array_ids,
                         "recorded_sex": [recorded.get(a) for a in array_ids], "r8_category": category,
                         "r8_reason_code": code})


def run_r8(expression: pd.DataFrame, recorded_sex: pd.Series, cohort_id: str,
           blocked_reason: str | None = None) -> R8Result:
    """Run R8 for one cohort. `expression` is probes x arrays; `recorded_sex` maps array id -> 'F'/'M'/NaN."""
    ids = list(map(str, expression.columns))
    recorded = recorded_sex.reindex(ids)
    if blocked_reason:
        return R8Result(cohort_id, BLOCKED, blocked_reason,
                        _empty_arrays(cohort_id, ids, recorded, "not_run", "R8_BLOCKED"), {})

    present_y = [p for p in Y_PROBES if p in expression.index]
    y_genes = sorted({Y_PROBES[p] for p in present_y})
    if XIST_PROBE not in expression.index or len(y_genes) < MIN_Y_GENES:
        why = (f"A0: XIST {'present' if XIST_PROBE in expression.index else 'absent'}; "
               f"{len(y_genes)} distinct Y gene(s) present (minimum {MIN_Y_GENES})")
        return R8Result(cohort_id, NOT_APPLICABLE, why,
                        _empty_arrays(cohort_id, ids, recorded, "not_run", "R8_NOT_APPLICABLE_A0"), {})

    x = expression.loc[XIST_PROBE].to_numpy(dtype=float)
    yv = expression.loc[present_y].to_numpy(dtype=float)
    with np.errstate(all="ignore"):
        probe_median = np.array([np.median(r[np.isfinite(r)]) if np.isfinite(r).any() else np.nan for r in yv])
        centred = yv - probe_median[:, None]
    finite_x = np.isfinite(x)
    finite_y = np.isfinite(centred).any(axis=0)
    y = np.array([np.median(c[np.isfinite(c)]) if f else np.nan for c, f in zip(centred.T, finite_y)])

    sx, sy = split_axis(x[finite_x]), split_axis(y[finite_y])
    informative = not sx.degenerate or not sy.degenerate
    rows = []
    for i, aid in enumerate(ids):
        rec = recorded.iloc[i]
        rec = None if (rec is None or (isinstance(rec, float) and np.isnan(rec)) or str(rec) not in ("F", "M")) else str(rec)
        use_x = (not sx.degenerate) and finite_x[i]
        use_y = (not sy.degenerate) and finite_y[i]
        x_call = ("F" if x[i] > sx.threshold else "M") if use_x else None     # X high -> female-type
        y_call = ("M" if y[i] > sy.threshold else "F") if use_y else None     # Y high -> male-type
        if not finite_x[i] and not finite_y[i]:
            cat, code, derived, level = UNASSESSABLE, "R8_UNASSESSABLE_NONFINITE", None, None
        elif use_x and use_y and x_call != y_call:
            derived, level = None, "ambiguous"
            cat, code = (UNDOCUMENTED, "R8_UNDOCUMENTED_AMBIGUOUS_RECORDED_MISSING") if rec is None \
                else (AMBIGUOUS, "R8_AMBIGUOUS")
        elif use_x or use_y:
            derived = x_call or y_call
            level = "two-axis" if (use_x and use_y) else "single-axis"
            if rec is None:
                cat, code = UNASSESSABLE, "R8_UNASSESSABLE_RECORDED_MISSING"
            elif level == "two-axis":
                cat, code = (CONC_2, "R8_CONCORDANT_TWO_AXIS") if derived == rec else (DISC_2, "R8_DISCORDANT_TWO_AXIS")
            else:
                cat, code = (CONC_1, "R8_CONCORDANT_SINGLE_AXIS") if derived == rec else (DISC_1, "R8_DISCORDANT_SINGLE_AXIS")
        else:
            cat, code, derived, level = UNASSESSABLE, "R8_UNASSESSABLE_NO_USABLE_AXIS", None, None
        rows.append({"cohort_id": cohort_id, "array_id": aid, "recorded_sex": rec, "xist_value": x[i],
                     "y_score": y[i], "x_usable": bool(use_x), "y_usable": bool(use_y), "x_call": x_call,
                     "y_call": y_call, "expression_sex": derived, "evidence_level": level,
                     "r8_category": cat, "r8_reason_code": code})
    status = INFORMATIVE if informative else UNINFORMATIVE
    reason = (f"X axis: {sx.reason}; Y axis: {sy.reason}; {len(y_genes)} Y genes ({len(present_y)} probes)")
    axes = {"x": sx.__dict__, "y": sy.__dict__, "y_genes_present": y_genes, "y_probes_present": present_y}
    return R8Result(cohort_id, status, reason, pd.DataFrame(rows), axes)
