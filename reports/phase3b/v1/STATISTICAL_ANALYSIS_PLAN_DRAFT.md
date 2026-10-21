# BIO-MB-001 — Statistical Analysis Plan, DRAFT v1 (Phase 3B)

**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen.** Nothing in this document has been
executed: no differential-expression, pathway, feature-selection or predictive analysis has been run,
no sample has been excluded, and no final sample count is frozen. Every method choice is provisional
until the decisions in section 11 are approved.

Labels: **[PROPOSED]** (a choice this draft makes, requiring approval), **[EVIDENCE]** (supported by a
cited report or source), **[DECISION NEEDED]** (open choice with no default yet), **[DATA NEEDED]**
(requires information not available locally).

## 0. Inputs reviewed and limitations

| Input | Location | Reviewed? |
|---|---|---|
| Scientific question, principles, cohort roles | `README.md` ("Core question"); `config/datasets.yaml` (`project`, `datasets[].role`); the BIO-MB-001 project brief | Yes |
| Phase 2A expression-input adjudication | `reports/phase2a/GSE63060/v1/ADJUDICATION_REPORT.md` | Yes |
| Phase 2B population eligibility (v2) | `reports/phase2b/GSE63060/v2/POPULATION_ELIGIBILITY_REPORT.md` | Yes |
| Phase 2C cohort history (v2) | `reports/phase2c/GSE63060/v2/SAMPLE_IDENTITY_AND_COHORT_HISTORY_REPORT.md` | Yes |
| Phase 2D supplements | `reports/phase2d/GSE63060/v1/SUPPLEMENTARY_SAMPLE_IDENTITY_REPORT.md` | Yes |
| Phase 3A decision framework | `reports/phase3a/GSE63060/v1/POPULATION_ELIGIBILITY_DECISION_FRAMEWORK.md` (cited as [3A]) | Yes |
| Phase 1 audit reports and phenotype tables | `reports/dataset_audit/<GSE>/`; `data/processed/<GSE>/phenotype_table.tsv` | Yes (metadata only) |
| **Hypotheses document, Analysis Plan, Statistical & Validation Plan** | Not present anywhere in the project (file-name and text search, 2026-10-09) | **No — not available locally** |
| **Notion pages** | No Notion connector is available in this session | **No — not reviewed.** Any plan content that exists only in Notion has not been reconciled with this draft |

Consequence: this draft is built from the project brief, the README, the configuration and the
Phase 2A–3A reports only. Before approval it must be reconciled with any existing Notion plan
(decision D0, section 11).

## 1. Objectives and hypotheses (restated from the project brief; no separate hypotheses document exists)

- **Q (core question):** to what extent do AD-associated peripheral-blood transcriptomic features
  replicate across cohorts, and how much of the reproducible signal is specific to AD rather than
  shared with other neurodegenerative diseases?
- **H1 (discovery, GSE63060) [PROPOSED wording]:** some genes are differentially expressed between
  GEO-deposited AD-labelled samples and deposited healthy controls, after prespecified adjustment.
- **H2 (replication) [PROPOSED wording]:**
  - GSE140829: locked discovery genes show concordant direction and association in an external cohort,
    subject to an independence check.
  - GSE63061: consistency within the related AddNeuroMed batch.
- **H3 (specificity) [PROPOSED wording]:** the extent to which replicated genes are also associated
  with idiopathic PD or other neurological diagnoses in GSE99039.

Principles carried from the brief:

- Reproducibility over predictive performance.
- Association, not causation.
- No claim that blood signals originate in the brain.
- No claim of a clinically validated biomarker.
- Prevent leakage.
- Keep confirmatory and exploratory work separate.

## 2. Primary estimand [PROPOSED — requires approval]

**E2, deposited-label estimand.** The population-level difference in log-scale blood expression, per
probe or gene, between GSE63060 samples deposited with GEO status "AD" and samples deposited as healthy
controls ("CTL"). The difference is conditional on prespecified covariates (section 4.6), among samples
meeting the eligibility rules in section 3.

