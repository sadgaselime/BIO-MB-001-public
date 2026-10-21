#!/usr/bin/env python3
"""C15 — cohort-level probe presence (metadata only; decision support for D6; no policy is approved).

For GSE63060 (illuminaHumanv3, GPL6947), GSE63061 (illuminaHumanv4, GPL10558) and GSE99039 (GPL570):
  * reads ONLY the probe identifiers (first field of each data row) of the deposited Series Matrix;
    the remainder of each row (expression values) is never split, parsed, stored or analysed;
  * joins them to the retained annotation evidence:
      - Option A probe classifications (illumina_option_a/v1, PROVISIONAL; gpl570_option_a/v1, D6-F);
      - the accession route for the Illumina platforms, regenerated with the exact logic of
        scripts/annotation_illumina_route_comparison.py (v3) from the verified Bioconductor 3.23 tarballs;
  * counts what is present in each cohort.

It does not choose a route, assess biological validity, detection or expression, or cover GSE140829 (D19).
Every input is verified first; any mismatch stops the run before anything is written. The full computation
runs twice and must be byte-identical. Writes reports/annotation_audit/c15_cohort_probe_presence/<version>/
and never overwrites a version.
"""
from __future__ import annotations

import argparse
import csv
import gzip
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
from biomarker_project.gene_history_reconciliation import _sqlite_from_tar  # noqa: E402

_spec = importlib.util.spec_from_file_location("route_v3", ROOT / "scripts/annotation_illumina_route_comparison.py")
route = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(route)

REF = ROOT / "reference/bioconductor_3.23"
IOA = ROOT / "reports/annotation_audit/illumina_option_a/v1"
G570 = ROOT / "reports/annotation_audit/gpl570_option_a/v1"
RV3 = ROOT / "reports/annotation_audit/illumina_route_comparison/v3"
OUT = ROOT / "reports/annotation_audit/c15_cohort_probe_presence"
OPTA_ELIGIBLE = route.OPTA_ELIGIBLE

