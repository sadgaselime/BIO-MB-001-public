"""Decision-matrix v2 builder (synthetic): REVIEW_v1 corrections R1-R5, R8 and R10 are enforced by the pure builder."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dm2", ROOT / "scripts/annotation_illumina_route_decision_matrix_v2.py")
dm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dm)

LUMI = "lumi HT-12 v4 R2"


def platform(cohort, lumi=False):
    trans = {"same -> concordant [eligible_direct]": 60,
             "different -> concordant [eligible_via_history_replacement]": 5,
             "different -> discordant [eligible_direct]": 3,
             "different -> discordant [eligible_via_history_replacement]": 2}
    not_m1 = []
    if lumi:
        trans["different -> not_in_M1 (Option A not eligible) [discontinued_no_replacement]"] = 2
        not_m1 = [("P1", "discontinued_no_replacement"), ("P2", "discontinued_no_replacement")]
    return {"cohort": cohort, "n": 120, "multi_gene_probes": 0 if lumi else 4, "no_gene_in_package": 20,
            "oa": {"eligible": 90, "eligible_direct": 85, "eligible_via_replacement": 5, "no_replacement": 3, "unexplained": 0,
                   "distinct_genes": 80, "genes_with_more_than_one_probe": 9, "collision_probes": 2,
                   "collision_successor_genes": 1, "collision_source_genes": 2},
            "oa_classes": {"discontinued_no_replacement": 2, "chain_ends_no_replacement": 1},
            "acc_classes": {"unique": 75, "accession_unmatched": 15, "no_accession": 30 - (0 if lumi else 6),
                            **({} if lumi else {"ambiguous": 6})},
            "acc_unique": 75, "acc_genes": 70, "acc_multi_probe_genes": 7, "acc_values": 130, "acc_version_suffixed": 0,
            "probes_gt1_accession": 0 if lumi else 3,
            "ambiguity": {"both": 0 if lumi else 3, "package_only": 0 if lumi else 1, "package_only_accession_unique": 0 if lumi else 1,
                          "accession_only": 0 if lumi else 3, "accession_only_single_package_gene": 0 if lumi else 3},
            "cmp": {"both": 70, "concordant": 65, "discordant": 5,
                    "discordant_by_class": {"eligible_direct": 3, "eligible_via_history_replacement": 2},
                    "oa_only_unresolved": 17, "oa_only_ambiguous": 3, "acc_only": 5, "genes_both": 68, "genes_oa_only": 12,
                    "genes_acc_only": 2, "M2_total": 72 if lumi else 70, "M2_same": 60, "M2_different": 12 if lumi else 10,
                    "transitions": trans, "not_in_M1": not_m1}}


def prov():
    def p(pk, md):
        return {"metadata_raw": md, "description_version": "1", "description_packaged": pk + "; x"}
    return {"illuminaHumanv3.db_1.26.0.tar.gz": p("2015-04-07 15:19:38 UTC", {"EGSOURCEDATE": "2015-Mar17"}),
            "illuminaHumanv4.db_1.26.0.tar.gz": p("2015-04-07 15:39:45 UTC", {"EGSOURCEDATE": "2015-Mar17"}),
            "lumiHumanIDMapping_1.10.1.tar.gz": {**p("2016-04-21 13:21:07 UTC", {"REFSEQ VERSION": " "}),
                                                 "ht12_v4_tables": {"HumanHT12_V4_0_R2_15002873_B": {
                                                     "distinct_probe_ids": 120, "probe_ids_also_in_R2_B": 120,
                                                     "shared_probe_ids_with_same_nuID": 120}}},
            "org.Hs.eg.db_3.23.1.tar.gz": p("2026-03-23 01:48:12 UTC", {"EGSOURCEDATE": "2026-Mar18"})}


def rows():
    data = {"illuminaHumanv3": platform("GSE63060"), "illuminaHumanv4": platform("GSE63061"), LUMI: platform("D19", lumi=True)}
    return data, dm.build_matrix(data, prov())


def get(rs, platform_, cid):
    return next(r for r in rs if r["platform"] == platform_ and r["criterion_id"] == cid)


def test_complete_vocabularies_and_status_rule():
    data, rs = rows()
    assert all(ok for _, ok in dm.matrix_checks(rs, data))
    assert len(rs) == 45 and not any(r["status"] == "decisive" for r in rs)


def test_r1_coverage_counted_once():
    _, rs = rows()
    for p in ("illuminaHumanv3", LUMI):
        assert get(rs, p, "C01")["advantage"] == "Option A"
        assert {get(rs, p, c)["advantage"] for c in ("C09", "C10")} == {dm.RESTATES}
        assert "equals the C01 difference" in get(rs, p, "C10")["joint_evidence"]


def test_r2_r3_r8_ambiguity_and_provenance():
    _, rs = rows()
    c08 = get(rs, LUMI, "C08")
    assert c08["advantage"] == "not determinable" and c08["status"] == "unresolved"
    assert "each route excludes the probes it finds ambiguous" in c08["criterion"]
    assert "property of the source representation" in c08["limitation"]
    c11 = get(rs, LUMI, "C11")
    assert c11["status"] == "unresolved" and "2016-04-21" in c11["option_a_evidence"] and "blank (raw value ' ')" in c11["option_a_evidence"]
    assert "approved under D6-F for GPL570 only" in c11["option_a_evidence"] and "gene_history.gz" in c11["limitation"]
    assert "is part of D19 and is not established here" in get(rs, LUMI, "C15")["limitation"]


def test_r4_r5_m2_decomposition_uses_probe_record_labels():
    _, rs = rows()
    j = get(rs, LUMI, "C05")["joint_evidence"]
    assert "M2 total 72; M1 total 70 (different metrics)" in j and " vs " not in j
    assert "2 replacement-derived and still discordant" in j and "2 outside M1" in j and "P1 [discontinued_no_replacement]" in j
    assert "2 eligible_via_history_replacement" in get(rs, LUMI, "C06")["joint_evidence"]
    assert "0 outside M1" in get(rs, "illuminaHumanv3", "C05")["joint_evidence"]


def test_r10_ties_are_neither():
    data = {"illuminaHumanv3": platform("GSE63060")}
    data["illuminaHumanv3"]["acc_unique"] = data["illuminaHumanv3"]["oa"]["eligible"]
    data["illuminaHumanv3"]["acc_genes"] = data["illuminaHumanv3"]["oa"]["distinct_genes"]
    rs = dm.build_matrix(data, prov())
    assert get(rs, "illuminaHumanv3", "C01")["advantage"] == "neither"
    assert get(rs, "illuminaHumanv3", "C02")["advantage"] == "neither"
