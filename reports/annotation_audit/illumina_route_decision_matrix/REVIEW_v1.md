# Independent review — Illumina annotation-route decision matrix v1

Reviewed 2026-10-13. **Review only.** The v1 deliverables are not modified. No correction below has
been applied. No mapping policy is selected or recommended, and D17, D19, D16, §5.2 and the
governing documents are unchanged. No GEO data were accessed, no QC or DE was run, nothing was
installed and nothing was committed.

## Scope and files reviewed

| File | SHA-256 (verified at review time) |
|---|---|
| `v1/DECISION_MATRIX.md` | `19ff46b8d4531e9000f2810f7fb98b71894450acc917df589af9296a72ef6ae9` |
| `v1/decision_matrix.tsv` | `4471726cf51d8c1e2ed278cb695c8d43fb344b51e7164a7bbc2794c36b0b166f` |
| `v1/decision_matrix_manifest.json` | `64224abae9bf4bc64772be053341b075f12316b5af99c6e434cf605704b7384b` |
| `illumina_route_comparison/v3/REPORT.md` | `0b21a7a42878acc0a6163376e95c1d0bcdc35818cb9dc6e666fa95faa5a76906` |
| `illumina_route_comparison/v3/comparison_manifest.json` | `f3c58d207446e0de2a180e8b04ecdada485ad00ac4e3f1718bf9c7e567955628` |
| `illumina_route_comparison/v3/metric_reconciliation_probes.tsv` | `d345ff888498ebce676af7de0941bf5512bfa12e73a31b00f55d3f14b1f3f3b0` |
| `illumina_route_comparison/v3/route_comparison_metrics.tsv` | `d693ab9d653e37a6307e1ddf91433504bedb1589c3ade3f00f39bc6209dacc4e` |
| `illumina_option_a/v1/*_probe_classification_PROVISIONAL.tsv` (3) | as in the matrix manifest (all match) |
| `reference/bioconductor_3.23/*.tar.gz` (4 used) | match `download_manifest.json` |

## Method

1. **Independent recomputation.** A review script in session scratch storage re-derived every figure
   in the matrix (not retained; see "Reproducibility of this review"). It does not import the
   project's code. It:
   - extracts the package SQLite databases from the retained tarballs;
   - queries `probes` / `accessions` (illuminaHumanv3/v4.db) and `HumanHT12_V4_0_R2_15002873_B ⟕ nuID_MappingInfo` (lumi);
   - builds its own accession → gene map as `org.Hs.eg.db` (`accessions` ∪ `refseq`, unversioned) → `genes.gene_id`;
   - reads Option A classes from the Option A v1 TSVs.

   The gene-history step itself cannot be re-derived, because `gene_history.gz` is not retained
   (see R7). The package gene columns of the Option A TSVs were re-checked against the raw package
   tables (all three match).
2. **Consistency checks.**
   - Every MD table row and limitation was string-matched to its TSV row.
   - All percentages were recomputed.
   - The transitions in `metric_reconciliation_probes.tsv` were tabulated.
3. **Reproduction.** The generator was re-run into a scratch directory (`--out-dir`). The test suite was run, and the overwrite refusal on v1 was confirmed.

## Results by check

### 1. Numerical claims vs TSV and retained sources — **all match**

Every number in `DECISION_MATRIX.md` equals the TSV entry and the independent recomputation.

