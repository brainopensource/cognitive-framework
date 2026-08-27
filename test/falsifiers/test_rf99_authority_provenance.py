"""RF-99: authority provenance is typed protocol data, on the real write path.

`ADR-0096 §13`: "authority provenance is present as typed protocol data for
every operation to which it applies, with `null` permitted only where
semantically inapplicable".

`test/contracts/test_event_substrate_v2.py` proves the envelope and the
derivation rule in isolation. This is the **runtime leg**: envelopes built by
the production `LedgerEmitter`, appended to a real store, read back out, and
folded -- because the failure this falsifier exists to catch is a write path
that constructs authority correctly and then loses it on the way to disk, or
one where an unprivileged role's append arrives indistinguishable from the
Kernel's.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.events import DEPRECATED_KINDS
from vanguard.packages.kernel.model import Event
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.ledger_emitter import (
    ROLE_AUTHORITY_SOURCES,
    WRITER_ROLES,
    DeprecatedKindError,
    LedgerEmitter,
    WriterAuthorityError,
)

_AT = "2026-08-25T12:00:00.000Z"


def _emitter(store, *, role: str = "session", version: str = "mhf.event/2",
             policy_version: str = "policy/7") -> LedgerEmitter:
    return LedgerEmitter(
        store,
        episode_id="ep-rf99",
        project_id=f"project-rf99-{role}-{version[-1]}",
        principal_id="agent-rf99",
        harness_digest="sha256:" + "7" * 64,
        clock=FixedClock(at=_AT, step_ms=1),
        random=SeededRandom(seed=99),
        role=role,
        writer_version=version,
        policy_version=policy_version,
    )


def _event(kind: str, **payload) -> Event:
    return Event(kind=kind, reason="rf99", at=_AT, run_id="run-rf99",
                 principal="agent-rf99", payload={"kind": kind, **payload})


class AuthorityIsDurableNotJustConstructed(unittest.TestCase):
    """Authority must survive the round trip through the store."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.db = str(Path(self._tmp.name) / "rf99.sqlite")

    def _read_back(self, emitter: LedgerEmitter, project_id: str):
        store = SqliteEventStore(self.db)
        read = store.read(EventRange(project_id=project_id))
        self.assertTrue(read.ok, read.error)
        return list(read.value or [])

    def test_every_v2_append_carries_a_typed_authority_source_after_a_round_trip(self) -> None:
        store = SqliteEventStore(self.db)
        emitter = _emitter(store)
        emitter.kernel().emit(_event("CapabilityGranted", grantId="grant-rf99"))
        emitter.kernel().emit(_event("EffectStarted", idempotencyKey="eff-1"))
        emitter.kernel().emit(_event("BudgetReserved", leaseId="lease-1"))

        stored = self._read_back(emitter, "project-rf99-session-2")
        self.assertEqual(len(stored), 3)
        for envelope in stored:
            self.assertEqual(envelope.schema_version, "mhf.event/2")
            self.assertEqual(envelope.authority_source, "kernel-capability")
            self.assertEqual(envelope.policy_version, "policy/7")

    def test_the_authority_fields_are_inside_the_signed_preimage(self) -> None:
        # If authority were outside the digest, it could be edited after the
        # fact without breaking the chain -- provenance nobody has to honour.
        store = SqliteEventStore(self.db)
        emitter = _emitter(store, role="kernel")
        envelope = emitter.kernel().emit(_event("KernelAlarm", detail="x"))
        assert envelope is not None
        preimage = envelope.to_mhf_dict(include_digest=False)
        self.assertIn("authority_source", preimage)
        self.assertIn("policy_version", preimage)
        self.assertIn("approval_reference", preimage)
        self.assertIn("capability_grant", preimage)

        forged = dict(preimage)
        forged["authority_source"] = "human-approval"
        from vanguard.packages.domain.canonicalisation.digest import digest_of
        self.assertNotEqual(digest_of(forged), envelope.content_digest)

    def test_the_chain_survives_across_a_v1_to_v2_writer_switch(self) -> None:
        store = SqliteEventStore(self.db)
        legacy = _emitter(store, version="mhf.event/1")
        legacy.kernel().emit(_event("EpisodeStarted", episodeId="ep-rf99"))
        stored = self._read_back(legacy, "project-rf99-session-1")
        self.assertEqual(stored[-1].schema_version, "mhf.event/1")
        self.assertIsNone(stored[-1].authority_source)

        modern = LedgerEmitter(
            store, episode_id="ep-rf99", project_id="project-rf99-session-1",
            principal_id="agent-rf99", harness_digest="sha256:" + "7" * 64,
            clock=FixedClock(at=_AT, step_ms=1),
            # A distinct seed: the emitters are deterministic, so reusing 99
            # would mint the id the `/1` write already holds.
            random=SeededRandom(seed=199),
            role="session", writer_version="mhf.event/2")
        modern.kernel().emit(_event("EffectCompleted", idempotencyKey="eff-2"))

        chain = self._read_back(modern, "project-rf99-session-1")
        self.assertEqual(len(chain), 2)
        # The `/1` record is never rewritten to carry authority it never had.
        self.assertIsNone(chain[0].authority_source)
        self.assertEqual(chain[1].authority_source, "kernel-capability")
        self.assertEqual(chain[1].prev_digest, chain[0].content_digest or chain[0].digest())


