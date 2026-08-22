# Product Requirements Document (PRD) — LEX Engine v1.0

> **Document Title:** Product Requirements Document (PRD) — LEX Autonomous Coding Swarm  
> **Status:** Approved / Canonical Product Law  
> **Product Code:** `LEX`  
> **Target Release:** v1.0.0 Enterprise  
> **Author:** AI Agentic Architecture Group (Principal Architect, Staff Systems Engineer, VP of Product)  

---

## 1. Product Vision & Market Problem Statement

### 1.1. The Problem
Enterprise software engineering teams and autonomous coding agent developers face a critical triad of blockers when using centralized cloud LLMs (OpenAI, Anthropic, Google):
1. **Data Sovereignty & IP Leakage:** Proprietary code, secrets, and algorithms cannot leave private workstations or VPCs.
2. **Cost & Latency at Scale:** Cloud API roundtrips incur significant per-token recurring OPEX and latency spikes (30s–90s per multi-turn task).
3. **Unverified Code & Hallucinations:** Large models generate plausibly looking code that fails silently at runtime or creates collusive unit tests (`assert True`) that deceive developers.
4. **VRAM Thrashing on Local Hardware:** Existing open-source agent tools attempt to run single giant models or haphazardly load/unload models, thrashing local GPU VRAM and crashing workstations.

### 1.2. The Product Vision
**LEX** is the **first local, hardware-aware, evidentiary multi-agent coding engine** that turns consumer/workstation GPUs (AMD Radeon 16GB–24GB / NVIDIA RTX 16GB–24GB) into a **private, sub-25-second, zero-hallucination code synthesizer and self-healing laboratory**.

---

## 2. Target Personas & Primary Use Cases

| Persona | Role & Environment | Primary Pain Point | LEX Value Proposition |
|:---|:---|:---|:---|
| **Principal Software Architect** | Enterprise backend, microservices | Requires strict interface contracts, typed domain models, and zero architecture drift. | LEX compiles intents into formal `TaskGraph IR` with immutable type signatures before coding starts. |
| **Staff AI Systems Engineer** | Local agentic workflows, autonomous pipelines | Needs reliable tool calls via MCP without polling or hallucinated test results. | LEX exposes an MCP Tool Server returning cryptographically signed `AgentExecutionEnvelope`s with real evidence. |
| **Privacy-Centric Developer** | Financial, defense, healthcare systems | 100% cloud airgap requirement; zero external network egress. | LEX operates completely offline on local Ollama weights with network-isolated sandboxes. |
| **Autonomous Agent Framework (e.g. Vanguard)** | Parent agent orchestrator | Needs delegated subagents (`agent.spawn`) with bounded budgets and verifiable execution proofs. | LEX accepts `TaskRequestEnvelope` with strict budgets/grants and returns zero-copy file references. |

---

## 3. Product Features & Functional Requirements (FR)

### FR-1: Tiered Swarm Hierarchical Decomposition
- **FR-1.1:** The system SHALL provide an O(1) heuristic risk filter and a lightweight 1.5B Router model (`qwen2.5:1.5b`) for instant triage (< 0.15s).
- **FR-1.2:** The system SHALL invoke a 27B / 30B Architect model (`qwen3.8:27b` / `qwen3-coder:30b`) to compile user requests into a `TaskGraph IR` with typed interfaces, invariants, and falsifiable acceptance criteria.
- **FR-1.3:** The system SHALL invoke 14B Worker models (`qwen2.5-coder:14b`) in concurrent slots (`OLLAMA_NUM_PARALLEL=2`) to synthesize implementation and test modules in parallel.

### FR-2: Active Hardware VRAM & Lifecycle Management
- **FR-2.1:** The system SHALL enforce an active VRAM polling drain protocol before loading worker models, polling `GET /api/ps` until `size_vram == 0` is confirmed.
- **FR-2.2:** The system SHALL co-reside Router (1.5B) and Workers (14B) in VRAM with `OLLAMA_MAX_LOADED_MODELS=2`, never exceeding 13.5GB VRAM on a 24GB hardware budget.

### FR-3: 3-Tier Rootless Sandbox Execution
- **FR-3.1:** The system SHALL execute all generated code inside an isolated sandbox using Bubblewrap (`bwrap`) as Tier A or Linux User Namespaces (`unshare -U -n -r`) as Tier B.
- **FR-3.2:** If isolated sandboxing is unavailable, the system SHALL enforce **Fail-Closed** security (Tier C), refusing dynamic code execution and falling back to static AST analysis.
- **FR-3.3:** The system SHALL bound all subprocess executions by CPU time (10s), memory limits (256MB), and network disabled (`--unshare-net`).

