# Dataset audit: GSE140829
**Overall audit status: `COMPLETE_REVIEW_REQUIRED`** — 4 issue(s) require review
> Evidence labels: **VERIFIED** (directly established from retrieved records/files), **REPORTED** (stated elsewhere, not reproduced), **UNRESOLVED** (insufficient evidence), **FAILED** (attempted, failed). There is no PASS status; Phase 1 performs no differential expression, feature selection, enrichment or modelling.
## 1. Accession and provisional role
- Accession: [GSE140829](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE140829)
- Provisional role: `potential_external_ad_validation` — Potential external AD validation cohort (whole blood).
- Analysis tier: `validation_candidate`
- Related accessions (config): none
- Participant independence: **UNRESOLVED** — A separate GEO accession does not prove participant-level independence from the AddNeuroMed series. Requires verification from study documentation.
- GEO title: Systems-level analysis of peripheral blood gene expression in dementia patients reveals an innate immune response shared across multiple disorders [ad_mci]
- GEO series type: Expression profiling by array
- GEO relations: SubSeries of: GSE140831; BioProject: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA591098
- GEO last update: Jun 15 2022
## 2. Retrieval status
| metadata resource | status | bytes | sha256 | retrieved (UTC) |
|---|---|---|---|---|
| GSE140829_series_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 21336 | d76323f463e587b196f6ccecce8cfcc3a30fd790caa90057ab1037f5fc2f4159 | 2026-10-09T14:08:20+00:00 |
| GSE140829_samples_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 1520541 | 3a5c0b54cee71e7c96d1a7a86facf730ec71ee660abe14a3649b4ed8b9fda754 | 2026-10-09T14:08:20+00:00 |
| GPL15988_platform_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 60086 | 12f3d9dd0c8a61610392034c489c8f42a72332b9fde06914750bc66bc16f24be | 2026-10-09T14:08:20+00:00 |

| file | requested | status | size | sha256 (prefix) | notes |
|---|---|---|---|---|---|
| GSE140829_series_matrix.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 226.3 MB | be4f08a2cb01fe91… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE140829_final_normalized_data.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 72.6 MB | 28613d74484a130c… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE140829_raw_data.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 326.9 MB | de2ba7864b0c1b43… | existing file re-used: checksum matches earlier manifest record (server not consulted) |

Network used in this run: **False** (offline mode: True).
## 3. Available files (GEO listing)
_GEO directory listing not retrieved in this run (offline or failed)._
## 4. Observed sample counts
- **VERIFIED** — GEO series lists 587 samples and all 587 sample records were retrieved
- **VERIFIED** — observed 587 GEO sample records; group counts match the reference values (all compared groups match)

| group | reported | observed | difference | status |
|---|---|---|---|---|
| TOTAL | 587 | 587 | 0 | MATCHES_REPORTED |
| AD | 204 | 204 | 0 | MATCHES_REPORTED |
| MCI | 134 | 134 | 0 | MATCHES_REPORTED |
| HC | 249 | 249 | 0 | MATCHES_REPORTED |

Reference counts source: GEO series record as reported in the BIO-MB-001 brief (REPORTED; used for comparison only, never enforced).
## 5. Observed diagnostic groups
Diagnosis field: `char:diagnosis`

| raw GEO label | n |
|---|---|
| AD | 204 |
| Control | 249 |
| MCI | 134 |

Canonical mapping (from config label_map; unmapped labels are flagged, not guessed):

| group | n |
|---|---|
| AD | 204 |
| HC | 249 |
| MCI | 134 |

Potential covariates (non-missing records out of total):

| field | n_present | n_missing | n_distinct |
|---|---|---|---|
| char:age_at_draw | 587 | 0 | 29 |
| char:Sex | 587 | 0 | 2 |
| char:apoe_status | 575 | 12 | 6 |
| char:batch | 587 | 0 | 19 |
| char:connectivity_zscore | 587 | 0 | 197 |
## 6. Sample reconciliation
### GSE140829_series_matrix.txt.gz (key: expression column/sample ID == GEO geo_accession)
- expression IDs: 587; phenotype records: 587; exact matches: 587
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'AD': 204, 'HC': 249, 'MCI': 134}
- full ID listing: `reports/dataset_audit/GSE140829/GSE140829_series_matrix_txt_gz_id_reconciliation.csv`
### GSE140829_final_normalized_data.txt.gz (key: expression column/sample ID == GEO title (regex '(\\d+_[A-Z])'))
- expression IDs: 551; phenotype records: 587; exact matches: 551
- expression-only: 0; phenotype-only: 36; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **False**
- group counts among matched records: {'AD': 198, 'HC': 229, 'MCI': 124}
- full ID listing: `reports/dataset_audit/GSE140829/GSE140829_final_normalized_data_txt_gz_id_reconciliation.csv`
- phenotype-only IDs (first 20): ['200373830016_D', '3999230062_J', '3999230071_D', '5872641011_F', '5872641012_B', '5872641012_D', '5872641012_F', '5872641012_J', '5872641016_B', '5872641016_G', '5872641018_A', '5872641018_D', '5872641018_F', '5872641018_L', '5872641031_H', '5872641032_B', '5872641032_C', '5872641053_I', '5872641059_D', '5872641070_B']
### GSE140829_raw_data.txt.gz (key: expression column/sample ID == GEO title (regex '(\\d+_[A-Z])'))
- expression IDs: 587; phenotype records: 587; exact matches: 587
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'AD': 204, 'HC': 249, 'MCI': 134}
- full ID listing: `reports/dataset_audit/GSE140829/GSE140829_raw_data_txt_gz_id_reconciliation.csv`

