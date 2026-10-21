# About this repository

This is the public release of BIO-MB-001, a snapshot of the author's working repository taken on 2026-10-22 (source
commit f109f9b). It contains the analysis code, pinned environment records, the statistical analysis plan and decision
register, every accepted output with its code-identity record, the manuscript and the figures.

What is not included:

- Raw GEO data (never versioned). Retrieve it with the Phase 1 audit tools; each file is checked against the SHA-256 in
  `data/raw/<GSE>/download_manifest.json`.
- The Bioconductor annotation archives (sources and hashes are in `reference/bioconductor_3.23/download_manifest.json`).
- The working history, and one pre-edit backup folder (`reports/_pre_edit_copies/2026-10-22_D9_GEO_report`), which held
  a summary of private correspondence with a data depositor. The current decision register records that correspondence
  only as received, without its contents.
- A machine-specific note on the project's local folder location.

Author: Sadga Selime (independent researcher), sadgaselime@gmail.com. See `README.md` to reproduce the analysis and
`reports/manuscript/medrxiv/` for the manuscript.
