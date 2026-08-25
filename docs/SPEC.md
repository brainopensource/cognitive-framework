---
id: normative-spec-index
class: law
authority: normative
canonical_for:
  - normative-specification
  - invariant-registry
status: living
owner: principal-systems-architect
version: "0.7.0"
last_verified: 2026-08-24
read_when:
  - implementing-any-runtime-change
  - resolving-authority-conflicts
do_not_read_when:
  - consulting-historical-proposals
subordinate_to: VISION.md
supersedes: []
superseded_by: null
---

# AETHER Normative Specification — Higgs Release (v0.7.0)

## What AETHER is

AETHER is a **general event-sourced agentic computation framework and experimental substrate**. It is
not primarily a security-certification system, a coding harness, or a workflow engine. The
fundamental unit is a **typed causal operation occurring within an execution lineage**. An "agent" is
not a privileged persistent object; it is a dynamic projection over lineage, events, artifacts,
policy, context, budget, and execution boundaries.

Events are the canonical causal history. Artifacts retain large relevant content. Projections
reconstruct semantic state. Caches and indexes remain derived and rebuildable. The kernel stays
minimal and domain-blind. Memory, skills, learning, topologies, and metacognition are higher-level
projections, plugins, or policies composed from the same primitives — never new kernel semantics.

This identity is fixed by [`VISION.md`](../VISION.md) (Law Zero) under
[`ADR-0095`](02_decisions/0095-vision-as-law-zero-and-roadmap-reconciliation.md). This specification
translates it into current normative requirements; it does not restate or amend it.

---

This file is the compact normative index. RFC-2119 terms (MUST, SHALL, SHOULD, MAY) are binding.
The detailed clauses remain canonical in the linked law leaves under [`01_law/`](01_law/); this
index intentionally keeps the axioms, invariant registry, refusals, and navigation contract in one
small bundle. Accepted ADRs explain why a rule exists; they never weaken this law unless this index
and the applicable law leaf are amended together. Reviews, proposals, research, and `_archive/` are
historical evidence only.

## Authority and precedence

0. [`VISION.md`](../VISION.md) is **Law Zero** (`class: charter`, `authority: constitutional`,
   `status: locked`). It defines architectural identity, ontology, product principles, and long-term
   direction for v0.7+. This specification and every leaf below it are **subordinate to it**. A
   conflict between this specification and the locked Vision is resolved in favour of the Vision, and
   the conflicting clause here MUST be reconciled rather than cited as a counter-authority. The Vision
   changes only through an explicit Vision-superseding ADR (`ADR-0095`).
1. This specification and the six `class: law`, `authority: normative` leaves in
   [`01_law/`](01_law/) form the normative specification. No one leaf has independent precedence;
   a change that affects more than one leaf MUST update every affected clause atomically.
2. Append-only decisions in [`02_decisions/INDEX.md`](02_decisions/INDEX.md) record rationale and
   amendments; an accepted ADR is binding only when reflected in the law.
3. [`03_execution/sprint_active.md`](03_execution/sprint_active.md) is the sole current work board;
   [`03_execution/milestones.md`](03_execution/milestones.md) is sequencing, not authorization.
4. Architecture, contracts, protocols, engineering guides, and theory are descriptive or advisory
   and must link back to law rather than restating it.
5. [`_archive/`]( _archive/) is frozen provenance. It is scanned for links and secrets but excluded
   from normal implementation context bundles.

## Design axioms A-1…A-6

- **A-1 Microkernel:** the S0–S12 effect reference monitor is the bounded TCB; domain, evaluation,
  scheduling, models, sandboxes, and plugin code remain outside it behind typed boundaries.
- **A-2 Two authority systems:** capability grants constrain agents; plugin isolation constrains
  plugin code. Neither system trusts the other's subject.
- **A-3 Events are truth:** grants, budgets, approvals, lifecycle, evaluation, and spawn effects are
  durable events. Fresh-process replay, not an in-memory double fold, proves replay parity.
