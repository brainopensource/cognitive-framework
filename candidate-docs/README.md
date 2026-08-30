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
purpose: Orient audiences and route them to canonical owners across architecture, reference, and guide documentation.
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
  - guide.getting-started
  - ref.commands
  - spec.core
  - decision.index
  - execution.active
  - theory.agent-substrate
reviewer: documentation-specialist
confidence: high
---

# Vanguard Candidate Documentation

## Purpose
This document is the canonical root entry point and navigation directory for the Vanguard candidate documentation tree, orienting human and agentic readers, explaining truth planes, and routing inquiries to their authoritative canonical owners.

## Scope
- Overview of the evidence-backed candidate documentation structure.
- Guided reading paths tailored for operators, agent pack developers, core contributors, and system architects.
- Truth plane definitions (`AS_BUILT` versus `TARGET`) and implementation status vocabulary.
- Canonical owner directory routing all 25 AS_BUILT pages and five TARGET-dependent surfaces completed in Block E.

## Non-responsibilities
- Deep subsystem architectural explanations (owned by [`arch.system.overview`](architecture/overview.md) and subsystem architecture leaves).
- Exact CLI flags, option syntax, and API schemas (owned by [`ref.commands`](reference/commands.md) and reference leaves).
- Normative product requirements and TARGET specifications (owned by [`spec.core`](SPEC.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Root candidate navigation is active and verified across all 25 Block D documentation work packets at analysis subject SHA `9fd444674bf3a97f2673ff36a5f5928ef046c574`.

## TARGET Status
- `PARTIAL` — The five approved TARGET surfaces are present. Their requirements, gaps, conflicts, decisions, execution intent, and theory remain explicitly separate from the AS_BUILT pages.

---

## 1. What This Candidate Documentation Describes

This documentation set represents the code-verified **AS_BUILT** state of Vanguard / AETHER reconstructed directly from production packages (`vanguard/packages/`), schemas (`schemas/`), manifests (`packs/`), and executable verification tests (`test/`). Every material implementation claim is tied to concrete code evidence.

TARGET product intent is reconstructed separately from current authority. Start with the compact [TARGET specification](SPEC.md), then use the [decision index](decisions/README.md), [milestone gates](execution/milestones.md), [active execution view](execution/active.md), or [agent-substrate theory](theory/agent-substrate.md). A TARGET requirement never proves implementation; each divergence is registered in the Block E reconciliation artifacts.

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
1. [Getting Started Guide](guides/getting-started.md): Installation, initialization (`init`), and first task run.
2. [Commands Reference](reference/commands.md): Python `vanguard` and TypeScript `vg` CLI commands.
3. [Run, Inspect & Resume Guide](guides/run-and-resume.md): Monitoring runs, checking events, and cold crash recovery.
4. [Operate Runtime Service Guide](guides/operate-runtime-service.md): Running `vanguard-daemon` and Studio.

### Path 2: Agent Pack & Tool Developer
1. [Compose an Agent Guide](guides/compose-an-agent.md): Building custom agent pack definitions.
2. [Add a Pack or Tool Guide](guides/add-pack-or-tool.md): Declaring tools and writing `IToolkit` handlers.
3. [Manifests & Packs Reference](reference/manifests.md): `mhf.manifest/2` schema and pack file layouts.
4. [Agency Turn Engine Architecture](architecture/agency.md): Context compiler layers and proposal turn loop.

### Path 3: Infrastructure & Adapter Contributor
1. [System Overview](architecture/overview.md): Subsystem boundary map and hexagonal layer rules.
2. [Hexagonal Ports Reference](reference/ports.md): The 5 SPI protocols and port signatures.
3. [Add an Adapter or Provider Guide](guides/add-adapter-or-provider.md): Implementing model or store adapters.
4. [Configuration & Profiles Reference](reference/configuration.md): Execution profiles and environment variables.

### Path 4: Architecture & Trust Auditor
1. [Kernel & Trusted Computing Base](architecture/kernel.md): 13-stage dispatch (S0–S12) and TCB budget.
2. [Runtime Execution Architecture](architecture/runtime-execution.md): `HarnessSession` lifecycle and `RunPlan` identity.
3. [Causal State & Persistence](architecture/causal-state.md): Event log truth model, reducers, and checkpoints.
4. [Assurance & Evaluation Architecture](architecture/assurance-evaluation.md): Trajectory capture and exterior signed verdicts.

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

### Architecture (`candidate-docs/architecture/`)
- [System Overview](architecture/overview.md) (`arch.system.overview`)
- [Runtime Execution Architecture](architecture/runtime-execution.md) (`arch.runtime.execution`)
- [Kernel & Trusted Computing Base](architecture/kernel.md) (`arch.trust.kernel`)
- [Agency Turn Engine](architecture/agency.md) (`arch.agency.turns`)
- [Causal State & Persistence](architecture/causal-state.md) (`arch.state.causal`)
- [Composition & Extensibility](architecture/composition-extensibility.md) (`arch.composition.extensibility`)
- [Delegation & Topology](architecture/delegation-topology.md) (`arch.orchestration.delegation`)
- [Memory & Governed Learning](architecture/memory-learning.md) (`arch.memory.learning`)
- [Assurance & Evaluation](architecture/assurance-evaluation.md) (`arch.assurance.evaluation`)
- [Application & Client Interfaces](architecture/application-interfaces.md) (`arch.interfaces.clients`)

### Reference (`candidate-docs/reference/`)
- [Commands Reference](reference/commands.md) (`ref.commands`)
- [Runtime Service Protocol Reference (`vg.4`)](reference/runtime-service.md) (`ref.runtime-service`)
- [Event Substrate & Envelope Reference](reference/events.md) (`ref.events`)
- [JSON Schemas & Wire Contracts](reference/schemas.md) (`ref.schemas`)
- [Configuration & Profiles Reference](reference/configuration.md) (`ref.configuration`)
- [Hexagonal Ports & SPI Reference](reference/ports.md) (`ref.ports`)
- [Manifests, Packs & Plugins](reference/manifests.md) (`ref.manifests`)
- [Artifact Storage & Memory Reference](reference/artifacts-memory.md) (`ref.artifacts`)

### Guides (`candidate-docs/guides/`)
- [Getting Started Guide](guides/getting-started.md) (`guide.getting-started`)
- [Run, Inspect & Resume Guide](guides/run-and-resume.md) (`guide.run-resume`)
- [Compose an Agent Guide](guides/compose-an-agent.md) (`guide.compose-agent`)
- [Add a Pack or Tool Guide](guides/add-pack-or-tool.md) (`guide.add-pack-tool`)
- [Add an Adapter or Provider Guide](guides/add-adapter-or-provider.md) (`guide.add-adapter-provider`)
- [Operate Runtime Service Guide](guides/operate-runtime-service.md) (`guide.operate-service`)
