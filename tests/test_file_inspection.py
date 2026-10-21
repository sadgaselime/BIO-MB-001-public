import gzip
import hashlib
import shutil
import tarfile

import numpy as np

from biomarker_project.file_inspection import (
    EMPTY, INSPECTED, MALFORMED, UNSUPPORTED, classify_measure, detect_format, inspect_file, iter_feature_rows,
)
from biomarker_project.processing_audit import (
    METADATA_ONLY, NON_NORMALIZED, PROCESSED, UNKNOWN, _decide, classify_file, compare_matrices,
)


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_plain_tsv(fixtures_dir):
    p = fixtures_dir / "expr_plain.tsv"
    before = _sha(p)
    r = inspect_file(p)
    assert r.usable and r.format == "delimited_text" and r.compression == "none"
    assert r.n_rows == 4 and r.n_columns == 4 and r.delimiter == "\t"
    assert r.feature_id_column == "ID_REF"
    assert r.candidate_sample_ids == ["S1", "S2", "S3"]
    assert r.duplicate_feature_ids["n_duplicated_ids"] == 1 and "P3" in r.duplicate_feature_ids["examples"]
    assert r.missing_values["total_missing_in_sample_columns"] == 1
    assert r.missing_values["top_columns_with_missing"] == {"S2": 1}
    assert _sha(p) == before, "inspection must not modify the file"


def test_csv_detected(fixtures_dir):
    r = inspect_file(fixtures_dir / "expr_plain.csv")
    assert r.delimiter == "," and r.candidate_sample_ids == ["S1", "S2"]


def test_gzip_table_matches_plain(fixtures_dir, tmp_path):
    gz = tmp_path / "expr.tsv.gz"
    with open(fixtures_dir / "expr_plain.tsv", "rb") as src, gzip.open(gz, "wb") as dst:
        shutil.copyfileobj(src, dst)
    plain, comp = inspect_file(fixtures_dir / "expr_plain.tsv"), inspect_file(gz)
    assert comp.compression == "gzip"
    assert (comp.n_rows, comp.candidate_sample_ids, comp.value_summary["max"]) == \
           (plain.n_rows, plain.candidate_sample_ids, plain.value_summary["max"])


def test_format_detection_ignores_misleading_name(fixtures_dir, tmp_path):
    fake = tmp_path / "looks_like.tar"
    shutil.copy(fixtures_dir / "expr_plain.tsv", fake)
    assert detect_format(fake) == ("delimited_text", "none")


def test_empty_file(fixtures_dir, tmp_path):
    r = inspect_file(fixtures_dir / "empty.txt")
    assert r.status == EMPTY and not r.usable
    gz = tmp_path / "empty.gz"
    with gzip.open(gz, "wb"):
        pass
    assert inspect_file(gz).status == EMPTY


def test_malformed_rows_with_extra_fields(fixtures_dir):
    r = inspect_file(fixtures_dir / "malformed_ragged.tsv")  # contains a row with too many fields
    assert r.status == MALFORMED and not r.usable
    assert "more fields than the header" in r.error


def test_short_rows_reported_and_counted_missing(tmp_path):
    p = tmp_path / "short.tsv"
    p.write_text("ID_REF\tS1\tS2\nP1\t1.0\t2.0\nP2\nP3\t3.0\t4.0\n")
    r = inspect_file(p)
    assert r.status == "INSPECTED_WITH_LIMITATIONS" and r.usable
    assert r.metadata["rows_with_too_few_fields"] == [{"line": 3, "n_fields": 1, "first_field": "P2"}]
    assert r.missing_values["total_missing_in_sample_columns"] == 2
    assert r.n_rows == 3


def test_binary_and_corrupt_gzip(tmp_path):
    b = tmp_path / "blob.bin"
    b.write_bytes(b"\x00\x01\x02binary\x00")
    assert inspect_file(b).status == UNSUPPORTED
    bad = tmp_path / "bad.txt.gz"
    bad.write_bytes(b"\x1f\x8b\x08\x00garbage")
    r = inspect_file(bad)
    assert not r.usable and r.error


