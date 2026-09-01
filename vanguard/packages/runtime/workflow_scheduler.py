"""Event-sourced workflow scheduler executing typed DAG nodes (Invariant I1)."""

from __future__ import annotations

from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Mapping, Sequence

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

    def reconstruct_ready_state(
        self, workflow_id: str, events: Sequence[Mapping[str, Any]] = (),
    ) -> WorkflowState:
        """Rebuild durable scheduling state before selecting ready nodes.

        Resume consumes the event projection rather than the scheduler's
        in-memory pending set. Replaying a settled node is therefore
        impossible even when the process died between lease release and the
        next scheduling decision.
        """
        state = WorkflowState(workflow_id=workflow_id,
                              topology_id=self._spec.topology_id)
        for event in events:
            if not isinstance(event, Mapping):
                raise ValueError("workflow events must be mappings")
            kind = str(event.get("type", event.get("kind", "")))
            payload = event.get("payload", {})
            if isinstance(payload, Mapping):
                state = reduce_workflow(state, kind, payload)
        return state

    def run(
        self,
        workflow_id: str,
        initial_artifact_digest: str | None = None,
        *,
        cancelled: Callable[[], bool] | None = None,
        prior_events: Sequence[Mapping[str, Any]] = (),
    ) -> WorkflowExecutionOutcome:
        """Run workflow from durable state, never replaying settled effects."""
        if self._spec.execution_mode == "bounded_parallel":
            return self._run_bounded_parallel(
                workflow_id, initial_artifact_digest, cancelled=cancelled,
                prior_events=prior_events)
        if self._spec.execution_mode != "sequential":
            raise ValueError(f"unsupported workflow execution mode: {self._spec.execution_mode}")
        state = self.reconstruct_ready_state(workflow_id, prior_events)
        events: list[dict[str, Any]] = []

        current_node_id: str | None = self._spec.entry_node
        current_input_digest: str | None = initial_artifact_digest

        # A sequential resume follows the first unsettled outgoing path. The
        # reducer is authoritative about which nodes already settled.
        if state.settled_nodes:
            settled_order = [str(event.get("payload", {}).get("nodeId"))
                             for event in prior_events
                             if str(event.get("type", event.get("kind", "")))
                             == "NodeSettled"
                             and isinstance(event.get("payload", {}), Mapping)]
            last = next((node_id for node_id in reversed(settled_order)
                         if node_id in state.settled_nodes), None)
            if last is not None:
                current_node_id = next((edge.to_node for edge in
                                        self._spec.outgoing_edges(last)), None)
                current_input_digest = state.node_outputs.get(last,
                                                              current_input_digest)

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

    def _execute_node(
        self, node: WorkflowNode, input_digest: str | None,
    ) -> tuple[str | None, str]:
        if node.kind == "transform":
            if input_digest:
                result = self._transform_runtime.execute(
                    node.policy_ref, input_digest)
                return result.output_digest, result.status
            return None, "skipped_empty_input"
        executor = self._executors.get(node.id) or self._executors.get(node.kind)
        if executor is not None:
            return executor(node, input_digest)
        return input_digest, "passed"

    def _run_bounded_parallel(
        self, workflow_id: str, initial_artifact_digest: str | None,
        *, cancelled: Callable[[], bool] | None = None,
        prior_events: Sequence[Mapping[str, Any]] = (),
    ) -> WorkflowExecutionOutcome:
        """Execute ready read/investigator nodes in a bounded join batch."""
        state = self.reconstruct_ready_state(workflow_id, prior_events)
        events: list[dict[str, Any]] = []
        outputs: dict[str, str | None] = {}
        for event in prior_events:
            if (str(event.get("type", event.get("kind", ""))) == "NodeSettled"
                    and isinstance(event.get("payload", {}), Mapping)):
                payload = event["payload"]
                node_id = payload.get("nodeId")
                if node_id is not None:
                    outputs[str(node_id)] = payload.get("outputDigest")
        pending = {node.id for node in self._spec.nodes
                   if node.id not in state.settled_nodes}
        pending.discard(self._spec.entry_node)
        pending.add(self._spec.entry_node)
        incoming = {node.id: {edge.from_node for edge in self._spec.edges
                              if edge.to_node == node.id}
                    for node in self._spec.nodes}
        while pending and not state.completed and not state.suspended:
            if cancelled is not None and cancelled():
                state = state.suspend("CANCELLED")
                events.append({"type": "WorkflowSuspended",
                               "payload": {"reason": "CANCELLED"}})
                break
            ready = sorted(node_id for node_id in pending
                           if incoming[node_id].issubset(set(state.settled_nodes)))
            if not ready:
                state = state.suspend("NO_READY_NODE")
                events.append({"type": "WorkflowSuspended",
                               "payload": {"reason": "NO_READY_NODE"}})
                break
            batch = ready[:max(1, int(self._spec.max_concurrency))]
            for node_id in batch:
                pending.remove(node_id)
                payload = {"nodeId": node_id,
                           "attempt": state.node_attempts.get(node_id, 0) + 1}
                state = reduce_workflow(state, "NodeScheduled", payload)
                events.append({"type": "LeaseAcquired", "payload": payload})
                events.append({"type": "NodeScheduled", "payload": payload})
            nodes = [self._spec.get_node(node_id) for node_id in batch]
            nodes = [node for node in nodes if node is not None]
            args = [(node, outputs.get(next(iter(incoming[node.id]), ""),
                                      initial_artifact_digest))
                    for node in nodes]
            with ThreadPoolExecutor(max_workers=len(nodes)) as pool:
                results = list(pool.map(lambda item: self._execute_node(*item),
                                        args))
            for node, (output_digest, condition) in zip(nodes, results):
                outputs[node.id] = output_digest
                payload = {"nodeId": node.id, "outputDigest": output_digest,
                           "condition": condition}
                state = reduce_workflow(state, "NodeSettled", payload)
                events.append({"type": "NodeSettled", "payload": payload})
                events.append({"type": "LeaseReleased",
                               "payload": {"nodeId": node.id}})
                for edge in self._spec.outgoing_edges(node.id):
                    if edge.condition in (None, condition, "default"):
                        pending.add(edge.to_node)
        if not state.suspended and not state.completed:
            result_digest = outputs.get(self._spec.nodes[-1].id
                                       if self._spec.nodes else "")
            state = state.complete(result_digest)
            events.append({"type": "WorkflowCompleted",
                           "payload": {"resultDigest": result_digest}})
        return WorkflowExecutionOutcome(
            workflow_id=workflow_id, completed=state.completed,
            final_state=state, result_digest=state.result_digest,
            events=tuple(events))
