# BIO-MB-001 Phase 3B — Scientific consistency audit of SAP draft v4 (read-only)

**Audited file:** `reports/phase3b/v4/STATISTICAL_ANALYSIS_PLAN_DRAFT.md`
(SHA-256 `c4588e5ebca9f36984ea34733ad91cb8b47bfaa7c63c63bdb6871c8fa03a647d`).

v4 states that it carries over all non-revised sections of v3 unchanged (v4 lines 7–16). The v3 text
that v4 leaves in force was therefore also audited:
`reports/phase3b/v3/STATISTICAL_ANALYSIS_PLAN_DRAFT.md` (SHA-256 `86c3a0a1…af97f`) §4, §5, §6, §8,
§9, with v2 where v3 defers to it.

**Scope and constraints:**

- This is an audit of text and reasoning only.
- Nothing was executed: no expression data, QC statistic, model, gene list or association result was
  read or computed.
- No D0–D22 decision is settled here, and the approval-gate status is not changed (still: G1, G2,
  G5, G7, G8 not satisfied; G3, G4, G6, G9 partial).
- No file other than this report was created or modified.

**Conventions:**

- **[DOC]** = what the document says, with line references: `v4:L` and `v3:L`.
- **[ASSESSMENT]** = the auditor's methodological judgement. These are statistical reasoning, not
  externally validated findings, and no citation is added.
- **[NOT VERIFIABLE HERE]** = could not be checked with local text and reasoning alone.

**Severity:**

- **Blocker:** prevents a deterministic or valid implementation, or creates a post-result choice.
- **Major:** a substantive inconsistency or incorrect reasoning that should be revised before approval.
- **Minor:** wording or completeness.

**Readiness classes (as requested):**

- **A:** deterministic and implementable as written. It still needs the SAP as a whole to be
  approved, but has no open parameter.
- **B:** implementable only after an explicit scientific approval of an open value or choice.
- **C:** mathematically or statistically underspecified, or internally inconsistent; needs revision.
- **D:** dependent on external information or software approval.

---

## 1. Summary of highest-priority blockers

| # | Blocker | Location | Class |
|---|---|---|---|
| B1 | **The R8 sex check cannot run, and its threshold could be set after viewing D.** The minimum separation D is unresolved (v4:84–88). The text also says "D is reported" while no value is approved, which would allow D to be computed before D_min is fixed. That conflicts with the v3 rule that Stage A parameters are fixed before Stage A (v3:191–192) | v4 §1.2 | B + C |
| B2 | **Thresholds for identifiability (c₁–c₃) could be set after viewing metadata outcomes.** c₁–c₃ are unresolved (v4:241–242). v3 schedules an "informational" M1–M8 run before QC (v3:369), with no requirement that c₁–c₃ be fixed first. The PI could then set thresholds knowing whether the study passes | v4 §3 step 4; v3 §5.2 | B + C |
| B3 | **The gene-level pipeline is incoherent for G3, the option v4 leans towards.** v4 replaces only v3 §6.1 step 5 and §6.2 rows 2–3 (v4:273). Text still in force says "each Entrez gene takes the statistics of its representative probe from step 6" (v3:428); takes direction from "the representative probe" (v3:454); locks "representative probe and its gene-level statistics" (v3:464); and uses a "representative probe" statistic for pathways (v3:445). Under G3 there is no representative probe | v4 §4.3 vs v3 §6.1–6.3 | C |
| B4 | **Errors in the independence reasoning that underpins D6** (§4 below). The heteroscedasticity condition is stated incorrectly; the "larger group" bias claim is imprecise; assumption (d) is stronger than needed. The D6 comparison therefore rests partly on incorrect statements | v4:291–312 | C |
| B5 | **The estimability tolerance depends on covariate scaling** (§3 below). The procedure claims order independence but is not scale-invariant, and its "equivalently" claim holds only in exact arithmetic | v4:218–233 | C |
| B6 | **Rules that could silently alter the effective signature between cohorts.** Validation-cohort feature QC, the annotation release linking Entrez IDs across platforms, and multi-mapped validation probes are undefined (§5 below) | v4 §5.1; v3 §6.4 | C (+ D) |
| B7 | **Which genes enter specificity, and whether the score-coverage rule applies to GSE99039, are inconsistent or undefined.** v3 says "each locked AD-signature gene" (v3:573); v2 §10.2 is headed "per locked, *replicated* gene" | v3 §8.1; v2 §10.2; v4 §5.4 | C |
| B8 | **External dependencies.** GSE140829 probe mapping (D19); R/Bioconductor environment (D8); GPL570 sex probes for GSE99039 (unresolved, v3 §3.4); Notion plan (D0) | — | D |

---

## 2. R8 sex check (review item 1)

### 2.1 Determinism audit

