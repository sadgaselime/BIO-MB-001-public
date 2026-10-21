#!/usr/bin/env python3
"""Tier B step 3 for GSE140829: pre-QC eligibility under the GSE140829 eligibility rules (v7:605, approved 2026-10-19).

Rules (GSE140829 eligibility rules §): R1 universe = the 587 GSM columns of the Series Matrix; R2-ID = GSM and array
barcode (parsed from the title) unique; R3/R4 = AD vs Control from char:diagnosis, MCI outside the primary contrast
(P1); R5 = no ambiguous-label category (three deposited values; any other value would be excluded and stop the
count check); R2-COV fields recorded: age_at_draw, Sex, batch (unit). char:connectivity_zscore and char:apoe_status are
not read. The sample description ("replicate 1"/"replicate 2") is recorded verbatim for the C1 duplicate review (D18);
it is not a participant code. R11: supplementary-file columns without a GSM record are listed, never added.
Metadata only: no expression value is read. Runs under the code-identity lifecycle with executed-code verification;
writes reports/eligibility/GSE140829/<version>/.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_MAIN_CODE = sys._getframe(0).f_code  # this module's executed code object (executed-code check, D8-3)


def _executed_code_registry():
    """Load scripts/_executed_code.py once per process (bootstrap; it verifies itself in check())."""
    name = "bio_mb_001_executed_code"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/_executed_code.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


_ec = _executed_code_registry()
if __name__ == "__main__":
    _ec.install(ROOT, _MAIN_CODE, __file__)  # before any project module is imported
sys.path.insert(0, str(ROOT / "src"))
from biomarker_project import code_identity as ci  # noqa: E402

ACC = "GSE140829"
OUT_REL = f"reports/eligibility/{ACC}"
SM_NAME = f"{ACC}_series_matrix.txt.gz"
SUPPLEMENTARY = (f"{ACC}_final_normalized_data.txt.gz", f"{ACC}_raw_data.txt.gz")
PHENOTYPE_REL = f"data/processed/{ACC}/phenotype_table.tsv"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
APPROVAL_MARKERS = ("GSE140829 eligibility rules §", "**APPROVED 2026-10-19", "D19-1")
LABELS = {"AD": "AD", "Control": "CTL", "MCI": "MCI"}
PRIMARY = {"AD": "case", "CTL": "control"}
EXPECTED = {"universe": 587, "AD": 204, "CTL": 249, "MCI": 134, "R5": 0}
BARCODE_RX = re.compile(r"(\d{9,12}_[A-L])")
LOG_COLUMNS = ["gsm", "array_barcode", "participant_code", "geo_status", "r5_category", "group", "eligible_in_dataset_preqc",
               "primary_contrast_preqc", "age", "gender", "batch", "replicate_annotation", "rules"]
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _unquote(v: str) -> str:
    v = v.strip()
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] == '"' else v


def read_samples(path: Path) -> dict:
    wanted = {"!Sample_geo_accession": "gsm", "!Sample_title": "title", "!Sample_description": "description"}
    fields, chars, header = {}, [], None
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        for line in fh:
            if line.startswith("!series_matrix_table_begin"):
                header = [_unquote(x) for x in next(fh).rstrip("\r\n").split("\t")]
                break   # expression rows are never read
            key, _, rest = line.rstrip("\r\n").partition("\t")
            if key in wanted:
                if wanted[key] in fields:
                    raise SystemExit(f"STOP: {key} appears more than once")
                fields[wanted[key]] = [_unquote(x) for x in rest.split("\t")]
            elif key == "!Sample_characteristics_ch1":
                chars.append([_unquote(x) for x in rest.split("\t")])
    if header is None or header[0] != "ID_REF" or set(fields) != set(wanted.values()):
        raise SystemExit("STOP: Series Matrix header or sample fields not found")
    n = len(fields["gsm"])
    samples = []
    for i in range(n):
        c = {}
        for row in chars:
            k, sep, v = row[i].partition(":")
            if sep and k.strip() in ("diagnosis", "Sex", "age_at_draw", "batch"):   # only the approved fields
                c.setdefault(k.strip(), []).append(v.strip())
        samples.append({"gsm": fields["gsm"][i], "title": fields["title"][i], "description": fields["description"][i],
                        **{k: ";".join(c.get(k, [])) for k in ("diagnosis", "Sex", "age_at_draw", "batch")}})
    return {"table_columns": header[1:], "samples": samples}


def barcode(title: str) -> str:
    m = BARCODE_RX.findall(title)
    return m[0] if len(m) == 1 else ""


def classify(sm: dict, supp_headers: dict[str, list[str]]) -> dict:
    s = sm["samples"]
    bc = [barcode(x["title"]) for x in s]
    cg, cb = Counter(x["gsm"] for x in s), Counter(bc)
    rows = []
    for x, b in zip(s, bc):
        rules = ["R1"]
        dup = [k for k, v, cnt in (("gsm", x["gsm"], cg), ("array_barcode", b, cb)) if not v or cnt[v] > 1]
        group = LABELS.get(x["diagnosis"], "")
        cat = "mapped" if group else ("missing" if not x["diagnosis"] else "non_specific")
        eligible = not dup
        contrast = PRIMARY.get(group, "") if eligible else ""
        if dup:
            rules.append("R2-ID:excluded(" + ",".join(dup) + ")")
        if cat != "mapped":
            rules.append(f"R5:excluded({cat})")
        elif dup:
            pass
        elif group == "MCI":
            rules.append("R4:outside_primary_contrast")
        else:
            rules.append(f"R3:{contrast}")
        rows.append({"gsm": x["gsm"], "array_barcode": b, "participant_code": "", "geo_status": x["diagnosis"],
                     "r5_category": cat, "group": group, "eligible_in_dataset_preqc": str(eligible),
                     "primary_contrast_preqc": contrast, "age": x["age_at_draw"], "gender": x["Sex"], "batch": x["batch"],
                     "replicate_annotation": x["description"], "rules": ";".join(rules)})
    known = set(bc)
    r11 = []
    for name, header in supp_headers.items():
        seen = set()
        for pos, col in enumerate(header, start=1):
            for b in BARCODE_RX.findall(col):
                if b not in known and b not in seen:
                    seen.add(b)
                    r11.append({"file": name, "column_position": pos, "header": col,
                                "reason": "no eligible GEO GSM record (expression-only array)"})
    tally = Counter(r["group"] for r in rows if r["eligible_in_dataset_preqc"] == "True")
    con = Counter(r["primary_contrast_preqc"] for r in rows if r["primary_contrast_preqc"])
    summary = [{"quantity": "R1 universe (Series Matrix GSM columns)", "n": len(rows)},
               {"quantity": "R2-ID excluded", "n": sum(r["eligible_in_dataset_preqc"] == "False" for r in rows)},
               {"quantity": "R5 excluded from contrasts", "n": sum(r["r5_category"] != "mapped" for r in rows)},
               {"quantity": "AD (eligible, pre-QC)", "n": tally["AD"]}, {"quantity": "CTL (eligible, pre-QC)", "n": tally["CTL"]},
               {"quantity": "MCI (retained, outside primary contrast; R4)", "n": tally["MCI"]},
               {"quantity": "primary contrast cases (AD, pre-QC)", "n": con["case"]},
               {"quantity": "primary contrast controls (CTL, pre-QC)", "n": con["control"]},
               {"quantity": "batches", "n": len({r["batch"] for r in rows})},
               {"quantity": "arrays annotated 'replicate 2' (for C1)", "n": sum(r["replicate_annotation"] == "replicate 2" for r in rows)},
               {"quantity": "R11 supplementary arrays without a GSM record", "n": len(r11)}]
    checks = [(f"R1: universe equals {EXPECTED['universe']}", len(rows) == EXPECTED["universe"]),
              ("R1: table column header equals !Sample_geo_accession in order", sm["table_columns"] == [x["gsm"] for x in s]),
              ("R2-ID: GSM and barcode unique and present", all(r["eligible_in_dataset_preqc"] == "True" for r in rows)),
              (f"AD = {EXPECTED['AD']}", tally["AD"] == EXPECTED["AD"]), (f"CTL = {EXPECTED['CTL']}", tally["CTL"] == EXPECTED["CTL"]),
              (f"MCI = {EXPECTED['MCI']}", tally["MCI"] == EXPECTED["MCI"]),
              ("R5 excluded = 0", sum(r["r5_category"] != "mapped" for r in rows) == EXPECTED["R5"]),
              ("age, sex and batch recorded for every array", all(r["age"] and r["gender"] and r["batch"] for r in rows))]
    return {"rows": rows, "r11": r11, "summary": summary, "checks": checks}


def _tsv(rows: list[dict], cols: list[str]) -> bytes:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def supplementary_header(path: Path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        return fh.readline().rstrip("\r\n").split("\t")


def phenotype_crosscheck(rows: list[dict]) -> list[tuple[str, bool]]:
    with open(ROOT / PHENOTYPE_REL, encoding="utf-8", newline="") as fh:
        ph = {r["geo_accession"]: r for r in csv.DictReader(fh, delimiter="\t")}
    same = set(ph) == {r["gsm"] for r in rows}
    agree = same and all(ph[r["gsm"]]["char:diagnosis"] == r["geo_status"] and ph[r["gsm"]]["char:Sex"] == r["gender"]
                         and ph[r["gsm"]]["char:batch"] == r["batch"] for r in rows)
    return [("phenotype table has the same GSM set", same), ("phenotype table agrees on diagnosis, sex and batch", agree)]


def produce(version: str) -> tuple[dict, dict]:
    raw = ROOT / f"data/raw/{ACC}"
    man = json.loads((raw / "download_manifest.json").read_text(encoding="utf-8"))["files"]
    prov, probs = {}, []
    for name in (SM_NAME, *SUPPLEMENTARY):
        h = _sha(raw / name)
        prov[f"data/raw/{ACC}/{name}"] = h
        if h != man[name]["current"]["sha256"]:
            probs.append(f"{name}: SHA-256 differs from the download manifest")
    sap = (ROOT / SAP_REL).read_text(encoding="utf-8") if (ROOT / SAP_REL).is_file() else ""
    if any(m not in sap for m in APPROVAL_MARKERS):
        probs.append("GSE140829 eligibility rules / D19-1 approval not found in the SAP")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    sm = read_samples(raw / SM_NAME)
    supp = {n: supplementary_header(raw / n) for n in SUPPLEMENTARY}
    r1, r2 = classify(sm, supp), classify(sm, supp)
    files = {"eligibility_log.tsv": _tsv(r1["rows"], LOG_COLUMNS),
             "r11_supplementary_columns.tsv": _tsv(r1["r11"], ["file", "column_position", "header", "reason"]),
             "eligibility_summary.tsv": _tsv(r1["summary"], ["quantity", "n"])}
    if files["eligibility_log.tsv"] != _tsv(r2["rows"], LOG_COLUMNS):
        raise SystemExit("STOP: two runs are not byte-identical")
    checks = r1["checks"] + phenotype_crosscheck(r1["rows"])
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED (nothing accepted):\n  " + "\n  ".join(failed))
    prov[PHENOTYPE_REL] = _sha(ROOT / PHENOTYPE_REL)
    manifest = {"status": f"Tier B step 3: {ACC} pre-QC eligibility under the GSE140829 eligibility rules (v7:605). Metadata "
                          "only; no expression value read; no QC, duplicate review, model or analysis.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/eligibility_gse140829.py --version {version}",
                "fields_not_read": ["char:connectivity_zscore", "char:apoe_status"], "expected_counts": EXPECTED,
                "inputs": prov | {"sap_sha256": _sha(ROOT / SAP_REL)},
                "validation": [{"check": n, "pass": ok} for n, ok in checks],
                "determinism": {"runs_compared": 2, "identical": True,
                                "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}}
    return files, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    a = ap.parse_args(argv)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / a.version, lambda s: produce(a.version),
                                   require_venv=REQUIRE_VENV, executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
