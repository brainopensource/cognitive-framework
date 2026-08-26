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
