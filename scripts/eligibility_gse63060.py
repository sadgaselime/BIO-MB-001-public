#!/usr/bin/env python3
"""Tier B step 3: cohort eligibility under the approved D2 rules (SAP v7:605), metadata only.

Cohorts: GSE63060 (default) and GSE63061 (--accession GSE63061; D2 rules applied as for GSE63060, PI instruction
2026-10-19). File names below are shown for GSE63060; each cohort uses its own files and expected counts (CONFIG).

Inputs (each verified against data/raw/GSE63060/download_manifest.json before use):
  * GSE63060_series_matrix.txt.gz: only the !Sample_* header lines (GSM, title = array barcode,
    description = participant code, characteristics) and the column-header line of the data table are read.
    No expression value is read: reading stops at the table header.
  * GSE63060_normalized.txt.gz and GSE63060_non-normalized.txt.gz: only their first (header) line, for R11.
  * data/processed/GSE63060/phenotype_table.tsv: a cross-check of GSM, title, description and status only.
Precondition: the annotation pin (Tier B step 2) exists and is accepted (reports/annotation_audit/annotation_pin/v1).

Rules applied (D2, approved 2026-10-10):
  R1  universe = the GSM columns of the Series Matrix (329 expected);
  R2-ID  exact-string uniqueness of GSM, title (barcode) and description (participant code); a non-unique value
      excludes the sample (uniqueness does not prove biological participant identity);
  R3  primary contrast by GEO `status`: AD vs CTL;  R4  MCI retained in the dataset, outside the primary contrast;
  R5  missing / borderline / transitional / non-specific / conflicting labels are excluded from contrasts and logged;
  R6  no exclusion or relabelling from inferred converter status or participant-code letters (nothing computed);
  R10 inherited submitter QC recorded as not independently auditable (documentation only);
  R11 expression-only or empty-header columns of the supplementary files are not eligible and never become samples;
  R12 the "included in case -control study" flag is not used for eligibility (recorded only);
  R13 this checksummed eligibility/exclusion log, created before any case-control model.
Not applied here: R2-COV (complete-case per model, at model time), R7/D4 (no age exclusion; age is a covariate),
R8/R9 and all QC (QC Stage A), duplicate handling (D18). The result is the PRE-QC eligible population.
Submitter contact fields in the Series Matrix are never read into the outputs.

Runs under the code-identity lifecycle with executed-code verification; writes reports/eligibility/GSE63060/<version>/
(never overwritten; failed runs kept as <version>.FAILED-<run_id>/).
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

ACC = "GSE63060"
OUT_REL = f"reports/eligibility/{ACC}"
PIN_REL = "reports/annotation_audit/annotation_pin/v1"
SM_NAME = f"{ACC}_series_matrix.txt.gz"
SUPPLEMENTARY = (f"{ACC}_normalized.txt.gz", f"{ACC}_non-normalized.txt.gz")
SUPPLEMENTARY_SUFFIX = ".AVG_Signal"
PHENOTYPE_REL = f"data/processed/{ACC}/phenotype_table.tsv"
CANONICAL = ("AD", "CTL", "MCI")
PRIMARY = {"AD": "case", "CTL": "control"}
EXPECTED = {"universe": 329, "AD": 145, "CTL": 104, "MCI": 80, "R5": 0}  # D2 (v7:605): pre-QC 145 AD vs 104 CTL; 80 MCI
# Per-cohort configuration. GSE63061: D2 rules applied as for GSE63060 (PI instruction 2026-10-19; v7:605); counts from the
# GEO records (Phase 1 audit): 388 GSM columns; AD 139, CTL 134, MCI 109; 6 R5-category labels (3 borderline MCI, 1 OTHER,
# 1 "CTL to AD", 1 "MCI to CTL").
CONFIG = {
    "GSE63060": {"EXPECTED": dict(EXPECTED)},
    "GSE63061": {"EXPECTED": {"universe": 388, "AD": 139, "CTL": 134, "MCI": 109, "R5": 6}},
}


def use(acc: str) -> None:
    """Point the module at one cohort (paths and expected counts)."""
    global ACC, OUT_REL, SM_NAME, SUPPLEMENTARY, PHENOTYPE_REL, EXPECTED
    if acc not in CONFIG:
        raise SystemExit(f"STOP: no eligibility configuration for {acc}")
    ACC, OUT_REL = acc, f"reports/eligibility/{acc}"
    SM_NAME, SUPPLEMENTARY = f"{acc}_series_matrix.txt.gz", (f"{acc}_normalized.txt.gz", f"{acc}_non-normalized.txt.gz")
    PHENOTYPE_REL, EXPECTED = f"data/processed/{acc}/phenotype_table.tsv", dict(CONFIG[acc]["EXPECTED"])
SOOD_FLAG = "included in case -control study"
REQUIRE_VENV = True  # D8-4: .venv/bin/python -I
REQUIRE_EXECUTED_CODE = True  # executed code must equal the identity record (scripts/_executed_code.py)


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _unquote(v: str) -> str:
    v = v.strip()
    return v[1:-1] if len(v) >= 2 and v[0] == v[-1] == '"' else v


def read_series_matrix_samples(path: Path) -> dict:
    """!Sample_* metadata needed by D2 and the table's column header; stops at the table header line."""
    wanted = {"!Sample_geo_accession": "gsm", "!Sample_title": "title", "!Sample_description": "description"}
    fields: dict[str, list[str]] = {}
    characteristics: list[list[str]] = []
    header = None
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        for line in fh:
            if line.startswith("!series_matrix_table_begin"):
                header = [_unquote(x) for x in next(fh).rstrip("\r\n").split("\t")]
                break  # expression rows are never read
            key, _, rest = line.rstrip("\r\n").partition("\t")
            if key in wanted:
                if wanted[key] in fields:
                    raise SystemExit(f"STOP: {key} appears more than once")
                fields[wanted[key]] = [_unquote(x) for x in rest.split("\t")]
            elif key == "!Sample_characteristics_ch1":
                characteristics.append([_unquote(x) for x in rest.split("\t")])
    if header is None or header[0] != "ID_REF":
        raise SystemExit("STOP: Series Matrix table header not found or does not start with ID_REF")
    if set(fields) != set(wanted.values()):
        raise SystemExit(f"STOP: missing sample fields {sorted(set(wanted.values()) - set(fields))}")
    n = len(fields["gsm"])
    if any(len(v) != n for v in fields.values()) or any(len(c) != n for c in characteristics):
        raise SystemExit("STOP: sample metadata lines differ in length")
    samples = []
    for i in range(n):
        chars: dict[str, list[str]] = {}
        for row in characteristics:
            k, sep, v = row[i].partition(":")
            if sep:
                chars.setdefault(k.strip(), []).append(v.strip())
        samples.append({"gsm": fields["gsm"][i], "title": fields["title"][i], "description": fields["description"][i],
                        "status_values": chars.get("status", []), "age": ";".join(chars.get("age", [])),
                        "gender": ";".join(chars.get("gender", [])), "sood_flag": ";".join(chars.get(SOOD_FLAG, []))})
    return {"table_columns": header[1:], "samples": samples}


