"""S11-ext (synthetic): score covariates appended, generic identifiability/design, gate."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("s11ext", PROJECT / "scripts/s11_ext.py")
ext = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ext)


def _data(seed=0, n_unit=6, per=10):
    rng = np.random.default_rng(seed)
    unit = pd.Series([f"b{u}" for u in range(n_unit) for _ in range(per)])
    g = np.array([float(i % 2) for i in range(n_unit * per)])
    N = np.column_stack([np.ones(len(g)), rng.integers(0, 2, len(g))] + [(unit == f"b{u}").to_numpy(float) for u in range(n_unit)])
    sc = pd.DataFrame(rng.normal(size=(len(g), 5)), columns=list(ext.s11.CLASSES.values()))
    return N, g, unit, sc


def test_with_scores_appends_five_standardized_columns():
    N, g, unit, sc = _data()
    X = ext.with_scores(N, sc)
    assert X.shape[1] == N.shape[1] + 5
    assert np.allclose(X[:, -5:].mean(axis=0), 0) and np.allclose(X[:, -5:].std(axis=0, ddof=1), 1)


def test_ident_design_proceeds_and_stops():
    N, g, unit, sc = _data()
    out = ext.ident_design(ext.with_scores(N, sc), g, unit, "c")
    assert out["decision"] == "PROCEED" and out["design"].matrix.shape[1] == out["r_N"] + 1 and out["mixed_units"] == 6
    g1 = (unit == "b0").to_numpy(float)                          # cases only in one unit
    assert ext.ident_design(ext.with_scores(N, sc), g1, unit, "c")["decision"] == "STOP"


def test_gate_refuses_without_recorded_approvals(tmp_path, monkeypatch):
    monkeypatch.setattr(ext, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="PRECONDITIONS NOT MET"):
        ext.produce("v_test")
