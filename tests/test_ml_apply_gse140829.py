"""GSE140829 frozen-model application (synthetic): configuration, apply-once gate and preconditions."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mlapply140829", PROJECT / "scripts/ml_apply_gse140829.py")
ap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ap)


def test_configuration():
    assert ap.ACC == "GSE140829" and ap.EXPECTED == {"AD": 201, "CTL": 248}
    assert ap.VAL_REL == "reports/validation/GSE140829/v1" and ap.OUT_REL == "reports/ml/GSE140829_external"


def test_refuses_without_accepted_inputs(tmp_path, monkeypatch):
    monkeypatch.setattr(ap, "ROOT", tmp_path)
    with pytest.raises(SystemExit, match="PRECONDITIONS NOT MET"):
        ap.produce("v_test", "v1")
