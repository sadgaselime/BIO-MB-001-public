# BIO-MB-001 — Decisions required before SAP approval (brief)

**Purpose.** To make every still-unapproved decision understandable and answerable. This is **not** a
SAP revision. No decision is approved, preferred or settled here, and the approval-gate status is
unchanged (v7:5–8).

**Sources (read-only):**

| Short name | File | Notes |
|---|---|---|
| [v7] | `reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md` | Cited `v7:L` |
| [v7-REG] | The same file, §11 | **There is no separate v7 register file**; the v7 decision register is v7 §11 (v7:597–625) |
| [v7-XA] | The same file, §10 | **There is no separate v7 cross-section audit file**; it is v7 §10 (v7:557–593) |
| [FA] | `reports/phase3b/v6/FINAL_SAP_READINESS_AUDIT.md` | — |
| Retained active text | v6 (`v6:L`), v5 (`v5:L`) and earlier drafts | As mapped in v7 §0.1 (v7:53–84) |

**Conventions:**

- "Documented proposed default" means a choice that the source labels [PROPOSED]. It is reported as
  documented and is **not** a recommendation of this brief.
- Consequences are taken only from the documents.
- Where a document records reasoning rather than evidence, this brief says so.

---

## 1. Which decisions block what

**Rule [v7:102–103], as amended 2026-10-10.** Each decision is approved before the stage or analysis it governs: discovery decisions before the corresponding real-data QC or analysis; rules on selecting or using discovery results before those results are generated or inspected; cohort- and analysis-specific decisions before that cohort or analysis begins (v7:103, rules 1–3; table v7:105–112).
Deferring an analysis does not permit changing its rules after its results are seen (rule 4). The amendment approves no decision. **Note:** the "Blocks SAP start?" column of the table below was written under the pre-amendment rule; read it against the "Must be approved before" column of v7 §1 (v7:105–112).
"Enabling" items (D9, D10, D19) are not Tier A approvals. They block only
specific analyses or claims (v7:612–613, 622).

| Decision | Tier [v7-REG] | What it governs (scope) | Blocks SAP start? | Blocks only… |
|---|---|---|---|---|
| D0 | A1 | Governance: reconciliation with any other plan | **Yes** | — |
| D1, D2, D3, D4, D17, D18 | A2 | Estimand, population, input, age, features, identity | **Yes** | — |
| D5 + D22 | A3 | QC (R8/R9) and the population | **Yes** | — |
| D7 | A4 | Estimability thresholds; assumption rule; every model | **Yes** | — |
| D6 | A5 | Gene-level unit: discovery gene-level claims, signature, validation, specificity, pathways | **Yes** (approval timing) | — |
| D15 | A5 | Discovery FDR level, signature cap, coverage | **Yes** | — |
| D20, D12 | A5 | Replication claims (validation) | Yes (approval timing) | Validation claims |
| D11 | A5 | GSE140829 input and S13 | Yes (approval timing) | GSE140829 replication and S13 |
| D13 | A5 | Specificity (GSE99039) | Yes (approval timing) | Specificity analyses and claims |
| D14 | A5 | Exploratory pathways | Yes (approval timing) | Pathway analysis |
| D16 | A5 | The sensitivity set | Yes (approval timing) | Sensitivity analyses |
| D21 | A5 "(if S11)" (v7:111, 624) | S11 only | Only if S11 is retained | S11 |
| D8 | A6 | The software environment | **Yes** (no computation without it) | — |
| D9 | Enabling | E1, the S4 interpretation, D18 pairing | No | E1; S4 interpretation; D18 pairing |
| D10 | Enabling | The "independent" wording for GSE140829 | No | That wording |
| D19 | Enabling | GSE140829 probe mapping | No | **All GSE140829 analyses** (v6:486, 497–498) |

---

## 2. Decisions

Every entry is **Unapproved**, except D0, which is approved as a governance designation only (not approval of the SAP), and D1, D2, D3, D4 and D5, and D18, which is partially approved (D-3/D-4 handling only), and D22, which is partially approved (R8 variant V-A and §3.5 QC policy rows 1–6 only), and D6, which is partially approved (gene-level option G3, S8 alternative G1, freezing rule, gene-history cutoff, gene-history procedure, GPL570 mapping and the D6-G Illumina annotation policy for GSE63060/GSE63061 (Option A0) only), and D17 (Option A), and the D18 D-1u ruling, GSE99039 title rule, R-rep1 rule and precedence rule (§5.2), and the D22 exclusion-list approval scope (policy only), and the D18 D-2 option (c), and the D18 D-1 handling and review workflow/log, and the QC Stage A ruling (GSE63060: compute and record candidate exclusions only), and the H1 analysis specification, D7, D15, D16 (with S-R8m) and the R8 review outcome, and the GSE63060 exclusion list (approved as rule-applied), and D12, D13 (conservative) and D20, and the GSE63061 application of D2/C1 and its QC ruling, and D8, which is approved for environment readiness only (D8-8; no real-data execution authorized) (explicit PI approvals recorded 2026-10-10; D22 partial approvals 2026-10-11; D6 partial approvals 2026-10-12 and 2026-10-13; D0 2026-10-14; D17, the D18 rulings above and D22 scope 2026-10-15; D-2 option (c) 2026-10-15; D6-G 2026-10-17; D8-8, D18 D-1 handling/workflow, the QC Stage A ruling, H1 specification, D7, D15, D16, the R8 outcome and the GSE63060 exclusion list 2026-10-18; D12, D13, D20 and the GSE63061 go-ahead, the GSE63061 exclusion list and the GSE63061 descriptive methods, the D8 glmnet amendment, the ML protocol, D19-1, D11 option (a), D10 wording, the GSE140829 eligibility rules and the GSE140829 C1 review 2026-10-19; see each entry). Register dependencies ("Depends on", v7 §11) are read under the C1 ruling of 2026-10-15 (v7:599): interaction in content or execution, not an approval prerequisite unless a row states otherwise.

