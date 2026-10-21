#!/usr/bin/env python3
"""Illumina mapping-route comparison (decision support only; no policy is approved).

Compares, per platform package, what the RETAINED evidence supports:
  * Option A (package Entrez IDs + approved gene-history procedure, cutoff 20260318): read from the
    verified provisional outputs in reports/annotation_audit/illumina_option_a/v1/.
  * Accession route (probe accession -> org.Hs.eg.db 3.23.1 accessions/refseq -> current Entrez ID):
    computed when org.Hs.eg.db 3.23.1 is retained in reference/bioconductor_3.23/ (v2 onwards). A probe's
    accessions are matched exactly (unversioned) to the union of org.Hs.eg.db's GenBank `accessions` and
    `refseq` tables; the probe's accession-route genes are the union over its accessions. Classes:
    no_accession, accession_unmatched (no accession found in org.Hs.eg.db), unique (exactly one gene),
    ambiguous (more than one gene). Only `unique` is an accession-route assignment.
    Without org.Hs.eg.db (v1) the route's assignments are reported as NOT COMPUTED.
Figures observed in the 2026-10-12 session for the accession route were never saved to the project;
v1 carried them as a non-reproducible appendix; v2 recomputes the same quantities and reports agreement.

Inputs are verified against their manifests before use. No GEO data are read; nothing is installed.
Writes reports/annotation_audit/illumina_route_comparison/<version>/ and never overwrites a version.
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
IOA = ROOT / "reports/annotation_audit/illumina_option_a/v1"
MISSING_ORG = {"file": "org.Hs.eg.db_3.23.1.tar.gz", "bytes": 103790170, "md5_published": "813be1921e7bc08c1348dbce9d244d0a",
               "sha256_recorded_2026_10_12": "470620665cf49d0319422731164f377e3e74253989f1d33a8a1d100cc3d49cfe",
               "url": "https://bioconductor.org/packages/3.23/data/annotation/src/contrib/org.Hs.eg.db_3.23.1.tar.gz"}
PLATFORMS = [  # label, tarball, sqlite member, accession query (probe, accession), Option A TSV, cohort
    ("illuminaHumanv3", "illuminaHumanv3.db_1.26.0.tar.gz", "illuminaHumanv3.db/inst/extdata/illuminaHumanv3.sqlite",
     "SELECT probe_id, accession FROM accessions", "illuminaHumanv3_probe_classification_PROVISIONAL.tsv", "GSE63060"),
    ("illuminaHumanv4", "illuminaHumanv4.db_1.26.0.tar.gz", "illuminaHumanv4.db/inst/extdata/illuminaHumanv4.sqlite",
     "SELECT probe_id, accession FROM accessions", "illuminaHumanv4_probe_classification_PROVISIONAL.tsv", "GSE63061"),
    ("lumi HT-12 v4 R2", "lumiHumanIDMapping_1.10.1.tar.gz", "lumiHumanIDMapping/inst/extdata/lumiHumanIDMapping.sqlite",
     "SELECT t.Probe_Id, m.Accession FROM HumanHT12_V4_0_R2_15002873_B t LEFT JOIN nuID_MappingInfo m ON m.nuID = t.nuID",
     "lumi_HT12_v4_R2_probe_classification_PROVISIONAL.tsv", "GSE140829 applicability unverified (D19)"),
]
PRIOR_SESSION_ACCESSION = {  # observed 2026-10-12 against the PACKAGE's own Entrez IDs (not against Option A); never saved
    "illuminaHumanv3": {"denominator": "29,551 single-gene probes", "route_exactly_one_gene": 29294, "same_gene": 29244,
                        "different_gene": 50, "route_ambiguous": 10, "no_route": 247},
    "illuminaHumanv4": {"denominator": "34,160 single-gene probes", "route_exactly_one_gene": 33761, "same_gene": 33697,
                        "different_gene": 64, "route_ambiguous": 10, "no_route": 389},
    "lumi HT-12 v4 R2": {"denominator": "47,323 nuIDs (manifest rows)", "route_resolved_exactly_one_gene": 31130,
                         "agrees_with_lumi_EntrezID": 30396, "differs_from_lumi_EntrezID": 283},
}
OPTA_ELIGIBLE = ("eligible_direct", "eligible_via_history_replacement")
ORG_MEMBER = "org.Hs.eg.db/inst/extdata/org.Hs.eg.sqlite"
ORG_QUERY = ("SELECT a.accession, g.gene_id FROM accessions a JOIN genes g ON g._id = a._id "
             "UNION SELECT r.accession, g.gene_id FROM refseq r JOIN genes g ON g._id = r._id")


def load_org_map() -> dict[str, frozenset] | None:
    """Unversioned accession -> current Entrez IDs from the retained org.Hs.eg.db 3.23.1 (None if not retained)."""
    if not (REF / MISSING_ORG["file"]).exists():
        return None
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_org_") as tmp:
        db = _sqlite_from_tar(REF / MISSING_ORG["file"], ORG_MEMBER, Path(tmp))
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        m = defaultdict(set)
        for a, g in con.execute(ORG_QUERY):
            m[str(a)].add(str(g))
        con.close()
    return {k: frozenset(v) for k, v in m.items()}


def verify() -> dict:
    ref = {e["file"]: e for e in json.loads((REF / "download_manifest.json").read_text())["files"]}
    man = json.loads((IOA / "counts_manifest_PROVISIONAL.json").read_text())
    problems, out = [], {"tarballs": {}, "option_a_outputs": {}}
    for _, tar, *_ in PLATFORMS:
        h = file_hashes(REF / tar)
        if (h["bytes"], h["md5"], h["sha256"]) != (ref[tar]["bytes"], ref[tar]["md5_published"], ref[tar]["sha256"]):
            problems.append(f"{tar} does not match reference manifest")
        out["tarballs"][tar] = h
    for name, sha in man["determinism"]["output_sha256"].items():
        h = file_hashes(IOA / name)
        if h["sha256"] != sha:
            problems.append(f"{name} does not match illumina_option_a/v1 manifest")
        out["option_a_outputs"][name] = h
    out["option_a_manifest"] = file_hashes(IOA / "counts_manifest_PROVISIONAL.json")
    out["org_hs_eg_db_retained"] = (REF / MISSING_ORG["file"]).exists()
    if out["org_hs_eg_db_retained"]:
        h = file_hashes(REF / MISSING_ORG["file"])
        e = ref.get(MISSING_ORG["file"])
        if e is None or (h["bytes"], h["md5"], h["sha256"]) != (e["bytes"], e["md5_published"], e["sha256"]) \
                or h["sha256"] != MISSING_ORG["sha256_recorded_2026_10_12"]:
            problems.append("org.Hs.eg.db_3.23.1.tar.gz does not match reference manifest / recorded SHA-256")
        out["org_hs_eg_db"] = h
    if problems:
        raise SystemExit("INPUT VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    return out


def pct(n, d):
    return f"{100 * n / d:.2f}%" if d else "n/a"


def platform(label, tar, member, query, opt_tsv, cohort, orgmap=None):
    with open(IOA / opt_tsv, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    n = len(rows)
    single = [r for r in rows if r["n_package_genes"] == "1"]
    cls = Counter(r["option_a_class"] for r in rows)
    elig = [r for r in rows if r["option_a_class"] in OPTA_ELIGIBLE]
    coll = [r for r in elig if r["successor_directly_mapped"] == "yes"]
    genes = defaultdict(int)
    for r in elig:
        genes[r["option_a_gene_id"]] += 1
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_route_") as tmp:
        db = _sqlite_from_tar(REF / tar, member, Path(tmp))
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        acc_rows = con.execute(query).fetchall()
        con.close()
    acc = defaultdict(set)
    for pid, a in acc_rows:
        if a is not None and str(a).strip():
            acc[str(pid)].add(str(a).strip())
    probe_ids = {r["probe_id"] for r in rows}
    unknown = set(acc) - probe_ids
    types = Counter()
    for s in acc.values():
        for a in s:
            types[a.split("_")[0] + "_" if "_" in a else "GenBank (no prefix)"] += 1
    with_acc = sum(1 for r in rows if r["probe_id"] in acc)
    single_with_acc = sum(1 for r in single if r["probe_id"] in acc)
    elig_with_acc = sum(1 for r in elig if r["probe_id"] in acc)
    versioned = sum(1 for s in acc.values() for a in s if "." in a)
    metrics = {
        "platform": label, "cohort": cohort, "probes_total": n,
        "single_gene_probes": len(single), "multi_gene_probes": cls["multiple_mappings_excluded"],
        "no_gene_in_package": cls["no_assignment_in_package"],
        "option_a": {"eligible": len(elig), "eligible_direct": cls["eligible_direct"],
                     "eligible_via_replacement": cls["eligible_via_history_replacement"],
                     "no_replacement": cls["discontinued_no_replacement"] + cls["chain_ends_no_replacement"],
                     "unexplained": cls["unexplained_absent_no_history"],
                     "pct_eligible_of_all_probes": pct(len(elig), n), "pct_eligible_of_single_gene_probes": pct(len(elig), len(single)),
                     "distinct_genes": len(genes), "genes_with_more_than_one_probe": sum(v > 1 for v in genes.values()),
                     "collision_probes": len(coll),
                     "collision_successor_genes": len({r["option_a_gene_id"] for r in coll}),
                     "collision_source_genes": len({r["package_gene_id"] for r in coll})},
        "accession_route_inputs": {"probes_with_accession": with_acc, "pct_of_all_probes": pct(with_acc, n),
                                   "single_gene_probes_with_accession": single_with_acc,
                                   "pct_of_single_gene_probes": pct(single_with_acc, len(single)),
                                   "option_a_eligible_probes_with_accession": elig_with_acc,
                                   "accession_values": sum(len(s) for s in acc.values()),
                                   "probes_with_more_than_one_accession": sum(len(s) > 1 for s in acc.values()),
                                   "accessions_with_version_suffix": versioned, "accession_prefixes": dict(sorted(types.items())),
                                   "accession_probe_ids_not_in_option_a_table": len(unknown)},
        "accession_route_assignments": "NOT COMPUTED: org.Hs.eg.db 3.23.1 not retained",
    }
    extra_checks = []
    if orgmap is not None:
        ar, cmp_, prior, extra_checks = accession_route(label, rows, acc, orgmap)
        metrics["accession_route_assignments"] = ar
        metrics["route_comparison"] = cmp_
        metrics["prior_session_replication"] = prior
    checks = [
        (f"{label}: Option A classes sum to probes", sum(cls.values()) == n),
        (f"{label}: single + multi + none = probes", len(single) + cls["multiple_mappings_excluded"] + cls["no_assignment_in_package"] == n),
        (f"{label}: eligible <= single-gene probes", len(elig) <= len(single)),
        (f"{label}: every accession probe ID exists in the Option A table", not unknown),
    ] + extra_checks
    return metrics, checks


def accession_route(label, rows, acc, orgmap):
    """Per-probe accession-route class and a like-for-like comparison with Option A on the same probes."""
    n = len(rows)
    acls, agene, cross = Counter(), {}, Counter()
    for r in rows:
        pid = r["probe_id"]
        if pid not in acc:
            c, gs = "no_accession", frozenset()
        else:
            gs = frozenset().union(*(orgmap.get(a, frozenset()) for a in acc[pid]))
            c = "accession_unmatched" if not gs else ("unique" if len(gs) == 1 else "ambiguous")
        acls[c] += 1
        agene[pid] = (c, gs)
        oa = "optionA_eligible" if r["option_a_class"] in OPTA_ELIGIBLE else f"optionA_{r['option_a_class']}"
        cross[(oa, c)] += 1
    both = conc = disc = amb_incl = amb_excl = oa_only = acc_only = 0
    oa_genes, acc_genes = set(), set()
    for r in rows:
        c, gs = agene[r["probe_id"]]
        e = r["option_a_class"] in OPTA_ELIGIBLE
        if e:
            oa_genes.add(r["option_a_gene_id"])
        if c == "unique":
            acc_genes.add(next(iter(gs)))
        if e and c == "unique":
            both += 1
            if r["option_a_gene_id"] in gs:
                conc += 1
            else:
                disc += 1
        elif e and c == "ambiguous":
            if r["option_a_gene_id"] in gs:
                amb_incl += 1
            else:
                amb_excl += 1
        elif e:
            oa_only += 1
        elif c == "unique":
            acc_only += 1
    n_oa = sum(1 for r in rows if r["option_a_class"] in OPTA_ELIGIBLE)
    ar = {"classes": dict(sorted(acls.items())), "assigned_unique": acls["unique"],
          "pct_assigned_of_all_probes": pct(acls["unique"], n), "distinct_genes": len(acc_genes)}
    cmp_ = {"denominator_all_probes": n, "optionA_eligible": n_oa, "accession_unique": acls["unique"],
            "both_assign_one_gene": both, "concordant": conc, "discordant": disc,
            "pct_concordant_of_both": pct(conc, both),
            "optionA_eligible_accession_ambiguous_including_optionA_gene": amb_incl,
            "optionA_eligible_accession_ambiguous_excluding_optionA_gene": amb_excl,
            "optionA_eligible_accession_unresolved": oa_only,
            "accession_unique_optionA_not_eligible": acc_only,
            "neither_assigns": n - both - amb_incl - amb_excl - oa_only - acc_only,
            "genes_both_routes": len(oa_genes & acc_genes), "genes_optionA_only": len(oa_genes - acc_genes),
            "genes_accession_only": len(acc_genes - oa_genes),
            "cross_tab_optionA_x_accession": {f"{a} | {b}": v for (a, b), v in sorted(cross.items())}}
    # Re-computation of the quantities observed (unsaved) on 2026-10-12: accession route vs the PACKAGE's own Entrez ID.
    single = [r for r in rows if r["n_package_genes"] == "1"]
    same = diff = amb = none = 0
    for r in single:
        c, gs = agene[r["probe_id"]]
        if c == "unique":
            same += r["package_gene_id"] in gs
            diff += r["package_gene_id"] not in gs
        elif c == "ambiguous":
            amb += 1
        else:
            none += 1
    # Reconciliation of metric M1 (same-probe Option A comparison) with metric M2 (package-ID comparison).
    # M1 set = Option A eligible AND accession unique; M2 set = single-gene package probe AND accession unique.
    # Option A eligible implies single-gene, so M1 is a subset of M2; every M2 probe is labelled with both results.
    trans, recon_rows = Counter(), []
    m1_set, m2_set = set(), set()
    for r in single:
        c, gs = agene[r["probe_id"]]
        if c != "unique":
            continue
        m2_set.add(r["probe_id"])
        e = r["option_a_class"] in OPTA_ELIGIBLE
        if e:
            m1_set.add(r["probe_id"])
        m2 = "same" if r["package_gene_id"] in gs else "different"
        m1 = ("concordant" if r["option_a_gene_id"] in gs else "discordant") if e else "not_in_M1 (Option A not eligible)"
        trans[(m2, m1, r["option_a_class"])] += 1
        if (m2, m1) != ("same", "concordant"):
            recon_rows.append({"platform": label, "probe_id": r["probe_id"], "package_gene_id": r["package_gene_id"],
                               "option_a_class": r["option_a_class"], "option_a_gene_id": r["option_a_gene_id"],
                               "history_chain": r["history_chain"], "accession_route_gene": next(iter(gs)),
                               "accessions": ";".join(sorted(acc[r["probe_id"]])), "M2_result": m2, "M1_result": m1})
    reconciliation = {"M1_total_both_assign": both, "M2_total_package_gene_and_accession_unique": same + diff,
                      "M1_subset_of_M2": m1_set <= m2_set, "in_M2_not_M1": sorted(m2_set - m1_set),
                      "transitions_M2_to_M1_by_option_a_class": {f"{a} -> {b} [{k}]": v for (a, b, k), v in sorted(trans.items())}}
    checks_recon = [
        (f"{label}: M1 set is a subset of M2 set", m1_set <= m2_set),
        (f"{label}: M2 total = M1 total + probes in M2 not M1", same + diff == both + len(m2_set - m1_set)),
        (f"{label}: M1 concordant = sum of transitions to concordant",
         conc == sum(v for (a, b, k), v in trans.items() if b == "concordant")),
        (f"{label}: M2 same = transitions same -> concordant", same == trans[("same", "concordant", "eligible_direct")]
         + trans[("same", "concordant", "eligible_via_history_replacement")]),
    ]
    prior = {"single_gene_probes": len(single), "route_exactly_one_gene": same + diff, "same_gene": same,
             "different_gene": diff, "route_ambiguous": amb, "no_route": none,
             "all_probes_resolved": acls["unique"] + acls["ambiguous"], "all_probes_unique": acls["unique"],
             "all_probes_ambiguous": acls["ambiguous"], "previously_reported": PRIOR_SESSION_ACCESSION[label]}
    checks = [
        (f"{label}: accession-route classes sum to probes", sum(acls.values()) == n),
        (f"{label}: comparison categories sum to probes",
         both + amb_incl + amb_excl + oa_only + acc_only + cmp_["neither_assigns"] == n and cmp_["neither_assigns"] >= 0),
        (f"{label}: concordant + discordant = both assign one gene", conc + disc == both),
        (f"{label}: Option A eligible partition sums", both + amb_incl + amb_excl + oa_only == n_oa),
        (f"{label}: cross-tab sums to probes", sum(cross.values()) == n),
    ] + checks_recon
    cmp_["reconciliation_M1_vs_M2"] = reconciliation
    cmp_["_reconciliation_rows"] = recon_rows
    return ar, cmp_, prior, checks


def report(metrics: list[dict], checks, src) -> str:
    L = ["# Illumina mapping-route comparison — v1 (decision support; no policy approved)", "",
         "## Executive summary", "",
         "- **Option A** (package Entrez IDs + approved gene-history procedure, cutoff 20260318) is fully quantified "
         "below from verified retained outputs.",
         "- **Accession route:** only its inputs could be measured. Resolving accessions to current Entrez IDs requires "
         "org.Hs.eg.db 3.23.1, which is not retained in the project; route assignments, concordance, discordance and "
         "ambiguity were therefore **not computed**. The comparison is incomplete until that source is retained.",
         "- No Illumina mapping policy is approved by this report. GSE140829 remains governed by D19; D17 is unchanged.", "",
         "## Methods and provenance", "",
         "- Option A: `reports/annotation_audit/illumina_option_a/v1/` (hashes verified against its manifest).",
         "- Accession-route inputs: `accessions` tables of illuminaHumanv3.db / illuminaHumanv4.db 1.26.0 and the "
         "`Accession` column of lumiHumanIDMapping 1.10.1 (`nuID_MappingInfo` joined to `HumanHT12_V4_0_R2_15002873_B`), "
         "read from the retained tarballs in `reference/bioconductor_3.23/` (hashes verified against its manifest).",
         f"- Missing for the accession route: `{MISSING_ORG['file']}` ({MISSING_ORG['bytes']:,} bytes; published MD5 "
         f"`{MISSING_ORG['md5_published']}`; recorded SHA-256 `{MISSING_ORG['sha256_recorded_2026_10_12']}`; {MISSING_ORG['url']}).",
         "- Denominators: *probes* = rows of each package's probe table (lumi: HT-12 v4 R2 manifest rows); *single-gene "
         "probes* = probes with exactly one Entrez ID in the package. Probe-level and gene-level figures are kept separate.", "",
         "## Comparison tables (probe level unless stated)", ""]
    for m in metrics:
        a, c = m["option_a"], m["accession_route_inputs"]
        L += [f"### {m['platform']} ({m['cohort']})", "",
              "| Measure | Option A | Accession route |", "|---|---:|---:|",
              f"| Probes (denominator) | {m['probes_total']:,} | {m['probes_total']:,} |",
              f"| Single-gene / multi-gene / no gene (package) | {m['single_gene_probes']:,} / {m['multi_gene_probes']:,} / {m['no_gene_in_package']:,} | same package table |",
              f"| Probes with an input for the route | {m['single_gene_probes']:,} single-gene | {c['probes_with_accession']:,} with ≥1 accession ({c['pct_of_all_probes']}) |",
              f"| Eligible assignments | {a['eligible']:,} ({a['pct_eligible_of_all_probes']} of probes; {a['pct_eligible_of_single_gene_probes']} of single-gene) | not computed |",
              f"| — direct / via replacement | {a['eligible_direct']:,} / {a['eligible_via_replacement']:,} | not computed |",
              f"| No replacement / unexplained | {a['no_replacement']:,} / {a['unexplained']:,} | not computed |",
              "| Concordant / discordant / ambiguous / unresolved | not applicable within one route | not computed |",
              f"| Distinct genes (gene level) | {a['distinct_genes']:,} | not computed |",
              f"| Genes measured by >1 eligible probe (gene level) | {a['genes_with_more_than_one_probe']:,} | not computed |",
              f"| Successor collisions: probes / distinct successor genes / distinct historical source genes | {a['collision_probes']:,} / {a['collision_successor_genes']:,} / {a['collision_source_genes']:,} | not applicable |", "",
              f"Accession-route inputs: {c['single_gene_probes_with_accession']:,} single-gene probes have ≥1 accession "
              f"({c['pct_of_single_gene_probes']}); {c['option_a_eligible_probes_with_accession']:,} Option A-eligible probes have one; "
              f"{c['probes_with_more_than_one_accession']:,} probes carry >1 accession; {c['accessions_with_version_suffix']:,} "
              f"accession values carry a version suffix; prefixes {c['accession_prefixes']}.", ""]
    L += ["## Reconciliation checks", ""] + [f"- [{'OK' if ok else 'FAILED'}] {n}" for n, ok in checks] + [""]
    L += ["## Implications for gene-level analysis (G3)", "",
          "- Under G3 every eligible probe of a gene is averaged. Each successor collision adds a replaced probe to a gene "
          "that already has directly mapped probes; its signal becomes part of that gene's average (Option A collision "
          "counts above). No probes were merged in these audits.",
          "- Probes without an eligible assignment are excluded from gene-level units (\"unmapped\", counted), so lower "
          "coverage reduces the measurable gene set and the validation/specificity measurability (v5 §7.3).",
          "- Option A's probe-to-gene knowledge dates to 2015-Mar17 (illuminaHumanv3/v4); lumi's manifest-based mapping "
          "has no recorded date. The accession route would use the 2026-03-18 Entrez snapshot but relies on unversioned "
          "accession roots, so sequence-level equivalence to the current transcript is not established for either route.", "",
          "## Neutral assessment of trade-offs", "",
          "- **Option A:** fully reproducible from retained inputs; consistent with the approved GPL570 policy (D6-F); "
          "older probe-to-gene knowledge; collisions concentrated in lumi.",
          "- **Accession route:** current Entrez snapshot, but its coverage, concordance and ambiguity on these platforms "
          "cannot be verified from retained evidence; it needs org.Hs.eg.db 3.23.1 retained before it can be evaluated.",
          "- A like-for-like decision is not supported until the accession route is recomputed from a retained source.", "",
          "## Decisions that remain unapproved", "",
          "- Illumina mapping policy (Option A, accession route, or other) for GSE63060 and GSE63061.",
          "- GSE140829 mapping (D19), including whether the HT-12 v4 R2 manifest table applies.",
          "- D17 feature rule; retention of org.Hs.eg.db 3.23.1 (download requires approval); installation of any annotation package.", "",
          "## Appendix — accession-route figures from the 2026-10-12 session (NOT reproducible from retained evidence)", "",
          "Observed interactively against each package's own Entrez IDs (not against Option A) and never saved to the "
          "project. Shown for orientation only; they are not verified results.", ""]
    for k, v in PRIOR_SESSION_ACCESSION.items():
        L.append(f"- {k}: " + "; ".join(f"{a} {b}" for a, b in v.items()))
    return "\n".join(L) + "\n"


def _recon_md(m: dict) -> list[str]:
    rc = m["route_comparison"]["reconciliation_M1_vs_M2"]
    lines = ["**Two different agreement metrics (do not compare their totals directly)**", "",
             "- **M1 — same-probe Option A comparison:** probes that Option A assigns AND the accession route resolves to "
             "one gene; agreement is judged against the Option A gene (after gene-history reconciliation). "
             f"Total {rc['M1_total_both_assign']:,} (concordant + discordant above).",
             "- **M2 — package-ID comparison (the 2026-10-12 definition):** probes with exactly one package Entrez ID AND "
             "an accession route resolving to one gene; agreement is judged against the package's own, un-reconciled ID. "
             f"Total {rc['M2_total_package_gene_and_accession_unique']:,} (same + different below).",
             f"- M1 ⊆ M2: {rc['M1_subset_of_M2']}. Probes in M2 but not M1 ({len(rc['in_M2_not_M1'])}): "
             + (", ".join(rc["in_M2_not_M1"][:20]) + (" …" if len(rc["in_M2_not_M1"]) > 20 else "") if rc["in_M2_not_M1"] else "none")
             + " (their package ID has no eligible Option A assignment).",
             "- Probe-level transitions M2 → M1 [Option A class]: "
             + "; ".join(f"{k}: {v:,}" for k, v in rc["transitions_M2_to_M1_by_option_a_class"].items()) + ".",
             "- Probe records for every transition other than same → concordant: `metric_reconciliation_probes.tsv`.", ""]
    return lines


def report_v2(metrics: list[dict], checks, version: str) -> str:
    L = [f"# Illumina mapping-route comparison — {version} (decision support; no policy approved)", "",
         "## Executive summary", ""]
    for m in metrics:
        c = m["route_comparison"]
        L.append(f"- **{m['platform']}** ({m['cohort']}): Option A assigns {c['optionA_eligible']:,} probes, the accession "
                 f"route {c['accession_unique']:,} (of {m['probes_total']:,}). Where both assign one gene "
                 f"({c['both_assign_one_gene']:,} probes) they agree for {c['concordant']:,} ({c['pct_concordant_of_both']}) "
                 f"and disagree for {c['discordant']:,}.")
    L += ["- Both routes are now computed from retained, hash-verified sources. No Illumina mapping policy is approved; "
          "GSE140829 remains governed by D19; D17 is unchanged.", "",
          "## Methods and provenance", "",
          "- Option A: `reports/annotation_audit/illumina_option_a/v1/` (hashes verified against its manifest).",
          "- Accession route: each probe's accessions (illuminaHumanv3.db / illuminaHumanv4.db 1.26.0 `accessions`; "
          "lumiHumanIDMapping 1.10.1 `nuID_MappingInfo.Accession` for the HT-12 v4 R2 table) matched exactly, without "
          "version suffixes, to the union of org.Hs.eg.db 3.23.1 `accessions` (GenBank) and `refseq` tables, then to "
          "`genes.gene_id` (Entrez Gene snapshot 2026-03-18). Probe genes = union over the probe's accessions.",
          "- Accession-route classes: `unique` (one gene; the only assignment), `ambiguous` (>1 gene), "
          "`accession_unmatched` (accessions not in org.Hs.eg.db), `no_accession`.",
          "- All sources read from `reference/bioconductor_3.23/` (hashes verified against `download_manifest.json`); nothing installed.",
          "- Denominators: *probes* = rows of each package's probe table (lumi: HT-12 v4 R2 manifest rows). Both routes are "
          "evaluated on exactly the same probes. Gene counts are distinct current Entrez IDs with at least one assigned probe.", "",
          "## Comparison tables", ""]
    for m in metrics:
        a, r, c, pr = m["option_a"], m["accession_route_assignments"], m["route_comparison"], m["prior_session_replication"]
        L += [f"### {m['platform']} ({m['cohort']})", "",
              "**Probe level** (denominator: all probes)", "",
              "| Measure | Option A | Accession route |", "|---|---:|---:|",
              f"| Probes | {m['probes_total']:,} | {m['probes_total']:,} |",
              f"| Assigned to exactly one gene | {a['eligible']:,} ({a['pct_eligible_of_all_probes']}) | {r['assigned_unique']:,} ({r['pct_assigned_of_all_probes']}) |",
              f"| Not assigned | {m['probes_total'] - a['eligible']:,} | {m['probes_total'] - r['assigned_unique']:,} |",
              f"| Route classes | direct {a['eligible_direct']:,}; via replacement {a['eligible_via_replacement']:,}; no replacement {a['no_replacement']:,}; unexplained {a['unexplained']:,}; multi-gene {m['multi_gene_probes']:,}; no gene {m['no_gene_in_package']:,} | " +
              "; ".join(f"{k} {v:,}" for k, v in r["classes"].items()) + " |", "",
              "**Like-for-like comparison on the same probes**", "",
              "| Category | Probes |", "|---|---:|",
              f"| Both assign one gene | {c['both_assign_one_gene']:,} |",
              f"| — concordant | {c['concordant']:,} ({c['pct_concordant_of_both']}) |",
              f"| — discordant | {c['discordant']:,} |",
              f"| Option A assigns; accession route ambiguous, includes the Option A gene | {c['optionA_eligible_accession_ambiguous_including_optionA_gene']:,} |",
              f"| Option A assigns; accession route ambiguous, excludes the Option A gene | {c['optionA_eligible_accession_ambiguous_excluding_optionA_gene']:,} |",
              f"| Option A assigns; accession route unresolved (no accession or unmatched) | {c['optionA_eligible_accession_unresolved']:,} |",
              f"| Accession route assigns; Option A does not | {c['accession_unique_optionA_not_eligible']:,} |",
              f"| Neither assigns | {c['neither_assigns']:,} |", "",
              "**Gene level** (distinct current Entrez IDs with ≥1 assigned probe)", "",
              "| Measure | Genes |", "|---|---:|",
              f"| Option A | {a['distinct_genes']:,} |", f"| Accession route | {r['distinct_genes']:,} |",
              f"| Both routes | {c['genes_both_routes']:,} |", f"| Option A only | {c['genes_optionA_only']:,} |",
              f"| Accession route only | {c['genes_accession_only']:,} |", "",
              f"Option A successor collisions (flagged, not merged): {a['collision_probes']:,} probes; "
              f"{a['collision_successor_genes']:,} successor genes; {a['collision_source_genes']:,} historical source genes.", "",
              "Cross-tabulation (Option A status × accession-route class): " +
              "; ".join(f"{k}: {v:,}" for k, v in c["cross_tab_optionA_x_accession"].items()) + ".", "",
              *( [] if version == "v2" else _recon_md(m) ),
              "**Re-computation of the unsaved 2026-10-12 figures** (accession route vs the package's own Entrez ID; "
              f"denominator {pr['single_gene_probes']:,} single-gene probes): exactly one gene {pr['route_exactly_one_gene']:,} "
              f"(same {pr['same_gene']:,}, different {pr['different_gene']:,}), ambiguous {pr['route_ambiguous']:,}, no route "
              f"{pr['no_route']:,}; all probes: unique {pr['all_probes_unique']:,}, ambiguous {pr['all_probes_ambiguous']:,}. "
              "Previously reported (not saved): " + "; ".join(f"{k} {v}" for k, v in pr["previously_reported"].items()) + ".", ""]
    L += ["## Reconciliation checks", ""] + [f"- [{'OK' if ok else 'FAILED'}] {n}" for n, ok in checks] + [""]
    L += ["## Implications for gene-level analysis (G3)", "",
          "- Under G3 every assigned probe of a gene is averaged, so the route determines which probes enter each gene's "
          "mean and which genes are measurable at all (unassigned probes are \"unmapped\" and counted).",
          "- Discordant probes would be averaged into different genes under the two routes; ambiguous accession-route "
          "probes would be lost under that route (multi-gene exclusion).",
          "- Option A collisions add replaced probes to genes that already have directly mapped probes.", "",
          "## Known limitations", "",
          "- Option A's probe-to-gene knowledge dates to 2015-Mar17 (illuminaHumanv3/v4); lumi's manifest mapping is undated.",
          "- The accession route uses the 2026-03-18 snapshot but matches unversioned accession roots: a match does not "
          "establish that the probe sequence targets the current transcript.",
          "- Package accession tables come from the manufacturer annotation (ACCNUM, documented in the chip packages); "
          "their own date is that of the package build.",
          "- Presence of probes in each cohort's Series Matrix and the D17 feature rule are not assessed (no GEO data used).", "",
          "## Neutral assessment of trade-offs", "",
          "- **Option A:** consistent with the approved GPL570 policy (D6-F) and the approved gene-history procedure; older "
          "probe-to-gene knowledge; collisions flagged.",
          "- **Accession route:** a single current snapshot with no history step; coverage, ambiguity and concordance as "
          "tabulated above; depends on unversioned accession matching.",
          "- The tables above, not this report, should drive the choice; neither route is approved here.", "",
          "## Decisions that remain unapproved", "",
          "- Illumina mapping policy (Option A, accession route, a combination, or other) for GSE63060 and GSE63061.",
          "- GSE140829 mapping (D19), including whether the HT-12 v4 R2 manifest table applies.",
          "- D17 feature rule; installation of any annotation package.", ""]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--out-dir", type=Path, default=None, help="override output directory (reproduction checks)")
    args = ap.parse_args()
    out = args.out_dir or ROOT / "reports/annotation_audit/illumina_route_comparison" / args.version
    if out.exists():
        raise SystemExit(f"{out.relative_to(ROOT)} already exists; choose a new --version")
    src = verify()

    def run():
        orgmap = load_org_map() if src["org_hs_eg_db_retained"] else None
        ms, ck = [], []
        for p in PLATFORMS:
            m, c = platform(*p, orgmap=orgmap)
            ms.append(m)
            ck += c
        rows = []
        sections = ("option_a", "accession_route_inputs") + (
            ("accession_route_assignments", "route_comparison", "prior_session_replication") if orgmap is not None else ())
        recon = [r for m in ms for r in m.get("route_comparison", {}).pop("_reconciliation_rows", [])] if orgmap is not None else []
        for m in ms:
            if args.version == "v2" and "route_comparison" in m:
                m["route_comparison"].pop("reconciliation_M1_vs_M2", None)
            for sect in sections:
                for k, v in m[sect].items():
                    rows.append({"platform": m["platform"], "section": sect, "measure": k, "value": json.dumps(v) if isinstance(v, dict) else v})
        if args.version == "v2":   # v2 was produced before the M1/M2 reconciliation existed; reproduce it exactly
            ck = [c for c in ck if "M1" not in c[0] and "M2" not in c[0]]
        rep_md = report_v2(ms, ck, args.version) if orgmap is not None else report(ms, ck, src)
        files = {"route_comparison_metrics.tsv": tsv(rows, ["platform", "section", "measure", "value"]), "REPORT.md": rep_md}
        if orgmap is not None and args.version != "v2":
            files["metric_reconciliation_probes.tsv"] = tsv(recon, ["platform", "probe_id", "package_gene_id", "option_a_class",
                                                                    "option_a_gene_id", "history_chain", "accession_route_gene",
                                                                    "accessions", "M2_result", "M1_result"])
        return files, ms, ck

    f1, m1, c1 = run()
    f2, m2, _ = run()
    h1 = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f1.items()}
    det = {"runs_compared": 2, "identical": h1 == {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f2.items()} and m1 == m2,
           "output_sha256": h1}
    status = "OK" if all(ok for _, ok in c1) else "FAILED"
    if status != "OK" or not det["identical"]:
        raise SystemExit(json.dumps({"checks": c1, "determinism": det}, indent=2) + "\nVALIDATION OR DETERMINISM FAILED (nothing written)")
    out.mkdir(parents=True)
    for k, v in f1.items():
        (out / k).write_text(v, encoding="utf-8")
    manifest = {"status": "Decision support only; no mapping policy approved", "sources": src, "missing_source": MISSING_ORG,
                "metrics": m1, "validation": {"status": status, "checks": [{"check": n, "status": "OK" if ok else "FAILED"} for n, ok in c1]},
                "determinism": det, "command": "python scripts/annotation_illumina_route_comparison.py --version " + args.version}
    (out / "comparison_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"written: {out}; validation {status}; determinism identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
