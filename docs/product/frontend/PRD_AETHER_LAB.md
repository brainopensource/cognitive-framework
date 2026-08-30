---
id: product.frontend.lab
class: product
authority: proposal
canonical_for:
  - aether-lab-product-requirements
status: proposed
owner: product-architecture
version: "0.2.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/PRD_AETHER_LAB.md
subordinate_to:
  - product.frontend.platform
  - ../../SPEC.md
---

# Product Requirements Document: AETHER Lab (Development & Inspection Companion)

## 1. Executive Summary & Product Thesis

**AETHER Lab** is the internal development companion and scientific microscope for engineers building, operating, evaluating, and evolving the AETHER substrate.

### 1.1 Core Thesis

> **A precision development microscope, not a bloated telemetry wall. Lab contains zero unique state machinery and reuses 100% of the shared client substrate.**

### 1.2 The "Smallest Useful Lab" Principle

The purpose of Lab is strictly bounded: answer difficult engineering questions about active and historical runs that are tedious to diagnose from raw terminal logs. It is NOT an IDE, NOT an alternative desktop app, and NOT a permanent wall dashboard.

---

## 2. AS_BUILT vs. TARGET State Assessment

| Dimension | AS_BUILT (Repository Evidence) | TARGET (Electroweak Baseline) | Strategic Gap & Action |
|---|---|---|---|
| **View Architecture** | 22 disparate exploratory views in `vanguard/clients/studio/src/ui/` with speculative features. | Focused core inspection workbenches built with **SolidJS** and lazy-loaded on demand. | Consolidate views down to a focused core of precision inspection workbenches. |
| **State Infrastructure** | Ad-hoc store in `vanguard/clients/studio/src/store/` maintaining custom state copies. | 100% reuse of `@aether/client` and `@aether/projections` with zero duplicate reducers. | Delete redundant UI state models; bind views directly to shared projection signals. |
| **Graph Rendering** | Experimental React Flow and manual DOM layout in `LineageGraphView.tsx`. | Lightweight DAG visualization for human-scale traces, lazy-loaded on demand. | Adopt zero-overhead trace visualization that bounds DOM node count regardless of graph depth. |
| **Analytical Querying** | Speculative DuckDB-Wasm plans without bounded memory controls. | Cursor-resumable event streaming through the public `RuntimeService` gateway, backed by the canonical ledger. | Focus initial Lab strictly on live ledger streaming and historical replay via standard client SDK. |

---

## 3. Users & Jobs-to-be-Done

- **Kernel & Agency Subsystem Engineers**:
  - Trace execution lineage and verify capability grant attenuation across agent turns.
  - Inspect context compaction triggers, token reduction ratios, and assembled prompt layers.
  - Audit budget lease reservations, commits, and releases.
- **Evaluation & Benchmark Researchers**:
  - Inspect recorded execution trajectories and verify signed exterior evaluator verdicts.
  - Audit causal relationships between model proposals, tool effects, and resulting artifacts.

---

## 4. Information Architecture & Workbenches

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ AETHER LAB │ Run: run-018f-9a4b ▾ │ Seq: 184/184 │ Health: LIVE (0 drops) │ Mode: LIVE TAIL │
├───────────┬──────────────────────────────────────────────────────────────────────────────────┤
│ WORKBENCH │ VIRTUALIZED EVENT LEDGER                                                         │
│           │                                                                                  │
│ [•] Runs  │ Filters: [All] [Approvals] [Errors] [Effects] [Budget]      Search: [__________] │
│ [ ] Events│                                                                                  │
│ [ ] Trace │ SEQ   TIMESTAMP    EVENT KIND           PRINCIPAL   STATUS     DURATION          │
│ [ ] Arts  │ 180   20:15:10.102 OperatorInvoked      operator    satisfied  12ms              │
│ [ ] Ctxt  │ 181   20:15:10.114 ApprovalRequested    operator    pending    --                │
│ [ ] System│ 182   20:15:12.440 ApprovalResolved     operator    approved   --                │
│           │ 183   20:15:12.445 EffectStarted        operator    running    --                │
│           │ 184   20:15:12.463 EffectCompleted      operator    satisfied  18ms              │
│           ├──────────────────────────────────────────────────────────────────────────────────┤
│           │ EVENT PAYLOAD INSPECTOR (SEQ 182: ApprovalResolved)                              │
│           │ {                                                                                │
│           │   "approvalId": "approval-k06-patch",                                            │
│           │   "resolution": "approved",                                                      │
│           │   "reviewer": "operator:local",                                                  │
│           │   "signature": "ed25519:44a2b8e390c1f4..."                                       │
│           │ }                                                                                │
└───────────┴──────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Core Workbenches (Initial Release)

