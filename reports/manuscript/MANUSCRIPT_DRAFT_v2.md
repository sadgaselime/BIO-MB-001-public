# A reproducible blood transcriptomic signal of Alzheimer's disease is largely explained by leukocyte composition and does not transport to individual-level classification

**Sadga Selime**, Independent researcher. Correspondence: sadgaselime@gmail.com.

**DRAFT v2 (2026-10-21). Not for circulation.** Every number is taken from an accepted, code-identity-verified output
of BIO-MB-001; the source of each is listed in the Provenance appendix. All references were verified against PubMed, Crossref, the publisher or bioRxiv (2026-10-21). The
statistical analysis plan (SAP v7) is a proposed draft that is not frozen; the individual decisions it governs were approved
before each analysis, as recorded in its decision register.

---

## Abstract

**Background.** Blood transcriptomic signatures of Alzheimer's disease (AD) have been reported repeatedly. Their
reproducibility across cohorts, their specificity relative to other neurodegenerative diseases, and their usefulness for
classifying individuals remain uncertain [5,6].

**Methods.** We analysed four public whole-blood microarray datasets under a prespecified, decision-logged plan:
- **Discovery:** GSE63060 (AddNeuroMed).
- **Related-cohort consistency:** GSE63061 (AddNeuroMed; possible participant overlap).
- **Replication:** GSE140829 (independence from AddNeuroMed participants unverified).
- **Specificity:** GSE99039 (Parkinson's disease).

Before any modelling, samples were selected by rule-based eligibility and quality control: a two-axis sex-concordance check
and a robust outlier check, with every exclusion list approved as rule-applied. Differential expression used limma with
age, sex and chip/batch adjustment. A 200-gene signature was locked in the discovery cohort before any other cohort's
expression was modelled. We then tested:
- a composite score test of that signature, a per-gene test and direction agreement in each cohort;
- a two-sided specificity test against Parkinson's disease, Holm-corrected across three contrasts;
- a leakage-controlled ridge classifier, trained with nested, chip-grouped cross-validation in the discovery cohort and
  applied once, frozen, to the other cohorts.

Leukocyte composition was assessed with five marker-based indices: in the discovery cohort as a prespecified sensitivity
analysis whose method was chosen after the primary results, and in the external cohorts post hoc.

**Results.**
- **Discovery:** in GSE63060 (145 AD, 60 controls), 1,401 of 17,425 genes were associated with AD at FDR < 0.05
  (739 lower, 662 higher in AD). The result was robust across 14 prespecified sensitivity analyses (Spearman ρ of t
  statistics 0.74–0.999).
- **Signature:** the locked 200-gene signature was dominated by lower expression in AD of oxidative-phosphorylation and
  ribosomal genes.
- **Related cohort:** in GSE63061 (139 AD, 133 controls) the composite score shifted strongly toward AD (one-sided
  p = 3.0 × 10⁻¹⁴; 194 of 200 genes consistent). This agreement may be inflated by participant overlap.
- **Replication:** in GSE140829 (201 AD, 248 controls) the signature replicated directionally but weakly (one-sided
  p = 0.0019; 43 of 200 genes replicated; 183 of 200 directionally concordant).
- **Specificity:** in GSE99039, the score was shifted in the AD direction in idiopathic Parkinson's disease (two-sided
  p = 0.018), but not significantly after the prespecified Holm correction (p = 0.053). Specificity could therefore be
  neither demonstrated nor excluded.
- **Classifier:**
  - in nested cross-validation it reached AUROC 0.841 (repeat range 0.824–0.852), above an age-only model (0.622) and an
    equal-weight gene score (0.780); a within-chip permutation null gave p = 0.005;
  - applied once, frozen, it reached AUROC 0.769 in GSE63061 but 0.525 (95% CI 0.471–0.579) in GSE140829, which is no
    better than chance.
- **Cell composition:**
  - in the discovery cohort, all 199 evaluable locked genes remained significant after adjustment;
  - in GSE140829, adjustment halved the composite shift (0.25 to 0.12; p = 0.041) and reduced gene-level replication from
    43 to 1 gene;
  - in idiopathic Parkinson's disease the shift fell from +0.20 to +0.08 (p = 0.27).

