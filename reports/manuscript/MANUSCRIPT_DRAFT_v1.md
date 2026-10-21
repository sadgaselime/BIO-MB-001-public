# A blood transcriptomic signature of Alzheimer's disease: prespecified discovery, cross-cohort replication, disease specificity and classifier transportability

**DRAFT v1 (2026-10-20). Not for circulation.** Every number is taken from an accepted, code-identity-verified output
of BIO-MB-001; the source of each is listed in the Provenance appendix. `[CITE]` marks a reference still to be added. The
statistical analysis plan (SAP v7) is a proposed draft that is not frozen; the individual decisions it governs were approved
before each analysis, as recorded in its decision register.

---

## Abstract

**Background.** Blood transcriptomic signatures of Alzheimer's disease (AD) have been reported repeatedly. Their
reproducibility across cohorts, their specificity relative to other neurodegenerative diseases, and their usefulness for
classifying individuals remain uncertain [CITE].

**Methods.** We analysed four public whole-blood microarray datasets under a prespecified, decision-logged plan:
- **Discovery:** GSE63060 (AddNeuroMed).
- **Related-cohort consistency:** GSE63061 (AddNeuroMed; possible participant overlap).
- **Replication:** GSE140829 (independence from AddNeuroMed participants unverified).
- **Specificity:** GSE99039 (Parkinson's disease).

Before any modelling, samples were selected by rule-based eligibility and quality control: a two-axis sex-concordance check
and a robust outlier check, with every exclusion list approved as rule-applied. Differential expression used limma with
age, sex and chip/batch adjustment. A 200-gene signature was locked in the discovery cohort before any other cohort's
expression was modelled. We then tested:
- a composite score test of that signature, a per-gene test and direction agreement in each cohort;
- a two-sided specificity test against Parkinson's disease, Holm-corrected across three contrasts;
- a leakage-controlled ridge classifier, trained with nested, chip-grouped cross-validation in the discovery cohort and
  applied once, frozen, to the other cohorts.

**Results.**
- **Discovery:** in GSE63060 (145 AD, 60 controls), 1,401 of 17,425 genes were associated with AD at FDR < 0.05
  (739 lower, 662 higher in AD). The result was robust across 14 prespecified sensitivity analyses (Spearman ρ of t
  statistics 0.74–0.999).
- **Signature:** the locked 200-gene signature was dominated by lower expression in AD of oxidative-phosphorylation and
  ribosomal genes.
- **Related cohort:** in GSE63061 (139 AD, 133 controls) the composite score shifted strongly toward AD (one-sided
  p = 3.0 × 10⁻¹⁴; 194 of 200 genes consistent). This agreement may be inflated by participant overlap.
- **Replication:** in GSE140829 (201 AD, 248 controls) the signature replicated directionally but weakly (one-sided
  p = 0.0019; 43 of 200 genes replicated; 183 of 200 directionally concordant).
- **Specificity:** in GSE99039, the score was shifted in the AD direction in idiopathic Parkinson's disease (two-sided
  p = 0.018), but not significantly after the prespecified Holm correction (p = 0.053). Specificity could therefore be
  neither demonstrated nor excluded.
- **Classifier:**
  - in nested cross-validation it reached AUROC 0.841 (repeat range 0.824–0.852), above an age-only model (0.622) and an
    equal-weight gene score (0.780); a within-chip permutation null gave p = 0.005;
  - applied once, frozen, it reached AUROC 0.769 in GSE63061 but 0.525 (95% CI 0.471–0.579) in GSE140829, which is no
    better than chance.

**Conclusions.** A blood transcriptomic AD signal reproduces as a modest group-level shift across cohorts. It may be
partly shared with Parkinson's disease, and in its present form it does not support individual-level classification in
an external cohort. Reproducibility within one consortium substantially overstated external performance.

---

## 1. Introduction

[To be written, about 4 paragraphs.]
- Need for blood-based AD biomarkers [CITE].
- Prior blood transcriptomic AD signatures, including work on AddNeuroMed [CITE].
- Recurring problems: reuse of related cohorts as "validation", label noise (MCI-to-AD converters among deposited AD),
  batch confounding, and data leakage in classifiers [CITE].
- Aims: (A) discovery; (B) replication; (C) specificity versus Parkinson's disease; (D) classifier transportability. All
  four were assessed under a plan fixed before results.

## 2. Methods

