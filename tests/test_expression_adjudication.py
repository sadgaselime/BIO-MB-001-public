"""Phase 2A adjudication tests (synthetic data only; no network)."""
import gzip
import hashlib
import importlib.util
import io
import json
import shutil
import tarfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from biomarker_project.expression_adjudication import (
    annotation_summary, compare_full, empty_label, parse_delimited_matrix, parse_series_matrix, rank_identity_mapping,
    read_bgx_from_tar,
)

FIXTURES = Path(__file__).parent / "fixtures"
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "phase2a_expression_adjudication.py"


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _gz(path, text):
    with gzip.open(path, "wb") as fh:
        fh.write(text.encode())


def _target(n_probes=60, samples=("S1", "S2", "S3"), seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.normal(8, 1.5, (n_probes, len(samples))), index=[f"P{i}" for i in range(n_probes)],
                        columns=list(samples))


# -------------------------------------------------------------- parsing
def test_split_record_repaired_in_memory_only(tmp_path):
    p = tmp_path / "m.txt.gz"
    _gz(p, "ID_REF\tA\tB\r\nP1\t1.0\t2.0\r\nP2\r\n\t3.0\t4.0\r\nP3\t5.0\t6.0\r\n")
    before = _sha(p)
    r = parse_delimited_matrix(p)
    assert list(r.data.index) == ["P1", "P2", "P3"]
    assert r.data.loc["P2"].tolist() == [3.0, 4.0]
    assert r.repaired_split_records == [{"id_line": 3, "values_line": 4, "feature_id": "P2",
                                         "repair": "ID line and following empty-ID value line joined (in memory only)"}]
    assert r.unrepaired_malformed == [] and r.line_endings["crlf"] == 5
    assert _sha(p) == before


def test_other_malformed_rows_are_excluded_and_logged(tmp_path):
    p = tmp_path / "m.txt"
    p.write_text("ID_REF\tA\tB\nP1\t1\t2\nP2\t3\nP3\t4\t5\t6\n\t7\t8\n")
    r = parse_delimited_matrix(p)
    assert list(r.data.index) == ["P1"]
    assert [b["line"] for b in r.unrepaired_malformed] == [3, 4, 5]
    assert r.repaired_split_records == []


def test_empty_headers_get_positional_labels(tmp_path):
    p = tmp_path / "m.txt"
    p.write_text("ID\tA.AVG_Signal\t\tC.AVG_Signal\t\nP1\t1\t2\t3\t4\n")
    r = parse_delimited_matrix(p)
    assert list(r.data.columns) == ["A.AVG_Signal", empty_label(3), "C.AVG_Signal", empty_label(5)]  # file column positions
    assert r.summary()["empty_header_positions_1based"] == [3, 5]


def test_series_matrix_parse(fixtures_dir):
    df, meta = parse_series_matrix(fixtures_dir / "series_matrix.txt.gz")
    assert df.shape == (40, 5) and list(df.columns) == meta["Sample_geo_accession"][0]


# ----------------------------------------------------------- comparison
def test_compare_full_identical_and_different():
    a = _target()
    b = a.rename(columns={"S1": "T1", "S2": "T2", "S3": "T3"})
    same = compare_full(a, b, {"S1": "T1", "S2": "T2", "S3": "T3"})
    assert same["identical"] and same["n_values_compared"] == 180
    b.iloc[5, 1] += 1e-6
    diff = compare_full(a, b, {"S1": "T1", "S2": "T2", "S3": "T3"})
    assert not diff["identical"] and diff["n_values_differing"] == 1


# ------------------------------------------------------- column mapping
def _source_from(target, rename):
    """Monotone (exp) transform per column: preserves within-column ranks exactly."""
    src = np.exp2(target) * 3.7
    return src.rename(columns=rename)


def test_unlabelled_columns_assigned_by_rank_identity():
    t = _target(samples=("S1", "S2", "S3", "S4"))
    src = _source_from(t, {"S2": empty_label(2), "S4": empty_label(4)})
    m = rank_identity_mapping(src, t)
    assert m["validation"]["passed"] and m["validation"]["n_best_match_is_own_column"] == 2
    got = {a["source_column"]: (a["assigned_target"], a["status"]) for a in m["assignments"]}
    assert got == {empty_label(2): ("S2", "CONTENT_MATCH_UNIQUE"), empty_label(4): ("S4", "CONTENT_MATCH_UNIQUE")}


