# ML protocol — PROPOSED DRAFT FOR PI REVIEW (not approved; noncanonical)

Date: 2026-10-19. Status: **proposal only.** Nothing here is approved, and no ML code has been written or run.
Governing rule: SAP v2:550–551 (active). Machine learning is exploratory, uses nested cross-validation inside
discovery only, and is never tuned on validation cohorts. It does not replace the inferential analyses (C-c, C-a)
and makes no diagnostic-accuracy claim (v6 §8.6 claim boundaries).

## M0. Environment blocker (must be resolved first)

The locked environment has **no ML library**. `.venv` has no scikit-learn or scipy. `renv.lock` holds 6 packages,
none of them glmnet. Options (each needs PI authorization plus a D8 environment amendment and new lock hashes):

- **E-a (recommended): R `glmnet`** (with its dependencies) added to `renv.lock`. It is the reference implementation
  of penalized logistic regression, and the R toolchain is already pinned and verified for limma.
- E-b: scikit-learn (and scipy) added to the hashed Python lock (`requirements.hashes…txt`) and `pyproject.toml`.
- E-c: no install. Ridge logistic regression written in numpy (Newton–IRLS) and checked against a closed-form
  test. This is feasible, but a hand-written fitter is weaker evidence for a paper. Not recommended.

## M1. Specification for review (each item marked [PROPOSED])

| Item | Proposal | Why / alternative |
|---|---|---|
| Target | Deposited AD vs CTL label, as in E2 (H1) | The labels are noisy: about 41 "AD" may be MCI at draw, and the GSE63060 control sex annotations are corrupted (44 mismatches; D9 open). Performance is an estimate against noisy labels. |
| Unit | One array = one participant. C1 found no duplicates in GSE63060. | — |
| Population | The approved GSE63060 primary population: 145 AD and 60 CTL | — |
| Inputs | G3 gene-level expression (17,425 genes) for the **whole feature-selection pipeline**. **Not** the locked 200-gene signature. | The lock was selected on all 205 arrays, so using it inside GSE63060 CV leaks. It may be used only on GSE63061, as a fixed model. |
| Excluded inputs | Recorded sex (corrupted in controls). Sex-chromosome genes (XIST plus the 13 R8 Y probes' genes) [option]. Chip ID as a predictor. | Prevents the classifier learning sex or batch. Alternative: keep the sex-chromosome genes and report a sensitivity analysis. |
| Covariates | Age is **not** an input to the expression model. A separate covariate-only baseline is fitted. | AD participants are older (75.4 vs 72.5 years). Age alone may discriminate. |
| Outer CV | **Leave-chip-group-out:** 5 folds, grouping whole chips (29 chips), stratified by AD fraction as far as grouping allows; repeated 20 times with fixed seeds. | Random array-level splits let chip effects leak between training and test. Alternative: stratified 5×10 repeated CV, reported as a sensitivity analysis. |
| Inner CV | 5-fold, grouped by chip, inside each outer training set: tunes λ (and α for an elastic net) | — |
| Within-fold preprocessing | All steps learned on training arrays only: gene centring and scaling; chip-mean removal estimated on training chips (test chips centred on their own diagnosis-blind means); feature filter | Diagnosis-blind per-chip centring of test chips uses no labels. |
| Feature selection | Inside each training fold: limma (age, sex, chip) top-k genes by p, with k ∈ {50, 100, 200} tuned in the inner loop. Then L2 (ridge) logistic regression. Primary model: **ridge with k tuned.** Secondary: elastic net (α ∈ {0.5}) on all genes. | Ridge is stable with correlated genes. The penalty and k are prespecified, never chosen by outer-loop results. |
| Class balance | Class weights inversely proportional to frequency (145/60); no resampling | — |
| Baselines | (B0) prevalence-only; (B1) age only (logistic); (B2) the W1 score of the locked signature recomputed **inside each fold** from fold-selected genes (no learning beyond selection) | B2 asks whether a learned weighting beats an equal-weight score. |
| Primary metric | Out-of-fold **AUROC**, with a 95% CI from the repeated-CV distribution, plus a DeLong CI on the pooled OOF predictions labelled approximate | — |
| Secondary metrics | Balanced accuracy at a threshold fixed in the inner loop; Brier score; calibration intercept and slope; AUPRC | — |
| Comparisons | AUROC difference vs B1 (age) and vs B2, reported with CIs, descriptive (exploratory) | — |
| Label-permutation check | 200 permutations of labels **within chip**, running the full pipeline | Gives the null AUROC distribution and detects leakage. |
| Leakage tests (synthetic, before real data) | (1) Pipeline on random labels gives AUROC ≈ 0.5. (2) A planted chip-label confound is not exploited under chip-grouped CV. (3) No test-fold row reaches any fitted object (asserted in code). | — |
| External application | Final model refit on all 205 arrays with the inner-loop procedure, frozen and hashed, then applied **once** to GSE63061 (cross-platform: GPL6947 to GPL10558, Entrez/G3; within-cohort diagnosis-blind standardization). Labelled "related cohort, possible participant overlap (H9)". GSE140829 only after D19 and D11. | Not used for tuning. |
| Reporting | TRIPOD+AI items as applicable; all prespecified models reported, including null results | — |

## M2. What this cannot claim

- No clinical diagnostic accuracy. The labels are deposited, the case mix is selected and there is no prospective cohort.
- GSE63061 performance is not independent validation (H9).
- No claim of superiority over published classifiers.

## M3. Decisions needed from the PI

1. The environment route (E-a / E-b / E-c) and the authorization to install. A D8 amendment is needed.
2. Approval of M1 as the written protocol: target, inputs, exclusion of sex-chromosome genes, chip-grouped CV, primary
   ridge model, baselines and metrics. This must happen **before** any ML code touches real data.