| Figure | v3 (GSE63060) | v4 (GSE63061) | lumi HT-12 v4 R2 | Status |
|---|---|---|---|---|
| Probes (denominator) | 49,576 | 48,107 | 47,323 | ✔ (package probe set = Option A TSV set) |
| Option A eligible / % | 29,489 / 59.48 | 34,038 / 70.75 | 37,491 / 79.22 | ✔ |
| Accession unique / % | 29,326 / 59.15 | 33,811 / 70.28 | 31,130 / 65.78 | ✔ |
| Genes OA / acc / both / OA-only / acc-only | 19,226 / 19,100 / 19,085 / 141 / 15 | 20,926 / 20,779 / 20,759 / 167 / 20 | 23,743 / 20,593 / 20,356 / 3,387 / 237 | ✔ |
| Multi-probe genes OA / acc (C03) | 6,554 / 6,531 | 7,678 / 7,620 | 8,600 / 6,873 | ✔ |
| M1 both / concordant / discordant / % | 29,294 / 29,284 / 10 / 99.97 | 33,761 / 33,745 / 16 / 99.95 | 30,677 / 30,640 / 37 / 99.88 | ✔ |
| M2 total / same / different | 29,294 / 29,244 / 50 | 33,761 / 33,697 / 64 | 30,679 / 30,396 / 283 | ✔ |
| In M2 not M1 | 0 | 0 | 2 (ILMN_1712269, ILMN_3239440) | ✔ |
| Replacement → concordant | 40 | 48 | 244 | ✔ |
| Via replacement (all) | 59 | 76 | 1,760 | ✔ |
| No replacement / unexplained | 62 / 0 | 122 / 0 | 6,468 / 1 | ✔ (lumi 6,468 = 6,032 discontinued + 436 chain ends) |
| Accession unmatched / no accession / ambiguous | 1,379 / 17,719 / 1,152 | 2,390 / 10,226 / 1,680 | 16,193 / 0 / 0 | ✔ |
| Package multi-gene / no gene | 1,175 / 18,850 | 1,726 / 12,221 | 0 / 3,363 | ✔ |
| Unresolved OA / acc (%) | 20,087 (40.52) / 20,250 (40.85) | 14,069 (29.25) / 14,296 (29.72) | 9,832 (20.78) / 16,193 (34.22) | ✔ |
| Single-route OA-only (unres.+amb.) / acc-only | 195 (185+10) / 32 | 277 (267+10) / 50 | 6,814 (6,814+0) / 453 | ✔ |
| Version-suffixed accessions / probes with >1 accession | 0 / 12,377 | 0 / 14,399 | 0 / 0 | ✔ |
| Collisions: probes / successor genes / source genes | 43 / 28 / 30 | 50 / 32 / 35 | 1,165 / 783 / 892 | ✔ |
| Source dates | 2015-Mar17 | 2015-Mar17 | metadata `REFSEQ VERSION` = single space | ✔ (see R6) |
| org.Hs.eg.db | 2026-Mar18 | | | ✔ |

The conclusions are numerically correct, with one wording issue (R4):
- "99.88–99.97% (M1)" is correct.
- "Option A assigns more probes and genes on every platform" is correct.
- "Most M2 disagreements on lumi are resolved by replacement" is correct: 244 of 283 (86.2%).

### 2. Completeness and comparability — **complete**

- There are 45 TSV rows: C01–C15 for each of the 3 platforms.
- No cell is empty.
- The MD tables and limitations match the TSV exactly.
- The criterion wording and evidence formats are identical across platforms.

The lumi zeros in C08 and C12 are structural rather than comparable evidence (R2).

### 3. illuminaHumanv4 accession-route multi-probe-gene figure — **present and correct**

- **Present:** `DECISION_MATRIX.md` line 57 and the TSV row (illuminaHumanv4, C03) both give **7,620**. Option A gives 7,678.
- **Correct:** the independent recomputation gives 7,620 genes with ≥2 accession-unique probes, from the 33,811 unique probes across 20,779 genes.
- **Where the abbreviation came from:** the "7,678 / …" and "—" seen earlier appeared only in the chat summaries of the previous task, not in any deliverable.
- **Caveat:** this figure is new in v1, so the v3 manifest has no cross-check for it. The matrix labels it as such (see R9).

### 4. Status definitions and implied preference — **defined, but three framing issues**

- **Definitions are present** (MD line 11):
  - *decisive*: settles the choice alone; none qualify.
  - *supportive*: informs but does not settle.
  - *unresolved*: cannot be judged from retained evidence.
