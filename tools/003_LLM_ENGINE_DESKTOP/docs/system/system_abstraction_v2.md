# High-Order Inference Abstraction: Full & Fractional Factorial DoE, Surrogate ML Modeling, and Hierarchical Swarms

**Document ID:** `LLM-DESKTOP-SYS-ABSTRACTION-V2`  
**Classification:** Staff Principal AI Architecture & Mathematical Specification  
**Subject:** High-Dimensional Design of Experiments ($2^k$ and $2^{k-1}$ Matrices), Scikit-Learn Surrogate Regression Modeling, Pareto Optimal Frontier, and Multi-Tier Hybrid Agent Orchestration  
**Target Environment:** Local LLM Substrate (`qwen3.8:27b` + `qwen2.5-coder:14b` + `qwen2.5:1.5b` on AMD Radeon 16GB VRAM & Ryzen 5800X3D).

---

## 1. High-Order Combinatorial Design of Experiments (DoE)

### 1.1 Limitations of One-Factor-At-A-Time (OFAT) Benchmarking

Standard single-variable testing assumes linear independence between inference levers. In reality, local LLM inference parameters exhibit strong **non-linear coupling and cross-layer interaction effects**:

$$\text{Throughput}(A \cup B) \neq \text{Throughput}(A) + \text{Throughput}(B)$$

* **Example Synergy:** Trimming context window (`num_ctx=2048`) frees ~4GB VRAM. Enabling Greedy Decoding (`temperature=0.0`) eliminates multinomial sampling in CPU memory. Combined, the CPU-GPU pipeline experiences zero cache thrashing, yielding a multiplicative speedup unattainable by either parameter in isolation.

### 1.2 The $2^k$ Full Factorial Parameter Space

We formalize the inference configuration as a binary feature vector $\mathbf{x} \in \{0, 1\}^5$, representing $k=5$ orthogonal optimization dimensions:

$$\Omega = \prod_{i=1}^{k} D_i = \{0, 1\}^5 \implies |\Omega| = 2^5 = 32\text{ Experimental Configurations}$$

```text
                               ┌─────────────────────────────┐
                               │  k=5 Optimization Features   │
                               └──────────────┬──────────────┘
                                              │
         ┌──────────────────┬─────────────────┼──────────────────┬──────────────────┐
         │                  │                 │                  │                  │
┌────────▼────────┐ ┌───────▼────────┐ ┌──────▼────────┐ ┌───────▼────────┐ ┌───────▼────────┐
│    $x_1$: CTX   │ │  $x_2$: THINK  │ │  $x_3$: GREEDY│ │  $x_4$: THREAD │ │  $x_5$: BUDGET │
│ 0: Default (32k)│ │ 0: Normal      │ │ 0: Temp=0.7   │ │ 0: OS Default  │ │ 0: Unlimited   │
│ 1: Trim (2048)  │ │ 1: Suppressed  │ │ 1: Temp=0.0   │ │ 1: 8 Phys Cores│ │ 1: Cap=600     │
└─────────────────┘ └────────────────┘ └───────────────┘ └────────────────┘ └────────────────┘
```

---

## 2. 16-Run Fractional Factorial Design ($2^{5-1}$) & Hypercube Sampling

To cut benchmark time by 50% without sacrificing statistical power, we use a **Resolution V Fractional Factorial Design ($2^{5-1} = 16\text{ runs}$)**.

### 2.1 Mathematical Basis of Half-Fraction Sampling

By setting the 5th factor generator as the interaction of the first four:
$$x_5 = x_1 \cdot x_2 \cdot x_3 \cdot x_4$$

We construct an orthogonal 16-row design matrix where:
1. Every individual parameter is active ($1$) in exactly 8 runs and inactive ($0$) in exactly 8 runs.
2. All main effects ($\beta_1 \dots \beta_5$) are completely unconfounded by 2-factor interactions ($\gamma_{ij}$).
3. **Execution Time:** $16 \text{ runs} \times 18.0\text{s} \approx \mathbf{4.8\text{ minutes}}$ on the `qwen2.5-coder:14b`.

### 2.2 The 16-Run Orthogonal Design Matrix

