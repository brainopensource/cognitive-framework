"""RF-76 compatibility-reader fidelity for supported ``mhf.event/1`` rows."""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.events import parse_event_envelope
from vanguard.packages.domain.ledger.reducer import compute_state_digest, initial_state, reduce_batch


class CompatibilityReaderFidelity(unittest.TestCase):
    def test_supported_old_wal_rows_rebuild_equivalent_state(self) -> None:
        rows = [
            {
                "schema_version": "mhf.event/1", "event_id": "evt-1", "kind": "EpisodeStarted",
                "seq": 1, "occurred_at": "2026-01-01T00:00:00Z", "run_id": "run-1",
                "principal": "principal-1", "episode_id": "episode-1",
                "payload": {"kind": "EpisodeStarted", "taskSpec": {"brief": "compat"}},
            },
            {
                "schema_version": "mhf.event/1", "event_id": "evt-2", "kind": "EpisodeCompleted",
                "seq": "2", "occurred_at": "2026-01-01T00:00:01Z", "run_id": "run-1",
                "principal": "principal-1", "episode_id": "episode-1",
                "payload": {"kind": "EpisodeCompleted", "outcome": "resolved"},
            },
        ]
        parsed = [parse_event_envelope(row) for row in rows]
        state = reduce_batch(initial_state(), parsed)
        replay = reduce_batch(initial_state(), [parse_event_envelope(row) for row in rows])
        self.assertEqual(compute_state_digest(state), compute_state_digest(replay))
        self.assertEqual(state.episode.status, "completed")
        # Reader defaults are compatibility metadata only; old rows do not gain
        # a fabricated principal/tenant/episode authority relationship.
        self.assertIsNone(parsed[0].principal_id)
        self.assertEqual(parsed[0].principal, "principal-1")


if __name__ == "__main__":
    unittest.main()