**Conclusions.** A blood transcriptomic AD signal reproduces across cohorts only as a modest group-level shift. Outside
the discovery cohort, that shift is largely accounted for by indices of leukocyte composition, and it may be partly
shared with Parkinson's disease. It does not support individual-level classification in an external cohort.
Reproducibility within one consortium substantially overstated external evidence.

---

## 1. Introduction

Blood-based biomarkers could make the detection and monitoring of Alzheimer's disease (AD) cheaper and more accessible
than cerebrospinal fluid or PET measures [1]. Plasma proteins, notably phosphorylated tau species, have advanced
furthest [2]. Peripheral blood transcriptomes offer a complementary view: they capture systemic immune, metabolic and
mitochondrial processes that have been linked to neurodegeneration [3], and large public microarray datasets are
available.

Several blood transcriptomic AD signatures and classifiers have been reported, many of them derived from the AddNeuroMed
cohorts deposited as GSE63060 and GSE63061 [3–6]. Reported classification accuracies are often high, although external
performance has been more modest [6]. These
studies share recurring vulnerabilities. Two cohorts from the same consortium are often treated as discovery and
"validation", although they may share participants and processing. Deposited diagnostic labels may not reflect diagnosis at the time of the blood draw,
and diagnostic criteria differ between cohorts.
Processing batches can be confounded with diagnosis. Feature selection or tuning outside the cross-validation loop can
inflate performance [7,8]. Finally, whole-blood expression reflects leukocyte composition as well as within-cell
regulation, so apparent disease signatures may be cell-mix signatures [9,10].

We therefore re-examined the question under a written, decision-logged statistical analysis plan, in which every
analytic choice that could depend on the results was fixed and approved before the corresponding data were modelled. We
asked four questions:
- (A) which blood genes are associated with AD in a discovery cohort;
- (B) whether a signature locked in that cohort reproduces in other cohorts, distinguishing a related cohort from a
  replication cohort;
- (C) whether the signature is also shifted in Parkinson's disease, which bears on disease specificity;
- (D) whether a leakage-controlled classifier transports to unseen cohorts.

We also assessed how much of the signal is explained by indices of leukocyte composition.

## 2. Methods

### 2.1 Governance and reproducibility
- **Plan and decisions:** the analysis followed a written SAP with a decision register. Each decision was approved before
  the analysis it governed, and changes after results were limited to labelled amendments.
- **Code identity:** every output was produced under a code-identity lifecycle that hashes the code, the R and Python
  environments and the inputs, and verifies the executed code against those hashes. Two independent computations had to be
  byte-identical before an output was accepted.
- **Software:** R 4.6.1, Bioconductor 3.23, limma 3.68.5 and glmnet 5.1, with a pinned Python environment.

### 2.2 Datasets and roles

| Dataset | Platform | Role | Primary population (after approved exclusions) |
|---|---|---|---|
| GSE63060 | Illumina HT-12 v3 (GPL6947) | Discovery | 145 AD, 60 CTL |
| GSE63061 | Illumina HT-12 v4 (GPL10558) | Related-cohort consistency; possible overlap | 139 AD, 133 CTL |
| GSE140829 | Illumina HT-12 v4, nuID-keyed (GPL15988) | Replication; independence unverified | 201 AD, 248 CTL |
| GSE99039 | Affymetrix HG-U133 Plus 2 (GPL570) | Parkinson's specificity | IPD 197, GPD 40, GU 22, CONTROL 229 (before complete-case on sex) |

Dataset sources: GSE63060 and GSE63061 (AddNeuroMed) [4,5]; GSE140829 [14]; GSE99039 [16].

### 2.3 Eligibility and quality control
- **Eligibility:** rule-based. Deposited diagnostic labels were used without relabelling, and MCI and other labels were
  kept outside the primary contrasts.
- **Duplicate review:** metadata and expression-similarity duplicate review, with a designated reviewer.
- **Sex check (R8):** two-axis sex concordance, using XIST and nine Y-chromosome genes (eight on GPL570), without a
  validated threshold.
