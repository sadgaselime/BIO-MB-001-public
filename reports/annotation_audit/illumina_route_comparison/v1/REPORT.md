# Illumina mapping-route comparison — v1 (decision support; no policy approved)

## Executive summary

- **Option A** (package Entrez IDs + approved gene-history procedure, cutoff 20260318) is fully quantified below from verified retained outputs.
- **Accession route:** only its inputs could be measured. Resolving accessions to current Entrez IDs requires org.Hs.eg.db 3.23.1, which is not retained in the project; route assignments, concordance, discordance and ambiguity were therefore **not computed**. The comparison is incomplete until that source is retained.
- No Illumina mapping policy is approved by this report. GSE140829 remains governed by D19; D17 is unchanged.

## Methods and provenance

- Option A: `reports/annotation_audit/illumina_option_a/v1/` (hashes verified against its manifest).
- Accession-route inputs: `accessions` tables of illuminaHumanv3.db / illuminaHumanv4.db 1.26.0 and the `Accession` column of lumiHumanIDMapping 1.10.1 (`nuID_MappingInfo` joined to `HumanHT12_V4_0_R2_15002873_B`), read from the retained tarballs in `reference/bioconductor_3.23/` (hashes verified against its manifest).
- Missing for the accession route: `org.Hs.eg.db_3.23.1.tar.gz` (103,790,170 bytes; published MD5 `813be1921e7bc08c1348dbce9d244d0a`; recorded SHA-256 `470620665cf49d0319422731164f377e3e74253989f1d33a8a1d100cc3d49cfe`; https://bioconductor.org/packages/3.23/data/annotation/src/contrib/org.Hs.eg.db_3.23.1.tar.gz).
- Denominators: *probes* = rows of each package's probe table (lumi: HT-12 v4 R2 manifest rows); *single-gene probes* = probes with exactly one Entrez ID in the package. Probe-level and gene-level figures are kept separate.

## Comparison tables (probe level unless stated)

### illuminaHumanv3 (GSE63060)

| Measure | Option A | Accession route |
|---|---:|---:|
| Probes (denominator) | 49,576 | 49,576 |
| Single-gene / multi-gene / no gene (package) | 29,551 / 1,175 / 18,850 | same package table |
| Probes with an input for the route | 29,551 single-gene | 31,857 with ≥1 accession (64.26%) |
| Eligible assignments | 29,489 (59.48% of probes; 99.79% of single-gene) | not computed |
| — direct / via replacement | 29,430 / 59 | not computed |
| No replacement / unexplained | 62 / 0 | not computed |
| Concordant / discordant / ambiguous / unresolved | not applicable within one route | not computed |
| Distinct genes (gene level) | 19,226 | not computed |
| Genes measured by >1 eligible probe (gene level) | 6,554 | not computed |
| Successor collisions: probes / distinct successor genes / distinct historical source genes | 43 / 28 / 30 | not applicable |

Accession-route inputs: 29,551 single-gene probes have ≥1 accession (100.00%); 29,489 Option A-eligible probes have one; 12,377 probes carry >1 accession; 0 accession values carry a version suffix; prefixes {'NM_': 50296, 'NR_': 4534, 'XM_': 1113, 'XR_': 1439}.

### illuminaHumanv4 (GSE63061)

| Measure | Option A | Accession route |
|---|---:|---:|
| Probes (denominator) | 48,107 | 48,107 |
| Single-gene / multi-gene / no gene (package) | 34,160 / 1,726 / 12,221 | same package table |
| Probes with an input for the route | 34,160 single-gene | 37,881 with ≥1 accession (78.74%) |
| Eligible assignments | 34,038 (70.75% of probes; 99.64% of single-gene) | not computed |
| — direct / via replacement | 33,962 / 76 | not computed |
| No replacement / unexplained | 122 / 0 | not computed |
| Concordant / discordant / ambiguous / unresolved | not applicable within one route | not computed |
| Distinct genes (gene level) | 20,926 | not computed |
| Genes measured by >1 eligible probe (gene level) | 7,678 | not computed |
| Successor collisions: probes / distinct successor genes / distinct historical source genes | 50 / 32 / 35 | not applicable |

Accession-route inputs: 34,160 single-gene probes have ≥1 accession (100.00%); 34,038 Option A-eligible probes have one; 14,399 probes carry >1 accession; 0 accession values carry a version suffix; prefixes {'NM_': 56375, 'NR_': 7477, 'XM_': 2043, 'XR_': 2218}.

### lumi HT-12 v4 R2 (GSE140829 applicability unverified (D19))

| Measure | Option A | Accession route |
|---|---:|---:|
| Probes (denominator) | 47,323 | 47,323 |
| Single-gene / multi-gene / no gene (package) | 43,960 / 0 / 3,363 | same package table |
| Probes with an input for the route | 43,960 single-gene | 47,323 with ≥1 accession (100.00%) |
| Eligible assignments | 37,491 (79.22% of probes; 85.28% of single-gene) | not computed |
| — direct / via replacement | 35,731 / 1,760 | not computed |
| No replacement / unexplained | 6,468 / 1 | not computed |
| Concordant / discordant / ambiguous / unresolved | not applicable within one route | not computed |
| Distinct genes (gene level) | 23,743 | not computed |
| Genes measured by >1 eligible probe (gene level) | 8,600 | not computed |
| Successor collisions: probes / distinct successor genes / distinct historical source genes | 1,165 / 783 / 892 | not applicable |

Accession-route inputs: 43,960 single-gene probes have ≥1 accession (100.00%); 37,491 Option A-eligible probes have one; 0 probes carry >1 accession; 0 accession values carry a version suffix; prefixes {'GenBank (no prefix)': 3311, 'NM_': 29183, 'NR_': 1960, 'XM_': 10355, 'XR_': 2514}.

## Reconciliation checks

- [OK] illuminaHumanv3: Option A classes sum to probes
- [OK] illuminaHumanv3: single + multi + none = probes
- [OK] illuminaHumanv3: eligible <= single-gene probes
- [OK] illuminaHumanv3: every accession probe ID exists in the Option A table
- [OK] illuminaHumanv4: Option A classes sum to probes
- [OK] illuminaHumanv4: single + multi + none = probes
- [OK] illuminaHumanv4: eligible <= single-gene probes
- [OK] illuminaHumanv4: every accession probe ID exists in the Option A table
- [OK] lumi HT-12 v4 R2: Option A classes sum to probes
- [OK] lumi HT-12 v4 R2: single + multi + none = probes
- [OK] lumi HT-12 v4 R2: eligible <= single-gene probes
- [OK] lumi HT-12 v4 R2: every accession probe ID exists in the Option A table

## Implications for gene-level analysis (G3)

- Under G3 every eligible probe of a gene is averaged. Each successor collision adds a replaced probe to a gene that already has directly mapped probes; its signal becomes part of that gene's average (Option A collision counts above). No probes were merged in these audits.
- Probes without an eligible assignment are excluded from gene-level units ("unmapped", counted), so lower coverage reduces the measurable gene set and the validation/specificity measurability (v5 §7.3).
- Option A's probe-to-gene knowledge dates to 2015-Mar17 (illuminaHumanv3/v4); lumi's manifest-based mapping has no recorded date. The accession route would use the 2026-03-18 Entrez snapshot but relies on unversioned accession roots, so sequence-level equivalence to the current transcript is not established for either route.

## Neutral assessment of trade-offs

- **Option A:** fully reproducible from retained inputs; consistent with the approved GPL570 policy (D6-F); older probe-to-gene knowledge; collisions concentrated in lumi.
- **Accession route:** current Entrez snapshot, but its coverage, concordance and ambiguity on these platforms cannot be verified from retained evidence; it needs org.Hs.eg.db 3.23.1 retained before it can be evaluated.
- A like-for-like decision is not supported until the accession route is recomputed from a retained source.

## Decisions that remain unapproved

- Illumina mapping policy (Option A, accession route, or other) for GSE63060 and GSE63061.
- GSE140829 mapping (D19), including whether the HT-12 v4 R2 manifest table applies.
- D17 feature rule; retention of org.Hs.eg.db 3.23.1 (download requires approval); installation of any annotation package.

## Appendix — accession-route figures from the 2026-10-12 session (NOT reproducible from retained evidence)

Observed interactively against each package's own Entrez IDs (not against Option A) and never saved to the project. Shown for orientation only; they are not verified results.

- illuminaHumanv3: denominator 29,551 single-gene probes; route_exactly_one_gene 29294; same_gene 29244; different_gene 50; route_ambiguous 10; no_route 247
- illuminaHumanv4: denominator 34,160 single-gene probes; route_exactly_one_gene 33761; same_gene 33697; different_gene 64; route_ambiguous 10; no_route 389
- lumi HT-12 v4 R2: denominator 47,323 nuIDs (manifest rows); route_resolved_exactly_one_gene 31130; agrees_with_lumi_EntrezID 30396; differs_from_lumi_EntrezID 283
