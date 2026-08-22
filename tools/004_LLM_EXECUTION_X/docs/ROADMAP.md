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
* **Goal:** Establish Rust domain primitives, async trait protocols, Serde JSON schemas, and module boundary checks.
* **Deliverables:**
  - `src/domain/` value objects (`task_graph.rs`, `evidence.rs`, `verdict.rs`, `receipt.rs`, `errors.rs`, `values.rs`).
  - `src/ports/` async traits (`model_provider.rs`, `sandbox.rs`, `telemetry.rs`).
  - `Cargo.toml` dependencies (`tokio`, `serde`, `reqwest`, `sha2`, `chrono`, `uuid`).
  - `config/lex_config.schema.json` and base configuration.
* **Story Points:** 5 SP
* **Exit Gate:** `cargo check` and 100% unit tests pass with zero compiler warnings.

---

### Sprint 1: Thin Vertical Slice (The Minimum Real Circuit in Pure Rust)
* **Goal:** Execute the first complete linear synthesis chain from compiled CLI prompt to verified execution envelope.
* **Deliverables:**
  - `src/adapters/ollama_adapter.rs` (Worker 14B async HTTP call).
  - `src/adapters/sandbox/unshare_sandbox.rs` (Isolated subprocess tempdir runner).
  - `src/adapters/file_telemetry.rs` (JSONL span and receipt recorder).
  - `src/engine/orchestrator.rs` linear pipeline:
    $$\text{Request} \longrightarrow \text{TaskNode} \longrightarrow \text{Worker 14B} \longrightarrow \text{Sandbox} \longrightarrow \text{Evidence} \longrightarrow \text{Verdict} \longrightarrow \text{Envelope}$$
  - `tests/thin_vertical_slice.rs` hermetic integration test with `FakeLlm` and `FakeSandbox`.
* **Story Points:** 8 SP
* **Exit Gate:** `cargo test` passes 100% in CI without GPU; live binary synthesizes valid code in < 20s.

---

### Sprint 2: Measurement Harness & Baseline Telemetry
* **Goal:** Build empirical measurement tools to capture real hardware latency, token speed, and VRAM usage.
* **Deliverables:**
  - `src/entrypoints/benchmark_runner.rs` with HumanEval mini-suite (20 problems).
  - Telemetry exporter (CSV + JSONL + W3C TraceContext).
  - Active VRAM capacity profiler.
* **Story Points:** 5 SP
* **Exit Gate:** Baseline benchmark report generated with zero missing/fabricated token metrics.

---

### Sprint 3: `TaskGraph IR`, Context Compiler (RAG) & 27B Architect
* **Goal:** Implement hierarchical intent decomposition into multi-module semantic contracts.
* **Deliverables:**
  - `src/engine/architect.rs` invoking Qwen 27B with Structured Output JSON Schema.
  - `src/engine/prompt_compiler.rs` compiling `TaskNode` into model-specific prompts.
  - `src/adapters/context_provider.rs` local AST repository indexer (~500 token context window).
* **Story Points:** 13 SP
* **Exit Gate:** 27B generates valid multi-module `TaskGraph IR` for 10 distinct complex prompts.

---

### Sprint 4: Multi-Module Topological DAG Worker Pool
* **Goal:** Execute multi-file synthesis in dependency order with concurrent worker execution.
* **Deliverables:**
  - `src/engine/worker_pool.rs` topological sort and Tokio async dispatch.
  - Concurrent Coder + Tester execution (`OLLAMA_NUM_PARALLEL=2`).
  - Active VRAM drain polling protocol (`GET /api/ps` -> `size_vram == 0`).
* **Story Points:** 8 SP
* **Exit Gate:** 3-file microservice synthesized in topological order with zero VRAM crashes on 24GB GPU.

---

### Sprint 5: Independent Verification & Multi-Operator Mutation Engine
* **Goal:** Eliminate test-code collusion through AST assertion density audits and active mutation probes.
* **Deliverables:**
  - `src/adapters/evidence/ast_evaluator.rs` (Assertion density counter).
  - `src/adapters/evidence/mutation_evaluator.rs` (5 mutation operators).
  - VerificationPolicy mutation threshold enforcement.
* **Story Points:** 8 SP
* **Exit Gate:** 100% of tautological tests (`assert True`) caught and rejected by mutation probe.

---

### Sprint 6: Diagnosis-Driven Self-Healing & Anti-Thrashing FSM
* **Goal:** Implement semantic failure diagnosis and state-hash oscillation circuit breakers.
* **Deliverables:**
  - `src/engine/failure_diagnostician.rs` (`FailureKind` classification).
  - `src/engine/anti_thrashing.rs` ($\text{RepairStateHash}_n == \text{RepairStateHash}_{n-2}$).
  - `src/engine/self_healing.rs` surgical patch generation with cumulative error memory.
* **Story Points:** 13 SP
* **Exit Gate:** Intentionally broken code auto-corrected in $\le 2$ cycles; duplicate tracebacks trip circuit breaker.

---

### Sprint 7: 3-Tier Rootless Sandbox Hardening
* **Goal:** Production-grade security sandboxing with zero `preexec_fn` deadlocks.
* **Deliverables:**
  - `src/adapters/sandbox/bwrap_sandbox.rs` (Bubblewrap Tier A).
  - `src/adapters/sandbox/unshare_sandbox.rs` (User Namespaces Tier B).
  - `src/adapters/sandbox/static_sandbox.rs` (Fail-closed Tier C fallback).
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
* **Goal:** Expose LEX as an MCP tool server and deliver a high-performance terminal interface.
* **Deliverables:**
  - `src/entrypoints/mcp_server.rs` (JSON-RPC 2.0 stdio tool server with `WorkspaceGrant` bounds).
  - `src/engine/ui_renderer.rs` (Terminal dashboard with live tokens/s and VRAM telemetry).
  - Packaging & distribution setup (`Cargo.toml`, standalone release binary `lex`).
* **Story Points:** 5 SP
* **Exit Gate:** External coding agents (Claude Code, Cursor, Vanguard) successfully call `lex_synthesize` over MCP stdio.

---

## 3. Total Velocity & Release Timeline

* **Total Story Points:** 81 SP (~40 Engineering Days)
* **Milestone 1 (Sprint 0–1):** Day 1–7 (Working Vertical Slice)
* **Milestone 2 (Sprint 2–4):** Day 8–20 (Swarm & DAG Core)
* **Milestone 3 (Sprint 5–7):** Day 21–32 (Verification & Self-Healing Moat)
* **Milestone 4 (Sprint 8–9):** Day 33–40 (Enterprise Productization & MCP Server)
