# BIO-MB-001 — Statistical Analysis Plan, DRAFT v7 (Phase 3B, targeted correction of v6)

**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen.**

- Only D1, D2, D3, D4 and D5 are approved, and D18 is partially approved (D-3/D-4 handling only) (each 2026-10-10), and D22 is partially approved (R8 variant V-A and §3.5 QC policy rows 1–6 only, 2026-10-11), and D6 is partially approved (gene-level option G3, S8 alternative G1 and freezing rule, 2026-10-12; gene-history cutoff 20260318, gene-history procedure and GPL570 mapping (Option A), 2026-10-13; Illumina annotation policy for GSE63060 and GSE63061 (D6-G, Option A0), 2026-10-17; nothing else), and D0 is approved as a governance designation only (2026-10-14: v7 is the governing statistical analysis document; this is not approval of the SAP or of any hypothesis), and D17 is approved (Option A, 2026-10-15), and the D18 D-1u ruling, GSE99039 title rule, R-rep1 rule and precedence rule (§5.2) and the D22 exclusion-list approval scope (policy only; no list approved) are approved (2026-10-15), and the D18 D-2 option (c) is approved (2026-10-15), and the D18 D-1 handling and review workflow/log are approved (2026-10-18; R2-ID scope unresolved), and the QC Stage A ruling is approved (GSE63060: compute and record candidate exclusions only; 2026-10-18), and the H1 analysis specification, D7, D15, D16 (with S-R8m) and the R8 review outcome (2026-10-18) are approved, and the register "Depends on" column is read under the C1 ruling (2026-10-15; v7:599), and D8 is approved for environment readiness only (D8-8, 2026-10-18; no real-data execution, annotation pin, Tier B or analysis is authorized by it; v7:611) (explicit PI instruction; conditions in §11). All other D0–D22 decisions, and the unapproved components of D6, D18 and D22, remain unapproved.
- The approval-gate status is unchanged:
  - **Not satisfied:** G1, G2, G5, G7, G8.
  - **Partially satisfied:** G3, G4, G6, G9.

**Preserved unchanged:**

- v1–v6;
- `reports/phase3b/v4/SCIENTIFIC_CONSISTENCY_AUDIT.md`;
- `reports/phase3b/v5/SCIENTIFIC_DECISION_REGISTER.md`;
- `reports/phase3b/v6/FINAL_SAP_READINESS_AUDIT.md` ([FA]).

v7 corrects the seven outstanding issues of [FA] §1, items 1–7. It also handles the smaller [FA]
findings that share text with them (F7, F9, F14, F17, F19–F21).

Nothing was executed:

- no expression value was read;
- no QC statistic, metadata pass/fail check, model, gene list, pathway result or signature exists;
- no sample is identified, classified, excluded or relabelled.

**Evidence used:**

- the v6 plan and [FA];
- the inherited v2 §7.4–7.5 (v2:308–364) and §9.5–9.6 (v2:457–469);
- v1 §4.6–4.9 (v1:147–194), which v2 §7.5 incorporates by reference;
- v3 §3.2 (v3:119–137) for covariate completeness.

Labels:

| Label | Meaning |
|---|---|
| **[EVIDENCE]** | Project file |
| **[REASONING]** | Statistical argument; not externally validated |
| **[PROPOSED]** | Default requiring PI approval |
| **[PROPOSED (no source)]** | Convention without empirical basis |
| **[DECISION NEEDED]** | Evidence does not determine an answer |
| **[UNRESOLVED]** | Cannot be resolved locally |
| **[DEPENDENCY]** | External information or authorization |

`v6:L` and `v5:L` refer to line numbers in those drafts.

---

## 0. Active-text map and change log

### 0.1 What is active

The active plan is **v7**, plus the **retained** parts of v6 below, plus the v5 and earlier texts that
v6 §0.1 (v6:43–71) keeps active, except where this map changes them.

| Text | Status in v7 |
|---|---|
| v6 §0 (v6:41–87) | Superseded by this §0. v6's v5-level map (v6:48–71) is **retained**, with the changes below. Under approved D5 option (b), the D_min requirements retained via v6:52–53 (v5:118 prerequisite; v5:217 sequencing) and the D-based separation rule (v5:174–175) are overridden by v7 §2.1–2.2. Under D22 (row 6 approved 2026-10-11), the retained R9 text of v5 §3.3 (v5:243–259) is overridden by the P3 definition in v7 §5.1 (v7:351) where they differ |
| v6 §1 (v6:91–101); §2.2 Tier B (v6:131–151) | **Retained**. Tier B step 2 ("Pin the annotation; probe → Entrez tables") is completed by the annotation pin record defined in §11 D6 (D1, approved 2026-10-17); creating that record is a separately gated later step that follows D8 (Tier B step 1) |
| v6 §2.1 Tier A (v6:117–129) | **Replaced** by v7 §1 |
| v6 §3 R8 requirement (v6:155–204) | **Replaced** by v7 §2 |
| v6 §4 duplicate workflow (v6:208–273) | **Retained**, with the v7 §5.4 addition (cluster composition report). Under D18 option B with S16 option 1 (partially approved 2026-10-10, D-3/D-4 handling only), the D-3/D-4 handling at v6:245–246 is superseded by v7 §5.1 F4 and §5.3 S16, and the tie rule at v6:248 is not used to select a representative for D-3/D-4 clusters. D-3 and D-4 have identical inclusion handling; a pair whose arrays carry different, undocumented participant codes is recorded as "D-3/D-4: identity uncertain" and is not taken as evidence of distinct participants (v7:605) |
| v6 §5 identifiability order (v6:277–305) | **Retained** |
| v6 §6.1–6.2 (v6:311–344); §6.5–6.6 (v6:396–416) | **Retained** |
| v6 §6.3–6.4 freezing and validity (v6:346–394) | **Replaced** by v7 §3 |
| v6 §7.1 (v6:422–439) | **Retained** |
| v6 §7.2 lock contents (v6:441–467) | **Replaced** by v7 §7 |
| v6 §8.1–8.5, §8.7, §8.9 (v6:473–542, 569–573, 582–602) | **Retained** |
| v6 §8.6 C-a (v6:544–567); §8.8 multiplicity (v6:575–580) | **Replaced** by v7 §4 |
| v6 §9.1–9.6 (v6:608–654) | **Retained** (Q2 consequence added in v7 §8.3) |
| v6 §9.7–9.8 (v6:656–679) | **Replaced** by v7 §8 |
| v6 §10.1 general rules and table (v6:685–714); §10.3 (v6:729–732) | **Replaced** by v7 §5 |
| v6 §10.2 S15 (v6:716–727) | **Retained** (its sample set is restated in v7 §5.3) |
| v6 §11–§16 (v6:736–890) | **Replaced** by v7 §9–§14 |

**Inherited text whose status v7 settles:**

| Inherited text | Status |
|---|---|
| **v2 §7.5** (v2:351–364) | **Retired.** Its necessary requirements are restated in v7 §6; its "assumption-failure rule" is replaced by v7 §6.3 |
| **v1 §4.6–4.9** (v1:147–194; pulled in by v2 §7.5) | **Retired.** v1 §4.6's chip-confounding fallback (duplicateCorrelation, or dropping chip) conflicts with v5 §4 and is not active. v1 §4.7 is covered by v5:397–398 and D8. v1 §4.8 and §4.9 are restated in v7 §6 |
| **v2 §9.6** (v2:464–469) | **Replaced** by v7 §4.1 (covariates restated and locked) |
| **v2 §9.5** (v2:457–462) GSE63061 effect correlation | **Retained** as a descriptive output (v7 §4.5) ([FA] F20) |
| **Reference notes** ([FA] F21) | Retained v5:704 ("gene-level fit of §5.4") means v6 §6.5. Retained v5:389 ("Cascade in §11") means v7 §9 |

### 0.2 Change log from v6

| [FA] issue | v7 change | v7 § |
|---|---|---|
| 1 Replication error-rate target | Three claim families, each with a stated controlled error rate and stated non-control; options for D20 | 4.2–4.4 |
| 2 Validation covariates | Restated from v2 §9.6, mapped per cohort and contrast, with missing-data and non-estimability rules; locked; added to Tier A | 4.1, 7, 1 |
| 3 G1 selection validity | Model families A (independence established under stated assumptions) and B (not established; sensitivity-only label); consistency vs validity separated | 3 |
| 4 Re-inclusion precedence | Exclusion tiers P/Q/F/I, a precedence rule, per-analysis sample-set formulas and an audit log | 5 |
| 5 R8 option consistency | A table of permitted D5 × D22 combinations; behaviour when D_min is not approved; "completed — uninformative" status | 2 |
| 6 v2 §7.5 | Retired; reporting and missing-data requirements restated; prespecified no-failure-rule default | 6, 0.1 |
| 7 Equivalence margin | No negligible-association or specificity conclusion without δ on a defined scale; what remains reportable; scale options for D13 | 8 |

---

## 1. Approval timing (replaces v6 §2.1; amended 2026-10-10 — stage-specific approval)

- **Amendment provenance.** Amended on 2026-10-10 on the PI's instruction approving the narrowing of the timing rule. That instruction approves **only this timing rule**. This amendment supersedes the earlier v7 §1 principle "Every scientific rule, threshold and choice is approved in Tier A, before QC Stage A starts" (v7 SHA-256 `0c35f278…bced`, before amendment) and the v6 principle it restated (v6:107–115; v6 is preserved unchanged). It **does not approve** any D0–D22 decision, hypothesis, threshold, model or analysis option. It changes neither any decision status nor the approval-gate status (v7:5–8).
- **Rule.** **(1)** Decisions governing the primary GSE63060 discovery population, expression input, probe eligibility, QC, statistical model, primary hypothesis and multiplicity control are approved **before the corresponding real-data QC or analysis begins**. **(2)** Decisions governing how discovery results are selected, interpreted or used for replication are approved **before discovery results are generated or inspected**. This covers the signature cap and coverage rules, the replication criteria and any result-dependent feature-selection rule. **(3)** Decisions specific to GSE63061, GSE140829, Parkinson's disease specificity and pathway analyses are approved **before the relevant cohort or analysis begins**. **(4)** Deferring an analysis **does not authorize changing its rules after its relevant results have been seen**. Any later change is a documented amendment, reported as post hoc (v6:149–151). **(5)** Unresolved assumptions and evidence blockers remain explicit (v7 §12; [UNRESOLVED] and [DEPENDENCY] labels). Execution-only items may complete later.

