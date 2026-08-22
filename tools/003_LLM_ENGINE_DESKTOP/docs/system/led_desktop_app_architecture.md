# LED (LLM Engine Desktop): Desktop Inference Studio, Empirical Benchmark Suite & ML Auto-Tuning Architecture

**Document ID:** `LED-DESKTOP-APP-ARCH-V1`  
**Classification:** Product Architecture & Engineering Specification  
**Subject:** High-Performance Open-Source Desktop LLM Studio (Alternative to LM Studio & Ollama Desktop UI) with Built-In Hardware Benchmarking, Scikit-Learn Surrogate Auto-Tuning, and GGUF Management  
**Target Environment:** Windows 11 Host + WSL2 Ubuntu 24.04 LTS, AMD Radeon GPU (16GB VRAM, ROCm/HIP), AMD Ryzen 7 5800X3D (8C/16T, 96MB 3D V-Cache).

---

## 1. Executive Product Vision & Boundaries

**LED (LLM Engine Desktop)** is a lightweight, open-source **Desktop Inference Studio and Local LLM Manager** engineered for developers, AI researchers, and power users. It provides a superior, developer-first alternative to closed-source or opaque tools like LM Studio and Ollama Desktop.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                SYSTEM BOUNDARY MATRIX                                  │
│                                                                                        │
│   ┌────────────────────────────────┐        ┌──────────────────────────────────────┐   │
│   │    VANGUARD (CEREBRO)          │        │    LEX (LLM EXECUTION X)             │   │
│   │ - Agência Recursiva, DAGs      │        │ - Sandbox Seguro de Execução         │   │
│   │ - Planejamento e Governança    │        │ - Linters, Subprocessos e Pytest     │   │
│   └───────────────┬────────────────┘        └──────────────────┬───────────────────┘   │
│                   │                                            │                       │
│                   └───────────────────────┬────────────────────┘                       │
│                                           │ OpenAI HTTP Protocol                       │
│                                           │ http://localhost:8080/v1                   │
│   ┌───────────────────────────────────────▼────────────────────────────────────────┐   │
│   │                LED (LLM ENGINE DESKTOP) — INFERENCE STUDIO                     │   │
│   │  1. Llama.cpp High-Performance C++ Runner (GGUF, ROCm/HIP, Vulkan, DirectML)   │   │
│   │  2. Hardware Profiler & VRAM/RAM Layer Split Visualizer                        │   │
│   │  3. Built-In Empirical Benchmarking Suite ("Bench Lab" Tab)                    │   │
│   │  4. ML Surrogate Auto-Tuner (Scikit-Learn Gradient Boosting Sweet Spot)       │   │
│   │  5. Model Catalog, Quantization & LoRA Adapter Manager                         │   │
│   │  6. Clean Desktop UI (Chat, Code, Completion, Prompt Engineering)             │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **Strict Architectural Boundary Invariant:**  
> LED **does not** manage autonomous agents, multi-agent swarms, or code execution sandboxes. Those capabilities belong strictly to **Vanguard** and **LEX**.  
> LED is **exclusively** the local desktop engine and UI that runs, tunes, benchmarks, and serves LLMs for text, code, chat, and API clients.

---

## 2. Core Pillars of the LED Desktop Platform

LED is organized into **5 functional subsystems**:

```text
LED DESKTOP STUDIO
├── 1. Engine Core          (llama.cpp native C++ backend, VRAM offload, ROCm/HIP)
├── 2. Model & Quant Hub    (GGUF management, HuggingFace download, quantization)
├── 3. Chat & Code Studio   (Desktop UI for direct interaction, system prompts)
├── 4. Bench Lab            (Automated 1-click empirical benchmarking & AST score)
└── 5. AI Auto-Tuner        (ML surrogate optimization for instant hardware sweet spot)
```

---

## 3. Pillar 1: High-Performance Engine Core (`llama.cpp`)

Instead of heavy Python/PyTorch dependencies (like vLLM), LED embeds the ultra-fast C++ **`llama.cpp`** backend (`llama-server` supervisor):

* **Native GGUF Zero-Copy Loading (`mmap`):** Cold starts take **<2 seconds**.
* **Precise Layer Offloading:** Allows partial GPU offloading when a model exceeds 16GB VRAM (e.g., 27B models allocate 12.5GB to VRAM and the remainder to RAM without crashing).
* **Hardware-Specific Advanced Toggles:**
  * **MTP / Draft Tokens = 2:** Native support for speculative decoding on AMD Radeon dedicated GPUs.
  * **FlashAttention-2 & Tiling:** Cuts attention VRAM footprint by 30%.
  * **Quantized KV Cache (`q8_0` / `q4_0`):** Saves 50–75% memory on context matrices.
* **Standardized Local API:** Exposes both OpenAI-compatible endpoints (`/v1/chat/completions`) and native high-speed endpoints (`/completion`).

---

## 4. Pillar 2: The "Bench Lab" (Integrated Benchmarking Function)

