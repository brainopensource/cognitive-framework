# Granular Sprint Backlog & Task Register — LEX Engine

> **Subsystem Path:** `tools/004_LLM_EXECUTION_X/`  
> **Status:** Active Execution Board (Pure Rust Engine Track)  
> **Current Sprint:** Sprint 0 / Sprint 1 (Foundation & Thin Vertical Slice)  

---

## 1. Epics Hierarchy

| Epic ID | Epic Title | Description & Moat |
|:---|:---|:---|
| **EPIC-1** | Foundation & Domain Contracts | Pure Rust value objects, `TaskGraph IR`, `EvidenceSet`, and `AgentExecutionEnvelope`. |
| **EPIC-2** | 3-Tier Sandbox & Execution | Bubblewrap Tier A, User Namespace Tier B, and Fail-Closed Tier C runners. |
| **EPIC-3** | Swarm Orchestrator & Hardware Physics | Ollama adapter with structured JSON schema, VRAM drain polling, and concurrent Tokio workers. |
| **EPIC-4** | Evidence Engine & Mutation Testing | AST assertion density counter, 5 mutation operators, and VerificationPolicy decision engine. |
| **EPIC-5** | Failure Diagnosis & Self-Healing | Semantic failure taxonomy (`FailureKind`), state-hash anti-thrashing circuit breaker, and patch loop. |
| **EPIC-6** | Interoperability & Product Interfaces | Protected MCP JSON-RPC stdio tool server, compiled CLI binary, and telemetry exporters. |

---

## 2. Sprint 0: Architecture Lock & Boundary Enforcement (Tasks)

| Task ID | Task Title | File Target(s) | Acceptance Criteria (DoD) | SP |
|:---|:---|:---|:---|:---:|
| **LEX-001** | Create Rust Domain Value Objects | `src/domain/task_graph.rs`, `src/domain/evidence.rs`, `src/domain/verdict.rs`, `src/domain/receipt.rs`, `src/domain/errors.rs`, `src/domain/values.rs` | Pure Rust structs with Serde derive; immutable value semantics; zero unsafe code. | 2 |
| **LEX-002** | Define Async Ports Traits | `src/ports/model_provider.rs`, `src/ports/sandbox.rs`, `src/ports/telemetry.rs` | `#[async_trait]` traits defined for all ports with complete error handling. | 1 |
| **LEX-003** | Cargo Crate Configuration | `Cargo.toml`, `src/lib.rs` | Clean crate compilation with zero warnings; strict dependency tree. | 1 |
| **LEX-004** | Configuration Schema & Base YAML | `config/lex_config.yaml`, `config/lex_config.schema.json` | JSON schema validates config YAML; env var overrides (`LEX_*`) supported. | 1 |

---

## 3. Sprint 1: Thin Vertical Slice in Pure Rust (Tasks — READY FOR EXECUTION)

| Task ID | Task Title | File Target(s) | Acceptance Criteria (DoD) | SP |
|:---|:---|:---|:---|:---:|
| **LEX-101** | Implement Ollama Worker Adapter | `src/adapters/ollama_adapter.rs` | Async HTTP client (reqwest/tokio) calls `qwen2.5-coder:14b` with token/s calculation. | 2 |
| **LEX-102** | Implement Subprocess Tempdir Sandbox | `src/adapters/sandbox/unshare_sandbox.rs` | Runs `pytest` inside ephemeral UUID temp directory with 10s timeout and env scrubbing. | 2 |
| **LEX-103** | Implement File Telemetry Logger | `src/adapters/file_telemetry.rs` | Writes span records to `output/telemetry.jsonl` with W3C `trace_id`. | 1 |
| **LEX-104** | Implement Linear Orchestrator Engine | `src/engine/orchestrator.rs` | Coordinates: Request $\to$ TaskNode $\to$ Worker 14B $\to$ Sandbox $\to$ EvidenceSet $\to$ VerificationPolicy $\to$ AgentExecutionEnvelope. | 2 |
| **LEX-105** | Build Hermetic Fakes & E2E Unit Test | `tests/fakes/fake_llm.rs`, `tests/fakes/fake_sandbox.rs`, `tests/thin_vertical_slice.rs` | 100% hermetic Rust unit test passes in CI in < 1 second with zero network and zero GPU via `cargo test`. | 1 |

---

## 4. Definition of Done (DoD) for All Tasks

1. **Compiler & Linter:** `cargo check` and `cargo clippy` report **0 warnings/errors**.
2. **Hermetic Test Suite:** `cargo test` passes **100% green** in CI without GPU or network access.
3. **Hexagonal Boundaries:** `src/engine/` never references `src/adapters/`; `src/domain/` has zero external dependencies.
4. **No Hidden State:** All artifacts written exclusively to designated workspace temp directories or `output/`.
5. **No Cheating:** Telemetry logs report true measured tokens without fabricated zeros.