| Run ID | $x_1$ (Context) | $x_2$ (No Think) | $x_3$ (Greedy) | $x_4$ (8 Threads) | $x_5$ (Budget Cap) | Semantic Tag |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **01** | 0 | 0 | 0 | 0 | 1 | `exp_16_budget` |
| **02** | 1 | 0 | 0 | 0 | 0 | `exp_16_ctx` |
| **03** | 0 | 1 | 0 | 0 | 0 | `exp_16_nothink` |
| **04** | 1 | 1 | 0 | 0 | 1 | `exp_16_ctx_nothink_budget` |
| **05** | 0 | 0 | 1 | 0 | 0 | `exp_16_greedy` |
| **06** | 1 | 0 | 1 | 0 | 1 | `exp_16_ctx_greedy_budget` |
| **07** | 0 | 1 | 1 | 0 | 1 | `exp_16_nothink_greedy_budget` |
| **08** | 1 | 1 | 1 | 0 | 0 | `exp_16_ctx_nothink_greedy` |
| **09** | 0 | 0 | 0 | 1 | 0 | `exp_16_thread8` |
| **10** | 1 | 0 | 0 | 1 | 1 | `exp_16_ctx_thread8_budget` |
| **11** | 0 | 1 | 0 | 1 | 1 | `exp_16_nothink_thread8_budget` |
| **12** | 1 | 1 | 0 | 1 | 0 | `exp_16_ctx_nothink_thread8` |
| **13** | 0 | 0 | 1 | 1 | 1 | `exp_16_greedy_thread8_budget` |
| **14** | 1 | 0 | 1 | 1 | 0 | `exp_16_ctx_greedy_thread8` |
| **15** | 0 | 1 | 1 | 1 | 0 | `exp_16_nothink_greedy_thread8` |
| **16** | 1 | 1 | 1 | 1 | 1 | `exp_16_all_enabled` |

---

## 3. Surrogate Machine Learning Modeling & Hyperdimensional Topology

Once the 16 physical runs are executed, we do not need to physically run the remaining 16 combinations on the GPU. Instead, we train a **Surrogate Regressor** with Scikit-Learn.

```text
┌──────────────────────────────────────┐
│  16 PHYSICAL GPU RUNS (CSV Dataset)  │
└──────────────────┬───────────────────┘
                   │ Features: [x1, x2, x3, x4, x5] -> Target: Latency / TPS
┌──────────────────▼───────────────────┐
│     SCIKIT-LEARN SURROGATE MODEL     │
│   HistGradientBoostingRegressor()    │
│  - Fits non-linear response surface  │
│  - Quantifies Feature Importances    │
└──────────────────┬───────────────────┘
                   │ Sub-millisecond Inference
┌──────────────────▼───────────────────┐
│  HYPERDIMENSIONAL SWEET SPOT FINDER  │
│  - Predicts all 32 combinations      │
│  - Identifies Global Minimum Latency │
│  - Parallel Coordinates Visualization│
└──────────────────────────────────────┘
```

### 3.1 Python Surrogate Model Architecture

```python
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance

def train_surrogate_model(csv_path: str):
    df = pd.read_csv(csv_path)
    
    # Feature matrix (5 binary dimensions)
    X = df[["flag_num_ctx", "flag_nothink", "flag_greedy", "flag_thread8", "flag_budget"]]
    y_latency = df["wall_time_sec"]
    y_tps = df["eval_tps"]
    
    # Fit Gradient Boosted Trees
    reg_latency = HistGradientBoostingRegressor(max_iter=100, min_samples_leaf=2)
    reg_latency.fit(X, y_latency)
    
    # Predict entire 32-combination space
    all_32_combinations = ... # Full grid
    predicted_latencies = reg_latency.predict(all_32_combinations)
    
    # Find theoretical global minimum
    optimal_idx = predicted_latencies.argmin()
    print(f"Optimal Configuration Predicted: {all_32_combinations[optimal_idx]}")
```

### 3.2 Hyperdimensional Visualizations

1. **Parallel Coordinates Plot:** Plots each parameter dimension as a vertical axis, connecting runs with colored lines (gradient mapped to Tokens/s or Latency).
2. **SHAP (SHapley Additive exPlanations):** Measures the exact contribution of each parameter to generation acceleration.

---

## 4. Mathematical Formalism: Pareto Optimal Inference Frontier

### 4.1 Multi-Objective Optimization Problem

We formulate inference tuning as a constrained multi-objective optimization problem over configuration space $\Omega$:

