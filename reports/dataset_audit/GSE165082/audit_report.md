# Dataset audit: GSE165082
**Overall audit status: `COMPLETE_REVIEW_REQUIRED`** — 2 issue(s) require review
> Evidence labels: **VERIFIED** (directly established from retrieved records/files), **REPORTED** (stated elsewhere, not reproduced), **UNRESOLVED** (insufficient evidence), **FAILED** (attempted, failed). There is no PASS status; Phase 1 performs no differential expression, feature selection, enrichment or modelling.
## 1. Accession and provisional role
- Accession: [GSE165082](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE165082)
- Provisional role: `optional_exploratory_pd_rnaseq` — Optional exploratory PD RNA-seq dataset. Exploratory until the 26-vs-30 discrepancy is explained.
- Analysis tier: `exploratory`
- Related accessions (config): GSE165081, GSE165083
- Participant independence: **NOT_APPLICABLE** — Exploratory PD dataset; not used for AD replication.
- GEO title: DNA methylation and expression profiles of whole blood in Parkinson’s disease (RNA-Seq)
- GEO series type: Expression profiling by high throughput sequencing
- GEO relations: SubSeries of: GSE165083; BioProject: https://www.ncbi.nlm.nih.gov/bioproject/PRJNA693202; SRA: https://www.ncbi.nlm.nih.gov/sra?term=SRP302340
- GEO last update: May 14 2021
## 2. Retrieval status
| metadata resource | status | bytes | sha256 | retrieved (UTC) |
|---|---|---|---|---|
| GSE165082_series_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 4687 | 971d3f06e24846e5c251b22e8968fc2012fa5f033c234e95e1cc4990eb9b6575 | 2026-10-09T14:09:03+00:00 |
| GSE165082_samples_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 79318 | eb73207f0f475e93aec0a85bdd6417f02ff3fc09f71cc7b8b4a28bedfb1d46a0 | 2026-10-09T14:09:03+00:00 |
| GPL11154_platform_brief.soft.txt | REUSED_VERIFIED_AGAINST_MANIFEST | 6991170 | 4b58d3fb16fbdfe266f092c690a38cfd5f048024010f1f675a7f6a25ddc58a41 | 2026-10-09T14:09:03+00:00 |

| file | requested | status | size | sha256 (prefix) | notes |
|---|---|---|---|---|---|
| GSE165082_series_matrix.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 4034 B | 16cd63f53761c494… | existing file re-used: checksum matches earlier manifest record (server not consulted) |
| GSE165082_PD-CC.counts.txt.gz | True | REUSED_VERIFIED_AGAINST_MANIFEST | 1.2 MB | d0912e66d0cf4e84… | existing file re-used: checksum matches earlier manifest record (server not consulted) |

Network used in this run: **False** (offline mode: True).
## 3. Available files (GEO listing)
_GEO directory listing not retrieved in this run (offline or failed)._
## 4. Observed sample counts
- **VERIFIED** — GEO series lists 26 samples and all 26 sample records were retrieved
- **VERIFIED** — observed 26 GEO sample records; group counts differ from the reference values (DESCRIBED_PARTICIPANTS)
- **VERIFIED** — GEO overall design text: "Parkinson's disease (PD) and control subjects where analyzed for changes in gene expression and DNA methylation. Each group contained 15 age-matched subjects. Two blood samples were taken from each subject. One sample was used for isolation of total RNA and the other was used for extraction of DNA. The PD group was compared to controls for each data type and correlations between data types were as"

| group | reported | observed | difference | status |
|---|---|---|---|---|
| TOTAL | 26 | 26 | 0 | MATCHES_REPORTED |
| HC |  | 14 |  | NO_REFERENCE_COUNT |
| PD |  | 12 |  | NO_REFERENCE_COUNT |
| DESCRIBED_PARTICIPANTS | 30 | 26 | -4 | DIFFERS_FROM_REPORTED |

Reference counts source: GEO sample list (26) and study description (30 participants) as reported in the brief (REPORTED; used for comparison only, never enforced).
## 5. Observed diagnostic groups
Diagnosis field: `char:group`

| raw GEO label | n |
|---|---|
| Control | 14 |
| PD | 12 |

