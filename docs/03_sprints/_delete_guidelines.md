# Master Audit, Architectural Review & Concept Consolidation Index

**Target Milestone:** Intermediary Sprint (Preparation for v0.6.1, v0.6.2, and v0.7.0)  
**Classification:** Neutral Architectural & Concept Audit for Director Review  
**Audience:** Director / System Architect  
**Status:** In Progress (Steps 1, 2 & 3 Complete; Awaiting Step 4)  

> [!IMPORTANT]
> **Advisory Disclaimer for the Director:**  
> This document is a factual, unbiased system engineering and concept review. It audits the live implementation in `vanguard/`, compares it with the normative law in [`docs/SPEC.md`](../SPEC.md), and catalogues all reviews and reference frameworks. It does **not** make executive decisions or declare product policies; all strategic decisions and wave authorizations remain exclusively with the Director.

---

## Document Index & Audit Phasing Plan

To prevent context noise and ensure rigorous verification, this consolidation is executed in ordered steps:
- **Step 1 [COMPLETE]: Vanguard Implementation Reality (`vanguard/`) vs. Normative Law ([`docs/SPEC.md`](../SPEC.md))**
- **Step 2 [COMPLETE]: Forensic & Review Documents Audit ([`docs/07_reviews/`](../07_reviews/))**
- **Step 3 [COMPLETE]: Research & Framework References Audit ([`docs/06_references/`](../06_references/))**
- **Step 4 [QUEUED]: Synthesis of Concept Collisions, Trade-offs, and Architectural Options for Wave 3+ & v0.7.0**

---

# Step 1: Vanguard Implementation Reality vs. Normative Law

This section audits the active codebase under `vanguard/` against the authoritative specification in [`docs/SPEC.md`](../SPEC.md) (RFC-2119 Normative Law).

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HEXAGONAL BOUNDARY LATTICE                         │
│                                                                             │
│  domain  ◄──  ports  ◄──  kernel  ◄──  agency  ◄──  runtime  ──►  adapters  │
│                                                        ▲                    │
│                                                        │                    │
│                                                   clients/cli               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1.1 Subsystem Inventory & Physical Mapping

The production codebase strictly enforces the hexagonal boundary lattice:
`domain ← ports ← kernel ← agency ← runtime → adapters` (with `clients/cli` as a client of runtime).

| Subsystem | Location | LOC / Files | Status & Core Responsibilities |
|---|---|---|---|
| **Domain** | `vanguard/packages/domain/` | 13 files | **Pure stdlib values & wire contracts.** Implements JCS canonicalization (`jcs.py`), JSON-RPC wire codec (`wire/jsonrpc.py`), generated schema types (`wire/types_gen.py`), Result ADT (`wire/result.py`), ledger events (`ledger/events.py`), state reducers (`ledger/reducer.py`), and resource selector algebra (`selectors/resource_selector.py`). Zero third-party dependencies. |
| **Ports** | `vanguard/packages/ports/` | 10 files | **Hexagonal port interfaces & SPI protocols.** Defines protocols for `kernel.py`, `model.py`, `sandbox.py`, `evaluator.py`, `event_store.py`, `blob_store.py`, `environment.py`, `determinism.py`, `index.py`, and the 5 extensible SPI protocols in `spi.py` (`PluginHost`, `ToolPlugin`, `ModelProvider`, `EvaluatorPlugin`, `PolicyPlugin`). |
| **Kernel** | `vanguard/packages/kernel/` | 9 files<br>(1,365 LOC logical) | **Trusted Computing Base (TCB limit $\le 1438$ LOC).** Implements the 13-stage dispatch pipeline S0–S12 (`dispatch.py`), monotonic capability attenuation algebra (`attenuation.py`), 6D typed lease arithmetic (`budget.py`), descriptor-bound grants (`grants.py`), fail-closed classifier (`classifier.py`), policy evaluator (`policy.py`), and execution provenance DAG (`provenance.py`). Domain-blind (enforces Invariant I-7). |
| **Agency** | `vanguard/packages/agency/` | 10 files | **Recursive turn engine.** Implements `EpisodeEngine` turn loop (`episode/engine.py`), model proposal translation, context compiler & token budgeting (`context/compiler.py`), structured compaction, and manifest gene digest verification (`manifests/`). |
| **Runtime** | `vanguard/packages/runtime/` | 18 files | **Composition, lifecycle, and governance.** Split into modular primitives: `compose.py` (harness composition), `session.py` (session runner), `wiring.py` (adapter wiring), `root.py` (composition facade), `ledger_emitter.py` (sole authorized ledger writer), `evaluator_gateway.py` (signed exterior verdict client), `governance/` (Ed25519 approvals), and `trajectory.py` (`mhf.trajectory/1` builder). |
| **Adapters** | `vanguard/packages/adapters/` | 14 files | **Concrete infrastructure implementations.** Models (`openrouter.py`, `ollama.py`, `cassette.py`, `fake.py`, `planner.py`), Evaluators (UID 10002 external daemon `daemon.py`, `rpc_client.py`), Sandbox (UID 10001 rootless bubblewrap `bwrap.py`, `toolkit.py`, `ceiling.py`), and Stores (SQLite WAL `event_store.py`). Must not import `kernel` or `agency`. |
| **Clients** | `vanguard/clients/cli/` | TypeScript/React | **Interactive CLI (`vg`).** TypeScript 5.x + Ink TUI communicating with the runtime via streaming JSON-RPC. Consumes generated wire readers. |

