---
id: macro-milestones-ladder
class: execution
authority: execution
canonical_for:
  - macro-milestones-ladder
  - wave-gates
status: living
owner: engineering-director
version: "0.7.3"
last_verified: 2026-08-26
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Macro Milestones — AETHER v0.7+

Sequencing and objective exit gates for the roadmap locked by [`VISION.md`](../../VISION.md) (Law
Zero) and accepted ADRs through [`ADR-0097`](../02_decisions/0097-phase0-ratification-and-two-lane-activation.md). Only
[`sprint_active.md`](sprint_active.md) authorizes current implementation. A milestone closes on
evidence from the canonical executable path, never because code, schemas, or isolated tests exist.

**Blocking is technical, never ceremonial.** A team is blocked only when its work depends on an
unfinished interface, schema, invariant, primitive, or runtime contract. Every blocked row below
names that dependency. There are no milestone-wide locks.

## Milestone Ladder

| Milestone | Outcome | Exit gate | Status | Blocked on |
|---|---|---|---|---|
| **M-0 Engineering Truth** | CI measures production truth and named falsifiers | F-01…F-21, codegen, architecture gates | **COMPLETE** | — |
| **M-1 Trust Spine** | Generic effect authority, budgets, provenance, event truth | S0–S12 falsifiers; single writer; TCB `<=1438` | **COMPLETE** | — |
| **M-2 Runtime Recovery** | Truthful trajectories and restart-safe state | RF-23 rich trajectory; RF-25 fresh-process WAL continuation | **COMPLETE** | — |
| **M-3 / M-3C Contracts & Convergence** | One `compose -> activate -> run` authority | RF-28–RF-45 retained; RF-78–RF-84 | **COMPLETE** | — |
| **W-3D Product Profiles** | Identity-bearing profiles and one adapter bootstrap | RF-87–RF-94 | **COMPLETE** | — |
| **M-4 Product Coding Proof + Trajectory Capture** | Useful, durable coding agent **and** the scientific observability that every later milestone is measured with | RF-95 plus `mhf.trajectory/2`, exact model-I/O and context/compaction/cache provenance, proof-honest RF-100, and fresh-process reconstruction | **PROVISIONALLY ACCEPTED FOR DEVELOPMENT — RF-95/review evidence open** | Passing RF-95 and independent review remain required for evidence release and baseline tagging |
| **M-5a Event-Derived Agent** | `Operation`, `Lineage`, `Scope`, `AgentView`; semantic state reconstructible from events; immutable `M-5A-BASE-v2` | RF-96/97/99/100; fresh process rebuilds goal identity, plan, attempts, settled effects, budget, strategy, and terminal status | **ACTIVE — implementation green; promotion pending** | M-4 closure, ADR-0098 acceptance, benchmark re-freeze, reviewed tag |
| **M-5b Generality Falsifier** | Formal Pack #2 through the unchanged post-M-5a substrate | RF-86 zero semantic diff vs `M-5A-BASE-v2`; deterministic independent witness | **ACTIVE — SAT/CNF OD-3 selected; pack/oracle slice green** | `M-5A-BASE-v2` for RF-86 and material formal run |
| **M-6 Recursive Delegation** | `agent.spawn` as nested execution lineages | RF-55–RF-59; four-dimensional additive conservation; independent depth/turn limits; join, cancellation, kill-tree recovery | **IMPLEMENTATION COMPLETE — acceptance review open** | independent review and recorded evidence receipt |
| **M-6.5 Adaptive Strategy** | `ProgressProjection` + meta-controller as policy/reducer/plugin | Deliberately blocked tasks show observable strategy change; paired runs with/without the controller show measured improvement | **IMPLEMENTATION ACTIVE — pure seam hardened; measurement not run** | M-4 telemetry (measurement); M-6 only for the delegate action |
| **M-7 Topologies & Justified Concurrency** | Topology as versioned artifact/config; causal partial order; simple safe parallelism | ≥3 topologies through one runtime with zero kernel/episode diff; advanced scheduler only if M7-01 justifies it | **PREPARATION ACTIVE — topology/scheduler contracts prepared; I-11 remains sequential** | M-6.5 + M7-01 result + ADR-0099 |
| **M-8 Memory, Skills, Learning** | Retrieval and memory as projections/plugins; versioned skills derived from trajectories | Measured lift on a held-out set with provenance and tested rollback | **PREPARATION ACTIVE — exterior contract kit prepared; ADR-0100 open** | M-7 + ADR-0100 |
| **M-9 AETHER v1.0** | Integrated coding + formal + research general agent framework | Adaptation, transfer, and long-horizon criteria met; v1.0 release | **PLANNED** | M-8 |

