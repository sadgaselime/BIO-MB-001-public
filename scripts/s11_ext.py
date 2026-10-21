#!/usr/bin/env python3
"""S11-ext (POST HOC, labelled): cell-composition marker scores added to the GSE140829 replication and GSE99039 specificity models.

Approved 2026-10-21 (S11-ext §, v7:624) after the GSE140829 and GSE99039 results were known. It never replaces a primary
result and never alters the lock; S15 is not extended. Family B (covariates estimated from expression).

Same construction as S11 (scripts/s11_cell_composition_gse63060.py): five MCP-counter classes (reference/mcpcounter_6b85a67),
each the mean diagnosis-blind z (n - 1) of its present markers, computed over each analysis's own samples; the scores
(standardized) are appended to each primary model's nuisance matrix; full-rank basis [Q_N, g]; D7 identifiability.
  GSE140829  C-c (one-sided, L_c), C-a (one-sided BH), C-b — as scripts/validation_gse140829.py, plus the scores.
  GSE99039   Q1 two-sided with Holm across IPD, GPD, GU; per gene two-sided BH — as scripts/specificity_gse99039.py, plus the scores.
Results are reported beside the accepted primary results (reports/validation/GSE140829/v1, reports/specificity/GSE99039/v1).
Runs under the code-identity lifecycle with executed-code verification; writes reports/s11_ext/<version>/.
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
from biomarker_project.differential_expression import Design  # noqa: E402
from biomarker_project.expression_adjudication import parse_series_matrix  # noqa: E402
from biomarker_project.limma_backend import check_environment, fit_feature_limma  # noqa: E402

OUT_REL = "reports/s11_ext"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
VAL140_REL, SPEC_REL = "reports/validation/GSE140829/v1", "reports/specificity/GSE99039/v1"
LABEL = "S11-ext: POST HOC (approved 2026-10-21 after the GSE140829 and GSE99039 results); family B; never replaces a primary result"
APPROVAL_MARKERS = ("S11-ext §", "POST HOC, labelled", "D21 resource §")
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


val = _load("scripts/validation_gse63061.py", "validation_gse63061")
v140 = _load("scripts/validation_gse140829.py", "validation_gse140829")
sp = _load("scripts/specificity_gse99039.py", "specificity_gse99039")
s11 = _load("scripts/s11_cell_composition_gse63060.py", "s11_cell_composition")
_sha, _tsv, _json = val._sha, val._tsv, val._json


def with_scores(N: np.ndarray, sc: pd.DataFrame) -> np.ndarray:
    cols = [N]
    for k in s11.CLASSES.values():
        v = sc[k].to_numpy(float)
        cols.append(((v - v.mean()) / v.std(ddof=1))[:, None])
    return np.column_stack(cols)


def ident_design(N: np.ndarray, g: np.ndarray, unit: pd.Series, coef: str) -> dict:
    """D7 identifiability (M2–M4) and the full-rank basis [Q_N, g] for an arbitrary nuisance matrix."""
    n, p = N.shape
    U, s, _ = np.linalg.svd(N, full_matrices=False)
    r = int((s > max(n, p) * s.max() * np.finfo(float).eps).sum())
    Q = U[:, :r]
    res = g - Q @ (Q.T @ g)
    E = float(res @ res / ((g - g.mean()) @ (g - g.mean())))
    tab = pd.crosstab(unit.astype(str).to_numpy(), g).reindex(columns=[1.0, 0.0], fill_value=0)
    mixed = tab[(tab[1.0] > 0) & (tab[0.0] > 0)]
    stops = []
    if not E > sp.ETA:
        stops.append("M3: not estimable")
    if len(mixed) < sp.C1:
        stops.append(f"M2: mixed units {len(mixed)} < c1")
    if min(int(mixed[1.0].sum()), int(mixed[0.0].sum())) < sp.C2:
        stops.append("M2: a group on mixed units < c2")
    if E > 0 and 1 / E > sp.C3:
        stops.append(f"M4: VIF {1 / E:.3g} > c3")
    out = {"decision": "STOP" if stops else "PROCEED", "stop_reasons": stops, "n": n, "E": E,
           "VIF": (1 / E if E > 0 else float("inf")), "mixed_units": int(len(mixed)), "r_N": r, "residual_df": n - r - 1}
    if not stops:
        out["design"] = Design(np.column_stack([Q, g]), [f"nuisance_q{i + 1}" for i in range(r)] + [coef], coef)
    return out


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in (VAL140_REL, SPEC_REL, s11.LOCK_REL, "reports/discovery/GSE63060/s11_v1"):
        pr = ci.acceptance_problems(ROOT / rel, "manifest.json", require_executed_code=True)
        if pr:
            probs.append(f"{rel} not accepted: {pr}")
    if not (ROOT / s11.MARKERS_REL).is_file() or _sha(ROOT / s11.MARKERS_REL) != s11.MARKERS_SHA256:
        probs.append("marker resource differs from the approved file")
    for rel, want in ((f"{v140.QCB_REL}/exclusion_list.tsv", v140.EXCLUSION_LIST_SHA256), (f"{sp.QCB_REL}/exclusion_list.tsv", sp.EXCLUSION_LIST_SHA256),
                      (f"{s11.LOCK_REL}/signature.tsv", val.SIGNATURE_SHA256)):
        if not (ROOT / rel).is_file() or _sha(ROOT / rel) != want:
            probs.append(f"{rel} differs from the approved file")
    sap = (ROOT / SAP_REL).read_text(encoding="utf-8") if (ROOT / SAP_REL).is_file() else ""
    missing = [m for m in APPROVAL_MARKERS if m not in sap]
    if missing:
        probs.append(f"approvals not found in the SAP: {missing}")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    sm = {}
    for acc in ("GSE140829", "GSE99039"):
        rel = f"data/raw/{acc}/{acc}_series_matrix.txt.gz"
        man = json.loads((ROOT / f"data/raw/{acc}/download_manifest.json").read_text(encoding="utf-8"))
        sm[rel] = _sha(ROOT / rel)
        if sm[rel] != man["files"][Path(rel).name]["current"]["sha256"]:
            raise SystemExit(f"STOP: {rel} SHA-256 differs from the download manifest")
    env = check_environment()
    prep = _load("scripts/discovery_prep_gse63060.py", "discovery_prep")
    fit = _load("scripts/discovery_fit_gse63060.py", "discovery_fit")
    markers = s11.read_markers(ROOT / s11.MARKERS_REL)
    signature = pd.read_csv(ROOT / s11.LOCK_REL / "signature.tsv", sep="\t", dtype={"entrez_gene_id": str})
    rd = lambda rel: pd.read_csv(ROOT / rel, sep="\t", dtype=str, keep_default_na=False)  # noqa: E731
    # GSE140829 inputs
    e140, x140 = rd(f"{v140.ELIG_REL}/eligibility_log.tsv"), set(rd(f"{v140.QCB_REL}/exclusion_list.tsv")["gsm"])
    nuid = rd(f"{v140.NUID_REL}/nuid_a0_classification.tsv")
    a0 = rd(f"{v140.A0_REL}/a0_probe_classification.tsv")
    a0p = a0[a0["cohort"] == v140.A0_PLATFORM_COHORT]
    vals140, _ = parse_series_matrix(ROOT / v140.SM_REL)
    vals140.columns = [str(c) for c in vals140.columns]
    # GSE99039 inputs
    e99, x99 = rd(f"{sp.ELIG_REL}/eligibility_log.tsv"), set(rd(f"{sp.QCB_REL}/exclusion_list.tsv")["gsm"])
    cls = rd(f"{sp.GPL570_REL}/probe_set_classification.tsv")
    vals99, _ = parse_series_matrix(ROOT / sp.SM_REL)
    vals99.columns = [str(c) for c in vals99.columns]
    uni99, tab99 = sp.gpl570_tables(cls, set(vals99.index))
    prim140 = json.loads((ROOT / VAL140_REL / "validation_summary.json").read_text(encoding="utf-8"))
    prim99 = json.loads((ROOT / SPEC_REL / "specificity_summary.json").read_text(encoding="utf-8"))

    def compute():
        files, out = {}, {"label": LABEL}
        # --- GSE140829 replication with composition covariates
        pop = v140.population(e140, x140, prep)
        table = val.selection_table(nuid, "GSE140829")
        genes = fit.gene_matrix(vals140[list(pop["gsm"])].astype(float), table)
        meas = val.measurability(signature, v140.measurability_universe(a0p, nuid), "GSE140829", genes)
        cov = val.coverage(meas)
        sc, used = s11.scores(genes, markers)
        N, _ = prep.nuisance_matrix(pop)
        idf = ident_design(with_scores(N, sc), pop["case_AD"].to_numpy(float), pop["chip"], "AD_vs_CTL")
        r140 = {"identifiability": {k: v for k, v in idf.items() if k != "design"}, "scores_used": used, "coverage": cov["score_assessable"]}
        if idf["decision"] == "PROCEED" and cov["score_assessable"]:
            score = val.w1_score(genes, meas)
            r140["C-c"] = val.c_c(score, idf["design"])
            nonconst = genes[genes.std(axis=1, ddof=1) > 0]
            g = fit_feature_limma(nonconst.to_numpy(), list(nonconst.index), list(nonconst.columns), idf["design"])
            ca = val.c_a(g.results, meas).rename(columns={"beta_GSE63061": "beta_GSE140829", "consistent_q_lt_0.05": "replicated_q_lt_0.05"})
            files["GSE140829__c_a_per_gene.tsv"] = _tsv(ca)
            r140["C-a"] = {"n": int(len(ca)), "n_replicated_q_lt_0.05": int(ca["replicated_q_lt_0.05"].sum())}
            r140["C-b"] = val.c_b(ca, meas, cov)["overall"]
        r140["primary_for_comparison"] = {"C-c": {k: prim140["C-c"][k] for k in ("estimate", "p_one_sided", "lower_bound_one_sided_95")},
                                          "C-a_n_replicated": prim140["C-a"]["n_replicated_q_lt_0.05"],
                                          "C-b_overall": prim140["C-b"]["overall"]}
        files["GSE140829__cell_scores.tsv"] = _tsv(sc.reset_index().rename(columns={"index": "gsm"}))
        out["GSE140829"] = r140
        # --- GSE99039 specificity with composition covariates
        res99, ps = {}, {}
        for disease, role in sp.CONTRASTS:
            smp, counts = sp.contrast_samples(e99, x99, disease, False)
            g99 = fit.gene_matrix(vals99[list(smp["gsm"])].astype(float), tab99)
            m99 = val.measurability(signature, uni99, sp.ACC, g99)
            c99 = val.coverage(m99)
            sc99, used99 = s11.scores(g99, markers)
            N99, _ = sp.nuisance(smp, False)
            idf99 = ident_design(with_scores(N99, sc99), smp["case"].to_numpy(float), smp["batch"], sp.COEF)
            r = {"role": role, "counts": counts["complete_case"], "scores_used": used99,
                 "identifiability": {k: v for k, v in idf99.items() if k != "design"}}
            if idf99["decision"] == "PROCEED" and c99["score_assessable"]:
                r["Q1"] = sp.q1(val.w1_score(g99, m99), idf99["design"])
                ps[disease] = r["Q1"]["p_two_sided"]
                nonconst = g99[g99.std(axis=1, ddof=1) > 0]
                fr = fit_feature_limma(nonconst.to_numpy(), list(nonconst.index), list(nonconst.columns), idf99["design"])
                pg = sp.per_gene(fr.results, m99)
                files[f"GSE99039_{disease}__per_gene.tsv"] = _tsv(pg)
                r["per_gene"] = {k: int(v) for k, v in pg["category"].value_counts().items()}
            pq = prim99["primary"][disease]["Q1"]
            r["primary_for_comparison"] = {k: pq[k] for k in ("estimate", "p_two_sided", "p_holm_three_contrasts", "category")}
            res99[disease] = r
        adj = sp.holm(ps)
        for k, r in res99.items():
            if "Q1" in r:
                r["Q1"]["p_holm_three_contrasts"] = adj[k]
                r["Q1"]["category"] = (("association with PD — " if k != "GENETIC_UNAFFECTED" else "association — ")
                                       + r["Q1"]["sign_relative_to_AD_signature"]) if adj[k] < sp.ALPHA else "association not demonstrated"
        out["GSE99039"] = res99
        files["s11_ext_summary.json"] = _json(out)
        return files

    f1 = compute()
    if f1 != compute():
        raise SystemExit("STOP: two runs are not byte-identical")
    manifest = {"status": f"{LABEL}. The SAP remains a proposed draft.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/s11_ext.py --version {version}",
                "inputs": {rel: _sha(ROOT / rel / "manifest.json") for rel in (VAL140_REL, SPEC_REL)} | sm
                | {s11.MARKERS_REL: s11.MARKERS_SHA256, "sap_sha256": _sha(ROOT / SAP_REL)},
                "r_environment": {k: v for k, v in env.items() if k.startswith(("found_", "pinned_"))},
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