### FR-4: Multi-Operator Mutation Testing & Anti-Collusion
- **FR-4.1:** The system SHALL perform AST assertion density audits on all generated test files, rejecting tests with 0 explicit assertions.
- **FR-4.2:** The system SHALL apply AST mutations (`OP_COMPARE_INVERT`, `OP_BOOLEAN_FLIP`, `OP_RETURN_SWAP`) to candidate code; if tests pass on broken code, the test suite SHALL be rejected as collusive.

### FR-5: Diagnosis-Driven Self-Healing Loop
- **FR-5.1:** The system SHALL categorize validation failures into a typed `FailureKind` taxonomy (`IMPLEMENTATION_ERROR`, `TEST_COLLUSION`, `CONTRACT_CONTRADICTION`, `SYNTAX_LINT_ERROR`, `SANDBOX_RESOURCE_OOM`).
- **FR-5.2:** The system SHALL track SHA-256 state hashes ($\text{RepairStateHash}_n == \text{RepairStateHash}_{n-2}$) and trip a circuit breaker upon detecting oscillation or non-progress.

### FR-6: Universal Protocol & Zero-Copy Wire Envelopes
- **FR-6.1:** The system SHALL accept standard `TaskRequestEnvelope` inputs and emit `TaskResponseEnvelope` (`AgentExecutionEnvelope`) outputs over MCP (stdio JSON-RPC), CLI, and WebSocket.
- **FR-6.2:** The system SHALL support Zero-Copy storage references (`storage.kind: "WORKSPACE_FILE"`), passing file URIs and SHA-256 digests instead of bloated inline strings.
- **FR-6.3:** The system SHALL propagate W3C `traceparent` headers across all telemetry spans.

---

## 4. Non-Functional Requirements (NFR) & Quality SLOs

| Category | Metric / Target | Verification Method |
|:---|:---|:---|
| **Latency (L0 Direct)** | P50 < 12 seconds, P95 < 20 seconds | Empirical benchmark runner (`bench_matrix.py`) |
| **Latency (L1 Structured)**| P50 < 28 seconds, P95 < 45 seconds | Empirical benchmark runner |
| **Self-Healing MTTR** | Average recovery iteration < 4.5 seconds | Telemetry event log timestamp deltas |
| **VRAM Consumption** | Peak VRAM ≤ 13.5 GB (on 24GB GPU) | Active polling via `GET /api/ps` / ROCm SMI |
| **Mutation Score** | 100% of non-equivalent mutants caught | AST mutation test runner (`mutation_evaluator.py`) |
| **Test Hermeticity** | 100% unit tests pass with zero GPU / zero network | CI test suite running with `FakeLlmProvider` |
| **Security Isolation** | Zero network egress, zero filesystem escape | Adversarial sandbox test suite (`test_sandbox_security.py`)|
| **Code Modularity** | Hexagonal boundary enforcement (0 illegal imports)| CI boundary linter (`linters/check_boundaries.py`) |

---

## 5. Competitive Landscape & 1-Billion-Dollar Moat

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LEX COMPETITIVE MATRIX                             │
├────────────────────┬──────────────┬──────────────┬──────────────┬───────────┤
│ Capability         │ LEX (Ours)   │ Claude Code  │ Cursor / IDE │ Aider     │
├────────────────────┼──────────────┼──────────────┼──────────────┼───────────┤
│ 100% Airgap Local  │  YES (Local) │ ❌ Cloud API │ ❌ Cloud API │ ⚠️ Hybrid │
│ Multi-Model Swarm  │  YES (Tiered)│ ❌ Single LLM│ ❌ Single LLM│ ❌ Single │
│ VRAM Drain Control │  YES (Metal) │ N/A          │ N/A          │ ❌ None   │
│ Mutation Probing   │  YES (AST)   │ ❌ None      │ ❌ None      │ ❌ None   │
│ Signed SLSA Receipt│  YES (Ed25519)❌ None      │ ❌ None      │ ❌ None   │
│ Standard MCP Server│  YES (Native)│ ⚠️ Client    │ ⚠️ Client    │ ❌ None   │
│ Sub-25s Local Time │  YES (14B/27B)❌ 30s-90s API│ ⚠️ Variable  │ ⚠️ Variable│
└────────────────────┴──────────────┴──────────────┴──────────────┴───────────┘
```

---

## 6. Success Metrics & Product KPIs

1. **Pass@1 Rate (HumanEval+ / MBPP):** $\ge 85\%$ first-pass, $\ge 95\%$ post-healing.
2. **SWE-bench Verified Resolution Rate:** $\ge 45\%$ on local weights.
3. **First-Pass Synthesis Rate:** $\ge 70\%$ of standard tasks pass without entering self-healing.
4. **Zero-Collusion Guarantee:** $0\%$ false-positive tests passing mutation probes.
5. **Developer Adoption:** Seamless 1-command startup (`make test && python -m tools.004_LLM_EXECUTION_X.entrypoints.cli`).
