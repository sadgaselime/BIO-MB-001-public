# BIO-MB-001 Phase 3A — GSE63060 population eligibility decision framework (v1)

Status: **decision framework only — no population is chosen, frozen, relabelled or excluded.** No
expression values were analysed for this document. No differential-expression, pathway,
feature-selection, machine-learning or confirmatory statistics. The approved research question is
unchanged.

Labels used throughout: **VERIFIED** (confirmed in local files or source text), **REPORTED** (stated in
a publication or GEO record, not reproduced), **INTERPRETATION**, **UNRESOLVED**, and
**PROPOSED (no source)** for rules this document suggests without an existing source behind them.

## 0. Evidence base

| Ref | Document / file | Used for |
|---|---|---|
| [2A] | `reports/phase2a/GSE63060/v1/ADJUDICATION_REPORT.md` §1–9 | Input file choice, processing, extra array, empty-header columns |
| [2B] | `reports/phase2b/GSE63060/v2/POPULATION_ELIGIBILITY_REPORT.md` §2–8 | Sood et al. 2015 subset, flag meaning, 64-control discrepancy |
| [2C] | `reports/phase2c/GSE63060/v2/SAMPLE_IDENTITY_AND_COHORT_HISTORY_REPORT.md` §2–7 | Lunnon 2012/2013: blood timing, converters, original QC, under-65 contradiction |
| [2D] | `reports/phase2d/GSE63060/v1/SUPPLEMENTARY_SAMPLE_IDENTITY_REPORT.md` §1–4 | Supplements unobtainable and, as described, not sample-level |
| [P1] | `data/processed/GSE63060/phenotype_table.tsv` (derived from GEO GSM records); `reports/dataset_audit/GSE63060/` | Field availability and counts |
| [PA] | `reports/phase2a/GSE63060/v1/probe_annotation_provisional_bgx2008.tsv`; `adjudication_summary.json` | QC probe availability; absence of detection p-values |
| [CFG] | `config/datasets.yaml` | Cohort roles and independence status |
| Papers | Sood et al., *Genome Biol* 2015 (Methods, Table 1); Lunnon et al., *J Alzheimers Dis* 2012 (p.687–688, Table 1); Lunnon et al., *J Alzheimers Dis* 2013 (p.739–741, Table 1) | Reported procedures, as cited in [2B]/[2C] |

**Statistical plan:** no statistical analysis plan exists in the project (VERIFIED: a search for plan,
SAP, protocol and estimand files and text found only earlier reports noting its absence, [2B] §8 item
6). This document therefore cannot be checked against a plan; section 7 lists what a future plan must
contain.

## 1. Facts this framework relies on

