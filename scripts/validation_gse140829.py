#!/usr/bin/env python3
"""Tier B steps 6–9 and 12 for GSE140829: replication test of the locked GSE63060 signature (SAP v7 §4; v6 §8).

Same locked specification and statistics as scripts/validation_gse63061.py (imported, not copied), with the GSE140829
decisions applied:
  population  approved GSE140829 exclusion list (v7:625, 2026-10-20): 201 AD vs 248 CTL; covariates age_at_draw (linear),
              Sex, batch (unit, fixed effect; D11 option (a), v7:614); identifiability M2–M4 with D7 c1 = 3, c2 = 5, c3 = 10.
  mapping     D19-1 (v7:622): nuID -> ILMN -> A0 (reports/annotation_audit/gse140829_nuid/v1); G3 = mean of the cohort's eligible
              present probes. Measurability category 1 (unmapped) is judged on the HT-12 v4 A0 universe; category 2 (no
              eligible probe in the Series Matrix) on GSE140829's own features.
  C-c, C-a, C-b  as locked (D20, D12); C-a summary and C-b without intervals (v7:68–69).
  §4.5        the effect correlation is prespecified for GSE63061 only and is not computed here.
Wording: GSE140829 is the replication cohort; a gene with q < 0.05 is "statistically replicated in GSE140829" (v6:553);
independence from AddNeuroMed participants is unverified (D10, v7:613), so "independent" is never used. Statistical
replication is not biological or clinical validation; magnitudes are not comparable across cohorts; no cross-cohort claim (X1).
Runs under the code-identity lifecycle with executed-code verification; writes reports/validation/GSE140829/<version>/.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
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
from biomarker_project.expression_adjudication import parse_series_matrix  # noqa: E402
from biomarker_project.limma_backend import check_environment, fit_feature_limma  # noqa: E402

ACC = "GSE140829"
OUT_REL = f"reports/validation/{ACC}"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
LOCK_REL = "reports/lock/GSE63060/v1"
NUID_REL = "reports/annotation_audit/gse140829_nuid/v1"
A0_REL = "reports/annotation_audit/illumina_a0/v2"
A0_PLATFORM_COHORT = "GSE63061"   # A0 rows classifying the full HT-12 v4 (GPL10558) probe universe
ELIG_REL, QCA_REL, QCB_REL = f"reports/eligibility/{ACC}/v1", f"reports/qc_stage_a/{ACC}/v1", f"reports/qc_stage_b/{ACC}/v1"
DUP_REL = f"reports/duplicate_review/{ACC}/c1_v1"
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
EXCLUSION_LIST_SHA256 = "d982afd4966cbaff077c1eb9910c289d0501ce60ff17af3981f64228185b93cd"
APPROVAL_MARKERS = ("GSE140829 exclusion-list approval §", EXCLUSION_LIST_SHA256, "GSE140829 C1 review §", "D19-1",
                    "O1 (separate within-cohort families) + X1", "C-c and C-a as specified; C-b descriptive only")
EXPECTED = {"AD": 201, "CTL": 248}
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


val = _load("scripts/validation_gse63061.py", "validation_gse63061")
_sha, _tsv, _json = val._sha, val._tsv, val._json


def measurability_universe(a0_platform: pd.DataFrame, nuid: pd.DataFrame) -> pd.DataFrame:
    """A0-shaped rows for GSE140829: every eligible HT-12 v4 probe (mapping), present iff it is a GSE140829 feature."""
    present = set(nuid["ilmn_probe_id"])
    e = a0_platform[a0_platform["a0_class"] == "eligible"][["probe_id", "a0_gene_id"]].copy()
    e["cohort"], e["a0_class"] = ACC, "eligible"
    e["in_series_matrix"] = e["probe_id"].map(lambda p: "yes" if p in present else "no")
    return e


def population(elig: pd.DataFrame, excluded: set[str], prep) -> pd.DataFrame:
    """The approved primary population, with the deposited batch as the unit (column name `chip` kept for the shared code)."""
    pop = prep.primary_population(elig, excluded)
    batch = elig.set_index("gsm")["batch"]
    pop["chip"] = "batch_" + pop["gsm"].map(batch).astype(str)
    return pop


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in (LOCK_REL, NUID_REL, ELIG_REL, DUP_REL, QCA_REL, QCB_REL):
        p = ci.acceptance_problems(ROOT / rel, "manifest.json", require_executed_code=True)
        if p:
            probs.append(f"{rel} not accepted: {p}")
    for rel, want in ((f"{LOCK_REL}/lock_record.json", val.LOCK_RECORD_SHA256), (f"{LOCK_REL}/signature.tsv", val.SIGNATURE_SHA256),
                      (f"{QCB_REL}/exclusion_list.tsv", EXCLUSION_LIST_SHA256)):
        if not (ROOT / rel).is_file() or _sha(ROOT / rel) != want:
            probs.append(f"{rel} differs from the locked/approved file")
    sap = (ROOT / SAP_REL).read_text(encoding="utf-8") if (ROOT / SAP_REL).is_file() else ""
    missing = [m for m in APPROVAL_MARKERS if m not in sap]
    if missing:
        probs.append(f"approvals not found in the SAP: {missing}")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    raw_man = json.loads((ROOT / f"data/raw/{ACC}/download_manifest.json").read_text(encoding="utf-8"))
    sm_sha = _sha(ROOT / SM_REL)
    if sm_sha != raw_man["files"][Path(SM_REL).name]["current"]["sha256"]:
        raise SystemExit("STOP: Series Matrix SHA-256 differs from the download manifest")
    env = check_environment()
    prep = _load("scripts/discovery_prep_gse63060.py", "discovery_prep")
    fit = _load("scripts/discovery_fit_gse63060.py", "discovery_fit")
    elig = pd.read_csv(ROOT / ELIG_REL / "eligibility_log.tsv", sep="\t", dtype=str, keep_default_na=False)
    excluded = set(pd.read_csv(ROOT / QCB_REL / "exclusion_list.tsv", sep="\t", dtype=str)["gsm"])
    a2 = pd.read_csv(ROOT / QCA_REL / "qc_a2_pairs.tsv", sep="\t", dtype=str)
    audit = pd.read_csv(ROOT / QCA_REL / "qc_audit.tsv", sep="\t", dtype=str, keep_default_na=False)
    nuid = pd.read_csv(ROOT / NUID_REL / "nuid_a0_classification.tsv", sep="\t", dtype=str, keep_default_na=False)
    a0 = pd.read_csv(ROOT / A0_REL / "a0_probe_classification.tsv", sep="\t", dtype=str, keep_default_na=False)
    a0_platform = a0[a0["cohort"] == A0_PLATFORM_COHORT]
    signature = pd.read_csv(ROOT / LOCK_REL / "signature.tsv", sep="\t", dtype={"entrez_gene_id": str})
    values, _ = parse_series_matrix(ROOT / SM_REL)
    values.columns = [str(c) for c in values.columns]

    def compute():
        pop = population(elig, excluded, prep)
        ident = prep.identifiability(pop)
        c2log = {"tier_b_step": 6, "a2_pairs": int(len(a2)), "r9_referred_d18": int((audit["r9_outcome"] == "referred_d18").sum())}
        c2log["status"] = "complete: no C2 candidates" if c2log["a2_pairs"] == 0 and c2log["r9_referred_d18"] == 0 else "C2 candidates: review required"
        table = val.selection_table(nuid, ACC)                     # probe_id = nuID (the Series Matrix feature key)
        genes = fit.gene_matrix(values[list(pop["gsm"])].astype(float), table)
        meas = val.measurability(signature, measurability_universe(a0_platform, nuid), ACC, genes)
        cov = val.coverage(meas)
        files = {"c2_duplicate_review_log.json": _json(c2log), "primary_population_log.tsv": _tsv(pop),
                 "identifiability_checks.json": _json(ident), "selection_table_G3.tsv": _tsv(table),
                 "measurability.tsv": _tsv(meas), "coverage.json": _json(cov)}
        result = {"cohort": ACC, "role": "replication cohort; independence from AddNeuroMed participants unverified (D10)",
                  "identifiability_decision": ident["decision"], "score_assessable": cov["score_assessable"],
                  "effect_correlation": "not computed: v7 §4.5 is prespecified for GSE63061 only"}
        if ident["decision"] != "PROCEED" or not c2log["status"].startswith("complete"):
            result["C-c"] = result["C-a"] = "not assessable (v7 §4.1 rule 4 / C2 incomplete)"
            files["validation_summary.json"] = _json(result)
            return files, pop, ident
        design = fit.full_rank_design(pop, prep.nuisance_matrix, ident["descriptive"]["r_N"])
        nonconst = genes[genes.std(axis=1, ddof=1) > 0]
        g = fit_feature_limma(nonconst.to_numpy(), list(nonconst.index), list(nonconst.columns), design)
        g.results["data_origin"] = "GEO"
        ca = val.c_a(g.results, meas).rename(columns={"beta_GSE63061": f"beta_{ACC}", "consistent_q_lt_0.05": "replicated_q_lt_0.05"})
        files["gene_level_results.tsv"] = _tsv(g.results)
        files["c_a_per_gene.tsv"] = _tsv(ca)
        k = int(ca["replicated_q_lt_0.05"].sum())
        result["C-a"] = {"family": f"measurable locked genes in {ACC}", "n": int(len(ca)), "n_replicated_q_lt_0.05": k,
                         "proportion_replicated": k / len(ca) if len(ca) else None,
                         "summary_note": "descriptive; no interval (a binomial interval assumes independent genes; v7:69)"}
        result["C-b"] = val.c_b(ca, meas, cov)
        if cov["score_assessable"]:
            score = val.w1_score(genes, meas)
            files["score_W1.tsv"] = _tsv(pd.DataFrame({"gsm": score.index, "group": list(pop["group"]), "S": score.to_numpy()}))
            result["C-c"] = val.c_c(score, design)
        else:
            result["C-c"] = "not assessable (coverage rule, v6 §8.4)"
        result["wording"] = ("statistical replication of deposited-label associations, not biological or clinical validation; "
                             "independence unverified (D10); magnitudes not comparable across cohorts; no cross-cohort claim (X1)")
        files["validation_summary.json"] = _json(result)
        files["limma_session_info.txt"] = ("\n".join(g.session_info) + "\n").encode()
        return files, pop, ident

    f1, pop, ident = compute()
    if f1 != compute()[0]:
        raise SystemExit("STOP: two runs are not byte-identical")
    checks = [("primary population is 201 AD + 248 CTL (approved list)",
               (int((pop.group == "AD").sum()), int((pop.group == "CTL").sum())) == (EXPECTED["AD"], EXPECTED["CTL"])),
              ("complete covariates (R2-COV) for every primary array", bool(pop[["age", "sex_male"]].notna().all().all())),
              ("unit is the deposited batch", bool(pop["chip"].str.startswith("batch_").all())),
              ("signature has 200 locked genes", len(signature) == 200)]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED:\n  " + "\n  ".join(failed))
    manifest = {"status": f"Tier B steps 6–9 and 12 for {ACC}: replication test of the locked GSE63060 signature. "
                          "The SAP remains a proposed draft (not approved, not frozen).",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/validation_gse140829.py --version {version}",
                "inputs": {rel: _sha(ROOT / rel / "manifest.json") for rel in (LOCK_REL, NUID_REL, ELIG_REL, DUP_REL, QCA_REL, QCB_REL)}
                | {SM_REL: sm_sha, "exclusion_list_sha256": EXCLUSION_LIST_SHA256, "sap_sha256": _sha(ROOT / SAP_REL),
                   "a0_probe_classification_sha256": _sha(ROOT / A0_REL / "a0_probe_classification.tsv")},
                "identifiability_decision": ident["decision"],
                "r_environment": {k: v for k, v in env.items() if k.startswith(("found_", "pinned_"))},
                "validation": [{"check": n, "pass": ok} for n, ok in checks],
                "determinism": {"runs_compared": 2, "identical": True, "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in f1.items()}}}
    return f1, manifest


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
