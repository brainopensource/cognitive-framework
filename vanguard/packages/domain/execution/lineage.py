"""Value contract for a causal execution lineage."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LineageRef:
    """Identity and ancestry of one bounded execution lineage.

    This is descriptive domain data. It does not grant authority and never
    replaces Kernel attenuation or capability validation.
    """

    lineage_id: str
    parent: str | None
    root: str
    depth: int

    def __post_init__(self) -> None:
        if not self.lineage_id:
            raise ValueError("lineage_id must be non-empty")
        if not self.root:
            raise ValueError("root must be non-empty")
        if self.depth < 0:
            raise ValueError("depth must be non-negative")
        if self.parent is None and self.depth != 0:
            raise ValueError("root lineages must have depth zero")
        if self.parent == self.lineage_id:
            raise ValueError("lineage cannot parent itself")
