"""Readable domain model for finite governance processes.

The JSON wire schemas remain authoritative.  These immutable types make the
runtime rules explicit: definitions contain a finite set of states and one
deterministic edge for each ``(state, event kind)`` pair; instances contain
only state that can be reconstructed from ledger events.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ...domain.wire.contracts import parse_wire


@dataclass(frozen=True, slots=True)
class Transition:
    from_state: str
    event_kind: str
    to_state: str


@dataclass(frozen=True, slots=True)
class ProcessHistory:
    from_state: str
    event_kind: str
    to_state: str
    event_id: str


@dataclass(frozen=True, slots=True)
class ProcessDefinition:
    definition_digest: str
    states: tuple[str, ...]
    initial_state: str
    transitions: tuple[Transition, ...]
    approval_points: frozenset[str]
    bound_effect_verbs: tuple[str, ...]

    @classmethod
    def from_wire(cls, value: Mapping[str, Any]) -> "ProcessDefinition":
        parsed = parse_wire("ProcessDefinition", value)
        return cls(
            definition_digest=str(parsed["definitionDigest"]),
            states=tuple(str(state) for state in parsed["states"]),
            initial_state=str(parsed["initialState"]),
            transitions=tuple(
                Transition(str(edge["from"]), str(edge["eventKind"]), str(edge["to"]))
                for edge in parsed["transitions"]
            ),
            approval_points=frozenset(str(state) for state in parsed["approvalPoints"]),
            bound_effect_verbs=tuple(str(verb) for verb in parsed["boundEffectVerbs"]),
        )

    def transition_for(self, state: str, event_kind: str) -> Transition | None:
        return next(
            (edge for edge in self.transitions if edge.from_state == state and edge.event_kind == event_kind),
            None,
        )

    def allowed_from(self, state: str) -> tuple[str, ...]:
        return tuple(edge.event_kind for edge in self.transitions if edge.from_state == state)


@dataclass(frozen=True, slots=True)
class ProcessInstance:
    process_id: str
    definition_digest: str
    current_state: str
    allowed_transitions: tuple[str, ...]
    pending_approvals: tuple[str, ...]
    bound_effect_verbs: tuple[str, ...]
    history: tuple[ProcessHistory, ...]

    def to_wire(self) -> dict[str, Any]:
        return {
            "processId": self.process_id,
            "definitionDigest": self.definition_digest,
            "currentState": self.current_state,
            "allowedTransitions": list(self.allowed_transitions),
            "pendingApprovals": list(self.pending_approvals),
            "boundEffectVerbs": list(self.bound_effect_verbs),
            "history": [
                {
                    "from": item.from_state,
                    "eventKind": item.event_kind,
                    "to": item.to_state,
                    "eventId": item.event_id,
                }
                for item in self.history
            ],
        }
