"""Fail-closed publication guard for benchmark run records.

The guard is deliberately independent of a runner.  A runner supplies the
observations it made; this module decides whether those observations can be
scored or published.
"""

from __future__ import annotations

from typing import Any, Mapping


class GuardRefusal(ValueError):
    """A run is not eligible to be scored."""

    def __init__(self, reason: str, *, publication_blocked: bool = False) -> None:
        self.reason = reason
        self.publication_blocked = publication_blocked
        super().__init__(reason)


def _tokens(run: Mapping[str, Any]) -> int:
    usage = run.get("usage")
    if isinstance(usage, Mapping):
        return int(usage.get("prompt_tokens", 0) or 0) + int(usage.get("completion_tokens", 0) or 0)
    return int(run.get("prompt_tokens", 0) or 0) + int(run.get("completion_tokens", 0) or 0)


def validate_run(run: Mapping[str, Any], *, repair_task: bool = True) -> dict[str, Any]:
    """Return a scoreable run summary or raise :class:`GuardRefusal`.

    Provider/instrument failures are explicitly marked as excluded from both
    the numerator and denominator, rather than being converted into failures.
    """
    if repair_task and bool(run.get("pre_passed", False)):
        raise GuardRefusal("inconclusive:precondition_satisfied")
    if bool(run.get("provider_error")) or bool(run.get("instrument_error")):
        raise GuardRefusal("inconclusive:instrument_error")
    effects = run.get("effects_applied", run.get("effects", 0))
    if int(effects or 0) == 0 and bool(run.get("post_passed", run.get("oracle_passed", False))):
        raise GuardRefusal("inconclusive:no_intervention")
    if _tokens(run) == 0:
        raise GuardRefusal("inconclusive:model_not_invoked")
    if not bool(run.get("verdict_present", run.get("evaluator_present", False))):
        raise GuardRefusal("inconclusive:no_verdict")
    containment = run.get("containment")
    if not isinstance(containment, Mapping) or not bool(containment.get("passed", False)):
        raise GuardRefusal("publication blocked: containment missing or failing", publication_blocked=True)
    return {"scoreable": True, "numerator": int(bool(run.get("passed", False))), "denominator": 1}


def classify_refusal(exc: GuardRefusal) -> dict[str, Any]:
    """Serialize a refusal without laundering it into pass/fail."""
    instrument = exc.reason == "inconclusive:instrument_error"
    return {
        "verdict": exc.reason,
        "scoreable": False,
        "numerator": 0,
        "denominator": 0 if instrument else 1,
        "publication_blocked": exc.publication_blocked,
    }
