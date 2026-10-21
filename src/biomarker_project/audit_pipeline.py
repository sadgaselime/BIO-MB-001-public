"""Orchestrates the Phase 1 audit of one accession, and of all configured accessions.

Each step is isolated: a failure is recorded (status FAILED, with the error) and the
audit continues with whatever evidence is still obtainable. Network-dependent steps
are labelled as such in the step log.
"""
from __future__ import annotations

import json
import logging
import os
import platform
import sys
import traceback
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from . import __version__
from .config import DatasetConfig, ProjectConfig
from .download import (
    SKIPPED_NOT_REQUESTED, Manifest, RetrievalRecord, download_file, retrieve_text, utcnow,
)
from .file_inspection import PRIMARY_MEASURES, InspectionResult, inspect_file
from .geo_client import GeoClient, parse_soft_brief
from .processing_audit import UNKNOWN, classify_file, compare_matrices
from .reporting import (
    FAILED, REPORTED, UNRESOLVED, VERIFIED, determine_audit_status, finding, render_dataset_markdown,
    render_summary_markdown, write_csv, write_json,
)
from .sample_reconciliation import (
    AMBIGUOUS, MISSING, MULTIPLE, UNMAPPED, apply_id_regex, build_phenotype_table, check_reported_leads,
    compare_group_counts, compare_identifier_sets, extract_field, normalize_sample_id, propose_exclusion_candidates,
    reconcile, write_reconciliation,
)

log = logging.getLogger(__name__)


# ------------------------------------------------------------------ context
@dataclass
class ProjectPaths:
    root: Path

    def raw(self, acc: str) -> Path:
        return self.root / "data" / "raw" / acc

    def metadata(self, acc: str) -> Path:
        return self.root / "data" / "metadata" / acc

    def processed(self, acc: str) -> Path:
        return self.root / "data" / "processed" / acc

    def report(self, acc: str) -> Path:
        return self.root / "reports" / "dataset_audit" / acc

    @property
    def audit_root(self) -> Path:
        return self.root / "reports" / "dataset_audit"

    @property
    def logs(self) -> Path:
        return self.root / "reports" / "logs"

    def rel(self, p: str | Path | None) -> str | None:
        if p is None:
            return None
        try:
            return str(Path(p).resolve().relative_to(self.root.resolve()))
        except ValueError:
            return str(p)


@dataclass
class AuditOptions:
    offline: bool = False
    skip_downloads: bool = False       # metadata-only run
    refresh_metadata: bool = False
    max_download_mb: float | None = None


@dataclass
class RunContext:
    run_id: str
    argv: list[str]
    config: ProjectConfig
    options: AuditOptions
    started_at: str = field(default_factory=utcnow)
    project_root: Path | None = None

    def _rel(self, p: str | Path) -> str:
        """Project-relative path for reports (avoids recording local home-directory paths)."""
        if self.project_root is not None:
            try:
                return str(Path(p).resolve().relative_to(self.project_root.resolve()))
            except ValueError:
                pass
        return str(p)

    def _cwd(self) -> str:
        if self.project_root is None:
            return os.getcwd()
        rel = self._rel(os.getcwd())
        return rel if not Path(rel).is_absolute() else "(outside project root)"

    def describe(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "argv": self.argv,
            "cwd": self._cwd(),
            "started_at": self.started_at,
            "offline": self.options.offline,
            "options": self.options.__dict__,
            "config_path": self._rel(self.config.path),
            "config_sha256": self.config.sha256,
            "versions": software_versions(),
            "platform": platform.platform(),
        }


def new_run_id() -> str:
    return f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:6]}"


def software_versions() -> dict[str, str]:
    import numpy
    import requests
    import yaml

    return {"biomarker_project": __version__, "python": sys.version.split()[0], "pandas": pd.__version__,
            "numpy": numpy.__version__, "requests": requests.__version__, "yaml": yaml.__version__}


