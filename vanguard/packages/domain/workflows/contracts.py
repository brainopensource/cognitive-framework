"""Pure domain value objects and AST contracts for workflow topology v2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Mapping

NodeKind = Literal[
    "transform",
    "model",
    "episode",
    "effect",
    "gate",
    "router",
    "join",
    "interrupt",
    "evaluator",
]


@dataclass(frozen=True, slots=True)
class WorkflowNode:
    """A typed execution node within a workflow DAG."""

    id: str
    kind: NodeKind
    policy_ref: str
    config_digest: str = ""


@dataclass(frozen=True, slots=True)
class WorkflowEdge:
    """A directed, optionally conditional edge between workflow nodes."""

    from_node: str
    to_node: str
    condition: str | None = None


@dataclass(frozen=True, slots=True)
class WorkflowSpec:
    """The immutable specification for a version 2 workflow topology."""

    topology_id: str
    version: str
    nodes: tuple[WorkflowNode, ...]
    edges: tuple[WorkflowEdge, ...]
    entry_node: str
    api: str = "mhf.topology/2"
    max_cycles: int = 5

    def get_node(self, node_id: str) -> WorkflowNode | None:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def outgoing_edges(self, node_id: str) -> tuple[WorkflowEdge, ...]:
        return tuple(edge for edge in self.edges if edge.from_node == node_id)
