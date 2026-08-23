---
id: system-overview-and-audit
class: architecture
authority: descriptive
canonical_for:
  - system-architecture-overview
  - repository-inventory
status: living
owner: senior-principal-systems-engineer
version: "0.6.1"
last_verified: 2026-08-21
read_when:
  - orienting-in-the-system-architecture
do_not_read_when:
  - implementing-a-specific-contract
supersedes: []
superseded_by: null
---

# Vanguard / AETHER System Overview

> **Classification:** Descriptive architecture with explicit current/future maturity.
> **Authority:** Non-normative. Governing law lives in [`docs/SPEC.md`](../SPEC.md) and [`docs/01_law/`](../01_law/).

---

## 1. System Charter & Executive Summary

**Vanguard / AETHER** is a Python-first, domain-blind recursive-agency substrate designed for autonomous systems with mathematical safety, cryptographically verifiable provenance, and fail-closed capabilities.

- **As-Built Core (`v0.6.1 Foundation`)**: A verified 13-stage reference monitor (TCB $\le 1438$ LOC, currently 1365 LOC), single-writer SQLite WAL event stream (`State = fold(events)`), rootless Bubblewrap sandbox (UID `10001`), and exterior Ed25519-signed evaluator daemon (UID `10002`).
- **Target Substrate**: A universal recursive agency substrate that compiles declarative manifests into Named Component Graphs, mediates attenuated subagent spawning, and harvests unforgeable execution trajectories for active inference and meta-cognitive self-improvement.

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
- **`B` — Bundle (`AS_BUILT`, GENERIC GRAPH QUEUED M-3)**: Manifest, resolved components, ceilings, policies, prompts, and routes freeze into an attributable `FrozenHarness`; ADR-0077 replaces coding-shaped slots with a Named Component Graph in M-3.
- **`C` — Corpus (`CONTRACT BUILT, CONTENT REPAIR ACTIVE M-2`)**: SQLite-WAL events and `mhf.trajectory/1` form the state/evidence corpus; RF-23 is still red for rich per-turn economics, route identity, and execution binding.
- **`D` — Digests (`D_H AS_BUILT; D_R COMPLETION ACTIVE M-2; D_X EXPERIMENT-BOUND`)**: Composition, execution, and experiment identities remain distinct: $D_H \ne D_R \ne D_X$.

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
