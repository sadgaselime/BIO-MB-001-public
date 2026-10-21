# Dataset audit: GSE165081
**Overall audit status: `COMPLETE_REVIEW_REQUIRED`** — 2 issue(s) require review
> Evidence labels: **VERIFIED** (directly established from retrieved records/files), **REPORTED** (stated elsewhere, not reproduced), **UNRESOLVED** (insufficient evidence), **FAILED** (attempted, failed). There is no PASS status; Phase 1 performs no differential expression, feature selection, enrichment or modelling.
## 1. Accession and provisional role
- Accession: [GSE165081](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE165081)
- Provisional role: `optional_future_methylation_extension` — Optional future DNA-methylation extension. NOT transcriptomic validation and never merged with RNA-seq expression matrices.
- Analysis tier: `future_extension`
- Related accessions (config): GSE165082, GSE165083
- Participant independence: **NOT_APPLICABLE** — Same participants as GSE165082 are expected (different modality); correspondence unverified.
- GEO title: DNA methylation and expression profiles of whole blood in Parkinson’s disease (Methylation)
- GEO series type: Methylation profiling by array
- GEO relations: SubSeries of: GSE165083; BioProject: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA693203
- GEO last update: May 14 2021
## 2. Retrieval status
| metadata resource | status | bytes | sha256 | retrieved (UTC) |
|---|---|---|---|---|
| GSE165081_series_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 5364 | 8843c5d3f20db1a54bd478a720f24baa51c9dedb713d5e6c00810236ca519a3b | 2026-10-09T14:09:04+00:00 |
| GSE165081_samples_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 147070 | 10da891965016ae3917d220d6ec73e7f80b1c7d2f2613841977efd53900aeb3a | 2026-10-09T14:09:04+00:00 |
| GPL13534_platform_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 4213086 | f2dbe7d16664a1da9d5592ccb39464a9f337a438f31825a778aadb2a87e785e0 | 2026-10-09T14:09:04+00:00 |

| file | requested | status | size | sha256 (prefix) | notes |
|---|---|---|---|---|---|
| GSE165081_Sample_Sheet.PD-CN.csv.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 417 B | 3351a20ba0210eb5… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE165081_detP.csv.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 2.5 MB | 4214d4bb77d200af… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| filelist.txt | True | REUSED_VERIFIED_AGAINST_MANIFEST | 4875 B | f263292ee14c28e9… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE165081_RAW.tar | False | SKIPPED_NOT_REQUESTED | ? |  | not requested in configuration (retrieve: false) |
| GSE165081_M.csv.gz | False | SKIPPED_NOT_REQUESTED | ? |  | not requested in configuration (retrieve: false) |
| GSE165081_series_matrix.txt.gz | False | SKIPPED_NOT_REQUESTED | ? |  | not requested in configuration (retrieve: false) |

Network used in this run: **False** (offline mode: True).
## 3. Available files (GEO listing)
_GEO directory listing not retrieved in this run (offline or failed)._
## 4. Observed sample counts
- **VERIFIED** — GEO series lists 28 samples and all 28 sample records were retrieved
- **VERIFIED** — observed 28 GEO sample records; group counts differ from the reference values (DESCRIBED_PARTICIPANTS)
- **VERIFIED** — GEO overall design text: "Parkinson's disease (PD) and control subjects where analyzed for changes in gene expression and DNA methylation. Each group contained 15 age-matched subjects. Two blood samples were taken from each subject. One sample was used for isolation of total RNA and the other was used for extraction of DNA. The PD group was compared to controls for each data type and correlations between data types were as"

| group | reported | observed | difference | status |
|---|---|---|---|---|
| TOTAL | 28 | 28 | 0 | MATCHES_REPORTED |
| HC |  | 14 |  | NO_REFERENCE_COUNT |
| PD |  | 14 |  | NO_REFERENCE_COUNT |
| DESCRIBED_PARTICIPANTS | 30 | 28 | -2 | DIFFERS_FROM_REPORTED |

Reference counts source: GEO sample list (28) and study description (30 participants) as reported in the brief (REPORTED; used for comparison only, never enforced).
## 5. Observed diagnostic groups
Diagnosis field: `char:group`

| raw GEO label | n |
|---|---|
| Control | 14 |
| PD | 14 |

Canonical mapping (from config label_map; unmapped labels are flagged, not guessed):

