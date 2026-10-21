# Model card: BIO-MB-001 frozen blood-transcriptome classifier (ridge, v1)

**Owner:** Sadga Selime (independent researcher), sadgaselime@gmail.com · **Version:** v1, frozen 2026-10-20 ·
**Final model SHA-256:** `e4f7f18e73795610d598abb676608dc2ad6edee291e4a9bfcf35be35cc239e51` ·
**Files:** `reports/ml/GSE63060/v1` (model, settings, cross-validation), `reports/ml/GSE63061_external/v1`,
`reports/ml/GSE140829_external/v1` (single external applications). Interactive view: the "model card" dashboard artifact.

> **Status: exploratory research model. Not a diagnostic test.** It performed at chance (AUROC 0.53) in the only
> replication cohort. It must not be used to make decisions about any person.

## 1. What the model does

| | |
|---|---|
| **Input** | Whole-blood gene expression (Illumina microarray, gene level) for one array |
| **Output** | A score between 0 and 1; at or above the frozen threshold (0.543) the profile is called "AD-like" |
| **Task** | Distinguish deposited Alzheimer's disease (AD) labels from control labels |
| **Algorithm** | Penalised (ridge) logistic regression on 200 genes, λ = 0.236, class-weighted |
| **Pre-processing** | Gene-level expression centred within each chip without using diagnosis; each gene standardised with training means and SDs; nine sex-chromosome genes used for the sex check removed (17,416 genes available) |
| **Gene choice** | Top k genes by limma inside each training fold; k ∈ {50, 100, 200} and λ chosen by inner cross-validation; the final refit chose k = 200 |
| **Not used as predictors** | Recorded sex, chip, site, age |

How a prediction is made, and the 20 most influential genes, are shown in Figure 8 of the manuscript. All 200 genes and
weights are in `reports/ml/GSE63060/v1_readable_model_genes.csv`.

## 2. Training data

GSE63060 (AddNeuroMed batch 1, Illumina HT-12 v3): 205 arrays (145 AD, 60 controls) on 29 chips, after pre-specified
exclusions (MCI and other labels outside the contrast; 44 controls with two-axis sex discordance). Labels are deposited
diagnoses and are not re-adjudicated.

## 3. Performance

**Within the training cohort** (20 repeats of nested, chip-grouped 5-fold cross-validation; ranges are 2.5th–97.5th
percentiles over repeats, which describe the variability of the estimate, not a confidence interval):

| Metric | Ridge | Age-only baseline | Equal-weight baseline |
|---|---|---|---|
| AUROC | 0.841 (0.824–0.852) | 0.622 | 0.780 |
| AUPRC | 0.922 | 0.813 | 0.886 |
| Brier score | 0.154 | 0.241 | — |
| Sensitivity / specificity at threshold | 0.75 / 0.75 | — | — |
| PPV (prevalence 71% AD) | 0.88 | — | — |
| Calibration slope / intercept | 0.93 / 0.74 | — | — |

Permutation null (200 within-chip label shuffles): mean AUROC 0.485, maximum 0.642; p = 0.005.

**Frozen model, applied once to each external cohort, without re-fitting or tuning:**

| Cohort | Relation to training data | AUROC (95% CI, DeLong) | Sensitivity / specificity | Brier | Age-only AUROC |
|---|---|---|---|---|---|
| GSE63061 | Same consortium; possible participant overlap | 0.769 (0.714–0.824) | 0.75 / 0.63 | 0.203 | 0.631 |
| GSE140829 | Separate study; independence unverified; different platform version | **0.525 (0.471–0.579)** | 0.61 / 0.41 | 0.304 | 0.472 |

All 200 model genes were measurable in both external cohorts.

## 4. How to read these numbers

- The good result in GSE63061 is **not** independent validation: the cohorts come from the same consortium and may
  share participants and processing.
- In GSE140829 the model is no better than chance. The manuscript's composition analysis suggests why: much of the
  signal outside the discovery cohort tracks leukocyte (white-cell) composition, which differs between cohorts.
- Probabilities are **not calibrated risks**: class weighting changes the baseline, and calibration in GSE140829 was
  poor (slope 0.13).

## 5. Intended and out-of-scope use

- **Intended:** research on whether blood-transcriptome AD signals transport between cohorts; a documented, frozen
  reference model for comparison by other researchers.
- **Out of scope:** diagnosis, screening, risk prediction, or any decision about an individual; RNA-seq or other
  platforms without re-validation; populations other than the AD-versus-control contrast it was trained on.

## 6. Safeguards against leakage and over-fitting

The ML protocol was written and approved before any ML code read real data. Synthetic tests had to pass first: random
labels gave chance AUROC; a strong batch–label confound (AUROC 0.87 on its own) was not exploited; changing test-fold
expression left every training choice unchanged. Gene selection, scaling and tuning happened only inside training folds,
whole chips were kept together, and each external cohort was scored exactly once.

## 7. Known limitations and ethical notes

- Deposited labels may be wrong or reflect diagnosis at a different time; 44 of 104 GSE63060 controls had sex
  discordance consistent with permuted labels or samples, and same-sex swaps cannot be detected.
- Small training set (60 controls), a single training cohort, and no measured blood counts.
- The datasets are public and de-identified; no new participants were recruited.
- AI assistance (Anthropic's Claude) was used to write the code and run the analyses under the author's direction; every
  decision was approved by the author and recorded before use.

## 8. Reproducing the model

```bash
.venv/bin/python -I scripts/ml_gse63060.py --version vN           # retrain and cross-validate (new version folder)
.venv/bin/python -I scripts/ml_apply_gse63061.py --ml-version v1   # apply the frozen model once
.venv/bin/python -I scripts/ml_apply_gse140829.py --ml-version v1
```

Each run checks the code, environment and input hashes and writes to a new, never-overwritten folder.