**What the AD group is, as far as the evidence allows [EVIDENCE]:**

- Group-level evidence indicates the deposited AD group combines people with AD at blood collection
  and about 41 people with MCI at collection who were diagnosed with AD within two years. GEO "AD" 145
  equals Lunnon 2013's AD 104 + MCIc 41 exactly ([2C] §3.2, §4.1).
- The converters cannot be identified sample by sample ([3A] F6; [2D] §3).

**Interpretation boundaries (binding on all reporting):**

- Results are associations with a deposited diagnostic label. They are **not** estimates for "AD
  diagnosed at blood collection" (E1), which current data cannot support ([3A] §2).
- No claims about prodromal detection, prediction of conversion, causality, brain origin or clinical
  validity.
- The biological interpretation ("AD-associated, possibly including prodromal stages") must always be
  stated together with the E2 definition and the converter caveat.

**Alternatives** (see [3A] §2):

- E1 becomes possible only if data owners provide diagnosis at blood draw [DATA NEEDED].
- E3 is a descriptive reading of E2, not a separately estimable target.

## 3. Population rules (inputs: [3A] §3 Option C, rules C1–C12)

None of these rules has been applied. Counts in the table describe the metadata, not a frozen
population.

| ID | Exact definition | Field / file | Evidence | Directly implementable? | New decision or data? | Blind to expression results? |
|---|---|---|---|---|---|---|
| R1 Input | Analyse the 329 GSM columns of `GSE63060_series_matrix.txt.gz`; never the supplementary normalized file (identical values plus an unlabelled array) | `data/raw/GSE63060/GSE63060_series_matrix.txt.gz` (sha256 in `download_manifest.json`) | [2A] §2, §9: all 12,608,267 values identical to the normalized file | Yes | Approve (D3) | Yes (decided on file integrity) |
| R2 Identity | Include only columns with a unique GSM, a unique participant code (`description`), a unique array barcode (`title`), and non-missing age and sex | Phenotype table columns `geo_accession`, `description`, `title`, `char:age`, `char:gender` | Phase 1 reconciliation: 329/329 unique and complete | Yes | Approve | Yes |
| R3 Case definition | Case: `char:status` == "AD". Control: `char:status` == "CTL" | `char:status` | GEO records; E2 (section 2) | Yes | Approve with the estimand (D1) | Yes |
| R4 MCI | `char:status` == "MCI" excluded **from the primary contrast only**; retained for exploratory analyses | `char:status` | Project scope (AD vs controls) | Yes | Approve | Yes |
| R5 Missing / ambiguous / conflicting labels | Exclude from case–control contrasts any sample whose diagnosis is missing, transitional, borderline, "OTHER" or conflicting. Apply the same rule in every cohort; log each exclusion by GSM | `diagnosis_status` in each phenotype table | **[PROPOSED (no source)]**; Phase 1 classification. GSE63060 has none; GSE63061 has 6 | Yes | Approve (D2) | Yes |
| R6 Converter status | **No converter-based exclusion or relabelling** in the primary analysis. Code letters are not used to define eligibility | — | [3A] C5; code meaning undocumented ([2C] §4.2) | Not implementable | E1 would need data-owner records (D9) | Yes |
| R7 Age | Prespecify one option: **(a) no age restriction, age as covariate [PROPOSED default]**; (b) restrict to ≥65 per the papers' stated criterion; (c) restrict to an age range shared across cohorts | `char:age` (GSE63060), `char:age_at_draw` (GSE140829), `char:age` (GSE63061), `char:age at exam` (GSE99039, 284/558 present) | Papers state <65 excluded, yet 21 GEO samples are <65 ([2C] §2 row 9). GSE140829 ages 61–89 | Yes | Choose (D4); (b) and (c) as sensitivity analyses | Yes |
| R8 Sex consistency | Compute expression-based sex from XIST (ILMN_1764573) and the Y-gene probes; flag a sample when it disagrees with recorded sex under a prespecified rule; exclude flagged samples; log by GSM | Series Matrix values for the probes listed in [3A] F10; `char:gender` | Original authors used an XIST check ([2C] §2 rows 7–8); Patel 2020 found 2 further mismatches with another method | Yes (probes present) | Approve method and threshold (D5) **[PROPOSED (no source)]** | **Yes — must be computed and finalised without diagnosis-related results** |
| R9 Array outliers | Prespecified, diagnosis-blind outlier rule: an array is flagged if its median correlation with all other arrays (all retained probes) is more than k robust SD below the cohort median, with k fixed in advance (proposed k = 3). Flagged arrays excluded from the primary analysis and included in a sensitivity analysis | Series Matrix | **[PROPOSED (no source)]**; Patel 2020 removed 10 unidentified outliers; GSE140829 submitters used connectivity Z < −2 | Yes | Approve rule and k (D5) | **Yes** |
| R10 Inherited QC | Record the submitters' pre-deposit QC (detection <80%, RIN, XIST, comorbidity) as inherited and unauditable; no attempt to re-apply | — | [2C] §2 row 7; no detection p-values or RIN deposited ([3A] F9) | Not implementable | No | — |
| R11 Unlabelled / undeposited arrays | `4856076038_D` and the 3 empty-header non-normalized columns are not eligible (not in the Series Matrix, or no deposited label) | — | [2A] §4–5 | Yes (automatic under R1) | No | Yes |
| R12 Sood-flag subset | `included in case -control study` is **not** an eligibility criterion | `char:included in case -control study` | Selected for another study ([2B] §4, §6) | Yes | Approve exclusion of B as primary (D1); optional secondary analysis | Yes |
| R13 Freeze before analysis | The eligibility list, sex-check and outlier results are written to a versioned exclusion log (GSM, rule, value), checksummed and approved **before** any case–control model is fitted. No change afterwards except by documented amendment | New file under `reports/` | Project principles | Yes | Approval step (gate G2/G6) | **Yes** |

