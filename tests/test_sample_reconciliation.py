import csv
import json

import pandas as pd
import pytest

from biomarker_project.config import ExpectedCounts, PhenotypeSpec, ReportedLead
from biomarker_project.geo_client import parse_soft_brief
from biomarker_project.sample_reconciliation import (
    AMBIGUOUS, MAPPED, MISSING, PROPOSED, UNMAPPED, build_phenotype_table, check_reported_leads, compare_group_counts,
    compare_identifier_sets, normalize_sample_id, propose_exclusion_candidates, reconcile, write_reconciliation,
)

SPEC = PhenotypeSpec(diagnosis_field="char:status", label_map={"AD": "AD", "CTL": "HC"},
                     ambiguous_labels=("borderline",), participant_id_field="description")


def _pheno(rows):
    """rows: (gsm, key, diagnosis_raw, status, canonical)"""
    return pd.DataFrame([{"geo_accession": g, "match_key": k, "diagnosis_raw": d, "diagnosis_status": s,
                          "diagnosis_canonical": c, "title": k, "diagnosis_field": "char:status"} for g, k, d, s, c in rows])


BASE = _pheno([("GSM1", "S1", "AD", MAPPED, "AD"), ("GSM2", "S2", "CTL", MAPPED, "HC"), ("GSM3", "S3", "AD", MAPPED, "AD")])


@pytest.fixture
def phenotype_from_fixture(fixtures_dir):
    recs = parse_soft_brief((fixtures_dir / "samples_brief.soft.txt").read_text())
    return build_phenotype_table(recs, SPEC)


def test_exact_matches():
    r = reconcile(["S1", "S2", "S3"], BASE)
    assert r.matched == ["S1", "S2", "S3"] and r.exact_one_to_one
    assert not r.left_only and not r.right_only


def test_expression_only_ids():
    r = reconcile(["S1", "S2", "S3", "S9"], BASE)
    assert r.left_only == ["S9"] and not r.exact_one_to_one


def test_phenotype_only_ids():
    r = reconcile(["S1", "S2"], BASE)
    assert r.right_only == ["S3"]


def test_duplicate_ids_on_either_side():
    dup_pheno = pd.concat([BASE, _pheno([("GSM4", "S1", "CTL", MAPPED, "HC")])], ignore_index=True)
    r = reconcile(["S1", "S2", "S2", "S3"], dup_pheno)
    assert r.duplicate_left_ids == {"S2": 2}
    assert r.duplicate_right_ids == {"S1": 2}
    assert not r.exact_one_to_one


def test_missing_ambiguous_and_unmapped_labels(phenotype_from_fixture):
    ph = phenotype_from_fixture
    status = dict(zip(ph["title"], ph["diagnosis_status"]))
    assert status == {"S1": MAPPED, "S2": MAPPED, "S3": MAPPED, "S4": AMBIGUOUS, "S5": MISSING}
    ph = ph.assign(match_key=ph["title"])
    extra = _pheno([("GSM9", "S9", "FTD", UNMAPPED, None)])
    r = reconcile(["S1", "S2", "S3", "S4", "S5", "S9"], pd.concat([ph, extra], ignore_index=True))
    assert r.missing_diagnosis == ["GSM900005"]
    assert r.ambiguous_diagnosis == [{"geo_accession": "GSM900004", "label": "borderline"}]
    assert r.unmapped_diagnosis == [{"geo_accession": "GSM9", "label": "FTD"}]


def test_group_counts_before_and_after_matching(phenotype_from_fixture):
    ph = phenotype_from_fixture.assign(match_key=phenotype_from_fixture["title"])
    r = reconcile(["S1", "S2", "S4"], ph)
    assert r.group_counts_all_records == {"<MISSING>": 1, "AD": 2, "AMBIGUOUS": 1, "HC": 1}
    assert r.group_counts_matched == {"AD": 1, "AMBIGUOUS": 1, "HC": 1}
    rows = compare_group_counts({"AD": 2, "HC": 1}, ExpectedCounts("ref", 5, {"AD": 2, "HC": 2}, 6), 5)
    by = {x["group"]: x for x in rows}
    assert by["TOTAL"]["status"] == "MATCHES_REPORTED"
    assert by["AD"]["status"] == "MATCHES_REPORTED"
    assert by["HC"]["status"] == "DIFFERS_FROM_REPORTED" and by["HC"]["difference"] == -1
    assert by["DESCRIBED_PARTICIPANTS"]["difference"] == -1


