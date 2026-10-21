# BIO-MB-001: source-code identity implementation, verification report (2026-10-18)

**Authorization:** explicit PI instruction "Authorize source-code identity implementation" (2026-10-18), limited to:
1. creating `code_identity.py` at the path in the plan;
2. synthetic-data-only tests;
3. the two specified SAP edits;
4. pre-edit copies, hashes and this report.

**What this does not do:** it approves neither D8-8 nor the annotation pin, nor any downstream analysis. No real study data was read. No QC, preprocessing, differential expression or ML was run. Nothing was installed or downloaded, and the environment was not changed. Nothing was staged, committed, pushed, reset or cleaned.

## 1. Preflight

| Check | Result |
|---|---|
| Plan `reports/planning/2026-10-18_model_sprint/MODEL_SPRINT_PLAN.md` | `SHA256SUMS` OK (`d13d6907…`) |
| Repository | HEAD `f4d781001a91eb6c571dcb19364f4b4437c59a0d`, 0 staged, `M README.md`, `M src/biomarker_project/__init__.py`, 53 status entries |
| SAP before editing | `161cf12d26a6e15e5ba27365cc06827ec83219144e1ae1ebb7fd5e765896bbbb` |
| User changes | `README.md` `8e52c51b…`; `__init__.py` `5b6fc851…`; both intact |
| Target paths | `src/biomarker_project/code_identity.py` and `tests/test_code_identity.py` did not exist beforehand |

## 2. Implementation: `src/biomarker_project/code_identity.py`

SHA-256 `57445bcf20f2cdec585347687781d13e2d065629a5cc2dcb1394f4f2aa965a7d`.

**Code set:**
- **Included** (the plan §6 list, exactly): `src/biomarker_project/**/*.py`, `scripts/**/*.py`, `R/**/*.R`, `tests/**/*.py`, `config/**/*.yaml`, `config/**/*.yml`, `pyproject.toml`, `renv.lock`, `.Rprofile`, `renv/activate.R`, `renv/settings.json`.
- **Excluded:**
  - any path with a directory component `__pycache__` or `.git`, or ending in `.egg-info`;
  - any file named `code_identity.json`, so the identity record is never part of its own source set.
- **Not reachable by any include pattern:** `data/`, `reports/` and other output locations, so outputs are never hashed. The exclusions and patterns are stored in each record (`spec`), and `verify` reuses the record's own specification.

**Hashing and ordering:**
- Every included file is hashed (SHA-256 of its bytes) whatever its git state: clean, modified, untracked or ignored.
- Symlinks are recorded as `kind: symlink` and hashed by their target string.
- Paths are POSIX, relative to the root and Unicode NFC, sorted by UTF-8 bytes.

**Fields recorded:**
- `git_head`;
- `git_status_porcelain` (full output of `git status --porcelain=v1 -z --untracked-files=all`, covering the whole repository);
- per file: `path`, `sha256`, `kind`, `executable`, and `git_state` (`clean`, `changed:XY`, `untracked`, `ignored` or `no_git`);
- `dirty`;
- `environment_records`: the SHA-256 of `conda_explicit_base.txt`, the `python_lock/v2` lock and manifest, and `renv.lock`; `null` if absent.

There is no timestamp, so capture is deterministic.

**Aggregate:** the SHA-256 of `"".join(f"{path}\t{sha256}\n")` over the ordered files, which is the plan's formula. `aggregate_from_files(record["files"])` recomputes it from the manifest alone.

**How `verify(record, root)` detects changes:**

| Change | Reported as |
|---|---|
| Content differs | `changed` |
| Path is gone | `missing` |
| New path | `added` |
| A missing path and an added path with equal SHA-256 | `renamed` |
| Executable bit differs | `mode_changed` |
| HEAD moved | `git_head_changed` |
| Stored aggregate doesn't match its own file list | `record_aggregate_inconsistent` |
| Repository-wide status differs | `git_status_changed`, **informational** only (it also changes when outputs are written); code-set differences are already reported per path |

