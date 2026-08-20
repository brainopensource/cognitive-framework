"""Sprint 1.2 ledger truth (F-01, F-02, F-05, F-14)."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.stores.event_store import InMemoryEventStore, SqliteEventStore
from vanguard.packages.domain.ledger.reducer import reconstruct_state
from vanguard.packages.kernel.model import Event
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.evaluation_listener import EvaluationListener
from vanguard.packages.runtime.ledger.recovery import RecoveryScanner
from vanguard.packages.runtime.ledger_emitter import (
    LedgerEmitter,
    WriterAuthorityError,
)
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext

LINEAGE = (
    "project_id",
    "principal_id",
    "parent_principal_id",
    "parent_episode_id",
    "harness_digest",
)


def _emitter(store=None, **kwargs) -> LedgerEmitter:
    defaults = dict(
        episode_id="ep-1",
        project_id="proj-a",
        principal_id="agent-1",
        harness_digest="sha256:" + ("a" * 64),
        role="session",
    )
    defaults.update(kwargs)
    return LedgerEmitter(store or InMemoryEventStore(), **defaults)


class EnvelopeLineage(unittest.TestCase):
    def test_every_emitted_envelope_carries_full_lineage(self) -> None:
        """F-01."""
        emitter = _emitter()
        envelope = emitter.emit_kind(
            "EpisodeStarted",
            run_id="run-1",
            principal="agent-1",
            payload={"kind": "EpisodeStarted"},
        )
        wire = envelope.to_mhf_dict()
        self.assertEqual(wire["schema_version"], "mhf.event/1")
        for field in LINEAGE:
            self.assertIn(field, wire)
        self.assertEqual(wire["project_id"], "proj-a")
        self.assertEqual(wire["principal_id"], "agent-1")
        self.assertEqual(wire["harness_digest"], "sha256:" + ("a" * 64))
        self.assertRegex(wire["digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertIsNone(wire["prev_digest"])

        second = emitter.emit_kind(
            "Heartbeat",
            run_id="run-1",
            principal="agent-1",
            payload={"kind": "Heartbeat"},
        )
        self.assertEqual(second.prev_digest, envelope.content_digest)
        self.assertEqual(int(second.seq), int(envelope.seq) + 1)


class WriterAuthority(unittest.TestCase):
    def test_orchestrator_cannot_append_privileged_kinds(self) -> None:
        """F-05."""
        emitter = _emitter()
        orch = emitter.orchestrator()
        with self.assertRaises(WriterAuthorityError):
            orch.emit_kind(
                "VerdictRecorded",
                run_id="run-1",
                principal="orchestrator",
                payload={"kind": "VerdictRecorded", "verdict": "pass"},
            )
        with self.assertRaises(WriterAuthorityError):
            orch.emit(Event(
                kind="CapabilityGranted",
                reason="forged",
                at="2026-08-20T00:00:00.000Z",
                run_id="run-1",
                principal="orchestrator",
            ))
        self.assertEqual(emitter.store.count(), 0)
        gateway = emitter.evaluator_gateway()
        recorded = gateway.emit_kind(
            "VerdictRecorded",
            run_id="run-1",
            principal="evaluator-gateway",
            payload={"kind": "VerdictRecorded"},
        )
        self.assertEqual(recorded.mhf_kind, "VerdictRecorded")


class ProjectChains(unittest.TestCase):
    def test_two_projects_interleaved_keep_independent_chains(self) -> None:
        """1.2-C: seq/prev_digest are per project_id (config-declared)."""
        store = InMemoryEventStore()
        a = _emitter(store, project_id="proj-a")
        b = _emitter(store, project_id="proj-b")
        a1 = a.emit_kind("Heartbeat", run_id="run-a", principal="p")
        b1 = b.emit_kind("Heartbeat", run_id="run-b", principal="p")
        a2 = a.emit_kind("Heartbeat", run_id="run-a", principal="p")
        b2 = b.emit_kind("Heartbeat", run_id="run-b", principal="p")
        self.assertEqual(int(a1.seq), 0)
        self.assertEqual(int(b1.seq), 0)
        self.assertEqual(int(a2.seq), 1)
        self.assertEqual(int(b2.seq), 1)
        self.assertEqual(a2.prev_digest, a1.content_digest)
        self.assertEqual(b2.prev_digest, b1.content_digest)
        self.assertNotEqual(a2.prev_digest, b2.prev_digest)


class ColdReplayParity(unittest.TestCase):
    def test_cold_reader_reconstructs_live_state_from_disk(self) -> None:
        """F-02 / I-4: fold from a fresh process-equivalent store, not the same list twice."""
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "ledger.sqlite3"
            live_store = SqliteEventStore(db)
            harness = Runtime.compose("vg-code-default", episode_id="ep-replay-1")
            session = HarnessSession(
                harness,
                SessionPorts(
                    model=ScriptedModel([finish()]),
                    environment=FakeEnvironment(),
                    clock=FakeClock(),
                    store=live_store,
                    interactive=False,
                ),
                TaskContext(
                    brief="replay",
                    repo_path=Path("/workspace"),
                    run_id="run-replay-1",
                    episode_id="ep-replay-1",
                    principal="agent-1",
                    project_id="proj-replay",
                ),
            )
            session.run()
            live_state = session.ledger_state()
            live_digest = session.state_digest()
            self.assertGreater(live_store.count(), 0)
            live_store.close()

            cold_store = SqliteEventStore(db)
            read = cold_store.read(EventRange())
            self.assertTrue(read.ok)
            envelopes = list(read.value or ())
            self.assertGreater(len(envelopes), 0)
            self.assertTrue(all(e.schema_version == "mhf.event/1" for e in envelopes))
            cold_state = reconstruct_state(envelopes)
            cold_store.close()

            self.assertEqual(live_state.episode.status, cold_state.episode.status)
            self.assertEqual(dict(live_state.grants), dict(cold_state.grants))
            self.assertEqual(
                {k: (v.lease_id, dict(v.dimensions), v.is_released)
                 for k, v in live_state.leases.items()},
                {k: (v.lease_id, dict(v.dimensions), v.is_released)
                 for k, v in cold_state.leases.items()},
            )
            self.assertEqual(
                [(k, a.status) for k, a in live_state.approvals.items()],
                [(k, a.status) for k, a in cold_state.approvals.items()],
            )
            self.assertEqual(live_digest, cold_state.digest())


class DurableIntent(unittest.TestCase):
    def test_intent_survives_process_death(self) -> None:
        """F-14: kill between S8a and S9; recovery reconciles to undeterminable."""
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "intent.sqlite3"
            child = r"""
