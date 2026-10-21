# BIO-MB-001 — Statistical Analysis Plan, DRAFT v5 (Phase 3B, audit-driven correction of v4)

**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen. No decision D0–D22 is approved. The
approval-gate status is unchanged:**

- **Not satisfied:** G1, G2, G5, G7, G8.
- **Partially satisfied:** G3, G4, G6, G9.

v1–v4 and `reports/phase3b/v4/SCIENTIFIC_CONSISTENCY_AUDIT.md` (the "audit"; findings B1–B8 and
sub-findings) are preserved unchanged.

Nothing was executed for v5:

- no expression value was read;
- no QC statistic, model, gene list, pathway result or signature exists;
- no sample is excluded or relabelled.

The only new local evidence is a text search of earlier reports for chip tabulations (§4.2).

**How v5 is organised.**

- The audit showed that v4's partial replacement of v3 left conflicting wording active. v5
  therefore **restates in full** every area the audit touched: QC, identifiability, gene-level
  pipeline, signature, validation, specificity, pathways, sensitivity analyses and the register.
- §0.2 lists exactly which earlier text remains active.
- Where a v5 section exists, it supersedes all earlier text on that topic.

Labels:

| Label | Meaning |
|---|---|
| **[EVIDENCE]** | Verified local fact or cited project report |
| **[REASONING]** | Methodological argument made here; standard results are named, not cited as verified |
| **[BACKGROUND]** | General domain knowledge, not verified in this project |
| **[PROPOSED]** | Suggested default; requires PI approval |
| **[PROPOSED (no source)]** | Suggested convention with no empirical or literature basis |
| **[DECISION NEEDED]** | Evidence does not determine an answer |
| **[UNRESOLVED]** | Cannot be resolved locally |
| **[DEPENDENCY]** | Requires external information or software approval |

Reference keys:

- [2A]–[2D] and [3A]: earlier phase reports.
- [P1]: phenotype tables.
- [v2], [v3], [v4]: earlier drafts.
- [AUD]: the audit.

---

## 0. Scope, supersession and change log

### 0.1 Change log from v4 (keyed to the audit)

| Audit item | v5 change | v5 § |
|---|---|---|
| B1 R8 threshold sequencing; missing high/low mapping | All R8 constants, including D_min, must be approved before Stage A. Nothing in Stage A, including D, is computed earlier. Axis interpretation restored and labelled as unvalidated. Per-array, per-axis non-finite rule defined. "Usable axis" defined. Options set out if D_min cannot be justified | 3.2 |
| B2 c₁–c₃ circularity | Thresholds, units, scaling and tolerance must be approved before **any** M-check. The v3 "informational" pre-QC run is withdrawn. Checks are split into decision checks and descriptive outputs, computed in one locked run | 4.2–4.3 |
| B3 G3 pipeline | One gene-level pipeline for every D6 option, built on a gene-level matrix U and a gene-level fit. "Representative probe" replaced by "selected probe" (G1/G1b/G2) or "constituent probes" (G3) | 5, 6, 7, 9 |
| B4 independence reasoning | Corrected: unequal group variances (not group sizes) create dependence; selection depends on true effects at any group sizes; assumption (d) removed | 5.3 |
| B5 tolerance scale | Scale-free estimability criterion E = 1 − R²_g with a stated numerical constant; standardized continuous columns; SVD only | 4.4 |
| B6 silent signature changes | Validation feature rule (proposed: none), cross-platform mapping rule, multi-mapped exclusion and scoring rule are all written into the lock | 6.2, 7.2 |
| B7 specificity gene set and coverage | Proposed: all locked genes; the coverage rule applies to GSE99039; both remain D13 decisions | 8 |
| B8 external dependencies | Unchanged; listed | 14.3 |
| Score weighting contradiction | Exact weighting convention stated (W1 direction-balanced proposed; W2 alternative) | 7.4 |
| S5 undefined | Rewritten as S5a–S5g, each run separately, plus one defined combination | 10 |
| C-b inherited "secondary" | Superseded everywhere: C-b descriptive; no p-value reported | 7.6 |
| Other sub-findings | Listed in §16 | 16 |

### 0.2 What remains active from earlier drafts

| Earlier text | Status in v5 |
|---|---|
| [v3 §1] inputs and limitations; [v3 §2] estimand E2 and discrepancies H1–H9 (with [v2 §3]) | **Active, unchanged** (summarized in §2) |
| [v3 §3] R2-ID / R2-COV and cohort missingness; [v2 §4.1, §4.3] R1–R13 and label handling | **Active, unchanged** |
| [v3 §7] GSE140829 mapping facts and gap | **Active, unchanged** |
| [v2 §7.4] covariate rationale; [v2 §9.1] cohort roles; [v2 §9.5] GSE63061 extra correlation (descriptive); [v2 §9.6] validation inputs; [v2 §11.2] version pin list; [v2 §11.3] exploratory list; [v2 §12] / [v3 §13] reproducibility | **Active**, except where a v5 section restates the topic |
| [v3 §4], [v4 §1–2] QC | **Superseded** by v5 §3 |
| [v3 §5], [v4 §3] identifiability; [v2 §7.3] | **Superseded** by v5 §4 |
| [v3 §6], [v4 §4–7]; [v2 §6.2–6.3], [v2 §9.2–9.4], [v2 §11.1] | **Superseded** by v5 §5–7, §9 |
| [v3 §8], [v2 §10] specificity | **Superseded** by v5 §8 |
| [v3 §9], [v2 §8] sensitivity | **Superseded** by v5 §10 |
| [v3 §10–12], [v4 §8–9] register and lists | **Superseded** by v5 §13–15 |

---

## 1. Inputs and limitations (unchanged; [v3 §1])

- Notion plan not reviewed (D0).
- No other plan document exists.
- R/Bioconductor not installed; nothing installed.

## 2. Foundations carried forward (summary for the consistency trace)

| Element | Definition (active source) |
|---|---|
| Primary estimand | **E2:** per-feature difference in deposited-scale blood expression between GSE63060 GEO `status` "AD" and "CTL" samples, conditional on approved covariates, among eligible samples ([v2 §3.1]). Includes ~41 likely converters (H1). Not E1 |
| Eligible population (pre-QC) | R1–R13 ([v2 §4.1]) with R2-ID and R2-COV ([v3 §3.1]) and R5 label handling ([v2 §4.3]) |
| Primary analysis population | Eligible population minus the rule-based QC exclusions of §3.5 |
| Cohort roles | GSE63060 discovery; GSE140829 replication candidate (independence unverified); GSE63061 related-cohort consistency; GSE99039 specificity ([v2 §9.1]) |

---

## 3. Sample QC (supersedes [v3 §4], [v4 §1–2])

### 3.1 Two stages and their separation

| Stage | Uses | Must not use | Output |
|---|---|---|---|
| **A — blind computation** | QC probe values (R8) or all deposited probes (R9); recorded sex (R8 A5 only); array IDs | Diagnosis; any model; any association result | Per-array table, checksummed before Stage B |
| **B — descriptive review** | Stage A table joined to chip/batch and deposited diagnosis **as counts only** | Association statistics; any change to Stage A parameters or policies | Review table; rule-applied exclusion list |

**Prerequisites (all approved and recorded before Stage A starts; none chosen after any Stage A
output exists):**

