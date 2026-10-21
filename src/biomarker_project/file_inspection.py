"""Read-only inspection of downloaded files.

Supported: GEO Series Matrix files, delimited text tables (TSV/CSV; plain or gzip),
GEO 'filelist.txt' manifests, Illumina sample sheets, and tar archives (member
listing only - nothing is extracted).

Design notes
  * Files are streamed. A first pass counts lines and checks field counts; a
    second, chunked pandas pass computes value summaries. Only a deterministic
    subsample of rows (every k-th row) is held in memory for distribution checks.
  * Headers are parsed by this module (csv module), not by pandas, so duplicate
    column names are reported verbatim instead of being silently renamed.
  * A column is a *candidate sample column* only if it is numeric in the data and
    is not the feature-ID column or a known annotation column. Illumina
    GenomeStudio measurement suffixes (e.g. '.AVG_Signal', '.Detection Pval') are
    recognised and the sample ID is derived from the prefix; the original column
    name is always preserved alongside the derived ID.
  * Nothing is written back to the inspected file.
"""
from __future__ import annotations

import csv
import gzip
import io
import logging
import math
import re
import tarfile
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# Inspection status vocabulary
INSPECTED = "INSPECTED"
INSPECTED_WITH_LIMITATIONS = "INSPECTED_WITH_LIMITATIONS"
MALFORMED = "MALFORMED"
EMPTY = "EMPTY"
UNSUPPORTED = "UNSUPPORTED"
FAILED = "FAILED"
USABLE_STATUSES = {INSPECTED, INSPECTED_WITH_LIMITATIONS}

KNOWN_FEATURE_ID_HEADERS = {
    "", "ID_REF", "IND_ID", "ID", "PROBE_ID", "PROBEID", "PROBE", "PROBESET_ID", "PROBESETID",
    "GENEID", "GENE_ID", "GENE", "SYMBOL", "TARGETID", "ILMN_ID", "ENSEMBL_ID", "FEATURE_ID",
}
# Numeric columns that describe features rather than samples (e.g. featureCounts output).
KNOWN_NUMERIC_ANNOTATION_HEADERS = {"LENGTH", "START", "END", "CHR", "CHROMOSOME", "STRAND", "GC", "PROBE_START"}
# Illumina GenomeStudio per-sample measurement suffixes -> canonical measurement names.
_MEASURES = [
    (re.compile(r"^avg[_ ]?signal$", re.I), "signal"),
    (re.compile(r"^detection[ _.]?p[_ -]?val(ue)?$", re.I), "detection_pval"),
    (re.compile(r"^detection$", re.I), "detection_pval"),
    (re.compile(r"^bead[_ ]?stderr$", re.I), "bead_stderr"),
    (re.compile(r"^avg[_ ]?nbeads$", re.I), "n_beads"),
]
_SUFFIXED = re.compile(r"^(?P<sample>.+?)[._ ](?P<measure>AVG_Signal|AVG Signal|Detection[ _.]?P[_ -]?val(?:ue)?|Detection|BEAD_STDERR|AVG_NBEADS)$", re.I)
PRIMARY_MEASURES = ("signal", "value")
SAMPLE_SHEET_MARKERS = {"Sample_Name"}
SAMPLE_SHEET_SUPPORT = {"Sentrix_ID", "Sentrix_Position", "Sample_Group", "Sample_Plate", "Sample_Well"}
NA_TOKENS = ["", "NA", "N/A", "NaN", "nan", "null", "NULL", "#N/A", "-"]
# GEO submitter contact fields (names, emails, postal addresses) are not needed for the audit and are
# left out of generated reports; they remain available in the downloaded GEO files themselves.
_CONTACT_FIELD = re.compile(r"^(Series|Sample)_contact_", re.I)


