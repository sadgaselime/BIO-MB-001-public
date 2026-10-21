#!/usr/bin/env python3
"""Phase 2A: read-only adjudication of candidate expression input files for one accession.

Example:
    python scripts/phase2a_expression_adjudication.py --accession GSE63060 --version v1

Inputs are read from data/ after their SHA-256 is verified against the download manifest.
Nothing under data/ is written. Outputs go to reports/phase2a/<ACCESSION>/<VERSION>/, and an
existing version directory is never overwritten. No inferential statistics are computed.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import biomarker_project
except ImportError:  # running from a checkout without 'pip install -e .'
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    import biomarker_project

import numpy as np
import pandas as pd

from biomarker_project.config import load_config
from biomarker_project.download import Manifest
from biomarker_project.expression_adjudication import (
    annotation_summary, compare_full, parse_delimited_matrix, parse_series_matrix, rank_identity_mapping,
    read_bgx_from_tar, sha256_file,
)

ROOT = Path(__file__).resolve().parents[1]


def _pick(names: list[str], suffix: str) -> str:
    hits = [n for n in names if n.endswith(suffix)]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one configured file ending in {suffix!r}, found {hits}")
    return hits[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--accession", default="GSE63060")
    ap.add_argument("--version", default="v1", help="report version directory name (never overwritten)")
    ap.add_argument("--project-root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    root = args.project_root.resolve()
    cfg = load_config(root / "config" / "datasets.yaml")
    ds = cfg.dataset(args.accession)
    acc = ds.accession
    out = root / "reports" / "phase2a" / acc / args.version
    if out.exists():
        raise SystemExit(f"{out.relative_to(root)} already exists; choose a new --version (outputs are never overwritten)")
    names = [f.name for f in ds.files]
    normalized = [n for n in names if n.endswith("_normalized.txt.gz") and "non-normalized" not in n]
    if len(normalized) != 1:
        raise SystemExit(f"expected exactly one configured normalized file, found {normalized}")
    files = {"series_matrix": _pick(names, "_series_matrix.txt.gz"), "normalized": normalized[0],
             "non_normalized": _pick(names, "_non-normalized.txt.gz"), "archive": _pick(names, "_RAW.tar")}
    raw = root / "data" / "raw" / acc

    # 1. provenance: verify every input against the manifest before reading it
    man = Manifest(raw / "download_manifest.json")
    inputs = {}
    for role, name in files.items():
        p = raw / name
        recorded = man.last_verified_sha(name)
        actual = sha256_file(p)
        inputs[role] = {"file": f"data/raw/{acc}/{name}", "sha256": actual, "manifest_sha256": recorded,
                        "verified": actual == recorded}
        if actual != recorded:
            raise SystemExit(f"checksum mismatch for {name}: refusing to continue")
    ph = pd.read_csv(root / "data" / "processed" / acc / "phenotype_table.tsv", sep="\t", dtype=str, keep_default_na=False)
    t2g = dict(zip(ph.title, ph.geo_accession))
    g2dx = dict(zip(ph.geo_accession, ph.diagnosis_canonical))
    t2dx = {t: g2dx[g] for t, g in t2g.items()}

    # 2. parse candidates
    sm, sm_meta = parse_series_matrix(raw / files["series_matrix"])
    norm = parse_delimited_matrix(raw / files["normalized"])
    nonnorm = parse_delimited_matrix(raw / files["non_normalized"])
    nn = nonnorm.data.copy()
    nn.columns = [c.removesuffix(".AVG_Signal") for c in nn.columns]

    # 3. full equivalence: series matrix vs normalized (GSM -> title)
    gsm2title = {g: t for t, g in t2g.items()}
    full = compare_full(sm, norm.data, {g: gsm2title[g] for g in sm.columns if g in gsm2title})
    extra_norm = [c for c in norm.data.columns if c not in t2g]
    extra_info = {}
    geo_cols = [c for c in norm.data.columns if c in t2g]
    cc = np.corrcoef(norm.data[geo_cols].to_numpy().T)
    np.fill_diagonal(cc, np.nan)
    typical = float(np.nanmedian(np.nanmax(cc, axis=1)))
    for c in extra_norm:
        r = norm.data[geo_cols].corrwith(norm.data[c]).sort_values(ascending=False)
        chip = c.split("_")[0]
        extra_info[c] = {
            "in_geo_sample_records": False,
            "identical_to_a_geo_column": any(np.array_equal(norm.data[c].to_numpy(), norm.data[g].to_numpy()) for g in geo_cols),
            "max_pearson_with_geo_sample": float(r.iloc[0]), "most_similar_geo_sample": r.index[0],
            "typical_max_pearson_between_geo_samples": typical,
            "geo_samples_on_same_chip": sorted(t for t in t2g if t.startswith(chip + "_")),
            "value_min": float(norm.data[c].min()), "value_max": float(norm.data[c].max()),
            "also_in_non_normalized": c in nn.columns,
        }

    # 4. empty-header columns of the non-normalized file
    mapping = rank_identity_mapping(nn, norm.data)
    per_col = mapping.pop("per_column")
    for a in mapping["assignments"]:
        a["geo_accession"] = t2g.get(a["assigned_target"]) if a["assigned_target"] else None
        a["diagnosis"] = t2dx.get(a["assigned_target"]) if a["assigned_target"] else None

    # 5. processing / scale evidence (descriptive only)
    vals = sm.to_numpy()
    srt = np.sort(vals, axis=0)
    shared = nn.index.intersection(norm.data.index)
    dropped = nn.index.difference(norm.data.index)
    named = [c for c in nn.columns if c in norm.data.columns]
    scale = {
        "geo_data_processing_text": sorted({v for row in sm_meta.get("Sample_data_processing", []) for v in row}),
        "normalized_value_range": [float(vals.min()), float(vals.max())],
        "distinct_per_sample_minima": int(len(np.unique(np.round(srt[0], 8)))),
        "distinct_per_sample_maxima": int(len(np.unique(np.round(srt[-1], 8)))),
        "max_deviation_of_sorted_columns_from_mean_profile": float(np.abs(srt - srt.mean(1, keepdims=True)).max()),
        "non_normalized_value_range": [float(np.nanmin(nn.to_numpy())), float(np.nanmax(nn.to_numpy()))],
        "non_normalized_negative_values": int((nn.to_numpy() < 0).sum()),
        "rank_identity_non_normalized_to_normalized_all_named_columns": mapping["validation"]["max_rank_differences"] == 0,
        "median_pearson_log2_nonnorm_vs_normalized": float(np.median([np.corrcoef(np.log2(nn.loc[shared, c]), norm.data.loc[shared, c])[0, 1] for c in named])),
        "n_probes_non_normalized": int(nn.shape[0]), "n_probes_normalized": int(norm.data.shape[0]),
        "n_probes_dropped_in_normalized": int(len(dropped)),
        "dropped_probe_mean_signal_range": [float(nn.loc[dropped].mean(axis=1).min()), float(nn.loc[dropped].mean(axis=1).max())] if len(dropped) else None,
        "kept_probe_mean_signal_range": [float(nn.loc[shared].mean(axis=1).min()), float(nn.loc[shared].mean(axis=1).max())],
        "non_normalized_has_detection_pvalues": any("detection" in c.lower() for c in nonnorm.column_labels),
    }

    # 6. annotation
    with tarfile.open(raw / files["archive"], "r:") as tf:  # list only; nothing is extracted to disk
        bgx = [m.name for m in tf.getmembers() if m.name.lower().endswith((".bgx", ".bgx.gz"))]
    if len(bgx) != 1:
        raise SystemExit(f"expected one BGX manifest in {files['archive']}, found {bgx}")
    bgx_member = bgx[0]
    heading, probes, member_sha = read_bgx_from_tar(raw / files["archive"], bgx_member)
    ann = annotation_summary(probes, sm.index)
    ann.update({"source": f"{files['archive']}::{bgx_member}", "member_sha256": member_sha, "bgx_heading": heading,
                "n_probes_in_manifest": int(len(probes)),
                "non_normalized_probe_set_equals_manifest": set(nn.index) == set(probes.Probe_Id)})
    split_annot = {r["feature_id"]: probes.set_index("Probe_Id").loc[r["feature_id"], ["Symbol", "Entrez_Gene_ID"]].to_dict()
                   for r in norm.repaired_split_records if r["feature_id"] in set(probes.Probe_Id)}

    # 7. cohort descriptors relevant to the primary-input decision (counts only)
    flag = "char:included in case -control study"
    crosstab = pd.crosstab(ph.diagnosis_raw, ph[flag]) if flag in ph else None
    counts = {
        "series_matrix": dict(pd.Series([g2dx[g] for g in sm.columns]).value_counts()),
        "normalized_labelled": dict(pd.Series([t2dx[c] for c in norm.data.columns if c in t2dx]).value_counts()),
        "non_normalized_labelled": dict(pd.Series([t2dx[c] for c in nn.columns if c in t2dx]).value_counts()),
    }

    # 8. write outputs (new directory only)
    out.mkdir(parents=True)
    per_col.to_csv(out / "non_normalized_column_matching.csv", index=False)
    pd.DataFrame(mapping["assignments"]).to_csv(out / "empty_header_column_assignment.csv", index=False)
    if crosstab is not None:
        crosstab.to_csv(out / "case_control_flag_by_diagnosis.csv")
    keep = ["Probe_Id", "Symbol", "Entrez_Gene_ID", "Source", "Probe_Type", "Chromosome", "RefSeq_ID", "Definition"]
    probes.set_index("Probe_Id").loc[sm.index].rename_axis("Probe_Id").reset_index()[keep].to_csv(out / "probe_annotation_provisional_bgx2008.tsv", sep="\t", index=False)
    summary = {
        "phase": "2A expression-input adjudication (descriptive; no inferential statistics)",
        "accession": acc, "version": args.version,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "software": {"biomarker_project": biomarker_project.__version__, "python": platform.python_version(),
                     "pandas": pd.__version__, "numpy": np.__version__},
        "inputs": inputs,
        "parsing": {"series_matrix": {"n_features": int(sm.shape[0]), "n_samples": int(sm.shape[1]),
                                      "duplicate_features": int(sm.index.duplicated().sum()), "missing_values": int(sm.isna().sum().sum()),
                                      "columns_equal_gsm_header": list(sm.columns) == sm_meta["Sample_geo_accession"][0]},
                    "normalized": norm.summary(), "non_normalized": nonnorm.summary()},
        "series_matrix_vs_normalized_full": full,
        "normalized_extra_columns": extra_info,
        "empty_header_mapping": mapping,
        "split_record_annotation": split_annot,
        "processing_and_scale": scale,
        "annotation": ann,
        "group_counts": {k: {kk: int(vv) for kk, vv in v.items()} for k, v in counts.items()},
        "case_control_flag_by_diagnosis": crosstab.to_dict() if crosstab is not None else None,
    }
    (out / "adjudication_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print(json.dumps({"output_dir": str(out.relative_to(root)), "full_identical": full["identical"],
                      "validation_passed": mapping["validation"]["passed"],
                      "assignments": [(a["source_column"], a["assigned_target"], a["status"]) for a in mapping["assignments"]]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