In traditional tools (LM Studio), measuring inference speed requires third-party scripts. In LED, **Benchmarking is a first-class citizen inside the Desktop UI**.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LED BENCH LAB (UI TAB)                           │
│                                                                             │
│  Target Model: [ qwen2.5-coder:14b ▼ ]   Prompt: [ fibo_challenge.md ▼ ]    │
│  Mode: (●) 6-Run Baseline OFAT   ( ) 16-Run Fractional DoE   ( ) Custom     │
│                                                                             │
│  [ ▶ START BENCHMARK ]                                                      │
│                                                                             │
│  Live Execution Graph:                                                      │
│  ├── Run 01: 27.33 t/s (Latency: 35.3s | Score: 85/100)                     │
│  ├── Run 02: 26.86 t/s (Latency: 32.1s | Score: 85/100)                     │
│  └── Run 04: 27.48 t/s (Latency: 16.5s | Score: 85/100) ⚡                   │
│                                                                             │
│  [ Export CSV ]  [ Export JSONL ]  [ View Raw .py Code ]                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Bench Lab Capabilities:
1. **Automated Test Sequence:** Runs reproducible tests sequentially without GPU contention.
2. **Real-Time Telemetry:** Records Prompt TPS, Generation TPS, Time To First Token (TTFT), and VRAM/RAM allocation.
3. **Automated AST Code Scoring:** Evaluates Python code syntax, type hints, and error boundaries on a $0\text{–}100$ scale.
4. **Data Science Storage:** Automatically exports logs to isolated model folders in `bench_finetune/<model_folder>/benchmark_results.csv`.

---

## 5. Pillar 3: AI-Powered Auto-Tuning (Surrogate ML Model)

LED includes an embedded **Machine Learning Auto-Tuner** using Scikit-Learn (`HistGradientBoostingRegressor`):

```text
┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│ 16 RUNS FACTORIAL MATRIX│ ───► │  EMBEDDED ML REGRESSOR  │ ───► │   1-CLICK "AUTO-TUNE"   │
│  (Coleta Real em ~4.8m) │      │  Scikit-Learn Gradient  │      │  Aplica o Sweet Spot na │
│                         │      │    Boosting Model       │      │  GPU Radeon sem chutar  │
└─────────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

### How the Auto-Tuner Works:
1. The user clicks **"Auto-Calibrate Hardware"**.
2. LED runs the **16-Run Fractional Factorial Matrix ($2^{5-1}$)** in ~4.8 minutes.
3. An internal Gradient Boosting regressor fits the response surface:
   $$f(\text{num\_ctx}, \text{temp}, \text{threads}, \text{think\_mode}, \text{budget}) \to (\text{Latency}, \text{TPS})$$
4. The ML model predicts all unexecuted combinations in **<2 milliseconds** and identifies the **Pareto Sweet Spot** (maximum code quality with minimum wall-clock latency).
5. LED automatically applies these tuned parameters to the model's runtime configuration.

---

## 6. Pillar 4: Model Management, Quantization & Fine-Tuning Hub

LED acts as the central hub for local GGUF weights:

* **1-Click GGUF Quantization (`llama-quantize` wrapper):** Convert FP16 Hugging Face weights into `Q4_K_M`, `Q8_0`, or `IQ3_M` directly inside the app.
* **LoRA Adapter Stacking:** Attach custom PEFT / QLoRA `.gguf` adapter files on top of base models dynamically.
* **Modelfile Declarative Compiler:** Compile custom system instructions, stop tokens, and default temperature profiles into immutable model targets.

---

## 7. Pillar 5: Desktop UX & Developer Interface

LED provides a distraction-free, professional interface:

1. **Model Explorer & VRAM Visualizer:** Visual bar showing exact VRAM vs RAM layer distribution (e.g., *48/64 layers in GDDR6, 16 layers in DDR4*).
2. **Chat & Code Playground:** Markdown rendering, syntax highlighting, copy-paste codeblocks, and system prompt switcher.
3. **Low-Level Server Console:** Real-time log of `llama-server` requests, token generation graphs, and active client connections.

---

## 8. Summary: Why LED Outperforms Existing Tools

| Feature | Ollama Desktop | LM Studio | LED (LLM Engine Desktop) |
| :--- | :---: | :---: | :---: |
| **Open Source Backend** | ✅ Yes | ❌ No (Closed Source) | ✅ **100% Open-Source (llama.cpp)** |
| **Built-In Bench Lab & AST Scoring** | ❌ No | ❌ No | ✅ **Native Feature (CSV/JSONL Data Science)** |
| **AI Auto-Tuning (Surrogate ML)** | ❌ No | ❌ No | ✅ **Native (Scikit-Learn Gradient Boosting)** |
| **MTP / Draft Tokens = 2 for AMD** | ❌ Opaque | ⚠️ Manual Menu | ✅ **First-Class 1-Click Toggle** |
| **VRAM / RAM Layer Inspector** | ⚠️ Partial | ✅ Yes | ✅ **Precise Hardware Telemetry** |
| **Zero-Bloat Developer API** | ✅ Yes | ✅ Yes | ✅ **OpenAI-Compatible (`/v1`) & Native** |
