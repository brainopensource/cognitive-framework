"""Reconstructible coding-harness state (`CodingTaskState`).

This is a runtime projection of durable facts, not an authority or a second
ledger. Callers may persist its canonical form and rebuild it from events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of

__all__ = ["CodingTaskState"]


@dataclass(frozen=True, slots=True)
class CodingTaskState:
    """Minimal durable state needed to resume a coding task semantically."""

    objective: str
    constraints: tuple[str, ...] = ()
    plan: tuple[str, ...] = ()
    strategy_steps: tuple[str, ...] = ()
    hypotheses: tuple[str, ...] = ()
    inspected_files: tuple[str, ...] = ()
    modified_files: tuple[str, ...] = ()
    verification_plan: tuple[str, ...] = ()
    last_verification: Mapping[str, Any] = field(default_factory=dict)
    failure_class: str | None = None
    next_action: str | None = None
    settled_effects: tuple[str, ...] = ()
    remaining_budgets: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("objective must be non-empty")
        for name in ("constraints", "plan", "strategy_steps", "hypotheses", "inspected_files",
                     "modified_files", "verification_plan", "settled_effects"):
            values = getattr(self, name)
            if not isinstance(values, tuple) or not all(isinstance(v, str) for v in values):
                raise TypeError(f"{name} must be a tuple of strings")
        if any(not isinstance(k, str) or not isinstance(v, int) or v < 0
               for k, v in self.remaining_budgets.items()):
            raise ValueError("remaining_budgets must contain non-negative integers")

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "constraints": list(self.constraints),
            "plan": list(self.plan),
            "strategySteps": list(self.strategy_steps),
            "hypotheses": list(self.hypotheses),
            "inspectedFiles": list(self.inspected_files),
            "modifiedFiles": list(self.modified_files),
            "verificationPlan": list(self.verification_plan),
            "lastVerification": dict(self.last_verification),
            "failureClass": self.failure_class,
            "nextAction": self.next_action,
            "settledEffects": list(self.settled_effects),
            "remainingBudgets": dict(self.remaining_budgets),
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CodingTaskState":
        def strings(name: str, camel: str) -> tuple[str, ...]:
            value = raw.get(camel, raw.get(name, ()))
            if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
                raise TypeError(f"{camel} must be a sequence")
            return tuple(str(item) for item in value)

        budgets = raw.get("remainingBudgets", raw.get("remaining_budgets", {}))
        verification = raw.get("lastVerification", raw.get("last_verification", {}))
        if not isinstance(budgets, Mapping) or not isinstance(verification, Mapping):
            raise TypeError("state mappings must be objects")
        return cls(
            objective=str(raw.get("objective", "")),
            constraints=strings("constraints", "constraints"),
            plan=strings("plan", "plan"),
            strategy_steps=strings("strategy_steps", "strategySteps"),
            hypotheses=strings("hypotheses", "hypotheses"),
            inspected_files=strings("inspected_files", "inspectedFiles"),
            modified_files=strings("modified_files", "modifiedFiles"),
            verification_plan=strings("verification_plan", "verificationPlan"),
            last_verification=dict(verification),
            failure_class=raw.get("failureClass", raw.get("failure_class")),
            next_action=raw.get("nextAction", raw.get("next_action")),
            settled_effects=strings("settled_effects", "settledEffects"),
            remaining_budgets={str(k): int(v) for k, v in budgets.items()},
        )
