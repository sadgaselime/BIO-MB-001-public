# BIO-MB-001 — Statistical Analysis Plan, DRAFT v3 (Phase 3B, specification review)

**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen. No decision (D0–D22) is approved and no
approval-gate condition is passed.** v1 (`reports/phase3b/v1/…`) and v2 (`reports/phase3b/v2/…`) are
preserved unchanged. v3 is a specification refinement of v2; where a v2 section is not restated here
it carries over unchanged and is cited as **[v2 §n]**.

Nothing in this document has been executed:

- No differential-expression, pathway, feature-selection, QC-statistic or predictive computation has
  been run.
- No sample is excluded or relabelled.
- No final analysis population, count, threshold or model exists.
- No disease-association result has been produced or viewed.

**Scientific question (unchanged).** Which blood-based molecular features distinguish Alzheimer's
disease from controls reproducibly across cohorts, and to what extent are they specific relative to
another neurodegenerative disease? Study title, objectives, hypotheses H1–H3 and estimand proposal
are unchanged from [v1 §1], [v2 §2–3].

Labels:

| Label | Meaning |
|---|---|
| **[PROPOSED]** | A choice this draft suggests, requiring approval |
| **[PROPOSED (no source)]** | A rule suggested here without an existing source |
| **[EVIDENCE]** | Supported by a cited report or verified local file |
| **[DECISION NEEDED]** | No single answer is determined by the evidence |
| **[DATA NEEDED]** | Requires information not available locally |
| **[GAP]** | Can be closed later from metadata or probe-ID lists, without disease-association results |
| **[UNRESOLVED]** | Could not be verified locally |

Reference keys as in v2: [2A]–[2D]; [3A] (facts F1–F14, estimands E1–E3, options, gate G1–G9);
[P1] = `data/processed/<GSE>/phenotype_table.tsv`; [v1], [v2].

---

## 0. Change log from v2

| # | Area | Change |
|---|---|---|
| 1 | D7 identifiability | Replaced the v2 response tree. Distinguishes an estimable contrast from perfect and near-perfect confounding. Blocking (`duplicateCorrelation`) and omitting chip are **no longer** presented as remedies for perfect confounding. Adds a **stop / report-limitation rule** and a list of required metadata-only checks, with no results claimed (§5) |
| 2 | D5/D22 QC | Full algorithms for the sex check and the array-outlier check (§4), covering: required inputs; deterministic classification; handling of non-finite Fisher-z values and of zero or non-finite robust scale; minimum-size and failure rules; and a two-stage separation between blind computation and descriptive review. Thresholds are stated to be internal to each dataset and not externally validated |
| 3 | D6/D12/D14/D15/D20 | New end-to-end ordering from annotation to signature lock (§6). Covers: one-representative-probe-per-gene rule with deterministic tie-breaking; gene-level multiplicity family; the 200 cap counts unique Entrez genes; rules for empty, up-only and down-only signatures; individual-gene vs composite replication; gene-level pathway statistic and exact universe. Versions remain unpinned |
| 4 | D13 specificity | States what GSE99039 can and cannot establish. Significant-AD plus non-significant-PD is explicitly not evidence of specificity. Lists scale-comparability limits and the claims that stay descriptive (§8) |
| 5 | R2 eligibility | v2's "age and sex non-missing" condition was GSE63060-specific. v3 separates identity rules (all cohorts) from per-analysis covariate completeness, with a cohort-by-cohort table. **New metadata facts:** GSE140829 has no participant-code field and contains 4 arrays described as "replicate 2"; GSE99039 has a `subject_id` field (§3) |
| 6 | D19 GSE140829 mapping | Separates what is established locally from what needs an approved resource. **Correction to v2 §5.1:** the GSE140829 raw file contains all **16** of the 16 sex-probe IDs checked, not "15". Presence in the nuID-keyed Series Matrix remains unverified (§7) |
| 7 | Register | D0–D22 retained with the same identities; entries updated. No new IDs (§10) |
| 8 | Back matter | Separate lists of (a) decisions needing PI approval and (b) metadata-only checks to run later (§11, §12) |

### 0.1 Local evidence gathered while preparing v3 (metadata and identifiers only)

All of the following came from phenotype tables or probe-identifier columns. No expression value was
read into any calculation.

| Check | Result |
|---|---|
| Missing age, sex and batch by deposited diagnosis, per cohort | Tabulated in §3.2 from [P1] |
| Identifier fields per cohort | GSM, title, description, `participant_id`, GSE99039 `char:subject_id` |
| GSE140829 Series Matrix ID column | Streamed for IDs only: 47,008 rows, every ID 18 characters long, none `ILMN_`-prefixed |
| GSE140829 raw-data file | `PROBE_ID` column and header: 47,231 rows; 13 non-sample columns (PROBE_ID plus 12 annotation columns); no nuID or probe-sequence column |
| GSE140829 sex probes | 16 sex-probe IDs looked up in the raw `PROBE_ID` column: all present |
| `GSE63061_RAW.tar` contents (in memory) | Listed: two GPL10558 v4 manifests (R1, R2). The R2 header was read: it includes a `Probe_Sequence` column; 47,323 probes; dated 15/4/2010 |
| Diagnosis labels | Re-tabulated; match v2 §4.3 |

---

## 1. Inputs and limitations (unchanged from [v2 §1], restated)

- **Notion:** the Notion Analysis Plan / Statistical & Validation Plan, if one exists, has not been
  reviewed; no Notion page was read or edited (D0).
- No hypotheses, analysis-plan or validation-plan document exists in the project.
- Software: R/Bioconductor is not installed. Nothing was installed for this draft.

## 2. Estimand and unresolved discrepancies (unchanged; see [v2 §3])

- Proposed primary estimand: **E2**, the deposited-label difference (GEO `status` "AD" vs "CTL") in
  GSE63060 (D1).
- Deposited diagnosis is distinct from diagnosis at blood collection. No sample is relabelled or
  called a converter.