### D0 — Reconciliation with any other analysis plan · A1 · blocks the whole SAP

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-14 (explicit PI instruction) as a governance designation only** — SAP v7 is the governing statistical analysis document; nine Notion planning pages, reviewed read-only on 2026-10-14, are retained as context (v7:603). This is not approval of the SAP, which remains not approved and not frozen (v7:3); the conflicts listed at v7:603 remain open |
| Question in plain language | Is there another plan (e.g. in Notion) that v7 must agree with? |
| Documented options | Provide the content; or provide a statement ([FA] §9, line 529: "Provide the content or a statement") |
| Consequences | Without reconciliation, two protocols may conflict ([REG] D0, assessment) |
| Cannot be claimed | That v7 is the sole prespecified protocol |
| **PI question** | *Answered 2026-10-14: other planning documents exist in Notion but do not govern; v7 governs and the Notion pages are retained as context (v7:603). Still open: the conflicts listed at v7:603, each by its own decision.* |

### D1 — Primary estimand · A2 · whole SAP

| Field | Content |
|---|---|
| Status | **Approved 2026-10-10 by explicit PI instruction: E2** (GEO-deposited labels: GSE63060 "AD" vs "CTL" in GEO `status`). Conditions: about 41 of the 145 "AD" samples were probably MCI at blood collection (a group-level inference, not verified individually; identities not known), so the estimand concerns deposited AD labels, not confirmed AD at blood collection. S4 is a labelled sensitivity only and is never equivalent to E1. E1 may be considered only if sample-level evidence becomes available and E1 is separately prespecified. The 41 vs 42 converter discrepancy remains unresolved. This approves nothing else (v7:604). Previously: unapproved, with proposed default E2 |
| Question | Compare the GEO-deposited diagnosis labels (AD vs control), or diagnosis at blood draw? |
| Options | **E2** (deposited label); **E1 via D9** (v7:604) |
| Consequences | **E2:** the only estimand supported by the deposited data. "AD" includes about 41 likely MCI-to-AD converters (H1; v5:96). **E1:** requires per-sample diagnosis at draw from the data owners (D9); not available locally |
| Cannot be claimed | **Under E2:** that effects describe AD as diagnosed at blood draw. **Under E1:** nothing, until D9 data exist |
| **PI question** | *Do you approve the deposited-label estimand E2, with the converter caveat, as the primary estimand?* (Answered 2026-10-18: H1 analysis specification approved — age linear, recorded sex and chip; limma moderated t, trend = TRUE; BH within the gene-level family at q < 0.05; v7:604.) |

### D2 — Eligibility and label rules · A2 · whole SAP

| Field | Content |
|---|---|
| Status | **Approved 2026-10-10 by explicit PI instruction:** the GSE63060 eligibility rule definitions R1, R2-ID, R2-COV, R3, R4, R5, R6, R10, R11, R12 and R13 (full wording at v7:605). Pre-QC contrast: 145 AD vs 104 CTL; the 80 MCI outside it. Not approved or fixed: R7 (D4), R8 (D5/D22), R9 criteria, duplicate handling (D18). No converter inference from code letters. Previously: unapproved, "As v5" |
| Question | Which arrays and labels are eligible (R1–R13, R2-ID/R2-COV, R5)? |
| Options | Approve as written; no alternative is listed in [v7-REG] |
| Consequences | Defines Base (v7:362) and Tier P (v7:351) |
| Cannot be claimed | Results for labels excluded by R5 (ambiguous or transition labels) |
| **PI question** | *Do you approve eligibility rules R1–R13, R2-ID/R2-COV and R5 as written?* (Answered 2026-10-19: the D2 rules are also applied to GSE63061 as written, with its own files; R5 excludes its 6 R5-category labels; v7:605.) |

### D3 — GSE63060 expression input · A2 · whole SAP

| Field | Content |
|---|---|
| Status | **Approved 2026-10-10 by explicit PI instruction:** `data/raw/GSE63060/GSE63060_series_matrix.txt.gz` (329 GSM × 38,323 probes) as the primary input, used as deposited without additional normalization or transformation (full conditions and limitations at v7:606). S10 re-normalization remains a sensitivity only, subject to D16, and is not approved by D3. Previously: unapproved, proposed "Series Matrix" |
| Options | Series Matrix (primary); S10 re-normalization is a sensitivity only (v7:606) |
| Consequences | The Series Matrix values are normalized by the submitters; S10 is family B (v7:229) |
| Cannot be claimed | Under S10: selection independence (v7:229) |
| **PI question** | *Do you approve the GSE63060 Series Matrix, without re-normalization, as the primary input?* |

### D4 — Age eligibility and covariate form · A2 · whole SAP