COHORTS = [  # cohort, GEO platform, annotation label, Option A table, route_v3 PLATFORMS index (None = no accession route)
    ("GSE63060", "GPL6947", "illuminaHumanv3", IOA / "illuminaHumanv3_probe_classification_PROVISIONAL.tsv", 0),
    ("GSE63061", "GPL10558", "illuminaHumanv4", IOA / "illuminaHumanv4_probe_classification_PROVISIONAL.tsv", 1),
    ("GSE99039", "GPL570", "hgu133plus2", G570 / "probe_set_classification.tsv", None),
]
GPL570_TSV_SHA256_D6F = "9e5f23fa8b10b3e120b518873905b79e5f338ca07ec83357e173d3a2ddea8d9c"  # cited in v7:609
# D5 R8 probe list (v7:608): XIST and 13 Y-chromosome probes, the same list for GSE63060 and GSE63061.
R8_PROBES = ["ILMN_1764573", "ILMN_1783142", "ILMN_1732039", "ILMN_1685690", "ILMN_1739587", "ILMN_2264634",
             "ILMN_1755537", "ILMN_2228976", "ILMN_2056795", "ILMN_1804958", "ILMN_2090059", "ILMN_1670821",
             "ILMN_1756506", "ILMN_2094332"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_series_matrix_ids(path: Path) -> dict:
    """Probe IDs and platform IDs only. Data rows are cut at the first tab; the value part is discarded unread."""
    platforms, ids, in_table, header_seen, n_data = [], [], False, False, 0
    with gzip.open(path, "rt", encoding="utf-8", errors="strict", newline="") as fh:
        for line in fh:
            if not in_table:
                if line.startswith("!Series_platform_id"):
                    platforms.append(line.split("\t", 1)[1].strip().strip('"'))
                elif line.startswith("!series_matrix_table_begin"):
                    in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            first = line.split("\t", 1)[0].strip().strip('"')
            if not header_seen:
                header_seen = True
                if first != "ID_REF":
                    raise SystemExit(f"STOP: {path.name}: table header does not start with ID_REF")
                continue
            ids.append(first)
            n_data += 1
    return {"platform_ids": platforms, "probe_ids": ids, "table_closed": in_table and header_seen, "n_rows": n_data}


def load_tsv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def verify_inputs() -> tuple[dict, list[str]]:
    """Hash and count checks. Returns (provenance, problems); the caller stops on any problem."""
    prov, problems = {"series_matrix": {}, "annotation": {}, "references": {}}, []
    refman = {e["file"]: e for e in json.loads((REF / "download_manifest.json").read_text())["files"]}
    v2man = json.loads((ROOT / "reports/annotation_audit/illumina_route_decision_matrix/v2/decision_matrix_manifest.json")
                       .read_text())["inputs_sha256"]
    for tar in ("illuminaHumanv3.db_1.26.0.tar.gz", "illuminaHumanv4.db_1.26.0.tar.gz", "org.Hs.eg.db_3.23.1.tar.gz"):
        h = sha256(REF / tar)
        prov["annotation"][f"reference/bioconductor_3.23/{tar}"] = h
        if h != refman[tar]["sha256"] or h != v2man[f"reference/bioconductor_3.23/{tar}"]:
            problems.append(f"{tar}: SHA-256 differs from reference download manifest or decision-matrix v2 manifest")
    if sha256(REF / "org.Hs.eg.db_3.23.1.tar.gz") != route.MISSING_ORG["sha256_recorded_2026_10_12"]:
        problems.append("org.Hs.eg.db_3.23.1.tar.gz: SHA-256 differs from the value recorded 2026-10-12")
    ioa = json.loads((IOA / "counts_manifest_PROVISIONAL.json").read_text())["determinism"]["output_sha256"]
    for name, exp in ioa.items():
        h = sha256(IOA / name)
        prov["annotation"][f"reports/annotation_audit/illumina_option_a/v1/{name}"] = h
        if h != exp:
            problems.append(f"illumina_option_a/v1/{name}: SHA-256 differs from its manifest")
    h = sha256(G570 / "probe_set_classification.tsv")
    prov["annotation"]["reports/annotation_audit/gpl570_option_a/v1/probe_set_classification.tsv"] = h
    if h != GPL570_TSV_SHA256_D6F:
        problems.append("gpl570_option_a/v1/probe_set_classification.tsv: SHA-256 differs from the D6-F record (v7:609)")
    rv3 = json.loads((RV3 / "comparison_manifest.json").read_text())["determinism"]["output_sha256"]
    for name in ("route_comparison_metrics.tsv", "metric_reconciliation_probes.tsv"):
        h = sha256(RV3 / name)
        prov["references"][f"reports/annotation_audit/illumina_route_comparison/v3/{name}"] = h
        if h != rv3[name]:
            problems.append(f"illumina_route_comparison/v3/{name}: SHA-256 differs from its manifest")
    for cohort, gpl, *_ in COHORTS:
        f = ROOT / f"data/raw/{cohort}/{cohort}_series_matrix.txt.gz"
        man = json.loads((ROOT / f"data/raw/{cohort}/download_manifest.json").read_text())["files"]
        exp = man[f.name]["current"]
        insp = json.loads((ROOT / f"reports/dataset_audit/{cohort}/files/{f.name}.inspection.json").read_text())
        audit = json.loads((ROOT / f"reports/dataset_audit/{cohort}/audit_report.json").read_text())
        h = sha256(f)
        prov["series_matrix"][cohort] = {"path": str(f.relative_to(ROOT)), "sha256": h, "bytes": f.stat().st_size,
                                         "expected_unique_ids": insp["n_unique_feature_ids"],
                                         "audit_platform_id": audit["dataset"]["platform_id"]}
        if h != exp["sha256"] or f.stat().st_size != exp["local_size"]:
            problems.append(f"{cohort}: Series Matrix SHA-256 or size differs from download manifest")
        if audit["dataset"]["platform_id"] != gpl:
            problems.append(f"{cohort}: audit platform {audit['dataset']['platform_id']} != expected {gpl}")
    return prov, problems


def accession_classes(idx: int, orgmap) -> dict[str, tuple[str, frozenset]]:
    """Per-probe accession-route class, with the exact query and class rule of route-comparison v3."""
    label, tar, member, query, opt_tsv, _ = route.PLATFORMS[idx]
    rows = load_tsv(IOA / opt_tsv)
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_c15_") as tmp:
        db = _sqlite_from_tar(REF / tar, member, Path(tmp))
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        acc_rows = con.execute(query).fetchall()
        con.close()
    acc = defaultdict(set)
    for pid, a in acc_rows:
        if a is not None and str(a).strip():
            acc[str(pid)].add(str(a).strip())
    out = {}
    for r in rows:
        pid = r["probe_id"]
        if pid not in acc:
            out[pid] = ("no_accession", frozenset(), "")
        else:
            gs = frozenset().union(*(orgmap.get(a, frozenset()) for a in acc[pid]))
            c = "accession_unmatched" if not gs else ("unique" if len(gs) == 1 else "ambiguous")
            out[pid] = (c, gs, ";".join(sorted(acc[pid])))
    return out


def route_status(oa_class: str, oa_gene: str, acc_class: str | None, acc_genes: frozenset) -> str:
    e = oa_class in OPTA_ELIGIBLE
    if acc_class is None:
        return "option_a_eligible" if e else "option_a_not_eligible"
    if e and acc_class == "unique":
        return "both_concordant" if oa_gene in acc_genes else "both_discordant"
    if e:
        return "option_a_only"
    if acc_class == "unique":
        return "accession_only"
    return "neither"


def regeneration_checks(label: str, ann: list[dict], acls: dict) -> tuple[list[tuple[str, bool]], dict]:
    """Regenerated accession route must reproduce route-comparison v3 exactly for this platform."""
    metrics = {}
    for r in load_tsv(RV3 / "route_comparison_metrics.tsv"):
        if r["platform"] == label:
            metrics[(r["section"], r["measure"])] = r["value"]
    exp_classes = json.loads(metrics[("accession_route_assignments", "classes")])
    got_classes = dict(sorted(Counter(c for c, _, _ in acls.values()).items()))
    both = disc = 0
    recon = set()
    for r in ann:
        c, gs, _ = acls[r["probe_id"]]
        e = r["option_a_class"] in OPTA_ELIGIBLE
        if e and c == "unique":
            both += 1
            disc += r["option_a_gene_id"] not in gs
        if r["n_package_genes"] == "1" and c == "unique":
            m2 = "same" if r["package_gene_id"] in gs else "different"
            m1 = ("concordant" if r["option_a_gene_id"] in gs else "discordant") if e else "not_in_M1"
            if (m2, m1) != ("same", "concordant"):
                recon.add(r["probe_id"])
    exp_recon = {r["probe_id"] for r in load_tsv(RV3 / "metric_reconciliation_probes.tsv") if r["platform"] == label}
    checks = [
        (f"{label}: regenerated accession classes equal route-comparison v3 ({exp_classes})", got_classes == exp_classes),
        (f"{label}: both-assign count equals v3 ({metrics[('route_comparison', 'both_assign_one_gene')]})",
         str(both) == metrics[("route_comparison", "both_assign_one_gene")]),
        (f"{label}: discordant count equals v3 ({metrics[('route_comparison', 'discordant')]})",
         str(disc) == metrics[("route_comparison", "discordant")]),
        (f"{label}: reconciliation probe set equals v3 ({len(exp_recon)} probes)", recon == exp_recon),
    ]
    return checks, {"classes": got_classes, "both_assign": both, "discordant": disc, "reconciliation_probes": len(recon)}


def compute(orgmap) -> dict:
    checks, rows_out, counts, regen = [], [], [], {}
    for cohort, gpl, label, opt_path, idx in COHORTS:
        sm = read_series_matrix_ids(ROOT / f"data/raw/{cohort}/{cohort}_series_matrix.txt.gz")
        ids = sm["probe_ids"]
        idset = set(ids)
        ann = load_tsv(opt_path)
        key = "probe_id" if "probe_id" in ann[0] else "probe_set_id"
        annmap = {r[key]: r for r in ann}
        acls = accession_classes(idx, orgmap) if idx is not None else None
        if acls is not None:
            c, info = regeneration_checks(label, ann, acls)
            checks += c
            regen[label] = info
        checks += [
            (f"{cohort}: Series Matrix table opened and closed", sm["table_closed"]),
            (f"{cohort}: Series Matrix platform is {gpl}", sm["platform_ids"] == [gpl]),
            (f"{cohort}: no duplicate probe IDs", len(ids) == len(idset)),
            (f"{cohort}: no empty probe IDs", all(ids)),
            (f"{cohort}: probe IDs = dataset-audit inspection count", len(idset) == EXPECTED[cohort]),
            (f"{cohort}: annotation table probe IDs unique", len(annmap) == len(ann)),
        ]
        status = Counter()
        oa_present = Counter()
        acc_present = Counter()
        genes_oa, genes_acc = set(), set()
        for pid in sorted(idset | set(annmap)):
            r = annmap.get(pid)
            in_sm, in_ann = pid in idset, r is not None
            oa_class = r["option_a_class"] if r else "not_in_annotation_table"
            oa_gene = r["option_a_gene_id"] if r else ""
            ac, ag, accs = (acls.get(pid, ("not_in_annotation_table", frozenset(), "")) if acls is not None
                            else (None, frozenset(), ""))
            st = route_status(oa_class, oa_gene, ac, ag) if in_ann else "not_in_annotation_table"
            if in_sm:
                status[st] += 1
                oa_present[oa_class] += 1
                if ac is not None:
                    acc_present[ac] += 1
                if oa_class in OPTA_ELIGIBLE:
                    genes_oa.add(oa_gene)
                if ac == "unique":
                    genes_acc.add(next(iter(ag)))
            rows_out.append({"cohort": cohort, "platform": label, "probe_id": pid,
                             "in_series_matrix": "yes" if in_sm else "no", "in_annotation_table": "yes" if in_ann else "no",
                             "option_a_class": oa_class, "option_a_gene_id": oa_gene,
                             "accession_class": "" if ac is None else ac,
                             "accession_gene_ids": ";".join(sorted(ag)), "accessions": accs, "route_status": st,
                             "d5_r8_probe": "yes" if (gpl != "GPL570" and pid in R8_PROBES) else ""})
        n_ann_absent = sum(1 for p in annmap if p not in idset)
        c = [("series_matrix_probe_ids", len(idset)),
             ("series_matrix_ids_not_in_annotation_table", status["not_in_annotation_table"]),
             ("annotation_table_probe_ids", len(annmap)),
             ("annotation_table_ids_not_in_series_matrix", n_ann_absent)]
        c += [(f"present_option_a_class:{k}", v) for k, v in sorted(oa_present.items())]
        c += [("present_option_a_eligible_probes", sum(oa_present[k] for k in OPTA_ELIGIBLE)),
              ("present_option_a_distinct_genes", len(genes_oa))]
        if acls is not None:
            c += [(f"present_accession_class:{k}", v) for k, v in sorted(acc_present.items())]
            c += [("present_accession_unique_probes", acc_present["unique"]),
                  ("present_accession_distinct_genes", len(genes_acc)),
                  ("present_route:both_concordant", status["both_concordant"]),
                  ("present_route:both_discordant", status["both_discordant"]),
                  ("platform_route:both_discordant", regen[label]["discordant"]),
                  ("present_route:option_a_only", status["option_a_only"]),
                  ("present_route:accession_only", status["accession_only"]),
                  ("present_route:neither", status["neither"]),
                  ("present_genes_both_routes", len(genes_oa & genes_acc)),
                  ("present_genes_option_a_only", len(genes_oa - genes_acc)),
                  ("present_genes_accession_only", len(genes_acc - genes_oa)),
                  ("d5_r8_probes_listed", len(R8_PROBES)),
                  ("d5_r8_probes_present", sum(p in idset for p in R8_PROBES))]
            checks.append((f"{cohort}: present route categories + absent-from-table sum to Series Matrix IDs",
                           sum(status.values()) == len(idset)))
        else:
            c += [("present_option_a_not_eligible_probes", status["option_a_not_eligible"])]
        checks.append((f"{cohort}: present Option A classes sum to Series Matrix IDs", sum(oa_present.values()) == len(idset)))
        counts += [{"cohort": cohort, "platform": label, "measure": m, "value": v} for m, v in c]
    return {"rows": rows_out, "counts": counts, "checks": checks, "regeneration": regen}


EXPECTED: dict[str, int] = {}


def serialize(res: dict) -> dict[str, bytes]:
    def tsv_bytes(rows):
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        return buf.getvalue().encode()
    return {"probe_presence.tsv": tsv_bytes(res["rows"]), "presence_counts.tsv": tsv_bytes(res["counts"])}


def report(res: dict, prov: dict, version: str) -> str:
    by = defaultdict(dict)
    for r in res["counts"]:
        by[r["cohort"]][r["measure"]] = r["value"]
    L = [f"# C15 — cohort probe presence ({version})", "",
         "**Metadata only. Decision support for the D6 Illumina package; nothing here approves a route, rule, release or pin.**",
         "Only Series Matrix probe identifiers were read; expression values were not parsed, stored or analysed.",
         "Option A tables are PROVISIONAL (illumina_option_a/v1) or D6-F (GPL570). The accession route was regenerated",
         "with the route-comparison v3 logic and reproduced v3 exactly (checks below). GSE140829 is out of scope (D19).", "",
         "## Presence by cohort", "", "| Measure | GSE63060 (illuminaHumanv3) | GSE63061 (illuminaHumanv4) | GSE99039 (GPL570) |",
         "|---|---|---|---|"]
    measures = []
    for c in ("GSE63060", "GSE63061", "GSE99039"):
        for m in by[c]:
            if m not in measures:
                measures.append(m)
    for m in measures:
        L.append(f"| {m} | " + " | ".join(f"{by[c][m]:,}" if m in by[c] else "—" for c in ("GSE63060", "GSE63061", "GSE99039")) + " |")
    L += ["", "Route categories (Illumina, probes present in the Series Matrix): both_concordant = both routes assign the same",
          "single gene; both_discordant = both assign one gene, different genes; option_a_only = Option A eligible, accession",
          "route not unique; accession_only = accession unique, Option A not eligible; neither = no single-gene assignment.",
          "`platform_route:both_discordant` is the platform-wide count from decision-matrix v2, for comparison.", "",
          "## What this does and does not establish", "",
          "- **Establishes:** which annotated probes are deposited in each cohort's Series Matrix, per route category.",
          "- **Does not establish:** which route to adopt; biological validity or accuracy of any mapping; whether a probe is",
          "  detectably expressed; gene-level reliability; anything for GSE140829; whether gene history may be used for Illumina.",
          "- Platform-wide coverage figures elsewhere are not cohort coverage; these counts are.", "",
          "## Verification", ""]
    L += [f"- [{'PASS' if ok else 'FAIL'}] {name}" for name, ok in res["checks"]]
    L += ["", "## Inputs (SHA-256)", ""]
    for sect in ("series_matrix", "annotation", "references"):
        for k, v in prov[sect].items():
            L.append(f"- `{k}`: `{v['sha256'] if isinstance(v, dict) else v}`")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", default="v1")
    a = ap.parse_args()
    out = OUT / a.version
    if out.exists():
        raise SystemExit(f"STOP: {out} exists; versions are never overwritten")
    prov, problems = verify_inputs()
    if problems:
        raise SystemExit("STOP — INPUT VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    for c in prov["series_matrix"]:
        EXPECTED[c] = prov["series_matrix"][c]["expected_unique_ids"]
    orgmap = route.load_org_map()
    if orgmap is None:
        raise SystemExit("STOP: org.Hs.eg.db 3.23.1 not retained")
    r1, r2 = compute(orgmap), compute(orgmap)
    s1, s2 = serialize(r1), serialize(r2)
    if s1 != s2:
        raise SystemExit("STOP: two runs are not byte-identical")
    failed = [n for n, ok in r1["checks"] if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED (nothing written):\n  " + "\n  ".join(failed))
    out.mkdir(parents=True)
    for name, b in s1.items():
        (out / name).write_bytes(b)
    (out / "REPORT.md").write_text(report(r1, prov, a.version), encoding="utf-8")
    manifest = {
        "status": "C15 metadata-only probe-presence evidence; decision support only; approves nothing",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": {"cohorts": [c[0] for c in COHORTS], "excluded": "GSE140829 (D19)",
                  "expression_values": "not parsed, stored or analysed; each data row is cut at its first tab"},
        "command": f"python3 -I scripts/c15_cohort_probe_presence.py --version {a.version}",
        "generator_sha256": sha256(Path(__file__)),
        "route_logic_sha256": sha256(ROOT / "scripts/annotation_illumina_route_comparison.py"),
        "environment": {"python": sys.version, "platform": _platform.platform()},
        "inputs": prov,
        "regeneration_vs_route_comparison_v3": r1["regeneration"],
        "validation": [{"check": n, "pass": ok} for n, ok in r1["checks"]],
        "determinism": {"runs_compared": 2, "identical": True,
                        "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in s1.items()}},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}; {len(r1['checks'])} checks passed")


if __name__ == "__main__":
    main()
