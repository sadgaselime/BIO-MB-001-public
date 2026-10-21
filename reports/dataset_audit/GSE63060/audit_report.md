# Dataset audit: GSE63060
**Overall audit status: `COMPLETE_REVIEW_REQUIRED`** — 9 issue(s) require review
> Evidence labels: **VERIFIED** (directly established from retrieved records/files), **REPORTED** (stated elsewhere, not reproduced), **UNRESOLVED** (insufficient evidence), **FAILED** (attempted, failed). There is no PASS status; Phase 1 performs no differential expression, feature selection, enrichment or modelling.
## 1. Accession and provisional role
- Accession: [GSE63060](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE63060)
- Provisional role: `provisional_primary_ad_discovery` — Provisional primary AD discovery cohort (AddNeuroMed batch 1).
- Analysis tier: `primary_candidate`
- Related accessions (config): GSE63061, GSE63063
- Participant independence: **UNRESOLVED** — Same AddNeuroMed SuperSeries (GSE63063) as GSE63061. Participant overlap with GSE63061 has not been excluded.
- GEO title: Alzheimer, MCI and control samples from AddneuroMed Cohort (batch 1)
- GEO series type: Expression profiling by array
- GEO relations: SubSeries of: GSE63063; BioProject: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA266531
- GEO last update: May 30 2024
## 2. Retrieval status
| metadata resource | status | bytes | sha256 | retrieved (UTC) |
|---|---|---|---|---|
| GSE63060_series_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 12303 | a50ab13646b2b147ea2e577f9b7bb6abd41e94232efec2ccfc6f90b33bcea0cb | 2026-10-09T14:07:56+00:00 |
| GSE63060_samples_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 586887 | 99def3c70fe6d82b85680d0224dd1e982f5d19da94e1168d910de8d9cfad5673 | 2026-10-09T14:07:56+00:00 |
| GPL6947_platform_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 893817 | 9c6312d19143f7219dec60c5805891e729cd3ea8f6849316c41dc88b5b39b546 | 2026-10-09T14:07:56+00:00 |

| file | requested | status | size | sha256 (prefix) | notes |
|---|---|---|---|---|---|
| GSE63060_series_matrix.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 62.8 MB | 342421d07105d786… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE63060_normalized.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 62.6 MB | 3a0d9f03e0e2e4b0… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE63060_non-normalized.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 64.6 MB | 163acd963f21ce51… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE63060_RAW.tar | True | REUSED_VERIFIED_AGAINST_MANIFEST | 6.5 MB | 021a8de0d4069391… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| filelist.txt | True | REUSED_VERIFIED_AGAINST_MANIFEST | 173 B | 4b55fd2c8d599327… | existing file re-used: checksum matches earlier manifest record (server not consulted) |

Network used in this run: **False** (offline mode: True).
## 3. Available files (GEO listing)
_GEO directory listing not retrieved in this run (offline or failed)._
## 4. Observed sample counts
- **VERIFIED** — GEO series lists 329 samples and all 329 sample records were retrieved
- **VERIFIED** — observed 329 GEO sample records; group counts match the reference values (all compared groups match)

| group | reported | observed | difference | status |
|---|---|---|---|---|
| TOTAL | 329 | 329 | 0 | MATCHES_REPORTED |
| AD | 145 | 145 | 0 | MATCHES_REPORTED |
| MCI | 80 | 80 | 0 | MATCHES_REPORTED |
| HC | 104 | 104 | 0 | MATCHES_REPORTED |

Reference counts source: GEO series record as reported in the BIO-MB-001 brief (REPORTED; used for comparison only, never enforced).
## 5. Observed diagnostic groups
Diagnosis field: `char:status`

| raw GEO label | n |
|---|---|
| AD | 145 |
| CTL | 104 |
| MCI | 80 |

Canonical mapping (from config label_map; unmapped labels are flagged, not guessed):

| group | n |
|---|---|
| AD | 145 |
| HC | 104 |
| MCI | 80 |

Potential covariates (non-missing records out of total):

| field | n_present | n_missing | n_distinct |
|---|---|---|---|
| char:age | 329 | 0 | 34 |
| char:gender | 329 | 0 | 2 |
| char:ethnicity | 329 | 0 | 3 |
| char:included in case -control study | 329 | 0 | 2 |