| # | Fact | Status | Source |
|---|---|---|---|
| F1 | Candidate input is the Series Matrix: 329 samples, 38,323 probes, 1:1 with GEO records; values identical to the normalized file; already normalized (do not re-normalize) | VERIFIED | [2A] §2, §9 |
| F2 | GEO labels: AD 145, CTL 104, MCI 80; every label maps; no missing or ambiguous diagnoses in GSE63060 | VERIFIED | [P1]; [2B] §3 |
| F3 | 329 distinct participant codes, GSM accessions and array barcodes; 29 chips; age and sex recorded for all 329 | VERIFIED | [P1] |
| F4 | Blood was drawn at the first visit; converters were defined by AD diagnosis within 2 years after sampling and analysed by the original authors as MCI | REPORTED (Lunnon 2012 p.687–688; 2013 p.739) | [2C] §2 rows 2–3, §3.1 |
| F5 | GEO "AD" 145 (46M/99F) equals Lunnon 2013's AD 104 + MCIc 41 exactly; GEO controls equal the 2013 controls exactly | VERIFIED (aggregate) | [2C] §3.2 |
| F6 | About 41 GEO "AD" samples were MCI at blood draw; the 37 M-coded AD samples are likely among them | SUPPORTED, NOT PROVEN — no sample-level source | [2C] §4.1–4.2; [2D] §3 |
| F7 | Both papers state that participants under 65 were excluded; GEO has 21 such samples (AD 10, CTL 8, MCI 3) | VERIFIED contradiction, UNRESOLVED | [2C] §2 row 9; [P1] |
| F8 | The original QC (detection <80%, XIST sex discrepancy, RIN, comorbidity, reclassification) was applied before deposit; no sample IDs are published | REPORTED; IDs UNRESOLVED | [2C] §2 row 7 |
| F9 | No detection p-values were deposited; RIN is not in GEO | VERIFIED | [PA] `non_normalized_has_detection_pvalues=false`; [P1] fields |
| F10 | Sex-check probes are present: XIST (ILMN_1764573) and Y genes (RPS4Y1, DDX3Y, KDM5D/JARID1D, UTY, EIF1AY, USP9Y, ZFY, CYorf15A/B) | VERIFIED (presence only; no values examined) | [PA] |
| F11 | Flag "yes" (49 AD / 67 CTL) marks Sood et al.'s age- and sex-matched subset, built for a healthy-ageing score benchmarked to an external ~70-year cohort; matching algorithm undocumented; the paper's own AD comparison used 64 controls, which cannot be identified | INTERPRETATION strongly supported; 64-control identity UNRESOLVED | [2B] §2–4 |
| F12 | Supplements are unobtainable here and are described as gene, probe and MRI tables, not sample lists | VERIFIED (access) / INTERPRETATION (content) | [2D] §1–2 |
| F13 | Independence between GSE63060 and GSE63061/GSE140829 is UNRESOLVED; no shared identifiers were found, which does not prove independence | VERIFIED | [CFG]; Phase 1 `overlap_checks.json` |
| F14 | GSE140829 records `age_at_draw`; GSE63061 has 6 ambiguous or transition labels; no cohort records conversion status or blood-draw timing for individual samples | VERIFIED | [P1] for each cohort |

## 2. Candidate estimands

| Estimand | Definition | Can the metadata support it? | Inappropriate claims |
|---|---|---|---|
| E1. Diagnosis at blood draw | Transcriptomic differences between people who had AD when blood was collected and controls | **No, not exactly.** About 41 GEO "AD" samples were probably MCI at blood draw (F5–F6). They cannot be identified per sample: the code-letter meaning is undocumented and about 4 converters have no letter (F6) | Any claim that results reflect AD present at collection, unless the converters are identified from data-owner records |
| E2. Deposited label | Differences between samples deposited under the GEO "AD" label and deposited controls | **Yes**, fully: labels, ages and sexes are complete (F2–F3) | That all cases had AD at collection; that signals are prodromal or predictive; that the label is a validated diagnosis at sampling; any causal or clinical-biomarker claim |
| E3. Later-conversion-inclusive | Differences between a group comprising AD at collection plus MCI-to-AD converters within 2 years, and controls | **Partly.** The aggregate composition is well supported (F5), but per-sample membership is not; operationally it is identical to E2 in GSE63060 | That the group is homogeneous; separate estimates for converters vs prevalent AD; time-to-conversion interpretations |

INTERPRETATION: with current evidence, **E2 is the only estimand the metadata can support exactly**.
E3 describes what E2 most likely contains. E1 requires sample-level information that is not
available.

All estimands: blood-based associations only. No inference that signals originate in the brain, no
causal claims, and no claim of a clinically validated biomarker.

## 3. Options

### Option A — all GEO-labelled AD and controls (145 / 104)

- **Population:** every Series Matrix sample with `char:status` = AD or CTL; MCI is outside the primary
  contrast. Exact rule: status ∈ {AD, CTL}, with no further restriction unless QC rules are added.
- **Estimand:** E2. It can be described as E3 in aggregate, with stated uncertainty.
- **Evidence:** labels complete and 1:1 with the data (F1–F3). The original authors report that using
  the whole cohort did not alter their own conclusion, for a different score ([2B] §2.2).
- **Main risks:**
  1. Case heterogeneity: about 28% of cases were probably MCI at sampling (F6), which dilutes or mixes
     any AD-at-collection signal.
  2. Age and sex imbalance: AD mean age 75.4 vs 72.4, female 68% vs 60% ([2B] §3); this must be
     handled by prespecified adjustment or restriction.
  3. The 21 under-65 samples contradict the published criterion (F7).
  4. QC inherited from the submitters is unauditable (F8).
- **Do not:** relabel any sample, or assume any label is wrong.

### Option B — GEO-flagged subset (49 / 67)

