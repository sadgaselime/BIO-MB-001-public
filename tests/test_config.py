import copy
from pathlib import Path

import pytest
import yaml

from biomarker_project.config import ConfigError, load_config, parse_config

PROJECT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "datasets.yaml"


def _raw(config_path):
    return yaml.safe_load(config_path.read_text())


def test_valid_config_loads(cfg):
    assert [d.accession for d in cfg.datasets] == ["GSE1000001", "GSE1000002"]
    ds = cfg.dataset("GSE1000001")
    assert ds.expected.total == 5 and ds.expected.groups == {"AD": 2, "HC": 2}
    assert ds.phenotype.label_map == {"AD": "AD", "CTL": "HC"}
    assert ds.files[1].sample_id_field == "title"
    assert len(cfg.sha256) == 64


def test_unknown_accession_lookup_is_readable(cfg):
    with pytest.raises(KeyError, match="not configured"):
        cfg.dataset("GSE999")


@pytest.mark.parametrize("mutate, expected_fragment", [
    (lambda d: d["datasets"][0].__setitem__("accession", "GSM12"), "accession must look like"),
    (lambda d: d["datasets"].append(copy.deepcopy(d["datasets"][0])), "configured more than once"),
    (lambda d: d["datasets"][0]["expected_counts"]["groups"].__setitem__("AD", -1), "non-negative integer"),
    (lambda d: d["datasets"][0]["phenotype"]["label_map"].__setitem__("X", "NOT_A_GROUP"), "not a canonical group"),
    (lambda d: d["datasets"][0].pop("role"), "role is required"),
    (lambda d: d["datasets"][0].__setitem__("modality", "proteomics"), "modality must be one of"),
    (lambda d: d["datasets"][0]["files"][0].__setitem__("location", "elsewhere"), "location must be one of"),
    (lambda d: d["datasets"][0]["platform"].__setitem__("id", "570"), "platform.id must look like"),
    (lambda d: d["datasets"][0]["files"][1].__setitem__("sample_id_regex", "no_group"), "capture group"),
    (lambda d: d["settings"].__setitem__("max_download_mb", 0), "must be > 0"),
    (lambda d: d["overlap_checks"][0].__setitem__("datasets", ["GSE1000001", "GSE42"]), "not a configured accession"),
    (lambda d: d["datasets"][0]["phenotype"].__setitem__("diagnosis_field", "status"), "diagnosis_field must be"),
    (lambda d: d["datasets"][0]["reported_leads"][0].__setitem__("kind", "rumour"), "kind must be one of"),
])
def test_invalid_config_raises_readable_error(config_path, mutate, expected_fragment):
    data = _raw(config_path)
    mutate(data)
    with pytest.raises(ConfigError) as exc:
        parse_config(data, path="test.yaml")
    assert expected_fragment in str(exc.value)
    assert "test.yaml" in str(exc.value)


def test_multiple_problems_reported_together(config_path):
    data = _raw(config_path)
    data["datasets"][0]["modality"] = "bad"
    data["datasets"][1]["expected_counts"]["total"] = "many"
    with pytest.raises(ConfigError) as exc:
        parse_config(data)
    assert len(exc.value.problems) >= 2


def test_missing_and_unparsable_files(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.yaml")
    bad = tmp_path / "bad.yaml"
    bad.write_text("datasets: [unclosed")
    with pytest.raises(ConfigError, match="YAML could not be parsed"):
        load_config(bad)


def test_project_config_represents_the_six_datasets():
    cfg = load_config(PROJECT_CONFIG)
    accs = {d.accession: d for d in cfg.datasets}
    assert set(accs) == {"GSE63060", "GSE63061", "GSE140829", "GSE99039", "GSE165082", "GSE165081"}
    assert accs["GSE63060"].platform_id == "GPL6947"
    assert accs["GSE63060"].expected.groups == {"AD": 145, "MCI": 80, "HC": 104}
    assert accs["GSE63060"].expected.total == 329
    assert accs["GSE63061"].platform_id == "GPL10558" and accs["GSE63061"].expected.total == 388
    assert accs["GSE140829"].platform_id == "GPL15988"
    assert accs["GSE140829"].expected.groups == {"AD": 204, "MCI": 134, "HC": 249}
    assert accs["GSE99039"].platform_id == "GPL570"
    assert accs["GSE99039"].expected.groups == {"HC": 233, "PD": 205, "OTHER_NEURO": 48}
    assert accs["GSE165082"].modality == "expression_rnaseq" and accs["GSE165082"].expected.described_participants == 30
    assert accs["GSE165081"].modality == "methylation_array" and accs["GSE165081"].expected.total == 28
    # Related cohorts are never pre-declared independent.
    assert accs["GSE63061"].independence_status == "UNRESOLVED"
    assert accs["GSE140829"].independence_status == "UNRESOLVED"
    # Genetic PD and unaffected carriers are kept separate from the main groups.
    lm = accs["GSE99039"].phenotype.label_map
    assert lm["GPD"] == "PD_GENETIC" and lm["GENETIC_UNAFFECTED"] == "GENETIC_UNAFFECTED"
    # Reported leads exist but no sample IDs are hard-coded as exclusions.
    assert all(not lead.sample_ids for lead in accs["GSE63060"].reported_leads)
