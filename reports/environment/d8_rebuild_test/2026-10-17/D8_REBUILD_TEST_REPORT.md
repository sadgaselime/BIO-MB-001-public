# BIO-MB-001: D8 throwaway rebuild test (2026-10-17)

**Status:** test evidence for a later D8 approval review. This report does **not** approve D8, the SAP, or the annotation pin. No QC, eligibility computation, sample selection, differential expression, pathway analysis, ML, or other real-data analysis was run. No canonical file, project environment, or dependency declaration was changed. Nothing was staged, committed, or pushed.

## 1. Authorization and scope

- **Authorization:** explicit PI authorization (2026-10-17), "D8 Throwaway Rebuild Test: Authorized Execution". It covers the downloads and installations strictly necessary for the test, into isolated, disposable targets only.
- **Objective:** determine whether the recorded R and Python environments can be reconstructed from their recorded specifications, and identify missing locks or provenance.
- **Platform scope:** macOS 26.6.2 (25G83), arm64, the same machine. No cross-platform or numerical-identity claim is made.
- **Disposable targets:** all under the session scratch directory outside the source tree (`<SCRATCH>/d8_rebuild/`):
  - `conda_env`, `conda_pkgs`;
  - `venv`, `wheels`;
  - `rproj`, `renv_root`, `renv_sandbox`, `r_user`, `r_libs_user`;
  - `dl_r`, `dl_rpkgs`, `tmp`.

  All were removed after evidence collection (§8). Only evidence files are in this directory.

## 2. Preflight (2026-10-17T16:43:33Z)

- **Repository:** `/Users/sadgasalim/Documents/BIO-MB-001`, branch `main`, HEAD `f4d781001a91eb6c571dcb19364f4b4437c59a0d`.
- **Working tree:** 0 staged files.
  - Modified: `README.md` (`8e52c51b62a48478f4cbd2d0ebf34ac5c46527bb410f7b8b8d18d64df69b3c57`) and `src/biomarker_project/__init__.py` (`5b6fc851ef3db59d53b5a9a138df893d295277798be21d88ca61030e6917adc1`). Both are the user's own modifications and are unchanged.
  - Everything else is untracked, as before.
- **Canonical files (recomputed):**
  - SAP `reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md`: `a51437993c89485c674f9c011b09f3776b6b095a0106213ec51c99433cbb3b60`
  - Brief `reports/phase3b/v7/DECISIONS_REQUIRED_BEFORE_SAP_APPROVAL.md`: `a5870e8884a0dd887ae44a6a9dbc56775399a5db17a1e560c904d781cb09c6ac`
- **Source records.** Each was recomputed and matches its previously recorded value:

| Record | SHA-256 |
|---|---|
| `reports/environment/d8_environment_capture/v1/conda_explicit_base.txt` | `52e2e785b7e7c92a0435beab3476fbb7966047ea920ad9bfcd15a1cd5b3eb731` |
| `reports/environment/d8_environment_capture/v1/manifest.json` | `31e1b9fb2c716cebbb189213016001f77cb23cccf969e4f70b72a88026f293be` |
| `renv.lock` | `fa51c7b9d10dd468fbeed8b2ad83b832eb8acc83adb828dc25361cbbc4359951` |
| `reports/environment/python_lock/v1/requirements.snapshot.txt` | `f7bffbf3fd57bdc1553adac9d045fb366eea67fc2814751f2155fe20f846560e` |
| `reports/environment/python_lock/v1/pip_inspect.json` | `47aa44f1fe6514c299fc8b3ad173fdb2eaeff4f92fa516f87822921cec2587e9` |
| `reports/environment/python_lock/v1/manifest.json` | `e7327e6221eccbece5c8ccd03a5b74c5a7c3cfd2a137cab227d2f2a077d74bb3` |
| `reports/environment/d8_readonly_checks/v1/d8_readonly_checks.json` | `98561cf9a31251be5855aec066e8f95299197931adf3ee8fc6602bc9b22209ac` |
| `reports/environment/D8_R_LIMMA_INSTALLATION.md` | `a5b3d2ffc6d02cded9732b6e0221f0e45c605c7d093f77104dc2e2e2e4182171` |
| `pyproject.toml` | `ca8c8bae73d6f4b894915914ad23b16b7f181f769b8c76e733362bcc9d5e1cfd` |
| `.Rprofile` / `renv/activate.R` / `renv/settings.json` | `3f9d62fc…` / `10cb02fe…` / `6b42809c…` (full values in `evidence/r_throwaway_inputs_sha256.txt`) |

