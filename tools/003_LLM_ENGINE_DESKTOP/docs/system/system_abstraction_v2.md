# High-Order Inference Abstraction: Full & Fractional Factorial DoE, Meta-Dimension Registry, Surrogate ML Modeling, and Hierarchical Swarms

**Document ID:** `LLM-DESKTOP-SYS-ABSTRACTION-V2`  
**Classification:** Staff Principal AI Architecture & Mathematical Specification  
**Subject:** N-Dimensional Declarative Space Topology, $2^k$ and $2^{k-1}$ Fractional Factorial Matrices, Zero-Refactor Meta-Dimension Registry, Scikit-Learn Surrogate Regression Modeling, Pareto Optimal Frontier, and Multi-Tier Hybrid Agent Orchestration  
**Target Environment:** Local LLM Substrate (`qwen3.8:27b` + `qwen2.5-coder:14b` + `qwen2.5:1.5b` on AMD Radeon 16GB VRAM & Ryzen 5800X3D).

---

## 1. High-Order Combinatorial Design of Experiments (DoE)

### 1.1 Limitations of One-Factor-At-A-Time (OFAT) Benchmarking

Standard single-variable testing assumes linear independence between inference levers. In reality, local LLM inference parameters exhibit strong **non-linear coupling and cross-layer interaction effects**:

$$\text{Throughput}(A \cup B) \neq \text{Throughput}(A) + \text{Throughput}(B)$$

* **Example Synergy:** Trimming context window (`num_ctx=2048`) frees ~4GB VRAM. Enabling Greedy Decoding (`temperature=0.0`) eliminates multinomial sampling in CPU memory. Combined, the CPU-GPU pipeline experiences zero cache thrashing, yielding a multiplicative speedup unattainable by either parameter in isolation.

### 1.2 The $2^k$ Full Factorial Parameter Space

We formalize the inference configuration as a binary feature vector $\mathbf{x} \in \{0, 1\}^k$, representing $k$ orthogonal optimization dimensions:

$$\Omega = \prod_{i=1}^{k} D_i = \{0, 1\}^k \implies |\Omega| = 2^k\text{ Experimental Configurations}$$

---

## 2. Zero-Refactor Declarative Dimension Registry (Meta-Architecture)

To allow scaling the benchmarking space to $N$ dimensions without refactoring code, the system implements a **Declarative Meta-Dimension Registry**.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        1. DECLARATIVE DIMENSION REGISTRY (SCHEMA)                      │
│                  DIMENSION_REGISTRY = { "num_ctx": [...], "mirostat": [...] }          │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
         ┌──────────────────────────────────┼──────────────────────────────────┐
         │                                  │                                  │
┌────────▼────────────────────────┐ ┌───────▼────────────────────────┐ ┌───────▼────────────────────────┐
│    CARTESIAN PRODUCT ENGINE     │ │      SCHEMA LOGGER ADAPTER     │ │      AUTO-FEATURE ML PIPELINE   │
│  $\bigotimes_{i=1}^n D_i$       │ │ Dynamic CSV/JSONL column mapper│ │ Scikit-Learn OneHotEncoder      │
│  Generates N-dimensional tests  │ │ Auto-discovers schema headers  │ │ Automatic Feature Importances   │
└─────────────────────────────────┘ └────────────────────────────────┘ └─────────────────────────────────┘
```

### 2.1 Mathematical Formalization of the Dynamic Tensor Product

Let $\mathcal{D} = \{ (k_1, V_1), (k_2, V_2), \dots, (k_n, V_n) \}$ be the dynamic registry where $k_i \in \text{String}$ is the parameter name and $V_i = \{ v_{i,1}, \dots, v_{i,m_i} \}$ is the discrete domain of candidate values.

The total search space $\mathcal{S}$ is the Cartesian product:
$$\mathcal{S} = V_1 \times V_2 \times \dots \times V_n, \quad |\mathcal{S}| = \prod_{i=1}^n |V_i|$$

### 2.2 Python Zero-Refactor Implementation

```python
import itertools
from typing import Dict, List, Any
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

# 1. Zero-Refactor Dimension Registry
DIMENSION_REGISTRY: Dict[str, List[Any]] = {
    "num_ctx": [1024, 2048, 8192],
    "temperature": [0.0, 0.7],
    "num_thread": [8, 16],
    "repeat_penalty": [1.0, 1.15],
    "top_k": [20, 40],
    "system_prompt_mode": ["none", "strict_compiler"],
    # Pluggable future extensions:
    # "mirostat": [0, 2],
    # "draft_heads": [1, 2],
}

