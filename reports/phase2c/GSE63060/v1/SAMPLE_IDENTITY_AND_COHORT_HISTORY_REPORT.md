# BIO-MB-001 Phase 2C — GSE63060 sample identity and cohort history (v1)

Status: **for review — no population chosen or frozen; the research question is unchanged.** No
expression data were analysed in this phase; no differential-expression, feature-selection, pathway,
machine-learning or confirmatory statistics were run. Builds on
`reports/phase2b/GSE63060/v2/POPULATION_ELIGIBILITY_REPORT.md` (unchanged).

Evidence labels: **VERIFIED** (directly confirmed in a retrieved source or the local files),
**REPORTED** (claimed by a publication or GEO record, not independently reproduced),
**INTERPRETATION**, **UNRESOLVED**.

Contents of this directory:

- `sources/` — retrieved records (read-only), with URLs, UTC retrieval times and SHA-256 in
  `PROVENANCE.json`. Sources that were checked but not stored are also listed there.
- `reproduce_comparisons.py` → `source_count_comparison.csv` (counts transcribed from the sources
  versus the local GEO phenotype tables). Run from the project root:
  `.venv/bin/python reports/phase2c/GSE63060/v1/reproduce_comparisons.py`.

## 1. Source access (VERIFIED)

| Source | What was obtained | Full text / supplement |
|---|---|---|
| Lunnon K et al., *J Alzheimers Dis* 2012;30:685–710 (PMID 22466004; doi 10.3233/JAD-2012-111592) | PubMed record and abstract | **Not accessed.** Not open access (Europe PMC: subscription required); the publisher site returned a bot-detection challenge (HTTP 403), which was not bypassed |
| Lunnon K et al., *J Alzheimers Dis* 2013;33:737–53 (PMID 23042217; doi 10.3233/JAD-2012-121363) | PubMed record and abstract | **Not accessed** (same reasons) |
| Lovestone S et al., *Ann N Y Acad Sci* 2009;1180:36–46 (PMID 19906259; doi 10.1111/j.1749-6632.2009.05064.x) | PubMed record and abstract | **Not accessed** (same reasons) |
| GEO search for series linked to these three PMIDs | 0 series | — |
| GEO search "AddNeuroMed" | 4 series: GSE63060, GSE63061, GSE63063, **GSE144858** | GSE144858 metadata retrieved (no data files) |
| PMC full-text search: GSE63060 with mismatch / mislabel / sample-swap / sample-identity terms | 8 articles; the relevant one retrieved: **Patel H, Iniesta R, Stahl D, Dobson RJB, Newhouse SJ, *J Alzheimers Dis* 2020 (PMID 32065794; doi 10.3233/JAD-191163; PMC7175937; CC BY-NC 4.0)** | Full text; the PMC record lists no supplementary files |
| PMC13360218 (*Diagnostics* 2026) | Checked | Uses all 329 GSE63060 samples as a cross-sectional cohort; nothing on conversion, timing, exclusions or IDs; not stored |

**To resolve the questions below, please provide** (PDF of the article plus all supplementary
files):

1. **Lunnon et al. 2013**, *J Alzheimers Dis* 33:737–53 — the most important. Its abstract describes
   the HT-12 v3 cohort with AD, control and "MCI likely to have an AD-endpoint" groups. The full text
   should give sample selection, QC, and the definition and follow-up of those MCI subjects.
2. **Lunnon et al. 2012**, *J Alzheimers Dis* 30:685–710 — the first analysis of the cohort, cited by
   Sood et al. for patient selection. Look for array QC, outliers and sample lists.
3. **Lovestone et al. 2009**, *Ann N Y Acad Sci* 1180:36–46 — AddNeuroMed design, visit schedule and
   (possibly) participant-coding conventions.
4. Optional: any AddNeuroMed data dictionary, or the GSE63060/GSE63061 submitters' documentation of
   the `description` codes and the "status" field.

## 2. Findings by question

### 2.1 Participant-code conventions and MCI-to-AD transitions

