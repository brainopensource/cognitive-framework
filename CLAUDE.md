# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Vanguard General Task Solver (GTS) — a verifiable, modular meta-harness runtime built around a strict
`observe → propose → authorize → effect → receipt → evaluate` turn lifecycle, where the exterior judge
that evaluates a run is architecturally unreachable from the agent it judges. Currently `v0.4.5-beta`.

This is a polyglot monorepo: a stdlib-only Python core (`vanguard-runtime`) plus a TypeScript/Ink CLI/TUI
client (`@vanguard/cli`), managed as an npm workspace.

## Commands

### Python (core runtime, from repo root)

```bash
python3 -m unittest discover -s test -t .          # full test suite
python3 -m unittest test.kernel.test_dispatch       # single test module (dotted path)
python3 -m unittest discover -s test/kernel -t .    # single test subpackage
python3 tools/run_active_contract_tests.py          # active-contract-only subset (CI-gated)
python3 tools/check_boundaries.py                   # import-layering architecture lint
python3 tools/check_tcb_budget.py                   # trusted-computing-base LOC budget
python3 tools/scan_secrets.py                        # secret scan
python3 tools/run_dogfood_r9.py                      # release/dogfood gate
python3 tools/check_backend_artifacts.py --release   # backend/OCI artifact check
```

Note: as of the last full run, the suite is not fully green — check against a clean baseline first before
assuming a red run is caused by your change. The `test/test_repo_paths.py` vs. `docs/agile/sprint0/`
stale-path bug referenced in earlier revisions of this file was fixed at the v0.5.0 Foundation Lock:
`tools/repo_paths.py` no longer resolves against the dead `docs/scrum`/`docs/main_v4` paths.

### TypeScript / CLI client (`vanguard/clients/cli`)

Run from repo root via npm workspaces, or `cd vanguard/clients/cli` directly:

```bash
npm run typecheck    # tsc --noEmit
npm test              # builds (tsc), then runs node --test on dist/test/*.test.js
npm run vg            # run the CLI live via tsx (src/main.tsx)
```

Node's built-in test runner is used (not Jest/Vitest); test sources are in
`vanguard/clients/cli/test/*.test.ts`.

### Cleanup

`make clean` (safe: py/js/build/test/cache artifacts), `make clean-all` (also removes `node_modules`).

## Architecture

Hexagonal / ports-and-adapters design with a **strict, CI-enforced unidirectional import boundary**
(`tools/check_boundaries.py`) across `vanguard/packages/`:

```
domain ← ports ← kernel ← agency ← runtime → adapters
```

- `domain/` — pure value objects and wire contracts; **stdlib-only**, no dependency on anything else in
  the tree. Has parallel Python and TypeScript sources.
- `ports/` — abstract interfaces only: `environment`, `evaluator`, `event_store`, `kernel`, `model`, `sandbox`.
- `kernel/` — the "Attenuation Kernel": `attenuation.py`, `budget.py`, `classifier.py`, `dispatch.py`,
  `grants.py`, `model.py`, `policy.py`, `provenance.py`. Capability leasing lives here.
- `agency/` — `episode/` (the observe→propose→authorize→effect→receipt→evaluate engine),
  `context/` (context compiler), `manifests/` (declarative harness configs, e.g. `vg-code-claude-shaped`).
- `runtime/` — the composition root (`root.py`, `coordination.py`) plus `governance/` (Ed25519 approval
  flow), `ledger/`, `loops/`, `service/`.
- `adapters/` — concrete implementations (`environment/`, `evaluators/`, `models/`, `sandbox/` — rootless
  bubblewrap, `stores/`). **May not import `kernel` or `agency` directly** — only `domain`/`ports`.

Enforcement is programmatic, not just convention: a change that reaches across these boundaries the wrong
way will fail `tools/check_boundaries.py` in CI, regardless of whether tests pass.

CLI/TUI entry point: `vanguard/clients/cli/src/main.tsx` (Ink/React), exposed as the `vg` binary.
Evaluator daemon entry point: `vanguard.packages.adapters.evaluators.daemon:main` (console script
`vanguard-evaluator`).

Model access is abstracted behind `ModelPort`, with adapters for OpenRouter (`OPENROUTER_API_KEY`),
DeepSeek, OpenAI, and local Ollama.

**Normative documentation (v0.5.0 Foundation Lock, `docs/SPEC.md` §8):**
`docs/SPEC.md` is the **only** living normative specification, with `docs/04_annex/KERNEL.md` and
`docs/04_annex/MEASUREMENT.md` carrying the same RFC-2119 force for the dispatch/security and measurement
domains respectively. `docs/05_adr/` holds the decision log (append-only, reversal conditions). Read
`docs/SPEC.md` before making architectural decisions, not just the README. `docs/02_roadmap/` holds
version gates and the epic map; `docs/03_sprints/sprint_active.md` is the execution board. The pre-lock
VG-00…13C corpus (previously referenced here as `docs/main_v4/`, which never actually existed on this
tree — it was `docs/01_specs/backend/`) is archived, evidence-not-law, at `docs/archive/v045/`; commit
messages and older docs citing VG-00..12 / GTS-13C refer to files now under
`docs/archive/v045/01_specs/backend/`.

## CI gates

`.github/workflows/ci.yml` (workflow `vanguard-ci`) runs a single job, `vanguard-living-gates`, chaining:
`test.test_repo_paths`, the Layer-0 microkernel suite (`test/layer0`), `tools/check_boundaries.py`,
`tools/check_tcb_budget.py`, `tools/check_domain_blindness.py` (I-7), `tools/check_isolation_policy.py`
(I-6), the code-default pack suite (`test/packs`), `tools/check_stale_paths.py`,
`tools/check_markdown_links.py`, and `tools/scan_secrets.py`. These are hard-fail gates by design — a gate
that reports without blocking is treated as a bug, not a feature.
