# Before posting: the steps only you can do (prepared 2026-10-21)

Everything that can be automated is done. The manuscript's 49 key numbers are checked against the accepted outputs
(`python3 reports/manuscript/medrxiv/check_numbers.py`; all pass), the figures are drawn from accepted outputs, and the
model is documented in `reports/ml/MODEL_CARD.md`. What remains needs you, because it involves your judgement, your
name or your accounts.

## 1. Be able to defend the paper (practice questions)

Try to answer each question aloud before reading the answer. If you can answer all ten in your own words, you understand
the paper well enough to post it.

1. **Why is GSE63061 not "validation"?** It comes from the same consortium (AddNeuroMed) as the discovery cohort and may
   contain the same people, processed the same way. Agreement there can reflect shared participants and processing, not
   a general biological truth. That is why the paper calls it "consistency", and why its near-perfect agreement (194 of
   200 genes) contrasts with GSE140829 (43 of 200).
2. **What does "locked before validation" mean, and why does it matter?** The 200 genes and their directions were fixed
   and hashed before any other cohort was modelled, so nothing could be tuned to make the other cohorts look good.
3. **What is the composite score test?** Each person gets one score: the average standardised expression of the 28
   up-genes minus that of the 172 down-genes. The test asks whether AD patients score higher than controls, adjusting for
   the cohort's covariates. It tests the signature as a whole, which is more powerful than testing 200 genes one by one.
4. **What is leukocyte composition, and why does adjusting for it matter?** Blood contains different white cells
   (neutrophils, T cells and so on), each with its own gene-expression pattern. If AD patients simply have more
   neutrophils, many genes will look "different" without any change inside the cells. Adding marker-based cell indices to
   the model asks whether the signal survives once the cell mix is accounted for. In GSE140829 it mostly did not.
5. **Why can't you say the signature is AD-specific?** The Parkinson's contrasts all shifted in the AD direction.
   The idiopathic PD shift was nominally significant (p = 0.018) but not after the pre-specified Holm correction
   (p = 0.053). And without a pre-set equivalence margin, "not significant" never proves "no effect".
6. **Why ridge regression rather than deep learning?** About 200 samples and 17,000 genes: a flexible model would
   overfit. Ridge logistic regression is the standard, well-understood choice, and it was compared with simpler
   baselines (age only, an equal-weight score) and a permutation null.
7. **What is data leakage, and how did you prevent it?** Leakage is when information from the test data influences
   training, inflating accuracy. Here, gene selection, scaling and tuning happened only inside training folds; whole chips
   were kept together; synthetic leakage tests passed before real data were used; and each external cohort was scored
   exactly once.
8. **What does AUROC 0.53 mean, and why report it?** 0.5 is a coin flip. In GSE140829 the frozen model was essentially
   at chance. Reporting it is the point of pre-specification: the result was not hidden, re-tuned or replaced.
9. **What was wrong with GSE63060's controls?** 44 of 104 controls had expression-based sex (XIST and Y-chromosome genes)
   opposite to their recorded sex, and the totals balanced exactly, suggesting swapped labels or samples. They were
   excluded by a pre-specified rule, and the data owners were contacted.
10. **What did AI do, and what did you do?** AI wrote and ran the code and drafted text. You chose the question,
    approved every decision before it was used (recorded in the decision register), reviewed the outputs and take
    responsibility for the claims. This is disclosed in Methods 2.10.

## 2. Read the PDF once, start to finish

Open `MANUSCRIPT_medRxiv_v1.pdf`. Mark anything you can't explain or don't agree with. If you change wording, edit
`MANUSCRIPT_medRxiv_v1.md`, then run these from the project root:

```bash
python3 reports/manuscript/medrxiv/check_numbers.py
bash reports/manuscript/medrxiv/build_manuscript.sh
```

## 3. Make the public code repository visible

The paper points to github.com/sadgaselime/BIO-MB-001-public, a clean copy of the project with the current files only (no
history and no private correspondence). Before you submit, open it → Settings → Change visibility → Public. The working
repository `BIO-MB-001` stays private.

## 4. Ask one researcher to read it (optional, recommended)

A posted preprint cannot be deleted, only withdrawn. Good people to ask are authors of the papers you cite (for example
the GSE140829 or ANMerge teams) or a bioinformatics lecturer at a nearby university. A short, specific request works best:

> Subject: Request for a short read of a preprint on blood transcriptomics in Alzheimer's disease
>
> Dear Dr [Name],
>
> I am an independent researcher (I finished high school in 2025 and am on a gap year). I have completed a pre-specified
> re-analysis of four public blood microarray datasets (GSE63060, GSE63061, GSE140829, GSE99039), testing whether a
> blood AD signature replicates, whether it is explained by leukocyte composition, and whether a leakage-controlled
> classifier transports to an external cohort. Your work on [their paper/topic] is directly relevant, so I would be very
> grateful if you could look at the attached manuscript before I post it on medRxiv. Even a few comments on the methods or
> framing would help.
>
> The main findings: strong agreement within AddNeuroMed, weak replication in GSE140829 that is largely explained by
> composition indices, no demonstrated specificity versus Parkinson's disease, and a chance-level external AUROC. All
> code and decision records are available.
>
> Thank you for considering it.
>
> Kind regards,
> Sadga Selime
> sadgaselime@gmail.com

## 5. ANMerge access (for the GSE63060 label question, later)

ANMerge is the curated AddNeuroMed release that may contain corrected sex labels (Synapse ID syn22252881). You need to
create a free Synapse account yourself (synapse.org), open the ANMerge project and follow its data-access instructions.
Access is not needed to post the preprint. It would allow a later version to test the label problem directly, and any
new analysis would first get its own plan and approval, like everything else in this project.

## 6. Data-owner and GEO follow-up

The discrepancy was reported to the GSE63060 submitter and to GEO (2026-10-21, ticket 26135014). GEO has contacted the
submitter and will reply when it hears back. Nothing more is needed from you until then. No permission to cite the
submitter's emails was given, so they are not quoted or summarised anywhere. If GEO's record is corrected, a short plan
for a labelled sensitivity re-check comes first, and a revised preprint can follow.

## 7. Submit

Follow `SUBMISSION_GUIDE.md`.
