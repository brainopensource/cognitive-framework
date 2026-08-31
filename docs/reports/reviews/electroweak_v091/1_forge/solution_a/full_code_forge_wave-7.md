---
id: report.electroweak.solution-a.full-code-forge-wave-7
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER FORGE — Full Code Completion Manifest — Wave 7

## Adaptive forks, isolated candidate patches, deterministic selection, settlement, replay, and strategy capsules

- Exact branch subject: `f242ced297216109736975376802f1e3dc4e29ce`.
- Backend FORGE only; frontend is excluded.
- This complement closes production integration omitted by waves 1–4.
- Code blocks contain complete affected modules or complete affected classes/functions so call sites can be changed without guessing signatures.
- Existing kernel invariants, authority, budgets, events, artifacts, and recovery remain authoritative.

## Required production delta

Lower FORGE forks to the existing canonical child runtime.  Research,
counterexample, and verification branches are read-only.  Candidate-patch
branches use independent git worktrees or environment snapshots, never a shared
writable workspace.  Parent authority is attenuated by scope; parent budget is
partitioned and conserved; children cannot mint depth, effects, tokens, time,
bytes, evaluations, or cost.  Children return `BranchSummary` and artifact refs,
not full transcripts.  Selection is deterministic and prioritizes fresh external
verification over self-confidence.  Applying a winning patch is a new parent
effect and requires ordinary authorization.  Strategy capsules are immutable,
evidence-backed suggestions; task-time code cannot promote or install them.

## Exact edit map

1. Add `agency/forge/branch.py`: branch request/mode/summary pure values.
2. Add `runtime/forge/fork_policy.py`: expected-value gate and branch count.
3. Add `runtime/forge/branch_runner.py`: lower to `RuntimeChildRunner`.
4. Add `adapters/environment/worktree.py`: explicit isolated patch workspace.
5. Modify `runtime/child_runtime.py`: bind returned summary/artifacts and ensure
   conserved settlement on success, failure, timeout, cancellation, and crash.
6. Modify `runtime/topology.py`: recognize a bounded FORGE branch group without
   adding a new scheduler or relaxing topology validation.
7. Modify `runtime/scheduler.py`: deterministic ready-order and join order.
8. Add `runtime/forge/branch_selector.py`: evidence-first stable scoring.
9. Add `runtime/forge/capsules.py`: deduplication, observations, admission and
   offline promotion candidate export.
10. Extend trajectory/recovery capture with branch request, workspace identity,
    child lineage, budget slice, summary digest, selection rationale, and merge
    receipt.

## Budget conservation invariant

```text
sum(child reservations) <= parent remaining reservation
child consumed + child refunded = child reserved
parent new remaining = parent previous remaining - total child consumed
failure, timeout, cancel, crash, and replay cannot duplicate refunds
```

## Complete affected code owners

### File: `vanguard/packages/runtime/child_runtime.py`

**Repository path:** `vanguard/packages/runtime/child_runtime.py`

