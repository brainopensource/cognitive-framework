# Vanguard / AETHER — Testing Subsystem Guide

This directory contains the automated test suite for the Vanguard / AETHER runtime (**1,119 collected test cases** across the Python test tree — plus two directories discovery cannot collect, see §4 — and the TypeScript CLI test suite).

---

## 1. Quick Start

### Prerequisites
- Python 3.10+ (tested on Python 3.12 in CI).
- Node.js 20+ (for CLI TypeScript tests).

### Setup
```bash
# Python dev dependencies (repo root)
python3 -m pip install -e '.[dev]'

# TypeScript dev dependencies (repo root)
npm ci
```

### Common Test Commands
```bash
# Run production kernel tests (TCB core)
python3 -m unittest discover -s test/kernel -t .

# Run hexagonal port contract tests
python3 -m unittest discover -s test/contracts -t .

# Run agency & episode turn tests
python3 -m unittest discover -s test/agency -t .

# Run runtime service & composition tests
python3 -m unittest discover -s test/runtime -t .

# Run security & isolation tests
python3 -m unittest discover -s test/security -t .
python3 -m unittest discover -s test/trust -t .

# Run domain pack tests (code-default)
python3 -m unittest discover -s test/packs -t .

# Run layer0 copy-fork tests
python3 -m unittest discover -s test/layer0 -t .

# Run a single focused test module
python3 -m unittest test.kernel.test_dispatch -v

# Run an exact single test case
python3 -m unittest test.kernel.test_dispatch.HappyPath.test_a_within_authority_write_completes -v

# Run TypeScript CLI tests (Node built-in test runner)
npm test
```

---

## 2. Test Suite Taxonomy & Architecture

The test suite is organized by architectural layer and subsystem:

```text
test/
├── kernel/            # Pure TCB: S0–S12 effect dispatch, attenuation, budget, grants, classifier, provenance
├── contracts/         # Hexagonal port contracts, JCS canonicalization, Dev1 primitives, ledger schemas
├── agency/            # EpisodeEngine, turn execution, context compilation, structured compaction, spawn()
├── runtime/           # VanguardCompositionRoot, approval flows, WAL ledger, replay/resume, provider health
├── adapters/          # Model adapters (OpenRouter, Ollama, fake, cassette), evaluator daemon, sandbox bwrap
├── security/          # Evaluator security bounds, rootless sandbox UID isolation (10001 vs 10002)
├── trust/             # Trust spine end-to-end receipt chains and cryptographic signature verification
├── governance/        # Ed25519 signature validation and human-in-the-loop approval policies
├── packs/             # Domain Pack #1 (packs/code-default) plugin tests (ast-patch, repo-map, planner, terminal)
├── layer0/            # Copy-fork microkernel suite (SPI, JSON-RPC, sequential driver, registry)
├── registry/          # Plugin registry lifecycle, RPC gate attenuation, validator tests
├── benchmarks/        # Latency benchmarks, telemetry provenance, instrument tuple verification
├── lab/               # Lab measurement harness, AA runners, statistical splits (promotion deferred)
├── tools/             # Tooling tests (check_core_changes, LAM/LAR analyzers, mock LLM router)
├── apps/              # Apps lattice slot tests
├── fixtures/          # Shared positive test fixtures and scripted mock backends
├── support/           # Test helpers and composition factories
└── broken/fixtures/   # Negative fixture corpus for fail-closed architectural lint verification
```

---

## 3. Subsystem Breakdown

