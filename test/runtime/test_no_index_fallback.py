"""T-45: IndexPort down/unbound is a documented fallback, never a silent empty map."""

from __future__ import annotations

import dataclasses
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Sequence

from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.agency.context import ContextPacketError
from vanguard.packages.agency.context.layers import Layer
from vanguard.packages.agency.episode.admission_gate import AdmissionVerdict

INDEX_PORT_UNBOUND = "index.port.unbound"
from vanguard.packages.ports.event_store import Result
from vanguard.packages.ports.index import (
    DependencyEdge,
    RepositoryMap,
    Symbol,
    TestAssociation,
)
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext


class DownIndex:
    """IndexPort that is bound in composition but cannot produce a map."""

    def index(self, root: str) -> Result[int]:
        return Result.fail("unavailable", "index down")

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        return Result.fail("unavailable", "index down")

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        return Result.fail("unavailable", "index down")

    def dependencies(self, *, path: str = "") -> Result[Sequence[DependencyEdge]]:
        return Result.fail("unavailable", "index down")

    def tests(self, *, path: str = "") -> Result[Sequence[TestAssociation]]:
        return Result.fail("unavailable", "index down")

    def repo_map(self, *, token_budget: int = 4000) -> Result[RepositoryMap]:
        return Result.fail("unavailable", "index down")


class UnboundSnapshotEnvironment(FakeEnvironment):
    def snapshot(self) -> Result[Any]:
        return Result.fail("unavailable", "snapshot unbound")


def _session(
    repo: Path,
    *,
    index: Any | None = None,
    environment: Any | None = None,
    index_component: str | None = "repo_index.json",
    harness_name: str = "vg-code-fast",
) -> HarnessSession:
    harness = dataclasses.replace(
        Runtime.compose(harness_name, episode_id="ep-no-index-1"),
        index_component=index_component,
    )
    ports = SessionPorts(
        model=FakeModel([]),
        environment=environment or FakeEnvironment(),
        clock=FakeClock(),
        store=SqliteEventStore(":memory:"),
        index=index,
        interactive=False,
    )
    task = TaskContext(
        brief="bind epoch without inventing symbols",
        repo_path=repo,
        run_id="run-no-index-1",
        episode_id="ep-no-index-1",
        principal="agent-1",
        max_turns=4,
    )
    return HarnessSession(harness, ports, task)


class NoIndexFallbackTests(unittest.TestCase):
    def test_unbound_index_binds_epoch_with_explicit_omission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "secret.py").write_text("def invented():\n    return 1\n")
            session = _session(repo, index=None, index_component=None, harness_name="vg-code-default")
            packet = session.context_packet
            self.assertIsNotNone(packet)
            self.assertIn(INDEX_PORT_UNBOUND, packet.omissions)
            self.assertTrue(packet.truncated)
            self.assertEqual(packet.symbols, ())
            names = {item.get("name") for item in packet.symbols}
            self.assertNotIn("invented", names)
            self.assertIsNotNone(packet.workspace_epoch)
            live = session.current_workspace_epoch()
            self.assertEqual(packet.workspace_epoch, live)
            env_text = "\n".join(
                block.text for block in session.operator._compiler._prefix
                if block.layer == Layer.ENVIRONMENT
            )
            self.assertIn(INDEX_PORT_UNBOUND, env_text)

    def test_down_index_does_not_serve_silent_empty_complete_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src").mkdir()
            (repo / "src" / "hidden.py").write_text("def hidden_symbol():\n    return 1\n")
            session = _session(repo, index=DownIndex())
            packet = session.context_packet
            self.assertIsNotNone(packet)
            self.assertIn(INDEX_PORT_UNBOUND, packet.omissions)
            self.assertTrue(packet.truncated)
            self.assertEqual(packet.symbols, ())
            self.assertNotIn("hidden_symbol", " ".join(str(item) for item in packet.symbols))
            self.assertIsNotNone(packet.workspace_epoch)
            self.assertEqual(packet.workspace_epoch, session.current_workspace_epoch())

    def test_snapshot_unbound_fails_closed_with_typed_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            session = _session(
                repo,
                index=DownIndex(),
                environment=UnboundSnapshotEnvironment(),
            )
            self.assertIsNone(session.context_packet)
            with self.assertRaises(ContextPacketError) as raised:
                session.current_workspace_epoch()
            self.assertIn("INDEX_UNBOUND", str(raised.exception))
            verdict = session._admit_completion(SimpleNamespace(), SimpleNamespace())
            self.assertIsInstance(verdict, AdmissionVerdict)
            self.assertFalse(verdict.admissible)
            self.assertEqual(verdict.reason, "INDEX_UNBOUND")


class IndexToolkitNoIndexFallbackTests(unittest.TestCase):
    def test_render_documents_unbound_index_and_does_not_invent_symbols(self) -> None:
        import sys

        pack = Path(__file__).resolve().parents[2] / "packs" / "code-default"
        sys.path.insert(0, str(pack))
        from toolkits.repo_map import IndexToolkit  # type: ignore[import-not-found]

        toolkit = IndexToolkit("/nonexistent-workspace", index=DownIndex())
        rendered = toolkit.render(4000)
        self.assertIn(INDEX_PORT_UNBOUND, rendered)
        self.assertNotIn("hidden_symbol", rendered)
        self.assertNotEqual(rendered.strip(), "")
        scanned = toolkit.scan()
        self.assertIn(INDEX_PORT_UNBOUND, scanned)


if __name__ == "__main__":
    unittest.main()