---

## 1.2 Normative Law Concordance Table: `vanguard/` vs. `docs/SPEC.md`

| SPEC Requirement / Axiom | Normative Specification | Live Implementation in `vanguard/` | Audit Verdict |
|---|---|---|---|
| **A-1. Microkernel & TCB Budget** | Layer 0 LOC target $\le 1438$ logical LOC for the kernel core. | `vanguard/packages/kernel/` contains exactly 1,365 logical LOC across 9 files. Enforced by `tools/linters/check_tcb_budget.py`. | **100% CONCORDANT** |
| **A-2. Independent Authority Systems** | Broker grants capability to agents; sandbox contains plugin execution. | Monotonic capability attenuation in `kernel/attenuation.py`; rootless bubblewrap sandbox isolation in `adapters/sandbox/bwrap.py`. | **100% CONCORDANT** |
| **A-3. Event-Sourced Durability** | Everything is an event. Replay is a required property. SQLite WAL ledger. | `SqliteEventStore` with `PRAGMA journal_mode = WAL`. `LedgerEmitter` is the sole writer. Cold replay parity tested in `test/runtime/test_ledger_truth.py`. | **100% CONCORDANT** |
| **A-4. Schema Authority & Code Generation** | JSON Schema + JCS canonicalization is sole source of truth. Generated types for Python and TS. | `jcs.py` canonicalization with golden vectors; `tools/codegen/generate_types.py` generates wire types into `domain/wire/types_gen.py`. | **100% CONCORDANT** |
| **A-5. Content-Addressed Identity** | Harness identity $D_H$ is distinct from Run identity $D_R$ and Experiment cell $D_X$. | `gene_digest` and manifest hashing in `agency/manifests/`; distinct execution and experiment IDs in runtime context. | **100% CONCORDANT** |
| **§1.0 Recursive Machine & Typed Leases** | Additive 4D budget (`usd_micros`, `tokens`, `bytes`, `millis`) + structural 2D ceilings (`depth`, `turns`). | Implemented in `kernel/budget.py` (`Lease` and `Governor` classes with component-wise subtraction and attenuation). | **100% CONCORDANT** |
| **§1.1 S0–S12 Dispatch Pipeline** | 13-stage monotonic mediator (Observe, Policy, Attenuate, Authorize, Effect, Ledger, Verdict). | Fully implemented in `kernel/dispatch.py` (`DispatchPipeline` executing stages S0 through S12). | **100% CONCORDANT** |
| **§1.6 Exterior Evaluation** | Separability thesis: the judge is unreachable from the judged (UID 10002 daemon, signed verdict with request-bound nonce). | `adapters/evaluators/daemon.py` and `runtime/evaluator_gateway.py` enforce signed Ed25519 verdicts with nonces. | **100% CONCORDANT** |
| **Invariant I-7 Domain Blindness** | Whole-word `coding`, `pytest`, `ast` forbidden in `domain/` and `kernel/`. | Verified on every commit by `tools/linters/check_domain_blindness.py`. | **100% CONCORDANT** |

