# Phase 3 Master Architectural Blueprint: Sprints 7 to 10 (v0.4.1 Release)

**Document Version:** 1.0.0  
**Date:** 2026-08-16  
**Target Release Tag:** `v0.4.1` (*Aether Beta MVP Cognitive Tools Vanguard Update*)  
**Scope:** Theory, Architecture, Methodologies, and Implementation Steps for Sprints 7, 8, 9, and 10.

---

## 1. Core Methodological Invariants

1. **Decoupled Architecture:** Core engine modules (`vanguard/packages/`) must remain clean, modular, and fully testable without requiring hardcoded third-party model bindings.
2. **Zero-Hint Honest Benchmarking:** All evaluations enforce zero prompt data leakage. Agents receive issue descriptions and pytest failure stack traces, never code solution hints.
3. **Stateless Replay & Telemetry:** All harness runs log full telemetry into `lam.sqlite` (CEI, FPSR, HOR, wall latency, token cost).

---

## 2. Sprint Roadmap Breakdown

### **Sprint 7: Harness Manifest Builder Framework**
- **Objective:** Build declarative JSON/YAML manifest compilation system to synthesize agentic harness environments.
- **Hierarchy:**
  - **Atom:** Primitives (`view_file`, `edit_file`, `run_command`).
  - **Molecule:** Task workspace + test suite.
  - **Cell:** Agent execution context & memory window.
  - **Body:** Multi-cell agent body with tool capabilities.
  - **Biome:** Full evaluation environment & isolated workspace.
- **Key Artifacts:** `vanguard/packages/manifests/builder.py`, `schemas/v4/harness_manifest.schema.json`.

### **Sprint 8: Coding Agent Harness CLI & TUI**
- **Objective:** Develop high-performance interactive CLI & Terminal User Interface (TUI) for running, stepping, and debugging agentic harness loops.
- **Key Commands:**
  - `agy harness run --manifest <file>`
  - `agy harness debug --scenario <id>`
  - `agy harness telemetry --db lam.sqlite`
- **Key Artifacts:** `vanguard/cli/harness.py`, `vanguard/tui/dashboard.py`.

### **Sprint 9: Meta-Harness Loop Engineering & Self-Correction**
- **Objective:** Implement autonomous context pruning, dynamic skill selection, and self-reflection loops.
- **Key Features:**
  - L1–L5 memory window compaction.
  - Autonomous retry on pytest failure with stack trace analysis.
  - Dynamic LAR routing escalation (`ollama` $\rightarrow$ `openrouter/free` $\rightarrow$ `openrouter/paid`).
- **Key Artifacts:** `vanguard/packages/runtime/loops/meta_loop.py`.

### **Sprint 10: Verification, Build Distribution & Release Shipment (v0.4.1)**
- **Objective:** Execute full E2E validation, package distribution binaries, and publish release tag `v0.4.1`.
- **Shipment Gate:**
  - 100% test suite pass rate across unit, integration, and E2E tiers.
  - Verification of `v0.4.1` release receipt.
  - Tag git repository: `v0.4.1`.
