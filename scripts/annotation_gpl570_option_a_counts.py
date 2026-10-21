#!/usr/bin/env python3
"""GPL570 probe-set counts under candidate Option A (NOT an approved mapping policy).

Option A (candidate): each probe set's Entrez Gene assignment from hgu133plus2.db 3.13.0
(Entrez Gene snapshot 2021-Apr14), with historical IDs that are absent from the org.Hs.eg.db 3.23.1
baseline reconciled through NCBI gene_history records dated on or before 20260318 (approved cutoff,
D6-E), exactly as classified in View A of reports/annotation_audit/ncbi_gene_history/v1.

Inputs (retained in the project; verified before use):
  reference/bioconductor_3.23/hgu133plus2.db_3.13.0.tar.gz   (manifest: download_manifest.json)
  reports/annotation_audit/ncbi_gene_history/v1/            (reconciliation table + manifest)
Every probe set is classified exactly once. No mapping is inferred for unresolved probe sets; nothing
is installed; no GEO data are read. "Eligible" here means annotation-eligible only (one Entrez ID);
presence in GSE99039's Series Matrix and any D17 feature rule are not assessed.

Runs under the code-identity lifecycle (src/biomarker_project/code_identity.py): outputs are staged, verified
and atomically finalized to reports/annotation_audit/gpl570_option_a/<version>/ (never overwritten); a version
other than v1 must reproduce the v1 table byte for byte. The gene-history v1 table is a frozen input: its raw
NCBI source is not retained, so it cannot be rebuilt independently (v7:643). Failed runs are kept as
<version>.FAILED-<run_id>/ and are never accepted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_MAIN_CODE = sys._getframe(0).f_code  # this module's executed code object (executed-code check, D8-3)


def _executed_code_registry():
    """Load scripts/_executed_code.py once per process (bootstrap; it verifies itself in check())."""
    name = "bio_mb_001_executed_code"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/_executed_code.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


_ec = _executed_code_registry()
if __name__ == "__main__":
    _ec.install(ROOT, _MAIN_CODE, __file__)  # before any project module is imported
sys.path.insert(0, str(ROOT / "src"))
from biomarker_project.gene_history_reconciliation import _sqlite_from_tar, file_hashes, tsv  # noqa: E402
from biomarker_project import code_identity as ci  # noqa: E402  (run lifecycle, D8-3)

TARBALL = ROOT / "reference/bioconductor_3.23/hgu133plus2.db_3.13.0.tar.gz"
TAR_MANIFEST = ROOT / "reference/bioconductor_3.23/download_manifest.json"
MEMBER = "hgu133plus2.db/inst/extdata/hgu133plus2.sqlite"
V1 = ROOT / "reports/annotation_audit/ncbi_gene_history/v1"
PACKAGE = "hgu133plus2"
CUTOFF = "20260318"
# Accession-route comparison recorded on 2026-10-12 (org.Hs.eg.db accession tables); the org.Hs.eg.db
# tarball is not retained, so these figures are carried forward, not recomputed.
ACCESSION_ROUTE_2026_10_12 = {"single_gene_probe_sets": 43149, "route_gives_exactly_one_gene": 23332,
                              "same_as_package_gene": 23314, "different_gene": 18,
                              "route_ambiguous_more_than_one_gene": 1, "no_accession_route": 19816,
                              "level": "probe set", "gene_level_disagreements": "not computed (source not retained)"}


def verify_inputs() -> dict:
    tm = json.loads(TAR_MANIFEST.read_text())["files"][0]
    h = file_hashes(TARBALL)
    v1m = json.loads((V1 / "reconciliation_manifest.json").read_text())
    v1_tsv = file_hashes(V1 / "gene_history_reconciliation.tsv")
    problems = []
    if (h["bytes"], h["md5"], h["sha256"]) != (tm["bytes"], tm["md5_published"], tm["sha256"]):
        problems.append("hgu133plus2 tarball does not match reference manifest")
    if h["sha256"] != v1m["sources"]["tarballs"]["hgu133plus2.db_3.13.0.tar.gz"]["sha256"]:
        problems.append("hgu133plus2 tarball differs from the copy used by gene-history v1")
    if v1_tsv["sha256"] != v1m["determinism"]["output_sha256"]["gene_history_reconciliation.tsv"]:
        problems.append("v1 reconciliation table differs from its manifest")
    if v1m["parameters"]["view_a_cutoff_inclusive"] != CUTOFF:
        problems.append("v1 View A cutoff is not the approved 20260318")
    if problems:
        raise SystemExit("INPUT VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    return {"tarball": {**h, "manifest": str(TAR_MANIFEST.relative_to(ROOT))},
            "v1_table": {**v1_tsv, "path": str((V1 / "gene_history_reconciliation.tsv").relative_to(ROOT))},
            "v1_input_id_sha256": v1m["inputs"][PACKAGE]["sha256_of_sorted_id_list"]}


def compute(src: dict) -> tuple[dict[str, str], dict]:
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_gpl570_") as tmp:
        db = _sqlite_from_tar(TARBALL, MEMBER, Path(tmp))
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        rows = con.execute("SELECT probe_id, gene_id, is_multiple FROM probes").fetchall()
        con.close()
    genes, flags = defaultdict(set), defaultdict(set)
    for pid, gid, mult in rows:
        genes[pid]                                   # register every probe set, including NULL-gene rows
        flags[pid].add(int(mult))
        if gid is not None and str(gid).strip():
            genes[pid].add(str(gid).strip())
    pkg_ids = sorted({g for s in genes.values() for g in s})
    if hashlib.sha256("\n".join(pkg_ids).encode()).hexdigest() != src["v1_input_id_sha256"]:
        raise SystemExit("package gene-ID set differs from the set reconciled in gene-history v1")

    v1 = {}
    with open(V1 / "gene_history_reconciliation.tsv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r["package"] == PACKAGE and r["baseline_status"] == "absent_from_baseline":
                v1[r["entrez_id"]] = r

    out, cls = [], Counter()
    for pid in sorted(genes):
        g = genes[pid]
        rec = {"probe_set_id": pid, "n_package_genes": len(g), "package_gene_id": "", "option_a_class": "",
               "option_a_gene_id": "", "history_chain": "", "successor_directly_mapped": "", "is_multiple_flag": ""}
        rec["is_multiple_flag"] = ";".join(str(x) for x in sorted(flags[pid]))
        if not g:
            c = "no_assignment_in_package"
        elif len(g) > 1:
            c = "multiple_mappings_excluded"
            rec["package_gene_id"] = ";".join(sorted(g, key=int))
        else:
            gid = next(iter(g))
            rec["package_gene_id"] = gid
            r = v1.get(gid)
            if r is None:
                c, rec["option_a_gene_id"] = "eligible_direct", gid
            elif r["viewA_class"] == "replaced_successor_in_baseline":
                c, rec["option_a_gene_id"], rec["history_chain"] = "eligible_via_history_replacement", r["viewA_final_successor"], r["viewA_chain"]
            elif r["viewA_class"] == "discontinued_no_replacement":
                c, rec["history_chain"] = "no_eligible_assignment_discontinued", r["viewA_chain"]
            else:
                c, rec["history_chain"] = f"unresolved_{r['viewA_class']}", r["viewA_chain"]
        rec["option_a_class"] = c
        cls[c] += 1
        out.append(rec)

    direct_genes = {r["option_a_gene_id"] for r in out if r["option_a_class"] == "eligible_direct"}
    for r in out:
        if r["option_a_class"] == "eligible_via_history_replacement":
            r["successor_directly_mapped"] = "yes" if r["option_a_gene_id"] in direct_genes else "no"

    multi_genes = {x for r in out if r["option_a_class"] == "multiple_mappings_excluded" for x in r["package_gene_id"].split(";")}
    single_genes = {r["package_gene_id"] for r in out if r["n_package_genes"] == 1}
    v1_rep = {k for k, r in v1.items() if r["viewA_class"] == "replaced_successor_in_baseline"}
    v1_disc = {k for k, r in v1.items() if r["viewA_class"] == "discontinued_no_replacement"}
    rep = [r for r in out if r["option_a_class"] == "eligible_via_history_replacement"]
    disc = [r for r in out if r["option_a_class"] == "no_eligible_assignment_discontinued"]
    gene_rep = {r["package_gene_id"] for r in rep}
    gene_disc = {r["package_gene_id"] for r in disc}
    n_total = len(out)
    counts = {
        "probe_sets_total": n_total,
        "classes": dict(sorted(cls.items())),
        "probe_sets_with_one_eligible_gene": cls["eligible_direct"] + cls["eligible_via_history_replacement"],
        "probe_level": {
            "replaced_under_cutoff": len(rep),
            "discontinued_no_replacement": len(disc),
            "collision_successor_already_directly_mapped": sum(r["successor_directly_mapped"] == "yes" for r in rep),
        },
        "gene_level": {
            "package_entrez_ids": len(pkg_ids),
            "replaced_under_cutoff": len(gene_rep),
            "discontinued_no_replacement": len(gene_disc),
            "collision_successor_already_directly_mapped": len({r["package_gene_id"] for r in rep if r["successor_directly_mapped"] == "yes"}),
            "distinct_option_a_genes": len({r["option_a_gene_id"] for r in out if r["option_a_gene_id"]}),
            "v1_replaced_genes_only_in_multi_gene_probe_sets": len(v1_rep - single_genes),
            "v1_discontinued_genes_only_in_multi_gene_probe_sets": len(v1_disc - single_genes),
        },
        "accession_route_comparison": ACCESSION_ROUTE_2026_10_12,
    }
    checks = [
        ("each probe set classified exactly once", len({r["probe_set_id"] for r in out}) == n_total == sum(cls.values())),
        ("probe sets = single + multiple + none",
         n_total == sum(v for k, v in cls.items() if k not in ("multiple_mappings_excluded", "no_assignment_in_package"))
         + cls["multiple_mappings_excluded"] + cls["no_assignment_in_package"]),
        ("single-gene probe sets match 2026-10-12 figure (43,149)",
         n_total - cls["multiple_mappings_excluded"] - cls["no_assignment_in_package"] == 43149),
        ("is_multiple flag consistent with gene count",
         all(("1" in r["is_multiple_flag"]) == (r["n_package_genes"] > 1) for r in out)),
        ("no unresolved classes", not any(k.startswith("unresolved_") for k in cls)),
        ("v1 View A replaced genes (36) = in single-gene probe sets + only in multi-gene probe sets",
         len(v1_rep) == 36 and gene_rep == (v1_rep & single_genes) and (v1_rep - single_genes) <= multi_genes),
        ("v1 View A discontinued genes (48) = in single-gene probe sets + only in multi-gene probe sets",
         len(v1_disc) == 48 and gene_disc == (v1_disc & single_genes) and (v1_disc - single_genes) <= multi_genes),
        ("no mapping inferred for non-eligible probe sets",
         all(not r["option_a_gene_id"] for r in out if not r["option_a_class"].startswith("eligible"))),
    ]
    validation = {"status": "OK" if all(ok for _, ok in checks) else "FAILED",
                  "checks": [{"check": n, "status": "OK" if ok else "FAILED"} for n, ok in checks]}
    cols = ["probe_set_id", "n_package_genes", "package_gene_id", "option_a_class", "option_a_gene_id", "history_chain",
            "successor_directly_mapped", "is_multiple_flag"]
    files = {"probe_set_classification.tsv": tsv(out, cols)}
    return files, {"counts": counts, "validation": validation}


def produce(version: str) -> tuple[dict, dict]:
    """The Option A (D6-F) computation (unchanged): verify inputs, compute twice, check; return files and manifest."""
    src = verify_inputs()
    f1, m1 = compute(src)
    f2, m2 = compute(src)
    h1 = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f1.items()}
    det = {"runs_compared": 2, "identical": h1 == {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f2.items()} and m1 == m2,
           "output_sha256": h1}
    if not det["identical"] or m1["validation"]["status"] != "OK":
        print(json.dumps({"validation": m1["validation"], "determinism": det}, indent=2))
        raise SystemExit("VALIDATION OR DETERMINISM FAILED (nothing accepted)")
    manifest = {"purpose": "Counts for candidate Option A (GPL570). Not an approved mapping policy.",
                "cutoff_inclusive": CUTOFF, "sources": src, **m1, "determinism": det,
                "command": ".venv/bin/python -I scripts/annotation_gpl570_option_a_counts.py --version " + version}
    return {k: v.encode("utf-8") for k, v in f1.items()}, manifest


OUT = ROOT / "reports/annotation_audit/gpl570_option_a"
TABLES = ("probe_set_classification.tsv",)
REQUIRE_VENV = True  # D8-4 / Q3: .venv/bin/python -I
REQUIRE_EXECUTED_CODE = True  # executed code must equal the identity record (scripts/_executed_code.py)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--equivalent-to", default=None,
                    help="reference version whose table must be byte-identical (default: v1 for any version other than v1)")
    args = ap.parse_args(argv)
    ref = args.equivalent_to or (None if args.version == "v1" else "v1")
    try:
        out = ci.run_with_identity(ROOT, OUT / args.version, lambda staging: produce(args.version),
                                   manifest_name="counts_manifest.json", equivalent_to=(OUT / ref) if ref else None,
                                   equivalent_files=list(TABLES), require_venv=REQUIRE_VENV,
                                   executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
