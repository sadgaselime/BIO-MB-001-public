#!/usr/bin/env python3
"""Tier B step 10: GSE63060 discovery fit (primary H1 model), probe level and gene level (v5 §5.4).

Approved specification (SAP v7, recorded 2026-10-18): estimand E2 (deposited AD vs CTL labels; ~41 AD probably MCI at draw);
primary population 145 AD vs 60 CTL (approved exclusion list); covariates age (linear), recorded sex and chip (unit, fixed
effect); limma lmFit + eBayes(trend = TRUE, robust = FALSE) through the D8 runner (R/limma_de.R, pins checked);
Benjamini–Hochberg within each family; gene-level claims use only the gene-level fit at q < 0.05 (D15); probe-level and
gene-level families are reported separately and never mixed. Identifiability: PROCEED (prep, Tier B step 8).

Design: the full-rank basis [Q_N, g] of v5 §4.4 step 7 (Q_N = left singular vectors of the nuisance matrix N retained at tau;
g = AD indicator). By Frisch–Waugh–Lovell the AD coefficient, its SE, residuals and df equal those of the chip-indicator
parameterization; only the AD coefficient is reported. Probe level: every Series Matrix probe (D17: no filter; multi-mapped and
unmapped included). Gene level (G3): mean of each gene's constituent eligible probes on the deposited scale (selection table).
This is NOT a signature lock (step 11) and NOT validation; the SAP is not approved, so results are provisional.
Runs under the code-identity lifecycle with executed-code verification; writes reports/discovery/GSE63060/fit_<version>/.
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
PREP_REL = f"reports/discovery/{ACC}/prep_v1"
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
COEF = "AD_vs_CTL"
Q_LEVEL = 0.05
EXPECTED = {"arrays": 205, "AD": 145, "probes": 38323, "genes": 17425}  # approved population; A0/G3 counts
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


def _load_prep_module():
    spec = importlib.util.spec_from_file_location("discovery_prep", ROOT / "scripts/discovery_prep_gse63060.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def full_rank_design(pop: pd.DataFrame, nuisance_matrix, expected_r: int) -> Design:
    N, _ = nuisance_matrix(pop)
    n, p = N.shape
    U, s, _ = np.linalg.svd(N, full_matrices=False)
    r = int((s > max(n, p) * s.max() * np.finfo(float).eps).sum())
    if r != expected_r:
        raise SystemExit(f"STOP: r_N = {r} differs from the locked identifiability run ({expected_r})")
    X = np.column_stack([U[:, :r], pop["case_AD"].to_numpy(float)])
    if np.linalg.matrix_rank(X) != r + 1:
        raise SystemExit("STOP: design rank is not r_N + 1")
    return Design(X, [f"nuisance_q{i + 1}" for i in range(r)] + [COEF], COEF)


def gene_matrix(values: pd.DataFrame, table: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for gid, probes in zip(table["entrez_gene_id"], table["constituent_probes"]):
        rows[str(gid)] = values.loc[probes.split(";")].mean(axis=0)
    return pd.DataFrame(rows).T


def summarize(res: pd.DataFrame) -> dict:
    sig = res[res["q_value_bh"] < Q_LEVEL]
    return {"n_tested": int(len(res)), "n_estimable": int(res["estimable"].sum()), f"n_q_lt_{Q_LEVEL}": int(len(sig)),
            "n_up_AD": int((sig["estimate"] > 0).sum()), "n_down_AD": int((sig["estimate"] < 0).sum()),
            "min_p": float(res["p_value"].min()), "df_total_median": float(res["df"].median())}


def produce(version: str) -> tuple[dict, dict]:
    probs = ci.acceptance_problems(ROOT / PREP_REL, "manifest.json", require_executed_code=True)
    if probs:
        raise SystemExit(f"STOP: discovery prep not accepted: {probs}")
    ident = json.loads((ROOT / PREP_REL / "identifiability_checks.json").read_text(encoding="utf-8"))
    if ident["decision"] != "PROCEED":
        raise SystemExit(f"STOP: identifiability decision is {ident['decision']} ({ident.get('stop_reasons')})")
    raw_man = json.loads((ROOT / f"data/raw/{ACC}/download_manifest.json").read_text(encoding="utf-8"))
    sm_sha = _sha(ROOT / SM_REL)
    if sm_sha != raw_man["files"][Path(SM_REL).name]["current"]["sha256"]:
        raise SystemExit("STOP: Series Matrix SHA-256 differs from the download manifest")
    env = check_environment()  # D8 pins (R, Bioconductor, limma, renv, BiocManager, statmod)
    prep = _load_prep_module()
    pop = pd.read_csv(ROOT / PREP_REL / "primary_population_log.tsv", sep="\t", dtype={"gsm": str, "chip": str})
    table = pd.read_csv(ROOT / PREP_REL / "selection_table_G3.tsv", sep="\t", dtype=str)
    values, _ = parse_series_matrix(ROOT / SM_REL)
    values.columns = [str(c) for c in values.columns]
    values = values[list(pop["gsm"])].astype(float)
    design = full_rank_design(pop, prep.nuisance_matrix, ident["descriptive"]["r_N"])
    genes = gene_matrix(values, table)

    def fit_all():
        p = fit_feature_limma(values.to_numpy(), list(values.index), list(values.columns), design)
        g = fit_feature_limma(genes.to_numpy(), list(genes.index), list(genes.columns), design)
        for run in (p, g):
            run.results["data_origin"] = "GEO"
        return p, g
    p1, g1 = fit_all()
    p2, g2 = fit_all()
    files = {"probe_level_results.tsv": _tsv(p1.results), "probe_level_moderation.tsv": _tsv(p1.moderation),
             "gene_level_results.tsv": _tsv(g1.results), "gene_level_moderation.tsv": _tsv(g1.moderation),
             "limma_session_info.txt": ("\n".join(g1.session_info) + "\n").encode()}
    again = {"probe_level_results.tsv": _tsv(p2.results), "probe_level_moderation.tsv": _tsv(p2.moderation),
             "gene_level_results.tsv": _tsv(g2.results), "gene_level_moderation.tsv": _tsv(g2.moderation),
             "limma_session_info.txt": ("\n".join(g2.session_info) + "\n").encode()}
    if files != again:
        raise SystemExit("STOP: two fits are not byte-identical")
    summary = {"probe_level": summarize(p1.results), "gene_level": summarize(g1.results)}
    files["discovery_summary.json"] = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
    checks = [("arrays and AD count as approved (205; 145 AD, 60 CTL)", values.shape[1] == EXPECTED["arrays"] and int(pop["case_AD"].sum()) == EXPECTED["AD"]),
              ("probe level covers all Series Matrix probes (38,323)", values.shape[0] == EXPECTED["probes"]),
              ("gene level covers the G3 genes (17,425)", genes.shape[0] == EXPECTED["genes"]),
              ("residual df equals n - r_N - 1", bool(np.allclose(p1.moderation["df_residual"], ident["descriptive"]["M5_residual_df"])))]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED:\n  " + "\n  ".join(failed))
    manifest = {"status": "Tier B step 10: GSE63060 discovery fit (primary H1 model), probe and gene level. Provisional: the SAP "
                          "is not approved; no signature is locked; no validation has been performed.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/discovery_fit_gse63060.py --version {version}",
                "inputs": {SM_REL: sm_sha, f"{PREP_REL}/manifest.json": _sha(ROOT / PREP_REL / "manifest.json")},
                "design": {"basis": "[Q_N, g] (v5 §4.4 step 7)", "r_N": ident["descriptive"]["r_N"], "coefficient": COEF,
                           "nuisance": "intercept, age (centred, scaled), sex indicator, chip indicators (all levels)"},
                "method": "limma::lmFit + eBayes(trend = TRUE, robust = FALSE); BH within family", "q_level_claims": Q_LEVEL,
                "r_environment": {k: v for k, v in env.items() if k.startswith(("found_", "pinned_"))},
                "summary": summary, "validation": [{"check": n, "pass": ok} for n, ok in checks],
                "determinism": {"fits_compared": 2, "identical": True,
                                "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}}
    return files, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    a = ap.parse_args(argv)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / f"fit_{a.version}", lambda s: produce(a.version),
                                   require_venv=REQUIRE_VENV, executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
