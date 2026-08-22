# Granular Sprint Backlog & Task Register — LEX Engine

> **Subsystem Path:** `tools/004_LLM_EXECUTION_X/`  
> **Status:** Active Execution Board  
> **Current Sprint:** Sprint 0 / Sprint 1 (Foundation & Thin Vertical Slice)  

---

## 1. Epics Hierarchy

| Epic ID | Epic Title | Description & Moat |
|:---|:---|:---|
| **EPIC-1** | Foundation & Domain Contracts | Pure Python stdlib value objects, `TaskGraph IR`, `EvidenceSet`, and `AgentExecutionEnvelope`. |
| **EPIC-2** | 3-Tier Sandbox & Execution | Bubblewrap Tier A, User Namespace Tier B, and Fail-Closed Tier C runners. |
| **EPIC-3** | Swarm Orchestrator & Hardware Physics | Ollama adapter with structured JSON schema, VRAM drain polling, and concurrent workers. |
| **EPIC-4** | Evidence Engine & Mutation Testing | AST assertion density counter, 5 mutation operators, and VerificationPolicy decision engine. |
| **EPIC-5** | Failure Diagnosis & Self-Healing | Semantic failure taxonomy (`FailureKind`), state-hash anti-thrashing circuit breaker, and patch loop. |
| **EPIC-6** | Interoperability & Product Interfaces | Protected MCP JSON-RPC stdio tool server, CLI with Rich live TUI, and telemetry exporters. |

---

## 2. Sprint 0: Architecture Lock & Boundary Enforcement (Tasks)

| Task ID | Task Title | File Target(s) | Acceptance Criteria (DoD) | SP |
|:---|:---|:---|:---|:---:|
| **LEX-001** | Create Domain Value Objects | `domain/task_graph.py`, `domain/evidence.py`, `domain/verdict.py`, `domain/receipt.py` | 100% pure Python stdlib; immutable frozen dataclasses; no external imports. | 2 |
| **LEX-002** | Define Ports Protocols | `ports/model_provider.py`, `ports/sandbox.py`, `ports/telemetry.py` | `typing.Protocol` classes defined for all 5 ports with complete type hints. | 1 |
| **LEX-003** | Implement Boundary Linter | `linters/check_boundaries.py` | AST import graph walker fails closed with exit code 1 on illegal hexagonal imports. | 1 |
| **LEX-004** | Configuration Schema & Base YAML | `config/lex_config.yaml`, `config/lex_config.schema.json` | JSON schema validates config YAML; env var overrides (`LEX_*`) supported. | 1 |

---

## 3. Sprint 1: Thin Vertical Slice (Tasks — READY FOR EXECUTION)

| Task ID | Task Title | File Target(s) | Acceptance Criteria (DoD) | SP |
|:---|:---|:---|:---|:---:|
| **LEX-101** | Implement Ollama Worker Adapter | `adapters/ollama_adapter.py` | Async HTTP client generates code using `qwen2.5-coder:14b` with token/s calculation. | 2 |
| **LEX-102** | Implement Subprocess Tempdir Sandbox | `adapters/sandbox/unshare_sandbox.py` | Runs `pytest` inside ephemeral UUID temp directory with 10s timeout and env scrubbing. | 2 |
| **LEX-103** | Implement File Telemetry Logger | `adapters/file_telemetry.py` | Writes span records to `output/telemetry.jsonl` with W3C `trace_id`. | 1 |
| **LEX-104** | Implement Linear Orchestrator Engine | `engine/orchestrator.py` | Coordinates: Request $\to$ TaskNode $\to$ Worker 14B $\to$ Sandbox $\to$ EvidenceSet $\to$ VerificationPolicy $\to$ AgentExecutionEnvelope. | 2 |
| **LEX-105** | Build Hermetic Fakes & E2E Unit Test | `tests/fakes/fake_llm_provider.py`, `tests/fakes/fake_sandbox.py`, `tests/integration/test_thin_vertical_slice.py` | 100% hermetic unit test passes in CI in < 1 second with zero network and zero GPU. | 1 |

---

## 4. Definition of Done (DoD) for All Tasks

1. **Boundary Linter:** `python linters/check_boundaries.py` reports **0 violations**.
2. **Hermetic Test Suite:** `pytest tests/unit/` and `pytest tests/integration/test_thin_vertical_slice.py` pass **100% green**.
3. **Type Checking & Linting:** `ruff check .` reports **0 errors**.
4. **No Hidden State:** All artifacts written exclusively to designated workspace temp directories or `output/`.
5. **No Cheating:** Telemetry logs report true measured tokens without fabricated zeros.