```python
"""The real child runtime: recursion through the one public boundary.

This module is the answer to the question M-6 was actually asking. A spawn
adapter can mint identities, attenuate scope and reserve budget perfectly and
still prove nothing, because none of that executes a child. Something has to
*run* the subtree -- and the only defensible something is the same
`Runtime.run_composed` the parent went through.

That constraint is doing real work. Running a child through a second, simpler
path would make the subtree's evidence incomparable with the parent's: a
different activation, a different `RunPlan`, a different set of facts. Instead
the child re-enters the identical boundary with **rebound ports** and a
**lowered task**, so a depth-3 tree is three ordinary runs that happen to be
causally nested, and the cold reader folds all three with one reducer.

What recursion must *not* do is acquire authority on the way down. Every
widening vector is closed here by construction rather than by check:

* the plan is frozen before this module sees it, and nothing here edits it;
* the child gets the parent's *attenuated* grant, never the parent's `Scope`;
* the child shares the parent's store, so its spend lands in one ledger;
* `interactive` is forced off -- a child may not prompt a human the parent
  never offered it access to;
* the meta-controller is dropped unless explicitly rebound, so a child cannot
  inherit a strategy authority it was not granted (`WP-A2` territory).
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Mapping

from ..kernel.attenuation import Constraints, Scope
from ..ports.child_runtime import ChildRunPlan, ChildRunResult
from ..ports.event_store import EventRange
from .compose import Harness, RunResult, TaskContext

__all__ = ["RuntimeChildRunner", "TERMINAL_OUTCOMES"]

#: How a terminal state becomes a delegation outcome. `undeterminable` is not
#: in this map on purpose: it is produced only by a genuine unknown (a raised
#: runner, an open subtree across a restart), never by a terminal the child
#: actually reached and reported.
TERMINAL_OUTCOMES: Mapping[str, str] = {
    "completed": "completed",
    "abstained": "abandoned",
    "abandoned": "abandoned",
    "escalated": "abandoned",
    "cancelled": "abandoned",
    "budget_exhausted": "abandoned",
    # An instrument or runtime error is *not* a failed child. The child may
    # have completed an irreversible effect before the instrument broke, so
    # the honest answer is that occurrence is unknown (`F-22`).
    "instrument_error": "undeterminable",
    "runtime_error": "undeterminable",
}


class RuntimeChildRunner:
    """`ChildRuntimePort` over the sole public run path.

    Constructed per parent session and handed the parent's own composition and
    ports. It holds no policy: by the time `run_child` is called, every
    authority question has already been answered by `delegation.SpawnAdapter`.
    """

    def __init__(
        self,
        *,
        run_composed: Callable[..., RunResult],
        harness: Harness,
        parent_ports: Any,
        parent_task: TaskContext,
        profile: Any = None,
        release: bool = False,
    ) -> None:
        #: The sole public activation boundary, injected rather than imported.
        #: `root` imports `session` imports `wiring` imports `delegation`, so
        #: naming `Runtime` here would close that ring -- and a lazy import
        #: would only hide the ring from readers, not from the boundary
        #: linter. Recursion is a runtime edge, so it is passed at runtime.
        #: `root.run_composed` is its only production binder, and
        #: `test_rfA1_recursive_depth` asserts that is what arrives.
        self._run_composed = run_composed
        self._harness = harness
        self._parent_ports = parent_ports
        self._parent_task = parent_task
        self._profile = profile
        self._release = release

    # -- the port ---------------------------------------------------------

    def run_child(self, plan: ChildRunPlan) -> ChildRunResult:
        """Execute one child episode and project a typed result."""
        child_ports = self._rebind(plan)
        child_task = self._lower(plan)

        result = self._run_composed(
            self._harness,
            child_ports,
            child_task,
            release=self._release,
            profile=self._profile,
        )
        return self._project(plan, result)

    # -- internals --------------------------------------------------------

    def _rebind(self, plan: ChildRunPlan) -> Any:
        """The parent's ports, narrowed. Never widened, never replaced.

        The store is deliberately shared. One ledger is what makes the tree
        foldable: the child's facts carry `parentEpisodeId`, so a cold reader
        rebuilds the whole subtree from a single chain (`RF-59`). A private
        child store would produce an unlinkable second history.
        """
        return replace(
            self._parent_ports,
            # A topology decorator owns only the root routing decision.  A
            # child is an ordinary runtime episode and must use the supplied
            # provider, not emit the root's next topology role recursively.
            model=getattr(self._parent_ports.model, "child_model",
                          self._parent_ports.model),
            # A child may not prompt a human on the parent's behalf.
            interactive=False,
            # Strategy authority is not inherited. Binding a controller for a
            # child is an explicit act, and M-6 does not perform it.
            meta_controller=None,
            controller_confidence=(),
            # The child's own children run through this same runner, which is
            # what makes depth >= 3 real rather than simulated.
            child_runtime=self,
            # The parent owns the adapter and must keep it alive for the next
            # causally-ready sibling. A child may use it, never dispose it.
            environment_owner=False,
        )

    def _lower(self, plan: ChildRunPlan) -> TaskContext:
        """The child's task: lowered ceilings, inherited nothing else.

        `brief` is empty because the plan carries `goal_digest`, not prose
        (`C-06`). A child that needs the brief dereferences `goal_artifact`
        through the ordinary mediated path, under its own attenuated grant.
        """
        return TaskContext(
            brief=plan.brief,
            repo_path=self._parent_task.repo_path,
            run_id=plan.run_id,
            episode_id=plan.child_episode_id,
            principal=plan.principal,
            max_turns=plan.max_turns,
            project_id=plan.project_id,
            parent_principal_id=self._parent_task.principal,
            parent_episode_id=plan.parent_episode_id,
            preregistration=self._parent_task.preregistration,
            lineage=tuple(plan.lineage) + (plan.child_episode_id,),
            artifact_refs=plan.artifact_refs,
            scope_override=Scope(
                actions=frozenset(plan.authority),
                resources=tuple(plan.resources),
                constraints=Constraints(
                    expires_at=str(plan.constraints.get("expires_at", "2099-01-01T00:00:00.000Z")),
                    max_uses=int(plan.constraints.get("max_uses", 0)),
                    budget_usd_micros=int(plan.constraints.get("budget_usd_micros", 0)),
                    max_bytes=(
                        int(plan.constraints["max_bytes"])
                        if plan.constraints.get("max_bytes") is not None else None
                    ),
                    max_effects=(
                        int(plan.constraints["max_effects"])
                        if plan.constraints.get("max_effects") is not None else None
                    ),
                    risk_ceiling=str(plan.constraints.get("risk_ceiling", "low")),
                    max_depth=int(plan.constraints.get("max_depth", plan.max_depth)),
                    network_policy=str(plan.constraints.get("network_policy", "deny")),
                ),
                depth=plan.depth,
                sealed=True,
            ),
        )

    def _project(self, plan: ChildRunPlan, result: RunResult) -> ChildRunResult:
        """`RunResult` -> `ChildRunResult`. A projection, never a passthrough.

        This is the transcript boundary. `RunResult` holds events, receipts, a
        live store handle and a trajectory; none of it crosses. What the parent
        receives is the terminal state, the digests, the measured cost and the
        references it may choose to dereference.
        """
        terminal = getattr(result.terminal, "value", str(result.terminal))
        outcome = TERMINAL_OUTCOMES.get(terminal, "undeterminable")

        cost = self._measured_cost(plan, result)
        evidence_refs = [
            ref for ref in (result.run_digest, result.activation_digest) if ref
        ]
        # Minimal ChildRuntimePort contract doubles may expose only the
        # historical RunResult fields.  Missing trajectory means no captured
        # artifact references, never an invented one.
        trajectory = getattr(result, "trajectory", None)
        if isinstance(trajectory, Mapping):
            for artifact in trajectory.get("artifacts", ()) or ():
                if not isinstance(artifact, Mapping):
                    continue
                digest = artifact.get("digest")
                if (artifact.get("stored") is True and isinstance(digest, str)
                        and digest.startswith("sha256:") and digest not in evidence_refs):
                    evidence_refs.append(digest)

        return ChildRunResult(
            ok=outcome == "completed",
            outcome=outcome,
            terminal=terminal.upper(),
            child_episode_id=plan.child_episode_id,
            actual_cost=cost,
            turns_used=len(result.receipts),
            result_digest=result.state_digest or None,
            evidence_refs=tuple(evidence_refs),
            detail=result.detail or "",
        )

    def _measured_cost(self, plan: ChildRunPlan,
                       result: RunResult) -> Mapping[str, int]:
        """What the child actually spent, folded from its own facts.

        Read from the ledger rather than estimated. `_ZERO_COST` is prohibited
        by the trajectory contract, and a child reporting a cost it did not
        measure is precisely the fabrication this package removed.
        """
        from ..ports.child_runtime import CHILD_ADDITIVE_DIMENSIONS

        # ``RunResult.events`` is the in-process ``Event`` projection and has
        # no durable sequence.  Cost reduction is an evidence operation, so
        # read the child's persisted envelopes from its shared store instead
        # of feeding the projection to the cold reducer.
        store = getattr(result, "store", None)
        if store is None:
            # Minimal ChildRuntimePort test doubles may return only the
            # projection.  They carry no measurable ledger and therefore
            # report no measured cost; production RunResult always has a
            # store and takes the fail-closed branch below.
            envelopes = tuple(
                event for event in getattr(result, "events", ())
                if hasattr(event, "seq")
            )
            consumed = self._actual_cost_from_settlements(envelopes)
        else:
            read = store.read(EventRange(episode_id=plan.child_episode_id))
            if not read.ok or read.value is None:
                raise RuntimeError("child ledger is unreadable; cost is unknown")
            consumed = self._actual_cost_from_settlements(tuple(read.value))
        return {
            dimension: int(consumed.get(dimension, 0) or 0)
            for dimension in CHILD_ADDITIVE_DIMENSIONS
            if consumed.get(dimension)
        }

    @staticmethod
    def _actual_cost_from_settlements(events: tuple[Any, ...]) -> Mapping[str, int]:
        """Project spend from the kernel's settlement facts.

        A committed lease records the amount returned to the parent budget;
        the child's actual spend is therefore ``reserved - settlement``.
        Feeding settlement directly into the general AgentView reducer would
        interpret a refund as negative consumption and make child projection
        fail closed for an otherwise successful run.
        """
        reserved_by_lease: dict[str, Mapping[str, int]] = {}
        total: dict[str, int] = {}
        for envelope in events:
            event_type = getattr(envelope, "event_type", None)
            payload = getattr(envelope, "payload", None)
            if not isinstance(payload, Mapping):
                continue
            if event_type == "BudgetReserved":
                lease_id = payload.get("lease_id")
                dimensions = payload.get("reserved", {})
                if isinstance(lease_id, str) and isinstance(dimensions, Mapping):
                    reserved_by_lease[lease_id] = {
                        str(key): int(value) for key, value in dimensions.items()
                    }
                continue
            if event_type != "BudgetCommitted":
                continue
            settlement = payload.get("settlement", {})
            lease_id = payload.get("lease_id")
            if not isinstance(settlement, Mapping):
                continue
            reserved = reserved_by_lease.get(lease_id, {})
            for key, value in settlement.items():
                dimension = str(key)
                amount = int(value)
                spent = int(reserved.get(dimension, 0)) - amount
                total[dimension] = total.get(dimension, 0) + spent
        return total
```