@dataclass
class InspectionResult:
    path: str
    file_name: str
    status: str
    format: str = "unknown"
    compression: str = "none"
    size_bytes: int | None = None
    n_rows: int | None = None            # data rows (excluding header/comments)
    n_columns: int | None = None
    delimiter: str | None = None
    header_line_number: int | None = None
    feature_id_column: str | None = None
    annotation_columns: list[str] = field(default_factory=list)
    sample_columns: list[dict[str, str]] = field(default_factory=list)  # {column, sample_id, measure, derivation}
    candidate_sample_ids: list[str] = field(default_factory=list)       # unique, first-seen order
    measurement_types: dict[str, int] = field(default_factory=dict)
    duplicate_column_headers: list[str] = field(default_factory=list)
    empty_header_sample_columns: list[int] = field(default_factory=list)  # 1-based positions of data columns without a header
    duplicate_sample_ids: list[str] = field(default_factory=list)
    n_unique_feature_ids: int | None = None
    duplicate_feature_ids: dict[str, Any] = field(default_factory=dict)
    missing_feature_ids: int | None = None
    missing_values: dict[str, Any] = field(default_factory=dict)
    value_summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    table_kind: str | None = None        # expression_matrix | sample_sheet | file_manifest | archive | ...
    limitations: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def usable(self) -> bool:
        return self.status in USABLE_STATUSES


class InspectionError(RuntimeError):
    pass


# ----------------------------------------------------------------- utilities
def _open_text(path: Path, compression: str) -> io.TextIOBase:
    raw = gzip.open(path, "rb") if compression == "gzip" else open(path, "rb")
    return io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")


def _magic(path: Path, n: int = 512) -> bytes:
    with open(path, "rb") as fh:
        return fh.read(n)


def _peek_text(path: Path, compression: str, n_bytes: int = 65536) -> str:
    with _open_text(path, compression) as fh:
        return fh.read(n_bytes)


def detect_format(path: Path) -> tuple[str, str]:
    """Return (format, compression) using content, not the file name."""
    path = Path(path)
    if path.stat().st_size == 0:
        return "empty", "none"
    head = _magic(path)
    compression = "none"
    if head[:2] == b"\x1f\x8b":
        compression = "gzip"
        try:
            with gzip.open(path, "rb") as gz:
                head = gz.read(4096)
        except (OSError, EOFError) as exc:
            raise InspectionError(f"gzip stream could not be read: {exc}") from exc
        if not head.strip():
            return "empty", compression
    elif tarfile.is_tarfile(path):
        return "tar_archive", "none"
    if b"\x00" in head:
        return "binary_unknown", compression
    text = head.decode("utf-8", errors="replace").lstrip("﻿")
    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    if not first.strip():
        return "empty", compression
    if first.startswith("!Series_") or first.startswith("!series_"):
        return "geo_series_matrix", compression
    if first.startswith("^"):
        return "geo_soft_text", compression
    if first.startswith("#Archive/File"):
        return "geo_filelist", compression
    return "delimited_text", compression


def _sniff_delimiter(lines: list[str]) -> str | None:
    best, best_score = None, 0
    for delim in ("\t", ",", ";"):
        counts = [ln.count(delim) for ln in lines if ln.strip()]
        if not counts or counts[0] == 0:
            continue
        consistent = sum(1 for c in counts if c == counts[0]) / len(counts)
        score = counts[0] * consistent
        if score > best_score:
            best, best_score = delim, score
    return best


def _field_count(line: str, delim: str) -> int:
    if '"' in line:
        return len(next(csv.reader([line], delimiter=delim)))
    return line.count(delim) + 1


def classify_measure(column: str) -> tuple[str, str, str]:
    """Return (sample_id, measure, derivation) for a numeric column header.

    'derivation' documents how the sample ID was obtained so it can be audited.
    """
    m = _SUFFIXED.match(column)
    if m:
        measure_raw = m.group("measure")
        for rx, canonical in _MEASURES:
            if rx.match(measure_raw):
                return m.group("sample"), canonical, f"stripped GenomeStudio suffix {column[len(m.group('sample')):]!r}"
    return column, "value", "column header used verbatim"


def _is_numeric_series(values: pd.Series, threshold: float = 0.95) -> tuple[bool, int]:
    nonnull = values.dropna()
    nonnull = nonnull[~nonnull.astype(str).str.strip().isin(NA_TOKENS)]
    if nonnull.empty:
        return False, 0
    parsed = pd.to_numeric(nonnull, errors="coerce")
    ok = int(parsed.notna().sum())
    return ok / len(nonnull) >= threshold, len(nonnull)


