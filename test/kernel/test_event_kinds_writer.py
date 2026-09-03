"""TSK-LED-001 / S060-B-01: EVENT_KINDS catalogues EffectRejected and KernelAlarm.

REQ-LEDGER-002. The reducer still preserves unknown kinds (CT-44).
"""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.events import (
    DEPRECATED_KINDS,
    EVENT_KINDS,
    WRITABLE_KINDS,
    parse_event_envelope,
)
from vanguard.packages.runtime.ledger_emitter import (
    DeprecatedKindError,
    LedgerEmitter,
    WriterAuthorityError,
)


def _raw(kind: str) -> dict:
    return {
        "schemaVersion": "vg.4",
        "eventId": "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
        "scope": "episode",
        "runId": "run-1",
        "episodeId": "ep-1",
        "seq": "1",
        "occurredAt": "2026-08-18T00:00:00.000Z",
        "recordedAt": "2026-08-18T00:00:00.001Z",
        "principal": "agent-1",
        "principalRole": "episode",
        "tenantId": "tenant-default",
        "ownerId": "owner-platform",
        "confidentiality": "internal",
        "retentionClass": "standard",
        "trainability": "prohibited",
        "redactionStatus": "none",
        "traceId": "trace-1",
        "spanId": "span-1",
        "payload": {"kind": kind},
    }


class ClosedEventKinds(unittest.TestCase):
    def test_effect_rejected_and_kernel_alarm_are_catalogued(self) -> None:
        self.assertIn("EffectRejected", EVENT_KINDS)
        self.assertIn("KernelAlarm", EVENT_KINDS)

    def test_catalogued_kinds_parse(self) -> None:
        for kind in ("EpisodeCompleted", "EffectRejected", "KernelAlarm"):
            env = parse_event_envelope(_raw(kind))
            self.assertEqual(env.payload["kind"], kind)

    def test_unknown_kind_is_not_in_the_writer_catalog(self) -> None:
        # CT-44 still reconstructs unknown kinds at the reducer. The writer
        # catalog is closed: a novel kind is not a member of EVENT_KINDS.
        self.assertNotIn("NotARealKind", EVENT_KINDS)
        self.assertNotIn("RunFailed", EVENT_KINDS)


class WriterRejectsUncataloguedKinds(unittest.TestCase):
    """The catalog is enforced at the writer, not merely asserted in a test.

    `ledger_emitter` imported `WRITABLE_KINDS` and never checked membership,
    so an invented kind appended cleanly and the reducer filed it into
    `unknown_events` -- a silent write no reader has a fold for. This is the
    behavioural half of this module's own docstring claim; the assertions
    above only inspect the catalog.
    """

    # `_assert_writer` reads only module-level tables, so it is exercised
    # unbound rather than standing up an emitter with a store and a clock.
    def _assert_writer(self, kind: str, writer: str = "orchestrator") -> None:
        LedgerEmitter._assert_writer(None, writer, kind)

    def test_writer_rejects_a_kind_outside_the_catalog(self) -> None:
        with self.assertRaises(WriterAuthorityError):
            self._assert_writer("NotARealKind")

    def test_writer_rejects_a_service_context_kind(self) -> None:
        # `runtime/service/` kinds (ADR-0062) are a separate vocabulary and
        # must never reach the ledger writer.
        for kind in ("RunFailed", "CheckpointRecorded", "CancellationRequested"):
            with self.assertRaises(WriterAuthorityError):
                self._assert_writer(kind)

    def test_deprecated_kinds_keep_their_own_error_type(self) -> None:
        # Ordering matters: the membership check runs first, so a deprecated
        # kind must still raise the more specific subclass rather than being
        # swallowed by "not writable".
        kind = sorted(DEPRECATED_KINDS)[0]
        with self.assertRaises(DeprecatedKindError):
            self._assert_writer(kind)

    def test_writable_kinds_pass_the_membership_check(self) -> None:
        # Unowned kinds any role may write, and kernel-owned kinds written by
        # the kernel. The new membership check must not disturb either.
        for kind in ("EpisodeStarted", "EpisodeCompleted"):
            self.assertIn(kind, WRITABLE_KINDS)
            self._assert_writer(kind)  # must not raise
        for kind in ("EffectRejected", "KernelAlarm"):
            self.assertIn(kind, WRITABLE_KINDS)
            self._assert_writer(kind, writer="kernel")  # must not raise

    def test_writer_authority_still_applies_after_the_membership_check(self) -> None:
        # The membership check is additive: a catalogued kind with an owner
        # must still be refused to a role that does not own it.
        with self.assertRaises(WriterAuthorityError):
            self._assert_writer("EffectRejected", writer="orchestrator")
