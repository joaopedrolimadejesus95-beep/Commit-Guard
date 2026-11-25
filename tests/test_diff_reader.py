import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from diff_reader import (
    EMPTY_TREE_HASH,
    get_changed_files,
    get_diff_for_file,
    resolver_base_ref,
    rodar_git,
)


def _git(repo_path, *args):
    subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(tmp_path):
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    return tmp_path


def test_resolver_base_ref_fallback_on_empty_or_missing(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "app.py").write_text("print('v1')\n", encoding="utf-8")
    _git(tmp_path, "add", "app.py")
    _git(tmp_path, "commit", "-m", "initial commit")

    assert resolver_base_ref(tmp_path, "") == EMPTY_TREE_HASH
    assert resolver_base_ref(tmp_path, "0" * 40) == EMPTY_TREE_HASH
    assert resolver_base_ref(tmp_path, "HEAD~1") == EMPTY_TREE_HASH
    assert resolver_base_ref(tmp_path, "HEAD") == "HEAD"


def test_get_changed_files_and_diff_single_commit(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "app.py")
    _git(tmp_path, "commit", "-m", "first")

    files = get_changed_files(tmp_path, base_ref="HEAD~1", head_ref="HEAD")
    assert files == ["app.py"]

    diff = get_diff_for_file(tmp_path, "app.py", base_ref="HEAD~1", head_ref="HEAD")
    assert "+x = 1" in diff


def test_get_changed_files_between_commits(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "a.py").write_text("a = 1\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("hello\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "c1")

    (tmp_path / "a.py").write_text("a = 2\n", encoding="utf-8")
    _git(tmp_path, "add", "a.py")
    _git(tmp_path, "commit", "-m", "c2")

    files = get_changed_files(tmp_path, base_ref="HEAD~1", head_ref="HEAD")
    assert files == ["a.py"]

    diff = get_diff_for_file(tmp_path, "a.py", base_ref="HEAD~1", head_ref="HEAD")
    assert "-a = 1" in diff
    assert "+a = 2" in diff


def test_rodar_git_invalid_command_raises(tmp_path):
    _init_repo(tmp_path)
    with pytest.raises(RuntimeError):
        rodar_git(tmp_path, ["rev-parse", "--verify", "nao-existe"])
