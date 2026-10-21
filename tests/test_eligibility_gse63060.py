"""GSE63060 eligibility runner (synthetic): a fake Series Matrix, supplementary headers, phenotype table, download
manifest and accepted pin in a temporary git repository. No project data are read."""
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
spec = importlib.util.spec_from_file_location("elig", PROJECT / "scripts/eligibility_gse63060.py")
elig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elig)

SAMPLES = [  # gsm, barcode, participant code, status
    ("GSM1", "B_1", "P1", "AD"), ("GSM2", "B_2", "P2", "AD"), ("GSM3", "B_3", "P3", "CTL"),
    ("GSM4", "B_4", "P4", "MCI"), ("GSM5", "B_5", "P5", "CTL"),
]


def series_matrix(samples, status_lines=None) -> bytes:
    q = lambda xs: "\t".join(f'"{x}"' for x in xs)  # noqa: E731
    lines = ['!Series_title\t"synthetic"',
             "!Sample_title\t" + q(s[1] for s in samples),
             "!Sample_geo_accession\t" + q(s[0] for s in samples),
             "!Sample_characteristics_ch1\t" + q(f"status: {s[3]}" for s in samples)]
    lines += status_lines or []
    lines += ["!Sample_characteristics_ch1\t" + q("age: 70" for _ in samples),
              "!Sample_characteristics_ch1\t" + q("gender: Female" for _ in samples),
              "!Sample_characteristics_ch1\t" + q("included in case -control study: yes" for _ in samples),
              "!Sample_description\t" + q(s[2] for s in samples),
              '!Sample_contact_email\t' + q("someone@example.invalid" for _ in samples),
              "!series_matrix_table_begin", '"ID_REF"\t' + q(s[0] for s in samples),
              '"P1"\t' + "\t".join("1.0" for _ in samples), "!series_matrix_table_end"]
    return gzip.compress(("\n".join(lines) + "\n").encode())


def build(root: Path, samples=SAMPLES, pin=True, status_lines=None, phenotype_override=None):
    raw = root / "data/raw/GSE63060"
    raw.mkdir(parents=True)
    files = {elig.SM_NAME: series_matrix(samples, status_lines),
             elig.SUPPLEMENTARY[0]: gzip.compress(("ID_REF\t" + "\t".join([s[1] for s in samples] + ["EXTRA_X"]) + "\n1\n").encode()),
             elig.SUPPLEMENTARY[1]: gzip.compress(("IND_ID\t" + "\t".join([s[1] + ".AVG_Signal" for s in samples] + [""]) + "\n").encode())}
    for n, b in files.items():
        (raw / n).write_bytes(b)
    (raw / "download_manifest.json").write_text(json.dumps({"files": {
        n: {"current": {"sha256": hashlib.sha256(b).hexdigest()}} for n, b in files.items()}}))
    ph = root / elig.PHENOTYPE_REL
    ph.parent.mkdir(parents=True)
    with open(ph, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["geo_accession", "title", "description", "char:status"])
        for s in samples:
            w.writerow(phenotype_override(s) if phenotype_override else [s[0], s[1], s[2], s[3]])
    if pin:
        ci.run_with_identity(root, root / elig.PIN_REL, lambda st: ({"annotation_pin_record.json": b"{}\n"}, {}),
                             executed_code=TrackedStub())


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = make_repo(tmp_path / "repo")
    monkeypatch.setattr(elig, "ROOT", root)
    monkeypatch.setattr(elig, "REQUIRE_VENV", False)
    monkeypatch.setattr(elig, "REQUIRE_EXECUTED_CODE", False)
    monkeypatch.setattr(elig, "EXPECTED", {"universe": 5, "AD": 2, "CTL": 2, "MCI": 1})
    return root


def out_dir(root):
    return root / elig.OUT_REL / "v1"


def test_r5_categories():
    assert elig.r5_category(["AD"]) == ("mapped", "AD")
    assert elig.r5_category([]) == ("missing", "")
    assert elig.r5_category(["borderline MCI"]) == ("borderline", "borderline MCI")
    assert elig.r5_category(["CTL to AD"]) == ("transitional", "CTL to AD")
    assert elig.r5_category(["OTHER"]) == ("non_specific", "OTHER")
    assert elig.r5_category(["AD", "CTL"]) == ("conflicting", "AD|CTL")
    assert elig.r5_category(["AD", "AD"]) == ("mapped", "AD")


def test_reader_takes_only_needed_fields_and_stops_at_table_header(tmp_path):
    p = tmp_path / "sm.txt.gz"
    p.write_bytes(series_matrix(SAMPLES))
    sm = elig.read_series_matrix_samples(p)
    assert sm["table_columns"] == [s[0] for s in SAMPLES]
    assert set(sm["samples"][0]) == {"gsm", "title", "description", "status_values", "age", "gender", "sood_flag"}
    assert "someone@example.invalid" not in json.dumps(sm)  # contact fields never read into outputs


