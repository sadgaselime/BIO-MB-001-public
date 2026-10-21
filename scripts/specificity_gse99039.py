#!/usr/bin/env python3
"""Tier B step 13: specificity of the locked GSE63060 signature in GSE99039 (SAP v6 §9; v7 §8; D13 approved 2026-10-19).

Locked specification:
  sets        approved GSE99039 exclusion list (v7:625): contrasts IPD vs CONTROL (primary), GPD vs CONTROL (secondary),
              GENETIC_UNAFFECTED vs CONTROL (secondary, descriptive only; D13); covariates Sex + batch (unit, fixed effect),
              complete case (R2-COV); S15 adds age at exam (linear), complete case, labelled sensitivity (no S15 for GU).
  mapping     GPL570 Option A (D6-F); G3 = mean of the eligible present probe sets per Entrez gene; D17 none.
  measurable  v6 §8.3 categories per contrast; coverage rule v6 §8.4 per contrast (same thresholds, D13); failure -> not assessable.
  score       W1, z over each contrast's score samples (n - 1), diagnosis-blind.
  Q1          theta_k = adjusted (disease - CONTROL) mean difference in S; H0 theta = 0, two-sided; Holm across the three
              contrasts (D13); theta with a two-sided 95% CI; the sign is reported relative to the AD signature.
  per gene    limma (trend = TRUE) on all measurable G3 genes of the contrast; two-sided p for the disease coefficient;
              BH across the measurable locked genes within the contrast; beta with an unadjusted two-sided 95% CI (labelled).
  categories  "association with PD — same direction as AD", "— opposite direction", "association not demonstrated".
Rules (v7 §8.1–8.2): no equivalence (no delta); non-significance is never evidence of absence; AD specificity is never
inferred; no AD x PD contrast; magnitudes not comparable across cohorts; specificity never alters the lock.
Runs under the code-identity lifecycle with executed-code verification; writes reports/specificity/GSE99039/<version>/.
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
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from biomarker_project import code_identity as ci  # noqa: E402
from biomarker_project.differential_expression import Design, benjamini_hochberg  # noqa: E402
from biomarker_project.expression_adjudication import parse_series_matrix  # noqa: E402
from biomarker_project.limma_backend import check_environment, fit_feature_limma  # noqa: E402

ACC = "GSE99039"
OUT_REL = f"reports/specificity/{ACC}"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
LOCK_REL = "reports/lock/GSE63060/v1"
GPL570_REL = "reports/annotation_audit/gpl570_option_a/v2"
ELIG_REL, QCA_REL, QCB_REL = f"reports/eligibility/{ACC}/v1", f"reports/qc_stage_a/{ACC}/v1", f"reports/qc_stage_b/{ACC}/v1"
DUP_REL = f"reports/duplicate_review/{ACC}/c1_v1"
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
EXCLUSION_LIST_SHA256 = "1551ab37d2ade028e16907aa6917821db006e8b43c9df010a63e41b8547e6b82"
APPROVAL_MARKERS = ("GSE99039 exclusion-list approval §", EXCLUSION_LIST_SHA256, "GSE99039 eligibility rules § (E-99)",
                    "R8-570a §", "Holm across the three specificity contrasts")
CONTROL = "CONTROL"
CONTRASTS = (("IPD", "primary"), ("GPD", "secondary"), ("GENETIC_UNAFFECTED", "secondary, descriptive only (D13)"))
EXPECTED_SETS = {"IPD": 197, "GPD": 40, "GENETIC_UNAFFECTED": 22, "CONTROL": 229}
COEF = "disease_vs_CONTROL"
C1, C2, C3, ETA = 3, 5, 10.0, 1e-8   # D7 (v7:610), common scope
ALPHA = Q_LEVEL = 0.05
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


val = _load("scripts/validation_gse63061.py", "validation_gse63061")
_sha, _tsv, _json = val._sha, val._tsv, val._json


def holm(p: dict[str, float]) -> dict[str, float]:
    """Holm step-down adjusted p-values (monotone, capped at 1)."""
    keys = sorted(p, key=lambda k: (p[k], k))
    m, out, run = len(keys), {}, 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (m - i) * p[k]))
        out[k] = run
    return out


def nuisance(samples: pd.DataFrame, with_age: bool) -> tuple[np.ndarray, list[str]]:
    """Intercept, [age centred/scaled], sex indicator, indicators for ALL batch levels (v7 §4.1; S15 adds age)."""
    cols, names = [np.ones(len(samples))], ["intercept"]
    if with_age:
        a = samples["age"].to_numpy(float)
        cols.append((a - a.mean()) / a.std(ddof=1)); names.append("age_scaled")
    cols.append(samples["sex_male"].to_numpy(float)); names.append("sex_male")
    for b in sorted(samples["batch"].unique()):
        cols.append((samples["batch"] == b).to_numpy(float)); names.append(f"batch_{b}")
    return np.column_stack(cols), names


def identifiability(samples: pd.DataFrame, with_age: bool) -> dict:
    N, _ = nuisance(samples, with_age)
    g = samples["case"].to_numpy(float)
    n, p = N.shape
    U, s, _ = np.linalg.svd(N, full_matrices=False)
    tau = max(n, p) * s.max() * np.finfo(float).eps
    r = int((s > tau).sum())
    Q = U[:, :r]
    resid = g - Q @ (Q.T @ g)
    E = float(resid @ resid / ((g - g.mean()) @ (g - g.mean()))) if np.unique(g).size > 1 else 0.0
    vif = float("inf") if E <= 0 else 1.0 / E
    tab = pd.crosstab(samples["batch"], samples["case"]).reindex(columns=[1, 0], fill_value=0)
    mixed = tab[(tab[1] > 0) & (tab[0] > 0)]
    m2 = {"mixed_units": int(len(mixed)), "case_on_mixed_units": int(mixed[1].sum()), "control_on_mixed_units": int(mixed[0].sum())}
    stops = []
    if E <= ETA:
        stops.append("M3: not estimable (E <= eta)")
    if m2["mixed_units"] < C1:
        stops.append(f"M2: mixed units {m2['mixed_units']} < c1 = {C1}")
    if min(m2["case_on_mixed_units"], m2["control_on_mixed_units"]) < C2:
        stops.append(f"M2: a group on mixed units < c2 = {C2}")
    if vif > C3:
        stops.append(f"M4: VIF {vif:.4g} > c3 = {C3}")
    return {"decision": "STOP" if stops else "PROCEED", "stop_reasons": stops,
            "decision_checks": {"M2": m2, "M3_E": E, "M4_VIF": vif}, "thresholds": {"c1": C1, "c2": C2, "c3": C3, "eta": ETA},
            "descriptive": {"n": n, "p": p, "r_N": r, "residual_df": n - r - 1}}


def design(samples: pd.DataFrame, with_age: bool, r: int) -> Design:
    N, _ = nuisance(samples, with_age)
    U, _, _ = np.linalg.svd(N, full_matrices=False)
    X = np.column_stack([U[:, :r], samples["case"].to_numpy(float)])
    if np.linalg.matrix_rank(X) != r + 1:
        raise SystemExit("STOP: design rank is not r_N + 1")
    return Design(X, [f"nuisance_q{i + 1}" for i in range(r)] + [COEF], COEF)


def q1(score: pd.Series, d: Design) -> dict:
    r = val.c_c(score, d)
    p1 = float(r["p_one_sided"])
    out = {k: r[k] for k in ("estimate", "std_error", "t_statistic", "df", "ci_low_two_sided_95", "ci_high_two_sided_95")}
    out["p_two_sided"] = float(min(1.0, 2 * min(p1, 1 - p1)))
    out["sign_relative_to_AD_signature"] = "same direction as AD" if r["estimate"] > 0 else "opposite direction"
    return out


def per_gene(fit: pd.DataFrame, meas: pd.DataFrame) -> pd.DataFrame:
    ok = meas[meas["measurable"]].copy()
    f = fit.set_index("feature_id").loc[ok["entrez_gene_id"]]
    ok["d"] = ok["direction"].map(val.DIRS)
    for c in ("estimate", "std_error", "ci_low", "ci_high", "t_statistic", "df", "p_value"):
        ok[c] = f[c].to_numpy()
    ok["q_value_bh"] = benjamini_hochberg(ok["p_value"].to_numpy())
    same = np.sign(ok["estimate"]) == ok["d"]
    ok["category"] = np.where(ok["q_value_bh"] < Q_LEVEL, np.where(same, "association — same direction as AD",
                                                                    "association — opposite direction"),
                              "association not demonstrated")
    ok["ci_note"] = "unadjusted two-sided 95% CI"
    return ok.drop(columns=["measurable"]).reset_index(drop=True)


def contrast_samples(elig: pd.DataFrame, excluded: set[str], disease: str, with_age: bool) -> tuple[pd.DataFrame, dict]:
    s = elig[elig["group"].isin([disease, CONTROL]) & ~elig["gsm"].isin(excluded)].copy()
    n_set = {"disease": int((s["group"] == disease).sum()), "CONTROL": int((s["group"] == CONTROL).sum())}
    s["sex_male"] = s["gender"].map({"Male": 1, "Female": 0})
    s["age"] = pd.to_numeric(s["age"], errors="coerce")
    need = ["sex_male", "batch"] + (["age"] if with_age else [])
    cc = s.dropna(subset=need)
    cc = cc[cc["batch"] != ""].copy()
    cc["case"] = (cc["group"] == disease).astype(int)
    counts = {"set": n_set, "complete_case": {"disease": int(cc["case"].sum()), "CONTROL": int((cc["case"] == 0).sum())},
              "removed_R2_COV": {"disease": n_set["disease"] - int(cc["case"].sum()), "CONTROL": n_set["CONTROL"] - int((cc["case"] == 0).sum())}}
    return cc.reset_index(drop=True), counts


def gpl570_tables(cls: pd.DataFrame, present: set[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    e = cls[cls["option_a_class"].str.startswith("eligible")][["probe_set_id", "option_a_gene_id"]].rename(
        columns={"probe_set_id": "probe_id", "option_a_gene_id": "a0_gene_id"})
    e["cohort"], e["a0_class"] = ACC, "eligible"
    e["in_series_matrix"] = e["probe_id"].map(lambda p: "yes" if p in present else "no")
    return e, val.selection_table(e, ACC)


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in (LOCK_REL, GPL570_REL, ELIG_REL, DUP_REL, QCA_REL, QCB_REL):
        mname = "counts_manifest.json" if rel == GPL570_REL else "manifest.json"
        p = ci.acceptance_problems(ROOT / rel, mname, require_executed_code=True)
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
    fit = _load("scripts/discovery_fit_gse63060.py", "discovery_fit")
    elig = pd.read_csv(ROOT / ELIG_REL / "eligibility_log.tsv", sep="\t", dtype=str, keep_default_na=False)
    excl = pd.read_csv(ROOT / QCB_REL / "exclusion_list.tsv", sep="\t", dtype=str)
    excluded = set(excl["gsm"])
    cls = pd.read_csv(ROOT / GPL570_REL / "probe_set_classification.tsv", sep="\t", dtype=str, keep_default_na=False)
    signature = pd.read_csv(ROOT / LOCK_REL / "signature.tsv", sep="\t", dtype={"entrez_gene_id": str})
    values, _ = parse_series_matrix(ROOT / SM_REL)
    values.columns = [str(c) for c in values.columns]
    universe, table = gpl570_tables(cls, set(values.index))

    def analyse(disease: str, with_age: bool) -> tuple[dict, dict]:
        tag = f"{disease}{'_S15' if with_age else ''}"
        smp, counts = contrast_samples(elig, excluded, disease, with_age)
        ident = identifiability(smp, with_age)
        genes = fit.gene_matrix(values[list(smp["gsm"])].astype(float), table)
        meas = val.measurability(signature, universe, ACC, genes)
        cov = val.coverage(meas)
        files = {f"{tag}__samples.tsv": _tsv(smp[["gsm", "group", "case", "sex_male", "batch", "age"]]),
                 f"{tag}__identifiability.json": _json(ident), f"{tag}__measurability.tsv": _tsv(meas), f"{tag}__coverage.json": _json(cov)}
        res = {"contrast": f"{disease} vs CONTROL", "S15_age_adjusted": with_age, "counts": counts,
               "identifiability": ident["decision"], "score_assessable": cov["score_assessable"]}
        if ident["decision"] != "PROCEED":
            res["Q1"] = res["per_gene"] = f"not assessable ({'; '.join(ident['stop_reasons'])})"
            return files, res
        d = design(smp, with_age, ident["descriptive"]["r_N"])
        nonconst = genes[genes.std(axis=1, ddof=1) > 0]
        g = fit_feature_limma(nonconst.to_numpy(), list(nonconst.index), list(nonconst.columns), d)
        pg = per_gene(g.results, meas)
        files[f"{tag}__per_gene.tsv"] = _tsv(pg)
        res["per_gene"] = {"n_measurable": int(len(pg)), **{k: int(v) for k, v in pg["category"].value_counts().items()}}
        if cov["score_assessable"]:
            score = val.w1_score(genes, meas)
            files[f"{tag}__score_W1.tsv"] = _tsv(pd.DataFrame({"gsm": score.index, "group": list(smp["group"]), "S": score.to_numpy()}))
            res["Q1"] = q1(score, d)
        else:
            res["Q1"] = "not assessable (coverage rule, v6 §8.4)"
        return files, res

    def compute():
        files, results = {}, {}
        for disease, role in CONTRASTS:
            f, r = analyse(disease, False)
            r["role"] = role
            files.update(f); results[disease] = r
        ps = {k: r["Q1"]["p_two_sided"] for k, r in results.items() if isinstance(r["Q1"], dict)}
        adj = holm(ps)
        for k, r in results.items():
            if isinstance(r["Q1"], dict):
                r["Q1"]["p_holm_three_contrasts"] = adj[k]
                r["Q1"]["category"] = (("association with PD — " if k != "GENETIC_UNAFFECTED" else "association — ")
                                       + r["Q1"]["sign_relative_to_AD_signature"]) if adj[k] < ALPHA else "association not demonstrated"
        s15 = {}
        for disease in ("IPD", "GPD"):
            f, r = analyse(disease, True)
            r["label"] = "S15 sensitivity (age-adjusted, complete case); unadjusted for multiplicity"
            files.update(f); s15[disease] = r
        summary = {"cohort": ACC, "primary": results, "S15": s15,
                   "rules": "two-sided; Holm across the three Q1 tests (D13); GENETIC_UNAFFECTED descriptive only; no equivalence "
                            "(no delta); non-significance is never evidence of absence; AD specificity is never inferred; "
                            "magnitudes not comparable across cohorts"}
        files["specificity_summary.json"] = _json(summary)
        return files, results

    f1, results = compute()
    if f1 != compute()[0]:
        raise SystemExit("STOP: two runs are not byte-identical")
    sets = {g: int(((elig["group"] == g) & ~elig["gsm"].isin(excluded)).sum()) for g in EXPECTED_SETS}
    checks = [("specificity sets equal the approved list (IPD 197, GPD 40, GU 22, CONTROL 229)", sets == EXPECTED_SETS),
              ("signature has 200 locked genes", len(signature) == 200)]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED:\n  " + "\n  ".join(failed))
    manifest = {"status": f"Tier B step 13: specificity of the locked GSE63060 signature in {ACC} (D13). The SAP remains a "
                          "proposed draft (not approved, not frozen).",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/specificity_gse99039.py --version {version}",
                "inputs": {rel: _sha(ROOT / rel / "manifest.json") for rel in (LOCK_REL, ELIG_REL, DUP_REL, QCA_REL, QCB_REL)}
                | {SM_REL: sm_sha, "exclusion_list_sha256": EXCLUSION_LIST_SHA256, "sap_sha256": _sha(ROOT / SAP_REL),
                   f"{GPL570_REL}/probe_set_classification.tsv": _sha(ROOT / GPL570_REL / "probe_set_classification.tsv")},
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