1. **Run Inspector (`/runs`)**: High-level run catalog, summary metrics (duration, tokens, cost, terminal verdict), and run attachment launcher.
2. **Virtualized Event Ledger (`/events`)**: High-throughput table rendering raw `EventEnvelope` streams with instant payload inspectors and filter presets (errors, approvals, effects, budget).
3. **Causal Trace Explorer (`/trace`)**: Lightweight DAG rendering causal relationships linking Goals -> Model Proposals -> Effects -> Artifacts.
4. **Artifact & Evidence Inspector (`/artifacts`)**: Content-addressed blob preview, hash verification, and evidence claim validation.
5. **Context Layer Inspector (`/context`)**: Breakdown of active token contributions across context layers (System, Memory, Tools, History, Retrieved Spans) and compaction diffs derived strictly from committed event facts.
6. **Subsystem & Capability Inspector (`/system`)**: Displays runtime health, active capability matrix (`/api/v1/capabilities`), and environment profile status.

### 4.2 Candidate Workbenches (Future Extensions)

- **Kernel Dispatch Microscope (S0–S12)**: Step-by-step inspector tracking individual effect descriptors across internal kernel stages (candidate for deep kernel debugging).
- **Paired Harness Comparison**: Side-by-side synchronized timeline comparing two agent harnesses over identical benchmark task seeds (candidate for M-7/M-8 evaluation).

---

## 5. Technology Stack & Lightweight Architecture

- **Frontend Core**: SolidJS + TypeScript + Vite + Bun.
- **Zero Heavy Dependencies**:
  - NO heavy external charting libraries by default; simple SVG sparklines and bar graphs.
  - NO complex external state managers; uses pure SolidJS signals connected to `@aether/projections`.
  - Lazy loading for all workbench modules (only the active workbench is loaded into memory).
- **Scalable Inspection Requirement**:
  - Inspection of 100k-event histories MUST remain responsive without requiring the entire event dataset or full trace graph to be mounted simultaneously in browser DOM memory.

---

## 6. Accessibility Requirements

- **Standard Compliance**: Target WCAG 2.2 Level AA compliance.
- **Keyboard Navigation**: Full keyboard operability across workbenches, event tables, and inspector drawers.
- **Screen Reader Support**: Accessible table structures with explicit headers, ARIA labels for payload inspectors, and semantic section headings.
- **Visual Ergonomics**: Support high-contrast dark/light modes; never rely on color alone for failure states; support reduced-motion settings.

---

## 7. Provisional Performance Targets

The following values represent **provisional engineering budgets (TARGET thresholds)** subject to verification via automated performance benchmarks on reference hardware:

- **Initial Bundle Size**: Target $<300\text{ KB}$ minified and compressed.
- **Cold Boot to Interactive**: Target $<600\text{ ms}$ in standard web browsers on reference hardware.
- **Virtual Table Performance**: Target smooth 60 fps scrolling over 100,000 events using DOM row virtualization.
- **Memory Footprint**: Target tab heap memory $<100\text{ MB}$ for active debugging sessions.

---

## 8. Non-Goals & Out-of-Scope Boundaries

- **NON-GOAL 1**: Lab is NOT an IDE and MUST NOT contain code editors or terminal emulators.
- **NON-GOAL 2**: Lab MUST NOT implement an alternative backend simulation loop.
- **NON-GOAL 3**: Lab MUST NOT expose mutating administrative endpoints that bypass runtime authorization.

---

## 9. Candidate Future Documents & Ownership References

- **Candidate Architecture Owner**: `docs/architecture/frontend/lab-inspection-architecture.md`
- **Candidate Reference Owner**: `docs/reference/frontend/lab-workbenches.md`
- **Candidate Decisions Owner**: `docs/decisions/frontend/adr-candidate-lab-minimal-scope.md`
- **Candidate Execution Owner**: `docs/execution/frontend/lab-backlog.md`