### 2.1 Governance and reproducibility
- **Plan and decisions:** the analysis followed a written SAP with a decision register. Each decision was approved before
  the analysis it governed, and changes after results were limited to labelled amendments.
- **Code identity:** every output was produced under a code-identity lifecycle that hashes the code, the R and Python
  environments and the inputs, and verifies the executed code against those hashes. Two independent computations had to be
  byte-identical before an output was accepted.
- **Software:** R 4.6.1, Bioconductor 3.23, limma 3.68.5 and glmnet 5.1, with a pinned Python environment.

### 2.2 Datasets and roles

| Dataset | Platform | Role | Primary population (after approved exclusions) |
|---|---|---|---|
| GSE63060 | Illumina HT-12 v3 (GPL6947) | Discovery | 145 AD, 60 CTL |
| GSE63061 | Illumina HT-12 v4 (GPL10558) | Related-cohort consistency; possible overlap | 139 AD, 133 CTL |
| GSE140829 | Illumina HT-12 v4, nuID-keyed (GPL15988) | Replication; independence unverified | 201 AD, 248 CTL |
| GSE99039 | Affymetrix HG-U133 Plus 2 (GPL570) | Parkinson's specificity | IPD 197, GPD 40, GU 22, CONTROL 229 (before complete-case on sex) |

### 2.3 Eligibility and quality control
- **Eligibility:** rule-based. Deposited diagnostic labels were used without relabelling, and MCI and other labels were
  kept outside the primary contrasts.
- **Duplicate review:** metadata and expression-similarity duplicate review, with a designated reviewer.
- **Sex check (R8):** two-axis sex concordance, using XIST and nine Y-chromosome genes (eight on GPL570), without a
  validated threshold.
- **Outlier check (R9):** robust outlier and near-identity flags.
- **Exclusions:** the PI reviewed and approved each cohort's complete rule-applied exclusion list before any expression model.
- **Finding:** in GSE63060, 44 of 104 deposited controls, and no AD arrays, were discordant on both sex axes. The
  expression-derived and recorded sex totals among controls were equal, consistent with a permutation of sex labels or
  sample identities. The comparable rates were 1 of 388 arrays in GSE63061, 2 of 587 in GSE140829 and 15 of 558 in
  GSE99039. A query to the data owners is pending.

### 2.4 Probe-to-gene mapping
- **Illumina:** Entrez-only mapping with a single pinned annotation snapshot; multi-mapped probes were excluded.
- **GSE140829:** its nuIDs were translated to ILMN probe identifiers through the pinned annotation. The translation was
  verified against a second package and against first-principles sequence decoding, with 47,008 of 47,008 features
  agreeing.
- **GPL570:** a separate, approved mapping.
- **Gene level:** each gene's value was the mean of its eligible probes.

### 2.5 Discovery and signature lock
- **Model:** limma (lmFit with eBayes, trend = TRUE) with AD status, age (linear), recorded sex and chip as a fixed effect,
  fitted in a full-rank basis.
- **Multiple testing:** Benjamini–Hochberg at q < 0.05.
- **Identifiability:** checked before the fit: 25 chips contained both groups; E = 0.82; VIF 1.22.
- **Signature:** the top 200 genes by q (ties broken by |β|, then |t|) were locked, with their directions, before any
  other cohort's expression was modelled.
- **Sensitivity analyses:** 14 prespecified analyses were run.

### 2.6 Validation tests (per cohort, no cross-cohort pooling)
- **Composite score test (C-c):** an equal-weight score (mean z of up-genes minus mean z of down-genes), with z computed
  without reference to diagnosis. A one-sided test of a shift toward AD, adjusted for the cohort's covariates, decided by
  the one-sided 95% lower bound.
- **Per-gene test (C-a):** a one-sided moderated t test in the locked direction, with BH correction across measurable
  locked genes.
- **Direction agreement (C-b):** descriptive only.
- **GSE63061:** additionally, a descriptive Pearson correlation of effects, with a nominal Fisher-z interval.
- **Coverage:** at least 50% and at least min(5, n) of the locked genes in each direction had to be measurable.

### 2.7 Specificity (GSE99039)
- **Q1:** a two-sided test of the score shift in each disease group versus controls, adjusted for sex and batch, with
  Holm correction across IPD (primary), GPD and GU (descriptive).
- **Per gene:** two-sided tests with BH correction within each contrast.
- **Age-adjusted sensitivity (S15):** labelled as sensitivity.
- **No equivalence margin:** none was specified, so no "absence of association" or "AD-specific" claim is possible by design.

