# Annotation pin creation (Tier B step 2), 2026-10-18

**Authorization:** PI instruction 2026-10-18 ("okay proceed", in reply to the proposal to create the pin from the verified v2
artifacts). It authorizes this pin only. No SAP or brief edit, no eligibility (Tier B step 3), QC, differential
expression, validation or model is authorized or was run.

**Command** (project root, 2026-10-18T17:58:09Z to 2026-10-18T17:58:10Z UTC, exit=0):
`.venv/bin/python -I scripts/annotation_pin.py --version v1 --authorization "<recorded verbatim in the pin>"`

**Output:** `reports/annotation_audit/annotation_pin/v1/`, produced under the code-identity lifecycle.

| File | SHA-256 |
|---|---|
| `annotation_pin_record.json` | `cde8ccd7d87b3622227a1b174599c4786fa94906159707fc4e498c72f3253a67` |
| `code_identity.json` | `7000fa6a12bcade9e35021f007647227176a491f73014b2883520eaa5b6cd55f` |
| `manifest.json` | `d48309e7f900f5434e592317b32fa8c09ed2661b2da470f7e7662ef12bebe930` |

## Verified after creation (read-only)

**Acceptance:** `acceptance_problems(require_executed_code=True)` reports no problems.

**Executed code:** tracked. The bootstrap code objects are `scripts/annotation_pin.py` and `scripts/_executed_code.py`; 2 further files were executed through the hashing loader. The only informational mismatch was `git_status_changed`.

**Identity:** aggregate `42eaf15b…` (the same as the three v2 runs); HEAD `f4d7810`; dirty = true.

**What the record pins** (SAP v7:609):

| Item | Content |
|---|---|
| GPL570 (D6-F) | `gpl570_option_a/v2`, table `9e5f23fa…` |
| GPL6947/GPL10558 (D6-G) | `illumina_a0/v2`, tables `6da6cf2c…`, `a68aa750…`, `e5b99695…` |
| Validation evidence (v7:112) | C15 `c15_cohort_probe_presence/v2` |
| Upstream provenance | Each upstream manifest, identity record and generating-script SHA-256 |
| Archives | hgu133plus2.db 3.13.0 `ddde58e7…`, illuminaHumanv3.db 1.26.0 `cea0c9cd…`, illuminaHumanv4.db 1.26.0 `362848d6…`, org.Hs.eg.db 3.23.1 `47062066…` (each verified against reference/bioconductor_3.23/download_manifest.json) |
| Frozen gene-history v1 | `42451a70…`; its raw NCBI source is not retained (v7:643) |
| Mapping rules | D6-F and D6-G |
| SAP at creation | `34bf22d1…`, status "PROPOSED DRAFT FOR REVIEW. Not approved, not frozen." |
| D8 environment records | conda spec `52e2e785…`, Python lock v2 `a57412d3…` and its manifest `9620fe56…`, `renv.lock` `fa51c7b9…` |
| Authorization | Recorded verbatim |

**No staging or FAILED folders exist.**

**Side effect:** the run wrote a git-ignored bytecode cache file for the bootstrap registry, which was removed.

## Not yet done

- **SAP citation of the pin.** Lock item 2 at v7:465 says the pin is "cited with its SHA-256 once that record has been created". Recording this in the canonical SAP needs a separate authorization.
- **Tier B steps 3 to 5.** These remain separately gated.
