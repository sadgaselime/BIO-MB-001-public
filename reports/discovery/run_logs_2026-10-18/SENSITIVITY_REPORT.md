# GSE63060 discovery sensitivity analyses (D16), run 2026-10-18 UTC

**Authorization:** D16 approved 2026-10-18 (S1–S16 with the v7 §5.3 sample sets, plus S-R8m; v7:619).

These analyses are prespecified and all are reported. None replaces the primary analysis, none locks a signature, and they are provisional because the SAP is not approved.

## Code and tests

- **Runner:** `scripts/discovery_sensitivity_gse63060.py`.
- **Tests:** `tests/test_discovery_sensitivity.py` 7/7; full suite **310/310** under the audit hook, with no guarded opens.

## Run

| Item | Value |
|---|---|
| Time (UTC) | 2026-10-18T19:40:30Z to 2026-10-18T20:04:27Z |
| Result | exit=0 |
| Output | `reports/discovery/GSE63060/sensitivity_v1` (accepted; executed code tracked; two runs byte-identical) |

Every design passed the v5 §4.4 identifiability check with the D7 values; no analysis gave STOP.

## Results

All results are gene level (G3 unless stated), compared with the primary gene-level fit: 1,401 genes at q < 0.05.

| Analysis | AD / CTL | q < 0.05 (up / down) | Spearman t vs primary | Primary hits with same sign | … and q < 0.05 |
|---|---|---|---|---|---|
| S1a: age ≥ 65 | 135 / 56 | 630 (235 / 395) | 0.956 | 1401 | 627 |
| S1b: age 61–88 | 141 / 57 | 910 (381 / 529) | 0.977 | 1401 | 896 |
| S3a: site added | 145 / 60 | 1662 (846 / 816) | 0.979 | 1401 | 1337 |
| S3b: site instead of chip | 145 / 60 | 1238 (595 / 643) | 0.938 | 1401 | 1083 |
| S4: exclude 37 M-coded AD | 108 / 60 | 1055 (494 / 561) | 0.961 | 1401 | 995 |
| S5a: exclude F1 (k = 3) | 143 / 60 | 1543 (749 / 794) | 0.999 | 1401 | 1398 |
| S5d: exclude F2 | equals the primary (no F2 arrays) | — | — | — | — |
| S5e: exclude F3 | 123 / 56 | 1266 (603 / 663) | 0.966 | 1401 | 1158 |
| S5f: re-include Q1-only arrays | 145 / 104 | 2909 (1552 / 1357) | 0.897 | 1401 | 1365 |
| S5g: exclude F1, F2, F3 | 121 / 56 | 1363 (658 / 705) | 0.966 | 1401 | 1208 |
| S7: mean filter at the 25th percentile | 145 / 60 | 1483 (716 / 767) | 0.992 | 1392 | 1389 |
| S7: mean filter at the 50th percentile | 145 / 60 | 1585 (791 / 794) | 0.988 | 1361 | 1349 |
| S8: G1 gene unit | 145 / 60 | 1422 (674 / 748) | 0.961 | 1399 | 1301 |
| S12: Sood-flagged subset | 49 / 37 | 615 (188 / 427) | 0.737 | 1397 | 545 |
| S16: re-include D-3 / D-4 | equals the primary (no D-3 / D-4 arrays) | — | — | — | — |
| S-R8m: remove the 46 corroborated sex mismatches | 145 / 58 | 1607 (771 / 836) | 0.991 | 1401 | 1378 |

In the S7 rows, the "same sign" count covers only primary genes that still have probes after filtering.

**Not run (reasons recorded in `sensitivity_summary.json`):**

| Analysis | Reason |
|---|---|
| S2 | Spline basis not specified |
| S5b, S5c | k values not approved |
| S6 | Array weights: runner support and basis invariance unverified |
| S9 | Resource not available |
| S10 | Not approved |
| S11 | D21 not approved |
| S13–S15 | Other cohorts |

## Reading (descriptive; no new claims)

- **Direction is preserved.** In every analysis, the direction of essentially all 1,401 primary genes stays the same: 1,361–1,401 same-sign, where the S7 filter removed a few genes.
- **Rank agreement is high.** Rank correlations with the primary are 0.90–0.999, except the much smaller S12 subset (0.74).
- **Significance counts follow sample size**, which is expected: S1a, S12 and S4 have fewer arrays.
- **Re-including the 44 sex-mismatched controls (S5f)** roughly doubles the significant count with a correlation of 0.90 to the primary. It is consistent with those arrays being genuine controls with misattached sex metadata. It does not establish that.

## Output hashes

See `reports/discovery/GSE63060/sensitivity_v1/manifest.json` (`output_sha256` and `determinism.output_sha256`).