- Unresolved discrepancies H1–H9 ([v2 §3.3]) remain unresolved and must be reported with any result:
  - H1: ~41 deposited "AD" were likely MCI at draw.
  - H2: 21 samples are aged under 65.
  - H3: 80 vs 77 MCI.
  - H4: the code convention is undocumented.
  - H5: submitter QC is unidentifiable.
  - H6: Sood control counts.
  - H7: Patel exclusions are unpublished.
  - H8: normalization probably included removed arrays.
  - H9: participant independence across series.

---

## 3. Eligibility — R2 reconciled across cohorts (correction 5)

### 3.1 Principle

v2 §4.2 combined two different things in R2: *identity* (one record = one distinct array from one
distinct participant) and *covariate completeness* (age and sex present). v3 separates them:

- **R2-ID (identity, every cohort)** [PROPOSED]:
  1. The GSM accession is unique.
  2. The array identifier is unique (barcode from `title`, or the title string where no barcode
     exists).
  3. Where the cohort has a participant-identifier field, that identifier is unique among arrays
     entering the same contrast.
  4. Where the deposited metadata itself marks repeated arrays (e.g. "replicate 2"), the repeat is
     handled under D18.

  Identity is **never** inferred from age, sex, site, diagnosis or aggregate counts.
- **R2-COV (covariate completeness, per analysis)** [PROPOSED]: a sample enters a given model only if
  every covariate *of that model* is non-missing (complete case). This is a property of each analysis,
  not a cohort-wide eligibility rule. The number lost to each missing covariate is reported for every
  analysis. No covariate is imputed unless separately approved (D13, D19).

The GSE63060 situation (all fields complete) is therefore **not** imposed on other cohorts as an
eligibility rule.

### 3.2 Cohort-by-cohort identity and missingness [EVIDENCE, P1]

| Cohort | Participant identifier available | Identity facts | Missing age | Missing sex | Missing batch / chip |
|---|---|---|---|---|---|
| GSE63060 (discovery) | `description` code (undocumented, H4) | GSM, barcode, code each unique (329/329) | 0 | 0 | 0 (chip from barcode) |
| GSE63061 (consistency) | `description` code (undocumented) | GSM, barcode, code each unique (388/388) | 0 | 0 | 0 (chip from barcode) |
| GSE140829 (replication candidate) | **None.** `participant_id` empty for all 587; `description` holds only "replicate 1" (583) or "replicate 2" (4); the bracketed token in `title` is identical for all 587 | GSM unique; barcode unique (587/587) | 0 | 0 | 0 (`char:batch`) |
| GSE99039 (specificity) | `char:subject_id` | GSM and title unique; `subject_id` unique for 550, missing for 8 (all 8 are HD_HD_BATCH, already excluded by R5) | see below | see below | 0 (`char:batch`) |

GSE99039 missingness by deposited label (`char:age at exam`, `char:Sex`):

| Label | n | Age missing | Sex missing |
|---|---|---|---|
| IPD | 205 | 85 | 14 |
| CONTROL | 233 | 114 | 21 |
| GPD | 41 | 21 | 0 |
| GENETIC_UNAFFECTED | 22 | **22 (all)** | 3 |
| OTHER_NEURO (all labels) | 49 | 24 | 7 |
| HD_HD_BATCH (excluded, R5) | 8 | 8 | 8 |

### 3.3 GSE140829 "replicate 2" arrays [EVIDENCE + DECISION NEEDED, D18]

- **Verified:** 4 arrays are deposited with description "replicate 2": AD 1, Control 1, MCI 2.
  2 of the 4 therefore fall within the AD–control replication contrast.
- **Interpretation (unverified):** "replicate 2" suggests a second array from a participant whose
  first array ("replicate 1") is also deposited. The metadata contain no field that identifies the
  partner array, so the pairing **cannot be established**. It must not be inferred from age, sex,
  diagnosis or batch.
- **Options (D18):**
  - (a) [PROPOSED] exclude the 4 "replicate 2" arrays from all contrasts. Under the interpretation
    above, this leaves one array per participant. If the interpretation is wrong, 4 independent
    arrays are lost (2 within the contrast).
  - (b) Include all arrays, accepting possible non-independence of up to 4 pairs.
  - (c) (a) as primary, (b) as sensitivity.

  Data-owner clarification would resolve this (D9).

### 3.4 Which missing fields affect which analysis

| Analysis | Cohort | Covariates (proposed) | Effect of missing fields |
|---|---|---|---|
| Primary discovery | GSE63060 | age, sex, chip | None (complete) |
| S1 age restriction (≥65; 61–88) | GSE63060 | as primary | None |
| Consistency | GSE63061 | age, sex, chip | None; 6 ambiguous labels excluded by R5, not by R2 |
| Replication | GSE140829 | age_at_draw, Sex, batch | None from covariates; D18 affects 2 contrast arrays |
| S1(b) shared age range | GSE140829, GSE63061 | as above | None (age complete) |
| Sex check R8 | GSE63060, GSE63061, GSE140829 | — | Recorded sex complete; GSE140829 also needs probe mapping (§7) |
| Specificity primary (IPD vs CONTROL; sex + batch) | GSE99039 | Sex, batch | Complete case loses **35** (IPD 14, CONTROL 21) of 438 |
| Specificity age-adjusted sensitivity | GSE99039 | age, Sex, batch | Complete case loses age-missing (IPD 85, CONTROL 114) plus any remaining sex-missing; at most 239 remain. The exact count of samples missing age or sex or both is a [GAP] (§12) |
| GPD vs CONTROL | GSE99039 | Sex, batch | GPD sex complete; CONTROL loses 21 |
| GENETIC_UNAFFECTED vs CONTROL | GSE99039 | Sex, batch | Loses 3 GU + 21 CONTROL; **no age-adjusted analysis possible** (age missing for all 22 GU) |
| S1 age restrictions | GSE99039 | — | Not applicable as a cohort-wide restriction (age missing for 199/438 IPD/CONTROL); excluded from the shared range ([v2 §8]) |
| Sex check R8 | GSE99039 | — | Unassessable for the 35 + others with missing sex; GPL570 sex-probe IDs not verified locally [UNRESOLVED] |