### 2.8 Classifier
- **Protocol:** written and approved before any machine-learning code touched real data.
- **Features:** gene-level expression, excluding the R8 sex-check genes. Recorded sex and chip were never used as predictors.
- **Pre-processing and selection:** expression was centred within each chip without reference to diagnosis. Inside each
  training fold: scaling, limma top-k selection (k ∈ {50, 100, 200}) and a ridge penalty, chosen by inner cross-validation.
- **Cross-validation:** 20 repeats of 5-fold cross-validation with whole chips kept together in each fold, inner folds
  likewise grouped by chip, and class-weighted fitting.
- **Baselines:** prevalence, age only and an equal-weight score.
- **Metrics and null:** AUROC, AUPRC, Brier score, calibration, and sensitivity, specificity and PPV at a threshold fixed
  in the inner loop; a 200-permutation within-chip label null.
- **Synthetic leakage tests (passed before any real-data run):** random labels gave chance AUROC; a strong batch–label
  confound (AUROC 0.87 on its own) was not exploited; changing test-fold expression left every training choice unchanged.
- **External application:** the final model was refitted on all 205 discovery arrays, frozen and hashed, then applied once
  to each external cohort with within-cohort standardization.

## 3. Results

### 3.1 Discovery
- **Associations:** 1,401 of 17,425 genes at q < 0.05: 739 lower and 662 higher in AD. At probe level, 1,744 of 38,323.
- **Sensitivity analyses:** all 14 preserved the sign of all, or nearly all, of the 1,401 genes. Spearman correlations of
  t statistics with the primary analysis ranged from 0.897 to 0.999 in 13 of them; the smallest-sample analysis
  (S12: 49 AD, 37 controls) gave 0.737.
- **The locked signature:** 172 genes lower and 28 higher in AD. The top-ranked genes were NDUFA1, MRPL51, CETN2, NDUFS5,
  RPL36AL, ATP6V1E1, SEM1, COX17, UFC1 and TBCA, all lower in AD.

### 3.1b Cell-composition sensitivity (S11; method chosen after primary results)
- **Model:** the five MCP-counter leukocyte marker indices added to the discovery model (E = 0.76; VIF 1.31).
- **Locked genes:** all 199 evaluable locked genes kept their direction and q < 0.05; median effect size was 0.84 of
  the primary.
- **All genes:** 783 of the 1,401 primary associations remained significant, and all kept their sign; ρ of t = 0.92.
- **Indices by group:** AD arrays had slightly higher neutrophil, monocytic and NK indices and lower T-cell indices
  (descriptive).
- **Interpretation:** the signature is not explained by these indices, but part of the wider discovery signal is
  composition-related.

### 3.2 Related-cohort consistency (GSE63061)
- **Coverage:** all 200 genes were measurable.
- **Composite score:** θ̂ = 1.24 score units, one-sided p = 3.0 × 10⁻¹⁴, lower bound 0.985.
- **Per-gene and direction:** 194 of 200 genes were consistent at q < 0.05; 198 of 200 agreed in direction.
- **Effect correlation:** Pearson r = 0.92 (nominal Fisher-z interval 0.90–0.94).

### 3.3 Replication (GSE140829)
- **Coverage:** all 200 genes were measurable.
- **Composite score:** θ̂ = 0.25, one-sided p = 0.0019, lower bound 0.108.
- **Per-gene and direction:** 43 of 200 genes were replicated at q < 0.05 (36 of 172 down, 7 of 28 up); 183 of 200 agreed
  in direction.
- **Strongest replicated genes:** RPS12, RPL32, ITGAM (up), GTF2H5, RPS25, RPL22 and RPS27A.

### 3.4 Specificity (GSE99039)
- **Coverage:** 190 of 200 genes were measurable on GPL570.
- **IPD versus controls (183 versus 208 after the sex requirement):** θ̂ = +0.20 (95% CI 0.04–0.37); two-sided p = 0.018;
  Holm-adjusted p = 0.053. Two genes were significant, both in the AD direction: TCIRG1 and NBEAL2.
- **GPD versus controls:** θ̂ = +0.10, p = 0.47.
- **GU versus controls:** θ̂ = +0.19, p = 0.37.
- **Age-adjusted:** IPD θ̂ = +0.17, p = 0.13.
- **Overall:** under the prespecified rule, no association with Parkinson's disease was demonstrated. Every estimate lay
  in the AD direction.