def test_end_to_end_synthetic_eligibility(repo):
    build(repo)
    assert elig.main(["--version", "v1"]) == 0
    d = out_dir(repo)
    assert ci.is_accepted(d)
    rows = list(csv.DictReader(open(d / "eligibility_log.tsv"), delimiter="\t"))
    assert [r["primary_contrast_preqc"] for r in rows] == ["case", "case", "control", "", "control"]
    assert rows[3]["rules"] == "R1;R4:outside_primary_contrast" and rows[0]["rules"] == "R1;R3:case"
    r11 = list(csv.DictReader(open(d / "r11_supplementary_columns.tsv"), delimiter="\t"))
    assert {(r["file"], r["header"], r["reason"].split(" ")[0]) for r in r11} == {
        (elig.SUPPLEMENTARY[0], "EXTRA_X", "no"), (elig.SUPPLEMENTARY[1], "", "empty")}
    m = json.loads((d / "manifest.json").read_text())
    assert all(c["pass"] for c in m["validation"]) and m["inputs"]["annotation_pin"]["dir"] == elig.PIN_REL
    assert "someone@example.invalid" not in "".join(p.read_text() for p in d.iterdir())


def test_duplicates_and_r5_labels_are_excluded_and_logged(repo, monkeypatch):
    samples = SAMPLES + [("GSM6", "B_1", "P6", "AD"), ("GSM7", "B_7", "P7", "OTHER")]
    monkeypatch.setattr(elig, "EXPECTED", {"universe": 7, "AD": 2, "CTL": 2, "MCI": 1})
    res = elig.classify({"table_columns": [s[0] for s in samples],
                         "samples": [{"gsm": s[0], "title": s[1], "description": s[2], "status_values": [s[3]],
                                      "age": "", "gender": "", "sood_flag": ""} for s in samples]}, {})
    byg = {r["gsm"]: r for r in res["rows"]}
    assert byg["GSM1"]["eligible_in_dataset_preqc"] == "False" and "R2-ID:excluded(title)" in byg["GSM1"]["rules"]
    assert byg["GSM6"]["primary_contrast_preqc"] == "" and byg["GSM7"]["r5_category"] == "non_specific"
    assert "R5:excluded(non_specific)" in byg["GSM7"]["rules"]
    assert dict(res["checks"])["R2-ID: GSM, barcode and participant code unique"] is False


def test_count_mismatch_fails_closed(repo, monkeypatch):
    build(repo)
    monkeypatch.setattr(elig, "EXPECTED", {"universe": 5, "AD": 3, "CTL": 2, "MCI": 1})
    assert elig.main(["--version", "v1"]) == 1
    assert not out_dir(repo).exists()
    failed = [p for p in out_dir(repo).parent.iterdir() if p.name.startswith("v1.FAILED-")]
    assert "D2 pre-QC count AD = 3" in json.loads((failed[0] / ci.FAILED_FILENAME).read_text())["exception"]


def test_missing_pin_fails_closed(repo):
    build(repo, pin=False)
    assert elig.main(["--version", "v1"]) == 1 and not out_dir(repo).exists()


def test_input_hash_mismatch_fails_closed(repo):
    build(repo)
    sm = repo / "data/raw/GSE63060" / elig.SM_NAME
    sm.write_bytes(sm.read_bytes() + b"\n")
    assert elig.main(["--version", "v1"]) == 1 and not out_dir(repo).exists()


def test_phenotype_disagreement_fails_closed(repo):
    build(repo, phenotype_override=lambda s: [s[0], s[1], s[2], "MCI" if s[0] == "GSM1" else s[3]])
    assert elig.main(["--version", "v1"]) == 1 and not out_dir(repo).exists()


def test_refuses_overwrite(repo):
    build(repo)
    assert elig.main(["--version", "v1"]) == 0
    assert elig.main(["--version", "v1"]) == 1


def test_gse63061_configuration():
    import importlib.util as iu
    sp = iu.spec_from_file_location("elig61", PROJECT / "scripts/eligibility_gse63060.py")
    m = iu.module_from_spec(sp)
    sp.loader.exec_module(m)
    m.use("GSE63061")
    assert m.ACC == "GSE63061" and m.SM_NAME == "GSE63061_series_matrix.txt.gz"
    assert m.EXPECTED == {"universe": 388, "AD": 139, "CTL": 134, "MCI": 109, "R5": 6}
    assert m.OUT_REL == "reports/eligibility/GSE63061" and m.PHENOTYPE_REL == "data/processed/GSE63061/phenotype_table.tsv"
