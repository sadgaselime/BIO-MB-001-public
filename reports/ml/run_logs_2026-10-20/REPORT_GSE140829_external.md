# Frozen GSE63060 classifier applied once to GSE140829 — run report (2026-10-20)

Authorization: explicit PI instruction 2026-10-20 ("run it"). Approved ML protocol (v7:603). Applied once; no re-fitting
or tuning; a second application is refused by the script. Accepted (code identity and executed-code verification: no
problems; two applications byte-identical). Manifest SHA-256: c7bd7bd70ebff215b2de1118f6d87af0243a0e8bd91b2132049f529d34316d78
Final model SHA-256 (from reports/ml/GSE63060/v1): e4f7f18e73795610d598abb676608dc2ad6edee291e4a9bfcf35be35cc239e51

Population 201 AD vs 248 CTL (approved list); unit = deposited batch (19); 200/200 model genes present (D19-1 mapping).

| Model | AUROC (DeLong 95%, approximate) | Sens | Spec | PPV | Brier | Calibration slope |
|---|---|---|---|---|---|---|
| Frozen ridge | **0.525 (0.471–0.579)** | 0.612 | 0.411 | 0.457 | 0.304 | 0.13 |
| Frozen age model (B1) | 0.472 (0.418–0.527) | — | — | — | 0.268 | −0.18 |

Ridge − age: +0.053 (−0.022 to 0.128), p = 0.17.

**Result: the frozen classifier does not discriminate AD from controls in GSE140829.** Its interval includes 0.5, and it
does not differ from the age model. This is a prespecified external test and is reported as it stands.

Context, from other accepted outputs:
- Within GSE63060 (nested CV) the AUROC was 0.841. Applied to GSE63061, a related AddNeuroMed cohort, it was 0.769.
- In GSE140829 the locked signature's composite score still shifts toward AD (C-c one-sided p = 0.0019; 43/200 genes
  replicated; 183/200 concordant). So a group-level association transports, but this individual-level classifier does not.

Possible explanations (hypotheses only; none is tested here, and none may be used to tune or re-test on GSE140829):
- different processing (GSE140829 lumi VST with its own normalization) and platform version (GPL15988 vs GPL6947);
- cohort, recruitment and label-definition differences between AddNeuroMed and GSE140829;
- a group-level effect that is small relative to individual variation in GSE140829 (C-c θ = 0.25 score units);
- per-unit centring, where 3 of the 19 batches are single-group;
- the GSE63061 result may be inflated by participant overlap and shared processing (H9).

Implication: the classifier is not externally validated. Any revised model would be post hoc. GSE140829 has now been
used as this model's test set and cannot serve again as an untouched test for a revised model.