- **Not repeated in the manifest.** The manifest lists the status vocabulary but not these definitions.
- **No criterion is decisive.** Nothing states or implies an approved preference.
- **"Supportive" next to an "Advantage" invites tallying.** Read beside an Advantage column, "supportive" can be taken as "supports that route". Option A has 4 advantages per platform, the accession route 2 (v3/v4) or 0 (lumi). This reads as a lean towards Option A, even though the text disclaims weighting. See R1–R3.

### 5. Explicit denominators — **satisfied**

- C01 and C09 state "denominator: all platform probes", and every percentage shows n / N.
- C04 shows "% of {both-assign total}".
- Gene-level counts are labelled as gene level.
- Definitions line 10 states both denominators.
- Conclusion bullet 1 cites M1 percentages without the denominator. It is traceable to C04.

### 6. Consistent distinction of M1, M2, replacement, discordance, ambiguity, single-route — **mostly consistent**

- M1 and M2 are defined separately.
- M1 ⊆ M2 is stated and verified.
- The totals are not compared (but see the R10 wording).
- Replacement is handled in C05, genuine discordance in C06 (M1 only), ambiguity in C08 and single-route probes in C10. These categories do not overlap.

Issues: C08's criterion text misstates exclusion (R2); C05 omits replacement-derived discordant probes (R5); conclusion bullet 3 omits the probes that leave the comparison (R4).

### 7. Dates, provenance, collision definitions, accession limits — **accurate, with gaps**

- **Source dates** are read from the package metadata tables and are correct.
- **Collision definition** is correct. C13's wording, "replaced probe joins a gene that already has directly mapped probes", matches the Option A code: a probe in `eligible_via_history_replacement` whose successor equals the Option A gene of some `eligible_direct` probe. Probes, successor genes and source genes are counted separately and correctly.
- **Accession limitations** are correct. C12 states unversioned matching and that a match does not prove the probe hybridises to the current transcript.
- **Citation:** the C14 source "v5 §7.2–7.3" is correct. Those sections hold the G3 unit, multi-mapped exclusion, presence and measurability rules.

Gaps: R6, R7 and R8.

### 8. Cohort presence, D17, D19 — **correctly unresolved**

- C15 reads NOT ASSESSED / unresolved on all platforms.
- D17 and D19 are named as unresolved in the header, C14, C15 and the conclusions.
- The lumi section is labelled "GSE140829 applicability unverified (D19)".
- The v7 register is consistent: D17 is unapproved and D19 is unapproved (Enabling).
- Minor terminology issue in R10.

### 9. Manifest hashes and validation claims — **accurate; coverage narrower than the wording**

- All 11 input hashes equal the current files.
- Both output hashes equal the v1 files.
- Re-running into scratch reproduced byte-identical MD and TSV files. The manifest was identical too, because the `command` string does not include `--out-dir`.
- All 27 checks report OK.
- `pytest`: 180 passed.
- The v1 directory refuses an overwrite.

Coverage limitations: R9.

## Findings and proposed corrections (not applied)

Severity:
- **Moderate:** could mislead a policy reader.
- **Minor:** accuracy or completeness of wording.
- **Cosmetic.**

No numerical defect was found.

