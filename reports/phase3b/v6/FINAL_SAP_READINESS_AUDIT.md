# BIO-MB-001 Phase 3B — Final SAP readiness audit of draft v6 (read-only)

**Audited file:** `reports/phase3b/v6/STATISTICAL_ANALYSIS_PLAN_DRAFT.md`
(SHA-256 `e060703879ae8697d375d141f209c09ce3c4c37ba928237bab3552803e79fad0`; 890 lines).

**Read for this audit:**

- the complete v6 text;
- the v6 active-text map (v6 §0.1) and the retained v5 sections it names (v5 §3.1–3.5, §4.1, §4.3,
  §4.4, §5.3, §9);
- the v5 decision register [REG] and the v4 scientific consistency audit [AUD]. Both were read earlier
  in this session; their checksums are unchanged (§10);
- the inherited v2 sections whose status the map leaves in question: v2 §7.5 (v2:351–364), §9.5
  (v2:457–462) and §9.6 (v2:464–469).

**Status:**

- Audit only. v6 is not modified and no v7 is created.
- **No decision D0–D22 is approved. The approval-gate status is unchanged** (v6:5–8).
- No analysis, QC statistic, metadata pass/fail check, model, gene selection, pathway analysis or
  signature lock was run.
- No expression value or sample-level result was inspected.

**Conventions:**

- **FACT** = what the text says (`v6:L`, `v5:L`, `v2:L`).
- **ASSESSMENT** = the auditor's statistical reasoning. It is not externally validated and no
  citation is added.
- **ACTION** = the smallest next step.

**Readiness classes:**

| Class | Meaning |
|---|---|
| **PI** | Ready for PI approval |
| **EXT** | Requires external evidence or authorization |
| **FIX** | Requires a technical or statistical correction to the text |
| **OPT** | Concerns an optional sensitivity analysis only |

---

## 1. Highest-priority remaining blockers

| # | Blocker | Where | Class |
|---|---|---|---|
| 1 | **No error-rate target is stated for the replication hierarchy.** Whether C-c and C-a together control the intended error rate cannot be judged | v6 §8.8 (v6:575–580) | **UNRESOLVED** → PI + FIX |
| 2 | **Validation-cohort covariates are not in the lock or in Tier A.** They exist only in inherited v2 §9.6, so they could be set after validation data are visible | v6:528, 452–459, 119–126; v2:466–469 | FIX |
| 3 | **The G1 independence claim is overstated.** It covers S5 as a "subset", but S5e (include variant) and S5f re-include arrays outside S_c. It is silent about designs that omit unit effects (S3) and about re-normalized or re-weighted data (S10, S6) | v6 §6.3–6.4 (v6:365, 382–391) | FIX (bears on the D6 decision) |
| 4 | **Re-inclusion sensitivities have no precedence rule.** S5e, S5f, S14 and S16 could reintroduce an array that is excluded for a *different* reason | v6:701–703, 712, 714, 731 | FIX |
| 5 | **R8 variant V-A is incompatible with D5 option (c)**, and with an indefinitely unset D_min. This could block the study permanently, and the plan has no compatibility rule | v6:123, 179–188; v5:221–234 | FIX |
| 6 | **Status of v2 §7.5 is undefined.** It holds reporting requirements, assumption diagnostics and a "failure rule", and is neither active nor superseded in the map | v6 §0.1 (v6:45–67); v5:71–82; v2:351–364 | FIX |
| 7 | **No positive specificity claim is possible without δ, and δ's scale is undefined.** This is implied but not stated | v6:128–129, 663, 667–670 | FIX (interpretation) |
| 8 | Unset scientific values and external items (pre-existing, not new): D_min; c₁–c₃; D6 option; R8 variant; W1/W2; δ; D0, D8, D19, GPL570 annotation | v6 §14 (v6:817–854) | PI / EXT |

---

## 2. G1 probe-selection validity (D6)

### F1 — S5e (include variant) and S5f are not subsets of S_c · **FIX**

**FACT.**

