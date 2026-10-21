# GSE140829 chain and GSE63061 frozen-model application — run report (2026-10-20)

PI go-ahead 2026-10-20 ("go ahead"). The SAP remains a proposed draft (not approved, not frozen). All outputs below
are accepted (code identity and executed-code verification: no problems). Full test suite 354/354 before the runs, with no guarded opens.

## Frozen ML model applied once to GSE63061 (reports/ml/GSE63061_external/v1)
Related cohort with possible participant overlap (H9); cross-platform (GPL6947 to GPL10558); no re-fitting or tuning; exploratory.
200/200 model genes present. 139 AD vs 133 CTL.

| Model | AUROC (DeLong 95%, approximate) | Sens | Spec | PPV | Brier | Calibration slope |
|---|---|---|---|---|---|---|
| Frozen ridge | **0.769 (0.714–0.824)** | 0.748 | 0.632 | 0.680 | 0.203 | 0.84 |
| Frozen age model (B1) | 0.631 (0.564–0.698) | — | — | — | 0.241 | 0.86 |

Ridge − age: +0.138 (0.056–0.220), p = 0.001.

## GSE140829 (approved D19-1, D11 (a), eligibility rules, C1 review)

| Step | Output | Result |
|---|---|---|
| D19-1 mapping | annotation_audit/gse140829_nuid/v1 | 47,008/47,008 translated; no cross-check disagreement; 33,804 eligible probes, 20,838 genes |
| Eligibility | eligibility/GSE140829/v1 | 587 arrays: 204 AD, 249 CTL, 134 MCI; 19 batches |
| C1 | duplicate_review/GSE140829/c1_v1 + PI review record | 587 replicate annotations; review recorded (v7:621) |
| QC Stage A | qc_stage_a/GSE140829/v1 | R8 informative (561 concordant, 24 ambiguous, 2 two-axis discordant); R9 16 flagged, 0 failures; **0 near-identical (A2) pairs**, so C2 found no partner for any "replicate 2" array |
| QC Stage B | qc_stage_b/GSE140829/v1 | Rule-applied list: 134 P1 (MCI), 2 Q1 (both AD), 4 Q3 (D-2 (c): 1 AD, 1 CTL, 2 MCI); proposed primary **201 AD vs 248 CTL**; 31 flagged arrays retained |

Exclusion list SHA-256 d982afd4966cbaff077c1eb9910c289d0501ce60ff17af3981f64228185b93cd; Stage B manifest SHA-256
20961a8aa04707021c6e102f323c846ae97e2401529ecf5251ee845795c339ab. Awaiting PI approval as rule-applied (v5:123–129).