### `test/kernel/` — Pure Security Core & TCB (95 tests)
Tests the pure mathematical security core of Vanguard (`vanguard/packages/kernel`):
- `test_dispatch.py`: Verifies the 13-stage effect dispatch pipeline (S0: ENTER → S1: PARSE → S2: RESOLVE → S3: DESCRIBE → S4: CLASSIFY → S5: AUTHORIZE → S6: GRANT → S7: RESERVE → S8: VERIFY → S8a: INTENT → S9: DISPATCH → S10: COMMIT → S11: RELEASE → S12: EMIT).
- `test_attenuation.py`: Verifies monotonic capability narrowing (child scope $\subseteq$ parent scope).
- `test_budget.py` & `test_grant_budget_events.py`: Verifies turn count, token budget, and cost ceiling enforcement.
- `test_grant_wire_shape.py`: Verifies capability grant serialization and deserialization.
- `test_provenance.py`: Verifies cryptographic lineage and execution causal DAGs.

Replay-parity (I-4, F-02) lives on the packages path in `test/runtime/test_ledger_truth.py`
(`ColdReplayParity`); the layer0 replay contract lives in `test/layer0/replay/test_parity.py`.
The former `test/kernel/test_replay_parity.py` imported the layer0 fold/driver despite its
location and is removed (Wave 1, 1.3-B hygiene) — it tested nothing packages-scoped.

### `test/contracts/` — Hexagonal Port Contracts & Wire Invariants (121 tests)
Enforces port behavior and wire schemas across both Python and TypeScript parity:
- `t1_dev1_canonicalisation.py`: Verifies RFC-8785 JSON Canonicalization Scheme (JCS) determinism.
- `t1_dev1_primitives.py` & `t1_dev1_selectors.py`: Verifies URI and resource selector parsing (`file://`, `proc://`, `net://`).
- `t1_wire_contracts.py`: Validates wire-level contracts for models, tools, and events.
- `t3_ledger.py` & `t7_artifact_graph.py`: Validates event stream append-only rules and artifact DAG constraints.
- `test_*_port.py`: Verifies abstract port contracts (`ModelPort`, `SandboxPort`, `EvaluatorPort`, `EventStorePort`, `EnvironmentPort`).

### `test/agency/` — Recursive Agency & Turn Engine (107 tests)
Tests the recursive turn execution and context machinery (`vanguard/packages/agency`):
- `test_episode.py` & `test_episode_spawn.py`: Verifies outer episode turn loop (`observe → propose → authorize → effect → receipt → evaluate`), timeout handling, and recursive subagent `spawn()`.
- `test_context_compiler.py` & `test_structured_compaction.py`: Verifies prompt building, context window token budgeting, and lossless structural compaction.
- `test_manifest_loader.py` & `test_manifest_metamorphic.py`: Verifies declarative YAML harness loading and metamorphic validation.

### `test/runtime/` — Composition & Service Orchestration (400 tests)
Tests the runtime services and persistence layer (`vanguard/packages/runtime`):
- `test_composition_root.py` & `test_composition_values.py`: Verifies dependency injection wiring and immutable configuration.
- `test_approval_flow.py` & `test_ed25519_approvals.py`: Verifies interactive human approvals and cryptographic signing.
- `test_resume_from_ledger.py` & `test_harness_session.py`: Verifies crash recovery, ledger replay, and session resumption.
- `test_provider_health.py` & `test_s21_named_causes.py`: Verifies backend provider error attribution and health probing.

### `test/adapters/` — Port Implementations (124 tests)
Tests the concrete adapters against real or mocked external dependencies (`vanguard/packages/adapters`):
- `test_openrouter.py`, `test_ollama.py`, `test_model_invocation.py`: Model provider adapters and routing policies.
- `test_evaluator_daemon.py` & `test_evaluator_signing.py`: Tests the exterior evaluator daemon and Ed25519 verdict signing over RPC.
- `test_sandbox_worker.py`: Tests rootless bubblewrap sandbox execution and stream capture.
- `test_tableworld.py`: Tests structured tabular environment adapter.

### `test/security/` & `test/trust/` — Isolation & Trust Spine (67 tests)
Verifies the fundamental security invariants of the system:
- `test_rootless_sandbox.py` & `test_sandbox_isolation.py`: Verifies filesystem namespace isolation, network sandboxing, and unprivileged user execution.
- `test_evaluator_security.py`: Verifies that worker processes (UID 10001) cannot communicate with or influence the evaluator judge (UID 10002).
- `test_spine.py`: Verifies end-to-end receipt chain integrity from initial prompt to signed verdict.

