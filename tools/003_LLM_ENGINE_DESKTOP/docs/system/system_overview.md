# Local LLM Desktop Engine: System Architecture, Hardware Topology, and Empirical Inference Standard

**Document ID:** `LLM-DESKTOP-SYS-OVERVIEW-V1`  
**Classification:** Staff Principal AI Architecture Specification  
**Subject:** High-Throughput Local Large Language Model Substrate, Empirical Benchmarking Engine, and Hardware-Aware Inference Optimization  
**Target Environment:** Windows 11 Host (Ollama Server Daemon) + WSL2 Ubuntu 24.04 LTS (Execution Client), AMD Radeon 16GB VRAM (ROCm/HIP Backend), AMD Ryzen 7 5800X3D (8C/16T, 96MB 3D V-Cache).

---

## 1. Executive Overview & System Topology

The `003_LLM_ENGINE_DESKTOP` project establishes a reproducible, production-grade local LLM execution, profiling, and benchmarking engine. It bridges containerized Linux workloads inside **WSL2 (Ubuntu 24.04 LTS)** with a high-performance **Windows 11 Ollama Host** running hardware-accelerated inferencing across dedicated **AMD Radeon VRAM** and **AMD Ryzen 3D V-Cache CPU cores**.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        WSL2 (UBUNTU 24.04 LTS) CLIENT SUBSTRATE                        │
│                                                                                        │
│   ┌───────────────────────────────┐         ┌──────────────────────────────────────┐   │
│   │   fibo_challenge_finetune.md  │         │          bench_matrix.py             │   │
│   │    (Immutable Prompt Target)  │         │  (Execution Engine & AST Evaluator)  │   │
│   └───────────────┬───────────────┘         └──────────────────┬───────────────────┘   │
│                   │                                            │                       │
│                   └───────────────────────┬────────────────────┘                       │
│                                           │ HTTP REST / Port 11434                     │
│                                           │ Atomic Injected Options                    │
└───────────────────────────────────────────┼────────────────────────────────────────────┘
                                            │ Localhost Forwarding
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                         WINDOWS 11 HOST OLLAMA RUNNER (V0.32+)                         │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                  Memory-Mapped GGUF Parser & llama.cpp Backend                 │   │
│   │            FlashAttention-2 Kernel + Quantized KV Cache Allocator              │   │
│   └───────────────────────────────────────┬────────────────────────────────────────┘   │
│                                           │ Compute & Tensor Dispatch                  │
│                     ┌─────────────────────┴─────────────────────┐                      │
│                     │                                           │                      │
│   ┌─────────────────▼──────────────────┐     ┌──────────────────▼──────────────────┐   │
│   │    AMD RADEON DEDICATED VRAM       │     │     AMD RYZEN 7 5800X3D CPU         │   │
│   │  - Capacity: 16.0 GB GDDR6         │     │  - Cores: 8 Physical Cores (SMT OFF)│   │
│   │  - Bandwidth: ~400–512 GB/s        │     │  - Cache: 96MB Unified 3D V-Cache   │   │
│   │  - Primary Workload: GEMM Compute  │     │  - Memory: DDR4 System RAM (PCIe)   │   │
│   └────────────────────────────────────┘     └─────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Hardware Substrate Physics & Memory Bottlenecks

### 2.1 The Two Phases of LLM Inference

1. **Prompt Prefill Phase (Compute-Bound, GEMM):**
   * Processes all input tokens in parallel.
   * Arithmetic Intensity: $\text{High} \gg 1\text{ FLOP/Byte}$.
   * Execution time governed by total GPU compute throughput ($\text{TFLOPS}$).

2. **Autoregressive Token Generation (Memory-Bandwidth Bound, GEMV):**
   * Decodes tokens sequentially ($1$ token per forward pass).
   * Arithmetic Intensity: $\text{Low} \approx 1\text{ FLOP/Byte loaded}$.
   * **Governing Throughput Equation:**
     $$\text{Theoretical Generation Speed (Tokens/s)} = \frac{\text{Memory Bandwidth (GB/s)}}{\text{Total Active Model Weight Size (GB)}}$$

### 2.2 Empirical Analysis of Layer Splitting (16GB VRAM Boundary)

* **Model A: `qwen2.5-coder:14b` (~9.2 GB in Q5_K_M / Q4_K_M):**
  * Fits **100% within the 16GB dedicated VRAM** of the AMD Radeon GPU.
  * Zero transfers over the PCIe system bus during token generation.
  * **Measured Generation Speed:** $\mathbf{26.8\text{ – }27.8\text{ tokens/second}}$.
  * **Single-Function Generation Latency:** $\mathbf{16.5\text{ seconds}}$.