## 4. Primary differential-expression analysis (GSE63060) [PROPOSED; provisional]

### 4.1 Expression input

- **Data:** Series Matrix values as deposited ([2A] §9). They are already normalized: log-like scale
  7.20–15.05; lumi variance-stabilizing transform plus quantile-type normalization
  ([2A] §6; [2B] §5; Lunnon 2012 p.688).
- **No further normalization of the primary data.** The evidence does not show a need for it, and
  re-normalizing would apply a second normalization ([2A] §6).
- The normalization was probably done together with arrays later removed by QC ([2C] §4.4). It is
  accepted as a limitation; a re-normalization sensitivity analysis is in section 9.

### 4.2 Annotation [DECISION NEEDED: D6]

- The current annotation is the platform's 2008 BGX manifest (RefSeq Build 36.2) ([2A] §7): 78.4% of
  probes have a symbol; 4,684 placeholder symbols; 10 symbols map to more than one Entrez ID.
- **Proposal:** a pinned, versioned modern annotation, either the Bioconductor `illuminaHumanv3.db` at a
  fixed Bioconductor release, or re-mapping of the BGX probe sequences against a fixed genome and
  transcript release. Record the version, retrieval date and checksum.
- Probes without a current Entrez ID are kept for probe-level testing but excluded from gene-level and
  pathway analyses.

### 4.3 Analysis unit and multi-probe policy [DECISION NEEDED: D6]

- **Primary inference at probe level [PROPOSED]**, which avoids mapping-dependent aggregation.
- A **gene-level result** is needed for cross-platform replication. For each Entrez gene, use the probe
  with the highest mean expression across *all eligible samples* (diagnosis-blind), fixed before
  testing.
- Alternatives for sensitivity (section 9): the probe with the largest variance (diagnosis-blind);
  averaging probes.
- **Never** choose a probe by its association with diagnosis.

### 4.4 Sample QC

R8–R9 (section 3), applied before modelling and logged.

### 4.5 Feature QC [PROPOSED]