- §6.4 states the independence argument for "any model fitted to a sample subset M ⊆ S_c". It lists
  as covered "sensitivity subsets (S1, S5, S12, S15)" (v6:376, 386).
- For GSE63060, S_c is the primary population: eligible AD + CTL after the §3.5 exclusions actually
  applied (v6:327). Those exclusions include R8 two-axis discordant arrays (v5:279).
- S5f re-includes those arrays (v6:702). S5e includes ambiguous arrays when the primary option
  excludes them (v6:701).
- The §6.3 exception row covers only S14 and S16 (v6:365); the §6.4 exception names only S14 and S16
  (v6:389–391).

**ASSESSMENT.**

- S5f, and S5e in its "include" form, fit models to sets that are **not** subsets of S_c.
- Listing "S5" as covered is therefore **incorrect** for those variants. The same limitation as for
  S14/S16 applies to them.

**Why it matters.** The audit trail would claim independence where it is not established.

**ACTION.** Add S5e (include variant) and S5f to the §6.3 exception row and to the §6.4 exception. In
v6:386, restrict "S5" to S5a–S5d, S5e (exclude variant) and S5g.

### F2 — The independence argument assumes all shared-unit variation is in the mean model · **FIX**

**FACT.** §6.4 assumes "Gaussian errors; sample rows independent with a common across-probe error
covariance" (v6:375–376). S3 includes "site instead of chip" (v6:697).

**ASSESSMENT.**

1. **The algebra is correct under the stated assumptions.**
   - For a model on M ⊆ S_c with an intercept, the contrast weight vector c and the residual
     projector are supported on M and orthogonal to 1_M.
   - Hence 1_{S_c}ᵀc = 0, and the same holds for residual directions.
   - With i.i.d. Gaussian rows this gives independence.
   - The same holds for least squares with **fixed** weights, since cᵀ1 = 0 still.
2. **"Rows independent" holds only if chip/batch effects are part of the mean.** Under the primary
   design (chip fixed effect) that is the case. Under a design that **omits** the unit term (S3
   "site instead of chip"), shared chip variation becomes correlated error. Then
   Cov(1ᵀe, cᵀe) = 1ᵀΣc, which is generally ≠ 0 for block-structured Σ, and the argument fails.
3. The same applies to any validation or specificity design in which shared processing variation is
   not captured by the batch term.

**Why it matters.** §6.4 implies coverage of "sensitivity subsets" generally, without this condition.

**ACTION.** State the condition explicitly: all shared-unit effects are in the mean model. List S3's
"site instead of chip" variant as **not covered**.

### F3 — S6 (estimated weights) and S10 (re-normalized values) are not covered · **FIX** (minor; **OPT** analyses)

**FACT.**

- S6 uses *estimated* array weights; their basis invariance is unverified (v6:704).
- S10 uses new values with the frozen probe identities (v6:363, 708).

**ASSESSMENT.**

- The §6.4 argument covers fixed weights only.
- For S10, the selection was made on the deposited values, while the test uses re-normalized values
  derived from the same raw measurements. The argument (one data matrix, orthogonal projections)
  does not apply, so independence is **not established**.
- §6.4 neither claims nor excludes these cases.

**ACTION.** List S6 and S10 as "independence not established".

### F4 — Freezing a selection is distinct from valid inference · **FIX** (wording)

**FACT.** The §6.4 heading is "Validity of frozen G1 selection" (v6:373). The caveats are retained
(v6:393–394).

**ASSESSMENT.**

- Freezing (§6.3) guarantees that each locked gene is measured by the same probe in every model of a
  cohort. It is a **reproducibility** property.
- §6.4 establishes only that, under stated assumptions, *selection* is independent of *that model's*
  test statistics. That is necessary but not sufficient for a valid gene-level test.
- Validity also requires a correct mean model, error assumptions and the moderation prior.
- It is also not established that the *population itself* is chosen independently of the outcome:
  - QC exclusions use expression (R8 sex probes; R9 correlations; D-3 duplicates; v5 §3.2–3.3,
    v6 §4).
  - These are diagnosis-blind, but no independence argument is given for them.