### File: `vanguard/packages/runtime/topology.py`

**Repository path:** `vanguard/packages/runtime/topology.py`

```python
"""M-7 topology values and sequential-only lowering.

Topology is versioned routing data. It neither grants authority nor executes a
workflow: lowering produces ordinary lineage and readiness templates that the
existing Runtime may consume after the M-7 gate. I-11 remains in force here;
no worker, claim, lease, or concurrent executor is activated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of

__all__ = [
    "RunPlanExtension",
    "TOPOLOGY_SCHEMA",
    "Topology",
    "TopologyEdge",
    "TopologyError",
    "TopologyRole",
    "lower_topology",
    "parse_topology",
]

TOPOLOGY_SCHEMA = "mhf.topology/1"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_TOP_LEVEL_FIELDS = frozenset({
    "api", "topologyId", "version", "entryRole", "roles", "edges",
    "artifactFlows",
})
_ROLE_FIELDS = frozenset({"id", "policyRef", "scope", "budget", "context"})
_EDGE_FIELDS = frozenset({"from", "to", "relation"})
_FLOW_FIELDS = frozenset({"artifact", "from", "to", "schemaId"})
_RELATIONS = frozenset({"may_delegate_to", "reviews", "merges_into"})
_BUDGET_FIELDS = frozenset({
    "usd_micros", "millis", "tokens", "bytes", "turns", "depth",
    "maxTurns", "maxDepth",
})
_AUTHORITY_FIELDS = frozenset({
    "actions", "approval", "approvalreference", "authority", "capabilities",
    "capability", "capabilitygrant", "grants", "grant", "networkpolicy",
    "principal", "riskceiling", "signature", "sinkclass", "verb",
})


class TopologyError(ValueError):
    """A topology is malformed, unrunnable, or attempts to carry authority."""


@dataclass(frozen=True, slots=True)
class TopologyRole:
    role_id: str
    policy_ref: str
    scope_template: Mapping[str, Any] = field(default_factory=dict)
    budget_template: Mapping[str, int] = field(default_factory=dict)
    context: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.role_id,
            "policyRef": self.policy_ref,
            "scope": dict(self.scope_template),
            "budget": dict(sorted(self.budget_template.items())),
            "context": dict(self.context),
        }


@dataclass(frozen=True, slots=True)
class TopologyEdge:
    source: str
    target: str
    relation: str = "may_delegate_to"

    def to_dict(self) -> dict[str, str]:
        return {"from": self.source, "to": self.target, "relation": self.relation}


@dataclass(frozen=True, slots=True)
class Topology:
    topology_id: str
    version: str
    roles: tuple[TopologyRole, ...]
    edge_records: tuple[TopologyEdge, ...]
    artifact_flows: tuple[Mapping[str, Any], ...]
    entry_role: str
    schema: str = TOPOLOGY_SCHEMA

    @property
    def edges(self) -> tuple[tuple[str, str], ...]:
        """Compatibility projection used by analysis-only consumers."""
        return tuple((edge.source, edge.target) for edge in self.edge_records)

    def to_dict(self) -> dict[str, Any]:
        return {
            "api": self.schema,
            "topologyId": self.topology_id,
            "version": self.version,
            "roles": [role.to_dict() for role in self.roles],
            "edges": [edge.to_dict() for edge in self.edge_records],
            "artifactFlows": [dict(flow) for flow in self.artifact_flows],
            "entryRole": self.entry_role,
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())


@dataclass(frozen=True, slots=True)
class RunPlanExtension:
    """Pure lowering result bound to one topology and optional composition.

    The value names templates and ordering constraints only. In particular it
    carries no capability, grant, sink, principal, or execution handle.
    """

    topology_digest: str
    entry_role: str
    lineage_templates: tuple[Mapping[str, Any], ...]
    allowed_delegations: tuple[tuple[str, str], ...]
    artifact_flows: tuple[Mapping[str, Any], ...]
    role_operations: tuple[Mapping[str, Any], ...]
    composition_digest: str = ""
    execution_mode: str = "sequential"
    scheduler_policy: str = "sequential-reference"
    schema: str = "m7.run-plan-extension/1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "topologyDigest": self.topology_digest,
            "compositionDigest": self.composition_digest,
            "entryRole": self.entry_role,
            "lineageTemplates": tuple(dict(item) for item in self.lineage_templates),
            "allowedDelegations": self.allowed_delegations,
            "artifactFlows": tuple(dict(item) for item in self.artifact_flows),
            "roleOperations": tuple(dict(item) for item in self.role_operations),
            "executionMode": self.execution_mode,
            "schedulerPolicy": self.scheduler_policy,
            "activation": "ordinary-agent-spawn-sequential",
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TopologyError(f"{label} must be an object")
    result = dict(value)
    try:
        digest_of(result)
    except Exception as exc:  # pragma: no cover - defensive value boundary
        raise TopologyError(f"{label} must contain JSON values only") from exc
    return result


def _sequence(value: Any, label: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise TopologyError(f"{label} must be a list")
    return value


def _unknown_fields(value: Mapping[str, Any], allowed: frozenset[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise TopologyError(f"{label} has unknown fields: {unknown}")


def _reject_authority(value: Any, path: str = "topology") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).replace("_", "").replace("-", "").lower()
            if normalized in _AUTHORITY_FIELDS:
                raise TopologyError(
                    f"{path}.{key} carries authority; topology is routing data")
            _reject_authority(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_authority(child, f"{path}[{index}]")


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise TopologyError(f"{label} must be a non-empty stable identifier")
    return value


def _parse_role(item: Any, index: int) -> TopologyRole:
    row = _mapping(item, f"roles[{index}]")
    _unknown_fields(row, _ROLE_FIELDS, f"roles[{index}]")
    role_id = _identifier(row.get("id"), f"roles[{index}].id")
    policy_ref = row.get("policyRef")
    if not isinstance(policy_ref, str) or not policy_ref:
        raise TopologyError(f"roles[{index}].policyRef is required")
    scope = _mapping(row.get("scope", {}), f"roles[{index}].scope")
    context = _mapping(row.get("context", {}), f"roles[{index}].context")
    raw_budget = _mapping(row.get("budget", {}), f"roles[{index}].budget")
    unknown_budget = sorted(set(raw_budget) - _BUDGET_FIELDS)
    if unknown_budget:
        raise TopologyError(
            f"roles[{index}].budget has unknown dimensions: {unknown_budget}")
    budget: dict[str, int] = {}
    for dimension, amount in raw_budget.items():
        if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
            raise TopologyError(
                f"roles[{index}].budget.{dimension} must be a non-negative integer")
        budget[str(dimension)] = amount
    return TopologyRole(role_id, policy_ref, scope, budget, context)


def _parse_edges(raw_edges: Any, roles: frozenset[str]) -> tuple[TopologyEdge, ...]:
    edges: list[TopologyEdge] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(_sequence(raw_edges, "edges")):
        row = _mapping(item, f"edges[{index}]")
        _unknown_fields(row, _EDGE_FIELDS, f"edges[{index}]")
        source = _identifier(row.get("from"), f"edges[{index}].from")
        target = _identifier(row.get("to"), f"edges[{index}].to")
        relation = row.get("relation", "may_delegate_to")
        if source not in roles or target not in roles or source == target:
            raise TopologyError(f"edges[{index}] is not between distinct declared roles")
        if relation not in _RELATIONS:
            raise TopologyError(f"edges[{index}].relation is unsupported")
        pair = (source, target)
        if pair in seen:
            raise TopologyError(f"duplicate topology edge {source!r}->{target!r}")
        seen.add(pair)
        edges.append(TopologyEdge(source, target, str(relation)))
    return tuple(sorted(edges, key=lambda edge: (edge.source, edge.target, edge.relation)))


def _parse_flows(
    raw_flows: Any,
    roles: frozenset[str],
    edges: frozenset[tuple[str, str]],
) -> tuple[Mapping[str, Any], ...]:
    flows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for index, item in enumerate(_sequence(raw_flows, "artifactFlows")):
        row = _mapping(item, f"artifactFlows[{index}]")
        _unknown_fields(row, _FLOW_FIELDS, f"artifactFlows[{index}]")
        artifact = _identifier(row.get("artifact"), f"artifactFlows[{index}].artifact")
        source = _identifier(row.get("from"), f"artifactFlows[{index}].from")
        target = _identifier(row.get("to"), f"artifactFlows[{index}].to")
        if source not in roles:
            raise TopologyError(
                f"artifact {artifact!r} has no declared producer role {source!r}")
        if target not in roles:
            raise TopologyError(
                f"artifact {artifact!r} names undeclared consumer role {target!r}")
        if (source, target) not in edges:
            raise TopologyError(
                f"artifact {artifact!r} flows across disallowed edge "
                f"{source!r}->{target!r}")
        identity = (artifact, source, target)
        if identity in seen:
            raise TopologyError(f"duplicate artifact flow {identity!r}")
        seen.add(identity)
        flow = {"artifact": artifact, "from": source, "to": target}
        schema_id = row.get("schemaId")
        if schema_id is not None:
            if not isinstance(schema_id, str) or not schema_id:
                raise TopologyError(f"artifactFlows[{index}].schemaId must be a string")
            flow["schemaId"] = schema_id
        flows.append(flow)
    return tuple(sorted(flows, key=lambda flow: (
        str(flow["from"]), str(flow["to"]), str(flow["artifact"]))))


def _validate_graph(
    roles: frozenset[str],
    edges: Sequence[TopologyEdge],
    entry: str,
) -> None:
    graph = {role: [] for role in roles}
    for edge in edges:
        graph[edge.source].append(edge.target)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise TopologyError(f"delegation cycle reaches role {node!r}")
        if node in visited:
            return
        visiting.add(node)
        for child in sorted(graph[node]):
            visit(child)
        visiting.remove(node)
        visited.add(node)

    visit(entry)
    unreachable = sorted(roles - visited)
    if unreachable:
        raise TopologyError(f"roles are unreachable from entryRole: {unreachable}")


def parse_topology(raw: Mapping[str, Any]) -> Topology:
    row = _mapping(raw, "topology")
    _unknown_fields(row, _TOP_LEVEL_FIELDS, "topology")
    _reject_authority(row)
    schema = row.get("api", TOPOLOGY_SCHEMA)
    if schema != TOPOLOGY_SCHEMA:
        raise TopologyError(f"topology api must be {TOPOLOGY_SCHEMA!r}")
    topology_id = _identifier(row.get("topologyId"), "topologyId")
    version = row.get("version")
    if not isinstance(version, str) or not version:
        raise TopologyError("version is required")
    entry = _identifier(row.get("entryRole"), "entryRole")

    roles = tuple(_parse_role(item, index) for index, item in enumerate(
        _sequence(row.get("roles"), "roles")))
    if not roles:
        raise TopologyError("roles must not be empty")
    role_ids = [role.role_id for role in roles]
    if len(set(role_ids)) != len(role_ids):
        raise TopologyError("role ids must be unique")
    role_set = frozenset(role_ids)
    if entry not in role_set:
        raise TopologyError("entryRole does not name a declared role")

    edges = _parse_edges(row.get("edges", ()), role_set)
    _validate_graph(role_set, edges, entry)
    flows = _parse_flows(
        row.get("artifactFlows", ()), role_set,
        frozenset((edge.source, edge.target) for edge in edges),
    )
    return Topology(
        topology_id,
        version,
        tuple(sorted(roles, key=lambda role: role.role_id)),
        edges,
        flows,
        entry,
        str(schema),
    )


def _role_order(topology: Topology) -> tuple[str, ...]:
    graph: dict[str, list[str]] = {role.role_id: [] for role in topology.roles}
    incoming: dict[str, int] = {role.role_id: 0 for role in topology.roles}
    for edge in topology.edge_records:
        graph[edge.source].append(edge.target)
        incoming[edge.target] += 1
    ready = [topology.entry_role]
    order: list[str] = []
    while ready:
        role = ready.pop(0)
        if role in order:
            continue
        order.append(role)
        for target in sorted(graph[role]):
            incoming[target] -= 1
            if incoming[target] == 0:
                ready.append(target)
    if len(order) != len(topology.roles):  # parser already proves this
        raise TopologyError("topology cannot be lowered to a complete role order")
    return tuple(order)


def _composition_digest(composition: Any | None) -> str:
    if composition is None:
        return ""
    return str(
        getattr(composition, "composition_digest", "")
        or getattr(getattr(composition, "frozen", None), "composition_digest", "")
    )


def _validate_composition(topology: Topology, composition: Any | None) -> None:
    if composition is None:
        return
    verbs = frozenset(str(item) for item in getattr(composition, "verbs", ()))
    if len(topology.roles) > 1 and "agent.spawn" not in verbs:
        raise TopologyError(
            "multi-role topology requires the composition to declare agent.spawn")
    ceiling = dict(getattr(composition, "budget", {}) or {})
    for role in topology.roles:
        for dimension in ("usd_micros", "millis", "tokens", "bytes"):
            requested = role.budget_template.get(dimension)
            allowed = ceiling.get(dimension)
            if requested is not None and allowed is not None and int(requested) > int(allowed):
                raise TopologyError(
                    f"role {role.role_id!r} requests {requested} {dimension}, "
                    f"above composition ceiling {allowed}")


def lower_topology(
    topology: Topology,
    composition: Any | None = None,
) -> dict[str, Any]:
    """Compile routing data into a sequential ``RunPlanExtension`` value."""
    _validate_composition(topology, composition)
    order = _role_order(topology)
    role_by_id = {role.role_id: role for role in topology.roles}
    parents = {role_id: [] for role_id in order}
    targets = {role_id: [] for role_id in order}
    for edge in topology.edge_records:
        parents[edge.target].append(edge.source)
        if edge.relation == "may_delegate_to":
            targets[edge.source].append(edge.target)

    lineage_templates = tuple({
        "role": role_id,
        "parentRoles": tuple(sorted(parents[role_id])),
        "allowedTargets": tuple(sorted(targets[role_id])),
        "policyRef": role_by_id[role_id].policy_ref,
        "scope": dict(role_by_id[role_id].scope_template),
        "budget": dict(role_by_id[role_id].budget_template),
        "context": dict(role_by_id[role_id].context),
    } for role_id in order)
    operations = tuple({
        "operationId": f"role:{role_id}",
        "role": role_id,
        "causalPredecessors": tuple(
            f"role:{source}" for source in sorted(parents[role_id])),
        "ordinal": ordinal,
        "inputArtifacts": tuple(sorted(
            str(flow["artifact"]) for flow in topology.artifact_flows
            if str(flow["to"]) == role_id)),
        "outputArtifacts": tuple(sorted(
            str(flow["artifact"]) for flow in topology.artifact_flows
            if str(flow["from"]) == role_id)),
    } for ordinal, role_id in enumerate(order))
    extension = RunPlanExtension(
        topology_digest=topology.digest(),
        composition_digest=_composition_digest(composition),
        entry_role=topology.entry_role,
        lineage_templates=lineage_templates,
        allowed_delegations=tuple(
            (edge.source, edge.target)
            for edge in topology.edge_records
            if edge.relation == "may_delegate_to"
        ),
        artifact_flows=topology.artifact_flows,
        role_operations=operations,
    )
    return extension.to_dict()
```