def r5_category(values: list[str]) -> tuple[str, str]:
    """(category, label) under R5 for a sample's GEO status value(s)."""
    distinct = sorted({v for v in values if v})
    if not distinct:
        return "missing", ""
    if len(distinct) > 1:
        return "conflicting", "|".join(distinct)
    label = distinct[0]
    if label in CANONICAL:
        return "mapped", label
    low = label.lower()
    if "borderline" in low:
        return "borderline", label
    if " to " in low:
        return "transitional", label
    return "non_specific", label


def supplementary_header(path: Path) -> list[str]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        return fh.readline().rstrip("\r\n").split("\t")


def classify(sm: dict, supp_headers: dict[str, list[str]]) -> dict:
    """Apply R1-R5, R11 and R12 (recorded); deterministic for given inputs."""
    samples = sm["samples"]
    gsms = [s["gsm"] for s in samples]
    counts = {k: Counter(s[k] for s in samples) for k in ("gsm", "title", "description")}
    rows = []
    for s in samples:
        rules = ["R1"]
        dup = [k for k in ("gsm", "title", "description") if counts[k][s[k]] > 1 or not s[k]]
        cat, label = r5_category(s["status_values"])
        group = label if cat == "mapped" else ""
        eligible_dataset = not dup
        contrast = PRIMARY.get(group, "") if eligible_dataset else ""
        if dup:
            rules.append("R2-ID:excluded(" + ",".join(dup) + ")")
        if cat != "mapped":
            rules.append(f"R5:excluded({cat})")
        elif dup:
            pass  # excluded by R2-ID: no contrast assignment
        elif group == "MCI":
            rules.append("R4:outside_primary_contrast")
        else:
            rules.append(f"R3:{contrast}")
        rows.append({"gsm": s["gsm"], "array_barcode": s["title"], "participant_code": s["description"],
                     "geo_status": "|".join(s["status_values"]), "r5_category": cat, "group": group,
                     "eligible_in_dataset_preqc": str(eligible_dataset), "primary_contrast_preqc": contrast,
                     "age": s["age"], "gender": s["gender"], "sood_flag_recorded_not_used_R12": s["sood_flag"],
                     "rules": ";".join(rules)})
    titles = {s["title"] for s in samples}
    r11 = []
    for name, header in supp_headers.items():
        for pos, col in enumerate(header[1:], start=2):
            barcode = col[: -len(SUPPLEMENTARY_SUFFIX)] if col.endswith(SUPPLEMENTARY_SUFFIX) else col
            if not barcode.strip():
                r11.append({"file": name, "column_position": pos, "header": col, "reason": "empty header"})
            elif barcode not in titles:
                r11.append({"file": name, "column_position": pos, "header": col,
                            "reason": "no eligible GEO GSM record (expression-only array)"})
    tally = Counter(r["group"] for r in rows if r["eligible_in_dataset_preqc"] == "True")
    contrast = Counter(r["primary_contrast_preqc"] for r in rows if r["primary_contrast_preqc"])
    summary = [
        {"quantity": "R1 universe (Series Matrix GSM columns)", "n": len(rows)},
        {"quantity": "R2-ID excluded", "n": sum(r["eligible_in_dataset_preqc"] == "False" for r in rows)},
        {"quantity": "R5 excluded from contrasts", "n": sum(r["r5_category"] != "mapped" for r in rows)},
        {"quantity": "AD (eligible, pre-QC)", "n": tally["AD"]},
        {"quantity": "CTL (eligible, pre-QC)", "n": tally["CTL"]},
        {"quantity": "MCI (retained, outside primary contrast; R4)", "n": tally["MCI"]},
        {"quantity": "primary contrast cases (AD, pre-QC)", "n": contrast["case"]},
        {"quantity": "primary contrast controls (CTL, pre-QC)", "n": contrast["control"]},
        {"quantity": "R11 supplementary columns not eligible", "n": len(r11)},
    ]
    checks = [
        (f"R1: universe equals the expected {EXPECTED['universe']} GSM columns", len(rows) == EXPECTED["universe"]),
        ("R1: table column header equals !Sample_geo_accession in order", sm["table_columns"] == gsms),
        ("R2-ID: GSM, barcode and participant code unique", all(r["eligible_in_dataset_preqc"] == "True" for r in rows)),
        (f"D2 pre-QC count AD = {EXPECTED['AD']}", tally["AD"] == EXPECTED["AD"]),
        (f"D2 pre-QC count CTL = {EXPECTED['CTL']}", tally["CTL"] == EXPECTED["CTL"]),
        (f"D2 count MCI = {EXPECTED['MCI']}", tally["MCI"] == EXPECTED["MCI"]),
        (f"R5 excluded = {EXPECTED.get('R5', 0)}", sum(r["r5_category"] != "mapped" for r in rows) == EXPECTED.get("R5", 0)),
        ("R11: no supplementary column became a sample", len(rows) == len(set(gsms))),
    ]
    return {"rows": rows, "r11": r11, "summary": summary, "checks": checks}


