# BIO-MB-001: model sprint plan (2026-10-18)

**NONCANONICAL PLANNING ARTIFACT. PROPOSED FOR PI REVIEW. NOT APPROVED.**

- This file changes no SAP decision and authorizes nothing.
- No real-data computation, QC, differential expression or model was run in preparing it.
- No expression value was read: the data checks hashed files against their download manifests and read metadata only.
- Canonical governing documents:
  - `reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md` (the SAP; SHA-256 `161cf12d…`);
  - `reports/phase3b/v7/DECISIONS_REQUIRED_BEFORE_SAP_APPROVAL.md` (the brief; `2cfcd4af…`).

## 1. Verified state (2026-10-17T20:20Z UTC, which is 2026-10-18 local)

| Item | Verified fact |
|---|---|
| Git | `main` at `f4d7810`; 0 staged; `M README.md`, `M src/biomarker_project/__init__.py` (user changes, hashes `8e52c51b…` and `5b6fc851…`); 50 untracked entries |
| SAP status | v7:3 reads "PROPOSED DRAFT FOR REVIEW. Not approved, not frozen." |
| D8 | **Not approved.** v7:611 says "D8 approval (D8-8) remains pending". D8-1 to D8-6 were implemented 2026-10-18 (`reports/environment/d8_closure_review/2026-10-18/`). |
| Final D8 audit | Delivered in conversation (2026-10-18), with no file record. It recommended Option A: D8 stays blocked until source-code identity is implemented. |
| Code identity (D8-3) | Specified in the execution report; **not implemented; not in the SAP** |
| Annotation pin | Not created (`reports/annotation_audit/annotation_pin/` is absent) |
| Raw data | All 20 locally present files listed in the six download manifests match their recorded SHA-256. One listed file is absent: `GSE99039_RAW.tar` (`SKIPPED_OFFLINE`, never downloaded). |
| Machine learning in the SAP | **Active inherited text** (v2:550–551, kept active via v5:76, v6:50 and v7 §0.1): "only with nested cross-validation inside discovery; never tuned on validation cohorts", **exploratory only**. No ML decision, protocol or model is approved. |
| "19-subject overlap" between GSE63060 and GSE63061 | **Not in the repository evidence.** The overlap checks (`reports/dataset_audit/overlap_checks.json`) found 0 shared participant codes and 0 shared array barcodes, and state that this "does NOT establish participant independence". The SAP labels overlap as *possible* (H9, v7:340). The figure 19 is treated here as a PI-supplied premise that hasn't been verified. The plan assumes overlap exists either way. |

## 2. (A) Gate register

**Already approved** (SAP §11):
- D0 (governance only);
- D1 (E2) and D1-H wording;
- D2, D3, D4, D5 (b), D17 (A);
- D6 partial: A–G, including the GPL570 Option A and Illumina A0 mappings;
- D18 partial;
- D22 partial (V-A, rows 1–6);
- the 2026-10-17 documentation decisions: the annotation pin definition, the real-data computation rule (v7:112) and the D8 scope (these are distinct from SAP D1–D3);
- D8-1 to D8-6 (2026-10-18).

