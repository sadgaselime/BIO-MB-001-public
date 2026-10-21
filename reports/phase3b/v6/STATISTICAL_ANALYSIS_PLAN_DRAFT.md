# BIO-MB-001 — Statistical Analysis Plan, DRAFT v6 (Phase 3B, targeted correction of v5)

**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen.**

- No decision D0–D22 is approved.
- The approval-gate status is unchanged:
  - **Not satisfied:** G1, G2, G5, G7, G8.
  - **Partially satisfied:** G3, G4, G6, G9.

Preserved unchanged: v1–v5, `reports/phase3b/v4/SCIENTIFIC_CONSISTENCY_AUDIT.md` ([AUD]) and
`reports/phase3b/v5/SCIENTIFIC_DECISION_REGISTER.md` ([REG]).

v6 corrects the six contradictions T1–T6 and the minor items T7–T10 identified in [REG] Part 3.4, plus
the approval-order requirement.

Nothing was executed:

- no expression value was read;
- no QC statistic, metadata pass/fail check, model, gene list, pathway result or signature exists;
- no sample is identified, excluded or relabelled.

No new local evidence was gathered. v6 is specification and reasoning only.

Labels:

| Label | Meaning |
|---|---|
| **[EVIDENCE]** | Project file or report |
| **[REASONING]** | Statistical argument made here; not externally validated |
| **[BACKGROUND]** | General domain knowledge, not verified in the project |
| **[PROPOSED]** | Suggested default requiring PI approval |
| **[PROPOSED (no source)]** | Convention with no empirical or literature basis |
| **[DECISION NEEDED]** | Evidence does not determine an answer |
| **[UNRESOLVED]** | Cannot be resolved locally |
| **[DEPENDENCY]** | External information or software authorization |

Line references `v5:L` are to `reports/phase3b/v5/STATISTICAL_ANALYSIS_PLAN_DRAFT.md`.

---

## 0. Scope, supersession and change log

### 0.1 Active-text map

The active plan is **v6**, plus the v5 sections listed as retained below, plus the earlier texts that
v5 §0.2 (v5:69–82) keeps active.

| v5 text | Status in v6 |
|---|---|
| §0 (v5:50–82) change log and map | Superseded by this §0; the earlier-draft map in v5:71–82 is retained, with the T2 addition below |
| §1 inputs (v5:86–90); §2 foundations (v5:92–99) | **Retained unchanged** (restated briefly in §1) |
| §3.1 QC stages (v5:105–133) | **Retained** |
| §3.2 R8 algorithm (v5:135–235) | **Retained**, including D_min sequencing and options (a)/(b)/(c) |
| §3.2 final paragraph "Until the PI decides…" (v5:236–238) | **Superseded** by v6 §3 |
| §3.3 R9 (v5:240–266) | **Retained**. The A2 review referral (v5:250–251) now points to v6 §4 |
| §3.4 Stage B (v5:268–273); §3.5 QC policies (v5:275–290) | **Retained**. The R8 rows apply only when R8 has run (v6 §3) |
| §4.1 estimability vs adequacy (v5:296–312) | **Retained** |
| §4.2 threshold pre-registration (v5:314–337) | **Superseded** by v6 §5 (content kept; order made explicit) |
| §4.3 decision vs descriptive checks (v5:339–347); §4.4 procedure (v5:349–398) | **Retained** |
| §5.1, §5.2, §5.4 (v5:404–421, 461–477); §5.3 "Approval needed" list (v5:454–459) | **Superseded** by v6 §6 |
| §5.3 validity reasoning (v5:423–452) | **Retained**; extended by v6 §6.4 |
| §6 signature lock (v5:481–524) | **Superseded** by v6 §7 |
| §7 validation (v5:528–630) | **Superseded** by v6 §8 |
| §8 specificity (v5:634–695) | **Superseded** by v6 §9 |
| §9 pathways (v5:699–715) | **Retained** |
| §10 sensitivity (v5:719–752) | **Superseded** by v6 §10 |
| §11–§16 (v5:756–970) | **Superseded** by v6 §11–§16 |

**Earlier-draft text affected by T2.** The row "Specificity age-adjusted sensitivity" of v3 §3.4
(v3:167), which v5 kept active via v5:74 but omitted from v5 §10, is now **implemented as v6 S15**
(§10.2). The v3 §3.4 table remains active as the source of the missingness facts.

### 0.2 Change log from v5

| Item ([REG] Part 3.4) | v6 change | v6 § |
|---|---|---|
| T1 specificity sidedness | Separate non-directional (primary) and directional (optional) specificity questions, with their own estimand, null, sidedness, effect measure and multiplicity. The validation one-sided test is not reused | 9 |
| T2 age-adjusted GSE99039 sensitivity | Restored as S15, with a matched-subset reference fit (S15-ref) | 10.2 |
| T3 G1 selection scope | Selection once per cohort on a prespecified selection set; frozen across all models and contrasts in that cohort; explicit exceptions | 6.2–6.4 |
| T4 C-a claim | Null, direction, family, adjusted-p rule and claim wording defined (proposal for D20) | 8.6 |
| T5 C-c test vs CI | One-sided test aligned with a one-sided 95% lower bound for the decision; the two-sided CI is descriptive only | 8.5 |
| T6 R8 requirement | Per-analysis dependency table; three protocol variants for D22; none approved | 3 |
| T7 score comparability | Cross-cohort magnitude comparison prohibited unless a standardization is approved | 8.9 |
| T8 D4/D7 order | Explicit order: D4 → design → D7 values → checks | 5 |
| T9 redundant coverage rule | Overall-50% rule removed, with proof that meaning is unchanged | 8.4 |
| T10 duplicate review | Reproducible workflow specified | 4 |
| Approval order | All scientific rules approved before QC Stage A; execution-only items may follow | 2 |

---

## 1. Foundations (unchanged; restated for the trace)

| Element | Definition |
|---|---|
| Primary estimand | **E2**, unchanged (v5:96): GSE63060 deposited "AD" vs "CTL" difference, conditional on approved covariates, among eligible samples. Includes ~41 likely converters (H1) |
| Eligibility | R1–R13, R2-ID/R2-COV, R5 (v5:97). **Unchanged** |
| Primary population | Eligible population minus the §3.5 rule-based QC exclusions (v5:98), which apply only if R8/R9 actually ran (v6 §3), and minus the duplicate-review exclusions under the approved D18 policy (v6 §4) |
| Cohort roles | Unchanged (v5:99) |