- UNRESOLVED: **no accessible source documents the participant-code convention** (for example
  KPO**M**0014, LDZ**CTL**016). The inference that the letter is the recruitment group remains an
  inference from naming patterns (Phase 2B).
- REPORTED (Lunnon 2013 abstract): the HT-12 v3 study comprised a training set of 78 AD and 78
  controls, and a validation set of 26 AD, 26 controls and **118 MCI "likely to have an AD-endpoint"**.
- VERIFIED (`source_count_comparison.csv`): against those totals (104 AD / 104 controls / 118 MCI),
  GSE63060 has **104 controls (exact)**, 145 AD and 80 MCI. Treating the 37 MCI-coded GEO "AD" samples
  as MCI gives 108 AD and 117 MCI — close to, but not equal to, 104 and 118.
- INTERPRETATION: consistent with the hypothesis that GEO's "AD" status for MCI-coded participants
  reflects a later diagnosis (conversion) rather than the diagnosis at blood draw. **Not
  established**: the sample sets are not documented as identical (326 in the abstract versus 329 in
  GEO), and the counts do not match exactly.
- REPORTED (GEO GSE144858, a separate AddNeuroMed blood DNA-methylation study, PMID 32745807): its
  design explicitly separates MCI participants who had MCI at **baseline blood extraction and
  progressed to AD within one year** (39 "converters") from stable MCI (68). This shows that
  conversion relative to baseline blood draw is a recorded concept in the consortium.
- VERIFIED: GSE144858 sample titles are generic ("Genomic DNA from blood N") and carry no AddNeuroMed
  participant codes or array barcodes, so **none of its samples can be linked to GSE63060 samples**.

### 2.2 Timing of blood collection relative to diagnosis

- UNRESOLVED for GSE63060: no accessible source gives per-sample or per-group timing. GEO records one
  "status" per sample with no visit or date.
- Indirect (REPORTED): the Lunnon 2013 abstract (MCI "likely to have an AD-endpoint") and the GSE144858
  design (baseline blood, conversion within one year) suggest conversion was tracked after baseline
  sampling in AddNeuroMed.

### 2.3 Sample exclusions, array outliers and sample-ID mismatches

- REPORTED (Patel et al. 2020, Methods and Table 1): GSE63060 and GSE63061 were used in their
  processed GEO form.
  - Sex was predicted from expression (R package massiR), and samples whose predicted and recorded
    sex disagreed were removed.
  - Outlying samples were then removed iteratively with a network-based method.
  - **GSE63060: 2 sex mismatches and 10 outliers removed** (249 → 237 AD and control samples; AD
    46M/99F → 45M/93F, controls 42M/62F → 40M/59F).
  - **GSE63061: 5 sex mismatches and 4 outliers removed** (274 → 265).
- VERIFIED: Patel's pre-QC GSE63060 counts equal the local GEO records exactly (AD 46M/99F, controls
  42M/62F, 249). Their probe counts (38,323 and 32,049) equal our Series Matrix counts.
- VERIFIED: Patel's pre-QC GSE63061 counts **do not** match the local records: 132 AD (51M/81F) and
  142 controls (55M/87F), versus GEO's 139 AD (54M/85F) and 134 controls (53M/81F). How their groups
  were formed from GEO's labels, including the transition labels, is not stated (UNRESOLVED).
- VERIFIED: **Patel et al. publish no sample IDs** for the removed samples: none in the article text
  and no supplementary files in the PMC record. Which 12 GSE63060 samples they removed cannot be
  determined from this source.
- From the arithmetic of their Table 1 (VERIFIED): the 12 removed GSE63060 samples comprised 7 AD
  (1 male, 6 female) and 5 controls (2 male, 3 female).
- INTERPRETATION: Patel et al. 2020 is a **plausible source for the project brief's two unattributed
  leads** (outlier exclusions; expression/phenotype mismatches detected as sex discrepancies). The
  brief gives no citation, so this attribution is **not confirmed**. Their exclusions are their own
  data-driven QC decisions, not cohort-documented exclusions.