| Tier | Decisions (only D1, D2, D3, D4 and D5 approved and D18 partially approved — D-3/D-4 handling only, 2026-10-10; D22 partially approved — R8 variant V-A and §3.5 QC policy rows 1–6 only, 2026-10-11; D6 partially approved — gene-level option G3, S8 alternative G1 and freezing rule (2026-10-12) and gene-history cutoff 20260318, gene-history procedure and GPL570 mapping (Option A) (2026-10-13) and Illumina annotation policy for GSE63060/GSE63061 (D6-G, Option A0) (2026-10-17) only; D0 approved as a governance designation only (2026-10-14; not approval of the SAP); D17 approved — Option A (2026-10-15); D18 D-1u ruling, GSE99039 title rule, R-rep1 rule and precedence rule (§5.2), and D22 exclusion-list approval scope (policy only) approved (2026-10-15); D18 D-2 option (c) approved (2026-10-15); D18 D-1 handling and review workflow/log approved (2026-10-18); QC Stage A ruling approved (GSE63060: compute and record only; 2026-10-18); the H1 analysis specification, D7, D15, D16 (with S-R8m) and the R8 review outcome (2026-10-18) approved; D8 approved for environment readiness only (D8-8, 2026-10-18; no real-data execution authorized; v7:611); all others unapproved) | Must be approved before |
|---|---|---|
| A1–A2 | D0; D1 (primary hypothesis: H1 wording approved 2026-10-14 as D1-H, v7:604 — its adjustment set, test, threshold and multiplicity rule are not approved and no analysis is authorized; H2 and H3 remain [PROPOSED] (v1:37–42; restated by reference in v2 §2)); D2; D3; D4; D17; D18 (GSE63060 identity and the precedence rule, v7 §5) | Real-data QC Stage A and every analysis they govern (rule 1) |
| A3–A4 | D5 and D22 **as a permitted combination** (v7 §2.2); D7 c₁–c₃, scope, conventions and the assumption-diagnostics rule (v7 §6.3) | Real-data QC Stage A (D5/D22) and the identifiability checks and model fits (D7) (rule 1) |
| A5 — discovery | D6 (option, selection scope, model-family labelling, v7 §3); D15 discovery q-level | The discovery fits (rule 1) |
| A5 — use of discovery results | D15 signature cap and coverage; D20 (claim families, error-rate options, weighting, C-c sidedness, validation covariates, v7 §4); D12; D16 sensitivity set | Discovery results being generated or inspected (rule 2) |
| A5 — cohort/analysis-specific | GSE63061 rules under D20 (v7 §4.1, §4.3); GSE140829: D11, D18 "replicate 2" option, D19 route; GSE99039: D13, including δ scale and value or "equivalence not used" (v7 §8); pathways: D14; S11: D21 | The relevant cohort or analysis (rule 3) |
| A6 | D8 | Any real-data computation, meaning any computation whose outputs enter QC, sample sets, models, the annotation pin or the lock (D2, approved 2026-10-17). Preparatory identifier-only audits require explicit PI authorization, and their artifacts are verified or regenerated in the D8-approved environment before entering any of these. C15 (2026-10-15) and the A0 classification (2026-10-17) preceded D8 approval and were performed under explicit PI authorization; this rule neither approves nor invalidates them retroactively, and they remain subject to that D8 verification before downstream use; that verification was completed 2026-10-18 by regenerating C15, A0 and GPL570 in the D8 environment as v2 artifacts byte-identical to v1 (reports/annotation_audit/v2_regeneration_2026-10-18). Every output of such a computation carries a source-tree identity record (src/biomarker_project/code_identity.py: the code set with per-file SHA-256, the aggregate SHA-256, git HEAD and the full git status including untracked and modified files), verified against the source tree after the computation with no code-set mismatch; a git commit alone is not sufficient (D8-3, explicit PI authorization 2026-10-18) |

**δ rule (restated for stage-specific timing):** if δ and its scale are not approved before the specificity analysis begins, the equivalence category and every negligible-association or specificity
conclusion are **unavailable for this study** (v7 §8). Under the relative-to-AD scale, the fraction must be fixed before discovery results exist (v7:533).

---

## 2. R8 requirement and permitted D5 × D22 combinations (replaces v6 §3; resolves [FA] issue 5 and F14)

### 2.1 Facts and computational dependency (unchanged from v6:157–166)

- R8 needs D_min (option (a)) or an approved option (b) or (c) (v5:217–234). Accordingly, v5:217 and the "D_min" prerequisite at v5:118 read: "until D5 is approved as option (a), (b) or (c)". Under (b) no D_min exists or is required; under (c) R8 is not run.
- For GSE140829, R8 needs D19. For GSE99039, it needs the GPL570 sex probes.
- No main model takes R8 output as an input. R8 changes only the population (two-axis discordant
  exclusions), and only the S5 R8 components use its flags.

### 2.2 Permitted combinations [D5 option (b) and D22 variant V-A approved as a permitted combination; see §11 D5, D22]

**D5 states:**

- **(a)** D_min justified and approved;
- **(b)** no-threshold variant (v5:226–228). Under (b), an axis is separating iff it is non-degenerate under the existing admissibility rule (v5:163, 170–171); v5:174–175 do not apply. Usability follows v5:185, unassessable arrays follow v5:153–156 and 193, and "completed — uninformative" (v7:170) means that neither axis is non-degenerate. D (v5:173) is computed and reported descriptively only and never determines classification, axis usability, separation or whether R8 is informative;
- **(c)** R8 not run (v5:229–234);
- **(u)** unset.

**D22 variants** (defined here; the per-analysis table at v6:181–188 is superseded by v7 §2 per v7:61 and is not used):

- **V-A:** R8 is a gate wherever it is assessable. **Gated analyses** (per cohort): the primary-population log (Tier B step 7, v6:139) and every subsequent analysis that depends on that cohort's eligible population. They start only when the cohort's R8 status is "completed — informative" or "not applicable"; otherwise they are "not assessable — R8" (v7:169–173, 548–549). QC Stage A (R8, R9) executes for a cohort only when its required inputs exist and its governing QC policies have been approved (v5:112–121; v7:552). Outputs from a cohort blocked by an external dependency are not used in any downstream analysis until that dependency is resolved and the cohort's R8 gate opens.
- **V-B:** R8 is optional. It runs if D5 permits, but no analysis waits for it.
- **V-C:** R8 is a gate for discovery only.

| D5 \ D22 | V-A | V-B | V-C |
|---|---|---|---|
| (a) | Permitted | Permitted (R8 runs; its rule-based exclusions apply where it completed; not a gate) | Permitted |
| (b) | Permitted | Permitted | Permitted |
| (c) | **Not permitted.** A gate that can never open would block every gated analysis | **Permitted** (the only combination with (c)) | **Not permitted** (discovery would be blocked) |
| (u) | **Not permitted.** Tier A3 is incomplete | Not permitted | Not permitted |

**If D_min cannot be justified [UNRESOLVED; D5]:**

- Option (a) is unavailable, so A3 can be completed only with **(b) under any variant** or **(c)
  under V-B**.
- The study does not start with D5 unset. This is **explicit**: Tier A is incomplete, so Tier B does
  not begin. It is not a silent block.
- No threshold is assumed, and R8 is never treated as completed.

**Cohort-level dependency blocks under V-A or V-C.** If R8 is "blocked" in a cohort by an external
dependency (D19 for GSE140829; GPL570 annotation for GSE99039):

- that cohort's gated analyses are reported as **"not assessable — blocked by R8 dependency"**;
- other cohorts proceed;
- the plan never reports these cohorts as analysed.

### 2.3 R8 status vocabulary (extends v6:168–177)

| Status | Meaning | Counts as R8 "completed" for gating and S5? |
|---|---|---|
| completed — informative | Stage A ran and at least one axis was separating | Yes |
| **completed — uninformative** | Stage A ran, but no axis was separating, so no array had a usable axis ([FA] F14) | **No.** Treated as "not performed" for V-A/V-C gating; the R8 S5 components are not run |
| not applicable | A0: probes absent or fewer than 2 Y genes | No. Under V-A/V-C, a cohort with "not applicable" proceeds (v7 §2.2); this is reported |
| not performed | (c), or V-B with R8 not run | No |
| blocked | External dependency | No (see §2.2) |

- **Under every combination:** results produced without informative R8 carry the label "sex
  consistency not verified".
- The R8 status per cohort is reported.

---

## 3. Probe-selection consistency vs inferential validity (replaces v6 §6.3–6.4; resolves [FA] issue 3)

### 3.1 Two different properties

| Property | What establishes it | Status |
|---|---|---|
| **Selection consistency** | Freezing T_c (§3.2): each gene is measured by the same probe, or the same constituent list, in every model of cohort c | Established **by construction** for all options |
| **Selection independence** (G1/G1b) | The selection is statistically independent of the test statistics of a given model. This is necessary, **not sufficient**, for a valid gene-level test | Established only for model family A (§3.3), under stated assumptions |
| **Inferential validity** | Independence plus a correct mean model, error model and moderation prior | **Not established by any argument in this plan.** It is conditional on assumptions that are unverified (v5:438–440) |

### 3.2 Freezing rule (restated from v6:346–371; unchanged except for the S5 row and S6, S11)

- T_c is built once per cohort (v6 §6.2) and used unchanged for every model in that cohort.
- **Exceptions:**
  - S7: no reselection; a filtered-out selected probe means "not measured under S7"; under G3, the
    average is over the surviving constituents.
  - S8: its own T_c.
  - S9: the frozen identities; "annotation-discordant" genes reported.
  - S10: the frozen identities, with new values.
  - S13: the unit rule is open with D11.
- The re-inclusion analyses (S5e include variant, S5f, S14) and the S6 and S11 designs use
  T_c unchanged. Their independence status is given in §3.3.
- Alternatives (re-selection per model or per contrast; GSE99039 IPD ∪ CONTROL only) remain D6
  options, as listed in v6:367–371.

### 3.3 Model families for G1 (and G1b) selection independence [REASONING]

**Stated assumptions (S-1 to S-5):**

- **S-1** Gaussian errors.
- **S-2** Errors independent across samples **given the model's mean**. This requires every shared
  unit effect (chip or batch) to be in the mean model.
- **S-3** A common error covariance across samples (no group-dependent or array-dependent variance).
- **S-4** The design matrix does not depend on expression data.
- **S-5** The model is fitted to deposited values, by least squares or fixed-weight least squares,
  with an intercept.

**Argument.** Take a model fitted to M ⊆ S_c under S-1 to S-5. Its contrast weights and residual
directions are supported on M and orthogonal to 1_M, hence to 1_{S_c}. So the S_c probe means are
independent of its coefficient and residual statistics.

**limma-trend.** Its prior depends on each probe's mean over M. Under the empirical-Bayes model this
leaves the moderated t conditionally t-distributed given the means, so independence still holds
*if the trend model is correct* [REASONING; unverified].

| Family | Membership | Status | Labelling |
|---|---|---|---|
| **A — independence established under S-1 to S-5** | Primary discovery model; validation C-c and C-a models; specificity Q1 and per-gene models; S1, S2, S3 (site **added**, chip retained), S4, S5a–S5d, S5e (exclude variant), S5g, S7, S9, S12, S15, S16 (excludes D-3/D-4 cluster members; a subset of the primary set) | Selection independent of the test statistics, **conditional on S-1 to S-5** | Results under G1 carry "conditional on selection assumptions S-1 to S-5" |
| **B — independence not established** | S5e (**include** variant) and S5f: re-included arrays outside S_c. S14: re-included arrays outside S_c. S3 (**site instead of chip**): S-2 fails because chip variation enters the errors. S6 (estimated array weights): the premise of S6 is that S-3 fails, and the weights are data-derived. S10 (re-normalized values): S-5 fails. S11 (deconvolution covariates estimated from expression): S-4 fails. S13 (different processed file) | No independence claim | **Sensitivity-only**, labelled "selection independence not established" |

**C-c note [REASONING].** The z-standardization (v6:503) uses means and SDs over the score samples.
Centring is orthogonal to 1, so the score test belongs to family A under S-1 to S-5.

**Not covered by any family.** Expression-based QC that defines the population (R8 sex probes, R9
correlations, D-3 duplicates) is diagnosis-blind but **not shown** to be independent of the test
statistics. This is a stated limitation for every option.

**Implication for D6 (not a choice).**

- Under G1, every primary result is conditional on S-1 to S-5. Family B results are sensitivity-only
  under any option.
- G2 and G3 involve no selection, so the selection-independence question does not arise for them.
  Inferential validity still depends on the model.
- G1b relies on a disjoint selection set (v5:441).
- The choice remains D6 [DECISION NEEDED].

---

## 4. Validation inference (replaces v6 §8.6, §8.8 and v2 §9.6; resolves [FA] issues 1–2 and F7)

### 4.1 Validation covariates — restated from the inherited source and locked

**Source [EVIDENCE].**

- v2 §9.6 (v2:466–469):
  - GSE140829: "age_at_draw, Sex, batch (19)";
  - GSE63061: "age, gender, chip (34 chips from barcodes)".
- Discovery design: group + age (linear) + sex + chip (v1:149–151; v5:397).
- Completeness: v3 §3.2 (v3:121–125) reports **0 missing** age, sex and batch/chip in GSE63060,
  GSE63061 and GSE140829.

