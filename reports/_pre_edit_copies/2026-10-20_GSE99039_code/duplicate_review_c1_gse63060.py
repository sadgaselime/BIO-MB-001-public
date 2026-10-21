#!/usr/bin/env python3
"""Tier B step 4: GSE63060 duplicate-review metadata candidates (C1; v6 §4 workflow, D18 approved 2026-10-18).

Candidate sources (fixed in v6 §4 before any review), metadata only:
  * identical GSM accession, array barcode (title) or participant code (description) within the cohort (R2-ID);
  * deposited replicate annotations: any !Sample_* field (other than characteristics values and submitter contact
    fields) whose value mentions "replicate", and any characteristics KEY that names a replicate.
Allowed evidence only (v6 §4): GSM, title/barcode, description (participant code), replicate fields, GEO processing
fields. Diagnosis, age, sex and every other phenotype VALUE are never read into the review table, and no
association result is used. Expression-based candidates (C2) belong to Tier B step 6 and are not handled here.

Handling under D18 (v7:621): R2-ID duplicate GSM or barcode -> R2-ID identity failure (Tier P2); D-1 (deposited
replicate annotation naming its partner) -> keep one array (not labelled as a replicate, otherwise lowest GSM),
exclude and list the others; any other link, including a shared description value -> D-1u (retained, flagged,
listed). A reviewer decision is needed only when candidates exist; the designated reviewer is recorded per (iv).

Precondition: the GSE63060 eligibility output (Tier B step 3) exists and is accepted.
Runs under the code-identity lifecycle with executed-code verification; writes
reports/duplicate_review/GSE63060/c1_<version>/ (never overwritten).
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
from collections import defaultdict
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
OUT_REL = f"reports/duplicate_review/{ACC}"
ELIG_REL = f"reports/eligibility/{ACC}/v1"
SM_NAME = f"{ACC}_series_matrix.txt.gz"
EXCLUDED_FIELD_PREFIXES = ("!Sample_contact_",)  # submitter personal data: never read
CONFIG = ("GSE63060", "GSE63061", "GSE140829")  # GSE63061: same C1 review (PI instruction 2026-10-19); GSE140829 (v7:605)


def use(acc: str) -> None:
    global ACC, OUT_REL, ELIG_REL, SM_NAME
    global IDENTITY_FIELDS
    ACC, OUT_REL, ELIG_REL, SM_NAME = acc, f"reports/duplicate_review/{acc}", f"reports/eligibility/{acc}/v1", f"{acc}_series_matrix.txt.gz"
    IDENTITY_FIELDS = COHORT_IDENTITY_FIELDS.get(acc, IDENTITY_FIELDS)


IDENTITY_FIELDS = {"!Sample_geo_accession": "gsm", "!Sample_title": "array_barcode", "!Sample_description": "participant_code"}
# GSE140829 has no participant-code field: its description holds the deposited replicate annotation ("replicate 1"/
# "replicate 2"), which the replicate-mention rule captures; it is not used as a participant code (v7:605).
COHORT_IDENTITY_FIELDS = {"GSE140829": {"!Sample_geo_accession": "gsm", "!Sample_title": "array_barcode"}}
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


def read_allowed_metadata(path: Path) -> dict:
    """Identity fields, replicate mentions and characteristics KEYS only; stops at the data table header."""
    ident: dict[str, list[str]] = {}
    replicate_mentions: list[dict] = []
    characteristic_keys: set[str] = set()
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        for line in fh:
            if line.startswith("!series_matrix_table_begin"):
                break  # expression rows are never read
            if not line.startswith("!Sample_") or line.startswith(EXCLUDED_FIELD_PREFIXES):
                continue
            key, _, rest = line.rstrip("\r\n").partition("\t")
            values = [_unquote(x) for x in rest.split("\t")]
            if key in IDENTITY_FIELDS:
                ident[IDENTITY_FIELDS[key]] = values
            if key == "!Sample_characteristics_ch1":
                for i, v in enumerate(values):  # only the KEY of each characteristic is inspected
                    k = v.partition(":")[0].strip()
                    characteristic_keys.add(k)
                    if "replicate" in k.lower():
                        replicate_mentions.append({"index": i, "field": f"characteristics key '{k}'", "value": v})
                continue
            for i, v in enumerate(values):
                if "replicate" in v.lower():
                    replicate_mentions.append({"index": i, "field": key, "value": v})
    if set(ident) != set(IDENTITY_FIELDS.values()):
        raise SystemExit("STOP: identity fields missing from the Series Matrix")
    return {"identity": ident, "replicate_mentions": replicate_mentions, "characteristic_keys": sorted(characteristic_keys)}


def find_candidates(meta: dict) -> list[dict]:
    ident = meta["identity"]
    n = len(ident["gsm"])
    out = []
    for field in [f for f in ("gsm", "array_barcode", "participant_code") if f in ident]:
        groups = defaultdict(list)
        for i in range(n):
            groups[ident[field][i]].append(i)
        for value, idx in sorted(groups.items()):
            if len(idx) > 1:
                cat = "R2-ID identity failure (Tier P2)" if field != "participant_code" else "D-1u (shared description value)"
                out.append({"source": "C1", "link": f"identical {field}", "value": value,
                            "gsms": ";".join(ident["gsm"][i] for i in idx), "category": cat, "action": "pending reviewer"})
    for m in meta["replicate_mentions"]:
        i = m["index"]
        out.append({"source": "C1", "link": "deposited replicate annotation", "value": f"{m['field']}: {m['value']}",
                    "gsms": ident["gsm"][i], "category": "D-1 if it names its partner, otherwise D-1u/D-2 per D18",
                    "action": "pending reviewer"})
    return out


REVIEW_COLUMNS = ["source", "link", "value", "gsms", "category", "action"]


def _tsv(rows, cols) -> bytes:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def produce(version: str) -> tuple[dict, dict]:
    raw = ROOT / f"data/raw/{ACC}"
    problems = []
    exp = json.loads((raw / "download_manifest.json").read_text(encoding="utf-8"))["files"][SM_NAME]["current"]["sha256"]
    sm_sha = _sha(raw / SM_NAME)
    if sm_sha != exp:
        problems.append("Series Matrix SHA-256 differs from the download manifest")
    elig = ROOT / ELIG_REL
    ep = ci.acceptance_problems(elig, "manifest.json", require_executed_code=True)
    if ep:
        problems.append(f"eligibility (Tier B step 3) not accepted: {ep}")
    if problems:
        raise SystemExit("STOP — INPUT VERIFICATION FAILED:\n  " + "\n  ".join(problems))
    with open(elig / "eligibility_log.tsv", encoding="utf-8", newline="") as fh:
        elig_gsms = [r["gsm"] for r in csv.DictReader(fh, delimiter="\t")]  # only the GSM column is used
    meta = read_allowed_metadata(raw / SM_NAME)
    c1, c2 = find_candidates(meta), find_candidates(meta)
    files = {"c1_review_table.tsv": _tsv(c1, REVIEW_COLUMNS)}
    if files != {"c1_review_table.tsv": _tsv(c2, REVIEW_COLUMNS)}:
        raise SystemExit("STOP: two runs are not byte-identical")
    checks = [("universe equals the eligibility log GSMs, in order", meta["identity"]["gsm"] == elig_gsms),
              ("review table carries no diagnosis or phenotype column", set(REVIEW_COLUMNS).isdisjoint(
                  {"status", "diagnosis", "age", "gender", "sex", "group"}))]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED (nothing accepted):\n  " + "\n  ".join(failed))
    status = ("complete: no C1 candidates; no reviewer decision required" if not c1
              else "C1 candidates found: review by the designated project reviewer pending (D18 (iv)); not complete")
    log = {"cohort": ACC, "tier_b_step": 4, "candidate_source": "C1 (metadata)", "status": status,
           "n_candidates": len(c1), "fields_examined": sorted(IDENTITY_FIELDS) + [
               "all other !Sample_* values except characteristics values and !Sample_contact_* (for 'replicate')",
               "characteristics keys only (for 'replicate')"],
           "characteristic_keys_seen": meta["characteristic_keys"], "rule_reference": "v6 §4; D18 (v7:621), approved 2026-10-18",
           "reviewer": "not applicable (no candidates)" if not c1 else "PENDING: designated project reviewer not yet named",
           "review_date": None, "c2_expression_candidates": "not handled here (Tier B step 6, after QC Stage A)"}
    files["duplicate_review_log_c1.json"] = (json.dumps(log, indent=2, sort_keys=True) + "\n").encode("utf-8")
    manifest = {"status": f"Tier B step 4 (C1 metadata) for {ACC}: {status}. Approves nothing; no analysis.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/duplicate_review_c1_gse63060.py --version {version}",
                "inputs": {f"data/raw/{ACC}/{SM_NAME}": {"sha256": sm_sha, "manifest_sha256": exp},
                           ELIG_REL: {"manifest_sha256": _sha(elig / "manifest.json"),
                                      "eligibility_log_sha256": _sha(elig / "eligibility_log.tsv")}},
                "validation": [{"check": n, "pass": ok} for n, ok in checks],
                "determinism": {"runs_compared": 2, "identical": True,
                                "output_sha256": {"c1_review_table.tsv": hashlib.sha256(files["c1_review_table.tsv"]).hexdigest()}}}
    return files, manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--accession", default="GSE63060", choices=sorted(CONFIG))
    a = ap.parse_args(argv)
    if a.accession != ACC:
        use(a.accession)
    try:
        out = ci.run_with_identity(ROOT, ROOT / OUT_REL / f"c1_{a.version}", lambda s: produce(a.version),
                                   require_venv=REQUIRE_VENV, executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
