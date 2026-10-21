# Tier B step 3: GSE63060 eligibility, 2026-10-18

**Authorization:** PI instruction 2026-10-18, "keep working and finish whatever is needed". The rules are those approved in D2 (2026-10-10; v7:605).
This step is **metadata only**: no expression value was read, and no QC, duplicate review, model or analysis was run.

## Code and tests

- New runner: `scripts/eligibility_gse63060.py`. It applies D2 rules R1, R2-ID, R3, R4, R5 and R11; records R12; documents R6 and R10; and writes the R13 log.
- It runs under the code-identity lifecycle with executed-code verification, and refuses to run unless the annotation pin (Tier B step 2) is accepted.
- New synthetic tests: `tests/test_eligibility_gse63060.py`, 9/9 passed.
- Full project suite: **274/274 passed** under an audit hook, with no opens under `data/`, `reference/` or `reports/`.

## Run

| Item | Value |
|---|---|
| Command | `.venv/bin/python -I scripts/eligibility_gse63060.py --version v1` |
| Time (UTC) | 2026-10-18T18:04:50Z to 2026-10-18T18:04:50Z |
| Result | exit=0 |
| Output | `reports/eligibility/GSE63060/v1/` (accepted; executed code tracked) |

**Inputs:**
- Series Matrix sample headers and the table column header only; reading stops at the table.
- The first line only of each supplementary file, for R11.
- The phenotype table, as a cross-check.
- Every input matched its download manifest.

The run also requires and cites the annotation pin record `cde8ccd7…`.

## Result (pre-QC; matches D2 exactly)

| Quantity | n |
|---|---|
| R1 universe (Series Matrix GSM columns) | 329 |
| R2-ID exclusions | 0 |
| R5 exclusions | 0 |
| AD, primary contrast (cases) | 145 |
| CTL, primary contrast (controls) | 104 |
| MCI, retained outside the primary contrast (R4) | 80 |
| R11 non-eligible supplementary columns | 5 |

The five R11 columns are:
- `4856076038_D` in the normalized file and in the non-normalized file (an expression-only array);
- three empty-header columns in the non-normalized file.

This is the same as D2's description of R11.

**All 9 validation checks passed**, including agreement with the phenotype table on barcode, participant code and status. Submitter contact fields are not present in any output.

## Output hashes

| File | SHA-256 |
|---|---|
| `eligibility_log.tsv` | `fc2509df7a795dac3506796dd0a33693d782cdd16ca3c9598f2baf7cee44780b` |
| `eligibility_summary.tsv` | `479e10f435fc451289b4fe1be1f134e8635c5e9a31cc92385ff0694790b71dbd` |
| `r11_supplementary_columns.tsv` | `07ed4b9a2fa10c77ee1023cb83caf2f8f7c4c5cc4ad1df8303faa12c01bf851d` |
| `code_identity.json` | `a484d1053d40dc08299c28089b43408e29a6af68340413ce6ad526099a3f779a` |
| `manifest.json` | `7b3a97e20f69624794fddd91f4c6cb00710a74ad7d0cb157c5ebde1fb0a728d8` |

**Side effect:** the run wrote a git-ignored bytecode cache file for the bootstrap registry, which was removed.

## Not done (needs PI decisions)

- **Tier B step 4, duplicate review.** It needs the remaining D18 parts.
- **QC Stage A** (R8/R9, D5/D22). The qc_stage_a code refuses non-synthetic cohorts by design, so it needs integration and authorization.
- **R2-COV** (complete-case eligibility per model) is applied at model time.
