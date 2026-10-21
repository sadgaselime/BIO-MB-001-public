# Dataset audit: GSE99039
**Overall audit status: `INCOMPLETE`** — GSE99039_RAW.tar: requested but not available (SKIPPED_OFFLINE)
> Evidence labels: **VERIFIED** (directly established from retrieved records/files), **REPORTED** (stated elsewhere, not reproduced), **UNRESOLVED** (insufficient evidence), **FAILED** (attempted, failed). There is no PASS status; Phase 1 performs no differential expression, feature selection, enrichment or modelling.
## 1. Accession and provisional role
- Accession: [GSE99039](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE99039)
- Provisional role: `pd_neurodegeneration_specificity_candidate` — PD and neurodegeneration specificity analysis candidate.
- Analysis tier: `specificity_candidate`
- Related accessions (config): none
- Participant independence: **UNRESOLVED** — Different platform from the AD cohorts; raw intensities must never be combined across platforms.
- GEO title: A blood-based gene signature characterizing Idiopathic Parkinson's disease
- GEO series type: Expression profiling by array
- GEO relations: BioProject: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA387280
- GEO last update: Jul 25 2021
## 2. Retrieval status
| metadata resource | status | bytes | sha256 | retrieved (UTC) |
|---|---|---|---|---|
| GSE99039_series_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 20239 | f4fb9d0947627ffae0e98b850191e3e70bd4bc2e3ba9578d069f318151cb175a | 2026-10-09T14:08:58+00:00 |
| GSE99039_samples_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 1474080 | 326f8b5191be445b46053da634f9f5e3196b97c0f53be3cdc3e58c90482f2281 | 2026-10-09T14:08:58+00:00 |
| GPL570_platform_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 6141153 | f92969223ad2ea5b4694f4f97a15313b722b8f25bdc9b52c74b5356d262586f8 | 2026-10-09T14:08:58+00:00 |

| file | requested | status | size | sha256 (prefix) | notes |
|---|---|---|---|---|---|
| GSE99039_series_matrix.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 63.8 MB | 197b7272a8a5040c… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| filelist.txt | True | REUSED_VERIFIED_AGAINST_MANIFEST | 47389 B | 7fb47f5f46ccdecd… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE99039_RAW.tar | True | SKIPPED_OFFLINE | ? |  | offline mode: file not present locally and no download attempted |

Network used in this run: **False** (offline mode: True).
## 3. Available files (GEO listing)
_GEO directory listing not retrieved in this run (offline or failed)._
## 4. Observed sample counts
- **VERIFIED** — GEO series lists 558 samples and all 558 sample records were retrieved
- **VERIFIED** — observed 558 GEO sample records; group counts differ from the reference values (OTHER_NEURO)

| group | reported | observed | difference | status |
|---|---|---|---|---|
| HC | 233 | 233 | 0 | MATCHES_REPORTED |
| PD | 205 | 205 | 0 | MATCHES_REPORTED |
| OTHER_NEURO | 48 | 49 | 1 | DIFFERS_FROM_REPORTED |
| AMBIGUOUS |  | 8 |  | NO_REFERENCE_COUNT |
| GENETIC_UNAFFECTED |  | 22 |  | NO_REFERENCE_COUNT |
| PD_GENETIC |  | 41 |  | NO_REFERENCE_COUNT |

Reference counts source: BIO-MB-001 brief (main groups only; genetic PD and unaffected carriers reported separately) (REPORTED; used for comparison only, never enforced).
## 5. Observed diagnostic groups
Diagnosis field: `char:disease label`

| raw GEO label | n |
|---|---|
| ATYPICAL_PD | 3 |
| CBD | 2 |
| CONTROL | 233 |
| DRD | 3 |
| DRD-DYT5 | 3 |
| GENETIC_UNAFFECTED | 22 |
| GPD | 41 |
| HD | 19 |
| HD_HD_BATCH | 8 |
| IPD | 205 |
| MSA | 8 |
| PD_DEMENTIA | 2 |
| PSP | 8 |
| Vascular dementia | 1 |

