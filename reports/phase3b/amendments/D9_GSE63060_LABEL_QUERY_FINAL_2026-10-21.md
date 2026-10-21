# D9 data-owner query — final text to send (2026-10-21)

Sender: Sadga Selime, gap-year student and independent researcher. Not yet sent. Attach `D9_GSE63060_46_arrays_2026-10-21.csv` (same folder).
Recipients: the GSE63060 contact listed on its GEO series page, and/or the corresponding author of Sood et al., Genome
Biology 2015. Look these up yourself; contact details are deliberately not stored in the project.

---

**Subject:** GSE63060: possible sex-annotation mismatch in control samples

Dear Dr [surname],

I am a gap-year student (I completed high school last year) working as an independent researcher, and I am
analysing the AddNeuroMed blood expression data you deposited as GEO series GSE63060
(Illumina HumanHT-12 v3, GPL6947). During routine quality control I found a pattern in the control samples that you may
want to know about, and I would be grateful for your advice.

I compared each array's recorded sex (the "gender" characteristic) with its expression-based sex, using the Y-chromosome
genes RPS4Y1 and KDM5D and the X-linked gene XIST:

- **Mismatches.** For all 145 AD-labelled and all 80 MCI-labelled arrays, expression and recorded sex agree. For **46 of
  the 104 control arrays**, both Y-chromosome markers disagree with the recorded sex: 23 recorded female and 23 recorded
  male. XIST agrees with the Y markers in 45 of these 46.
- **Balanced totals.** Among the controls, the expression-based totals (62 female, 42 male) exactly equal the recorded
  totals. That suggests the sex labels, or the sample-to-array assignment, may have been permuted among the controls
  rather than mis-recorded at random.
- **Comparison cohort.** The same check on GSE63061 (AddNeuroMed batch 2) flags only 1 of 388 arrays.

Could you tell me:
1. whether the sex annotations of the control samples in GSE63060 are known to contain errors, or were assigned in a
   different order from the arrays;
2. whether the sample-to-array assignment (GSM, array barcode and participant code) for these controls is correct;
3. if a corrected annotation exists, whether it could be shared.

I attach the 46 GSM accessions with the per-array marker calls. My analysis treats these arrays conservatively: they are
excluded from my primary analysis by a rule fixed in advance. I would like to report the issue accurately, and I will of
course acknowledge any clarification you can give.

Thank you for making these data available.

Kind regards,
Sadga Selime
Gap-year student and independent researcher
[your email]
