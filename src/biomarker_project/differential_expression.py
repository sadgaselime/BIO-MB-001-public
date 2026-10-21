"""Per-feature linear models, Student-t inference and Benjamini-Hochberg adjustment (numpy only).

Method (used by the synthetic pipeline): for every feature, ordinary least squares on the same
design matrix, y = X b + e, e ~ N(0, s^2) independently. The coefficient of interest is the
case-indicator (case minus control, adjusted for the other design columns). Inference uses the
ordinary t statistic with n - p residual degrees of freedom and a two-sided p-value; the
confidence interval is b +/- t_{1-(1-level)/2, n-p} * SE. p-values are adjusted across all
estimable features with the Benjamini-Hochberg step-up procedure.

This is NOT the SAP's planned primary method (limma-trend moderated t, pending D8 software
pinning); it is a documented, dependency-free stand-in behind the same output schema, so a
moderated-t implementation can replace `fit_feature_ols` later without changing callers.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

_FPMIN = 1e-300
_EPS = 1e-15
_MAXIT = 2000

RESULT_COLUMNS = ["feature_id", "estimate", "std_error", "ci_low", "ci_high", "t_statistic", "df",
                  "p_value", "q_value_bh", "estimable", "rank", "data_origin"]


class DesignError(ValueError):
    pass


# ----------------------------------------------------------------- t distribution
def _betacf(a: float, b: float, x: np.ndarray) -> np.ndarray:
    """Continued fraction for the regularized incomplete beta (modified Lentz)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = np.ones_like(x)
    d = 1.0 - qab * x / qap
    d = 1.0 / np.where(np.abs(d) < _FPMIN, _FPMIN, d)
    h = d.copy()
    for m in range(1, _MAXIT + 1):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)),
                   -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            d = 1.0 / np.where(np.abs(d) < _FPMIN, _FPMIN, d)
            c = 1.0 + aa / c
            c = np.where(np.abs(c) < _FPMIN, _FPMIN, c)
            delta = d * c
            h = h * delta
        if np.all(np.abs(delta - 1.0) < _EPS):
            return h
    raise ArithmeticError("incomplete beta continued fraction did not converge")


def regularized_incomplete_beta(a: float, b: float, x) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.full(x.shape, np.nan)
    out[x <= 0.0] = 0.0
    out[x >= 1.0] = 1.0
    mid = (x > 0.0) & (x < 1.0)
    if mid.any():
        xm = x[mid]
        bt = np.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * np.log(xm) + b * np.log1p(-xm))
        direct = xm < (a + 1.0) / (a + b + 2.0)
        res = np.empty_like(xm)
        if direct.any():
            res[direct] = bt[direct] * _betacf(a, b, xm[direct]) / a
        if (~direct).any():
            res[~direct] = 1.0 - bt[~direct] * _betacf(b, a, 1.0 - xm[~direct]) / b
        out[mid] = res
    return out


def t_two_sided_p(t, df: float) -> np.ndarray:
    """Two-sided p-value P(|T| >= |t|) for Student's t with `df` degrees of freedom."""
    if df <= 0:
        raise ValueError("df must be positive")
    t = np.asarray(t, dtype=float)
    with np.errstate(over="ignore", invalid="ignore"):
        x = df / (df + t * t)
    x = np.where(np.isinf(t), 0.0, x)
    p = regularized_incomplete_beta(df / 2.0, 0.5, x)
    return np.where(np.isnan(t), np.nan, p)


def t_quantile(prob: float, df: float) -> float:
    """Quantile of Student's t for prob in (0.5, 1), by bisection on the two-sided p-value."""
    if not 0.5 < prob < 1.0:
        raise ValueError("prob must be in (0.5, 1)")
    target = 2.0 * (1.0 - prob)
    lo, hi = 0.0, 1.0
    while t_two_sided_p(hi, df) > target:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_two_sided_p(mid, df) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ----------------------------------------------------------------- multiplicity
