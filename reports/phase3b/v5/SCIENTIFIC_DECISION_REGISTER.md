# BIO-MB-001 Phase 3B — Scientific decision register for SAP draft v5

**Reviewed file:** `reports/phase3b/v5/STATISTICAL_ANALYSIS_PLAN_DRAFT.md`
(SHA-256 `33d11ac677bb59a6b689cbe793897938608248db674e4cc2be0cab4ab2362f0e`; 970 lines).

**Also read:**

- `reports/phase3b/v4/SCIENTIFIC_CONSISTENCY_AUDIT.md`;
- the inherited v3 §3.4 table (v3:156–175) and v3 register row D13 (v3:653), which v5 §0.2 keeps
  active or supersedes;
- `reports/phase2c/GSE63060/v2/SAMPLE_IDENTITY_AND_COHORT_HISTORY_REPORT.md` rows 7–8 (lines 42–43);
- `reports/phase2c/GSE63060/v1/sources/PMC7175937.xml` (Patel 2020), text search only.

**Status:**

- This is a review document, **not a SAP revision**.
- No decision is approved or settled. The official approval-gate status is unchanged (v5:3–7).
- No analysis, QC statistic, metadata pass/fail check, diagnosis-by-chip count, model, gene selection,
  pathway analysis or signature lock was run.
- No expression value was read.
- No network or Notion access.

**Conventions:**

- **FACT** = stated in a project file, cited `v5:L` (line numbers of the v5 file) or file:line.
- **ASSESSMENT** = the reviewer's statistical or scientific reasoning. It is not externally validated
  and no citation is added.
- **RECOMMENDATION** = a suggested next action. It is not a decision.

**Classification (one primary class per decision; secondary classes noted where relevant):**

| Class | Meaning |
|---|---|
| **EV** | Evidence-dependent: more source information is required |
| **PI** | PI decision: a scientific choice must be approved |
| **TS** | Technical specification: the rule needs a precise, implementable definition |
| **RL** | Ready for later implementation: sufficiently specified, not yet authorized |

---

## Part 1 — Review of the six priority areas

### A. D6: gene-level inference and annotation (v5 §5, lines 402–477; also §6.2, §7.2, §8.1, §9)

**FACT.**

- **G1:** highest mean "over the samples of the model being fitted"; ties → probe ID ascending
  (v5:418).
- **G1b:** highest mean over a prespecified disjoint MCI selection set; undefined for GSE99039
  (v5:419).
- **G2:** an annotation-only rule; requires an unverified resource and a GPL570 rule (v5:420).
- **G3:** mean of all eligible probes; constituent probe sets differ by platform (v5:421).
- **Eligible probe:** one-to-one Entrez mapping that passes the feature rule; multi-mapped probes
  never used (v5:408).
- **Pipeline (v5:461–477):** probe-level fit (BH family 1), then build U, then a separate gene-level
  fit on U (BH family 2). Direction = sign(β_g) (v5:474).
- Lock fields: v5:509–521. Validation units: v5:543. Pathway input: v5:704.
- The plan states the evidence does not select an option (v5:446–452).

| Question | ASSESSMENT |
|---|---|
| Complete, internally consistent pipeline per option? | **G3: yes, for all four cohorts** (v5:421, 461–477, 543, 660). **G1: complete for one fitted model, but incompletely specified across models** — see "G1 issue" below. **G1b: complete for the Illumina cohorts only**; undefined for GSE99039 (v5:419, 661). **G2: not implementable**: resource unverified and no GPL570 rule (v5:420, 662) |
| Compatible quantities through discovery → lock → validation → pathways? | **Yes for the quantity used.** Each stage uses the gene-level fit on U (v5:468–474, 513, 611, 704). The probe-level family is kept separate (v5:475). Under G1/G1b/G2 the gene-level β_g equals the selected probe's probe-level effect, but q differs (v5:471–473). This is coherent |
| **G1 issue (TS)** | U's columns are "samples of the model being fitted" (v5:410), and G1 selects "over the samples of the model being fitted" (v5:418). So **the selected probe for a locked gene can change**: (i) between discovery sensitivity designs, because each sensitivity changes the sample set (v5:726–727 asks for "effects of the locked genes under the sensitivity" without saying whether the discovery selected probe is held fixed); and (ii) between the three GSE99039 contrasts (v5:650–652), which each have a different sample set. v5:523–524 guarantees that no *cohort* receives a different rule, but says nothing about within-cohort contrasts or sensitivities. This needs a precise rule: hold the discovery selection fixed for discovery sensitivities, and choose one selection set per validation or specificity cohort (e.g. the union of the cohort's contrast samples), or justify re-selection |
| GPL570 / GSE99039 | **Unresolved** (FACT v5:660–662; v5:147). G1 and G3 are defined. G1b has no disjoint set. G2 has no rule. The GPL570 annotation resource is unpinned (v5:540, D8). Sex probes are unidentified (v5:147) |
| Cross-platform mapping | FACT: one pinned release sharing an Entrez snapshot; Entrez-only match; retired IDs become "unmapped" (v5:540). ASSESSMENT: specified as a rule, but **whether separately versioned Illumina and Affymetrix annotation resources can share one Entrez snapshot is not verified in the project** (EV/D8). If they cannot, an approved ID-history procedure is needed (v5:540 allows this) |
| Evidence enough to recommend an option? | **No.** The options differ in **estimand** (G3: average probe signal; G1/G1b/G2: a selected probe; v5:443–444), in reliance on distributional assumptions (v5:437–442, 448–449) and in resource needs. No project evidence bears on which estimand the PI wants, how well probes are expressed in blood, or whether a G2 resource exists. **The choice genuinely requires PI approval.** Implementation ease is not a valid criterion and is not used here |