| Element | [DOC] | [ASSESSMENT] | Class |
|---|---|---|---|
| Ordering and admissible splits | Strict inequality between adjacent values; n_low, n_high ≥ n_min = 5 (v4:58–63) | Deterministic. Tied values cannot be split. A | A (n_min proposed → approval) |
| Objective and ties in W | Minimize W(s); candidates within 10⁻¹²·W_total of the minimum are tied; smallest s wins (v4:64–69) | Deterministic given a computed minimum. **The claim that the tolerance "makes the choice independent of floating-point summation order" (v4:68–69) is overstated.** A candidate lying at the tolerance boundary can still flip between implementations. The risk is negligible in practice, but the sentence should say "reduces", not "makes independent". Minor | A (wording) |
| Threshold | t = midpoint of adjacent distinct values; no value equals t (v4:70–71) | Correct and deterministic | A |
| **Mapping from high/low to female/male type** | v4 states only "High = v > t; low = v < t" (v4:71). The mapping "X-call female-type if X_i > t_X; Y-call male-type if Y_i > t_Y" was in v3 A2 (v3:227–228), **which v4 replaces** (v4:48) | **The active text no longer defines which side is female or male.** The intent is obvious, but the specification is formally incomplete. Major (easy fix) | C |
| Degenerate axis | < 2 distinct values; no admissible split; W_total = 0 (v4:72–75) | Deterministic. "W_total = 0" is subsumed by "< 2 distinct values"; the parenthetical example "all but fewer than n_min values tied" is hard to parse. The rule itself ("no admissible split") is sufficient. Minor | A |
| Separation measure D | Formula (v4:79); +∞ if both SDs are 0 and means differ; undefined → non-separating | (i) The **SD denominator (n or n−1) is not stated.** (ii) A "perfectly separated" axis is "listed" (v4:81–82), but it is not stated whether it **counts as separating**. Since +∞ ≥ any D_min, it would, but the "artefact possible" note leaves the handling open. Minor | C (minor) |
| Minimum D | Unresolved; R8 cannot execute (v4:84–88) | Correctly not invented. But see blocker B1: "D is reported" implies Stage A may compute D before D_min is approved. To stay outcome-blind *with respect to the QC threshold itself*, D_min must be approved before any D is computed | B; C (sequencing) |
| Per-array non-finite handling | v4: non-finite on an axis → "unassessable on this axis" (v4:55–56). v3 A0 (kept unchanged per v4:48): non-finite XIST, or all Y probes non-finite → array **unassessable** (v3:218–219) | **Conflict.** Under v4, an array with non-finite XIST could still receive a Y-only call; under v3 A0 it is wholly unassessable. Must be reconciled. Major | C |
| Meaning of "usable axis" | Table rows "X only / Y only" (v4:97–98) | Two mechanisms can produce a single axis: (a) the cohort-level axis is non-separating or degenerate; (b) a per-array non-finite value. v4 does not say which one(s) "usable" refers to. Combined with the conflict above, single-axis classification is not fully deterministic | C |
| Evidence grading | Single-axis is never pooled with two-axis (v4:101–102); single-axis discordance only in sensitivity S5 (v4:116) | Consistent with the requested principle. Consequence (not stated): if one axis is non-separating cohort-wide, **no R8 primary exclusion is possible in that cohort.** Acceptable, but it should be explicit | A |
| Ambiguous handling | Option chosen beforehand under D22 (v4:117) | Requires approval | B |
| Discordance ≠ misidentification | v4:120–131 | Clear and adequate. Labelled REASONING and BACKGROUND appropriately | A |

### 2.2 Scientifically unsupported or approval-dependent elements of R8

- **[DOC]** These are labelled PROPOSED (no source): n_min = 5; the 10⁻¹² tie tolerance; ≥ 2 Y genes
  (v3:216). **[ASSESSMENT]** They are conventions requiring approval (B), not scientifically
  supported values.
- D_min: unresolved (B), correctly flagged.
- **[ASSESSMENT]** A per-axis two-class split (Otsu-type) assumes the two sexes form the two modes of
  each axis. With very unequal sex ratios or loss-of-Y in older men (v4:104–107, labelled
  BACKGROUND), the within-class-variance minimizer can place the threshold inside a mode. The D check
  partly guards against this, but only once D_min exists. This is a limitation, not an error.
- **Platform availability:** GSE140829 requires the D19 mapping (v3 §7); GSE99039 GPL570 sex-probe
  identifiers are unresolved (v3 §3.4). → D.

---

## 3. R9 outlier check (review item 2)