| Field | Content |
|---|---|
| Status | **Approved 2026-10-10 by explicit PI instruction:** no age-based exclusion in the primary GSE63060 AD vs CTL contrast (145 AD / 104 CTL before QC; the 21 under-65 samples retained); GEO `char:age` as a linear covariate. The papers-vs-GEO under-65 discrepancy is unresolved and the meaning of the age field is unverified (full wording at v7:607). S1(a) ≥ 65 (135/96), S1(b) 61–88 (141/99) and S2 spline remain sensitivities subject to D16. Previously: unapproved, "No restriction; linear age" |
| Options | No restriction; **≥ 65**; age as a **spline** (v7:607; the spline is S2) |
| Consequences | **≥ 65** follows the original papers but excludes 21 samples with an unexplained discrepancy (H2; v2:575). **No restriction** keeps them. The 61–88 range is sensitivity S1(b) |
| Cannot be claimed | **Without a restriction:** that the population matches the published inclusion criteria. **With ≥ 65:** that the 21 excluded samples are ineligible in fact (unexplained) |
| **PI question** | *Should the primary analysis restrict age (≥ 65), or include all ages? Should age be linear in the primary model?* |

### D5 + D22 — R8 sex check and QC policies · A3 · whole SAP (must be a permitted combination)

| Field | Content |
|---|---|
| Status | **D5: APPROVED 2026-10-10 (explicit PI instruction)**: option (b); D descriptive only; R8 and R9 conventions approved as unvalidated operational conventions (full wording at v7:608). **D22: PARTIALLY APPROVED — 2026-10-11 (explicit PI instruction)**: R8 variant V-A (R8 gates wherever assessable; gated analyses and QC Stage A scope per v7:139); §3.5 QC rows 1–5 (R8 two-axis discordant excluded, S5f re-includes; R8 single-axis discordant, ambiguous and unassessable retained; R9 flags retained under role (iii)); row 6 (numerical-failure arrays excluded, rule-based and listed, Tier P3, never lifted, not varied; detailed R9 failure rules, including Option C as a D22 median-level threshold distinct from the D5 pairwise tolerance, at v7:351). The exclusion-list approval scope was further approved 2026-10-15 (policy only; no exclusion list is approved). The precedence rule was approved 2026-10-15 under D18 (v7:621). D16 remains unapproved, and QC Stage A remains blocked (full wording at v7:625). D_min remains unresolved (no source; v7:633) but is not required under option (b). Previously: unapproved, "D_min unset; variant unset" QC Stage A ruling 2026-10-18 (explicit PI instruction, option A): for GSE63060, QC Stage A may compute and record candidate exclusions before D16; nothing is applied until the exclusion-list approval step and D16 are decided (v7:625). GSE63060 exclusion list approved 2026-10-18 as rule-applied (option (a)): 145 AD vs 60 CTL; v7:625. |
| Question | Should a sex-consistency check gate the analyses, and if so, how is "clear separation" defined? |
| D5 options (v7:130–135) | **(a)** D_min justified and approved; **(b)** no-threshold variant; **(c)** R8 not run; (u) unset (not permitted) |
| D22 options (v7:137–141) | **V-A** gate wherever assessable; **V-B** optional; **V-C** gate for discovery only |
| Permitted combinations (v7:143–148) | (a) or (b) with any variant; **(c) only with V-B**. (c)+V-A, (c)+V-C and anything with (u) are **not permitted** |
| Other D22 choices in active text | R8 ambiguous arrays: **retained (approved 2026-10-11)**; alternatives "exclude, or retain only" (v5:281) not chosen, and "retain only" remains undefined — listed in [v7-REG] D22 (‡; §4). Also the R9 role (role (iii) approved 2026-10-11) and the numerical-failure exclusion (approved 2026-10-11, with the detailed rules at v7:351) (v5 §3.5; v7:625) |
| Consequences | **(a):** needs a source not in the project (v5:224–225). **(b):** a weaker safeguard (v5:226–228). **(c):** the only sex QC is the submitters' unauditable XIST check, for GSE63060 only (v5:230–233). **V-A:** maximum checking; GSE140829 and GSE99039 may become "not assessable — blocked by R8 dependency" (v7:158–163). **V-B:** everything proceeds, labelled "sex consistency not verified" where R8 is not informative (v7:175–176). **V-C:** discovery waits; downstream cohorts proceed with the label |
| Cannot be claimed | Under (c) or V-B without informative R8: that sample sex was verified. Under any option: that R8 thresholds are externally validated (v5:131–133) |
| **PI questions** | *(1)–(3) answered: D5 option (b) (2026-10-10); V-A and R8-ambiguous arrays retained (2026-10-11). Exclusion-list approval scope approved 2026-10-15 (policy only; approved text at v7:625, which adds that the list is approved after QC Stage B). Precedence rule approved 2026-10-15 under D18 (v7:621). Still open (v7:625): do you approve D16? Wording as selected 2026-10-14: "the PI explicitly approves the complete rule-applied exclusion list for each cohort, across all tiers and rules, before the population is linked to any expression model; approval is limited to verifying that the prespecified rules were applied correctly; approval of individual QC policy rows does not constitute approval of the list; any deviation requires a documented protocol amendment (v5:127–128)."* (Answered 2026-10-18: QC Stage A may compute and record candidate exclusions for GSE63060 before D16; nothing applied; v7:625.) (Answered 2026-10-18: R8 review outcome R0 + R3 approved — R8 not amended; D9 query; S-R8m; v7:625.) (Answered 2026-10-18: GSE63060 exclusion list approved as rule-applied; v7:625.) (Answered 2026-10-19: GSE63061 QC Stage A/B may compute and record candidates under the same policies; v7:625.) (Answered 2026-10-19: the GSE63061 exclusion list is approved as rule-applied; 139 AD vs 133 CTL; v7:625.) |

