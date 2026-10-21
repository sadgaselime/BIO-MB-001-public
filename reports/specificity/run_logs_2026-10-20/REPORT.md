# GSE99039 specificity of the locked GSE63060 signature — run report (2026-10-20)

Authorization: explicit PI instruction 2026-10-20 ("authorize GSE99039 specificity"), after approval of the GSE99039
exclusion list (v7:625). D13 conservative specification (v7:616). The SAP remains a proposed draft (not approved, not frozen).
Command: `.venv/bin/python -I scripts/specificity_gse99039.py --version v1` produced the accepted output
reports/specificity/GSE99039/v1 (code identity and executed-code verification: no problems; two runs byte-identical).
Manifest SHA-256 80547b4d02d011664a083459c54838cea8275333aa943b6a0bb6729d278804ee;
summary SHA-256 f98213900348932ce5714af5d27d96c33ff08fcfe724034e746f902543676aa3. Full suite 370/370 before the run.

Measurable locked genes on GPL570: 190 of 200. Ten are unmapped under Option A: UQCRHL, UQCRBP1, ATP5F1EP2, LBHD1, TOMM7,
SNORD33, RPL6, RPL26, RPL17 and RPL21, all down_in_AD. The coverage rule is met in every contrast.

| Contrast (sex + batch, complete case) | n (disease / CONTROL) | θ̂ (score units) [two-sided 95% CI] | p two-sided | p Holm (3 contrasts) | Category |
|---|---|---|---|---|---|
| **IPD vs CONTROL (primary)** | 183 / 208 | +0.202 [0.036, 0.369] | 0.0175 | **0.053** | association not demonstrated |
| GPD vs CONTROL (secondary) | 40 / 208 | +0.101 [−0.175, 0.378] | 0.47 | 0.74 | association not demonstrated |
| GU vs CONTROL (descriptive) | 19 / 208 | +0.189 [−0.226, 0.603] | 0.37 | 0.74 | association not demonstrated |

Per gene (two-sided, BH within contrast): IPD has 2 of 190 at q < 0.05, both in the same direction as AD (TCIRG1, NBEAL2; up).
GPD and GU have 0 of 190. For IPD, 149 of 190 estimates share the sign of the AD signature (descriptive).

S15, age-adjusted complete case, a labelled sensitivity with no multiplicity adjustment: IPD +0.171 [−0.049, 0.391],
p = 0.13 (116 / 119); GPD +0.127 [−0.293, 0.546], p = 0.55 (19 / 119).

Interpretation (prespecified rules, v7 §8.1–8.2):
- Under the approved Holm rule, no PD association is demonstrated. The primary IPD contrast is borderline: its unadjusted
  two-sided p is 0.018 and its CI excludes 0, but its Holm-adjusted p is 0.053.
- **This is not evidence that the signature is unrelated to PD.** Non-significance is never evidence of absence, and
  without δ no equivalence or "AD-specific" conclusion can be drawn.
- Every point estimate is in the same direction as AD. A partial shared-neurodegeneration (or shared non-specific)
  component cannot be excluded.
- Magnitudes are not comparable across cohorts (v6 §8.9). There is no AD × PD contrast. Specificity does not alter the lock.
