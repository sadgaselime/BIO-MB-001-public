# BIO-MB-001 — Statistical Analysis Plan, DRAFT v4 (Phase 3B, targeted refinement of v3)

**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen. No decision (D0–D22) is approved, and
no approval-gate condition is passed or improved by this revision.** v1, v2 and v3 are preserved
unchanged.

v4 revises only the seven areas listed in §0. Every other section of
`reports/phase3b/v3/STATISTICAL_ANALYSIS_PLAN_DRAFT.md` carries over unchanged and is cited as
**[v3 §n]**. That includes:

- the scientific question, estimand and discrepancies H1–H9 ([v3 §2]);
- R2 cohort reconciliation ([v3 §3]);
- GSE140829 mapping ([v3 §7]);
- specificity ([v3 §8]);
- the remaining sensitivity analyses ([v3 §9]);
- the metadata-only check list ([v3 §12]).

Nothing has been executed for v4:

- no expression value was read;
- no QC statistic, model, gene list, pathway result or signature exists;
- no sample is excluded or relabelled;
- no new local evidence was gathered — v4 is reasoning and specification only.

Labels: **[EVIDENCE]** verified local fact or cited report · **[REASONING]** statistical argument
given here (standard results are named, not cited as verified sources) · **[PROPOSED]** suggested
choice requiring approval · **[PROPOSED (no source)]** suggested value with no empirical or
literature basis · **[DECISION NEEDED]** · **[UNRESOLVED]** · **[BACKGROUND]** general domain
knowledge not verified in this project.

---

## 0. Change log from v3

| # | Section | Change |
|---|---|---|
| 1 | R8 sex check (§1) | Exact split rule, including tied values and degenerate splits. Graded evidence levels: a single-axis call is never equivalent to two-axis concordance. Minimum separation stays unresolved. Discordance is explicitly not proof of misidentification |
| 2 | R9 outliers (§2) | Batch-structure caveat expanded. **The R9 role is fixed before Stage A: proposed default is QC reporting plus sensitivity-only exclusion — flags never remove arrays from the primary analysis.** MAD failure behaviour restated |
| 3 | Identifiability (§3) | The term-order rule is replaced by a deterministic, order-independent design-matrix procedure based on projection and SVD rank. The group contrast is tested first. The stop rule is preserved; c₁–c₃ remain unresolved |
| 4 | Gene-level inference (§4) | The v3 claim that diagnosis-blind highest-mean selection "keeps selection valid" is withdrawn and replaced by a conditional argument with stated assumptions and failure modes. Four gene-level options are compared. **No option is declared valid by default; D6 requires approval** |
| 5 | Composite score (§5) | Exact formulas for two-directional and one-directional signatures; handling of unmeasurable genes; proposed coverage rule for score assessability (values require PI approval); the lock stays fixed across cohorts |
| 6 | Direction concordance (§6) | Within-batch label permutation is judged **not justified** as a confirmatory test when age and sex are covariates. **C-b is downgraded to descriptive** pending methodological approval of a specified alternative |
| 7 | Pathways (§7) | One primary exploratory method and one secondary method, with matched statistic, universe, size filter and multiplicity family. Versions remain unpinned |
| 8 | Register (§8) | D5, D6, D7, D12, D14, D15, D20 and D22 updated (marked †). No IDs added, removed or merged |

---

## 1. R8 sex-consistency check — refined (replaces [v3 §4.2] steps A2–A5; A0–A1 unchanged)

Inputs, the probe sets, Stage A/B separation and the "not externally validated" statement are
unchanged from [v3 §4.1–4.2]. X_i is the XIST value; Y_i is the median of the median-centred Y probes.

### 1.1 A2 — per-axis split rule (deterministic)

Apply the rule separately to the X values and the Y values. Use only arrays that are finite on that
axis (non-finite arrays are "unassessable on this axis").