The command-line `verify` exits with 1 on any non-informational mismatch.

**Integration not done (outside this authorization):** having real-data runners write `code_identity.json` next to their outputs, as plan §6 proposes, is a later source change.

## 3. Tests: `tests/test_code_identity.py`

SHA-256 `658ef61964e43aff82dc280cc910584cadc53313975836498464647efff15978`.

The tests use temporary git repositories with fake source files only. No real data is touched.

Command, run twice:

```
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -p no:cacheprovider -v tests/test_code_identity.py
```

**Result: 10 passed, both runs** (`evidence/pytest_run1.txt`, `evidence/pytest_run2.txt`). The repository's untracked-files status hash was identical before and after the test run (`e999c48b…`), so no bytecode or cache was written.

| Required check | Test |
|---|---|
| Unchanged files and repeated-run determinism | `test_unchanged_tree_is_deterministic_and_verifies`: identical records, identical written-record hashes, `verify` returns `[]` |
| Changed file | `test_changed_file` |
| Added untracked file | `test_added_untracked_file_is_hashed`: hashed, state `untracked`, present in the full status |
| Removed and renamed files | `test_removed_and_renamed_files` |
| Paths | `test_paths_are_posix_relative_nfc_and_byte_ordered`: an NFD file name is recorded as NFC |
| Exclusions | `test_exclusions_and_out_of_scope_paths`: `__pycache__`, `.egg-info`, `code_identity.json`, `reports/`, `data/` and a non-code file in `src/` are ignored; the only report is the informational status change |
| Aggregate from the manifest | `test_aggregate_reproducible_from_manifest` |
| Tampering and HEAD change | `test_record_tampering_and_head_change` |
| Mode change | `test_mode_change_detected_but_not_in_aggregate` |
| No git; environment records | `test_environment_records_and_non_git_tree` |

**Side effect found and reversed:** the read-only real-tree check ran Python with `-I`, which ignores `PYTHONDONTWRITEBYTECODE`, so it wrote `src/biomarker_project/__pycache__/code_identity.cpython-313.pyc`. That file is git-ignored and excluded from the code set. I removed it, as it was my own artifact; no other cache file was created.

**Existing project tests:** not run. None tests this module. Some of them invoke the synthetic pipeline or Rscript, and running them isn't needed to verify the module.

## 4. Read-only check on the real source tree

Source files only; no data was read. Record: `evidence/realtree_identity_check_2026-10-18.json` (its SHA-256 is in `SHA256SUMS`).

| Result | Value |
|---|---|
| Files in the code set | 62: 42 untracked, 19 clean, 1 modified (`__init__.py`) |
| Aggregate | `9df997801d9ff050a44487c0697f38be6308e760c1fc5d722a48ad73420be760` |
| Determinism | Two consecutive captures are identical |
| Independent shell recomputation over the same 62 files | `9df99780…`, **equal** |
| `verify` immediately after writing the record | Only `git_status_changed` (informational), caused by the new evidence file |
| Reconciliation with the plan baseline | The module's manifest, minus the 2 new files plus `tests/fixtures/valid_config.yaml`, gives exactly the plan baseline `7ffb05d6b5706ff87eef231da29a2635b24d92a8fb242910e59eb1aad365db72`. No baseline source file has changed. |

## 5. SAP edits

**Pre-edit copy:** `reports/_pre_edit_copies/2026-10-18_code_identity/`, holding the SAP (`161cf12d…`), `PROVENANCE.txt` and `SHA256SUMS` (2/2 OK).