### Cross-file value concordance (read-only)
| file_a | file_b | status | n_shared_features | n_shared_samples | fraction_identical | max_abs_difference | pearson_r |
|---|---|---|---|---|---|---|---|
| GSE140829_series_matrix.txt.gz | GSE140829_final_normalized_data.txt.gz | NO_OVERLAP | 0 | 0 |  |  |  |
| GSE140829_series_matrix.txt.gz | GSE140829_raw_data.txt.gz | NO_OVERLAP | 0 | 0 |  |  |  |

Reported leads:

_none_

Proposed exclusion candidates (NOT applied): 36 — see `reports/dataset_audit/GSE140829/proposed_exclusions.csv`
## 7. Processing-state assessment
| file | state | confidence | review | filename_hint | basis |
|---|---|---|---|---|---|
| GSE140829_series_matrix.txt.gz | PROCESSED_NORMALIZED | HIGH | False |  | values on a log-like scale (min 6.72, max 15.3): a transformation has been applied; GSM data_processing: 'Data was imported from BeadStudio/GenomeStudio output (raw_data.txt) using lumi.  Illumina Ids were converted to nuIDs and expression values were normalized using variance-stabilizing transform.  Interarray normalization was done using robust spline normalization (normalized_data.txt).  Probes were ' |
| GSE140829_final_normalized_data.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True | PROCESSED_NORMALIZED | values on a log-like scale (min 6.07, max 15.3): a transformation has been applied |
| GSE140829_raw_data.txt.gz | NON_NORMALIZED | HIGH | True | RAW_INSTRUMENT | Illumina GenomeStudio-style per-sample columns ['bead_stderr', 'detection_pval', 'n_beads', 'signal'] (summarised probe profile export; usually exported before normalisation); linear-scale intensities (min 56.8, max 3.97e+04, 0.00% negative); per-sample distributions differ (max SD/IQR 0.622 at q25-q75): no between-sample distribution normalisation evident |

Phase 1 does not normalise or transform any data.
## 8. Platform and modality
- Configured modality: `expression_microarray` (Illumina BeadArray)
- Configured platform: GPL15988 — Illumina HumanHT-12 v4 (as reported)
- Observed platform: **GPL15988** — HumanHT-12 v4 Expression BeadChip (nuID) (technology: oligonucleotide beads; distribution: custom-commercial)
- **VERIFIED** — configured platform GPL15988; GEO series platform(s): ['GPL15988']
- **VERIFIED** — GPL15988: HumanHT-12 v4 Expression BeadChip (nuID) (oligonucleotide beads)
- **VERIFIED** — GEO series type: ['Expression profiling by array']; configured modality: expression_microarray
## 9. Issues and limitations
| severity | category | description |
|---|---|---|
| medium | processing | GSE140829_final_normalized_data.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review |
| medium | processing | GSE140829_raw_data.txt.gz: processing state NON_NORMALIZED (confidence HIGH) requires review; content-based state NON_NORMALIZED contradicts the file-name hint RAW_INSTRUMENT |
| medium | reconciliation | GSE140829_final_normalized_data.txt.gz: not an exact one-to-one match with GEO records (0 expression-only, 36 phenotype-only, 0 duplicated expression IDs, 0 duplicated phenotype keys, 0 records without key) |
| low | inspection | GSE140829_raw_data.txt.gz: 26204 missing values in 365 sample column(s) |

