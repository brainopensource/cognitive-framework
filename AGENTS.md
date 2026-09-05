---
id: repo-agents-contract
class: standard
authority: execution
canonical_for:
  - agent-contributor-contract
  - repository-anti-sprawl-rules
status: living
owner: repository-governance
version: "0.9.3"
last_verified: 2026-09-03
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
VISION.md / AGENTS.md / docs/execution/spec.md
    Vision, Operational Rules, Compact Normative Law & Delta Spec

docs/architecture/ & docs/backend/ & docs/frontend/ & docs/product/
    System & Component Architecture (including DEC-01–DEC-11), Reference, Product PRDs

docs/execution/
    Five-file operational runway: milestones.md, spec.md, technical.md, backlog.md, tasks.md

docs/theory/ | docs/research/ | docs/reports/
    Durable Theory | Non-Canonical Research | Technical Strategy & Audit Reports
```

- **Vision & Operational Rules**: [`VISION.md`](VISION.md), [`AGENTS.md`](AGENTS.md).
- **The Law & Invariants**: [`docs/execution/spec.md`](docs/execution/spec.md).
- **The Execution Runway**: [`docs/execution/tasks.md`](docs/execution/tasks.md), [`docs/execution/spec.md`](docs/execution/spec.md), [`docs/execution/technical.md`](docs/execution/technical.md), [`docs/execution/milestones.md`](docs/execution/milestones.md), [`docs/execution/backlog.md`](docs/execution/backlog.md).

### Repository-Intelligence Navigation Protocol

Humans and AI agents MUST use repository-intelligence artifacts as a token-bounded routing layer,
not as architectural authority. For targeted work, navigate in this order:

```text
dev_context_logs/context_summary.{md,json}       # Tier 1: fast state/evidence bootstrap
    -> .generated/knowledge/code-map.jsonl       # subsystem and canonical-owner routing
    -> .generated/knowledge/{symbols,ownership}.jsonl
    -> canonical documentation                   # applicable law, decisions, architecture
    -> targeted source and tests                 # implementation and executable falsifiers
    -> dev_context_logs/ Tier 2, SQLite, evidence, benchmarks
```

Load only the entries, files, and sections needed for the assigned task. Do not place complete
indexes, broad source trees, or all Tier-2 logs into the context window when a targeted query is
sufficient.

#### Executable Retrieval Recipe (Mandatory Starting Sequence)

For any implementation, review, or bugfix task, agents MUST begin with this token-bounded
sequence before broad exploration. Each step answers a specific development question:

```bash
# Step 0 — Bootstrap state: which gates must stay green? what is already failing?
cat dev_context_logs/context_summary.md          # refresh first with: make dev-context

# Step 1 — Primary SOTA Fast Path: One-shot task bundle (symbols, callers, falsifiers, docs)
#          Replaces multiple manual searches with a single, auto-delta synchronized plan.
uv run lda plan "<task keywords or intent>" --budget 8000

# Step 1b — Concept / intent lookup (when symbol name is unknown):
uv run lda resolve "<natural language intent or concept>"

# Step 2 — Post-edit sync (sub-50ms incremental re-index with 0 MB background daemon):
uv run lda index --delta

