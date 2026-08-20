# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Vanguard / AETHER — a verifiable, modular recursive-agency substrate built around a strict
`observe → propose → authorize → effect → receipt → evaluate` turn lifecycle, where the exterior judge
that evaluates a run is architecturally unreachable from the agent it judges.

**Concept Lock:** v0.6.0 (`docs/SPEC.md`, ADRs `0069`–`0074`). **Shipped package version** remains
`0.4.5b1` in `pyproject.toml` until a later release cut.

This is a polyglot monorepo: a stdlib-only Python core (`vanguard-runtime`) plus a TypeScript/Ink CLI/TUI
client (`@vanguard/cli`), managed as an npm workspace.

**Pre-development hold.** Concept Lock is complete and awaiting Engineering Director / Chief Engineer
approval. Do **not** start production coding, CI rewiring, runtime convergence, plugin implementation,
or `layer0/` deletion until
`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`
authorizes Wave 0.

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

Note: the full Python suite is not fully green. Check against a clean baseline before assuming a red
run is caused by your change. Living CI currently gates `test/layer0` plus packs and lexical tools —
that is **false confidence** relative to v0.6 law (packages are the subject of record; Wave 0 will
rewire CI **after** director approval). `test/test_repo_paths.py` / `check_stale_paths` may still fail
on an archive citation (`docs/sprint6B`); that is Wave 0 hygiene, not architecture.

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

**Normative documentation (v0.6.0 Concept Lock, `docs/SPEC.md`):**
`docs/SPEC.md` is the **only** living normative specification, with `docs/04_annex/KERNEL.md` and
`docs/04_annex/MEASUREMENT.md` carrying the same RFC-2119 force for the dispatch/security and measurement
domains respectively. ADRs `0069`–`0074` outrank the v0.5.0 “M1 destination = `layer0/`” story.
`docs/05_adr/` holds the decision log (append-only). Read `docs/SPEC.md` before making architectural
decisions. The living foundation roadmap and gap register is
`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.
`docs/02_roadmap/` and `docs/03_sprints/sprint_active.md` are historical unless that register says
otherwise. The pre-lock VG-00…13C corpus is archived, evidence-not-law, at `docs/archive/v045/`.

**Runtime identity:** production lattice is `vanguard/packages/`. `layer0/` is a copy-fork to absorb,
not a destination rewrite. Do not add a third tree.

**Living CI (as-built, not yet Wave 0):** `.github/workflows/ci.yml` (workflow `vanguard-ci`) currently
runs `test.test_repo_paths`, `test/layer0`, `tools/check_boundaries.py`, `tools/check_tcb_budget.py`,
`tools/check_domain_blindness.py` (I-7), `tools/check_isolation_policy.py` (I-6), `test/packs`,
`tools/check_stale_paths.py`, `tools/check_markdown_links.py`, and `tools/scan_secrets.py`. That set
does **not** yet include `test/kernel` or packages runtime/agency/adapters — a known Concept Lock
gap. Do not rewire it until Wave 0 is authorized.