| Cohort | Contrast | Phenotype fields ([P1] columns) | Covariates in the model | Unit term | Expected missingness [EVIDENCE: v3 §3.2] |
|---|---|---|---|---|---|
| GSE63060 (discovery) | AD vs CTL | `char:age`, `char:gender`, chip from `title` barcode | age (linear), sex, chip | chip (29) | 0 |
| GSE63061 (consistency) | AD vs CTL (R5 labels excluded) | `char:age`, `char:gender`, chip from `title` barcode | age (linear), sex, chip | chip (34) | 0 |
| GSE140829 (replication) | AD vs Control | `char:age_at_draw`, `char:Sex`, `char:batch` | age_at_draw (linear), sex, batch | batch (19) | 0 |
| GSE140829 S13 | AD vs Control | as above | **Open** with D11 (whether batch is included for a ComBat-corrected file) | — | 0 |
| GSE99039 (specificity) | IPD / GPD / GU vs CONTROL | `char:Sex`, `char:batch`; S15 adds `char:age at exam` | sex, batch; S15 adds age (linear) | batch (37) | Sex 35 of IPD/CONTROL; age per v6 §10.2 |

**Rules [PROPOSED; D20/D11]:**

1. **Functional form:** age is linear in all cohorts (spline only in S2); sex is an indicator; the
   unit is a fixed effect. No interaction terms.
2. **Missing data:** complete case per model (R2-COV). Excluded counts are reported (v7 §6.2). No
   imputation.
3. **A required covariate is unavailable** (field absent or entirely missing): the cohort's model is
   **"not assessable"**. **No substitute covariate set** is used unless one was approved at A5 and
   locked. None is proposed.
4. **Non-estimable or insufficient design** (v5 §4.4 STOP): "not assessable". No covariate is dropped
   to restore estimability.
   - An *aliased nuisance term*, such as a covariate constant within the score samples, is handled
     automatically by v5 §4.4 steps 7–8. Group estimability is unaffected, the aliasing is reported,
     and this is not a choice.
5. **The models differ by cohort** (chip vs batch; different age fields). The plan does **not**
   assume a common model across cohorts.
6. **Locking:** this table and these rules are written into the lock (v7 §7, item 5) **before any
   validation outcome is examined**.

### 4.2 Claim families and the error rate each procedure controls [REASONING]

| Family | Hypotheses | Procedure (as proposed) | Controls | Does **not** control |
|---|---|---|---|---|
| **R1 — composite replication, per cohort** | One per cohort: H0_c: θ_c ≤ 0 | One-sided t-test at α = 0.05; decision via the one-sided 95% lower bound (v6 §8.5) | Type I error ≤ 0.05 **for that cohort's claim**, under the model assumptions | The probability of a false composite claim in *either* cohort (up to about 0.0975 if the tests are independent; at most 0.10); any joint error with R2 |
| **R2 — per-gene replication, per cohort** | F_c = {H0_g,c: d_g·β_g,c ≤ 0, for g measurable and locked} | One-sided moderated t; BH at q < 0.05 within F_c | **FDR ≤ 0.05 within F_c**, under PRDS (unverified; v6:556) | FWER within F_c; FDR across cohorts pooled; any joint error with R1 |
| **R3 — claims across validation cohorts** | E.g. "replicated in both" or "in at least one" | **None defined** | — | — |

**Consequence.** As proposed, the hierarchy (R1 primary, R2 secondary, C-b descriptive) controls
**per-claim type I error for R1** and **within-cohort FDR for R2**. It does **not** provide familywise
control over all replication claims. Any statement implying such control is **not permitted**.

### 4.3 Options for D20 [DECISION NEEDED; none approved]

**R1/R2 linkage, within a cohort:**

| Option | Rule | Error-rate statement |
|---|---|---|
| **O1 — separate families** [PROPOSED default] | R1 and R2 tested independently. R2 is always reported, labelled secondary | As in §4.2. No combined control |
| O2 — fixed-sequence gate | R2 claims are made only if R1 rejects in that cohort | Under the cohort's global null (θ_c ≤ 0 and all gene nulls true), P(any claim) ≤ 0.05. With a passed gate, BH-FDR within F_c applies; the **conditional** FDR properties after gating are not established here [REASONING] |
| O3 — FWER for per-gene claims | Holm within F_c instead of BH | FWER ≤ 0.05 within F_c; lower power |

**Across cohorts (R3):**

| Option | Rule | Error-rate statement |
|---|---|---|
| **X1 — no cross-cohort claim** [PROPOSED default] | Results reported side by side; GSE140829 as replication, GSE63061 as consistency; no "both" or "either" statement | No cross-cohort error rate needed, because no such claim is made |
| X2 — "replicated in both" | Intersection–union: claim only if each R1 test rejects at α | Type I ≤ α for the conjunction claim. Note that GSE63061 is a consistency cohort, so "replicated" wording would require D10/D20 approval |
| X3 — "in at least one" | Holm across the two R1 tests | FWER ≤ 0.05 for the R1 claims |

**Why there is no unique choice [REASONING].** The target depends on how the PI intends claims to be
used (a single headline replication claim vs several reported findings). The cohorts also have
different roles (independence unverified; related cohort). Neither question is settled by evidence.

### 4.4 C-a specification (replaces v6:544–567; unchanged except where marked)

- **Null, alternative, test, family, BH rule and claim wording:** as v6:548–553 (family R2).
- **Fit scope ([FA] F7):**
  - The cohort's gene-level model is fitted to **all rows of U_c**, so the empirical-Bayes prior uses
    every gene.
  - BH is applied to the **measurable locked genes only**.
- **Per-gene bounds ([FA] F7):** the one-sided 95% bound in the locked direction is **unadjusted**
  and labelled so. Claims use q only.
- **Gatekeeping:** per the D20 option O1/O2/O3 (§4.3).
- **Claim boundaries:** as v6:559–567. Statistical replication ≠ biological or clinical validation.
  "Replicated" is not used for GSE63061.

### 4.5 GSE63061 effect correlation (retained from v2 §9.5)

- The correlation between discovery and GSE63061 gene-level effects across the measurable locked
  genes is reported with a CI, as **descriptive**.
- It is labelled: possible participant overlap may inflate agreement (H9).
- It is not a replication claim.

---

## 5. Sample-set precedence for all analyses (replaces v6 §10.1 and §10.3; resolves [FA] issue 4 and F17)

### 5.1 Exclusion tiers

| Tier | Contents | Can a sensitivity lift it? |
|---|---|---|
| **P — primary eligibility** (never lifted) | P1: arrays outside the R1 universe (including R11 undeposited arrays), non-contrast labels (R3/R4) and R5-category labels. R6, R10, R12 and R13 produce no exclusions (rules of non-use or documentation). R7 (age) is governed by D4 and applied according to its approved option. R8 is assigned to Q1/Q2/F2/F3 below, and R9 to P3 (numerical failures) and F1 (flags). P2: R2-ID identity failures on GSM accession or array barcode, and D-1 metadata-confirmed duplicates (the non-kept member). A non-unique undocumented description value used as the participant code is not a P2 exclusion: the arrays are retained, flagged, listed and reported under the D-1u ruling (v7:621). P3: R9 numerical failures (R9 A0/A1/A3), defined as follows under D22 (approved 2026-10-11; overrides v5:243–259 where they differ). R9 is run separately within each cohort on that cohort's deposited Series Matrix arrays; R9 needs neither R8 output nor probe mapping, and QC Stage A execution and the use of its outputs follow the cohort's V-A gate (v7:139). (i) A0: a zero-variance array is a numerical failure (v5:244). The A1 correlation matrix is computed once, over the cohort's arrays remaining after A0; pair counts (A1) and medians (A3) refer only to these arrays, and this one fixed matrix is used throughout. (ii) A1: an array with more than half of its pairs non-finite is a numerical failure (v5:249); no m_i or z_i is computed for it, but its finite r_ij still enter other arrays' medians. (iii) A3: m_i is the median of array i's finite r_ij from the fixed matrix (v5:253); A1 and A3 outcomes never change any other array's median. If m_i ≥ 1 − 10⁻⁸ (including computed m_i > 1), z_i is not computed and the array is "R9 near-identical — referred to D18": it is not a numerical failure, is not R9-flagged, does not count toward A3b and does not enter A4/A5, and is retained in the primary analysis subject to other approved rules; its D18 handling follows F4 (S16 only, subject to D16). This is a D22 median-level threshold; it reuses the constant of, but is distinct from, the D5 pairwise near-identical tolerance applied at A2 (v7:608). A2 lists pairs with r_ij ≥ 1 − 10⁻⁸ for the D18 review (v5:250–251); membership of an A2 pair does not by itself refer an array under A3, and a referral is never by itself a numerical failure. If m_i ≤ −1 (including computed m_i < −1), z_i is not computed and the array is a numerical failure. Otherwise z_i = atanh(m_i), and a non-finite z_i (defensive) is a numerical failure. Only arrays with finite z_i count toward the A3b 10-array minimum, and A4's M and S are computed over arrays with finite z_i only. (iv) R9 not applicable: R9 "actually ran" (v6:97) includes a run that later stops as not applicable. Failures classified at stages that ran remain P3, and no failure is inferred for a stage that did not run: an A0 stop (fewer than 10 arrays remain) retains A0 failures only; an A3b or A4 stop retains A0, A1 and A3 failures. (v) Rationale: a numerical-failure array is excluded because the R9 statistic cannot be computed validly for it under these rules (for m_i ≤ −1 the correlation profile is defined, but the statistic is not); this replaces the v5:284 wording "The array yields no valid correlation profile" as the rationale. P3 arrays are listed, never lifted and not varied in any sensitivity analysis. P4: R2-COV (per model) | **No** |
| **Q — primary QC/identity exclusions that one named sensitivity may lift** | Q1: R8 two-axis discordant (lifted only by S5f). Q2: R8 ambiguous, **if** the approved primary option excludes them (lifted only by the S5e include variant). Q3: D-2 replicate arrays, GSE140829 "replicate 2" (lifted only by S14). Q4: none — under D18 option B, D-3/D-4 arrays are not excluded from the primary analysis (see F4) | Only by the named sensitivity |
| **F — flags that are not primary exclusions** | F1: R9 flags at k = 3, 2.5 or 4. F2: R8 single-axis discordant. F3: R8 ambiguous, **if** the primary option retains them. F4: every array in a qualifying D-3/D-4 cluster, i.e. a connected C2 cluster (v6:218–220) containing at least one D-3 or D-4 pair; arrays excluded under another independently applicable rule (e.g. a non-kept D-1 member, P2) remain excluded; a similarity flag alone never excludes an array from the primary analysis | A named sensitivity may *impose* their exclusion (S5a–S5e, S5g; S16 for F4, which runs only if approved under D16) |
| **I — restrictions intrinsic to a sensitivity** | S1 age ranges; S4 "M"-coded AD; S12 Sood subset; S15 age-complete subset | Applied only in that sensitivity |

### 5.2 Precedence rule [APPROVED 2026-10-15 under D18 (v7:621); which sensitivity sets exist is decided under D16]

For any analysis A:

> **Sample set(A) = Base − (Tier Q exclusions not lifted by A) − (Tier F flags that A excludes) −
> (Tier I restrictions of A) − (Tier P4 for A's covariates)**,
> where **Base = eligible arrays after Tier P1–P3**.

- **An array is re-included by a lift only if every one of its Tier P and Tier Q reasons is lifted by
  A.** Tier P is never lifted.
- So an array that is both R8 two-axis discordant (Q1) and a D-2 replicate (Q3) is **not**
  re-included by S5f or by S14.
- Every array's exclusion reasons are recorded as a **multi-label** set. No single "primary reason"
  is used.

### 5.3 Sample-set definitions (auditable)

| Analysis | Sample set |
|---|---|
| Primary (each cohort) | Base − Q1 − Q2 (if the primary excludes ambiguous) − Q3 (per D18 option) − P4 (R2-COV, per model); Q4 is empty because D-3/D-4 arrays are retained under D18 option B (v7:352; F4 flags only) |
| S1, S4, S12 | Primary − the intrinsic restriction |
| S2, S3, S6, S7, S8, S9, S10, S11 | Primary set (design, values or features differ) |
| S5a / S5b / S5c | Primary − F1 at k = 3 / 2.5 / 4 |
| S5d | Primary − F2 (only if R8 completed — informative) |
| S5e | Primary − F3 (if the primary retains ambiguous), **or** Primary + Q2-only arrays (if the primary excludes them) |
| S5f | Primary + arrays whose only Tier P/Q reason is Q1 |
| S5g | Primary − F1(k = 3) − F2 − F3 (R8 parts only if completed — informative) |
| S13 | Primary set of GSE140829, mapped to the S13 file (rule open with D11) |
| S14 | Primary + arrays whose only Tier P/Q reason is Q3 |
| S15 (GSE99039) | Specificity primary set − the age-missing intrinsic restriction |
| S16 | Primary − F4: every array in each qualifying D-3/D-4 cluster is excluded, with no representative selected; arrays excluded under any other rule remain excluded (definition only; S16 runs only if approved under D16) |

### 5.4 Audit log

Before any model is fitted, a checksummed **sample-set log** records:

- per array: all Tier P/Q/F reasons;
- the analysis × array membership matrix.

**Overlap counts** (arrays with more than one reason) are reported.

**Duplicate cluster composition ([FA] F17).** After the D-3/D-4 rule has been applied, the deposited
label composition of each cluster is reported descriptively. That report changes no decision.
Under D18 option B with S16 option 1, label-discordant clusters are retained in the primary analysis under their deposited labels and excluded in S16 if they qualify under F4, like any other qualifying
cluster; label discordance alone is not a primary exclusion, and no sample is relabelled.

No actual sample is examined or classified in this draft.

### 5.5 General sensitivity rules (restated from v6:687–691)

- Every sensitivity is prespecified and reported, and none replaces the primary analysis.
- Each passes v5 §4.4, including c₁–c₃.
- No sensitivity locks a new signature.
- T_c is frozen (v7 §3.2).
- Family B analyses carry the label "selection independence not established" (v7 §3.3).

**Sensitivity list:** S1–S16, titled as in v6:695–714; sample sets are defined in §5.3, which governs wherever the two differ (including S16). S5 sample sets are as in §5.3.

---

## 6. Reporting, missing data and assumption diagnostics (replaces v2 §7.5 and v1 §4.8–4.9; resolves [FA] issue 6)

### 6.1 Reporting requirements (restated from v2:356–360 and v1:175–183)

- **Probe level:**
  - the AD − CTL effect on the deposited scale (approximately log2; caveat stated), with 95% CI;
  - moderated t, p and BH FDR;
  - mean expression;
  - annotation with resource and version;
  - the number of probes tested.
- **Gene level:** β_g with 95% CI, moderated t, p, q; the T_c entry (selected probe or constituent
  list).
- **Every model:**
  - sample counts per group after each eligibility, QC, duplicate and covariate step (v7 §5.4);
  - R8 status (v7 §2.3);
  - the model-family label (v7 §3.3).
- **No result is suppressed** for being non-significant.

### 6.2 Missing data (restated from v1:186–190, with the observed facts)

- Complete case per model (R2-COV). Excluded counts are reported. No imputation.
- **Rule inherited from v1:** where a model's complete-case loss exceeds **10%**, a prespecified
  sensitivity must exist. The known case is GSE99039 age (S15). GSE99039 sex loses 35/438, which is
  8% (v3 §3.4). The validation cohorts have 0 missing (v3 §3.2).
- If an unexpected loss above 10% occurs where no sensitivity was prespecified, it is reported as a
  limitation. **No post hoc imputation or added analysis is used for claims.**

### 6.3 Assumption diagnostics — prespecified rule replacing the v2 "failure rule" [PROPOSED; D7]

- **Diagnostics:** the mean–variance trend, residual summaries and array-weight estimates. They are
  **reported descriptively only**.
- **No assumption-failure rule alters any primary, validation or specificity model.** Each model is
  fixed by the decisions approved for its stage before that stage begins (v7 §1).
- Alternative specifications exist **only** as the prespecified sensitivities S2 (age spline) and S6
  (array weights).
- **Alternative [DECISION NEEDED; D7]:** the PI may prespecify, at A4, a quantitative failure
  criterion together with a fixed alternative model. **None is proposed.** If neither this default
  nor an alternative is approved at A4, the A4 gate is not met: no identifiability check or model fit governed by D7 starts, and no results are produced (v7 §1, rule 1).
- This removes the discretionary, potentially post-result "failure rule" of v2:361–362.

---

## 7. Lock contents (replaces v6 §7.2)

Written and checksummed before any validation or specificity expression is modelled against
diagnosis.

1. The D6 option, the selection-set definitions, the freezing rule, the model-family labels (v7 §3),
   and the checksum of T_GSE63060.
2. The annotation resource and release; the mapping rule; the validation feature rule (v6 §8.2); and the annotation pin record (Tier B step 2; §11 D6), cited with its SHA-256 once that record has been created (created 2026-10-18: reports/annotation_audit/annotation_pin/v1/annotation_pin_record.json, SHA-256 cde8ccd7d87b3622227a1b174599c4786fa94906159707fc4e498c72f3253a67).
3. Per gene: Entrez ID and symbol; selected probe or constituent list; β_g with 95% CI, moderated t
   and q; direction and rank.
4. Counts: eligible, up and down genes.
5. **Validation specification:**
   - the weighting;
   - the standardization;
   - the coverage rule (v6 §8.4);
   - the C-c estimand, test, bound and α (v6 §8.5);
   - the C-a rule, fit scope and bound labelling (v7 §4.4);
   - the C-b specification (v6 §8.7);
   - **the claim families and the D20 options chosen (O and X; v7 §4.2–4.3)**;
   - **the covariate table and rules (v7 §4.1)**.
6. **Specificity specification:**
   - estimands, tests, sidedness and multiplicity (v6 §9.4–9.5);
   - coverage (v6 §9.6);
   - covariates (v7 §4.1);
   - **δ with its scale, or "equivalence not used" (v7 §8)**.
7. The sample-set precedence rule and the sensitivity definitions (v7 §5).

The same lock governs every cohort. No cohort receives a different gene list, weighting, coverage,
mapping, covariate set or test specification. The lock also cites the SHA-256 of the source-tree identity record of every output it contains (v7:112) and the D8 environment record hashes.

---

## 8. Specificity conclusions and the equivalence margin (replaces v6 §9.7–9.8; resolves [FA] issue 7 and F9)

### 8.1 What requires δ

**Until δ is approved at Tier A5, on a defined effect scale, no result in this study can establish
any of the following:**

- that a PD association is negligible;
- that the signature is "compatible with no meaningful association" with PD;
- that the signature is **specific to AD**.

### 8.2 What can be reported without δ

| Output | Rule |
|---|---|
| Q1 score test (IPD primary; GPD and GU secondary) | Two-sided test, θ̂ with a two-sided 95% CI, direction relative to the AD signature (v6:635) |
| Per-gene tests | Two-sided; BH within contrast; β̂ with an unadjusted two-sided 95% CI (labelled); direction relative to d_g (v6:637) |
| Categories | "Association with PD — same direction as AD", "— opposite direction", **"association not demonstrated"** (v6:660–662) |
| S15 | Age-adjusted counterparts, labelled sensitivity |
| Descriptive | Coverage, R8 status, missingness |

**Rules that always apply:**

- **Non-significance is never evidence of absence.**
- AD specificity is never inferred from a significant AD result plus a non-significant PD result.
- No AD × PD contrast is estimable.
- Magnitudes are not comparable across cohorts (v6 §8.9).
- Specificity never alters the lock.

### 8.3 Q2 consequence, recorded for D13 ([FA] F9)

- If both Q1 and the optional directional Q2 are approved with Holm (v6:636), Q2 adds no AD-direction
  decision beyond Q1 and its sign.
- It also tightens opposite-direction detection to p₁ ≤ 0.025 [REASONING; FA F9].
- The choice remains D13.

### 8.4 δ scale and value — D13 options [DECISION NEEDED; no value proposed; nothing externally validated]

| Scale option | Definition | Considerations [REASONING] |
|---|---|---|
| Δ-score | δ on θ_PD (cohort-specific z-score units of S) | Directly matches Q1. The unit depends on the contrast composition and on coverage (v6 §8.9) |
| Standardized score difference | δ on θ_PD divided by the pooled within-group SD of S | Closer to a standardized mean difference. Still affected by coverage and correlation. Needs justification |
| Per-gene log2 | δ on |β_g,PD| on the GPL570 RMA log2 scale | Gene-interpretable. Platform compression differs from Illumina (v5:687–693) |
| Relative to the AD effect | δ as a fixed fraction of the discovery effect | Conflicts with the cross-cohort magnitude prohibition (v6 §8.9) unless a standardization is approved. The fraction must be fixed before discovery results |

**If δ is approved:**

- Test: TOST at α = 0.05 per bound, i.e. a 90% CI within ±δ.
- Multiplicity follows the corresponding Q1 or per-gene family.

**If δ is not approved:** "equivalence not used" is recorded in the lock, and §8.1 applies.

---

## 9. STOP cascade (replaces v6 §11)

As v6:740–747, with these changes:

- **Gating:** under V-A or V-C, gated analyses in a cohort with R8 status "not performed",
  "completed — uninformative" or "blocked" are reported as **"not assessable — R8"** (v7 §2.2–2.3).
- **Covariates:** a required covariate that is unavailable, or a non-estimable design, makes the
  cohort "not assessable" (v7 §4.1).
- **Stage gate not met** (v7 §1): a Tier B step or analysis does not start while any decision governing it is unapproved. For example, D5 unset or a non-permitted D5 × D22 combination blocks QC Stage A and every later step;
  an unapproved cohort- or analysis-specific decision blocks only that cohort or analysis. No stage is authorized while its governing decisions remain unresolved.

---

## 10. Cross-section audit after the v7 edits

### 10.1 Trace of the corrected rules

| Rule | Defined | Referenced consistently in |
|---|---|---|
| Error-rate claims | §4.2–4.3 | §7 item 5; §11 register D20; §1 A5 |
| Validation covariates | §4.1 | §7 items 5–6; §1 A5; §9; §11 D11/D20 |
| Model families A/B | §3.3 | §5.5; §6.1 reporting; §7 item 1; §11 D6 |
| Precedence tiers | §5.1–5.3 | §5.4 log; §6.1 counts; §7 item 7; §11 D16/D18 |
| D5 × D22 combinations | §2.2 | §1 A3; §9; §11 D5/D22 |
| v2 §7.5 status | §0.1; §6 | §1 A4 (assumption rule); §11 D7 |
| δ requirement | §8.1–8.4 | §1 A5; §7 item 6; §11 D13 |

### 10.2 Inherited wording now inactive

| Inactive text | Replaced by |
|---|---|
| v2 §7.5 "unless a prespecified failure rule is approved (D7)" (v2:361–362) | §6.3 |
| v1 §4.6 chip-confounding fallback (v1:158–160) | Already superseded by v5 §4; formally retired here |
| v2 §9.6 covariate table (v2:464–469) | §4.1 |
| v6:386 "sensitivity subsets (S1, S5, S12, S15)" | §3.3 family table |
| v6:577–580 hierarchy without error-rate statements | §4.2–4.3 |
| v6:183, 187 (V-A/V-C without combination rules) | §2.2 |
| v6:663 δ wording without scale | §8.1–8.4 |
| v6:702, 712, 714, 731 (re-inclusions without precedence) | §5 |

### 10.3 Confirmations

| Check | Result |
|---|---|
| D0–D22 IDs unchanged; only D1, D2, D3, D4 and D5 approved and D18 partially approved — D-3/D-4 handling only (2026-10-10, explicit PI instruction; §11), D22 partially approved — R8 variant V-A and §3.5 QC policy rows 1–6 only (2026-10-11, explicit PI instruction; §11), D6 partially approved — gene-level option G3, S8 alternative G1 and freezing rule (2026-10-12) and gene-history cutoff 20260318, gene-history procedure and GPL570 mapping (Option A) (2026-10-13) and Illumina annotation policy for GSE63060/GSE63061 (D6-G, Option A0) (2026-10-17) only (explicit PI instruction; §11), D0 approved as a governance designation only (2026-10-14, explicit PI instruction; not approval of the SAP; §11), D17 approved — Option A, D18 D-1u ruling, GSE99039 title rule, R-rep1 rule and precedence rule (§5.2), and D22 exclusion-list approval scope (policy only) (2026-10-15, explicit PI instruction; §11), D18 D-2 option (c) (2026-10-15, explicit PI instruction; §11), D18 D-1 handling and review workflow/log (2026-10-18, explicit PI instruction; §11), QC Stage A ruling (GSE63060: compute and record only; 2026-10-18, explicit PI instruction; §11), the H1 analysis specification, D7, D15, D16 (with S-R8m) and the R8 review outcome (2026-10-18) (explicit PI instruction; §11), D8 approved for environment readiness only (D8-8, 2026-10-18, explicit PI instruction; no real-data execution authorized; §11), all others unapproved | Yes |
| Gate status unchanged | Yes |
| E2 and eligibility unchanged | Yes. The tiers in §5 restate the existing rules |
| Lock fixed across cohorts | Yes |
| Non-significance ≠ absence | Yes |
| No new confirmatory test or threshold silently approved | All additions are [PROPOSED] or [DECISION NEEDED] |

---

## 11. Decision register (D0–D22; D1, D2, D3, D4 and D5 approved and D18 partially approved — D-3/D-4 handling only, 2026-10-10, and D22 partially approved — R8 variant V-A and §3.5 QC policy rows 1–6 only, 2026-10-11, and D6 partially approved — gene-level option G3, S8 alternative G1 and freezing rule (2026-10-12) and gene-history cutoff 20260318, gene-history procedure and GPL570 mapping (Option A) (2026-10-13) and Illumina annotation policy for GSE63060/GSE63061 (D6-G, Option A0) (2026-10-17) only, and D0 approved as a governance designation only (2026-10-14; not approval of the SAP), and D17 approved — Option A, the D18 D-1u ruling, GSE99039 title rule, R-rep1 rule and precedence rule (§5.2), and the D22 exclusion-list approval scope (policy only) (2026-10-15), and the D18 D-2 option (c) (2026-10-15), and the D18 D-1 handling and review workflow/log (2026-10-18), and the QC Stage A ruling (GSE63060: compute and record only; 2026-10-18), and the H1 analysis specification, D7, D15, D16 (with S-R8m) and the R8 review outcome (2026-10-18), and D8 approved for environment readiness only (D8-8, 2026-10-18; no real-data execution authorized), by explicit PI instruction, marked §; all others unapproved)

† = changed in v7. ‡ = option list reconciled with the retained active text (targeted register reconciliation; wording and sources cited; no decision status changed; nothing approved). § = approved by explicit PI instruction, on the date given in the row. The approval covers only that row's stated decision and conditions. **"Depends on" (C1 ruling — review item C1, not the C1 metadata candidate source of v6:216 — 2026-10-15, explicit PI instruction; reading R-1):** a listed dependency indicates interaction in content or execution, not an approval prerequisite, unless the row explicitly states otherwise. The ruling itself approves no decision and changes no decision status or gate.

| ID | Proposed default | Open options | Tier                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Depends on |
|---|--|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| D0 § | **APPROVED 2026-10-14 (explicit PI instruction) as a governance designation only: SAP v7 (this file, with the retained text mapped in v7 §0.1) is the governing statistical analysis document for BIO-MB-001.** This designation is not approval of the SAP: v7 remains a proposed draft, not approved and not frozen (v7:3), and no hypothesis is approved. The Notion planning pages Statistical & Validation Plan (last edited 2026-10-13T19:31Z), Analysis Plan (2026-10-09T12:01Z), Hypotheses & Predictions (2026-10-09T11:58Z), Hypotheses (2026-10-07T15:01Z), Research Question (2026-10-07T15:00Z), Questions (2026-10-09T11:54Z), Project Roadmap (2026-10-07T15:03Z), Dataset Registry (2026-10-09T12:45Z) and Decision Log (2026-10-09T12:29Z), as read on 2026-10-14, are retained as historical and contextual planning material; where they conflict with v7, v7 governs, and no Notion content is adopted unless a separately approved decision incorporates it. Approved decisions (D1–D5; the approved parts of D6, D18 and D22) stand, including where earlier provisional Notion text differs (e.g. the GSE63060 non-normalized-file preference versus D3). Conflicts requiring their own decisions: competing hypothesis sets (including pathway coherence as a hypothesis); machine-learning scope; the role of GSE165082; the gene-count cap (D15); the replication criterion (D20/D12); the reported 19-participant GSE63060/GSE63061 overlap (unverified; no cited source); the roles of GSE140829; the research-question wording. D0 approves no hypothesis (H1–H3), no D1–D22 component beyond those already approved, no dataset role, and no QC, differential-expression or other analysis, and changes no gate status or dependency. | Notion pages as the governing plan (not chosen); deferral of D0 (not chosen) | A1 | — |
| D1 § | **H1 analysis specification § — separate approval, 2026-10-18 (explicit PI instruction; the proposals of v5:397 and v5 §5.4):** primary model for GSE63060 AD vs CTL (E2): adjustment for age (linear; D4), recorded sex and chip (unit); test: limma moderated t with trend = TRUE (D8 runner: lmFit + eBayes(trend = TRUE, robust = FALSE)); multiplicity: Benjamini–Hochberg within the gene-level family, claims at q < 0.05 (D15); the probe-level family is reported separately and never mixed (v5 §5.4). Caveat: recorded sex disagrees with expression-derived sex for 46 GSE63060 arrays (R8 review, v7:625). This approves no analysis by itself; the remaining Tier B steps and gates apply. **APPROVED 2026-10-10 (explicit PI instruction): E2.** Primary comparison: GSE63060 samples labelled "AD" vs "CTL" in the deposited GEO `status` field. **Mandatory caveat:** about 41 of the 145 GEO-labelled AD samples were probably MCI at blood collection. This is a group-level inference from published cohort-level correspondence, not verified individual-level classification, and the individuals' identities are not known. The estimand therefore concerns deposited AD labels, not confirmed AD diagnosis at blood collection. S4 is only a labelled, convention-dependent sensitivity; excluding M-coded samples is never equivalent to E1. The published 41 vs 42 converter discrepancy remains unresolved. D1 approval does not approve D2–D22, H1–H3, thresholds, models, other analyses or any gate. **D1-H § — separate approval, 2026-10-14 (explicit PI instruction): the wording of primary hypothesis H1 only, verbatim from SAP v1 §1 (v1:35–36): "some genes are differentially expressed between GEO-deposited AD-labelled samples and deposited healthy controls, after prespecified adjustment", stated for estimand E2 with its mandatory caveat.** The 2026-10-10 E2 approval did not approve H1–H3; D1-H is a later, separate approval of the H1 wording alone. D1-H does not approve the adjustment set, the statistical test or model, the evaluation threshold (D15), or the multiplicity rule (D15; v6 §6.5), and it authorizes no analysis; each requires its own approval before the corresponding real-data QC or analysis (v7 §1, rule 1). H2 and H3 (v1:37–42) remain [PROPOSED], to be decided with D20/D12 (with D10/D19) and D13 respectively; no Notion wording is adopted. Pathway or biological coherence is not a hypothesis of this SAP; pathway analysis remains exploratory (v5 §9; D14). "H1–H3" here means the v1 §1 hypotheses, not the discrepancies H1–H9 of v2 §3.3. Source as read on 2026-10-14: reports/phase3b/v1/STATISTICAL_ANALYSIS_PLAN_DRAFT.md, SHA-256 27b99212733cc91869445e09e71290b7ca10558bae8401dd516a15c7982d9820; this hash identifies the file as read and is not evidence of its earlier integrity (no earlier independent record exists). D1-H changes no gate | E1 via D9: considered later only if suitable sample-level evidence becomes available and E1 is separately prespecified before its relevant analysis | A2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D9 |
| D2 § | **APPROVED 2026-10-10 (explicit PI instruction): GSE63060 eligibility rule definitions.** R1: the 329 GSM columns of the GSE63060 Series Matrix are the eligible deposited sample universe. R2-ID: exact-string uniqueness of GSM, barcode and participant code; uniqueness does not prove biological participant identity. R2-COV: complete-case eligibility per statistical model. R3: primary contrast by GEO `status` AD vs CTL. R4: MCI retained in the dataset but outside the primary contrast. R5: the existing missing/borderline/transitional/non-specific/conflicting-label rule. R6: no exclusion or relabelling based on inferred converter status or undocumented participant-code letters. R10: inherited submitter QC documented as not independently auditable where sample-level exclusion records are unavailable. R11: expression-only arrays or empty-header columns lacking eligible GEO GSM records are excluded and do not become additional samples. R12: the undocumented Sood "included in case-control study" flag is not used for primary eligibility. R13: a checksummed eligibility/exclusion log is created before any case–control model. Pre-QC primary contrast: 145 GEO-labelled AD vs 104 GEO-labelled CTL; the 80 MCI remain outside it. **Not approved or fixed by D2:** R7 (D4 age policy); R8 (D5/D22 sex QC); R9 (array-outlier criteria and related QC); expression-based duplicate handling and precedence (D18). Code letters are not used to infer converter status. D1 caveat (context, not a D2 approval): about 41 of the 145 AD samples were probably MCI at blood collection (group-level inference) | — | A2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D1, D18 |
| D3 § | **APPROVED 2026-10-10 (explicit PI instruction):** `data/raw/GSE63060/GSE63060_series_matrix.txt.gz` (329 GSM sample columns × 38,323 probes) is the primary GSE63060 expression input, used as deposited **without additional normalization or transformation**, following the D2 eligible GSM universe. It is verified identical to `GSE63060_normalized.txt.gz` across all 12,608,267 shared values; the supplementary normalized file is not a separate primary input. The deposited values are already transformed and processed; the exact LUMI parameters and filtering procedure remain undocumented. Normalization may have included arrays not in the eligible GSM universe; the effect is unquantified. Annotation and probe-to-gene mapping remain for D6/D8; QC and outlier decisions for D5/D22/R9. D3 approves no other analysis choice and resolves none of these uncertainties | S10: re-normalization of `GSE63060_non-normalized.txt.gz`, a sensitivity option only, subject to D16 (**not approved by D3**) | A2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | — |
| D4 § | **APPROVED 2026-10-10 (explicit PI instruction): no age-based exclusion** in the primary GSE63060 AD vs CTL discovery contrast; GEO `char:age` included as a **linear covariate**. All 145 GEO-labelled AD and 104 CTL samples are retained before QC; all 21 under-65 samples (AD 10, CTL 8, MCI 3) remain in the eligible dataset, and MCI stays outside the primary contrast (D2 R4). **Caveats:** the papers state that participants under 65 were excluded, but GEO contains 21 under-65 samples. This discrepancy is unresolved; the analysis choice neither establishes the original recruitment criteria nor proves these samples were eligible or ineligible at recruitment. The meaning of GEO `char:age` (age at blood collection vs another time point) is unverified, and the observed GEO age field is distinct from the original study's stated eligibility criterion. Sensitivities, subject to D16 (not approved by D4): S1(a) restriction to age ≥ 65 (pre-QC 135 AD / 96 CTL); S1(b) restriction to ages 61–88 inclusive (141 AD / 99 CTL); S2 age as the existing 3-df spline, with no age-based exclusion (a covariate-form change, not a restriction) | ≥ 65 and spline remain only as S1(a) and S2, subject to D16 | A2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | — |
| D5 † § | **APPROVED 2026-10-10 (explicit PI instruction): option (b)**: R8 without a validated separation threshold (no D_min); separation, usability and informativeness per v7:133; D computed and reported descriptively only. **Unvalidated operational conventions** (not scientifically validated thresholds): R8 n_min = 5; tie tolerance 10⁻¹²; ≥ 2 distinct Y genes; probe list XIST ILMN_1764573 and 13 Y probes: RPS4Y1 ILMN_1783142; DDX3Y ILMN_1732039; KDM5D ILMN_1685690; UTY ILMN_1739587, ILMN_2264634; EIF1AY ILMN_1755537, ILMN_2228976; USP9Y ILMN_2056795; ZFY ILMN_1804958, ILMN_2090059; CYorf15A ILMN_1670821; CYorf15B ILMN_1756506, ILMN_2094332 (v2:175–176; the same 13 Y probes for GSE63061). R9 k = 3; minimum 10 arrays; near-identical tolerance r ≥ 1 − 10⁻⁸. The "[PROPOSED (no source)]" tags at v5:152, 164, 166, 245, 250 and v6:219, and "provisional" at v5:260, now read "approved under D5 as an unvalidated operational convention; no source". D5 approves no D22 rule (variant, sample exclusion or GSE63061 policy), no further D18 component, and no S16 or other analysis; Tier A3 remains incomplete until D22 is approved as a permitted combination (v7:143–148) | (a) unavailable (no D_min source); (c) not chosen | A3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D22 |
| D6 † § | **PARTIALLY APPROVED — 2026-10-12 (D6-A to D6-D) and 2026-10-13 (D6-E, D6-F) (explicit PI instruction): gene-level option, S8 alternative, freezing rule, gene-history cutoff, gene-history procedure and GPL570 mapping only (scope of the 2026-10-12 and 2026-10-13 approvals; the separate D6-G Illumina approval of 2026-10-17 is recorded below).** (1) **D6-A — primary gene-level option G3** (v5:421; v6:330): u_g(i) is the mean of the eligible probes of gene g on the deposited scale (the single probe if only one), eligible probes being those eligible under the finally approved annotation and eligibility rules (v5:408). The estimand is the average probe signal: opposing probe effects can cancel, and no claim is made about a particular probe (v5:443–444); constituent probe sets differ by platform (v5:450–451). This decision introduces and approves no feature-filter rule (D17 unchanged). (2) **D6-B — S8 alternative G1** (v5:418; v6:327): S8 builds its own T_c by G1 with the same sets and freezing (v7:197; v6:361); S8 is defined but may not run until D16 is approved. (3) **D6-C — freezing rule and selection sets:** the freezing rule as stated in v7 §3.2 (v7:191–204) and the selection sets at v6 §6.2 (v6:327–328) are approved as written; the three alternatives at v6:367–371 are rejected. (4) **D6-D — annotation resource:** read-only verification of candidate annotation resources is authorized; no annotation resource, release, release-specific mapping rule (v5:540–541) or installation is approved. (5) **D6-E — gene-history cutoff (approved 2026-10-13, explicit PI instruction):** if NCBI Gene history is used to reconcile historical Entrez Gene IDs in the primary mapping, only entries dated on or before 20260318 (the Entrez Gene snapshot date of org.Hs.eg.db 3.23.1) may be applied; later entries remain visible as timing discrepancies (reports/annotation_audit/ncbi_gene_history/v1, View B) and must not alter the frozen primary mapping. D6-E does not approve the annotation resource, the use of gene history in the mapping, or the mapping rule. (6) **D6-F — GPL570 mapping, Option A (approved 2026-10-13, explicit PI instruction):** GPL570 (GSE99039) probe sets are mapped to Entrez Gene IDs with hgu133plus2.db 3.13.0 (Bioconductor 3.23; archive SHA-256 ddde58e777a8341536a664c7d4be874a2f395f8aaa019c1f738462a8ce74cc44, matching reference/bioconductor_3.23/download_manifest.json; probe-to-gene knowledge from Entrez Gene dated 2021-04-14). The reference Entrez-ID snapshot is org.Hs.eg.db 3.23.1 (Entrez Gene, 2026-03-18). Package Entrez IDs absent from the reference snapshot are reconciled by the NCBI gene-history reconciliation procedure, which is approved here as a procedure, separately from the D6-E cutoff: the View A rules of reports/annotation_audit/ncbi_gene_history/v1 (successor taken only from the GeneID field, never from symbols; GeneID "-" = no replacement; every chain step recorded; cycles, duplicate records and unresolved successors left unresolved), applying only records dated on or before 20260318. For GPL570 the clause "every platform annotation comes from one pinned release sharing an Entrez snapshot" (v5:540; v5 unchanged, amended here) reads: a platform-specific annotation release may be used provided its Entrez IDs are reconciled to the single reference snapshot by this procedure; the Entrez-ID match key, the exclusion of multi-mapped probes (v5:541) and the rule that IDs without a replacement become "unmapped" and are counted are retained. Classifications, exclusions and collision flags are as recorded in reports/annotation_audit/gpl570_option_a/v1 (probe_set_classification.tsv SHA-256 9e5f23fa8b10b3e120b518873905b79e5f338ca07ec83357e173d3a2ddea8d9c): 43,111 probe sets with one eligible gene (43,086 direct, 25 via replacement), 38 discontinued without replacement, 1,562 multi-gene (excluded), 9,964 without a gene; 16 probe sets (12 genes) flagged as collisions, not merged. Limitation: the GPL570 probe-to-gene knowledge dates to 2021-04-14; presence in the GSE99039 Series Matrix and D17 are not assessed. D6-F supersedes D6-D for GPL570 only; it covers no Illumina platform and approves no package installation. This approval authorizes no analysis. **D6-G § — separate approval, 2026-10-17 (explicit PI instruction): Illumina annotation policy, Option A0, for GSE63060 (GPL6947; illuminaHumanv3.db 1.26.0, archive SHA-256 cea0c9cd155197154d57400cb3f18108e451cf26e714c39698d68e45cd503a1b) and GSE63061 (GPL10558; illuminaHumanv4.db 1.26.0, archive SHA-256 362848d6e78c7fa6206e1a4c68a4b68c1ea065267d550114837bc3b9d833ee85), as identified in reference/bioconductor_3.23/download_manifest.json.** (1) Each probe takes the Entrez Gene identifier or identifiers recorded in the probes table of the designated package. NCBI gene-history records are not used to reconcile discontinued identifiers to successors; identifiers absent from the org.Hs.eg.db 3.23.1 Entrez snapshot (archive SHA-256 470620665cf49d0319422731164f377e3e74253989f1d33a8a1d100cc3d49cfe) are not rescued through gene history, and a package identifier with no eligible current mapping is unmapped and counted. This does not establish biological equivalence between historical and current identifiers. D6-F and D6-G use org.Hs.eg.db 3.23.1 as their shared Entrez eligibility snapshot (v6:482); the platform annotation packages remain distinct releases, and this shared snapshot does not by itself resolve every aspect of the release-pinning requirement. (2) Probes assigned more than one Entrez Gene identifier by the package mapping are excluded from gene-level aggregation and counted separately (v5:541); this is distinct from accessions that link to more than one gene in the comparison database. (3) A probe whose single eligible package-assigned identifier differs from the unique identifier linked by its recorded accessions in org.Hs.eg.db 3.23.1 is retained under the package mapping, flagged and listed with both identifiers, platform and cohort presence; it is not excluded solely because the two routes disagree. The accession comparison is an annotation-stability check, not independent validation. (4) For eligible probes, accessions with no current gene link (accession_unmatched) and accessions linking to more than one gene (ambiguous) are reported separately and do not override the package mapping; probes eligible only under the accession comparison are not added. (5) Presence is determined separately for GSE63060 and GSE63061 from each cohort's Series Matrix ID column (v5:544); platform-wide classifications and cohort-present counts are reported separately. (6) Gene-history successor collisions are not applicable under A0. (7) The annotation audit records the archive versions and SHA-256 values, the org.Hs.eg.db 3.23.1 snapshot, the accession-comparison and A0 classification-generation script versions and SHA-256 values, and the final A0 classification table with its SHA-256, and identifies unmapped, excluded and discordant probes, accession-comparison categories and cohort presence. The existing tables in reports/annotation_audit/illumina_option_a/v1, the C15 route_status fields and the decision-matrix counts apply gene-history reconciliation (Option A) and are not the final A0 classification; generating and verifying the final A0 classification table requires separate authorization. Reported evidence, not a substitute for the final A0 classification: applying A0 is expected to leave unmapped the 45 GSE63060 and 41 GSE63061 cohort-present probes that were replacement-derived under Option A, leaving 10 and 15 genes, respectively, without a cohort-present probe. The previously reported cohort-present discordant probes (9 in GSE63060 and 15 in GSE63061; 15 distinct probe IDs) are all directly mapped and therefore remain the same set under A0, subject to confirmation against the final classification. D6-G does not change D6-F (GPL570) or D19 (GSE140829) and authorizes no package download or installation, no generation of the final A0 classification table and no analysis. **D6-G A0 classification — generated and verified 2026-10-17 under separate PI authorization:** reports/annotation_audit/illumina_a0/v1 — a0_probe_classification.tsv (SHA-256 6da6cf2c1d7d1911c17301d60c1f153f91856f405f7fde1faf6f553b3013ae7c), a0_counts.tsv (a68aa75080026e175cb148994c42f4fbc38d0a3c386a526dc12cb0b63887d625), a0_discordant_probes.tsv (e5b99695ac5b600bba0157c1d9b673be5f20a513e43e5887d0b7c6faccb85958), manifest.json (e797fdaf841e1e1806d98e528c859fef0ed4658c27eb83e8de5952e14c39151b). Code, identified by content hash only (no version string; not under version control): generator scripts/annotation_illumina_a0_classification.py (7b017d19b2fe8ec41a40a39f7b6b3b255d9c410a0c56fef0f7b7133f25bf9adf); accession-comparison logic scripts/annotation_illumina_route_comparison.py (09f1675d17e0ab23d54b7a42d6f42b624640ffbd0191a84a7c31ebeb47319193); Series Matrix ID reader scripts/c15_cohort_probe_presence.py (2b726833b35d109c3a9465973d807f11b5b48bf43f576079aad43b314abb1e3b). Inputs: the three archives above, verified against reference/bioconductor_3.23/download_manifest.json; data/raw/GSE63060/GSE63060_series_matrix.txt.gz (342421d07105d786d623a4b86dc4a21b764da352e4facc7a032fbd36b0f19371) and data/raw/GSE63061/GSE63061_series_matrix.txt.gz (c6de1af5bd36bca3de0921d53051bdefd05666f6e94a6906a26c8cb461dd55f5), probe identifiers only; no gene-history input. Verification: 18 built-in integrity checks passed; an independent re-audit passed (schema rules; presence against both Series Matrix ID columns; recomputed platform-wide and cohort-present counts; discordant probes 10 and 16 platform-wide, 9 and 15 cohort-present, 15 distinct IDs; eligible, multi-ID and no-gene sets equal to the Option A table's; 45 and 41 present probes left unmapped and 10 and 15 genes without a present probe; byte-identical rerun). Cohort-present eligible probes and genes: GSE63060 25,305 and 17,425; GSE63061 24,031 and 16,190. These verified artifacts replace the reported Option A-derived evidence above for D6-G purposes; the Option A tables remain historical comparison evidence. The classification is not an annotation pin and does not complete Tier B step 2. **Annotation pin definition (D1, approved 2026-10-17, explicit PI instruction):** Tier B step 2 is completed by an immutable, hash-recorded annotation pin record at reports/annotation_audit/annotation_pin/v1, listing the approved classification tables with their SHA-256 (GPL570: D6-F, reports/annotation_audit/gpl570_option_a/v1/probe_set_classification.tsv; GPL6947 and GPL10558: D6-G A0, reports/annotation_audit/illumina_a0/v1/a0_probe_classification.tsv), the source archives with their SHA-256, the shared Entrez snapshot org.Hs.eg.db 3.23.1, the governing mapping rules (D6-F, D6-G), the generating scripts' SHA-256, the provenance manifests and the validation evidence. Provisional Option A tables (reports/annotation_audit/illumina_option_a/v1) remain provisional and are never pinned. The pin does not install annotation packages. Creating the pin record is a separately gated later step: it follows D8 (Tier B step 1) and requires its own authorization; this definition does not create it. **Remain unapproved:** the annotation resource, release and mapping rule for GSE140829 (D19 unchanged); installation of any annotation package (separately authorized only if a later step requires it); creation of the annotation pin record is no longer outstanding: it was created 2026-10-18 under explicit PI authorization from the verified v2 artifacts (reports/annotation_audit/annotation_pin/v1/annotation_pin_record.json, SHA-256 cde8ccd7d87b3622227a1b174599c4786fa94906159707fc4e498c72f3253a67; manifest SHA-256 d48309e7f900f5434e592317b32fa8c09ed2661b2da470f7e7662ef12bebe930) | G1b, G2 not chosen; selection alternatives (v6:367–371) rejected; for D6-G, Option A (gene-history reconciliation for Illumina) and the accession route not chosen | A5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D8 |
| D7 † § | **APPROVED 2026-10-18 (explicit PI instruction):** c₁ = 3 (minimum mixed units — chips, or batches where no chip is recorded — containing both compared groups), c₂ = 5 (minimum arrays of each compared group on mixed units), c₃ = 10 (maximum VIF_g), common to all cohorts; with the proposed η = 10⁻⁸, scaling and rank tolerance (v5:324–326); conventions without a published source, fixed before any M-check output and without inspection of diagnosis by chip; assumption rule as proposed: diagnostics descriptive, no failure rule (§6.3). Approves no analysis by itself. Previously: v5 §4.4 procedure; c₁–c₃ unset; **assumption rule: diagnostics descriptive, no failure rule (§6.3)** | c₂ minority count; residual df; a prespecified failure criterion and fixed alternative model | A4                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D4, D2, D18, D22 |
| D8 § | **APPROVED FOR ENVIRONMENT READINESS ONLY — 2026-10-18 (D8-8, explicit PI instruction), within the scope and limitations of the D8-8 decision record.** Environment evidence and limitations: the conda layer is reconstructed from the conda explicit specification (545 archive SHA-256 values verified; the installed interpreter hash depends on the install prefix; the 77 pip-installed Anaconda base packages are outside that specification and its reproducibility claim, and project Python runs only through .venv); the Python lock reports/environment/python_lock/v2 covers CPython 3.13.9 on macOS arm64 only (16 wheels matching PyPI-published hashes; package index inferred); the project R library equals the renv.lock restore, with BiocVersion the official Bioconductor 3.23 binary (build-machine provenance and functional identity with the earlier source-built copy not established); R 4.6.1 is verified at installer, receipt and installed-file level (CRC32, not cryptographic; not reinstalled); biomarker-project is outside D8 scope; platform macOS 26.6.2 arm64 on this machine only; no claim of analysis reproducibility or cross-platform numerical identity. Code identity: the documentary prerequisites are complete (v7:112 requires a verified source-tree identity record on every real-data output; v7:486 requires the lock to cite those records and the D8 environment record hashes; environment-record verification in src/biomarker_project/code_identity.py passed its synthetic tests); the operational prerequisite is not met: no real-data runner yet implements the capture, manifest and post-run verification lifecycle, and real-data execution remains prohibited until the applicable runner calls capture() before computation, writes code_identity.json and enters its SHA-256 in the output manifest, calls verify() after computation and fails closed on any substantive mismatch, and passes synthetic tests of that lifecycle. This approval does not approve the SAP as a whole, annotation pin creation, Tier B, QC, differential expression, validation, model training or any other real-data analysis, runner execution, or any download, installation or environment change. Pinned R/Bioconductor. Factual status: R 4.6.1 (system, outside renv), Bioconductor 3.23 and the project renv library pinned by renv.lock SHA-256 fa51c7b9d10dd468fbeed8b2ad83b832eb8acc83adb828dc25361cbbc4359951 (limma 3.68.5, statmod 1.5.2, BiocVersion 3.23.1, BiocManager 1.30.27, renv 1.3.1) were installed 2026-10-12 as recorded in reports/environment/D8_R_LIMMA_INSTALLATION.md (SHA-256 a5b3d2ffc6d02cded9732b6e0221f0e45c605c7d093f77104dc2e2e2e4182171); that installation did not by itself approve D8; no annotation or pathway package is installed. **D8 scope (D3, approved 2026-10-17, explicit PI instruction):** the D8 record covers R 4.6.1 with its installer record; renv.lock with its recorded SHA-256; the R restore evidence, including the documented caveat that renv restores BiocVersion from the r-universe-built binary (same version and git commit, different Repository/Depends metadata; reports/environment/D8_R_LIMMA_INSTALLATION.md §3a); the project Python environment (CPython 3.13.9, Anaconda base build hc7d8306_100_cp313; exact package versions in reports/environment/python_lock/v1; installed-file digests in reports/environment/d8_readonly_checks/v1); a recorded conda explicit specification of the base environment; the BLAS/LAPACK and sqlite details; and the platform scope macOS 26.6.2 arm64, with no claim of cross-platform numerical identity. A throwaway rebuild test was performed 2026-10-17 under explicit PI authorization (reports/environment/d8_rebuild_test/2026-10-17/D8_REBUILD_TEST_REPORT.md, SHA-256 f19cc744b3968f44134af61d25d06ab3d22096e79101eea276d0028e2d9b2de7): the conda layer (conda explicit specification reports/environment/d8_environment_capture/v1/conda_explicit_base.txt, SHA-256 52e2e785b7e7c92a0435beab3476fbb7966047ea920ad9bfcd15a1cd5b3eb731) and the 16 third-party Python packages were reconstructed and verified, and the R packages restored at their locked versions with BiocVersion restored as the official Bioconductor 3.23 binary; R 4.6.1 was verified at installer and installed-file level, not reinstalled; the local project package was not built. D8 decisions D8-1 to D8-6 (explicit PI instruction, 2026-10-18) and their implementation, including the hash-pinned Python lock in reports/environment/python_lock/v2 and the replacement of the project library's source-built BiocVersion with the verified official binary (renv.lock unchanged), are recorded in reports/environment/d8_closure_review/2026-10-18/D8_EXECUTION_REPORT.md; D8-8 was approved 2026-10-18 for environment readiness only (see the start of this row). Reconstruction on this machine does not demonstrate reproducibility of analyses. Defining this scope does not approve D8 | Validated alternative | A6                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | — |
| D9 | Request | — | Enabling                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | — |
| D10 | "Unverified" | — | Enabling                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | D9 |
| D11 † | Series Matrix + batch; covariates per §4.1; S13 covariate and unit rule open | ComBat | A5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D19 |
| D12 | C-c; C-a; C-b descriptive | Inferential C-b | A5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D15, D20 |
| D13 † ‡ | v6 §9.1–9.6; S15 "[PROPOSED; D13/D16]" (v6:718); **δ and its scale unset → no negligible or specificity conclusion (§8)** | Q2 (consequence §8.3); Holm across contrasts; GPL570 coverage; δ scale options and δ value or "equivalence not used" (§8.4); replicated-genes-only analysis "only as a separately prespecified, labelled analysis" (v6:611–612); GENETIC_UNAFFECTED interpretation "left to D13" (v6:620); S15 multiple imputation, "a possible alternative" not proposed (v6:723) | A5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D6, D12 |
| D14 ‡ | As v5 §9 (v5:699–715) | Inter-gene correlation "estimated or fixed" [DECISION NEEDED; D14] (v5:709); collections and versions "unpinned until D8 and D14" (v5:714) | A5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D6, D8 |
| D15 ‡ § | **APPROVED 2026-10-18 (explicit PI instruction):** q < 0.05; signature cap 200; per-direction coverage 50% and min(5); no coverage restriction at selection (conventions without a published source, v6:510). Approves no analysis by itself. Previously: q < 0.05; 200; per-direction coverage (all [PROPOSED]; v6:422, 510) | Other values of these proposed conventions; coverage restriction at selection "(alternative: D15)" (v6:431) | A5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | — |
| D16 † § | **APPROVED 2026-10-18 (explicit PI instruction):** S1–S16 with the §5.3 sample sets, as defined; plus S-R8m (R8 review outcome R3, v7:625): the primary population with the 46 GSE63060 arrays whose two strongest Y markers both disagree with recorded sex removed (reports/qc_stage_a/GSE63060/r8_diagnostics/v2/r8_marker_calls_series_matrix.tsv). Anything the definitions leave open remains open; no sensitivity replaces the primary analysis; approves no analysis by itself. Previously: S1–S16 with the §5.3 sample sets | — | A5 | D4–D7, D13, D18, D21 |
| D17 § | **APPROVED 2026-10-15 (explicit PI instruction): Option A**: no additional expression filter in the primary discovery analysis. The proposed default is retained to preserve potentially relevant low-expression features and avoid an unnecessary additional filter. S7 sensitivity analyses apply the 25th- and 50th-percentile expression filters, separately from the primary analysis. Any expression-filter threshold is calculated using mean expression across all eligible samples, without diagnosis labels or between-group variance to select features. Status: user selection received 2026-10-13; approved 2026-10-15 by explicit PI instruction, covering only the policy stated in this row; the SAP remains unapproved and unfrozen (v7:3). The listed dependency on D15 is an interaction in content or execution, not an approval prerequisite (C1, v7:599); D15 remains unapproved. S7 is defined but may not run until D16 is approved. This decision does not authorize QC, differential-expression analysis, or any other analysis, and does not override any other approval gate. | S7: 25th- and 50th-percentile filters as sensitivity analyses; no additional expression filter in the primary analysis | A2 | D15 |
| D18 † § | **PARTIALLY APPROVED — D-3/D-4 handling only, 2026-10-10 (explicit PI instruction):** (1) option B: all D-3/D-4 arrays are retained in the primary analysis unless another independently approved rule excludes them; (2) S16 option 1: every array in each qualifying D-3/D-4 cluster is excluded in S16, with no representative selected; (3) label-discordant clusters are retained in the primary analysis under their deposited labels and excluded in S16 like any other qualifying cluster; (4) a qualifying cluster is a connected C2 cluster containing at least one D-3 or D-4 pair, and independently applicable exclusions remain in force. Differing undocumented participant codes do not prove distinct biological participants. **D-1 handling and review workflow/log § — separate approval, 2026-10-18 (explicit PI instruction; the proposed wording, items (i)–(v), approved as written, including item (iii) in full):** (i) no participant-identifier field is designated for GSE63060 or GSE63061; the description codes are undocumented. (ii) D-1 applies only to a deposited replicate annotation naming its partner: keep one array (not labelled as a replicate, otherwise lowest GSM; v6:248), exclude and list the others (Tier P2); if the arrays carry different deposited diagnosis labels, exclude all of that participant's arrays from every contrast in that cohort in which any would otherwise be eligible, report the labels descriptively, and relabel nothing. (iii) Any other candidate link, including a shared description value, is D-1u: retained under deposited labels, flagged, listed and reported descriptively; sensitivity treatment deferred to D16. A non-unique GSM accession or array identifier remains an R2-ID identity failure; D2 is unchanged. (iv) The designated project reviewer receives the blinded table (v6:237); the log also records the reviewer's name, the review date and the rationale for the retained array. (v) The §5.4 descriptive report extends to D-1 and D-1u. Still unresolved: the R2-ID scope (cohort-wide vs per contrast); the designated project reviewer has not been named. This approval does not approve D16 or any analysis. The C2 similarity tolerance is approved under D5 (2026-10-10) as an unvalidated operational convention; S16 is defined but may not run until D16 is approved; this approval authorizes no analysis. **D-1u ruling § — separate approval, 2026-10-15 (explicit PI instruction; review item C2, not the C2 expression candidate source of v6:218):** arrays linked only by a shared undocumented description (participant-code) value are D-1u: retained under their deposited labels, flagged, listed and reported; any sensitivity treatment is deferred to D16. A duplicate GSM accession or array barcode remains an R2-ID identity failure (Tier P2). A description-value match is not evidence of participant identity. D2 (v7:605) is unchanged; the R2-ID participant-code check is still run and reported; where the participant code is an undocumented description value (as in GSE63060/61), a non-unique value is handled as D-1u, not excluded. A shared documented, designated participant-identifier field is not covered by this ruling. This ruling does not approve D-1 handling, a flag-tier label, S17, the review workflow/log or the precedence rule, and authorizes no analysis. **Precedence rule § — separate approval, 2026-10-15 (explicit PI instruction):** the precedence rule of §5.2 as written (v7:358–369); this approval does not approve any sensitivity set (D16), the D-2 option, or any analysis. **GSE99039 title rule § — separate approval, 2026-10-15 (explicit PI instruction):** for GSE99039 (Affymetrix), no array identifier is defined. The GEO title is checked for uniqueness only; a duplicated title is an unresolved duplicate-review candidate, not an R2-ID exclusion. Title uniqueness, and correspondence between titles and CEL file names, are not validation of array identity. For GSE99039 this replaces the proposed use of "the title string where no barcode exists" as an array identifier (v3:103–104). Unresolved candidates block progression only as provided by an approved duplicate-review workflow. **R-rep1 § — separate approval, 2026-10-15 (explicit PI instruction):** a deposited "replicate 1" with no other replicate annotation is not a duplicate-review candidate. This rule does not establish that such arrays are independent and does not exempt them from any other candidate source or rule (GSM accession or array-identifier duplicates, shared undocumented description values, C2 expression similarity). It is independent of the D-2 option. **D-2 § — separate approval, 2026-10-15 (explicit PI instruction): option (c) for GSE140829 "replicate 2"** (v3:148–152, via v6:244): the four arrays deposited with description "replicate 2" (GSM4187770, GSM4187771, GSM4187772, GSM4187773; data/metadata/GSE140829/GSE140829_samples_brief.soft.txt) are Tier Q3 and are excluded from the primary sample set (v7:352, 375). The sensitivity is S14 as defined at v7:384 under the precedence rule (v7:364–365): it re-includes only arrays whose only Tier P/Q reason is Q3. The GSE140829 replication contrast is AD vs Control (v7:266; score samples are eligible AD + CTL, v6:502): GSM4187770 and GSM4187773 carry the deposited label MCI and have no group in that contrast, so S14 cannot re-include them in it; this does not define their eligibility for any other analysis, and they remain among the cohort's deposited arrays for cohort-level QC (v7:351). GSM4187771 (Control) and GSM4187772 (AD) are the only arrays S14 could re-include, and only if neither has any other Tier P or Q reason. Practical condition (not an explicit SAP rule): an array must be present in the selected input file to be available for re-inclusion (input unresolved under D11). This approval does not define GSE140829's general eligibility or Tier P1 rules, which remain undefined (v7 §12). The meaning of "replicate 2", the identity of any partner arrays and the arrays' biological independence are not established; data-owner clarification (D9) is deferred. This approval does not approve D16 (S14 may not run until D16 is approved), D11, D19, D-1 handling, the review workflow/log, or any analysis | Unapproved D18 components: none of the proposed components (D-1 handling and the review workflow/log approved 2026-10-18); the R2-ID scope (cohort-wide vs per contrast) is unresolved. D-2 option (a) not chosen; option (b) not chosen as the primary rule (it enters only as the S14 sensitivity under option (c)) | A2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D9 |
| D19 | Approved resource | — | Enabling                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | D8, D6 |
| D20 † ‡ | **O1 + X1** (§4.3); W1; C-c one-sided with L_c; C-a q < 0.05; **covariates locked (§4.1)** | O2, O3; X2, X3; W2; "report only L_c" (v6:538); two-sided C-c (v6:539–540); a cross-cohort score standardization "justified and approved at Tier A (D20)" (v6:591; candidate "not proposed", v6:601) | A5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D12 |
| D21 | Not proposed | — | A5 (if S11)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | D8 |
| D22 † ‡ § | **PARTIALLY APPROVED — 2026-10-11 (explicit PI instruction): R8 variant V-A and §3.5 QC policy rows 1–6 only (v5:279–284).** (1) **V-A:** R8 gates wherever assessable; gated analyses and QC Stage A execution scope per v7:139; a permitted combination with approved D5 option (b) (v7:146). (2) **Row 1, R8 two-axis discordant (v5:279):** excluded from the primary analysis (Tier Q1); S5f re-includes them, subject to the precedence rule (§5.2, approved 2026-10-15 under D18, v7:621). (3) **Row 2, R8 single-axis discordant (v5:280):** retained in the primary analysis (Tier F2); S5d and S5g exclude them. (4) **Row 3, R8 ambiguous (v5:281):** retained in the primary analysis (Tier F3; Tier Q2 does not apply); S5e and S5g exclude them. (5) **Row 4, R8 unassessable (v5:282):** retained; the source documents define no sensitivity variation. (6) **Row 5, R9 flag (v5:283):** retained in the primary analysis under role (iii) (Tier F1); S5a, S5b and S5c exclude flagged arrays at k = 3, 2.5 and 4 respectively, and S5g uses k = 3; k = 3 is the D5 unvalidated operational convention (v7:608), and k = 2.5 and 4 are not approved. (7) **Row 6, R9 numerical failure (v5:284):** numerical-failure arrays are excluded from the primary analysis; the exclusions are rule-based and listed, Tier P3, never lifted and not varied in sensitivity analyses. The detailed R9 failure rules are approved as defined in the P3 entry (v7 §5.1, v7:351): the A1 matrix is computed over the cohort's arrays remaining after A0, with the documented A0 and A1 triggers; one fixed correlation matrix is used (A1/A3 outcomes never change other arrays' medians; finite r_ij of A1-failed arrays still contribute); m_i ≥ 1 − 10⁻⁸ (Option C) refers the array to D18 without computing z_i and retains it (not a numerical failure); this is a new D22 median-level threshold, distinct from the D5 pairwise tolerance; m_i ≤ −1 is a numerical failure (P3); failures from stages that ran are kept when R9 later becomes not applicable, no failure is inferred for stages that did not run, and "R9 actually ran" (v6:97) includes such a run; R9 runs separately within each cohort, subject to the V-A gate; A4's M and S use arrays with finite z_i; the exclusion rationale is that the R9 statistic cannot be computed validly. Rows 1–4 apply only where R8 is "completed — informative" under V-A; S5 analyses are defined but may not run until D16 is approved; this approval authorizes no analysis. **Further approved 2026-10-15 (explicit PI instruction): the exclusion-list approval scope (v5:123–129)** — the PI reviews and approves the complete rule-applied exclusion list for each cohort, across all tiers and rules, after QC Stage B and before the population is linked to any expression model; approval is limited to verifying that the prespecified rules were applied correctly; approval of individual QC policy rows does not constitute approval of the list; any deviation requires a documented protocol amendment (v5:127–128). This approves the policy only; no exclusion list exists or is approved. **Remain unapproved:** D16. Except as permitted by the QC Stage A ruling that follows, QC Stage A may not start until this remaining D22 item is approved and its other prerequisites are satisfied (v5:112–121; v7:108, 139). **QC Stage A ruling § — separate approval, 2026-10-18 (explicit PI instruction, option A):** for GSE63060, QC Stage A (R8, R9) may compute and record candidate exclusions before D16 is approved; no exclusion is applied until the exclusion-list approval step (v5:123–129) and D16 are decided, and Stage A outputs are not used downstream until then. This ruling approves no exclusion list, no sensitivity set, no other cohort and no analysis. **R8 review outcome § — separate approval, 2026-10-18 (explicit PI instruction): R0 + R3** (reports/phase3b/amendments/R8_GSE63060_AMENDMENT_REVIEW_2026-10-18.md, SHA-256 e8d843cf42368d277d5e9693b324da2d5a9a061497d4fc69c3f52d24f6b0f30f): R8 is not amended; its findings are recorded (weak XIST and non-informative DDX3Y, USP9Y and ZFY probes on GPL6947; 46 arrays where both strong Y markers disagree with recorded sex, 23 recorded F and 23 recorded M, corroborated by XIST in 45); a data-owner query on GSE63060 sample/label assignment (D9) is to be sent by the PI; sensitivity S-R8m is added under D16. The Q1 candidates remain unapplied until the exclusion-list approval step. Under V-A, GSE140829 (D19) and GSE99039 (GPL570 sex-probe identification) are not assessable until their dependencies are resolved (v7:158–163) | V-B, V-C not chosen; R8-ambiguous policy "alternatives: exclude, or retain only" (v5:281): not chosen ("retain only" is undefined in the source documents and is not defined here). (R9-role alternatives (i)/(ii) of v4 §2.3 are not active options: v4 §1–2 is superseded by v5 §3 (v5:77), which restates only role (iii) (v5:283)) | A3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | D5 |

