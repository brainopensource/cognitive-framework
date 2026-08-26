"""Opt-in, between-turn M-6.5 controller seam.

The controller is deliberately a value-in/value-out policy hook.  This module
does not know about stores, models, capabilities, or event emitters.  Callers
must turn a returned directive into an ordinary proposal in their existing
runtime path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..domain.ledger.agent_view import AgentView
from ..domain.ledger.progress import ConfidenceRecord, ProgressView
from ..ports.meta_controller import MetaController, StrategyDirective

__all__ = [
    "ControllerInputError",
    "ControllerOutputError",
    "ControllerProposal",
    "consult",
    "directive_attribution",
    "guarded_consult",
    "validate_confidence",
    "validate_directive",
    "view_reference_set",
]


@dataclass(frozen=True, slots=True)
class ControllerProposal:
    """A normal, non-authoritative runtime proposal."""

    kind: str
    payload: Mapping[str, Any]
    attribution: Mapping[str, Any]


def directive_attribution(
    directive: StrategyDirective,
    view: AgentView,
    progress: ProgressView,
    confidence: Sequence[ConfidenceRecord],
) -> dict[str, Any]:
    refs = tuple(record.digest() for record in confidence)
    return {
        "controllerId": directive.controller_id,
        "directiveKind": directive.kind,
        "confidenceRefs": refs,
        "reasonDigest": digest_of({"reason": directive.reason}),
        "inputDigest": digest_of({"view": view.to_canonical_dict(), "progress": progress.to_dict()}),
    }


def consult(
    controller: MetaController | None,
    view: AgentView,
    progress: ProgressView,
    confidence: Sequence[ConfidenceRecord] = (),
) -> ControllerProposal | None:
    """Consult once between turns and map output to an ordinary proposal."""
    if controller is None:
        return None
    records = tuple(confidence)
    directive = controller.assess(view, progress, records)
    if directive is None:
        return None
    attribution = directive_attribution(directive, view, progress, records)
    payload: dict[str, Any] = {"reason": directive.reason}
    if directive.brief is not None:
        payload["brief"] = directive.brief
    if directive.scope_slice is not None:
        payload["scope"] = dict(directive.scope_slice)
    return ControllerProposal(kind=directive.kind, payload=payload, attribution=attribution)


# --------------------------------------------------------------------------
# M-6.5 fail-closed consultation guards (`B-M65`)
#
# `consult` above is the minimal seam: value in, value out.  A measured study
# needs more than that, because the five ways an adaptive-strategy result gets
# manufactured are all *input* or *output* defects rather than logic errors:
#
#   1. stale confidence     -- deciding on a signal computed before the last
#                              context change, so the "adaptation" is a reply
#                              to a situation that no longer exists;
#   2. missing references   -- a confidence record about a subject the view
#                              has never seen, which cannot be re-derived by a
#                              second reader and so is not evidence;
#   3. nondeterministic     -- a controller that answers differently to the
#      directives              same inputs makes paired runs incomparable;
#   4. budget bypass        -- a directive that quietly enlarges the budget it
#                              was supposed to be economising;
#   5. authority escalation -- a directive carrying capabilities, grants, or a
#                              principal, i.e. a policy plugin writing itself
#                              a permission slip.
#
# All five fail closed: `guarded_consult` raises rather than returning a
# proposal it cannot vouch for.  Metacognition stays policy, never privilege.
# --------------------------------------------------------------------------

#: Keys that would turn a routing hint into a grant.
_AUTHORITY_KEYS = frozenset({
    "capabilities", "capability", "grants", "grant", "authority", "principal",
    "uid", "role", "sink", "verb", "selector", "approval", "signature",
})
#: Keys that would let a strategy hint raise its own ceiling.
_BUDGET_KEYS = frozenset({
    "budget", "budgets", "usd_micros", "usdMicros", "millis", "tokens",
    "bytes", "turns", "depth", "limit", "limits", "ceiling", "maxBudget",
})


class ControllerInputError(ValueError):
    """The controller was consulted on inputs that cannot support a decision."""


class ControllerOutputError(ValueError):
    """The controller returned something a pure policy plugin may not return."""


def view_reference_set(view: AgentView) -> frozenset[str]:
    """Every subject a confidence record may legitimately be *about*.

    Derived from the projection, so a second reader folding the same events
    computes the same set. A reference outside it is unverifiable by
    construction, which is why it is refused rather than ignored.
    """
    # `goal` is always a legitimate subject: every lineage has exactly one,
    # and `C-06` keeps its *content* out of the ledger. Excluding the token
    # because the content is absent would make goal-level confidence
    # inexpressible on the canonical path -- which is what happened the first
    # time this guard met a real run.
    refs: set[str] = {view.lineage_id, "goal"}
    if view.goal:
        refs.add(view.goal)
    refs.update(str(key) for key in view.settled_effects)
    if view.strategy:
        refs.add(view.strategy)
    for group in (view.attempts, view.plan_revisions, view.children):
        for item in group:
            for key in ("id", "attemptId", "revisionId", "lineageId", "childLineageId"):
                value = item.get(key)
                if isinstance(value, str) and value:
                    refs.add(value)
    return frozenset(refs)


def validate_confidence(
    view: AgentView,
    confidence: Sequence[ConfidenceRecord],
) -> None:
    """Refuse unverifiable or out-of-date confidence before it is acted on."""
    known = view_reference_set(view)
    for record in confidence:
        if record.subject_ref not in known:
            raise ControllerInputError(
                f"confidence subject {record.subject_ref!r} is not in the view")
        calibration = dict(record.calibration or {})
        epoch = calibration.get("contextEpoch", calibration.get("context_epoch"))
        if epoch is None:
            raise ControllerInputError(
                "confidence record does not declare the context epoch it was "
                "computed at, so it cannot be shown to be current")
        if int(epoch) != int(view.context_epoch):
            raise ControllerInputError(
                f"confidence for epoch {epoch} is stale at epoch {view.context_epoch}")


def validate_directive(
    directive: StrategyDirective,
    *,
    remaining_budget: Mapping[str, int] | None = None,
) -> None:
    """Refuse a directive that reaches for authority or budget it was not given."""
    slice_ = dict(directive.scope_slice or {})
    for key in slice_:
        lowered = str(key)
        if lowered in _AUTHORITY_KEYS:
            raise ControllerOutputError(
                f"directive scope carries authority key {key!r}; a controller "
                f"proposes, it does not grant")
    for key, value in slice_.items():
        if str(key) in _BUDGET_KEYS or str(key).startswith("max"):
            if remaining_budget is None:
                raise ControllerOutputError(
                    f"directive scope names budget key {key!r} with no "
                    f"remaining-budget ceiling to check it against")
            dimension = _BUDGET_ALIASES.get(str(key), str(key))
            ceiling = remaining_budget.get(dimension)
            if ceiling is None:
                raise ControllerOutputError(
                    f"directive scope names unknown budget dimension {key!r}")
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ControllerOutputError(
                    f"budget slice {key!r} must be a non-negative integer")
            if value > ceiling:
                raise ControllerOutputError(
                    f"directive requests {value} of {dimension} but only "
                    f"{ceiling} remains; a controller cannot enlarge a budget")
    try:
        digest_of(slice_)
    except Exception as exc:  # pragma: no cover - defensive
        raise ControllerOutputError(
            "directive scope must be a plain value, not a runtime handle") from exc


#: `maxTurns` is the spelling a delegate slice uses for the `turns` dimension.
_BUDGET_ALIASES: Mapping[str, str] = {
    "maxTurns": "turns", "max_turns": "turns",
    "maxDepth": "depth", "max_depth": "depth",
    "maxTokens": "tokens", "max_tokens": "tokens",
    "maxMillis": "millis", "max_millis": "millis",
    "maxBytes": "bytes", "max_bytes": "bytes",
    "usdMicros": "usd_micros", "maxUsdMicros": "usd_micros",
}


def guarded_consult(
    controller: MetaController | None,
    view: AgentView,
    progress: ProgressView,
    confidence: Sequence[ConfidenceRecord] = (),
    *,
    remaining_budget: Mapping[str, int] | None = None,
    determinism_samples: int = 2,
) -> ControllerProposal | None:
    """`consult` with every M-6.5 falsifier applied, fail-closed.

    This is the form a measured study and a runtime integration must use.  It
    is deliberately separate from `consult`: the seam stays minimal for the
    callers that only need the value mapping, while anything that will be
    *reported as evidence* goes through the guarded path.
    """
    if controller is None:
        return None
    records = tuple(confidence)
    validate_confidence(view, records)

    directive = controller.assess(view, progress, records)
    for _ in range(max(0, determinism_samples - 1)):
        again = controller.assess(view, progress, records)
        if again != directive:
            raise ControllerOutputError(
                "controller returned different directives for identical inputs; "
                "paired runs cannot be compared against a nondeterministic arm")
    if directive is None:
        return None
    validate_directive(directive, remaining_budget=remaining_budget)

    attribution = directive_attribution(directive, view, progress, records)
    payload: dict[str, Any] = {"reason": directive.reason}
    if directive.brief is not None:
        payload["brief"] = directive.brief
    if directive.scope_slice is not None:
        payload["scope"] = dict(directive.scope_slice)
    return ControllerProposal(kind=directive.kind, payload=payload,
                              attribution=attribution)