**RECOMMENDATION** (not a decision):

1. The PI first states the gene-level *target*: "a gene's best-measured probe" (G1/G1b/G2) or
   "average probe signal" (G3). That narrows D6 on scientific grounds.
2. Before any G2 approval, D8 must establish whether a probe-quality resource exists.
3. Whatever is chosen, the G1 selection-scope rule above must be fixed (TS).

### B. D7: model identifiability (v5 §4, lines 294–398)

**FACT.**

- Design N: intercept, standardized age, sex indicator, all unit indicators, sensitivity terms
  (v5:351–358).
- SVD with τ = max(n, p)·σ_max·ε on the scaled N (v5:326, 359–362).
- E = ‖g − Q_N Q_Nᵀ g‖² / ‖g − ḡ‖² = 1 − R²_g; estimable iff E > η = 10⁻⁸ (v5:324, 364–367).
- Minimum information: c₁, c₂, c₃ (VIF); all unset, as is their scope (v5:319–327, 369–370).
- Thresholds approved before any M-check; the informational run is withdrawn (v5:316–330).
- Decision vs descriptive checks (v5:344–347).
- Estimability vs adequacy table (v5:296–312).
- No revision after outputs (v5:394–395).
- §11 step 0 places D7 approval before QC (step 3) and identifiability (step 4) (v5:760–764).

| Question | ASSESSMENT |
|---|---|
| Is estimability tested correctly? | **Yes in exact arithmetic.** N contains the intercept, so ‖g − ḡ‖² is the correct total, and E > 0 ⇔ g ∉ span(N). The constant-g guard (v5:363) precedes the division. Numerically, the decision depends on r_N (via τ) and on η. Both are deterministic once fixed |
| Invariant to units and rescaling? | **Yes, effectively.** Standardizing continuous columns (v5:325, 353) makes the scaled N identical whatever the age units (years, months, decades). E depends only on span(N) given r_N, so any further rescaling of nuisance columns leaves it unchanged (v5:367 states this correctly). Residual dependence: σ_max (in τ) depends on the indicator columns and n, but these do not depend on units. Not a concern |
| Thresholds fixed before pass/fail checks? | **Yes as written** (v5:316–330, 760). Stage B QC tabulations "by chip/batch and by deposited diagnosis" (v5:270) happen *after* step 0, so they cannot inform threshold choice. If Stage B cross-tabulates chip × diagnosis, it reveals M1-type information before step 4. That is harmless only because the thresholds are already fixed; the plan relies on this ordering, which is stated |
| Estimability distinguished from adequate adjustment? | **Yes** (v5:296–312): "A PASS means only 'estimable with the approved minimum information'" (v5:312) |
| Could the procedure permit insufficient independent information? | **Possibly, depending on unset values.** (i) With unit fixed effects, the information about g comes from within-unit variation of g. 1/VIF = E is exactly the share of g's variance left after the nuisance terms, so **c₃ is the principal safeguard**, and its value is unset. (ii) **c₂ counts all samples of each group on mixed units** (v5:322). A mixed unit with 11 AD and 1 CTL contributes 11 AD samples but little contrast information. c₂ as defined can be satisfied by heavily unbalanced mixed units. A per-unit minority count (e.g. Σ_u min(n_AD,u, n_CTL,u)) would measure within-unit contrast information more directly; this is an option, not a correction. (iii) No minimum residual df is a decision criterion; M5 is descriptive (v5:347). (iv) "Independent information" also assumes independent errors within units after the fixed effect, and one array per participant (D18). E does not test these |

**RECOMMENDATION:**

- The PI sets c₁–c₃ and their scope (common vs cohort-specific) before any M-check.
- The PI also considers redefining c₂ as a within-unit minority count, and whether a minimum residual
  df should be a decision check.
- All of this must be fixed before §11 step 4.

### C. D20: replication score and multiplicity (v5 §7.4–7.7, lines 558–630; lock §6.2, lines 504–524)

**FACT.**

- **W1:** S = mean_{U_c} z − mean_{D_c} z (proposed). **W2:** gene-equal. One-directional forms are
  identical under both (v5:568–581).
