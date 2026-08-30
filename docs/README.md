---
id: nav.home
canonical_id: nav.home
class: navigation
authority: descriptive
truth_plane: BOTH
status: living
implementation_status: PARTIAL
owner: documentation-governance
canonical_for:
  - documentation authority explanation
  - audience reading paths
  - canonical navigation
purpose: Orient audiences and route them to canonical owners across architecture, backend, frontend, product, execution, theory, and research documentation.
audience:
  - newcomer
  - operator
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-001
  - E-B-002
  - E-B-021
  - E-B-022
  - E-B-023
  - E-B-024
  - E-B-025
  - E-B-026
  - E-B-042
  - E-B-043
  - E-B-047
normative_authority:
  - VISION.md
  - docs/SPEC.md
  - docs/01_law/
  - decision.index
  - docs/03_execution/sprint_active.md
relationships:
  - arch.system.overview
  - arch.system.boundaries
  - arch.system.data-flow
  - guide.getting-started
  - ref.commands
  - spec.core
  - decision.index
  - execution.active
  - theory.agent-substrate
  - nav.frontend
  - nav.research
reviewer: documentation-specialist
confidence: high
---

# Vanguard Candidate Documentation

## Purpose
This document is the canonical root entry point and navigation directory for the Vanguard candidate documentation tree, orienting human and agentic readers, explaining truth planes, and routing inquiries to their authoritative canonical owners.

## Scope
- Overview of the evidence-backed candidate documentation structure partitioned into global architecture, backend, frontend, product, execution, theory, and research domains.
- Guided reading paths tailored for operators, agent pack developers, core contributors, and system architects.
- Truth plane definitions (`AS_BUILT` versus `TARGET`) and implementation status vocabulary.
- Canonical owner directory routing all system-wide, backend, frontend, product, execution, theory, and research documentation surfaces.

