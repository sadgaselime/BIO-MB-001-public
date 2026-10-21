#!/usr/bin/env python3
"""Tier B step 5 (Stage B): GSE63060 descriptive QC review and the RULE-APPLIED exclusion list (v5 §3.4–3.5).

Stage B (v5:268–273): the Stage A per-array table joined to chip and deposited diagnosis AS COUNTS ONLY; no inferential
test; Stage B cannot change any exclusion. Exclusions follow the approved policies mechanically (D22 rows 1–6, v7:625;
tiers and precedence, v7 §5.1–5.2):
  P1  outside the primary contrast: non-contrast labels (R3/R4: MCI), R5-category labels, R11 (never in the universe);
  P2  R2-ID / D18 D-1 exclusions (none for GSE63060: C1 review complete, no candidates);
  P3  R9 numerical failure (none in QC Stage A v1);
  Q1  R8 two-axis discordant, where R8 is "completed — informative" (D22 row 1; lifted only by S5f);
  F1/F2/F3 flags are retained and listed (never exclusions).
The list is RULE-APPLIED and AWAITS the PI's exclusion-list approval (v5:123–129: verifying that the prespecified rules
were applied correctly). Nothing here fits a model or links expression to diagnosis.
Runs under the code-identity lifecycle with executed-code verification; writes reports/qc_stage_b/GSE63060/<version>/.
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

ACC = "GSE63060"
OUT_REL = f"reports/qc_stage_b/{ACC}"
QC_REL = f"reports/qc_stage_a/{ACC}/v1"
ELIG_REL = f"reports/eligibility/{ACC}/v1"
DUP_REL = f"reports/duplicate_review/{ACC}/c1_v1"
CONFIG = ("GSE63060", "GSE63061", "GSE140829")  # GSE63061: same policies (PI instruction 2026-10-19); GSE140829 (v7:605)


def use(acc: str) -> None:
    global ACC, OUT_REL, QC_REL, ELIG_REL, DUP_REL
    ACC, OUT_REL, QC_REL = acc, f"reports/qc_stage_b/{acc}", f"reports/qc_stage_a/{acc}/v1"
    ELIG_REL, DUP_REL = f"reports/eligibility/{acc}/v1", f"reports/duplicate_review/{acc}/c1_v1"


STATUS = "RULE-APPLIED — AWAITING PI EXCLUSION-LIST APPROVAL (v5:123–129); not applied to any model"
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _tsv(df: pd.DataFrame) -> bytes:
    return df.to_csv(sep="\t", index=False, lineterminator="\n").encode("utf-8")


REVIEW_REL = "reports/duplicate_review/GSE140829/c1_review_2026-10-19"   # PI C1 review (v7:621), GSE140829 only
REVIEW_MARKER = "GSE140829 C1 review §"


def c1_review(root: Path, dup_rel: str) -> tuple[dict | None, list[str]]:
    """The recorded GSE140829 C1 review, verified against the C1 output it reviews and the SAP record."""
    p = root / REVIEW_REL / "c1_review_decision.json"
    if not p.is_file():
        return None, ["GSE140829 C1 review record missing"]
    rec = json.loads(p.read_text(encoding="utf-8"))
    sums = (root / REVIEW_REL / "SHA256SUMS").read_text(encoding="utf-8").split()
    sap = (root / "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md").read_text(encoding="utf-8")
    probs = []
    if sums[:2] != [_sha(p), "c1_review_decision.json"]:
        probs.append("C1 review record differs from its SHA256SUMS")
    if rec.get("c1_manifest_sha256") != _sha(root / dup_rel / "manifest.json"):
        probs.append("C1 review record does not refer to this C1 output")
    if not rec.get("status", "").startswith("complete") or REVIEW_MARKER not in sap:
        probs.append("C1 review not complete or not recorded in the SAP (v7:621)")
    return (rec if not probs else None), probs


def build(elig: pd.DataFrame, audit: pd.DataFrame, r8_status: str, q3: frozenset = frozenset()) -> dict[str, pd.DataFrame]:
    m = elig.merge(audit, left_on="gsm", right_on="array_id", how="left", validate="one_to_one")
    if m["array_id"].isna().any():
        raise SystemExit("STOP: an eligible array has no QC Stage A row")
    # unit: the chip from the barcode; for GSE140829 the approved unit is the deposited batch (v7:605, 614)
    m["chip"] = ("batch_" + m["batch"].astype(str)) if "batch" in m.columns else m["array_barcode"].str.split("_").str[0]
    tiers, reasons = [], []
    for _, r in m.iterrows():
        t, why = [], []
        if r["eligible_in_dataset_preqc"] != "True":
            t.append("P2"); why.append("R2-ID")
        if r["r5_category"] != "mapped":
            t.append("P1"); why.append(f"R5 ({r['r5_category']})")
        elif r["group"] not in ("AD", "CTL"):
            t.append("P1"); why.append(f"non-contrast label {r['group']} (R3/R4)")
        if r["r9_outcome"] == "numerical_failure":
            t.append("P3"); why.append("R9 numerical failure")
        if r["r8_category"] == "discordant_two_axis" and r8_status == "completed — informative":
            t.append("Q1"); why.append("R8 two-axis discordant (D22 row 1)")
        if r["gsm"] in q3:
            t.append("Q3"); why.append("D-2 replicate without identifiable partner (D-2 option (c); primary excluded, S14 only)")
        tiers.append(";".join(t)); reasons.append("; ".join(why))
    m["exclusion_tiers"], m["reasons"] = tiers, reasons
    m["in_primary_population"] = m["exclusion_tiers"] == ""
    m["retained_flags"] = m["flags"].fillna("")
    excl = m.loc[m["exclusion_tiers"] != "", ["gsm", "array_barcode", "group", "exclusion_tiers", "reasons", "retained_flags"]].copy()
    excl["status"] = STATUS
    flags = m.loc[(m["retained_flags"] != "") & m["in_primary_population"], ["gsm", "group", "retained_flags"]].copy()
    by_chip = (m.groupby("chip").agg(n=("gsm", "size"), r8_discordant_two_axis=("r8_category", lambda s: int((s == "discordant_two_axis").sum())),
                                     r8_ambiguous=("r8_category", lambda s: int((s == "ambiguous").sum())),
                                     r9_flagged=("r9_outcome", lambda s: int((s == "flagged").sum())),
                                     r9_numerical_failure=("r9_outcome", lambda s: int((s == "numerical_failure").sum())))
               .reset_index())
    by_dx = (pd.crosstab(m["group"], m["r8_category"]).join(pd.crosstab(m["group"], m["r9_outcome"]), rsuffix="_r9")
             .reset_index().rename(columns={"group": "deposited_group"}))
    primary = m.loc[m["in_primary_population"], "group"].value_counts().reindex(["AD", "CTL"], fill_value=0)
    summary = pd.DataFrame([
        {"quantity": "R1 universe", "n": len(m)},
        {"quantity": "excluded (any tier)", "n": int((m["exclusion_tiers"] != "").sum())},
        {"quantity": "P1 (outside primary contrast)", "n": int(m["exclusion_tiers"].str.contains("P1").sum())},
        {"quantity": "P2", "n": int(m["exclusion_tiers"].str.contains("P2").sum())},
        {"quantity": "P3", "n": int(m["exclusion_tiers"].str.contains("P3").sum())},
        {"quantity": "Q1", "n": int(m["exclusion_tiers"].str.contains("Q1").sum())},
        {"quantity": "Q1 among AD/CTL", "n": int((m["exclusion_tiers"].str.contains("Q1") & m["group"].isin(["AD", "CTL"])).sum())},
        *([{"quantity": "Q3 (D-2 option (c))", "n": int(m["exclusion_tiers"].str.contains("Q3").sum())},
           {"quantity": "Q3 among AD/CTL", "n": int((m["exclusion_tiers"].str.contains("Q3") & m["group"].isin(["AD", "CTL"])).sum())}]
          if q3 else []),
        {"quantity": "primary population AD (proposed, pending approval)", "n": int(primary["AD"])},
        {"quantity": "primary population CTL (proposed, pending approval)", "n": int(primary["CTL"])},
        {"quantity": "retained flagged arrays in proposed primary population", "n": len(flags)},
    ])
    return {"exclusion_list": excl, "retained_flags": flags, "counts_by_chip": by_chip, "counts_by_diagnosis": by_dx, "summary": summary}


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    for rel in (QC_REL, ELIG_REL, DUP_REL):
        p = ci.acceptance_problems(ROOT / rel, "manifest.json", require_executed_code=True)
        if p:
            probs.append(f"{rel} not accepted: {p}")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    elig = pd.read_csv(ROOT / ELIG_REL / "eligibility_log.tsv", sep="\t", dtype=str, keep_default_na=False)
    audit = pd.read_csv(ROOT / QC_REL / "qc_audit.tsv", sep="\t", dtype=str, keep_default_na=False)
    r8_status = json.loads((ROOT / QC_REL / "manifest.json").read_text(encoding="utf-8"))["cohort_status"]["r8_status"]
    q3 = frozenset()
    if ACC == "GSE140829":   # D-2 option (c) via the recorded C1 review (v7:621)
        rec, rp = c1_review(ROOT, DUP_REL)
        if rp:
            raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(rp))
        q3 = frozenset(rec["decisions"]["D-2_option_c_Q3"]["gsms"])
    t1, t2 = build(elig, audit, r8_status, q3), build(elig, audit, r8_status, q3)
    files = {f"{k}.tsv": _tsv(v) for k, v in t1.items()}
    if files != {f"{k}.tsv": _tsv(v) for k, v in t2.items()}:
        raise SystemExit("STOP: two runs are not byte-identical")
    s = dict(zip(t1["summary"]["quantity"], t1["summary"]["n"]))
    checks = [("every eligible array has a QC Stage A row", True),
              ("primary population + excluded = universe", s["excluded (any tier)"] + s["primary population AD (proposed, pending approval)"]
               + s["primary population CTL (proposed, pending approval)"] == s["R1 universe"])]
    manifest = {"status": f"Tier B step 5 Stage B for {ACC}: descriptive counts and the rule-applied exclusion list. {STATUS}.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/qc_stage_b_gse63060.py --version {version}",
                "inputs": {rel: {"manifest_sha256": _sha(ROOT / rel / "manifest.json")} for rel in (QC_REL, ELIG_REL, DUP_REL)},
                "r8_cohort_status": r8_status, "summary": s,
                "validation": [{"check": n, "pass": ok} for n, ok in checks],
                "determinism": {"runs_compared": 2, "identical": True,
                                "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}}
    if not all(ok for _, ok in checks):
        raise SystemExit("STOP — VERIFICATION FAILED")
    return files, manifest


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
