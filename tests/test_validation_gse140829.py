"""GSE140829 replication runner (synthetic): batch unit, measurability universe and the approval gate."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[1]


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v = load("scripts/validation_gse140829.py", "val140829")
prep = load("scripts/discovery_prep_gse63060.py", "dprep_140829")


def test_measurability_universe_separates_unmapped_from_absent():
    a0p = pd.DataFrame({"probe_id": ["ILMN_1", "ILMN_2", "ILMN_3"], "a0_class": ["eligible", "eligible", "unmapped_no_package_gene"],
                        "a0_gene_id": ["10", "20", ""]})
    nuid = pd.DataFrame({"probe_id": ["n1"], "ilmn_probe_id": ["ILMN_1"]})
    u = v.measurability_universe(a0p, nuid)
    assert dict(zip(u["a0_gene_id"], u["in_series_matrix"])) == {"10": "yes", "20": "no"}
    sig = pd.DataFrame({"lock_rank": [1, 2, 3], "entrez_gene_id": ["10", "20", "30"], "symbol": ["A", "B", "C"],
                        "direction": ["up_in_AD", "down_in_AD", "down_in_AD"]})
    genes = pd.DataFrame({"s1": [1.0], "s2": [2.0]}, index=["10"])
    cats = list(v.val.measurability(sig, u, "GSE140829", genes)["category"])
    assert cats == ["4_measurable", "2_no_eligible_probe_in_series_matrix", "1_unmapped"]


def test_population_uses_batch_as_the_unit():
    elig = pd.DataFrame({"gsm": ["G1", "G2", "G3"], "array_barcode": ["1_A", "1_B", "2_A"], "participant_code": "",
                         "group": ["AD", "CTL", "MCI"], "eligible_in_dataset_preqc": "True", "age": ["70", "71", "72"],
                         "gender": ["Female", "Male", "Male"], "batch": ["20", "21", "20"]})
    pop = v.population(elig, set(), prep)
    assert list(pop["gsm"]) == ["G1", "G2"] and list(pop["chip"]) == ["batch_20", "batch_21"]


def test_gate_refuses_without_recorded_approvals(tmp_path, monkeypatch):
    monkeypatch.setattr(v, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="PRECONDITIONS NOT MET"):
        v.produce("v_test")
