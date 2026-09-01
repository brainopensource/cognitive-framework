"""Role-aware model routing and escalation (`spec §28`, `§29`).

This wraps the substrate's existing `RoleAwareRouter`/`TierLadder`
(`runtime/tier_escalation.py`) rather than replacing it. The substrate already
owns band definitions and escalation mechanics; what is missing is the
*policy* mapping a Coding Max role and failure history onto a band.

`spec §29`: *"Do not escalate unnecessarily."* Escalation therefore requires a
recorded reason and consumes budget; it is never the default response to a
single failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

__all__ = ["CodingRole", "ModelRouter", "ModelSelection"]


class CodingRole(str, Enum):
    """`spec §28` roles."""

    CLASSIFIER = "classifier"
    PLANNER = "planner"
    WORKER = "worker"
    REVIEWER = "reviewer"
    REPLANNER = "replanner"
    SUMMARIZER = "summarizer"


#: Default band per role. Cheap models handle mechanical synthesis; the worker
#: and reviewer get the strong band because that is where correctness is
#: decided. Classification is absent: it is deterministic and needs no model.
_DEFAULT_BAND: Mapping[CodingRole, str] = {
    CodingRole.CLASSIFIER: "cheap",
    CodingRole.SUMMARIZER: "cheap",
    CodingRole.PLANNER: "mid",
    CodingRole.REPLANNER: "mid",
    CodingRole.WORKER: "strong",
    CodingRole.REVIEWER: "strong",
}

_LADDER: tuple[str, ...] = ("cheap", "mid", "strong", "frontier")


@dataclass(frozen=True, slots=True)
class ModelSelection:
    role: CodingRole
    band: str
    model: str
    reason: str
    escalated: bool = False
    attempt: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value, "band": self.band, "model": self.model,
            "reason": self.reason, "escalated": self.escalated,
            "attempt": self.attempt,
        }


class ModelRouter:
    """`spec §28` selector over the substrate's band configuration."""

    def __init__(
        self,
        bands: Mapping[str, Sequence[str]],
        *,
        default_model: str = "",
        allow_escalation: bool = True,
    ) -> None:
        self._bands = {k: tuple(v) for k, v in bands.items()}
        self._default = default_model
        self._allow_escalation = allow_escalation
        self._escalations: dict[CodingRole, int] = {}

    def select(
        self,
        role: CodingRole,
        *,
        task_profile: Any = None,
        previous_failures: int = 0,
        budget_can_escalate: bool = True,
        force_band: str | None = None,
    ) -> ModelSelection:
        band = force_band or _DEFAULT_BAND.get(role, "mid")
        reason = f"default band for {role.value}"
        escalated = False

        # A high-complexity task starts the worker one rung up rather than
        # discovering the need after two wasted failures.
        complexity = float(getattr(task_profile, "estimated_complexity", 0.0) or 0.0)
        if role is CodingRole.WORKER and complexity >= 0.75 and not force_band:
            band = _up(band)
            reason = f"task complexity {complexity:.2f} warrants a stronger worker"

        # `spec §29`: escalate on *repeated* failure, never on the first.
        if (previous_failures >= 2 and self._allow_escalation
                and budget_can_escalate and not force_band):
            band = _up(band)
            escalated = True
            self._escalations[role] = self._escalations.get(role, 0) + 1
            reason = (f"{previous_failures} prior failures in role {role.value}; "
                      f"escalating one band")

        return ModelSelection(
            role=role, band=band, model=self._model_for(band),
            reason=reason, escalated=escalated,
            attempt=self._escalations.get(role, 0),
        )

    def stronger_model(self, selection: ModelSelection) -> ModelSelection:
        """One rung up from an existing selection (`spec §29` helper)."""
        band = _up(selection.band)
        if band == selection.band:
            return selection
        return ModelSelection(
            role=selection.role, band=band, model=self._model_for(band),
            reason="explicit escalation after repeated difficult failure",
            escalated=True, attempt=selection.attempt + 1,
        )

    def _model_for(self, band: str) -> str:
        """First configured model in the band, degrading down the ladder.

        Degrading rather than raising matters: a deployment that configures
        only two bands must still run, and a missing `frontier` entry should
        quietly resolve to the strongest band that exists.
        """
        for candidate in (band, *reversed(_LADDER[: _LADDER.index(band)]
                                          if band in _LADDER else ())):
            models = self._bands.get(candidate, ())
            if models:
                return models[0]
        return self._default

    def escalation_count(self) -> Mapping[str, int]:
        return {role.value: count for role, count in self._escalations.items()}


def _up(band: str) -> str:
    if band not in _LADDER:
        return band
    index = _LADDER.index(band)
    return _LADDER[min(index + 1, len(_LADDER) - 1)]
