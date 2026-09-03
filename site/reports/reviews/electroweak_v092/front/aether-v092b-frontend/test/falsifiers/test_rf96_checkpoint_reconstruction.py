"""RF-96: cold reconstruction, and the checkpoint that may only accelerate it.

`ADR-0096 §13`: "a conforming execution survives process destruction and
rebuilds without depending on inaccessible authoritative object state". The
checkpoint is the thing most likely to violate that quietly -- not by failing,
but by succeeding with the wrong state. Every test here is written to fail if
a checkpoint is ever believed without proof.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from vanguard.packages.adapters.stores.blob_store import FileBlobStore, InMemoryBlobStore
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.domain.ledger.reducer import (
    REDUCER_VERSION,
    initial_state,
    reduce_batch,
)
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.checkpoints import (
    CHECKPOINT_SCHEMA_VERSION,
    Checkpoint,
    CheckpointManager,
    CheckpointPins,
    CheckpointValidationError,
    decode_state,
    encode_state,
)

ROOT = Path(__file__).resolve().parents[2]


def _event(seq: int, kind: str, payload: dict, *, version: str = "mhf.event/2") -> EventEnvelope:
    body = {"kind": kind, **payload}
    return EventEnvelope(
        schema_version=version,
        event_id=f"0192f0a0-0000-7000-8000-{seq:012d}",
        scope="episode",
        seq=str(seq),
        occurred_at="2026-08-25T12:00:00.000Z",
        recorded_at="2026-08-25T12:00:00.000Z",
        principal="agent-rf96",
        principal_role="episode",
        tenant_id="tenant-default",
        owner_id="owner-platform",
        confidentiality="internal",
        retention_class="extended",
        trainability="prohibited",
        redaction_status="none",
        payload=body,
        run_id="run-rf96",
        episode_id="ep-rf96",
        project_id="project-rf96",
        mhf_kind=kind,
        authority_source="kernel-capability" if version == "mhf.event/2" else None,
        policy_version="policy/1" if version == "mhf.event/2" else None,
    )


def _history() -> list[EventEnvelope]:
    """A history that exercises every family the reducer folds into a record."""
    return [
        _event(1, "EpisodeStarted", {"episodeId": "ep-rf96", "runId": "run-rf96"},
               version="mhf.event/1"),
        _event(2, "GoalDeclared", {"goalDigest": "sha256:" + "a" * 64,
                                   "episodeId": "ep-rf96"}),
        _event(3, "BudgetReserved", {"leaseId": "lease-1",
                                     "dimensions": {"tokens": 100},
                                     "limits": {"tokens": 100}}),
        _event(4, "CapabilityGranted", {"grantId": "grant-1", "authority": ["fs.read"]}),
        _event(5, "EffectStarted", {"idempotencyKey": "eff-1",
                                    "descriptorDigest": "sha256:" + "b" * 64}),
        _event(6, "EffectCompleted", {"idempotencyKey": "eff-1",
                                      "descriptorDigest": "sha256:" + "b" * 64,
                                      "receiptDigest": "sha256:" + "c" * 64,
                                      "outcome": "ok"}),
        _event(7, "PlanRevised", {"planDigest": "sha256:" + "d" * 64, "revision": 1}),
        _event(8, "ProgressAssessed", {"assessment": "on_track", "turn": 2}),
        _event(9, "BudgetCommitted", {"leaseId": "lease-1", "debits": {"tokens": 40}}),
        _event(10, "ContextCompacted", {"inputDigest": "sha256:" + "e" * 64,
                                        "outputDigest": "sha256:" + "f" * 64}),
    ]


class StateRoundTripsLosslessly(unittest.TestCase):
    """If encoding drops a field, every later proof is proving the wrong state."""

    def test_a_populated_state_survives_encode_decode_by_digest(self) -> None:
        state = reduce_batch(initial_state(), _history())
        self.assertEqual(decode_state(encode_state(state)).digest(), state.digest())

    def test_the_round_trip_preserves_every_declared_field(self) -> None:
        state = reduce_batch(initial_state(), _history())
        restored = decode_state(encode_state(state))
        self.assertEqual(restored.effects.keys(), state.effects.keys())
        self.assertEqual(restored.leases.keys(), state.leases.keys())
        self.assertEqual(restored.goals, state.goals)
        self.assertEqual(restored.plan_revisions, state.plan_revisions)
        self.assertEqual(restored.context_compactions, state.context_compactions)
        self.assertEqual(restored.episode.status, state.episode.status)

    def test_the_canonical_digest_form_is_not_used_as_the_blob(self) -> None:
        # `to_canonical_dict` is built for the digest and is lossy; a
        # checkpoint that stored it would decode to a smaller state.
        state = reduce_batch(initial_state(), _history())
        self.assertNotEqual(encode_state(state)["state"], state.to_canonical_dict())


class CheckpointParityWithColdFold(unittest.TestCase):
    """`from_checkpoint` must be indistinguishable from `full_cold`."""

    def setUp(self) -> None:
        self.blobs = InMemoryBlobStore()
        self.manager = CheckpointManager(self.blobs)
        self.events = _history()

    def test_a_checkpoint_plus_tail_equals_the_full_cold_fold(self) -> None:
        head, tail = self.events[:6], self.events
        checkpoint = self.manager.capture(reduce_batch(initial_state(), head))
        assert checkpoint is not None
        warm = self.manager.reconstruct(tail, checkpoint=checkpoint)
        cold = self.manager.reconstruct(tail)
        self.assertEqual(warm.capability, "from_checkpoint")
        self.assertEqual(cold.capability, "full_cold")
        self.assertEqual(warm.state_digest, cold.state_digest)

    def test_only_the_tail_is_replayed(self) -> None:
        checkpoint = self.manager.capture(reduce_batch(initial_state(), self.events[:6]))
        assert checkpoint is not None
        warm = self.manager.reconstruct(self.events, checkpoint=checkpoint)
        self.assertEqual(warm.events_replayed, 4)

    def test_verification_requires_the_executed_parity_comparison(self) -> None:
        checkpoint = self.manager.capture(reduce_batch(initial_state(), self.events[:6]))
        assert checkpoint is not None
        unverified = self.manager.reconstruct(self.events, checkpoint=checkpoint)
        verified = self.manager.reconstruct(
            self.events, checkpoint=checkpoint, verify=True)
        # C-04: loading cleanly is capability, never verification.
        self.assertEqual(unverified.verification, "unverified")
        self.assertEqual(verified.verification, "verified")

    def test_a_cold_fold_is_never_reported_as_verified(self) -> None:
        self.assertEqual(self.manager.reconstruct(self.events).verification, "unverified")

    def test_an_empty_history_is_undeterminable_not_an_empty_state(self) -> None:
        outcome = self.manager.reconstruct([])
        self.assertEqual(outcome.capability, "none")
        self.assertIsNone(outcome.state)


class ACorruptCheckpointFailsClosedToTheColdFold(unittest.TestCase):
    """Every rejection lands on the slow correct answer, never on a wrong one."""

    def setUp(self) -> None:
        self.blobs = InMemoryBlobStore()
        self.manager = CheckpointManager(self.blobs)
        self.events = _history()
        self.truth = reduce_batch(initial_state(), self.events).digest()
        self.checkpoint = self.manager.capture(
            reduce_batch(initial_state(), self.events[:6]))
        assert self.checkpoint is not None

    def _assert_cold_fallback(self, checkpoint: Checkpoint, marker: str) -> None:
        outcome = self.manager.reconstruct(self.events, checkpoint=checkpoint)
        self.assertEqual(outcome.capability, "full_cold")
        self.assertEqual(outcome.state_digest, self.truth)
        self.assertIn(marker, outcome.fallback_reason)
        self.assertIsNone(outcome.checkpoint)

    def test_an_absent_blob_falls_back(self) -> None:
        self._assert_cold_fallback(
            replace(self.checkpoint, blob_digest="sha256:" + "0" * 64), "absent")

    def test_bytes_that_do_not_hash_to_their_address_fall_back(self) -> None:
        # A store whose addresses lie. `has()` says yes and the bytes are wrong.
        self.blobs._blobs[self.checkpoint.blob_digest] = b'{"state": {}}'
        self._assert_cold_fallback(self.checkpoint, "digest mismatch")

    def test_a_state_digest_that_does_not_recompute_falls_back(self) -> None:
        self._assert_cold_fallback(
            replace(self.checkpoint, state_digest="sha256:" + "9" * 64),
            "state digest mismatch")

    def test_a_reducer_pin_mismatch_falls_back(self) -> None:
        pins = replace(self.checkpoint.pins, reducer_version="v0.9.0")
        self._assert_cold_fallback(replace(self.checkpoint, pins=pins), "reducer pin")

    def test_an_event_schema_pin_mismatch_falls_back(self) -> None:
        pins = replace(self.checkpoint.pins, event_schema_version="mhf.event/1")
        self._assert_cold_fallback(
            replace(self.checkpoint, pins=pins), "event schema pin")

    def test_a_checkpoint_schema_pin_mismatch_falls_back(self) -> None:
        pins = replace(self.checkpoint.pins, checkpoint_schema_version="mhf.checkpoint/9")
        self._assert_cold_fallback(
            replace(self.checkpoint, pins=pins), "checkpoint schema pin")

    def test_undecodable_bytes_fall_back(self) -> None:
        broken = self.blobs.put(b"not json at all").value
        self._assert_cold_fallback(
            replace(self.checkpoint, blob_digest=str(broken),
                    state_digest=self.checkpoint.state_digest),
            "decodable JSON")

    def test_a_checkpoint_folded_from_a_different_history_loses_to_the_events(self) -> None:
        # The dangerous case: internally consistent, externally wrong. Only
        # the executed parity comparison catches it.
        divergent = reduce_batch(initial_state(), self.events[:3] + self.events[7:])
        forged = self.manager.capture(divergent)
        assert forged is not None
        forged = replace(forged, last_seq=6)
        outcome = self.manager.reconstruct(
            self.events, checkpoint=forged, verify=True)
        self.assertEqual(outcome.capability, "full_cold")
        self.assertEqual(outcome.verification, "unverified")
        self.assertTrue(
            outcome.fallback_reason.startswith(
                ("parity_mismatch", "checkpoint_not_a_prefix")),
            outcome.fallback_reason)
        self.assertEqual(outcome.state_digest, self.truth)

    def test_load_still_reports_the_reason_to_a_caller_that_wants_it(self) -> None:
        with self.assertRaises(CheckpointValidationError):
            self.manager.load(replace(self.checkpoint, state_digest="sha256:" + "9" * 64))


class CheckpointCaptureIsAnOrdinaryArtifact(unittest.TestCase):
    """No second durability mechanism: blob first, store computes the address."""

    def test_capture_flows_through_the_artifact_writer_when_one_is_given(self) -> None:
        from vanguard.packages.runtime.artifacts import ArtifactWriter, CapturePolicy

        blobs = InMemoryBlobStore()
        emitted: list = []

        class Emitter:
            def emit_kind(self, kind, **kwargs):
                emitted.append((kind, kwargs))
                return None

        writer = ArtifactWriter(
            blobs, Emitter(), policy=CapturePolicy(retention="standard"),
            run_id="run-rf96", principal="agent-rf96")
        manager = CheckpointManager(blobs, artifacts=writer)
        checkpoint = manager.capture(reduce_batch(initial_state(), _history()))
        assert checkpoint is not None
        self.assertTrue(blobs.has(checkpoint.blob_digest))
        self.assertEqual([ref.role for ref in writer.index], ["checkpoint_state"])
        self.assertTrue(emitted)

    def test_digests_only_retention_yields_no_checkpoint_rather_than_a_dangling_one(self) -> None:
        from vanguard.packages.runtime.artifacts import ArtifactWriter, CapturePolicy

        blobs = InMemoryBlobStore()

        class Emitter:
            def emit_kind(self, kind, **kwargs):
                return None

        writer = ArtifactWriter(
            blobs, Emitter(), policy=CapturePolicy(retention="digests_only"),
            run_id="run-rf96", principal="agent-rf96")
        manager = CheckpointManager(blobs, artifacts=writer)
        self.assertIsNone(manager.capture(reduce_batch(initial_state(), _history())))

    def test_a_run_without_a_checkpoint_still_reconstructs(self) -> None:
        manager = CheckpointManager(InMemoryBlobStore())
        outcome = manager.reconstruct(_history(), checkpoint=None)
        self.assertEqual(outcome.capability, "full_cold")
        self.assertEqual(outcome.fallback_reason, "")

    def test_the_fact_carries_digests_and_no_state(self) -> None:
        manager = CheckpointManager(InMemoryBlobStore())
        checkpoint = manager.capture(reduce_batch(initial_state(), _history()))
        assert checkpoint is not None
        fact = checkpoint.to_fact()
        serialised = json.dumps(fact)
        self.assertNotIn("sha256:" + "a" * 64, serialised.replace(
            checkpoint.state_digest, ""))
        self.assertEqual(Checkpoint.from_fact(fact), checkpoint)
        self.assertEqual(fact["pins"]["reducerVersion"], REDUCER_VERSION)


_FRESH_RECONSTRUCTOR = r"""
import sys
from vanguard.packages.adapters.stores.blob_store import FileBlobStore
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.checkpoints import Checkpoint, CheckpointManager
import json