- **A-4 One schema:** JSON Schema, JCS, and golden vectors are the wire source of truth; generated
  Python/TypeScript readers replace handwritten mirrors.
- **A-5 Harness identity:** `D_H` hashes every behavior-affecting composition input. `D_R` adds the
  runtime/environment/model/oracle identity and `D_X` adds dataset/protocol identity; never collapse
  the three.
- **A-6 Asymmetric evolution:** new authority verbs require a bound falsifier and TCB proof; all
  other evolution lands as packs, plugins, manifests, adapters, policies, or exterior pipelines.

## Invariant registry I-1…I-11

| ID | Short invariant | Canonical detail |
|---|---|---|
| I-1 | One schema-generated `EffectRequest` | [`01_law/RUNTIME.md`](01_law/RUNTIME.md#invariants-i-1--i-11) |
| I-2 | Emitted equals declared; forged is rejected | [`01_law/RUNTIME.md`](01_law/RUNTIME.md#invariants-i-1--i-11) |
| I-3 | Every control merges with its call site | [`01_law/RUNTIME.md`](01_law/RUNTIME.md#invariants-i-1--i-11) |
| I-4 | Durable fresh-process replay | [`01_law/RUNTIME.md`](01_law/RUNTIME.md#13-determinism--replay-contract) |
| I-5 | Exterior signed judge | [`01_law/EVIDENCE.md`](01_law/EVIDENCE.md#evaluator-and-verdicts) |
| I-6 | Plugins untrusted by default | [`01_law/DISPATCH.md`](01_law/DISPATCH.md#6-the-workload-perimeter) |
| I-7 | Domain-blind kernel | [`01_law/DISPATCH.md`](01_law/DISPATCH.md#1-the-trusted-computing-base) |
| I-8 | Specifications are generated or normative, never both | [`01_law/RUNTIME.md`](01_law/RUNTIME.md#invariants-i-1--i-11) |
| I-9 | Complete recovered trajectory | [`01_law/EVIDENCE.md`](01_law/EVIDENCE.md#trajectory-accounting) |
| I-10 | Metaphors are not architecture | [`01_law/RUNTIME.md`](01_law/RUNTIME.md#invariants-i-1--i-11) |
| I-11 | Single sequential turn loop | [`01_law/RUNTIME.md`](01_law/RUNTIME.md#11-the-turn-state-machine) |

## Law map

| Subject | Read this first | Use when |
|---|---|---|
| Dispatch, leases, failure paths | [`DISPATCH.md`](01_law/DISPATCH.md) | changing kernel, grants, isolation, or recovery gates |
| Turn loop, events, replay, cold continuation | [`RUNTIME.md`](01_law/RUNTIME.md) | changing sessions, ledger, or runtime lifecycle |
| Manifests, plugins, SPIs, packs | [`EXTENSIBILITY.md`](01_law/EXTENSIBILITY.md) | changing composition or plugin lifecycle |
| Trajectories, evaluator, identities | [`EVIDENCE.md`](01_law/EVIDENCE.md) | changing verdicts, evidence, or cost accounting |
| Statistical measurement and promotion | [`MEASUREMENT.md`](01_law/MEASUREMENT.md) | changing experiments or promotion claims |
| Capabilities, TCB, threat model | [`SECURITY.md`](01_law/SECURITY.md) | changing trust boundaries or sandbox policy |

## Architectural refusals

- The sole production chain is `mhf.manifest/2 -> CanonicalManifest -> FrozenComposition ->
  ActivationPlan -> RunPlan -> EpisodeEngine`. Compatibility formats normalize at ingress and never
  become a second runtime value. `FrozenComposition` owns `D_H`; activation/runtime identity binds
  it into `D_R`.
- The runtime never executes a dynamic control-flow DAG *as a substrate authority*. `mhf.manifest/2`
  is a static composition graph declaring the space of possibilities; the trajectory recorded in the
  ledger is the emergent causal graph of what was actually used. The turn loop stays unary and
  sequential (I-11) until M-7 measurement and an explicit Director lift. Multi-agent behavior is
  mediated delegation (`agent.spawn`, M-6) or a composed plugin — never a second engine.
- **An agent is not a persistent privileged object.** `Agent = Identity + Policy + Event-Derived
  Projection + Execution Boundary`. Runtime objects MAY hold transient optimization state, but no
  state required for semantic continuation may exist only inside them (see
  [`01_law/RUNTIME.md`](01_law/RUNTIME.md#15-agent-state-is-a-projection)). Target architecture;
  M-5a closes the current gap.
- **Memory, skills, learning, topology, scheduling, and metacognition are never kernel semantics.**
  They land as projections, plugins, policies, or versioned configuration over the same primitives.
  A meta-controller holds no special authority and passes through S0–S12 like any other proposer.
- UDS and in-process dispatch share schemas and wire semantics, but in-process execution is direct,
  zero-copy memory dispatch; it does not pay socket/serialization overhead for context bundles.
- A turn owns an ordered list of `invocations`, so retries and escalations conserve additive costs.
- `evaluation: none` is declared before execution and derives `unattributable_for_promotion = true`.
  Unsigned or forged verdicts fail closed.
- Cold continuation loads durable pre-crash events, joins the trajectory prefix, reconciles pending
  Governor leases (no budget leak), and emits `RunRecovered` before a complete `mhf.trajectory/1` at
  `EpisodeCompleted`.
- M-4 product evidence (RF-95) is derived from one real-model coding run through canonical
  composition, ordinary mediated tools, a real workspace diff, task verification, file-backed WAL,
  trajectory, and fresh-process reconstruction. Synthetic providers, alternate drivers, stitched
  traces, and manual event repair cannot satisfy the gate.
- RF-85 retains the stronger nine-row hermetic assurance contract but no longer blocks M-4 or M-5.
  Its canonical auditor distinguishes `absent`, `invalid`, `unverifiable`, and `present_valid`; only
  a complete envelope bound to immutable preregistration and authoritative verifiers may be
  promotion-eligible. An unresolved S8a intent remains F-22 `undeterminable` in every profile.
- `agent.spawn` is a generic S0–S12 effect whose post-intent child creation belongs to a runtime
  adapter; the kernel MUST NOT branch on the verb or know child topology.
- Scheduler claim TTL/heartbeat is coordination metadata, not budget `millis`. Concurrent physical
  attempts are at-least-once; durable settlement is idempotent/exactly-once per command identity.
- M-8 topology is declared component/policy data lowered to ordinary scheduling and mediated spawn.
  A substrate workflow/topology engine requires RF-66 reversal evidence and a successor ADR.
- Execution assurance is explicit and identity-bearing: the resolved `ExecutionProfile` MUST enter
  `D_R`; `product`, `local`, `sandboxed`, and `hermetic` are distinct modes. Product execution MAY
  use the host adapter with durable WAL and explicit approvals. An unavailable requested containment
  mode MUST fail closed rather than silently falling back to the host.
- The runtime bootstrap is the sole production seam for concrete adapter construction. Plugin
  activation MUST materialize a service/handle or fail; lifecycle metadata without a callable service
  is not production activation.

## v0.7+ concept lock

[`VISION.md`](../VISION.md) is Law Zero; `ADR-0095` locks the architectural thesis and the roadmap.
`ADR-0094` remains in force: M-4 is the RF-95 useful, durable coding proof and RF-85 is an optional
hermetic assurance certification. The substrate baseline is re-tagged after **M-5a**, so RF-86
measures Formal Pack #2 against the event-derived agent semantics rather than against a substrate
that is about to change. Prior sequencing in ADR-0088/0093 is superseded by `ADR-0095` §3–§4;
their composition, identity, refusal, and release-baseline content is retained.

## Milestone compatibility

Sequencing detail and technical dependencies live in
[`03_execution/milestones.md`](03_execution/milestones.md). Historical identifiers keep their
historical meaning; `ADR-0095` §4 is the authoritative translation table.

| Milestone | Version | Gate |
|---|---|---|
| M-0 | v0.6.0 | CI truth and falsifiers F-01…F-21 — complete |
| M-1 | v0.6.0 | signed Ed25519 trust spine and verdicts — complete |
| M-2 | v0.6.1 | one runtime, RF-23 truthful trajectory, RF-25 cold continuation — complete |
| M-3 | v0.6.2 | graph/lifecycle contracts and layer0 removal — complete |
| M-3C | v0.6.2 | RF-78…RF-84 canonical composition, activation, durability, evidence — complete |
| M-4 | v0.7.0 | RF-95: one useful real-model coding run with mediated observe/edit/verify, durable WAL, complete trajectory, fresh-process reconstruction — **plus scientific trajectory capture** |
| M-5a | v0.7.x | Event-derived `AgentView`, lineage/scope semantics, provenance for context/cache/compaction; substrate re-tagged to a new `M-5-BASE` |
| M-5b | v0.7.x | RF-86 Formal Pack #2 parity plus RF-52/RF-53 T0 witness, measured against the post-M-5a baseline |
| M-6 | v0.8.0 | RF-55…RF-59 mediated `agent.spawn` as nested execution lineages through generic S0–S12 dispatch |
| M-6.5 | v0.8.x | Adaptive strategy / meta-control as policy, reducer, or plugin; measured against paired runs without it |
| M-7 | v0.9.0 | Declarative topologies as versioned data, plus measured concurrency/parallelism where justified (M7-01 result and successor ADR) |
| M-8 | v0.9.x | Memory, retrieval, skills, and learning as projections with held-out evaluation, provenance, and rollback |
| M-9 | v1.0 | Integrated AETHER v1.0 General Agent Framework |

## Compatibility anchors for former SPEC sections

The detailed body formerly carried by this file is preserved verbatim (apart from path metadata) in
[`01_law/RUNTIME.md`](01_law/RUNTIME.md). These anchors keep existing deep links stable:

## 0. Design Axioms

See [axioms above](#design-axioms-a-1a-6).

## 1. Layer 0 — The Microkernel

See [`RUNTIME.md`](01_law/RUNTIME.md#1-layer-0--the-microkernel).

## 2. Plugin Architecture & SPI Definitions

See [`EXTENSIBILITY.md`](01_law/EXTENSIBILITY.md).

## 3. Autonomous Execution Safety & Deterministic State

See [`RUNTIME.md`](01_law/RUNTIME.md#3-autonomous-execution-safety--deterministic-state).

## 4. Coding Domain Pack (first domain; foundation E2E, not this lock wave)

See [`EXTENSIBILITY.md`](01_law/EXTENSIBILITY.md#read-map).

## 5. Evolution Blueprint — Phase 2 (autonomous & meta-cognitive)

See [`RUNTIME.md`](01_law/RUNTIME.md#5-evolution-blueprint--phase-2-autonomous--meta-cognitive).

## 6. Evolution Blueprint — Phase 3 (General Task Solver)

See [`RUNTIME.md`](01_law/RUNTIME.md#6-evolution-blueprint--phase-3-general-task-solver).

## 7. Telemetry, Self-Tuning & Model Distillation

See [`MEASUREMENT.md`](01_law/MEASUREMENT.md) and [`RUNTIME.md`](01_law/RUNTIME.md#7-telemetry-self-tuning--model-distillation).

## 8. Migration Plan & CI Gates (v0.6.1)

See [`03_execution/milestones.md`](03_execution/milestones.md) and [`03_execution/sprint_active.md`](03_execution/sprint_active.md).

## 9. What This Specification Refuses To Build

See [architectural refusals](#architectural-refusals).

## Invariants I-1 … I-11

See [the invariant registry](#invariant-registry-i-1i-11).
