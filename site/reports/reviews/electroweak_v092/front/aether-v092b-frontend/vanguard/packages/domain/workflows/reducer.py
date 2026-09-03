"""Pure, deterministic event-sourced reducer for workflow graph state."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping

from .contracts import WorkflowSpec


@dataclass(frozen=True, slots=True)
class WorkflowState:
    """Event-sourced projection of workflow execution state (zero mutable state)."""

    workflow_id: str
    topology_id: str
    active_nodes: tuple[str, ...] = field(default_factory=tuple)
    settled_nodes: tuple[str, ...] = field(default_factory=tuple)
    node_outputs: Mapping[str, str] = field(default_factory=dict)  # node_id -> output_digest
    node_attempts: Mapping[str, int] = field(default_factory=dict)  # node_id -> attempts
    completed: bool = False
    result_digest: str | None = None
    suspended: bool = False
    suspend_reason: str | None = None

    def schedule_node(self, node_id: str) -> WorkflowState:
        attempts = self.node_attempts.get(node_id, 0) + 1
        new_attempts = dict(self.node_attempts)
        new_attempts[node_id] = attempts
        return replace(
            self,
            active_nodes=tuple(sorted(set(self.active_nodes + (node_id,)))),
            node_attempts=new_attempts,
        )

    def settle_node(
        self,
        node_id: str,
        output_digest: str | None = None,
    ) -> WorkflowState:
        remaining_active = tuple(n for n in self.active_nodes if n != node_id)
        new_settled = tuple(sorted(set(self.settled_nodes + (node_id,))))
        new_outputs = dict(self.node_outputs)
        if output_digest is not None:
            new_outputs[node_id] = output_digest
        return replace(
            self,
            active_nodes=remaining_active,
            settled_nodes=new_settled,
            node_outputs=new_outputs,
        )

    def complete(self, result_digest: str | None = None) -> WorkflowState:
        return replace(
            self,
            completed=True,
            active_nodes=(),
            result_digest=result_digest,
        )

    def suspend(self, reason: str) -> WorkflowState:
        return replace(
            self,
            suspended=True,
            suspend_reason=reason,
        )


def reduce_workflow(
    state: WorkflowState,
    event_type: str,
    payload: Mapping[str, Any],
) -> WorkflowState:
    """Pure deterministic reduction: (WorkflowState, Event) -> WorkflowState (Invariant I9)."""
    if event_type == "NodeScheduled":
        node_id = str(payload.get("nodeId", ""))
        return state.schedule_node(node_id)
    if event_type == "NodeSettled":
        node_id = str(payload.get("nodeId", ""))
        output_digest = payload.get("outputDigest")
        return state.settle_node(node_id, str(output_digest) if output_digest else None)
    if event_type == "WorkflowCompleted":
        result_digest = payload.get("resultDigest")
        return state.complete(str(result_digest) if result_digest else None)
    if event_type == "WorkflowSuspended":
        reason = str(payload.get("reason", "unknown"))
        return state.suspend(reason)
    return state
