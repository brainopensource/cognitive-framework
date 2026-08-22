# Local LLM Engine Desktop (LED): Desktop Inference Studio, Benchmarking Lab & AI Auto-Tuner

**Module Code:** `003_LLM_ENGINE_DESKTOP` (LED)  
**Classification:** Desktop Inference Platform & Empirical Benchmark Suite (Alternative to LM Studio & Ollama Desktop)  
**Target Environment:** Windows 11 Host + WSL2 Ubuntu 24.04 LTS (Python 3.10+), AMD Radeon (16GB VRAM, ROCm/HIP), AMD Ryzen 7 5800X3D (8C/16T, 96MB 3D V-Cache).

---

## 1. What is LED?

**LED (Local LLM Engine Desktop)** is an open-source, high-performance **Desktop Inference Studio and Model Runner** built on top of `llama.cpp`. 

It serves as a developer-first alternative to LM Studio and Ollama Desktop, combining standard local chat, text and code generation with **built-in empirical benchmarking ("Bench Lab")** and **Machine Learning Auto-Tuning** (using Scikit-Learn Gradient Boosting to find the hardware "Sweet Spot" automatically).

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              LED DESKTOP STUDIO ECOSYSTEM                              │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                      1. ENGINE CORE & BACKEND (llama.cpp)                      │   │
│   │   - Native GGUF loader (mmap cold starts <2s)                                  │   │
│   │   - AMD Radeon ROCm/HIP & Vulkan GPU acceleration                              │   │
│   │   - Advanced flags: MTP / Draft Tokens = 2, FlashAttention-2, KV Cache Quant  │   │
│   │   - OpenAI-compatible local server (http://localhost:8080/v1)                  │   │
│   └───────────────────────────────────────┬────────────────────────────────────────┘   │
│                                           │                                            │
│         ┌─────────────────────────────────┼─────────────────────────────────┐          │
│         │                                 │                                 │          │
│   ┌─────▼───────────────────────────┐ ┌───▼───────────────────────────┐ ┌───▼──────────▼─────────────────┐   │
│   │    2. CHAT & CODE STUDIO        │ │        3. BENCH LAB           │ │     4. AI AUTO-TUNER          │   │
│   │  - Clean desktop chat interface │ │  - 1-click model benchmarks   │ │  - 16-run Fractional DoE     │   │
│   │  - System prompts & Modelfiles  │ │  - AST code quality scoring   │ │  - Scikit-Learn Surrogate ML │   │
│   │  - Real-time VRAM/RAM telemetry │ │  - CSV & JSONL Data Science   │ │  - Automatic "Sweet Spot" app │   │
│   └─────────────────────────────────┘ └───────────────────────────────┘ └───────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Architectural Boundary Invariant:**  
> LED **does not** duplicate Vanguard (which governs cognitive agency, planning, and DAGs) nor LEX (which runs code execution sandboxes).  
> LED is **strictly the local model runner, inference studio, and benchmark engine**.

---

## 2. Directory Structure

```text
tools/003_LLM_ENGINE_DESKTOP/
├── README.md                                # [This Document] Product Overview & Architecture Guide
├── docs/
│   ├── prompts/
│   │   └── fibo_challenge_finetune.md       # Canonical challenge prompt target
│   └── system/
│       ├── led_desktop_app_architecture.md  # [Primary Spec] Complete Desktop Studio Architecture
│       ├── system_overview.md               # Hardware physics, VRAM limits & OFAT baseline findings
│       └── system_abstraction_v2.md         # 16-run DoE, Surrogate ML & Meta-Dimension Registry
├── matrix_execution/
│   └── bench_matrix.py                      # Multi-model benchmarking engine & atomic data logger
└── bench_finetune/
    ├── qwen_38_27B/                         # Isolated dataset for Qwen 3.8 27B model
    │   ├── benchmark_results.csv            # Excel-ready tabular data
    │   ├── benchmark_results.jsonl          # Data Science JSONL dataset
    │   └── runs/                            # Raw generated Python files
    ├── qwen_25C_14B/                        # Isolated dataset for Qwen 2.5 Coder 14B model
    │   ├── benchmark_results.csv            # Excel-ready tabular data
    │   ├── benchmark_results.jsonl          # Data Science JSONL dataset
    │   └── runs/                            # Raw generated Python files
    └── qwen_25_15B/                         # Isolated dataset for Qwen 2.5 1.5B model
        ├── benchmark_results.csv            # Excel-ready tabular data
        ├── benchmark_results.jsonl          # Data Science JSONL dataset
        └── runs/                            # Raw generated Python files
```

---

## 3. Core Capabilities

### 3.1 1-Click Bench Lab & Automated AST Scoring
Every run is measured and parsed through Python's Abstract Syntax Tree (`ast`) module, outputting a quality score from **0 to 100**:
* **Syntax & Parse Validity (30 pts):** Validates clean compilation without syntax errors.
* **Target Function Existence (25 pts):** Ensures expected function definitions exist in AST.
* **Type Annotations (15 pts):** Verifies argument and return type annotations.
* **Input Validation & Errors (15 pts):** Checks for explicit `ValueError` handling.
* **Purity (15 pts):** Ensures zero introductory conversational chatter or unprompted markdown tags.

### 3.2 AI-Powered Hardware Auto-Tuner (Surrogate ML)
* **16-Run Fractional Factorial DoE ($2^{5-1}$):** Gathers a balanced orthogonal dataset in **~4.8 minutes**.
* **Scikit-Learn `HistGradientBoostingRegressor`:** Learns the 5D response surface in **<2ms**, finding the global **Pareto Sweet Spot** (maximum score, minimum latency) tailored specifically to your AMD Radeon + Ryzen hardware.

---

## 4. Quick Start & Execution

```bash
# 1. Benchmark Qwen 2.5 Coder 14B (~28 t/s):
python3 tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix.py qwen2.5-coder:14b

# 2. Benchmark Qwen 3.8 27B (~11-14 t/s):
python3 tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix.py qwen3.8:27b

# 3. Benchmark Qwen 2.5 1.5B (>125 t/s):
python3 tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix.py qwen2.5:1.5b
```

---

## 5. Key Documentation Links

* 📄 [LED Desktop App Architecture Specification (`docs/system/led_desktop_app_architecture.md`)](file:///home/rocha/Coding/Aether-D-System/tools/003_LLM_ENGINE_DESKTOP/docs/system/led_desktop_app_architecture.md)
* 📄 [System Overview & OFAT Empirical Findings (`docs/system/system_overview.md`)](file:///home/rocha/Coding/Aether-D-System/tools/003_LLM_ENGINE_DESKTOP/docs/system/system_overview.md)
* 📄 [High-Order DoE, Meta-Dimensions & Surrogate ML (`docs/system/system_abstraction_v2.md`)](file:///home/rocha/Coding/Aether-D-System/tools/003_LLM_ENGINE_DESKTOP/docs/system/system_abstraction_v2.md)
* 📄 [Canonical Challenge Prompt (`docs/prompts/fibo_challenge_finetune.md`)](file:///home/rocha/Coding/Aether-D-System/tools/003_LLM_ENGINE_DESKTOP/docs/prompts/fibo_challenge_finetune.md)
