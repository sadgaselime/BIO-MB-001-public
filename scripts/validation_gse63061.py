#!/usr/bin/env python3
"""Tier B steps 6–9 and 12 for GSE63061: consistency test of the locked GSE63060 signature (SAP v7 §4; v6 §8).

Locked specification (lock reports/lock/GSE63060/v1, written before any GSE63061 expression was modelled):
  population  approved GSE63061 exclusion list applied (AD + CTL; R5 labels excluded; Q1 arrays excluded); covariates
              age (linear), recorded sex, chip (unit, fixed effect) (v7 §4.1); identifiability M2–M4 with D7 c1 = 3,
              c2 = 5, c3 = 10 — STOP makes C-c and C-a "not assessable" (v7 §4.1 rule 4).
  mapping     A0 (D6-G), pinned illumina_a0/v2; G3 gene level = mean of the cohort's eligible present probes; D17 none.
  measurable  v6 §8.3: 1 unmapped, 2 no eligible probe in the Series Matrix, 3 constant in cohort, 4 measurable.
  coverage    per direction non-empty at lock: >= 50% and >= min(5, n locked) measurable, else score not assessable.
  score       W1: z over all score samples (n - 1), diagnosis-blind; S = mean_up z - mean_down z.
  C-c         theta = adjusted AD - CTL difference in S; one-sided t test (H1 theta > 0), alpha 0.05; decision bound
              L_c (one-sided 95%); two-sided 95% CI descriptive (D20, v6 §8.5).
  C-a         gene-level limma fit on all measurable G3 genes (trend = TRUE); one-sided p in the locked direction;
              BH over the measurable locked genes; "consistent in GSE63061" iff q < 0.05; unadjusted one-sided bounds.
              Summary: count, denominator and proportion consistent, with no interval (v7:69, 2026-10-19).
  C-b         per direction and overall: concordant count, measurable count, proportion; no interval or p-value (D12;
              v7:68, 2026-10-19).
  §4.5        Pearson r of discovery and GSE63061 gene-level effects over measurable locked genes, with the Fisher-z 95%
              interval labelled nominal (v7:83, 2026-10-19): it assumes independent genes, so co-expression, signature
              selection and possible participant overlap (H9) make it too narrow and may inflate r. Descriptive only.
Wording: GSE63061 is a related-cohort CONSISTENCY test; "replicated" is never used (v6 §8.6). Magnitudes are not
comparable across cohorts (v6 §8.9). No cross-cohort claim (X1).
Runs under the code-identity lifecycle with executed-code verification; writes reports/validation/GSE63061/<version>/.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
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
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from biomarker_project import code_identity as ci  # noqa: E402
from biomarker_project.differential_expression import Design, benjamini_hochberg  # noqa: E402
from biomarker_project.expression_adjudication import parse_series_matrix  # noqa: E402
from biomarker_project.limma_backend import APPROVED_PINS, _env, check_environment, find_rscript, fit_feature_limma  # noqa: E402

ACC = "GSE63061"
OUT_REL = f"reports/validation/{ACC}"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
LOCK_REL = "reports/lock/GSE63060/v1"
PIN_REL = "reports/annotation_audit/annotation_pin/v1"
A0_REL = "reports/annotation_audit/illumina_a0/v2"
ELIG_REL, QCA_REL, QCB_REL = f"reports/eligibility/{ACC}/v1", f"reports/qc_stage_a/{ACC}/v1", f"reports/qc_stage_b/{ACC}/v1"
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
STATS_R = ROOT / "R/validation_stats.R"
LOCK_RECORD_SHA256 = "70b9e4d3ce260778665bafeed491d77efd1ce2f227aa11599f4534980da8f3c9"
SIGNATURE_SHA256 = "9ca4310ce634b536f5acdfb942d89daa3fc319721d39812fc026af8c41242975"
EXCLUSION_LIST_SHA256 = "75307975a67ebedb24b4d908eb6627ae0a196b0421e2d4dffc21260b69ec2697"
APPROVAL_MARKERS = ("GSE63061 exclusion-list approval §", EXCLUSION_LIST_SHA256,
                    "GSE63061 descriptive methods § (2026-10-19, explicit PI instruction",
                    "O1 (separate within-cohort families) + X1", "C-c and C-a as specified; C-b descriptive only")
EXPECTED = {"AD": 139, "CTL": 133}
COEF = "AD_vs_CTL"
ALPHA = Q_LEVEL = 0.05
DIRS = {"up_in_AD": 1, "down_in_AD": -1}
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tsv(df: pd.DataFrame) -> bytes:
    return df.to_csv(sep="\t", index=False, float_format="%.17g", lineterminator="\n").encode("utf-8")


def _json(d) -> bytes:
    return (json.dumps(d, indent=2, sort_keys=True) + "\n").encode()


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def r_stats(mode: list[str], tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Run R/validation_stats.R (R version pinned by D8) on temporary TSV inputs; return its output table."""
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_vstats_") as tmp:
        tmp = Path(tmp)
        args = []
        for flag, df in tables.items():
            df.to_csv(tmp / f"{flag}.tsv", sep="\t", index=False, float_format="%.17g")
            args += [f"--{flag}", str(tmp / f"{flag}.tsv")]
        proc = subprocess.run([find_rscript(), "--no-save", "--no-restore", str(STATS_R), "--R", APPROVED_PINS["R"],
                               *mode, *args, "--out", str(tmp / "out.tsv")], cwd=ROOT, env=_env(), capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit(f"STOP: R/validation_stats.R failed (exit {proc.returncode}): {proc.stderr.strip()[-1000:]}")
        return pd.read_csv(tmp / "out.tsv", sep="\t", dtype={"feature_id": str, "coefficient": str})


def selection_table(a0: pd.DataFrame, cohort: str) -> pd.DataFrame:
    e = a0[(a0["cohort"] == cohort) & (a0["a0_class"] == "eligible") & (a0["in_series_matrix"] == "yes")]
    t = (e.groupby("a0_gene_id")["probe_id"].apply(lambda s: ";".join(sorted(s))).reset_index()
         .rename(columns={"a0_gene_id": "entrez_gene_id", "probe_id": "constituent_probes"}))
    t["n_probes"] = t["constituent_probes"].str.count(";") + 1
    return t.sort_values("entrez_gene_id", key=lambda c: c.astype(int)).reset_index(drop=True)


def measurability(signature: pd.DataFrame, a0: pd.DataFrame, cohort: str, genes: pd.DataFrame) -> pd.DataFrame:
    """v6 §8.3 category per locked gene; `genes` = G3 values over the score samples (rows = Entrez IDs)."""
    rows = a0[(a0["cohort"] == cohort) & (a0["a0_class"] == "eligible")]
    mapped = set(rows["a0_gene_id"])
    present = set(rows.loc[rows["in_series_matrix"] == "yes", "a0_gene_id"])
    out = []
    for gid in signature["entrez_gene_id"].astype(str):
        if gid not in mapped:
            cat = "1_unmapped"
        elif gid not in present or gid not in genes.index:
            cat = "2_no_eligible_probe_in_series_matrix"
        elif float(np.nanstd(genes.loc[gid].to_numpy(float))) == 0.0:
            cat = "3_constant_in_cohort"
        else:
            cat = "4_measurable"
        out.append(cat)
    m = signature[["lock_rank", "entrez_gene_id", "symbol", "direction"]].copy()
    m["entrez_gene_id"] = m["entrez_gene_id"].astype(str)
    m["category"] = out
    m["measurable"] = m["category"] == "4_measurable"
    return m


def coverage(meas: pd.DataFrame) -> dict:
    res = {}
    for d in DIRS:
        sub = meas[meas["direction"] == d]
        n_lock, n_meas = int(len(sub)), int(sub["measurable"].sum())
        need = max(0.5 * n_lock, min(5, n_lock))
        res[d] = {"locked": n_lock, "measurable": n_meas, "required": need, "met": n_lock == 0 or n_meas >= need}
    res["score_assessable"] = all(res[d]["met"] for d in DIRS)
    return res


def w1_score(genes: pd.DataFrame, meas: pd.DataFrame) -> pd.Series:
    """W1 (v6 §8.4): diagnosis-blind z per gene over all score samples (n - 1); S = mean_up z - mean_down z."""
    ok = meas[meas["measurable"]]
    G = genes.loc[ok["entrez_gene_id"]].astype(float)
    z = G.sub(G.mean(axis=1), axis=0).div(G.std(axis=1, ddof=1), axis=0)
    s = pd.Series(0.0, index=genes.columns)
    for d, sign in DIRS.items():
        ids = list(ok.loc[ok["direction"] == d, "entrez_gene_id"])
        if ids:
            s = s + sign * z.loc[ids].mean(axis=0)
    return s


def c_c(score: pd.Series, design: Design) -> dict:
    y = pd.DataFrame({"sample_id": score.index, "S": score.to_numpy()})
    X = pd.DataFrame(design.matrix, columns=design.columns)
    X.insert(0, "sample_id", list(score.index))
    r = r_stats(["--ols", "--coef", design.coefficient], {"y": y, "design": X}).iloc[0].to_dict()
    r.update({"decision_rule": "reject H0: theta <= 0 iff p_one_sided < 0.05 (equivalently L_c > 0)",
              "consistent_direction_shift": bool(r["p_one_sided"] < ALPHA), "bound_agrees_with_test":
              bool((r["p_one_sided"] < ALPHA) == (r["lower_bound_one_sided_95"] > 0))})
    return r


def c_a(gene_fit: pd.DataFrame, meas: pd.DataFrame) -> pd.DataFrame:
    ok = meas[meas["measurable"]].copy()
    f = gene_fit.set_index("feature_id").loc[ok["entrez_gene_id"]]
    ok["d"] = ok["direction"].map(DIRS)
    ok["beta_GSE63061"] = f["estimate"].to_numpy()
    ok["std_error"] = f["std_error"].to_numpy()
    ok["t_statistic"] = f["t_statistic"].to_numpy()
    ok["df"] = f["df"].to_numpy()
    tail = r_stats(["--tail"], {"input": pd.DataFrame({"feature_id": ok["entrez_gene_id"],
                                                         "t_signed": ok["d"] * ok["t_statistic"], "df": ok["df"]})})
    ok["p_one_sided"] = tail["p_one_sided"].to_numpy()
    ok["q_value_bh"] = benjamini_hochberg(ok["p_one_sided"].to_numpy())
    q95 = tail["q95"].to_numpy()
    ok["bound_one_sided_95_unadjusted"] = np.where(ok["d"] > 0, ok["beta_GSE63061"] - q95 * ok["std_error"],
                                                   ok["beta_GSE63061"] + q95 * ok["std_error"])
    ok["bound_side"] = np.where(ok["d"] > 0, "lower", "upper")
    ok["consistent_q_lt_0.05"] = ok["q_value_bh"] < Q_LEVEL
    ok["concordant_sign"] = np.sign(ok["beta_GSE63061"]) == ok["d"]
    return ok.drop(columns=["measurable", "category"]).reset_index(drop=True)


def c_b(ca: pd.DataFrame, meas: pd.DataFrame, cov: dict) -> dict:
    out = {"T_measurable": int(meas["measurable"].sum()), "coverage_status": cov, "inferential": False,
           "note": "no interval or p-value (D12; v7:68)"}
    for d, sub in [(d, ca[ca["direction"] == d]) for d in DIRS] + [("overall", ca)]:
        n, k = int(len(sub)), int(sub["concordant_sign"].sum())
        out[d] = {"measurable": n, "concordant": k, "discordant": n - k, "proportion_concordant": k / n if n else None}
    return out


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in (LOCK_REL, PIN_REL, ELIG_REL, QCA_REL, QCB_REL):
        p = ci.acceptance_problems(ROOT / rel, "manifest.json", require_executed_code=True)
        if p:
            probs.append(f"{rel} not accepted: {p}")
    for rel, want in ((f"{LOCK_REL}/lock_record.json", LOCK_RECORD_SHA256), (f"{LOCK_REL}/signature.tsv", SIGNATURE_SHA256),
                      (f"{QCB_REL}/exclusion_list.tsv", EXCLUSION_LIST_SHA256)):
        if not (ROOT / rel).is_file() or _sha(ROOT / rel) != want:
            probs.append(f"{rel} differs from the locked/approved file")
    sap = (ROOT / SAP_REL).read_text(encoding="utf-8") if (ROOT / SAP_REL).is_file() else ""
    missing = [m for m in APPROVAL_MARKERS if m not in sap]
    if missing:
        probs.append(f"approvals not found in the SAP: {missing}")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    pin = json.loads((ROOT / PIN_REL / "annotation_pin_record.json").read_text(encoding="utf-8"))
    a0_sha = _sha(ROOT / A0_REL / "a0_probe_classification.tsv")
    if pin["upstream"]["illumina_a0"]["tables_sha256"]["a0_probe_classification.tsv"] != a0_sha:
        probs.append("A0 table differs from the annotation pin")
    raw_man = json.loads((ROOT / f"data/raw/{ACC}/download_manifest.json").read_text(encoding="utf-8"))
    sm_sha = _sha(ROOT / SM_REL)
    if sm_sha != raw_man["files"][Path(SM_REL).name]["current"]["sha256"]:
        probs.append("Series Matrix SHA-256 differs from the download manifest")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    env = check_environment()
    prep = _load("scripts/discovery_prep_gse63060.py", "discovery_prep")
    fit = _load("scripts/discovery_fit_gse63060.py", "discovery_fit")
    elig = pd.read_csv(ROOT / ELIG_REL / "eligibility_log.tsv", sep="\t", dtype=str, keep_default_na=False)
    excluded = set(pd.read_csv(ROOT / QCB_REL / "exclusion_list.tsv", sep="\t", dtype=str)["gsm"])
    a2 = pd.read_csv(ROOT / QCA_REL / "qc_a2_pairs.tsv", sep="\t", dtype=str)
    audit = pd.read_csv(ROOT / QCA_REL / "qc_audit.tsv", sep="\t", dtype=str, keep_default_na=False)
    a0 = pd.read_csv(ROOT / A0_REL / "a0_probe_classification.tsv", sep="\t", dtype=str, keep_default_na=False)
    signature = pd.read_csv(ROOT / LOCK_REL / "signature.tsv", sep="\t", dtype={"entrez_gene_id": str})
    values, _ = parse_series_matrix(ROOT / SM_REL)
    values.columns = [str(c) for c in values.columns]

    def compute():
        pop = prep.primary_population(elig, excluded)
        ident = prep.identifiability(pop)
        c2log = {"tier_b_step": 6, "a2_pairs": int(len(a2)), "r9_referred_d18": int((audit["r9_outcome"] == "referred_d18").sum())}
        c2log["status"] = "complete: no C2 candidates" if c2log["a2_pairs"] == 0 and c2log["r9_referred_d18"] == 0 else "C2 candidates: review required"
        table = selection_table(a0, ACC)
        vals = values[list(pop["gsm"])].astype(float)
        genes = fit.gene_matrix(vals, table)
        meas = measurability(signature, a0, ACC, genes)
        cov = coverage(meas)
        files = {"c2_duplicate_review_log.json": _json(c2log), "primary_population_log.tsv": _tsv(pop),
                 "identifiability_checks.json": _json(ident), "selection_table_G3.tsv": _tsv(table),
                 "measurability.tsv": _tsv(meas), "coverage.json": _json(cov)}
        result = {"cohort": ACC, "role": "related-cohort consistency (possible participant overlap with GSE63060, H9)",
                  "identifiability_decision": ident["decision"], "score_assessable": cov["score_assessable"]}
        if ident["decision"] != "PROCEED" or not c2log["status"].startswith("complete"):
            result["C-c"] = result["C-a"] = "not assessable (v7 §4.1 rule 4 / C2 incomplete)"
            files["validation_summary.json"] = _json(result)
            return files, pop, ident, None
        design = fit.full_rank_design(pop, prep.nuisance_matrix, ident["descriptive"]["r_N"])
        nonconst = genes[genes.std(axis=1, ddof=1) > 0]
        g = fit_feature_limma(nonconst.to_numpy(), list(nonconst.index), list(nonconst.columns), design)
        g.results["data_origin"] = "GEO"
        ca = c_a(g.results, meas)
        files["gene_level_results.tsv"] = _tsv(g.results)
        files["c_a_per_gene.tsv"] = _tsv(ca)
        k = int(ca["consistent_q_lt_0.05"].sum())
        result["C-a"] = {"family": "measurable locked genes in GSE63061", "n": int(len(ca)), "n_consistent_q_lt_0.05": k,
                         "proportion_consistent": k / len(ca) if len(ca) else None,
                         "summary_note": "descriptive; no interval (a binomial interval assumes independent genes; v7:69)"}
        result["C-b"] = c_b(ca, meas, cov)
        disc = signature.set_index("entrez_gene_id").loc[ca["entrez_gene_id"], "beta_AD_minus_CTL"].to_numpy()
        cor = r_stats(["--cor"], {"input": pd.DataFrame({"x": disc, "y": ca["beta_GSE63061"].to_numpy()})}).iloc[0].to_dict()
        cor = {"n_genes": cor["n"], "pearson_r": cor["pearson_r"], "fisher_z_95_nominal_low": cor["ci_low"],
               "fisher_z_95_nominal_high": cor["ci_high"]}
        result["effect_correlation_v7_4_5"] = cor | {"label": "descriptive; the Fisher-z interval is nominal: it assumes independent genes, "
                                                     "so co-expression, signature selection and possible participant overlap (H9) make it "
                                                     "too narrow and may inflate r; not a replication claim (v7:83)"}
        if cov["score_assessable"]:
            score = w1_score(genes, meas)
            files["score_W1.tsv"] = _tsv(pd.DataFrame({"gsm": score.index, "group": list(pop["group"]), "S": score.to_numpy()}))
            result["C-c"] = c_c(score, design)
        else:
            result["C-c"] = "not assessable (coverage rule, v6 §8.4)"
        result["wording"] = "consistency, not replication; magnitudes not comparable across cohorts; no cross-cohort claim (X1)"
        files["validation_summary.json"] = _json(result)
        files["limma_session_info.txt"] = ("\n".join(g.session_info) + "\n").encode()
        return files, pop, ident, result

    f1, pop, ident, result = compute()
    if f1 != compute()[0]:
        raise SystemExit("STOP: two runs are not byte-identical")
    checks = [("primary population is 139 AD + 133 CTL (approved list)",
               (int((pop.group == "AD").sum()), int((pop.group == "CTL").sum())) == (EXPECTED["AD"], EXPECTED["CTL"])),
              ("complete covariates (R2-COV) for every primary array", bool(pop[["age", "sex_male"]].notna().all().all())),
              ("signature has 200 locked genes", len(signature) == 200)]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED:\n  " + "\n  ".join(failed))
    manifest = {"status": f"Tier B steps 6–9 and 12 for {ACC}: related-cohort consistency test of the locked GSE63060 signature. "
                          "The SAP remains a proposed draft (not approved, not frozen).",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/validation_gse63061.py --version {version}",
                "inputs": {rel: _sha(ROOT / rel / "manifest.json") for rel in (LOCK_REL, PIN_REL, ELIG_REL, QCA_REL, QCB_REL)}
                | {SM_REL: sm_sha, "lock_record_sha256": LOCK_RECORD_SHA256, "signature_sha256": SIGNATURE_SHA256,
                   "exclusion_list_sha256": EXCLUSION_LIST_SHA256, "a0_probe_classification_sha256": a0_sha,
                   "sap_sha256": _sha(ROOT / SAP_REL)},
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
