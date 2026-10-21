# BIO-MB-001: D8 closure review (2026-10-17)

**Status:** review only. This report approves nothing:
- D8, the SAP and the annotation pin are **not approved**.
- No canonical file was edited.
- Nothing was installed, built or downloaded.
- No environment was modified.
- No biomedical analysis was run.
- Nothing was staged, committed or pushed.

Every proposal below is labelled **PROPOSED FOR PI REVIEW**.

**What this review did:**
- Read-only file inspection.
- Read-only checks: hashing; `lsbom`/`cksum` against the R installer receipt; printing renv 1.3.1 function bodies; Python `sys.path` and `importlib` lookups.
- Public web pages read for provenance (cited in §4.6). No package or archive was downloaded.

## 1. Executive conclusion

The 2026-10-17 rebuild test plus this review leave **no unresolved factual question** blocking D8. What remains are PI decisions on scope and claim strength, followed by small, separately authorized implementation steps.

**Key new findings:**

1. **BiocVersion's r-universe metadata is consistent with Bioconductor's official binary pipeline.**
   - Bioconductor states that it "now uses R-universe to build the Windows and macOS binaries" (§4.6).
   - The limma binary the project has used since 2026-10-12 carries the same pipeline fields (`RemoteUrl` on GitHub, `RemoteSha`, `Packaged … root`).
   - BiocVersion contains no R code and no compiled code. Its only functional content is its version number, which yields Bioconductor 3.23 in both copies.
   - Recommendation: accept the official binary as the D8 reference artifact.
2. **The project package's editable install in `.venv` is inert.**
   - Python 3.13.9 reports "Skipping hidden .pth file" for `__editable__.biomarker_project-0.1.0.pth`, which carries the macOS `hidden` flag.
   - `importlib.util.find_spec('biomarker_project')` returns `None` in `.venv`.
   - Every script inserts `src/` into `sys.path` itself, and pytest uses `pythonpath = ["src"]`.
   - Project code therefore runs from the source tree, and its identity is a code-provenance question, not an environment-build question.
3. **The installed R 4.6.1 framework matches its installer receipt.**
   - 3,412 of 3,412 regular files match the receipt BOM on size and CRC32 (read-only check).
   - The only extra paths are 5 fontconfig cache files.
   - A full reinstall is not needed for an identity-scoped D8 claim.
4. **The 77 pip-only Anaconda base packages are not on the project's import path.** The `.venv` `sys.path` contains only the base standard library and `.venv/site-packages`.
5. **The 16-package Python lock is dependency-complete for CPython 3.13.9 on macOS arm64**, with exactly one hash-pinned artifact per package.

**Proposed D8 outcome:** D8 can move to an approval decision after the eight register decisions in §11. Only one of them, the R library alignment in §4.5 (recommended, optional), would need a new installation; it is a single 6 KB package.

## 2. Preflight (2026-10-17T19:54:39Z)

| Check | Result |
|---|---|
| Repository root / branch / HEAD | `/Users/sadgasalim/Documents/BIO-MB-001` / `main` / `f4d781001a91eb6c571dcb19364f4b4437c59a0d` |
| Working tree | 52 status entries: 2 modified (`README.md`, `src/biomarker_project/__init__.py`), 50 untracked, the same set as at session start; 0 staged |
| Changes since the last report | No project file outside `.venv`, `.git` and `renv/library` is newer than the rebuild test's `SHA256SUMS` (checked before this review wrote anything) |
| SAP v7 | `a51437993c89485c674f9c011b09f3776b6b095a0106213ec51c99433cbb3b60`, the post-E8 value |
| Brief | `a5870e8884a0dd887ae44a6a9dbc56775399a5db17a1e560c904d781cb09c6ac`, the post-E8 value |
| User changes | `README.md` `8e52c51b62a48478f4cbd2d0ebf34ac5c46527bb410f7b8b8d18d64df69b3c57`; `__init__.py` `5b6fc851ef3db59d53b5a9a138df893d295277798be21d88ca61030e6917adc1`; both intact |
| D8 capture | `conda_explicit_base.txt` `52e2e785…cb731` and `manifest.json` `31e1b9fb…3be` match their recorded values |
| Rebuild test | `SHA256SUMS` `49b4744c53c7bec30ea9e29d0680f9245f8d5caf656721f1065ef0b365ac9025`; 41/41 entries OK, including the report (`f19cc744…`) and the 4 test scripts |
| Generated Python lock | Test artifact only. No file outside `reports/environment/d8_rebuild_test/` references `requirements.hashes`. `pyproject.toml` (`ca8c8bae…`) and `renv.lock` (`fa51c7b9…`) are unchanged. |
| Annotation pin | `reports/annotation_audit/annotation_pin/` does not exist |