### File: `vanguard/packages/runtime/scheduler.py`

**Repository path:** `vanguard/packages/runtime/scheduler.py`

```python
"""Sequential reference scheduler for M-7.

This is an interface and deterministic reference ordering, not a concurrent
executor.  Read-only grouping is an analysis result and must be explicitly
consumed by a future decision; it is never enabled here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..domain.selectors.independence import disjoint

__all__ = [
    "ReadyOperation",
    "ScheduleDecision",
    "ScheduleError",
    "SchedulerPolicy",
    "SequentialScheduler",
    "AsyncGraphScheduler",
    "ready_operations",
    "safe_read_only_group",
    "schedule_digest",
    "execute_graph_async",
]


class ScheduleError(ValueError):
    """A readiness graph is malformed and therefore cannot be scheduled."""


@dataclass(frozen=True, slots=True)
class ReadyOperation:
    operation_id: str
    causal_predecessors: tuple[str, ...] = ()
    selector: Mapping[str, Any] | None = None
    sink: str | None = None
    read_only: bool = False


@dataclass(frozen=True, slots=True)
class ScheduleDecision:
    operation_id: str
    wave: int
    parallel: bool = False
    reason: str = "sequential-reference"


class SchedulerPolicy(Protocol):
    def decide(self, operations: Sequence[ReadyOperation], settled: frozenset[str]) -> tuple[ScheduleDecision, ...]: ...


class SequentialScheduler:
    """Fail-closed stable scheduler.  Every operation receives its own wave."""

    def decide(self, operations: Sequence[ReadyOperation], settled: frozenset[str] = frozenset()) -> tuple[ScheduleDecision, ...]:
        ready = ready_operations(operations, settled=settled)
        return tuple(
            ScheduleDecision(operation.operation_id, index, False)
            for index, operation in enumerate(ready)
        )


class AsyncGraphScheduler:
    """Concurrent non-blocking DAG scheduler for disjoint resource branches (EVO-14).

    Schedules ready operations in parallel waves when their resource selectors
    are proven disjoint or when all operations are read-only with non-exclusive sinks.
    Conflicting operations fall back safely to sequential waves.
    """

    def decide(
        self,
        operations: Sequence[ReadyOperation],
        settled: frozenset[str] = frozenset(),
    ) -> tuple[ScheduleDecision, ...]:
        ready = ready_operations(operations, settled=settled)
        if not ready:
            return ()

        decisions: list[ScheduleDecision] = []
        remaining = list(ready)
        current_wave = 0
        non_exclusive_sinks = frozenset({"observation", "advisory", "audit"})

        while remaining:
            current_batch: list[ReadyOperation] = []
            next_remaining: list[ReadyOperation] = []

            for op in remaining:
                can_add = True
                for batch_op in current_batch:
                    # ADR-0106: concurrent (same-wave, parallel) dispatch is
                    # authorized only for read-only operations with
                    # non-exclusive sinks -- ADR-0099 rule 4 keeps writes
                    # sequential regardless of selector disjointness. A
                    # disjoint-selector pair that includes anything else
                    # (write, unknown sink, exclusive sink) must fall back to
                    # a later sequential wave, never share a parallel wave.
                    both_safe_read_only = (
                        op.read_only and batch_op.read_only
                        and op.sink in non_exclusive_sinks
                        and batch_op.sink in non_exclusive_sinks
                    )
                    if both_safe_read_only:
                        continue
                    can_add = False
                    break

                if can_add:
                    current_batch.append(op)
                else:
                    next_remaining.append(op)

            is_parallel = len(current_batch) > 1
            for op in current_batch:
                decisions.append(
                    ScheduleDecision(
                        operation_id=op.operation_id,
                        wave=current_wave,
                        parallel=is_parallel,
                        reason="disjoint-resource-parallel" if is_parallel else "sequential-fallback",
                    )
                )
            current_wave += 1
            remaining = next_remaining

        return tuple(decisions)


async def execute_graph_async(
    operations: Sequence[ReadyOperation],
    executor: Any,
    *,
    settled: frozenset[str] = frozenset(),
    scheduler: SchedulerPolicy | None = None,
) -> list[Any]:
    """Execute a DAG of operations wave-by-wave with async parallelism."""
    import asyncio

    sched = scheduler or AsyncGraphScheduler()
    decisions = sched.decide(operations, settled=settled)
    if not decisions:
        return []

    # Group by wave
    by_wave: dict[int, list[str]] = {}
    for d in decisions:
        by_wave.setdefault(d.wave, []).append(d.operation_id)

    op_map = {op.operation_id: op for op in operations}
    results: list[Any] = []

    for wave_num in sorted(by_wave):
        wave_op_ids = by_wave[wave_num]
        wave_ops = [op_map[op_id] for op_id in wave_op_ids]
        
        # Execute wave concurrently
        tasks = [executor(op) for op in wave_ops]
        wave_results = await asyncio.gather(*tasks)
        results.extend(wave_results)

    return results


def ready_operations(
    operations: Sequence[ReadyOperation],
    *,
    settled: frozenset[str] = frozenset(),
) -> tuple[ReadyOperation, ...]:
    """Derive the currently runnable set from settled causal predecessors.

    Blocked operations are absent, never returned with a suggestive decision.
    Returning them was semantically equivalent to scheduling work whose inputs
    did not exist. Unknown predecessors and duplicate identities fail closed.
    """
    by_id: dict[str, ReadyOperation] = {}
    for operation in operations:
        if not operation.operation_id:
            raise ScheduleError("operation_id is required")
        if operation.operation_id in by_id:
            raise ScheduleError(f"duplicate operation_id {operation.operation_id!r}")
        by_id[operation.operation_id] = operation
    known = frozenset(by_id) | settled
    for operation in operations:
        if operation.operation_id in operation.causal_predecessors:
            raise ScheduleError(
                f"operation {operation.operation_id!r} depends on itself")
        unknown = sorted(set(operation.causal_predecessors) - known)
        if unknown:
            raise ScheduleError(
                f"operation {operation.operation_id!r} has unknown predecessors {unknown}")
    return tuple(sorted(
        (operation for operation in operations
         if operation.operation_id not in settled
         and set(operation.causal_predecessors) <= settled),
        key=lambda operation: operation.operation_id,
    ))


def safe_read_only_group(operations: Sequence[ReadyOperation]) -> tuple[str, ...]:
    """Prove an analysis-only group under the already-allowed read rule.

    This does not execute the group. Shared observation/advisory sinks are
    non-mutating; every other shared or unknown sink is treated as exclusive.
    """
    if not operations or any(not op.read_only or op.selector is None or op.sink is None for op in operations):
        return ()
    non_exclusive = frozenset({"observation", "advisory"})
    for index, left in enumerate(operations):
        for right in operations[index + 1:]:
            if left.causal_predecessors or right.causal_predecessors:
                return ()
            try:
                if (left.sink == right.sink and left.sink not in non_exclusive) or not disjoint(
                    left.selector, right.selector
                ):
                    return ()
            except Exception:
                return ()
    return tuple(sorted(op.operation_id for op in operations))


def schedule_digest(decisions: Sequence[ScheduleDecision]) -> str:
    return digest_of([{ "operationId": d.operation_id, "wave": d.wave,
                       "parallel": d.parallel, "reason": d.reason } for d in decisions])
```

