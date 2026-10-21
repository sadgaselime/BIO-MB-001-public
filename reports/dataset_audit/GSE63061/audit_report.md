# Dataset audit: GSE63061
**Overall audit status: `COMPLETE_REVIEW_REQUIRED`** — 5 issue(s) require review
> Evidence labels: **VERIFIED** (directly established from retrieved records/files), **REPORTED** (stated elsewhere, not reproduced), **UNRESOLVED** (insufficient evidence), **FAILED** (attempted, failed). There is no PASS status; Phase 1 performs no differential expression, feature selection, enrichment or modelling.
## 1. Accession and provisional role
- Accession: [GSE63061](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE63061)
- Provisional role: `related_cohort_consistency_candidate` — Related-cohort consistency / replication candidate (AddNeuroMed batch 2). NOT an independent external validation cohort.
- Analysis tier: `secondary_candidate`
- Related accessions (config): GSE63060, GSE63063
- Participant independence: **UNRESOLVED** — Same AddNeuroMed SuperSeries as GSE63060; possible participant overlap.
- GEO title: Alzheimer, Mild Cognitive impairment and control samples from AddneuroMed Cohort (batch 2)
- GEO series type: Expression profiling by array
- GEO relations: SubSeries of: GSE63063; BioProject: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA266530
- GEO last update: May 30 2024
## 2. Retrieval status
| metadata resource | status | bytes | sha256 | retrieved (UTC) |
|---|---|---|---|---|
| GSE63061_series_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 14214 | be727cae86a54516c97c02419cdfc9afdc8905dcb80496d599376b79e67a7a31 | 2026-10-09T14:08:09+00:00 |
| GSE63061_samples_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 692754 | 44a5941ee162606637994963e76ee3dcc9cc77f1a9eb53743e6fff5cbcc103a6 | 2026-10-09T14:08:09+00:00 |
| GPL10558_platform_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 3690658 | 52a808fe0f2a92a7581ab957551c79d887fda8a067f1b9c4c9ad6a55bdc0a3b0 | 2026-10-09T14:08:09+00:00 |

| file | requested | status | size | sha256 (prefix) | notes |
|---|---|---|---|---|---|
| GSE63061_series_matrix.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 63.7 MB | c6de1af5bd36bca3… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE63061_normalized.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 63.5 MB | 724407efd592bf35… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE63061_non-normalized.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 31.3 MB | a63663ed42b32ab5… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE63061_RAW.tar | True | REUSED_VERIFIED_AGAINST_MANIFEST | 27.4 MB | 19dbc61b4da9ac80… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| filelist.txt | True | REUSED_VERIFIED_AGAINST_MANIFEST | 260 B | 08f49ebd32f02ed5… | existing file re-used: checksum matches earlier manifest record (server not consulted) |

Network used in this run: **False** (offline mode: True).
## 3. Available files (GEO listing)
_GEO directory listing not retrieved in this run (offline or failed)._
## 4. Observed sample counts
- **VERIFIED** — GEO series lists 388 samples and all 388 sample records were retrieved
- **VERIFIED** — observed 388 GEO sample records; group counts match the reference values (all compared groups match)

| group | reported | observed | difference | status |
|---|---|---|---|---|
| TOTAL | 388 | 388 | 0 | MATCHES_REPORTED |
| AD |  | 139 |  | NO_REFERENCE_COUNT |
| AMBIGUOUS |  | 6 |  | NO_REFERENCE_COUNT |
| HC |  | 134 |  | NO_REFERENCE_COUNT |
| MCI |  | 109 |  | NO_REFERENCE_COUNT |

Reference counts source: GEO series record as reported in the BIO-MB-001 brief (REPORTED; used for comparison only, never enforced).
## 5. Observed diagnostic groups
Diagnosis field: `char:status`

| raw GEO label | n |
|---|---|
| AD | 139 |
| CTL | 134 |
| CTL to AD | 1 |
| MCI | 109 |
| MCI to CTL | 1 |
| OTHER | 1 |
| borderline MCI | 3 |

Canonical mapping (from config label_map; unmapped labels are flagged, not guessed):

