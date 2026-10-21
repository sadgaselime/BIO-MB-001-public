# Tier B step 5, Stage B: GSE63060 descriptive QC review and rule-applied exclusion list (2026-10-18)

**Authorization:** Tier B progression under the PI instructions of 2026-10-18. The QC policies are D22 rows 1–6 (v7:625).

Stage B is descriptive counts only (v5:268–273). There is no inferential test, no model, and no linking of expression to diagnosis.

**The exclusion list is RULE-APPLIED and AWAITS PI APPROVAL** (v5:123–129). Nothing has been applied.

## Code and tests

- **Runner:** `scripts/qc_stage_b_gse63060.py`, which runs under the identity lifecycle with executed-code verification.
- **Tests:** `tests/test_qc_stage_b.py` 4/4; full suite **292/292** under the audit hook, with no guarded opens.

## Run

| Item | Value |
|---|---|
| Command | `.venv/bin/python -I scripts/qc_stage_b_gse63060.py --version v1` |
| Time (UTC) | 2026-10-18T19:07:14Z to 2026-10-18T19:07:15Z |
| Result | exit=0 |
| Output | `reports/qc_stage_b/GSE63060/v1/` (accepted) |

## Rule-applied exclusion list (proposed; awaiting approval)

| Tier | n | Rule |
|---|---|---|
| P1 | 80 | MCI, a non-contrast label (R3/R4); kept in the dataset |
| P2 | 0 | — |
| P3 | 0 | — |
| Q1 | 44 | R8 two-axis discordant (D22 row 1; S5f re-includes) — **all 44 are deposited CTL** |

**Proposed primary population: 145 AD vs 60 CTL.**

Retained with flags (never exclusions): 26 F3 (R8 ambiguous) and 2 F1 (R9 k = 3).

## Stage B finding (descriptive)

**R8 two-axis discordant by deposited group:**

| Group | Discordant (Q1) |
|---|---|
| AD | 0 of 145 |
| CTL | 44 of 104 |
| MCI | 0 of 80 |

**Corroborated mismatches (both strong Y markers; r8_diagnostics v2):** all 46 are CTL, 23 recorded F and 23 recorded M.

Among the 104 CTL, expression-derived sex totals equal the recorded totals exactly: **62 F and 42 M**. This is the pattern of a
**permutation of sex labels, or of sample identities, among the control arrays**. It is not established which.

**Implications for the PI:**

1. **If only the sex labels are permuted**, the arrays are still controls:
   - excluding 44 of them (Q1) costs power but does not bias the AD–CTL contrast;
   - for those arrays the recorded-sex covariate would be wrong.
2. **If sample identities are permuted among controls**, every control array's other metadata (age, sex) may be misattached. The control label itself would remain correct.
3. **Approving the list is limited to verifying that the rules were applied correctly** (v5:123–129). Any other handling needs a
   documented protocol amendment before the population is linked to any expression model. Examples: re-including the 44 with expression-derived sex as the covariate, or dropping recorded sex from the adjustment set.
4. **The D9 data-owner query** (draft: `reports/phase3b/amendments/D9_GSE63060_LABEL_QUERY_DRAFT_2026-10-18.md`) should now ask
   specifically about the control arrays.

## Output hashes

| File | SHA-256 |
|---|---|
| `exclusion_list.tsv` | `28cf7aac…` |
| `summary.tsv` | `a32cb9db…` |
| `counts_by_diagnosis.tsv` | `502189bc…` |
| `counts_by_chip.tsv` | `52725b7c…` |
| `retained_flags.tsv` | `846dc109…` |
| `code_identity.json` | `9f8353e0…` |
| `manifest.json` | `69d8d182…` |