- probe lists;
- minimum Y genes;
- n_min and the tie tolerance;
- D_min;
- R9 k and the minimum array count;
- the near-identical tolerance;
- the R8 and R9 role and handling policies of §3.5.

**Scope of approval of exclusions [PROPOSED; D22].**

- The PI's approval of the exclusion list is limited to **verifying that the prespecified rules were
  applied correctly**. It is not a discretionary choice.
- Any deviation requires a documented protocol amendment *before* the population is linked to any
  expression model, and is reported.
- This removes the discretion that the audit flagged ([AUD §9]).

**Not externally validated.** Every boundary below is derived within each dataset. Error rates are
unknown. Flags are reported as "flagged by a dataset-internal rule". No sample is excluded solely
because it is flagged; exclusions follow only the prespecified policies of §3.5.

### 3.2 R8 sex-consistency check

**Inputs.**

- The cohort's Series Matrix values for sex probes verified present **in that Series Matrix**.
- Recorded sex.
- All deposited arrays, diagnosis ignored.

**Probe sets.** XIST ILMN_1764573, plus the 13 Y probes (9 genes) of [v2 §5.1]. These are verified
for GSE63060 and GSE63061 [EVIDENCE].

- GSE140829: requires D19 [DEPENDENCY].
- GSE99039: GPL570 sex probes not identified [UNRESOLVED].

**Steps (deterministic once the prerequisites are approved):**

- **A0 — cohort applicability.** R8 is *not applicable* if XIST is absent or fewer than 2 distinct Y
  genes are present ([PROPOSED (no source)]).
- **A0b — per-array, per-axis finiteness** (supersedes the v3 whole-array rule).
  - Array i is *finite on X* if its XIST value is finite.
  - It is *finite on Y* if at least one Y probe value is finite.
  - An array finite on neither axis is "unassessable (non-finite)".
- **A1 — scores.**
  - X_i = XIST value.
  - For each Y probe, subtract its median over arrays with a finite value.
  - Y_i = median of the array's finite centred Y values.
- **A2 — per-axis split.** Applied separately to the finite X values and the finite Y values.
  1. Sort: v₍₁₎ ≤ … ≤ v₍ₙ₎.
  2. Admissible s: v₍ₛ₎ < v₍ₛ₊₁₎, s ≥ n_min, n − s ≥ n_min. Tied values are never split.
     n_min = 5 ([PROPOSED (no source)]).
  3. W(s) = within-class sum of squares.
  4. Let W_min be the minimum. Candidates with W(s) ≤ W_min + 10⁻¹²·W_total ([PROPOSED (no source)])
     are tied, and the smallest s is chosen. The tolerance *reduces* sensitivity to floating-point
     summation order but cannot eliminate it at the boundary [AUD §2.1].
  5. t = (v₍ₛ*₎ + v₍ₛ*₊₁₎)/2. No value equals t. High: v > t; low: v < t.
  6. **Degenerate axis:** no admissible s. This includes fewer than 2 distinct values and
     n < 2·n_min.
- **A3 — separation.**
  - D = |mean_high − mean_low| / sqrt((sd_high² + sd_low²)/2), with SDs using the n − 1 denominator.
  - If both SDs are 0 and the means differ, D = +∞; this counts as separating and is listed.
  - An axis is **separating** iff it is non-degenerate and D ≥ D_min.
- **A4 — interpretation of the classes** [REASONING / BACKGROUND; **not externally validated** for
  these deposited, VST-scaled data]. Restored from [v3 §4.2 A2]:
  - **X axis:** high (X_i > t_X) → *female-type*; low → *male-type*. Basis: XIST is expressed from the
    inactive X chromosome present in cells with two or more X chromosomes.
  - **Y axis:** high (Y_i > t_Y) → *male-type*; low → *female-type*. Basis: Y-linked genes require a
    Y chromosome.

  These are expected biological directions. That the *higher class* produced by A2 corresponds to
  the biological sex group is an assumption, and is checked only indirectly through D.
- **Usable axis for array i:** the axis is separating for the cohort **and** array i is finite on it.
- **A5 — classification and comparison.**

| Usable axes for array i | Calls | Expression-derived sex | Evidence level |
|---|---|---|---|
| X and Y | Agree | Female or male pattern | **Two-axis** |
| X and Y | Disagree | **Ambiguous** | — |
| X only, or Y only | — | Female- or male-type | **Single-axis** (weaker; a Y-only call is especially weak in older men because of possible mosaic loss of Y [BACKGROUND]) |
| None | — | Not assessable | — |

| Comparison with recorded sex | Category |
|---|---|
| Two-axis = recorded | Concordant (two-axis) |
| Two-axis ≠ recorded | **Discordant (two-axis)** |
| Single-axis = recorded | Concordant (single-axis) |
| Single-axis ≠ recorded | **Discordant (single-axis)** |
| Ambiguous | Ambiguous |
| Recorded sex missing, or no usable axis | Unassessable |

**A discordance is not proof of sample misidentification** [REASONING]. It is compatible with:

- a metadata error;
- sex-chromosome aneuploidy or mosaicism;
- loss of Y;
- sample mixture;
- technical failure;
- misclassification near t.

Reports say "sex-check discordant". Diagnosis labels are never altered.

**Sequencing (resolves B1).**

- **R8 Stage A is not started until D_min has been scientifically justified and approved.**
- D is an output of Stage A only. It is never computed, plotted or inspected to choose D_min.
- **No X or Y distribution is examined before approval.**

**If D_min cannot be justified from existing evidence [UNRESOLVED; D5].** No local or cited source
gives a validated value, and none is invented here. The PI must choose one of:

- **(a)** Justify D_min from evidence external to these datasets' sex probes, such as published
  separation on comparable platforms. This requires a source not yet in the project.
- **(b)** Approve a protocol variant without a D_min: every non-degenerate axis is treated as usable,
  and cross-axis disagreement ("ambiguous") is the only safeguard. This is a weaker design, with
  more risk of mis-calls when an axis separates poorly, and must be approved as such.
- **(c)** Do not run R8. The sex check is then recorded as "not performed".
  - The only sex QC is then the submitters' pre-deposit XIST check, which is unauditable (REPORTED for
    GSE63060: one AD and one control removed in 2012 for an XIST/recorded-sex discrepancy;
    [2C] v2 §2 row 7).
  - No such check is documented for the other cohorts.
  - S5 components that depend on R8 are not run.

**Until the PI decides:** R8 status is "unavailable". The primary population contains no R8-based
exclusion. Whether the primary analysis may proceed without R8 is itself part of D5/D22
[DECISION NEEDED].

### 3.3 R9 array-outlier check

- **A0.**
  - Drop probes with any non-finite value (reported).
  - Arrays with zero variance → numerical failure.
  - If fewer than 10 arrays remain ([PROPOSED (no source)]) → R9 not applicable.
- **A1.**
  - Pearson r_ij over the common probes.
  - A non-finite r_ij is omitted from that array's median (count reported).
  - Arrays with more than half of their pairs omitted → numerical failure.
- **A2.** Pairs with r_ij ≥ 1 − 10⁻⁸ ([PROPOSED (no source)]) are listed for the D18 duplicate review
  and retained.
- **A3.**
  - m_i = median_j r_ij (even count: mean of the two middle values).
  - z_i = atanh(m_i).
  - |m_i| ≥ 1 or non-finite z_i → numerical failure.