Participant-ID field `description`: 329 present, 329 distinct, 0 duplicated ID(s) covering 0 records.
## 6. Sample reconciliation
### GSE63060_series_matrix.txt.gz (key: expression column/sample ID == GEO geo_accession)
- expression IDs: 329; phenotype records: 329; exact matches: 329
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'AD': 145, 'HC': 104, 'MCI': 80}
- full ID listing: `reports/dataset_audit/GSE63060/GSE63060_series_matrix_txt_gz_id_reconciliation.csv`
### GSE63060_normalized.txt.gz (key: expression column/sample ID == GEO title)
- expression IDs: 330; phenotype records: 329; exact matches: 329
- expression-only: 1; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **False**
- group counts among matched records: {'AD': 145, 'HC': 104, 'MCI': 80}
- full ID listing: `reports/dataset_audit/GSE63060/GSE63060_normalized_txt_gz_id_reconciliation.csv`
- expression-only IDs (first 20): ['4856076038_D']
### GSE63060_non-normalized.txt.gz (key: expression column/sample ID == GEO title)
- expression IDs: 330; phenotype records: 329; exact matches: 326
- expression-only: 1; phenotype-only: 3; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 3
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **False**
- group counts among matched records: {'AD': 142, 'HC': 104, 'MCI': 80}
- full ID listing: `reports/dataset_audit/GSE63060/GSE63060_non-normalized_txt_gz_id_reconciliation.csv`
- expression-only IDs (first 20): ['4856076038_D']
- phenotype-only IDs (first 20): ['4856050008_B', '4856050008_K', '4856050048_A']

### Cross-file value concordance (read-only)
| file_a | file_b | status | n_shared_features | n_shared_samples | fraction_identical | max_abs_difference | pearson_r |
|---|---|---|---|---|---|---|---|
| GSE63060_series_matrix.txt.gz | GSE63060_normalized.txt.gz | IDENTICAL_VALUES | 2000 | 329 | 1.0 | 0.0 | 1.0 |
| GSE63060_series_matrix.txt.gz | GSE63060_non-normalized.txt.gz | DIFFERENT_VALUES | 2000 | 326 | 0.0 | 47614.21271416 | 0.7307804823570967 |

Reported leads:

| lead | status | description | check |
|---|---|---|---|
| GSE63060-LEAD-1 | REPORTED | A published analysis of this cohort reports excluding outlier samples. | UNRESOLVED: no sample IDs recorded for this lead in the configuration; add them from the publication to enable a direct check |
| GSE63060-LEAD-2 | REPORTED | A separate published report describes possible expression/phenotype sample-ID mismatches in this series. | UNRESOLVED: no sample IDs recorded for this lead in the configuration; add them from the publication to enable a direct check |

Proposed exclusion candidates (NOT applied): 5 — see `reports/dataset_audit/GSE63060/proposed_exclusions.csv`
## 7. Processing-state assessment
| file | state | confidence | review | filename_hint | basis |
|---|---|---|---|---|---|
| GSE63060_series_matrix.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True |  | values on a log-like scale (min 7.2, max 15): a transformation has been applied; GSM data_processing mentions processing software/transform: 'Using LUMI package in R' (method details not stated) |
| GSE63060_normalized.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True | PROCESSED_NORMALIZED | values on a log-like scale (min 7.2, max 15): a transformation has been applied |
| GSE63060_non-normalized.txt.gz | NON_NORMALIZED | MEDIUM | True | NON_NORMALIZED | linear-scale intensities (min 68.3, max 5.18e+04, 0.00% negative); per-sample distributions differ (max SD/IQR 0.464 at q25-q75): no between-sample distribution normalisation evident |
| GSE63060_RAW.tar | METADATA_ONLY | HIGH | True | RAW_INSTRUMENT | archive contains only platform annotation/manifest files: ['GPL6947_HumanHT-12_V3_0_R1_11283641_A.bgx.gz'] |
| filelist.txt | METADATA_ONLY | HIGH | False | METADATA_ONLY | table kind 'file_manifest' contains no expression values |

Phase 1 does not normalise or transform any data.
## 8. Platform and modality
- Configured modality: `expression_microarray` (Illumina BeadArray)
- Configured platform: GPL6947 — Illumina HumanHT-12 V3.0 expression beadchip
- Observed platform: **GPL6947** — Illumina HumanHT-12 V3.0 expression beadchip (technology: oligonucleotide beads; distribution: commercial)
- **VERIFIED** — configured platform GPL6947; GEO series platform(s): ['GPL6947']
- **VERIFIED** — GPL6947: Illumina HumanHT-12 V3.0 expression beadchip (oligonucleotide beads)
- **VERIFIED** — GEO series type: ['Expression profiling by array']; configured modality: expression_microarray
## 9. Issues and limitations
| severity | category | description |
|---|---|---|
| high | inspection | GSE63060_normalized.txt.gz: 1 row(s) shorter than the header (values absent, counted as missing): line 30881 'ILMN_2315789' (1 fields) |
| high | inspection | GSE63060_non-normalized.txt.gz: 3 data column(s) with an empty header at positions [317, 323, 329]: values present but not attributable to any sample |
| high | reconciliation | GSE63060_normalized.txt.gz: not an exact one-to-one match with GEO records (1 expression-only, 0 phenotype-only, 0 duplicated expression IDs, 0 duplicated phenotype keys, 0 records without key) |
| high | reconciliation | GSE63060_non-normalized.txt.gz: not an exact one-to-one match with GEO records (1 expression-only, 3 phenotype-only, 0 duplicated expression IDs, 0 duplicated phenotype keys, 0 records without key) |
| medium | processing | GSE63060_series_matrix.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review |
| medium | processing | GSE63060_normalized.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review |
| medium | processing | GSE63060_non-normalized.txt.gz: processing state NON_NORMALIZED (confidence MEDIUM) requires review |
| medium | processing | GSE63060_RAW.tar: processing state METADATA_ONLY (confidence HIGH) requires review; content-based state METADATA_ONLY contradicts the file-name hint RAW_INSTRUMENT |
| low | inspection | GSE63060_normalized.txt.gz: 330 missing values in 330 sample column(s) |

