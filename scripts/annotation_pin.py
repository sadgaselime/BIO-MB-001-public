#!/usr/bin/env python3
"""Annotation pin record builder (Tier B step 2; SAP v7:609 pin definition, v7:112 real-data rule).

NOT YET AUTHORIZED TO RUN ON THE PROJECT. Creating the pin requires a separate explicit PI authorization;
the command line refuses to start without --authorization.

The pin record lists, each with its SHA-256 (v7:609):
  * the approved classification tables, taken ONLY from regenerated v2 artifacts that pass
    code_identity.is_accepted(..., require_equivalence=True), i.e. produced under the identity lifecycle in the
    D8 environment with executed-code verification, byte-identical to v1 tables that still match their v1
    manifests (GPL570: D6-F gpl570_option_a; GPL6947/GPL10558: D6-G illumina_a0);
  * C15 cohort probe-presence v2 as validation evidence (v7:112 names C15 and A0);
  * the source annotation archives (verified against reference/bioconductor_3.23/download_manifest.json) and the
    shared Entrez snapshot org.Hs.eg.db 3.23.1;
  * the frozen gene-history v1 input of D6-F (its raw NCBI source is not retained and cannot be rebuilt; v7:643);
  * the governing mapping rules (D6-F, D6-G) by reference to the SAP, with the SAP's SHA-256 and status line;
  * the generating scripts' SHA-256 and code-identity aggregates (from each upstream identity record), the
    upstream manifests and identity records, and their validation evidence.
Every dependency is checked before anything is created and again inside the lifecycle; any problem stops the
run. Provisional Option A tables (illumina_option_a/v1) are never pinned. The pin installs nothing.
Output: reports/annotation_audit/annotation_pin/<version>/ under the code-identity lifecycle (never overwritten).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
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

PIN_OUT = "reports/annotation_audit/annotation_pin"
SAP = "reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md"
REFERENCE_MANIFEST = "reference/bioconductor_3.23/download_manifest.json"
ARCHIVES = {  # role -> archive file name in reference/bioconductor_3.23/
    "GPL570 platform package (D6-F)": "hgu133plus2.db_3.13.0.tar.gz",
    "GPL6947 platform package (D6-G)": "illuminaHumanv3.db_1.26.0.tar.gz",
    "GPL10558 platform package (D6-G)": "illuminaHumanv4.db_1.26.0.tar.gz",
    "shared Entrez snapshot": "org.Hs.eg.db_3.23.1.tar.gz",
}
FROZEN_INPUTS = {  # D6-F gene-history input; verified against its own manifest, never regenerated
    "dir": "reports/annotation_audit/ncbi_gene_history/v1",
    "table": "gene_history_reconciliation.tsv",
    "manifest": "reconciliation_manifest.json",
}
UPSTREAM = {  # key -> (artifact base dir, manifest name, generating script, pinned tables)
    "gpl570_option_a": ("reports/annotation_audit/gpl570_option_a", "counts_manifest.json",
                        "scripts/annotation_gpl570_option_a_counts.py", ("probe_set_classification.tsv",)),
    "illumina_a0": ("reports/annotation_audit/illumina_a0", "manifest.json",
                    "scripts/annotation_illumina_a0_classification.py",
                    ("a0_probe_classification.tsv", "a0_counts.tsv", "a0_discordant_probes.tsv")),
    "c15_cohort_probe_presence": ("reports/annotation_audit/c15_cohort_probe_presence", "manifest.json",
                                  "scripts/c15_cohort_probe_presence.py", ("probe_presence.tsv", "presence_counts.tsv")),
}
UPSTREAM_VERSION = "v2"
REFERENCE_VERSION = "v1"
EXPECTED_TABLE_SHA256 = {  # recorded values the regenerated tables must reproduce (v7:609 and the A0 manifest)
    "gpl570_option_a/probe_set_classification.tsv": "9e5f23fa8b10b3e120b518873905b79e5f338ca07ec83357e173d3a2ddea8d9c",
    "illumina_a0/a0_probe_classification.tsv": "6da6cf2c1d7d1911c17301d60c1f153f91856f405f7fde1faf6f553b3013ae7c",
    "illumina_a0/a0_counts.tsv": "a68aa75080026e175cb148994c42f4fbc38d0a3c386a526dc12cb0b63887d625",
    "illumina_a0/a0_discordant_probes.tsv": "e5b99695ac5b600bba0157c1d9b673be5f20a513e43e5887d0b7c6faccb85958",
}
MAPPING_RULES = {
    "D6-F": "GPL570 Option A: hgu133plus2.db 3.13.0 with Entrez IDs reconciled to org.Hs.eg.db 3.23.1 by the gene-history "
            "procedure, cutoff 20260318 (SAP v7:609)",
    "D6-G": "GPL6947/GPL10558 Option A0: package probes-table mapping, no gene-history reconciliation, multi-Entrez probes "
            "excluded, discordant probes retained and flagged, accession-only probes not added (SAP v7:609)",
}
REQUIRE_VENV = True  # D8-4 / Q3: .venv/bin/python -I
REQUIRE_EXECUTED_CODE = True  # executed code must equal the identity record (scripts/_executed_code.py)


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _validation_passed(manifest: dict) -> bool:
    v = manifest.get("validation")
    if isinstance(v, list):
        return bool(v) and all(c.get("pass") is True for c in v)
    if isinstance(v, dict):
        return v.get("status") == "OK"
    return False


def collect(root: Path | str) -> tuple[dict, list[str]]:
    """Check every dependency and assemble the pin record body. Returns (record, problems)."""
    root = Path(root).resolve()
    probs: list[str] = []
    rec: dict = {"upstream": {}, "archives": {}, "frozen_inputs": {}, "mapping_rules": MAPPING_RULES}
    current_env = ci.capture(root)["environment_records"]
    if not all(current_env.values()):
        probs.append(f"D8 environment records missing now: {[k for k, v in current_env.items() if not v]}")
    for key, (base, mname, script, tables) in UPSTREAM.items():
        d = root / base / UPSTREAM_VERSION
        reasons = ci.acceptance_problems(d, mname, require_equivalence=True, require_executed_code=True)
        if reasons:
            probs.append(f"{key}/{UPSTREAM_VERSION} not accepted: {reasons}")
            continue
        m = json.loads((d / mname).read_text(encoding="utf-8"))
        idrec = json.loads((d / ci.RECORD_FILENAME).read_text(encoding="utf-8"))
        eq = m["equivalence"]
        if eq.get("reference") != f"{base}/{REFERENCE_VERSION}":
            probs.append(f"{key}: equivalence reference is {eq.get('reference')}, not {base}/{REFERENCE_VERSION}")
        missing_eq = [t for t in tables if not (eq.get("tables", {}).get(t) or {}).get("identical")]
        if missing_eq:
            probs.append(f"{key}: no byte-identical equivalence for {missing_eq}")
        if not _validation_passed(m):
            probs.append(f"{key}: upstream validation did not pass")
        if m["identity"]["environment_records"] != current_env:
            probs.append(f"{key}: produced under different D8 environment records than now")
        gen = next((f for f in idrec["files"] if f["path"] == script), None)
        if gen is None:
            probs.append(f"{key}: generating script {script} absent from its identity record")
        try:  # the v1 reference must still match its own manifest (guards against an altered reference)
            v1_recorded = json.loads((root / base / REFERENCE_VERSION / mname).read_text(encoding="utf-8"))["determinism"]["output_sha256"]
        except (OSError, KeyError, ValueError) as e:
            v1_recorded = {}
            probs.append(f"{key}: {REFERENCE_VERSION} manifest unavailable or lacks determinism hashes: {e}")
        table_hashes = {}
        for t in tables:
            h = _sha(d / t)
            table_hashes[t] = h
            if v1_recorded.get(t) != h:
                probs.append(f"{key}/{t}: SHA-256 differs from the {REFERENCE_VERSION} manifest record")
            ref_t = root / base / REFERENCE_VERSION / t
            if not ref_t.is_file() or _sha(ref_t) != v1_recorded.get(t):
                probs.append(f"{key}/{REFERENCE_VERSION}/{t}: reference table differs from its own manifest")
            exp = EXPECTED_TABLE_SHA256.get(f"{key}/{t}")
            if exp is not None and h != exp:
                probs.append(f"{key}/{t}: SHA-256 {h} differs from the recorded {exp}")
        rec["upstream"][key] = {
            "dir": f"{base}/{UPSTREAM_VERSION}", "manifest": mname, "manifest_sha256": _sha(d / mname),
            "identity_record_sha256": m["identity"]["record_sha256"], "identity_aggregate_sha256": m["identity"]["aggregate_sha256"],
            "identity_git_head": m["identity"]["git_head"], "generating_script": script,
            "generating_script_sha256": gen["sha256"] if gen else None, "tables_sha256": table_hashes,
            "equivalence_reference": eq.get("reference"), "validation_passed": _validation_passed(m),
            "role": "validation evidence (v7:112)" if key == "c15_cohort_probe_presence" else "pinned classification table(s)",
        }
    refman_path = root / REFERENCE_MANIFEST
    if not refman_path.is_file():
        probs.append(f"{REFERENCE_MANIFEST} missing")
    else:
        refman = {e["file"]: e for e in json.loads(refman_path.read_text(encoding="utf-8"))["files"]}
        rec["reference_manifest_sha256"] = _sha(refman_path)
        for role, name in ARCHIVES.items():
            p = root / "reference/bioconductor_3.23" / name
            if not p.is_file() or name not in refman:
                probs.append(f"archive {name} missing or not in {REFERENCE_MANIFEST}")
                continue
            h = _sha(p)
            if h != refman[name]["sha256"]:
                probs.append(f"archive {name}: SHA-256 differs from {REFERENCE_MANIFEST}")
            rec["archives"][name] = {"role": role, "sha256": h}
    fd = root / FROZEN_INPUTS["dir"]
    try:
        fm = json.loads((fd / FROZEN_INPUTS["manifest"]).read_text(encoding="utf-8"))
        th = _sha(fd / FROZEN_INPUTS["table"])
        if th != fm["determinism"]["output_sha256"][FROZEN_INPUTS["table"]]:
            probs.append("frozen gene-history v1 table differs from its manifest")
        rec["frozen_inputs"]["gene_history_v1"] = {
            "table": f"{FROZEN_INPUTS['dir']}/{FROZEN_INPUTS['table']}", "table_sha256": th,
            "manifest_sha256": _sha(fd / FROZEN_INPUTS["manifest"]),
            "note": "frozen input; raw NCBI gene_history.gz not retained, so it cannot be rebuilt independently (v7:643)"}
    except (OSError, KeyError, ValueError) as e:
        probs.append(f"frozen gene-history v1 input unavailable: {e}")
    sap = root / SAP
    if sap.is_file():
        lines = sap.read_text(encoding="utf-8").split("\n")
        rec["sap"] = {"path": SAP, "sha256": _sha(sap), "status_line": lines[2] if len(lines) > 2 else None}
    else:
        probs.append(f"{SAP} missing")
    rec["d8_environment_records"] = current_env
    return rec, probs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--authorization", required=True,
                    help="reference to the explicit PI authorization for creating this pin (recorded verbatim)")
    a = ap.parse_args(argv)
    if not a.authorization.strip():
        print("REFUSED: --authorization is empty", file=sys.stderr)
        return 2
    _, probs = collect(ROOT)  # fail closed before anything is created
    if probs:
        print("REFUSED — DEPENDENCIES NOT VERIFIED:\n  " + "\n  ".join(probs), file=sys.stderr)
        return 1

    def compute(staging: Path):
        rec, again = collect(ROOT)  # re-checked inside the lifecycle
        if again:
            raise SystemExit("dependencies changed during the run: " + "; ".join(again))
        body = {"schema": "bio-mb-001/annotation-pin/v1", "authorization": a.authorization, **rec}
        data = (json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8")
        return {"annotation_pin_record.json": data}, {
            "status": "Annotation pin record (Tier B step 2). Pins the listed artifacts only; approves no analysis.",
            "command": f".venv/bin/python -I scripts/annotation_pin.py --version {a.version} --authorization <recorded>",
            "authorization": a.authorization}

    try:
        out = ci.run_with_identity(ROOT, ROOT / PIN_OUT / a.version, compute, manifest_name="manifest.json",
                                   require_venv=REQUIRE_VENV,
                                   executed_code=_ec if REQUIRE_EXECUTED_CODE else None,
                                   require_executed_code=REQUIRE_EXECUTED_CODE)
    except ci.RunFailed as e:
        print(f"RUN FAILED: {e}", file=sys.stderr)
        return 1
    print(f"accepted {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
