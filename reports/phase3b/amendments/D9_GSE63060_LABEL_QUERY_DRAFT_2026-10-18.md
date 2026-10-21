# D9 data-owner query: GSE63060 sample and sex annotation (DRAFT for PI review, 2026-10-18)

**Status:** draft only. The PI reviews, edits and sends it; it has not been sent. Approved as part of the R8 review outcome R3 (v7:625).

**Suggested recipient:** the GSE63060 submitter or contact listed on GEO, and/or the AddNeuroMed data custodians. The
contact details are on the GEO series page; they are deliberately not copied here.

---

**Subject:** GSE63060: possible mismatch between recorded sex and array data for control samples

Dear GSE63060 submitters,

We are analysing GEO series GSE63060 (AddNeuroMed batch 1, Illumina HumanHT-12 v3, GPL6947) as deposited. During routine
quality control we compared each array's recorded sex (`!Sample_characteristics_ch1` "gender") with expression-derived sex
from the Y-chromosome genes RPS4Y1 (ILMN_1783142) and KDM5D (ILMN_1685690) and from XIST (ILMN_1764573).

**What we observe:**
- **Agreement elsewhere.** The two Y-chromosome markers agree with each other on 328 of 329 arrays. For all 145 AD-labelled and all 80 MCI-labelled arrays, expression-derived sex agrees with the recorded sex.
- **Mismatches among controls.** For **46 of the 104 CTL-labelled arrays**, both Y markers disagree with the recorded sex: 23 recorded female and 23 recorded male. XIST agrees with the Y markers for 45 of these 46.
- **A permutation pattern.** Among the 104 CTL-labelled arrays, the expression-derived sex totals (62 female, 42 male) equal the recorded totals exactly. This suggests the sex annotations, or the sample-to-array assignment, may have been permuted among the control samples.

**For comparison:** our sex-consistency QC procedure flags 44 GSE63060 control arrays as discordant on both XIST and the Y-chromosome genes. The same procedure, applied to GSE63061 (AddNeuroMed batch 2, GPL10558), flags only 1 of its 388 arrays. This suggests the GSE63060 control annotations specifically are affected.

**We would be grateful if you could confirm:**
1. whether the sex (gender) annotations of the CTL samples in GSE63060 are known to contain errors, or were assigned in a different order from the arrays;
2. whether the sample-to-array assignment (GSM ↔ array barcode ↔ participant code) for the CTL samples is correct;
3. if a corrected annotation exists, whether it can be shared, including the corrected diagnosis, age and sex per array.

We can provide the list of the 46 GSM accessions and our per-array marker values on request.

With thanks,
[PI name, affiliation]

---

**Supporting evidence:**
- `reports/qc_stage_a/GSE63060/r8_diagnostics/v2/` (marker calls; `r8_marker_agreement.json`);
- `reports/qc_stage_b/GSE63060/v1/` (counts by deposited group);
- `reports/phase3b/amendments/R8_GSE63060_AMENDMENT_REVIEW_2026-10-18.md`.

The list of 46 GSMs is the `both_y_markers_disagree_with_recorded` column of `r8_marker_calls_series_matrix.tsv`.
