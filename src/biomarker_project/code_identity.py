"""Source-tree identity record (D8-3; reports/planning/2026-10-18_model_sprint/MODEL_SPRINT_PLAN.md §6).

A git commit alone does not identify the code that produced an output when files are untracked or
modified. ``capture`` therefore hashes every file in the code set, whatever its git state, and also
records git HEAD and the full ``git status --porcelain=v1 --untracked-files=all``.

Code set: files matching INCLUDE_GLOBS or INCLUDE_FILES under the project root, minus any path with a
component in EXCLUDE_DIR_NAMES, ending in EXCLUDE_DIR_SUFFIXES, or with a basename in
EXCLUDE_FILE_NAMES. Data, reports and other outputs are never in the code set, because no include
pattern reaches data/ or reports/. The identity record's own file name is excluded so that writing it
next to a source file cannot change the identity.

Paths are POSIX, relative to the root, Unicode NFC; files are ordered by the UTF-8 bytes of their path.
aggregate_sha256 = SHA-256 of "".join(f"{path}\\t{sha256}\\n" for each file in that order), so it can be
recomputed from the manifest alone (``aggregate_from_files``). The executable bit is recorded per file
and checked by ``verify``, but is not part of the aggregate (the plan's digest formula).

``verify`` recaptures with the record's own include/exclude specification and reports, per path:
changed (content), missing, added, renamed (a missing and an added path with equal SHA-256),
mode_changed, plus git_head_changed and environment_record_changed (each environment record that
changed, is missing now, was absent at capture, or has appeared; never skipped). Changes to the full git status that do not involve code-set paths
(for example new output files) are reported as informational only.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import subprocess
import sys
import unicodedata
from pathlib import Path

SCHEMA = "bio-mb-001/code-identity/v1"
INCLUDE_GLOBS = (
    "src/biomarker_project/**/*.py",
    "scripts/**/*.py",
    "R/**/*.R",
    "tests/**/*.py",
    "config/**/*.yaml",
    "config/**/*.yml",
)
INCLUDE_FILES = ("pyproject.toml", "renv.lock", ".Rprofile", "renv/activate.R", "renv/settings.json")
EXCLUDE_DIR_NAMES = ("__pycache__", ".git")
EXCLUDE_DIR_SUFFIXES = (".egg-info",)
EXCLUDE_FILE_NAMES = ("code_identity.json",)
ENVIRONMENT_RECORDS = (
    "reports/environment/d8_environment_capture/v1/conda_explicit_base.txt",
    "reports/environment/python_lock/v2/requirements.hashes.macos-arm64-cp313.txt",
    "reports/environment/python_lock/v2/manifest.json",
    "renv.lock",
)
RECORD_FILENAME = "code_identity.json"


def _norm(rel: str) -> str:
    return unicodedata.normalize("NFC", rel)


def _excluded(rel: str, spec: dict) -> bool:
    parts = rel.split("/")
    if any(p in spec["exclude_dir_names"] for p in parts[:-1]):
        return True
    if any(p.endswith(tuple(spec["exclude_dir_suffixes"])) for p in parts[:-1]):
        return True
    return parts[-1] in spec["exclude_file_names"]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def default_spec() -> dict:
    return {"include_globs": list(INCLUDE_GLOBS), "include_files": list(INCLUDE_FILES),
            "exclude_dir_names": list(EXCLUDE_DIR_NAMES), "exclude_dir_suffixes": list(EXCLUDE_DIR_SUFFIXES),
            "exclude_file_names": list(EXCLUDE_FILE_NAMES), "environment_records": list(ENVIRONMENT_RECORDS)}


def code_set(root: Path, spec: dict) -> list[str]:
    """Relative POSIX NFC paths of the code set, sorted by UTF-8 bytes. Symlinks are included as links."""
    root = Path(root)
    found: set[str] = set()
    candidates = [p for g in spec["include_globs"] for p in root.glob(g)]
    candidates += [root / f for f in spec["include_files"]]
    for p in candidates:
        if not (p.is_symlink() or p.is_file()):
            continue
        rel = _norm(p.relative_to(root).as_posix())
        if not _excluded(rel, spec):
            found.add(rel)
    return sorted(found, key=lambda s: s.encode("utf-8"))


def _git(root: Path, *args: str) -> bytes | None:
    try:
        out = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout


def _git_states(root: Path) -> tuple[str | None, list[str] | None, dict[str, str], set[str] | None]:
    head = _git(root, "rev-parse", "--verify", "-q", "HEAD")
    head = head.decode().strip() if head else None
    raw = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if raw is None:
        return head, None, {}, None
    entries, states = [], {}
    fields = raw.decode("utf-8", "surrogateescape").split("\0")
    i = 0
    while i < len(fields) and fields[i]:
        xy, path = fields[i][:2], _norm(fields[i][3:])
        entries.append(fields[i])
        if xy[0] in "RC" and i + 1 < len(fields):  # rename/copy: next field is the source path
            entries[-1] += " <- " + fields[i + 1]
            states[_norm(fields[i + 1])] = "renamed_from"
            i += 1
        states[path] = "untracked" if xy == "??" else "ignored" if xy == "!!" else f"changed:{xy}"
        i += 1
    tracked_raw = _git(root, "ls-files", "-z")
    tracked = {_norm(t) for t in tracked_raw.decode("utf-8", "surrogateescape").split("\0") if t} if tracked_raw is not None else None
    return head, entries, states, tracked


def aggregate_from_files(files: list[dict]) -> str:
    ordered = sorted(files, key=lambda f: f["path"].encode("utf-8"))
    return hashlib.sha256("".join(f"{f['path']}\t{f['sha256']}\n" for f in ordered).encode("utf-8")).hexdigest()


def capture(root: Path | str, spec: dict | None = None) -> dict:
    """Identity record for the code set under ``root``. Deterministic for an unchanged tree (no timestamp)."""
    root = Path(root).resolve()
    spec = spec or default_spec()
    head, status, states, tracked = _git_states(root)
    files = []
    for rel in code_set(root, spec):
        p = root / rel
        if p.is_symlink():
            sha, kind, mode_x = hashlib.sha256(os.readlink(p).encode("utf-8")).hexdigest(), "symlink", False
        else:
            sha, kind, mode_x = _sha256_file(p), "file", bool(p.stat().st_mode & 0o111)
        if tracked is None:
            state = "no_git"
        else:
            state = states.get(rel) or ("clean" if rel in tracked else "ignored")
        files.append({"path": rel, "sha256": sha, "kind": kind, "executable": mode_x, "git_state": state})
    env = {}
    for rel in spec["environment_records"]:
        p = root / rel
        env[rel] = _sha256_file(p) if p.is_file() else None
    return {
        "schema": SCHEMA,
        "spec": spec,
        "git_head": head,
        "git_status_porcelain": status,
        "dirty": any(f["git_state"] != "clean" for f in files) if tracked is not None else None,
        "n_files": len(files),
        "files": files,
        "aggregate_sha256": aggregate_from_files(files),
        "aggregate_definition": "sha256 of concatenated 'path<TAB>sha256<LF>' lines, paths sorted by UTF-8 bytes",
        "environment_records": env,
    }


def verify(record: dict, root: Path | str) -> list[dict]:
    """Mismatches between ``record`` and the tree now (empty list = code set identical). Informational
    entries have ``"informational": True`` and do not indicate a code-set difference."""
    now = capture(root, record["spec"])
    out: list[dict] = []
    if aggregate_from_files(record["files"]) != record["aggregate_sha256"]:
        out.append({"type": "record_aggregate_inconsistent"})
    old = {f["path"]: f for f in record["files"]}
    new = {f["path"]: f for f in now["files"]}
    missing = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))
    by_sha_added: dict[str, list[str]] = {}
    for p in added:
        by_sha_added.setdefault(new[p]["sha256"], []).append(p)
    for p in missing:
        cands = by_sha_added.get(old[p]["sha256"])
        if cands:
            q = cands.pop(0)
            added.remove(q)
            out.append({"type": "renamed", "path": p, "to": q})
        else:
            out.append({"type": "missing", "path": p})
    out += [{"type": "added", "path": p} for p in added]
    for p in sorted(set(old) & set(new)):
        if old[p]["sha256"] != new[p]["sha256"] or old[p]["kind"] != new[p]["kind"]:
            out.append({"type": "changed", "path": p})
        elif old[p]["executable"] != new[p]["executable"]:
            out.append({"type": "mode_changed", "path": p})
    # Environment records: every path in the record's spec is compared, fail-closed. A file that was
    # absent at capture, is missing now, has changed or has appeared is a substantive mismatch.
    recorded_env = record.get("environment_records") or {}
    for rel in record["spec"]["environment_records"]:
        was, cur = recorded_env.get(rel), now["environment_records"].get(rel)
        if was is not None and cur == was:
            continue
        reason = ("absent_at_capture" if was is None and cur is None else "appeared" if was is None
                  else "missing_now" if cur is None else "changed")
        out.append({"type": "environment_record_changed", "path": rel, "reason": reason,
                    "recorded": was, "now": cur})
    if record["git_head"] != now["git_head"]:
        out.append({"type": "git_head_changed", "recorded": record["git_head"], "now": now["git_head"]})
    if record["git_status_porcelain"] != now["git_status_porcelain"]:
        # Code-set differences are reported above; the full status also changes when outputs are written.
        out.append({"type": "git_status_changed", "informational": True})
    return out


def write_record(record: dict, path: Path | str) -> str:
    """Write the record as canonical JSON (sorted keys, LF) and return the SHA-256 of the written file."""
    data = (json.dumps(record, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    Path(path).write_bytes(data)
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------------------------------
# Run lifecycle (D8-3 integration; reports/planning/2026-10-18_model_sprint/MODEL_SPRINT_PLAN.md §6)
#
#   1. refuse if out_dir exists (versions are never overwritten); optionally require the .venv interpreter
#      in isolated mode (-I);
#   2. create the sibling staging directory <name>.staging-<run_id>/ (same parent, hence same filesystem);
#   3. capture() and write code_identity.json into staging BEFORE compute() is called;
#   4. compute(staging) returns ({file name: bytes}, manifest dict); the files are written to staging;
#   5. optional equivalence: every returned file named in `equivalent_files` must be byte-identical to the
#      same-named file in `equivalent_to` (for example v2 against v1);
#   6. verify() against the step-3 record, plus the loaded-module check; every mismatch that is not
#      informational fails the run;
#   7. only then is the manifest written (identity SHA-256 and aggregate, verification result, output
#      SHA-256 of every file) and staging is renamed to out_dir with a NO-REPLACE rename (macOS renamex_np
#      RENAME_EXCL; Linux renameat2 RENAME_NOREPLACE). Plain os.rename would silently replace an existing empty
#      directory; the no-replace rename fails with EEXIST if out_dir exists at that instant, even if another
#      process created it concurrently, and the run then fails closed. On any other platform finalization is
#      refused rather than weakened.
# Any failure in steps 3-7 (including exceptions from compute) writes RUN_FAILED.json into the staging
# directory, renames it to <name>.FAILED-<run_id>/ and raises RunFailed. out_dir is created only by the
# final rename, so an interrupted run leaves at most a .staging-* directory, which is never accepted.
#
# Informational vs substantive: only git_status_changed is informational. Writing outputs under reports/
# changes the repository-wide git status but never the code set (no include pattern reaches reports/);
# every code-set, mode, HEAD, environment-record and loaded-module difference is substantive.
#
# Loaded-module check: every module in sys.modules whose file lies under root must be in the code set,
# except files under root/.venv/ (third-party packages; covered by the D8 Python lock, not by code identity).
#
# Executed-code check (optional here, required by the project runners): ``executed_code`` is the registry in
# scripts/_executed_code.py. Its check() proves that the code that executed equals the bytes hashed in the
# identity record: helper modules are compiled from bytes hashed at load time, and the bootstrap modules (the
# runner script and the registry) are compared as code objects against the recorded bytes. A file changed
# after import, even if changed back before capture, therefore fails the run. Its summary is written to the
# manifest (identity_verification.executed_code); acceptance can require it (require_executed_code).
# --------------------------------------------------------------------------------------------------
LIFECYCLE_SCHEMA = "bio-mb-001/run-lifecycle/v1"
FAILED_FILENAME = "RUN_FAILED.json"
RESERVED_NAMES = {RECORD_FILENAME, FAILED_FILENAME}
ENV_DIR_NAMES = (".venv",)


class RunFailed(RuntimeError):
    """A lifecycle run failed; ``failed_dir`` holds the preserved evidence (or is None if nothing was created)."""

    def __init__(self, message: str, failed_dir: Path | None = None, mismatches: list[dict] | None = None):
        super().__init__(message)
        self.failed_dir = failed_dir
        self.mismatches = mismatches or []


def _utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _rename_noreplace(src: Path | str, dst: Path | str) -> None:
    """Rename src to dst, failing with FileExistsError if dst exists (never replaces, even an empty directory)."""
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    s, d = os.fsencode(str(src)), os.fsencode(str(dst))
    if sys.platform == "darwin":
        fn = libc.renamex_np
        fn.argtypes, fn.restype = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint], ctypes.c_int
        rc = fn(s, d, 0x00000004)  # RENAME_EXCL
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        fn = libc.renameat2
        fn.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        fn.restype = ctypes.c_int
        rc = fn(-100, s, -100, d, 1)  # AT_FDCWD, RENAME_NOREPLACE
    else:
        raise OSError(errno.ENOSYS, f"no atomic no-replace rename on {sys.platform}; finalization refused")
    if rc != 0:
        e = ctypes.get_errno()
        if e == errno.EEXIST:
            raise FileExistsError(e, os.strerror(e), str(dst))
        raise OSError(e, os.strerror(e), str(dst))


def interpreter_problems(root: Path | str) -> list[str]:
    """Problems with the running interpreter for a project run (D8-4: .venv/bin/python -I)."""
    root = Path(root).resolve()
    out = []
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        out.append(f"interpreter prefix {sys.prefix} is not {root / '.venv'}")
    if not sys.flags.isolated:
        out.append("interpreter not started in isolated mode (-I)")
    return out


def loaded_module_mismatches(root: Path | str, record: dict) -> tuple[list[dict], dict]:
    """Substantive mismatches for project-root modules outside the record's code set, plus counts."""
    root = Path(root).resolve()
    in_set = {f["path"] for f in record["files"]}
    out, n_project, n_env = [], 0, 0
    for name, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        try:
            rel = _norm(Path(f).resolve().relative_to(root).as_posix())
        except ValueError:
            continue  # not under the project root (standard library or other)
        if rel.split("/")[0] in ENV_DIR_NAMES:
            n_env += 1
            continue
        n_project += 1
        if rel not in in_set:
            out.append({"type": "out_of_set_module", "path": rel, "module": name})
    return out, {"project_modules": n_project, "environment_modules": n_env}