class RoleConsistencyOnTheWritePath(unittest.TestCase):
    """A role may only claim what it actually held."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.db = str(Path(self._tmp.name) / "rf99-roles.sqlite")

    def test_every_writer_role_has_a_declared_authority_source(self) -> None:
        # An undeclared role would fall through to "unattributed" -- readable,
        # but it means a production writer with no stated basis exists.
        self.assertEqual(set(WRITER_ROLES) - set(ROLE_AUTHORITY_SOURCES), set())

    def test_an_orchestrator_append_is_distinguishable_from_the_kernels(self) -> None:
        store = SqliteEventStore(self.db)
        emitter = _emitter(store, role="orchestrator")
        envelope = emitter.orchestrator().emit(
            _event("ObservationProduced", grantId="grant-forged",
                   approvalId="approval-forged"))
        assert envelope is not None
        self.assertEqual(envelope.authority_source, "orchestrator-policy")
        self.assertIsNone(envelope.capability_grant)
        self.assertIsNone(envelope.approval_reference)

    def test_a_privileged_kind_is_refused_to_an_unprivileged_role(self) -> None:
        store = SqliteEventStore(self.db)
        emitter = _emitter(store, role="orchestrator")
        with self.assertRaises(WriterAuthorityError):
            emitter.orchestrator().emit(_event("CapabilityGranted", grantId="g"))

    def test_the_refusal_leaves_nothing_durable_behind(self) -> None:
        store = SqliteEventStore(self.db)
        emitter = _emitter(store, role="orchestrator")
        with self.assertRaises(WriterAuthorityError):
            emitter.orchestrator().emit(_event("EffectStarted", idempotencyKey="e"))
        read = store.read(EventRange(project_id="project-rf99-orchestrator-2"))
        self.assertEqual(list(read.value or []), [])

    def test_a_deprecated_kind_is_refused_on_the_real_write_path(self) -> None:
        store = SqliteEventStore(self.db)
        emitter = _emitter(store, role="session")
        for kind in sorted(DEPRECATED_KINDS):
            with self.assertRaises(DeprecatedKindError, msg=kind):
                emitter.kernel().emit(_event(kind))
        read = store.read(EventRange(project_id="project-rf99-session-2"))
        self.assertEqual(list(read.value or []), [])

    def test_an_approval_reference_binds_only_from_an_approving_role(self) -> None:
        store = SqliteEventStore(self.db)
        approver = _emitter(store, role="approval")
        bound = approver.approval().emit(
            _event("ApprovalResolved", approvalId="approval-real", status="approved"))
        assert bound is not None
        self.assertEqual(bound.authority_source, "human-approval")
        self.assertEqual(bound.approval_reference, "approval-real")

    def test_null_means_inapplicable_and_never_unknown(self) -> None:
        store = SqliteEventStore(self.db)
        emitter = _emitter(store, role="session")
        envelope = emitter.kernel().emit(_event("EpisodeStarted", episodeId="ep-rf99"))
        assert envelope is not None
        # No grant and no approval are in play for an episode start, so both
        # are null -- but the two non-nullable fields are still populated.
        self.assertIsNone(envelope.capability_grant)
        self.assertIsNone(envelope.approval_reference)
        self.assertTrue(envelope.authority_source)
        self.assertTrue(envelope.policy_version)


if __name__ == "__main__":
    unittest.main()
