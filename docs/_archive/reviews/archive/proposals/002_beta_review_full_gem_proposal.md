# Vanguard / AETHER — Executive Review & Phased Technical Proposal
## From Substrate to Meta-Framework: Harness & Loop Engineering for General Task-Solving Swarms

**Document Identity:** `002_beta_review_full_gem_proposal.md`  
**Classification:** Definitive Tier S+ SOTA Architectural Mandate, Meta-Framework Specification & Multi-Paradigm Synthesis  
**Governing Body:** The Leadership 7 (Engineering Director, CTO, CIO, Principal Staff Engineer, Principal Systems Architect, Tech Lead, PhD AI Specialist)  
**Date:** 2026-08-21  
**Baseline Anchor:** `main` @ `afa8e2a` (verified against live code tree)  
**Authority Context:** Companion to [`docs/00_overview/SYSTEM_OVERVIEW.md`](../../../../docs/00_overview/SYSTEM_OVERVIEW.md). Serves as the authoritative master blueprint for proposed append-only ADRs (`0077`–`0082`), milestone execution from **v0.6.1** through **v1.0.0**, and zero-guesswork developer specifications.

---

## Table of Contents

1. [Executive Summary & Leadership 7 Consensus](#1-executive-summary--leadership-7-consensus)
2. [Strategic Vision: From Substrate to General Swarm Meta-Framework](#2-strategic-vision-from-substrate-to-general-swarm-meta-framework)
3. [Adjudication of Open Architectural Tensions (T-1 through T-9)](#3-adjudication-of-open-architectural-tensions-t-1-through-t-9)
4. [Proposed Append-Only ADR Catalog (ADRs 0077–0082)](#4-proposed-append-only-adr-catalog-adrs-00770082)
5. [Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0)](#5-phased-milestone-roadmap--version-ladder-v061--v100)
6. [Active Inference, Trajectory Science & The Compounding Flywheel](#6-active-inference-trajectory-science--the-compounding-flywheel)
7. [Zero-Guesswork Developer Implementation Bridge](#7-zero-guesswork-developer-implementation-bridge)
8. [Repository Hygiene, Stale Debt Pruning & Linter Hardening](#8-repository-hygiene-stale-debt-pruning--linter-hardening)
9. [Document Update Cascade & Transition Plan](#9-document-update-cascade--transition-plan)
10. [The Four Foundational Proofs & Leadership Sign-Off Mandate](#10-the-four-foundational-proofs--leadership-sign-off-mandate)
11. [Alternative Architectural Approach: The Adaptive Informational Harness & Pareto-Dynamic General Solver Framework](#11-alternative-architectural-approach-the-adaptive-informational-harness--pareto-dynamic-general-solver-framework)

---

## 1. Executive Summary & Leadership 7 Consensus

### 1.1 The Product Vision — Stated Once, Governing Everything Below

> **AETHER is an unforgeable, domain-blind operating substrate for building bounded autonomous task solvers — proven first on software engineering, and architected to evolve into a meta-framework for harness and loop engineering of general task-solving swarms.**

Translated into five falsifiable engineering claims:
1. **Unforgeable:** No execution grades itself. Every capability claim traces to an exterior, Ed25519-signed, request-bound verdict (UID 10002) that the agent cannot inspect, patch, or influence.
2. **Domain-Blind:** A new domain (Math, Data Science, Deductive Systems, Research) arrives as data (manifest + plugins + oracles) with **zero diffs** under `domain/` or `kernel/`.
3. **Bounded Solvers:** Agents execute under monotonic capability attenuation and typed 6D leases; delegation never widens authority or budget.
4. **Proven on Software Engineering:** The first domain pack (`code-default`) serves as the empirical stress-test of the kernel against compilers, test suites, and git diffs.
5. **Self-Improving Ecologies:** The substrate harvests rich, signed trajectories into skills and DPO preference pairs, improving *only* through a human-gated, partial-order promotion frontier it cannot manipulate.

The **meta-framework destiny** dictates that AETHER does not ship a single hardcoded agent. It ships the **composition engine, execution waist, and verification pipeline** that compiles declarative manifests into arbitrary task-solving agent topologies (debate, tree search, reflection, and stigmergic swarms).

### 1.2 Leadership 7 Consensus Matrix

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       LEADERSHIP 7 CONSENSUS MATRIX                                      │
├────────────────────────────────┬───────────────────────────────────────┬─────────────────────────────────┤
│ Role                           │ Core Focus & Jurisdiction             │ Key Determination & Mandate     │
├────────────────────────────────┼───────────────────────────────────────┼─────────────────────────────────┤
│ 1. Engineering Director        │ Authority, Governance & Stop Lines    │ Enforce M-4 Foundation Stop;    │
│                                │                                       │ ratify v0.6.1–v0.7.0 release.   │
├────────────────────────────────┼───────────────────────────────────────┼─────────────────────────────────┤
│ 2. Chief Technology Officer    │ Moat, SOTA Alignment & Macro Strategy │ Authorize Component Graph;      │
│                                │                                       │ preserve 3-Plane separability.  │
├────────────────────────────────┼───────────────────────────────────────┼─────────────────────────────────┤
│ 3. Chief Information Officer   │ Auditability, Traceability & Security │ Strict cryptographic trinity;   │
│                                │                                       │ zero unlogged side effects.     │
├────────────────────────────────┼───────────────────────────────────────┼─────────────────────────────────┤
│ 4. Principal Staff Engineer    │ Gap Register & Substrate Generality   │ Rebalance Wave 3 falsifiers;    │
│                                │                                       │ eliminate hollow trajectories.  │
├────────────────────────────────┼───────────────────────────────────────┼─────────────────────────────────┤
│ 5. Principal Systems Architect │ Boundary Lattice & TCB Invariants     │ Maintain TCB ≤ 1438 LOC;        │
│                                │                                       │ isolate S0–S12 dispatch core.   │
├────────────────────────────────┼───────────────────────────────────────┼─────────────────────────────────┤
│ 6. Tech Lead                   │ Sprint Execution & Dev Bridge         │ Provide zero-guesswork schemas, │
│                                │                                       │ FSMs, and falsifier matrices.   │
├────────────────────────────────┼───────────────────────────────────────┼─────────────────────────────────┤
│ 7. PhD AI Specialist           │ Trajectory Science & Active Inference │ Un-hollow NOVA-1 cost vectors;  │
│                                │                                       │ prime M-10 RL & skill harvest.  │
└────────────────────────────────┴───────────────────────────────────────┴─────────────────────────────────┘
```

### 1.3 The Twelve Binding Executive Rulings

| # | Ruling | Owner | Strategic Disposition |
|---|---|---|---|
| **R-1** | **Swarm Destination via Substrate Path:** Swarms are spawn-topologies + policy over the State Plane—never a new engine, never $O(N^2)$ chatter. | CTO | Strategic |
| **R-2** | **Sacred M-4 Foundation Stop Line:** No meta-cognition, swarm features, or kernel changes before 9 verified rows on one uncheated real run. | Engineering Director | Non-negotiable |
| **R-3** | **Immediate NOVA-1 Trajectory Un-Hollowing:** Per-turn cost accounting, latency, and model fingerprinting execute in Wave 2. | Tech Lead + Principal Staff | Immediate |
| **R-4** | **Named Component Graph Manifest (`mhf.manifest/2`):** Manifest evolves into a typed graph; slots degrade to pack convention. | Engineering Director | Wave 3 Implementation |
| **R-5** | **Absent-vs-Forged Security Model:** You may declare guardrails off (`evaluation: none`); you can never forge a verdict. | CIO + Systems Architect | Law-Level |
| **R-6** | **Capability-Mediated `agent.spawn`:** Designed now (`ADR-0080`), implemented in kernel at Milestone M-6 only. | Systems Architect | Strict Sequencing |
| **R-7** | **Layer-0 Absorption & Deletion:** Registry FSM and Compose compiler absorbed into `runtime/`; `layer0/` deleted behind NOVA-4 suite. | Principal Staff | Wave 3 Exit Gate |
| **R-8** | **Universal Turn Loop Claim Published:** Mechanism claim published with bound falsifier (`RF-082`); no metaphysics. | PhD AI Specialist | Law-Level |
| **R-9** | **NOVA-2 Cold Replay Concurrency Proof:** Suspend/resume from SQLite WAL executed in Wave 2 to prove concurrency is a scheduler refactor. | Tech Lead | Immediate |
| **R-10**| **Pack #2 Gate (Math & Deductive Systems):** Proves domain blindness (Invariant I-7) at M-5 with **zero diffs** under `domain/` and `kernel/`. | Principal Staff | Milestone M-5 Gate |
| **R-11**| **Clean Documentation Triad Consolidation:** Collapse 7 governance tiers into the Clean Triad post-M-4. | Engineering Director | Post-M-4 |
| **R-12**| **Corpus-First, McNemar-Gated Learning Layer:** Active Inference (VFE/EFE) and DPO skill harvesting operate exclusively on signed evidence. | PhD AI Specialist | Milestone M-10 |

### 1.4 Three Critical Forensic Codebase Findings (Resolved)

1. **Plugin Lifecycle FSM Event Parity:** `layer0/registry/lifecycle.py` currently maps only 5 of 7 states to events (`DISCOVERED` and `VERIFIED` emit nothing). This document formally authorizes adding `PluginDiscovered` and `PluginVerified` to the closed event catalog to make the M-3 exit gate mathematically satisfiable.
2. **Manifest Dual-Dialect Convergence:** `domain/artifacts/manifest.py` already types `components` as a named component tuple `tuple[tuple[str, tuple[str, ...]], ...]`, while `schemas/mhf/harness_manifest.schema.json` freezes 5 slots. Evolving to `mhf.manifest/2` is a mechanical convergence of existing parsers, not an ungrounded rewrite.
3. **Falsifier Identifier Namespace Disambiguation:** Resolves the identifier collision between kernel controls in `KERNEL.md` (`F-01`–`F-25`) and sprint register falsifiers by formally designating register falsifiers as `RF-01`–`RF-25`.

---

## 2. Strategic Vision: From Substrate to General Swarm Meta-Framework

### 2.1 2026 SOTA Competitive & Theoretical Landscape

A comprehensive survey of frontier agentic engineering confirms that AETHER's architectural foundations solve the primary failure modes of contemporary agent systems:

```text
┌───────────────────────────────────────────────────┬───────────────────────────────────────────────────┐
│            MONOLITHIC / FRAGILE PATTERNS          │              AETHER / VANGUARD SOLUTION           │
├───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
│ 1. Conflation of Authority, State & Evidence      │ 1. Tripartite Plane Separation                    │
│    (Agent acts as its own judge and historian)    │    (Strict separation: Decision / State / Evidence)│
├───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
│ 2. Unbounded Context & Memory Rot                 │ 2. Homeostatic Bounds & Structured Compaction     │
│    (Infinite token accumulation degrades logic)   │    (Prefix-stable L1–L5 context layers)           │
├───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
│ 3. Epistemic Solipsism (Self-Judging Fallacy)     │ 3. Socratic Falsification & Exterior Oracles      │
│    (Agent claims success without ground truth)    │    (Ed25519-signed exterior judge outside worker) │
├───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
│ 4. Catastrophic Amnesia Across Lifecycles         │ 4. Trajectory Harvesting & Procedural Skills      │
│    (Identical failures repeated across sessions)  │    (Un-hollowed trajectories feed DPO & skills)   │
├───────────────────────────────────────────────────┼───────────────────────────────────────────────────┤
│ 5. Quadratic Communication Explosion              │ 5. Stigmergic Swarms & Blackboard Architecture    │
│    (O(N^2) natural language chatter in swarms)    │    (Coordination via shared State Plane / Ledger) │
└───────────────────────────────────────────────────┴───────────────────────────────────────────────────┘
```

### 2.2 The Swarm Paradigm: Stigmergy Over Conversational Chatter

Most multi-agent frameworks fail when scaling beyond 4 agents because agents communicate via unconstrained natural-language messages ($\mathcal{O}(N^2)$ chatter), rapidly exhausting context windows with social coordination noise.

AETHER implements **Stigmergic Coordination**:
- Agents coordinate **indirectly** through modifications to the shared **State Plane** (the workspace filesystem and SQLite WAL ledger).
- *Agent A (Architect/Decomposer)* creates a structured specification file or sub-task reservation.
- *Agent B (Worker/Coder)* observes the state change via its context manager, acquires a capability-attenuated lease, and applies modifications.
- *Agent C (Critic/Auditor)* triggers an exterior signed evaluation against the modified workspace.
- Communication overhead remains $\mathcal{O}(N)$, context windows remain pristine, and execution provenance is cryptographically recorded in the event ledger.

### 2.3 The A-B-C-D Operating Foundation

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       THE A-B-C-D OPERATING FOUNDATION                                   │
├───────────────────┬──────────────────────────────────────────────────────────────┬───────────────────────┤
│ Pillar            │ Mechanism & Responsibility                                   │ Status & Trajectory   │
├───────────────────┼──────────────────────────────────────────────────────────────┼───────────────────────┤
│ A — Authority     │ S0–S12 Reference Monitor, descriptor-bound grants,           │ Solid & Generic       │
│                   │ monotonic attenuation, typed 6D budgets (TCB ≤ 1438 LOC).    │ (1365 logical LOC)    │
├───────────────────┼──────────────────────────────────────────────────────────────┼───────────────────────┤
│ B — Bundle        │ Manifest → compose() → FrozenHarness(D_H).                   │ Evolving to Named     │
│                   │ The composition surface defining agent & swarm topology.     │ Component Graph (M-3) │
├───────────────────┼──────────────────────────────────────────────────────────────┼───────────────────────┤
│ C — Corpus        │ SQLite WAL fold(events) → mhf.trajectory/1 at completion.    │ Un-hollowing via      │
│                   │ The unforgeable training dataset for downstream RL & skills. │ NOVA-1 in Wave 2      │
├───────────────────┼──────────────────────────────────────────────────────────────┼───────────────────────┤
│ D — Digest        │ Cryptographic identity trinity: D_H ≠ D_R ≠ D_X via JCS.     │ Locked & Generic      │
│                   │ Uncollapsible measurement denominators for all A/B testing.  │ (RFC 8785 standard)   │
└───────────────────┴──────────────────────────────────────────────────────────────┴───────────────────────┘
```

---

## 3. Adjudication of Open Architectural Tensions (T-1 through T-9)

Each open tension from [`SYSTEM_OVERVIEW.md`](../../../../docs/00_overview/SYSTEM_OVERVIEW.md) is resolved below with an executive determination, disposition label, and governing ADR reference:

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    EXECUTIVE ADJUDICATION REGISTER                                       │
├─────┬───────────────────────────────┬───────────────────────────────┬─────────────────┬──────────────────┤
│ ID  │ Tension Description           │ Executive Determination       │ Disposition     │ Governing ADR    │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-1 │ Manifest: Fixed Slots vs.     │ Adopt Named Component Graph;  │ GENERALIZE NOW  │ ADR-0077         │
│     │ Named Component Graph         │ slot names = pack convention. │ (Wave 3)        │                  │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-2 │ Trajectory Quality: Hollow    │ Execute NOVA-1 immediately in │ STRENGTHEN NOW  │ ADR-0078         │
│     │ Corpus (ZERO_COST)            │ Wave 2; populate cost & model.│ (Wave 2)        │                  │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-3 │ Guardrails: Mandatory vs.     │ Adopt Absent-vs-Forged rule;  │ GENERALIZE NOW  │ ADR-0079         │
│     │ Absent-vs-Forged Model        │ unsigned verdicts always deny.│ (Wave 3)        │                  │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-4 │ Spawning: Engine-Owned vs.    │ Expose agent.spawn as verb;   │ DESIGN Wave 3   │ ADR-0080         │
│     │ Capability-Mediated Verb      │ implement in kernel post-M-4. │ IMPLEMENT M-6   │                  │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-5 │ Layer-0 Absorption Timeline   │ Absorb FSM into runtime in    │ ABSORB & DELETE │ ADR-0081         │
│     │ and Fork Deletion             │ 3.1; delete layer0/ at M-3.   │ (Wave 3)        │                  │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-6 │ Turn Loop as Mechanism vs.    │ Publish formal falsifier:     │ KEEP & DOCUMENT │ ADR-0082         │
│     │ Pluggable Loop Engine         │ 3 algorithms over 1 loop.     │ (Wave 3)        │                  │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-7 │ K ≪ N Concurrency Proof       │ Execute NOVA-2 suspend/resume │ STRENGTHEN NOW  │ Extends ADR-0074 │
│     │ (Cold Reconstruct from WAL)   │ falsifier in Wave 2.          │ (Wave 2)        │                  │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-8 │ Governance Corpus Mass        │ Collapse 7 tiers to Clean     │ SIMPLIFY        │ Scheduled M-5    │
│     │ (3.4k lines across 7 tiers)   │ Triad (SPEC + ADR + 1 board). │ (Post-M-4)      │                  │
├─────┼───────────────────────────────┼───────────────────────────────┼─────────────────┼──────────────────┤
│ T-9 │ Five-SPI Freeze Revisit       │ Maintain freeze in v0.6;      │ REVISIT         │ Scheduled M-9    │
│     │ against Mature Component Graph│ revisit after M-8 validation. │ (Post-M-8)      │                  │
└─────┴───────────────────────────────┴───────────────────────────────┴─────────────────┴──────────────────┘
```

### 3.1 Detailed Adjudication Highlights

- **T-1 (Named Component Graph):** Allows declaring $N$ planners, $M$ evaluators, and arbitrary toolkits with explicit bindings. This enables critic-reviser loops, multi-agent debate, and tree search without writing a single line of engine code. Slot names (`main`, `evaluator`) survive purely as pack conventions.
- **T-2 (Trajectory Un-Hollowing / NOVA-1):** Moving NOVA-1 to **immediate Wave 2 execution** is the highest-leverage decision on the board. Every run between now and Wave 4 that executes with `_ZERO_COST` permanently degrades the training corpus.
- **T-3 (Absent-vs-Forged Guardrails):** "You may turn a guardrail off; you may never turn off the record that it was off." Non-coding packs may declare `evaluation: { mode: "none" }`. The trajectory is marked `attributable_for_promotion: false`, but the execution proceeds cleanly. Unsigned verdicts remain categorically illegal under all configurations.
- **T-4 (`agent.spawn` as Capability Verb):** Planners will be able to request sub-agent spawns via standard `EffectRequest(verb="agent.spawn")` subject to S0–S12 authorization and monotonic capability attenuation. Design lands in Wave 3; kernel code lands in M-6.
- **T-6 (Universal Turn Loop Falsifier):** Publishes the explicit challenge: *"Name an agentic algorithm that cannot be expressed as spawn-topology + planner policy over this loop."*
- **T-7 (NOVA-2 Suspend/Resume Proof):** An episode is suspended mid-turn, reconstructed from the SQLite WAL in a fresh process, and resumed to completion. Passing this proves concurrency is a scheduling refactor rather than an architectural rewrite.

---

## 4. Proposed Append-Only ADR Catalog (ADRs 0077–0082)

### ADR-0077: Named Component Graph Manifest Schema (`mhf.manifest/2`)

```text
Title:     Named Component Graph Manifest Schema
Status:    Proposed (Locks in v0.6.1 / Lands in Wave 3)
Applies:   SPEC.md §2.3, domain/artifacts/manifest.py, runtime/compose.py,
           schemas/mhf/harness_manifest.schema.json
Extends:   ADR-0005, ADR-0070

Context:
  The fixed 5-slot manifest prevents multi-agent topologies (debate, critic loops,
  tree search) from being declared without engine modification.

Decision:
  1. harness_manifest.schema.json defines a map of `components`:
     components:
       <name>:
         kind: planner | memory | toolkit | context | evaluation
         ref: <plugin_ref>
         model_route: <route_key>  # Optional per-component model routing
         config: { ... }
         ceiling: { verbs: [...], paths: [...] }
     bindings:
       primary_planner: <name>
       evaluators: [<name>]
       active_toolkits: [<name>]
       stigmergic_blackboard: <bool>
  2. D_H = JCS digest of the entire resolved component graph, model routes,
     prompt layers, and governance policies.
  3. Converges existing tuple parser in domain/artifacts/manifest.py with schema.

Falsifiers:
  RF-077-A: Multi-planner manifest (proposer + critic) compiles to valid FrozenHarness.
  RF-077-B: Any component name, config, or ceiling mutation produces distinct D_H.
  RF-077-C: code-default migrates mechanically with zero behavioral change.
```

### ADR-0078: Trajectory Un-Hollowing & Per-Turn Cost Accounting (NOVA-1)

```text
Title:     Trajectory Un-Hollowing and Model Fingerprinting (NOVA-1)
Status:    Proposed (Locks in v0.6.1 / Lands in Wave 2)
Applies:   runtime/trajectory.py, schemas/mhf/trajectory.schema.json
Extends:   ADR-0068, ADR-0074

Context:
  trajectory.py emits _ZERO_COST, violating I-9 and rendering the execution corpus
  useless for downstream RL/DPO/skill-synthesis — the meta-framework's learning engine.

Decision:
  1. Collect per-turn token usage (prompt, completion, cached), wall-clock latency,
     and model fingerprint digests from ModelResponse events.
  2. trajectory.py populates turns[i].cost and episode.cost from accumulated ledger.
  3. verdict is explicit null with attributable: false when no exterior verdict exists.

Falsifiers:
  RF-078: Completed episode with >0 generated tokens MUST emit trajectory with
  total_cost.tokens > 0 and populated model_fingerprint.
```

### ADR-0079: Absent-vs-Forged Guardrail Declarations

```text
Title:     Absent-vs-Forged Guardrail Declarations
Status:    Proposed (Locks in v0.6.1 / Lands in Wave 3)
Applies:   runtime/compose.py, runtime/evaluator_gateway.py, domain/artifacts/manifest.py
Extends:   ADR-0004, ADR-0029, ADR-M0-08

Context:
  The meta-framework must support non-coding compositions (math, research, data science)
  that do not require an exterior UID 10002 daemon.

Decision:
  1. Compositions may declare evaluation: { mode: "none" } or sandbox: { mode: "in_process" }.
  2. D_H encodes this; trajectories tagged attributable_for_promotion: false.
  3. Unsigned verdicts remain unconditionally rejected by EvaluatorGateway.
  4. Seven permanent non-negotiables are the fixed substrate boundary.

Falsifiers:
  RF-079-A: evaluation: none initializes without spawning UID 10002 daemon.
  RF-079-B: Synthetic VerdictRecorded injected into evaluation: none is rejected.
  RF-079-C: Trajectory from evaluation: none run carries attributable: false.
```

### ADR-0080: Capability-Mediated `agent.spawn` Architecture

```text
Title:     Capability-Mediated agent.spawn — Design and Deferred Implementation
Status:    Proposed (Design in Wave 3 / Implementation Deferred to M-6)
Applies:   kernel/dispatch.py, agency/episode/engine.py, ports/spi.py
Extends:   ADR-0011, ADR-0012, ADR-0070

Context:
  Swarm and recursive delegation patterns require planners to spawn child agents
  as mediated effects, not engine-internal calls.

Decision:
  1. agent.spawn is a standard capability verb dispatched through S0–S12.
  2. Planners emit EffectRequest with verb agent.spawn only if ceiling permits.
  3. Child capabilities and budgets are strictly monotonic sub-allocations of parent.
  4. Implementation deferred to M-6; no kernel changes before Wave 4 closes.

Falsifiers:
  RF-080-A: Planner without agent.spawn grant receives AuthorizationDenied at S5.
  RF-080-B: Child agent capabilities are verified as strict subset of parent grant.
```

### ADR-0081: Layer-0 Final Absorption and Deletion Sequence

```text
Title:     Layer-0 Final Absorption and Deletion Sequence
Status:    Proposed (Lands in Wave 3)
Applies:   layer0/, vanguard/packages/runtime/registry/
Extends:   ADR-0069, ADR-0076

Decision:
  1. Port plugin lifecycle FSM and registry validation into runtime/registry/.
  2. Add PluginDiscovered and PluginVerified events to closed event catalog.
  3. Implement NOVA-4 negative lifecycle test suite in test/contracts/.
  4. Remove layer0/ completely at M-3 exit gate.

Falsifiers:
  RF-081-A: Zero occurrences of layer0 across codebase after Sprint 3.1.
  RF-081-B: Plugin lifecycle FSM emits verified ledger events on all 7 transitions.
```

### ADR-0082: Universal Turn Loop as Mechanism (Published Falsifier)

```text
Title:     Universal Turn Loop as Mechanism — Published Falsifier
Status:    Proposed (Locks in v0.6.1 / Documented in Wave 3)
Applies:   agency/episode/engine.py, SPEC.md §3
Extends:   ADR-0003, ADR-0070

Context:
  The meta-framework's expressiveness thesis is that ALL agentic algorithms are
  expressible as spawn-topology + planner-policy over a single turn loop
  (observe → propose → authorize → effect → receipt → evaluate → reflect*).

Decision:
  1. The turn loop is mechanism, never plugin.
  2. The published falsifier: "Name an agentic algorithm that cannot be expressed
     as spawn-topology + planner policy over this loop."

Falsifiers:
  RF-082-A: At least 3 distinct agentic algorithms (ReAct, tree-search, critic-loop)
           demonstrated as spawn-topology + planner-policy, zero engine changes.
```

---

## 5. Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0)

### 5.1 Foundation Phase Releases (v0.6.1 – v0.7.0)

#### Release v0.6.1: Substrate Correction Lock & Wave 2 Completion
- **Goals:** Close Wave 2 convergence; fix trajectory cost un-hollowing (NOVA-1); implement cold suspend/resume falsifier (NOVA-2); complete `root.py` split.
- **Entry Gate:** Wave 1 green on disk; ADRs `0077`–`0082` accepted.
- **Key Deliverables:**
  1. Ingest real per-turn token usage, latency, and model fingerprint in `runtime/trajectory.py`.
  2. Implement `test_cold_suspend_resume` in `test/contracts/` (NOVA-2).
  3. Verify clean split: `root.py` (126 LOC) → `compose.py`, `session.py`, `wiring.py`.
  4. Fix `_PROC_PATTERN` to read from compiled ceiling rather than literal string (NOVA-3).
- **Exit Gate:** `check_boundaries.py` 100% green; TCB budget ≤ 1438 logical LOC; `RF-04` passes with non-zero cost vectors; zero `layer0` imports; NOVA-2 green.

#### Release v0.6.2: Wave 3 Extensibility Lock & Component Graph
- **Goals:** Absorb plugin lifecycle into `runtime/registry/`; implement Named Component Graph in `compose.py`; delete `layer0/`; verify echo plugin lifecycle over UDS.
- **Entry Gate:** v0.6.1 signed off.
- **Key Deliverables:**
  1. Named Component Graph parser in `runtime/compose.py` (`mhf.manifest/2`).
  2. Plugin FSM (`DISCOVERED` → `ACTIVATED` → `RETIRED`) with ledgered transitions.
  3. NOVA-4 negative lifecycle test suite (6 falsifiers).
  4. `packs/code-default/harness.yaml` migrated mechanically to graph syntax.
  5. Absent-vs-forged guardrail schema accepted.
  6. `agent.spawn` design note and test sketches completed.
- **Exit Gate:** Echo plugin walks full lifecycle over UDS; `layer0/` deleted; domain blindness linter passes on widened surface.

#### Release v0.6.3: Pre-M4 Hardening & Conformance
- **Goals:** Lock golden test cassettes, isolate rootless bwrap sandbox execution, and verify end-to-end evaluator daemon RPCs.
- **Entry Gate:** v0.6.2 green.
- **Key Deliverables:**
  1. UID 10001 (worker) and UID 10002 (evaluator) process isolation verified.
  2. Ed25519 signature verification on all pre-registered evaluation suites.
  3. Deterministic cassette mocks for regression testing.
  4. Universal turn loop falsifier (`RF-16`) validated with 3 distinct topologies.
- **Exit Gate:** 100% test pass rate across all collected tests; all 15 linters green.

#### Release v0.7.0: Milestone M-4 Foundation Stop Line ███
- **Goals:** Execute the single real-world, uncheated, end-to-end autonomous coding run.
- **Entry Gate:** v0.6.3 green.
- **Mandatory 9-Row Verification Matrix (One Uninterrupted Run):**
  1. Real frontier model via OpenRouter/Ollama.
  2. Authorized filesystem effect via S0–S12 Reference Monitor.
  3. Real workspace file mutation on disk.
  4. Execution within rootless bubblewrap sandbox (UID 10001).
  5. Exterior Ed25519-signed verdict from daemon (UID 10002).
  6. Complete event sequence recorded in SQLite WAL ledger.
  7. Cold replay in fresh process matches live state exactly.
  8. Trajectory emitted with non-zero costs and valid model fingerprint (NOVA-5).
  9. Execution performed on unified `vanguard/packages/` runtime.
- **Exit Gate: STOP LINE.** No further code development until the Director formally signs off on the M-4 Evidence Report.

---

### 5.2 Post-Foundation: Generality Phase (v0.8.0)

**Milestone M-5: Generality Proof & Doc Consolidation**
- **Outcome 1:** Implement Pack #2 — **Math & Theorem Proving / Deductive Systems** (SymPy / Datalog engine / Lean-style formal verifier). Verify **ZERO diffs** under `domain/` and `kernel/`.
- **Outcome 2:** Collapse documentation corpus from 7 tiers into the Clean Triad (`SPEC.md` + `docs/05_adr/` + `sprint_active.md` + `schemas/`).
- **Gate:** Invariant I-7 (domain-blindness) proven as empirical fact; trajectory parity assertion verified (Pack #2 emits rich, valid `mhf.trajectory/1` rows).

---

### 5.3 Post-Foundation: Emergence & Swarm Phase (v0.9.0)

**Milestone M-6: Mediated Delegation (`agent.spawn`)**
- **Outcome:** Implement `agent.spawn` as capability verb in S0–S12. Planners spawn sub-agents.
- **Gate:** Planner without grant cannot delegate; child stays attenuated; spawn is a ledgered, budgeted, receipted effect.
- **Validation:** Reference compositions: hierarchical decomposition + tree search.

**Milestone M-7: Controlled Concurrency & Stigmergic Swarms**
- **Outcome:** Parallel execution for disjoint resource selectors; $K \ll N$ agent/worker pool separation; stigmergic blackboard coordination over SQLite WAL.
- **Gate:** Selector soundness verified; zero event loss under backpressure; Invariant I-11 lifted on measurement data.

**Milestone M-8: Framework Builder Abstraction**
- **Outcome:** Declaratively compose debate (proposer + critic + aggregator), evolutionary search, and multi-agent delegation over the Component Graph.
- **Gate:** Multiple diverse agent topologies execute simultaneously without engine changes; Pack #1, Pack #2, and Pack #3 execute side-by-side on one runtime.

---

### 5.4 Meta-Cognitive Phase (v1.0.0)

**Milestone M-9: Scaled Orchestration & High Performance**
- **Outcome:** Optimize IPC and SQLite WAL throughput; benchmark 100+ concurrent logical agents over a bounded worker pool; revisit 5-SPI freeze against mature Component Graph.
- **Gate:** Sub-millisecond reference monitor overhead; bounded memory footprint.

**Milestone M-10: Meta-Cognitive Substrate (FINAL)**
- **Outcome:** Outer-loop reflective planner at the `outer` slot, capability-restricted to manifest-mutation, skill-write, and oracle-preregistration (never workspace). Harvests signed trajectories → compiles deterministic macro-tools + DPO pairs → paired McNemar vs. undeletable baseline → signed promotion pointer → cassette-replay regression → human promotion gate.
- **Gate:** System proposes, tests, and promotes an improved version of its own composition with the entire chain attributable via $D_H / D_R / D_X$ and signed verdicts, on a corpus whose evidence was never forgeable.

---

## 6. Active Inference, Trajectory Science & The Compounding Flywheel

### 6.1 Mathematical Formulation of Active Inference

Based on [`docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS.md`](../../../../docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS.md), AETHER models self-improvement and dynamic policy routing using exact Free Energy Principles bounded by the 6D economic reservation tensor $\mathbf{R}$:

$$\theta^* = \arg\min_{\theta \in \Theta} \mathcal{F}(\theta) \quad \text{subject to} \quad \text{Cost}(\theta) \le \mathbf{R}_{\max}$$

#### 1. Variational Free Energy ($\mathcal{F}$ — Posterior State & Context Compression):
$$\mathcal{F}(q, \mathcal{W}) = \mathbb{E}_q\left[\ln q(\mathbf{s}) - \ln p(\mathbf{s}, \mathbf{o})\right] = D_{\text{KL}}\big[ q(\mathbf{s}) \parallel p(\mathbf{s} \mid \mathbf{o}) \big] - \ln p(\mathbf{o})$$
*Compresses global blackboard state $\mathcal{W}$ into minimal observation context $\mathbf{o}$ by minimizing epistemic surprise.*

#### 2. Expected Free Energy ($\mathcal{G}$ — Policy & Swarm Action Selection):
$$\mathcal{G}(\pi) = -\underbrace{\mathbb{E}_{\tilde{q}}\left[\ln p(\mathbf{o}_\tau \mid \text{Goal})\right]}_{\text{Extrinsic Value (Goal Utility / Pass Rate)}} - \underbrace{\mathbb{E}_{\tilde{q}}\left[\ln q(\mathbf{s}_\tau \mid \mathbf{o}_\tau, \pi) - \ln q(\mathbf{s}_\tau \mid \pi)\right]}_{\text{Epistemic Value (Information Gain / Uncertainty Reduction)}} + \lambda \sum_{d \in \{ \$, t, k \}} \frac{R_d(\pi)}{R_{\max, d}}$$

### 6.2 The Immutable Macro-Skill Tool Registry (Token Collapse Engine)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                         UN-GAMEABLE CONTINUOUS SELF-IMPROVEMENT LOOP                     │
│                                                                                          │
│  1. EXECUTION           Rich Trajectory emitted at EpisodeCompleted                      │
│     (Runtime)           (Per-turn tokens, latency, model fingerprint, signed verdict)    │
│                                           │                                              │
│                                           ▼                                              │
│  2. HARVEST             Harvester extracts verified n-grams & DPO preference pairs       │
│     (Offline)           (Chosen vs. Rejected conditioned strictly on Ed25519 verdict)    │
│                                           │                                              │
│                                           ▼                                              │
│  3. SYNTHESIS           Skill Synthesizer compiles AST deterministic macro-tools         │
│     (Agency)            (Collapses 20-turn 50k token loops into 1-turn 500 token tools)  │
│                                           │                                              │
│                                           ▼                                              │
│  4. LAB VALIDATION      Paired McNemar Exact Test vs. Non-Deletable Baseline             │
│     (MEASUREMENT.md)    (χ² ≥ 3.841, p < 0.05, N ≥ 50 on discordant pairs only)          │
│                                           │                                              │
│                                           ▼                                              │
│  5. PROMOTION           Signed Promotion Event flips default pointer in Registry         │
│     (Governance)        (New D_H digest; zero in-place mutation in production)           │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

Why this self-improvement loop **cannot be gamed by construction**:
1. **Unreachable Ground Truth:** Verdicts are signed by the exterior daemon (UID 10002); an agent cannot generate synthetic rewards.
2. **Uncollapsible Denominators:** $D_H \neq D_R \neq D_X$ ensures that prompt mutations or model route changes produce distinct measurement identities.
3. **Statistically Honest Promotion:** Annex [`MEASUREMENT.md`](../../../../docs/04_annex/MEASUREMENT.md) enforces McNemar's exact test over discordant pairs with Holm-Bonferroni correction, rejecting underpowered claims.
4. **Pointer Immutability:** Promotion never mutates running code in place; it registers a new $D_H$ in the manifest registry.

---

## 7. Zero-Guesswork Developer Implementation Bridge

### 7.1 Normative Wire Contracts (JSON Schema)

#### Named Component Graph Schema (`schemas/mhf/harness_manifest.schema.json`)
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MHF Named Component Graph Manifest v2",
  "type": "object",
  "required": ["schema_version", "name", "components", "bindings", "governance"],
  "properties": {
    "schema_version": { "type": "string", "enum": ["mhf.manifest/2"] },
    "name": { "type": "string" },
    "components": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["kind", "ref"],
        "properties": {
          "kind": { "type": "string", "enum": ["planner", "memory", "toolkit", "context", "evaluation"] },
          "ref": { "type": "string" },
          "model_route": { "type": "string" },
          "config": { "type": "object" },
          "ceiling": {
            "type": "object",
            "properties": {
              "verbs": { "type": "array", "items": { "type": "string" } },
              "paths": { "type": "array", "items": { "type": "string" } }
            }
          }
        }
      }
    },
    "bindings": {
      "type": "object",
      "required": ["primary_planner"],
      "properties": {
        "primary_planner": { "type": "string" },
        "evaluators": { "type": "array", "items": { "type": "string" } },
        "active_toolkits": { "type": "array", "items": { "type": "string" } },
        "stigmergic_blackboard": { "type": "boolean", "default": false }
      }
    },
    "governance": {
      "type": "object",
      "properties": {
        "evaluation": { "type": "object" },
        "sandbox": { "type": "object" },
        "approval_policy": { "type": "string" }
      }
    }
  }
}
```

---

### 7.2 Plugin Lifecycle State Machine (`runtime/registry/`)

```text
┌──────────────┐  resolve()  ┌──────────────┐  verify()  ┌──────────────┐
│  DISCOVERED  │ ──────────► │   RESOLVED   │ ────────► │   VERIFIED   │
└──────────────┘             └──────────────┘            └──────────────┘
                                                                │
                                                                │ activate()
                                                                ▼
┌──────────────┐  retire()   ┌──────────────┐  quiesce() ┌──────────────┐
│   RETIRED    │ ◄────────── │  QUIESCING   │ ◄──────── │  ACTIVATED   │
└──────────────┘             └──────────────┘            └──────────────┘
       ▲                                                        │
       └────────────────── fault() ─────────────────────────────┘
```

| Current State | Trigger | Next State | Ledger Event Emitted | Invariants & Pre-Conditions |
|---|---|---|---|---|
| `NONE` | `discover(manifest)` | `DISCOVERED` | `PluginDiscovered` | Manifest schema is valid. |
| `DISCOVERED` | `resolve(deps)` | `RESOLVED` | `PluginResolved` | All component refs exist on disk. |
| `RESOLVED` | `verify(sig/hash)` | `VERIFIED` | `PluginVerified` | Plugin integrity matches digest. |
| `VERIFIED` | `activate(ctx)` | `ACTIVATED` | `PluginActivated` | Sandbox isolation initialized. |
| `ACTIVATED` | `quiesce()` | `QUIESCING` | `PluginQuiescing` | No new effect dispatches accepted. |
| `QUIESCING` | `retire()` | `RETIRED` | `PluginRetired` | In-flight effects drained and logged. |
| `ACTIVATED` | `fault(err)` | `RETIRED` | `PluginFaulted` | Cell killed; cannot remain active. |

---

### 7.3 1-to-1 Executable Falsifier Matrix

Every architectural requirement maps 1-to-1 to an automated test:

| Req ID | Target Module | Test Name | Assertion / Failure Condition |
|---|---|---|---|
| `RF-01` | `runtime/compose.py` | `test_component_graph_compile` | Multi-planner manifest compiles cleanly to `FrozenHarness`. |
| `RF-02` | `domain/artifacts/manifest.py` | `test_component_graph_digest_unique` | Distinct component bindings produce distinct $D_H$ digests. |
| `RF-03` | `runtime/compose.py` | `test_code_default_mechanical_migration` | Migrated `code-default` manifest exhibits identical behavior. |
| `RF-04` | `runtime/trajectory.py` | `test_trajectory_non_zero_cost` | Non-trivial turn execution MUST emit total tokens > 0. |
| `RF-05` | `runtime/trajectory.py` | `test_trajectory_model_fingerprint` | Model fingerprint is present and matches provider digest. |
| `RF-06` | `runtime/trajectory.py` | `test_trajectory_verdict_embedded` | Verdict is embedded or explicitly null with `attributable: false`. |
| `RF-07` | `runtime/compose.py` | `test_absent_evaluator_compiles` | `evaluation: none` compiles without spawning UID 10002 daemon. |
| `RF-08` | `runtime/evaluator_gateway.py` | `test_unsigned_verdict_rejected` | Forged or unsigned verdict is rejected by gateway. |
| `RF-09` | `runtime/trajectory.py` | `test_absent_eval_unattributable` | `evaluation: none` tags trajectory as non-attributable for promotion. |
| `RF-10` | `runtime/registry/` | `test_unknown_ref_fails_compose` | Unknown plugin ref fails at composition time, not at runtime. |
| `RF-11` | `runtime/registry/` | `test_faulted_cell_killed` | Faulted cell is killed and cannot remain in `ACTIVATED` state. |
| `RF-12` | `runtime/registry/` | `test_frozen_composition_immutable` | No code path exists to mutate a `FrozenHarness` post-freeze. |
| `RF-13` | `runtime/registry/` | `test_empty_ceiling_denies` | Empty capability ceiling denies all privileged effects. |
| `RF-14` | `runtime/registry/` | `test_in_process_requires_grant` | `in_process` execution requires explicit governance grant. |
| `RF-15` | `runtime/registry/` | `test_registry_exclusive_plugin_write` | Only registry is authorized to emit `Plugin*` ledger events. |
| `RF-16` | `test/falsifiers/` | `test_react_as_topology` | ReAct loop expressed as topology + policy over turn loop. |
| `RF-17` | `test/falsifiers/` | `test_tree_search_as_topology` | Tree search expressed as topology + policy over turn loop. |
| `RF-18` | `test/falsifiers/` | `test_critic_loop_as_topology` | Critic-reviser expressed as topology + policy over turn loop. |
| `RF-19` | `adapters/stores/event_store.py` | `test_cold_suspend_resume` | Mid-turn suspend cleanly reconstructs from cold WAL in fresh process. |
| `RF-20` | `runtime/session.py` | `test_stigmergic_state_coordination` | Multiple agents coordinate via state plane without chat chatter. |

---

### 7.4 Negative Constraints & Anti-Patterns Checklist

Developers must strictly observe these negative rules. CI linters will automatically reject non-compliant PRs:
- ❌ **DO NOT import `kernel` or `agency` in `adapters/`:** Adapters implement ports only.
- ❌ **DO NOT import coding or domain tokens in `kernel/` or `domain/`:** Invariant I-7 enforces domain blindness.
- ❌ **DO NOT exceed TCB budget:** `vanguard/packages/kernel/` must remain $\le 1438$ logical LOC.
- ❌ **DO NOT bypass the single ledger writer:** All durable events must flow through `LedgerEmitter`.
- ❌ **DO NOT catch generic `Exception` without typed re-raise:** Fail-closed domain semantics are mandatory.
- ❌ **DO NOT mutate a `FrozenHarness` post-freeze:** Cryptographic composition immutability is absolute.
- ❌ **DO NOT write `Plugin*` events outside the registry:** Writer authority is strictly partitioned.
- ❌ **DO NOT accept unsigned verdicts under any composition:** Categorically illegal.
- ❌ **DO NOT sum sibling `depth` budgets:** Depth is a structural lease, not an additive currency.
- ❌ **DO NOT implement a swarm engine, workflow DAG, or graph DB:** Standing architectural refusal.

---

## 8. Repository Hygiene, Stale Debt Pruning & Linter Hardening

Based on the forensic codebase audit, the following hygiene actions are mandated:

| Action ID | Target File / Artifact | Finding & Action Required | Responsibility |
|---|---|---|---|
| `HYG-01` | `DELETE.md` (Repo Root) | 0-byte file at root. **Delete immediately.** | Tech Lead |
| `HYG-02` | `docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS_B.md` | Exact duplicate of `_A` (same `id: REF-06-M5`). **Delete duplicate.** | Systems Architect |
| `HYG-03` | `docs/06_references/RESEARCH_Harness_Builder_Framework.md` | Competing distributed architecture (Redis/NATS/K8s). **Mark ARCHIVED/REJECTED.** | CTO |
| `HYG-04` | `docs/06_references/vanguard_body_detailed.md` | Biological framing conflicts with ADR-M0-10. **Move to archive index.** | Principal Staff |
| `HYG-05` | `tools/linters/check_markdown_links.py` | Stale globs validate only 2 files. **Expand to all `docs/` and ADRs.** | Tech Lead |

---

## 9. Document Update Cascade & Transition Plan

Upon formal ratification, the following mechanical updates will be executed:

| Target Document | Target Section | Change Authorized | Governing ADR |
|---|---|---|---|
| `docs/SPEC.md` | §2.3 | Manifest structure updated to Named Component Graph (`mhf.manifest/2`) | ADR-0077 |
| `docs/SPEC.md` | §5.4 | Mandatory per-turn cost accounting and model fingerprinting | ADR-0078 |
| `docs/SPEC.md` | §3.1 | Universal turn loop claim published with formal falsifier | ADR-0082 |
| `docs/SPEC.md` | §9 | Refusal list reaffirmed (no DAG engine, no swarm engine) | ADR-0070 |
| `docs/05_adr/` | `INDEX.md` | Append ADRs 0077–0082 as immutable records | This document |
| `docs/03_sprints/sprint_active.md` | Sprints 2.2, 3.1–3.5 | Ingest NOVA-1/2/3 into Wave 2; Sprints 3.3/3.4/3.5 into Wave 3 | ADRs 0077–0081 |
| `docs/02_roadmap/milestones.md` | M-5 through M-10 | Post-foundation macro ladder recorded at outcome level | This document |
| `docs/03_sprints/doing/wave3_extensibility.md` | Full sprint plan | Rebalanced with NOVA-4 negative suite + Component Graph | ADRs 0077, 0079, 0081 |

---

## 10. The Four Foundational Proofs & Leadership Sign-Off Mandate

The meta-framework earns the right to exist only when these four claims survive empirical falsification:

- **P1 — "The corpus is learnable:"** NOVA-1 passes; `RF-04` content assertions green (costs > 0, populated turns, valid model fingerprint, signed verdict).
- **P2 — "The substrate is domain-general:"** Milestone M-5 gate passes; Pack #2 (Math/Deductive Systems) ships with **zero diffs** under `domain/` and `kernel/`.
- **P3 — "Concurrency is a scheduler refactor:"** NOVA-2 passes; cold suspend/resume from SQLite WAL succeeds deterministically in a fresh process.
- **P4 — "Self-improvement is safe:"** Milestone M-10 gate passes; signed promotion frontier + McNemar exact test + $D_H \neq D_R \neq D_X$ identity trinity prevents reward gaming by construction.

---

### Ratification & Sign-Off

```text
[APPROVED & RATIFIED BY THE LEADERSHIP 7]

• Engineering Director:        _________________________  Date: ____________
• Chief Technology Officer:    _________________________  Date: ____________
• Chief Information Officer:   _________________________  Date: ____________
• Principal Staff Engineer:    _________________________  Date: ____________
• Principal Systems Architect: _________________________  Date: ____________
• Tech Lead:                   _________________________  Date: ____________
• PhD AI Specialist:           _________________________  Date: ____________
```

---

## 11. Alternative Architectural Approach: The Adaptive Informational Harness & Pareto-Dynamic General Solver Framework

### 11.1 Executive Vision: The Primacy of Informational Harnessing

While classical agent substrates focus heavily on rigid state-machine boundaries and reference monitors, an alternative paradigm starts from a fundamental information-theoretic insight:

> **Agent intelligence, operational cost, execution latency, and problem-solving success are direct functions of informational topology. Controlling the harness that governs information flow, context projection, and state mutation is strictly superior to hardcoding agent roles or running unconstrained multi-agent dialogue.**

Modern single-agent CLI harnesses (e.g., Claude Code CLI, Hermes) demonstrate exceptional speed and execution accuracy by grounding the model directly in the local workspace with tight feedback loops and streaming tool execution. However, they hit hard ceilings on long-horizon reasoning, cannot explore speculative paths in parallel without exponential context bloat, and do not self-compound across tasks. Conversely, traditional multi-agent frameworks suffer from $O(N^2)$ conversational chatter, hallucinations compounding across ungrounded dialogue, and runaway token bills.

This alternative architecture synthesizes the **tactical agility of high-performance CLI harnesses** with **stigmergic swarm coordination**, **dynamic Pareto optimization**, and a **closed-loop compounding data flywheel**. It treats models as stateless, interchangeable cognitive transforms operating over an adaptive informational harness.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     THE ADAPTIVE INFORMATIONAL HARNESS META-FRAMEWORK                            │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                    Stigmergic State Plane (Shared Blackboard $\mathcal{W}$)                │  │
│  │   • Workspace / Artifacts   • Hypothesis & Proof Graph   • Constraint & Verification Log   │  │
│  └──────────────────────────────┬──────────────────────────────────────▲──────────────────────┘  │
│                                 │ Read Slice                           │ Atomic Mutation         │
│                                 ▼                                      │ $\Delta \mathcal{W}$     │
│                 ┌───────────────────────────────┐        ┌─────────────┴───────────────┐         │
│                 │   Informational Bottleneck    │        │ Decoupled Verification      │         │
│                 │      $\mathcal{B}_\theta(W)$  │        │ Oracle Engine $\mathcal{V}$ │         │
│                 └───────────────┬───────────────┘        └─────────────▲───────────────┘         │
│                                 │ Filtered & Compressed                │ Action Receipts         │
│                                 │ Context View                         │ & State Deltas          │
│                                 ▼                                      │                         │
│                 ┌──────────────────────────────────────────────────────┴───────────────┐         │
│                 │           Ephemeral Swarm Compute Units (Stateless)                  │         │
│                 │   [Scout]  •  [Coder / Synthesizer]  •  [Socratic Critic]  •  [...]   │         │
│                 └──────────────────────────────────────────────────────────────────────┘         │
│                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  DYNAMIC PARETO CONTROLLER: Cost ◄► Tokens ◄► Latency ◄► Quality                                 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 11.2 Core Primitives & Informational Flow Architecture

The meta-framework is built on four mathematically defined, language-agnostic primitives that generalize across all problem domains:

#### 1. The Stigmergic Blackboard ($\mathcal{W}$)
Coordination occurs entirely through mutations to an environmental blackboard rather than inter-agent messaging:
$$\mathcal{W} = \langle \mathcal{A}, \mathcal{H}, \mathcal{E}, \mathcal{T} \rangle$$
- $\mathcal{A}$ (**Artifact Store**): Source code trees, research documents, data frames, or proof scripts.
- $\mathcal{H}$ (**Hypothesis Graph**): Directed acyclic graph of active problem-solving hypotheses, explored branches, and dead ends.
- $\mathcal{E}$ (**Evidence & Invariant Ledger**): Append-only log of external test results, oracle verdicts, and empirical observations.
- $\mathcal{T}$ (**Telemetry & Cost Matrix**): Real-time token consumption, compute time, and financial cost tallies.

*Key Invariant:* Agents never talk directly to each other ($O(1)$ communication overhead per step). They inspect slices of $\mathcal{W}$ and propose atomic state deltas $\Delta \mathcal{W}$.

#### 2. The Dynamic Informational Bottleneck ($\mathcal{B}_\theta$)
A parameterized projection function grounded in Variational Free Energy that compresses the global blackboard state $\mathcal{W}$ into an optimal context window for a given sub-task:
$$\mathcal{B}_\theta: \mathcal{W} \times \text{TaskProfile} \to \text{ContextWindow}_{\le k}$$
$$\arg\min_{\mathbf{o}} \mathcal{F}(\mathbf{o}, \mathcal{W}) = D_{\text{KL}}\big[ q(\mathbf{s}) \parallel p(\mathbf{s} \mid \mathbf{o}) \big] - \ln p(\mathbf{o})$$
- Eliminates context window dilution by projecting only relevant AST subtrees, recent tool execution diffs, and salient hypothesis branches.
- Dynamically adjusts compression ratios ($k$-token budget) according to the active Pareto optimization profile.

#### 3. Dynamic Opportunity Leases ($\mathcal{L}$)
Every execution step is granted an explicit, non-renewable lease bounded across multiple dimensions with dynamic ROI tracking:
$$\mathcal{L} = \langle \text{MaxTokens}, \text{MaxWallTime}, \text{AllowedTools}, \text{TargetSlice}, \text{BudgetCost}, \text{EntropyCeiling} \rangle$$
- If an ephemeral worker exceeds any threshold in $\mathcal{L}$ or generates repetitive high-entropy output without progress, the harness terminates execution and rolls back uncommitted state.
- Workers demonstrating high Expected Free Energy reduction ($\Delta \mathcal{G}$) receive automatic, bounded lease renewals.

#### 4. Decoupled Verification Oracles ($\mathcal{V}$)
Independent evaluation harnesses that grade candidate mutations $\Delta \mathcal{W}$ against objective criteria:
$$\mathcal{V}(\Delta \mathcal{W}, \mathcal{W}) \to \langle \text{Status} \in \{\text{Pass}, \text{Fail}, \text{Indeterminate}\}, \text{Score} \in [0, 1], \text{EvidenceReceipt} \rangle$$
- Oracles range from fast deterministic checks (compilers, linters, unit tests, schema validators) to formal proof checkers and adversarial LLM critics.
- Workers cannot modify or self-certify oracle results.

---

### 11.3 Swarm & Harness Topology: High-Velocity Coordination Without Chatter

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    SWARM & HARNESS EXECUTION TOPOLOGY                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  [User Goal / Task Entry]                                                                              │
│             │                                                                                          │
│             ▼                                                                                          │
│  ┌─────────────────────────┐                                                                           │
│  │ Dynamic Pareto Router   │ ◄─── Selects Profile (Speed / Balanced / Deep Verification)               │
│  └──────────┬──────────────┘                                                                           │
│             │                                                                                          │
│             ├───────────────────────────────────────────────────────────────────────┐                  │
│             │ (Serial / Fast Path)                                                  │ (Parallel Swarm) │
│             ▼                                                                       ▼                  │
│  ┌─────────────────────────┐                                           ┌──────────────────────────┐    │
│  │ Ephemeral Single Worker │                                           │ Speculative Branch Swarm │    │
│  │ • Direct Tool Stream    │                                           │ • Worker A (Heuristic 1) │    │
│  │ • Local AST Diffing     │                                           │ • Worker B (Heuristic 2) │    │
│  └──────────┬──────────────┘                                           │ • Worker C (Adversarial) │    │
│             │                                                          └────────────┬─────────────┘    │
│             │                                                                       │                  │
│             ▼                                                                       ▼                  │
│  ┌────────────────────────────────────────────────────────────────────────────────────────────────┐    │
│  │ Decoupled Critic & Oracle Gate $\mathcal{V}$ (Compilers, Unit Tests, Formal Proofs, Invariants)│    │
│  └──────────────────────────────────────────────┬─────────────────────────────────────────────────┘    │
│                                                 │                                                      │
│                                                 ▼                                                      │
│                                    [State Commit ──► $\mathcal{W}$]                                    │
│                                                 │                                                      │
│                                                 ▼                                                      │
│                                 [Compounding Data Flywheel Feed]                                       │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Stigmergic Synchronization:** Agents coordinate asynchronously by reading and writing to the blackboard $\mathcal{W}$. When a scout agent identifies an AST dependency or an empirical contradiction, it writes a fact node to $\mathcal{W}$; executor agents consume that node on their next lease turn without any direct agent-to-agent negotiation.
2. **Speculative Parallel Branching & Pareto Merge:**
   - On complex or high-ambiguity tasks, the harness spawns multiple lightweight workers with distinct exploration priors (e.g., greedy local patch vs. structural refactoring).
   - Workers execute in isolated scratch branches.
   - The decoupled oracle $\mathcal{V}$ evaluates all resulting candidate branches simultaneously, committing the highest-scoring, lowest-cost branch to $\mathcal{W}$ and pruning the remainder.
3. **Hierarchical Context Compaction Pipelines:** Raw tool outputs (e.g., massive compiler logs, search dumps) are compressed at the capture edge by specialized lightweight transforms before being presented to planning agents, maintaining constant context density.

---

### 11.4 Dynamic Pareto Optimization Matrix

The meta-framework replaces static execution loops with a **Dynamic Pareto Controller** that balances four interdependent variables: **Financial Cost ($C$)**, **Token Consumption ($T$)**, **Wall-Clock Latency ($L$)**, and **Output Quality / Confidence ($Q$)**.

```text
                                        [Quality / Confidence (Q)]
                                                    ▲
                                                   ╱│╲
                                                  ╱ │ ╲
                                                 ╱  │  ╲
                                                ╱   │   ╲
                       [Financial Cost (C)] ◄───────┼───────► [Wall-Clock Latency (L)]
                                                ╲   │   ╱
                                                 ╲  │  ╱
                                                  ╲ │ ╱
                                                   ╲│╱
                                                    ▼
                                          [Token Volume (T)]
```

#### Pareto Operational Profiles

| Profile Name | Target Optimization | Typical Latency | Token Spend / Turn | Routing & Model Strategy | Harness & Swarm Topology | Ideal Task Types |
|---|---|---|---|---|---|---|
| **$\alpha$ — Flash Tactical** | Minimize Cost & Latency | $< 1.0\text{s}$ | $500 - 2,000$ | Small fast models; strict heuristic prompting | Ephemeral single-turn worker; direct local tool execution; zero debate | Unit test fixes, syntax errors, simple script generation, file lookups |
| **$\beta$ — Balanced Autonomous** | Balanced Pareto Frontier | $3.0 - 10.0\text{s}$ | $2,000 - 8,000$ | Mid-tier models; dynamic context projection | Scout $\to$ Executor pipeline; single-pass verification oracle | Multi-file feature additions, refactoring, bug triage, data analysis |
| **$\gamma$ — SOTA Deductive** | Maximize Quality & Rigor | $15.0 - 60.0\text{s}$ | $8,000 - 35,000$ | Frontier reasoning models; multi-candidate search | Speculative tree search; adversarial debate; multi-stage oracle verification | Architecture design, formal verification, complex math, security audits |
| **$\delta$ — Adaptive Self-Escalating** | Dynamic Optimal Efficiency | Variable | Dynamic | Starts at $\alpha$; escalates to $\beta$ or $\gamma$ upon oracle failure | Tiered escalation with state preservation | General autonomous problem solving under strict budget ceilings |

#### The Dynamic Frontier Controller Algorithm
1. **Initial Profile Selection:** The task entry is classified by a lightweight heuristic estimator that predicts complexity and sets initial profile $\theta_0$.
2. **Execution & Oracle Check:** The worker executes under lease $\mathcal{L}(\theta_0)$ and submits candidate delta $\Delta \mathcal{W}$ to oracle $\mathcal{V}$.
3. **Adaptive Escalation:** If $\mathcal{V}$ fails or returns low confidence:
   - The failure context is captured as an evidence node in $\mathcal{W}$.
   - The controller automatically escalates to profile $\theta_{i+1}$ (allocating higher model tier, wider context projection, or multi-branch exploration).
   - Only the delta and the specific falsifier are passed forward, avoiding full context replay.

---

### 11.5 The Compounding Data Flywheel: Self-Evolution & Cost Collapse

A critical differentiator of this architecture is that every executed trajectory actively reduces the token and dollar cost of future executions while increasing accuracy.

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   THE COMPOUNDING DATA FLYWHEEL                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│   [Live Execution Trajectories]                                                                        │
│                 │                                                                                      │
│                 ▼                                                                                      │
│   ┌───────────────────────────┐                                                                        │
│   │ 1. Attribution & Harvest  │ ──► Logs (State $\mathcal{W}$, Action $A$, Oracle Score $S$, Cost $C$) │
│   └─────────────┬─────────────┘                                                                        │
│                 │                                                                                      │
│                 ▼                                                                                      │
│   ┌───────────────────────────┐                                                                        │
│   │ 2. Compiled Tool Registry │ ──► Distills multi-step token loops into deterministic macro-tools     │
│   └─────────────┬─────────────┘     (Turns 50k tokens of agent reasoning into a 500-token tool call)   │
│                 │                                                                                      │
│                 ▼                                                                                      │
│   ┌───────────────────────────┐                                                                        │
│   │ 3. DPO & Policy Fine-Tune │ ──► Harvests verified winner/loser branch pairs for model distillation │
│   └─────────────┬─────────────┘     (Enables smaller models to match frontier performance)             │
│                 │                                                                                      │
│                 ▼                                                                                      │
│   ┌───────────────────────────┐                                                                        │
│   │ 4. Meta-Policy Adaptation │ ──► Updates Pareto routing thresholds and context compression ratios   │
│   └─────────────┬─────────────┘                                                                        │
│                 │                                                                                      │
│                 └───────────────────────────────┐                                                      │
│                                                 ▼                                                      │
│                                  [Next Execution: 70–95% Cheaper & Faster]                             │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Step-Level Attribution & Cost Accounting:** Every action, tool invocation, and context projection is tagged with exact token and financial costs, paired with the subsequent oracle score $\Delta S$.
2. **Compiled Deterministic Macro-Skill Tool Registry:**
   - When the flywheel identifies repeated multi-step patterns in successful trajectories (e.g., resolving a recurring dependency conflict or executing a specific AST migration), an offline synthesizer distills the sequence into a standalone, deterministic executable tool with unit tests.
   - Future workflows invoke the new macro-tool directly, collapsing a 15-turn reasoning loop into a single tool dispatch (producing a $>90\%$ reduction in token expenditure).
3. **Preference Pair Extraction & Distillation (DPO/RL):**
   - Branching explorations evaluated by $\mathcal{V}$ produce clean, unforgeable preference pairs: $\langle \text{Prompt}, \text{Winner Branch}, \text{Loser Branch} \rangle$.
   - These datasets continuously train smaller, cheaper models to replicate the decision quality of large frontier models on domain-specific workloads.
4. **Meta-Cognitive Policy Optimization:** The router's difficulty classification heuristics and context projection filters are updated using empirical Bayesian updates from production runs, ensuring the Pareto frontier continually shifts towards lower cost and higher reliability.

---

### 11.6 Dual Capability: Unified Primitives for Coding and General Problem Solving

Rather than maintaining separate architectures for software development and general task automation, the four primitives ($\mathcal{W}$, $\mathcal{B}_\theta$, $\mathcal{L}$, $\mathcal{V}$) instantiate both domains with identical execution mechanics:

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              UNIFIED PRIMITIVES ACROSS MULTIPLE DOMAINS                                │
├────────────────────────────┬──────────────────────────────────────────┬────────────────────────────────┤
│ Primitive                  │ Software Engineering Domain              │ General Autonomous Task Domain │
├────────────────────────────┼──────────────────────────────────────────┼────────────────────────────────┤
│ **Blackboard**             │ File tree, AST index, git diffs, build   │ Document corpus, claims graph, │
│ $\mathcal{W}$              │ logs, unit test results                  │ entity tables, data pipelines  │
├────────────────────────────┼──────────────────────────────────────────┼────────────────────────────────┤
│ **Bottleneck**             │ File-slice projector, failing stack      │ Semantic claim summarizer,     │
│ $\mathcal{B}_\theta$       │ traces, relevant function signatures     │ table slice filter, search top-K│
├────────────────────────────┼──────────────────────────────────────────┼────────────────────────────────┤
│ **Action Lease**           │ Diff budget, terminal tool allowance,    │ API rate limits, web scrapers, │
│ $\mathcal{L}$              │ max test runner execution timeout        │ database write permissions     │
├────────────────────────────┼──────────────────────────────────────────┼────────────────────────────────┤
│ **Verification Oracle**    │ Compilers, linters, unit tests,          │ Formal deduction engines,      │
│ $\mathcal{V}$              │ coverage suites, security scanners       │ schema validators, logic oracles│
└────────────────────────────┴──────────────────────────────────────────┴────────────────────────────────┘
```

#### Application Walkthroughs

##### 1. High-Velocity Software Engineering Walkthrough
1. **Task:** Fix an intermittently failing asynchronous race condition across three microservice modules.
2. **Informational Flow:**
   - $\mathcal{B}_\theta$ projects the stack trace, relevant test file, and targeted interface signatures into a 3,000-token context.
   - Profile $\beta$ spawns two workers with diverse synchronization strategies.
   - Both workers generate AST diffs in isolated scratch workspaces.
   - Oracle $\mathcal{V}$ runs the test suite concurrently against both patches.
   - The passing patch is atomically merged into $\mathcal{W}$; the failure trajectory is logged for skill distillation.
   - Total execution time: $4.2\text{s}$; total cost: $<\$0.02$.

##### 2. Autonomous Multi-Domain Research & Deductive Synthesis Walkthrough
1. **Task:** Reconcile conflicting experimental datasets across 50 scientific papers and produce a verified synthesis table.
2. **Informational Flow:**
   - $\mathcal{W}$ initializes with the bibliography and target schema.
   - A swarm of lightweight Scout workers ($\alpha$ profile) reads paper slices in parallel, extracting claims and empirical metrics into the blackboard graph.
   - A Synthesizer worker identifies contradictions and flags them in $\mathcal{H}$.
   - A Socratic Critic and Formal Logic Oracle ($\mathcal{V}$) verify claim consistency and eliminate ungrounded extrapolations.
   - The final verified dataset is committed to $\mathcal{W}$ and exported.
   - Total execution achieved without any unstructured agent-to-agent chatter.

---

### 11.7 Architectural Comparison & Strategic Differentiators

| Architectural Dimension | Monolithic CLI Harnesses (e.g. Claude Code, Hermes) | Traditional Multi-Agent Frameworks (e.g. AutoGen, CrewAI, LangGraph) | Proposed Adaptive Informational Harness Meta-Framework |
|---|---|---|---|
| **Coordination Model** | Single agent in linear loop; no swarming | Conversational dialogue ($O(N^2)$ chatter) or rigid DAG edges | **Stigmergic Blackboard ($\mathcal{W}$)**; $O(1)$ decoupled communication |
| **Context Management** | Monolithic linear history with truncation | Full conversation pass-through; rapid context rot | **Dynamic Informational Bottlenecks ($\mathcal{B}_\theta$)** tailored per lease |
| **Pareto Optimization** | Fixed model & prompt tier per session | Typically static model assignments | **Dynamic Pareto Controller** ($\alpha \to \delta$ adaptive scaling) |
| **Verification & Trust** | Agent evaluates its own tool output | Subjective consensus or conversational voting | **Decoupled Exterior Oracles ($\mathcal{V}$)**; zero self-grading |
| **Data Flywheel & Learning** | Ephemeral sessions; zero compounding | Logs transcripts without structured attribution | **Compounding Flywheel**: Macro-skill distillation & automated DPO datasets |
| **Domain Portability** | Hardcoded terminal and code-editing primitives | High-level chat primitives; poor tactical coding speed | **Unified Primitives** ($\mathcal{W}, \mathcal{B}_\theta, \mathcal{L}, \mathcal{V}$) across code, data, and logic |

---

### 11.8 Synthesis & Strategic Takeaway

This alternative architecture demonstrates that solving the general task-solving problem does not require choosing between the **raw tactical speed of single-agent CLI harnesses** and the **higher-order problem-solving capability of multi-agent swarms**.

By establishing an **Adaptive Informational Harness** that strictly regulates the flow of state, context, leases, and verification:
- The system achieves **near-instant, ultra-cheap execution** on routine coding and lookup tasks.
- It dynamically scales to **speculative, parallel swarm exploration** on complex deductive and creative challenges.
- It turns every execution into a **permanent, compounding asset**, systematically reducing operational costs and driving long-term autonomous capability.
