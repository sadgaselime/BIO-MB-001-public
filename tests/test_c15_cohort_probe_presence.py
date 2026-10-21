"""C15 probe-presence helpers (synthetic): only probe IDs are taken from a Series Matrix; route categories are exact."""
from __future__ import annotations

import gzip
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("c15", ROOT / "scripts/c15_cohort_probe_presence.py")
c15 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c15)


def write_matrix(path: Path, header="ID_REF", close=True):
    lines = ['!Series_title\t"x"', '!Series_platform_id\t"GPL6947"', "!series_matrix_table_begin",
             f'"{header}"\t"GSM1"\t"GSM2"', '"ILMN_1"\t1.5\t2.5', '"ILMN_2"\tNA\t3.0']
    if close:
        lines.append("!series_matrix_table_end")
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def test_reads_only_ids_and_platform(tmp_path):
    p = tmp_path / "m.txt.gz"
    write_matrix(p)
    sm = c15.read_series_matrix_ids(p)
    assert sm["probe_ids"] == ["ILMN_1", "ILMN_2"]
    assert sm["platform_ids"] == ["GPL6947"] and sm["table_closed"] and sm["n_rows"] == 2
    assert set(sm) == {"platform_ids", "probe_ids", "table_closed", "n_rows"}  # no value field is returned


def test_wrong_header_stops(tmp_path):
    p = tmp_path / "m.txt.gz"
    write_matrix(p, header="PROBE")
    with pytest.raises(SystemExit):
        c15.read_series_matrix_ids(p)


def test_route_status_categories():
    g = frozenset({"10"})
    assert c15.route_status("eligible_direct", "10", "unique", g) == "both_concordant"
    assert c15.route_status("eligible_via_history_replacement", "11", "unique", g) == "both_discordant"
    assert c15.route_status("eligible_direct", "10", "ambiguous", frozenset({"10", "12"})) == "option_a_only"
    assert c15.route_status("multiple_mappings_excluded", "", "unique", g) == "accession_only"
    assert c15.route_status("no_assignment_in_package", "", "no_accession", frozenset()) == "neither"
    assert c15.route_status("eligible_direct", "10", None, frozenset()) == "option_a_eligible"
    assert c15.route_status("discontinued_no_replacement", "", None, frozenset()) == "option_a_not_eligible"
