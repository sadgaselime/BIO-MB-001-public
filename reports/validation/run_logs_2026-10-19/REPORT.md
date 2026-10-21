# GSE63061 consistency test of the locked GSE63060 signature — run report (2026-10-19)

Authorization: explicit PI instruction 2026-10-19 ("i authorize"), after approval of the GSE63061 exclusion list (v7:625)
and the GSE63061 descriptive methods (v7:68, 69, 83). The SAP remains a proposed draft (not approved, not frozen).

Command: `.venv/bin/python -I scripts/validation_gse63061.py --version v1` → accepted `reports/validation/GSE63061/v1`
(code identity and executed-code verification: no problems; two runs byte-identical). The run-created
`scripts/__pycache__/_executed_code.cpython-313.pyc` was deleted afterwards.
Manifest SHA-256: d340593ab6d8ae03b68517f71f235ed978b3e6255d5a2f4ec3e99d38a16bfc69
Summary SHA-256: 53dc319edc8093cfb183c9d9f0b8e1e2d6b7e366852f513a925618981fb145fb

| Item | Result |
|---|---|
| Population | 139 AD vs 133 CTL (approved list); covariates age, sex, chip (34 chips) |
| Identifiability | PROCEED: 31 mixed chips (127 AD, 129 CTL on mixed), E = 0.813, VIF 1.23; r_N = 36; residual df 235 |
| Measurability / coverage | 200 of 200 locked genes measurable (28 up, 172 down); coverage met in both directions |
| C-c (primary) | θ̂ = 1.242 score units (SE 0.155), t = 7.99, df 235, one-sided p = 3.0e-14; L_c = 0.985 > 0; two-sided 95% CI 0.936–1.549 (descriptive) |
| C-a (secondary) | 194 of 200 measurable locked genes consistent at BH q < 0.05 (168 of 172 down, 26 of 28 up); proportion 0.97, no interval |
| C-b (descriptive) | sign concordant 198/200 (0.99): down 170/172, up 28/28; no interval or p-value |
| §4.5 correlation | Pearson r = 0.923 over 200 genes; Fisher-z 95% interval 0.899–0.941, **nominal** |

Interpretation limits (prespecified):
- GSE63061 is a related-cohort **consistency** cohort; "replicated" is not used. Possible participant overlap with
  GSE63060 (H9) may inflate every agreement measure, and cannot be excluded with the deposited data.
- Statistical consistency is not biological or clinical validation. θ magnitudes are not comparable across cohorts.
- The Fisher-z interval assumes independent genes; co-expression, selection and overlap make it too narrow.
- Independent replication requires GSE140829 (blocked on D19/D11).
