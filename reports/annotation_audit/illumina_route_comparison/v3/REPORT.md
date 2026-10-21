# Illumina mapping-route comparison — v3 (decision support; no policy approved)

## Executive summary

- **illuminaHumanv3** (GSE63060): Option A assigns 29,489 probes, the accession route 29,326 (of 49,576). Where both assign one gene (29,294 probes) they agree for 29,284 (99.97%) and disagree for 10.
- **illuminaHumanv4** (GSE63061): Option A assigns 34,038 probes, the accession route 33,811 (of 48,107). Where both assign one gene (33,761 probes) they agree for 33,745 (99.95%) and disagree for 16.
- **lumi HT-12 v4 R2** (GSE140829 applicability unverified (D19)): Option A assigns 37,491 probes, the accession route 31,130 (of 47,323). Where both assign one gene (30,677 probes) they agree for 30,640 (99.88%) and disagree for 37.
- Both routes are now computed from retained, hash-verified sources. No Illumina mapping policy is approved; GSE140829 remains governed by D19; D17 is unchanged.

## Methods and provenance

- Option A: `reports/annotation_audit/illumina_option_a/v1/` (hashes verified against its manifest).
- Accession route: each probe's accessions (illuminaHumanv3.db / illuminaHumanv4.db 1.26.0 `accessions`; lumiHumanIDMapping 1.10.1 `nuID_MappingInfo.Accession` for the HT-12 v4 R2 table) matched exactly, without version suffixes, to the union of org.Hs.eg.db 3.23.1 `accessions` (GenBank) and `refseq` tables, then to `genes.gene_id` (Entrez Gene snapshot 2026-03-18). Probe genes = union over the probe's accessions.
- Accession-route classes: `unique` (one gene; the only assignment), `ambiguous` (>1 gene), `accession_unmatched` (accessions not in org.Hs.eg.db), `no_accession`.
- All sources read from `reference/bioconductor_3.23/` (hashes verified against `download_manifest.json`); nothing installed.
- Denominators: *probes* = rows of each package's probe table (lumi: HT-12 v4 R2 manifest rows). Both routes are evaluated on exactly the same probes. Gene counts are distinct current Entrez IDs with at least one assigned probe.

## Comparison tables

### illuminaHumanv3 (GSE63060)

**Probe level** (denominator: all probes)

| Measure | Option A | Accession route |
|---|---:|---:|
| Probes | 49,576 | 49,576 |
| Assigned to exactly one gene | 29,489 (59.48%) | 29,326 (59.15%) |
| Not assigned | 20,087 | 20,250 |
| Route classes | direct 29,430; via replacement 59; no replacement 62; unexplained 0; multi-gene 1,175; no gene 18,850 | accession_unmatched 1,379; ambiguous 1,152; no_accession 17,719; unique 29,326 |

**Like-for-like comparison on the same probes**

| Category | Probes |
|---|---:|
| Both assign one gene | 29,294 |
| — concordant | 29,284 (99.97%) |
| — discordant | 10 |
| Option A assigns; accession route ambiguous, includes the Option A gene | 9 |
| Option A assigns; accession route ambiguous, excludes the Option A gene | 1 |
| Option A assigns; accession route unresolved (no accession or unmatched) | 185 |
| Accession route assigns; Option A does not | 32 |
| Neither assigns | 20,055 |

**Gene level** (distinct current Entrez IDs with ≥1 assigned probe)

| Measure | Genes |
|---|---:|
| Option A | 19,226 |
| Accession route | 19,100 |
| Both routes | 19,085 |
| Option A only | 141 |
| Accession route only | 15 |

Option A successor collisions (flagged, not merged): 43 probes; 28 successor genes; 30 historical source genes.

Cross-tabulation (Option A status × accession-route class): optionA_discontinued_no_replacement | accession_unmatched: 62; optionA_eligible | accession_unmatched: 185; optionA_eligible | ambiguous: 10; optionA_eligible | unique: 29,294; optionA_multiple_mappings_excluded | accession_unmatched: 1; optionA_multiple_mappings_excluded | ambiguous: 1,142; optionA_multiple_mappings_excluded | unique: 32; optionA_no_assignment_in_package | accession_unmatched: 1,131; optionA_no_assignment_in_package | no_accession: 17,719.

**Two different agreement metrics (do not compare their totals directly)**