Canonical mapping (from config label_map; unmapped labels are flagged, not guessed):

| group | n |
|---|---|
| HC | 14 |
| PD | 12 |
## 6. Sample reconciliation
### GSE165082_series_matrix.txt.gz (key: expression column/sample ID == GEO geo_accession)
- expression IDs: 26; phenotype records: 26; exact matches: 26
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'HC': 14, 'PD': 12}
- full ID listing: `reports/dataset_audit/GSE165082/GSE165082_series_matrix_txt_gz_id_reconciliation.csv`
### GSE165082_PD-CC.counts.txt.gz (key: expression column/sample ID == GEO title)
- expression IDs: 26; phenotype records: 26; exact matches: 26
- expression-only: 0; phenotype-only: 0; records without extractable key: 0
- duplicate expression IDs: 0; duplicate phenotype IDs: 0
- IDs altered by conservative normalisation (whitespace/Unicode only): 0
- near-miss hints (NOT used for matching): 0
- exact one-to-one correspondence: **True**
- group counts among matched records: {'HC': 14, 'PD': 12}
- full ID listing: `reports/dataset_audit/GSE165082/GSE165082_PD-CC_counts_txt_gz_id_reconciliation.csv`

Reported leads:

| lead | status | description | check |
|---|---|---|---|
| GSE165082-LEAD-1 | REPORTED | GEO lists 26 samples whereas the study description refers to 30 participants. | count discrepancy: compared through expected_counts (see the group-count table); the reason for the difference is UNRESOLVED |

Proposed exclusion candidates (NOT applied): 0 — see `reports/dataset_audit/GSE165082/proposed_exclusions.csv`
## 7. Processing-state assessment
| file | state | confidence | review | filename_hint | basis |
|---|---|---|---|---|---|
| GSE165082_series_matrix.txt.gz | METADATA_ONLY | HIGH | False |  | table kind 'metadata_only_series_matrix' contains no expression values |
| GSE165082_PD-CC.counts.txt.gz | NON_NORMALIZED | MEDIUM | True | NON_NORMALIZED | all values are non-negative integers (max 12835229): raw count-like data; per-sample distributions differ (max SD/IQR 0.430 at q25-q75): no between-sample distribution normalisation evident |

Phase 1 does not normalise or transform any data.
## 8. Platform and modality
- Configured modality: `expression_rnaseq` (RNA sequencing)
- Configured platform: None — None
- Observed platform: **GPL11154** — Illumina HiSeq 2000 (Homo sapiens) (technology: high-throughput sequencing; distribution: virtual)
- **VERIFIED** — platform not specified in config; GEO reports ['GPL11154']
- **VERIFIED** — GPL11154: Illumina HiSeq 2000 (Homo sapiens) (high-throughput sequencing)
- **VERIFIED** — GEO series type: ['Expression profiling by high throughput sequencing']; configured modality: expression_rnaseq
- **VERIFIED** — RNA-seq dataset: values are not on the same scale as microarray intensities and must never be pooled with them
## 9. Issues and limitations
| severity | category | description |
|---|---|---|
| medium | counts | DESCRIBED_PARTICIPANTS: observed 26 vs reported 30 (difference -4) |
| medium | processing | GSE165082_PD-CC.counts.txt.gz: processing state NON_NORMALIZED (confidence MEDIUM) requires review |