# ------------------------------------------------------------- value summary
class _ValueAccumulator:
    """Streaming summary of numeric sample columns plus a deterministic row subsample."""

    def __init__(self, sample_cols: list[str], every_k: int, max_rows: int):
        self.cols = sample_cols
        self.every_k = max(1, every_k)
        self.max_rows = max_rows
        self.n_values = 0
        self.n_missing = 0
        self.n_non_numeric = 0
        self.n_negative = 0
        self.n_zero = 0
        self.n_non_integer = 0
        self.vmin = math.inf
        self.vmax = -math.inf
        self.missing_by_col: Counter = Counter()
        self.sampled: list[np.ndarray] = []
        self.rows_seen = 0

    def add(self, chunk: pd.DataFrame) -> None:
        block = chunk[self.cols]
        before_na = block.isna()
        # dtype-agnostic (pandas 2 'object' and pandas 3 'str' columns both need coercion)
        if all(pd.api.types.is_numeric_dtype(t) for t in block.dtypes):
            numeric = block
        else:
            numeric = block.apply(pd.to_numeric, errors="coerce")
        after_na = numeric.isna()
        self.n_non_numeric += int((after_na & ~before_na).to_numpy().sum())
        self.missing_by_col.update({c: int(v) for c, v in before_na.sum().items() if v})
        arr = numeric.to_numpy(dtype=float)
        finite = np.isfinite(arr)
        vals = arr[finite]
        self.n_missing += int(before_na.to_numpy().sum())
        self.n_values += int(vals.size)
        if vals.size:
            self.vmin = min(self.vmin, float(vals.min()))
            self.vmax = max(self.vmax, float(vals.max()))
            self.n_negative += int((vals < 0).sum())
            self.n_zero += int((vals == 0).sum())
            self.n_non_integer += int((vals != np.floor(vals)).sum())
        idx = np.arange(self.rows_seen, self.rows_seen + len(arr))
        keep = (idx % self.every_k) == 0
        if keep.any() and sum(len(s) for s in self.sampled) < self.max_rows:
            self.sampled.append(arr[keep])
        self.rows_seen += len(arr)

    def summary(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "columns_summarised": len(self.cols),
            "n_numeric_values": self.n_values,
            "n_missing_values": self.n_missing,
            "n_non_numeric_tokens": self.n_non_numeric,
        }
        if self.n_values == 0:
            return out
        out.update({
            "min": self.vmin,
            "max": self.vmax,
            "fraction_negative": self.n_negative / self.n_values,
            "fraction_zero": self.n_zero / self.n_values,
            "fraction_integer_valued": 1 - self.n_non_integer / self.n_values,
        })
        if self.sampled:
            mat = np.vstack(self.sampled)
            out["sampled_rows"] = int(mat.shape[0])
            out["sampling"] = f"every {self.every_k}th data row (deterministic)"
            pooled = mat[np.isfinite(mat)]
            qs = [0.0, 0.01, 0.25, 0.5, 0.75, 0.99, 1.0]
            if pooled.size:
                out["pooled_quantiles_sampled"] = {str(q): float(np.quantile(pooled, q)) for q in qs}
            if mat.shape[1] >= 2 and mat.shape[0] >= 20:
                with np.errstate(all="ignore"):
                    per_col_q = np.nanquantile(mat, [0.05, 0.25, 0.5, 0.75, 0.95], axis=0)
                iqr = float(np.quantile(pooled, 0.75) - np.quantile(pooled, 0.25)) if pooled.size else float("nan")
                sd_across = np.nanstd(per_col_q, axis=1)
                medians = per_col_q[2]
                out["per_sample_distribution"] = {
                    "median_of_sample_medians": float(np.nanmedian(medians)),
                    "range_of_sample_medians": [float(np.nanmin(medians)), float(np.nanmax(medians))],
                    "sd_of_sample_quantiles_over_pooled_iqr": (
                        {q: float(s / iqr) for q, s in zip(["q05", "q25", "q50", "q75", "q95"], sd_across)}
                        if iqr and np.isfinite(iqr) and iqr > 0 else None
                    ),
                    "note": "computed on sampled rows only; small values indicate near-identical per-sample distributions",
                }
        return out


