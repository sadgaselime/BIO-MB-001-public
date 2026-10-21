"""Discovery prep (Tier B 6–9) for GSE63060 (synthetic): identifiability maths, population log, G3 table, gates."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from test_run_identity_lifecycle import make_repo

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dprep", PROJECT / "scripts/discovery_prep_gse63060.py")
dp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dp)


def pop_from(rows):
    df = pd.DataFrame(rows, columns=["gsm", "group", "chip", "age", "sex_male"])
    df["case_AD"] = (df["group"] == "AD").astype(int)
    return df


def balanced(n_chips=4, per=6, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for c in range(n_chips):
        for i in range(per):
            rows.append((f"G{c}_{i}", "AD" if i % 2 == 0 else "CTL", f"C{c}", 70 + rng.normal(0, 5), int(rng.integers(0, 2))))
    return pop_from(rows)


def test_balanced_design_proceeds():
    r = dp.identifiability(balanced())
    assert r["decision"] == "PROCEED" and r["decision_checks"]["M2"]["mixed_units"] == 4
    assert r["decision_checks"]["M4_VIF"] < 10 and r["descriptive"]["aliasing_null_space_dim"] == 1   # chips sum to intercept


def test_group_confounded_with_chip_stops():
    rows = [(f"A{i}", "AD", "C1", 70.0 + i, i % 2) for i in range(6)] + [(f"B{i}", "CTL", "C2", 71.0 + i, i % 2) for i in range(6)]
    r = dp.identifiability(pop_from(rows))
    assert r["decision"] == "STOP" and not r["decision_checks"]["M3_estimable"]


def test_too_few_mixed_units_stops():
    p = balanced(n_chips=2)
    r = dp.identifiability(p)
    assert r["decision"] == "STOP" and any("c1" in s for s in r["stop_reasons"])


def test_e_matches_one_minus_r2():
    p = balanced(seed=3)
    N, _ = dp.nuisance_matrix(p)
    g = p["case_AD"].to_numpy(float)
    beta, *_ = np.linalg.lstsq(N, g, rcond=None)
    r2 = 1 - ((g - N @ beta) ** 2).sum() / ((g - g.mean()) ** 2).sum()
    assert abs(dp.identifiability(p)["decision_checks"]["M3_E"] - (1 - r2)) < 1e-10


def test_primary_population_applies_exclusions_and_covariates():
    elig = pd.DataFrame({"gsm": ["G1", "G2", "G3", "G4"], "array_barcode": ["111_A", "111_B", "222_A", "222_B"],
                         "participant_code": ["KPOA1", "LDZC2", "XYZ3", "PRGM4"], "group": ["AD", "CTL", "CTL", "MCI"],
                         "eligible_in_dataset_preqc": ["True"] * 4, "age": ["70", "71", "72", "73"],
                         "gender": ["Female", "Male", "Female", "Male"]})
    pop = dp.primary_population(elig, {"G2"})
    assert list(pop["gsm"]) == ["G1", "G3"] and list(pop["chip"]) == ["111", "222"]
    assert list(pop["site"]) == ["KPO", "undetermined"] and list(pop["sex_male"]) == [0, 0]


def test_selection_table_g3():
    a0 = pd.DataFrame({"cohort": ["GSE63060"] * 5 + ["GSE63061"], "a0_class": ["eligible", "eligible", "eligible", "excluded_multi_entrez", "eligible", "eligible"],
                       "in_series_matrix": ["yes", "yes", "no", "yes", "yes", "yes"],
                       "probe_id": ["P2", "P1", "P3", "P4", "P5", "P6"], "a0_gene_id": ["10", "10", "10", "", "2", "10"]})
    t = dp.selection_table(a0)
    assert t.to_dict("records") == [{"entrez_gene_id": "2", "constituent_probes": "P5", "n_probes": 1},
                                    {"entrez_gene_id": "10", "constituent_probes": "P1;P2", "n_probes": 2}]


def test_refuses_without_recorded_approvals(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    monkeypatch.setattr(dp, "ROOT", root)
    monkeypatch.setattr(dp, "REQUIRE_VENV", False)
    monkeypatch.setattr(dp, "REQUIRE_EXECUTED_CODE", False)
    assert dp.main(["--version", "v1"]) == 1 and not (root / dp.OUT_REL / "prep_v1").exists()
