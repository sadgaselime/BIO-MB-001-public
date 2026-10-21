# Synthetic pipeline run: synthetic_demo

> **SYNTHETIC DATA — NOT BIOLOGICAL EVIDENCE. Every value in this run was simulated from a known generative model. No real cohort data were used; no result here may be reported as a finding about Alzheimer's disease or any GEO dataset.**

## Run configuration

- Seed: `20261011`
- Contrast: `AD` − `CTL` (feature-level)
- Covariates: age, sex; design columns: `(Intercept)`, `group[AD]`, `age`, `sex[M]`
- FDR level: 0.05; CI level: 0.95
- Full configuration, software versions and file checksums: `provenance.json`.

## Synthetic cohort counts

| group | n_generated | n_analysed |
|---|---|---|
| AD | 60 | 60 |
| CTL | 60 | 60 |
| MCI | 20 | 0 |

## Sample-set rules applied

| rule | approval | source | n_in | n_removed | n_out |
|---|---|---|---|---|---|
| contrast_label_restriction | approved | D1/D2 approved 2026-10-10 (v7:604-605); Tier P1 non-contrast labels (v7:351) | 140 | 20 | 120 |

Input validation: **OK** (14 checks; `validation.json`).

## QC Stage A (synthetic cohorts only)

R8 under approved D5 option (b) with the D5 conventions (v5:149-202; v7:133, 608); R9 under the approved D22 P3 definition (v7:351), run separately per cohort. **QC Stage A remains blocked for real cohorts** (v7:625). Candidate exclusions below are **not applied** (exclusion-list approval scope unresolved, v5:123-129); flags and D18 referrals never exclude.

### Cohort statuses and V-A gate

| cohort_id | r8_status | r9_status | r9_stop_stage | va_gate_open | gated_analyses |
|---|---|---|---|---|---|
| SYN-MAIN | completed — informative | completed | — | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R9-CLEAN | not applicable | completed | — | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R9-ZERO-VARIANCE | not applicable | completed | — | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R9-MIN-ARRAYS-10 | not applicable | completed | — | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R9-MIN-ARRAYS-9 | not applicable | not applicable | A0 | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R9-NONFINITE-A1 | not applicable | not applicable | A4 | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R9-NEAR-IDENTICAL | not applicable | completed | — | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R9-NEGATIVE-MEDIAN | not applicable | not applicable | A4 | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R9-A3B-STOP | not applicable | not applicable | A3b | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R8-CATEGORIES | completed — informative | completed | — | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R8-UNINFORMATIVE | completed — uninformative | not applicable | A0 | False | not assessable — R8 |
| FX-R8-NOT-APPLICABLE | not applicable | completed | — | True | V-A gate open; primary-population log not started: exclusion-list approval scope unresolved (v5:123-129; v7:552); Q1/P3 candidates not applied |
| FX-R8-BLOCKED | blocked | completed | — | False | not assessable — blocked by R8 dependency |

### R9 outcomes per cohort (arrays)

| cohort_id | flagged | not_applicable | numerical_failure | passed | referred_d18 |
|---|---|---|---|---|---|
| FX-R8-BLOCKED | 0 | 0 | 0 | 12 | 0 |
| FX-R8-CATEGORIES | 0 | 0 | 0 | 24 | 0 |
| FX-R8-NOT-APPLICABLE | 0 | 0 | 0 | 12 | 0 |
| FX-R8-UNINFORMATIVE | 0 | 8 | 0 | 0 | 0 |
| FX-R9-A3B-STOP | 0 | 2 | 0 | 0 | 10 |
| FX-R9-CLEAN | 1 | 0 | 0 | 19 | 0 |
| FX-R9-MIN-ARRAYS-10 | 0 | 0 | 1 | 10 | 0 |
| FX-R9-MIN-ARRAYS-9 | 0 | 9 | 1 | 0 | 0 |
| FX-R9-NEAR-IDENTICAL | 0 | 0 | 0 | 14 | 16 |
| FX-R9-NEGATIVE-MEDIAN | 0 | 21 | 1 | 0 | 0 |
| FX-R9-NONFINITE-A1 | 0 | 10 | 12 | 0 | 0 |
| FX-R9-ZERO-VARIANCE | 0 | 0 | 1 | 19 | 0 |
| SYN-MAIN | 11 | 0 | 0 | 129 | 0 |

### Main cohort (SYN-MAIN) R8 categories

| r8_category | n |
|---|---|
| concordant_two_axis | 137 |
| discordant_two_axis | 3 |

### Candidate primary exclusions (PROPOSED — NOT APPLIED)

