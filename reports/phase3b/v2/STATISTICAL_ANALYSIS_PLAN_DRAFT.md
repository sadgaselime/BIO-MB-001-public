# BIO-MB-001 — Statistical Analysis Plan, DRAFT v2 (Phase 3B, reviewer-informed)

**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen. Supersedes nothing until approved;
`reports/phase3b/v1/STATISTICAL_ANALYSIS_PLAN_DRAFT.md` is preserved unchanged.**

Nothing in this document has been executed. No differential-expression, pathway, feature-selection,
QC-statistic or predictive computation has been run; no expression values have been examined for
this draft; no sample is excluded; no final analysis population or count exists. Metadata-only
facts added in v2 (age ranges, participant-code formats, sex-probe availability) came from phenotype
tables and probe-ID lists, not from expression values.

Labels: **[PROPOSED]** a choice this draft suggests, requiring approval · **[EVIDENCE]** supported
by a cited report or verified local file · **[DECISION NEEDED]** no single answer is determined by the
evidence · **[DATA NEEDED]** requires information not available locally · **[PROPOSED (no source)]** a
rule suggested here without an existing source · **[GAP]** a specification gap that can be closed
without looking at disease-association results.

Reference keys: [2A]–[2D], [3A] as in v1 (Phase 2A–3A reports); **[3A]** =
`reports/phase3a/GSE63060/v1/POPULATION_ELIGIBILITY_DECISION_FRAMEWORK.md`, whose facts **F1–F14**,
estimands **E1–E3**, rules **C1–C12** and gate conditions **G1–G9** are cited here; **[P1]** =
`data/processed/<GSE>/phenotype_table.tsv` (derived from GEO sample records); **[v1]** = the v1 draft.

---

## 0. What changed from v1 (summary)

| Review area | Main change in v2 |
|---|---|
| A Estimand | Unchanged proposal (E2), now with an explicit register of unresolved historical discrepancies (§3.3) |
| B Eligibility | Each of R1–R13 reviewed individually; objective vs judgement-based rules separated; R2 code parsing defined; explicit label-handling table (§4.3) |
| C Sex check | Measurements, combination method, comparison and ambiguity handling specified; **no validated threshold claimed** (§5.1) |
| D Outliers | Correlation, feature set, robust scale and threshold defined; limitations stated; no automatic exclusion (§5.2) |
| E Features | **Default changed:** no additional expression filter in the primary analysis (25th percentile becomes a sensitivity); multi-probe biases and the S8 variance-selection problem documented (§6) |
| F Model | Metadata-only identifiability checks and a prespecified response tree (§7) |
| G Sensitivity | **S1 corrected:** shared age range is the intersection 61–88, not "≥61"; S4, S8, S10 risks expanded (§8) |
| H Replication | Separate roles and reporting for GSE140829 and GSE63061; the three replication criteria reviewed; sign-test independence problem documented (§9) |
| I Specificity | Three-category evidence scheme; equivalence margin left unresolved (§10) |
| J Pathways | Gene universe, multiplicity and the version list to pin (§11) |
| Register | D0–D16 retained with the same identities; **new D17–D22** for genuinely missing decisions (§13) |

---

## 1. Inputs reviewed and limitations

Unchanged from [v1] §0, plus:

- **Notion:** no Notion connector was available in the session that produced v1. The Notion
  Analysis Plan / Statistical & Validation Plan, if one exists, has **not** been reviewed (D0).
- No hypotheses, analysis-plan or statistical/validation-plan document exists in the project.

## 2. Objectives and hypotheses

Unchanged from [v1] §1 (Q, H1–H3 and principles). H1–H3 wording remains **[PROPOSED]**.

---

## 3. Primary estimand and population (review area A)

### 3.1 Proposed primary estimand [PROPOSED — requires approval, D1]

**E2, deposited-label estimand:** the difference in deposited-scale blood expression, per probe,
between GSE63060 samples deposited with GEO `status` "AD" and samples deposited as "CTL",
conditional on the covariates approved under D7, among samples meeting the approved eligibility rules.

### 3.2 Deposited diagnosis versus diagnosis at blood collection [EVIDENCE]

| Concept | What it means | Available? |
|---|---|---|
| Deposited diagnosis | The GEO `status` field as deposited | Yes, for all 329 samples ([3A] F2) |
| Diagnosis at blood collection | Clinical diagnosis at the first visit, when blood was drawn | **No** per-sample source ([2C] §4; [2D] §3) |
| Later conversion | MCI at baseline, AD within 2 years | Aggregate evidence only: GEO "AD" 145 = AD 104 + MCIc 41 in Lunnon 2013 ([2C] §3.2) |

No individual sample is relabelled, excluded or labelled a converter. Reports must state the E2
definition and the converter caveat together ([v1] §2 interpretation boundaries, unchanged).

### 3.3 Unresolved historical discrepancies (kept visible)

| # | Discrepancy | Source | Status |
|---|---|---|---|
| H1 | ~41 deposited "AD" likely MCI at blood draw; not identifiable per sample | [2C] §3.2, §4.1–4.2 | UNRESOLVED |
| H2 | 21 GEO samples aged <65 although both Lunnon papers state <65 excluded | [2C] §2 row 9 | UNRESOLVED |
| H3 | GEO MCI 80 vs Lunnon 2013 MCInc 77; GEO 329 vs 326 | [2C] §5 | UNRESOLVED |
| H4 | Participant-code letter convention undocumented | [2C] §5 | UNRESOLVED |
| H5 | Submitter QC exclusions (detection, XIST, RIN, comorbidity) not identifiable | [2C] §2 row 7 | UNRESOLVED (permanent unless owners supply) |
| H6 | Sood et al. 64 vs 67 controls; GSE63061 Table 1 vs Methods (71/72, 31/30) | [2B] §3 | UNRESOLVED (relevant only to Option B / GSE63061) |
| H7 | Patel 2020: 2 sex mismatches + 10 outliers removed from GSE63060, IDs unpublished | [2C] v1 §2.3 | UNRESOLVED |
| H8 | Deposited normalization probably included arrays later removed | [2C] §4.4; [2B] §5 | SUPPORTED, NOT PROVEN |
| H9 | Participant independence GSE63060 ↔ GSE63061 / GSE140829 | [3A] F13 | UNRESOLVED |

