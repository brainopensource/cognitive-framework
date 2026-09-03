"""Wave 1 Sprint 1.2/1.3 acceptance evidence (F-01, F-02, F-05–F-07, F-09–F-12, F-14, F-15)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from test.agency.doubles import ScriptedModel, finish
from test.runtime.test_harness_session import FakeClock, FakeEnvironment
from vanguard.packages.adapters.evaluators.signing import VerdictSigner
from vanguard.packages.adapters.stores.event_store import InMemoryEventStore, SqliteEventStore
from vanguard.packages.domain.ledger.reducer import reconstruct_state
from vanguard.packages.domain.selectors.resource_selector import ceiling_allows
from vanguard.packages.kernel.attenuation import Constraints, Scope, attenuate
from vanguard.packages.kernel.budget import Governor, Reservation
from vanguard.packages.kernel.model import Event
from vanguard.packages.ports.event_store import EventRange, Result
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.runtime.evaluation_listener import EvaluationListener
from vanguard.packages.runtime.ledger.recovery import RecoveryScanner
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter, WriterAuthorityError
from vanguard.packages.runtime.root import HarnessSession, Runtime, SessionPorts, TaskContext
from vanguard.packages.runtime.trajectory import assemble_trajectory

LINEAGE = (
    "project_id", "principal_id", "parent_principal_id",
    "parent_episode_id", "harness_digest",
)
SCHEMA = Path(__file__).resolve().parents[2] / "schemas" / "mhf" / "trajectory.schema.json"


def _emitter(store=None, **kwargs) -> LedgerEmitter:
    defaults = dict(
        episode_id="ep-1", project_id="proj-a", principal_id="agent-1",
        harness_digest="sha256:" + ("a" * 64), role="session",
    )
    defaults.update(kwargs)
    return LedgerEmitter(store or InMemoryEventStore(), **defaults)


def _fs(paths: tuple[str, ...] = ("/workspace",)) -> dict:
    return {"kind": "fs", "root": "/workspace", "paths": list(paths)}


class EnvelopeLineage(unittest.TestCase):
    def test_every_emitted_envelope_carries_full_lineage(self) -> None:
        emitter = _emitter()
        envelope = emitter.emit_kind(
            "EpisodeStarted", run_id="run-1", principal="agent-1",
            payload={"kind": "EpisodeStarted"})
        wire = envelope.to_mhf_dict()
        # ADR-0098 cutover: production single-writes /2. /1 stays readable.
        self.assertEqual(wire["schema_version"], "mhf.event/2")
        self.assertTrue(wire["authority_source"])
        self.assertTrue(wire["policy_version"])
        for field in LINEAGE:
            self.assertIn(field, wire)
        second = emitter.emit_kind(
            "Heartbeat", run_id="run-1", principal="agent-1",
            payload={"kind": "Heartbeat"})
        self.assertEqual(second.prev_digest, envelope.content_digest)


class WriterAuthority(unittest.TestCase):
    def test_orchestrator_cannot_append_privileged_kinds(self) -> None:
        emitter = _emitter()
        with self.assertRaises(WriterAuthorityError):
            emitter.orchestrator().emit_kind(
                "VerdictRecorded", run_id="run-1", principal="orch",
                payload={"kind": "VerdictRecorded"})
        with self.assertRaises(WriterAuthorityError):
            emitter.orchestrator().emit(Event(
                kind="CapabilityGranted", reason="forged",
                at="2026-08-20T00:00:00.000Z", run_id="run-1", principal="orch"))


class ProjectChains(unittest.TestCase):
    def test_two_projects_interleaved_keep_independent_chains(self) -> None:
        store = InMemoryEventStore()
        a = _emitter(store, project_id="proj-a")
        b = _emitter(store, project_id="proj-b")
        a1 = a.emit_kind("Heartbeat", run_id="run-a", principal="p")
        b1 = b.emit_kind("Heartbeat", run_id="run-b", principal="p")
        a2 = a.emit_kind("Heartbeat", run_id="run-a", principal="p")
        self.assertEqual(int(a1.seq), 0)
        self.assertEqual(int(b1.seq), 0)
        self.assertEqual(a2.prev_digest, a1.content_digest)


class _SignedVerifier:
    """Fake `EvaluatorPort`: a genuinely Ed25519-signed, bound verdict.

    Not a stand-in payload -- `runtime/evaluator_gateway.record_verdict`
    refuses to ledger a `VerdictRecorded` without `verdict.binding` and
    `verdict.signature` both set (ADR-0076 §5), so this is the only way to
    get a real `VerdictRecorded` onto the WAL for the cold-replay fixture.
    """

    def __init__(self, evaluation_request_id: str) -> None:
        self._signer = VerdictSigner(b"k" * 32, "eval-key-1")
        self._evaluation_request_id = evaluation_request_id

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        binding = {
            "verdict": "pass",
            "subject_digest": "sha256:" + ("c" * 64),
            "evaluation_request_id": self._evaluation_request_id,
            "oracle_id": "oracle-replay",
            "nonce": "n" * 16,
            "key_id": self._signer.key_id,
            "signed_at": "2026-08-20T00:00:00.000Z",
        }
        signature = self._signer.sign(binding)
        verdict = Verdict(
            outcome="claims", claims=(), reason="", signature=signature,
            signer_key_id=self._signer.key_id, binding=binding,
        )
        return Result.success(verdict)


class ColdReplayParity(unittest.TestCase):
    def test_cold_reader_reconstructs_live_state_from_disk(self) -> None:
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
                    verifier=_SignedVerifier("eval-replay-1"),
                    interactive=False,
                ),
                TaskContext(
                    brief="replay", repo_path=Path("/workspace"),
                    run_id="run-replay-1", episode_id="ep-replay-1",
                    principal="agent-1", project_id="proj-replay",
                ),
            )
            session.run()
            live_state = session.ledger_state()
            live_digest = session.state_digest()
            self.assertGreater(live_store.count(), 0)
            # The verdict actually reduced into *live* state, not just
            # ledgered -- otherwise a cold/live match would prove nothing.
            self.assertIn("eval-replay-1", live_state.verdicts)
            self.assertEqual(live_state.verdicts["eval-replay-1"].verdict, "pass")
            live_store.close()
            cold_store = SqliteEventStore(db)
            envelopes = list(cold_store.read(EventRange()).value or ())
            cold_state = reconstruct_state(envelopes)
            cold_store.close()
            self.assertEqual(live_state.episode.status, cold_state.episode.status)
            self.assertEqual(dict(live_state.grants), dict(cold_state.grants))
            # I-4: the signed verdict is evidence, not decoration -- a fresh
            # process folding the same WAL from disk must reconstruct it,
            # not lose it to `unknown_events` (M-2).
            self.assertIn("eval-replay-1", cold_state.verdicts)
            self.assertEqual(
                cold_state.verdicts["eval-replay-1"].signature,
                live_state.verdicts["eval-replay-1"].signature,
            )
            self.assertEqual(cold_state.unknown_events, ())
            self.assertEqual(live_digest, cold_state.digest())


class BranchResume(unittest.TestCase):
    """SPEC §1.3: "fold to `seq=N` + resume with a divergent `branch_id`".

    Absorbed at 2.2-A from `test/layer0/events/test_fold.py`, which held the
    only executable evidence for this law. KEEP, not KILL: the envelope
    already carried `branch_id`, but the reducer dropped it, so a fold of the
    trunk and a fold of a divergent branch reduced to the same state and the
    same digest — the one thing time-travel debugging must be able to tell
    apart.
    """

    def _envelope(self, emitter, kind, branch):
        envelope = emitter.emit_kind(kind, run_id="run-b", principal="agent-1",
                                     payload={"kind": kind})
        return replace(envelope, mhf_branch_id=branch)

    def test_a_resumed_branch_is_distinguishable_from_the_trunk(self) -> None:
        emitter = _emitter(episode_id="ep-branch")
        prefix = [self._envelope(emitter, "EpisodeStarted", "main"),
                  self._envelope(emitter, "TurnStarted", "main")]
        trunk = reconstruct_state(prefix + [self._envelope(emitter, "TurnStarted", "main")])
        forked = reconstruct_state(prefix + [self._envelope(emitter, "TurnStarted", "alt")])

        self.assertEqual(trunk.branch_id, "main")
        self.assertEqual(forked.branch_id, "alt")
        self.assertEqual(trunk.event_count, forked.event_count)
        self.assertNotEqual(
            trunk.digest(), forked.digest(),
            "a divergent branch that folds to the trunk's digest is untraceable")

    def test_folding_to_seq_n_is_a_prefix_of_the_whole(self) -> None:
        emitter = _emitter(episode_id="ep-seq")
        events = [self._envelope(emitter, "TurnStarted", "main") for _ in range(4)]
        self.assertEqual(reconstruct_state(events[:2]).event_count, 2)
        self.assertEqual(reconstruct_state(events).event_count, 4)
        self.assertEqual(reconstruct_state(events[:2]).last_seq, events[1].seq)


class DurableIntent(unittest.TestCase):
    def test_intent_survives_process_death(self) -> None:
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
            recovered = RecoveryScanner().reconcile_open_intents(
                store, occurred_at="2026-08-20T00:01:00.000Z")
            self.assertEqual(len(recovered), 1)
            self.assertEqual(recovered[0].payload.get("status"), "undeterminable")
            store.close()


class ListenerUsesEmitter(unittest.TestCase):
    def test_listener_output_matches_emitter_schema(self) -> None:
        store = InMemoryEventStore()
        emitter = _emitter(store)
        completed = emitter.emit_kind(
            "EpisodeCompleted", run_id="run-001", principal="agent-1",
            payload={"kind": "EpisodeCompleted"})
        out = EvaluationListener(store, emitter=emitter).process_envelope(completed)
        self.assertIsNotNone(out)
        assert out is not None
        self.assertEqual(out.to_mhf_dict()["kind"], "EvaluationRequested")
        self.assertEqual(out.prev_digest, completed.content_digest)


class IdentityAndCeilings(unittest.TestCase):
    def test_prompt_or_ceiling_change_changes_digest(self) -> None:
        first = Runtime.compose("vg-code-default", episode_id="e-a")
        again = Runtime.compose("vg-code-default", episode_id="e-b")
        self.assertEqual(first.composition_digest, again.composition_digest)
        identity = dict(first.frozen.identity)
        identity["systemPrompt"] = identity.get("systemPrompt", "") + "\n# changed"
        from vanguard.packages.domain.canonicalisation.digest import digest_of
        changed = digest_of({**first.frozen.identity_preimage(), **identity})
        self.assertNotEqual(first.composition_digest, changed)

    def test_declared_ceiling_survives_compilation_and_denies(self) -> None:
        harness = Runtime.compose("vg-code-default")
        self.assertTrue(harness.capability_ceiling)
        denied = ceiling_allows(
            harness.capability_ceiling,
            {"kind": "fs", "root": "/etc", "paths": ["/etc/passwd"]})
        self.assertFalse(denied.included)
        # 1.3-B: the ceiling is the JCS-canonical *text* the manifest
        # declared (`CapabilityRequirement.selector`), not a parsed object --
        # a within-grant request must still be recognised through it.
        allowed = ceiling_allows(
            harness.capability_ceiling,
            {"kind": "fs", "root": "/workspace", "paths": ["/workspace/a.py"]})
        self.assertTrue(allowed.included)
        # `proc.exec`'s own declared `generic` selector is part of the same
        # ceiling -- never covered by a blanket filesystem grant.
        proc_allowed = ceiling_allows(
            harness.capability_ceiling,
            {"kind": "generic", "uriPattern": "proc://exec/allow/git,pytest,ruff,python3"})
        self.assertTrue(proc_allowed.included)

    def test_empty_ceiling_denies_everything(self) -> None:
        decision = ceiling_allows((), _fs())
        self.assertFalse(decision.included)
        self.assertEqual(decision.reason, "empty_ceiling")


class BudgetAlgebra(unittest.TestCase):
    def test_child_grant_wider_than_parent_is_denied_whole(self) -> None:
        parent = Scope(
            actions=frozenset({"fs.read"}),
            resources=(_fs(),),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=4, budget_usd_micros=1000, max_bytes=100, max_depth=3),
            depth=0,
        )
        child = Scope(
            actions=frozenset({"fs.read"}),
            resources=(_fs(),),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=4, budget_usd_micros=1000, max_bytes=None, max_depth=3),
            depth=1,
        )
        result = attenuate(parent, child)
        self.assertFalse(result.ok)

    def test_sibling_depths_are_not_summed(self) -> None:
        parent = Scope(
            actions=frozenset({"fs.read"}),
            resources=(_fs(),),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=8, budget_usd_micros=10_000, max_depth=2),
            depth=0,
        )
        request = Scope(
            actions=frozenset({"fs.read"}),
            resources=(_fs(),),
            constraints=parent.constraints,
            depth=1,
        )
        first = attenuate(parent, request)
        second = attenuate(parent, request)
        self.assertTrue(first.ok and second.ok)
        self.assertEqual(first.granted.depth, 1)
        self.assertEqual(second.granted.depth, 1)

    def test_child_budget_debits_parent_remaining(self) -> None:
        gov = Governor({"usd_micros": 1000})
        parent = gov.reserve("run", Reservation(usd_micros=400))
        child = gov.reserve("run", Reservation(usd_micros=100), parent_lease_id=parent.lease_id)
        gov.commit(child, {"usd_micros": 100})
        gov.release(child)
        self.assertEqual(gov.remaining("usd_micros"), 500)


class TrajectoryEmission(unittest.TestCase):
    def test_episode_completed_emits_schema_valid_mhf_trajectory_1(self) -> None:
        harness = Runtime.compose("vg-code-default", episode_id="ep-traj")
        session = HarnessSession(
            harness,
            SessionPorts(
                model=ScriptedModel([finish()]),
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                interactive=False,
            ),
            TaskContext(
                brief="traj", repo_path=Path("/workspace"),
                run_id="run-traj", episode_id="ep-traj", principal="agent-1",
            ),
        )
        result = session.run()
        self.assertIsNotNone(result.trajectory)
        row = result.trajectory
        assert row is not None
        self.assertEqual(row["schema"], "mhf.trajectory/2")
        schema_v2 = json.loads((SCHEMA.parent / "trajectory_v2.schema.json").read_text(encoding="utf-8"))
        for key in schema_v2["required"]:
            self.assertIn(key, row)
        aborted = assemble_trajectory(
            task=session.task, harness_digest=harness.composition_digest,
            terminal="abandoned", receipts=(), contexts=(),
            events=(), verdict=None)
        self.assertIsNone(aborted["verdict"])
        completed = [
            e for e in (session.ports.store.read(EventRange()).value or ())
            if (e.payload.get("kind") or e.mhf_kind) == "EpisodeCompleted"
        ]
        self.assertTrue(completed)
        self.assertEqual(completed[-1].payload.get("trajectory", {}).get("schema"),
                         "mhf.trajectory/2")


if __name__ == "__main__":
    unittest.main()
