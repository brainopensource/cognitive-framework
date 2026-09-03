"""Guard validation logic for benchmark runs."""

from __future__ import annotations

from typing import Any, Mapping


class GuardRefusal(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def classify_refusal(run: Mapping[str, Any]) -> str | None:
    if run.get("pre_passed"):
        return "precondition_already_satisfied"
    if run.get("effects_applied", 0) == 0 and run.get("post_passed"):
        return "no_intervention_occurred"
    if run.get("effects_applied", 0) > 0 and run.get("prompt_tokens", 0) == 0 and run.get("completion_tokens", 0) == 0:
        return "agent_not_invoked"
    if run.get("provider_error"):
        return "instrument_or_provider_failure"
    if run.get("effects_applied", 0) > 0 and not run.get("verdict_present", False):
        return "no_verdict_recorded"
    return None


def validate_run(run: Mapping[str, Any]) -> None:
    refusal = classify_refusal(run)
    if refusal is not None:
        raise GuardRefusal(refusal)