- **Must-not-change baseline:** recorded before the test in `evidence/baseline_before.txt` and after it in `evidence/baseline_after.txt`; see §8. It covers:
  - the base conda explicit list;
  - `/opt/anaconda3/conda-meta` and `/opt/anaconda3/pkgs` listings;
  - `.venv` pip freeze;
  - every file in the project renv library;
  - `~/.conda/environments.txt` and `/opt/anaconda3/.condarc`;
  - the R framework library listing;
  - the R/renv/pyproject configuration files.

## 3. Conda / base Python (target A)

**Input:** `conda_explicit_base.txt`, conda 26.1.1, `osx-arm64`, 545 entries. Channels:
- 540 from `repo.anaconda.com/pkgs/main`;
- 3 from conda-forge `noarch`;
- 2 from conda-forge `osx-arm64`.

**URL availability:** all 545 URLs returned HTTP 200 to a HEAD request; total Content-Length 874,770,425 bytes (`evidence/conda_url_head_check.tsv`).

**Command** (run with the working directory in scratch):

```
CONDA_PKGS_DIRS=<SCRATCH>/d8_rebuild/conda_pkgs CONDA_REGISTER_ENVS=false \
  /opt/anaconda3/bin/conda create -y -p <SCRATCH>/d8_rebuild/conda_env \
  --file reports/environment/d8_environment_capture/v1/conda_explicit_base.txt
```

- **Run:** 2026-10-17T16:45:24Z to 16:47:03Z, exit 0, empty stderr.
- **Isolation:**
  - The package cache was redirected to scratch, so nothing was written to `/opt/anaconda3/pkgs`.
  - Environment registration was disabled; `~/.conda/environments.txt` is unchanged.

**Results:**
- `conda list --explicit --md5` of the rebuilt prefix is **identical** to the input: all 545 URL+MD5 lines (`evidence/conda_rebuilt_explicit.txt`). The name/version/build sets of the conda packages are identical (545 = 545).
- Every downloaded archive's SHA-256 **matches** the `sha256` in the corresponding base `conda-meta` record (545/545), and every MD5 matches (`evidence/conda_archive_sha256_vs_base_records.tsv`). conda also verified each MD5 from the explicit file.
- Interpreter: `Python 3.13.9 | packaged by Anaconda, Inc. | (main, Oct 21 2025, 19:11:29) [Clang 20.1.8 ]`, with sqlite 3.51.0 and OpenSSL 3.6.2.

**Limitations:**
1. **The installed `bin/python3.13` hash is prefix-dependent.** The rebuilt binary is `f41dbc35…`; the base binary is `e2b3c517…`, as recorded in `d8_readonly_checks/v1`. Both are 6,045,728 bytes, contain their own prefix once and no build placeholder, and carry ad-hoc signatures. The package declares `file_mode: binary` with a build-prefix placeholder, and the pristine package file (`2954439e…`) matches its `paths.json`. The installed-binary hash therefore cannot serve as an identity check across prefixes; the package-archive hash is the valid identity.
2. **The base environment also holds 77 pip-installed (`pypi`) packages** that `conda list --explicit` does not capture (`evidence/base_pypi_packages_not_in_explicit_spec.txt`). The rebuilt prefix has 0. The project `.venv` uses `include-system-site-packages = false`, so these packages are outside the project's Python environment. The explicit spec reconstructs the conda layer of the base, not the whole base prefix.
3. **conda refreshed its channel-notices cache** at `~/Library/Caches/conda/notices` (a pre-existing user cache) during `conda create`. No terms-of-service prompt occurred, and `~/Library/Caches/conda-anaconda-tos` was not modified.

## 4. Project Python dependencies (target B)

**Inputs:**
- `requirements.snapshot.txt`: 17 packages, exact versions.
- `d8_readonly_checks.json`: the installed wheel tags, file-hash verification and `RECORD` hashes for each package.
- `pyproject.toml`: declares only minimum versions.
- **No pip configuration exists** (global, user or site), so packages came from the default index (PyPI). This is inferred from the absent configuration; the original installation did not record its index.