| Element | [DOC] | [ASSESSMENT] | Class |
|---|---|---|---|
| Flag formula | z_i < M − k·S, one-sided, k = 3 provisional (v3:298–299; v4:139–144) | Internally consistent with the MAD definition (v4:146) | A (k proposed → B) |
| Zero or non-finite MAD | Not applicable; no flags; no substitute estimator (v4:146–151; v3:295–297) | Consistent and explicit | A |
| Numerical-failure classes | zero variance; non-finite m_i; \|m_i\| ≥ 1; > half of pairs omitted (v4:153–154) | Consistent with v3 A0/A1/A3 | A |
| Minimum sample requirement | ≥ 10 arrays checked at A0 (v3:278) | **The check is applied only at A0.** Arrays later removed at A1 (omitted pairs) or A3 (\|m_i\| ≥ 1) can reduce the count below 10 before A4, and no re-check is specified. Minor | C (minor) |
| Role (iii) vs numerical-failure exclusion | "The primary population then does not depend on R9 at all" (v4:183); numerical-failure arrays proposed "exclude, listed" from the primary analysis (v4:194–195; v4:498) | **Internal tension.** Numerical-failure status is computed inside R9 Stage A, so the primary population *does* depend on R9 outputs for that class. The dependence is technical and diagnosis-independent, but v4:183 should be qualified. Minor | C (wording) |
| Sensitivity S5 definition | v2 S5: "Include R8/R9-flagged arrays; k = 2.5 and 4" (v2:376), which presumes primary exclusion. v3:623–624 adds k-variants. v4 (iii): primary *includes* R9 flags; S5 "shows influence" by excluding them (v4:179); single-axis R8 discordance excluded "only in sensitivity S5" (v4:116) | **S5 is now undefined.** Its direction is reversed relative to v2, and it bundles R9 exclusion at k ∈ {2.5, 3, 4}, single-axis R8 exclusion and possibly ambiguous-sex exclusion. It is not stated whether these are separate sensitivity runs or one combined run. Major | C |
| Batch structure | v4 §2.2 (v4:156–171) | Adequately described. **[ASSESSMENT]** Two further interpretive consequences: (1) under (iii), if flags are chip-concentrated, S5 removes chips, so S5 conflates "outlier removal" with "chip removal"; (2) removing whole chips can make the S5 design non-estimable or change the mixed-chip information. v3:629–630 handles non-estimability ("reported as not estimable") but not reduced information (c₁–c₃ applied to sensitivity designs?). Unspecified | C (minor) |
| Choice of role before Stage A | v4:201–202 | Consistent with the outcome-blind principle | B (D22) |

**[ASSESSMENT] Overall:** the R9 formula, the MAD behaviour and the role are internally consistent.
The S5 definition and the minimum-count re-check need revision. Batch structure can distort
interpretation of both the flags and S5, which v4 acknowledges only for the flags.

---

## 4. D7 model identifiability (review item 3)

### 4.1 Is estimability tested correctly?

- **[DOC]** g̃ = g − Q_N Q_Nᵀ g; estimable iff ‖g̃‖ > τ_g; "equivalently" rank([N, g]) = r_N + 1
  (v4:228–233).
- **[ASSESSMENT]**
  - **Exact arithmetic: correct.** The AD–CTL coefficient is estimable if and only if g ∉ span(N),
    i.e. g̃ ≠ 0.
  - **Numerically, three issues (blocker B5):**
    1. **Scale dependence.** τ = max(n, p)·σ_max·ε (v4:218–219) scales with the largest singular
       value. That value is dominated by the column with the largest magnitude: age in years, values
       around 50–100. Rescaling age (years vs decades) changes τ, and can change r_N for nearly
       collinear nuisance columns. The procedure is order-invariant (as claimed) but **not
       scale-invariant**. Standardizing non-indicator columns before the SVD, or using a relative
       criterion, would remove this.
    2. **The two criteria are not equivalent numerically.** ‖g̃‖ compared with τ_g (a tolerance
       built from the singular values of [N, g]) is a different test from counting the singular
       values of [N, g] above τ_g. They can disagree near the boundary. One criterion should be
       designated.
    3. **The relative criterion is already available.** ‖g̃‖² / ‖g − ḡ‖² = 1 − R²_g, a
       scale-free quantity. Estimability could be declared via 1 − R²_g > a stated small constant,
       which links directly to VIF_g (step 4).
  - **Guard missing:** if all samples are in one group, ‖g − ḡ‖ = 0 and R²_g is undefined (0/0).
    The order of step 2 (compute R²) and the estimability test should handle this. Minor.
  - **Method inconsistency:** v3 M3 specifies QR with a stated tolerance (v3:359), v4 specifies SVD.
    One method must be chosen. Minor.

### 4.2 Verification of the redundant-nuisance claim

- **[DOC]** The group coefficient, its SE, the residuals and the residual df n − r_N − 1 depend on N
  only through span(N), and hold for WLS with fixed weights (v4:249–258).
