#!/usr/bin/env python3
"""Reproduce the publication-vs-GEO cross-checks of Phase 2B v2 (descriptive only).

Run from the project root:
    .venv/bin/python reports/phase2b/GSE63060/v2/reproduce_crosschecks.py

Reads data/processed/<ACC>/phenotype_table.tsv (derived from the GEO sample records) and compares
it with values transcribed by hand from Sood et al., Genome Biol 2015;16:185 (PMC4561473):
Materials and methods (case-control section) and Table 1. Writes
publication_vs_geo_crosscheck.csv and control64_reconstruction_check.json next to this script.
No expression data, no hypothesis tests.
"""
import itertools
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FLAG = "char:included in case -control study"

# (accession, group, n, mean_age, sd_age, female, male, location in paper)
PAPER = [
    ("GSE63060", "CTL", 67, None, None, None, None, "Methods text (batch 1 Control = 67)"),
    ("GSE63060", "MCI", 39, None, None, None, None, "Methods text (batch 1 MCI = 39)"),
    ("GSE63060", "AD", 49, None, None, None, None, "Methods text (batch 1 AD = 49)"),
    ("GSE63061", "CTL", 72, None, None, None, None, "Methods text (batch 2 Control = 72)"),
    ("GSE63061", "MCI", 30, None, None, None, None, "Methods text (batch 2 MCI = 30)"),
    ("GSE63061", "AD", 40, None, None, None, None, "Methods text (batch 2 AD = 40)"),
    ("GSE63060", "CTL", 67, 69.6, 4.2, 41, 26, "Table 1, batch 1 'Control MCI'"),
    ("GSE63060", "MCI", 39, 70.0, 3.3, 24, 15, "Table 1, batch 1 'MCI'"),
    ("GSE63060", "CTL", 64, 70.2, 3.7, 41, 23, "Table 1, batch 1 'Control AD'"),
    ("GSE63060", "AD", 49, 69.8, 4.4, 34, 15, "Table 1, batch 1 'AD'"),
    ("GSE63061", "CTL", 71, 70.8, 2.9, 44, 27, "Table 1, batch 2 'Control MCI' and 'Control AD'"),
    ("GSE63061", "MCI", 31, 69.5, 4.5, 23, 8, "Table 1, batch 2 'MCI'"),
    ("GSE63061", "AD", 40, 69.9, 4.3, 23, 17, "Table 1, batch 2 'AD'"),
]


def load(acc):
    ph = pd.read_csv(ROOT / "data" / "processed" / acc / "phenotype_table.tsv", sep="\t", dtype=str, keep_default_na=False)
    ph["age"] = pd.to_numeric(ph["char:age"])
    return ph


def main():
    rows = []
    totals = {}
    for acc in ("GSE63060", "GSE63061"):
        ph = load(acc)
        totals[acc] = {"all_samples": len(ph), "flag_yes": int((ph[FLAG] == "yes").sum())}
        y = ph[ph[FLAG] == "yes"]
        for a, grp, n, m, sd, f, mm, where in PAPER:
            if a != acc:
                continue
            g = y[y.diagnosis_raw == grp]
            sx = g["char:gender"].value_counts()
            geo = {"n": len(g), "mean_age": round(g.age.mean(), 2), "sd_age": round(g.age.std(), 2),
                   "female": int(sx.get("Female", 0)), "male": int(sx.get("Male", 0))}
            rows.append({
                "accession": acc, "group": grp, "paper_location": where,
                "paper_n": n, "geo_flagged_n": geo["n"], "n_matches": n == geo["n"],
                "paper_mean_age": m, "geo_mean_age": geo["mean_age"], "paper_sd_age": sd, "geo_sd_age": geo["sd_age"],
                "paper_female_male": None if f is None else f"{f}/{mm}", "geo_female_male": f"{geo['female']}/{geo['male']}",
                "sex_split_matches": None if f is None else (f == geo["female"] and mm == geo["male"]),
            })
    out = pd.DataFrame(rows)
    out.to_csv(HERE / "publication_vs_geo_crosscheck.csv", index=False)

    # Can Table 1's 64 batch-1 'Control AD' (41 F / 23 M, mean 70.2, SD 3.7) be obtained from the
    # 67 flagged controls by removing 3 males, using the integer ages recorded in GEO?
    ph = load("GSE63060")
    c = ph[(ph[FLAG] == "yes") & (ph.diagnosis_raw == "CTL")]
    males = c[c["char:gender"] == "Male"].index
    combos = list(itertools.combinations(males, 3))
    hits = [cb for cb in combos if round(c.age.drop(list(cb)).mean(), 1) == 70.2 and round(c.age.drop(list(cb)).std(), 1) == 3.7]
    best = max(c.age.drop(list(cb)).mean() for cb in combos)
    check = {"n_flagged_controls": len(c), "n_flagged_male_controls": len(males), "n_three_male_removals_tested": len(combos),
             "n_matching_table1_mean_70.2_sd_3.7": len(hits), "highest_achievable_mean_age": round(best, 3),
             "totals": totals, "superseries_GSE63063_total_expected": totals["GSE63060"]["all_samples"] + totals["GSE63061"]["all_samples"]}
    (HERE / "control64_reconstruction_check.json").write_text(json.dumps(check, indent=2) + "\n")
    print(out.to_string(index=False))
    print(json.dumps(check, indent=2))


if __name__ == "__main__":
    main()
