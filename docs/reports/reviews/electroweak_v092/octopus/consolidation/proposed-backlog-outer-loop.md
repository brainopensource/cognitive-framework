---
id: execution.proposed-backlog.outer-loop
canonical_id: execution.proposed-backlog.outer-loop
class: execution
authority: descriptive
status: proposed
implementation_status: NOT_STARTED
owner: consolidation-agent
canonical_for:
  - outer-loop orchestrator delivery sequence
purpose: >
  PROPOSED package sequence and milestone gates for arch.outer-loop.orchestrator.
  This file does NOT modify docs/execution/active.md, backlog.md, or milestones.md —
  those remain the sole authorized boards (per VISION.md's precedence ladder, layer 5).
  A human/operator promotes items from here into the real backlog.
audience: [maintainer, release-owner]
last_verified: "2026-09-02"
relationships:
  - arch.outer-loop.orchestrator
  - execution.active
  - execution.backlog
  - execution.milestones
---

# Proposed Backlog — Outer-Loop Orchestrator

## Milestone ladder (proposed, gated, additive to existing M-0..M-10)

| Milestone | TARGET outcome | Acceptance boundary |
|---|---|---|
| **M-O1** | Event contract + `EventBus` projection exists | `orch.*` events replay deterministically from ledger, same evidence discipline as M-5a `AgentView` |
| **M-O2** | `SequentialDirector` (Strategy A) runs a real 3+ package chain end-to-end | Package graph from `backlog.md`-shaped input dispatches N `HarnessSession`s in dependency order with zero manual `active.md` edits during the run |
| **M-O3** | `Compactor` reusing LDA as retrieval backend | A package's `TaskContext` is built from compacted dependency memory, measured token reduction vs. raw-transcript baseline on `benchmark_20_suite` |
| **M-O4** | `DirectorObserver` (Strategy B) + `ApprovalGate` hybrid mode | Drift/inconclusive/budget triggers correctly escalate on injected-fault benchmark cases; non-triggering runs complete with zero human turns |
| **M-O5** | `EvolutionaryOuterLoop` (Strategy C) on scoreable packages + ablation report | Head-to-head table (§9 of architecture doc) produced from `benchmark_20_suite`, reusing `cmx06_protocol.json` report shape |

Each milestone gate is a package's own admission evidence, same discipline as the existing
board: "mechanism presence is not closure; state transitions require empirical receipts"
(quoting `docs/execution/backlog.md` §1's own invariant — this proposal inherits it, does not
relax it).

## Package sequence (proposed; WIP=1 per lane, same convention as current board)

### Lane A (build)

| ID | Package | Depends on | Notes |
|---|---|---|---|
| `ORCH-01` | `OrchestrationEvent` schema + `EventBus` port + SQLite-WAL projection | none | Pure addition to existing ledger; no kernel change |
| `ORCH-02` | `Planner` port + `ExecutionPlan` builder from `backlog.md`-shaped YAML/JSON | `ORCH-01` | Reads dependency graph, does not write it |
| `ORCH-03` | `Dispatcher` port wrapping existing `HarnessSession`/`EpisodeEngine` spawn | `ORCH-01` | Thin — this is intentionally the smallest package, it only owns spawn/collect |
| `ORCH-04` | `SequentialDirector` (Strategy A) | `ORCH-02`, `ORCH-03` | Delivers M-O2 |
| `ORCH-05` | `Compactor` v1 (episode-summary compaction, no retrieval yet) | `ORCH-01` | Standalone; can build in parallel with `ORCH-02..04` |
| `ORCH-06` | `Compactor` v2 — LDA-backed retrieval integration | `ORCH-05`, existing `tools/007_LLM_DOCS_ATLAS` | Delivers M-O3; **extends** LDA, does not fork it |
| `ORCH-07` | `Verifier` port (exterior, package-granularity) | `ORCH-01` | Independent of `AdmissionGate`; reuses evaluator pattern from `benchmarks/frontier_v090/evaluators.py` |
| `ORCH-08` | `ApprovalGate` + `ApprovalPolicy` (interactive/autonomous/hybrid) | `ORCH-01` | No LLM dependency — pure policy/state machine |
| `ORCH-09` | `DirectorObserver` (Strategy B) | `ORCH-04`, `ORCH-07`, `ORCH-08` | Delivers M-O4; itself an ephemeral agent over the substrate |
| `ORCH-10` | `EvolutionaryOuterLoop` (Strategy C) + evaluator wiring | `ORCH-03`, `ORCH-07` | Opt-in per package manifest field |
| `ORCH-11` | `find_dead_ends` / `find_bottlenecks` / drift-scoring utilities | `ORCH-01` | Pure functions over event stream, no new subsystem |

### Lane B (measurement, independently gated)

| ID | Package | Depends on | Notes |
|---|---|---|---|
| `ORCH-M1` | Extend `benchmarks/benchmark_20_suite/runner.py` with `orchestration_policy` param | `ORCH-04` | Reuse existing harness, do not fork it |
| `ORCH-M2` | Ablation report generator, `cmx06_protocol.json`-shaped output comparing A/B/C | `ORCH-M1`, `ORCH-09`, `ORCH-10` | Delivers M-O5 |
| `ORCH-M3` | Fault-injection fixtures for drift/inconclusive/budget-exceeded escalation paths | `ORCH-08` | Required evidence for M-O4's acceptance boundary |

## Explicit non-goals for this backlog slice

- No frontend work (per mandate: "Foque no backend apenas").
- No change to `vanguard/packages/kernel/*`.
- No new persistence engine — `EventBus` is a projection over the existing SQLite-WAL ledger.
- No forked memory/retrieval system — `ORCH-06` extends LDA.
- `ORCH-10` (evolutionary strategy) is not on the critical path to M-O2/M-O3/M-O4 and can slip
  without blocking the rest of the ladder.

## Promotion procedure

1. Owner reviews `arch.outer-loop.orchestrator` and this file.
2. If accepted, file an ADR superseding nothing (additive layer, per the architecture doc §3)
   and copy the accepted subset of the table above into the real `docs/execution/backlog.md`
   and `docs/execution/milestones.md`, in that repo's own frontmatter/lifecycle format.
3. `docs/execution/active.md` picks up `ORCH-01` as the first authorized package once a lane
   has WIP capacity.
