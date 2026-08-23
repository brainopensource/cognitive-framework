# Normative Technical Specification: LED (LLM Engine Desktop)

**Document Code:** `SPEC-LED-2026-V1`  
**Standard:** Pure RFC-2119 Normative Technical Law  
**Subject:** Tri-Language Architecture (Rust + Go + Python), Data Schemas, DoE Formulation, and Error Taxonomy  
**Target Environment:** Windows 11 Host + WSL2 Ubuntu 24.04 LTS, AMD Radeon 16GB VRAM, AMD Ryzen 7 5800X3D.

---

## 1. RFC-2119 Terminology Conformance

The key words **"MUST"**, **"MUST NOT"**, **"REQUIRED"**, **"SHALL"**, **"SHALL NOT"**, **"SHOULD"**, **"SHOULD NOT"**, **"RECOMMENDED"**, **"MAY"**, and **"OPTIONAL"** in this document are to be interpreted as described in [RFC-2119](https://www.ietf.org/rfc/rfc2119.txt).

---

## 2. Tri-Language Component Model & Inter-Process Contracts

LED is strictly partitioned into three decoupled computational tiers:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TIER 1: GO DESKTOP GUI (`led-desktop-gui`)               │
│  - Framework: Wails v2 / Native WebView                                     │
│  - Responsibility: Desktop window management, Tray icon, View rendering    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ IPC / Localhost HTTP REST
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    TIER 2: RUST ENGINE SUPERVISOR (`led-engine-core`)       │
│  - Framework: Axum / Tokio / llama.cpp C++ FFI Bindings                     │
│  - Responsibility: Process lifecycle, SSE token streaming, OpenAI gateway   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Subprocess Call (On-Demand)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                  TIER 3: PYTHON DATA SCIENCE WORKER (`led-ml-worker`)       │
│  - Framework: Scikit-Learn / Pandas / Python AST                            │
│  - Responsibility: DoE generation, AST evaluation, Gradient Boosting fit    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Tier 1: Go Desktop GUI Rules
* The Desktop GUI **MUST NOT** perform raw tensor compute or matrix multiplications.
* The Desktop GUI **MUST** communicate with the Rust backend over HTTP `http://127.0.0.1:8080` or native IPC.
* The Desktop GUI **MUST** render the three canonical tabs: `[Chat & Code]`, `[Bench Lab]`, and `[AI Auto-Tuner]`.

### 2.2 Tier 2: Rust Engine Core Rules
* The Rust engine **MUST** bind to `127.0.0.1:8080` and expose OpenAI-compatible routes (`/v1/chat/completions`, `/v1/models`).
* The Rust engine **MUST** stream tokens using Server-Sent Events (SSE) with `Transfer-Encoding: chunked`.
* The Rust engine **MUST** supervise the `llama-server` lifecycle, detecting crashed worker threads within $\le 500\text{ ms}$.

### 2.3 Tier 3: Python ML Worker Rules
* The Python worker **MUST** be invoked as an isolated subprocess or CLI tool.
* The Python worker **MUST** implement AST parsing via `ast.parse()` without executing untrusted user code via `eval()` or `exec()`.

---

## 3. Data Schemas & Wire Contracts

### 3.1 Benchmark Record JSON Schema (`benchmark_results.jsonl`)

Every benchmark record **MUST** conform to the following JSON schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "LEDBenchmarkRecord",
  "type": "object",
  "required": [
    "timestamp_iso",
    "run_id",
    "model_name",
    "prompt_tokens",
    "prompt_tps",
    "eval_tokens",
    "eval_tps",
    "wall_time_sec",
    "auto_score",
    "auto_feedback",
    "output_file"
  ],
  "properties": {
    "timestamp_iso": { "type": "string", "format": "date-time" },
    "run_id": { "type": "string" },
    "experiment_name": { "type": "string" },
    "model_name": { "type": "string" },
    "num_ctx": { "type": ["integer", "string"] },
    "num_thread": { "type": ["integer", "string"] },
    "temperature": { "type": ["number", "string"] },
    "top_k": { "type": ["integer", "string"] },
    "top_p": { "type": ["number", "string"] },
    "num_predict": { "type": ["integer", "string"] },
    "has_system_prompt": { "type": "string", "enum": ["Yes", "No"] },
    "prompt_tokens": { "type": "integer", "minimum": 0 },
    "prompt_tps": { "type": "number", "minimum": 0.0 },
    "eval_tokens": { "type": "integer", "minimum": 0 },
    "eval_tps": { "type": "number", "minimum": 0.0 },
    "wall_time_sec": { "type": "number", "minimum": 0.0 },
    "auto_score": { "type": "integer", "minimum": 0, "maximum": 100 },
    "auto_feedback": { "type": "string" },
    "output_file": { "type": "string" }
  },
  "additionalProperties": true
}
```

### 3.2 Calibrated Preset Schema (`presets/<model>_turbo.json`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "LEDPresetConfig",
  "type": "object",
  "required": ["preset_name", "target_model", "options", "predicted_latency_sec", "predicted_tps"],
  "properties": {
    "preset_name": { "type": "string" },
    "target_model": { "type": "string" },
    "options": {
      "type": "object",
      "required": ["num_ctx", "num_thread", "temperature", "top_k"],
      "properties": {
        "num_ctx": { "type": "integer" },
        "num_thread": { "type": "integer" },
        "temperature": { "type": "number" },
        "top_k": { "type": "integer" },
        "top_p": { "type": "number" },
        "num_predict": { "type": "integer" },
        "draft_tokens": { "type": "integer" }
      }
    },
    "predicted_latency_sec": { "type": "number" },
    "predicted_tps": { "type": "number" },
    "system_prompt": { "type": ["string", "null"] }
  }
}
```

