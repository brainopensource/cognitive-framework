"""mhf.trajectory/1 record emitted at EpisodeCompleted."""

from __future__ import annotations

from typing import Mapping

from layer0.events.canonical import digest_of
from layer0.spi.types_gen import TrajectoryRef

__all__ = ["trajectory_record"]


def trajectory_record(*, run_id: str, event_count: int, extra: Mapping[str, object] | None = None) -> TrajectoryRef:
    body = {"schema": "mhf.trajectory/1", "run_id": run_id, "event_count": event_count}
    if extra:
        body.update(dict(extra))
    return TrajectoryRef(digest=digest_of(body), schema="mhf.trajectory/1")