- **Population:** `char:included in case -control study` = yes, among AD and CTL.
- **Documented purpose:** a matched subset for testing a muscle-derived healthy-ageing score against a
  ~70-year reference cohort (ULSAM). It is not an eligibility rule for AD case–control comparisons
  ([2B] §2, §6).
- **Matching:** precisely balanced on age and sex (Table 1 matches GEO within 0.1 years; [2B] §3).
  Algorithm, caliper and age bound are undocumented.
- **Why matching counts is not enough:** reproducing 49/67 confirms which samples carry the flag, not
  that the selection suits our question.
  - The paper's own AD comparison used 64 controls, which cannot be identified ([2B] §3).
  - All MCI-coded AD (37) are excluded for reasons the paper does not state ([2B] §4).
  - The flag exists only in the AddNeuroMed cohorts, so the rule cannot be applied to GSE140829 or
    GSE99039 (F14).
- **Implied estimand:** E2 restricted to an age-matched window. It probably excludes most converters,
  which brings it closer to E1, but that is not documented (F6). The subset is neither independent nor
  demonstrably unbiased.
- **Suitability:** not suitable as the primary population on current evidence. Possible as a clearly
  labelled secondary "reproduce Sood et al." analysis, if wanted.

### Option C — explicit, prespecified eligibility criteria

No sample list or final counts are produced here. Each rule must be approved before it is applied, and
applied before any outcome analysis.

| Rule | Proposal | Rationale | Supporting source | Information available locally? | Unknown / caveat |
|---|---|---|---|---|---|
| C1 Input | Use the GEO Series Matrix only; samples are its 329 GSM columns | Exact GEO linkage, no malformed rows, no unlabelled array | [2A] §2, §9 | Yes | Submitter preprocessing parameters undocumented ([2A] §6) |
| C2 Identity | Require a unique GSM, unique participant code, unique array barcode, and non-missing age and sex | Auditable sample identity; avoids duplicates | Phase 1 reconciliation; [P1] | Yes (all 329 qualify; VERIFIED) | — |
| C3 Diagnosis | Case = `char:status` "AD"; control = "CTL"; MCI excluded from the primary contrast (not from the dataset) | Uses the only diagnostic field present | GEO records [P1] | Yes | The label's timing is unknown for about 41 cases (F6), so this implements E2, not E1 |
| C4 Missing / ambiguous / conflicting labels | Exclude from case–control analyses any sample whose diagnosis is missing, ambiguous, transitional or conflicting; record each in an exclusion log | Consistent cross-cohort handling | **PROPOSED (no source)**; Phase 1 diagnosis-status framework | Yes. GSE63060 has none (F2); GSE63061 has 6 (F14) | — |
| C5 Converter status | **No converter-based rule in the primary population**; record "conversion status unknown" | Conversion cannot be established from evidence at blood draw; code letters are undocumented | [2C] §4; [2D] §3 | **No** | Requires data-owner records. A code-letter sensitivity analysis is possible only if explicitly labelled as resting on an undocumented convention |
| C6 Age | Choose and prespecify one of: (a) no restriction, age as covariate; (b) restrict to ≥65 per the papers' stated criterion; (c) restrict to an age range shared across cohorts | (b) follows the papers' text but contradicts the deposit (F7); (a)/(c) avoid relying on an unexplained discrepancy | Lunnon 2012 p.687; 2013 p.739 for (b); **PROPOSED (no source)** for (a)/(c) | Yes (ages recorded for all) | Why 21 participants under 65 were deposited (F7) |
| C7 Sex check | Flag samples whose expression-based sex (XIST and Y-gene probes) disagrees with recorded sex. Decision rule, thresholds and handling to be prespecified; exclusions logged by GSM | Original authors and Patel et al. both used sex checks; mismatches indicate possible sample mix-ups | Lunnon 2012/2013 (XIST; [2C] §2 row 8); Patel 2020 ([2C] v1 §2.3) | Probes yes (F10); thresholds **PROPOSED (no source)** | Results depend on method (the original XIST check was already applied, yet Patel found 2 more); computed blind to diagnosis |
| C8 Detection rate | Not implementable; record the submitters' pre-deposit QC as inherited | Detection p-values not deposited | F9; Lunnon 2012 p.688 | **No** | Cannot be audited |
| C9 RIN | Not implementable; record the pre-deposit RIN ≥7 criterion as inherited | RIN not in GEO | F8–F9 | **No** | Cannot be audited |
| C10 Array outliers | A prespecified, label-blind outlier rule (for example inter-array correlation or distance thresholds on all probes), with a sensitivity analysis including the flagged arrays | Our own reproducible QC; Patel's 10 outliers are unidentifiable | **PROPOSED (no source)**; Patel 2020 as precedent only | Yes, data available | Threshold choice is a researcher degree of freedom; must be fixed before any case–control results are seen |
| C11 Batch / site covariates | Chip (from barcode title) and site (code prefix) as adjustment covariates, not eligibility criteria | Technical and site structure | [P1]; [2C] §4.3 (site prefixes supported, not proven) | Chip yes; site supported, not proven | Site mapping undocumented |
| C12 No outcome-driven selection | Eligibility fixed and logged before any case–control expression comparison; no sample removed on the basis of association results | Prevents selection bias and leakage | Project principles | — | Requires a written statistical analysis plan |

