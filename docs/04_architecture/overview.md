---
id: system-overview-and-audit
class: architecture
authority: descriptive
canonical_for:
  - system-architecture-overview
  - repository-inventory
status: living
owner: senior-principal-systems-engineer
version: "0.8.0"
last_verified: 2026-08-26
read_when:
  - orienting-in-the-system-architecture
do_not_read_when:
  - implementing-a-specific-contract
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Vanguard / AETHER System Overview

> **Classification:** Descriptive architecture with explicit current/target maturity.
> **Authority:** Non-normative and introduces no architecture of its own. Governing authority is
> [`VISION.md`](../../VISION.md) (Law Zero), then [`docs/SPEC.md`](../SPEC.md) and
> [`docs/01_law/`](../01_law/).

---

## 1. System Charter

**AETHER is a general event-sourced agentic computation framework and experimental substrate.** The
fundamental unit is a **typed causal operation within an execution lineage**. An agent is a
projection over lineage, events, artifacts, policy, context, budget, and execution boundaries — not a
persistent privileged object.

### Layer decomposition

| Layer | Owns | Must not own |
|---|---|---|
| **Kernel** | Minimal generic invariants: authority, budgets, effect admissibility | Any domain, topology, scheduling, memory, or meta semantics |
| **Event / Artifact substrate** | Durable causal facts, lineage, reducers, identities, artifacts | Derived state as truth |
| **Runtime** | Composition, sessions, lifecycle, effects, persistence, reconstruction | Domain behavior |
| **Agency** | Generic observation/proposal/operation transition mechanics | Specific agents |
| **Extensibility** | Tools, model adapters, plugins, indexes, context providers, evaluators, protocol adapters | Authority |
| **Packs & policies** | How capabilities are organized for concrete tasks | Substrate semantics |
| **Topology / scheduler / memory / learning / meta-control** *(future)* | Structure, temporality, projections, adaptation | New cores |

Behavioral complexity grows at the edges; the trusted core stays small.

### Four separated responsibilities

```text
Topology   defines WHAT may run        (structure; versioned data)
Scheduler  decides WHEN/WHERE          (readiness, placement, temporality)
Kernel     decides WHETHER authorized  (generic invariants)
Ledger     records WHAT HAPPENED       (append-only truth)
```

These never merge. Topology and scheduler value mechanisms exist, but public runtime integration and
the ADR-0099 scheduling decision remain open.

### Composition vs trajectory

**Composition** is the static declaration of the space of possibilities (`mhf.manifest/2`, frozen into
`D_H`). **Trajectory** is the emergent causal graph of what was actually used, recorded in the ledger
and observed after the fact. The runtime is not a workflow engine and executes no dynamic control-flow
DAG as a substrate authority.

### Physical order vs logical causality

`seq` is durable append order within a `project_id`. It is **not** logical dependency. Causation,
parentage, correlation, lineage, branches, and joins define the logical, partially ordered execution
graph. Branch/join/readiness semantics are target architecture (M-7), not current behavior.

### Maturity

| Area | Today | Target |
|---|---|---|
| Ledger, cold replay, composition, S0–S12, profiles | implemented | unchanged |
| Coding product + scientific trajectory capture | mechanisms present; RF-95 bundle/review absent | independently accepted M-4 proof |
| Agent state as projection (`AgentView`) | implemented; successor baseline gate open | accepted M-5a control |
| Delegation | partial; synthetic fallback, durable identity and budget binding gaps | canonical recursive M-6 runtime |
| Meta-control/topology | package mechanisms present; experiments/integration open | valid M-6.5 result and M-7 decision |
| Memory/learning | in-memory prototypes only | ADR-0100 durable authorized M-8 MVP |

---

## 2. The Three Planes of Responsibility

