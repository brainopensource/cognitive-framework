---
adr: 0071
title: "Authority vs state: decision plane proposes, ledger proves; hybrid event sourcing; identity trinity D_H/D_R/D_X; replay taxonomy"
status: accepted
source_section: "v0.6 Concept Lock"
---

# ADR-0071: Authority, ledger, identity trinity, and replay taxonomy

**Context.** Reviews use "orchestrator authoritative" in a way that collides with
`State = fold(Events)`. A single `harness_digest` is being asked to answer composition, execution,
and experiment questions at once. Replay tests in `test/layer0/replay/test_parity.py` fold the
same in-memory list twice and are treated as I-4 proof. SPEC §1.3 names a CI job `replay-parity`
that is absent from `.github/workflows/ci.yml`. Packages already persist events with SQLite WAL
(`vanguard/packages/adapters/stores/event_store.py`).

**Decision.**

### Authority split

- **Decision plane** (scheduler / future orchestrator / kernel): who runs, when, which lease,
  which budget, which capabilities.
- **State plane** (ledger + pure reducers): what happened.
- Sequence: `Decision → DurableEvent → fold → EffectiveState`.
- Orchestrator memory, plugin local state, and projections are never source of truth.
  `Projection = f(Ledger)`; `Cache = g(Ledger, CAS)`.

### Hybrid event sourcing

- `State = fold(Events)` remains Invariant I-4.
- Snapshots are an optimization, not an authority.
- CAS/blob store holds bytes; events hold content-addressed refs. Blob durability still precedes
  any event that names a digest (SPEC §1.2 D-19).
- Store: SQLite WAL with FULL sync remains (ADR-0010). Inbox/outbox (ADR-0062) remains.
- Consistency unit is `project_id`. A global total order across projects is not required.
- Concurrent executions are **not** required to produce byte-identical ledgers.

### Identity trinity

- `D_H` — harness composition (resolved manifest + plugins + assets + policies). FrozenHarness
  digest is `D_H` only.
- `D_R` — execution identity: `H(D_H ∥ runtime ∥ environment ∥ model identity ∥ oracle identity)`.
- `D_X` — experiment cell: `H(D_R ∥ dataset ∥ protocol)`.
- A/B measurement MUST NOT collapse these. Two runs of the same FrozenHarness with different
  model versions are different `D_R`.

### Replay taxonomy

These MUST NOT be treated as equivalent:

| Kind | Bar |
|---|---|
| State replay | Reconstruct grants, budgets, approvals, episode FSM from the ledger |
| Schedule replay | Requires recorded nondeterminism (clock, RNG, model cassettes) |
| Real-world re-execution | Not required to match |
| Byte-identical fixtures | Only fully controlled inputs |

A test that folds the same in-memory sequence twice is not I-4. The named `replay-parity` CI job
is a **requirement** for the next code phase, not a claim about the current workflow.

**Alternative considered (and rejected).**

- Orchestrator as source of truth. Rejected: crash/restart would invent history.
- Byte-identical concurrent ledger as a general requirement. Rejected: unsatisfiable once real
  clocks/models exist; belongs only to controlled fixtures.
- Collapsing identity into one digest. Rejected: poisons A/B.
- Rebuilding the ledger in `layer0/` or Rust before using packages WAL. Rejected: ADR-0069.

**Evidence / bound test / links.** Forensic §§11, 17, 19 P0-3/P0-6/P0-7; ADR-0010; ADR-0062;
`event_store.py:139`; `test/layer0/replay/test_parity.py:40-41`. Bound test: cold replay against
live terminal state for grants, budgets, approvals, episode lifecycle — code phase.
`REQ-TRUST-001`.

**Reversal condition.** A newer ADR that replaces the ledger as authority (for example a
snapshot-primary store with events as audit-only), with a demonstrated replay that cannot be
expressed as fold. Performance preference is not reversal.

**Owner · status.** Principal Staff Engineer / Tech Lead · accepted · 2026-08-20 · accepted
