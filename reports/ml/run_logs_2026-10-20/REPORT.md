# GSE63060 exploratory ML run — report (2026-10-20)

Protocol: reports/planning/ML_PROTOCOL_DRAFT_2026-10-19.md (approved as drafted, v7:603); implementation record
reports/planning/ML_IMPLEMENTATION_SPEC_2026-10-19.md; environment R glmnet 5.1 (v7:611). Exploratory (v2:550–551).

Run: `.venv/bin/python -I scripts/ml_gse63060.py --version v1`, started 2026-10-19 19:18, accepted 2026-10-20 ~11:5x
(code identity and executed-code verification: no problems; observed CV, first 3 permutations and final model recomputed
byte-identical). Wall time 16.5 h, of which ~4 h with the Mac fully awake (pmset log; the rest was system sleep).
Manifest SHA-256: ebb7c816af15e07216e32dd3bbe76ccdca3d708dd22a3bebbc51ca04400e0fc0
Final model SHA-256: e4f7f18e73795610d598abb676608dc2ad6edee291e4a9bfcf35be35cc239e51
Earlier interrupted attempt: reports/ml/GSE63060/v1.staging-b71dcb7cc907 (code record only; never accepted).

Inputs: 205 arrays (145 AD, 60 CTL), 29 chips, 17,416 genes (G3 minus 9 R8 sex-probe genes).

| Model (20 × 5-fold leave-chip-group-out) | AUROC mean (2.5–97.5% over repeats) | Sens | Spec | PPV | Brier | Calibration slope |
|---|---|---|---|---|---|---|
| **Ridge (primary)** | **0.841 (0.824–0.852)** | 0.750 | 0.753 | 0.881 | 0.154 | 0.93 |
| Elastic net (secondary) | 0.850 (0.836–0.864) | 0.775 | 0.753 | 0.884 | 0.153 | 1.63 |
| B2 equal-weight score | 0.780 (0.774–0.788) | — | — | — | — | — |
| B1 age only | 0.622 (0.612–0.632) | — | — | — | 0.241 | 0.77 |
| B0 prevalence | — | — | — | — | 0.208 | — |

DeLong on repeat-averaged predictions (approximate): ridge AUROC 0.846 (0.788–0.904); ridge − age +0.223 (0.127–0.320),
p = 5.9e-6; ridge − equal-weight +0.063 (0.023–0.102), p = 0.0019; ridge − elastic net −0.016 (−0.038–0.006), p = 0.15.
Permutation null (200 within-chip label permutations): null mean 0.485, 97.5th percentile 0.587, max 0.642; observed 0.841;
p = 1/201 = 0.005 (the smallest attainable with 200 permutations).
Final model (all 205 arrays): k = 200 genes, lambda 0.236, threshold 0.543. Inner choice of k across outer folds: 50 (59), 100 (31), 200 (10).

Interpretation limits:
- Exploratory; against deposited labels (E2; some "AD" may be MCI at draw). Not diagnostic accuracy.
- Calibration intercept +0.74 (probabilities too low on average) is expected from inverse-frequency class weights.
  Probabilities are not calibrated risks. The PPV of 0.88 reflects this cohort's 71% AD prevalence.
- Cross-validated within one cohort and platform; batch handled by chip-grouped folds and per-chip centring.
- External application (GSE63061, related cohort, H9) has not been run; it needs PI authorization.