| group | n |
|---|---|
| HC | 14 |
| PD | 14 |
## 6. Sample reconciliation
### GSE165081_Sample_Sheet.PD-CN.csv.gz (key: sample_sheet column/sample ID == GEO title)
- sample_sheet IDs: 28; phenotype records: 28; exact matches: 28
- sample_sheet-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate sample_sheet IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'HC': 14, 'PD': 14}
- full ID listing: `reports/dataset_audit/GSE165081/GSE165081_Sample_Sheet_PD-CN_csv_gz_id_reconciliation.csv`
- label concordance with GEO records: {'compared': 28, 'identical_group_labels': 28}
### GSE165081_detP.csv.gz (key: expression column/sample ID == GEO title)
- expression IDs: 28; phenotype records: 28; exact matches: 28
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'HC': 14, 'PD': 14}
- full ID listing: `reports/dataset_audit/GSE165081/GSE165081_detP_csv_gz_id_reconciliation.csv`

Reported leads:

| lead | status | description | check |
|---|---|---|---|
| GSE165081-LEAD-1 | REPORTED | GEO lists 28 methylation samples whereas the study description refers to 30 participants. | count discrepancy: compared through expected_counts (see the group-count table); the reason for the difference is UNRESOLVED |

Proposed exclusion candidates (NOT applied): 0 — see `reports/dataset_audit/GSE165081/proposed_exclusions.csv`
## 7. Processing-state assessment
| file | state | confidence | review | filename_hint | basis |
|---|---|---|---|---|---|
| GSE165081_Sample_Sheet.PD-CN.csv.gz | METADATA_ONLY | HIGH | False | METADATA_ONLY | table kind 'sample_sheet' contains no expression values |
| GSE165081_detP.csv.gz | UNKNOWN | LOW | True |  | no content-based evidence; processing state cannot be established |
| filelist.txt | METADATA_ONLY | HIGH | False | METADATA_ONLY | table kind 'file_manifest' contains no expression values |

Phase 1 does not normalise or transform any data.
## 8. Platform and modality
- Configured modality: `methylation_array` (Illumina Infinium methylation array)
- Configured platform: None — None
- Observed platform: **GPL13534** — Illumina HumanMethylation450 BeadChip (HumanMethylation450_15017482) (technology: oligonucleotide beads; distribution: commercial)
- **VERIFIED** — platform not specified in config; GEO reports ['GPL13534']
- **VERIFIED** — GPL13534: Illumina HumanMethylation450 BeadChip (HumanMethylation450_15017482) (oligonucleotide beads)
- **VERIFIED** — GEO series type: ['Methylation profiling by array']; configured modality: methylation_array
- **VERIFIED** — DNA methylation dataset: kept separate; not transcriptomic validation and never merged with RNA-seq or microarray expression matrices
## 9. Issues and limitations
| severity | category | description |
|---|---|---|
| high | processing | GSE165081_detP.csv.gz: processing state UNKNOWN (confidence LOW) requires review; no content-based evidence; processing state cannot be established |
| medium | counts | DESCRIBED_PARTICIPANTS: observed 28 vs reported 30 (difference -2) |

