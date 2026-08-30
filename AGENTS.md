---
id: repo-agents-contract
class: standard
authority: execution
canonical_for:
  - agent-contributor-contract
  - repository-anti-sprawl-rules
status: living
owner: repository-governance
version: "0.9.0b1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Repository Guidelines

**Start here:** [`README.md`](README.md) is the primary navigation map. This file specifies operational rules and procedures for AI agents and human contributors.

---

## 1. Project Structure & Documentation Architecture

Vanguard / AETHER is a Python-first recursive-agency substrate (`requires-python >= 3.10`, tested on Python 3.12 in CI) with a TypeScript/React/Ink interactive CLI (`vg`).

### Documentation Hierarchy
All documentation is partitioned into distinct authority tiers:

```text
VISION.md / AGENTS.md / docs/SPEC.md
    Vision, Operational Rules, Compact Normative Law

docs/decisions.md
    Foundational Decision Record Index

docs/architecture/ & docs/backend/ & docs/frontend/ & docs/product/
    System & Component Architecture, Reference, Product PRDs

docs/execution/
    Active Execution State (active.md) & Milestone Ladder

docs/theory/ | docs/research/ | docs/reports/
    Durable Theory | Non-Canonical Research | Technical Strategy & Audit Reports
```

- **Vision & Operational Rules**: [`VISION.md`](VISION.md), [`AGENTS.md`](AGENTS.md).
- **The Law & Decisions**: [`docs/SPEC.md`](docs/SPEC.md) + [`docs/decisions.md`](docs/decisions.md).
- **The Execution**: [`docs/execution/active.md`](docs/execution/active.md).

### Hexagonal Production Lattice (`vanguard/packages/`)
The canonical production truth lives in `vanguard/packages/`, strictly enforcing the hexagonal boundary flow:
```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a client slot of runtime)
```

| Subsystem | Location | Responsibilities & Contents |
|---|---|---|
| **`domain/`** | `vanguard/packages/domain/` | Pure value objects, wire contracts, JCS canonicalization, ledger reducers, evidence models, selector algebra (`resource_selector.py`). Stdlib Python only. |
| **`ports/`** | `vanguard/packages/ports/` | Hexagonal port protocols (`kernel`, `model`, `sandbox`, `evaluator`, `event_store`, `blob_store`, `environment`, `determinism`, `index`, and 5 SPI protocols in `spi.py`). |
| **`kernel/`** | `vanguard/packages/kernel/` | Trusted Computing Base (TCB limit `<=1438` LOC; currently 1365 LOC). 13-stage dispatch pipeline (S0–S12), monotonic capability attenuation, typed budget algebra, capability grants, fail-closed policy, execution provenance DAG. Domain-blind. |
| **`agency/`** | `vanguard/packages/agency/` | Recursive turn engine. `EpisodeEngine` turn loop, attenuated child agent `spawn()`, context compiler, structured compaction. |
| **`runtime/`** | `vanguard/packages/runtime/` | Composition and lifecycle (`compose.py`, `session.py`, `wiring.py`, `ledger_emitter.py`, `evaluator_gateway.py`), governance & Ed25519 approvals (`governance/`), SQLite WAL event store. |
| **`adapters/`** | `vanguard/packages/adapters/` | Concrete implementations: Models (OpenRouter, Ollama, Cassette, Fake), Evaluator daemon & RPC client (UID 10002), Rootless Sandbox (bwrap UID 10001), SQLite store. **Must not** import `kernel` or `agency`. |
| **`apps/`** | `vanguard/packages/apps/` | Reserved boundary-lattice slot. |

---

## 2. Development & Testing Commands

### Environment Setup
```bash
# Python dev dependencies (repo root)
uv sync

# TypeScript dev dependencies (repo root)
npm ci
```

### Python Test Commands
```bash
# Production kernel tests (pure TCB core)
python3 -m unittest discover -s test/kernel -t .

# Hexagonal contract tests
python3 -m unittest discover -s test/contracts -t .

# Agency & turn execution tests
python3 -m unittest discover -s test/agency -t .

# Domain pack tests (code-default)
python3 -m unittest discover -s test/packs -t .

# Single focused module / single test case
python3 -m unittest test.kernel.test_dispatch -v
python3 -m unittest test.kernel.test_dispatch.TestDispatchPipeline.test_s0_observe_produces_receipt -v

# Full suite
python3 -m unittest discover -s test -t .
```

### Architecture, TCB, & Security Linters
```bash
# Enforce hexagonal boundaries
python3 tools/linters/check_boundaries.py

# Verify Trusted Computing Base budget (threshold <= 1438 LOC)
python3 tools/linters/check_tcb_budget.py

# Scan workspace for leaked secrets and API keys
python3 tools/linters/scan_secrets.py

# Invariant checks
python3 tools/linters/check_domain_blindness.py   # Invariant I-7
python3 tools/linters/check_isolation_policy.py   # Invariant I-6
python3 tools/linters/check_duplication.py --enforce # Duplication detector
python3 tools/linters/check_markdown_links.py     # Relative link verification
python3 tools/linters/check_stale_paths.py        # Stale documentation path check
```

