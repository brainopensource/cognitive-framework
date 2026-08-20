"""Single-turn LLM driver wrapping ModelPort as IPlanner (SPEC §2.2)."""

from __future__ import annotations

from typing import Any, ClassVar, Mapping, Sequence

from vanguard.packages.domain.wire.result import Err, Ok, Result
from vanguard.packages.domain.wire.types_gen import (
    EffectRequest,
    EpisodeOutcome,
    EpisodeView,
    Proposal,
    Receipt,
    Reflection,
    Reservation,
    SinkClass,
    TrajectoryRef,
)
from vanguard.packages.ports.model import ModelPort

__all__ = ["DefaultPlannerAdapter"]

# Same shapes the coding pack / vg-code-default already grant (ADR-0076 §2).
_PROC_PATTERN = "proc://exec/allow/git,pytest,ruff,python3"


def _selector_for(verb: str, root: str) -> dict[str, Any]:
    if verb == "proc.exec":
        return {"kind": "generic", "uriPattern": _PROC_PATTERN}
    return {"kind": "fs", "root": root, "paths": [root]}


class DefaultPlannerAdapter:
    spi_version: ClassVar[str] = "1.0"

    def __init__(
        self,
        model: ModelPort,
        *,
        tools: Sequence[Mapping[str, Any]] = (),
        resource_root: str = "/workspace",
    ) -> None:
        self._model = model
        self._tools = tuple(tools)
        self._resource_root = resource_root

    def plan(self, view: EpisodeView, budget: Reservation) -> Result[Proposal]:
        context = {
            "goal": view.goal,
            "turn": view.turn,
            "run_id": view.run_id,
            "episode_id": view.episode_id,
        }
        proposed = self._model.propose(context, list(self._tools), {"max_tokens": budget.tokens})
        if not proposed.ok:
            message = proposed.error.message if proposed.error else "model failed"
            return Err("instrument_error", message, instrument_error=True)
        payload = dict(proposed.value or {})
        calls = payload.get("toolCalls") or ()
        requests: list[EffectRequest] = []
        for call in calls:
            if not isinstance(call, Mapping):
                continue
            verb = str(call.get("name") or call.get("verb") or "")
            raw_args = call.get("arguments") or call.get("args") or {}
            if not isinstance(raw_args, Mapping):
                raw_args = {}
            requests.append(
                EffectRequest(
                    verb=verb,
                    args=dict(raw_args),
                    selector=_selector_for(verb, self._resource_root),
                    sink=SinkClass.OBSERVATION,
                    reservation=budget,
                )
            )
        return Ok(
            Proposal(
                thought=str(payload.get("text") or view.goal),
                requests=tuple(requests),
            )
        )

    def observe(self, receipts: Sequence[Receipt], view: EpisodeView) -> None:
        _ = receipts, view

    def reflect(
        self, outcome: EpisodeOutcome, trajectory: TrajectoryRef,
    ) -> Result[Reflection | None]:
        _ = outcome, trajectory
        return Ok(None)