| group | n |
|---|---|
| AD | 139 |
| AMBIGUOUS | 6 |
| HC | 134 |
| MCI | 109 |

Potential covariates (non-missing records out of total):

| field | n_present | n_missing | n_distinct |
|---|---|---|---|
| char:age | 388 | 0 | 38 |
| char:gender | 388 | 0 | 2 |
| char:ethnicity | 388 | 0 | 18 |
| char:included in case -control study | 388 | 0 | 2 |

Participant-ID field `description`: 388 present, 388 distinct, 0 duplicated ID(s) covering 0 records.
## 6. Sample reconciliation
### GSE63061_series_matrix.txt.gz (key: expression column/sample ID == GEO geo_accession)
- expression IDs: 388; phenotype records: 388; exact matches: 388
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'AD': 139, 'AMBIGUOUS': 6, 'HC': 134, 'MCI': 109}
- full ID listing: `reports/dataset_audit/GSE63061/GSE63061_series_matrix_txt_gz_id_reconciliation.csv`
### GSE63061_normalized.txt.gz (key: expression column/sample ID == GEO title)
- expression IDs: 388; phenotype records: 388; exact matches: 388
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'AD': 139, 'AMBIGUOUS': 6, 'HC': 134, 'MCI': 109}
- full ID listing: `reports/dataset_audit/GSE63061/GSE63061_normalized_txt_gz_id_reconciliation.csv`
### GSE63061_non-normalized.txt.gz (key: expression column/sample ID == GEO title)
- expression IDs: 388; phenotype records: 388; exact matches: 388
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'AD': 139, 'AMBIGUOUS': 6, 'HC': 134, 'MCI': 109}
- full ID listing: `reports/dataset_audit/GSE63061/GSE63061_non-normalized_txt_gz_id_reconciliation.csv`

### Cross-file value concordance (read-only)
| file_a | file_b | status | n_shared_features | n_shared_samples | fraction_identical | max_abs_difference | pearson_r |
|---|---|---|---|---|---|---|---|
| GSE63061_series_matrix.txt.gz | GSE63061_normalized.txt.gz | IDENTICAL_VALUES | 2000 | 388 | 1.0 | 0.0 | 1.0 |
| GSE63061_series_matrix.txt.gz | GSE63061_non-normalized.txt.gz | DIFFERENT_VALUES | 2000 | 388 | 0.0 | 21966.49433731 | 0.6835015224789338 |

Reported leads:

_none_

Proposed exclusion candidates (NOT applied): 6 — see `reports/dataset_audit/GSE63061/proposed_exclusions.csv`
## 7. Processing-state assessment
| file | state | confidence | review | filename_hint | basis |
|---|---|---|---|---|---|
| GSE63061_series_matrix.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True |  | values on a log-like scale (min 3.93, max 14.8): a transformation has been applied; GSM data_processing mentions processing software/transform: 'Using LUMI package in R' (method details not stated) |
| GSE63061_normalized.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True | PROCESSED_NORMALIZED | values on a log-like scale (min 3.93, max 14.8): a transformation has been applied |
| GSE63061_non-normalized.txt.gz | NON_NORMALIZED | MEDIUM | True | NON_NORMALIZED | linear-scale intensities (min 54.3, max 2.47e+04, 0.00% negative); per-sample distributions differ (max SD/IQR 0.916 at q25-q75): no between-sample distribution normalisation evident |
| GSE63061_RAW.tar | METADATA_ONLY | HIGH | True | RAW_INSTRUMENT | archive contains only platform annotation/manifest files: ['GPL10558_HumanHT-12_V4_0_R1_15002873_B.txt.gz', 'GPL10558_HumanHT-12_V4_0_R2_15002873_B.txt.gz'] |
| filelist.txt | METADATA_ONLY | HIGH | False | METADATA_ONLY | table kind 'file_manifest' contains no expression values |

