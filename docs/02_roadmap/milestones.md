---
id: macro-milestones-ladder
class: execution
authority: execution
canonical_for:
  - macro-milestones-ladder
  - wave-gates
status: living
owner: engineering-director
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Macro Milestones — AETHER / Vanguard (M-0 → M-10)

**Status:** Authoritative macro execution ladder. Macro milestones define high-level outcomes and objective exit gates only. Living task-level execution is centralized in [`docs/03_sprints/sprint_active.md`](../03_sprints/sprint_active.md).

**Principle:** A milestone is complete only when its objective falsifiers and gates pass on the canonical path—never when code merely merges.

---

## Foundation Phases (Waves 0 → 4)

| Milestone | Version | Wave | Outcome | Exit Gate (Objective Evidence) | Status | Depends on |
|---|---|---:|---|---|---|---|
| **M-0 Engineering truth** | v0.6.0 | 0 | Living CI measures `vanguard/packages/` and named falsifiers | Production suites wired in CI; F-01…F-21 registered as tests; codegen `--check` wired | **COMPLETE** | Director approval (ADR-0075) |
| **M-1 Trust spine** | v0.6.0 | 1 | Unforgeable evidence, provable state, complete identity, typed budgets, real trajectories | F-01…F-15 green on canonical path; suites of record green; TCB budget ≤ 1438 LOC | **COMPLETE (GREEN)** | M-0 |
| **M-2 One runtime** | v0.6.1 | 2 | One canonical runtime plus economically truthful trajectories and restart-safe state | RF-23 populated/conserved `mhf.trajectory/1` green; RF-25 fresh-interpreter SQLite-WAL continuation green; retained convergence gates green | **IN FLIGHT (Wave 2C re-gate)** | M-1 |
| **M-3 Extensibility** | v0.6.2 | 3 | Typed Named Component Graph and complete plugin lifecycle on the canonical path | RF-28…RF-45; echo lifecycle over wire; NOVA-4 negatives; `layer0/` source/package/CI surface atomically absent | QUEUED | M-2 |
| **M-4 Foundation E2E (STOP)** | v0.6.3 | 4 | One honest coding-agent run through the complete substrate | Nine populated evidence rows, one uninterrupted `run_id`, zero human intervention or stitched/cassette substitution | QUEUED | M-1, M-2, M-3 |

---

## Post-Foundation Macro Roadmap (Waves 5 → 10)

*These milestones define outcomes and gates only. Sprint-level detail is deferred until the preceding milestone is completed.*

| Milestone | Version | Wave | Focus & Outcome | Exit Gate (Objective Evidence) | Depends on |
|---|---|---:|---|---|---|
| **M-5 Generality Proof & Consolidation** | v0.7.0 | 5 | Pack #2 **Math & Formal Deductive Verification**, Clean-Triad collapse, and exact T0 witness memo | Zero diffs under `packages/{domain,kernel}/`; trajectory/evidence parity with Pack #1; memo key binds subject, inputs, environment, checker, toolchain, assurance, and policy version | M-4 |
| **M-6 Mediated Delegation (`agent.spawn`)** | v0.8.0 | 6 | `agent.spawn` becomes one capability-mediated S0–S12 effect; recursion stays policy | RF-55…RF-59 and RF-26; no grant means deny; child authority/budget/depth monotonically attenuate; kernel remains ≤1438 LOC | M-5 |
| **M-7 Controlled Concurrency & Pareto Routing** | v0.9.0 | 7 | Independence groups, bounded worker pool, WAL-backed claims/leases, and alpha↔delta controller activation | M-7 measurement ADR plus named falsifiers; no duplicate/unknown effect; measured calls, envelopes, bytes, WAL contention, retries, critical path, and cost per signed pass; I-11 lifted only by ADR | M-5, M-6 |
| **M-8 Framework Builder Abstraction** | v0.9.0 | 8 | Debate, critic/reviser, bounded trees, and evolutionary search expressed as manifests plus SDK/CLI clients | RF-65 runs reference topologies with zero kernel/episode-engine diff; RF-66 universal-loop challenge adjudicated | M-6, M-7 |
| **M-9 Retrieval, Skills & Macro Laboratory** | v1.0.0 candidate | 9 | Replaceable hybrid retrieval, evidence-ranked skills, scaled orchestration measurement, and least-privilege macro candidates | RF-77 index rebuild; source-digest citations; held-out retrieval lift; macro selector hull and adversarial replay; five-SPI review; published scale measurements | M-7, M-8 |
| **M-10 Governed Meta-Cognition (1.0)** | v1.0.0 | 10 | VFE belief fitting, EFE policy selection, attributable DPO/trajectory credit, and reversible promotion | RF-67…RF-70; prediction recorded before observation; Pareto-safe exact paired McNemar with A/A floor, effect interval, exterior verdict, human pointer, and tested rollback | M-8, M-9 |

---

## Standing Architectural Constraints

- **Single Execution Board:** Live sprint tasks live exclusively in [`docs/03_sprints/sprint_active.md`](../03_sprints/sprint_active.md).
- **Sequential Execution (I-11):** Sequential execution remains mandatory until the M-7 measurement gate fires.
- **TCB Budget:** Microkernel in `vanguard/packages/kernel/` must not exceed $\le 1438$ LOC.
- **Refusals:** Strictly adhere to the non-claims and refusals in [`SPEC.md` §9](../SPEC.md#9-what-this-specification-refuses-to-build).
