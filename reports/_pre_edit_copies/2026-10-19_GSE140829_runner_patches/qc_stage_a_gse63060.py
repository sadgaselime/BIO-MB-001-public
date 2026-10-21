#!/usr/bin/env python3
"""Tier B step 5: QC Stage A (R8 sex consistency, R9 array outliers) for GSE63060 — candidates recorded only.

Authorization: PI ruling 2026-10-18 (option A; v7:625): QC Stage A may COMPUTE AND RECORD candidate exclusions for
GSE63060. No exclusion is applied until the exclusion-list approval step (v5:123-129) and D16 are decided, and the
Stage A outputs are not usable downstream until then (qc_stage_a: stage_a_outputs_usable_downstream = False).

Inputs (verified first):
  * GSE63060_series_matrix.txt.gz values AS DEPOSITED (D3; no normalization or transformation), restricted to the
    R1 universe in eligibility-log order;
  * reports/eligibility/GSE63060/v1/eligibility_log.tsv: ONLY the gsm and gender columns are read. Diagnosis is never
    read or passed to QC (QC is diagnosis-blind);
Preconditions: annotation pin (step 2), eligibility (step 3) and C1 duplicate review (step 4, complete) accepted.
Rules: as implemented in src/biomarker_project/qc_r8.py (D5 option (b), D5 conventions) and qc_r9.py (D22 P3, k = 3),
orchestrated by qc_stage_a.run_qc_stage_a. Runs under the code-identity lifecycle with executed-code verification;
writes reports/qc_stage_a/GSE63060/<version>/ (never overwritten).
"""
from __future__ import annotations

import argparse
import csv
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
from biomarker_project.expression_adjudication import parse_series_matrix  # noqa: E402
from biomarker_project.qc_stage_a import QCCohortInput, run_qc_stage_a  # noqa: E402

ACC = "GSE63060"
OUT_REL = f"reports/qc_stage_a/{ACC}"
PIN_REL = "reports/annotation_audit/annotation_pin/v1"
ELIG_REL = f"reports/eligibility/{ACC}/v1"
DUP_REL = f"reports/duplicate_review/{ACC}/c1_v1"
SM_NAME = f"{ACC}_series_matrix.txt.gz"
EXPECTED_SHAPE = (38323, 329)  # D3 (v7:606): 329 GSM columns x 38,323 probes
SEX_MAP = {"Female": "F", "Male": "M"}
AUTHORIZATION = ("PI ruling 2026-10-18 (option A; recorded at v7:625): QC Stage A may compute and record candidate "
                 "exclusions for GSE63060; none applied until the exclusion-list approval step and D16 are decided")
CONFIG = {
    "GSE63060": {"EXPECTED_SHAPE": EXPECTED_SHAPE, "AUTHORIZATION": AUTHORIZATION},
    "GSE63061": {"EXPECTED_SHAPE": (32049, 388),  # Series Matrix: 388 GSM columns x 32,049 probes (Phase 1 audit)
                 "AUTHORIZATION": ("PI instruction 2026-10-19 (GSE63061 go-ahead; recorded at v7:625): QC Stage A may compute and "
                                   "record candidate exclusions for GSE63061 under the same QC policies as GSE63060; none applied "
                                   "until the GSE63061 exclusion list is approved")},
}


def use(acc: str) -> None:
    global ACC, OUT_REL, ELIG_REL, DUP_REL, SM_NAME, EXPECTED_SHAPE, AUTHORIZATION
    ACC, OUT_REL, ELIG_REL = acc, f"reports/qc_stage_a/{acc}", f"reports/eligibility/{acc}/v1"
    DUP_REL, SM_NAME = f"reports/duplicate_review/{acc}/c1_v1", f"{acc}_series_matrix.txt.gz"
    EXPECTED_SHAPE, AUTHORIZATION = CONFIG[acc]["EXPECTED_SHAPE"], CONFIG[acc]["AUTHORIZATION"]


DIAGNOSIS_COLUMNS = {"group", "geo_status", "status", "diagnosis", "primary_contrast_preqc", "r5_category"}
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(type(o))


def _tsv(df: pd.DataFrame) -> bytes:
    return df.to_csv(sep="\t", index=False, float_format="%.17g", lineterminator="\n").encode("utf-8")