The addition of the duplicate-review rule to the population definition is a **clarification** of the
existing R2-ID / D18 identity rule ([REG] T10). It is not a new eligibility criterion.

---

## 2. Order of approvals and checks (resolves the approval-order requirement)

**Principle [REASONING].** Discovery outputs are disease-association results. A rule chosen after they
are visible, even one that only governs validation or specificity, can be influenced by them. The
same applies to metadata pass/fail outputs. Therefore:

- **Every scientific rule, threshold and choice is approved in Tier A, before QC Stage A starts.**
- Only *enabling* items, such as installing software, executing a mapping or receiving owner
  information, may complete later. Those cannot introduce a new threshold.
- [REG] §3.2 ("can wait until …") is reinterpreted accordingly: it describes when items are
  **executed**, not when they are **approved**.

### 2.1 Tier A — approvals (recorded and checksummed in an approvals log before any computation below)

| Order | Decisions | Why this position |
|---|---|---|
| A1 | D0 (reconcile any other plan) | Governance precondition for approving anything |
| A2 | D1 estimand; D2 eligibility; D3 input; **D4 age eligibility and age covariate form**; D17 feature filters; D18 identity and duplicate policy (§4) | Defines the population and design columns |
| A3 | D5 QC constants (D_min, or option (a)/(b)/(c) of v5:221–234); D22 QC policies **and the R8-requirement variant** (§3) | QC must be fully specified before Stage A |
| A4 | **D7** c₁–c₃, scope and conventions (§5) | Applied to the design fixed in A2; values must not depend on any data |
| A5 | D6 gene-level option **and selection scope** (§6); D15 q-level, cap and coverage; D20 weighting, C-c, C-a and multiplicity rules (§8); D12 criteria; D13 specificity estimand, tests, multiplicity, coverage and **δ (or a decision that equivalence is not used)** (§9); D14 pathways; D11 GSE140829 input; D16 sensitivity set (§10); D21 (if S11 is retained) | All of these govern how discovery outputs are used. They must precede discovery results |
| A6 | D8 environment authorization (versions) | Enabling, but its versions are recorded before execution |

**δ rule:** if δ is not justified and approved at A5, the equivalence category stays **unavailable
for this study**. It cannot be added after discovery or specificity results exist.

### 2.2 Tier B — execution (each step only after the previous one; nothing in Tier A may be revised)

1. Install the pinned environment (D8).
2. Pin the annotation; probe → Entrez tables.
3. Eligibility.
4. Duplicate-review metadata candidates (§4).
5. QC Stage A, then Stage B (v5 §3).
6. Duplicate-review expression candidates (§4).
7. Primary population log.
8. Metadata checks M1–M8 (v5 §4.3–4.4).
9. Selection tables (§6).
10. Discovery fits.
11. Signature lock (§7).
12. Validation (§8; GSE140829 only after D19 has been executed).
13. Specificity (§9).
14. Pathways (v5 §9).
15. Sensitivity analyses (§10).

**Amendments.** Any change to a Tier A item after Tier B has started requires a documented protocol
amendment. That amendment states which pass/fail or association outputs were already visible, and
analyses run after the amendment are reported as **post hoc**.

---

## 3. R8 requirement by analysis (resolves T6; supersedes v5:236–238)

**Facts [EVIDENCE: v5].**

- R8 cannot start until D_min is approved, or option (b) or (c) is chosen (v5:217–234).
- For GSE140829, R8 also needs D19 (v5:146).
- For GSE99039, R8 needs the GPL570 sex probes to be identified (v5:147).

**Computational dependency [REASONING].** No primary, validation or specificity model takes R8 output
as an input. R8 only changes the population, through two-axis discordant exclusions (v5:279). Only
the R8 components of S5 (S5d, S5e, S5f, and the R8 part of S5g) *use* R8 flags. Whether the main
analyses *require* R8 is therefore a protocol choice, not a technical necessity.

**R8 status vocabulary (always reported per cohort):**

| Status | Meaning |
|---|---|
| **completed** | Stage A ran |
| **not applicable** | A0 rule: probes absent or fewer than 2 Y genes |
| **not performed** | Threshold or option not approved, or the protocol variant does not require it |
| **blocked** | Mapping or annotation dependency |

R8 is never reported as completed unless Stage A ran. No threshold is assumed.

### 3.1 Protocol variants for D22 [DECISION NEEDED; none approved]

| Analysis | V-A: R8 required wherever assessable | V-B: R8 not required (deposited-label estimand) | V-C: R8 required for discovery only |
|---|---|---|---|
| Discovery primary (GSE63060) | Waits for R8 completed (or not applicable) | Proceeds; R8 "not performed" | Waits |
| Validation: GSE63061 consistency | Waits | Proceeds | Proceeds |
| Validation: GSE140829 replication | Waits (also blocked by D19) | Proceeds once D19 is executed | Proceeds once D19 is executed |
| Specificity (GSE99039) | Waits for GPL570 sex-probe identification and D_min | Proceeds | Proceeds |
| S5d, S5e, S5f, R8 part of S5g | Run only where R8 completed | Not run | Run in GSE63060 only |
| Other sensitivities | Follow their parent analysis | Follow their parent analysis | Follow their parent analysis |

**Consequences [REASONING]:**

- **V-A** maximizes sample-integrity checking, but blocks every analysis until D5 is resolved, and
  blocks specificity until GPL570 annotation is available.
- **V-B** keeps E2 computable everywhere, but leaves recorded sex (a model covariate) and the
  sample–metadata correspondence unverified. For GSE63060, the only sex QC is then the submitters'
  pre-deposit XIST check, which cannot be audited (v5:230–233). For other cohorts none is documented.
- **V-C** protects the confirmatory discovery estimate and accepts the V-B limitation for the
  downstream cohorts.

Under every variant:

- the R8 status is reported in each cohort's results;
- results produced without R8 carry the limitation "sex consistency not verified";
- the variant is chosen at Tier A3 (§2.1).

---

## 4. Duplicate-array review workflow (resolves T10; D18)

**Scope.** Within-cohort only. Cross-series participant overlap (H9) is outside this workflow,
because platforms differ and identity cannot be established from expression across them.

**Candidate sources (fixed before any review):**

- **C1, metadata** (Tier B step 4):
  - identical GSM, array barcode or participant identifier within a cohort (R2-ID);
  - deposited replicate annotations (e.g. GSE140829 "replicate 2"; v3 §3.3).
