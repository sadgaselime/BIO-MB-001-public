# NCBI gene-history reconciliation audit (Option C, dual reporting) — v1

Audit only. No annotation resource, mapping rule or shared-snapshot requirement is chosen or changed (D6-D unapproved). No GEO data, probe lists, QC, DE, S8 or confirmatory analysis were used.

## Sources (verified before use; see reconciliation_manifest.json)

- Baseline: org.Hs.eg.db 3.23.1, Entrez Gene snapshot 2026-Mar18 (193797 gene IDs).
- NCBI gene_history.gz retrieved 2026-10-12T17:16:35Z (server Last-Modified 2026-10-09 08:36:13 GMT); 166633 human rows. NCBI recalculates this file daily and publishes no checksum or versioned release: reproducibility rests on the retained file and its SHA-256, not on the URL.
- Historical IDs: illuminaHumanv3.db 1.26.0 and illuminaHumanv4.db 1.26.0 (Entrez snapshot 2015-Mar17), hgu133plus2.db 3.13.0 (2021-Apr14), lumiHumanIDMapping 1.10.1 table HumanHT12_V4_0_R2_15002873_B (undated).

## Reporting policies

- **View A (primary, snapshot-consistent).** org.Hs.eg.db is fixed. IDs present in it are preserved. For absent IDs only gene_history records dated on or before 20260318 are used; later records are reported, not applied.
- **View B (October history audit).** All human records in the retained file are used. Chains continue through IDs that are in the baseline but discontinued in the file.
- Both: successor = GeneID column only (never symbols); GeneID "-" = explicit no-replacement state (README wording plus observed data); every chain step is recorded; cycles, duplicate records and unresolvable successors are flagged; nothing is merged.

## Counts by package (every distinct historical ID classified once per view)

| Package | Input IDs | Absent from baseline | of which in history | Tabulated rows |
|---|---|---|---|---|
| illuminaHumanv3 | 20011 | 98 | 98 | 98 |
| illuminaHumanv4 | 21748 | 146 | 146 | 147 |
| hgu133plus2 | 22251 | 84 | 84 | 86 |
| lumi HT-12 v4 R2 | 30500 | 7169 | 7168 | 7171 |

**View A classes:**

- illuminaHumanv3: discontinued_no_replacement 53, present_in_baseline 19913, replaced_successor_in_baseline 45
- illuminaHumanv4: discontinued_no_replacement 87, present_in_baseline 21602, replaced_successor_in_baseline 59
- hgu133plus2: discontinued_no_replacement 48, present_in_baseline 22167, replaced_successor_in_baseline 36
- lumi HT-12 v4 R2: chain_ends_no_replacement 410, discontinued_no_replacement 5414, present_in_baseline 23331, replaced_successor_in_baseline 1344, unexplained_absent_no_history 1

**View B classes:**

- illuminaHumanv3: discontinued_no_replacement 53, present_in_baseline_no_history 19913, replaced_successor_in_baseline 45
- illuminaHumanv4: discontinued_no_replacement 87, present_in_baseline_discontinued_in_history 1, present_in_baseline_no_history 21601, replaced_successor_in_baseline 59
- hgu133plus2: discontinued_no_replacement 48, present_in_baseline_discontinued_in_history 2, present_in_baseline_no_history 22165, replaced_successor_in_baseline 36
- lumi HT-12 v4 R2: chain_ends_no_replacement 410, discontinued_no_replacement 5414, present_in_baseline_discontinued_in_history 2, present_in_baseline_no_history 23329, replaced_successor_in_baseline 1344, unexplained_absent_no_history 1

## Timing-discrepant IDs (17): present in the 2026-03-18 baseline, discontinued in the retained file

| Entrez ID | Successor | Date | vs cutoff | Successor in baseline | Affected packages |
|---|---|---|---|---|---|
| 3653 | 104472715 | 20260527 | after_cutoff | yes | illuminaHumanv4;hgu133plus2;lumi HT-12 v4 R2 |
| 6914 | - | 20260523 | after_cutoff | — | — |
| 645261 | 117751736 | 20260324 | after_cutoff | yes | hgu133plus2;lumi HT-12 v4 R2 |
| 105377447 | 107986315 | 20260320 | after_cutoff | yes | — |
| 105379065 | 117751736 | 20260324 | after_cutoff | yes | — |
| 107986635 | 105377950 | 20260319 | after_cutoff | yes | — |
| 107986636 | 105377950 | 20260319 | after_cutoff | yes | — |
| 107986673 | 4301 | 20260318 | on_or_before_cutoff | yes | — |
| 124900389 | 339260 | 20260319 | after_cutoff | yes | — |
| 124900671 | 26234 | 20260325 | after_cutoff | yes | — |
| 124901281 | 8418 | 20260731 | after_cutoff | yes | — |
| 124901283 | 8418 | 20260731 | after_cutoff | yes | — |
| 124902122 | 105375980 | 20260417 | after_cutoff | yes | — |
| 124903827 | 440556 | 20260523 | after_cutoff | yes | — |
| 124904106 | - | 20260522 | after_cutoff | — | — |
| 124904164 | 105378685 | 20260401 | after_cutoff | yes | — |
| 128966744 | 150763 | 20260915 | after_cutoff | yes | — |

