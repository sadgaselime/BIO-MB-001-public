"""S11 cell composition (synthetic): marker parsing, diagnosis-blind scores, design with score covariates, comparisons, gate."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("s11", PROJECT / "scripts/s11_cell_composition_gse63060.py")
s11 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s11)


def test_read_markers_keeps_only_the_five_k1_classes(tmp_path):
    p = tmp_path / "genes.txt"
    p.write_text('"HUGO symbols"\t"Cell population"\t"ENTREZID"\t"ENSEMBL ID"\n"CD3D"\t"T cells"\t915\t"E1"\n'
                 '"X"\t"Fibroblasts"\t5\t"E2"\n"CD19"\t"B lineage"\t930\t"E3"\n')
    m = s11.read_markers(p)
    assert set(m) == set(s11.CLASSES.values()) and m["T_cells"] == ["915"] and m["B_lineage"] == ["930"] and m["Neutrophils"] == []


def test_scores_are_mean_z_of_present_markers():
    genes = pd.DataFrame({"a": [1.0, 10.0], "b": [2.0, 20.0], "c": [3.0, 30.0]}, index=["1", "2"])
    sc, used = s11.scores(genes, {"T_cells": ["1", "2", "99"]})
    z = (genes - genes.mean(axis=1).to_numpy()[:, None]) / genes.std(axis=1, ddof=1).to_numpy()[:, None]
    assert np.allclose(sc["T_cells"].to_numpy(), z.mean(axis=0).to_numpy()) and used["T_cells"] == {"markers": 3, "present": 2}


def _pop(seed=0):
    rng = np.random.default_rng(seed)
    rows = [(f"G{c}_{i}", "AD" if i % 3 else "CTL", f"C{c}", 70 + rng.normal(0, 5), int(rng.integers(0, 2)))
            for c in range(6) for i in range(9)]
    df = pd.DataFrame(rows, columns=["gsm", "group", "chip", "age", "sex_male"])
    df["case_AD"] = (df["group"] == "AD").astype(int)
    return df


def test_identify_adds_five_score_columns():
    pop = _pop()
    sc = pd.DataFrame(np.random.default_rng(1).normal(size=(len(pop), 5)), columns=list(s11.CLASSES.values()), index=pop["gsm"])
    N = s11.nuisance(pop, sc)
    assert N.shape[1] == 3 + 6 + 5
    idf = s11.identify(pop, sc)
    assert idf["decision"] == "PROCEED" and idf["design"].coefficient == "AD_vs_CTL"


def test_compare_locked_excludes_marker_genes():
    sig = pd.DataFrame({"entrez_gene_id": ["1", "2", "915"], "direction": ["down_in_AD", "up_in_AD", "down_in_AD"]})
    prim = pd.DataFrame({"feature_id": ["1", "2", "915"], "estimate": [-1.0, 1.0, -1.0], "t_statistic": [-5.0, 4.0, -3.0],
                         "q_value_bh": [0.001, 0.001, 0.01]})
    s = prim.assign(estimate=[-0.5, -0.1, 1.0], t_statistic=[-3.0, -0.5, 2.0], q_value_bh=[0.01, 0.9, 0.5])
    r = s11.compare_locked(prim, s, sig, {"915"})
    assert r["n_locked_compared"] == 2 and r["same_sign_as_locked"] == 1 and r["q_lt_0.05_and_same_sign"] == 1
    assert r["excluded_marker_genes"] == ["915"]


def test_gate_refuses_without_recorded_approvals(tmp_path, monkeypatch):
    monkeypatch.setattr(s11, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="PRECONDITIONS NOT MET"):
        s11.produce("v_test")