### All findings
| status | topic | statement | evidence |
|---|---|---|---|
| VERIFIED | sample_count | GEO series lists 28 samples and all 28 sample records were retrieved | series record !Series_sample_id vs retrieved GSM records |
| VERIFIED | platform | platform not specified in config; GEO reports ['GPL13534'] | GEO series record |
| VERIFIED | platform | GPL13534: Illumina HumanMethylation450 BeadChip (HumanMethylation450_15017482) (oligonucleotide beads) | GEO platform record |
| VERIFIED | modality | GEO series type: ['Methylation profiling by array']; configured modality: methylation_array | GEO series record |
| VERIFIED | relations | GEO relation: SubSeries of: GSE165083 | GEO series record |
| REPORTED | independence | participant independence status: NOT_APPLICABLE. Same participants as GSE165082 are expected (different modality); correspondence unverified. | configuration (not established from data) |
| VERIFIED | diagnosis_labels | every sample has a diagnosis label in char:group that is mapped or explicitly flagged | GEO sample characteristics |
| VERIFIED | sample_count | observed 28 GEO sample records; group counts differ from the reference values (DESCRIBED_PARTICIPANTS) | GEO sample records vs config expected_counts |
| VERIFIED | retrieval | GSE165081_Sample_Sheet.PD-CN.csv.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 417 bytes, SHA-256 3351a20ba0210eb50960f4889319bedf37e1c96f3baa7e30f41552e467e85ebf | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE165nnn/GSE165081/suppl/GSE165081_Sample_Sheet.PD-CN.csv.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE165081_detP.csv.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 2457980 bytes, SHA-256 4214d4bb77d200af04d2bf904bbc343311254a4b09624ee02ce06b5a07f0392a | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE165nnn/GSE165081/suppl/GSE165081_detP.csv.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | filelist.txt: REUSED_VERIFIED_AGAINST_MANIFEST, 4875 bytes, SHA-256 f263292ee14c28e9f7c70624f2c40ce0a19b81ed4f8c0387bd978a2be617cd0a | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE165nnn/GSE165081/suppl/filelist.txt; integrity: none_applicable |
| VERIFIED | inspection | GSE165081_Sample_Sheet.PD-CN.csv.gz: delimited_text (gzip), kind=sample_sheet, rows=28, columns=9, candidate samples=28 | streamed file inspection |
| VERIFIED | processing | GSE165081_Sample_Sheet.PD-CN.csv.gz: METADATA_ONLY (confidence HIGH) | table kind 'sample_sheet' contains no expression values |
| VERIFIED | inspection | GSE165081_detP.csv.gz: delimited_text (gzip), kind=expression_matrix, rows=485512, columns=29, candidate samples=28 | streamed file inspection |
| UNRESOLVED | processing | GSE165081_detP.csv.gz: UNKNOWN (confidence LOW) | no content evidence |
| VERIFIED | inspection | filelist.txt: geo_filelist (none), kind=file_manifest, rows=61, columns=5, candidate samples=0 | streamed file inspection |
| VERIFIED | processing | filelist.txt: METADATA_ONLY (confidence HIGH) | table kind 'file_manifest' contains no expression values |
| VERIFIED | reconciliation | GSE165081_Sample_Sheet.PD-CN.csv.gz: 28 sample_sheet IDs vs 28 phenotype records; 28 exact matches, 0 sample_sheet-only, 0 phenotype-only, 0/0 duplicated IDs | sample_sheet column/sample ID == GEO title |
| VERIFIED | reconciliation | GSE165081_detP.csv.gz: 28 expression IDs vs 28 phenotype records; 28 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO title |
| REPORTED | reported_lead | GSE165081-LEAD-1: GEO lists 28 methylation samples whereas the study description refers to 30 participants. | BIO-MB-001 brief |
| VERIFIED | sample_count | GEO overall design text: "Parkinson's disease (PD) and control subjects where analyzed for changes in gene expression and DNA methylation. Each group contained 15 age-matched subjects. Two blood samples were taken from each subject. One sample was used for isolation of total RNA and the other was used for extraction of DNA. The PD group was compared to controls for each data type and correlations between data types were as" | GEO series record (quoted, not interpreted) |
| VERIFIED | modality | DNA methylation dataset: kept separate; not transcriptomic validation and never merged with RNA-seq or microarray expression matrices | configuration + GEO type |
## 10. Recommended next actions
1. Investigate the differences between observed and reported counts (see group-count table); no samples were removed or added to match reference values.
2. Lead GSE165081-LEAD-1: establish from the publication/authors why GEO sample numbers differ from the described participants; do not infer or impute missing samples.
3. Keep GSE165081 future extension until its open discrepancies are explained.
4. Choose the downstream input file for this dataset only after reviewing the processing evidence: GSE165081_detP.csv.gz = UNKNOWN (LOW). Do not apply normalisation to data that is already normalised.
## 11. Run information
- Run ID: `20261009T140756Z-e178f3`
- Audit started/finished (UTC): 2026-10-09T14:09:04+00:00 / 2026-10-09T14:09:05+00:00
- Software: biomarker_project 0.1.0, Python 3.13.9, pandas 3.0.6, numpy 2.5.3, requests 2.34.2, PyYAML 6.0.3
- Config SHA-256: `c1438e0f29cc22fa51679dcaf7999ff599c01d97e4c77b656e244ebce8eb0d48`
- Command: `scripts/run_all_audits.py --offline`