**Prior-report claims re-checked in this review:**
- 41/41 checksums;
- the 3,567-file total and 16/16 identical packages (recomputed from `venv_installed_file_comparison.json`);
- 16 locked packages with 16 hashes;
- all R artifact SHA-256 values against the 2026-10-12 record;
- BiocVersion field differences (from retained `biocversion_description_comparison.txt`).

**One claim with no retained evidence:** the transcript printed `pip check`'s "No broken requirements found" but did not save it. The same property is re-established independently in §5, item 2.

## 3. Verified findings, each tied to its evidence

| # | Finding | Evidence |
|---|---|---|
| F1 | Conda layer: 545/545 archives SHA-256-identical to the base `conda-meta` records; rebuilt explicit list identical | `d8_rebuild_test/…/evidence/conda_archive_sha256_vs_base_records.tsv`, `conda_rebuilt_explicit.txt` |
| F2 | 16 third-party wheels match the PyPI-published SHA-256 values; the installed files of all 16 packages match `.venv` (3,567 hashed files) | `python_wheel_resolution.tsv`, `venv_installed_file_comparison.json` |
| F3 | R package binaries restored by renv equal the 2026-10-12 recorded SHA-256 values | `renv_downloaded_binaries_sha256.txt`, `r_package_artifacts.tsv`, `D8_R_LIMMA_INSTALLATION.md` §3 |
| F4 | renv is identical in all 77 files. BiocManager, statmod and limma are identical except `DESCRIPTION` and `Meta/package.rds`. BiocVersion differs in metadata and help files only. | `r_library_file_comparison.txt`, `r_description_field_diff.txt` |
| F5 | BiocVersion has no `R/` directory and no `libs/` in either copy; its `NAMESPACE` is the default `exportPattern("^[^.]")` | Directory listing of the project library; `biocversion_description_comparison.txt` (tar listings) |
| F6 | The project limma binary carries `RemoteUrl: https://github.com/bioc/limma`, `RemoteRef: RELEASE_3_23`, `RemoteSha: 825d1c83…`, `Packaged: 2026-08-10 … root`, `Repository: Bioconductor 3.23` | `renv/library/…/limma/DESCRIPTION` (read 2026-10-17) |
| F7 | The `.venv` editable `.pth` is skipped as hidden; `biomarker_project` cannot be imported from `.venv` without the `src` path | `ls -lO` shows `hidden`; `python -I -v` prints "Skipping hidden .pth file"; `find_spec` returns `None` |
| F8 | The editable install was generated by `setuptools (84.0.0)`. The conda layer ships setuptools 80.9.0 and wheel 0.45.1. | `.venv/…/biomarker_project-0.1.0.dist-info/WHEEL`; `conda_explicit_base.txt` |
| F9 | R framework: 3,412/3,412 regular files match the receipt BOM on CRC32 and size. 7 BOM entries are zero-byte `._` AppleDouble files not present as files. 5 extra paths, all under `fontconfig/cache/`. | `evidence/r_framework_vs_receipt_bom.tsv`, `evidence/r_framework_paths_not_in_receipt.txt`, `evidence/r_receipt_sha256.txt` |
| F10 | The R framework is not relocatable: `libR.dylib` install names and `R_HOME_DIR` are absolute paths under `/Library/Frameworks/R.framework` | `otool -L`; `bin/R` line 4 |
| F11 | The system R library holds only base and recommended packages (29 plus `translations`) | Directory listing |
| F12 | `.venv` `sys.path` contains no Anaconda `site-packages`; `pyvenv.cfg` has `include-system-site-packages = false` | `.venv/bin/python -I` `sys.path`; `d8_readonly_checks.json` |
| F13 | Of the 77 base pip-only distributions, only `packaging` and `pip` share a name with `.venv` packages, and `.venv` has its own copies (26.3 and 26.2.1) | Name comparison of `base_pypi_packages_not_in_explicit_spec.txt` against `requirements.snapshot.txt` |

## 4. BiocVersion

### 4.1 Verifiable facts

| Property | Status |
|---|---|
| Version | Both copies are **3.23.1** (verified) |
| Commit | Source copy records `git_last_commit: 252d7c8`; binary records `RemoteSha: 252d7c8f03a39a9b83f6de7e9dbf9a5ee6584365`. The prefixes agree. This is recorded metadata; the commit was **not** checked against git.bioconductor.org. |
| Repository metadata | Source: `Bioconductor 3.23`, packaged by `biocbuild` 2025-10-30. Binary: `https://bioc.r-universe.dev`, packaged by `root` 2026-03-01, archive owner `runner`, built under R 4.6.0. |
| R requirement | Source: `R (>= 4.6.0)`; binary: `R (>= 4.4.0)`. This is an install-time check only; R 4.6.1 satisfies both. |
| Source vs binary identity | Not byte-identical. The binary is `cea69c8e…`, 6,054 B; the source is `7a9fdd2f…`, 990 B. Different artifact types. |
| Executable content | **None in either copy:** no `R/`, no `libs/`, default NAMESPACE (F5). The differences are confined to `DESCRIPTION`, `Meta/*.rds` and help/index files, which are generated metadata. |
| Functional consequence | **None demonstrated.** The package's runtime role is to report its version. `BiocManager::version()` returned `3.23` with the restored binary (`r_throwaway_status_sessioninfo.txt`) and with the source-built copy (D8 record §3a). `R/limma_de.R` derives `bioc` from limma's `DESCRIPTION` `Repository` field and the renv setting (`renv/settings.json`, lines 34–40), not from BiocVersion. |
| renv consistency | In the throwaway restore, `renv::status()` did not flag BiocVersion; only limma showed "[3.68.5: unchanged]" (`r_throwaway_status_sessioninfo.txt`) |