---

## 4. Sample identity and eligibility (review area B)

All rules below are **provisional**. None is applied; no exclusion list exists.

### 4.1 Rule-by-rule review

"Objective" = can be applied mechanically from recorded fields once approved; "judgement" = requires
a scientific choice (threshold, definition or interpretation) before it can be applied.

| Rule | Definition (v2) | Field / file | Evidence | Objective or judgement | Implementable now? | Needs decision / data | Blind to expression results? |
|---|---|---|---|---|---|---|---|
| R1 Input | Use the 329 GSM columns of `GSE63060_series_matrix.txt.gz` | `data/raw/GSE63060/…series_matrix…` | [2A] §2, §9 | Objective (choice already justified) | Yes | D3 | Yes |
| R2 Identity | See §4.2 | `geo_accession`, `title`, `description`, `char:age`, `char:gender` | Phase 1 reconciliation | Objective checks; **interpretation of the code as a participant ID is judgement** | Yes | D18 | Yes |
| R3 Case/control | Case: `char:status` = "AD"; control: "CTL" | `char:status` | GEO records | Objective | Yes | D1, D2 | Yes |
| R4 MCI | `status` = "MCI" outside the primary contrast; retained for exploratory work | `char:status` | Project scope | Objective | Yes | D2 | Yes |
| R5 Label handling | See §4.3 | `diagnosis_raw`, `diagnosis_status` per cohort | Phase 1 classification | **Judgement** (what counts as ambiguous; whether to exclude or analyse separately) | Yes once approved | D2 | Yes |
| R6 Converters | No converter-based exclusion or relabelling; code letters not used | — | [3A] C5 | Objective (a rule of non-use) | Yes | D9 for any future E1 | Yes |
| R7 Age | One prespecified option (§8 S1 corrected) | age fields per cohort | [2C] §2 row 9 | **Judgement** | Yes once chosen | D4 | Yes |
| R8 Sex consistency | See §5.1 | Series Matrix sex probes; `char:gender` | Lunnon 2012/2013 XIST check; Patel 2020 | **Judgement** (method; ambiguity rule; no validated cutoff) | Probes present in GSE63060/63061; GSE140829 needs mapping | D5, D19, D22 | **Yes — required** |
| R9 Array outliers | See §5.2 | Series Matrix | Patel 2020 / GSE140829 submitters as precedent only | **Judgement** (metric, k) | Yes once approved | D5, D22 | **Yes — required** |
| R10 Inherited QC | Record submitters' pre-deposit QC as inherited, unauditable | — | [2C] §2 row 7; [3A] F9 | Objective (documentation) | Yes | No | — |
| R11 Undeposited arrays | `4856076038_D` and the 3 empty-header non-normalized columns are not eligible | — | [2A] §4–5 | Objective (follows from R1) | Yes | No | Yes |
| R12 Sood flag | `included in case -control study` not used as eligibility | `char:included…` | [2B] §4, §6 | Objective (a rule of non-use) | Yes | D1 | Yes |
| R13 Freeze | Exclusion log (GSM, rule, value, reviewer decision) written, checksummed and approved before any case–control model | new versioned file | Project principles | Objective (procedure) | Yes | Gate G2/G6 | Yes |

### 4.2 R2 — sample identity and the participant code

**Why uniqueness is required.** One participant contributing two arrays would (i) violate the
independence assumption of the per-sample linear model, (ii) inflate apparent precision, and (iii)
risk leakage if the same participant appeared in discovery and validation. GEO provides no explicit
participant-ID field; the `description` field is the only candidate.

**How the code is parsed [PROPOSED].** The code is treated as an opaque string and compared by exact
match (after trimming whitespace only, as in Phase 1). Structure observed [EVIDENCE, P1]:

| Series | Observed shapes (digits shown as 9) | Distinct / total |
|---|---|---|
| GSE63060 | `KPOM9999`, `KPOA9999`, `KPOC9999`, `PRG[A/C/M]9999`, `THS[A/C/M]9999`, `TLS[A/C/M]9999`, `LDZ[A/C/M]9999`, `LND9999` | 329 / 329 |
| GSE63061 | `[KPO/LDZ/PRG/THS/TLS/LND][ADC/CTL/MCI]999`, `DCR99999`, `OA9999` | 388 / 388 |

The prefix/letter structure is **not** used for eligibility (R6). Parsing into site or group is used
only where explicitly approved (site covariate sensitivity S3; code-letter sensitivity S4).

**What uniqueness does and does not show.** Unique codes rule out *exact* duplicate codes. They do
**not** prove one array per participant: the code is not documented as a participant identifier
([2C] §5, H4), and a participant could in principle carry different codes across visits or series.
The formats differ between GSE63060 and GSE63061, so absence of shared codes (Phase 1 overlap check)
does not establish independence (H9).

**Proposed R2 definition:** include a column only if its GSM, array barcode (`title`) and code
(`description`) are each unique within the series and age and sex are non-missing. Additionally
[PROPOSED (no source)]: after sample QC, a diagnosis-blind check for near-identical arrays
(correlation above a prespecified bound) as a technical-duplicate screen; any hit is reviewed, not
auto-excluded (D18).

### 4.3 R5 — explicit label handling (all cohorts) [PROPOSED; D2]