# ------------------------------------------------------------ main entry point
def inspect_file(path: str | Path, sample_rows: int = 5000) -> InspectionResult:
    path = Path(path)
    res = InspectionResult(path=str(path), file_name=path.name, status=FAILED)
    try:
        if not path.exists():
            res.error = "file does not exist"
            return res
        res.size_bytes = path.stat().st_size
        fmt, comp = detect_format(path)
        res.format, res.compression = fmt, comp
        if fmt == "empty":
            res.status, res.error = EMPTY, "file is empty (no content after decompression)"
        elif fmt == "tar_archive":
            _inspect_tar(path, res)
        elif fmt == "geo_series_matrix":
            _inspect_series_matrix(path, res, sample_rows)
        elif fmt == "geo_filelist":
            _inspect_filelist(path, res)
        elif fmt == "delimited_text":
            _inspect_delimited(path, res, sample_rows)
        else:
            res.status, res.error = UNSUPPORTED, f"format {fmt!r} is not supported for inspection"
    except InspectionError as exc:
        res.status, res.error = FAILED, str(exc)
    except Exception as exc:  # defensive: an inspection must never crash the audit
        log.exception("Inspection of %s failed", path)
        res.status, res.error = FAILED, f"{type(exc).__name__}: {exc}"
    if res.status == INSPECTED and res.limitations:
        res.status = INSPECTED_WITH_LIMITATIONS
    return res


# -------------------------------------------------------------------- tar
def _inspect_tar(path: Path, res: InspectionResult) -> None:
    with tarfile.open(path, "r:") as tf:
        members = tf.getmembers()
    res.table_kind = "archive"
    listing, ext_counts, unsafe = [], Counter(), []
    for m in members:
        name = m.name
        if name.startswith("/") or ".." in Path(name).parts:
            unsafe.append(name)
        lower = name.lower()
        for suffix in (".gz", ".bz2", ".zip"):
            if lower.endswith(suffix):
                lower = lower[: -len(suffix)]
        ext = Path(lower).suffix or "(none)"
        ext_counts[ext] += 1
        listing.append({"name": name, "size": m.size, "type": "file" if m.isfile() else "other"})
    res.n_rows = len(members)
    res.metadata = {"members": listing[:500], "n_members": len(members), "extension_counts": dict(ext_counts),
                    "members_truncated": len(listing) > 500}
    if unsafe:
        res.limitations.append(f"archive contains unsafe member paths (never extract blindly): {unsafe[:5]}")
    res.limitations.append("archive members listed only; contents not extracted or inspected")
    res.status = INSPECTED


def _inspect_filelist(path: Path, res: InspectionResult) -> None:
    with _open_text(path, res.compression) as fh:
        rows = list(csv.reader(fh, delimiter="\t"))
    header, body = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]
    res.table_kind = "file_manifest"
    res.delimiter = "\t"
    res.n_rows, res.n_columns = len(body), len(header)
    entries = [dict(zip([h.lstrip("#") for h in header], r)) for r in body]
    res.metadata = {"entries": entries[:1000], "n_entries": len(entries),
                    "type_counts": dict(Counter(e.get("Type", "?") for e in entries))}
    res.status = INSPECTED


# ------------------------------------------------------------ series matrix
def _split_matrix_line(line: str) -> list[str]:
    return next(csv.reader([line.rstrip("\r\n")], delimiter="\t", quotechar='"'))