def test_missing_file(tmp_path):
    r = inspect_file(tmp_path / "absent.txt")
    assert not r.usable and "does not exist" in r.error


def test_illumina_suffixes_preserve_original_columns(fixtures_dir):
    r = inspect_file(fixtures_dir / "illumina_nonnormalized.txt")
    assert r.feature_id_column == "PROBE_ID"
    assert r.annotation_columns == ["SYMBOL"], "non-numeric annotation must not be treated as a sample"
    assert r.candidate_sample_ids == ["S1", "S2"]
    assert r.measurement_types == {"signal": 2, "detection_pval": 2}
    cols = {c["column"]: c for c in r.sample_columns}
    assert cols["S1.AVG_Signal"]["sample_id"] == "S1"
    assert "stripped GenomeStudio suffix" in cols["S1.AVG_Signal"]["derivation"]


def test_classify_measure_does_not_strip_unknown_suffixes():
    assert classify_measure("Sample.1")[0] == "Sample.1"
    assert classify_measure("4856076025_A.AVG_Signal")[:2] == ("4856076025_A", "signal")
    assert classify_measure("5872617031_A.DETECTION PVAL")[:2] == ("5872617031_A", "detection_pval")


def test_empty_header_data_columns_reported(tmp_path):
    p = tmp_path / "emptyhdr.tsv"
    p.write_text("IND_ID\tA.AVG_Signal\t\tB.AVG_Signal\t\nP1\t1.5\t2.5\t3.5\t4.5\nP2\t5.5\t6.5\t7.5\t8.5\n")
    r = inspect_file(p)
    assert r.empty_header_sample_columns == [3, 5]
    assert r.candidate_sample_ids[:2] == ["A", "B"] or "A" in r.candidate_sample_ids
    assert any("EMPTY header" in l for l in r.limitations)


def test_duplicate_column_headers_reported_verbatim(tmp_path):
    p = tmp_path / "dup.tsv"
    p.write_text("ID_REF\tS1\tS1\tS2\nP1\t1\t2\t3\nP2\t4\t5\t6\n")
    r = inspect_file(p)
    assert r.duplicate_column_headers == ["S1"]
    assert r.duplicate_sample_ids == ["S1"]


def test_series_matrix_omits_submitter_contact_details(tmp_path):
    p = tmp_path / "sm.txt"
    p.write_text('!Series_title\t"T"\n!Series_contact_name\t"Jane,,Doe"\n!Series_contact_email\t"jane@example.org"\n'
                 '!Series_contact_address\t"1 Lab Road"\n!Sample_geo_accession\t"GSM1"\n!Sample_contact_email\t"jane@example.org"\n'
                 '!series_matrix_table_begin\n"ID_REF"\t"GSM1"\n"P1"\t1.5\n!series_matrix_table_end\n')
    before = p.read_bytes()
    r = inspect_file(p)
    dumped = str(r.to_dict())
    assert "jane@example.org" not in dumped and "Jane" not in dumped and "Lab Road" not in dumped
    assert r.metadata["series"] == {"Series_title": ["T"]}
    assert r.metadata["omitted_contact_fields"] == ["Series_contact_address", "Series_contact_email", "Series_contact_name"]
    assert p.read_bytes() == before, "input file must not be modified"


def test_series_matrix(fixtures_dir):
    r = inspect_file(fixtures_dir / "series_matrix.txt.gz")
    assert r.format == "geo_series_matrix" and r.status == INSPECTED
    assert r.n_rows == 40 and r.feature_id_column == "ID_REF"
    assert r.candidate_sample_ids == [f"GSM90000{i}" for i in range(1, 6)]
    assert r.metadata["header_matches_sample_geo_accession"] is True
    assert r.metadata["sample_title"] == ["S1", "S2", "S3", "S4", "S5"]
    rows = dict(iter_feature_rows(r, max_features=2))
    assert list(rows) == ["P1", "P2"] and set(rows["P1"]) == set(r.candidate_sample_ids)


