# D8 R/limma environment — installation record

Installation date: 2026-10-12 (R framework receipt install time 2026-10-12 11:31:08 UTC).
BiocVersion 3.23.1 added 2026-10-12 (PI approval; §3a).
Scope: the approved D8 environment only. No real GEO data were read; no confirmatory analysis is enabled.
`renv` pins the project R *package library*; it does **not** pin the system R installation, which is
recorded separately below.

## 1. Platform

| Item | Value |
|---|---|
| OS | macOS 26.6.2 (Tahoe), build 25G83 |
| Architecture | arm64 (R platform `aarch64-apple-darwin23`) |
| Project Python | `.venv`, Python 3.13.9 (unchanged) |

## 2. System R (outside renv)

| Item | Value |
|---|---|
| Version | R 4.6.1 (2026-06-24) "Happy Hop" |
| R home (`R RHOME`) | `/Library/Frameworks/R.framework/Resources` |
| Executables | `/usr/local/bin/R`, `/usr/local/bin/Rscript` → `/Library/Frameworks/R.framework/Resources/bin/` |
| Installer | `R-4.6.1-arm64.pkg`, official CRAN: `https://cran.r-project.org/bin/macosx/sonoma-arm64/base/R-4.6.1-arm64.pkg` (105,066,342 bytes) |
| SHA-1 (published on the CRAN macOS page) | `fc9f4ada15589e8e037b9bf05563d21e97181635` — **matched** (`openssl sha1`) |
| SHA-256 (computed) | `67f6eea4ced4ce48f0a0d4fa3a1cac43d1859a05a88993ee3dff7c52e7edbc4b` |
| Signature (`pkgutil --check-signature`, CRAN's documented method) | Developer ID Installer: Simon Urbanek (VZLD955F6P); chain to Apple Root CA; trusted timestamp 2026-06-25 21:58:22 UTC |
| Notarization / Gatekeeper | "trusted by the Apple notary service"; `spctl --assess --type install`: accepted, source = Notarized Developer ID |
| Install command (run by the PI; needs an admin password) | `sudo installer -pkg R-4.6.1-arm64.pkg -target /` |
| Receipts (`pkgutil --pkgs`) | `org.R-project.R.fw.pkg` 4.6.1 (Library/Frameworks); `org.R-project.R.GUI.pkg` 1.83 (Applications); `org.r-project.arm64.tcltk` 8.6.13; `org.r-project.arm64.texinfo` 7.3 — all install-time 1791804668 |

## 3. Project-local package environment (renv)

| Package | Version | Source | Binary URL | Bytes | MD5 published = downloaded | SHA-256 |
|---|---|---|---|---|---|---|
| renv | 1.3.1 | CRAN | `https://cran.r-project.org/bin/macosx/sonoma-arm64/contrib/4.6/renv_1.3.1.tgz` | 2,666,400 | `8883824eda66da595523614332bdb23a` ✓ | `4207d0bf47d362c0e2ec47bd085d6ba7b12377081a0414bb545169ae595644f3` |
| BiocManager | 1.30.27 | CRAN | `…/contrib/4.6/BiocManager_1.30.27.tgz` | 662,320 | `d9ebb67fc8390a1f780fc5ef9ade7af8` ✓ | `b06f1048b9bd9c5731e656184a70645994fc8e8992b514b9aceb5177c51bdae0` |
| statmod | 1.5.2 | CRAN | `…/contrib/4.6/statmod_1.5.2.tgz` | 333,151 | `6d9c4881d82782fbd347197be486292d` ✓ | `80f2c8d675bc2d18dd6be692f162c8bd4b0d500d8ac490ed75464af18775e8fc` |
| limma | 3.68.5 | Bioconductor 3.23 (RELEASE_3_23, RemoteSha `825d1c8330d024adb6c54af66d79b0f4ec258530`) | `https://bioconductor.org/packages/3.23/bioc/bin/macosx/sonoma-arm64/contrib/4.6/limma_3.68.5.tgz` | 2,968,964 | `3feec182f3e9d7a77ce6a4c4d1043b53` ✓ | `b3f18c81c502dc3e9653f7d5e58898e9ddb6615f3f4808e91d450c36824eada7` |

### 3a. BiocVersion (added after PI approval, 2026-10-12)

| Item | Value |
|---|---|
| Installed version | BiocVersion 3.23.1 (`BiocManager::version()` → 3.23) |
| Installed from | official Bioconductor 3.23 **source** package `https://bioconductor.org/packages/3.23/bioc/src/contrib/BiocVersion_3.23.1.tar.gz` (990 bytes) |
| Source MD5 (published in `…/3.23/bioc/src/contrib/PACKAGES`) = downloaded | `1ea22c71ce7f9862be8dcfaa37a2f1e4` ✓; SHA-256 `7a9fdd2f50e69facc752a8d8aede12cdc872d1fb59fea2355f3b499ace6864f4` |
| Source DESCRIPTION | `Repository: Bioconductor 3.23`; packaged by `biocbuild` 2025-10-30; git commit 252d7c8; `Depends: R (>= 4.6.0)`; `NeedsCompilation: no` (DESCRIPTION, NAMESPACE and one Rd file; no compilation) |
| Binary also checked (not installed) | `…/3.23/bioc/bin/macosx/sonoma-arm64/contrib/4.6/BiocVersion_3.23.1.tgz` (6,054 bytes), MD5 `dab387f575308ddd75ffaba682bd35fd` ✓ (published), SHA-256 `cea69c8e00240f6f6c0aeb8f7123c39f21132df8487d96d98018b6e0ef5f9805` |
| Why source, not binary | the official 3.23 arm64 binary was built by r-universe (`Repository: https://bioc.r-universe.dev`, `RemoteRef: HEAD`, `Depends: R (>= 4.4.0)`, built 2026-03-01); installing it would record r-universe as the source. The source package is the same 3.23.1 release from the same official repository, built by Bioconductor, with Bioconductor 3.23 metadata |
| Command | `install.packages("BiocVersion_3.23.1.tar.gz", repos = NULL, type = "source", lib = <project renv library>)`, then `renv::snapshot(packages = c("renv","BiocManager","limma","statmod","BiocVersion"), prompt = FALSE)` (standard snapshot, no `force`) |
| Other packages | verified unchanged before/after: limma 3.68.5, renv 1.3.1, BiocManager 1.30.27, statmod 1.5.2 |
| `renv::status()` | "No issues found -- the project is in a consistent state." The startup "out-of-sync" message no longer appears |
| Isolated restore check | lockfile + `.Rprofile` + `renv/activate.R` + `renv/settings.json` copied to a throwaway project (separate `RENV_PATHS_ROOT`); `renv::restore(prompt = FALSE)` downloaded and installed all packages at the locked versions (renv 1.3.1, BiocManager 1.30.27, statmod 1.5.2, limma 3.68.5, BiocVersion 3.23.1). The project environment was not touched |
| Restore-check observations | (i) renv restored BiocVersion from the 3.23 **binary** repository, i.e. the r-universe-built binary (same version and git commit 252d7c8; different `Repository`/`Depends` metadata) — a restore on another Mac does not reproduce the source-built file byte-for-byte; (ii) `renv::status()` in the throwaway copy listed limma as "out of sync [3.68.5: unchanged]" only because renv adds `RemoteType: bioconductor` to packages it installs itself (version and content identical apart from DESCRIPTION line wrapping), and listed packages as "used: n" because the copy contains no R code |

Expected MD5s come from each repository's `PACKAGES` index for the sonoma-arm64 / R 4.6 binaries.
Each binary was downloaded, verified, and then installed from that verified file into the project
library (`renv/library/macos/R-4.6/aarch64-apple-darwin23/`). R's installer also reported
"SHA256 sums checked" for the package contents.

Bioconductor 3.23 corresponds to R 4.6 (`r_ver_for_bioc_ver` in `https://bioconductor.org/config.yaml`)
and is pinned in `renv/settings.json` (`bioconductor.version: "3.23"`) and in `renv.lock`.
The global renv package cache is disabled (`use.cache: false`).

**Repository configuration** (as set by renv): CRAN `https://cloud.r-project.org`; BioCsoft
`https://bioconductor.org/packages/3.23/bioc` (plus BioCann/BioCexp/BioCworkflows/BioCbooks for 3.23).

## 4. Commands (in order)

```
curl … https://cran.r-project.org/bin/macosx/                                # metadata
curl … https://bioconductor.org/config.yaml; …/packages/3.23/bioc/html/limma.html
curl -o R-4.6.1-arm64.pkg https://cran.r-project.org/bin/macosx/sonoma-arm64/base/R-4.6.1-arm64.pkg
openssl sha1 R-4.6.1-arm64.pkg; shasum -a 256 R-4.6.1-arm64.pkg
pkgutil --check-signature R-4.6.1-arm64.pkg; spctl --assess --type install -vv R-4.6.1-arm64.pkg
sudo installer -pkg R-4.6.1-arm64.pkg -target /                              # by the PI
R --version; R RHOME; pkgutil --pkgs; pkgutil --pkg-info org.R-project.R.fw.pkg
curl <repo>/PACKAGES; curl <repo>/<pkg>.tgz; MD5/SHA-256 verification        # 4 packages
R CMD INSTALL -l <scratch bootstrap lib> renv_1.3.1.tgz
Rscript --vanilla -e "renv::init(bare=TRUE, bioconductor='3.23', settings=list(use.cache=FALSE), …)"
Rscript -e "install.packages(<verified .tgz>, repos=NULL, type='binary', lib=<project renv library>)"   # renv, statmod, BiocManager, limma
Rscript -e "renv::snapshot(packages=c('renv','BiocManager','limma','statmod'), prompt=FALSE, force=TRUE)"
```

`RENV_PATHS_ROOT` pointed at a temporary directory during installation so that renv's cache/index did
not touch the user's global renv root.

## 5. sessionInfo() (project, limma attached)

```
R version 4.6.1 (2026-06-24)
Platform: aarch64-apple-darwin23
Running under: macOS Tahoe 26.6.2
Matrix products: default
BLAS:   /Library/Frameworks/R.framework/Versions/4.6/Resources/lib/libRblas.0.dylib
LAPACK: /Library/Frameworks/R.framework/Versions/4.6/Resources/lib/libRlapack.dylib;  LAPACK version 3.12.1
locale: en_US.UTF-8/en_US.UTF-8/en_US.UTF-8/C/en_US.UTF-8/en_US.UTF-8
time zone: Asia/Muscat
attached base packages: stats graphics grDevices datasets utils methods base
other attached packages: limma_3.68.5
loaded via a namespace: BiocManager_1.30.27 compiler_4.6.1 tools_4.6.1 renv_1.3.1 statmod_1.5.2
```

Every pipeline run with `analysis.method: limma` also stores the runner's version check and
`sessionInfo()` in its `provenance.json` (`r_environment`).

## 6. Checksums of resulting files

| File | SHA-256 |
|---|---|
| `renv.lock` (after BiocVersion, current) | `fa51c7b9d10dd468fbeed8b2ad83b832eb8acc83adb828dc25361cbbc4359951` |
| `renv.lock` (initial D8 snapshot, superseded) | `7ed4563fc7ab81237369723a58b860c89b67a616f298469f86a7a7cc0a811888` |
| `.Rprofile` | `3f9d62fc3f1bf5888a09816101b705f9844ef4cd44ee5ad157f4168dac4af4d4` |
| `renv/settings.json` | `6b42809ced3edcc0dadf5043b0ee4777cc9a5d59ae43857cac99235a448a8890` |
| `renv/activate.R` | `10cb02fe000afc9814ca287f18c9e525dd8a031712a440e48eef6e1893eed94b` |
| `renv/.gitignore` | `2c31e978189a98022566bd6084936f5608222b2bb9230b8d189b5a1c97a2c2da` |
| `R/limma_de.R` | `38daec142a85dbeff89e32fca3bfc3e14a40ac01efe2fd28c6613bba11257b83` |

`renv.lock` (renv 1.3.1 format) records versions, sources and repositories but no per-package
hashes; the binary checksums are recorded in §3.

## 7. Warnings and deviations

1. **statmod 1.5.2** is a required limma import; approved by the PI as a dependency (verified as above).
2. **BiocVersion — resolved 2026-10-12.** Initially not installed (not yet approved), so the first
   lockfile was written with `force = TRUE` and renv reported the project out of sync. After PI
   approval, BiocVersion 3.23.1 was installed from the verified official source package and the
   lockfile was re-snapshotted normally (§3a); the project is now in a consistent state.
3. **BiocManager fetched by `renv::init`.** With `bioconductor = '3.23'`, `renv::init` installed BiocManager
   from CRAN on its own before the verified file was installed; it was then overwritten with the
   verified 1.30.27 binary (installed version confirmed 1.30.27).
4. **renv sandbox outside the project.** renv created its standard system-library sandbox (links to
   base R packages) at `~/Library/Caches/org.R-project.R/R/renv/sandbox/`. No packages were installed there.
5. **CRAN repository URL.** renv recorded `https://cloud.r-project.org` (the CRAN cloud mirror) rather than
   `https://cran.r-project.org`; binaries were verified against `cran.r-project.org`.
6. **R.app GUI, Tcl/Tk 8.6.13 and Texinfo 7.3** were installed by the default CRAN package together with
   the R framework.
7. A locale warning (`Sys.setlocale`) appears if R is started without a locale; the runner sets
   `LC_ALL=en_US.UTF-8`.

## 8. Files created or changed for D8

BiocVersion step changed only `renv.lock`, the project renv library and this record.
Created: `R/limma_de.R`, `src/biomarker_project/limma_backend.py`, `tests/test_limma_backend.py`,
`renv.lock`, `.Rprofile`, `renv/` (activate.R, settings.json, .gitignore, library/ — git-ignored),
this record. Changed: `src/biomarker_project/synthetic_pipeline.py` (`analysis.method`: "ols" | "limma";
limma moderation sidecar; R environment in provenance), `src/biomarker_project/sample_policy.py`
(D8 removed from the deferred list), `config/synthetic_pipeline.yaml` (`method: limma`).
No secrets, tokens or passwords are recorded here.
