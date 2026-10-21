#!/usr/bin/env python3
"""Audit all configured accessions independently: python scripts/run_all_audits.py"""
import sys
from pathlib import Path

try:
    from biomarker_project.cli import main
except ImportError:  # allow running from a checkout without 'pip install -e .'
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from biomarker_project.cli import main

if __name__ == "__main__":
    sys.exit(main(single=False))