- **A3b (new; [AUD §3]).** If fewer than 10 arrays with finite z_i remain → R9 not applicable.
- **A4.** M = median(z_i); S = 1.4826·median|z_i − M|. **If S = 0 or S is non-finite → R9 not
  applicable.** No flags, the condition is reported, and no substitute scale is used without a new
  decision.
- **A5.** Flag if z_i < M − k·S; k = 3 provisional; one-sided.

**Reference and feature set:** all deposited arrays and probes, uncentred ([v2 §5.2]).

**Batch structure** [REASONING]: see [v4 §2.2]. Flags can mark whole chips, miss arrays on uniformly
shifted chips, and correlate with diagnosis where chip and diagnosis are imbalanced. There is no
batch-neutral version of R9.

### 3.4 Stage B (descriptive only)

- Tabulate R8 categories, R9 flags and numerical failures by chip/batch and by deposited diagnosis, as
  counts.
- No inferential test is performed.
- Stage B cannot change any exclusion. Exclusions follow §3.5 mechanically.

### 3.5 QC policies, fixed before Stage A [PROPOSED; D22]

| QC outcome | Primary analysis | Sensitivity | Why |
|---|---|---|---|
| R8 two-axis discordant | **Excluded** (rule-based, listed) | S5f re-includes | Strongest available evidence of sample–metadata inconsistency |
| R8 single-axis discordant | Retained | S5d excludes | Weaker evidence (§3.2) |
| R8 ambiguous | Retained [PROPOSED; alternatives: exclude, or retain only] | S5e excludes | Least outcome-dependent default; cause unknown |
| R8 unassessable | Retained | — | No evidence |
| R9 flag | **Retained** — role (iii) of [v4 §2.3] | S5a–S5c exclude | Primary population not dependent on a batch- or diagnosis-correlated statistic |
| Numerical failure (R9 A0, A1, A3) | **Excluded** (rule-based, listed) | Not varied | The array yields no valid correlation profile |

**Qualification of the v4 claim** ([AUD §3]): the primary population is independent of R9 *flags*.
It depends on R9 Stage A only through the technical numerical-failure class.

Limitations of retaining flagged arrays: possible variance inflation, or bias if they are imbalanced
by group. These are assessed in S5 and S6.

---

## 4. Model identifiability (supersedes [v3 §5], [v4 §3], [v2 §7.3])

### 4.1 Mathematical estimability vs scientific adequacy

| Concept | Meaning | Established by |
|---|---|---|
| **Estimable contrast** | A unique least-squares AD–CTL coefficient exists: g ∉ span(N) | §4.4 steps 3–5 |
| **Minimum information** | The coefficient rests on enough within-unit information (mixed chips/batches; VIF) | §4.4 step 6, thresholds c₁–c₃ |
| **Scientific adequacy** | The coefficient estimates the intended quantity without material bias | **Not established by any check here** |

Passing §4.4 does **not** establish scientific adequacy. Residual threats [REASONING]:

- confounding by factors not captured by chip/batch;
- non-linear age effects (S2);
- unmeasured confounders: cell composition (S11), RIN, medication, APOE ([v2 §7.4]);
- label composition: the E2 "AD" group includes likely converters (H1);
- inherited submitter QC and normalization (H5, H8).

A PASS means only "estimable with the approved minimum information".

### 4.2 Pre-registration of decision thresholds (resolves B2)

**Before any metadata check M1–M8 is computed for any cohort**, the following must be approved and
recorded [DECISION NEEDED; D7]:

| Quantity | Unit / scale | Value |
|---|---|---|
| c₁ | Minimum number of mixed units (chips or batches containing both compared groups) | **Unset** |
| c₂ | Minimum number of samples of **each** compared group on mixed units | **Unset** |
| c₃ | Maximum VIF_g = 1/E (dimensionless; invariant to rescaling nuisance columns) | **Unset** |
| η | Numerical estimability constant for E | 10⁻⁸ [PROPOSED (no source); numerical, not scientific] |
| Scaling | Continuous nuisance columns centred and scaled to unit SD over the model samples; indicators 0/1 | [PROPOSED] |
| Rank tolerance | τ = max(n, p)·σ_max·ε_machine on the scaled N | [PROPOSED] |
| Scope | Whether c₁–c₃ are common to all cohorts or cohort-specific (chip vs batch; different n) | **Unset** |

- **The v3 "informational" pre-QC run is withdrawn.** No M-check of any kind runs before the
  approval above.
- **Prior exposure [EVIDENCE, limited]:**
  - [2B] v1 §4.1 tabulated the Sood "included" flag within chips ("varies within 29 of 29 chips"),
    not diagnosis.
  - A text search of earlier reports for "chip" found no diagnosis × chip table.
  - [2B] reported age and sex by diagnosis.
  - So the decision quantities (M2–M4) are believed unobserved. This rests on a text search, not on
    exhaustive verification.

### 4.3 Checks: decision vs descriptive

All checks are computed **together in one locked run** per cohort and design, on the approved post-QC
population, after §4.2 approval. The output is checksummed.

| Type | Checks | Effect |
|---|---|---|
| **Decision** | M2 mixed-unit counts; M3/E estimability; M4 VIF | Determine PROCEED or STOP (§4.4) |
| **Descriptive** | M1 group × unit table; M5 residual df; M6 singleton units; M7 chip × site; M8 age and sex by group and unit; condition number of N | Reported. **Cannot** alter PROCEED/STOP, the design or any threshold |

### 4.4 Deterministic procedure

1. **Build N** with:
   - the intercept;
   - age, centred and scaled;
   - the sex indicator;
   - indicators for **all** unit levels (redundancy allowed);
   - any sensitivity terms (site indicators; standardized spline columns).

   Column order is irrelevant.
2. **Nuisance space.**
   - SVD of N.
   - r_N = number of singular values > τ.
   - Q_N = the corresponding left singular vectors.
3. **Guard.** If g is constant (one group only) → **STOP: not estimable**.
4. **Estimability (sole criterion; supersedes v3 M3 QR and the v4 "equivalently" clause).**
   - E = ‖g − Q_N Q_Nᵀ g‖² / ‖g − ḡ‖² = 1 − R²_g.
   - Estimable iff E > η.
   - E is scale-free, and invariant to rescaling nuisance columns given r_N.
5. **Not estimable → STOP.**
6. **Minimum information.** If mixed units < c₁, or either group on mixed units < c₂, or
   VIF_g = 1/E > c₃ → **STOP**.
7. **PROCEED.**
   - Fit the approved design with unit as a fixed effect, using the full-rank basis [Q_N, g] or an
     equivalent basis.
   - Verify that the rank is r_N + 1.
   - Report only the group coefficient.
   - [REASONING: Frisch–Waugh–Lovell] The group coefficient, its SE, the residuals and the df
     (n − r_N − 1) are invariant to the choice of basis under least squares and under fixed-weight
     least squares.
   - **[UNRESOLVED / not verifiable locally]** Whether *estimated* array weights (S6) are
     basis-invariant must be checked against the pinned software.
8. **Aliasing report.** The null space of N lists exact dependencies among the named nuisance
   columns. Their coefficients are not reported.
9. **Singleton units** are retained and reported (no within-unit information under a fixed effect).
10. **Scope of the procedure.** It applies to every sensitivity design (c₁–c₃ included), every
    validation cohort and every specificity contrast. On STOP:

    | Where STOP occurs | Recorded as |
    |---|---|
    | Discovery primary | "Primary contrast not estimable / insufficient information". Cascade in §11 |
    | A sensitivity design | "Sensitivity not estimable / insufficient" |
    | A validation cohort | "Not assessable" — not a negative result |
    | A specificity contrast | "Not assessable" |