- **Outlier check (R9):** robust outlier and near-identity flags.
- **Exclusions:** the PI reviewed and approved each cohort's complete rule-applied exclusion list before any expression model.
- **Finding:** in GSE63060, 44 of 104 deposited controls, and no AD arrays, were discordant on both sex axes. The
  expression-derived and recorded sex totals among controls were equal, consistent with a permutation of sex labels or
  sample identities. The comparable rates were 1 of 388 arrays in GSE63061, 2 of 587 in GSE140829 and 15 of 558 in
  GSE99039. The data owners were queried and the discrepancy was reported to GEO in October 2026; no corrected GEO record was available at the time of writing. A
  curated AddNeuroMed release (ANMerge) reports correcting errors in previously shared data [17].

### 2.4 Probe-to-gene mapping
- **Illumina:** Entrez-only mapping with a single pinned annotation snapshot; multi-mapped probes were excluded.
- **GSE140829:** its nuIDs were translated to ILMN probe identifiers through the pinned annotation. The translation was
  verified against a second package and against first-principles sequence decoding, with 47,008 of 47,008 features
  agreeing.
- **GPL570:** a separate, approved mapping.
- **Gene level:** each gene's value was the mean of its eligible probes.

### 2.5 Discovery and signature lock
- **Model:** limma (lmFit with eBayes, trend = TRUE) with AD status, age (linear), recorded sex and chip as a fixed effect,
  fitted in a full-rank basis.
- **Multiple testing:** Benjamini–Hochberg at q < 0.05.
- **Identifiability:** checked before the fit: 25 chips contained both groups; E = 0.82; VIF 1.22.
- **Signature:** the top 200 genes by q (ties broken by |β|, then |t|) were locked, with their directions, before any
  other cohort's expression was modelled.
- **Sensitivity analyses:** 14 prespecified analyses were run.

### 2.6 Validation tests (per cohort, no cross-cohort pooling)
- **Composite score test (C-c):** an equal-weight score (mean z of up-genes minus mean z of down-genes), with z computed
  without reference to diagnosis. A one-sided test of a shift toward AD, adjusted for the cohort's covariates, decided by
  the one-sided 95% lower bound.
- **Per-gene test (C-a):** a one-sided moderated t test in the locked direction, with BH correction across measurable
  locked genes.
- **Direction agreement (C-b):** descriptive only.
- **GSE63061:** additionally, a descriptive Pearson correlation of effects, with a nominal Fisher-z interval.
- **Coverage:** at least 50% and at least min(5, n) of the locked genes in each direction had to be measurable.

### 2.7 Specificity (GSE99039)
- **Q1:** a two-sided test of the score shift in each disease group versus controls, adjusted for sex and batch, with
  Holm correction across IPD (primary), GPD and GU (descriptive).
- **Per gene:** two-sided tests with BH correction within each contrast.
- **Age-adjusted sensitivity (S15):** labelled as sensitivity.
- **No equivalence margin:** none was specified, so no "absence of association" or "AD-specific" claim is possible by design.

### 2.8 Cell-composition sensitivity (S11 and S11-ext)
- **Indices:** five leukocyte-class indices (T cells, B lineage, NK cells, monocytic lineage, neutrophils) from the
  published MCP-counter marker lists [11]. The marker file was pinned by commit and SHA-256 (licence CC0). Each index is
  the mean of diagnosis-blind z-scores of the class's markers measurable in the cohort.
- **Use:** the indices were added as linear covariates to each primary model.
- **Discovery cohort (S11):** S11 was prespecified as a sensitivity analysis, but its method was chosen after the primary
  results.
- **External cohorts (S11-ext):** the extension to GSE140829 and GSE99039 was decided post hoc.
- **Status:** both are labelled family B, meaning the covariates are estimated from expression. Neither alters the
  locked signature.
- **Overlap:** CD3D, a T-cell marker and a locked gene, stayed in the T-cell index and was excluded from the S11
  locked-gene comparison.

### 2.9 Classifier
- **Protocol:** written and approved before any machine-learning code touched real data.
- **Features:** gene-level expression, excluding the R8 sex-check genes. Recorded sex and chip were never used as predictors.
- **Pre-processing and selection:** expression was centred within each chip without reference to diagnosis. Inside each
  training fold: scaling, limma top-k selection (k ∈ {50, 100, 200}) and a ridge penalty, chosen by inner cross-validation.