def run_with_identity(root: Path | str, out_dir: Path | str, compute, manifest_extra: dict | None = None, *,
                      manifest_name: str = "manifest.json", equivalent_to: Path | str | None = None,
                      equivalent_files: list[str] | None = None, require_venv: bool = False,
                      spec: dict | None = None, executed_code=None, require_executed_code: bool = False) -> Path:
    """Run ``compute`` under the identity lifecycle described above; return the accepted out_dir."""
    root, out_dir = Path(root).resolve(), Path(out_dir)
    if out_dir.exists():
        raise RunFailed(f"{out_dir} exists; versions are never overwritten")
    if require_venv and (probs := interpreter_problems(root)):
        raise RunFailed("interpreter check failed: " + "; ".join(probs))
    if manifest_name in RESERVED_NAMES:
        raise RunFailed(f"manifest name {manifest_name} is reserved")
    if require_executed_code and (executed_code is None or not executed_code.is_installed()):
        raise RunFailed("executed-code tracking required but not installed (scripts/_executed_code.py)")
    run_id = hashlib.sha256(f"{os.getpid()}-{_utc()}-{os.urandom(8).hex()}".encode()).hexdigest()[:12]
    staging = out_dir.with_name(f"{out_dir.name}.staging-{run_id}")
    started = _utc()
    staging.mkdir(parents=True)

    def fail(message: str, mismatches: list[dict] | None = None, exc: BaseException | None = None):
        evidence = {"schema": LIFECYCLE_SCHEMA, "status": "FAILED", "run_id": run_id, "out_dir": str(out_dir),
                    "started_utc": started, "failed_utc": _utc(), "reason": message, "mismatches": mismatches or [],
                    "exception": None if exc is None else f"{type(exc).__name__}: {exc}"}
        (staging / FAILED_FILENAME).write_text(json.dumps(evidence, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        failed_dir = out_dir.with_name(f"{out_dir.name}.FAILED-{run_id}")
        _rename_noreplace(staging, failed_dir)
        err = RunFailed(f"{message} (evidence: {failed_dir})", failed_dir, mismatches)
        err.lifecycle_handled = True
        raise err from exc

    try:
        record = capture(root, spec)
        record_sha = write_record(record, staging / RECORD_FILENAME)
        files, body = compute(staging)
        bad = [n for n in files if "/" in n or n in RESERVED_NAMES or n == manifest_name or n.startswith(".")]
        if bad:
            fail(f"compute returned reserved or nested file names: {bad}")
        for n, b in files.items():
            (staging / n).write_bytes(b)
        equivalence = None
        if equivalent_to is not None:
            ref = Path(equivalent_to)
            names = list(equivalent_files if equivalent_files is not None else files)
            tables, problems = {}, []
            for n in names:
                rf = ref / n
                if n not in files:
                    problems.append({"type": "equivalence_file_not_produced", "path": n})
                    continue
                if not rf.is_file():
                    problems.append({"type": "equivalence_reference_missing", "path": str(rf)})
                    continue
                same = rf.read_bytes() == files[n]
                tables[n] = {"identical": same, "sha256": _sha256_bytes(files[n]), "reference_sha256": _sha256_file(rf)}
                if not same:
                    problems.append({"type": "not_byte_identical_to_reference", "path": n})
            equivalence = {"reference": str(ref.resolve().relative_to(root)) if ref.resolve().is_relative_to(root) else str(ref),
                           "tables": tables, "identical": not problems and bool(tables)}
            if problems or not tables:
                fail("equivalence check failed", problems or [{"type": "no_equivalence_files"}])
        mismatches = verify(record, root)
        mod_mismatches, mod_counts = loaded_module_mismatches(root, record)
        exec_mismatches = executed_code.check(record, root) if executed_code is not None else []
        substantive = [m for m in mismatches + mod_mismatches + exec_mismatches if not m.get("informational")]
        if substantive:
            fail("post-run identity verification failed", substantive)
        clash = set(body) & {"lifecycle", "identity", "identity_verification", "equivalence", "output_sha256"}
        if clash or (manifest_extra and set(manifest_extra) & {"lifecycle", "identity", "identity_verification",
                                                                "equivalence", "output_sha256"}):
            fail(f"manifest keys reserved by the lifecycle: {sorted(clash)}")
        manifest = {**(manifest_extra or {}), **body,
                    "lifecycle": {"schema": LIFECYCLE_SCHEMA, "run_id": run_id, "started_utc": started,
                                  "finalized_utc": _utc(), "out_dir": out_dir.name,
                                  "interpreter": {"executable": sys.executable, "prefix": sys.prefix,
                                                  "isolated": bool(sys.flags.isolated), "version": sys.version}},
                    "identity": {"record_file": RECORD_FILENAME, "record_sha256": record_sha,
                                 "aggregate_sha256": record["aggregate_sha256"], "n_files": record["n_files"],
                                 "git_head": record["git_head"], "dirty": record["dirty"],
                                 "environment_records": record["environment_records"]},
                    "identity_verification": {"status": "PASS", "verified_utc": _utc(),
                                              "informational": [m for m in mismatches if m.get("informational")],
                                              **mod_counts,
                                              "executed_code": ({k: v for k, v in executed_code.summary().items()}
                                                                if executed_code is not None else {"tracked": False})},
                    "equivalence": equivalence,
                    "output_sha256": {**{n: _sha256_bytes(b) for n, b in files.items()}, RECORD_FILENAME: record_sha}}
        (staging / manifest_name).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if out_dir.exists():
            fail(f"{out_dir} appeared during the run; not overwritten")
        try:
            _rename_noreplace(staging, out_dir)
        except FileExistsError:
            fail(f"{out_dir} was created concurrently; not overwritten")
        return out_dir
    except RunFailed as e:
        if getattr(e, "lifecycle_handled", False) or not staging.exists():
            raise
        fail("computation raised RunFailed", exc=e)
    except BaseException as exc:  # includes KeyboardInterrupt: evidence is preserved, then re-raised as RunFailed
        if staging.exists():
            fail("computation raised an exception", exc=exc)
        raise


def acceptance_problems(d: Path | str, manifest_name: str = "manifest.json", require_equivalence: bool = False,
                        require_executed_code: bool = False) -> list[str]:
    """Reasons why directory ``d`` is not an accepted lifecycle output (empty list = accepted)."""
    d = Path(d)
    if not d.is_dir():
        return [f"{d} is not a directory"]
    probs = []
    if ".staging-" in d.name or ".FAILED-" in d.name:
        probs.append("staging or failed directory")
    if (d / FAILED_FILENAME).exists():
        probs.append(f"{FAILED_FILENAME} present")
    mp, rp = d / manifest_name, d / RECORD_FILENAME
    if not mp.is_file() or not rp.is_file():
        return probs + ["manifest or identity record missing"]
    try:
        m = json.loads(mp.read_text(encoding="utf-8"))
        rec = json.loads(rp.read_text(encoding="utf-8"))
    except ValueError:
        return probs + ["manifest or identity record is not valid JSON"]
    if (m.get("lifecycle") or {}).get("schema") != LIFECYCLE_SCHEMA:
        probs.append("manifest lacks the lifecycle schema")
    ident = m.get("identity") or {}
    if ident.get("record_sha256") != _sha256_file(rp):
        probs.append("identity record SHA-256 differs from the manifest")
    if not (rec.get("aggregate_sha256") == ident.get("aggregate_sha256") == aggregate_from_files(rec.get("files", []))):
        probs.append("identity aggregate inconsistent")
    if (m.get("identity_verification") or {}).get("status") != "PASS":
        probs.append("identity verification did not pass")
    if require_executed_code and ((m.get("identity_verification") or {}).get("executed_code") or {}).get("tracked") is not True:
        probs.append("executed-code verification not recorded")
    outs = m.get("output_sha256") or {}
    present = {p.name for p in d.iterdir()} - {manifest_name}
    if present != set(outs):
        probs.append(f"files differ from the manifest: extra {sorted(present - set(outs))}, missing {sorted(set(outs) - present)}")
    for n, h in outs.items():
        if (d / n).is_file() and _sha256_file(d / n) != h:
            probs.append(f"{n}: SHA-256 differs from the manifest")
    eq = m.get("equivalence")
    if require_equivalence and not (eq and eq.get("identical") is True):
        probs.append("byte-identical equivalence to the reference version not established")
    return probs


def is_accepted(d: Path | str, manifest_name: str = "manifest.json", require_equivalence: bool = False,
                require_executed_code: bool = False) -> bool:
    return not acceptance_problems(d, manifest_name, require_equivalence, require_executed_code)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("--root", default=".")
    c.add_argument("--out", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--root", default=".")
    v.add_argument("--record", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "capture":
        print(write_record(capture(a.root), a.out))
        return 0
    mismatches = verify(json.loads(Path(a.record).read_text(encoding="utf-8")), a.root)
    print(json.dumps(mismatches, indent=1))
    return 1 if any(not m.get("informational") for m in mismatches) else 0


if __name__ == "__main__":
    sys.exit(main())