Phase 1 does not normalise or transform any data.
## 8. Platform and modality
- Configured modality: `expression_microarray` (Illumina BeadArray)
- Configured platform: GPL10558 — Illumina HumanHT-12 V4.0 expression beadchip
- Observed platform: **GPL10558** — Illumina HumanHT-12 V4.0 expression beadchip (technology: oligonucleotide beads; distribution: commercial)
- **VERIFIED** — configured platform GPL10558; GEO series platform(s): ['GPL10558']
- **VERIFIED** — GPL10558: Illumina HumanHT-12 V4.0 expression beadchip (oligonucleotide beads)
- **VERIFIED** — GEO series type: ['Expression profiling by array']; configured modality: expression_microarray
## 9. Issues and limitations
| severity | category | description |
|---|---|---|
| medium | phenotype | 6 sample(s) with ambiguous diagnosis label: {'borderline MCI': 3, 'OTHER': 1, 'CTL to AD': 1, 'MCI to CTL': 1} |
| medium | processing | GSE63061_series_matrix.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review |
| medium | processing | GSE63061_normalized.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review |
| medium | processing | GSE63061_non-normalized.txt.gz: processing state NON_NORMALIZED (confidence MEDIUM) requires review |
| medium | processing | GSE63061_RAW.tar: processing state METADATA_ONLY (confidence HIGH) requires review; content-based state METADATA_ONLY contradicts the file-name hint RAW_INSTRUMENT |