def setup_logging(paths: ProjectPaths, run_id: str, verbose: bool = False) -> Path:
    paths.logs.mkdir(parents=True, exist_ok=True)
    log_path = paths.logs / f"audit_{run_id}.log"
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for h in list(root.handlers):
        if getattr(h, "_bio_mb", False):
            root.removeHandler(h)
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.DEBUG if verbose else logging.INFO)
    sh.setFormatter(fmt)
    for h in (fh, sh):
        h._bio_mb = True  # type: ignore[attr-defined]
        root.addHandler(h)
    for noisy in ("urllib3", "charset_normalizer"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return log_path


# --------------------------------------------------------------- helpers
class _Steps:
    def __init__(self):
        self.items: list[dict[str, Any]] = []

    def run(self, name: str, fn: Callable[[], Any], network: bool = False) -> Any:
        entry = {"step": name, "network_dependent": network, "started_at": utcnow()}
        try:
            out = fn()
            entry["status"] = "OK"
            return out
        except Exception as exc:  # recorded, never raised: other steps continue
            entry["status"] = FAILED
            entry["error"] = f"{type(exc).__name__}: {exc}"
            log.error("Step %s failed: %s", name, exc)
            log.debug("%s", traceback.format_exc())
            return None
        finally:
            entry["finished_at"] = utcnow()
            self.items.append(entry)


def _series_summary(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec["fields"]
    one = lambda k: (f.get(k) or [None])[0]  # noqa: E731
    return {
        "accession": rec["accession"],
        "title": one("Series_title"),
        "status": one("Series_status"),
        "submission_date": one("Series_submission_date"),
        "last_update_date": one("Series_last_update_date"),
        "type": f.get("Series_type", []),
        "platform_ids": f.get("Series_platform_id", []),
        "sample_ids": f.get("Series_sample_id", []),
        "relations": f.get("Series_relation", []),
        "pubmed_ids": f.get("Series_pubmed_id", []),
        "supplementary_files": f.get("Series_supplementary_file", []),
        "summary": " ".join(f.get("Series_summary", [])),
        "overall_design": " ".join(f.get("Series_overall_design", [])),
    }


def _platform_summary(rec: dict[str, Any]) -> dict[str, Any]:
    f = rec["fields"]
    one = lambda k: (f.get(k) or [None])[0]  # noqa: E731
    return {"accession": rec["accession"], "title": one("Platform_title"), "technology": one("Platform_technology"),
            "distribution": one("Platform_distribution"), "organism": one("Platform_organism"),
            "manufacturer": one("Platform_manufacturer")}


def _match_keys(sample_records: list[dict[str, Any]], spec_field: str, regex: str | None) -> dict[str, str | None]:
    out = {}
    for rec in sample_records:
        if rec.get("entity") != "SAMPLE":
            continue
        vals = extract_field(rec, spec_field)
        val = vals[0] if len(vals) == 1 else (" | ".join(vals) if vals else None)
        out[rec["accession"]] = apply_id_regex(val, regex)
    return out


def _field_coverage(ph: pd.DataFrame, fields: tuple[str, ...]) -> list[dict[str, Any]]:
    rows = []
    for f_ in fields:
        col = f_ if f_ in ph.columns else None
        if col is None:
            rows.append({"field": f_, "n_present": 0, "n_missing": len(ph), "n_distinct": 0})
            continue
        s = ph[col]
        present = s.notna() & (s.astype(str).str.strip() != "")
        rows.append({"field": f_, "n_present": int(present.sum()), "n_missing": int((~present).sum()),
                     "n_distinct": int(s[present].nunique())})
    return rows


# --------------------------------------------------------------- dataset audit
def audit_dataset(ds: DatasetConfig, ctx: RunContext, paths: ProjectPaths, client: GeoClient) -> dict[str, Any]:
    cfg, opts = ctx.config, ctx.options
    acc = ds.accession
    log.info("==== Auditing %s (%s) ====", acc, ds.role)
    steps = _Steps()
    findings: list[dict[str, str]] = []
    issues: list[dict[str, str]] = []
    next_actions: list[str] = []
    started = utcnow()
    meta_dir, raw_dir, rep_dir, proc_dir = paths.metadata(acc), paths.raw(acc), paths.report(acc), paths.processed(acc)
    for d in (meta_dir, raw_dir, rep_dir, proc_dir):
        d.mkdir(parents=True, exist_ok=True)
    n_requests_before = len(client.request_log)

    def issue(severity: str, category: str, description: str) -> None:
        issues.append({"severity": severity, "category": category, "description": description})

    result: dict[str, Any] = {
        "report_schema_version": 1,
        "dataset": {
            "accession": acc, "role": ds.role, "role_description": ds.role_description,
            "analysis_tier": ds.analysis_tier, "modality": ds.modality, "technology": ds.technology,
            "platform_id": ds.platform_id, "platform_name": ds.platform_name, "landing_page": ds.landing_page,
            "related_accessions": list(ds.related_accessions), "independence_status": ds.independence_status,
            "independence_note": ds.independence_note, "expected_source": ds.expected.source,
            "expected_total": ds.expected.total, "expected_groups": ds.expected.groups,
        },
        "run": ctx.describe(),
        "started_at": started,
    }

    # ---- 1. GEO metadata (network-dependent unless cached snapshots exist)
    meta_manifest = Manifest(meta_dir / "retrieval_manifest.json")
    meta_records: list[RetrievalRecord] = []

    def get_meta(name: str, url: str) -> RetrievalRecord:
        rec = retrieve_text(client, url, meta_dir / name, meta_manifest, refresh=opts.refresh_metadata)
        meta_records.append(rec)
        return rec

    series_rec = steps.run("retrieve_series_metadata",
                           lambda: get_meta(f"{acc}_series_brief.soft.txt", client.query_url(acc, "self")), network=True)
    samples_rec = steps.run("retrieve_sample_metadata",
                            lambda: get_meta(f"{acc}_samples_brief.soft.txt", client.query_url(acc, "gsm")), network=True)

    series: dict[str, Any] | None = None
    sample_records: list[dict[str, Any]] = []
    if series_rec is not None and series_rec.available:
        def _parse_series():
            recs = parse_soft_brief(Path(series_rec.path).read_text(encoding="utf-8", errors="replace"))
            sr = [r for r in recs if r["entity"] == "SERIES"]
            if not sr or sr[0]["accession"] != acc:
                raise ValueError(f"series snapshot does not describe {acc}")
            return _series_summary(sr[0])
        series = steps.run("parse_series_metadata", _parse_series)
    if samples_rec is not None and samples_rec.available:
        sample_records = steps.run(
            "parse_sample_metadata",
            lambda: [r for r in parse_soft_brief(Path(samples_rec.path).read_text(encoding="utf-8", errors="replace"))
                     if r["entity"] == "SAMPLE"]) or []

    platforms = []
    for gpl in (series or {}).get("platform_ids", []):
        prec = steps.run(f"retrieve_platform_{gpl}",
                         lambda g=gpl: get_meta(f"{g}_platform_brief.soft.txt", client.query_url(g, "self")), network=True)
        if prec is not None and prec.available:
            p = steps.run(f"parse_platform_{gpl}", lambda pr=prec: _platform_summary(
                [r for r in parse_soft_brief(Path(pr.path).read_text(encoding="utf-8", errors="replace")) if r["entity"] == "PLATFORM"][0]))
            if p:
                platforms.append(p)

    result["metadata_retrieval"] = [dict(m.to_dict(), path=paths.rel(m.path)) for m in meta_records]
    for m in meta_records:
        if not m.available:
            findings.append(finding("retrieval", FAILED, f"metadata resource {m.name}: {m.status}", m.error or ""))
    result["metadata"] = {"series": series, "platforms": platforms, "n_sample_records": len(sample_records),
                          "sample_records_available": bool(sample_records)}

    # ---- 2. sample-list completeness and platform/modality checks
    if series:
        listed = series["sample_ids"]
        got = [r["accession"] for r in sample_records]
        if sample_records:
            if set(listed) == set(got) and len(got) == len(set(got)):
                findings.append(finding("sample_count", VERIFIED,
                                        f"GEO series lists {len(listed)} samples and all {len(got)} sample records were retrieved",
                                        "series record !Series_sample_id vs retrieved GSM records"))
            else:
                missing, extra = sorted(set(listed) - set(got)), sorted(set(got) - set(listed))
                findings.append(finding("sample_count", FAILED,
                                        f"sample records incomplete: {len(missing)} listed but not retrieved, {len(extra)} unexpected",
                                        f"missing (first 10): {missing[:10]}; extra: {extra[:10]}"))
                issue("high", "retrieval", f"GSM records retrieved ({len(got)}) do not match series sample list ({len(listed)})")
        obs_platforms = series["platform_ids"]
        if ds.platform_id:
            st = VERIFIED if obs_platforms == [ds.platform_id] else FAILED
            findings.append(finding("platform", st,
                                    f"configured platform {ds.platform_id}; GEO series platform(s): {obs_platforms}",
                                    "GEO series record"))
            if st == FAILED:
                issue("high", "platform", f"platform mismatch: config {ds.platform_id} vs GEO {obs_platforms}")
        else:
            findings.append(finding("platform", VERIFIED, f"platform not specified in config; GEO reports {obs_platforms}",
                                    "GEO series record"))
        for p in platforms:
            findings.append(finding("platform", VERIFIED, f"{p['accession']}: {p['title']} ({p['technology']})", "GEO platform record"))
        findings.append(finding("modality", VERIFIED, f"GEO series type: {series['type']}; configured modality: {ds.modality}",
                                "GEO series record"))
        for rel in series["relations"]:
            if rel.startswith("SubSeries of") or rel.startswith("SuperSeries of"):
                findings.append(finding("relations", VERIFIED, f"GEO relation: {rel}", "GEO series record"))
        sample_platforms = Counter(p for r in sample_records for p in r["fields"].get("Sample_platform_id", []))
        if len(sample_platforms) > 1:
            issue("high", "platform", f"samples span several platforms: {dict(sample_platforms)}")

    findings.append(finding("independence", UNRESOLVED if ds.independence_status == "UNRESOLVED" else REPORTED,
                            f"participant independence status: {ds.independence_status}. {ds.independence_note}",
                            "configuration (not established from data)"))
    if ds.independence_status == "UNRESOLVED":
        next_actions.append("Verify participant-level independence/overlap with related cohorts from study documentation or "
                            "the data owners; a different GEO accession does not establish independence.")

    # ---- 3. phenotype table
    phenotype = pd.DataFrame()
    if sample_records:
        phenotype = steps.run("build_phenotype_table", lambda: build_phenotype_table(sample_records, ds.phenotype))
        if phenotype is None:
            phenotype = pd.DataFrame()
    ph_info: dict[str, Any] = {"diagnosis_field": ds.phenotype.diagnosis_field}
    if not phenotype.empty:
        def _write_ph():
            from .download import atomic_write_text
            atomic_write_text(proc_dir / "phenotype_table.tsv", phenotype.to_csv(sep="\t", index=False))
        steps.run("write_phenotype_table", _write_ph)
        ph_info["table_path"] = paths.rel(proc_dir / "phenotype_table.tsv")
        ph_info["raw_label_counts"] = dict(sorted(Counter(phenotype["diagnosis_raw"].fillna("<MISSING>")).items()))
        canon = phenotype.apply(lambda r: r["diagnosis_canonical"] if r["diagnosis_status"] in ("MAPPED", AMBIGUOUS)
                                else f"<{r['diagnosis_status']}>", axis=1)
        ph_info["canonical_counts"] = dict(sorted(Counter(canon).items()))
        ph_info["status_counts"] = dict(Counter(phenotype["diagnosis_status"]))
        ph_info["fields_of_interest"] = _field_coverage(phenotype, ds.phenotype.fields_of_interest)
        for st, sev, msg in ((MISSING, "high", "missing diagnosis label"), (UNMAPPED, "high", "unexpected (unmapped) diagnosis label"),
                             (MULTIPLE, "high", "conflicting diagnosis values"), (AMBIGUOUS, "medium", "ambiguous diagnosis label")):
            sub = phenotype[phenotype["diagnosis_status"] == st]
            if len(sub):
                labels = dict(Counter(sub["diagnosis_raw"].fillna("<MISSING>")))
                issue(sev, "phenotype", f"{len(sub)} sample(s) with {msg}: {labels}")
                findings.append(finding("diagnosis_labels", VERIFIED, f"{len(sub)} sample(s) with {msg}: {labels}",
                                        f"GEO characteristics field {ds.phenotype.diagnosis_field}"))
        if not ph_info["status_counts"].get(MISSING) and not ph_info["status_counts"].get(UNMAPPED):
            findings.append(finding("diagnosis_labels", VERIFIED,
                                    f"every sample has a diagnosis label in {ds.phenotype.diagnosis_field} that is mapped or explicitly flagged",
                                    "GEO sample characteristics"))
        if ph_info["status_counts"].get(AMBIGUOUS):
            next_actions.append("Decide (in a prespecified analysis plan) how ambiguous/transition diagnosis labels are handled; "
                                "they are kept separate and nothing has been excluded.")
        if ds.phenotype.participant_id_field:
            pid = phenotype["participant_id"]
            present = pid.dropna()
            dup = present[present.duplicated(keep=False)]
            ph_info["participant_ids"] = {"field": ds.phenotype.participant_id_field, "n_present": int(len(present)),
                                          "n_distinct": int(present.nunique()), "n_duplicated_ids": int(dup.nunique()),
                                          "n_records_with_duplicated_ids": int(len(dup))}
            if len(present) < len(phenotype):
                issue("medium", "phenotype", f"{len(phenotype) - len(present)} sample(s) lack a participant ID in "
                                             f"{ds.phenotype.participant_id_field}")
            if len(dup):
                issue("high", "phenotype",
                      f"{dup.nunique()} participant ID(s) occur in more than one sample ({len(dup)} samples): possible repeated "
                      f"measures / technical replicates; must be handled to prevent leakage")
                findings.append(finding("participants", VERIFIED,
                                        f"{dup.nunique()} participant IDs shared by {len(dup)} samples "
                                        f"(examples: {sorted(dup.unique())[:5]})", ds.phenotype.participant_id_field))
                next_actions.append("Review samples sharing a participant ID (repeated measures/replicates) and define a "
                                    "one-sample-per-participant rule or grouped splitting before any modelling.")
        # group-count comparison (all records)
        groups = Counter(phenotype.loc[phenotype["diagnosis_status"] == "MAPPED", "diagnosis_canonical"])
        if (phenotype["diagnosis_status"] == AMBIGUOUS).any():
            groups["AMBIGUOUS"] = int((phenotype["diagnosis_status"] == AMBIGUOUS).sum())
        cmp_rows = compare_group_counts(dict(groups), ds.expected, len(phenotype))
        result["group_count_comparison"] = cmp_rows
        for row in cmp_rows:
            if row["status"] == "DIFFERS_FROM_REPORTED":
                issue("medium", "counts", f"{row['group']}: observed {row['observed']} vs reported {row['reported']} "
                                          f"(difference {row['difference']:+d})")
        differs = [r_ for r_ in cmp_rows if r_["status"] == "DIFFERS_FROM_REPORTED"]
        findings.append(finding("sample_count", VERIFIED,
                                f"observed {len(phenotype)} GEO sample records; group counts "
                                f"{'match' if not differs else 'differ from'} the reference values "
                                f"({', '.join(r_['group'] for r_ in differs) or 'all compared groups match'})",
                                "GEO sample records vs config expected_counts"))
        if differs:
            next_actions.append("Investigate the differences between observed and reported counts (see group-count table); "
                                "no samples were removed or added to match reference values.")
    result["phenotype"] = ph_info

    # ---- 4. GEO directory listing (network)
    listing = None
    if not client.offline:
        def _listing():
            rows = []
            configured = {(f.location, f.name) for f in ds.files}
            for loc in ("matrix", "suppl"):
                try:
                    entries = client.list_directory(acc, loc)
                except Exception as exc:  # a missing 'suppl' directory is legitimate
                    log.warning("Could not list %s/%s: %s", acc, loc, exc)
                    rows.append({"location": loc, "name": f"<listing failed: {exc}>", "size_label": "", "modified": "",
                                 "configured": ""})
                    continue
                for e in entries:
                    rows.append({"location": loc, "name": e.name, "size_label": e.size_label, "modified": e.modified,
                                 "configured": (loc, e.name) in configured})
            write_json(meta_dir / "geo_file_listing.json", {"retrieved_at": utcnow(), "entries": rows})
            return rows
        listing = steps.run("list_geo_files", _listing, network=True)
        if listing is not None:
            names = {(r["location"], r["name"]) for r in listing}
            for f in ds.files:
                if (f.location, f.name) not in names:
                    issue("medium", "files", f"configured file {f.location}/{f.name} is not in the current GEO listing")
            unlisted = [r["name"] for r in listing if r["configured"] is False]
            if unlisted:
                findings.append(finding("files", VERIFIED, f"GEO lists files not configured for retrieval: {unlisted}",
                                        "GEO HTTPS directory listing"))
    result["geo_file_listing"] = listing

    # ---- 5. downloads
    manifest = Manifest(raw_dir / "download_manifest.json")
    max_bytes = int((opts.max_download_mb or cfg.settings.max_download_mb) * 1e6)
    offline_client = GeoClient(cfg.settings, offline=True)
    files_out = []
    records: dict[str, RetrievalRecord] = {}
    for f in ds.files:
        url = client.file_url(acc, f.location, f.name)
        dest = raw_dir / f.name
        requested = f.retrieve and not opts.skip_downloads
        if not f.retrieve or (opts.skip_downloads and not dest.exists()):
            rec = RetrievalRecord(name=f.name, url=url, path=str(dest), status=SKIPPED_NOT_REQUESTED, finished_at=utcnow())
            rec.notes.append("not requested in configuration (retrieve: false)" if not f.retrieve
                             else "metadata-only run (--skip-downloads)")
        else:
            use = offline_client if opts.skip_downloads else client
            rec = steps.run(f"retrieve_{f.name}", lambda u=url, d=dest, c=use: download_file(c, u, d, max_bytes, manifest),
                            network=not opts.skip_downloads and not client.offline)
            if rec is None:
                rec = RetrievalRecord(name=f.name, url=url, path=str(dest), status="FAILED", error="unexpected error; see log")
        records[f.name] = rec
        files_out.append({"name": f.name, "location": f.location, "url": url, "requested": requested,
                          "sample_id_field": f.sample_id_field, "sample_id_regex": f.sample_id_regex,
                          "retrieval": dict(rec.to_dict(), path=paths.rel(rec.path))})
        if requested and not rec.available:
            sev = "medium" if rec.status.startswith("SKIPPED") else "high"
            issue(sev, "retrieval", f"{f.name}: {rec.status}" + (f" — {rec.error}" if rec.error else ""))
            findings.append(finding("retrieval", FAILED if not rec.status.startswith("SKIPPED") else UNRESOLVED,
                                    f"{f.name} not available locally ({rec.status})", "; ".join(rec.notes) or (rec.error or "")))
            if rec.status == "SKIPPED_TOO_LARGE":
                next_actions.append(f"Decide whether {f.name} ({(rec.remote_size or 0) / 1e6:.0f} MB) is needed; if so: "
                                    + (rec.notes[0] if rec.notes else "raise --max-download-mb"))
        elif rec.available:
            findings.append(finding("retrieval", VERIFIED,
                                    f"{f.name}: {rec.status}, {rec.local_size} bytes, SHA-256 {rec.sha256}",
                                    f"{url}; integrity: {(rec.integrity or {}).get('method')}"))

    # ---- 6-7. inspection and processing state
    inspections: dict[str, InspectionResult] = {}
    gsm_processing = sorted({t for r in sample_records for t in r["fields"].get("Sample_data_processing", [])})
    (rep_dir / "files").mkdir(exist_ok=True)
    for fo in files_out:
        rec = records[fo["name"]]
        if not rec.available:
            continue
        insp = steps.run(f"inspect_{fo['name']}", lambda p=rec.path: inspect_file(p, cfg.settings.inspection_sample_rows))
        if insp is None:
            continue
        inspections[fo["name"]] = insp
        d = insp.to_dict()
        d["path"] = paths.rel(d["path"])
        write_json(rep_dir / "files" / f"{fo['name']}.inspection.json", d)
        fo["inspection"] = {k: d[k] for k in ("status", "format", "compression", "table_kind", "n_rows", "n_columns",
                                              "feature_id_column", "measurement_types", "duplicate_column_headers",
                                              "duplicate_sample_ids", "n_unique_feature_ids", "duplicate_feature_ids",
                                              "missing_feature_ids", "missing_values", "value_summary", "limitations",
                                              "empty_header_sample_columns",
                                              "error", "annotation_columns")}
        fo["inspection"]["n_candidate_sample_ids"] = len(insp.candidate_sample_ids)
        fo["inspection"]["report"] = paths.rel(rep_dir / "files" / f"{fo['name']}.inspection.json")
        if not insp.usable:
            issue("high", "inspection", f"{fo['name']}: {insp.status} — {insp.error}")
            findings.append(finding("inspection", FAILED, f"{fo['name']} could not be inspected: {insp.status}", insp.error or ""))
        else:
            findings.append(finding("inspection", VERIFIED,
                                    f"{fo['name']}: {insp.format} ({insp.compression}), kind={insp.table_kind}, rows={insp.n_rows}, "
                                    f"columns={insp.n_columns}, candidate samples={len(insp.candidate_sample_ids)}",
                                    "streamed file inspection"))
            dfi = insp.duplicate_feature_ids or {}
            if dfi.get("n_duplicated_ids"):
                issue("low", "inspection", f"{fo['name']}: {dfi['n_duplicated_ids']} duplicated feature IDs "
                                           f"({dfi['n_rows_involved']} rows)")
            short = insp.metadata.get("n_rows_with_too_few_fields")
            if short:
                rows_ = insp.metadata.get("rows_with_too_few_fields", [])
                issue("high", "inspection", f"{fo['name']}: {short} row(s) shorter than the header (values absent, "
                                            f"counted as missing): " + ", ".join(f"line {r['line']} {r['first_field']!r} "
                                                                                 f"({r['n_fields']} fields)" for r in rows_[:10]))
                findings.append(finding("inspection", VERIFIED, f"{fo['name']}: {short} truncated row(s) in the deposited "
                                                                f"file: {[r['first_field'] for r in rows_[:10]]}",
                                        "field-count check of every row"))
            if insp.empty_header_sample_columns:
                issue("high", "inspection", f"{fo['name']}: {len(insp.empty_header_sample_columns)} data column(s) with an empty "
                                            f"header at positions {insp.empty_header_sample_columns}: values present but not "
                                            f"attributable to any sample")
                findings.append(finding("inspection", VERIFIED, f"{fo['name']}: {len(insp.empty_header_sample_columns)} unlabelled "
                                                                f"data column(s) at positions {insp.empty_header_sample_columns}",
                                        "header parsed verbatim"))
            if insp.duplicate_column_headers and [h for h in insp.duplicate_column_headers if h.strip()]:
                issue("high", "inspection", f"{fo['name']}: duplicated column headers "
                                            f"{[h for h in insp.duplicate_column_headers if h.strip()][:10]}")
            mv = insp.missing_values or {}
            if mv.get("total_missing_in_sample_columns"):
                issue("low", "inspection", f"{fo['name']}: {mv['total_missing_in_sample_columns']} missing values in "
                                           f"{mv['n_sample_columns_with_missing']} sample column(s)")
        proc = classify_file(insp, ds.modality, gsm_processing)
        fo["processing"] = proc
        if proc["requires_review"]:
            issue("medium" if proc["state"] != UNKNOWN else "high", "processing",
                  f"{fo['name']}: processing state {proc['state']} (confidence {proc['confidence']}) requires review"
                  + (f"; {'; '.join(proc['notes'])}" if proc["notes"] else ""))
        findings.append(finding("processing", VERIFIED if proc["confidence"] == "HIGH" else UNRESOLVED,
                                f"{fo['name']}: {proc['state']} (confidence {proc['confidence']})",
                                "; ".join(e["observation"] for e in proc["evidence"] if e["supports"]) or "no content evidence"))
    for fo in files_out:
        if fo["name"] not in inspections and fo["requested"]:
            fo["processing"] = {"state": UNKNOWN, "confidence": "LOW", "requires_review": True, "filename_hint": None,
                                "filename_conflict": False, "scores": {}, "notes": ["file not available for inspection"],
                                "evidence": [{"source": "file_structure", "observation": "file not retrieved/inspected",
                                              "supports": None, "weight": "none"}]}

    # ---- 8. sample reconciliation
    recon_out = []
    recon_objs = {}
    expr_id_sets: dict[str, set[str]] = {}
    spec_by_name = {f.name: f for f in ds.files}
    for name, insp in inspections.items():
        fspec = spec_by_name[name]
        if not insp.usable or not insp.candidate_sample_ids or phenotype.empty:
            continue
        if not fspec.sample_id_field:
            if insp.table_kind in ("expression_matrix", "sample_sheet"):
                issue("medium", "reconciliation", f"{name}: has sample identifiers but no sample_id_field is configured; "
                                                  f"not reconciled")
            continue

        def _recon(insp=insp, fspec=fspec, name=name):
            keys = _match_keys(sample_records, fspec.sample_id_field, fspec.sample_id_regex)
            ph = phenotype.copy()
            ph["match_key"] = ph["geo_accession"].map(keys)
            if insp.table_kind == "sample_sheet":
                left_ids = insp.metadata["sample_sheet"]["sample_names"]
                left_label = "sample_sheet"
            else:
                left_ids = [c["sample_id"] for c in insp.sample_columns if c["measure"] in PRIMARY_MEASURES]
                left_label = "expression"
            key_desc = f"{left_label} column/sample ID == GEO {fspec.sample_id_field}" + (
                f" (regex {fspec.sample_id_regex!r})" if fspec.sample_id_regex else "")
            res = reconcile(left_ids, ph, "match_key", left_label=left_label, right_label="phenotype",
                            key_description=key_desc, left_source=name, right_source=f"GEO sample records ({acc})")
            outputs = write_reconciliation(res, rep_dir, Path(name).name.replace(".", "_"))
            entry = {"file": name, "summary": res.summary(),
                     "outputs": {k: paths.rel(v) for k, v in outputs.items()}}
            if insp.table_kind == "sample_sheet":
                recs = insp.metadata["sample_sheet"]["records"]
                gmap = dict(zip(ph["match_key"], ph["diagnosis_raw"]))
                agree = sum(1 for r in recs if "Sample_Group" in r and gmap.get(r["Sample_Name"]) == r["Sample_Group"])
                compared = sum(1 for r in recs if r.get("Sample_Name") in gmap)
                entry["label_concordance"] = {"compared": compared, "identical_group_labels": agree}
            return res, entry
        out = steps.run(f"reconcile_{name}", _recon)
        if out is None:
            continue
        res, entry = out
        recon_objs[name] = res
        recon_out.append(entry)
        expr_id_sets[name] = set(res.matched) | set(res.left_only)
        s = entry["summary"]
        status = VERIFIED
        stmt = (f"{name}: {s['n_left_ids']} {s['left_label']} IDs vs {s['n_right_records']} phenotype records; "
                f"{s['n_matched']} exact matches, {len(s['left_only'])} {s['left_label']}-only, {len(s['right_only'])} "
                f"phenotype-only, {len(s['duplicate_left_ids'])}/{len(s['duplicate_right_ids'])} duplicated IDs")
        findings.append(finding("reconciliation", status, stmt, s["key_description"]))
        if not res.exact_one_to_one:
            issue("high" if (res.left_only or res.duplicate_left_ids) else "medium", "reconciliation",
                  f"{name}: not an exact one-to-one match with GEO records ({len(res.left_only)} {s['left_label']}-only, "
                  f"{len(res.right_only)} phenotype-only, {len(res.duplicate_left_ids)} duplicated {s['left_label']} IDs, "
                  f"{len(res.duplicate_right_ids)} duplicated phenotype keys, {len(res.right_records_without_key)} records "
                  f"without key)")
            next_actions.append(f"Review unmatched/duplicated identifiers for {name} in {entry['outputs']['csv']}.")
        if entry.get("label_concordance") and entry["label_concordance"]["compared"] != entry["label_concordance"]["identical_group_labels"]:
            issue("high", "phenotype", f"{name}: group labels disagree with GEO records for "
                                       f"{entry['label_concordance']['compared'] - entry['label_concordance']['identical_group_labels']} sample(s)")
    result["reconciliation"] = recon_out

    # ---- 9. cross-file value concordance (series matrix vs supplementary matrices)
    concord = []
    sm = [n for n, i in inspections.items() if i.format == "geo_series_matrix" and i.table_kind == "expression_matrix"]
    for smn in sm:
        for name, insp in inspections.items():
            if name == smn or insp.table_kind != "expression_matrix" or not spec_by_name[name].sample_id_field:
                continue
            fspec = spec_by_name[name]

            def _cmp(smn=smn, insp=insp, fspec=fspec):
                keys = _match_keys(sample_records, fspec.sample_id_field, fspec.sample_id_regex)
                smap = {g: k for g, k in keys.items() if k}
                return compare_matrices(inspections[smn], insp, smap, cfg.settings.concordance_max_features)
            c = steps.run(f"concordance_{smn}_vs_{name}", _cmp)
            if c:
                concord.append(c)
                findings.append(finding("processing", VERIFIED if c.get("status") in ("IDENTICAL_VALUES", "DIFFERENT_VALUES",
                                                                                         "HIGHLY_CORRELATED_NOT_IDENTICAL") else UNRESOLVED,
                                        f"series matrix vs {name}: {c.get('status')} "
                                        f"({c.get('n_shared_features', 0)} features x {c.get('n_shared_samples', 0)} samples compared; "
                                        f"fraction identical {c.get('fraction_identical')})",
                                        "read-only value comparison on the first features"))
    result["concordance"] = concord

    # ---- 10. reported leads and modality notes
    leads = check_reported_leads(ds.reported_leads, phenotype if not phenotype.empty else pd.DataFrame(), expr_id_sets)
    result["reported_leads"] = leads
    for l_ in leads:
        findings.append(finding("reported_lead", REPORTED, f"{l_['lead_id']}: {l_['description']}", l_["source"]))
        if l_.get("kind") == "count_discrepancy":
            next_actions.append(f"Lead {l_['lead_id']}: establish from the publication/authors why GEO sample numbers differ "
                                f"from the described participants; do not infer or impute missing samples.")
        elif not l_["checked_ids"]:
            findings.append(finding("reported_lead", UNRESOLVED, f"{l_['lead_id']}: no sample IDs configured to check",
                                    "config reported_leads[].sample_ids is empty"))
            next_actions.append(f"Add the sample IDs referenced by lead {l_['lead_id']} (from the cited publication) to the "
                                f"configuration so they can be checked against GEO records; they will not be auto-excluded.")
    if ds.expected.described_participants is not None and not phenotype.empty:
        design = (series or {}).get("overall_design", "")
        if design:
            findings.append(finding("sample_count", VERIFIED, f"GEO overall design text: {design[:400]!r}",
                                    "GEO series record (quoted, not interpreted)"))
    if ds.modality == "methylation_array":
        findings.append(finding("modality", VERIFIED, "DNA methylation dataset: kept separate; not transcriptomic validation "
                                                      "and never merged with RNA-seq or microarray expression matrices", "configuration + GEO type"))
    if ds.modality == "expression_rnaseq":
        findings.append(finding("modality", VERIFIED, "RNA-seq dataset: values are not on the same scale as microarray "
                                                      "intensities and must never be pooled with them", "configuration + GEO type"))
    if ds.analysis_tier in ("exploratory", "future_extension"):
        next_actions.append(f"Keep {acc} {ds.analysis_tier.replace('_', ' ')} until its open discrepancies are explained.")

    # ---- 11. proposed exclusions (never applied)
    proposals = propose_exclusion_candidates(acc, phenotype, recon_objs) if not phenotype.empty else []
    write_csv(rep_dir / "proposed_exclusions.csv", proposals,
              ["accession", "geo_accession", "sample_id", "reason", "evidence", "source_file", "status"])
    result["n_proposed_exclusions"] = len(proposals)

    # ---- processing-suitability next action
    usable_expr = [fo for fo in files_out if fo.get("inspection", {}).get("table_kind") == "expression_matrix"]
    if usable_expr:
        next_actions.append("Choose the downstream input file for this dataset only after reviewing the processing evidence: "
                            + "; ".join(f"{fo['name']} = {fo['processing']['state']} ({fo['processing']['confidence']})"
                                        for fo in usable_expr)
                            + ". Do not apply normalisation to data that is already normalised.")

    # ---- finalise
    result["files"] = files_out
    result["steps"] = steps.items
    result["findings"] = findings
    sev_rank = {"high": 0, "medium": 1, "low": 2}
    result["issues"] = sorted(issues, key=lambda i: sev_rank.get(i["severity"], 3))
    result["next_actions"] = list(dict.fromkeys(next_actions))
    result["network_used"] = len(client.request_log) > n_requests_before
    result["finished_at"] = utcnow()
    status, reasons = determine_audit_status(result)
    result["audit_status"], result["audit_status_reasons"] = status, reasons
    result["outputs"] = {
        "report_json": paths.rel(rep_dir / "audit_report.json"),
        "report_markdown": paths.rel(rep_dir / "audit_report.md"),
        "proposed_exclusions": paths.rel(rep_dir / "proposed_exclusions.csv"),
        "phenotype_table": ph_info.get("table_path"),
        "download_manifest": paths.rel(raw_dir / "download_manifest.json"),
        "metadata_manifest": paths.rel(meta_dir / "retrieval_manifest.json"),
    }
    write_json(rep_dir / "audit_report.json", result)
    from .download import atomic_write_text
    atomic_write_text(rep_dir / "audit_report.md", render_dataset_markdown(result))
    log.info("%s audit status: %s (%s)", acc, status, "; ".join(reasons))
    return result


def failed_result(ds: DatasetConfig, ctx: RunContext, paths: ProjectPaths, exc: BaseException) -> dict[str, Any]:
    """Minimal, truthful report when the audit of a dataset crashed unexpectedly."""
    rep_dir = paths.report(ds.accession)
    rep_dir.mkdir(parents=True, exist_ok=True)
    now = utcnow()
    result = {
        "report_schema_version": 1,
        "dataset": {"accession": ds.accession, "role": ds.role, "role_description": ds.role_description,
                    "analysis_tier": ds.analysis_tier, "modality": ds.modality, "technology": ds.technology,
                    "platform_id": ds.platform_id, "platform_name": ds.platform_name, "landing_page": ds.landing_page,
                    "related_accessions": list(ds.related_accessions), "independence_status": ds.independence_status,
                    "independence_note": ds.independence_note, "expected_source": ds.expected.source,
                    "expected_total": ds.expected.total, "expected_groups": ds.expected.groups},
        "run": ctx.describe(), "started_at": now, "finished_at": now,
        "metadata": {"sample_records_available": False}, "files": [], "steps": [
            {"step": "audit_dataset", "status": FAILED, "error": f"{type(exc).__name__}: {exc}"}],
        "findings": [finding("audit", FAILED, f"audit crashed: {type(exc).__name__}: {exc}", "see run log")],
        "issues": [{"severity": "high", "category": "audit", "description": f"audit crashed: {exc}"}],
        "next_actions": ["Inspect the run log, fix the cause and re-run the audit for this accession."],
        "audit_status": "FAILED", "audit_status_reasons": [f"audit crashed: {exc}"],
        "outputs": {"report_json": paths.rel(rep_dir / "audit_report.json")},
    }
    write_json(rep_dir / "audit_report.json", result)
    from .download import atomic_write_text
    atomic_write_text(rep_dir / "audit_report.md", render_dataset_markdown(result))
    return result


# ------------------------------------------------------------ multi-dataset
def run_overlap_checks(cfg: ProjectConfig, paths: ProjectPaths) -> list[dict[str, Any]]:
    out = []
    for oc in cfg.overlap_checks:
        values, missing = {}, []
        for acc in oc.datasets:
            p = paths.processed(acc) / "phenotype_table.tsv"
            if not p.exists():
                missing.append(acc)
                continue
            ph = pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False)
            col = oc.field if oc.field in ph.columns else None
            if col is None:
                missing.append(f"{acc} (no column {oc.field})")
                continue
            vals = [apply_id_regex(v, oc.id_regex) if oc.id_regex else v for v in ph[col].tolist()]
            values[acc] = [v for v in vals if v]
        entry = {"id": oc.id, "datasets": ", ".join(oc.datasets), "field": oc.field + (f" ~ {oc.id_regex}" if oc.id_regex else ""),
                 "note": oc.note}
        if missing or len(values) < 2:
            entry.update({"status": "UNRESOLVED_NOT_RUN", "detail": f"phenotype tables unavailable for: {missing}"})
        else:
            cmp = compare_identifier_sets(values)
            entry["pairs"] = cmp["pairs"]
            shared = sum(p["n_shared"] for p in cmp["pairs"])
            if shared:
                entry["status"] = "POSSIBLE_OVERLAP_FLAGGED"
                entry["detail"] = "; ".join(f"{'/'.join(p['datasets'])}: {p['n_shared']} shared of {p['n_values']} "
                                            f"(e.g. {p['shared_values'][:5]})" for p in cmp["pairs"])
            else:
                entry["status"] = "NO_SHARED_IDENTIFIERS_FOUND"
                entry["detail"] = ("no identical values; this does NOT establish participant independence (identifiers may "
                                   "be coded differently between deposits)")
        out.append(entry)
    write_json(paths.audit_root / "overlap_checks.json", {"generated_at": utcnow(), "checks": out})
    return out


def build_summary(cfg: ProjectConfig, paths: ProjectPaths, latest_run_id: str) -> dict[str, Any]:
    rows, ready, failed, review, processing = [], [], [], [], []
    for ds in cfg.datasets:
        p = paths.report(ds.accession) / "audit_report.json"
        if not p.exists():
            rows.append({"accession": ds.accession, "role": ds.role, "audit_status": "NOT_AUDITED",
                         "n_samples_geo": None, "groups": "", "files_available": "", "files_not_available": "",
                         "audited_at": ""})
            failed.append(f"{ds.accession}: not audited yet")
            continue
        r = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        files = r.get("files", [])
        avail = [f["name"] for f in files if f.get("requested") and f["retrieval"].get("available_locally")]
        navail = [f"{f['name']} ({f['retrieval'].get('status')})" for f in files
                  if f.get("requested") and not f["retrieval"].get("available_locally")]
        rows.append({"accession": ds.accession, "role": ds.role, "audit_status": r.get("audit_status"),
                     "n_samples_geo": (r.get("metadata") or {}).get("n_sample_records"),
                     "groups": ", ".join(f"{k}={v}" for k, v in ((r.get("phenotype") or {}).get("canonical_counts") or {}).items()),
                     "files_available": ", ".join(avail), "files_not_available": ", ".join(navail),
                     "audited_at": r.get("finished_at"), "run_id": (r.get("run") or {}).get("run_id")})
        if (r.get("metadata") or {}).get("sample_records_available"):
            ready.append(f"{ds.accession}: GEO sample metadata retrieved and parsed "
                         f"({r['metadata']['n_sample_records']} records); phenotype table at {r['outputs'].get('phenotype_table')}")
        for f in files:
            if f.get("requested") and f["retrieval"].get("available_locally") and \
                    (f.get("inspection") or {}).get("status", "").startswith("INSPECTED"):
                ready.append(f"{ds.accession}: {f['name']} retrieved (SHA-256 {str(f['retrieval'].get('sha256'))[:12]}…) and inspected")
            if f.get("processing") and f.get("requested"):
                processing.append({"accession": ds.accession, "file": f["name"], "state": f["processing"]["state"],
                                   "confidence": f["processing"]["confidence"],
                                   "requires_review": f["processing"]["requires_review"]})
        failed.extend(f"{ds.accession}: {x}" for x in navail)
        failed.extend(f"{ds.accession}: step {s['step']} failed ({s.get('error')})" for s in r.get("steps", [])
                      if s.get("status") == "FAILED")
        review.extend(f"{ds.accession} [{i['severity']}] {i['description']}" for i in r.get("issues", [])
                      if i["severity"] in ("high", "medium"))
    ov_path = paths.audit_root / "overlap_checks.json"
    overlaps = json.loads(ov_path.read_text())["checks"] if ov_path.exists() else []
    for o in overlaps:
        review.append(f"overlap check {o['id']} ({o['datasets']}): {o['status']} — {o['detail']}")
    summary = {"generated_at": utcnow(), "latest_run_id": latest_run_id, "project": cfg.project,
               "config_sha256": cfg.sha256, "versions": software_versions(), "datasets": rows,
               "ready": ready, "failed": failed, "review": review, "overlap_checks": overlaps, "processing": processing}
    write_json(paths.audit_root / "audit_summary.json", summary)
    write_csv(paths.audit_root / "audit_summary.csv", rows,
              ["accession", "role", "audit_status", "n_samples_geo", "groups", "files_available", "files_not_available",
               "audited_at", "run_id"])
    from .download import atomic_write_text
    atomic_write_text(paths.audit_root / "audit_summary.md", render_summary_markdown(summary))
    return summary


def run_audits(cfg: ProjectConfig, accessions: list[str], paths: ProjectPaths, options: AuditOptions,
               argv: list[str], client: GeoClient | None = None, run_id: str | None = None) -> dict[str, Any]:
    """Audit each accession independently; one failure never stops the others."""
    run_id = run_id or new_run_id()
    ctx = RunContext(run_id=run_id, argv=argv, config=cfg, options=options, project_root=paths.root)
    client = client or GeoClient(cfg.settings, offline=options.offline)
    paths.logs.mkdir(parents=True, exist_ok=True)
    with open(paths.logs / "run_history.jsonl", "a", encoding="utf-8") as fh:  # so interrupted runs stay traceable
        fh.write(json.dumps({"run_id": run_id, "event": "STARTED", "started_at": ctx.started_at, "argv": argv,
                             "accessions": accessions, "options": options.__dict__}) + "\n")
    results = {}
    for acc in accessions:
        ds = cfg.dataset(acc)
        try:
            results[acc] = audit_dataset(ds, ctx, paths, client)
        except Exception as exc:  # last-resort guard; audit_dataset already isolates its steps
            log.exception("Audit of %s crashed", acc)
            results[acc] = failed_result(ds, ctx, paths, exc)
    overlaps = run_overlap_checks(cfg, paths)
    summary = build_summary(cfg, paths, run_id)
    history = {"run_id": run_id, "event": "FINISHED", "started_at": ctx.started_at, "finished_at": utcnow(), "argv": argv,
               "options": options.__dict__, "config_sha256": cfg.sha256, "versions": software_versions(),
               "network_requests": len(client.request_log),
               "statuses": {a: r["audit_status"] for a, r in results.items()}}
    paths.logs.mkdir(parents=True, exist_ok=True)
    with open(paths.logs / "run_history.jsonl", "a", encoding="utf-8") as fh:  # append-only audit trail
        fh.write(json.dumps(history) + "\n")
    return {"run_id": run_id, "results": results, "overlaps": overlaps, "summary": summary}