def test_sample_sheet_and_filelist(fixtures_dir):
    s = inspect_file(fixtures_dir / "sample_sheet.csv")
    assert s.table_kind == "sample_sheet" and s.duplicate_sample_ids == ["X_02"]
    f = inspect_file(fixtures_dir / "filelist.txt")
    assert f.table_kind == "file_manifest" and f.metadata["type_counts"] == {"TAR": 1, "BGX": 1}


def test_tar_listed_not_extracted(tmp_path):
    member = tmp_path / "GPL1_annotation.bgx"
    member.write_text("annotation")
    tar = tmp_path / "x_RAW.tar"
    with tarfile.open(tar, "w") as tf:
        tf.add(member, arcname=member.name)
    member.unlink()
    r = inspect_file(tar)
    assert r.table_kind == "archive" and r.metadata["n_members"] == 1
    assert not member.exists(), "archive must not be extracted"
    proc = classify_file(r, "expression_microarray")
    assert proc["state"] == METADATA_ONLY and proc["confidence"] in ("MEDIUM", "HIGH")


# --------------------------------------------------- processing-state audit
def _write_matrix(path, arr, prefix="S"):
    with open(path, "w") as fh:
        fh.write("ID_REF\t" + "\t".join(f"{prefix}{j}" for j in range(arr.shape[1])) + "\n")
        for i, row in enumerate(arr):
            fh.write(f"F{i}\t" + "\t".join(repr(float(v)) if not float(v).is_integer() else str(int(v)) for v in row) + "\n")


def test_quantile_normalized_log_scale_is_processed(tmp_path):
    rng = np.random.default_rng(0)
    base = np.sort(rng.normal(8, 1.5, 400))
    arr = np.column_stack([rng.permutation(base) for _ in range(6)])
    p = tmp_path / "anything.txt"
    _write_matrix(p, arr)
    out = classify_file(inspect_file(p), "expression_microarray")
    # Both observations come from one evidence source (values), so confidence is capped at MEDIUM.
    assert out["state"] == PROCESSED and out["confidence"] == "MEDIUM" and out["requires_review"]


def test_series_matrix_with_geo_annotation_reaches_high_confidence(fixtures_dir):
    out = classify_file(inspect_file(fixtures_dir / "series_matrix.txt.gz"), "expression_microarray")
    assert out["state"] == PROCESSED and out["confidence"] == "HIGH"
    assert {e["source"] for e in out["evidence"] if e["supports"] == PROCESSED} == {"value_distribution", "geo_annotation"}


def test_integer_counts_are_non_normalized(fixtures_dir):
    out = classify_file(inspect_file(fixtures_dir / "counts.txt.gz"), "expression_rnaseq")
    assert out["state"] == NON_NORMALIZED


def test_filename_alone_never_decides():
    evidence = [{"source": "filename", "observation": "x_normalized", "supports": PROCESSED, "weight": "strong"}]
    out = _decide(evidence, PROCESSED)
    assert out["state"] == UNKNOWN and out["requires_review"]


def test_uninspectable_file_is_unknown(fixtures_dir):
    out = classify_file(inspect_file(fixtures_dir / "malformed_ragged.tsv"), "expression_microarray")
    assert out["state"] == UNKNOWN and out["requires_review"]


def test_filename_contradiction_is_flagged(fixtures_dir, tmp_path):
    p = tmp_path / "GSE1_normalized.csv"
    shutil.copy(fixtures_dir / "sample_sheet.csv", p)
    out = classify_file(inspect_file(p), "methylation_array")
    assert out["state"] == METADATA_ONLY and out["filename_conflict"] and out["requires_review"]


def test_compare_matrices_identical_and_mapped(fixtures_dir):
    sm = inspect_file(fixtures_dir / "series_matrix.txt.gz")
    sup = inspect_file(fixtures_dir / "normalized.txt.gz")
    smap = {f"GSM90000{i}": f"S{i}" for i in range(1, 5)}
    out = compare_matrices(sm, sup, smap, max_features=40)
    assert out["status"] == "IDENTICAL_VALUES" and out["n_shared_samples"] == 4 and out["n_shared_features"] == 40
