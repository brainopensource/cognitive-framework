"""Pure ledger reducer for declared governance processes (REQ-EXEC-002)."""

from __future__ import annotations

from dataclasses import replace
from typing import Sequence

from ...domain.ledger.events import EventEnvelope
from ...ports.event_store import EventRange, EventStorePort
from .model import ProcessDefinition, ProcessHistory, ProcessInstance


class ProcessError(RuntimeError):
    """The ledger could not be used to reconstruct a process safely."""


class ProcessEngine:
    """Advance a finite process using ordered governance ledger events only.

    Events are associated with an instance by ``payload.processId``. Pending
    approvals suspend every transition except their matching
    ``ApprovalResolved`` event. No episode state or model service participates.
    """

    def __init__(self, definition: ProcessDefinition) -> None:
        self.definition = definition

    def initial_instance(self, process_id: str) -> ProcessInstance:
        if not process_id:
            raise ValueError("process_id must not be empty")
        return ProcessInstance(
            process_id=process_id,
            definition_digest=self.definition.definition_digest,
            current_state=self.definition.initial_state,
            allowed_transitions=self.definition.allowed_from(self.definition.initial_state),
            pending_approvals=(),
            bound_effect_verbs=self.definition.bound_effect_verbs,
            history=(),
        )

    def apply(self, instance: ProcessInstance, event: EventEnvelope) -> ProcessInstance:
        if instance.definition_digest != self.definition.definition_digest:
            raise ProcessError("instance definition digest does not match the loaded definition")
        payload = event.payload
        if event.scope != "governance" or payload.get("processId") != instance.process_id:
            return instance

        kind = payload.get("kind")
        if not isinstance(kind, str):
            return instance

        pending = list(instance.pending_approvals)
        if kind == "ApprovalRequested":
            approval_id = payload.get("approvalId")
            if isinstance(approval_id, str) and approval_id and approval_id not in pending:
                pending.append(approval_id)

        if instance.pending_approvals:
            if kind != "ApprovalResolved":
                return instance
            approval_id = payload.get("approvalId")
            if approval_id not in pending:
                return instance
            pending.remove(approval_id)
            if payload.get("resolution") != "approved" or pending:
                return replace(instance, pending_approvals=tuple(pending))

        edge = self.definition.transition_for(instance.current_state, kind)
        if edge is None:
            return replace(instance, pending_approvals=tuple(pending))

        history = instance.history + (
            ProcessHistory(edge.from_state, edge.event_kind, edge.to_state, event.event_id),
        )
        return ProcessInstance(
            process_id=instance.process_id,
            definition_digest=instance.definition_digest,
            current_state=edge.to_state,
            allowed_transitions=self.definition.allowed_from(edge.to_state),
            pending_approvals=tuple(pending),
            bound_effect_verbs=instance.bound_effect_verbs,
            history=history,
        )

    def replay(self, process_id: str, events: Sequence[EventEnvelope]) -> ProcessInstance:
        instance = self.initial_instance(process_id)
        for event in sorted(events, key=lambda item: int(item.seq)):
            instance = self.apply(instance, event)
        return instance

    def resume(self, process_id: str, store: EventStorePort) -> ProcessInstance:
        """Reconstitute an instance from the durable governance ledger."""
        result = store.read(EventRange(scope="governance"))
        if not result.ok:
            detail = result.error.message if result.error else "unknown event-store failure"
            raise ProcessError(f"cannot read governance ledger: {detail}")
        return self.replay(process_id, result.value or ())
