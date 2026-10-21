#!/usr/bin/env python3
"""R8 amendment review: diagnosis-blind diagnostics of the sex probes in GSE63060 (decision support only).

Purpose: explain why R8 (as approved: D5 option (b), XIST ILMN_1764573 + 13 Y probes, Y axis = median of centred
Y probes) called 44 two-axis discordant arrays in QC Stage A v1 (reports/qc_stage_a/GSE63060/v1), so that the PI
can decide on an amendment. These diagnostics are POST HOC: R8 outputs were already visible (v6 §2.2).

Per sex probe and per source it reports level, spread, separation between recorded-female and recorded-male arrays
(difference in means; AUC), the probe's own two-class split (qc_r8.split_axis, the R8 split rule) and how many
arrays that single-probe split calls differently from recorded sex. Sources:
  * series_matrix — the D3 input as deposited (all 329 arrays);
  * log2_non_normalized — log2 of the deposited AVG_Signal (326 arrays whose column carries a barcode; the 3
    empty-header columns are left out because their identity is only inferred, phase2a report §5).
Inputs read: the two expression files (sex probes and, for the expression-level percentile, every probe of each
array), and only the gsm, array_barcode and gender columns of the eligibility log. Diagnosis is never read.
Nothing here changes R8, QC Stage A, any candidate or any rule. Runs under the code-identity lifecycle.
"""
from __future__ import annotations

import argparse
import csv
import gzip
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
from biomarker_project.qc_r8 import XIST_PROBE, Y_PROBES, split_axis  # noqa: E402

