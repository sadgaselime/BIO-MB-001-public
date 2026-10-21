"""D6-G A0 classifier (synthetic): package mapping only, no gene-history rescue, discordant retained and flagged."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("a0", ROOT / "scripts/annotation_illumina_a0_classification.py")
a0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a0)

BASE = {"10", "20", "30"}


def test_eligible_and_comparison_statuses():
    assert a0.classify({"10"}, BASE, "unique", frozenset({"10"}))["comparison_status"] == "concordant"
    r = a0.classify({"10"}, BASE, "unique", frozenset({"99"}))
    assert (r["a0_class"], r["a0_gene_id"], r["comparison_status"]) == ("eligible", "10", "discordant")
    assert a0.classify({"10"}, BASE, "accession_unmatched", frozenset())["comparison_status"] == "accession_unmatched"
    assert a0.classify({"10"}, BASE, "ambiguous", frozenset({"10", "20"}))["comparison_status"] == "ambiguous"


def test_no_gene_history_rescue():
    r = a0.classify({"777"}, BASE, "unique", frozenset({"20"}))
    assert r["a0_class"] == "unmapped_not_in_snapshot" and r["a0_gene_id"] == ""
    assert r["comparison_status"] == "accession_only_not_added"   # accession gene never added


def test_multi_and_empty():
    assert a0.classify({"10", "20"}, BASE, "unique", frozenset({"10"}))["a0_class"] == "excluded_multi_entrez"
    assert a0.classify(set(), BASE, "no_accession", frozenset())["a0_class"] == "unmapped_no_package_gene"