### Always-parallel lanes

These never block on a milestone. They block only on their own named interface.

| Lane | Home | Depends on |
|---|---|---|
| Model & tool adapters | `vanguard/packages/adapters/` | `ports/` |
| UI / CLI | `vanguard/clients/cli/` | client request contract |
| Indexing & retrieval | adapters | `IndexPort` |
| Context management | `agency/context/` | generic; no kernel change |
| Coding pack tool loop | `packs/code-default/` | existing SPI |
| Tooling, linters, docs | `tools/`, `docs/` | — |
| **M7-01 concurrency measurement** | analysis only | none — **named historical lane, retained** |

**M7-01** keeps its identifier and its provenance (`ADR-0092`). It captures actual sequential
`EffectStarted`/settlement records with resolved resources, selectors, sinks, idempotency keys,
timing, WAL contention, and cache-hit rates over a fixed-seed workload. It may not add concurrency,
scheduler, workers, claims, leases, or topology. It terminates in an explicit Director decision to
**implement, simplify, or cancel**, recorded as a successor ADR. Below ~30% useful independence the
default decision is to cancel advanced scheduling and retain I-11 — that is a success of the process,
not a failure. This decision is an input to M-7 and does not gate M-4, M-5a, M-5b, M-6, or M-6.5.

## Milestone identifier mapping

Historical identifiers keep their historical meaning; `ADR-0095` §4 is authoritative for translation.
Older documents and ADRs are read through this table rather than edited.

| Historical id | Historical meaning | v0.7+ successor |
|---|---|---|
| M-4 | Product coding proof (RF-95) | **M-4**, plus trajectory capture |
| M-5 | Formal Pack #2 (RF-86) | split into **M-5a** then **M-5b** |
| M-6 | Mediated `agent.spawn` | **M-6**, reframed as nested lineages |
| M-7 | Measured scheduler / concurrency | folded into **M-7**; M7-01 keeps its name |
| M-8 | Declarative topology support | folded into **M-7** |
| M-9 | Retrieval, skills, macro laboratory | **M-8** |
| M-10 | Governed meta-cognition | **M-6.5** (operational) and **M-9** (integration) |

## Milestone contracts

### M-4 — product proof and scientific baseline (RF-95)

One fixed coding task completes through the canonical coding pack and `Runtime.run_composed` with a
live attributable provider, mediated repository observation, an authorized real file mutation and
non-empty diff, a passing preregistered verification receipt, the `product` profile in `D_R`,
file-backed SQLite-WAL, a complete terminal trajectory, and fresh-process reconstruction. No
fake/cassette model, alternate driver, stitched trace, or manual event repair qualifies.

M-4 additionally installs the observability that the rest of the roadmap is measured with: model
invocations, selected context, tool calls, effects, failures, retries, latency, tokens, cost,
artifacts, and outcomes, following the provenance rule in
[`../01_law/EVIDENCE.md`](../01_law/EVIDENCE.md). Without it, M-6.5, M-7, and M-8 are unfalsifiable
by construction.

Host execution is allowed; it remains an adapter behind the same capability mediation and ledger. It
is not permission for the client or model to mutate the workspace outside the substrate.

### M-5a — the agent becomes a projection

M-5a defines which facts are semantically necessary to reconstruct an agentic execution: goal
declaration, plan creation and revision, observation, proposal, effect settlement, progress
assessment, strategy change, context compaction, evaluation, and conclusion.

The criterion for introducing an event kind is **not** "this happened internally". It is: *does this
change the history we must reconstruct or analyze?* Each new kind still requires an ADR, allocation,
writer, reducer, schema, conformance vector, and coverage proof.

`AgentView` is a **projection, not a second source of truth**. The canonical ledger reducer stays
single; domains may hold their own projections over it. What stays stable across domains are the
contracts for event identity, lineage, persistence, effects, and composition.

M-5a knowingly changes substrate semantics and therefore happens **before** the baseline used to
prove generality. The historical `M-5-BASE` tag is immutable and MUST NOT move. `M-5A-BASE-v2` is
created once only after the migration lands and gates are green.

