---
id: agents-capability-architecture
class: specification
authority: operational
canonical_for:
  - agent-capabilities
  - skills-techniques-proficiencies
status: living
owner: capability-architecture
version: "1.0.0"
last_verified: 2026-09-05
supersedes: []
superseded_by: null
---

# Universal Agent Capability Architecture: Skills, Techniques, & Proficiencies

This document establishes the formal architectural and mathematical foundation for agent capabilities within the Vanguard / AETHER ecosystem. It defines the four-tier ontological progression, the operational contracts for atomic execution, the open-loop and closed-loop composition patterns, and the integration interfaces across the runtime lattice and Model Context Protocol (MCP) clients.

---

## 1. The Ontological Progression of Agency

Autonomous software engineering agents exhibit a structured progression of cognitive competence:

$$\text{Level 1: Skill} \xrightarrow{\quad\text{composition}\quad} \text{Level 2: Technique} \xrightarrow{\quad\text{feedback closure}\quad} \text{Level 3: Proficiency} \xrightarrow{\quad\text{meta-adaptation}\quad} \text{Level 4: Mastery}$$

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ LEVEL 4: MASTERY (Dynamic Meta-Heuristics & Self-Evolving Policy)                        │
│ - Online algorithm selection, multi-agent game-theoretic equilibrium, learned weights   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 3: PROFICIENCY (Closed-Loop SWE Feedback with State Machine)                      │
│ - FSM-governed iteration, incremental AST delta indexing (<30ms), fail-closed rollback │
│ - Example: autofix-swe-loop                                                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 2: TECHNIQUE (Synergistic Open-Loop Capability Composition)                       │
│ - Static composition of 2+ atomic skills; unidirectional execution pipeline             │
│ - Examples: spec-driven-codegen (LDA + LLM), tdd-falsifier (LDA + TestRunner)           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ LEVEL 1: SKILL (Atomic Execution Primitive)                                             │
│ - Single-responsibility, hermetic, zero internal loops, stateless execution            │
│ - Examples: test-runner, lda-navigator, llama-cpp, lam-engine                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Formal Mathematical Definitions

1. **Atomic Skill ($\mathcal{S}$):**
   An atomic skill is a deterministic or stochastic mapping $\mathcal{S}: \mathcal{X} \to \mathcal{Y}$ over a bounded execution time $t < T_{\max}$ with no internal control loops ($\text{depth} = 0$). It satisfies hermetic containment:
   $$\forall x \in \mathcal{X}, \quad \text{State}(\text{Host})_{t_0} \equiv \text{State}(\text{Host})_{t_1 \setminus \text{effects}(y)}$$

2. **Technique ($\mathcal{T}$):**
   A technique is a directed acyclic composition of $k \ge 2$ atomic skills $\mathcal{S}_1, \dots, \mathcal{S}_k$:
   $$\mathcal{T}(x) = (\mathcal{S}_k \circ \dots \circ \mathcal{S}_2 \circ \mathcal{S}_1)(x)$$
   Techniques are strictly **open-loop**: data propagates downstream without dynamic control branches or iterative repair cycles.

3. **Proficiency ($\mathcal{P}$):**
   A proficiency is a closed feedback loop governed by a discrete Finite State Machine (FSM) $\mathcal{M} = (Q, \Sigma, \delta, q_0, F)$ where state transitions depend on empirical verification receipts (oracles, compiler diagnostics, unit tests):
   $$q_{t+1} = \delta(q_t, \text{Receipt}_t), \quad \text{where } \text{Receipt}_t = \mathcal{T}_{\text{verify}}(\text{Patch}_t)$$
   A proficiency guarantees:
   - **Monotonic progress or fail-closed abort:** $\text{turns} \le N_{\max}$.
   - **State consistency:** On failure to reach $q \in F$, rollback occurs: $\text{Filesystem}_{t_{\text{end}}} \equiv \text{Filesystem}_{t_0}$.
   - **AST Synchronization:** Incremental re-indexing latency satisfies $\tau_{\text{sync}} < 30\,\text{ms}$.

4. **Mastery ($\mathcal{M}$):**
   Adaptive meta-heuristic routing that dynamically configures proficiencies, models, and hyperparameters based on observed repository topology, historical entropy, and budget constraints.

---

## 2. Directory Taxonomy & Component Map

The repository segregates agent capabilities strictly by ontological depth under `.agents/`:

```text
.agents/
├── skills/                          # Tier 1: Atomic primitives (no internal loops)
│   ├── test-runner/                 # Isolated subprocess test execution & JSON parsing
│   ├── lda-navigator/               # Token-bounded AST retrieval & caller graph queries
│   ├── llama-cpp/                   # Zero-cost local GGUF inference via native llama-server
│   ├── lam-engine/                  # LLM API Mock for sub-millisecond offline replay
│   ├── spec-driven-codegen/         # Backward-compatibility skill bridge -> technique
│   ├── tdd-falsifier/               # Backward-compatibility skill bridge -> technique
│   └── autofix-loop/                # Backward-compatibility skill bridge -> proficiency
│
├── techniques/                      # Tier 2: Open-loop compositions
│   ├── spec-driven-codegen/         # Compose: lda-navigator + llama-cpp
│   └── tdd-falsifier/               # Compose: lda-navigator + test-runner
│
└── proficiencies/                   # Tier 3: Closed-loop SWE feedback loops
    └── autofix-swe-loop/            # Compose: T1 + T2 + AST Delta + Fail-Closed Rollback
```

---

## 3. Subsystem Specifications

### 3.1. Skill: `test-runner`
- **Location:** `.agents/skills/test-runner/`
- **Interface:** `scripts/run_test.py`
- **Responsibilities:**
  - Hard subprocess isolation with non-blocking pipes and timeout-bounded kill trees (`SIGTERM` $\to 500\,\text{ms} \to$ `SIGKILL`).
  - Robust regex state parsing across Python `unittest` (handling multiline docstrings and verbose traceback blocks) and `pytest`.
  - Emits normalized JSON schema containing: `success`, `exit_code`, `duration_seconds`, `failures_count`, `errors_count`, `failures[]`, and `summary`.

### 3.2. Skill: `lda-navigator`
- **Location:** `.agents/skills/lda-navigator/`
- **Interface:** `uv run lda [plan|resolve|context|callers|index --delta]`
- **Responsibilities:**
  - Sub-30ms AST querying and graph traversal over SQLite index (`.lda/index.db`).
  - Zero idle memory (no persistent daemon); token-budgeted context compaction (`--budget N`).
  - Incremental AST delta synchronization (`lda index --delta`) executed in $<25\,\text{ms}$.

### 3.3. Skill: `llama-cpp`
- **Location:** `.agents/skills/llama-cpp/`
- **Interface:** Native `llama-server` on `127.0.0.1:8080/v1/chat/completions`
- **Responsibilities:**
  - Local GPU-offloaded GGUF inference (Vulkan/ROCm, e.g., AMD Radeon RX 9060 XT 16GB).
  - High-velocity generation (160–180 tok/s on Qwen2.5-Coder-1.5B).
  - Enforces `--reasoning off` for sub-3B syntax generation to prevent `<think>` token budget exhaustion.

### 3.4. Technique 1: `spec-driven-codegen`
- **Location:** `.agents/techniques/spec-driven-codegen/`
- **Composed Skills:** `lda-navigator` + `llama-cpp`
- **Flow:**
  1. Calls `lda resolve` and `lda context` to extract precise AST slices and imports within budget.
  2. Compiles a high-density, prompt-free code synthesis template.
  3. Queries `llama-server` to emit clean, syntactically grounded code blocks.

### 3.5. Technique 2: `tdd-falsifier`
- **Location:** `.agents/techniques/tdd-falsifier/`
- **Composed Skills:** `lda-navigator` + `test-runner`
- **Flow:**
  1. Queries LDA callers and test relations for the target file/symbol.
  2. Synthesizes the exact test execution command.
  3. Dispatches `test-runner` with a bounded timeout (default: $10.0\,\text{s}$).

### 3.6. Proficiency: `autofix-swe-loop`
- **Location:** `.agents/proficiencies/autofix-swe-loop/`
- **Composed Elements:** `spec-driven-codegen` + `tdd-falsifier` + `lda index --delta`
- **FSM State Machine:**
  - $S_0$ (`VERIFY_BASELINE`): Runs `tdd-falsifier`. If passing, aborts immediately with `ALREADY_PASSING`.
  - $S_1$ (`GENERATE_PATCH`): Runs `spec-driven-codegen` with accumulated traceback diagnostics.
  - $S_2$ (`APPLY_AND_SYNC`): Writes candidate patch to disk and triggers `lda index --delta` ($<25\,\text{ms}$).
  - $S_3$ (`VERIFY_PATCH`): Runs `tdd-falsifier`.
    - If `PASS`: Transition to $S_4$ (`RESOLVED`). Emit clean unified diff and telemetry.
    - If `FAIL` and $t < T_{\max}$: Accumulate new traceback and loop to $S_1$.
    - If `FAIL` and $t \ge T_{\max}$: Transition to $S_5$ (`ROLLBACK`). Restore original file byte-for-byte; exit with failure code.