| cohort_id | array_id | candidate_tiers | r8_reason_code | r9_reason_code |
|---|---|---|---|---|
| SYN-MAIN | SYN-S0005 | Q1 | R8_DISCORDANT_TWO_AXIS | R9_PASSED |
| SYN-MAIN | SYN-S0098 | Q1 | R8_DISCORDANT_TWO_AXIS | R9_PASSED |
| SYN-MAIN | SYN-S0105 | Q1 | R8_DISCORDANT_TWO_AXIS | R9_PASSED |
| FX-R9-ZERO-VARIANCE | FX-R9-ZERO-VARIANCE-A01 | P3 | R8_NOT_APPLICABLE_A0 | R9_A0_ZERO_VARIANCE |
| FX-R9-MIN-ARRAYS-10 | FX-R9-MIN-ARRAYS-10-A01 | P3 | R8_NOT_APPLICABLE_A0 | R9_A0_ZERO_VARIANCE |
| FX-R9-MIN-ARRAYS-9 | FX-R9-MIN-ARRAYS-9-A01 | P3 | R8_NOT_APPLICABLE_A0 | R9_A0_ZERO_VARIANCE |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A01 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A02 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A03 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A04 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A05 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A06 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A07 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A08 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A09 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A10 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A11 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NONFINITE-A1 | FX-R9-NONFINITE-A1-A12 | P3 | R8_NOT_APPLICABLE_A0 | R9_A1_NONFINITE_MAJORITY |
| FX-R9-NEGATIVE-MEDIAN | FX-R9-NEGATIVE-MEDIAN-A12 | P3 | R8_NOT_APPLICABLE_A0 | R9_A3_MEDIAN_LE_MINUS1 |
| FX-R8-CATEGORIES | FX-R8-CATEGORIES-A06 | Q1 | R8_DISCORDANT_TWO_AXIS | R9_PASSED |

### Boundary fixtures

- **FX-R9-CLEAN**: R9 completes; A20 has a low correlation profile and is expected to be flagged (k = 3)
- **FX-R9-ZERO-VARIANCE**: A01 zero variance -> A0 numerical failure; one probe with a NaN is dropped
- **FX-R9-MIN-ARRAYS-10**: 11 arrays, 1 A0 failure -> exactly 10 remain: R9 proceeds (A0 and A3b boundaries met)
- **FX-R9-MIN-ARRAYS-9**: 10 arrays, 1 A0 failure -> 9 remain: R9 not applicable at A0; the A0 failure is retained
- **FX-R9-NONFINITE-A1**: A01-A12 have 11 of 21 pairs non-finite -> A1 numerical failures; their finite r_ij (= 0) still enter the medians of A13-A22 (fixed matrix), which become 0 -> S = 0 -> R9 not applicable at A4; A1 failures retained
- **FX-R9-NEAR-IDENTICAL**: A01-A16 near-identical clones: median r >= 1 - 1e-8 -> referred to D18 (Option C), not failures; A17/A18 are an A2 pair but their medians are ordinary -> A2-listed only, scored normally
- **FX-R9-NEGATIVE-MEDIAN**: A12 = exact negative of 11 identical arrays: m = -1 -> A3 numerical failure; the 11 identical arrays are A2 pairs (r = 1) but their medians are not near 1, so they are scored with equal z, giving S = 0 -> R9 not applicable at A4; the A3 failure is retained
- **FX-R9-A3B-STOP**: 12 arrays, 10 referred to D18 -> only 2 finite z_i -> R9 not applicable at A3b; referrals stay referrals
- **FX-R8-CATEGORIES**: R8 informative: A01 ambiguous; A06 two-axis discordant (Q1 candidate); A04 single-axis discordant; A03 single-axis (Y only) concordant; A07 unassessable (non-finite); A21 unassessable (recorded missing)
- **FX-R8-UNINFORMATIVE**: 8 arrays < 2·n_min: both axes degenerate -> completed — uninformative; V-A gate closed; R9 not applicable at A0 (< 10 arrays)
- **FX-R8-NOT-APPLICABLE**: only 1 distinct Y gene present -> R8 not applicable (A0); V-A gate open
- **FX-R8-BLOCKED**: external dependency unresolved -> R8 blocked; R9 still runs, outputs unusable until the gate opens

## Method

D8-approved method: limma::lmFit on one shared design (intercept, case indicator, covariates), then limma::eBayes(trend = TRUE, robust = FALSE) with all other arguments at their defaults; moderated t with df.total; two-sided p-values; 95% CI from topTable(confint = 0.95), i.e. coefficient ± qt(0.975, df.total) × moderated SE; Benjamini–Hochberg across all features in the fit. Run via R/limma_de.R in the pinned renv environment (R 4.6.1, Bioconductor 3.23, limma 3.68.5).

## Results (synthetic): 52 of 2014 features with BH q < 0.05

**Population: QC-unfiltered contrast set — not the primary population.** The primary-population log cannot start while the exclusion-list approval scope is unresolved (v5:123-129; v7:552), so QC candidate exclusions (Q1, P3) are included here; see `de_population.json`.

Top 15 by p-value. `estimate` is the adjusted synthetic AD − CTL difference on the simulated log2-like scale.

