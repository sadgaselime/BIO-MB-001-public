# Illumina annotation-route decision matrix — v2

**Assessment only. No Illumina mapping policy is selected, recommended or approved.** No weighting or ranking is applied. GSE140829 remains governed by D19; D17 (expression/feature filter) is unresolved. Supersedes the presentation of v1 (retained unchanged) following REVIEW_v1.md; no v1 figure changed.

## Definitions

- **Option A:** package Entrez IDs reconciled to org.Hs.eg.db 3.23.1 by the NCBI gene-history procedure (View A, cutoff 20260318). The procedure is approved for GPL570 only (D6-F); approval for GPL570 does not approve it for any Illumina platform, where Option A is provisional.
- **Accession route:** probe accessions matched (unversioned) to org.Hs.eg.db 3.23.1 GenBank accessions ∪ RefSeq; only a unique match is an assignment.
- **M1:** probes both routes assign; agreement judged against the post-gene-history Option A gene. **M2:** probes with one package Entrez ID and a unique accession-route gene; agreement judged against the package's original ID. M1 ⊆ M2; the two totals are different metrics and are not compared. Probe-level labels follow v3/metric_reconciliation_probes.tsv.
- **Denominators:** probe-level percentages use all probes of the platform table (lumi: rows of HumanHT12_V4_0_R2_15002873_B); M1 agreement uses the M1 total; gene-level counts are distinct current Entrez IDs. Historical source genes and successor genes are counted separately.
- **Advantage:** which route, if either, is better on that criterion alone. Advantage entries are not independent and must not be counted or summed; C09 and C10 restate C01 and are marked 'restates C01 (not counted)'.
- **Status:** *decisive* = settles the choice on its own (none qualify); *supportive* = informative evidence that does not settle the choice; *unresolved* = the comparative merit cannot be judged from retained evidence. Every criterion whose advantage is 'not determinable' is *unresolved*.
- **Reconstruction:** *full* = recomputed here from retained raw sources; *partial* = the Option A side depends on the retained gene-history v1 records, whose raw NCBI source is not retained.

## illuminaHumanv3 — GSE63060

| ID | Criterion | Option A | Accession route | Joint (same probes) | Advantage (this criterion only) | Status |
|---|---|---|---|---|---|---|
| C01 | Probes assigned exactly one eligible gene (denominator: all platform probes) | 29,489 / 49,576 (59.48%) | 29,326 / 49,576 (59.15%) | difference +163 probes (Option A − accession route) | Option A | supportive |
| C02 | Distinct current Entrez genes represented (gene level) | 19,226 | 19,100 | both routes 19,085; Option A only 141; accession only 15; difference +126 genes | Option A | supportive |
| C03 | Genes represented by more than one eligible probe (gene level; G3 averages them) | 6,554 of 19,226 genes | 6,531 of 19,100 genes (new in the decision matrix; verified by two independently built accession maps and by probe/gene totals) | — | neither | unresolved |
| C04 | M1 — same-probe agreement (probes both routes assign; judged against the post-gene-history Option A gene) | — (joint metric) | — (joint metric) | both assign 29,294; concordant 29,284 (99.97% of 29,294); discordant 10 | neither | supportive |
| C05 | ID-replacement effects (M2 → M1 transitions; M2 = agreement with the package's original Entrez ID) | 59 probes assigned via a gene-history successor (all probes, not only M1) | — (no history step) | M2 total 29,294; M1 total 29,294 (different metrics). Of 50 M2 'different' probes: 40 concordant under M1 after replacement; 0 replacement-derived and still discordant; 10 discordant with a direct assignment; 0 outside M1 (Option A not eligible) | neither | supportive |
| C06 | Genuine disagreements (M1 discordant probes) | — (joint metric) | — (joint metric) | 10 probes: 10 eligible_direct (Option A class); listed in v3/metric_reconciliation_probes.tsv | not determinable | unresolved |
| C07 | Option A: package IDs with no current gene (no replacement / unexplained); accession route: no accession or unmatched accessions | no replacement 62 (discontinued_no_replacement 62; chain_ends_no_replacement 0); unexplained 0 | accession unmatched 1,379; no accession 17,719 | — | not determinable | unresolved |
| C08 | Ambiguous probes (>1 candidate gene under the route's own mapping; each route excludes the probes it finds ambiguous) | package lists >1 Entrez ID: 1,175 (excluded before gene-history reconciliation) | accession matches >1 current gene: 1,152 | same probes: ambiguous under both 1,142; package only 33 (accession route assigns 32 of them uniquely); accession only 10 (package lists exactly one Entrez ID for 10 of them) | not determinable | unresolved |
| C09 | Unresolved probes (no eligible assignment; denominator: all platform probes) | 20,087 / 49,576 (40.52%), incl. 18,850 with no package gene | 20,250 / 49,576 (40.85%), incl. 19,098 with no matched accession | = all probes − C01 assigned; difference +163 (accession route − Option A) equals the C01 difference | restates C01 (not counted) | supportive |
| C10 | Probes assigned by only one route (no cross-check) | Option A only: 195 (accession unresolved 185; accession ambiguous 10) | accession only: 32 | difference +163 equals the C01 difference | restates C01 (not counted) | supportive |
| C11 | Probe-to-gene source, version, provenance and age (provenance context) | package Entrez source date 2015-Mar17 (metadata EGSOURCEDATE); package built 2015-04-07 15:19:38 UTC (DESCRIPTION 'Packaged'); IDs reconciled to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) with the gene-history procedure (approved under D6-F for GPL570 only; its use for Illumina platforms is not approved and is provisional here) | probe accessions from the same package build matched to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18; built 2026-03-23 01:48:12 UTC) | — | not determinable | unresolved |
| C12 | Accession-matching limitations | not applicable (Option A uses package gene assignments) | 0 of 57,382 accession values carry a version suffix; matching is on unversioned roots; 12,377 probes carry >1 accession | — | not determinable | unresolved |
| C13 | Successor collisions (Option A; a replacement-derived probe joins a gene that already has directly mapped probes) | probes 43; distinct successor genes 28; distinct historical source genes 30 | not applicable (no history step) | — | not determinable | unresolved |
| C14 | Downstream consequences for gene-level (G3) aggregation | probes per gene and collisions determine each gene's average; replacement-derived probes enter successor genes | ambiguous probes are lost; single-gene accession probes define the gene averages | — | not determinable | unresolved |
| C15 | Presence of probes in the cohort's Series Matrix | NOT ASSESSED | NOT ASSESSED | NOT ASSESSED | not determinable | unresolved |