- The text does not overclaim this outright, but the heading invites the reading "valid".

**ACTION.** Retitle §6.4 "Conditions under which frozen G1 selection is independent of test
statistics". Add one sentence noting that expression-based QC selection is diagnosis-blind but not
shown to be independent of the test statistics.

**D6 status.** Not chosen here. G1 remains defensible *conditional* on the stated assumptions. G2 and
G3 avoid the selection question entirely (v5:443–449). G1b is undefined for GSE99039 and G2 is not
implementable for GPL570 (v6:328–329). → **PI** once F1–F4 are corrected; **EXT** for G2.

---

## 3. Replication multiplicity (D20)

### F5 — No error-rate target is stated · **UNRESOLVED** (PI + FIX)

**FACT.**

- Per cohort: C-c one-sided α = 0.05; C-a BH q < 0.05; C-b descriptive (v6:577).
- No gatekeeping: C-a is reported "whatever the C-c result" (v6:555).
- Across cohorts: separate α; Holm as the alternative (v6:578–580).
- The document never states which error rate the hierarchy is meant to control.

**ASSESSMENT.** As written, the procedures control the following, each under its own assumptions:

| Claim set | Error-rate control |
|---|---|
| C-c per cohort | Type I error at 0.05 (one-sided) |
| C-a per cohort | FDR at 0.05, under PRDS (v6:556) |
| C-c together with C-a | **No familywise control.** With no gate, a cohort can produce C-a claims while C-c fails |
| Across the two cohorts | No adjustment (separate questions; v6:578) |

This is coherent *if* the intended target is "per-question error control, with primary and secondary
claims interpreted separately". It is **not** coherent if the target is familywise control of all
replication claims. Because the target is unstated, **whether the hierarchy controls the intended
error rate cannot be determined** from the files.