- **C2, expression** (Tier B step 6): pairs with r ≥ 1 − 10⁻⁸ from R9 A2 (v5:250;
  [PROPOSED (no source)]), computed diagnosis-blind in R9 Stage A. Pairs are grouped into connected
  clusters when an array appears in more than one pair.

**Allowed evidence:**

- GEO accession, title and barcode (chip, position);
- participant-identifier fields;
- deposited description and replicate fields;
- GEO processing fields;
- the pair's r value.

**Not allowed:**

- diagnosis;
- age, sex, site or any other phenotype value. Identity is never inferred from these (standing
  project rule; v3 §3.3);
- any association result.

The reviewer receives a review table that **omits diagnosis and phenotype columns**.

### 4.1 Categories and proposed handling [PROPOSED; D18]

| Category | Definition | Proposed handling |
|---|---|---|
| D-1 metadata-confirmed | Arrays linked by the same participant identifier, or by an explicit replicate link naming the partner | Keep one array per participant: the array not labelled as a replicate; otherwise the lowest GSM accession number. Exclude the other(s) from contrasts; list them |
| D-2 replicate without identifiable partner | A replicate annotation exists but no partner can be identified (the GSE140829 case) | D18 options (a), (b) or (c) of v3 §3.3 (proposed: a) |
| D-3 expression-only | C2 pair or cluster; metadata silent | Keep the lowest GSM accession in the cluster in the primary analysis; exclude the others; **S16** re-includes them |
| D-4 conflicting | C2 pair whose metadata name *different* participants | "Identity uncertain". Same handling as D-3, labelled uncertain; S16 re-includes them |

- **Deterministic tie rule:** lowest GSM accession number. This is arbitrary but outcome-independent.
- **Alternative (D18):** retain all D-3 and D-4 arrays in the primary analysis and exclude them in S16
  (reverse roles).

### 4.2 Recording

A checksummed **duplicate-review log** contains, per pair or cluster:

- cohort and array identifiers;
- candidate source (C1/C2) and r value;
- the metadata fields examined and their values;
- the category and the action taken;
- the rule reference;
- the reviewer and date.

The log is completed before the M-checks (Tier B step 8). Decisions are rule applications. A
deviation requires an amendment (§2.2).

**Uncertainty.**

- D-3 and D-4 arrays are reported as "identity uncertain".
- The 1 − 10⁻⁸ tolerance is a convention. Looser tolerances would need evidence that is not available
  [UNRESOLVED]. Near-duplicates below the tolerance (e.g. re-hybridized RNA) are therefore **not
  detected** by C2.

No actual sample is identified, examined or excluded in this draft.

---

## 5. Identifiability thresholds and the D4 → D7 order (resolves T8; supersedes v5 §4.2)

**Logical order [REASONING].**

1. **D4 (A2)** fixes age eligibility and the age covariate form. Together with D2, D18 and D22 this
   defines the population and the columns of N (v5:351–358).
2. **D7 (A4)** then fixes the following, which do not depend on any data:
   - c₁ (minimum number of mixed units);
   - c₂ (minimum number of each compared group on mixed units);
   - c₃ (maximum VIF_g = 1/E);
   - their scope (common vs cohort-specific);
   - η = 10⁻⁸ [PROPOSED (no source)];
   - the scaling convention (continuous columns standardized; indicators 0/1);
   - τ = max(n, p)·σ_max·ε on the scaled N.
3. The **M-checks** run once, after QC and duplicate review (Tier B step 8), on the approved
   population, using the v5 §4.4 procedure. No D7 value is revised afterwards (v5:394–395).

So **D7 depends on D4** (and on D2, D18, D22). **D4 does not depend on D7.** This corrects the v5
register entry "D4 depends on D7" (v5:845).

**Options still open within D7** (from [REG] D7):

- c₂ redefined as a within-unit minority count, Σ_u min(n_AD,u, n_CTL,u);
- a minimum residual df as a decision check.

Both remain PI options. **No value is proposed here.**

**Prior exposure:** as in v5:331–337. No diagnosis × chip table was found in earlier reports, but this
rests on a text search only.

---

## 6. Gene-level unit with frozen selection (resolves T3; supersedes v5 §5.1, §5.2, §5.4 and v5:454–459)

### 6.1 Terms

- **Eligible probe** (unchanged; v5:408): one-to-one Entrez mapping under the pinned annotation;
  passes the approved feature rule. Multi-mapped and unmapped probes are never used in gene-level
  units.
- **Selection set S_c:** the prespecified samples whose values define the gene-level unit in cohort c
  (§6.2).
- **Selection table T_c:** per Entrez gene, the selected probe (G1, G1b, G2) or the constituent probe
  list (G3) for cohort c. Created once, checksummed, then **frozen**.
- **Gene-level matrix U:** rows = Entrez genes in T_c; columns = the samples of the model being
  fitted; u_g(i) is computed from T_c.

### 6.2 D6 options with selection sets [DECISION NEEDED; none approved]

| Option | Unit | Selection set S_c and statistic | Defined for |
|---|---|---|---|
| **G1** | Eligible probe with the highest **unweighted mean over S_c**; ties → probe ID ascending | **GSE63060:** the primary population (AD + CTL after eligibility, §3.5 exclusions actually applied, and §4). **GSE63061, GSE140829:** the cohort's primary score samples (AD + CTL after the same rules). **GSE99039:** the union of all prespecified specificity contrast samples (IPD, CONTROL, GPD, GENETIC_UNAFFECTED after the same rules) | All cohorts |
| **G1b** | Highest unweighted mean over the cohort's MCI arrays (after the same rules); ties as G1 | GSE63060, GSE63061, GSE140829 MCI sets (v5:419) | Illumina cohorts. **GSE99039 undefined** [UNRESOLVED] |
| **G2** | Annotation-only rule fixed before data | None | **Requires** a resource and a GPL570 rule [DEPENDENCY: D8] |
| **G3** | Mean of the cohort's eligible probes for g; T_c lists them | None (the list is defined by annotation and the feature rule) | All cohorts |

**Permitted information for building T_c:**

- the expression values of eligible probes for the samples in S_c;
- **set membership only.** Diagnosis labels may be used only to *define* membership of S_c (e.g.
  "AD or CTL"). They are never used to compute group-specific statistics.

**Not permitted:** covariates, per-group means, any model output, any association result.

