# Product Requirements Document (PRD): LED (LLM Engine Desktop)

**Document Code:** `PRD-LED-2026-V1`  
**Classification:** Product Engineering & Architectural Standard  
**Product Name:** LED (LLM Engine Desktop)  
**Vision:** High-Performance, Open-Source Desktop Inference Studio, Empirical Benchmark Lab & AI Auto-Tuner for Local Large Language Models.

---

## 1. Product Overview & The Problem Space

### 1.1 The Market Pain
Current local LLM desktop solutions suffer from deep architectural flaws:
* **LM Studio:** Closed-source, opaque, memory-heavy (Electron bloat), lacks automated empirical benchmarking, and forces manual guesswork for parameters (like Draft Tokens, context size, threads).
* **Ollama Desktop:** Operates as a "black box", hides low-level hardware telemetry, lacks an integrated benchmarking lab, and defaults to wasteful context windows (32k–262k tokens) that trigger unwanted CPU/RAM layer offloading on 16GB GPUs.

### 1.2 The LED Solution
LED is a **developer-first, lightweight, tri-language Desktop Studio**:
1. **Rust Backend Core:** Zero-GIL, high-throughput C++ FFI bridge to `llama.cpp` with native SSE streaming and OpenAI-compatible proxy (`/v1`).
2. **Go Desktop GUI (Wails):** Native Windows/Linux desktop client (<30MB RAM footprint, cold starts in <0.2s, zero Electron bloat).
3. **Python AI Auto-Tuner:** Embedded Scikit-Learn surrogate modeling to automatically calculate the Pareto "Sweet Spot" for any local GPU/CPU hardware in <5 minutes.

---

## 2. Target Personas

* **Persona A (The AI & Software Engineer):** Needs maximum tokens/sec, precise VRAM layer offloading, and an OpenAI-compatible local endpoint (`http://localhost:8080/v1`) for IDE integration (VSCode, Cursor, Aider, Vanguard, LEX).
* **Persona B (The Hardware Optimizer / Researcher):** Wants empirical numbers, AST code quality metrics, DoE matrices, and reproducible CSV/JSONL logs rather than subjective impressions.
* **Persona C (The Privacy-Conscious Power User):** Demands a 100% offline, open-source desktop app with zero telemetry, instant cold starts, and a beautiful native interface.

---

## 3. Functional Requirements (FR)

### FR-1: High-Performance Engine Core (Rust + `llama.cpp`)
* The system **SHALL** embed a lightweight Rust process supervisor managing `llama-server` and direct C++ FFI bindings.
* The system **SHALL** support GGUF zero-copy memory mapping (`mmap`) with cold starts $<2.0\text{ seconds}$.
* The system **SHALL** provide explicit toggles for: Multi-Token Prediction (MTP / Draft Tokens = 2 for AMD Radeon), FlashAttention-2, and Quantized KV Cache (`q8_0` / `q4_0`).

### FR-2: Integrated "Bench Lab" Tab
* The system **SHALL** provide a native 1-click benchmarking UI with standardized challenge prompts (`fibo_challenge_finetune.md`).
* The system **SHALL** execute benchmark runs **strictly sequentially** to avoid GPU/VRAM contention.
* The system **SHALL** parse and score generated code on a $0\text{–}100$ scale using automated Abstract Syntax Tree (AST) validation.

### FR-3: Machine Learning Auto-Tuner (Surrogate ML)
* The system **SHALL** execute a 16-run Fractional Factorial DoE ($2^{5-1}$) in $<5.0\text{ minutes}$.
* The system **SHALL** train an on-device Scikit-Learn `HistGradientBoostingRegressor` to predict latency and TPS across all 32 combinations.
* The system **SHALL** identify the Pareto-optimal "Sweet Spot" and offer 1-click application.

### FR-4: Model & Quantization Hub
* The system **SHALL** manage local GGUF model files and provide 1-click quantization (FP16 $\to$ `Q4_K_M`, `Q8_0`, `IQ3_M`).
* The system **SHALL** support dynamic LoRA adapter attachment.

### FR-5: Native Desktop Studio GUI (Go + Wails)
* The system **SHALL** provide a lightweight native desktop UI with 3 primary views:
  1. **Chat & Code Studio:** Streaming conversation, markdown rendering, and Modelfile presets.
  2. **Bench Lab:** Interactive test runner, live latency charts, and CSV/JSONL export.
  3. **AI Auto-Tuner:** Parameter importance ranking (SHAP) and hardware calibration wizard.

### FR-6: Local API Gateway & Multi-Client Compatibility
* The system **SHALL** expose an OpenAI-compatible HTTP API on `http://localhost:8080/v1` for seamless consumption by external tools (Vanguard, LEX, IDEs).

---

## 4. Non-Functional Requirements (NFR)

* **NFR-1 (Memory Footprint):** The desktop UI and engine supervisor **SHALL** consume $<30\text{ MB}$ of system RAM (excluding model weights).
* **NFR-2 (Cold Start):** The desktop UI **SHALL** launch in $<0.2\text{ seconds}$.
* **NFR-3 (Zero-GIL Streaming):** The backend **SHALL** stream Server-Sent Events (SSE) in Rust with $<5\text{ms}$ inter-token jitter.
* **NFR-4 (Hermeticity & Privacy):** The application **SHALL** operate 100% offline with zero telemetry or outbound analytics.
* **NFR-5 (Resilience):** Benchmarking datasets **SHALL** be flushed atomically per run to prevent data loss.
* **NFR-6 (Cross-Platform):** The application **SHALL** run natively on Windows 11 and Ubuntu 24.04 / WSL2.

---

## 5. Service Level Objectives (SLOs)

| Metric | Target SLO | Measurement Method |
| :--- | :--- | :--- |
| **API Response Jitter** | $P_{99} < 10\text{ ms}$ | SSE streaming packet arrival timestamps |
| **16-Run DoE Duration** | $< 5.0\text{ minutes}$ (on 14B) | Total wall-clock time from launch to CSV write |
| **ML Training Time** | $< 0.1\text{ seconds}$ | Scikit-Learn fit duration |
| **AST Parse Overhead** | $< 5\text{ ms}$ per code sample | Python `ast.parse()` execution time |

---

## 6. The $1M Competitive Moat

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE LED COMPETITIVE MOAT                          │
│                                                                             │
│   1. MATHEMATICAL AUTO-TUNING vs GUESSWORK                                  │
│      - LM Studio: Guess parameters manually.                                │
│      - LED: Scikit-Learn finds the exact Pareto Sweet Spot in 4.8 minutes. │
│                                                                             │
│   2. NATIVE GO/RUST vs ELECTRON BLOAT                                       │
│      - LM Studio: 500MB+ RAM for Electron UI.                               │
│      - LED: <30MB RAM native Wails/Go executable.                           │
│                                                                             │
│   3. FIRST-CLASS BENCH LAB vs ZERO TELEMETRY                                │
│      - Ollama/LM Studio: No built-in AST code benchmarking.                 │
│      - LED: 1-Click AST evaluation, CSV export, and Data Science ready.     │
└─────────────────────────────────────────────────────────────────────────────┘
```
