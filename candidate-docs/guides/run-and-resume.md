---
id: guide.run-resume
canonical_id: guide.run-resume
class: how-to
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: guides-operator
canonical_for:
  - run/status/events/artifact/resume procedure
  - verification and failure handling
purpose: Step-by-step operational guide for executing tasks, querying status, inspecting events, creating checkpoints, and cold-resuming runs.
audience:
  - operator
  - developer
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-002
  - E-B-005
  - E-B-009
  - E-B-025
  - E-B-026
  - E-B-028
  - E-B-029
  - E-B-030
  - E-B-042
  - E-B-043
  - E-B-044
  - E-B-045
  - E-B-046
  - E-B-047
  - E-B-048
  - E-B-049
relationships:
  - arch.state.causal
  - arch.runtime.execution
  - ref.commands
reviewer: documentation-specialist
confidence: high
---

# Run, Inspect & Resume Guide

## Purpose
This guide is the canonical owner for operational procedures governing agent task execution, querying status and event logs, retrieving artifacts, capturing state checkpoints, and resuming runs after process interruptions or crashes.

## Scope
- Executing runs with explicit profiles and timeouts.
- Querying status, event histories, and verifying artifacts using `vanguard` and `vg`.
- Creating snapshot checkpoints.
- Performing cold resume (`RF-25`) from durable SQLite WAL state.
- Handling undeterminable crash reconciliation.

## Non-responsibilities
- Theoretical foundations of causal state folding (owned by [`arch.state.causal`](../architecture/causal-state.md)).
- Complete event envelope schema references (owned by [`ref.events`](../reference/events.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Cold resume, event streaming, and artifact retrieval are fully operational and tested across fresh OS processes.

---

## 1. Starting a Run

To start a task and capture its `run_id`:

```bash
# Python direct harness execution
vanguard run "Refactor database queries" --profile product --timeout 300 --json
```

Output:
```json
{
  "run_id": "018f3a9a-7c20-7000-8000-000000000001",
  "status": "RUNNING",
  "plan_digest": "a1b2c3d4..."
}
```

---

## 2. Inspecting Active or Completed Runs

### Querying Run Status
```bash
vanguard status --run-id 018f3a9a-7c20-7000-8000-000000000001
```

### Inspecting Causally Ordered Events
Query the event stream from sequence `0` or after a specific sequence counter:

```bash
vanguard events --run-id 018f3a9a-7c20-7000-8000-000000000001 --after-seq 10 --limit 50 --json
```

### Retrieving Content-Addressed Artifacts
Verify and fetch an artifact blob by its SHA-256 digest:

```bash
vanguard artifacts --run-id 018f3a9a-7c20-7000-8000-000000000001 --digest 3f7a1b92c4e5... --output ./output.md
```

---

## 3. Creating Checkpoints

To capture a verified state snapshot for fast resumption:

```bash
vg checkpoint --run-id 018f3a9a-7c20-7000-8000-000000000001
```

The runtime verifies the state digest against the event fold and writes a verified checkpoint record into `.vanguard/state.db` (`RF-96`).

---

## 4. Cold Resumption (`resume`)

If a run is interrupted by network failure, timeout, or unexpected process termination:

```bash
vanguard resume --run-id 018f3a9a-7c20-7000-8000-000000000001
```

### What Happens During Resume (`RF-25`)
1. Vanguard launches a fresh process and connects to `.vanguard/state.db`.
2. The runtime reads the event history and folds state projections (`LedgerState`, `AgentView`).
3. If an uncommitted effect was in flight during the crash (`EffectStarted` without receipt), the recovery manager reconciles it as undeterminable (`EffectReconciled`).
4. Execution re-enters the turn loop at turn $N+1$ with full context intact.

---

## 5. Recovering from Failures

| Failure State | Recovery Procedure |
|---|---|
| Run Paused at Approval | Inspect pending gate with `vg trace`, then issue `vg approve --run-id <ID> --request-id <REQ_ID>` |
| Budget Exhausted | Re-launch with `vanguard resume --run-id <ID>` after adjusting profile budget ceilings |
| Corrupted Checkpoint Cache | Checkpoints are discardable; deleting corrupted checkpoint forces automatic replay from genesis event `0` |

---

## Related Documentation
- [Causal State Architecture](../architecture/causal-state.md)
- [Runtime Execution Architecture](../architecture/runtime-execution.md)
- [Commands Reference](../reference/commands.md)