## Non-responsibilities
- Deep subsystem architectural explanations (owned by [`arch.system.overview`](architecture/overview.md), [`arch.system.boundaries`](architecture/boundaries.md), [`arch.system.data-flow`](architecture/data-flow.md), and backend architecture leaves).
- Exact CLI flags, option syntax, and API schemas (owned by [`ref.commands`](backend/reference/commands.md) and reference leaves).
- Normative product requirements and TARGET specifications (owned by [`spec.core`](SPEC.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Root candidate navigation is active and verified across all 25 Block D documentation work packets at analysis subject SHA `9fd444674bf3a97f2673ff36a5f5928ef046c574`.

## TARGET Status
- `PARTIAL` — The approved TARGET surfaces are present. Their requirements, gaps, conflicts, decisions, execution intent, and theory remain explicitly separate from the AS_BUILT pages.

---

## 1. What This Candidate Documentation Describes

This documentation set represents the code-verified **AS_BUILT** state of Vanguard / AETHER reconstructed directly from production packages (`vanguard/packages/`), schemas (`schemas/`), manifests (`packs/`), and executable verification tests (`test/`). Every material implementation claim is tied to concrete code evidence.

TARGET product intent is reconstructed separately from current authority. Start with the compact [TARGET specification](SPEC.md), then use the [decision index](decisions.md), [milestone gates](execution/milestones.md), [active execution view](execution/active.md), or [agent-substrate theory](theory/agent-substrate.md). A TARGET requirement never proves implementation; each divergence is registered in the Block E reconciliation artifacts.

---

## 2. Choose a Path

Depending on your objective, follow one of the recommended reading paths:

```text
┌─────────────────────────────────────────────────────────────┐
│                       CHOOSE YOUR PATH                      │
├─────────────────────────────────────────────────────────────┤
│  1. Newcomer / Operator:                                    │
│     Getting Started -> Commands -> Run & Resume             │
│                                                             │
│  2. Agent / Pack Developer:                                 │
│     Compose an Agent -> Add Pack or Tool -> Manifests       │
│                                                             │
│  3. Substrate & Infrastructure Contributor:                 │
│     System Overview -> Kernel TCB -> Hexagonal Ports        │
│                                                             │
│  4. System Architect / Auditor:                             │
│     Runtime Execution -> Causal State -> Assurance / Eval   │
└─────────────────────────────────────────────────────────────┘
```

### Path 1: Newcomer & Operator Quickstart
1. [Getting Started Guide](backend/guides/getting-started.md): Installation, initialization (`init`), and first task run.
2. [Commands Reference](backend/reference/commands.md): Python `vanguard` and TypeScript `vg` CLI commands.
3. [Run, Inspect & Resume Guide](backend/guides/run-and-resume.md): Monitoring runs, checking events, and cold crash recovery.
4. [Operate Runtime Service Guide](backend/guides/operate-runtime-service.md): Running `vanguard-daemon` and Studio.

### Path 2: Agent Pack & Tool Developer
1. [Compose an Agent Guide](backend/guides/compose-an-agent.md): Building custom agent pack definitions.
2. [Add a Pack or Tool Guide](backend/guides/add-pack-or-tool.md): Declaring tools and writing `IToolkit` handlers.
3. [Manifests & Packs Reference](backend/reference/manifests.md): `mhf.manifest/2` schema and pack file layouts.
4. [Agency Turn Engine Architecture](backend/architecture/agency.md): Context compiler layers and proposal turn loop.

### Path 3: Infrastructure & Adapter Contributor
1. [System Overview](architecture/overview.md): Subsystem boundary map and hexagonal layer rules.
2. [Hexagonal Ports Reference](backend/reference/ports.md): The 5 SPI protocols and port signatures.
3. [Add an Adapter or Provider Guide](backend/guides/add-adapter-or-provider.md): Implementing model or store adapters.
4. [Configuration & Profiles Reference](backend/reference/configuration.md): Execution profiles and environment variables.

### Path 4: Architecture & Trust Auditor
1. [Kernel & Trusted Computing Base](backend/architecture/kernel.md): 13-stage dispatch (S0–S12) and TCB budget.
2. [Runtime Execution Architecture](backend/architecture/runtime-execution.md): `HarnessSession` lifecycle and `RunPlan` identity.
3. [Causal State & Persistence](backend/architecture/causal-state.md): Event log truth model, reducers, and checkpoints.
4. [Assurance & Evaluation Architecture](backend/architecture/assurance-evaluation.md): Trajectory capture and exterior signed verdicts.

---

## 3. Truth Planes & Status Vocabulary

Documentation pages in Vanguard are classified by explicit truth planes and status labels:

### Truth Planes
- **`AS_BUILT`**: Describes the existing, verified implementation in the repository as of analysis subject SHA `9fd444674bf3a97f2673ff36a5f5928ef046c574`. All 25 Block D pages operate strictly on this plane.
- **`TARGET_DEPENDENT`**: Describes aspirational requirements, future specifications, and milestone plans. Deferred to Block E reconciliation.

### Implementation Status Labels
- **`IMPLEMENTED`**: Fully evidenced in production code, schemas, and passing contract tests.
- **`PARTIAL`**: Operational mechanisms with identified integration seams or command asymmetries (e.g. `delegation-topology.md`, `application-interfaces.md`).
- **`EXPERIMENTAL`**: Research or canary components not part of the default execution path.
- **`DEFERRED`**: Content intentionally excluded from Block D pending Block E TARGET reconciliation.

---

## 4. Canonical Owner Directory

Every durable architectural and operational fact has exactly one canonical owner:

### Global Architecture (`candidate-docs/architecture/`)
- [System Overview](architecture/overview.md) (`arch.system.overview`)
- [System Boundaries & Isolation](architecture/boundaries.md) (`arch.system.boundaries`)
- [End-to-End Data Flow](architecture/data-flow.md) (`arch.system.data-flow`)

### Backend Architecture (`candidate-docs/backend/architecture/`)
- [Runtime Execution Architecture](backend/architecture/runtime-execution.md) (`arch.runtime.execution`)
- [Kernel & Trusted Computing Base](backend/architecture/kernel.md) (`arch.trust.kernel`)
- [Agency Turn Engine](backend/architecture/agency.md) (`arch.agency.turns`)
- [Causal State & Persistence](backend/architecture/causal-state.md) (`arch.state.causal`)
- [Composition & Extensibility](backend/architecture/composition-extensibility.md) (`arch.composition.extensibility`)
- [Delegation & Topology](backend/architecture/delegation-topology.md) (`arch.orchestration.delegation`)
- [Memory & Governed Learning](backend/architecture/memory-learning.md) (`arch.memory.learning`)
- [Assurance & Evaluation](backend/architecture/assurance-evaluation.md) (`arch.assurance.evaluation`)
- [Application & Client Interfaces](backend/architecture/application-interfaces.md) (`arch.interfaces.clients`)

### Backend Reference (`candidate-docs/backend/reference/`)
- [Commands Reference](backend/reference/commands.md) (`ref.commands`)
- [Runtime Service Protocol Reference (`vg.4`)](backend/reference/runtime-service.md) (`ref.runtime-service`)
- [Event Substrate & Envelope Reference](backend/reference/events.md) (`ref.events`)
- [JSON Schemas & Wire Contracts](backend/reference/schemas.md) (`ref.schemas`)
- [Configuration & Profiles Reference](backend/reference/configuration.md) (`ref.configuration`)
- [Hexagonal Ports & SPI Reference](backend/reference/ports.md) (`ref.ports`)
- [Manifests, Packs & Plugins](backend/reference/manifests.md) (`ref.manifests`)
- [Artifact Storage & Memory Reference](backend/reference/artifacts-memory.md) (`ref.artifacts`)

### Backend Guides (`candidate-docs/backend/guides/`)
- [Getting Started Guide](backend/guides/getting-started.md) (`guide.getting-started`)
- [Run, Inspect & Resume Guide](backend/guides/run-and-resume.md) (`guide.run-resume`)
- [Compose an Agent Guide](backend/guides/compose-an-agent.md) (`guide.compose-agent`)
- [Add a Pack or Tool Guide](backend/guides/add-pack-or-tool.md) (`guide.add-pack-tool`)
- [Add an Adapter or Provider Guide](backend/guides/add-adapter-or-provider.md) (`guide.add-adapter-provider`)
- [Operate Runtime Service Guide](backend/guides/operate-runtime-service.md) (`guide.operate-service`)

### Frontend Documentation (`candidate-docs/frontend/`)
- [Frontend Documentation Directory](frontend/README.md) (`nav.frontend` — Intentionally Deferred)

### Product Requirements (`candidate-docs/product/`)
- [Frontend PRD Placement Manifest](product/frontend/FRONTEND_PRD_PLACEMENT_MANIFEST.md) (`frontend-prd-placement-manifest`)
- [Frontend Platform PRD](product/frontend/PRD_FRONTEND_PLATFORM.md) (`product.frontend.platform`)
- [AETHER CLI PRD](product/frontend/PRD_AETHER_CLI.md) (`product.frontend.cli`)
- [AETHER TUI PRD](product/frontend/PRD_AETHER_TUI.md) (`product.frontend.tui`)
- [AETHER Desktop PRD](product/frontend/PRD_AETHER_DESKTOP.md) (`product.frontend.desktop`)
- [AETHER Lab PRD](product/frontend/PRD_AETHER_LAB.md) (`product.frontend.lab`)

### Execution (`candidate-docs/execution/`)
- [Active Execution View](execution/active.md) (`execution.active`)
- [Milestone Gates](execution/milestones.md) (`execution.milestones`)

### Theory & Research (`candidate-docs/theory/`, `candidate-docs/research/`)
- [Agent Substrate Theory](theory/agent-substrate.md) (`theory.agent-substrate`)