**ACTION.** The PI states the target in D20 (for example: "per-cohort type I error for C-c;
within-cohort FDR for C-a, interpreted as secondary"; or "FWER across C-c and C-a via fixed-sequence
gatekeeping"). Add one sentence to §8.8.

### F6 — Validation covariates are not locked or approved in Tier A · **FIX**

**FACT.**

- C-c's estimand is "conditional on the cohort's approved covariates" (v6:528). C-a uses the "same
  covariates" (v6:548).
- The covariates appear only in inherited v2 §9.6: GSE140829 age_at_draw, Sex, batch (19); GSE63061
  age, gender, chip (34) (v2:466–469). v2 §9.6 is kept active via v5:76.
- The lock's validation specification lists the weighting, standardization, coverage, C-c, C-a, C-b
  and multiplicity, but **not the covariate set or their functional form** (v6:452–459).
- Tier A5 does not list validation covariates (v6:125).

**ASSESSMENT.**

- Validation decisions are not *fully* prespecified before validation results.
- The covariate set (and, for example, linear vs spline age) could be fixed or altered after
  validation data are loaded.
- Everything else in the replication specification is in the lock.

**ACTION.** Add "validation covariates and functional form (per v2 §9.6, or as approved)" to lock
item 5 (v6:452) and to Tier A5 (v6:125).

### F7 — C-a bounds and the scope of the moderation fit · **FIX** (minor)

**FACT.**

- C-a reports "β̂_g,c with its one-sided 95% bound in the locked direction" (v6:554). Claims use BH
  q (v6:552–553).
- The validation gene-level fit is "the cohort's gene-level fit (moderated t)" (v6:550). U has
  "rows = Entrez genes in T_c" (v6:320).

**ASSESSMENT.**

- The per-gene bound is unadjusted. It can exclude 0 when q ≥ 0.05, so reporting it alongside the
  q-based claim without a label invites misreading.
- Whether the cohort fit (and hence the empirical-Bayes prior) uses **all rows of U_c** or only the
  locked genes is implied by v6:320 but not stated for validation. The moderated t changes with that
  choice.

**ACTION.**

- Label the bounds "unadjusted".
- State: "the cohort fit uses all rows of U_c; BH is applied to the measurable locked genes only".

### F8 — C-c test and bound (verified)

**FACT.** H0: θ_c ≤ 0; one-sided α = 0.05; decision via the one-sided 95% lower bound; the two-sided
CI is descriptive (v6:530–533). The sidedness is fixed in the lock (v6:542).

**ASSESSMENT.**

- **Correct.** For a t-based coefficient test, p < 0.05 ⇔ L_c > 0.
- The two-sided CI is properly separated as a different question.
- Under the Holm alternative, the bounds are declared unadjusted (v6:580). Acceptable as labelled.

→ **PI** (D20 choices: W1/W2, sidedness alternative, gatekeeping, Holm).

---

## 4. Specificity test (D13)

### F9 — Q2 with Holm is redundant in the AD direction and penalizes the opposite direction · **PI** (consequence to record)

**FACT.**

- Q1 is two-sided (v6:635).
- Q2 is optional, one-sided in the AD direction, "if both Q1 and Q2 are approved, Holm across Q1 and
  Q2" (v6:636).

**ASSESSMENT.** For the same t-statistic: if θ̂ > 0, then p₂ = p₁/2; if θ̂ < 0, then p₂ = 1 − p₁/2.
With Holm at 0.05:

| Direction of θ̂ | Holm outcome |
|---|---|
| θ̂ > 0 | p₂ is compared to 0.025 (⇔ p₁ ≤ 0.05), then p₁ to 0.05. **Both are rejected exactly when p₁ ≤ 0.05.** Q2 adds no AD-direction decision beyond Q1 plus its sign |
| θ̂ < 0 | Q1 is the smaller p-value and is compared to 0.025. **Opposite-direction detection becomes stricter** (p₁ ≤ 0.025) |

So approving Q2 under Holm brings no AD-direction gain and costs power for the opposite direction.
The directional conclusion is already available from Q1's sign at ≤ α/2 error (v6:635; correct).

**ACTION.** Record this consequence in D13 before the PI decides on Q2. No option is chosen here.

### F10 — No positive specificity claim is defined; δ's scale is unspecified · **FIX** (interpretation) + **EXT** (δ justification)

**FACT.**

- The categories are association (same or opposite direction), "association not demonstrated", and
  equivalence via TOST with δ, which is "unavailable unless δ is justified and approved at Tier A5"
  (v6:660–663).
- "If δ is not justified and approved at A5, the equivalence category stays unavailable for this
  study" (v6:128–129).
- Non-significance is never reported as absence or specificity (v6:667–670).

**ASSESSMENT.**

- The non-significance safeguards are **correct and explicit**.
- **Consequence that is not stated:** without an approved δ, *no result in this study can support a
  claim that the AD signature is not associated with PD*. "Specificity" can then only be discussed as
  "association not demonstrated".
- δ's **scale** is not defined. Q1 is on cohort-specific score units (z-scale; v6:635, 640); per-gene
  effects are on the GPL570 (RMA log2) scale. A δ must name its scale to be prespecifiable.

**ACTION.** Add two sentences to §9.7–9.8: (i) without δ, no specificity claim is possible; (ii) δ, if
proposed, must state its scale (score units and/or per-gene log2).

### F11 — Verified elements

- Q1 null, sidedness and interval; the directional-error statement; per-gene two-sided BH within each
  contrast; contrast-level multiplicity (IPD primary; GPD/GU secondary, unadjusted, labelled; Holm
  alternative) (v6:635–648).
- The validation one-sided test is explicitly not reused (v6:623–629).
- Non-significance is not equated with absence (v6:662, 667–670).

**Minor note** (OPT/interpretive): z is standardized per contrast (v6:640), so CONTROL samples have
different z-values in different contrasts. This is acceptable, because comparisons across contrasts
are not made, but it should be stated.

→ **PI** for D13 (Q2, contrast multiplicity, GPL570 coverage values, GU interpretation), after F10.

---

## 5. R8/R9 and approval order

### F12 — Constants and roles are fixed before Stage A (verified)

**FACT.**

- "Every scientific rule, threshold and choice is approved in Tier A, before QC Stage A starts"
  (v6:111).
- A3 includes D5 (D_min or option a/b/c) and D22 (policies and R8 variant) (v6:123).
- The retained v5 prerequisites list probe lists, constants, D_min, k and the minimum count
  (v5:112–121).
- The R9 role is retained (v5:283).
- The R8 sequencing rule is retained (v5:217–219).

**ASSESSMENT.** No QC rule can run before its constants and role are approved, as written.

### F13 — V-A is incompatible with D5 option (c) and with an unset D_min · **FIX**

**FACT.**

- Under V-A, "Discovery primary … Waits for R8 completed (or not applicable)" (v6:183).
- D5 option (c) is "Do not run R8" (v5:229).
- R8 cannot start until D_min or (b)/(c) is chosen (v6:159).

**ASSESSMENT.**

- Approving V-A together with option (c) yields a permanent block: R8 is "not performed", so
  discovery never proceeds.
- V-A with D_min left unset and no option chosen yields an indefinite block.
- The plan states what proceeds under each variant (v6:181–188), **as requested**, but has no
  compatibility rule between D5 and D22.

**ACTION.** Add: "V-A requires D5 option (a) with an approved D_min, or option (b). The A3 approval
must be jointly consistent."

### F14 — The R8 status vocabulary cannot express an uninformative run · **FIX** (minor)

**FACT.** "completed — Stage A ran" (v6:172). Arrays without a usable axis are "Not assessable"
(v5:193, 202).

**ASSESSMENT.** If both axes are degenerate or non-separating, Stage A "ran" but checked nothing. The
status would read "completed", which misrepresents the QC.

**ACTION.** Add the status "completed — uninformative (no separating axis)", treated like "not
performed" for V-A purposes.

---

## 6. D7 estimability

### F15 — Criterion, tolerance, thresholds and adequacy are distinct and pre-fixed (verified) · **PI**

**FACT.**

- Estimability is E > η (v5:364–367). η = 10⁻⁸ is labelled numerical, with no source (v6:288).
- τ is applied on the standardized N (v6:289–290).
- c₁–c₃ and their scope are unset and fixed at A4 before the M-checks (v6:283–292, 124).
- No D7 value is revised afterwards (v6:292).
- Adequacy is explicitly *not* established by any check (v5:296–312).

**ASSESSMENT.**

- The four elements are **distinct and correctly ordered**.
- **No unit dependence remains**: continuous columns are standardized; c₁ and c₂ are counts; c₃ (VIF)
  is dimensionless; E is invariant given r_N.
- **Remaining arbitrary elements**, all labelled as such:
  - η (numerical, outcome-independent);
  - the definition of c₂, which can be met by heavily unbalanced mixed units (minority-count option
    listed, v6:299);
  - the absence of a residual-df decision criterion (option listed, v6:300).

**ACTION.** The PI sets c₁–c₃ and their scope, and decides on the two listed options, at A4.

---

## 7. Sensitivity and duplicate handling

### F16 — No precedence rule for re-inclusion sensitivities · **FIX**

**FACT.**

- S5e may include ambiguous arrays (v6:701); S5f re-includes R8 two-axis discordant arrays (v6:702).
- S14 includes "replicate 2" arrays (v6:712); S16 re-includes D-3/D-4 arrays (v6:714, 731).
- No text states what happens when an array is excluded for **more than one** reason (for example,
  R8 two-axis discordant *and* a D-1 duplicate, *or* a numerical failure).

**ASSESSMENT.** As written, a re-inclusion sensitivity could silently reintroduce an array that the
primary analysis excludes under another, unrelated rule. That changes the sensitivity's meaning.

**ACTION.** Add to §10.1: "a sensitivity lifts only the exclusion it names. Arrays excluded under any
other rule (eligibility, R5, numerical failure, another QC or duplicate category) remain excluded".
Report the overlaps.

### F17 — Duplicate tie rule across contrast boundaries · **PI** / **FIX** (minor)

**FACT.**

- D-3/D-4: keep the lowest GSM in a cluster; exclude the others (v6:245–248).
- C2 pairs come from R9, which runs on all deposited arrays, including MCI (v5:262).
- The reviewer sees no diagnosis (v6:237).

**ASSESSMENT.**

- A cluster may contain a contrast array (AD/CTL) and a non-contrast array (MCI). The blind rule can
  keep the MCI array and drop the AD/CTL array, so a contrast sample is lost.
- Identical expression under *different deposited diagnoses* is itself evidence of an identity
  conflict, which the blinded reviewer cannot see.
- The rule is outcome-independent, so this is not a bias concern, but its consequences are
  unreported.

**ACTION.** After the rule is applied (post-decision, descriptive only), report each cluster's
deposited-label composition. The PI decides at A2 whether label-discordant clusters are excluded
entirely (D18).

### F18 — Lock integrity and auditability (verified)

**FACT.**

- Discovery sensitivities never lock a new signature (v6:689).
- T_c is frozen, including for S16 (v6:690, 732).
- The duplicate log records sources, r, the fields examined, category, action, rule, reviewer and
  date. It is checksummed before the M-checks (v6:252–264).

**ASSESSMENT.** S5 and S16 cannot alter the locked signature. Duplicate outcomes are auditable.

---

## 8. Supersession and completeness

### F19 — v2 §7.5 status undefined · **FIX**

**FACT.**

- v2 §7.5 (v2:351–364) contains: the effect scale, multiplicity, the reporting list (effect with CI,
  moderated t, p, FDR, mean expression, annotation, group sizes after each step), missing data, and
  "assumption diagnostics … do not change the model after results unless a prespecified failure rule
  is approved (D7)" (v2:361).
- v5 §0.2 lists v2 §7.4 as active and v2 §7.3 as superseded (v5:76, 78), but not §7.5.
- v6 §0.1 inherits that map (v6:45–50).

**ASSESSMENT.** The confirmatory reporting requirements and the assumption-failure rule have
ambiguous status. The "failure rule" is unspecified anywhere and could be invoked after results.

**ACTION.** Declare v2 §7.5 active (reporting) and state "no assumption-failure rule; diagnostics are
descriptive only". Or supersede it explicitly.

### F20 — The GSE63061 effect-correlation analysis may have dropped out · **FIX** (minor; descriptive only)

**FACT.**

- v2 §9.5 (v2:457–462), active via v5:76 "except where a v5 section restates the topic", was restated
  at v5:629–630, inside v5 §7.
- v5 §7 is superseded by v6 §8 (v6:63), which does not mention the correlation.

**ASSESSMENT.** It is unclear whether this descriptive analysis remains.

**ACTION.** One line in v6 §8.1 retaining or withdrawing it.

### F21 — Dangling references in retained v5 text · **FIX** (minor)

**FACT.**

- Retained v5 §9 uses "the gene-level fit of §5.4" (v5:704); v5 §5.4 is superseded by v6 §6.5
  (v6:60, 396).
- Retained v5 §4.4 refers to the "Cascade in §11" (v5:389), which is now v6 §11.

**ASSESSMENT.** The intended meaning is clear, but the references point to superseded text.

**ACTION.** Add a two-row reference note to v6 §0.1.

### F22 — Open dependencies that could change a confirmatory result

| Dependency | Effect | Class |
|---|---|---|
| D6 option (v6:323–330) | The gene-level unit for discovery claims and the signature | PI |
| Annotation release / Entrez snapshot (v6:483) | Gene mapping, discovery and validation | EXT (D8) |
| D19 mapping (v6:486, 497–498) | GSE140829 replication | EXT |
| R8 variant and D_min (v6:179–204) | The discovery population | PI / EXT |
| Validation covariates (F6) | Validation decisions | FIX |
| Error-rate target (F5) | Replication claims | UNRESOLVED |

**Not confirmatory:**

- S13 unit rule (v6:364, 711) → OPT;
- G1b for GSE99039 and G2 for GPL570 (v6:328–329), which matter only if those options are chosen;
- software-behaviour checks (camera statistic; estimated weights) → EXT (D8).

**No omitted active sensitivity was found** beyond F20. S15 is restored (v6:713, 716–727); S14 and
S16 are present.

---

## 9. Decision readiness of every remaining issue

| Issue | Class | Smallest next action |
|---|---|---|
| D1 estimand; D2 eligibility; D3 input; D4 age; D17 filters | **PI** | Approve at A2 |
| D7 c₁–c₃, scope, c₂ definition, residual-df option (F15) | **PI** | Set at A4 |
| D5 conventions (n_min, tolerances, k, minimum counts) | **PI** | Approve at A3 |
| D5 D_min, option (a) | **EXT** | Source a separation reference, or choose (b)/(c) |
| D22 R8 variant (with F13 rule) | **FIX → PI** | Add the compatibility rule; then choose V-A/B/C |
| R8 status "completed — uninformative" (F14) | **FIX** | Add the status |
| D6 option and selection scope (after F1–F4) | **FIX → PI** | Correct §6.3–6.4; then choose |
| D6 G2 resource and GPL570 rule | **EXT** | D8 investigation |
| D6 G1b for GSE99039 | **PI / UNRESOLVED** | Only if G1b is chosen |
| D20 error-rate target (F5) | **UNRESOLVED → PI** | State the target |
| Validation covariates in lock and Tier A (F6) | **FIX** | Add to v6:452 and v6:125 |
| C-a unadjusted bounds; fit scope (F7) | **FIX** | Label; state the fit scope |
| D20 W1/W2, gatekeeping, Holm, C-c sidedness | **PI** | Choose at A5 |
| D12 inferential C-b | **PI** (keep descriptive) | — |
| D13 Q2 consequence (F9) | **PI** | Record the consequence; decide on Q2 |
| D13 no-specificity-without-δ statement and δ scale (F10) | **FIX** | Two sentences |
| D13 δ value | **EXT** (justification) → PI | Provide a rationale or "not used" |
| D13 GPL570 coverage; GU interpretation; contrast multiplicity | **PI** | A5 |
| Re-inclusion precedence (F16) | **FIX** | One rule in §10.1 |
| Duplicate cluster label composition (F17) | **FIX → PI** | Post-decision report; D18 choice |
| D18 duplicate handling | **PI** | A2 |
| v2 §7.5 status (F19) | **FIX** | Declare it active or superseded |
| GSE63061 correlation (F20) | **FIX** (descriptive) | One line |
| Dangling references (F21) | **FIX** | Map note |
| S3 site-only and S6/S10 independence (F2, F3) | **FIX** (OPT analyses) | List as not covered |
| S13 unit rule | **OPT** | Specify with D11 |
| D11 GSE140829 input | **PI** | A5 |
| D14 pathways | **PI**, with EXT for versions | A5; pin after D8 |
| D15 thresholds; D16 sensitivity set | **PI** (D16 after F16) | A5 |
| D21 / S11 | **OPT** | Defer, or drop S11 |
| D0 Notion plan | **EXT** | Provide the content or a statement |
| D8 environment | **EXT** (authorization) | Authorize the versions |
| D9, D10 | **EXT** | Owner contact (optional) |
| D19 GSE140829 mapping | **EXT** | Choose a route under D8 |
| GPL570 sex probes | **EXT** | Needs the GPL570 annotation |

---

## 10. Verification of unchanged files and limitations

**Integrity.** A checksum baseline of all 261 project files (data, reports, config, code, scripts,
tests and top-level files) was taken at the start of this audit and re-checked at completion (see the
completion report). That covers v1–v6, the v4 audit and the v5 register.

**Limitations:**

| Limitation | Detail |
|---|---|
| Earlier documents | [REG] and [AUD] were read earlier in this session, not re-read line by line here. Their checksums match the versions read |
| Expected-information claims | The validity statements in F1–F3 and F9 are analytical reasoning. They were not checked by simulation (no computation was permitted) |
| Software behaviour | The camera statistic and estimated-weight invariance remain unverifiable without D8 |
| Notion and the Lunnon PDF | Not read (constraints and tooling, as before) |
| Gate status | Not changed. No decision is approved |
