#!/usr/bin/env python3
"""Audit a single configured accession, e.g.: python scripts/run_dataset_audit.py --accession GSE63060"""
import sys
from pathlib import Path

try:
    from biomarker_project.cli import main
except ImportError:  # allow running from a checkout without 'pip install -e .'
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from biomarker_project.cli import main

if __name__ == "__main__":
    sys.exit(main(single=True))
