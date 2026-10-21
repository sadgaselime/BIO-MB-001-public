"""End-to-end synthetic pipeline: generate -> validate -> sample-set rules -> feature-level models
-> BH adjustment -> results, report and provenance.

SYNTHETIC DATA ONLY. Outputs demonstrate the data flow and output schema; they are not
biological findings and say nothing about any real cohort.

Output directory layout (all analytical files are deterministic for a given config and seed;
only provenance.json carries timestamps and environment details):
  inputs/synthetic_expression.csv     features x samples (log2-like synthetic values)
  inputs/synthetic_samples.csv        sample metadata as generated (shuffled row order)
  inputs/synthetic_planted_truth.csv  planted effects per feature
  validation.json                     structural input checks
  sample_flow.csv                     every sample: group, analysed or removed, rule, reason
  de_results.csv                      one row per feature (schema: RESULT_COLUMNS)
  planted_signal_recovery.json        comparison of results with the planted truth
  qc/                                 (if qc.enabled) QC Stage A on synthetic cohorts: cohort statuses,
                                      per-array audit with reason codes, A2 pairs, candidate
                                      exclusions (NOT applied), R8 axes and R9 summaries
  report.md                           human-readable summary with synthetic-data warnings
  provenance.json                     config, seed, versions, paths, SHA-256 of every output
"""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from . import __version__
from .differential_expression import RESULT_COLUMNS, build_design, fit_feature_ols
from .limma_backend import fit_feature_limma
from .input_validation import validate_inputs
from .reporting import write_json
from .qc_fixtures import build_fixtures
from .qc_stage_a import QCCohortInput, run_qc_stage_a
from .sample_policy import DEFERRED_RULES, ContrastLabelRestriction, apply_rules
from .synthetic_data import GROUPS, SyntheticSpec, generate_synthetic_cohort

MARKER = "SYNTHETIC_RUN_MARKER"
WARNING = ("SYNTHETIC DATA — NOT BIOLOGICAL EVIDENCE. Every value in this run was simulated from a "
           "known generative model. No real cohort data were used; no result here may be reported "
           "as a finding about Alzheimer's disease or any GEO dataset.")
FLOAT_FORMAT = "%.10g"
ANALYSIS_DEFAULTS = {"case": "AD", "control": "CTL", "covariates": ["age", "sex"],
                     "covariate_levels": {"sex": ["F", "M"]}, "fdr_level": 0.05, "ci_level": 0.95,
                     "method": "ols"}   # "ols" (numpy reference) or "limma" (D8: lmFit + eBayes(trend=TRUE, robust=FALSE))
METHOD_TEXT = {
    "ols": ("Per-feature ordinary least squares on one shared design (intercept, case indicator, covariates); "
            "ordinary t statistic with n − p residual df; two-sided p-values; confidence intervals b ± t·SE; "
            "Benjamini–Hochberg adjustment across all estimable features. Numpy reference implementation, kept "
            "for comparison with the D8 limma method."),
    "limma": ("D8-approved method: limma::lmFit on one shared design (intercept, case indicator, covariates), "
              "then limma::eBayes(trend = TRUE, robust = FALSE) with all other arguments at their defaults; "
              "moderated t with df.total; two-sided p-values; 95% CI from topTable(confint = 0.95), i.e. "
              "coefficient ± qt(0.975, df.total) × moderated SE; Benjamini–Hochberg across all features in the fit. "
              "Run via R/limma_de.R in the pinned renv environment (R 4.6.1, Bioconductor 3.23, limma 3.68.5)."),
}
QC_DEFAULTS = {"enabled": False, "boundary_fixtures": True}
MAIN_COHORT = "SYN-MAIN"


def load_config(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}
    unknown = set(cfg) - {"run_name", "seed", "output_dir", "synthetic", "analysis", "qc"}
    if unknown:
        raise ValueError(f"unknown top-level config key(s): {sorted(unknown)}")
    unknown = set(cfg.get("analysis") or {}) - set(ANALYSIS_DEFAULTS)
    if unknown:
        raise ValueError(f"unknown analysis key(s): {sorted(unknown)}")
    unknown = set(cfg.get("qc") or {}) - set(QC_DEFAULTS)
    if unknown:
        raise ValueError(f"unknown qc key(s): {sorted(unknown)}")
    return cfg


