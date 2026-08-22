# Sprint Task Register & Epics Backlog: LED (LLM Engine Desktop)

**Document Code:** `BACKLOG-LED-2026-V1`  
**Classification:** Granular Engineering Task Backlog  
**Subject:** 6 Epics, Granular Tasks (LED-001 to LED-105), Acceptance Criteria, and Definition of Done (DoD).

---

## 1. Definition of Done (DoD) Standard

A backlog task is strictly **DONE** when and only when:
1. **Code & Unit Tests:** Implementation is complete with unit/integration test coverage $\ge 85\%$.
2. **Hermeticity:** All tests run offline without external API dependencies or network calls.
3. **Documentation:** Public structs, functions, and interfaces contain complete docstrings and type annotations.
4. **Clean Builds:** Zero compiler warnings in Rust (`cargo clippy`), Go (`golangci-lint`), and Python (`ruff`).

---

## 2. Epics & Granular Task Breakdown

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LED EPICS REGISTRY                             │
│                                                                             │
│  EPIC 1: Mathematical Validation & DoE Prototyping        (LED-001 - 005)   │
│  EPIC 2: Rust Engine Core & C++ FFI Bridge                (LED-010 - 020)   │
│  EPIC 3: Go Desktop Studio UI (Wails v2)                  (LED-030 - 040)   │
│  EPIC 4: Native Bench Lab & AST Scorer                    (LED-050 - 060)   │
│  EPIC 5: AI Auto-Tuner & Surrogate ML Model               (LED-070 - 080)   │
│  EPIC 6: Packaging & Distribution Installers              (LED-090 - 100)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Epic 1: Mathematical Validation & DoE Prototyping (Sprint 0 - COMPLETE & VERIFIED)

#### `LED-001`: Implement 16-Run Fractional Factorial Benchmark Runner
* **Status:** **DONE (VERIFIED)**
* **Description:** Create `matrix_execution/bench_matrix_16.py` using Resolution V design matrix $x_5 = x_1 x_2 x_3 x_4$.
* **Acceptance Criteria:**
  * Executes 16 runs sequentially on `qwen2.5:1.5b` and `qwen2.5-coder:14b`.
  * Logs records atomically to `benchmark_results_16.csv` with UTF-8-SIG encoding.
* **Estimate:** 3 SP (Completed)

#### `LED-002`: Implement Scikit-Learn Surrogate Model (`train_surrogate.py` & `train_surrogate_expanded.py`)
* **Status:** **DONE (VERIFIED)**
* **Description:** Train high-order Response Surface Regressor to learn $f(\mathbf{x}) \to (\text{Latency}, \text{TPS})$ across 1,080 combinations.
* **Acceptance Criteria:**
  * Outputs feature importance rankings (SHAP weights).
  * Emits `presets/<model>_true_sweet_spot.json` with the optimal Pareto Sweet Spot configuration.
* **Estimate:** 3 SP (Completed)

#### `LED-003`: Implement Empirical Validation Runner (`validate_sweet_spot.py`)
* **Status:** **DONE (VERIFIED)**
* **Description:** Execute 1 real verification run on Ollama using the Sweet Spot parameters and calculate error delta ($\Delta\%$).
* **Acceptance Criteria:**
  * Error margin between predicted latency and actual latency is $\le 15\%$ (Achieved: **3.5% to 7.2% Error!**).
  * Generated code passes AST evaluation with score $\ge 85/100$ (Achieved: **85/100**).
* **Estimate:** 2 SP (Completed)

---

### Epic 2: Rust Engine Core & C++ FFI Bridge (Sprint 1–2)

#### `LED-010`: Rust Process Supervisor & llama-server Lifecycle
* **Description:** Build `led-engine-core` supervisor in Rust using Tokio to spawn, monitor, and gracefully restart `llama-server`.
* **Acceptance Criteria:**
  * Detects worker thread crashes within $500\text{ ms}$.
  * Manages port allocation and socket health checks.
* **Estimate:** 5 SP

#### `LED-011`: Zero-GIL Server-Sent Events (SSE) Streaming Gateway
* **Description:** Implement high-throughput SSE token streamer in Axum.
* **Acceptance Criteria:**
  * $P_{99}$ streaming jitter $< 10\text{ ms}$ under local concurrency.
  * Native support for standard OpenAI chunk format (`data: {"choices": [...]}`).
* **Estimate:** 5 SP

#### `LED-012`: Advanced Hardware Flags Injection
* **Description:** Expose Rust configuration builder for MTP / Draft Tokens = 2, FlashAttention-2, and `q8_0` KV cache.
* **Acceptance Criteria:**
  * Injects flags dynamically during model initialization.
* **Estimate:** 3 SP

---

### Epic 3: Go Desktop Studio UI (Wails v2) (Sprint 3–4)

#### `LED-030`: Wails v2 Desktop Application Scaffolding
* **Description:** Initialize native Go desktop application window with Tailwind CSS frontend.
* **Acceptance Criteria:**
  * Binary size $< 35\text{ MB}$.
  * Window launches in $< 0.2\text{ seconds}$ with memory footprint $< 30\text{ MB}$.
* **Estimate:** 5 SP

#### `LED-031`: Model Explorer & Real-Time VRAM Visualizer
* **Description:** Build UI component showing exact layer distribution across GPU VRAM (GDDR6) and System RAM (DDR4).
* **Acceptance Criteria:**
  * Updates VRAM consumption dynamically on model load/unload.
* **Estimate:** 5 SP

#### `LED-032`: Chat & Code Playground with Syntax Highlighting
* **Description:** Implement interactive chat and completion playground with markdown rendering and 1-click code copying.
* **Acceptance Criteria:**
  * Smooth 60fps token streaming animation without UI stutter.
* **Estimate:** 3 SP

---

### Epic 4: Native Bench Lab & AST Scorer (Sprint 5–6)

#### `LED-050`: Integrated Bench Lab Dashboard
* **Description:** Native desktop UI tab to select challenge prompts, trigger 1-click benchmarks, and view live latency charts.
* **Acceptance Criteria:**
  * Live chart updates token-by-token during benchmark runs.
* **Estimate:** 5 SP

#### `LED-051`: Automated Python AST Code Scorer
* **Description:** Native bridge to evaluate generated Python code on syntax, type hints, and error boundaries (0–100 scale).
* **Acceptance Criteria:**
  * Evaluates code in $< 10\text{ ms}$ without executing untrusted code.
* **Estimate:** 3 SP

---

### Epic 5: AI Auto-Tuner & Surrogate ML Model (Sprint 7–8)

#### `LED-070`: 1-Click Hardware Calibration Wizard
* **Description:** UI button that triggers the 16-run DoE, calls the Scikit-Learn worker, and presents the optimal Sweet Spot.
* **Acceptance Criteria:**
  * End-to-end auto-tuning finishes in $< 5\text{ minutes}$.
* **Estimate:** 5 SP

#### `LED-071`: Modelfile & Preset Exporter
* **Description:** Generate compiled `Modelfile.turbo` and `presets/<model>_turbo.json` with 1-click apply.
* **Acceptance Criteria:**
  * Immediately applies the calibrated preset to the running engine.
* **Estimate:** 3 SP

---

### Epic 6: Packaging & Distribution Installers (Sprint 9)

#### `LED-090`: Standalone Windows 11 Installer (`.msi` / `.exe`)
* **Description:** Package Rust backend + Go GUI + llama.cpp runtime into a single Windows installer with zero prerequisites.
* **Acceptance Criteria:**
  * Installs and runs on clean Windows 11 machine without Python or C++ installed.
* **Estimate:** 5 SP