### All findings
| status | topic | statement | evidence |
|---|---|---|---|
| VERIFIED | sample_count | GEO series lists 388 samples and all 388 sample records were retrieved | series record !Series_sample_id vs retrieved GSM records |
| VERIFIED | platform | configured platform GPL10558; GEO series platform(s): ['GPL10558'] | GEO series record |
| VERIFIED | platform | GPL10558: Illumina HumanHT-12 V4.0 expression beadchip (oligonucleotide beads) | GEO platform record |
| VERIFIED | modality | GEO series type: ['Expression profiling by array']; configured modality: expression_microarray | GEO series record |
| VERIFIED | relations | GEO relation: SubSeries of: GSE63063 | GEO series record |
| UNRESOLVED | independence | participant independence status: UNRESOLVED. Same AddNeuroMed SuperSeries as GSE63060; possible participant overlap. | configuration (not established from data) |
| VERIFIED | diagnosis_labels | 6 sample(s) with ambiguous diagnosis label: {'borderline MCI': 3, 'OTHER': 1, 'CTL to AD': 1, 'MCI to CTL': 1} | GEO characteristics field char:status |
| VERIFIED | diagnosis_labels | every sample has a diagnosis label in char:status that is mapped or explicitly flagged | GEO sample characteristics |
| VERIFIED | sample_count | observed 388 GEO sample records; group counts match the reference values (all compared groups match) | GEO sample records vs config expected_counts |
| VERIFIED | retrieval | GSE63061_series_matrix.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 63713724 bytes, SHA-256 c6de1af5bd36bca3de0921d53051bdefd05666f6e94a6906a26c8cb461dd55f5 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63061/matrix/GSE63061_series_matrix.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE63061_normalized.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 63549302 bytes, SHA-256 724407efd592bf355309d72ce1d3bed165ddf2180e553cc425aaf8c90db8ba2d | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63061/suppl/GSE63061_normalized.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE63061_non-normalized.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 31288958 bytes, SHA-256 a63663ed42b32ab59e8045ef94e6c739dfeddf9bd3aff90a4308c30bfde25e47 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63061/suppl/GSE63061_non-normalized.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE63061_RAW.tar: REUSED_VERIFIED_AGAINST_MANIFEST, 27443200 bytes, SHA-256 19dbc61b4da9ac807799a96081f4eae405079dad108b82a9d2bdb74678cdb948 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63061/suppl/GSE63061_RAW.tar; integrity: tar_member_listing |
| VERIFIED | retrieval | filelist.txt: REUSED_VERIFIED_AGAINST_MANIFEST, 260 bytes, SHA-256 08f49ebd32f02ed5e0d7ed6da0a1e161cced6286174d5597fecd240d8d13c54c | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63061/suppl/filelist.txt; integrity: none_applicable |
| VERIFIED | inspection | GSE63061_series_matrix.txt.gz: geo_series_matrix (gzip), kind=expression_matrix, rows=32049, columns=389, candidate samples=388 | streamed file inspection |
| UNRESOLVED | processing | GSE63061_series_matrix.txt.gz: PROCESSED_NORMALIZED (confidence MEDIUM) | values on a log-like scale (min 3.93, max 14.8): a transformation has been applied; GSM data_processing mentions processing software/transform: 'Using LUMI package in R' (method details not stated) |
| VERIFIED | inspection | GSE63061_normalized.txt.gz: delimited_text (gzip), kind=expression_matrix, rows=32051, columns=389, candidate samples=388 | streamed file inspection |
| UNRESOLVED | processing | GSE63061_normalized.txt.gz: PROCESSED_NORMALIZED (confidence MEDIUM) | values on a log-like scale (min 3.93, max 14.8): a transformation has been applied |
| VERIFIED | inspection | GSE63061_non-normalized.txt.gz: delimited_text (gzip), kind=expression_matrix, rows=47323, columns=389, candidate samples=388 | streamed file inspection |
| UNRESOLVED | processing | GSE63061_non-normalized.txt.gz: NON_NORMALIZED (confidence MEDIUM) | linear-scale intensities (min 54.3, max 2.47e+04, 0.00% negative); per-sample distributions differ (max SD/IQR 0.916 at q25-q75): no between-sample distribution normalisation evident |
| VERIFIED | inspection | GSE63061_RAW.tar: tar_archive (none), kind=archive, rows=2, columns=None, candidate samples=0 | streamed file inspection |
| VERIFIED | processing | GSE63061_RAW.tar: METADATA_ONLY (confidence HIGH) | archive contains only platform annotation/manifest files: ['GPL10558_HumanHT-12_V4_0_R1_15002873_B.txt.gz', 'GPL10558_HumanHT-12_V4_0_R2_15002873_B.txt.gz'] |
| VERIFIED | inspection | filelist.txt: geo_filelist (none), kind=file_manifest, rows=3, columns=5, candidate samples=0 | streamed file inspection |
| VERIFIED | processing | filelist.txt: METADATA_ONLY (confidence HIGH) | table kind 'file_manifest' contains no expression values |
| VERIFIED | reconciliation | GSE63061_series_matrix.txt.gz: 388 expression IDs vs 388 phenotype records; 388 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO geo_accession |
| VERIFIED | reconciliation | GSE63061_normalized.txt.gz: 388 expression IDs vs 388 phenotype records; 388 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO title |
| VERIFIED | reconciliation | GSE63061_non-normalized.txt.gz: 388 expression IDs vs 388 phenotype records; 388 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO title |
| VERIFIED | processing | series matrix vs GSE63061_normalized.txt.gz: IDENTICAL_VALUES (2000 features x 388 samples compared; fraction identical 1.0) | read-only value comparison on the first features |
| VERIFIED | processing | series matrix vs GSE63061_non-normalized.txt.gz: DIFFERENT_VALUES (2000 features x 388 samples compared; fraction identical 0.0) | read-only value comparison on the first features |
## 10. Recommended next actions
1. Verify participant-level independence/overlap with related cohorts from study documentation or the data owners; a different GEO accession does not establish independence.
2. Decide (in a prespecified analysis plan) how ambiguous/transition diagnosis labels are handled; they are kept separate and nothing has been excluded.
3. Choose the downstream input file for this dataset only after reviewing the processing evidence: GSE63061_series_matrix.txt.gz = PROCESSED_NORMALIZED (MEDIUM); GSE63061_normalized.txt.gz = PROCESSED_NORMALIZED (MEDIUM); GSE63061_non-normalized.txt.gz = NON_NORMALIZED (MEDIUM). Do not apply normalisation to data that is already normalised.
## 11. Run information
- Run ID: `20261009T140756Z-e178f3`
- Audit started/finished (UTC): 2026-10-09T14:08:09+00:00 / 2026-10-09T14:08:20+00:00
- Software: biomarker_project 0.1.0, Python 3.13.9, pandas 3.0.6, numpy 2.5.3, requests 2.34.2, PyYAML 6.0.3
- Config SHA-256: `c1438e0f29cc22fa51679dcaf7999ff599c01d97e4c77b656e244ebce8eb0d48`
- Command: `scripts/run_all_audits.py --offline`
