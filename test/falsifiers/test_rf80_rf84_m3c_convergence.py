"""RF-80..RF-84: executable M-3C convergence falsifiers (ADR-0088)."""

from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.evidence.foundation import FoundationEvidenceError, EvidenceRow
from vanguard.packages.runtime.compose import Runtime as CompositionRuntime
from vanguard.packages.runtime.root import Runtime, TaskContext
from vanguard.packages.runtime import lab_driver
from vanguard.packages.runtime.wiring import DEFAULT_BINDINGS


class M3CConvergenceFalsifiers(unittest.TestCase):
    def _execute(self, *, store: SqliteEventStore | None = None, release: bool = False):
        with tempfile.TemporaryDirectory() as directory, patch(
            "vanguard.packages.runtime.root._bwrap_path", return_value="/bin/true"
        ):
            return Runtime.execute_harness(
                "vg-table-default",
                TaskContext("finish", Path(directory), run_id="rf80-run", episode_id="rf80-ep"),
                model=FakeModel([{"kind": "finish", "note": "done"}]),
                store=store,
                release=release,
            )

    def test_rf80_public_execution_traverses_registry_and_retires(self) -> None:
        result = self._execute()
        kinds = [event.kind for event in result.events]
        self.assertIn("PluginActivated", kinds)
        self.assertEqual(kinds.count("PluginActivated"), kinds.count("PluginRetired"))
        self.assertGreater(kinds.index("PluginActivated"), kinds.index("EpisodeStarted"))
        self.assertGreater(kinds.index("PluginRetired"), kinds.index("EpisodeCompleted"))

    def test_rf81_both_domains_resolve_without_global_table_authority(self) -> None:
        code = CompositionRuntime.compose("vg-code-default")
        table = CompositionRuntime.compose("vg-table-default")
        self.assertEqual(set(code.bindings), set(code.verbs))
        self.assertEqual(set(table.bindings), {"table.read", "table.patch"})
        self.assertTrue(set(table.bindings).isdisjoint(DEFAULT_BINDINGS))

    def test_rf82_release_refuses_memory_and_accepts_explicit_wal(self) -> None:
        with self.assertRaisesRegex(ValueError, "file-backed SQLite-WAL"):
            self._execute(store=SqliteEventStore(":memory:"), release=True)
        with tempfile.TemporaryDirectory() as directory:
            store = SqliteEventStore(Path(directory) / "events.db")
            result = self._execute(store=store, release=True)
            mode = store._conn.execute("PRAGMA journal_mode").fetchone()[0]
            self.assertEqual(mode.lower(), "wal")
            self.assertTrue(result.store.read().ok)

    def test_rf83_asserted_evidence_is_not_a_valid_row_state(self) -> None:
        with self.assertRaisesRegex(FoundationEvidenceError, "derived or absent"):
            EvidenceRow(1, "real_model_invocation", status="asserted")

    def test_rf84_public_runtime_contains_one_compose_activate_session_trace(self) -> None:
        public_source = inspect.getsource(Runtime.execute_harness)
        boundary_source = inspect.getsource(Runtime.run_composed)
        lab_source = inspect.getsource(lab_driver.run_lab_task)
        self.assertEqual(public_source.count("cls.compose("), 1)
        self.assertEqual(public_source.count("cls.run_composed("), 1)
        self.assertEqual(boundary_source.count("plan_activation("), 1)
        self.assertEqual(boundary_source.count("= session.run()"), 1)
        self.assertIn("Runtime.run_composed(", lab_source)
        self.assertNotIn("HarnessSession(", lab_source)
        self.assertNotIn("ManifestLoader", public_source + boundary_source)


if __name__ == "__main__":
    unittest.main()