def _inspect_series_matrix(path: Path, res: InspectionResult, sample_rows: int) -> None:
    series_meta: dict[str, list[str]] = {}
    sample_meta: dict[str, list[list[str]]] = {}
    begin_line = end_line = header = None
    n_table_rows = 0
    bad_rows: list[int] = []
    with _open_text(path, res.compression) as fh:
        for lineno, line in enumerate(fh, start=1):
            if begin_line is None:
                if line.startswith("!series_matrix_table_begin"):
                    begin_line = lineno
                elif line.startswith("!Series_"):
                    key, *vals = _split_matrix_line(line)
                    series_meta.setdefault(key[1:], []).append("\t".join(vals))
                elif line.startswith("!Sample_"):
                    key, *vals = _split_matrix_line(line)
                    sample_meta.setdefault(key[1:], []).append(vals)
                continue
            if end_line is not None:
                continue
            if line.startswith("!series_matrix_table_end"):
                end_line = lineno
                continue
            if header is None:
                header = _split_matrix_line(line)
                continue
            if not line.strip():
                continue
            n_table_rows += 1
            if _field_count(line.rstrip("\r\n"), "\t") != len(header) and len(bad_rows) < 20:
                bad_rows.append(lineno)

    res.delimiter = "\t"
    gsm_ids = (sample_meta.get("Sample_geo_accession") or [[]])[0]
    res.metadata = {
        "series": {k: v for k, v in series_meta.items() if not _CONTACT_FIELD.match(k)},
        "omitted_contact_fields": sorted(k for k in series_meta if _CONTACT_FIELD.match(k)),
        "sample_fields": sorted(sample_meta),
        "sample_geo_accession": gsm_ids,
        "sample_title": (sample_meta.get("Sample_title") or [[]])[0],
        "sample_data_processing": sorted({v for row in sample_meta.get("Sample_data_processing", []) for v in row}),
        "sample_characteristics_rows": len(sample_meta.get("Sample_characteristics_ch1", [])),
        "sample_platform_id": sorted({v for row in sample_meta.get("Sample_platform_id", []) for v in row}),
        "table_begin_line": begin_line,
        "table_end_line": end_line,
    }
    if begin_line is None:
        res.status, res.error = MALFORMED, "no '!series_matrix_table_begin' marker found"
        return
    if end_line is None:
        res.limitations.append("no '!series_matrix_table_end' marker: file may be truncated")
    if header is None:
        res.status, res.error = MALFORMED, "table section has no header row"
        return
    res.header_line_number = begin_line + 1
    res.n_columns = len(header)
    res.n_rows = n_table_rows
    res.feature_id_column = header[0]
    sample_cols = header[1:]
    res.duplicate_column_headers = sorted(c for c, n in Counter(header).items() if n > 1)
    res.sample_columns = [{"column": c, "column_index": i, "sample_id": c, "measure": "value",
                           "derivation": "series-matrix column header (GSM accession)"}
                          for i, c in enumerate(sample_cols, start=1)]
    res.candidate_sample_ids = list(dict.fromkeys(sample_cols))
    res.duplicate_sample_ids = sorted(c for c, n in Counter(sample_cols).items() if n > 1)
    res.measurement_types = {"value": len(sample_cols)}
    res.metadata["header_matches_sample_geo_accession"] = list(sample_cols) == list(gsm_ids)
    if gsm_ids and set(sample_cols) != set(gsm_ids):
        res.limitations.append("table column headers differ from the !Sample_geo_accession header line")
    if bad_rows:
        res.status = MALFORMED
        res.error = f"rows with a field count different from the header (first lines: {bad_rows})"
        return
    res.table_kind = "expression_matrix" if n_table_rows else "metadata_only_series_matrix"
    if n_table_rows == 0:
        res.limitations.append("series matrix contains no data rows (metadata only)")
        res.status = INSPECTED
        return
    _stream_values(path, res, skiprows=begin_line + 1, nrows=n_table_rows, ncols=len(header),
                   feature_idx=0, sample_idx=list(range(1, len(header))), labels=sample_cols,
                   sample_rows=sample_rows, quotechar='"')
    res.status = INSPECTED