- **M1 — same-probe Option A comparison:** probes that Option A assigns AND the accession route resolves to one gene; agreement is judged against the Option A gene (after gene-history reconciliation). Total 29,294 (concordant + discordant above).
- **M2 — package-ID comparison (the 2026-10-12 definition):** probes with exactly one package Entrez ID AND an accession route resolving to one gene; agreement is judged against the package's own, un-reconciled ID. Total 29,294 (same + different below).
- M1 ⊆ M2: True. Probes in M2 but not M1 (0): none (their package ID has no eligible Option A assignment).
- Probe-level transitions M2 → M1 [Option A class]: different -> concordant [eligible_via_history_replacement]: 40; different -> discordant [eligible_direct]: 10; same -> concordant [eligible_direct]: 29,244.
- Probe records for every transition other than same → concordant: `metric_reconciliation_probes.tsv`.

**Re-computation of the unsaved 2026-10-12 figures** (accession route vs the package's own Entrez ID; denominator 29,551 single-gene probes): exactly one gene 29,294 (same 29,244, different 50), ambiguous 10, no route 247; all probes: unique 29,326, ambiguous 1,152. Previously reported (not saved): denominator 29,551 single-gene probes; route_exactly_one_gene 29294; same_gene 29244; different_gene 50; route_ambiguous 10; no_route 247.

### illuminaHumanv4 (GSE63061)

**Probe level** (denominator: all probes)

| Measure | Option A | Accession route |
|---|---:|---:|
| Probes | 48,107 | 48,107 |
| Assigned to exactly one gene | 34,038 (70.75%) | 33,811 (70.28%) |
| Not assigned | 14,069 | 14,296 |
| Route classes | direct 33,962; via replacement 76; no replacement 122; unexplained 0; multi-gene 1,726; no gene 12,221 | accession_unmatched 2,390; ambiguous 1,680; no_accession 10,226; unique 33,811 |

**Like-for-like comparison on the same probes**

| Category | Probes |
|---|---:|
| Both assign one gene | 33,761 |
| — concordant | 33,745 (99.95%) |
| — discordant | 16 |
| Option A assigns; accession route ambiguous, includes the Option A gene | 9 |
| Option A assigns; accession route ambiguous, excludes the Option A gene | 1 |
| Option A assigns; accession route unresolved (no accession or unmatched) | 267 |
| Accession route assigns; Option A does not | 50 |
| Neither assigns | 14,019 |

**Gene level** (distinct current Entrez IDs with ≥1 assigned probe)

| Measure | Genes |
|---|---:|
| Option A | 20,926 |
| Accession route | 20,779 |
| Both routes | 20,759 |
| Option A only | 167 |
| Accession route only | 20 |

Option A successor collisions (flagged, not merged): 50 probes; 32 successor genes; 35 historical source genes.

Cross-tabulation (Option A status × accession-route class): optionA_discontinued_no_replacement | accession_unmatched: 122; optionA_eligible | accession_unmatched: 267; optionA_eligible | ambiguous: 10; optionA_eligible | unique: 33,761; optionA_multiple_mappings_excluded | accession_unmatched: 6; optionA_multiple_mappings_excluded | ambiguous: 1,670; optionA_multiple_mappings_excluded | unique: 50; optionA_no_assignment_in_package | accession_unmatched: 1,995; optionA_no_assignment_in_package | no_accession: 10,226.

**Two different agreement metrics (do not compare their totals directly)**

- **M1 — same-probe Option A comparison:** probes that Option A assigns AND the accession route resolves to one gene; agreement is judged against the Option A gene (after gene-history reconciliation). Total 33,761 (concordant + discordant above).
- **M2 — package-ID comparison (the 2026-10-12 definition):** probes with exactly one package Entrez ID AND an accession route resolving to one gene; agreement is judged against the package's own, un-reconciled ID. Total 33,761 (same + different below).
- M1 ⊆ M2: True. Probes in M2 but not M1 (0): none (their package ID has no eligible Option A assignment).
- Probe-level transitions M2 → M1 [Option A class]: different -> concordant [eligible_via_history_replacement]: 48; different -> discordant [eligible_direct]: 16; same -> concordant [eligible_direct]: 33,697.
- Probe records for every transition other than same → concordant: `metric_reconciliation_probes.tsv`.

**Re-computation of the unsaved 2026-10-12 figures** (accession route vs the package's own Entrez ID; denominator 34,160 single-gene probes): exactly one gene 33,761 (same 33,697, different 64), ambiguous 10, no route 389; all probes: unique 33,811, ambiguous 1,680. Previously reported (not saved): denominator 34,160 single-gene probes; route_exactly_one_gene 33761; same_gene 33697; different_gene 64; route_ambiguous 10; no_route 389.

### lumi HT-12 v4 R2 (GSE140829 applicability unverified (D19))

**Probe level** (denominator: all probes)

| Measure | Option A | Accession route |
|---|---:|---:|
| Probes | 47,323 | 47,323 |
| Assigned to exactly one gene | 37,491 (79.22%) | 31,130 (65.78%) |
| Not assigned | 9,832 | 16,193 |
| Route classes | direct 35,731; via replacement 1,760; no replacement 6,468; unexplained 1; multi-gene 0; no gene 3,363 | accession_unmatched 16,193; unique 31,130 |

**Like-for-like comparison on the same probes**

| Category | Probes |
|---|---:|
| Both assign one gene | 30,677 |
| — concordant | 30,640 (99.88%) |
| — discordant | 37 |
| Option A assigns; accession route ambiguous, includes the Option A gene | 0 |
| Option A assigns; accession route ambiguous, excludes the Option A gene | 0 |
| Option A assigns; accession route unresolved (no accession or unmatched) | 6,814 |
| Accession route assigns; Option A does not | 453 |
| Neither assigns | 9,379 |

**Gene level** (distinct current Entrez IDs with ≥1 assigned probe)

| Measure | Genes |
|---|---:|
| Option A | 23,743 |
| Accession route | 20,593 |
| Both routes | 20,356 |
| Option A only | 3,387 |
| Accession route only | 237 |

Option A successor collisions (flagged, not merged): 1,165 probes; 783 successor genes; 892 historical source genes.

Cross-tabulation (Option A status × accession-route class): optionA_chain_ends_no_replacement | accession_unmatched: 436; optionA_discontinued_no_replacement | accession_unmatched: 6,030; optionA_discontinued_no_replacement | unique: 2; optionA_eligible | accession_unmatched: 6,814; optionA_eligible | unique: 30,677; optionA_no_assignment_in_package | accession_unmatched: 2,912; optionA_no_assignment_in_package | unique: 451; optionA_unexplained_absent_no_history | accession_unmatched: 1.

**Two different agreement metrics (do not compare their totals directly)**

- **M1 — same-probe Option A comparison:** probes that Option A assigns AND the accession route resolves to one gene; agreement is judged against the Option A gene (after gene-history reconciliation). Total 30,677 (concordant + discordant above).
- **M2 — package-ID comparison (the 2026-10-12 definition):** probes with exactly one package Entrez ID AND an accession route resolving to one gene; agreement is judged against the package's own, un-reconciled ID. Total 30,679 (same + different below).
- M1 ⊆ M2: True. Probes in M2 but not M1 (2): ILMN_1712269, ILMN_3239440 (their package ID has no eligible Option A assignment).
- Probe-level transitions M2 → M1 [Option A class]: different -> concordant [eligible_via_history_replacement]: 244; different -> discordant [eligible_direct]: 32; different -> discordant [eligible_via_history_replacement]: 5; different -> not_in_M1 (Option A not eligible) [discontinued_no_replacement]: 2; same -> concordant [eligible_direct]: 30,396.
- Probe records for every transition other than same → concordant: `metric_reconciliation_probes.tsv`.

**Re-computation of the unsaved 2026-10-12 figures** (accession route vs the package's own Entrez ID; denominator 43,960 single-gene probes): exactly one gene 30,679 (same 30,396, different 283), ambiguous 0, no route 13,281; all probes: unique 31,130, ambiguous 0. Previously reported (not saved): denominator 47,323 nuIDs (manifest rows); route_resolved_exactly_one_gene 31130; agrees_with_lumi_EntrezID 30396; differs_from_lumi_EntrezID 283.

## Reconciliation checks

- [OK] illuminaHumanv3: Option A classes sum to probes
- [OK] illuminaHumanv3: single + multi + none = probes
- [OK] illuminaHumanv3: eligible <= single-gene probes
- [OK] illuminaHumanv3: every accession probe ID exists in the Option A table
- [OK] illuminaHumanv3: accession-route classes sum to probes
- [OK] illuminaHumanv3: comparison categories sum to probes
- [OK] illuminaHumanv3: concordant + discordant = both assign one gene
- [OK] illuminaHumanv3: Option A eligible partition sums
- [OK] illuminaHumanv3: cross-tab sums to probes
- [OK] illuminaHumanv3: M1 set is a subset of M2 set
- [OK] illuminaHumanv3: M2 total = M1 total + probes in M2 not M1
- [OK] illuminaHumanv3: M1 concordant = sum of transitions to concordant
- [OK] illuminaHumanv3: M2 same = transitions same -> concordant
- [OK] illuminaHumanv4: Option A classes sum to probes
- [OK] illuminaHumanv4: single + multi + none = probes
- [OK] illuminaHumanv4: eligible <= single-gene probes
- [OK] illuminaHumanv4: every accession probe ID exists in the Option A table
- [OK] illuminaHumanv4: accession-route classes sum to probes
- [OK] illuminaHumanv4: comparison categories sum to probes
- [OK] illuminaHumanv4: concordant + discordant = both assign one gene
- [OK] illuminaHumanv4: Option A eligible partition sums
- [OK] illuminaHumanv4: cross-tab sums to probes
- [OK] illuminaHumanv4: M1 set is a subset of M2 set
- [OK] illuminaHumanv4: M2 total = M1 total + probes in M2 not M1
- [OK] illuminaHumanv4: M1 concordant = sum of transitions to concordant
- [OK] illuminaHumanv4: M2 same = transitions same -> concordant
- [OK] lumi HT-12 v4 R2: Option A classes sum to probes
- [OK] lumi HT-12 v4 R2: single + multi + none = probes
- [OK] lumi HT-12 v4 R2: eligible <= single-gene probes
- [OK] lumi HT-12 v4 R2: every accession probe ID exists in the Option A table
- [OK] lumi HT-12 v4 R2: accession-route classes sum to probes
- [OK] lumi HT-12 v4 R2: comparison categories sum to probes
- [OK] lumi HT-12 v4 R2: concordant + discordant = both assign one gene
- [OK] lumi HT-12 v4 R2: Option A eligible partition sums
- [OK] lumi HT-12 v4 R2: cross-tab sums to probes
- [OK] lumi HT-12 v4 R2: M1 set is a subset of M2 set
- [OK] lumi HT-12 v4 R2: M2 total = M1 total + probes in M2 not M1
- [OK] lumi HT-12 v4 R2: M1 concordant = sum of transitions to concordant
- [OK] lumi HT-12 v4 R2: M2 same = transitions same -> concordant

## Implications for gene-level analysis (G3)

- Under G3 every assigned probe of a gene is averaged, so the route determines which probes enter each gene's mean and which genes are measurable at all (unassigned probes are "unmapped" and counted).
- Discordant probes would be averaged into different genes under the two routes; ambiguous accession-route probes would be lost under that route (multi-gene exclusion).
- Option A collisions add replaced probes to genes that already have directly mapped probes.

## Known limitations

- Option A's probe-to-gene knowledge dates to 2015-Mar17 (illuminaHumanv3/v4); lumi's manifest mapping is undated.
- The accession route uses the 2026-03-18 snapshot but matches unversioned accession roots: a match does not establish that the probe sequence targets the current transcript.
- Package accession tables come from the manufacturer annotation (ACCNUM, documented in the chip packages); their own date is that of the package build.
- Presence of probes in each cohort's Series Matrix and the D17 feature rule are not assessed (no GEO data used).

## Neutral assessment of trade-offs

- **Option A:** consistent with the approved GPL570 policy (D6-F) and the approved gene-history procedure; older probe-to-gene knowledge; collisions flagged.
- **Accession route:** a single current snapshot with no history step; coverage, ambiguity and concordance as tabulated above; depends on unversioned accession matching.
- The tables above, not this report, should drive the choice; neither route is approved here.

## Decisions that remain unapproved

- Illumina mapping policy (Option A, accession route, a combination, or other) for GSE63060 and GSE63061.
- GSE140829 mapping (D19), including whether the HT-12 v4 R2 manifest table applies.
- D17 feature rule; installation of any annotation package.

