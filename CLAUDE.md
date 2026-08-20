# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project

Vanguard / AETHER — a verifiable, modular recursive-agency substrate built around
`observe → propose → authorize → effect → receipt → evaluate`. The exterior judge is supposed to be
unreachable from the agent it grades.

**Concept Lock:** v0.6.0 (`docs/SPEC.md`, ADRs `0069`–`0074`). **Shipped package:** `vanguard-runtime`
`0.4.5b1` (`pyproject.toml`); `requires-python = ">=3.10"`.

**Human / Director navigation:** [`README.md`](README.md) (reading order, as-built vs planned, what is
held). This file is for agents working in the tree.

Polyglot monorepo: stdlib-oriented Python core plus TypeScript/Ink CLI (`@vanguard/cli`), npm workspace
at repo root.

**Pre-development hold.** Concept Lock docs are complete and awaiting Engineering Director / Chief
Engineer **APPROVED**. Do **not** start production coding, CI rewiring, runtime convergence, plugin
implementation, F1 fixes, or `layer0/` deletion until
`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`
authorizes Wave 0.

**As-built vs planned (do not conflate):**

| Locked / planned (SPEC + `002`) | On disk today |
|---|---|
| Packages = sole CI subject of record | Living CI gates `test/layer0` + packs + lexical tools |
| Fail-closed ceilings; signed verdicts only | `layer0/spi/ceiling.py` fail-open; F1 unsigned `"pass"` in `layer0/scheduler/driver.py` |
| Complete `D_H`; `mhf.trajectory/1` | `FrozenHarness` exists; trajectory schema file **missing** |
| Wire-first plugins on packages path | JSON-RPC lives under `layer0/spi/jsonrpc.py` (packages toolkit already imports it) |
| One coding-agent E2E (Wave 4) | `packs/code-default` + `agency/manifests/vg-*` + `vg` CLI — not that E2E yet |

## Commands

### Python (repo root)

```bash
python3 -m unittest discover -s test -t .          # full suite — not fully green
python3 -m unittest test.kernel.test_dispatch      # single module
python3 -m unittest discover -s test/kernel -t .   # production kernel — not in living CI
python3 -m unittest discover -s test/layer0 -t .   # fork suite — currently CI-gated
python3 -m unittest discover -s test/packs -t .    # code-default pack — currently CI-gated
python3 tools/run_active_contract_tests.py         # exists; not a living-CI step
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/scan_secrets.py
python3 tools/run_dogfood_r9.py
python3 tools/check_backend_artifacts.py --release
```

Living CI (`.github/workflows/ci.yml`, Python 3.12) currently runs: `test.test_repo_paths`,
`test/layer0`, `check_boundaries.py`, `check_tcb_budget.py`, `check_domain_blindness.py` (I-7),
`check_isolation_policy.py` (I-6), `test/packs`, `check_stale_paths.py`, `check_markdown_links.py`,
`scan_secrets.py`. It does **not** run `test/kernel` or packages runtime/agency/adapters. That is
false confidence relative to v0.6 law. `test_repo_paths` / `check_stale_paths` may fail on an archive
citation (`docs/sprint6B`) — Wave 0 hygiene, not architecture. Do not rewire CI until Wave 0 is
authorized.

### TypeScript / CLI (`vanguard/clients/cli`)

From repo root (`package.json` workspaces) or the CLI directory:

```bash
npm run typecheck    # tsc --noEmit
npm test             # tsc, then node --test on dist/test/*.test.js
npm run vg           # tsx src/main.tsx
```

Node's built-in test runner (not Jest/Vitest); sources in `vanguard/clients/cli/test/*.test.ts`.

### Cleanup

`make clean` (py/js/build/test/cache); review `make clean-all` before using it (`node_modules`).

## Architecture

Hexagonal lattice, CI-enforced (`tools/check_boundaries.py`).
`PACKAGE_NAMES = {domain, ports, kernel, agency, runtime, adapters, apps}`:

```
domain ← ports ← kernel ← agency ← runtime → adapters
```

- `domain/` — pure value objects and wire contracts; **stdlib-only Python**, plus a small parallel
  TypeScript set (`contracts.ts`, JCS helpers). Imports nothing else in the tree.
- `ports/` — `environment.py`, `evaluator.py`, `event_store.py`, `blob_store.py`, `kernel.py`,
  `model.py`, `sandbox.py`, `determinism.py`, `index.py`.
- `kernel/` — attenuation, budget, classifier, dispatch, grants, policy, provenance, `model.py`
  (kernel types, not an LLM adapter).
- `agency/` — `episode/engine.py` (`EpisodeEngine`, `spawn()`), `context/` (compiler/compaction),
  `manifests/vg-*` (as-built harness configs).
- `runtime/` — `root.py` (composition root), `governance/`, `ledger/`, `service/`. There is **no**
  `coordination.py` or `loops/` package. Coding-adjacent leftovers (`tier_escalation.py`,
  `skill_index.py`, …) still live here; extraction is Wave 3–4.
- `adapters/` — `models/` (OpenRouter, Ollama, cassette, fake), `evaluators/`, `sandbox/` (rootless
  bwrap), `stores/` (SQLite WAL), `environment/`. **Must not** import `kernel` or `agency`.
- `apps/` — lattice slot; only `__init__.py` today.

`layer0/` is a copy-fork (spi, registry, scheduler, kernel, events, compose). Absorb contracts; do
not rewrite production into it.

CLI entry: `vanguard/clients/cli/src/main.tsx` (`vg`).  
Evaluator: `vanguard.packages.adapters.evaluators.daemon:main` (`vanguard-evaluator`).

**Normative documentation:** `docs/SPEC.md` (only living spec) + `docs/04_annex/KERNEL.md` +
`docs/04_annex/MEASUREMENT.md`. ADRs `0069`–`0074` outrank the v0.5.0 “M1 destination = layer0”
story. Roadmap/gap register:
`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.
`docs/02_roadmap/` and `docs/03_sprints/sprint_active.md` are historical as *next* work.
`docs/archive/v045/` is evidence, not law.
