# Repository Guidelines

**Start here:** [`README.md`](README.md) is the primary navigation map. This file specifies operational rules and procedures for AI agents and human contributors.

---

## 1. Project Structure & Documentation Architecture

Vanguard / AETHER is a Python-first recursive-agency substrate (`requires-python >= 3.10`, tested on Python 3.12 in CI) with a TypeScript/React/Ink interactive CLI (`vg`).

### The Canonical Documentation Triad
All documentation is strictly partitioned into three distinct authority tiers:

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

- **The Law**: [`docs/SPEC.md`](docs/SPEC.md) + accepted ADRs [`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0086`](docs/05_adr/0086-historical-adr-working-tree-consolidation.md).
- **The Decisions**: [`docs/05_adr/INDEX.md`](docs/05_adr/INDEX.md).
- **The Execution**: [`docs/03_sprints/sprint_active.md`](docs/03_sprints/sprint_active.md) & [`docs/02_roadmap/milestones.md`](docs/02_roadmap/milestones.md).

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
python3 -m pip install -e '.[dev]'

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
3. **Wave 2 (IN FLIGHT)**: In-Place Lattice Convergence (absorb `layer0` contracts, split `root.py`, eliminate duplicate surfaces).
4. **Wave 3 (QUEUED)**: Extensibility & Plugin Walking Skeleton (named component graphs, registry lifecycle on wire).
5. **Wave 4 (QUEUED - Foundation Stop)**: First Real Coding-Agent E2E (one real run with zero human cheating).
6. **Waves 5–10 (Macro Roadmap)**: Generality proof (Pack #2), mediated `agent.spawn`, concurrency, and Meta-Cognition.

---

## 4. Coding Style & Architectural Conventions

- **Python**: Python 3.10+ syntax with 4-space indentation, strict type hints, focused single-responsibility modules, and `snake_case` functions/variables with `PascalCase` classes.
- **Dependency Hierarchy**: Lower layers must never import higher layers (`domain ← ports ← kernel ← agency ← runtime → adapters`). Adapters implement port interfaces and must never import kernel or agency.
- **TCB Budget**: Code added to `vanguard/packages/kernel/` must not exceed the line-of-code budget ($\le 1438$ LOC) enforced by `tools/check_tcb_budget.py`.
- **TypeScript**: TypeScript 5.x with strict type checking, standard formatting matching existing files, and zero runtime dependencies outside React/Ink and Node stdlib.
- **Hermetic Testing**: All unit and contract tests must execute deterministically without network access or live API keys. Use fakes, test doubles, or cassette recordings.

---

## 5. Commit & Pull Request Guidelines

- **Commit Messages**: Use concise imperative subjects with established subsystem prefixes:
  - `feat(kernel): ...`, `fix(runtime): ...`, `test(contracts): ...`, `docs: ...`, `cleanup: ...`.
- **PR Description**:
  - Explain the exact behavior change and verification evidence.
  - Cite at least one valid active requirement from `docs/SPEC.md` or active ADRs (e.g. `REQ-TRUST-001`, `REQ-LATTICE-002`).
  - Confirm that `check_boundaries.py`, `check_tcb_budget.py`, and `scan_secrets.py` pass.
- **Security Invariants**: Changes crossing sandbox, capability, approval, or evaluator boundaries must include corresponding security tests under `test/security/` or `test/trust/`.

---

## 6. Security & Credentials

- Never commit credentials, private keys, or unreviewed model output dumps.
- Model provider API keys (`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`) are read exclusively from environment variables and must remain unset during automated test runs.
- Model adapters are structured as OpenRouter, Ollama, Cassette, Fake — not individual vendor files.

---

## 7. Strict Documentation Anti-Sprawl Invariant

> [!CAUTION]
> **MANDATORY INSTRUCTION FOR ALL AI AGENTS & CONTRIBUTORS:**  
> AI Agents **MUST NOT** create new Markdown files under `docs/`, `docs/plans/`, or anywhere across the workspace to leave scratch notes, plans, reviews, or summaries.  
> 
> All documentation updates must strictly edit existing canonical files in the **Clean Triad**:
> 1. **Modifying Normative Law** $\to$ Edit [`docs/SPEC.md`](docs/SPEC.md) (and [`docs/04_annex/`](docs/04_annex/)).
> 2. **Recording Architectural Decisions** $\to$ Add a new append-only ADR in [`docs/05_adr/`](docs/05_adr/).
> 3. **Updating Tasks, Sprints, or Execution Progress** $\to$ Edit [`docs/03_sprints/sprint_active.md`](docs/03_sprints/sprint_active.md) (and [`docs/02_roadmap/milestones.md`](docs/02_roadmap/milestones.md) for macro gates).
> 
> Any temporary thinking, scratch notes, or intermediate outputs must be kept in model scratchpads or ephemeral artifact directories—never committed as files in the repository tree.
