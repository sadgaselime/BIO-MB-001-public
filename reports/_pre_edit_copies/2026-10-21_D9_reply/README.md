# BIO-MB-001: Reproducible blood transcriptomic signals of Alzheimer's disease

**Sadga Selime**, Independent researcher.

A fully pre-specified, decision-logged analysis of public whole-blood microarray data. It asks whether blood gene
expression patterns associated with Alzheimer's disease (AD) reproduce across cohorts, whether they are specific to AD
compared with Parkinson's disease, and whether they support a classifier that works on unseen cohorts.

> **Status (2026-10-21):** all analyses are complete and accepted. The manuscript draft is in `reports/manuscript/`.
> The statistical analysis plan is a proposed draft: each decision it governs was approved before its analysis, as
> recorded in its decision register. A query to the GSE63060 data owners (D9) is pending.

## Key findings

| Question | Result |
|---|---|
| **A. Discovery** (GSE63060, 145 AD / 60 controls) | 1,401 of 17,425 genes associated with AD at FDR < 0.05; robust across 14 pre-specified sensitivity analyses. A 200-gene signature, dominated by lower oxidative-phosphorylation and ribosomal gene expression, was locked before any other cohort was modelled. |
| **B. Replication** | GSE63061 (same consortium; possible participant overlap): strong consistency (one-sided p = 3 × 10⁻¹⁴). **GSE140829** (independence unverified): directional replication only, and weak (p = 0.0019; 43 of 200 genes). |
| **C. Specificity** (GSE99039, Parkinson's) | Idiopathic PD shift in the AD direction, +0.20 (p = 0.018; Holm-adjusted p = 0.053): **association not demonstrated, specificity not established.** |
| **D. Classifier** | Ridge model, leakage-controlled: AUROC **0.84** within the discovery cohort (permutation p = 0.005). The frozen model scored **0.77** in GSE63061 and **0.53 (chance)** in GSE140829. |
| **Cell composition** | The signature survives marker-based leukocyte adjustment in the discovery cohort. In GSE140829 and in idiopathic PD, adjustment removes most of the signal (post hoc analysis). |

**In one sentence:** a reproducible but modest group-level blood signal of AD that, outside the discovery cohort, is
largely accounted for by leukocyte composition, may be shared with Parkinson's disease, and does not support
individual-level classification in an external cohort.

Every number above comes from an accepted, code-identity-verified output; see [Where the results are](#where-the-results-are).

## Datasets and roles

| Accession | Role | Platform | Primary population (after approved exclusions) |
|---|---|---|---|
| GSE63060 | Discovery (AddNeuroMed batch 1) | Illumina HT-12 v3 (GPL6947) | 145 AD, 60 CTL |
| GSE63061 | Related-cohort consistency (AddNeuroMed batch 2): **not** independent validation | Illumina HT-12 v4 (GPL10558) | 139 AD, 133 CTL |
| GSE140829 | Replication; independence from AddNeuroMed unverified | Illumina HT-12 v4, nuID-keyed (GPL15988) | 201 AD, 248 CTL |
| GSE99039 | Parkinson's specificity | Affymetrix HG-U133 Plus 2 (GPL570) | IPD 197, GPD 40, GU 22, CONTROL 229 |
| GSE165082 / GSE165081 | Audited only (exploratory RNA-seq / methylation) | — | not analysed |

Dataset-specific settings are in [`config/datasets.yaml`](config/datasets.yaml).

## How the analysis is governed

- **Plan first.** The statistical analysis plan (`reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md`) and its
  decision brief record every choice and when it was approved. Changes made after results are labelled amendments or
  post hoc analyses.
- **Lock before validation.** The signature was locked (`reports/lock/GSE63060/v1`) before any other cohort's expression
  was modelled against diagnosis.
- **Approved exclusions only.** Each cohort's rule-applied exclusion list was approved before any expression model used it.
- **Code identity.** Each runner hashes its code, environment and inputs; checks that the executed code matches those
  hashes; computes its result twice and requires byte-identical output; and writes into a new, never-overwritten version
  folder. An output counts as accepted only if `code_identity.acceptance_problems` returns no problems.
- **Classifier hygiene.** The ML protocol was written and approved before any ML code read real data. Synthetic leakage
  tests ran first. The frozen model was applied once to each external cohort and never re-tuned.

## Setup (macOS)

Requirements: Python 3.13 and R 4.6.1, with Bioconductor 3.23 managed by renv.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

The exact Python environment is hash-pinned in `reports/environment/python_lock/v2/`. In R, run `renv::restore()` from
the project root; the pins include limma 3.68.5, statmod 1.5.2 and glmnet 5.1. Environment records are in
`reports/environment/`.

Run the tests. They use synthetic fixtures and need no GEO data; R-dependent tests skip if `Rscript` is missing:

```bash
.venv/bin/python -m pytest -q
```

## Reproducing the results

Raw GEO files are not versioned. Retrieve them with the audit tools below; every file is checked against the SHA-256 in
`data/raw/<GSE>/download_manifest.json`. The Bioconductor annotation archives in `reference/bioconductor_3.23/` are also
not versioned; their sources and hashes are listed in that folder's `download_manifest.json`.

Run every runner with the isolated project interpreter, for example
`.venv/bin/python -I scripts/<runner>.py --version vN`. Each runner refuses to run unless the approvals it depends on are
recorded in the plan and its input files match their hashes. To reproduce an existing result, write to a new version
(for example `--version v2`), because existing versions are never overwritten.

| Step | Runner(s) |
|---|---|
| Annotation | `annotation_illumina_a0_classification.py`, `c15_cohort_probe_presence.py`, `annotation_gpl570_option_a_counts.py`, `annotation_pin.py`, `annotation_gse140829_nuid.py` |
| Eligibility | `eligibility_gse63060.py [--accession GSE63061]`, `eligibility_gse140829.py`, `eligibility_gse99039.py` |
| Duplicate review and QC | `duplicate_review_c1_gse63060.py`, `qc_stage_a_gse63060.py`, `r8_diagnostics_gse63060.py`, `qc_stage_b_gse63060.py` (each with `--accession`) |
| Discovery and lock | `discovery_prep_gse63060.py`, `discovery_fit_gse63060.py`, `discovery_sensitivity_gse63060.py`, `signature_lock_gse63060.py` |
| Validation and specificity | `validation_gse63061.py`, `validation_gse140829.py`, `specificity_gse99039.py` |
| Classifier | `ml_gse63060.py`, then `ml_apply_gse63061.py` / `ml_apply_gse140829.py --ml-version v1` (each applies the model once) |
| Cell composition | `s11_cell_composition_gse63060.py`, `s11_ext.py` (post hoc) |

Each step's run report is in the matching `reports/**/run_logs_*/REPORT.md`.

## Where the results are

| Result | Folder |
|---|---|
| Discovery fit and sensitivity analyses | `reports/discovery/GSE63060/fit_v1`, `sensitivity_v1`, `s11_v1` |
| Locked signature | `reports/lock/GSE63060/v1` |
| Validation / replication | `reports/validation/GSE63061/v1`, `reports/validation/GSE140829/v1` |
| Specificity | `reports/specificity/GSE99039/v1` |
| Classifier | `reports/ml/GSE63060/v1`, `reports/ml/GSE63061_external/v1`, `reports/ml/GSE140829_external/v1` |
| Composition-adjusted (post hoc) | `reports/s11_ext/v1` |
| QC and approved exclusion lists | `reports/qc_stage_a/<GSE>/v1`, `reports/qc_stage_b/<GSE>/v1` |
| Manuscript | `reports/manuscript/MANUSCRIPT_DRAFT_v2.md` |
| Plan, decisions, briefs | `reports/phase3b/v7/`, `reports/planning/`, `reports/phase3b/amendments/` |

## Phase 1 audit tools (data retrieval)

The original Phase 1 tools retrieve GEO metadata and files with full provenance, inspect file formats by content, and
reconcile sample identifiers against GEO records. They never modify or pool data.

```bash
.venv/bin/python scripts/run_dataset_audit.py --accession GSE63060   # one dataset (network)
.venv/bin/python scripts/run_all_audits.py                          # all configured datasets
```

Options:
- `--offline`: audit only files already on disk.
- `--skip-downloads`: metadata only.
- `--refresh-metadata`: re-query GEO.
- `--max-download-mb N`: per-file size limit.
- `-v`: debug logging.

Raw files are never overwritten. Reports go to `reports/dataset_audit/`.

A synthetic end-to-end pipeline (simulated data only) is also kept:
`scripts/run_synthetic_pipeline.py --config config/synthetic_pipeline.yaml --verify-determinism`.

## Repository layout

```
config/                 dataset and synthetic-pipeline configuration
src/biomarker_project/  library: code identity, QC (R8 sex check, R9 outliers), limma backend, sample policy,
                        differential expression, Phase 1 retrieval and audit modules
scripts/                one lifecycle-governed runner per analysis step (see the table above)
R/                      limma, validation-statistics and glmnet engines (run through the pinned R environment)
tests/                  pytest suite (synthetic data only)
reference/              pinned reference manifests (MCP-counter marker list, CC0; Bioconductor archive hashes)
reports/                plan, decisions, every accepted output with its code-identity record, run reports, manuscript
data/                   download manifests only (raw data not versioned)
```

## Limitations

- Labels are as deposited. GSE63060 contains 44 control arrays with two-axis sex discordance, which are excluded by a
  pre-specified rule; the data-owner query is pending.
- GSE63061 may share participants with GSE63060. The independence of GSE140829 is unverified.
- Score magnitudes are not compared across cohorts. No equivalence margin was set, so AD specificity cannot be
  established.
- Cell composition is estimated from marker genes developed mainly for tissue; the external composition analysis is post hoc.
- Exploratory classifier only: not a diagnostic test, with no clinical or prospective validation.

## Acknowledgements

The analysis and code were developed with AI assistance (Anthropic's Claude) under the author's direction and review.
Data: GEO series GSE63060, GSE63061, GSE140829 and GSE99039, and their depositors.
