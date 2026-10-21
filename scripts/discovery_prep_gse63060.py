#!/usr/bin/env python3
"""Tier B steps 6–9 for GSE63060: C2 duplicate log, primary-population log, identifiability checks M1–M8, G3 selection table.

  6  C2 expression duplicates (v6 §4): from QC Stage A (R9 A2 near-identical pairs; A3 referrals) — no expression is read here.
  7  Primary-population log: the approved exclusion list applied (SAP v7:625, approved 2026-10-18): AD + CTL arrays without
     any exclusion tier; covariates per the approved H1 specification (v7:604): age (linear), recorded sex, chip (unit).
  8  M1–M8 in ONE locked run (v5 §4.3–4.4) with the approved D7 values (v7:610): c1 = 3, c2 = 5, c3 = 10, eta = 1e-8,
     tau = max(n, p)·sigma_max·eps; decision checks M2–M4 give PROCEED or STOP; M1, M5–M8 are descriptive only.
  9  Selection table T_c for G3 (D6, v7:609): per Entrez gene, the constituent eligible A0 probes present in GSE63060, from
     the pinned illumina_a0/v2 table (annotation pin v1); D17: no additional expression filter.
No expression value is read and no model is fitted (the fit is Tier B step 10, scripts/discovery_fit_gse63060.py).
Runs under the code-identity lifecycle with executed-code verification; writes reports/discovery/GSE63060/prep_<version>/.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
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

ACC = "GSE63060"
OUT_REL = f"reports/discovery/{ACC}"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
PIN_REL = "reports/annotation_audit/annotation_pin/v1"
A0_REL = "reports/annotation_audit/illumina_a0/v2"
ELIG_REL, QCA_REL, QCB_REL = f"reports/eligibility/{ACC}/v1", f"reports/qc_stage_a/{ACC}/v1", f"reports/qc_stage_b/{ACC}/v1"
EXCLUSION_LIST_SHA256 = "28cf7aac65bc86b9416b853646708bd1c7531d7846eb3d85a35fb89ae6261e8d"
APPROVAL_MARKERS = ("GSE63060 exclusion-list approval §", EXCLUSION_LIST_SHA256, "**H1 analysis specification §",
                    "c₁ = 3 (minimum mixed units", "c₂ = 5", "c₃ = 10")
C1, C2, C3, ETA = 3, 5, 10.0, 1e-8
SITE_RX = re.compile(r"^(KPO|LDZ|PRG|THS|TLS|LND)")
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


def primary_population(elig: pd.DataFrame, excluded: set[str]) -> pd.DataFrame:
    pop = elig[elig["group"].isin(["AD", "CTL"]) & (elig["eligible_in_dataset_preqc"] == "True") & ~elig["gsm"].isin(excluded)].copy()
    pop["age"] = pd.to_numeric(pop["age"], errors="coerce")
    pop["sex_male"] = pop["gender"].map({"Male": 1, "Female": 0})
    pop["chip"] = pop["array_barcode"].str.split("_").str[0]
    pop["site"] = pop["participant_code"].map(lambda c: (SITE_RX.match(c or "") or [None])[0] or "undetermined")
    pop["case_AD"] = (pop["group"] == "AD").astype(int)
    return pop[["gsm", "array_barcode", "participant_code", "group", "case_AD", "age", "gender", "sex_male", "chip", "site"]].reset_index(drop=True)


def nuisance_matrix(pop: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """N (v5 §4.4 step 1): intercept, age centred and scaled, sex indicator, indicators for ALL chip levels."""
    age = pop["age"].to_numpy(float)
    cols = [np.ones(len(pop)), (age - age.mean()) / age.std(ddof=1), pop["sex_male"].to_numpy(float)]
    names = ["intercept", "age_scaled", "sex_male"]
    for chip in sorted(pop["chip"].unique()):
        cols.append((pop["chip"] == chip).to_numpy(float)); names.append(f"chip_{chip}")
    return np.column_stack(cols), names


def identifiability(pop: pd.DataFrame) -> dict:
    N, names = nuisance_matrix(pop)
    g = pop["case_AD"].to_numpy(float)
    n, p = N.shape
    U, s, Vt = np.linalg.svd(N, full_matrices=False)
    tau = max(n, p) * s.max() * np.finfo(float).eps
    r = int((s > tau).sum())
    Q = U[:, :r]
    if np.unique(g).size < 2:
        return {"decision": "STOP", "reason": "group constant (not estimable)", "r_N": r}
    resid = g - Q @ (Q.T @ g)
    E = float(resid @ resid / ((g - g.mean()) @ (g - g.mean())))
    vif = float("inf") if E <= 0 else 1.0 / E
    tab = pd.crosstab(pop["chip"], pop["group"]).reindex(columns=["AD", "CTL"], fill_value=0)
    mixed = tab[(tab["AD"] > 0) & (tab["CTL"] > 0)]
    m2 = {"mixed_units": int(len(mixed)), "AD_on_mixed_units": int(mixed["AD"].sum()), "CTL_on_mixed_units": int(mixed["CTL"].sum())}
    estimable = E > ETA
    stops = []
    if not estimable:
        stops.append("M3: not estimable (E <= eta)")
    if m2["mixed_units"] < C1:
        stops.append(f"M2: mixed units {m2['mixed_units']} < c1 = {C1}")
    if min(m2["AD_on_mixed_units"], m2["CTL_on_mixed_units"]) < C2:
        stops.append(f"M2: a group on mixed units < c2 = {C2}")
    if vif > C3:
        stops.append(f"M4: VIF {vif:.4g} > c3 = {C3}")
    null = Vt[r:].T if r < p else np.zeros((p, 0))
    aliasing = [{n_: float(v) for n_, v in zip(names, col) if abs(v) > 1e-8} for col in null.T]
    return {"decision": "STOP" if stops else "PROCEED", "stop_reasons": stops,
            "decision_checks": {"M2": m2, "M3_E": E, "M3_estimable": bool(estimable), "M4_VIF": vif},
            "thresholds": {"c1": C1, "c2": C2, "c3": C3, "eta": ETA, "tau": tau},
            "descriptive": {"n": n, "p": p, "r_N": r, "M5_residual_df": n - r - 1,
                            "M6_singleton_units": sorted(tab.index[tab.sum(axis=1) == 1].tolist()),
                            "condition_number_retained": float(s[0] / s[r - 1]), "aliasing_null_space_dim": p - r},
            "aliasing": aliasing, "nuisance_columns": names}


def selection_table(a0: pd.DataFrame) -> pd.DataFrame:
    e = a0[(a0["cohort"] == ACC) & (a0["a0_class"] == "eligible") & (a0["in_series_matrix"] == "yes")]
    t = (e.groupby("a0_gene_id")["probe_id"].apply(lambda s: ";".join(sorted(s))).reset_index()
         .rename(columns={"a0_gene_id": "entrez_gene_id", "probe_id": "constituent_probes"}))
    t["n_probes"] = t["constituent_probes"].str.count(";") + 1
    return t.sort_values("entrez_gene_id", key=lambda c: c.astype(int)).reset_index(drop=True)


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in (PIN_REL, ELIG_REL, QCA_REL, QCB_REL):
        p = ci.acceptance_problems(ROOT / rel, "manifest.json", require_executed_code=True)
        if p:
            probs.append(f"{rel} not accepted: {p}")
    if _sha(ROOT / QCB_REL / "exclusion_list.tsv") != EXCLUSION_LIST_SHA256:
        probs.append("exclusion list differs from the approved list")
    sap = (ROOT / SAP_REL).read_text(encoding="utf-8")
    missing = [m for m in APPROVAL_MARKERS if m not in sap]
    if missing:
        probs.append(f"approvals not found in the SAP: {missing}")
    pin = json.loads((ROOT / PIN_REL / "annotation_pin_record.json").read_text(encoding="utf-8"))
    a0_sha = _sha(ROOT / A0_REL / "a0_probe_classification.tsv")
    if pin["upstream"]["illumina_a0"]["tables_sha256"]["a0_probe_classification.tsv"] != a0_sha:
        probs.append("A0 table differs from the annotation pin")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    elig = pd.read_csv(ROOT / ELIG_REL / "eligibility_log.tsv", sep="\t", dtype=str, keep_default_na=False)
    excluded = set(pd.read_csv(ROOT / QCB_REL / "exclusion_list.tsv", sep="\t", dtype=str)["gsm"])
    a2 = pd.read_csv(ROOT / QCA_REL / "qc_a2_pairs.tsv", sep="\t", dtype=str)
    audit = pd.read_csv(ROOT / QCA_REL / "qc_audit.tsv", sep="\t", dtype=str, keep_default_na=False)
    a0 = pd.read_csv(ROOT / A0_REL / "a0_probe_classification.tsv", sep="\t", dtype=str, keep_default_na=False)

    def compute():
        pop = primary_population(elig, excluded)
        ident = identifiability(pop)
        c2log = {"tier_b_step": 6, "source": "C2 (R9 A2 pairs and A3 referrals, QC Stage A v1)", "a2_pairs": int(len(a2)),
                 "r9_referred_d18": int((audit["r9_outcome"] == "referred_d18").sum()),
                 "status": "complete: no C2 candidates (no D-3/D-4)" if len(a2) == 0 and not (audit["r9_outcome"] == "referred_d18").any()
                 else "C2 candidates found: review required"}
        m1 = pd.crosstab(pop["chip"], pop["group"]).reindex(columns=["AD", "CTL"], fill_value=0).reset_index()
        m7 = pd.crosstab(pop["chip"], pop["site"]).reset_index()
        m8 = (pop.groupby(["chip", "group"]).agg(n=("gsm", "size"), mean_age=("age", "mean"), n_male=("sex_male", "sum")).reset_index())
        m8g = pop.groupby("group").agg(n=("gsm", "size"), mean_age=("age", "mean"), sd_age=("age", "std"), n_male=("sex_male", "sum")).reset_index()
        files = {"c2_duplicate_review_log.json": (json.dumps(c2log, indent=2, sort_keys=True) + "\n").encode(),
                 "primary_population_log.tsv": _tsv(pop), "identifiability_checks.json": (json.dumps(ident, indent=2, sort_keys=True) + "\n").encode(),
                 "m1_group_by_chip.tsv": _tsv(m1), "m7_chip_by_site.tsv": _tsv(m7), "m8_age_sex_by_chip_group.tsv": _tsv(m8),
                 "m8_age_sex_by_group.tsv": _tsv(m8g), "selection_table_G3.tsv": _tsv(selection_table(a0))}
        return files, pop, ident, c2log
    f1, pop, ident, c2log = compute()
    if f1 != compute()[0]:
        raise SystemExit("STOP: two runs are not byte-identical")
    sel = selection_table(a0)
    checks = [("primary population is 145 AD + 60 CTL (approved list)", (int((pop.group == "AD").sum()), int((pop.group == "CTL").sum())) == (145, 60)),
              ("complete covariates (R2-COV) for every primary array", bool(pop[["age", "sex_male"]].notna().all().all())),
              ("C2 step complete", c2log["status"].startswith("complete")),
              ("G3 table: 25,305 eligible present probes over 17,425 genes (A0 counts)", (int(sel["n_probes"].sum()), len(sel)) == (25305, 17425))]
    manifest = {"status": f"Tier B steps 6–9 for {ACC}. Identifiability decision: {ident['decision']}. No expression read; no model fitted.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/discovery_prep_gse63060.py --version {version}",
                "inputs": {rel: _sha(ROOT / rel / "manifest.json") for rel in (PIN_REL, ELIG_REL, QCA_REL, QCB_REL)}
                | {"a0_probe_classification_sha256": a0_sha, "exclusion_list_sha256": EXCLUSION_LIST_SHA256, "sap_sha256": _sha(ROOT / SAP_REL)},
                "identifiability_decision": ident["decision"], "stop_reasons": ident.get("stop_reasons", []),
                "validation": [{"check": n, "pass": ok} for n, ok in checks],
                "determinism": {"runs_compared": 2, "identical": True, "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in f1.items()}}}
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED:\n  " + "\n  ".join(failed))
    return f1, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    a = ap.parse_args(argv)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / f"prep_{a.version}", lambda s: produce(a.version),
                                   require_venv=REQUIRE_VENV, executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