1. Sort the n finite values: v₍₁₎ ≤ … ≤ v₍ₙ₎.
2. **Admissible split points:** indices s with v₍ₛ₎ < v₍ₛ₊₁₎ (strict inequality), n_low = s ≥ n_min
   and n_high = n − s ≥ n_min.
   - Because a split may fall only between *distinct* values, **tied values are always in the same
     class**.
   - n_min = 5 [PROPOSED (no source)].
3. For each admissible s, compute the pooled within-class sum of squares:
   W(s) = Σ_low (v − mean_low)² + Σ_high (v − mean_high)².
4. Choose s* minimizing W(s). **Ties in W:** values within 10⁻¹² × W_total of the minimum
   [PROPOSED (no source)] are treated as tied, where W_total is the sum of squares about the overall
   mean. Among tied candidates, choose the smallest s. The tolerance makes the choice independent of
   floating-point summation order.
5. Threshold t = (v₍ₛ*₎ + v₍ₛ*₊₁₎) / 2. No observed value can equal t, because t lies strictly between
   two distinct adjacent values. High = v > t; low = v < t.
6. **Degenerate axis** (classed non-separating, no calls from that axis):
   - fewer than 2 distinct values;
   - no admissible split (for example, n < 2·n_min, or all but fewer than n_min values tied);
   - W_total = 0.

### 1.2 A3 — separation measure

D = |mean_high − mean_low| / sqrt((sd_high² + sd_low²)/2), computed at s*.

- If both class SDs are 0 and the means differ, D = +∞. This is recorded as "perfectly separated"
  (finite-sample artefact possible; listed).
- If D is undefined, the axis is non-separating.
- **The minimum D for an axis to count as separating remains [UNRESOLVED / DECISION NEEDED, D5].**
  No published or local evidence gives a validated value for these deposited, VST-scaled data. The
  draft does not invent one.
- Until a value is approved, R8 cannot be executed. D is reported, but no axis can be classed as
  separating.

### 1.3 A4 — evidence levels for expression-derived sex

| Axes usable | X-call / Y-call | Expression-derived sex | Evidence level |
|---|---|---|---|
| Both | Female-type / female-type | Female pattern | **Two-axis concordant** (strongest available) |
| Both | Male-type / male-type | Male pattern | **Two-axis concordant** |
| Both | Calls disagree | Ambiguous | — |
| X only | Female- or male-type | Female- or male-type | **Single-axis (X)** — weaker |
| Y only | Female- or male-type | Female- or male-type | **Single-axis (Y)** — weaker; see note |
| Neither | — | Not assessable | — |

The evidence level is carried into every downstream table. A single-axis call is never reported as,
or pooled with, a two-axis call.

**Note on Y-only calls [BACKGROUND, not verified here].** Mosaic loss of chromosome Y in blood cells
is reported to be common in older men. It lowers Y-gene expression and can make a genuine male sample
look female-type on the Y axis. The AD cohorts are elderly. Y-only calls (and the "X low, Y low"
ambiguous pattern) therefore carry particular uncertainty.

### 1.4 A5 — comparison with recorded sex and proposed Stage B handling (D22)

| Category | Definition | Proposed handling (not applied) |
|---|---|---|
| Concordant (two-axis) | Two-axis call = recorded sex | None |
| **Discordant (two-axis)** | Two-axis call ≠ recorded sex | Listed; proposed for the PI's exclusion review |
| Concordant (single-axis) | Single-axis call = recorded sex | None; evidence level reported |
| **Discordant (single-axis)** | Single-axis call ≠ recorded sex | Listed; **not proposed for primary exclusion**; excluded only in sensitivity S5 |
| Ambiguous | Two-axis calls disagree | As chosen beforehand under D22 (exclude / retain / sensitivity-only) |
| Unassessable | Missing recorded sex or no usable axis | Retained; listed |

**A discordance flag is not proof of sample misidentification [REASONING].** It is equally compatible
with:

- an error in the recorded sex field (metadata, not sample, error);
- sex-chromosome aneuploidy or mosaicism (e.g. XXY: X high, Y high; 45,X: both low) [BACKGROUND];
- loss of chromosome Y (above);
- sample mixture;
- technical failure;
- misclassification near the threshold.