- UNRESOLVED: whether Lunnon 2012 or 2013 report array QC exclusions or sample lists (full texts not
  accessed). Sood et al. 2015 report none (Phase 2B v2).
- No source mentions the Phase 2A file anomalies (the unlabelled array `4856076038_D`; the three
  empty-header AD columns).

### 2.4 Exact age/gender-matching procedure

- UNRESOLVED: no accessible source documents the algorithm, caliper or age bound. The only description
  remains the qualitative one in Sood et al. 2015 (largest possible group with the same age and gender
  balance; ~70 years).

## 3. The three published-count discrepancies (Sood et al. 2015 versus GEO)

| Discrepancy | What is VERIFIED | Source identifying the samples | Status |
|---|---|---|---|
| GSE63060: 64 controls in the AD comparison vs 67 flagged controls | The 3 controls not used are male (Table 1 41F/23M vs GEO 41F/26M); they cannot be reconstructed from GEO ages (Phase 2B v2: 0 of 2,600 combinations) | **None** | UNRESOLVED — identities not inferred |
| GSE63061: 71 vs 72 controls | Sood's Methods text and GEO both say 72; only Table 1 says 71; sex splits imply one female (44F/27M vs 45F/27M) | **None** | UNRESOLVED |
| GSE63061: 31 vs 30 MCI | Methods text and GEO both say 30; Table 1 says 31; sex splits imply one female (23F/8M vs 22F/8M) | **None** | UNRESOLVED |

- INTERPRETATION: the two GSE63061 differences are consistent with **one female participant counted
  as MCI in Table 1 but as a control in the Methods text and in GEO**. This could be a Table 1 error
  or a label change between analysis and deposit. No source identifies the participant, and none was
  inferred.
- VERIFIED: every GSM record in both series shows the same last-update date (30 May 2024; submitted
  6 Nov 2014; public 5 Aug 2015). GEO's records do not reveal what changed, so post-publication label
  revisions can be neither confirmed nor excluded (UNRESOLVED).
- Patel et al.'s GSE63061 counts (May 2018 download) also differ from the current GEO labels, a
  further indication that GSE63061 group assignment is not stable across sources (UNRESOLVED).

## 4. Sample identities established in this phase

**None.** No source examined names any GSE63060 or GSE63061 sample (GSM accession, array barcode or
participant code) in connection with exclusions, outliers, mismatches, conversions or the matched
subsets. Consistent with the brief, no identities were inferred to make counts match.

## 5. Implications for the project (INTERPRETATION; no decision taken)

1. **Case definition remains the critical open item.** The available evidence is consistent with the
   37 MCI-coded GSE63060 "AD" samples being MCI at blood draw, but does not establish it. Lunnon 2013
   (full text) is the most likely source to settle it.
2. **Published QC exists but cannot be reproduced by sample.** Patel et al. removed 12 GSE63060
   samples (2 sex mismatches, 10 outliers) without listing them. If this project wants equivalent
   checks, they must be prespecified and run as our own QC in a later phase, documented and applied
   blind to diagnosis-related expression results — not inherited from Patel et al.
3. **GSE63061 labels differ across sources** (Sood Table 1, Sood Methods / GEO, Patel), which matters
   for its role as a related-cohort consistency dataset. Use current GEO labels and document the
   discrepancies, unless a source resolves them.
4. Population options A–D from Phase 2B v2 are unchanged. Nothing here favours the flagged subset;
   the main open question (converters) affects every option.

## 6. Unresolved (carried forward)

1. Participant-code convention, and the conversion status and blood-draw timing of the 37 MCI-coded
   GSE63060 AD samples — needs Lunnon 2013 (and 2012) full text, or submitter documentation.
2. Identities of Sood's 3 unused male controls (GSE63060) and of the one GSE63061 participant counted
   differently.
3. Identities of the 12 GSE63060 (and 9 GSE63061) samples removed by Patel et al., and how Patel
   grouped GSE63061.
4. The matching algorithm and age bound used by Sood et al.
5. Whether GEO sample labels changed after 2015.
6. Confirmation that Patel et al. 2020 is the source of the brief's two leads.
