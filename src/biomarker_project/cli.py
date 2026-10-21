"""Shared command-line handling for scripts/run_dataset_audit.py and scripts/run_all_audits.py."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .audit_pipeline import AuditOptions, ProjectPaths, new_run_id, run_audits, setup_logging
from .config import ConfigError, load_config

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def build_parser(single: bool) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=("Audit one configured GEO accession." if single else "Audit every configured GEO accession independently.")
        + " Phase 1 only: retrieval, provenance, inspection and sample reconciliation.")
    if single:
        p.add_argument("--accession", required=True, help="configured accession, e.g. GSE63060")
    else:
        p.add_argument("--accessions", nargs="+", help="restrict to these configured accessions")
    p.add_argument("--config", type=Path, default=None, help="dataset configuration (default: <project>/config/datasets.yaml)")
    p.add_argument("--project-root", type=Path, default=DEFAULT_ROOT, help="project root (default: repository root)")
    p.add_argument("--offline", action="store_true",
                   help="never use the network; audit only files already present locally")
    p.add_argument("--skip-downloads", action="store_true",
                   help="metadata-only run: retrieve GEO metadata but no data files (existing files are still verified)")
    p.add_argument("--refresh-metadata", action="store_true",
                   help="re-query GEO metadata; changed responses are saved as new timestamped snapshots")
    p.add_argument("--max-download-mb", type=float, default=None, help="override settings.max_download_mb")
    p.add_argument("-v", "--verbose", action="store_true", help="debug logging on the console")
    return p


def main(single: bool, argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)
    args = build_parser(single).parse_args(argv[1:])
    root = args.project_root.resolve()
    paths = ProjectPaths(root)
    run_id = new_run_id()
    log_path = setup_logging(paths, run_id, args.verbose)
    log = logging.getLogger("biomarker_project.cli")
    try:
        cfg = load_config(args.config or root / "config" / "datasets.yaml")
    except ConfigError as exc:
        log.error("%s", exc)
        return 2
    if single:
        try:
            cfg.dataset(args.accession)
        except KeyError as exc:
            log.error("%s", exc.args[0])
            return 2
        accessions = [args.accession]
    else:
        accessions = args.accessions or [d.accession for d in cfg.datasets]
        unknown = [a for a in accessions if a not in {d.accession for d in cfg.datasets}]
        if unknown:
            log.error("Unknown accession(s): %s", unknown)
            return 2
    opts = AuditOptions(offline=args.offline, skip_downloads=args.skip_downloads,
                        refresh_metadata=args.refresh_metadata, max_download_mb=args.max_download_mb)
    log.info("Run %s | mode=%s | accessions=%s | log=%s", run_id, "OFFLINE" if opts.offline else "NETWORK",
             accessions, log_path)
    out = run_audits(cfg, accessions, paths, opts, argv=argv, run_id=run_id)
    print("\nAudit statuses (no dataset is ever labelled PASS):")
    for acc, r in out["results"].items():
        print(f"  {acc:<10} {r['audit_status']:<28} {r['outputs'].get('report_markdown') or r['outputs'].get('report_json')}")
    print(f"Summary: {paths.rel(paths.audit_root / 'audit_summary.md')}\nLog: {paths.rel(log_path)}")
    return 0
