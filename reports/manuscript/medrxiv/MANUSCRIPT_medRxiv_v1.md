---
title: "A reproducible blood transcriptomic signal of Alzheimer's disease is largely explained by leukocyte composition and does not transport to individual-level classification"
---

**Sadga Selime**

Independent researcher

Correspondence: Sadga Selime, sadgaselime@gmail.com

**Keywords:** Alzheimer's disease; blood transcriptomics; replication; leukocyte composition; Parkinson's disease;
machine learning; reproducibility; pre-specified analysis

## Abstract

**Background.** Blood transcriptomic signatures of Alzheimer's disease (AD) have been reported repeatedly, but their
reproducibility across cohorts, their specificity relative to other neurodegenerative diseases and their value for
classifying individuals remain uncertain.

**Methods.** We analysed four public whole-blood microarray datasets under a written, decision-logged analysis plan:
GSE63060 (discovery), GSE63061 (a related cohort with possible participant overlap), GSE140829 (replication) and GSE99039
(Parkinson's disease). Samples were selected by pre-specified eligibility and quality-control rules, including a two-axis
sex-concordance check. Differential expression used limma with age, sex and chip or batch adjustment. A 200-gene signature
was locked in the discovery cohort before any other cohort was modelled, and then tested with a composite score test, a
per-gene test and direction agreement. Specificity was tested two-sided against Parkinson's disease, with Holm correction
across three contrasts. A ridge classifier was trained with nested, chip-grouped cross-validation and applied once, frozen,
to the other cohorts. Leukocyte composition was assessed with marker-based indices: in discovery, as a sensitivity analysis
whose method was chosen after the primary results; externally, post hoc.

**Results.** In GSE63060 (145 AD, 60 controls), 1,401 of 17,425 genes were associated with AD (FDR < 0.05); the result was
robust across 14 sensitivity analyses. The locked signature was dominated by lower expression of oxidative-phosphorylation
and ribosomal genes. It shifted strongly toward AD in GSE63061 (one-sided p = 3.0 × 10⁻¹⁴) and weakly in GSE140829 (201 AD,
248 controls; p = 0.0019; 43 of 200 genes replicated). In idiopathic Parkinson's disease the score shifted in the AD
direction (two-sided p = 0.018; Holm-adjusted p = 0.053), so specificity was neither demonstrated nor excluded. The
classifier reached a cross-validated AUROC of 0.841 (permutation p = 0.005), 0.769 in GSE63061, and 0.525 (95% CI
0.471–0.579) in GSE140829. Composition adjustment left the signature intact in discovery but halved the GSE140829 shift
(p = 0.041; 1 gene replicated) and reduced the Parkinson's shift to +0.08 (p = 0.27).

**Conclusions.** A blood transcriptomic AD signal reproduces across cohorts only as a modest group-level shift. Outside the
discovery cohort it is largely accounted for by leukocyte composition, it may be shared with Parkinson's disease, and it
does not support individual-level classification in an external cohort. Agreement within one consortium substantially
overstated external evidence.

### Key points

- **Question:** Do blood gene-expression signals of Alzheimer's disease reproduce in other cohorts, are they specific to
  AD, and can they classify individuals in a cohort the model has never seen?
- **Findings:** A signature locked in one cohort reproduced almost perfectly in a sister cohort from the same consortium,
  but only weakly in a separate replication cohort. There, most of the signal disappeared after adjustment for leukocyte
  composition, and a classifier with a cross-validated AUROC of 0.84 performed at chance (0.53).
- **Meaning:** Blood transcriptomic AD signatures should be judged by tests in demonstrably independent cohorts, with
  composition-adjusted models, rather than by agreement between related cohorts.

## 1. Introduction

Blood-based biomarkers could make the detection and monitoring of Alzheimer's disease (AD) cheaper and more accessible
than cerebrospinal fluid or PET measures [1]. Plasma proteins, notably phosphorylated tau species, have advanced
furthest [2]. Peripheral blood transcriptomes offer a complementary view: they capture systemic immune, metabolic and
mitochondrial processes that have been linked to neurodegeneration [3], and large public microarray datasets are
available.

Several blood transcriptomic AD signatures and classifiers have been reported, many of them derived from the AddNeuroMed
cohorts deposited as GSE63060 and GSE63061 [3–6]. Reported classification accuracies are often high, although external
performance has been more modest [6]. These studies share recurring vulnerabilities. Two cohorts from the same consortium
are often treated as discovery and "validation", although they may share participants and processing. Deposited
diagnostic labels may not reflect diagnosis at the time of the blood draw, and diagnostic criteria differ between cohorts.
Processing batches can be confounded with diagnosis. Feature selection or tuning outside the cross-validation loop can
inflate performance [7,8]. Finally, whole-blood expression reflects leukocyte composition as well as within-cell
regulation, so apparent disease signatures may be cell-mix signatures [9,10].

We therefore re-examined the question under a written, decision-logged statistical analysis plan, in which every
analytic choice that could depend on the results was fixed and approved before the corresponding data were modelled. We
asked four questions: (A) which blood genes are associated with AD in a discovery cohort; (B) whether a signature locked
in that cohort reproduces in other cohorts, distinguishing a related cohort from a replication cohort; (C) whether the
signature is also shifted in Parkinson's disease, which bears on disease specificity; and (D) whether a
leakage-controlled classifier transports to unseen cohorts. We also assessed how much of the signal is explained by
indices of leukocyte composition. The overall design is shown in Figure 1.

![**Figure 1. Study design.** Roles, deposited and analysed sample numbers of the four cohorts (top row); discovery and
locking of the 200-gene signature in GSE63060 and the tests of that unchanged signature in the other cohorts (middle
row); the classifier trained by nested, chip-grouped cross-validation, frozen and applied once to each external cohort
(bottom row); and the leukocyte-composition sensitivity analyses (bottom band). Sample numbers are after the approved
rule-applied exclusions. IPD, idiopathic Parkinson's disease; GPD, genetic Parkinson's disease; GU, genetic
unaffected; CTL, control.](figures/Figure1_study_design.png){width=100%}

## 2. Methods

### 2.1 Governance and reproducibility

The analysis followed a written statistical analysis plan (SAP) with a decision register. The plan as a whole was not
formally frozen; instead, each decision was approved before the analysis it governed, and changes made after results were
limited to labelled amendments or post hoc analyses. Every output was produced under a code-identity lifecycle that hashes
the code, the R and Python environments and the inputs, and verifies the executed code against those hashes. Each result
was computed twice, and the two computations had to be byte-identical before the output was accepted. Software: R 4.6.1,
Bioconductor 3.23, limma 3.68.5 and glmnet 5.1, with a pinned Python environment.

### 2.2 Datasets and roles

Four public whole-blood datasets were used, each with a role fixed in advance (Table 1). Dataset sources: GSE63060 and
GSE63061 (AddNeuroMed) [4,5]; GSE140829 [11]; GSE99039 [12].

Table: **Table 1. Cohorts, platforms and pre-specified roles.** Primary populations are after the approved rule-applied
exclusions; in GSE99039, numbers are before the complete-case requirement on recorded sex.

| Dataset | Platform | Role | Primary population |
|---|---|---|---|
| GSE63060 | Illumina HT-12 v3 (GPL6947) | Discovery | 145 AD, 60 CTL |
| GSE63061 | Illumina HT-12 v4 (GPL10558) | Related-cohort consistency; possible participant overlap | 139 AD, 133 CTL |
| GSE140829 | Illumina HT-12 v4, nuID-keyed (GPL15988) | Replication; independence unverified | 201 AD, 248 CTL |
| GSE99039 | Affymetrix HG-U133 Plus 2 (GPL570) | Parkinson's disease specificity | IPD 197, GPD 40, GU 22, CTL 229 |

### 2.3 Eligibility and quality control

Eligibility was rule-based. Deposited diagnostic labels were used without relabelling, and mild cognitive impairment
and other labels were kept outside the primary contrasts. Duplicates were reviewed using metadata and expression
similarity, with a designated reviewer. Sex was checked on two independent axes (R8), using XIST and nine Y-chromosome
genes (eight on GPL570), without a validated threshold; robust outlier and near-identity flags were also computed (R9).
The author reviewed and approved each cohort's complete rule-applied exclusion list before any expression model was fitted.

This check produced an important finding. In GSE63060, 44 of 104 deposited controls, and no AD arrays, were discordant on
both sex axes. The expression-derived and recorded sex totals among controls were equal, which is consistent with a
permutation of sex labels or sample identities. The comparable rates were 1 of 388 arrays in GSE63061, 2 of 587 in
GSE140829 and 15 of 558 in GSE99039. The data owners were queried and the discrepancy was reported to GEO in October 2026; no
corrected GEO record was available at the time of writing. A curated AddNeuroMed release (ANMerge) reports correcting errors in previously shared data [13].

### 2.4 Probe-to-gene mapping

Illumina probes were mapped to Entrez genes with a single pinned annotation snapshot, and multi-mapped probes were
excluded. For GSE140829, nuIDs were translated to ILMN probe identifiers through the pinned annotation; the translation was
verified against a second package and against first-principles sequence decoding, with 47,008 of 47,008 features
agreeing. GPL570 used a separate, approved mapping. Each gene's value was the mean of its eligible probes.

### 2.5 Discovery and signature lock

Differential expression was estimated with limma (lmFit with eBayes, trend = TRUE), modelling AD status, age (linear),
recorded sex and chip as a fixed effect in a full-rank basis. Multiple testing used Benjamini–Hochberg at q < 0.05.
Identifiability was checked before the fit: 25 chips contained both groups, with design efficiency E = 0.82 and variance
inflation factor (VIF) 1.22. The top 200 genes by q (ties broken by |β|, then |t|) were locked, with their directions,
before any other cohort's expression was modelled. Fourteen pre-specified sensitivity analyses varied the age range,
batch and site terms, QC exclusions, expression filtering, the gene-level summary and the sample subset.

### 2.6 Validation tests

Each cohort was analysed separately, without pooling. The primary test (C-c) used an equal-weight signature score: the
mean z-score of the up-genes minus the mean z-score of the down-genes, with z computed without reference to diagnosis.
A shift toward AD was tested one-sided, adjusted for the cohort's covariates, and decided by the one-sided 95% lower
bound. A per-gene test (C-a) used one-sided moderated t tests in the locked direction, with BH correction across
measurable locked genes; direction agreement (C-b) was descriptive. For GSE63061, a descriptive Pearson correlation of
effects was added, with a nominal Fisher-z interval. A cohort was testable only if at least 50%, and at least min(5, n),
of the locked genes in each direction were measurable.

### 2.7 Specificity

In GSE99039, the score shift in each disease group versus controls was tested two-sided (Q1), adjusted for sex and
batch, with Holm correction across idiopathic PD (primary), genetic PD and genetic unaffected carriers (descriptive).
Per-gene tests were two-sided with BH correction within each contrast. An age-adjusted model (S15) was a labelled
sensitivity analysis. No equivalence margin was specified, so by design no claim of "absence of association" or
"AD-specific" could be made.

### 2.8 Cell-composition sensitivity (S11 and S11-ext)

Five leukocyte-class indices (T cells, B lineage, NK cells, monocytic lineage, neutrophils) were built from the published
MCP-counter marker lists [14], pinned by commit and SHA-256 (licence CC0). Each index is the mean of diagnosis-blind
z-scores of that class's markers measurable in the cohort, and the indices were added as linear covariates to each
primary model. In the discovery cohort (S11), the analysis was pre-specified as a sensitivity analysis but its method was
chosen after the primary results. The extension to GSE140829 and GSE99039 (S11-ext) was decided post hoc. Because the
covariates are themselves estimated from expression, both analyses are labelled accordingly, and neither alters the
locked signature. CD3D, a T-cell marker that is also a locked gene, stayed in the T-cell index and was excluded from the
S11 locked-gene comparison.

### 2.9 Classifier

The machine-learning protocol was written and approved before any machine-learning code touched real data. Features were
gene-level expression values, excluding the R8 sex-check genes; recorded sex and chip were never used as predictors.
Expression was centred within each chip without reference to diagnosis. Inside each training fold, the pipeline scaled the
data, selected the top k genes with limma (k ∈ {50, 100, 200}) and fitted a ridge penalty, with k and the penalty chosen
by inner cross-validation. The outer loop was 20 repeats of 5-fold cross-validation with whole chips kept together in each
fold, inner folds likewise grouped by chip, and class-weighted fitting. Baselines were prevalence only, age only and an
equal-weight score. Metrics were AUROC, AUPRC, Brier score, calibration, and sensitivity, specificity and PPV at a threshold
fixed in the inner loop; a 200-permutation within-chip label null gave the reference distribution.

Before any real-data run, synthetic leakage tests had to pass: random labels gave chance AUROC; a strong batch–label
confound (AUROC 0.87 on its own) was not exploited; and changing test-fold expression left every training choice
unchanged. The final model was then refitted on all 205 discovery arrays, frozen and hashed, and applied once to each
external cohort with within-cohort standardisation. How the frozen model turns an expression profile into a prediction is
shown in Figure 8.

### 2.10 Use of AI tools

The author used an AI assistant (Anthropic's Claude, model Claude Opus 5.5, through Claude Code) to write and test
analysis code, run the analyses, and draft and edit the manuscript text. Every analytic decision was made or approved by the
author, recorded in a decision register before the corresponding analysis, and verified through the code-identity
checks described in 2.1. The author reviewed all outputs and text and takes full responsibility for the content. AI
tools are not authors.

### 2.11 Reporting

The classifier component is reported with reference to TRIPOD+AI [15] where applicable. No new data were collected.

## 3. Results

### 3.1 Discovery: a mitochondrial and ribosomal signature

In GSE63060, 1,401 of 17,425 genes were associated with AD at q < 0.05: 739 were lower and 662 higher in AD. At probe
level, 1,744 of 38,323 probes reached the same threshold. The strongest associations were reductions in AD (Figure 2a).
The locked 200-gene signature contained 172 genes lower and 28 higher in AD. The ten top-ranked genes were NDUFA1, MRPL51,
CETN2, NDUFS5, RPL36AL, ATP6V1E1, SEM1, COX17, UFC1 and TBCA, all lower in AD; several encode components of the
mitochondrial respiratory chain or of ribosomes.

The result was robust (Figure 2b). All 14 sensitivity analyses preserved the sign of all, or nearly all, of the 1,401
genes. Spearman correlations of t statistics with the primary analysis ranged from 0.897 to 0.999 in 13 of them; the
analysis with the smallest sample (49 AD, 37 controls) gave 0.737.

![**Figure 2. Discovery in GSE63060.** (a) Volcano plot of 17,425 genes: adjusted AD minus control effect (x-axis)
against statistical significance (y-axis). Coloured points are the 200 locked genes (blue, lower in AD; orange, higher);
grey points are other genes at FDR < 0.05; the dashed line marks FDR 0.05. The most significant locked genes are labelled.
(b) Agreement of each of the 14 pre-specified sensitivity analyses with the primary analysis, measured as the Spearman
correlation of gene-level t statistics; n is the number of arrays in each analysis.](figures/Figure2_discovery.png){width=100%}

### 3.2 Related-cohort consistency (GSE63061)

All 200 locked genes were measurable in GSE63061. The signature score was clearly higher in AD than in controls
(Figure 3a): the adjusted shift was θ̂ = 1.24 score units (one-sided p = 3.0 × 10⁻¹⁴; lower bound 0.985). At gene level,
194 of 200 genes were consistent at q < 0.05 and 198 of 200 agreed in direction, and the discovery and GSE63061 effects
were tightly correlated (Pearson r = 0.92; nominal Fisher-z interval 0.90–0.94; Figure 5a).

### 3.3 Replication (GSE140829)

All 200 genes were also measurable in GSE140829, but the picture was very different. The composite test passed
(θ̂ = 0.25; one-sided p = 0.0019; lower bound 0.108), yet the AD and control score distributions overlapped almost
completely (Figure 3b). Only 43 of 200 genes replicated at q < 0.05 (36 of 172 down-genes and 7 of 28 up-genes), although
183 of 200 agreed in direction (Figure 5b). The strongest replicated genes were RPS12, RPL32, ITGAM (up), GTF2H5, RPS25,
RPL22 and RPS27A.

![**Figure 3. Distribution of the locked signature score by group.** Each point is one array; boxes show the median and
interquartile range. (a) GSE63061, related AddNeuroMed cohort. (b) GSE140829, replication cohort. (c) GSE99039, idiopathic
Parkinson's disease versus controls (the primary specificity contrast; arrays with recorded sex). Scores are unadjusted
and on each cohort's own scale; the formal tests (Figure 4) adjust for each cohort's covariates.](figures/Figure3_score_distributions.png){width=100%}

### 3.4 Specificity (GSE99039)

On GPL570, 190 of 200 locked genes were measurable. In idiopathic PD versus controls (183 versus 208 arrays after the sex
requirement), the score shifted in the AD direction: θ̂ = +0.20 (95% CI 0.04–0.37; two-sided p = 0.018; Holm-adjusted
p = 0.053; Figure 3c and Figure 4c). Two genes were individually significant, both in the AD direction: TCIRG1 and
NBEAL2. The genetic PD (θ̂ = +0.10, p = 0.47) and genetic unaffected (θ̂ = +0.19, p = 0.37) contrasts were not significant,
and the age-adjusted IPD estimate was +0.17 (p = 0.13). Under the pre-specified rule, therefore, no association with
Parkinson's disease was demonstrated, but every estimate lay in the AD direction.

![**Figure 4. Composite score shifts of the locked 200-gene signature.** Adjusted mean difference in the signature score
(disease minus control) with two-sided 95% confidence intervals. (a) GSE63061, related cohort with possible participant
overlap. (b) GSE140829, replication cohort. (c) GSE99039, Parkinson's disease contrasts versus controls (primary analysis
two-sided and Holm-corrected across three contrasts). Blue, primary pre-specified analyses; orange, post hoc analyses
additionally adjusted for five marker-based leukocyte composition indices. Each panel uses its cohort's own score scale,
so magnitudes are not comparable across panels.](figures/Figure4_score_shifts.png){width=78%}

![**Figure 5. Per-gene agreement of the locked signature.** Each point is one of the 200 locked genes: its discovery effect
in GSE63060 (x-axis) against its effect in the second cohort (y-axis), both adjusted AD minus control differences.
(a) GSE63061: coloured genes are consistent at one-sided BH q < 0.05 in the locked direction. (b) GSE140829: coloured
genes are replicated at the same threshold. Note the different y-axis scales.](figures/Figure5_gene_agreement.png){width=100%}

### 3.5 Leukocyte composition

In the discovery cohort, AD arrays had slightly higher neutrophil, monocytic and NK indices and lower T-cell indices
(descriptive; Figure 6a). Adding the five indices to the discovery model (E = 0.76; VIF 1.31) left the signature intact:
all 199 evaluable locked genes kept their direction and q < 0.05, and their median effect size was 0.84 of the primary
(Figure 6b). Across all genes, 783 of the 1,401 primary associations remained significant, all with the same sign
(Spearman ρ of t = 0.92). The signature is therefore not explained by these indices in the discovery cohort, although
part of the wider discovery signal is composition-related.

Outside the discovery cohort the result was different (post hoc). In GSE140829, adjustment reduced the composite shift
from 0.25 to 0.12 (one-sided p = 0.041; lower bound 0.006). Gene-level replication fell from 43 to 1 of 200, and
direction agreement from 0.92 to 0.78 (Figure 4b and Figure 6c). In idiopathic PD, the shift fell from +0.20 to +0.08
(p = 0.27; Holm p = 0.51), and the genetic PD and genetic unaffected contrasts remained non-significant (Figure 4c). Most
of the externally reproducible signal, and the borderline Parkinson's shift, therefore track the leukocyte composition
indices.

![**Figure 6. Leukocyte composition.** (a) Marker-based leukocyte indices (MCP-counter markers) in GSE63060 controls and
AD arrays (descriptive). (b) Discovery cohort: locked-gene effects in the primary model (x-axis) against the model
additionally adjusted for the five indices (y-axis); the dashed line is equality (199 genes; CD3D excluded because it is a
T-cell marker). (c) GSE140829: the same comparison in the replication cohort (200 genes; post hoc). Points near the
dashed line keep their effect after adjustment; points pulled toward zero lose it.](figures/Figure6_leukocyte_composition.png){width=100%}

### 3.6 Classifier

Within GSE63060, under nested chip-grouped cross-validation, the ridge model reached an AUROC of 0.841 (Table 2; Figure 7a).
It exceeded the age-only model by 0.22 (DeLong p = 5.9 × 10⁻⁶) and the equal-weight score by 0.06 (p = 0.002). The
within-chip permutation null averaged 0.485 (maximum 0.642; p = 0.005; Figure 7b).

Table: **Table 2. Classifier discrimination within the discovery cohort.** Out-of-fold results over 20 repeats of
nested, chip-grouped 5-fold cross-validation in GSE63060.

| Model | AUROC (range over repeats) | Sensitivity / specificity |
|---|---|---|
| Ridge | 0.841 (0.824–0.852) | 0.75 / 0.75 |
| Elastic net | 0.850 | — |
| Equal-weight score | 0.780 | — |
| Age only | 0.622 | — |

The frozen model was then applied once to each external cohort, without re-tuning (Table 3; Figure 7c). It retained much
of its performance in the related cohort GSE63061 (AUROC 0.769), but in the replication cohort GSE140829 it performed at
chance (0.525) and did not differ from the age-only model (p = 0.17).

Table: **Table 3. Frozen classifier applied once to external cohorts.** AUROC with DeLong 95% confidence interval.

| Cohort | Ridge AUROC (95% CI) | Age-only AUROC |
|---|---|---|
| GSE63061 (related) | 0.769 (0.714–0.824) | 0.631 |
| GSE140829 (replication) | 0.525 (0.471–0.579) | 0.472 (difference p = 0.17) |

![**Figure 7. Classifier discrimination.** (a) Out-of-fold AUROC over 20 repeats of nested, chip-grouped 5-fold
cross-validation in GSE63060 for the ridge model, the elastic net, an equal-weight score of fold-selected genes and an
age-only model; dashed line, chance. (b) Mean AUROC under 200 within-chip label permutations, with the observed mean
ridge AUROC (0.841). (c) ROC curves: GSE63060 from repeat-averaged out-of-fold predictions (AUROC 0.85 for the averaged
predictions, compared with a mean of 0.841 over individual repeats), and the frozen model applied once to GSE63061 and
GSE140829.](figures/Figure7_classifier.png){width=100%}

![**Figure 8. Anatomy of the frozen classifier.** (Left) The steps from blood expression to a prediction. (Right) The 20 of
200 genes with the largest weights (per standard deviation of expression): orange, higher expression pushes toward an
AD-like prediction; blue, lower expression does. Ridge regression spreads the signal across all genes, so individual
weights are small and should not be read as a diagnostic gene panel.](figures/Figure8_model_anatomy.png){width=100%}

## 4. Discussion

In a fully pre-specified analysis of four public whole-blood cohorts, a 200-gene AD signature derived in the AddNeuroMed
discovery cohort reproduced across cohorts, but only as a modest group-level shift. Three features of the results
qualify that reproduction.

**Within-consortium agreement overstated external evidence.** In GSE63061, from the same consortium, agreement was
nearly complete: 194 of 200 genes were consistent, effects correlated at r = 0.92, and the frozen classifier reached
AUROC 0.77. In GSE140829 the composite test passed (one-sided p = 0.0019), but only 43 genes replicated
individually, direction agreement fell to 92%, and the same classifier performed at chance (AUROC 0.53). Score
magnitudes are not comparable across cohorts, so we do not compare θ directly; the contrast in gene-level and
classifier results is nonetheless large and consistent (Figures 5 and 7). Possible participant overlap and shared
processing within AddNeuroMed provide a plausible explanation. The pattern suggests that "validation" in a sister
cohort should not be read as external evidence [15].

**The external signal is largely a leukocyte-composition signal.** The signature is dominated by lower expression of
mitochondrial oxidative-phosphorylation and ribosomal genes. The genes that replicated in GSE140829, or shifted in
Parkinson's disease, included ribosomal and myeloid-associated genes (ITGAM, TCIRG1, NBEAL2). In whole blood, ribosomal
transcript abundance tracks lymphocyte content, and myeloid genes track neutrophil and monocyte content [9,10]. In the
discovery cohort, adjustment for five marker-based composition indices left every evaluable locked gene significant; the
lock was, after all, selected to be robust there. In GSE140829, the same adjustment halved the composite shift and removed
almost all gene-level replication, and in idiopathic Parkinson's disease it removed most of the borderline shift
(Figure 6).

AD arrays showed slightly higher myeloid and NK indices and lower T-cell indices, consistent with reports of altered
leukocyte profiles in AD, and with the monocyte- and neutrophil-driven innate immune signal reported by the GSE140829
investigators [11,16]. Adjustment cannot distinguish confounding from mediation. If AD is accompanied by a genuine shift in
circulating immune cells, that shift is itself disease-associated biology, but it is unlikely to be specific to AD; those
investigators found the same innate immune signal in several non-AD dementias, and peripheral neutrophil-to-lymphocyte
ratios are also elevated in Parkinson's disease [11,17]. The external extension of this analysis was post hoc, and the
indices are noisy proxies, so these findings are hypothesis-generating.

**Specificity was not established.** The idiopathic PD contrast showed a same-direction shift that was nominally
significant, but not after the pre-specified Holm correction, and largely composition-related on adjustment. No
equivalence margin was defined, so our data cannot show absence of association. The same-direction estimates in all
three Parkinson's contrasts argue against interpreting the signature as AD-specific. They are more consistent with a
shared, possibly non-specific, systemic component [11,12,17].

**Classifier transportability.** Inside the discovery cohort, a leakage-controlled ridge model clearly outperformed
age-only and equal-weight baselines and a within-chip permutation null. Its failure in GSE140829 was observed in a
single pre-specified application of a frozen model, and we did not re-tune it. That failure is consistent with the
composition findings: a classifier trained on one cohort's mixture of cell-mix, processing and disease effects need not
generalise when those components differ.

**Data quality.** Quality control revealed that 44 of 104 deposited controls in GSE63060 had expression-derived sex
discordant on both X and Y axes, with balanced totals suggestive of permuted labels or identities. Because GSE63060 is
widely reused, this finding warrants attention. The affected arrays were excluded by a pre-specified rule, but a two-axis
sex check cannot detect label or sample swaps between participants of the same sex, so residual mislabelling in GSE63060
cannot be ruled out. ANMerge, a curated release of the AddNeuroMed data that reports correcting errors in previously
shared data [13], offers a route to test this directly; we have not yet used it.

**Strengths and implications.** The study's strengths are a written plan with logged approvals; signature locking
before any other cohort's expression was modelled; per-cohort roles fixed in advance; byte-reproducible outputs under
code-identity verification; and a machine-learning protocol with synthetic leakage tests run before real data. The design
prevented outcome-dependent revision, which is visible here as a willingness to report a chance-level external AUROC and a
non-significant specificity test. For future work, blood transcriptomic AD signatures should be evaluated against
composition-adjusted models and measured blood counts, tested in cohorts that are demonstrably independent, and compared
with other neurodegenerative diseases using pre-specified equivalence margins.

## 5. Limitations

- Labels are as deposited. They may not reflect diagnosis at the time of the blood draw, and diagnostic criteria differ
  across cohorts.
- The independence of GSE140829 from AddNeuroMed participants is unverified, and GSE63061 may overlap with GSE63060.
- Platforms and processing differ (Illumina v3 and v4, nuID-keyed data, Affymetrix), and score magnitudes cannot be
  compared across cohorts.
- No equivalence margin was set, so specificity cannot be established.
- The GSE63060 deposit has known annotation problems: two-axis sex-discordant arrays were excluded, but same-sex label or
  sample swaps are undetectable from the deposited data. Re-analysis against the curated ANMerge release [13] was not
  performed.
- Cell composition was assessed only with marker-based indices from markers developed mainly for tissue. The S11 method
  was chosen after the primary results, and the external extension (S11-ext) was post hoc. Both residual confounding and
  over-adjustment are possible, and no measured blood counts were available.
- Classifier probabilities are not calibrated risks (class weighting); there is no clinical validation and no
  prospective cohort.

## 6. Conclusions

A carefully pre-specified re-analysis found a real but modest blood transcriptomic signal of AD. It reproduced strongly
within one consortium and weakly outside it, where it was largely explained by leukocyte composition, may be shared with
Parkinson's disease, and did not support individual-level classification. Claims of blood transcriptomic AD biomarkers
should be tested against these three hurdles: independent cohorts, composition adjustment and disease specificity.

## Declarations

**Ethics statement.** This study is a secondary analysis of de-identified data that are openly available in the Gene
Expression Omnibus (GSE63060, GSE63061, GSE140829, GSE99039). The original studies obtained ethical approval and
participant consent, as described in their publications [4,5,11,12]. No new participants were recruited, and no
additional ethics approval was required.

**Funding.** None. This work received no specific funding.

**Competing interests.** The author declares no competing interests.

**Data availability.** All data are publicly available from GEO under the accessions above. Derived outputs (exclusion
lists, signature, test results, model coefficients) are included in the project repository.

**Code availability.** All analysis code, pinned environment specifications, decision records and accepted outputs with
their code-identity records are available at https://github.com/sadgaselime/BIO-MB-001-public. The figures are drawn by `R/manuscript_figures_design.R`,
`R/manuscript_figures.R` and `R/manuscript_figures_results.R` from the accepted outputs.

**Author contributions.** S.S. conceived the study, made all analytic decisions, supervised and verified the analyses, and
wrote the manuscript (see 2.10 on AI assistance).

**Acknowledgements.** The author thanks the investigators and participants of the AddNeuroMed cohorts, the GSE140829 study
and the GSE99039 study for making their data openly available.

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
11. Nachun D, Ramos EM, Karydas A, Dokuru D, Gao F, Yang Z, Van Berlo V, Sears R, Kramer J, Boxer AL, Rosen H, Miller BL, Coppola G. Systems-level analysis of peripheral blood gene expression in dementia patients reveals an innate immune response shared across multiple disorders. *bioRxiv*. 2019 (posted 13 December). doi:10.1101/2019.12.13.875112. Preprint (GSE140829 depositors' study); no peer-reviewed version found as of 2026-10-21.
12. Shamir R, et al. Analysis of blood-based gene expression in idiopathic Parkinson disease. *Neurology*. 2017;89(16):1676–1683. doi:10.1212/WNL.0000000000004516
13. Birkenbihl C, et al. ANMerge: a comprehensive and accessible Alzheimer's disease patient-level dataset. *J Alzheimers Dis*. 2021;79(1):423–431. doi:10.3233/JAD-200948
14. Becht E, et al. Estimating the population abundance of tissue-infiltrating immune and stromal cell populations using gene expression. *Genome Biol*. 2016;17:218. doi:10.1186/s13059-016-1070-5 (erratum published)
15. Collins GS, Moons KGM, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ*. 2024;385:e078378. doi:10.1136/bmj-2023-078378
16. Gate D, et al. Clonally expanded CD8 T cells patrol the cerebrospinal fluid in Alzheimer's disease. *Nature*. 2020;577(7790):399–404. doi:10.1038/s41586-019-1895-7
17. Hosseini S, Shafiabadi N, Khanzadeh M, et al. Neutrophil to lymphocyte ratio in Parkinson's disease: a systematic review and meta-analysis. *BMC Neurol*. 2023;23(1):333. doi:10.1186/s12883-023-03380-7

## Supplementary Table S1. Locations of accepted outputs in the project repository

| Result | Output directory |
|---|---|
| Discovery fit and sensitivities | reports/discovery/GSE63060/fit_v1, sensitivity_v1 |
| Signature lock | reports/lock/GSE63060/v1 (signature SHA-256 9ca4310c…) |
| GSE63061 consistency | reports/validation/GSE63061/v1 |
| GSE140829 replication | reports/validation/GSE140829/v1 |
| GSE99039 specificity | reports/specificity/GSE99039/v1 |
| Classifier CV and final model | reports/ml/GSE63060/v1 (final model SHA-256 e4f7f18e…) |
| External classifier applications | reports/ml/GSE63061_external/v1, reports/ml/GSE140829_external/v1 |
| QC and exclusion lists | reports/qc_stage_b/(cohort)/v1 |
| Cell-composition sensitivity (S11) | reports/discovery/GSE63060/s11_v1 |
| Composition-adjusted replication and specificity (S11-ext, post hoc) | reports/s11_ext/v1 |
| Marker resource | reference/mcpcounter_6b85a67 (genes.txt SHA-256 408f6c5d…) |
