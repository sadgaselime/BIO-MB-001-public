#!/usr/bin/env python3
"""Reproduce the Phase 2C v1 count comparisons (descriptive only; no expression data).

Run from the project root:
    .venv/bin/python reports/phase2c/GSE63060/v1/reproduce_comparisons.py

Compares local GEO phenotype tables (data/processed/<ACC>/phenotype_table.tsv) with counts
transcribed by hand from:
  * Patel et al., J Alzheimers Dis 2020 (PMC7175937), Table 1 "Demographics before QC";
  * the abstract of Lunnon et al., J Alzheimers Dis 2013 (PMID 23042217).
Writes source_count_comparison.csv next to this script.
"""
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
_CODE = [re.compile(r"^(KPO|LDZ|PRG|THS|TLS|LND)([AMC])\d+$"), re.compile(r"^(KPO|LDZ|PRG|THS|TLS|LND)(ADC|CTL|MCI)\d+$")]
_GROUP = {"A": "AD", "ADC": "AD", "C": "CTL", "CTL": "CTL", "M": "MCI", "MCI": "MCI"}


def code_group(code):
    for rx in _CODE:
        m = rx.match(code or "")
        if m:
            return _GROUP[m.group(2)]
    return None


def load(acc):
    ph = pd.read_csv(ROOT / "data" / "processed" / acc / "phenotype_table.tsv", sep="\t", dtype=str, keep_default_na=False)
    ph["code_group"] = ph["description"].map(code_group)
    return ph


def sex(ph, dx):
    g = ph[ph.diagnosis_raw == dx]["char:gender"].value_counts()
    return int(g.get("Male", 0)), int(g.get("Female", 0))


def main():
    rows = []
    # Patel et al. 2020, Table 1, demographics before QC: (case M/F, control M/F, total)
    patel = {"GSE63060": ((46, 99), (42, 62), 249), "GSE63061": ((51, 81), (55, 87), 274)}
    for acc, (case, ctrl, total) in patel.items():
        ph = load(acc)
        geo_case, geo_ctrl = sex(ph, "AD"), sex(ph, "CTL")
        rows.append({"source": "Patel 2020 Table 1 (before QC)", "accession": acc, "quantity": "AD male/female",
                     "source_value": f"{case[0]}/{case[1]}", "local_geo_value": f"{geo_case[0]}/{geo_case[1]}",
                     "agrees": case == geo_case})
        rows.append({"source": "Patel 2020 Table 1 (before QC)", "accession": acc, "quantity": "control male/female",
                     "source_value": f"{ctrl[0]}/{ctrl[1]}", "local_geo_value": f"{geo_ctrl[0]}/{geo_ctrl[1]}",
                     "agrees": ctrl == geo_ctrl})
        n_geo = int(ph.diagnosis_raw.isin(["AD", "CTL"]).sum())
        rows.append({"source": "Patel 2020 Table 1 (before QC)", "accession": acc, "quantity": "AD + control samples",
                     "source_value": total, "local_geo_value": n_geo, "agrees": total == n_geo})
    # Lunnon et al. 2013 abstract (HT-12 v3): training 78 AD + 78 controls; validation 26 AD + 26 controls + 118 MCI
    ph = load("GSE63060")
    n = ph.diagnosis_raw.value_counts()
    m_coded_ad = int(((ph.diagnosis_raw == "AD") & (ph.code_group == "MCI")).sum())
    for q, src, loc in [("AD", 104, int(n.get("AD", 0))), ("CTL", 104, int(n.get("CTL", 0))), ("MCI", 118, int(n.get("MCI", 0))),
                        ("AD excluding MCI-coded AD", 104, int(n.get("AD", 0)) - m_coded_ad),
                        ("MCI including MCI-coded AD", 118, int(n.get("MCI", 0)) + m_coded_ad)]:
        rows.append({"source": "Lunnon 2013 abstract", "accession": "GSE63060", "quantity": q,
                     "source_value": src, "local_geo_value": loc, "agrees": src == loc})
    out = pd.DataFrame(rows)
    out.to_csv(HERE / "source_count_comparison.csv", index=False)
    print(out.to_string(index=False))
    print(f"\nGSE63060 AD samples with an MCI-type participant code: {m_coded_ad}")


if __name__ == "__main__":
    main()
