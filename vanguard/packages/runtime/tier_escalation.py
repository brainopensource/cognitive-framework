"""Escalate through model tiers when the cheap model is stuck; fall back for
execution once a plan exists (`REQ-TRUST-001`).

Salvaged idea from the deleted `MetaLoopEngine` (`S7-A-04`'s salvage note:
"tier escalation -> S8-B-03"). The old engine escalated *inside* the episode
loop and graded its own escalation decision, which inverted `A-05`. This does
neither: it is a policy *around* `drive_until_green`, calling it once per tier
and deciding the next tier from the **stop reason alone** -- never from a
model's or an evaluator's opinion of its own output. No second dispatch path,
no second loop inside the engine.

The shape: start cheap (free). If the cheap tier cannot make progress --
`no_progress`, `attempts_exhausted` with no real verb, or certain instrument
errors -- step up one tier and try again. Once a tier produces a real
`ProposalProduced` with a verb (evidence the loop is actually working, not
evidence of success), the policy remembers that model and prefers stepping
back down to it or below on the *next* task, because most of a repair loop's
turns are read/verify/re-check, not the one hard reasoning step, and cheap
turns cost nothing.

Every attempt at every tier is a separate, fully-labelled run. Nothing here
merges the ledgers or fabricates a combined "session" -- an escalation report
is a sequence of runs, and the caller decides what that sequence means.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Mapping, Sequence

from .repair import StopReason

__all__ = [
    "EscalationOutcome", "ModelRole", "RouteDecision", "RoleAwareRouter",
    "TierLadder", "run_with_escalation",
]


class ModelRole(str, Enum):
    """A workflow role, never an additional model/effect loop."""

    ARCHITECT = "architect"
    EXECUTOR = "executor"
    DIAGNOSTIC = "diagnostic"
    REVIEWER = "reviewer"


@dataclass(frozen=True, slots=True)
class RouteDecision:
    """Attributable route selection made before an episode starts."""

    requested_model: str
    resolved_model: str
    role: ModelRole
    band: str
    reason: str
    episode_id: str
    pricing_known: bool
    trigger: str = ""
    parent_episode_id: str | None = None
    parent_state_digest: str | None = None
    budget_snapshot: Mapping[str, int] = field(default_factory=dict)
    provider_usage_status: str = "unknown"

    def to_dict(self) -> dict[str, object]:
        return {
            "requestedModel": self.requested_model,
            "resolvedModel": self.resolved_model,
            "role": self.role.value,
            "band": self.band,
            "reason": self.reason,
            "episodeId": self.episode_id,
            "pricingKnown": self.pricing_known,
            "trigger": self.trigger,
            "parentEpisodeId": self.parent_episode_id,
            "parentStateDigest": self.parent_state_digest,
            "budgetSnapshot": dict(self.budget_snapshot or {}),
            "providerUsageStatus": self.provider_usage_status,
        }


class RoleAwareRouter:
    """Choose a configured model by role without executing or retrying it.

    This is intentionally a pure policy.  Provider health and paid-budget
    authorization are supplied by callers; a missing or forbidden model raises
    rather than silently selecting the preceding attempt's model.
    """

    def __init__(self, *, bands: Mapping[str, Sequence[str]],
                 planner_model: str | None = None,
                 recovery_model: str | None = None,
                 reviewer_model: str | None = None) -> None:
        from ..adapters.models.config import get_medium_model
        self._bands = {name: tuple(models) for name, models in bands.items()}
        self._planner = planner_model or get_medium_model()
        self._recovery = recovery_model or get_medium_model()
        self._reviewer = reviewer_model

    def choose(self, role: ModelRole, *, episode_id: str, reason: str,
               healthy_free_models: Sequence[str] = (),
               allow_paid: bool = False,
               complexity: int = 0,
               remaining_budget_micros: int | None = None,
               healthy_models: Sequence[str] | None = None,
               trigger: str = "",
               parent_episode_id: str | None = None,
               parent_state_digest: str | None = None,
               budget_snapshot: Mapping[str, int] | None = None) -> RouteDecision:
        if role is ModelRole.EXECUTOR:
            candidates = tuple(healthy_free_models) or self._bands.get("free", ())
            if not candidates:
                raise ValueError("no healthy free executor model is registered")
            model, band = candidates[0], "free"
        elif role is ModelRole.ARCHITECT:
            model, band = self._planner, "medium"
        elif role is ModelRole.DIAGNOSTIC:
            model, band = self._recovery, "medium"
        else:
            candidates = ((self._reviewer,) if self._reviewer else ()) or self._bands.get("free", ())
            if not candidates:
                raise ValueError("no reviewer model is registered")
            model, band = candidates[0], "free" if candidates[0] in self._bands.get("free", ()) else "medium"
        if band != "free" and not allow_paid:
            raise ValueError(f"paid model {model!r} is not authorized for {role.value}")
        from ..adapters.models.routing import resolve_route
        route = resolve_route(model)
        if healthy_models is not None and model not in set(healthy_models):
            raise ValueError(f"model {model!r} is not healthy")
        if not route.resolved_model:
            raise ValueError(f"model {model!r} did not resolve to a provider identity")
        if not route.pricing_known:
            raise ValueError(f"pricing is unknown for paid model {model!r}")
        if remaining_budget_micros is not None and band != "free":
            estimated = route.estimated_cost_micros(max(1, complexity or 1))
            if estimated > remaining_budget_micros:
                raise ValueError(f"model {model!r} exceeds remaining paid budget")
        return RouteDecision(model, route.resolved_model, role, band, reason,
                             episode_id, route.pricing_known, trigger,
                             parent_episode_id, parent_state_digest,
                             dict(budget_snapshot or {}), "unknown")

#: Stop reasons that mean "this tier could not drive the loop", worth trying
#: the next tier for. Reasons *not* here (workspace_missing, paid_model_refused,
#: model_tag_absent, provider_key_missing) are configuration facts, not
#: capability signals, and escalating past them would hide a setup bug as a
#: model failure.
_ESCALATE_ON = (
    StopReason.NO_PROGRESS,
    "instrument_error:multi_action_proposal",
    "instrument_error:provider_malformed_response",
    "instrument_error:unclassified",
)


@dataclass(frozen=True, slots=True)
class TierLadder:
    """An ordered list of `(band, model_name)` to climb, cheapest first."""

    rungs: tuple[tuple[str, str], ...]

    @classmethod
    def from_bands(cls, models_for_band: Callable[[str], Sequence[str]],
                   bands: Sequence[str] = ("free", "medium", "high")) -> "TierLadder":
        """Build a ladder from the LAM registry, one representative per band.

        Only the first id in each band is used. A ladder that tried every
        model in every band would turn one task into a dozen paid calls before
        it ever climbed, which is the opposite of "escalate only when stuck".
        """
        rungs: list[tuple[str, str]] = []
        for band in bands:
            names = models_for_band(band)
            if names:
                rungs.append((band, names[0]))
        return cls(rungs=tuple(rungs))


@dataclass(frozen=True, slots=True)
class TierAttempt:
    band: str
    model_name: str
    result: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"band": self.band, "modelName": self.model_name,
                "outcome": self.result.get("outcome"),
                "turns": self.result.get("turns")}


@dataclass(frozen=True, slots=True)
class EscalationOutcome:
    """Every rung tried, and which one (if any) is worth descending to."""

    attempts: tuple[TierAttempt, ...]
    final: dict[str, Any]
    #: The cheapest rung that produced real verbs, for the caller to prefer on
    #: the *next* task. `None` means nothing on the ladder made progress.
    settled_band: str | None
    settled_model: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempts": [a.to_dict() for a in self.attempts],
            "final": self.final,
            "settledBand": self.settled_band,
            "settledModel": self.settled_model,
        }


def _made_progress(result: dict[str, Any]) -> bool:
    """Evidence the loop actually ran, not evidence the task was solved.

    A tier that reaches `oracle_green` obviously made progress. A tier that
    took real turns with real verbs also counts: it proves the model can drive
    the harness, even if it did not finish, and that is what makes a rung
    worth remembering for next time.
    """
    if result.get("outcome") == StopReason.ORACLE_GREEN:
        return True
    return any(entry.get("verb") for entry in result.get("session", ()))


def run_with_escalation(
    ladder: TierLadder,
    run_one: Callable[[str, str], dict[str, Any]],
) -> EscalationOutcome:
    """Climb `ladder` calling `run_one(band, model_name)` until progress.

    `run_one` is the caller's own `run_lab_task` closure -- this module runs no
    episode and dispatches no effect itself. Stops climbing the first time a
    rung makes progress, or reports the top rung's result if none did.
    """
    if not ladder.rungs:
        raise ValueError("empty tier ladder: nothing to run")

    attempts: list[TierAttempt] = []
    settled_band: str | None = None
    settled_model: str | None = None

    for band, model_name in ladder.rungs:
        result = run_one(band, model_name)
        attempts.append(TierAttempt(band=band, model_name=model_name, result=result))

        if _made_progress(result):
            settled_band, settled_model = band, model_name
            break

        outcome = str(result.get("outcome", ""))
        if outcome not in _ESCALATE_ON and not any(
                outcome.startswith(reason) for reason in _ESCALATE_ON
                if isinstance(reason, str)):
            # A configuration fact (missing key, refused paid model, absent
            # workspace), not a capability signal. Climbing past it would hide
            # a setup bug as if a smarter model had been needed.
            break

    return EscalationOutcome(
        attempts=tuple(attempts),
        final=attempts[-1].result,
        settled_band=settled_band,
        settled_model=settled_model,
    )