### `test/packs/` — Domain Packs (27 tests)
Tests domain-specific packs (`packs/code-default/`):
- `test_ast_patch.py`: Verifies AST-level code modification plugins.
- `test_repo_map.py`: Verifies repository symbol indexing and map generation.
- `test_single_planner.py`: Verifies single-step and hierarchical plan formulation.
- `test_terminal_runner.py`: Verifies safe terminal command execution within the sandbox.
- `test_walking_skeleton.py`: Verifies the end-to-end flow of compiling `harness.yaml` into a runnable coding agent.

### `test/layer0/` — Copy-Fork Microkernel (25 tests)
Tests the copy-fork components (`layer0/`) destined for absorption into `vanguard/packages/` during Wave 2:
- `test_interfaces.py`: Verifies SPI contracts.
- `test_driver.py`: Verifies sequential scheduling. **Note**: Defect F1 currently *passes* in CI because the driver itself fabricates `"pass"` verdicts; fixing F1 in Wave 1 requires wiring real signed exterior evaluator checks.
- `test_canonical.py` & `test_fold.py`: Verifies event store and memory ledger operations.

### `test/broken/fixtures/` — Negative Architectural Fixtures
Contains deliberate architectural violations (cycles, illegal imports, domain leakages, secret patterns, TCB budget breaches). These fixtures are executed by tools in `tools/` (e.g. `check_boundaries.py`, `check_domain_blindness.py`, `check_isolation_policy.py`, `scan_secrets.py`) to prove that our linters **fail-closed** when violations occur.

---

## 4. Full Execution Results & Master Summary Table

**Baseline of record: 2026-08-20, main `4f9f8b1` (re-verified during the Director review, `ADR-0075`).**

Root discovery (`python3 -m unittest discover -s test -t .`) collects **1,119 tests — 7 failures, 5 errors, 8 skipped**. The per-directory table below sums slightly higher because two directories are **silently excluded from discovery**: `test/integration/` (13 defined tests) and `test/governance/` are missing `__init__.py` and cannot be imported at all — they run in no configuration. This is falsifier **F-19** in the `002` gap register (Wave 0: make them importable or retire them with a recorded reason). Do not count them as green.

**CI subject of record (ADR-0073):** the production-path suites are `test/kernel`, `test/contracts`, `test/agency`, `test/runtime`, `test/adapters`, plus `test/security` and `test/trust`. A green `test/layer0` suite alone is **not** success — the layer0 driver fabricates its own `"pass"` verdict (defect F1), so its suite certifies the defect. Living CI does not yet run the production suites; wiring it is Wave 0.

### Master Results Table

| Subsystem | Test Directory | Tests Run | Passed | Failures | Errors | Skipped | Pass Rate | Status |
|---|---|---|---|---|---|---|---|---|
| **Kernel (TCB)** | `test/kernel/` | 95 | 95 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Contracts** | `test/contracts/` | 121 | 121 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Agency** | `test/agency/` | 107 | 107 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Runtime** | `test/runtime/` | 400 | 390 | 3 | 0 | 7 | **97.5%** | ⚠️ Offline Sensitivity (Ollama daemon offline) |
| **Adapters** | `test/adapters/` | 124 | 116 | 2 | 5 | 1 | **93.5%** | ⚠️ Legacy Output Lifting / Sprint Path |
| **Security** | `test/security/` | 45 | 45 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Trust Spine** | `test/trust/` | 22 | 22 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Domain Packs** | `test/packs/` | 27 | 27 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Layer-0 Fork** | `test/layer0/` | 25 | 25 | 0 | 0 | 0 | **100.0%** | ✅ PASS (Note: F1 passes silently) |
| **Registry** | `test/registry/` | 26 | 26 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Governance** | `test/governance/` | — | — | — | — | — | — | ⛔ NOT COLLECTED (no `__init__.py`, F-19) |
| **Integration** | `test/integration/` | — | — | — | — | — | — | ⛔ NOT COLLECTED (13 defined tests never run, F-19) |
| **Apps Slot** | `test/apps/` | 4 | 4 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Benchmarks** | `test/benchmarks/` | 20 | 20 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Lab Measurement**| `test/lab/` | 54 | 54 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Tooling Tests** | `test/tools/` | 38 | 38 | 0 | 0 | 0 | **100.0%** | ✅ PASS |
| **Root Tests** | `test/test_*.py` | 29 | 27 | 2 | 0 | 0 | **93.1%** | ⚠️ Historical Sprint Path Assertions |
| **TOTAL (root discovery)** | *Monorepo Suite* | **1,119** | **1,099** | **7** | **5** | **8** | **98.2%** | **Solid Core Foundation** |

