"""Versioned topology values and lowering (M-7 preparation only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of

__all__ = ["TopologyError", "Topology", "TopologyRole", "parse_topology", "lower_topology"]


class TopologyError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class TopologyRole:
    role_id: str
    policy_ref: str
    scope_template: Mapping[str, Any]
    budget_template: Mapping[str, Any]
    context: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class Topology:
    topology_id: str
    version: str
    roles: tuple[TopologyRole, ...]
    edges: tuple[tuple[str, str], ...]
    artifact_flows: tuple[Mapping[str, Any], ...]
    entry_role: str

    def to_dict(self) -> dict[str, Any]:
        return {"topologyId": self.topology_id, "version": self.version,
                "roles": [{"id": r.role_id, "policyRef": r.policy_ref,
                            "scope": dict(r.scope_template), "budget": dict(r.budget_template),
                            "context": dict(r.context)} for r in self.roles],
                "edges": [{"from": a, "to": b} for a, b in self.edges],
                "artifactFlows": [dict(x) for x in self.artifact_flows], "entryRole": self.entry_role}

    def digest(self) -> str:
        return digest_of(self.to_dict())


def parse_topology(raw: Mapping[str, Any]) -> Topology:
    if not isinstance(raw, Mapping):
        raise TopologyError("topology must be an object")
    tid, version, entry = raw.get("topologyId"), raw.get("version"), raw.get("entryRole")
    if not all(isinstance(x, str) and x for x in (tid, version, entry)):
        raise TopologyError("topologyId, version and entryRole are required")
    raw_roles = raw.get("roles")
    if not isinstance(raw_roles, Sequence) or isinstance(raw_roles, (str, bytes)):
        raise TopologyError("roles must be a list")
    roles: list[TopologyRole] = []
    ids: set[str] = set()
    for item in raw_roles:
        if not isinstance(item, Mapping) or not isinstance(item.get("id"), str) or not item["id"]:
            raise TopologyError("role id is required")
        rid = item["id"]
        if rid in ids:
            raise TopologyError("duplicate role id")
        ids.add(rid)
        # Topology describes routing only; authority belongs to grants/policy.
        if any(key in item for key in ("capabilities", "grants", "authority")):
            raise TopologyError("topology cannot encode authority")
        roles.append(TopologyRole(rid, str(item.get("policyRef", "")),
                                  dict(item.get("scope", {})), dict(item.get("budget", {})),
                                  dict(item.get("context", {}))))
    if entry not in ids:
        raise TopologyError("entry role does not exist")
    raw_edges = raw.get("edges", [])
    edges = tuple((str(e.get("from")), str(e.get("to"))) for e in raw_edges
                  if isinstance(e, Mapping) and isinstance(e.get("from"), str) and isinstance(e.get("to"), str))
    if len(edges) != len(raw_edges) or any(a not in ids or b not in ids or a == b for a, b in edges):
        raise TopologyError("invalid delegation edge")
    graph = {rid: [] for rid in ids}
    for a, b in edges: graph[a].append(b)
    visiting: set[str] = set(); visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting: raise TopologyError("delegation cycle")
        if node in visited: return
        visiting.add(node)
        for child in graph[node]: visit(child)
        visiting.remove(node); visited.add(node)
    for rid in ids: visit(rid)
    return Topology(str(tid), str(version), tuple(roles), edges,
                    tuple(x for x in raw.get("artifactFlows", []) if isinstance(x, Mapping)), str(entry))


def lower_topology(topology: Topology) -> dict[str, Any]:
    return {"topologyDigest": topology.digest(), "entryRole": topology.entry_role,
            "lineageTemplates": tuple({"role": r.role_id, "policyRef": r.policy_ref,
                                        "scope": dict(r.scope_template), "budget": dict(r.budget_template),
                                        "context": dict(r.context)} for r in topology.roles),
            "allowedDelegations": topology.edges, "artifactFlows": topology.artifact_flows,
            "activation": "ordinary-agent-spawn-sequential"}