**R2-COV** (covariate completeness) does **not** restrict S_c. Selection uses expression only.
Covariate completeness applies to each model separately (v3 §3.1).

**Timing:** T_c is built after the cohort's primary population (or score samples) is fixed, and
**before any expression model is fitted in that cohort** (Tier B step 9).

### 6.3 Freezing rule [PROPOSED; D6]

T_c is used **unchanged** for every model in cohort c:

- the primary model;
- C-a, C-b and C-c;
- every specificity contrast;
- S15;
- every sensitivity analysis.

The exceptions are fixed in advance:

| Analysis | Rule |
|---|---|
| S7 (additional feature filter) | G1/G1b/G2: if the frozen selected probe fails the filter, the gene is "not measured under S7". **No reselection.** G3: the average is taken over the surviving constituent probes, and genes with none surviving are "not measured under S7" |
| S8 (alternative D6 option) | Builds its own T_c by the alternative option, with the same sets and freezing |
| S9 (2008 BGX annotation) | Keeps the frozen probe identities. Genes whose frozen probe maps to a different Entrez ID under BGX are reported as "annotation-discordant", not re-mapped |
| S10 (re-normalization) | Same probe identities; new values |
| S13 (GSE140829 final processed file) | Its feature identifiers differ from the Series Matrix ([v2 §9.6]). The unit rule for S13 must be specified together with D11 [TS; open] |
| S14, S16 (re-inclusion of excluded arrays) | T_c unchanged. The re-included arrays are not in S_c (see §6.4) |

**Alternatives requiring D6 approval if preferred (not proposed):**

1. Re-select per model. Units would change across analyses, which is the T3 problem.
2. Re-select per GSE99039 contrast.
3. For GSE99039, S_c = IPD ∪ CONTROL only, applied to all contrasts.

### 6.4 Validity of frozen G1 selection [REASONING; extends v5:423–452]

Under the v5 §5.3 setting (Gaussian errors; sample rows independent with a common across-probe error
covariance), take any model fitted to a sample subset M ⊆ S_c that includes an intercept.

- Its group-contrast vector and residual space are supported on M and orthogonal to 1_M.
- They are therefore orthogonal to 1_{S_c}, which equals 1_M on M.
- Samples in S_c \ M are independent of M.

So the S_c means, and hence the selection, are independent of that model's test statistics. This
covers:

- the primary model;
- sensitivity subsets (S1, S5, S12, S15);
- each GSE99039 contrast, since each contrast ⊆ the union S_c.

**Exception:** where a model includes arrays **outside** S_c (S14, S16 re-inclusions), exact
independence is not guaranteed. The dependence involves only the re-included arrays and is
unquantified; it is reported as a limitation.

The caveats in v5:438–440 (unequal variances; non-Gaussian errors; the mean-dependent limma-trend
prior) still apply.

### 6.5 Discovery pipeline (replaces v5:461–477; otherwise unchanged)

1. Probe-level fit on all probes passing the feature rule. BH across all tested probes: the
   **probe-level family**.
2. Build T_GSE63060 (§6.2), then U.
3. Gene-level fit on U (same design and settings). Per gene: β_g, SE, 95% CI, moderated t, p. BH
   across the rows of U: the **gene-level family**.
4. Direction d_g = sign(β_g).
5. The two families are reported separately.
6. Probe-discordant genes are flagged (v5:476–477).

### 6.6 Approval needed (D6)

1. The option.
2. The selection sets in §6.2 (or one of the listed alternatives).
3. The freezing rule and exceptions in §6.3.
4. For G1b: a solution for GSE99039.
5. For G2: a resource and a GPL570 rule.
6. The S8 alternative.

The evidence does not select an option (v5:446–452).

---

## 7. Signature lock (supersedes v5 §6)

### 7.1 Selection [PROPOSED; D15] (unchanged from v5:483–502)

- **Eligibility:** gene-level q < 0.05.
- **Ranking:**
  1. q ascending;
  2. then |β_g| descending;
  3. then |moderated t| descending;
  4. then Entrez ID ascending.
- **Cap:** 200 unique Entrez genes.
- **Coverage restriction at selection:** none (alternative: D15).

**Special cases:**

| Case | Response |
|---|---|
| No eligible genes | No signature. Validation and signature-based specificity are not run; the threshold is not relaxed |
| One-directional | Locked as such |
| Fewer than 10 genes | Labelled "low gene count" ([PROPOSED (no source)]) |

### 7.2 Lock contents (written before any validation or specificity expression is modelled against diagnosis; checksummed)

1. The D6 option, the selection-set definitions and freezing rule (§6), and the checksum of
   T_GSE63060.
2. The annotation resource and release; the mapping rule; the validation feature rule (§8.2).
3. Per gene:
   - Entrez ID and symbol;
   - the discovery selected probe or constituent list;
   - β_g with 95% CI, moderated t, q;
   - direction d_g and rank.
4. Counts: eligible, up and down genes.
5. **Validation scoring and test specification:**
   - the weighting convention;
   - the standardization;
   - the coverage rule (§8.4);
   - the C-c estimand, test, bound and α (§8.5);
   - the C-a rule (§8.6);
   - the C-b descriptive specification (§8.7);
   - the multiplicity rule (§8.8).
6. **Specificity test specification:**
   - the estimands, tests, sidedness and multiplicity (§9.4–9.5);
   - the coverage rule application (§9.6);
   - δ, or "equivalence not used".

The same lock (same checksum) governs every validation and specificity cohort. **No cohort receives a
different gene list, weighting, coverage rule, mapping rule or test specification.** Each cohort's own
T_c is produced later, by the locked rule (§6), and is reported.

---

## 8. Validation: replication (GSE140829) and consistency (GSE63061) (supersedes v5 §7)

### 8.1 Roles (unchanged)

- GSE140829: replication, independence unverified.
- GSE63061: related-cohort consistency.
- Results are reported separately. Nothing is tuned on them.

### 8.2 Mapping, feature and probe rules (unchanged from v5:536–545, except unit construction)

| Rule | Specification |
|---|---|
| Cross-platform mapping | One pinned annotation release with a shared Entrez snapshot. Entrez-only match. Retired or merged IDs become "unmapped" unless an ID-history procedure is approved [DEPENDENCY: D6, D8] |
| Multi-mapped probes | Excluded in every cohort |
| Validation feature filter | **None** [PROPOSED; D17] |
| Presence | Only IDs present in the cohort's own Series Matrix count. GSE140829 requires D19 |
| Gene-level unit | By the locked D6 rule and the frozen T_c (§6) |
| Reporting | T_c is reported per cohort |

