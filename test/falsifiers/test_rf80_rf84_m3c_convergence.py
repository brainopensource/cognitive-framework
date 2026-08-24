"""RF-80..RF-84: executable M-3C convergence falsifiers (ADR-0088)."""

from __future__ import annotations

import inspect
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.evidence.foundation import FoundationEvidenceError, EvidenceRow
from vanguard.packages.domain.ledger.reducer import compute_state_digest, reconstruct_state
from vanguard.packages.runtime.compose import Runtime as CompositionRuntime
from vanguard.packages.runtime.root import Runtime, TaskContext
from vanguard.packages.runtime import lab_driver
from vanguard.packages.runtime.authority_audit import audit_runtime_authority
from vanguard.packages.runtime.wiring import DEFAULT_BINDINGS
from vanguard.packages.ports.event_store import EventRange


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
            started = next(e for e in result.store.read().value
                           if e.payload.get("kind") == "EpisodeStarted")
            self.assertEqual(started.payload["runDigest"], result.run_digest)
            self.assertEqual(result.trajectory["run_digest"], result.run_digest)
            self.assertEqual(
                result.foundation_evidence.run_digest, result.run_digest
            )
            self.assertEqual(
                result.foundation_evidence.composition_digest,
                result.composition_digest,
            )
            store.close()
            script = (
                "import json,sys; "
                "from vanguard.packages.adapters.stores.event_store import SqliteEventStore; "
                "from vanguard.packages.ports.event_store import EventRange; "
                "s=SqliteEventStore(sys.argv[1]); "
                "xs=list(s.read(EventRange(run_id='rf80-run')).value); "
                "start=next(x for x in xs if x.payload.get('kind')=='EpisodeStarted'); "
                "print(json.dumps({'count':len(xs),'run_digest':start.payload['runDigest']}))"
            )
            cold = subprocess.run(
                [sys.executable, "-c", script, str(Path(directory) / "events.db")],
                check=True, text=True, capture_output=True,
            )
            recovered = json.loads(cold.stdout)
            self.assertGreater(recovered["count"], 0)
            self.assertEqual(recovered["run_digest"], result.run_digest)

    def test_rf83_asserted_evidence_is_not_a_valid_row_state(self) -> None:
        with self.assertRaisesRegex(FoundationEvidenceError, "derived or absent"):
            EvidenceRow(1, "real_model_invocation", status="asserted")

    def test_rf82_hard_death_fresh_process_does_not_repeat_settled_effect(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / "hard-death.db"
            writer = """
import os,sys
from test.contracts.test_b3_wal_recovery import _make_envelope
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
s=SqliteEventStore(sys.argv[1])
e1=_make_envelope(1,'hard-run','hard-project','EffectStarted',{'verb':'patch.apply','idempotency_key':'settled-key'})
e2=_make_envelope(2,'hard-run','hard-project','EffectCompleted',{'verb':'patch.apply','idempotency_key':'settled-key','outcome':'ok'},prev_digest=e1.digest())
assert s.append([e1,e2]).ok
os._exit(23)
"""
            crashed = subprocess.run([sys.executable, "-c", writer, str(db)])
            self.assertEqual(crashed.returncode, 23)
            reader = """
import json,sys
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.reducer import compute_state_digest,reconstruct_state
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.ledger.recovery import RecoveryScanner
s=SqliteEventStore(sys.argv[1]); xs=list(s.read(EventRange(project_id='hard-project')).value)
settled={e.payload.get('idempotency_key') for e in xs if e.payload.get('kind')=='EffectCompleted'}
marker=sys.argv[2]
def physical():
    open(marker,'w').write('executed')
    return 'executed'
reused,_=RecoveryScanner.continue_idempotent_effect(s,'settled-key',physical)
print(json.dumps({'count':len(xs),'reused':reused,'physical_executed':__import__('os').path.exists(marker),'chain':xs[1].prev_digest==xs[0].digest(),'state_digest':compute_state_digest(reconstruct_state(xs))}))
"""
            marker = Path(directory) / "physical-effect.marker"
            recovered = subprocess.run(
                [sys.executable, "-c", reader, str(db), str(marker)], check=True,
                text=True, capture_output=True,
            )
            report = json.loads(recovered.stdout)
            local_store = SqliteEventStore(db)
            local_events = list(local_store.read(EventRange(project_id="hard-project")).value)
            expected_state = compute_state_digest(reconstruct_state(local_events))
            self.assertEqual(report, {"count": 2, "reused": True,
                                      "physical_executed": False,
                                      "chain": True, "state_digest": expected_state})

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
        trace = audit_runtime_authority()
        self.assertTrue(trace.passed, trace.violations)
        self.assertTrue(trace.trace_digest.startswith("sha256:"))

    def test_rf84_trace_audit_detects_a_competing_runtime_caller(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "runtime").mkdir()
            (root / "runtime" / "rogue.py").write_text(
                "HarnessSession(h, p, t)\nsession.run()\n", encoding="utf-8"
            )
            trace = audit_runtime_authority(root)
            self.assertFalse(trace.passed)
            self.assertEqual(len(trace.violations), 2)


if __name__ == "__main__":
    unittest.main()
