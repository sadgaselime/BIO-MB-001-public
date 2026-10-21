#!/usr/bin/env python3
"""S11 for GSE63060: discovery model with cell-composition marker scores as covariates (D21 option K1, v7:624).

Label: METHOD CHOSEN 2026-10-21, AFTER PRIMARY RESULTS (S11 itself was prespecified under D16; its method was not).
Family B (covariates estimated from expression; v7:229): selection independence is not claimed. S11 never alters the lock.

Specification (fixed before computation, no tuning):
  population  the approved GSE63060 primary population (145 AD, 60 CTL; prep_v1).
  scores      MCP-counter marker lists (reference/mcpcounter_6b85a67, CC0; D21 resource §): T cells, B lineage, NK cells,
              Monocytic lineage, Neutrophils. Each score = mean over the class's markers present in the G3 matrix of the
              gene's z over the primary population (n - 1), diagnosis-blind.
  model       the H1 discovery model (age linear, recorded sex, chip fixed effect) plus the five scores (linear), in the
              full-rank basis [Q_N, g]; identifiability with the approved D7 values; limma trend = TRUE; BH over all genes.
  comparison  against the primary gene-level fit (fit_v1): all genes (Spearman of t, sign agreement among the 1,401
              primary q < 0.05 genes) and the locked genes excluding marker genes (CD3D): sign agreement, Spearman of t,
              and the number still at q < 0.05 in the locked direction.
Claim boundary: robustness to S11 means "not explained by these composition indices", not "independent of cell composition".
Runs under the code-identity lifecycle with executed-code verification; writes reports/discovery/GSE63060/s11_<version>/.
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

ACC = "GSE63060"
OUT_REL = f"reports/discovery/{ACC}"
PREP_REL, FIT_REL, LOCK_REL = f"reports/discovery/{ACC}/prep_v1", f"reports/discovery/{ACC}/fit_v1", "reports/lock/GSE63060/v1"
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
MARKERS_REL = "reference/mcpcounter_6b85a67/genes.txt"
MARKERS_SHA256 = "408f6c5d02c8f9bd2f1599c598367881853520934f8ce398a4886a8b296922bb"
APPROVAL_MARKERS = ("**APPROVED 2026-10-21", "option K1", "D21 resource §", MARKERS_SHA256)
CLASSES = {"T cells": "T_cells", "B lineage": "B_lineage", "NK cells": "NK_cells", "Monocytic lineage": "Monocytic_lineage",
           "Neutrophils": "Neutrophils"}
LABEL = "METHOD CHOSEN 2026-10-21, AFTER PRIMARY RESULTS (D21 K1); family B; never alters the lock"
C1, C2, C3, ETA, Q = 3, 5, 10.0, 1e-8, 0.05
COEF = "AD_vs_CTL"
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


def read_markers(path: Path) -> dict[str, list[str]]:
    m = pd.read_csv(path, sep="\t", dtype=str)
    out = {}
    for pop_name, key in CLASSES.items():
        out[key] = sorted(set(m.loc[m["Cell population"] == pop_name, "ENTREZID"].dropna().astype(str)), key=int)
    return out


def scores(genes: pd.DataFrame, markers: dict[str, list[str]]) -> tuple[pd.DataFrame, dict]:
    """Per class: mean diagnosis-blind z (n - 1) over the class's markers present in `genes` (rows = Entrez IDs)."""
    out, used = {}, {}
    for k, ids in markers.items():
        present = [g for g in ids if g in genes.index]
        G = genes.loc[present].astype(float)
        z = G.sub(G.mean(axis=1), axis=0).div(G.std(axis=1, ddof=1), axis=0)
        out[k] = z.mean(axis=0)
        used[k] = {"markers": len(ids), "present": len(present)}
    return pd.DataFrame(out), used


def nuisance(pop: pd.DataFrame, sc: pd.DataFrame) -> np.ndarray:
    age = pop["age"].to_numpy(float)
    cols = [np.ones(len(pop)), (age - age.mean()) / age.std(ddof=1), pop["sex_male"].to_numpy(float)]
    for lvl in sorted(pop["chip"].astype(str).unique()):
        cols.append((pop["chip"].astype(str) == lvl).to_numpy(float))
    for k in CLASSES.values():
        v = sc[k].to_numpy(float)
        cols.append((v - v.mean()) / v.std(ddof=1))
    return np.column_stack(cols)


def identify(pop: pd.DataFrame, sc: pd.DataFrame) -> dict:
    g = pop["case_AD"].to_numpy(float)
    N = nuisance(pop, sc)
    n, p = N.shape
    U, s, _ = np.linalg.svd(N, full_matrices=False)
    r = int((s > max(n, p) * s.max() * np.finfo(float).eps).sum())
    Qn = U[:, :r]
    res = g - Qn @ (Qn.T @ g)
    E = float(res @ res / ((g - g.mean()) @ (g - g.mean())))
    tab = pd.crosstab(pop["chip"].astype(str), pop["group"]).reindex(columns=["AD", "CTL"], fill_value=0)
    mixed = tab[(tab["AD"] > 0) & (tab["CTL"] > 0)]
    stops = []
    if not E > ETA:
        stops.append("M3: not estimable")
    if len(mixed) < C1:
        stops.append(f"M2: mixed units {len(mixed)} < c1")
    if min(int(mixed["AD"].sum()), int(mixed["CTL"].sum())) < C2:
        stops.append("M2: a group on mixed units < c2")
    if E > 0 and 1 / E > C3:
        stops.append(f"M4: VIF {1 / E:.3g} > c3")
    out = {"decision": "STOP" if stops else "PROCEED", "stop_reasons": stops, "n": n, "E": E,
           "VIF": (1 / E if E > 0 else float("inf")), "mixed_units": int(len(mixed)), "r_N": r, "residual_df": n - r - 1}
    if not stops:
        out["design"] = Design(np.column_stack([Qn, g]), [f"nuisance_q{i + 1}" for i in range(r)] + [COEF], COEF)
    return out


