# Repository Guidelines

## Project Structure & Module Organization

Vanguard is a Python-first agent runtime with a TypeScript CLI. Core packages live under `vanguard/packages/`, organized by dependency direction: `domain` (pure contracts), `ports`, `kernel`, `agency`, `runtime`, and concrete `adapters`. The CLI is under `vanguard/clients/cli/`. Python tests are in `test/`, grouped by subsystem; TypeScript tests are in `vanguard/clients/cli/test/`. Repository checks and provider utilities are in `tools/`; benchmark harnesses are in `benchmarkings/` and `lab/`; schemas, containers, and normative documentation are in `schemas/`, `containers/`, and `docs/`.

## Build, Test, and Development Commands

Install Python extras with `python3 -m pip install -e '.[dev]'` and JavaScript dependencies with `npm ci`.

- `python3 -m unittest discover -s test -t .` runs the full Python suite.
- `python3 -m unittest test.kernel.test_dispatch -v` runs a focused module.
- `npm test` runs CLI tests; `npm run typecheck` performs strict TypeScript checking.
- `python3 tools/run_active_contract_tests.py` runs active contract coverage.
- `python3 tools/check_boundaries.py`, `python3 tools/check_tcb_budget.py`, and `python3 tools/scan_secrets.py` run architecture, TCB, and secret checks.
- `make clean` removes caches and generated artifacts; review targets before using `make clean-all`.

## Coding Style & Naming Conventions

Use Python 3.10+ with four-space indentation, type hints, focused modules, and `snake_case` names; classes use `PascalCase`. Keep imports aligned with the package lattice: lower layers must not import higher layers, and adapters should depend on ports. TypeScript follows the existing workspace style and strict typechecking. No formatter or linter is a universal gate, so match nearby code.

## Testing Guidelines

Add Python tests as `test_*.py` under the matching `test/<area>/` directory and TypeScript tests as `*.test.ts` in the CLI test directory. Include contract, boundary, security, or integration coverage when changing those concerns. Run focused tests first, then the full suite and relevant tools before submitting.

## Commit & Pull Request Guidelines

Use concise imperative subjects with the established prefixes, for example `feat(runtime): ...`, `fix(kernel): ...`, `docs: ...`, or `cleanup: ...`. PRs should explain behavior and verification, link relevant issues, and cite at least one valid active requirement such as `REQ-TRUST-001` in the body. Include screenshots for UI changes and call out configuration or security implications.

## Security & Configuration

Never commit credentials, live model responses containing secrets, or unreviewed generated artifacts. Provider keys are read from environment variables (for example `OPENROUTER_API_KEY`); keep them unset for deterministic local and trust-spine tests. Changes crossing sandbox, evaluator, capability, or approval boundaries require corresponding security tests and checks.
