"""Deterministic synthetic expression fixture with known planted signals.

SYNTHETIC DATA ONLY. Nothing produced here is derived from, or says anything about, a real
cohort. The fixture mimics the *shape* of the planned GSE63060 analysis (log2-like expression,
AD / CTL / MCI labels, age and sex) so the pipeline can be exercised end to end.

Planted structure (all values are known and written to the truth table):
  * `n_up` features with group effect +effect_log2 and `n_down` with -effect_log2 (AD - CTL);
    MCI samples receive half of the effect;
  * `n_age` features with a linear age effect (per year);
  * `n_sex` features with a male-minus-female effect;
  * every feature has its own baseline mean and residual SD;
  * optionally (include_sex_probes) XIST and the 13 Y probes of the approved R8 probe list, with
    female/male levels, and `n_recorded_sex_swaps` samples whose recorded sex is flipped (planted
    R8 discordance; marked in the `synthetic_truth_recorded_sex_swapped` metadata column).
The same seed always yields identical data (numpy PCG64 via `default_rng`, fixed draw order).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

GROUPS = ("AD", "CTL", "MCI")


@dataclass(frozen=True)
class SyntheticSpec:
    seed: int = 20261011
    n_ad: int = 60
    n_ctl: int = 60
    n_mci: int = 20
    n_features: int = 2000
    n_up: int = 25
    n_down: int = 25
    effect_log2: float = 1.0
    n_age: int = 20
    age_effect_per_year: float = 0.03
    n_sex: int = 10
    sex_effect_male: float = 2.0
    noise_sd: float = 0.5
    age_mean_ad: float = 76.0
    age_mean_ctl: float = 74.0
    age_mean_mci: float = 75.0
    age_sd: float = 6.0
    p_female: float = 0.6
    include_sex_probes: bool = False   # append XIST + 13 Y probes (R8 probe IDs) with sex-specific levels
    n_recorded_sex_swaps: int = 0      # samples whose recorded sex is flipped (planted R8 discordance)

    def __post_init__(self) -> None:
        if min(self.n_ad, self.n_ctl, self.n_mci, self.n_features) < 0:
            raise ValueError("sample and feature counts must be non-negative")
        if self.n_up + self.n_down + self.n_age + self.n_sex > self.n_features:
            raise ValueError("planted feature blocks exceed n_features")
        if self.noise_sd <= 0 or self.age_sd <= 0:
            raise ValueError("noise_sd and age_sd must be positive")
        if not 0.0 <= self.p_female <= 1.0:
            raise ValueError("p_female must be in [0, 1]")
        if self.n_recorded_sex_swaps and not self.include_sex_probes:
            raise ValueError("n_recorded_sex_swaps requires include_sex_probes")
        if not 0 <= self.n_recorded_sex_swaps <= self.n_ad + self.n_ctl + self.n_mci:
            raise ValueError("n_recorded_sex_swaps out of range")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SyntheticCohort:
    expression: pd.DataFrame   # features x samples, index 'feature_id'
    samples: pd.DataFrame      # one row per sample (deliberately NOT in matrix column order)
    truth: pd.DataFrame        # one row per feature: planted effects
    spec: SyntheticSpec


def generate_synthetic_cohort(spec: SyntheticSpec) -> SyntheticCohort:
    rng = np.random.default_rng(spec.seed)
    counts = {"AD": spec.n_ad, "CTL": spec.n_ctl, "MCI": spec.n_mci}
    groups = np.array([g for g in GROUPS for _ in range(counts[g])], dtype=object)
    n = groups.size
    sample_ids = [f"SYN-S{i:04d}" for i in range(1, n + 1)]
    age_means = {"AD": spec.age_mean_ad, "CTL": spec.age_mean_ctl, "MCI": spec.age_mean_mci}
    age = np.round(np.array([age_means[g] for g in groups]) + rng.normal(0.0, spec.age_sd, n), 1)
    sex = np.where(rng.random(n) < spec.p_female, "F", "M")

    f = spec.n_features
    feature_ids = [f"SYN-P{i:05d}" for i in range(1, f + 1)]
    baseline = rng.uniform(6.0, 12.0, f)
    feature_sd = spec.noise_sd * rng.lognormal(0.0, 0.25, f)
    group_eff = np.zeros(f)
    age_eff = np.zeros(f)
    sex_eff = np.zeros(f)
    perm = rng.permutation(f)
    blocks = np.split(perm[: spec.n_up + spec.n_down + spec.n_age + spec.n_sex],
                      np.cumsum([spec.n_up, spec.n_down, spec.n_age]))
    group_eff[blocks[0]] = spec.effect_log2
    group_eff[blocks[1]] = -spec.effect_log2
    age_eff[blocks[2]] = spec.age_effect_per_year
    sex_eff[blocks[3]] = spec.sex_effect_male

    group_weight = np.array([{"AD": 1.0, "CTL": 0.0, "MCI": 0.5}[g] for g in groups])
    age_centred = age - 75.0
    male = (sex == "M").astype(float)
    noise = rng.normal(0.0, 1.0, (f, n)) * feature_sd[:, None]
    values = (baseline[:, None] + np.outer(group_eff, group_weight) + np.outer(age_eff, age_centred)
              + np.outer(sex_eff, male) + noise)

    expression = pd.DataFrame(values, index=pd.Index(feature_ids, name="feature_id"), columns=sample_ids)
    samples = pd.DataFrame({"sample_id": sample_ids, "group": groups.astype(str), "age": age, "sex": sex,
                            "data_origin": "SYNTHETIC"})
    # Metadata rows are shuffled so that the pipeline must align by identifier, never by position.
    samples = samples.iloc[rng.permutation(n)].reset_index(drop=True)
    if spec.include_sex_probes:
        # Drawn after all other values so that the rest of the cohort is unchanged by this option.
        from .qc_r8 import XIST_PROBE, Y_PROBES
        xist = 11.0 - 5.0 * male + rng.normal(0.0, 0.3, n)
        ys = [5.0 + 4.0 * male + rng.normal(0.0, 0.3, n) for _ in Y_PROBES]
        sex_rows = pd.DataFrame(np.vstack([xist, *ys]), index=pd.Index([XIST_PROBE, *Y_PROBES], name="feature_id"),
                                columns=sample_ids)
        expression = pd.concat([expression, sex_rows])
        swapped = set(np.array(sample_ids)[rng.choice(n, spec.n_recorded_sex_swaps, replace=False)])
        flip = samples["sample_id"].isin(swapped)
        samples.loc[flip, "sex"] = samples.loc[flip, "sex"].map({"F": "M", "M": "F"})
        samples["synthetic_truth_recorded_sex_swapped"] = flip
    truth = pd.DataFrame({"feature_id": feature_ids, "planted_group_effect_ad_minus_ctl": group_eff,
                          "planted_age_effect_per_year": age_eff, "planted_sex_effect_male": sex_eff,
                          "baseline_mean": baseline, "residual_sd": feature_sd})
    if spec.include_sex_probes:
        n_y = len(sex_rows) - 1
        truth = pd.concat([truth, pd.DataFrame({
            "feature_id": list(sex_rows.index), "planted_group_effect_ad_minus_ctl": 0.0,
            "planted_age_effect_per_year": 0.0, "planted_sex_effect_male": [-5.0] + [4.0] * n_y,
            "baseline_mean": [11.0] + [5.0] * n_y, "residual_sd": 0.3})], ignore_index=True)
    return SyntheticCohort(expression=expression, samples=samples, truth=truth, spec=spec)
