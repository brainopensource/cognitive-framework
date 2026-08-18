# Vanguard General Task Solver (GTS)

> **A SOTA verifiable, modular meta-harness runtime that accumulates machine competence under an exterior judge it cannot game.**

[![Vanguard Core Integrity](https://img.shields.io/badge/Vanguard-v0.4.5--beta-blue.svg)](docs/scrum/sprints/wave20/evidence/s20-g-03-release-claims.md)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal_plane_separated-green.svg)](docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md)
[![Verification](https://img.shields.io/badge/Tests-488_passed-success.svg)](tools/run_active_contract_tests.py)
[![TCB Budget](https://img.shields.io/badge/TCB_LOC-1315%2F1438-brightgreen.svg)](tools/check_tcb_budget.py)

---

## 1. Executive Summary & Core Thesis

Vanguard is an agentic coding and general task solver framework built on a fundamental security and architectural thesis (`VG-02`):

> **When an agent solves a task, what solved it — model, scaffold, prompt, tools, context policy, retry — must be separable, and the judge must be unreachable from the judged.**

Vanguard enforces an invariant, deterministic turn lifecycle across all domains:
```text
observe ──▶ propose ──▶ authorize ──▶ effect ──▶ receipt ──▶ evaluate
```

---

## 2. Orders of Abstraction & Biological Framework Dictionary

Vanguard conceptualizes software architecture using a **Biological Hierarchy of Emergent Competence**.

> [!IMPORTANT]
> **Architectural Invariant (GTS-13C §3.6):** The biological vocabulary is **NOT an OOP class hierarchy** (we do *not* write `class Cell(Polymer)`). It is a conceptual taxonomy and an **emergent telemetry depth** logged in `lam.sqlite`. Build one recursive coordinator, and the biological hierarchy becomes an empirical finding in the ledger.

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ LEVEL 9: ENTITY / AGI SWARM       ──▶ Autonomous Multi-Agent Orchestration & Swarm Topology │
│ LEVEL 8: ORGANS & SYSTEMS         ──▶ Paired Measurement Lab (`lab harness bench`)          │
│ LEVEL 7: CELLS                    ──▶ Sandboxed Autonomous Agent Workspace & Lifecycle      │
│ LEVEL 6: ORGANELLES               ──▶ Exterior Signed Evaluator (UID 10002) & Double Probes │
│ LEVEL 5: GENES (DNA / RNA)        ──▶ Declarative Manifest Packs (`vg-code-*`, `AGENTS.md`)  │
│ LEVEL 4: PROTEINS & ENZYMES       ──▶ Context Compactor (L1–L5) & `ProposalTranslator`      │
│ LEVEL 3: LINEAR POLYMERS          ──▶ `EpisodeEngine` Depth-1 Multi-Turn Recursion Loop     │
│ LEVEL 2: MOLECULES                ──▶ Attenuation Kernel & Rootless Bubblewrap Sandbox       │
│ LEVEL 1: ATOMS                    ──▶ Abstract Ports (`ModelPort`) & Single Verbs (`fs.read`)│
│ LEVEL 0: SUB-ATOMIC PRIMITIVES    ──▶ Canonical Wire Value Objects, Hashes & Ed25519 Keys   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Biological Dictionary: From Primitives to Emergent AGI

| Biological Tier | Biological Analogy | Vanguard Code Component & Realization | Emergent Competence |
|---|---|---|---|
| **0. Sub-Atomic** | Protons, Neutrons, Electrons (Pure energy/charge, no chemistry alone) | `domain/wire/contracts.py`: Canonical Value Objects, SHA-256 digests, Ed25519 asymmetric keys, JsonSchema contracts. | **Byte-Level Determinism** |
| **1. Atoms** | Carbon, Hydrogen, Oxygen (Periodic table elements with valency & affinity) | `ports/`: `ModelPort`, `LedgerPort`, `EvaluatorPort`; Single Verbs (`fs.read`, `fs.search`, `fs.write`, `patch.apply`, `proc.exec`). | **Capability Valency** |
| **2. Molecules** | Water, Glucose, Amino Acid Monomers (Atoms bound into functional units) | `kernel/dispatch.py`, `adapters/sandbox/rootless.py`: Attenuation Kernel, USD micro-budget leases, rootless Bubblewrap containerization. | **Sandboxed Isolation** |
| **3. Linear Polymers** | Unfolded Peptide Chains (Sequential monomers linked in series) | `agency/episode/engine.py`: `EpisodeEngine` depth-1 sequential multi-turn recursion (`observe → propose → authorize → effect → receipt → evaluate`). | **Multi-Turn Traceability** |
| **4. Functional Proteins** | Folded Enzymes & Molecular Motors (Folded polymers with active chemical catalytic function) | `agency/context/compiler.py`, `adapters/models/invocation.py`: L1–L5 Context Compactor, byte-stable system prompts, `ProposalTranslator`. | **Cognitive Pruning & Efficiency** |
| **5. Genes (DNA / RNA)** | Nucleic Acid Sequence Manuals (Instructions dictating protein assembly) | `agency/manifests/`: Pure-data JSON Manifests (`vg-code-claude-shaped`, `vg-code-opencode-shaped`), `AGENTS.md` / `CLAUDE.md` context discovery. | **Declarative Harness Alignment** |
| **6. Organelles** | Mitochondria, Ribosomes (Membrane-bound functional cellular machinery) | `adapters/evaluators/daemon.py`: Out-of-process signed Evaluator Daemon (UID `10002`) running sealed double probes. | **Un-gameable Verification** |
| **7. Cells** | Single-cell Organisms (Self-contained, bounded factory operating continuously under DNA instructions) | `runtime/root.py`, `runtime/coding_coordinator.py`: Autonomous Agent Workspace runtime executing episodes end-to-end. | **Autonomous Problem Solving** |
| **8. Organs & Systems** | Tissues, Muscular & Nervous Systems (Coordinated specialized cell groups) | `lab/`: Paired Measurement Laboratory (`lab harness bench`), McNemar A/A floor tracking against undeletable `vg-shell-only`. | **Empirical Benchmark Laboratory** |
| **9. Entity / AGI Swarm** | Conscious Macro-Organism (Harmonious coordination of trillions of specialized nanomachines) | `runtime/governance/`: Multi-Agent Competence Distillation (`O-01`), Cross-Agent Delegation, and Heterogeneous Swarm Orchestration. | **Emergent Machine AGI** |

---

## 3. Six-Plane Architectural Blueprint

Vanguard isolates responsibilities into six decoupled planes ([`03_vanguard_architecture_planes_and_execution_model_v040.md`](docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md)):

```text
Interaction  ──▶ CLI · TUI · Inspector · Web Surface
                     │ (authenticated RPC requests)
Cognition    ──▶ Episodes · Operators · Context Compaction (L1–L5)
                     │ (proposals)
Control      ──▶ Broker · Attenuation Kernel · Leases · Ed25519 Approvals
                     │ (scoped capability grants)
Workload     ──▶ Sandboxed Environment Adapters (Git, FS, Shell, LSP)
                     │ (execution receipts)
Evidence     ──▶ Exterior Evaluators (UID 10002) · Claims · Oracle Probes
                     │ (unreachable signed verdicts)
Evolution    ──▶ Distillation · Attestation · Promotion Pointers (O-01)
```

---

## 4. Repository Structure & Package Lattice

Below is the project directory tree illustrating the main modules, submodules, clients, benchmark tools, and execution environments down to an actionable navigation depth.

```text
Aether-D-System/
├── .github/                      # CI workflows and repository configuration
│   └── workflows/ci.yml          # Boundary checks, TCB budget, secret scans, & test CI gates
├── benchmarkings/                # Empirical benchmark suites & zero-hint execution runners
│   ├── zero_hint_v1/             # Phase 1 zero-hint benchmark task set
│   ├── tasks_phase2/             # Phase 2 multi-turn repository coding task set
│   ├── tasks_phase3/             # Phase 3 task set (TableWorld & non-coding structured reasoning)
│   ├── swe_pro_tiers/            # Tiered SWE-bench coding evaluation suites
│   └── frontier_tier5_datalog_engine/ # Frontier-tier logic & datalog evaluation engine
├── containers/                   # OCI container specs & build digests
│   ├── worker.Dockerfile         # Unprivileged rootless Bubblewrap worker container (UID 10001)
│   ├── evaluator.Dockerfile      # Out-of-process signed evaluator daemon container (UID 10002)
│   └── manifest.json             # Immutable release build SHA-256 digests
├── docs/                         # Normative specifications, architectural roadmaps, & sprint logs
│   ├── main_v4/                  # Core Vanguard v4 Specification Corpus (VG-00..12, GTS-13C)
│   ├── agile/                    # Sprint evidence, dogfood run logs, and release gates
│   └── reviews/done/             # Sprint review summaries & architectural decisions
├── lab/                          # Paired Measurement Laboratory framework
│   ├── bench.py                  # Lab harness bench runner for A/A control & McNemar tests
│   ├── build.py                  # Environment setup & container preparation for lab tasks
│   ├── diff.py                   # Automated git diff generation and evaluation packaging
│   └── tasks/                    # Standardized evaluation benchmark tasks
├── test/                         # Comprehensive Python test suite (unit, integration, security)
│   ├── adapters/                 # Tests for sandbox, model, and verifier adapters
│   ├── agency/                   # Tests for context compaction, compiler, and episode recursion
│   ├── benchmarks/               # Tests for benchmark runners and evaluation harnesses
│   ├── contracts/                # Contract compliance tests for wire schemas and value objects
│   ├── governance/               # Tests for Ed25519 approval policies and permission gates
│   ├── integration/              # End-to-end multi-turn recursion and integration tests
│   ├── kernel/                   # Tests for attenuation kernel, budget leases, and action dispatch
│   ├── lab/                      # Tests for lab bench execution and patch diffing
│   ├── runtime/                  # Tests for composition root and task coordinators
│   ├── security/                 # Sandbox isolation and privilege escalation security tests
│   ├── support/                  # Test helpers, mock fixtures, and synthetic state builders
│   └── trust/                    # Cryptographic signature, hash chain, and claim verifiers
├── tools/                        # Repository validation, security, and developer utilities
│   ├── 001_LLM_API_ROUTER/       # Local proxy router for routing and mocking LLM calls
│   ├── 002_LLM_API_MOCK/         # Deterministic mock server for model API integration tests
│   ├── check_boundaries.py       # Enforces unidirectional package import lattice rules
│   ├── check_tcb_budget.py       # Enforces Kernel Trusted Computing Base (TCB) LOC limit (<= 1438)
│   ├── scan_secrets.py           # Scans repository for unencrypted keys, tokens, or credentials
│   ├── run_dogfood_r9.py         # Executes production dogfood release verification suite
│   └── run_active_contract_tests.py # Runs active contract suite across package boundaries
└── vanguard/                     # Physical Vanguard system code
    ├── clients/                  # User-facing client applications and client core libraries
    │   ├── cli/                  # TypeScript CLI application with interactive Ink/React TUI
    │   │   ├── src/adapters/     # Client-side RPC adapters & IPC communication channels
    │   │   ├── src/application/  # State management, episode controls, and command parsing
    │   │   ├── src/headless/     # Non-interactive CLI runner for automated pipelines
    │   │   └── src/tui/          # Terminal UI components built with Ink & React
    │   └── client-core/          # Shared TypeScript type definitions, contracts, and utilities
    └── packages/                 # Core Python backend packages (hexagonal lattice)
        ├── domain/               # Pure value objects, wire contracts, and state reducers (Order 0)
        │   ├── primitives/       # Core domain types (hashes, capabilities, leases, Ed25519 keys)
        │   ├── wire/             # Canonical wire contracts, JSON schemas, & language bindings
        │   ├── ledger/           # Turn event schemas, immutable reducers, & cryptographic log chains
        │   ├── artifacts/        # Task execution output schemas, file diffs, & patch payloads
        │   ├── evidence/         # Verifier proof tokens, probe claims, & signed evaluation verdicts
        │   ├── selectors/        # Pure state queries and telemetry filtering functions
        │   └── canonicalisation/ # Deterministic byte-sorting & JSON normalization utilities
        ├── ports/                # Abstract interfaces for external capabilities (Order 1)
        │   ├── model.py          # Abstract LLM inference port (`ModelPort`)
        │   ├── sandbox.py        # Abstract execution sandbox port (`SandboxPort`)
        │   ├── evaluator.py      # Abstract sealed evaluator port (`EvaluatorPort`)
        │   ├── event_store.py    # Abstract event ledger storage interface (`EventStorePort`)
        │   ├── blob_store.py     # Abstract binary artifact storage interface (`BlobStorePort`)
        │   ├── kernel.py         # Abstract capability kernel interface
        │   ├── environment.py   # Abstract workspace environment configuration interface
        │   └── determinism.py    # Deterministic clock, seed, and execution control contract
        ├── kernel/               # Capability attenuation & turn dispatch engine (Order 2)
        │   ├── dispatch.py       # Universal turn lifecycle engine (observe->propose->auth->effect->receipt->eval)
        │   ├── attenuation.py    # Capability attenuation kernel (`T2`) enforcing dynamic scope reduction
        │   ├── budget.py         # Micro-budget USD leases, token trackers, and execution limits
        │   ├── grants.py         # Capability grant issuance, attenuation tree, and scope validation
        │   ├── classifier.py     # Security action risk classification and approval tiering
        │   ├── policy.py         # Security policy rules and capability permission maps
        │   ├── provenance.py     # Cryptographic lineage and action authorization origin tracking
        │   └── model.py          # Internal kernel model representation and capability boundary definitions
        ├── agency/               # Context compaction, proposal translation, and multi-turn loops (Order 3)
        │   ├── context/          # L1–L5 Context Compactor and byte-stable prompt compiler
        │   │   ├── compaction.py # Content compression, history pruning, and token sliding-window logic
        │   │   ├── compiler.py   # Assembles system prompts, capabilities, and dynamic AGENTS.md rules
        │   │   ├── layers.py     # L1–L5 context layer definitions (System -> Workspace -> Ephemeral)
        │   │   └── regrounding.py# Context regrounding logic following error states or phase transitions
        │   ├── episode/          # Multi-turn execution loop driver (`EpisodeEngine`)
        │   │   ├── engine.py     # Depth-1 multi-turn recursion loop driving agent proposal cycles
        │   │   └── state.py      # Episode state machine, trajectory history, and state transitions
        │   └── manifests/        # Declarative, data-only harness manifest definitions (Order 4)
        │       ├── loader.py     # Manifest parser, schema validator, and configuration inflator
        │       ├── discovery.py  # Workspace manifest detection (AGENTS.md / CLAUDE.md / aliases.json)
        │       └── vg-*/         # Manifest configs (e.g. `vg-code-claude-shaped`, `vg-shell-only`)
        ├── runtime/              # Composition root, daemon lifecycle, & task orchestration
        │   ├── root.py           # Primary composition root linking concrete adapters to abstract ports
        │   ├── coding_coordinator.py # Autonomous coding coordinator for repository task resolution
        │   ├── coding_entrypoint.py  # Entrypoint for spawning autonomous solving sessions
        │   ├── coding_plan.py    # Dynamic task breakdown, step planning, and strategy tracking
        │   ├── coding_progress.py# Progress monitoring, failure recovery, and step completion tracking
        │   ├── coding_verification.py# Automated local test verification before submitting solutions
        │   ├── governance/       # Ed25519 human approval flows, security checks, and gate releases
        │   ├── lab_driver.py     # Execution driver for lab benchmark evaluation suites
        │   ├── tier_escalation.py# Dynamic model escalation logic (Free -> Cheap -> Frontier)
        │   ├── model_selection.py# Model routing policy based on task difficulty and budget
        │   ├── session_log.py    # Execution session recorder (`lam.sqlite` SQLite database)
        │   └── service/          # Vanguard daemon RPC server and API handlers
        └── adapters/             # Concrete implementations of external ports (Order 1/2/5)
            ├── models/           # Concrete LLM integrations (OpenRouter, Ollama, DeepSeek, cassettes)
            │   ├── openrouter.py # OpenRouter API provider implementation
            │   ├── ollama.py     # Local Ollama model provider implementation
            │   ├── invocation.py # Standardized prompt formatting and API payload serialization
            │   ├── cassette.py   # VCR-style request/response recording for offline testing
            │   └── routing.py    # API key loading and multi-provider endpoint routing
            ├── sandbox/          # Concrete execution environments
            │   ├── rootless.py   # Linux Bubblewrap rootless container isolation backend
            │   ├── worker.py     # Sandboxed execution worker process manager
            │   └── fake.py       # In-memory mock sandbox for unit testing
            ├── evaluators/       # Sealed evaluation backends
            │   ├── daemon.py     # Signed verifier daemon running as unprivileged UID 10002
            │   ├── client.py     # RPC client for communicating with evaluator daemons
            │   ├── isolated.py   # Isolated process test runner for local evaluations
            │   └── signing.py    # Ed25519 payload signing and cryptographic verifier attestations
            ├── stores/           # Storage implementation backends
            │   ├── event_store.py  # SQLite-backed event store for persistent episode logs
            │   └── fs_blob.py    # Filesystem-backed binary artifact store
            └── environment/      # Concrete host environment hooks and workspace initialization
```

### High-Level Module & Submodule Architecture Breakdown

#### 1. Backend Core (`vanguard/packages/`)
The Python backend enforces hexagonal architecture and unidirectional dependency layers (enforced by `check_boundaries.py` in CI):

- **`domain/` (Order 0 — Lowest Level)**: Pure, zero-dependency data models, contracts, and reducers.
  - `primitives/`: Core domain primitives including cryptographic hashes, capability tokens, USD micro-budget leases, and Ed25519 keys.
  - `wire/`: Canonical JSON wire formats (`contracts.py`, `contracts.ts`) defining exact schemas exchanged across process boundaries.
  - `ledger/`: Append-only turn event definitions and pure state reducers driving deterministic execution history.
  - `artifacts/`: Structures representing execution output payloads, code diffs, and patch artifacts.
  - `evidence/`: Verifier proof tokens, probe claims, and signed evaluation verdicts.
  - `selectors/`: Pure query functions used to extract state metrics and telemetry from event streams.
  - `canonicalisation/`: Byte-stable sorting and JSON canonicalization utilities for hash generation.

- **`ports/` (Order 1)**: Abstract interfaces (Python ABCs) isolating internal logic from external infrastructure.
  - `model.py` (`ModelPort`): Interface for model completion, prompt formatting, and token generation.
  - `sandbox.py` (`SandboxPort`): Interface for isolated process execution and workspace filesystem access.
  - `evaluator.py` (`EvaluatorPort`): Interface for sealed, out-of-process task evaluation.
  - `event_store.py` / `blob_store.py`: Interfaces for event persistence and binary output storage.
  - `kernel.py`, `environment.py`, `determinism.py`: Contracts for attenuation kernels, workspace sandboxes, and deterministic hardware clocks/seeds.

- **`kernel/` (Order 2)**: Central capability control, security attenuation, and turn dispatch logic.
  - `dispatch.py`: Universal turn engine driving the 6-stage turn cycle (`observe -> propose -> authorize -> effect -> receipt -> evaluate`).
  - `attenuation.py` (`T2`): Dynamically narrows capability scope so an agent cannot escalate privileges during execution.
  - `budget.py`: Tracks token expenditures and USD micro-budget leases.
  - `grants.py`: Issues, manages, and validates capability token trees.
  - `classifier.py` & `policy.py`: Evaluates proposed actions against security policies and assigns action risk tiers.
  - `provenance.py`: Verifies cryptographic origin and authorization lineage for every requested action.

- **`agency/` (Order 3)**: High-level cognitive assembly, prompt context compression, and multi-turn loops.
  - `context/`: L1–L5 Context Compactor & Compiler. `compiler.py` builds byte-stable system prompts incorporating `AGENTS.md` rules; `compaction.py` compresses long turn histories; `layers.py` structures layers from system to ephemeral memory; `regrounding.py` re-orients the agent after errors.
  - `episode/`: `engine.py` (`EpisodeEngine`) runs depth-1 multi-turn recursion loops driving agent proposal cycles, supported by `state.py` trajectory tracking.
  - `manifests/`: Declarative, data-only harness manifests (`loader.py`, `discovery.py`) defining agent behavioral profiles (`vg-code-claude-shaped`, `vg-shell-only`, etc.).

- **`runtime/` — Composition Root & Daemon Lifecycle**:
  - `root.py`: Main composition root injecting concrete adapters into abstract ports.
  - `coding_coordinator.py` & `coding_entrypoint.py`: High-level orchestrators managing autonomous coding problem-solving sessions end-to-end.
  - `coding_plan.py`, `coding_progress.py`, `coding_verification.py`: Generate step-by-step resolution plans, monitor execution progress, and verify solutions via local test suites.
  - `tier_escalation.py` & `model_selection.py`: Route prompts to appropriate model tiers, escalating from local/free models to paid frontier models upon failures.
  - `governance/`: Handles Ed25519 human approval signatures and sprint release signoff verification.
  - `session_log.py` & `telemetry.py`: Logs full turn trajectories to local `lam.sqlite` databases.
  - `service/`: Exposes Vanguard runtime via IPC/RPC daemon endpoints.

- **`adapters/` (Order 1/2/5 — External Boundary)**: Concrete drivers implementing abstract ports.
  - `models/`: Integrations for OpenRouter (`openrouter.py`), local Ollama (`ollama.py`), prompt formatting (`invocation.py`), cassette VCR recording (`cassette.py`), and key routing (`routing.py`).
  - `sandbox/`: Linux Bubblewrap rootless container sandbox (`rootless.py`), worker process isolation (`worker.py`), and mock sandboxes (`fake.py`).
  - `evaluators/`: Sealed evaluation backends including signed verifier daemon running under UID 10002 (`daemon.py`), client RPCs (`client.py`), and Ed25519 verdict signers (`signing.py`).
  - `stores/`: SQLite event storage and filesystem blob storage implementations.

---

#### 2. User Interfaces & CLI (`vanguard/clients/`)
- **`cli/`**: TypeScript application providing interactive terminal interfaces.
  - `src/tui/`: Terminal User Interface built with React and Ink, providing visual turn progress, live budget trackers, and diff views.
  - `src/headless/`: Non-interactive CLI mode for automated benchmark runs and headless server integration.
  - `src/application/` & `src/adapters/`: Client state management and RPC connectors to the Vanguard Python runtime.
- **`client-core/`**: Shared TypeScript contracts, wire interfaces, and client utilities.

---

#### 3. Measurement & Benchmarks (`lab/` & `benchmarkings/`)
- **`lab/`**: Paired Measurement Laboratory framework (`bench.py`, `build.py`, `diff.py`) running paired A/A and A/B benchmark controls with McNemar statistical hypothesis testing to measure agent improvements.
- **`benchmarkings/`**: Benchmark datasets (`zero_hint_v1`, `tasks_phase2`, `tasks_phase3`, `swe_pro_tiers`, `frontier_tier5_datalog_engine`) containing zero-hint coding, structured data, and logic tasks.

---

#### 4. Containerization & Security Isolation (`containers/`)
- `worker.Dockerfile`: Unprivileged Bubblewrap worker sandbox (UID 10001) for isolated tool execution.
- `evaluator.Dockerfile`: Out-of-process signed verifier daemon container (UID 10002) unreachable from the agent environment.
- `manifest.json`: Cryptographic SHA-256 build digests ensuring reproducible environment builds.

---

#### 5. Tools & Integrity Verification (`tools/`)
- Structural enforcement scripts (`check_boundaries.py` enforcing unidirectional imports, `check_tcb_budget.py` enforcing kernel LOC <= 1438).
- Security scripts (`scan_secrets.py` to prevent credential exposure).
- Gate release and contract test suites (`run_dogfood_r9.py`, `run_active_contract_tests.py`).
- Mock LLM routers (`001_LLM_API_ROUTER`, `002_LLM_API_MOCK`) for offline test execution.

---

#### 6. Test Suite (`test/`)
- Comprehensive test suite organized by subsystem matching the backend package lattice: `kernel/`, `agency/`, `runtime/`, `adapters/`, `contracts/`, `governance/`, `security/`, `trust/`, `lab/`, and `benchmarks/`.

---

#### 7. Specifications & Documentation (`docs/`)
- `main_v4/`: Vanguard v4 Specification Corpus (`VG-00` through `VG-12`, `GTS-13C`).
- `agile/` & `reviews/done/`: Sprint planning docs, dogfood logs, and architectural decision reviews.

### CI Architectural Boundary Lattice

Import direction is strictly unidirectional (`tools/check_boundaries.py`):

$$\text{domain} \longleftarrow \text{ports} \longleftarrow \text{kernel} \longleftarrow \text{agency} \longleftarrow \text{runtime} \longrightarrow \text{adapters}$$

- **`domain`**: Standard library only. Imports nothing else in the repository.
- **`ports`**: Imports `domain` only.
- **`kernel`**: Imports `domain` and `ports`.
- **`agency`**: Imports `domain`, `ports`, and `kernel`.
- **`adapters`**: Imports `domain` and `ports`. Zero direct imports of `kernel` or `agency`.
- **`runtime`**: Composition root injecting concrete adapters into abstract ports.

---

## 5. Master Roadmap & Sprint Overview

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1 & 2: FOUNDATION, KERNEL & BETA RELEASE (Sprint 0 – Sprint 6B) [COMPLETE]      │
│ • Sprint 0–1: Governance, ICD, CI boundaries, wire contracts (T1)                   │
│ • Sprint 2–5:  Ledger store, attenuation kernel (T2), Episode recursion (T4), UID 10002 │
│ • Sprint 6A-B: Rootless Bubblewrap worker, Ed25519 approval, Gate R9 Dogfood 3/3 PASS│
│                👉 DELIVERS: Vanguard MVP Beta v0.4.1-beta Release Candidate           │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 3: HARNESS RECONSTRUCTIONS, MEASUREMENT & RELEASE (Sprint 7 – Sprint 10)       │
│ • Sprint 7: Pure-data manifests (`vg-code-claude-shaped`, `vg-code-opencode-shaped`),  │
│             aliases.json translation, dynamic `AGENTS.md` context discovery          │
│ • Sprint 8: Laboratory bench (`lab harness bench`), paired A/A control against       │
│             `vg-shell-only`, verifier-deployment gap measurement                     │
│ • Sprint 9: TableWorld non-coding structured-data witness with zero kernel changes   │
│ • Sprint 10: Non-authoritative memory recall (L5), offline distillation (O-01),     │
│              and Phase 3 release gate dossier                                        │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Model Escalation & Routing Hierarchy

Vanguard abstracts models behind `ModelPort`. Local GPU models ($0) handle routine syntactic tasks, while cloud models (OpenRouter/OpenAI/Anthropic) handle high-tier refactoring:

# Openrouter Guidelines

    OpenRouter:
        base_url: https://openrouter.ai/api/v1
        api_key_env: "OPENROUTER_API_KEY" on ModelRoute (the engine reads the env var)
        Verified Free Models:
            openrouter/free
            inclusionai/ling-3.0-tiny:free
            poolside/laguna-s-2.1:free
            cohere/north-mini-code:free
            google/gemma-4-26b-a4b-it:free
            nvidia/nemotron-3-super-120b-a12b:free
            openai/gpt-oss-20b:free
        Verified Low-Cost Paid Models: 8. deepseek/deepseek-v4-flash 9. xiaomi/mimo-v2.5
        Frontier Cloud Models: z-ai/glm-5.2, openai/gpt-5.6-luna, deepseek/deepseek-v4-pro, minimax/minimax-m3
    DeepSeek API:
        base_url: https://api.deepseek.com/v1
        model: deepseek-reasoner or deepseek-coder on ModelRoute
        api_key_env: "DEEPSEEK_API_KEY"
    OpenAI:
        base_url: https://api.openai.com/v1
        model: gpt-4o on ModelRoute
        api_key_env: "OPENAI_API_KEY"

Ollama Guidelines

    Tier 1 models:
        llama3.2:3b
        qwen2.5:1.5b
    Tier 2 models: 3. qwen3.6:27b 4. deepseek-r1:14b


---

## 7. Verification & Release Verification Commands

Verify repository integrity, boundaries, TCB budget, and test suite locally:

```bash
# 1. Verify Backend Artifacts & OCI Image Manifests (--release)
python3 tools/check_backend_artifacts.py --release

# 2. Check Package Import Boundaries (115 source files)
python3 tools/check_boundaries.py

# 3. Check Kernel Trusted Computing Base (TCB) LOC Budget (Limit <= 1438 LOC)
python3 tools/check_tcb_budget.py

# 4. Check Secret Patterns Across Repository
python3 tools/scan_secrets.py

# 5. Run Sprint 6B Gate R9 Production Dogfood (3/3 PASS)
python3 tools/run_dogfood_r9.py

# 6. Execute Complete Unit Test Suite (488/488 Tests Green)
python3 -m unittest discover -s test -t .
```

---

## 8. Alignment Matrix with `docs/main_v4`

| Specification File | Purpose in Vanguard | Alignment Status |
|---|---|---|
| [`00_vanguard_registry_v040.md`](docs/main_v4/00_vanguard_registry_v040.md) | Document index, precedence rules (`PR-3`), & terminology | **Fully Aligned** |
| [`01_vanguard_engineering_handbook_v040.md`](docs/main_v4/01_vanguard_engineering_handbook_v040.md) | Engineering guidelines & architecture standards | **Fully Aligned** |
| [`02_vanguard_charter_claims_and_non_claims_v040.md`](docs/main_v4/02_vanguard_charter_claims_and_non_claims_v040.md) | Non-claims, separability thesis, & negative result validity | **Fully Aligned** |
| [`03_vanguard_architecture_planes_and_execution_model_v040.md`](docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md) | Six-plane separation & universal turn lifecycle | **Fully Aligned** |
| [`05_vanguard_kernel_capabilities_and_security_v040.md`](docs/main_v4/05_vanguard_kernel_capabilities_and_security_v040.md) | Capability attenuation, budget leases, & kernel security | **Fully Aligned** |
| [`09_vanguard_decision_register_v040.md`](docs/main_v4/09_vanguard_decision_register_v040.md) | Architectural Decision Records (ADRs) | **Fully Aligned** |
| [`13_C_gts_mvp_program_and_engineering_plan.md`](docs/main_v4/13_C_gts_mvp_program_and_engineering_plan.md) | GTS MVP program plan, sprint definitions, & Ch.10 gate questions | **Fully Aligned** |
