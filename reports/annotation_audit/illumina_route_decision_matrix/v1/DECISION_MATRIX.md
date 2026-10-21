# Illumina annotation-route decision matrix — v1

**Assessment only. No Illumina mapping policy is selected, recommended or approved.** No weighting or ranking is applied; each criterion is judged on its own. GSE140829 remains governed by D19; D17 is unresolved.

## Definitions

- **Option A:** package Entrez IDs reconciled to org.Hs.eg.db 3.23.1 by the approved gene-history procedure (cutoff 20260318); approved for GPL570 only (D6-F), provisional here.
- **Accession route:** probe accessions matched (unversioned) to org.Hs.eg.db 3.23.1 accessions/RefSeq; only a unique match is an assignment.
- **M1:** same-probe agreement against the post-gene-history Option A gene. **M2:** agreement against the package's original Entrez ID. M1 ⊆ M2; their totals are different metrics.
- **Denominators:** probe-level percentages use all probes of the platform table (lumi: HT-12 v4 R2 manifest rows); gene-level counts are distinct current Entrez IDs. Historical source genes and successor genes are counted separately.
- **Status:** *decisive* = settles the choice on its own (none qualify on current evidence); *supportive* = informs but does not settle; *unresolved* = cannot be judged from retained evidence.

## illuminaHumanv3 (GSE63060)

| ID | Criterion | Option A | Accession route | Advantage (this criterion only) | Status |
|---|---|---|---|---|---|
| C01 | Probes assigned exactly one eligible gene (denominator: all platform probes) | 29,489 / 49,576 (59.48%) | 29,326 / 49,576 (59.15%) | Option A | supportive |
| C02 | Distinct current Entrez genes represented (gene level) | 19,226 | 19,100 (both routes 19,085; Option A only 141; accession only 15) | Option A | supportive |
| C03 | Genes represented by more than one eligible probe (gene level; G3 averages them) | 6,554 | 6,531 (computed in this matrix from retained sources; not reported in v3) | neither | unresolved |
| C04 | M1 — same-probe agreement (probes both routes assign; vs the post-gene-history Option A gene) | both assign 29,294 | concordant 29,284 (99.97% of 29,294); discordant 10 | neither | supportive |
| C05 | ID-replacement effects (M2 → M1 transitions; M2 = vs the package's original Entrez ID) | 59 probes assigned via a gene-history successor | M2 total 29,294 vs M1 total 29,294; 40 probes 'different' under M2 become concordant under M1 after replacement; 0 probes are in M2 but not M1 | neither | supportive |
| C06 | Genuine disagreements (M1 discordant probes) | 10 probes assign a different gene than the accession route | same probes | not determinable | unresolved |
| C07 | Discontinued IDs without replacement / unexplained (Option A); unmatched accessions (accession route) | no replacement 62; unexplained 0 | accession unmatched 1,379; no accession 17,719 | not determinable | unresolved |
| C08 | Ambiguous assignments (one probe → more than one gene; excluded under both routes) | multi-gene probes in package 1,175 | accession ambiguous 1,152 | accession route | supportive |
| C09 | Unresolved probes (no eligible assignment; denominator: all probes) | 20,087 (40.52%), incl. 18,850 with no package gene | 20,250 (40.85%), incl. 19,098 without a matched accession | Option A | supportive |
| C10 | Probes assigned by only one route | Option A only: 195 (accession unresolved 185; accession ambiguous 10) | accession only: 32 | Option A | supportive |
| C11 | Probe-to-gene source, version, provenance and age | illuminaHumanv3 package Entrez source date: 2015-Mar17; reconciled to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) by the approved gene-history procedure | manufacturer accessions from the package matched to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) | accession route | supportive |
| C12 | Accession-matching limitations | not applicable (Option A uses package gene assignments) | 0 accession values carry a version; matching is on unversioned roots; 12,377 probes carry >1 accession | not determinable | unresolved |
| C13 | Successor collisions (Option A; replaced probe joins a gene that already has directly mapped probes) | probes 43; distinct successor genes 28; distinct historical source genes 30 | not applicable (no history step) | not determinable | unresolved |
| C14 | Downstream consequences for gene-level (G3) aggregation | probes per gene and collisions determine each gene's average; replacement-derived probes enter successor genes | ambiguous probes are lost; single-gene accession probes define the gene averages | not determinable | unresolved |
| C15 | Presence of probes in the cohort's Series Matrix | NOT ASSESSED | NOT ASSESSED | not determinable | unresolved |

