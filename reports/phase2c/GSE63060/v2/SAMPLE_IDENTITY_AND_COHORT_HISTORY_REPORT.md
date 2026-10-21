# BIO-MB-001 Phase 2C — GSE63060 sample identity and cohort history (v2)

Status: **for review — no population chosen or frozen; no sample excluded, relabelled or identified.**
No expression data were analysed; no differential-expression, feature-selection, pathway,
machine-learning or confirmatory statistics. v2 adds the two Lunnon et al. papers supplied by the
user. v1 (`../v1/`) is unchanged and its conclusions stand except where explicitly updated below.

Evidence levels: **ESTABLISHED** (directly stated in a source or verified exactly in local files),
**SUPPORTED, NOT PROVEN** (consistent evidence, no sample-level confirmation), **UNRESOLVED**.

Contents of this directory:

- `sources/` — `PROVENANCE.json` (paths, DOIs, SHA-256, pages inspected, licences) and a copy of
  Lunnon 2013, which is open access (CC BY-NC). Lunnon 2012 was not copied: it is marked "All rights
  reserved", so only its location and checksum are recorded.
- `reproduce_lunnon_comparisons.py` → `lunnon_vs_geo_comparison.csv`, `code_letter_sex_accounting.csv`.
  Run from the project root:
  `.venv/bin/python reports/phase2c/GSE63060/v2/reproduce_lunnon_comparisons.py`.

## 1. Sources inspected

| Source | Status |
|---|---|
| Lunnon K et al. 2013, *J Alzheimers Dis* 33:737–753, doi 10.3233/JAD-2012-121363 (user-supplied PDF, sha256 `d92a3d61…`) | **All 17 pages read.** Online supplementary Tables 1–2 not supplied, not inspected |
| Lunnon K et al. 2012, *J Alzheimers Dis* 30:685–710, doi 10.3233/JAD-2012-111592 (user-supplied PDF, sha256 `dbe7ff38…`) | **All 26 pages read.** Online supplementary Tables 1–10 and Figure 1 not supplied, not inspected |
| Lovestone S et al. 2009, *Ann N Y Acad Sci* 1180:36–46 | **Not found** in the project or `~/Downloads` (filename search); not inspected |
| AddNeuroMed data dictionary / participant-code documentation | Not found |

No network requests were made in this phase. Neither paper mentions GEO, GSE63060, GSM accessions,
array barcodes or participant codes.

## 2. Evidence table

