"""T-37: packet omissions are a ledger; truncated is not complete."""

from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path
from dataclasses import replace
from typing import Any

from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.repo_index import FileRepoIndex
from vanguard.packages.agency.context import (
    ContextPacketError,
    build_context_packet,
    validate_completion_omissions,
)
from vanguard.packages.domain.workspace_epoch import WorkspaceEpoch
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext


def _epoch() -> WorkspaceEpoch:
    return WorkspaceEpoch(
        tree_hash="sha256:" + "a" * 64,
        index_digest="sha256:" + "b" * 64,
        source_revision="sha256:" + "c" * 64,
        compiled_at_turn=0,
    )


class OmissionLedgerTests(unittest.TestCase):
    def test_build_reports_explicit_omitted_items(self) -> None:
        packet = build_context_packet(
            task_digest="sha256:task",
            repository_snapshot="sha256:repo",
            provider="index",
            provider_version="1",
            query_digest="sha256:q",
            budget_tokens=20,
            reserve_tokens=10,
            selected=(
                {"kind": "file", "path": "src/keep.py", "estimated_tokens": 8},
                {"kind": "file", "path": "src/required.py", "estimated_tokens": 50},
            ),
            workspace_epoch=_epoch(),
            require_epoch=True,
        )
        self.assertEqual(packet.files, ("src/keep.py",))
        self.assertEqual(packet.omissions, ("src/required.py",))
        self.assertTrue(packet.truncated)
        self.assertIn("src/required.py", packet.omission_report())

    def test_truncated_packet_cannot_admit_completed(self) -> None:
        packet = build_context_packet(
            task_digest="sha256:task",
            repository_snapshot="sha256:repo",
            provider="index",
            provider_version="1",
            query_digest="sha256:q",
            budget_tokens=20,
            reserve_tokens=10,
            selected=(
                {"kind": "file", "path": "src/keep.py", "estimated_tokens": 8},
                {"kind": "file", "path": "src/required.py", "estimated_tokens": 50},
            ),
            workspace_epoch=_epoch(),
            require_epoch=True,
        )
        with self.assertRaises(ContextPacketError) as raised:
            validate_completion_omissions(packet, required=("src/required.py",))
        self.assertIn("src/required.py", str(raised.exception))

    def test_complete_packet_with_no_required_omissions_admits(self) -> None:
        packet = build_context_packet(
            task_digest="sha256:task",
            repository_snapshot="sha256:repo",
            provider="index",
            provider_version="1",
            query_digest="sha256:q",
            budget_tokens=100,
            selected=({"kind": "file", "path": "src/keep.py", "estimated_tokens": 8},),
            workspace_epoch=_epoch(),
            require_epoch=True,
        )
        self.assertFalse(packet.truncated)
        validate_completion_omissions(packet, required=("src/keep.py",))


class SessionOmissionAdmissionTests(unittest.TestCase):
    def _session(self, repo: Path, index: FileRepoIndex) -> HarnessSession:
        harness = dataclasses.replace(
            Runtime.compose("vg-code-fast", episode_id="ep-omit-1"),
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
            brief="omit required files",
            repo_path=repo,
            run_id="run-omit-1",
            episode_id="ep-omit-1",
            principal="agent-1",
            max_turns=4,
        )
        return HarnessSession(harness, ports, task)

    def test_completion_rejected_when_required_files_were_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "keep.py").write_text("def keep():\n    return 1\n")
            (repo / "src" / "required.py").write_text("def required():\n    return 1\n")
            index = FileRepoIndex()
            session = self._session(repo, index)
            packet = session.context_packet
            self.assertIsNotNone(packet)
            session.context_packet = replace(
                packet, omissions=("src/required.py",), truncated=True,
            )
            session._completion_changed_files.add("src/required.py")
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(verdict.admissible)
            self.assertIn("OMISSION", verdict.reason)


if __name__ == "__main__":
    unittest.main()
