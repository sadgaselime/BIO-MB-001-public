# GSE99039: decisions needed for the Parkinson's specificity analysis (brief, 2026-10-20)

Noncanonical decision-preparation note. **Nothing here is approved.** The work behind it was read-only:
- Sample characteristics (diagnosis as counts only) and the feature-ID column were read from the GSE99039 Series Matrix.
- The pinned GPL570 Option A table (`reports/annotation_audit/gpl570_option_a/v2`) was queried.
- No submitter contact field was read, no expression value was read, and nothing was downloaded or installed.

## Already approved (not reopened)

- **D13**, conservative specification (v7:616):
  - two-sided Q1 score test;
  - Holm across the three contrasts;
  - no equivalence test and no Q2;
  - GENETIC_UNAFFECTED (GU) descriptive only;
  - the same coverage thresholds as the other cohorts;
  - S15 (age-adjusted) as defined.
- **Contrasts and covariates** (v6 §9.2, v7 §4.1):
  - IPD vs CONTROL is primary; GPD vs CONTROL is secondary; GU vs CONTROL is secondary and descriptive;
  - other labels are descriptive only;
  - covariates: sex and batch, complete case; S15 adds age at exam.
- **Gene mapping:** GPL570 Option A (D6-F, v7:609). 43,111 eligible present probe sets over 20,820 genes.
- **GSE99039 title rule** (v7:621): the title is checked for uniqueness only.
- **Claim rules** (v7 §8.1–8.2):
  - non-significance is never evidence of absence;
  - "AD-specific" is never claimed.

## Facts (Series Matrix, 558 arrays, platform GPL570, 37 batches)

| Label | Arrays | Sex recorded | Sex + age at exam (S15) | Batches (sex-complete) |
|---|---|---|---|---|
| CONTROL | 233 | 212 | 119 | 31 |
| IPD | 205 | 191 | 120 | 26 |
| GPD | 41 | 41 | 20 | 17 |
| GENETIC_UNAFFECTED | 22 | 19 | **0** | 7 |
| Other (HD 19, HD_HD_BATCH 8, MSA 8, PSP 8, DRD 3, DRD-DYT5 3, ATYPICAL_PD 3, CBD 2, PD_DEMENTIA 2, Vascular dementia 1) | 57 | — | — | — |

- GSM accessions and titles are unique.
- `subject_id` is present for 550 arrays and all 550 values are unique. The 8 arrays without one are all HD_HD_BATCH.
- Other fields present but not prespecified as covariates: `learning set` (the submitter's TRAINING/VALIDATION/TEST split),
  UPDRS, Hoehn & Yahr, MoCA (191 values are "0", which looks like a placeholder), age at first symptoms, and the mutated-gene field.

## Decision E-99: GSE99039 eligibility rules (analogue of the GSE140829 rules)

| Rule | Proposal |
|---|---|
| R1 universe | All 558 Series Matrix GSM columns |
| R2-ID | GSM accession unique. Title: uniqueness only (approved title rule). **`subject_id` designated the participant identifier**: an identical value would be a C1 D-1 candidate (none exist). A missing value (8 HD_HD_BATCH arrays) is recorded and is not an exclusion. |
| Contrast labels (R3/R4) | Read from `char:disease label` exactly as deposited: IPD, GPD, GENETIC_UNAFFECTED and CONTROL. All other labels are outside the specificity contrasts (P1) and reported descriptively. No relabelling, including of the mutated-gene field. |
| R2-COV | Sex and batch, complete case per model (losses: CONTROL 21, IPD 14, GU 3). S15 adds `age at exam` (GU has no S15 analysis; v3 §3.4). |
| Not used | `learning set`, UPDRS, H&Y, MoCA, age at first symptoms, mutated-gene field |

## Decision R8-570: sex-check probes on GPL570 (needed for R8 under V-A)

The R8 rule uses XIST plus the Y-chromosome genes of the approved Illumina probe set: RPS4Y1, DDX3Y, KDM5D, UTY, EIF1AY,
USP9Y, ZFY and TXLNGY (formerly CYorf15A/B). On GPL570, all of these have eligible Option A probe sets, and every one is
present in GSE99039:

| Gene | GPL570 probe sets (eligible, present) |
|---|---|
| XIST | 214218_s_at, 221728_x_at, 224588_at, 224589_at, 224590_at, 227671_at, 243712_at |
| Y genes | RPS4Y1 201909_at; DDX3Y 1570359_at, 1570360_s_at, 205000_at, 205001_s_at; KDM5D 206700_s_at; UTY 208067_x_at, 210322_x_at, 211149_at; EIF1AY 204409_s_at, 204410_at; USP9Y 206624_at, 228492_at; ZFY 207246_at, 230760_at; TXLNGY 214131_at, 223645_s_at, 223646_s_at, 232618_at, 236694_at |

**Options** (the R8 algorithm, thresholds and the D5 option (b) rule are unchanged; only the probe definition is new):
- **R8-570a (recommended):**
  - X axis = the mean of the XIST probe sets, excluding `_x_at` probe sets;
  - Y axis = all listed Y probe sets, excluding `_x_at`.
  - Affymetrix marks `_x_at` probe sets as possibly cross-hybridizing. Excluding them is decided here, before any expression is read.
  - That leaves 6 XIST probe sets and 18 Y probe sets over 8 genes.
- R8-570b: all listed probe sets, including `_x_at`.

R8 can't assess arrays with no recorded sex (53, including 21 CONTROL and 14 IPD); they are recorded as such.

## What follows once E-99 and R8-570 are approved

Each step reuses tested runners:
1. eligibility, then C1 duplicate review, then QC Stage A/B;
2. the rule-applied exclusion list comes back to you for approval;
3. the specificity run: Q1 for each contrast with Holm across the three, per-gene two-sided BH within each contrast, and the S15 sensitivity.

Results will be worded as "association with PD (same or opposite direction to AD)" or "association not demonstrated".
"AD-specific" is never used.
