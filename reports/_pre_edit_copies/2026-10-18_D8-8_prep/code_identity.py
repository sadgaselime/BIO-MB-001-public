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
mode_changed, plus git_head_changed. Changes to the full git status that do not involve code-set paths
(for example new output files) are reported as informational only.
"""
from __future__ import annotations

import argparse
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