### D6 — Gene-level unit · A5 · whole SAP (approval timing); governs all gene-level work

| Field | Content |
|---|---|
| Status | **PARTIALLY APPROVED — 2026-10-12 (explicit PI instruction)**: G3 is the primary gene-level option (average probe signal; opposing probe effects can cancel; no feature-filter rule introduced); G1 is the S8 alternative (S8 blocked until D16 is approved); the freezing rule as stated in v7 §3.2 (v7:191–204) and the selection sets at v6 §6.2 (v6:327–328) are approved, and the alternatives at v6:367–371 are rejected. Annotation-resource verification is authorized; no annotation resource, release, mapping rule or installation is approved, except the GPL570 mapping below. **Gene-history cutoff approved 2026-10-13:** only NCBI Gene-history entries dated on or before 20260318 may be applied to the primary mapping; later entries remain visible as timing discrepancies and must not alter the frozen primary mapping. **GPL570 mapping (D6-F) approved 2026-10-13:** hgu133plus2.db 3.13.0 (probe-to-gene knowledge 2021-04-14), with Entrez IDs reconciled to org.Hs.eg.db 3.23.1 (2026-03-18) by the gene-history procedure, approved separately from the 20260318 cutoff; Illumina platforms not covered (full wording at v7:609). **D6-G approved 2026-10-17:** Illumina annotation policy Option A0 for GSE63060 (illuminaHumanv3.db 1.26.0) and GSE63061 (illuminaHumanv4.db 1.26.0): package probes-table mapping without gene-history reconciliation; probes with more than one package Entrez ID excluded; discordant probes retained under the package mapping, flagged and listed; accession_unmatched and ambiguous categories reported separately; accession-only probes not added. The existing illumina_option_a/v1 tables and counts use gene-history reconciliation and are not the final A0 classification; the final A0 classification was generated and verified 2026-10-17 under separate authorization (reports/annotation_audit/illumina_a0/v1); annotation pin created 2026-10-18 (reports/annotation_audit/annotation_pin/v1); package installation remains pending (D8 approved for environment readiness only, 2026-10-18); GSE140829 remains under D19 (full wording at v7:609). Previously: unapproved, "None declared" |
| Question | How should one value per gene be formed from several probes? |
| Options (v6:325–330, retained) | **G1** highest-mean probe over a fixed selection set; **G1b** highest mean over MCI arrays; **G2** annotation-only rule; **G3** mean of the eligible probes. **Selection alternatives** (v6:367–371): re-select per model; re-select per GSE99039 contrast; IPD ∪ CONTROL only for GSE99039 |
| Consequences | **G1:** primary results are conditional on assumptions S-1 to S-5, which are unverified (v7:208–216, 240). **G1b:** undefined for GSE99039 (v6:328; v7:641). **G2:** needs a probe-quality resource and a GPL570 rule — external (v6:329). **G3:** no selection, but the estimand is "average probe signal", and constituent probes differ across platforms (v5:443, 450–451). **Re-selection alternatives:** units change across analyses (v6:369) |
| Cannot be claimed | **G1/G1b:** unconditional inferential validity (v7:189). **G3:** claims about a specific probe. **Any option:** that expression-based QC selection is independent of the tests (v7:234–236). Family B results are sensitivity-only (v7:229) |
| **PI question** | *Answered: G3 primary, S8 = G1, freezing rule and selection sets (2026-10-12); GPL570 mapping (2026-10-13). Illumina platforms GSE63060 and GSE63061 answered 2026-10-17: D6-G, Option A0 (v7:609). Still open: the GSE140829 annotation (D19); package installation (annotation pin created 2026-10-18, Tier B step 2; D8 approved for environment readiness only, 2026-10-18). The final A0 classification was generated and verified 2026-10-17 (v7:609).* |

### D7 — Estimability thresholds and assumption rule · A4 · whole SAP

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-18 (explicit PI instruction):** c₁ = 3 (minimum mixed units — chips, or batches where no chip is recorded — containing both compared groups), c₂ = 5 (minimum arrays of each compared group on mixed units), c₃ = 10 (maximum VIF_g), common to all cohorts; with the proposed η = 10⁻⁸, scaling and rank tolerance (v5:324–326); conventions without a published source, fixed before any M-check output and without inspection of diagnosis by chip; assumption rule as proposed: diagnostics descriptive, no failure rule (§6.3). Approves no analysis by itself. Previously: Unapproved. **c₁–c₃ and their scope unset**; assumption rule proposed: diagnostics descriptive, no failure rule (v7:610, 443–454) |
| Question | How much within-chip/batch information is required before the AD–control comparison is fitted? Should any diagnostic be allowed to change the model? |
| Options | Values of c₁ (mixed units), c₂ (each group on mixed units) and c₃ (maximum VIF); common or cohort-specific scope (v6:283–290); c₂ as a minority count; a residual-df check (v6:299–300); a prespecified failure criterion with a fixed alternative model (v7:451–453) |
| Consequences | Without c₁–c₃, Tier A4 is incomplete and no model runs. c₂ as defined can be met by unbalanced mixed units ([FA] F15). The no-failure-rule default fixes the models at Tier A; any alternative must be prespecified at A4 (v7:451–453) |
| Cannot be claimed | That passing the checks establishes scientific adequacy (v5:296–312) |
| **PI question** | *What are c₁, c₂ and c₃, and do they apply to all cohorts? Redefine c₂ or add a residual-df check? Accept "diagnostics are descriptive only", or specify a failure criterion and alternative model now?* (Answered 2026-10-18: c₁ = 3, c₂ = 5, c₃ = 10, common to all cohorts; diagnostics descriptive, no failure rule; v7:610.) |

