# BIO-MB-001 Phase 1 — dataset audit summary
Generated (UTC): 2026-10-09T14:09:05+00:00 from per-dataset reports on disk. Latest run: `20261009T140756Z-e178f3`.
> No dataset is labelled PASS. Every dataset still requires the scientific decisions listed below before any confirmatory analysis. Phase 1 performed no differential expression, feature selection, enrichment or modelling.
## Status by dataset
| accession | provisional role | audit status | GEO samples | observed groups (canonical) | requested files available | requested files NOT available | audited (UTC) |
|---|---|---|---|---|---|---|---|
| GSE63060 | provisional_primary_ad_discovery | COMPLETE_REVIEW_REQUIRED | 329 | AD=145, HC=104, MCI=80 | GSE63060_series_matrix.txt.gz, GSE63060_normalized.txt.gz, GSE63060_non-normalized.txt.gz, GSE63060_RAW.tar, filelist.txt |  | 2026-10-09T14:08:09+00:00 |
| GSE63061 | related_cohort_consistency_candidate | COMPLETE_REVIEW_REQUIRED | 388 | AD=139, AMBIGUOUS=6, HC=134, MCI=109 | GSE63061_series_matrix.txt.gz, GSE63061_normalized.txt.gz, GSE63061_non-normalized.txt.gz, GSE63061_RAW.tar, filelist.txt |  | 2026-10-09T14:08:20+00:00 |
| GSE140829 | potential_external_ad_validation | COMPLETE_REVIEW_REQUIRED | 587 | AD=204, HC=249, MCI=134 | GSE140829_series_matrix.txt.gz, GSE140829_final_normalized_data.txt.gz, GSE140829_raw_data.txt.gz |  | 2026-10-09T14:08:58+00:00 |
| GSE99039 | pd_neurodegeneration_specificity_candidate | INCOMPLETE | 558 | AMBIGUOUS=8, GENETIC_UNAFFECTED=22, HC=233, OTHER_NEURO=49, PD=205, PD_GENETIC=41 | GSE99039_series_matrix.txt.gz, filelist.txt | GSE99039_RAW.tar (SKIPPED_OFFLINE) | 2026-10-09T14:09:03+00:00 |
| GSE165082 | optional_exploratory_pd_rnaseq | COMPLETE_REVIEW_REQUIRED | 26 | HC=14, PD=12 | GSE165082_series_matrix.txt.gz, GSE165082_PD-CC.counts.txt.gz |  | 2026-10-09T14:09:04+00:00 |
| GSE165081 | optional_future_methylation_extension | COMPLETE_REVIEW_REQUIRED | 28 | HC=14, PD=14 | GSE165081_Sample_Sheet.PD-CN.csv.gz, GSE165081_detP.csv.gz, filelist.txt |  | 2026-10-09T14:09:05+00:00 |
## What is ready
- GSE63060: GEO sample metadata retrieved and parsed (329 records); phenotype table at data/processed/GSE63060/phenotype_table.tsv
- GSE63060: GSE63060_series_matrix.txt.gz retrieved (SHA-256 342421d07105…) and inspected
- GSE63060: GSE63060_normalized.txt.gz retrieved (SHA-256 3a0d9f03e0e2…) and inspected
- GSE63060: GSE63060_non-normalized.txt.gz retrieved (SHA-256 163acd963f21…) and inspected
- GSE63060: GSE63060_RAW.tar retrieved (SHA-256 021a8de0d406…) and inspected
- GSE63060: filelist.txt retrieved (SHA-256 4b55fd2c8d59…) and inspected
- GSE63061: GEO sample metadata retrieved and parsed (388 records); phenotype table at data/processed/GSE63061/phenotype_table.tsv
- GSE63061: GSE63061_series_matrix.txt.gz retrieved (SHA-256 c6de1af5bd36…) and inspected
- GSE63061: GSE63061_normalized.txt.gz retrieved (SHA-256 724407efd592…) and inspected
- GSE63061: GSE63061_non-normalized.txt.gz retrieved (SHA-256 a63663ed42b3…) and inspected
- GSE63061: GSE63061_RAW.tar retrieved (SHA-256 19dbc61b4da9…) and inspected
- GSE63061: filelist.txt retrieved (SHA-256 08f49ebd32f0…) and inspected
- GSE140829: GEO sample metadata retrieved and parsed (587 records); phenotype table at data/processed/GSE140829/phenotype_table.tsv
- GSE140829: GSE140829_series_matrix.txt.gz retrieved (SHA-256 be4f08a2cb01…) and inspected
- GSE140829: GSE140829_final_normalized_data.txt.gz retrieved (SHA-256 28613d74484a…) and inspected
- GSE140829: GSE140829_raw_data.txt.gz retrieved (SHA-256 de2ba7864b0c…) and inspected
- GSE99039: GEO sample metadata retrieved and parsed (558 records); phenotype table at data/processed/GSE99039/phenotype_table.tsv
- GSE99039: GSE99039_series_matrix.txt.gz retrieved (SHA-256 197b7272a8a5…) and inspected
- GSE99039: filelist.txt retrieved (SHA-256 7fb47f5f46cc…) and inspected
- GSE165082: GEO sample metadata retrieved and parsed (26 records); phenotype table at data/processed/GSE165082/phenotype_table.tsv
- GSE165082: GSE165082_series_matrix.txt.gz retrieved (SHA-256 16cd63f53761…) and inspected
- GSE165082: GSE165082_PD-CC.counts.txt.gz retrieved (SHA-256 d0912e66d0cf…) and inspected
- GSE165081: GEO sample metadata retrieved and parsed (28 records); phenotype table at data/processed/GSE165081/phenotype_table.tsv
- GSE165081: GSE165081_Sample_Sheet.PD-CN.csv.gz retrieved (SHA-256 3351a20ba021…) and inspected
- GSE165081: GSE165081_detP.csv.gz retrieved (SHA-256 4214d4bb77d2…) and inspected
- GSE165081: filelist.txt retrieved (SHA-256 f263292ee14c…) and inspected