- **Cross-validation:** 20 repeats of 5-fold cross-validation with whole chips kept together in each fold, inner folds
  likewise grouped by chip, and class-weighted fitting.
- **Baselines:** prevalence, age only and an equal-weight score.
- **Metrics and null:** AUROC, AUPRC, Brier score, calibration, and sensitivity, specificity and PPV at a threshold fixed
  in the inner loop; a 200-permutation within-chip label null.
- **Synthetic leakage tests (passed before any real-data run):** random labels gave chance AUROC; a strong batch–label
  confound (AUROC 0.87 on its own) was not exploited; changing test-fold expression left every training choice unchanged.
- **External application:** the final model was refitted on all 205 discovery arrays, frozen and hashed, then applied once
  to each external cohort with within-cohort standardization.

## 3. Results

### 3.1 Discovery
- **Associations:** 1,401 of 17,425 genes at q < 0.05: 739 lower and 662 higher in AD. At probe level, 1,744 of 38,323.
- **Sensitivity analyses:** all 14 preserved the sign of all, or nearly all, of the 1,401 genes. Spearman correlations of
  t statistics with the primary analysis ranged from 0.897 to 0.999 in 13 of them; the smallest-sample analysis
  (S12: 49 AD, 37 controls) gave 0.737.
- **The locked signature:** 172 genes lower and 28 higher in AD. The top-ranked genes were NDUFA1, MRPL51, CETN2, NDUFS5,
  RPL36AL, ATP6V1E1, SEM1, COX17, UFC1 and TBCA, all lower in AD.

### 3.1b Cell-composition sensitivity (S11; method chosen after primary results)
- **Model:** the five MCP-counter leukocyte marker indices added to the discovery model (E = 0.76; VIF 1.31).
- **Locked genes:** all 199 evaluable locked genes kept their direction and q < 0.05; median effect size was 0.84 of
  the primary.
- **All genes:** 783 of the 1,401 primary associations remained significant, and all kept their sign; ρ of t = 0.92.
- **Indices by group:** AD arrays had slightly higher neutrophil, monocytic and NK indices and lower T-cell indices
  (descriptive).
- **Interpretation:** the signature is not explained by these indices, but part of the wider discovery signal is
  composition-related.

### 3.2 Related-cohort consistency (GSE63061)
- **Coverage:** all 200 genes were measurable.
- **Composite score:** θ̂ = 1.24 score units, one-sided p = 3.0 × 10⁻¹⁴, lower bound 0.985.
- **Per-gene and direction:** 194 of 200 genes were consistent at q < 0.05; 198 of 200 agreed in direction.
- **Effect correlation:** Pearson r = 0.92 (nominal Fisher-z interval 0.90–0.94).

### 3.3 Replication (GSE140829)
- **Coverage:** all 200 genes were measurable.
- **Composite score:** θ̂ = 0.25, one-sided p = 0.0019, lower bound 0.108.
- **Per-gene and direction:** 43 of 200 genes were replicated at q < 0.05 (36 of 172 down, 7 of 28 up); 183 of 200 agreed
  in direction.
- **Strongest replicated genes:** RPS12, RPL32, ITGAM (up), GTF2H5, RPS25, RPL22 and RPS27A.

### 3.4 Specificity (GSE99039)
- **Coverage:** 190 of 200 genes were measurable on GPL570.
- **IPD versus controls (183 versus 208 after the sex requirement):** θ̂ = +0.20 (95% CI 0.04–0.37); two-sided p = 0.018;
  Holm-adjusted p = 0.053. Two genes were significant, both in the AD direction: TCIRG1 and NBEAL2.
- **GPD versus controls:** θ̂ = +0.10, p = 0.47.
- **GU versus controls:** θ̂ = +0.19, p = 0.37.
- **Age-adjusted:** IPD θ̂ = +0.17, p = 0.13.
- **Overall:** under the prespecified rule, no association with Parkinson's disease was demonstrated. Every estimate lay
  in the AD direction.

