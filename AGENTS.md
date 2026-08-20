# Repository Guidelines

**Start here:** [`README.md`](README.md) is the primary navigation map (law vs evidence, as-built surfaces, Director review path, and the Wave 0–4 foundation plan). This file specifies operational rules and procedures for AI agents and human contributors.

---

## 1. Project Structure & Module Organization

Vanguard / AETHER is a Python-first recursive-agency substrate (`requires-python >= 3.10`, tested on Python 3.12 in CI) with a TypeScript/React/Ink interactive CLI (`vg`).

- **Concept Lock v0.6.0 Law**: [`docs/SPEC.md`](docs/SPEC.md) + ADRs [`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0074`](docs/05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md).
- **Living Foundation Roadmap**: [`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md).

### Hexagonal Production Lattice (`vanguard/packages/`)
The canonical production truth lives in `vanguard/packages/`, strictly enforcing the hexagonal boundary flow:
```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a client slot of runtime)
```

| Subsystem | Location | Responsibilities & Contents |
|---|---|---|
| **`domain/`** | `vanguard/packages/domain/` | Pure value objects, wire contracts, JCS canonicalization, ledger reducers, evidence models, manifest parsers. Stdlib Python only. Zero dependencies on other repo packages. |
| **`ports/`** | `vanguard/packages/ports/` | Hexagonal port protocols: `kernel`, `model`, `sandbox`, `evaluator`, `event_store`, `blob_store`, `environment`, `determinism`, `index`. |
| **`kernel/`** | `vanguard/packages/kernel/` | Trusted Computing Base (TCB limit `<=1438` LOC). 13-stage dispatch pipeline (S0–S12), monotonic capability attenuation, budget & turn tracking, capability grants, fail-closed policy, execution provenance DAG. Domain-blind. |
| **`agency/`** | `vanguard/packages/agency/` | Recursive turn engine. `EpisodeEngine` turn loop, child agent `spawn()`, context compiler, structured compaction, manifest loader, and as-built configs (`manifests/vg-*`). |
| **`runtime/`** | `vanguard/packages/runtime/` | Composition root (`root.py`), governance & Ed25519 approvals (`governance/`), SQLite WAL event store (`ledger/`), and runtime RPC services (`service/`). |
| **`adapters/`** | `vanguard/packages/adapters/` | Concrete implementations: Models (OpenRouter, Ollama, Cassette, Fake), Evaluator daemon & RPC client (UID 10002), Rootless Sandbox (bwrap UID 10001), SQLite store. **Must not** import `kernel` or `agency`. |
| **`apps/`** | `vanguard/packages/apps/` | Reserved boundary-lattice slot (`__init__.py`). |

### Adjacent Surfaces & Artifacts

| Surface | Path | Role & Status |
|---|---|---|
| **Layer-0 Fork** | `layer0/` | Temporary copy-fork (SPI, JSON-RPC, registry/broker, sequential driver). Contains defect **F1** (`layer0/scheduler/driver.py`). To be absorbed and pruned in Wave 2. |
| **Domain Pack #1** | `packs/code-default/` | First Modular Harness Framework (MHF) pack. Contains `harness.yaml`, plugin manifests (`fs`, `ast-patch`, `repo-map`, `terminal`, `evaluation-gate`, `single-planner`), prompt templates. |
| **CLI / TUI** | `vanguard/clients/cli/` | TypeScript/Ink interactive TUI (`vg`). Workspace scripts: `npm run vg`. Tests in `vanguard/clients/cli/test/`. |
| **Test Suite** | `test/` | 900+ test cases across 17 test categories (`kernel/`, `contracts/`, `agency/`, `runtime/`, `adapters/`, `security/`, `trust/`, `packs/`, `layer0/`, `tools/`, etc.). See [`test/README.md`](test/README.md). |
| **Tooling** | `tools/` | Static architecture linters (`check_boundaries.py`, `check_tcb_budget.py`, `scan_secrets.py`, `check_domain_blindness.py`, `check_isolation_policy.py`), codegen (`tools/codegen/generate_types.py`), dogfood runners. |
| **Schemas** | `schemas/v4/`, `schemas/mhf/` | Wire schemas and JCS vectors. (`mhf.trajectory/1` to land in Wave 1). |
| **Isolation Containers** | `containers/` | OCI and bubblewrap container definitions (worker UID 10001 vs evaluator UID 10002). |
| **Lab & Benchmarks** | `lab/`, `benchmarkings/` | Latency benchmarks, AA measurement runners (Phase-2 promotion deferred). |

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

# Layer-0 copy-fork tests
python3 -m unittest discover -s test/layer0 -t .

# Single focused module / single test case
python3 -m unittest test.kernel.test_dispatch -v
python3 -m unittest test.kernel.test_dispatch.TestDispatchPipeline.test_s0_observe_produces_receipt -v

# Full suite (expect known offline environment sensitivities in runtime/adapters)
python3 -m unittest discover -s test -t .
```

### Architecture, TCB, & Security Linters
```bash
# Enforce hexagonal boundaries
python3 tools/check_boundaries.py

# Verify Trusted Computing Base budget (threshold <= 1438 LOC)
python3 tools/check_tcb_budget.py

# Scan workspace for leaked secrets and API keys
python3 tools/scan_secrets.py

# Invariant checks
python3 tools/check_domain_blindness.py   # Invariant I-7
python3 tools/check_isolation_policy.py   # Invariant I-6
python3 tools/check_markdown_links.py     # Relative link verification
python3 tools/check_stale_paths.py        # Stale documentation path check
```

### TypeScript CLI Commands (`vanguard/clients/cli`)
```bash
npm run typecheck    # Typecheck TypeScript sources
npm test             # Run Node built-in test runner on dist/test/*.test.js
npm run vg           # Launch interactive TUI
```

---

## 3. Pre-Development Hold & Wave Plan

> [!IMPORTANT]
> The codebase is under **pre-development hold**. Concept Lock documentation is finalized and awaiting Engineering Director / Chief Engineer **APPROVAL**.
>
> Do **not** begin Wave 0 CI rewiring, F1 fixes, runtime convergence, plugin implementation, or `layer0/` deletion until the Director approves and roadmap `002` authorizes Wave 0.

Sequence upon authorization:
1. **Wave 0**: CI Truth & Named Falsifiers (`vanguard/packages` as sole subject of record).
2. **Wave 1**: Fail-Closed Trust Spine (fix F1, fail-closed ceilings, signed verdicts, `mhf.trajectory/1`).
3. **Wave 2**: In-Place Lattice Convergence (absorb `layer0` contracts into `packages`, delete `layer0/`).
4. **Wave 3**: Walking Skeleton (manifest + plugin compilation to `FrozenHarness` on packages path).
5. **Wave 4**: First Real Coding-Agent E2E (Foundation Stop).

---

## 4. Coding Style & Architectural Conventions

- **Python**: Python 3.10+ syntax with 4-space indentation, strict type hints, focused single-responsibility modules, and `snake_case` functions/variables with `PascalCase` classes.
- **Dependency Hierarchy**: Lower layers must never import higher layers (`domain ← ports ← kernel ← agency ← runtime → adapters`). Adapters implement port interfaces and must never import kernel or agency.
- **TCB Budget**: Code added to `vanguard/packages/kernel/` must not exceed the line-of-code budget enforced by `tools/check_tcb_budget.py`.
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
