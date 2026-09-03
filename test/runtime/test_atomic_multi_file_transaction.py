"""T-17: adapter 2PC — AST preflight before disk; syntax fail rolls back the set.

Single-file sequential observation remains S8-B-09 (`test_aci_gifts`).
This module proves multi-file `GitEnvironment.apply` is all-or-nothing.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.environment.git import GitEnvironment
from vanguard.packages.adapters.environment.transaction import (
    AtomicMultiFileTransactionManager,
    FileMutation,
)
from vanguard.packages.ports.environment import EffectRequest

_PRE = "VALUE = 1\n"
_GOOD = "VALUE = 2\n"
_BAD = "def broken(\n    return 1\n"
_FILES = ("a.py", "b.py", "c.py", "d.py", "e.py")
_TMP_MARKERS = (".vg-txn-", ".tmp")


def _git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t17@vanguard.dev"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T-17"], cwd=root, check=True, capture_output=True)


def _mod_hunk(path: str, old: str, new: str) -> str:
    old_n = old.count("\n") or 1
    new_n = new.count("\n") or 1
    minus = "".join(f"-{line}\n" for line in old.splitlines())
    plus = "".join(f"+{line}\n" for line in new.splitlines())
    return (
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
        f"@@ -1,{old_n} +1,{new_n} @@\n"
        f"{minus}{plus}"
    )


def _leftover_tmp(root: Path) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part == ".git" for part in path.parts):
            continue
        name = path.name
        if any(marker in name for marker in _TMP_MARKERS):
            hits.append(path.relative_to(root).as_posix())
    return hits


class TestAtomicMultiFileTransaction(unittest.TestCase):
    def test_file_4_of_5_syntax_fail_rolls_back_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git_repo(repo)
            pre_image: dict[str, str] = {}
            for name in _FILES:
                (repo / name).write_text(_PRE, encoding="utf-8")
                pre_image[name] = _PRE

            hunks = []
            for index, name in enumerate(_FILES):
                replacement = _BAD if index == 3 else _GOOD
                hunks.append(_mod_hunk(name, _PRE, replacement))
            patch = "".join(hunks)

            env = GitEnvironment(repo_path=repo)
            result = env.apply(
                EffectRequest(verb="patch.apply", action="patch", patch=patch)
            )

            self.assertFalse(result.ok, "syntax-fail multi-file apply must not commit")
            self.assertIsNotNone(result.error)
            self.assertIn("SyntaxError", result.error.message if result.error else "")
            for name, expected in pre_image.items():
                self.assertEqual(
                    (repo / name).read_text(encoding="utf-8"),
                    expected,
                    f"{name} must match pre-image after rollback",
                )
            self.assertEqual(_leftover_tmp(repo), [])

    def test_valid_five_file_set_commits_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _git_repo(repo)
            for name in _FILES:
                (repo / name).write_text(_PRE, encoding="utf-8")
            patch = "".join(_mod_hunk(name, _PRE, _GOOD) for name in _FILES)
            env = GitEnvironment(repo_path=repo)
            result = env.apply(
                EffectRequest(verb="patch.apply", action="patch", patch=patch)
            )
            self.assertTrue(result.ok, result.error and result.error.message)
            for name in _FILES:
                self.assertEqual((repo / name).read_text(encoding="utf-8"), _GOOD)
            self.assertEqual(_leftover_tmp(repo), [])

    def test_manager_preflight_does_not_touch_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in _FILES:
                (root / name).write_text(_PRE, encoding="utf-8")
            mutations = []
            for index, name in enumerate(_FILES):
                content = _BAD if index == 3 else _GOOD
                mutations.append(FileMutation(path=name, content=content, action="modify"))
            manager = AtomicMultiFileTransactionManager(root)
            result = manager.execute_transaction(mutations)
            self.assertFalse(result.ok)
            for name in _FILES:
                self.assertEqual((root / name).read_text(encoding="utf-8"), _PRE)
            self.assertEqual(_leftover_tmp(root), [])


if __name__ == "__main__":
    unittest.main()