def benjamini_hochberg(p) -> np.ndarray:
    """BH-adjusted p-values (q-values); NaN p-values stay NaN and are not counted in the family."""
    p = np.asarray(p, dtype=float)
    q = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    m = int(ok.sum())
    if m == 0:
        return q
    ps = p[ok]
    order = np.argsort(ps, kind="mergesort")
    scaled = ps[order] * m / np.arange(1, m + 1)
    scaled = np.minimum(np.minimum.accumulate(scaled[::-1])[::-1], 1.0)
    adj = np.empty(m)
    adj[order] = scaled
    q[ok] = adj
    return q


# ----------------------------------------------------------------- design and fit
@dataclass
class Design:
    matrix: np.ndarray
    columns: list[str]
    coefficient: str          # name of the coefficient of interest

    @property
    def coef_index(self) -> int:
        return self.columns.index(self.coefficient)


def build_design(samples: pd.DataFrame, *, group_col: str, case: str, control: str,
                 covariates: list[str]) -> Design:
    """Intercept + case indicator + covariates (numeric as-is; categorical as treatment indicators
    against the alphabetically first level). `samples` must contain only case and control rows."""
    groups = samples[group_col].astype(str)
    if not set(groups) <= {case, control}:
        raise DesignError(f"design rows must be {case} or {control} only; found {sorted(set(groups))}")
    cols = {"(Intercept)": np.ones(len(samples)), f"group[{case}]": (groups == case).to_numpy(dtype=float)}
    for cov in covariates:
        s = samples[cov]
        if pd.api.types.is_numeric_dtype(s):
            cols[cov] = s.to_numpy(dtype=float)
        else:
            levels = sorted(map(str, s.unique()))
            for lev in levels[1:]:
                cols[f"{cov}[{lev}]"] = (s.astype(str) == lev).to_numpy(dtype=float)
    X = np.column_stack(list(cols.values()))
    names = list(cols.keys())
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise DesignError(f"design matrix is rank-deficient (columns {names})")
    if X.shape[0] - X.shape[1] < 1:
        raise DesignError("no residual degrees of freedom")
    return Design(matrix=X, columns=names, coefficient=f"group[{case}]")


def fit_feature_ols(values: np.ndarray, feature_ids: list[str], design: Design,
                    ci_level: float = 0.95) -> pd.DataFrame:
    """Fit y = X b + e for every row of `values` (features x samples, columns in design row order)."""
    Y = np.asarray(values, dtype=float)
    X = design.matrix
    n, p = X.shape
    if Y.shape[1] != n:
        raise DesignError(f"values have {Y.shape[1]} samples but the design has {n} rows")
    df = n - p
    Q, R = np.linalg.qr(X)
    B = np.linalg.solve(R, Q.T @ Y.T).T                     # features x p
    resid = Y - B @ X.T
    sigma2 = (resid ** 2).sum(axis=1) / df
    R_inv = np.linalg.solve(R, np.eye(p))
    unscaled = (R_inv @ R_inv.T)[design.coef_index, design.coef_index]
    j = design.coef_index
    est = B[:, j]
    se = np.sqrt(sigma2 * unscaled)
    # Numerical guard (implementation detail, not a scientific threshold): a residual variance at
    # rounding-error level, below (1000 * machine eps * max|y|)^2, is treated as zero -> not estimable.
    scale = np.maximum(np.abs(Y).max(axis=1), 1.0)
    estimable = sigma2 > (1e3 * np.finfo(float).eps * scale) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(estimable, est / se, np.nan)
    pval = t_two_sided_p(t, df)
    tcrit = t_quantile(1.0 - (1.0 - ci_level) / 2.0, df)
    out = pd.DataFrame({
        "feature_id": feature_ids, "estimate": est, "std_error": se,
        "ci_low": np.where(estimable, est - tcrit * se, np.nan),
        "ci_high": np.where(estimable, est + tcrit * se, np.nan),
        "t_statistic": t, "df": df, "p_value": pval,
    })
    out["q_value_bh"] = benjamini_hochberg(out["p_value"].to_numpy())
    out["estimable"] = estimable
    # Deterministic ranking: p ascending, then |t| descending, then feature_id.
    order = out.assign(_abs_t=-out["t_statistic"].abs()).sort_values(
        ["p_value", "_abs_t", "feature_id"], kind="mergesort", na_position="last").index
    out.loc[order, "rank"] = np.arange(1, len(out) + 1)
    out["rank"] = out["rank"].astype(int)
    return out
