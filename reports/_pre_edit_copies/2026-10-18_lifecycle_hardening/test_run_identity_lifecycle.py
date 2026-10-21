"""Run lifecycle (synthetic): temporary git repositories, fake source files and fake outputs only."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from biomarker_project import code_identity as ci

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
ENV = list(ci.ENVIRONMENT_RECORDS)


def git(root, *args):
    subprocess.run([*GIT, "-C", str(root), *args], check=True, capture_output=True)


def make_repo(root: Path) -> Path:
    files = {
        "src/biomarker_project/a.py": "A = 1\n",
        "scripts/run.py": "print('x')\n",
        "R/fit.R": "x <- 1\n",
        "tests/test_a.py": "def test(): pass\n",
        "config/c.yaml": "k: v\n",
        "pyproject.toml": "[project]\nname='t'\n",
        "renv.lock": "{}\n",
        ENV[0]: "@EXPLICIT\n", ENV[1]: "x==1\n", ENV[2]: "{}\n",
    }
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "init")
    return root


@pytest.fixture
def repo(tmp_path):
    return make_repo(tmp_path / "repo")


def ok_compute(staging):
    return {"table.tsv": b"a\tb\n1\t2\n"}, {"status": "synthetic"}


def run(repo, compute=ok_compute, version="v1", **kw):
    return ci.run_with_identity(repo, repo / "reports/out" / version, compute, {"purpose": "test"}, **kw)


def leftovers(repo):
    return sorted(p.name for p in (repo / "reports/out").iterdir()) if (repo / "reports/out").exists() else []


def test_capture_happens_before_compute(repo):
    seen = {}

    def compute(staging):
        rec = json.loads((staging / ci.RECORD_FILENAME).read_text())
        seen["aggregate"] = rec["aggregate_sha256"]
        seen["manifest_absent"] = not (staging / "manifest.json").exists()
        return ok_compute(staging)

    out = run(repo, compute)
    assert seen["manifest_absent"] and seen["aggregate"] == ci.capture(repo)["aggregate_sha256"]
    assert json.loads((out / "manifest.json").read_text())["identity"]["aggregate_sha256"] == seen["aggregate"]


def test_success_manifest_linkage_and_atomic_finalization(repo):
    out = run(repo)
    m = json.loads((out / "manifest.json").read_text())
    rec_bytes = (out / ci.RECORD_FILENAME).read_bytes()
    assert m["identity"]["record_sha256"] == hashlib.sha256(rec_bytes).hexdigest()
    assert m["identity"]["aggregate_sha256"] == json.loads(rec_bytes)["aggregate_sha256"]
    assert m["output_sha256"]["table.tsv"] == hashlib.sha256(b"a\tb\n1\t2\n").hexdigest()
    assert m["identity_verification"]["status"] == "PASS"
    assert {i["type"] for i in m["identity_verification"]["informational"]} <= {"git_status_changed"}
    assert m["purpose"] == "test" and m["status"] == "synthetic"
    assert leftovers(repo) == ["v1"]  # no staging or failed directory remains
    assert ci.is_accepted(out) and ci.acceptance_problems(out) == []


def _change_code(repo):
    (repo / "scripts/run.py").write_text("print('changed')\n")


def _add_file(repo):
    (repo / "src/biomarker_project/new.py").write_text("N = 1\n")


def _remove_file(repo):
    (repo / "R/fit.R").unlink()


def _rename_file(repo):
    (repo / "src/biomarker_project/a.py").rename(repo / "src/biomarker_project/b.py")


def _chmod(repo):
    os.chmod(repo / "scripts/run.py", 0o755)


def _commit(repo):
    (repo / "README.md").write_text("outside the code set\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-q", "-m", "head moves")


def _env(repo):
    (repo / ENV[1]).write_text("x==2\n")


@pytest.mark.parametrize("mutate,expected", [
    (_change_code, "changed"), (_add_file, "added"), (_remove_file, "missing"), (_rename_file, "renamed"),
    (_chmod, "mode_changed"), (_commit, "git_head_changed"), (_env, "environment_record_changed"),
])
def test_substantive_mismatch_during_compute_fails_closed(repo, mutate, expected):
    def compute(staging):
        mutate(repo)
        return ok_compute(staging)

    with pytest.raises(ci.RunFailed) as e:
        run(repo, compute)
    assert not (repo / "reports/out/v1").exists()
    failed = e.value.failed_dir
    assert failed.name.startswith("v1.FAILED-") and failed.is_dir()
    ev = json.loads((failed / ci.FAILED_FILENAME).read_text())
    assert ev["status"] == "FAILED" and expected in {m["type"] for m in ev["mismatches"]}
    assert all(not m.get("informational") for m in ev["mismatches"])
    assert not ci.is_accepted(failed)


def test_output_only_changes_are_informational_and_accepted(repo):
    def compute(staging):
        (repo / "reports/side_note.txt").write_text("generated elsewhere under reports/\n")
        return ok_compute(staging)

    out = run(repo, compute)
    info = json.loads((out / "manifest.json").read_text())["identity_verification"]["informational"]
    assert [i["type"] for i in info] == ["git_status_changed"] and ci.is_accepted(out)


def test_compute_exception_preserves_failure_evidence(repo):
    def compute(staging):
        raise SystemExit("STOP — INPUT VERIFICATION FAILED: synthetic")

    with pytest.raises(ci.RunFailed) as e:
        run(repo, compute)
    ev = json.loads((e.value.failed_dir / ci.FAILED_FILENAME).read_text())
    assert "SystemExit" in ev["exception"] and (e.value.failed_dir / ci.RECORD_FILENAME).exists()
    assert not (repo / "reports/out/v1").exists() and not ci.is_accepted(e.value.failed_dir)


def test_interrupted_run_leaves_only_rejected_staging(repo):
    src = Path(ci.__file__).resolve().parents[1]
    code = textwrap.dedent(f"""
        import os, sys
        sys.path.insert(0, {str(src)!r})
        from biomarker_project import code_identity as ci
        def compute(staging):
            (staging / "partial.tsv").write_bytes(b"half")
            os._exit(9)  # simulated hard interruption: no cleanup runs
        ci.run_with_identity({str(repo)!r}, {str(repo / 'reports/out/v1')!r}, compute)
    """)
    r = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True)
    assert r.returncode == 9
    names = leftovers(repo)
    assert len(names) == 1 and names[0].startswith("v1.staging-") and not (repo / "reports/out/v1").exists()
    assert not ci.is_accepted(repo / "reports/out" / names[0])


def test_staging_renamed_to_final_name_is_still_rejected_without_complete_manifest(repo):
    d = repo / "reports/out/v1"
    d.mkdir(parents=True)
    ci.write_record(ci.capture(repo), d / ci.RECORD_FILENAME)
    (d / "table.tsv").write_bytes(b"x")
    assert "manifest or identity record missing" in ci.acceptance_problems(d)


def test_tampered_output_is_rejected(repo):
    out = run(repo)
    (out / "table.tsv").write_bytes(b"tampered\n")
    assert any("SHA-256 differs" in p for p in ci.acceptance_problems(out))
    (out / "table.tsv").write_bytes(b"a\tb\n1\t2\n")
    (out / "extra.tsv").write_bytes(b"x")
    assert any("files differ from the manifest" in p for p in ci.acceptance_problems(out))


def test_out_of_set_project_module_is_detected(repo):
    helper = repo / "notes" / "helper_out_of_set.py"
    helper.parent.mkdir()
    helper.write_text("VALUE = 3\n")
    name = "helper_out_of_set_synthetic"

    def compute(staging):
        spec = importlib.util.spec_from_file_location(name, helper)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return ok_compute(staging)

    try:
        with pytest.raises(ci.RunFailed) as e:
            run(repo, compute)
    finally:
        sys.modules.pop(name, None)
    assert {"type": "out_of_set_module", "path": "notes/helper_out_of_set.py", "module": name} in e.value.mismatches


def test_in_set_and_environment_modules_are_allowed(repo):
    venv_mod = repo / ".venv/lib/site/thirdparty_synthetic.py"
    venv_mod.parent.mkdir(parents=True)
    venv_mod.write_text("T = 1\n")
    names = ["inset_synthetic", "thirdparty_synthetic"]

    def compute(staging):
        for n, p in zip(names, [repo / "src/biomarker_project/a.py", venv_mod]):
            spec = importlib.util.spec_from_file_location(n, p)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[n] = mod
            spec.loader.exec_module(mod)
        return ok_compute(staging)

    try:
        out = run(repo, compute)
    finally:
        for n in names:
            sys.modules.pop(n, None)
    v = json.loads((out / "manifest.json").read_text())["identity_verification"]
    assert v["project_modules"] >= 1 and v["environment_modules"] >= 1


def test_refuses_existing_version_before_capture(repo):
    (repo / "reports/out/v1").mkdir(parents=True)
    with pytest.raises(ci.RunFailed, match="never overwritten"):
        run(repo)
    assert leftovers(repo) == ["v1"]


def test_v1_v2_byte_identical_equivalence(repo):
    v1 = run(repo, version="v1")
    v2 = run(repo, version="v2", equivalent_to=v1, equivalent_files=["table.tsv"])
    eq = json.loads((v2 / "manifest.json").read_text())["equivalence"]
    assert eq["identical"] is True and eq["reference"] == "reports/out/v1"
    assert eq["tables"]["table.tsv"]["sha256"] == eq["tables"]["table.tsv"]["reference_sha256"]
    assert ci.is_accepted(v2, require_equivalence=True) and not ci.is_accepted(v1, require_equivalence=True)


def test_v2_not_identical_to_v1_fails(repo):
    v1 = run(repo, version="v1")
    with pytest.raises(ci.RunFailed) as e:
        run(repo, lambda s: ({"table.tsv": b"different\n"}, {}), version="v2", equivalent_to=v1, equivalent_files=["table.tsv"])
    assert e.value.mismatches == [{"type": "not_byte_identical_to_reference", "path": "table.tsv"}]
    assert not (repo / "reports/out/v2").exists()


def test_missing_equivalence_reference_fails(repo):
    with pytest.raises(ci.RunFailed) as e:
        run(repo, version="v2", equivalent_to=repo / "reports/out/v1", equivalent_files=["table.tsv"])
    assert e.value.mismatches[0]["type"] == "equivalence_reference_missing"


def test_interpreter_check_refuses_before_anything_is_created(repo):
    assert ci.interpreter_problems(repo)  # this tmp repo has no .venv
    with pytest.raises(ci.RunFailed, match="interpreter check failed"):
        run(repo, require_venv=True)
    assert leftovers(repo) == []


def test_reserved_names_and_keys_fail(repo):
    with pytest.raises(ci.RunFailed):
        run(repo, lambda s: ({ci.RECORD_FILENAME: b"x"}, {}))
    with pytest.raises(ci.RunFailed):
        run(repo, lambda s: ({"t.tsv": b"x"}, {"identity": "forged"}), version="v2")