- z is computed over all score samples, diagnosis-blind (v5:565–566).
- Test: one-sided p plus two-sided 95% CI (v5:583–586).
- Coverage rule (v5:590–600).
- Empty signature → no replication (v5:500).
- C-a: one-sided per gene, BH within cohort (v5:610–614).
- C-b: descriptive, no p-value (v5:615–620).
- Hierarchy C-c → C-a → C-b (v5:621).
- Separate one-sided α = 0.05 per cohort; Holm as the alternative (v5:623–628).
- The lock carries the weighting, standardization, coverage and mapping rules (v5:516–524).

| Question | ASSESSMENT |
|---|---|
| Formula complete for two-directional, one-directional and empty signatures? | **Yes.** Two-directional and one-directional cases are given for both conventions (v5:570–573). Empty signature → not run (v5:500). A two-directional lock losing a direction → not assessable (v5:596–598). Genes constant in a cohort are excluded before z (v5:551). No undefined case found |
| Comparable across cohorts with different coverage? | **Inference yes, magnitude no.** Each cohort's one-sided test is valid within that cohort. But the score's scale depends on (a) the number of measurable genes per direction and the inter-gene correlation, which set Var(S), and (b) z being standardized over a sample whose diagnosis mix differs by cohort, since the SD includes the group effect. **β̂ for S is therefore not comparable across cohorts.** v5 does not say this. Cross-cohort magnitude comparison should be declared descriptive, or a standardized score effect prespecified (TS) |
| Coverage rule coherent with the per-direction minimum? | **Yes.** min(5, locked) together with 50% is consistent, and "all required when fewer than 5 are locked" follows (v5:594–595). **Rule 1 is redundant:** if every non-empty direction has ≥ 50% measurable, the total does too (v5:592 vs 593–594). Harmless; noted for clarity |
| Complete hierarchy of per-gene tests, CIs, cohort score and multiplicity? | **Not quite (TS):** (i) **C-a has no declared threshold for "replicated"** (v5:610–614 gives the p-value and BH, but no q cut-off), yet it is called inferential. (ii) The C-c test is one-sided, but the CI is two-sided 95% (v5:585–586). The two can disagree at the margin (one-sided p < 0.05 with a two-sided CI that includes 0); a one-sided 95% lower bound would match the test. (iii) "Hierarchy" (v5:621) is an ordering of importance, not a gatekeeping procedure. Whether C-a claims are made when C-c fails is unstated. (iv) Cross-cohort: separate α per cohort is coherent given distinct roles (v5:625–627); Holm is the stated alternative. PI choice |
| Lock, weights and mapping unchanged across validation cohorts? | **Yes across cohorts** (v5:523–524). Per-cohort probe re-selection under G1 is a rule-based, reported difference in measurement (v5:543, 545), not a change to the lock. **Within-cohort variation under G1 (across contrasts or sensitivities)** is not covered (see A) |

**RECOMMENDATION:**

- **PI choices:** W1 vs W2, and cross-cohort multiplicity.
- **Targeted specification fixes:** a C-a threshold; a one-sided bound for C-c (or an explicit
  two-sided rationale); whether C-a is gated by C-c; a statement that score magnitudes are not
  comparable across cohorts.

### D. D13: neurodegenerative-disease specificity (v5 §8, lines 634–695)

**FACT.**

- All locked genes are used (v5:638).
- Separate contrasts; IPD vs CONTROL primary (v5:648–653).
- Covariates sex + batch, complete case (−35) (v5:655).
- Same locked score formula and weighting; the coverage rule applies (v5:664–669).
- Evidence categories with δ unavailable (v5:671–677).
- No specificity claim from significance contrasts (v5:681–683).
- No direct AD vs PD estimate (v5:684–685); effect scales not comparable (v5:687–693).
- The lock includes "the one-sided test direction" (v5:520).
- Active inherited v3 §3.4 lists a GSE99039 **age-adjusted sensitivity** (v3:167). GU has no age data
  at all (v3:169). The v3 D13 alternatives included the age-adjusted sensitivity (v3:653).

