"""Canonical state-dependent tool policy value objects and resolvers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

ToolPolicyMode = Literal["auto", "required", "none"]


@dataclass(frozen=True, slots=True)
class ToolPolicy:
    """Canonical request-boundary policy declaring allowed tools and required selection."""

    mode: ToolPolicyMode = "auto"
    allowed: tuple[str, ...] = ()

    def is_allowed(self, tool_name: str) -> bool:
        if not self.allowed:
            return True
        return tool_name in self.allowed


def resolve_tool_policy(
    phase: str = "inspect",
    *,
    verification_passed: bool = False,
    preset_mode: str | None = None,
    custom_allowed: Sequence[str] | None = None,
) -> ToolPolicy:
    """Derive effective tool policy based on workflow phase and verification status."""
    if custom_allowed is not None:
        return ToolPolicy(mode="required", allowed=tuple(custom_allowed))

    if preset_mode in {"research", "explain"}:
        return ToolPolicy(mode="auto")

    if verification_passed:
        return ToolPolicy(mode="auto")

    if phase == "inspect":
        return ToolPolicy(
            mode="required",
            allowed=("fs.read", "fs.search"),
        )
    if phase == "edit":
        return ToolPolicy(
            mode="required",
            allowed=("fs.read", "fs.search", "patch.apply"),
        )
    if phase == "verify":
        return ToolPolicy(
            mode="required",
            allowed=("proc.exec", "fs.read", "patch.apply"),
        )

    return ToolPolicy(mode="required")


#: The phase ladder lives here, not in the engine: `ADR-0060` requires the
#: episode loop to name no domain verb. Which attempted effects advance the
#: workflow phase is preset policy, exactly like the allowed sets above.
_VERIFY_TRIGGERS = frozenset({"patch.apply"})
_EDIT_TRIGGERS = frozenset({"fs.read", "fs.search"})


def derive_phase(seen_verbs: Sequence[str] | frozenset[str] | set[str]) -> str:
    """Map attempted effect verbs onto the workflow phase ladder.

    Phase advances only from *attempted* effects, never from model prose. A
    denied dispatch still advances the phase: it proves the workflow moved
    past the earlier phase, and verify-phase allowances must stay reachable
    after a patch attempt regardless of its outcome.
    """
    seen = set(seen_verbs)
    if seen & _VERIFY_TRIGGERS:
        return "verify"
    if seen & _EDIT_TRIGGERS:
        return "edit"
    return "inspect"
