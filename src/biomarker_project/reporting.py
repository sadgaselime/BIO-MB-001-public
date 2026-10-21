"""Machine-readable (JSON/CSV) and human-readable (Markdown) audit reports.

Evidence vocabulary used in every report:
  VERIFIED   - directly established from retrieved records or inspected files
  REPORTED   - stated in a publication, the project brief or metadata, not reproduced
  UNRESOLVED - insufficient evidence to decide
  FAILED     - an operation was attempted and failed

Overall dataset audit statuses (there is deliberately no 'PASS'):
  FAILED                       - sample metadata could not be retrieved/parsed
  INCOMPLETE                   - some requested file was not retrieved or not inspectable
  COMPLETE_REVIEW_REQUIRED     - all requested steps ran; open issues need human review
  COMPLETE_NO_ISSUES_DETECTED  - all requested steps ran and no issue was detected
                                 (still subject to scientific review before use)
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Iterable

from .download import atomic_write_text

VERIFIED, REPORTED, UNRESOLVED, FAILED = "VERIFIED", "REPORTED", "UNRESOLVED", "FAILED"
EVIDENCE_LEVELS = (VERIFIED, REPORTED, UNRESOLVED, FAILED)

AUDIT_FAILED = "FAILED"
AUDIT_INCOMPLETE = "INCOMPLETE"
AUDIT_REVIEW = "COMPLETE_REVIEW_REQUIRED"
AUDIT_CLEAN = "COMPLETE_NO_ISSUES_DETECTED"


def finding(topic: str, status: str, statement: str, evidence: str = "") -> dict[str, str]:
    if status not in EVIDENCE_LEVELS:
        raise ValueError(f"unknown evidence status {status!r}")
    return {"topic": topic, "status": status, "statement": statement, "evidence": evidence}


def determine_audit_status(result: dict[str, Any]) -> tuple[str, list[str]]:
    """Derive the overall status from what actually happened. Never returns PASS."""
    reasons = []
    if not result.get("metadata", {}).get("sample_records_available"):
        return AUDIT_FAILED, ["GEO sample records could not be retrieved or parsed"]
    for f in result.get("files", []):
        if not f.get("requested"):
            continue
        r = f.get("retrieval", {})
        if not r.get("available_locally"):
            reasons.append(f"{f['name']}: requested but not available ({r.get('status')})")
            continue
        insp = f.get("inspection") or {}
        if insp.get("status") not in ("INSPECTED", "INSPECTED_WITH_LIMITATIONS"):
            reasons.append(f"{f['name']}: could not be inspected ({insp.get('status')})")
    if any(s.get("status") == FAILED for s in result.get("steps", [])):
        reasons.extend(f"step failed: {s['step']} ({s.get('error')})" for s in result["steps"] if s.get("status") == FAILED)
    if reasons:
        return AUDIT_INCOMPLETE, reasons
    if result.get("issues"):
        return AUDIT_REVIEW, [f"{len(result['issues'])} issue(s) require review"]
    return AUDIT_CLEAN, ["all requested steps completed and no issue was detected"]


# ------------------------------------------------------------------ writers
def write_json(path: Path, obj: Any) -> None:
    atomic_write_text(Path(path), json.dumps(obj, indent=2, sort_keys=False, default=str) + "\n")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], columns: list[str]) -> None:
    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow({c: "" if r.get(c) is None else r.get(c) for c in columns})
    atomic_write_text(Path(path), sio.getvalue())


# ---------------------------------------------------------------- markdown
def _md_table(rows: list[dict[str, Any]], cols: list[str], headers: list[str] | None = None) -> str:
    if not rows:
        return "_none_\n"
    headers = headers or cols

    def cell(v: Any) -> str:
        s = "" if v is None else str(v)
        return s.replace("|", "\\|").replace("\n", " ")

    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(cell(r.get(c)) for c in cols) + " |" for r in rows]
    return "\n".join(out) + "\n"


def _fmt_size(n: Any) -> str:
    if not isinstance(n, (int, float)):
        return "?"
    return f"{n / 1e6:.1f} MB" if n >= 1e5 else f"{n} B"


def render_dataset_markdown(r: dict[str, Any]) -> str:
    ds = r["dataset"]
    md = [f"# Dataset audit: {ds['accession']}\n"]
    md.append(f"**Overall audit status: `{r['audit_status']}`** — " + "; ".join(r["audit_status_reasons"]) + "\n")
    md.append("> Evidence labels: **VERIFIED** (directly established from retrieved records/files), **REPORTED** "
              "(stated elsewhere, not reproduced), **UNRESOLVED** (insufficient evidence), **FAILED** (attempted, failed). "
              "There is no PASS status; Phase 1 performs no differential expression, feature selection, enrichment or modelling.\n")

    md.append("## 1. Accession and provisional role\n")
    md.append(f"- Accession: [{ds['accession']}]({ds['landing_page']})\n- Provisional role: `{ds['role']}` — {ds['role_description']}\n"
              f"- Analysis tier: `{ds['analysis_tier']}`\n- Related accessions (config): {', '.join(ds['related_accessions']) or 'none'}\n"
              f"- Participant independence: **{ds['independence_status']}** — {ds['independence_note']}\n")
    meta = r.get("metadata", {})
    if meta.get("series"):
        s = meta["series"]
        md.append(f"- GEO title: {s.get('title')}\n- GEO series type: {', '.join(s.get('type', []))}\n"
                  f"- GEO relations: {'; '.join(s.get('relations', [])) or 'none'}\n- GEO last update: {s.get('last_update_date')}\n")

    md.append("## 2. Retrieval status\n")
    md.append(_md_table(r.get("metadata_retrieval", []), ["name", "status", "local_size", "sha256", "finished_at"],
                        ["metadata resource", "status", "bytes", "sha256", "retrieved (UTC)"]))
    md.append("\n" + _md_table([
        {"name": f["name"], "requested": f["requested"], "status": f["retrieval"].get("status"),
         "size": _fmt_size(f["retrieval"].get("local_size") or f["retrieval"].get("remote_size")),
         "sha256": (f["retrieval"].get("sha256") or "")[:16] + ("…" if f["retrieval"].get("sha256") else ""),
         "note": "; ".join(f["retrieval"].get("notes", []) + ([f["retrieval"]["error"]] if f["retrieval"].get("error") else []))}
        for f in r.get("files", [])], ["name", "requested", "status", "size", "sha256", "note"],
        ["file", "requested", "status", "size", "sha256 (prefix)", "notes"]))
    if r.get("network_used") is not None:
        md.append(f"\nNetwork used in this run: **{r['network_used']}** (offline mode: {r['run']['offline']}).\n")

    md.append("## 3. Available files (GEO listing)\n")
    listing = r.get("geo_file_listing")
    if listing is None:
        md.append("_GEO directory listing not retrieved in this run (offline or failed)._\n")
    else:
        md.append(_md_table(listing, ["location", "name", "size_label", "modified", "configured"],
                            ["location", "file", "listed size", "listed date", "in config"]))

    md.append("## 4. Observed sample counts\n")
    for f_ in r.get("findings", []):
        if f_["topic"] == "sample_count":
            md.append(f"- **{f_['status']}** — {f_['statement']}\n")
    md.append("\n" + _md_table(r.get("group_count_comparison", []), ["group", "reported", "observed", "difference", "status"]))
    md.append(f"\nReference counts source: {ds['expected_source']} (REPORTED; used for comparison only, never enforced).\n")

    md.append("## 5. Observed diagnostic groups\n")
    ph = r.get("phenotype", {})
    md.append(f"Diagnosis field: `{ph.get('diagnosis_field')}`\n\n")
    md.append(_md_table([{"label": k, "n": v} for k, v in (ph.get("raw_label_counts") or {}).items()], ["label", "n"],
                        ["raw GEO label", "n"]))
    md.append("\nCanonical mapping (from config label_map; unmapped labels are flagged, not guessed):\n\n")
    md.append(_md_table([{"group": k, "n": v} for k, v in (ph.get("canonical_counts") or {}).items()], ["group", "n"]))
    if ph.get("fields_of_interest"):
        md.append("\nPotential covariates (non-missing records out of total):\n\n")
        md.append(_md_table(ph["fields_of_interest"], ["field", "n_present", "n_missing", "n_distinct"]))
    if ph.get("participant_ids"):
        p = ph["participant_ids"]
        md.append(f"\nParticipant-ID field `{p['field']}`: {p['n_present']} present, {p['n_distinct']} distinct, "
                  f"{p['n_duplicated_ids']} duplicated ID(s) covering {p['n_records_with_duplicated_ids']} records.\n")

    md.append("## 6. Sample reconciliation\n")
    rec = r.get("reconciliation", [])
    if not rec:
        md.append("_No expression file with sample columns was available for reconciliation._\n")
    for x in rec:
        s = x["summary"]
        md.append(f"### {x['file']} (key: {s['key_description']})\n")
        md.append(f"- {s['left_label']} IDs: {s['n_left_ids']}; {s['right_label']} records: {s['n_right_records']}; exact matches: {s['n_matched']}\n"
                  f"- {s['left_label']}-only: {len(s['left_only'])}; {s['right_label']}-only: {len(s['right_only'])}; "
                  f"records without extractable key: {len(s['right_records_without_key'])}\n"
                  f"- duplicate {s['left_label']} IDs: {len(s['duplicate_left_ids'])}; duplicate {s['right_label']} IDs: {len(s['duplicate_right_ids'])}\n"
                  f"- IDs altered by conservative normalisation (whitespace/Unicode only): {len(s['normalization_changes'])}\n"
                  f"- near-miss hints (NOT used for matching): {len(s['near_miss_hints'])}\n"
                  f"- exact one-to-one correspondence: **{s['exact_one_to_one']}**\n"
                  f"- group counts among matched records: {s['group_counts_matched']}\n"
                  f"- full ID listing: `{x['outputs']['csv']}`\n")
        if s["left_only"]:
            md.append(f"- {s['left_label']}-only IDs (first 20): {s['left_only'][:20]}\n")
        if s["right_only"]:
            md.append(f"- {s['right_label']}-only IDs (first 20): {s['right_only'][:20]}\n")
        if x.get("label_concordance"):
            md.append(f"- label concordance with GEO records: {x['label_concordance']}\n")
    if r.get("concordance"):
        md.append("\n### Cross-file value concordance (read-only)\n")
        md.append(_md_table(r["concordance"], ["file_a", "file_b", "status", "n_shared_features", "n_shared_samples",
                                               "fraction_identical", "max_abs_difference", "pearson_r"]))
    md.append("\nReported leads:\n\n")
    md.append(_md_table([{"lead": l["lead_id"], "status": l["evidence_status"], "description": l["description"],
                          "check": l.get("check") or json.dumps(l["checked_ids"])} for l in r.get("reported_leads", [])],
                        ["lead", "status", "description", "check"]))
    md.append(f"\nProposed exclusion candidates (NOT applied): {r.get('n_proposed_exclusions', 0)} — see "
              f"`{r.get('outputs', {}).get('proposed_exclusions')}`\n")

    md.append("## 7. Processing-state assessment\n")
    md.append(_md_table([{"file": f["name"], "state": f["processing"]["state"], "confidence": f["processing"]["confidence"],
                          "review": f["processing"]["requires_review"], "filename_hint": f["processing"]["filename_hint"],
                          "basis": "; ".join(e["observation"] for e in f["processing"]["evidence"] if e["supports"])
                          or "; ".join(f["processing"]["notes"])}
                         for f in r.get("files", []) if f.get("processing")],
                        ["file", "state", "confidence", "review", "filename_hint", "basis"]))
    md.append("\nPhase 1 does not normalise or transform any data.\n")

    md.append("## 8. Platform and modality\n")
    md.append(f"- Configured modality: `{ds['modality']}` ({ds['technology']})\n- Configured platform: {ds['platform_id']} — {ds['platform_name']}\n")
    for p in meta.get("platforms", []):
        md.append(f"- Observed platform: **{p.get('accession')}** — {p.get('title')} (technology: {p.get('technology')}; "
                  f"distribution: {p.get('distribution')})\n")
    for f_ in r.get("findings", []):
        if f_["topic"] in ("platform", "modality"):
            md.append(f"- **{f_['status']}** — {f_['statement']}\n")

    md.append("## 9. Issues and limitations\n")
    md.append(_md_table(r.get("issues", []), ["severity", "category", "description"]))
    md.append("\n### All findings\n")
    md.append(_md_table(r.get("findings", []), ["status", "topic", "statement", "evidence"]))

    md.append("## 10. Recommended next actions\n")
    md.append("\n".join(f"{i}. {a}" for i, a in enumerate(r.get("next_actions", []), 1)) + "\n")

    md.append("## 11. Run information\n")
    run = r["run"]
    md.append(f"- Run ID: `{run['run_id']}`\n- Audit started/finished (UTC): {r['started_at']} / {r['finished_at']}\n"
              f"- Software: biomarker_project {run['versions'].get('biomarker_project')}, Python {run['versions'].get('python')}, "
              f"pandas {run['versions'].get('pandas')}, numpy {run['versions'].get('numpy')}, requests {run['versions'].get('requests')}, "
              f"PyYAML {run['versions'].get('yaml')}\n- Config SHA-256: `{run['config_sha256']}`\n- Command: `{' '.join(run['argv'])}`\n")
    return "".join(s if s.endswith("\n") else s + "\n" for s in md)


def render_summary_markdown(summary: dict[str, Any]) -> str:
    md = ["# BIO-MB-001 Phase 1 — dataset audit summary\n"]
    md.append(f"Generated (UTC): {summary['generated_at']} from per-dataset reports on disk. "
              f"Latest run: `{summary['latest_run_id']}`.\n")
    md.append("> No dataset is labelled PASS. Every dataset still requires the scientific decisions listed below before "
              "any confirmatory analysis. Phase 1 performed no differential expression, feature selection, enrichment or modelling.\n")
    md.append("## Status by dataset\n")
    md.append(_md_table(summary["datasets"], ["accession", "role", "audit_status", "n_samples_geo", "groups",
                                              "files_available", "files_not_available", "audited_at"],
                        ["accession", "provisional role", "audit status", "GEO samples", "observed groups (canonical)",
                         "requested files available", "requested files NOT available", "audited (UTC)"]))
    md.append("## What is ready\n")
    md.append("\n".join(f"- {x}" for x in summary["ready"]) or "_nothing_")
    md.append("\n## What failed or was not retrieved\n")
    md.append("\n".join(f"- {x}" for x in summary["failed"]) or "_nothing_")
    md.append("\n## Requires human or scientific review\n")
    md.append("\n".join(f"- {x}" for x in summary["review"]) or "_nothing_")
    md.append("\n## Cross-dataset identifier checks (possible participant overlap)\n")
    md.append(_md_table(summary.get("overlap_checks", []), ["id", "datasets", "field", "status", "detail"]))
    md.append("\n## Processing-state overview\n")
    md.append(_md_table(summary.get("processing", []), ["accession", "file", "state", "confidence", "requires_review"]))
    return "".join(s if s.endswith("\n") else s + "\n" for s in md)
