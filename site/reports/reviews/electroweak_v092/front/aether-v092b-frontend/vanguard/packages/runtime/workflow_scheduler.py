"""Event-sourced workflow scheduler executing typed DAG nodes (Invariant I1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from ..domain.workflows.contracts import WorkflowNode, WorkflowSpec
from ..domain.workflows.reducer import WorkflowState, reduce_workflow
from ..ports.blob_store import BlobStorePort
from .transform_runtime import TransformRuntime


@dataclass(frozen=True, slots=True)
class WorkflowExecutionOutcome:
    workflow_id: str
    completed: bool
    final_state: WorkflowState
    result_digest: str | None
    events: tuple[dict[str, Any], ...]


class WorkflowScheduler:
    """Orchestrates ephemeral execution of workflow DAG nodes without granting authority."""

    def __init__(
        self,
        spec: WorkflowSpec,
        transform_runtime: TransformRuntime,
        blob_store: BlobStorePort,
        node_executors: Mapping[str, Callable[[WorkflowNode, str | None], tuple[str | None, str]]] | None = None,
    ) -> None:
        self._spec = spec
        self._transform_runtime = transform_runtime
        self._blob_store = blob_store
        self._executors = dict(node_executors or {})

    def run(
        self,
        workflow_id: str,
        initial_artifact_digest: str | None = None,
    ) -> WorkflowExecutionOutcome:
        """Run workflow from entry node to terminal settlement."""
        state = WorkflowState(
            workflow_id=workflow_id,
            topology_id=self._spec.topology_id,
        )
        events: list[dict[str, Any]] = []

        current_node_id: str | None = self._spec.entry_node
        current_input_digest: str | None = initial_artifact_digest

        cycle_count = 0
        max_cycles = self._spec.max_cycles * len(self._spec.nodes)

        while current_node_id is not None and not state.completed and not state.suspended:
            cycle_count += 1
            if cycle_count > max_cycles:
                state = state.suspend("CYCLE_LIMIT_EXCEEDED")
                events.append({"type": "WorkflowSuspended", "payload": {"reason": "CYCLE_LIMIT_EXCEEDED"}})
                break

            node = self._spec.get_node(current_node_id)
            if node is None:
                state = state.suspend(f"NODE_NOT_FOUND:{current_node_id}")
                events.append({"type": "WorkflowSuspended", "payload": {"reason": f"NODE_NOT_FOUND:{current_node_id}"}})
                break

            # 1. Schedule event
            sched_payload = {"nodeId": node.id, "attempt": state.node_attempts.get(node.id, 0) + 1}
            state = reduce_workflow(state, "NodeScheduled", sched_payload)
            events.append({"type": "NodeScheduled", "payload": sched_payload})

            # 2. Execute node based on kind
            output_digest: str | None = None
            condition_signal = "default"

            if node.kind == "transform":
                if current_input_digest:
                    res = self._transform_runtime.execute(node.policy_ref, current_input_digest)
                    output_digest = res.output_digest
                    condition_signal = res.status
                else:
                    condition_signal = "skipped_empty_input"
            elif node.id in self._executors:
                executor = self._executors[node.id]
                output_digest, condition_signal = executor(node, current_input_digest)
            elif node.kind in self._executors:
                executor = self._executors[node.kind]
                output_digest, condition_signal = executor(node, current_input_digest)
            else:
                # Default pass-through for uncustomized node kinds in testing
                output_digest = current_input_digest
                condition_signal = "passed"

            # 3. Settle event
            settle_payload = {"nodeId": node.id, "outputDigest": output_digest, "condition": condition_signal}
            state = reduce_workflow(state, "NodeSettled", settle_payload)
            events.append({"type": "NodeSettled", "payload": settle_payload})

            # 4. Route along outgoing edges
            edges = self._spec.outgoing_edges(node.id)
            next_node_id: str | None = None
            for edge in edges:
                if edge.condition is None or edge.condition == condition_signal or edge.condition == "default":
                    next_node_id = edge.to_node
                    break

            current_input_digest = output_digest
            current_node_id = next_node_id

        if not state.suspended and not state.completed:
            complete_payload = {"resultDigest": current_input_digest}
            state = reduce_workflow(state, "WorkflowCompleted", complete_payload)
            events.append({"type": "WorkflowCompleted", "payload": complete_payload})

        return WorkflowExecutionOutcome(
            workflow_id=workflow_id,
            completed=state.completed,
            final_state=state,
            result_digest=state.result_digest,
            events=tuple(events),
        )