**Lock construction.** For each third-party package:
1. Query `https://pypi.org/pypi/<name>/<version>/json`.
2. Select the single wheel whose filename tag set equals the recorded installed tag set. Exactly one candidate existed for each of the 16 packages; no guessing was needed.
3. Download it and verify its SHA-256 against PyPI's published digest: 16/16 match.

Outputs: `evidence/python_wheel_resolution.tsv` and the test lock `evidence/requirements.hashes.TEST.txt`.

**Installation** (2026-10-17T16:49Z):

```
<SCRATCH>/d8_rebuild/conda_env/bin/python3 -I -m venv <SCRATCH>/d8_rebuild/venv
PIP_CONFIG_FILE=/dev/null <SCRATCH>/d8_rebuild/venv/bin/python -I -m pip install --disable-pip-version-check \
  --no-cache-dir --require-hashes --no-deps --only-binary=:all: --no-index \
  --find-links <SCRATCH>/d8_rebuild/wheels -r evidence/requirements.hashes.TEST.txt
```

The venv bootstrapped pip 25.2 through ensurepip, which the lock then replaced with pip 26.2.1.

**Results:**
- The command exited 0, and `pip check` reports no broken requirements.
- `pip freeze` of the rebuilt venv equals the recorded snapshot, minus the local project (`evidence/venv_rebuilt_freeze.txt`).
- **File-level identity.** For all 16 packages, every hashed file in the installed `RECORD` is identical to the original `.venv` by path and SHA-256: 3,567 files in total. Excluded: `.pyc` files, `INSTALLER`, `REQUESTED`, `direct_url.json`, `RECORD` itself, and console scripts under `bin/`. Every rebuilt file also re-hashes to its own `RECORD` (`evidence/venv_installed_file_comparison.json`).
- numpy links Apple Accelerate for both BLAS and LAPACK, as in the original (`evidence/venv_import_smoke.json`, `evidence/venv_numpy_otool.txt`). The smoke test only imports packages and prints versions; it runs no computation.

**Classification:**

| Item | Classification |
|---|---|
| 16 third-party packages (certifi, charset-normalizer, idna, iniconfig, numpy, packaging, pandas, pip, pluggy, Pygments, pytest, python-dateutil, PyYAML, requests, six, urllib3) | **Rebuilt and verified.** Hash-pinned wheels; installed files identical to `.venv`. |
| Base interpreter (from the rebuilt conda environment) | **Rebuilt with documented limitations** (§3: prefix-dependent binary hash) |
| `biomarker-project==0.1.0` (local, editable) | **Not rebuilt in this test.** An editable install would rewrite `src/biomarker_project.egg-info` inside the source tree. Its build backend requirement, `setuptools>=64`, is unpinned, and the setuptools version used originally is not recorded. |

**The lock is a test artifact.** `requirements.hashes.TEST.txt` was generated as evidence. It was not adopted, and no project dependency declaration was changed.

## 5. R environment (target C)

**System R.** The installer cannot be reinstalled in isolation: `installer` needs administrator rights and writes to `/Library/Frameworks`, which would modify the existing installation. I verified the recorded installer instead, and downloaded it to scratch without installing it:
- Source: `https://cran.r-project.org/bin/macosx/sonoma-arm64/base/R-4.6.1-arm64.pkg`.
- Size: 105,066,342 bytes.
- SHA-1 `fc9f4ada15589e8e037b9bf05563d21e97181635` and SHA-256 `67f6eea4ced4ce48f0a0d4fa3a1cac43d1859a05a88993ee3dff7c52e7edbc4b` are identical to the D8 record.
- Signature: Developer ID Installer Simon Urbanek (VZLD955F6P), notarized; `spctl` accepted it.
- Installed receipt: `org.R-project.R.fw.pkg` 4.6.1, install-time 1791804668.

Evidence: `evidence/r_installer_verification.txt`.

**Package artifacts, independently downloaded.** These match the repository `PACKAGES` MD5s and are byte-identical (SHA-256) to the D8 record §3/§3a (`evidence/r_package_artifacts.tsv`):

