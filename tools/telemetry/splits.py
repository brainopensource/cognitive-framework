"""Corpus partitioning, contamination controls, and touch ledger (S9-C-05).

Owning contract: VG-07 §5.5, REQ-BENCH-001.

Partitions instances into strictly separated partitions:
- DEV: public development and prompt iteration.
- HOLDOUT: evaluation only; tuning on holdout immediately burns it to DEV.
- SEALED: cryptographically sealed benchmark set.
- LIVE: streaming / uncurated incoming tasks.
- DEPLOYMENT: production post-deployment evaluations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence, Set


class SplitPartition(str, Enum):
    DEV = "DEV"
    HOLDOUT = "HOLDOUT"
    SEALED = "SEALED"
    LIVE = "LIVE"
    DEPLOYMENT = "DEPLOYMENT"


class ContaminationError(RuntimeError):
    """Raised when an illegal cross-partition contamination is attempted."""
    pass


@dataclass
class TouchRecord:
    """Immutable audit entry for partition access or burn."""

    timestamp: str
    task_id: str
    original_partition: SplitPartition
    access_type: str  # e.g., 'eval_read', 'prompt_tuning', 'training'
    burned_to: SplitPartition | None
    actor: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "taskId": self.task_id,
            "originalPartition": self.original_partition.value,
            "accessType": self.access_type,
            "burnedTo": self.burned_to.value if self.burned_to else None,
            "actor": self.actor,
            "note": self.note,
        }


class SplitRegistry:
    """Manages partition membership and enforces one-way contamination burns."""

    def __init__(self, initial_splits: Mapping[SplitPartition, Sequence[str]] | None = None) -> None:
        self._partitions: dict[SplitPartition, set[str]] = {p: set() for p in SplitPartition}
        if initial_splits:
            for part, ids in initial_splits.items():
                self._partitions[part] = set(ids)
        self._ledger: list[TouchRecord] = []

    def get_partition(self, task_id: str) -> SplitPartition | None:
        for part, ids in self._partitions.items():
            if task_id in ids:
                return part
        return None

    def access_instance(
        self,
        task_id: str,
        access_type: str,
        actor: str,
        timestamp: str = "2026-08-17T00:00:00Z",
    ) -> SplitPartition:
        """Access an instance. If a prompt_tuning / training access touches HOLDOUT, burn to DEV."""
        current_part = self.get_partition(task_id)
        if current_part is None:
            raise KeyError(f"Task ID {task_id!r} not found in any corpus partition")

        burned_to = None
        if access_type in {"prompt_tuning", "training", "parameter_search"}:
            if current_part in {SplitPartition.HOLDOUT, SplitPartition.SEALED}:
                # One-way burn: permanently moves instance from HOLDOUT/SEALED to DEV
                self._partitions[current_part].remove(task_id)
                self._partitions[SplitPartition.DEV].add(task_id)
                burned_to = SplitPartition.DEV
                current_part = SplitPartition.DEV

        record = TouchRecord(
            timestamp=timestamp,
            task_id=task_id,
            original_partition=self.get_partition(task_id) or current_part,
            access_type=access_type,
            burned_to=burned_to,
            actor=actor,
            note="Burned to DEV due to tuning access" if burned_to else "Standard evaluation access",
        )
        self._ledger.append(record)
        return current_part

    def touch_ledger(self) -> list[TouchRecord]:
        return list(self._ledger)

    def is_burned(self, task_id: str) -> bool:
        return any(r.task_id == task_id and r.burned_to is not None for r in self._ledger)