### D8 — Software environment · A6 · whole SAP

| Field | Content |
|---|---|
| Status | **APPROVED FOR ENVIRONMENT READINESS ONLY — 2026-10-18 (D8-8, explicit PI instruction; v7:611).** Amended 2026-10-19 (explicit PI instruction): R glmnet 5.1 and its CRAN dependencies added to renv.lock for the approved exploratory ML protocol; existing pins unchanged (v7:611). Real-data execution remains prohibited until the applicable runner implements the code-identity lifecycle (capture, manifest, post-run verification) and passes its synthetic tests (v7:112); this is not approval of the SAP as a whole, the annotation pin, Tier B or any analysis. Before 2026-10-18 D8 was unapproved. The PI-authorized installation (R 4.6.1, Bioconductor 3.23, limma 3.68.5, renv 1.3.1, BiocManager 1.30.27, statmod 1.5.2, BiocVersion 3.23.1) was completed 2026-10-12 (reports/environment/D8_R_LIMMA_INSTALLATION.md, SHA-256 a5b3d2ff…); that record's phrase "the approved D8 environment" refers to this authorized installation, not to approval of D8. Python environment snapshot: reports/environment/python_lock/v1 (reviewed 2026-10-17); hash-pinned lock for CPython 3.13.9 on macOS arm64: reports/environment/python_lock/v2 (D8-2, 2026-10-18). Approval deferred 2026-10-15; approved for environment readiness only 2026-10-18 |
| Options | Pinned R/Bioconductor; a validated alternative (v7:611) |
| Consequences | No model, annotation pin or pathway analysis is possible without it. Software behaviour (camera statistic; estimated weights) is unverified until pinned (v7:643) |
| Cannot be claimed | Any result; any statement about software behaviour |
| **PI question** | *Installation of the PI-authorized versions was completed 2026-10-12 (v7:611; reports/environment/D8_R_LIMMA_INSTALLATION.md); installation does not approve D8. D8 scope defined 2026-10-17 (D3; v7:611). The conda explicit specification is recorded and the throwaway rebuild test was performed 2026-10-17 (results partial; reports/environment/d8_rebuild_test/2026-10-17). Decisions D8-1 to D8-6 were taken and implemented 2026-10-18 (reports/environment/d8_closure_review/2026-10-18/D8_EXECUTION_REPORT.md). Answered 2026-10-18: D8-8 approved for environment readiness only (v7:611). Still open: runner integration of the code-identity lifecycle before any real-data execution; reproducibility of analyses is not demonstrated.* |

### D11 — GSE140829 input · A5 · blocks GSE140829 replication and S13

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-19 (explicit PI instruction): option (a), Series Matrix + batch fixed effect (v7:614).** Previously: Unapproved. Series Matrix + batch; **S13 covariate and unit rule open** (v7:614, 267) |
| Options | Series Matrix + batch covariate; ComBat-corrected final file (v7:614) |
| Consequences | Historical v2 register (v2:582): "ComBat on diagnosis-imbalanced batches can distort effects; final file has 36 fewer samples". S13 is family B (v7:229) |
| Cannot be claimed | Under S13: selection independence. Under either: independence of GSE140829 from the discovery participants (D10) |
| **PI question** | *Is the GSE140829 Series Matrix with a batch covariate the replication input? For S13, should batch be included in the model of a ComBat-corrected file, and how are its features mapped?* (Answered 2026-10-19: Series Matrix + batch, option (a); features mapped under D19-1; S13 remains open; v7:614, 622.) |

### D12 — Replication criteria · A5 · blocks validation claims

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-19 (explicit PI instruction; the documented proposed default):** C-c and C-a as specified; C-b descriptive only (no inferential C-b). Approves no analysis by itself. Previously: Unapproved. C-c; C-a; C-b descriptive (v7:615) |
| Options | Keep C-b descriptive; or an inferential C-b via an approved procedure. The candidates P1–P3 are judged "none adequate as specified" (v6:569–573; v5:619–620) |
| Consequences | Descriptive C-b gives no p-value |
| Cannot be claimed | Under descriptive C-b: that direction agreement exceeds chance |
| **PI question** | *Should direction concordance (C-b) remain descriptive only?* (Answered 2026-10-19: yes, C-b descriptive; D12 approved as proposed; v7:615.) |

