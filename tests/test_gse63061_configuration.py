"""GSE63061 configuration of the Tier B runners (synthetic): paths, expected shape and authorization switch correctly."""
from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_c1_review_switches_cohort():
    m = load("scripts/duplicate_review_c1_gse63060.py", "c1_61")
    m.use("GSE63061")
    assert (m.ACC, m.OUT_REL, m.ELIG_REL, m.SM_NAME) == ("GSE63061", "reports/duplicate_review/GSE63061",
                                                          "reports/eligibility/GSE63061/v1", "GSE63061_series_matrix.txt.gz")


def test_qc_stage_a_switches_cohort_shape_and_authorization():
    m = load("scripts/qc_stage_a_gse63060.py", "qa_61")
    default_auth = m.AUTHORIZATION
    m.use("GSE63061")
    assert m.EXPECTED_SHAPE == (32049, 388) and m.DUP_REL == "reports/duplicate_review/GSE63061/c1_v1"
    assert "GSE63061" in m.AUTHORIZATION and m.AUTHORIZATION != default_auth and m.OUT_REL == "reports/qc_stage_a/GSE63061"


def test_qc_stage_b_switches_cohort():
    m = load("scripts/qc_stage_b_gse63060.py", "qb_61")
    m.use("GSE63061")
    assert (m.OUT_REL, m.QC_REL, m.ELIG_REL, m.DUP_REL) == ("reports/qc_stage_b/GSE63061", "reports/qc_stage_a/GSE63061/v1",
                                                          "reports/eligibility/GSE63061/v1", "reports/duplicate_review/GSE63061/c1_v1")


def test_default_cohort_unchanged():
    for rel, name in (("scripts/qc_stage_a_gse63060.py", "qa_60"), ("scripts/qc_stage_b_gse63060.py", "qb_60"),
                      ("scripts/duplicate_review_c1_gse63060.py", "c1_60"), ("scripts/eligibility_gse63060.py", "el_60")):
        assert load(rel, name).ACC == "GSE63060"
