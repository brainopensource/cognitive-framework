"""Pure execution scope and strict child attenuation contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


class InvalidScopeAttenuation(ValueError):
    """Raised when a child scope is not a strict narrowing of its parent."""


_RESOURCE_KEYS = frozenset({"usd_micros", "millis", "tokens", "bytes"})


@dataclass(frozen=True, slots=True)
class ExecutionScope:
    """Spatio-temporal boundary reference for one lineage.

    Capability authority is referenced by id only. Actual grant attenuation is
    performed by the Kernel; this object only proves the child declaration is
    no broader than its parent declaration.
    """

    lineage_id: str
    budget: Mapping[str, int]
    max_depth: int
    max_turns: int
    capability_grant: str | None
    terminal_conditions: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.lineage_id:
            raise ValueError("lineage_id must be non-empty")
        if self.max_depth < 0 or self.max_turns < 0:
            raise ValueError("scope ceilings must be non-negative")
        unknown = set(self.budget) - _RESOURCE_KEYS
        if unknown:
            raise ValueError(f"unknown budget dimensions: {sorted(unknown)}")
        if any(int(value) < 0 for value in self.budget.values()):
            raise ValueError("scope budget cannot be negative")

    def attenuated_for_child(
        self,
        *,
        budget_slice: Mapping[str, int],
        lineage_id: str,
        max_depth: int | None = None,
        max_turns: int | None = None,
        capability_grant: str | None = None,
        terminal_conditions: tuple[str, ...] | None = None,
    ) -> "ExecutionScope":
        """Create a strictly narrower child declaration.

        The child must name a different lineage and may not increase any
        resource or ceiling. Grant attenuation itself remains a Kernel action.
        """

        if lineage_id == self.lineage_id:
            raise InvalidScopeAttenuation("child lineage must differ from parent")
        if set(budget_slice) - _RESOURCE_KEYS:
            raise InvalidScopeAttenuation("unknown child budget dimension")
        child_budget = {key: int(value) for key, value in budget_slice.items()}
        for key, value in child_budget.items():
            if value < 0 or value > int(self.budget.get(key, 0)):
                raise InvalidScopeAttenuation(f"child budget exceeds parent for {key}")
        child_depth = self.max_depth if max_depth is None else int(max_depth)
        child_turns = self.max_turns if max_turns is None else int(max_turns)
        if child_depth < 0 or child_depth > self.max_depth:
            raise InvalidScopeAttenuation("child max_depth exceeds parent")
        if child_turns < 0 or child_turns > self.max_turns:
            raise InvalidScopeAttenuation("child max_turns exceeds parent")
        if capability_grant == self.capability_grant and self.capability_grant is not None:
            raise InvalidScopeAttenuation("child must use an attenuated grant reference")
        return ExecutionScope(
            lineage_id=lineage_id,
            budget=child_budget,
            max_depth=child_depth,
            max_turns=child_turns,
            capability_grant=capability_grant,
            terminal_conditions=(
                self.terminal_conditions
                if terminal_conditions is None
                else tuple(terminal_conditions)
            ),
        )
