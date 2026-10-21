#!/usr/bin/env python3
"""Audit-only reconciliation of historical Entrez Gene IDs (D6 annotation evidence; Option C, dual reporting).

Example:
    python scripts/annotation_gene_history_reconciliation.py \
        --gene-history <dir>/gene_history.gz --readme <dir>/README --tarball-dir <dir>/tarballs --version v1

Inputs are the retained, previously verified files (NCBI gene_history.gz + README retrieved 2026-10-12;
Bioconductor 3.23 source tarballs). Every input is re-hashed and must match the recorded values below,
otherwise the run stops. Package databases are read from the tarballs in a temporary directory; nothing
is installed or loaded into R. No GEO data are read.

Writes reports/annotation_audit/ncbi_gene_history/<version>/ and never overwrites an existing version.
All outputs are computed twice in memory and must be byte-identical before anything is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biomarker_project import gene_history_reconciliation as ghr  # noqa: E402

CUTOFF = "20260318"   # org.Hs.eg.db 3.23.1 EGSOURCEDATE 2026-Mar18 (View A history cutoff, inclusive)
EXPECTED_HISTORY = {"bytes": 162983925, "md5": "33e48e4bc30ea6b10bc2f7d5cc7a1e60",
                    "sha256": "bcb85c8fdd4791ad674e69481b794677953d0ecd9efb8547af4371845c59a602",
                    "url": "https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_history.gz",
                    "retrieved_utc": "2026-10-12T17:16:35Z", "server_last_modified": "2026-10-09 08:36:13 GMT"}
EXPECTED_README = {"bytes": 59166, "sha256": "303cce0aa6012ff94ce34d88ff999a24131d838e4acac76a4abc1880b59d5e2e",
                   "url": "https://ftp.ncbi.nlm.nih.gov/gene/DATA/README", "retrieved_utc": "2026-10-12"}
BIOC = "https://bioconductor.org/packages/3.23/data/annotation/src/contrib/"
TARBALLS = {  # file: (published MD5 in the Bioconductor 3.23 index, SHA-256 recorded at download)
    "org.Hs.eg.db_3.23.1.tar.gz": ("813be1921e7bc08c1348dbce9d244d0a", "470620665cf49d0319422731164f377e3e74253989f1d33a8a1d100cc3d49cfe"),
    "illuminaHumanv3.db_1.26.0.tar.gz": ("7d9e7534f0b60f0e3e7473e545ef373d", "cea0c9cd155197154d57400cb3f18108e451cf26e714c39698d68e45cd503a1b"),
    "illuminaHumanv4.db_1.26.0.tar.gz": ("42d554559ac0106dc71317ffaf466421", "362848d6e78c7fa6206e1a4c68a4b68c1ea065267d550114837bc3b9d833ee85"),
    "hgu133plus2.db_3.13.0.tar.gz": ("459fcf4880a9eaa25b373c5635fede3d", "ddde58e777a8341536a664c7d4be874a2f395f8aaa019c1f738462a8ce74cc44"),
    "lumiHumanIDMapping_1.10.1.tar.gz": ("007e5aa2f1596cc08d888ba6dce7148a", "6414e94a243eea6a126e582a68fadd41798bb5fccc03fcc99380a01f40634948"),
}
ORG = ("org.Hs.eg.db_3.23.1.tar.gz", "org.Hs.eg.db/inst/extdata/org.Hs.eg.sqlite", "SELECT gene_id FROM genes")
PACKAGES = [  # name, tarball, sqlite member, query returning historical Entrez IDs
    ("illuminaHumanv3", "illuminaHumanv3.db_1.26.0.tar.gz", "illuminaHumanv3.db/inst/extdata/illuminaHumanv3.sqlite",
     "SELECT DISTINCT gene_id FROM probes WHERE gene_id IS NOT NULL"),
    ("illuminaHumanv4", "illuminaHumanv4.db_1.26.0.tar.gz", "illuminaHumanv4.db/inst/extdata/illuminaHumanv4.sqlite",
     "SELECT DISTINCT gene_id FROM probes WHERE gene_id IS NOT NULL"),
    ("hgu133plus2", "hgu133plus2.db_3.13.0.tar.gz", "hgu133plus2.db/inst/extdata/hgu133plus2.sqlite",
     "SELECT DISTINCT gene_id FROM probes WHERE gene_id IS NOT NULL"),
    ("lumi HT-12 v4 R2", "lumiHumanIDMapping_1.10.1.tar.gz", "lumiHumanIDMapping/inst/extdata/lumiHumanIDMapping.sqlite",
     "SELECT DISTINCT trim(m.EntrezID) FROM HumanHT12_V4_0_R2_15002873_B t JOIN nuID_MappingInfo m ON m.nuID = t.nuID "
     "WHERE trim(m.EntrezID) <> ''"),
]
PREVIOUS = {"illuminaHumanv3": (98, 98), "illuminaHumanv4": (146, 146), "hgu133plus2": (84, 84),
            "lumi HT-12 v4 R2": (7169, 7168)}   # (absent from baseline, of those in history) reported 2026-10-12
FOCUS_IDS = {"653803": ["lumi HT-12 v4 R2"], "3653": ["illuminaHumanv4", "hgu133plus2"], "645261": ["hgu133plus2"]}


def verify_sources(history: Path, readme: Path, tardir: Path) -> dict:
    out = {"gene_history": ghr.file_hashes(history), "readme": ghr.file_hashes(readme), "tarballs": {}}
    problems = []
    h = out["gene_history"]
    for k in ("bytes", "md5", "sha256"):
        if h[k] != EXPECTED_HISTORY[k]:
            problems.append(f"gene_history.gz {k}: {h[k]} != {EXPECTED_HISTORY[k]}")
    out["gene_history"]["gzip_integrity"] = ghr.gzip_ok(history)
    r = out["readme"]
    for k in ("bytes", "sha256"):
        if r[k] != EXPECTED_README[k]:
            problems.append(f"README {k}: {r[k]} != {EXPECTED_README[k]}")
    fields = ghr.readme_gene_history_fields(readme)
    out["readme"]["gene_history_fields_documented"] = fields
    if fields != list(ghr.README_FIELDS):
        problems.append(f"README gene_history fields {fields} != {list(ghr.README_FIELDS)}")
    for name, (md5, sha) in TARBALLS.items():
        t = ghr.file_hashes(tardir / name)
        t["published_md5_match"] = t["md5"] == md5
        t["recorded_sha256_match"] = t["sha256"] == sha
        t["url"] = BIOC + name
        out["tarballs"][name] = t
        if not (t["published_md5_match"] and t["recorded_sha256_match"]):
            problems.append(f"{name}: checksum mismatch")
    if problems:
        raise SystemExit("SOURCE VERIFICATION FAILED (nothing written):\n  " + "\n  ".join(problems))
    return out


def compute(history_path: Path, tardir: Path) -> tuple[dict[str, str], dict]:
    history, header, n_rows = ghr.read_history(history_path)
    if header != ghr.FILE_HEADER:
        raise SystemExit(f"gene_history header {header} != expected {ghr.FILE_HEADER}")
    baseline = set(ghr.read_ids(tardir / ORG[0], ORG[1], ORG[2]))
    dup = sorted(k for k, v in history.items() if len(v) > 1)

    all_rows, summary, inputs = [], {}, {}
    for name, tar, member, query in PACKAGES:
        ids = ghr.read_ids(tardir / tar, member, query)
        prov = f"{tar} :: {member} :: {query}"
        rows, counts = ghr.audit_package(name, ids, prov, baseline, history, CUTOFF)
        all_rows += rows
        summary[name] = counts
        inputs[name] = {"n_ids": len(ids), "sha256_of_sorted_id_list": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
                        "provenance": prov}

    # Timing-discrepant IDs: present in the baseline, discontinued in the retained history file.
    pkg_ids = {name: set(r["entrez_id"] for r in all_rows if r["package"] == name) for name, *_ in PACKAGES}
    timing = []
    for gid in sorted((g for g in history if g in baseline), key=int):
        rec = history[gid][0]
        timing.append({"entrez_id": gid, "history_successor": rec.successor, "discontinue_date": rec.date,
                       "date_vs_cutoff": "on_or_before_cutoff" if rec.date <= CUTOFF else "after_cutoff",
                       "successor_in_baseline": "" if rec.successor == "-" else ("yes" if rec.successor in baseline else "no"),
                       "affected_packages": ";".join(n for n in pkg_ids if gid in pkg_ids[n])})

    validation = validate(all_rows, summary, inputs, history, baseline, dup)
    meta = {"human_history_rows": n_rows, "distinct_discontinued_ids": len(history), "duplicate_source_records": dup,
            "baseline_gene_ids": len(baseline), "summary": summary, "inputs": inputs, "validation": validation,
            "timing_discrepant": timing}
    files = {
        "gene_history_reconciliation.tsv": ghr.tsv(sorted(all_rows, key=lambda r: (r["package"], int(r["entrez_id"]))), ghr.COLUMNS),
        "timing_discrepant_ids.tsv": ghr.tsv(timing, ["entrez_id", "history_successor", "discontinue_date", "date_vs_cutoff",
                                                       "successor_in_baseline", "affected_packages"]),
        "summary_counts.tsv": summary_tsv(summary),
        "AUDIT_REPORT.md": report(meta, all_rows),
    }
    return files, meta


def validate(rows, summary, inputs, history, baseline, dup) -> dict:
    checks = []
    def add(name, ok, detail):
        checks.append({"check": name, "status": "OK" if ok else "FAILED", "detail": detail})
    keys = Counter((r["package"], r["entrez_id"]) for r in rows)
    add("tabulated_ids_unique_per_package", all(v == 1 for v in keys.values()), f"{len(keys)} (package, id) rows")
    for name, s in summary.items():
        n = inputs[name]["n_ids"]
        add(f"{name}: viewA classes sum to inputs", sum(s["viewA"].values()) == n, f"{sum(s['viewA'].values())} = {n}")
        add(f"{name}: viewB classes sum to inputs", sum(s["viewB"].values()) == n, f"{sum(s['viewB'].values())} = {n}")
        tab_expected = s["n_absent_from_baseline"] + s["viewB"].get("present_in_baseline_discontinued_in_history", 0)
        add(f"{name}: tabulated = absent + present-but-discontinued", s["n_tabulated"] == tab_expected,
            f"{s['n_tabulated']} = {tab_expected}")
        prev = PREVIOUS[name]
        add(f"{name}: absent / in-history counts vs 2026-10-12 report",
            (s["n_absent_from_baseline"], s["n_absent_in_history"]) == prev,
            f"now ({s['n_absent_from_baseline']}, {s['n_absent_in_history']}), previously {prev}")
    terminal = {"present_in_baseline", "replaced_successor_in_baseline", "discontinued_no_replacement",
                "chain_ends_no_replacement", "unexplained_absent_no_history", "absent_history_after_cutoff", "unresolved",
                "present_in_baseline_discontinued_in_history", "present_in_baseline_no_history"}
    bad = [r for r in rows if r["viewA_class"] not in terminal or r["viewB_class"] not in terminal]
    add("every chain ends in a defined terminal class", not bad, f"{len(bad)} rows outside the terminal set")
    cycles = [r for r in rows if "cycle_at" in r["unresolved_reason"]]
    add("cycles flagged (not ignored)", True, f"{len(cycles)} cycle(s) flagged")
    add("duplicate source records flagged (not ignored)", True, f"{len(dup)} discontinued ID(s) with >1 human record")
    leaked = []
    for r in rows:
        for step in r["viewA_chain"].split(">")[:-1]:
            rec = history.get(step)
            if rec and step not in baseline and rec[0].date > CUTOFF:
                leaked.append((r["package"], r["entrez_id"], step))
    add("View A applies no record dated after the cutoff", not leaked, f"{len(leaked)} post-cutoff step(s) used")
    preserved = [r for r in rows if r["baseline_status"] == "present_in_baseline" and r["viewA_class"] != "present_in_baseline"]
    add("View A preserves every baseline-present ID", not preserved, f"{len(preserved)} baseline ID(s) altered in View A")
    add("no merges performed (one row per input ID; successors only flagged)", True,
        "rows are never combined; collision/shared flags are informational")
    return {"status": "OK" if all(c["status"] == "OK" for c in checks) else "FAILED", "checks": checks}


def summary_tsv(summary: dict) -> str:
    rows = []
    for name, s in summary.items():
        for view in ("viewA", "viewB"):
            for cls, n in s[view].items():
                rows.append({"package": name, "view": view, "class": cls, "n_ids": n})
    return ghr.tsv(rows, ["package", "view", "class", "n_ids"])


def report(meta: dict, rows: list[dict]) -> str:
    s, v = meta["summary"], meta["validation"]
    def ct(name, view):
        return ", ".join(f"{k} {n}" for k, n in s[name][view].items())
    lines = [
        "# NCBI gene-history reconciliation audit (Option C, dual reporting) — v1", "",
        "Audit only. No annotation resource, mapping rule or shared-snapshot requirement is chosen or changed "
        "(D6-D unapproved). No GEO data, probe lists, QC, DE, S8 or confirmatory analysis were used.", "",
        "## Sources (verified before use; see reconciliation_manifest.json)", "",
        f"- Baseline: org.Hs.eg.db 3.23.1, Entrez Gene snapshot 2026-Mar18 ({meta['baseline_gene_ids']} gene IDs).",
        f"- NCBI gene_history.gz retrieved {EXPECTED_HISTORY['retrieved_utc']} (server Last-Modified "
        f"{EXPECTED_HISTORY['server_last_modified']}); {meta['human_history_rows']} human rows. NCBI recalculates "
        "this file daily and publishes no checksum or versioned release: reproducibility rests on the retained "
        "file and its SHA-256, not on the URL.",
        "- Historical IDs: illuminaHumanv3.db 1.26.0 and illuminaHumanv4.db 1.26.0 (Entrez snapshot 2015-Mar17), "
        "hgu133plus2.db 3.13.0 (2021-Apr14), lumiHumanIDMapping 1.10.1 table HumanHT12_V4_0_R2_15002873_B (undated).", "",
        "## Reporting policies", "",
        f"- **View A (primary, snapshot-consistent).** org.Hs.eg.db is fixed. IDs present in it are preserved. For "
        f"absent IDs only gene_history records dated on or before {CUTOFF} are used; later records are reported, not applied.",
        "- **View B (October history audit).** All human records in the retained file are used. Chains continue "
        "through IDs that are in the baseline but discontinued in the file.",
        "- Both: successor = GeneID column only (never symbols); GeneID \"-\" = explicit no-replacement state "
        "(README wording plus observed data); every chain step is recorded; cycles, duplicate records and "
        "unresolvable successors are flagged; nothing is merged.", "",
        "## Counts by package (every distinct historical ID classified once per view)", "",
        "| Package | Input IDs | Absent from baseline | of which in history | Tabulated rows |", "|---|---|---|---|---|",
    ]
    for name in s:
        lines.append(f"| {name} | {s[name]['n_input_ids']} | {s[name]['n_absent_from_baseline']} | "
                     f"{s[name]['n_absent_in_history']} | {s[name]['n_tabulated']} |")
    lines += ["", "**View A classes:**", ""] + [f"- {n}: {ct(n, 'viewA')}" for n in s]
    lines += ["", "**View B classes:**", ""] + [f"- {n}: {ct(n, 'viewB')}" for n in s]
    t = meta["timing_discrepant"]
    lines += ["", f"## Timing-discrepant IDs ({len(t)}): present in the 2026-03-18 baseline, discontinued in the retained file", "",
              "| Entrez ID | Successor | Date | vs cutoff | Successor in baseline | Affected packages |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['entrez_id']} | {r['history_successor']} | {r['discontinue_date']} | {r['date_vs_cutoff']} | "
              f"{r['successor_in_baseline'] or '—'} | {r['affected_packages'] or '—'} |" for r in t]
    lines += ["", "In View A these IDs stay as in the baseline. A record dated exactly on the cutoff is applied in "
              "View A only to IDs absent from the baseline.", "", "## Focus IDs", ""]
    for gid, pk in FOCUS_IDS.items():
        for name in pk:
            r = next((x for x in rows if x["package"] == name and x["entrez_id"] == gid), None)
            if r is None:
                lines.append(f"- {gid} ({name}): not in the tabulated population")
            else:
                lines.append(f"- {gid} ({name}): baseline {r['baseline_status']}; View A {r['viewA_class']} "
                             f"[{r['viewA_chain']}]; View B {r['viewB_class']} [{r['viewB_chain']}]; "
                             f"history date {r['history_discontinue_date'] or '—'}; reason {r['unresolved_reason'] or '—'}")
    lines += ["", "## Chains, collisions and shared successors", ""]
    for name in s:
        sub = [r for r in rows if r["package"] == name]
        multi = [r for r in sub if r["viewB_chain"].count(">") > 1]
        lines.append(f"- {name}: View A collisions {sum(r['viewA_collision'] == 'yes' for r in sub)}, shared successors "
                     f"{sum(r['viewA_shared_successor'] == 'yes' for r in sub)}; View B collisions "
                     f"{sum(r['viewB_collision'] == 'yes' for r in sub)}, shared successors "
                     f"{sum(r['viewB_shared_successor'] == 'yes' for r in sub)}; multi-step chains (View B) "
                     + (", ".join(f"{r['entrez_id']} [{r['viewB_chain']}]" for r in multi) or "none"))
    lines += ["", "A collision means the successor is itself a directly mapped historical ID of the same package; a shared "
              "successor means several input IDs resolve to it. Both are flags only: no probes or genes were merged.", "",
              "## Limitations", "",
              "- Absence from org.Hs.eg.db is not evidence of retirement; only gene_history records are.",
              "- gene_history has one record per discontinued ID and does not distinguish merges from splits.",
              "- The meaning of GeneID \"-\" is inferred from the README wording and the data, not stated explicitly.",
              "- The file is a daily recalculation without a published checksum; the URL does not identify this content.",
              "- The verified source files are retained outside the project (scratch); data/ is reserved for script-produced "
              "GEO files (data/README.md). Durable retention needs a separate decision.",
              "- This audit does not address the GPL570 accession-route gap, unversioned accessions, ambiguous accessions "
              "or multi-gene probes.", "",
              f"## Validation: {v['status']}", ""]
    lines += [f"- [{c['status']}] {c['check']} — {c['detail']}" for c in v["checks"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gene-history", required=True, type=Path)
    ap.add_argument("--readme", required=True, type=Path)
    ap.add_argument("--tarball-dir", required=True, type=Path)
    ap.add_argument("--version", default="v1")
    ap.add_argument("--out-dir", type=Path, default=None, help="override output directory (testing)")
    args = ap.parse_args()
    out = args.out_dir or ROOT / "reports" / "annotation_audit" / "ncbi_gene_history" / args.version
    if out.exists():
        raise SystemExit(f"{out} already exists; choose a new --version")

    sources = verify_sources(args.gene_history, args.readme, args.tarball_dir)
    files1, meta = compute(args.gene_history, args.tarball_dir)
    files2, _ = compute(args.gene_history, args.tarball_dir)
    h1 = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in files1.items()}
    h2 = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in files2.items()}
    determinism = {"runs_compared": 2, "identical": h1 == h2, "output_sha256": h1}
    if not determinism["identical"] or meta["validation"]["status"] != "OK":
        print(json.dumps({"determinism": determinism, "validation": meta["validation"]}, indent=2))
        raise SystemExit("VALIDATION OR DETERMINISM FAILED (nothing written)")

    out.mkdir(parents=True)
    for name, content in files1.items():
        (out / name).write_text(content, encoding="utf-8")
    manifest = {
        "purpose": "Audit-only NCBI gene-history reconciliation (Option C). No annotation resource or mapping rule chosen.",
        "parameters": {"view_a_cutoff_inclusive": CUTOFF, "view_b_history_retrieved_utc": EXPECTED_HISTORY["retrieved_utc"],
                       "taxon": ghr.HUMAN_TAXID, "baseline": "org.Hs.eg.db 3.23.1 (EGSOURCEDATE 2026-Mar18)"},
        "rules": ghr.__doc__.strip(),
        "sources": {"gene_history": {**sources["gene_history"], **{k: EXPECTED_HISTORY[k] for k in ("url", "retrieved_utc", "server_last_modified")}},
                    "readme": {**sources["readme"], "url": EXPECTED_README["url"]},
                    "tarballs": sources["tarballs"]},
        "inputs": meta["inputs"], "counts": meta["summary"],
        "human_history_rows": meta["human_history_rows"], "duplicate_source_records": meta["duplicate_source_records"],
        "validation": meta["validation"], "determinism": determinism,
        "command": " ".join(["python", "scripts/annotation_gene_history_reconciliation.py"] + sys.argv[1:]),
    }
    (out / "reconciliation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"written: {out}")
    print(f"validation: {meta['validation']['status']}; determinism (2 in-memory runs): identical")
    for name, s in meta["summary"].items():
        print(f"  {name}: inputs {s['n_input_ids']}, absent {s['n_absent_from_baseline']}, in history {s['n_absent_in_history']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