```text
┌────────────────────────────────────────────────────────────────────────┐
│                          1. DECISION PLANE                             │
│ Ephemeral context compilation, model proposals, turn loops (Unprivileged)│
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ kernel.dispatch()
┌───────────────────────────────────▼────────────────────────────────────┐
│                           2. STATE PLANE                               │
│ Single-writer SQLite WAL causal stream: State = fold(EventLog)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ evaluate_run()
┌───────────────────────────────────▼────────────────────────────────────┐
│                          3. EVIDENCE PLANE                             │
│ Cryptographic identities (DH, DR, DX) & Exterior Ed25519 Signed Verdicts │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Decision Plane**: Unprivileged LLM prompt completion, reasoning, and intent proposal.
2. **State Plane**: Immutable causal event log where derived state is strictly computed via deterministic reducers.
3. **Evidence Plane**: Verifiable hash identities ($D_H, D_R, D_X$), artifact content digests, and independent evaluator signatures.

---

## 3. The A-B-C-D Foundation

- **`A` — Authority (`AS_BUILT`)**: S0–S12 mediation, selectors, attenuation, typed leases, and fail-closed policy ([`kernel/dispatch.py`](../../vanguard/packages/kernel/dispatch.py)).
- **`B` — Bundle (`MIXED`, M-3C ACTIVE)**: `/2` and registry contracts exist, while the public runtime still requires convergence to `FrozenComposition -> ActivationPlan -> RunPlan`.
- **`C` — Corpus (`AS_BUILT CORE`, M-4 BINDING PENDING)**: RF-23/RF-25 are retained green; M-3C must derive the nine-row evidence bundle from canonical sources.
- **`D` — Digests (`AS_BUILT CORE`, CROSS-BINDING PENDING)**: $D_H \ne D_R \ne D_X$ remains law; activation and foundation evidence must preserve their subjects.

---

## 4. Hexagonal Boundary Lattice

```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a client slot of runtime)
```

- **`domain/`**: Pure Python stdlib value objects, events, JCS canonicalization, and selector algebra.
- **`ports/`**: Hexagonal boundary protocols: kernel dependencies plus model, sandbox, evaluator, stores, environment, determinism, index, and five SPIs.
- **`kernel/`**: Pure Trusted Computing Base ($\le 1438$ LOC budget). 13-stage dispatch pipeline, monotonic attenuation, and typed budget algebra.
- **`agency/`**: Turn engine (`EpisodeEngine`), current attenuated child construction, and context compaction. Capability-mediated `agent.spawn` through S0–S12 remains queued for M-6.
- **`runtime/`**: Composition root (`compose.py`), session management, and single-writer ledger emitter.
- **`adapters/`**: Port implementations (OpenRouter, Ollama, Cassette, Fake, bwrap sandbox, evaluator daemon).

---

## 5. Navigational Map to Deep Modular Topics

| Deep Topic | Canonical Modular Location |
|---|---|
| **C4 Context, Container & Components** | [`docs/04_architecture/`](./) · [`c4_context.md`](c4_context.md) · [`c4_component.md`](c4_component.md) |
| **S0–S12 Dispatch & Replay Sequences** | [`sequences.md`](sequences.md) |
| **Episode & Plugin State Machines** | [`state_machines.md`](state_machines.md) |
| **Traceability Matrix (Concept $\leftrightarrow$ Code $\leftrightarrow$ Test)** | [`traceability_matrix.md`](traceability_matrix.md) |
| **Wire & Event Contracts** | [`docs/05_contracts/events.md`](../05_contracts/events.md) · [`trajectories.md`](../05_contracts/trajectories.md) |
| **Hexagonal Port Protocols** | [`docs/06_protocols/kernel.md`](../06_protocols/kernel.md) · [`evaluator.md`](../06_protocols/evaluator.md) |
| **Mathematical & Cognitive Theory** | [`docs/08_theory/active_inference.md`](../08_theory/active_inference.md) · [`economic_resources.md`](../08_theory/economic_resources.md) |
| **Autonomous Contributor Guides** | [`docs/07_engineering/development.md`](../07_engineering/development.md) · [`context_bundles.md`](../07_engineering/context_bundles.md) |
