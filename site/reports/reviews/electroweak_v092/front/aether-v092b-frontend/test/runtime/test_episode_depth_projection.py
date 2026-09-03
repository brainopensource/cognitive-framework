"""Episode depth is a projection of the ledger, not a second store.

S7-A-05. `runtime/coordination.py` kept episode depth in its own SQLite table:
a second budget ledger with no lease, no release, no overrun debit, no
conservation property, no events and no attenuation. A-07 says everything is an
event and every surface is a projection of it, so depth must be derivable from
the event stream alone.

The biological labels (Atom -> Body) are applied *by the projection* over an
integer depth. They are never classes, and nothing downstream may branch on a
subtype.
"""

from __future__ import annotations

import unittest

from vanguard.packages.domain.ledger.events import EventEnvelope
from vanguard.packages.runtime.ledger.projections import (
    EpisodeDepthProjection,
    rebuild_projection,
)


def episode_started(
    episode_id: str,
    *,
    seq: str,
    causation_id: str | None = None,
    run_id: str = "run-1",
) -> EventEnvelope:
    """An EpisodeStarted envelope, optionally caused by a parent episode."""

    payload: dict[str, object] = {"kind": "EpisodeStarted", "episodeId": episode_id}
    if causation_id is not None:
        payload["causationId"] = causation_id
    return EventEnvelope(
        schema_version="vg.4",
        event_id=f"evt-{episode_id}",
        scope="episode",
        seq=seq,
        occurred_at="2026-08-16T00:00:00Z",
        recorded_at="2026-08-16T00:00:00Z",
        principal="agent-1",
        principal_role="agent",
        tenant_id="t1",
        owner_id="o1",
        confidentiality="internal",
        retention_class="standard",
        trainability="no",
        redaction_status="none",
        payload=payload,
        run_id=run_id,
        episode_id=episode_id,
    )


class _ReplayStore:
    """Minimal EventStorePort stand-in returning a fixed event sequence."""

    def __init__(self, events: list[EventEnvelope]) -> None:
        self._events = events

    def read(self, _range: object) -> object:
        class _Res:
            ok = True

            def __init__(self, value: list[EventEnvelope]) -> None:
                self.value = value
                self.error = None

        return _Res(self._events)


class DepthDerivesFromEventsAlone(unittest.TestCase):
    def _chain(self) -> EpisodeDepthProjection:
        projection = EpisodeDepthProjection()
        for event in (
            episode_started("ep-root", seq="0001"),
            episode_started("ep-a", seq="0002", causation_id="ep-root"),
            episode_started("ep-b", seq="0003", causation_id="ep-a"),
            episode_started("ep-c", seq="0004", causation_id="ep-b"),
            episode_started("ep-d", seq="0005", causation_id="ep-c"),
        ):
            projection.apply(event)
        return projection

    def test_root_episode_is_atom_at_depth_zero(self) -> None:
        projection = EpisodeDepthProjection()
        projection.apply(episode_started("ep-root", seq="0001"))
        self.assertEqual(projection.depth_of("ep-root"), 0)
        self.assertEqual(projection.label_of("ep-root"), "Atom")

    def test_causation_chain_yields_emergent_labels(self) -> None:
        projection = self._chain()
        self.assertEqual(projection.label_of("ep-root"), "Atom")
        self.assertEqual(projection.label_of("ep-a"), "Molecule")
        self.assertEqual(projection.label_of("ep-b"), "Polymer")
        self.assertEqual(projection.label_of("ep-c"), "Cell")
        self.assertEqual(projection.label_of("ep-d"), "Body")
        self.assertEqual(projection.depth_of("ep-d"), 4)

    def test_depth_saturates_at_body(self) -> None:
        projection = self._chain()
        projection.apply(episode_started("ep-e", seq="0006", causation_id="ep-d"))
        self.assertEqual(projection.depth_of("ep-e"), 5)
        self.assertEqual(projection.label_of("ep-e"), "Body")

    def test_labels_are_projection_output_not_classes(self) -> None:
        """A-07: labels are applied over integer depth, never as a class tree."""

        import vanguard.packages.runtime.ledger.projections as module

        names = {name for name in dir(module) if not name.startswith("_")}
        for forbidden in ("Atom", "Molecule", "Polymer", "Cell", "Body", "Organism"):
            self.assertNotIn(forbidden, names)

    def test_unknown_episode_has_no_fabricated_depth(self) -> None:
        projection = EpisodeDepthProjection()
        self.assertIsNone(projection.depth_of("never-started"))
        self.assertIsNone(projection.label_of("never-started"))

    def test_orphan_causation_does_not_invent_a_parent(self) -> None:
        """A child whose parent was never observed is not silently rooted."""

        projection = EpisodeDepthProjection()
        projection.apply(episode_started("ep-orphan", seq="0001", causation_id="ep-missing"))
        self.assertIsNone(projection.depth_of("ep-orphan"))
        self.assertEqual(projection.to_dict()["unresolved"], ["ep-orphan"])

    def test_rebuild_from_sequence_zero_matches_incremental(self) -> None:
        """GTS-13C T3.4: a projection rebuilt from 0 is byte-identical."""

        events = [
            episode_started("ep-root", seq="0001"),
            episode_started("ep-a", seq="0002", causation_id="ep-root"),
            episode_started("ep-b", seq="0003", causation_id="ep-a"),
        ]
        incremental = EpisodeDepthProjection()
        for event in events:
            incremental.apply(event)

        rebuilt = rebuild_projection(_ReplayStore(events), EpisodeDepthProjection())
        self.assertEqual(rebuilt.to_dict(), incremental.to_dict())
        self.assertEqual(rebuilt.digest(), incremental.digest())

    def test_out_of_order_arrival_still_resolves_depth(self) -> None:
        """The child may be reduced before its parent; depth is not arrival order."""

        projection = EpisodeDepthProjection()
        projection.apply(episode_started("ep-b", seq="0003", causation_id="ep-a"))
        projection.apply(episode_started("ep-a", seq="0002", causation_id="ep-root"))
        projection.apply(episode_started("ep-root", seq="0001"))
        self.assertEqual(projection.depth_of("ep-b"), 2)
        self.assertEqual(projection.label_of("ep-b"), "Polymer")


if __name__ == "__main__":
    unittest.main()