| # | Question | Source evidence (quotation ≤15 words or paraphrase) | Location | GEO comparison (VERIFIED locally) | Confidence | Limitation |
|---|---|---|---|---|---|---|
| 1 | Which study produced the GSE63060 data? | Paraphrase: 356 RNA samples (116 control, 127 MCI, 113 AD) on HT-12 v3, arrays processed at UCLA, lumi VST + quantile normalization; after chip QC "leaving 329 chips in the final analysis" | 2012 p.687–688, Methods and Table 1 | GSE63060: 329 samples, HT-12 v3 (GPL6947), lumi processing statement | Direct for the paper; the GEO link is supported (same count, platform and processing; Sood 2015 cites these papers for cohort 1) | No source names the GEO accession |
| 2 | Timing of blood collection | "RNA was extracted from all samples from their first visit" | 2012 p.687, Whole blood RNA extraction | — | Direct (cohort level) | Per-sample visit dates not available |
| 3 | Definition of MCI converters | 2012: MCI who converted to AD "within 2 years post-sampling (N = 42)" were analysed by their status at sampling. 2013: within 2 years of baseline, some MCI progressed to clinical AD (MCIc); others remained MCI (MCInc) | 2012 Table 1 footnote p.688; 2013 p.739 | — | Direct | Diagnosis dates not available |
| 4 | Are GEO "AD" labels baseline AD only? | 2013 groups: AD 104 (32M/72F); MCIc 41 (14M/27F); controls 104 (42M/62F); MCInc 77 (39M/38F) | 2013 Table 1 p.741 | GEO AD 145 (46M/99F) = **AD + MCIc exactly** (145; 46M/99F); GEO CTL 104 (42M/62F) = 2013 controls exactly; mean ages 75.40 vs 75.29 and 72.38 vs 72.37 | Aggregate match exact; meaning **supported, not proven** | No sample list in either paper |
| 5 | Which GEO AD samples are converters? | Neither paper lists participants | — | 37 AD with "M" codes (14M/23F, mean age 75.03) vs MCIc 41 (14M/27F, 75.0). Adding 4 females from the 11 London (no-letter) AD samples would close the sex gap | **Supported, not proven** for the 37; the other ~4 unidentifiable | Code letters undocumented; no IDs |
| 6 | Participant-code meaning | Sites listed: London, Kuopio, Lodz, Perugia, Thessaloniki, Toulouse, plus the London Dementia Case Register | 2012 p.687 | Code prefixes KPO, LDZ, PRG, THS, TLS, LND match these cities; letters A/C/M agree with diagnosis except 37 M→AD and 1 C→MCI | Prefixes = sites: supported; letters = baseline group: supported, not proven | No source defines the codes |
| 7 | Original sample QC | 2012: chips removed for detection rate <80%, XIST/recorded-gender discrepancy (1 AD, 1 control), 20 low-detection, 2 MCI (FTD conversion, meningioma), 1 AD revoked diagnosis, 1 AD low RIN; RIN >7.0 required. 2013: 30 chips excluded (low detection; XIST and/or SNP-based gender mismatch; diagnostic reclassification other than MCI→AD), leaving 326 | 2012 p.688 Table 1 footnote; 2013 p.740 | GEO = 329 = the 2012 post-QC count, so the QC-failed chips are presumably not GEO samples | Direct (procedures and counts) | **No sample IDs** for any exclusion; not reproducible by sample |
| 8 | XIST probe used for the sex check | 2013: ILMN_1764573. 2012: "ILMN 26235" | 2013 p.740; 2012 p.688 | ILMN_1764573 is the only XIST probe in the GPL6947 manifest and is in GEO; "ILMN_26235" is not a valid probe ID | 2013 consistent; 2012 ID likely a typo (interpretation) | — |
| 9 | Age inclusion | Both papers: subjects excluded if younger than 65 | 2012 p.687; 2013 p.739 | **21 GEO samples are under 65** (AD 10, CTL 8, MCI 3), yet GEO mean ages match the papers' tables | **Contradiction**, unresolved | — |
| 10 | Probe filtering | 2013: probes not expressed in any sample removed, leaving 38,311. 2012: non-varying probes removed, leaving 19,161 for analysis | 2013 p.740; 2012 p.688 | GEO normalized / Series Matrix: 38,323 probes | Close to 2013 (12 probes apart); not identical | Filter rule not exactly reproducible |
| 11 | Normalization | "variance stabilization and quantile normalization" (lumi), described **before** the removal of outlier chips | 2012 p.688; 2013 p.740 | Phase 2A/2B: deposited values are not a plain quantile normalization of the deposited arrays; an extra normalized array (`4856076038_D`) is in the supplementary files | Supported, not proven, that normalization included arrays later removed | Order of operations not stated explicitly |
| 12 | Matching for the 64 vs 67 controls (Sood 2015) | Lunnon papers do not describe Sood's matched subset | — | — | Unresolved | Different study |
| 13 | GSE63061 (71/72 controls; 31/30 MCI) | Lunnon papers cover only the HT-12 v3 (batch 1) cohort | — | — | Unresolved | Not covered |

## 3. Established findings

1. **Blood was collected at baseline (first visit)** for this cohort, and MCI converters were defined
   by conversion to clinical AD **within 2 years after sampling** (Lunnon 2012 p.687–688; Lunnon 2013
   p.739). In both papers converters were analysed as MCI, their status at sampling.
2. **The GSE63060 group sizes and sex splits equal Lunnon 2013's groups when MCI converters are
   counted as AD.**
   - GEO "AD": 145 (46M/99F) = 104 AD + 41 MCIc (46M/99F).
   - GEO controls: 104 (42M/62F) = the 2013 controls.
   - Mean ages agree to within 0.11 years.
   - GEO's total of 329 equals the Lunnon 2012 count of chips in the final analysis.
3. **The original authors applied array QC before analysis**: detection rate, XIST-based sex check,
   RIN, comorbidity, and diagnostic reclassification. They publish **no sample identifiers** for any
   exclusion, so these exclusions cannot be reproduced or mapped to GEO samples.
4. **Both papers state an exclusion of subjects younger than 65, but GEO contains 21 such samples.**
5. Neither paper defines participant codes, mentions GEO, or addresses Sood et al.'s 64-control
   comparison or GSE63061.

## 4. Supported, not proven