| rank | feature_id | estimate | ci_low | ci_high | std_error | t_statistic | p_value | q_value_bh |
|---|---|---|---|---|---|---|---|---|
| 1 | SYN-P01716 | -0.9951747515 | -1.107562101 | -0.8827874016 | 0.05678530516 | -17.52521623 | 1.927560821e-35 | 3.882107493e-32 |
| 2 | SYN-P01382 | -0.9539934572 | -1.064748783 | -0.8432381315 | 0.05596070173 | -17.04756066 | 2.211080227e-34 | 2.226557788e-31 |
| 3 | SYN-P01392 | 1.061570014 | 0.9373448156 | 1.185795213 | 0.06276654646 | 16.91299067 | 4.418980247e-34 | 2.966608739e-31 |
| 4 | SYN-P01532 | 1.009943409 | 0.8903937001 | 1.129493118 | 0.06040418881 | 16.71975783 | 1.198956578e-33 | 6.036746371e-31 |
| 5 | SYN-P01459 | -1.063163083 | -1.199429294 | -0.9268968716 | 0.06885043913 | -15.44163111 | 9.870739096e-31 | 3.975933708e-28 |
| 6 | SYN-P00440 | 1.043827425 | 0.909419611 | 1.178235238 | 0.06791145725 | 15.37041711 | 1.442723123e-30 | 4.842740616e-28 |
| 7 | SYN-P01804 | 1.231164877 | 1.062535455 | 1.399794298 | 0.08520241077 | 14.44988311 | 2.046532058e-28 | 5.888165093e-26 |
| 8 | SYN-P01750 | -1.052815642 | -1.198422125 | -0.9072091584 | 0.07356974422 | -14.31044314 | 4.367570604e-28 | 1.0995359e-25 |
| 9 | SYN-P00269 | 0.987929879 | 0.8467301378 | 1.12912962 | 0.07134317519 | 13.84757374 | 5.480057126e-27 | 1.226315006e-24 |
| 10 | SYN-P00246 | 0.9893550473 | 0.8415649571 | 1.137145138 | 0.07467304267 | 13.24915943 | 1.482502796e-25 | 2.985760632e-23 |
| 11 | SYN-P00891 | -1.136807906 | -1.3091385 | -0.9644773117 | 0.08707248096 | -13.0558805 | 4.326891065e-25 | 7.922144186e-23 |
| 12 | SYN-P01519 | -0.9827497399 | -1.134699126 | -0.8308003533 | 0.07677458623 | -12.80045635 | 1.789242375e-24 | 3.002945119e-22 |
| 13 | SYN-P01697 | -1.018363604 | -1.177484685 | -0.8592425235 | 0.08039818657 | -12.66649968 | 3.773326975e-24 | 5.845754253e-22 |
| 14 | SYN-P01489 | 1.117319331 | 0.9389457091 | 1.295692954 | 0.09012580667 | 12.39732961 | 1.695374485e-23 | 2.438917294e-21 |
| 15 | SYN-P00133 | 1.114590106 | 0.9342225303 | 1.294957681 | 0.0911332799 | 12.2303302 | 4.314822848e-23 | 5.793368811e-21 |

## Planted-signal recovery (simulation check only)

- fdr_level: 0.05
- n_features: 2014
- n_planted_group_features: 50
- n_called_q_below_level: 52
- true_positives: 50
- false_positives: 2
- observed_false_discovery_proportion: 0.038461538461538464
- sensitivity: 1.0
- true_positives_with_correct_sign: 50
- planted_effects_inside_ci: 47
- null_features_ci_covering_zero: 1868
- n_null_features: 1964

## Deferred pending scientific approval (not implemented in this run)

- **QC Stage A on real cohorts (R8, R9)**: implemented for synthetic cohorts only (qc_stage_a.py); refused for real cohorts (QC Stage A may not start until the remaining D22 items are approved (v7:625))
- **Applying QC candidate exclusions (P3, Q1)**: computed and listed, not applied (exclusion-list approval scope unresolved (v5:123-129))
- **Duplicate / near-identical review (D18)**: not implemented (D18 partially approved (v7:621))
- **R2-COV covariate exclusions (Tier P4)**: not implemented; missing covariates fail validation instead (v7:351)
- **Precedence rule for sample sets**: not implemented (v7 §5.2, proposed (D18/D16))
- **Sensitivity sample sets S1-S16**: not implemented (D16 unapproved)
- **Exclusion-list approval step**: not implemented (v5:123-129, unresolved)
- **Probe-to-gene collapsing and gene-level family**: not implemented (feature level only) (D6 unresolved)

> SYNTHETIC DATA — NOT BIOLOGICAL EVIDENCE. Every value in this run was simulated from a known generative model. No real cohort data were used; no result here may be reported as a finding about Alzheimer's disease or any GEO dataset.