### D13 — Specificity in GSE99039 · A5 · blocks specificity analyses and claims

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-19 (explicit PI instruction; conservative specification):** "equivalence not used" (no δ; no negligible-association or AD-specificity claim, v7:494–499); no Q2 directional test; Holm across the three specificity contrasts (v6:647); the same coverage thresholds for GPL570 (v6:653); GENETIC_UNAFFECTED reported descriptively only; no replicated-genes-only add-on (v6:611); S15 as defined (complete case, no imputation). Approves no analysis by itself. Previously: Unapproved. **δ and its scale unset → no negligible-association or specificity conclusion** (v7:616, 494–499) |
| Question | How is association with PD tested, and what, if anything, would count as "negligible"? |
| Options | **Q2** directional test in addition to Q1 (v6:636; consequence at v7:519–524); **Holm across the three contrasts** (v6:647); GPL570 coverage thresholds (v6:653); **δ scale**: Δ-score, standardized score difference, per-gene log2, or relative to the AD effect (v7:528–533); δ value, or "equivalence not used" (v7:540). Also in retained text, now listed in [v7-REG] D13 (‡; §4): a replicated-genes-only add-on (v6:611) and the GU interpretation (v6:620); and S15 multiple imputation as a non-proposed alternative (v6:723) |
| Consequences | **Without δ:** only two-sided association tests, CIs and "association not demonstrated" (v7:501–509). **Q2 with Holm:** no AD-direction gain; opposite-direction detection tightens to p₁ ≤ 0.025 (v7:521–523). **Relative-to-AD scale:** conflicts with the magnitude prohibition unless a standardization is approved (v7:533) |
| Cannot be claimed | Without δ: that a PD association is negligible or that the signature is AD-specific (v7:494–499). Under any option: absence of association from non-significance (v7:513) |
| **PI questions** | *(1) Approve δ with a defined scale, or record "equivalence not used"? (2) Add Q2? (3) Holm across contrasts? (4) Same coverage thresholds for GPL570? (5) What does the GENETIC_UNAFFECTED label mean for interpretation? (6) Add a replicated-genes-only analysis?* (Answered 2026-10-19: (1) equivalence not used; (2) no Q2; (3) Holm across contrasts; (4) same GPL570 coverage thresholds; (5) GENETIC_UNAFFECTED descriptive only; (6) no replicated-genes-only add-on; v7:616.) |

### D14 — Pathways (exploratory) · A5 · blocks pathways only

| Field | Content |
|---|---|
| Status | Unapproved. "As v5 §9" (v7:617) |
| Options (v5 §9, retained) | Inter-gene correlation "estimated or fixed" (v5:709); collections and versions (v5:714). Now listed in [v7-REG] D14 (‡; §4) |
| Consequences | Gene-set results depend on the method and database version |
| Cannot be claimed | Confirmatory pathway conclusions; brain mechanisms (v5:715) |
| **PI question** | *Should inter-gene correlation be estimated or fixed, and which gene-set collections should be used?* |

### D15 — FDR level, signature cap and coverage · A5 · whole SAP (discovery and lock)

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-18 (explicit PI instruction):** q < 0.05; signature cap 200; per-direction coverage 50% and min(5); no coverage restriction at selection (conventions without a published source, v6:510). Approves no analysis by itself. Previously: Unapproved. q < 0.05; cap 200; per-direction coverage 50% and min(5) (v7:618) |
| Options | Other values (all are conventions; v6:510); a coverage restriction at selection (v6:431, alternative) — now listed in [v7-REG] D15 (‡; §4) |
| Consequences | These set the discovery claims and the signature's size |
| Cannot be claimed | That these values are empirically justified (labelled "no source"; v6:510) |
| **PI question** | *Do you approve q < 0.05, a 200-gene cap and the 50% / min(5) coverage rule, and no coverage restriction at selection?* (Answered 2026-10-18: approved as proposed; v7:618.) |

### D16 — Sensitivity set · A5 · blocks sensitivity analyses

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-18 (explicit PI instruction):** S1–S16 with the §5.3 sample sets, as defined; plus S-R8m (R8 review outcome R3, v7:625): the primary population with the 46 GSE63060 arrays whose two strongest Y markers both disagree with recorded sex removed (reports/qc_stage_a/GSE63060/r8_diagnostics/v2/r8_marker_calls_series_matrix.tsv). Anything the definitions leave open remains open; no sensitivity replaces the primary analysis; approves no analysis by itself. Previously: Unapproved. S1–S16 with the §5.3 sample sets (v7:619) |
| Options | Approve the set as defined (no alternative listed) |
| Consequences | Must be fixed before results (prespecification). Family B members are sensitivity-only (v7:229) |
| Cannot be claimed | That any sensitivity replaces the primary analysis (v7:406) |
| **PI question** | *Do you approve sensitivities S1–S16 with the sample sets of v7 §5.3?* (Answered 2026-10-18: approved, with S-R8m added; v7:619.) |

### D17 — Expression filters · A2 · whole SAP

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-15 (explicit PI instruction): Option A** (v7:620): no additional expression filter in the primary discovery analysis, with S7 (25th/50th percentile) as sensitivity. The D15 dependency is an interaction, not an approval prerequisite (C1, v7:599); D15 remains unapproved. S7 may not run until D16 is approved; no analysis is authorized. Previously: decision for review (user selection received 2026-10-13) |
| Options | No filter; S7 (25th/50th percentile) as a sensitivity (v7:620) |
| Consequences | Historical v2 register (v2:588): a filter reduces the testing burden but may remove low-expressed relevant genes |
| Cannot be claimed | — |
| **PI question** | *Answered 2026-10-15: Option A approved (v7:620). (The validation-cohort feature filter, v6 §8.2, v6:485, is a separate unresolved question.)* |