### 8.3 Measurability categories (unchanged; v5:547–556)

1. Unmapped.
2. No eligible probe in the Series Matrix.
3. Constant in cohort.
4. Measurable.

Categories 1–3 are "not measurable", never "not replicated". GSE140829 is entirely unmapped until D19
is resolved.

### 8.4 Score and coverage (W1/W2 unchanged; coverage rule simplified)

- **Score samples:** eligible AD + CTL after QC, §4 and R2-COV (and D18 for GSE140829).
- **Standardization:** z_gi = (u_g(i) − mean_g) / sd_g over all score samples (n − 1 denominator),
  diagnosis-blind.
- **Weighting [DECISION NEEDED; D20]:**
  - **W1 (proposed):** S = mean_{U_c} z − mean_{D_c} z. Up-only: mean_{U_c} z. Down-only:
    −mean_{D_c} z. Equal weight within a direction; each direction has total weight 1.
  - **W2:** S = (Σ_{U_c} z − Σ_{D_c} z) / (|U_c| + |D_c|). One-directional forms are identical to W1.

**Coverage rule [PROPOSED (no source); D15]:** for each direction that is non-empty at lock, at least
50% of that direction's locked genes **and** at least min(5, locked in that direction) must be
measurable. Otherwise the score is **not assessable** in that cohort, and it is never converted to a
one-directional score.

**Why the v5 overall-50% rule is removed without changing meaning [REASONING]:**

- If every non-empty direction has |X_c| ≥ 0.5|X|, then summing over directions gives
  Σ|X_c| ≥ 0.5 Σ|X|.
- So the v5 overall rule (v5:592) was implied by the per-direction rule (v5:593–594), and dropping it
  changes nothing.
- The v5 statement that a direction with zero measurable genes makes the score not assessable
  (v5:596–598) is likewise a consequence: 0 < min(5, n) whenever n ≥ 1.

### 8.5 Composite score test C-c (primary) — estimand, test and interval aligned (resolves T5)

| Element | Specification [PROPOSED; D20] |
|---|---|
| Estimand | θ_c = the adjusted mean difference in S between AD and CTL in cohort c (AD − CTL), conditional on the cohort's approved covariates, in **score units** (cohort-specific z-scale) |
| Question | Directional replication: is the locked signature shifted in the AD direction in cohort c? |
| Hypotheses | H0: θ_c ≤ 0; H1: θ_c > 0 |
| Test | One-sided, α = 0.05 per cohort (§8.8) |
| Decision interval | **One-sided 95% lower confidence bound L_c.** For the same t-based model, p < 0.05 ⇔ L_c > 0, so the test and the bound cannot disagree |
| Descriptive interval | Two-sided 95% CI for θ_c, reported as a within-cohort description of magnitude. **It answers a different question** (the plausible range in either direction) and is **not used for the replication decision**. If p < 0.05 while the two-sided CI includes 0, the decision follows the one-sided test and bound |
| Interpretation | "Directional replication of the composite signature in cohort c" (or "consistency" for GSE63061) |

**Alternatives (D20):**

- report only L_c;
- or, if the PI prefers a non-directional replication question, a two-sided test with the two-sided
  CI. This changes the estimand and must be approved before lock.

The sidedness is fixed in the lock and is not chosen after validation results.

### 8.6 Per-gene replication C-a (secondary) — claim definition (resolves T4) [PROPOSED; D20/D12]

| Element | Specification |
|---|---|
| Null hypothesis (gene g, cohort c) | H0_g,c: d_g·β_g,c ≤ 0, where d_g is the locked direction and β_g,c the gene-level AD − CTL effect in cohort c (same covariates) |
| Alternative | d_g·β_g,c > 0 |
| Test | One-sided p-value from the cohort's gene-level fit (moderated t) |
| Multiplicity family | The measurable locked genes **in cohort c** (each cohort a separate family) |
| Adjusted-p rule | BH-adjusted q_g,c |
| Replication claim | Gene g "statistically replicated in GSE140829" (or "consistent in GSE63061") iff **q_g,c < 0.05** |
| Direction evidence | Built into the one-sided null: q < 0.05 requires the estimate to lie in the locked direction. Report β̂_g,c with its one-sided 95% bound in the locked direction |
| Gatekeeping | **None proposed.** C-a is reported whatever the C-c result, labelled secondary. Alternative: fixed-sequence gatekeeping (C-a claims only if C-c is significant in that cohort) |
| Dependence caveat [REASONING] | BH validity assumes positive dependence (PRDS). This is plausible for co-expressed genes but not verified |
| Descriptive summary | Proportion replicated with a binomial CI, labelled descriptive |

**Claim boundaries [REASONING]:**

- "Statistically replicated" means only that the locked direction of association between deposited
  diagnosis labels and expression is reproduced in another deposited dataset.
- It is **not**:
  - **biological validation:** mechanism, cell-type origin or causality;
  - **clinical validation:** diagnostic accuracy, calibration, prospective or independent-population
    performance.
- For GSE140829, independence is unverified (D10). For GSE63061, the word "replicated" is not used.

### 8.7 Direction concordance C-b (descriptive only; unchanged from v5:615–620)

- Report T, the concordant and discordant counts by direction, and the coverage status.
- No p-value.
- Inferential only if D12 approves a justified procedure.

### 8.8 Hierarchy and multiplicity

- **Per cohort:** C-c primary (one-sided α = 0.05); C-a secondary (BH q < 0.05); C-b descriptive.
- **Across cohorts [PROPOSED; D20]:** separate α per cohort, because they answer different questions;
  no pooled claim. Alternative: Holm across the two C-c tests. In that case the decisions use the
  Holm-adjusted p, and the bounds are reported unadjusted and labelled as such.

### 8.9 Score magnitude comparability (resolves T7)

**Not comparable [REASONING].** θ̂_c depends on:

- the number of measurable genes in each direction;
- the inter-gene correlation;
- the cohort's diagnosis mix, which enters sd_g;
- platform and processing.

**Prohibited**, unless a standardization is justified and approved at Tier A (D20):

- statements that θ is larger or smaller in one cohort than another (validation vs validation,
  validation vs discovery, or vs GSE99039);
- pooling;
- meta-analysis of θ̂ across cohorts.

**Allowed:** each cohort's own test, bound and interval, shown side by side with the label
"magnitudes not comparable across cohorts".

