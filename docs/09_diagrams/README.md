---
id: diagrams-archive-index
class: archive
authority: advisory
canonical_for: []
status: frozen
owner: documentation-architect
version: "0.6.1"
last_verified: 2026-08-23
read_when:
  - inspecting-historical-diagrams
do_not_read_when:
  - implementing-runtime-behavior
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Architecture & Epistemic Diagrams

> **NON-NORMATIVE / FROZEN PROVENANCE**
>
> This directory preserves visual design history. Its diagrams cannot authorize implementation;
> current behavior and work must be traced to SPEC/annex law, accepted ADRs, and the active board.
> Biological, cosmological, and tier-of-being labels below are preserved rejected metaphors, not
> components, authority boundaries, implementation requirements, or capability claims.

This directory contains master vector blueprints illustrating the AETHER / Vanguard substrate architecture, epistemological boundaries, capability microkernel dispatch, and long-horizon evolution.

---

## 1. Three Planes & Kernel Dispatch Pipeline
**File:** [`01_three_planes_and_kernel_dispatch.svg`](01_three_planes_and_kernel_dispatch.svg)

Illustrates:
- **Decision Plane (Volatile):** Models, Planners, Context Engineering, and $D_H$ Composition Identity.
- **Microkernel Reference Monitor (S0–S12):** 13-stage dispatch pipeline, monotonic attenuation, four additive resource reservations plus structural depth/turn ceilings, and rootless bubblewrap sandboxing (UID 10001).
- **State Plane (Immutable):** Single-writer SQLite Write-Ahead Log (WAL), pure deterministic state reduction (zero I/O, zero clocks, zero randomness), and $D_R$ runtime Merkle DAG identity.
- **Evidence Plane (Exterior):** Isolated Exterior Evaluator daemon (UID 10002) emitting Ed25519-signed verdicts bound to oracle hashes and task nonces.

---

## 2. The 14-Tier Cosmological & Cognitive Continuum
**File:** [`02_fourteen_tier_continuum.svg`](02_fourteen_tier_continuum.svg)

Maps machine intelligence from physical bitstreams to self-sustaining cognitive cosmos across 14 discrete tiers:
- **Micro-Physics (Tiers 00–05):** Turing substrate, Unix Domain Sockets, SHA-256 digests, Identity/Ledger/Budget particles, Mediated Verbs, and the Capability Microkernel.
- **Meso-Biology (Tiers 06–09):** Manifest DNA, AST Context Enzymes, Cellular Sandboxes, Organ Systems, and the Sovereign Agent Persona.
- **Macro-Cosm (Tiers 10–13):** Stigmergic Swarms (Dynamic Hats), Distributed Knowledge Societies, Multi-Domain Biomes (Code, Math, Science, Security), and the Universal Autonomous Cosmos.

---

## 3. Substrate Evolution: v0.6.0 Concept Lock vs. v0.6.1 Generality & Beyond
**File:** [`03_v060_vs_v061_evolution_and_spawn.svg`](03_v060_vs_v061_evolution_and_spawn.svg)

Comparative blueprint detailing:
- **v0.6.0 Foundation Law:** Linear `EpisodeEngine` turn loop, fixed `harness.yaml` pack, rigid exterior verification, and the Foundation Stop Condition (Wave 4: 1 real verified coding run).
- **v0.6.1 Substrate Generality:** Component Graph manifest, Absent-vs-Forged guardrail flexibility, capability-mediated `agent.spawn` DAG delegation, and the Post-Foundation Macro-Roadmap (M-5 through M-10).

---

## 4. Closed-Loop Empirical Distillation & Self-Evolution
**File:** [`04_closed_loop_self_evolution_dpo.svg`](04_closed_loop_self_evolution_dpo.svg)

Illustrates the self-improving cognitive loop:
- **Step 1:** Live execution generating tamper-evident trajectories ($	au$).
- **Step 2:** Independent exterior oracle signing binary verdicts $Y(	au) \in \{0, 1\}$.
- **Step 3:** DPO preference pair extraction $(	au_{	ext{chosen}}, 	au_{	ext{rejected}})$ and skill card procedural synthesis (`skills/*.md`).
- **Step 4:** Offline LoRA/SFT fine-tuning of local 7B/14B models, gated on paired McNemar statistical hypothesis testing ($\chi^2 \ge 3.841, p < 0.05$).
- **Feedback Acceleration:** Immediate procedural memory reuse + sub-100ms local model reflex replacing expensive frontier calls.

---

## 5. Unified Agentic Workflow & Metamorphic Runtime Substrate
**File:** [`05_unified_agentic_workflow_and_metamorphic_runtime.svg`](05_unified_agentic_workflow_and_metamorphic_runtime.svg)

End-to-end operational blueprint uniting:
- **Command & Decision Plane:** Dual-mode interactive CLI (`vg`) / autonomous driver, L1–L5 hierarchical context compiler, unprivileged LLM proposal engine, universal `EpisodeEngine` turn loop, and M-6.5 adaptive strategy meta-controller.
- **TCB Capability Kernel (S0–S12):** Strict reference monitor ($\le 1438$ LOC), dynamic classification, monotonic capability attenuation, four additive resource reservations plus structural ceilings, guarded execution with durable intent (`EffectStarted`), and Ed25519 descriptor-bound human approval governance.
- **Adapters & Execution Sandbox:** Rootless bubblewrap sandbox (UID 10001) with user/PID/mount isolation, domain-blind port adapters, and recursive `agent.spawn` nested execution lineages.
- **State & Evidence Planes:** Single-writer SQLite WAL append-only causal stream, deterministic `AgentView` event fold (zero in-memory persistent agent state), content-addressed blob store, exterior evaluator daemon (UID 10002) with Ed25519-signed binary verdicts $Y(\tau) \in \{0, 1\}$, and trajectory dataset synthesis for closed-loop DPO and skill promotion.
