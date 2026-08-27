---
id: repo-root-readme
class: navigation
authority: descriptive
canonical_for:
  - repository-overview
  - quick-start
status: living
owner: documentation-architect
version: "0.7.3.dev0"
last_verified: 2026-08-26
supersedes: []
superseded_by: null
---

# AETHER — Higgs Development (`0.7.3.dev0`)

**AETHER is a general event-sourced agentic computation framework and experimental substrate.**

Complex agentic behavior emerges from composing small, observable, replaceable primitives — not from
hard-coded domain workflows. The fundamental unit is a **typed causal operation within an execution
lineage**. An "agent" is not a persistent object in this architecture: it is a *projection* over
lineage, events, artifacts, policy, context, budget, and execution boundaries. A process can die;
another process opens the ledger and continues.

Coding agents, researchers, planners, critics, teams, memory, and metacognition are different
organizations over the same substrate. Security, containment, exterior evaluation, and cryptographic
promotion evidence are **optional assurance profiles** — real capabilities, not the project's purpose.

The architectural authority is [`VISION.md`](VISION.md) (Law Zero, `ADR-0095`).

AETHER is an event-sourced general agentic computation substrate — a domain-blind ~1,373-LOC kernel enforcing S0–S12 capability dispatch and typed budgets, a durable SQLite-WAL ledger where state is a fold over causal facts and any process can reopen and continue, and above it composition, mediated recursive delegation, declarative topologies, authorized durable memory and governed CAS promotion, all as derived capabilities rather than new cores — with the backend mechanism roughly 90% built and the real remaining work being three fail-open defects plus independent evidence receipts for M-4 through M-8. Next, nothing happens on M-9/M-10 until M-8 is independently accepted — that's the standing prohibition, and the seams they'll need (immutable run-plan extensions, authorized memory ports, immutable composition manifests, evidence envelopes, exterior candidate generators) already exist as byproducts of doing M-7 and M-8 correctly; after M-8 acceptance and a fresh authorization, M-9 becomes the v1.0 integration and transfer release — frozen public protocol with a compatibility policy, a third non-coding workload proving generality beyond code and formal, long-run recovery, operational SLOs, installer and independent-user qualification — and M-10 stays post-1.0 research into causal self-models and architecture evolution, admissible only on measured superiority over simpler methods and governed through the same generator/evaluator/promoter path, with anything beyond that (distributed scheduling, topology search, continuous learning) requiring its own falsifier and successor ADR rather than inheriting authority from this roadmap.

```text
observe → propose → authorize → effect → receipt → evaluate
```

| Dimension | Details |
|---|---|
| **Architectural authority** | [`VISION.md`](VISION.md) — constitutional; law and roadmap are subordinate to it |
| **Normative law** | [`docs/SPEC.md`](docs/SPEC.md) + [`docs/01_law/`](docs/01_law/) + accepted ADRs indexed through [`0103`](docs/02_decisions/0103-progress-projection-and-checkpoint-contract.md) and [`0099`](docs/02_decisions/0099-m7-topology-scheduler-disposition.md) |
| **Development package** | `vanguard-runtime` `0.7.3.dev0` (`pyproject.toml` is the version source); Python `>=3.10` (tested on Python 3.12 in CI) |
| **Current status** | [`sprint_active.md`](docs/03_execution/sprint_active.md) is the sole current-state source; status is not duplicated here. |
| **Roadmap** | M-4 → M-5a event-derived agent → {M-5b generality ∥ M-6 delegation} → M-6.5 adaptive strategy → M-7 topologies & justified concurrency → M-8 memory/skills/learning → M-9 v1.0 |
| **Production truth** | `vanguard/packages/` (`domain` → `ports` → `kernel` → `agency` → `runtime` → `adapters`) |

