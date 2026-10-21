"""Load and validate the dataset configuration (config/datasets.yaml).

Validation collects *all* problems and raises a single ConfigError with a readable,
itemised message, so an invalid configuration can be fixed in one pass.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ACCESSION_RE = re.compile(r"^GSE\d+$")
PLATFORM_RE = re.compile(r"^GPL\d+$")
FILE_LOCATIONS = {"matrix", "suppl"}
MODALITIES = {"expression_microarray", "expression_rnaseq", "methylation_array"}
# Phenotype fields understood by sample_reconciliation.extract_field().
SIMPLE_SAMPLE_FIELDS = {"geo_accession", "title", "description", "source_name"}
INDEPENDENCE_STATUSES = {"UNRESOLVED", "VERIFIED_INDEPENDENT", "VERIFIED_OVERLAPPING", "NOT_APPLICABLE"}


class ConfigError(ValueError):
    """Raised when the configuration file is missing, unparsable or invalid."""

    def __init__(self, problems: list[str], path: str | Path | None = None):
        self.problems = problems
        where = f" in {path}" if path else ""
        msg = f"Invalid dataset configuration{where} ({len(problems)} problem(s)):\n" + "\n".join(
            f"  - {p}" for p in problems
        )
        super().__init__(msg)


@dataclass(frozen=True)
class Settings:
    geo_query_url: str
    geo_files_base_url: str
    http_timeout_seconds: float = 60
    max_retries: int = 3
    retry_backoff_seconds: float = 5
    polite_delay_seconds: float = 0.4
    max_download_mb: float = 400
    user_agent: str = "BIO-MB-001-dataset-audit"
    inspection_sample_rows: int = 5000
    concordance_max_features: int = 2000
    min_download_kb_per_s: float = 20      # abort (resumably) if average throughput stays below this
    stall_window_seconds: float = 120      # ... measured after this many seconds of transfer


@dataclass(frozen=True)
class FileSpec:
    name: str
    location: str
    retrieve: bool = True
    sample_id_field: str | None = None
    sample_id_regex: str | None = None


@dataclass(frozen=True)
class ReportedLead:
    id: str
    description: str
    source: str
    sample_ids: tuple[str, ...] = ()
    kind: str = "sample_ids"   # sample_ids | count_discrepancy


LEAD_KINDS = {"sample_ids", "count_discrepancy"}


@dataclass(frozen=True)
class PhenotypeSpec:
    diagnosis_field: str
    label_map: dict[str, str]
    ambiguous_labels: tuple[str, ...] = ()
    participant_id_field: str | None = None
    fields_of_interest: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExpectedCounts:
    source: str
    total: int | None
    groups: dict[str, int]
    described_participants: int | None = None


@dataclass(frozen=True)
class DatasetConfig:
    accession: str
    role: str
    role_description: str
    analysis_tier: str
    modality: str
    technology: str
    platform_id: str | None
    platform_name: str | None
    landing_page: str
    related_accessions: tuple[str, ...]
    independence_status: str
    independence_note: str
    expected: ExpectedCounts
    phenotype: PhenotypeSpec
    files: tuple[FileSpec, ...]
    reported_leads: tuple[ReportedLead, ...] = ()


@dataclass(frozen=True)
class OverlapCheck:
    id: str
    datasets: tuple[str, ...]
    field: str
    id_regex: str | None = None
    note: str = ""


@dataclass(frozen=True)
class ProjectConfig:
    path: Path
    sha256: str
    project: dict[str, Any]
    settings: Settings
    canonical_groups: dict[str, str]
    datasets: tuple[DatasetConfig, ...]
    overlap_checks: tuple[OverlapCheck, ...] = field(default_factory=tuple)

    def dataset(self, accession: str) -> DatasetConfig:
        for ds in self.datasets:
            if ds.accession == accession:
                return ds
        known = ", ".join(d.accession for d in self.datasets)
        raise KeyError(f"Accession {accession!r} is not configured. Configured accessions: {known}")


def _valid_field_spec(spec: str) -> bool:
    return spec in SIMPLE_SAMPLE_FIELDS or (spec.startswith("char:") and len(spec) > 5)


def _check_regex(pattern: str | None, where: str, problems: list[str]) -> None:
    if pattern is None:
        return
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        problems.append(f"{where}: invalid regular expression {pattern!r} ({exc})")
        return
    if compiled.groups < 1:
        problems.append(f"{where}: regular expression {pattern!r} must contain one capture group")


def _parse_settings(raw: Any, problems: list[str]) -> Settings | None:
    if not isinstance(raw, dict):
        problems.append("'settings' must be a mapping")
        return None
    for key in ("geo_query_url", "geo_files_base_url"):
        if not isinstance(raw.get(key), str) or not raw[key].startswith("https://"):
            problems.append(f"settings.{key} must be an https:// URL")
    numeric_positive = [
        "http_timeout_seconds", "max_download_mb", "inspection_sample_rows", "concordance_max_features",
        "stall_window_seconds",
    ]
    numeric_nonneg = ["max_retries", "retry_backoff_seconds", "polite_delay_seconds", "min_download_kb_per_s"]
    for key in numeric_positive + numeric_nonneg:
        if key in raw:
            val = raw[key]
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                problems.append(f"settings.{key} must be a number (got {val!r})")
            elif key in numeric_positive and val <= 0:
                problems.append(f"settings.{key} must be > 0 (got {val})")
            elif val < 0:
                problems.append(f"settings.{key} must be >= 0 (got {val})")
    known = set(Settings.__dataclass_fields__)
    for key in raw:
        if key not in known:
            problems.append(f"settings.{key} is not a recognised setting")
    if any(p.startswith("settings.") for p in problems):
        return None
    return Settings(**{k: v for k, v in raw.items() if k in known})


def _parse_dataset(raw: Any, idx: int, canonical: dict[str, str], problems: list[str]) -> DatasetConfig | None:
    where = f"datasets[{idx}]"
    if not isinstance(raw, dict):
        problems.append(f"{where} must be a mapping")
        return None
    acc = raw.get("accession")
    if not isinstance(acc, str) or not ACCESSION_RE.match(acc):
        problems.append(f"{where}.accession must look like 'GSE12345' (got {acc!r})")
        acc = f"<invalid:{idx}>"
    where = f"datasets[{acc}]"
    start = len(problems)

    for key in ("role", "role_description", "analysis_tier", "technology", "landing_page"):
        if not isinstance(raw.get(key), str) or not raw[key].strip():
            problems.append(f"{where}.{key} is required and must be a non-empty string")
    modality = raw.get("modality")
    if modality not in MODALITIES:
        problems.append(f"{where}.modality must be one of {sorted(MODALITIES)} (got {modality!r})")

    platform = raw.get("platform") or {}
    if not isinstance(platform, dict):
        problems.append(f"{where}.platform must be a mapping")
        platform = {}
    pid = platform.get("id")
    if pid is not None and (not isinstance(pid, str) or not PLATFORM_RE.match(pid)):
        problems.append(f"{where}.platform.id must look like 'GPL570' or be null (got {pid!r})")

    indep = raw.get("independence") or {}
    indep_status = indep.get("status", "UNRESOLVED")
    if indep_status not in INDEPENDENCE_STATUSES:
        problems.append(f"{where}.independence.status must be one of {sorted(INDEPENDENCE_STATUSES)}")

    exp_raw = raw.get("expected_counts") or {}
    if not isinstance(exp_raw, dict):
        problems.append(f"{where}.expected_counts must be a mapping")
        exp_raw = {}
    total = exp_raw.get("total")
    if total is not None and (isinstance(total, bool) or not isinstance(total, int) or total < 0):
        problems.append(f"{where}.expected_counts.total must be a non-negative integer or null (got {total!r})")
    groups = exp_raw.get("groups") or {}
    if not isinstance(groups, dict):
        problems.append(f"{where}.expected_counts.groups must be a mapping")
        groups = {}
    for g, n in groups.items():
        if g not in canonical:
            problems.append(f"{where}.expected_counts.groups: {g!r} is not a canonical group {sorted(canonical)}")
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            problems.append(f"{where}.expected_counts.groups.{g} must be a non-negative integer (got {n!r})")
    described = exp_raw.get("described_participants")
    if described is not None and (isinstance(described, bool) or not isinstance(described, int) or described < 0):
        problems.append(f"{where}.expected_counts.described_participants must be a non-negative integer")
    if not isinstance(exp_raw.get("source"), str) or not exp_raw.get("source"):
        problems.append(f"{where}.expected_counts.source must state where the reference counts come from")

    ph = raw.get("phenotype")
    if not isinstance(ph, dict):
        problems.append(f"{where}.phenotype is required and must be a mapping")
        ph = {}
    diag = ph.get("diagnosis_field")
    if not isinstance(diag, str) or not _valid_field_spec(diag):
        problems.append(
            f"{where}.phenotype.diagnosis_field must be one of {sorted(SIMPLE_SAMPLE_FIELDS)} or 'char:<key>' (got {diag!r})"
        )
    label_map = ph.get("label_map") or {}
    if not isinstance(label_map, dict) or not label_map:
        problems.append(f"{where}.phenotype.label_map must be a non-empty mapping of raw label -> canonical group")
        label_map = {}
    for raw_label, group in label_map.items():
        if group not in canonical:
            problems.append(
                f"{where}.phenotype.label_map: {raw_label!r} -> {group!r} is not a canonical group {sorted(canonical)}"
            )
    ambiguous = tuple(str(x) for x in (ph.get("ambiguous_labels") or []))
    overlap = set(ambiguous) & {str(k) for k in label_map}
    if overlap:
        problems.append(f"{where}.phenotype: labels listed as both mapped and ambiguous: {sorted(overlap)}")
    pfield = ph.get("participant_id_field")
    if pfield is not None and not _valid_field_spec(pfield):
        problems.append(f"{where}.phenotype.participant_id_field is not a recognised field spec (got {pfield!r})")
    foi = tuple(ph.get("fields_of_interest") or [])
    for f_ in foi:
        if not _valid_field_spec(f_):
            problems.append(f"{where}.phenotype.fields_of_interest: {f_!r} is not a recognised field spec")

    files_raw = raw.get("files")
    files: list[FileSpec] = []
    if not isinstance(files_raw, list) or not files_raw:
        problems.append(f"{where}.files must be a non-empty list")
        files_raw = []
    seen_files: set[tuple[str, str]] = set()
    for j, fr in enumerate(files_raw):
        fw = f"{where}.files[{j}]"
        if not isinstance(fr, dict):
            problems.append(f"{fw} must be a mapping")
            continue
        name, loc = fr.get("name"), fr.get("location")
        if not isinstance(name, str) or not name or "/" in name or name.startswith("."):
            problems.append(f"{fw}.name must be a plain file name (got {name!r})")
            continue
        if isinstance(acc, str) and ACCESSION_RE.match(acc) and not (name.startswith(acc) or name == "filelist.txt"):
            problems.append(f"{fw}.name {name!r} should start with the accession {acc} (or be filelist.txt)")
        if loc not in FILE_LOCATIONS:
            problems.append(f"{fw}.location must be one of {sorted(FILE_LOCATIONS)} (got {loc!r})")
        if (name, loc) in seen_files:
            problems.append(f"{fw}: duplicate file entry {loc}/{name}")
        seen_files.add((name, loc))
        sid = fr.get("sample_id_field")
        if sid is not None and not _valid_field_spec(sid):
            problems.append(f"{fw}.sample_id_field is not a recognised field spec (got {sid!r})")
        _check_regex(fr.get("sample_id_regex"), f"{fw}.sample_id_regex", problems)
        retrieve = fr.get("retrieve", True)
        if not isinstance(retrieve, bool):
            problems.append(f"{fw}.retrieve must be true or false")
        files.append(FileSpec(name=name, location=str(loc), retrieve=bool(retrieve),
                              sample_id_field=sid, sample_id_regex=fr.get("sample_id_regex")))

    leads = []
    for j, lr in enumerate(raw.get("reported_leads") or []):
        lw = f"{where}.reported_leads[{j}]"
        if not isinstance(lr, dict) or not all(isinstance(lr.get(k), str) and lr.get(k) for k in ("id", "description", "source")):
            problems.append(f"{lw} must have non-empty 'id', 'description' and 'source'")
            continue
        kind = lr.get("kind", "sample_ids")
        if kind not in LEAD_KINDS:
            problems.append(f"{lw}.kind must be one of {sorted(LEAD_KINDS)} (got {kind!r})")
        ids = lr.get("sample_ids") or []
        if not isinstance(ids, list):
            problems.append(f"{lw}.sample_ids must be a list")
            ids = []
        leads.append(ReportedLead(id=lr["id"], description=lr["description"].strip(), source=lr["source"],
                                  sample_ids=tuple(str(i) for i in ids), kind=kind))

    if len(problems) > start:
        return None
    return DatasetConfig(
        accession=acc,
        role=raw["role"],
        role_description=raw["role_description"].strip(),
        analysis_tier=raw["analysis_tier"],
        modality=modality,
        technology=raw["technology"],
        platform_id=pid,
        platform_name=platform.get("name"),
        landing_page=raw["landing_page"],
        related_accessions=tuple(raw.get("related_accessions") or []),
        independence_status=indep_status,
        independence_note=str(indep.get("note", "")).strip(),
        expected=ExpectedCounts(source=exp_raw["source"], total=total, groups=dict(groups),
                                described_participants=described),
        phenotype=PhenotypeSpec(
            diagnosis_field=diag,
            label_map={str(k): str(v) for k, v in label_map.items()},
            ambiguous_labels=ambiguous,
            participant_id_field=pfield,
            fields_of_interest=foi,
        ),
        files=tuple(files),
        reported_leads=tuple(leads),
    )


def parse_config(data: Any, path: str | Path = "<memory>", sha256: str = "") -> ProjectConfig:
    problems: list[str] = []
    if not isinstance(data, dict):
        raise ConfigError(["top level of the configuration must be a mapping"], path)
    if data.get("schema_version") != 1:
        problems.append(f"schema_version must be 1 (got {data.get('schema_version')!r})")
    project = data.get("project") or {}
    if not isinstance(project, dict) or not project.get("id"):
        problems.append("'project' must be a mapping with at least an 'id'")
    settings = _parse_settings(data.get("settings"), problems)
    canonical = data.get("canonical_groups")
    if not isinstance(canonical, dict) or not canonical:
        problems.append("'canonical_groups' must be a non-empty mapping of group code -> description")
        canonical = {}
    raw_datasets = data.get("datasets")
    datasets: list[DatasetConfig] = []
    if not isinstance(raw_datasets, list) or not raw_datasets:
        problems.append("'datasets' must be a non-empty list")
        raw_datasets = []
    seen: set[str] = set()
    for i, rd in enumerate(raw_datasets):
        ds = _parse_dataset(rd, i, canonical, problems)
        if ds is None:
            continue
        if ds.accession in seen:
            problems.append(f"datasets: accession {ds.accession} is configured more than once")
        seen.add(ds.accession)
        datasets.append(ds)

    overlaps = []
    for i, oc in enumerate(data.get("overlap_checks") or []):
        ow = f"overlap_checks[{i}]"
        if not isinstance(oc, dict) or not oc.get("id"):
            problems.append(f"{ow} must be a mapping with an 'id'")
            continue
        dsets = oc.get("datasets") or []
        if not isinstance(dsets, list) or len(dsets) < 2:
            problems.append(f"{ow}.datasets must list at least two accessions")
            continue
        for a in dsets:
            if isinstance(raw_datasets, list) and a not in {d.get("accession") for d in raw_datasets if isinstance(d, dict)}:
                problems.append(f"{ow}.datasets: {a!r} is not a configured accession")
        if not isinstance(oc.get("field"), str) or not _valid_field_spec(oc["field"]):
            problems.append(f"{ow}.field is not a recognised field spec (got {oc.get('field')!r})")
        _check_regex(oc.get("id_regex"), f"{ow}.id_regex", problems)
        overlaps.append(OverlapCheck(id=oc["id"], datasets=tuple(dsets), field=oc.get("field", ""),
                                     id_regex=oc.get("id_regex"), note=str(oc.get("note", "")).strip()))

    if problems:
        raise ConfigError(problems, path)
    assert settings is not None
    return ProjectConfig(path=Path(path), sha256=sha256, project=project, settings=settings,
                         canonical_groups=dict(canonical), datasets=tuple(datasets),
                         overlap_checks=tuple(overlaps))


def load_config(path: str | Path) -> ProjectConfig:
    path = Path(path)
    if not path.is_file():
        raise ConfigError([f"configuration file not found: {path}"], path)
    raw_bytes = path.read_bytes()
    try:
        data = yaml.safe_load(raw_bytes)
    except yaml.YAMLError as exc:
        raise ConfigError([f"YAML could not be parsed: {exc}"], path) from exc
    return parse_config(data, path=path, sha256=hashlib.sha256(raw_bytes).hexdigest())
