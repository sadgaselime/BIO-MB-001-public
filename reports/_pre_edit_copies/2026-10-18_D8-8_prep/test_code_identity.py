"""Source-tree identity (synthetic): temporary git repositories with fake source files only."""
from __future__ import annotations

import hashlib
import os
import subprocess
import unicodedata

import pytest

from biomarker_project import code_identity as ci

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]


def git(root, *args):
    subprocess.run([*GIT, "-C", str(root), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    files = {
        "src/biomarker_project/a.py": "A = 1\n",
        "src/biomarker_project/sub/b.py": "B = 2\n",
        "scripts/run.py": "print('x')\n",
        "R/fit.R": "x <- 1\n",
        "tests/test_a.py": "def test(): pass\n",
        "config/c.yaml": "k: v\n",
        "pyproject.toml": "[project]\nname='t'\n",
        "renv.lock": "{}\n",
    }
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def codes(mismatches):
    return [(m["type"], m.get("path")) for m in mismatches if not m.get("informational")]


def test_unchanged_tree_is_deterministic_and_verifies(repo):
    r1, r2 = ci.capture(repo), ci.capture(repo)
    assert r1 == r2
    assert r1["n_files"] == 8 and r1["dirty"] is False
    assert {f["git_state"] for f in r1["files"]} == {"clean"}
    assert r1["git_head"] and r1["git_status_porcelain"] == []
    assert ci.verify(r1, repo) == []
    out1, out2 = repo.parent / "r1.json", repo.parent / "r2.json"
    assert ci.write_record(r1, out1) == ci.write_record(r2, out2)


def test_aggregate_reproducible_from_manifest(repo):
    r = ci.capture(repo)
    text = "".join(f"{f['path']}\t{f['sha256']}\n" for f in r["files"])
    assert hashlib.sha256(text.encode()).hexdigest() == r["aggregate_sha256"] == ci.aggregate_from_files(r["files"])
    for f in r["files"]:
        assert hashlib.sha256((repo / f["path"]).read_bytes()).hexdigest() == f["sha256"]


def test_changed_file(repo):
    r = ci.capture(repo)
    (repo / "scripts/run.py").write_text("print('y')\n")
    assert codes(ci.verify(r, repo)) == [("changed", "scripts/run.py")]
    r2 = ci.capture(repo)
    assert r2["aggregate_sha256"] != r["aggregate_sha256"] and r2["dirty"] is True
    assert next(f for f in r2["files"] if f["path"] == "scripts/run.py")["git_state"] == "changed: M"


def test_added_untracked_file_is_hashed(repo):
    r = ci.capture(repo)
    (repo / "src/biomarker_project/new.py").write_text("N = 3\n")
    assert codes(ci.verify(r, repo)) == [("added", "src/biomarker_project/new.py")]
    r2 = ci.capture(repo)
    assert next(f for f in r2["files"] if f["path"] == "src/biomarker_project/new.py")["git_state"] == "untracked"
    assert "?? src/biomarker_project/new.py" in r2["git_status_porcelain"]


def test_removed_and_renamed_files(repo):
    r = ci.capture(repo)
    (repo / "R/fit.R").unlink()
    (repo / "src/biomarker_project/sub/b.py").rename(repo / "src/biomarker_project/sub/c.py")
    assert codes(ci.verify(r, repo)) == [("missing", "R/fit.R"), ("renamed", "src/biomarker_project/sub/b.py")]
    ren = next(m for m in ci.verify(r, repo) if m["type"] == "renamed")
    assert ren["to"] == "src/biomarker_project/sub/c.py"


def test_mode_change_detected_but_not_in_aggregate(repo):
    r = ci.capture(repo)
    os.chmod(repo / "scripts/run.py", 0o755)
    assert codes(ci.verify(r, repo)) == [("mode_changed", "scripts/run.py")]
    assert ci.capture(repo)["aggregate_sha256"] == r["aggregate_sha256"]


def test_exclusions_and_out_of_scope_paths(repo):
    r = ci.capture(repo)
    extra = [
        "src/biomarker_project/__pycache__/a.cpython-313.pyc",
        "src/biomarker_project/__pycache__/x.py",
        "src/biomarker_project.egg-info/x.py",
        "src/biomarker_project/code_identity.json",
        "reports/out/result.py",
        "data/raw/GSE0/x.py",
        "src/biomarker_project/notes.txt",
    ]
    for rel in extra:
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("z\n")
    assert codes(ci.verify(r, repo)) == []
    assert [m["type"] for m in ci.verify(r, repo)] == ["git_status_changed"]  # informational only
    assert ci.capture(repo)["aggregate_sha256"] == r["aggregate_sha256"]


def test_paths_are_posix_relative_nfc_and_byte_ordered(repo):
    nfd = unicodedata.normalize("NFD", "src/biomarker_project/é.py")
    (repo / nfd).write_text("E = 5\n")
    (repo / "src/biomarker_project/B.py").write_text("B = 0\n")
    paths = [f["path"] for f in ci.capture(repo)["files"]]
    assert "src/biomarker_project/é.py" in paths  # NFC
    assert all(not p.startswith("/") and "\\" not in p for p in paths)
    assert paths == sorted(paths, key=lambda s: s.encode("utf-8"))


def test_record_tampering_and_head_change(repo):
    r = ci.capture(repo)
    bad = dict(r, aggregate_sha256="0" * 64)
    assert ("record_aggregate_inconsistent", None) in codes(ci.verify(bad, repo))
    (repo / "renv.lock").write_text('{"x": 1}\n')
    git(repo, "commit", "-q", "-am", "second")
    found = codes(ci.verify(r, repo))
    assert ("changed", "renv.lock") in found and ("git_head_changed", None) in found


def test_environment_records_and_non_git_tree(tmp_path):
    (tmp_path / "src/biomarker_project").mkdir(parents=True)
    (tmp_path / "src/biomarker_project/a.py").write_text("A = 1\n")
    (tmp_path / "renv.lock").write_text("{}\n")
    r = ci.capture(tmp_path)
    assert r["git_head"] is None and r["git_status_porcelain"] is None and r["dirty"] is None
    assert {f["git_state"] for f in r["files"]} == {"no_git"}
    assert r["environment_records"]["renv.lock"] == hashlib.sha256(b"{}\n").hexdigest()
    assert r["environment_records"]["reports/environment/python_lock/v2/manifest.json"] is None