| Category | Definition | Labels observed [P1] | Proposed handling |
|---|---|---|---|
| Missing | No value in the diagnosis field | none in any of the four cohorts | Exclude from case–control contrasts; log |
| Borderline | Label states a borderline category | GSE63061 "borderline MCI" (3) | Exclude from AD/CTL contrasts; may enter exploratory MCI work only if approved |
| Transitional | Label states a change of diagnosis | GSE63061 "CTL to AD" (1), "MCI to CTL" (1) | Exclude from all primary and replication contrasts; list individually |
| Non-specific | Label that does not identify a study group | GSE63061 "OTHER" (1); GSE99039 "HD_HD_BATCH" (8) | Exclude; list individually |
| Conflicting | Two or more different diagnosis values for one sample | none observed | Exclude; list individually |
| Mapped | Label maps to one canonical group | all others | Eligible subject to remaining rules |

GSE63060 contains no samples in the first five categories [EVIDENCE]. Exclusion is from contrasts,
not deletion from data; every excluded sample is logged by GSM and label.

---

## 5. Sample QC (review areas C and D)

Both QC procedures are **diagnosis-blind**: they are computed and reviewed without fitting or viewing
any case–control model, and before any disease-association result exists. Flags are proposals for
review (D22), not automatic exclusions.

### 5.1 R8 sex-consistency check

**Measurements [EVIDENCE: probe presence verified from Series Matrix ID lists].**

| Platform / series | XIST | Y-chromosome probes present in the Series Matrix |
|---|---|---|
| GSE63060 (GPL6947) | ILMN_1764573 | RPS4Y1 ILMN_1783142; DDX3Y ILMN_1732039; KDM5D/JARID1D ILMN_1685690; UTY ILMN_1739587, ILMN_2264634; EIF1AY ILMN_1755537, ILMN_2228976; USP9Y ILMN_2056795; ZFY ILMN_1804958, ILMN_2090059; CYorf15A ILMN_1670821; CYorf15B ILMN_1756506, ILMN_2094332 (13 probes, 9 genes) |
| GSE63061 (GPL10558) | ILMN_1764573 | the same 13 probes (NLGN4Y ILMN_2210199 and UTY ILMN_1651456 are on the platform but absent from the Series Matrix) |
| GSE140829 (GPL15988, nuID) | present in the platform manifest / raw file | all 15 present in the raw file; **presence in the nuID Series Matrix not verified** — requires ILMN→nuID mapping (lumi ID mapping, not installed) [GAP; D19] |

**Proposed combination method [PROPOSED (no source); D5].**

1. X score = XIST value (deposited scale).
2. Y score = median across the available Y probes of each probe's value centred by its own median
   across all arrays in the series (all 329 for GSE63060; diagnosis-blind).
3. Expression-derived sex: assign "female pattern" when X is high and Y low, "male pattern" when X is
   low and Y high, and "ambiguous" otherwise (both high, both low, or within an intermediate zone).
4. "High/low" boundaries are taken from the separation between the two modes of the X and Y score
   distributions within the series (for example, the midpoint between the two cluster centres of a
   two-group partition of (X, Y)), fixed by a written procedure before the values are inspected.

**What the data can and cannot justify.**

- XIST and Y-gene expression are biologically sex-linked and usually strongly bimodal in blood, which
  makes the approach plausible. **No validated numeric cutoff exists for these deposited, VST-scaled
  data**, and whether the distributions here separate cleanly can only be seen by inspecting them.
- This draft therefore does **not** set numeric thresholds. It proposes the procedure. Thresholds
  would be derived from the sex-probe distributions alone (no diagnosis information, no other genes),
  documented, and approved (D5) before any exclusion.

**Comparison with recorded sex and ambiguity handling [PROPOSED; D22].**

| Expression-derived | Recorded `char:gender` | Classification | Proposed handling |
|---|---|---|---|
| Female or male pattern | Same | Concordant | Eligible |
| Female or male pattern | Opposite | **Discordant** (possible sample or metadata mix-up) | Proposed exclusion from all analyses; listed by GSM; included in sensitivity S5 |
| Ambiguous (e.g. X high and Y high, or both low) | Either | Ambiguous | Not excluded automatically; listed; reviewer decides by a prespecified rule (exclude / retain / sensitivity only) |
| Any | Missing | Unassessable | Not applicable to GSE63060 (sex complete); GSE99039 53 missing ([P1]) |

Notes: XIST-high plus Y-high can indicate a sample mixture or a sex-chromosome karyotype variant; the
plan does not attempt to distinguish these.

### 5.2 R9 array-outlier check [PROPOSED (no source); D5, D22]

**Definition.**

- **Arrays:** all 329 Series Matrix arrays (diagnosis-blind and largest reference set). Alternative:
  only R3-eligible arrays (D5).
- **Feature set:** all 38,323 deposited probes, values as deposited (no additional filter, no
  centring). Alternative: probes centred by their own mean across arrays (more sensitive to
  sample-specific deviation, but more influenced by group and batch structure) — D5.
- **Similarity:** Pearson correlation r_ij between arrays i and j; Fisher transform z_ij = atanh(r_ij).
- **Per-array statistic:** m_i = median over j ≠ i of z_ij.
- **Robust centre and scale:** M = median(m_i); S = 1.4826 × median(|m_i − M|) (scaled MAD).
- **Flag:** m_i < M − k·S. **Provisional k = 3**; alternatives k = 2.5 or 4 (S5), or an
  interquartile-range rule. k is fixed before inspection and is not tuned.

**Limitations.**

- **Diagnosis structure:** if disease shifts many genes, AD arrays may have systematically slightly
  lower correlation with the (control-plus-MCI-heavy) majority, which could produce diagnosis-related
  flagging. Deposited, quantile-type-normalized data make large shifts unlikely, but this cannot be
  assumed.
- **Batch structure:** arrays on a technically shifted chip may be flagged together, so the check
  partly detects chip effects, which the model also adjusts for.