### 4.2 What the evidence does and doesn't establish

- **Established:** Bioconductor states it uses R-universe to build its macOS binaries (§4.6), and the binary was served from the official Bioconductor 3.23 repository with its published MD5. The r-universe metadata is therefore what an official Bioconductor 3.23 macOS binary is expected to carry.
- **Not established:** that this particular file was produced by any specific organization's build machines. Nothing indicates the binary was built outside Bioconductor's chosen build system, and this report makes no such claim.
- **Two separate questions:**
  - *Build provenance:* the source tarball has higher provenance certainty, because it was packaged by `biocbuild`.
  - *Functional equivalence:* the two copies have no functional difference for a package with no code.

### 4.3 The 2026-10-12 source-build procedure

`D8_R_LIMMA_INSTALLATION.md` §3a records:
- the URL, the 990-byte size, the MD5 from `PACKAGES`, and the SHA-256;
- the command `install.packages("BiocVersion_3.23.1.tar.gz", repos = NULL, type = "source", lib = <project renv library>)`;
- the follow-up `renv::snapshot(...)`.

This is enough to repeat the step, with these gaps:
1. It isn't part of `renv::restore()`, so any restore needs a manual extra step.
2. Environment variables are not recorded (only that `RENV_PATHS_ROOT` was temporary during installation).
3. The `Built:` stamp of a rebuild will necessarily differ, so a repeat can't be byte-identical to the project copy. Whether `Meta/*.rds` and help files are reproducible byte-for-byte across source installs is untested.

The procedure is technically sound; installing a source package with no compilation needs only base R.

### 4.4 Options compared

| Option | Build-provenance certainty | Functional equivalence | Restore path | Cost and risk |
|---|---|---|---|---|
| **1. Accept the official binary** as the D8 reference artifact (SHA-256 `cea69c8e…`) | Official repository and published MD5; r-universe pipeline consistent with Bioconductor's statement | Equivalent (no code) | Plain `renv::restore()`, already tested and passed | Lowest. Matches how limma is already accepted (F6). |
| 2. Restore BiocVersion from the verified source tarball in a disposable environment | Highest (packaged by `biocbuild`) | Equivalent | `renv::restore(exclude = "BiocVersion")` followed by a manual source install | Adds a nonstandard step for every future rebuild. The `Built` stamp means byte identity with the project copy is unattainable anyway. |
| 3. Pin the source archive in the specification, e.g. through renv's cellar | As option 2 | Equivalent | renv 1.3.1 has cellar roots (`renv/cellar`, `renv/local`, `RENV_PATHS_CELLAR`, `RENV_PATHS_LOCAL`; verified in `renv_cellar_roots`). `renv_retrieve_cellar_find` tries **binary before source**. Whether `restore()` would pick a cellar source over the repository binary for a `Source: Bioconductor` record is **not established** by reading the code. | Untested mechanism. It adds a project file, a 990-byte tarball in a git-ignored folder, which then needs its own provenance record. |
| 4. Other | — | — | No further option is supported by the evidence | — |

### 4.5 Recommendation (PROPOSED FOR PI REVIEW)

**Option 1.** Accept the official Bioconductor 3.23 sonoma-arm64 binary `BiocVersion_3.23.1.tgz` (SHA-256 `cea69c8e00240f6f6c0aeb8f7123c39f21132df8487d96d98018b6e0ef5f9805`) as the D8 reference artifact. Record it in an R artifact manifest; see §9, criterion C2.

Choose one of two sub-options:
- **1a (recommended):** replace the project library's source-built BiocVersion with this verified binary, so the project library equals what `renv.lock` restores. This modifies the project environment by one metadata-only package and **needs authorization**. `renv.lock` stays unchanged.
- **1b:** keep the source-built copy and document a metadata-only difference between the project library and the reference restore.

**Test plan for 1a** (not executed; needs authorization):
- **Inputs:**
  - the binary URL `https://bioconductor.org/packages/3.23/bioc/bin/macosx/sonoma-arm64/contrib/4.6/BiocVersion_3.23.1.tgz`, expected 6,054 B, MD5 `dab387f575308ddd75ffaba682bd35fd`, SHA-256 `cea69c8e…5f9805`;
  - the `PACKAGES` index from the same directory, for the MD5.
