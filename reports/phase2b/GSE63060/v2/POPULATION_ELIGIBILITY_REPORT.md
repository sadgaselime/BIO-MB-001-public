# BIO-MB-001 Phase 2B — GSE63060 sample-population eligibility (v2)

Status: **for review — no population chosen or frozen; the research question is unchanged.** v2
supersedes v1 (`../v1/POPULATION_ELIGIBILITY_REPORT.md`, kept unchanged) by adding evidence from the
original publication. No expression data were used; no differential-expression or other inferential
analysis was run.

Evidence labels: **VERIFIED** (confirmed directly in the publication text or local files),
**REPORTED** (stated by the publication or GEO, not independently reproduced), **INTERPRETATION**
(what the evidence suggests for this project), **UNRESOLVED**.

Contents of this directory:

- `sources/` — retrieved source copies (read-only), with URLs, retrieval times (UTC) and SHA-256 in
  `PROVENANCE.json`.
- `reproduce_crosschecks.py` — regenerates the two cross-check files from the local phenotype tables:
  `.venv/bin/python reports/phase2b/GSE63060/v2/reproduce_crosschecks.py`.
- `publication_vs_geo_crosscheck.csv` and `control64_reconstruction_check.json` — its outputs.

## 1. Sources

- VERIFIED: **the PMC link supplied with the task (PMC4592294) is the wrong article.** It resolves to
  an unrelated news item ("Second-hand smoke exposure higher for kids and teens"). It was not used.
- VERIFIED: the publication cited by GSE63060, GSE63061 and the SuperSeries GSE63063 is PubMed
  26343147, which NCBI resolves to **Sood S, Gallagher IJ, Lunnon K, et al. "A novel multi-tissue RNA
  diagnostic of healthy ageing relates to cognitive health status." *Genome Biology*
  2015;16:185**, PMCID PMC4561473, DOI 10.1186/s13059-015-0750-x, CC BY 4.0. The full text was
  retrieved from NCBI.
- VERIFIED: Additional file 1 (six tabs) was retrieved from the publisher, because the PMC file links
  returned HTML pages. Its phenodata tab covers only the age-classifier muscle, brain and skin
  datasets. **No supplement lists AddNeuroMed or GSE63060/GSE63061 sample IDs, exclusions or
  outliers.** Additional files 2–4 (a ULSAM table and two figures) were not retrieved, because their
  descriptions show no AddNeuroMed sample content.
- VERIFIED: the SuperSeries GSE63063 lists 717 samples (329 + 388) and defers its design to the
  SubSeries; it does not define the flag. The live GSE63060 and GSE63061 series records are
  byte-identical to the local snapshots used since Phase 1.
- Not consulted: the earlier AddNeuroMed papers the article cites for patient selection and design
  (Lunnon et al., J Alzheimers Dis 2012;30:685–710 and 2013;33:737–53; Lovestone et al., Ann N Y Acad
  Sci 2009;1180:36–46), and the publication behind the project brief's "outlier exclusion" lead.

## 2. What the publication states (REPORTED; Materials and methods case-control section, Results, Table 1)

1. **Purpose of the subset.** The blood analysis tested a muscle-derived *healthy-ageing gene score*,
   not AD markers found in this cohort. For the primary analysis, controls were matched so as to create
   the largest possible group with the same age and gender balance as the AD or MCI groups. The
   resulting case-control groups had a median age similar to the ULSAM reference cohort (~70 years).
   The authors state explicitly that the analysis used a **subset of the subjects deposited at GEO**.
2. **Counts.** 297 samples were used: batch 1 (GSE63060) Control 67, MCI 39, AD 49; batch 2
   (GSE63061) Control 72, MCI 30, AD 40. The authors add that retrospectively including the entire
   cohort (n = 717) did not alter the outcome of their analysis.
3. **Table 1** (an "age- and gender-balanced subset"). Batch 1: AD 49 (69.8 ± 4.4 y; 34F/15M);
   controls for the AD comparison **64** (70.2 ± 3.7; 41F/23M); controls for the MCI comparison 67
   (69.6 ± 4.2; 41F/26M); MCI 39. Batch 2: AD 40; controls 71; MCI **31**. Table 1 also gives MMSE and
   CDR-SOB, which are not in GEO.
4. **Results text.** 113 batch-1 subjects and 111 batch-2 subjects were ranked, consistent with
   49 + 64 and 40 + 71 for the AD comparisons. Age and gender were described as "precisely balanced
   (~70 years)".
5. **Matching rule.** No caliper, algorithm, age bound or sample list is given.
6. **The GEO flag.** The paper does **not** mention the GEO characteristic
   `included in case -control study`.