**Not proposed by default:** using expression-derived sex as a covariate where recorded sex is
missing. It is possible, but it mixes a QC instrument with an analysis covariate (D13 alternative).

All other R-rules (R1, R3–R13) carry over from [v2 §4.1], with R5 label handling as in [v2 §4.3].

---

## 4. Sample QC algorithms — R8 and R9 (correction 2; D5, D22)

### 4.1 Common structure: two separated stages

| Stage | What it uses | What it must not use | Output |
|---|---|---|---|
| **Stage A — blind computation** | Expression values of the QC probes (R8) or of all deposited probes (R9); recorded sex (R8, step A5 only); array identifiers | Diagnosis, any case–control model, any association result | Per-array QC table, written and checksummed before Stage B |
| **Stage B — descriptive review** | Stage A table joined to chip/batch and to deposited diagnosis, **as counts only** | Any disease-association statistic; any change to Stage A parameters | Review table; reviewer's prespecified response; proposed exclusion list for approval |

Rules for both stages:

- Stage A parameters (probe lists, k, minimum sizes, numerical tolerances) are fixed in the approved
  SAP before Stage A runs. They are **not** changed after Stage B.
- **No sample is excluded solely because it is flagged.** Flags become proposed exclusions only
  through the D22 review, and exclusions only after the PI's approval of the list (R13).
- **Not externally validated.** Every boundary in this section is derived *within* each dataset from
  its own distribution. None comes from an external validation study, so classification error rates
  are unknown. Results are reported as "flagged by a dataset-internal rule".

### 4.2 R8 sex-consistency algorithm (Stage A)

**Required inputs:**

- The deposited Series Matrix matrix for the cohort, restricted to the prespecified sex probes, which
  must have been verified as present **in that Series Matrix** (not the manifest; §7).
- Recorded sex.
- All deposited arrays in the series, regardless of diagnosis (GSE63060: 329).

**Probe sets [EVIDENCE for GSE63060/GSE63061; see §7 for GSE140829]:**

- X marker: XIST ILMN_1764573.
- Y markers: the 13 probes listed in [v2 §5.1], covering 9 genes.

**Steps:**

- **A0 Applicability.**
  - If XIST is absent, or fewer than 2 distinct Y genes are present [PROPOSED (no source)], R8 is
    declared *not applicable* for that cohort. This is reported and no array is flagged.
  - Any array with a non-finite value in XIST, or in all Y probes, is classed **unassessable**
    (listed; not flagged as discordant).
- **A1 Y score.** For each Y probe, subtract its median across arrays with finite values. Y_i is the
  median of these centred values across the available Y probes for array i (finite values only).
  X_i is the XIST value.
- **A2 Per-axis threshold.** For X and for Y separately, choose the threshold t that minimizes the
  pooled within-class sum of squares when splitting the sorted finite values into a low and a high
  class (Otsu-type, exhaustive over all split points).
  - This is deterministic. Ties between split points are resolved by taking the lowest split index.
  - X-call: female-type if X_i > t_X, male-type otherwise. Y-call: male-type if Y_i > t_Y,
    female-type otherwise.
- **A3 Separation check (numerical/biological failure rule).** For each axis, compute
  D = |mean_high − mean_low| / sqrt((sd_high² + sd_low²)/2).
  - If either class contains fewer than 5 arrays, or D is non-finite, the axis is declared
    *non-separating*.
  - The minimum D required for separation is a **[DECISION NEEDED, D5]**. The draft records the
    measure but sets no value.
  - If an axis is non-separating, only the other axis is used, and every call from the cohort is
    labelled "single-axis".
  - If both axes are non-separating, R8 is *not applicable* for the cohort.
- **A4 Expression-derived sex.**
  - Female pattern: X-call and Y-call both female-type.
  - Male pattern: both male-type.
  - **Ambiguous:** the calls disagree (X high with Y high, or X low with Y low).
- **A5 Comparison with recorded sex** (recorded sex is the only metadata used in Stage A):

| Expression-derived | Recorded | Category |
|---|---|---|
| Female/male pattern | Same | Concordant |
| Female/male pattern | Opposite | **Discordant** |
| Ambiguous | Any | **Ambiguous** |
| Any | Missing | **Unassessable (recorded sex missing)** |
| — | — | **Unassessable (non-finite input)** |

**Stage A output (per array):** X_i, Y_i, the thresholds, D per axis, both calls, expression-derived
sex, recorded sex, category, and the applicability status.

**Proposed handling in Stage B (D22), not applied:**

- Discordant arrays: proposed for exclusion.
- Ambiguous arrays: listed; the PI chooses one prespecified option before Stage B: (i) exclude,
  (ii) retain, or (iii) retain in the primary analysis and exclude in sensitivity S5.
- Unassessable arrays: retained; listed.

Ambiguity can reflect sample mixture, sex-chromosome variation or technical failure; the plan does not
distinguish between these.

### 4.3 R9 array-outlier algorithm (Stage A)

**Required inputs:** the cohort's deposited Series Matrix (all arrays, all deposited probes).

**Steps:**

- **A0 Input integrity.**
  - Count non-finite values per probe and per array.
  - Probes with any non-finite value are dropped from R9 for all arrays; the number dropped is
    reported. The deposited GSE63060 matrix has no missing values ([2A] §1), but the rule is stated
    for all cohorts.
  - Arrays with zero variance across the remaining probes are classed **numerical failure**. They
    are removed from steps A1–A4 and listed for review.
  - If fewer than 10 arrays remain [PROPOSED (no source)], R9 is *not applicable* for the cohort.
- **A1 Correlations.** Pearson r_ij for every pair of remaining arrays, over the common probe set.
  - Any non-finite r_ij (not expected after A0) is recorded and omitted from that array's median.
    The number of omitted pairs per array is reported.
  - If more than half of an array's pairs are omitted, the array is classed numerical failure.