# Step 3 — Deterministic Fallback (when LDA index is cold, degraded, or unbuilt):
python3 tools/docs_rag_v0.py "<task keywords>" --budget 8000
python3 tools/docs_rag_v0.py --file vanguard/packages/kernel/budget.py
grep "<Symbol>" .generated/knowledge/symbols.jsonl
```

- Step 0 answers: *which gates, headrooms, and failure signatures are already known?*
- Step 1 answers: *which subsystem owns the task, what are the exact symbol ranges, who calls them (blast radius), which canonical docs must stay synchronized, and which executable test falsifiers verify the change?*
- Step 1b answers: *which classes/functions implement a given semantic behavior or concept?*
- Step 2 answers: *how do I refresh AST ranges and relation facts instantly after editing a file without a full rebuild?*
- Step 3 answers: *how do I deterministically route documentation debt if the SQLite graph is unavailable?*

#### Core LDA Engineering Patterns (Anti-Blind Exploration)

Instead of dumping multi-thousand line files into context or running unguided greps, developers and agents MUST use these targeted patterns:

1. **Explain Code & Explore Concepts** (e.g. *"how does explanation or artifact audit work?"*):
   ```bash
   uv run lda resolve "explanation agent"           # Finds exact class/function (e.g. explain.py::Explanation)
   uv run lda context "explain artifact" --budget 3000 # Compiles token-bounded AST context
   ```
2. **Find Modules & Architecture Blast Radius**:
   ```bash
   uv run lda repomap --focus vanguard/packages/runtime/ --budget 2000 # Dense structural skeleton
   uv run lda callers vanguard.packages.runtime.explain.explain_artifact # Upstream callers before touching
   ```
3. **Debug Bugs & Run Instant Falsifiers**:
   ```bash
   uv run lda plan "fix admission gate verification failure" # Bundles symbol + callers + exact test commands
   # Output gives copy-paste falsifiers: python3 -m unittest test.packs.code_default.test_context_policy -v
   ```
4. **Create Features & Verify Drift**:
   ```bash
   uv run lda plan "<new feature description>"      # Identify required ports, protocols, and contracts
   # [Implement surgical edits]
   uv run lda index --delta                         # Sub-50ms AST synchronization
   uv run lda drift --json                          # Verify 0 stale paths, 0 orphan contracts
   ```

**Health check before trust**: `.generated/knowledge/report.json` must report
`"status": "VALIDATED"` with non-zero row counts. LDA users must additionally confirm
`uv run lda doctor --json` reports `"index_healthy": true`. Operational workflows, MCP tools,
and the token-efficient Golden Order are defined in [`.agents/skills/lda-navigator/SKILL.md`](.agents/skills/lda-navigator/SKILL.md).
Local model inference and anti-hallucination protocols are defined in [`.agents/skills/llama-cpp/SKILL.md`](.agents/skills/llama-cpp/SKILL.md).
Otherwise, report the degraded navigation mode and fall back deterministically to `rg --files`,
targeted `rg`, canonical documents, source, and tests. A worked example of the full sequence is in
[`docs/README.md`](docs/README.md) (§ Worked Example).

The authority rule is:

```text
indexes route; canonical documents constrain; source implements; tests falsify;
ledger and benchmark artifacts demonstrate observed behavior
```

Before relying on `.lda/index.db*`, `.generated/knowledge/`, or `dev_context_logs/`, agents MUST
check, when the metadata is available, that:

- the recorded source revision or digest matches the inspected repository subject;
- required entity counts are non-zero and expected tables/files are present;
- referenced paths and primary symbols resolve in the current tree;
- generator/schema versions are supported and the artifact is not marked stale or invalid.

An index that opens successfully but is empty, stale, or contains unresolved paths is not healthy
for navigation. When freshness or usability cannot be established, report that limitation and fall
back deterministically to `rg --files`, targeted `rg`, canonical documents, source, and tests.
Generated indexes, LDA databases, summaries, diagrams, and historical logs are reconstructible
projections: they MUST NOT override higher-authority documentation, current source, tests, Git state,
or durable runtime evidence, and MUST NOT be edited manually.

### Hexagonal Production Lattice (`vanguard/packages/`)
The canonical production truth lives in `vanguard/packages/`, strictly enforcing the hexagonal boundary flow:
```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a client slot of runtime)
```

| Subsystem | Location | Responsibilities & Contents |
|---|---|---|
| **`domain/`** | `vanguard/packages/domain/` | Pure value objects, wire contracts, RFC 8785 JCS canonicalization, ledger reducers, evidence models, selector algebra (`resource_selector.py`), task state models. Pure Python stdlib only (zero I/O, zero network, zero dependencies). |
| **`ports/`** | `vanguard/packages/ports/` | Hexagonal port typing protocols (`KernelPort`, `ModelPort`, `SandboxPort`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `EnvironmentPort`, `DeterminismPort`, `IndexPort`, and 5 SPI protocols in `spi.py`). |
| **`kernel/`** | `vanguard/packages/kernel/` | Trusted Computing Base (TCB limit `<=1438` LOC; currently 1386 LOC). 13-stage dispatch pipeline (S0–S12), monotonic capability attenuation, typed budget algebra, descriptor-bound capability grants, fail-closed policy, execution provenance DAG. Strictly domain-blind (Invariant I-7). |
| **`agency/`** | `vanguard/packages/agency/` | Recursive turn loop engine (`EpisodeEngine`), attenuated child subagent `spawn()`, structured context compactor, admission gates, and prompt composers. |
| **`runtime/`** | `vanguard/packages/runtime/` | System composition and lifecycle (`compose.py`, `session.py`, `wiring.py`), single-writer `LedgerEmitter`, Ed25519 cryptographic approvals (`governance/`), SQLite WAL event store. |
| **`adapters/`** | `vanguard/packages/adapters/` | Concrete implementations: Models (OpenRouter, llama.cpp / llama-server, Cassette, Fake), Evaluator daemon & RPC client (UID 10002), Rootless Bubblewrap Sandbox (`bwrap` UID 10001), SQLite WAL event store. **Must not** import `kernel` or `agency`. |
| **`apps/`** | `vanguard/packages/apps/` | Thin application entrypoints (e.g., `apps/coding_max/facade.py` exposing `CodingMaxFacade` / `CodingMax`). Coordinates CLI/API requests into `ApplicationService` compositions. |
| **`clients/`** | `vanguard/clients/` | Client workspaces: TypeScript/React/Ink CLI (`vg`), Desktop UI, TUI, and Studio interfaces. |

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

Current status belongs only in the execution runway: [`docs/execution/tasks.md`](docs/execution/tasks.md) (flat work tree), [`docs/execution/milestones.md`](docs/execution/milestones.md) (TARGET gates), [`docs/execution/spec.md`](docs/execution/spec.md) (typed deltas), [`docs/execution/technical.md`](docs/execution/technical.md) (handbook), [`docs/execution/backlog.md`](docs/execution/backlog.md) (packages). Present-tense HEAD architecture lives in `docs/architecture/`, `docs/backend/`, and `docs/SPEC.md`.
Do not infer authorization from archived proposals, reviews, research, completed sprint records, or unused `.draft/` triad files.

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
- **Knowledge-Base Synchronized**: Touching code under `vanguard/packages/<subsystem>/` requires consulting `.generated/knowledge/code-map.jsonl` for that path (or `python3 tools/docs_rag_v0.py --file <path>`), updating the mapped canonical-owner documentation, and regenerating `just docs-knowledge` so the index of record stays truthful.
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
- **`docs/execution/`**: Exactly five authoritative operational runway documents:
  - `milestones.md`: Stable TARGET outcomes and release predicates (M-0 to M-10 plus MS-* overlay). No sprint calendar.
  - `backlog.md`: Stable capability package inventory (SUB-*, MEM-*, CMX-*, OCT-*, T-* aliases). No sprint queue.
  - `spec.md`: Feature delta contract (typed schemas, invariants, error matrix).
  - `technical.md`: Self-explaining engineering handbook for remaining work (FACT vs `[PROPOSAL]`).
  - `tasks.md`: Flat tasks and subtasks by context. `requires:` edges only; no waves or WIP calendar.
- **`docs/theory/` | `docs/research/` | `docs/reports/`**: Non-canonical conceptual theory, research, and audit reports (`authority: non-canonical`).

---

## 7. Strict Documentation Anti-Sprawl Invariant

> [!CAUTION]
> **MANDATORY INSTRUCTION FOR ALL AI AGENTS & CONTRIBUTORS:**  
> AI Agents **MUST NOT** create new Markdown files under `docs/`, `docs/plans/`, or anywhere across the workspace to leave scratch notes, plans, reviews, or summaries.  
> 
> All documentation updates must strictly edit existing canonical files in the documentation hierarchy:
> 1. **Modifying Normative Law & System Spec** $\to$ Edit [`docs/execution/spec.md`](docs/execution/spec.md).
> 2. **Recording Architectural Rationale & Trade-offs** $\to$ Edit corresponding subsystem architecture docs in [`docs/backend/architecture/`](docs/backend/architecture/) or [`docs/architecture/`](docs/architecture/).
> 3. **Updating Tasks or Execution Progress** $\to$ Edit [`docs/execution/tasks.md`](docs/execution/tasks.md) and [`docs/execution/spec.md`](docs/execution/spec.md). Engineering recipes go in [`docs/execution/technical.md`](docs/execution/technical.md).
> 
> **Invariant on Execution Architecture**: AI agents must never invent parallel architecture documents; all feature extensions must be expressed as delta contracts in `docs/execution/spec.md` and promoted to `docs/architecture/` upon milestone gate passage. The fifth execution file `technical.md` is the authorized handbook, not a second architecture plane.
>
> Any temporary thinking, scratch notes, or intermediate outputs must be kept in model scratchpads or ephemeral artifact directories—never committed as files in the repository tree.
