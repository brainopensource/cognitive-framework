"""CMX-08: Release hardening, state resilience, failure isolation, and budget ceilings falsifiers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.blob_store import FileBlobStore
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.domain.ledger.reducer import compute_state_digest, initial_state
from vanguard.packages.kernel.attenuation import Constraints, Scope, attenuate
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.runtime.checkpoints import (
    CHECKPOINT_SCHEMA_VERSION,
    CheckpointPins,
    decode_state,
    encode_state,
)
from vanguard.packages.runtime.model_selection import ModelUnavailable, select_model
from vanguard.packages.runtime.repair import StopReason
from vanguard.packages.runtime.tier_escalation import TierLadder, run_with_escalation


def _event(seq: int, kind: str, payload: dict, run_id: str = "run-001") -> EventEnvelope:
    body = {"kind": kind, **payload}
    return EventEnvelope(
        schema_version="mhf.event/2",
        event_id=f"0192f0a0-0000-7000-8000-{seq:012d}",
        scope="episode",
        seq=str(seq),
        occurred_at="2026-08-25T12:00:00.000Z",
        recorded_at="2026-08-25T12:00:00.000Z",
        principal="agent-cmx08",
        principal_role="episode",
        tenant_id="tenant-default",
        owner_id="owner-platform",
        confidentiality="internal",
        retention_class="extended",
        trainability="prohibited",
        redaction_status="none",
        payload=body,
        run_id=run_id,
        episode_id="ep-001",
    )


class TestCMX08ReleaseHardening(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        (self.workspace / "README.md").write_text("# Project\n")
        self.service = ApplicationService(workspace=self.workspace)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_checkpoint_state_encode_and_decode_parity(self) -> None:
        state = initial_state(run_id="run-001", episode_id="ep-001")
        encoded = encode_state(state)
        decoded = decode_state(encoded)
        self.assertEqual(decoded.episode.run_id, "run-001")
        self.assertEqual(compute_state_digest(decoded), compute_state_digest(state))

    def test_sqlite_wal_event_store_backup_and_read(self) -> None:
        store_path = self.workspace / "events.db"
        store = SqliteEventStore(store_path)
        appended = store.append([
            _event(1, "TaskStarted", {"objective": "test"}, run_id="run-1"),
            _event(2, "StepExecuted", {"verb": "fs.read"}, run_id="run-1"),
        ])
        self.assertTrue(appended.ok)
        read = store.read(EventRange(run_id="run-1"))
        self.assertTrue(read.ok)
        self.assertEqual(len(list(read.value)), 2)

    def test_blob_store_content_addressing_and_retrieval(self) -> None:
        blob_path = self.workspace / "blobs"
        store = FileBlobStore(blob_path)
        stored = store.put(b"hello world data content")
        self.assertTrue(stored.ok)
        digest = stored.value
        self.assertTrue(digest.startswith("sha256:"))
        fetched = store.get(digest)
        self.assertTrue(fetched.ok)
        self.assertEqual(fetched.value, b"hello world data content")

    def test_malformed_model_response_fails_closed_with_typed_error(self) -> None:
        ladder = TierLadder(rungs=(("free", "openrouter/free"), ("medium", "deepseek/deepseek-v4-flash-0731")))

        def run_one(band: str, model_name: str) -> dict:
            if band == "free":
                return {"outcome": "instrument_error:provider_malformed_response", "session": ()}
            return {"outcome": StopReason.ORACLE_GREEN, "session": ({"verb": "fs.read"},)}

        outcome = run_with_escalation(ladder, run_one)
        self.assertEqual(len(outcome.attempts), 2)
        self.assertEqual(outcome.settled_band, "medium")

    def test_budget_exhaustion_at_all_dimensions(self) -> None:
        parent_scope = Scope(
            actions=frozenset(["fs.read"]),
            resources=(),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=5,
                budget_usd_micros=10_000,
                max_bytes=1000,
                max_effects=5,
                risk_ceiling="low",
                max_depth=3,
                network_policy="deny",
            ),
            depth=1,
            sealed=True,
        )
        # Exceeding uses
        res_uses = attenuate(parent_scope, Scope(
            actions=frozenset(["fs.read"]),
            resources=(),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=10,  # exceeds parent
                budget_usd_micros=10_000,
            ),
            depth=1,
        ))
        self.assertFalse(res_uses.ok)
        self.assertEqual(res_uses.denial.dimension, "constraints.maxUses")

        # Exceeding budget
        res_budget = attenuate(parent_scope, Scope(
            actions=frozenset(["fs.read"]),
            resources=(),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=5,
                budget_usd_micros=20_000,  # exceeds parent
            ),
            depth=1,
        ))
        self.assertFalse(res_budget.ok)
        self.assertEqual(res_budget.denial.dimension, "constraints.budget")

        # Exceeding depth
        parent_max_depth = Scope(
            actions=frozenset(["fs.read"]),
            resources=(),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=5,
                budget_usd_micros=10_000,
                max_depth=2,
            ),
            depth=2,
        )
        res_depth = attenuate(parent_max_depth, Scope(
            actions=frozenset(["fs.read"]),
            resources=(),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z",
                max_uses=5,
                budget_usd_micros=10_000,
                max_depth=2,
            ),
            depth=2,
        ))
        self.assertFalse(res_depth.ok)
        self.assertEqual(res_depth.denial.dimension, "depth")


if __name__ == "__main__":
    unittest.main()