def compare_locked(primary: pd.DataFrame, s11: pd.DataFrame, signature: pd.DataFrame, exclude: set[str]) -> dict:
    sig = signature[~signature["entrez_gene_id"].isin(exclude)].copy()
    d = sig["direction"].map({"up_in_AD": 1, "down_in_AD": -1}).to_numpy()
    p = primary.set_index("feature_id").loc[sig["entrez_gene_id"]]
    s = s11.set_index("feature_id").loc[sig["entrez_gene_id"]]
    same = np.sign(s["estimate"].to_numpy()) == d
    return {"n_locked_compared": int(len(sig)), "excluded_marker_genes": sorted(exclude),
            "same_sign_as_locked": int(same.sum()),
            "q_lt_0.05_and_same_sign": int((same & (s["q_value_bh"].to_numpy() < Q)).sum()),
            "spearman_t_vs_primary": float(pd.Series(p["t_statistic"].to_numpy()).rank().corr(pd.Series(s["t_statistic"].to_numpy()).rank())),
            "median_abs_estimate_ratio_s11_over_primary": float(np.median(np.abs(s["estimate"].to_numpy()) / np.abs(p["estimate"].to_numpy())))}


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in (PREP_REL, FIT_REL, LOCK_REL):
        pr = ci.acceptance_problems(ROOT / rel, "manifest.json", require_executed_code=True)
        if pr:
            probs.append(f"{rel} not accepted: {pr}")
    if not (ROOT / MARKERS_REL).is_file() or _sha(ROOT / MARKERS_REL) != MARKERS_SHA256:
        probs.append(f"{MARKERS_REL} differs from the approved resource")
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
    sens = _load("scripts/discovery_sensitivity_gse63060.py", "discovery_sensitivity")
    pop = pd.read_csv(ROOT / PREP_REL / "primary_population_log.tsv", sep="\t", dtype={"gsm": str, "chip": str})
    table = pd.read_csv(ROOT / PREP_REL / "selection_table_G3.tsv", sep="\t", dtype=str)
    primary = pd.read_csv(ROOT / FIT_REL / "gene_level_results.tsv", sep="\t", dtype={"feature_id": str})
    signature = pd.read_csv(ROOT / LOCK_REL / "signature.tsv", sep="\t", dtype={"entrez_gene_id": str})
    markers = read_markers(ROOT / MARKERS_REL)
    values, _ = parse_series_matrix(ROOT / SM_REL)
    values.columns = [str(c) for c in values.columns]
    genes = fit.gene_matrix(values[list(pop["gsm"])].astype(float), table)

    def compute():
        sc, used = scores(genes, markers)
        idf = identify(pop, sc)
        files = {"cell_scores.tsv": _tsv(sc.reset_index().rename(columns={"index": "gsm"})),
                 "identifiability.json": _json({k: v for k, v in idf.items() if k != "design"} | {"scores": used})}
        result = {"label": LABEL, "identifiability": idf["decision"], "scores_used": used,
                  "score_means_by_group_descriptive": {k: {g: float(sc.loc[pop.loc[pop["group"] == g, "gsm"], k].mean())
                                                            for g in ("AD", "CTL")} for k in sc.columns}}
        if idf["decision"] != "PROCEED":
            result["fit"] = f"not assessable ({'; '.join(idf['stop_reasons'])})"
            files["s11_summary.json"] = _json(result)
            return files
        run = fit_feature_limma(genes.to_numpy(), list(genes.index), list(genes.columns), idf["design"])
        run.results["data_origin"] = "GEO"
        files["gene_level_results_S11.tsv"] = _tsv(run.results)
        overlap = set(sum(markers.values(), [])) & set(signature["entrez_gene_id"])
        result["comparison_all_genes"] = sens.compare(primary, run.results)
        result["comparison_locked_genes"] = compare_locked(primary, run.results, signature, overlap)
        files["s11_summary.json"] = _json(result)
        files["limma_session_info.txt"] = ("\n".join(run.session_info) + "\n").encode()
        return files

    f1 = compute()
    if f1 != compute():
        raise SystemExit("STOP: two runs are not byte-identical")
    checks = [("population is 145 AD + 60 CTL (approved)", (int((pop.group == "AD").sum()), int((pop.group == "CTL").sum())) == (145, 60)),
              ("G3 matrix has 17,425 genes", genes.shape[0] == 17425)]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED:\n  " + "\n  ".join(failed))
    manifest = {"status": f"S11 (cell composition, D21 K1) for {ACC}. {LABEL}. The SAP remains a proposed draft.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/s11_cell_composition_gse63060.py --version {version}",
                "inputs": {rel: _sha(ROOT / rel / "manifest.json") for rel in (PREP_REL, FIT_REL, LOCK_REL)}
                | {SM_REL: sm_sha, MARKERS_REL: MARKERS_SHA256, "sap_sha256": _sha(ROOT / SAP_REL)},
                "r_environment": {k: v for k, v in env.items() if k.startswith(("found_", "pinned_"))},
                "validation": [{"check": n, "pass": ok} for n, ok in checks],
                "determinism": {"runs_compared": 2, "identical": True, "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in f1.items()}}}
    return f1, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    a = ap.parse_args(argv)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / f"s11_{a.version}", lambda s: produce(a.version),
                                   require_venv=REQUIRE_VENV, executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
