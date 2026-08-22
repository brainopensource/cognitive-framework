# Macro Roadmap & Milestone Ladders — LEX v1.0

> **Subsystem Path:** `tools/004_LLM_EXECUTION_X/`  
> **Status:** Approved / Living Macro Plan  
> **Planning Horizon:** Sprints 0 through 9 (v1.0 Production Readiness)  
> **Estimation Method:** Modified Fibonacci Story Points (1 SP = ~0.5 Engineering Day)  

---

## 1. Macro Milestone Ladder

```text
M-0 (Foundation Lock) ──► M-1 (Vertical Slice) ──► M-2 (Measurement Lab) ──► M-3 (Swarm & DAG) ──► M-4 (Self-Healing) ──► M-5 (Productization)
[Sprint 0]                 [Sprint 1]               [Sprint 2]                [Sprints 3-4]          [Sprints 5-7]           [Sprints 8-9]
```

---

## 2. Granular Sprint Roadmap

### Sprint 0: Architecture Lock & Boundary Enforcement
* **Goal:** Establish domain primitives, typing protocols, JSON schemas, and automated CI boundary linters.
* **Deliverables:**
  - `domain/` value objects (`task_graph.py`, `evidence.py`, `verdict.py`, `receipt.py`, `errors.py`, `values.py`).
  - `ports/` protocol interfaces (`model_provider.py`, `sandbox.py`, `telemetry.py`).
  - `linters/check_boundaries.py` enforcing hexagonal imports.
  - `config/lex_config.schema.json` and base configuration.
* **Story Points:** 5 SP
* **Exit Gate:** `make lint` and 100% unit tests pass with zero violations.

---

### Sprint 1: Thin Vertical Slice (The Minimum Real Circuit)
* **Goal:** Execute the first complete linear synthesis chain from CLI prompt to verified execution envelope.
* **Deliverables:**
  - `adapters/ollama_adapter.py` (Worker 14B call).
  - `adapters/sandbox/unshare_sandbox.py` (Subprocess tempdir runner).
  - `adapters/file_telemetry.py` (JSONL logger).
  - `engine/orchestrator.py` linear pipeline:
    $$\text{Request} \longrightarrow \text{TaskNode} \longrightarrow \text{Worker 14B} \longrightarrow \text{Sandbox} \longrightarrow \text{Evidence} \longrightarrow \text{Verdict} \longrightarrow \text{Envelope}$$
  - `tests/fakes/` hermetic test suite (`test_thin_vertical_slice.py`).
* **Story Points:** 8 SP
* **Exit Gate:** Hermetic E2E test passes in CI without GPU; live run creates valid `.py` + `test_.py` in < 20s.

---

### Sprint 2: Measurement Harness & Baseline Telemetry
* **Goal:** Build empirical measurement tools to capture real hardware latency, token speed, and VRAM usage.
* **Deliverables:**
  - `entrypoints/benchmark_runner.py` with HumanEval mini-suite (20 problems).
  - Telemetry exporter (CSV + JSONL + W3C TraceContext).
  - Active VRAM capacity profiler.
* **Story Points:** 5 SP
* **Exit Gate:** Baseline benchmark report generated with zero missing/fabricated token metrics.

---

### Sprint 3: `TaskGraph IR`, Context Compiler (RAG) & 27B Architect
* **Goal:** Implement hierarchical intent decomposition into multi-module semantic contracts.
* **Deliverables:**
  - `engine/architect.py` invoking Qwen 27B with Structured Output JSON Schema.
  - `engine/prompt_compiler.py` compiling `TaskNode` into model-specific prompts.
  - `adapters/context_provider.py` local AST repository indexer (~500 token context window).
* **Story Points:** 13 SP
* **Exit Gate:** 27B generates valid multi-module `TaskGraph IR` for 10 distinct complex prompts.

---

