#!/usr/bin/env python3
"""Tier B step 11: signature lock for the GSE63060 discovery (SAP v7 §7; selection v6 §7.1 with D15).

Selection (D15, approved 2026-10-18; v6 §7.1): gene-level q < 0.05 from the primary fit (reports/discovery/GSE63060/fit_v1);
ranked by q ascending, then |beta| descending, then |moderated t| descending, then Entrez ID ascending; cap 200 unique Entrez
genes; no coverage restriction at selection. Direction = sign(beta). Symbols from the pinned org.Hs.eg.db 3.23.1 archive.

The lock record contains every item of v7 §7 (1–7): the D6 option and freezing rule with the T_GSE63060 checksum; the annotation
resource and pin; the per-gene table; the counts; the validation and specificity specifications; the precedence rule and the
sensitivity definitions. Each specification is embedded as the EXACT approved SAP text (file, line range, SHA-256 of the
excerpt), with the SAP and v6 file hashes, so nothing is paraphrased. It also cites the SHA-256 of the identity record of every
output it contains and the D8 environment record hashes (v7:486). The lock is written before any validation or specificity
expression is modelled against diagnosis. Runs under the code-identity lifecycle; writes reports/lock/GSE63060/<version>/.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
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
import pandas as pd  # noqa: E402

from biomarker_project import code_identity as ci  # noqa: E402
from biomarker_project.gene_history_reconciliation import _sqlite_from_tar  # noqa: E402

ACC = "GSE63060"
OUT_REL = f"reports/lock/{ACC}"
FIT_REL, PREP_REL, SENS_REL = f"reports/discovery/{ACC}/fit_v1", f"reports/discovery/{ACC}/prep_v1", f"reports/discovery/{ACC}/sensitivity_v1"
PIN_REL = "reports/annotation_audit/annotation_pin/v1"
UPSTREAM = [PIN_REL, "reports/annotation_audit/illumina_a0/v2", f"reports/eligibility/{ACC}/v1", f"reports/duplicate_review/{ACC}/c1_v1",
            f"reports/qc_stage_a/{ACC}/v1", f"reports/qc_stage_b/{ACC}/v1", PREP_REL, FIT_REL]
V7 = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
V6 = "reports/phase3b/v6/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
ORG_TAR = "reference/bioconductor_3.23/org.Hs.eg.db_3.23.1.tar.gz"
ORG_MEMBER = "org.Hs.eg.db/inst/extdata/org.Hs.eg.sqlite"
Q, CAP = 0.05, 200
# v7 §7 items -> exact approved text (file, first line, last line); line numbers are those of the files hashed in the record
SECTIONS = {
    "1_D6_register_row": (V7, 609, 609), "1_freezing_rule_v7_3_2": (V7, 191, 205), "1_model_families_v7_3_3": (V7, 206, 248),
    "2_mapping_feature_presence_v6_8_2": (V6, 479, 489),
    "5_measurability_v6_8_3": (V6, 490, 499), "5_score_weighting_coverage_v6_8_4": (V6, 500, 523),
    "5_C-c_v6_8_5": (V6, 524, 543), "5_C-b_v6_8_7": (V6, 569, 574),
    "5_magnitude_v6_8_9": (V6, 582, 605), "5_covariates_v7_4_1": (V7, 251, 288), "5_claim_families_v7_4_2": (V7, 289, 300),
    "5_C-a_v7_4_4": (V7, 323, 335), "5_GSE63061_correlation_v7_4_5": (V7, 336, 344),
    "5_D12_register_row": (V7, 615, 615), "5_D20_register_row": (V7, 623, 623), "5_D15_register_row": (V7, 618, 618),
    "6_specificity_v6_9_1_to_9_6": (V6, 608, 655), "6_without_delta_v7_8_1_8_2": (V7, 492, 518), "6_D13_register_row": (V7, 616, 616),
    "7_precedence_and_sets_v7_5": (V7, 345, 415), "7_sensitivity_definitions_v6_10_1": (V6, 685, 714), "7_D16_register_row": (V7, 619, 619),
}
NOTES = {"7_sensitivity_definitions_v6_10_1": "v7 §0.1 maps v6 §10.1 as replaced by v7 §5; v7 §5 restates the general rules and "
                                                  "sample sets but not the S1–S16 designs, so this table is included as the only text naming them.",
         "5_C-a_v7_4_4": "v6 §8.6 (C-a) and v6 §8.8 (multiplicity) are replaced by v7 §4 (v7 §0.1) and are not included."}
APPROVAL_MARKERS = ("| D12 § | **APPROVED 2026-10-19", "| D13 † ‡ § | **APPROVED 2026-10-19", "| D20 † ‡ § | **APPROVED 2026-10-19",
                    "| D15 ‡ § | **APPROVED 2026-10-18", "| D16 † § | **APPROVED 2026-10-18")
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha(p: Path) -> str:
    return _sha_bytes(p.read_bytes())


def select(res: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    elig = res[res["q_value_bh"] < Q].copy()
    elig["entrez_int"] = elig["feature_id"].astype(int)
    elig["abs_beta"], elig["abs_t"] = elig["estimate"].abs(), elig["t_statistic"].abs()
    ranked = elig.sort_values(["q_value_bh", "abs_beta", "abs_t", "entrez_int"], ascending=[True, False, False, True], kind="mergesort")
    sig = ranked.head(CAP).copy()
    sig.insert(0, "lock_rank", range(1, len(sig) + 1))
    sig["direction"] = sig["estimate"].map(lambda b: "up_in_AD" if b > 0 else "down_in_AD")
    return sig.drop(columns=["entrez_int", "abs_beta", "abs_t"]), int(len(elig))


def symbols(root: Path, ids: list[str]) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_lock_") as tmp:
        db = _sqlite_from_tar(root / ORG_TAR, ORG_MEMBER, Path(tmp))
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        rows = con.execute("SELECT g.gene_id, i.symbol FROM genes g JOIN gene_info i ON g._id = i._id").fetchall()
        con.close()
    m = {str(g): s for g, s in rows}
    return {i: m.get(i, "") for i in ids}


def excerpts(root: Path) -> dict:
    out = {}
    for key, (rel, a, b) in SECTIONS.items():
        lines = (root / rel).read_text(encoding="utf-8").split("\n")
        text = "\n".join(lines[a - 1:b])
        out[key] = {"file": rel, "lines": f"{a}-{b}", "sha256": _sha_bytes(text.encode("utf-8")), "text": text}
        if key in NOTES:
            out[key]["note"] = NOTES[key]
    return out


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in UPSTREAM + [SENS_REL]:
        p = ci.acceptance_problems(ROOT / rel, "counts_manifest.json" if "gpl570" in rel else "manifest.json", require_executed_code=True)
        if p:
            probs.append(f"{rel} not accepted: {p}")
    v7 = (ROOT / V7).read_text(encoding="utf-8")
    missing = [m for m in APPROVAL_MARKERS if m not in v7]
    if missing:
        probs.append(f"approvals not found in the SAP: {missing}")
    pin = json.loads((ROOT / PIN_REL / "annotation_pin_record.json").read_text(encoding="utf-8"))
    if pin["archives"]["org.Hs.eg.db_3.23.1.tar.gz"]["sha256"] != _sha(ROOT / ORG_TAR):
        probs.append("org.Hs.eg.db archive differs from the pin")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    res = pd.read_csv(ROOT / FIT_REL / "gene_level_results.tsv", sep="\t", dtype={"feature_id": str})
    table = pd.read_csv(ROOT / PREP_REL / "selection_table_G3.tsv", sep="\t", dtype=str).set_index("entrez_gene_id")
    sig, n_eligible = select(res)
    sym = symbols(ROOT, list(sig["feature_id"]))
    sig.insert(2, "symbol", sig["feature_id"].map(sym))
    sig["constituent_probes"] = sig["feature_id"].map(table["constituent_probes"])
    sig["n_constituent_probes"] = sig["feature_id"].map(table["n_probes"])
    cols = ["lock_rank", "feature_id", "symbol", "direction", "estimate", "ci_low", "ci_high", "std_error", "t_statistic", "df",
            "p_value", "q_value_bh", "constituent_probes", "n_constituent_probes"]
    sig = sig[cols].rename(columns={"feature_id": "entrez_gene_id", "estimate": "beta_AD_minus_CTL"})
    sig_bytes = sig.to_csv(sep="\t", index=False, float_format="%.17g", lineterminator="\n").encode()
    again = select(res)[0]
    deterministic = list(again["feature_id"]) == list(sig["entrez_gene_id"]) and list(again["lock_rank"]) == list(sig["lock_rank"])
    ex = excerpts(ROOT)
    counts = {"eligible_genes_q_lt_0.05": n_eligible, "locked_genes": int(len(sig)), "locked_up_in_AD": int((sig["direction"] == "up_in_AD").sum()),
              "locked_down_in_AD": int((sig["direction"] == "down_in_AD").sum()),
              "low_gene_count_label": bool(len(sig) < 10), "symbols_missing": int((sig["symbol"] == "").sum())}
    ident = {rel: json.loads((ROOT / rel / ("counts_manifest.json" if "gpl570" in rel else "manifest.json")).read_text(encoding="utf-8"))["identity"]
             for rel in UPSTREAM}
    record = {
        "schema": "bio-mb-001/signature-lock/v1", "cohort": ACC,
        "status": "SIGNATURE LOCK (Tier B step 11). Written before any validation or specificity expression is modelled against "
                  "diagnosis. The same lock governs every cohort (v7 §7). The SAP remains a proposed draft (not approved, not frozen).",
        "item_1_gene_level_unit": {"D6_option": "G3 (mean of eligible probes; deposited scale)", "S8_alternative": "G1",
                                   "T_GSE63060": {"path": f"{PREP_REL}/selection_table_G3.tsv", "sha256": _sha(ROOT / PREP_REL / "selection_table_G3.tsv")}},
        "item_2_annotation": {"pin_record": f"{PIN_REL}/annotation_pin_record.json", "pin_record_sha256": _sha(ROOT / PIN_REL / "annotation_pin_record.json"),
                              "mapping": "D6-G A0 (GPL6947/GPL10558), D6-F Option A (GPL570); Entrez only; multi-mapped excluded",
                              "validation_feature_rule": "none (D17 Option A)", "GSE140829": "D19 unresolved: unmapped until resolved"},
        "item_3_signature_table": {"path": "signature.tsv", "sha256": _sha_bytes(sig_bytes),
                                   "selection_rule": "q < 0.05; q asc, |beta| desc, |t| desc, Entrez asc; cap 200; no coverage restriction (D15)"},
        "item_4_counts": counts,
        "items_5_6_7_specifications": {k: {kk: v[kk] for kk in ("file", "lines", "sha256", "note") if kk in v} for k, v in ex.items()},
        "approved_choices": {"D12": "C-c; C-a; C-b descriptive", "D20": "O1 + X1; W1; C-c one-sided with L_c; C-a q < 0.05; covariates locked",
                             "D13": "equivalence not used; no Q2; Holm across the three contrasts; same GPL570 coverage; GU descriptive; no replicated-genes-only",
                             "D15": "q < 0.05; cap 200; per-direction coverage 50% and min(5)", "D16": "S1–S16 (§5.3) + S-R8m"},
        "source_files_sha256": {V7: _sha(ROOT / V7), V6: _sha(ROOT / V6)},
        "identity_records_of_contained_outputs": {rel: {"record_sha256": i["record_sha256"], "aggregate_sha256": i["aggregate_sha256"]} for rel, i in ident.items()},
        "d8_environment_record_hashes": ident[FIT_REL]["environment_records"],
        "primary_fit_reference": {"gene_level_results_sha256": _sha(ROOT / FIT_REL / "gene_level_results.tsv")},
    }
    files = {"signature.tsv": sig_bytes,
             "lock_record.json": (json.dumps(record, indent=2, sort_keys=True) + "\n").encode(),
             "sap_excerpts.json": (json.dumps(ex, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()}
    checks = [("selection is deterministic (re-selected identically)", deterministic),
              ("200 genes locked (cap) from the 1,401 eligible", (counts["locked_genes"], n_eligible) == (min(CAP, n_eligible), n_eligible)),
              ("every locked gene has a symbol", counts["symbols_missing"] == 0),
              ("every locked gene has constituent probes in T_GSE63060", bool(sig["constituent_probes"].notna().all()))]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED:\n  " + "\n  ".join(failed))
    manifest = {"status": record["status"], "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/signature_lock_gse63060.py --version {version}",
                "counts": counts, "validation": [{"check": n, "pass": ok} for n, ok in checks]}
    return files, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    a = ap.parse_args(argv)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / a.version, lambda s: produce(a.version),
                                   require_venv=REQUIRE_VENV, executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
