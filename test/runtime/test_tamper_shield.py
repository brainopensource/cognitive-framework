"""T-18: TestTamperShield hashes IndexPort-enumerated tests at turn 0.

Path.glob("test/**") is insufficient: an index-known oracle outside that
tree must still freeze, and an assertion edit must fail admission.

`TestTamperShieldIsWiredIntoAdmission` is the reopened half.  The mechanism
below was correct and had zero production callers, so nothing in a real run
ever consulted it; these cases pin `HarnessSession` freezing the shield at
turn 0 and evaluating it inside `_admit_completion`.
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
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)

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


class TestTamperShieldIsWiredIntoAdmission(unittest.TestCase):
    """T-18 REOPENED: the shield must have a production caller, not just a test."""

    def _session(self, root: Path, index: _Index) -> HarnessSession:
        from test.agency.doubles import ScriptedModel, finish
        from test.runtime.test_harness_session import FakeClock, FakeEnvironment
        from vanguard.packages.adapters.stores.event_store import SqliteEventStore

        # The public default preset must itself declare the enumeration source;
        # inheriting protection only in fast/balanced/max leaves `vg code`
        # fail-open.
        harness = Runtime.compose("vg-code-default", episode_id="ep-tamper")
        return HarnessSession(
            harness,
            SessionPorts(
                model=ScriptedModel([finish("done")]),
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                index=index,
                interactive=False,
            ),
            TaskContext(
                brief="tamper", repo_path=root, project_id="project-tamper",
                run_id="run-tamper", episode_id="ep-tamper",
                principal="agent-tamper", max_turns=2),
        )

    def test_the_session_freezes_the_enumerated_set_at_turn_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _workspace(root)
            session = self._session(
                root, _Index(("test/test_app.py", "hidden/spec_oracle.py")))

            self.assertIsNotNone(session._tamper_shield)
            self.assertEqual(
                set(session._tamper_shield.frozen_test_digests),
                {"test/test_app.py", "hidden/spec_oracle.py"},
            )

    def test_an_assertion_edit_rejects_the_real_admission_call(self) -> None:
        """The production path, not the mechanism in isolation."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _workspace(root)
            session = self._session(
                root, _Index(("test/test_app.py", "hidden/spec_oracle.py")))

            (root / "hidden" / "spec_oracle.py").write_text(_TAMPERED, encoding="utf-8")
            verdict = session._admit_completion(None, {"kind": "finish"})

            self.assertFalse(verdict.admissible)
            self.assertEqual(verdict.reason, "TAMPER_VIOLATION")
            self.assertIn("spec_oracle.py", verdict.rejection_feedback or "")

    def test_a_failed_enumeration_is_not_read_as_a_clean_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _workspace(root)
            session = self._session(root, _Index(("test/test_app.py",), fail=True))

            self.assertTrue(session._tamper_shield.enumeration_failed)
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(verdict.admissible)
            self.assertEqual(verdict.reason, "TAMPER_VIOLATION")

    def test_an_untouched_oracle_set_does_not_reject_on_tamper(self) -> None:
        """The shield may not become a blanket denial of every completion."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _workspace(root)
            session = self._session(
                root, _Index(("test/test_app.py", "hidden/spec_oracle.py")))

            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertNotEqual(verdict.reason, "TAMPER_VIOLATION")


if __name__ == "__main__":
    unittest.main()