| Question | ASSESSMENT |
|---|---|
| Estimand and gene set clearly defined? | **Gene set: yes** (v5:638). **Estimand: implicit.** The per-gene estimand is the IPD − CONTROL difference conditional on sex and batch, among complete cases; it is not written as an estimand. **Score test direction is ambiguous (contradiction, TS):** §8.1 applies "the same locked formula" (v5:666), and the lock fixes a one-sided direction (v5:520, 585). A one-sided test in the AD direction cannot detect a PD association in the opposite direction, but the per-gene categories are two-sided (v5:675). The specificity score test needs its own prespecified sidedness |
| Missing age and sex, and separate genetic groups, consistent with the inference? | **Partly.** (i) Sex: complete case (v5:655); R8 is unavailable for GPL570 (v5:147), so recorded sex is unverified. (ii) **Age is not adjusted in any active specificity analysis.** v5 §10 lists S1–S14 as the full sensitivity set and says S1 is "Not applied to GSE99039" (v5:731). The age-adjusted GSE99039 sensitivity from v3 §3.4 (v3:167, still active per v5:74) appears neither in v5 §10 nor in v5 D13 (v5:854). Since age is a known determinant of blood expression and IPD/CONTROL age balance is unknown (age missing for 199/438; v3 §3.2), "association with PD" may partly reflect age. **This is an inconsistency between active texts** (§4 below). (iii) GPD and GU are kept separate (v5:651–652). Correct. The scientific purpose of GU vs CONTROL is not stated, and GU cannot be age-adjusted (v3:169) |
| Valid distinction between association, negligible association and inconclusive? | **Valid given δ is unset.** v5 reduces to two operative categories ("association" / "not demonstrated"), with equivalence unavailable (v5:675–677). The former "inconclusive" category is absorbed into "not demonstrated", which is correct while δ is unresolved. Minor: the "CI excludes 0" condition is implied by q < 0.05 for matching two-sided procedures (redundant, not wrong). Whether the PD direction relative to the locked AD direction is reported is not stated (TS) |
| Avoids reading non-significance as specificity? | **Yes, explicitly** (v5:681–683, 686) |

**RECOMMENDATION:**

- Targeted corrections (§4 below): state the specificity score test's sidedness; reinstate or
  explicitly drop the GSE99039 age-adjusted sensitivity.
- PI decisions: δ (with a scientific justification), coverage thresholds for GPL570, and the purpose
  of GU vs CONTROL.

### E. R8: sex-discordance check (v5 §3.2, lines 135–238)

**FACT.**

- Inputs (v5:137–147).
- A0–A5 (v5:151–202).
- Axis interpretation labelled "not externally validated" (v5:176–184).
- D_min unset; the check must not start before approval (v5:217–219).
- Options (a)/(b)/(c) if D_min cannot be justified (v5:221–234).
- R8 "unavailable" until decided; whether the primary analysis may proceed without R8 is open
  (v5:236–238).
- **Local sources:**
  - Phase 2C reports that the original authors removed arrays for an "XIST/recorded-gender
    discrepancy (1 AD, 1 control)", and in 2013 for "XIST and/or SNP-based gender mismatch", using
    ILMN_1764573 (2C v2:42–43). **No numeric threshold is reported there.**
  - Patel 2020 (PMC7175937.xml) reports "No. gender mismatches" = 2 for GSE63060 in Table 1. A text
    search found no XIST method or threshold.
  - The Lunnon 2013 PDF was **not re-read** in this review (no PDF text tool is installed; none was
    installed).

| Question | ASSESSMENT |
|---|---|
| Implementable as written | A0, A0b, A1, A2 (split, ties, degenerate axis), A3 (formula, +∞ rule), A4 mapping and A5 classification are deterministic once the constants are approved. **RL**, conditional on D5 |
| Thresholds implicitly treated as validated? | **No.** n_min = 5, the 10⁻¹² tie tolerance and ≥ 2 Y genes are labelled "[PROPOSED (no source)]" (v5:152, 164, 166). The axis interpretation is labelled not validated (v5:176–177). Option (b) explicitly names its weaker safeguard (v5:226–228). One caution: D = +∞ "counts as separating" (v5:174) is a convention, not a validated rule; it is listed |
| Defensible threshold source in the project? | **None found.** The local sources document *that* XIST-based checks were done, not *how* the boundary was set (FACT above). The Lunnon PDF was not re-read, so a threshold in its full text cannot be excluded; [2C] records none |
| What remains blocked | R8 Stage A for every cohort, until D5 (D_min or option a/b/c). For GSE140829, D19 as well. For GSE99039, identification of the GPL570 sex probes (D8/D6 annotation). S5d, S5e, S5f and the R8 part of S5g (v5:739–743). Whether the primary analysis may proceed without R8 (D22; v5:237–238) |

**RECOMMENDATION:**

- If the PI wants option (a), obtain and add to the project a source that reports separation of XIST
  or Y-gene expression on Illumina whole-blood arrays. Check the Lunnon PDF text for a reported
  boundary.
- Otherwise the PI chooses (b) or (c) explicitly. Choosing (c) leaves sex QC to the submitters'
  unauditable pre-deposit check, for GSE63060 only (v5:230–233).

### F. External dependencies (D0, D8, D19, GSE99039 sex probes)