---

## 12. Remaining open items

| Item | Status |
|---|---|
| D_min | **Unresolved** — no source |
| c₁–c₃ | Unset |
| D6 option | G3 primary, S8 = G1, freezing rule approved (2026-10-12; §11 D6); gene-history cutoff 20260318, gene-history procedure and GPL570 mapping (Option A) approved (2026-10-13); Illumina annotation policy for GSE63060 and GSE63061 approved 2026-10-17 (D6-G, Option A0; §11 D6); final A0 classification generated and verified 2026-10-17 (reports/annotation_audit/illumina_a0/v1, including cohort Series Matrix presence); annotation pin created 2026-10-18 (Tier B step 2; reports/annotation_audit/annotation_pin/v1); package installation pending (D8 approved for environment readiness only, 2026-10-18; v7:611); GSE140829 annotation unset (D19) |
| D20 O and X options; W1/W2 | Unset |
| δ and its scale | Unset |
| R8 variant | V-A approved 2026-10-11 (§11 D22) |
| Failure-rule alternative (D7) | Unset |
| S13 covariate and unit rule | Open |
| G1b for GSE99039; G2 for GPL570 | Unresolved |
| GSE140829 eligible-array universe and contrast-label (Tier P1) rules | Undefined — R1, R3, R4 and R11 are GSE63060 definitions (v7:605); required before any GSE140829 analysis (v7:103, rule 3) |
| External | D9/D10, D19, GPL570 and Illumina annotation package installation and pinning (mappings approved under D6-F and D6-G), software-behaviour checks; the raw NCBI gene_history.gz used for reports/annotation_audit/ncbi_gene_history/v1 (SHA-256 bcb85c8fdd4791ad674e69481b794677953d0ecd9efb8547af4371845c59a602, retrieved 2026-10-12T17:16:35Z) is not retained in the project, so its records cannot be rebuilt independently |
| Not established by any argument | Inferential validity under S-1 to S-5 (assumptions unverified); independence of expression-based QC selection |

