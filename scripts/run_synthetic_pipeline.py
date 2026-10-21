#!/usr/bin/env python3
"""Run the synthetic end-to-end pipeline (SYNTHETIC DATA ONLY; no real cohort data are read).

Example:
    python scripts/run_synthetic_pipeline.py --config config/synthetic_pipeline.yaml --verify-determinism

Writes to reports/synthetic_pipeline/<run_name>_seed<seed>/ unless --out-dir is given. The output
directory is cleared first, but only if it was created by this pipeline. With
--verify-determinism the run is repeated in a temporary directory and the SHA-256 of every
analytical output is compared; the exit status is non-zero if anything differs.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biomarker_project.reporting import write_json  # noqa: E402
from biomarker_project.synthetic_pipeline import (  # noqa: E402
    WARNING, load_config, resolve_config, run_synthetic_pipeline)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "config" / "synthetic_pipeline.yaml"))
    ap.add_argument("--seed", type=int, default=None, help="override the configured seed")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--verify-determinism", action="store_true",
                    help="repeat the run in a temporary directory and compare analytical outputs")
    args = ap.parse_args(argv)

    cfg = load_config(Path(args.config))
    resolved = resolve_config(cfg, seed=args.seed)
    seed = resolved["synthetic"]["seed"]
    out_dir = Path(args.out_dir) if args.out_dir else ROOT / "reports" / "synthetic_pipeline" / f"{resolved['run_name']}_seed{seed}"
    argv_record = [sys.argv[0], *(argv if argv is not None else sys.argv[1:])]

    print(WARNING)
    summary = run_synthetic_pipeline(cfg, out_dir, seed=args.seed, config_path=args.config, argv=argv_record)
    print(f"output: {summary['out_dir']}")
    print(f"features: {summary['n_features']}; analysed samples: {summary['n_analysed']}; "
          f"q below level: {summary['n_q_below_level']}")
    print(f"analytic digest: {summary['analytic_digest']}")

    if args.verify_determinism:
        with tempfile.TemporaryDirectory(prefix="bio_mb_001_synthetic_") as tmp:
            repeat = run_synthetic_pipeline(cfg, Path(tmp) / "repeat", seed=args.seed, config_path=args.config,
                                            argv=argv_record)
        diffs = sorted(k for k in set(summary["output_sha256"]) | set(repeat["output_sha256"])
                       if summary["output_sha256"].get(k) != repeat["output_sha256"].get(k))
        check = {"repeat_run_identical": not diffs, "differing_files": diffs,
                 "first_digest": summary["analytic_digest"], "repeat_digest": repeat["analytic_digest"]}
        write_json(out_dir / "determinism_check.json", check)
        print(f"determinism check: {'IDENTICAL' if not diffs else 'DIFFERENT: ' + ', '.join(diffs)}")
        return 0 if not diffs else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