### D18 — Identity, duplicates and precedence · A2 · whole SAP

| Field | Content |
|---|---|
| Status | **PARTIALLY APPROVED — D-3/D-4 handling only, 2026-10-10 (explicit PI instruction):** option B (all D-3/D-4 arrays retained in the primary analysis unless another independently approved rule excludes them); S16 option 1 (every array in each qualifying cluster excluded in S16, no representative); label-discordant clusters retained in primary under deposited labels and excluded in S16 like other qualifying clusters; a qualifying cluster is a connected C2 cluster with at least one D-3 or D-4 pair (full wording at v7:621). Also approved 2026-10-15 (v7:621): the precedence rule (§5.2, as written), the GSE99039 title rule and R-rep1. D-2 option (c) approved 2026-10-15 (v7:621). D-1 handling and the review workflow/log approved 2026-10-18 (explicit PI instruction): the wording (i)–(v) in the Options row below, approved as written including item (iii) in full (v7:621). Still unresolved: the R2-ID scope; the designated project reviewer has not been named. D-1u ruling approved 2026-10-15 (v7:621). S16 may not run until D16 is approved; no analysis is authorized. Previously: unapproved, "Workflow and precedence proposed" |
| Options | Resolved 2026-10-10: reverse D-3/D-4 roles (option B) adopted; label-discordant clusters not excluded entirely. Resolved 2026-10-18: D-1 handling and review workflow/log (v7:621; v6:243–244). Resolved 2026-10-15: D-2 option (c) (v7:621). Resolved 2026-10-15: precedence rule (§5.2), GSE99039 title rule, R-rep1 (v7:621). Wording approved 2026-10-18 (explicit PI instruction), as written, including item (iii) in full (it supersedes the narrower 2026-10-15 scope of the D-1u ruling): (i) no participant-identifier field is designated for GSE63060 or GSE63061; the description codes are undocumented (v2:104; reports/phase2c/GSE63060/v2/SAMPLE_IDENTITY_AND_COHORT_HISTORY_REPORT.md:27, 41). (ii) D-1 applies only to a deposited replicate annotation naming its partner: keep one array (not labelled as a replicate, otherwise lowest GSM; v6:248), exclude and list the others (Tier P2); if the arrays carry different deposited diagnosis labels, exclude all of that participant's arrays from every contrast in that cohort in which any would otherwise be eligible, report the labels descriptively, and relabel nothing. (iii) Any other candidate link, including a shared description value, is D-1u: retained under deposited labels, flagged, listed and reported descriptively; sensitivity treatment deferred to D16. A non-unique GSM accession or array identifier remains an R2-ID identity failure; D2 is unchanged. (iv) The designated project reviewer receives the blinded table (v6:237); the log also records the reviewer's name, the review date and the rationale for the retained array. (v) §5.4's descriptive report extends to D-1 and D-1u. Resolved 2026-10-15 by the D-1u ruling (v7:621): a shared undocumented description value used as the participant code is D-1u, not an R2-ID exclusion; D2 is unchanged. The R2-ID scope (cohort-wide vs per contrast) is unresolved. |
| Consequences | Precedence: an array returns only if all its reasons are lifted (v7:364–367). The near-identical tolerance cannot detect re-hybridized duplicates (v6:269–271) |
| Cannot be claimed | That all duplicates were detected; the identity of GSE140829 replicate pairs (needs D9) |
| **PI question** | *Do you approve the duplicate workflow?* (Answered 2026-10-15: D-2 option (c) for GSE140829 "replicate 2"; v7:621.) (Answered 2026-10-15: precedence rule approved under D18; GSE99039 title rule and R-rep1 approved; v7:621.) (Answered 2026-10-10: label-discordant clusters are not excluded entirely; v7:621.) (Answered 2026-10-18: D-1 handling and review workflow/log approved, items (i)–(v); v7:621. Still open: the R2-ID scope and naming the designated reviewer.) (Answered 2026-10-19 for GSE140829: the PI is the designated reviewer; 583 "replicate 1" arrays D-1u retained and flagged; 4 "replicate 2" arrays Q3 under D-2 option (c); v7:621.) |

### D20 — Replication claims and error rates · A5 · blocks validation claims

| Field | Content |
|---|---|
| Status | **APPROVED 2026-10-19 (explicit PI instruction; the documented proposed default):** O1 (separate within-cohort families) + X1 (no cross-cohort claim); weighting W1; C-c one-sided with L_c; C-a at q < 0.05; covariates locked (§4.1); no cross-cohort score standardization. Approves no analysis by itself. Previously: Unapproved. Documented proposed default: O1 + X1; W1 (v7:623) |
| Question | What error rate should replication claims control, and may a claim span both validation cohorts? |
| Options | Within cohort: **O1** separate families; **O2** fixed-sequence gate; **O3** Holm per gene (v7:305–309). Across cohorts: **X1** no cross-cohort claim; **X2** "replicated in both"; **X3** "in at least one" (v7:313–317). Weighting **W1/W2** (v6:505–508). C-c sidedness: one-sided (default), "report only L_c", or two-sided (v6:538–540). "report only L_c" and the cross-cohort standardization (v6:591) now listed in [v7-REG] D20 (‡; §4) |
| Consequences | **O1:** per-cohort type I error for C-c and within-cohort FDR for C-a; **no combined control** (v7:297–299). **O2:** P(any claim) ≤ 0.05 under the cohort's global null; conditional FDR after gating not established (v7:308). **O3:** FWER per gene; lower power. **X2:** "replicated" wording for GSE63061 needs D10/D20 approval (v7:316). **X3:** FWER ≤ 0.05 for the two composite claims |
| Cannot be claimed | **O1:** familywise control over all replication claims. **X1:** any "both" or "either" statement. **Any option:** cross-cohort magnitude comparison (v6 §8.9); biological or clinical validation (v7:333) |
| **PI question** | *What error rate must replication claims control (choose O1, O2 or O3, and X1, X2 or X3)? W1 or W2? One-sided C-c with L_c, L_c only, or two-sided?* (Answered 2026-10-19: O1 + X1; W1; one-sided C-c with L_c; v7:623.) |

