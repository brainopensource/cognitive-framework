# CLAUDE.md

This file provides high-density guidance to Claude Code (claude.ai/code) when operating in this repository.

---

## 1. Project Overview & Core Mission

**Vanguard / AETHER** is a verifiable, capability-attenuated recursive-agency substrate built around the loop:
```text
observe → propose → authorize → effect → receipt → evaluate
```

- **Concept Lock Law**: v0.6.0 (`docs/SPEC.md`, ADRs `0069`–`0075`, `docs/04_annex/KERNEL.md`). Director-approved per `ADR-0075`.
- **Shipped Package**: `vanguard-runtime` `0.4.5b1` (`pyproject.toml`); Python `>=3.10` (CI runs Python 3.12).
- **Core Security Thesis**: What solved a task must be separable from the agent, and the judge that evaluates the agent must be physically and cryptographically unreachable from the agent it evaluates (Worker UID `10001` in rootless bubblewrap sandbox vs Evaluator UID `10002`).
- **Human / Director Navigation**: Refer to [`README.md`](README.md) for full context and reading order.

---

## 2. Pre-Development Hold Status

> [!IMPORTANT]
> The Engineering Director review returned **APPROVED** (`docs/05_adr/0075`, [`003_V060_DIRECTOR_REVIEW.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_DIRECTOR_REVIEW.md)). **Wave 0 is the only authorized next code change** — CI subject-of-record rewire plus the named falsifiers F-01…F-21 in `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.
>
> Do **not** initiate runtime convergence, plugin implementation, `layer0/` deletion, concurrency, or any Wave 1+ work before the Wave 0 exit gate is green. No Wave 0 code has been written yet.

### As-Built Reality vs Target Lock (Do Not Conflate)

| Target Lock (SPEC + ADRs + `002`) | As-Built State on Disk Today |
|---|---|
| `vanguard/packages/` = Sole CI subject of record | **Done (M-0/M-1).** Living CI gates `vanguard/packages/` suites + falsifiers; `test/layer0` is advisory only |
| Fail-closed ceilings; signed evaluator verdicts only | **Done (M-1/2.1-D).** `adapters/sandbox/ceiling.py` is fail-closed; `layer0/kernel/`, `layer0/scheduler/` (incl. the F1 unsigned `"pass"`) deleted at 2.2-B |
| Complete `D_H` harness compile; `mhf.trajectory/1` | **Done (M-1).** `FrozenHarness`/`D_H` in `domain/artifacts/manifest.py`; `mhf.trajectory/1` emitted at `EpisodeCompleted` |
| Wire-first plugins on canonical packages path | JSON-RPC 2.0 lives in `domain/wire/jsonrpc.py` (2.1-A); `layer0/spi/` deleted at 2.2-B. Plugin lifecycle (`layer0/registry/`, `layer0/compose/`) still Wave-3 material |
| One verified coding-agent E2E (Wave 4) | `packs/code-default` + `agency/manifests/vg-*` + `vg` CLI — not that E2E yet |

---

## 3. As-Built Codebase Inventory

```text
Aether-D-System/
├── vanguard/packages/                # PRODUCTION LATTICE
│   ├── domain/                       # Pure stdlib Python: contracts, events, reducers, primitives, JCS
│   ├── ports/                        # Hexagonal ports: kernel, model, sandbox, evaluator, stores, env
│   ├── kernel/                       # Pure TCB core: S0–S12 dispatch, attenuation, budget, grants, policy
│   ├── agency/                       # Turn loop: EpisodeEngine, subagent spawn(), context compaction
│   ├── runtime/                      # Composition root (root.py), governance (Ed25519), SQLite WAL ledger
│   ├── adapters/                     # Adapters: models (OpenRouter, Ollama), evaluator daemon, bwrap
│   └── apps/                         # Reserved client lattice slot
├── layer0/                           # Copy-fork to absorb (SPI, jsonrpc, broker, scheduler driver)
├── packs/code-default/               # First domain pack (MHF harness, ast-patch, repo-map, terminal)
├── vanguard/clients/cli/             # TypeScript/React/Ink interactive terminal UI (`vg`)
├── test/                             # 900+ test suite across 17 directories (see test/README.md)
├── tools/                            # Boundaries, TCB budget, secrets scan, domain blindness, codegen
├── schemas/                          # v4 wire schemas and MHF plugin/harness schemas
├── containers/                       # Worker UID 10001 and Evaluator UID 10002 container definitions
├── benchmarks/                       # Unified benchmarks (SWE, greenfield, datalog)
└── docs/                             # Normative specs, ADRs, annexes, gap register, and evidence
```

---

## 4. Architectural Rules & Hexagonal Boundaries

Enforced on every change by `tools/check_boundaries.py`:

```text
domain ← ports ← kernel ← agency ← runtime → adapters
```

- **`domain/`**: Pure stdlib Python value objects. Imports nothing else in the repository.
- **`ports/`**: Abstract interfaces. Imports only from `domain/`.
- **`kernel/`**: Pure Trusted Computing Base (LOC `<= 1438`). Imports only from `domain/` and `ports/`. Must remain domain-blind (no coding/tooling tokens).
- **`agency/`**: Recursive turn engine. Imports from `domain/`, `ports/`, and `kernel/`.
- **`runtime/`**: Composition root and system services. Imports from `domain/`, `ports/`, `kernel/`, and `agency/`.
- **`adapters/`**: Concrete external integrations. Imports from `domain/` and `ports/`. **Must never import `kernel/` or `agency/`**.
- **`apps/`**: Client boundary slot consuming `runtime/`.

---

## 5. Development & Testing Commands

### Python Environment (Repo Root)
```bash
# Full test suite (expect some environment-sensitive failures in offline mode)
python3 -m unittest discover -s test -t .

# Production kernel suite (TCB core — 95 tests)
python3 -m unittest discover -s test/kernel -t .

# Hexagonal contract suite (121 tests)
python3 -m unittest discover -s test/contracts -t .

# Agency turn execution suite (107 tests)
python3 -m unittest discover -s test/agency -t .

# Domain pack suite (27 tests)
python3 -m unittest discover -s test/packs -t .

# Layer-0 copy-fork suite (25 tests)
python3 -m unittest discover -s test/layer0 -t .

# Single test module or method
python3 -m unittest test.kernel.test_dispatch -v
python3 -m unittest test.kernel.test_dispatch.TestDispatchPipeline.test_s0_observe_produces_receipt -v
```

### Static Architecture & Security Linters
```bash
python3 tools/check_boundaries.py         # Hexagonal boundary enforcement
python3 tools/check_tcb_budget.py         # Kernel TCB LOC limit check
python3 tools/scan_secrets.py             # Secret leak detection
python3 tools/check_domain_blindness.py   # Invariant I-7 (no domain tokens in kernel)
python3 tools/check_isolation_policy.py   # Invariant I-6 (container/subprocess execution)
python3 tools/check_markdown_links.py     # Markdown link validation
python3 tools/check_stale_paths.py        # Stale documentation path check
```

### TypeScript CLI (`vanguard/clients/cli`)
```bash
npm run typecheck    # TypeScript compiler check (tsc --noEmit)
npm test             # Node built-in test runner on dist/test/*.test.js
npm run vg           # Launch interactive TUI
```

### Cleanup
```bash
make clean           # Removes py/js caches, test artifacts, build outputs
```

---

## 6. Known Environmental & Test Behaviors

1. **Local Ollama Daemon**: If Ollama is not running locally on port 11434, 3 tests in `test/runtime` (`test_s20_live_turn_freeze.py`, `test_s21_named_causes.py`, `test_w16_task_sets_and_live_smoke.py`) will report `provider_unreachable` instead of `model_tag_absent`. This is expected in offline dev environments.
2. **API Keys**: Keep `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, and `OPENAI_API_KEY` unset during automated testing to enforce offline determinism against fakes and cassettes.
3. **Negative Lint Fixtures**: `test/broken/fixtures/` contains intentional architectural violations used by tools in `tools/` to test that linters fail-closed.

---

## 7. Documentation Hierarchy & Authority

When resolving architectural questions or ambiguous requirements, follow this strict precedence:
1. **[`docs/SPEC.md`](docs/SPEC.md)** — Sole living normative specification (RFC-2119).
2. **Lock ADRs ([`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0074`](docs/05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md))** — Append-only architectural decisions.
3. **Annexes ([`04_annex/KERNEL.md`](docs/04_annex/KERNEL.md), [`04_annex/MEASUREMENT.md`](docs/04_annex/MEASUREMENT.md))** — Security and measurement constitutions.
4. **Execution Roadmap ([`002 Gap Register`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md))** — Sequence of foundation waves.
5. **Lock Plan ([`GAMMA`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md)) and Director Review ([`003`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_DIRECTOR_REVIEW.md))** — Planning and review documents (BETA/DELTA phases consolidated to git history per `ADR-0075`).
6. **Forensic Evidence ([`docs/07_reviews/`](docs/07_reviews/), [`docs/03_sprints/`](docs/03_sprints/))** — Advisory evidence and history; cannot be cited as binding requirements.
