# D8 environment amendment — R glmnet (2026-10-19)

**Authorization:** explicit PI instruction, 2026-10-19 (install route "R glmnet (Recommended)"), for the
exploratory ML protocol (reports/planning/ML_PROTOCOL_DRAFT_2026-10-19.md, approved the same day as drafted).
This amends the D8 environment record (D8-8, 2026-10-18). It approves no analysis by itself.

## What was done
1. Pre-install copy of renv.lock: reports/_pre_edit_copies/2026-10-19_glmnet_install/ (SHA-256 fa51c7b9d10dd468fbeed8b2ad83b832eb8acc83adb828dc25361cbbc4359951).
2. `renv::install("glmnet@5.1", type = "binary")` from CRAN (https://cloud.r-project.org; the repository already in renv.lock).
   Six CRAN binaries were downloaded (about 15 MB) and installed into the project renv library:
   glmnet 5.1, Rcpp 1.1.2, RcppEigen 0.3.4.0.2, foreach 1.5.2, iterators 1.0.14, shape 1.4.6.1.
3. `renv::snapshot(packages = c("BiocManager","BiocVersion","limma","renv","statmod","glmnet"))`.
   The snapshot also re-described the existing BiocVersion entry from the installed DESCRIPTION
   (r-universe metadata; the known D8 observation, D8_R_LIMMA_INSTALLATION.md:50–55). That change was **not
   authorized**, so the original BiocVersion entry was restored byte-for-byte. All five pre-existing entries,
   the R block and the repositories are identical to the pre-install lock.
4. Added to renv.lock: glmnet, Rcpp, RcppEigen, foreach, iterators, shape (project library) and their
   recommended dependencies Matrix 1.7-5, survival 3.8-6, lattice 0.22-9, codetools 0.2-20 (already in R's
   system library; recorded, not installed).

renv.lock SHA-256: fa51c7b9d10dd468fbeed8b2ad83b832eb8acc83adb828dc25361cbbc4359951 → 1498fa48e9cfe38ee5a3e52416460a179e31105d4d5be111a4ec025ed16180d5

## Verification
- Existing D8 pins re-checked after install (limma_backend.check_environment): R 4.6.1, Bioconductor 3.23,
  limma 3.68.5, renv 1.3.1, BiocManager 1.30.27, statmod 1.5.2: all match.
- glmnet 5.1 loads from the project library and fits a synthetic ridge-logistic path.
- installed_packages.tsv: version, repository, build string and an installed-tree SHA-256 per package
  (SHA-256 of sorted "relative path<TAB>sha256" lines).
- renv::status() reports the new packages as "not used" until project code references glmnet (expected).

## Limitations
- CRAN binaries were not compared against a second, independent download (as was done for the D8 rebuild
  test); the installed-tree hashes are recorded for later comparison.
- The previous identity records (lock, validation) cite the old renv.lock hash; they remain valid records of
  their runs. New runs record the new hash.
