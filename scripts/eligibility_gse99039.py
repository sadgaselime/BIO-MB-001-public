#!/usr/bin/env python3
"""Tier B step 3 for GSE99039: pre-QC eligibility under the GSE99039 eligibility rules E-99 (v7:605, approved 2026-10-20).

Rules (E-99): R1 universe = the 558 GSM columns of the Series Matrix; R2-ID = GSM accession unique; the title is checked for
uniqueness only (GSE99039 title rule: a duplicated title is a duplicate-review candidate, not an R2-ID exclusion);
char:subject_id is the participant identifier (an identical value is a C1 candidate; a missing value is recorded, not an
exclusion). Contrast labels from char:disease label exactly as deposited, with no relabelling: IPD, GPD and
GENETIC_UNAFFECTED, each vs CONTROL (v6 §9.2 roles; D13). All other labels are outside the specificity contrasts (P1) and
descriptive only. R2-COV fields recorded: Sex, batch (unit) and age at exam (S15). Not read: learning set, UPDRS, Hoehn &
Yahr, MoCA, age at first symptoms, mutated-gene field. Metadata only: no expression value is read. Runs under the
code-identity lifecycle with executed-code verification; writes reports/eligibility/GSE99039/<version>/.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
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

ACC = "GSE99039"
OUT_REL = f"reports/eligibility/{ACC}"
SM_NAME = f"{ACC}_series_matrix.txt.gz"
PHENOTYPE_REL = f"data/processed/{ACC}/phenotype_table.tsv"
SAP_REL = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
APPROVAL_MARKERS = ("GSE99039 eligibility rules § (E-99)", "R8-570a §")
CONTRAST = {"IPD": "case:IPD", "GPD": "case:GPD", "GENETIC_UNAFFECTED": "case:GENETIC_UNAFFECTED", "CONTROL": "control"}
EXPECTED = {"universe": 558, "CONTROL": 233, "IPD": 205, "GPD": 41, "GENETIC_UNAFFECTED": 22, "other": 57}
CHAR_KEYS = {"disease label": "label", "Sex": "sex", "batch": "batch", "age at exam": "age", "subject_id": "subject_id"}
LOG_COLUMNS = ["gsm", "array_barcode", "participant_code", "geo_status", "r5_category", "group", "eligible_in_dataset_preqc",
               "primary_contrast_preqc", "age", "gender", "batch", "rules"]
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


def _missing(v: str) -> bool:
    return v.strip() in ("", "NA", "ND", "N")


def read_samples(path: Path) -> dict:
    wanted = {"!Sample_geo_accession": "gsm", "!Sample_title": "title"}
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
    samples = []
    for i in range(len(fields["gsm"])):
        c = {}
        for row in chars:
            k, sep, v = row[i].partition(":")
            if sep and k.strip() in CHAR_KEYS:   # only the approved fields
                c.setdefault(CHAR_KEYS[k.strip()], []).append(v.strip())
        samples.append({"gsm": fields["gsm"][i], "title": fields["title"][i],
                        **{k: ";".join(c.get(k, [])) for k in CHAR_KEYS.values()}})
    return {"table_columns": header[1:], "samples": samples}


def classify(sm: dict) -> dict:
    s = sm["samples"]
    cg, ct = Counter(x["gsm"] for x in s), Counter(x["title"] for x in s)
    cs = Counter(x["subject_id"] for x in s if x["subject_id"])
    rows = []
    for x in s:
        rules = ["R1"]
        eligible = bool(x["gsm"]) and cg[x["gsm"]] == 1
        label = x["label"]
        contrast = CONTRAST.get(label, "") if eligible else ""
        if not eligible:
            rules.append("R2-ID:excluded(gsm)")
        if ct[x["title"]] > 1:
            rules.append("title:duplicate(C1 candidate; title rule)")
        if not x["subject_id"]:
            rules.append("subject_id:missing(recorded)")
        elif cs[x["subject_id"]] > 1:
            rules.append("subject_id:duplicate(C1 candidate)")
        if not label:
            rules.append("label:missing(P1)")
        elif label in CONTRAST:
            rules.append(f"contrast:{contrast}")
        else:
            rules.append("P1:outside_specificity_contrasts(descriptive)")
        rows.append({"gsm": x["gsm"], "array_barcode": x["title"], "participant_code": x["subject_id"], "geo_status": label,
                     "r5_category": "mapped" if label else "missing", "group": label,
                     "eligible_in_dataset_preqc": str(eligible), "primary_contrast_preqc": contrast,
                     "age": "" if _missing(x["age"]) else x["age"],
                     "gender": x["sex"] if x["sex"] in ("Female", "Male") else "", "batch": x["batch"], "rules": ";".join(rules)})
    tally = Counter(r["group"] for r in rows)
    other = sum(n for g, n in tally.items() if g not in CONTRAST)
    summary = [{"quantity": "R1 universe (Series Matrix GSM columns)", "n": len(rows)},
               {"quantity": "R2-ID excluded (GSM)", "n": sum(r["eligible_in_dataset_preqc"] == "False" for r in rows)},
               *({"quantity": f"{g} (deposited label)", "n": tally[g]} for g in CONTRAST),
               {"quantity": "other labels (P1, descriptive only)", "n": other},
               {"quantity": "arrays with a duplicated title (C1 candidates)", "n": sum(v for v in ct.values() if v > 1)},
               {"quantity": "arrays with a duplicated subject_id (C1 candidates)", "n": sum(v for v in cs.values() if v > 1)},
               {"quantity": "missing subject_id (recorded)", "n": sum(not x["subject_id"] for x in s)},
               {"quantity": "Sex recorded", "n": sum(bool(r["gender"]) for r in rows)},
               {"quantity": "age at exam recorded", "n": sum(bool(r["age"]) for r in rows)},
               {"quantity": "batches", "n": len({r["batch"] for r in rows})}]
    checks = [(f"R1: universe equals {EXPECTED['universe']}", len(rows) == EXPECTED["universe"]),
              ("R1: table column header equals !Sample_geo_accession in order", sm["table_columns"] == [x["gsm"] for x in s]),
              ("R2-ID: GSM unique and present", all(r["eligible_in_dataset_preqc"] == "True" for r in rows)),
              *((f"{g} = {EXPECTED[g]}", tally[g] == EXPECTED[g]) for g in CONTRAST),
              (f"other labels = {EXPECTED['other']}", other == EXPECTED["other"]),
              ("batch recorded for every array", all(r["batch"] for r in rows))]
    return {"rows": rows, "summary": summary, "checks": checks}


def _tsv(rows: list[dict], cols: list[str]) -> bytes:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def phenotype_crosscheck(rows: list[dict]) -> list[tuple[str, bool]]:
    with open(ROOT / PHENOTYPE_REL, encoding="utf-8", newline="") as fh:
        ph = {r["geo_accession"]: r for r in csv.DictReader(fh, delimiter="\t")}
    same = set(ph) == {r["gsm"] for r in rows}
    agree = same and all(ph[r["gsm"]]["char:disease label"] == r["geo_status"] and ph[r["gsm"]]["char:batch"] == r["batch"]
                         and ph[r["gsm"]]["char:subject_id"] == r["participant_code"] for r in rows)
    return [("phenotype table has the same GSM set", same), ("phenotype table agrees on label, batch and subject_id", agree)]


def produce(version: str) -> tuple[dict, dict]:
    raw = ROOT / f"data/raw/{ACC}"
    probs = []
    man = json.loads((raw / "download_manifest.json").read_text(encoding="utf-8"))["files"] if (raw / "download_manifest.json").is_file() else {}
    sm_sha = _sha(raw / SM_NAME) if (raw / SM_NAME).is_file() else None
    if sm_sha is None or sm_sha != man.get(SM_NAME, {}).get("current", {}).get("sha256"):
        probs.append(f"{SM_NAME}: SHA-256 differs from the download manifest")
    sap = (ROOT / SAP_REL).read_text(encoding="utf-8") if (ROOT / SAP_REL).is_file() else ""
    if any(m not in sap for m in APPROVAL_MARKERS):
        probs.append("GSE99039 eligibility rules (E-99) / R8-570a approval not found in the SAP")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    sm = read_samples(raw / SM_NAME)
    r1, r2 = classify(sm), classify(sm)
    files = {"eligibility_log.tsv": _tsv(r1["rows"], LOG_COLUMNS), "eligibility_summary.tsv": _tsv(r1["summary"], ["quantity", "n"])}
    if files["eligibility_log.tsv"] != _tsv(r2["rows"], LOG_COLUMNS):
        raise SystemExit("STOP: two runs are not byte-identical")
    checks = r1["checks"] + phenotype_crosscheck(r1["rows"])
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED (nothing accepted):\n  " + "\n  ".join(failed))
    manifest = {"status": f"Tier B step 3: {ACC} pre-QC eligibility under the GSE99039 eligibility rules E-99 (v7:605). Metadata "
                          "only; no expression value read; no QC, duplicate review, model or analysis.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/eligibility_gse99039.py --version {version}",
                "fields_not_read": ["char:learning set", "char:updrs *", "char:hoehn & yahr *", "char:moca score",
                                    "char:age at 1st symptoms", "char:genetic (mutated pd genes)", "char:tissue"],
                "expected_counts": EXPECTED,
                "inputs": {f"data/raw/{ACC}/{SM_NAME}": sm_sha, PHENOTYPE_REL: _sha(ROOT / PHENOTYPE_REL), "sap_sha256": _sha(ROOT / SAP_REL)},
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
