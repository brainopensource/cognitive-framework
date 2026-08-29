"""Workflow state recovery through event replay."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..domain.workflows.reducer import WorkflowState, reduce_workflow


def replay_workflow_events(
    workflow_id: str,
    topology_id: str,
    events: Sequence[Mapping[str, Any]],
) -> WorkflowState:
    """Reconstruct exact workflow state from an immutable event sequence (Invariant I9)."""
    state = WorkflowState(workflow_id=workflow_id, topology_id=topology_id)
    for ev in events:
        event_type = ev.get("type", "")
        payload = ev.get("payload", {})
        state = reduce_workflow(state, event_type, payload)
    return state
