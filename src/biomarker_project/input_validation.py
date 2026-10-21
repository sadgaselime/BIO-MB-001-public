"""Structural validation of an expression matrix and its sample metadata before any model is fitted.

Checks are structural only (identifiers, alignment, dimensions, missing values, labels, covariate
completeness). They never remove samples: any failure stops the run with a readable report.
Sample *exclusion* rules (QC Stage A, R8, R9, duplicate review, R2-COV) are not implemented here;
see `sample_policy.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

OK, FAILED = "OK", "FAILED"


class InputValidationError(ValueError):
    def __init__(self, report: "ValidationReport"):
        self.report = report
        failed = [c for c in report.checks if c["status"] == FAILED]
        super().__init__("input validation failed: " + "; ".join(f"{c['check']}: {c['detail']}" for c in failed))


@dataclass
class ValidationReport:
    checks: list[dict[str, Any]] = field(default_factory=list)

    def add(self, check: str, passed: bool, detail: str) -> None:
        self.checks.append({"check": check, "status": OK if passed else FAILED, "detail": detail})

    @property
    def ok(self) -> bool:
        return all(c["status"] == OK for c in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {"status": OK if self.ok else FAILED, "checks": self.checks}


def _dupes(values: pd.Index | pd.Series) -> list[str]:
    s = pd.Series(list(values), dtype=object)
    return sorted(map(str, s[s.duplicated(keep=False)].unique()))


def validate_inputs(expression: pd.DataFrame, samples: pd.DataFrame, *, allowed_groups: list[str],
                    contrast: tuple[str, str], covariates: list[str],
                    covariate_levels: dict[str, list[str]] | None = None,
                    min_per_group: int = 2) -> tuple[pd.DataFrame, ValidationReport]:
    """Validate inputs; return metadata re-ordered to the matrix column order, plus the report.

    `expression` is features x samples. Raises InputValidationError if any check fails.
    """
    rep = ValidationReport()
    covariate_levels = covariate_levels or {}

    has_id = "sample_id" in samples.columns and "group" in samples.columns
    rep.add("metadata_columns", has_id, "sample_id and group columns present" if has_id
            else f"missing required column(s); found {list(samples.columns)}")
    if not has_id:
        raise InputValidationError(rep)

    ids = samples["sample_id"]
    blank = ids.isna() | (ids.astype(str).str.strip() == "")
    rep.add("metadata_ids_nonempty", not blank.any(), f"{int(blank.sum())} empty sample_id value(s)")
    d = _dupes(ids)
    rep.add("metadata_ids_unique", not d, "all unique" if not d else f"duplicated: {d[:10]}")
    d = _dupes(expression.columns)
    rep.add("matrix_sample_ids_unique", not d, "all unique" if not d else f"duplicated: {d[:10]}")
    d = _dupes(expression.index)
    rep.add("matrix_feature_ids_unique", not d, "all unique" if not d else f"duplicated: {d[:10]}")

    in_matrix = set(map(str, expression.columns))
    in_meta = set(map(str, ids.dropna()))
    only_m, only_s = sorted(in_matrix - in_meta), sorted(in_meta - in_matrix)
    aligned = not only_m and not only_s
    rep.add("sample_id_sets_match", aligned,
            "matrix columns and metadata identifiers are the same set" if aligned
            else f"matrix-only: {only_m[:10]} ({len(only_m)}); metadata-only: {only_s[:10]} ({len(only_s)})")

    dims = expression.shape[0] >= 1 and expression.shape[1] == len(samples)
    rep.add("dimensions", dims, f"matrix {expression.shape[0]} features x {expression.shape[1]} samples; "
                                f"metadata {len(samples)} rows")

    numeric = all(pd.api.types.is_numeric_dtype(t) for t in expression.dtypes)
    rep.add("matrix_numeric", numeric, "all columns numeric" if numeric else "non-numeric matrix column(s)")
    if numeric:
        vals = expression.to_numpy(dtype=float)
        n_bad = int((~np.isfinite(vals)).sum())
        rep.add("matrix_missing_values", n_bad == 0,
                f"{n_bad} missing or non-finite value(s); no imputation is performed")

    labels = samples["group"]
    bad = sorted(set(map(str, labels.dropna())) - set(allowed_groups))
    rep.add("group_labels_allowed", not bad and not labels.isna().any(),
            f"allowed {allowed_groups}; unexpected {bad}; missing {int(labels.isna().sum())}")

    case, control = contrast
    in_contrast = samples[labels.isin([case, control])]
    counts = {g: int((in_contrast["group"] == g).sum()) for g in (case, control)}
    rep.add("contrast_group_sizes", min(counts.values()) >= min_per_group,
            f"{counts} (minimum {min_per_group} per group)")

    for cov in covariates:
        if cov not in samples.columns:
            rep.add(f"covariate_{cov}", False, "column absent")
            continue
        col = in_contrast[cov]
        n_miss = int(col.isna().sum())
        detail = f"{n_miss} missing among contrast samples"
        good = n_miss == 0
        if cov in covariate_levels:
            unexpected = sorted(set(map(str, col.dropna())) - set(covariate_levels[cov]))
            good = good and not unexpected
            detail += f"; allowed levels {covariate_levels[cov]}; unexpected {unexpected}"
        elif not pd.api.types.is_numeric_dtype(col):
            good = False
            detail += "; numeric covariate expected"
        else:
            good = good and bool(np.isfinite(col.to_numpy(dtype=float)).all())
        rep.add(f"covariate_{cov}", good, detail)

    if not rep.ok:
        raise InputValidationError(rep)
    aligned_meta = samples.set_index("sample_id").loc[list(expression.columns)].reset_index()
    rep.add("metadata_aligned_to_matrix", list(aligned_meta["sample_id"]) == list(expression.columns),
            "metadata re-ordered by identifier to the matrix column order")
    return aligned_meta, rep