| # | Gate | Blocks | Depends on | Recommended option | Authorization status |
|---|---|---|---|---|---|
| G1 | D8-3 implementation: a source-tree identity module, a synthetic-only test, and the SAP lock §7 and A6-row edits | D8-8 (under Option A) and every real-data output | — | Implement as in §6 of this plan | **NOT AUTHORIZED** (source and canonical edits) |
| G2 | D8-8, D8 approval | Tier B step 2 onward and every real-data computation (v7:112) | G1 | Approve once G1 is verified | **NOT AUTHORIZED** (PI decision) |
| G3 | Creating the annotation pin record (Tier B step 2) | Eligibility, QC, discovery, the lock | G2; C15 and A0 artifacts verified or regenerated in the D8 environment (v7:112) | Create per D1 at `reports/annotation_audit/annotation_pin/v1` | **NOT AUTHORIZED** (separate) |
| G4 | Tier B step 3, eligibility (D2 rules R1–R13) on GSE63060 | Duplicate review, QC | G3 | Run the approved D2 rules | **NOT AUTHORIZED** |
| G5 | Remaining D18 parts (duplicate review, Tier B step 4) | QC Stage A, sample sets | G4 | See brief §D18 | **Open decision** |
| G6 | QC Stage A on real GSE63060 (D5 option (b) and D22 V-A are approved) | Discovery fits | G5 | As approved | **NOT AUTHORIZED** |
| G7 | D7 (c₁–c₃, failure-rule alternative) | Model fits (A4) | — | v5 §4.4 procedure with values set | **Open decision** |
| G8 | H1 adjustment set, test, threshold and multiplicity | Discovery inference | — | Proposed in the brief | **Open decision** |
| G9 | D15 (discovery q-level, cap 200, coverage) | Discovery fits and selection | — | q < 0.05; cap 200 (both [PROPOSED]) | **Open decision** |
| G10 | D16 (sensitivity set, S6 method) and D21 (if S11) | Use of discovery results | — | — | **Open decision** |
| G11 | D20 and D12 (claim families, O/X, W, C-c) | Validation claims and the lock | — | O1+X1, W1 (proposed) | **Open decision** |
| G12 | D11 and D19 (GSE140829 input, GPL15988 mapping) and the GSE140829 eligibility/label rules (v7:642) | All GSE140829 analyses | — | — | **Open decision** |
| G13 | D13 with δ and its scale (GSE99039) | Specificity claims | — | — | **Open decision** |
| G14 | D14 (pathways), D9, D10 | Exploratory pathways; E1; wording | — | — | **Open decision** |
| G15 | ML protocol (exploratory, nested cross-validation inside discovery only) | Any classifier | G2–G9 at least; a written ML protocol | §5 below | **No approved protocol** |
| G16 | SAP approval and freeze | Confirmatory claims | All the above | — | **NOT AUTHORIZED** |

## 3. (B) Data readiness

File presence is not QC status. No QC has run on any cohort.

| Cohort | Role (SAP) | Platform | GEO samples (audit) | Local files (SHA-256 vs manifest) | Annotation status | Readiness |
|---|---|---|---|---|---|---|
| GSE63060 | Discovery (D1, D3) | GPL6947 | 329: AD 145, CTL 104, MCI 80 | Series matrix, normalized, non-normalized, RAW.tar, filelist: all OK | D6-G A0 approved; classification table exists; **pin not created** | Input approved (D3); eligibility, duplicates and QC **not run** |
| GSE63061 | Descriptive effect correlation only (v7 §4.5); "Replicated" is not used | GPL10558 | 388: AD 139, CTL 134, MCI 109, ambiguous 6 | All 5 OK | D6-G A0 approved | Labels for the 6 ambiguous samples undecided; possible overlap with GSE63060 (H9) |
| GSE140829 | External validation | GPL15988 | 587: AD 204, HC 249, MCI 134 | 3 files OK; the normalized file has 36 phenotype-only records | **D19 unresolved** | Blocked: D11, D19 and the eligibility/label rules (v7:642) |
| GSE99039 | Specificity (PD and other neurological conditions) | GPL570 | 558 | Series matrix and filelist OK; **RAW.tar absent** (not needed under the current inputs) | D6-F Option A approved | Blocked: D13 and δ |
| GSE165082 | Exploratory only; never pooled with microarray data (v2:549, active) | RNA-seq (GPL11154) | 26 (30 described) | Counts and series matrix OK | Not applicable (gene IDs) | Orthogonal or exploratory only; no PD-versus-AD claim |
| GSE165081 | **Excluded from transcriptomic analysis**: methylation, future extension only (v1:301; v2:549) | GPL13534 (methylation) | 28 | Sample sheet, detP and filelist OK | — | Exclusion confirmed; no planned use |

## 4. (C) Execution DAG

