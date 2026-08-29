---
id: "0106"
class: decision
authority: binding-decision
canonical_for:
  - deterministic-transform-algebra
  - protocol-recovery-state-machine
  - state-dependent-tool-policy
  - workflow-topology-v2-seam
status: accepted
owner: repository-governance
version: "1.0.0"
last_verified: 2026-08-29
supersedes: []
superseded_by: null
---

# ADR-0106: Deterministic Transform Algebra, Bounded Protocol Recovery, and Event-Sourced Workflow Topology

## Context & Problem Statement

Empirical benchmark forensics across LLM executions reveal four primary sources of system failure:
1. **Premature Malformed-Proposal Termination**: Non-fatal syntax deviations (DSML tags, markdown code blocks, truncated JSON) cause immediate instrument error termination in the turn engine without bounded recovery.
2. **Scattered Provider-Specific Heuristics**: Dialect normalization was coupled into provider adapters rather than passing through a shared protocol recovery pipeline.
3. **Unconstrained Tool Policy**: Relying solely on prompt instructions results in disallowed command execution and un-repaired errors.
4. **Agent Overuse**: Modeling every processing step as an autonomous agent introduces heavy overhead, nondeterminism, and context bloat where deterministic code transforms are superior.

## Decisions

### 1. Five SPIs Remain Frozen (No Sixth SPI)
The 5 standard Service Provider Interfaces in `vanguard/packages/ports/spi.py` (`IPlanner`, `IContextManager`, `IToolkit`, `IMemoryEngine`, `IEvaluationGate`) remain strictly frozen. Transforms are modeled as pure artifact-to-artifact functional operations defined in `vanguard/packages/domain/transforms/` and executed via `vanguard/packages/runtime/transform_runtime.py`.

### 2. Five-Plane Execution Model
1. **Immutable Artifacts**: Content-addressed (sha256) storage for all intermediate and semantic outputs.
2. **Event-Sourced State**: Pure deterministic reducer `reduce(state, event) -> state` with zero I/O.
3. **Workflow Graph**: Versioned DAG (`mhf.topology/2`) supporting typed node kinds: `transform`, `model`, `episode`, `effect`, `gate`, `router`, `join`, `interrupt`, `evaluator`.
4. **Ephemeral Workers**: Stateless executors receiving artifact digests and attenuated capabilities.
5. **Kernel Authority**: Trusted Computing Base (`vanguard/packages/kernel/`) remains domain-blind; workflow DAGs carry no inherent authority and all effects pass through Kernel capability dispatch.

### 3. Bounded Protocol Recovery & Invariant I3 ("No Silent Repair")
The episode turn engine delegates malformed proposals to `protocol_recovery.py`. Decoders classify deviations (truncation, markdown patch, schema mismatch). If a semantic candidate (such as a patch) is extracted from text, it produces a repair directive and structured feedback for the model; it is never executed automatically as an authorized effect.

### 4. State-Dependent Tool Policy
The runtime computes effective tool policies per workflow phase (`inspect`, `edit`, `verify`) and projects them to model request parameters (`tool_choice`, `tools`). Adapters declare capabilities and emit explicit capability downgrades if a provider cannot enforce strict tool choice.

### 5. Deterministic Attribution Projection (Invariant I10)
Run failure classification (`llm`, `provider`, `protocol`, `harness`, `framework`, `dataset`, `oracle`, `mixed`, `unknown`) is computed as a deterministic projection over the event log in `triage.py`. Unknown classification never defaults to model failure.

### 6. Preflight Baseline Gate (Invariant I15)
Workspaces with invalid baselines fail closed during preflight and consume zero live model budget.

## Consequences & Compliance

- `vanguard/packages/kernel/` budget remains <= 1438 LOC.
- `vanguard/packages/domain/` remains pure stdlib Python with zero external dependencies.
- `vanguard/packages/adapters/` do not import `kernel` or `agency`.
- Backward compatibility with `mhf.topology/1` is preserved.
