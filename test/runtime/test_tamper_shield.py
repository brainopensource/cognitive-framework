"""T-18: TestTamperShield hashes IndexPort-enumerated tests at turn 0.

Path.glob("test/**") is insufficient: an index-known oracle outside that
tree must still freeze, and an assertion edit must fail admission.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Sequence

from vanguard.packages.ports.event_store import Result
from vanguard.packages.ports.index import (
    DependencyEdge,
    RepositoryMap,
    Symbol,
    TestAssociation,
)
from vanguard.packages.runtime.governance.tamper_shield import TestTamperShield

_PUBLIC = "def test_public():\n    assert 1 + 1 == 2\n"
_HIDDEN = "def test_hidden():\n    assert add(1, 1) == 2\n"
_TAMPERED = "def test_hidden():\n    assert True\n"


class _Index:
    """Minimal IndexPort: tests() is the enumeration source of record."""

    def __init__(self, test_paths: tuple[str, ...], *, fail: bool = False) -> None:
        self._assoc = tuple(TestAssociation(path, "src/app.py") for path in test_paths)
        self._fail = fail

    def index(self, root: str) -> Result[int]:
        return Result.success(len(self._assoc))

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        paths = tuple(item.test_path for item in self._assoc)
        return Result.success(tuple(p for p in paths if p.startswith(prefix)))

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        return Result.success(())

    def dependencies(self, *, path: str = "") -> Result[Sequence[DependencyEdge]]:
        return Result.success(())

    def tests(self, *, path: str = "") -> Result[Sequence[TestAssociation]]:
        if self._fail:
            return Result.fail("unavailable", "index enumeration failed")
        return Result.success(
            tuple(
                item for item in self._assoc
                if not path or item.test_path.startswith(path) or item.source_path.startswith(path)
            )
        )

    def repo_map(self, *, token_budget: int = 4000) -> Result[RepositoryMap]:
        return Result.fail("unavailable", "unused")


def _workspace(root: Path) -> tuple[Path, Path]:
    public = root / "test" / "test_app.py"
    hidden = root / "hidden" / "spec_oracle.py"
    public.parent.mkdir(parents=True)
    hidden.parent.mkdir(parents=True)
    public.write_text(_PUBLIC, encoding="utf-8")
    hidden.write_text(_HIDDEN, encoding="utf-8")
    return public, hidden


class TestTamperShieldAdmission(unittest.TestCase):
    def test_assertion_edit_on_enumerated_test_rejects_admission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _workspace(root)
            index = _Index(("test/test_app.py", "hidden/spec_oracle.py"))
            shield = TestTamperShield.freeze(root, index)

            (root / "hidden" / "spec_oracle.py").write_text(_TAMPERED, encoding="utf-8")
            verdict = shield.evaluate()

            self.assertFalse(verdict.admissible)
            self.assertIn("TAMPER", verdict.reason)

    def test_glob_only_list_is_insufficient_index_known_oracle_outside_test_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _workspace(root)
            hidden_rel = "hidden/spec_oracle.py"
            globbed = {
                path.relative_to(root).as_posix()
                for path in root.glob("test/**")
                if path.is_file()
            }
            self.assertNotIn(hidden_rel, globbed)

            shield = TestTamperShield.freeze(
                root, _Index(("test/test_app.py", hidden_rel)),
            )
            self.assertIn(hidden_rel, shield.frozen_test_digests)

            (root / hidden_rel).write_text(_TAMPERED, encoding="utf-8")
            verdict = shield.evaluate()
            self.assertFalse(verdict.admissible)
            self.assertIn("TAMPER", verdict.reason)

    def test_unmodified_enumerated_tests_admit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _workspace(root)
            shield = TestTamperShield.freeze(
                root, _Index(("test/test_app.py", "hidden/spec_oracle.py")),
            )
            verdict = shield.evaluate()
            self.assertTrue(verdict.admissible)

    def test_deleted_enumerated_test_rejects_admission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public, hidden = _workspace(root)
            shield = TestTamperShield.freeze(
                root, _Index(("test/test_app.py", "hidden/spec_oracle.py")),
            )
            hidden.unlink()
            verdict = shield.evaluate()
            self.assertFalse(verdict.admissible)
            self.assertIn("TAMPER", verdict.reason)
            self.assertTrue(public.exists())


if __name__ == "__main__":
    unittest.main()