- The deposited probe set has already been filtered by the submitters to 38,323 probes; the rule is
  undocumented ([2A] §6; [2C] §2 row 10).
- Additional filter: retain probes whose mean expression across all eligible samples exceeds a fixed
  quantile of the distribution (proposed: the 25th percentile), computed diagnosis-blind.
- The filtering threshold is checked in sensitivity analyses. No variance filtering using the group
  labels.

### 4.6 Design and contrast [PROPOSED]

- **Model:** `expression ~ group + age + sex + chip`, where `group` ∈ {CTL (reference), AD} (R3) and
  age is linear in years.
- **Chip** is the array barcode prefix: 29 chips.
- **Site** (participant-code prefix) is *not* in the primary model, because the site mapping is
  supported but not proven ([2C] §4.3). It is a sensitivity covariate.
- **Rationale:**
  - Age and sex differ between groups (AD mean 75.4 vs 72.4 years; female 68% vs 60%; [2B] §3), and
    both are recorded for all samples.
  - Chip is a technical factor available for all samples.
- **Prerequisite check [PROPOSED]:** before the model is approved, tabulate diagnosis by chip
  (metadata only). If chip is confounded with diagnosis, replace the chip fixed effect with a
  random-effect or duplicate-correlation approach, or drop it with justification (D7).
- **Not available, so not used:** APOE, MMSE, RIN, blood-cell counts.
- **Cell composition:** the original authors reported differences in basophil and monocyte counts
  (Lunnon 2012 p.697). Estimated cell proportions (deconvolution) are a sensitivity covariate only;
  they are model-dependent and may sit on the causal pathway.
- **Contrast:** AD − CTL. Effect = log2-scale difference on the deposited (VST) scale. The VST scale is
  approximately log2; report this caveat.

### 4.7 Estimation [PROPOSED; environment decision D8]

- Probe-wise linear models with empirical-Bayes moderated variances (`limma`, trend = TRUE).
- **Environment:** R/Bioconductor is **not installed**, and the project venv lacks SciPy/statsmodels
  (checked 2026-10-09). Installing a pinned R/Bioconductor environment, or approving a Python
  alternative, is a decision (D8). Nothing has been installed.

### 4.8 Multiple testing and reporting

- **Multiple testing:** Benjamini–Hochberg FDR across all tested probes. Primary significance threshold
  FDR < 0.05 [PROPOSED].
- **Report for every probe:** log2 effect with 95% CI, moderated t, p, FDR, mean expression, gene
  annotation and version.
- **Report for every model:** sample counts per group after each eligibility step (generated, not
  pre-assumed).
- No result is suppressed for being non-significant.

### 4.9 Missing data and assumptions

- **Missing data:** the Series Matrix has no missing values ([2A] §1). Age and sex are complete. Any
  missing covariate in other cohorts is handled by complete-case analysis, reporting the excluded
  counts, plus a sensitivity analysis where missingness exceeds 10% (relevant to GSE99039 age).
- **Assumption checks** (prespecified and reported, not used to select results):
  - mean–variance trend plot;
  - residual distribution summaries;
  - array weights (`arrayWeights`) as a sensitivity analysis.

## 5. Replication and consistency without leakage [PROPOSED]

### 5.1 Roles (from `config/datasets.yaml`; not changed here)

- **GSE140829 — external replication candidate.**
  - Its GEO record names no consortium; its relationship to AddNeuroMed is undocumented.
  - Participant independence from AddNeuroMed is **UNRESOLVED** ([3A] F13).
  - Before replication is called "external", document independence: data-owner confirmation or study
    documentation (D10).
- **GSE63061 — consistency, not independent validation.**
  - Same AddNeuroMed SuperSeries, different platform (HT-12 v4) and lab (UK).
  - Participant overlap with GSE63060 cannot be excluded: no shared codes or barcodes found, which does
    not prove independence.
  - Its 6 ambiguous or transition labels follow R5.

### 5.2 Locking before validation

