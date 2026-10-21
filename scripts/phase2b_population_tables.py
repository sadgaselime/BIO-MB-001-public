#!/usr/bin/env python3
"""Phase 2B: descriptive tables for the 'included in case -control study' GEO sample annotation.

Example:
    python scripts/phase2b_population_tables.py --accessions GSE63060 GSE63061 --version v1

Reads only the derived phenotype tables (data/processed/<ACC>/phenotype_table.tsv, built from
the GEO sample records). Produces counts and simple descriptive summaries (no hypothesis tests,
no expression data). Writes to reports/phase2b/<FIRST_ACCESSION>/<VERSION>/ and never
overwrites an existing version.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FLAG = "char:included in case -control study"
_CODE = [re.compile(r"^(KPO|LDZ|PRG|THS|TLS|LND)([AMC])\d+$"), re.compile(r"^(KPO|LDZ|PRG|THS|TLS|LND)(ADC|CTL|MCI)\d+$")]
_GROUP = {"A": "AD", "ADC": "AD", "C": "CTL", "CTL": "CTL", "M": "MCI", "MCI": "MCI"}


def code_group(participant_code: str) -> str | None:
    """Recruitment group encoded in an AddNeuroMed participant code, or None if the code has no group letter.

    Examples: 'KPOM0014' -> 'MCI', 'LDZCTL016' -> 'CTL', 'LND0174' -> None, 'DCR00088' -> None.
    This is an observed naming pattern, not a documented coding scheme.
    """
    for rx in _CODE:
        m = rx.match(participant_code or "")
        if m:
            return _GROUP[m.group(2)]
    return None


def annotate(ph: pd.DataFrame) -> pd.DataFrame:
    ph = ph.copy()
    ph["age_num"] = pd.to_numeric(ph["char:age"], errors="coerce")
    ph["code_group"] = ph["description"].map(code_group)
    ph["code_concordant"] = ph["code_group"].isna() | (ph["code_group"] == ph["diagnosis_raw"])
    ph["age_le_75"] = ph["age_num"] <= 75
    ph["meets_observed_necessary_conditions"] = ph["age_le_75"] & ph["code_concordant"]
    return ph


def tables(ph: pd.DataFrame) -> dict[str, pd.DataFrame]:
    out = {
        "diagnosis_by_flag": pd.crosstab(ph.diagnosis_raw, ph[FLAG], margins=True),
        "age_by_diagnosis_and_flag": ph.groupby([FLAG, "diagnosis_raw"]).age_num.agg(["count", "mean", "median", "min", "max"]).round(1),
        "age_by_diagnosis_all": ph.groupby("diagnosis_raw").age_num.agg(["count", "mean", "median", "min", "max"]).round(1),
        "sex_by_diagnosis_and_flag": pd.crosstab([ph[FLAG], ph.diagnosis_raw], ph["char:gender"]),
        "code_group_by_diagnosis": pd.crosstab(ph.code_group.fillna("(no group letter)"), ph.diagnosis_raw),
        "flag_by_conditions": pd.crosstab([ph.age_le_75, ph.code_group.notna(), ph.code_concordant], ph[FLAG]),
        "flag_by_site": pd.crosstab(ph.description.str.extract(r"^([A-Z]+)")[0], ph[FLAG]),
    }
    out["necessary_conditions_check"] = pd.DataFrame([{
        "n_yes": int((ph[FLAG] == "yes").sum()),
        "n_yes_failing_conditions": int(((ph[FLAG] == "yes") & ~ph.meets_observed_necessary_conditions).sum()),
        "n_meeting_conditions": int(ph.meets_observed_necessary_conditions.sum()),
        "n_meeting_conditions_but_no": int(((ph[FLAG] == "no") & ph.meets_observed_necessary_conditions).sum()),
    }])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Descriptive tables for the GEO case-control inclusion flag")
    ap.add_argument("--accessions", nargs="+", default=["GSE63060", "GSE63061"])
    ap.add_argument("--version", default="v1")
    ap.add_argument("--project-root", type=Path, default=ROOT)
    a = ap.parse_args(argv)
    root = a.project_root.resolve()
    out = root / "reports" / "phase2b" / a.accessions[0] / a.version
    if out.exists():
        raise SystemExit(f"{out.relative_to(root)} already exists; choose a new --version")
    results = {}
    frames = {}
    for acc in a.accessions:
        ph = pd.read_csv(root / "data" / "processed" / acc / "phenotype_table.tsv", sep="\t", dtype=str, keep_default_na=False)
        if FLAG not in ph:
            raise SystemExit(f"{acc}: field {FLAG!r} not present")
        frames[acc] = annotate(ph)
        results[acc] = tables(frames[acc])
    out.mkdir(parents=True)
    for acc, tabs in results.items():
        for name, df in tabs.items():
            df.to_csv(out / f"{acc}_{name}.csv")
        exc = frames[acc][(frames[acc][FLAG] == "no") & frames[acc].meets_observed_necessary_conditions]
        exc[["geo_accession", "title", "description", "diagnosis_raw", "char:age", "char:gender", "char:ethnicity"]] \
            .to_csv(out / f"{acc}_flag_no_despite_meeting_observed_conditions.csv", index=False)
    (out / "run_info.json").write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "inputs": [f"data/processed/{acc}/phenotype_table.tsv" for acc in a.accessions],
        "argv": ["scripts/phase2b_population_tables.py"] + (argv if argv is not None else sys.argv[1:]),
        "note": "descriptive only; no expression data and no hypothesis tests were used",
    }, indent=2) + "\n")
    print(f"wrote {len(list(out.iterdir()))} files to {out.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