def resolve_config(cfg: dict[str, Any], seed: int | None = None) -> dict[str, Any]:
    synth = dict(cfg.get("synthetic") or {})
    if seed is not None:
        synth["seed"] = seed
    elif "seed" in cfg:
        synth.setdefault("seed", cfg["seed"])
    spec = SyntheticSpec(**synth)
    analysis = {**ANALYSIS_DEFAULTS, **(cfg.get("analysis") or {})}
    qc = {**QC_DEFAULTS, **(cfg.get("qc") or {})}
    return {"run_name": cfg.get("run_name", "synthetic_demo"), "synthetic": spec.to_dict(), "analysis": analysis,
            "qc": qc}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _prepare_out_dir(out_dir: Path) -> None:
    """Start from a clean directory. Only a directory previously written by this pipeline
    (it contains the marker file) is cleared; anything else is refused."""
    if out_dir.exists() and any(out_dir.iterdir()):
        if not (out_dir / MARKER).is_file():
            raise FileExistsError(f"{out_dir} exists, is not empty and was not created by the synthetic pipeline")
        shutil.rmtree(out_dir)
    (out_dir / "inputs").mkdir(parents=True, exist_ok=True)
    (out_dir / MARKER).write_text(WARNING + "\n", encoding="utf-8")


def _write_df(df: pd.DataFrame, path: Path, index: bool = False) -> None:
    df.to_csv(path, index=index, float_format=FLOAT_FORMAT, lineterminator="\n")


def _recovery(results: pd.DataFrame, truth: pd.DataFrame, fdr: float) -> dict[str, Any]:
    m = results.merge(truth[["feature_id", "planted_group_effect_ad_minus_ctl"]], on="feature_id")
    planted = m["planted_group_effect_ad_minus_ctl"] != 0
    called = m["q_value_bh"] < fdr
    tp = int((planted & called).sum())
    fp = int((~planted & called).sum())
    sign_ok = int((planted & called & (np.sign(m["estimate"]) == np.sign(m["planted_group_effect_ad_minus_ctl"]))).sum())
    pe = m.loc[planted]
    covered = int(((pe["ci_low"] <= pe["planted_group_effect_ad_minus_ctl"])
                   & (pe["planted_group_effect_ad_minus_ctl"] <= pe["ci_high"])).sum())
    null = m.loc[~planted]
    null_cov = int(((null["ci_low"] <= 0) & (0 <= null["ci_high"])).sum())
    return {
        "note": "Evaluation against the planted synthetic truth; meaningful only for this simulation.",
        "fdr_level": fdr, "n_features": int(len(m)), "n_planted_group_features": int(planted.sum()),
        "n_called_q_below_level": int(called.sum()), "true_positives": tp, "false_positives": fp,
        "observed_false_discovery_proportion": (fp / int(called.sum())) if int(called.sum()) else None,
        "sensitivity": tp / int(planted.sum()) if int(planted.sum()) else None,
        "true_positives_with_correct_sign": sign_ok,
        "planted_effects_inside_ci": covered,
        "null_features_ci_covering_zero": null_cov, "n_null_features": int(len(null)),
    }