- **Masking:** a cluster of similar outliers raises its own median correlation.

**Required descriptive review before any exclusion (D22).** Report flagged arrays with their GSM,
chip, diagnosis and m_i; tabulate flags by diagnosis and by chip. Diagnosis appears only as a count of
flags, never as an association result. If flags are concentrated in one diagnosis group or one chip,
the reviewer applies a prespecified response (for example, a within-chip recalculation) rather than
choosing ad hoc. No flagged array is excluded until the rule and the flag list are approved.

---

## 6. Features, annotation and analysis units (review area E)

### 6.1 Additional expression filter — reassessed [PROPOSED; D17]

- v1 proposed retaining probes above the 25th percentile of mean expression. On review:
  1. the deposited probe set is already filtered by the submitters (38,323 of 48,803 platform
     probes; [2A] §6), almost certainly removing the lowest-signal probes;
  2. limma-trend models the mean–variance relationship directly;
  3. an additional filter reduces the multiple-testing burden but can remove genuinely low-expressed,
     disease-relevant transcripts.
- **v2 default [PROPOSED]: no additional expression filter in the primary analysis.** The 25th- and
  50th-percentile filters move to sensitivity S7.
- Any filter uses the overall mean across all eligible samples, a statistic approximately independent
  of the case–control test statistic under the null; filters using group labels or between-group
  variance are not permitted.

### 6.2 Analysis units

| Analysis | Unit | Why |
|---|---|---|
| Discovery (primary) | **Probe** | Avoids mapping and aggregation choices; every deposited probe tested |
| Replication / consistency | **Gene (Entrez)**, or identical probe ID where both platforms carry it (D6 alternative) | Platforms differ; gene is the common unit |
| Disease specificity | Gene (Entrez) | GPL570 vs Illumina |
| Pathways | Gene (Entrez) | Gene-set databases are gene-level |

### 6.3 Multi-probe policy — reassessed [PROPOSED; D6]

- **Proposed default:** for gene-level results, the probe with the highest mean expression across all
  eligible samples (diagnosis-blind), chosen before testing.
- **Rationale:** higher-signal probes tend to have better signal-to-noise; the choice uses no outcome
  information.
- **Potential biases:**
  - It favours probes for abundant transcripts or isoforms, which may differ from the isoform affected
    by disease.
  - Different platforms may select probes targeting different transcripts of the same gene, so
    cross-platform discordance can be technical.
  - It ignores information in other probes.
- **Alternative for Illumina–Illumina comparisons (GSE63060 v3 → GSE63061/GSE140829 v4):** match by
  identical Illumina probe ID where present on both platforms (sex probes, for example, share IDs),
  and fall back to gene-level matching otherwise. This is likely to reduce technical discordance, but
  coverage must be counted (D6).
- **Not recommended:** v1's sensitivity alternative "largest-variance probe" (S8) uses total variance,
  which includes the between-group difference. It is therefore not independent of the outcome and can
  bias selection towards associated probes. v2 replaces it (§8).
- **Never:** choosing a probe by its association with diagnosis.

### 6.4 Annotation — not pinned yet [DECISION NEEDED; D6]

The current annotation is the 2008 BGX ([2A] §7). No defensible single choice can be pinned without
inspecting candidate resources, which requires network access or an installed environment. Options
for approval:

| Option | Resource | Pros | Cons / to pin |
|---|---|---|---|
| A1 | Bioconductor `illuminaHumanv3.db` (GPL6947) and `illuminaHumanv4.db` (GPL10558/GPL15988), with `lumiHumanIDMapping` for nuIDs, from one Bioconductor release | Standard, versioned, reproducible | Bioconductor release, package versions and annotation dates |
| A2 | GEO platform tables GPL6947 / GPL10558 / GPL15988 / GPL570 (full annotation) | Submitter-linked | Snapshot date; partly dated |
| A3 | Re-mapping probe sequences (in the BGX) to a fixed genome and transcript set | Most current, transparent | Genome build, transcript release (e.g. GENCODE N), aligner and version; more work |
| A0 | 2008 BGX as primary | Already local | Outdated; 4,684 placeholder symbols |

Whatever is chosen, record the resource, version, date and checksum; probes without a current Entrez
ID remain in probe-level discovery and are reported as "unmapped" elsewhere.

---

## 7. Primary statistical model (review area F)

### 7.1 Candidate method [PROPOSED; D7, D8]

Probe-wise linear models with empirical-Bayes moderated variances (`limma`, trend = TRUE). This is
pending approval of a pinned environment (D8); R/Bioconductor is not installed and nothing has been
installed.

### 7.2 Metadata-only identifiability checks (before any model is fitted) [GAP — resolvable now]

These use phenotype and barcode metadata only, no expression values:

1. **Diagnosis × chip table** for R3-eligible samples: counts per chip per group; number of chips
   containing only one group; samples on such chips.
2. **Design-matrix rank** of the proposed design (group, age, sex, chip), computed from metadata.
3. **Chip size:** chips with one eligible sample (no within-chip information).
4. **Chip × site table** (site = code prefix, if S3 is approved): collinearity between chip and site.
5. **Age and sex by group and by chip:** distribution summaries (known by group: AD mean 75.4 vs
   72.4; female 68% vs 60%; [2B] §3).
6. **Residual degrees of freedom** of the design.

### 7.3 Prespecified response (decided before any expression model) [PROPOSED; D7]

| Check result | Response |
|---|---|
| Full rank; no single-group chips | Chip as a fixed effect (primary design) |
| Full rank; some single-group chips | Chip as fixed effect (the comparison uses within-chip information). Report the proportion of samples on single-group chips. If that proportion exceeds a prespecified threshold (to be set in D7), use chip as a blocking factor with `duplicateCorrelation` instead |
| Rank-deficient because chip is aliased with group | Chip cannot be a fixed effect. Use `duplicateCorrelation` blocking; if not estimable, omit chip and record confounding as a limitation |
| Singleton chips | Retained; they contribute nothing to within-chip contrasts under a fixed effect |