## What failed or was not retrieved
- GSE99039: GSE99039_RAW.tar (SKIPPED_OFFLINE)

## Requires human or scientific review
- GSE63060 [high] GSE63060_normalized.txt.gz: 1 row(s) shorter than the header (values absent, counted as missing): line 30881 'ILMN_2315789' (1 fields)
- GSE63060 [high] GSE63060_non-normalized.txt.gz: 3 data column(s) with an empty header at positions [317, 323, 329]: values present but not attributable to any sample
- GSE63060 [high] GSE63060_normalized.txt.gz: not an exact one-to-one match with GEO records (1 expression-only, 0 phenotype-only, 0 duplicated expression IDs, 0 duplicated phenotype keys, 0 records without key)
- GSE63060 [high] GSE63060_non-normalized.txt.gz: not an exact one-to-one match with GEO records (1 expression-only, 3 phenotype-only, 0 duplicated expression IDs, 0 duplicated phenotype keys, 0 records without key)
- GSE63060 [medium] GSE63060_series_matrix.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review
- GSE63060 [medium] GSE63060_normalized.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review
- GSE63060 [medium] GSE63060_non-normalized.txt.gz: processing state NON_NORMALIZED (confidence MEDIUM) requires review
- GSE63060 [medium] GSE63060_RAW.tar: processing state METADATA_ONLY (confidence HIGH) requires review; content-based state METADATA_ONLY contradicts the file-name hint RAW_INSTRUMENT
- GSE63061 [medium] 6 sample(s) with ambiguous diagnosis label: {'borderline MCI': 3, 'OTHER': 1, 'CTL to AD': 1, 'MCI to CTL': 1}
- GSE63061 [medium] GSE63061_series_matrix.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review
- GSE63061 [medium] GSE63061_normalized.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review
- GSE63061 [medium] GSE63061_non-normalized.txt.gz: processing state NON_NORMALIZED (confidence MEDIUM) requires review
- GSE63061 [medium] GSE63061_RAW.tar: processing state METADATA_ONLY (confidence HIGH) requires review; content-based state METADATA_ONLY contradicts the file-name hint RAW_INSTRUMENT
- GSE140829 [medium] GSE140829_final_normalized_data.txt.gz: processing state PROCESSED_NORMALIZED (confidence MEDIUM) requires review
- GSE140829 [medium] GSE140829_raw_data.txt.gz: processing state NON_NORMALIZED (confidence HIGH) requires review; content-based state NON_NORMALIZED contradicts the file-name hint RAW_INSTRUMENT
- GSE140829 [medium] GSE140829_final_normalized_data.txt.gz: not an exact one-to-one match with GEO records (0 expression-only, 36 phenotype-only, 0 duplicated expression IDs, 0 duplicated phenotype keys, 0 records without key)
- GSE99039 [medium] 8 sample(s) with ambiguous diagnosis label: {'HD_HD_BATCH': 8}
- GSE99039 [medium] 8 sample(s) lack a participant ID in char:subject_id
- GSE99039 [medium] OTHER_NEURO: observed 49 vs reported 48 (difference +1)
- GSE99039 [medium] GSE99039_RAW.tar: SKIPPED_OFFLINE
- GSE165082 [medium] DESCRIBED_PARTICIPANTS: observed 26 vs reported 30 (difference -4)
- GSE165082 [medium] GSE165082_PD-CC.counts.txt.gz: processing state NON_NORMALIZED (confidence MEDIUM) requires review
- GSE165081 [high] GSE165081_detP.csv.gz: processing state UNKNOWN (confidence LOW) requires review; no content-based evidence; processing state cannot be established
- GSE165081 [medium] DESCRIBED_PARTICIPANTS: observed 28 vs reported 30 (difference -2)
- overlap check ADDNEUROMED-PARTICIPANT-CODES (GSE63060, GSE63061): NO_SHARED_IDENTIFIERS_FOUND — no identical values; this does NOT establish participant independence (identifiers may be coded differently between deposits)
- overlap check ADDNEUROMED-ARRAY-BARCODES (GSE63060, GSE63061): NO_SHARED_IDENTIFIERS_FOUND — no identical values; this does NOT establish participant independence (identifiers may be coded differently between deposits)
- overlap check AD-COHORTS-ARRAY-BARCODES (GSE63060, GSE63061, GSE140829): NO_SHARED_IDENTIFIERS_FOUND — no identical values; this does NOT establish participant independence (identifiers may be coded differently between deposits)
- overlap check PD-STUDY-RNA-VS-METHYLATION (GSE165082, GSE165081): POSSIBLE_OVERLAP_FLAGGED — GSE165082/GSE165081: 26 shared of [26, 28] (e.g. ['011', '012', '015', '016', '021'])

