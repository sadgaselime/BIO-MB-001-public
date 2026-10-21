#!/usr/bin/env python3
"""Illumina annotation-route decision matrix, v2 (assessment only; no mapping policy is selected or approved).

Corrects the wording, framing and validation documentation of v1 as identified in
reports/annotation_audit/illumina_route_decision_matrix/REVIEW_v1.md (R1-R10). v1 and its generator
(scripts/annotation_illumina_route_decision_matrix.py) are left unchanged.

Every metric is recomputed here from retained sources:
  * reference/bioconductor_3.23/ package and org.Hs.eg.db tarballs (raw sources; fully reconstructable);
  * reports/annotation_audit/ncbi_gene_history/v1/gene_history_reconciliation.tsv (retained, derived records).
    The raw NCBI gene_history.gz behind it is NOT retained, so every Option A figure that depends on
    gene-history replacement is reconstructable only from those retained records (marked "partial").
Recomputed figures are compared with the route-comparison v3 manifest, the Option A v1 tables and the
probe-level records in v3/metric_reconciliation_probes.tsv. No GEO data are read; nothing is installed.
Writes reports/annotation_audit/illumina_route_decision_matrix/<version>/ and never overwrites a version.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import platform as _platform
import re
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from biomarker_project.gene_history_reconciliation import _sqlite_from_tar, file_hashes, tsv  # noqa: E402

DM = ROOT / "reports/annotation_audit/illumina_route_decision_matrix"
V3 = ROOT / "reports/annotation_audit/illumina_route_comparison/v3"
IOA = ROOT / "reports/annotation_audit/illumina_option_a/v1"
GH = ROOT / "reports/annotation_audit/ncbi_gene_history/v1"
REF = ROOT / "reference/bioconductor_3.23"
_spec = importlib.util.spec_from_file_location("route_cmp", ROOT / "scripts/annotation_illumina_route_comparison.py")
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

STATUSES = ("decisive", "supportive", "unresolved")
RESTATES = "restates C01 (not counted)"
ADVANTAGES = ("Option A", "accession route", "neither", "not determinable", RESTATES)
COLUMNS = ["platform", "cohort_context", "criterion_id", "criterion", "option_a_evidence", "accession_route_evidence",
           "joint_evidence", "advantage", "derived_from", "limitation", "status", "reconstruction", "sources"]
ORG_TAR, ORG_MEMBER = "org.Hs.eg.db_3.23.1.tar.gz", "org.Hs.eg.db/inst/extdata/org.Hs.eg.sqlite"
CHIP_GENES = "SELECT probe_id, gene_id FROM probes"
LUMI_TABLE = "HumanHT12_V4_0_R2_15002873_B"
LUMI_GENES = f"SELECT t.Probe_Id, trim(m.EntrezID) FROM {LUMI_TABLE} t LEFT JOIN nuID_MappingInfo m ON m.nuID = t.nuID"
SRC_GENES = {"illuminaHumanv3": CHIP_GENES, "illuminaHumanv4": CHIP_GENES, "lumi HT-12 v4 R2": LUMI_GENES}
ELIGIBLE = ("eligible_direct", "eligible_via_history_replacement")
NOT_IN_M1 = "not_in_M1 (Option A not eligible)"
FULL = "full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs)"
PARTIAL = ("partial: accession-route side full; Option A side depends on the retained gene-history v1 records "
           "(raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently)")
PARTIAL_OA = ("partial: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, "
              "so those records cannot be rebuilt independently)")
REVIEW_V1_SHA256 = "a130d99f9fd31438c9506727f1d2d2096969025424fdf288d078529f09359f96"  # REVIEW_v1.md as written 2026-10-13
GH_NOTE = ("Option A replacement-dependent figures trace to the retained gene-history v1 records (the human records the "
           "audit used, kept verbatim in gene_history_reconciliation.tsv); the raw NCBI gene_history.gz (SHA-256 bcb85c8f…) is not "
           "retained and cannot be re-obtained byte-identically (ncbi_gene_history/SOURCE_RETENTION.md).")
GH_APPROVAL = ("approved under D6-F for GPL570 only; its use for Illumina platforms is not approved "
               "and is provisional here")


def pct(n, d):
    return f"{100 * n / d:.2f}%" if d else "n/a"


def sha(p: Path) -> str:
    return file_hashes(p)["sha256"]


def _read_tsv(p: Path) -> list[dict]:
    with open(p, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ------------------------------------------------------------------ input verification (recorded checks)
def verify() -> tuple[dict, list, dict]:
    checks = []
    v3m = json.loads((V3 / "comparison_manifest.json").read_text())
    for k, h in v3m["determinism"]["output_sha256"].items():
        checks.append((f"input: v3 {k} SHA-256 equals the v3 manifest", sha(V3 / k) == h))
    checks.append(("input: v3 validation status is OK", v3m["validation"]["status"] == "OK"))
    ref = {e["file"]: e for e in json.loads((REF / "download_manifest.json").read_text())["files"]}
    for tar, rec in {**v3m["sources"]["tarballs"], ORG_TAR: v3m["sources"]["org_hs_eg_db"]}.items():
        h = sha(REF / tar)
        checks.append((f"input: {tar} SHA-256 equals the v3 manifest and reference/download_manifest.json",
                       h == rec["sha256"] == ref[tar]["sha256"]))
    iom = json.loads((IOA / "counts_manifest_PROVISIONAL.json").read_text())
    for k, h in iom["determinism"]["output_sha256"].items():
        checks.append((f"input: Option A {k} SHA-256 equals its manifest and the v3 record",
                       sha(IOA / k) == h == v3m["sources"]["option_a_outputs"][k]["sha256"]))
    ghm = json.loads((GH / "reconciliation_manifest.json").read_text())
    checks.append(("input: gene-history v1 manifest SHA-256 equals the one recorded by Option A v1",
                   sha(GH / "reconciliation_manifest.json") == iom["sources"]["v1_manifest_sha256"]))
    checks.append(("input: gene-history v1 table SHA-256 equals its manifest",
                   sha(GH / "gene_history_reconciliation.tsv") == ghm["determinism"]["output_sha256"]["gene_history_reconciliation.tsv"]))
    checks.append(("input: gene-history View A cutoff is 20260318", ghm["parameters"]["view_a_cutoff_inclusive"] == "20260318"))
    review = (DM / "REVIEW_v1.md").read_text(encoding="utf-8")
    checks.append(("preserved: REVIEW_v1.md SHA-256 equals the value at review completion (a130d99f…)",
                   sha(DM / "REVIEW_v1.md") == REVIEW_V1_SHA256))
    checks.append(("preserved: v1 decision_matrix_manifest.json SHA-256 equals the value recorded in REVIEW_v1.md",
                   sha(DM / "v1/decision_matrix_manifest.json") in review))
    v1m = json.loads((DM / "v1/decision_matrix_manifest.json").read_text())
    for k, h in v1m["determinism"]["output_sha256"].items():
        checks.append((f"preserved: v1 {k} SHA-256 equals the v1 manifest", sha(DM / "v1" / k) == h))
    files = sorted([*V3.iterdir(), *IOA.iterdir(), GH / "reconciliation_manifest.json", GH / "gene_history_reconciliation.tsv",
                    REF / "download_manifest.json", *[REF / t for t in (*v3m["sources"]["tarballs"], ORG_TAR)],
                    *(DM / "v1").iterdir(), DM / "REVIEW_v1.md", ROOT / "reports/annotation_audit/ncbi_gene_history/SOURCE_RETENTION.md"])
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in files if p.is_file()}
    return v3m, checks, inputs


# ------------------------------------------------------------------ provenance read from retained tarballs
def package_provenance() -> dict:
    """Metadata tables (raw values kept) and DESCRIPTION 'Packaged' build dates; lumi HT-12 v4 table facts."""
    out = {}
    for label, tar, member, *_ in [*rc.PLATFORMS, ("org", ORG_TAR, ORG_MEMBER)]:
        with tarfile.open(REF / tar, "r:gz") as tf:
            desc = next(n for n in tf.getnames() if n.count("/") == 1 and n.endswith("/DESCRIPTION"))
            text = tf.extractfile(desc).read().decode("utf-8")
        fields = dict(re.findall(r"^(Version|Packaged): (.*)$", text, flags=re.M))
        with tempfile.TemporaryDirectory(prefix="bio_mb_001_dm2_") as tmp:
            con = sqlite3.connect(f"file:{_sqlite_from_tar(REF / tar, member, Path(tmp))}?mode=ro", uri=True)
            md = {str(k): str(v) for k, v in con.execute("SELECT name, value FROM metadata")}
            extra = {}
            if label.startswith("lumi"):
                tabs = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'HumanHT12_V4%' ORDER BY name")]
                extra["ht12_v4_tables"] = {t: {
                    "rows": con.execute(f"SELECT count(*) FROM {t}").fetchone()[0],
                    "distinct_probe_ids": con.execute(f"SELECT count(DISTINCT Probe_Id) FROM {t}").fetchone()[0],
                    "probe_ids_also_in_R2_B": con.execute(f"SELECT count(DISTINCT Probe_Id) FROM {t} WHERE Probe_Id IN (SELECT Probe_Id FROM {LUMI_TABLE})").fetchone()[0],
                    "shared_probe_ids_with_same_nuID": con.execute(f"SELECT count(*) FROM {t} a JOIN {LUMI_TABLE} b ON a.Probe_Id = b.Probe_Id AND a.nuID = b.nuID").fetchone()[0]}
                    for t in tabs}
                extra["representation"] = {
                    "R2_B_rows": con.execute(f"SELECT count(*) FROM {LUMI_TABLE}").fetchone()[0],
                    "R2_B_distinct_probe_ids": con.execute(f"SELECT count(DISTINCT Probe_Id) FROM {LUMI_TABLE}").fetchone()[0],
                    "R2_B_nuIDs_missing_from_mapping": con.execute(f"SELECT count(*) FROM {LUMI_TABLE} t LEFT JOIN nuID_MappingInfo m ON m.nuID = t.nuID WHERE m.nuID IS NULL").fetchone()[0],
                    "mapping_rows": con.execute("SELECT count(*) FROM nuID_MappingInfo").fetchone()[0],
                    "mapping_distinct_nuIDs": con.execute("SELECT count(DISTINCT nuID) FROM nuID_MappingInfo").fetchone()[0],
                    "EntrezID_values_with_non_digit_characters": con.execute("SELECT count(*) FROM nuID_MappingInfo WHERE trim(EntrezID) GLOB '*[^0-9]*'").fetchone()[0],
                    "Accession_values_with_separators": con.execute("SELECT count(*) FROM nuID_MappingInfo WHERE Accession GLOB '*[,; |/]*'").fetchone()[0]}
            con.close()
        out[tar] = {"metadata_raw": {k: md[k] for k in ("EGSOURCEDATE", "EGSOURCENAME", "CHIPNAME", "REFSEQ VERSION") if k in md},
                    "description_version": fields.get("Version", ""), "description_packaged": fields.get("Packaged", ""), **extra}
    return out


def shown(v: str) -> str:
    return v if v.strip() else f"blank (raw value {v!r})"


def built(prov: dict, tar: str) -> str:
    return prov[tar]["description_packaged"].split(";")[0].strip()


# ------------------------------------------------------------------ recomputation from retained sources
def independent_org_map() -> tuple[dict, set]:
    """Accession -> current Entrez IDs, built independently of the v3 code (version suffixes stripped)."""
    m = defaultdict(set)
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_dm2_") as tmp:
        con = sqlite3.connect(f"file:{_sqlite_from_tar(REF / ORG_TAR, ORG_MEMBER, Path(tmp))}?mode=ro", uri=True)
        for table in ("accessions", "refseq"):
            for a, g in con.execute(f"SELECT t.accession, g.gene_id FROM {table} t JOIN genes g USING (_id)"):
                m[re.sub(r"\.\d+$", "", str(a).strip())].add(str(g))
        genes = {str(g) for (g,) in con.execute("SELECT gene_id FROM genes")}
        con.close()
    return {k: frozenset(v) for k, v in m.items()}, genes


def assign(acc: dict, orgmap: dict, ids: list) -> dict:
    out = {}
    for p in ids:
        if not acc.get(p):
            out[p] = ("no_accession", frozenset())
            continue
        gs = frozenset().union(*(orgmap.get(a, frozenset()) for a in acc[p]))
        out[p] = ("accession_unmatched" if not gs else "unique" if len(gs) == 1 else "ambiguous", gs)
    return out


def recompute(v3m: dict) -> tuple[dict, list]:
    org_ind, org_genes = independent_org_map()
    org_v3 = rc.load_org_map()
    gh_rows = _read_tsv(GH / "gene_history_reconciliation.tsv")
    rec_rows = _read_tsv(V3 / "metric_reconciliation_probes.tsv")
    data, checks = {}, []
    for (label, tar, member, acc_query, opt_tsv, cohort), m3 in zip(rc.PLATFORMS, v3m["metrics"]):
        assert m3["platform"] == label
        rows = _read_tsv(IOA / opt_tsv)
        by = {r["probe_id"]: r for r in rows}
        ids = [r["probe_id"] for r in rows]
        n = len(rows)
        with tempfile.TemporaryDirectory(prefix="bio_mb_001_dm2_") as tmp:
            con = sqlite3.connect(f"file:{_sqlite_from_tar(REF / tar, member, Path(tmp))}?mode=ro", uri=True)
            gene_rows = con.execute(SRC_GENES[label]).fetchall()
            acc_rows = con.execute(acc_query).fetchall()
            con.close()
        pkg, acc = defaultdict(set), defaultdict(set)
        for p, g in gene_rows:
            pkg[str(p)]
            if g is not None and str(g).strip():
                pkg[str(p)].add(str(g).strip())
        acc_values = version_suffixed = 0
        for p, a in acc_rows:
            if a is not None and str(a).strip():
                acc_values += 1
                version_suffixed += bool(re.search(r"\.\d+$", str(a).strip()))
                acc[str(p)].add(str(a).strip())
        acc_unv = {p: {re.sub(r"\.\d+$", "", a) for a in s} for p, s in acc.items()}

        # --- Option A reconstruction: raw part (package table, org.Hs.eg.db) + retained gene-history v1 records
        pkg_ok = set(pkg) == set(ids) and all(
            by[p]["n_package_genes"] == str(len(pkg[p])) and by[p]["package_gene_id"] == ";".join(sorted(pkg[p], key=int)) for p in ids)
        absent = {r["entrez_id"]: r for r in gh_rows if r["package"] == label and r["baseline_status"] == "absent_from_baseline"}
        pkg_ids = {g for s in pkg.values() for g in s}
        recon_cls = {}
        for p in ids:
            g = pkg[p]
            if not g:
                recon_cls[p] = ("no_assignment_in_package", "")
            elif len(g) > 1:
                recon_cls[p] = ("multiple_mappings_excluded", "")
            else:
                gid = next(iter(g))
                if gid in org_genes:
                    recon_cls[p] = ("eligible_direct", gid)
                elif gid in absent and absent[gid]["viewA_class"] == "replaced_successor_in_baseline":
                    recon_cls[p] = ("eligible_via_history_replacement", absent[gid]["viewA_final_successor"])
                elif gid in absent:
                    recon_cls[p] = (absent[gid]["viewA_class"], "")
                else:
                    recon_cls[p] = ("UNRECONSTRUCTABLE", "")
        cls = Counter(r["option_a_class"] for r in rows)
        oa = {r["probe_id"]: r["option_a_gene_id"] for r in rows if r["option_a_class"] in ELIGIBLE}
        oa_gene_n = Counter(oa.values())
        rep = [r for r in rows if r["option_a_class"] == "eligible_via_history_replacement"]
        direct_genes = {r["option_a_gene_id"] for r in rows if r["option_a_class"] == "eligible_direct"}
        col = [r for r in rep if r["option_a_gene_id"] in direct_genes]
        oa_m = {"eligible": len(oa), "eligible_direct": cls["eligible_direct"], "eligible_via_replacement": len(rep),
                "no_replacement": cls["discontinued_no_replacement"] + cls["chain_ends_no_replacement"],
                "unexplained": cls["unexplained_absent_no_history"], "distinct_genes": len(oa_gene_n),
                "genes_with_more_than_one_probe": sum(v > 1 for v in oa_gene_n.values()), "collision_probes": len(col),
                "collision_successor_genes": len({r["option_a_gene_id"] for r in col}),
                "collision_source_genes": len({r["package_gene_id"] for r in col})}

        # --- accession route: independent map, and the v3 map, per probe
        a_ind, a_v3 = assign(acc_unv, org_ind, ids), assign(acc, org_v3, ids)
        acls = Counter(c for c, _ in a_ind.values())
        ac = {p: next(iter(gs)) for p, (c, gs) in a_ind.items() if c == "unique"}
        ac_gene_n = Counter(ac.values())
        ac_gene_n_v3 = Counter(next(iter(gs)) for c, gs in a_v3.values() if c == "unique")

        # --- comparison on the same probes (M1), M2 and probe-level transitions
        both = set(oa) & set(ac)
        conc = {p for p in both if oa[p] == ac[p]}
        disc = both - conc
        m2 = {p for p in ac if len(pkg[p]) == 1}
        trans, trans_rec, not_m1 = Counter(), set(), []
        for p in sorted(m2):
            a = "same" if next(iter(pkg[p])) == ac[p] else "different"
            b = ("concordant" if p in conc else "discordant") if p in both else NOT_IN_M1
            trans[f"{a} -> {b} [{by[p]['option_a_class']}]"] += 1
            if not (a == "same" and b == "concordant"):
                trans_rec.add((p, a, b, by[p]["option_a_class"]))
            if b == NOT_IN_M1:
                not_m1.append((p, by[p]["option_a_class"]))
        tsv_rec = {(r["probe_id"], r["M2_result"], r["M1_result"], r["option_a_class"]) for r in rec_rows if r["platform"] == label}
        amb_oa = [p for p in oa if a_ind[p][0] == "ambiguous"]
        amb = {"both": sum(len(pkg[p]) > 1 and a_ind[p][0] == "ambiguous" for p in ids),
               "package_only": sum(len(pkg[p]) > 1 and a_ind[p][0] != "ambiguous" for p in ids),
               "package_only_accession_unique": sum(len(pkg[p]) > 1 and a_ind[p][0] == "unique" for p in ids),
               "accession_only": sum(len(pkg[p]) <= 1 and a_ind[p][0] == "ambiguous" for p in ids),
               "accession_only_single_package_gene": sum(len(pkg[p]) == 1 and a_ind[p][0] == "ambiguous" for p in ids)}
        cmp_ = {"both": len(both), "concordant": len(conc), "discordant": len(disc),
                "discordant_by_class": dict(sorted(Counter(by[p]["option_a_class"] for p in disc).items())),
                "oa_only_unresolved": sum(1 for p in oa if p not in ac and a_ind[p][0] != "ambiguous"),
                "oa_only_ambiguous": len(amb_oa), "acc_only": len(set(ac) - set(oa)),
                "genes_both": len(set(oa_gene_n) & set(ac_gene_n)), "genes_oa_only": len(set(oa_gene_n) - set(ac_gene_n)),
                "genes_acc_only": len(set(ac_gene_n) - set(oa_gene_n)),
                "M2_total": len(m2), "M2_same": sum(next(iter(pkg[p])) == ac[p] for p in m2),
                "transitions": dict(sorted(trans.items())), "not_in_M1": not_m1}
        cmp_["M2_different"] = cmp_["M2_total"] - cmp_["M2_same"]
        rcm, rr = m3["route_comparison"], m3["route_comparison"]["reconciliation_M1_vs_M2"]
        d = {"cohort": m3["cohort"], "n": n, "multi_gene_probes": sum(len(pkg[p]) > 1 for p in ids),
             "no_gene_in_package": sum(not pkg[p] for p in ids), "oa": oa_m, "oa_classes": dict(cls),
             "acc_classes": dict(sorted(acls.items())), "acc_unique": len(ac), "acc_genes": len(ac_gene_n),
             "acc_multi_probe_genes": sum(v > 1 for v in ac_gene_n.values()), "acc_values": acc_values,
             "acc_version_suffixed": version_suffixed, "probes_gt1_accession": sum(len(s) > 1 for s in acc.values()),
             "ambiguity": amb, "cmp": cmp_}
        data[label] = d

        def ck(name, ok):
            checks.append((f"{label}: {name}", bool(ok)))
        ck("[raw] package probe table reproduces the Option A v1 probe set, gene counts and package gene IDs", pkg_ok)
        ck("[raw] package Entrez IDs absent from org.Hs.eg.db 3.23.1 genes = gene-history v1 'absent_from_baseline' IDs for this package",
           {g for g in pkg_ids if g not in org_genes} == set(absent))
        ck("[raw + retained gene-history records] per-probe Option A class and gene reconstructed = Option A v1 table",
           all(recon_cls[p] == (by[p]["option_a_class"], by[p]["option_a_gene_id"]) for p in ids))
        ck("[raw] eligible_direct probes = single package gene present in org.Hs.eg.db 3.23.1",
           {p for p in ids if recon_cls[p][0] == "eligible_direct"} == {p for p in ids if by[p]["option_a_class"] == "eligible_direct"})
        ck("Option A metrics (eligible, direct, via replacement, no replacement, unexplained, genes, multi-probe genes, collisions) recomputed from the Option A v1 table = v3 manifest",
           all(oa_m[k] == m3["option_a"][k] for k in oa_m))
        ck("[raw] multi-gene and no-gene probe counts = v3 manifest",
           (d["multi_gene_probes"], d["no_gene_in_package"]) == (m3["multi_gene_probes"], m3["no_gene_in_package"]))
        ck("[raw] accession classes from the independent org.Hs.eg.db map = classes from the v3 map, probe by probe",
           all(a_ind[p] == a_v3[p] for p in ids))
        ck("[raw] accession classes, unique probes and distinct genes = v3 manifest",
           (d["acc_classes"], len(ac), len(ac_gene_n)) == (m3["accession_route_assignments"]["classes"],
                                                          m3["accession_route_assignments"]["assigned_unique"],
                                                          m3["accession_route_assignments"]["distinct_genes"]))
        ck("[raw] C03 accession-route multi-probe genes: independent map = v3 map; probe sum = unique probes; gene count = distinct genes",
           d["acc_multi_probe_genes"] == sum(v > 1 for v in ac_gene_n_v3.values())
           and sum(ac_gene_n.values()) == len(ac) and len(ac_gene_n) == m3["accession_route_assignments"]["distinct_genes"])
        ck("[raw] accession inputs (values, version-suffixed values, probes with >1 accession) = v3 manifest",
           (acc_values, version_suffixed, d["probes_gt1_accession"]) == (
               m3["accession_route_inputs"]["accession_values"], m3["accession_route_inputs"]["accessions_with_version_suffix"],
               m3["accession_route_inputs"]["probes_with_more_than_one_accession"]))
        ck("M1 both / concordant / discordant = v3 manifest",
           (len(both), len(conc), len(disc)) == (rcm["both_assign_one_gene"], rcm["concordant"], rcm["discordant"]))
        ck("single-route and ambiguous-under-accession Option A probes = v3 manifest",
           (cmp_["oa_only_unresolved"], cmp_["oa_only_ambiguous"], cmp_["acc_only"]) == (
               rcm["optionA_eligible_accession_unresolved"],
               rcm["optionA_eligible_accession_ambiguous_including_optionA_gene"] + rcm["optionA_eligible_accession_ambiguous_excluding_optionA_gene"],
               rcm["accession_unique_optionA_not_eligible"]))
        ck("gene overlap = v3 manifest", (cmp_["genes_both"], cmp_["genes_oa_only"], cmp_["genes_acc_only"]) == (
            rcm["genes_both_routes"], rcm["genes_optionA_only"], rcm["genes_accession_only"]))
        ck("M2 total / same / different and M1 subset of M2 = v3 manifest",
           (cmp_["M2_total"], cmp_["M2_same"], cmp_["M2_different"], both <= m2, len(both)) == (
               rr["M2_total_package_gene_and_accession_unique"], m3["prior_session_replication"]["same_gene"],
               m3["prior_session_replication"]["different_gene"], True, rr["M1_total_both_assign"]))
        ck("M2 -> M1 transition counts = v3 manifest", cmp_["transitions"] == rr["transitions_M2_to_M1_by_option_a_class"])
        ck("probes outside M1 = v3 manifest list", [p for p, _ in not_m1] == sorted(rr["in_M2_not_M1"]))
        ck("every non-(same -> concordant) transition matches v3/metric_reconciliation_probes.tsv probe by probe", trans_rec == tsv_rec)
        ck("C09 unresolved = all probes - C01 assigned (both routes)",
           (n - len(oa), n - len(ac)) == (n - m3["option_a"]["eligible"], n - m3["accession_route_assignments"]["assigned_unique"]))
        ck("C10 single-route difference = C01 coverage difference",
           (cmp_["oa_only_unresolved"] + cmp_["oa_only_ambiguous"]) - cmp_["acc_only"] == len(oa) - len(ac))
        ck("ambiguity cross-tabulation partitions the package-multi-gene and accession-ambiguous probes",
           amb["both"] + amb["package_only"] == d["multi_gene_probes"] and amb["both"] + amb["accession_only"] == acls["ambiguous"])
    return data, checks


# ------------------------------------------------------------------ matrix (pure)
def build_matrix(data: dict, prov: dict) -> list[dict]:
    rows = []
    org_date = prov[ORG_TAR]["metadata_raw"].get("EGSOURCEDATE", "")
    org_built = built(prov, ORG_TAR)
    tar_of = {label: tar for label, tar, *_ in rc.PLATFORMS}
    for label, d in data.items():
        n, a, c, amb = d["n"], d["oa"], d["cmp"], d["ambiguity"]
        is_lumi = label.startswith("lumi")
        pv = prov[tar_of[label]]
        trans = c["transitions"]
        repl_conc = sum(v for k, v in trans.items() if k.startswith("different -> concordant"))
        repl_disc = trans.get("different -> discordant [eligible_via_history_replacement]", 0)
        direct_disc = trans.get("different -> discordant [eligible_direct]", 0)
        out_m1 = c["not_in_M1"]
        gap = a["eligible"] - d["acc_unique"]
        ggap = a["distinct_genes"] - d["acc_genes"]
        oa_un, ac_un = n - a["eligible"], n - d["acc_unique"]
        ac_nomatch = d["acc_classes"].get("no_accession", 0) + d["acc_classes"].get("accession_unmatched", 0)
        oa_single = c["oa_only_unresolved"] + c["oa_only_ambiguous"]
        src = "recomputed from reference/bioconductor_3.23 and the Option A v1 / gene-history v1 tables; checked against v3/comparison_manifest.json"

        def add(cid, crit, oa, ac, joint, adv, lim, status, recon, sources=src, derived="—"):
            assert adv in ADVANTAGES and status in STATUSES
            assert not (adv == "not determinable" and status != "unresolved")
            rows.append({"platform": label, "cohort_context": d["cohort"], "criterion_id": cid, "criterion": crit,
                         "option_a_evidence": oa, "accession_route_evidence": ac, "joint_evidence": joint, "advantage": adv,
                         "derived_from": derived, "limitation": lim, "status": status, "reconstruction": recon, "sources": sources})

        def better(x, y):
            return "Option A" if x > y else "accession route" if x < y else "neither"

        add("C01", "Probes assigned exactly one eligible gene (denominator: all platform probes)",
            f"{a['eligible']:,} / {n:,} ({pct(a['eligible'], n)})", f"{d['acc_unique']:,} / {n:,} ({pct(d['acc_unique'], n)})",
            f"difference {gap:+,} probes (Option A − accession route)", better(a["eligible"], d["acc_unique"]),
            "This is the single platform-wide coverage difference; C09 and C10 restate it and are not separate advantages. "
            "Coverage is not cohort-specific, and higher coverage is not evidence of biological validity.",
            "supportive", PARTIAL)
        add("C02", "Distinct current Entrez genes represented (gene level)",
            f"{a['distinct_genes']:,}", f"{d['acc_genes']:,}",
            f"both routes {c['genes_both']:,}; Option A only {c['genes_oa_only']:,}; accession only {c['genes_acc_only']:,}; difference {ggap:+,} genes",
            better(a["distinct_genes"], d["acc_genes"]),
            "Gene-level counterpart of C01: related to probe coverage but not an arithmetic restatement of it. Includes genes whose "
            "only probes are replacement-derived (Option A) or matched by unversioned accession (accession route); measurability "
            "in a cohort is not assessed.", "supportive", PARTIAL)
        add("C03", "Genes represented by more than one eligible probe (gene level; G3 averages them)",
            f"{a['genes_with_more_than_one_probe']:,} of {a['distinct_genes']:,} genes",
            f"{d['acc_multi_probe_genes']:,} of {d['acc_genes']:,} genes (new in the decision matrix; verified by two independently built accession maps and by probe/gene totals)",
            "—", "neither",
            "Multiple probes per gene are expected under G3 and are neither good nor bad in themselves; their effect depends on "
            "probe concordance in the cohort.", "unresolved", PARTIAL)
        add("C04", "M1 — same-probe agreement (probes both routes assign; judged against the post-gene-history Option A gene)",
            "— (joint metric)", "— (joint metric)",
            f"both assign {c['both']:,}; concordant {c['concordant']:,} ({pct(c['concordant'], c['both'])} of {c['both']:,}); discordant {c['discordant']:,}",
            "neither", "Agreement between two annotation routes is not biological confirmation; both may share upstream sources.",
            "supportive", PARTIAL)
        add("C05", "ID-replacement effects (M2 → M1 transitions; M2 = agreement with the package's original Entrez ID)",
            f"{a['eligible_via_replacement']:,} probes assigned via a gene-history successor (all probes, not only M1)",
            "— (no history step)",
            f"M2 total {c['M2_total']:,}; M1 total {c['both']:,} (different metrics). Of {c['M2_different']:,} M2 'different' probes: "
            f"{repl_conc:,} concordant under M1 after replacement; {repl_disc:,} replacement-derived and still discordant; "
            f"{direct_disc:,} discordant with a direct assignment; {len(out_m1):,} outside M1 (Option A not eligible"
            + (": " + ", ".join(f"{p} [{k}]" for p, k in out_m1) if out_m1 else "") + ")",
            "neither",
            "M1 and M2 are different metrics; their totals are not compared. Labels follow v3/metric_reconciliation_probes.tsv "
            "(M2_result different; M1_result concordant / discordant / not_in_M1). Replacement agreement shows the two routes "
            "converge on the same current ID, not that the probe measures it.", "supportive", PARTIAL_OA)
        add("C06", "Genuine disagreements (M1 discordant probes)", "— (joint metric)", "— (joint metric)",
            f"{c['discordant']:,} probes: " + "; ".join(f"{v:,} {k}" for k, v in c["discordant_by_class"].items()) + " (Option A class); listed in v3/metric_reconciliation_probes.tsv"
            if c["discordant"] else "0 probes",
            "not determinable",
            "Which route is correct for a discordant probe cannot be decided from annotation tables; sequence-level evidence would be required.",
            "unresolved", PARTIAL, "v3/metric_reconciliation_probes.tsv; recomputed")
        oc = d["oa_classes"]
        add("C07", "Option A: package IDs with no current gene (no replacement / unexplained); accession route: no accession or unmatched accessions",
            f"no replacement {a['no_replacement']:,} (discontinued_no_replacement {oc.get('discontinued_no_replacement', 0):,}; "
            f"chain_ends_no_replacement {oc.get('chain_ends_no_replacement', 0):,}); unexplained {a['unexplained']:,}",
            f"accession unmatched {d['acc_classes'].get('accession_unmatched', 0):,}; no accession {d['acc_classes'].get('no_accession', 0):,}",
            "—", "not determinable",
            "Absence of a current mapping does not establish that a probe is non-functional; an accession absent from org.Hs.eg.db is not proof of retirement.",
            "unresolved", PARTIAL)
        lumi_amb = (" For this table both counts are zero by construction: lumiHumanIDMapping stores one EntrezID and one Accession "
                    "field per nuID (one row per nuID; no multi-value separators), so ambiguity cannot be represented. The zero is a "
                    "property of the source representation, not evidence that ambiguity is absent biologically.") if is_lumi else ""
        add("C08", "Ambiguous probes (>1 candidate gene under the route's own mapping; each route excludes the probes it finds ambiguous)",
            f"package lists >1 Entrez ID: {d['multi_gene_probes']:,} (excluded before gene-history reconciliation)",
            f"accession matches >1 current gene: {d['acc_classes'].get('ambiguous', 0):,}",
            f"same probes: ambiguous under both {amb['both']:,}; package only {amb['package_only']:,} (accession route assigns "
            f"{amb['package_only_accession_unique']:,} of them uniquely); accession only {amb['accession_only']:,} (package lists "
            f"exactly one Entrez ID for {amb['accession_only_single_package_gene']:,} of them)",
            "not determinable",
            "The two definitions differ (package multi-mapping of 2015-era IDs vs union of current genes over a probe's accessions), "
            "so their totals are not a like-for-like quality measure." + lumi_amb, "unresolved", FULL)
        add("C09", "Unresolved probes (no eligible assignment; denominator: all platform probes)",
            f"{oa_un:,} / {n:,} ({pct(oa_un, n)}), incl. {d['no_gene_in_package']:,} with no package gene",
            f"{ac_un:,} / {n:,} ({pct(ac_un, n)}), incl. {ac_nomatch:,} with no matched accession",
            f"= all probes − C01 assigned; difference {ac_un - oa_un:+,} (accession route − Option A) equals the C01 difference",
            RESTATES,
            "Arithmetic complement of C01, not an independent advantage. Includes control/non-gene probes; the share relevant to a "
            "cohort depends on Series Matrix content (not assessed).", "supportive", PARTIAL, derived="C01")
        add("C10", "Probes assigned by only one route (no cross-check)",
            f"Option A only: {oa_single:,} (accession unresolved {c['oa_only_unresolved']:,}; accession ambiguous {c['oa_only_ambiguous']:,})",
            f"accession only: {c['acc_only']:,}",
            f"difference {oa_single - c['acc_only']:+,} equals the C01 difference",
            RESTATES,
            "The difference restates C01. Single-route probes have no cross-check; their validity is the least supported.",
            "supportive", PARTIAL, derived="C01")
        md = pv["metadata_raw"]
        if is_lumi:
            oa_src = (f"Entrez/accession content date not recorded (metadata REFSEQ VERSION: {shown(md.get('REFSEQ VERSION', ''))}); "
                      f"lumiHumanIDMapping {pv['description_version']} package built {built(prov, tar_of[label])} (DESCRIPTION 'Packaged'; "
                      "a build date, not a mapping-content date)")
        else:
            oa_src = (f"package Entrez source date {md.get('EGSOURCEDATE', '')} (metadata EGSOURCEDATE); package built "
                      f"{built(prov, tar_of[label])} (DESCRIPTION 'Packaged')")
        add("C11", "Probe-to-gene source, version, provenance and age (provenance context)",
            f"{oa_src}; IDs reconciled to org.Hs.eg.db 3.23.1 (Entrez Gene {org_date}) with the gene-history procedure "
            f"({GH_APPROVAL})",
            f"probe accessions from the same package build matched to org.Hs.eg.db 3.23.1 (Entrez Gene {org_date}; built {org_built})",
            "—", "not determinable",
            "Annotation age is provenance context, not evidence of biological accuracy: a newer gene-ID snapshot does not show "
            "that a probe measures the current transcript, and the accession route's probe accessions are as old as the package "
            "build. " + GH_NOTE, "unresolved", FULL + " (dates); Option A history step: " + PARTIAL_OA.split(": ", 1)[1],
            "reference/bioconductor_3.23 metadata tables and DESCRIPTION files; ncbi_gene_history/SOURCE_RETENTION.md")
        add("C12", "Accession-matching limitations", "not applicable (Option A uses package gene assignments)",
            f"{d['acc_version_suffixed']:,} of {d['acc_values']:,} accession values carry a version suffix; matching is on "
            f"unversioned roots; {d['probes_gt1_accession']:,} probes carry >1 accession", "—", "not determinable",
            "An accession match shows the identifiers are linked in NCBI records, not that the probe sequence hybridizes to the "
            "current transcript." + (" One accession per nuID by construction (see C08)." if is_lumi else ""),
            "unresolved", FULL)
        add("C13", "Successor collisions (Option A; a replacement-derived probe joins a gene that already has directly mapped probes)",
            f"probes {a['collision_probes']:,}; distinct successor genes {a['collision_successor_genes']:,}; distinct historical "
            f"source genes {a['collision_source_genes']:,}", "not applicable (no history step)", "—", "not determinable",
            "Successor genes and historical source genes are different counts. Collisions are flagged, never merged; under G3 the "
            "replaced probes would join the successor gene's average.", "unresolved", PARTIAL_OA)
        add("C14", "Downstream consequences for gene-level (G3) aggregation",
            "probes per gene and collisions determine each gene's average; replacement-derived probes enter successor genes",
            "ambiguous probes are lost; single-gene accession probes define the gene averages", "—", "not determinable",
            "Effects on expression estimates require cohort data (probe presence, D17 (expression/feature filter), probe "
            "concordance) and are not assessed here.", "unresolved", "not applicable (qualitative)", "v5 §7.2–7.3 (rules); this matrix")
        lumi_tabs = ""
        if is_lumi:
            t = pv["ht12_v4_tables"]
            lumi_tabs = (" lumiHumanIDMapping holds three HT-12 v4 tables: " + "; ".join(
                f"{k} ({v['distinct_probe_ids']:,} probe IDs; {v['probe_ids_also_in_R2_B']:,} also in {LUMI_TABLE}, "
                f"{v['shared_probe_ids_with_same_nuID']:,} with the same nuID)" for k, v in t.items())
                + f". This matrix uses {LUMI_TABLE}. These counts describe the package only; which table (if any) "
                "corresponds to GSE140829 is part of D19 and is not established here.")
        add("C15", "Presence of probes in the cohort's Series Matrix", "NOT ASSESSED", "NOT ASSESSED", "NOT ASSESSED", "not determinable",
            "Requires the cohort's authorized Series Matrix probe list; no GEO data used. Platform-wide counts are not cohort coverage."
            + lumi_tabs, "unresolved", "not assessed", "not assessed")
    return rows


CHANGES = [
    ("R1", "C09 and C10 advantage set to 'restates C01 (not counted)' with derived_from = C01; C01/C09/C10 limitations and Definitions state they are one coverage fact; C02 noted as related but not a restatement"),
    ("R2", "C08 reworded (each route excludes its own ambiguous probes); same-probe cross-tabulation added; advantage 'not determinable', status 'unresolved'; lumi zero explained as a source-representation property"),
    ("R3", "C11 is provenance context: advantage 'not determinable', status 'unresolved' on every platform; rule enforced: 'not determinable' ⇒ 'unresolved'"),
    ("R4", "Conclusion decomposes every platform's M2 'different' probes (replacement-concordant / discordant by class / outside M1, with probe IDs)"),
    ("R5", "C05 and C06 report replacement-derived discordant probes using the labels of v3/metric_reconciliation_probes.tsv"),
    ("R6", "C11 reports raw REFSEQ VERSION and DESCRIPTION build dates (lumi 2016-04-21); C15 lists the HT-12 v4 tables without claiming GSE140829 applicability"),
    ("R7", "C11 limitation, 'reconstruction' column and Provenance section disclose the unretained gene_history.gz and what remains reconstructable"),
    ("R8", "C11 and Definitions state the gene-history procedure is approved for GPL570 only (D6-F), provisional for Illumina"),
    ("R9", "Checks renamed to what they test; Option A and C03 figures recomputed and checked; input verification recorded; manifest records generator/dependency hashes, interpreter, full command and an independent-process run"),
    ("R10", "Heading without nested parentheses; joint metrics in a 'joint' column; 'M2 total; M1 total (different metrics)'; C07 composition shown; 'D17 (expression/feature filter)'; ties → 'neither'"),
]


def render(rows: list[dict], data: dict, checks: list, prov: dict, version: str) -> str:
    L = [f"# Illumina annotation-route decision matrix — {version}", "",
         "**Assessment only. No Illumina mapping policy is selected, recommended or approved.** No weighting or ranking is "
         "applied. GSE140829 remains governed by D19; D17 (expression/feature filter) is unresolved. Supersedes the presentation "
         "of v1 (retained unchanged) following REVIEW_v1.md; no v1 figure changed.", "",
         "## Definitions", "",
         "- **Option A:** package Entrez IDs reconciled to org.Hs.eg.db 3.23.1 by the NCBI gene-history procedure (View A, "
         "cutoff 20260318). The procedure is approved for GPL570 only (D6-F); approval for GPL570 does not approve it for any "
         "Illumina platform, where Option A is provisional.",
         "- **Accession route:** probe accessions matched (unversioned) to org.Hs.eg.db 3.23.1 GenBank accessions ∪ RefSeq; "
         "only a unique match is an assignment.",
         "- **M1:** probes both routes assign; agreement judged against the post-gene-history Option A gene. **M2:** probes with "
         "one package Entrez ID and a unique accession-route gene; agreement judged against the package's original ID. "
         "M1 ⊆ M2; the two totals are different metrics and are not compared. Probe-level labels follow "
         "v3/metric_reconciliation_probes.tsv.",
         "- **Denominators:** probe-level percentages use all probes of the platform table (lumi: rows of "
         f"{LUMI_TABLE}); M1 agreement uses the M1 total; gene-level counts are distinct current Entrez IDs. Historical "
         "source genes and successor genes are counted separately.",
         "- **Advantage:** which route, if either, is better on that criterion alone. Advantage entries are not independent "
         "and must not be counted or summed; C09 and C10 restate C01 and are marked 'restates C01 (not counted)'.",
         "- **Status:** *decisive* = settles the choice on its own (none qualify); *supportive* = informative evidence that does "
         "not settle the choice; *unresolved* = the comparative merit cannot be judged from retained evidence. Every criterion "
         "whose advantage is 'not determinable' is *unresolved*.",
         "- **Reconstruction:** *full* = recomputed here from retained raw sources; *partial* = the Option A side depends on the "
         "retained gene-history v1 records, whose raw NCBI source is not retained.", ""]
    for label, d in data.items():
        sub = [r for r in rows if r["platform"] == label]
        L += [f"## {label} — {d['cohort']}", "",
              "| ID | Criterion | Option A | Accession route | Joint (same probes) | Advantage (this criterion only) | Status |",
              "|---|---|---|---|---|---|---|"]
        L += [f"| {r['criterion_id']} | {r['criterion']} | {r['option_a_evidence']} | {r['accession_route_evidence']} | "
              f"{r['joint_evidence']} | {r['advantage']} | {r['status']} |" for r in sub]
        L += ["", "Limitations and reconstruction:", ""] + [
            f"- {r['criterion_id']}: {r['limitation']} *Reconstruction: {r['reconstruction']}.*" for r in sub] + [""]
    m1 = "; ".join(f"{k} {d['cmp']['concordant']:,} / {d['cmp']['both']:,} ({pct(d['cmp']['concordant'], d['cmp']['both'])})" for k, d in data.items())
    cov = "; ".join(f"{k} {d['oa']['eligible'] - d['acc_unique']:+,} probes, {d['oa']['distinct_genes'] - d['acc_genes']:+,} genes" for k, d in data.items())
    dec = []
    for k, d in data.items():
        c, t = d["cmp"], d["cmp"]["transitions"]
        rcn = sum(v for x, v in t.items() if x.startswith("different -> concordant"))
        rdi = t.get("different -> discordant [eligible_via_history_replacement]", 0)
        ddi = t.get("different -> discordant [eligible_direct]", 0)
        out = c["not_in_M1"]
        dec.append(f"  - {k}: {c['M2_different']:,} = {rcn:,} concordant after replacement + {ddi + rdi:,} M1-discordant "
                   f"({ddi:,} direct, {rdi:,} replacement-derived) + {len(out):,} outside M1"
                   + (" (" + "; ".join(f"{p} [{cl}]" for p, cl in out) + ")" if out else ""))
    L += ["## Conclusions", "", "**Established by the retained evidence**", "",
          f"- M1 agreement (concordant / both assign), separately per platform: {m1}.",
          f"- Option A assigns more probes (C01) and genes (C02) than the accession route on every platform ({cov}). "
          "This is one coverage difference; C09 and C10 restate it.",
          "- Probes that differ under M2 (package ID ≠ accession-route gene) decompose as follows "
          "(all non-trivial records are in v3/metric_reconciliation_probes.tsv):", *dec, "",
          "**Suggested but not established**", "",
          "- That Option A's extra coverage reflects valid probe-to-gene relationships: it rests on package assignments "
          "dated 2015 (illuminaHumanv3/v4) or of unrecorded date in a 2016 build (lumi) and, for lumi, on many replacements "
          "and collisions.",
          "- That the accession route's newer gene-ID snapshot is more accurate biologically (unversioned accession matches "
          "do not confirm that the probe targets the current transcript).", "",
          "**Unknown**", "",
          "- Which route is correct for each discordant or single-route probe.",
          "- Cohort-specific coverage (probe presence in each Series Matrix), the D17 decision (expression/feature filter), "
          "and the effect of either route on gene-level estimates.",
          f"- Which lumiHumanIDMapping HT-12 v4 table, if any, applies to GSE140829 (D19); this matrix uses {LUMI_TABLE}.", "",
          "**Evidence required before a policy decision**", "",
          "- Probe presence in each cohort's authorized Series Matrix (GSE63060, GSE63061; GSE140829 after D19).",
          "- The D17 decision.",
          "- A decision on how discordant and single-route probes are treated, and whether sequence-level evidence (e.g. the "
          "packages' re-annotation fields) should be considered.",
          "- A decision on whether the gene-history procedure, approved under D6-F for GPL570 only, may be applied to Illumina platforms.", "",
          "## Not yet assessed / unresolved", "",
          "- Probe presence in cohort inputs (no GEO data used); D17; the Illumina mapping policy; D19 (GSE140829); any "
          "biological validation beyond annotation agreement.", "",
          "## Provenance and reconstructability", "",
          "- Fully reconstructed from retained raw sources (package and org.Hs.eg.db tarballs, hash-verified): probe sets, "
          "package gene IDs, multi-gene / no-gene probes, which package IDs are absent from org.Hs.eg.db 3.23.1, eligible_direct "
          "probes, every accession-route figure, C08, C12, and source dates.",
          "- Reconstructed only from retained derived records: the replacement / no-replacement / unexplained class of each "
          "package ID absent from org.Hs.eg.db, and therefore every Option A figure that includes replacement-derived probes "
          "(C01–C07, C09, C10, C13 Option A side). The per-probe Option A classes were re-derived from the package tables plus "
          "the retained gene-history v1 records and equal the Option A v1 table. " + GH_NOTE,
          "- The set of absent package IDs computed from the raw sources equals the set recorded in gene-history v1 for each "
          "platform, so the retained records cover every ID that needs them.", "",
          "## Changes from v1 (REVIEW_v1.md)", "", "| Finding | Change in v2 |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in CHANGES] + ["", "## Validation", ""]
    L += [f"- [{'OK' if ok else 'FAILED'}] {n}" for n, ok in checks] + [""]
    L += ["## Package provenance (read from retained tarballs)", ""]
    for tar, v in prov.items():
        L.append(f"- {tar}: DESCRIPTION Version {v['description_version']}, Packaged {v['description_packaged'].split(';')[0].strip()}; "
                 + "; ".join(f"metadata {a}={shown(b)}" for a, b in v["metadata_raw"].items()))
    return "\n".join(L) + "\n"


def matrix_checks(rows: list[dict], data: dict) -> list:
    return [
        ("matrix: every platform has exactly C01–C15",
         all(sorted(r["criterion_id"] for r in rows if r["platform"] == p) == [f"C{i:02d}" for i in range(1, 16)] for p in data)),
        ("matrix: statuses and advantages use the allowed vocabularies",
         all(r["status"] in STATUSES and r["advantage"] in ADVANTAGES for r in rows)),
        ("matrix: no criterion has status 'decisive'", not any(r["status"] == "decisive" for r in rows)),
        ("matrix: every 'not determinable' advantage has status 'unresolved'",
         all(r["status"] == "unresolved" for r in rows if r["advantage"] == "not determinable")),
        ("matrix: C09 and C10 are marked as restating C01", all(r["advantage"] == RESTATES and r["derived_from"] == "C01"
                                                               for r in rows if r["criterion_id"] in ("C09", "C10"))),
        ("matrix: no empty cell", all(str(v).strip() for r in rows for v in r.values())),
    ]


def run(v3m: dict) -> tuple[list, list, dict, dict]:
    prov = package_provenance()
    data, checks = recompute(v3m)
    rows = build_matrix(data, prov)
    r = prov["lumiHumanIDMapping_1.10.1.tar.gz"]["representation"]
    checks.append(("lumi HT-12 v4 R2: [raw] source representation is single-valued (one R2_B row per probe ID, every nuID mapped, "
                   "one mapping row per nuID, no multi-value EntrezID/Accession), so the C08/C12 zeros are structural",
                   r["R2_B_rows"] == r["R2_B_distinct_probe_ids"] == data["lumi HT-12 v4 R2"]["n"]
                   and r["R2_B_nuIDs_missing_from_mapping"] == 0 and r["mapping_rows"] == r["mapping_distinct_nuIDs"]
                   and r["EntrezID_values_with_non_digit_characters"] == 0 and r["Accession_values_with_separators"] == 0))
    checks = checks + matrix_checks(rows, data)
    return rows, checks, prov, data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="v2")
    ap.add_argument("--out-dir", type=Path, default=None, help="override output directory (reproduction checks)")
    ap.add_argument("--hashes-only", action="store_true", help="print output hashes without writing (independent-process check)")
    args = ap.parse_args()
    out = args.out_dir or DM / args.version
    if not args.hashes_only and out.exists():
        raise SystemExit(f"{out} already exists; inspect it — nothing replaced")
    v3m, in_checks, inputs = verify()
    if not all(ok for _, ok in in_checks):
        raise SystemExit("INPUT VERIFICATION FAILED:\n  " + "\n  ".join(n for n, ok in in_checks if not ok))

    def generate():
        rows, checks, prov, data = run(v3m)
        checks = in_checks + checks
        return {"DECISION_MATRIX.md": render(rows, data, checks, prov, args.version),
                "decision_matrix.tsv": tsv(rows, COLUMNS)}, checks, prov

    def hashes(files):
        return {k: hashlib.sha256(v.encode()).hexdigest() for k, v in files.items()}

    f1, c1, prov = generate()
    if args.hashes_only:
        print(json.dumps(hashes(f1), sort_keys=True))
        return 0
    f2, _, _ = generate()
    h1 = hashes(f1)
    proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--version", args.version, "--hashes-only"],
                          capture_output=True, text=True, cwd=ROOT)
    h_ind = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.returncode == 0 else {"error": proc.stderr[-2000:]}
    det = {"in_process_runs_compared": 2, "in_process_identical": h1 == hashes(f2),
           "independent_process_identical": h_ind == h1, "output_sha256": h1}
    status = "OK" if all(ok for _, ok in c1) else "FAILED"
    if status != "OK" or not det["in_process_identical"] or not det["independent_process_identical"]:
        raise SystemExit(json.dumps({"failed_checks": [n for n, ok in c1 if not ok], "determinism": det,
                                     "independent": h_ind}, indent=2) + "\nFAILED (nothing written)")
    out.mkdir(parents=True)
    for k, v in f1.items():
        (out / k).write_text(v, encoding="utf-8")
    gen = {str(p.relative_to(ROOT)): sha(p) for p in [
        Path(__file__).resolve(), ROOT / "scripts/annotation_illumina_route_comparison.py",
        ROOT / "src/biomarker_project/gene_history_reconciliation.py", ROOT / "tests/test_illumina_route_decision_matrix_v2.py"]}
    manifest = {
        "status": "Assessment only; no Illumina mapping policy selected or approved; D17 and D19 unchanged",
        "supersedes_presentation_of": "reports/annotation_audit/illumina_route_decision_matrix/v1 (unchanged)",
        "review": "reports/annotation_audit/illumina_route_decision_matrix/REVIEW_v1.md",
        "generator_sha256": gen,
        "environment": {"python": sys.version.split()[0], "implementation": _platform.python_implementation()},
        "command": " ".join([str(Path(sys.executable).relative_to(ROOT)) if Path(sys.executable).is_relative_to(ROOT) else sys.executable,
                             str(Path(__file__).resolve().relative_to(ROOT)), *sys.argv[1:]]),
        "inputs_sha256": inputs, "package_provenance": prov,
        "definitions": {"option_a": "package Entrez IDs + gene-history procedure (View A, cutoff 20260318); approved for GPL570 only (D6-F); provisional for Illumina",
                        "accession_route": "unversioned accession match to org.Hs.eg.db 3.23.1 (accessions ∪ refseq); unique match only",
                        "M1": "probes both routes assign; agreement vs post-gene-history Option A gene",
                        "M2": "probes with one package Entrez ID and a unique accession-route gene; agreement vs the package's original ID",
                        "probe_denominator": f"all probes of the platform table (lumi: {LUMI_TABLE} rows)",
                        "gene_counts": "distinct current Entrez IDs; successor and historical source genes counted separately",
                        "statuses": {"decisive": "settles the choice on its own (none qualify)",
                                     "supportive": "informative evidence that does not settle the choice",
                                     "unresolved": "comparative merit cannot be judged from retained evidence; required whenever advantage is 'not determinable'"},
                        "advantages": list(ADVANTAGES), "advantage_entries_independent": False, "weighting": "none",
                        "reconstruction": {"full": FULL, "partial": PARTIAL}},
        "reconstructability": {"raw_gene_history_retained": False,
                               "raw_gene_history_sha256_recorded": "bcb85c8fdd4791ad674e69481b794677953d0ecd9efb8547af4371845c59a602",
                               "retained_gene_history_records": "reports/annotation_audit/ncbi_gene_history/v1/gene_history_reconciliation.tsv",
                               "note": GH_NOTE},
        "validation": {"status": status, "checks": [{"check": n, "status": "OK" if ok else "FAILED"} for n, ok in c1]},
        "determinism": det}
    (out / "decision_matrix_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"written: {out}; validation {status} ({len(c1)} checks); determinism identical (in-process and independent process)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