### 3.4b Composition-adjusted replication and specificity (S11-ext; post hoc)
- **GSE140829, with the five marker indices added:** the composite shift fell from 0.25 to 0.12 (one-sided p = 0.041;
  lower bound 0.006). Gene-level replication fell from 43 to 1 of 200, and direction agreement from 0.92 to 0.78.
- **GSE99039, idiopathic PD:** the shift fell from +0.20 to +0.08 (p = 0.27; Holm p = 0.51). GPD and GU remained
  non-significant.
- **Interpretation:** most of the externally reproducible signal, and the borderline Parkinson's shift, track leukocyte
  composition indices. In the discovery cohort, by contrast, the signature survived adjustment (3.1b).

### 3.5 Classifier
- **Within GSE63060 (nested CV):**

  | Model | AUROC (range over repeats) | Sensitivity / specificity |
  |---|---|---|
  | Ridge | 0.841 (0.824–0.852) | 0.75 / 0.75 |
  | Elastic net | 0.850 | — |
  | Equal-weight score | 0.780 | — |
  | Age only | 0.622 | — |

  Ridge exceeded age only by 0.22 (DeLong p = 5.9 × 10⁻⁶) and the equal-weight score by 0.06 (p = 0.002). The permutation
  null averaged 0.485 (maximum 0.642; p = 0.005).
- **Frozen model, applied once:**

  | Cohort | AUROC (95% CI) | Age-only model |
  |---|---|---|
  | GSE63061 | 0.769 (0.714–0.824) | 0.631 |
  | GSE140829 | 0.525 (0.471–0.579) | 0.472 (difference p = 0.17) |

## 4. Discussion

In a fully prespecified analysis of four public whole-blood cohorts, a 200-gene AD signature derived in the AddNeuroMed
discovery cohort reproduced across cohorts, but only as a modest group-level shift. Three features of the results
qualify that reproduction.

**Within-consortium agreement overstated external evidence.** In GSE63061, from the same consortium, agreement was
nearly complete: 194 of 200 genes were consistent, effects correlated at r = 0.92, and the frozen classifier reached
AUROC 0.77. In GSE140829 the composite test passed (one-sided p = 0.0019), but only 43 genes replicated
individually, direction agreement fell to 92%, and the same classifier performed at chance (AUROC 0.53). Score
magnitudes are not comparable across cohorts, so we do not compare θ directly; the contrast in gene-level and
classifier results is nonetheless large and consistent. Possible participant overlap and shared
processing within AddNeuroMed provide a plausible explanation. The pattern suggests that "validation" in a sister
cohort should not be read as external evidence [12].

**The external signal is largely a leukocyte-composition signal.** The signature is dominated by lower expression of
mitochondrial oxidative-phosphorylation and ribosomal genes. The genes that replicated in GSE140829, or shifted in
Parkinson's disease, included ribosomal and myeloid-associated genes (ITGAM, TCIRG1, NBEAL2). In whole blood, ribosomal
transcript abundance tracks lymphocyte content, and myeloid genes track neutrophil and monocyte content [9,10].
- In the discovery cohort, adjustment for five marker-based composition indices left every evaluable locked gene
  significant. The lock was selected to be robust there.
- In GSE140829, the same adjustment halved the composite shift and removed almost all gene-level replication.
- In idiopathic Parkinson's disease it removed most of the borderline shift.

AD arrays showed slightly higher myeloid and NK indices and lower T-cell indices, consistent with reports of altered
leukocyte profiles in AD, and with the monocyte- and neutrophil-driven innate immune signal
reported by the GSE140829 investigators [13,14]. Adjustment cannot distinguish confounding from mediation. If AD is accompanied by a
genuine shift in circulating immune cells, that shift is itself disease-associated biology, but it is unlikely to be
specific to AD; those investigators found the same innate immune signal in several non-AD dementias, and
peripheral neutrophil-to-lymphocyte ratios are also elevated in Parkinson's disease [14,15]. The external extension of this analysis was post hoc, and the indices are noisy proxies, so these
findings are hypothesis-generating.

