"""Check that the key numbers quoted in the manuscript match the accepted outputs.

Usage (from the project root): python3 reports/manuscript/medrxiv/check_numbers.py
Each check reads a value from an accepted output, formats it as the manuscript does, and confirms that exact text
appears in MANUSCRIPT_medRxiv_v1.md. Exits non-zero if any check fails. Reads outputs only; computes no statistics.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MS = " ".join((Path(__file__).with_name("MANUSCRIPT_medRxiv_v1.md")).read_text(encoding="utf-8").split())


def j(rel):
    return json.loads((ROOT / rel).read_text())


def tsv(rel):
    with open(ROOT / rel, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def f2(x):
    return f"{x:.2f}"


def f3(x):
    return f"{x:.3f}"


def comma(n):
    return f"{int(n):,}"


def sci(x):
    m, e = f"{x:.1e}".split("e")
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return f"{m} × 10{str(int(e)).translate(sup)}"


disc = j("reports/discovery/GSE63060/fit_v1/discovery_summary.json")
sens = j("reports/discovery/GSE63060/sensitivity_v1/sensitivity_summary.json")["run"]
s11 = j("reports/discovery/GSE63060/s11_v1/s11_summary.json")
v61 = j("reports/validation/GSE63061/v1/validation_summary.json")
v140 = j("reports/validation/GSE140829/v1/validation_summary.json")
spec = j("reports/specificity/GSE99039/v1/specificity_summary.json")
ext = j("reports/s11_ext/v1/s11_ext_summary.json")
ml = j("reports/ml/GSE63060/v1/ml_summary.json")
sig = tsv("reports/lock/GSE63060/v1/signature.tsv")
e61 = {r["model"]: r for r in tsv("reports/ml/GSE63061_external/v1/external_metrics.tsv")}
e140 = {r["model"]: r for r in tsv("reports/ml/GSE140829_external/v1/external_metrics.tsv")}
d140 = tsv("reports/ml/GSE140829_external/v1/external_auc_difference_vs_B1.tsv")

g, p = disc["gene_level"], disc["probe_level"]
rhos = sorted(v.get("comparison_with_primary", {})["spearman_t_vs_primary"] for v in sens.values()
              if v.get("comparison_with_primary", {}).get("spearman_t_vs_primary") is not None)
top10 = ", ".join(r["symbol"] for r in sorted(sig, key=lambda r: int(r["lock_rank"]))[:10])
top10 = top10.rsplit(", ", 1)[0] + " and " + top10.rsplit(", ", 1)[1]
ipd, gpd, gu = (spec["primary"][k]["Q1"] for k in ("IPD", "GPD", "GENETIC_UNAFFECTED"))
x140, xipd = ext["GSE140829"], ext["GSE99039"]["IPD"]["Q1"]
r = ml["ridge"]
pn = ml["permutation_null"]
dd = {d["comparison"]: d for d in ml["delong_differences_approximate"]}

CHECKS = [
    ("discovery genes significant", comma(g["n_q_lt_0.05"])),
    ("discovery genes tested", comma(g["n_tested"])),
    ("discovery down / up", f"{g['n_down_AD']} were lower and {g['n_up_AD']} higher"),
    ("probe level", f"{comma(p['n_q_lt_0.05'])} of {comma(p['n_tested'])}"),
    ("sensitivity rho range (13 analyses)", f"{f3(rhos[1])} to {f3(rhos[-1])}"),
    ("sensitivity smallest rho", f3(rhos[0])),
    ("number of sensitivity analyses run with comparisons", "14 sensitivity analyses" if len(rhos) == 14 else "MISMATCH"),
    ("locked down / up", f"{sum(r_['direction'] == 'down_in_AD' for r_ in sig)} genes lower and "
                         f"{sum(r_['direction'] == 'up_in_AD' for r_ in sig)} higher"),
    ("top 10 genes", top10),
    ("S11 locked genes", f"all {s11['comparison_locked_genes']['q_lt_0.05_and_same_sign']} evaluable locked genes"),
    ("S11 effect ratio", f2(s11["comparison_locked_genes"]["median_abs_estimate_ratio_s11_over_primary"])),
    ("S11 all genes", f"{s11['comparison_all_genes']['of_which_same_sign_and_q_lt_0.05']} of the 1,401"),
    ("S11 rho", f"ρ of t = {f2(s11['comparison_all_genes']['spearman_t_vs_primary'])}"),
    ("GSE63061 theta", f"θ̂ = {f2(v61['C-c']['estimate'])}"),
    ("GSE63061 p", sci(v61["C-c"]["p_one_sided"])),
    ("GSE63061 lower bound", f3(v61["C-c"]["lower_bound_one_sided_95"])),
    ("GSE63061 consistent genes", f"{v61['C-a']['n_consistent_q_lt_0.05']} of 200"),
    ("GSE63061 direction", f"{v61['C-b']['overall']['concordant']} of 200 agreed"),
    ("GSE63061 r", f"r = {f2(v61['effect_correlation_v7_4_5']['pearson_r'])}"),
    ("GSE63061 r interval", f"{f2(v61['effect_correlation_v7_4_5']['fisher_z_95_nominal_low'])}–"
                            f"{f2(v61['effect_correlation_v7_4_5']['fisher_z_95_nominal_high'])}"),
    ("GSE140829 theta", f"θ̂ = {f2(v140['C-c']['estimate'])}"),
    ("GSE140829 p", f"p = {v140['C-c']['p_one_sided']:.4f}"),
    ("GSE140829 lower bound", f3(v140["C-c"]["lower_bound_one_sided_95"])),
    ("GSE140829 replicated", f"{v140['C-a']['n_replicated_q_lt_0.05']} of 200"),
    ("GSE140829 direction", f"{v140['C-b']['overall']['concordant']} of 200 agreed"),
    ("IPD theta and CI", f"θ̂ = +{f2(ipd['estimate'])} (95% CI {f2(ipd['ci_low_two_sided_95'])}–{f2(ipd['ci_high_two_sided_95'])}"),
    ("IPD p", f"p = {f3(ipd['p_two_sided'])}"),
    ("IPD Holm p", f"Holm-adjusted\np = {f3(ipd['p_holm_three_contrasts'])}"),
    ("GPD", f"θ̂ = +{f2(gpd['estimate'])}, p = {f2(gpd['p_two_sided'])}"),
    ("GU", f"θ̂ = +{f2(gu['estimate'])}, p = {f2(gu['p_two_sided'])}"),
    ("IPD age-adjusted", f"+{f2(spec['S15']['IPD']['Q1']['estimate'])} (p = {f2(spec['S15']['IPD']['Q1']['p_two_sided'])})"),
    ("S11-ext GSE140829 shift", f"from 0.25 to {f2(x140['C-c']['estimate'])}"),
    ("S11-ext GSE140829 p", f"p = {f3(x140['C-c']['p_one_sided'])}"),
    ("S11-ext GSE140829 bound", f"lower bound {f3(x140['C-c']['lower_bound_one_sided_95'])}"),
    ("S11-ext replicated", f"from 43 to {x140['C-a']['n_replicated_q_lt_0.05']} of 200"),
    ("S11-ext direction", f"from 0.92 to {f2(x140['C-b']['proportion_concordant'])}"),
    ("S11-ext IPD", f"+0.20 to +{f2(xipd['estimate'])}\n(p = {f2(xipd['p_two_sided'])}; Holm p = {f2(xipd['p_holm_three_contrasts'])})"),
    ("ridge CV AUROC and range", f"{f3(r['auroc']['mean'])} ({f3(r['auroc']['p2_5'])}–{f3(r['auroc']['p97_5'])})"),
    ("ridge sens / spec", f"{f2(r['sensitivity']['mean'])} / {f2(r['specificity']['mean'])}"),
    ("elastic net", f"| Elastic net | {f3(ml['elastic_net']['auroc']['mean'])} |"),
    ("equal weight", f"| Equal-weight score | {f3(ml['B2_equal_weight']['auroc']['mean'])} |"),
    ("age only", f"| Age only | {f3(ml['B1_age']['auroc']['mean'])} |"),
    ("ridge vs age", f"by {f2(dd['ridge - B1_age']['auc_difference'])} (DeLong p = {sci(dd['ridge - B1_age']['p_two_sided'])})"),
    ("ridge vs equal weight", f"by {f2(dd['ridge - B2_equal_weight']['auc_difference'])} (p = {f3(dd['ridge - B2_equal_weight']['p_two_sided'])})"),
    ("permutation null", f"averaged {f3(pn['null_mean'])} (maximum {f3(pn['null_max'])}; p = {f3(pn['p_value'])}"),
    ("GSE63061 external", f"{f3(float(e61['ridge']['auc']))} ({f3(float(e61['ridge']['ci_low']))}–{f3(float(e61['ridge']['ci_high']))})"),
    ("GSE63061 age only", f3(float(e61["B1_age"]["auc"]))),
    ("GSE140829 external", f"{f3(float(e140['ridge']['auc']))} ({f3(float(e140['ridge']['ci_low']))}–{f3(float(e140['ridge']['ci_high']))})"),
    ("GSE140829 age only", f"{f3(float(e140['B1_age']['auc']))} (difference p = {f2(float(d140[0]['p_two_sided']))})"),
]

fails = 0
for label, text in CHECKS:
    ok = " ".join(text.split()) in MS
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'}  {label}: {text!r}")
print(f"\n{len(CHECKS) - fails} of {len(CHECKS)} checks passed")
sys.exit(1 if fails else 0)
