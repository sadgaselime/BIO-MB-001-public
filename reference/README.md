# Reference resources

Verified, version-pinned third-party reference files (annotation packages, identifier-history files)
used as inputs to annotation audits. GEO data are **not** stored here; they live in `data/`
(`data/README.md`), which is reserved for script-produced GEO files.

Rules:

- Files are stored byte-for-byte as served by the official source and made read-only (`chmod 444`).
- Each subdirectory has a `download_manifest.json` recording the source URL, retrieval time (UTC),
  server-reported size and date, local size, published checksum (if any), MD5 and SHA-256, and status.
- A file is never overwritten. A different version or a re-download with different bytes is added
  as a separate file and manifest entry.
- Packages here are **not installed** into the project R library; installation is a separate,
  approved step (renv).

| Directory | Contents |
|---|---|
| `bioconductor_3.23/` | Bioconductor 3.23 annotation source tarballs |