Limitations:

- C01: Difference +163 probes. Coverage is platform-wide, not cohort-specific, and higher coverage is not evidence of biological validity.
- C02: Gene counts include genes whose only probes are replacement-derived (Option A) or matched by unversioned accession (accession route); measurability in a cohort is not assessed.
- C03: Multiple probes per gene are expected under G3 and are neither good nor bad in themselves; their effect depends on probe concordance in the cohort.
- C04: Agreement between two annotation routes is not biological confirmation; both may share upstream sources.
- C05: M1 and M2 are different metrics; their totals must not be compared directly. Replacement agreement shows the two routes converge on the same current ID, not that the probe measures it.
- C06: Which route is correct for a discordant probe cannot be decided from annotation tables; sequence-level evidence would be required.
- C07: Absence of a current mapping does not establish that a probe is non-functional; an accession absent from org.Hs.eg.db is not proof of retirement.
- C08: The two ambiguity definitions differ (package multi-mapping vs union of accession matches) and are not the same probes.
- C09: Includes control/non-gene probes in both routes; the share relevant to any cohort depends on Series Matrix content (not assessed).
- C10: Single-route probes have no cross-check; their validity is the least supported.
- C11: Option A's probe-to-gene knowledge predates the reference snapshot; the accession route's accessions are as old as the package build. Newer is not automatically more accurate.
- C12: An accession match shows the identifiers are linked in NCBI records, not that the probe sequence hybridizes to the current transcript.
- C13: Successor genes and historical source genes are different counts. Collisions are flagged, never merged; under G3 the replaced probes would join the successor gene's average.
- C14: Effects on expression estimates require cohort data (probe presence, D17 rule, probe concordance) and are not assessed here.
- C15: Requires the cohort's authorized Series Matrix probe list; no GEO data used. Platform-wide counts are not cohort coverage.

## illuminaHumanv4 (GSE63061)

| ID | Criterion | Option A | Accession route | Advantage (this criterion only) | Status |
|---|---|---|---|---|---|
| C01 | Probes assigned exactly one eligible gene (denominator: all platform probes) | 34,038 / 48,107 (70.75%) | 33,811 / 48,107 (70.28%) | Option A | supportive |
| C02 | Distinct current Entrez genes represented (gene level) | 20,926 | 20,779 (both routes 20,759; Option A only 167; accession only 20) | Option A | supportive |
| C03 | Genes represented by more than one eligible probe (gene level; G3 averages them) | 7,678 | 7,620 (computed in this matrix from retained sources; not reported in v3) | neither | unresolved |
| C04 | M1 — same-probe agreement (probes both routes assign; vs the post-gene-history Option A gene) | both assign 33,761 | concordant 33,745 (99.95% of 33,761); discordant 16 | neither | supportive |
| C05 | ID-replacement effects (M2 → M1 transitions; M2 = vs the package's original Entrez ID) | 76 probes assigned via a gene-history successor | M2 total 33,761 vs M1 total 33,761; 48 probes 'different' under M2 become concordant under M1 after replacement; 0 probes are in M2 but not M1 | neither | supportive |
| C06 | Genuine disagreements (M1 discordant probes) | 16 probes assign a different gene than the accession route | same probes | not determinable | unresolved |
| C07 | Discontinued IDs without replacement / unexplained (Option A); unmatched accessions (accession route) | no replacement 122; unexplained 0 | accession unmatched 2,390; no accession 10,226 | not determinable | unresolved |
| C08 | Ambiguous assignments (one probe → more than one gene; excluded under both routes) | multi-gene probes in package 1,726 | accession ambiguous 1,680 | accession route | supportive |
| C09 | Unresolved probes (no eligible assignment; denominator: all probes) | 14,069 (29.25%), incl. 12,221 with no package gene | 14,296 (29.72%), incl. 12,616 without a matched accession | Option A | supportive |
| C10 | Probes assigned by only one route | Option A only: 277 (accession unresolved 267; accession ambiguous 10) | accession only: 50 | Option A | supportive |
| C11 | Probe-to-gene source, version, provenance and age | illuminaHumanv4 package Entrez source date: 2015-Mar17; reconciled to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) by the approved gene-history procedure | manufacturer accessions from the package matched to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) | accession route | supportive |
| C12 | Accession-matching limitations | not applicable (Option A uses package gene assignments) | 0 accession values carry a version; matching is on unversioned roots; 14,399 probes carry >1 accession | not determinable | unresolved |
| C13 | Successor collisions (Option A; replaced probe joins a gene that already has directly mapped probes) | probes 50; distinct successor genes 32; distinct historical source genes 35 | not applicable (no history step) | not determinable | unresolved |
| C14 | Downstream consequences for gene-level (G3) aggregation | probes per gene and collisions determine each gene's average; replacement-derived probes enter successor genes | ambiguous probes are lost; single-gene accession probes define the gene averages | not determinable | unresolved |
| C15 | Presence of probes in the cohort's Series Matrix | NOT ASSESSED | NOT ASSESSED | not determinable | unresolved |