- **A2 Near-identical pairs.** Any pair with r_ij ≥ 1 − 10⁻⁸ [PROPOSED (no source)] is written to a
  separate list for the D18 technical-duplicate review. Such pairs are retained in A3.
- **A3 Per-array statistic.**
  - m_i = median over j ≠ i of r_ij, computed on the r scale. For an even count, it is the mean of the
    two middle values.
  - Then z_i = atanh(m_i). Taking the median before transforming avoids infinite pairwise Fisher
    values when some r_ij = ±1. For an odd count it equals the median of the transformed values,
    because the median commutes with monotone transforms.
  - If |m_i| ≥ 1 or z_i is non-finite, the array is classed numerical failure. It is removed from A4
    and listed.
- **A4 Robust centre and scale.** Over arrays with finite z_i: M = median(z_i);
  S = 1.4826 × median(|z_i − M|).
  - **If S = 0 or S is non-finite, the rule is not applicable for the cohort.** No array is flagged
    by R9, the condition is reported, and an alternative scale requires a new PI decision. The draft
    does not silently substitute another estimator.
- **A5 Flag.** Array i is flagged if z_i < M − k·S, with **provisional k = 3** (D5). Alternatives
  k = 2.5 and k = 4 are sensitivity S5 only. The rule is one-sided: only low concordance is flagged.

**Reference set and feature set:** all deposited arrays and all deposited probes, uncentred, as in
[v2 §5.2]. The alternatives there remain part of D5.

**Stage A output (per array):** m_i, z_i, M, S, k, the flag, the numerical-failure class, the count of
omitted pairs, and the near-identical-pair list.

**Stage B (D22), descriptive only:**

- Tabulate flags and numerical failures by chip/batch and by deposited diagnosis, as counts.
- If flags concentrate in one diagnosis or one chip, the response must already be chosen from a list
  fixed beforehand:
  - (i) proceed with the proposed list;
  - (ii) recompute A1–A5 within chip (requires a prespecified minimum chip size);
  - (iii) take no R9 exclusions in the primary analysis and treat R9 exclusion as sensitivity only.
- "Concentrated" requires a definition before Stage B [DECISION NEEDED, D22]. No inferential test of
  flag-by-diagnosis association is proposed.

Limitations of R9 are as in [v2 §5.2]: diagnosis or batch structure can drive flags, and outliers can
mask each other.

---

## 5. Model identifiability — D7 (correction 1)

### 5.1 Definitions

Let X be the design matrix of the proposed primary model: intercept, group indicator (AD vs CTL), age,
sex and chip indicators. It is restricted to the samples entering the model, i.e. after the approved
R-rules and QC.

| Situation | Definition | Consequence |
|---|---|---|
| **Estimable contrast** | The group column is not a linear combination of the other columns: rank(X) = rank(X without group) + 1 | The AD–CTL coefficient is identified. With chip as a fixed effect, the information comes only from chips containing both groups ("mixed chips") |
| **Perfect confounding** | Every chip with samples in the model contains only one group, so the group column lies in the span of the chip indicators | **The disease contrast is not estimable** with chip adjustment. No data-analytic method can separate disease from chip from these data |
| **Near-perfect confounding** | Estimable, but the group information rests on few mixed chips or few samples on mixed chips; the variance inflation of the group coefficient is large | Identified but fragile: the estimate is imprecise and depends on a few chips. It requires a prespecified threshold rule (§5.3) |

**Why the v2 remedies are not remedies under perfect confounding:**

- **Blocking (`duplicateCorrelation`, chip as a random effect).** This makes the group contrast
  "estimable" only by comparing *between* chips. It assumes chip effects are random, exchangeable and
  independent of diagnosis, and that assumption is exactly what perfect confounding makes untestable.
  The resulting estimate is still a disease-plus-chip difference.
- **Omitting chip.** This produces an estimate of disease plus chip with no adjustment. Its bias is
  unknown in sign and size.
- Neither is an automatic solution. v3 removes both from the default response. Each could only be
  reported, if at all, as an explicitly labelled, non-primary analysis with separate PI approval.

### 5.2 Required metadata-only checks before fitting any expression model [GAP — not yet run]

None of these checks has been run. **No results are reported or assumed here.**

**Inputs:** the approved sample list, deposited diagnosis, recorded age and sex, and chip (from the
`title` barcode prefix) or batch (`char:batch`). No expression values.

| # | Check | Output |
|---|---|---|
| M1 | Group × chip contingency table | Counts per chip per group |
| M2 | Mixed-chip summary | Number of mixed chips; AD and CTL counts on mixed chips; count and proportion of samples on single-group chips |
| M3 | Rank test | rank(X) and rank(X without group), by QR decomposition with a stated tolerance; also rank(X) for every sensitivity design (S1–S3, S5) |
| M4 | Group variance inflation | VIF_group = 1 / (1 − R²) from regressing the group indicator on the other columns of X (metadata only) |
| M5 | Residual degrees of freedom | n − rank(X) |
| M6 | Singleton chips | Chips with one sample in the model |
| M7 | Chip × site table | For S3 only; site from the code prefix |
| M8 | Covariate balance | Age and sex by group and by chip (descriptive) |

**When and where they run:**

- **Timing:**
  - Run once on the R3-eligible set before QC, for information only.
  - Run again, **definitively**, on the approved post-QC population. The response in §5.3 is applied
    only to the definitive run.
  - Both runs happen before any expression model is fitted.
- **Cohorts:** GSE63060 (chip, 29 levels), GSE63061 (chip, 34 levels), GSE140829 (batch, 19 levels),
  and GSE99039 (batch, 37 levels; per specificity contrast).

### 5.3 Prespecified response (fixed before M1–M8 are run) [PROPOSED; thresholds DECISION NEEDED, D7]