## Cross-dataset identifier checks (possible participant overlap)
| id | datasets | field | status | detail |
|---|---|---|---|---|
| ADDNEUROMED-PARTICIPANT-CODES | GSE63060, GSE63061 | description | NO_SHARED_IDENTIFIERS_FOUND | no identical values; this does NOT establish participant independence (identifiers may be coded differently between deposits) |
| ADDNEUROMED-ARRAY-BARCODES | GSE63060, GSE63061 | title | NO_SHARED_IDENTIFIERS_FOUND | no identical values; this does NOT establish participant independence (identifiers may be coded differently between deposits) |
| AD-COHORTS-ARRAY-BARCODES | GSE63060, GSE63061, GSE140829 | title ~ (\d+_[A-Z]) | NO_SHARED_IDENTIFIERS_FOUND | no identical values; this does NOT establish participant independence (identifiers may be coded differently between deposits) |
| PD-STUDY-RNA-VS-METHYLATION | GSE165082, GSE165081 | title ~ (\d{3}) | POSSIBLE_OVERLAP_FLAGGED | GSE165082/GSE165081: 26 shared of [26, 28] (e.g. ['011', '012', '015', '016', '021']) |

## Processing-state overview
| accession | file | state | confidence | requires_review |
|---|---|---|---|---|
| GSE63060 | GSE63060_series_matrix.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True |
| GSE63060 | GSE63060_normalized.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True |
| GSE63060 | GSE63060_non-normalized.txt.gz | NON_NORMALIZED | MEDIUM | True |
| GSE63060 | GSE63060_RAW.tar | METADATA_ONLY | HIGH | True |
| GSE63060 | filelist.txt | METADATA_ONLY | HIGH | False |
| GSE63061 | GSE63061_series_matrix.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True |
| GSE63061 | GSE63061_normalized.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True |
| GSE63061 | GSE63061_non-normalized.txt.gz | NON_NORMALIZED | MEDIUM | True |
| GSE63061 | GSE63061_RAW.tar | METADATA_ONLY | HIGH | True |
| GSE63061 | filelist.txt | METADATA_ONLY | HIGH | False |
| GSE140829 | GSE140829_series_matrix.txt.gz | PROCESSED_NORMALIZED | HIGH | False |
| GSE140829 | GSE140829_final_normalized_data.txt.gz | PROCESSED_NORMALIZED | MEDIUM | True |
| GSE140829 | GSE140829_raw_data.txt.gz | NON_NORMALIZED | HIGH | True |
| GSE99039 | GSE99039_series_matrix.txt.gz | PROCESSED_NORMALIZED | HIGH | False |
| GSE99039 | filelist.txt | METADATA_ONLY | HIGH | False |
| GSE99039 | GSE99039_RAW.tar | UNKNOWN | LOW | True |
| GSE165082 | GSE165082_series_matrix.txt.gz | METADATA_ONLY | HIGH | False |
| GSE165082 | GSE165082_PD-CC.counts.txt.gz | NON_NORMALIZED | MEDIUM | True |
| GSE165081 | GSE165081_Sample_Sheet.PD-CN.csv.gz | METADATA_ONLY | HIGH | False |
| GSE165081 | GSE165081_detP.csv.gz | UNKNOWN | LOW | True |
| GSE165081 | filelist.txt | METADATA_ONLY | HIGH | False |