Reports use "sex-check discordant", never "mislabelled" or "swapped". A discordant array's diagnosis
label is never altered.

---

## 2. R9 array-outlier check — refined (amends [v3 §4.3])

### 2.1 Algorithm (unchanged except where stated)

Steps A0–A5 are as in [v3 §4.3]:

- non-finite handling;
- median-then-Fisher statistic;
- near-identical pairs referred to D18;
- k = 3 provisional.

**MAD rule restated:** M = median(z_i), S = 1.4826 × median|z_i − M| over arrays with finite z_i.
If S = 0 or S is non-finite, R9 is **not applicable** for that cohort:

- no array is flagged;
- the condition is reported;
- no substitute scale estimator is used unless separately approved.

Arrays classed as numerical failure (zero variance; non-finite m_i; |m_i| ≥ 1; more than half their
pairs omitted) are listed separately from R9 flags.

### 2.2 Batch structure [REASONING]

A global correlation statistic measures similarity to *all* arrays. Systematic chip or batch shifts
(hybridization day, scanner, reagent lot) lower the correlation of every array on an affected chip
with the rest of the cohort. R9 flags can therefore:

- mark whole chips or batches rather than individual defective arrays;
- miss a defective array on a chip whose arrays are all shifted together;
- correlate with diagnosis wherever chip and diagnosis are imbalanced.

GSE63060 has about 11 arrays per chip (329 / 29) [EVIDENCE: counts from [v2]]. That is too few for
reliable within-chip robust statistics in many chips. Within-chip centring before correlation removes
chip shifts but also removes any diagnosis signal aligned with chip composition.

There is no batch-neutral version of R9 without trade-offs. This is a limitation, not a solved
problem.

### 2.3 Role of R9 flags — fixed before Stage A [PROPOSED; D22]

| Option | Primary analysis | Dependence on data-driven, possibly diagnosis- or batch-correlated flags | Main risk |
|---|---|---|---|
| (i) QC reporting only | All arrays | None | Defective arrays inflate variance or bias; nothing tests their influence |
| (ii) Primary exclusion | Flagged arrays removed | **Highest**: the primary population depends on a statistic that may track batch or diagnosis | Diagnosis- or batch-correlated selection of the analysed sample |
| **(iii) Reporting + sensitivity-only exclusion (proposed default)** | All arrays | **None in the primary analysis**; sensitivity S5 shows influence | Genuine technical outliers remain in the primary analysis |

**Why (iii) is proposed.** It is the least outcome-dependent option that still assesses influence:

- The primary population then does not depend on R9 at all.
- Option (i) gives the same primary analysis but no influence assessment.

**Limitations of (iii):**

- Real outlying arrays may reduce power or, if imbalanced by group, bias the primary estimate.
- The primary analysis is protected only partially by array-quality weighting (S6), and S6 is itself
  a sensitivity analysis.

**Rules for (iii):**

- **Numerical-failure arrays** are not R9 flags. They cannot contribute valid data, and their
  exclusion from the primary analysis is a separate D22 item, proposed as "exclude, listed".
- Under (iii), Stage B is purely descriptive: flag counts by chip/batch and by diagnosis. No
  Stage B response alters the primary population. The v3 Stage B response list (proceed / within-chip
  recompute / sensitivity-only) is withdrawn for R9.
- If (ii) is chosen instead, the v3 response list and a definition of "concentrated flags" are
  required before Stage A.
- The role is chosen and recorded **before** Stage A runs. It is never chosen after seeing flag
  counts or any association result.

---

## 3. Model identifiability — deterministic procedure (replaces [v3 §5.3])

The definitions and the metadata-only checks M1–M8 are unchanged from [v3 §5.1–5.2]. None has been
run.

### 3.1 Notation

- n samples in the model.
- g = group indicator column (AD = 1, CTL = 0).
- N = nuisance block: intercept, age, sex and chip indicators (all chip levels coded as indicators;
  redundancy permitted), plus any sensitivity terms. Columns are named but **their order plays no
  role** below.
