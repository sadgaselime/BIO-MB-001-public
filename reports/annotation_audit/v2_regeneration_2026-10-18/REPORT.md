# Annotation artifact v2 regeneration (2026-10-18)

**Authorization:** explicit PI instruction (2026-10-18), "Regenerate v2 only". GPL570 (D6-F), C15 and Illumina A0 (D6-G)
were regenerated in the D8-approved environment (SAP v7:112). **No annotation pin was created.** No Tier B step 3 or later,
QC, differential expression, validation or model was run.

## Commands

All were run from the project root, in this order, under the code-identity lifecycle and executed-code registry (UTC):

| Command | Start | End | Exit |
|---|---|---|---|
| `.venv/bin/python -I scripts/annotation_gpl570_option_a_counts.py --version v2` | 17:52:03 | 17:52:04 | 0 |
| `.venv/bin/python -I scripts/c15_cohort_probe_presence.py --version v2` | 17:52:09 | 17:52:22 | 0 |
| `.venv/bin/python -I scripts/annotation_illumina_a0_classification.py --version v2` | 17:52:26 | 17:52:39 | 0 |

Each script printed `accepted reports/annotation_audit/<artifact>/v2`, and stderr was empty. Logs are in this folder.

## Independent verification (read-only, after the runs)

**Every v2 folder passes** `acceptance_problems(require_equivalence=True, require_executed_code=True)` with no problems.

**Tables:**
- Every table is **byte-identical to v1** (`cmp`) and equals the v1 manifest's determinism hash.
- The four D6-recorded hashes (v7:609 and the A0 manifest) are reproduced:
  - GPL570 `probe_set_classification.tsv`: `9e5f23fa…`
  - A0 `a0_probe_classification.tsv`: `6da6cf2c…`
  - A0 `a0_counts.tsv`: `a68aa750…`
  - A0 `a0_discordant_probes.tsv`: `e5b99695…`
- The two C15 tables (`3e83d320…`, `d110318e…`) are byte-identical to v1.

**Validation passed:** GPL570 status OK; C15 31/31 checks; A0 18/18 checks.

**Executed code:** tracked in every run.

| Run | Executed through the hashing loader | Bootstrap code objects |
|---|---|---|
| GPL570 | 3 | its runner and `scripts/_executed_code.py` |
| C15 | 4 | its runner and `scripts/_executed_code.py` |
| A0 | 5 | its runner and `scripts/_executed_code.py` |

**Mismatches:** the only informational mismatch was `git_status_changed`, caused by the outputs being written.

**Identity** (the same in all three runs):
- aggregate `42eaf15b2223da78…` over 67 code-set files;
- git HEAD `f4d7810`; dirty = true (untracked and modified files are hashed);
- D8 environment records equal to the current ones: conda spec `52e2e785…`, Python lock v2 `a57412d3…` and its manifest `9620fe56…`, `renv.lock` `fa51c7b9…`.

**Interpreter:** `.venv`, isolated mode.

**No staging or FAILED folders exist.**

**Side effect:** the runs wrote `scripts/__pycache__/_executed_code.cpython-313.pyc`, because the bootstrap registry is loaded by Python's standard loader. That file is git-ignored and excluded from the code set, and was removed afterwards.

## What this does and does not establish

- **Establishes:** the v1 annotation artifacts are reproduced byte-for-byte in the D8-approved environment, with verified source-tree identity and verified executed code. The future pin can cite these v2 artifacts (v7:609 via the pin builder).
- **Does not establish:** any biological result, QC status or analysis. The gene-history v1 table remains a frozen input whose raw source is not retained (v7:643).

## Hashes

Every file in the three v2 folders is listed in `v2_artifact_sha256.txt`. This folder's own files are listed in `SHA256SUMS`.
