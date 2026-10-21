# Tier B step 5: QC Stage A for GSE63060 (candidates recorded only), 2026-10-18

**Authorization:** PI ruling 2026-10-18, option A, recorded at SAP v7:625 and in the brief (D5 + D22 section). QC Stage A may
compute and record candidate exclusions for GSE63060. **No exclusion is applied** until the exclusion-list approval step
(v5:123–129) and D16 are decided, and Stage A outputs are **not usable downstream** until then.

## Code changes (permission granted by the PI at the prompt, option 1)

- **`src/biomarker_project/qc_stage_a.py`:**
  - Real cohorts are still refused unless `real_data_authorization` is non-blank.
  - The authorization and the data origin are recorded in the cohort status.
  - Nothing else changed: candidates are never applied, and `stage_a_outputs_usable_downstream` is always False.
- **`tests/test_qc_stage_a.py`:** two tests added.
  - Blank or missing authorization is refused.
  - An authorized real cohort applies nothing and gives the same QC results as the same synthetic data.
- **New runner `scripts/qc_stage_a_gse63060.py`:**
  - Inputs: Series Matrix values as deposited (D3), plus only the gsm and gender columns of the eligibility log. Diagnosis is never read.
  - Preconditions: the pin, eligibility and C1 duplicate review must all be accepted, and C1 must be complete.
  - Runs under the identity lifecycle with executed-code verification.
- **Tests:** `tests/test_qc_stage_a_gse63060.py` 3/3; full suite **285/285** under the audit hook, with no guarded opens.

## Run

| Item | Value |
|---|---|
| Command | `.venv/bin/python -I scripts/qc_stage_a_gse63060.py --version v1` |
| Time (UTC) | 2026-10-18T18:36:53Z to 2026-10-18T18:36:56Z |
| Result | exit=0 |
| Output | `reports/qc_stage_a/GSE63060/v1/` |

The output is accepted; executed code is tracked (7 files through the hashing loader); 6/6 checks passed.

## Results

**Input:** 38,323 probes × 329 arrays; 0 non-finite values; recorded sex is F 200, M 129.

**R8 (sex consistency):** status "completed — informative". Both axes split (non-degenerate), and the V-A gate is technically open.

| R8 category | Arrays |
|---|---|
| Concordant on two axes | 246 |
| Ambiguous (axes disagree; Tier F3, retained) | 39 |
| **Discordant on two axes (candidate Tier Q1)** | **44** |

**R9 (array outliers):** completed; 329 arrays scored; 327 passed; 2 flagged at k = 3 (Tier F1, retained). There were 0 numerical failures (P3), 0 near-identical pairs (A2) and 0 referrals to D18.

**Candidate exclusions:** 44 (all Q1), each marked "PROPOSED — NOT APPLIED". **No exclusion was applied.**

## FINDING FOR PI REVIEW: the R8 result is implausible on this data

44 two-axis discordant arrays (13%) is far more than the few sex mismatches reported for this cohort (original XIST check;
Patel 2020 found 2 further mismatches). The evidence points to a measurement problem, not 44 mislabelled samples:

- **The axes are compressed.**
  - XIST ranges 7.37 to 9.97; the split is at 8.15, with class means 7.66 and 8.64.
  - The Y score (the median of 13 centred Y probes) ranges −0.08 to 0.37; the split is at 0.065.
  - Female-versus-male XIST differences on Illumina log₂ data are usually several units.
- **The discordance is symmetric:**
  - 22 recorded-M arrays are female-type on both axes;
  - 22 recorded-F arrays are male-type on both axes;
  - 39 arrays have axes that disagree.
- **Plausible causes, not verified:**
  - the deposited values are already normalized and compress the sex signal;
  - the median over 13 Y probes is dominated by probes that are not expressed in blood.

This is R8 exactly as approved (D5 option (b), no validated threshold; the brief notes it is "a weaker safeguard").

**Recommendation:** do not use the Q1 candidates or the "informative" R8 status, at the exclusion-list approval step or anywhere else,
until the PI has reviewed whether R8 as specified is valid for GSE63060. Any change to R8 (probe set, axis definition,
or D5 option) is a Tier A change after Tier B has started, so it needs a documented protocol amendment (v6 §2.2).
Nothing has been applied, so nothing downstream is affected.

## Output hashes

| File | SHA-256 |
|---|---|
| `qc_audit.tsv` | `76fa385e…` |
| `qc_candidate_exclusions.tsv` | `4983cca2…` |
| `qc_cohort_status.tsv` | `a3e4b986…` |
| `qc_a2_pairs.tsv` | `13f3d57c…` |
| `qc_r8_axes.json` | `5c523609…` |
| `qc_r9_summary.json` | `5757f1f9…` |
| `code_identity.json` | `03c1a663…` |
| `manifest.json` | `22d1c6f8…` |

A git-ignored bytecode cache file for the registry was removed after the run.