- Rank tolerance [PROPOSED]: τ = max(n, p) · σ_max · ε_machine, where σ_max is the largest singular
  value of the matrix concerned. This is the conventional numerical-rank tolerance.

### 3.2 Procedure

1. **Nuisance column space.**
   - Compute the SVD of N.
   - r_N = number of singular values > τ.
   - Q_N = the r_N left singular vectors for those singular values (an orthonormal basis of span(N)).
     It is unique as a subspace, whatever the column order.
2. **Group estimability (tested first).**
   - Residualize the group indicator: g̃ = g − Q_N Q_Nᵀ g.
   - Compute R²_g = 1 − ‖g̃‖² / ‖g − ḡ‖². This is the proportion of group variation explained by the
     nuisance terms, and N contains the intercept.
   - The contrast is **estimable** iff ‖g̃‖ > τ_g, where τ_g = τ computed for [N, g]. Equivalently,
     the SVD rank of [N, g] equals r_N + 1.
3. **If not estimable → STOP** ([v3 §5.3] stop rule preserved):
   - report that the primary disease contrast is not estimable under the approved design;
   - report M1–M6;
   - fit no model.
4. **Minimum information.** VIF_g = 1 / (1 − R²_g), plus the M2 mixed-chip counts.
   - If any approved threshold fails (mixed chips < c₁; AD or CTL on mixed chips < c₂;
     VIF_g > c₃) → **STOP** as in step 3.
   - **c₁–c₃ remain unresolved [DECISION NEEDED, D7].** No local evidence or validated source gives
     values. The checks cannot be executed until the PI sets them.
5. **Aliased nuisance terms (detected, not resolved by term order).**
   - The null space of N (right singular vectors with singular values ≤ τ) lists every exact linear
     dependency among the named nuisance columns. Each dependency is reported by the columns it
     involves (for example "chip indicators sum to intercept", or "site set ⊂ chip set").
   - Handling: the model is fitted with design [Q_N, g] (or any full-rank basis spanning the same
     space) in place of the redundant N.
   - **Invariance [REASONING: Frisch–Waugh–Lovell theorem; standard linear-model result].** For the
     least-squares fit, the following depend on N only through span(N), so they are identical
     whichever redundant columns are dropped or however the basis is chosen:
     - the group coefficient;
     - its standard error;
     - the residuals;
     - the residual degrees of freedom n − r_N − 1.

     The same holds for weighted least squares with fixed weights (S6), using the weighted
     projection.
   - Consequence: **only the group coefficient is interpreted or reported.** Nuisance coefficients
     involved in a dependency are not identifiable and are not reported.
6. **Near-aliasing of nuisance terms** (singular values just above τ) does not affect group
   estimability (step 2 handles it). It is reported as the condition number of N for numerical
   transparency.
7. **The same procedure** applies to every sensitivity design and every validation or specificity
   cohort. For a validation cohort, STOP means "not assessable", not a negative result.

**Implementation note [REASONING].** Some software silently drops aliased coefficients in
column-order fashion. To avoid order dependence, an approved implementation passes the full-rank
basis from step 5 explicitly, and must verify that rank([basis, g]) = r_N + 1.

---

## 4. Representative probe and gene-level inference — reassessed (replaces [v3 §6.1 step 5, §6.2 rows 2–3 and the "accepted consequence" paragraph])

### 4.1 Withdrawn claim

v3 stated that the highest-mean rule "is diagnosis-blind, which keeps the selection valid". **That is
withdrawn.** Being diagnosis-blind does not by itself guarantee that selection is statistically
independent of the selected probe's test statistic.

### 4.2 When highest-mean selection is independent of the test statistic [REASONING]

Setting:

- For one probe in a linear model with an intercept, the sample mean across all samples in the model
  is ȳ = (1/n)·1ᵀy.
