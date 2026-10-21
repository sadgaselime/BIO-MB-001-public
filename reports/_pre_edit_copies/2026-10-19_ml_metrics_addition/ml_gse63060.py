#!/usr/bin/env python3
"""Exploratory ML in GSE63060: nested chip-grouped CV of a ridge classifier (approved ML protocol, 2026-10-19).

Protocol: reports/planning/ML_PROTOCOL_DRAFT_2026-10-19.md (approved as drafted, v7:603; SHA-256 fb4f7881…);
environment: R glmnet 5.1 (D8 glmnet amendment, v7:611). Governing rule v2:550–551: nested CV inside discovery
only; never tuned on validation cohorts. Exploratory; no diagnostic-accuracy claim.

Inputs: the approved GSE63060 primary population (145 AD, 60 CTL; prep_v1) and its G3 gene-level matrix
(17,425 genes) minus the sex-chromosome genes of the R8 probe set (XIST + the 13 Y probes; protocol M1). Recorded
sex and chip are never predictors; age enters only the B1 baseline. The engine (R/ml_glmnet_cv.R) performs per-chip
centring, within-fold scaling and limma selection, ridge (k in {50, 100, 200}) with inner-loop lambda/k choice,
an elastic net (alpha 0.5) secondary model, baselines B0–B2, metrics over 20 repeats of 5-fold leave-chip-group-out
CV, DeLong intervals on repeat-averaged predictions, a 200-permutation within-chip label null, and the final
model refit on all 205 arrays (frozen; applied once to GSE63061 by scripts/ml_apply_gse63061.py).
Runs under the code-identity lifecycle with executed-code verification; writes reports/ml/GSE63060/<version>/.
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
from biomarker_project.expression_adjudication import parse_series_matrix  # noqa: E402
from biomarker_project.limma_backend import APPROVED_PINS, _env, find_rscript  # noqa: E402
from biomarker_project.qc_r8 import XIST_PROBE, Y_PROBES  # noqa: E402

ACC = "GSE63060"
OUT_REL = f"reports/ml/{ACC}"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
PROTOCOL_REL = "reports/planning/ML_PROTOCOL_DRAFT_2026-10-19.md"
PROTOCOL_SHA256 = "fb4f7881c7245d3b4b6bd856f33bd8d90e4ab6a0e239b9b5f52d07a35373ef98"
RENV_LOCK_SHA256 = "1498fa48e9cfe38ee5a3e52416460a179e31105d4d5be111a4ec025ed16180d5"
PREP_REL = f"reports/discovery/{ACC}/prep_v1"
A0_REL = "reports/annotation_audit/illumina_a0/v2"
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
ENGINE = ROOT / "R/ml_glmnet_cv.R"
GLMNET_PIN = "5.1"
APPROVAL_MARKERS = ("ML protocol approval §", PROTOCOL_SHA256, "D8 glmnet amendment §", RENV_LOCK_SHA256)
SETTINGS = {"seed": 20261019, "n_outer": 5, "n_inner": 5, "n_repeats": 20, "kgrid": "50,100,200", "alpha_en": 0.5,
            "b2_genes": 200, "n_lambda": 60, "use_sex": "true", "n_perm": 200}
DETERMINISM_PERMS = 3
EXPECTED = {"arrays": 205, "AD": 145, "genes_g3": 17425}
CORES = 7
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True
MODELS = ("ridge", "B0_prevalence", "B1_age", "B2_equal_weight", "elastic_net")


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sex_chromosome_genes(a0: pd.DataFrame, cohort: str) -> list[str]:
    """Entrez IDs of the R8 sex probes (XIST + the 13 Y probes) that are eligible A0 probes in the cohort."""
    probes = {XIST_PROBE, *Y_PROBES}
    r = a0[(a0["cohort"] == cohort) & (a0["a0_class"] == "eligible") & a0["probe_id"].isin(probes)]
    return sorted(set(r["a0_gene_id"]), key=int)


def engine(mode: str, E: pd.DataFrame, P: pd.DataFrame, settings: dict, extra: dict | None = None,
           cores: int = 1, root: Path | None = None) -> dict[str, bytes]:
    """Run R/ml_glmnet_cv.R in a temporary directory; return its output files as bytes."""
    root = root or ROOT
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_ml_") as tmp:
        tmp = Path(tmp)
        E.to_csv(tmp / "E.tsv", sep="\t", float_format="%.17g", index_label="feature_id")
        P.to_csv(tmp / "P.tsv", sep="\t", index=False, float_format="%.17g")
        args = [f"--{mode}", "--R", APPROVED_PINS["R"], "--limma", APPROVED_PINS["limma"], "--glmnet", GLMNET_PIN,
                "--expression", str(tmp / "E.tsv"), "--pheno", str(tmp / "P.tsv"), "--outdir", str(tmp / "out"),
                "--cores", str(cores)]
        for k, v in {**settings, **(extra or {})}.items():
            if k in ("model", "settings"):
                (tmp / f"{k}.tsv").write_bytes(v)
                v = tmp / f"{k}.tsv"
            args += [f"--{k}", str(v)]
        proc = subprocess.run([find_rscript(), "--no-save", "--no-restore", str(ENGINE), *args], cwd=root, env=_env(),
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit(f"STOP: R/ml_glmnet_cv.R --{mode} failed (exit {proc.returncode}): {proc.stderr.strip()[-1500:]}")
        return {p.name: p.read_bytes() for p in sorted((tmp / "out").iterdir())}


def _tab(b: bytes) -> pd.DataFrame:
    import io
    return pd.read_csv(io.BytesIO(b), sep="\t")


def summarize(files: dict[str, bytes]) -> dict:
    met = _tab(files["repeat_metrics.tsv"])
    out = {"repeat_distribution_note": "2.5th–97.5th percentiles over 20 CV repeats (variability of the CV estimate, "
                                       "not a sampling confidence interval)"}
    for m, g in met.groupby("model", sort=False):
        out[m] = {c: {"mean": float(g[c].mean()), "p2_5": float(g[c].quantile(0.025)), "p97_5": float(g[c].quantile(0.975))}
                  for c in ("auroc", "auprc", "brier", "calibration_intercept", "calibration_slope", "balanced_accuracy")
                  if g[c].notna().any()}
    out["delong_on_repeat_averaged_predictions_approximate"] = _tab(files["delong_auc_averaged.tsv"]).to_dict("records")
    out["delong_differences_approximate"] = _tab(files["delong_auc_differences_averaged.tsv"]).to_dict("records")
    if "permutation_null.tsv" in files:
        perm = _tab(files["permutation_null.tsv"])["mean_auroc"].to_numpy()
        obs = float(met.loc[met["model"] == "ridge", "auroc"].mean())
        out["permutation_null"] = {"n": int(len(perm)), "observed_mean_auroc": obs, "null_mean": float(perm.mean()),
                                   "null_p97_5": float(np.quantile(perm, 0.975)), "null_max": float(perm.max()),
                                   "p_value": float((1 + (perm >= obs).sum()) / (1 + len(perm)))}
    return out


def build_inputs(values: pd.DataFrame, pop: pd.DataFrame, table: pd.DataFrame, a0: pd.DataFrame, gene_matrix):
    vals = values[list(pop["gsm"])].astype(float)
    genes = gene_matrix(vals, table)
    sexg = sex_chromosome_genes(a0, ACC)
    E = genes.drop(index=[g for g in sexg if g in genes.index])
    P = pd.DataFrame({"array": list(pop["gsm"]), "chip": pop["chip"].astype(str).to_numpy(), "y": pop["case_AD"].astype(int).to_numpy(),
                      "age": pop["age"].astype(float).to_numpy(), "sex_male": pop["sex_male"].astype(int).to_numpy()})
    return E, P, sexg, genes.shape[0]


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    p = ci.acceptance_problems(ROOT / PREP_REL, "manifest.json", require_executed_code=True)
    if p:
        probs.append(f"{PREP_REL} not accepted: {p}")
    for rel, want in ((PROTOCOL_REL, PROTOCOL_SHA256), ("renv.lock", RENV_LOCK_SHA256)):
        if not (ROOT / rel).is_file() or _sha(ROOT / rel) != want:
            probs.append(f"{rel} differs from the approved file")
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
    fit = _load("scripts/discovery_fit_gse63060.py", "discovery_fit")
    pop = pd.read_csv(ROOT / PREP_REL / "primary_population_log.tsv", sep="\t", dtype={"gsm": str, "chip": str})
    table = pd.read_csv(ROOT / PREP_REL / "selection_table_G3.tsv", sep="\t", dtype=str)
    a0 = pd.read_csv(ROOT / A0_REL / "a0_probe_classification.tsv", sep="\t", dtype=str, keep_default_na=False)
    values, _ = parse_series_matrix(ROOT / SM_REL)
    values.columns = [str(c) for c in values.columns]
    E, P, sexg, n_g3 = build_inputs(values, pop, table, a0, fit.gene_matrix)
    checks = [("population is 205 arrays, 145 AD (approved)", len(P) == EXPECTED["arrays"] and int(P["y"].sum()) == EXPECTED["AD"]),
              ("G3 matrix has 17,425 genes before sex-gene removal", n_g3 == EXPECTED["genes_g3"]),
              ("complete age and sex", bool(P[["age", "sex_male"]].notna().all().all()))]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED:\n  " + "\n  ".join(failed))
    cv = engine("cv", E, P, SETTINGS, cores=CORES)
    final = engine("final", E, P, SETTINGS, cores=1)
    # determinism: the observed CV, the first permutations and the final model are recomputed and compared byte-for-byte
    cv2 = engine("cv", E, P, {**SETTINGS, "n_perm": 0}, cores=CORES)
    perm2 = engine("cv", E, P, {**SETTINGS, "n_perm": DETERMINISM_PERMS}, cores=CORES)
    final2 = engine("final", E, P, SETTINGS, cores=1)
    same_cv = all(cv[k] == cv2[k] for k in cv2)
    perm_rows = cv["permutation_null.tsv"].decode().splitlines()[: DETERMINISM_PERMS + 1]
    same_perm = perm2["permutation_null.tsv"].decode().splitlines() == perm_rows
    if not (same_cv and same_perm and final == final2):
        raise SystemExit(f"STOP: recomputation differs (cv {same_cv}, permutations {same_perm}, final {final == final2})")
    files = {**cv, **final}
    summary = summarize(files) | {
        "inputs": {"arrays": len(P), "AD": int(P["y"].sum()), "CTL": int((P["y"] == 0).sum()), "chips": int(P["chip"].nunique()),
                   "genes": int(E.shape[0]), "sex_chromosome_genes_removed": sexg},
        "final_model_sha256": hashlib.sha256(files["final_model_coefficients.tsv"]).hexdigest(),
        "label": "Exploratory (v2:550–551). Labels are deposited diagnoses (E2); performance is against noisy labels; "
                 "no diagnostic-accuracy claim."}
    files["ml_summary.json"] = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
    files["sex_chromosome_genes_removed.tsv"] = ("entrez_gene_id\n" + "".join(f"{g}\n" for g in sexg)).encode()
    manifest = {"status": "Exploratory ML (approved protocol, v7:603): GSE63060 nested chip-grouped CV, permutation null and "
                          "frozen final model. Not applied to any other cohort by this run. The SAP remains a proposed draft.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/ml_gse63060.py --version {version}",
                "inputs": {SM_REL: sm_sha, f"{PREP_REL}/manifest.json": _sha(ROOT / PREP_REL / "manifest.json"),
                           PROTOCOL_REL: PROTOCOL_SHA256, "renv.lock": RENV_LOCK_SHA256, "sap_sha256": _sha(ROOT / SAP_REL)},
                "settings": SETTINGS, "glmnet_pin": GLMNET_PIN, "cores": CORES,
                "validation": [{"check": n, "pass": ok} for n, ok in checks],
                "determinism": {"observed_cv_recomputed": True, "first_permutations_recomputed": DETERMINISM_PERMS,
                                "final_model_recomputed": True, "identical": True,
                                "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}}
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