def test_ambiguous_or_noisy_unlabelled_columns_stay_unresolved():
    t = _target(samples=("S1", "S2", "S3"))
    t["S3"] = t["S2"]  # two indistinguishable targets
    src = _source_from(t, {"S2": empty_label(2)}).drop(columns="S3")
    m = rank_identity_mapping(src, t)
    a = m["assignments"][0]
    assert a["status"] == "UNRESOLVED" and a["assigned_target"] is None
    rng = np.random.default_rng(5)
    t2 = _target(samples=("S1", "S2"))
    noisy = _source_from(t2, {"S2": empty_label(2)})
    noisy[empty_label(2)] = rng.permutation(noisy[empty_label(2)].to_numpy())  # unrelated column
    a2 = rank_identity_mapping(noisy, t2)["assignments"][0]
    assert a2["status"] == "UNRESOLVED" and a2["reasons_not_assigned"]


def test_assignment_refused_when_validation_fails():
    t = _target(samples=("S1", "S2", "S3"))
    src = _source_from(t, {"S3": empty_label(3)})
    src["S1"] = src["S1"].sample(frac=1, random_state=1).to_numpy()  # a labelled column that no longer matches
    m = rank_identity_mapping(src, t)
    assert not m["validation"]["passed"]
    assert m["assignments"][0]["status"] == "UNRESOLVED"
    assert "method validation on labelled columns failed" in m["assignments"][0]["reasons_not_assigned"]


# ----------------------------------------------------------- annotation
BGX = ("Illumina\n[Heading]\nDate\t1/1/2008\nNumber of Probes\t4\n[Probes]\n"
       "Species\tSource\tSymbol\tEntrez_Gene_ID\tProbe_Id\tProbe_Type\tChromosome\tRefSeq_ID\tDefinition\n"
       "Hs\tRefSeq\tGENEA\t1\tP0\tS\t1\tNM_1\tdefA\n"
       "Hs\tRefSeq\tGENEA\t1\tP1\tA\t1\tNM_1\tdefA\n"
       "Hs\tUnigene\t\t\tP2\tS\t\t\tdefB\n"
       "Hs\tRefSeq\tLOC9\t9\tP3\tS\t2\tNM_9\tdefC\n"
       "[Controls]\nProbe_Id\nC1\n")


def _bgx_tar(tmp_path):
    member = tmp_path / "GPL1_test.bgx.gz"
    _gz(member, BGX)
    tar = tmp_path / "X_RAW.tar"
    with tarfile.open(tar, "w") as tf:
        tf.add(member, arcname=member.name)
    member.unlink()
    return tar, member.name


def test_bgx_read_in_memory_and_summarised(tmp_path):
    tar, name = _bgx_tar(tmp_path)
    heading, probes, sha = read_bgx_from_tar(tar, name)
    assert heading["Number of Probes"] == "4" and len(probes) == 4 and len(sha) == 64
    assert not (tmp_path / name).exists(), "nothing extracted to disk"
    s = annotation_summary(probes, pd.Index(["P0", "P1", "P2", "P3", "PX"]))
    assert s["n_missing_from_annotation"] == 1 and s["n_with_symbol"] == 3 and s["n_with_entrez"] == 3
    assert s["n_symbols_with_multiple_probes"] == 1 and s["n_probes_in_multi_probe_symbols"] == 2
    assert s["n_placeholder_symbols_LOC_or_HS"] == 1