### All findings
| status | topic | statement | evidence |
|---|---|---|---|
| VERIFIED | sample_count | GEO series lists 587 samples and all 587 sample records were retrieved | series record !Series_sample_id vs retrieved GSM records |
| VERIFIED | platform | configured platform GPL15988; GEO series platform(s): ['GPL15988'] | GEO series record |
| VERIFIED | platform | GPL15988: HumanHT-12 v4 Expression BeadChip (nuID) (oligonucleotide beads) | GEO platform record |
| VERIFIED | modality | GEO series type: ['Expression profiling by array']; configured modality: expression_microarray | GEO series record |
| VERIFIED | relations | GEO relation: SubSeries of: GSE140831 | GEO series record |
| UNRESOLVED | independence | participant independence status: UNRESOLVED. A separate GEO accession does not prove participant-level independence from the AddNeuroMed series. Requires verification from study documentation. | configuration (not established from data) |
| VERIFIED | diagnosis_labels | every sample has a diagnosis label in char:diagnosis that is mapped or explicitly flagged | GEO sample characteristics |
| VERIFIED | sample_count | observed 587 GEO sample records; group counts match the reference values (all compared groups match) | GEO sample records vs config expected_counts |
| VERIFIED | retrieval | GSE140829_series_matrix.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 226272058 bytes, SHA-256 be4f08a2cb01fe912a764df66fd654dec70d9e1ecd36bded00b675b27e7f83f3 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140829/matrix/GSE140829_series_matrix.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE140829_final_normalized_data.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 72571520 bytes, SHA-256 28613d74484a130cfe7f00034db6ae7358983adb50a1e8b01fb2d1e17ae1798b | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140829/suppl/GSE140829_final_normalized_data.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE140829_raw_data.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 326906021 bytes, SHA-256 de2ba7864b0c1b4350203e8fcc3d10382e990b3e5e98c5a1a4973ef8a7fd7938 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE140nnn/GSE140829/suppl/GSE140829_raw_data.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | inspection | GSE140829_series_matrix.txt.gz: geo_series_matrix (gzip), kind=expression_matrix, rows=47008, columns=588, candidate samples=587 | streamed file inspection |
| VERIFIED | processing | GSE140829_series_matrix.txt.gz: PROCESSED_NORMALIZED (confidence HIGH) | values on a log-like scale (min 6.72, max 15.3): a transformation has been applied; GSM data_processing: 'Data was imported from BeadStudio/GenomeStudio output (raw_data.txt) using lumi.  Illumina Ids were converted to nuIDs and expression values were normalized using variance-stabilizing transform.  Interarray normalization was done using robust spline normalization (normalized_data.txt).  Probes were ' |
| VERIFIED | inspection | GSE140829_final_normalized_data.txt.gz: delimited_text (gzip), kind=expression_matrix, rows=15987, columns=552, candidate samples=551 | streamed file inspection |
| UNRESOLVED | processing | GSE140829_final_normalized_data.txt.gz: PROCESSED_NORMALIZED (confidence MEDIUM) | values on a log-like scale (min 6.07, max 15.3): a transformation has been applied |
| VERIFIED | inspection | GSE140829_raw_data.txt.gz: delimited_text (gzip), kind=expression_matrix, rows=47231, columns=2361, candidate samples=587 | streamed file inspection |
| VERIFIED | processing | GSE140829_raw_data.txt.gz: NON_NORMALIZED (confidence HIGH) | Illumina GenomeStudio-style per-sample columns ['bead_stderr', 'detection_pval', 'n_beads', 'signal'] (summarised probe profile export; usually exported before normalisation); linear-scale intensities (min 56.8, max 3.97e+04, 0.00% negative); per-sample distributions differ (max SD/IQR 0.622 at q25-q75): no between-sample distribution normalisation evident |
| VERIFIED | reconciliation | GSE140829_series_matrix.txt.gz: 587 expression IDs vs 587 phenotype records; 587 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO geo_accession |
| VERIFIED | reconciliation | GSE140829_final_normalized_data.txt.gz: 551 expression IDs vs 587 phenotype records; 551 exact matches, 0 expression-only, 36 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO title (regex '(\\d+_[A-Z])') |
| VERIFIED | reconciliation | GSE140829_raw_data.txt.gz: 587 expression IDs vs 587 phenotype records; 587 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO title (regex '(\\d+_[A-Z])') |
| UNRESOLVED | processing | series matrix vs GSE140829_final_normalized_data.txt.gz: NO_OVERLAP (0 features x 0 samples compared; fraction identical None) | read-only value comparison on the first features |
| UNRESOLVED | processing | series matrix vs GSE140829_raw_data.txt.gz: NO_OVERLAP (0 features x 0 samples compared; fraction identical None) | read-only value comparison on the first features |
## 10. Recommended next actions
1. Verify participant-level independence/overlap with related cohorts from study documentation or the data owners; a different GEO accession does not establish independence.
2. Review unmatched/duplicated identifiers for GSE140829_final_normalized_data.txt.gz in reports/dataset_audit/GSE140829/GSE140829_final_normalized_data_txt_gz_id_reconciliation.csv.
3. Choose the downstream input file for this dataset only after reviewing the processing evidence: GSE140829_series_matrix.txt.gz = PROCESSED_NORMALIZED (HIGH); GSE140829_final_normalized_data.txt.gz = PROCESSED_NORMALIZED (MEDIUM); GSE140829_raw_data.txt.gz = NON_NORMALIZED (HIGH). Do not apply normalisation to data that is already normalised.
## 11. Run information
- Run ID: `20261009T140756Z-e178f3`
- Audit started/finished (UTC): 2026-10-09T14:08:20+00:00 / 2026-10-09T14:08:58+00:00
- Software: biomarker_project 0.1.0, Python 3.13.9, pandas 3.0.6, numpy 2.5.3, requests 2.34.2, PyYAML 6.0.3
- Config SHA-256: `c1438e0f29cc22fa51679dcaf7999ff599c01d97e4c77b656e244ebce8eb0d48`
- Command: `scripts/run_all_audits.py --offline`
