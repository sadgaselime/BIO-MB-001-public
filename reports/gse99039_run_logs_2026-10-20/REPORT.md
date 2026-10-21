# GSE99039 chain to the rule-applied exclusion list — run report (2026-10-20)

PI approvals 2026-10-20: E-99 eligibility rules (v7:605) and R8-570a sex-check probe sets (v7:608). The SAP remains a proposed
draft (not approved, not frozen). Code: new scripts/eligibility_gse99039.py. Optional R8 probe lists were added to
src/biomarker_project/qc_r8.py and qc_stage_a.py, with defaults unchanged. The C1 and QC Stage A/B runners were configured
for GSE99039. Full test suite 364/364 with no guarded opens. All four outputs below are accepted (code identity and
executed-code verification: no problems).

| Step | Output | Result |
|---|---|---|
| Eligibility | eligibility/GSE99039/v1 | 558 arrays: IPD 205, GPD 41, GU 22, CONTROL 233, other 57; 37 batches; Sex recorded 505; age at exam 284; no duplicated GSM, title or subject_id; 8 missing subject_id (all HD_HD_BATCH) |
| C1 | duplicate_review/GSE99039/c1_v1 | complete: no candidates |
| QC Stage A | qc_stage_a/GSE99039/v1 | R8 informative with R8-570a (6 XIST and 18 Y probe sets, 8 Y genes): 463 concordant, 27 ambiguous, 15 two-axis discordant, 53 not assessable (49 with recorded sex missing, 4 ambiguous with sex missing); R9 10 flagged, 0 failures; 0 A2 pairs |
| QC Stage B | qc_stage_b/GSE99039/v1 | Rule-applied list: 57 P1 (other labels), 15 Q1 (13 within the contrast groups: IPD 8, CONTROL 4, GPD 1; plus HD 1 and ATYPICAL_PD 1, which are also P1). Proposed sets: **IPD 197, GPD 40, GU 22, CONTROL 229**; 33 flagged arrays retained |

Exclusion list SHA-256 1551ab37d2ade028e16907aa6917821db006e8b43c9df010a63e41b8547e6b82; Stage B manifest SHA-256
548db75f54c11e09a5e7d405d0781fd25b63d2c25c341f7d356708f2df69fc2c. Awaiting PI approval as rule-applied (v5:123–129).
Arrays without recorded sex stay in these sets but drop out at model time (R2-COV complete case: sex + batch).
