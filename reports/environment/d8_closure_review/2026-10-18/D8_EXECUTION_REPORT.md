# BIO-MB-001: D8 decision and implementation batch, execution report (2026-10-18)

**Status:** this report records PI decisions D8-1 to D8-6 (explicit PI instruction, "D8 Decision and Implementation Batch", 2026-10-18) and the authorized implementation steps D8-1T, D8-2 and D8-7.

**D8 is not approved.** D8-8 was not authorized. Tier B is not unlocked, and the annotation pin was not created. No QC, differential expression, discovery, replication, specificity or ML analysis was run. Nothing was staged, committed, pushed or reset.

**Starting point:**
- the review `reports/environment/d8_closure_review/2026-10-17/D8_CLOSURE_REVIEW.md` (SHA-256 `217d59b1617c01c9a9d7c30c81c1ab62d9e0b69f0a5ad32ab6e287d0cebdd9cf`; its `SHA256SUMS` is `b84202fb…`);
- the rebuild test `reports/environment/d8_rebuild_test/2026-10-17/` (`SHA256SUMS` `49b4744c…`).

**Timestamps** are UTC. The system clock read 2026-10-17T20:04–20:10Z, which is 2026-10-18 local time (Asia/Muscat). The directory is dated with the local date given in the PI's instruction.

## 1. Preflight (2026-10-17T20:04:40Z)

| Check | Observed |
|---|---|
| Branch / HEAD | `main` / `f4d781001a91eb6c571dcb19364f4b4437c59a0d` |
| Staged | 0 |
| Working tree | 52 entries: `M README.md`, `M src/biomarker_project/__init__.py`, plus 50 untracked. Same as the review. |
| User changes | `README.md` `8e52c51b…3c57`; `__init__.py` `5b6fc851…dc1`; both intact |
| Review manifest | 4/4 OK |
| Rebuild-test manifest | 41/41 OK |
| SAP before editing | `a51437993c89485c674f9c011b09f3776b6b095a0106213ec51c99433cbb3b60` |
| Brief before editing | `a5870e8884a0dd887ae44a6a9dbc56775399a5db17a1e560c904d781cb09c6ac` |
| `renv.lock` | `fa51c7b9d10dd468fbeed8b2ad83b832eb8acc83adb828dc25361cbbc4359951` |
| `pyproject.toml` | `ca8c8bae73d6f4b894915914ad23b16b7f181f769b8c76e733362bcc9d5e1cfd` |
| Tested lock `requirements.hashes.TEST.txt` | `a7dc1ed210fcd2d5fbe103beceb02099ff1c565ad7141ae0915cdce084b2350f` (checksum-listed, OK) |
| Environment records | `conda_explicit_base.txt` `52e2e785…`, capture `manifest.json` `31e1b9fb…`, `python_lock/v1` (3 files), `d8_readonly_checks.json` `98561cf9…`, `D8_R_LIMMA_INSTALLATION.md` `a5b3d2ff…`. All match their recorded values. |

No discrepancy with the review was found.

**Pre-edit copies:** `reports/_pre_edit_copies/2026-10-18_D8_batch/`, holding:
- `canonical/` (SAP and brief);
- `biocversion_library/BiocVersion/` (16 files; `diff -r` against the live directory was identical before the install);
- `SHA256SUMS`, 18/18 OK.

## 2. Decisions implemented

The PI's instruction is the basis for each decision.

### D8-1 / D8-1T: BiocVersion

**Decision:** the official Bioconductor 3.23 sonoma-arm64 binary is the D8 reference artifact. Sub-option 1a was applied: the project library now holds that binary.

**Preconditions** (all passed; `evidence/biocversion_artifact_verification.tsv`):