**What can run in parallel now** (no gate; each still needs the stated authorization):
- G1 (code, plus the SAP edit);
- decisions G5 and G7–G14, which are PI decisions and independent of one another;
- writing the ML protocol (G15).

**What must run in order:**

```
G1 → G2 (D8-8) → verify/regenerate the C15 and A0 artifacts in the D8 environment → G3 (pin)
   → G4 (eligibility) → [G5 decided] duplicate review → [G6] QC Stage A on GSE63060
   → [G7, G8, G9 decided] discovery limma fit (D8 runner, lmFit + eBayes(trend = TRUE))
   → [G10, G11 decided] selection, freeze and LOCK (v7 §7, plus code identity)
   → GSE63061 descriptive correlation | [G12] GSE140829 validation | [G13] GSE99039 specificity
   → [G15] exploratory ML, inside discovery only, with external evaluation only after the lock
```

## 5. (D) Modelling protocol (PROPOSED; requires SAP amendment or approval)

1. **Discovery (GSE63060 only).**
   - The primary model is the SAP's limma gene-level model: D1 E2 labels, age as a covariate (D4), G3 gene level, D17 with no extra filter.
   - Any classifier is exploratory (v2:550). It is fitted only inside GSE63060, using **nested cross-validation**: the inner loop handles tuning and feature selection, the outer loop estimates performance.
   - Feature selection, including the limma ranking, is redone inside each outer training fold, so selection doesn't leak into the performance estimate.
   - Folds are stratified by label and grouped by participant code, so duplicate arrays (D-clusters) never straddle folds.
2. **GSE63061, which may overlap with GSE63060.**
   - Never pooled with GSE63060 for training.
   - Never used for tuning, and never reported as independent validation.
   - Used only for the descriptive effect correlation (v7 §4.5), labelled for possible overlap (H9).
   - If a classifier is applied to it, the result is labelled "not independent; possible participant overlap".
   - No random split crosses GSE63060 and GSE63061.
   - If the PI documents the 19 overlapping participants with identifiers, those participants are removed from any GSE63061 evaluation and the removal is reported.
3. **External validation (GSE140829).**
   - The **locked** model is evaluated once, after D11, D19, D20 and D12 are decided. There is no tuning, recalibration or threshold choice on this cohort.
   - The platform (GPL15988) differs from discovery. Cross-platform score standardization needs D20 approval (v6:591).
4. **Specificity (GSE99039).** The locked score is applied to PD versus control and other neurological conditions versus control, under D13 and δ. Without δ there is no "specific" claim (v7 §8).
5. **Orthogonal evidence (GSE165082).**
   - RNA-seq, PD, 26 samples, exploratory.
   - The direction of locked genes is reported descriptively, never pooled with microarray data, and never used as an AD validation.
   - GSE165081 is not used.
6. **Metrics, if an exploratory classifier is approved.**
   - AUC with 95% CI from the outer folds (discovery) or by bootstrap (external), plus a calibration plot.
   - The decision threshold is fixed in discovery.
   - Reports carry the D1 caveat: about 41 AD-labelled samples were probably MCI at blood draw.
   - A classifier result is never a confirmatory claim.

## 6. (E) Source-code identity plan (for G1)

**Planning baseline**, computed read-only 2026-10-17T20:2xZ. It is tied to no output and is not a provenance claim for any earlier output.
- **Code set:** 61 files. Includes `src/biomarker_project/**/*.py`, `scripts/**/*.py`, `R/**/*.R`, `tests/**/*.py`, `config/**/*.y*ml`, `pyproject.toml`, `renv.lock`, `.Rprofile`, `renv/activate.R` and `renv/settings.json`; excludes `__pycache__`.
- **Git state of the code set:** 40 untracked, 1 modified.
- **Aggregate digest** (the SHA-256 of the sorted `path<TAB>sha256` list): `7ffb05d6b5706ff87eef231da29a2635b24d92a8fb242910e59eb1aad365db72`. Because 40 files are untracked, **a commit alone cannot identify this tree.**