In View A these IDs stay as in the baseline. A record dated exactly on the cutoff is applied in View A only to IDs absent from the baseline.

## Focus IDs

- 653803 (lumi HT-12 v4 R2): baseline absent_from_baseline; View A unexplained_absent_no_history [653803]; View B unexplained_absent_no_history [653803]; history date —; reason absent_from_baseline_and_history
- 3653 (illuminaHumanv4): baseline present_in_baseline; View A present_in_baseline [3653]; View B present_in_baseline_discontinued_in_history [3653>104472715]; history date 20260527; reason —
- 3653 (hgu133plus2): baseline present_in_baseline; View A present_in_baseline [3653]; View B present_in_baseline_discontinued_in_history [3653>104472715]; history date 20260527; reason —
- 645261 (hgu133plus2): baseline present_in_baseline; View A present_in_baseline [645261]; View B present_in_baseline_discontinued_in_history [645261>117751736]; history date 20260324; reason —

## Chains, collisions and shared successors

- illuminaHumanv3: View A collisions 34, shared successors 4; View B collisions 34, shared successors 4; multi-step chains (View B) none
- illuminaHumanv4: View A collisions 40, shared successors 6; View B collisions 40, shared successors 6; multi-step chains (View B) none
- hgu133plus2: View A collisions 26, shared successors 0; View B collisions 27, shared successors 0; multi-step chains (View B) none
- lumi HT-12 v4 R2: View A collisions 892, shared successors 275; View B collisions 892, shared successors 277; multi-step chains (View B) 644291 [644291>728936>284565]

A collision means the successor is itself a directly mapped historical ID of the same package; a shared successor means several input IDs resolve to it. Both are flags only: no probes or genes were merged.

## Limitations

- Absence from org.Hs.eg.db is not evidence of retirement; only gene_history records are.
- gene_history has one record per discontinued ID and does not distinguish merges from splits.
- The meaning of GeneID "-" is inferred from the README wording and the data, not stated explicitly.
- The file is a daily recalculation without a published checksum; the URL does not identify this content.
- The verified source files are retained outside the project (scratch); data/ is reserved for script-produced GEO files (data/README.md). Durable retention needs a separate decision.
- This audit does not address the GPL570 accession-route gap, unversioned accessions, ambiguous accessions or multi-gene probes.

## Validation: OK

- [OK] tabulated_ids_unique_per_package — 7502 (package, id) rows
- [OK] illuminaHumanv3: viewA classes sum to inputs — 20011 = 20011
- [OK] illuminaHumanv3: viewB classes sum to inputs — 20011 = 20011
- [OK] illuminaHumanv3: tabulated = absent + present-but-discontinued — 98 = 98
- [OK] illuminaHumanv3: absent / in-history counts vs 2026-10-12 report — now (98, 98), previously (98, 98)
- [OK] illuminaHumanv4: viewA classes sum to inputs — 21748 = 21748
- [OK] illuminaHumanv4: viewB classes sum to inputs — 21748 = 21748
- [OK] illuminaHumanv4: tabulated = absent + present-but-discontinued — 147 = 147
- [OK] illuminaHumanv4: absent / in-history counts vs 2026-10-12 report — now (146, 146), previously (146, 146)
- [OK] hgu133plus2: viewA classes sum to inputs — 22251 = 22251
- [OK] hgu133plus2: viewB classes sum to inputs — 22251 = 22251
- [OK] hgu133plus2: tabulated = absent + present-but-discontinued — 86 = 86
- [OK] hgu133plus2: absent / in-history counts vs 2026-10-12 report — now (84, 84), previously (84, 84)
- [OK] lumi HT-12 v4 R2: viewA classes sum to inputs — 30500 = 30500
- [OK] lumi HT-12 v4 R2: viewB classes sum to inputs — 30500 = 30500
- [OK] lumi HT-12 v4 R2: tabulated = absent + present-but-discontinued — 7171 = 7171
- [OK] lumi HT-12 v4 R2: absent / in-history counts vs 2026-10-12 report — now (7169, 7168), previously (7169, 7168)
- [OK] every chain ends in a defined terminal class — 0 rows outside the terminal set
- [OK] cycles flagged (not ignored) — 0 cycle(s) flagged
- [OK] duplicate source records flagged (not ignored) — 0 discontinued ID(s) with >1 human record
- [OK] View A applies no record dated after the cutoff — 0 post-cutoff step(s) used
- [OK] View A preserves every baseline-present ID — 0 baseline ID(s) altered in View A
- [OK] no merges performed (one row per input ID; successors only flagged) — rows are never combined; collision/shared flags are informational