| Artifact | SHA-256 |
|---|---|
| `renv_1.3.1.tgz` | `4207d0bf47d362c0e2ec47bd085d6ba7b12377081a0414bb545169ae595644f3` |
| `BiocManager_1.30.27.tgz` | `b06f1048b9bd9c5731e656184a70645994fc8e8992b514b9aceb5177c51bdae0` |
| `statmod_1.5.2.tgz` | `80f2c8d675bc2d18dd6be692f162c8bd4b0d500d8ac490ed75464af18775e8fc` |
| `limma_3.68.5.tgz` | `b3f18c81c502dc3e9653f7d5e58898e9ddb6615f3f4808e91d450c36824eada7` |
| `BiocVersion_3.23.1.tgz` (binary) | `cea69c8e00240f6f6c0aeb8f7123c39f21132df8487d96d98018b6e0ef5f9805` |
| `BiocVersion_3.23.1.tar.gz` (source) | `7a9fdd2f50e69facc752a8d8aede12cdc872d1fb59fea2355f3b499ace6864f4` |

**Throwaway restore.** The four project R configuration files (`renv.lock`, `.Rprofile`, `renv/activate.R`, `renv/settings.json`) were copied unmodified to `<SCRATCH>/d8_rebuild/rproj` (hashes in `evidence/r_throwaway_inputs_sha256.txt`). Then:

```
cd <SCRATCH>/d8_rebuild/rproj
RENV_PATHS_ROOT=<SCRATCH>/d8_rebuild/renv_root RENV_PATHS_SANDBOX=<SCRATCH>/d8_rebuild/renv_sandbox \
R_USER_CACHE_DIR=… R_USER_DATA_DIR=… R_USER_CONFIG_DIR=… R_LIBS_USER=<SCRATCH>/d8_rebuild/r_libs_user \
TMPDIR=<SCRATCH>/d8_rebuild/tmp LC_ALL=en_US.UTF-8 Rscript -e 'renv::restore(prompt = FALSE)'
```

- **Run:** 2026-10-17T16:52Z, exit 0.
- **What was installed:** renv 1.3.1 (bootstrapped by `activate.R`), BiocManager 1.30.27, BiocVersion 3.23.1, statmod 1.5.2 and limma 3.68.5. All are at their locked versions. R 4.6.1 runs on `aarch64-apple-darwin23`; BLAS and LAPACK are R's reference libraries (LAPACK 3.12.1); `BiocManager::version()` returns 3.23 (`evidence/r_throwaway_status_sessioninfo.txt`).
- **Downloaded binaries:** the binaries renv downloaded have the same SHA-256 as the independently verified artifacts above (`evidence/renv_downloaded_binaries_sha256.txt`).
- **File-level comparison with the project library** (`evidence/r_library_file_comparison.txt`, `evidence/r_description_field_diff.txt`):

| Package | Comparison |
|---|---|
| renv | All 77 files identical |
| BiocManager, statmod, limma | Every file identical except `DESCRIPTION` and `Meta/package.rds`. The only differences are installer-added `Remote*` fields; for limma, also field order. |
| BiocVersion | Differs. `DESCRIPTION`, `Meta/*.rds` and the help files differ; `NAMESPACE` is identical. See below. |

**`renv::status()`.** It again showed the two observations already documented in D8 record §3a:
- limma is "out of sync [3.68.5: unchanged]", because renv adds `RemoteType` to packages it installs itself;
- packages show "used: n", because the throwaway copy contains no R code.

**BiocVersion provenance caveat.** The restore installs the binary from the official Bioconductor 3.23 binary repository (`bioconductor.org/packages/3.23/bioc/bin/macosx/sonoma-arm64/contrib/4.6`). The project library holds the version that was built from source on 2026-10-12.

| Field | Restored binary | Project library (built from Bioconductor source) |
|---|---|---|
| `Version` | 3.23.1 | 3.23.1 |
| `Repository` | `https://bioc.r-universe.dev` | `Bioconductor 3.23` |
| `Depends` | `R (>= 4.4.0)` | `R (>= 4.6.0)` |
| Commit | `RemoteSha 252d7c8f03a39a9b83f6de7e9dbf9a5ee6584365`, `RemoteRef HEAD` | `git_last_commit 252d7c8` (branch `devel`) |
| `Packaged` / `Built` | 2026-03-01 08:31:08 UTC by `root`; built under R 4.6.0. Archive file owner is `runner`. | 2025-10-30 by `biocbuild`; installed under R 4.6.1 on 2026-10-12 |

**What the evidence supports, and what it doesn't:**
- *Supported:* the binary served by the official Bioconductor 3.23 repository carries r-universe metadata and the same version and short commit as the Bioconductor-built source.
- *Not established:* which organization's build infrastructure produced the binary, or whether the two installations are functionally equivalent. No such claim is made.