| Result of the definitive checks | Response |
|---|---|
| Group column aliased (perfect confounding; M3 rank does not increase) | **STOP.** Declare the primary disease contrast not estimable under the approved design. Report M1–M6 and the limitation. Fit no substitute primary model. Any further analysis needs a new, separately approved protocol amendment and must be labelled non-primary |
| Estimable, but below the prespecified minimum information (any of: mixed chips < c₁, AD on mixed chips < c₂, CTL on mixed chips < c₂, VIF_group > c₃) | **STOP / report limitation** as above. The values c₁–c₃ are **not set in this draft**; the PI must set them before the checks run |
| Estimable and meets the minimum information | Fit the primary design with chip as a fixed effect. Report M1–M6 alongside results |
| A nuisance column is aliased (e.g. chip with site in S3; a covariate constant within the model) but group is not | Drop the aliased nuisance column by a prespecified rule: drop the later-listed term in the order group, age, sex, chip, site. Report it. Group is never dropped |
| Singleton chips | Retained; they contribute no within-chip information under a fixed effect. Reported |

- The same rule applies, with batch in place of chip, to GSE63061, GSE140829 and each GSE99039
  contrast. For a validation cohort, a STOP means "replication not assessable in that cohort", not a
  negative result.
- No response is chosen or revised after expression results exist.

### 5.4 Covariates and remaining model specification

Unchanged from [v2 §7.1, 7.4–7.5]:

- limma (trend = TRUE) is a candidate pending D8.
- Covariates are age (linear), sex and chip; site is sensitivity only.
- Effect is AD − CTL on the deposited scale.
- BH FDR over tested probes.

v2's §7.3 tree is withdrawn and replaced by §5.3 above.

---

## 6. Probe-to-gene mapping, signature and pathways (correction 3; D6, D12, D14, D15, D20)

### 6.1 Order of operations [PROPOSED]

Each step is completed and its output versioned and checksummed before the next starts. Steps 1–5 use
no association information.

1. **Annotation lock (D6).** Choose and pin the annotation resource and version (unpinned in this
   draft). Produce a probe → Entrez table for each platform. Each probe is classed as:
   - *one-to-one* (one Entrez ID);
   - *multi-mapped* (more than one Entrez ID);
   - *unmapped*.
2. **Population and QC lock** (R-rules, §4, R13).
3. **Identifiability checks and response** (§5).
4. **Feature rules** (D17; proposed: none beyond the deposited set).
5. **Representative-probe table (diagnosis-blind).** Among the one-to-one probes of each Entrez gene
   that pass step 4, select the probe with the highest mean expression across all samples entering
   the primary model.
   - Deterministic tie-break: probe ID in ascending lexicographic order.
   - The table is written before any model is fitted.
6. **Probe-level discovery.** Fit the model to every probe passing step 4 (including multi-mapped
   and unmapped probes). Apply BH across **all tested probes**. This is the primary inferential
   family for probe-level claims.
7. **Gene-level discovery table.**
   - Each Entrez gene takes the statistics of its representative probe from step 6.
   - BH is re-applied across representative probes: one test per gene, so the gene-level family is
     the set of genes with a representative probe.
   - Gene-level claims use this q value. Probe-level claims use the step-6 q value.
   - The two families are reported separately and never mixed.
8. **Signature selection and lock** (§6.3).
9. **Validation mapping** (§6.4), then **validation testing** (§6.5).
10. **Pathways** (exploratory; §6.6).

### 6.2 Duplicate probes per gene — handling by analysis

| Analysis | Probes mapping to the same gene |
|---|---|
| Probe-level discovery | All probes tested and reported individually. Each probe's gene annotation is shown. Multi-mapped and unmapped probes are included |
| Gene-level discovery | Representative probe only (step 5). Other probes of the same gene are reported in a supplementary table. Genes with significant probes of **opposite** direction (step-6 q < 0.05) are flagged as "probe-discordant" |
| Signature | One entry per Entrez gene (the representative probe). Multi-mapped and unmapped probes are not eligible |
| Validation | One probe per signature gene per validation cohort (§6.4) |
| Pathways | One statistic per Entrez gene (representative probe) |

**Accepted consequence:** a gene whose representative probe is non-significant while another probe
is significant is not in the signature. The highest-mean rule is diagnosis-blind, which keeps the
selection valid, at the cost of possibly missing isoform-specific signals ([v2 §6.3]).

### 6.3 Signature construction [PROPOSED; D15]

- **Eligibility:** genes with gene-level q < 0.05 (step 7). The threshold is D15.
- **Direction:** the sign of the representative probe's AD − CTL effect.
- **Ranking (deterministic):**
  1. gene-level q ascending;
  2. then |effect| descending;
  3. then |moderated t| descending;
  4. then Entrez ID numerically ascending.
- **Cap:** the top **200 unique Entrez genes** (if the cap is retained, D15). Gene uniqueness is
  guaranteed by construction, since each gene has one representative probe, and is asserted at lock
  (zero duplicate Entrez IDs). The cap never counts probe records.
- **Lock file** (before any validation-cohort expression is modelled against diagnosis):
  - Entrez ID, symbol, representative probe and its gene-level statistics, direction and rank.
  - The annotation resource and version.
  - The counts of eligible, up and down genes.
  - Checksum.
- **Empty and one-sided signatures (prespecified):**

| Case | Response |
|---|---|
| No eligible genes | No signature. Report "no gene met the prespecified discovery threshold". Replication (C-a, C-b, C-c) and signature-based specificity are **not run**. The threshold is **not relaxed**; any relaxed-threshold analysis would be a new, labelled exploratory analysis needing approval |
| Only up-regulated, or only down-regulated, genes | Signature locked as one-directional. C-c score = mean z of the available direction (sign-adjusted so that the expected AD − CTL difference is positive). Reported with the limitation that a one-directional score is more sensitive to global shifts (normalization, cell composition) |
| Fewer than 10 genes [PROPOSED (no source)] | Signature locked as is. C-c and C-b are run but labelled "low gene count" |

