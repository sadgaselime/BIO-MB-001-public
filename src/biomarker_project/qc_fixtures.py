"""Deterministic synthetic QC cohorts, one per R8/R9 rule boundary. SYNTHETIC DATA ONLY.

Every fixture is a small cohort (probes x arrays) built from a seeded generator or exact
arithmetic, with the expected outcome of its target arrays stated in `purpose` and verified in
tests/test_qc_stage_a.py. Exact-value fixtures (identical arrays, exact negatives) use balanced
+/-1 patterns whose Pearson correlations are exactly +1 or -1 in floating point.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .qc_r8 import XIST_PROBE, Y_PROBES
from .qc_stage_a import QCCohortInput

N_PROBES = 200


def _cohort(cid: str, values: np.ndarray, purpose: str, sex=None, probes=None, blocked=None) -> QCCohortInput:
    n = values.shape[1]
    ids = [f"{cid}-A{i:02d}" for i in range(1, n + 1)]
    probes = probes or [f"SYN-Q{i:04d}" for i in range(1, values.shape[0] + 1)]
    sex = list(sex) if sex is not None else ["F" if i % 2 else "M" for i in range(n)]
    expr = pd.DataFrame(values, index=pd.Index(probes, name="feature_id"), columns=ids)
    samples = pd.DataFrame({"sample_id": ids, "sex": sex, "data_origin": "SYNTHETIC"})
    return QCCohortInput(cid, expr, samples, blocked, purpose)


def _ordinary(rng, n_arrays: int, n_probes: int = N_PROBES) -> np.ndarray:
    profile = rng.uniform(6, 12, n_probes)                       # shared probe means -> r ~ 0.9+
    return profile[:, None] + rng.normal(0, 0.5, (n_probes, n_arrays))


def _balanced(n_probes: int = 16) -> np.ndarray:
    return np.tile([1.0, -1.0], n_probes // 2)                   # mean 0, sum of squares = n_probes


def _sex_block(rng, sex: list[str], xist_missing=(), y_missing=()) -> tuple[np.ndarray, list[str]]:
    male = np.array([s == "M" for s in sex], dtype=float)
    xist = 11.0 - 5.0 * male + rng.normal(0, 0.3, male.size)
    ys = [5.0 + 4.0 * male + rng.normal(0, 0.3, male.size) for _ in Y_PROBES]
    block = np.vstack([xist, *ys])
    for a in xist_missing:
        block[0, a] = np.nan
    for a in y_missing:
        block[1:, a] = np.nan
    return block, [XIST_PROBE, *Y_PROBES]


def build_fixtures(seed: int) -> list[QCCohortInput]:
    rng = np.random.default_rng(seed)
    out = []

    # --- R9 boundaries ---------------------------------------------------------------
    v = _ordinary(rng, 20)
    v[:, 19] = v[:, 19] * 0.2 + rng.normal(0, 3.0, N_PROBES)     # one degraded array
    out.append(_cohort("FX-R9-CLEAN", v, "R9 completes; A20 has a low correlation profile and is expected to be flagged (k = 3)"))

    v = _ordinary(rng, 20)
    v[:, 0] = 7.5                                                 # constant array
    v[5, 3] = np.nan                                              # probe 6 dropped at A0 (reported)
    out.append(_cohort("FX-R9-ZERO-VARIANCE", v, "A01 zero variance -> A0 numerical failure; one probe with a NaN is dropped"))

    v = _ordinary(rng, 11)
    v[:, 0] = 3.0
    out.append(_cohort("FX-R9-MIN-ARRAYS-10", v, "11 arrays, 1 A0 failure -> exactly 10 remain: R9 proceeds (A0 and A3b boundaries met)"))

    v = _ordinary(rng, 10)
    v[:, 0] = 3.0
    out.append(_cohort("FX-R9-MIN-ARRAYS-9", v, "10 arrays, 1 A0 failure -> 9 remain: R9 not applicable at A0; the A0 failure is retained"))

    big = _ordinary(rng, 22)
    big[:, :12] = rng.normal(0, 1, (N_PROBES, 12)) * 1e200        # squared norms overflow -> r non-finite among these
    out.append(_cohort("FX-R9-NONFINITE-A1", big,
                       "A01-A12 have 11 of 21 pairs non-finite -> A1 numerical failures; their finite r_ij (= 0) still "
                       "enter the medians of A13-A22 (fixed matrix), which become 0 -> S = 0 -> R9 not applicable at A4; "
                       "A1 failures retained"))

    base = rng.uniform(6, 12, N_PROBES)
    clones = base[:, None] + rng.normal(0, 1e-6, (N_PROBES, 16))
    others = base[:, None] + rng.normal(0, 0.5, (N_PROBES, 14))
    others[:, 1] = others[:, 0] + rng.normal(0, 1e-6, N_PROBES)  # one ordinary near-identical pair
    out.append(_cohort("FX-R9-NEAR-IDENTICAL", np.hstack([clones, others]),
                       "A01-A16 near-identical clones: median r >= 1 - 1e-8 -> referred to D18 (Option C), not failures; "
                       "A17/A18 are an A2 pair but their medians are ordinary -> A2-listed only, scored normally"))

    a = _balanced()
    ordinary = rng.normal(0, 1, (16, 10))
    vals = np.hstack([np.tile(a[:, None], (1, 11)), -a[:, None], ordinary])
    out.append(_cohort("FX-R9-NEGATIVE-MEDIAN", vals,
                       "A12 = exact negative of 11 identical arrays: m = -1 -> A3 numerical failure; the 11 identical "
                       "arrays are A2 pairs (r = 1) but their medians are not near 1, so they are scored with equal z, "
                       "giving S = 0 -> R9 not applicable at A4; the A3 failure is retained"))

    near = base[:, None] + rng.normal(0, 1e-6, (N_PROBES, 10))
    two = base[:, None] + rng.normal(0, 0.5, (N_PROBES, 2))
    out.append(_cohort("FX-R9-A3B-STOP", np.hstack([near, two]),
                       "12 arrays, 10 referred to D18 -> only 2 finite z_i -> R9 not applicable at A3b; referrals stay referrals"))

    # --- R8 boundaries ---------------------------------------------------------------
    sex = ["F"] * 12 + ["M"] * 12
    block, probes = _sex_block(rng, sex, xist_missing=[2], y_missing=[3, 14])
    block[0, 0] = 11.5                                              # A01: female pattern on X ...
    block[1:, 0] = 9.5                                              # ... male pattern on Y -> ambiguous
    rec = list(sex)
    rec[5] = "M"                                                    # A06: female array recorded M -> two-axis discordant
    rec[3] = "M"                                                    # A04: Y missing, X female-type, recorded M -> single-axis discordant
    rec[20] = None                                                  # A21: recorded sex missing -> unassessable
    block[0, 6], block[1:, 6] = np.nan, np.nan                      # A07: finite on neither axis -> unassessable (non-finite)
    out.append(_cohort("FX-R8-CATEGORIES", np.vstack([block, _ordinary(rng, 24, 30)]),
                       "R8 informative: A01 ambiguous; A06 two-axis discordant (Q1 candidate); A04 single-axis discordant; "
                       "A03 single-axis (Y only) concordant; A07 unassessable (non-finite); A21 unassessable (recorded missing)",
                       sex=rec, probes=probes + [f"SYN-Q{i:04d}" for i in range(1, 31)]))

    block, probes = _sex_block(rng, ["F", "M"] * 4)
    out.append(_cohort("FX-R8-UNINFORMATIVE", np.vstack([block, _ordinary(rng, 8, 30)]),
                       "8 arrays < 2·n_min: both axes degenerate -> completed — uninformative; V-A gate closed; "
                       "R9 not applicable at A0 (< 10 arrays)",
                       sex=["F", "M"] * 4, probes=probes + [f"SYN-Q{i:04d}" for i in range(1, 31)]))

    sex = ["F", "M"] * 6
    block, probes = _sex_block(rng, sex)
    keep = [0, 1]                                                   # XIST + RPS4Y1 only -> 1 Y gene
    out.append(_cohort("FX-R8-NOT-APPLICABLE", np.vstack([block[keep], _ordinary(rng, 12, 30)]),
                       "only 1 distinct Y gene present -> R8 not applicable (A0); V-A gate open",
                       sex=sex, probes=[probes[k] for k in keep] + [f"SYN-Q{i:04d}" for i in range(1, 31)]))

    sex = ["F", "M"] * 6
    block, probes = _sex_block(rng, sex)
    out.append(_cohort("FX-R8-BLOCKED", np.vstack([block, _ordinary(rng, 12, 30)]),
                       "external dependency unresolved -> R8 blocked; R9 still runs, outputs unusable until the gate opens",
                       sex=sex, probes=probes + [f"SYN-Q{i:04d}" for i in range(1, 31)],
                       blocked="synthetic stand-in for an unresolved probe-mapping dependency"))
    return out
