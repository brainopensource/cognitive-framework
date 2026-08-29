---
id: product.frontend.lab
class: product
authority: proposal
canonical_for:
  - aether-lab-product-requirements
  - internal-inspection-and-debugging-tools
status: proposed
owner: product-architecture
version: "0.1.0"
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
| **View Architecture** | 22 disparate exploratory views in `vanguard/clients/studio/src/ui/` with speculative features. | 5 focused, high-value workbenches built with **SolidJS** and lazy-loaded on demand. | Consolidate 22 views down to 5 precision workbenches; archive speculative screens. |
| **State Infrastructure** | Ad-hoc store in `vanguard/clients/studio/src/store/` maintaining custom state copies. | 100% reuse of `@aether/client` and `@aether/projections` with zero duplicate reducers. | Delete redundant UI state models; bind views directly to shared projection signals. |
| **Graph Rendering** | Experimental React Flow and manual DOM layout in `LineageGraphView.tsx`. | Lightweight SVG/Canvas DAG renderer for human-scale traces, lazy-loaded on demand. | Implement zero-dependency SVG DAG renderer with layout computed in Web Workers. |
| **Analytical Querying** | Speculative DuckDB-Wasm plans without bounded memory controls. | Standard cursor-paginated SQLite event streaming; optional client-side export for analytical tools. | Focus initial Lab strictly on live ledger streaming and historical replay. |

---

## 3. Users & Jobs-to-be-Done

- **Kernel & Agency Subsystem Engineers**:
  - Trace individual effect requests through the S0–S12 kernel dispatch pipeline.
  - Verify capability grant attenuation across recursive child agent spawns.
  - Audit budget lease reservations, commits, and releases.
- **Context & Model Alignment Engineers**:
  - Inspect prompt layer assembly (L1 System, L2 Memory, L3 Tools, L4 History, L5 Retrieved Artifacts).
  - Observe context compaction triggers and token reduction ratios.
- **Evaluation & Benchmark Researchers**:
  - Run side-by-side comparisons of two agent harnesses over identical benchmark task seeds.
  - Detect exact divergence points in execution trajectories and verify signed exterior evaluator verdicts.

---

## 4. Information Architecture & Focused Workbenches

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ AETHER LAB │ Run: run-018f-9a4b ▾ │ Seq: 184/184 │ Health: LIVE (0 drops) │ Mode: LIVE TAIL │
├───────────┬──────────────────────────────────────────────────────────────────────────────────┤
│ WORKBENCH │ KERNEL DISPATCH MICROSCOPE (S0–S12)                                              │
│           │                                                                                  │
│ [•] Runs  │ Effect: fs.patch (descriptor: sha256:desc_fs_patch_dispatch)                     │
│ [ ] Trace │ ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌──────┐   ┌─────┐   ┌─────┐ │
│ [ ] Ledger│ │ S0  ├──►│ S1  ├──►│ S2  ├──►│ S3  ├──►│ S4  ├──►│ S8a  ├──►│ S10 ├──►│ S12 │ │
│ [•] Kernel│ │Obsrv│   │Class│   │Grant│   │Lease│   │Apprv│   │Intent│   │Exec │   │Recon│ │
│ [ ] Ctxt  │ └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └──────┘   └─────┘   └─────┘ │
│ [ ] Eval  │                                                                                  │
│           │ Status: SETTLED (18ms) │ Grant: grant-018f (fs:write:kernel/*)                   │
│           │ Lease: lease-88b ($0.002 reserved, $0.0018 committed, $0.0002 released)         │
│           │ Signed Decision: reviewer:operator:local key:web-key-01 verdict:APPROVED        │
│           ├──────────────────────────────────────────────────────────────────────────────────┤
│           │ VIRTUALIZED EVENT LEDGER                                                         │
│           │ SEQ   TIMESTAMP    EVENT KIND           PRINCIPAL   STATUS     DURATION          │
│           │ 180   20:15:10.102 OperatorInvoked      operator    satisfied  12ms              │
│           │ 181   20:15:10.114 ApprovalRequested    operator    pending    --                │
│           │ 182   20:15:12.440 ApprovalResolved     operator    approved   --                │
│           │ 183   20:15:12.445 EffectStarted        operator    running    --                │
│           │ 184   20:15:12.463 EffectCompleted      operator    satisfied  18ms              │
└───────────┴──────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Workbench 1: Virtualized Event Ledger Tailer

- **High-Throughput Table**: Renders raw `EventEnvelope` streams with zero dropped frames.
- **Filter Presets**: One-click filters for Errors, Approvals, Kernel Denials, Tool Effects, and Budget Commits.
- **Payload Inspector**: JSON tree viewer showing exact canonical payload fields with copy-to-clipboard functionality.

### 4.2 Workbench 2: Causal Trace & Provenance Explorer

- **Causal DAG**: Renders causal relationships linking Goals -> Context Compilations -> Model Proposals -> Kernel Grants -> Effects -> Artifacts.
- **Node Inspector**: Clicking any node filters the event ledger to that exact span and displays associated duration, token cost, and outcome.

### 4.3 Workbench 3: Kernel Dispatch Microscope

- **S0–S12 Pipeline Stepper**: Visualizes the 13 dispatch stages for any selected effect descriptor.
- **Security & Budget Audit**: Inspects matched capability grant, budget lease reservation vs actual settlement, policy evaluation verdict, and signed approval challenge.

### 4.4 Workbench 4: Context & Compaction Inspector

- **Context Stack Visualization**: Color-coded breakdown of active tokens across context layers (System, Memory, Tools, History, Artifacts).
- **Compaction Diff**: Before-and-after view of context compaction events showing pruned spans and summary insertions.

### 4.5 Workbench 5: Paired Harness Comparison

- **Synchronized Replay**: Loads two recorded runs side-by-side over identical task prompts.
- **Divergence Detection**: Highlights the exact sequence number where harness decisions, tool calls, or model outputs diverged.

---

## 5. Technology Stack & Extreme Lightness

- **Frontend Core**: SolidJS + TypeScript + Vite + Bun.
- **Zero Heavy Dependencies**:
  - NO heavy chart libraries by default; simple SVG sparklines and bar graphs.
  - NO complex external state managers; uses pure SolidJS signals connected to `@aether/projections`.
  - Lazy loading for all workbench modules (only the active workbench is loaded into memory).

---

## 6. Non-Functional & Performance Budgets

- **Initial Bundle Size**: $<300\text{ KB}$ minified and compressed.
- **Cold Boot to Interactive**: $<600\text{ ms}$ in standard web browsers.
- **Virtual Table Performance**: Smooth 60 fps scrolling over 100,000 events using DOM row virtualization ($<150$ DOM nodes rendered simultaneously).
- **Memory Footprint**: Total tab heap memory $<100\text{ MB}$ for active debugging sessions.

---

## 7. Non-Goals & Out-of-Scope Boundaries

- **NON-GOAL 1**: Lab is NOT an IDE and MUST NOT contain code editors or terminal emulators.
- **NON-GOAL 2**: Lab MUST NOT implement an alternative backend simulation loop.
- **NON-GOAL 3**: Lab MUST NOT expose mutating administrative endpoints that bypass runtime authorization.

---

## 8. Deferred Documentation & Canonical References

- **Future Architecture Owner**: `docs/architecture/frontend/lab-inspection-architecture.md`
- **Future Reference Owner**: `docs/reference/frontend/lab-workbenches.md`
- **Future Decisions Owner**: `docs/decisions/frontend/0111-lab-minimal-companion-scope.md`
- **Future Execution Owner**: `docs/execution/frontend/lab-backlog.md`