A candidate standardization (θ̂_c divided by the pooled within-group SD of S_c) is **not proposed**.
It remains affected by coverage and correlation.

---

## 9. Disease specificity — GSE99039 (resolves T1; supersedes v5 §8)

### 9.1 Gene set (unchanged proposal; D13)

- All locked genes (one fixed object).
- A replicated-genes-only analysis may be added only as a separately prespecified, labelled
  analysis.

### 9.2 Contrasts and roles [PROPOSED; D13]

| Contrast | Role |
|---|---|
| IPD vs CONTROL | **Primary** specificity contrast |
| GPD vs CONTROL | Secondary |
| GENETIC_UNAFFECTED vs CONTROL | Secondary, descriptive. The scientific meaning of the deposited label is not verified in the project, so its interpretation is left to D13 |
| OTHER_NEURO labels | Descriptive only |

### 9.3 Why the validation test is not reused [REASONING]

- The validation C-c (§8.5) asks a **directional** question (shift in the AD direction).
- The specificity question, whether the AD signature is associated with PD, is **non-directional**: a
  PD association in either direction is relevant.
- A one-sided test in the AD direction cannot detect an opposite-direction association. So it is
  **not** used in GSE99039, and the lock carries a separate specificity specification (§7.2 item 6).

### 9.4 Estimands and tests [PROPOSED; D13]

| Question | Estimand | Null / alternative | Sidedness and α | Effect measure and interval |
|---|---|---|---|---|
| **Q1 (primary, non-directional):** is the signature score associated with PD? | θ_PD,k = adjusted mean difference in S (locked weighting) between the disease group and CONTROL in contrast k, conditional on sex + batch, complete cases | H0: θ_PD,k = 0; H1: θ_PD,k ≠ 0 | Two-sided, α = 0.05 (primary: k = IPD) | θ̂ in score units, with a two-sided 95% CI. The sign of a significant estimate is reported as "same direction as the AD signature" (θ > 0) or "opposite" (θ < 0). A directional conclusion from the sign of a two-sided test keeps the directional error rate at most α/2 [REASONING] |
| **Q2 (optional, directional; not proposed by default):** is PD associated with a shift in the AD direction? | Same θ_PD,k | H0: θ ≤ 0; H1: θ > 0 | One-sided α = 0.05, only if approved. If both Q1 and Q2 are approved, Holm across Q1 and Q2 | One-sided 95% lower bound |
| **Per gene:** is gene g associated with PD? | β_g,PD,k = adjusted IPD − CONTROL (or disease − CONTROL) difference in u_g | H0: β = 0; H1: β ≠ 0 | Two-sided, BH across the measurable locked genes **within contrast k** | β̂ with a two-sided 95% CI (unadjusted, labelled). Category by q < 0.05 and sign relative to d_g |

- Score samples are the contrast's eligible samples (complete for sex and batch).
- z is computed over each contrast's score samples, diagnosis-blind.
- Units come from the frozen T_GSE99039 (§6).

### 9.5 Multiplicity across contrasts [PROPOSED; D13]

- Q1 for IPD vs CONTROL is the single primary specificity test.
- Q1 for GPD and GU is secondary, unadjusted and labelled.
- Alternative: Holm across the three Q1 tests.
- Per-gene families are separate per contrast.

### 9.6 Coverage

- The §8.4 coverage rule applies to each contrast [PROPOSED].
- Whether the same thresholds suit GPL570 is part of D13 [DECISION NEEDED].
- Failure means "not assessable".

### 9.7 Evidence categories (per gene and for Q1)

| Category | Rule |
|---|---|
| Association with PD — same direction as AD | q < 0.05 (gene) or p < 0.05 (Q1), estimate sign matching d_g (gene) or θ > 0 (Q1) |
| Association with PD — opposite direction | As above, with the opposite sign |
| **Association not demonstrated** | Otherwise |
| Compatible with no meaningful association | TOST with margin δ. **Unavailable unless δ is justified and approved at Tier A5** (§2.1). No value is proposed |

### 9.8 What cannot be concluded (unchanged in substance from v5:679–695)

- **A non-significant PD result is "association not demonstrated", never "absent" and never "specific
  to AD".**
- AD specificity is never inferred from a significant AD result together with a non-significant PD
  result.
- No AD × PD contrast is estimable.
- Effect magnitudes are not comparable across platforms or cohorts (§8.9; v5:687–693).
- Specificity results never alter the lock or any replication result.

**Covariates and missingness:**

- sex + batch, complete case (v3 §3.4: −35 for IPD vs CONTROL);
- age-adjusted analysis as S15 (§10.2);
- R8 per §3.

---

## 10. Sensitivity analyses (supersedes v5 §10)

### 10.1 General rules

- All are prespecified, all are reported, and none replaces the primary analysis.
- Each passes v5 §4.4 (including c₁–c₃); failure → "not estimable / insufficient".
- Discovery sensitivities never lock a new signature.
- All use the frozen T_c (§6.3), apart from its listed exceptions.
- R8-dependent variants run only where R8 has the status "completed" (§3).

| # | Definition |
|---|---|
| S1 | Age restriction: (a) ≥ 65; (b) 61–88 (GSE63060, GSE63061, GSE140829). Not GSE99039 |
| S2 | Age as a 3-df spline |
| S3 | Site added, or site instead of chip (if estimable) |
| S4 | Exclude the 37 "M"-coded AD samples (convention-dependent; not E1) |
| S5a–S5c | Exclude R9-flagged arrays at k = 3, 2.5 and 4 |
| S5d | Exclude R8 single-axis discordant arrays (only if R8 completed) |
| S5e | Exclude R8 ambiguous arrays, or include them if the primary excludes them (only if R8 completed) |
| S5f | Re-include R8 two-axis discordant arrays (only if R8 completed) |
| S5g | Combination: R9 (k = 3), plus single-axis discordant and ambiguous arrays (the R8 parts only if R8 completed) |
| S6 | Estimated array weights (basis invariance unverified; v5:379–380) |
| S7 | Additional mean-expression filter at the 25th and 50th percentiles (discovery; §6.3 exception) |
| S8 | Alternative D6 option |
| S9 | 2008 BGX annotation (§6.3 exception) |
| S10 | Re-normalization from the non-normalized file (only if approved) |
| S11 | Cell composition (D21) |
| S12 | Sood flagged subset (49 vs 67) |
| S13 | GSE140829 final processed file (unit rule open with D11) |
| S14 | GSE140829 including "replicate 2" arrays (D18 option c) |
| **S15** | **GSE99039 age-adjusted specificity (restored; §10.2)** |
| **S16** | **Re-include duplicate-review D-3 and D-4 arrays (§4)** |

