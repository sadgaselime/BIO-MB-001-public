# S11 cell-composition sensitivity, GSE63060 — run report (2026-10-21)

**Label: method chosen 2026-10-21, after primary results (D21 option K1); family B; never alters the lock.**
Authorization: explicit PI instruction 2026-10-21 ("AUTHORIZE S11"). Output reports/discovery/GSE63060/s11_v1 was accepted
(code identity and executed-code verification: no problems; two runs byte-identical). Manifest SHA-256
e1d7053252f570d73f0be06966352e6b7472df459491b1cbf36cbd9854100203. Full suite 375/375 before the run.

Model: the H1 discovery model (age, sex, chip) plus five MCP-counter marker scores. Markers present: T cells 14/16,
B lineage 7/9, NK 8/9, monocytic 7/7, neutrophils 14/15. Identifiability: PROCEED (E = 0.763, VIF 1.31, 25 mixed chips,
residual df 168).

| Comparison with the primary fit | Result |
|---|---|
| **Locked genes (199; CD3D excluded as a T-cell marker)** | **199/199 same sign and still q < 0.05**; Spearman ρ of t = 0.937; median abs(effect) ratio S11/primary = 0.84 |
| All genes | 857 at q < 0.05 (vs 1,401 primary); of the 1,401 primary genes, 1,401 same sign and 783 still q < 0.05; Spearman ρ of t = 0.924 |

Descriptive score means, AD vs CTL (z units; no test): neutrophils +0.049 vs −0.118; monocytic +0.030 vs −0.074;
NK +0.040 vs −0.098; T cells −0.030 vs +0.072; B lineage ~0 in both.

Interpretation:
- The locked signature is **not explained by these composition indices**: every gene keeps its direction and significance,
  and effects shrink by about 16% (median).
- The broader discovery signal is **partly composition-related**: 44% of the primary associations (618 of 1,401) lose
  significance after adjustment, although all keep their sign.
- AD arrays show slightly higher myeloid/NK and lower T-cell indices (descriptive).
- Limits: the marker scores are relative, noisy proxies, and the markers were developed mainly for tissue, so residual
  confounding by composition cannot be excluded. Discovery cohort only; S11-ext (other cohorts) is not decided.