# ---------------------------------------------------------------- delimited
def _inspect_delimited(path: Path, res: InspectionResult, sample_rows: int) -> None:
    head_lines: list[str] = []
    comment_lines = 0
    with _open_text(path, res.compression) as fh:
        for line in fh:
            if not head_lines and (line.startswith("#") or not line.strip()):
                comment_lines += 1
                continue
            head_lines.append(line.rstrip("\r\n"))
            if len(head_lines) >= 50:
                break
    if not head_lines:
        res.status, res.error = EMPTY, "no header or data lines found"
        return
    delim = _sniff_delimiter(head_lines)
    if delim is None:
        res.status, res.error = MALFORMED, "could not determine a column delimiter (tab, comma or semicolon)"
        return
    res.delimiter = delim
    header = next(csv.reader([head_lines[0]], delimiter=delim))
    res.header_line_number = comment_lines + 1
    res.n_columns = len(header)
    res.duplicate_column_headers = sorted(c for c, n in Counter(header).items() if n > 1)
    if comment_lines:
        res.metadata["leading_comment_or_blank_lines"] = comment_lines

    # Pass 1: count rows and check field counts (streaming).
    n_rows, long_rows, short_rows, n_short, n_long, blank = 0, [], [], 0, 0, 0
    with _open_text(path, res.compression) as fh:
        for lineno, line in enumerate(fh, start=1):
            if lineno <= comment_lines + 1:
                continue
            stripped = line.rstrip("\r\n")
            if not stripped.strip():
                blank += 1
                continue
            n_rows += 1
            nf = _field_count(stripped, delim)
            if nf > len(header):
                n_long += 1
                if len(long_rows) < 20:
                    long_rows.append(lineno)
            elif nf < len(header):
                n_short += 1
                if len(short_rows) < 50:
                    short_rows.append({"line": lineno, "n_fields": nf,
                                       "first_field": next(csv.reader([stripped], delimiter=delim))[0]})
    res.n_rows = n_rows
    if blank:
        res.limitations.append(f"{blank} blank line(s) inside the table were ignored")
    if n_long:
        # Extra fields cannot be assigned to columns safely: refuse to interpret values.
        res.metadata["n_rows_with_too_many_fields"] = n_long
        res.status = MALFORMED
        res.error = (f"{n_long} row(s) have more fields than the header ({len(header)}); first offending lines: "
                     f"{long_rows}")
        return
    if n_short:
        # Short rows are kept, their absent fields counted as missing, and every one is reported.
        res.metadata["n_rows_with_too_few_fields"] = n_short
        res.metadata["rows_with_too_few_fields"] = short_rows
        res.limitations.append(
            f"{n_short} row(s) have fewer fields than the header ({len(header)}); their absent values are counted "
            f"as missing, not imputed. Rows (line, fields, first field): "
            + "; ".join(f"{r['line']}, {r['n_fields']}, {r['first_field']!r}" for r in short_rows[:10]))
    if n_rows == 0:
        res.status = INSPECTED
        res.table_kind = "header_only"
        res.limitations.append("table has a header but no data rows")
        return

    # Column classification on the first rows.
    probe = pd.read_csv(path, sep=delim, header=None, skiprows=comment_lines + 1, nrows=min(500, n_rows),
                        names=list(range(len(header))), index_col=False, dtype=str, keep_default_na=False,
                        compression="gzip" if res.compression == "gzip" else None, encoding="utf-8-sig",
                        encoding_errors="replace")
    numeric_cols, nonnumeric_cols, empty_cols = [], [], []
    for i in range(len(header)):
        col = probe[i].where(~probe[i].str.strip().isin(NA_TOKENS))
        is_num, n_nonnull = _is_numeric_series(col)
        if n_nonnull == 0:
            empty_cols.append(i)
        elif is_num:
            numeric_cols.append(i)
        else:
            nonnumeric_cols.append(i)

    # Sample sheet? (rows are samples, not features)
    if SAMPLE_SHEET_MARKERS <= set(header) and SAMPLE_SHEET_SUPPORT & set(header):
        _describe_sample_sheet(path, res, header, delim, comment_lines)
        return

    feature_idx = None
    if header[0].strip().upper() in KNOWN_FEATURE_ID_HEADERS or 0 in nonnumeric_cols:
        feature_idx = 0
    elif nonnumeric_cols:
        feature_idx = nonnumeric_cols[0]
        res.limitations.append(f"feature-ID column is not the first column; using {header[feature_idx]!r}")
    else:
        res.limitations.append("no non-numeric identifier column found; rows have no feature IDs")
    res.feature_id_column = header[feature_idx] if feature_idx is not None else None
    res.metadata["feature_id_column_index"] = feature_idx
    annotation = [i for i in nonnumeric_cols if i != feature_idx]
    sample_idx = []
    for i in numeric_cols:
        if i == feature_idx:
            continue
        if header[i].strip().upper() in KNOWN_NUMERIC_ANNOTATION_HEADERS:
            annotation.append(i)
        else:
            sample_idx.append(i)
    res.annotation_columns = [header[i] for i in sorted(annotation)]
    if empty_cols:
        res.limitations.append(f"{len(empty_cols)} column(s) empty in the first {min(500, n_rows)} rows: "
                               f"{[header[i] for i in empty_cols][:10]}")

    # Map measurement columns to sample IDs (positional index kept, so duplicate headers are safe).
    sample_columns, last_sample = [], None
    for i in sample_idx:
        col = header[i]
        sid, measure, how = classify_measure(col)
        if measure == "value" and any(rx.match(col.strip()) for rx, _ in _MEASURES):
            # A bare measurement header such as 'Detection Pval' that follows a sample column.
            if last_sample is None:
                res.limitations.append(f"measurement column {col!r} (index {i}) has no preceding sample column")
                continue
            measure = next(canon for rx, canon in _MEASURES if rx.match(col.strip()))
            sid, how = last_sample, f"bare measurement column assigned to preceding sample column {last_sample!r}"
        if measure in PRIMARY_MEASURES:
            last_sample = sid
        sample_columns.append({"column": col, "column_index": i, "sample_id": sid, "measure": measure,
                               "derivation": how})
    res.sample_columns = sample_columns
    res.empty_header_sample_columns = [c["column_index"] + 1 for c in sample_columns if not c["column"].strip()]
    if res.empty_header_sample_columns:
        res.limitations.append(f"{len(res.empty_header_sample_columns)} numeric data column(s) have an EMPTY header (1-based "
                               f"positions {res.empty_header_sample_columns}); their values cannot be linked to a sample")
    res.measurement_types = dict(Counter(c["measure"] for c in sample_columns))
    primary = [c for c in sample_columns if c["measure"] in PRIMARY_MEASURES]
    res.candidate_sample_ids = list(dict.fromkeys(c["sample_id"] for c in primary))
    res.duplicate_sample_ids = sorted(s for s, n in Counter(c["sample_id"] for c in primary).items() if n > 1)
    if not primary:
        res.table_kind = "table_without_sample_columns"
        res.limitations.append("no numeric sample columns detected")
        res.status = INSPECTED
        return
    res.table_kind = "expression_matrix"
    primary_idx = [c["column_index"] for c in primary]
    _stream_values(path, res, skiprows=comment_lines + 1, nrows=n_rows, ncols=len(header),
                   feature_idx=feature_idx, sample_idx=primary_idx, labels=[c["column"] for c in primary],
                   sample_rows=sample_rows, quotechar='"', delim=delim)
    res.status = INSPECTED