### All findings
| status | topic | statement | evidence |
|---|---|---|---|
| VERIFIED | sample_count | GEO series lists 329 samples and all 329 sample records were retrieved | series record !Series_sample_id vs retrieved GSM records |
| VERIFIED | platform | configured platform GPL6947; GEO series platform(s): ['GPL6947'] | GEO series record |
| VERIFIED | platform | GPL6947: Illumina HumanHT-12 V3.0 expression beadchip (oligonucleotide beads) | GEO platform record |
| VERIFIED | modality | GEO series type: ['Expression profiling by array']; configured modality: expression_microarray | GEO series record |
| VERIFIED | relations | GEO relation: SubSeries of: GSE63063 | GEO series record |
| UNRESOLVED | independence | participant independence status: UNRESOLVED. Same AddNeuroMed SuperSeries (GSE63063) as GSE63061. Participant overlap with GSE63061 has not been excluded. | configuration (not established from data) |
| VERIFIED | diagnosis_labels | every sample has a diagnosis label in char:status that is mapped or explicitly flagged | GEO sample characteristics |
| VERIFIED | sample_count | observed 329 GEO sample records; group counts match the reference values (all compared groups match) | GEO sample records vs config expected_counts |
| VERIFIED | retrieval | GSE63060_series_matrix.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 62803860 bytes, SHA-256 342421d07105d786d623a4b86dc4a21b764da352e4facc7a032fbd36b0f19371 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63060/matrix/GSE63060_series_matrix.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE63060_normalized.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 62643363 bytes, SHA-256 3a0d9f03e0e2e4b05c5a64cb218c030f17965f7a31ee06aa91514f8c210ce25a | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63060/suppl/GSE63060_normalized.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE63060_non-normalized.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 64628849 bytes, SHA-256 163acd963f21ce51495b85d4a0187bb7ae6b11904f3b1d49114bfa39494931b7 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63060/suppl/GSE63060_non-normalized.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE63060_RAW.tar: REUSED_VERIFIED_AGAINST_MANIFEST, 6543360 bytes, SHA-256 021a8de0d4069391f5a8386d18225ef4c90345c82bbcaed7f1d413ed9db09876 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63060/suppl/GSE63060_RAW.tar; integrity: tar_member_listing |
| VERIFIED | retrieval | filelist.txt: REUSED_VERIFIED_AGAINST_MANIFEST, 173 bytes, SHA-256 4b55fd2c8d59932798954853a67926f9429d227518d03b3499e3c49df2fb7538 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63060/suppl/filelist.txt; integrity: none_applicable |
| VERIFIED | inspection | GSE63060_series_matrix.txt.gz: geo_series_matrix (gzip), kind=expression_matrix, rows=38323, columns=330, candidate samples=329 | streamed file inspection |
| UNRESOLVED | processing | GSE63060_series_matrix.txt.gz: PROCESSED_NORMALIZED (confidence MEDIUM) | values on a log-like scale (min 7.2, max 15): a transformation has been applied; GSM data_processing mentions processing software/transform: 'Using LUMI package in R' (method details not stated) |
| VERIFIED | inspection | GSE63060_normalized.txt.gz: delimited_text (gzip), kind=expression_matrix, rows=38324, columns=331, candidate samples=330 | streamed file inspection |
| VERIFIED | inspection | GSE63060_normalized.txt.gz: 1 truncated row(s) in the deposited file: ['ILMN_2315789'] | field-count check of every row |
| UNRESOLVED | processing | GSE63060_normalized.txt.gz: PROCESSED_NORMALIZED (confidence MEDIUM) | values on a log-like scale (min 7.2, max 15): a transformation has been applied |
| VERIFIED | inspection | GSE63060_non-normalized.txt.gz: delimited_text (gzip), kind=expression_matrix, rows=48803, columns=331, candidate samples=328 | streamed file inspection |
| VERIFIED | inspection | GSE63060_non-normalized.txt.gz: 3 unlabelled data column(s) at positions [317, 323, 329] | header parsed verbatim |
| UNRESOLVED | processing | GSE63060_non-normalized.txt.gz: NON_NORMALIZED (confidence MEDIUM) | linear-scale intensities (min 68.3, max 5.18e+04, 0.00% negative); per-sample distributions differ (max SD/IQR 0.464 at q25-q75): no between-sample distribution normalisation evident |
| VERIFIED | inspection | GSE63060_RAW.tar: tar_archive (none), kind=archive, rows=1, columns=None, candidate samples=0 | streamed file inspection |
| VERIFIED | processing | GSE63060_RAW.tar: METADATA_ONLY (confidence HIGH) | archive contains only platform annotation/manifest files: ['GPL6947_HumanHT-12_V3_0_R1_11283641_A.bgx.gz'] |
| VERIFIED | inspection | filelist.txt: geo_filelist (none), kind=file_manifest, rows=2, columns=5, candidate samples=0 | streamed file inspection |
| VERIFIED | processing | filelist.txt: METADATA_ONLY (confidence HIGH) | table kind 'file_manifest' contains no expression values |
| VERIFIED | reconciliation | GSE63060_series_matrix.txt.gz: 329 expression IDs vs 329 phenotype records; 329 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO geo_accession |
| VERIFIED | reconciliation | GSE63060_normalized.txt.gz: 330 expression IDs vs 329 phenotype records; 329 exact matches, 1 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO title |
| VERIFIED | reconciliation | GSE63060_non-normalized.txt.gz: 330 expression IDs vs 329 phenotype records; 326 exact matches, 1 expression-only, 3 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO title |
| VERIFIED | processing | series matrix vs GSE63060_normalized.txt.gz: IDENTICAL_VALUES (2000 features x 329 samples compared; fraction identical 1.0) | read-only value comparison on the first features |
| VERIFIED | processing | series matrix vs GSE63060_non-normalized.txt.gz: DIFFERENT_VALUES (2000 features x 326 samples compared; fraction identical 0.0) | read-only value comparison on the first features |
| REPORTED | reported_lead | GSE63060-LEAD-1: A published analysis of this cohort reports excluding outlier samples. | BIO-MB-001 brief (primary citation to be added by the PI) |
| UNRESOLVED | reported_lead | GSE63060-LEAD-1: no sample IDs configured to check | config reported_leads[].sample_ids is empty |
| REPORTED | reported_lead | GSE63060-LEAD-2: A separate published report describes possible expression/phenotype sample-ID mismatches in this series. | BIO-MB-001 brief (primary citation to be added by the PI) |
| UNRESOLVED | reported_lead | GSE63060-LEAD-2: no sample IDs configured to check | config reported_leads[].sample_ids is empty |
## 10. Recommended next actions
1. Verify participant-level independence/overlap with related cohorts from study documentation or the data owners; a different GEO accession does not establish independence.
2. Review unmatched/duplicated identifiers for GSE63060_normalized.txt.gz in reports/dataset_audit/GSE63060/GSE63060_normalized_txt_gz_id_reconciliation.csv.
3. Review unmatched/duplicated identifiers for GSE63060_non-normalized.txt.gz in reports/dataset_audit/GSE63060/GSE63060_non-normalized_txt_gz_id_reconciliation.csv.
4. Add the sample IDs referenced by lead GSE63060-LEAD-1 (from the cited publication) to the configuration so they can be checked against GEO records; they will not be auto-excluded.
5. Add the sample IDs referenced by lead GSE63060-LEAD-2 (from the cited publication) to the configuration so they can be checked against GEO records; they will not be auto-excluded.
6. Choose the downstream input file for this dataset only after reviewing the processing evidence: GSE63060_series_matrix.txt.gz = PROCESSED_NORMALIZED (MEDIUM); GSE63060_normalized.txt.gz = PROCESSED_NORMALIZED (MEDIUM); GSE63060_non-normalized.txt.gz = NON_NORMALIZED (MEDIUM). Do not apply normalisation to data that is already normalised.
## 11. Run information
- Run ID: `20261009T140756Z-e178f3`
- Audit started/finished (UTC): 2026-10-09T14:07:56+00:00 / 2026-10-09T14:08:09+00:00
- Software: biomarker_project 0.1.0, Python 3.13.9, pandas 3.0.6, numpy 2.5.3, requests 2.34.2, PyYAML 6.0.3
- Config SHA-256: `c1438e0f29cc22fa51679dcaf7999ff599c01d97e4c77b656e244ebce8eb0d48`
- Command: `scripts/run_all_audits.py --offline`