### M-5b — generality as falsification

M-5b tries to break the abstraction with a materially non-coding domain producing a deterministic,
independently checkable witness. If executing it requires mathematical knowledge in the kernel, a
change to the generic episode mechanism, or a second runtime, that is an architectural finding.

**OD-3 is decided: SAT/CNF with complete-assignment witnesses.** The exterior oracle checks every
clause deterministically from pinned DIMACS and witness bytes; it performs no search and the
generator cannot self-grade. This gives an exact positive witness and negative vectors with no
solver dependency or substrate knowledge. Lean/SMT remain later pack candidates, not M-5b gates.

RF-86 is measured as a diff against `M-5A-BASE-v2` over `vanguard/packages/{domain, kernel, ports,
runtime, agency/episode}` and runs in CI as `ci/rf86_gate.sh`. Two rules are binding:

1. **`M-5A-BASE-v2` MUST be created only after the ADR-authorised substrate change lands.** Creating
   it early makes the gate fire on the authorised change itself; the historical `M-5-BASE` remains
   immutable provenance.
2. **RF-86 MUST NOT be weakened to accommodate a substrate change** — not by narrowing the frozen
   paths, not by allowlisting a file, not by downgrading the failure to a warning. A substrate change
   with no ADR behind it is the finding, not the tag.

The gate fails closed when `M-5A-BASE-v2` does not resolve, so `actions/checkout` runs with
`fetch-depth: 0` and the tag is pushed alongside the branch.

### M-6 — recursion as nested lineages

Spawn does not instantiate an agent. It creates a child lineage with its own identity, parent
reference, goal, selected context, budget, capabilities, depth boundary, and terminal conditions,
which produces its own events and artifacts and whose result the parent incorporates. Recursion is
the nesting of bounded causal regions.

Recovery follows from this: neither parent nor child must survive as a process. Reopen the ledger and
classify each lineage as complete, interrupted, waiting, or still executable. The kill-tree drill —
SIGKILL the parent mid-child, assert the cold path returns `UNDETERMINABLE` and never a silent
retry — is part of the gate.

### M-6.5 — metacognition without privilege

A meta-controller observes projections of progress, failure, repetition, uncertainty, budget
consumption, or missing knowledge, and selects a strategy: revise the plan, request context, abandon a
hypothesis, change verification, delegate, or stop.

No decision rewrites history. `PlanRevised` does not delete the previous plan; it supersedes it in the
projection while preserving the path by which the change happened. That is precisely what makes the
approach scientifically useful later.

**Metacognition is policy/reducer/plugin, never a kernel primitive.** Its benefit is established by
paired runs with and without the controller over success rate, wasted loops, tool calls, cost,
latency, failure recovery, and final quality.

### M-7 — structure, time, and justified concurrency

Topology defines structure: which roles or lineages exist, which causal relations are permitted, who
may request work from whom, which artifacts connect stages. The scheduler decides temporality: among
ready operations, which run first, where, which are parallelized, suspended, or prioritized. The
kernel decides admissibility. The ledger records what happened. **These four responsibilities do not
merge.**

A role is not a new class — it is a lineage created with a given policy, context configuration,
capabilities, and goal. Direct agent, planner/executor, critic/reviser, debate, research fan-out, and
bounded tree search become configurations of one operational language.

Simple, obviously safe parallelism (independent reads, independent searches) may land as soon as the
contracts permit. Advanced scheduling — claim TTL, leasing, worker pools — requires the M7-01 result
and a successor ADR, because the hard part is budget reservation, idempotent settlement, and recovery
with in-flight effects, not the reads.

### M-8 — memory, skills, and learning

Memory and retrieval are projections and plugins, never canonical truth. Skills are versioned
reusable structures — prompt policies, small programs, parameterized operation sequences, topology
fragments, heuristics, strategy policies — derived from analyzed trajectories.

The lifecycle is: runs produce trajectories; trajectories produce data; analysis identifies success
and failure patterns; candidate skills or policies emerge; candidates are evaluated on independent
workloads; improved versions are explicitly promoted; poor versions are rolled back.

**An agent may propose a skill; it may not unilaterally declare it better.** Promotion requires
explicit evaluation, provenance, and tested rollback.

### M-9 — AETHER v1.0

Integration of coding, formal reasoning, research, event-derived identity, durable recovery,
recursive delegation, metacognitive replanning, topologies, long-term memory, skill acquisition,
model/tool routing, bounded autonomous execution, and full observability and reproduction.