| Edit | Status |
|---|---|
| **A6 timing row (v7:112)**, the requirement that every real-data output carries a verified identity record | **Applied.** Appended text: "Every output of such a computation carries a source-tree identity record (src/biomarker_project/code_identity.py: the code set with per-file SHA-256, the aggregate SHA-256, git HEAD and the full git status including untracked and modified files), verified against the source tree after the computation with no code-set mismatch; a git commit alone is not sufficient (D8-3, explicit PI authorization 2026-10-18)". |
| **Lock §7 item 8** ("The source-tree identity record (code set, aggregate SHA-256, git HEAD and status) and the D8 environment record hashes.") | **Not applied: stopped and reverted** (see below) |

**A6 edit checks:**
- `diff` against the pre-edit copy shows only `112c112`;
- 661 lines, unchanged; pipes on line 112: 4 before, 4 after;
- line 3 still reads "**Status: PROPOSED DRAFT FOR REVIEW. Not approved, not frozen.**";
- the cited module path exists.

**SAP after editing:** `27fde98d04fc6ec9d90627e07d4c0e89a13f7697d267977fba78fa5706df0d9a`

**Why the lock edit was stopped.** A new numbered list item needs a new line, which shifts every later SAP line by one. The brief cites 75 SAP line numbers at or after line 484 (for example v7:611 for D8 and v7:603–625 for the register), and the SAP cites its own lines too (v7:533, 599, 604, 605, 608, 621). All of these would silently point to the wrong lines. A line-neutral alternative isn't possible: in Markdown, two list items can't share a line, and a paragraph placed directly after the list would merge into item 8. The edit was applied, checked, and reverted. The SAP now differs from the pre-edit copy only at line 112.

## 6. Points needing the PI's attention

1. **Lock §7 item 8** (blocking for the lock gate, not for D8-8). Choose one:
   - **(a)** apply it together with a mechanical renumbering of every affected `v7:NNN` citation in the brief and in the SAP's self-citations (+1 for lines ≥ 484), verified by a script;
   - **(b)** keep the requirement only in the A6 row, which already applies to the lock as a real-data output;
   - **(c)** add it at the next SAP version.

   Recommendation: (b) for now. The A6 row already requires an identity record on every output that enters the lock.
2. **Mode changes.** Plan §6 said a mode change "alters the digest", but its digest formula (`path<TAB>sha256`) excludes mode. The implementation follows the formula, records the executable bit, and has `verify` report `mode_changed`. If you want mode inside the aggregate, that changes the formula and needs a decision.
3. **Test fixtures.** The plan's written code set (`tests/**/*.py`) excludes `tests/fixtures/` (YAML, TSV, gz and text fixtures). The plan's baseline command accidentally included one of them, `tests/fixtures/valid_config.yaml`. The implementation follows the written specification. Fixtures affect test behaviour only, not real-data outputs; adding `tests/fixtures/**` would be a small specification change.

## 7. Files changed or created

| Path | Action | SHA-256 |
|---|---|---|
| `src/biomarker_project/code_identity.py` | Created (untracked) | `57445bcf…a7d` |
| `tests/test_code_identity.py` | Created (untracked) | `658ef619…978` |
| `reports/phase3b/v7/STATISTICAL_ANALYSIS_PLAN_DRAFT.md` | Line 112 edited | `161cf12d…` → `27fde98d…` |
| `reports/_pre_edit_copies/2026-10-18_code_identity/` | Created (3 files) | See its `SHA256SUMS` |
| `reports/environment/code_identity_implementation/2026-10-18/` | Created (this report, `evidence/`, `SHA256SUMS`) | See `SHA256SUMS` |

**Unchanged:** the brief (`2cfcd4af…`), `README.md`, `__init__.py`, `renv.lock`, `pyproject.toml`, `.venv`, raw data, and all other files.

## 8. Remaining D8 blockers

- **D8-8 approval** (PI decision). Code identity is now implemented and tested, but not yet wired into any runner.
- **Lock §7 item 8 placement** (point 1 above). Not a D8 blocker if option (b) is accepted.
- **Runner integration** of `code_identity.json` (a later source change, needed before the first real-data output). It is not needed for D8-8 itself.