Limitations and reconstruction:

- C01: This is the single platform-wide coverage difference; C09 and C10 restate it and are not separate advantages. Coverage is not cohort-specific, and higher coverage is not evidence of biological validity. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C02: Gene-level counterpart of C01: related to probe coverage but not an arithmetic restatement of it. Includes genes whose only probes are replacement-derived (Option A) or matched by unversioned accession (accession route); measurability in a cohort is not assessed. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C03: Multiple probes per gene are expected under G3 and are neither good nor bad in themselves; their effect depends on probe concordance in the cohort. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C04: Agreement between two annotation routes is not biological confirmation; both may share upstream sources. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C05: M1 and M2 are different metrics; their totals are not compared. Labels follow v3/metric_reconciliation_probes.tsv (M2_result different; M1_result concordant / discordant / not_in_M1). Replacement agreement shows the two routes converge on the same current ID, not that the probe measures it. *Reconstruction: partial: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C06: Which route is correct for a discordant probe cannot be decided from annotation tables; sequence-level evidence would be required. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C07: Absence of a current mapping does not establish that a probe is non-functional; an accession absent from org.Hs.eg.db is not proof of retirement. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C08: The two definitions differ (package multi-mapping of 2015-era IDs vs union of current genes over a probe's accessions), so their totals are not a like-for-like quality measure. *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs).*
- C09: Arithmetic complement of C01, not an independent advantage. Includes control/non-gene probes; the share relevant to a cohort depends on Series Matrix content (not assessed). *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C10: The difference restates C01. Single-route probes have no cross-check; their validity is the least supported. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C11: Annotation age is provenance context, not evidence of biological accuracy: a newer gene-ID snapshot does not show that a probe measures the current transcript, and the accession route's probe accessions are as old as the package build. Option A replacement-dependent figures trace to the retained gene-history v1 records (the human records the audit used, kept verbatim in gene_history_reconciliation.tsv); the raw NCBI gene_history.gz (SHA-256 bcb85c8f…) is not retained and cannot be re-obtained byte-identically (ncbi_gene_history/SOURCE_RETENTION.md). *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs) (dates); Option A history step: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C12: An accession match shows the identifiers are linked in NCBI records, not that the probe sequence hybridizes to the current transcript. *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs).*
- C13: Successor genes and historical source genes are different counts. Collisions are flagged, never merged; under G3 the replaced probes would join the successor gene's average. *Reconstruction: partial: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C14: Effects on expression estimates require cohort data (probe presence, D17 (expression/feature filter), probe concordance) and are not assessed here. *Reconstruction: not applicable (qualitative).*
- C15: Requires the cohort's authorized Series Matrix probe list; no GEO data used. Platform-wide counts are not cohort coverage. *Reconstruction: not assessed.*

## illuminaHumanv4 — GSE63061

| ID | Criterion | Option A | Accession route | Joint (same probes) | Advantage (this criterion only) | Status |
|---|---|---|---|---|---|---|
| C01 | Probes assigned exactly one eligible gene (denominator: all platform probes) | 34,038 / 48,107 (70.75%) | 33,811 / 48,107 (70.28%) | difference +227 probes (Option A − accession route) | Option A | supportive |
| C02 | Distinct current Entrez genes represented (gene level) | 20,926 | 20,779 | both routes 20,759; Option A only 167; accession only 20; difference +147 genes | Option A | supportive |
| C03 | Genes represented by more than one eligible probe (gene level; G3 averages them) | 7,678 of 20,926 genes | 7,620 of 20,779 genes (new in the decision matrix; verified by two independently built accession maps and by probe/gene totals) | — | neither | unresolved |
| C04 | M1 — same-probe agreement (probes both routes assign; judged against the post-gene-history Option A gene) | — (joint metric) | — (joint metric) | both assign 33,761; concordant 33,745 (99.95% of 33,761); discordant 16 | neither | supportive |
| C05 | ID-replacement effects (M2 → M1 transitions; M2 = agreement with the package's original Entrez ID) | 76 probes assigned via a gene-history successor (all probes, not only M1) | — (no history step) | M2 total 33,761; M1 total 33,761 (different metrics). Of 64 M2 'different' probes: 48 concordant under M1 after replacement; 0 replacement-derived and still discordant; 16 discordant with a direct assignment; 0 outside M1 (Option A not eligible) | neither | supportive |
| C06 | Genuine disagreements (M1 discordant probes) | — (joint metric) | — (joint metric) | 16 probes: 16 eligible_direct (Option A class); listed in v3/metric_reconciliation_probes.tsv | not determinable | unresolved |
| C07 | Option A: package IDs with no current gene (no replacement / unexplained); accession route: no accession or unmatched accessions | no replacement 122 (discontinued_no_replacement 122; chain_ends_no_replacement 0); unexplained 0 | accession unmatched 2,390; no accession 10,226 | — | not determinable | unresolved |
| C08 | Ambiguous probes (>1 candidate gene under the route's own mapping; each route excludes the probes it finds ambiguous) | package lists >1 Entrez ID: 1,726 (excluded before gene-history reconciliation) | accession matches >1 current gene: 1,680 | same probes: ambiguous under both 1,670; package only 56 (accession route assigns 50 of them uniquely); accession only 10 (package lists exactly one Entrez ID for 10 of them) | not determinable | unresolved |
| C09 | Unresolved probes (no eligible assignment; denominator: all platform probes) | 14,069 / 48,107 (29.25%), incl. 12,221 with no package gene | 14,296 / 48,107 (29.72%), incl. 12,616 with no matched accession | = all probes − C01 assigned; difference +227 (accession route − Option A) equals the C01 difference | restates C01 (not counted) | supportive |
| C10 | Probes assigned by only one route (no cross-check) | Option A only: 277 (accession unresolved 267; accession ambiguous 10) | accession only: 50 | difference +227 equals the C01 difference | restates C01 (not counted) | supportive |
| C11 | Probe-to-gene source, version, provenance and age (provenance context) | package Entrez source date 2015-Mar17 (metadata EGSOURCEDATE); package built 2015-04-07 15:39:45 UTC (DESCRIPTION 'Packaged'); IDs reconciled to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) with the gene-history procedure (approved under D6-F for GPL570 only; its use for Illumina platforms is not approved and is provisional here) | probe accessions from the same package build matched to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18; built 2026-03-23 01:48:12 UTC) | — | not determinable | unresolved |
| C12 | Accession-matching limitations | not applicable (Option A uses package gene assignments) | 0 of 68,113 accession values carry a version suffix; matching is on unversioned roots; 14,399 probes carry >1 accession | — | not determinable | unresolved |
| C13 | Successor collisions (Option A; a replacement-derived probe joins a gene that already has directly mapped probes) | probes 50; distinct successor genes 32; distinct historical source genes 35 | not applicable (no history step) | — | not determinable | unresolved |
| C14 | Downstream consequences for gene-level (G3) aggregation | probes per gene and collisions determine each gene's average; replacement-derived probes enter successor genes | ambiguous probes are lost; single-gene accession probes define the gene averages | — | not determinable | unresolved |
| C15 | Presence of probes in the cohort's Series Matrix | NOT ASSESSED | NOT ASSESSED | NOT ASSESSED | not determinable | unresolved |

Limitations and reconstruction:

- C01: This is the single platform-wide coverage difference; C09 and C10 restate it and are not separate advantages. Coverage is not cohort-specific, and higher coverage is not evidence of biological validity. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C02: Gene-level counterpart of C01: related to probe coverage but not an arithmetic restatement of it. Includes genes whose only probes are replacement-derived (Option A) or matched by unversioned accession (accession route); measurability in a cohort is not assessed. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C03: Multiple probes per gene are expected under G3 and are neither good nor bad in themselves; their effect depends on probe concordance in the cohort. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C04: Agreement between two annotation routes is not biological confirmation; both may share upstream sources. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C05: M1 and M2 are different metrics; their totals are not compared. Labels follow v3/metric_reconciliation_probes.tsv (M2_result different; M1_result concordant / discordant / not_in_M1). Replacement agreement shows the two routes converge on the same current ID, not that the probe measures it. *Reconstruction: partial: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C06: Which route is correct for a discordant probe cannot be decided from annotation tables; sequence-level evidence would be required. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C07: Absence of a current mapping does not establish that a probe is non-functional; an accession absent from org.Hs.eg.db is not proof of retirement. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C08: The two definitions differ (package multi-mapping of 2015-era IDs vs union of current genes over a probe's accessions), so their totals are not a like-for-like quality measure. *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs).*
- C09: Arithmetic complement of C01, not an independent advantage. Includes control/non-gene probes; the share relevant to a cohort depends on Series Matrix content (not assessed). *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C10: The difference restates C01. Single-route probes have no cross-check; their validity is the least supported. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C11: Annotation age is provenance context, not evidence of biological accuracy: a newer gene-ID snapshot does not show that a probe measures the current transcript, and the accession route's probe accessions are as old as the package build. Option A replacement-dependent figures trace to the retained gene-history v1 records (the human records the audit used, kept verbatim in gene_history_reconciliation.tsv); the raw NCBI gene_history.gz (SHA-256 bcb85c8f…) is not retained and cannot be re-obtained byte-identically (ncbi_gene_history/SOURCE_RETENTION.md). *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs) (dates); Option A history step: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C12: An accession match shows the identifiers are linked in NCBI records, not that the probe sequence hybridizes to the current transcript. *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs).*
- C13: Successor genes and historical source genes are different counts. Collisions are flagged, never merged; under G3 the replaced probes would join the successor gene's average. *Reconstruction: partial: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C14: Effects on expression estimates require cohort data (probe presence, D17 (expression/feature filter), probe concordance) and are not assessed here. *Reconstruction: not applicable (qualitative).*
- C15: Requires the cohort's authorized Series Matrix probe list; no GEO data used. Platform-wide counts are not cohort coverage. *Reconstruction: not assessed.*

## lumi HT-12 v4 R2 — GSE140829 applicability unverified (D19)

| ID | Criterion | Option A | Accession route | Joint (same probes) | Advantage (this criterion only) | Status |
|---|---|---|---|---|---|---|
| C01 | Probes assigned exactly one eligible gene (denominator: all platform probes) | 37,491 / 47,323 (79.22%) | 31,130 / 47,323 (65.78%) | difference +6,361 probes (Option A − accession route) | Option A | supportive |
| C02 | Distinct current Entrez genes represented (gene level) | 23,743 | 20,593 | both routes 20,356; Option A only 3,387; accession only 237; difference +3,150 genes | Option A | supportive |
| C03 | Genes represented by more than one eligible probe (gene level; G3 averages them) | 8,600 of 23,743 genes | 6,873 of 20,593 genes (new in the decision matrix; verified by two independently built accession maps and by probe/gene totals) | — | neither | unresolved |
| C04 | M1 — same-probe agreement (probes both routes assign; judged against the post-gene-history Option A gene) | — (joint metric) | — (joint metric) | both assign 30,677; concordant 30,640 (99.88% of 30,677); discordant 37 | neither | supportive |
| C05 | ID-replacement effects (M2 → M1 transitions; M2 = agreement with the package's original Entrez ID) | 1,760 probes assigned via a gene-history successor (all probes, not only M1) | — (no history step) | M2 total 30,679; M1 total 30,677 (different metrics). Of 283 M2 'different' probes: 244 concordant under M1 after replacement; 5 replacement-derived and still discordant; 32 discordant with a direct assignment; 2 outside M1 (Option A not eligible: ILMN_1712269 [discontinued_no_replacement], ILMN_3239440 [discontinued_no_replacement]) | neither | supportive |
| C06 | Genuine disagreements (M1 discordant probes) | — (joint metric) | — (joint metric) | 37 probes: 32 eligible_direct; 5 eligible_via_history_replacement (Option A class); listed in v3/metric_reconciliation_probes.tsv | not determinable | unresolved |
| C07 | Option A: package IDs with no current gene (no replacement / unexplained); accession route: no accession or unmatched accessions | no replacement 6,468 (discontinued_no_replacement 6,032; chain_ends_no_replacement 436); unexplained 1 | accession unmatched 16,193; no accession 0 | — | not determinable | unresolved |
| C08 | Ambiguous probes (>1 candidate gene under the route's own mapping; each route excludes the probes it finds ambiguous) | package lists >1 Entrez ID: 0 (excluded before gene-history reconciliation) | accession matches >1 current gene: 0 | same probes: ambiguous under both 0; package only 0 (accession route assigns 0 of them uniquely); accession only 0 (package lists exactly one Entrez ID for 0 of them) | not determinable | unresolved |
| C09 | Unresolved probes (no eligible assignment; denominator: all platform probes) | 9,832 / 47,323 (20.78%), incl. 3,363 with no package gene | 16,193 / 47,323 (34.22%), incl. 16,193 with no matched accession | = all probes − C01 assigned; difference +6,361 (accession route − Option A) equals the C01 difference | restates C01 (not counted) | supportive |
| C10 | Probes assigned by only one route (no cross-check) | Option A only: 6,814 (accession unresolved 6,814; accession ambiguous 0) | accession only: 453 | difference +6,361 equals the C01 difference | restates C01 (not counted) | supportive |
| C11 | Probe-to-gene source, version, provenance and age (provenance context) | Entrez/accession content date not recorded (metadata REFSEQ VERSION: blank (raw value ' ')); lumiHumanIDMapping 1.10.1 package built 2016-04-21 13:21:07 UTC (DESCRIPTION 'Packaged'; a build date, not a mapping-content date); IDs reconciled to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18) with the gene-history procedure (approved under D6-F for GPL570 only; its use for Illumina platforms is not approved and is provisional here) | probe accessions from the same package build matched to org.Hs.eg.db 3.23.1 (Entrez Gene 2026-Mar18; built 2026-03-23 01:48:12 UTC) | — | not determinable | unresolved |
| C12 | Accession-matching limitations | not applicable (Option A uses package gene assignments) | 0 of 47,323 accession values carry a version suffix; matching is on unversioned roots; 0 probes carry >1 accession | — | not determinable | unresolved |
| C13 | Successor collisions (Option A; a replacement-derived probe joins a gene that already has directly mapped probes) | probes 1,165; distinct successor genes 783; distinct historical source genes 892 | not applicable (no history step) | — | not determinable | unresolved |
| C14 | Downstream consequences for gene-level (G3) aggregation | probes per gene and collisions determine each gene's average; replacement-derived probes enter successor genes | ambiguous probes are lost; single-gene accession probes define the gene averages | — | not determinable | unresolved |
| C15 | Presence of probes in the cohort's Series Matrix | NOT ASSESSED | NOT ASSESSED | NOT ASSESSED | not determinable | unresolved |

Limitations and reconstruction:

- C01: This is the single platform-wide coverage difference; C09 and C10 restate it and are not separate advantages. Coverage is not cohort-specific, and higher coverage is not evidence of biological validity. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C02: Gene-level counterpart of C01: related to probe coverage but not an arithmetic restatement of it. Includes genes whose only probes are replacement-derived (Option A) or matched by unversioned accession (accession route); measurability in a cohort is not assessed. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C03: Multiple probes per gene are expected under G3 and are neither good nor bad in themselves; their effect depends on probe concordance in the cohort. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C04: Agreement between two annotation routes is not biological confirmation; both may share upstream sources. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C05: M1 and M2 are different metrics; their totals are not compared. Labels follow v3/metric_reconciliation_probes.tsv (M2_result different; M1_result concordant / discordant / not_in_M1). Replacement agreement shows the two routes converge on the same current ID, not that the probe measures it. *Reconstruction: partial: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C06: Which route is correct for a discordant probe cannot be decided from annotation tables; sequence-level evidence would be required. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C07: Absence of a current mapping does not establish that a probe is non-functional; an accession absent from org.Hs.eg.db is not proof of retirement. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C08: The two definitions differ (package multi-mapping of 2015-era IDs vs union of current genes over a probe's accessions), so their totals are not a like-for-like quality measure. For this table both counts are zero by construction: lumiHumanIDMapping stores one EntrezID and one Accession field per nuID (one row per nuID; no multi-value separators), so ambiguity cannot be represented. The zero is a property of the source representation, not evidence that ambiguity is absent biologically. *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs).*
- C09: Arithmetic complement of C01, not an independent advantage. Includes control/non-gene probes; the share relevant to a cohort depends on Series Matrix content (not assessed). *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C10: The difference restates C01. Single-route probes have no cross-check; their validity is the least supported. *Reconstruction: partial: accession-route side full; Option A side depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C11: Annotation age is provenance context, not evidence of biological accuracy: a newer gene-ID snapshot does not show that a probe measures the current transcript, and the accession route's probe accessions are as old as the package build. Option A replacement-dependent figures trace to the retained gene-history v1 records (the human records the audit used, kept verbatim in gene_history_reconciliation.tsv); the raw NCBI gene_history.gz (SHA-256 bcb85c8f…) is not retained and cannot be re-obtained byte-identically (ncbi_gene_history/SOURCE_RETENTION.md). *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs) (dates); Option A history step: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C12: An accession match shows the identifiers are linked in NCBI records, not that the probe sequence hybridizes to the current transcript. One accession per nuID by construction (see C08). *Reconstruction: full: recomputed from retained raw sources (package and org.Hs.eg.db tarballs).*
- C13: Successor genes and historical source genes are different counts. Collisions are flagged, never merged; under G3 the replaced probes would join the successor gene's average. *Reconstruction: partial: depends on the retained gene-history v1 records (raw NCBI gene_history.gz not retained, so those records cannot be rebuilt independently).*
- C14: Effects on expression estimates require cohort data (probe presence, D17 (expression/feature filter), probe concordance) and are not assessed here. *Reconstruction: not applicable (qualitative).*
- C15: Requires the cohort's authorized Series Matrix probe list; no GEO data used. Platform-wide counts are not cohort coverage. lumiHumanIDMapping holds three HT-12 v4 tables: HumanHT12_V4_0_R1_15002873_B (47,231 probe IDs; 47,231 also in HumanHT12_V4_0_R2_15002873_B, 47,231 with the same nuID); HumanHT12_V4_0_R2_15002873_B (47,323 probe IDs; 47,323 also in HumanHT12_V4_0_R2_15002873_B, 47,323 with the same nuID); HumanHT12_V4_0_R2_15002873_B_WGDASL (29,377 probe IDs; 29,320 also in HumanHT12_V4_0_R2_15002873_B, 29,320 with the same nuID). This matrix uses HumanHT12_V4_0_R2_15002873_B. These counts describe the package only; which table (if any) corresponds to GSE140829 is part of D19 and is not established here. *Reconstruction: not assessed.*

## Conclusions

**Established by the retained evidence**

- M1 agreement (concordant / both assign), separately per platform: illuminaHumanv3 29,284 / 29,294 (99.97%); illuminaHumanv4 33,745 / 33,761 (99.95%); lumi HT-12 v4 R2 30,640 / 30,677 (99.88%).
- Option A assigns more probes (C01) and genes (C02) than the accession route on every platform (illuminaHumanv3 +163 probes, +126 genes; illuminaHumanv4 +227 probes, +147 genes; lumi HT-12 v4 R2 +6,361 probes, +3,150 genes). This is one coverage difference; C09 and C10 restate it.
- Probes that differ under M2 (package ID ≠ accession-route gene) decompose as follows (all non-trivial records are in v3/metric_reconciliation_probes.tsv):
  - illuminaHumanv3: 50 = 40 concordant after replacement + 10 M1-discordant (10 direct, 0 replacement-derived) + 0 outside M1
  - illuminaHumanv4: 64 = 48 concordant after replacement + 16 M1-discordant (16 direct, 0 replacement-derived) + 0 outside M1
  - lumi HT-12 v4 R2: 283 = 244 concordant after replacement + 37 M1-discordant (32 direct, 5 replacement-derived) + 2 outside M1 (ILMN_1712269 [discontinued_no_replacement]; ILMN_3239440 [discontinued_no_replacement])

**Suggested but not established**

- That Option A's extra coverage reflects valid probe-to-gene relationships: it rests on package assignments dated 2015 (illuminaHumanv3/v4) or of unrecorded date in a 2016 build (lumi) and, for lumi, on many replacements and collisions.
- That the accession route's newer gene-ID snapshot is more accurate biologically (unversioned accession matches do not confirm that the probe targets the current transcript).

**Unknown**

- Which route is correct for each discordant or single-route probe.
- Cohort-specific coverage (probe presence in each Series Matrix), the D17 decision (expression/feature filter), and the effect of either route on gene-level estimates.
- Which lumiHumanIDMapping HT-12 v4 table, if any, applies to GSE140829 (D19); this matrix uses HumanHT12_V4_0_R2_15002873_B.

**Evidence required before a policy decision**

- Probe presence in each cohort's authorized Series Matrix (GSE63060, GSE63061; GSE140829 after D19).
- The D17 decision.
- A decision on how discordant and single-route probes are treated, and whether sequence-level evidence (e.g. the packages' re-annotation fields) should be considered.
- A decision on whether the gene-history procedure, approved under D6-F for GPL570 only, may be applied to Illumina platforms.

## Not yet assessed / unresolved

- Probe presence in cohort inputs (no GEO data used); D17; the Illumina mapping policy; D19 (GSE140829); any biological validation beyond annotation agreement.

## Provenance and reconstructability

- Fully reconstructed from retained raw sources (package and org.Hs.eg.db tarballs, hash-verified): probe sets, package gene IDs, multi-gene / no-gene probes, which package IDs are absent from org.Hs.eg.db 3.23.1, eligible_direct probes, every accession-route figure, C08, C12, and source dates.
- Reconstructed only from retained derived records: the replacement / no-replacement / unexplained class of each package ID absent from org.Hs.eg.db, and therefore every Option A figure that includes replacement-derived probes (C01–C07, C09, C10, C13 Option A side). The per-probe Option A classes were re-derived from the package tables plus the retained gene-history v1 records and equal the Option A v1 table. Option A replacement-dependent figures trace to the retained gene-history v1 records (the human records the audit used, kept verbatim in gene_history_reconciliation.tsv); the raw NCBI gene_history.gz (SHA-256 bcb85c8f…) is not retained and cannot be re-obtained byte-identically (ncbi_gene_history/SOURCE_RETENTION.md).
- The set of absent package IDs computed from the raw sources equals the set recorded in gene-history v1 for each platform, so the retained records cover every ID that needs them.

## Changes from v1 (REVIEW_v1.md)

| Finding | Change in v2 |
|---|---|
| R1 | C09 and C10 advantage set to 'restates C01 (not counted)' with derived_from = C01; C01/C09/C10 limitations and Definitions state they are one coverage fact; C02 noted as related but not a restatement |
| R2 | C08 reworded (each route excludes its own ambiguous probes); same-probe cross-tabulation added; advantage 'not determinable', status 'unresolved'; lumi zero explained as a source-representation property |
| R3 | C11 is provenance context: advantage 'not determinable', status 'unresolved' on every platform; rule enforced: 'not determinable' ⇒ 'unresolved' |
| R4 | Conclusion decomposes every platform's M2 'different' probes (replacement-concordant / discordant by class / outside M1, with probe IDs) |
| R5 | C05 and C06 report replacement-derived discordant probes using the labels of v3/metric_reconciliation_probes.tsv |
| R6 | C11 reports raw REFSEQ VERSION and DESCRIPTION build dates (lumi 2016-04-21); C15 lists the HT-12 v4 tables without claiming GSE140829 applicability |
| R7 | C11 limitation, 'reconstruction' column and Provenance section disclose the unretained gene_history.gz and what remains reconstructable |
| R8 | C11 and Definitions state the gene-history procedure is approved for GPL570 only (D6-F), provisional for Illumina |
| R9 | Checks renamed to what they test; Option A and C03 figures recomputed and checked; input verification recorded; manifest records generator/dependency hashes, interpreter, full command and an independent-process run |
| R10 | Heading without nested parentheses; joint metrics in a 'joint' column; 'M2 total; M1 total (different metrics)'; C07 composition shown; 'D17 (expression/feature filter)'; ties → 'neither' |

## Validation

- [OK] input: v3 route_comparison_metrics.tsv SHA-256 equals the v3 manifest
- [OK] input: v3 REPORT.md SHA-256 equals the v3 manifest
- [OK] input: v3 metric_reconciliation_probes.tsv SHA-256 equals the v3 manifest
- [OK] input: v3 validation status is OK
- [OK] input: illuminaHumanv3.db_1.26.0.tar.gz SHA-256 equals the v3 manifest and reference/download_manifest.json
- [OK] input: illuminaHumanv4.db_1.26.0.tar.gz SHA-256 equals the v3 manifest and reference/download_manifest.json
- [OK] input: lumiHumanIDMapping_1.10.1.tar.gz SHA-256 equals the v3 manifest and reference/download_manifest.json
- [OK] input: org.Hs.eg.db_3.23.1.tar.gz SHA-256 equals the v3 manifest and reference/download_manifest.json
- [OK] input: Option A illuminaHumanv3_probe_classification_PROVISIONAL.tsv SHA-256 equals its manifest and the v3 record
- [OK] input: Option A illuminaHumanv4_probe_classification_PROVISIONAL.tsv SHA-256 equals its manifest and the v3 record
- [OK] input: Option A lumi_HT12_v4_R2_probe_classification_PROVISIONAL.tsv SHA-256 equals its manifest and the v3 record
- [OK] input: gene-history v1 manifest SHA-256 equals the one recorded by Option A v1
- [OK] input: gene-history v1 table SHA-256 equals its manifest
- [OK] input: gene-history View A cutoff is 20260318
- [OK] preserved: REVIEW_v1.md SHA-256 equals the value at review completion (a130d99f…)
- [OK] preserved: v1 decision_matrix_manifest.json SHA-256 equals the value recorded in REVIEW_v1.md
- [OK] preserved: v1 DECISION_MATRIX.md SHA-256 equals the v1 manifest
- [OK] preserved: v1 decision_matrix.tsv SHA-256 equals the v1 manifest
- [OK] illuminaHumanv3: [raw] package probe table reproduces the Option A v1 probe set, gene counts and package gene IDs
- [OK] illuminaHumanv3: [raw] package Entrez IDs absent from org.Hs.eg.db 3.23.1 genes = gene-history v1 'absent_from_baseline' IDs for this package
- [OK] illuminaHumanv3: [raw + retained gene-history records] per-probe Option A class and gene reconstructed = Option A v1 table
- [OK] illuminaHumanv3: [raw] eligible_direct probes = single package gene present in org.Hs.eg.db 3.23.1
- [OK] illuminaHumanv3: Option A metrics (eligible, direct, via replacement, no replacement, unexplained, genes, multi-probe genes, collisions) recomputed from the Option A v1 table = v3 manifest
- [OK] illuminaHumanv3: [raw] multi-gene and no-gene probe counts = v3 manifest
- [OK] illuminaHumanv3: [raw] accession classes from the independent org.Hs.eg.db map = classes from the v3 map, probe by probe
- [OK] illuminaHumanv3: [raw] accession classes, unique probes and distinct genes = v3 manifest
- [OK] illuminaHumanv3: [raw] C03 accession-route multi-probe genes: independent map = v3 map; probe sum = unique probes; gene count = distinct genes
- [OK] illuminaHumanv3: [raw] accession inputs (values, version-suffixed values, probes with >1 accession) = v3 manifest
- [OK] illuminaHumanv3: M1 both / concordant / discordant = v3 manifest
- [OK] illuminaHumanv3: single-route and ambiguous-under-accession Option A probes = v3 manifest
- [OK] illuminaHumanv3: gene overlap = v3 manifest
- [OK] illuminaHumanv3: M2 total / same / different and M1 subset of M2 = v3 manifest
- [OK] illuminaHumanv3: M2 -> M1 transition counts = v3 manifest
- [OK] illuminaHumanv3: probes outside M1 = v3 manifest list
- [OK] illuminaHumanv3: every non-(same -> concordant) transition matches v3/metric_reconciliation_probes.tsv probe by probe
- [OK] illuminaHumanv3: C09 unresolved = all probes - C01 assigned (both routes)
- [OK] illuminaHumanv3: C10 single-route difference = C01 coverage difference
- [OK] illuminaHumanv3: ambiguity cross-tabulation partitions the package-multi-gene and accession-ambiguous probes
- [OK] illuminaHumanv4: [raw] package probe table reproduces the Option A v1 probe set, gene counts and package gene IDs
- [OK] illuminaHumanv4: [raw] package Entrez IDs absent from org.Hs.eg.db 3.23.1 genes = gene-history v1 'absent_from_baseline' IDs for this package
- [OK] illuminaHumanv4: [raw + retained gene-history records] per-probe Option A class and gene reconstructed = Option A v1 table
- [OK] illuminaHumanv4: [raw] eligible_direct probes = single package gene present in org.Hs.eg.db 3.23.1
- [OK] illuminaHumanv4: Option A metrics (eligible, direct, via replacement, no replacement, unexplained, genes, multi-probe genes, collisions) recomputed from the Option A v1 table = v3 manifest
- [OK] illuminaHumanv4: [raw] multi-gene and no-gene probe counts = v3 manifest
- [OK] illuminaHumanv4: [raw] accession classes from the independent org.Hs.eg.db map = classes from the v3 map, probe by probe
- [OK] illuminaHumanv4: [raw] accession classes, unique probes and distinct genes = v3 manifest
- [OK] illuminaHumanv4: [raw] C03 accession-route multi-probe genes: independent map = v3 map; probe sum = unique probes; gene count = distinct genes
- [OK] illuminaHumanv4: [raw] accession inputs (values, version-suffixed values, probes with >1 accession) = v3 manifest
- [OK] illuminaHumanv4: M1 both / concordant / discordant = v3 manifest
- [OK] illuminaHumanv4: single-route and ambiguous-under-accession Option A probes = v3 manifest
- [OK] illuminaHumanv4: gene overlap = v3 manifest
- [OK] illuminaHumanv4: M2 total / same / different and M1 subset of M2 = v3 manifest
- [OK] illuminaHumanv4: M2 -> M1 transition counts = v3 manifest
- [OK] illuminaHumanv4: probes outside M1 = v3 manifest list
- [OK] illuminaHumanv4: every non-(same -> concordant) transition matches v3/metric_reconciliation_probes.tsv probe by probe
- [OK] illuminaHumanv4: C09 unresolved = all probes - C01 assigned (both routes)
- [OK] illuminaHumanv4: C10 single-route difference = C01 coverage difference
- [OK] illuminaHumanv4: ambiguity cross-tabulation partitions the package-multi-gene and accession-ambiguous probes
- [OK] lumi HT-12 v4 R2: [raw] package probe table reproduces the Option A v1 probe set, gene counts and package gene IDs
- [OK] lumi HT-12 v4 R2: [raw] package Entrez IDs absent from org.Hs.eg.db 3.23.1 genes = gene-history v1 'absent_from_baseline' IDs for this package
- [OK] lumi HT-12 v4 R2: [raw + retained gene-history records] per-probe Option A class and gene reconstructed = Option A v1 table
- [OK] lumi HT-12 v4 R2: [raw] eligible_direct probes = single package gene present in org.Hs.eg.db 3.23.1
- [OK] lumi HT-12 v4 R2: Option A metrics (eligible, direct, via replacement, no replacement, unexplained, genes, multi-probe genes, collisions) recomputed from the Option A v1 table = v3 manifest
- [OK] lumi HT-12 v4 R2: [raw] multi-gene and no-gene probe counts = v3 manifest
- [OK] lumi HT-12 v4 R2: [raw] accession classes from the independent org.Hs.eg.db map = classes from the v3 map, probe by probe
- [OK] lumi HT-12 v4 R2: [raw] accession classes, unique probes and distinct genes = v3 manifest
- [OK] lumi HT-12 v4 R2: [raw] C03 accession-route multi-probe genes: independent map = v3 map; probe sum = unique probes; gene count = distinct genes
- [OK] lumi HT-12 v4 R2: [raw] accession inputs (values, version-suffixed values, probes with >1 accession) = v3 manifest
- [OK] lumi HT-12 v4 R2: M1 both / concordant / discordant = v3 manifest
- [OK] lumi HT-12 v4 R2: single-route and ambiguous-under-accession Option A probes = v3 manifest
- [OK] lumi HT-12 v4 R2: gene overlap = v3 manifest
- [OK] lumi HT-12 v4 R2: M2 total / same / different and M1 subset of M2 = v3 manifest
- [OK] lumi HT-12 v4 R2: M2 -> M1 transition counts = v3 manifest
- [OK] lumi HT-12 v4 R2: probes outside M1 = v3 manifest list
- [OK] lumi HT-12 v4 R2: every non-(same -> concordant) transition matches v3/metric_reconciliation_probes.tsv probe by probe
- [OK] lumi HT-12 v4 R2: C09 unresolved = all probes - C01 assigned (both routes)
- [OK] lumi HT-12 v4 R2: C10 single-route difference = C01 coverage difference
- [OK] lumi HT-12 v4 R2: ambiguity cross-tabulation partitions the package-multi-gene and accession-ambiguous probes
- [OK] lumi HT-12 v4 R2: [raw] source representation is single-valued (one R2_B row per probe ID, every nuID mapped, one mapping row per nuID, no multi-value EntrezID/Accession), so the C08/C12 zeros are structural
- [OK] matrix: every platform has exactly C01–C15
- [OK] matrix: statuses and advantages use the allowed vocabularies
- [OK] matrix: no criterion has status 'decisive'
- [OK] matrix: every 'not determinable' advantage has status 'unresolved'
- [OK] matrix: C09 and C10 are marked as restating C01
- [OK] matrix: no empty cell

## Package provenance (read from retained tarballs)

- illuminaHumanv3.db_1.26.0.tar.gz: DESCRIPTION Version 1.26.0, Packaged 2015-04-07 15:19:38 UTC; metadata EGSOURCEDATE=2015-Mar17; metadata EGSOURCENAME=Entrez Gene; metadata CHIPNAME=HumanHT12v3
- illuminaHumanv4.db_1.26.0.tar.gz: DESCRIPTION Version 1.26.0, Packaged 2015-04-07 15:39:45 UTC; metadata EGSOURCEDATE=2015-Mar17; metadata EGSOURCENAME=Entrez Gene; metadata CHIPNAME=HumanHT12v4
- lumiHumanIDMapping_1.10.1.tar.gz: DESCRIPTION Version 1.10.1, Packaged 2016-04-21 13:21:07 UTC; metadata REFSEQ VERSION=blank (raw value ' ')
- org.Hs.eg.db_3.23.1.tar.gz: DESCRIPTION Version 3.23.1, Packaged 2026-03-23 01:48:12 UTC; metadata EGSOURCEDATE=2026-Mar18; metadata EGSOURCENAME=Entrez Gene
