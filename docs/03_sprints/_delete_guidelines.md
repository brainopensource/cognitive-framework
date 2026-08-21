# Master Audit, Architectural Review & Concept Consolidation Index

**Target Milestone:** Intermediary Sprint (Preparation for v0.6.1, v0.6.2, and v0.7.0)  
**Classification:** Neutral Architectural & Concept Audit for Director Review  
**Audience:** Director / System Architect  
**Status:** In Progress (Step 1: Vanguard Codebase Reality vs. Normative Law)  

> [!IMPORTANT]
> **Advisory Disclaimer for the Director:**  
> This document is a factual, unbiased system engineering and concept review. It audits the live implementation in `vanguard/`, compares it with the normative law in [`docs/SPEC.md`](../SPEC.md), and catalogues all reviews and reference frameworks. It does **not** make executive decisions or declare product policies; all strategic decisions and wave authorizations remain exclusively with the Director.

---

## Document Index & Audit Phasing Plan

To prevent context noise and ensure rigorous verification, this consolidation is executed in ordered steps:
- **Step 1 [CURRENT]: Vanguard Implementation Reality (`vanguard/`) vs. Normative Law ([`docs/SPEC.md`](../SPEC.md))**
- **Step 2 [QUEUED]: Forensic & Review Documents Audit ([`docs/07_reviews/`](../07_reviews/))**
- **Step 3 [QUEUED]: Research & Framework References Audit ([`docs/06_references/`](../06_references/))**
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
*(End of Step 1. Step 2 will review and catalogue all files in `docs/07_reviews/` upon Director confirmation.)*
