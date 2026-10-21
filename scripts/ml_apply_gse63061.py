#!/usr/bin/env python3
"""Apply the frozen GSE63060 ridge model ONCE to GSE63061 (approved ML protocol, 2026-10-19; v7:603).

The model (reports/ml/GSE63060/<ml_version>/final_model_coefficients.tsv, hashed in that run's summary) is applied
without any re-fitting or tuning: per-chip centring within GSE63061, within-cohort diagnosis-blind standardization
of each model gene, missing genes held at the cohort mean (z = 0, counted), the frozen threshold, and the frozen B1
age model for comparison. Population: the approved GSE63061 primary population (139 AD, 133 CTL; validation v1).
Labelled: related cohort, possible participant overlap with GSE63060 (H9); cross-platform (GPL6947 -> GPL10558);
exploratory; not independent validation; no diagnostic-accuracy claim.
Runs under the code-identity lifecycle with executed-code verification; writes reports/ml/GSE63061_external/<version>/.
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

ACC = "GSE63061"
OUT_REL = f"reports/ml/{ACC}_external"
VAL_REL = f"reports/validation/{ACC}/v1"
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
EXPECTED = {"AD": 139, "CTL": 133}
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


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


def produce(version: str, ml_version: str) -> tuple[dict, dict]:
    ml_rel = f"reports/ml/GSE63060/{ml_version}"
    probs = []
    for rel in (ml_rel, VAL_REL):
        p = ci.acceptance_problems(ROOT / rel, "manifest.json", require_executed_code=True)
        if p:
            probs.append(f"{rel} not accepted: {p}")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    ml = _load("scripts/ml_gse63060.py", "ml_gse63060")
    summary = json.loads((ROOT / ml_rel / "ml_summary.json").read_text(encoding="utf-8"))
    model_b = (ROOT / ml_rel / "final_model_coefficients.tsv").read_bytes()
    if hashlib.sha256(model_b).hexdigest() != summary["final_model_sha256"]:
        raise SystemExit("STOP: frozen model differs from the hash recorded by the ML run")
    settings_b = (ROOT / ml_rel / "final_model_settings.tsv").read_bytes()
    out_dir = ROOT / OUT_REL
    done = [d.name for d in out_dir.iterdir() if ".staging-" not in d.name and ".FAILED-" not in d.name] if out_dir.exists() else []
    if done:
        raise SystemExit(f"STOP: {OUT_REL} already holds {done}; the frozen model is applied once")
    raw_man = json.loads((ROOT / f"data/raw/{ACC}/download_manifest.json").read_text(encoding="utf-8"))
    sm_sha = _sha(ROOT / SM_REL)
    if sm_sha != raw_man["files"][Path(SM_REL).name]["current"]["sha256"]:
        raise SystemExit("STOP: Series Matrix SHA-256 differs from the download manifest")
    fit = _load("scripts/discovery_fit_gse63060.py", "discovery_fit")
    pop = pd.read_csv(ROOT / VAL_REL / "primary_population_log.tsv", sep="\t", dtype={"gsm": str, "chip": str})
    if (int((pop.group == "AD").sum()), int((pop.group == "CTL").sum())) != (EXPECTED["AD"], EXPECTED["CTL"]):
        raise SystemExit("STOP: GSE63061 population differs from the approved 139 AD / 133 CTL")
    table = pd.read_csv(ROOT / VAL_REL / "selection_table_G3.tsv", sep="\t", dtype=str)
    values, _ = parse_series_matrix(ROOT / SM_REL)
    values.columns = [str(c) for c in values.columns]
    genes = fit.gene_matrix(values[list(pop["gsm"])].astype(float), table)
    P = pd.DataFrame({"array": list(pop["gsm"]), "chip": pop["chip"].astype(str).to_numpy(), "y": pop["case_AD"].astype(int).to_numpy(),
                      "age": pop["age"].astype(float).to_numpy(), "sex_male": pop["sex_male"].astype(int).to_numpy()})
    extra = {"model": model_b, "settings": settings_b}
    files = ml.engine("apply", genes, P, {}, extra)
    if files != ml.engine("apply", genes, P, {}, extra):
        raise SystemExit("STOP: two applications are not byte-identical")
    files["external_label.json"] = (json.dumps({
        "cohort": ACC, "model_source": ml_rel, "final_model_sha256": summary["final_model_sha256"],
        "label": "related cohort, possible participant overlap with GSE63060 (H9); cross-platform (GPL6947 -> GPL10558); "
                 "applied once, no re-fitting or tuning; exploratory; not independent validation; DeLong intervals approximate; "
                 "no diagnostic-accuracy claim"}, indent=2, sort_keys=True) + "\n").encode()
    manifest = {"status": "Exploratory ML: frozen GSE63060 model applied once to GSE63061 (approved protocol, v7:603).",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/ml_apply_gse63061.py --version {version} --ml-version {ml_version}",
                "inputs": {SM_REL: sm_sha, f"{ml_rel}/manifest.json": _sha(ROOT / ml_rel / "manifest.json"),
                           f"{VAL_REL}/manifest.json": _sha(ROOT / VAL_REL / "manifest.json")},
                "determinism": {"runs_compared": 2, "identical": True,
                                "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}}
    return files, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--ml-version", required=True)
    a = ap.parse_args(argv)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / a.version, lambda s: produce(a.version, a.ml_version),
                                   require_venv=REQUIRE_VENV, executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
