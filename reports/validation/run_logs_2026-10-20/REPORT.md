# GSE140829 replication test of the locked GSE63060 signature — run report (2026-10-20)

Authorization: explicit PI instruction 2026-10-20 ("authorize GSE140829 validation"), after approval of the GSE140829
exclusion list (v7:625). The SAP remains a proposed draft (not approved, not frozen).
Command: `.venv/bin/python -I scripts/validation_gse140829.py --version v1` → accepted `reports/validation/GSE140829/v1` (code identity and
executed-code verification: no problems; two runs byte-identical). Full suite 357/357 before the run, with no guarded opens.
Manifest SHA-256: 0180790f06df4cd79229bd61327262b285fc227a53e033430c1af44f93208594
Summary SHA-256: 6a0556cb4dd93f38944ff1c8f0548f681cc5c66eca3dde2ea1c956e34a08e203

| Item | Result |
|---|---|
| Population | 201 AD vs 248 CTL (approved list); covariates age_at_draw, Sex, batch (19 batches) |
| Identifiability | PROCEED: 16 mixed batches (201 AD, 245 CTL on mixed), E = 0.899, VIF 1.11; r_N = 19; residual df 429 |
| Measurability / coverage | 200 of 200 locked genes measurable (D19-1 mapping); coverage met in both directions |
| **C-c (primary)** | θ̂ = 0.248 score units (SE 0.085), t = 2.91, df 429, **one-sided p = 0.0019; L_c = 0.108 > 0**; two-sided 95% CI 0.081–0.416 (descriptive) |
| C-a (secondary) | **43 of 200** measurable locked genes statistically replicated at BH q < 0.05 (36 of 172 down, 7 of 28 up); proportion 0.215, no interval |
| C-b (descriptive) | sign concordant 183/200 (0.915): down 157/172, up 26/28; no interval or p-value |

Strongest replicated genes (lowest q): RPS12, RPL32, ITGAM (up), GTF2H5, RPS25, RPL22, RPS27A, SNTB2 (up).

Interpretation limits (prespecified):
- Statistical replication of a deposited-label association; not biological or clinical validation.
- Independence of GSE140829 from AddNeuroMed participants is unverified (D10); "independent" is not used.
- θ magnitudes are not comparable across cohorts (v6 §8.9); no cross-cohort claim (X1).
- No effect correlation for GSE140829 (v7 §4.5 is GSE63061 only).