---

## 3. Wave Execution & Concept Staging

Execution sequence:
1. **Wave 0 (COMPLETE)**: CI Truth & Named Falsifiers (`vanguard/packages` as sole subject of record).
2. **Wave 1 (COMPLETE - GREEN)**: Fail-Closed Trust Spine (bound signed verdicts, single emitter, typed budgets, `mhf.trajectory/1`).
3. **Wave 2 (COMPLETE - GREEN)**: RF-23 truthful trajectories and RF-25 fresh-process SQLite-WAL continuation close M-2.
4. **M-3C / W-3D (COMPLETE)**: canonical composition, activation, durability, evidence, profiles, and product bootstrap are closed.
5. **M-4–M-8**: current state, ownership, and authorization live only in the active execution board; mechanism presence never implies acceptance.
6. **M-9/M-10 (NON-AUTHORIZING)**: compatibility seams only; no implementation before M-8 acceptance.

Current status belongs only in [`docs/execution/active.md`](docs/execution/active.md).
Do not infer authorization from archived proposals, reviews, research, or completed sprint records.

---

## 4. Coding Style & Architectural Conventions

- **Python**: Python 3.10+ syntax with 4-space indentation, strict type hints, focused single-responsibility modules, and `snake_case` functions/variables with `PascalCase` classes.
- **Dependency Hierarchy**: Lower layers must never import higher layers (`domain ← ports ← kernel ← agency ← runtime → adapters`). Adapters implement port interfaces and must never import kernel or agency.
- **TCB Budget**: Code added to `vanguard/packages/kernel/` must not exceed the line-of-code budget ($\le 1438$ LOC) enforced by `tools/check_tcb_budget.py`.
- **TypeScript**: TypeScript 5.x with strict type checking, standard formatting matching existing files, and zero runtime dependencies outside React/Ink and Node stdlib.
- **Hermetic Testing**: All unit and contract tests must execute deterministically without network access or live API keys. Use fakes, test doubles, or cassette recordings.

---

## 5. Agent Implementation Rules & Required Validation Behavior

AI Agents working in this repository MUST comply with the following operational constraints:
- **Scope Contained**: Modify code strictly within the assigned task scope.
- **Tests Synchronized**: Update or add automated tests whenever runtime behavior or contracts change.
- **Docs Synchronized**: Update canonical documentation when durable architecture, contract, API, workflow, configuration, or user behavior changes.
- **No Unsolicited Docs Sprawl**: Do not edit or create documentation files when code behavior does not change. Never create scratch Markdown under `docs/`.
- **No Custom ADRs / Reports**: Never create new ADRs for ordinary architecture updates or post-hoc Markdown implementation reports in the repository tree.
- **No Manual Edit of Generated Artifacts**: Never manually edit rebuildable machine outputs under `.generated/knowledge/` or `.generated/diagrams/`.
- **Validation Commands**:
  - Run `just check` during incremental development loops.
  - Run `just verify` before claiming task, PR, or sprint completion.
- **Honest Status Reporting**: Agents MUST report commands actually executed and NEVER claim `PASS` for an unexecuted command. Never suppress failing assertions with `|| true`. Fix task-introduced failures before declaring completion.

---

## 6. Documentation Routing & Ownership Model

When updating documentation, route information to its semantic owner:
- **`docs/SPEC.md`**: Normative RFC-2119 specifications and core target requirements.
- **`docs/architecture/`**: Global system architecture, dispatch pipeline, isolation, and system workflows.
- **`docs/backend/`**: Microkernel, event engine, delegation, memory, and reference schemas/ports/APIs.
- **`docs/frontend/`**: Frontend client architecture, state management, and design tokens.
- **`docs/product/`**: Product PRDs, requirements, and user behavior.
- **`docs/execution/active.md`**: Current sprint status, task ladder, and active authorization.
- **`docs/decisions.md`**: Immutable Architecture Decision Records (ADRs).
- **`docs/theory/` | `docs/research/` | `docs/reports/`**: Non-canonical conceptual theory, research, and audit reports (`authority: non-canonical`).

---

## 7. Strict Documentation Anti-Sprawl Invariant

> [!CAUTION]
> **MANDATORY INSTRUCTION FOR ALL AI AGENTS & CONTRIBUTORS:**  
> AI Agents **MUST NOT** create new Markdown files under `docs/`, `docs/plans/`, or anywhere across the workspace to leave scratch notes, plans, reviews, or summaries.  
> 
> All documentation updates must strictly edit existing canonical files in the documentation hierarchy:
> 1. **Modifying Normative Law** $\to$ Edit [`docs/SPEC.md`](docs/SPEC.md).
> 2. **Recording Architectural Decisions** $\to$ Edit [`docs/decisions.md`](docs/decisions.md).
> 3. **Updating Tasks, Sprints, or Execution Progress** $\to$ Edit [`docs/execution/active.md`](docs/execution/active.md).
> 
> Any temporary thinking, scratch notes, or intermediate outputs must be kept in model scratchpads or ephemeral artifact directories—never committed as files in the repository tree.
