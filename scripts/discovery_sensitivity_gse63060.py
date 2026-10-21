#!/usr/bin/env python3
"""GSE63060 discovery sensitivity analyses approved under D16 (SAP v7:619; definitions v6 §10.1, sample sets v7 §5.3).

All are prespecified, all are reported, none replaces the primary analysis, and none locks a signature (v6 §10.1).
Each sensitivity design passes the v5 §4.4 identifiability procedure with the approved D7 values (c1 = 3, c2 = 5,
c3 = 10) before it is fitted; STOP is recorded as "not estimable / insufficient". The fit is the primary limma
specification (lmFit + eBayes(trend = TRUE), D8 runner) on the GENE-LEVEL family (G3 unless the analysis changes it),
compared descriptively with the primary gene-level fit (reports/discovery/GSE63060/fit_v1).

Runnable here:  S1a (age >= 65), S1b (age 61–88), S3a (site added), S3b (site instead of chip), S4 (exclude the "M"-coded
AD samples; undocumented coding assumption; not E1), S5a (exclude F1, k = 3), S5d (exclude F2), S5e (exclude F3 ambiguous),
S5f (re-include arrays whose only tier is Q1), S5g (exclude F1 k = 3, F2, F3), S7 (mean-expression filter at the 25th / 50th
percentile over all D2-eligible arrays, without diagnosis; D17), S8 (G1: highest-mean eligible probe over the primary
population; D6-B), S12 (Sood "included in case -control study" = yes subset), S16 (re-include D-3/D-4: none exist),
S-R8m (remove the 46 arrays whose two strongest Y markers disagree with recorded sex).
Not run (recorded with the reason): S2 (spline basis not specified), S5b/S5c (k = 2.5 and 4 not approved), S6 (estimated
array weights: runner support and basis invariance unverified), S9 (2008 BGX annotation not available), S10 (re-normalization
not approved), S11 (D21 not approved), S13–S15 (other cohorts).
Runs under the code-identity lifecycle with executed-code verification; writes reports/discovery/GSE63060/sensitivity_<version>/.
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
PREP_REL, FIT_REL = f"reports/discovery/{ACC}/prep_v1", f"reports/discovery/{ACC}/fit_v1"
ELIG_REL, QCA_REL, QCB_REL = f"reports/eligibility/{ACC}/v1", f"reports/qc_stage_a/{ACC}/v1", f"reports/qc_stage_b/{ACC}/v1"
R8D_REL = f"reports/qc_stage_a/{ACC}/r8_diagnostics/v2"
A0_REL = "reports/annotation_audit/illumina_a0/v2"
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
APPROVAL_MARKERS = ("S1–S16 with the §5.3 sample sets, as defined; plus S-R8m", "c₁ = 3 (minimum mixed units")
C1, C2, C3, ETA, Q = 3, 5, 10.0, 1e-8, 0.05
CODE_RX = r"^(?:KPO|LDZ|PRG|THS|TLS|LND)([AMC]|ADC|CTL|MCI)"
NOT_RUN = {"S2": "3-df spline basis (type, knots) not specified in the SAP", "S5b": "k = 2.5 not approved (D22 row 5)",
           "S5c": "k = 4 not approved (D22 row 5)", "S6": "estimated array weights: runner support and basis invariance unverified (v5:379-380)",
           "S9": "2008 BGX annotation resource not available", "S10": "re-normalization not approved", "S11": "D21 not approved",
           "S13": "GSE140829 (D11)", "S14": "GSE140829 (D18 option c)", "S15": "GSE99039 (D13)"}
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


def nuisance(pop: pd.DataFrame, unit: str, extra: tuple[str, ...] = ()) -> np.ndarray:
    age = pop["age"].to_numpy(float)
    cols = [np.ones(len(pop)), (age - age.mean()) / age.std(ddof=1), pop["sex_male"].to_numpy(float)]
    for f in (unit, *extra):
        for lvl in sorted(pop[f].astype(str).unique()):
            cols.append((pop[f].astype(str) == lvl).to_numpy(float))
    return np.column_stack(cols)


def identify(pop: pd.DataFrame, unit: str, extra: tuple[str, ...] = ()) -> dict:
    """v5 §4.4 with the approved D7 values; returns the decision and, on PROCEED, the full-rank design basis."""
    g = pop["case_AD"].to_numpy(float)
    if np.unique(g).size < 2:
        return {"decision": "STOP", "stop_reasons": ["group constant"]}
    N = nuisance(pop, unit, extra)
    n, p = N.shape
    U, s, _ = np.linalg.svd(N, full_matrices=False)
    r = int((s > max(n, p) * s.max() * np.finfo(float).eps).sum())
    Q = U[:, :r]
    res = g - Q @ (Q.T @ g)
    E = float(res @ res / ((g - g.mean()) @ (g - g.mean())))
    tab = pd.crosstab(pop[unit].astype(str), pop["group"]).reindex(columns=["AD", "CTL"], fill_value=0)
    mixed = tab[(tab["AD"] > 0) & (tab["CTL"] > 0)]
    stops = []
    if not E > ETA:
        stops.append("not estimable")
    if len(mixed) < C1:
        stops.append(f"mixed units {len(mixed)} < c1")
    if min(int(mixed["AD"].sum()), int(mixed["CTL"].sum())) < C2:
        stops.append("a group on mixed units < c2")
    if E > 0 and 1 / E > C3:
        stops.append(f"VIF {1 / E:.3g} > c3")
    out = {"decision": "STOP" if stops else "PROCEED", "stop_reasons": stops, "n": n, "n_AD": int(g.sum()), "n_CTL": int(n - g.sum()),
           "E": E, "VIF": (1 / E if E > 0 else float("inf")), "mixed_units": int(len(mixed)), "r_N": r, "residual_df": n - r - 1}
    if not stops:
        X = np.column_stack([Q, g])
        out["design"] = Design(X, [f"nuisance_q{i + 1}" for i in range(r)] + ["AD_vs_CTL"], "AD_vs_CTL")
    return out


def gene_matrix_g3(values: pd.DataFrame, table: pd.DataFrame, keep_probes: set[str] | None = None) -> pd.DataFrame:
    rows = {}
    for gid, probes in zip(table["entrez_gene_id"], table["constituent_probes"]):
        pr = [p for p in probes.split(";") if keep_probes is None or p in keep_probes]
        if pr:
            rows[str(gid)] = values.loc[pr].mean(axis=0)
    return pd.DataFrame(rows).T


def gene_matrix_g1(values: pd.DataFrame, table: pd.DataFrame, selection_samples: list[str]) -> pd.DataFrame:
    rows = {}
    for gid, probes in zip(table["entrez_gene_id"], table["constituent_probes"]):
        pr = sorted(probes.split(";"))
        means = values.loc[pr, selection_samples].mean(axis=1)
        best = means[means == means.max()].index.min()  # highest unweighted mean over S_c; ties -> probe ID ascending
        rows[str(gid)] = values.loc[best]
    return pd.DataFrame(rows).T


def compare(primary: pd.DataFrame, sens: pd.DataFrame) -> dict:
    m = primary.merge(sens, on="feature_id", suffixes=("_p", "_s"))
    sig_p = m["q_value_bh_p"] < Q
    same_sign = np.sign(m["estimate_p"]) == np.sign(m["estimate_s"])
    return {"n_genes_tested": int(len(sens)), "n_q_lt_0.05": int((sens["q_value_bh"] < Q).sum()),
            "n_up_AD": int(((sens["q_value_bh"] < Q) & (sens["estimate"] > 0)).sum()),
            "n_down_AD": int(((sens["q_value_bh"] < Q) & (sens["estimate"] < 0)).sum()),
            "spearman_t_vs_primary": float(m["t_statistic_p"].rank().corr(m["t_statistic_s"].rank())),
            "primary_significant_genes_compared": int(sig_p.sum()),
            "of_which_same_sign": int((sig_p & same_sign).sum()),
            "of_which_same_sign_and_q_lt_0.05": int((sig_p & same_sign & (m["q_value_bh_s"] < Q)).sum())}


def build_sets(pop, elig, audit, excl, r8calls):
    flags = audit.set_index("array_id")["flags"].fillna("")
    f1 = {g for g, f in flags.items() if "F1(k=3)" in f}
    f2 = {g for g, f in flags.items() if "F2" in f.split(";")}
    f3 = {g for g, f in flags.items() if f.split(";").count("F3")}
    letter = elig.set_index("gsm")["participant_code"].str.extract(CODE_RX)[0]
    m_coded_ad = {g for g in pop.loc[pop["group"] == "AD", "gsm"] if letter.get(g) == "M"}
    sood = set(elig.loc[elig["sood_flag_recorded_not_used_R12"] == "yes", "gsm"])
    q1_only = set(excl.loc[excl["exclusion_tiers"] == "Q1", "gsm"])
    r8m = set(r8calls.loc[r8calls["both_y_markers_disagree_with_recorded"] == True, "gsm"])  # noqa: E712
    base = pop.copy()
    return {
        "S1a": base[base["age"] >= 65], "S1b": base[(base["age"] >= 61) & (base["age"] <= 88)],
        "S3a": base, "S3b": base, "S4": base[~base["gsm"].isin(m_coded_ad)],
        "S5a": base[~base["gsm"].isin(f1)], "S5d": base[~base["gsm"].isin(f2)], "S5e": base[~base["gsm"].isin(f3)],
        "S5f": "plus_q1", "S5g": base[~base["gsm"].isin(f1 | f2 | f3)], "S7_p25": base, "S7_p50": base, "S8": base,
        "S12": base[base["gsm"].isin(sood)], "S16": base, "S-R8m": base[~base["gsm"].isin(r8m)],
    }, {"F1": f1, "F2": f2, "F3": f3, "M_coded_AD": m_coded_ad, "Q1_only": q1_only, "R8m": r8m}


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in (PREP_REL, FIT_REL, ELIG_REL, QCA_REL, QCB_REL, R8D_REL):
        p = ci.acceptance_problems(ROOT / rel, "manifest.json", require_executed_code=True)
        if p:
            probs.append(f"{rel} not accepted: {p}")
    sap = (ROOT / SAP_REL).read_text(encoding="utf-8")
    if any(m not in sap for m in APPROVAL_MARKERS):
        probs.append("D16 / D7 approvals not found in the SAP")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    env = check_environment()
    pop = pd.read_csv(ROOT / PREP_REL / "primary_population_log.tsv", sep="\t", dtype={"gsm": str, "chip": str, "site": str})
    table = pd.read_csv(ROOT / PREP_REL / "selection_table_G3.tsv", sep="\t", dtype=str)
    elig = pd.read_csv(ROOT / ELIG_REL / "eligibility_log.tsv", sep="\t", dtype=str, keep_default_na=False)
    audit = pd.read_csv(ROOT / QCA_REL / "qc_audit.tsv", sep="\t", dtype=str, keep_default_na=False)
    excl = pd.read_csv(ROOT / QCB_REL / "exclusion_list.tsv", sep="\t", dtype=str, keep_default_na=False)
    r8calls = pd.read_csv(ROOT / R8D_REL / "r8_marker_calls_series_matrix.tsv", sep="\t")
    primary = pd.read_csv(ROOT / FIT_REL / "gene_level_results.tsv", sep="\t", dtype={"feature_id": str})
    values, _ = parse_series_matrix(ROOT / SM_REL)
    values.columns = [str(c) for c in values.columns]
    values = values.astype(float)
    sets, members = build_sets(pop, elig, audit, excl, r8calls)
    # S5f: primary + arrays whose only tier is Q1 (their covariates from the eligibility log)
    q1 = elig[elig["gsm"].isin(members["Q1_only"])].copy()
    q1_pop = pd.DataFrame({"gsm": q1["gsm"], "group": q1["group"], "case_AD": (q1["group"] == "AD").astype(int),
                           "age": pd.to_numeric(q1["age"]), "sex_male": q1["gender"].map({"Male": 1, "Female": 0}),
                           "chip": q1["array_barcode"].str.split("_").str[0]})
    q1_pop["site"] = elig.set_index("gsm").loc[q1_pop["gsm"], "participant_code"].str.extract(r"^(KPO|LDZ|PRG|THS|TLS|LND)")[0].fillna("undetermined").to_numpy()
    sets["S5f"] = pd.concat([pop, q1_pop], ignore_index=True)
    eligible_gsms = list(elig.loc[elig["eligible_in_dataset_preqc"] == "True", "gsm"])
    probe_mean = values[eligible_gsms].mean(axis=1)  # over all D2-eligible arrays; no diagnosis (D17)
    elig_probes = {p for s in table["constituent_probes"] for p in s.split(";")}
    filt = {k: set(probe_mean[probe_mean >= probe_mean.quantile(q)].index) for k, q in (("S7_p25", 0.25), ("S7_p50", 0.5))}

    def run_all():
        results, summary = {}, {}
        for name, sp in sets.items():
            sp = sp.reset_index(drop=True)
            unit, extra = ("site", ()) if name == "S3b" else ("chip", ("site",) if name == "S3a" else ())
            idf = identify(sp, unit, extra)
            same_as_primary = name not in ("S3a", "S3b", "S7_p25", "S7_p50", "S8") and sorted(sp["gsm"]) == sorted(pop["gsm"])
            entry = {k: v for k, v in idf.items() if k != "design"} | {"unit": unit, "extra_factors": list(extra)}
            if same_as_primary:
                entry["status"] = "sample set equals the primary population; not refitted (identical to the primary)"
            elif idf["decision"] == "STOP":
                entry["status"] = "not estimable / insufficient (v5 §4.4)"
            else:
                cols = list(sp["gsm"])
                if name.startswith("S7"):
                    genes = gene_matrix_g3(values[cols], table, filt[name])
                    entry["probes_retained_of_eligible"] = [len(filt[name] & elig_probes), len(elig_probes)]
                elif name == "S8":
                    genes = gene_matrix_g1(values[cols], table, cols)
                else:
                    genes = gene_matrix_g3(values[cols], table)
                run = fit_feature_limma(genes.to_numpy(), list(genes.index), cols, idf["design"])
                run.results["data_origin"] = "GEO"
                results[name] = run.results
                entry["status"] = "fitted"
                entry["comparison_with_primary"] = compare(primary, run.results)
            summary[name] = entry
        return results, summary
    r1, s1 = run_all()
    r2, s2 = run_all()
    files = {f"gene_level_{k}.tsv": _tsv(v) for k, v in r1.items()}
    if files != {f"gene_level_{k}.tsv": _tsv(v) for k, v in r2.items()} or json.dumps(s1, sort_keys=True, default=str) != json.dumps(s2, sort_keys=True, default=str):
        raise SystemExit("STOP: two runs are not byte-identical")
    report = {"run": s1, "not_run": NOT_RUN, "set_members_n": {k: len(v) for k, v in members.items()},
              "s7_threshold_basis": "mean over all D2-eligible arrays (329), no diagnosis (D17)"}
    files["sensitivity_summary.json"] = (json.dumps(report, indent=2, sort_keys=True, default=float) + "\n").encode()
    manifest = {"status": "GSE63060 discovery sensitivity analyses (D16). Prespecified; none replaces the primary; no signature locked. "
                          "Provisional: SAP not approved.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/discovery_sensitivity_gse63060.py --version {version}",
                "inputs": {rel: _sha(ROOT / rel / "manifest.json") for rel in (PREP_REL, FIT_REL, ELIG_REL, QCA_REL, QCB_REL, R8D_REL)},
                "r_environment": {k: v for k, v in env.items() if k.startswith("found_")},
                "validation": [{"check": "every approved analysis is either run or listed as not run", "pass": True}],
                "determinism": {"runs_compared": 2, "identical": True, "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}}
    return files, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    a = ap.parse_args(argv)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / f"sensitivity_{a.version}", lambda s: produce(a.version),
                                   require_venv=REQUIRE_VENV, executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