[![Vision](https://img.shields.io/badge/Law_Zero-VISION.md-purple.svg)](VISION.md)
[![Lattice](https://img.shields.io/badge/Production-vanguard%2Fpackages-green.svg)](docs/SPEC.md)
[![Active board](https://img.shields.io/badge/Status-sprint__active-orange.svg)](docs/03_execution/sprint_active.md)

## 1. What exists today vs the locked target

This section is deliberately honest about the gap. The target below is binding architecture; the
"today" column is what the code actually does.

| Capability | Today | Locked target |
|---|---|---|
| Event-sourced ledger, cold replay | **Works.** Single-writer SQLite-WAL, `State = fold(events)`, fresh-process continuation (RF-25) | unchanged |
| Canonical composition → activation → run | **Works.** One authority (RF-78–RF-84) | unchanged |
| Capability-mediated effects, typed budgets | **Works.** S0–S12, monotonic attenuation, TCB ≤ 1438 LOC | unchanged |
| Execution profiles in `D_R` | **Works.** `product`/`local`/`sandboxed`/`hermetic`, fail-closed | + retention/reproducibility axis (M-4) |
| Coding agent product (`vg code`, resume) | Mechanism present; RF-95 bundle/review absent | accepted useful end-to-end proof (M-4) |
| Scientific trajectory capture | `/2`, model I/O and provenance mechanisms present | independently accepted release evidence |
| Agent state as projection | `AgentView` and checkpoints implemented | accepted successor baseline (M-5a) |
| Second domain (formal pack) | SAT material path demonstrated; historical control invalid | fresh graph-coloring falsifier after successor baseline (M-5b) |
| `agent.spawn` / recursive delegation | Partial; synthetic-success fallback and recovery/identity/budget gaps | canonical nested execution lineages (M-6) |
| Metacognition / adaptive strategy | **Accepted.** Verified paired study and independent acceptance envelope | valid positive or negative paired study (M-6.5) |
| Topologies, scheduler, concurrency | Lowering integrated into `Runtime.run_composed`; ADR-0099 recorded | three topologies plus ADR-0099 disposition (M-7) |
| Memory, retrieval, skills, learning | Durable memory ports, CAS storage, and governed learning engine implemented | verified durable memory, lift, CAS promotion/rollback (M-8) |
| Hermetic assurance (RF-85) | **Available, optional, claims zero rows** | stays optional |

Mechanism presence is not milestone acceptance; the active board cites the evidence gaps.

## 2. Documentation authority

| # | Layer | Documents |
|---|---|---|
| 0 | **Vision (constitutional)** | [`VISION.md`](VISION.md) — identity, ontology, direction |
| 1 | **Law (normative)** | [`docs/SPEC.md`](docs/SPEC.md), [`docs/01_law/`](docs/01_law/) |
| 2 | **Decisions (binding)** | [`docs/02_decisions/`](docs/02_decisions/) |
| 3 | **Contracts & protocols** | [`docs/05_contracts/`](docs/05_contracts/), [`docs/06_protocols/`](docs/06_protocols/), `schemas/` |
| 4 | **Sequencing** | [`docs/03_execution/milestones.md`](docs/03_execution/milestones.md), [`backlog.md`](docs/03_execution/backlog.md) |
| 5 | **Authorization** | [`docs/03_execution/sprint_active.md`](docs/03_execution/sprint_active.md); [`sprint_upcoming.md`](docs/03_execution/sprint_upcoming.md) is staging |
| 6 | **Communication** | this README, [`docs/04_architecture/`](docs/04_architecture/), [`docs/07_engineering/`](docs/07_engineering/) |

A lower document may not be used to reject a Vision concept. This README introduces no architecture
of its own.

### Reading order

1. [`VISION.md`](VISION.md) — what AETHER is and where it is going.
2. [`docs/SPEC.md`](docs/SPEC.md) — normative requirements and invariants.
3. [`docs/01_law/`](docs/01_law/) — detailed contracts (`DISPATCH`, `RUNTIME`, `EXTENSIBILITY`, `EVIDENCE`, `MEASUREMENT`, `SECURITY`).
4. [`docs/02_decisions/INDEX.md`](docs/02_decisions/INDEX.md) — accepted ADRs through `0102`.
5. [`docs/03_execution/milestones.md`](docs/03_execution/milestones.md), [`backlog.md`](docs/03_execution/backlog.md), then [`sprint_active.md`](docs/03_execution/sprint_active.md).
6. [`docs/04_architecture/overview.md`](docs/04_architecture/overview.md) — as-built map, navigational only.

---

## 3. What Exists in This Repository (As-Built Inventory)

The codebase keeps canonical production truth in `vanguard/packages/`, alongside domain packs,
tooling, and test infrastructure:

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
| **Plugin Registry** | `vanguard/packages/runtime/registry/` | Canonical M-3 lifecycle FSM, isolation broker, worker wire, and composition compiler; M-3 falsifier closure remains active. |
| **Code Pack #1** | `packs/code-default/` | First Modular Harness Framework (MHF) domain pack. Contains `harness.yaml`, plugin manifests (`fs`, `ast-patch`, `repo-map`, `terminal`, `evaluation-gate`, `single-planner`), prompt templates, and schema definitions. |
| **CLI / TUI** | `vanguard/clients/cli/` | Interactive terminal UI (`vg`) written in TypeScript using React and Ink. Workspace scripts: `npm run vg`. |
| **Test Suite** | `test/` | Comprehensive test suite covering all layers (`test/kernel`, `test/contracts`, `test/agency`, `test/runtime`, `test/adapters`, `test/security`, `test/trust`, `test/packs`, `test/falsifiers`, `test/registry`). Details in [`test/README.md`](test/README.md). |
| **Tooling** | `tools/` | Static architectural linters: boundary lattice, TCB budget, secrets, domain blindness, isolation, event coverage, duplication, stale paths, Markdown links, RF-72 identifier allocation, and type codegen. |
| **Containers** | `containers/` | Container isolation images establishing process identity: Worker UID `10001` (`worker.Dockerfile`) vs Evaluator UID `10002` (`evaluator.Dockerfile`). |

---

## 4. Architecture & Hexagonal Boundary Lattice

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

## 5. Roadmap & Execution Status

Sequencing: [`docs/03_execution/milestones.md`](docs/03_execution/milestones.md). Authorization:
[`docs/03_execution/sprint_active.md`](docs/03_execution/sprint_active.md).

Stable dependency order is `C0 -> {M-4, M-5a}`, `M-5a -> M-5b`, `M-4 -> M-6`,
`M-6 -> {M-6.5, M-7}`, and `{M-6.5, M-7} -> M-8`. Exact current state and permitted parallel work
belong only to the active board.

`M7-01` remains a named parallel measurement lane (`ADR-0092`) and ends in an explicit decision to
implement, simplify, or cancel advanced scheduling.

Historical milestone identifiers keep their meaning; `ADR-0095` §4 is the translation table.

---

## 6. Optional Assurance: Trust, Attenuation & Isolation

> These are **optional profiles**, not the identity of AETHER and not prerequisites for ordinary
> development (`ADR-0094`, `ADR-0095`). What is always binding is honesty: the resolved
> `ExecutionProfile` enters `D_R`, no run may claim assurance it did not have, and an explicitly
> requested containment mode that is unavailable fails closed rather than falling back to the host.

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
2. **Intent and Receipt**: Every privileged side effect records durable pre-effect intent before execution and a terminal receipt, failure, rejection, or explicit undeterminable reconciliation afterward.
3. **Physical & Network Isolation**: Worker execution happens in a rootless bubblewrap container (UID `10001`). The evaluator runs in an isolated environment (UID `10002`) and communicates only through signed verdicts.
4. **Fail-Closed Governance**: Dangerous actions require cryptographic Ed25519 human approval.

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
python3 tools/linters/check_boundaries.py       # Hexagonal lattice enforcement
python3 tools/linters/check_tcb_budget.py       # TCB kernel LOC budget check
python3 tools/linters/scan_secrets.py           # Secret & credential leak scanner
python3 tools/linters/check_domain_blindness.py # Kernel domain blindness (I-7)
python3 tools/linters/check_isolation_policy.py # Sandbox isolation policy (I-6)
python3 tools/linters/check_falsifier_ids.py    # RF namespace and allocation integrity
python3 tools/linters/check_markdown_links.py   # Documentation link integrity
python3 tools/linters/check_stale_paths.py      # Stale path reference checker
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
- **Testing Architecture & Guide**: [`test/README.md`](test/README.md)

`AGENTS.md` is the single tool-neutral contributor contract for humans and AI agents. There are no
model-specific instruction files; current execution state lives only in
[`sprint_active.md`](docs/03_execution/sprint_active.md).