| Check | Result |
|---|---|
| URL | `https://bioconductor.org/packages/3.23/bioc/bin/macosx/sonoma-arm64/contrib/4.6/BiocVersion_3.23.1.tgz` |
| Size | 6,054 bytes |
| MD5 | `dab387f575308ddd75ffaba682bd35fd`, equal to the `PACKAGES` index entry |
| SHA-256 | `cea69c8e00240f6f6c0aeb8f7123c39f21132df8487d96d98018b6e0ef5f9805`, equal to the review and to the 2026-10-12 record |
| `PACKAGES` index SHA-256 | `511af9af…c522`, identical to the copy downloaded 2026-10-17 |
| Archive members | Only `BiocVersion/…` paths (no absolute or `..` paths) |

**Target:** only `renv/library/macos/R-4.6/aarch64-apple-darwin23/BiocVersion/`.

**Baseline before the install:**
- `renv::status()`: "No issues found", synchronized `TRUE`;
- `BiocManager::version()` returns 3.23;
- `Rscript R/limma_de.R --check <D8 pins>` exits 0 (`evidence/r_status_before_install.txt`, `evidence/limma_pin_check_before.tsv`).

The pin check verifies versions only; it reads no data.

**Command:**

```
cd /private/tmp && Rscript --vanilla -e "install.packages('<SCRATCH>/BiocVersion_3.23.1.tgz', repos = NULL, type = 'binary', lib = '<project renv library>')"
```

It exited 0 with no output (`evidence/biocversion_install.log`).

**Post-install verification** (all passed):

| Check | Result |
|---|---|
| Installed files | 16, identical as a set to the archive members, and **all 16 byte-identical** to the archive, `DESCRIPTION` included (`evidence/biocversion_binary_archive_members_sha256.txt`) |
| Other packages | Every file of renv, BiocManager, limma and statmod is unchanged (`evidence/renv_library_sha256_before.txt` and `_after.txt`; 179 files in each) |
| `renv.lock` | Unchanged (`fa51c7b9…`) |
| `renv::status()` | "No issues found", synchronized `TRUE` |
| Versions | `BiocManager::version()` returns 3.23; `packageVersion("BiocVersion")` returns 3.23.1 |
| Installed metadata | `Repository: https://bioc.r-universe.dev`, `RemoteSha: 252d7c8f03a39a9b83f6de7e9dbf9a5ee6584365`, `Depends: R (>= 4.4.0)`, `Built: R 4.6.0; ; 2026-03-01 08:32:25 UTC; unix` (`evidence/r_status_after_install.txt`) |
| Pin check | Exits 0; its info output is identical to the pre-install output (`evidence/limma_pin_check_after.tsv`) |
| `git status` | Hash of the porcelain output unchanged (`245cdb8d…`); the library is git-ignored |

**Rollback:**
1. Remove `renv/library/macos/R-4.6/aarch64-apple-darwin23/BiocVersion`.
2. Copy back `reports/_pre_edit_copies/2026-10-18_D8_batch/biocversion_library/BiocVersion`.
3. Verify against `SHA256SUMS`, and check that `renv::status()` reports a consistent state.

Rollback is not needed.

**Interpretation.** The project library now equals what `renv::restore()` installs from `renv.lock` on this platform. The source-built copy described in `D8_R_LIMMA_INSTALLATION.md` §3a is superseded as the current state. That record was not edited, and remains accurate for 2026-10-12.

**What the checks show, and what they don't:**
- *Shown:* the same version, recorded commit and Bioconductor version-reporting behaviour, and the same results from the D8 pin check.
- *Not shown:* that the binary and the source-built copy are functionally identical in every respect. The observed facts are that neither copy contains R or compiled code, and that the checks above give identical results.
- *Build provenance:* the binary came from the official repository with its published MD5, and carries R-universe metadata, which is consistent with Bioconductor's documented use of R-universe for macOS binaries. Which machines built it is not established.

### D8-2: Python lock

**Created** in `reports/environment/python_lock/v2/`:

| File | SHA-256 |
|---|---|
| `requirements.hashes.macos-arm64-cp313.txt` | `a57412d37dc67120489bf1095f98ceebdeccf9448780535c9586c818538d131b` |
| `manifest.json` | See `SHA256SUMS` |
| `SHA256SUMS` | — |

