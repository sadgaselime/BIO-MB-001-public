# GSE63060 discovery: Tier B steps 6–10, 2026-10-18

**Authorization:** PI approvals of 2026-10-18 (recorded in SAP v7 §11 and the brief):
- H1 analysis specification (v7:604);
- D7: c₁ = 3, c₂ = 5, c₃ = 10 (v7:610);
- D15 (v7:618);
- D16 + S-R8m (v7:619);
- R8 outcome R0 + R3;
- QC Stage A ruling;
- the GSE63060 exclusion list, approved as rule-applied (v7:625).

**PROVISIONAL.** The SAP remains a proposed draft, not approved or frozen. No signature is locked (step 11), and no
validation, replication or specificity analysis has been performed.

## Code and tests

- `scripts/discovery_prep_gse63060.py`, steps 6–9. Tests: `tests/test_discovery_prep.py` 7/7.
- `scripts/discovery_fit_gse63060.py`, step 10. Tests: `tests/test_discovery_fit.py` 4/4, including:
  - a synthetic end-to-end limma fit through the D8 runner;
  - an exact check that the full-rank basis reproduces the chip-indicator coefficient (Frisch–Waugh–Lovell).
- Full suite: **303/303** under the audit hook, with no guarded opens.

## Steps 6–9: prep_v1

`2026-10-18T19:18:17Z` to `2026-10-18T19:18:18Z` UTC, exit=0. Accepted. No expression values were read.

**Step 6, C2 expression duplicates:** none (0 A2 pairs and 0 R9 referrals).

**Step 7, primary population:** **145 AD vs 60 CTL**. Covariates are complete.

| Group | Mean age (SD) | Male |
|---|---|---|
| AD | 75.4 (6.6) | 46 of 145 |
| CTL | 72.5 (5.9) | 20 of 60 |

**Step 8, M1–M8 (one locked run):** **PROCEED**.

| Decision check | Result | Threshold |
|---|---|---|
| Mixed chips (M2) | 25 | ≥ 3 |
| AD arrays on mixed chips | 123 | ≥ 5 |
| CTL arrays on mixed chips | 60 | ≥ 5 |
| Estimability E (M3) | 0.821 | > 10⁻⁸ |
| VIF (M4) | 1.22 | ≤ 10 |

Descriptive checks: residual df 173; no singleton chips; one aliasing dependency (the chip indicators sum to the intercept).

**Step 9, G3 selection table:** 17,425 genes from 25,305 eligible probes, taken from the pinned A0 table.

## Step 10: discovery fit (fit_v1)

`2026-10-18T19:20:45Z` to `2026-10-18T19:22:24Z` UTC, exit=0. The output is accepted, two fits were byte-identical, and the R pins matched
(R 4.6.1, Bioconductor 3.23, limma 3.68.5).

**Design:** [Q_N, g], with nuisance terms intercept, age, sex and chip. **Method:** limma lmFit + eBayes(trend = TRUE). BH is applied within each family.

| Family | Tested | q < 0.05 | Up in AD | Down in AD |
|---|---|---|---|---|
| **Gene level (claims)** | 17,425 | **1,401** | 662 | 739 |
| Probe level (reported separately) | 38,323 | 1,744 | 811 | 933 |

The ten strongest genes are all lower in AD. By Entrez ID: 51258, 4694, 1069, 4725, 6166, 529, 7979, 10063, 51506, 6902.
Effects are small: the median |log₂ effect| over all genes is 0.013, and the largest is about 1.08.

## Caveats that apply to every result

1. **E2 estimand:** about 41 of the 145 "AD" arrays were probably MCI at blood draw.
2. **Controls:** 44 of 104 were excluded for corroborated sex mismatches, which appear to be a permutation among controls. The D9 query is pending, and S-R8m and S5f are the planned sensitivity views.
3. **Inherited data:** the data are the submitter-normalized values (D3); submitter QC cannot be audited (R10).
4. **Blood, not brain:** these are blood transcript differences. No causal or diagnostic claim is made.

## Not done (next steps and their gates)

- **Step 11, signature lock.** It needs the validation specification: D20, D12, the covariate table and the lock contents (v7 §7).
- **Sensitivity analyses S1–S16 and S-R8m.** Approved (D16); not yet run.
- **External cohorts.** GSE63061 (descriptive, D20); GSE140829 (D11, D19 and its eligibility rules); GSE99039 (D13, δ).
- **Any classifier.** It needs a written ML protocol (exploratory only; nested cross-validation inside discovery).

## Output hashes (fit_v1; see its manifest for full values)

| File | SHA-256 (prefix) |
|---|---|
| `gene_level_results.tsv` | `5773dcc1…` |
| `probe_level_results.tsv` | `6dc837f4…` |
| `discovery_summary.json` | `f3649e0c…` |
| `manifest.json` | `d00d70fa…` |
| `code_identity.json` | `9063ae69…` |

**Housekeeping:** after the fit run, cleanup removed every bytecode cache file in `scripts/__pycache__` (git-ignored; regenerated
automatically), not only the one this run created.