---

## 4. Empirical Evaluation: Ontological Comparison

Empirical evaluation executed on an AMD Radeon RX 9060 XT (16 GB VRAM) using `Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf` on an off-by-one sliding window rate limiter defect (`tools/model_benchmarks/experiments/bench_ontological_progression.py`):

| Mode | Ontological Level | Turns | Pass / Fail | Total Time | Tokens | AST Sync Latency | Defect Elimination |
|---|---|---|---|---|---|---|---|
| **Mode 0** | Blind Zero-shot (Raw Prompt) | 1 turn | **FAIL** (0/3 tests) | 1.32s | 184 | N/A | Corrupted sliding window bounds; syntax errors |
| **Mode 1** | Technique 1 (Spec-Driven Open-Loop) | 1 turn | **FAIL** (0/3 tests) | 2.16s | 231 | N/A | Accurate signature, off-by-one window cutoff |
| **Mode 2** | **Proficiency (Autofix SWE Loop)** | **2 turns** | **PASS (3/3 tests)** | **3.96s** | **559** | **22ms (`lda --delta`)** | **100% verified repair with clean diff** |

### Key Scientific Findings
1. **The Inadequacy of Open-Loop Generation:** Open-loop techniques (even when grounded with AST slices) fail on subtle semantic edge cases when using small models ($\sim 1.5\text{B}$ parameters).
2. **Convergence through Closed-Loop Telemetry:** Ingesting structured test diagnostics and original pristine code in Turn 2 resolved 100% of failing assertions in $<4.0\,\text{s}$ wall-clock time without human intervention.
3. **AST Delta Invariance:** Sub-30ms incremental indexing (`lda index --delta`) ensures the cognitive engine's symbolic graph remains mathematically consistent across mutating loop iterations.

---

## 5. Hexagonal Runtime Catalog & Prompt Budget Protocol

The production runtime discovers capabilities declaratively through `vanguard/packages/runtime/agent_plugins.py`.

### Architectural Invariant N-06 Compliance
In accordance with Invariant `N-06`, `vanguard/packages/runtime/` strictly forbids `subprocess` imports. `agent_plugins.py` provides pure declarative metadata discovery, category filtering, and token-bounded prompt prefix compilation. Subprocess execution logic is strictly segregated into `tools/` and `.agents/`.

### Prompt Prefix Budget (`W12-A`)
To prevent capability descriptions from crowding out reasoning context, the prompt prefix generator conforms to the following budget constraint:
$$\text{Length}(\text{Prefix}) < 4096 \text{ characters} \quad (\approx 1000 \text{ tokens})$$
As verified by unit tests, the active 8-plugin catalog consumes only **1774 characters** ($\approx 430$ tokens), leaving $>85\%$ of the headroom intact.

---

## 6. Unified CLI & Model Context Protocol (MCP) Interface

Capabilities are exposed via two standard communication surfaces:

### 6.1. Unified CLI (`tools/agent_plugins/cli.py`)
```bash
# List all registered capabilities with category and description
python3 tools/agent_plugins/cli.py list

# Emit token-budgeted prompt prefix (<4096 chars)
python3 tools/agent_plugins/cli.py prefix

# Execute an atomic test
python3 tools/agent_plugins/cli.py run test-runner "python3 -m unittest test.kernel.test_dispatch -v"

# Execute closed-loop SWE repair
python3 tools/agent_plugins/cli.py autofix \
  --task "Fix off-by-one in limiter" \
  --file "path/to/file.py" \
  --max-turns 3
```

### 6.2. Universal MCP Server (`tools/agent_plugins/mcp_server.py`)
A stdio JSON-RPC server implementing the Model Context Protocol:
- **`agent_list_plugins`**: Returns the catalog of skills, techniques, and proficiencies.
- **`agent_run_test`**: Runs an isolated, timeout-bounded test suite and returns parsed diagnostics.
- **`agent_generate_patch`**: Runs spec-driven code generation with AST context and error feedback.
- **`agent_run_falsifier`**: Discovers and executes targeted test suites for a symbol or file.
- **`agent_autofix`**: Runs the complete closed-loop SWE repair state machine.

### 6.3. Multi-Harness Synchronization
Running `python3 tools/universal_mcp_sync.py` automatically validates and synchronizes the 4-quad MCP configuration across:
- **Cursor:** `.cursor/mcp.json`
- **Claude Code:** `~/.claude.json`
- **OpenAI Codex:** `~/.codex/mcp.json`
- **Google Antigravity:** `~/.gemini/antigravity-cli/mcp_config.json`
