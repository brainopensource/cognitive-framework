---
id: repo-root-readme
class: navigation
authority: descriptive
canonical_for:
  - repository-overview
  - quick-start
status: living
owner: documentation-architect
version: "0.9.3"
last_verified: 2026-09-03
supersedes: []
superseded_by: null
---

# AETHER — Strongforce Development (`0.9.3`)

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

AETHER is an event-sourced general agentic computation substrate: a bounded domain-blind kernel
enforces S0–S12 dispatch and typed budgets; a SQLite-WAL ledger makes state a fold over causal facts;
and composition, recursive delegation, declarative topologies, authorized durable memory, and governed
learning remain higher-layer capabilities rather than new cores. M-1 through M-3 are preservation
anchors. The current delivery path is to repair the M-8 empirical-evidence path, issue an independent
positive/negative/undeterminable disposition, then deliver Coding Max as a thin application over a
thick declarative code-pack composition. The living package is `0.9.3`. M-9 (historical gate name
`0.9.0b1`), M-10 `0.9.0`, and the post-M-10 1.0 horizon remain gated by exact-subject evidence;
mechanism presence and green tests never substitute for independently accepted receipts.

```text
observe → propose → authorize → effect → receipt → evaluate
```

| Dimension | Details |
|---|---|
| **Architectural authority** | [`VISION.md`](VISION.md) — constitutional; law and roadmap are subordinate to it |
| **Normative law** | [`docs/SPEC.md`](docs/SPEC.md) (invariants & TCB ceilings; rationale in [`docs/backend/architecture/`](docs/backend/architecture/)) |
| **Development package** | `vanguard-runtime` **0.9.3** (`pyproject.toml` is the version source). That string is not M-9 acceptance. Python `>=3.10` (tested on Python 3.12 in CI) |
| **Current status** | Execution runway: [`docs/execution/tasks.md`](docs/execution/tasks.md) (work tree), [`docs/execution/milestones.md`](docs/execution/milestones.md) (TARGET gates). Present HEAD architecture is `docs/SPEC.md` + `docs/architecture/` + `docs/backend/`. |
| **Roadmap** | `0.9.3` Strongforce line → M-8 evidence integrity → Coding Max vertical slice → M-9 installable beta (gate) → M-10 `0.9.0` → non-authorizing 1.0 qualification horizon |
| **Production truth** | `vanguard/packages/` (`domain` → `ports` → `kernel` → `agency` → `runtime` → `adapters`; `apps` is a runtime client) |