The rule is selected from the metadata results above and recorded before any differential-expression
output exists. It is not revisited after results are seen.

### 7.4 Covariates: rationale and limitations

| Covariate | Rationale | Limitations |
|---|---|---|
| Age (linear) | Known to affect blood expression; AD older than controls | Linear form may misfit (S2 spline); residual confounding; age may relate to disease stage |
| Sex | Large sex effects in blood; sex distribution differs by group | Recorded sex assumed correct after R8 |
| Chip | Technical batch available for every sample | Possibly correlated with recruitment site and processing date; handled by §7.3 |
| Site (code prefix) | Recruitment and handling differences | Mapping supported, not proven ([2C] §4.3); likely collinear with chip; sensitivity only (S3) |
| Not available | APOE, MMSE, RIN, cell counts, medication, fasting state | Unmeasured confounding stated as a limitation; cell composition only via S11 |

### 7.5 Contrast, multiplicity, reporting, missing data, assumptions

Unchanged from [v1] §4.6–4.9, except:

- **Effect scale:** AD − CTL on the deposited scale, which is approximately log2 (caveat retained).
- **Multiplicity:** BH FDR across all tested probes (number tested reported); proposed primary
  threshold FDR < 0.05 (D15).
- **Report:** log2 effect with 95% CI, moderated t, p, FDR, mean expression, annotation and version,
  and group sizes after each eligibility and QC step.
- **Missing data:** none in the Series Matrix; age and sex complete in GSE63060.
- **Assumption diagnostics** (mean–variance trend, residual summaries) are reported; they do not change
  the model after results unless a prespecified failure rule is approved (D7).

---

## 8. Sensitivity analyses — consistency review (review area G)

All are **prespecified proposals** (D16) to be run and reported whatever their results.