Canonical mapping (from config label_map; unmapped labels are flagged, not guessed):

| group | n |
|---|---|
| AMBIGUOUS | 8 |
| GENETIC_UNAFFECTED | 22 |
| HC | 233 |
| OTHER_NEURO | 49 |
| PD | 205 |
| PD_GENETIC | 41 |

Potential covariates (non-missing records out of total):

| field | n_present | n_missing | n_distinct |
|---|---|---|---|
| char:Sex | 505 | 53 | 2 |
| char:age at exam | 292 | 266 | 46 |
| char:batch | 558 | 0 | 37 |
| char:learning set | 558 | 0 | 3 |
| char:genetic (mutated pd genes) | 510 | 48 | 10 |
| char:moca score | 552 | 6 | 19 |

Participant-ID field `char:subject_id`: 550 present, 550 distinct, 0 duplicated ID(s) covering 0 records.
## 6. Sample reconciliation
### GSE99039_series_matrix.txt.gz (key: expression column/sample ID == GEO geo_accession)
- expression IDs: 558; phenotype records: 558; exact matches: 558
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'AMBIGUOUS': 8, 'GENETIC_UNAFFECTED': 22, 'HC': 233, 'OTHER_NEURO': 49, 'PD': 205, 'PD_GENETIC': 41}
- full ID listing: `reports/dataset_audit/GSE99039/GSE99039_series_matrix_txt_gz_id_reconciliation.csv`

Reported leads:

_none_

Proposed exclusion candidates (NOT applied): 8 — see `reports/dataset_audit/GSE99039/proposed_exclusions.csv`
## 7. Processing-state assessment
| file | state | confidence | review | filename_hint | basis |
|---|---|---|---|---|---|
| GSE99039_series_matrix.txt.gz | PROCESSED_NORMALIZED | HIGH | False |  | values on a log-like scale (min 1.46, max 15.2): a transformation has been applied; GSM data_processing: 'Data were preprocessed using RMA. Then the data were log2 transformed and quantile normalized. RMA was selected as it produced better patient correlations than MAS5 and GC-RMA.' |
| filelist.txt | METADATA_ONLY | HIGH | False | METADATA_ONLY | table kind 'file_manifest' contains no expression values |
| GSE99039_RAW.tar | UNKNOWN | LOW | True |  | file not available for inspection |