[![Vision](https://img.shields.io/badge/Law_Zero-VISION.md-purple.svg)](VISION.md)
[![Lattice](https://img.shields.io/badge/Production-vanguard%2Fpackages-green.svg)](docs/SPEC.md)
[![Execution](https://img.shields.io/badge/Status-tasks.md-orange.svg)](docs/execution/tasks.md)

## 1. What exists today vs the locked target

This section is deliberately honest about the gap. The target below is binding architecture; the
"today" column is what the code actually does.

| Capability | Today | Locked target |
|---|---|---|
| Event-sourced ledger, cold replay | **Works.** Single-writer SQLite-WAL, `State = fold(events)`, fresh-process continuation (RF-25) | unchanged |
| Canonical composition → activation → run | **Works.** One authority (RF-78–RF-84) | unchanged |
| Capability-mediated effects, typed budgets | **Works.** S0–S12, monotonic attenuation, TCB ≤ 1438 LOC | unchanged |
| Execution profiles in `D_R` | **Works.** `product`/`local`/`sandboxed`/`hermetic`, fail-closed | + retention/reproducibility axis (M-4) |
| Coding agent product (`vg code`, resume) | **RF-95 verified `passed`** (`M-4-rf95-candidate-07`); acceptance is operator-attested, not yet from an organizationally independent reviewer | accepted useful end-to-end proof with a genuinely separate reviewer (M-4) |
| Scientific trajectory capture | `/2`, model I/O and provenance mechanisms present | independently accepted release evidence |
| Agent state as projection | `AgentView` and checkpoints implemented | accepted successor baseline (M-5a) |
| Second domain (formal pack) | SAT material path demonstrated; historical control invalid | fresh graph-coloring falsifier after successor baseline (M-5b) |
| `agent.spawn` / recursive delegation | Mechanism and accepted depth-3/recovery/budget evidence present | preserve canonical nested execution lineages (M-6) |
| Metacognition / adaptive strategy | Mechanism present; published study is `undeterminable` | valid positive or negative paired study (M-6.5) |
| Topologies, scheduler, concurrency | Roles lower and spawn through `Runtime.run_composed`; multi-role effects/artifact flow remain open | three real artifact-producing topologies plus ADR-0099 disposition (M-7) |
| Memory, retrieval, skills, learning | Durable memory ports, CAS storage, and governed learning engine implemented | verified durable memory, lift, CAS promotion/rollback (M-8) |
| Hermetic assurance (RF-85) | **Available, optional, claims zero rows** | stays optional |

Mechanism presence is not milestone acceptance; [`docs/execution/milestones.md`](docs/execution/milestones.md) cites the evidence gaps.

### Immediate delivery order

1. Repair `REL-01/H0`: route empirical runs through official runtime adapters,
   execute materialized tasks and exterior oracles, and emit no synthetic
   success/lift/cost from dry-run mode.
2. Freeze and run the `REL-02/H1` single-attempt canary with content-addressed
   tasks, strict budgets, explicit missingness, and independent evaluation.
3. Close the evidence-integrity sprint with an honest M-8 disposition; a valid
   negative result closes the sprint but does not accept M-8.
4. Deliver the Coding Max vertical slice: three data-selected presets,
   port-backed repository intelligence, durable recovery/resume, multi-file and
   greenfield policies, and one thin CLI/API facade over the shared runtime.
5. Qualify Coding Max on frozen internal repository-scale tasks before enabling
   reviewer/specialist roles or experimental SBFL, mutation, branch-search, or
   ToolScript treatments.
6. Authorize and qualify M-9 (installable beta), then M-10 `0.9.0`; after M-10, qualify
   the stable framework plus Coding Max and two non-coding reference agents for
   the 1.0 horizon.
7. Run official SWE-bench optimization as a separate preregistered measurement
   program; local canaries never create an official score.

LIM (`tools/006_LLM_INT_MACHINE/`) and LEX research harnesses may assist
development and research. They never provide Vanguard runtime or acceptance authority; adopted
techniques must be independently implemented behind Vanguard interfaces and verified by tests,
falsifiers, and the normal evidence gates.

## Centralized Model Policy & Registry

All model access across runtime, benchmarks, CLI, and apps is **strictly governed by a single source of truth**:
👉 [`vanguard/packages/adapters/models/models_registry.json`](vanguard/packages/adapters/models/models_registry.json)

- **Default Coding Model (Tier 2 Flash)**: `deepseek/deepseek-v4-flash-0731` ($0.14 / $0.28 per MTok $\to$ 140,000 / 280,000 $\mu$USD).
- **Secondary Flash Model (Tier 2)**: `z-ai/glm-5.3-flash`.
- **Free Tier (Tier 1)**: `openrouter/free`, `minimax/minimax-m3:free`, `inclusionai/ling-3.0-tiny:free`.
- **Prohibition on Hardcoded Models**: Hardcoding model names or using unauthorized models (e.g. deprecated versions) in benchmarks or runtime code fails closed with `ModelUnavailable` / `ModelPolicyError`.

## 2. Documentation authority

| # | Layer | Documents |
|---|---|---|
| 0 | **Vision (constitutional)** | [`VISION.md`](VISION.md) — identity, ontology, direction |
| 1 | **Law (normative)** | [`docs/SPEC.md`](docs/SPEC.md) — normative requirements, TCB ceilings, invariants |
| 2 | **Architecture & Reference** | [`docs/architecture/`](docs/architecture/), [`docs/backend/`](docs/backend/), [`docs/frontend/`](docs/frontend/) — system workflows, subsystem design, DEC-01–DEC-11 rationale, wire contracts |
| 3 | **Product PRDs** | [`docs/product/`](docs/product/) |
| 4 | **Execution runway** | [`docs/execution/tasks.md`](docs/execution/tasks.md), [`docs/execution/milestones.md`](docs/execution/milestones.md), [`docs/execution/spec.md`](docs/execution/spec.md), [`docs/execution/technical.md`](docs/execution/technical.md), [`docs/execution/backlog.md`](docs/execution/backlog.md) |
| 5 | **Theory & Reports** | [`docs/theory/`](docs/theory/), [`docs/research/`](docs/research/), [`docs/reports/`](docs/reports/) |

A lower document may not be used to reject a Vision concept. This README introduces no architecture
of its own.

### Reading order

1. [`VISION.md`](VISION.md) — what AETHER is and where it is going.
2. [`docs/SPEC.md`](docs/SPEC.md) — normative requirements and invariants.
3. [`docs/architecture/overview.md`](docs/architecture/overview.md) & [`docs/backend/`](docs/backend/) — as-built architecture and rationale.
4. [`docs/execution/tasks.md`](docs/execution/tasks.md) & [`docs/execution/milestones.md`](docs/execution/milestones.md) (future work vs TARGET gates).

### Fast targeted navigation

For implementation and review work, use the repository's generated intelligence to route a small,
task-specific context before opening source broadly:

```bash
# 0. Bootstrap state (gates, headroom, known failures)
cat dev_context_logs/context_summary.md

# 1. Route a task to its canonical documents, inside a token budget
python3 tools/docs_rag_v0.py "<task keywords>" --budget 8000

# 2. Reverse route a code path to its canonical owner documentation + symbols
python3 tools/docs_rag_v0.py --file vanguard/packages/kernel/budget.py
```

Or the equivalent artifact flow, if you prefer reading the raw JSONL projections:

```text
dev_context_logs/context_summary.{md,json}
    -> .generated/knowledge/code-map.jsonl
    -> .generated/knowledge/{symbols,ownership}.jsonl
    -> applicable canonical documentation
    -> targeted source and tests
    -> Tier-2 logs, SQLite trajectories, and benchmark evidence as needed
```

These artifacts are navigation aids, not authorities. Confirm their repository revision/digest,
non-zero content, and referenced paths before use; an index that merely opens is not necessarily
current or usable. If LDA or generated knowledge is empty, stale, or inconsistent, fall back to
`rg --files`, targeted `rg`, canonical documentation, source, and tests. Prefer selected entries and
sections over loading whole indexes or log directories into an AI context window. The canonical
skill guide for repository intelligence is [`.agents/skills/lda-navigator/SKILL.md`](.agents/skills/lda-navigator/SKILL.md)
(with in-depth technical formulation in [`docs/onboarding/SKILL_LDA_Docs_atlas.md`](docs/onboarding/SKILL_LDA_Docs_atlas.md)).
The mandatory agent procedure and authority rules are defined in [`AGENTS.md`](AGENTS.md#repository-intelligence-navigation-protocol).

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
│   │   └── apps/                     # Thin application entrypoints (apps/coding_max)
│   └── clients/                      # TypeScript client workspaces (CLI `vg`, Desktop UI, TUI, Studio, Lab)
├── packs/code-default/               # Domain Pack #1 (MHF harness, ast-patch, repo-map, terminal)
├── test/                             # Automated test suite (1100+ tests across 17 categories)
├── tools/                            # Boundary checkers, TCB budget, secrets scanner, codegen
├── schemas/                          # v4 wire schemas and MHF plugin/harness/event schemas
└── containers/                       # Bubblewrap & OCI isolation images (UID 10001 worker, 10002 judge)
```

### Detailed Subsystem Inventory

| Subsystem | Path | Description & As-Built Capabilities |
|---|---|---|
| **Domain** | `vanguard/packages/domain/` | Pure stdlib Python. Implements primitives, wire contracts (`wire/contracts.py`, `jsonrpc.py`, `types_gen.py`), ledger reducers and events (`ledger/`), evidence models (`evidence/claim.py`), canonical selector algebra (`selectors/resource_selector.py`), RFC 8785 canonicalization (`canonicalisation/jcs.py`), and manifest definitions. Zero I/O, zero network, zero external dependencies. |
| **Ports** | `vanguard/packages/ports/` | Hexagonal abstract interfaces: `KernelPort`, `ModelPort`, `SandboxPort`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `EnvironmentPort`, `DeterminismPort`, `IndexPort`, and the 5 SPI protocols (`spi.py`). |
| **Kernel (TCB)** | `vanguard/packages/kernel/` | Pure security core (`<=1438` LOC limit; currently 1386 LOC). Implements 13-stage effect dispatch (`dispatch.py` S0–S12), monotonic capability attenuation (`attenuation.py`), typed budget algebra (`budget.py`), descriptor-bound capability grants (`grants.py`), action classification (`classifier.py`), fail-closed policy (`policy.py`), and cryptographic provenance DAG (`provenance.py`). Strictly domain-blind (Invariant I-7). |
| **Agency** | `vanguard/packages/agency/` | Recursive turn engine. Implements `EpisodeEngine` (`episode/engine.py`) with budget enforcement and attenuated child subagent `spawn()`; context compiler & structured token compactor (`context/`). |
| **Runtime** | `vanguard/packages/runtime/` | System composition and lifecycle. Modularly structured in place into `compose.py`, `session.py`, `wiring.py`, single-writer `ledger_emitter.py`, `evaluator_gateway.py`, governance approvals (`governance/`), and SQLite WAL event store adapters. |
| **Adapters** | `vanguard/packages/adapters/` | Concrete implementations: Model adapters (`models/openrouter.py`, `ollama.py`, `cassette.py`, `fake.py`), Exterior Evaluator daemon & RPC client (`evaluators/daemon.py`, `gate.py`, `signing.py`), Rootless Bubblewrap Sandbox (`sandbox/rootless.py`), and SQLite WAL event store (`stores/event_store.py`). Must NEVER import kernel or agency. |
| **Apps** | `vanguard/packages/apps/` | Thin application entrypoints (e.g., `vanguard/packages/apps/coding_max/facade.py` exposing `CodingMaxFacade` / `CodingMax`). Coordinates CLI/API requests into `ApplicationService` compositions. |
| **Plugin Registry** | `vanguard/packages/runtime/registry/` | Canonical M-3 lifecycle FSM, isolation broker, worker wire, and composition compiler; M-3 falsifier closure remains active. |
| **Code Pack #1** | `packs/code-default/` | First Modular Harness Framework (MHF) domain pack. Contains `harness.yaml`, plugin manifests (`fs`, `ast-patch`, `repo-map`, `terminal`, `evaluation-gate`, `single-planner`), prompt templates, and schema definitions. |
| **Clients** | `vanguard/clients/` | TypeScript workspaces: interactive CLI (`vg`) in `clients/cli/`, Desktop UI (`clients/desktop/`), TUI (`clients/tui/`), Lab (`clients/lab/`), and Studio (`clients/studio/`). |
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

Sequencing: [`docs/execution/milestones.md`](docs/execution/milestones.md). Work tree:
[`docs/execution/tasks.md`](docs/execution/tasks.md). Packages: [`docs/execution/backlog.md`](docs/execution/backlog.md). Deltas: [`docs/execution/spec.md`](docs/execution/spec.md). Handbook: [`docs/execution/technical.md`](docs/execution/technical.md).

Stable dependency order is `C0 -> {M-4, M-5a}`, `M-5a -> M-5b`, `M-4 -> M-6`,
`M-6 -> {M-6.5, M-7}`, and `{M-6.5, M-7} -> M-8`. Exact current state and permitted parallel work
belong only to [`docs/execution/tasks.md`](docs/execution/tasks.md) and [`docs/execution/milestones.md`](docs/execution/milestones.md).

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

### Practical Development Loop (`just`)

The repository uses `just` to expose clean, repository-owned validation commands.

```bash
# 1. Normal local development check (fast)
just check

# 2. Browse local documentation with live rendering (MkDocs + Mermaid)
just docs-serve

# 3. Validate documentation structure, frontmatter, links, and linting
just docs-check

# 4. Strict MkDocs site build
just docs-build

# 5. Regenerate machine-readable knowledge base (.generated/knowledge/)
just docs-knowledge

# 6. Complete documentation qualification gate
just docs-full

# 7. Complete local/CI qualification gate (run before PR completion / sprint closure)
just verify
```

### Python Environment (`uv`)
`pyproject.toml` and `uv.lock` are the canonical Python dependency surfaces.

```bash
# Synchronize environment with locked dependencies
uv sync

# Add or remove a package
uv add <package>
uv remove <package>

# Run commands within the uv virtual environment
uv run <command>
```

### Validation Workflow Summary

| Situation | Command | Scope & Behavior |
|---|---|---|
| **Normal development** | `just check` | Fast architectural linters, TCB budget, and doc metadata checks |
| **Browse documentation** | `just docs-serve` | Serve MkDocs site with live Mermaid rendering at `localhost:8000` |
| **Validate documentation** | `just docs-check` | Frontmatter validation, link/anchor checks, and markdownlint |
| **Before PR / Task completion** | `just verify` | Complete local/CI gate: locks, linters, tests, typecheck, docs-full |
| **Sprint / Milestone closure** | `just verify` | Complete repository qualification gate |
| **Release qualification** | `python3 tools/release_qualification.py` | Signed release envelope and external git receipt verification |

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
model-specific instruction files. Future work lives in the five-file execution runway
([`tasks.md`](docs/execution/tasks.md) and companions). Present HEAD architecture lives in `docs/SPEC.md` and `docs/architecture/`.


## 10. Mental models worth internalising

- **The episode is the program.** There is no workflow engine, no topology language, no graph
  validator — there is a loop that observes, proposes, gets authorised, acts, and reduces. If you find
  yourself declaring a shape for the work *before* the work runs, you are building the thing
  `docs/SPEC.md` §1.1 (loop-over-DAG inversion) rejects.
- **The broker grants; the sandbox contains.** Two distinct boundaries. The kernel decides *whether* an
  effect is permitted. The perimeter decides *what an attacker can reach when the kernel was wrong*. A
  logical mediator in the host language is not containment — see [`docs/backend/architecture/kernel.md`](docs/backend/architecture/kernel.md)
  and [`docs/architecture/boundaries.md`](docs/architecture/boundaries.md) before writing anything near this.
- **Content informs, never authorises.** Untrusted content may inform work; it must never authorise a
  capability-widening effect — read [`docs/backend/architecture/kernel.md`](docs/backend/architecture/kernel.md)
  before touching provenance code.
- **The verifier is outside everything.** No cognition or adapter module may import the evaluator gate
  or reason about its internals. If your change needs the evaluator's logic to be visible from agent
  code, the design is wrong, not the import lint.
- **A gate that cannot fail is not a gate.** Every control needs a must-fail counterpart proving it can
  actually deny. A green suite over unwired code is worse than no control — it manufactures false
  assurance.
- **One document is normative per contract.** If you're about to write a second source of truth for
  something `docs/SPEC.md` already owns, stop — extend the section, don't fork it.
- **Minimise what must be simultaneously correct.** The kernel has a strict <=1438 LOC target for exactly this reason —
  correctness argument size, not code golf.
- **Polyglot plugins live outside the trusted computing base.** The wire schema (JSON Schema + JCS) *is*
  the narrow waist between languages; there is no other legitimate cross-language coupling.
- **Adding a domain must not touch the core.** The kernel is strictly domain-blind (Invariant I-7).
  `python3 tools/linters/check_domain_blindness.py` is expected to return zero violations, always.
  If your PR breaks that check, the code is in the wrong package.

## Testing taxonomy (kept intact from VG-01 §4)

Three kinds, and the distinction matters when you're deciding what a new test should be:

- **Mock** — no I/O, no clock, no randomness; deterministic by construction. Fast, runs on every commit.
- **Cassette** — a recorded real interaction (model call, network response) replayed deterministically.
  Proves the code handles a real shape of response without needing a live credential in CI.
- **Live** — an actual external call. Rare, gated, and never a prerequisite for a merge unless the PR
  explicitly says so.

**Satisfiability check:** before writing a test asserting a property, ask whether the property is
actually reachable given the test's own setup. A test that can only ever pass (or can only ever be
vacuously satisfied) is not testing anything — this is how historical ADR-0028's span-reset defect
shipped with a green suite.

## Where things live

Read [`docs/SPEC.md`](docs/SPEC.md) for normative requirements and the as-built seven-package lattice
(`domain, ports, kernel, agency, runtime, adapters, apps`) enforced by `tools/linters/check_boundaries.py`.
Evaluation and measurement rules (paired designs, McNemar, empirical evidence) are specified in
[`docs/backend/architecture/assurance-evaluation.md`](docs/backend/architecture/assurance-evaluation.md) —
read it before proposing any evaluation claim.