## 13. Metadata-only checks for later

Unchanged from v6:858–871, plus: the sample-set log of §5.4 (Tier B, before any model).

## 14. Disposition of the [FA] issues

| [FA] issue | Status | v7 § |
|---|---|---|
| 1 Replication error-rate target | **Resolved in specification.** Each family's controlled and uncontrolled error rates are stated, overall control is prohibited from being claimed, and options are given. The target itself remains a D20 decision (unapproved) | 4.2–4.3 |
| 2 Validation covariates | **Resolved:** restated from the source, mapped per cohort and contrast, with missing-data and non-estimability rules, locked and placed in Tier A. The S13 covariate rule remains open with D11 | 4.1, 7, 1 |
| 3 G1 validity | **Resolved in specification:** the exceptions are classified (family B, sensitivity-only); consistency, independence and validity are separated. **Inferential validity itself remains conditional and unverified**; D6 partially approved (§11 D6) | 3 |
| 4 Re-inclusion precedence | **Resolved:** tiers, the precedence rule, sample-set formulas and the audit log | 5 |
| 5 R8 option consistency | **Resolved:** permitted combinations, explicit non-start when D5 is unset, the "completed — uninformative" status; choices unapproved | 2 |
| 6 v2 §7.5 | **Resolved:** retired, with requirements restated. The failure rule is replaced by a no-discretion default, and its alternative remains a D7 decision | 0.1, 6 |
| 7 Equivalence margin | **Resolved in specification:** the δ requirement is stated, what is reportable without δ is listed, and scale options are given. δ is unapproved and no value is proposed | 8 |
| Also handled: F7, F9, F14, F17, F20, F21 | Resolved in text | 4.4, 8.3, 2.3, 5.4, 4.5, 0.1 |
