---
id: normative-spec-index
class: law
authority: normative
canonical_for:
  - normative-specification
  - invariant-registry
status: living
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-23
read_when:
  - implementing-any-runtime-change
  - resolving-authority-conflicts
do_not_read_when:
  - consulting-historical-proposals
supersedes: []
superseded_by: null
---

# SPEC — Vanguard Meta-Harness Framework (MHF v1)

This file is the compact normative index. RFC-2119 terms (MUST, SHALL, SHOULD, MAY) are binding.
The detailed clauses remain canonical in the linked law leaves under [`01_law/`](01_law/); this
index intentionally keeps the axioms, invariant registry, refusals, and navigation contract in one
small bundle. Accepted ADRs explain why a rule exists; they never weaken this law unless this index
and the applicable law leaf are amended together. Reviews, proposals, research, and `_archive/` are
historical evidence only.

## Authority and precedence

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

- The runtime never executes a dynamic control-flow DAG. `mhf.manifest/2` is a static composition
  graph; the turn loop stays unary and sequential. Multi-agent behavior is mediated delegation
  (`agent.spawn`, M-6) or a composed plugin.
- UDS and in-process dispatch share schemas and wire semantics, but in-process execution is direct,
  zero-copy memory dispatch; it does not pay socket/serialization overhead for context bundles.
- A turn owns an ordered list of `invocations`, so retries and escalations conserve additive costs.
- `evaluation: none` is declared before execution and derives `unattributable_for_promotion = true`.
  Unsigned or forged verdicts fail closed.
- Cold continuation loads durable pre-crash events, joins the trajectory prefix, reconciles pending
  Governor leases (no budget leak), and emits `RunRecovered` before a complete `mhf.trajectory/1` at
  `EpisodeCompleted`.

## Milestone compatibility

| Milestone | Version | Gate |
|---|---|---|
| M-0 | v0.6.0 | CI truth and falsifiers F-01…F-21 — complete |
| M-1 | v0.6.0 | signed Ed25519 trust spine and verdicts — complete |
| M-2 | v0.6.1 | one runtime, RF-23 truthful trajectory, RF-25 cold continuation — Wave 2C |
| M-3 | v0.6.2 | `mhf.manifest/2`, plugin lifecycle, layer0 removal |
| M-4 | v0.6.3 | one real, un-forged E2E run with nine evidence lines |
| M-5…M-10 | future | Pack #2, mediated spawn, Pareto concurrency, builder, macros, active inference |

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

See [`EXTENSIBILITY.md`](01_law/EXTENSIBILITY.md#packs-and-domain-boundaries).

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