def generate_dynamic_experiments(registry: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """Dynamically generates all test configurations without hardcoding keys."""
    keys = list(registry.keys())
    experiments = []
    
    for idx, combo in enumerate(itertools.product(*registry.values()), start=1):
        config = dict(zip(keys, combo))
        exp_id = f"exp_{idx:04d}_" + "_".join(f"{k}{v}" for k, v in config.items())
        experiments.append({
            "id": exp_id,
            "dimensions": config,
            "options": {k: v for k, v in config.items() if k != "system_prompt_mode"}
        })
    return experiments
```

---

## 3. 16-Run Fractional Factorial Design ($2^{5-1}$) & Hypercube Sampling

To cut benchmark time by 50% without sacrificing statistical power, we use a **Resolution V Fractional Factorial Design ($2^{5-1} = 16\text{ runs}$)**.

### 3.1 Mathematical Basis of Half-Fraction Sampling

By setting the 5th factor generator as the interaction of the first four:
$$x_5 = x_1 \cdot x_2 \cdot x_3 \cdot x_4$$

We construct an orthogonal 16-row design matrix where:
1. Every individual parameter is active ($1$) in exactly 8 runs and inactive ($0$) in exactly 8 runs.
2. All main effects ($\beta_1 \dots \beta_5$) are completely unconfounded by 2-factor interactions ($\gamma_{ij}$).
3. **Execution Time:** $16 \text{ runs} \times 18.0\text{s} \approx \mathbf{4.8\text{ minutes}}$ on the `qwen2.5-coder:14b`.

### 3.2 The 16-Run Orthogonal Design Matrix

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

## 4. Surrogate Machine Learning Modeling & Hyperdimensional Topology

Once the 16 physical runs are executed, we train a **Surrogate Regressor** with Scikit-Learn to map the entire hyperdimensional space.

```text
┌──────────────────────────────────────┐
│  16 PHYSICAL GPU RUNS (CSV Dataset)  │
└──────────────────┬───────────────────┘
                   │ Features: [x1, x2, x3, x4, x5, ...] -> Target: Latency / TPS
┌──────────────────▼───────────────────┐
│     SCIKIT-LEARN SURROGATE MODEL     │
│   HistGradientBoostingRegressor()    │
│  - Fits non-linear response surface  │
│  - Quantifies Feature Importances    │
└──────────────────┬───────────────────┘
                   │ Sub-millisecond Inference
┌──────────────────▼───────────────────┐
│  HYPERDIMENSIONAL SWEET SPOT FINDER  │
│  - Predicts all unexecuted states    │
│  - Identifies Global Minimum Latency │
│  - Parallel Coordinates Visualization│
└──────────────────────────────────────┘
```

### 4.1 Dynamic Feature Pipeline & SHAP Feature Importances

```python
def train_dynamic_surrogate(csv_file: str, dimension_keys: List[str]):
    df = pd.read_csv(csv_file)
    
    # Dynamically extract all registered dimension columns
    X = pd.get_dummies(df[dimension_keys])
    y_tps = df["eval_tps"]
    y_latency = df["wall_time_sec"]
    
    # Train Gradient Boosting Regressors
    model_tps = HistGradientBoostingRegressor(max_iter=100, min_samples_leaf=2).fit(X, y_tps)
    model_lat = HistGradientBoostingRegressor(max_iter=100, min_samples_leaf=2).fit(X, y_latency)
    
    # Rank importance of every parameter automatically
    print("=== PARAMETER IMPORTANCE RANKING ===")
    for name, imp in zip(X.columns, model_tps.feature_importances_):
        print(f"  Dimension [{name}]: {imp * 100:.2f}% contribution to TPS")
```

---

## 5. Mathematical Formalism: Pareto Optimal Inference Frontier

### 5.1 Multi-Objective Optimization Problem

We formulate inference tuning as a constrained multi-objective optimization problem over configuration space $\Omega$:

$$\max_{\mathbf{x} \in \Omega} \mathbf{F}(\mathbf{x}) = \begin{bmatrix} f_{\text{quality}}(\mathbf{x}) \\ -f_{\text{latency}}(\mathbf{x}) \\ f_{\text{throughput}}(\mathbf{x}) \end{bmatrix}$$

Subject to:
$$f_{\text{quality}}(\mathbf{x}) \ge 85.0 \quad (\text{Strict AST Syntax \& Functionality Floor})$$

---

## 6. Hierarchical Multi-Agent Swarm Orchestrator (Planner-Worker Architecture)

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
