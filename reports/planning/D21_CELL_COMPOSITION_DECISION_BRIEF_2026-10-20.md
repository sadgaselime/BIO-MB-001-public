# D21: cell composition (S11) — decision brief (2026-10-20)

Noncanonical decision-preparation note. **Nothing here is approved.** No data were read, and nothing was downloaded or installed.

## Status in the plan

- S11 is in the approved sensitivity set: "Cell composition (D21)" (v6:709; D16 approved 2026-10-18, v7:619).
  Its method was never defined: D21 is "Not proposed" (v7:624).
- S11 is family B: its covariates are estimated from expression, so selection independence cannot be claimed under S11 (v7:229).
  It uses the primary set (v7:377), and it never alters the lock (v7 §3.2).
- **Timing disclosure.** The method is being chosen after the discovery, replication, specificity and classifier results
  are known. S11 itself was prespecified; its method was not. Every S11 output must therefore carry this label:
  "method chosen 2026-10-20, after primary results". The choice must be fixed before any S11 computation, with no tuning.

## Why it matters now (from accepted outputs)

- The strongest replicated genes in GSE140829 are ribosomal (RPS12, RPL32, RPS25, RPL22, RPS27A), plus ITGAM.
- In GSE99039, the only significant genes in IPD are TCIRG1 and NBEAL2.
- Ribosomal transcripts track lymphocyte content in whole blood; ITGAM, TCIRG1 and NBEAL2 are myeloid-associated
  (domain knowledge, not tested here). So a shift in leukocyte mix is a plausible alternative to disease-specific
  expression changes.
- None of the cohorts deposits measured blood counts, so any adjustment must be estimated from expression.

## Options

| Option | Method | Resource needed | Assessment |
|---|---|---|---|
| **K1 (recommended)** | Fixed marker-gene scores per major leukocyte class (neutrophils, monocytes, T cells, B cells, NK cells), each the mean diagnosis-blind z of a published marker list, entered as covariates | A published, versioned marker list, pinned as a file with its SHA-256 (candidates below) | Transparent, platform-agnostic through Entrez IDs, no tuning, works on all four Illumina/Affymetrix cohorts. Scores are relative abundance indices, not proportions |
| K2 | Reference-based deconvolution, e.g. LM22-type signature matrices | The reference matrix; licence terms must allow use and redistribution of results | Gives proportion estimates, but references are often licence-restricted, and cross-platform calibration is uncertain |
| K3 | No reference: surrogate variables or principal components as covariates | A Bioconductor package (e.g. sva), so an install | Captures composition and much else; not interpretable as cell composition |
| K4 | Drop S11 and state the limitation | None | Leaves the main interpretive question unanswered |

**Candidate K1 marker resources** (availability, exact version and licence are to be **verified before authorization**; I have
not checked them in this session):
- the MCP-counter marker lists (Becht et al., 2016);
- the immune/blood cell marker sets used by xCell (Aran et al., 2017);
- a blood-specific marker table published as a supplementary file.

The resource would be downloaded once, hashed, recorded under D8, and never edited.

## Proposed S11 scope (K1)

| Item | Proposal |
|---|---|
| **S11 as defined** | GSE63060 discovery model (H1) refitted with the five scores added as covariates; report the effect on the 200 locked genes (rank correlation of t, sign agreement and how many stay at q < 0.05). It never alters the lock |
| S11-ext (optional, **post hoc**, labelled) | The same covariates added to the GSE140829 C-c / C-a model and the GSE99039 Q1 model, reported side by side with the primary results |
| Scores | Marker genes are excluded from the locked-gene comparison where they overlap; scores are computed per cohort, diagnosis-blind |
| Claim boundary | A result robust to S11 is "not explained by these composition indices", not "independent of cell composition" |

## Decisions for the PI

1. **D21:** K1, K2, K3 or K4.
2. If K1 or K2: **authorization to identify, verify and download one named resource.** I would present the exact file, source,
   size and licence for your approval before downloading it.
3. Whether to include **S11-ext** (post hoc, labelled).
