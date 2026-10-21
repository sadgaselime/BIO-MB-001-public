"""BIO-MB-001: reproducible blood-transcriptome analysis of Alzheimer's disease.

Library modules for GEO retrieval and audit (Phase 1), code identity (hashed code, environment and inputs with
executed-code verification), QC (R8 sex check, R9 outliers, QC Stage A), the limma backend, sample policy and
differential expression. The real-data analyses run through the lifecycle-governed runners in scripts/; the synthetic
pipeline (synthetic_pipeline.py) runs on simulated data only.
"""
__version__ = "0.1.0"