### 10.2 S15 — age-adjusted GSE99039 specificity (restored from v3 §3.4, v3:167; resolves T2)

| Element | Specification [PROPOSED; D13/D16] |
|---|---|
| Purpose | The primary specificity models are **not** age-adjusted, because age at exam is missing for 199 of 438 IPD/CONTROL samples (v3 §3.2). S15 assesses whether the Q1 and per-gene PD results are sensitive to adjustment for age, which may confound PD–expression associations |
| Contrasts | S15a: IPD vs CONTROL. S15b: GPD vs CONTROL (GPD age missing 21/41; v3 §3.2). **GENETIC_UNAFFECTED vs CONTROL is not possible** (age missing for all 22; v3:169) |
| Eligible samples | The contrast's eligible samples with **non-missing age at exam and non-missing sex** (complete case). At most 239 for IPD/CONTROL (v3:167). The exact count is a metadata-only item (§15) |
| Age missingness handling | Complete case. **No imputation.** Multiple imputation is a possible alternative, but would require approval and a missingness model. The losses by group are reported, together with a **descriptive comparison of age-present vs age-missing samples on sex, batch and group** (metadata only; no tests) |
| Model | The primary specificity model (sex + batch) **plus age** (linear, standardized), fitted to the S15 subset. The same Q1 test (two-sided), per-gene tests, frozen T_GSE99039 and locked score |
| Reference fit S15-ref | The **primary model without age, fitted to the same S15 subset**. This separates the effect of adjusting for age (S15 vs S15-ref) from the effect of restricting the sample (S15-ref vs primary) |
| Reporting | θ̂ and per-gene results for the primary fit, S15-ref and S15, side by side. Labelled sensitivity. No new evidence category. Never replaces the primary analysis |
| Identifiability | v5 §4.4 applies to each S15 design |

### 10.3 S16 — duplicate-review re-inclusion

- Re-include the D-3 and D-4 arrays excluded in §4.1, for each affected cohort.
- T_c is unchanged (§6.4 exception).

---

## 11. Execution order and STOP cascade (supersedes v5 §11)

Approvals: §2.1 (Tier A). Execution: §2.2 (Tier B).

**STOP cascade (unchanged in substance from v5:772–777, with R8 statuses added):**

- **Discovery STOP** (estimability or minimum information) → no discovery results, signature,
  validation, specificity or pathways. The limitation is reported.
- **No eligible genes** → no lock. No validation or signature-based specificity. Exploratory
  pathways on the gene-level fit may still run.
- **A validation or specificity STOP, or a coverage failure** → "not assessable" for that cohort or
  contrast only.
- **Under V-A** (§3), a cohort whose R8 status is "not performed" or "blocked" does not proceed. Its
  status is reported as "blocked by R8".

---

## 12. Final consistency check

### 12.1 Confirmations requested

| Requirement | Result | Where |
|---|---|---|
| No obsolete v3/v4/v5 wording remains active where it conflicts with v6 | v5 sections touched by T1–T10 are superseded by section or line range (§0.1). Earlier superseded wording remains as listed in v5:798–822. **New in v6:** v5:236–238, v5:314–337, v5:404–421, v5:454–477, v5:481–695 and v5:719–970 are superseded, including v5:845 (register row D4). v5 §9 pathways (v5:699–715) is retained | §0.1, §12.2 |
| D0–D22 keep their IDs; none approved | Yes | §13 |
| Primary estimand and eligibility unchanged | E2 unchanged. Eligibility unchanged. The duplicate-review workflow clarifies the existing R2-ID / D18 identity rule ([REG] T10) | §1, §4 |
| Locked signature and scoring fixed across cohorts | Yes: one lock, including the validation and specificity test specifications; T_c is built by a locked rule | §7.2 |
| Specificity does not equate non-significance with absence | Yes | §9.7–9.8 |
| No new confirmatory test or threshold silently approved | All new rules are labelled [PROPOSED] or [DECISION NEEDED] under existing IDs (D6, D12, D13, D15, D16, D18, D20, D22). None is approved | §3, §6, §8, §9, §10 |

### 12.2 Wording superseded in v6

| Superseded | Replaced by |
|---|---|
| v5:236–238, "Until the PI decides…" (primary analysis only) | §3 (all analyses) |
| v5:410, 418: G1 "over the samples of the model being fitted" | §6.2 selection sets; §6.3 freezing |
| v5:543: "G1 uses the cohort's score samples" | §6.2 (GSE99039 union; frozen) |
| v5:520: lock "one-sided test direction" applied to all cohorts | §7.2 items 5–6 (separate validation and specificity specifications) |
| v5:585–586: one-sided p with two-sided CI as the replication statement | §8.5 |
| v5:592: overall-50% coverage rule | §8.4 (removed; implied) |
| v5:610–614: C-a without a claim threshold | §8.6 |
| v5:664–669: "same locked formula" for specificity (sidedness implicit) | §9.3–9.4 |
| v5:675: "CI excludes 0 and q < 0.05" | §9.7 (q-based; sign relative to the AD direction reported) |
| v5:729–752: sensitivity list without the GSE99039 age-adjusted analysis | §10 (S15, S16 added) |
| v5:845: "D4 depends on D7" | §5; §13 D4 / D7 rows |
| [REG] §3.2: approval timing "can wait" | §2 (execution may wait; approval may not) |

---

## 13. Decision register (D0–D22; none approved)

† = changed in v6.