*Verification*: $1099 + 7 + 5 + 8 = 1119$ collected tests. Uncollected directories (F-19) are excluded from every total by construction.

---

## 5. Detailed Analysis of Test Execution & Root Causes

### A. Subsystems at 100% Pass Rate
- **`test/kernel` (95/95)**: Pure TCB dispatch stages (S0–S12), monotonic capability attenuation, budget cost calculations, grant serialization, execution provenance DAG, and deterministic event replay all pass with zero errors.
- **`test/contracts` (121/121)**: RFC-8785 JSON Canonicalization Scheme (JCS), Dev1 primitives, selectors, wire contracts, and abstract port compliance (`ModelPort`, `SandboxPort`, `EvaluatorPort`, etc.) all pass.
- **`test/agency` (107/107)**: Recursive `EpisodeEngine` turn execution, subagent `spawn()`, context compaction, and manifest loaders pass.
- **`test/security` & `test/trust` (67/67)**: Evaluator process isolation (UID 10002 unreachable from UID 10001 worker), rootless Bubblewrap sandbox isolation, and trust spine receipt verification pass.
- **`test/packs` (27/27)**: All plugins for Domain Pack #1 (`code-default`) including AST patch, repo map, planner, and terminal runner pass.
- **`test/layer0` & `test/registry` (51/51)**: Microkernel copy-fork and plugin registry lifecycle tests pass.
- **`test/benchmarks`, `test/lab`, `test/tools` (112/112)**: Latency telemetry, measurement runners, and change verification tools pass.

### B. Understanding Non-Passing Tests & Root Causes

#### 1. `test/runtime` (3 Failures, 7 Skipped)
- **Root Cause (Failures)**: Local Ollama Daemon Offline.
  - Three tests (`test_s20_live_turn_freeze.py`, `test_s21_named_causes.py`, `test_w16_task_sets_and_live_smoke.py`) test error attribution when a specific model tag is absent in Ollama. They expect the error string `"not pulled"` or outcome `"instrument_error:model_tag_absent"`.
  - When the local Ollama daemon is not active on `127.0.0.1:11434`, the adapter receives a connection failure, resulting in `"no daemon answering at http://127.0.0.1:11434/api/chat"` and `"instrument_error:provider_unreachable"`.
- **Root Cause (Skipped)**: Offline Hermetic Design.
  - 7 live LLM integration tests intentionally skip when live API keys (`OPENROUTER_API_KEY`, etc.) are unset in the local environment, ensuring that tests never make unbudgeted network calls.

#### 2. `test/adapters` (2 Failures, 5 Errors, 1 Skipped)
- **Root Cause (3 Errors — real behavioral gaps, falsifier F-21)**: `ProposalTranslator` lifting in `test_model_invocation.py`.
  - Verified by direct reproduction against `vanguard/packages/adapters/models/invocation.py`: a tool call spelled with the `parameters` key, and two fenced-payload forms (quoted info-string values; `payloadArgument` bodies), currently degrade to prose (`{"kind": "finish"}`) instead of lifting to an action. The tests encode intended contract behavior the translator does not implement. These are **not** stale tests; the earlier "legacy output shape / structured ToolCall" explanation recorded here was wrong. Fix or re-scope in Wave 0/1 together with P1-17.
