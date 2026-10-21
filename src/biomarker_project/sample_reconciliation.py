"""Explicit comparison of expression sample IDs against phenotype (GEO sample) records.

Identifier normalisation policy (normalize_sample_id):
  * Unicode NFC normalisation, removal of a leading byte-order mark, and removal of
    leading/trailing whitespace. NOTHING else: case, internal whitespace, punctuation,
    leading zeros and suffixes are preserved because they may distinguish samples.
  * Original identifiers are always kept alongside the normalised form, and every
    identifier changed by normalisation is reported.
  * Case-insensitive or punctuation-insensitive equality is reported only as a
    "near-miss hint" for human review; it is never used to match samples.

No sample is ever dropped. Exclusion candidates are written to a separate table
with an explicit reason and status PROPOSED_FOR_REVIEW_NOT_APPLIED.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .config import ExpectedCounts, PhenotypeSpec, ReportedLead
from .geo_client import parse_characteristics

# Diagnosis status vocabulary
MAPPED = "MAPPED"
MISSING = "MISSING"
AMBIGUOUS = "AMBIGUOUS"
UNMAPPED = "UNMAPPED"          # label present but not in the configured label map (unexpected)
MULTIPLE = "MULTIPLE_VALUES"   # the diagnosis field occurs more than once with different values

PROPOSED = "PROPOSED_FOR_REVIEW_NOT_APPLIED"


def normalize_sample_id(raw: Any) -> str | None:
    """Conservative identifier normalisation (see module docstring). Returns None for empty IDs."""
    if raw is None:
        return None
    if isinstance(raw, float) and raw != raw:  # NaN
        return None
    s = unicodedata.normalize("NFC", str(raw)).lstrip("﻿").strip()
    return s or None


def _loose_key(s: str) -> str:
    """Only for near-miss hints: case-folded, alphanumerics only."""
    return re.sub(r"[^0-9a-z]", "", s.casefold())


# --------------------------------------------------------------- phenotype
def extract_field(record: dict[str, Any], spec: str) -> list[str]:
    """Return all values of a field spec for a parsed GSM SOFT record (see config.SIMPLE_SAMPLE_FIELDS)."""
    fields = record.get("fields", {})
    if spec == "geo_accession":
        return fields.get("Sample_geo_accession") or [record.get("accession", "")]
    if spec == "title":
        return fields.get("Sample_title", [])
    if spec == "description":
        return fields.get("Sample_description", [])
    if spec == "source_name":
        return fields.get("Sample_source_name_ch1", [])
    if spec.startswith("char:"):
        key = spec[5:]
        return [v for k, v in parse_characteristics(fields.get("Sample_characteristics_ch1", [])) if k == key]
    raise ValueError(f"unknown field spec {spec!r}")


def apply_id_regex(value: str | None, regex: str | None) -> str | None:
    if value is None or regex is None:
        return value
    m = re.search(regex, value)
    return m.group(1) if m else None


def build_phenotype_table(sample_records: list[dict[str, Any]], spec: PhenotypeSpec) -> pd.DataFrame:
    """One row per GSM record with original values preserved and a canonical diagnosis column added."""
    rows = []
    ambiguous = set(spec.ambiguous_labels)
    for rec in sample_records:
        if rec.get("entity") != "SAMPLE":
            continue
        f = rec["fields"]
        diag_vals = [v for v in extract_field(rec, spec.diagnosis_field)]
        distinct = list(dict.fromkeys(v.strip() for v in diag_vals if v.strip()))
        if not distinct:
            raw, canon, status = None, None, MISSING
        elif len(distinct) > 1:
            raw, canon, status = " | ".join(distinct), None, MULTIPLE
        else:
            raw = distinct[0]
            if raw in spec.label_map:
                canon, status = spec.label_map[raw], MAPPED
            elif raw in ambiguous:
                canon, status = "AMBIGUOUS", AMBIGUOUS
            else:
                canon, status = None, UNMAPPED
        participant = None
        if spec.participant_id_field:
            pv = extract_field(rec, spec.participant_id_field)
            participant = " | ".join(pv) if pv else None
        row = {
            "geo_accession": rec.get("accession"),
            "title": " | ".join(f.get("Sample_title", [])) or None,
            "description": " | ".join(f.get("Sample_description", [])) or None,
            "source_name": " | ".join(f.get("Sample_source_name_ch1", [])) or None,
            "platform_id": " | ".join(f.get("Sample_platform_id", [])) or None,
            "series_ids": " | ".join(f.get("Sample_series_id", [])) or None,
            "data_processing": " | ".join(f.get("Sample_data_processing", [])) or None,
            "diagnosis_field": spec.diagnosis_field,
            "diagnosis_raw": raw,
            "diagnosis_canonical": canon,
            "diagnosis_status": status,
            "participant_id": participant,
        }
        for k, v in parse_characteristics(f.get("Sample_characteristics_ch1", [])):
            col = f"char:{k}" if k else "char:(unkeyed)"
            row[col] = v if col not in row else f"{row[col]} | {v}"
        rows.append(row)
    return pd.DataFrame(rows)


# ----------------------------------------------------------- reconciliation
@dataclass
class ReconciliationResult:
    left_label: str
    right_label: str
    key_description: str
    n_left_ids: int
    n_right_records: int
    n_matched: int
    matched: list[str]
    left_only: list[str]
    right_only: list[str]
    duplicate_left_ids: dict[str, int]
    duplicate_right_ids: dict[str, int]
    normalization_changes: list[dict[str, str]]
    right_records_without_key: list[str]
    missing_diagnosis: list[str]
    ambiguous_diagnosis: list[dict[str, str]]
    unmapped_diagnosis: list[dict[str, str]]
    group_counts_all_records: dict[str, int]
    group_counts_matched: dict[str, int]
    raw_label_counts_all_records: dict[str, int]
    near_miss_hints: list[dict[str, str]]
    rows: list[dict[str, Any]] = field(default_factory=list)

    @property
    def exact_one_to_one(self) -> bool:
        return (not self.left_only and not self.right_only and not self.duplicate_left_ids
                and not self.duplicate_right_ids and not self.right_records_without_key)

    def summary(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("rows")
        d["exact_one_to_one"] = self.exact_one_to_one
        return d


def _group_label(row: pd.Series) -> str:
    status = row.get("diagnosis_status")
    if status == MAPPED:
        return str(row["diagnosis_canonical"])
    if status == AMBIGUOUS:
        return "AMBIGUOUS"
    return f"<{status}>"


def reconcile(
    left_ids: Iterable[Any],
    phenotype: pd.DataFrame,
    key_column: str = "match_key",
    left_label: str = "expression",
    right_label: str = "phenotype",
    key_description: str = "",
    left_source: str = "",
    right_source: str = "",
) -> ReconciliationResult:
    """Compare identifiers from an expression file (left) with phenotype records (right).

    phenotype must contain `key_column` (the identifier expected in the expression file,
    possibly None when it could not be extracted) plus geo_accession and diagnosis columns.
    """
    left_original = [x for x in left_ids]
    changes: list[dict[str, str]] = []
    left_norm: list[str] = []
    for x in left_original:
        n = normalize_sample_id(x)
        if n is None:
            changes.append({"side": left_label, "original": repr(x), "normalized": "<empty>"})
            continue
        if n != str(x):
            changes.append({"side": left_label, "original": str(x), "normalized": n})
        left_norm.append(n)

    ph = phenotype.copy()
    right_norm = []
    for x in ph[key_column].tolist():
        n = normalize_sample_id(x)
        if n is not None and n != str(x):
            changes.append({"side": right_label, "original": str(x), "normalized": n})
        right_norm.append(n)
    ph["key_normalized_"] = right_norm

    lc, rc = Counter(left_norm), Counter(k for k in right_norm if k is not None)
    left_set, right_set = set(lc), set(rc)
    matched = sorted(left_set & right_set)
    left_only = sorted(left_set - right_set)
    right_only = sorted(right_set - left_set)
    no_key = ph.loc[ph["key_normalized_"].isna(), "geo_accession"].astype(str).tolist()

    ph["group_label_"] = ph.apply(_group_label, axis=1) if len(ph) else []
    all_counts = dict(Counter(ph["group_label_"])) if len(ph) else {}
    matched_mask = ph["key_normalized_"].isin(left_set)
    matched_counts = dict(Counter(ph.loc[matched_mask, "group_label_"])) if len(ph) else {}
    raw_counts = dict(Counter(ph["diagnosis_raw"].fillna("<MISSING>"))) if len(ph) else {}

    def _rows_with(status: str) -> pd.DataFrame:
        return ph.loc[ph["diagnosis_status"] == status] if len(ph) else ph

    missing = _rows_with(MISSING)["geo_accession"].astype(str).tolist()
    ambiguous = [{"geo_accession": r.geo_accession, "label": r.diagnosis_raw} for r in _rows_with(AMBIGUOUS).itertuples()]
    unmapped = [{"geo_accession": r.geo_accession, "label": r.diagnosis_raw}
                for r in pd.concat([_rows_with(UNMAPPED), _rows_with(MULTIPLE)]).itertuples()] if len(ph) else []

    hints = []
    loose_right: dict[str, list[str]] = {}
    for r in right_only:
        loose_right.setdefault(_loose_key(r), []).append(r)
    for l_ in left_only:
        for cand in loose_right.get(_loose_key(l_), []):
            hints.append({f"{left_label}_id": l_, f"{right_label}_id": cand,
                          "reason": "equal after case-folding and removing non-alphanumerics (NOT used for matching)"})

    # Per-identifier rows for the machine-readable report.
    rows: list[dict[str, Any]] = []
    for orig in left_original:
        n = normalize_sample_id(orig)
        rows.append({
            "side": left_label, "source": left_source, "original_id": orig, "normalized_id": n,
            "status": "matched" if n in right_set else ("empty_id" if n is None else f"{left_label}_only"),
            "duplicate_count": lc.get(n, 0) if n else 0, "geo_accession": "", "diagnosis_raw": "",
            "diagnosis_canonical": "", "diagnosis_status": "",
        })
    for r in ph.itertuples():
        n = r.key_normalized_
        rows.append({
            "side": right_label, "source": right_source, "original_id": getattr(r, key_column), "normalized_id": n,
            "status": "matched" if n in left_set else ("no_key_extracted" if n is None else f"{right_label}_only"),
            "duplicate_count": rc.get(n, 0) if n else 0, "geo_accession": r.geo_accession,
            "diagnosis_raw": r.diagnosis_raw, "diagnosis_canonical": r.diagnosis_canonical,
            "diagnosis_status": r.diagnosis_status,
        })

    return ReconciliationResult(
        left_label=left_label, right_label=right_label, key_description=key_description,
        n_left_ids=len(left_original), n_right_records=len(ph), n_matched=len(matched),
        matched=matched, left_only=left_only, right_only=right_only,
        duplicate_left_ids={k: v for k, v in lc.items() if v > 1},
        duplicate_right_ids={k: v for k, v in rc.items() if v > 1},
        normalization_changes=changes, right_records_without_key=no_key,
        missing_diagnosis=missing, ambiguous_diagnosis=ambiguous, unmapped_diagnosis=unmapped,
        group_counts_all_records=dict(sorted(all_counts.items())),
        group_counts_matched=dict(sorted(matched_counts.items())),
        raw_label_counts_all_records=dict(sorted(raw_counts.items(), key=lambda kv: str(kv[0]))),
        near_miss_hints=hints, rows=rows,
    )


def write_reconciliation(result: ReconciliationResult, out_dir: Path, prefix: str) -> dict[str, str]:
    """Write every identifier (CSV) and the summary (JSON). Returns written paths."""
    from .download import atomic_write_text  # local import avoids a cycle at module import

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{prefix}_id_reconciliation.csv"
    json_path = out_dir / f"{prefix}_id_reconciliation_summary.json"
    cols = ["side", "source", "original_id", "normalized_id", "status", "duplicate_count",
            "geo_accession", "diagnosis_raw", "diagnosis_canonical", "diagnosis_status"]
    buf = _csv_text(result.rows, cols)
    atomic_write_text(csv_path, buf)
    atomic_write_text(json_path, json.dumps(result.summary(), indent=2, default=str) + "\n")
    return {"csv": str(csv_path), "json": str(json_path)}


def _csv_text(rows: list[dict[str, Any]], cols: list[str]) -> str:
    import io

    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})
    return sio.getvalue()


# --------------------------------------------------------- counts & leads
def compare_group_counts(observed: dict[str, int], expected: ExpectedCounts, observed_total: int) -> list[dict[str, Any]]:
    """Compare observed counts against reference counts. Never alters the data."""
    rows = []
    if expected.total is not None:
        rows.append({"group": "TOTAL", "reported": expected.total, "observed": observed_total,
                     "difference": observed_total - expected.total,
                     "status": "MATCHES_REPORTED" if observed_total == expected.total else "DIFFERS_FROM_REPORTED"})
    for g, n in expected.groups.items():
        obs = observed.get(g, 0)
        rows.append({"group": g, "reported": n, "observed": obs, "difference": obs - n,
                     "status": "MATCHES_REPORTED" if obs == n else "DIFFERS_FROM_REPORTED"})
    for g, obs in sorted(observed.items()):
        if g not in expected.groups:
            rows.append({"group": g, "reported": None, "observed": obs, "difference": None,
                         "status": "NO_REFERENCE_COUNT"})
    if expected.described_participants is not None:
        rows.append({"group": "DESCRIBED_PARTICIPANTS", "reported": expected.described_participants,
                     "observed": observed_total, "difference": observed_total - expected.described_participants,
                     "status": ("MATCHES_REPORTED" if observed_total == expected.described_participants
                                else "DIFFERS_FROM_REPORTED")})
    return rows


def check_reported_leads(leads: Iterable[ReportedLead], phenotype: pd.DataFrame,
                         expression_ids: dict[str, set[str]]) -> list[dict[str, Any]]:
    """Check sample IDs named by reported leads against the retrieved records. Nothing is excluded."""
    out = []
    pheno_cols = [c for c in ("geo_accession", "title", "description", "participant_id") if c in phenotype]
    for lead in leads:
        entry: dict[str, Any] = {"lead_id": lead.id, "description": lead.description, "source": lead.source,
                                 "evidence_status": "REPORTED", "checked_ids": []}
        entry["kind"] = lead.kind
        if lead.kind == "count_discrepancy":
            entry["check"] = ("count discrepancy: compared through expected_counts (see the group-count table); "
                              "the reason for the difference is UNRESOLVED")
        elif not lead.sample_ids:
            entry["check"] = ("UNRESOLVED: no sample IDs recorded for this lead in the configuration; "
                              "add them from the publication to enable a direct check")
        for sid in lead.sample_ids:
            n = normalize_sample_id(sid)
            found_pheno = [c for c in pheno_cols if n in set(phenotype[c].dropna().astype(str))]
            found_expr = [f for f, ids in expression_ids.items() if n in ids]
            entry["checked_ids"].append({"id": sid, "found_in_phenotype_fields": found_pheno,
                                         "found_in_expression_files": found_expr})
        out.append(entry)
    return out


def propose_exclusion_candidates(accession: str, phenotype: pd.DataFrame,
                                 recons: dict[str, ReconciliationResult]) -> list[dict[str, Any]]:
    """Candidates for *human review*. Never applied by the pipeline."""
    rows = []
    for r in phenotype.itertuples():
        if r.diagnosis_status in (MISSING, AMBIGUOUS, UNMAPPED, MULTIPLE):
            rows.append({"accession": accession, "geo_accession": r.geo_accession, "sample_id": r.title,
                         "reason": f"diagnosis label {r.diagnosis_status}: {r.diagnosis_raw!r}",
                         "evidence": f"GEO sample characteristics ({r.diagnosis_field})",
                         "source_file": "GEO sample records", "status": PROPOSED})
    for fname, rec in recons.items():
        gsm_by_key: dict[str, list[str]] = {}
        for row in rec.rows:
            if row["side"] == rec.right_label and row["normalized_id"]:
                gsm_by_key.setdefault(row["normalized_id"], []).append(str(row["geo_accession"]))
        for sid in rec.right_only:
            rows.append({"accession": accession, "geo_accession": ";".join(gsm_by_key.get(sid, [])), "sample_id": sid,
                         "reason": f"phenotype record has no column in {fname}", "evidence": "ID reconciliation",
                         "source_file": fname, "status": PROPOSED})
        for sid in rec.left_only:
            rows.append({"accession": accession, "geo_accession": "", "sample_id": sid,
                         "reason": f"column in {fname} has no matching phenotype record", "evidence": "ID reconciliation",
                         "source_file": fname, "status": PROPOSED})
        for sid, n in rec.duplicate_left_ids.items():
            rows.append({"accession": accession, "geo_accession": "", "sample_id": sid,
                         "reason": f"identifier appears {n} times in {fname}", "evidence": "ID reconciliation",
                         "source_file": fname, "status": PROPOSED})
    return rows


def compare_identifier_sets(values_by_dataset: dict[str, list[str]]) -> dict[str, Any]:
    """Exact comparison of identifier sets across datasets (for possible-overlap flags)."""
    norm = {a: {normalize_sample_id(v) for v in vals if normalize_sample_id(v)} for a, vals in values_by_dataset.items()}
    accs = list(norm)
    pairs = []
    for i in range(len(accs)):
        for j in range(i + 1, len(accs)):
            shared = sorted(norm[accs[i]] & norm[accs[j]])
            pairs.append({"datasets": [accs[i], accs[j]], "n_values": [len(norm[accs[i]]), len(norm[accs[j]])],
                          "n_shared": len(shared), "shared_values": shared})
    return {"pairs": pairs}