def _tsv(rows: list[dict], columns: list[str]) -> bytes:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


LOG_COLUMNS = ["gsm", "array_barcode", "participant_code", "geo_status", "r5_category", "group",
               "eligible_in_dataset_preqc", "primary_contrast_preqc", "age", "gender",
               "sood_flag_recorded_not_used_R12", "rules"]


def verify_inputs(root: Path) -> tuple[dict, list[str]]:
    prov, problems = {"files": {}}, []
    raw = root / f"data/raw/{ACC}"
    man = json.loads((raw / "download_manifest.json").read_text(encoding="utf-8"))["files"]
    for name in (SM_NAME, *SUPPLEMENTARY):
        exp = man[name]["current"]["sha256"]
        h = _sha(raw / name)
        prov["files"][f"data/raw/{ACC}/{name}"] = {"sha256": h, "manifest_sha256": exp}
        if h != exp:
            problems.append(f"{name}: SHA-256 differs from the download manifest")
    prov["files"][PHENOTYPE_REL] = {"sha256": _sha(root / PHENOTYPE_REL)}
    pin = root / PIN_REL
    pin_probs = ci.acceptance_problems(pin, "manifest.json", require_executed_code=True)
    if pin_probs:
        problems.append(f"annotation pin (Tier B step 2) not accepted: {pin_probs}")
    else:
        prov["annotation_pin"] = {"dir": PIN_REL, "record_sha256": _sha(pin / "annotation_pin_record.json"),
                                  "manifest_sha256": _sha(pin / "manifest.json")}
    return prov, problems