- **Dependencies:** none; no compilation.
- **Preservation:**
  - copy `renv/library/macos/R-4.6/aarch64-apple-darwin23/BiocVersion/` (16 files) to `reports/_pre_edit_copies/<date>_biocversion_library/` with `SHA256SUMS` and `PROVENANCE.txt`;
  - record the `renv.lock` SHA-256 (`fa51c7b9…`).
- **Commands** (download to a new empty scratch directory):

  ```
  curl -o <SCR>/BiocVersion_3.23.1.tgz <URL>; curl -o <SCR>/PACKAGES <dir>/PACKAGES
  md5 -q / shasum -a 256 → must equal the values above
  cd /private/tmp && Rscript --vanilla -e 'install.packages("<SCR>/BiocVersion_3.23.1.tgz", repos = NULL, type = "binary", lib = "<project renv library>")'
  cd <project> && Rscript -e 'renv::status(); BiocManager::version()'
  Rscript R/limma_de.R --check <pins>
  ```

  The last command is the existing environment pin check. It reads no data and fits nothing.
- **Success criteria:**
  - Every installed file except `DESCRIPTION` matches the tarball member byte for byte.
  - `DESCRIPTION` matches the tarball's apart from any fields R adds on installation, each listed.
  - `renv.lock` SHA-256 is unchanged.
  - `renv::status()` raises no BiocVersion issue.
  - `BiocManager::version()` returns 3.23.
  - The pin check exits with status 0.
  - The other four packages' file hashes are unchanged.
- **Failure criteria:** any hash mismatch, a change to `renv.lock`, a new `renv::status()` issue, or a non-zero pin check. On failure, restore the pre-edit copy and verify it against `SHA256SUMS`.
- **Cleanup:** remove the scratch download; keep the evidence file.
- **Evidence D8 needs:** the hashes before and after, the status output and the pin-check output.

### 4.6 Sources (accessed 2026-10-17)

- **Bioconductor 3.23 release announcement**, https://www.bioconductor.org/news/bioc_3_23_release/: release date April 29, 2026. It says Bioconductor "does not have active daily windows builders" and will be "testing the windows and mac binaries generated through the r-universe system".
- **Bioconductor and rOpenSci blog post** (2026-04-08), https://blog.bioconductor.org/posts/2026-04-08-r-universe-collaboration/: "Bioconductor now uses R-universe to build the Windows and macOS binaries". The post doesn't describe `DESCRIPTION` metadata, and mentions mirroring to bioconductor.org only as planned.
- **BiocVersion release page**, https://bioconductor.org/packages/release/bioc/html/BiocVersion.html: version 3.23.1, with sonoma-arm64 and big-sur-x86_64 binaries. It links an r-universe page next to the build report but makes no statement about who builds the binaries.
- **rOpenSci** (2024-01-14), https://ropensci.org/blog/2024/01/14/runiverse-arm64/: R-universe's general arm64 approach. Background only.

## 5. Python lock audit (`evidence/requirements.hashes.TEST.txt`, `cf. SHA256SUMS`)

| # | Question | Finding |
|---|---|---|
| 1 | All 16 third-party packages present? | Yes: 16 requirement lines, 16 `--hash` lines |
| 2 | Transitive dependencies included? | Yes for the target platform. Evaluating every `Requires-Dist` from `pip_inspect.json` under the recorded environment (CPython 3.13.9, darwin, arm64) gives all active requirements satisfied inside the set. The inactive markers are `colorama` (win32), `exceptiongroup` and `tomli` (<3.11), `tzdata` (win32 or emscripten), and `numpy>=2.3.3` (Python ≥3.14). |
| 3 | Exact versions and sources explicit? | Versions are `==`. The lock omits the index URL, but each artifact's URL (`files.pythonhosted.org`) is recorded in `python_wheel_resolution.tsv`. No pip configuration exists, so PyPI as the original index is **inferred** from that absence, not recorded. |
| 4 | Hashes of distribution files? | Yes: PyPI-published SHA-256 of the wheel files, re-verified on download. These are not installed-file hashes. |
| 5 | Hash coverage | Exactly one artifact per package, the wheel matching the recorded installed tag: `cp313` macOS arm64 or universal2, or `py3-none-any`. That is deliberate platform scoping; the lock will not install on other platforms or Python versions. |
| 6 | Compatible with Python 3.13.9 on macOS arm64? | Yes; installed and verified in the rebuild test |
| 7 | Gaps: markers, extras, direct URLs, editable or local packages | The dev extra (pytest and its dependencies) is included. No direct-URL dependencies. The only local or editable package, `biomarker-project`, is excluded (§6). `pip` 26.2.1 is pinned. The bootstrap pip 25.2 comes from the conda Python archive, which is hash-verified (F1). |
| 8 | Is "3,567 file-for-file" supported, and with what scope? | Supported: the per-package values in `venv_installed_file_comparison.json` sum to 3,567, and 16/16 packages are identical. Scope: every `RECORD` row with a hash, excluding `.pyc`, `INSTALLER`, `REQUESTED`, `direct_url.json`, `RECORD` itself and `../../../bin/` console scripts. The rebuilt files were also re-hashed against their own `RECORD`. |
| 9 | Could a package resolve to a different artifact? | Not under `--require-hashes`, since each package has one hash. Without hash checking, pip could choose a different wheel or an sdist. |
| 10 | Layer captured | Only the project dependency layer. The base is covered by the conda explicit specification. |