| Dependency | What is missing | Why required | What it blocks |
|---|---|---|---|
| **D0** (v5:88, 841, 899) | The content of any Notion "Analysis Plan / Statistical & Validation Plan" (its existence is unknown), and authorization to read it (this review was not permitted to) | Prespecified hypotheses or thresholds in another plan could conflict with v5. Two protocols would undermine prespecification | **Protocol approval** (governance) for all confirmatory analyses. Not a computational dependency |
| **D8** (v5:90, 849, 905) | Authorization to install a pinned environment (R/Bioconductor with limma; annotation packages; gene-set resources) or an approved, validated alternative; exact versions | The candidate model (v5:397–398) and all annotation pins (v5:540) need software. Two software behaviours are unverified: the camera statistic (v5:705) and estimated-weight invariance (v5:379–380) | **Primary discovery** (model fit; annotation lock §11 step 1), signature lock, all validation and specificity, pathways, and S6/S9. Also D19 route (a) and the GPL570 annotation |
| **D19** (v5:75, 146, 544, 556, 860; v3 §7) | An approved ILMN↔nuID mapping: a mapping package (version), the GPL15988 platform table (network), or validated new code from the local GPL10558 sequences, plus evidence that GPL15988 shares those sequences | The GSE140829 Series Matrix uses nuIDs; probe presence cannot be inferred from the raw file (v3 §7.2) | **External replication in GSE140829** (C-c, C-a, C-b), R8 there, S13 and S14. **Not** discovery, GSE63061 consistency or specificity (v5:641) |
| **GSE99039 sex probes** (v5:147, 916–918) | A pinned GPL570 annotation identifying XIST and Y-gene probe sets, then a check of their presence in the Series Matrix | R8 requires probes verified present in the Series Matrix (v5:139) | **R8 in GSE99039 only.** Whether specificity may proceed without R8 is **not stated** in v5 (D22 covers only the primary analysis; v5:237) (TS). Shares the D8/D6 annotation dependency |
| D9 / D10 (v5:850–851) | Data-owner information | E1, S4 interpretation, D18 pairing, independence wording | E1 (not planned); the wording of GSE140829 claims. Not the E2 primary |

---

## Part 2 — Decision register (D0–D22)

Each entry gives:

- the current v5 proposal;
- the evidence;
- the assessment;
- the open options;
- the recommended next action;
- whether PI approval is needed;
- what is blocked;
- references;
- the class.

### D0 — Reconciliation with any other analysis plan · **EV**

- **Proposal:** provide the content for reconciliation (v5:841).
- **Evidence:** Notion not reviewed (v5:88). No other plan document exists (v5:89).
- **Assessment:** this is governance, not statistics. It cannot be assessed until the content is
  provided.
- **Options:** supply the Notion content; or the PI declares that none exists or that v5 supersedes
  it.
- **Next action:** the PI provides the content or a written statement.
- **PI approval:** yes.
- **Blocks:** approval of the confirmatory protocol.
- **Refs:** v5:88, 841, 899.

### D1 — Primary estimand · **PI**

- **Proposal:** E2 (deposited label) with the converter caveat (v5:96, 842).
- **Evidence:** [3A]; H1, ~41 likely converters (v5:96).
- **Assessment:** E2 is the only estimand supportable from deposited data. E1 is infeasible without
  D9.
- **Options:** approve E2; seek E1 through D9.
- **Next action:** PI approval of E2 wording.
- **PI approval:** yes.
- **Blocks:** all confirmatory analyses.
- **Refs:** v5:96, 309, 842.

### D2 — Eligibility and label rules · **RL** (PI approval pending)

- **Proposal:** R2-ID for all cohorts; R2-COV per analysis; R5 (v5:97, 843).
- **Evidence:** v3 §3 (active, v5:74); [P1] label tables.
- **Assessment:** deterministic rules; no open parameter.
- **Options:** as v5.
- **Next action:** PI approval.
- **PI approval:** yes.
- **Blocks:** every population definition.
- **Refs:** v5:74, 97, 843.

### D3 — GSE63060 expression input · **RL**

- **Proposal:** Series Matrix, no re-normalization (v5:844).
- **Evidence:** [2A] (full value equality with the normalized file).
- **Assessment:** sufficiently specified.
- **Options:** S10 alternative only.
- **Next action:** PI approval.
- **PI approval:** yes.
- **Blocks:** discovery.
- **Refs:** v5:844, 748.

### D4 — Age eligibility · **PI**