Phase 1 does not normalise or transform any data.
## 8. Platform and modality
- Configured modality: `expression_microarray` (Affymetrix 3' IVT array)
- Configured platform: GPL570 — Affymetrix Human Genome U133 Plus 2.0 Array
- Observed platform: **GPL570** — [HG-U133_Plus_2] Affymetrix Human Genome U133 Plus 2.0 Array (technology: in situ oligonucleotide; distribution: commercial)
- **VERIFIED** — configured platform GPL570; GEO series platform(s): ['GPL570']
- **VERIFIED** — GPL570: [HG-U133_Plus_2] Affymetrix Human Genome U133 Plus 2.0 Array (in situ oligonucleotide)
- **VERIFIED** — GEO series type: ['Expression profiling by array']; configured modality: expression_microarray
## 9. Issues and limitations
| severity | category | description |
|---|---|---|
| medium | phenotype | 8 sample(s) with ambiguous diagnosis label: {'HD_HD_BATCH': 8} |
| medium | phenotype | 8 sample(s) lack a participant ID in char:subject_id |
| medium | counts | OTHER_NEURO: observed 49 vs reported 48 (difference +1) |
| medium | retrieval | GSE99039_RAW.tar: SKIPPED_OFFLINE |

### All findings
| status | topic | statement | evidence |
|---|---|---|---|
| VERIFIED | sample_count | GEO series lists 558 samples and all 558 sample records were retrieved | series record !Series_sample_id vs retrieved GSM records |
| VERIFIED | platform | configured platform GPL570; GEO series platform(s): ['GPL570'] | GEO series record |
| VERIFIED | platform | GPL570: [HG-U133_Plus_2] Affymetrix Human Genome U133 Plus 2.0 Array (in situ oligonucleotide) | GEO platform record |
| VERIFIED | modality | GEO series type: ['Expression profiling by array']; configured modality: expression_microarray | GEO series record |
| UNRESOLVED | independence | participant independence status: UNRESOLVED. Different platform from the AD cohorts; raw intensities must never be combined across platforms. | configuration (not established from data) |
| VERIFIED | diagnosis_labels | 8 sample(s) with ambiguous diagnosis label: {'HD_HD_BATCH': 8} | GEO characteristics field char:disease label |
| VERIFIED | diagnosis_labels | every sample has a diagnosis label in char:disease label that is mapped or explicitly flagged | GEO sample characteristics |
| VERIFIED | sample_count | observed 558 GEO sample records; group counts differ from the reference values (OTHER_NEURO) | GEO sample records vs config expected_counts |
| VERIFIED | retrieval | GSE99039_series_matrix.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 63827685 bytes, SHA-256 197b7272a8a5040c2843cbefd44f8bd43e9b7820562732d5b1ffd30841bfcb50 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE99nnn/GSE99039/matrix/GSE99039_series_matrix.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | filelist.txt: REUSED_VERIFIED_AGAINST_MANIFEST, 47389 bytes, SHA-256 7fb47f5f46ccdecd3bce2397a60a1d0b2ae5920f344b388a32aea184428c88ec | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE99nnn/GSE99039/suppl/filelist.txt; integrity: none_applicable |
| UNRESOLVED | retrieval | GSE99039_RAW.tar not available locally (SKIPPED_OFFLINE) | offline mode: file not present locally and no download attempted |
| VERIFIED | inspection | GSE99039_series_matrix.txt.gz: geo_series_matrix (gzip), kind=expression_matrix, rows=54675, columns=559, candidate samples=558 | streamed file inspection |
| VERIFIED | processing | GSE99039_series_matrix.txt.gz: PROCESSED_NORMALIZED (confidence HIGH) | values on a log-like scale (min 1.46, max 15.2): a transformation has been applied; GSM data_processing: 'Data were preprocessed using RMA. Then the data were log2 transformed and quantile normalized. RMA was selected as it produced better patient correlations than MAS5 and GC-RMA.' |
| VERIFIED | inspection | filelist.txt: geo_filelist (none), kind=file_manifest, rows=559, columns=5, candidate samples=0 | streamed file inspection |
| VERIFIED | processing | filelist.txt: METADATA_ONLY (confidence HIGH) | table kind 'file_manifest' contains no expression values |
| VERIFIED | reconciliation | GSE99039_series_matrix.txt.gz: 558 expression IDs vs 558 phenotype records; 558 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO geo_accession |
## 10. Recommended next actions
1. Verify participant-level independence/overlap with related cohorts from study documentation or the data owners; a different GEO accession does not establish independence.
2. Decide (in a prespecified analysis plan) how ambiguous/transition diagnosis labels are handled; they are kept separate and nothing has been excluded.
3. Investigate the differences between observed and reported counts (see group-count table); no samples were removed or added to match reference values.
4. Choose the downstream input file for this dataset only after reviewing the processing evidence: GSE99039_series_matrix.txt.gz = PROCESSED_NORMALIZED (HIGH). Do not apply normalisation to data that is already normalised.
## 11. Run information
- Run ID: `20261009T140756Z-e178f3`
- Audit started/finished (UTC): 2026-10-09T14:08:58+00:00 / 2026-10-09T14:09:03+00:00
- Software: biomarker_project 0.1.0, Python 3.13.9, pandas 3.0.6, numpy 2.5.3, requests 2.34.2, PyYAML 6.0.3
- Config SHA-256: `c1438e0f29cc22fa51679dcaf7999ff599c01d97e4c77b656e244ebce8eb0d48`
- Command: `scripts/run_all_audits.py --offline`