### 3.4b Composition-adjusted replication and specificity (S11-ext; post hoc)
- **GSE140829, with the five marker indices added:** the composite shift fell from 0.25 to 0.12 (one-sided p = 0.041;
  lower bound 0.007). Gene-level replication fell from 43 to 1 of 200, and direction agreement from 0.92 to 0.78.
- **GSE99039, idiopathic PD:** the shift fell from +0.20 to +0.08 (p = 0.27; Holm p = 0.51). GPD and GU remained
  non-significant.
- **Interpretation:** most of the externally reproducible signal, and the borderline Parkinson's shift, track leukocyte
  composition indices. In the discovery cohort, by contrast, the signature survived adjustment (3.1b).

### 3.5 Classifier
- **Within GSE63060 (nested CV):**

  | Model | AUROC (range over repeats) | Sensitivity / specificity |
  |---|---|---|
  | Ridge | 0.841 (0.824–0.852) | 0.75 / 0.75 |
  | Elastic net | 0.850 | — |
  | Equal-weight score | 0.780 | — |
  | Age only | 0.622 | — |

  Ridge exceeded age only by 0.22 (DeLong p = 5.9 × 10⁻⁶) and the equal-weight score by 0.06 (p = 0.002). The permutation
  null averaged 0.485 (maximum 0.642; p = 0.005).
- **Frozen model, applied once:**

  | Cohort | AUROC (95% CI) | Age-only model |
  |---|---|---|
  | GSE63061 | 0.769 (0.714–0.824) | 0.631 |
  | GSE140829 | 0.525 (0.471–0.579) | 0.472 (difference p = 0.17) |

## 4. Discussion

[To be written.] Points to develop:
1. **Within-consortium agreement overstated external evidence.** GSE63061 gave very strong agreement and AUROC 0.77. In
   GSE140829 the group-level effect was much weaker and individual-level discrimination failed.
2. **The signal is real but modest.** The primary replication test passed, and 92% of genes agreed in direction.
3. **Biology.** Lower expression of oxidative-phosphorylation and ribosomal genes, alongside myeloid-associated genes
   (ITGAM, TCIRG1, NBEAL2), is compatible with shifts in leukocyte composition. In S11 the locked signature survived
   marker-based adjustment, but 44% of the wider discovery signal did not. [CITE]
4. **Specificity.** A borderline same-direction shift in Parkinson's disease argues against claiming AD specificity.
5. **Label quality.** A large set of sex-discordant controls in GSE63060 points to a deposited-annotation problem in a
   widely reused dataset.
6. **What the governed design prevented.** It precluded outcome-dependent choices; for example, the classifier was not
   re-tuned after the GSE140829 failure.

## 5. Limitations

- Labels are as deposited. "AD" may include MCI at the time of the blood draw, and diagnostic criteria differ across cohorts.
- The independence of GSE140829 from AddNeuroMed participants is unverified, and GSE63061 may overlap with GSE63060.
- Platforms and processing differ (Illumina v3 and v4, nuID-keyed data, Affymetrix), and score magnitudes cannot be
  compared across cohorts.
- No equivalence margin was set, so specificity cannot be established.
- Cell composition was assessed only with marker-based indices, in the discovery cohort only (S11), with the method chosen after the primary results; residual confounding is possible.
- Classifier probabilities are not calibrated risks (class weighting); there is no clinical validation and no prospective cohort.

## 6. Data and code availability

All datasets are public on GEO. The code, environment locks, identity records, decision register and every accepted output
are in the BIO-MB-001 repository [repository link to be added].

## Provenance appendix (accepted outputs)

| Result | Output directory |
|---|---|
| Discovery fit and sensitivities | reports/discovery/GSE63060/fit_v1, sensitivity_v1 |
| Signature lock | reports/lock/GSE63060/v1 (signature SHA-256 9ca4310c…) |
| GSE63061 consistency | reports/validation/GSE63061/v1 |
| GSE140829 replication | reports/validation/GSE140829/v1 |
| GSE99039 specificity | reports/specificity/GSE99039/v1 |
| Classifier CV and final model | reports/ml/GSE63060/v1 (final model SHA-256 e4f7f18e…) |
| External classifier applications | reports/ml/GSE63061_external/v1, reports/ml/GSE140829_external/v1 |
| QC and exclusion lists | reports/qc_stage_b/<cohort>/v1 |
