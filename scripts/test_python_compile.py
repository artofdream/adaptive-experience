#!/usr/bin/env python3
"""Unit tests for check_python_compile.py.

Invalid fixture must fail. Current repository must pass. Git-backed cases
skip when git is absent (CI alpine).
"""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_python_compile import (  # noqa: E402
    check_python_compile,
    list_scoped_python,
    main,
)

HAS_GIT = shutil.which("git") is not None
BROKEN = "def broken(\n"


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "fixture@example.test"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "fixture"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _git_add(root: Path, rel: str) -> None:
    subprocess.run(["git", "add", "--", rel], cwd=root, check=True, capture_output=True, text=True)


class TestPythonCompileWalkFixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_invalid_fixture_fails(self) -> None:
        _write(self.root / "scripts" / "broken.py", BROKEN)
        _write(self.root / "scripts" / "ok.py", "VALUE = 1\n")
        ok, errors, count = check_python_compile(self.root, prefer_walk=True)
        self.assertFalse(ok)
        self.assertEqual(count, 2)
        self.assertTrue(any("scripts/broken.py" in err for err in errors), errors)

    def test_valid_fixture_passes(self) -> None:
        _write(self.root / "scripts" / "ok.py", "VALUE = 1\n")
        _write(self.root / "platform" / "ok.py", "VALUE = 2\n")
        _write(self.root / "edge" / "ok.py", "VALUE = 3\n")
        ok, errors, count = check_python_compile(self.root, prefer_walk=True)
        self.assertTrue(ok, errors)
        self.assertEqual(count, 3)
        self.assertEqual(errors, [])

    def test_out_of_scope_python_is_ignored(self) -> None:
        _write(self.root / "scripts" / "ok.py", "VALUE = 1\n")
        _write(self.root / "research" / "broken.py", BROKEN)
        ok, errors, count = check_python_compile(self.root, prefer_walk=True)
        self.assertTrue(ok, errors)
        self.assertEqual(count, 1)


@unittest.skipUnless(HAS_GIT, "git not on PATH")
class TestPythonCompileGitFixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _init_repo(self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_git_lists_only_tracked_scoped_files(self) -> None:
        _write(self.root / "scripts" / "ok.py", "VALUE = 1\n")
        _write(self.root / "scripts" / "untracked_broken.py", BROKEN)
        _write(self.root / "docs" / "skipped.py", "VALUE = 9\n")
        _git_add(self.root, "scripts/ok.py")
        paths = list_scoped_python(self.root)
        self.assertEqual(paths, ["scripts/ok.py"])
        ok, errors, count = check_python_compile(self.root)
        self.assertTrue(ok, errors)
        self.assertEqual(count, 1)

    def test_git_tracked_invalid_fixture_fails(self) -> None:
        _write(self.root / "scripts" / "broken.py", BROKEN)
        _git_add(self.root, "scripts/broken.py")
        ok, errors, count = check_python_compile(self.root)
        self.assertFalse(ok)
        self.assertEqual(count, 1)
        self.assertTrue(any("scripts/broken.py" in err for err in errors), errors)


class TestPythonCompileRepository(unittest.TestCase):
    def test_current_repository_compiles(self) -> None:
        ok, errors, count = check_python_compile()
        self.assertTrue(ok, errors)
        self.assertGreater(count, 0)

    def test_main_exits_zero(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            code = main()
        self.assertEqual(code, 0, buf.getvalue())
        self.assertIn("ok:", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
