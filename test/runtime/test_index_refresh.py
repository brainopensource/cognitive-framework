"""T-16: index.refresh after write; next compile must not serve a pre-write map."""

from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.repo_index import FileRepoIndex
from vanguard.packages.agency.context import ContextPacketError, validate_completion_epoch
from vanguard.packages.kernel import FailurePath
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext


def _ok_write_result() -> Any:
    return SimpleNamespace(
        failure=FailurePath.OK,
        outcome=SimpleNamespace(
            status="ok",
            detail="patched",
            result_digest="sha256:" + "e" * 64,
        ),
    )


class IndexRefreshAfterWriteTests(unittest.TestCase):
    def _session(self, repo: Path, index: FileRepoIndex) -> HarnessSession:
        harness = dataclasses.replace(
            Runtime.compose("vg-code-fast", episode_id="ep-refresh-1"),
            index_component="repo_index.json",
        )
        ports = SessionPorts(
            model=FakeModel([]),
            environment=FakeEnvironment(),
            clock=FakeClock(),
            store=SqliteEventStore(":memory:"),
            index=index,
            interactive=False,
        )
        task = TaskContext(
            brief="refresh the index after a write",
            repo_path=repo,
            run_id="run-refresh-1",
            episode_id="ep-refresh-1",
            principal="agent-1",
            max_turns=4,
        )
        return HarnessSession(harness, ports, task)

    def test_dirty_tree_does_not_present_pre_write_map_as_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "pkg" / "mod.py"
            target.parent.mkdir()
            target.write_text("def run():\n    return 1\n")
            index = FileRepoIndex()
            self.assertTrue(index.index(str(root)).ok)
            before = index.repo_map().value
            self.assertFalse(before.truncated)
            self.assertTrue(any(item.name == "run" for item in before.symbols))
            self.assertFalse(any(item.name == "added_after_write" for item in before.symbols))
            target.write_text(
                "def run():\n    return 1\n\ndef added_after_write():\n    return 2\n"
            )
            stale = index.repo_map().value
            names = {item.name for item in stale.symbols}
            self.assertNotIn("added_after_write", names)
            self.assertTrue(stale.truncated, "stale pre-write repo_map must not be served as complete")

    def test_observe_write_refreshes_index_and_packet_includes_new_symbol(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "src" / "main.py"
            target.parent.mkdir()
            target.write_text("def run():\n    return 1\n")
            index = FileRepoIndex()
            session = self._session(repo, index)
            first = session.context_packet
            self.assertIsNotNone(first)
            names_before = {item.get("name") for item in first.symbols}
            self.assertIn("run", names_before)
            self.assertNotIn("added_after_write", names_before)
            first_digest = first.workspace_epoch.index_digest
            first_epoch = first.workspace_epoch

            target.write_text(
                "def run():\n    return 1\n\ndef added_after_write():\n    return 2\n"
            )
            session._observe_completion_dispatch(
                SimpleNamespace(action="patch.apply", args={"path": "src/main.py"}),
                _ok_write_result(),
            )
            packet = session.context_packet
            self.assertIsNotNone(packet)
            names = {item.get("name") for item in packet.symbols}
            omitted = " ".join(str(item) for item in packet.omissions)
            self.assertTrue(
                "added_after_write" in names or "added_after_write" in omitted,
                f"new symbol missing from packet and omissions: names={names} omissions={packet.omissions}",
            )
            self.assertNotEqual(packet.workspace_epoch.index_digest, first_digest)
            self.assertNotEqual(packet.workspace_epoch, first_epoch)
            self.assertEqual(packet.workspace_epoch, session.current_workspace_epoch())
            live_names = {item.name for item in index.repo_map().value.symbols}
            self.assertIn("added_after_write", live_names)
            self.assertFalse(index.repo_map().value.truncated)

    def test_stale_epoch_still_cannot_complete_after_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "src" / "main.py"
            target.parent.mkdir()
            target.write_text("def run():\n    return 1\n")
            index = FileRepoIndex()
            session = self._session(repo, index)
            stale = session.context_packet
            target.write_text("def run():\n    return 2\n")
            current = session.current_workspace_epoch()
            with self.assertRaises(ContextPacketError):
                validate_completion_epoch(stale, current)
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(verdict.admissible)
            self.assertIn("EPOCH", verdict.reason)


if __name__ == "__main__":
    unittest.main()
