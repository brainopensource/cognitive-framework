---
id: adr-0099-m7-topology-scheduler-disposition
adr: 0099
class: decision
authority: binding-decision
canonical_for:
  - m7-topology-scheduler-disposition
  - sequential-reference-scheduler
status: accepted
owner: engineering-leadership
version: "1.0.0"
last_verified: 2026-08-27
accepted_date: 2026-08-27
extends:
  - ADR-0092
  - ADR-0097
supersedes: []
superseded_by: null
---

# ADR-0099 — M-7 Topology and Scheduler Disposition

## Context

M7-01 was authorized as an analysis-only measurement so that scheduler policy would follow
recorded causal effects rather than an assumption that more parallelism is better. The M-7
topology and runtime seam tests provide the falsifiers for topology lowering, dependency
readiness, selector conservatism, sink classification, timing completeness, and disabled-path
behavior.

## Evidence

The independent M7-01 test set passed 10/10:

- `test/runtime/test_m65_m7_m8_seams.py` passed the topology sequentiality and fail-closed seam
  checks.
- `test/falsifiers/test_m701_recorded_workload.py` passed the real canonical-path workload,
  including recorded selector decomposition, event-timestamp timing, digest stability, and
  conservative cache/WAL accounting.
- The canonical workload contained three settled effects and three pairs. One pair was useful
  independence (`1/3`); the other pairs were serialized by resource and sink constraints. No
  effect windows overlapped, and unknown selectors were not treated as evidence for concurrency.
- The topology suite confirmed that direct, planner/executor/reviewer, and fork/read/merge
  structures lower through the same runtime shape and activate only the sequential reference
  scheduler.

## Decision

The M-7 scheduler disposition is **`SEQUENTIAL_CONFIRMED`**.

1. The sequential reference scheduler remains the only active scheduler policy.
2. Topology is a data-level runtime extension and does not grant authority, alter Kernel
   semantics, or create a second execution runtime.
3. Read-only independence remains an analysis result and a future optimization seam; it does not
   authorize parallel execution in the current Beta MVP.
4. Writes, spawning, promotion, shared or unknown sinks, causal predecessors, overlapping
   selectors, incomplete timing, and unsettled effects remain sequential and fail closed.
5. Any future change from this disposition requires a new preregistered workload and evidence
   showing material wall-time benefit after coordination, contention, cache, recovery, and state
   equivalence costs.

## Consequences

M-7 retains topology lowering and telemetry without enabling concurrency. This disposition closes
the scheduler decision question but does not by itself accept the M-7 milestone or waive the
independent evidence, baseline, integration, or security gates defined by ADR-0101 and the
canonical execution board.