- **[ASSESSMENT] Correct for ordinary and fixed-weight least squares, given estimability.** By the
  Frisch–Waugh–Lovell result, β̂_g = g̃ᵀy / g̃ᵀg̃, where g̃ is the residual of g after projection onto
  span(N). This depends only on the projector onto span(N), not on the basis. The residuals equal
  (I − P_[N,g])y, which is also basis-free, and the df follow.

  For the moderated statistics, the residual variance and df are the inputs and are invariant, so the
  moderated t for the group coefficient is invariant too, given a fixed prior.

  **[NOT VERIFIABLE HERE]** Whether *estimated* array weights (S6, `arrayWeights`) are invariant to
  the basis depends on the software's estimation procedure. v4 restricts the claim to "fixed weights",
  which is appropriate, but S6 uses estimated weights.
- **[ASSESSMENT]** "Drop redundant terms" and "fit on [Q_N, g]" are interchangeable only for the
  group coefficient. v4 correctly limits reporting to it (v4:259–260).

### 4.3 Mathematically estimable ≠ scientifically adequate

**[ASSESSMENT]** Estimability (steps 1–3) guarantees only that a unique least-squares group
coefficient exists. It does **not** establish:

- **adequate information:** the c₁–c₃ thresholds address this but are unresolved (B);
- **absence of confounding by chip-level or site-level factors:** a chip fixed effect removes only
  chip-shared effects;
- **correct functional form:** linear age;
- **absence of unmeasured confounding:** cell composition, RIN, medication, APOE — v2 §7.4
  limitations;
- **that the coefficient targets the intended estimand:** it estimates the E2 deposited-label
  difference, including H1, ~41 likely converters among "AD";
- **robustness to submitter QC and normalization history:** H5, H8.

v4 does not state this distinction explicitly in §3. It should, so that a PASS from steps 1–4 is not
read as "model adequate".

### 4.4 Gaps from replacing v3 §5.3 wholesale

- **[DOC]** v4 §3 "replaces [v3 §5.3]" (v4:206).
- **[ASSESSMENT]** Three rows and rules of v3 §5.3 are no longer stated in active text:
  - the instruction to *fit chip as a fixed effect when checks pass* (v3:382);
  - singleton-chip handling (v3:384);
  - "No response is chosen or revised after expression results exist" (v3:389).

  The intent survives elsewhere, but the active specification is incomplete. Minor to major,
  because the last rule is a safeguard.
- **Cohort-specific thresholds:** whether c₁–c₃ are common across cohorts of different sizes and with
  batch rather than chip structure (GSE140829: 19 batches; GSE99039: 37) is unspecified. B.
- **Circularity (blocker B2):** see §1.

---

## 5. D6 representative probe and gene-level inference (review item 4)

### 5.1 Audit of v4's independence argument (v4:281–316)

| Statement | [DOC] | [ASSESSMENT] |
|---|---|---|
| Overall mean is uncorrelated with non-intercept coefficients | v4:285–289 | **Correct** when the intercept is in the column space: (XᵀX)⁻¹Xᵀ1 = e_intercept |
| Independence under (a)–(d) | v4:291–299 | **Correct in conclusion, but (d) is stronger than needed.** Assume Gaussian rows, independent across samples, with a common across-probe covariance. Then the projections of the data onto span(1) and onto span(g̃) plus the residual space are independent, *whatever the mean structure*. So the vector of probe means is independent of each probe's (β̂_g, s²) even when other probes of the gene are associated. Selection then leaves the selected probe's null distribution unchanged whenever **that probe's** coefficient is 0; (d) is not required for validity. (d) matters for interpreting *which* hypothesis was tested, not for the independence |
| Heteroscedasticity row | "Cov(ȳ, contrast) ≠ 0 when n_AD ≠ n_CTL (145 vs 104)" (v4:308) | **Incorrect condition.** With group variances σ²_AD and σ²_CTL and no covariates, Cov(ȳ, ȳ_AD − ȳ_CTL) = (σ²_AD − σ²_CTL)/n. This is non-zero whenever the variances differ, **regardless of group sizes**, and zero whenever they are equal, regardless of sizes. Unequal sizes are neither necessary nor sufficient. Major (it misstates when G1 fails) |
| Bias "under the alternative" | "a probe up-regulated in the larger group has a higher overall mean, so selection leans towards probes that rise in AD (the larger group)" (v4:312) | **Imprecise.** E[ȳ_j] includes (n_AD/n)·β_j for *any* group sizes, so the dependence on the true effect exists even with balanced groups. Whether it "favours AD-up probes" depends on what the comparison holds fixed. Correct statement: the overall mean depends on the probe's true group effect (weighted by the AD proportion), so the *probability of being selected* depends on the effect parameters, not on noise. This affects which probe represents an associated gene (representation bias, power); it does not affect null validity. Major (the reasoning feeds D6) |
| Moderated-statistics caveat | v4:310 | Reasonable as stated; correctly not claimed exact |
| Gene-level hypothesis wording | "The representative probe is not associated with group" (v4:314–316) | Correct and important. Under G1/G1b/G2 the tested hypothesis is data-selected (G1, G1b) or rule-selected (G2) per gene; claims must be phrased per representative probe |

