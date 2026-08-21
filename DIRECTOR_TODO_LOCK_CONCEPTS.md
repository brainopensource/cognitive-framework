# Executive Briefing & Concept Lock Mandate

**Target:** Engineering Director / Chief Architect  
**Objective:** Comprehensive System Audit, Concept Reconciliation, and Strategic Version Lock (v0.6.1 / v0.6.2 $\to$ v0.7.0)  
**Date:** 2026-08-21  
**Status:** Ready for Director Review & Decision  

---

## 1. Executive Mandate & Instructions for the Director

> [!IMPORTANT]
> **DIRECTOR ACTION MANDATE:**  
> You are tasked with performing an independent, authoritative audit of the entire Vanguard / AETHER substrate across its **code**, **specifications**, **reviews**, and **theoretical research**.  
> 
> You hold **full decision authority** to decide all architectural parameters, roadmap milestones, and conceptual locks for the next versions (**v0.6.1**, **v0.6.2**, and **v0.7.0**). The review documents in [`docs/07_reviews/`](docs/07_reviews/) and research papers in [`docs/06_references/`](docs/06_references/) serve as historical evidence, advisory proposals, and options—**not unquestioned law**. You will review the trade-offs, reconcile competing ideas, and formalize the next locked architecture via append-only ADRs.