INTERPRETATION: applied with C5 as written, Option C implements **E2 with transparent QC and
explicit age handling**. It cannot implement E1 without data-owner information.

### Option D — defer the population decision

Minimum evidence needed before freezing:

1. **Satisfiable now from GEO files:**
   - Written estimand (E2 or E3 wording).
   - Approved rules C1–C4, C6, C7, C10–C12, and their exclusion logs.
   - A written statistical analysis plan.
   - A documented discovery/validation role for each cohort (with independence recorded as unresolved).
2. **Needs the original data owners** (GEO submitters, AddNeuroMed/Dementia Case Register custodians):
   - Per-sample diagnosis at blood draw, or converter status, for the 145 "AD".
   - The definition of the participant-code letters.
   - The reason 21 participants under 65 were deposited.
   - The identity of the 3 extra MCI samples relative to Lunnon 2013.
   - Any participant overlap with GSE63061.
3. **May remain unresolved permanently:**
   - Identities of samples excluded by the submitters' and Patel et al.'s QC.
   - Sood et al.'s 64 controls and the GSE63061 Table 1 discrepancy.
   - Exact normalization parameters and the probe filter.

**Proceeding without the owner information:** the project can proceed with an explicitly limited,
cross-sectional E2 estimand, stating that the case group probably includes about 41 participants who
were MCI at blood draw. That would not support claims about AD present at collection or about
prediction of conversion.

## 4. Structured comparison (qualitative; no scores)

| Option | Target population and estimand | Exact eligibility rules required | Available evidence | Unresolved assumptions | Main bias / validity risks | Reproducibility | Suitability for primary analysis | Conditions before approval |
|---|---|---|---|---|---|---|---|---|
| A | All GEO AD vs CTL; E2 (E3 in aggregate) | status ∈ {AD, CTL}; plus any approved QC | Complete labels, ages and sexes; exact aggregate match to Lunnon 2013 | Labels as deposited are accepted; converter fraction known only in aggregate | Case heterogeneity (~28% probable converters); age and sex imbalance; under-65 contradiction; unauditable inherited QC | High: rule uses recorded fields only; transferable to other cohorts | Plausible for E2 with explicit limitations | Estimand written as E2; age/sex handling prespecified; QC (C7/C10) approved; limitations recorded |
| B | Sood et al. matched subset; E2 within ~58–75 years, probably fewer converters (undocumented) | flag = yes | Counts, sex and age match the paper; purpose documented | Undocumented matching algorithm; reasons for excluding MCI-coded AD; the paper's 64-control set | Selection designed for another hypothesis and reference cohort; inherited undocumented selection; small n; not applicable to other cohorts | Low for the selection logic; high for the flag lookup | Not suitable as primary on current evidence; possible secondary reproduction | Only as a labelled secondary analysis, if wanted |
| C | Explicit rules C1–C12; E2 with transparent QC | C1–C12 as approved | All inputs for C1–C4, C6, C7, C10, C11 exist locally | C5 cannot be implemented; site-prefix meaning; QC thresholds | Researcher degrees of freedom in QC thresholds (mitigated by prespecification); residual converter heterogeneity | High if prespecified and logged | Plausible for E2; cannot deliver E1 | Approval of each rule; SAP written; exclusion logs generated before outcome analysis |
| D | Not yet defined | — | Current reports 2A–2D | Whether data owners can supply sample-level timing | Delay; risk of indefinite deferral | — | — | Defined deadline or condition for ending the deferral |