| # | Sev. | Affected entry | Issue | Proposed correction |
|---|---|---|---|---|
| R1 | Moderate | C01, C09, C10 (all platforms; Advantage = Option A) | The three rows are arithmetically dependent. C09 = N − C01. The C10 difference equals the C01 difference: 195−32 = 163, 277−50 = 227, 6,814−453 = 6,361. One coverage fact therefore appears as three "Option A" advantages, and a reader who counts advantages over-weights it. | Set C09 and C10 Advantage to "neither (derived from C01)", or add to Definitions: "C09 and C10 are restatements of C01; Advantage entries are not independent and must not be counted." |
| R2 | Moderate | C08 (v3, v4: Advantage "accession route"; lumi: "neither") and the C08 criterion text | (a) The Advantage compares two non-equivalent definitions (1,175 package multi-gene vs 1,152 accession-ambiguous). The row's own limitation says they "are not the same probes". (b) "Excluded under both routes" is incorrect. Each route excludes only its own ambiguous probes: 32 / 50 package-multi-gene probes are assigned uniquely by the accession route, and 10 / 10 accession-ambiguous probes are assigned by Option A (v3 / v4). (c) For lumi both zeros are structural, because each nuID has one EntrezID and one Accession, so they carry no comparative information. | (a) Advantage "not determinable". (b) Criterion: "Ambiguous assignments (one probe → more than one gene; each route excludes the probes it finds ambiguous)". (c) Add to the lumi limitation: "Zero by construction (one Entrez ID and one accession per nuID); not evidence of lower ambiguity." |
| R3 | Moderate | C11 (v3, v4: Advantage "accession route"; lumi: "not determinable" + status "supportive") | The v3/v4 Advantage rests on snapshot recency alone, which contradicts the row's limitation ("Newer is not automatically more accurate") and the "Suggested but not established" conclusion. The lumi status conflicts with the status definitions, because "not determinable" means "cannot be judged", which is the definition of *unresolved*. | v3/v4: Advantage "not determinable", or keep it but qualify the evidence as "(gene-ID snapshot recency only; not accuracy)". lumi: status "unresolved". |
| R4 | Minor | Conclusions, "Established", bullet 3 | "The remaining genuine disagreements are the M1 discordant probes" omits the 2 M2-different probes that leave the comparison. | "Of 283 lumi M2 differences, 244 become concordant after gene-history replacement, 37 remain M1-discordant (5 of them replacement-derived) and 2 leave the comparison because Option A has no eligible gene (ILMN_1712269, ILMN_3239440); all are listed in v3/metric_reconciliation_probes.tsv." |
| R5 | Minor | C05 accession-route evidence (all platforms) | The row reports replacement → concordant only. On lumi, 5 replacement-derived probes are M1-discordant (`different -> discordant [eligible_via_history_replacement]`). On v3/v4 there are 0. | Append: "; {k} replacement-derived probes remain discordant (counted in C06)", with k = 0, 0, 5. |
| R6 | Minor | C11 lumi Option A evidence; "Package source dates" section; manifest `package_metadata` | (a) "REFSEQ VERSION: not recorded" normalises the raw value, which is a single space. (b) The retained tarball's `DESCRIPTION` gives `Packaged: 2016-04-21 13:21:07 UTC`, a build date that bounds the mapping content and is not reported. (c) The package also holds other HT-12 v4 tables (`HumanHT12_V4_0_R1_15002873_B`, `HumanHT12_V4_0_R2_15002873_B_WGDASL`). This is relevant to D19 and not mentioned. | (a) "REFSEQ VERSION blank (single space)". (b) Add "package build date 2016-04-21 (DESCRIPTION `Packaged`; build date, not a mapping-content date)". (c) Add to the lumi C15 limitation or a D19 note: "the package also contains HT-12 v4 R1 and R2-WGDASL tables; which table applies is part of D19". |
| R7 | Minor | C11 limitation (all platforms); Option A history-dependent figures in C01–C03, C05, C07 and C13 | These figures depend on the gene-history v1 table. Its raw source (`gene_history.gz`, SHA `bcb85c8f…`) is not retained and cannot be re-obtained byte-identically (`ncbi_gene_history/SOURCE_RETENTION.md`). The 7,281 records it used are retained, so the figures are traceable but not re-derivable from raw source. The matrix does not say this. | Add to the C11 limitation: "Option A replacement figures trace to the retained gene-history v1 records; the raw gene_history.gz is not retained (SOURCE_RETENTION.md)." |
| R8 | Minor | C11 Option A evidence (TSV, standalone rows) | "Reconciled … by the approved gene-history procedure" can be read as approval for Illumina. The procedure is approved under D6-F for GPL570; Definitions line 7 qualifies this, but the TSV row does not. | "…by the gene-history procedure (approved for GPL570 under D6-F; provisional for Illumina)". |
| R9 | Minor | Validation section; manifest | (a) The 27 checks recompute only accession-route, M1/M2 and gene-overlap figures. Option A figures and C12 inputs are taken from the v3 manifest through the hash chain and not recomputed, and the C03 accession figure has no cross-check. (This review independently confirmed all of them.) (b) The check "no criterion is marked decisive without justification" only tests that none is decisive. (c) The manifest does not hash the generating script (`9871b7f4…`) or its test (`b25fc00a…`); `determinism` records only in-process runs; `command` omits the interpreter and any `--out-dir`; the Python version is not recorded. (d) The verify() hash checks raise on failure but are not listed among the recorded checks. | In a v2 (never in v1): (a) state the recomputed scope explicitly, or add Option A recomputation from the TSVs and a C03 consistency check (Σ probes = unique; number of genes = distinct genes). (b) Rename to "no criterion is marked decisive". (c) Add the script and test hashes, the independent-process result, the full command and the Python version. (d) List the input-verification checks. |
| R10 | Cosmetic | Several | (a) The lumi heading has nested parentheses. (b) C04 splits one joint metric across the two route columns. (c) C05 reads "M2 total X vs M1 total Y" although the limitation forbids comparing the totals. (d) C07 lumi "no replacement 6,468" does not show its composition (6,032 discontinued + 436 chain ends). (e) "D17 feature rule": the register titles D17 "Expression filters". (f) In code, ties in C02/C09/C10 default to "accession route", and C10 compares 185 rather than 195. Neither affects the current outputs. | (a) "lumi HT-12 v4 R2 — GSE140829 applicability unverified (D19)". (b) Put the M1 figures in one cell, or label the columns. (c) "M2 total X; M1 total Y (different metrics)". (d) Show the split. (e) "D17 (expression/feature filter)". (f) Use "neither" on ties and compare the full Option A-only total. |