11. **No response, threshold or design is chosen or revised after any M-check output or any
    expression result exists.**

**Covariates:** age (linear), sex and unit; site is sensitivity only ([v2 §7.4]). Candidate method:
limma with trend = TRUE, pending D8.

---

## 5. Gene-level unit and discovery inference (supersedes [v3 §6.1–6.2], [v4 §4]; resolves B3, B4)

### 5.1 Terms

| Term | Meaning |
|---|---|
| **Eligible probe** | Probe with exactly one Entrez ID under the pinned annotation (one-to-one) that passes the approved feature rule. Multi-mapped and unmapped probes are **never** used in gene-level units, in any cohort |
| **Gene-level unit u_g(i)** | Per-sample value representing gene g, built by the approved D6 option |
| **Gene-level matrix U** | Rows = Entrez genes with ≥ 1 eligible probe; columns = samples of the model being fitted |
| **Selected probe** | The single probe defining u_g under G1, G1b or G2 |
| **Constituent probes** | All eligible probes averaged under G3. The term "representative probe" is retired |

### 5.2 D6 options (all open; none approved) [DECISION NEEDED]

| Option | u_g(i) | Selection data | Defined for |
|---|---|---|---|
| **G1** | Value of the eligible probe with the highest mean over the samples of the model being fitted; ties → probe ID ascending | Same samples as the test | All cohorts |
| **G1b** | Value of the eligible probe with the highest mean over a **prespecified disjoint selection set**; ties as G1 | MCI arrays of the same cohort that pass R1, R2-ID, R5 and the §3.5 QC exclusions: GSE63060 MCI (80 deposited); GSE63061 "MCI" (109; borderline excluded by R5); GSE140829 MCI (134; D18 applied) | Illumina cohorts. **GSE99039: undefined** (no MCI; no approved substitute) [UNRESOLVED] |
| **G2** | Value of the eligible probe chosen by an annotation-only rule fixed before data (e.g. a probe-quality grade, then probe ID ascending) | None | **Requires** a resource that provides such grades (availability unverified; D8) **and** a separate annotation-only rule for GPL570 (none specified) [DEPENDENCY] |
| **G3** | Mean of all eligible probes of g on the deposited scale (equals the single probe if only one) | None | All cohorts; the constituent probe sets differ by platform |

### 5.3 Validity of the gene-level test under each option [REASONING; corrects v4 §4.2]

**Setting:**

- Gaussian errors.
- Sample rows independent, each with the same across-probe error covariance.
- An intercept in the model.

Under this setting, the projections of the data onto span(1) and onto span(g̃) plus the residual space
are independent **whatever the mean structure**. So the vector of probe overall means is independent
of every probe's (β̂_g, s²).

| Point | Corrected statement |
|---|---|
| G1 validity | Selection by overall mean leaves the selected probe's test distribution unchanged whenever **that probe's own** group coefficient is 0. Other probes of the gene may be associated; v4 assumption (d) is unnecessary and removed |
| Unequal variances | With sample-specific error variances σ_i², Cov(ȳ, β̂_g) = (1/n)·Σ_i σ_i² g̃_i / ‖g̃‖². With no covariates and group variances: (σ²_AD − σ²_CTL)/n. **Dependence arises from unequal variances, not unequal group sizes.** It is zero for equal variances at any sizes (including 145 vs 104) and non-zero for unequal variances at any sizes. The v4 statement tying it to n_AD ≠ n_CTL is withdrawn |
| Dependence on true effects | E[ȳ_j] = (1/n)·1ᵀX·b_j contains (n_AD/n)·β_j at **any** group sizes. Among probes with equal control-group level, a probe higher in AD has a higher expected overall mean, so its probability of being selected depends on its true effect. This affects *which* probe represents an associated gene (representation, power, cross-cohort comparability), **not** null validity. The v4 "larger group" statement is withdrawn |
| Other caveats | Non-Gaussian errors (uncorrelated but not independent); limma-trend's prior depends on the mean. Small but unquantified |
| G1b | Disjoint selection samples: independent under sample independence, apart from weak, unquantified links via joint normalization and shared chips |
| G2 | No data used, so no selection dependence |
| G3 | No selection. Because the model is linear, the G3 coefficient equals the average of the constituent probes' coefficients (opposite effects cancel). Validity follows from the model alone. Estimand: "average probe signal" |
| Claim wording | G1/G1b/G2: "the selected probe for gene g is (not) associated". G3: "the average signal of gene g's eligible probes is (not) associated". A non-significant gene is never described as "not associated" |

**Status:** the evidence does not select a unique option.

- G2 and G3 do not rely on the §5.3 independence assumptions; G1 relies on them fully; G1b relies on
  them weakly.
- G3 needs no new resource but changes the estimand, and its constituent probes differ across
  platforms.
- v4's "leaning G3" is **not** carried forward as a default.

**Approval needed (D6):**

- (i) the option;
- (ii) for G1b, the disjoint sets above and a solution for GSE99039;
- (iii) for G2, the resource and a GPL570 rule;
- (iv) the alternative option used as S8.

### 5.4 Discovery pipeline (one pipeline for all options)

1. **Probe-level discovery.** Fit the primary model to every probe passing the feature rule,
   including multi-mapped and unmapped probes. BH across all tested probes: the **probe-level
   family**.
2. **Build U** for the primary-model samples by the approved option, diagnosis-blind. Record each
   gene's selected probe (G1/G1b/G2) or constituent probe list (G3). Checksum.
3. **Gene-level fit.** Fit the same design (same covariates, identifiability result and limma
   settings) to U. This gives, per gene: effect β_g (AD − CTL), SE, 95% CI, moderated t and p.
   BH across all rows of U: the **gene-level family**.
   - Under G1/G1b/G2, β_g equals the selected probe's probe-level effect, but the moderated t and q
     differ because the moderation prior and the BH family differ.
   - **Gene-level claims use only the gene-level fit.**
4. **Direction** of gene g = sign(β_g) from the gene-level fit.
5. Probe-level and gene-level families are reported separately and never mixed.
6. Probe-discordant genes: genes whose eligible probes have probe-level q < 0.05 in opposite
   directions are flagged.

---

## 6. Signature lock (supersedes [v3 §6.3], [v2 §9.2])

### 6.1 Selection [PROPOSED; D15]

- **Eligibility:** gene-level q < 0.05.
- **Ranking (deterministic):**
  1. q ascending;
  2. then |β_g| descending;
  3. then |moderated t| descending;
  4. then Entrez ID numerically ascending.
- **Cap:** the top 200 **unique Entrez genes**. U has one row per gene, so uniqueness holds by
  construction and is asserted at lock.
- **Coverage restriction at selection:** none by default. Alternative: restrict to genes annotated on
  every validation platform (annotation-only; D15).

**Prespecified special cases:**

| Case | Response |
|---|---|
| No eligible genes | No signature. Replication, specificity-on-signature and signature-dependent analyses are **not run**. The threshold is not relaxed (a relaxed analysis would be new, labelled exploratory work needing approval) |
| Up-only or down-only | Locked as one-directional; score per §7.4 |
| Fewer than 10 genes ([PROPOSED (no source)]) | Locked; scores labelled "low gene count" |