7. **Clinical criteria (whole cohort).** Exclusion of other neurological or psychiatric illness,
   unstable systemic illness or organ failure, and a geriatric depression score of 4/5 or more. AD was
   diagnosed by NINCDS-ADRDA and DSM-IV (possible or probable); MCI by Petersen amnestic-MCI criteria;
   all participants had MMSE, and controls and MCI also had CERAD. Selection and clinical details are
   referred to the earlier AddNeuroMed publications.
8. **Exclusions and outliers.** No array QC, outlier removal or participant-level exclusion is
   described for the AddNeuroMed blood data. Removal of technically defective chips is described only
   for the Affymetrix muscle datasets. MCI-to-AD conversion is not discussed.
9. **Preprocessing.** Blood was collected in PAXgene tubes; total RNA was amplified with the TotalPrep
   kit. Batch 1 was profiled on HT-12 v3 in a USA facility, batch 2 on HT-12 v4 in a UK facility.
   Expression data were "transformed using variance stabilization and then quantile normalized using
   the LUMI package in R". No probe or detection filtering is described.

## 3. Publication versus local GEO metadata (VERIFIED; `publication_vs_geo_crosscheck.csv`)

| | Paper | Local GEO, flag = "yes" | Agreement |
|---|---|---|---|
| GSE63060 Control / MCI / AD (Methods text) | 67 / 39 / 49 | 67 / 39 / 49 | exact |
| GSE63061 Control / MCI / AD (Methods text) | 72 / 30 / 40 | 72 / 30 / 40 | exact |
| Total used / whole cohort | 297 / 717 | 155 + 142 = 297 / 329 + 388 = 717 | exact |
| GSE63060 controls (Table 1, MCI comparison), F/M | 67, 41/26 | 67, 41/26 | exact |
| GSE63060 AD, F/M | 49, 34/15 | 49, 34/15 | exact |
| GSE63060 MCI, F/M | 39, 24/15 | 39, 24/15 | exact |
| GSE63060 controls for the AD comparison (Table 1) | **64**, 41/23 | 67, 41/26 | **differs: 3 male controls not used** |
| GSE63061 controls (Table 1) | **71**, 44/27 | 72, 45/27 | **differs by one female** |
| GSE63061 MCI (Table 1) | **31**, 23/8 | 30, 22/8 | **differs by one female** |
| GSE63061 AD, F/M | 40, 23/17 | 40, 23/17 | exact |

- Mean ages agree to within 0.1 year (GEO 69.61 / 69.88 / 69.90 versus the paper's 69.6 / 69.8 /
  70.0 for GSE63060 controls / AD / MCI). The small differences are consistent with the paper using
  more precise ages than GEO's whole years (INTERPRETATION).
- **The 64 batch-1 controls cannot be identified from GEO.** Using GEO ages, none of the 2,600 ways
  of removing 3 male controls from the 67 reproduces Table 1's 70.2 ± 3.7; the highest achievable
  mean is 70.05 (`control64_reconstruction_check.json`).
- **The batch-2 Table 1 counts (71 / 31) conflict with the paper's own Methods text and with GEO
  (72 / 30)**, apparently through one female participant.
- **Overall GSE63060 counts** (VERIFIED, local): 145 AD, 104 controls, 80 MCI. Females: 99/145 AD
  (68%), 62/104 controls (60%). Mean age: AD 75.4, controls 72.4.

## 4. Meaning of the `included in case -control study` flag

- INTERPRETATION (strongly supported): **"yes" marks the samples used in the publication's primary
  age- and gender-matched case-control analysis.** All six group counts and the 297/717 totals match
  exactly; sex splits and age means match Table 1. The flag is not defined in either source; the link
  rests on this numerical correspondence.
- INTERPRETATION: the observed footprint from v1 (no "yes" sample over 75; 19 additional "no" samples
  across both batches) fits a matching-driven selection centred on ~70 years. It is **not** a
  documented eligibility rule: the paper states no age bound.
- UNRESOLVED: why all 37 GSE63060 AD participants with MCI-type participant codes are "no", including
  17 aged 75 or under. The paper is silent on MCI-to-AD conversion; matching alone does not obviously
  explain excluding every one of them.
- UNRESOLVED: exactly which samples formed the batch-1 AD-comparison control group (64), and which
  batch-2 participant moves between the control and MCI counts.

## 5. Preprocessing: publication versus files (links to Phase 2A)

- REPORTED: variance-stabilizing transformation, then quantile normalization, in lumi.
- VERIFIED (Phase 2A and this phase): the values are on a log-like scale with a common floor and
  ceiling; each sample is a strictly rank-preserving function of its non-normalized signals; and the
  sorted sample profiles are nearly, but not exactly, identical (maximum deviation 0.0067).