**Distinctions:**
- *Artifact identity* and *installed-file identity:* demonstrated.
- *Specification completeness:* complete for the scoped platform, except that the index URL is inferred.
- *Full environment reconstruction:* demonstrated when the conda layer is combined with this lock.
- *Numerical reproducibility of analyses:* **not** demonstrated or addressed.

**Recommendation (PROPOSED FOR PI REVIEW):** add a reviewed, platform-scoped lock in a later authorized edit. No new download is needed, provided the requirement lines are copied byte for byte from the tested file.
- **Proposed destination:** `reports/environment/python_lock/v2/` with these files:
  - `requirements.hashes.macos-arm64-cp313.txt`;
  - `manifest.json`;
  - `SHA256SUMS`.

  This follows the project's versioned-record convention, and `pyproject.toml` stays unchanged.
- **Header and manifest fields:**
  - status (D8 record, PI-approved on <date>);
  - platform scope (macOS arm64, CPython 3.13.9 from conda build `hc7d8306_100_cp313`);
  - index `https://pypi.org/simple` (inferred, with the reason);
  - the source records' SHA-256 (`requirements.snapshot.txt`, `d8_readonly_checks.json`);
  - the generator script `wheel_lock.py` and its SHA-256;
  - the tested-lock SHA-256;
  - the install command;
  - the exclusion of `biomarker-project`.
- **Acceptance criteria:**
  - the requirement lines are byte-identical to the tested lock;
  - each hash equals the `pypi_published_sha256` in `python_wheel_resolution.tsv`;
  - the manifest's hashes verify.

  No re-installation test is required, because the tested lines are unchanged.

## 6. The `biomarker-project` build

**Inspected:**
- `pyproject.toml`: backend `setuptools.build_meta`, requires `setuptools>=64`, `src/` layout, no entry points, no `readme`, no package data. There is no `setup.py`, `setup.cfg` or `MANIFEST.in`.
- The existing `src/biomarker_project.egg-info/`: git-ignored (`.gitignore:4`) and dated 2026-10-09. Its `SOURCES.txt` lists only the 10 committed modules, so it is stale.
- The `.venv` editable install (F7, F8).
- Import behaviour: every script inserts `ROOT/src` into `sys.path` before importing; `pyproject` sets pytest `pythonpath = ["src"]`; nothing uses `importlib.metadata` or `pkg_resources`.

**What a build reads and writes.** The facts are verified; the expected behaviour comes from setuptools documentation and is to be confirmed by the test.
- *Reads:* `pyproject.toml` and `src/**`.
- *Writes in the directory being built:* a `build/` directory and `src/biomarker_project.egg-info/`. pip ≥21.3 builds in place, so building directly from the project would rewrite the git-ignored, stale `egg-info`. That is why a copy is required.

**Options compared:**

| Option | Assessment |
|---|---|
| 1. Wheel from a clean temporary copy of the **working tree** | Tests that the current code builds. It does not change runtime evidence, because runtime never uses an installed artifact (F7). |
| 2. Exported source archive (`git archive HEAD`) | **Unsuitable**: HEAD lacks the 12 untracked modules now in `src/biomarker_project/` and the user's uncommitted `__init__.py` change, so it would test a different code state |
| **3. Declare the project-package build out of D8 scope** | Supported by evidence. The installed artifact is inert (F7); project code identity is the set of source-file hashes. **Gap:** `provenance.json` currently records only `package_version` ("0.1.0") and output hashes, **not** source-file hashes or a commit (`synthetic_pipeline.py`, provenance block). Option 3 therefore needs code identity to be recorded at the lock gate. |

