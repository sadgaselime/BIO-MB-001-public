# Illumina platforms under Option A — input assessment (PROVISIONAL)

Recorded 2026-10-13. **Provisional; not reviewed or approved.** Option A was approved for GPL570 only;
its application to Illumina platforms must be evaluated and approved separately. No counts in this
file are probe-level Option A results.

## Platforms and candidate packages

| Cohort | Platform | Candidate annotation (Bioconductor 3.23) | Package Entrez snapshot | Feature-ID key (package) |
|---|---|---|---|---|
| GSE63060 | GPL6947, HumanHT-12 v3 | illuminaHumanv3.db 1.26.0 | 2015-Mar17 | `ILMN_` probe IDs (verified 2026-10-12) |
| GSE63061 | GPL10558, HumanHT-12 v4 | illuminaHumanv4.db 1.26.0 | 2015-Mar17 | `ILMN_` probe IDs (verified 2026-10-12) |
| GSE140829 | GPL15988, HumanHT-12 v4 (nuID) | lumiHumanIDMapping 1.10.1 (nuID → ILMN / Entrez) | not recorded (`REFSEQ VERSION` blank) | nuID; which manifest table applies is unverified; route is part of D19 (unresolved) |

## Inputs available in the project

- `reports/annotation_audit/ncbi_gene_history/v1/`: gene-level reconciliation of each package's
  historical Entrez IDs (View A, cutoff 20260318), with input-ID set hashes in the manifest.
- Gene-level View A context (from `v1/summary_counts.tsv`, not probe-level):

  | Package | Entrez IDs | Present in baseline | Replaced (successor in baseline) | No replacement | Unexplained |
  |---|---:|---:|---:|---:|---:|
  | illuminaHumanv3 | 20,011 | 19,913 | 45 | 53 | 0 |
  | illuminaHumanv4 | 21,748 | 21,602 | 59 | 87 | 0 |
  | lumi HT-12 v4 R2 | 30,500 | 23,331 | 1,344 | 5,824 (5,414 direct + 410 chain ends) | 1 (`653803`) |

## Missing inputs (probe-level Option A counts cannot be computed)

The package databases (probe → Entrez tables) are required. The verified copies were held in
session scratch storage, which was cleared; none is in `reference/`.

| File | Bytes | Published MD5 | Recorded SHA-256 | Official source |
|---|---:|---|---|---|
| `illuminaHumanv3.db_1.26.0.tar.gz` | 6,455,664 | `7d9e7534f0b60f0e3e7473e545ef373d` | `cea0c9cd155197154d57400cb3f18108e451cf26e714c39698d68e45cd503a1b` | `https://bioconductor.org/packages/3.23/data/annotation/src/contrib/illuminaHumanv3.db_1.26.0.tar.gz` |
| `illuminaHumanv4.db_1.26.0.tar.gz` | 6,705,381 | `42d554559ac0106dc71317ffaf466421` | `362848d6e78c7fa6206e1a4c68a4b68c1ea065267d550114837bc3b9d833ee85` | `https://bioconductor.org/packages/3.23/data/annotation/src/contrib/illuminaHumanv4.db_1.26.0.tar.gz` |
| `lumiHumanIDMapping_1.10.1.tar.gz` | 27,559,728 | `007e5aa2f1596cc08d888ba6dce7148a` | `6414e94a243eea6a126e582a68fadd41798bb5fccc03fcc99380a01f40634948` | `https://bioconductor.org/packages/3.23/data/annotation/src/contrib/lumiHumanIDMapping_1.10.1.tar.gz` |

Status: **stopped**. Re-downloading these files (and retaining them under `reference/bioconductor_3.23/`)
needs explicit approval. The GPL570 counting script (`scripts/annotation_gpl570_option_a_counts.py`)
could be generalized once the inputs exist; for GSE140829 the nuID route also depends on D19.

## Known differences from GPL570 to weigh before any approval

- Illumina probe-to-gene knowledge dates to 2015-Mar17 (older than GPL570's 2021-Apr14).
- For Illumina, the accession route resolved ~99% of single-gene probes on 2026-10-12 (v3: 29,294 of
  29,551; v4: 33,761 of 34,160), unlike GPL570; Option A is therefore not the only high-coverage route.
- The packages' ReMOAT re-annotation (sequence-based, undated) is an additional Illumina-only source.

## Update 2026-10-13 (inputs recovered; counts computed — still PROVISIONAL)

With PI approval the three tarballs were re-downloaded, verified (size, published MD5, recorded SHA-256;
identical bytes to the v1 copies) and retained read-only under `reference/bioconductor_3.23/`
(see its `download_manifest.json`). Provisional probe-level counts are in `v1/`
(`counts_manifest_PROVISIONAL.json`, produced by `scripts/annotation_illumina_option_a_counts.py`).
The "Missing inputs" and "Status: stopped" sections above describe the state before this update.
No Illumina mapping policy is approved; D19 is unchanged.