# --------------------------------------------------------- end-to-end
def _load_script():
    spec = importlib.util.spec_from_file_location("phase2a_script", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def mini(tmp_path):
    acc = "GSE1000001"
    root = tmp_path / "proj"
    (root / "config").mkdir(parents=True)
    cfg = (FIXTURES / "valid_config.yaml").read_text().replace(
        "      - {name: GSE1000001_normalized.txt.gz, location: suppl, retrieve: true, sample_id_field: title}",
        "      - {name: GSE1000001_normalized.txt.gz, location: suppl, retrieve: true, sample_id_field: title}\n"
        "      - {name: GSE1000001_non-normalized.txt.gz, location: suppl, retrieve: true, sample_id_field: title}\n"
        "      - {name: GSE1000001_RAW.tar, location: suppl, retrieve: true}")
    (root / "config" / "datasets.yaml").write_text(cfg)
    raw = root / "data" / "raw" / acc
    raw.mkdir(parents=True)
    shutil.copy(FIXTURES / "series_matrix.txt.gz", raw / f"{acc}_series_matrix.txt.gz")
    sm, _ = parse_series_matrix(raw / f"{acc}_series_matrix.txt.gz")
    titles = {f"GSM90000{i}": f"S{i}" for i in range(1, 6)}
    norm = sm.rename(columns=titles)
    norm["X9"] = norm["S1"].to_numpy()[::-1]  # extra column not in GEO records
    rows = ["ID_REF\t" + "\t".join(norm.columns)] + [f"{i}\t" + "\t".join(map(str, r)) for i, r in zip(norm.index, norm.to_numpy())]
    _gz(raw / f"{acc}_normalized.txt.gz", "\r\n".join(rows) + "\r\n")
    nn = np.exp2(norm) * 2.5
    hdr = ["IND_ID"] + [("" if c == "S5" else f"{c}.AVG_Signal") for c in nn.columns]
    extra = pd.DataFrame(100.0, index=["Q1", "Q2"], columns=nn.columns)
    nn = pd.concat([nn, extra])
    _gz(raw / f"{acc}_non-normalized.txt.gz", "\n".join(["\t".join(hdr)] + [f"{i}\t" + "\t".join(map(str, r)) for i, r in zip(nn.index, nn.to_numpy())]) + "\n")
    bgx_rows = "".join(f"Hs\tRefSeq\tG{k}\t{k}\t{p}\tS\t1\tNM_{k}\td\n" for k, p in enumerate(nn.index))
    bgx = BGX.split("Hs\tRefSeq\tGENEA")[0] + bgx_rows + "[Controls]\nProbe_Id\nC1\n"
    member = tmp_path / "GPL9999999_test.bgx.gz"
    _gz(member, bgx)
    with tarfile.open(raw / f"{acc}_RAW.tar", "w") as tf:
        tf.add(member, arcname=member.name)
    files = {}
    for f in raw.iterdir():
        files[f.name] = {"current": {}, "history": [{"sha256": _sha(f), "available_locally": True}]}
    (raw / "download_manifest.json").write_text(json.dumps({"files": files}))
    proc = root / "data" / "processed" / acc
    proc.mkdir(parents=True)
    ph = pd.DataFrame({"geo_accession": list(titles), "title": list(titles.values()),
                       "diagnosis_raw": ["AD", "CTL", "AD", "CTL", "AD"], "diagnosis_canonical": ["AD", "HC", "AD", "HC", "AD"],
                       "char:included in case -control study": ["yes", "no", "yes", "no", "no"]})
    ph.to_csv(proc / "phenotype_table.tsv", sep="\t", index=False)
    return root, acc


def test_end_to_end_outputs_and_no_overwrite(mini):
    root, acc = mini
    data_before = {p: _sha(p) for p in (root / "data").rglob("*") if p.is_file()}
    mod = _load_script()
    assert mod.main(["--accession", acc, "--version", "v1", "--project-root", str(root)]) == 0
    out = root / "reports" / "phase2a" / acc / "v1"
    s = json.loads((out / "adjudication_summary.json").read_text())
    assert all(v["verified"] for v in s["inputs"].values())
    assert s["series_matrix_vs_normalized_full"]["identical"] is True
    assert list(s["normalized_extra_columns"]) == ["X9"]
    a = s["empty_header_mapping"]["assignments"]
    assert [(x["assigned_target"], x["geo_accession"], x["status"]) for x in a] == [("S5", "GSM900005", "CONTENT_MATCH_UNIQUE")]
    assert s["processing_and_scale"]["n_probes_dropped_in_normalized"] == 2
    assert (out / "probe_annotation_provisional_bgx2008.tsv").exists()
    assert {p: _sha(p) for p in (root / "data").rglob("*") if p.is_file()} == data_before, "data/ must be untouched"
    with pytest.raises(SystemExit, match="already exists"):
        mod.main(["--accession", acc, "--version", "v1", "--project-root", str(root)])


def test_checksum_mismatch_refuses_to_run(mini):
    root, acc = mini
    man = root / "data" / "raw" / acc / "download_manifest.json"
    d = json.loads(man.read_text())
    d["files"][f"{acc}_normalized.txt.gz"]["history"][0]["sha256"] = "0" * 64
    man.write_text(json.dumps(d))
    with pytest.raises(SystemExit, match="checksum mismatch"):
        _load_script().main(["--accession", acc, "--version", "v1", "--project-root", str(root)])
    assert not (root / "reports" / "phase2a").exists()