def test_normalization_is_conservative():
    assert normalize_sample_id("  S1\t") == "S1"
    assert normalize_sample_id("﻿S1") == "S1"
    assert normalize_sample_id("") is None and normalize_sample_id(None) is None
    # Never altered: case, punctuation, leading zeros, internal whitespace, suffixes.
    for s in ("s1", "S-1", "S_1", "001", "S 1", "S1.AVG_Signal", "S1a"):
        assert normalize_sample_id(s) == s


def test_original_ids_preserved_and_near_misses_not_matched(tmp_path):
    r = reconcile([" S1", "s2", "S-3"], BASE)
    assert r.matched == ["S1"]
    assert {"side": "expression", "original": " S1", "normalized": "S1"} in r.normalization_changes
    assert r.left_only == ["S-3", "s2"], "case/punctuation differences must not be matched"
    assert {h["expression_id"] for h in r.near_miss_hints} == {"s2", "S-3"}
    out = write_reconciliation(r, tmp_path, "test")
    with open(out["csv"]) as fh:
        rows = list(csv.DictReader(fh))
    originals = [row["original_id"] for row in rows if row["side"] == "expression"]
    assert originals == [" S1", "s2", "S-3"]
    summary = json.loads(open(out["json"]).read())
    assert summary["n_matched"] == 1 and summary["exact_one_to_one"] is False


def test_every_unmatched_and_duplicate_id_is_listed(tmp_path):
    r = reconcile(["S1", "S1", "S8"], BASE)
    out = write_reconciliation(r, tmp_path, "t")
    rows = list(csv.DictReader(open(out["csv"])))
    assert {(x["original_id"], x["status"]) for x in rows} >= {("S8", "expression_only"), ("S2", "phenotype_only"),
                                                               ("S3", "phenotype_only")}
    assert [x["duplicate_count"] for x in rows if x["original_id"] == "S1" and x["side"] == "expression"] == ["2", "2"]


def test_no_sample_dropped_proposals_only(phenotype_from_fixture):
    ph = phenotype_from_fixture.assign(match_key=phenotype_from_fixture["title"])
    n_before = len(ph)
    r = reconcile(["S1", "S2", "S3", "S4", "S6"], ph)
    proposals = propose_exclusion_candidates("GSE1", ph, {"f.txt": r})
    assert len(ph) == n_before
    assert all(p["status"] == PROPOSED and p["reason"] for p in proposals)
    reasons = " ".join(p["reason"] for p in proposals)
    assert "MISSING" in reasons and "AMBIGUOUS" in reasons and "no matching phenotype record" in reasons
    pheno_only = [p for p in proposals if p["reason"].startswith("phenotype record has no column")]
    assert [(p["sample_id"], p["geo_accession"]) for p in pheno_only] == [("S5", "GSM900005")]


def test_reported_leads_checked_not_applied(phenotype_from_fixture):
    leads = [ReportedLead("L1", "desc", "src", ("S1", "S99")), ReportedLead("L2", "no ids", "src", ()),
             ReportedLead("L3", "26 vs 30", "src", (), kind="count_discrepancy")]
    out = check_reported_leads(leads, phenotype_from_fixture, {"expr.txt": {"S1"}})
    assert out[0]["checked_ids"][0]["found_in_expression_files"] == ["expr.txt"]
    assert out[0]["checked_ids"][1]["found_in_phenotype_fields"] == []
    assert out[1]["check"].startswith("UNRESOLVED")
    assert out[2]["kind"] == "count_discrepancy" and "UNRESOLVED" in out[2]["check"]


def test_identifier_set_comparison():
    out = compare_identifier_sets({"A": ["P1", "P2", " P3"], "B": ["P3", "p1"]})
    assert out["pairs"][0]["shared_values"] == ["P3"]
