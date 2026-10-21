"""Audit-only reconciliation of historical Entrez Gene IDs against org.Hs.eg.db and NCBI gene_history.

Option C (dual reporting):
  View A - snapshot-consistent baseline: org.Hs.eg.db (Entrez Gene snapshot dated CUTOFF) is fixed.
           IDs present in the baseline are preserved. For absent IDs, only gene_history records dated
           on or before CUTOFF are used; later records are reported as "after cutoff", never applied.
  View B - the retained NCBI gene_history file as retrieved: every human record is used, whatever its
           date. IDs still present in the baseline but discontinued in the file are reported separately.

Rules (both views):
  * A successor is taken only from the GeneID column of a gene_history record; symbols are never used
    to infer a replacement.
  * GeneID "-" is recorded as an explicit no-replacement state (README: the symbol field applies "if
    the discontinued record was not replaced"; observed data: "-" in GeneID).
  * Chains are followed one record at a time; every intermediate ID is recorded. A chain ends when an
    ID is present in the baseline, has a "-" record, has no usable record, or revisits an ID (cycle).
  * An ID with more than one gene_history record is not resolved (duplicate_history_records).
  * Absence from org.Hs.eg.db is never treated as evidence of retirement or merging.
  * Nothing is merged: successors shared by several input IDs, or equal to another input ID of the same
    package, are flagged only.

No GEO data, expression values or dataset probe lists are read.
"""
from __future__ import annotations

import gzip
import hashlib
import io
import sqlite3
import tarfile
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HUMAN_TAXID = "9606"
README_FIELDS = ("tax_id", "GeneID", "Discontinued GeneID", "Discontinued Symbol", "Discontinue Date")
FILE_HEADER = ["#tax_id", "GeneID", "Discontinued_GeneID", "Discontinued_Symbol", "Discontinue_Date"]


# ---------------------------------------------------------------- source verification
def file_hashes(path: Path) -> dict:
    md5, sha = hashlib.md5(), hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            md5.update(chunk)
            sha.update(chunk)
    return {"path": str(path), "bytes": path.stat().st_size, "md5": md5.hexdigest(), "sha256": sha.hexdigest()}


def gzip_ok(path: Path) -> bool:
    with gzip.open(path, "rb") as fh:
        while fh.read(1 << 20):
            pass
    return True


def readme_gene_history_fields(readme: Path) -> list[str]:
    """Field names documented in the README's gene_history section (up to the next ==== divider)."""
    lines = readme.read_text(encoding="utf-8", errors="replace").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("gene_history"))
    found = []
    for l in lines[start + 1:]:
        if l.startswith("====="):
            break
        s = l.strip()
        if s.endswith(":") and s[:-1] in README_FIELDS:
            found.append(s[:-1])
    return found


# ---------------------------------------------------------------- inputs
@dataclass
class HistoryRecord:
    successor: str          # "-" = no replacement
    symbol: str
    date: str               # YYYYMMDD


def read_history(path: Path) -> tuple[dict[str, list[HistoryRecord]], list[str], int]:
    """Human (tax_id 9606) records keyed by discontinued GeneID. Returns (records, header, n_rows)."""
    recs: dict[str, list[HistoryRecord]] = defaultdict(list)
    n = 0
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if parts[0] != HUMAN_TAXID:
                continue
            n += 1
            tax, cur, old, sym, date = parts
            recs[old].append(HistoryRecord(cur, sym, date))
    return dict(recs), header, n


@dataclass
class PackageSource:
    name: str               # e.g. "illuminaHumanv3"
    tarball: Path
    member: str             # sqlite path inside the tarball
    query: str              # returns one column of historical Entrez IDs
    provenance: str


def _sqlite_from_tar(tarball: Path, member: str, tmp: Path) -> Path:
    with tarfile.open(tarball, "r:gz") as tf:
        m = tf.getmember(member)
        out = tmp / Path(member).name
        with tf.extractfile(m) as src, open(out, "wb") as dst:
            dst.write(src.read())
    return out


def read_ids(tarball: Path, member: str, query: str) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_genehist_") as tmp:
        db = _sqlite_from_tar(tarball, member, Path(tmp))
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            ids = sorted({str(r[0]).strip() for r in con.execute(query) if r[0] is not None and str(r[0]).strip()})
        finally:
            con.close()
    return ids


# ---------------------------------------------------------------- resolution
@dataclass
class Resolution:
    cls: str
    chain: list[str] = field(default_factory=list)   # input ID first, then each successor followed
    final: str = ""                                  # resolved current ID, if any
    reason: str = ""


