"""Discovery sensitivity analyses (synthetic): set construction, G1 tie rule, filtered G3, identifiability, comparison, gate."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from test_run_identity_lifecycle import make_repo

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dsens", PROJECT / "scripts/discovery_sensitivity_gse63060.py")
ds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ds)


def pop(n_chips=4, per=8, seed=0):
    rng = np.random.default_rng(seed)
    rows = [(f"G{c}_{i}", "AD" if i % 2 else "CTL", f"C{c}", ["KPO", "LDZ"][i % 2 == 0 and c % 2], 60 + rng.integers(0, 30), int(rng.integers(0, 2)))
            for c in range(n_chips) for i in range(per)]
    df = pd.DataFrame(rows, columns=["gsm", "group", "chip", "site", "age", "sex_male"])
    df["case_AD"] = (df["group"] == "AD").astype(int)
    return df


def test_identify_proceeds_and_returns_full_rank_design():
    r = ds.identify(pop(), "chip")
    assert r["decision"] == "PROCEED" and np.linalg.matrix_rank(r["design"].matrix) == r["r_N"] + 1


def test_identify_site_as_unit_needs_c1_mixed_sites():
    r = ds.identify(pop(), "site")
    assert r["decision"] == "STOP" and any("c1" in s for s in r["stop_reasons"])   # only 2 sites < c1 = 3


def test_g1_picks_highest_mean_over_selection_with_id_tiebreak():
    v = pd.DataFrame({"A": [1.0, 5.0, 5.0], "B": [1.0, 5.0, 5.0], "C": [9.0, 0.0, 0.0]}, index=["p1", "p2", "p0"])
    t = pd.DataFrame({"entrez_gene_id": ["7"], "constituent_probes": ["p1;p2;p0"]})
    g = ds.gene_matrix_g1(v, t, ["A", "B"])          # p2 and p0 tie at 5 over A,B -> p0 (ID ascending)
    assert g.loc["7"].tolist() == [5.0, 5.0, 0.0]


def test_filtered_g3_drops_genes_without_retained_probes():
    v = pd.DataFrame({"A": [1.0, 3.0, 9.0]}, index=["p1", "p2", "p3"])
    t = pd.DataFrame({"entrez_gene_id": ["1", "2"], "constituent_probes": ["p1;p2", "p3"]})
    g = ds.gene_matrix_g3(v, t, {"p2"})
    assert list(g.index) == ["1"] and g.loc["1"].tolist() == [3.0]


def test_compare_counts_same_sign_and_significance():
    prim = pd.DataFrame({"feature_id": ["a", "b", "c"], "estimate": [1, -1, 0.1], "t_statistic": [5, -5, 0.2], "q_value_bh": [0.01, 0.01, 0.9]})
    sens = pd.DataFrame({"feature_id": ["a", "b", "c"], "estimate": [0.8, 0.5, 0.1], "t_statistic": [4, 1, 0.3], "q_value_bh": [0.02, 0.5, 0.9]})
    c = ds.compare(prim, sens)
    assert c["primary_significant_genes_compared"] == 2 and c["of_which_same_sign"] == 1 and c["of_which_same_sign_and_q_lt_0.05"] == 1


def test_build_sets_membership():
    p = pd.DataFrame({"gsm": ["g1", "g2", "g3", "g4"], "group": ["AD", "AD", "CTL", "CTL"], "age": [64, 70, 90, 75]})
    elig = pd.DataFrame({"gsm": ["g1", "g2", "g3", "g4", "g5"], "participant_code": ["KPOM1", "KPOA2", "KPOC3", "LDZC4", "KPOC5"],
                         "sood_flag_recorded_not_used_R12": ["yes", "no", "yes", "no", "no"]})
    audit = pd.DataFrame({"array_id": ["g1", "g2", "g3", "g4"], "flags": ["F1(k=3)", "F3", "", "F3-undetermined"]})
    excl = pd.DataFrame({"gsm": ["g5"], "exclusion_tiers": ["Q1"]})
    r8 = pd.DataFrame({"gsm": ["g3", "g5"], "both_y_markers_disagree_with_recorded": [True, True]})
    sets, mem = ds.build_sets(p, elig, audit, excl, r8)
    assert list(sets["S1a"]["gsm"]) == ["g2", "g3", "g4"] and list(sets["S1b"]["gsm"]) == ["g1", "g2", "g4"]
    assert mem["M_coded_AD"] == {"g1"} and mem["F1"] == {"g1"} and mem["F3"] == {"g2"} and mem["Q1_only"] == {"g5"}
    assert list(sets["S12"]["gsm"]) == ["g1", "g3"] and list(sets["S-R8m"]["gsm"]) == ["g1", "g2", "g4"]


def test_refuses_without_preconditions(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    for k, v in {"ROOT": root, "REQUIRE_VENV": False, "REQUIRE_EXECUTED_CODE": False}.items():
        monkeypatch.setattr(ds, k, v)
    assert ds.main(["--version", "v1"]) == 1 and not (root / ds.OUT_REL / "sensitivity_v1").exists()
