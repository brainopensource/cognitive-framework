# AETHER / Vanguard — Version 6 (Concept Lock v0.6.0)

A verifiable, capability-attenuated recursive-agency substrate.

```text
observe → propose → authorize → effect → receipt → evaluate
```

| Dimension | Details |
|---|---|
| **Concept Lock** | v0.6.0 — Normative Law: [`docs/SPEC.md`](docs/SPEC.md) + ADRs [`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0074`](docs/05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md) |
| **Shipped package** | `vanguard-runtime` `0.4.5b1` (`pyproject.toml`); Python `>=3.10` (tested on Python 3.12 in CI) |
| **Status** | **Documentation Lock Complete**. Production coding held pending Engineering Director / Chief Engineer approval. |
| **Foundation Plan** | Wave 0 (CI truth + named falsifiers) through Wave 4 (first real coding-agent E2E) |
| **Production Truth** | `vanguard/packages/` (Hexagonal lattice: `domain` → `ports` → `kernel` → `agency` → `runtime` → `adapters`) |

[![Concept Lock](https://img.shields.io/badge/AETHER-v0.6.0--concept--lock-blue.svg)](docs/SPEC.md)
[![Lattice](https://img.shields.io/badge/Production-vanguard%2Fpackages-green.svg)](docs/SPEC.md)
[![Hold](https://img.shields.io/badge/Production_coding-held-orange.svg)](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md)

---

## 1. Executive Summary for Engineering Director & Chief Engineer

This repository is under **final independent review** before Wave 0 implementation begins. You own the go/no-go decision.

### The Mission & Core Thesis
Vanguard/AETHER provides a verifiable recursive-agency substrate:
1. **Separability**: The solution and its execution traces must be strictly separable from the agent itself.
2. **Evaluator Isolation**: The judge that evaluates and grades an agent's run is physically and cryptographically unreachable from the agent it grades (Worker UID `10001` vs Evaluator UID `10002`).
3. **Pluggable Agency**: Harnesses are compiled from declarative manifests and plugins into an immutable `FrozenHarness`. Coding is **Domain Pack #1** (`packs/code-default/`), not the hardcoded ontology of the substrate.

### Decision Requested
- **`APPROVED`**: Concept Lock v0.6.0 foundation and specifications are accepted; Wave 0 implementation may proceed.
- **`BLOCKED`**: Architectural issues identified that require specification/ADR amendments prior to code execution.

### Director Review Reading Order
1. **This Document** — Complete repository inventory, as-built state, and operational roadmap.
2. **Normative Law**:
   - [`docs/SPEC.md`](docs/SPEC.md) — The sole normative specification (RFC-2119).
   - [`docs/05_adr/INDEX.md`](docs/05_adr/INDEX.md) — Architecture Decision Records (especially Lock ADRs [`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0074`](docs/05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md)).
   - [`docs/04_annex/KERNEL.md`](docs/04_annex/KERNEL.md) — Dispatch, capability grants, and security model.
   - [`docs/04_annex/MEASUREMENT.md`](docs/04_annex/MEASUREMENT.md) — Measurement doctrine (Phase-2 promotion deferred).
3. **Foundation Roadmap & Execution Register**:
   - [`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md) — The active Wave 0→4 gap register.
   - [`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md) — Concept Lock Plan.
4. **Live Codebases**:
   - `vanguard/packages/` — Canonical production lattice.
   - `layer0/` — Copy-fork to absorb (SPI, JSON-RPC, lifecycle).
   - `packs/code-default/` — First MHF-shaped domain pack.
   - `vanguard/clients/cli/` — TypeScript/Ink interactive TUI (`vg`).
   - `test/` — Comprehensive test suite ([`test/README.md`](test/README.md)).

---

## 2. What Exists in This Repository (As-Built Inventory)

The codebase is organized into well-defined subsystems, separating production truth from temporary copy-forks, domain packs, tooling, and test infrastructure:

```text
Aether-D-System/
├── vanguard/
│   ├── packages/                     # CANONICAL PRODUCTION LATTICE (Python)
│   │   ├── domain/                   # Pure value objects, wire contracts, JCS canonicalization
│   │   ├── ports/                    # Port interfaces (kernel, model, sandbox, evaluator, stores)
│   │   ├── kernel/                   # Pure security & attenuation core (TCB: S0–S12 dispatch)
│   │   ├── agency/                   # Recursive turn machine (EpisodeEngine, context, compaction)
│   │   ├── runtime/                  # Composition root, governance, WAL ledger, RPC service
│   │   ├── adapters/                 # Adapters: models (OpenRouter/Ollama), evaluator, bwrap, SQLite
│   │   └── apps/                     # Reserved client lattice slot
│   └── clients/cli/                  # TypeScript/React/Ink interactive terminal UI (`vg`)
├── layer0/                           # Copy-fork to absorb into packages (SPI, JSON-RPC, registry)
├── packs/code-default/               # Domain Pack #1 (MHF harness, ast-patch, repo-map, terminal)
├── test/                             # Automated test suite (900+ tests across 17 categories)
├── tools/                            # Boundary checkers, TCB budget, secrets scanner, codegen
├── schemas/                          # v4 wire schemas and MHF plugin/harness schemas
├── containers/                       # Bubblewrap & OCI isolation images (UID 10001 worker, 10002 judge)
├── lab/ & benchmarkings/             # Lab measurement harness & latency benchmarks (promotion deferred)
└── docs/                             # Normative specs (SPEC.md, ADRs, annexes) and forensic evidence
```

### Detailed Subsystem Inventory

| Subsystem | Path | Description & As-Built Capabilities |
|---|---|---|
| **Domain** | `vanguard/packages/domain/` | Pure stdlib Python. Implements primitives (`primitives/primitives.py`), wire contracts (`wire/contracts.py`), ledger reducers and events (`ledger/`), evidence models (`evidence/claim.py`), selectors (`selectors/resource_selector.py`), JCS canonicalization (`canonicalisation/jcs.py`), and manifest compiler (`artifacts/manifest.py`). |
| **Ports** | `vanguard/packages/ports/` | Hexagonal abstract interfaces: `KernelPort`, `ModelPort`, `SandboxPort`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `EnvironmentPort`, `DeterminismPort`, `IndexPort`. |
| **Kernel (TCB)** | `vanguard/packages/kernel/` | Pure security core (`<=1438` LOC limit). Implements 13-stage effect dispatch (`dispatch.py` S0–S12), monotonic capability attenuation (`attenuation.py`), token & cost budgets (`budget.py`), capability grants (`grants.py`), action classification (`classifier.py`), fail-closed policy (`policy.py`), and cryptographic provenance DAG (`provenance.py`). |
| **Agency** | `vanguard/packages/agency/` | Recursive turn engine. Implements `EpisodeEngine` (`episode/engine.py`) with budget enforcement and child subagent `spawn()`; context compiler & structured token compactor (`context/`); older as-built manifests (`manifests/vg-*`). |
| **Runtime** | `vanguard/packages/runtime/` | System composition root (`root.py` `VanguardCompositionRoot`), governance & Ed25519 approvals (`governance/`), SQLite WAL event store & stream reducers (`ledger/`), and runtime RPC service (`service/`). Residual coding-specific services (`tier_escalation.py`, `skill_index.py`) scheduled for pack extraction in Waves 3–4. |
| **Adapters** | `vanguard/packages/adapters/` | Concrete implementations: Model adapters (`models/openrouter.py`, `ollama.py`, `cassette.py`, `fake.py`), Exterior Evaluator daemon & RPC client (`evaluators/daemon.py`, `client.py`), Rootless Bubblewrap Sandbox (`sandbox/rootless.py`), and SQLite WAL event store (`stores/event_store.py`). |
| **Apps** | `vanguard/packages/apps/` | Reserved boundary slot in hexagonal lattice; empty today. |
| **Layer-0 Fork** | `layer0/` | Temporary copy-fork providing SPI protocols (`spi/`), JSON-RPC 2.0 transport over UDS/stdio (`spi/jsonrpc.py`), and plugin registry/broker (`registry/`). **Known Defect F1**: Sequential scheduler driver (`scheduler/driver.py`) currently fabricates unsigned `"pass"` verdict rather than calling the exterior evaluator; to be absorbed and fixed in Waves 1–2. |
| **Code Pack #1** | `packs/code-default/` | First Modular Harness Framework (MHF) domain pack. Contains `harness.yaml`, plugin manifests (`fs`, `ast-patch`, `repo-map`, `terminal`, `evaluation-gate`, `single-planner`), prompt templates, and schema definitions. |
| **CLI / TUI** | `vanguard/clients/cli/` | Interactive terminal UI (`vg`) written in TypeScript using React and Ink. Features session management, streaming event views, human approval prompts, and cryptographic Ed25519 signing. Workspace scripts: `npm run vg`. |
| **Test Suite** | `test/` | Comprehensive test suite covering all layers (`test/kernel`, `test/contracts`, `test/agency`, `test/runtime`, `test/adapters`, `test/security`, `test/trust`, `test/packs`, `test/layer0`, `test/tools`, etc.). Full details in [`test/README.md`](test/README.md). |
| **Tooling** | `tools/` | Static architecture linters: `check_boundaries.py` (hexagonal lattice), `check_tcb_budget.py` (kernel LOC), `scan_secrets.py` (secret detector), `check_domain_blindness.py` (I-7), `check_isolation_policy.py` (I-6), `check_stale_paths.py`, `check_markdown_links.py`, and type codegen (`tools/codegen/generate_types.py`). |
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

Vanguard enforces security at multiple distinct barriers:

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
│  - Monotonic capability grant │                       │  - Cryptographic receipt tree │
└───────────────────────────────┘                       └───────────────────────────────┘
```

1. **Monotonic Attenuation**: Child agents spawned via `spawn()` can only receive a subset of the parent's capability grants. Privileges strictly narrow down the execution tree.
2. **Pre/Post Receipts**: Every side effect generates a pre-effect receipt and post-effect receipt recorded in the append-only SQLite WAL ledger.
3. **Physical & Network Isolation**: Worker execution happens in a rootless bubblewrap container (UID `10001`). The evaluator runs in an isolated environment (UID `10002`) and communicates only through signed verdicts.
4. **Fail-Closed Governance**: Dangerous actions (terminal execution outside sandbox, destructive filesystem operations) require cryptographic Ed25519 human approval.

---

## 5. Documentation Map (Normative Law vs Evidence)

| Document | Authority Level | Role & Scope |
|---|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | **Sole Normative Law** | The single living specification. All RFC-2119 keywords (`MUST`, `SHALL`, `SHOULD`) are authoritative here. |
| [`docs/05_adr/INDEX.md`](docs/05_adr/) | **Normative Law** | Append-only Architecture Decision Records. ADRs [`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0074`](docs/05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md) define the v0.6 Concept Lock. |
| [`docs/04_annex/KERNEL.md`](docs/04_annex/KERNEL.md) | **Normative Law** | Security constitution, capability dispatch rules, and S0–S12 invariants. |
| [`docs/04_annex/MEASUREMENT.md`](docs/04_annex/MEASUREMENT.md) | **Normative Law** | Lab measurement doctrine (v0.6: identity locked; promotion deferred). |
| [`002 Gap Register`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md) | **Operational Sequence** | The active Wave 0→4 roadmap and gap register. |
| [`GAMMA Lock Plan`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md) | **Lock Plan** | Concept Lock execution plan and convergence mapping. |
| [`docs/07_reviews/`](docs/07_reviews/) | **Evidence Corpus** | Forensic discoveries, gap analyses, and reviews. Non-normative. |
| [`docs/02_roadmap/`](docs/02_roadmap/), [`docs/03_sprints/`](docs/03_sprints/) | **Historical Evidence** | Pre-v0.6 milestone and sprint records (superseded as active plans). |

---

## 6. Foundation Roadmap (Waves 0 to 4)

Upon Director **APPROVAL**, execution proceeds through five focused waves:

```text
Wave 0: CI Truth & Named Falsifiers
        Rewire CI to gate vanguard/packages; activate boundary & codegen checkers.
         │
Wave 1: Fail-Closed Trust Spine
        Fix F1 (signed evaluator verdicts); enforce fail-closed ceilings; land mhf.trajectory/1.
         │
Wave 2: In-Place Lattice Convergence
        Absorb layer0 SPI, JSON-RPC, and registry into vanguard/packages; delete layer0/ fork.
         │
Wave 3: Walking Skeleton
        End-to-end framework compiling declarative manifests and plugins into FrozenHarness.
         │
Wave 4: First Real Coding-Agent E2E (Foundation Stop)
        Deliver production coding agent using packs/code-default/.
```

---

## 7. Developer & Reviewer Commands

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

## 8. Model Access & Adapter Architecture

Model providers are strictly abstracted behind `ModelPort` (`vanguard/packages/ports/model.py`):
- **Adapters on disk**: OpenRouter (`adapters/models/openrouter.py`), Ollama (`adapters/models/ollama.py`), Cassette replay (`adapters/models/cassette.py`), Fake (`adapters/models/fake.py`).
- **Provider Routing**: DeepSeek, OpenAI, Anthropic, and open-weights models are addressed via route configurations and environment keys (`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`), not separate vendor files.
- **Deterministic Testing**: Keep API keys unset during local test runs to ensure hermetic, deterministic execution against cassettes and fakes.

---

## 9. Contributor & Agent References

- **Contributor & Agent Procedure**: [`AGENTS.md`](AGENTS.md)
- **Claude Guidance**: [`CLAUDE.md`](CLAUDE.md)
- **Testing Architecture & Guide**: [`test/README.md`](test/README.md)
