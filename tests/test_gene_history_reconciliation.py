"""Gene-history reconciliation rules on synthetic records (no NCBI or GEO data)."""
from __future__ import annotations

from biomarker_project.gene_history_reconciliation import HistoryRecord, audit_package, resolve

CUT = "20260318"
BASE = {"10", "20", "30", "50"}
HIST = {
    "1": [HistoryRecord("10", "A", "20200101")],          # replaced -> in baseline
    "2": [HistoryRecord("3", "B", "20200101")],           # two-step chain
    "3": [HistoryRecord("20", "C", "20210101")],
    "4": [HistoryRecord("-", "D", "20190101")],           # no replacement
    "5": [HistoryRecord("10", "E", "20260601")],          # only a post-cutoff record
    "6": [HistoryRecord("7", "F", "20200101")],           # cycle 6 -> 7 -> 6
    "7": [HistoryRecord("6", "G", "20200101")],
    "8": [HistoryRecord("10", "H", "20200101"), HistoryRecord("20", "H", "20200101")],   # duplicate records
    "9": [HistoryRecord("99", "I", "20200101")],          # successor absent everywhere
    "30": [HistoryRecord("50", "J", "20260701")],         # in baseline, discontinued after cutoff
    "11": [HistoryRecord("10", "K", "20200101")],         # shares successor 10 with "1"
}


def test_view_a_rules():
    assert resolve("10", BASE, HIST, CUT).cls == "present_in_baseline"
    r = resolve("2", BASE, HIST, CUT)
    assert (r.cls, r.chain, r.final) == ("replaced_successor_in_baseline", ["2", "3", "20"], "20")
    assert resolve("4", BASE, HIST, CUT).cls == "discontinued_no_replacement"
    assert resolve("5", BASE, HIST, CUT).cls == "absent_history_after_cutoff"     # not applied in View A
    assert "cycle_at" in resolve("6", BASE, HIST, CUT).reason
    assert resolve("8", BASE, HIST, CUT).reason.startswith("duplicate_history_records")
    assert resolve("9", BASE, HIST, CUT).reason.startswith("successor_absent_from_baseline_and_history")
    assert resolve("12345", BASE, HIST, CUT).cls == "unexplained_absent_no_history"
    assert resolve("30", BASE, HIST, CUT).cls == "present_in_baseline"            # baseline preserved


def test_view_b_rules():
    assert resolve("5", BASE, HIST, None).final == "10"                           # post-cutoff record applied
    r = resolve("30", BASE, HIST, None)                                           # followed past the baseline
    assert r.chain == ["30", "50"] and r.final == "50"


def test_audit_counts_flags_and_no_merging():
    ids = ["1", "10", "11", "2", "30", "4", "5", "12345"]
    rows, counts = audit_package("pkg", ids, "synthetic", BASE, HIST, CUT)
    assert sum(counts["viewA"].values()) == sum(counts["viewB"].values()) == len(ids)
    assert counts["viewB"]["present_in_baseline_discontinued_in_history"] == 1
    by = {r["entrez_id"]: r for r in rows}
    assert "10" not in by                                  # baseline-present, no history: counted, not tabulated
    assert by["1"]["viewA_collision"] == "yes"             # successor 10 is a direct input ID
    assert by["1"]["viewA_shared_successor"] == "yes" and by["11"]["viewA_shared_successor"] == "yes"
    assert len(rows) == len({r["entrez_id"] for r in rows})   # one row per input, nothing merged
    assert by["30"]["viewA_class"] == "present_in_baseline"
    assert by["30"]["viewB_class"] == "present_in_baseline_discontinued_in_history"
