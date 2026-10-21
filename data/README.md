# Data directory

Nothing in this directory is edited by hand. Every file is produced by the audit
scripts and is traceable through a manifest.

| Directory | Contents | Mutability |
|---|---|---|
| `raw/<GSE>/` | GEO Series Matrix and supplementary files, byte-for-byte as served by GEO, plus `download_manifest.json` | **Immutable.** Completed files are made read-only (`chmod 444`). An existing file is never overwritten; a size/checksum mismatch is reported as `CONFLICT_EXISTING_FILE_DIFFERS` and left for a human. |
| `metadata/<GSE>/` | GEO SOFT "brief" snapshots of the series record, all sample (GSM) records and the platform record(s), the GEO directory listing, and `retrieval_manifest.json` | **Immutable snapshots.** `--refresh-metadata` re-queries GEO; an identical response is discarded and a changed response is saved as a new timestamped snapshot. Older snapshots are kept. |
| `processed/<GSE>/` | `phenotype_table.tsv`: one row per GSM record with original GEO values preserved and `diagnosis_canonical` / `diagnosis_status` columns added from the configured label map | Derived and regenerated on every run. No expression values are ever written here in Phase 1. |

Manifests record, for every retrieval attempt: source URL, start/finish time (UTC),
server-reported size, local size, SHA-256, integrity check (full gzip decompression
or tar member listing), status, and notes. `history` keeps every attempt; `current`
is the latest.

## Retrieval status vocabulary

`DOWNLOADED`, `REUSED_VERIFIED` (size matches the server; checksum matches the manifest
if one was recorded), `REUSED_VERIFIED_AGAINST_MANIFEST` (offline; checksum matches an
earlier record), `REUSED_UNVERIFIED`, `SKIPPED_TOO_LARGE`, `SKIPPED_NOT_REQUESTED`,
`SKIPPED_OFFLINE`, `FAILED`, `FAILED_NOT_FOUND`, `FAILED_SIZE_MISMATCH`,
`FAILED_INTEGRITY`, `CONFLICT_EXISTING_FILE_DIFFERS`.

Partial downloads are kept as `<name>.part` and resumed with HTTP Range requests on
the next run. Files that fail integrity checks are moved to `<name>.corrupt-<timestamp>`.

## Data use

All datasets are public GEO records. Check each series' GEO page and the original
publications for citation requirements before publishing results. Do not add
controlled-access or identifiable participant data to this repository.
