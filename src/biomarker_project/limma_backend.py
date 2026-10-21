"""Python wrapper for the D8-approved limma runner (R/limma_de.R), invoked as a separate Rscript step.

Method (D8): limma::lmFit followed by limma::eBayes(trend = TRUE, robust = FALSE), other eBayes
arguments at their defaults. Output maps onto the existing RESULT_COLUMNS schema:
  estimate     = case coefficient (logFC)
  std_error    = moderated SE = sqrt(s2.post) * stdev.unscaled
  ci_low/high  = topTable(confint = 0.95): estimate -/+ qt(0.975, df.total) * std_error
  t_statistic  = moderated t;  df = df.total;  p_value = 2 * pt(-|t|, df.total)
  q_value_bh   = BH across every feature in the fit (limma adj.P.Val; cross-checked in Python)
Moderation details (df_prior, s2_prior, s2_post, ave_expr, sigma, ...) are returned separately.

The runner refuses to execute (exit status 3) unless R, Bioconductor, limma, renv, BiocManager and
statmod match APPROVED_PINS. Rscript runs with the project root as working directory so that the
project .Rprofile activates the renv library.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .differential_expression import RESULT_COLUMNS, Design, benjamini_hochberg

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT_ROOT / "R" / "limma_de.R"
APPROVED_PINS = {"R": "4.6.1", "bioc": "3.23", "limma": "3.68.5", "renv": "1.3.1",
                 "BiocManager": "1.30.27", "statmod": "1.5.2"}
METHOD = "limma::lmFit + limma::eBayes(trend = TRUE, robust = FALSE); topTable(confint = 0.95, adjust.method = 'BH')"
MODERATION_COLUMNS = ["feature_id", "ave_expr", "sigma", "df_residual", "df_prior", "s2_prior", "s2_post", "stdev_unscaled"]


class LimmaEnvironmentError(RuntimeError):
    pass


@dataclass
class LimmaRun:
    results: pd.DataFrame        # RESULT_COLUMNS
    moderation: pd.DataFrame     # MODERATION_COLUMNS
    info: dict[str, str]         # versions, paths, method
    session_info: list[str]


def find_rscript() -> str:
    path = shutil.which("Rscript")
    if not path:
        raise LimmaEnvironmentError("Rscript not found on PATH (D8 requires R 4.6.1)")
    return path


def _env() -> dict[str, str]:
    env = dict(os.environ)
    env.setdefault("LC_ALL", "en_US.UTF-8")
    env.pop("R_LIBS", None)
    env.pop("R_LIBS_USER", None)
    return env


def _pin_args(pins: dict[str, str]) -> list[str]:
    return [a for k in APPROVED_PINS for a in (f"--{k}", pins[k])]


def _read_info(path: Path) -> tuple[dict[str, str], list[str]]:
    info, session = {}, []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            key, _, val = line.partition("\t")
            if key == "sessionInfo":
                session.append(val)
            else:
                info[key] = val
    return info, session


def _run(args: list[str], info_path: Path) -> tuple[dict[str, str], list[str]]:
    proc = subprocess.run([find_rscript(), "--no-save", "--no-restore", str(RUNNER), *args, "--info", str(info_path)],
                          cwd=PROJECT_ROOT, env=_env(), capture_output=True, text=True)
    info, session = _read_info(info_path)
    if proc.returncode == 3:
        raise LimmaEnvironmentError("R environment does not match the approved D8 pins: "
                                    + " ".join(l for l in proc.stderr.splitlines() if "VERSION" in l or "MISSING" in l))
    if proc.returncode != 0:
        raise LimmaEnvironmentError(f"limma runner failed (exit {proc.returncode}): {proc.stderr.strip()[-2000:]}")
    return info, session


def check_environment(pins: dict[str, str] | None = None) -> dict[str, str]:
    """Return found versions and paths; raise LimmaEnvironmentError if any pin does not match."""
    pins = pins or APPROVED_PINS
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_limma_") as tmp:
        info, _ = _run(["--check", *_pin_args(pins)], Path(tmp) / "info.tsv")
    for k, v in pins.items():                      # independent Python-side confirmation
        if info.get(f"found_{k}") != v:
            raise LimmaEnvironmentError(f"{k}: found {info.get(f'found_{k}')}, pinned {v}")
    return info


def fit_feature_limma(values: np.ndarray, feature_ids: list[str], sample_ids: list[str], design: Design,
                      ci_level: float = 0.95, pins: dict[str, str] | None = None) -> LimmaRun:
    pins = pins or APPROVED_PINS
    Y = np.asarray(values, dtype=float)
    if Y.shape != (len(feature_ids), len(sample_ids)) or design.matrix.shape[0] != len(sample_ids):
        raise ValueError("values, feature ids, sample ids and design rows are inconsistent")
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_limma_") as tmp:
        tmp = Path(tmp)
        pd.DataFrame(Y, index=pd.Index(feature_ids, name="feature_id"), columns=sample_ids).to_csv(
            tmp / "E.tsv", sep="\t", float_format="%.17g")
        pd.DataFrame(design.matrix, index=pd.Index(sample_ids, name="sample_id"), columns=design.columns).to_csv(
            tmp / "X.tsv", sep="\t", float_format="%.17g")
        info, session = _run(["--fit", *_pin_args(pins), "--expression", str(tmp / "E.tsv"), "--design",
                              str(tmp / "X.tsv"), "--coef", design.coefficient, "--confint", repr(ci_level),
                              "--out", str(tmp / "out.tsv")], tmp / "info.tsv")
        raw = pd.read_csv(tmp / "out.tsv", sep="\t", dtype={"feature_id": str})
    if list(raw["feature_id"]) != list(feature_ids):
        raise LimmaEnvironmentError("limma output feature order differs from the input")
    q_python = benjamini_hochberg(raw["p_value"].to_numpy())
    if not np.allclose(q_python, raw["q_value_bh"].to_numpy(), rtol=1e-12, atol=0):
        raise LimmaEnvironmentError("limma BH q-values disagree with the Python BH implementation")
    res = raw.rename(columns={"df_total": "df"})
    res["estimable"] = np.isfinite(res["t_statistic"])
    order = res.assign(_abs_t=-res["t_statistic"].abs()).sort_values(
        ["p_value", "_abs_t", "feature_id"], kind="mergesort", na_position="last").index
    res.loc[order, "rank"] = np.arange(1, len(res) + 1)
    res["rank"] = res["rank"].astype(int)
    res["data_origin"] = None          # set by the caller
    return LimmaRun(results=res[RESULT_COLUMNS], moderation=raw[MODERATION_COLUMNS], info=info, session_info=session)
