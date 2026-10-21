# C15 — cohort probe presence (v1)

**Metadata only. Decision support for the D6 Illumina package; nothing here approves a route, rule, release or pin.**
Only Series Matrix probe identifiers were read; expression values were not parsed, stored or analysed.
Option A tables are PROVISIONAL (illumina_option_a/v1) or D6-F (GPL570). The accession route was regenerated
with the route-comparison v3 logic and reproduced v3 exactly (checks below). GSE140829 is out of scope (D19).

## Presence by cohort

| Measure | GSE63060 (illuminaHumanv3) | GSE63061 (illuminaHumanv4) | GSE99039 (GPL570) |
|---|---|---|---|
| series_matrix_probe_ids | 38,323 | 32,049 | 54,675 |
| series_matrix_ids_not_in_annotation_table | 0 | 0 | 0 |
| annotation_table_probe_ids | 49,576 | 48,107 | 54,675 |
| annotation_table_ids_not_in_series_matrix | 11,253 | 16,058 | 0 |
| present_option_a_class:discontinued_no_replacement | 40 | 61 | — |
| present_option_a_class:eligible_direct | 25,305 | 24,031 | 43,086 |
| present_option_a_class:eligible_via_history_replacement | 45 | 41 | 25 |
| present_option_a_class:multiple_mappings_excluded | 911 | 1,151 | 1,562 |
| present_option_a_class:no_assignment_in_package | 12,022 | 6,765 | 9,964 |
| present_option_a_eligible_probes | 25,350 | 24,072 | 43,111 |
| present_option_a_distinct_genes | 17,435 | 16,205 | 20,820 |
| present_accession_class:accession_unmatched | 962 | 1,286 | — |
| present_accession_class:ambiguous | 897 | 1,123 | — |
| present_accession_class:no_accession | 11,228 | 5,685 | — |
| present_accession_class:unique | 25,236 | 23,955 | — |
| present_accession_unique_probes | 25,236 | 23,955 | — |
| present_accession_distinct_genes | 17,345 | 16,109 | — |
| present_route:both_concordant | 25,206 | 23,906 | — |
| present_route:both_discordant | 9 | 15 | — |
| platform_route:both_discordant | 10 | 16 | — |
| present_route:option_a_only | 135 | 151 | — |
| present_route:accession_only | 21 | 34 | — |
| present_route:neither | 12,952 | 7,943 | — |
| present_genes_both_routes | 17,331 | 16,090 | — |
| present_genes_option_a_only | 104 | 115 | — |
| present_genes_accession_only | 14 | 19 | — |
| d5_r8_probes_listed | 14 | 14 | — |
| d5_r8_probes_present | 14 | 14 | — |
| present_option_a_class:no_eligible_assignment_discontinued | — | — | 38 |
| present_option_a_not_eligible_probes | — | — | 11,564 |

Route categories (Illumina, probes present in the Series Matrix): both_concordant = both routes assign the same
single gene; both_discordant = both assign one gene, different genes; option_a_only = Option A eligible, accession
route not unique; accession_only = accession unique, Option A not eligible; neither = no single-gene assignment.
`platform_route:both_discordant` is the platform-wide count from decision-matrix v2, for comparison.

## What this does and does not establish

- **Establishes:** which annotated probes are deposited in each cohort's Series Matrix, per route category.
- **Does not establish:** which route to adopt; biological validity or accuracy of any mapping; whether a probe is
  detectably expressed; gene-level reliability; anything for GSE140829; whether gene history may be used for Illumina.
- Platform-wide coverage figures elsewhere are not cohort coverage; these counts are.

## Verification