**Specificity was not established.** The idiopathic PD contrast showed a same-direction shift that was nominally
significant, but not after the prespecified Holm correction, and largely composition-related on adjustment. No
equivalence margin was defined, so our data cannot show absence of association. The same-direction estimates in all
three Parkinson's contrasts argue against interpreting the signature as AD-specific. They are more consistent with a
shared, possibly non-specific, systemic component [14–16].

**Classifier transportability.** Inside the discovery cohort, a leakage-controlled ridge model clearly outperformed
age-only and equal-weight baselines and a within-chip permutation null. Its failure in GSE140829 was observed in a
single prespecified application of a frozen model, and we did not re-tune it. That failure is consistent with the
composition findings. A classifier trained on one cohort's mixture of cell-mix, processing and disease effects need not
generalize when those components differ.

**Data quality.** Quality control revealed that 44 of 104 deposited controls in GSE63060 had expression-derived sex
discordant on both X and Y axes, with balanced totals suggestive of permuted labels or identities. Because GSE63060 is
widely reused, this finding warrants attention. The affected arrays were excluded by a prespecified rule, but a two-axis sex
check cannot detect label or sample swaps between participants of the same sex, so residual mislabelling in GSE63060 cannot
be ruled out. ANMerge, a curated release of the AddNeuroMed data that reports correcting errors in previously shared data [17],
offers a route to test this directly; we have not yet used it.

**Strengths and implications.**
- **Strengths:** a written plan with logged approvals; signature locking before any other cohort's expression was
  modelled; per-cohort roles fixed in advance; byte-reproducible outputs under code-identity verification; and a
  machine-learning protocol with synthetic leakage tests run before real data.
- **Effect of the design:** it prevented outcome-dependent revision. That is visible here as a willingness to report a
  chance-level external AUROC and a non-significant specificity test.
- **Implications for future work:**
  - blood transcriptomic AD signatures should be evaluated against composition-adjusted models and measured blood
    counts;
  - they should be tested in cohorts that are demonstrably independent;
  - they should be compared with other neurodegenerative diseases using prespecified equivalence margins.

## 5. Limitations

- Labels are as deposited. They may not reflect diagnosis at the time of the blood draw, and diagnostic criteria differ across cohorts.
- The independence of GSE140829 from AddNeuroMed participants is unverified, and GSE63061 may overlap with GSE63060.
- Platforms and processing differ (Illumina v3 and v4, nuID-keyed data, Affymetrix), and score magnitudes cannot be
  compared across cohorts.
- No equivalence margin was set, so specificity cannot be established.
- The GSE63060 deposit has known annotation problems: two-axis sex-discordant arrays were excluded, but same-sex label or sample
  swaps are undetectable from the deposited data. Re-analysis against the curated ANMerge release [17] was not performed.
- Cell composition was assessed only with marker-based indices from markers developed mainly for tissue. The S11 method was chosen after the primary results, and the external extension (S11-ext) was post hoc. Both residual confounding and over-adjustment are possible, and no measured blood counts were available.
- Classifier probabilities are not calibrated risks (class weighting); there is no clinical validation and no prospective cohort.

## 6. Data and code availability

All datasets are public on GEO. The code, environment locks, identity records, decision register and every accepted output
are in the BIO-MB-001 repository (currently private: github.com/sadgaselime/BIO-MB-001; to be made public on publication).

## References