### 6.2 Lock contents

Written before any validation or specificity expression value is modelled against diagnosis.
Checksummed. The lock contains:

1. The D6 option and the pinned annotation resource and release (§7.2).
2. Per gene:
   - Entrez ID and symbol;
   - the discovery selected probe or constituent probe list;
   - β_g with 95% CI, moderated t, gene-level q;
   - direction and rank.
3. Counts: eligible genes, locked up genes, locked down genes.
4. **Scoring rule:**
   - the weighting convention (§7.4);
   - the standardization;
   - the coverage thresholds (§7.5);
   - the one-sided test direction.
5. **Validation feature rule** (§7.2) and **mapping rule** (§7.2).

The same lock file (same checksum) governs every validation and specificity cohort. **No cohort
receives a different gene list, weighting, coverage rule or mapping rule.**

---

## 7. Validation: replication and consistency (supersedes [v3 §6.4–6.5], [v4 §5–6], [v2 §9.2–9.4])

### 7.1 Roles (unchanged; [v2 §9.1])

- GSE140829: replication, independence unverified.
- GSE63061: related-cohort consistency.
- Results are reported under separate headings. Neither is used to tune anything.

### 7.2 Mapping, feature and probe rules (resolves B6) [PROPOSED unless stated]

| Rule | Specification | Status |
|---|---|---|
| Cross-platform mapping | Every platform annotation comes from **one pinned release** sharing an Entrez snapshot. The match key is **Entrez ID only** (no symbol matching). Retired or merged IDs are not remapped unless an ID-history procedure is approved; they become "unmapped" and are counted | Resource and release unpinned [DEPENDENCY: D6, D8] |
| Multi-mapped probes | Excluded from gene-level units in **every** cohort (same as discovery) | Proposed |
| Validation feature filter | **None.** No expression-based filtering in validation cohorts. Every eligible probe present in the cohort's Series Matrix is usable. Any alternative must be prespecified in the lock | Proposed (approval: D17/D15) |
| Gene-level unit | Built by the same D6 option from the cohort's own data and annotation: G1 uses the cohort's score samples; G1b the cohort's MCI set; G2 the platform rule; G3 the platform's eligible probes | Per D6 |
| Presence | A probe is present only if its ID appears in **that cohort's Series Matrix** ID column (not the manifest or raw file). GSE140829 requires D19 | — |
| Reporting | The selected probe or constituent list per gene per cohort is reported (it can differ from discovery) | Proposed |

### 7.3 Measurability categories (each locked gene, each cohort)

1. **Unmapped:** no Entrez match on the platform.
2. **No eligible probe in the Series Matrix.**
3. **Constant in cohort:** SD of u_g over the score samples is 0 or non-finite.
4. **Measurable.**

The v2/v3 category "excluded by approved feature QC" is removed, because the proposed validation
feature filter is "none". Categories 1–3 are "not measurable", never "not replicated". Until D19 is
resolved, every locked gene is unmapped in GSE140829.

### 7.4 Composite score (C-c; primary) — exact definition

**Inputs:**

- Score samples: all eligible samples of the cohort's AD–control contrast, after R-rules, §3.5 QC and
  R2-COV (and D18 for GSE140829).
- U_c, D_c: the measurable locked up and down genes.
- z_gi = (u_g(i) − mean_g) / sd_g, with the mean and SD (n − 1 denominator) over all score samples,
  diagnosis-blind.

**Weighting convention [DECISION NEEDED; D20].** Two candidates. The lock records one.

| Convention | Two-directional lock | Up-only lock | Down-only lock | Gene weights |
|---|---|---|---|---|
| **W1, direction-balanced** [PROPOSED default] | S_i = mean_{U_c} z − mean_{D_c} z | mean_{U_c} z | −mean_{D_c} z | Equal **within** a direction: 1/\|U_c\| for up genes, −1/\|D_c\| for down genes. Each direction carries total weight 1 |
| **W2, gene-equal** | S_i = (Σ_{U_c} z − Σ_{D_c} z) / (\|U_c\| + \|D_c\|) | Same as W1 | Same as W1 | ±1/(\|U_c\| + \|D_c\|) for every gene |

- This corrects the v4 sentence "all measurable genes are weighted equally", which holds only for W2
  or for one-directional locks.
- **Rationale [REASONING]:**
  - W1 keeps both biological directions represented regardless of imbalance. It matches the v2
    definition.
  - W2 lets the larger direction dominate, but treats every gene identically.
  - Neither is determined by evidence.

**Test.** S ~ group + the cohort's approved covariates, with identifiability per §4. Report:

- the one-sided p-value for the group coefficient > 0;
- β̂ with a two-sided 95% CI.

**Not assessable** if §4 STOPs, or if the §7.5 coverage rule fails.

### 7.5 Coverage rule for score assessability [PROPOSED (no source); D15]

1. At least 50% of all locked genes are measurable.
2. For each direction that is non-empty at lock: at least 50% of that direction's locked genes **and**
   at least min(5, locked in that direction) are measurable.
   - When fewer than 5 genes are locked in a direction, all of them must be measurable.
3. A two-directional lock with a direction that has zero measurable genes is **not assessable**. It is
   never converted to a one-directional score (a one-directional version may be shown only as a
   labelled descriptive analysis).

The 50% and 5 values are conventions requiring approval.

**Reported per cohort:**

- category counts and lists by direction;
- the measurable proportions;
- whether the rule passed.

### 7.6 Per-gene replication (C-a; secondary) and direction concordance (C-b; descriptive)

- **C-a (secondary, inferential).**
  - For each measurable locked gene: gene-level fit in the cohort (same covariates; §4).
  - One-sided p-value in the locked direction.
  - BH across the measurable locked genes **within that cohort**.
  - The proportion replicating is reported with a binomial CI labelled descriptive.
- **C-b (descriptive / exploratory only; supersedes [v3 §6.5] bullets and [v2 §9.4]).**
  - Report T = the proportion of measurable locked genes whose cohort effect has the locked sign,
    plus concordant and discordant counts by direction and the coverage status.
  - **No p-value is reported**, including no sign-test p-value.
  - C-b is never called "secondary" or confirmatory. It becomes inferential only if D12 approves a
    justified procedure; the candidates are P1–P3 of [v4 §6.3], none adequate as specified.
- **Hierarchy (every cohort):** C-c primary → C-a secondary → C-b descriptive.

### 7.7 Multiplicity across cohorts [PROPOSED; D20]

- GSE140829 (replication) and GSE63061 (consistency) answer different, separately reported
  questions. Each C-c is tested at one-sided α = 0.05.
- There is no pooled claim and no cross-cohort adjustment.
- Alternative: Holm across the two C-c tests.
- GSE63061 additionally reports the correlation of discovery and cohort effects across measurable
  locked genes (descriptive; [v2 §9.5]).

---

## 8. Disease specificity — GSE99039 (supersedes [v3 §8], [v2 §10]; resolves B7)

### 8.1 What is assessed [PROPOSED; D13]

- **Gene set:** **all locked genes** (identical lock; §6.2). Not only genes that replicated.
- **Rationale [REASONING]:**
  - Restricting to replicated genes would make the specificity set depend on validation outcomes.
  - It would also make specificity depend on D19, since GSE140829 is unmapped until D19 is resolved.
  - Using all locked genes keeps one fixed object across cohorts.
