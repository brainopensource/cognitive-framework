"""T-14 WorkspaceEpoch: bind packets; write invalidates until refresh."""

from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path
from typing import Any

from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.repo_index import FileRepoIndex, InMemoryRepoIndex
from vanguard.packages.agency.context import (
    ContextPacketError,
    build_context_packet,
    validate_completion_epoch,
    validate_resume_identity,
)
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.workspace_epoch import WorkspaceEpoch
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext


def _epoch(**overrides: object) -> WorkspaceEpoch:
    values: dict[str, object] = {
        "tree_hash": "sha256:" + "a" * 64,
        "index_digest": "sha256:" + "b" * 64,
        "source_revision": "sha256:" + "c" * 64,
        "compiled_at_turn": 0,
    }
    values.update(overrides)
    return WorkspaceEpoch(**values)  # type: ignore[arg-type]


def _packet(*, epoch: WorkspaceEpoch | None) -> Any:
    return build_context_packet(
        task_digest="sha256:task",
        repository_snapshot="sha256:repo",
        provider="index",
        provider_version="1",
        query_digest="sha256:q",
        budget_tokens=100,
        repository_identity="sha256:repo",
        selection_policy_identity={"policyId": "agency.context-compiler/default"},
        index_snapshot_digest="sha256:idx",
        workspace_epoch=epoch,
    )


class WorkspaceEpochValueTests(unittest.TestCase):
    def test_four_fields_map_to_law_names(self) -> None:
        epoch = _epoch(compiled_at_turn=3)
        canonical = epoch.to_canonical_dict()
        self.assertEqual(canonical["treeHash"], epoch.tree_hash)
        self.assertEqual(canonical["indexDigest"], epoch.index_digest)
        self.assertEqual(canonical["sourceRevision"], epoch.source_revision)
        self.assertEqual(canonical["compiledAtTurn"], 3)

    def test_missing_tree_hash_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            _epoch(tree_hash="")

    def test_missing_index_digest_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            _epoch(index_digest="")


class PacketEpochTests(unittest.TestCase):
    def test_legacy_packet_without_epoch_may_resume(self) -> None:
        packet = _packet(epoch=None)
        validate_resume_identity(
            packet,
            repository_identity="sha256:repo",
            index_snapshot_digest="sha256:idx",
            selection_policy_identity={"policyId": "agency.context-compiler/default"},
        )

    def test_legacy_packet_cannot_admit_completed(self) -> None:
        packet = _packet(epoch=None)
        with self.assertRaises(ContextPacketError):
            validate_completion_epoch(packet, _epoch())

    def test_stale_epoch_cannot_admit_completed(self) -> None:
        packet = _packet(epoch=_epoch())
        current = _epoch(tree_hash="sha256:" + "d" * 64)
        with self.assertRaises(ContextPacketError):
            validate_completion_epoch(packet, current)

    def test_matching_epoch_admits_for_completion_check(self) -> None:
        epoch = _epoch()
        validate_completion_epoch(_packet(epoch=epoch), epoch)

    def test_product_compile_without_epoch_refuses(self) -> None:
        with self.assertRaises(ContextPacketError):
            build_context_packet(
                task_digest="sha256:task",
                repository_snapshot="sha256:repo",
                provider="index",
                provider_version="1",
                query_digest="sha256:q",
                budget_tokens=100,
                require_epoch=True,
            )


class IndexEpochBindingTests(unittest.TestCase):
    def test_index_digest_is_snapshot_not_directory_listing(self) -> None:
        same_names_a = InMemoryRepoIndex({
            "pkg/mod.py": "def alpha():\n    return 1\n",
        })
        same_names_b = InMemoryRepoIndex({
            "pkg/mod.py": "def beta():\n    return 2\n",
        })
        map_a = same_names_a.repo_map().value
        map_b = same_names_b.repo_map().value
        listing = digest_of({"files": list(map_a.files)})
        self.assertEqual(list(map_a.files), list(map_b.files))
        self.assertNotEqual(map_a.index_digest, listing)
        self.assertNotEqual(map_a.index_digest, map_b.index_digest)
        self.assertTrue(map_a.tree_hash)
        self.assertTrue(map_a.index_digest)
        self.assertTrue(map_a.source_revision)

    def test_write_changes_tree_hash_without_reindex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "pkg" / "mod.py"
            target.parent.mkdir()
            target.write_text("def run():\n    return 1\n")
            index = FileRepoIndex()
            self.assertTrue(index.index(str(root)).ok)
            before = index.repo_map().value.tree_hash
            target.write_text("def run():\n    return 2\n")
            after = index.repo_map().value.tree_hash
            self.assertNotEqual(before, after)

    def test_unindexed_file_index_fails_closed_on_tree_hash(self) -> None:
        fresh = FileRepoIndex()
        mapped = fresh.repo_map()
        self.assertFalse(mapped.ok)


class SessionEpochFalsifierTests(unittest.TestCase):
    def _session(self, repo: Path, index: Any) -> HarnessSession:
        harness = dataclasses.replace(
            Runtime.compose("vg-code-fast", episode_id="ep-epoch-1"),
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
            brief="bind the workspace epoch",
            repo_path=repo,
            run_id="run-epoch-1",
            episode_id="ep-epoch-1",
            principal="agent-1",
            max_turns=4,
        )
        return HarnessSession(harness, ports, task)

    def test_product_compile_stamps_epoch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "main.py").write_text("def run():\n    return 1\n")
            index = FileRepoIndex()
            session = self._session(repo, index)
            packet = session.context_packet
            self.assertIsNotNone(packet)
            self.assertIsNotNone(packet.workspace_epoch)
            self.assertTrue(packet.workspace_epoch.tree_hash)
            self.assertTrue(packet.workspace_epoch.index_digest)
            self.assertEqual(
                packet.workspace_epoch.source_revision,
                index.repo_map().value.source_revision,
            )
            self.assertEqual(packet.workspace_epoch.compiled_at_turn, 0)

    def test_write_invalidates_packet_until_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "src" / "main.py"
            target.parent.mkdir()
            target.write_text("def run():\n    return 1\n")
            index = FileRepoIndex()
            session = self._session(repo, index)
            stale = session.context_packet
            first_epoch = stale.workspace_epoch
            target.write_text("def run():\n    return 2\n")
            current = session.current_workspace_epoch()
            self.assertNotEqual(first_epoch, current)
            with self.assertRaises(ContextPacketError):
                validate_completion_epoch(stale, current)
            verdict = session._admit_completion(None, {"kind": "finish"})
            self.assertFalse(verdict.admissible)
            self.assertIn("EPOCH", verdict.reason)
            refreshed = session.refresh_context_packet()
            self.assertEqual(refreshed.workspace_epoch, session.current_workspace_epoch())
            self.assertNotEqual(refreshed.workspace_epoch, first_epoch)
            validate_completion_epoch(refreshed, session.current_workspace_epoch())


if __name__ == "__main__":
    unittest.main()