- **Platform coverage at selection.** By default, genes are **not** restricted to those mappable on
  the validation platforms (coverage is reported instead). Alternative: restrict eligibility to genes
  annotated on every validation platform. This is decided from annotation only and is acceptable if
  prespecified (D15).

### 6.4 Validation-cohort mapping (D6, D19)

For each validation cohort and each locked gene:

- Map the Entrez ID through that platform's pinned annotation.
- Select the gene's representative probe in that cohort by the same diagnosis-blind, highest-mean rule
  over its eligible samples, with the same tie-break.
- Alternative (S8b): use the identical Illumina probe ID if it is **present in that cohort's Series
  Matrix** (verified from the matrix's ID column, not from a manifest or raw file). Otherwise fall
  back to the highest-mean rule.

Unmeasurable categories as in [v2 §9.3].

### 6.5 Individual-gene vs composite replication (D12, D20)

| | Individual-gene replication (C-a) | Composite-score replication (C-c) | Direction concordance (C-b) |
|---|---|---|---|
| Question | Which locked genes show the discovery direction in the validation cohort? | Does the locked signature as a whole separate AD from controls? | Is direction agreement across tested genes greater than chance? |
| Unit | Each tested locked gene | One score per sample | The set of tested genes |
| Test | Validation model per gene; one-sided in the locked direction; BH across tested locked genes | Score = mean z(up) − mean z(down). z is computed per representative probe across all eligible validation samples (diagnosis-blind). The score is modelled with the cohort's covariates; one-sided | Statistic: proportion of tested genes with concordant sign. Null: diagnosis labels permuted within batch strata (≥10,000 permutations, fixed seed), refitting each time |
| A positive result supports | "Gene g replicated" | "The signature replicated as a composite" | "Directional transfer above chance" |
| A positive result does **not** support | That the composite replicates | That any particular gene replicates | That any gene or the score replicates |

- **Proposed hierarchy (D20):** C-c primary; C-b and C-a secondary ([v2 §9.4]).
- Permutation within batch strata preserves the batch–diagnosis structure but not the age and sex
  associations; this limitation is reported.
- GSE63061 results go under "consistency"; GSE140829 under "replication (independence unverified)"
  ([v2 §9.1]).

### 6.6 Pathways (exploratory; D14)

- **Gene-level statistic:** the moderated t of each gene's representative probe from the discovery
  model (step 7). One value per Entrez gene.
- **Tested-gene universe:** exactly the Entrez genes with a representative probe at step 5, i.e.
  one-to-one mapped, passing feature rules, and tested at step 6. Multi-mapped and unmapped probes
  are outside the universe. The universe size is reported.
- **Gene sets:** intersected with the universe *before* the size limits (proposed 15–500) are
  applied. Sets outside the limits after intersection are not tested; their number is reported.
- **Methods (options, D14):**
  - Pre-ranked competitive test on the moderated t, allowing for inter-gene correlation (e.g.
    `cameraPR`).
  - `camera` on the representative-probe matrix with the discovery design.
  - Over-representation of signature-eligible genes (all genes at gene-level q < 0.05, before the
    cap), up and down separately, against the same universe.
- **Multiplicity:** BH within each collection × direction × method; nothing is pooled across them.
- **Versions:** nothing is pinned or guessed. The components to pin are listed in [v2 §11.2] and are
  unchanged.

---

## 7. GSE140829 probe mapping — D19 (correction 6)

### 7.1 Established from existing local files [EVIDENCE]

| Fact | Source |
|---|---|
| The Series Matrix data table has 47,008 rows; every ID is an 18-character string; none is an `ILMN_` ID (consistent with nuIDs; the encoding was not verified) | `GSE140829_series_matrix.txt.gz`, ID column only |
| The raw-data file has 47,231 probe rows keyed by `PROBE_ID` (`ILMN_…`), with `SYMBOL` and 11 other annotation columns. It has **no nuID column and no probe-sequence column** | `GSE140829_raw_data.txt.gz`, header and ID column |
| All 16 sex-probe IDs checked are present in the raw `PROBE_ID` column: XIST ILMN_1764573, the 13 Y probes of [v2 §5.1], NLGN4Y ILMN_2210199 and UTY ILMN_1651456. (v2 said "15"; corrected) | as above |
| Row counts differ (47,231 raw vs 47,008 Series Matrix), so **the two probe sets are not identical** | as above |
| A local GPL10558 (HT-12 v4) manifest, R2 dated 15/4/2010 with 47,323 probes, includes a `Probe_Sequence` column; an R1 manifest is also present | `GSE63061_RAW.tar` (read in memory) |

### 7.2 Not established; requires an approved resource or software [UNRESOLVED]

- **Whether any particular probe, including each sex probe, is present in the GSE140829 Series
  Matrix.** Presence in the raw file or in a platform manifest does **not** imply presence in the
  Series Matrix: the probe sets differ by 223 rows, and the reason is unknown.
- The ILMN → nuID correspondence. It needs one of:
  - (a) an approved mapping package (e.g. `lumiHumanIDMapping`, version to be pinned under D8);
  - (b) the GEO GPL15988 platform table (not downloaded; network not used);
  - (c) new code that derives nuIDs from the `Probe_Sequence` column of the local GPL10558 manifest
    and matches them to the Series Matrix IDs.

  Option (c) would itself require approval for new code, validation of the encoding against a
  reference implementation, and evidence that GPL15988 probes share sequences with the GPL10558
  manifest. **The GPL15988–GPL10558 relationship has not been verified locally.**
- That the nuID encoding is a deterministic, reversible encoding of probe sequence is **REPORTED**
  (lumi documentation, background knowledge). It was not verified in this project.

### 7.3 Consequences until resolved

- R8 cannot be applied to GSE140829. Its sex-check status is "not yet assessable".
- Gene-level replication in GSE140829 cannot be mapped.
- No GSE140829 analysis can proceed until D19 (and D8 if a package is chosen) is approved and the
  mapping is executed and checksummed.

---

## 8. Disease specificity — GSE99039 (correction 4; D13)

### 8.1 What the comparison can establish

- **Within GSE99039:** whether each locked AD-signature gene (and the composite score) differs between
  IPD and CONTROL. This is an internally valid comparison on one platform, subject to its covariate
  limits (§3.4). The same applies to GPD vs CONTROL and GENETIC_UNAFFECTED vs CONTROL, each kept
  separate.
- **After δ is approved:** whether a gene's PD effect is compatible with no meaningful PD association
  (equivalence, two one-sided tests at 90% CI within ±δ).

### 8.2 What it cannot establish

- **AD specificity.**
  - A significant AD effect in GSE63060 with a non-significant PD effect in GSE99039 is **not**
    evidence that the feature is specific to AD. A difference in significance is not a significant
    difference.
  - Non-significance may reflect low power, platform differences or covariate loss.
- **A direct AD-vs-PD comparison.** No cohort contains both AD and PD on the same platform. The
  AD × PD contrast and the difference between the AD and PD effects are **not estimable**.
- **Absence of a PD effect,** without an approved δ. Until then, the only allowed categories are
  "association with PD" and "association not demonstrated".
- **Specificity relative to other diseases.** GSE99039's OTHER_NEURO groups are small (1–19 per
  label). Any analysis of them is descriptive unless separately approved.