**Consequence.** Restoring from `renv.lock` reproduces every locked version, and four of the five packages are file-identical in code. For BiocVersion, it does not reproduce the project library's source-built installation byte for byte.

**Smallest evidence-backed remedies** (not tested; each needs a PI decision):
- **(a)** Accept the binary and record the documented metadata difference.
- **(b)** Add a documented restore step that installs BiocVersion 3.23.1 from the verified source tarball (`7a9fdd2f…`), as was done on 2026-10-12, without changing `renv.lock`.

## 6. Deviations from the authorized plan

- **System R was not reinstalled** (see §5). The installer was downloaded and verified only.
- **The local `biomarker-project` package was not installed** (see §4).
- **No other substitutions.** No package version, source or specification was changed to force success.

## 7. Verdicts

| Target | Verdict | Basis |
|---|---|---|
| A. Conda base (conda layer) | **PASS** | 545/545 archives available and SHA-256-identical to the base records; rebuilt explicit list identical to the specification |
| A'. Whole base prefix | **PARTIAL** | 77 pip-installed packages are not in the explicit spec; installed binary hashes are prefix-dependent |
| B. Project third-party Python packages | **PASS** | Hash-pinned lock built without guessing; 16/16 PyPI digests verified; installed files identical to `.venv` |
| B'. Local project package | **NOT TESTED** | Editable install writes into the source tree; build backend unpinned |
| C. R packages from `renv.lock` | **PARTIAL** | All versions restored, and binaries match the recorded SHA-256; BiocVersion restores as the r-universe-metadata binary, not the recorded source build |
| C'. System R 4.6.1 | **PARTIAL** (installer verified, not reinstalled) | Installer hash, signature and notarization match the record; reinstalling needs administrator rights and would modify the existing installation |

**Reconstruction is not reproducibility.** The test shows that the recorded specifications resolve, on this machine on 2026-10-17, to the same artifacts as the existing environments. It does **not** show:
- that the artifacts will remain available;
- that results reproduce on other machines or OS versions;
- that numerical output is identical.

None of these was tested.

## 8. Cleanup and preservation

- **Removed** (2026-10-17T16:54:29Z): the entire `<SCRATCH>/d8_rebuild` tree, about 5.6 GB. It held the conda environment and package cache, the venv, the wheels, the R installer, the R package downloads, the renv root, the throwaway project and the temporary directories.
  - renv's sandbox directory was read-only and held only symlinks to base R packages plus a marker file. Its write bit was set, on the directory only, before removal; no link was followed.
- **Kept:** the four small test scripts, copied to `evidence/test_scripts/`.
- **Not removed:** no source archive or pre-existing evidence record.
- **Baseline after cleanup** (`evidence/baseline_after.txt`): identical to `baseline_before.txt`. Unchanged:
  - the base conda explicit list (still `52e2e785…`);
  - the `/opt/anaconda3` `conda-meta` and `pkgs` listings;
  - `.venv` pip freeze;
  - every file in the project renv library;
  - `~/.conda/environments.txt` and `/opt/anaconda3/.condarc`;
  - the R framework library listing;
  - `.Rprofile`, `renv/settings.json`, `renv/activate.R` and `pyproject.toml`.
- **R user cache:** the `~/Library/Caches/org.R-project.R` tree listing is unchanged.
- **Side effect:** conda refreshed its notices cache (§3, limitation 3).

## 9. Outstanding for D8 review

1. **Biggest gap.** The PI decides how the D8 record handles the BiocVersion restore difference: remedy (a) or (b) in §5.
2. **Python lock.** Decide whether a hash-pinned Python lock (the content of `requirements.hashes.TEST.txt`, or a regenerated equivalent) should become a project record. It would be a new file; `pyproject.toml` is not to be changed without authorization.
3. **Local package.** Decide how the local `biomarker-project` package and its build backend (setuptools) are to be pinned, or declared out of scope.
4. **Base environment scope.** Decide whether the 77 pip-only packages in the Anaconda base are formally out of D8 scope (the project venv excludes them), or whether the interpreter should come from a dedicated minimal environment.
5. **SAP citation.** Cite this report and the D8 capture in the SAP D8 row (v7:611). That is a canonical-file edit and needs separate authorization.
6. **D8 approval** itself remains a separate PI decision.

## 10. Files

Every file in this directory is listed with its SHA-256 in `SHA256SUMS`, next to this report.