### 5.2 Comparison of G1, G1b, G2, G3 as defined in v4

| Option | Definition as written | Compatible with gene-level inferential claims? | Compatible with downstream replication, specificity and pathways? | Issues | Class |
|---|---|---|---|---|---|
| **G1** | Highest mean across samples in the model; ties → probe ID (v4:322) | Yes, conditionally (equal variance across groups; Gaussian; see the corrections in §5.1). Claim unit = representative probe | Validation re-selects per cohort (v3:486–487), so the same gene may be measured by different probes across cohorts. Acceptable only if reported. Pathways: consistent | Correct the §5.1 errors; require reporting of the probe actually used per cohort | A (as rule); B (choice) |
| **G1b** | Highest mean across arrays not in the contrast, "GSE63060 MCI, n = 80" (v4:323) | Selection data disjoint from test data, so independence holds under sample independence. The weak link via joint normalization and shared chips is acknowledged | **Underspecified for every other cohort.** "Each cohort applies the same rule to its own data" (v4:339–340) is undefined where the disjoint set differs (GSE63061 MCI; GSE140829 MCI; GSE99039 other diagnoses). Also undefined: whether the MCI arrays are subject to R-rules and QC before use, and whether R2-COV applies | As stated | C |
| **G2** | Annotation-only rule, e.g. quality grade then probe ID (v4:324) | Fully independent of the data | "Identical probe for G2" (v4:340) applies to Illumina–Illumina pairs only. **GPL570 (GSE99039) has neither Illumina IDs nor the same grading, so the rule is undefined for the specificity cohort.** Resource availability unverified | — | D (+ C for GPL570) |
| **G3** | Per-sample mean of all one-to-one probes, then model the summary (v4:325) | Yes. **[ASSESSMENT]** Because the model is linear, the G3 group coefficient equals the average of the probe-level coefficients; probes with opposite effects cancel. The claim unit is "average probe signal" (v4 says so) | **Inherited text is inconsistent (blocker B3):** v3:428, v3:445, v3:454, v3:464 refer to "representative probe". Also, the probe set averaged differs by platform (v3 vs v4 Illumina; GPL570 probe sets), so the gene-level quantity is not the same measurement across cohorts. Replication compares *different probe averages*, which v4 does not mention. Also v2 S8(a) "mean of all mapped probes" is G3 (v2:379); adopting G3 as primary requires redefining S8 | — | C (text); B (choice) |
| G4 | Noted only | — | Correctly noted as unable to supply a direction | — | — |

**[ASSESSMENT]** v4 correctly declines to declare a default valid (v4:333–335). The "leaning G3" is
labelled unapproved. No D6 decision is settled by this audit.

---

## 6. Replication: D12, D15, D20 (review item 5)

### 6.1 Score formulas and one-directional signatures

| Element | [DOC] | [ASSESSMENT] | Class |
|---|---|---|---|
| Two-directional score | S_i = mean_{U_c} z − mean_{D_c} z (v4:373) | Well defined when U_c and D_c are non-empty (guaranteed by the coverage rule) | A |
| One-directional scores | Up-only: mean_{U_c} z; down-only: −mean_{D_c} z (v4:374–375) | Well defined; signs consistent with a one-sided test of > 0 | A |
| **Weighting statement** | "All measurable genes are weighted equally" (v4:377) | **False for the two-directional formula** unless \|U_c\| = \|D_c\|: each up gene has weight 1/\|U_c\| and each down gene 1/\|D_c\|. A direction with 5 measurable genes carries the same total weight as one with 150. Either the sentence or the formula must change. Which weighting is intended is a scientific choice. Major | C, then B |
| Standardization | z over all score samples, n − 1 denominator (v4:365–367) | Diagnosis-blind and deterministic. Centring and scaling are per-gene constants, so they do not bias the group contrast under the null | A |
| "Constant in cohort" | SD = 0 or non-finite (v4:357–358) | Deterministic; avoids division by zero | A |
| Test | S ~ group + covariates; one-sided > 0; 95% CI (v4:379–380) | Consistent. Since the test is one-sided, the CI type (two-sided 95% vs one-sided) should be stated. Minor | A (minor) |

### 6.2 Unmappable genes, cohort-specific missingness and coverage

- **[DOC]** Categories: unmapped; absent from the Series Matrix; excluded by approved feature QC;
  measurable; constant (v4:351–358). Unmeasurable genes are dropped, not imputed or replaced
  (v4:378). Coverage rule: ≥ 50% overall; per direction ≥ 50% and ≥ min(5, locked); no silent
  conversion to a one-directional score (v4:384–391). Values flagged as conventions (v4:395–396).
