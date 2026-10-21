"""Evidence-based classification of the processing state of each inspected file.

States: RAW_INSTRUMENT, NON_NORMALIZED, PROCESSED_NORMALIZED, METADATA_ONLY, UNKNOWN.

Evidence sources (independent of each other):
  * file_structure     - archive members, table kind, measurement columns
  * value_distribution - scale, integer-ness, sign, per-sample distribution similarity
  * geo_annotation     - GSM 'data_processing' text (describes the GSM VALUE column, i.e.
                         the Series Matrix table; NOT the supplementary files)
  * filename           - recorded for transparency, weight 0: never decides a state,
                         only flagged if it contradicts the content-based result.

Decision rule: evidence weights (strong=3, moderate=2, weak=1) are summed per state.
  HIGH   : score >= 4 from >= 2 independent sources and no competing state, or definitive
           structural evidence (e.g. a table with no values is METADATA_ONLY; an archive of
           only CEL/IDAT files is RAW_INSTRUMENT) with no competing state
  MEDIUM : score >= 2 and any competing state scores at least 2 less
  LOW    : otherwise when a leading state exists but evidence is thin
  UNKNOWN: no content evidence, or competing states within 1 point of each other.
Anything other than HIGH requires review. Nothing in this module transforms data.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any

import numpy as np

from .file_inspection import InspectionResult, iter_feature_rows

RAW = "RAW_INSTRUMENT"
NON_NORMALIZED = "NON_NORMALIZED"
PROCESSED = "PROCESSED_NORMALIZED"
METADATA_ONLY = "METADATA_ONLY"
UNKNOWN = "UNKNOWN"
WEIGHTS = {"strong": 3, "moderate": 2, "weak": 1, "none": 0}

RAW_EXTENSIONS = {".cel", ".idat", ".fastq", ".fq", ".bam", ".cram", ".sra", ".xys", ".pair"}
ANNOTATION_EXTENSIONS = {".bgx", ".bpm", ".csv", ".txt", ".gpr"}
STRONG_PROCESSING_TERMS = re.compile(r"normali[sz]|quantile|\brma\b|\brsn\b|\bvst\b|neqc|\bmas5\b|gcrma", re.I)
WEAK_PROCESSING_TERMS = re.compile(r"\blumi\b|log2|log-?transform|limma|background[- ]?(correct|subtract)", re.I)
FILENAME_HINTS = [
    (re.compile(r"non[-_]?normali[sz]ed|unnormali[sz]ed", re.I), NON_NORMALIZED),
    (re.compile(r"normali[sz]ed", re.I), PROCESSED),
    (re.compile(r"(^|[_.-])raw([_.-]|$)", re.I), RAW),
    (re.compile(r"counts?", re.I), NON_NORMALIZED),
    (re.compile(r"filelist|sample_sheet|samplesheet", re.I), METADATA_ONLY),
]


def _ev(source: str, observation: str, supports: str | None, weight: str) -> dict[str, Any]:
    return {"source": source, "observation": observation, "supports": supports, "weight": weight}


def filename_hint(name: str) -> str | None:
    for rx, state in FILENAME_HINTS:
        if rx.search(name):
            return state
    return None


def classify_file(insp: InspectionResult, modality: str, geo_data_processing: list[str] | None = None) -> dict[str, Any]:
    evidence: list[dict[str, Any]] = []
    hint = filename_hint(insp.file_name)
    evidence.append(_ev("filename", f"file name {insp.file_name!r} suggests {hint or 'nothing specific'}", None, "none"))

    if not insp.usable:
        evidence.append(_ev("file_structure", f"file could not be inspected ({insp.status}: {insp.error})", None, "none"))
        return _decide(evidence, hint, forced=(UNKNOWN, "LOW"))

    kind = insp.table_kind
    # ---- structure
    if kind == "archive":
        exts = {k.lower(): v for k, v in insp.metadata.get("extension_counts", {}).items()}
        members = [m["name"] for m in insp.metadata.get("members", [])]
        raw_n = sum(v for k, v in exts.items() if k in RAW_EXTENSIONS)
        annot = [m for m in members if re.match(r"^GPL\d+", m.split("/")[-1]) or m.lower().endswith((".bgx", ".bgx.gz"))]
        if raw_n and raw_n == sum(exts.values()):
            evidence.append(_ev("file_structure", f"all {raw_n} archive members are instrument-level files {sorted(exts)}", RAW, "strong"))
        elif members and len(annot) == len(members):
            evidence.append(_ev("file_structure", f"archive contains only platform annotation/manifest files: {members[:5]}",
                                METADATA_ONLY, "strong"))
        else:
            evidence.append(_ev("file_structure", f"archive member types {exts} do not identify a processing state", None, "none"))
        return _decide(evidence, hint)
    if kind in ("file_manifest", "sample_sheet", "metadata_only_series_matrix", "header_only", "table_without_sample_columns"):
        evidence.append(_ev("file_structure", f"table kind '{kind}' contains no expression values", METADATA_ONLY, "strong"))
        return _decide(evidence, hint)
    if kind != "expression_matrix":
        evidence.append(_ev("file_structure", f"unrecognised table kind {kind!r}", None, "none"))
        return _decide(evidence, hint)

    mtypes = insp.measurement_types
    if {"detection_pval", "bead_stderr", "n_beads"} & set(mtypes):
        evidence.append(_ev("file_structure",
                            f"Illumina GenomeStudio-style per-sample columns {sorted(mtypes)} (summarised probe "
                            f"profile export; usually exported before normalisation)", NON_NORMALIZED, "moderate"))

    # ---- values
    vs = insp.value_summary or {}
    if vs.get("n_numeric_values"):
        vmin, vmax = vs["min"], vs["max"]
        frac_int, frac_neg = vs["fraction_integer_valued"], vs["fraction_negative"]
        if frac_int > 0.999 and vmin >= 0 and vmax > 1000:
            weight = "strong" if modality == "expression_rnaseq" else "moderate"
            evidence.append(_ev("value_distribution",
                                f"all values are non-negative integers (max {vmax:.0f}): raw count-like data", NON_NORMALIZED, weight))
        elif 0 <= vmin and vmax <= 1 and modality == "methylation_array":
            evidence.append(_ev("value_distribution",
                                f"values bounded in [0, 1] (min {vmin:.3g}, max {vmax:.3g}): p-values or beta values; "
                                f"processing state cannot be inferred from values alone", None, "none"))
        elif vmax <= 25 and vmin > -10:
            evidence.append(_ev("value_distribution",
                                f"values on a log-like scale (min {vmin:.3g}, max {vmax:.3g}): a transformation has been applied",
                                PROCESSED, "moderate"))
        elif vmax > 1000:
            note = f"linear-scale intensities (min {vmin:.3g}, max {vmax:.3g}, {frac_neg:.2%} negative)"
            evidence.append(_ev("value_distribution", note, NON_NORMALIZED, "weak"))
        else:
            evidence.append(_ev("value_distribution", f"value range {vmin:.3g}..{vmax:.3g} is not diagnostic", None, "none"))
        psd = (vs.get("per_sample_distribution") or {}).get("sd_of_sample_quantiles_over_pooled_iqr")
        if psd:
            central = max(psd.get("q25", math.inf), psd.get("q50", math.inf), psd.get("q75", math.inf))
            if central < 0.01:
                evidence.append(_ev("value_distribution",
                                    f"per-sample quantiles nearly identical (max SD/IQR {central:.4f} at q25-q75): consistent "
                                    f"with quantile-type normalisation", PROCESSED, "moderate"))
            elif central > 0.1:
                evidence.append(_ev("value_distribution",
                                    f"per-sample distributions differ (max SD/IQR {central:.3f} at q25-q75): no between-sample "
                                    f"distribution normalisation evident", NON_NORMALIZED, "weak"))
            else:
                evidence.append(_ev("value_distribution",
                                    f"per-sample distribution similarity intermediate (max SD/IQR {central:.3f})", None, "none"))
    else:
        evidence.append(_ev("value_distribution", "no numeric values available for inspection", None, "none"))

    # ---- GEO annotation (only meaningful for the Series Matrix VALUE table)
    if insp.format == "geo_series_matrix":
        texts = list(geo_data_processing or []) + list(insp.metadata.get("sample_data_processing", []))
        joined = " | ".join(dict.fromkeys(t for t in texts if t))
        if joined:
            if STRONG_PROCESSING_TERMS.search(joined):
                evidence.append(_ev("geo_annotation", f"GSM data_processing: {joined[:300]!r}", PROCESSED, "moderate"))
            elif WEAK_PROCESSING_TERMS.search(joined):
                evidence.append(_ev("geo_annotation", f"GSM data_processing mentions processing software/transform: "
                                                      f"{joined[:300]!r} (method details not stated)", PROCESSED, "weak"))
            else:
                evidence.append(_ev("geo_annotation", f"GSM data_processing: {joined[:300]!r} (not diagnostic)", None, "none"))
        else:
            evidence.append(_ev("geo_annotation", "no GSM data_processing text available", None, "none"))
    else:
        evidence.append(_ev("geo_annotation", "GEO provides no per-file processing description for supplementary files",
                            None, "none"))
    return _decide(evidence, hint)


def _decide(evidence: list[dict[str, Any]], hint: str | None, forced: tuple[str, str] | None = None) -> dict[str, Any]:
    scores: dict[str, int] = defaultdict(int)
    sources: dict[str, set[str]] = defaultdict(set)
    for e in evidence:
        if e["supports"] and e["source"] != "filename":
            scores[e["supports"]] += WEIGHTS[e["weight"]]
            sources[e["supports"]].add(e["source"])
    notes = []
    if forced:
        state, conf = forced
    elif not scores:
        state, conf = UNKNOWN, "LOW"
        notes.append("no content-based evidence; processing state cannot be established")
    else:
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])
        top, top_score = ranked[0]
        runner = ranked[1][1] if len(ranked) > 1 else 0
        if runner and top_score - runner <= 1:
            state, conf = UNKNOWN, "LOW"
            notes.append(f"conflicting evidence: {dict(scores)}")
        else:
            state = top
            definitive = any(e["supports"] == top and e["source"] == "file_structure" and e["weight"] == "strong"
                             and top in (METADATA_ONLY, RAW) for e in evidence)
            if runner == 0 and (definitive or (top_score >= 4 and len(sources[top]) >= 2)):
                conf = "HIGH"
            elif top_score >= 2:
                conf = "MEDIUM"
            else:
                conf = "LOW"
            if runner:
                notes.append(f"some evidence supports other states: {dict(scores)}")
    filename_conflict = bool(hint and state not in (UNKNOWN, hint))
    if filename_conflict:
        notes.append(f"content-based state {state} contradicts the file-name hint {hint}")
    return {
        "state": state,
        "confidence": conf,
        "requires_review": state == UNKNOWN or conf != "HIGH" or filename_conflict,
        "filename_hint": hint,
        "filename_conflict": filename_conflict,
        "scores": dict(scores),
        "evidence": evidence,
        "notes": notes,
    }


def compare_matrices(a: InspectionResult, b: InspectionResult, sample_map: dict[str, str],
                     max_features: int = 2000) -> dict[str, Any]:
    """Read-only comparison of values for shared features/samples in two matrices.

    sample_map maps sample IDs of `a` to sample IDs of `b`. Used to establish, e.g.,
    whether a Series Matrix table is identical to a supplementary 'normalized' file.
    """
    out: dict[str, Any] = {"file_a": a.file_name, "file_b": b.file_name, "max_features": max_features}
    if not (a.usable and b.usable) or a.table_kind != "expression_matrix" or b.table_kind != "expression_matrix":
        out["status"] = "NOT_COMPARABLE"
        out["reason"] = "both files must be inspected expression matrices"
        return out
    rows_a = dict(iter_feature_rows(a, max_features=max_features))
    rows_b = dict(iter_feature_rows(b, features=set(rows_a)))
    feats = [f for f in rows_a if f in rows_b]
    pairs_a, pairs_b = [], []
    samples_used = set()
    for f in feats:
        for sa, sb in sample_map.items():
            if sa in rows_a[f] and sb in rows_b[f]:
                pairs_a.append(rows_a[f][sa])
                pairs_b.append(rows_b[f][sb])
                samples_used.add(sa)
    out.update({"n_features_read_from_a": len(rows_a), "n_shared_features": len(feats),
                "n_shared_samples": len(samples_used), "n_value_pairs": len(pairs_a)})
    if not pairs_a:
        out["status"] = "NO_OVERLAP"
        return out
    x, y = np.asarray(pairs_a), np.asarray(pairs_b)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    diff = np.abs(x - y)
    tol = 1e-6 * np.maximum(1.0, np.abs(x))
    out["fraction_identical"] = float(np.mean(diff <= tol)) if x.size else None
    out["max_abs_difference"] = float(diff.max()) if x.size else None
    out["pearson_r"] = float(np.corrcoef(x, y)[0, 1]) if x.size > 2 and x.std() > 0 and y.std() > 0 else None
    if x.size and np.all(x > 0) and np.all(y > 0):
        lx = np.log2(x)
        out["pearson_r_log2a_vs_b"] = float(np.corrcoef(lx, y)[0, 1]) if lx.std() > 0 and y.std() > 0 else None
    if out["fraction_identical"] is not None and out["fraction_identical"] > 0.999:
        out["status"] = "IDENTICAL_VALUES"
    elif out.get("pearson_r") is not None and out["pearson_r"] > 0.99:
        out["status"] = "HIGHLY_CORRELATED_NOT_IDENTICAL"
    else:
        out["status"] = "DIFFERENT_VALUES"
    out["note"] = "first features of file A compared; sample IDs mapped through GEO sample records"
    return out