1. Hansson O. Biomarkers for neurodegenerative diseases. *Nat Med*. 2021;27:954–963.
2. Palmqvist S, et al. Discriminative accuracy of plasma phospho-tau217 for Alzheimer disease vs other neurodegenerative disorders. *JAMA*. 2020;324(8):772–781. doi:10.1001/jama.2020.12134
3. Lunnon K, Ibrahim Z, Proitsi P, et al.; AddNeuroMed Consortium. Mitochondrial dysfunction and immune activation are detectable in early Alzheimer's disease blood. *J Alzheimers Dis*. 2012;30(3):685–710. doi:10.3233/JAD-2012-111592. PMID 22466004.
4. Lovestone S, et al.; AddNeuroMed Consortium. AddNeuroMed—the European collaboration for the discovery of novel biomarkers for Alzheimer's disease. *Ann N Y Acad Sci*. 2009;1180:36–46. PMID 19906259.
5. Sood S, et al. A novel multi-tissue RNA diagnostic of healthy ageing relates to cognitive health status. *Genome Biol*. 2015;16:185. doi:10.1186/s13059-015-0750-x
6. Lee T, Lee H. Prediction of Alzheimer's disease using blood gene expression data. *Sci Rep*. 2020;10:3485.
7. Kapoor S, Narayanan A. Leakage and the reproducibility crisis in machine-learning-based science. *Patterns*. 2023;4(9):100804. doi:10.1016/j.patter.2023.100804
8. Whalen S, Schreiber J, Noble WS, Pollard KS. Navigating the pitfalls of applying machine learning in genomics. *Nat Rev Genet*. 2022;23(3):169–181. doi:10.1038/s41576-021-00434-9
9. Whitney AR, et al. Individuality and variation in gene expression patterns in human blood. *Proc Natl Acad Sci USA*. 2003;100(4):1896–1901. PMID 12578971.
10. Palmer C, Diehn M, Alizadeh AA, Brown PO. Cell-type specific gene expression profiles of leukocytes in human peripheral blood. *BMC Genomics*. 2006;7:115. doi:10.1186/1471-2164-7-115
11. Becht E, et al. Estimating the population abundance of tissue-infiltrating immune and stromal cell populations using gene expression. *Genome Biol*. 2016;17:218. doi:10.1186/s13059-016-1070-5 (erratum published)
12. Collins GS, Moons KGM, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ*. 2024;385:e078378. doi:10.1136/bmj-2023-078378
13. Gate D, et al. Clonally expanded CD8 T cells patrol the cerebrospinal fluid in Alzheimer's disease. *Nature*. 2020;577(7790):399–404. doi:10.1038/s41586-019-1895-7
14. Nachun D, Ramos EM, Karydas A, Dokuru D, Gao F, Yang Z, Van Berlo V, Sears R, Kramer J, Boxer AL, Rosen H, Miller BL, Coppola G. Systems-level analysis of peripheral blood gene expression in dementia patients reveals an innate immune response shared across multiple disorders. *bioRxiv*. 2019 (posted 13 December). doi:10.1101/2019.12.13.875112. Preprint (GSE140829 depositors' study); no peer-reviewed version found as of 2026-10-21.
15. Hosseini S, Shafiabadi N, Khanzadeh M, et al. Neutrophil to lymphocyte ratio in Parkinson's disease: a systematic review and meta-analysis. *BMC Neurol*. 2023;23(1):333. doi:10.1186/s12883-023-03380-7
16. Shamir R, et al. Analysis of blood-based gene expression in idiopathic Parkinson disease. *Neurology*. 2017;89(16):1676–1683. doi:10.1212/WNL.0000000000004516
17. Birkenbihl C, et al. ANMerge: a comprehensive and accessible Alzheimer's disease patient-level dataset. *J Alzheimers Dis*. 2021;79(1):423–431. doi:10.3233/JAD-200948

## Provenance appendix (accepted outputs)

| Result | Output directory |
|---|---|
| Discovery fit and sensitivities | reports/discovery/GSE63060/fit_v1, sensitivity_v1 |
| Signature lock | reports/lock/GSE63060/v1 (signature SHA-256 9ca4310c…) |
| GSE63061 consistency | reports/validation/GSE63061/v1 |
| GSE140829 replication | reports/validation/GSE140829/v1 |
| GSE99039 specificity | reports/specificity/GSE99039/v1 |
| Classifier CV and final model | reports/ml/GSE63060/v1 (final model SHA-256 e4f7f18e…) |
| External classifier applications | reports/ml/GSE63061_external/v1, reports/ml/GSE140829_external/v1 |
| QC and exclusion lists | reports/qc_stage_b/<cohort>/v1 |
| Cell-composition sensitivity (S11) | reports/discovery/GSE63060/s11_v1 |
| Composition-adjusted replication and specificity (S11-ext, post hoc) | reports/s11_ext/v1 |
| Marker resource | reference/mcpcounter_6b85a67 (genes.txt SHA-256 408f6c5d…) |