def _describe_sample_sheet(path: Path, res: InspectionResult, header: list[str], delim: str, comment_lines: int) -> None:
    df = pd.read_csv(path, sep=delim, header=None, skiprows=comment_lines + 1, names=header, dtype=str,
                     keep_default_na=False, index_col=False,
                     compression="gzip" if res.compression == "gzip" else None, encoding="utf-8-sig")
    res.table_kind = "sample_sheet"
    res.feature_id_column = None
    ids = df["Sample_Name"].tolist()
    res.metadata["sample_sheet"] = {
        "sample_names": ids,
        "duplicate_sample_names": sorted(s for s, n in Counter(ids).items() if n > 1),
        "columns": header,
        "group_counts": dict(Counter(df["Sample_Group"])) if "Sample_Group" in df else None,
        "records": df.to_dict(orient="records"),
    }
    res.candidate_sample_ids = list(dict.fromkeys(ids))
    res.duplicate_sample_ids = res.metadata["sample_sheet"]["duplicate_sample_names"]
    res.limitations.append("sample sheet: rows are samples (phenotype-side information), not expression values")
    res.status = INSPECTED


def _stream_values(path: Path, res: InspectionResult, skiprows: int, nrows: int, ncols: int,
                   feature_idx: int | None, sample_idx: list[int], labels: list[str], sample_rows: int,
                   quotechar: str = '"', delim: str = "\t", chunksize: int = 2000) -> None:
    every_k = max(1, nrows // max(1, sample_rows))
    acc = _ValueAccumulator(sample_idx, every_k, sample_rows)
    ids: Counter = Counter()
    missing_ids = 0
    dtype = {feature_idx: str} if feature_idx is not None else None
    reader = pd.read_csv(path, sep=delim, header=None, skiprows=skiprows, nrows=nrows, names=list(range(ncols)),
                         index_col=False, quotechar=quotechar, chunksize=chunksize, dtype=dtype,
                         na_values=NA_TOKENS, keep_default_na=False, low_memory=False,
                         compression="gzip" if res.compression == "gzip" else None,
                         encoding="utf-8-sig", encoding_errors="replace", skip_blank_lines=True)
    for chunk in reader:
        if feature_idx is not None:
            col = chunk[feature_idx]
            missing_ids += int(col.isna().sum())
            ids.update(col.dropna().tolist())
        acc.add(chunk)
    if feature_idx is not None:
        dups = {k: n for k, n in ids.items() if n > 1}
        res.n_unique_feature_ids = len(ids)
        res.missing_feature_ids = missing_ids
        res.duplicate_feature_ids = {"n_duplicated_ids": len(dups), "n_rows_involved": sum(dups.values()),
                                     "examples": dict(sorted(dups.items())[:20])}
    summary = acc.summary()
    missing_by = acc.missing_by_col
    header_lookup = dict(zip(sample_idx, labels))
    res.missing_values = {
        "total_missing_in_sample_columns": acc.n_missing,
        "n_sample_columns_with_missing": len(missing_by),
        "top_columns_with_missing": {header_lookup.get(k, str(k)): v for k, v in missing_by.most_common(10)},
        "non_numeric_tokens_in_sample_columns": acc.n_non_numeric,
        "na_tokens_recognised": NA_TOKENS,
    }
    if acc.n_non_numeric:
        res.limitations.append(f"{acc.n_non_numeric} non-numeric token(s) found in sample columns")
    res.value_summary = summary


def iter_feature_rows(result: InspectionResult, features: set[str] | None = None,
                      max_features: int | None = None) -> Iterator[tuple[str, dict[str, float]]]:
    """Yield (feature_id, {sample_id: value}) for primary-measure columns of an inspected matrix.

    Used for read-only cross-file concordance checks. Stops after max_features rows.
    """
    if result.table_kind != "expression_matrix" or result.feature_id_column is None:
        return
    path = Path(result.path)
    skip = result.header_line_number or 1
    prim = [c for c in result.sample_columns if c["measure"] in PRIMARY_MEASURES]
    delim = result.delimiter or "\t"
    with _open_text(path, result.compression) as fh:
        for _ in range(skip):  # skip everything up to and including the header row
            fh.readline()
        fid_idx = 0 if result.format == "geo_series_matrix" else None
        if fid_idx is None:
            # feature column position: first column unless inspection chose another
            fid_idx = result.metadata.get("feature_id_column_index", 0)
        col_idx = [(c["column_index"], c["sample_id"]) for c in prim]
        yielded = 0
        for line in fh:
            if line.startswith("!series_matrix_table_end"):
                break
            if not line.strip():
                continue
            if features is not None and '"' not in line.split(delim, fid_idx + 1)[fid_idx]:
                # cheap pre-filter on the unquoted ID field before parsing the whole line
                if line.split(delim, fid_idx + 1)[fid_idx] not in features:
                    continue
            parts = next(csv.reader([line.rstrip("\r\n")], delimiter=delim))
            fid = parts[fid_idx]
            if features is not None and fid not in features:
                continue
            vals = {}
            for i, sid in col_idx:
                try:
                    vals[sid] = float(parts[i])
                except (ValueError, IndexError):
                    vals[sid] = float("nan")
            yield fid, vals
            yielded += 1
            if max_features is not None and yielded >= max_features:
                break