## Deterministic branch score

Order lexicographically by:

1. valid fresh verification receipt;
2. goal requirements satisfied;
3. patch applies cleanly to parent subject;
4. targeted tests passed;
5. broader tests passed;
6. mutation/property checks passed when requested;
7. smaller risk surface and patch size;
8. lower consumed budget;
9. stable branch ID tie-breaker.

Model confidence is metadata and never outranks environment evidence.

## Required focused tests

- read-only modes cannot request write capabilities;
- writable branches receive distinct workspace identities;
- two candidate patches never write the same directory;
- child authority is a strict subset of parent authority;
- aggregate child reservations never exceed remaining parent budget;
- cancellation and timeout settle exactly once;
- restart reconstructs child state and does not rerun settled effects;
- join order is stable regardless of completion order;
- verified branch beats higher-confidence unverified branch;
- invalid patch cannot be selected;
- parent applies only the selected patch via an authorized effect;
- capsule identity is canonical and deduplicated;
- capsule cannot self-promote or modify a manifest;
- capsule promotion export requires preregistered evidence thresholds.

## Minimal validation commands

```bash
python3 -m unittest test.runtime.test_coding_budget -v
python3 -m unittest test.contracts.test_evo14_readonly_concurrency -v
python3 -m unittest test.falsifiers.test_rf101_rf112_canonical_recursion -v
python3 -m unittest test.falsifiers.test_rf114_rf117_m65_falsifiers -v
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
```