1. **GEO's "AD" status for GSE63060 reflects diagnosis after follow-up, not diagnosis at blood
   draw**, for about 41 MCI-to-AD converters. On the papers' own definitions, their blood was taken
   while they had MCI.
2. **The 37 GEO "AD" samples with "M" participant codes are those converters.** Their sex split
   (14M/23F) and mean age (75.03) are consistent with MCIc (14M/27F, 75.0). The remaining ~4 converters
   would have to be among the 11 London AD samples, whose codes carry no group letter. They cannot be
   identified; the code-letter meaning is not documented.
3. Code prefixes denote sites (KPO = Kuopio, LDZ = Lodz, PRG = Perugia, THS = Thessaloniki, TLS =
   Toulouse, LND = London).
4. The deposited normalized values come from a normalization that included arrays later removed by QC.
   This would explain the unlabelled array `4856076038_D` and the Phase 2B finding that the values are
   not a plain quantile normalization of the deposited arrays.

## 5. Unresolved (with what would resolve each)

| Question | Status | What would resolve it |
|---|---|---|
| Sample-level identity of converters (which ~41 GEO AD samples) | Partially clarified at aggregate level only | Supplementary tables of Lunnon 2012/2013 (if they list samples), or the submitters / AddNeuroMed data access |
| GEO MCI = 80 vs MCInc 77 (+2M/+1F); GEO 329 vs 2013's 326 | Unresolved | Same; Lunnon 2013's additional "reclassification" exclusions are not identified |
| 21 GEO samples under 65 despite the stated exclusion | Unresolved contradiction | AddNeuroMed protocol (Lovestone 2009) or the submitters |
| Participant-code convention | Unresolved | Lovestone 2009 or AddNeuroMed documentation |
| Whether GEO AD/MCI labels changed over time | Unresolved | GEO submitters |
| Sood 2015: 64 vs 67 controls (GSE63060) | Unresolved — not addressed by these papers | Sood et al. authors |
| GSE63061: 71 vs 72 controls, 31 vs 30 MCI | Unresolved — not addressed | Sood et al. authors / GSE63061 submitters |
| Patel 2020 exclusions (2 sex mismatches, 10 outliers) | Unresolved — no IDs | Patel et al. code or data (not examined) |

Clarification relative to v1: the earlier comparison with the Lunnon 2013 abstract (104 AD vs GEO 145)
is now explained at aggregate level. GEO's AD group includes the 41 converters. v1's "108 vs 104 /
117 vs 118" calculation assumed every converter carries an M code; the sex accounting in section 4
shows about 4 converters must instead be London samples with no group letter.

## 6. Implications for the scientific options (no decision taken)

- **Case definition becomes a concrete, evidence-based design choice.** With good support, about 28%
  of GSE63060 "AD" samples (≈41/145) were MCI at blood draw and received an AD diagnosis within two
  years. Two prespecifiable definitions follow:
  - (i) "AD at blood draw": baseline AD only. This cannot be implemented exactly from GEO; it would
    rest on the undocumented code letters and would leave ≈4 London converters unidentifiable.
  - (ii) "AD by end of follow-up": GEO's label as deposited.

  These describe different biological states, so the choice affects any reproducibility claim.
- **The evidence does not justify a population decision by itself.** It sharpens the question but
  identifies no samples. Any rule using code letters would rest on an undocumented convention, and the
  under-65 contradiction and the 3 unexplained MCI samples remain.
- **QC must be our own.** The original authors' exclusions are documented but not identifiable, and
  were already applied before deposit. Later QC (Patel 2020) is also unidentifiable. Any sex-check or
  outlier procedure for this project must be prespecified and run by us.
- GSE63061 and the Sood-paper discrepancies are untouched by these sources.

## 7. Recommended next scientific decisions (for the PI; not taken here)

1. Decide the **AD case definition** for the primary analysis (baseline-diagnosis AD vs AD by end of
   follow-up). Decide whether a code-letter-based sensitivity analysis is acceptable, given that the
   convention is undocumented.
2. Decide how to treat the **21 participants under 65** given the stated cohort criterion.
3. Prespecify **our own QC**: an XIST/Y-gene sex check and an outlier rule, applied blind to
   case-control expression differences.
4. Seek the Lunnon 2012/2013 **supplementary files** and Lovestone 2009 (or contact the submitters or
   AddNeuroMed) for sample-level converter status before any population is frozen.
