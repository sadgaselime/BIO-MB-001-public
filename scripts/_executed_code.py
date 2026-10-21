"""Executed-code registry (D8-3 hardening): ties a run's identity record to the code that actually executes.

Problem: a runner's own file and its project helpers are loaded before the identity record is captured, so a
file changed after import (and possibly changed back) could execute code that the record never hashed.

Mechanism (enforced, not assumed):
  * Bootstrap modules: the runner script (__main__) and this registry are loaded before any hook can exist.
    Each records its own module code object at load time (``sys._getframe(0).f_code``). ``check`` recompiles
    the file bytes whose SHA-256 is in the identity record and requires the result to equal the code object
    that executed (code-object equality: bytecode, constants, names, nested code, line table).
  * Every other project module: ``install`` replaces ``SourceFileLoader.get_code`` so that, for files under the
    project root (outside .venv/), the loader reads the bytes once, records their SHA-256 and compiles exactly
    those bytes (no bytecode cache is read or written). ``check`` requires each executed SHA-256 to equal the
    identity record's SHA-256 for that path.
  * Any project-root module present in sys.modules that is neither a bootstrap module nor loaded through the
    hook (for example loaded before ``install``) is reported as unverified.
Every reported mismatch is substantive. Files under root/.venv/ are third-party packages covered by the D8
Python lock, not by code identity, and are not tracked here.

Scope limit (stated, not hidden): the check compares code objects and source bytes. It cannot detect code that
was changed in memory after loading (for example by monkeypatching), and it trusts the interpreter itself.
"""
import hashlib
import importlib.machinery
import sys
import unicodedata
from pathlib import Path

_SELF_CODE = sys._getframe(0).f_code
_ENV_DIR_NAMES = (".venv",)
_STATE = {"root": None, "installed": False, "executed": {}, "bootstrap": {}}


def _project_rel(path) -> str | None:
    root = _STATE["root"]
    try:
        rel = Path(path).resolve().relative_to(root).as_posix()
    except (ValueError, TypeError, OSError):
        return None
    rel = unicodedata.normalize("NFC", rel)
    return None if rel.split("/")[0] in _ENV_DIR_NAMES else rel


def is_installed() -> bool:
    return _STATE["installed"]


def install(root, main_code, main_file) -> None:
    """Register the bootstrap code objects and install the hashing loader (once per process)."""
    if _STATE["installed"]:
        raise RuntimeError("executed-code registry already installed")
    _STATE["root"] = Path(root).resolve()
    for code, f in ((_SELF_CODE, __file__), (main_code, main_file)):
        rel = _project_rel(f)
        if rel is None:
            raise RuntimeError(f"bootstrap file {f} is not under the project root")
        _STATE["bootstrap"][rel] = code
    original = importlib.machinery.SourceFileLoader.get_code

    def get_code(self, fullname):
        path = self.get_filename(fullname)
        rel = _project_rel(path)
        if rel is None:
            return original(self, fullname)
        data = self.get_data(path)
        _STATE["executed"][rel] = hashlib.sha256(data).hexdigest()
        return compile(data, path, "exec", dont_inherit=True)

    importlib.machinery.SourceFileLoader.get_code = get_code
    _STATE["installed"] = True


def summary() -> dict:
    return {"tracked": _STATE["installed"], "executed_files": len(_STATE["executed"]),
            "bootstrap_files": len(_STATE["bootstrap"]),
            "executed": dict(sorted(_STATE["executed"].items())), "bootstrap": sorted(_STATE["bootstrap"])}


def check(record: dict, root=None) -> list[dict]:
    """Substantive mismatches between the code that executed and ``record`` (an identity record)."""
    if not _STATE["installed"]:
        return [{"type": "executed_code_not_tracked"}]
    root = _STATE["root"]
    recorded = {f["path"]: f["sha256"] for f in record["files"]}
    out = []
    for rel, sha in sorted(_STATE["executed"].items()):
        if rel not in recorded:
            out.append({"type": "out_of_set_module", "path": rel, "how": "executed through the hashing loader"})
        elif sha != recorded[rel]:
            out.append({"type": "executed_code_differs", "path": rel, "executed_sha256": sha, "recorded_sha256": recorded[rel]})
    for rel, code in sorted(_STATE["bootstrap"].items()):
        if rel not in recorded:
            out.append({"type": "out_of_set_module", "path": rel, "how": "bootstrap"})
            continue
        data = (root / rel).read_bytes()
        if hashlib.sha256(data).hexdigest() != recorded[rel]:
            out.append({"type": "executed_code_differs", "path": rel, "how": "bootstrap file differs from the record now"})
        elif compile(data, code.co_filename, "exec", dont_inherit=True) != code:
            out.append({"type": "executed_code_differs", "path": rel, "how": "bootstrap code object differs from the recorded bytes"})
    known = set(_STATE["executed"]) | set(_STATE["bootstrap"])
    for name, mod in sorted(sys.modules.items()):
        rel = _project_rel(getattr(mod, "__file__", None)) if getattr(mod, "__file__", None) else None
        if rel is not None and rel not in known:
            out.append({"type": "unverified_loaded_module", "path": rel, "module": name})
    return out
