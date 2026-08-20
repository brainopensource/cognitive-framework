# Repository Guidelines

**Start here:** [`README.md`](README.md) is the navigation map (law vs evidence, as-built surfaces, Director path, Wave 0–4 plan). This file is contributor procedure.

## Project Structure & Module Organization

Vanguard / AETHER is a Python-first recursive-agency runtime (`requires-python >= 3.10`) with a TypeScript CLI. **v0.6.0 Concept Lock** law is `docs/SPEC.md` plus ADRs `0069`–`0074`. The living foundation sequence is `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.

**Production lattice:** `vanguard/packages/` — `domain` → `ports` → `kernel` → `agency` → `runtime` → `adapters`. `apps/` is a boundary-lattice slot and is empty of coding modules today. **`layer0/`** is a copy-fork to absorb, not a destination rewrite. Do not add a third tree.

| Path | What it is |
|---|---|
| `vanguard/packages/` | Production kernel, `EpisodeEngine`, WAL ledger, evaluator, sandbox |
| `layer0/` | Fork (SPI/jsonrpc/broker/driver). Contains defect F1 |
| `packs/code-default/` | First MHF-shaped domain pack |
| `vanguard/packages/agency/manifests/vg-*` | Older as-built harness configs |
| `vanguard/clients/cli/` | `vg` TUI; tests in `vanguard/clients/cli/test/` |
| `test/` | Python tests by subsystem (`kernel/`, `runtime/`, `layer0/`, `packs/`, …) |
| `tools/` | Boundaries, TCB, secrets, dogfood; `tools/codegen/generate_types.py` |
| `schemas/v4/`, `schemas/mhf/` | Wire schemas (no `mhf.trajectory/1` file yet) |
| `lab/`, `benchmarkings/`, `containers/`, `docs/` | Lab, benches, OCI images, law + evidence |

Do **not** start Wave 0 CI rewiring, F1 fixes, runtime convergence, plugin implementation, or `layer0/` deletion until Director **APPROVED** and `002` authorizes Wave 0.

## Build, Test, and Development Commands

Install Python extras with `python3 -m pip install -e '.[dev]'` and JavaScript dependencies with `npm ci` (workspace root).

- `python3 -m unittest discover -s test -t .` — full Python suite (**not** fully green).
- `python3 -m unittest discover -s test/kernel -t .` — production kernel (**not** in living CI).
- `python3 -m unittest discover -s test/layer0 -t .` / `test/packs` — currently living-CI gated.
- `python3 -m unittest test.kernel.test_dispatch -v` — focused module.
- `npm test` / `npm run typecheck` / `npm run vg` — CLI (from repo root or `vanguard/clients/cli`).
- `python3 tools/run_active_contract_tests.py` — exists; **not** a step in `.github/workflows/ci.yml` today.
- `python3 tools/check_boundaries.py`, `check_tcb_budget.py`, `scan_secrets.py` — architecture / TCB / secrets.
- `make clean` removes caches; review targets before `make clean-all`.

Living CI (`.github/workflows/ci.yml`) currently runs `test_repo_paths`, `test/layer0`, boundaries, TCB, I-7, I-6, `test/packs`, stale paths, markdown links, secrets. That is **not** the v0.6 subject of record.

## Coding Style & Naming Conventions

Use Python 3.10+ with four-space indentation, type hints, focused modules, and `snake_case` names; classes use `PascalCase`. Keep imports aligned with the package lattice: lower layers must not import higher layers, and adapters should depend on ports. TypeScript follows the existing workspace style and strict typechecking. No formatter or linter is a universal gate, so match nearby code.

## Testing Guidelines

Add Python tests as `test_*.py` under the matching `test/<area>/` directory and TypeScript tests as `*.test.ts` in the CLI test directory. Include contract, boundary, security, or integration coverage when changing those concerns. Run focused tests first, then the full suite and relevant tools before submitting. Do not treat a green `test/layer0` run as I-2/I-4.

## Commit & Pull Request Guidelines

Use concise imperative subjects with the established prefixes, for example `feat(runtime): ...`, `fix(kernel): ...`, `docs: ...`, or `cleanup: ...`. PRs should explain behavior and verification, link relevant issues, and cite at least one valid active requirement such as `REQ-TRUST-001` in the body. Include screenshots for UI changes and call out configuration or security implications.

## Security & Configuration

Never commit credentials, live model responses containing secrets, or unreviewed generated artifacts. Provider keys are read from environment variables (for example `OPENROUTER_API_KEY`); keep them unset for deterministic local and trust-spine tests. Model **adapter files** are OpenRouter, Ollama, cassette, fake — not separate DeepSeek/OpenAI modules. Changes crossing sandbox, evaluator, capability, or approval boundaries require corresponding security tests and checks.