def preconditions(root: Path) -> tuple[dict, list[str]]:
    prov, probs = {}, []
    raw = root / f"data/raw/{ACC}"
    exp = json.loads((raw / "download_manifest.json").read_text(encoding="utf-8"))["files"][SM_NAME]["current"]["sha256"]
    h = _sha(raw / SM_NAME)
    prov[f"data/raw/{ACC}/{SM_NAME}"] = {"sha256": h, "manifest_sha256": exp}
    if h != exp:
        probs.append("Series Matrix SHA-256 differs from the download manifest")
    for rel, label in ((PIN_REL, "annotation pin (step 2)"), (ELIG_REL, "eligibility (step 3)"), (DUP_REL, "C1 duplicate review (step 4)")):
        p = ci.acceptance_problems(root / rel, "manifest.json", require_executed_code=True)
        if p:
            probs.append(f"{label} not accepted: {p}")
        else:
            prov[rel] = {"manifest_sha256": _sha(root / rel / "manifest.json")}
    if not probs:
        log = json.loads((root / DUP_REL / "duplicate_review_log_c1.json").read_text(encoding="utf-8"))
        if not log["status"].startswith("complete"):
            probs.append(f"C1 duplicate review not complete: {log['status']}")
    return prov, probs


def load_inputs(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    with open(root / ELIG_REL / "eligibility_log.tsv", encoding="utf-8", newline="") as fh:
        rows = [{"gsm": r["gsm"], "gender": r["gender"]} for r in csv.DictReader(fh, delimiter="\t")]  # no diagnosis
    gsms = [r["gsm"] for r in rows]
    values, _meta = parse_series_matrix(root / f"data/raw/{ACC}" / SM_NAME)
    values.columns = [str(c) for c in values.columns]
    if sorted(values.columns) != sorted(gsms):
        raise SystemExit("STOP: Series Matrix columns differ from the eligibility universe")
    expr = values[gsms].astype(float)
    samples = pd.DataFrame({"sample_id": gsms, "sex": [SEX_MAP.get(r["gender"], np.nan) for r in rows], "data_origin": "GEO"})
    return expr, samples


def serialize(res) -> dict[str, bytes]:
    return {"qc_cohort_status.tsv": _tsv(res.cohorts), "qc_audit.tsv": _tsv(res.audit),
            "qc_a2_pairs.tsv": _tsv(res.a2_pairs), "qc_candidate_exclusions.tsv": _tsv(res.candidate_exclusions),
            "qc_r8_axes.json": (json.dumps(res.r8_axes, indent=2, sort_keys=True, default=_json_default) + "\n").encode(),
            "qc_r9_summary.json": (json.dumps(res.r9_summaries, indent=2, sort_keys=True, default=_json_default) + "\n").encode()}


def produce(version: str) -> tuple[dict, dict]:
    prov, probs = preconditions(ROOT)
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    expr, samples = load_inputs(ROOT)
    cohort = QCCohortInput(ACC, expr, samples, purpose="Tier B step 5 QC Stage A on the R1 universe (diagnosis-blind)",
                           real_data_authorization=AUTHORIZATION)
    r1, r2 = run_qc_stage_a([cohort]), run_qc_stage_a([cohort])
    f1, f2 = serialize(r1), serialize(r2)
    if f1 != f2:
        raise SystemExit("STOP: two runs are not byte-identical")
    st = r1.cohorts.iloc[0]
    checks = [
        (f"expression shape is {EXPECTED_SHAPE[0]} probes x {EXPECTED_SHAPE[1]} arrays", tuple(expr.shape) == EXPECTED_SHAPE),
        ("arrays in eligibility-log order", list(expr.columns) == list(samples["sample_id"])),
        ("recorded sex mapped for every array", bool(samples["sex"].notna().all())),
        ("QC inputs carry no diagnosis column", DIAGNOSIS_COLUMNS.isdisjoint(set(samples.columns) | set(r1.audit.columns))),
        ("no exclusion applied", not bool(r1.audit["exclusion_applied"].any())),
        ("Stage A outputs marked not usable downstream", not bool(st["stage_a_outputs_usable_downstream"])),
    ]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED (nothing accepted):\n  " + "\n  ".join(failed))
    manifest = {
        "status": f"Tier B step 5 QC Stage A for {ACC}: candidates COMPUTED AND RECORDED ONLY; no exclusion applied; "
                  "outputs not usable downstream until the exclusion-list approval step and D16 are decided.",
        "authorization": AUTHORIZATION,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": f".venv/bin/python -I scripts/qc_stage_a_gse63060.py --version {version}",
        "inputs": prov, "n_probes": int(expr.shape[0]), "n_arrays": int(expr.shape[1]),
        "non_finite_values": int((~np.isfinite(expr.to_numpy())).sum()),
        "cohort_status": {k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in st.to_dict().items()},
        "n_candidate_exclusions": int(len(r1.candidate_exclusions)),
        "validation": [{"check": n, "pass": ok} for n, ok in checks],
        "determinism": {"runs_compared": 2, "identical": True,
                        "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in f1.items()}},
    }
    return f1, json.loads(json.dumps(manifest, default=_json_default))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--accession", default="GSE63060", choices=sorted(CONFIG))
    a = ap.parse_args(argv)
    if a.accession != ACC:
        use(a.accession)
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