- **[ASSESSMENT]**
  - The coverage rule is internally consistent. Rule 3 follows from rule 2. For small locked
    directions, min(5, locked) together with 50% effectively requires every gene when fewer than 5
    are locked; that is acceptable but should be stated. Values: B.
  - **Cohort-specific sample missingness** enters through the "score samples" defined by R2-COV
    (v4:360–361). Coherent.
  - **GSE140829:** until D19 is resolved every locked gene is unmapped, so the score is "not
    assessable". v4 does not say this explicitly, but it follows from v3:562–565. D.

### 6.3 Per-gene tests (C-a) and multiplicity

- **[DOC]** v4 does not restate C-a. v3: one-sided per gene in the locked direction; BH across the
  tested locked genes (v3:500). v4 hierarchy: C-c primary, C-a secondary (v4:458).
- **[ASSESSMENT]**
  - Within a cohort this is coherent.
  - **Across cohorts**, the family structure is unstated. C-c is tested in GSE140829 (replication) and
    GSE63061 (consistency). Is each tested at one-sided α = 0.05 separately, with distinct claims?
    v2 §9.1 implies separate claims, but no statement fixes it. B.
  - C-a "proportion replicating" with a binomial CI is labelled descriptive (v2 §9.4). That is
    consistent with the same independence concern that downgraded C-b.

### 6.4 Rules that could silently change the effective locked signature between cohorts

| Risk | Where | [ASSESSMENT] |
|---|---|---|
| Validation-cohort feature QC | Category "excluded by approved feature QC" (v4:354) | **No validation feature rule is defined anywhere** (D17 concerns discovery filtering). If a filter is chosen after validation data are loaded, the measurable set changes post hoc. It must be prespecified per cohort, or declared "none". C |
| Annotation release linking Entrez IDs | Lock records the discovery annotation (v3:465); validation uses "that platform's pinned annotation" (v3:485) | If the platforms' resources use different Entrez snapshots, retired or merged IDs move genes into "unmapped" without any visible decision. All platforms should be pinned to one release, or a documented ID-history mapping used. C/D |
| Multi-mapped probes in validation | Discovery excludes multi-mapped probes (v3:443) | **Not stated for validation.** Allowing them in one cohort and not another changes what measures a gene. C |
| Per-cohort probe re-selection (G1) and the S8b fallback | v3:486–490 | The gene list stays fixed but the probe changes. This is not a change in the lock, but it must be reported per gene and cohort (not currently required). C (minor) |
| GSE140829 "replicate 2" handling | D18 | Changes the score samples, not the signature. Prespecified as option (a)/(c). B |

**[ASSESSMENT]** No rule *explicitly* modifies the locked gene list (v4:350, 406). The risks above
alter what is effectively measured, without a documented decision.

---

## 7. C-b — descriptive status throughout? (review item 6)

| Location | [DOC] | Consistent with "descriptive only"? |
|---|---|---|
| v4 §6.4 (v4:452–459) | Descriptive; no confirmatory p; hierarchy C-c > C-a > C-b descriptive | Yes |
| v4 register D12, D20 (v4:494, v4:497) | "C-b descriptive"; inferential only after D12 approval | Yes |
| v4 §9.3 (v4:530) | A valid confirmatory test is unresolved | Yes |
| **v3 §6.5 bullets (v3:504–506)**, still in force (v4 replaces only "the C-b column", v4:411) | "Proposed hierarchy (D20): C-c primary; **C-b and C-a secondary**"; permutation limitation bullet | **No — literal conflict.** v4:458–459 says it changes v2/v3, so the intent is clear, but the inherited bullet still lists C-b as secondary. C (document) |
| v3 §6.3 small-signature row (v3:474) | "C-c and C-b are run but labelled 'low gene count'" | Neutral ("run"); acceptable if "run" means descriptive |
| v2 §9.4 (v2:438) | C-b with permutation; "C-b as primary" listed as an alternative | Superseded by v4 §6.4, but v2 is not formally amended (expected; v2 is preserved) |
| v4 §6.4 sign-test value (v4:455) | "report the sign-test value labelled 'assumes independence — descriptive'" | **[ASSESSMENT]** Reporting a sign-test *p-value* even with a label invites confirmatory reading. Consider reporting only counts and T. Minor |
| Specificity (v3 §8) and pathways (v4 §7) | No use of C-b | Yes |

**[ASSESSMENT]** C-b is descriptive in all v4-authored text. One inherited v3 bullet (v3:504)
contradicts it and should be explicitly superseded. Whether C-b is subject to the §5.4 coverage rule
is unstated. Minor.

---

## 8. D14 pathways (review item 7)

