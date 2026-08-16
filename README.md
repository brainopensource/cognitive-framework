# Vanguard General Task Solver (GTS)

> **A SOTA verifiable, modular meta-harness runtime that accumulates machine competence under an exterior judge it cannot game.**

[![Vanguard Core Integrity](https://img.shields.io/badge/Vanguard-v0.4.1--beta-blue.svg)](docs/agile/sprint6B/RELEASE_CANDIDATE_RECEIPT.json)
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

## 2. Orders of Abstraction (Hierarchical Taxonomy)

Vanguard is organized across **Six Orders of Abstraction**, building from immutable mathematical primitives up to multi-agent measurement swarms:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ ORDER 5: ORGANISMS & SWARMS (Measurement Laboratory, Distillation & Multi-Agent)       │
│ • Paired Laboratory Bench (`lab harness bench`), McNemar A/A Control (`vg-shell-only`) │
│ • Out-of-Process Signed Evaluator (UID 10002), TableWorld Non-Coding Witness            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ ORDER 4: CELLS & PACKS (Pure-Data Manifest Configurations)                              │
│ • Manifest Packs: `vg-code-default`, `vg-code-claude-shaped`, `vg-code-opencode-shaped` │
│ • Workspace Instruction Discovery: Dynamic `AGENTS.md` / `CLAUDE.md` Injection           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ ORDER 3: POLYMERS & PROTEINS (Cognitive Engine & Recursion)                             │
│ • Context Compiler L1–L5 (Byte-Stable System Prompt & Schemas KV-Cache Optimization)    │
│ • `ProposalTranslator` & `EpisodeEngine` Depth-1 Single-Observation Recursion Loop      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ ORDER 2: MOLECULES (Control Kernel & Sandbox Effector)                                  │
│ • Attenuation Kernel (`kernel/dispatch.py`), Descriptor Leasing & USD Micro-Budgeting    │
│ • Rootless Bubblewrap Worker Containment (`adapters/sandbox/rootless.py`)               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ ORDER 1: ATOMS (Ports & Capabilities)                                                   │
│ • Hexagonal Abstract Ports (`ModelPort`, `LedgerPort`, `EvaluatorPort`)                 │
│ • Single-Verb Capabilities (`fs.read`, `fs.search`, `fs.write`, `patch.apply`, `proc.exec`) │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ ORDER 0: SUB-ATOMIC PRIMITIVES (Wire Contracts & Data Values)                           │
│ • Canonical Value Objects, `EffectIntent`, `Receipt`, `CorrectionRecord`                │
│ • SHA-256 Descriptors, Ed25519 Asymmetric Signatures, JsonSchema Verification Profiles  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Layer Breakdown

* **Order 0 — Sub-Atomic Primitives (`domain/wire/contracts.py`):** Pure values, canonical JSON serialization, SHA-256 descriptor digests, and Ed25519 asymmetric signatures. Contains zero IO logic.
* **Order 1 — Atoms / Ports & Verbs (`ports/`):** Hexagonal interfaces for models, ledgers, evaluators, and sandboxes. Single-action effectors (`fs.read`, `fs.search`, `fs.write`, `patch.apply`, `proc.exec`).
* **Order 2 — Molecules / Kernel & Containment (`kernel/`, `adapters/sandbox/`):** Capability attenuation, USD micro-budget leases, and rootless Linux namespace isolation via Bubblewrap (`bwrap`).
* **Order 3 — Polymers / Cognitive Engine (`agency/`):** Prefix-stable L1–L5 Context Compiler, manifest-driven `ProposalTranslator`, and the depth-1 `EpisodeEngine` recursion loop.
* **Order 4 — Cells / Pure-Data Harness Manifests (`agency/manifests/`):** Competitor-shaped harnesses (`vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`) declared **strictly as pure JSON data**, without kernel diffs. Includes workspace instruction discovery (`AGENTS.md`, `CLAUDE.md`).
* **Order 5 — Organisms & Swarms / Measurement & Evaluators (`lab/`, `adapters/evaluators/`):** Paired measurement laboratory (`lab harness bench`), control arm (`vg-shell-only`), out-of-process signed evaluator daemon (UID `10002`), TableWorld structured-data witness, and offline competence distillation (`O-01`).

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

```text
Aether-D-System/
├── .github/workflows/ci.yml         # Boundary, TCB, secret scan, & test CI gates
├── benchmarkings/                   # Empirical benchmark suites & live zero-hint runners
├── containers/                      # OCI build files & manifest.json digests
│   ├── worker.Dockerfile            # Bubblewrap worker container (UID 10001)
│   ├── evaluator.Dockerfile         # Signed evaluator daemon container (UID 10002)
│   └── manifest.json                # Immutable release build SHA-256 digests
├── docs/
│   ├── main_v4/                     # Normative Vanguard v4 Specification Corpus (VG-00..12, GTS-13C)
│   ├── reviews/todo/                # S7–S10 Master Architectural Roadmap
│   └── agile/sprint6B/              # Gate R0–R10 release evidence & dogfood log
├── tools/                           # Boundary check, TCB budget, secret scan, & dogfood tools
└── vanguard/packages/               # Physical package boundaries (enforced in CI)
    ├── domain/                      # Pure values, wire contracts, state reducers (Order 0)
    ├── ports/                       # Abstract interfaces & in-memory fakes (Order 1)
    ├── kernel/                      # Attenuation kernel, budget leases, dispatch (Order 2)
    ├── agency/                      # Context compiler, proposal translator, episode engine (Order 3)
    │   └── manifests/               # Data-only harness configurations (Order 4)
    ├── runtime/                     # Composition root & daemon lifecycle
    │   └── governance/              # Ed25519 approval flow & release signoff
    └── adapters/                    # Concrete adapters (Model, Sandbox, Evaluator) (Order 1/2/5)
```

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

| Escalation Tier | Complexity & Scope | Target Models | Platform / Provider | Benchmark Validation |
|---|---|---|---|---|
| **Tier 1** | Single-file typos, syntax fixes | `qwen2.5:1.5b` → `llama3.2:3b` | Local Ollama ($0) | Single-file calculator repair (< 1s) |
| **Tier 2** | Multi-file dependency & import repair | `deepseek-r1:14b` → `qwen3.6:27b` | Local Ollama ($0) | Import-cycle repair, test reaction |
| **Tier 3** | Subdirectory refactoring & search | `openrouter/free` → `meta-llama/llama-3.3-70b-instruct` | Cloud OpenRouter | Thread-safe Token Bucket Rate Limiter |
| **Tier 4** | Subsystem state machines & concurrency | `deepseek/deepseek-chat` → `gpt-4o` → `claude-3.5-sonnet` | Cloud OpenRouter / OpenAI | DAG Dependency Resolver with Cycle Detection |
| **Tier 5** | Frontier autonomous refactoring | `claude-3.5-sonnet` → `deepseek-r1` → `gpt-4.5` | Cloud OpenRouter / Anthropic | Incremental Stratified Datalog Fixed-Point Engine |

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