| # | v1 definition | v2 review | v2 definition |
|---|---|---|---|
| S1 | Restrict to ≥65; and to the range shared with GSE140829 (≥61) | **Corrected.** Observed AD/CTL age ranges [EVIDENCE, P1]: GSE63060 52–88; GSE63061 59–95; GSE140829 61–89. Their intersection is **61–88**, not "≥61". A lower bound alone does not define a shared range | (a) ≥65 (papers' criterion); (b) **61–88**, the intersection of the three AD cohorts' observed AD/CTL ranges. GSE99039 is excluded from the intersection: age missing for 199/438 IPD/CONTROL; 35–82 where present |
| S2 | Age spline (3 df) | Consistent | Unchanged |
| S3 | Add site; remove chip | Site–chip collinearity must be checked first (§7.2 item 4) | Unchanged; run only if the §7.2 check shows site is estimable alongside or instead of chip |
| S4 | Exclude 37 "M"-coded AD | **High risk** — see below | Retained as an explicitly labelled, convention-dependent sensitivity |
| S5 | Include R8/R9-flagged arrays; k = 2.5 and 4 | Consistent with §5 | Unchanged; plus "ambiguous sex-check arrays excluded" variant if D22 retains them in the primary |
| S6 | arrayWeights | Consistent | Unchanged |
| S7 | No filter; 50th percentile | **Updated** to match the new primary default (no filter) | 25th-percentile and 50th-percentile mean-expression filters (diagnosis-blind) |
| S8 | Largest-variance probe; mean of probes | **Largest-variance option removed** (selection depends on between-group variance; §6.3) | (a) mean of all mapped probes per gene; (b) identical-probe-ID matching where available (D6) |
| S9 | 2008 BGX vs modern annotation | Consistent once D6 is decided | Unchanged |
| S10 | Re-normalize the non-normalized file with the inferred 3-column mapping | **High risk** — see below | Retained only if approved, labelled inferred |
| S11 | Add estimated cell proportions | Requires a method and reference (D21) | Unchanged, pending D21 |
| S12 | Flagged subset (49/67) | Consistent; never a replacement primary | Unchanged |
| S13 | GSE140829 final ComBat file vs Series Matrix + batch | Applies to replication, not discovery | Unchanged; reported within §9 |

**S4 risks.** The letter convention (A/C/M) is undocumented (H4). Excluding M-coded AD assumes that M
means "MCI at baseline", which is plausible from the aggregate evidence but unproven. It cannot remove
the ~4 converters among London samples, which have no letter, and could remove non-converters if the
letter means something else. Its result must be labelled "under an undocumented coding assumption"
and cannot be presented as an estimate of E1.

**S10 risks.** The 3 empty-header columns were mapped to GEO samples by exact rank identity
([2A] §5): strong, but inferred, not documented. Re-normalization would use only the 329 deposited
arrays, whereas the submitters normalized with additional arrays (H8). It would also include the
10,480 low-signal probes the submitters removed, with an unknown filter rule. Differences from the
primary analysis would therefore mix normalization, probe set and sample-set effects, and cannot be
attributed to normalization alone.

---

## 9. Replication and consistency (review area H)

### 9.1 Roles and interpretation

| Cohort | Role (v2) | What a positive result can support | What it cannot support |
|---|---|---|---|
| GSE140829 | **External replication candidate** until participant independence from AddNeuroMed is documented (H9; D10) | "Replicated in a separately deposited cohort on a different platform version (independence unverified)" | "Independent external validation" until D10 evidence exists |
| GSE63061 | **Related-cohort consistency analysis** (same SuperSeries, consortium and recruitment framework; different platform version and laboratory; possible participant overlap) | "Consistent in a related AddNeuroMed batch" | Any claim of independent replication; agreement may be inflated by shared participants or design |

Neither cohort is used to select genes, set thresholds or tune the primary model.

### 9.2 Locking the discovery signature [PROPOSED; D15]

After the discovery analysis is approved, a versioned, checksummed lock file is written. It contains,
per probe: probe ID, annotation resource and version, Entrez ID, gene symbol, effect, 95% CI, FDR,
direction, and the gene-level probe chosen under D6. It also states the signature definition (all
probes at FDR < 0.05 mapped to genes; if more than the prespecified cap, the top genes ranked by FDR
then |effect|; proposed cap 200, D15) and fixed score weights (+1 up, −1 down). The lock file, plus
its checksum, must exist before any validation-cohort expression value is modelled against diagnosis.

### 9.3 Mapping and coverage reporting

Each locked gene is placed in exactly one category per validation cohort:

1. no Entrez mapping on the validation platform (annotation);
2. mapped, but no probe present in the deposited Series Matrix (submitter filtering);
3. present but excluded by approved feature QC;
4. tested.

Counts and gene lists are reported for every category. Categories 1–3 are "not measurable", never
"not replicated".

### 9.4 Replication criteria — reviewed [PROPOSED; D12, D20]

| Criterion | Question it answers | Justification | Limitations |
|---|---|---|---|
| C-a Per-gene one-sided test (direction from discovery), BH across tested locked genes | Which individual genes replicate? | Direction is prespecified, so a one-sided test matches the hypothesis | Low power per gene; BH assumes positive dependence (reasonable for co-expressed genes) |
| C-b Direction concordance across tested locked genes | Does the signature's direction pattern transfer beyond chance? | Summarizes the signature without thresholds | **The sign test assumes independent genes; co-expression makes it anti-conservative.** v2 proposes a label-permutation null within the validation cohort (permute diagnosis labels, recompute concordance; ≥10,000 permutations, fixed seed). The sign test is reported descriptively only |
| C-c Prespecified signature score (mean z of up-genes − mean z of down-genes; z computed within the validation cohort across all eligible samples, diagnosis-blind), modelled with the same covariates | Does the composite signature differ between groups, and by how much? | One test using all genes; an interpretable effect size | Depends on weights and gene set; a significant score does not imply that individual genes replicate |

The three criteria answer distinct questions, but together they create a multiplicity problem.
**Proposed hierarchy (D20):**

- Primary replication outcome: C-c, the score effect, one-sided α = 0.05, reported with its CI.
- Secondary: C-b (permutation) and C-a (per-gene).
- **Alternative:** C-b as primary.

The choice needs approval because the scientific question ("to what extent do features replicate")
does not by itself determine whether the composite or the per-gene view is primary.

**Uncertainty reporting:**

- Discovery and validation effects side by side with CIs.
- The proportion of tested genes replicating under C-a, with a binomial CI labelled descriptive.
- Platform and scale differences stated.

### 9.5 Consistency reporting for GSE63061

Same mapping (§9.3) and criteria, reported under the "consistency" heading. In addition, report the
correlation between discovery and GSE63061 effects across tested locked genes (with CI). State
explicitly that possible participant overlap could inflate agreement. GSE63061 transitional and
ambiguous labels follow R5.

### 9.6 Validation-cohort inputs and covariates [PROPOSED; D11, D19]

| Cohort | Input | Covariates | Open items |
|---|---|---|---|
| GSE140829 | Series Matrix (VST + RSN, nuID, 587, not batch-corrected); final ComBat file as S13 | age_at_draw, Sex, batch (19) | nuID→Entrez and sex-probe mapping (lumi ID mapping); D19 |
| GSE63061 | Series Matrix | age, gender, chip (34 chips from barcodes) | Chip-confounding check as in §7.2 |

---

## 10. Disease specificity — GSE99039 (review area I) [PROPOSED; D13]

### 10.1 Groups (kept distinct)

| Group | Label(s) | Use |
|---|---|---|
| Idiopathic PD | IPD | Primary PD contrast vs CONTROL |
| Controls | CONTROL | Reference |
| Genetic PD | GPD | Separate contrast vs CONTROL; never pooled with IPD without an approved rule |
| Genetically unaffected | GENETIC_UNAFFECTED | Separate; never pooled with CONTROL without an approved rule |
| Other neurological | each OTHER_NEURO label (HD, PSP, MSA, CBD, DRD, DRD-DYT5, ATYPICAL_PD, PD_DEMENTIA, Vascular dementia) | Each tabulated; pooling only under an approved rule (several are not neurodegenerative, e.g. DRD) |
| Ambiguous | HD_HD_BATCH | Excluded (R5) |

### 10.2 Evidence categories per locked, replicated gene

| Category | Rule | Status |
|---|---|---|
| Association with PD | 95% CI of the PD-vs-control effect excludes 0 and FDR < 0.05 across the tested genes | Definable now |
| Compatible with no meaningful association | 90% CI lies entirely within ±δ (two one-sided tests) | **δ unresolved; cannot be applied until approved (D13)** |
| Inconclusive | Neither of the above | Definable once δ exists |
| Until δ is approved | "Association" or "**association not demonstrated**" only | Non-significance is never reported as absence of association |

Choosing δ needs a scientific justification (for example a fraction of the AD effect, or a minimal
biologically meaningful log-fold change on a comparable scale). It is left open.

### 10.3 Covariates and limitations

- **Missing covariates:** sex is missing for 53/558; age at exam is present for only 239 of the 438
  IPD/CONTROL samples. Complete-case age adjustment would discard about 45%.
- **Proposal:** sex + batch primary, age-adjusted complete-case as a sensitivity. This requires
  approval (D13).
- **Cross-platform limits:**
  - Affymetrix RMA vs Illumina VST;
  - different laboratories, populations and recruitment;
  - different probe designs.
- **Consequences:** effect sizes are not on a common scale. Cross-cohort comparison of AD and PD
  effects is **descriptive only**. No within-cohort AD × PD interaction is estimable. Non-replication
  across platforms is not evidence of specificity.
- **Optional extension [DATA NEEDED]:** GSE140829's parent SuperSeries GSE140831 includes FTD-spectrum
  disorders on the same platform. It has not been retrieved.

---

## 11. Pathways and exploratory analyses (review area J)

### 11.1 Pathway analysis [PROPOSED; D14] — exploratory interpretation, not confirmatory

- **Gene universe:** all Entrez genes represented by at least one probe tested in the specific
  analysis, on that platform, after approved feature QC. It is defined separately for each cohort and
  analysis and is never the whole genome.
- **Input:** gene-level statistics from §6.2.
- **Methods:**
  - Primary: competitive rank-based testing that accounts for inter-gene correlation (e.g. `camera`).
  - Secondary: over-representation of FDR < 0.05 genes against the same universe.
- **Multiplicity:** BH within each collection, with collections reported separately. Set size limits
  are prespecified (proposed 15–500).
- **Interpretation limits:** blood cell composition, cell activation and GO redundancy; no brain
  mechanisms.

### 11.2 Versions that must be pinned before any execution [GAP / D8, D14]

| Component | To pin |
|---|---|
| R (or Python) | Exact version |
| Bioconductor | Release |
| Statistics | `limma` version |
| Annotation | `illuminaHumanv3.db`, `illuminaHumanv4.db`, `lumiHumanIDMapping`, `hgu133plus2.db`, `org.Hs.eg.db` (versions and annotation dates), or the D6 alternative |
| Gene sets | GO (release date) and Reactome (version), or an MSigDB release; tool versions (e.g. `msigdbr`) |
| Cell composition (if S11) | Method, reference matrix and versions (D21) |
| Environment | Lock file with checksums |

### 11.3 Exploratory only (unless separately approved)

- **Pathway analysis:** §11.1.
- **MCI analyses** in GSE63060 and GSE63061.
- **Code-letter analyses:** S4 is retained as a labelled sensitivity.
- **GSE165082 (RNA-seq) and GSE165081 (methylation):** exploratory; never pooled with microarray data.
- **Machine learning:** only with nested cross-validation inside discovery; never tuned on validation
  cohorts.
- **"Reproduce Sood et al." (Option B):** optional.

---

## 12. Reproducibility requirements

Unchanged from [v1] §10, plus:

- QC flag lists, the identifiability-check tables (§7.2), the response chosen (§7.3) and the signature
  lock file (§9.2) are each versioned and checksummed at the moment they are created.

---

## 13. Decision register (D0–D16 retained; D17–D22 new)

All decisions require the PI's approval before implementation. None is approved.

| ID | Question | Evidence available | Proposed default | Alternatives and consequences | Additional data? | Depends on | Approval before implementation |
|---|---|---|---|---|---|---|---|
| D0 | Is there an existing Notion (or other) analysis/validation plan this draft must reconcile with? | No local plan; Notion not reviewed | Provide the Notion content for reconciliation before approval | Approving without reconciliation risks conflicting plans | **Yes** (Notion content) | — | Yes |
| D1 | Which estimand is primary? | [3A] §2; [2C] §3–4; H1 | E2 (deposited label) with mandatory converter caveat | E1 needs per-sample diagnosis at draw (D9); Option B as primary rejected by default ([2B] §6); E3 is only descriptive | For E1 only | D9 | Yes |
| D2 | Which eligibility and label-handling rules apply (R2–R5, R12; §4.3)? | [3A] Option C; [P1] labels | As in §4 | Stricter rules reduce n; looser ones admit ambiguous labels | No | D1, D18 | Yes |
| D3 | Which expression input? | [2A] §2, §9 | GSE63060 Series Matrix, no re-normalization | Normalized file: needs repairs and contains an unlabelled array; non-normalized: needs re-processing (S10 risks) | No | — | Yes |
| D4 | Age eligibility? | H2; §8 S1 ranges | No restriction; age as covariate; S1(a)/(b) as sensitivities | ≥65 follows the papers but excludes 21 samples with an unexplained discrepancy; 61–88 harmonizes with validation cohorts | Explanation of H2 would help (D9) | D7 | Yes |
| D5 | Sex-check and outlier methods and thresholds (R8, R9)? | §5; probe presence verified; no validated cutoff | §5.1 procedure (thresholds from sex-probe modes, fixed before inspection); §5.2 with k = 3 | Different k or feature sets change who is flagged; all-arrays vs eligible-only reference | No (but thresholds are set only after approved, blinded inspection of sex probes) | D22 | Yes |
| D6 | Annotation resource and multi-probe policy? | [2A] §7; §6.3–6.4 | Not pinned; options A1–A3; highest-mean probe per gene; probe-ID matching alternative for Illumina–Illumina | Choice changes gene-level replication and pathways; A0 (2008 BGX) outdated | Yes (resource or install) | D8 | Yes |
| D7 | Primary model, covariates and the confounding response rule? | §7; [2B] §3 | limma: group + age + sex + chip; §7.3 response tree; threshold for single-group-chip proportion to be set | Blocking vs fixed effect; omitting chip; site inclusion; a failure rule for assumptions | No (metadata checks §7.2 first) | D8, D4 | Yes |
| D8 | Analysis environment? | R absent; venv lacks SciPy/statsmodels | Install a pinned R/Bioconductor environment (limma, annotation packages) | A Python alternative lacks a standard moderated-statistics implementation and needs validation | No | — | Yes (installation itself requires approval) |
| D9 | Request data-owner information? | [3A] §3 Option D; H1–H4, H9 | Request diagnosis at draw, the under-65 explanation, code convention and overlap; proceed with E2 meanwhile | Without it, E1 is infeasible and S4 remains convention-dependent | **Yes** | — | Yes |
| D10 | Standard for calling GSE140829 "independent"? | [3A] F13 | "External candidate, independence unverified" until documented | Over-claiming if overlap exists | **Yes** (documentation) | D9 | Yes |
| D11 | GSE140829 input? | GEO processing statement | Series Matrix + batch covariate; final ComBat file as S13 | ComBat on diagnosis-imbalanced batches can distort effects; final file has 36 fewer samples | No | D19 | Yes |
| D12 | What counts as "replicated"? | §9.4 | C-a, C-b (permutation), C-c as defined | Sign-test-based concordance is anti-conservative; thresholds change claims | No | D15, D20 | Yes |
| D13 | Specificity strategy, groups, covariates and δ? | §10; GSE99039 metadata | IPD vs CONTROL primary; groups distinct; sex + batch primary; δ unresolved | Pooling rules; age-adjusted complete-case loses ~45%; without δ only "not demonstrated" | Justification for δ | D12 | Yes |
| D14 | Pathway framework and versions? | §11 | Competitive rank-based + ORA; GO BP and Reactome, versions to pin | Database and version change results | Yes (resources) | D6, D8 | Yes |
| D15 | Significance threshold and signature size? | §7.5, §9.2 | FDR < 0.05; cap 200 genes ranked by FDR then \|effect\| | A lower cap gives fewer, stronger genes; no cap gives an unwieldy score | No | — | Yes |
| D16 | Which sensitivity analyses? | §8 | S1–S13 as revised in v2 | Adding or removing analyses after results would be selective reporting | No | D4–D7, D21 | Yes |
| **D17 (new)** | Additional expression filter for discovery? | §6.1; deposited set already filtered | None in the primary analysis; 25th/50th percentile as S7 | A filter reduces the testing burden but may remove low-expressed relevant genes | No | D15 | Yes |
| **D18 (new)** | How is participant-code uniqueness used, and is a technical-duplicate screen required? | §4.2; codes undocumented | Exact-string uniqueness (R2) plus a diagnosis-blind near-identical-array screen, reviewed not auto-excluded | Without the screen, duplicate arrays under different codes go undetected | Code documentation (D9) | D9 | Yes |
| **D19 (new)** | Validation-cohort covariates, chip fields and sex-probe mapping (esp. GSE140829 nuIDs)? | §5.1, §9.6 | Covariates per §9.6; sex probes via the lumi ID mapping once installed | Without mapping, R8 cannot be applied to GSE140829 | Mapping package (D8) | D8, D6 | Yes |
| **D20 (new)** | Which replication criterion is primary (multiplicity across C-a/C-b/C-c)? | §9.4 | C-c (score) primary; C-b and C-a secondary | C-b as primary emphasizes direction transfer; no hierarchy inflates false claims | No | D12 | Yes |
| **D21 (new)** | Cell-composition method for S11? | Lunnon 2012 cell-count differences; no measured counts | Not proposed (requires method choice) | Reference-based deconvolution methods differ; may adjust away disease-related signal | Reference choice and versions | D8 | Yes |
| **D22 (new)** | Procedure for reviewing QC flags (who reviews, blinding, ambiguous sex results, flags concentrated by diagnosis or chip)? | §5 | Flags reviewed with GSM, chip and diagnosis counts only; prespecified responses; approval before exclusion | Ad-hoc review risks outcome-driven exclusions | No | D5 | Yes |

---

## 14. Specification gaps vs scientific decisions

### 14.1 Specification gaps resolvable from existing evidence without disease-association results

1. Diagnosis × chip table, design rank, singleton chips and residual df for GSE63060 (§7.2), and the
   same for GSE63061 chips. Metadata only.
2. Chip × site collinearity table (§7.2 item 4). Metadata only.
3. GSE140829 sex-probe and gene mapping from nuIDs, once an ID-mapping resource is available (§5.1;
   D19). The probe IDs are known from the raw file.
4. Coverage counts for §9.3 categories 1–2 (annotation and presence in each Series Matrix): probe-ID
   lists only, once annotation is chosen.
5. Listing of the GSE63061 and GSE99039 samples falling under each R5 category (§4.3), from labels only.
6. Confirmation that every approved covariate is complete or quantifying its missingness per cohort
   (largely done: §9.6, §10.3).
7. Version inventory for §11.2 once an environment is approved.

### 14.2 Decisions requiring the PI's approval (evidence does not determine a unique answer)

| Decision | Why the evidence does not settle it |
|---|---|
| D1 Estimand | E2 is the only exactly supportable estimand, but whether a deposited-label estimand is scientifically acceptable for the question is a judgement |
| D4 Age | The papers' criterion conflicts with the deposited data; no source explains which is correct |
| D5 / D22 QC thresholds and review | No validated cutoff exists for these data; every k or classification boundary is a convention |
| D6 Annotation and multi-probe | Several defensible resources and probe rules exist, with different trade-offs |
| D7 Model | Fixed vs blocked chip and the single-group-chip threshold involve bias–variance trade-offs not determined by the data |
| D11 GSE140829 input | Series Matrix + batch vs ComBat both have known risks |
| D12 / D20 Replication | The question does not specify whether composite or per-gene replication is primary |
| D13 Specificity, δ and pooling | δ requires a scientific definition of a meaningful effect; pooling rules are clinical judgements |
| D14 / D21 Pathways and cell composition | Resource and method choices are conventions with known sensitivities |
| D15 / D17 Thresholds | FDR level, signature cap and filtering trade power against stringency |
| D16 Sensitivity set | Which assumptions matter most is a judgement; it must be fixed before results |
| D0 / D9 / D10 / D18 / D19 | Depend on information not yet available (Notion content, data owners, mapping resources) |

## 15. Approval gate (from [3A] §5)

No gate condition is satisfied by this draft:

- **Not satisfied:** G1, G2, G5, G7, G8.
- **Partially satisfied:** G3, G4, G6, G9.

v2 narrows specification gaps but approves nothing.