Limitations:

- C01: Difference +227 probes. Coverage is platform-wide, not cohort-specific, and higher coverage is not evidence of biological validity.
- C02: Gene counts include genes whose only probes are replacement-derived (Option A) or matched by unversioned accession (accession route); measurability in a cohort is not assessed.
- C03: Multiple probes per gene are expected under G3 and are neither good nor bad in themselves; their effect depends on probe concordance in the cohort.
- C04: Agreement between two annotation routes is not biological confirmation; both may share upstream sources.
- C05: M1 and M2 are different metrics; their totals must not be compared directly. Replacement agreement shows the two routes converge on the same current ID, not that the probe measures it.
- C06: Which route is correct for a discordant probe cannot be decided from annotation tables; sequence-level evidence would be required.
- C07: Absence of a current mapping does not establish that a probe is non-functional; an accession absent from org.Hs.eg.db is not proof of retirement.
- C08: The two ambiguity definitions differ (package multi-mapping vs union of accession matches) and are not the same probes.
- C09: Includes control/non-gene probes in both routes; the share relevant to any cohort depends on Series Matrix content (not assessed).
- C10: Single-route probes have no cross-check; their validity is the least supported.
- C11: Option A's probe-to-gene knowledge predates the reference snapshot; the accession route's accessions are as old as the package build. Newer is not automatically more accurate.
- C12: An accession match shows the identifiers are linked in NCBI records, not that the probe sequence hybridizes to the current transcript.
- C13: Successor genes and historical source genes are different counts. Collisions are flagged, never merged; under G3 the replaced probes would join the successor gene's average.
- C14: Effects on expression estimates require cohort data (probe presence, D17 rule, probe concordance) and are not assessed here.
- C15: Requires the cohort's authorized Series Matrix probe list; no GEO data used. Platform-wide counts are not cohort coverage.

## lumi HT-12 v4 R2 (GSE140829 applicability unverified (D19))