- Because 1 lies in the column space of X, the covariance between ȳ and any non-intercept least-squares
  coefficient is zero: (X'X)⁻¹X'1 is the intercept unit vector.
- ȳ is also orthogonal to the residual space.

Under the following assumptions, the vector of all probe means for a gene is **independent** of the
vector of their group coefficients and residual variances. Selecting by highest mean then leaves the
selected probe's null distribution unchanged:

- (a) errors are Gaussian;
- (b) errors are independent across samples;
- (c) each sample has the same error covariance across probes, so variance does not differ by
  diagnosis or covariates;
- (d) the gene-level null hypothesis holds: no probe of the gene is associated with group.

This is the same logic behind "independent filtering" by overall mean (discussed in the literature,
e.g. Bourgon, Gentleman & Huber, PNAS 2010 — **not reviewed locally**).

**Where the argument fails or weakens:**

| Failure | Effect |
|---|---|
| Group-dependent variance (heteroscedasticity) | Cov(ȳ, contrast) ≠ 0 when n_AD ≠ n_CTL (145 vs 104); selection is no longer exactly independent |
| Non-Gaussian errors | Uncorrelated ≠ independent; the dependence is likely small but unquantified |
| Moderated statistics | limma-trend's prior variance depends on the mean, so selection by mean changes which prior applies. Modest, but not covered by the exact argument |
| Selection set ≠ model set | Must use exactly the samples and design in the model; a different set (e.g. adding MCI) changes the argument (see G1b) |
| Under the alternative | With unequal group sizes, a probe up-regulated in the larger group has a higher overall mean, so selection leans towards probes that rise in AD (the larger group). This does not inflate type I error under the gene-level null, but biases *which* probe represents an associated gene |

**What the gene-level hypothesis means under any representative-probe rule.** "The representative
probe is not associated with group." A non-significant gene cannot be described as "not associated":
its other probes are untested at gene level.

### 4.3 Options for the gene-level unit (D6) [DECISION NEEDED]

| Option | Rule | Independence from the test | Main advantages | Main limitations |
|---|---|---|---|---|
| **G1** (v3 rule) | Highest mean across the samples in the model; ties → probe ID ascending | Exact only under (a)–(d) in §4.2 | Simple; favours expressed probes | Conditional validity; biased probe choice under the alternative; cohort-specific choice can pick different probes per cohort |
| **G1b** | Highest mean across arrays **not** in the contrast (GSE63060 MCI, n = 80); ties as G1 | Independent of the AD–CTL data under sample independence (disjoint samples). Joint normalization creates a weak, unquantified link | Selection data disjoint from test data | Depends on MCI composition; smaller n; no analogous disjoint set in some cohorts |
| **G2** | Fixed external rule from annotation alone, set before data: e.g. a probe-quality grade from the pinned resource, then probe ID ascending | Fully independent (no data used) | Same probe across Illumina cohorts where available; transparent | Needs a resource offering quality grades (**availability unverified**; D8); may choose probes not expressed in blood, losing power |
| **G3** | Gene-level summary: per sample, the mean of all one-to-one probes of the gene (deposited scale), then fit the model to the summary | No selection step, so no selection dependence | Uses all probes; no choice of representative | Changes the estimand to "average probe signal"; dilutes isoform-specific or poor-probe signals; probe- and gene-level results can disagree |
| (G4, noted) | Gene-level combination of probe p-values (e.g. Simes) | Valid under positive dependence | Null = "no probe associated", closer to a gene concept | Gives no single effect or direction for the signature or score; would need G1–G3 alongside |

**Status:** the evidence does not select a unique option.

- G2 and G3 avoid reliance on the §4.2 assumptions; G1 and G1b rely on them to different degrees.
- G3 is the only option that needs no new resource and no selection step, but it redefines the
  gene-level quantity.
- **No default is declared valid.** If the PI wants a provisional working choice for drafting, G3
  (with G1 as sensitivity S8) is the least assumption-dependent option available without new
  resources. That is a reasoned leaning, not an approved choice.

**Downstream consistency (whichever option is approved):**

- The same option type is used in discovery, signature construction, validation (each cohort applies
  the same rule to its own data, or the identical probe for G2), and pathways.
- The gene-level BH family is "all Entrez genes with a gene-level unit tested".
- Probe-level BH (all tested probes) remains a separate family ([v3 §6.1]).

---

## 5. Composite replication score — exact definition (replaces the C-c rows of [v3 §6.3, §6.5])

### 5.1 Notation and lock

- U = locked up-genes; D = locked down-genes. Fixed at lock and never changed for any cohort.
- For validation cohort c, each locked gene is assigned to one category of [v2 §9.3]:
  - unmapped;
  - absent from the Series Matrix;
  - excluded by approved feature QC;
  - **measurable**.

  One further category is added: **constant in cohort** (SD = 0 or non-finite across the score
  samples).
- U_c ⊆ U and D_c ⊆ D are the measurable genes.
- Score samples: all eligible samples in cohort c's AD–control contrast, after R-rules, approved QC
  and R2-COV.

### 5.2 Per-gene standardization (diagnosis-blind)

For each measurable gene k, take x_ki, the gene-level unit under the approved D6 option. Then
z_ki = (x_ki − mean_k) / sd_k, with the mean and SD (n − 1 denominator) over all score samples
regardless of diagnosis.

### 5.3 Score

| Locked signature | Score for sample i | Expected sign under replication |
|---|---|---|
| Two-directional (U, D non-empty) | S_i = mean_{k∈U_c} z_ki − mean_{k∈D_c} z_ki | Positive (AD > CTL) |
| Up-only (D empty at lock) | S_i = mean_{k∈U_c} z_ki | Positive |
| Down-only (U empty at lock) | S_i = − mean_{k∈D_c} z_ki | Positive |

- All measurable genes are weighted equally.
- Unmeasurable genes are **dropped, not imputed, and never replaced** by other genes.
- **Test:** S ~ group + the cohort's covariates (identifiability per §3), with a one-sided test of the
  group coefficient > 0. Report the estimate with its 95% CI.

### 5.4 Coverage rule for score assessability [PROPOSED (no source); requires PI approval, D15/D20]

The score in cohort c is **assessable** only if all of the following hold:

1. ≥ 50% of all locked genes are measurable: |U_c| + |D_c| ≥ 0.5 (|U| + |D|).
2. For each direction that is non-empty at lock: ≥ 50% of that direction's locked genes are
   measurable, **and** at least min(5, number locked in that direction) are measurable.
3. Consequently, a two-directional lock whose up- or down-component has zero measurable genes in
   cohort c is **not assessable as locked**. It is not silently converted to a one-directional score.
   A one-directional version may be reported only as a labelled descriptive analysis.

- **Rationale [REASONING]:** a majority of each locked component should be present so that the
  cohort's score represents the locked signature, not an arbitrary subset.
- The 50% and 5 values are conventions. No evidence establishes a unique threshold, so they require
  approval.
- If the score is not assessable, the result is "composite replication not assessable in cohort c",
  never "not replicated".

### 5.5 Coverage reporting (every cohort)

- Counts and gene lists by category and direction.
- The proportion measurable overall and per direction.
- Whether the coverage rule passed.

The lock is the same file (same checksum) for every cohort. Coverage differences between GSE140829 and
GSE63061 are reported side by side.

---

## 6. Direction concordance (C-b) — reassessed and downgraded (replaces the C-b column of [v3 §6.5])

### 6.1 Target null hypothesis

- Statistic T = the proportion of measurable locked genes whose covariate-adjusted validation effect
  has the locked sign.
- The relevant null: **H0: β_k = 0 for every measurable locked gene k in the validation model
  (group + age + sex + batch)**, i.e. no association with diagnosis conditional on the covariates.
- Under H0, genes are correlated, so T is not Binomial(m, ½).

### 6.2 Why within-batch label permutation is not justified here [REASONING]

Permuting diagnosis labels within batch is exact under a *stronger* null: diagnosis is independent of
expression, age and sex jointly within batch. Labels are then exchangeable within batch.

In the observed data, diagnosis is associated with age and sex:

- GSE63060 AD vs CTL differ in mean age and in sex proportion ([2B] §3);
- validation-cohort balance is not yet tabulated.

Permuted labels lose that association, so the permutation distribution of the covariate-adjusted
statistic does not represent the conditional null H0. The test is then not guaranteed to have its
nominal size: it can be conservative or anti-conservative depending on the covariate structure.

**Strata with one diagnosis:** labels in such a stratum are fixed under within-stratum permutation.
They add no permutation variation. If most samples are in single-diagnosis strata, the number of
distinct permutations can be too small for the intended resolution.

### 6.3 Candidate procedures (none approved)

| Candidate | Null tested | Assumptions | Concerns |
|---|---|---|---|
| (P1) Restricted label permutation within batch × sex × age-band strata | Exchangeability within strata | Within-stratum exchangeability; age banding approximates age adjustment | Residual confounding within age bands; many single-diagnosis strata likely; band choice is arbitrary |
| (P2) Freedman–Lane residual permutation, the same row permutation for all genes (within batch blocks) | Conditional H0 (approximately) | Exchangeable errors of the reduced model; approximate, not exact, in finite samples | Sensitive to heteroscedasticity; needs validation of the implementation |
| (P3) Rotation test of the covariate-adjusted model (as in limma's rotation gene-set procedures; documentation not reviewed locally), with T as the statistic | Conditional H0 under Gaussian errors | Gaussian, homoscedastic errors | Exactness depends on normality; T computed on rotated data needs implementation review |

**Status: [UNRESOLVED].** None of P1–P3 can be specified here with confidence that it delivers a
valid confirmatory p-value for T in these cohorts.

### 6.4 Downgrade [PROPOSED]

- **C-b is descriptive only:**
  - report T;
  - report the numbers of concordant and discordant genes by direction;
  - report the sign-test value labelled "assumes independence — descriptive".
- **No confirmatory p-value is claimed for C-b** unless the PI approves one of P1–P3 (or another
  procedure) after methodological review (D12).
- **Hierarchy (D20):** C-c primary; C-a secondary; C-b descriptive. This changes v2/v3, which had C-b
  as secondary or as an alternative primary.

---

## 7. Pathway analysis — primary vs secondary (replaces [v3 §6.6]; exploratory throughout)

| Element | Primary exploratory method | Secondary method |
|---|---|---|
| Method | Competitive gene-set test on the gene-level expression data under the discovery model (camera-type), allowing for inter-gene correlation | Over-representation analysis (one-sided hypergeometric / Fisher test) |
| Input data | Gene-level matrix (one row per Entrez gene, D6 option) for the samples in the discovery model; same design, contrast and weights as the gene-level discovery model | Binary gene lists: gene-level q < 0.05 (D15) and effect > 0 (up list) or < 0 (down list), before the 200 cap |
| Statistic | Moderated t of the gene-level unit for the AD − CTL contrast (computed by the method from the model) | Membership in the up or down list |
| Gene universe | Entrez genes with a gene-level unit tested in discovery (one-to-one probes only, after feature rules) | **Identical universe** |
| Set preparation | Intersect each set with the universe, then keep sets with 15–500 universe genes [PROPOSED] | **Same filtered collection** as the primary (sets are not re-filtered on list overlap) |
| Inter-gene correlation | Must be specified (estimated or fixed) before execution [DECISION NEEDED, D14] | Not modelled; secondary results are treated as anti-conservative |
| Direction | One two-sided p per set, with direction reported | Separate tests for the up and down lists |
| Multiplicity family | BH within each collection (e.g. GO BP; Reactome), separately | BH within each collection × list (up, down), separately |
| Role | Main exploratory pathway report | Supporting description; never used to rescue or overrule primary results |

**Rules:**

- Results are not combined across methods or collections.
- Collections, versions and software remain **unpinned** until D8 and D14 are approved ([v2 §11.2]).
- Interpretation limits (blood cell composition, redundancy, no brain mechanism) as in [v2 §11.1].

---

## 8. Decision register (D0–D22; none approved)

Entries not listed are unchanged from [v3 §10]. † = changed in v4.

| ID | Question | Evidence | Proposed default | Alternatives and consequences | Additional data? | Depends on | Approval before implementation |
|---|---|---|---|---|---|---|---|
| D5 † | QC algorithms and parameters | §1–2 | Split rule §1.1 (n_min = 5; tie tolerance 10⁻¹²); evidence levels §1.3; R9 as [v3] with explicit MAD failure | **Minimum separation D unresolved; R8 cannot run until set.** k, n_min and tolerances are conventions | No | D22 | Yes |
| D6 † | Annotation and gene-level unit | §4 | **No default declared valid.** Options G1, G1b, G2, G3 (G4 noted); leaning G3 with G1 as sensitivity, unapproved | The options differ in estimand, independence assumptions and resource needs | Yes for G2 (resource) | D8 | Yes |
| D7 † | Identifiability procedure and thresholds | §3 | SVD/projection procedure; group tested first; STOP if not estimable or below thresholds; aliased nuisance handled via basis (invariant) | **c₁–c₃ unresolved** | No (M1–M8 first) | D4, D8 | Yes |
| D12 † | Replication criteria | §5–6 | C-c as §5; C-a per gene; **C-b descriptive** | Approve P1, P2 or P3 to restore an inferential C-b | Methodological review | D15, D20 | Yes |
| D14 † | Pathway framework | §7 | Primary camera-type competitive test; secondary ORA; matched universe and filters | Inter-gene correlation handling; collections; versions unpinned | Yes | D6, D8 | Yes |
| D15 † | Threshold, cap, coverage | §5.4; [v3 §6.3] | q < 0.05; cap 200 unique genes; coverage rule 50% overall and per direction, ≥ min(5, locked) per direction | Other coverage values; no rule (risks unrepresentative scores) | No | — | Yes |
| D20 † | Replication hierarchy | §6.4 | C-c primary; C-a secondary; C-b descriptive | C-b inferential only after D12 approval | No | D12 | Yes |
| D22 † | QC review and role of flags | §1.4, §2.3 | R9 role (iii): reporting + sensitivity-only; numerical failures exclude (listed); single-axis R8 discordance sensitivity-only; ambiguous option chosen beforehand | (i) reporting only; (ii) primary exclusion (most outcome-dependent; requires a "concentrated" definition) | No | D5 | Yes |

The other entries (D0–D4, D8–D11, D13, D16–D19, D21) are unchanged from [v3 §10].

**Approval gate ([3A] §5): unchanged.**

- **Not satisfied:** G1, G2, G5, G7, G8.
- **Partially satisfied:** G3, G4, G6, G9.

---

## 9. Remaining items requiring the PI's approval or still unresolved

### 9.1 Scientific or methodological decisions (evidence does not determine a unique answer)

1. **D5:** the minimum separation D for R8 (unresolved; R8 cannot run without it); n_min; tolerances; k.
2. **D22:** the R9 role (proposed iii); the ambiguous-sex option; handling of numerical-failure arrays.
3. **D7:** the minimum-information thresholds c₁–c₃.
4. **D6:** the gene-level unit (G1 / G1b / G2 / G3) and the annotation resource.
5. **D15:** the coverage-rule values (50%, 5), the FDR level and the cap.
6. **D12 / D20:** whether any inferential C-b procedure (P1–P3) is adopted; the hierarchy.
7. **D14:** inter-gene correlation handling; gene-set collections.
8. Unchanged from v3: D1, D4, D11, D13 (δ), D16, D17, D18, D21.

### 9.2 Dependent on external information or approval to install software

D0, D8, D9, D10, D19.

### 9.3 Unresolved methodological points recorded rather than forced

| Point | Why it stays unresolved |
|---|---|
| A valid confirmatory test for C-b under covariate adjustment | §6.3 |
| Quantified dependence between G1 selection and the moderated statistic under heteroscedasticity | §4.2 |
| A batch-neutral R9 statistic | §2.2 |
| An externally validated R8 separation criterion | §1.2 |
