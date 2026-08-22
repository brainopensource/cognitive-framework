# Macro Roadmap & Milestone Ladders: LED (LLM Engine Desktop)

**Document Code:** `ROADMAP-LED-2026-V1`  
**Classification:** Strategic Planning & Milestone Ladders  
**Subject:** 6 Macro Milestones (M-0 to M-5), Sprints 0–9, Story Point Allocation (81 SP Total), and Release Exit Criteria.

---

## 1. Macro Milestone Timeline (M-0 to M-5)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 LED MACRO MILESTONE LADDER                             │
│                                                                                        │
│  [M-0] Mathematical & DoE Validation (Python Prototype)            [IN FLIGHT / TODAY] │
│   │                                                                                    │
│  [M-1] Rust Engine Core & llama.cpp FFI Supervisor                 [SPRINT 1-2]        │
│   │                                                                                    │
│  [M-2] Go / Wails Desktop Studio GUI (Chat & Code)                 [SPRINT 3-4]        │
│   │                                                                                    │
│  [M-3] Native Bench Lab & AST Evaluator Tab                        [SPRINT 5-6]        │
│   │                                                                                    │
│  [M-4] AI Auto-Tuner & Surrogate ML Optimization                   [SPRINT 7-8]        │
│   │                                                                                    │
│  [M-5] Production Release & Native Packaging ($1M Milestone)       [SPRINT 9]          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Milestone Breakdown & Exit Criteria

### Milestone M-0: Mathematical & DoE Validation (Python Prototype)
* **Goal:** Verify that 16-run Fractional Factorial DoE and Scikit-Learn Gradient Boosting identify the empirical Pareto Sweet Spot on local hardware.
* **Scope:** `matrix_execution/bench_matrix_16.py`, `train_surrogate.py`, `validate_sweet_spot.py`.
* **Exit Criteria:**
  * 16 runs complete sequentially on `qwen2.5:1.5b` and `qwen2.5-coder:14b`.
  * Surrogate regressor predicts latency with $\Delta < 15\%$ error margin against real validation run.

### Milestone M-1: Rust Engine Core & `llama.cpp` Supervisor
* **Goal:** Build the ultra-lightweight C++ / Rust backend server (`led-engine-core`).
* **Scope:** Axum HTTP server, SSE token streaming, process supervisor, and OpenAI proxy (`/v1`).
* **Exit Criteria:**
  * Rust memory footprint $< 10\text{ MB}$.
  * Token streaming latency jitter $P_{99} < 10\text{ ms}$.

### Milestone M-2: Go / Wails Desktop Studio GUI
* **Goal:** Build the native desktop window and Chat/Code playground.
* **Scope:** Wails v2 + HTML/Tailwind frontend, model explorer, VRAM visualizer, and system tray.
* **Exit Criteria:**
  * App cold-start time $< 0.2\text{ seconds}$.
  * Total UI RAM usage $< 30\text{ MB}$.

### Milestone M-3: Native Bench Lab Tab
* **Goal:** Embed the 1-click benchmarking engine directly inside the Go desktop UI.
* **Scope:** Real-time generation graphs, AST code score visualizer, and CSV/JSONL export.
* **Exit Criteria:**
  * 1-click benchmark execution with live progress bar and zero UI freezing.

### Milestone M-4: AI Auto-Tuner Tab
* **Goal:** Integrate on-device Scikit-Learn auto-tuning wizard.
* **Scope:** Parameter importance ranking (SHAP), Pareto frontier scatter plot, and 1-click "Apply Sweet Spot".
* **Exit Criteria:**
  * Auto-Tuning completes in $< 5\text{ minutes}$ on a 14B model.

### Milestone M-5: Production Release & Native Packaging
* **Goal:** Compile standalone installers for Windows 11 (`.exe` / `.msi`) and Linux (`.deb` / `.AppImage`).
* **Scope:** Code signing, auto-update mechanism, and documentation portal.
* **Exit Criteria:**
  * Clean standalone installation with zero external Python/C++ prerequisite dependencies.

---

## 3. Sprint Sequencing & Story Points Allocation

| Sprint | Milestone | Focus Area | Story Points | Duration | Status |
| :---: | :---: | :--- | :---: | :---: | :---: |
| **Sprint 0** | **M-0** | Python 16-Run DoE Matrix, AST Evaluator & Surrogate ML | **8 SP** | 1 Day | **Active** |
| **Sprint 1** | **M-1** | Rust Axum Server, Process Lifecycle & llama-server FFI | **13 SP** | 1 Week | Queued |
| **Sprint 2** | **M-1** | Zero-GIL SSE Streaming & OpenAI `/v1` Route Adapter | **8 SP** | 1 Week | Queued |
| **Sprint 3** | **M-2** | Go + Wails Desktop Application Scaffolding & System Tray | **13 SP** | 1 Week | Queued |
| **Sprint 4** | **M-2** | Chat & Code Studio UI with Syntax Highlighting | **8 SP** | 1 Week | Queued |
| **Sprint 5** | **M-3** | Native Bench Lab Tab & Real-Time Telemetry Streaming | **8 SP** | 1 Week | Queued |
| **Sprint 6** | **M-3** | Automated AST Code Scorer & Dataset Exporter | **5 SP** | 1 Week | Queued |
| **Sprint 7** | **M-4** | Scikit-Learn Surrogate Worker Subprocess Integration | **8 SP** | 1 Week | Queued |
| **Sprint 8** | **M-4** | 1-Click Hardware Auto-Tuner & Modelfile Exporter | **5 SP** | 1 Week | Queued |
| **Sprint 9** | **M-5** | Production Windows/Linux Installers & Polish | **5 SP** | 1 Week | Queued |
| **TOTAL** | | **Full Product Backlog** | **86 SP** | | |