- VERIFIED (this phase): the deposited values are **not** reproduced by a single quantile
  normalization of the 330 deposited arrays. Values at the same rank differ across samples whether the
  rank is taken within the 38,323 retained probes (maximum spread 0.0067) or within all 48,803 probes
  (maximum 0.056).
- INTERPRETATION: the published description fits the data in kind (variance-stabilized,
  quantile-type). The exact procedure — the set of arrays normalized together, the order of probe
  filtering, any additional steps — differs from a plain quantile normalization of the deposited data.
  The probe filter that removed 10,480 low-signal probes is not described in the paper (UNRESOLVED).
- Implication (unchanged): treat the Series Matrix as submitter-processed, already normalized data,
  and do not normalize it again.

## 6. Reproducing the paper versus choosing our population

- **Reproducing the paper** means recovering the populations its authors used for *their* hypothesis:
  a healthy-ageing score benchmarked against an external ~70-year reference cohort, with
  matching-based confounding control. Their selection is study-specific, its algorithm is
  undocumented, and it cannot be fully reconstructed (the 64 controls).
- **Our study** asks whether AD-associated blood transcriptomic features replicate across cohorts and
  how specific they are to AD. Our population should be defined by prespecified, documented criteria,
  applicable in the same way to every cohort (GSE63061, GSE140829, GSE99039) using fields those
  cohorts record, and chosen without reference to expression results.
- The flag is a record of **another study's design choice**, not a statement about who is eligible as
  an AD case or control. Reusing it would inherit a selection made for a different question, a
  different reference cohort and an unspecified matching procedure.

## 7. Population options (assessment only; no choice made)

| Option | GSE63060 n (AD/HC) | Evidence-based strengths | Evidence-based weaknesses |
|---|---|---|---|
| A. All GEO AD and controls | 145 / 104 | Fully specified by GEO diagnosis; the same rule can be applied to every cohort; every sample met AddNeuroMed's clinical criteria; the original authors report that using the whole cohort did not change their conclusion (for their score) | AD older (75.4 vs 72.4) and more often female (68% vs 60%), so age and sex handling must be prespecified; includes 37 AD participants with MCI-type codes whose blood-draw timing is unknown |
| B. Flagged subset | 49 / 67 | Now traceable to the publication's matched set (counts verified); age and sex balanced by design | Matching built for another hypothesis and reference cohort; algorithm undocumented; the paper's own AD comparison used 64 controls, which cannot be identified; batch-2 Table 1 conflicts with Methods and GEO; unexplained exclusion of all MCI-coded AD; no equivalent in GSE140829 or GSE99039 |
| C. Explicit criteria (age 75 or under; code group consistent with diagnosis) | 51 / 69 | Reproducible from recorded fields; close to B | The publication states neither rule, so both criteria are reverse-engineered from B's footprint and have no protocol basis; the code-letter meaning is inferred |
| D. Defer | — | The remaining uncertainty is specific and checkable | Further sources must be consulted; the decision still has to be written into a statistical analysis plan |

Considerations that apply to any option:

- AD case definition: whether to include MCI-coded AD participants, which depends on blood-draw timing.
- Prespecified handling of age and sex: restriction, matching or adjustment.
- Whether a "reproduce-the-paper" analysis on population B is wanted as a separate, clearly labelled
  secondary analysis.

## 8. Unresolved

1. The meaning of the participant-code letters, and the blood-draw timing for the 37 MCI-coded AD
   participants. Possible sources: Lovestone et al. 2009; Lunnon et al. 2012/2013.
2. The membership of the paper's 64 batch-1 AD-comparison controls, and the batch-2 control/MCI
   discrepancy (Table 1 versus Methods and GEO).
3. The matching algorithm and any unstated age bound.
4. The exact normalization set or order, and the probe-filter rule.
5. The source and sample IDs of the "published outlier exclusions" and "sample-ID mismatch" leads in
   the project brief. Neither is described in this publication.
6. There is still no written statistical analysis plan in which to record the eventual decision.

## 9. Changes from v1

- **The publication was checked.** v1's recommendation to defer was conditional on this; it is now
  done, and the flag's role is established (section 4) apart from the noted discrepancies.
- **v1's hypothesis is confirmed:** "yes" marks the paper's case-control subset.
- **v1's observed rules ("75 or under", "code concordant") are re-characterised:** they describe the
  outcome of a matching procedure, not documented eligibility criteria.
- **New findings:** the 64-control discrepancy, the batch-2 Table 1 inconsistency, the absence of any
  stated outlier exclusions in the paper, and the preprocessing check in section 5.
- **No population is chosen in v2.**
