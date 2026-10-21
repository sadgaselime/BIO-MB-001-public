"""Tests for the Phase 2B descriptive population tables (synthetic data only)."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "phase2b_population_tables.py"


def _mod():
    spec = importlib.util.spec_from_file_location("phase2b", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.mark.parametrize("code, expected", [
    ("KPOM0014", "MCI"), ("PRGA0003", "AD"), ("KPOC0001", "CTL"), ("LDZCTL016", "CTL"), ("THSMCI025", "MCI"),
    ("KPOADC047", "AD"), ("LND0174", None), ("DCR00088", None), ("OA123", None), ("", None), ("KPOX0001", None),
])
def test_code_group(code, expected):
    assert _mod().code_group(code) == expected


def _ph(rows):
    return pd.DataFrame(rows, columns=["geo_accession", "title", "description", "diagnosis_raw", "char:age",
                                       "char:gender", "char:ethnicity", "char:included in case -control study"])


def test_conditions_and_tables():
    m = _mod()
    ph = m.annotate(_ph([
        ["G1", "t1", "KPOA0001", "AD", "70", "F", "x", "yes"],
        ["G2", "t2", "KPOM0002", "AD", "70", "M", "x", "no"],    # code MCI, diagnosis AD -> discordant
        ["G3", "t3", "KPOC0003", "CTL", "80", "F", "x", "no"],   # over 75
        ["G4", "t4", "LND0004", "CTL", "60", "M", "x", "no"],    # meets conditions but 'no'
    ]))
    assert ph.meets_observed_necessary_conditions.tolist() == [True, False, False, True]
    chk = m.tables(ph)["necessary_conditions_check"].iloc[0].to_dict()
    assert chk == {"n_yes": 1, "n_yes_failing_conditions": 0, "n_meeting_conditions": 2, "n_meeting_conditions_but_no": 1}


def test_main_writes_new_version_only(tmp_path):
    m = _mod()
    root = tmp_path / "p"
    d = root / "data" / "processed" / "GSE1"
    d.mkdir(parents=True)
    _ph([["G1", "t1", "KPOA0001", "AD", "70", "F", "x", "yes"], ["G2", "t2", "KPOC0002", "CTL", "71", "M", "x", "yes"]]) \
        .assign(title=["t1", "t2"]).to_csv(d / "phenotype_table.tsv", sep="\t", index=False)
    before = (d / "phenotype_table.tsv").read_bytes()
    assert m.main(["--accessions", "GSE1", "--version", "v1", "--project-root", str(root)]) == 0
    out = root / "reports" / "phase2b" / "GSE1" / "v1"
    assert (out / "GSE1_diagnosis_by_flag.csv").exists() and (out / "run_info.json").exists()
    assert (d / "phenotype_table.tsv").read_bytes() == before
    with pytest.raises(SystemExit, match="already exists"):
        m.main(["--accessions", "GSE1", "--version", "v1", "--project-root", str(root)])