### All findings
| status | topic | statement | evidence |
|---|---|---|---|
| VERIFIED | sample_count | GEO series lists 26 samples and all 26 sample records were retrieved | series record !Series_sample_id vs retrieved GSM records |
| VERIFIED | platform | platform not specified in config; GEO reports ['GPL11154'] | GEO series record |
| VERIFIED | platform | GPL11154: Illumina HiSeq 2000 (Homo sapiens) (high-throughput sequencing) | GEO platform record |
| VERIFIED | modality | GEO series type: ['Expression profiling by high throughput sequencing']; configured modality: expression_rnaseq | GEO series record |
| VERIFIED | relations | GEO relation: SubSeries of: GSE165083 | GEO series record |
| REPORTED | independence | participant independence status: NOT_APPLICABLE. Exploratory PD dataset; not used for AD replication. | configuration (not established from data) |
| VERIFIED | diagnosis_labels | every sample has a diagnosis label in char:group that is mapped or explicitly flagged | GEO sample characteristics |
| VERIFIED | sample_count | observed 26 GEO sample records; group counts differ from the reference values (DESCRIBED_PARTICIPANTS) | GEO sample records vs config expected_counts |
| VERIFIED | retrieval | GSE165082_series_matrix.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 4034 bytes, SHA-256 16cd63f53761c494cfb5911ca2e705d508d721fa374ac180be645d396078ac29 | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE165nnn/GSE165082/matrix/GSE165082_series_matrix.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | retrieval | GSE165082_PD-CC.counts.txt.gz: REUSED_VERIFIED_AGAINST_MANIFEST, 1181704 bytes, SHA-256 d0912e66d0cf4e841c6f57ac3ab119acdb50d3419edd10bcb39df32ac029521f | https://ftp.ncbi.nlm.nih.gov/geo/series/GSE165nnn/GSE165082/suppl/GSE165082_PD-CC.counts.txt.gz; integrity: gzip_full_decompression |
| VERIFIED | inspection | GSE165082_series_matrix.txt.gz: geo_series_matrix (gzip), kind=metadata_only_series_matrix, rows=0, columns=27, candidate samples=26 | streamed file inspection |
| VERIFIED | processing | GSE165082_series_matrix.txt.gz: METADATA_ONLY (confidence HIGH) | table kind 'metadata_only_series_matrix' contains no expression values |
| VERIFIED | inspection | GSE165082_PD-CC.counts.txt.gz: delimited_text (gzip), kind=expression_matrix, rows=63677, columns=27, candidate samples=26 | streamed file inspection |
| UNRESOLVED | processing | GSE165082_PD-CC.counts.txt.gz: NON_NORMALIZED (confidence MEDIUM) | all values are non-negative integers (max 12835229): raw count-like data; per-sample distributions differ (max SD/IQR 0.430 at q25-q75): no between-sample distribution normalisation evident |
| VERIFIED | reconciliation | GSE165082_series_matrix.txt.gz: 26 expression IDs vs 26 phenotype records; 26 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO geo_accession |
| VERIFIED | reconciliation | GSE165082_PD-CC.counts.txt.gz: 26 expression IDs vs 26 phenotype records; 26 exact matches, 0 expression-only, 0 phenotype-only, 0/0 duplicated IDs | expression column/sample ID == GEO title |
| REPORTED | reported_lead | GSE165082-LEAD-1: GEO lists 26 samples whereas the study description refers to 30 participants. | BIO-MB-001 brief |
| VERIFIED | sample_count | GEO overall design text: "Parkinson's disease (PD) and control subjects where analyzed for changes in gene expression and DNA methylation. Each group contained 15 age-matched subjects. Two blood samples were taken from each subject. One sample was used for isolation of total RNA and the other was used for extraction of DNA. The PD group was compared to controls for each data type and correlations between data types were as" | GEO series record (quoted, not interpreted) |
| VERIFIED | modality | RNA-seq dataset: values are not on the same scale as microarray intensities and must never be pooled with them | configuration + GEO type |
## 10. Recommended next actions
1. Investigate the differences between observed and reported counts (see group-count table); no samples were removed or added to match reference values.
2. Lead GSE165082-LEAD-1: establish from the publication/authors why GEO sample numbers differ from the described participants; do not infer or impute missing samples.
3. Keep GSE165082 exploratory until its open discrepancies are explained.
4. Choose the downstream input file for this dataset only after reviewing the processing evidence: GSE165082_PD-CC.counts.txt.gz = NON_NORMALIZED (MEDIUM). Do not apply normalisation to data that is already normalised.
## 11. Run information
- Run ID: `20261009T140756Z-e178f3`
- Audit started/finished (UTC): 2026-10-09T14:09:03+00:00 / 2026-10-09T14:09:04+00:00
- Software: biomarker_project 0.1.0, Python 3.13.9, pandas 3.0.6, numpy 2.5.3, requests 2.34.2, PyYAML 6.0.3
- Config SHA-256: `c1438e0f29cc22fa51679dcaf7999ff599c01d97e4c77b656e244ebce8eb0d48`
- Command: `scripts/run_all_audits.py --offline`
