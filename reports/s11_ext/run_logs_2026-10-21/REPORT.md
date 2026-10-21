# S11-ext (POST HOC) — composition-adjusted replication and specificity — run report (2026-10-21)

**Label: POST HOC.** Approved 2026-10-21 (S11-ext §, v7:624), after the GSE140829 and GSE99039 results were known; family B;
never replaces a primary result; never alters the lock. Authorization: explicit PI instruction ("authorize S11-ext").
Output reports/s11_ext/v1 accepted (code identity and executed-code verification: no problems; two runs byte-identical).
Manifest SHA-256 2ace292f21225eb7716187b3b2870a3ce52cbf12a8ba75b221f5b09c1500eba0; summary SHA-256
d81d005894449aa661466e2ad35d690e3e77ed4f25955d89bbe16ce59d3ba297. Full suite 378/378 before the run.

## GSE140829 replication (201 AD vs 248 CTL; identifiability PROCEED, VIF 1.15)

| Test | Primary (accepted) | + composition scores (S11-ext) |
|---|---|---|
| C-c θ̂ (one-sided p; L_c) | 0.248 (p = 0.0019; L_c 0.108) | **0.116 (p = 0.041; L_c 0.0065)** |
| C-a replicated at q < 0.05 | 43 / 200 | **1 / 200** |
| C-b concordant | 183 / 200 (0.915) | 155 / 200 (0.775) |

## GSE99039 specificity (Holm across the three contrasts)

| Contrast | Primary θ̂ (p; Holm p) | + composition scores θ̂ [95% CI] (p; Holm p) |
|---|---|---|
| IPD vs CONTROL (183 / 208) | +0.202 (0.018; 0.053) | **+0.080 [−0.062, 0.222] (0.27; 0.51)** |
| GPD vs CONTROL (40 / 208) | +0.101 (0.47; 0.74) | +0.150 [−0.072, 0.372] (0.18; 0.51) |
| GU vs CONTROL (19 / 208) | +0.189 (0.37; 0.74) | +0.231 [−0.101, 0.563] (0.17; 0.51) |

Per gene after adjustment: 0 of 190 at q < 0.05 in every contrast (primary IPD: 2).

## Interpretation (post hoc; hypothesis-generating)
- In GSE140829 the composite shift is **attenuated by about half** but stays above zero at the one-sided 5% level. Gene-level
  replication almost disappears (43 to 1), and direction agreement falls to 78%. **Most of the externally replicated
  signal tracks leukocyte-composition indices.**
- The borderline IPD shift shrinks by about 60% and is no longer near significance. **It is largely composition-related.**
- Contrast with S11 in the discovery cohort, where all 199 locked genes survived: composition explains much more of the
  signal outside the discovery cohort. The signature's discovery-specific component did not transport; what transported
  is largely composition-linked.
- Adjustment cannot separate confounding from mediation. AD-related changes in blood leukocyte mix may themselves be part
  of the disease-associated biology.
- Limits: post hoc; marker indices are noisy relative proxies developed mainly for tissue; residual confounding and
  over-adjustment are both possible.