db, blob_root, fact_path = sys.argv[1], sys.argv[2], sys.argv[3]
store = SqliteEventStore(db)
read = store.read(EventRange(project_id="project-rf96"))
events = list(read.value or [])
manager = CheckpointManager(FileBlobStore(blob_root))
checkpoint = Checkpoint.from_fact(json.loads(open(fact_path).read()))
outcome = manager.reconstruct(events, checkpoint=checkpoint, verify=True)
print(json.dumps({
    "capability": outcome.capability,
    "verification": outcome.verification,
    "digest": outcome.state_digest,
    "replayed": outcome.events_replayed,
    "reason": outcome.fallback_reason,
}))
"""


class FreshProcessReconstruction(unittest.TestCase):
    """RF-96 proper: no process-local object survives, and the state still rebuilds."""

    def test_a_second_process_rebuilds_the_same_state_from_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "rf96.sqlite")
            blob_root = str(Path(tmp) / "blobs")
            fact_path = Path(tmp) / "checkpoint.json"

            store = SqliteEventStore(db)
            events = _history()
            appended = store.append(events)
            self.assertTrue(appended.ok, appended.error)

            blobs = FileBlobStore(blob_root)
            manager = CheckpointManager(blobs)
            checkpoint = manager.capture(reduce_batch(initial_state(), events[:6]))
            assert checkpoint is not None
            fact_path.write_text(json.dumps(checkpoint.to_fact()))
            expected = reduce_batch(initial_state(), events).digest()

            result = subprocess.run(
                [sys.executable, "-c", _FRESH_RECONSTRUCTOR, db, blob_root, str(fact_path)],
                capture_output=True, text=True, cwd=str(ROOT), timeout=180)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout.strip().splitlines()[-1])

        self.assertEqual(payload["capability"], "from_checkpoint")
        self.assertEqual(payload["verification"], "verified")
        self.assertEqual(payload["digest"], expected)
        self.assertEqual(payload["reason"], "")

    def test_a_second_process_with_a_destroyed_blob_still_rebuilds_cold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = str(Path(tmp) / "rf96.sqlite")
            blob_root = Path(tmp) / "blobs"
            fact_path = Path(tmp) / "checkpoint.json"

            store = SqliteEventStore(db)
            events = _history()
            self.assertTrue(store.append(events).ok)

            manager = CheckpointManager(FileBlobStore(str(blob_root)))
            checkpoint = manager.capture(reduce_batch(initial_state(), events[:6]))
            assert checkpoint is not None
            fact_path.write_text(json.dumps(checkpoint.to_fact()))
            expected = reduce_batch(initial_state(), events).digest()

            # The cache is destroyed between processes. The events are not.
            for path in blob_root.rglob("*"):
                if path.is_file():
                    path.unlink()

            result = subprocess.run(
                [sys.executable, "-c", _FRESH_RECONSTRUCTOR, db, str(blob_root),
                 str(fact_path)],
                capture_output=True, text=True, cwd=str(ROOT), timeout=180)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout.strip().splitlines()[-1])

        self.assertEqual(payload["capability"], "full_cold")
        self.assertEqual(payload["digest"], expected)
        self.assertIn("absent", payload["reason"])


class CheckpointPerformance(unittest.TestCase):
    """A checkpoint that does not reduce replayed work is a liability, not a cache."""

    def test_replayed_event_count_falls_with_checkpoint_depth(self) -> None:
        blobs = InMemoryBlobStore()
        manager = CheckpointManager(blobs)
        events = [
            _event(i, "ProgressAssessed", {"assessment": "on_track", "turn": i})
            for i in range(1, 501)
        ]
        cold = manager.reconstruct(events)
        checkpoint = manager.capture(reduce_batch(initial_state(), events[:450]))
        assert checkpoint is not None
        warm = manager.reconstruct(events, checkpoint=checkpoint, verify=True)

        self.assertEqual(cold.events_replayed, 500)
        self.assertEqual(warm.events_replayed, 50)
        self.assertEqual(warm.verification, "verified")
        self.assertEqual(warm.state_digest, cold.state_digest)


if __name__ == "__main__":
    unittest.main()


class RuntimeIntegration(unittest.TestCase):
    """The session seam: a real run, checkpointed and rebuilt from its own ledger."""

    def _session(self, blobs):
        from test.agency.doubles import ScriptedModel, finish
        from test.runtime.test_harness_session import FakeClock, FakeEnvironment
        from vanguard.packages.adapters.stores.event_store import SqliteEventStore
        from vanguard.packages.runtime.artifacts import CapturePolicy
        from vanguard.packages.runtime.root import (
            HarnessSession, Runtime, SessionPorts, TaskContext,
        )

        harness = Runtime.compose("vg-code-default", episode_id="ep-rf96-rt")
        ports = SessionPorts(
            model=ScriptedModel([finish("done")]), environment=FakeEnvironment(),
            clock=FakeClock(), store=SqliteEventStore(":memory:"),
            interactive=False, blobs=blobs,
            capture_policy=CapturePolicy(retention="standard"))
        task = TaskContext(
            brief="checkpoint the fold", repo_path=Path("/workspace"),
            run_id="run-rf96-rt", episode_id="ep-rf96-rt",
            principal="agent-1", max_turns=2)
        return HarnessSession(harness, ports, task)

    def test_a_session_checkpoints_and_rebuilds_to_the_same_digest(self) -> None:
        blobs = InMemoryBlobStore()
        session = self._session(blobs)
        session.run()

        checkpoint = session.checkpoint()
        self.assertIsNotNone(checkpoint)
        # Taking the checkpoint is itself an artifact capture, so it appends
        # facts. The truth is the fold *after* those, and the tail replay is
        # what has to pick them up.
        expected = session.state_digest()
        outcome = session.reconstruct(verify=True)
        self.assertEqual(outcome.capability, "from_checkpoint")
        self.assertEqual(outcome.verification, "verified")
        self.assertEqual(outcome.state_digest, expected)

    def test_a_session_without_a_blob_store_cold_folds_rather_than_failing(self) -> None:
        session = self._session(None)
        session.run()
        self.assertIsNone(session.checkpoints)
        self.assertIsNone(session.checkpoint())
        outcome = session.reconstruct()
        self.assertEqual(outcome.capability, "full_cold")
        self.assertEqual(outcome.verification, "unverified")
        self.assertEqual(outcome.state_digest, session.state_digest())

    def test_a_session_whose_checkpoint_blob_vanished_still_rebuilds(self) -> None:
        blobs = InMemoryBlobStore()
        session = self._session(blobs)
        session.run()
        checkpoint = session.checkpoint()
        assert checkpoint is not None
        expected = session.state_digest()
        blobs._blobs.pop(checkpoint.blob_digest)

        outcome = session.reconstruct()
        self.assertEqual(outcome.capability, "full_cold")
        self.assertEqual(outcome.state_digest, expected)
        self.assertIn("absent", outcome.fallback_reason)
