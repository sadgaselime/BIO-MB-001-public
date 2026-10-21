"""Discovery fit (synthetic): full-rank basis equivalence, G3 gene means, and an end-to-end limma fit in a temporary repo."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from biomarker_project import code_identity as ci
from test_annotation_lifecycle_integration import TrackedStub
from test_run_identity_lifecycle import make_repo

PROJECT = Path(__file__).resolve().parents[1]


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fit = load("scripts/discovery_fit_gse63060.py", "dfit")
prep = load("scripts/discovery_prep_gse63060.py", "dprep2")


def population(n_chips=5, per=8, seed=1):
    rng = np.random.default_rng(seed)
    rows = [(f"G{c}_{i}", "AD" if i % 3 else "CTL", f"C{c}", 70 + rng.normal(0, 5), int(rng.integers(0, 2)))
            for c in range(n_chips) for i in range(per)]
    df = pd.DataFrame(rows, columns=["gsm", "group", "chip", "age", "sex_male"])
    df["case_AD"] = (df["group"] == "AD").astype(int)
    return df


def test_full_rank_basis_gives_the_chip_indicator_coefficient():
    pop = population()
    r = prep.identifiability(pop)["descriptive"]["r_N"]
    design = fit.full_rank_design(pop, prep.nuisance_matrix, r)
    y = np.random.default_rng(5).normal(size=len(pop)) + 0.7 * pop["case_AD"].to_numpy()
    b_basis = np.linalg.lstsq(design.matrix, y, rcond=None)[0][-1]
    N, _ = prep.nuisance_matrix(pop)
    full = np.column_stack([N, pop["case_AD"].to_numpy(float)])
    b_full = (np.linalg.pinv(full) @ y)[-1]           # chip indicators with redundancy (minimum-norm solution)
    assert abs(b_basis - b_full) < 1e-10


def test_wrong_rank_stops():
    pop = population()
    with pytest.raises(SystemExit):
        fit.full_rank_design(pop, prep.nuisance_matrix, 999)


def test_gene_matrix_is_mean_of_constituents():
    v = pd.DataFrame({"A": [1.0, 3.0, 10.0], "B": [2.0, 4.0, 20.0]}, index=["p1", "p2", "p3"])
    t = pd.DataFrame({"entrez_gene_id": ["7", "8"], "constituent_probes": ["p1;p2", "p3"]})
    g = fit.gene_matrix(v, t)
    assert g.loc["7"].tolist() == [2.0, 3.0] and g.loc["8"].tolist() == [10.0, 20.0]


@pytest.mark.skipif(shutil.which("Rscript") is None, reason="R 4.6.1 (D8) not installed")
def test_end_to_end_synthetic_limma_fit(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    pop = population(n_chips=4, per=9)
    pop["array_barcode"], pop["participant_code"], pop["gender"], pop["site"] = pop["chip"] + "_X", "P", "Female", "undetermined"
    rng = np.random.default_rng(2)
    probes = [f"P{j}" for j in range(40)]
    vals = rng.normal(8, 1, (40, len(pop)))
    vals[:5] += 1.5 * pop["case_AD"].to_numpy()                    # planted AD effect in P0..P4
    sm = "\n".join(["!series_matrix_table_begin", '"ID_REF"\t' + "\t".join(f'"{g}"' for g in pop["gsm"])] +
                   [f'"{p}"\t' + "\t".join(f"{x:.6f}" for x in row) for p, row in zip(probes, vals)] + ["!series_matrix_table_end"]) + "\n"
    b = gzip.compress(sm.encode())
    raw = root / "data/raw/GSE63060"
    raw.mkdir(parents=True)
    (raw / "GSE63060_series_matrix.txt.gz").write_bytes(b)
    (raw / "download_manifest.json").write_text(json.dumps({"files": {"GSE63060_series_matrix.txt.gz": {"current": {"sha256": hashlib.sha256(b).hexdigest()}}}}))
    ident = prep.identifiability(pop)
    table = pd.DataFrame({"entrez_gene_id": [str(i) for i in range(20)], "constituent_probes": [f"P{2 * i};P{2 * i + 1}" for i in range(20)]})
    ci.run_with_identity(root, root / fit.PREP_REL, lambda s: ({
        "identifiability_checks.json": json.dumps(ident).encode(),
        "primary_population_log.tsv": pop.to_csv(sep="\t", index=False).encode(),
        "selection_table_G3.tsv": table.to_csv(sep="\t", index=False).encode()}, {}), executed_code=TrackedStub())
    for k, v in {"ROOT": root, "REQUIRE_VENV": False, "REQUIRE_EXECUTED_CODE": False,
                 "EXPECTED": {"arrays": len(pop), "AD": int(pop["case_AD"].sum()), "probes": 40, "genes": 20}}.items():
        monkeypatch.setattr(fit, k, v)
    monkeypatch.setattr(fit, "_load_prep_module", lambda: prep)
    assert fit.main(["--version", "v1"]) == 0
    d = root / fit.OUT_REL / "fit_v1"
    assert ci.is_accepted(d)
    res = pd.read_csv(d / "probe_level_results.tsv", sep="\t").set_index("feature_id")
    assert (res.loc[[f"P{j}" for j in range(5)], "estimate"] > 0.8).all()       # planted effects recovered
    assert res.loc[[f"P{j}" for j in range(5)], "q_value_bh"].max() < 0.05
    summ = json.loads((d / "discovery_summary.json").read_text())
    assert summ["gene_level"]["n_tested"] == 20 and summ["probe_level"]["n_tested"] == 40
