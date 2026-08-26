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

__all__ = ["ControllerProposal", "consult", "directive_attribution"]


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