ACC = "GSE63060"
OUT_REL = f"reports/qc_stage_a/{ACC}/r8_diagnostics"
QC_REL = f"reports/qc_stage_a/{ACC}/v1"
ELIG_REL = f"reports/eligibility/{ACC}/v1"
SM_NAME, RAW_NAME = f"{ACC}_series_matrix.txt.gz", f"{ACC}_non-normalized.txt.gz"
SUFFIX = ".AVG_Signal"
SEX_MAP = {"Female": "F", "Male": "M"}
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_raw(path: Path, barcode_to_gsm: dict[str, str]) -> pd.DataFrame:
    """log2 of the non-normalized AVG_Signal for columns with a barcode header; probes x GSM."""
    df = pd.read_csv(path, sep="\t", index_col=0, dtype={0: str})
    keep = {c: barcode_to_gsm[c[: -len(SUFFIX)]] for c in df.columns
            if isinstance(c, str) and c.endswith(SUFFIX) and c[: -len(SUFFIX)] in barcode_to_gsm}
    out = df[list(keep)].rename(columns=keep).astype(float)
    if (out.to_numpy() <= 0).any():
        raise SystemExit("STOP: non-positive raw signal; log2 undefined")
    return np.log2(out)


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    """P(value in `pos` > value in `neg`) + 0.5·P(tie) (Mann–Whitney)."""
    allv = np.concatenate([pos, neg])
    ranks = pd.Series(allv).rank(method="average").to_numpy()
    r_pos = ranks[: len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def probe_rows(expr: pd.DataFrame, sex: pd.Series, source: str) -> list[dict]:
    pct = expr.rank(axis=0, pct=True)  # each probe's percentile within its array (expression-level indicator)
    rows = []
    for probe in [XIST_PROBE, *Y_PROBES]:
        if probe not in expr.index:
            rows.append({"source": source, "probe": probe, "gene": "XIST" if probe == XIST_PROBE else Y_PROBES[probe],
                         "present": False})
            continue
        v = expr.loc[probe]
        f, m = v[sex == "F"].to_numpy(float), v[sex == "M"].to_numpy(float)
        is_x = probe == XIST_PROBE
        sp = split_axis(v.to_numpy(float))
        if sp.degenerate:
            disc = None
        else:
            call = np.where(v.to_numpy(float) > sp.threshold, "F" if is_x else "M", "M" if is_x else "F")
            disc = int((call != sex.to_numpy()).sum())
        rows.append({"source": source, "probe": probe, "gene": "XIST" if is_x else Y_PROBES[probe], "present": True,
                     "n_arrays": int(v.size), "min": float(v.min()), "median": float(v.median()), "max": float(v.max()),
                     "median_within_array_percentile": float(pct.loc[probe].median()),
                     "mean_female": float(f.mean()), "mean_male": float(m.mean()), "sd_female": float(f.std(ddof=1)),
                     "sd_male": float(m.std(ddof=1)),
                     "expected_direction_difference": float((f.mean() - m.mean()) if is_x else (m.mean() - f.mean())),
                     "auc_expected_direction": auc(f, m) if is_x else auc(m, f),
                     "split_low_size": sp.low_size, "split_threshold": sp.threshold, "split_d_descriptive": sp.d_descriptive,
                     "split_degenerate": sp.degenerate, "split_calls_discordant_with_recorded_sex": disc})
    return rows


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    qc = ci.acceptance_problems(ROOT / QC_REL, "manifest.json", require_executed_code=True)
    el = ci.acceptance_problems(ROOT / ELIG_REL, "manifest.json", require_executed_code=True)
    if qc or el:
        probs.append(f"QC Stage A v1 or eligibility not accepted: {qc} {el}")
    raw_dir = ROOT / f"data/raw/{ACC}"
    man = json.loads((raw_dir / "download_manifest.json").read_text(encoding="utf-8"))["files"]
    prov = {}
    for n in (SM_NAME, RAW_NAME):
        h = _sha(raw_dir / n)
        prov[f"data/raw/{ACC}/{n}"] = {"sha256": h, "manifest_sha256": man[n]["current"]["sha256"]}
        if h != man[n]["current"]["sha256"]:
            probs.append(f"{n}: SHA-256 differs from the download manifest")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    with open(ROOT / ELIG_REL / "eligibility_log.tsv", encoding="utf-8", newline="") as fh:
        el_rows = [{"gsm": r["gsm"], "array_barcode": r["array_barcode"], "gender": r["gender"]}
                   for r in csv.DictReader(fh, delimiter="\t")]  # no diagnosis column is read
    gsms = [r["gsm"] for r in el_rows]
    sex = pd.Series([SEX_MAP.get(r["gender"]) for r in el_rows], index=gsms)
    sm, _ = parse_series_matrix(raw_dir / SM_NAME)
    sm.columns = [str(c) for c in sm.columns]
    sm = sm[gsms].astype(float)
    raw = read_raw(raw_dir / RAW_NAME, {r["array_barcode"]: r["gsm"] for r in el_rows})
    raw_gsms = [g for g in gsms if g in raw.columns]
    raw = raw[raw_gsms]

    def compute():
        rows = probe_rows(sm, sex.loc[gsms], "series_matrix") + probe_rows(raw, sex.loc[raw_gsms], "log2_non_normalized")
        scale = {"series_matrix": {q: float(np.quantile(sm.to_numpy(), q)) for q in (0, 0.25, 0.5, 0.75, 1)},
                 "log2_non_normalized": {q: float(np.quantile(raw.to_numpy(), q)) for q in (0, 0.25, 0.5, 0.75, 1)}}
        return (pd.DataFrame(rows).to_csv(sep="\t", index=False, float_format="%.10g", lineterminator="\n").encode(),
                (json.dumps({"value_quantiles": scale, "n_arrays": {"series_matrix": len(gsms), "log2_non_normalized": len(raw_gsms)},
                             "arrays_without_raw_column": sorted(set(gsms) - set(raw_gsms))}, indent=2, sort_keys=True) + "\n").encode())
    a, b = compute(), compute()
    if a != b:
        raise SystemExit("STOP: two runs are not byte-identical")
    files = {"r8_probe_diagnostics.tsv": a[0], "r8_scale_summary.json": a[1]}
    manifest = {"status": "R8 amendment review diagnostics for GSE63060 (post hoc; decision support only; changes nothing).",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/r8_diagnostics_gse63060.py --version {version}",
                "inputs": prov, "qc_stage_a_v1_manifest_sha256": _sha(ROOT / QC_REL / "manifest.json"),
                "validation": [{"check": "recorded sex mapped for every array", "pass": bool(sex.notna().all())},
                               {"check": "series matrix arrays = eligibility universe", "pass": list(sm.columns) == gsms}],
                "determinism": {"runs_compared": 2, "identical": True,
                                "output_sha256": {n: hashlib.sha256(x).hexdigest() for n, x in files.items()}}}
    if not all(c["pass"] for c in manifest["validation"]):
        raise SystemExit("STOP — VERIFICATION FAILED")
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