### 8.3 Scale comparability

- GSE99039 is Affymetrix GPL570 (RMA, log2, quantile). The AD cohorts are Illumina (lumi VST-type,
  and RSN for GSE140829). Probe designs, dynamic range and fold-change compression differ between
  these technologies. Different laboratories, populations, recruitment and sample handling add
  further non-comparability.
- Consequently, raw effect sizes (log-fold differences) are **not on a common scale** across cohorts.
  Standardized effects (e.g. Hedges' g) partly address scale but not technology-specific compression
  or noise. They are therefore also not treated as directly comparable.

**Claims that remain descriptive only:**

- comparisons of effect magnitude between AD and PD cohorts;
- statements such as "stronger in AD than in PD";
- the proportion of AD-signature genes also associated with PD;
- side-by-side forest plots across platforms.

### 8.4 Equivalence margin

δ remains **unresolved** (D13). It requires a scientific justification on a stated scale, for
example a minimal biologically meaningful standardized difference, before any "compatible with no
meaningful association" category can be used. This draft proposes no value.

---

## 9. Sensitivity analyses

S1–S13 are as in [v2 §8], with these v3 adjustments:

- **S5:** the k = 2.5 and k = 4 variants use the §4.3 algorithm unchanged otherwise. The
  ambiguous-sex variant follows the option chosen under §4.2.
- **S8(b):** identical-probe-ID matching requires verified presence in the target Series Matrix
  (§6.4).
- **D18 (new sensitivity):** GSE140829 with and without the "replicate 2" arrays (§3.3), if option (c)
  is chosen.
- Every sensitivity design must also pass the §5.2 M3 rank check. If a sensitivity design is not
  estimable, that sensitivity is reported as "not estimable" and is not modified.

---

## 10. Decision register (D0–D22; none approved)

Columns as in v2. Entries changed in v3 are marked †.

| ID | Question | Evidence available | Proposed default | Alternatives and consequences | Additional data? | Depends on | Approval before implementation |
|---|---|---|---|---|---|---|---|
| D0 | Is there a Notion or other plan to reconcile with? | Not reviewed | Provide the content for reconciliation | Conflicting plans | **Yes** | — | Yes |
| D1 | Primary estimand | [3A] §2; H1 | E2 with converter caveat | E1 infeasible without D9; E3 descriptive | For E1 | D9 | Yes |
| D2 | Eligibility and label rules (R2–R5, R12) † | §3; [v2 §4.3] | R2-ID for all cohorts; R2-COV per analysis; R5 as v2 | Cohort-wide completeness rules would drop GSE99039 samples unnecessarily | No | D1, D18 | Yes |
| D3 | Expression input (GSE63060) | [2A] §9 | Series Matrix, no re-normalization | Supplementary files (repairs; inferred labels) | No | — | Yes |
| D4 | Age eligibility | H2; S1 ranges | No restriction; S1(a) ≥65, S1(b) 61–88 | ≥65 excludes 21 with unexplained discrepancy | Owner explanation | D7 | Yes |
| D5 | QC algorithms and parameters † | §4 | §4.2 / §4.3 algorithms; k = 3; minimum Y genes 2; minimum arrays 10; near-identical tolerance 10⁻⁸; class minimum 5 | Separation threshold for D **not proposed**; alternative scale estimators only by new decision | No | D22 | Yes |
| D6 | Annotation and multi-probe policy † | [2A] §7; §6 | Unpinned resource; representative probe = highest mean, ties by probe ID; multi-mapped excluded from gene-level work | Resource choice changes coverage; identical-ID matching for Illumina pairs | Yes (resource) | D8 | Yes |
| D7 | Model and identifiability response † | §5 | Chip fixed effect if estimable with minimum information; **STOP and report limitation** otherwise | Blocking or omitting chip only as separately approved non-primary analyses; thresholds c₁–c₃ to be set | No (metadata checks M1–M8 first) | D4, D8 | Yes |
| D8 | Analysis environment | R absent | Pinned R/Bioconductor | Python alternative needs validation | No | — | Yes (installation itself) |
| D9 | Request data-owner information † | H1–H4, H9; §3.3 | Request diagnosis at draw, under-65 explanation, code convention, overlap, GSE140829 replicate pairing | Without it E1 is infeasible; D18 stays interpretive | **Yes** | — | Yes |
| D10 | Standard for calling GSE140829 independent | [3A] F13 | "Independence unverified" | Over-claiming | **Yes** | D9 | Yes |
| D11 | GSE140829 input | GEO processing | Series Matrix + batch; ComBat file as S13 | ComBat risks; 36 fewer samples | No | D19 | Yes |
| D12 | What counts as replicated † | §6.5 | C-a, C-b (permutation within batch), C-c as defined | Sign test anti-conservative | No | D15, D20 | Yes |
| D13 | Specificity strategy, covariates, δ † | §8; §3.4 | IPD vs CONTROL with sex + batch (complete case, −35); groups separate; δ unresolved; no specificity claim from significance differences | Age-adjusted sensitivity (≤239); expression-derived sex for missing sex (not default) | Justification for δ | D12 | Yes |
| D14 | Pathway framework † | §6.6 | Universe and statistic as §6.6; methods to choose; versions unpinned | Database and version change results | Yes | D6, D8 | Yes |
| D15 | Threshold, cap, coverage restriction † | §6.3 | q < 0.05; cap 200 unique Entrez genes; no coverage restriction; empty/one-sided rules as §6.3 | Lower cap; restricting to validation-mappable genes | No | — | Yes |
| D16 | Sensitivity set † | §9 | S1–S13 plus D18 variant | Post-hoc changes are selective reporting | No | D4–D7, D18, D21 | Yes |
| D17 | Additional expression filter | [v2 §6.1] | None in the primary analysis; 25th/50th percentile as S7 | Filtering trades power against coverage | No | D15 | Yes |
| D18 | Identity: participant codes, duplicate screen, GSE140829 replicates † | §3.1–3.3; §4.3 A2 | R2-ID; near-identical pairs reviewed; exclude GSE140829 "replicate 2" arrays (option a) | Include all (b); (a) + sensitivity (c) | Owner clarification | D9 | Yes |
| D19 | GSE140829 mapping and covariates † | §7 | Resolve the nuID mapping via an approved resource; until then R8 and gene mapping are not assessable | Package; GPL15988 table; new sequence-derived code (needs validation) | **Yes** | D8, D6 | Yes |
| D20 | Primary replication criterion | §6.5 | C-c primary; C-b, C-a secondary | C-b primary | No | D12 | Yes |
| D21 | Cell-composition method (S11) | No measured counts | Not proposed | Methods may remove disease signal | Yes | D8 | Yes |
| D22 | QC review procedure † | §4.1 | Two-stage: blind Stage A, descriptive Stage B; prespecified responses; no exclusion solely from flags | A "concentrated flags" definition is required; ad-hoc review risks bias | No | D5 | Yes |

**Approval gate ([3A] §5):** no condition is passed.

- **Not satisfied:** G1, G2, G5, G7, G8.
- **Partially satisfied:** G3, G4, G6, G9.

Improved wording does not change this status.

---

## 11. Decisions that genuinely require the PI's approval

These need scientific judgement; the evidence does not determine a unique answer.

| Decision | Choice required | Why the evidence does not settle it |
|---|---|---|
| D1 | Accept E2 (deposited label) as primary | Whether a deposited-label estimand answers the question is a scientific judgement |
| D4 | Age rule | Published criterion and deposited data conflict, with no explanation |
| D5 | Separation threshold for D; k; minimum sizes; tolerances | No external validation exists; all are conventions |
| D22 | Ambiguous-sex option; definition of "concentrated" flags; within-chip minimum size | Trade-off between protecting against technical artefacts and avoiding outcome-related exclusion |
| D6 | Annotation resource and representative-probe rule | Several defensible resources and rules |
| D7 | Minimum-information thresholds c₁–c₃; whether any non-primary analysis is permitted after a STOP | Bias–precision trade-offs not determined by data |
| D11 | GSE140829 input (Series Matrix + batch vs ComBat) | Both carry known risks |
| D12 / D20 | Replication criteria and hierarchy | The question does not fix composite vs per-gene primacy |
| D13 | δ, pooling rules, covariate set for GSE99039 | Requires a definition of a meaningful effect and clinical pooling judgements |
| D14 / D21 | Pathway method and databases; cell-composition method | Conventions with known sensitivities |
| D15 / D17 | FDR level, cap, coverage restriction, filtering | Power vs stringency |
| D16 | Final sensitivity set | Must be fixed before results |
| D18 | GSE140829 replicate handling | Pairing is not identifiable from metadata |
| D0 / D9 / D10 / D19 / D8 | Depend on external information or on installation approval | Not decidable from local evidence |

---

## 12. Checks that can be run later using metadata or probe-ID lists only

None of these has been run. Each needs only metadata or identifiers, and no disease-association
result.

1. **M1–M8 (§5.2)** for GSE63060, GSE63061, GSE140829 and the GSE99039 contrasts:
   - first on R3-eligible samples;
   - definitively on the approved post-QC population;
   - including M3 for every sensitivity design.
2. Exact complete-case counts per analysis (§3.4), including the GSE99039 age-or-sex-missing union
   for the age-adjusted sensitivity.
3. R2-ID uniqueness checks per cohort (GSM, array ID, participant ID where present), with explicit
   listing of GSE140829 "replicate 2" arrays and GSE99039 missing `subject_id`.
4. Sex-probe presence in each Series Matrix's ID column, once identifiers are mappable:
   - GSE140829 needs D19;
   - GSE99039 needs a GPL570 annotation to identify XIST and Y-gene probe sets [UNRESOLVED].
5. Explanation of the 223-row difference between the GSE140829 raw file and Series Matrix, once nuIDs
   are mappable (identifier comparison only).
6. Annotation coverage per platform after D6:
   - one-to-one, multi-mapped and unmapped probe counts;
   - expected universe size;
   - representative-probe candidates per gene (identifiers only; the mean-expression step is Stage A
     work after approval).
7. Coverage of the eventual locked signature on each validation platform (§6.4, unmeasurable
   categories). This requires only the lock file and identifier lists.
8. Gene-set size distribution after intersection with each platform's annotated gene universe
   (identifiers only).
9. Inventory of software and database versions once D8 is approved.

---

## 13. Reproducibility

Unchanged from [v2 §12]. In addition, the following are each versioned and checksummed when created:

- Stage A QC tables and Stage B review tables (§4.1);
- the M1–M8 outputs and the response applied (§5.3);
- the annotation lock and representative-probe table (§6.1 steps 1 and 5);
- the signature lock (§6.3).