---

## 1.3 Architectural Gaps, Drifts & Nuances Identified

While the foundation is structurally solid, the following nuances and in-flight items exist between the live code and the future macro roadmap:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          IDENTIFIED GAPS & NUANCES                          │
├────────────────────────────────┬────────────────────────────────────────────┤
│ 1. Hollow Trajectory Cost       │ trajectory.py emits _ZERO_COST placeholders │
│                                │ (F-12 tests pass schema, but cost is zero) │
├────────────────────────────────┼────────────────────────────────────────────┤
│ 2. Fixed-Slot Manifest vs.     │ runtime/compose.py uses fixed slot schema; │
│    Component Graph             │ dynamic component graph is queued (Wave 3) │
├────────────────────────────────┼────────────────────────────────────────────┤
│ 3. layer0/ Absorption State    │ SPI protocols and wire absorbed; plugin    │
│                                │ lifecycle FSM (registry/compose) in layer0 │
├────────────────────────────────┼────────────────────────────────────────────┤
│ 4. agent.spawn Capability Verb │ Exists as engine method in agency/episode, │
│                                │ not yet a first-class mediated tool verb   │
└────────────────────────────────┴────────────────────────────────────────────┘
```

1. **Trajectory Cost Telemetry (Gap G1 / NOVA-1)**:
   * *Code Reality*: In `vanguard/packages/runtime/trajectory.py` (lines 53, 75), the trajectory builder uses `dict(_ZERO_COST)` dummy placeholders.
   * *Impact*: The trajectory satisfies the schema `mhf.trajectory/1` (making F-12 green), but the actual per-turn token costs and model usage metrics are not populated from model responses.
   * *Note for Director*: Populating real costs into `trajectory.py` is necessary before training or trajectory harvesting (DPO/RL) can use the dataset.

2. **Harness Composition: Fixed-Slot Template vs. Component Graph (Gap G2)**:
   * *Code Reality*: `vanguard/packages/runtime/compose.py` currently loads a fixed-slot manifest (`harness.yaml` with pre-defined slots: model, context, tools, evaluator, sandbox).
   * *Roadmap Direction*: SPEC A-5 and Wave 3 plan a generic **Named Component Graph** where arbitrary plugin nodes and topologies (critic loops, debate, trees) can be declared declaratively.

3. **`layer0/` Convergence Status**:
   * *Code Reality*: `layer0/kernel/`, `layer0/scheduler/`, and `layer0/spi/` have been absorbed and removed. However, `layer0/registry/` (Plugin Lifecycle FSM: Discovered $\to$ Loaded $\to$ Active $\to$ Faulted $\to$ Retired) and `layer0/compose/` (Manifest Compiler) remain in `layer0/` and must be ported into `vanguard/packages/runtime/registry/` during Wave 3 before `layer0/` is retired.

4. **Mediation of `agent.spawn` (Gap G3)**:
   * *Code Reality*: Recursive delegation is implemented internally in `vanguard/packages/agency/episode/engine.py` via `spawn()`.
   * *Roadmap Direction*: Exposing `agent.spawn` as a mediated tool verb with its own capability grant and lease attenuation is scheduled for Wave 5+.

---

## 1.4 Verification & Metric Baseline

- **Architectural & Security Linters**: 8 / 8 Passing (0 errors)
  - `check_boundaries.py` (248 files verified)
  - `check_tcb_budget.py` (1,365 / 1,438 LOC logical)
  - `check_domain_blindness.py` (Invariant I-7)
  - `check_isolation_policy.py` (Invariant I-6)
  - `check_duplication.py` (Zero duplicate surfaces)
  - `check_markdown_links.py` (100% link resolution)
  - `check_stale_paths.py` (Zero obsolete doc references)
  - `scan_secrets.py` (Zero leaked credentials)
- **Unit & Contract Test Suite**: **434 Tests 100% GREEN (OK)** in 8.2s (`test/kernel`, `test/contracts`, `test/agency`, `test/packs`, `test/tools`, `test/falsifiers`).

---

# Step 2: Comprehensive Audit of Forensic & Review Documents (`docs/07_reviews/`)

This section catalogues and evaluates every document under `docs/07_reviews/`. It identifies what each document contributes, how they relate to the codebase, and where proposals evolved or diverged.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          07_REVIEWS DOCUMENT HIERARCHY                      │
│                                                                             │
│  [Investigation]                                                            │
│   ├── VANGUARD_V060_FORENSIC_DISCOVERY.md (Evidence of dual-tree split)     │
│   └── ARCHIVE.md (Historical review consolidation map)                      │
│                                                                             │
│  [Director Approved Lock (v0.6.0)]                                          │
│   ├── 001_V060_concept_phase_GAMMA.md (Concept Lock & P0 adjudication)      │
│   ├── 002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md (Falsifiers F01..F21) │
│   └── 003_V060_DIRECTOR_REVIEW.md (Director Approval & Wave 0 mandate)     │
│                                                                             │
│  [Advisory Generality & Alignment (v0.6.1+ Vision)]                        │
│   ├── 004_V061_ALIGNMENT_ROADMAP.md (Macro Milestone ladder M-0..M-10)     │
│   ├── 005_V061_SUBSTRATE_GENERALITY_REVIEW.md (Component Graph & Spawning) │
│   └── 006_V061_aether-substrate-briefing.md (Substrate Theory & 3 Planes)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2.1 Individual Document Analysis

### 1. `docs/07_reviews/ARCHIVE.md`
- **Type / Role:** Archive Index & Provenance Note.
- **Core Content:** Records the consolidation of the old `OLD_TECH_LEAD_REVIEW_archive/` (Tech Lead, Architect, AI Specialist, Systems-Eng advisory logs) into git history at commit `4f9f8b1`.
- **Status in Architecture:** Informational metadata. Explains where legacy pre-v0.6 reviews are preserved.

---

### 2. `docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md`
- **Type / Role:** Forensic Investigation Report (`[FACT]` / `[INFERENCE]` / `[PROPOSAL]`).
- **Core Content:**
  - Unearthed the dual-runtime problem (`vanguard/packages/` vs `layer0/`).
  - Caught the living CI anomaly (CI was gating `test/layer0` and skipping `test/kernel`).
  - Identified defect F1 (`layer0/scheduler/driver.py` fabricating `VerdictRecorded {verdict: "pass"}`).
  - Documented the exact split-brain duplications between `layer0/events/` and `domain/ledger/`.
- **Status in Architecture:** Diagnostic evidence cited by ADRs `0069`–`0075`. Not normative law.

---

### 3. `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md`
- **Type / Role:** Approved Concept Lock Plan.
- **Core Content:**
  - Adjudicated four independent advisory lanes into 12 core P0 architectural decisions.
  - Locked the Python-first decision (rejecting a premature Rust rewrite or a third `core/` tree).
  - Defined the S0–S12 Reference Monitor, monotonic capability attenuation, descriptor-bound grants, and Ed25519 external evaluator.
  - Established the separation of the 3 Planes: Decision, State, and Evidence.
- **Status in Architecture:** Formally approved by Director Review (`003`) and codified in ADRs `0069`–`0074` and [`docs/SPEC.md`](../SPEC.md).

---

### 4. `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`
- **Type / Role:** Living Engineering Gap & Falsifier Register.
- **Core Content:**
  - Catalogues 21 bound falsifiers (F-01 through F-21) mapped to specific verification tests.
  - Defines the 5 Foundation Waves (Wave 0: CI Truth, Wave 1: Trust Spine, Wave 2: Lattice Convergence, Wave 3: Extensibility, Wave 4: Foundation E2E Stop).
- **Status in Architecture:** The operational engineering roadmap for Foundation execution.

---

### 5. `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_DIRECTOR_REVIEW.md`
- **Type / Role:** Formal Engineering Director Approval Verdict.
- **Core Content:**
  - Formal C-level **APPROVED** verdict authorizing Wave 0.
  - Added findings F-18 (I-7 domain-blindness scan scope), F-19 (test discovery hygiene), F-20 (canonical oracle registry restoration), and F-21 (proposal translation lifts).
  - Explicitly established the rule: **No scope beyond the `002` register without a new ADR.**
- **Status in Architecture:** The formal governance authorization anchor for v0.6.0.

---

### 6. `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/004_V061_ALIGNMENT_ROADMAP.md`
- **Type / Role:** Alignment Roadmap Proposal (v0.6.1+).
- **Core Content:**
  - Proposes formalizing the Substrate Generality Review conclusions into append-only ADRs (`0077+`).
  - Lays out the post-foundation Macro Milestone ladder (M-5 through M-10) up to Meta-Cognition and Self-Improvement.
  - Mandates keeping M-5 through M-10 as outcome/gate milestones without authorising unstarted sprint-level details.
- **Status in Architecture:** Advisory roadmap proposal for post-v0.6.0 staging.

---

### 7. `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md`
- **Type / Role:** Independent Generality Audit.
- **Core Content:**
  - Investigates whether Vanguard is a general multi-agent substrate or merely a coding harness with a kernel attached.
  - Verdict: The foundational primitives (S0–S12 mediator, monotonic attenuation, SQLite WAL, exterior judge) are general and robust.
  - Bottlenecks identified: (1) `harness.yaml` is a fixed-slot template rather than a dynamic **Named Component Graph**, (2) Planners cannot spawn subagents as a mediated tool verb.
  - Recommends rebalancing Wave 3 with a negative falsifier suite (NOVA-4).
- **Status in Architecture:** Advisory review providing the architectural blueprint for Wave 3+ extensibility.

---

### 8. `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/006_V061_aether-substrate-briefing.md`
- **Type / Role:** Theoretical & Conceptual Substrate Briefing.
- **Core Content:**
  - Formulates the theory of composable agentic substrates: Separability Thesis, Three Planes of Responsibility, Measurement Denominators ($D_H \neq D_R \neq D_X$).
  - Explores the tension between "Everything-is-a-Plugin" (total composition freedom with zero central authority) vs. "Privileged Reference Monitor" (Vanguard's fail-closed kernel).
  - Concludes that Vanguard achieves the synthesis: an immutable, minimal authority kernel ($\le 1438$ LOC) that enables an unconstrained composition graph above it.
- **Status in Architecture:** Theoretical briefing and conceptual grounding for the framework.

---

## 2.2 Concept Concordance & Evolution Matrix

The review documents exhibit strong internal consistency on the core trust spine, with clear conceptual evolution regarding composition and spawning:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONCEPT CONCORDANCE & EVOLUTION                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. UNANIMOUS CORE CONSENSUS:                                                │
│    • Separability Thesis: Judge unreachable from the judged (Ed25519 UID).  │
│    • Three Planes: Decision (volatile), State (WAL), Evidence (signed).     │
│    • Identity Trinity: D_H (manifest) ≠ D_R (run) ≠ D_X (experiment).       │
│    • Single Recursion: Agent = Principal + HarnessInstance (attenuated).   │
│    • TCB Limit: Kernel <= 1438 LOC logical, Python stdlib core.             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. CONCEPTUAL EVOLUTION / DIFFERING SCOPE:                                  │
│    • Manifest Topology: Fixed 5-slot template (001/SPEC)                    │
│      ──► Evolved to: Named Component Graph (004/005).                       │
│    • Subagent Spawning: Engine internal method (001/SPEC)                   │
│      ──► Evolved to: Mediated capability verb for planners (004/005).       │
│    • Guardrail Policy: Universal evaluator daemon required (001)            │
│      ──► Evolved to: "Absent-vs-Forged" declaration model (004/005).        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2.3 Advisory Observations for Director Consideration

1. **Manifest Schema Transition (Fixed Slot $\to$ Component Graph)**:
   * *Observation*: Transitioning from fixed slots (`planner`, `context`, `memory`, `evaluator`, `toolkits`) to a **Named Component Graph** in Wave 3 allows complex topologies (debate, tree search, reflection loops) without modifying the kernel.
   * *Advisory Note*: The Director should decide whether to formalize the Component Graph schema at the start of Wave 3 before `compose.py` v2 is finalized.

2. **`agent.spawn` Capability Verb**:
   * *Observation*: Exposing `spawn` as a mediated tool verb allows model planners to spawn child agents directly under strict budget attenuation.
   * *Advisory Note*: All reviews agree this should remain **Design Only** during Waves 1–4 and be implemented post-M-4.

3. **Guardrail Declaration ("Absent-vs-Forged")**:
   * *Observation*: For non-coding domains (math, chat, research) where a UID 10002 daemon is not present, compositions can declare `evaluation: none`. $D_H$ records this absence, and resulting trajectories are marked non-promotable, preserving the integrity of the trust spine without breaking generality.

---

# Step 3: Comprehensive Audit of Research & Reference Documents (`docs/06_references/`)

This section audits, catalogues, and evaluates all 12 reference and research documents under `docs/06_references/`. These documents provide the empirical benchmarks, mathematical foundations, and multi-agent theories that inform Vanguard / AETHER's long-term evolution (Waves 5–10 / Meta-Cognition).

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          06_REFERENCES TAXONOMY                             │
│                                                                             │
│  [State-of-the-Art Agentic Harness Research]                                │
│   ├── RESEARCH_harness_agentic_coding_builder_research_and_framework.md     │
│   ├── RESEARCH_harness_agentic_coding_builder_research_and_framework_B.md   │
│   └── RESEARCH_Harness_Builder_Framework.md (Product PRD & Plugins)        │
│                                                                             │
│  [Mathematical, Optimization & Meta-Cognitive Foundations]                 │
│   ├── RESEARCH_THEORETICAL_SYNTHESIS.md (Active Inference / Credit / DPO)   │
│   ├── RESEARCH_THEORETICAL_SYNTHESIS_B.md (Duplicate Copy)                  │
│   └── RESEARCH_deepseek-harness_algorithms-ideas.md (Reverse Eng & M5 Math) │
│                                                                             │
│  [Architectural Proposals & Model Selections]                               │
│   ├── RESEARCH_k3_harness-suggestion.md (SOTA Plan & A-B-C-D Model)         │
│   ├── proposal_glm_harness_BETA.md (Independent GLM External Assessment)    │
│   ├── proposal_hy3_harness.md & proposal_hy3_improved.md (HY3 Architecture) │
│   ├── vanguard_body_detailed.md (Subsystem anatomy)                         │
│   └── openrouter_llm_models_suggested.md (Model routing & benchmark tiers)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3.1 Individual Document Analysis

### 1. `RESEARCH_harness_agentic_coding_builder_research_and_framework.md` (and `..._B.md`)
- **Focus / Scope:** Comprehensive SOTA Survey on Agentic Coding Harnesses (Terminal-Bench 2.0/2.1, Lego-RL, SWE-bench Verified).
- **Core Thesis:**  
  > *"Model is cognitive capacity; Agent is an iterative decision policy; Harness is the operating system that turns that policy into verifiable autonomous behavior."*
- **Key Technical Findings:**
  - **Harness Variance:** On Terminal-Bench 2.0 with the exact same base model (GPT-5.3-Codex), different harnesses vary from 64.7% (Terminus 2) to 78.4% (SageAgent) — proving the harness is a major independent variable.
  - **Lego-RL:** Training models inside real harnesses eliminates train-inference mismatch, yielding +6.4% on SWE-bench.
  - **Context Engineering Hierarchy:** Deterministic structural navigation (AST, symbols, call graphs, lexical search) must precede vector RAG and agentic exploration.
  - **Multi-Agent Restraint:** Single-agent execution with deterministic policy planes should be default; subagents are reserved for true isolation, parallelism, or verification.

---

### 2. `RESEARCH_Harness_Builder_Framework.md`
- **Focus / Scope:** Product Requirements Document (PRD) for an extensible Harness Builder framework.
- **Core Thesis:**  
  > *"Every box in the system is a plugin. Every plugin is replaceable. Every protocol is universal."*
- **Architecture Proposed:** Modular harness compilation from decoupled plugin adapters (`LLMAdapter`, `MemoryAdapter`, `ToolsAdapter`, `PromptEngine`, `CacheAdapter`) orchestrated over an event bus.

---

### 3. `RESEARCH_THEORETICAL_SYNTHESIS.md` (and `..._B.md`)
- **Focus / Scope:** Mathematical optimization models for Wave 6 / Milestone M5 (Meta-Cognition, Credit Assignment, Active Inference).
- **Core Formulations:**
  - **Sub-Horizon Fault Isolation:** Formulates Counterfactual Causal Credit $\mathcal{C}(a_t)$ across discrete action traces when terminal outcome $Y(\tau)=0$.
  - **Variational Free Energy Minimization:** Translates Friston's Active Inference into discrete parameter manifold mutations across the 6D resource lease tensor.
  - **Gated Trajectory DPO:** Direct Preference Optimization with cryptographic Ed25519 oracle gating on Chosen/Rejected pairs to prevent reward hacking.
  - **Elo-Decayed Skill Eviction:** Low-entropy procedural memory with dynamic eviction to prevent semantic collision and procedural amnesia.

---

### 4. `RESEARCH_k3_harness-suggestion.md`
- **Focus / Scope:** SOTA Plan for AETHER (Staff Engineer / Principal Architect / Tech Lead advisory proposal).
- **Core Framework (The A-B-C-D Foundation):**
  - **A — Authority:** S0–S12 mediator, monotonic attenuation, 6D typed leases, fail-closed selectors ($\le 1438$ LOC TCB).
  - **B — Bundle / Composition:** Named Component Graph compiling into `FrozenHarness(D_H)`.
  - **C — Corpus:** SQLite WAL `fold(events)` emitting rich `mhf.trajectory/1` records with exact token costs and model fingerprints.
  - **D — Digest:** Measurement identity ($D_H \neq D_R \neq D_X$).
- **Key Diagnostic:** Identifies that **A and D are already generic in Vanguard, while B is template-shaped and C is hollow (`_ZERO_COST`)**. The plan orders making B and C generic without weakening A.

---

### 5. `proposal_glm_harness_BETA.md`
- **Focus / Scope:** Independent external GLM model assessment of the v0.6.1 trajectory.
- **Key Assessment:**
  - Validates that Vanguard's foundation (3 Planes, typed budget, WAL durability, external judge) is built correctly.
  - Confirms that the single highest-leverage immediate defect is the hollow trajectory cost (`_ZERO_COST` in `trajectory.py`), which would poison future RL/DPO training datasets if not fixed before Wave 4.
  - Recommends rebalancing Wave 3 around the component graph before moving to multi-agent emergence.

---

### 6. `RESEARCH_deepseek-harness_algorithms-ideas.md`
- **Focus / Scope:** Systematic reverse-engineering playbook and algorithmic ideas for Meta-Cognitive testing in isolated experiment directories.
- **Key Contributions:** Maps external AI harness architectures to Vanguard's port/plugin system, and proposes isolating PhD-level meta-cognitive algorithms under `experiments/` before graduating to production plugins.

---

### 7. `proposal_hy3_harness.md` & `proposal_hy3_improved.md`
- **Focus / Scope:** Early architectural proposals exploring the separation of substrate microkernels, declarative manifests, and dynamic execution adapters.

---

### 8. `vanguard_body_detailed.md`
- **Focus / Scope:** Comprehensive anatomical breakdown of Vanguard's internal package structure, dispatch loops, and module dependencies.

---

### 9. `openrouter_llm_models_suggested.md`
- **Focus / Scope:** Curated model selection guide for routing planners, fast tool-executors, and critic evaluators via OpenRouter.

---

## 3.2 Matrix: Research Framework vs. Vanguard Live Codebase

| Research Concept (06_references) | Vanguard As-Built Reality (`vanguard/`) | Alignment / Actionable Insight |
|---|---|---|
| **Lego-RL / Unforgeable Trajectories** | `vanguard/packages/runtime/trajectory.py` emits `mhf.trajectory/1`, but uses dummy `_ZERO_COST`. | **Critical alignment item:** Wire per-turn model token costs and fingerprints into `trajectory.py` (NOVA-1) before data harvesting. |
| **Separability Thesis (Independent Judge)** | `adapters/evaluators/daemon.py` (UID 10002) + `evaluator_gateway.py` enforce signed Ed25519 verdicts. | **100% Aligned:** Vanguard strictly realizes the Separability Thesis. |
| **Hierarchical Context Engineering** | `vanguard/packages/agency/context/compiler.py` implements AST-aware budgeting and structured compaction. | **Aligned:** Aligns with research findings that AST/symbol structures must precede vector search. |
| **A-B-C-D Substrate Model** | A (Kernel) & D (Identity) are generic; B (Compose) is fixed-slot; C (Trajectory) needs cost populating. | **Roadmap Blueprint:** Directly guides Wave 3 (Component Graph) and Wave 2 close (Trajectory Cost). |
| **Multi-Agent by Policy, Not Engine** | `Agent = Principal + HarnessInstance` in `agency/episode/engine.py`. | **100% Aligned:** Avoids building heavy swarm engines; swarm topologies are expressible via recursive delegation. |
| **Meta-Cognition / Active Inference (M5/M10)** | Deferred to Phase 2 (post-M-4). | **Correctly Staged:** Research provides the exact mathematical formulations (Friston variational free energy, DPO oracle gating) for when M-10 is entered. |

---

## 3.3 Conceptual Collisions & Points of Tension in the Literature

The reference corpus presents three healthy theoretical tensions for system design:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THEORETICAL TENSIONS IN RESEARCH                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. PLUG-EVERYTHING vs. UNFORGEABLE REFERENCE MONITOR:                       │
│    • Pure Plug (PRD): "Every box is a plugin; no privileged core."          │
│    • Vanguard Reality: Immutable, minimal TCB (<=1438 LOC) that mediates    │
│      capabilities and signs verdicts, with total pluggability above it.     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. NATURAL LANGUAGE SELF-REFLECTION vs. EXTERIOR GROUNDED ORACLES:          │
│    • Reflexion / Verbalization: Agent reflects in buffer (hallucinatory).   │
│    • Vanguard SOTA: Exterior Ed25519 signed verdicts with compiler/test     │
│      oracle receipts (unforgeable ground truth).                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. MULTI-AGENT SWARMS BY DEFAULT vs. RESTRAINED SINGLE-AGENT CONTEXT:       │
│    • Swarm Hype: Spawning 10 agents for simple tasks (token explosion).     │
│    • Vanguard Discipline: Single turn loop default; spawn only for true     │
│      context isolation, parallel subprocesses, or independent review.       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3.4 Advisory Summary for the Director

1. **Research Validates Vanguard's Architectural Choices**:
   * The literature (Lego-RL, Terminal-Bench 2.1) firmly establishes that the **harness architecture dominates model performance** and that external, unforgeable verification is essential.
2. **Immediate High-Leverage Fix**:
   * Populating real token costs and model metadata into `vanguard/packages/runtime/trajectory.py` (NOVA-1) is the single most important task before running production episodes, ensuring the training corpus is never born hollow.
3. **Wave 3 Component Graph is the Bridge to Full Generality**:
   * Evolving `harness.yaml` into a **Named Component Graph** will fulfill the research vision of expressing debate, critic loops, and tree search without touching the microkernel.

---
*(End of Step 3. Step 4 will synthesize all findings into a unified executive index for Wave 3+ and v0.7.0 upon Director confirmation.)*