* **Model B: `qwen3.8:27b` (~17.5 GB on disk, ~18.8 GB in memory):**
  * Exceeds 16GB VRAM capacity $\implies$ **~12.5 GB allocated to GPU VRAM**, while **~6.3 GB spills into System DDR4 RAM**.
  * Forward passes are throttled by the slowest interconnect (PCIe Gen4 + DDR4 bus at $\sim 35\text{ GB/s}$).
  * **Measured Generation Speed:** $\mathbf{10.5\text{ – }14.15\text{ tokens/second}}$.
  * **Single-Function Generation Latency:** $\mathbf{116\text{ – }212\text{ seconds}}$.

---

## 3. The One-Factor-At-A-Time (OFAT) Benchmark Suite

The benchmarking suite [`bench_matrix.py`](file:///home/rocha/Coding/Aether-D-System/tools/003_LLM_ENGINE_DESKTOP/matrix_execution/bench_matrix.py) runs 6 isolated single-variable experiments using an identical, immutable challenge prompt:

📄 **Standardized Prompt:** [`fibo_challenge_finetune.md`](file:///home/rocha/Coding/Aether-D-System/tools/003_LLM_ENGINE_DESKTOP/docs/prompts/fibo_challenge_finetune.md)

### 3.1 Empirical Matrix Results: `qwen3.8:27b` vs `qwen2.5-coder:14b`

| Run ID | Experiment Name | Modified Variable | `qwen3.8:27b` Speed | `qwen2.5-coder:14b` Speed | `qwen3.8` Latency | `qwen2.5` Latency | Quality Score |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **01** | **Baseline** | Default Ollama Config | 10.51 t/s | 27.33 t/s | 212.95s | 35.32s | 100 vs 85 |
| **02** | **Context Trimmed** | `num_ctx: 2048` | **14.15 t/s (+35%)** | 26.86 t/s | **116.68s** | 32.09s | 100 vs 85 |
| **03** | **Thinking Suppressed** | Strict System Instruction | 11.30 t/s | **27.80 t/s** | 125.06s | 31.06s | 100 vs 85 |
| **04** | **Greedy Decoding** | `temp: 0.0`, `top_k: 1` | 12.47 t/s | 27.48 t/s | 145.42s | **16.50s** ⚡ | 85 vs 85 |
| **05** | **Thread Affinity** | `num_thread: 8` | 11.62 t/s | 27.53 t/s | 171.12s | 32.05s | 100 vs 85 |
| **06** | **Budget & Stop** | `num_predict: 400/600` | 9.83 t/s | 26.41 t/s | 75.59s | 33.25s | 45 vs 85 |

---

## 4. Data Persistence & Automated AST Evaluation Architecture

### 4.1 Resilient Atomic Logging Engine

To ensure zero data loss during long-running benchmarks, `bench_matrix.py` implements **atomic per-run flushing**:
* Immediately appends and flushes (`f.flush()`) records to `benchmark_results.jsonl`.
* Writes UTF-8-SIG encoded rows to `benchmark_results.csv` for native Microsoft Excel and Google Sheets compatibility.
* Exports raw, unmodified output files to `runs/run_*.py`.

### 4.2 Automated Abstract Syntax Tree (AST) Evaluation Algorithm

Every generated output is parsed and scored on a $0\text{–}100$ scale:
1. **Python Grammar & Syntax Validity (30 pts):** Verified via `ast.parse()`. Catches syntax and indentation errors.
2. **Target Function Existence (25 pts):** Searches AST for `ast.FunctionDef(name='get_nth_fibonacci')`.
3. **Type Annotation Strictness (15 pts):** Validates return type hints (`node.returns is not None`).
4. **Input Error Boundary Validation (15 pts):** Verifies explicit `ValueError` raising on negative inputs.
5. **Output Purity (15 pts):** Deducts points if conversational boilerplate, thinking tokens, or unprompted markdown exist.

---

## 5. Directory Structure & Organization Standard

```text
tools/003_LLM_ENGINE_DESKTOP/
├── docs/
│   ├── prompts/
│   │   └── fibo_challenge_finetune.md       # Canonical input prompt target
│   └── system/
│       ├── system_overview.md               # [This Document] System architecture & findings
│       └── system_abstraction_v2.md         # High-order factorial DoE & Multi-agent swarm
├── matrix_execution/
│   └── bench_matrix.py                      # Multi-model benchmarking engine & data logger
└── bench_finetune/
    ├── qwen_38_27B/                         # Isolated dataset partition for 27B model
    │   ├── benchmark_results.csv            # Excel-ready tabular data
    │   ├── benchmark_results.jsonl          # Data Science JSONL dataset
    │   └── runs/                            # Raw generated .py runs (01 to 06)
    └── qwen_25C_14B/                        # Isolated dataset partition for 14B model
        ├── benchmark_results.csv            # Excel-ready tabular data
        ├── benchmark_results.jsonl          # Data Science JSONL dataset
        └── runs/                            # Raw generated .py runs (01 to 06)
```
