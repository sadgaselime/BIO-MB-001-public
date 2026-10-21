#!/usr/bin/env python3
"""Reproduce the Phase 2C v2 comparisons between the Lunnon et al. papers and local GEO records.

Run from the project root:
    .venv/bin/python reports/phase2c/GSE63060/v2/reproduce_lunnon_comparisons.py

Paper values are transcribed by hand (location given for each). GEO values come from
data/processed/GSE63060/phenotype_table.tsv. Descriptive only: no expression data are read,
no tests are performed, and no sample is relabelled, excluded or assigned an identity.
Writes lunnon_vs_geo_comparison.csv and code_letter_sex_accounting.csv next to this script.
"""
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

# (label, n, male, female, mean_age or None, location)
L2012 = {  # Lunnon et al. 2012, Table 1 (p.688), "Samples used in analysis"
    "Control": (105, 43, 62, 72.4, "2012 Table 1 p.688"),
    "MCI (MCI-MCI)": (78, 39, 39, 74.3, "2012 Table 1 p.688"),
    "MCI-AD": (42, 14, 28, 74.6, "2012 Table 1 p.688"),
    "AD": (104, 32, 72, 75.4, "2012 Table 1 p.688"),
}
# Lunnon et al. 2013, Table 1 (p.741): (n, female, male, mean age) per column
L2013 = {
    "Control training": (78, 45, 33, 72.1), "Control validation": (26, 17, 9, 73.2),
    "AD training": (78, 52, 26, 75.5), "AD validation": (26, 20, 6, 75.1),
    "MCInc": (77, 38, 39, 74.3), "MCIc": (41, 27, 14, 75.0),
}


def load():
    ph = pd.read_csv(ROOT / "data" / "processed" / "GSE63060" / "phenotype_table.tsv", sep="\t", dtype=str, keep_default_na=False)
    ph["age"] = pd.to_numeric(ph["char:age"])
    ph["site"] = ph["description"].str.extract(r"^([A-Z]{3})")[0]
    ph["code_letter"] = ph["description"].str.extract(r"^[A-Z]{3}([AMC])\d")[0]
    return ph


def geo(ph, mask):
    g = ph[mask]
    s = g["char:gender"].value_counts()
    return len(g), int(s.get("Male", 0)), int(s.get("Female", 0)), round(g.age.mean(), 2)


def pooled(parts):
    n = sum(p[0] for p in parts)
    return n, sum(p[2] for p in parts), sum(p[1] for p in parts), round(sum(p[0] * p[3] for p in parts) / n, 2)  # n, male, female, mean


def main():
    ph = load()
    rows = []

    def add(src, group, paper, geo_vals, loc):
        rows.append({"source": src, "group": group, "location": loc,
                     "paper_n": paper[0], "geo_n": geo_vals[0],
                     "paper_male_female": f"{paper[1]}/{paper[2]}", "geo_male_female": f"{geo_vals[1]}/{geo_vals[2]}",
                     "paper_mean_age": paper[3], "geo_mean_age": geo_vals[3],
                     "n_and_sex_identical": (paper[0], paper[1], paper[2]) == geo_vals[:3]})

    ctl, ad, mci = (ph.diagnosis_raw == "CTL"), (ph.diagnosis_raw == "AD"), (ph.diagnosis_raw == "MCI")
    # Lunnon 2013 pooled groups vs GEO
    c13 = pooled([L2013["Control training"], L2013["Control validation"]])
    add("Lunnon 2013", "controls (training+validation) vs GEO CTL", c13, geo(ph, ctl), "2013 Table 1 p.741")
    ad13 = pooled([L2013["AD training"], L2013["AD validation"], L2013["MCIc"]])
    add("Lunnon 2013", "AD + MCIc vs GEO AD", ad13, geo(ph, ad), "2013 Table 1 p.741")
    adonly = pooled([L2013["AD training"], L2013["AD validation"]])
    add("Lunnon 2013", "AD only vs GEO AD", adonly, geo(ph, ad), "2013 Table 1 p.741")
    m = L2013["MCInc"]
    add("Lunnon 2013", "MCInc vs GEO MCI", (m[0], m[2], m[1], m[3]), geo(ph, mci), "2013 Table 1 p.741")
    # Lunnon 2012 groups vs GEO
    c = L2012["Control"]
    add("Lunnon 2012", "Control vs GEO CTL", c[:4], geo(ph, ctl), c[4])
    a, ma = L2012["AD"], L2012["MCI-AD"]
    add("Lunnon 2012", "AD + MCI-AD vs GEO AD", (a[0] + ma[0], a[1] + ma[1], a[2] + ma[2], round((a[0] * a[3] + ma[0] * ma[3]) / (a[0] + ma[0]), 2)), geo(ph, ad), a[4])
    mm = L2012["MCI (MCI-MCI)"]
    add("Lunnon 2012", "MCI-MCI vs GEO MCI", mm[:4], geo(ph, mci), mm[4])
    tot12 = sum(v[0] for v in L2012.values())
    rows.append({"source": "Lunnon 2012", "group": "total chips in final analysis vs GEO samples", "location": "2012 p.688 text + Table 1",
                 "paper_n": tot12, "geo_n": len(ph), "n_and_sex_identical": tot12 == len(ph)})
    rows.append({"source": "Lunnon 2013", "group": "total subjects after QC vs GEO samples", "location": "2013 p.740",
                 "paper_n": 326, "geo_n": len(ph), "n_and_sex_identical": 326 == len(ph)})
    out = pd.DataFrame(rows)
    out.to_csv(HERE / "lunnon_vs_geo_comparison.csv", index=False)

    # Code-letter sex accounting for GEO AD (no identities assigned)
    acc = []
    for label, mask in [("AD, code letter A", ad & (ph.code_letter == "A")), ("AD, code letter M", ad & (ph.code_letter == "M")),
                        ("AD, LND site (no letter)", ad & (ph.site == "LND")), ("all GEO AD", ad)]:
        n, mm_, ff, age = geo(ph, mask)
        acc.append({"group": label, "n": n, "male": mm_, "female": ff, "mean_age": age})
    acc.append({"group": "Lunnon 2013 MCIc (paper)", "n": 41, "male": 14, "female": 27, "mean_age": 75.0})
    acc.append({"group": "Lunnon 2013 AD (paper, training+validation)", "n": 104, "male": 32, "female": 72, "mean_age": adonly[3]})
    under65 = ph[ph.age < 65].groupby("diagnosis_raw").size().to_dict()
    acc.append({"group": f"GEO samples aged <65 (both papers state <65 excluded): {under65}", "n": int((ph.age < 65).sum())})
    pd.DataFrame(acc).to_csv(HERE / "code_letter_sex_accounting.csv", index=False)
    print(out.to_string(index=False))
    print()
    print(pd.DataFrame(acc).to_string(index=False))


if __name__ == "__main__":
    main()
