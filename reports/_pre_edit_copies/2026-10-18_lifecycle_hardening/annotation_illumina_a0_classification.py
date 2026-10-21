#!/usr/bin/env python3
"""D6-G final A0 classification for the Illumina platforms (approved 2026-10-17; v7:609).

Scope: GSE63060 (GPL6947, illuminaHumanv3.db 1.26.0) and GSE63061 (GPL10558, illuminaHumanv4.db 1.26.0).
Rules (D6-G, Option A0):
  * each probe takes the Entrez ID(s) in the package `probes` table;
  * NO gene-history reconciliation: an ID absent from the org.Hs.eg.db 3.23.1 `genes` table is unmapped;
  * probes with more than one package Entrez ID are excluded (v5:541);
  * accession comparison (annotation-stability check only, logic of route-comparison v3): a probe's
    unversioned accessions are matched to org.Hs.eg.db accessions ∪ refseq; discordant probes are retained
    under the package mapping and flagged; accession_unmatched / ambiguous are reported; probes eligible
    only by accession are never added;
  * presence per cohort = the cohort's Series Matrix ID_REF column (expression values are never parsed).
No gene-history file is read. D6-F (GPL570) and D19 (GSE140829) are out of scope. Inputs are verified first;
any failed integrity check stops the run. The computation runs twice and must be byte-identical. Runs under the
code-identity lifecycle (src/biomarker_project/code_identity.py): outputs are staged, verified and atomically
finalized to reports/annotation_audit/illumina_a0/<version>/ (never overwritten); a version other than v1 must
reproduce the v1 tables byte for byte. Failed runs are kept as <version>.FAILED-<run_id>/ and are never accepted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import platform as _platform
import sqlite3
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from biomarker_project.gene_history_reconciliation import _sqlite_from_tar  # noqa: E402  (archive extraction only)
from biomarker_project import code_identity as ci  # noqa: E402  (run lifecycle, D8-3)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


route = _load("route_v3", "scripts/annotation_illumina_route_comparison.py")   # accession map + query
c15 = _load("c15_v1", "scripts/c15_cohort_probe_presence.py")                   # Series Matrix ID reader

REF = ROOT / "reference/bioconductor_3.23"
OUT = ROOT / "reports/annotation_audit/illumina_a0"
IOA = ROOT / "reports/annotation_audit/illumina_option_a/v1"     # comparison only, never used as input rules
ORG_TAR, ORG_MEMBER = "org.Hs.eg.db_3.23.1.tar.gz", "org.Hs.eg.db/inst/extdata/org.Hs.eg.sqlite"
PLATFORMS = [  # label, tarball, sqlite member, cohort, GEO platform, Option A table (comparison only)
    ("illuminaHumanv3", "illuminaHumanv3.db_1.26.0.tar.gz", "illuminaHumanv3.db/inst/extdata/illuminaHumanv3.sqlite",
     "GSE63060", "GPL6947", "illuminaHumanv3_probe_classification_PROVISIONAL.tsv"),
    ("illuminaHumanv4", "illuminaHumanv4.db_1.26.0.tar.gz", "illuminaHumanv4.db/inst/extdata/illuminaHumanv4.sqlite",
     "GSE63061", "GPL10558", "illuminaHumanv4_probe_classification_PROVISIONAL.tsv"),
]
REPORTED = {"discordant_present": {"GSE63060": 9, "GSE63061": 15}, "discordant_distinct_present": 15,
            "discordant_platform": {"illuminaHumanv3": 10, "illuminaHumanv4": 16},
            "replacement_unmapped_present": {"GSE63060": 45, "GSE63061": 41},
            "successor_genes_without_present_probe": {"GSE63060": 10, "GSE63061": 15}}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def classify(package_genes: set, baseline: set, acc_class: str, acc_genes: frozenset) -> dict:
    """A0 class and accession-comparison status for one probe (pure; unit-tested)."""
    if not package_genes:
        a0, gene, reason = "unmapped_no_package_gene", "", "no Entrez ID in package probes table"
    elif len(package_genes) > 1:
        a0, gene, reason = "excluded_multi_entrez", "", "more than one package Entrez ID (v5:541)"
    else:
        g = next(iter(package_genes))
        if g in baseline:
            a0, gene, reason = "eligible", g, ""
        else:
            a0, gene, reason = "unmapped_not_in_snapshot", "", "package Entrez ID absent from org.Hs.eg.db 3.23.1; not reconciled (A0)"
    if a0 == "eligible":
        if acc_class == "unique":
            status = "concordant" if gene in acc_genes else "discordant"
        else:
            status = acc_class   # accession_unmatched | ambiguous | no_accession
    else:
        status = "accession_only_not_added" if acc_class == "unique" else f"not_eligible_{acc_class}"
    return {"a0_class": a0, "a0_gene_id": gene, "reason": reason, "comparison_status": status}


def verify_inputs() -> tuple[dict, list[str]]:
    prov, problems = {"archives": {}, "series_matrix": {}, "comparison_only": {}}, []
    refman = {e["file"]: e for e in json.loads((REF / "download_manifest.json").read_text())["files"]}
    for tar in [p[1] for p in PLATFORMS] + [ORG_TAR]:
        h = sha256(REF / tar)
        prov["archives"][tar] = {"sha256": h, "manifest_sha256": refman[tar]["sha256"], "version_file": refman[tar].get("version")}
        if h != refman[tar]["sha256"]:
            problems.append(f"{tar}: SHA-256 differs from reference/bioconductor_3.23/download_manifest.json")
    for _, _, _, cohort, gpl, opt in PLATFORMS:
        f = ROOT / f"data/raw/{cohort}/{cohort}_series_matrix.txt.gz"
        exp = json.loads((ROOT / f"data/raw/{cohort}/download_manifest.json").read_text())["files"][f.name]["current"]
        insp = json.loads((ROOT / f"reports/dataset_audit/{cohort}/files/{f.name}.inspection.json").read_text())
        h = sha256(f)
        prov["series_matrix"][cohort] = {"path": str(f.relative_to(ROOT)), "sha256": h, "expected_ids": insp["n_unique_feature_ids"],
                                         "platform": gpl}
        if h != exp["sha256"]:
            problems.append(f"{cohort}: Series Matrix SHA-256 differs from download manifest")
        ioa = json.loads((IOA / "counts_manifest_PROVISIONAL.json").read_text())["determinism"]["output_sha256"]
        ho = sha256(IOA / opt)
        prov["comparison_only"][f"illumina_option_a/v1/{opt}"] = ho
        if ho != ioa[opt]:
            problems.append(f"{opt}: differs from its Option A manifest (comparison input)")
    return prov, problems


def read_db(tar: str, member: str, queries: list[str]) -> list[list]:
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_a0_") as tmp:
        db = _sqlite_from_tar(REF / tar, member, Path(tmp))
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        res = [con.execute(q).fetchall() for q in queries]
        con.close()
    return res


def compute(baseline: set, orgmap: dict, expected_ids: dict) -> dict:
    rows, counts, checks, comparison, disc_rows = [], [], [], {}, []
    for label, tar, member, cohort, gpl, opt in PLATFORMS:
        probes, accs = read_db(tar, member, ["SELECT probe_id, gene_id FROM probes", "SELECT probe_id, accession FROM accessions"])
        genes = defaultdict(set)
        for pid, gid in probes:
            genes[str(pid)]
            if gid is not None and str(gid).strip():
                genes[str(pid)].add(str(gid).strip())
        acc = defaultdict(set)
        for pid, a in accs:
            if a is not None and str(a).strip():
                acc[str(pid)].add(str(a).strip())
        sm = c15.read_series_matrix_ids(ROOT / f"data/raw/{cohort}/{cohort}_series_matrix.txt.gz")
        present = set(sm["probe_ids"])
        checks += [(f"{cohort}: Series Matrix platform {gpl}", sm["platform_ids"] == [gpl]),
                   (f"{cohort}: Series Matrix IDs unique and = inspection count ({expected_ids[cohort]})",
                    len(present) == len(sm["probe_ids"]) == expected_ids[cohort]),
                   (f"{label}: every accession probe ID is a package probe", set(acc) <= set(genes))]
        cls_platform, cls_present, cmp_platform, cmp_present = Counter(), Counter(), Counter(), Counter()
        elig_genes_platform, elig_genes_present = set(), set()
        for pid in sorted(genes):
            if pid in acc:
                gs = frozenset().union(*(orgmap.get(a, frozenset()) for a in acc[pid]))
                ac = "accession_unmatched" if not gs else ("unique" if len(gs) == 1 else "ambiguous")
            else:
                gs, ac = frozenset(), "no_accession"
            r = classify(genes[pid], baseline, ac, gs)
            if r["a0_class"] == "eligible" and r["a0_gene_id"] not in genes[pid]:
                checks.append((f"{label}:{pid}: eligible gene differs from package gene (gene-history use)", False))
            is_present = pid in present
            row = {"platform": label, "cohort": cohort, "probe_id": pid, "in_series_matrix": "yes" if is_present else "no",
                   "n_package_genes": len(genes[pid]), "package_gene_ids": ";".join(sorted(genes[pid], key=int)),
                   "a0_class": r["a0_class"], "a0_gene_id": r["a0_gene_id"], "exclusion_or_unmapped_reason": r["reason"],
                   "accession_class": ac, "accession_gene_ids": ";".join(sorted(gs, key=int)),
                   "accessions": ";".join(sorted(acc.get(pid, ()))), "comparison_status": r["comparison_status"],
                   "discordant_flag": "yes" if r["comparison_status"] == "discordant" else ""}
            rows.append(row)
            cls_platform[r["a0_class"]] += 1
            cmp_platform[r["comparison_status"]] += 1
            if r["a0_class"] == "eligible":
                elig_genes_platform.add(r["a0_gene_id"])
            if is_present:
                cls_present[r["a0_class"]] += 1
                cmp_present[r["comparison_status"]] += 1
                if r["a0_class"] == "eligible":
                    elig_genes_present.add(r["a0_gene_id"])
            if row["discordant_flag"]:
                disc_rows.append({k: row[k] for k in ("platform", "cohort", "probe_id", "in_series_matrix",
                                                      "a0_gene_id", "accession_gene_ids", "accessions")})
        n = len(genes)
        checks += [(f"{label}: every probe classified once", sum(cls_platform.values()) == n),
                   (f"{label}: present classes sum to present package IDs", sum(cls_present.values()) == len(present & set(genes)))]
        for scope, cls, cmp_, ng, tot in (("platform", cls_platform, cmp_platform, elig_genes_platform, n),
                                         ("cohort_present", cls_present, cmp_present, elig_genes_present, len(present))):
            counts.append({"platform": label, "cohort": cohort, "scope": scope, "measure": "probes_total", "value": tot})
            for k, v in sorted(cls.items()):
                counts.append({"platform": label, "cohort": cohort, "scope": scope, "measure": f"a0_class:{k}", "value": v})
            counts.append({"platform": label, "cohort": cohort, "scope": scope, "measure": "eligible_distinct_genes", "value": len(ng)})
            for k, v in sorted(cmp_.items()):
                counts.append({"platform": label, "cohort": cohort, "scope": scope, "measure": f"comparison:{k}", "value": v})
        counts.append({"platform": label, "cohort": cohort, "scope": "cohort_present", "measure": "series_matrix_ids_not_in_package_table",
                       "value": len(present - set(genes))})
        # Comparison with the provisional Option A table (consistency only; never an input to A0 rules).
        oa = {r["probe_id"]: r for r in csv.DictReader(open(IOA / opt, encoding="utf-8"), delimiter="\t")}
        a0 = {r["probe_id"]: r for r in rows if r["platform"] == label}
        same = lambda f: {p for p, r in a0.items() if f(r)}
        oa_set = lambda cs: {p for p, r in oa.items() if r["option_a_class"] in cs}
        checks += [
            (f"{label}: A0 eligible == Option A eligible_direct", same(lambda r: r["a0_class"] == "eligible") == oa_set({"eligible_direct"})),
            (f"{label}: A0 multi-ID exclusions == Option A multiple_mappings_excluded",
             same(lambda r: r["a0_class"] == "excluded_multi_entrez") == oa_set({"multiple_mappings_excluded"})),
            (f"{label}: A0 no-package-gene == Option A no_assignment_in_package",
             same(lambda r: r["a0_class"] == "unmapped_no_package_gene") == oa_set({"no_assignment_in_package"})),
            (f"{label}: A0 not-in-snapshot == all other single-gene Option A classes",
             same(lambda r: r["a0_class"] == "unmapped_not_in_snapshot")
             == {p for p, r in oa.items() if r["n_package_genes"] == "1" and r["option_a_class"] != "eligible_direct"}),
        ]
        rep_present = {p for p, r in oa.items() if r["option_a_class"] == "eligible_via_history_replacement" and p in present}
        succ = {oa[p]["option_a_gene_id"] for p in rep_present}
        comparison[cohort] = {
            "replacement_derived_present_now_unmapped": len(rep_present & same(lambda r: r["a0_class"] == "unmapped_not_in_snapshot")),
            "replacement_derived_present_total": len(rep_present),
            "option_a_successor_genes_without_present_a0_probe": len(succ - elig_genes_present),
            "discordant_present": cmp_present["discordant"], "discordant_platform": cmp_platform["discordant"]}
    pres_disc = {r["probe_id"] for r in disc_rows if r["in_series_matrix"] == "yes"}
    comparison["discordant_distinct_present"] = len(pres_disc)
    return {"rows": rows, "counts": counts, "checks": checks, "comparison": comparison, "discordant": disc_rows}


def to_tsv(rows) -> bytes:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode()


def produce(version: str) -> tuple[dict, dict]:
    """The D6-G A0 computation (unchanged rules): verify inputs, compute twice, check; return files and manifest."""
    prov, problems = verify_inputs()
    if problems:
        raise SystemExit("STOP — INPUT VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    (genes_rows,) = read_db(ORG_TAR, ORG_MEMBER, ["SELECT gene_id FROM genes"])
    baseline = {str(g) for (g,) in genes_rows}
    orgmap = route.load_org_map()
    exp = {c: prov["series_matrix"][c]["expected_ids"] for c in prov["series_matrix"]}
    r1, r2 = compute(baseline, orgmap, exp), compute(baseline, orgmap, exp)
    files = {"a0_probe_classification.tsv": to_tsv(r1["rows"]), "a0_counts.tsv": to_tsv(r1["counts"]),
             "a0_discordant_probes.tsv": to_tsv(r1["discordant"])}
    if files != {"a0_probe_classification.tsv": to_tsv(r2["rows"]), "a0_counts.tsv": to_tsv(r2["counts"]),
                 "a0_discordant_probes.tsv": to_tsv(r2["discordant"])}:
        raise SystemExit("STOP: two runs are not byte-identical")
    failed = [n for n, ok in r1["checks"] if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED (nothing accepted):\n  " + "\n  ".join(failed[:20]))
    cmpv = r1["comparison"]
    comparison_vs_reported = {
        "discordant_present": {c: {"a0": cmpv[c]["discordant_present"], "reported": REPORTED["discordant_present"][c]} for c in ("GSE63060", "GSE63061")},
        "discordant_distinct_present": {"a0": cmpv["discordant_distinct_present"], "reported": REPORTED["discordant_distinct_present"]},
        "discordant_platform": {p[0]: {"a0": cmpv[p[3]]["discordant_platform"], "reported": REPORTED["discordant_platform"][p[0]]} for p in PLATFORMS},
        "replacement_derived_present_now_unmapped": {c: {"a0": cmpv[c]["replacement_derived_present_now_unmapped"],
                                                         "reported": REPORTED["replacement_unmapped_present"][c]} for c in ("GSE63060", "GSE63061")},
        "option_a_successor_genes_without_present_a0_probe": {c: {"a0": cmpv[c]["option_a_successor_genes_without_present_a0_probe"],
                                                                  "reported": REPORTED["successor_genes_without_present_probe"][c]} for c in ("GSE63060", "GSE63061")},
    }
    manifest = {
        "status": "D6-G final A0 classification (Option A0, approved 2026-10-17, v7:609). Not an annotation pin; "
                  "no package installed; no analysis authorized. D6-F/GPL570 and D19/GSE140829 out of scope.",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": f".venv/bin/python -I scripts/annotation_illumina_a0_classification.py --version {version}",
        "generator_sha256": sha256(Path(__file__)),
        "accession_comparison_logic": {"script": "scripts/annotation_illumina_route_comparison.py",
                                       "sha256": sha256(ROOT / "scripts/annotation_illumina_route_comparison.py"),
                                       "used": "load_org_map (org.Hs.eg.db accessions ∪ refseq)"},
        "series_matrix_reader": {"script": "scripts/c15_cohort_probe_presence.py", "sha256": sha256(ROOT / "scripts/c15_cohort_probe_presence.py")},
        "gene_history_used": False,
        "snapshot": {"org.Hs.eg.db": "3.23.1", "entrez_source_date": "2026-Mar18", "baseline_gene_ids": len(baseline)},
        "environment": {"python": sys.version, "platform": _platform.platform(), "sqlite": sqlite3.sqlite_version},
        "inputs": prov,
        "validation": [{"check": n, "pass": ok} for n, ok in r1["checks"]],
        "comparison_vs_reported_option_a_evidence": comparison_vs_reported,
        "determinism": {"runs_compared": 2, "identical": True,
                        "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}},
    }
    return files, manifest


TABLES = ("a0_probe_classification.tsv", "a0_counts.tsv", "a0_discordant_probes.tsv")
REQUIRE_VENV = True  # D8-4 / Q3: .venv/bin/python -I


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", default="v1")
    ap.add_argument("--equivalent-to", default=None,
                    help="reference version whose tables must be byte-identical (default: v1 for any version other than v1)")
    a = ap.parse_args(argv)
    ref = a.equivalent_to or (None if a.version == "v1" else "v1")
    try:
        out = ci.run_with_identity(ROOT, OUT / a.version, lambda staging: produce(a.version), manifest_name="manifest.json",
                                   equivalent_to=(OUT / ref) if ref else None, equivalent_files=list(TABLES),
                                   require_venv=REQUIRE_VENV)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
