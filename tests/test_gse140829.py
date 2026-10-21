"""GSE140829 (synthetic): D19-1 nuID translation and its cross-checks, eligibility rules, C1 identity fields, QC configuration."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


nu = load("scripts/annotation_gse140829_nuid.py", "nuid140829")
el = load("scripts/eligibility_gse140829.py", "elig140829")
c1 = load("scripts/duplicate_review_c1_gse63060.py", "c1_140829")
qa = load("scripts/qc_stage_a_gse63060.py", "qca_140829")
qb = load("scripts/qc_stage_b_gse63060.py", "qcb_140829")

SEQ = "TTTTTTGAAGATCAGCTCCGTGGGGCTGGTTTTGGTCCACAGCATAACAG"   # published HT-12 v4 probe ILMN_1700306
NUID = "0..gjSdbqnr.rUSTBI"                                   # its nuID in GSE140829


def test_nuid_decoding_reproduces_the_probe_sequence():
    assert nu.decode_nuid(NUID).startswith(SEQ) and len(nu.decode_nuid(NUID)) == 51
    assert nu.sequence_matches(NUID, SEQ) and not nu.sequence_matches(NUID, "A" + SEQ[1:])


def test_build_fails_closed_on_any_disagreement():
    a0 = {"ILMN_1": {"a0_class": "eligible", "a0_gene_id": "7", "exclusion_or_unmapped_reason": ""}}
    extra = [("ILMN_1", NUID, SEQ)]
    rows, s = nu.build([NUID], extra, {NUID: "ILMN_1"}, a0)
    assert s["problems"] == {} and rows[0]["ilmn_probe_id"] == "ILMN_1" and s["eligible_entrez_genes"] == 1
    _, s = nu.build([NUID], extra, {NUID: "ILMN_9"}, a0)                      # (b) disagrees
    assert "(b) lumiHumanIDMapping disagrees" in s["problems"]
    _, s = nu.build([NUID], [("ILMN_1", NUID, "C" * 50)], {NUID: "ILMN_1"}, a0)  # (c) disagrees
    assert "(c) decoded sequence disagrees" in s["problems"]
    _, s = nu.build([NUID], extra + [("ILMN_2", NUID, SEQ)], {NUID: "ILMN_1"}, a0)  # (a) ambiguous
    assert "(a) not exactly one ILMN ID" in s["problems"]


def _sample(gsm, title, dx, rep="replicate 1"):
    return {"gsm": gsm, "title": title, "description": rep, "diagnosis": dx, "Sex": "Female", "age_at_draw": "70", "batch": "20"}


def test_eligibility_rules():
    sm = {"table_columns": ["G1", "G2", "G3", "G4"],
          "samples": [_sample("G1", "Whole blood, AD, 5786049087_A [ad_mci]", "AD"),
                      _sample("G2", "Whole blood, Control, 5786049087_B [ad_mci]", "Control"),
                      _sample("G3", "Whole blood, MCI, 5786049087_C [ad_mci]", "MCI", "replicate 2"),
                      _sample("G4", "Whole blood, X, 5786049087_C [ad_mci]", "Other")]}
    r = el.classify(sm, {})
    rows = {x["gsm"]: x for x in r["rows"]}
    assert rows["G1"]["primary_contrast_preqc"] == "case" and rows["G2"]["group"] == "CTL"
    assert "R2-ID:excluded(array_barcode)" in rows["G3"]["rules"] and rows["G3"]["replicate_annotation"] == "replicate 2"
    assert rows["G4"]["r5_category"] == "non_specific" and rows["G4"]["participant_code"] == ""


def test_c1_uses_no_participant_code_for_gse140829():
    c1.use("GSE140829")
    assert "!Sample_description" not in c1.IDENTITY_FIELDS
    meta = {"identity": {"gsm": ["G1", "G2"], "array_barcode": ["a", "b"]},
            "replicate_mentions": [{"index": 1, "field": "!Sample_description", "value": "replicate 2"}]}
    out = c1.find_candidates(meta)
    assert len(out) == 1 and out[0]["link"] == "deposited replicate annotation" and out[0]["gsms"] == "G2"


def test_qc_configuration_for_gse140829():
    assert qa.CONFIG["GSE140829"]["EXPECTED_SHAPE"] == (47008, 587) and "D19-1" in qa.CONFIG["GSE140829"]["AUTHORIZATION"]
    assert "GSE140829" in qb.CONFIG


def test_eligibility_gate_refuses_without_recorded_approval(tmp_path, monkeypatch):
    monkeypatch.setattr(el, "ROOT", tmp_path)
    raw = tmp_path / "data/raw/GSE140829"
    raw.mkdir(parents=True)
    import gzip, hashlib, json
    files = {}
    for n in (el.SM_NAME, *el.SUPPLEMENTARY):
        b = gzip.compress(b"x\n")
        (raw / n).write_bytes(b)
        files[n] = {"current": {"sha256": hashlib.sha256(b).hexdigest()}}
    (raw / "download_manifest.json").write_text(json.dumps({"files": files}))
    with pytest.raises(SystemExit, match="approval not found"):
        el.produce("v_test")
