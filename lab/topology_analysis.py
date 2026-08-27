"""M-7 topology falsification, analysis-only (`B-M7`).

`runtime/topology.py` (Dev A) parses and lowers a topology.  This module asks
the questions a *falsifier* asks, which are different from the ones a parser
asks:

* **Is the structure runnable at all?**  A stage that consumes an artifact no
  role produces parses cleanly and then deadlocks -- or worse, runs on nothing
  and reports success.  `parse_topology` does not currently catch that, so it
  is caught here and reported as a finding rather than patched into a module
  this lane does not own.
* **Do several topologies really share one runtime?**  The M-7 exit gate is
  "≥3 topologies through one runtime with zero kernel/episode diff".  A
  comparison that only shows three topologies *parse* proves nothing; what
  must hold is that they lower to the same shape through the same code, and
  differ only in the data.
* **Does the topology stay data?**  A topology that names a verb, sink,
  capability or grant has stopped being routing and started being authority.

Nothing here schedules, executes, or activates concurrency.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.runtime.topology import (
    Topology,
    TopologyError,
    lower_topology,
    parse_topology,
)

__all__ = [
    "TopologyFinding",
    "analyze_topology",
    "missing_resources",
    "three_topology_report",
    "unreachable_roles",
]

#: Tokens that turn routing data into an authority statement.
_AUTHORITY_TOKENS = ("capabilities", "grants", "authority", "verb", "sinkClass",
                     "principal", "approval")


@dataclass(frozen=True, slots=True)
class TopologyFinding:
    code: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


def missing_resources(topology: Topology) -> tuple[str, ...]:
    """Artifacts a stage consumes that no role in this topology produces.

    Producers are roles named as an artifact flow's source; a flow whose
    source is not a declared role produces nothing, so its artifact is
    unsatisfiable no matter how the scheduler orders the stages.
    """
    roles = {role.role_id for role in topology.roles}
    produced: set[str] = set()
    consumed: dict[str, str] = {}
    for flow in topology.artifact_flows:
        artifact = flow.get("artifact")
        if not isinstance(artifact, str) or not artifact:
            continue
        source, target = flow.get("from"), flow.get("to")
        if isinstance(source, str) and source in roles:
            produced.add(artifact)
        if isinstance(target, str):
            consumed[artifact] = target
    return tuple(sorted(f"{artifact}->{consumed[artifact]}"
                        for artifact in consumed if artifact not in produced))


def unreachable_roles(topology: Topology) -> tuple[str, ...]:
    """Roles no delegation path reaches from the entry role.

    A declared role nothing can reach is dead structure. It is a warning
    rather than an error -- a topology may legitimately declare a role a
    later version will wire -- but it must be visible, because an unreachable
    role is also how a stage silently stops running.
    """
    graph: dict[str, list[str]] = {role.role_id: [] for role in topology.roles}
    for source, target in topology.edges:
        graph[source].append(target)
    seen: set[str] = set()
    stack = [topology.entry_role]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(graph.get(node, ()))
    return tuple(sorted(set(graph) - seen))


def analyze_topology(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Parse, validate and lower one topology into a deterministic report."""
    findings: list[TopologyFinding] = []
    try:
        topology = parse_topology(raw)
    except TopologyError as exc:
        return {
            "topologyId": raw.get("topologyId"),
            "parsed": False,
            "runnable": False,
            "findings": [TopologyFinding("parse_rejected", str(exc)).to_dict()],
            "report_digest": digest_of({"topologyId": raw.get("topologyId"),
                                        "parse_rejected": str(exc)}),
        }

    for artifact in missing_resources(topology):
        findings.append(TopologyFinding(
            "missing_resource",
            f"{artifact} consumes an artifact no declared role produces"))
    for role in unreachable_roles(topology):
        findings.append(TopologyFinding(
            "unreachable_role", f"{role} is not reachable from the entry role"))

    serialised = json.dumps(topology.to_dict(), sort_keys=True)
    for token in _AUTHORITY_TOKENS:
        if token in serialised:
            findings.append(TopologyFinding(
                "authority_in_topology",
                f"topology names {token!r}; routing data must not carry authority"))

    lowered = lower_topology(topology)
    report = {
        "topologyId": topology.topology_id,
        "version": topology.version,
        "parsed": True,
        "runnable": not any(f.code in {"missing_resource", "authority_in_topology"}
                            for f in findings),
        "roleCount": len(topology.roles),
        "edgeCount": len(topology.edges),
        "topologyDigest": topology.digest(),
        "lowering": {"keys": sorted(lowered),
                     "activation": lowered["activation"],
                     "entryRole": lowered["entryRole"],
                     "lineageTemplateCount": len(lowered["lineageTemplates"])},
        "findings": [f.to_dict() for f in findings],
    }
    report["report_digest"] = digest_of(report)
    return report


def three_topology_report(topologies: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Evidence for "≥3 topologies through one runtime, zero kernel diff".

    The claim is about *sharing*, so the report checks the two halves that can
    actually be falsified without a live run: every topology lowers through
    the same code to the same shape (`sharedLoweringShape`), and each remains
    a distinct artifact rather than three names for one structure
    (`distinctDigests`). Whether they then execute identically is an
    integrated test, not something this analysis may assert.
    """
    reports = [analyze_topology(raw) for raw in topologies]
    shapes = {tuple(r["lowering"]["keys"]) for r in reports if r["parsed"]}
    activations = {r["lowering"]["activation"] for r in reports if r["parsed"]}
    digests = {r["topologyDigest"] for r in reports if r["parsed"]}
    body = {
        "protocol": "M-7-three-topology",
        "analysisOnly": True,
        "count": len(reports),
        "runnable": sum(1 for r in reports if r.get("runnable")),
        "sharedLoweringShape": len(shapes) == 1,
        "sharedActivation": sorted(activations),
        "distinctDigests": len(digests) == len(reports),
        "sequentialOnly": activations == {"ordinary-agent-spawn-sequential"},
        "topologies": reports,
    }
    body["report_digest"] = digest_of(body)
    return body


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: python3 lab/topology_analysis.py TOPOLOGIES.json", file=sys.stderr)
        return 2
    raw = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    topologies: Iterable[Mapping[str, Any]] = (
        raw.get("topologies", ()) if isinstance(raw, Mapping) else raw)
    report = three_topology_report(list(topologies))
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["runnable"] == report["count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
