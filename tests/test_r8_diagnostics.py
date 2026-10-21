"""R8 diagnostics (synthetic): fake deposited and raw files with sex probes; accepted fake prerequisites."""
from __future__ import annotations

import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from biomarker_project import code_identity as ci
from biomarker_project.qc_r8 import XIST_PROBE, Y_PROBES
from test_annotation_lifecycle_integration import TrackedStub
from test_run_identity_lifecycle import make_repo

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r8d", PROJECT / "scripts/r8_diagnostics_gse63060.py")
r8d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r8d)

N = 20


def test_auc_bounds_and_ties():
    assert r8d.auc(np.array([3.0, 4.0]), np.array([1.0, 2.0])) == 1.0
    assert r8d.auc(np.array([1.0, 2.0]), np.array([3.0, 4.0])) == 0.0
    assert r8d.auc(np.array([1.0]), np.array([1.0])) == 0.5


def build(root: Path):
    rng = np.random.default_rng(3)
    gsms, bars = [f"GSM{i}" for i in range(N)], [f"B_{i}" for i in range(N)]
    sexes = ["Female" if i % 2 == 0 else "Male" for i in range(N)]
    probes = [XIST_PROBE, *list(Y_PROBES)[:3], *[f"P{j}" for j in range(30)]]
    raw = {}
    for p in probes:
        if p == XIST_PROBE:
            raw[p] = [2000 + rng.normal(0, 50) if s == "Female" else 150 + rng.normal(0, 10) for s in sexes]
        elif p in Y_PROBES:
            raw[p] = [120 + rng.normal(0, 5) if s == "Female" else 900 + rng.normal(0, 40) for s in sexes]
        else:
            raw[p] = list(300 + rng.normal(0, 30, N))
    sm_rows = [f'"{p}"\t' + "\t".join(f"{np.log2(v):.6f}" for v in vals) for p, vals in raw.items()]
    sm = gzip.compress(("\n".join(["!series_matrix_table_begin", '"ID_REF"\t' + "\t".join(f'"{g}"' for g in gsms), *sm_rows,
                                   "!series_matrix_table_end"]) + "\n").encode())
    nn = gzip.compress(("IND_ID\t" + "\t".join(b + ".AVG_Signal" for b in bars) + "\n" +
                        "".join(f"{p}\t" + "\t".join(f"{v:.4f}" for v in vals) + "\n" for p, vals in raw.items())).encode())
    d = root / "data/raw/GSE63060"
    d.mkdir(parents=True)
    (d / r8d.SM_NAME).write_bytes(sm)
    (d / r8d.RAW_NAME).write_bytes(nn)
    (d / "download_manifest.json").write_text(json.dumps({"files": {n: {"current": {"sha256": hashlib.sha256(b).hexdigest()}}
                                                                     for n, b in ((r8d.SM_NAME, sm), (r8d.RAW_NAME, nn))}}))
    log = "gsm\tarray_barcode\tgroup\tgender\n" + "".join(f"{g}\t{b}\tAD\t{s}\n" for g, b, s in zip(gsms, bars, sexes))
    stub = TrackedStub()
    ci.run_with_identity(root, root / r8d.ELIG_REL, lambda s: ({"eligibility_log.tsv": log.encode()}, {}), executed_code=stub)
    ci.run_with_identity(root, root / r8d.QC_REL, lambda s: ({"qc_audit.tsv": b"x\n"}, {}), executed_code=stub)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    monkeypatch.setattr(r8d, "ROOT", root)
    monkeypatch.setattr(r8d, "REQUIRE_VENV", False)
    monkeypatch.setattr(r8d, "REQUIRE_EXECUTED_CODE", False)
    return root


def test_end_to_end_separates_clean_synthetic_sex_signal(repo):
    build(repo)
    assert r8d.main(["--version", "v1"]) == 0
    d = repo / r8d.OUT_REL / "v1"
    assert ci.is_accepted(d)
    df = pd.read_csv(d / "r8_probe_diagnostics.tsv", sep="\t")
    present = df[df["present"]]
    assert set(present["source"]) == {"series_matrix", "log2_non_normalized"}
    assert (present["auc_expected_direction"] == 1.0).all()
    assert (present["split_calls_discordant_with_recorded_sex"] == 0).all()
    assert "AD" not in (d / "r8_probe_diagnostics.tsv").read_text().split()


def test_requires_accepted_qc_stage_a(repo):
    build(repo)
    import shutil
    shutil.rmtree(repo / r8d.QC_REL)
    assert r8d.main(["--version", "v1"]) == 1 and not (repo / r8d.OUT_REL / "v1").exists()
