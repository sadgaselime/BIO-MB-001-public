# GSE63061: Tier B steps 3–5 (eligibility, C1 duplicate review, QC Stage A/B), 2026-10-19

**Authorization:** PI "go ahead", 2026-10-19, recorded at SAP v7:605 (D2 applied to GSE63061) and v7:625 (GSE63061 QC ruling).
- The rules and QC policies are the same as for GSE63060.
- Candidates are computed and recorded only; **nothing is applied** until the GSE63061 exclusion list is approved as rule-applied (v5:123–129).
- No expression is linked to diagnosis.
- GSE63061's role is related-cohort consistency (possible participant overlap with GSE63060, H9).

## Code

- **Parametrized by `--accession`:**
  - `scripts/eligibility_gse63060.py`;
  - `scripts/duplicate_review_c1_gse63060.py`;
  - `scripts/qc_stage_a_gse63060.py` (GSE63061 shape 32,049 × 388; its own authorization text);
  - `scripts/qc_stage_b_gse63060.py`.

  The GSE63060 defaults are unchanged. Backups are in `reports/_pre_edit_copies/2026-10-19_GSE63061_parametrize/`.
- **Tests:** `tests/test_gse63061_configuration.py` (4) and a GSE63061 configuration test in `tests/test_eligibility_gse63060.py`. One label assertion there was updated, because the check label now reports the configured count.
- **Full suite:** **320/320** under the audit hook, with no guarded opens.

## Runs

All runs used `.venv/bin/python -I <runner> --version v1 --accession GSE63061`, and all outputs are accepted with executed code tracked.

| Step | Output | Time (UTC) |
|---|---|---|
| Eligibility | `reports/eligibility/GSE63061/v1` | 2026-10-18T21:35:09Z |
| C1 duplicate review | `reports/duplicate_review/GSE63061/c1_v1` | 2026-10-18T21:35:10Z |
| QC Stage A | `reports/qc_stage_a/GSE63061/v1` | 2026-10-18T21:35:10Z |
| QC Stage B | `reports/qc_stage_b/GSE63061/v1` | 2026-10-18T21:35:13Z |

A first attempt failed at argument parsing, before anything was created; the cause was a shell word-splitting slip. It was re-run.

## Results

**Eligibility:**
- Universe: 388 GSMs.
- R2-ID: 0 exclusions.
- **R5: 6** excluded from contrasts (borderline MCI 3, OTHER 1, CTL to AD 1, MCI to CTL 1).
- AD 139, CTL 134, MCI 109.
- R11: 0. All checks passed, including agreement with the phenotype table.

**C1 duplicate review:** complete, no candidates.

**QC Stage A:**
- R8 "completed — informative", with 9 Y genes (13 probes).
- R9 completed: 6 flagged at k = 3 (F1, retained); 0 numerical failures; 0 near-identical pairs; 0 referrals to D18.

**R8 two-axis discordant:**

| Group | Discordant (Q1) |
|---|---|
| AD | 0 |
| CTL | **1** |
| MCI | 0 |

Ambiguous arrays (F3, retained): AD 23, CTL 18, MCI 17, R5-labelled 0.

**Stage B: rule-applied exclusion list (awaiting PI approval)**

| Tier | n | Contents |
|---|---|---|
| P1 | 115 | 109 MCI + 6 R5 |
| Q1 | 1 | 1 control |
| P2, P3 | 0 | — |

**Proposed primary population: 139 AD vs 133 CTL.**

## Comparison with GSE63060 (descriptive)

| Cohort | Two-axis sex mismatches | Of which controls |
|---|---|---|
| GSE63060 | 44 | 44 |
| GSE63061 | 1 | 1 |

Both use the same R8 procedure and the same platform family. This strengthens the reading that the GSE63060 finding is a
**dataset-specific annotation problem among GSE63060 controls**, not a failure of R8. It is relevant to the D9 data-owner query.
