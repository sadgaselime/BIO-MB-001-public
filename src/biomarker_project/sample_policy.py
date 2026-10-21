"""Explicit interface for sample-set rules, with a record of which SAP rules are deferred.

A sample-set rule takes the validated, aligned metadata and returns which samples it keeps and,
for every removed sample, a reason and an exclusion tier. The pipeline runs only rules whose
`approval` is "approved" or "synthetic-only"; anything else raises UnapprovedRuleError, so an
unapproved SAP rule cannot be switched on by accident.

Implemented: the contrast-label restriction (only case and control labels enter the contrast).
This mirrors the approved D1/D2 rule that non-contrast labels are not analysed (v7:604-605;
Tier P1, v7:351). Here it is applied to synthetic labels only.

QC Stage A (R8, R9) is implemented in qc_stage_a.py for synthetic cohorts only; its candidate
exclusions are not applied (CandidateQCExclusions is not runnable). Deliberately NOT implemented
(see DEFERRED_RULES): QC Stage A on real cohorts, duplicate review (D18), R2-COV covariate exclusions, the precedence rule (v7 §5.2), sensitivity
sample sets (S1-S16, D16) and the exclusion-list approval step.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

RUNNABLE_APPROVALS = ("approved", "synthetic-only")


class UnapprovedRuleError(RuntimeError):
    pass


@dataclass
class RuleResult:
    kept: pd.DataFrame           # metadata rows that remain
    removed: pd.DataFrame        # sample_id, group, reason, tier


class SampleSetRule(Protocol):
    name: str
    approval: str                # "approved", "synthetic-only", or anything else (not runnable)
    source: str                  # SAP reference

    def apply(self, samples: pd.DataFrame) -> RuleResult: ...


@dataclass
class ContrastLabelRestriction:
    case: str
    control: str
    name: str = "contrast_label_restriction"
    approval: str = "approved"
    source: str = "D1/D2 approved 2026-10-10 (v7:604-605); Tier P1 non-contrast labels (v7:351)"

    def apply(self, samples: pd.DataFrame) -> RuleResult:
        keep = samples["group"].isin([self.case, self.control])
        removed = samples.loc[~keep, ["sample_id", "group"]].copy()
        removed["reason"] = f"label not in contrast {self.case} vs {self.control}"
        removed["tier"] = "P1 (non-contrast label)"
        return RuleResult(kept=samples.loc[keep].copy(), removed=removed)


@dataclass(frozen=True)
class DeferredRule:
    name: str
    status: str
    reference: str


DEFERRED_RULES: tuple[DeferredRule, ...] = (
    DeferredRule("QC Stage A on real cohorts (R8, R9)", "implemented for synthetic cohorts only (qc_stage_a.py); "
                 "refused for real cohorts", "QC Stage A may not start until the remaining D22 items are approved (v7:625)"),
    DeferredRule("Applying QC candidate exclusions (P3, Q1)", "computed and listed, not applied",
                 "exclusion-list approval scope unresolved (v5:123-129)"),
    DeferredRule("Duplicate / near-identical review (D18)", "not implemented", "D18 partially approved (v7:621)"),
    DeferredRule("R2-COV covariate exclusions (Tier P4)", "not implemented; missing covariates fail validation instead",
                 "v7:351"),
    DeferredRule("Precedence rule for sample sets", "not implemented", "v7 §5.2, proposed (D18/D16)"),
    DeferredRule("Sensitivity sample sets S1-S16", "not implemented", "D16 unapproved"),
    DeferredRule("Exclusion-list approval step", "not implemented", "v5:123-129, unresolved"),
    DeferredRule("Probe-to-gene collapsing and gene-level family", "not implemented (feature level only)", "D6 unresolved"),
)


def apply_rules(samples: pd.DataFrame, rules: list[SampleSetRule]) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    """Apply rules in order. Returns (kept metadata, removal log, per-rule summary)."""
    removed_all = []
    summary = []
    current = samples
    for rule in rules:
        if rule.approval not in RUNNABLE_APPROVALS:
            raise UnapprovedRuleError(f"rule '{rule.name}' has approval '{rule.approval}' and may not run")
        res = rule.apply(current)
        log = res.removed.assign(rule=rule.name)
        removed_all.append(log)
        summary.append({"rule": rule.name, "approval": rule.approval, "source": rule.source,
                        "n_in": len(current), "n_removed": len(res.removed), "n_out": len(res.kept)})
        current = res.kept
    cols = ["sample_id", "group", "rule", "reason", "tier"]
    removed = pd.concat(removed_all, ignore_index=True)[cols] if removed_all else pd.DataFrame(columns=cols)
    return current, removed, summary
