# LED (LLM Engine Desktop): Final Aligned Execution Plan & Architecture

**Document Code:** `LED-FINAL-PLAN-ALIGNED-2026`  
**Classification:** Approved Engineering Implementation Plan  
**Target Module:** `tools/003_LLM_ENGINE_DESKTOP` (LED)  
**Alignment Status:** 100% Aligned via `/grill-me` Design Decisions

---

## 1. Approved Execution Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STAGE 1: 16-RUN FRACTIONAL FACTORIAL DoE                 │
│  - Script: bench_matrix_16.py                                               │
│  - Step 1A: qwen2.5:1.5b (~60s) -> Validates pipeline integrity             │
│  - Step 1B: qwen2.5-coder:14b (~4.8m) -> Produces primary coding dataset    │
│  - Output: benchmark_results_16.csv (16 orthogonal rows per model)          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    STAGE 2: SCIKIT-LEARN SURROGATE ML MODEL                 │
│  - Script: train_surrogate.py                                               │
│  - Algorithm: HistGradientBoostingRegressor                                 │
│  - Objective: Minimize Wall Latency subject to AST Score >= 85              │
│  - Output: Feature Importances + Pareto Sweet Spot + Presets (JSON/Modelfile)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    STAGE 3: EMPIRICAL SWEET SPOT VALIDATION                 │
│  - Script: validate_sweet_spot.py                                           │
│  - Executes 1 real test with recommended parameters                         │
│  - Compares Predicted vs Actual Latency/TPS (Calculates Error Margin Δ%)    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    STAGE 4: LED DESKTOP STUDIO APP SCAFFOLDING              │
│  - Directory: tools/003_LLM_ENGINE_DESKTOP/app/                             │
│  - Backend: FastAPI service (engine supervisor + telemetry + OpenAI API)    │
│  - Frontend: Lightweight Web UI (http://localhost:8080) with 3 tabs:        │
│      1. [Chat & Code Studio]   2. [Bench Lab]   3. [AI Auto-Tuner]          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Agreed Implementation Details

### Stage 1: 16-Run Fractional DoE Runner (`bench_matrix_16.py`)
* **File:** `tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix_16.py`
* **Features:**
  * Resolution V $2^{5-1}$ orthogonal design matrix (16 runs).
  * Parameters:
    * $x_1$: `num_ctx` (`2048` vs `default`)
    * $x_2$: `suppress_thinking` (`system prompt` vs `none`)
    * $x_3$: `greedy_sampling` (`temp=0.0, top_k=1` vs `default`)
    * $x_4$: `thread_affinity` (`num_thread=8` vs `default`)
    * $x_5$: `budget_cap` (`num_predict=600` vs `default`)
  * Model sequence: `qwen2.5:1.5b` first, followed by `qwen2.5-coder:14b`.
  * Atomic per-run logging with `flush()` to `benchmark_results_16.csv` and `.jsonl`.

### Stage 2: Scikit-Learn Surrogate ML Model (`train_surrogate.py`)
* **File:** `tools/003_LLM_ENGINE_DESKTOP/matrix_execution/train_surrogate.py`
* **Features:**
  * Fits `HistGradientBoostingRegressor` on `wall_time_sec` and `eval_tps`.
  * Evaluates all 32 combinations in the full Cartesian product grid $\Omega = \{0, 1\}^5$.
  * Objective: $\min \text{Latency}(\mathbf{x})$ with $\text{AST Score} \ge 85$.
  * Emits both `presets/<model>_turbo.json` and a compiled `Modelfile.turbo`.

### Stage 3: Empirical Validation Runner (`validate_sweet_spot.py`)
* **File:** `tools/003_LLM_ENGINE_DESKTOP/matrix_execution/validate_sweet_spot.py`
* **Features:**
  * Executes 1 real verification run on Ollama using the Sweet Spot parameters.
  * Measures actual Tokens/s, Latency, and AST Quality Score.
  * Calculates prediction accuracy ($\Delta\%$) and prints a summary table.

### Stage 4: LED Desktop Studio App Scaffolding (`app/`)
* **Directory:** `tools/003_LLM_ENGINE_DESKTOP/app/`
* **Structure:**
  * `core/engine_manager.py`: Local `llama-server` / Ollama process supervisor.
  * `core/hardware_probe.py`: Real-time VRAM/RAM allocation telemetry for AMD Radeon + Ryzen.
  * `api/server.py`: FastAPI server serving static Web UI and OpenAI-compatible proxy (`/v1`).
  * `static/index.html`: Clean, responsive web dashboard accessible at `http://localhost:8080` with:
    * **Tab 1:** Chat & Code Studio.
    * **Tab 2:** Bench Lab (1-click matrix execution and live graph).
    * **Tab 3:** AI Auto-Tuner (1-click hardware calibration and sweet spot apply).

---

## 3. Verification & Execution Sequence

```bash
# 1. Run 16-run benchmark on Qwen 2.5 1.5B (~60s):
python3 tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix_16.py qwen2.5:1.5b

# 2. Run 16-run benchmark on Qwen 2.5 Coder 14B (~4.8m):
python3 tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix_16.py qwen2.5-coder:14b

# 3. Train Surrogate Model and generate Sweet Spot presets:
python3 tools/003_LLM_ENGINE_DESKTOP/matrix_execution/train_surrogate.py tools/003_LLM_ENGINE_DESKTOP/bench_finetune/qwen_25C_14B/benchmark_results_16.csv

# 4. Empirically validate the Sweet Spot:
python3 tools/003_LLM_ENGINE_DESKTOP/matrix_execution/validate_sweet_spot.py qwen2.5-coder:14b

# 5. Launch the LED Desktop Studio Web Dashboard:
python3 tools/003_LLM_ENGINE_DESKTOP/app/api/server.py
```