---

## 4. Mathematical Formulation & AST Scoring Norms

### 4.1 Fractional Factorial Resolution V Generator

The 16-run orthogonal design matrix $\mathbf{X} \in \{-1, +1\}^{16 \times 5}$ **MUST** be generated using the relation:
$$x_5 = x_1 \cdot x_2 \cdot x_3 \cdot x_4$$

Where $x_i \in \{-1, +1\}$ corresponds to the binary optimization states:
* $x_1$: `num_ctx` ($\{-1: \text{default}, +1: 2048\}$)
* $x_2$: `suppress_thinking` ($\{-1: \text{none}, +1: \text{strict\_system}\}$ )
* $x_3$: `greedy_sampling` ($\{-1: \text{temp=0.7}, +1: \text{temp=0.0}\}$ )
* $x_4$: `thread_affinity` ($\{-1: \text{default}, +1: 8\text{ physical cores}\}$ )
* $x_5$: `budget_cap` ($\{-1: \text{unlimited}, +1: 600\text{ tokens}\}$ )

### 4.2 AST Code Quality Metric (0–100 Scale)

The automated evaluation function $S_{\text{total}}$ **SHALL** compute:
$$S_{\text{total}} = S_{\text{syntax}} + S_{\text{signature}} + S_{\text{types}} + S_{\text{error}} + S_{\text{purity}}$$

* $S_{\text{syntax}} = 30$ if `ast.parse(code)` succeeds; else $0$ (abort further checks).
* $S_{\text{signature}} = 25$ if $\exists \text{FunctionDef}(\text{name}=\text{'get\_nth\_fibonacci'})$; else $0$.
* $S_{\text{types}} = 15$ if function return annotation exists; else $0$.
* $S_{\text{error}} = 15$ if `ValueError` exists in the AST body; else $0$.
* $S_{\text{purity}} = 15$ if output contains pure code with no unprompted chat filler; else $0$.

---

## 5. Error Taxonomy & System Codes

| Error Code | Subsystem | Trigger Condition | Severity | System Action |
| :--- | :--- | :--- | :--- | :--- |
| `ERR-LED-001` | Engine | `llama-server` process failed to start or port 8080 busy. | CRITICAL | Fallback to retry with exponential backoff ($\le 3$ retries). |
| `ERR-LED-002` | Hardware | GPU VRAM out-of-memory during model weight allocation. | HIGH | Automatically reduce `num_ctx` by 50% and offload layers to CPU RAM. |
| `ERR-LED-003` | Bench Lab | API connection timed out during benchmark run. | MEDIUM | Record run as failed, flush partial CSV record, continue next run. |
| `ERR-LED-004` | Auto-Tuner | Insufficient variance in training dataset for ML regression. | LOW | Warn user, suggest running full $32$-run grid. |
| `ERR-LED-005` | AST | Generated code has fatal unclosed syntax error. | LOW | Assign $S_{\text{syntax}} = 0$, record feedback traceback. |
