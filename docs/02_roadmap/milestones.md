# Macro Milestones — AETHER / Vanguard (M-0 → M-10)

**Status:** Authoritative macro execution ladder. Macro milestones define high-level outcomes and objective exit gates only. Living task-level execution is centralized in [`docs/03_sprints/sprint_active.md`](../03_sprints/sprint_active.md).

**Principle:** A milestone is complete only when its objective falsifiers and gates pass on the canonical path—never when code merely merges.

---

## Foundation Phases (Waves 0 → 4)

| Milestone | Wave | Outcome | Exit Gate (Objective Evidence) | Status | Depends on |
|---|---|---|---|---|---|
| **M-0 Engineering truth** | 0 | Living CI measures `vanguard/packages/` and named falsifiers | Production suites wired in CI; F-01…F-21 registered as tests; codegen `--check` wired | **COMPLETE** | Director approval (ADR-0075) |
| **M-1 Trust spine** | 1 | Unforgeable evidence, provable state, complete identity, typed budgets, real trajectories | F-01…F-15 green on canonical path; suites of record green; TCB budget ≤ 1438 LOC | **COMPLETE (GREEN)** | M-0 |
| **M-2 One runtime** | 2 | `layer0/` duplicated halves absorbed; single wire, single algebra, single writer; `root.py` split in place | F-16 green; zero `layer0` imports under `vanguard/`; duplicate kill surfaces deleted; reducer fold rules complete | **IN FLIGHT (Re-gate Round 4)** | M-1 |
| **M-3 Extensibility** | 3 | Plugin lifecycle real on canonical path; named component graph manifest; kernel domain-blind | ADR-M0-13 echo-plugin lifecycle on wire; F-18 domain-blindness green; freeze-at-compose negatives; `layer0/` fully deleted | QUEUED | M-2 |
| **M-4 Foundation E2E (STOP)** | 4 | One real coding-agent run through the complete substrate with trustworthy state & evidence | 9-row integration verification on `packs/code-default/` (model, effect, sandbox, signed eval, WAL, cold replay) with zero human intervention | QUEUED | M-1, M-2, M-3 |

---

## Post-Foundation Macro Roadmap (Waves 5 → 10)

*These milestones define outcomes and gates only. Sprint-level detail is deferred until the preceding milestone is completed.*

| Milestone | Wave | Focus & Outcome | Exit Gate (Objective Evidence) | Depends on |
|---|---|---|---|---|
| **M-5 Generality Proof & Consolidation** | 5 | Governance documentation consolidation; Pack #2 (non-coding domain: math/data) proving domain blindness | Zero diffs under `domain/` and `kernel/` for Pack #2 (Invariant I-7 verified); suspend/resume cold-reconstruction falsifier passed | M-4 |
| **M-6 Mediated Delegation (`agent.spawn`)** | 6 | `agent.spawn` capability-mediated verb in S0–S12 dispatch enabling native tree search, MCTS, and hierarchical decomposition | Planners without spawn grant cannot delegate; child remains monotonically attenuated; spawn recorded as mediated effect | M-5 |
| **M-7 Controlled Concurrency** | 7 | Independence groups activated for non-conflicting selectors; async scheduling & $K \ll N$ logical-to-worker separation | Measurement gate on selector disjointness & cold-resume scalability; zero event loss under backpressure | M-5, M-6 |
| **M-8 Framework Builder Abstraction** | 8 | Arbitrary agentic topologies (Debate, Critic/Revisor, Evolutionary Search) composed declaratively via named component graphs | Reference validation suites running multi-pack without engine modifications | M-6, M-7 |
| **M-9 Scaled High-Performance Orchestration** | 9 | Scaled multi-agent load with measured sub-millisecond IPC and bounded ledger pressure | Performance benchmarks satisfying strict latency and resource utilization limits | M-7, M-8 |
| **M-10 Meta-Cognitive Substrate (Final)** | 10 | Continuous autonomous self-improvement: active inference, unforgeable DPO trajectory harvesting, dynamic skill synthesis | End-to-end self-tuning loop: system proposes, verifies, and promotes an optimized harness under empirical hypothesis testing | M-8, M-9 |

---

## Standing Architectural Constraints

- **Single Execution Board:** Live sprint tasks live exclusively in [`docs/03_sprints/sprint_active.md`](../03_sprints/sprint_active.md).
- **Sequential Execution (I-11):** Sequential execution remains mandatory until the M-7 measurement gate fires.
- **TCB Budget:** Microkernel in `vanguard/packages/kernel/` must not exceed $\le 1438$ LOC.
- **Refusals:** Strictly adhere to the non-claims and refusals in [`SPEC.md` §9](../SPEC.md#9-what-this-specification-refuses-to-build).
