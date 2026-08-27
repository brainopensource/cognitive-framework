"""M-7 topology and recorded-workload fixtures (`B-M7`).

Two fixture families, kept together because the M-7 question spans both:

* **Topologies** -- the structures that must run through *one* runtime with no
  kernel or episode fork.  Three are valid (direct, planner/executor,
  critic/reviser); two are invalid in ways a topology validator must catch
  rather than lower (a delegation cycle, and a stage consuming an artifact
  nothing produces).
* **Workloads** -- recorded sequential effect traces for M7-01.  Each isolates
  one reason a pair did or did not have to serialise, so the analyzer's
  decomposition can be checked against a case whose right answer is known by
  construction rather than by re-running the analyzer.

Nothing here executes, schedules, or grants.  Topologies carry routing only:
a `capabilities` or `grants` key in a role is itself the falsifier.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "CONFLICTING_WRITE_WORKLOAD",
    "CAUSAL_DEPENDENCY_WORKLOAD",
    "CRITIC_REVISER",
    "CYCLIC",
    "DIRECT",
    "MISSING_RESOURCE",
    "PLANNER_EXECUTOR",
    "SAFE_READ_WORKLOAD",
    "VALID_TOPOLOGIES",
]


def _role(role_id: str, **extra: Any) -> dict[str, Any]:
    return {"id": role_id, "policyRef": f"policy/{role_id}@1",
            "scope": {"workspace": "/workspace"},
            "budget": {"turns": 4, "depth": 1}, "context": {"window": "recent"},
            **extra}


#: The degenerate case: one lineage, no delegation. If this does not run
#: through the same path as the others, "topology as data" is not true.
DIRECT: dict[str, Any] = {
    "topologyId": "direct", "version": "1.0.0", "entryRole": "agent",
    "roles": [_role("agent")], "edges": [], "artifactFlows": [],
}

PLANNER_EXECUTOR: dict[str, Any] = {
    "topologyId": "planner-executor", "version": "1.0.0", "entryRole": "planner",
    "roles": [_role("planner"), _role("executor")],
    "edges": [{"from": "planner", "to": "executor"}],
    "artifactFlows": [{"artifact": "plan", "from": "planner", "to": "executor"}],
}

CRITIC_REVISER: dict[str, Any] = {
    "topologyId": "critic-reviser", "version": "1.0.0", "entryRole": "author",
    "roles": [_role("author"), _role("critic"), _role("reviser")],
    "edges": [{"from": "author", "to": "critic"},
              {"from": "critic", "to": "reviser"}],
    "artifactFlows": [{"artifact": "draft", "from": "author", "to": "critic"},
                      {"artifact": "critique", "from": "critic", "to": "reviser"}],
}

#: Three topologies, one runtime: the M-7 exit gate's subject.
VALID_TOPOLOGIES = (DIRECT, PLANNER_EXECUTOR, CRITIC_REVISER)

#: Invalid: `reviser` delegates back to `author`. A cycle is not a loop the
#: scheduler can unroll -- it is a structure with no terminal condition.
CYCLIC: dict[str, Any] = {
    "topologyId": "cyclic", "version": "1.0.0", "entryRole": "author",
    "roles": [_role("author"), _role("critic"), _role("reviser")],
    "edges": [{"from": "author", "to": "critic"},
              {"from": "critic", "to": "reviser"},
              {"from": "reviser", "to": "author"}],
    "artifactFlows": [],
}

#: Invalid: `executor` consumes `researchNotes`, which no role produces. This
#: lowers cleanly and then deadlocks or silently runs on nothing -- the worst
#: pair of outcomes, which is why it belongs in a validator rather than in a
#: runtime timeout.
MISSING_RESOURCE: dict[str, Any] = {
    "topologyId": "missing-resource", "version": "1.0.0", "entryRole": "planner",
    "roles": [_role("planner"), _role("executor")],
    "edges": [{"from": "planner", "to": "executor"}],
    "artifactFlows": [{"artifact": "plan", "from": "planner", "to": "executor"},
                      {"artifact": "researchNotes", "from": "researcher",
                       "to": "executor"}],
}


def _effect(key: str, kind: str, **payload: Any) -> dict[str, Any]:
    return {"payload": {"kind": kind, "idempotencyKey": key, **payload}}


def _fs(*paths: str) -> dict[str, Any]:
    return {"kind": "fs", "root": "/workspace", "paths": list(paths)}


#: Two reads of disjoint files on the `observation` sink: the canonical safe
#: parallel pair, and the only kind M-7 permits without ADR-0099.
SAFE_READ_WORKLOAD = [
    _effect("read-a", "EffectStarted", sink="observation", resource=_fs("/workspace/a.py"),
            atMillis=0),
    _effect("read-a", "EffectCompleted", atMillis=8, cacheHit=False, walWriteMillis=1),
    _effect("read-b", "EffectStarted", sink="observation", resource=_fs("/workspace/b.py"),
            atMillis=9),
    _effect("read-b", "EffectCompleted", atMillis=17, cacheHit=True, walWriteMillis=1),
]

#: Two writes to the *same* file. Disjointness fails, so no scheduler could
#: have run these together whatever the topology said.
CONFLICTING_WRITE_WORKLOAD = [
    _effect("write-1", "EffectStarted", sink="privileged", resource=_fs("/workspace/a.py"),
            atMillis=0),
    _effect("write-1", "EffectCompleted", atMillis=20, cacheHit=False, walWriteMillis=6),
    _effect("write-2", "EffectStarted", sink="privileged", resource=_fs("/workspace/a.py"),
            atMillis=21),
    _effect("write-2", "EffectCompleted", atMillis=41, cacheHit=False, walWriteMillis=6),
]

#: Disjoint resources, but the second names the first as a predecessor. The
#: pair is unrecoverable for a scheduler, and attributing it to the resource
#: would overstate the win available.
CAUSAL_DEPENDENCY_WORKLOAD = [
    _effect("plan", "EffectStarted", sink="observation", resource=_fs("/workspace/plan.md"),
            atMillis=0),
    _effect("plan", "EffectCompleted", atMillis=10, cacheHit=False, walWriteMillis=2),
    _effect("apply", "EffectStarted", sink="privileged", resource=_fs("/workspace/src.py"),
            causalPredecessors=["plan"], atMillis=11),
    _effect("apply", "EffectCompleted", atMillis=31, cacheHit=False, walWriteMillis=5),
]