$$\max_{\mathbf{x} \in \Omega} \mathbf{F}(\mathbf{x}) = \begin{bmatrix} f_{\text{quality}}(\mathbf{x}) \\ -f_{\text{latency}}(\mathbf{x}) \\ f_{\text{throughput}}(\mathbf{x}) \end{bmatrix}$$

Subject to:
$$f_{\text{quality}}(\mathbf{x}) \ge 85.0 \quad (\text{Strict AST Syntax \& Functionality Floor})$$

```text
       Nota do Código (Qualidade 0-100)
       100 ▲                ┌──────────────────┐
           │                │ ★ SWEET SPOT     │
           │                │ (Score=100, t=16s)│
        85 ┼────────────────┼──────────────────┴───────────────
           │                │   ● Baseline (Score=100, t=212s)
           │                │
           │   ● Truncated  │
           │  (Score=45, t=75s)
           │
         0 └────────────────┼─────────────────────────────────►
           0               30                                220
                                Latência Total (Segundos)
```

---

## 5. Hierarchical Multi-Agent Swarm Orchestrator (Planner-Worker Architecture)

Instead of relying on a single monolithic model, the system establishes a **3-Tier Asymmetric Multi-Agent Swarm** that assigns tasks according to model parameter capacity, memory footprint, and generation velocity.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TIER 0: CLIENT INGESTION                               │
│                         High-Level Specification / User Goal                           │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Raw Prompt
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                    TIER 1: FAST ROUTER & TRIAGE (Qwen 2.5 1.5B)                        │
│ - Generation Speed: >130 tokens/second | Latency: <0.3s                                │
│ - Responsibility: Classify complexity, estimate token budget, route to Tier 2 or 3     │
└─────────────────────┬────────────────────────────────────────────────────┬─────────────┘
                      │ Simple Syntax / Lookup                             │ Complex Refactor / Arch
                      │                                                    │
                      │                        ┌───────────────────────────▼─────────────┐
                      │                        │   TIER 2: THE ARCHITECT & PLANNER       │
                      │                        │          (Qwen 3.8 27B)                 │
                      │                        │ - High-Order System Reasoning           │
                      │                        │ - Decomposes task into JSON Contracts   │
                      │                        │ - Outputs: AST Signatures & Test Cases  │
                      │                        └───────────────────────────┬─────────────┘
                      │                                                    │
                      └────────────────────────┬───────────────────────────┘
                                               │ Atomic Sub-Task Prompts
┌──────────────────────────────────────────────▼─────────────────────────────────────────┐
│                        TIER 3: PARALLEL WORKER CODERS & TESTERS                        │
│                                 (Qwen 2.5 Coder 14B)                                   │
│ - Generation Speed: ~28 tokens/second | Latency: 10–18s                                │
│ - Worker A: Implements function body (`module.py`)                                     │
│ - Worker B: Implements unit test suite (`test_module.py`)                              │
└──────────────────────────────────────────────┬─────────────────────────────────────────┘
                                               │ Generated Code & Tests
┌──────────────────────────────────────────────▼─────────────────────────────────────────┐
│                       TIER 4: LOCAL CLOSED-LOOP EXECUTION ENGINE                       │
│ - Environment: WSL2 Linux Subprocess (`python3 -m unittest` / `ruff check`)            │
│ - Success -> Return artifact to user.                                                  │
│ - Failure -> Pass Traceback to Worker Coder for autonomous 4-second micro-patch.       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Autonomous Self-Healing Feedback Loop

When code generated by the Worker fails verification, the engine initiates an automated local correction loop without human intervention:

```text
┌──────────────────────────────────────┐
│  Worker Coder Generates `module.py`  │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│ Subprocess executes: `pytest -q`     │
└──────────────────┬───────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   [Tests Pass]          [AssertionError / Exception]
        │                     │
┌───────▼────────┐     ┌──────▼────────────────────────────────────────┐
│ Deliver Output │     │ Hotfix Request to Qwen 2.5 Coder 14B:         │
│  to User / Disk│     │ - Original Code Snippet                       │
└────────────────┘     │ - Captured Terminal Traceback                 │
                       │ - Prompt: "Fix only the failing line."        │
                       └──────────────────────┬────────────────────────┘
                                              │
                                       (Repeats in <5s)
```