The v1 test is not component count. It is: solve novel tasks in at least three domains; create and
revise plans autonomously; recognize failure and change strategy; delegate subtasks; recover after a
crash; reuse knowledge from prior executions; produce verifiable results; improve policies/skills
without modifying the core; operate over long horizons under bounded budget; and keep working when
models, tools, and topologies are replaced.

This is released as **AETHER v1.0 General Agent Framework**. No AGI claim is made or implied.

## Standing Architectural Constraints

- [`VISION.md`](../../VISION.md) is Law Zero. This file sequences it; it does not amend it.
- `sprint_active.md` is the only current implementation authority.
- S0–S12, monotonic attenuation, typed budgets, JCS, `D_H/D_R/D_X`, single-writer ledger truth, and
  I-9 continuity remain frozen. Assurance mechanisms remain available as optional profiles; profile
  identity in `D_R`, no false promotion claims, and fail-closed behaviour on an explicitly requested
  unavailable profile remain binding in every mode.
- I-11 sequential execution remains mandatory until M-7 measurement and explicit Director lift.
- Composition is a static declaration of possibilities; the trajectory is the emergent causal graph.
  Neither is a runtime workflow engine.
- Memory, skills, learning, topology, scheduling, and metacognition never become kernel semantics.
- A new event kind requires a successor decision, allocation, writer, reducer, schema, conformance
  vector, and coverage proof.
- No broad rewrite, third runtime, domain-specific kernel branch, or package-per-concept taxonomy.

## Two-Lane Delivery Model

| Dimension | Devs A — Principal / Specialist | Devs B — Senior Developers |
|---|---|---|
| Primary responsibility | Irreversible or cross-module architecture, contract ownership, identity, lifecycle, composition/activation integration, final technical arbitration within ratified law | Bounded implementation of frozen contracts: packs, adapters, persistence wiring, fixtures, callers, conformance, CI, migrations |
| Autonomy | May decide high-level reversible design within the active charter without per-task approval | May decide local implementation details without changing an interface, authority boundary, or accepted decision |
| Prohibited delegation | Unresolved ontology, trust, identity, event-writer, compatibility-sunset, or recovery decisions cannot be delegated to B | Must not redesign kernel, authority, identity, canonicalization, lifecycle ownership, event semantics, or recovery |
| Integration | Publishes interface + RED contract; owns shared hotspots and cross-lane merge | Builds against frozen interfaces; rebases after A contract slices; reports architectural gaps as falsifiers |
| Acceptance | Cannot self-certify a cross-lane gate | Cannot close a milestone from local tests alone |

Every task moved to the active board MUST state: owner lane/class, exact outcome, affected modules,
dependencies, architectural risk, migration path, rollback, acceptance criterion, allocated falsifier,
evidence artifact, definition of done, and prohibited scope.

```text
A interface + RED -> B bounded implementation -> A integration
-> cross-lane gate -> full repository gates -> independent sign-off
```

## Dependency Rules

- Work is blocked only by a named unfinished interface, schema, invariant, primitive, or runtime
  contract — never because a preceding milestone has not been ceremonially closed.
- `M-5A-BASE-v2` must point to the reviewed post-M-5a substrate before Formal Pack or mediated-
  delegation work can produce promotion evidence. Pack/adapter preparation outside the frozen
  substrate may proceed earlier, but RF-86 fails closed until the tag resolves. The historical
  `M-5-BASE` tag is never moved.
- An ADR-authorized substrate correction makes the old RF-86 baseline intentionally red; advance the
  tag only after the correction is committed and verified. RF-86 is never weakened.
- ADR-0090/0091 prepare M-6 event/digest semantics but do not activate delegation.
- Topology decides what may run; scheduler decides when/where; kernel decides whether an effect is
  authorized; the ledger records what happened. These responsibilities do not merge.
- Security/assurance may vary by execution profile. Layer boundaries, event lineage, and authority
  mediation do not.
- Reviews under `_archive/` are inputs, never execution authority.

## Common Gate Sequence

```text
accepted ADR when architecture changes
-> allocated RED falsifier
-> focused suites
-> full Python and TypeScript gates
-> boundaries / TCB / domain blindness / event coverage / duplication
-> RF IDs / metadata / links / stale paths / secrets
-> real-run evidence
-> independent milestone decision
```