**Proposed implementation** (needs authorization; no source change made). A new module `src/biomarker_project/code_identity.py`:
- `capture(root) -> dict`, which returns:
  - `git_head`;
  - `git_status_porcelain` (`--untracked-files=all`);
  - `files`: path, SHA-256 and git state for every file in the code set;
  - `aggregate_sha256`;
  - `environment_records`: the SHA-256 of `conda_explicit_base.txt`, `python_lock/v2` and `renv.lock`;
  - `dirty` (true/false).
- `verify(record, root) -> list[mismatch]`.
- Every real-data runner writes `code_identity.json` next to its outputs, and its hash enters the output manifest.

**Tests** (synthetic, in a temporary git repository): capture is stable on an unchanged tree; any byte change, a new untracked file, or a mode change alters the digest; `verify` reports the exact mismatches.

**SAP edits** (canonical; need authorization):
- lock §7 gains "8. The source-tree identity record (code set, aggregate SHA-256, git HEAD and status) and the D8 environment record hashes";
- the v7:112 A6 row gains the requirement that every real-data output carries a verified identity record.

## 7. (F) Real-data execution checklist (each run)

- [ ] **Authorization:** record the authorizing PI instruction and date, and check the relevant gates in §2 against the SAP.
- [ ] **Inputs:** path, SHA-256 matched against the download manifest, and the D3-approved file only.
- [ ] **Environment:** `.venv/bin/python` (D8-4 boundary); `Rscript R/limma_de.R --check <pins>` exits 0; record the environment hashes.
- [ ] **Code identity:** `code_identity.json` captured before the run and verified after it.
- [ ] **Sample labels:** the GEO `status` field (D1 E2); a label table with counts, and the reconciliation per the D2 R-rules.
- [ ] **Exclusions:** eligibility (P), QC (Q) and identity exclusions, each with a reason code and the §5.2 precedence rule; arrays counted at every step (a sample-flow table).
- [ ] **Annotation:** the pin record SHA-256 is cited (v7:465); probe-to-Entrez per D6-F or D6-G; counts of eligible probes and genes.
- [ ] **Preprocessing:** none beyond D3 ("as deposited"); D17 adds no filter; G3 gene-level averaging.
- [ ] **Model:** design matrix, covariates (age per D4), D8 limma settings, seed; for ML, the nested cross-validation folds are recorded.
- [ ] **Validation:** only on locked artifacts, once; the lock SHA-256 is cited.
- [ ] **Metrics:** as prespecified; nothing post hoc without an "exploratory" label.
- [ ] **Logs:** stdout, stderr and the R `sessionInfo`, with timestamps (UTC).
- [ ] **Output provenance:** the SHA-256 of every output, the manifest, and a determinism re-run where feasible; failures are reported as they occurred.

## 8. Decisions needed from the PI, ranked by what blocks the next stage

1. **Authorize G1:** the code-identity module, its synthetic test, and the two SAP edits.
2. **D8-8 approval** once G1 is verified.
3. **Authorize G3:** verify or regenerate the C15 and A0 artifacts in the D8 environment, then create the annotation pin.
4. **Authorize G4:** eligibility on GSE63060.
5. **Decide G5:** the remaining D18 duplicate-review parts.
6. **Authorize G6:** QC Stage A on real GSE63060.
7. **Decide G7, G8 and G9:** D7 values, the H1 test and multiplicity, and D15. These gate the first discovery model.
8. Then G10–G14 for the lock and the external cohorts, and G15 if an exploratory classifier is wanted.

## 9. Realistic by 2026-10-19

| Scenario | Achievable |
|---|---|
| **With items 1–4 authorized promptly** | G1 implemented and tested, D8-8, the pin created, and GSE63060 eligibility run |
| **Also items 5–6** | Possibly QC Stage A |
| **Not achievable by 2026-10-19 without skipping gates** | A discovery model fit, any lock, any validation, any classifier. These need G7–G11 decided first. |