## 5. Approval gate

| # | Condition | Status | Evidence |
|---|---|---|---|
| G1 | Estimand and case definition written clearly | **Not satisfied** | Section 2 compares estimands; none is approved |
| G2 | Inclusion and exclusion rules prespecified | **Not satisfied** | Option C rules are proposals, not approved |
| G3 | Source of each eligibility field documented | **Partially satisfied** | GEO fields documented ([P1]; [2B] §3; [2C] §2). Conversion status and code-letter meaning have no documented source |
| G4 | Ambiguous diagnoses handled consistently | **Partially satisfied** | GSE63060 has none (VERIFIED). GSE63061's 6 are flagged in Phase 1, but no cross-cohort rule is approved (C4 proposed) |
| G5 | QC reproducible and independent of desired results | **Not satisfied** | Inherited QC is unauditable (F8–F9); C7/C10 not yet specified or run |
| G6 | Sample-level exclusions auditable | **Partially satisfied** | Phase 1 tooling (reconciliation CSVs, `proposed_exclusions.csv`) supports per-GSM logs. No exclusions applied yet; the submitters' and Patel's exclusions are not auditable |
| G7 | Discovery/validation relationship handled appropriately | **Not satisfied** | Independence of GSE63061 and GSE140829 UNRESOLVED (F13); the cross-cohort eligibility harmonisation (F14) is not written |
| G8 | Statistical plan consistent with the selected population | **Not satisfied** | No statistical analysis plan exists |
| G9 | Remaining limitations explicitly recorded | **Partially satisfied** | Recorded across reports 2A–2D and this document; not yet consolidated into an approved plan |

Nothing is marked satisfied merely because this framework describes it.

## 6. Recommended next action (not a population decision)

**Most defensible next action:** the PI decides the **estimand** first (E2, deposited label, is the only
one supportable exactly with current data). That decision is then recorded in a new statistical
analysis plan together with the Option C rule set, approved or modified rule by rule. In parallel, the
data owners are asked for sample-level diagnosis at blood draw.

The population choice itself (A, B, C or a defined deferral D) follows from those two steps and remains
open here.

**Smallest set of information that would materially change the decision:**

1. Per-sample diagnosis at blood draw, or converter status, for the 145 GEO "AD" samples. This would
   make E1 feasible.
2. The submitters' explanation of the 21 participants under 65.

Everything else in section 3 Option D items 2–3 refines the decision but does not change it.

**Mandatory before freezing:** G1, G2, G5, G7, G8 satisfied; G3, G4, G6, G9 completed.
**Optional improvements:**

- The code-letter sensitivity analysis, labelled as resting on an undocumented convention.
- A secondary Sood-reproduction analysis on Option B.
- A re-normalization sensitivity analysis from the non-normalized file ([2A] §9).
- Obtaining the supplements, which are unlikely to be sample-level ([2D] §2).

**Questions that can be closed:**

- Input file: the Series Matrix ([2A] §9), provisionally.
- Meaning of the GEO flag: the Sood et al. matched subset ([2B] §4).
- Whether the supplements are likely to identify samples: unlikely ([2D] §2).
- Whether Sood's 64 controls matter: they only matter if Option B is chosen.

**Questions that should remain open:** converter identities; the under-65 contradiction; the 80 vs 77
MCI and 329 vs 326 counts; code-letter meaning; cohort independence; the identities of samples removed
by the submitters' and Patel's QC.

## 7. Where a future statistical analysis plan will need content (no plan is changed here)

- Estimand statement and case definition (G1).
- Eligibility rules and exclusion-log format (G2, G6).
- QC specification (C7, C10) with thresholds and sensitivity analyses (G5).
- Handling of age and sex: restriction, matching or adjustment (C6).
- Covariates (C11).
- Discovery/validation roles and cross-cohort harmonisation of diagnosis and age fields (G7; F14).
- Explicit limitation statements for E2 (section 2).