| ID | Question | Proposed default (v6) | Open options | Approval tier (§2.1) | Depends on |
|---|---|---|---|---|---|
| D0 | Reconcile any other plan | Provide the content | — | A1 | — |
| D1 | Estimand | E2 with caveat | E1 via D9 | A2 | D9 |
| D2 | Eligibility | As v5 | — | A2 | D1, D18 |
| D3 | GSE63060 input | Series Matrix | S10 | A2 | — |
| D4 † | Age eligibility and covariate form | No restriction; linear age; S1 | ≥ 65 primary; spline | A2 | **None** (D9 optional) |
| D5 | QC constants; D_min | v5 constants; D_min unset; (a)/(b)/(c) | — | A3 | D22 |
| D6 † | Gene-level unit | None declared; selection sets and freezing per §6 | G1/G1b/G2/G3; listed selection alternatives | A5 | D8 |
| D7 † | Identifiability thresholds | Procedure as v5 §4.4; η; scaling; τ. **c₁–c₃, scope unset** | c₂ minority count; residual-df check | A4 | **D4**, D2, D18, D22 |
| D8 | Environment | Pinned R/Bioconductor | Validated alternative | A6 | — |
| D9 | Data-owner requests | Request | — | Enabling | — |
| D10 | GSE140829 independence | "Unverified" | — | Enabling | D9 |
| D11 | GSE140829 input | Series Matrix + batch; S13 (unit rule open) | ComBat | A5 | D19 |
| D12 † | Replication criteria | C-c §8.5; C-a §8.6; C-b descriptive | Inferential C-b | A5 | D15, D20 |
| D13 † | Specificity | All locked genes; Q1 two-sided primary (IPD); per-gene two-sided BH within contrast; GPD and GU secondary; coverage applies; S15; δ unset (equivalence unavailable unless approved at A5) | Q2 directional; Holm across contrasts; GPL570 coverage values; replicated-only add-on | A5 | D6, D12 |
| D14 | Pathways | As v5 §9 | Correlation; collections | A5 | D6, D8 |
| D15 † | FDR, cap, coverage | q < 0.05; 200 unique; per-direction coverage rule (§8.4) | Other values | A5 | — |
| D16 † | Sensitivity set | S1–S16 | — | A5 | D4–D7, D13, D18, D21 |
| D17 | Filters | None (discovery and validation); S7 | — | A2 | D15 |
| D18 † | Identity and duplicates | §4 workflow; D-1 keep one; D-2 option (a); D-3/D-4 keep lowest GSM, S16 | Reverse D-3/D-4 roles; D-2 options (b)/(c) | A2 | D9 |
| D19 | GSE140829 mapping | Approved resource | — | Enabling | D8, D6 |
| D20 † | Replication hierarchy and inference | W1; C-c one-sided with L_c; C-a q < 0.05, no gatekeeping; separate α per cohort; no magnitude comparison | W2; two-sided C-c; gatekeeping; Holm; approved standardization | A5 | D12 |
| D21 | Cell composition | Not proposed | — | A5 (if S11 retained) | D8 |
| D22 † | QC policies; R8 requirement | §3.5 policies; **R8 variant V-A / V-B / V-C unset** | — | A3 | D5 |

---

## 14. Items requiring approval or resolution

### 14.1 PI scientific decisions (Tier A)

| Decision | Choice required |
|---|---|
| D22 | R8 variant |
| D5 | D_min, or option (a)/(b)/(c) |
| D7 | c₁–c₃ and scope |
| D6 | Option, selection sets, freezing |
| D20 | W1/W2; C-c sidedness; C-a rule; gatekeeping; cross-cohort multiplicity |
| D13 | Q1/Q2; contrast multiplicity; GPL570 coverage; δ or "not used"; GU interpretation |
| D18 | Duplicate handling |
| D15, D16, D17, D12, D14, D11, D21 | As listed in §13 |
| D1–D4 | As listed in §13 |

### 14.2 Unresolved methodology

- A validated R8 separation criterion.
- A valid inferential C-b.
- A batch-neutral R9.
- G1 dependence under unequal variances, and for re-included arrays (§6.4).
- G1b for GSE99039.
- G2 for GPL570.
- The S13 unit rule.
- A justified cross-cohort score standardization.

### 14.3 External dependencies

| Item | Dependency |
|---|---|
| D0 | Notion plan |
| D8 | Software environment |
| D9 / D10 | Data owners |
| D19 | GSE140829 mapping |
| — | GPL570 sex probes and annotation |
| — | Annotation and gene-set releases |
| — | Verification of software behaviour: camera statistic; estimated weights |

---

## 15. Metadata-only checks for later (no pass/fail check before Tier A)

1. M1–M8, per v5 §4.3, at Tier B step 8 only.
2. **S15 eligible counts:** GSE99039 samples with both age at exam and sex present, by contrast; and
   the descriptive comparison of age-present vs age-missing samples (sex, batch, group).
3. R2-ID and duplicate-review C1 candidates (§4), at Tier B step 4.
4. Sex-probe presence:
   - GSE140829 after D19;
   - GSE99039 after the GPL570 annotation is pinned.
5. The GSE140829 223-row difference, after D19.
6. Annotation coverage per platform; the expected universe.
7. Lock coverage per cohort and contrast (identifiers only).
8. Gene-set sizes after intersection with the universe.
9. Version inventory after D8.

---

## 16. Disposition of [REG] items

| Item | Status | v6 § |
|---|---|---|
| T1 specificity sidedness | **Resolved in specification.** Q1 non-directional primary; Q2 optional directional; per-gene two-sided; families defined. Final choice remains D13 (unapproved) | 9.3–9.5, 7.2 |
| T2 age-adjusted GSE99039 sensitivity | **Resolved:** restored as S15 with S15-ref; the map updated | 10.2, 0.1 |
| T3 G1 selection scope | **Resolved in specification:** selection sets, timing, permitted information, freezing, exceptions, validity argument. Choice remains D6 (unapproved) | 6.2–6.4 |
| T4 C-a claim | **Resolved as a proposal:** null, direction, family, q < 0.05 rule, claim boundaries. Remains D20/D12 (unapproved) | 8.6 |
| T5 C-c test vs CI | **Resolved:** decision via the one-sided test and the matching one-sided bound; the two-sided CI is descriptive and answers a different question. Alternatives listed under D20 | 8.5 |
| T6 R8 requirement | **Resolved in specification:** per-analysis table, status vocabulary, variants V-A/B/C. Choice remains D22 (unapproved); no threshold invented | 3 |
| T7 score comparability | **Resolved:** magnitude comparison prohibited unless an approved standardization exists | 8.9 |
| T8 D4/D7 order | **Resolved** | 5, 13 |
| T9 redundant coverage rule | **Resolved:** removed, with proof that meaning is unchanged | 8.4 |
| T10 duplicate review | **Resolved in specification:** workflow, evidence rules, categories, log, uncertainty. Handling remains D18 (unapproved) | 4 |
| Approval order | **Resolved:** Tier A before any computation; execution-only items later | 2 |
| Remaining open (not forced) | D_min; c₁–c₃; D6 option; W1/W2; δ; R8 variant; S13 unit rule; GPL570 G2 and G1b; external dependencies | 14 |
