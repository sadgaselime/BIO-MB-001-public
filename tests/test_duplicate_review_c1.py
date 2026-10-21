"""Tier B step 4 C1 duplicate review (synthetic): fake Series Matrix and accepted fake eligibility output."""
from __future__ import annotations

import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from biomarker_project import code_identity as ci
from test_annotation_lifecycle_integration import TrackedStub
from test_run_identity_lifecycle import make_repo

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dupc1", PROJECT / "scripts/duplicate_review_c1_gse63060.py")
dup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dup)


def matrix(rows, extra_lines=()) -> bytes:
    q = lambda xs: "\t".join(f'"{x}"' for x in xs)  # noqa: E731
    lines = ["!Sample_title\t" + q(r[1] for r in rows), "!Sample_geo_accession\t" + q(r[0] for r in rows),
             "!Sample_characteristics_ch1\t" + q(f"status: {r[3]}" for r in rows),
             "!Sample_characteristics_ch1\t" + q("age: 70" for _ in rows),
             "!Sample_description\t" + q(r[2] for r in rows),
             "!Sample_contact_name\t" + q("replicate person" for _ in rows), *extra_lines,
             "!series_matrix_table_begin", '"ID_REF"\t' + q(r[0] for r in rows), '"P1"\t' + "\t".join("1" for _ in rows)]
    return gzip.compress(("\n".join(lines) + "\n").encode())


ROWS = [("GSM1", "B1", "P1", "AD"), ("GSM2", "B2", "P2", "CTL"), ("GSM3", "B3", "P3", "MCI")]


def build(root, rows=ROWS, extra_lines=(), elig=True, elig_gsms=None):
    raw = root / "data/raw/GSE63060"
    raw.mkdir(parents=True)
    b = matrix(rows, extra_lines)
    (raw / dup.SM_NAME).write_bytes(b)
    (raw / "download_manifest.json").write_text(json.dumps({"files": {dup.SM_NAME: {"current": {"sha256": hashlib.sha256(b).hexdigest()}}}}))
    if elig:
        log = "gsm\tgroup\n" + "".join(f"{g}\tX\n" for g in (elig_gsms or [r[0] for r in rows]))
        ci.run_with_identity(root, root / dup.ELIG_REL, lambda s: ({"eligibility_log.tsv": log.encode()}, {}),
                             executed_code=TrackedStub())


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    monkeypatch.setattr(dup, "ROOT", root)
    monkeypatch.setattr(dup, "REQUIRE_VENV", False)
    monkeypatch.setattr(dup, "REQUIRE_EXECUTED_CODE", False)
    return root


def out(root):
    return root / dup.OUT_REL / "c1_v1"


def test_no_candidates_completes_without_reviewer(repo):
    build(repo)
    assert dup.main(["--version", "v1"]) == 0
    d = out(repo)
    assert ci.is_accepted(d)
    log = json.loads((d / "duplicate_review_log_c1.json").read_text())
    assert log["n_candidates"] == 0 and log["status"].startswith("complete") and log["reviewer"].startswith("not applicable")
    assert (d / "c1_review_table.tsv").read_text().strip() == "\t".join(dup.REVIEW_COLUMNS)


def test_identity_duplicates_and_replicate_annotations_are_candidates(repo):
    rows = [("GSM1", "B1", "P1", "AD"), ("GSM2", "B1", "P2", "CTL"), ("GSM3", "B3", "P1", "MCI")]
    build(repo, rows, extra_lines=['!Sample_source_name_ch1\t"blood"\t"blood replicate 2 of GSM1"\t"blood"'])
    assert dup.main(["--version", "v1"]) == 0
    d = out(repo)
    table = list(csv.DictReader(open(d / "c1_review_table.tsv"), delimiter="\t"))
    links = {(r["link"], r["gsms"]) for r in table}
    assert ("identical array_barcode", "GSM1;GSM2") in links and ("identical participant_code", "GSM1;GSM3") in links
    assert ("deposited replicate annotation", "GSM2") in links
    assert {r["category"] for r in table if r["link"] == "identical participant_code"} == {"D-1u (shared description value)"}
    log = json.loads((d / "duplicate_review_log_c1.json").read_text())
    assert log["n_candidates"] == 3 and "pending" in log["status"] and log["reviewer"].startswith("PENDING")


def test_review_table_is_blinded_and_contact_fields_never_read(repo):
    build(repo)
    assert dup.main(["--version", "v1"]) == 0
    text = "".join(p.read_text() for p in out(repo).iterdir())
    assert "AD" not in (out(repo) / "c1_review_table.tsv").read_text() and "replicate person" not in text
    meta = dup.read_allowed_metadata(repo / "data/raw/GSE63060" / dup.SM_NAME)
    assert "status: AD" not in json.dumps(meta) and meta["characteristic_keys"] == ["age", "status"]


def test_requires_accepted_eligibility(repo):
    build(repo, elig=False)
    assert dup.main(["--version", "v1"]) == 1 and not out(repo).exists()


def test_universe_must_match_eligibility(repo):
    build(repo, elig_gsms=["GSM1", "GSM2"])
    assert dup.main(["--version", "v1"]) == 1 and not out(repo).exists()


def test_input_hash_mismatch_fails(repo):
    build(repo)
    p = repo / "data/raw/GSE63060" / dup.SM_NAME
    p.write_bytes(p.read_bytes() + b"\n")
    assert dup.main(["--version", "v1"]) == 1 and not out(repo).exists()