- After the primary analysis is approved, the **discovery signature** is written to a versioned,
  checksummed file. It contains gene ID, annotation version, probe used, direction, effect size, CI and
  FDR.
- It includes the prespecified **signature definition**: all genes at FDR < 0.05, capped at a
  prespecified maximum (proposed: the top 200 by FDR, then by |effect|) for the score in 5.3.
- **No validation-cohort expression values may be modelled against diagnosis before the lock.**
  - Phase 1 inspected file structure and value distributions only, without any group comparison; this
    is recorded as compliant.
  - Validation cohorts are never used to select genes, set thresholds or tune models.

### 5.3 Replication analysis in each validation cohort (run separately per cohort; no pooling)

- **Population:**
  - GSE140829: `char:diagnosis` AD vs Control; GSE63061: AD vs CTL.
  - Apply R2, R5, R7 (as approved), R8 and R9 with the same prespecified rules, using each cohort's
    platform-appropriate sex probes.
  - MCI excluded from the replication contrast.
- **Input:**
  - GSE140829: the Series Matrix (VST + RSN, nuID probes, 587 samples, not batch-corrected), with
    `char:batch` (19 levels) as a covariate [PROPOSED]. The submitters' final file (ComBat-corrected,
    gene-collapsed, 551 samples after their own outlier and batch exclusions) is a sensitivity input
    (D11).
  - GSE63061: the Series Matrix.
- **Mapping:** genes matched by Entrez ID using each platform's pinned annotation (nuID → Entrez for
  GPL15988). Unmatched discovery genes are reported as "not measurable", not as failures.
- **Model:** the same model form as discovery (group + age + sex + batch/chip), fitted only for the
  locked genes.
- **Replication criteria [PROPOSED; D12]:**
  1. **Per gene:** same direction **and** one-sided p < 0.05 after BH correction across the locked
     genes measurable in that cohort.
  2. **Signature level:** a sign test of direction concordance across all locked, measurable genes.
  3. **Score:** a prespecified score (mean of z-standardized up-genes minus mean of down-genes, weights
     fixed at discovery) compared AD vs controls (effect size with CI).
- Discovery and replication effect sizes are reported side by side.
- Non-replication on another platform is reported as non-replication. It is not assumed to be either
  biology or artefact.

## 6. Disease-specificity analysis (GSE99039) [PROPOSED]