### Sprint 4: Multi-Module Topological DAG Worker Pool
* **Goal:** Execute multi-file synthesis in dependency order with concurrent worker execution.
* **Deliverables:**
  - `engine/worker_pool.py` topological sort and async dispatch.
  - Concurrent Coder + Tester execution (`OLLAMA_NUM_PARALLEL=2`).
  - Active VRAM drain polling protocol (`GET /api/ps` -> `size_vram == 0`).
* **Story Points:** 8 SP
* **Exit Gate:** 3-file microservice synthesized in topological order with zero VRAM crashes on 24GB GPU.

---

### Sprint 5: Independent Verification & Multi-Operator Mutation Engine
* **Goal:** Eliminate test-code collusion through AST assertion density audits and active mutation probes.
* **Deliverables:**
  - `adapters/evidence/ast_evaluator.py` (Assertion density counter).
  - `adapters/evidence/mutation_evaluator.py` (5 mutation operators).
  - VerificationPolicy mutation threshold enforcement.
* **Story Points:** 8 SP
* **Exit Gate:** 100% of tautological tests (`assert True`) caught and rejected by mutation probe.

---

### Sprint 6: Diagnosis-Driven Self-Healing & Anti-Thrashing FSM
* **Goal:** Implement semantic failure diagnosis and state-hash oscillation circuit breakers.
* **Deliverables:**
  - `engine/failure_diagnostician.py` (`FailureKind` classification).
  - `engine/anti_thrashing.py` ($\text{RepairStateHash}_n == \text{RepairStateHash}_{n-2}$).
  - `engine/self_healing.py` surgical patch generation with cumulative error memory.
* **Story Points:** 13 SP
* **Exit Gate:** Intentionally broken code auto-corrected in $\le 2$ cycles; duplicate tracebacks trip circuit breaker.

---

### Sprint 7: 3-Tier Rootless Sandbox Hardening
* **Goal:** Production-grade security sandboxing with zero `preexec_fn` deadlocks.
* **Deliverables:**
  - `adapters/sandbox/bwrap_sandbox.py` (Bubblewrap Tier A).
  - `adapters/sandbox/unshare_sandbox.py` (User Namespaces Tier B).
  - `adapters/sandbox/static_sandbox.py` (Fail-closed Tier C fallback).
* **Story Points:** 8 SP
* **Exit Gate:** Adversarial security suite passes (network access blocked, filesystem escape blocked).

---

### Sprint 8: Full `LEX-Bench` Suite Execution (CASE-001..015)
* **Goal:** Execute the full 15-case benchmark matrix and validate real-world repository repairs.
* **Deliverables:**
  - Implementation of all 15 `LEX-Bench` scenarios.
  - SWE-bench Verified subset evaluation runner.
* **Story Points:** 8 SP
* **Exit Gate:** $\ge 85\%$ pass@1 on HumanEval+, 15/15 `LEX-Bench` cases pass.

---

### Sprint 9: Productization: Protected MCP Server & Real-Time Rich TUI
* **Goal:** Expose LEX as an MCP tool server and deliver a beautiful terminal interface.
* **Deliverables:**
  - `entrypoints/mcp_server.py` (JSON-RPC 2.0 stdio tool server with `WorkspaceGrant` bounds).
  - `engine/ui_renderer.py` (Rich live terminal dashboard with live tokens/s and VRAM telemetry).
  - Packaging & distribution setup (`pyproject.toml`, standalone Rust FFI bindings).
* **Story Points:** 5 SP
* **Exit Gate:** External coding agents (Claude Code, Cursor, Vanguard) successfully call `lex_synthesize` over MCP stdio.

---

## 3. Total Velocity & Release Timeline

* **Total Story Points:** 81 SP (~40 Engineering Days)
* **Milestone 1 (Sprint 0–1):** Day 1–7 (Working Vertical Slice)
* **Milestone 2 (Sprint 2–4):** Day 8–20 (Swarm & DAG Core)
* **Milestone 3 (Sprint 5–7):** Day 21–32 (Verification & Self-Healing Moat)
* **Milestone 4 (Sprint 8–9):** Day 33–40 (Enterprise Productization & MCP Server)
