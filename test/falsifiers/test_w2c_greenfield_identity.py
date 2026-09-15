"""W2c: an unborn Git repository is a valid, content-addressed candidate.

The product session must publish a ``ChangeSurfaceUpdated`` carrier for a
greenfield tree without laundering the absence of ``HEAD`` into an unbound
identity.  A directory that Git cannot enumerate remains a refusal.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from test.runtime.test_harness_session import FakeClock
from vanguard.packages.adapters.environment.git import GitEnvironment
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.kernel import FailurePath
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.entrypoint import _completion_policy, _manifest
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext
from vanguard.packages.runtime.session import WorkspaceSnapshotRefused


def _ok_result() -> SimpleNamespace:
    return SimpleNamespace(
        failure=FailurePath.OK,
        outcome=SimpleNamespace(
            status="ok",
            detail="patch applied",
            result_digest="sha256:patch-result",
        ),
    )


def _session(root: Path) -> HarnessSession:
    return HarnessSession(
        Runtime.compose("vg-code-default", episode_id="ep-w2c"),
        SessionPorts(
            model=FakeModel([]),
            environment=GitEnvironment(root),
            clock=FakeClock(),
            store=SqliteEventStore(":memory:"),
            interactive=False,
            completion_policy=_completion_policy(_manifest("code")),
        ),
        TaskContext(
            brief="Create a greenfield project from scratch",
            repo_path=root,
            run_id="run-w2c",
            episode_id="ep-w2c",
        ),
    )


class GreenfieldGitSnapshotIdentity(unittest.TestCase):
    def test_unborn_repository_has_a_content_snapshot_and_explicit_absent_revision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "app.py").write_text("print('greenfield')\n", encoding="utf-8")

            snapshot = GitEnvironment(root).snapshot()

            self.assertTrue(snapshot.ok, snapshot.error)
            self.assertIsNotNone(snapshot.value)
            assert snapshot.value is not None
            self.assertTrue(snapshot.value.digest.startswith("sha256:"))
            self.assertEqual(snapshot.value.metadata["head_commit"], None)
            self.assertIn("unborn", snapshot.value.snapshot_id)

    def test_greenfield_change_surface_has_a_bound_candidate_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "app.py").write_text("print('greenfield')\n", encoding="utf-8")
            session = _session(root)

            session._observe_completion_dispatch(
                SimpleNamespace(action="patch.apply", args={"path": "app.py"}),
                _ok_result(),
            )

            events = session.ports.store.read(EventRange(run_id="run-w2c"))
            self.assertTrue(events.ok, events.error)
            payload = next(
                event.payload for event in events.value or ()
                if event.payload.get("kind") == "ChangeSurfaceUpdated"
            )
            self.assertTrue(payload["candidateDigest"].startswith("sha256:"))
            self.assertEqual(payload["candidateDigest"], session._workspace_digest())

    def test_unresolved_head_with_other_history_is_not_an_unborn_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "w2c@example.test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "w2c-test"], cwd=root, check=True)
            (root / "prior.py").write_text("VALUE = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "prior.py"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=root, check=True)
            subprocess.run(["git", "checkout", "-q", "--orphan", "greenfield"], cwd=root, check=True)

            snapshot = GitEnvironment(root).snapshot()

            self.assertFalse(snapshot.ok)
            self.assertIsNotNone(snapshot.error)
            self.assertEqual(snapshot.error.kind, "instrument_error")
            self.assertIn("HEAD", snapshot.error.message)

    def test_non_repository_still_refuses_snapshot_enumeration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("print('not a repository')\n", encoding="utf-8")

            snapshot = GitEnvironment(root).snapshot()

            self.assertFalse(snapshot.ok)
            self.assertIsNotNone(snapshot.error)
            self.assertEqual(snapshot.error.kind, "instrument_error")

    def test_non_repository_is_a_typed_session_refusal_not_an_empty_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app.py").write_text("print('not a repository')\n", encoding="utf-8")
            session = _session(root)

            with self.assertRaises(WorkspaceSnapshotRefused) as raised:
                session._observe_completion_dispatch(
                    SimpleNamespace(action="patch.apply", args={"path": "app.py"}),
                    _ok_result(),
                )

            self.assertEqual(raised.exception.kind, "instrument_error")
            self.assertNotIn("unbound identity", str(raised.exception))
