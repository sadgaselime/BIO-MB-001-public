#!/usr/bin/env python3
"""Illumina annotation-route decision matrix (assessment only; no mapping policy is selected or approved).

Compares Option A (package Entrez IDs reconciled by the approved gene-history procedure, cutoff 20260318)
with the accession route (probe accessions -> org.Hs.eg.db 3.23.1) for three platform packages,
independently, using:
  * reports/annotation_audit/illumina_route_comparison/v3/ (report, metrics, M1/M2 reconciliation, manifest)
  * reports/annotation_audit/illumina_option_a/v1/        (per-probe Option A classes)
  * reference/bioconductor_3.23/                           (retained, verified source tarballs)
Every overlapping figure is recomputed from the retained sources and must equal the v3 manifest.
No weighting or ranking is applied: each criterion records evidence, which route (if either) has an
advantage on that criterion alone, the limitation, and a status (decisive / supportive / unresolved).
No GEO data are read; nothing is installed. Writes
reports/annotation_audit/illumina_route_decision_matrix/<version>/ and never overwrites a version.
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
sys.path.insert(0, str(ROOT / "src"))
from biomarker_project.gene_history_reconciliation import _sqlite_from_tar, file_hashes, tsv  # noqa: E402

V3 = ROOT / "reports/annotation_audit/illumina_route_comparison/v3"
IOA = ROOT / "reports/annotation_audit/illumina_option_a/v1"
GH = ROOT / "reports/annotation_audit/ncbi_gene_history/v1"
REF = ROOT / "reference/bioconductor_3.23"
_spec = importlib.util.spec_from_file_location("route_cmp", ROOT / "scripts/annotation_illumina_route_comparison.py")
rc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rc)

STATUSES = ("decisive", "supportive", "unresolved")
ADVANTAGES = ("Option A", "accession route", "neither", "not determinable")
COLUMNS = ["platform", "cohort_context", "criterion_id", "criterion", "option_a_evidence", "accession_route_evidence",
           "advantage", "limitation", "status", "sources"]


def pct(n, d):
    return f"{100 * n / d:.2f}%" if d else "n/a"


# ------------------------------------------------------------------ verification
def verify() -> dict:
    problems = []
    v3m = json.loads((V3 / "comparison_manifest.json").read_text())
    for k, sha in v3m["determinism"]["output_sha256"].items():
        if file_hashes(V3 / k)["sha256"] != sha:
            problems.append(f"v3 {k} does not match its manifest")
    if v3m["validation"]["status"] != "OK":
        problems.append("v3 validation is not OK")
    ref = {e["file"]: e for e in json.loads((REF / "download_manifest.json").read_text())["files"]}
    for tar, rec in {**v3m["sources"]["tarballs"], "org.Hs.eg.db_3.23.1.tar.gz": v3m["sources"]["org_hs_eg_db"]}.items():
        h = file_hashes(REF / tar)
        if h["sha256"] != rec["sha256"] or h["sha256"] != ref[tar]["sha256"]:
            problems.append(f"{tar} differs from the v3 manifest or the reference manifest")
    iom = json.loads((IOA / "counts_manifest_PROVISIONAL.json").read_text())
    for k, sha in iom["determinism"]["output_sha256"].items():
        if file_hashes(IOA / k)["sha256"] != sha or v3m["sources"]["option_a_outputs"][k]["sha256"] != sha:
            problems.append(f"Option A {k} does not match its manifest or the v3 record")
    ghm = json.loads((GH / "reconciliation_manifest.json").read_text())
    if file_hashes(GH / "reconciliation_manifest.json")["sha256"] != iom["sources"]["v1_manifest_sha256"]:
        problems.append("gene-history v1 manifest differs from the one recorded by Option A v1")
    if ghm["parameters"]["view_a_cutoff_inclusive"] != "20260318":
        problems.append("gene-history cutoff is not 20260318")
    if problems:
        raise SystemExit("INPUT VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    inputs = {str(p.relative_to(ROOT)): file_hashes(p)["sha256"] for p in sorted(
        [*V3.iterdir(), *IOA.iterdir(), GH / "reconciliation_manifest.json", REF / "download_manifest.json",
         ROOT / "scripts/annotation_illumina_route_comparison.py"]) if p.is_file()}
    return {"v3_manifest": v3m, "inputs_sha256": inputs}


def package_metadata() -> dict:
    """Source dates read from the retained package databases (traceable, not from memory)."""
    out = {}
    for tar, member, table in [("illuminaHumanv3.db_1.26.0.tar.gz", "illuminaHumanv3.db/inst/extdata/illuminaHumanv3.sqlite", "metadata"),
                               ("illuminaHumanv4.db_1.26.0.tar.gz", "illuminaHumanv4.db/inst/extdata/illuminaHumanv4.sqlite", "metadata"),
                               ("lumiHumanIDMapping_1.10.1.tar.gz", "lumiHumanIDMapping/inst/extdata/lumiHumanIDMapping.sqlite", "metadata"),
                               ("org.Hs.eg.db_3.23.1.tar.gz", "org.Hs.eg.db/inst/extdata/org.Hs.eg.sqlite", "metadata")]:
        with tempfile.TemporaryDirectory(prefix="bio_mb_001_dm_") as tmp:
            db = _sqlite_from_tar(REF / tar, member, Path(tmp))
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            md = {str(k): str(v) for k, v in con.execute(f"SELECT name, value FROM {table}")}
            con.close()
        out[tar] = {k: (md[k].strip() or "not recorded") for k in ("EGSOURCEDATE", "EGSOURCENAME", "REFSEQ VERSION", "CHIPNAME") if k in md}
    return out


# ------------------------------------------------------------------ recomputation
def recompute(v3m: dict) -> tuple[dict, list]:
    orgmap = rc.load_org_map()
    data, checks = {}, []
    for (label, tar, member, query, opt_tsv, cohort), m3 in zip(rc.PLATFORMS, v3m["metrics"]):
        assert m3["platform"] == label
        with open(IOA / opt_tsv, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh, delimiter="\t"))
        with tempfile.TemporaryDirectory(prefix="bio_mb_001_dm_") as tmp:
            db = _sqlite_from_tar(REF / tar, member, Path(tmp))
            con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
            acc_rows = con.execute(query).fetchall()
            con.close()
        acc = defaultdict(set)
        for pid, a in acc_rows:
            if a is not None and str(a).strip():
                acc[str(pid)].add(str(a).strip())
        ar, cmp_, prior, _ = rc.accession_route(label, rows, acc, orgmap)
        acc_gene_probes = Counter()
        for r in rows:
            if r["probe_id"] in acc:
                gs = frozenset().union(*(orgmap.get(a, frozenset()) for a in acc[r["probe_id"]]))
                if len(gs) == 1:
                    acc_gene_probes[next(iter(gs))] += 1
        recon = cmp_["reconciliation_M1_vs_M2"]
        pairs = [
            ("accession unique probes", ar["assigned_unique"], m3["accession_route_assignments"]["assigned_unique"]),
            ("accession distinct genes", ar["distinct_genes"], m3["accession_route_assignments"]["distinct_genes"]),
            ("accession classes", ar["classes"], m3["accession_route_assignments"]["classes"]),
            ("M1 both / concordant / discordant", (cmp_["both_assign_one_gene"], cmp_["concordant"], cmp_["discordant"]),
             (m3["route_comparison"]["both_assign_one_gene"], m3["route_comparison"]["concordant"], m3["route_comparison"]["discordant"])),
            ("M1/M2 reconciliation", recon, m3["route_comparison"]["reconciliation_M1_vs_M2"]),
            ("gene overlap", (cmp_["genes_both_routes"], cmp_["genes_optionA_only"], cmp_["genes_accession_only"]),
             (m3["route_comparison"]["genes_both_routes"], m3["route_comparison"]["genes_optionA_only"], m3["route_comparison"]["genes_accession_only"])),
            ("M2 same / different", (prior["same_gene"], prior["different_gene"]),
             (m3["prior_session_replication"]["same_gene"], m3["prior_session_replication"]["different_gene"])),
        ]
        for name, got, want in pairs:
            checks.append((f"{label}: recomputed {name} equals v3 manifest", got == want))
        with open(V3 / "metric_reconciliation_probes.tsv", encoding="utf-8") as fh:
            rec_rows = [r for r in csv.DictReader(fh, delimiter="\t") if r["platform"] == label]
        tsv_trans = Counter(f"{r['M2_result']} -> {r['M1_result']} [{r['option_a_class']}]" for r in rec_rows)
        man_trans = {k: v for k, v in recon["transitions_M2_to_M1_by_option_a_class"].items() if not k.startswith("same -> concordant")}
        checks.append((f"{label}: metric_reconciliation_probes.tsv transitions equal v3 manifest", dict(tsv_trans) == man_trans))
        data[label] = {"cohort": m3["cohort"], "m3": m3, "acc_multi_probe_genes": sum(v > 1 for v in acc_gene_probes.values()),
                       "acc_classes": ar["classes"], "recon": recon}
    return data, checks


# ------------------------------------------------------------------ matrix (pure)
def build_matrix(data: dict, meta: dict) -> list[dict]:
    rows = []
    date = {"illuminaHumanv3": meta["illuminaHumanv3.db_1.26.0.tar.gz"].get("EGSOURCEDATE", ""),
            "illuminaHumanv4": meta["illuminaHumanv4.db_1.26.0.tar.gz"].get("EGSOURCEDATE", ""),
            "lumi HT-12 v4 R2": "not recorded (REFSEQ VERSION: " + meta["lumiHumanIDMapping_1.10.1.tar.gz"].get("REFSEQ VERSION", "not recorded") + ")"}
    org_date = meta["org.Hs.eg.db_3.23.1.tar.gz"].get("EGSOURCEDATE", "")
    for label, d in data.items():
        m, a, r, c, rec = d["m3"], d["m3"]["option_a"], d["m3"]["accession_route_assignments"], d["m3"]["route_comparison"], d["recon"]
        n = m["probes_total"]
        t = rec["transitions_M2_to_M1_by_option_a_class"]
        repl = sum(v for k, v in t.items() if k.startswith("different -> concordant"))
        not_m1 = sum(v for k, v in t.items() if "not_in_M1" in k)
        oa_un = n - a["eligible"]
        ac_un = d["acc_classes"].get("no_accession", 0) + d["acc_classes"].get("accession_unmatched", 0)
        cov_gap = a["eligible"] - r["assigned_unique"]
        src = "v3/comparison_manifest.json; illumina_option_a/v1; recomputed from reference/bioconductor_3.23"

        def add(cid, crit, oa, ac, adv, lim, status, sources=src):
            assert adv in ADVANTAGES and status in STATUSES
            rows.append({"platform": label, "cohort_context": d["cohort"], "criterion_id": cid, "criterion": crit,
                         "option_a_evidence": oa, "accession_route_evidence": ac, "advantage": adv,
                         "limitation": lim, "status": status, "sources": sources})

        add("C01", "Probes assigned exactly one eligible gene (denominator: all platform probes)",
            f"{a['eligible']:,} / {n:,} ({pct(a['eligible'], n)})", f"{r['assigned_unique']:,} / {n:,} ({pct(r['assigned_unique'], n)})",
            "Option A" if cov_gap > 0 else ("accession route" if cov_gap < 0 else "neither"),
            f"Difference {cov_gap:+,} probes. Coverage is platform-wide, not cohort-specific, and higher coverage is not evidence of biological validity.",
            "supportive")
        add("C02", "Distinct current Entrez genes represented (gene level)",
            f"{a['distinct_genes']:,}", f"{r['distinct_genes']:,} (both routes {c['genes_both_routes']:,}; Option A only {c['genes_optionA_only']:,}; accession only {c['genes_accession_only']:,})",
            "Option A" if a["distinct_genes"] > r["distinct_genes"] else "accession route",
            "Gene counts include genes whose only probes are replacement-derived (Option A) or matched by unversioned accession (accession route); measurability in a cohort is not assessed.",
            "supportive")
        add("C03", "Genes represented by more than one eligible probe (gene level; G3 averages them)",
            f"{a['genes_with_more_than_one_probe']:,}", f"{d['acc_multi_probe_genes']:,} (computed in this matrix from retained sources; not reported in v3)", "neither",
            "Multiple probes per gene are expected under G3 and are neither good nor bad in themselves; their effect depends on probe concordance in the cohort.",
            "unresolved")
        add("C04", "M1 — same-probe agreement (probes both routes assign; vs the post-gene-history Option A gene)",
            f"both assign {c['both_assign_one_gene']:,}", f"concordant {c['concordant']:,} ({c['pct_concordant_of_both']} of {c['both_assign_one_gene']:,}); discordant {c['discordant']:,}",
            "neither",
            "Agreement between two annotation routes is not biological confirmation; both may share upstream sources.",
            "supportive")
        add("C05", "ID-replacement effects (M2 → M1 transitions; M2 = vs the package's original Entrez ID)",
            f"{a['eligible_via_replacement']:,} probes assigned via a gene-history successor",
            f"M2 total {rec['M2_total_package_gene_and_accession_unique']:,} vs M1 total {rec['M1_total_both_assign']:,}; "
            f"{repl:,} probes 'different' under M2 become concordant under M1 after replacement; {not_m1:,} probes are in M2 but not M1",
            "neither",
            "M1 and M2 are different metrics; their totals must not be compared directly. Replacement agreement shows the two routes converge on the same current ID, not that the probe measures it.",
            "supportive")
        add("C06", "Genuine disagreements (M1 discordant probes)",
            f"{c['discordant']:,} probes assign a different gene than the accession route", "same probes", "not determinable",
            "Which route is correct for a discordant probe cannot be decided from annotation tables; sequence-level evidence would be required.",
            "unresolved", "v3/metric_reconciliation_probes.tsv")
        add("C07", "Discontinued IDs without replacement / unexplained (Option A); unmatched accessions (accession route)",
            f"no replacement {a['no_replacement']:,}; unexplained {a['unexplained']:,}",
            f"accession unmatched {d['acc_classes'].get('accession_unmatched', 0):,}; no accession {d['acc_classes'].get('no_accession', 0):,}",
            "not determinable",
            "Absence of a current mapping does not establish that a probe is non-functional; an accession absent from org.Hs.eg.db is not proof of retirement.",
            "unresolved")
        add("C08", "Ambiguous assignments (one probe → more than one gene; excluded under both routes)",
            f"multi-gene probes in package {m['multi_gene_probes']:,}", f"accession ambiguous {d['acc_classes'].get('ambiguous', 0):,}",
            "Option A" if m["multi_gene_probes"] < d["acc_classes"].get("ambiguous", 0) else ("accession route" if m["multi_gene_probes"] > d["acc_classes"].get("ambiguous", 0) else "neither"),
            "The two ambiguity definitions differ (package multi-mapping vs union of accession matches) and are not the same probes.",
            "supportive")
        add("C09", "Unresolved probes (no eligible assignment; denominator: all probes)",
            f"{oa_un:,} ({pct(oa_un, n)}), incl. {m['no_gene_in_package']:,} with no package gene",
            f"{ac_un + d['acc_classes'].get('ambiguous', 0):,} ({pct(ac_un + d['acc_classes'].get('ambiguous', 0), n)}), incl. {ac_un:,} without a matched accession",
            "Option A" if oa_un < ac_un + d["acc_classes"].get("ambiguous", 0) else "accession route",
            "Includes control/non-gene probes in both routes; the share relevant to any cohort depends on Series Matrix content (not assessed).",
            "supportive")
        add("C10", "Probes assigned by only one route",
            f"Option A only: {c['optionA_eligible_accession_unresolved'] + c['optionA_eligible_accession_ambiguous_including_optionA_gene'] + c['optionA_eligible_accession_ambiguous_excluding_optionA_gene']:,} "
            f"(accession unresolved {c['optionA_eligible_accession_unresolved']:,}; accession ambiguous {c['optionA_eligible_accession_ambiguous_including_optionA_gene'] + c['optionA_eligible_accession_ambiguous_excluding_optionA_gene']:,})",
            f"accession only: {c['accession_unique_optionA_not_eligible']:,}",
            "Option A" if c["optionA_eligible_accession_unresolved"] > c["accession_unique_optionA_not_eligible"] else "accession route",
            "Single-route probes have no cross-check; their validity is the least supported.",
            "supportive")
        add("C11", "Probe-to-gene source, version, provenance and age",
            f"{label} package Entrez source date: {date[label]}; reconciled to org.Hs.eg.db 3.23.1 (Entrez Gene {org_date}) by the approved gene-history procedure",
            f"manufacturer accessions from the package matched to org.Hs.eg.db 3.23.1 (Entrez Gene {org_date})",
            "accession route" if label != "lumi HT-12 v4 R2" else "not determinable",
            "Option A's probe-to-gene knowledge predates the reference snapshot; the accession route's accessions are as old as the package build. Newer is not automatically more accurate.",
            "supportive", "reference/bioconductor_3.23 package metadata tables")
        add("C12", "Accession-matching limitations",
            "not applicable (Option A uses package gene assignments)",
            f"{m['accession_route_inputs']['accessions_with_version_suffix']:,} accession values carry a version; matching is on unversioned roots; "
            f"{m['accession_route_inputs']['probes_with_more_than_one_accession']:,} probes carry >1 accession",
            "not determinable",
            "An accession match shows the identifiers are linked in NCBI records, not that the probe sequence hybridizes to the current transcript.",
            "unresolved")
        add("C13", "Successor collisions (Option A; replaced probe joins a gene that already has directly mapped probes)",
            f"probes {a['collision_probes']:,}; distinct successor genes {a['collision_successor_genes']:,}; distinct historical source genes {a['collision_source_genes']:,}",
            "not applicable (no history step)", "not determinable",
            "Successor genes and historical source genes are different counts. Collisions are flagged, never merged; under G3 the replaced probes would join the successor gene's average.",
            "unresolved", "illumina_option_a/v1; v3/comparison_manifest.json")
        add("C14", "Downstream consequences for gene-level (G3) aggregation",
            "probes per gene and collisions determine each gene's average; replacement-derived probes enter successor genes",
            "ambiguous probes are lost; single-gene accession probes define the gene averages",
            "not determinable",
            "Effects on expression estimates require cohort data (probe presence, D17 rule, probe concordance) and are not assessed here.",
            "unresolved", "v5 §7.2–7.3 (rules); this matrix")
        add("C15", "Presence of probes in the cohort's Series Matrix", "NOT ASSESSED", "NOT ASSESSED", "not determinable",
            "Requires the cohort's authorized Series Matrix probe list; no GEO data used. Platform-wide counts are not cohort coverage."
            + (" GSE140829 applicability of the HT-12 v4 R2 table is restricted by D19." if label.startswith("lumi") else ""),
            "unresolved", "not assessed")
    return rows


def render(rows: list[dict], data: dict, checks: list, meta: dict, version: str) -> str:
    L = [f"# Illumina annotation-route decision matrix — {version}", "",
         "**Assessment only. No Illumina mapping policy is selected, recommended or approved.** No weighting or ranking "
         "is applied; each criterion is judged on its own. GSE140829 remains governed by D19; D17 is unresolved.", "",
         "## Definitions", "",
         "- **Option A:** package Entrez IDs reconciled to org.Hs.eg.db 3.23.1 by the approved gene-history procedure "
         "(cutoff 20260318); approved for GPL570 only (D6-F), provisional here.",
         "- **Accession route:** probe accessions matched (unversioned) to org.Hs.eg.db 3.23.1 accessions/RefSeq; only a "
         "unique match is an assignment.",
         "- **M1:** same-probe agreement against the post-gene-history Option A gene. **M2:** agreement against the package's "
         "original Entrez ID. M1 ⊆ M2; their totals are different metrics.",
         "- **Denominators:** probe-level percentages use all probes of the platform table (lumi: HT-12 v4 R2 manifest rows); "
         "gene-level counts are distinct current Entrez IDs. Historical source genes and successor genes are counted separately.",
         "- **Status:** *decisive* = settles the choice on its own (none qualify on current evidence); *supportive* = informs "
         "but does not settle; *unresolved* = cannot be judged from retained evidence.", ""]
    for label, d in data.items():
        sub = [r for r in rows if r["platform"] == label]
        L += [f"## {label} ({d['cohort']})", "", "| ID | Criterion | Option A | Accession route | Advantage (this criterion only) | Status |",
              "|---|---|---|---|---|---|"]
        L += [f"| {r['criterion_id']} | {r['criterion']} | {r['option_a_evidence']} | {r['accession_route_evidence']} | "
              f"{r['advantage']} | {r['status']} |" for r in sub]
        L += ["", "Limitations:", ""] + [f"- {r['criterion_id']}: {r['limitation']}" for r in sub] + [""]
    L += ["## Conclusions", "",
          "**Established by the retained evidence**", "",
          "- On probes both routes assign, they agree for 99.88–99.97% (M1), separately on each platform.",
          "- Option A assigns more probes and genes than the accession route on every platform; the gap is small for "
          "illuminaHumanv3/v4 and large for the lumi HT-12 v4 R2 table.",
          "- Most M2 disagreements on lumi are resolved by gene-history replacement; the remaining genuine disagreements "
          "are the M1 discordant probes listed in v3/metric_reconciliation_probes.tsv.", "",
          "**Suggested but not established**", "",
          "- That Option A's extra coverage reflects valid probe-to-gene relationships (it rests on older package "
          "assignments and, for lumi, on many replacements and collisions).",
          "- That the accession route is more current in a biologically meaningful way (unversioned accession matches do "
          "not confirm the probe targets the current transcript).", "",
          "**Unknown**", "",
          "- Which route is correct for each discordant or single-route probe.",
          "- Cohort-specific coverage (probe presence in each Series Matrix), the D17 feature rule, and the effect of "
          "either route on gene-level estimates.",
          "- Whether the lumi HT-12 v4 R2 table applies to GSE140829 (D19).", "",
          "**Evidence required before a policy decision**", "",
          "- Probe presence in each cohort's authorized Series Matrix (GSE63060, GSE63061; GSE140829 after D19).",
          "- The D17 feature-rule decision.",
          "- A decision on how discordant and single-route probes are treated, and whether sequence-level evidence "
          "(e.g. the packages' re-annotation fields) should be considered.", "",
          "## Not yet assessed / unresolved", "",
          "- Probe presence in cohort inputs (no GEO data used); D17; the Illumina mapping policy; D19 (GSE140829); any "
          "biological validation beyond annotation agreement.", "",
          "## Validation", ""] + [f"- [{'OK' if ok else 'FAILED'}] {n}" for n, ok in checks] + [""]
    L += ["## Package source dates (read from retained package databases)", ""] + \
         [f"- {k}: " + "; ".join(f"{a}={b or 'blank'}" for a, b in v.items()) for k, v in meta.items()]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--out-dir", type=Path, default=None, help="override output directory (reproduction checks)")
    args = ap.parse_args()
    out = args.out_dir or ROOT / "reports/annotation_audit/illumina_route_decision_matrix" / args.version
    if out.exists():
        raise SystemExit(f"{out} already exists; inspect it — nothing replaced")
    ver = verify()

    def run():
        meta = package_metadata()
        data, checks = recompute(ver["v3_manifest"])
        rows = build_matrix(data, meta)
        checks = checks + [
            ("every platform has every criterion", Counter(r["platform"] for r in rows) == Counter({p: 15 for p in data})),
            ("statuses and advantages use the allowed vocabularies",
             all(r["status"] in STATUSES and r["advantage"] in ADVANTAGES for r in rows)),
            ("no criterion is marked decisive without justification", not any(r["status"] == "decisive" for r in rows)),
        ]
        return {"DECISION_MATRIX.md": render(rows, data, checks, meta, args.version),
                "decision_matrix.tsv": tsv(rows, COLUMNS)}, checks, meta

    f1, c1, meta = run()
    f2, _, _ = run()
    h1 = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f1.items()}
    det = {"runs_compared": 2, "identical": h1 == {k: hashlib.sha256(v.encode()).hexdigest() for k, v in f2.items()}, "output_sha256": h1}
    status = "OK" if all(ok for _, ok in c1) else "FAILED"
    if status != "OK" or not det["identical"]:
        raise SystemExit(json.dumps({"checks": [(n, ok) for n, ok in c1], "determinism": det}, indent=2) + "\nFAILED (nothing written)")
    out.mkdir(parents=True)
    for k, v in f1.items():
        (out / k).write_text(v, encoding="utf-8")
    manifest = {"status": "Assessment only; no Illumina mapping policy selected or approved; D17 and D19 unchanged",
                "inputs_sha256": ver["inputs_sha256"], "package_metadata": meta,
                "definitions": {"option_a": "package Entrez IDs + approved gene-history procedure (cutoff 20260318)",
                                "accession_route": "unversioned accession match to org.Hs.eg.db 3.23.1; unique match only",
                                "M1": "same-probe agreement vs post-gene-history Option A gene",
                                "M2": "agreement vs package's original Entrez ID", "probe_denominator": "all probes of the platform table",
                                "gene_counts": "distinct current Entrez IDs; successor and historical source genes counted separately",
                                "statuses": list(STATUSES), "advantages": list(ADVANTAGES), "weighting": "none"},
                "validation": {"status": status, "checks": [{"check": n, "status": "OK" if ok else "FAILED"} for n, ok in c1]},
                "determinism": det, "command": "python scripts/annotation_illumina_route_decision_matrix.py --version " + args.version}
    (out / "decision_matrix_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"written: {out}; validation {status}; determinism identical")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