### D21 — Cell composition (S11) · A5 if S11 is retained · blocks S11 only

| Field | Content |
|---|---|
| Status | Unapproved. "Not proposed" (v7:624) |
| Options | Defer, or drop S11 ([FA] line 528) |
| Consequences | S11 is family B: its covariates are estimated from expression (v7:229) |
| Cannot be claimed | Under S11: selection independence |
| **PI question** | *Keep S11? If so, which deconvolution method and reference?* |

### Enabling items (not Tier A; they block specific analyses or claims)

| ID | Status | Missing | Blocks | **PI question** |
|---|---|---|---|---|
| D9 | Unapproved ("Request"; v7:612) | Data-owner information | E1; the S4 interpretation; D18 pairing | *Should the data owners be contacted?* |
| D10 | Unapproved ("Unverified"; v7:613) | Independence documentation | Any "independent" wording for GSE140829 | *Accept "independence unverified" wording?* (Answered 2026-10-19: yes; v7:613.) |
| D19 | Unapproved ("Approved resource"; v7:622) | An ILMN↔nuID mapping route | **All GSE140829 analyses** | *Which mapping route is authorized (package, GPL15988 table, or validated new code)?* (Answered 2026-10-19: D19-1, pinned illuminaHumanv4.db ExtraInfo nuID route with run-time cross-checks; v7:622.) |

---

## 3. Unresolved items that are not decisions (limitations)

These cannot be fixed by an approval:

- Inferential validity under S-1 to S-5 (unverified).
- Independence of expression-based QC selection.
- G1b for GSE99039.
- G2 for GPL570.
- The GPL570 sex probes.
- Software behaviour checks.

(v7:641, 643–644)

---

## 4. Cross-check of IDs and options (discrepancies marked UNRESOLVED)

All decision IDs D0–D22 appear in [v7-REG] (v7:603–625). D2 and D3 have no listed alternatives.

| # | Item | Finding | Status |
|---|---|---|---|
| 1 | "v7 decision register" and "v7 cross-section audit" | Not separate files; they are v7 §11 and §10 (v7:597, 557) | **Reconciled:** references are to v7 sections; no file change needed |
| 2 | D14 | [v7-REG] lists open options "—" (v7:617), but retained v5 §9 marks inter-gene correlation [DECISION NEEDED; D14] (v5:709) and leaves collections unpinned (v5:714) | **Reconciled:** both options added to v7 §11 D14 (‡) with source citations |
| 3 | D15 | [v7-REG] lists "—" (v7:618); retained v6:431 lists a coverage-restriction alternative under D15 | **Reconciled:** added to v7 §11 D15 (‡), with "other values" of the [PROPOSED] conventions (v6:422, 510) |
| 4 | D20 | [v7-REG] lists "two-sided C-c" but not "report only L_c" (v6:538) | **Reconciled:** added to v7 §11 D20 (‡). Also added: the cross-cohort standardization option in retained v6 §8.9 (v6:591; candidate not proposed, v6:601), which was likewise missing |
| 5 | D13 | [v7-REG] omits the replicated-genes-only add-on (v6:611) and the GU interpretation (v6:620) | **Reconciled:** both added to v7 §11 D13 (‡). Also added: S15 (v6:718) in the default, and S15 multiple imputation as a non-proposed alternative (v6:723) |
| 6 | D22 | [v7-REG] lists only V-A/V-B/V-C; the ambiguous-sex policy alternatives are in retained v5:281 | **Reconciled:** added to v7 §11 D22 (‡). The R9-role alternatives (i)/(ii) of v4 §2.3 are **not** active options: v4 §1–2 is superseded by v5 §3 (v5:77), which restates only role (iii) (v5:283) |
| 7 | D11 consequence text | Taken from the historical v2 register (v2:582), not from active v7 text | Cited as historical |

Items 2–6 were reconciled by editing only the option and default cells of v7 §11 (rows D13, D14, D15, D20, D22) and its legend line; no decision status changed. No option cited above was found absent from its source line. Each was checked against the quoted line
numbers.

---

## 5. Minimum answer set to complete Tier A

D0; D1; D2; D3; D4; D17; D18; **D5 + D22 (a permitted combination)**; **D7**; D6; D15; D20; D12;
D11; D13; D14; D16; D21 (or drop S11); D8.

The enabling items D9, D10 and D19 can follow, but D19 must be resolved before any GSE140829
analysis.
