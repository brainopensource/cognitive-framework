---
id: arch.orchestration.delegation
canonical_id: arch.orchestration.delegation
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: PARTIAL
owner: orchestration-delegation
canonical_for:
  - spawn lifecycle
  - child identity/scope/budget
  - topology/1 lowering
  - workflow/2 partial status
purpose: Detail the mediated spawn lifecycle, child scope attenuation, topology lowering, and isolated workflow mechanisms.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-019
  - E-B-024
  - E-B-032
  - E-B-033
  - E-B-034
  - E-B-035
  - E-B-036
  - E-B-055
relationships:
  - arch.system.overview
  - arch.trust.kernel
  - arch.agency.turns
  - ref.manifests
reviewer: documentation-specialist
confidence: high
---

# Delegation & Topology Architecture

## Purpose
This document is the canonical architecture owner for recursive child agent spawning (`agent.spawn`), child scope attenuation and budget conservation, `mhf.topology/1` lowering to sequential turns, and the status of isolated workflow mechanisms (`UNR-B-002`).

## Scope
- Mediated child agent spawning lifecycle (`SpawnAdapter`, `ChildSpawned`, `ChildReturned`).
- Recursive child identity, lineage tracking, and monotonic capability attenuation.
- `mhf.topology/1` declaration lowering to sequential `EpisodeEngine` turn execution (`INV-B-008`).
- Isolated workflow schedulers (`WorkflowScheduler`, `StagedWorkflowEngine`) and integration status.

## Non-responsibilities
- Concurrency models or multi-threaded parallel execution (canonical runtime turns are strictly sequential).
- Manifest schema field declarations (owned by [`ref.manifests`](../reference/manifests.md)).
- Kernel capability grant internals (owned by [`arch.trust.kernel`](kernel.md)).

## AS_BUILT Status
- `PARTIAL` — Sequential mediated child spawning and topology/1 lowering are fully operational (`IMPLEMENTED`), while `mhf.topology/2` workflow schedulers remain isolated mechanisms without canonical runtime callers (`UNR-B-002`).

---

## 1. The Delegation Boundary & Mediated Spawning

Agent delegation in Vanguard is strictly mediated: an agent cannot create arbitrary background processes or escape its parent sandbox.

```text
Parent EpisodeEngine
       │
       │ Proposes `spawn(role, task, budget_fraction)`
       ▼
Kernel.dispatch(EffectRequest("agent.spawn", ...))
       │
       │ Validates capability & leases sub-budget
       ▼
SpawnAdapter (Sole writer of ChildSpawned / ChildReturned)
       │
       ▼
Attenuated Child HarnessSession (Sequential execution)
       │
       ▼
Returns SpawnResult (Value-only outcome to Parent)
```

### Invariants of Delegation
- **Writer Role Isolation (`INV-B-007`)**: `SpawnAdapter` is the sole legal writer of `ChildSpawned` and `ChildReturned` events. Child episodes and plugins propose actions; they never append directly to the ledger.
- **Value-Only Outcome**: A child episode returns a structured result value to the parent; it cannot mutate parent in-memory state or inherit parent leases.

---

## 2. Child Scope, Identity & Budget Conservation

When a child episode is spawned:

1. **Lineage Binding**: The child receives a unique `episode_id` bound to `parent_episode_id`, `parent_principal_id`, and `run_id`.
2. **Monotonic Scope Attenuation (`INV-B-004`)**: The child scope is a strict subset of the parent scope. Tool permissions, network rules, and workspace access can be narrowed, never widened.
3. **Budget Partitioning (`INV-B-005`)**: The child budget is carved out of the parent lease. Unspent child budgets are refunded to the parent upon return. Overruns fail the child episode without bankrupting the parent.
4. **Recursion Depth Ceiling**: Depth counter increments per spawn level. Reaching `max_depth` (default: 3) fails closed with `RecursionDepthExceeded`.

---

## 3. `mhf.topology/1` Lowering to Sequential Turns (`INV-B-008`)

Declarative multi-agent topologies (e.g. Primary Agent $	o$ Reviewer Agent $	o$ Verifier Agent) declared under `mhf.topology/1` do not introduce concurrent background runtimes.

Instead, `vanguard.packages.runtime.topology` lowers topology declarations into ordinary sequential turns within the canonical `EpisodeEngine`:
- Step 1 executes the primary role to yield an artifact.
- Step 2 passes the artifact to the reviewer role in a subsequent sequential episode.
- Complete causal provenance is preserved in the unified run ledger.

---

## 4. Isolated Workflow Mechanisms (`UNR-B-002`)

The codebase includes advanced staged workflow implementations under `vanguard/packages/runtime/`:
- `WorkflowScheduler` (`workflow_scheduler.py`): Graph-based task scheduler supporting dependency-driven stage progression.
- `StagedWorkflowEngine` (`staged_workflow.py`): Stage execution engine with rollback hooks.

**Implementation Caveat (`UNR-B-002`)**: While these components are fully implemented and unit-tested in isolation, they are not integrated into the canonical `HarnessSession` entry point or the single ledger writer. Canonical runtime execution continues to use sequential topology lowering.

---

## Implementation Evidence

- **Delegation & Child Runtime**: `vanguard/packages/runtime/delegation.py`, `vanguard/packages/runtime/child_runtime.py`.
- **Topology Lowering**: `vanguard/packages/runtime/topology.py`.
- **Workflow Engines**: `vanguard/packages/runtime/workflow_scheduler.py`, `vanguard/packages/runtime/staged_workflow.py`.
- **Tests**: `test/agency/test_episode_spawn.py`, `test/falsifiers/test_rf101_rf112_canonical_recursion.py`, `test/runtime/test_topology_lowering.py`.
