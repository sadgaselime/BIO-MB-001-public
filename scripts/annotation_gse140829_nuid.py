#!/usr/bin/env python3
"""D19-1 mapping for GSE140829: nuID -> ILMN probe ID -> approved A0 class (v7:622, approved 2026-10-19).

Route (D19-1): each GSE140829 Series Matrix feature (a nuID) is translated to its HT-12 v4 ILMN probe ID through the
pinned illuminaHumanv4.db 1.26.0 ExtraInfo NuID field. The translation is verified, failing closed on any disagreement,
against (b) lumiHumanIDMapping 1.10.1 table HumanHT12_V4_0_R2_15002873_B and (c) first-principles nuID decoding
(each body character is one base triplet of a 64-symbol alphabet; the decoded sequence must equal the annotated
50-base ProbeSequence). The gene mapping is the approved A0 rule (D6-G) taken unchanged from the pinned
illumina_a0/v2 classification of the HT-12 v4 (GPL10558) probe universe; presence is GSE140829's own Series Matrix.
Archives are read from reference/bioconductor_3.23 after their SHA-256 is checked against the annotation pin; only the
two SQLite members are extracted, into a temporary directory, and opened read-only. No expression value is read.
Runs under the code-identity lifecycle with executed-code verification; writes
reports/annotation_audit/gse140829_nuid/<version>/.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
import sqlite3
import sys
import tarfile
import tempfile
from collections import Counter, defaultdict
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
OUT_REL = "reports/annotation_audit/gse140829_nuid"
PIN_REL = "reports/annotation_audit/annotation_pin/v1"
A0_REL = "reports/annotation_audit/illumina_a0/v2"
REF = "reference/bioconductor_3.23"
V4_TAR, V4_MEMBER = "illuminaHumanv4.db_1.26.0.tar.gz", "illuminaHumanv4.db/inst/extdata/illuminaHumanv4.sqlite"
LUMI_TAR, LUMI_MEMBER = "lumiHumanIDMapping_1.10.1.tar.gz", "lumiHumanIDMapping/inst/extdata/lumiHumanIDMapping.sqlite"
LUMI_TABLE = "HumanHT12_V4_0_R2_15002873_B"
A0_SOURCE_COHORT = "GSE63061"   # the A0 rows that classify the full HT-12 v4 (GPL10558) probe universe
SM_REL = f"data/raw/{ACC}/{ACC}_series_matrix.txt.gz"
EXPECTED_FEATURES = 47008
NUID_CODE = [chr(c) for c in range(65, 91)] + [chr(c) for c in range(97, 123)] + [str(d) for d in range(10)] + ["_", "."]
COLUMNS = ["platform", "cohort", "probe_id", "ilmn_probe_id", "in_series_matrix", "a0_class", "a0_gene_id",
           "exclusion_or_unmapped_reason"]
REQUIRE_VENV = True
REQUIRE_EXECUTED_CODE = True


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_nuid(nuid: str) -> str:
    """Bases encoded by a nuID body (characters 2..n; each is one triplet, A, C, G, T = 0..3); padding retained."""
    val = {c: i for i, c in enumerate(NUID_CODE)}
    return "".join("ACGT"[v >> 4] + "ACGT"[(v >> 2) & 3] + "ACGT"[v & 3] for v in (val[c] for c in nuid[1:]))


def sequence_matches(nuid: str, seq: str | None) -> bool:
    if not seq:
        return False
    d = decode_nuid(nuid)
    return d.startswith(seq.upper()) and len(d) - len(seq) < 3


def series_matrix_ids(path: Path) -> list[str]:
    ids, on = [], False
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        for line in fh:
            if line.startswith("!series_matrix_table_begin"):
                on = True
                next(fh)
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if on:
                ids.append(line.split("\t", 1)[0].strip().strip('"'))   # the ID column only; values are not parsed
    return ids


def _extract(tar_path: Path, member: str, dest: Path) -> Path:
    with tarfile.open(tar_path, "r:gz") as tf:
        m = tf.getmember(member)
        if not m.isfile():
            raise SystemExit(f"STOP: {member} is not a regular file in {tar_path.name}")
        out = dest / Path(member).name
        with tf.extractfile(m) as src, open(out, "wb") as dst:
            dst.write(src.read())
    return out


def build(ids: list[str], extra: list[tuple], lumi: dict[str, str], a0: dict[str, dict]) -> tuple[list[dict], dict]:
    nu2ilmn, seq = defaultdict(set), {}
    for ilmn, nuid, s in extra:
        if nuid:
            nu2ilmn[nuid].add(ilmn)
        seq[ilmn] = s
    rows, problems = [], Counter()
    for n in ids:
        hits = nu2ilmn.get(n, set())
        if len(hits) != 1:
            problems["(a) not exactly one ILMN ID"] += 1
            continue
        ilmn = next(iter(hits))
        if lumi.get(n) != ilmn:
            problems["(b) lumiHumanIDMapping disagrees"] += 1
        if not sequence_matches(n, seq.get(ilmn)):
            problems["(c) decoded sequence disagrees"] += 1
        c = a0.get(ilmn)
        if c is None:
            problems["A0 classification missing"] += 1
            continue
        rows.append({"platform": "GPL15988", "cohort": ACC, "probe_id": n, "ilmn_probe_id": ilmn, "in_series_matrix": "yes",
                     "a0_class": c["a0_class"], "a0_gene_id": c["a0_gene_id"],
                     "exclusion_or_unmapped_reason": c["exclusion_or_unmapped_reason"]})
    counts = Counter(r["a0_class"] for r in rows)
    genes = {r["a0_gene_id"] for r in rows if r["a0_class"] == "eligible"}
    return rows, {"features": len(ids), "translated": len(rows), "problems": dict(problems),
                  "a0_class_counts": dict(sorted(counts.items())), "eligible_entrez_genes": len(genes)}


def _tsv(rows: list[dict]) -> bytes:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def produce(version: str) -> tuple[dict, dict]:
    probs = []
    pa = ci.acceptance_problems(ROOT / PIN_REL, "manifest.json", require_executed_code=True)
    if pa:
        probs.append(f"annotation pin not accepted: {pa}")
    pin = json.loads((ROOT / PIN_REL / "annotation_pin_record.json").read_text(encoding="utf-8")) if not pa else {}
    ref = {e["file"]: e for e in json.loads((ROOT / REF / "download_manifest.json").read_text(encoding="utf-8"))["files"]}
    if pin and _sha(ROOT / REF / "download_manifest.json") != pin["reference_manifest_sha256"]:
        probs.append("reference manifest differs from the annotation pin")
    if pin and pin["archives"][V4_TAR]["sha256"] != _sha(ROOT / REF / V4_TAR):
        probs.append(f"{V4_TAR} differs from the annotation pin")
    if _sha(ROOT / REF / LUMI_TAR) != ref[LUMI_TAR]["sha256"] or not ref[LUMI_TAR]["status"].startswith("VERIFIED"):
        probs.append(f"{LUMI_TAR} differs from the verified reference manifest")
    a0_sha = _sha(ROOT / A0_REL / "a0_probe_classification.tsv")
    if pin and pin["upstream"]["illumina_a0"]["tables_sha256"]["a0_probe_classification.tsv"] != a0_sha:
        probs.append("A0 table differs from the annotation pin")
    raw_man = json.loads((ROOT / f"data/raw/{ACC}/download_manifest.json").read_text(encoding="utf-8"))
    sm_sha = _sha(ROOT / SM_REL)
    if sm_sha != raw_man["files"][Path(SM_REL).name]["current"]["sha256"]:
        probs.append("Series Matrix SHA-256 differs from the download manifest")
    if probs:
        raise SystemExit("STOP — PRECONDITIONS NOT MET:\n  " + "\n  ".join(probs))
    with open(ROOT / A0_REL / "a0_probe_classification.tsv", encoding="utf-8", newline="") as fh:
        a0 = {r["probe_id"]: r for r in csv.DictReader(fh, delimiter="\t") if r["cohort"] == A0_SOURCE_COHORT}
    ids = series_matrix_ids(ROOT / SM_REL)
    with tempfile.TemporaryDirectory(prefix="bio_mb_001_nuid_") as tmp:
        v4 = _extract(ROOT / REF / V4_TAR, V4_MEMBER, Path(tmp))
        lu = _extract(ROOT / REF / LUMI_TAR, LUMI_MEMBER, Path(tmp))
        with sqlite3.connect(f"file:{v4}?mode=ro", uri=True) as c:
            extra = c.execute("select IlluminaID, NuID, ProbeSequence from ExtraInfo order by IlluminaID").fetchall()
        with sqlite3.connect(f"file:{lu}?mode=ro", uri=True) as c:
            lumi = dict(c.execute(f"select nuID, Probe_Id from '{LUMI_TABLE}'").fetchall())
    r1, s1 = build(ids, extra, lumi, a0)
    r2, s2 = build(ids, extra, lumi, a0)
    files = {"nuid_a0_classification.tsv": _tsv(r1)}
    if files["nuid_a0_classification.tsv"] != _tsv(r2) or s1 != s2:
        raise SystemExit("STOP: two runs are not byte-identical")
    checks = [(f"Series Matrix has {EXPECTED_FEATURES} unique features", len(ids) == EXPECTED_FEATURES == len(set(ids))),
              ("every feature translated to exactly one ILMN ID (a)", s1["translated"] == len(ids)),
              ("no disagreement with lumiHumanIDMapping (b) or sequence decoding (c)", not s1["problems"]),
              ("ILMN IDs are unique across features", len({r["ilmn_probe_id"] for r in r1}) == len(r1))]
    failed = [n for n, ok in checks if not ok]
    if failed:
        raise SystemExit("STOP — VERIFICATION FAILED (nothing accepted):\n  " + "\n  ".join(failed) + f"\n  {s1}")
    files["nuid_mapping_summary.json"] = (json.dumps(s1, indent=2, sort_keys=True) + "\n").encode()
    manifest = {"status": "D19-1 nuID mapping for GSE140829 (v7:622). Annotation only; no expression value read; no analysis.",
                "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "command": f".venv/bin/python -I scripts/annotation_gse140829_nuid.py --version {version}",
                "inputs": {SM_REL: sm_sha, f"{REF}/{V4_TAR}": _sha(ROOT / REF / V4_TAR), f"{REF}/{LUMI_TAR}": _sha(ROOT / REF / LUMI_TAR),
                           f"{A0_REL}/a0_probe_classification.tsv": a0_sha, f"{PIN_REL}/manifest.json": _sha(ROOT / PIN_REL / "manifest.json")},
                "summary": s1, "validation": [{"check": n, "pass": ok} for n, ok in checks],
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
