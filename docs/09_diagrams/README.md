# Architecture & Epistemic Diagrams

> **NON-NORMATIVE / FROZEN PROVENANCE**
>
> This directory preserves visual design history. Its diagrams cannot authorize implementation;
> current behavior and work must be traced to SPEC/annex law, accepted ADRs, and the active board.

This directory contains master vector blueprints illustrating the AETHER / Vanguard substrate architecture, epistemological boundaries, capability microkernel dispatch, and long-horizon evolution.

---

## 1. Three Planes & Kernel Dispatch Pipeline
**File:** [`01_three_planes_and_kernel_dispatch.svg`](01_three_planes_and_kernel_dispatch.svg)

Illustrates:
- **Decision Plane (Volatile):** Models, Planners, Context Engineering, and $D_H$ Composition Identity.
- **Microkernel Reference Monitor (S0–S12):** 13-stage dispatch pipeline, monotonic attenuation, 6D economic tensor reservations, and rootless bubblewrap sandboxing (UID 10001).
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