- **Alternative:** a replicated-genes-only analysis, as an additional, labelled, prespecified
  analysis.

This supersedes the [v2 §10.2] heading "per locked, replicated gene".

**Contrasts, kept separate:**

- IPD vs CONTROL (primary);
- GPD vs CONTROL;
- GENETIC_UNAFFECTED vs CONTROL;
- OTHER_NEURO labels descriptive only.

**Covariates:** sex + batch, complete case ([v3 §3.4]: −35 for IPD vs CONTROL). Identifiability per
§4; STOP means "not assessable".

**Gene-level units:** per D6 on GPL570, with the same mapping rules (§7.2):

- G1 and G3 are defined;
- **G1b is undefined;**
- **G2 needs a GPL570 rule** [UNRESOLVED / DEPENDENCY].

**Score:**

- Same locked formula and weighting (§7.4).
- z is computed over each contrast's score samples.
- **The §7.5 coverage rule applies** [PROPOSED]. Whether the same thresholds suit a different
  technology is part of D13 [DECISION NEEDED].

### 8.2 Evidence categories per locked gene

| Category | Rule |
|---|---|
| Association with PD | 95% CI of the IPD − CONTROL effect excludes 0 **and** BH q < 0.05 across the measurable locked genes |
| Association not demonstrated | Otherwise |
| Compatible with no meaningful association | Equivalence by TOST with margin δ. **Unavailable until δ is scientifically justified and approved** (D13; no value proposed) |

### 8.3 What cannot be concluded

- **AD specificity** is never inferred from a significant AD association together with a
  non-significant PD association. A difference in significance is not a significant difference;
  non-significance may reflect power, platform or covariate loss.
- **AD vs PD effects:** no cohort contains both, so the AD × PD contrast and the difference between
  the AD and PD effects are **not estimable**.
- **Absence of a PD effect** cannot be claimed without δ.
- **Effect magnitudes are not on a common scale** [REASONING]. The platforms are Affymetrix RMA vs
  Illumina VST/RSN, with different probe designs, compression, laboratories and populations.
  Standardized effects do not remove technology-specific compression. Descriptive only:
  - magnitude comparisons;
  - "stronger in AD";
  - the proportion of AD-signature genes also associated with PD;
  - cross-platform forest plots.

Specificity results never alter the lock or any replication result.

---

## 9. Pathway analysis — exploratory (supersedes [v4 §7], [v3 §6.6], [v2 §11.1])

| Element | Primary exploratory | Secondary |
|---|---|---|
| Method | Competitive gene-set test with inter-gene correlation (camera-type) | ORA (one-sided hypergeometric / Fisher) |
| Input | Gene-level matrix U and the **gene-level fit** of §5.4 (same design, contrast and weights) | Gene lists from the gene-level fit: q < 0.05 and β_g > 0 (up) or < 0 (down), before the cap |
| Statistic | Gene-level moderated t for AD − CTL. Whether the chosen software computes this internally, and with which defaults, must be verified at pinning [UNRESOLVED; D8] | List membership |
| Universe | Rows of U (Entrez genes with ≥ 1 eligible probe tested) | Identical |
| Gene-set IDs | Gene-set collections mapped to the **same Entrez release** as the probe annotation, or via an approved documented mapping [DEPENDENCY: D6, D14] | Same |
| Set filter | Intersect with the universe, then keep 15–500 genes [PROPOSED] | Same filtered collection |
| Inter-gene correlation | Estimated or fixed: [DECISION NEEDED; D14] | Not modelled (anti-conservative; secondary) |
| Empty lists | — | An empty up or down list → that ORA is **not run**; reported |
| Multiplicity | BH within each collection | BH within each collection × list |
| Role | Main exploratory report | Supporting only; never rescues or overrules the primary |

- Collections and versions are unpinned until D8 and D14 ([v2 §11.2]).
- Interpretation limits as in [v2 §11.1]: blood cell composition; no brain mechanism.

---

## 10. Sensitivity analyses (supersedes [v2 §8], [v3 §9])

**General rules:**

- All are prespecified and all are reported.
- None replaces the primary analysis.
- Each passes §4, including c₁–c₃. Failure → "not estimable / insufficient".
- **Discovery sensitivities never lock a new signature.** They report probe-level and gene-level
  results, plus the effects of the locked genes under the sensitivity.

| # | Definition |
|---|---|
| S1 | Age restriction: (a) ≥ 65; (b) 61–88, the intersection of the AD/CTL age ranges of GSE63060, GSE63061 and GSE140829 [EVIDENCE, P1]. Not applied to GSE99039 |
| S2 | Age as a 3-df spline |
| S3 | Site added, or site instead of chip (M7 descriptive; only if estimable) |
| S4 | Exclude the 37 "M"-coded AD samples. Labelled "under an undocumented coding assumption"; not an E1 estimate |
| **S5** | **QC influence (rewritten; each run separately, relative to the primary population):** |
| S5a | Exclude R9-flagged arrays, k = 3 |
| S5b | Exclude R9-flagged arrays, k = 2.5 |
| S5c | Exclude R9-flagged arrays, k = 4 |
| S5d | Exclude R8 single-axis discordant arrays |
| S5e | Exclude R8 ambiguous arrays (or include them, if the approved primary option excludes them) |
| S5f | Re-include R8 two-axis discordant arrays (influence of the primary R8 exclusion) |
| S5g | **Defined combination:** exclude R9-flagged arrays (k = 3), R8 single-axis discordant arrays **and** R8 ambiguous arrays, i.e. every QC flag at k = 3 excluded, whatever the primary ambiguous-sex option |
| | Numerical-failure arrays are excluded in every variant. R8-dependent variants are not run if R8 is unavailable (§3.2). Flag-to-chip concentration is reported, because S5 may then partly remove chips [REASONING] |
| S6 | Array-quality weights (estimated). Basis invariance not verified (§4.4 step 7) |
| S7 | Additional diagnosis-blind mean-expression filter at the 25th and 50th percentiles (discovery only; applied before U is built) |
| S8 | The alternative D6 option, prespecified together with D6. For G1 between Illumina platforms: identical-probe-ID matching, where present in the target Series Matrix |
| S9 | 2008 BGX annotation vs the pinned annotation |
| S10 | Re-normalization from the non-normalized file (inferred labels for 3 columns; only if approved; [v2 §8] risks) |
| S11 | Cell-composition adjustment (method: D21) |
| S12 | Sood flagged subset (49 vs 67); never a replacement for the primary |
| S13 | GSE140829 final ComBat file vs Series Matrix + batch (validation) |
| S14 | GSE140829 including the "replicate 2" arrays (if D18 option c) — the "D18 variant" of v3 |

---

## 11. Order of operations and STOP cascade

| Step | Action | Prerequisite approvals |
|---|---|---|
| 0 | Approve: annotation resource and release (D6, D8); all §3.1 QC prerequisites (D5, D22); §4.2 thresholds (D7); D6 option and S8; D15 / D17 / D20 rules; sensitivity set (D16) | PI |
| 1 | Pin annotation; probe → Entrez tables; checksum | 0 |
| 2 | Eligibility (R-rules) | D2, D4, D18 |
| 3 | QC Stage A (R8 if available; R9); Stage B; rule-applied exclusion list (§3.5) | D5, D22 |
| 4 | Identifiability (one locked run; §4) | D7 |
| 5 | Probe-level discovery; build U; gene-level fit (§5.4) | D3, D6, D8 |
| 6 | Signature lock (§6) | D15, D20 |
| 7 | Validation (§7) | D19 for GSE140829; D10, D11, D12 |
| 8 | Specificity (§8) | D13 |
| 9 | Pathways (§9) | D14 |
| 10 | Sensitivity analyses (§10) | D16 |