- **Root Cause (2 Errors — missing evidence artifact, falsifier F-20)**: `test_oracle_registry.py`.
  - `repo_paths.preregistered_oracles()` resolves to `docs/sprint6B/preregistered_oracles.json`, which no longer exists **anywhere in the tree** — the file was deleted with `docs/sprint6B/`, not relocated (the previously recorded `docs/03_sprints/evidence/` destination does not exist). Wave 0 must restore the registry artifact at a canonical path or retire these tests with a recorded reason.
- **Root Cause (2 Failures — open contract decision, P1-17)**: Selector Grammar in `test_model_invocation.py`.
  - The tests expect `proc://exec/allow/...` `generic`-kind selectors; the current path yields `process`-kind. Which algebra wins is the P1-17 Wave 0/1 contract decision; the reds are honest until it is made.

#### 3. `test/test_repo_paths.py` (2 Failures)
- **Root Cause**: Same stale `docs/sprint6B/` registry path as F-20 above (Wave 0 hygiene item P1-15).

---

## 6. Static Architecture Linters Status

Status of static architectural enforcement scripts in `tools/`:

```text
check_boundaries.py        ✅ PASS  (297 source files checked, 0 violations)
check_tcb_budget.py        ✅ PASS  (1347 LOC vs 1438 LOC threshold, 131 lines safety margin)
scan_secrets.py            ✅ PASS  (0 leaked secrets/tokens in scanned surfaces)
check_domain_blindness.py  ✅ PASS* (scans layer0/ ONLY — narrower than Invariant I-7, which also
                                    covers vanguard/packages/{domain,kernel}/; falsifier F-18, Wave 0)
check_isolation_policy.py  ✅ PASS  (Invariant I-6: proc.exec plugins declare container/subprocess)
check_markdown_links.py    ✅ PASS  (All local markdown links resolve)
check_stale_paths.py       ❌ FAIL  (RED on docs/sprint6B references — Wave 0 cleanup item)
```

> [!NOTE]
> `check_stale_paths.py` is currently **RED** due to 6 references to `docs/sprint6B` across review/spec files. This is tracked as a Wave 0 documentation hygiene item and is not an architectural defect.

---

## 7. TypeScript CLI Tests

The CLI test suite lives under `vanguard/clients/cli/test/` and uses Node's built-in test runner:

```bash
# Run typechecking
npm run typecheck

# Run test suite
npm test
```

Test files:
- `transport.test.ts`: JSON-RPC / IPC transport between CLI and runtime.
- `signer.test.ts`: Ed25519 key management and message signing in TypeScript.
- `commands.test.ts`: CLI command parsing and execution handlers.
- `ui.test.ts`: Ink/React terminal UI component rendering and layout.
- `soak.test.ts`: CLI session stress testing and event streaming.

---

## 8. Guidelines for Writing New Tests

1. **Hermetic & Offline by Default**: Tests must run without network access or paid API keys. Never depend on live external endpoints in standard unit or contract tests. Use cassette replays, fakes (`test/fixtures/coding_scripted_backends.py`), or `ModelPort` doubles.
2. **Deterministic Execution**: Avoid time-dependent or random assertions. Use seeded pseudorandom generators or explicit timestamps.
3. **Naming Conventions**: Name test files `test_<feature>.py` and place them in the directory corresponding to their architectural layer. Test classes should inherit from `unittest.TestCase` and test methods must start with `test_`.
4. **Boundary Compliance**: Test files in `test/<layer>` must respect the hexagonal dependency rules of the layer they test.
5. **Fail-Closed Assertions**: When testing security gates or evaluators, verify that missing, corrupted, or unsigned inputs result in an explicit refusal or error, never a default pass.
