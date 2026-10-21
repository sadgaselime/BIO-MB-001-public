# GSE140829: decisions needed to unblock independent replication (brief, 2026-10-19)

Noncanonical decision-preparation note. **Nothing here is approved.** The work behind it was read-only:
- Feature IDs and sample characteristics (diagnosis as counts only) were read from the GSE140829 Series Matrix.
- The pinned annotation tarballs already in `reference/bioconductor_3.23/` were extracted to a scratch directory and queried read-only.
- Nothing was downloaded or installed, and no expression value was modelled.

## 1. D19: probe mapping (blocks all GSE140829 analyses)

**The problem.** GSE140829 (platform GPL15988, HT-12 v4) keys its 47,008 features by **nuID**. A nuID is a lossless
encoding of the 50-base probe sequence. The approved A0 mapping (D6-G) is keyed by ILMN probe ID.

**Evidence (three independent routes agree on every feature):**

| Check | Result |
|---|---|
| (a) The pinned `illuminaHumanv4.db` 1.26.0 (the A0 source), table `ExtraInfo` (NuID to IlluminaID) | 47,008 of 47,008 nuIDs found; 0 map to more than one probe |
| (b) `lumiHumanIDMapping` 1.10.1, table HumanHT12_V4_0_R2_15002873_B (nuID to Probe_Id) | 47,008 of 47,008 found; 0 multi-mapped; **47,008 of 47,008 agree with (a)** |
| (c) First-principles decoding: each nuID body character is one base triplet (A, C, G, T = 0–3; 64-symbol alphabet) | Decoded sequence equals the annotated 50-base `ProbeSequence` for **47,008 of 47,008** |

**What the A0 classification gives** (the HT-12 v4 / GPL10558 classification already used for GSE63061):

| Class | Probes |
|---|---|
| Eligible | 33,804 probes over **20,838 Entrez genes** |
| Unmapped (no package gene) | 11,291 |
| Excluded (multi-Entrez) | 1,719 |
| Not in snapshot | 194 |

**Options:**

| Option | Description | Assessment |
|---|---|---|
| **D19-1 (recommended)** | nuID to ILMN through the pinned `illuminaHumanv4.db` ExtraInfo; then the approved A0 rule exactly as for GSE63061. Code verifies (b) and (c) at run time and fails closed on any disagreement. | Reuses the approved annotation and snapshot, so GSE63061 and GSE140829 genes are defined identically. No new resource, because the package is already pinned. Identity is sequence-derived. |
| D19-2 | nuID to Entrez directly from lumiHumanIDMapping | A second annotation snapshot (2016-era), single-valued by construction, so ambiguity cannot be represented. Breaks comparability with A0. |
| D19-3 | The GPL15988 GEO platform table | Not needed: the identity question is already settled by (a)–(c). |

The approval would be: "D19-1: nuID translated to ILMN probe ID via the pinned illuminaHumanv4.db ExtraInfo NuID
field, verified at run time against lumiHumanIDMapping R2 and nuID sequence decoding; gene mapping by the approved A0 rule."

## 2. D11: the GSE140829 input

**Series Matrix facts:**
- 587 arrays: 204 AD, 249 Control, 134 MCI.
- Sex: 305 F / 282 M. `age_at_draw` 61–89. Both are complete.
- `batch`: 19 levels, two of them singletons (batches 27 and 35).

**Options** (v7:614):
- **(a)** the Series Matrix with a batch fixed effect. This is the documented proposal and matches v7 §4.1.
- **(b)** the ComBat-corrected final file. The record notes it has 36 fewer samples and that ComBat on
  diagnosis-imbalanced batches can distort effects.

Recommendation: **(a)**. The S13 alternative (the ComBat file) can stay open, because it blocks only S13.

## 3. GSE140829 eligibility rules (required before any analysis; v7:642)

R1, R3, R4 and R11 are GSE63060 definitions. Proposed GSE140829 analogues, for the PI to review:

| Rule | Proposal |
|---|---|
| Universe (R1) | All 587 Series Matrix arrays |
| Contrast (R3/R4) | AD vs Control; MCI outside the contrast (P1) |
| Ambiguous labels (R5) | None: the deposited field has three clean values |
| Covariates (R2-COV) | age_at_draw, Sex, batch (complete); unit = batch |
| Submitter `connectivity_zscore` | Not used: our own QC (R8 under V-A, R9) applies. After D19, R8 becomes assessable, because XIST and the Y probes map. |
| `apoe_status` | Not used (not a prespecified covariate) |
| D10 wording | "Replication cohort; independence from AddNeuroMed participants unverified". Never "independent". |

## 4. What follows once D19, D11 and the rules are approved

Each step reuses runners that are already tested:
1. eligibility, then C1 duplicate review, then QC Stage A/B;
2. the GSE140829 rule-applied exclusion list comes back to you for approval;
3. C-c, C-a, C-b replication of the locked signature (here the word "replicated" is permitted, per v6 §8.6);
4. the frozen ML model applied once, if you authorize it.

This is the first evidence that is not limited by the AddNeuroMed overlap.