| ID | Criterion | Option A | Accession route | Advantage (this criterion only) | Status |
|---|---|---|---|---|---|
| C01 | Probes assigned exactly one eligible gene (denominator: all platform probes) | 37,491 / 47,323 (79.22%) | 31,130 / 47,323 (65.78%) | Option A | supportive |
| C02 | Distinct current Entrez genes represented (gene level) | 23,743 | 20,593 (both routes 20,356; Option A only 3,387; accession only 237) | Option A | supportive |
| C03 | Genes represented by more than one eligible probe (gene level; G3 averages them) | 8,600 | 6,873 (computed in this matrix from retained sources; not reported in v3) | neither | unresolved |
| C04 | M1 — same-probe agreement (probes both routes assign; vs the post-gene-history Option A gene) | both assign 30,677 | concordant 30,640 (99.88% of 30,677); discordant 37 | neither | supportive |
| C05 | ID-replacement effects (M2 → M1 transitions; M2 = vs the package's original Entrez ID) | 1,760 probes assigned via a gene-history successor | M2 total 30,679 vs M1 total 30,677; 244 probes 'different' under M2 become concordant under M1 after replacement; 2 probes are in M2 but not M1 | neither | supportive |
| C06 | Genuine disagreements (M1 discordant probes) | 37 probes assign a different gene than the accession route | same probes | not determinable | unresolved |
| C07 | Discontinued IDs without replacement / unexplained (Option A); unmatched accessions (accession route) | no replacement 6,468; unexplained 1 | accession unmatched 16,193; no accession 0 | not determinable | unresolved |
| C08 | Ambiguous assignments (one probe → more than one gene; excluded under both routes) | multi-gene probes in package 0 | accession ambiguous 0 | neither | supportive |
| C09 | Unresolved probes (no eligible assignment; denominator: all probes) | 9,832 (20.78%), incl. 3,363 with no package gene | 16,193 (34.22%), incl. 16,193 without a matched accession | Option A | supportive |
| C10 | Probes assigned by only one route | Option A only: 6,814 (accession unresolved 6,814; accession ambiguous 0) | accession only: 453 | Option A | supportive |
| C11 | Probe-to-gene source, version, provenance and age | lumi HT-12 v4 R2 package Entrez source date: not recorded (REFSEQ VERSION: not recorded); reconciled to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) by the approved gene-history procedure | manufacturer accessions from the package matched to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) | not determinable | supportive |
| C12 | Accession-matching limitations | not applicable (Option A uses package gene assignments) | 0 accession values carry a version; matching is on unversioned roots; 0 probes carry >1 accession | not determinable | unresolved |
| C13 | Successor collisions (Option A; replaced probe joins a gene that already has directly mapped probes) | probes 1,165; distinct successor genes 783; distinct historical source genes 892 | not applicable (no history step) | not determinable | unresolved |
| C14 | Downstream consequences for gene-level (G3) aggregation | probes per gene and collisions determine each gene's average; replacement-derived probes enter successor genes | ambiguous probes are lost; single-gene accession probes define the gene averages | not determinable | unresolved |
| C15 | Presence of probes in the cohort's Series Matrix | NOT ASSESSED | NOT ASSESSED | not determinable | unresolved |

Limitations:

- C01: Difference +6,361 probes. Coverage is platform-wide, not cohort-specific, and higher coverage is not evidence of biological validity.
- C02: Gene counts include genes whose only probes are replacement-derived (Option A) or matched by unversioned accession (accession route); measurability in a cohort is not assessed.
- C03: Multiple probes per gene are expected under G3 and are neither good nor bad in themselves; their effect depends on probe concordance in the cohort.
- C04: Agreement between two annotation routes is not biological confirmation; both may share upstream sources.
- C05: M1 and M2 are different metrics; their totals must not be compared directly. Replacement agreement shows the two routes converge on the same current ID, not that the probe measures it.
- C06: Which route is correct for a discordant probe cannot be decided from annotation tables; sequence-level evidence would be required.
- C07: Absence of a current mapping does not establish that a probe is non-functional; an accession absent from org.Hs.eg.db is not proof of retirement.
- C08: The two ambiguity definitions differ (package multi-mapping vs union of accession matches) and are not the same probes.
- C09: Includes control/non-gene probes in both routes; the share relevant to any cohort depends on Series Matrix content (not assessed).
- C10: Single-route probes have no cross-check; their validity is the least supported.
- C11: Option A's probe-to-gene knowledge predates the reference snapshot; the accession route's accessions are as old as the package build. Newer is not automatically more accurate.
- C12: An accession match shows the identifiers are linked in NCBI records, not that the probe sequence hybridizes to the current transcript.
- C13: Successor genes and historical source genes are different counts. Collisions are flagged, never merged; under G3 the replaced probes would join the successor gene's average.
- C14: Effects on expression estimates require cohort data (probe presence, D17 rule, probe concordance) and are not assessed here.
- C15: Requires the cohort's authorized Series Matrix probe list; no GEO data used. Platform-wide counts are not cohort coverage. GSE140829 applicability of the HT-12 v4 R2 table is restricted by D19.

## Conclusions

**Established by the retained evidence**

- On probes both routes assign, they agree for 99.88–99.97% (M1), separately on each platform.
- Option A assigns more probes and genes than the accession route on every platform; the gap is small for illuminaHumanv3/v4 and large for the lumi HT-12 v4 R2 table.
- Most M2 disagreements on lumi are resolved by gene-history replacement; the remaining genuine disagreements are the M1 discordant probes listed in v3/metric_reconciliation_probes.tsv.

