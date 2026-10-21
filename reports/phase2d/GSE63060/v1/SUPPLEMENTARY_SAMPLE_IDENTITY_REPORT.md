# BIO-MB-001 Phase 2D — Supplementary sample-identity investigation, GSE63060 (v1)

Status: **for review — supplements not obtained; no population chosen or frozen; no sample
reclassified, excluded or identified.** No expression data were analysed. Builds on
`reports/phase2c/GSE63060/v2/SAMPLE_IDENTITY_AND_COHORT_HISTORY_REPORT.md` (unchanged).

Evidence labels: **DIRECT** (stated in a source or verified in local files), **INFERENCE**,
**UNRESOLVED**.

## 1. Retrieval outcome (DIRECT; details in `sources/PROVENANCE.json`)

Supplementary links printed in the supplied PDFs:

| Paper | Printed link | Location in PDF |
|---|---|---|
| Lunnon 2013 (doi 10.3233/JAD-2012-121363) | http://dx.doi.org/10.3233/JAD-2012-121363 | p.738 |
| | http://www.j-alz.com/issues/33/vol33-3.html#supplementarydata03 | p.741 (Supplementary Table 2) |
| Lunnon 2012 (doi 10.3233/JAD-2012-111592) | http://dx.doi.org/10.3233/JAD-111592 — **invalid as printed** (DOI resolver: "DOI Not Found") | p.686 |
| | http://www.j-alz.com/issues/30/vol30-3.html#supplementarydata04 | p.688 (supplementary Table 1) |

One attempt was made per official route, on 2026-10-09:

- **The journal's issue pages (j-alz.com)** now redirect to SAGE and return a bot-detection challenge
  (HTTP 403).
- **The DOI pages, the SAGE supplementary pages and the IOS Press pages** for both papers all return
  the same challenge (HTTP 403).

Challenges were **not** bypassed and no unofficial mirrors were tried. Europe PMC had already reported
no supplementary files and no open-access full text for either paper (Phase 2C v1).

**No supplementary file was retrieved; no tables or sheets were inspected.**

**For manual retrieval** (download the supplementary files from the article's "Supplemental
material" section):

- https://journals.sagepub.com/doi/suppl/10.3233/JAD-2012-121363
- https://journals.sagepub.com/doi/suppl/10.3233/JAD-2012-111592

Place the files, for example, in `~/Downloads/`; Phase 2D can then be repeated as v2.

## 2. What the supplements are described as containing (DIRECT, from the main texts)

| Paper | Supplementary item | Description in the main text |
|---|---|---|
| Lunnon 2013 | Supplementary Table 1 | Structural MRI measures: 34 cortical-thickness and 41 volume regions, 109 measures in total (p.740, p.745) |
| | Supplementary Table 2 | The 203 probes selected by t-tests in the training cohort (p.741) |
| Lunnon 2012 | Supplementary Table 1 | Differentially expressed probes, FDR < 0.01 (p.688, p.690) |
| | Supplementary Tables 2–7 | Gene significance and module membership per co-expression module (p.689–690) |
| | Supplementary Table 8 | Candidate and pathway genes: AD GWAS genes, respiratory chain, immune genes (p.690, p.695) |
| | Supplementary Table 9 | Blood-cell-type enrichment of dysregulated genes (p.697) |
| | Supplementary Table 10 | Brain-related gene sets used for module preservation (p.697) |
| | Supplementary Figure 1; glossary | KEGG pathway figure; WGCNA glossary (p.688, p.695) |

INFERENCE: every supplementary item is described as **probe-, gene-, module- or MRI-measure-level**.
**None is described as a participant or sample list**, a converter list, an exclusion list or a set of
visit dates. Even if obtained, the supplements are therefore **unlikely** to identify individual
GSE63060 samples. This is an expectation from the descriptions, not a verified fact; it needs
confirming once the files are available.

## 3. Status of each question

| Question | Status | Evidence available now |
|---|---|---|
| Can the 41 published MCI converters be mapped to GEO sample IDs? | **UNRESOLVED** | No sample-level source. Aggregate match only (Phase 2C v2: GEO AD 145 / 46M/99F = AD 104 + MCIc 41) |
| Are the 37 M-coded GEO AD samples explicitly identified as converters? | **UNRESOLVED** — no explicit identification exists in any examined source | Remains "supported, not proven" (sex split and mean age consistent with MCIc; code letters undocumented) |
| GEO MCI 80 vs MCInc 77; GEO total 329 vs 326 | **UNRESOLVED** | Lunnon 2012 reports 329 final chips; Lunnon 2013 excluded further chips for later diagnostic reclassification (other than MCI→AD) without IDs |
| 21 GEO samples younger than 65 despite the stated exclusion | **UNRESOLVED** contradiction | Both papers state the exclusion; GEO records ages 52–64 for 21 samples |
| The 64 controls in Sood et al.'s AD comparison | **UNRESOLVED** — outside the scope of the Lunnon papers and supplements | Sood et al. 2015 (Phase 2B v2) gives no list |
| Exclusions, matching, participant-code meanings, blood-draw / follow-up dates | Procedures DIRECT (main texts); **sample-level details UNRESOLVED** | Blood at first visit; 2-year conversion window; QC criteria — all without identifiers (Phase 2C v2) |

No identifiers were compared against local GEO metadata because no supplementary identifiers were
obtained. No sample identity was inferred from age, sex, site or aggregate counts.

## 4. Implications (no decision taken)

- The Phase 2C v2 conclusions are unchanged. Group-level evidence strongly indicates that GSE63060
  "AD" includes about 41 participants who were MCI at blood draw. Sample-level identification is not
  available from any examined source.
- Even if the supplements are obtained, they are unlikely to help (section 2). The more promising
  route to sample-level converter status, baseline diagnosis and visit dates is **data-owner
  documentation**: the GEO submitters (GSE63060 contributors A. Hodges, R. Howard) or AddNeuroMed
  data access.
- The pending design decisions remain: AD case definition, treatment of the under-65 samples, and our
  own prespecified QC. Any population rule must be justified without sample-level converter labels,
  or deferred until such labels are obtained from the data owners.

## 5. Limitations

- No supplementary material was obtained or inspected.
- The descriptions in section 2 come from the main texts and may be incomplete.
- Lovestone et al. 2009 remains unavailable.