def resolve(gid: str, baseline: set[str], history: dict[str, list[HistoryRecord]], cutoff: str | None) -> Resolution:
    """Follow gene_history from gid. cutoff=None uses all records (View B); otherwise only records dated
    <= cutoff (View A). In View A an ID present in the baseline ends the chain. In View B an ID present in
    the baseline ends the chain only if the history file has no record for it; otherwise its record is
    followed (post-baseline discontinuation)."""
    chain = [gid]
    node = gid
    while True:
        if node in baseline and (cutoff is not None or node not in history):
            if node == gid:
                return Resolution("present_in_baseline", chain, node)
            return Resolution("replaced_successor_in_baseline", chain, node)
        recs = history.get(node, [])
        if len(recs) > 1:
            return Resolution("unresolved", chain, "", f"duplicate_history_records:{node}")
        usable = [r for r in recs if cutoff is None or r.date <= cutoff]
        if not usable:
            if recs:   # only a record dated after the cutoff (View A)
                why = "history_record_after_cutoff" if node == gid else f"successor_record_after_cutoff:{node}"
                return Resolution("unresolved" if node != gid else "absent_history_after_cutoff", chain, "", why)
            if node == gid:
                return Resolution("unexplained_absent_no_history", chain, "", "absent_from_baseline_and_history")
            return Resolution("unresolved", chain, "", f"successor_absent_from_baseline_and_history:{node}")
        rec = usable[0]
        if rec.successor == "-":
            if node == gid:
                return Resolution("discontinued_no_replacement", chain, "", "")
            return Resolution("chain_ends_no_replacement", chain, "", f"no_replacement_at:{node}")
        if rec.successor in chain:
            return Resolution("unresolved", chain + [rec.successor], "", f"cycle_at:{rec.successor}")
        chain.append(rec.successor)
        node = rec.successor


def view_b_class(gid: str, baseline: set[str], history: dict[str, list[HistoryRecord]], res: Resolution) -> str:
    """View B adds the distinction 'present in baseline but discontinued in the history file'."""
    if gid in baseline:
        return "present_in_baseline_discontinued_in_history" if gid in history else "present_in_baseline_no_history"
    return res.cls


# ---------------------------------------------------------------- audit
COLUMNS = ["package", "entrez_id", "baseline_status", "history_record_count", "history_direct_successor",
           "history_discontinued_symbol", "history_discontinue_date", "history_date_vs_cutoff",
           "viewA_class", "viewA_chain", "viewA_final_successor", "viewA_final_in_baseline",
           "viewA_collision", "viewA_shared_successor",
           "viewB_class", "viewB_chain", "viewB_final_successor", "viewB_final_in_baseline",
           "viewB_collision", "viewB_shared_successor", "unresolved_reason", "source_provenance"]


def audit_package(name: str, ids: list[str], provenance: str, baseline: set[str],
                  history: dict[str, list[HistoryRecord]], cutoff: str) -> tuple[list[dict], dict]:
    """Rows for the audit population (absent from baseline, or listed in gene_history) and full counts."""
    idset = set(ids)
    rows, counts_a, counts_b = [], Counter(), Counter()
    for gid in ids:
        ra = resolve(gid, baseline, history, cutoff)
        rb = resolve(gid, baseline, history, None)
        cb = view_b_class(gid, baseline, history, rb)
        counts_a[ra.cls] += 1
        counts_b[cb] += 1
        if gid in baseline and gid not in history:
            continue                                  # counted, not tabulated (no reconciliation question)
        recs = history.get(gid, [])
        r0 = recs[0] if len(recs) == 1 else None
        rows.append({
            "package": name, "entrez_id": gid,
            "baseline_status": "present_in_baseline" if gid in baseline else "absent_from_baseline",
            "history_record_count": len(recs),
            "history_direct_successor": r0.successor if r0 else "",
            "history_discontinued_symbol": r0.symbol if r0 else "",
            "history_discontinue_date": r0.date if r0 else "",
            "history_date_vs_cutoff": "" if not r0 else ("on_or_before_cutoff" if r0.date <= cutoff else "after_cutoff"),
            "viewA_class": ra.cls, "viewA_chain": ">".join(ra.chain), "viewA_final_successor": ra.final,
            "viewA_final_in_baseline": _yn(ra.final, baseline),
            "viewB_class": cb, "viewB_chain": ">".join(rb.chain), "viewB_final_successor": rb.final,
            "viewB_final_in_baseline": _yn(rb.final, baseline),
            "unresolved_reason": rb.reason or ra.reason,
            "source_provenance": provenance,
        })
    for view in ("viewA", "viewB"):
        finals = Counter(r[f"{view}_final_successor"] for r in rows
                         if r[f"{view}_final_successor"] and r[f"{view}_final_successor"] != r["entrez_id"])
        for r in rows:
            f = r[f"{view}_final_successor"]
            replaced = bool(f) and f != r["entrez_id"]
            r[f"{view}_collision"] = "yes" if replaced and f in idset else "no"
            r[f"{view}_shared_successor"] = "yes" if replaced and finals[f] > 1 else "no"
    return rows, {"n_input_ids": len(ids), "viewA": dict(sorted(counts_a.items())), "viewB": dict(sorted(counts_b.items())),
                  "n_tabulated": len(rows), "n_absent_from_baseline": sum(g not in baseline for g in ids),
                  "n_absent_in_history": sum(g not in baseline and g in history for g in ids)}


def _yn(final: str, baseline: set[str]) -> str:
    return "" if not final else ("yes" if final in baseline else "no")


def tsv(rows: list[dict], columns: list[str]) -> str:
    buf = io.StringIO()
    buf.write("\t".join(columns) + "\n")
    for r in rows:
        buf.write("\t".join(str(r.get(c, "")) for c in columns) + "\n")
    return buf.getvalue()