### Your Audit Objectives:
1. **Audit Live Code Reality vs. Law:** Review the hexagonal lattice in [`vanguard/packages/`](vanguard/packages/) against [`docs/SPEC.md`](docs/SPEC.md).
2. **Adjudicate Open Concept Tensions:**
   - *Manifest Shape:* Fixed 5-slot template vs. Dynamic **Named Component Graph** ([`005_V061_SUBSTRATE_GENERALITY_REVIEW.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md) §3.1).
   - *Spawning:* In-engine execution vs. Capability-mediated `agent.spawn` tool verb ([`005`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md) §3.2).
   - *Guardrails:* Mandatory UID 10002 daemon vs. Declarative "Absent-vs-Forged" model ([`005`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md) §3.4).
   - *Trajectory Dataset:* Populating real token costs and model metadata into [`trajectory.py`](vanguard/packages/runtime/trajectory.py) (Gap G1 / NOVA-1) to un-hollow the training corpus.
3. **Establish Version Milestones:** Finalize the roadmap ladder across Waves 2 through 10 in [`docs/02_roadmap/milestones.md`](docs/02_roadmap/milestones.md) and the living sprint board in [`docs/03_sprints/sprint_active.md`](docs/03_sprints/sprint_active.md).

---

## 2. High-Level Mental Model & Core Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             THE CLEAN TRIAD                                 │
│                                                                             │
│  1. THE LAW (WHAT)        ──► docs/SPEC.md (+ docs/04_annex/)               │
│  2. THE DECISIONS (WHY)   ──► docs/05_adr/ (Immutable, append-only records) │
│  3. THE EXECUTION (HOW)   ──► docs/03_sprints/sprint_active.md & 02_roadmap │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Three Planes of Responsibility
1. **Decision Plane (Volatile / Reconstructible):** Governed by the S0–S12 Reference Monitor in [`kernel/`](vanguard/packages/kernel/). Mediates effects, monotonic capability attenuation, and 6D typed leases.
2. **State Plane (Immutable / Event-Sourced):** Governed by [`adapters/stores/event_store.py`](vanguard/packages/adapters/stores/event_store.py) (SQLite WAL `PRAGMA journal_mode = WAL`). `State = fold(events)` reconstructible cold from disk.
3. **Evidence Plane (Exterior / Unreachable):** Governed by [`adapters/evaluators/daemon.py`](vanguard/packages/adapters/evaluators/daemon.py) (UID 10002). Emits Ed25519-signed verdicts bound to request nonces.

### The A-B-C-D Operating Foundation
* **A — Authority (Kernel):** Descriptor-bound grants, monotonic attenuation, typed 6D budgets ($\le 1438$ LOC TCB). *Status: Solid & Generic.*
* **B — Bundle (Composition):** Manifest $\to$ `FrozenHarness(D_H)` compiler. *Status: Currently a fixed-slot template; evolving to a Component Graph.*
* **C — Corpus (Evidence):** SQLite WAL `fold(events)` emitting `mhf.trajectory/1`. *Status: Schema-valid, but requires non-zero cost wiring.*
* **D — Digest (Identity):** Cryptographic identity trinity ($D_H \neq D_R \neq D_X$). *Status: Locked & Generic.*

---

## 3. Complete Repository Map & File Index

```text
/
├── vanguard/                     # CANONICAL PRODUCTION CODEBASE
│   ├── packages/                 # Hexagonal production lattice
│   │   ├── domain/               # Pure value objects, JCS, ledger events, wire models
│   │   ├── ports/                # Hexagonal port protocols & 5 SPI interfaces
│   │   ├── kernel/               # Trusted Computing Base (1365 LOC, limit <=1438)
│   │   ├── agency/               # Recursive turn engine, context compiler, compaction
│   │   ├── runtime/              # Composition, session, governance, emitter, trajectory
│   │   ├── adapters/             # Models, evaluator daemon, bwrap sandbox, SQLite WAL
│   │   └── apps/                 # Reserved boundary-lattice slot
│   └── clients/                  # Client applications
│       └── cli/                  # Interactive TypeScript + Ink CLI (vg)
│
├── benchmarks/                   # UNIFIED BENCHMARK FRAMEWORK (3 Core Suites)
│   ├── swe_bench/                # Real-world GitHub issue resolution
│   ├── greenfield/               # Red-to-green API & webapp construction tasks
│   ├── datalog_engine/           # Frontier deductive query engine solver
│   ├── run.py / bench.py / ...   # Unified benchmark harness & diff tools
│   └── README.md                 # Benchmark suite documentation
│
├── layer0/                       # CONVERGENCE COPY-FORK (Awaiting Wave 3)
│   ├── registry/                 # Plugin lifecycle FSM (To be absorbed into packages)
│   ├── compose/                  # Manifest compiler (To be absorbed into packages)
│   └── README.md                 # Convergence instructions & absorption map
│
├── tools/                        # SYSTEM TOOLS & ARCHITECTURAL LINTERS
│   ├── linters/                  # 8 Active CI Linters (Boundaries, TCB, I-7, I-6, etc.)
│   ├── common/                   # Shared path resolvers (repo_paths.py, simple_yaml.py)
│   ├── codegen/                  # Type generator from JSON Schemas (generate_types.py)
│   ├── telemetry/                # Metrics and trace collection tools
│   ├── substrate_visualizer/     # Provenance DAG visualizer
│   ├── 001_LLM_API_ROUTER/       # LLM router testing project (LAR)
│   └── 002_LLM_API_MOCK/         # LLM mock server project (LAM)
│
├── test/                         # COMPREHENSIVE TEST SUITE (434 Tests 100% Green)
│   ├── kernel/                   # Core TCB dispatch and attenuation tests
│   ├── contracts/                # Hexagonal SPI and wire contract tests
│   ├── agency/                   # Recursive turn loop & context tests
│   ├── packs/                    # Domain pack & capability selector tests
│   ├── runtime/                  # Session, emitter, and cold-replay tests
│   ├── adapters/                 # Model, sandbox, and evaluator tests
│   ├── falsifiers/               # Bound falsifiers F-01 through F-21
│   ├── security/ & trust/        # Sandbox and cryptographic verification tests
│   └── broken/                   # Negative test harness with planted defect fixtures
│
├── docs/                         # CANONICAL DOCUMENTATION HIERARCHY
│   ├── SPEC.md                   # Normative RFC-2119 Specification (The Law)
│   ├── 02_roadmap/               # Macro Milestones ladder (milestones.md, backlog.md)
│   ├── 03_sprints/               # Living Sprint Board (sprint_active.md)
│   ├── 04_annex/                 # Normative Annexes (KERNEL.md, MEASUREMENT.md)
│   ├── 05_adr/                   # Architecture Decision Records (0000..0076, INDEX.md)
│   ├── 06_references/            # Research Papers & Framework Literature (12 docs)
│   └── 07_reviews/               # Forensic Audits & Advisory Reviews (8 docs)
│
├── README.md                     # Primary repository navigation map
├── AGENTS.md                     # Contributor & Agent guidelines (Anti-Sprawl Rule)
└── pyproject.toml                # Python package configuration (vanguard-runtime)
```

---

## 4. Production Subsystem Inventory (`vanguard/packages/`)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HEXAGONAL PRODUCTION LATTICE                         │
│                                                                             │
│  domain  ◄──  ports  ◄──  kernel  ◄──  agency  ◄──  runtime  ──►  adapters  │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Package | Path | File Count / LOC | Key Modules & Responsibilities |
|---|---|---|---|
| **Domain** | [`vanguard/packages/domain/`](vanguard/packages/domain/) | 13 files | • [`jcs.py`](vanguard/packages/domain/ledger/jcs.py): RFC 8785 canonicalizer.<br>• [`events.py`](vanguard/packages/domain/ledger/events.py): Canonical catalog of 30+ event kinds.<br>• [`reducer.py`](vanguard/packages/domain/ledger/reducer.py): Deterministic `fold(events) $\to$ State`.<br>• [`resource_selector.py`](vanguard/packages/domain/selectors/resource_selector.py): Total, fail-closed capability algebra.<br>• [`wire/jsonrpc.py`](vanguard/packages/domain/wire/jsonrpc.py): JSON-RPC 2.0 wire codec. |
| **Ports** | [`vanguard/packages/ports/`](vanguard/packages/ports/) | 10 files | • [`spi.py`](vanguard/packages/ports/spi.py): The 5 extensible SPI protocols (`PluginHost`, `ToolPlugin`, `ModelProvider`, `EvaluatorPlugin`, `PolicyPlugin`).<br>• [`kernel.py`](vanguard/packages/ports/kernel.py), [`sandbox.py`](vanguard/packages/ports/sandbox.py), [`evaluator.py`](vanguard/packages/ports/evaluator.py), [`event_store.py`](vanguard/packages/ports/event_store.py). |
| **Kernel** | [`vanguard/packages/kernel/`](vanguard/packages/kernel/) | 9 files<br>(1,365 LOC) | • **TCB Limit: $\le 1438$ LOC (Currently 1365 LOC).**<br>• [`dispatch.py`](vanguard/packages/kernel/dispatch.py): S0–S12 13-stage dispatch pipeline.<br>• [`attenuation.py`](vanguard/packages/kernel/attenuation.py): Monotonic capability attenuation.<br>• [`budget.py`](vanguard/packages/kernel/budget.py): 6D typed lease arithmetic.<br>• [`grants.py`](vanguard/packages/kernel/grants.py): Descriptor-bound capability grants. |
| **Agency** | [`vanguard/packages/agency/`](vanguard/packages/agency/) | 10 files | • [`engine.py`](vanguard/packages/agency/episode/engine.py): `EpisodeEngine` turn loop & subagent `spawn()`.<br>• [`compiler.py`](vanguard/packages/agency/context/compiler.py): Token budgeting, context compilation, structured compaction.<br>• [`manifests/`](vanguard/packages/agency/manifests/): Pack manifests and gene digests. |
| **Runtime** | [`vanguard/packages/runtime/`](vanguard/packages/runtime/) | 18 files | • [`compose.py`](vanguard/packages/runtime/compose.py): Harness composition.<br>• [`session.py`](vanguard/packages/runtime/session.py): Session lifecycle runner.<br>• [`ledger_emitter.py`](vanguard/packages/runtime/ledger_emitter.py): Single authorized ledger writer.<br>• [`evaluator_gateway.py`](vanguard/packages/runtime/evaluator_gateway.py): Signed exterior verdict client.<br>• [`trajectory.py`](vanguard/packages/runtime/trajectory.py): `mhf.trajectory/1` builder.<br>• [`governance/`](vanguard/packages/runtime/governance/): Ed25519 cryptographic approvals. |
| **Adapters** | [`vanguard/packages/adapters/`](vanguard/packages/adapters/) | 14 files | • [`models/`](vanguard/packages/adapters/models/): OpenRouter, Ollama, Cassette, Fake adapters.<br>• [`evaluators/daemon.py`](vanguard/packages/adapters/evaluators/daemon.py): UID 10002 external evaluation daemon.<br>• [`sandbox/bwrap.py`](vanguard/packages/adapters/sandbox/bwrap.py): UID 10001 rootless bubblewrap sandbox.<br>• [`stores/event_store.py`](vanguard/packages/adapters/stores/event_store.py): SQLite WAL event store. |
| **CLI** | [`vanguard/clients/cli/`](vanguard/clients/cli/) | TypeScript | • Interactive TUI (`vg`) in React/Ink connecting via streaming JSON-RPC. |

---

## 5. Normative Law & Architecture Decisions Summary

### 5.1 The Law: [`docs/SPEC.md`](docs/SPEC.md)
* **A-1 Microkernel:** Layer 0 provides state, dispatch, lifecycle, and scheduler ($\le 1438$ LOC TCB).
* **A-2 Two Authority Systems:** Broker grants capabilities to agents; sandbox contains plugin processes.
* **A-3 Event-Sourced:** Everything is an event. Replay is a required, CI-tested property.
* **A-4 Single Source Schema:** JSON Schema + JCS canonicalization generates all wire dataclasses and TS readers.
* **A-5 Content-Addressed Identity:** $D_H$ (manifest) $\neq D_R$ (run) $\neq D_X$ (experiment).
* **§1.6 Separability Thesis:** Grader cannot be read, patched, or reasoned about by the graded entity.
* **§9 Refusals:** Substrate explicitly refuses in-process fake passes, GUI backend couplings, continuous un-promoted self-updates, and graph database engines.

### 5.2 Key Architecture Decision Records ([`docs/05_adr/`](docs/05_adr/))
* [**ADR-0069**](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md): Python-first core; `vanguard/packages/` canonical; `layer0/` is absorbed, not a rewrite target; Rust rewrite rejected.
* [**ADR-0070**](docs/05_adr/0070-agent-identity-principal-and-harness.md): `Agent = Principal + HarnessInstance`; `spawn` is the sole delegation primitive; subagent is a `Principal` with `parent_id`.
* [**ADR-0071**](docs/05_adr/0071-three-plane-architecture-identity-trinity-replay-taxonomy.md): Decision/State/Evidence planes; $D_H / D_R / D_X$ separation; strict replay taxonomy (cold fold from disk).
* [**ADR-0072**](docs/05_adr/0072-plugin-architecture-wire-first-exterior-evaluation.md): Wire-first plugins over UDS/JSON-RPC; exterior evaluation daemon (UID 10002).
* [**ADR-0073**](docs/05_adr/0073-v060-lock-vs-defer.md): Explicit partition of locked vs. deferred vs. rejected capabilities.
* [**ADR-0074**](docs/05_adr/0074-v060-concept-lock-strengthening-amendments.md): 6D typed budget algebra (`usd_micros`, `tokens`, `bytes`, `millis`, `depth`, `turns`); writer authority rules.
* [**ADR-0075**](docs/05_adr/0075-director-review-v060-approved-wave0-authorized.md): Director approval of Concept Lock GAMMA; authorization of Wave 0.
* [**ADR-0076**](docs/05_adr/0076-foundation-execution-decisions-canonical-artifacts.md): Foundation execution decisions; canonical selector algebra and event catalog.

---

## 6. Review & Reference Corpus Index

### 6.1 Audit & Review Corpus ([`docs/07_reviews/`](docs/07_reviews/))
* [`VANGUARD_V060_FORENSIC_DISCOVERY.md`](docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md): Comprehensive investigation exposing the dual runtime and fake scheduler passes.
* [`001_V060_concept_phase_GAMMA.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md): Approved concept lock plan uniting the 12 P0 decisions.
* [`002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md): Falsifiers register (F-01..F-21) and foundation wave gates.
* [`003_V060_DIRECTOR_REVIEW.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_DIRECTOR_REVIEW.md): Formal Director approval verdict with findings F-18..F-21.
* [`004_V061_ALIGNMENT_ROADMAP.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/004_V061_ALIGNMENT_ROADMAP.md): Post-foundation macro milestone staging (M-5 through M-10).
* [`005_V061_SUBSTRATE_GENERALITY_REVIEW.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md): Substrate generality audit defining the Component Graph and mediated spawning.
* [`006_V061_aether-substrate-briefing.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/006_V061_aether-substrate-briefing.md): Theoretical briefing on composite agentic substrates and the Separability Thesis.

### 6.2 Research & Theoretical References ([`docs/06_references/`](docs/06_references/))
* [`RESEARCH_harness_agentic_coding_builder_research_and_framework.md`](docs/06_references/RESEARCH_harness_agentic_coding_builder_research_and_framework.md): SOTA survey (Terminal-Bench 2.1, Lego-RL, context engineering hierarchy).
* [`RESEARCH_k3_harness-suggestion.md`](docs/06_references/RESEARCH_k3_harness-suggestion.md): SOTA Plan for AETHER formulating the A-B-C-D operating foundation.
* [`RESEARCH_THEORETICAL_SYNTHESIS.md`](docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS.md): First-principles math for credit assignment, active inference, and gated DPO.
* [`proposal_glm_harness_BETA.md`](docs/06_references/proposal_glm_harness_BETA.md): External GLM evaluation diagnosing trajectory cost gaps.
* [`RESEARCH_Harness_Builder_Framework.md`](docs/06_references/RESEARCH_Harness_Builder_Framework.md): Product PRD for universal plugin composition.
* [`RESEARCH_deepseek-harness_algorithms-ideas.md`](docs/06_references/RESEARCH_deepseek-harness_algorithms-ideas.md): Reverse-engineering playbook and PhD experiment sandbox structure.

---

## 7. Strategic Macro Milestones Ladder (M-0 to M-10)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MACRO MILESTONE LADDER                             │
│                                                                             │
│  [FOUNDATION PHASE]                                                         │
│   • M-0 (Wave 0): CI Truth & Named Falsifiers                [COMPLETE]     │
│   • M-1 (Wave 1): Fail-Closed Trust Spine & Emitter          [GREEN/LOCKED] │
│   • M-2 (Wave 2): In-Place Lattice Convergence               [IN FLIGHT]    │
│   • M-3 (Wave 3): Extensibility & Component Graph Skeleton   [QUEUED]       │
│   • M-4 (Wave 4): First Real Coding-Agent E2E (STOP LINE)    [QUEUED]       │
│                                                                             │
│  [MACRO GENERALITY & EMERGENCE PHASE (POST-M-4)]                            │
│   • M-5: Post-Foundation Consolidation & Non-Coding Pack #2                 │
│   • M-6: Mediated agent.spawn & Hierarchical Decomposition / Tree Search    │
│   • M-7: Concurrency at Scale (Gated on Suspend/Resume Falsifier)           │
│   • M-8: Multi-Agent Composition Graphs (Debate, Critic Loops, Swarms)      │
│   • M-9: High-Performance Logical Agent Orchestration                       │
│   • M-10: Meta-Cognitive Substrate (Skill Synthesis, DPO Harvest, RL)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Director Decision & Review Checklist

Use this checklist to record your final determinations for the next version:

- [ ] **1. Trajectory Telemetry (NOVA-1):** Authorize populating real token costs and model fingerprints into [`trajectory.py`](vanguard/packages/runtime/trajectory.py).
- [ ] **2. Harness Composition Schema:** Authorize evolving `harness.yaml` into a **Named Component Graph** (Wave 3 / ADR-0077).
- [ ] **3. Guardrail Declaration Model:** Authorize the "Absent-vs-Forged" guardrail model for non-coding packs.
- [ ] **4. `agent.spawn` Verb:** Confirm `agent.spawn` remains *Design Only* during Waves 1–4, and authorize implementation post-M-4.
- [ ] **5. Layer-0 Retirement Timing:** Confirm `layer0/registry/` and `layer0/compose/` will be absorbed into `vanguard/packages/runtime/` during Wave 3 before `layer0/` is deleted.
- [ ] **6. Version Nomenclature:** Authorize version release milestones (e.g. v0.6.1 Substrate Correction Lock $\to$ v0.6.2 Extensibility $\to$ v0.7.0 Foundation Stop).
