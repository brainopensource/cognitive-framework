"""TSK-LED-001 / S060-B-01: EVENT_KINDS catalogues EffectRejected and KernelAlarm.

REQ-LEDGER-002. The reducer still preserves unknown kinds (CT-44).
"""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.events import EVENT_KINDS, parse_event_envelope


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