**Suggested but not established**

- That Option A's extra coverage reflects valid probe-to-gene relationships (it rests on older package assignments and, for lumi, on many replacements and collisions).
- That the accession route is more current in a biologically meaningful way (unversioned accession matches do not confirm the probe targets the current transcript).

**Unknown**

- Which route is correct for each discordant or single-route probe.
- Cohort-specific coverage (probe presence in each Series Matrix), the D17 feature rule, and the effect of either route on gene-level estimates.
- Whether the lumi HT-12 v4 R2 table applies to GSE140829 (D19).

**Evidence required before a policy decision**

- Probe presence in each cohort's authorized Series Matrix (GSE63060, GSE63061; GSE140829 after D19).
- The D17 feature-rule decision.
- A decision on how discordant and single-route probes are treated, and whether sequence-level evidence (e.g. the packages' re-annotation fields) should be considered.

## Not yet assessed / unresolved

- Probe presence in cohort inputs (no GEO data used); D17; the Illumina mapping policy; D19 (GSE140829); any biological validation beyond annotation agreement.

## Validation

- [OK] illuminaHumanv3: recomputed accession unique probes equals v3 manifest
- [OK] illuminaHumanv3: recomputed accession distinct genes equals v3 manifest
- [OK] illuminaHumanv3: recomputed accession classes equals v3 manifest
- [OK] illuminaHumanv3: recomputed M1 both / concordant / discordant equals v3 manifest
- [OK] illuminaHumanv3: recomputed M1/M2 reconciliation equals v3 manifest
- [OK] illuminaHumanv3: recomputed gene overlap equals v3 manifest
- [OK] illuminaHumanv3: recomputed M2 same / different equals v3 manifest
- [OK] illuminaHumanv3: metric_reconciliation_probes.tsv transitions equal v3 manifest
- [OK] illuminaHumanv4: recomputed accession unique probes equals v3 manifest
- [OK] illuminaHumanv4: recomputed accession distinct genes equals v3 manifest
- [OK] illuminaHumanv4: recomputed accession classes equals v3 manifest
- [OK] illuminaHumanv4: recomputed M1 both / concordant / discordant equals v3 manifest
- [OK] illuminaHumanv4: recomputed M1/M2 reconciliation equals v3 manifest
- [OK] illuminaHumanv4: recomputed gene overlap equals v3 manifest
- [OK] illuminaHumanv4: recomputed M2 same / different equals v3 manifest
- [OK] illuminaHumanv4: metric_reconciliation_probes.tsv transitions equal v3 manifest
- [OK] lumi HT-12 v4 R2: recomputed accession unique probes equals v3 manifest
- [OK] lumi HT-12 v4 R2: recomputed accession distinct genes equals v3 manifest
- [OK] lumi HT-12 v4 R2: recomputed accession classes equals v3 manifest
- [OK] lumi HT-12 v4 R2: recomputed M1 both / concordant / discordant equals v3 manifest
- [OK] lumi HT-12 v4 R2: recomputed M1/M2 reconciliation equals v3 manifest
- [OK] lumi HT-12 v4 R2: recomputed gene overlap equals v3 manifest
- [OK] lumi HT-12 v4 R2: recomputed M2 same / different equals v3 manifest
- [OK] lumi HT-12 v4 R2: metric_reconciliation_probes.tsv transitions equal v3 manifest
- [OK] every platform has every criterion
- [OK] statuses and advantages use the allowed vocabularies
- [OK] no criterion is marked decisive without justification

## Package source dates (read from retained package databases)

- illuminaHumanv3.db_1.26.0.tar.gz: EGSOURCEDATE=2015-Mar17; EGSOURCENAME=Entrez Gene; CHIPNAME=HumanHT12v3
- illuminaHumanv4.db_1.26.0.tar.gz: EGSOURCEDATE=2015-Mar17; EGSOURCENAME=Entrez Gene; CHIPNAME=HumanHT12v4
- lumiHumanIDMapping_1.10.1.tar.gz: REFSEQ VERSION=not recorded
- org.Hs.eg.db_3.23.1.tar.gz: EGSOURCEDATE=2026-Mar18; EGSOURCENAME=Entrez Gene
