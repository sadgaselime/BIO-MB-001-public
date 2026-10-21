"""Phase 2A: read-only adjudication of candidate expression files for one GEO series.

Everything here is non-destructive: input files are read (and checksum-verified against
the download manifest), never modified; repairs such as re-joining a split record are
applied to in-memory copies only and are logged.

Provided checks
  * Full-matrix parsing with explicit handling of malformed records, including detection
    of a "split record" (a probe ID followed by a line break, its values on the next line
    with an empty ID field). A split record is only repaired when the pattern is exact.
  * Exhaustive value comparison of two matrices over all shared probes and samples.
  * Content-based identification of unlabelled (empty-header) columns: each column of a
    "source" matrix is compared with every column of a "target" matrix by Spearman
    correlation and by exact rank identity. The method is first validated on the columns
    whose labels are known; an unlabelled column is assigned only if it is rank-identical
    to exactly one target column that has no labelled counterpart.
  * Parsing of an Illumina BGX manifest read in memory from a tar archive (no extraction)
    and a summary of probe-to-gene mapping coverage and ambiguity.

No differential expression, feature selection or other inferential analysis is performed.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import io
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

MAPPING_MIN_SPEARMAN = 0.9999   # an assignment needs (near-)perfect rank agreement ...
MAPPING_MAX_RANK_DIFFERENCES = 0  # ... no probe may change rank ...
MAPPING_MIN_MARGIN = 0.05       # ... and the runner-up must be clearly worse


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _open_bytes(path: Path) -> bytes:
    with open(path, "rb") as fh:
        head = fh.read(2)
    opener = gzip.open if head == b"\x1f\x8b" else open
    with opener(path, "rb") as fh:
        return fh.read()


# ------------------------------------------------------------------ parsing
@dataclass
class MatrixParse:
    path: str
    header: list[str]
    data: pd.DataFrame                      # rows = feature IDs, columns = header[1:] (positional labels if empty)
    column_labels: list[str]                # original header text for each data column ('' preserved)
    n_lines: int
    line_endings: dict[str, int]
    repaired_split_records: list[dict[str, Any]] = field(default_factory=list)
    unrepaired_malformed: list[dict[str, Any]] = field(default_factory=list)
    duplicate_feature_ids: list[str] = field(default_factory=list)
    n_missing_values: int = 0

    def summary(self) -> dict[str, Any]:
        return {
            "path": self.path, "n_lines": self.n_lines, "line_endings": self.line_endings,
            "n_header_fields": len(self.header), "n_data_columns": self.data.shape[1],
            "n_features": self.data.shape[0],
            "empty_header_positions_1based": [i + 1 for i, c in enumerate(self.header) if c == ""],
            "repaired_split_records": self.repaired_split_records,
            "unrepaired_malformed": self.unrepaired_malformed,
            "duplicate_feature_ids": self.duplicate_feature_ids,
            "n_missing_values": self.n_missing_values,
        }


def empty_label(position_1based: int) -> str:
    return f"<EMPTY_HEADER@col{position_1based}>"


def parse_delimited_matrix(path: Path, delimiter: str = "\t") -> MatrixParse:
    """Parse a feature x sample text matrix (first column = feature ID). Never modifies the file."""
    raw = _open_bytes(path)
    text = raw.decode("utf-8", errors="strict")
    lines = text.split("\n")
    endings = {"crlf": sum(1 for l in lines if l.endswith("\r")), "lf_only": sum(1 for l in lines[:-1] if not l.endswith("\r"))}
    lines = [l[:-1] if l.endswith("\r") else l for l in lines]
    if lines and lines[-1] == "":
        lines = lines[:-1]
    header = next(csv.reader([lines[0]], delimiter=delimiter))
    n = len(header)
    ids, rows, repaired, bad = [], [], [], []
    i = 1
    while i < len(lines):
        fields = lines[i].split(delimiter)
        if len(fields) == n:
            if fields[0] == "":
                bad.append({"line": i + 1, "n_fields": n, "problem": "empty feature ID with full field count"})
            else:
                ids.append(fields[0])
                rows.append(fields[1:])
            i += 1
            continue
        nxt = lines[i + 1].split(delimiter) if i + 1 < len(lines) else None
        if len(fields) == 1 and fields[0] and nxt is not None and len(nxt) == n and nxt[0] == "":
            repaired.append({"id_line": i + 1, "values_line": i + 2, "feature_id": fields[0],
                             "repair": "ID line and following empty-ID value line joined (in memory only)"})
            ids.append(fields[0])
            rows.append(nxt[1:])
            i += 2
            continue
        bad.append({"line": i + 1, "n_fields": len(fields), "first_field": fields[0][:40],
                    "problem": "field count differs from header; excluded"})
        i += 1
    values = pd.DataFrame(rows, dtype=str).replace({"": np.nan, "NA": np.nan, "NaN": np.nan}).astype(float).to_numpy() \
        if rows else np.empty((0, n - 1))
    labels = [c if c != "" else empty_label(j + 1) for j, c in enumerate(header)][1:]
    df = pd.DataFrame(values, index=pd.Index(ids, name=header[0] or "feature_id"), columns=labels)
    dups = sorted(df.index[df.index.duplicated()].unique())
    return MatrixParse(path=str(path), header=header, data=df, column_labels=header[1:], n_lines=len(lines),
                       line_endings=endings, repaired_split_records=repaired, unrepaired_malformed=bad,
                       duplicate_feature_ids=list(dups), n_missing_values=int(np.isnan(values).sum()))


def parse_series_matrix(path: Path) -> tuple[pd.DataFrame, dict[str, list[list[str]]]]:
    """Return (value table with GSM columns, !Sample_ header fields)."""
    text = _open_bytes(path).decode("utf-8", errors="strict")
    lines = text.splitlines()
    b = lines.index("!series_matrix_table_begin")
    e = lines.index("!series_matrix_table_end")
    meta: dict[str, list[list[str]]] = {}
    for l in lines[:b]:
        if l.startswith("!Sample_"):
            k, *v = next(csv.reader([l], delimiter="\t"))
            meta.setdefault(k[1:], []).append(v)
    df = pd.read_csv(io.StringIO("\n".join(lines[b + 1:e])), sep="\t", index_col=0, dtype={0: str})
    df.index = df.index.astype(str)
    return df, meta


# ---------------------------------------------------------------- comparison
def compare_full(a: pd.DataFrame, b: pd.DataFrame, sample_map: dict[str, str]) -> dict[str, Any]:
    """Exhaustive comparison of a[:, k] with b[:, sample_map[k]] over all shared features."""
    feats = a.index.intersection(b.index)
    pairs = [(k, v) for k, v in sample_map.items() if k in a.columns and v in b.columns]
    A = a.loc[feats, [k for k, _ in pairs]].to_numpy()
    B = b.loc[feats, [v for _, v in pairs]].to_numpy()
    diff = np.abs(A - B)
    both_nan = np.isnan(A) & np.isnan(B)
    differing = int(((diff > 0) & ~both_nan).sum() + (np.isnan(A) ^ np.isnan(B)).sum())
    return {
        "n_features_a": int(a.shape[0]), "n_features_b": int(b.shape[0]), "n_shared_features": int(len(feats)),
        "features_only_in_a": sorted(set(a.index) - set(b.index))[:50],
        "features_only_in_b": sorted(set(b.index) - set(a.index))[:50],
        "n_samples_compared": len(pairs), "n_values_compared": int(A.size),
        "n_values_differing": differing,
        "max_abs_difference": float(np.nanmax(diff)) if A.size else None,
        "identical": differing == 0 and A.size > 0,
    }


def _zscore_cols(x: np.ndarray) -> np.ndarray:
    x = x - x.mean(axis=0)
    return x / np.sqrt((x ** 2).sum(axis=0))


def rank_identity_mapping(source: pd.DataFrame, target: pd.DataFrame) -> dict[str, Any]:
    """Match every source column to target columns by rank agreement over shared features.

    Returns per-column results, a validation over source columns whose label also exists
    in the target, and assignments for unlabelled source columns (labels starting '<EMPTY').
    """
    feats = source.index.intersection(target.index)
    S_df, T_df = source.loc[feats], target.loc[feats]
    spear = _zscore_cols(S_df.rank().to_numpy()).T @ _zscore_cols(T_df.rank().to_numpy())
    tcols = list(T_df.columns)
    t_rank_min = T_df.rank(method="min")
    rows = []
    for i, scol in enumerate(S_df.columns):
        order = np.argsort(spear[i])[::-1]
        best, second = tcols[order[0]], tcols[order[1]]
        s_rank = S_df[scol].rank(method="min")
        rank_diff = int((s_rank != t_rank_min[best]).sum())
        o = np.argsort(S_df[scol].to_numpy(), kind="stable")
        mono = int((np.diff(T_df[best].to_numpy()[o]) < -1e-12).sum())
        rows.append({
            "source_column": scol, "best_target": best, "spearman_best": float(spear[i, order[0]]),
            "runner_up_target": second, "spearman_runner_up": float(spear[i, order[1]]),
            "margin": float(spear[i, order[0]] - spear[i, order[1]]),
            "probes_with_rank_difference": rank_diff, "monotonicity_violations": mono,
            "tied_values_source": int(S_df[scol].duplicated().sum()), "tied_values_target": int(T_df[best].duplicated().sum()),
        })
    res = pd.DataFrame(rows)
    labelled = res[~res.source_column.str.startswith("<EMPTY")]
    known = labelled[labelled.source_column.isin(tcols)]
    validation = {
        "n_labelled_columns_with_known_target": int(len(known)),
        "n_best_match_is_own_column": int((known.source_column == known.best_target).sum()),
        "min_own_spearman": float(known.spearman_best.min()) if len(known) else None,
        "min_margin": float(known.margin.min()) if len(known) else None,
        "max_rank_differences": int(known.probes_with_rank_difference.max()) if len(known) else None,
    }
    validation["passed"] = bool(len(known) and validation["n_best_match_is_own_column"] == len(known)
                                and validation["max_rank_differences"] == 0)
    unclaimed = [c for c in tcols if c not in set(labelled.source_column)]
    assignments = []
    unlabelled = res[res.source_column.str.startswith("<EMPTY")]
    best_counts = unlabelled.best_target.value_counts()
    for r in unlabelled.itertuples():
        reasons = []
        if not validation["passed"]:
            reasons.append("method validation on labelled columns failed")
        if r.spearman_best < MAPPING_MIN_SPEARMAN:
            reasons.append(f"Spearman {r.spearman_best:.6f} < {MAPPING_MIN_SPEARMAN}")
        if r.probes_with_rank_difference > MAPPING_MAX_RANK_DIFFERENCES:
            reasons.append(f"{r.probes_with_rank_difference} probes change rank")
        if r.margin < MAPPING_MIN_MARGIN:
            reasons.append(f"margin {r.margin:.4f} < {MAPPING_MIN_MARGIN}")
        if r.best_target not in unclaimed:
            reasons.append("best target already has a labelled source column")
        if best_counts[r.best_target] > 1:
            reasons.append("several unlabelled columns share the same best target")
        assignments.append({
            "source_column": r.source_column, "assigned_target": None if reasons else r.best_target,
            "status": "CONTENT_MATCH_UNIQUE" if not reasons else "UNRESOLVED",
            "reasons_not_assigned": reasons, "spearman_best": r.spearman_best, "margin": r.margin,
            "probes_with_rank_difference": r.probes_with_rank_difference,
            "evidence_type": "inferred from data content (rank identity); not documented by the submitter",
        })
    return {"n_shared_features": int(len(feats)), "per_column": res, "validation": validation,
            "unclaimed_target_columns": unclaimed, "assignments": assignments}


# ---------------------------------------------------------------- annotation
def read_bgx_from_tar(tar_path: Path, member: str) -> tuple[dict[str, str], pd.DataFrame, str]:
    """Read an Illumina BGX manifest from a tar archive in memory. Returns (heading, probe table, member sha256)."""
    with tarfile.open(tar_path, "r:") as tf:
        blob = tf.extractfile(member).read()
    member_sha = hashlib.sha256(blob).hexdigest()
    text = (gzip.decompress(blob) if blob[:2] == b"\x1f\x8b" else blob).decode("utf-8", errors="replace")
    lines = text.splitlines()
    sec = {l.strip("[]"): i for i, l in enumerate(lines) if l.startswith("[") and l.endswith("]")}
    heading = {}
    for l in lines[sec["Heading"] + 1:sec["Probes"]]:
        k, _, v = l.partition("\t")
        heading[k] = v
    end = min(v for k, v in sec.items() if v > sec["Probes"])
    probes = pd.read_csv(io.StringIO("\n".join(lines[sec["Probes"] + 1:end])), sep="\t", dtype=str, keep_default_na=False)
    return heading, probes, member_sha


def annotation_summary(probes: pd.DataFrame, probe_ids: pd.Index) -> dict[str, Any]:
    t = probes.set_index("Probe_Id")
    missing = [p for p in probe_ids if p not in t.index]
    a = t.loc[[p for p in probe_ids if p in t.index]]
    sym = a["Symbol"].str.strip()
    ent = a["Entrez_Gene_ID"].str.strip()
    has_sym, has_ent = sym != "", ent != ""
    g = sym[has_sym].value_counts()
    both = a[has_sym & has_ent]
    s2e = both.groupby(sym[has_sym & has_ent])["Entrez_Gene_ID"].nunique()
    e2s = both.groupby(ent[has_sym & has_ent])["Symbol"].nunique()
    return {
        "n_probes_queried": int(len(probe_ids)), "n_missing_from_annotation": len(missing),
        "missing_examples": missing[:20],
        "n_with_symbol": int(has_sym.sum()), "n_with_entrez": int(has_ent.sum()),
        "n_symbol_without_entrez": int((has_sym & ~has_ent).sum()),
        "n_placeholder_symbols_LOC_or_HS": int(sym.str.match(r"^(LOC\d+|HS\.\d+)$").sum()),
        "source_counts": a["Source"].value_counts().to_dict(),
        "probe_type_counts": a["Probe_Type"].value_counts().to_dict(),
        "n_distinct_symbols": int(len(g)), "n_symbols_with_multiple_probes": int((g > 1).sum()),
        "n_probes_in_multi_probe_symbols": int(g[g > 1].sum()), "max_probes_per_symbol": int(g.max()) if len(g) else 0,
        "n_symbols_mapping_to_multiple_entrez": int((s2e > 1).sum()),
        "symbols_mapping_to_multiple_entrez": sorted(s2e[s2e > 1].index.tolist()),
        "n_entrez_mapping_to_multiple_symbols": int((e2s > 1).sum()),
        "n_with_chromosome": int((a["Chromosome"].str.strip() != "").sum()),
    }