import os, sys
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.kernel.model import Event
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter
store = SqliteEventStore(sys.argv[1])
emitter = LedgerEmitter(
    store, episode_id="ep-crash", project_id="proj-crash",
    principal_id="agent-1", harness_digest="sha256:" + ("b" * 64),
    role="kernel")
emitter.append_intent(Event(
    kind="EffectStarted", reason="s8a", at="2026-08-20T00:00:00.000Z",
    run_id="run-crash", principal="agent-1",
    payload={"kind": "EffectStarted", "idempotencyKey": "fx-1"}))
os._exit(1)
"""
            proc = subprocess.run(
                [sys.executable, "-c", child, str(db)],
                cwd=str(Path(__file__).resolve().parents[2]),
                env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2])},
            )
            self.assertNotEqual(proc.returncode, 0)
            store = SqliteEventStore(db)
            kinds = [
                (e.payload.get("kind") or e.mhf_kind)
                for e in (store.read(EventRange()).value or ())
            ]
            self.assertIn("EffectStarted", kinds)
            self.assertNotIn("EffectCompleted", kinds)
            recovered = RecoveryScanner().reconcile_open_intents(
                store, occurred_at="2026-08-20T00:01:00.000Z")
            self.assertEqual(len(recovered), 1)
            self.assertEqual(recovered[0].payload.get("status"), "undeterminable")
            store.close()


class ListenerUsesEmitter(unittest.TestCase):
    def test_listener_output_matches_emitter_schema(self) -> None:
        """1.2-F."""
        store = InMemoryEventStore()
        emitter = _emitter(store)
        completed = emitter.emit_kind(
            "EpisodeCompleted",
            run_id="run-001",
            principal="agent-1",
            payload={"kind": "EpisodeCompleted", "evaluationProtocol": "oracle_green"},
        )
        listener = EvaluationListener(store, emitter=emitter)
        out = listener.process_envelope(completed)
        self.assertIsNotNone(out)
        assert out is not None
        wire = out.to_mhf_dict()
        self.assertEqual(wire["schema_version"], "mhf.event/1")
        self.assertEqual(wire["kind"], "EvaluationRequested")
        self.assertEqual(wire["seq"], int(completed.seq) + 1)
        self.assertEqual(wire["prev_digest"], completed.content_digest)
        for field in LINEAGE:
            self.assertIn(field, wire)


if __name__ == "__main__":
    unittest.main()