**Cascade:**

- STOP at step 4 (discovery) → steps 5–9 are not run, and the limitation is reported.
- No eligible genes at step 6 → steps 7–8 (signature-based) are not run. Pathways may still run
  (exploratory, on the gene-level fit).
- A validation or specificity STOP or coverage failure → "not assessable" for that cohort only.

---

## 12. Cross-section consistency trace (after the v5 edits)

### 12.1 Definitions as now active

| Concept | Single active definition | Used consistently in |
|---|---|---|
| Estimand | E2 (§2) | §4.1 (adequacy), §5.4, reporting |
| Eligible population | R1–R13, R2-ID/COV, R5 (§2) | §3, §4, §7.4 score samples, §8 |
| Primary population | Eligible minus §3.5 rule-based exclusions (R8 two-axis discordant; numerical failures) | §4, §5.4, §10 (S5 relative to it) |
| Gene-level unit | §5.1–5.2 (D6 option) | §5.4, §6.2, §7.2, §8.1, §9 |
| Gene-level statistic and direction | Gene-level fit on U; direction = sign(β_g) (§5.4) | §6.1 ranking, §6.2 lock, §7.6 C-a, §9 |
| Locked signature | §6.2 lock, including the scoring, mapping and feature rules | §7, §8 (identical file) |
| Replication score | §7.4 (W1/W2 per lock), §7.5 coverage | §7, §8.1 |
| Specificity assessment | All locked genes; §8.2 categories | §8 only |
| Pathway input | U plus the gene-level fit; universe = rows of U | §9 |
| Sensitivity | §10 S1–S14 | §4 step 10, §11 |

### 12.2 Obsolete wording no longer active (explicitly superseded)

| Superseded text | Replaced by |
|---|---|
| [v3 §4.2 A0] whole-array non-finite rule | §3.2 A0b |
| [v4 §1.2] "D is reported" before D_min is approved | §3.2 sequencing |
| [v3 §4.3] Stage B response list for R9 | §3.4–3.5 |
| [v4 §2.3] "primary does not depend on R9 at all" | §3.5 qualification |
| [v3 §5.2] informational pre-QC run; QR in M3 | §4.2–4.4 |
| [v3 §5.3] term-order dropping rule | §4.4 |
| [v4 §3.2] "equivalently" clause and scale-dependent ‖g̃‖ test | §4.4 step 4 |
| [v3 §6.1 steps 5, 7], [v3 §6.2], [v3 §6.3 direction and lock fields]: "representative probe" | §5.4, §6.2 |
| [v3 §6.2] "diagnosis-blind … keeps the selection valid" | §5.3 |
| [v4 §4.2] heteroscedasticity condition; "larger group" statement; assumption (d) | §5.3 |
| [v4 §4.3] "leaning G3" | §5.3 status (no default) |
| [v3 §6.5] hierarchy bullet "C-b and C-a secondary"; within-batch permutation null | §7.6 |
| [v2 §9.4] C-b permutation, "C-b as primary" alternative, sign test reported | §7.6 |
| [v4 §6.4] sign-test value reported | §7.6 (no p-value) |
| [v4 §5.3] "all measurable genes are weighted equally" | §7.4 |
| [v2 §9.3], [v4 §5.1] "excluded by approved feature QC" category | §7.3 |
| [v3 §6.6], [v4 §7] "representative-probe" pathway statistic | §9 |
| [v2 §10.2] "per locked, replicated gene" | §8.1 |
| [v2 §8 S5] "include flagged arrays"; [v3 §9 S5] | §10 S5a–S5g |
| [v2 §8 S8] "mean of probes" as fixed sensitivity | §10 S8 (alternative D6 option) |
| [v3 §9] "D18 (new sensitivity)" | §10 S14 |

### 12.3 Remaining cross-section dependencies (not hidden; all listed in §14)

- D6 ↔ D8 (resource) ↔ D14 (gene-set release).
- D19 ↔ every GSE140829 analysis.
- D5 ↔ whether R8 exists at all.
- D7 thresholds ↔ every PROCEED/STOP.
- D20 weighting ↔ the lock.
- D13 ↔ specificity coverage and δ.

---

## 13. Decision register (D0–D22; none approved; full restatement)

† = changed in v5.

| ID | Question | Evidence | Proposed default | Alternatives and consequences | Additional data? | Depends on | Approval before implementation |
|---|---|---|---|---|---|---|---|
| D0 | Reconcile with a Notion or other plan | Not reviewed | Provide the content | Conflicting plans | **Yes** | — | Yes |
| D1 | Primary estimand | [3A]; H1 | E2 with converter caveat | E1 infeasible without D9 | For E1 | D9 | Yes |
| D2 | Eligibility and label rules | [v3 §3]; [v2 §4.3] | R2-ID all cohorts; R2-COV per analysis; R5 | — | No | D1, D18 | Yes |
| D3 | GSE63060 input | [2A] | Series Matrix, no re-normalization | S10 | No | — | Yes |
| D4 | Age eligibility | H2 | No restriction; S1(a), S1(b) | ≥ 65 primary | Owner explanation | D7 | Yes |
| D5 † | R8 and R9 constants | §3 | n_min 5; tie tolerance; ≥ 2 Y genes; k = 3; minimum 10 arrays; near-identical tolerance. **D_min unset; options (a)/(b)/(c) if unjustifiable** | R8 unavailable until decided | External source for (a) | D22 | Yes, before Stage A |
| D6 † | Gene-level unit and annotation | §5 | **None declared**; G1 / G1b / G2 / G3 open; S8 alternative to be chosen with it | Estimand, assumptions, resources and platform coverage differ | Yes (G2; resource) | D8 | Yes |
| D7 † | Identifiability thresholds and conventions | §4 | Procedure §4.4; η = 10⁻⁸; scaling and τ as §4.2. **c₁–c₃ and their scope unset** | — | No | D4, D8 | Yes, before any M-check |
| D8 | Environment | R absent | Pinned R/Bioconductor | Python (needs validation) | No | — | Yes (installation) |
| D9 | Data-owner requests | H1–H4, H9; D18 | Request | — | **Yes** | — | Yes |
| D10 | GSE140829 independence standard | [3A] F13 | "Unverified" | — | **Yes** | D9 | Yes |
| D11 | GSE140829 input | GEO | Series Matrix + batch; S13 | ComBat | No | D19 | Yes |
| D12 † | Replication criteria | §7 | C-c (§7.4), C-a (§7.6); **C-b descriptive, no p-value** | Inferential C-b only via an approved P1–P3 or other justified procedure | Methodological review | D15, D20 | Yes |
| D13 † | Specificity | §8 | All locked genes; IPD vs CONTROL with sex + batch; the §7.5 coverage rule applies; δ unset | Replicated-genes-only analysis; different coverage thresholds for GPL570 | Justification for δ | D6, D12 | Yes |
| D14 † | Pathways | §9 | Camera-type primary; ORA secondary; universe = rows of U; same Entrez release | Correlation handling; collections | Yes | D6, D8 | Yes |
| D15 † | FDR, cap, coverage | §6–7 | q < 0.05; 200 unique genes; 50% / min(5) coverage; no coverage restriction at selection | Other values | No | — | Yes |
| D16 † | Sensitivity set | §10 | S1–S14 with S5a–g | — | No | D4–D7, D18, D21 | Yes |
| D17 † | Expression filters | §7.2; S7 | None (discovery primary **and** validation) | Filters as S7 | No | D15 | Yes |
| D18 | Identity and GSE140829 replicates | [v3 §3] | Exclude "replicate 2" (a); S14 if (c) | (b) | Owner clarification | D9 | Yes |
| D19 | GSE140829 mapping | [v3 §7] | Approved resource | Package; GPL15988 table; validated new code | **Yes** | D8, D6 | Yes |
| D20 † | Replication hierarchy, weighting, cross-cohort multiplicity | §7.4–7.7 | C-c > C-a > C-b (descriptive); **W1**; separate α per cohort | W2; Holm across cohorts | No | D12 | Yes, before lock |
| D21 | Cell composition (S11) | — | Not proposed | — | Yes | D8 | Yes |
| D22 † | QC policies and review scope | §3.1, §3.5 | Policies as §3.5; approval limited to verifying rule application | Ambiguous excluded or retained-only; whether primary may proceed without R8 | No | D5 | Yes, before Stage A |

