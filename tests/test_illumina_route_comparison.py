"""Regression test: the two accession-route agreement metrics (M1 vs M2) reconcile at probe level.

M1 = Option A eligible AND accession route unique (agreement vs the Option A gene, after gene-history).
M2 = single package gene AND accession route unique (agreement vs the package's own, un-reconciled ID).
Synthetic records only; no package, NCBI or GEO data.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("route_cmp", ROOT / "scripts/annotation_illumina_route_comparison.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)


def row(pid, n, pkg, cls, gene="", chain=""):
    return {"probe_id": pid, "n_package_genes": str(n), "package_gene_id": pkg, "option_a_class": cls,
            "option_a_gene_id": gene, "history_chain": chain, "successor_directly_mapped": ""}


ROWS = [
    row("p1", 1, "1", "eligible_direct", "1"),                                  # same -> concordant
    row("p2", 1, "2", "eligible_via_history_replacement", "20", "2>20"),        # different -> concordant
    row("p3", 1, "3", "discontinued_no_replacement", "", "3"),                  # different -> not in M1 (the lumi case)
    row("p4", 1, "4", "eligible_direct", "4"),                                  # different -> discordant
    row("p5", 1, "5", "eligible_direct", "5"),                                  # accession ambiguous: in neither metric
    row("p6", 0, "", "no_assignment_in_package"),                               # no package gene: not in M2
]
ACC = {"p1": {"A1"}, "p2": {"A2"}, "p3": {"A3"}, "p4": {"A4"}, "p5": {"A5"}, "p6": {"A6"}}
ORG = {"A1": frozenset({"1"}), "A2": frozenset({"20"}), "A3": frozenset({"30"}), "A4": frozenset({"40"}),
       "A5": frozenset({"5", "50"}), "A6": frozenset({"60"})}


def test_m1_m2_reconcile_at_probe_level():
    ar, cmp_, prior, checks = rc.accession_route("illuminaHumanv3", ROWS, ACC, ORG)
    rec = cmp_["reconciliation_M1_vs_M2"]
    assert all(ok for _, ok in checks), [n for n, ok in checks if not ok]
    assert cmp_["both_assign_one_gene"] == rec["M1_total_both_assign"] == 3
    assert prior["route_exactly_one_gene"] == rec["M2_total_package_gene_and_accession_unique"] == 4
    assert rec["M1_subset_of_M2"] and rec["in_M2_not_M1"] == ["p3"]
    assert (cmp_["concordant"], cmp_["discordant"]) == (2, 1)
    assert (prior["same_gene"], prior["different_gene"]) == (1, 3)
    t = rec["transitions_M2_to_M1_by_option_a_class"]
    assert t["different -> concordant [eligible_via_history_replacement]"] == 1
    assert t["different -> not_in_M1 (Option A not eligible) [discontinued_no_replacement]"] == 1
    # every M2 'different' probe is accounted for by exactly one transition
    assert sum(v for k, v in t.items() if k.startswith("different")) == prior["different_gene"]
    rows = {r["probe_id"]: r for r in cmp_["_reconciliation_rows"]}
    assert set(rows) == {"p2", "p3", "p4"}                     # all transitions except same -> concordant are recorded
    assert cmp_["accession_unique_optionA_not_eligible"] == 2   # p3 and p6
