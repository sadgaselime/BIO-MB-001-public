"""QC Stage A orchestration (R8 + R9 per cohort), audit table, candidate exclusions and the V-A gate.

Real cohorts: `run_qc_stage_a` refuses any cohort containing a sample whose `data_origin` is not
"SYNTHETIC" unless the cohort carries an explicit PI authorization (`real_data_authorization`). The PI
ruling of 2026-10-18 (v7:625) permits QC Stage A to COMPUTE AND RECORD candidate exclusions for GSE63060;
no exclusion is applied until the exclusion-list approval step (v5:123-129) and D16 are decided, and
Stage A outputs remain unusable downstream until then.

What is produced per array: R8 category, R9 outcome, reason codes, A2 pairs and D18 referrals,
and the *candidate* primary-exclusion tiers implied by the approved D22 policies:
  P3 - R9 numerical failure (v7:351), never lifted;
  Q1 - R8 two-axis discordant, only where R8 is "completed — informative" (D22 row 1).
Candidate exclusions are NOT applied: the exclusion-list approval step is unresolved, and the rule
that would apply them is registered with a non-runnable approval status, so `apply_rules` refuses it.
Flags (F1 R9 k=3, F2 single-axis discordant, F3 ambiguous) and D18 review items never exclude.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import qc_r8, qc_r9
from .sample_policy import RuleResult

REAL_COHORT_BLOCK = ("QC Stage A is blocked for real cohorts without an explicit PI authorization: the exclusion-list "
                     "approval step (v5:123-129) and D16 are undecided; the PI ruling of 2026-10-18 (v7:625) permits "
                     "computing and recording candidate exclusions only, and must be cited (real_data_authorization).")
GATE_OPEN_STATUSES = (qc_r8.INFORMATIVE, qc_r8.NOT_APPLICABLE)   # V-A, v7:139
# An open V-A gate is necessary, not sufficient: the primary-population log (Tier B step 7) also needs
# the approved exclusions applied, and the exclusion-list approval step is unresolved (v7:552, 375).
PRIMARY_POPULATION_BLOCKED = ("primary-population log not started: exclusion-list approval scope unresolved "
                              "(v5:123-129; v7:552); Q1/P3 candidates not applied")


class QCStageABlocked(RuntimeError):
    pass


@dataclass
class QCCohortInput:
    cohort_id: str
    expression: pd.DataFrame        # probes x arrays
    samples: pd.DataFrame           # sample_id, sex (recorded), data_origin
    r8_dependency_blocked: str | None = None
    purpose: str = ""
    real_data_authorization: str | None = None   # required for any non-SYNTHETIC sample; recorded in the output


@dataclass
class QCStageAResult:
    cohorts: pd.DataFrame
    audit: pd.DataFrame
    a2_pairs: pd.DataFrame
    candidate_exclusions: pd.DataFrame
    r8_axes: dict
    r9_summaries: dict


def authorize(cohort: QCCohortInput) -> None:
    origin = cohort.samples.get("data_origin")
    if origin is None:
        raise QCStageABlocked(f"{cohort.cohort_id}: {REAL_COHORT_BLOCK} (data_origin missing)")
    if not (origin == "SYNTHETIC").all() and not (cohort.real_data_authorization or "").strip():
        raise QCStageABlocked(f"{cohort.cohort_id}: {REAL_COHORT_BLOCK}")
    if set(map(str, cohort.expression.columns)) != set(map(str, cohort.samples["sample_id"])):
        raise ValueError(f"{cohort.cohort_id}: expression columns and sample ids differ")


def run_qc_stage_a(cohorts: list[QCCohortInput]) -> QCStageAResult:
    for c in cohorts:          # authorise every cohort before computing anything
        authorize(c)
    status_rows, audits, pairs, axes, r9sum = [], [], [], {}, {}
    for c in cohorts:
        recorded = c.samples.set_index("sample_id")["sex"]
        r8 = qc_r8.run_r8(c.expression, recorded, c.cohort_id, blocked_reason=c.r8_dependency_blocked)
        r9 = qc_r9.run_r9(c.expression, c.cohort_id)     # R9 needs neither R8 output nor probe mapping (v7:351)
        gate_open = r8.status in GATE_OPEN_STATUSES
        status_rows.append({
            "cohort_id": c.cohort_id, "purpose": c.purpose, "n_arrays": c.expression.shape[1],
            "r8_status": r8.status, "r8_reason": r8.reason, "r9_status": r9.status,
            "r9_stop_stage": r9.stop_stage, "va_gate_open": gate_open,
            "gated_analyses": f"V-A gate open; {PRIMARY_POPULATION_BLOCKED}" if gate_open else (
                "not assessable — blocked by R8 dependency" if r8.status == qc_r8.BLOCKED else "not assessable — R8"),
            "sex_consistency_label": None if r8.status == qc_r8.INFORMATIVE else "sex consistency not verified",
            "stage_a_outputs_usable_downstream": False,   # gate open is not sufficient (see PRIMARY_POPULATION_BLOCKED)
            "data_origin": ";".join(sorted(set(map(str, c.samples["data_origin"])))),
            "real_data_authorization": c.real_data_authorization,
        })
        merged = r8.arrays.merge(r9.arrays.drop(columns="cohort_id"), on="array_id", how="outer")
        merged.insert(1, "r8_cohort_status", r8.status)
        merged.insert(2, "r9_cohort_status", r9.status)
        audits.append(merged)
        pairs.append(r9.a2_pairs)
        axes[c.cohort_id] = r8.axes
        r9sum[c.cohort_id] = {"status": r9.status, "stop_stage": r9.stop_stage, **r9.summary}

    audit = pd.concat(audits, ignore_index=True)
    audit["candidate_tiers"] = audit.apply(_candidate_tiers, axis=1)
    audit["flags"] = audit.apply(_flags, axis=1)
    audit["d18_review"] = (audit["r9_outcome"] == qc_r9.REFERRED) | (audit["a2_partner_count"] > 0)
    audit["exclusion_applied"] = False
    cand = audit.loc[audit["candidate_tiers"] != "", ["cohort_id", "array_id", "candidate_tiers", "r8_reason_code",
                                                      "r9_reason_code"]].copy()
    cand["status"] = "PROPOSED — NOT APPLIED (exclusion-list approval scope unresolved, v5:123-129)"
    return QCStageAResult(pd.DataFrame(status_rows), audit,
                          pd.concat(pairs, ignore_index=True) if pairs else pd.DataFrame(),
                          cand.reset_index(drop=True), axes, r9sum)


def _candidate_tiers(r: pd.Series) -> str:
    tiers = []
    if r["r9_outcome"] == qc_r9.FAILURE:
        tiers.append("P3")
    if r["r8_category"] == qc_r8.DISC_2 and r["r8_cohort_status"] == qc_r8.INFORMATIVE:
        tiers.append("Q1")
    return ";".join(tiers)


def _flags(r: pd.Series) -> str:
    f = []
    if r["r9_outcome"] == qc_r9.FLAGGED:
        f.append("F1(k=3)")
    if r["r8_category"] == qc_r8.DISC_1:
        f.append("F2")
    if r["r8_category"] == qc_r8.AMBIGUOUS:
        f.append("F3")
    if r["r8_category"] == qc_r8.UNDOCUMENTED:
        f.append("F3-undetermined")   # ambiguous vs unassessable is undocumented (v5:201-202); not resolved here
    return ";".join(f)


@dataclass
class CandidateQCExclusions:
    """Would remove arrays with candidate tiers. Not runnable: approval is pending (v5:123-129)."""
    audit: pd.DataFrame
    name: str = "qc_stage_a_candidate_exclusions"
    approval: str = "blocked: exclusion-list approval scope unresolved"
    source: str = "D22 rows 1 and 6 (v7:625); exclusion-list approval scope v5:123-129 unresolved"

    def apply(self, samples: pd.DataFrame) -> RuleResult:   # pragma: no cover - refused by apply_rules
        raise AssertionError("candidate QC exclusions must not be applied")
