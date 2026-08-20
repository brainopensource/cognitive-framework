# AETHER / Vanguard — Version 6 (Concept Lock)

A verifiable recursive-agency substrate: **planned** — harnesses compile from manifests and
plugins into a `FrozenHarness`; **as-built** — a `FrozenHarness` compose path already exists in
`vanguard/packages/domain/artifacts/manifest.py`, but complete `D_H` (prompt, ceiling, policy,
routes), wire-first plugins on the packages path, and `mhf.trajectory/1` are **locked, not fully
implemented**. Effects pass an attenuation kernel; the judge that grades a run is supposed to be
unreachable from the agent it grades (defect **F1** in `layer0/` currently violates that).

```text
observe → propose → authorize → effect → receipt → evaluate
```

| | |
|---|---|
| **Concept Lock** | v0.6.0 — `docs/SPEC.md` + ADRs `0069`–`0074` |
| **Shipped package** | `vanguard-runtime` `0.4.5b1` (`pyproject.toml`); Python `>=3.10` (living CI uses 3.12) |
| **Status** | Documentation lock complete. **Production coding held** until Engineering Director / Chief Engineer approval. |
| **Next authorized code** | Wave 0 (CI subject-of-record + named falsifiers) — only after **APPROVED** |

[![Concept Lock](https://img.shields.io/badge/AETHER-v0.6.0--concept--lock-blue.svg)](docs/SPEC.md)
[![Lattice](https://img.shields.io/badge/Production-vanguard%2Fpackages-green.svg)](docs/SPEC.md)
[![Hold](https://img.shields.io/badge/Production_coding-held-orange.svg)](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md)

---

## Director / Chief Engineer — start here

This repository is under **final independent review** before Wave 0. You own the go/no-go. Law is
SPEC + ADRs + annexes; GAMMA and the gap register are the lock plan and the operational sequence;
`docs/07_reviews/` is evidence, not a second spec.

### Suggested path (whole-project, not GAMMA-only)

1. **This file** — what exists, what is held, where to look.
2. **Law:** [`docs/SPEC.md`](docs/SPEC.md) · [`docs/05_adr/INDEX.md`](docs/05_adr/INDEX.md) (especially [`0069`](docs/05_adr/0069-runtime-convergence-python-first-packages-canonical.md)–[`0074`](docs/05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md)) · [`docs/04_annex/KERNEL.md`](docs/04_annex/KERNEL.md) · [`docs/04_annex/MEASUREMENT.md`](docs/04_annex/MEASUREMENT.md)
3. **Lock + execution register:** [`GAMMA`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md) · [`002 foundation roadmap / gap register`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md)
4. **Live code (minimum):** `vanguard/packages/` (production lattice) · `layer0/` (fork to absorb) · `packs/code-default/` · `vanguard/clients/cli/` · `.github/workflows/ci.yml`
5. **Advisory evidence** (do not treat as competing plans):
   - [`docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/`](docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/) — `00_tech_lead_*`, `00_arch_lead_*`, `00_AI-Specialist_*`, `00_SYTEMS-ENG_*` suggestion files
   - [`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/`](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/) — principal proposal, parecer v4, full-refactor, execution plan, Aether waves (non-normative)
6. **Forensics / process history:** [`VANGUARD_V060_FORENSIC_DISCOVERY.md`](docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md) · [BETA](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_BETA.md) · [DELTA](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_DELTA.md)

Agent/contributor pointers: [`AGENTS.md`](AGENTS.md) · [`CLAUDE.md`](CLAUDE.md).

### Decision we need from you

**APPROVED** — v0.6 foundation and docs are finalized; Wave 0 may begin.  
**BLOCKED** — remaining issues that cannot be closed on paper, before any production implementation.

You may correct SPEC/ADR/annex/roadmap/docs as part of review (ADRs are **append-only**: add a new
ADR rather than silently editing `0069`–`0074`). Do **not** start production coding (CI rewire, F1
fix, runtime merge, plugin implementation, `layer0/` deletion) as part of the review.

---

## What this system is

Vanguard/AETHER compiles **harnesses** (manifest + plugins → `FrozenHarness`) and runs **agents**
(`Agent = Principal + HarnessInstance`) through one effect machine. That is the **locked** v0.6
shape. Coding is Domain Pack #1, not the ontology.

**Today:** the production loop is `EpisodeEngine` in packages; coding harnesses exist both as
`packs/code-default/` (MHF-shaped `harness.yaml`) and as older `vanguard/packages/agency/manifests/vg-*`
trees. The CLI (`vg`) is a client of the runtime. The first *honest* coding-agent product is
**Wave 4**, after the trust spine and one runtime authority are real — not a second framework.

Thesis: *what solved it must be separable, and the judge must be unreachable from the judged.*

---

## What exists in this tree (as-built)

Two runtimes are on disk. **Packages is production truth.** `layer0/` is a copy-fork whose SPI /
JSON-RPC / lifecycle contracts are to be absorbed — not a destination rewrite, and not a third tree.

| Surface | Path | Role today |
|---|---|---|
| Production lattice | `vanguard/packages/` | Kernel (S0–S12 in `kernel/dispatch.py`), `EpisodeEngine.spawn()`, SQLite WAL store, exterior evaluator, bwrap sandbox, OpenRouter/Ollama adapters, composition root `runtime/root.py` |
| Convergence fork | `layer0/` | SPI + JSON-RPC/UDS + broker/lifecycle + sequential driver — **also** `MemoryLedger`, fail-open ceilings, fabricated verdict **F1** (`layer0/scheduler/driver.py`) |
| First domain pack | `packs/code-default/` | MHF `harness.yaml` + plugin yaml: planner, fs, ast-patch, repo-map, terminal, evaluation gate (pack tests exist; not the Wave-4 E2E yet) |
| Older manifests | `vanguard/packages/agency/manifests/vg-*` | As-built harness configs (`vg-code-default`, `vg-code-claude-shaped`, `vg-shell-only`, …) |
| `apps/` | `vanguard/packages/apps/` | Lattice slot only (`__init__.py`). Not a coding package today |
| CLI / TUI | `vanguard/clients/cli/` | `vg` (Ink/React). Workspace scripts: `npm run vg` from repo root |
| Tests | `test/` | Full suite exists; **not fully green**. `test/kernel` is **not** in living CI |
| Living CI | `.github/workflows/ci.yml` | `test_repo_paths`, `test/layer0`, boundaries, TCB, I-7, I-6, `test/packs`, stale paths, markdown links, secrets — **not** kernel/runtime/agency/adapters |
| Schemas | `schemas/v4/`, `schemas/mhf/` | v4 JCS vectors as-built; MHF subset present; **`mhf.trajectory/1` not on disk** (Wave 1) |
| Isolation images | `containers/` | Worker UID 10001, evaluator UID 10002 |
| Lab / benches | `lab/`, `benchmarkings/` | Measurement and task sets; Phase-2 promotion is **deferred** |

**Held until APPROVED:** Wave 0 CI rewire, F1 fix, ceiling fail-closed, dual-tree convergence, `root.py`
split, plugin walking skeleton, extra packs, concurrency, Meta-Harness, Rust.

---

## Architecture (production lattice)

Hexagonal, CI-enforced (`tools/check_boundaries.py`):

```text
domain ← ports ← kernel ← agency ← runtime → adapters
         (apps/ is a client of runtime, not a second ontology)
```

- **`domain/`** — pure value objects and wire contracts; stdlib-only Python, plus a small parallel TypeScript set.
- **`ports/`** — `environment`, `evaluator`, `event_store`, `blob_store`, `kernel`, `model`, `sandbox`, `determinism`, `index`.
- **`kernel/`** — attenuation, budget, grants, dispatch, policy, provenance, classifier (`kernel/model.py` is kernel types, not an LLM).
- **`agency/`** — `EpisodeEngine` (turn loop + `spawn()`), context compiler, `manifests/vg-*`.
- **`runtime/`** — `root.py`, `governance/`, `ledger/`, `service/` (no `coordination.py` / `loops/` on disk).
- **`adapters/`** — models, sandbox, evaluators, stores, environment. **Must not** import `kernel` or `agency`.
- **`apps/`** — reserved client slot in `check_boundaries.py`; empty of coding modules today.

Dispatch/security constitution: [`docs/04_annex/KERNEL.md`](docs/04_annex/KERNEL.md).  
Measurement constitution (promotion **deferred**): [`docs/04_annex/MEASUREMENT.md`](docs/04_annex/MEASUREMENT.md).

The retired 14-tier biological taxonomy is gone on purpose ([ADR-M0-10](docs/05_adr/ADR-M0-10-no-metaphysics.md)).

---

## Repository map

```text
Aether-D-System/
├── .github/workflows/ci.yml          # living CI (layer0-centric today — Wave 0 will change this)
├── layer0/                           # copy-fork to absorb (not the v0.6 destination)
│   ├── spi/                          # Protocols + jsonrpc — promote into packages
│   ├── registry/                     # plugin lifecycle / broker — promote
│   ├── scheduler/                    # sequential driver; F1 lives here
│   ├── kernel/ · events/ · compose/  # diverging ports — packages remains semantic oracle
├── vanguard/
│   ├── packages/                     # PRODUCTION lattice
│   │   ├── domain/ ports/ kernel/ agency/ runtime/ adapters/
│   │   └── apps/                     # lattice slot; empty of coding modules today
│   └── clients/cli/                  # TypeScript Ink TUI (`vg`)
├── packs/code-default/               # MHF-shaped first domain pack
├── test/                             # Python suite by subsystem (kernel, runtime, layer0, packs, …)
├── tools/                            # boundaries, TCB, secrets, dogfood; codegen at tools/codegen/
├── schemas/v4/ · schemas/mhf/ · containers/ · lab/ · benchmarkings/
└── docs/                             # see Documentation map below
```

CLI entry: `vanguard/clients/cli/src/main.tsx` (`npm run vg`).  
Evaluator entry: `vanguard.packages.adapters.evaluators.daemon:main` (`vanguard-evaluator`).

---

## Documentation map (what is law)

| Document | Role |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | **Only** living normative spec (RFC-2119 here and in annexes only) |
| [`docs/05_adr/`](docs/05_adr/) | Append-only decisions. `0069`–`0074` are the v0.6 lock. `0067` is a numbering hole |
| [`docs/04_annex/KERNEL.md`](docs/04_annex/KERNEL.md) | Dispatch / capabilities / security |
| [`docs/04_annex/MEASUREMENT.md`](docs/04_annex/MEASUREMENT.md) | Lab measurement doctrine (v0.6: identity locked; promotion deferred) |
| [GAMMA](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md) | Concept Lock plan (not a second SPEC) |
| [`002` roadmap / gap register](docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md) | Living foundation sequence (Wave 0→4) |
| [`docs/02_roadmap/`](docs/02_roadmap/), [`docs/03_sprints/sprint_active.md`](docs/03_sprints/sprint_active.md) | **Historical** M0–M6 / sprint board — superseded as *next* work |
| [`docs/07_reviews/`](docs/07_reviews/) | Forensic + advisory corpus — evidence. Director may later archive bloat |
| [`docs/archive/v045/`](docs/archive/v045/) | Pre-lock VG-00…13C — evidence, not law |

**Authority on conflict:** SPEC, then a newer ADR, then GAMMA (plan), then `002` (register). Review
files and old roadmaps cannot be cited as requirements.

Foundation sequence after APPROVED (no calendar dates):

```text
Wave 0  CI truth + named falsifiers
Wave 1  Fail-closed trust spine (F1, ceilings, lineage, D_H, trajectory, writers)
Wave 2  Converge in place (absorb layer0 contracts; then delete dupes)
Wave 3  Walking skeleton — framework that compiles harnesses
Wave 4  One real coding-agent E2E  ← foundation stop
        then extra packs, concurrency, multi-agent policy, Meta-Harness
```

---

## Commands

Python (repo root). The full suite is **not** fully green; living CI does **not** yet run `test/kernel`.

```bash
python3 -m pip install -e '.[dev]'   # Python 3.10+
python3 -m unittest discover -s test -t .            # full suite (expect some FAIL/ERROR)
python3 -m unittest discover -s test/kernel -t .     # production kernel (not in living CI)
python3 -m unittest discover -s test/layer0 -t .     # fork suite (currently CI-gated)
python3 -m unittest discover -s test/packs -t .      # code-default pack (currently CI-gated)
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/scan_secrets.py
python3 tools/run_active_contract_tests.py           # exists; not a living-CI step today
# Wave 0 (after APPROVED): python3 tools/codegen/generate_types.py --check
```

CLI (npm workspace at repo root, or `cd vanguard/clients/cli`):

```bash
npm ci
npm run typecheck
npm test
npm run vg
```

`make clean` removes caches; review `make clean-all` before using it (`node_modules`).

---

## Model access

Abstracted behind `ModelPort`. Adapter **modules** on disk: OpenRouter, Ollama, cassette, fake.
DeepSeek / OpenAI appear as **routes and env keys** (`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`,
`OPENAI_API_KEY`), not as separate adapter files. Keep keys unset for deterministic / trust-spine tests.

| Provider | Notes |
|---|---|
| OpenRouter | `vanguard/packages/adapters/models/openrouter.py` |
| Ollama | `.../ollama.py`; some `test/runtime` cases are env-sensitive |
| Cassette / fake | offline / unit |

---

## As-built module notes (packages)

Useful inventory; file names drift — treat SPEC/ADRs as law if this list disagrees.

- **`domain/`** — primitives, wire contracts, ledger events/reducers, evidence, selectors, JCS canonicalisation.
- **`kernel/`** — `dispatch.py`, `attenuation.py`, `budget.py`, `grants.py`, `classifier.py`, `policy.py`, `provenance.py`.
- **`agency/episode/engine.py`** — production `EpisodeEngine` / `spawn()` (canonical recursive machine).
- **`agency/context/`** — prompt/context compiler and compaction.
- **`agency/manifests/`** — as-built `vg-code-default`, `vg-code-claude-shaped`, `vg-shell-only`, `vg-table-default`, …
- **`runtime/root.py`** — composition root (large; split **in place** is Wave 2, not a new tree). Also: `governance/`, `ledger/`, `service/`, plus coding-adjacent leftovers (`tier_escalation.py`, `skill_index.py`, …) still in runtime — pack extraction is Wave 3–4.
- **`adapters/evaluators/`** — exterior signed judge (UID 10002). The **layer0** scheduler currently fabricates `"pass"` (F1); packages must **read** signed verdicts.
- **`adapters/sandbox/`** — rootless bubblewrap for untrusted exec.
- **`adapters/stores/`** — SQLite WAL event store (packages). Layer0 uses `MemoryLedger` (`layer0/events/store.py`).

Import rule: `domain ← ports ← kernel ← agency ← runtime → adapters`. Adapters never import kernel/agency.
