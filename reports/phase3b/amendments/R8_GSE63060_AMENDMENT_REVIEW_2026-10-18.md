# R8 (sex consistency) on GSE63060: amendment review, 2026-10-18

**Status:** PROPOSAL FOR PI DECISION. NOT APPROVED. This is a noncanonical document.
- No SAP rule, QC code, candidate or exclusion has been changed.
- Nothing has been applied.
- **Post hoc:** R8 outputs for GSE63060 were already visible when this review was made (QC Stage A v1). Any amendment must say so (v6 §2.2).
- **Requested by the PI 2026-10-18:** "Review R8 as an amendment".

## Evidence

All of it is diagnosis-blind, produced under the code-identity lifecycle, and accepted with executed code verified.

| Item | Location | Notes |
|---|---|---|
| QC Stage A v1 | `reports/qc_stage_a/GSE63060/v1/` | R8 as approved: 246 concordant on two axes, 39 ambiguous, 44 discordant on two axes (Q1 candidates, not applied) |
| Diagnostics v1 | `reports/qc_stage_a/GSE63060/r8_diagnostics/v1/` | Per-probe level, separation and split, for deposited (D3) values and log2 raw values |
| Diagnostics v2 | `reports/qc_stage_a/GSE63060/r8_diagnostics/v2/` | v1 plus calls for the strongest markers and their agreement |

Diagnostics v2 file hashes (prefixes): `r8_marker_agreement.json` `a24d36ea…`, `r8_marker_calls_series_matrix.tsv` `6983c3bd…`, `r8_probe_diagnostics.tsv` `13f3581f…`, `manifest.json` `376ab21e…`.

**Ad hoc check** (metadata only, written to no file): the 46 mismatched arrays are spread across 23 of 29 chips, with 1 to 5 per chip.

## Findings

### F1. Several R8 probes carry little or no sex signal on GPL6947

The table shows AUC for recorded sex on the deposited scale. The raw scale agrees.

| Probe(s) | Gene | AUC | Expected-direction difference | Notes |
|---|---|---|---|---|
| ILMN_1732039 | DDX3Y | 0.56 | 0.01 | Essentially no signal |
| ILMN_2056795 | USP9Y | 0.64 | 0.03 | Essentially no signal |
| ILMN_1804958, ILMN_2090059 | ZFY | 0.56, 0.70 | 0.01, 0.06 | Essentially no signal |
| ILMN_1764573 | XIST | 0.80 | 0.60 (deposited); 0.83 (raw) | Weak |
| ILMN_1783142 | RPS4Y1 | 0.82 | 2.76 | Own split: d = 17.9, low class 200 |
| ILMN_1685690 | KDM5D | 0.85 | 0.82 | Own split: d = 8.3 |

R8's Y axis is the median of all 13 centred Y probes, so the dead probes dilute it. The weak XIST probe disagrees with the Y markers on about 28 arrays (mostly recorded-female arrays called male by XIST alone). This inflates R8's **ambiguous** category: 37 of its 39 ambiguous arrays are not flagged by the strong Y markers.

### F2. The 44 discordant calls are corroborated by independent markers

| Measure | Result |
|---|---|
| RPS4Y1 and KDM5D (own splits) agree | 328 / 329 arrays |
| Both strong Y markers disagree with recorded sex | **46** arrays: **23 recorded F and 23 recorded M** |
| XIST agrees with the Y markers on those 46 | 45 / 46 |
| R8's 44 discordant arrays inside these 46 | all 44 (the other 2 are R8 "ambiguous") |
| Raw (non-normalized) scale | RPS4Y1 gives the same count (46) |

Earlier, I suggested the R8 result might be a measurement artifact. **That interpretation is not supported for the discordant arrays.** Three independent sex markers agree that about 46 arrays (14%) do not match their recorded sex.

### F3. The pattern suggests a sample-label integrity problem, not only a sex-QC issue

The mismatches are exactly balanced (23/23) and spread across 23 of 29 chips. That is consistent with sample metadata (including sex) being attached to the wrong arrays for part of the series; it is also consistent with errors in the recorded sex itself. The data cannot tell these apart.

If labels were misattached, the **diagnosis labels of those arrays may be wrong too**. GSE63060 is the discovery cohort, so this bears on the primary analysis, not just on QC. It is NOT established. It is a hypothesis that warrants a data-owner query (D9) and sensitivity handling.

## Options for the PI

| Option | What changes | Effect on the 46 | Cost and risk |
|---|---|---|---|
| **R0. No amendment to R8.** Record F1–F3 as corroboration | Nothing in the rules | 44 stay Q1 candidates and 2 stay ambiguous (retained), until the exclusion-list approval step and D16 | Ambiguous stays inflated (39); no protocol amendment needed |
| **R1. Amend the R8 probe set by a label-free criterion.** For example, a Y probe enters the Y axis only if its own R8 split is well separated (descriptive d ≥ 5; here only RPS4Y1 and KDM5D). XIST is kept | Y axis definition (Tier A change: documented amendment, post hoc) | About 45 two-axis discordant (Q1). Ambiguous becomes about 28 (driven by XIST), including the 1 mismatched array where XIST disagrees | The criterion is chosen after seeing the data, though it does not use recorded sex. The d ≥ 5 cut-off is a new convention with no source |
| **R2. Amend R8 to drop XIST.** The Y axis is restricted as in R1 | X axis removed: a single-axis R8 | The 46 become **single-axis discordant: Tier F2, RETAINED** in the primary analysis under approved D22 row 2 | This changes the 46 from excluded to retained. It weakens the safeguard exactly where the corroboration is strongest. **Not recommended** |
| **R3. Treat it as an identity problem** (with R0 or R1) | Adds: a D9 data-owner query on GSE63060 sample/label assignment; a planned sensitivity analysis that excludes all 46 corroborated mismatches (D16) | The primary analysis keeps the R8/Q1 handling; the sensitivity analysis removes all 46 | Needs D9 and D16 decisions. The query may not be answered |

## Recommendation

**R0 + R3.**
- Keep R8 as approved: its discordant calls are corroborated, and an amendment would be post hoc.
- Record F1–F3 as part of the QC record.
- Open a D9 data-owner query about sample/label assignment in GSE63060.
- Plan a sensitivity analysis excluding all 46 corroborated mismatches when D16 is decided.

R1 is defensible if the inflated ambiguous category is judged a problem worth amending. Note, though, that ambiguous arrays are retained (D22 row 3), so R1 would mainly change labels and counts, not the primary population. R2 is not recommended.

## What remains true under any option

- Nothing is applied until the exclusion-list approval step and D16 are decided.
- No diagnosis label was used in this review.
- The 46 GSMs are listed in `r8_marker_calls_series_matrix.tsv` (column `both_y_markers_disagree_with_recorded`).