---

## 14. Items requiring approval or resolution

### 14.1 PI scientific decisions (the evidence does not determine an answer)

| Decision | Choice required |
|---|---|
| D5 | D_min, or option (a)/(b)/(c); constants |
| D22 | Ambiguous-sex policy; whether primary may proceed without R8 |
| D7 | c₁–c₃ and whether they are common or cohort-specific |
| D6 | Option and S8 alternative; G1b sets and the GSE99039 solution; G2 rules |
| D20 | W1 vs W2; cross-cohort multiplicity |
| D15 | Coverage values; FDR level; cap |
| D17 | Validation filter "none" |
| D12 | Any inferential C-b |
| D13 | Gene set, coverage for GPL570, δ |
| D14 | Correlation handling; collections |
| D16 | The sensitivity set |
| Unchanged | D1, D2, D3, D4, D11, D18, D21 |

### 14.2 Unresolved methodology (recorded, not forced)

- A validated R8 separation criterion.
- A valid inferential C-b.
- A batch-neutral R9.
- The magnitude of G1 selection dependence under unequal variances.
- G1b for GSE99039.
- G2 for GPL570.

### 14.3 External or software dependencies

| Item | Dependency |
|---|---|
| D0 | Notion plan |
| D8 | Software environment |
| D9 / D10 | Data owners |
| D19 | GSE140829 mapping |
| — | GPL570 sex probes |
| — | Annotation and gene-set releases |
| — | Verification of software behaviour: camera statistic; estimated weights |

---

## 15. Metadata-only checks to run later (updated timing)

1. **M1–M8 per §4.3.** Run only after the §4.2 approvals, in one locked run on the approved post-QC
   population, for every cohort and design.
2. Exact complete-case counts per analysis ([v3 §3.4]), including the GSE99039 union of missing age
   or sex.
3. R2-ID listings: GSE140829 "replicate 2" arrays; GSE99039 missing `subject_id`.
4. Sex-probe presence in each Series Matrix:
   - GSE140829 after D19;
   - GSE99039 after a GPL570 annotation is pinned.
5. The explanation of the 223-row difference in GSE140829, after D19.
6. Annotation coverage per platform after D6/D8: one-to-one, multi-mapped and unmapped counts;
   eligible-probe counts per gene; the expected universe.
7. Lock coverage per validation and specificity platform (identifiers only).
8. Gene-set sizes after intersection with each universe.
9. Version inventory after D8.

---

## 16. Disposition of audit findings

| Audit finding | Status | v5 § |
|---|---|---|
| B1: R8 cannot run; threshold could be set after viewing D | **Partially resolved.** Sequencing fixed (no D before approval); options set out. D_min remains unset by design, so R8 still cannot run | 3.2 |
| B1 sub: high/low → sex mapping missing | Resolved | 3.2 A4 |
| R8 per-array non-finite conflict | Resolved | 3.2 A0b |
| R8 "usable axis" undefined | Resolved | 3.2 |
| R8 SD denominator; +∞ handling | Resolved | 3.2 A3 |
| R8 floating-point wording | Resolved | 3.2 A2 |
| B2: c₁–c₃ could be set after metadata outcomes | **Resolved** (pre-registration; informational run withdrawn). Values remain unset (decision) | 4.2–4.3 |
| D7: dropped v3 rules (fit instruction, singletons, no post-result revision) | Resolved | 4.4 steps 7, 9, 11 |
| D7: QR vs SVD | Resolved | 4.4 |
| D7: one-group guard | Resolved | 4.4 step 3 |
| D7: cohort-specific thresholds | Partially resolved (scope made an explicit decision) | 4.2 |
| D7: estimable vs adequate | Resolved | 4.1 |
| B3: G3 pipeline incoherent | Resolved | 5.1, 5.4, 6.2, 7.2, 9 |
| B4: independence reasoning errors | Resolved | 5.3 |
| B5: scale-dependent tolerance | Resolved | 4.2, 4.4 |
| B6: silent cohort changes (feature filter, annotation release, multi-mapped, per-cohort probe) | **Partially resolved.** Rules proposed and locked; the annotation release depends on D6/D8 | 6.2, 7.2 |
| Score weighting contradiction | Resolved (convention explicit; W1 vs W2 is a decision) | 7.4 |
| One-sided test vs CI | Resolved | 7.4 |
| Cross-cohort multiplicity | Partially resolved (proposal; D20) | 7.7 |
| Coverage rule for small directions | Resolved (stated) | 7.5 |
| GSE140829 score not assessable before D19 | Resolved (stated) | 7.3 |
| B7: specificity gene set; coverage for GSE99039 | **Resolved as an active rule**; remains a D13 decision | 8.1 |
| S5 undefined | Resolved | 10 |
| S5 chip-concentration interpretation | Partially resolved (reported; c₁–c₃ apply to sensitivity designs) | 10, 4.4 |
| R9 minimum count after removals | Resolved | 3.3 A3b |
| R9 "does not depend at all" wording | Resolved | 3.5 |
| QC approval discretion | Resolved | 3.1 |
| C-b inherited "secondary" | Resolved | 7.6, 12.2 |
| Sign-test p-value reporting | Resolved (not reported) | 7.6 |
| C-b coverage reporting | Resolved | 7.6 |
| ORA empty lists | Resolved | 9 |
| Gene-set Entrez release | Partially resolved (rule stated; release unpinned) | 9 |
| Discovery STOP propagation | Resolved | 11 |
| G1b undefined beyond GSE63060 | Partially resolved (Illumina cohorts defined; GSE99039 unresolved) | 5.2 |
| G2 undefined for GPL570 | Unresolved (dependency) | 5.2 |
| G3 cross-platform probe-set difference | Resolved (disclosed) | 5.2–5.3 |
| Camera internal statistic | Unresolved (not verifiable locally) | 9 |
| Estimated-weights basis invariance | Unresolved (not verifiable locally) | 4.4 |
| B8: external dependencies (D19, D8, GPL570 sex probes, D0) | **Unresolved** (external) | 14.3 |