def _md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(FLOAT_FORMAT % v if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(lines)


def _render_qc(qc) -> list[str]:
    if qc is None:
        return []
    main = qc.audit[qc.audit["cohort_id"] == MAIN_COHORT]
    status = qc.cohorts[["cohort_id", "r8_status", "r9_status", "r9_stop_stage", "va_gate_open", "gated_analyses"]]
    outcome = qc.audit.groupby(["cohort_id", "r9_outcome"]).size().unstack(fill_value=0).reset_index()
    return [
        "## QC Stage A (synthetic cohorts only)", "",
        "R8 under approved D5 option (b) with the D5 conventions (v5:149-202; v7:133, 608); R9 under the approved "
        "D22 P3 definition (v7:351), run separately per cohort. **QC Stage A remains blocked for real cohorts** "
        "(v7:625). Candidate exclusions below are **not applied** (exclusion-list approval scope unresolved, "
        "v5:123-129); flags and D18 referrals never exclude.", "",
        "### Cohort statuses and V-A gate", "", _md_table(status.fillna("—")), "",
        "### R9 outcomes per cohort (arrays)", "", _md_table(outcome), "",
        f"### Main cohort ({MAIN_COHORT}) R8 categories", "",
        _md_table(main.groupby("r8_category").size().rename("n").reset_index()), "",
        "### Candidate primary exclusions (PROPOSED — NOT APPLIED)", "",
        _md_table(qc.candidate_exclusions[["cohort_id", "array_id", "candidate_tiers", "r8_reason_code", "r9_reason_code"]])
        if len(qc.candidate_exclusions) else "None.", "",
        "### Boundary fixtures", "",
        "\n".join(f"- **{r.cohort_id}**: {r.purpose}" for r in qc.cohorts.itertuples() if r.cohort_id != MAIN_COHORT)
        or "Not run.", "",
    ]


def _render_report(cfg: dict, counts: pd.DataFrame, rule_summary: list[dict], design_cols: list[str],
                   results: pd.DataFrame | None, recovery: dict | None, validation: dict, qc=None) -> str:
    a = cfg["analysis"]
    if results is None:
        return "\n".join([f"# Synthetic pipeline run: {cfg['run_name']}", "", f"> **{WARNING}**", "",
                          "## Synthetic cohort counts", "", _md_table(counts), "", *_render_qc(qc),
                          "## Differential expression: not assessable — R8 (V-A gate closed, v7:139)", "",
                          f"> {WARNING}", ""])
    top = results.sort_values("rank").head(15)[
        ["rank", "feature_id", "estimate", "ci_low", "ci_high", "std_error", "t_statistic", "p_value", "q_value_bh"]]
    n_sig = int((results["q_value_bh"] < a["fdr_level"]).sum())
    out = [
        f"# Synthetic pipeline run: {cfg['run_name']}", "",
        f"> **{WARNING}**", "",
        "## Run configuration", "",
        f"- Seed: `{cfg['synthetic']['seed']}`",
        f"- Contrast: `{a['case']}` − `{a['control']}` (feature-level)",
        f"- Covariates: {', '.join(a['covariates']) or 'none'}; design columns: {', '.join(f'`{c}`' for c in design_cols)}",
        f"- FDR level: {a['fdr_level']}; CI level: {a['ci_level']}",
        "- Full configuration, software versions and file checksums: `provenance.json`.", "",
        "## Synthetic cohort counts", "", _md_table(counts), "",
        "## Sample-set rules applied", "",
        _md_table(pd.DataFrame(rule_summary)), "",
        f"Input validation: **{validation['status']}** ({len(validation['checks'])} checks; `validation.json`).", "",
        *_render_qc(qc),
        "## Method", "",
        METHOD_TEXT[a["method"]], "",
        f"## Results (synthetic): {n_sig} of {len(results)} features with BH q < {a['fdr_level']}", "",
        "**Population: QC-unfiltered contrast set — not the primary population.** The primary-population log "
        "cannot start while the exclusion-list approval scope is unresolved (v5:123-129; v7:552), so QC candidate "
        "exclusions (Q1, P3) are included here; see `de_population.json`.", "",
        "Top 15 by p-value. `estimate` is the adjusted synthetic AD − CTL difference on the simulated log2-like scale.", "",
        _md_table(top), "",
        "## Planted-signal recovery (simulation check only)", "",
        "\n".join(f"- {k}: {v}" for k, v in recovery.items() if k != "note"), "",
        "## Deferred pending scientific approval (not implemented in this run)", "",
        "\n".join(f"- **{d.name}**: {d.status} ({d.reference})" for d in DEFERRED_RULES), "",
        f"> {WARNING}", "",
    ]
    return "\n".join(out)


def run_synthetic_pipeline(config: dict[str, Any], out_dir: Path, *, seed: int | None = None,
                           config_path: str | None = None, argv: list[str] | None = None) -> dict[str, Any]:
    """Run the full synthetic pipeline into `out_dir` (cleared first). Returns a summary dict."""
    out_dir = Path(out_dir)
    cfg = resolve_config(config, seed=seed)
    a = cfg["analysis"]
    spec = SyntheticSpec(**cfg["synthetic"])
    _prepare_out_dir(out_dir)

    cohort = generate_synthetic_cohort(spec)
    _write_df(cohort.expression, out_dir / "inputs" / "synthetic_expression.csv", index=True)
    _write_df(cohort.samples, out_dir / "inputs" / "synthetic_samples.csv")
    _write_df(cohort.truth, out_dir / "inputs" / "synthetic_planted_truth.csv")

    # Re-read from disk so the analysis consumes exactly the files that are recorded in provenance.
    expression = pd.read_csv(out_dir / "inputs" / "synthetic_expression.csv", index_col="feature_id")
    samples = pd.read_csv(out_dir / "inputs" / "synthetic_samples.csv", dtype={"sample_id": str, "group": str, "sex": str})
    aligned, validation = validate_inputs(
        expression, samples, allowed_groups=list(GROUPS), contrast=(a["case"], a["control"]),
        covariates=list(a["covariates"]), covariate_levels=a.get("covariate_levels") or {})
    write_json(out_dir / "validation.json", validation.to_dict())

    rules = [ContrastLabelRestriction(case=a["case"], control=a["control"])]
    analysed, removed, rule_summary = apply_rules(aligned, rules)
    flow = aligned[["sample_id", "group"]].merge(removed[["sample_id", "rule", "reason", "tier"]], on="sample_id", how="left")
    flow.insert(2, "analysed", flow["rule"].isna())

    qc = None
    gate_open = True
    if cfg["qc"]["enabled"]:
        qc = _run_qc(cfg, expression, aligned, out_dir)
        main = qc.cohorts.set_index("cohort_id").loc[MAIN_COHORT]
        gate_open = bool(main["va_gate_open"])
        audit = qc.audit[qc.audit["cohort_id"] == MAIN_COHORT].rename(columns={"array_id": "sample_id"})
        flow = flow.merge(audit[["sample_id", "r8_category", "r9_outcome", "candidate_tiers", "flags", "d18_review",
                                 "exclusion_applied"]], on="sample_id", how="left")
        if not gate_open:
            flow["analysed"] = False
    _write_df(flow.sort_values("sample_id", kind="mergesort"), out_dir / "sample_flow.csv")

    if not gate_open:
        write_json(out_dir / "de_not_assessable.json", {
            "status": f"not assessable — R8 (cohort {MAIN_COHORT} R8 status: {main['r8_status']})",
            "rule": "V-A: gated analyses start only when R8 is 'completed — informative' or 'not applicable' (v7:139)"})
        return _finish(cfg, spec, out_dir, config_path, argv, qc, None, None, analysed, rule_summary, aligned, validation)

    q = flow.get("candidate_tiers", pd.Series("", index=flow.index)).fillna("")
    write_json(out_dir / "de_population.json", {
        "population": f"{a['case']} + {a['control']} contrast set after the contrast-label rule only (QC-unfiltered)",
        "is_primary_population": False,
        "reason": ("synthetic demonstration; the primary population (Base - Q1 - ..., v7:375) is not formed because "
                   "the exclusion-list approval scope is unresolved (v5:123-129; v7:552)"),
        "n_analysed": int(len(analysed)),
        "q1_candidates_included": sorted(flow.loc[flow["analysed"] & q.str.contains("Q1"), "sample_id"]),
        "p3_candidates_included": sorted(flow.loc[flow["analysed"] & q.str.contains("P3"), "sample_id"]),
    })

    design = build_design(analysed, group_col="group", case=a["case"], control=a["control"], covariates=list(a["covariates"]))
    values = expression[list(analysed["sample_id"])].to_numpy(dtype=float)
    r_env = None
    if a["method"] == "limma":
        run = fit_feature_limma(values, list(expression.index), list(analysed["sample_id"]), design,
                                ci_level=a["ci_level"])
        results = run.results
        _write_df(run.moderation, out_dir / "de_limma_moderation.csv")
        r_env = {"info": run.info, "sessionInfo": run.session_info}
    elif a["method"] == "ols":
        results = fit_feature_ols(values, list(expression.index), design, ci_level=a["ci_level"])
    else:
        raise ValueError(f"unknown analysis.method {a['method']!r}")
    results["data_origin"] = "SYNTHETIC"
    results = results[RESULT_COLUMNS].sort_values("rank", kind="mergesort")
    _write_df(results, out_dir / "de_results.csv")

    recovery = _recovery(results, cohort.truth, a["fdr_level"])
    write_json(out_dir / "planted_signal_recovery.json", recovery)
    return _finish(cfg, spec, out_dir, config_path, argv, qc, design, results, analysed, rule_summary, aligned,
                   validation, recovery, r_env)


def _run_qc(cfg: dict, expression: pd.DataFrame, aligned: pd.DataFrame, out_dir: Path):
    """QC Stage A on the main synthetic cohort (all deposited arrays, diagnosis ignored; v5:141) and,
    optionally, on the deterministic boundary fixtures. Writes qc/*. Candidate exclusions are not applied."""
    cohorts = [QCCohortInput(MAIN_COHORT, expression, aligned[["sample_id", "sex", "data_origin"]],
                             purpose="main synthetic cohort (all arrays incl. non-contrast labels)")]
    if cfg["qc"]["boundary_fixtures"]:
        cohorts += build_fixtures(cfg["synthetic"]["seed"])
    qc = run_qc_stage_a(cohorts)
    d = out_dir / "qc"
    d.mkdir(exist_ok=True)
    _write_df(qc.cohorts, d / "qc_cohort_status.csv")
    _write_df(qc.audit, d / "qc_array_audit.csv")
    _write_df(qc.a2_pairs, d / "qc_a2_pairs.csv")
    _write_df(qc.candidate_exclusions, d / "qc_candidate_exclusions_NOT_APPLIED.csv")
    write_json(d / "qc_details.json", {"warning": WARNING, "r8_axes": qc.r8_axes, "r9_summaries": qc.r9_summaries})
    return qc


def _finish(cfg, spec, out_dir, config_path, argv, qc, design, results, analysed, rule_summary, aligned, validation,
            recovery=None, r_env=None) -> dict[str, Any]:
    a = cfg["analysis"]
    counts = (aligned.groupby("group").size().rename("n_generated").to_frame()
              .join(analysed.groupby("group").size().rename("n_analysed")).fillna(0).astype(int)
              .reindex(list(GROUPS)).fillna(0).astype(int).reset_index())
    (out_dir / "report.md").write_text(
        _render_report(cfg, counts, rule_summary, design.columns if design else [], results, recovery,
                       validation.to_dict(), qc), encoding="utf-8")

    outputs = sorted(p for p in out_dir.rglob("*") if p.is_file() and p.name != "provenance.json")
    analytic = {str(p.relative_to(out_dir)): _sha256(p) for p in outputs}
    provenance = {
        "warning": WARNING,
        "pipeline": "biomarker_project.synthetic_pipeline", "package_version": __version__,
        "run_name": cfg["run_name"], "seed": spec.seed, "resolved_config": cfg,
        "config_path": config_path, "argv": argv if argv is not None else sys.argv,
        "output_dir": str(out_dir.resolve()),
        "inputs": "generated in-run from the seed (no external input files)",
        "software": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
                     "pyyaml": yaml.__version__, "platform": platform.platform()},
        "started_or_written_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "design_columns": design.columns if design else None, "n_analysed": int(len(analysed)),
        "residual_df": int(results["df"].iloc[0]) if results is not None else None,
        "de_method": cfg["analysis"]["method"],
        "r_environment": r_env,
        "output_sha256": analytic,
        "analytic_digest": hashlib.sha256(json.dumps(analytic, sort_keys=True).encode()).hexdigest(),
    }
    write_json(out_dir / "provenance.json", provenance)
    return {"out_dir": str(out_dir), "analytic_digest": provenance["analytic_digest"], "output_sha256": analytic,
            "n_features": int(len(results)) if results is not None else 0, "n_analysed": int(len(analysed)),
            "n_q_below_level": int((results["q_value_bh"] < a["fdr_level"]).sum()) if results is not None else None,
            "recovery": recovery, "qc_cohorts": qc.cohorts if qc else None}