- **Proposal:** no restriction; S1(a) ≥ 65 and S1(b) 61–88 as sensitivities (v5:731, 845).
- **Evidence:** H2 (21 under-65 samples versus the papers' stated criterion).
- **Assessment:** the evidence conflicts. Note that the register lists D4 as depending on D7
  (v5:845); the logical dependency is the reverse (D7 checks run on the D4-defined population). Minor
  register inconsistency.
- **Options:** no restriction; ≥ 65 primary.
- **Next action:** PI decision; optionally D9.
- **PI approval:** yes.
- **Blocks:** discovery population.
- **Refs:** v5:731, 845.

### D5 — R8/R9 constants and D_min · **EV** (D_min) + **PI** (conventions)

- **Proposal:** n_min 5; tie tolerance 10⁻¹²; ≥ 2 Y genes; k = 3; ≥ 10 arrays; near-identical
  tolerance 1 − 10⁻⁸; **D_min unset**; options (a)/(b)/(c) (v5:112–121, 151–175, 221–234, 245–260,
  846).
- **Evidence:** no threshold source in the project (§E above).
- **Assessment:** R9 is fully specified once its conventions are approved. R8 is blocked by D_min.
- **Options:** (a) external source; (b) no-threshold variant; (c) no R8.
- **Next action:** locate a source or choose (b)/(c).
- **PI approval:** yes, before Stage A.
- **Blocks:** R8 everywhere; S5d–S5g (R8 parts); possibly the primary analysis (D22).
- **Refs:** v5:112–121, 135–260, 846.

### D6 — Gene-level unit and annotation · **PI** + **TS** + **EV** (G2)

- **Proposal:** none declared; G1/G1b/G2/G3 open; S8 = the alternative (v5:414–459, 847).
- **Evidence:** reasoning only (v5:423–452); no project evidence on probe performance in blood.
- **Assessment:** see Part 1A. The G1 selection scope across sensitivities and contrasts is
  underspecified (v5:410, 418, 726–727). G2 is not implementable. G1b is undefined for GSE99039.
- **Options:** G1, G1b, G2, G3 (and the S8 counterpart).
- **Next action:** the PI states the gene-level target; fix the G1 scope rule; D8 to establish G2
  feasibility.
- **PI approval:** yes.
- **Blocks:** the gene-level discovery fit, signature lock, validation units, pathways, and the
  cross-platform mapping rule (v5:540).
- **Refs:** v5:402–477, 509, 540–545, 658–662, 704, 746, 847.

### D7 — Identifiability thresholds and conventions · **PI**

- **Proposal:** the §4.4 procedure; η = 10⁻⁸; standardized scaling; τ; **c₁–c₃ and scope unset**
  (v5:319–327, 848).
- **Evidence:** no diagnosis × chip table in earlier reports (text search; v5:331–337).
- **Assessment:** the procedure is correct and unit-invariant. The safeguard strength depends on the
  unset c₃. c₂ as defined can be met by unbalanced mixed units (Part 1B).
- **Options:** values; common vs cohort-specific; c₂ redefinition; a residual-df criterion.
- **Next action:** the PI sets the values before any M-check.
- **PI approval:** yes.
- **Blocks:** §11 step 4 and therefore all model fitting.
- **Refs:** v5:294–398, 760–764, 848.

### D8 — Analysis environment · **PI** (authorization) with an external software dependency

- **Proposal:** pinned R/Bioconductor (v5:849).
- **Evidence:** R not installed (v5:90).
- **Assessment:** a prerequisite for nearly every computational step. Two software behaviours need
  verification (v5:379–380, 705).
- **Options:** R/Bioconductor; a validated alternative.
- **Next action:** PI authorization of installation and of the versions.
- **PI approval:** yes.
- **Blocks:** discovery onward (Part 1F).
- **Refs:** v5:90, 379–380, 397–398, 705, 849.

### D9 — Data-owner requests · **EV**

- **Proposal:** request the information (v5:850).
- **Evidence:** H1–H4, H9.
- **Assessment:** does not block E2.
- **Options:** request; proceed without.
- **Next action:** PI decides whether to contact the owners.
- **PI approval:** yes.
- **Blocks:** E1; the S4 interpretation; D18 pairing.
- **Refs:** v5:850.

### D10 — GSE140829 independence standard · **EV**

- **Proposal:** "independence unverified" (v5:532, 851).
- **Assessment:** affects claim wording only.
- **Next action:** obtain documentation (D9).
- **PI approval:** yes.
- **Blocks:** any "independent validation" claim.
- **Refs:** v5:532, 851.

### D11 — GSE140829 input · **PI**

- **Proposal:** Series Matrix + batch; ComBat file as S13 (v5:751, 852).
- **Assessment:** both inputs carry known risks.
- **Next action:** PI decision; implementation also needs D19.
- **PI approval:** yes.
- **Blocks:** GSE140829 replication.
- **Refs:** v5:751, 852.

### D12 — Replication criteria · **PI** + **TS**

- **Proposal:** C-c (v5:558–589), C-a (v5:610–614), C-b descriptive (v5:615–620, 853).
- **Assessment:** C-a lacks a "replicated" threshold. An inferential C-b remains unresolved.
- **Options:** a C-a threshold (e.g. a BH q cut-off, PI choice); approve P1–P3 or keep C-b
  descriptive.
- **Next action:** specify the C-a threshold; keep C-b descriptive unless a procedure is justified.
- **PI approval:** yes.
- **Blocks:** replication reporting (after the lock).
- **Refs:** v5:608–621, 853.

### D13 — Specificity · **PI** + **TS** + **EV** (δ)

- **Proposal:** all locked genes; IPD vs CONTROL with sex + batch; coverage rule applies; δ unset
  (v5:634–695, 854).
- **Evidence:** GSE99039 missingness (v3 §3.2, §3.4).
- **Assessment:** see Part 1D. The score sidedness is ambiguous. The age-adjusted sensitivity is
  orphaned. The purpose of GU is unstated.
- **Options:** δ basis; GPL570 coverage thresholds; replicated-genes-only as an additional analysis;
  sidedness.
- **Next action:** targeted correction (§4); the PI supplies a δ rationale or accepts "not
  demonstrated" only.
- **PI approval:** yes.
- **Blocks:** the specificity analysis.
- **Refs:** v5:520, 585, 634–695, 731, 854; v3:167, 169, 653.

### D14 — Pathways · **PI** + **EV** (resources)

- **Proposal:** camera-type primary; ORA secondary; universe = rows of U; same Entrez release
  (v5:699–715, 855).
- **Assessment:** internally consistent. The internal statistic is unverified (v5:705).
- **Options:** inter-gene correlation handling; collections.
- **Next action:** decide after D6/D8.
- **PI approval:** yes.
- **Blocks:** exploratory pathways only.
- **Refs:** v5:699–715, 855.

### D15 — FDR, cap, coverage · **PI**

- **Proposal:** q < 0.05; 200 unique genes; coverage 50% / min(5); no coverage restriction at
  selection (v5:485–494, 590–600, 856).
- **Assessment:** coherent; coverage rule 1 is redundant (Part 1C).
- **Options:** other values; restriction to validation-annotated genes.
- **Next action:** PI approval before the lock.
- **PI approval:** yes.
- **Blocks:** discovery claims (q level) and the signature lock.
- **Refs:** v5:483–502, 590–600, 856.

### D16 — Sensitivity set · **PI** + **TS**

- **Proposal:** S1–S14 with S5a–g (v5:719–752, 857).
- **Assessment:** the GSE99039 age-adjusted sensitivity is missing relative to the active v3 §3.4
  (v3:167). The G1 selection scope under sensitivity designs is undefined (v5:726–727).
- **Options:** add or omit the age-adjusted specificity sensitivity; the G1 scope rule.
- **Next action:** targeted correction; then PI approval **before any discovery result exists**
  (prespecification).
- **PI approval:** yes.
- **Blocks:** sensitivity reporting. Fixing the set before results guards against selective
  reporting.
- **Refs:** v5:719–752, 857.

### D17 — Expression filters · **PI** (RL once approved)

- **Proposal:** none in discovery or validation; S7 percentiles (v5:542, 745, 858).
- **Assessment:** deterministic.
- **Next action:** PI approval.
- **PI approval:** yes.
- **Blocks:** the eligible-probe definition (v5:408), hence discovery.
- **Refs:** v5:408, 542, 745, 858.

### D18 — Identity and GSE140829 replicates · **PI** + **EV** (pairing)

- **Proposal:** exclude "replicate 2" (option a); S14 if (c) (v5:752, 859).
- **Evidence:** v3 §3.3 (4 arrays; pairing unidentifiable).
- **Assessment:** affects GSE140829 only. The near-identical-pair review (v5:250) also falls under
  D18 for every cohort, and **its review procedure is not specified** (TS, minor).
- **Next action:** PI choice; D9 for pairing.
- **PI approval:** yes.
- **Blocks:** GSE140829 score samples, and the duplicate review in every cohort.
- **Refs:** v5:250, 752, 859.

### D19 — GSE140829 mapping · **EV**

- **Proposal:** an approved resource (v5:860).
- **Evidence:** v3 §7 (47,008 vs 47,231 rows; no nuID column locally).
- **Next action:** choose a route under D8.
- **PI approval:** yes.
- **Blocks:** all GSE140829 analyses (Part 1F).
- **Refs:** v5:75, 146, 544, 556, 860.

### D20 — Replication hierarchy, weighting, cross-cohort multiplicity · **PI** + **TS**

- **Proposal:** C-c > C-a > C-b; W1; separate α per cohort (v5:558–630, 861).
- **Assessment:** see Part 1C: CI sidedness; no gatekeeping; magnitudes not comparable across
  cohorts.
- **Options:** W1/W2; Holm; a gatekeeping rule.
- **Next action:** PI choice before the lock; targeted spec fixes.
- **PI approval:** yes, before the lock.
- **Blocks:** the signature lock (the scoring rule is part of it, v5:516–521).
- **Refs:** v5:516–521, 558–630, 861.

### D21 — Cell composition (S11) · **EV** / **PI**

- **Proposal:** none (v5:749, 862).
- **Assessment:** optional sensitivity only.
- **Next action:** defer.
- **PI approval:** yes, if S11 is run.
- **Blocks:** S11 only.
- **Refs:** v5:749, 862.

### D22 — QC policies and review scope · **PI**

- **Proposal:** §3.5 policies; approval limited to rule verification (v5:123–129, 275–290, 863).
- **Assessment:** coherent and outcome-independent as specified. Open: the ambiguous-sex policy;
  whether the primary analysis may proceed without R8 (v5:237–238); **whether specificity may proceed
  without R8** (not addressed; TS).
- **Next action:** PI decisions before Stage A.
- **PI approval:** yes.
- **Blocks:** QC Stage A, hence discovery.
- **Refs:** v5:123–129, 236–238, 275–290, 863.

---

## Part 3 — Prioritization

### 3.1 Smallest set to settle before the first confirmatory discovery analysis (v5 §11 steps 0–5)

| Decision | What must be settled |
|---|---|
| D1 | Estimand E2 |
| D2 | Eligibility rules |
| D3 | Input |
| D4 | Age rule |
| D5 + D22 | R9 constants and role; for R8, either D_min **or** option (b)/(c) **and** whether the primary analysis may proceed without R8 |
| D7 | c₁–c₃, scope, conventions |
| D8 | Environment authorization |
| D17 | Discovery feature rule (defines eligible probes) |
| D15 | Discovery q level (the cap and coverage can wait until the lock) |
| D6 | Gene-level unit, including the G1 scope rule if G1 is chosen. Needed because §5.4 runs the gene-level fit in the same step (v5:765). The probe-level family alone would need only D3/D8 and the annotation pin |
| D18 | The R2-ID and near-identical-pair review procedure (applies to GSE63060) |
| D16 | The sensitivity set must be **fixed** before any discovery result exists, although the sensitivity analyses can run later |
| D0 | Governance: reconciliation before protocol approval |

### 3.2 Can wait until signature lock, external validation or specificity

- Before the lock: D20 (weighting, hierarchy, multiplicity); D12 (C-a threshold); D15 (cap,
  coverage).
- Before validation: D10, D11 and D19 (GSE140829 only); D9 (wording).
- Before specificity: D13 (δ, sidedness, coverage for GPL570, GU purpose); the GSE99039 sex-probe
  annotation; whether specificity may proceed without R8 (D22).
- Before pathways (exploratory): D14.

### 3.3 Concern optional sensitivity analyses only

| Decision | Sensitivity |
|---|---|
| D21 | S11 |
| D4 (S1 variants) | S1 |
| D5 | k = 2.5 / 4 (S5b, S5c) |
| D6 S8 alternative | S8 |
| S6 | Estimated-weight invariance check |
| D17 | S7 percentiles |
| D3 | S10 |
| D11 | S13 |
| D18 (option c) | S14 |
| — | S3 (site), S4 (code letters), S12 (Sood subset), S9 (annotation comparison) |

### 3.4 Apparent contradictions or gaps needing a targeted v5 correction before approval

| # | Issue | Evidence (FACT) | Why it matters (ASSESSMENT) |
|---|---|---|---|
| T1 | **Specificity score sidedness** | §8.1 applies "the same locked formula" (v5:666). The lock fixes "the one-sided test direction" (v5:520). §7.4 is one-sided > 0 (v5:585). The per-gene categories are two-sided (v5:675) | A one-sided AD-direction test cannot detect an opposite-direction PD association. The sidedness of the specificity score test is undefined |
| T2 | **GSE99039 age-adjusted sensitivity orphaned** | Active v3 §3.4 lists it (v3:167); v5:74 keeps v3 §3 active. v5 §10 (v5:729–752) and D13 (v5:854) omit it. v5 §15 item 2 still asks for the "union of missing age or sex" (v5:913–914) | Either reinstate it in §10 or explicitly withdraw it. As written, the active texts disagree, and PD associations are never age-adjusted |
| T3 | **G1 selection scope** across sensitivity designs and GSE99039 contrasts | v5:410, 418, 650–652, 726–727 | The locked gene's measured probe may change silently within a cohort |
| T4 | **C-a has no replication threshold** | v5:610–614 | An inferential criterion with no decision rule |
| T5 | **C-c CI sidedness** | v5:585–586 | A two-sided CI can disagree with the one-sided test |
| T6 | Whether **specificity (and validation) may proceed without R8** | v5:236–238 covers only the primary analysis; v5:147 (GSE99039 unresolved) | Undefined behaviour for GSE99039 and, before D19, GSE140829 |
| T7 | Score magnitude comparability across cohorts not stated | v5:565–566, 583–586 | Prevents an implied cross-cohort magnitude comparison |
| T8 | Minor: D4 "depends on D7" | v5:845 | The dependency appears reversed |
| T9 | Minor: coverage rule 1 redundant | v5:592–594 | Clarity only |
| T10 | Minor: near-identical-pair (D18) review procedure unspecified | v5:250 | Needed for discovery-cohort identity checks |

---

## Part 4 — Limitations of this review

| Limitation | Detail |
|---|---|
| Lunnon 2013 PDF not re-read | No PDF text-extraction tool is available, and none was installed. The statement that no threshold source exists rests on the [2C] summary and a text search of the Patel 2020 XML |
| Software behaviour | The camera statistic and estimated-weight invariance cannot be checked without D8 |
| Notion | Not read (D0) |
| Prior exposure to diagnosis × chip information | Still rests on the v5 text search (v5:331–337). This review did not compute any table |
| Assessments | Statistical reasoning, not externally validated |
