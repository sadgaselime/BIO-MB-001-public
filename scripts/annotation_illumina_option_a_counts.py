#!/usr/bin/env python3
"""PROVISIONAL probe-level counts for the Illumina platforms under the Option A logic.

NOT an approved mapping policy: D6-F (v7:609) covers GPL570 only. This script applies the same logic
to the Illumina candidate packages so that the PI can review it separately:
  each probe's Entrez Gene assignment from the package, with IDs absent from the org.Hs.eg.db 3.23.1
  baseline reconciled by the approved gene-history procedure (records dated on or before 20260318),
  exactly as classified in View A of reports/annotation_audit/ncbi_gene_history/v1.

Packages (Bioconductor 3.23, retained under reference/bioconductor_3.23/, verified before use):
  illuminaHumanv3.db 1.26.0 (GSE63060, GPL6947)     probes table; Entrez snapshot 2015-Mar17
  illuminaHumanv4.db 1.26.0 (GSE63061, GPL10558)    probes table; Entrez snapshot 2015-Mar17
  lumiHumanIDMapping 1.10.1, table HumanHT12_V4_0_R2_15002873_B joined to nuID_MappingInfo
      (manifest-based; no snapshot date recorded). Whether this table applies to GSE140829 is NOT
      established; the GSE140829 route remains governed by D19 and is not resolved here.

Every probe is classified exactly once; nothing is inferred for unresolved probes; successors that are
already directly mapped are flagged, never merged. No GEO data are read; nothing is installed.
Writes reports/annotation_audit/illumina_option_a/<version>/ and never overwrites an existing version.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from biomarker_project.gene_history_reconciliation import _sqlite_from_tar, file_hashes, tsv  # noqa: E402

REF = ROOT / "reference/bioconductor_3.23"
V1 = ROOT / "reports/annotation_audit/ncbi_gene_history/v1"
CUTOFF = "20260318"
CHIPDB_QUERY = "SELECT probe_id, gene_id FROM probes"
LUMI_QUERY = ("SELECT t.Probe_Id, trim(m.EntrezID) FROM HumanHT12_V4_0_R2_15002873_B t "
              "LEFT JOIN nuID_MappingInfo m ON m.nuID = t.nuID")
PACKAGES = [  # v1 package label, tarball, sqlite member, query, cohort note
    ("illuminaHumanv3", "illuminaHumanv3.db_1.26.0.tar.gz", "illuminaHumanv3.db/inst/extdata/illuminaHumanv3.sqlite",
     CHIPDB_QUERY, "GSE63060 (GPL6947); Entrez snapshot 2015-Mar17"),
    ("illuminaHumanv4", "illuminaHumanv4.db_1.26.0.tar.gz", "illuminaHumanv4.db/inst/extdata/illuminaHumanv4.sqlite",
     CHIPDB_QUERY, "GSE63061 (GPL10558); Entrez snapshot 2015-Mar17"),
    ("lumi HT-12 v4 R2", "lumiHumanIDMapping_1.10.1.tar.gz", "lumiHumanIDMapping/inst/extdata/lumiHumanIDMapping.sqlite",
     LUMI_QUERY, "manifest table HumanHT12_V4_0_R2_15002873_B; applicability to GSE140829 unverified (D19)"),
]
NO_REPLACEMENT = {"discontinued_no_replacement", "chain_ends_no_replacement"}


def verify_inputs() -> dict:
    ref = {e["file"]: e for e in json.loads((REF / "download_manifest.json").read_text())["files"]}
    v1m = json.loads((V1 / "reconciliation_manifest.json").read_text())
    problems, out = [], {"tarballs": {}}
    for _, tar, *_ in PACKAGES:
        h = file_hashes(REF / tar)
        e = ref.get(tar)
        if e is None or (h["bytes"], h["md5"], h["sha256"]) != (e["bytes"], e["md5_published"], e["sha256"]):
            problems.append(f"{tar}: does not match reference/bioconductor_3.23/download_manifest.json")
        if h["sha256"] != v1m["sources"]["tarballs"][tar]["sha256"]:
            problems.append(f"{tar}: differs from the copy used by gene-history v1")
        out["tarballs"][tar] = h
    t = file_hashes(V1 / "gene_history_reconciliation.tsv")
    if t["sha256"] != v1m["determinism"]["output_sha256"]["gene_history_reconciliation.tsv"]:
        problems.append("gene-history v1 table differs from its manifest")
    if v1m["parameters"]["view_a_cutoff_inclusive"] != CUTOFF:
        problems.append("gene-history v1 View A cutoff is not 20260318")
    if problems:
        raise SystemExit("INPUT VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    out["v1_table"] = t
    out["v1_manifest_sha256"] = file_hashes(V1 / "reconciliation_manifest.json")["sha256"]
    out["v1_input_id_sha256"] = {name: v1m["inputs"][name]["sha256_of_sorted_id_list"] for name, *_ in PACKAGES}
    return out


def classify_package(name, tar, member, query, src, v1_rows) -> tuple[list[dict], dict, list]:
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_illumina_") as tmp:
        db = _sqlite_from_tar(REF / tar, member, Path(tmp))
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        rows = con.execute(query).fetchall()
        con.close()
    genes = defaultdict(set)
    for pid, gid in rows:
        genes[str(pid)]
        if gid is not None and str(gid).strip():
            genes[str(pid)].add(str(gid).strip())
    ids = sorted({g for s in genes.values() for g in s})
    id_hash_ok = hashlib.sha256("\n".join(ids).encode()).hexdigest() == src["v1_input_id_sha256"][name]

    v1 = {r["entrez_id"]: r for r in v1_rows if r["package"] == name and r["baseline_status"] == "absent_from_baseline"}
    out, cls = [], Counter()
    for pid in sorted(genes):
        g = genes[pid]
        rec = {"package": name, "probe_id": pid, "n_package_genes": len(g), "package_gene_id": "", "option_a_class": "",
               "option_a_gene_id": "", "history_chain": "", "successor_directly_mapped": ""}
        if not g:
            c = "no_assignment_in_package"
        elif len(g) > 1:
            c, rec["package_gene_id"] = "multiple_mappings_excluded", ";".join(sorted(g, key=int))
        else:
            gid = next(iter(g))
            rec["package_gene_id"] = gid
            r = v1.get(gid)
            if r is None:
                c, rec["option_a_gene_id"] = "eligible_direct", gid
            elif r["viewA_class"] == "replaced_successor_in_baseline":
                c, rec["option_a_gene_id"], rec["history_chain"] = "eligible_via_history_replacement", r["viewA_final_successor"], r["viewA_chain"]
            else:
                c, rec["history_chain"] = r["viewA_class"], r["viewA_chain"]   # no_replacement / unexplained: nothing inferred
        rec["option_a_class"] = c
        cls[c] += 1
        out.append(rec)

    direct = {r["option_a_gene_id"] for r in out if r["option_a_class"] == "eligible_direct"}
    for r in out:
        if r["option_a_class"] == "eligible_via_history_replacement":
            r["successor_directly_mapped"] = "yes" if r["option_a_gene_id"] in direct else "no"
    rep = [r for r in out if r["option_a_class"] == "eligible_via_history_replacement"]
    succ_sources = defaultdict(set)
    for r in rep:
        succ_sources[r["option_a_gene_id"]].add(r["package_gene_id"])
    single = {r["package_gene_id"] for r in out if r["n_package_genes"] == 1}
    multi = {x for r in out if r["option_a_class"] == "multiple_mappings_excluded" for x in r["package_gene_id"].split(";")}
    v1_by = defaultdict(set)
    for k, r in v1.items():
        v1_by[r["viewA_class"]].add(k)
    gene_by = defaultdict(set)
    for r in out:
        if r["n_package_genes"] == 1 and r["option_a_class"] != "eligible_direct":
            gene_by[r["option_a_class"]].add(r["package_gene_id"])

    counts = {
        "probes_total": len(out),
        "classes": dict(sorted(cls.items())),
        "probes_with_one_eligible_gene": cls["eligible_direct"] + cls["eligible_via_history_replacement"],
        "probe_level": {"current": cls["eligible_direct"], "replaced_under_cutoff": len(rep),
                        "no_replacement": sum(cls[c] for c in NO_REPLACEMENT),
                        "unexplained": cls["unexplained_absent_no_history"],
                        "multi_gene_excluded": cls["multiple_mappings_excluded"], "unmapped": cls["no_assignment_in_package"],
                        "collision_successor_already_directly_mapped": sum(r["successor_directly_mapped"] == "yes" for r in rep)},
        "gene_level": {"package_entrez_ids": len(ids),
                       "replaced_under_cutoff": len(gene_by["eligible_via_history_replacement"]),
                       "no_replacement": len(gene_by["discontinued_no_replacement"] | gene_by["chain_ends_no_replacement"]),
                       "unexplained": len(gene_by["unexplained_absent_no_history"]),
                       "collision_successor_already_directly_mapped": len({r["package_gene_id"] for r in rep if r["successor_directly_mapped"] == "yes"}),
                       "shared_successors_more_than_one_source_gene": sum(len(v) > 1 for v in succ_sources.values()),
                       "distinct_option_a_genes": len({r["option_a_gene_id"] for r in out if r["option_a_gene_id"]})},
        "v1_gene_classes_only_in_multi_gene_probes": {c: len(v1_by[c] - single) for c in sorted(v1_by)},
    }
    checks = [
        (f"{name}: each probe classified exactly once", len({r["probe_id"] for r in out}) == len(out) == sum(cls.values())),
        (f"{name}: package gene-ID set equals gene-history v1 input set", id_hash_ok),
        (f"{name}: no mapping inferred for non-eligible probes",
         all(not r["option_a_gene_id"] for r in out if not r["option_a_class"].startswith("eligible"))),
    ]
    for c, s in v1_by.items():   # every v1 absent gene is in a single-gene probe (classified) or only in multi-gene probes
        checks.append((f"{name}: v1 {c} genes ({len(s)}) = single-gene part + multi-gene-only part",
                       (s & single) == (gene_by["eligible_via_history_replacement"] if c == "replaced_successor_in_baseline" else gene_by[c]) & s
                       and (s - single) <= multi))
    return out, counts, checks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="v1")
    args = ap.parse_args()
    outdir = ROOT / "reports/annotation_audit/illumina_option_a" / args.version
    if outdir.exists():
        raise SystemExit(f"{outdir.relative_to(ROOT)} already exists; choose a new --version")
    src = verify_inputs()
    with open(V1 / "gene_history_reconciliation.tsv", encoding="utf-8") as fh:
        v1_rows = list(csv.DictReader(fh, delimiter="\t"))

    def run():
        files, counts, checks = {}, {}, []
        cols = ["package", "probe_id", "n_package_genes", "package_gene_id", "option_a_class", "option_a_gene_id",
                "history_chain", "successor_directly_mapped"]
        for name, tar, member, query, note in PACKAGES:
            out, c, ch = classify_package(name, tar, member, query, src, v1_rows)
            slug = name.replace(" ", "_").replace("-", "")
            files[f"{slug}_probe_classification_PROVISIONAL.tsv"] = tsv(out, cols)
            counts[name] = {"cohort_note": note, **c}
            checks += ch
        return files, counts, checks

    f1, c1, k1 = run()
    f2, c2, _ = run()
    h1 = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f1.items()}
    det = {"runs_compared": 2, "identical": h1 == {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f2.items()} and c1 == c2,
           "output_sha256": h1}
    validation = {"status": "OK" if all(ok for _, ok in k1) else "FAILED",
                  "checks": [{"check": n, "status": "OK" if ok else "FAILED"} for n, ok in k1]}
    if validation["status"] != "OK" or not det["identical"]:
        print(json.dumps({"validation": validation, "determinism": det}, indent=2))
        raise SystemExit("VALIDATION OR DETERMINISM FAILED (nothing written)")
    outdir.mkdir(parents=True)
    for k, v in f1.items():
        (outdir / k).write_text(v, encoding="utf-8")
    manifest = {"status": "PROVISIONAL — not an approved mapping policy; D6-F covers GPL570 only; D19 unchanged",
                "cutoff_inclusive": CUTOFF, "sources": src, "counts": c1, "validation": validation, "determinism": det,
                "command": "python scripts/annotation_illumina_option_a_counts.py --version " + args.version}
    (outdir / "counts_manifest_PROVISIONAL.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"counts": c1, "validation": validation["status"]}, indent=2))
    print(f"written: {outdir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
