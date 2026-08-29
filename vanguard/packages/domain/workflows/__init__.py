"""Workflow domain contracts and pure state reducer."""

from vanguard.packages.domain.workflows.contracts import (
    NodeKind,
    WorkflowEdge,
    WorkflowNode,
    WorkflowSpec,
)
from vanguard.packages.domain.workflows.reducer import (
    WorkflowState,
    reduce_workflow,
)

__all__ = [
    "NodeKind",
    "WorkflowEdge",
    "WorkflowNode",
    "WorkflowSpec",
    "WorkflowState",
    "reduce_workflow",
]
