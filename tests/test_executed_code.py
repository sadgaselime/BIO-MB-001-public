"""Executed-code registry (synthetic, real mechanism): each scenario runs a synthetic runner in a fresh
``.venv`` interpreter (-I -B) inside a temporary git repository holding copies of the real
scripts/_executed_code.py and src/biomarker_project/code_identity.py. No project data are read.
"""
from __future__ import annotations

import json
import os
import py_compile
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from test_run_identity_lifecycle import git, make_repo

PROJECT = Path(__file__).resolve().parents[1]

RUNNER = textwrap.dedent('''
    from __future__ import annotations
    import importlib.util
    import json
    import sys
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    ACTION = sys.argv[1]
    if ACTION == "preload":  # a project module loaded BEFORE the registry is installed
        _s = importlib.util.spec_from_file_location("preloaded", ROOT / "src/biomarker_project/helper2.py")
        _m = importlib.util.module_from_spec(_s); sys.modules["preloaded"] = _m; _s.loader.exec_module(_m)
    _MAIN_CODE = sys._getframe(0).f_code


    def _executed_code_registry():
        name = "bio_mb_001_executed_code"
        if name not in sys.modules:
            spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/_executed_code.py")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        return sys.modules[name]


    _ec = _executed_code_registry()
    if __name__ == "__main__":
        _ec.install(ROOT, _MAIN_CODE, __file__)
    sys.path.insert(0, str(ROOT / "src"))
    from biomarker_project import helper  # noqa: E402  (through the hashing loader)
    from biomarker_project import code_identity as ci  # noqa: E402
    # actions after import and BEFORE identity capture (the window the registry must close)
    if ACTION in ("revert_helper", "revert_self", "change_registry"):
        target, content = Path(sys.argv[2]), Path(sys.argv[3]).read_bytes()
        target.write_bytes(content)


    def compute(staging):
        return {"out.tsv": helper.VALUE.encode()}, {"status": "synthetic"}


    try:
        out = ci.run_with_identity(ROOT, ROOT / "reports/out/v1", compute, executed_code=_ec, require_executed_code=True)
    except ci.RunFailed as e:
        print(json.dumps({"failed": True, "mismatches": e.mismatches, "value": helper.VALUE}))
        raise SystemExit(1)
    print(json.dumps({"accepted": str(out), "value": helper.VALUE}))
''')


@pytest.fixture
def repo(tmp_path):
    root = make_repo(tmp_path / "repo")
    (root / "scripts").mkdir(exist_ok=True)
    shutil.copy(PROJECT / "scripts/_executed_code.py", root / "scripts/_executed_code.py")
    shutil.copy(PROJECT / "src/biomarker_project/code_identity.py", root / "src/biomarker_project/code_identity.py")
    (root / "src/biomarker_project/__init__.py").write_text('"""synthetic package"""\n')
    (root / "src/biomarker_project/helper.py").write_text("VALUE = 'o'\n")
    (root / "src/biomarker_project/helper2.py").write_text("W = 2\n")
    (root / "scripts/runner.py").write_text(RUNNER)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "synthetic runner")
    return root


def launch(repo, *args):
    r = subprocess.run([sys.executable, "-I", "-B", str(repo / "scripts/runner.py"), *map(str, args)],
                       capture_output=True, text=True, cwd=repo)
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    assert lines, r.stderr
    return r.returncode, json.loads(lines[-1])


def types(result):
    return {m["type"] for m in result.get("mismatches", [])}


def test_clean_run_records_executed_and_bootstrap_code(repo):
    code, res = launch(repo, "none")
    assert code == 0, res
    m = json.loads((Path(res["accepted"]) / "manifest.json").read_text())
    ec = m["identity_verification"]["executed_code"]
    assert ec["tracked"] is True
    assert set(ec["bootstrap"]) == {"scripts/runner.py", "scripts/_executed_code.py"}
    assert {"src/biomarker_project/helper.py", "src/biomarker_project/code_identity.py",
            "src/biomarker_project/__init__.py"} <= set(ec["executed"])
    files = {f["path"]: f["sha256"] for f in json.loads((Path(res["accepted"]) / "code_identity.json").read_text())["files"]}
    assert all(files[p] == h for p, h in ec["executed"].items())


def test_helper_changed_before_import_and_reverted_before_capture_fails(repo, tmp_path):
    helper = repo / "src/biomarker_project/helper.py"
    original = tmp_path / "helper_original.py"
    original.write_bytes(helper.read_bytes())
    helper.write_text("VALUE = 'x'\n")  # the code that will execute
    code, res = launch(repo, "revert_helper", helper, original)  # file restored after import, before capture
    assert code == 1 and res["value"] == "x"
    assert any(m["type"] == "executed_code_differs" and m["path"] == "src/biomarker_project/helper.py"
               for m in res["mismatches"])
    assert not (repo / "reports/out/v1").exists()


def test_runner_script_changed_after_start_fails(repo, tmp_path):
    runner = repo / "scripts/runner.py"
    committed = tmp_path / "runner_committed.py"
    committed.write_bytes(runner.read_bytes())
    runner.write_text(RUNNER.replace('{"status": "synthetic"}', '{"status": "synthetic", "variant": 1}'))
    code, res = launch(repo, "revert_self", runner, committed)  # restored to the committed bytes before capture
    assert code == 1
    assert any(m["type"] == "executed_code_differs" and m["path"] == "scripts/runner.py" for m in res["mismatches"])


def test_registry_changed_after_load_fails(repo, tmp_path):
    reg = repo / "scripts/_executed_code.py"
    changed = tmp_path / "registry_changed.py"
    changed.write_text(reg.read_text() + "\n\ndef _added_after_load():\n    return 1\n")
    code, res = launch(repo, "change_registry", reg, changed)
    assert code == 1
    assert any(m["type"] == "executed_code_differs" and m["path"] == "scripts/_executed_code.py" for m in res["mismatches"])


def test_module_loaded_before_install_is_unverified(repo):
    code, res = launch(repo, "preload")
    assert code == 1
    assert any(m["type"] == "unverified_loaded_module" and m["path"] == "src/biomarker_project/helper2.py"
               for m in res["mismatches"])


def test_stale_bytecode_is_never_executed_for_project_modules(repo):
    helper = repo / "src/biomarker_project/helper.py"
    helper.write_text("VALUE = 'y'\n")  # same length as the committed "VALUE = 'o'\n"
    py_compile.compile(str(helper), invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
    st = helper.stat()
    helper.write_text("VALUE = 'o'\n")  # source back to the committed bytes ...
    os.utime(helper, ns=(st.st_atime_ns, st.st_mtime_ns))  # ... with the stale cache's mtime and size
    code, res = launch(repo, "none")
    assert code == 0 and res["value"] == "o"  # compiled from the hashed source, not from the stale cache
