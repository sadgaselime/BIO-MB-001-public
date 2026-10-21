"""Decision-matrix builder: complete per-platform criteria, allowed vocabularies, M1/M2 kept separate (synthetic)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dm", ROOT / "scripts/annotation_illumina_route_decision_matrix.py")
dm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dm)


def platform(cohort):
    oa = {"eligible": 90, "eligible_direct": 85, "eligible_via_replacement": 5, "no_replacement": 3, "unexplained": 0,
          "distinct_genes": 80, "genes_with_more_than_one_probe": 9, "collision_probes": 2,
          "collision_successor_genes": 1, "collision_source_genes": 2}
    rec = {"M1_total_both_assign": 70, "M2_total_package_gene_and_accession_unique": 72, "M1_subset_of_M2": True,
           "in_M2_not_M1": ["x", "y"],
           "transitions_M2_to_M1_by_option_a_class": {"same -> concordant [eligible_direct]": 60,
                                                      "different -> concordant [eligible_via_history_replacement]": 5,
                                                      "different -> discordant [eligible_direct]": 5,
                                                      "different -> not_in_M1 (Option A not eligible) [discontinued_no_replacement]": 2}}
    m3 = {"probes_total": 120, "multi_gene_probes": 4, "no_gene_in_package": 20, "cohort": cohort, "option_a": oa,
          "accession_route_assignments": {"assigned_unique": 75, "distinct_genes": 70},
          "accession_route_inputs": {"accessions_with_version_suffix": 0, "probes_with_more_than_one_accession": 3},
          "route_comparison": {"genes_both_routes": 68, "genes_optionA_only": 12, "genes_accession_only": 2,
                               "both_assign_one_gene": 70, "concordant": 65, "discordant": 5, "pct_concordant_of_both": "92.86%",
                               "optionA_eligible_accession_unresolved": 15, "optionA_eligible_accession_ambiguous_including_optionA_gene": 4,
                               "optionA_eligible_accession_ambiguous_excluding_optionA_gene": 1, "accession_unique_optionA_not_eligible": 5}}
    return {"cohort": cohort, "m3": m3, "acc_multi_probe_genes": 7,
            "acc_classes": {"unique": 75, "ambiguous": 6, "accession_unmatched": 9, "no_accession": 30}, "recon": rec}


META = {"illuminaHumanv3.db_1.26.0.tar.gz": {"EGSOURCEDATE": "2015-Mar17"}, "illuminaHumanv4.db_1.26.0.tar.gz": {"EGSOURCEDATE": "2015-Mar17"},
        "lumiHumanIDMapping_1.10.1.tar.gz": {"REFSEQ VERSION": "not recorded"}, "org.Hs.eg.db_3.23.1.tar.gz": {"EGSOURCEDATE": "2026-Mar18"}}


def test_matrix_complete_and_m1_m2_separate():
    data = {"illuminaHumanv3": platform("GSE63060"), "illuminaHumanv4": platform("GSE63061"), "lumi HT-12 v4 R2": platform("D19")}
    rows = dm.build_matrix(data, META)
    assert len(rows) == 45 and {r["platform"] for r in rows} == set(data)
    assert all(r["status"] in dm.STATUSES and r["advantage"] in dm.ADVANTAGES for r in rows)
    assert not any(r["status"] == "decisive" for r in rows)
    c05 = next(r for r in rows if r["criterion_id"] == "C05" and r["platform"] == "lumi HT-12 v4 R2")
    assert "M2 total 72 vs M1 total 70" in c05["accession_route_evidence"] and "must not be compared directly" in c05["limitation"]
    c13 = next(r for r in rows if r["criterion_id"] == "C13")
    assert "distinct successor genes 1; distinct historical source genes 2" in c13["option_a_evidence"]
    c15 = [r for r in rows if r["criterion_id"] == "C15"]
    assert all(r["option_a_evidence"] == "NOT ASSESSED" and r["status"] == "unresolved" for r in c15)