- **Data:**
  - Series Matrix (RMA, log2, quantile; GPL570). The CEL archive (~2.5 GB) was not downloaded.
  - Covariates: `char:Sex` (505/558 present); `char:age at exam` (284/558 present, a major
    limitation); `char:batch` (37 levels).
  - `char:learning set` (the original authors' split) is not used for selection.
- **Groups:**
  - Primary contrast: idiopathic PD (IPD) vs CONTROL.
  - Separate contrasts: OTHER_NEURO (each diagnosis tabulated, pooled only under an approved rule)
    vs CONTROL.
  - **Genetic PD (GPD) and GENETIC_UNAFFECTED are kept separate** from IPD and controls, and are not
    pooled without an approved justification (D13).
  - HD_HD_BATCH is ambiguous (R5).
- **Analysis:** for the locked replicated AD genes only, estimate PD-vs-control effects with the same
  model form. The complete-case age handling is reported, with a sensitivity analysis without age.
- **Interpretation rules:**
  1. "Specific to AD" requires an AD-cohort association **and** evidence of no association, or of a
     different association, in PD. Absence of significance is not evidence of absence: report effect
     sizes with CIs, plus equivalence bounds prespecified as part of D13.
  2. No single cohort contains both AD and PD, so a formal disease × gene interaction cannot be
     estimated within one cohort. Cross-cohort comparisons of standardized effects are confounded by
     platform, lab and population and are labelled **descriptive**.
  3. Non-replication across platforms is not evidence of biological specificity.
- **Optional extension** [DATA NEEDED]: the GSE140829 series summary describes a cohort including
  FTD-spectrum disorders, and the record lists it as a SubSeries of GSE140831
  (`data/metadata/GSE140829/GSE140829_series_brief.soft.txt`). That would allow within-cohort disease contrasts on one
  platform. It has not been retrieved or assessed.

## 7. Pathway analysis [PROPOSED]

- **Purpose:** descriptive interpretation of discovery and replicated results. Not confirmatory.
- **Databases:** GO Biological Process and Reactome, at pinned versions (for example a fixed MSigDB
  release). Record version, date and checksum; no live web queries during analysis.
- **Methods:**
  - **Primary:** rank-based competitive testing (for example `camera`, which accounts for inter-gene
    correlation) on the full gene-level statistics.
  - **Secondary:** over-representation of FDR < 0.05 genes, with a **universe = all Entrez genes
    measurable after feature QC on that platform**.
- **Multiple testing and set size:** BH FDR within each database; minimum and maximum set sizes
  prespecified (proposed 15–500).
- **Interpretation limits:**
  - Blood pathways reflect cell composition and activation.
  - No inference of brain mechanisms.
  - Redundancy among GO terms is acknowledged.

## 8. Exploratory analyses (not confirmatory unless separately approved)

- MCI vs controls, and MCI vs AD, in GSE63060 and GSE63061.
- Code-letter-based sensitivity analysis (section 9), labelled as resting on an undocumented
  convention.
- GSE165082 (PD RNA-seq, 26 samples vs 30 described): exploratory only. Not pooled with microarrays.
- GSE165081 (methylation): future extension only. Not transcriptomic validation.
- Machine learning and classifiers: exploratory, and only with strict nested cross-validation inside
  the discovery cohort. Never tuned on validation cohorts.
- A "reproduce Sood et al." analysis on the flagged subset (49/67): optional, clearly labelled.

## 9. Prespecified sensitivity analyses

All sensitivity analyses below are run and reported whatever their results. None replaces the primary
analysis because its result looks "better".

| # | Assumption varied | Variant |
|---|---|---|
| S1 | Age eligibility (R7) | Restrict to ≥65; and to the age range shared with GSE140829 (≥61) |
| S2 | Age handling | Age with a natural spline (3 df) instead of linear |
| S3 | Covariates | Add site (participant-code prefix); remove chip |
| S4 | Converter heterogeneity | Exclude the 37 AD samples with "M" participant codes. **Labelled as resting on an undocumented convention; it cannot remove the ~4 London converters** |
| S5 | Sample QC | Include R8/R9-flagged arrays; outlier threshold k = 2.5 and 4 |
| S6 | Array quality weighting | `arrayWeights` |
| S7 | Feature filter | No additional filter; 50th-percentile filter |
| S8 | Multi-probe policy | Largest-variance probe; mean of probes |
| S9 | Annotation | Original 2008 BGX annotation vs the pinned modern annotation |
| S10 | Normalization | Re-normalize the non-normalized file for the 329 GEO samples (VST + quantile), using the content-based mapping of the 3 empty-header columns ([2A] §5) and labelling it as inferred |
| S11 | Cell composition | Add estimated blood-cell proportions |
| S12 | Population | Flagged subset (49/67); report only, not as a replacement primary |
| S13 | GSE140829 input | Submitter final (ComBat, 551) vs Series Matrix + batch |

## 10. Reproducibility requirements

- **Pinned environment:** R/Bioconductor or Python versions recorded; lock file.
- **Code:** analysis code in `src/` or `scripts/` with tests.
- **Seeds:** fixed random seeds where relevant.
- **Inputs:** every input referenced by its checksum from the manifests.
- **Outputs:** versioned report folders (never overwritten).
- **Logs:** exclusion logs and the discovery-signature lock file are checksummed and committed before
  validation analyses run.

## 11. Decision register and approval gate

All items require the PI's approval unless marked otherwise. **Bold** rows are the items explicitly
flagged for review.

| ID | Decision | Proposed default | Supporting evidence | Consequence of each choice | Approval required? |
|---|---|---|---|---|---|
| D0 | Reconcile with any existing Notion Analysis Plan / Statistical & Validation Plan | Provide the Notion content (export or local copy) before approval | Notion not accessible in this session (section 0) | If a Notion plan differs, the draft must be amended | Yes |
| **D1** | **Primary estimand** | E2 (deposited label), with mandatory converter caveat | [3A] §2; [2C] §3–4 | E2: supportable now, limited interpretation. E1: needs data-owner diagnosis at draw. Flagged subset as primary: rejected by default ([2B] §6) | **Yes** |
| **D2** | **Sample eligibility rules R2–R5, R12** | As in section 3 | [3A] Option C | Determines the analysable population; no counts are frozen until applied | **Yes** |
| D3 | **Expression input** | GSE63060 Series Matrix; no re-normalization | [2A] §2, §9 | Alternative inputs add repairs or an unlabelled array ([2A] §9) | **Yes** |
| D4 | Age eligibility (R7) | No restriction; age covariate; S1 as sensitivity | [2C] §2 row 9 | Restricting to ≥65 follows the papers' text, loses 21 samples and leaves the discrepancy unexplained | Yes |
| D5 | Sample QC rules (R8, R9) | XIST/Y-gene sex check; correlation outlier rule, k = 3 | [2C] §2 rows 7–8; Patel 2020 precedent | Thresholds change who is excluded; must be fixed blind | Yes |
| **D6** | **Annotation and multi-probe policy** | Pinned modern annotation; probe-level primary; highest-mean probe per gene for gene level | [2A] §7 | Affects gene-level replication and pathway results | **Yes** |
| **D7** | **Statistical model** | limma: group + age + sex + chip; site as sensitivity; chip-confounding check first | [2B] §3 (age/sex imbalance); [P1] chip field | Covariate choice changes estimates; over-adjustment if chip is confounded | **Yes** |
| D8 | Analysis environment | Install a pinned R/Bioconductor (limma) environment, or approve a Python alternative | R not installed; no SciPy in venv | Installing changes the environment; needs your approval | Yes |
| D9 | Request data-owner information (diagnosis at draw, under-65 explanation, overlap with GSE63061) | Request it; proceed with E2 meanwhile | [3A] §3 Option D | If obtained, E1 becomes feasible and S4 can be replaced by an exact analysis | Yes |
| D10 | Independence standard for "external" replication | GSE140829 labelled "external candidate, independence unverified" until documented | [3A] F13 | Over-claiming replication if overlap exists | Yes |
| D11 | GSE140829 input | Series Matrix + batch covariate; final ComBat file as sensitivity | GSE140829 GEO processing statement | ComBat with diagnosis-imbalanced batches can distort effects | Yes |
| **D12** | **Replication criteria** | Per-gene direction + BH one-sided p < 0.05; sign test; prespecified score | Section 5.3 | Defines what "replicated" means; must be fixed before unblinding | **Yes** |
| **D13** | **Disease-specificity strategy** | IPD vs CONTROL primary; genetic PD separate; descriptive cross-cohort comparison; equivalence bounds to be set | Section 6; GSE99039 metadata | Without bounds, "specific" cannot be claimed; cross-platform limits | **Yes** |
| D14 | Pathway framework | camera + ORA; GO BP and Reactome, pinned versions | Section 7 | Database and version change results | Yes |
| D15 | Significance and signature size | FDR < 0.05; signature capped at 200 genes | Section 4.8, 5.2 | The cap trades off power against interpretability | Yes |
| D16 | Sensitivity analysis set | S1–S13 | Section 9 | Adding or removing analyses after results would be selective reporting | Yes |

**Approval gate (from [3A] §5; status unchanged by this draft):**

- G1 estimand, G2 rules, G5 QC, G7 discovery/validation relationship and G8 statistical plan remain
  **not satisfied** until D1, D2, D5, D10–D12 are approved and this draft is promoted to an approved
  version.
- G3, G4, G6 and G9 remain **partially satisfied**.

Writing this draft does not satisfy any gate condition.