| Element | [DOC] (v4:465–481) | [ASSESSMENT] | Class |
|---|---|---|---|
| Primary vs secondary | Primary: camera-type competitive test on the gene-level matrix; secondary: ORA | Clearly distinguished | A |
| Gene-level input | Gene-level matrix (D6 option), same design, contrast and weights as the gene-level model | Compatible with all D6 options **only if** a gene-level *matrix fit* exists. Under G1/G1b/G2, v3:428 implies the gene-level statistics are *taken from* the probe-level fit; a camera-type test needs the matrix of representative rows. Equivalent in substance, but it ties into blocker B3 | C (via B3) |
| Statistic | "Moderated t … (computed by the method from the model)" | **[NOT VERIFIABLE HERE]** Whether the intended software computes a moderated t internally, and with what defaults, cannot be checked without the pinned software documentation (D8). Should be verified at pinning | D |
| Universe | Entrez genes with a gene-level unit tested in discovery (one-to-one probes, after feature rules); identical for ORA | Consistent between methods and with all D6 options | A |
| Size filter | Intersect, then 15–500; same filtered collection for ORA | Consistent. Values proposed → B | B |
| Inter-gene correlation | Must be specified; D14 | Correctly open | B |
| Multiplicity | Primary: BH within collection. Secondary: BH within collection × list | Consistent with the primary's one test per set and the secondary's two lists. Methods are never combined (v4:479) | A |
| ORA with empty lists | Not addressed | If no gene reaches gene-level q < 0.05, or one direction is empty, ORA is undefined for that list. The rule should be "not run; reported". Minor | C (minor) |
| Annotation release consistency | Not addressed | Gene-set databases and probe annotation must share an Entrez release, or universe intersection is biased by ID drift. Links D6 and D14 | C/D |
| Versions | Unpinned until D8 and D14 (v4:480) | Correct | D |
| Inherited v3 §6.2 row "Pathways: … (representative probe)" (v3:445) | Still in force | Conflicts with G3 (blocker B3) | C |

---

## 9. Cross-section trace (review item 8)

| Stage | Defined in | Conflicts, circularity or hidden dependencies found |
|---|---|---|
| Eligibility (R1–R13, R2-ID/R2-COV) | v3 §3 | None new. D18 open (B) |
| QC: R8 | v4 §1 + v3 A0–A1 | v4/v3 A0 non-finite conflict (C); missing sex mapping (C); D_min sequencing (B1) |
| QC: R9 | v4 §2 + v3 §4.3 | S5 undefined (C); minor count re-check (C) |
| QC approval | v3:193–194 (exclusions after the PI approves the list); Stage B shows counts by diagnosis | **[ASSESSMENT] Post-result-adjacent discretion.** For R8 two-axis discordant arrays, the PI approves a proposed exclusion list after Stage B has shown diagnosis counts. If approval is discretionary rather than a check that the rule was applied, diagnosis composition could influence exclusions. Recommend restricting approval to rule-application verification. Major |
| Identifiability | v4 §3 + v3 §5.1–5.2 | B2 circularity; B5 tolerance; QR vs SVD; dropped v3 rules (§4.4) |
| Feature rules | D17 (v2 §6.1) | No validation-cohort feature rule (C) |
| Gene-level unit | v4 §4 + v3 §6.1, 6.2, 6.3 | B3 text conflict under G3; B4 reasoning errors |
| Signature lock | v3 §6.3 | Lock fields assume a representative probe (C under G3); otherwise deterministic ranking, unique-gene cap and empty-signature rules (A) |
| Validation | v4 §5 + v3 §6.4 | Weighting statement (C); B6 risks; cross-cohort multiplicity (B) |
| Specificity | v3 §8; v2 §10 | **B7:** v3:573 assesses "each locked AD-signature gene"; v2 §10.2 says "per locked, *replicated* gene". Restricting to replicated genes makes the specificity set depend on validation outcomes. That can be legitimate if prespecified, but the two texts conflict. Also unstated: whether the §5.4 coverage rule and z-standardization apply in GSE99039 (IPD + CONTROL score samples), and how G2 applies on GPL570. C |
| Pathways | v4 §7 | ORA empty lists; annotation release (C minor/D) |
| Discovery STOP propagation | v4 §3 step 3 | **Not stated:** if discovery STOPs, no signature exists, so replication, specificity and signature-based work do not run. Implied by v3:472 only for "no eligible genes". Minor |

**Unsupported or overstated claims found in v4-authored text:**

1. The floating-point independence claim (v4:68–69). Overstated.
2. The "equivalently" estimability claim (v4:232–233). Exact arithmetic only.
3. The heteroscedasticity condition (v4:308). Incorrect.
4. The larger-group bias statement (v4:312). Imprecise.
5. "All measurable genes are weighted equally" (v4:377). False for the two-directional formula.
6. "The primary population then does not depend on R9 at all" (v4:183). Overstated, given the
   numerical-failure exclusion.

**Claims appropriately labelled (no issue):**

