# AETHER / Vanguard Substrates Upgrade — Version 6 (Concept Lock v0.6.0)

A verifiable, capability-attenuated recursive-agency substrate.

```text
observe → propose → authorize → effect → receipt → evaluate
```

| Dimension | Details |
|---|---|
| **Concept Lock** | v0.6.0 — Normative Law: [`docs/SPEC.md`](docs/SPEC.md) + ADRs [`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0074`](docs/05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md) |
| **Shipped package** | `vanguard-runtime` `0.4.5b1` (`pyproject.toml`); Python `>=3.10` (tested on Python 3.12 in CI) |
| **Status** | **Concept Lock APPROVED** by the Engineering Director (`ADR-0075`). Wave 0 authorized; production coding not yet started. |
| **Foundation Plan** | Wave 0 (CI truth + named falsifiers) through Wave 4 (first real coding-agent E2E) |
| **Production Truth** | `vanguard/packages/` (Hexagonal lattice: `domain` → `ports` → `kernel` → `agency` → `runtime` → `adapters`) |

[![Concept Lock](https://img.shields.io/badge/AETHER-v0.6.0--concept--lock-blue.svg)](docs/SPEC.md)
[![Lattice](https://img.shields.io/badge/Production-vanguard%2Fpackages-green.svg)](docs/SPEC.md)
[![Approved](https://img.shields.io/badge/Director_review-APPROVED_Wave_0-brightgreen.svg)](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_D## 1. Executive Summary & Documentation Architecture

Vanguard / AETHER provides a verifiable, capability-attenuated recursive-agency substrate:
1. **The Separability Thesis**: The solution and its execution traces must be strictly separable from the agent itself.
2. **Evaluator Isolation**: The judge that evaluates and grades an agent's run is physically and cryptographically unreachable from the agent it grades (Worker UID `10001` vs Evaluator UID `10002`).
3. **Pluggable Agency**: Harnesses are compiled from declarative manifests and plugins into an immutable `FrozenHarness`. Coding is **Domain Pack #1** (`packs/code-default/`), not the hardcoded ontology of the substrate.

### The Canonical Documentation Triad

All documentation in this repository is strictly organized into three distinct authority layers:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                             1. THE LAW (WHAT)                            │
│  docs/SPEC.md (+ docs/04_annex/) — Pure RFC-2119 Normative Specification │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ governs
┌────────────────────────────────────▼─────────────────────────────────────┐
│                          2. THE DECISIONS (WHY)                          │
│  docs/05_adr/ — Immutable, append-only Architecture Decision Records     │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ directs
┌────────────────────────────────────▼─────────────────────────────────────┐
│                        3. THE EXECUTION (HOW & NOW)                      │
│  docs/03_sprints/sprint_active.md — Single living board & milestone ladder│
└──────────────────────────────────────────────────────────────────────────┘
```

### Clean Triad Reading Order
1. **This Document (`README.md`)** — Subsystem inventory, as-built architecture, and verified commands.
2. **The Normative Law**:
   - [`docs/SPEC.md`](docs/SPEC.md) — The sole normative specification (RFC-2119).
   - [`docs/04_annex/KERNEL.md`](docs/04_annex/KERNEL.md) — Dispatch, capability grants, and security model.
   - [`docs/04_annex/MEASUREMENT.md`](docs/04_annex/MEASUREMENT.md) — Measurement doctrine.
3. **The Decision Records**:
   - [`docs/05_adr/INDEX.md`](docs/05_adr/INDEX.md) — Architecture Decision Records (especially Lock ADRs [`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0076`](docs/05_adr/0076-foundation-execution-decisions-canonical-artifacts.md)).
4. **The Active Execution Board**:
   - [`docs/03_sprints/sprint_active.md`](docs/03_sprints/sprint_active.md) — Single living execution board, active wave lanes, and task register.
   - [`docs/02_roadmap/milestones.md`](docs/02_roadmap/milestones.md) — Authoritative Macro Milestones (M-0 through M-10).

---

## 2. What Exists in This Repository (As-Built Inventory)

The codebase strictly separates canonical production truth from temporary copy-forks, domain packs, tooling, and test infrastructure:

```text
Aether-D-System/
├── vanguard/
│   ├── packages/                     # CANONICAL PRODUCTION LATTICE (Python)
│   │   ├── domain/                   # Pure value objects, wire contracts, JCS, single selector algebra
│   │   ├── ports/                    # Port interfaces (kernel, model, sandbox, evaluator, stores, spi)
│   │   ├── kernel/                   # Pure security & attenuation core (TCB <= 1438 LOC: S0–S12 dispatch)
│   │   ├── agency/                   # Recursive turn machine (EpisodeEngine, context, compaction)
│   │   ├── runtime/                  # Compose, session, wiring, LedgerEmitter, evaluator gateway
│   │   ├── adapters/                 # Adapters: models (OpenRouter/Ollama), evaluator, bwrap, SQLite
│   │   └── apps/                     # Reserved client lattice slot
│   └── clients/cli/                  # TypeScript/React/Ink interactive terminal UI (`vg`)
├── layer0/                           # Copy-fork under active convergence (SPI, JSON-RPC, registry)
├── packs/code-default/               # Domain Pack #1 (MHF harness, ast-patch, repo-map, terminal)
├── test/                             # Automated test suite (1100+ tests across 17 categories)
├── tools/                            # Boundary checkers, TCB budget, secrets scanner, codegen
├── schemas/                          # v4 wire schemas and MHF plugin/harness/event schemas
└── containers/                       # Bubblewrap & OCI isolation images (UID 10001 worker, 10002 judge)
```

### Detailed Subsystem Inventory

| Subsystem | Path | Description & As-Built Capabilities |
|---|---|---|
| **Domain** | `vanguard/packages/domain/` | Pure stdlib Python. Implements primitives, wire contracts (`wire/contracts.py`, `jsonrpc.py`, `types_gen.py`), ledger reducers and events (`ledger/`), evidence models (`evidence/claim.py`), canonical selector algebra (`selectors/resource_selector.py`), RFC 8785 canonicalization (`canonicalisation/jcs.py`), and manifest definitions. |
| **Ports** | `vanguard/packages/ports/` | Hexagonal abstract interfaces: `KernelPort`, `ModelPort`, `SandboxPort`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `EnvironmentPort`, `DeterminismPort`, `IndexPort`, and the 5 SPI protocols (`spi.py`). |
| **Kernel (TCB)** | `vanguard/packages/kernel/` | Pure security core (`<=1438` LOC limit; currently 1365 LOC). Implements 13-stage effect dispatch (`dispatch.py` S0–S12), monotonic capability attenuation (`attenuation.py`), typed budget algebra (`budget.py`), descriptor-bound capability grants (`grants.py`), action classification (`classifier.py`), fail-closed policy (`policy.py`), and cryptographic provenance DAG (`provenance.py`). Domain-blind (Invariant I-7). |
| **Agency** | `vanguard/packages/agency/` | Recursive turn engine. Implements `EpisodeEngine` (`episode/engine.py`) with budget enforcement and attenuated child subagent `spawn()`; context compiler & structured token compactor (`context/`). |
| **Runtime** | `vanguard/packages/runtime/` | System composition and lifecycle. Modularly structured in place into `compose.py`, `session.py`, `wiring.py`, single-writer `ledger_emitter.py`, `evaluator_gateway.py`, governance approvals (`governance/`), and SQLite WAL event store adapters. |
| **Adapters** | `vanguard/packages/adapters/` | Concrete implementations: Model adapters (`models/openrouter.py`, `ollama.py`, `cassette.py`, `fake.py`), Exterior Evaluator daemon & RPC client (`evaluators/daemon.py`, `gate.py`, `signing.py`), Rootless Bubblewrap Sandbox (`sandbox/rootless.py`), and SQLite WAL event store (`stores/event_store.py`). |
| **Apps** | `vanguard/packages/apps/` | Reserved boundary slot in hexagonal lattice. |
| **Layer-0 Fork** | `layer0/` | Temporary copy-fork being absorbed into `vanguard/packages/`. Duplicate kernel, scheduler, and fold modules removed; registry and compose compiler scheduled for complete absorption. |
| **Code Pack #1** | `packs/code-default/` | First Modular Harness Framework (MHF) domain pack. Contains `harness.yaml`, plugin manifests (`fs`, `ast-patch`, `repo-map`, `terminal`, `evaluation-gate`, `single-planner`), prompt templates, and schema definitions. |
| **CLI / TUI** | `vanguard/clients/cli/` | Interactive terminal UI (`vg`) written in TypeScript using React and Ink. Workspace scripts: `npm run vg`. |
| **Test Suite** | `test/` | Comprehensive test suite covering all layers (`test/kernel`, `test/contracts`, `test/agency`, `test/runtime`, `test/adapters`, `test/security`, `test/trust`, `test/packs`, `test/falsifiers`, `test/registry`). Details in [`test/README.md`](test/README.md). |
| **Tooling** | `tools/` | Static architectural linters: `check_boundaries.py` (hexagonal lattice), `check_tcb_budget.py` (TCB LOC), `scan_secrets.py`, `check_domain_blindness.py` (I-7), `check_isolation_policy.py` (I-6), `check_event_coverage.py` (E-COV), `check_duplication.py --enforce`, `check_stale_paths.py`, `check_markdown_links.py`, and type codegen (`tools/codegen/generate_types.py`). |
| **Containers** | `containers/` | Container isolation images establishing process identity: Worker UID `10001` (`worker.Dockerfile`) vs Evaluator UID `10002` (`evaluator.Dockerfile`). |

---

## 3. Architecture & Hexagonal Boundary Lattice

The architecture strictly enforces a hexagonal boundary lattice verified on every commit by `tools/check_boundaries.py`:

```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a client of runtime, not a second ontology)
```

### Invariant Rules
1. **`domain/`** imports nothing from the repository (pure Python stdlib).
2. **`ports/`** imports only from `domain/`.
3. **`kernel/`** (Trusted Computing Base) imports only from `domain/` and `ports/`. It is strictly domain-blind (no coding/tool semantics).
4. **`agency/`** imports from `domain/`, `ports/`, and `kernel/`.
5. **`runtime/`** wires the components together and imports from `domain/`, `ports/`, `kernel/`, and `agency/`.
6. **`adapters/`** implement the interfaces in `ports/`. Adapters **must never** import directly from `kernel/` or `agency/`.
7. **`apps/`** consumes services from `runtime/`.

---

## 4. Trust, Attenuation, & Security Model

```text
               ┌────────────────────────────────────────────────────────┐
               │                     EpisodeEngine                      │
               │  observe → propose → authorize → effect → evaluate     │
               └──────────────────────────┬─────────────────────────────┘
                                          │
                         13-Stage Kernel Dispatch (S0–S12)
        ┌─────────────────────────────────┴─────────────────────────────────┐
        ▼                                                                   ▼
┌───────────────────────────────┐                       ┌───────────────────────────────┐
│     Worker Sandbox (Bwrap)    │                       │    Exterior Evaluator Judge   │
│         UID: 10001            │                       │         UID: 10002            │
│  - Filesystem namespace isol. │                       │  - Independent process/host   │
│  - Ephemeral tmpfs workspace  │                       │  - Signed Ed25519 verdicts    │
│  - Monotonic capability grant │                       │  - Single LedgerEmitter write │
└───────────────────────────────┘                       └───────────────────────────────┘
```

1. **Monotonic Attenuation**: Child agents spawned via `spawn()` can only receive a subset of the parent's capability grants. Privileges strictly narrow down the execution tree.
2. **Pre/Post Receipts**: Every side effect generates a pre-effect receipt and post-effect receipt recorded in the append-only SQLite WAL ledger.
3. **Physical & Network Isolation**: Worker execution happens in a rootless bubblewrap container (UID `10001`). The evaluator runs in an isolated environment (UID `10002`) and communicates only through signed verdicts.
4. **Fail-Closed Governance**: Dangerous actions require cryptographic Ed25519 human approval.

---

## 5. Macro Roadmap & Execution Status

Execution status and macro milestones are tracked in:
- **Macro Roadmap (M-0 → M-10)**: [`docs/02_roadmap/milestones.md`](docs/02_roadmap/milestones.md)
- **Active Execution Board**: [`docs/03_sprints/sprint_active.md`](docs/03_sprints/sprint_active.md)

```text
M-0 (Complete) ──▶ M-1 (Complete) ──▶ M-2 (In Flight) ──▶ M-3 (Queued) ──▶ M-4 (Foundation Stop) ──▶ M-5..M-10 (Post-Foundation)
[CI Truth/Falsif]   [Trust Spine]      [One Runtime]     [Extensibility]    [One Real Coding E2E]    [Generality & Self-Tuning]
```

---

## 6. Developer & Reviewer Commands

### Python Environment (Python 3.10+)
```bash
# Install editable package with dev dependencies
python3 -m pip install -e '.[dev]'

# Run focused production kernel tests
python3 -m unittest discover -s test/kernel -t .

# Run contract tests
python3 -m unittest discover -s test/contracts -t .

# Run agency turn engine tests
python3 -m unittest discover -s test/agency -t .

# Run domain pack tests
python3 -m unittest discover -s test/packs -t .

# Run static architectural linters
python3 tools/check_boundaries.py       # Hexagonal lattice enforcement
python3 tools/check_tcb_budget.py       # TCB kernel LOC budget check
python3 tools/scan_secrets.py           # Secret & credential leak scanner
python3 tools/check_domain_blindness.py # Kernel domain blindness (I-7)
python3 tools/check_isolation_policy.py # Sandbox isolation policy (I-6)
python3 tools/check_markdown_links.py   # Documentation link integrity
python3 tools/check_stale_paths.py      # Stale path reference checker
```

### TypeScript CLI Environment (Node.js 20+)
```bash
# Install dependencies
npm ci

# Typecheck and run CLI test suite
npm run typecheck
npm test

# Run interactive CLI
npm run vg
```

---

## 7. Model Access & Adapter Architecture

Model providers are strictly abstracted behind `ModelPort` (`vanguard/packages/ports/model.py`):
- **Adapters on disk**: OpenRouter (`adapters/models/openrouter.py`), Ollama (`adapters/models/ollama.py`), Cassette replay (`adapters/models/cassette.py`), Fake (`adapters/models/fake.py`).
- **Provider Routing**: DeepSeek, OpenAI, Anthropic, and open-weights models are addressed via route configurations and environment keys (`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`), not separate vendor files.
- **Deterministic Testing**: Keep API keys unset during local test runs to ensure hermetic, deterministic execution against cassettes and fakes.

---

## 8. Contributor & Agent References

- **Contributor & Agent Procedure**: [`AGENTS.md`](AGENTS.md)
- **Claude Guidance**: [`CLAUDE.md`](CLAUDE.md)
- **Testing Architecture & Guide**: [`test/README.md`](test/README.md)