def phenotype_crosscheck(root: Path, rows: list[dict]) -> list[tuple[str, bool]]:
    with open(root / PHENOTYPE_REL, encoding="utf-8", newline="") as fh:
        ph = {r["geo_accession"]: r for r in csv.DictReader(fh, delimiter="\t")}
    same_set = set(ph) == {r["gsm"] for r in rows}
    agree = same_set and all(ph[r["gsm"]]["title"] == r["array_barcode"] and ph[r["gsm"]]["description"] == r["participant_code"]
                             and ph[r["gsm"]]["char:status"] == r["geo_status"] for r in rows)
    return [("phenotype table has the same GSM set", same_set),
            ("phenotype table agrees on barcode, participant code and status", agree)]


def produce(version: str) -> tuple[dict, dict]:
    prov, problems = verify_inputs(ROOT)
    if problems:
        raise SystemExit("STOP — INPUT VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    raw = ROOT / f"data/raw/{ACC}"
    sm = read_series_matrix_samples(raw / SM_NAME)
    supp = {n: supplementary_header(raw / n) for n in SUPPLEMENTARY}
    r1, r2 = classify(sm, supp), classify(sm, supp)
    files = {"eligibility_log.tsv": _tsv(r1["rows"], LOG_COLUMNS),
             "r11_supplementary_columns.tsv": _tsv(r1["r11"], ["file", "column_position", "header", "reason"]),
             "eligibility_summary.tsv": _tsv(r1["summary"], ["quantity", "n"])}
    if files != {"eligibility_log.tsv": _tsv(r2["rows"], LOG_COLUMNS),
                 "r11_supplementary_columns.tsv": _tsv(r2["r11"], ["file", "column_position", "header", "reason"]),
                 "eligibility_summary.tsv": _tsv(r2["summary"], ["quantity", "n"])}:
        raise SystemExit("STOP: two runs are not byte-identical")
    checks = r1["checks"] + phenotype_crosscheck(ROOT, r1["rows"])
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED (nothing accepted):\n  " + "\n  ".join(failed))
    manifest = {
        "status": f"Tier B step 3: {ACC} pre-QC eligibility under D2 (v7:605). Metadata only; no expression value "
                  "read; no QC, duplicate review, model or analysis. Approves nothing.",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": f".venv/bin/python -I scripts/eligibility_gse63060.py --version {version}",
        "rules_applied": ["R1", "R2-ID", "R3", "R4", "R5", "R11", "R12 (recorded, not used)", "R13 (this log)"],
        "rules_documented_only": {"R6": "no converter-based exclusion or relabelling; code letters unused",
                                  "R10": "inherited submitter QC not independently auditable (no sample-level records)"},
        "not_applied_here": {"R2-COV": "complete-case per statistical model, at model time",
                             "R7/D4": "no age-based exclusion; age is a covariate (D4)",
                             "R8/R9": "QC Stage A (D5/D22), Tier B step 5", "D18": "duplicate review, Tier B step 4"},
        "expected_counts_D2": EXPECTED,
        "inputs": prov,
        "validation": [{"check": n, "pass": ok} for n, ok in checks],
        "determinism": {"runs_compared": 2, "identical": True,
                        "output_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}},
    }
    return files, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--accession", default="GSE63060", choices=sorted(CONFIG))
    a = ap.parse_args(argv)
    if a.accession != ACC:
        use(a.accession)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / a.version, lambda staging: produce(a.version),
                                   manifest_name="manifest.json", require_venv=REQUIRE_VENV,
                                   executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