- loss of chromosome Y (BACKGROUND);
- Bourgon et al. 2010 (marked "not reviewed locally");
- the Frisch–Waugh–Lovell invariance (correct, standard);
- the "conventional numerical-rank tolerance" (REASONING; used widely, but see the scale caveat).

---

## 10. Implementation-readiness classification (review item 9)

| Rule / component | Class | Reason |
|---|---|---|
| R2-ID identity checks (v3 §3.1) | A | Deterministic from metadata |
| R2-COV complete-case per analysis | A | Deterministic |
| D18 GSE140829 replicate handling | B | Option (a)/(b)/(c) |
| R8 A0 applicability (≥ 2 Y genes) | B | Proposed constant |
| R8 A1 Y score | A | Deterministic |
| R8 A2 split rule | C | Missing high/low → sex mapping; non-finite conflict with v3 A0 |
| R8 A3 separation | B + C | D_min open; SD denominator and +∞ handling; sequencing |
| R8 A4/A5 classification and evidence levels | C | "Usable axis" undefined |
| R8 ambiguous handling | B | D22 option |
| R8 for GSE140829 / GSE99039 | D | D19 mapping; GPL570 probes unresolved |
| R9 A0–A5 | A (k: B) | Deterministic; minor re-check gap (C minor) |
| R9 role (iii) | B | D22 |
| Sensitivity S5 | C | Direction and composition undefined |
| D7 estimability test | C | Scale-dependent tolerance; dual criterion |
| D7 STOP rules | A (thresholds: B) | Deterministic once c₁–c₃ are set |
| D7 c₁–c₃ | B | Unresolved; must be fixed before any M-check run |
| D7 nuisance-alias handling | A | Mathematically sound (FWL) |
| D7 metadata checks M1–M8 | A | Metadata only (QR/SVD wording to reconcile) |
| D6 G1 | A as rule; B as choice | Inferential text needs the §5.1 corrections |
| D6 G1b | C | Undefined beyond GSE63060 |
| D6 G2 | D (+ C) | Resource unverified; undefined for GPL570 |
| D6 G3 | B; inherited text C | Pipeline text tied to the representative probe |
| Probe-level BH family | A | — |
| Gene-level BH family | A (given D6) | — |
| Signature ranking, cap, empty and one-directional rules | A | Deterministic (v3 §6.3) |
| Signature lock contents | C | Assumes a representative probe |
| Score formulas | A | — |
| Score weighting | C → B | Statement contradicts formula; intended weighting is a choice |
| Coverage rule values | B | Conventions |
| Validation feature QC | C | Undefined |
| Cross-platform annotation release | C/D | Undefined; resource needed |
| C-a per gene within cohort | A | — |
| Cross-cohort multiplicity | B | Unstated |
| C-b descriptive | A | Inherited v3 bullet to supersede (C, document) |
| C-b inferential (P1–P3) | B / C | Unresolved methodology |
| Pathways: universe, filters, families | A (values: B) | Consistent |
| Pathways: inter-gene correlation, collections | B | D14 |
| Pathways: software statistic, versions | D | D8, D14 |
| ORA empty-list handling | C (minor) | Unstated |
| Specificity gene set and score rules in GSE99039 | C | Conflicting / undefined |
| Specificity δ | B | D13 |
| GSE140829 analyses | D | D19 |
| Notion reconciliation | D | D0 |

---

## 11. What this audit could not verify

| Item | Why not |
|---|---|
| Behaviour of the intended software | camera-type test statistic; whether `arrayWeights` is basis-invariant; how limma treats rank-deficient designs. Software not installed; documentation not reviewed (v4:445 also notes this) |
| Literature-dependent statements | Loss-of-Y prevalence; Bourgon et al. 2010; nuID encoding. Labelled BACKGROUND or REPORTED in v3/v4; not checked (no network) |
| Whether thresholds would pass or fail on real metadata | Proposed thresholds (n_min, 10 arrays, coverage 50% / 5) would pass or fail; M1–M8 have not been run, by design |
| Whether the Notion plan conflicts with v4 | Not read, per constraints |

---

## 12. Audit outcome

- **No decision D0–D22 is approved or settled by this audit.**
- The approval-gate status is unchanged:
  - **Not satisfied:** G1, G2, G5, G7, G8.
  - **Partially satisfied:** G3, G4, G6, G9.
- v4 is **not implementation-ready**:
  - **Blocker B1:** R8 cannot execute until D_min is set.
  - **Blocker B2:** c₁–c₃ are unset.
  - **Blocker B3:** the gene-level pipeline is internally inconsistent for G3, the option v4 leans
    towards.
  - **B4–B7:** several specification defects (class C) need a revision before approval.
  - **B8:** external dependencies (class D) remain for GSE140829, the software environment, GSE99039
    sex probes and the Notion plan.
