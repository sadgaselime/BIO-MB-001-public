# ML implementation specification (2026-10-19) — fixed before any real-data ML run

Implements the approved protocol (reports/planning/ML_PROTOCOL_DRAFT_2026-10-19.md, SHA-256 fb4f7881…; v7:603) with
R glmnet 5.1 (v7:611). Noncanonical. These are technical choices the protocol leaves open; they are fixed here,
before any ML code reads real data, and none is chosen from results.

| Element | Fixed choice |
|---|---|
| Code | R/ml_glmnet_cv.R (5c3bd845c4521eb2…), scripts/ml_gse63060.py (c9f04e732e531651…), scripts/ml_apply_gse63061.py (2e1261ce2098b256…) |
| Inputs | Approved GSE63060 population (145 AD, 60 CTL); G3 genes minus the R8 sex probes' genes (XIST + 13 Y probes, via A0) |
| Batch handling | Every gene centred within its chip (diagnosis-blind); with chip-grouped folds this equals centring test chips on their own means |
| Folds | Chips shuffled (seeded), stable-sorted by AD fraction, dealt in snake order to 5 folds (outer) and 5 folds (inner); 20 outer repeats; seed 20261019 |
| Selection | limma lmFit + eBayes(trend = TRUE) on training arrays: intercept, age (scaled), recorded sex, chip indicators, AD; rank by p, then abs(t) desc, then gene ID; k ∈ {50, 100, 200} |
| Model | glmnet binomial, alpha = 0 (ridge); standardize = FALSE after training-set z-scaling; 60-point log lambda grid 100 → 0.001; class weights n/(2·n_class); full path (no early stopping) |
| Inner choice | Minimum class-weighted binomial deviance on pooled inner out-of-fold predictions; ties → larger lambda, then smaller k |
| Threshold | Youden-optimal on the same inner predictions (classify p ≥ threshold) |
| Secondary | Elastic net alpha = 0.5 on all genes, lambda by the same inner criterion |
| Baselines | B0 training prevalence (Brier only; its pooled AUROC is uninformative and not reported); B1 class-weighted logistic on age; B2 equal-weight score of the top 200 training genes, signed by limma t |
| Metrics | Per repeat on pooled OOF predictions: AUROC, AUPRC (average precision), Brier, calibration intercept/slope, balanced accuracy. Summary: mean and 2.5–97.5th percentiles over repeats (CV variability, not a CI). DeLong AUROC and paired-difference intervals on per-array predictions averaged over repeats, labelled approximate |
| Permutation null | 200 within-chip label permutations, primary model only (ridge with selection; secondary/baselines omitted to bound compute), all 20 repeats each; p = (1 + #null ≥ observed)/(1 + 200) |
| Determinism | Observed CV, final model and the first 3 permutations recomputed and compared byte-for-byte |
| Final model | Inner procedure on all 205 arrays; coefficients, training means/SDs, k, lambda, threshold and B1 frozen and hashed |
| GSE63061 | Separate runner, applied once: per-chip centring, within-cohort standardization, missing genes at z = 0 (counted), frozen threshold; labelled related cohort (H9), cross-platform, exploratory |
| Leakage tests (passed, synthetic) | random labels → chance AUROC; chip-label confound (offset alone AUROC 0.87) not exploited (< 0.7); planted signal found; changing test-chip expression leaves every training-fold choice unchanged; DeLong matches an independent implementation |