- [PASS] illuminaHumanv3: regenerated accession classes equal route-comparison v3 ({'accession_unmatched': 1379, 'ambiguous': 1152, 'no_accession': 17719, 'unique': 29326})
- [PASS] illuminaHumanv3: both-assign count equals v3 (29294)
- [PASS] illuminaHumanv3: discordant count equals v3 (10)
- [PASS] illuminaHumanv3: reconciliation probe set equals v3 (50 probes)
- [PASS] GSE63060: Series Matrix table opened and closed
- [PASS] GSE63060: Series Matrix platform is GPL6947
- [PASS] GSE63060: no duplicate probe IDs
- [PASS] GSE63060: no empty probe IDs
- [PASS] GSE63060: probe IDs = dataset-audit inspection count
- [PASS] GSE63060: annotation table probe IDs unique
- [PASS] GSE63060: present route categories + absent-from-table sum to Series Matrix IDs
- [PASS] GSE63060: present Option A classes sum to Series Matrix IDs
- [PASS] illuminaHumanv4: regenerated accession classes equal route-comparison v3 ({'accession_unmatched': 2390, 'ambiguous': 1680, 'no_accession': 10226, 'unique': 33811})
- [PASS] illuminaHumanv4: both-assign count equals v3 (33761)
- [PASS] illuminaHumanv4: discordant count equals v3 (16)
- [PASS] illuminaHumanv4: reconciliation probe set equals v3 (64 probes)
- [PASS] GSE63061: Series Matrix table opened and closed
- [PASS] GSE63061: Series Matrix platform is GPL10558
- [PASS] GSE63061: no duplicate probe IDs
- [PASS] GSE63061: no empty probe IDs
- [PASS] GSE63061: probe IDs = dataset-audit inspection count
- [PASS] GSE63061: annotation table probe IDs unique
- [PASS] GSE63061: present route categories + absent-from-table sum to Series Matrix IDs
- [PASS] GSE63061: present Option A classes sum to Series Matrix IDs
- [PASS] GSE99039: Series Matrix table opened and closed
- [PASS] GSE99039: Series Matrix platform is GPL570
- [PASS] GSE99039: no duplicate probe IDs
- [PASS] GSE99039: no empty probe IDs
- [PASS] GSE99039: probe IDs = dataset-audit inspection count
- [PASS] GSE99039: annotation table probe IDs unique
- [PASS] GSE99039: present Option A classes sum to Series Matrix IDs

## Inputs (SHA-256)

- `GSE63060`: `342421d07105d786d623a4b86dc4a21b764da352e4facc7a032fbd36b0f19371`
- `GSE63061`: `c6de1af5bd36bca3de0921d53051bdefd05666f6e94a6906a26c8cb461dd55f5`
- `GSE99039`: `197b7272a8a5040c2843cbefd44f8bd43e9b7820562732d5b1ffd30841bfcb50`
- `reference/bioconductor_3.23/illuminaHumanv3.db_1.26.0.tar.gz`: `cea0c9cd155197154d57400cb3f18108e451cf26e714c39698d68e45cd503a1b`
- `reference/bioconductor_3.23/illuminaHumanv4.db_1.26.0.tar.gz`: `362848d6e78c7fa6206e1a4c68a4b68c1ea065267d550114837bc3b9d833ee85`
- `reference/bioconductor_3.23/org.Hs.eg.db_3.23.1.tar.gz`: `470620665cf49d0319422731164f377e3e74253989f1d33a8a1d100cc3d49cfe`
- `reports/annotation_audit/illumina_option_a/v1/illuminaHumanv3_probe_classification_PROVISIONAL.tsv`: `8214b0078512282701525617f81872ce189004df663079e96157cda8fe279de4`
- `reports/annotation_audit/illumina_option_a/v1/illuminaHumanv4_probe_classification_PROVISIONAL.tsv`: `fc73bebe9b614759cced5dcf553084e87091e2959a41866eff277b0916175153`
- `reports/annotation_audit/illumina_option_a/v1/lumi_HT12_v4_R2_probe_classification_PROVISIONAL.tsv`: `cd8edfd1016c1bf8f45a70a18cfda4c649c8b3e75fe55b9f23a3f138132fd739`
- `reports/annotation_audit/gpl570_option_a/v1/probe_set_classification.tsv`: `9e5f23fa8b10b3e120b518873905b79e5f338ca07ec83357e173d3a2ddea8d9c`
- `reports/annotation_audit/illumina_route_comparison/v3/route_comparison_metrics.tsv`: `d693ab9d653e37a6307e1ddf91433504bedb1589c3ade3f00f39bc6209dacc4e`
- `reports/annotation_audit/illumina_route_comparison/v3/metric_reconciliation_probes.tsv`: `d345ff888498ebce676af7de0941bf5512bfa12e73a31b00f55d3f14b1f3f3b0`