**Recommendation (PROPOSED FOR PI REVIEW): option 3**, with these conditions:
- D8 covers third-party software only.
- Project code is identified by a commit or by source-file SHA-256 values recorded with every analysis output. This is **not implemented yet**: `provenance.json` holds only `package_version`. It belongs to the code-freeze and lock gate (the SAP's lock section), not to D8, and the PI should treat it as a required lock-gate item.
- The hidden `.pth` defect is documented: README line 65's editable install doesn't currently make the package importable, and README line 71's check would fail. README is a user-modified file and is not edited here.

**Option 1 test plan, if the PI prefers it** (needs authorization):
1. `rsync -a --exclude '*.egg-info' --exclude '__pycache__' pyproject.toml src <SCR>/proj/`.
2. Record the SHA-256 of every source-tree file before and after.
3. Choose a backend:
   - **(a)** the conda layer's setuptools 80.9.0, already hash-verified (F1, F8); no download needed; or
   - **(b)** setuptools 84.0.0, the version used originally. Its wheel and PyPI hash have **not** been obtained; downloading them is identified but not done.
4. `<conda-python> -I -m pip wheel --no-deps --no-build-isolation --no-index -w <SCR>/out <SCR>/proj`.
5. **Pass criteria:**
   - exactly one `biomarker_project-0.1.0-py3-none-any.whl` is produced;
   - each module in the wheel is byte-identical to its `src/` file;
   - the metadata lists the 4 runtime dependencies and the `dev` extra;
   - the source tree's hashes are unchanged.
6. Delete `<SCR>`.

**Authorization needed:** a scratch-only build, plus a download only for (b).

## 7. Base-environment scope (the 77 pip-only packages)

- **What D8 must guarantee:** the software that executes project computations. That is:
  - the Python interpreter and standard library;
  - the third-party Python packages imported by `src/` and `scripts/`;
  - R 4.6.1 and the renv library, invoked by `limma_backend.py` through `Rscript` on `PATH`.
- **How the interpreter is selected:** `.venv/bin/python` resolves to `/opt/anaconda3/bin/python3.13` (`pyvenv.cfg`), with `include-system-site-packages = false`.
- **Relevance of the 77 packages:** they live in the base `site-packages`, which is not on `.venv` `sys.path` (F12). None is a declared or transitive project dependency (§5, item 2). The two name overlaps (`packaging`, `pip`) resolve to `.venv`'s own copies (F13). They do not affect project runtime **when the project runs through `.venv`**.

**Options:**

| Option | Assessment |
|---|---|
| A. Full base, conda plus pip packages | Over-scoped. It pins 77 unrelated packages (FastAPI, Firebase, Google and similar) and needs further pip hashes. |
| B. A dedicated minimal environment | The cleanest long-term boundary, but it needs a new environment and a new test, and the conda layer (545 packages) would change. |
| **C. Scoped exclusion** | Smallest defensible scope, justified by F12, F13 and §5, item 2 |

**Recommendation (PROPOSED FOR PI REVIEW): option C.**
- **In scope:** the conda layer of `/opt/anaconda3` exactly as specified by `conda_explicit_base.txt`, which provides the interpreter, standard library and native libraries; plus the `.venv` third-party layer.
- **Out of scope:** pip-only packages in the base.
- **Supported execution boundary:** project code runs only through `.venv/bin/python`.

Option B stays available as a future improvement, for example before publication.

## 8. R interpreter

- **Established:**
  - The installer's identity and provenance: SHA-1 matches the CRAN-published value; SHA-256 matches the record; Developer ID signature, notarized, accepted by Gatekeeper (`d8_rebuild_test/…/r_installer_verification.txt`).
  - The installed receipt is `org.R-project.R.fw.pkg` 4.6.1.
  - **New:** the installed framework matches that receipt's BOM: 3,412/3,412 regular files by CRC32 and size (F9).
- **Not established:**
  - A fresh installation was not tested.
  - CRC32 is not a cryptographic hash.
  - The BOM was written at installation and is not signed afterwards. Its link to the verified installer is the receipt's package-id, version and install time, together with the identical installer hash recorded on 2026-10-12 and again on 2026-10-17.
  - Symbolic links were not checked against the BOM.
- **Feasibility of an isolated reinstall:** not feasible without administrator rights or a virtual machine, because the framework is not relocatable (F10). A VM install would show only that the installer works on a fresh system, which the signature and hash already establish for the artifact.

**Recommendation (PROPOSED FOR PI REVIEW):** D8 should use an identity-scoped standard for the R interpreter, with no reinstall:

> installer hash, signature and notarization verified; installed receipt matches; installed files match the receipt BOM.

All of this evidence exists now.

**Optional strengthening** (needs authorization for a download of about 105 MB, no installation): expand the verified `.pkg` (`pkgutil --expand-full`) and compare the installed files with the payload by SHA-256. That would replace CRC32 with a cryptographic comparison and tie the BOM to the signed installer.

## 9. Proposed D8 acceptance criteria (PROPOSED FOR PI REVIEW)

**Levels:**

| Level | Meaning |
|---|---|
| L1 | Pinned specification in a project record |
| L2 | Artifacts available, with hash-verified integrity |
| L3 | Environment reconstructed from L1 in isolation |
| L4 | Installed-package verification against the reference |
| L5 | Build provenance documented |
| L6 | Platform limits stated |
| L7 | Analysis reproducibility — **not a D8 criterion.** It is handled per analysis: the provenance record, the `--verify-determinism` check and the SAP lock. |

**Rubric.** PASS means the level is met. PARTIAL means it is met with a documented gap. FAIL means an artifact is unavailable or a hash mismatches.

| Component | Required | Status now | What turns PARTIAL into PASS |
|---|---|---|---|
| C1. Conda layer | L1–L4, L6 | **PASS**. Installed binary hashes depend on the install prefix, so L4 is assessed through archive hashes and conda metadata. | — |
| C2. R package library | L1–L5 | **PARTIAL.** `renv.lock` holds no hashes, and the project library's BiocVersion differs from the reference. | (i) Record an R artifact manifest: the 5 binary SHA-256 values from `r_package_artifacts.tsv`, plus the BiocVersion decision. (ii) Apply option 1a and verify it, or record 1b as a documented metadata-only difference. |
| C3. Python third-party layer | L1–L4, L6 | **PARTIAL.** L2–L4 pass; L1 is only a test artifact. | Promote the lock byte-identically (§5) |
| C4. `biomarker-project` | Out of D8 scope if §6 option 3 is adopted | **NOT TESTED** | Adopt option 3 (scoped out, with code identity at the lock gate), or pass the option 1 test |
| C5. R interpreter | L2, L4, L5, L6 under the identity-scoped standard (§8) | **PARTIAL** until the standard is adopted; the evidence is complete | Adopt the §8 standard |
| C6. Platform | L6 | **PASS** for this machine: macOS 26.6.2 (25G83) arm64, no cross-platform claim | — |
| C7. Base boundary | Documented | **PARTIAL** until §7 option C is adopted | Adopt option C |
| **Overall D8** | Every component PASS or documented as out of scope; then the PI's approval decision | **PARTIAL** | The items above, then the D8 approval (register item D8-8) |

## 10. Minimal documentation plan (no edits made; each needs separate authorization)

E1–E8 were re-verified as present in the hashes above. No independently verified error requires a correction. The plan uses the existing D8 row and the brief's D8 section, with no new canonical sections.

**DP1 (required before the D8 review).** File: `reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md`, line 611 (the `| D8 |` row of the decision register).

Current sentence:

> A rebuild test in a throwaway environment is required before reproducibility is described as demonstrated; it requires separate authorization for any download or installation and has not been performed.

Proposed replacement (no pipe characters):

> A throwaway rebuild test was performed 2026-10-17 under explicit PI authorization (reports/environment/d8_rebuild_test/2026-10-17/D8_REBUILD_TEST_REPORT.md, SHA-256 f19cc744b3968f44134af61d25d06ab3d22096e79101eea276d0028e2d9b2de7): the conda layer (conda explicit specification reports/environment/d8_environment_capture/v1/conda_explicit_base.txt, SHA-256 52e2e785b7e7c92a0435beab3476fbb7966047ea920ad9bfcd15a1cd5b3eb731) and the 16 third-party Python packages were reconstructed and verified, and the R packages restored at their locked versions with BiocVersion restored as the official Bioconductor 3.23 binary; R 4.6.1 was verified at installer and installed-file level, not reinstalled; the local project package was not built. Open D8 items are listed in reports/environment/d8_closure_review/2026-10-17/D8_CLOSURE_REVIEW.md. Reconstruction on this machine does not demonstrate reproducibility of analyses.

Reason: the current sentence is now factually outdated. Evidence: §2 hashes. Checks after the edit: line count unchanged, pipe count unchanged.

**DP2 (required).** File: `reports/phase3b/v7/DECISIONS_REQUIRED_BEFORE_SAP_APPROVAL.md`, line 155 (`### D8`, the **PI question** row).

Current sentence:

> Open: D8 approval, once the D8 record holds the conda explicit specification of the base environment and the required throwaway rebuild test has been authorized and passed; reproducibility is not yet demonstrated.

Proposed replacement:

> The conda explicit specification is recorded and the throwaway rebuild test was performed 2026-10-17 (results partial; reports/environment/d8_rebuild_test/2026-10-17). Open: the D8 decisions listed in reports/environment/d8_closure_review/2026-10-17/D8_CLOSURE_REVIEW.md §11, then D8 approval; reproducibility of analyses is not demonstrated.

Reason: the current wording makes approval conditional on a test that has now been performed.

**DP3 (useful).** Same file, line 151 (the `### D8` **Status** row).

Current text:

> Python environment snapshot: reports/environment/python_lock/v1 (not reviewed).

Proposed replacement:

> Python environment snapshot: reports/environment/python_lock/v1 (reviewed 2026-10-17 in reports/environment/d8_closure_review/2026-10-17; a hash-pinned test lock exists in reports/environment/d8_rebuild_test/2026-10-17 and is not a project record).

**DP4 (at D8 approval; template only).** SAP line 611, after "Defining this scope does not approve D8", add the PI's decisions D8-1 to D8-7, with dates, and the record paths and hashes created by the approved implementation steps. This is drafted only after those decisions.

**Non-canonical observation (useful, not blocking).** `src/biomarker_project/limma_backend.py` line 1 says "D8-approved limma runner", and line 32 names a constant `APPROVED_PINS`. Both predate the 2026-10-15 deferral, and the brief already explains the similar wording in the installation record (brief line 151). Rewording them is optional and needs authorization, because it is a code edit.

## 11. Consolidated decision register

The type column marks scientific or governance decisions (**G**) and technical implementation steps (**T**).

| ID | Type | Decision | Evidence already available | Recommended option | Alternatives | Consequences of each option | Additional test needed | Authorization needed | Blocking status |
|---|---|---|---|---|---|---|---|---|---|
| D8-1 | G | BiocVersion reference artifact | F4–F6, §4.1–4.6 | **Option 1:** official binary `cea69c8e…` | 2: source rebuild step; 3: cellar-pinned source | 1: standard restore and no custom step, with provenance certainty limited to "official repository, R-universe pipeline". 2 and 3: higher build-provenance certainty, a nonstandard restore and an untested mechanism (3). | None for 1 | PI decision | Blocks C2 |
| D8-1T | T | Align the project library (option 1a) | §4.5 plan | **1a:** install the verified binary into the project library | 1b: keep the source-built copy | 1a: library equals the reference. 1b: a documented metadata-only difference remains permanently. | The 1a test in §4.5 | Download (6 KB) and installation into the project renv library | Blocks C2 under 1a; not under 1b |
| D8-2 | G/T | Status and destination of the Python lock | §5 | Promote byte-identically to `reports/environment/python_lock/v2/` with a manifest | Keep as a test artifact; regenerate | Promote: C3 passes. Keep: C3 stays partial. Regenerate: no benefit, more work. | None | File creation (new record) | Blocks C3 |
| D8-3 | G | Project-package build | F7, F8, §6 | **Option 3:** out of D8 scope; code identity at the lock gate | 1: scratch wheel test; 2: git archive (unsuitable) | 3: no test, with a clear boundary; requires code-identity recording at the lock gate, which is not yet implemented. 1: confirms the build, adds no runtime evidence, and needs a backend pin choice. | None for 3 (§6 plan for 1) | PI decision (scratch build for option 1) | Blocks C4 |
| D8-4 | G | D8 environment boundary and the 77 base pip packages | F12, F13, §5 item 2, §7 | **Option C:** conda layer plus `.venv` layer; execution only through `.venv` | A: full base; B: dedicated environment | C: smallest defensible scope. A: pins unrelated software. B: cleanest, but needs a new environment and a new test. | None for C | PI decision | Blocks C7 |
| D8-5 | G | R interpreter standard | F9, F10, §8 | Identity-scoped standard: installer, receipt and BOM | Add a SHA-256 payload comparison (download); full reinstall in a VM | Recommended: evidence complete, CRC32-level file check. Payload comparison: cryptographic file check. VM: tests installability only. | None (optional payload comparison) | PI decision (download for the optional check) | Blocks C5 |
| D8-6 | G | D8 acceptance criteria | §9 | Adopt the §9 rubric and its L1–L7 definitions | Stricter (L7 inside D8); looser (versions only) | Stricter: unattainable until analyses exist. Looser: overstates reproducibility. | None | PI decision | Prerequisite for D8-8 |
| D8-7 | T | Minimal canonical edits | §10 | DP1 and DP2 now (DP3 useful); DP4 at approval | Defer all edits until approval | Now: canonical files stop saying "not performed". Defer: the stale statement remains until approval. | Line and pipe-count checks | Canonical-file edit authorization (with pre-edit copies) | DP1 and DP2 block the D8 review |
| D8-8 | G | Final D8 approval | All of the above | Approve once D8-1 to D8-7 are resolved and C1–C7 are PASS or documented out of scope | Defer | Approve: Tier B step 1 completes, and the annotation pin creation becomes eligible for its own separate authorization. Defer: Tier B stays blocked. | — | Explicit PI approval | Gates Tier B |

## 12. Remaining authorization gates

| Gate | Needed for |
|---|---|
| Edits to the canonical SAP and brief (DP1, DP2, optionally DP3) | D8-7 |
| Creating `reports/environment/python_lock/v2/` | D8-2 |
| Downloading the 6 KB BiocVersion binary and installing it into the project renv library | D8-1T, option 1a only |
| A scratch-only wheel build | D8-3, option 1 only |
| A download of about 105 MB for the payload comparison | D8-5, optional |
| D8 approval | D8-8 |
| Creating the annotation pin | After D8 approval; separate |

## 13. Manifest

SHA-256 values for this report and its evidence files are in `SHA256SUMS` in this directory.

| File | Content |
|---|---|
| `evidence/r_framework_vs_receipt_bom.tsv` | Per-file status, size and CRC32 from the receipt BOM |
| `evidence/r_framework_paths_not_in_receipt.txt` | Paths on disk not listed in the BOM |
| `evidence/r_receipt_sha256.txt` | SHA-256 of the receipt `.bom` and `.plist` |
