"""Signature lock (synthetic): the D15 selection and tie-breaking rule, the cap, direction, and the SAP excerpt mechanics."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

from test_run_identity_lifecycle import make_repo

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lock", PROJECT / "scripts/signature_lock_gse63060.py")
lk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lk)


def res(rows):
    return pd.DataFrame(rows, columns=["feature_id", "estimate", "t_statistic", "q_value_bh"])


def test_selection_order_and_tiebreaks():
    r = res([("30", 0.5, 3.0, 0.01), ("20", -0.9, -3.0, 0.01), ("10", 0.9, 4.0, 0.01), ("5", 0.9, 4.0, 0.01),
             ("7", 2.0, 9.0, 0.001), ("8", 1.0, 1.0, 0.2)])
    sig, n = lk.select(r)
    # q asc; then |beta| desc; then |t| desc; then Entrez asc
    assert n == 5 and list(sig["feature_id"]) == ["7", "5", "10", "20", "30"]
    assert list(sig["direction"]) == ["up_in_AD", "up_in_AD", "up_in_AD", "down_in_AD", "up_in_AD"]
    assert list(sig["lock_rank"]) == [1, 2, 3, 4, 5]


def test_cap(monkeypatch):
    monkeypatch.setattr(lk, "CAP", 3)
    r = res([(str(i), 1.0 / (i + 1), 2.0, 0.001 * (i + 1)) for i in range(10)])
    sig, n = lk.select(r)
    assert n == 10 and list(sig["feature_id"]) == ["0", "1", "2"]


def test_no_eligible_genes_gives_empty_signature():
    sig, n = lk.select(res([("1", 1.0, 1.0, 0.5)]))
    assert n == 0 and sig.empty


def test_excerpts_hash_exact_lines(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    f = root / "doc.md"
    f.write_text("a\nb\nc\nd\n")
    monkeypatch.setattr(lk, "SECTIONS", {"x": ("doc.md", 2, 3)})
    ex = lk.excerpts(root)
    import hashlib
    assert ex["x"]["text"] == "b\nc" and ex["x"]["sha256"] == hashlib.sha256(b"b\nc").hexdigest()


def test_refuses_without_preconditions(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    for k, v in {"ROOT": root, "REQUIRE_VENV": False, "REQUIRE_EXECUTED_CODE": False}.items():
        monkeypatch.setattr(lk, k, v)
    assert lk.main(["--version", "v1"]) == 1 and not (root / lk.OUT_REL / "v1").exists()
