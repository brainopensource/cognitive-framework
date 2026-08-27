"""Digest-pinned task benchmark for M-6.5 paired study (`WP-B2`).

Requirements:
- >=20 tasks across >=4 recoverable block types.
- 4 block types: context_deficit, plan_stalemate, hypothesis_loop, verification_gap.
- Each task has an immutable, digest-pinned manifest.
- Default pilot seeds: >=3 seeds (e.g. 42, 137, 2026) yielding >=60 pairs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of

__all__ = [
    "DEFAULT_STUDY_SEEDS",
    "M65TaskManifest",
    "generate_m65_task_suite",
]

DEFAULT_STUDY_SEEDS = (42, 137, 2026)


@dataclass(frozen=True, slots=True)
class M65TaskManifest:
    task_id: str
    name: str
    block_type: str
    difficulty: float
    description: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskId": self.task_id,
            "name": self.name,
            "blockType": self.block_type,
            "difficulty": round(self.difficulty, 4),
            "description": self.description,
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())


def generate_m65_task_suite(task_count: int = 24) -> tuple[M65TaskManifest, ...]:
    """Generate a canonical benchmark suite of >=20 tasks across 4 recoverable block types."""
    if task_count < 20:
        raise ValueError("M-6.5 study requires >=20 benchmark tasks")

    block_types = (
        ("context_deficit", "Task requires missing external context or domain knowledge"),
        ("plan_stalemate", "Task requires revising execution plan to avoid deadlocks"),
        ("hypothesis_loop", "Task requires abandoning invalid hypothesis to prevent loop"),
        ("verification_gap", "Task requires strengthening verification to catch subtle defect"),
    )

    tasks: list[M65TaskManifest] = []
    tasks_per_block = task_count // len(block_types)

    for b_idx, (block_type, desc_template) in enumerate(block_types):
        count = tasks_per_block if b_idx < len(block_types) - 1 else (task_count - len(tasks))
        for i in range(count):
            task_num = len(tasks) + 1
            task_id = f"m65-task-{task_num:03d}"
            diff = 0.3 + (i * 0.08)
            task = M65TaskManifest(
                task_id=task_id,
                name=f"{block_type}_{i+1}",
                block_type=block_type,
                difficulty=diff,
                description=f"{desc_template} (variant {i+1})",
            )
            tasks.append(task)

    return tuple(tasks)