**Checks:**
- The requirement lines (everything but comments) are **byte-identical** to the tested lock (`diff` printed nothing).
- 16/16 pins have the same version and SHA-256 as the PyPI-published values in `python_wheel_resolution.tsv`, all of status `sha256_match`.
- No version or hash was regenerated, and nothing was installed.

**Scope.** The header and manifest state:
- CPython 3.13.9 (Anaconda build `hc7d8306_100_cp313`) on macOS arm64 **only**;
- no coverage of other platforms or Python versions;
- index `https://pypi.org/simple`, marked *inferred*;
- `biomarker-project` and the base pip-only packages are excluded.

The manifest cites the hashes of the rebuild report, its `SHA256SUMS`, the wheel-resolution table, the install log, the rebuilt freeze, the installed-file comparison, the generator script, the review, and the source records.

**Preserved:** the tested lock and all rebuild-test evidence remain in place, unchanged (41/41 OK).

### D8-3: code identity (requirement recorded; not implemented)

**Requirement.** Applies to every output that will enter QC, sample sets, models, the annotation pin or the lock; the same scope as the D2 definition at v7:112. Each such output must carry a **source-tree identity record**:

1. `git rev-parse HEAD`.
2. `git status --porcelain=v1 --untracked-files=all`.
3. The SHA-256 of **every** file in the code set, whether tracked, modified or untracked:
   - `src/biomarker_project/**/*.py`, `scripts/**/*.py`, `R/**/*.R`, `tests/**/*.py`;
   - `config/**`;
   - `pyproject.toml`, `renv.lock`, `.Rprofile`, `renv/activate.R`, `renv/settings.json`;
   - excluding `__pycache__/` and `*.egg-info/`.
4. An aggregate digest: the SHA-256 of the sorted `path<TAB>sha256` list.
5. The SHA-256 of the D8 environment records in force: the conda explicit specification, `python_lock/v2`, `renv.lock`, and the R artifact evidence.

**A commit alone does not satisfy this requirement.** Today the working tree has 2 modified files and 50 untracked entries, including 12 untracked modules in `src/biomarker_project/`.

**Status:**
- Not implemented. The current `provenance.json` records only `package_version` plus output hashes (`synthetic_pipeline.py`).
- Implementing it is a source-code change and needs separate authorization.
- Placing the requirement in the SAP's lock section (v7:458–486) is a canonical edit outside this batch and needs separate authorization.
- No existing output is retrofitted.
- `biomarker-project` was not built or installed.

### D8-4: execution boundary (documented)

These are inspected facts:

| Component | Role and evidence |
|---|---|
| Conda layer of `/opt/anaconda3` | Provides the interpreter, standard library and native libraries. It is defined by `conda_explicit_base.txt` (545 packages); the 2026-10-17 rebuild matched all archive hashes. |
| `.venv` | `pyvenv.cfg`: `home = /opt/anaconda3/bin`, `include-system-site-packages = false`. `sys.path` is the base standard library plus `.venv/site-packages`, with **no** base `site-packages`. Its third-party layer is defined by `python_lock/v2`. |
| Project code | Runs from the source tree. All 12 of the 13 scripts in `scripts/` that import `biomarker_project` insert `ROOT/src` into `sys.path` (the 13th, `phase2b_population_tables.py`, doesn't import the package). pytest uses `pythonpath = ["src"]` (`pyproject.toml` line 25). **The `.venv` editable install is not functional:** the `.pth` carries the macOS `hidden` flag and Python 3.13.9 skips it, so `find_spec('biomarker_project')` returns `None`. |
| R framework | `/usr/local/bin/Rscript` points to `/Library/Frameworks/R.framework/Resources/bin/Rscript` (R 4.6.1). Invoked by `limma_backend.py` through `shutil.which("Rscript")`. |
| Project R library | `renv/library/macos/R-4.6/aarch64-apple-darwin23`, activated by `.Rprofile` when Rscript runs with the project root as working directory |

**Supported boundary:** project Python code runs only through `.venv/bin/python` (or `python` with `.venv` activated), from the project root. R runs through `/usr/local/bin/Rscript` with the project root as working directory.

**Out of scope:** the 77 pip-only base packages. They aren't on the `.venv` path, and none is a declared or transitive dependency.

**Caution:** a bare `python3` on `PATH` resolves to `/opt/anaconda3/bin/python3`, the base environment. Several python.org interpreters are also on `PATH` (3.14, 3.11, 3.12). Running project scripts with any of these is **outside the supported boundary**.

### D8-5: R interpreter evidence standard

**Adopted standard:** installer identity, the receipt, and an installed-file comparison against the receipt BOM.

**What it establishes:**
- The installer `R-4.6.1-arm64.pkg` (105,066,342 bytes): SHA-1 `fc9f4ada…` matches CRAN's published value; SHA-256 `67f6eea4…`; Developer ID signature, notarized, accepted by Gatekeeper. Verified 2026-10-12 and again 2026-10-17.
- The receipt `org.R-project.R.fw.pkg` is version 4.6.1.
- 3,412/3,412 installed regular files match the receipt BOM on size and CRC32. Evidence: `reports/environment/d8_closure_review/2026-10-17/evidence/r_framework_vs_receipt_bom.tsv`, plus the paths-not-in-receipt file (5 fontconfig cache files only).

**What it does not establish:**
- a fresh installation;
- a cryptographic (SHA-256) match of installed files, since CRC32 is not cryptographic;
- a signed link between the BOM and the installer (the BOM is written at installation);
- a check of symbolic links.

No download, reinstall or VM was used.

### D8-6: acceptance rubric

The review's §9 rubric was checked against the required distinctions. Two additions make them explicit:

| Required distinction | Where it sits in the rubric |
|---|---|
| Environment artifact integrity | L2 |
| Restoration and reconstruction | L3, plus installed-package verification L4 |
| **Code identity** | Not a D8 level. Added as a lock-gate requirement (D8-3); without it, an output cannot be tied to its source tree. |
| Analysis-specific reproducibility | L7, outside D8. Per analysis: provenance, determinism check and the SAP lock. |
| **Scientific validation** | Outside D8 and not addressed by any environment check. It belongs to the SAP's confirmatory and replication design. |

**No environment check implies that any analysis has been run, reproduced or validated.**

**Component status after this batch:**

| Component | Status |
|---|---|
| C1 conda layer | PASS |
| C2 R library | PASS. Artifact hashes are recorded in `d8_rebuild_test/2026-10-17/evidence/r_package_artifacts.tsv`, and the project library equals the reference restore by file comparison (BiocVersion: this batch; the other four packages: code files identical on 2026-10-17, apart from renv-added `DESCRIPTION` and `Meta/package.rds` fields). |
| C3 Python layer | PASS (`python_lock/v2`) |
| C4 `biomarker-project` | Out of D8 scope (D8-3) |
| C5 R interpreter | PASS under the D8-5 standard |
| C6 platform | PASS for macOS 26.6.2 arm64 on this machine only |
| C7 boundary | Documented (D8-4) |

These statuses are technical findings. **D8-8 (approval) is the PI's separate decision.**

### D8-7: canonical documentation edits

| File | Line | Change |
|---|---|---|
| SAP `reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md` | 611 (`\| D8 \|` row) | Replaced the sentence "A rebuild test … has not been performed." with DP1 from the review |
| Brief `reports/phase3b/v7/DECISIONS_REQUIRED_BEFORE_SAP_APPROVAL.md` | 155 (D8 PI question) | DP2 |
| Brief | 151 (D8 status) | DP3, applied for consistency: line 151 called `python_lock/v1` "not reviewed", which v2 has superseded |

**Factual adjustments to the review's draft text:**
- DP1 and DP2 now cite this execution report and state that D8-1 to D8-6 were taken and implemented 2026-10-18, with D8-8 pending. The draft cited the review's list of open items, which this batch resolves.
- DP1 adds that the project library's BiocVersion was replaced, and that `renv.lock` is unchanged.

**Checks:**
- **Diff against the pre-edit copies:** only `611c611` (SAP) and `151c151` and `155c155` (brief).
- **Line counts:** 661 and 309, both unchanged.
- **Pipe counts:** 6, 3 and 3, unchanged.
- **Status line:** SAP line 3 still reads "**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen.**"
- **Outdated text:** "has not been performed" no longer appears in the SAP.
- **Citations:** every `reports/…` path cited on the three edited lines exists, including this report once written; checked after writing.
- The `f19cc744…` and `52e2e785…` hashes cited in DP1 match their files.

**Hashes after editing:**

| File | SHA-256 |
|---|---|
| SAP | `161cf12d26a6e15e5ba27365cc06827ec83219144e1ae1ebb7fd5e765896bbbb` |
| Brief | `2cfcd4afe86539162dd1cc8d850f6e566a3c80bf53c7b2817af765e3016334ca` |

E1–E8 text was not touched.

## 3. Created and changed artifacts

| Path | Action |
|---|---|
| `renv/library/macos/R-4.6/aarch64-apple-darwin23/BiocVersion/` (16 files; git-ignored) | Replaced with the verified official binary. Member hashes are in `evidence/biocversion_binary_archive_members_sha256.txt`. |
| `reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md` | Line 611 edited: `a5143799…` → `161cf12d…` |
| `reports/phase3b/v7/DECISIONS_REQUIRED_BEFORE_SAP_APPROVAL.md` | Lines 151 and 155 edited: `a5870e88…` → `2cfcd4af…` |
| `reports/environment/python_lock/v2/` | Created (3 files) |
| `reports/_pre_edit_copies/2026-10-18_D8_batch/` | Created (18 copied files, plus `SHA256SUMS` and `PROVENANCE.txt`) |
| `reports/environment/d8_closure_review/2026-10-18/` | Created: this report, `evidence/` and `SHA256SUMS` |

**Not changed:**
- `renv.lock`, `pyproject.toml`, `.venv` and the Anaconda base;
- the R framework;
- any source file;
- `README.md` and `__init__.py`;
- any prior evidence, including the 2026-10-17 review and the rebuild test;
- `reports/environment/D8_R_LIMMA_INSTALLATION.md`.

**Downloaded:** only `BiocVersion_3.23.1.tgz` and its `PACKAGES` index, into a scratch directory outside the project that was removed after evidence collection.

## 4. Skipped or partial steps

- **D8-3 implementation** (writing source-tree identity records) was not performed; it is a source change and needs authorization.
- **Inserting the code-identity requirement into the SAP's lock section** needs a separate canonical edit.
- **Optional:** wording in `src/biomarker_project/limma_backend.py` ("D8-approved", `APPROVED_PINS`) and the README editable-install instructions remain as they are. They are not canonical files, and the batch doesn't authorize changing them.

## 5. Final state

Recorded in the final check below and in `SHA256SUMS`:
- 0 staged files;
- HEAD `f4d7810`;
- 52 status entries: the two pre-existing user modifications plus untracked entries. The new files sit under already-untracked `reports/` directories.

## 6. Remaining blockers

| Target | Blocked on |
|---|---|
| **D8-8** | Explicit PI approval. All technical components are PASS or documented as out of scope (§2, D8-6). The code-identity requirement is recorded but not implemented; it is a lock-gate item, not a D8 environment item. |
| **Tier B** | D8-8; then step 2 (creating the annotation pin record) needs its own separate authorization, followed by steps 3–5 |
| **Annotation pin** | D8-8, then separate authorization |
| **Downstream analyses** | All the above, plus the outstanding SAP decisions (D7, D9–D16, D18-1, D18-2, D19, D20, D21, H1 details) and SAP approval |
