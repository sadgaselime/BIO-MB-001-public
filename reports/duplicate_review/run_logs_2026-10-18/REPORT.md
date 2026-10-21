# Tier B step 4 (C1 metadata duplicate review): GSE63060, 2026-10-18

**Authorization:**
- D18 D-1 handling and review workflow/log approved by the PI 2026-10-18 ("i approve"); recorded at SAP v7:621 and in the brief.
- Tier B progression under the PI instruction "keep working and finish whatever is needed" (2026-10-18).

No expression value was read; no QC, model or analysis was run.

## Code and tests

- Runner: `scripts/duplicate_review_c1_gse63060.py` (v6 §4 candidate source C1). It reads only the allowed identity fields, the replicate mentions and the characteristics KEYS. Diagnosis and phenotype values and submitter contact fields are never read.
- Precondition: the accepted eligibility output (Tier B step 3).
- Tests: `tests/test_duplicate_review_c1.py`, 6/6.
- Full suite: **280/280 passed** under the audit hook, with no guarded opens.

## Run

| Item | Value |
|---|---|
| Command | `.venv/bin/python -I scripts/duplicate_review_c1_gse63060.py --version v1` |
| Time (UTC) | 2026-10-18T18:30:33Z to 2026-10-18T18:30:33Z |
| Result | exit=0 |
| Output | `reports/duplicate_review/GSE63060/c1_v1/` (accepted; executed code tracked) |

## Result

**No C1 candidates.**
- No identical GSM, barcode or participant code within GSE63060.
- No deposited replicate annotation in any examined field.
- Characteristics keys seen: age, ethnicity, gender, included in case -control study, status, tissue.

The log status is "complete: no C1 candidates; no reviewer decision required".

The **C2 expression candidates** (D-3/D-4) belong to Tier B step 6, after QC Stage A.

## Output hashes

| File | SHA-256 |
|---|---|
| `c1_review_table.tsv` (header only) | `220b3cf6…` |
| `duplicate_review_log_c1.json` | `5af748f5…` |
| `code_identity.json` | `6ce5d218…` |
| `manifest.json` | `ecfe03a1…` |

A git-ignored bytecode cache file for the registry was removed after the run.