## Overall assessment

- **Numerically sound and complete.** Every reported figure was independently reproduced from the retained sources and matches the TSV, the v3 manifest and the source tables. The v4 C03 accession figure (7,620) is present and correct.
- **Validation claims hold.** The manifest hashes, determinism and validation claims are accurate.
- **Unresolved items are handled correctly.** Cohort probe presence, D17 and D19 are left unresolved.
- **No defect invalidates a figure.** The issues are framing and completeness:
  - R1–R3 are moderate because the Advantage column can be read as a tally that favours Option A, or as favouring the accession route on recency. Neither was intended, and neither is supported as a policy argument.
  - R4–R10 are wording and provenance completeness.
- **No v2 has been written.** If the corrections are wanted, they belong in a new `v2/`, with v1 preserved. This review does not authorize or recommend any mapping policy.

## Reproducibility of this review

- **Scratch only, not retained:** the independent recomputation script and the regenerated copy of v1 are in session scratch storage, outside the project.
- **Key queries:**
  - `SELECT probe_id, gene_id FROM probes`;
  - `SELECT probe_id, accession FROM accessions`;
  - `SELECT t.Probe_Id, m.Accession | trim(m.EntrezID) FROM HumanHT12_V4_0_R2_15002873_B t LEFT JOIN nuID_MappingInfo m ON m.nuID = t.nuID`;
  - org map: `accessions ⋈ genes ∪ refseq ⋈ genes` (version suffix stripped).
- **Commands run:**
  - `.venv/bin/python scripts/annotation_illumina_route_decision_matrix.py --out-dir <scratch>`: validation OK, determinism identical, MD/TSV/manifest hashes equal to v1.
  - `.venv/bin/python scripts/annotation_illumina_route_decision_matrix.py`: refused, "already exists … nothing replaced".
  - `.venv/bin/python -m pytest -q`: 180 passed.
- **Repository state:** the only modifications in the working tree are the user's pre-existing ones (`README.md`, `src/biomarker_project/__init__.py`). This file is the only one added by the review.
