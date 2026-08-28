# VANGUARD / AETHER v0.6 — FORENSIC DISCOVERY

**Status:** Investigation. **Not law.** Law remains `docs/SPEC.md` and active ADRs until Concept Lock
supersedes them by citation.
**Tree:** `/home/rocha/Coding/Aether-D-System`
**HEAD:** `c7e9ded` (`docs: added staff docs`)
**Last `layer0/` + packages kernel code:** `2af33ca` (`feat(W2): Wave 2 Done`)
**Investigator:** Principal Staff Engineer / Tech Lead
**Date:** 2026-08-20
**Procedure:** `docs/07_reviews/TODO_DONT_COMMIT_BEFORE_DOING_IT_v2.md`
**As-built package version:** `pyproject.toml` `0.4.5b1` (Python `>=3.10`)

Evidence labels: `[FACT]` `[INFERENCE]` `[PROPOSAL]` `[UNKNOWN]`

---

## Phase status (this engagement)

| Item | Class | Evidence |
|---|---|---|
| TODO §5–19 forensic investigation | `DONE` | this file |
| Deliverable 1 (`VANGUARD_V060_FORENSIC_DISCOVERY.md`) | `DONE` | this file |
| Deliverable 2 (`PROMPT_ARCHITECTURE_CONCEPT_LOCK_V060.md`) | `IN_PROGRESS` | written then executed in-session |
| Runtime rewrite / CI rewire / dual-tree deletion | `DEFERRED` | TODO §4 and Concept Lock exit forbid code |
| User-suggestion steps 2–6 (CI truth, converge, substrate, plugins, E2E coding path) | `DEFERRED` | next major phase after Concept Lock |

This document does **not** design a new architecture. Locked P0 decisions live in the Concept Lock
ADRs (`0069`–`0073`) produced after this report.

---

## 1. Executive Summary

The repository contains **two Python runtimes** that claim the same Layer-0 job:

1. `vanguard/packages/` — the mature hexagonal production lattice (kernel S0–S12, SQLite WAL ledger,
   exterior evaluator daemon, rootless sandbox, episode `spawn()`, composition root).
2. `layer0/` — a copy-fork walking skeleton with SPI contracts, JSON-RPC/UDS broker, compose(),
   and a sequential scheduler that **fabricates** `VerdictRecorded {verdict: "pass"}`.

Living CI (`.github/workflows/ci.yml`) gates `test/layer0` + `test/packs` + lexical tools and
**does not run** `test/kernel`, `test/runtime`, `test/agency`, `test/adapters`, or the CLI.
On this tree the packages kernel suite is green (95 OK) while the full suite is red
(1119 ran, 7 FAIL, 5 ERROR). CI therefore cannot be treated as proof that the production lattice
works.

Current `docs/SPEC.md` (v0.5.0 Foundation Lock) names `layer0/` as the **M1 destination**. That
sentence is implementation-aspirational and contradicts as-built maturity. Supporting reviews
conflict with each other (Rust core vs Python-first; `layer0/` as target vs packages as canonical;
new top-level `core/`; evaluator as product plugin). Those conflicts are recorded here; they are
**not** silently merged.

**What must be locked before development resumes:** one production lattice, one recursive agent
primitive, decision-vs-state authority, plugin wire, evaluator exteriority, identity trinity,
replay taxonomy, and an explicit deferral of Meta-Harness / distribution / WASM / Rust rewrite.

---

## 2. Investigation Method

- As-built: executable trees, tests actually run, CI YAML, schemas, git history.
- Normative: `docs/SPEC.md`, `docs/04_annex/{KERNEL,MEASUREMENT}.md`, `docs/05_adr/` including
  `ADR-M0-*` (present on disk, missing from `INDEX.md`).
- Proposals: `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/*` treated as non-authoritative until
  adopted by ADR.
- Conflict rule: `AS-BUILT != NORMATIVE` is recorded, not reconciled in code.
- Re-verification: parecer v4 numbers from commit `99d1e0b` were **not** inherited; commands were
  re-run on `c7e9ded`.

Out of scope for this file: roadmap, sprints, production implementation, deleting either runtime.

---

## 3. Repository As-Built

### 3.1 Trees

| Tree | Role today | Maturity |
|---|---|---|
| `vanguard/packages/` | Hexagonal production lattice: `domain → ports → kernel → agency → runtime → adapters` (+ `apps/`) | EXISTS, TESTED, **not CI-gated as a suite** |
| `layer0/` | Parallel microkernel: `events, kernel, spi, registry, scheduler, compose` | EXISTS, TESTED (`test/layer0`), **CI-gated** |
| `packs/code-default/` | First domain pack (planner, toolkits, oracles, harness.yaml) | EXISTS, TESTED, CI-gated |
| `vanguard/clients/cli/` | TypeScript Ink CLI | EXISTS, TESTED locally, **not in living CI** |
| `schemas/mhf/` | Four JSON Schemas (`event_envelope`, `spi_payloads`, `effect_request`, `harness_manifest`) | PARTIAL |
| `schemas/v4/` | Historical v4 schemas + vectors | EXISTS |
| `tools/` | Boundary/TCB/domain-blind/isolation/stale/secrets/E-COV | EXISTS, mixed CI |
| `lab/`, `benchmarkings/` | Measurement / dogfood | EXISTS, not living-CI |

`[FACT]` `pyproject.toml:6-10` — package name `vanguard-runtime`, version `0.4.5b1`,
`requires-python = ">=3.10"`. Console script `vanguard-evaluator` points at
`vanguard.packages.adapters.evaluators.daemon:main`.

`[FACT]` `tools/check_boundaries.py:22` — `PACKAGE_NAMES = {domain, ports, kernel, agency, runtime, adapters, apps}`.
Layer-0 packages are a **second** lattice in the same checker (`LAYER0_PACKAGES`, lines 59–61).

### 3.2 Subsystem map

| Subsystem | packages | layer0 | Status |
|---|---|---|---|
| Event model | `domain/ledger/events.py` | `events/taxonomy.py` + `spi/types_gen.py` | DUPLICATED |
| Canonicalisation | `domain/canonicalisation/` | `events/canonical.py` | DUPLICATED |
| Kernel S0–S12 | `kernel/dispatch.py` (442 physical LOC) | `kernel/dispatch.py` (392 physical LOC, imports `layer0.spi.types_gen`) | DUPLICATED, diverging |
| Effect dispatch | Kernel + `agency/episode/engine.py` | `scheduler/driver.py` `_effect` | DUPLICATED |
| Authorization / attenuation | `kernel/{policy,attenuation,grants}.py` | same names under `layer0/kernel/` | DUPLICATED |
| Budgets / leases | `kernel/budget.py` 6-D Reservation | `kernel/budget.py` | DUPLICATED |
| Scheduler | Episode engine sequential loop | `scheduler/driver.py` SequentialTurnDriver | DUPLICATED; layer0 is the CI subject |
| Episode lifecycle | `agency/episode/` | scheduler emits lifecycle kinds | DUPLICATED |
| Ledger | `adapters/stores/event_store.py` `SqliteEventStore` WAL | `events/store.py` `MemoryLedger` in-memory | packages EXISTS/TESTED; layer0 MOCK/PARTIAL |
| Reducers / fold | `domain/ledger/reducer.py` | `events/fold.py` | DUPLICATED |
| Snapshots | recovery in `runtime/ledger/` | `CHECKPOINT_CREATED` synthetic emit | PARTIAL vs MOCK |
| CAS / blob | `adapters/stores/blob_store.py` | `events/blob.py` | packages EXISTS; layer0 PARTIAL |
| Inbox/outbox | `runtime/service/inbox.py` (ADR-0062) | absent | packages EXISTS; layer0 MISSING |
| Evaluator | `adapters/evaluators/daemon.py` Ed25519 + UDS + UID 10002 | scheduler emits unsigned `"pass"` | packages EXISTS/TESTED; layer0 MOCK |
| Verdict signing | `adapters/evaluators/signing.py` | none | packages EXISTS |
| Plugin registry / lifecycle | manifests under `agency/manifests/` | `registry/lifecycle.py` | layer0 PARTIAL; packages PARTIAL |
| Plugin execution | `adapters/sandbox/toolkit.py` already speaks `layer0.spi.jsonrpc` | `registry/worker.py` echo cell | PARTIAL (seam exists; worker synthetic) |
| SPI / contracts | `ports/` Protocols | `spi/interfaces.py` + `types_gen.py` | DUPLICATED |
| Sandbox | `adapters/sandbox/rootless.py` bubblewrap | `registry/sandbox.py` rlimits | packages EXISTS; layer0 PARTIAL |
| Model providers | OpenRouter, DeepSeek, OpenAI, Ollama, cassette | none | packages EXISTS |
| Context / memory | `agency/context/`, `adapters/stores/memory_engine.py` | SPI fakes only | packages PARTIAL; layer0 MOCK |
| Toolkits | sandbox toolkit + coding pack | `EchoToolkit` | packages EXISTS; layer0 MOCK |
| Selectors | `domain/selectors/resource_selector.py` | `events/selectors.py` | DUPLICATED (import-path fork) |
| CLI | `vanguard/clients/cli` | none | EXISTS, not CI-gated |
| Orchestrator | mixed into `runtime/root.py` (1418 LOC) | compose() only | PARTIAL / GOD-OBJECT |
| Harness composition | `domain/artifacts/manifest.py` `compose()` | `layer0/compose/compiler.py` `compose()` | DUPLICATED |
| Packs | `packs/code-default/` | I-7 forbids coding tokens in layer0 | EXISTS, CI-gated |
| Telemetry / trajectory | SPEC §7 schema; layer0 emits digest-only TrajectoryRef | `scheduler/driver.py` `_trajectory` | PARTIAL |
| Experiment infra | `lab/`, `runtime/lab_driver.py` | none | PARTIAL |
| Multi-agent / spawn | `EpisodeEngine.spawn()` attenuation + causationId | `driver.spawn()` emits CHILD_SPAWNED then immediate CHILD_RETURNED `spans: []` | packages PARTIAL/TESTED; layer0 MOCK |

---

## 4. Test & CI Reality

### 4.1 Commands run on this tree (2026-08-20)

```text
[FACT]
Command: python3 -m unittest discover -s test/layer0 -t .
Result: Ran 25 tests in 0.014s  OK  exit 0
Implication: CI's Layer-0 suite is green. It does not prove packages kernel/runtime.
```

```text
[FACT]
Command: python3 -m unittest discover -s test/packs -t .
Result: Ran 27 tests in 2.140s  OK  exit 0
Implication: code-default pack + I-6/I-7 fixture proofs are green.
```

```text
[FACT]
Command: python3 tools/check_boundaries.py
Result: BOUNDARY PASS: 297 source files checked  exit 0
```

```text
[FACT]
Command: python3 tools/check_tcb_budget.py
Result: TCB PASS: 1347 logical lines across 9 files (alarm above 1438)  exit 0
         baseline 1307, current 1347, threshold 1438
Implication: TCB budget measures vanguard/packages/kernel/*.py only, not layer0/kernel.
```

```text
[FACT]
Command: python3 tools/check_domain_blindness.py
Result: DOMAIN-BLINDNESS PASS: no coding|pytest|ast tokens in layer0/  exit 0
Implication: I-7 is a lexical grep over layer0/ only (tools/check_domain_blindness.py:17-18,54-55).
```

```text
[FACT]
Command: python3 tools/check_isolation_policy.py
Result: ISOLATION POLICY PASS  exit 0
Implication: YAML isolation field check on packs/**/*.yaml, not runtime confinement proof.
```

```text
[FACT — pre-Wave-0 baseline; resolved at Wave 0 (ADR-0075 F-20)]
Command: python3 tools/check_stale_paths.py
Result: STALE PATH FAIL: docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/...
        stale path(s) sprint6B (in archived review file, now deleted)
        exit 1
Implication: living CI job would fail on this tree. Archive review cites a dead path.
```

```text
[FACT]
Command: python3 tools/scan_secrets.py
Result: SECRET SCAN PASS  exit 0
```

```text
[FACT]
Command: python3 tools/check_event_coverage.py
Result: E-COV PASS: 40 kinds, 100% emitter coverage  exit 0
Implication: FALSE CONFIDENCE. The checker greps string literals in declared directories
             (tools/check_event_coverage.py:46-50). VerdictRecorded "emitter" is the
             fabricated pass in layer0/scheduler/driver.py:138-139.
```

```text
[FACT — pre-Wave-0 baseline; resolved at Wave 0 (ADR-0075 F-20)]
Command: python3 -m unittest test.test_repo_paths
Result: Ran 5 tests, FAILED (failures=2)  exit 1
        test_audit_and_governance_from_foreign_cwd — stale sprint6B ref
        test_repo_root_from_this_file — expected sprint6B/preregistered_oracles.json,
          actual docs/03_sprints/evidence/preregistered_oracles.json
Implication: living CI first step (test.test_repo_paths) is red on this tree.
Wave 0 resolution: oracle restored to test/fixtures/preregistered_oracles.json
```

```text
[FACT]
Command: python3 -m unittest discover -s test/kernel -t .
Result: Ran 95 tests in 0.503s  OK  exit 0
Implication: production kernel is green and is **not** in living CI.
```

```text
[FACT]
Command: python3 -m unittest discover -s test/runtime -t .
Result: Ran 400 tests in 26.597s  FAILED (failures=3, skipped=7)  exit 1
        All 3: Ollama absent at 127.0.0.1:11434 labelled provider_unreachable
        vs expected model_tag_absent
Implication: environment-sensitive; not a dispatch-kernel break.
```

```text
[FACT — pre-Wave-0 baseline; resolved at Wave 0 (ADR-0075 F-20, F-21)]
Command: python3 -m unittest discover -s test -t .
Result: Ran 1119 tests in 36.800s  FAILED (failures=7, errors=5, skipped=8)  exit 1
Failures: 2 model-invocation selector kind (process vs generic);
          3 Ollama tag/unreachable;
          2 test_repo_paths (sprint6B).
Errors: 3 model-invocation KeyError args/action;
        2 test_oracle_registry FileNotFoundError (sprint6B path — ghost)
Implication: CLAUDE.md warning that the suite is not fully green is confirmed.
```

```text
[FACT]
Command: wc -l vanguard/packages/runtime/root.py layer0/scheduler/driver.py \
         layer0/kernel/dispatch.py vanguard/packages/kernel/dispatch.py
Result: 1418 / 232 / 392 / 442
```

### 4.2 What CI actually protects

`[FACT]` `.github/workflows/ci.yml` job `vanguard-living-gates` runs:

1. `test.test_repo_paths` — **would fail** (stale sprint-6B ref) **[Wave 0 DONE: oracle at `test/fixtures/`, ADR-0075 F-20]**
2. `test/layer0`
3. `check_boundaries.py`
4. `check_tcb_budget.py`
5. `check_domain_blindness.py`
6. `check_isolation_policy.py`
7. `test/packs`
8. `check_stale_paths.py` — **would fail**
9. `check_markdown_links.py` (not re-run here)
10. `scan_secrets.py`

Not run: `test/kernel`, `test/runtime`, `test/agency`, `test/adapters`, `test/contracts`,
`test/integration`, CLI `npm test`, `check_event_coverage.py` (exists, not in this workflow).

`[INFERENCE]` CI currently certifies the walking skeleton and lexical properties, not the
production hexagonal runtime.

---

## 5. Documentation Authority Map

| Document | Class | Notes |
|---|---|---|
| `docs/SPEC.md` | `[NORMATIVE]` until Concept Lock ADRs supersede cited sentences | v0.5.0 Foundation Lock; says `layer0/` is M1 destination (§1) |
| `docs/04_annex/KERNEL.md` | `[NORMATIVE]` | RFC-2119; "M1 ports verbatim" — destination inverted by ADR-0069 without rewriting S0–S12 |
| `docs/04_annex/MEASUREMENT.md` | `[NORMATIVE]` | no `layer0/` destination claim found |
| `docs/05_adr/0000`–`0068` except `0067` | `[CURRENT DECISION]` / mixed | `0067` is a documented hole |
| `docs/05_adr/ADR-M0-01`…`13` | `[CURRENT DECISION]` | **files exist; INDEX omits them** |
| `docs/05_adr/DEFERRED_REJECTED.md` | `[CURRENT DECISION]` | REJ-01 playbook/DAG; DEF-05 systems language |
| `docs/05_adr/DRIFT_REGISTER_v045.md` | `[HISTORICAL]` | evidence of v0.4.5 drift |
| `docs/01_executive/vision.md` | `[PROPOSAL]` / product vision | not RFC-2119 |
| `docs/02_roadmap/*` | `[HISTORICAL]` planning | next major phase, not this one |
| `docs/03_sprints/sprint_active.md` | execution board | still titled M0 Docs Lock v0.5.0 |
| `principal_engineer_proposal.md` | `[PROPOSAL]` | conceptual north star for v0.6 |
| `vanguard-arquitetura-v4-parecer-e-plano.md` | `[REVIEW]` | empirical diagnosis; commit `99d1e0b` |
| `Vanguard-substrate-060-full-refactor-v3-1.md` | `[PROPOSAL]` | Rust core — **rejected** |
| `vanguard-substrate-060-execution-plan.md` | `[PROPOSAL]` | Python-first useful; `layer0` as production target — **overridden** |
| `aether-v1-roadmap-waves.md` | `[PROPOSAL]` | roadmap — **out of this phase** |
| `docs/07_reviews/TODO_DONT_COMMIT_BEFORE_DOING_IT_v2.md` | procedure for this investigation | not architecture |
| `docs/archive/v045/` | `[HISTORICAL]` | evidence not law (SPEC authority line) |

### 5.1 Explicit contradictions (not silently merged)

| ID | Document A | Document B | As-built Z | SPEC W |
|---|---|---|---|---|
| C1 | Full Refactor: Rust core beside both trees | Execution Plan: Python-first, Rust after gate | No Rust tree exists | Python control plane (ADR-0063); no-systems-language (ADR-0006) |
| C2 | Execution Plan: evolve `layer0` as v0.6 production | Parecer v4 + principal proposal: recover packages | packages has WAL/evaluator/sandbox; layer0 has MemoryLedger | SPEC §1: layer0 is M1 destination |
| C3 | Parecer v4: extract shared nucleus to new `core/` | Principal: no third identity | two trees already | SPEC names both lattices |
| C4 | Parecer Anel 2: Evaluator as product plugin | ADR-0004, ADR-M0-08, SPEC §2.1 | daemon is first-party exterior | judge unreachable |
| C5 | SPEC §2.1 hot-swap mid-run | ADR-0005 freeze at composition | compose() freeze exists; no hot-swap implementation | both sentences currently in law |
| C6 | SPEC I-4 replay-parity CI job | layer0 `test_parity.py` folds the same in-memory list twice | packages has `test/kernel/test_replay_parity.py` but it imports **layer0** fold/driver | "CI job replay-parity" named, not present in `ci.yml` |
| C7 | E-COV 100% = emission proof | E-COV is lexical grep | synthetic VerdictRecorded still "covered" | I-2 emitted=declared |

---

## 6. `vanguard/packages/` vs `layer0/` Forensics

### 6.1 Origin

`[FACT]` git log on `layer0/` includes `d3af6e3 feat(W1): Layer 0, Events and Schemas`,
`f0f7d8f feat(W1): Layer 0, Kernel, Registry`, `baca054 feat(W1): Version 0.6.0 Beta and Gamma`,
`2af33ca feat(W2): Wave 2 Done`.

`[INFERENCE]` `layer0/` is a Wave-1/2 copy-fork intended as the SPEC §1 microkernel, not an
independent historical lineage. Selector files share the same VG-04 docstring; they differ by
import path:

- `layer0/events/selectors.py:37` — `from .canonical import canonicalise, utf16_sort_key`
- `vanguard/packages/domain/selectors/resource_selector.py:37` — `from ..canonicalisation.jcs import ...`

Kernel dispatch: packages documents S0–S12 in the module docstring and uses packages domain
types; layer0 dispatch imports `layer0.spi.types_gen` (`layer0/kernel/dispatch.py:8-9`).

### 6.2 Equivalence matrix

| Concern | `vanguard/packages/` | `layer0/` | Relationship | Evidence | Maturity |
|---|---|---|---|---|---|
| Selectors | `domain/selectors/resource_selector.py` | `events/selectors.py` | copy-fork | docstring identical; import path differs | both real |
| Canonicalisation | `domain/canonicalisation/` | `events/canonical.py` | fork | both claim RFC 8785 | packages is TCB-adjacent; layer0 used by skeleton |
| EffectRequest | domain + ports | `spi/types_gen.py` | DUPLICATED | SPEC I-1 still open (SPEC §8.2) | two types |
| Kernel | `kernel/dispatch.py` 442 LOC | `kernel/dispatch.py` 392 LOC | diverging port | wc -l; import retarget | packages more complete + 95 tests |
| Provenance | `kernel/provenance.py` + engine causationId | `kernel/provenance.py` | fork | engine.py:667-687 | packages wired on spawn path |
| Grants | `kernel/grants.py` | `kernel/grants.py` + `registry/grants.py` ceilings | split | registry/grants.py:16-27 | packages production; layer0 compose path |
| Budget | `kernel/budget.py` | `kernel/budget.py` | fork | ADR-M0-07 6-D | both present |
| Ledger | `SqliteEventStore` WAL | `MemoryLedger` | **not equivalent** | event_store.py:139; store.py:1-12 | packages durable; layer0 test double |
| SQLite WAL | yes | no | unique to packages | PRAGMA journal_mode = WAL | KEEP packages |
| Reducers | `domain/ledger/reducer.py` | `events/fold.py` | fork | replay tests call layer0 fold | both |
| Recovery | `runtime/ledger/` | `driver.recover` emits RUN_RECOVERED | packages richer | driver.py:164-168 | packages KEEP |
| Inbox/outbox | `runtime/service/inbox.py` | absent | unique to packages | ADR-0062 | KEEP packages |
| Evaluator | daemon + signing + isolated | fabricated pass | unique to packages | daemon.py:1-7; driver.py:138-139 | KEEP packages; layer0 defect F1 |
| Signatures | Ed25519 verdicts | none | unique to packages | | KEEP |
| Sandbox | rootless bwrap | rlimits on plugin cell | complementary | rootless.py; registry/sandbox.py | KEEP packages; absorb cell rlimits |
| Plugin runtime | toolkit UDS client already uses `layer0.spi.jsonrpc` | broker + worker | **absorb layer0 wire** | toolkit.py:1-8; jsonrpc.py | promote layer0 codec |
| Scheduler | EpisodeEngine | SequentialTurnDriver | overlap | F1 in driver | keep engine semantics; replace synthetic verdict |
| Model interfaces | `ports/model.py` + adapters | none | unique to packages | | KEEP |
| Composition | `domain/artifacts/manifest.py` + `runtime/root.py` | `compose/compiler.py` | duplicated FrozenHarness | two compose() functions | converge; do not add third |
| Coding-specific | `apps/coding/`, `packs/code-default/` | forbidden by I-7 | unique outside layer0 | | KEEP packs |

### 6.3 Unique / defects

**Keep from packages:** kernel semantics + tests, JCS, WAL ledger, exterior evaluator, sandbox,
stores, models, episode engine `spawn()`, approvals, inbox, recovery.

**Promote from layer0:** SPI Protocols (`spi/interfaces.py`), generated-types direction
(`types_gen.py`), JSON-RPC/UDS (`spi/jsonrpc.py`), isolation broker/cell, lifecycle FSM,
`compose()` digest shape (`mhf.frozen-harness/1`).

**Do not delete layer0 modules until a later parity gate.** `[PROPOSAL]` recorded for Concept Lock,
not executed here.

**Defects still present (re-verified, not inherited from `99d1e0b`):**

- **F1** `[FACT]` `layer0/scheduler/driver.py:138-139` —
  `emit(EventKind.VERDICT_RECORDED, ..., payload={"verdict": "pass"})` with no signed verdict read.
- **F1b** `[FACT]` `FixedGate.gate` ignores verdicts (`layer0/spi/fakes.py:165-167`).
- **F-spawn** `[FACT]` `driver.spawn` (`:170-192`) emits `CHILD_SPAWNED` then immediate
  `CHILD_RETURNED` with `spans: []`. No child episode, no attenuation, no budget conservation.
- **F-ceiling-open** `[FACT]` `layer0/spi/ceiling.py:21-22` — empty capabilities ⇒ `return True`.
- **F-compose-ceiling** `[FACT]` `layer0/compose/compiler.py:54-79` calls `intersect_ceilings` then
  stores `parsed.capabilities` (harness list), not the intersection, on `FrozenHarness`.
- **F-worker** `[FACT]` `layer0/registry/worker.py:113-123` — only `echo` / `fs.read` echo.
- **F-replay-proxy** `[FACT]` `test/layer0/replay/test_parity.py:40-41` —
  `live_state = fold(store.envelopes)` vs `replayed_state = fold(list(store.envelopes))` — same
  in-memory sequence, not cold SQLite replay.
- **God-object** `[FACT]` `runtime/root.py` is 1418 lines: composition, approval resume, sandbox
  bind, evaluator bind, coding entry.

---

## 7. SPEC × ADR × Code × Tests × Proposals Matrix

| Concept | Current SPEC | Active ADRs | As-built | Tests | Tech Lead / principal | Reviews | Conflict / gap | Required decision |
|---|---|---|---|---|---|---|---|---|
| Runtime target | Python; layer0 M1 dest | 0006, 0063 | two Python trees; py 3.10+ | kernel 95 OK not in CI | Python-first; packages canonical | v3.1 Rust; exec plan layer0 dest | C1 C2 | **P0** packages canonical |
| Microkernel boundary | layer0 four things | M0 lattice in SPEC §1 | packages hexagon + layer0 second lattice | check_boundaries 297 files | converge in place | parecer wants `core/` | C3 | **P0** no third tree |
| Events | 40 kinds, E-COV | I-2 | taxonomy in layer0; packages ledger kinds overlap | E-COV lexical 40/40 | behavioral emitters | v3.1 F1 | C7 | lock kinds; reject lexical=proof |
| Ledger | SQLite WAL + JSONL | 0010 | packages WAL; layer0 memory | packages store tests exist | hybrid ES | v3.1 rebuild in Rust | C2 | **P0** keep WAL |
| Authority | kernel mediates effects | 0021, 0051, M0-11 | Kernel.dispatch + engine | test/kernel | decision plane vs ledger | "orchestrator authoritative" language | refine terms | **P0** |
| Scheduler | sequential I-11 | 0007 deferred | EpisodeEngine + SequentialTurnDriver | layer0 driver tests | sequential now | — | dual schedulers | **P0** sequential; one driver later |
| Plugins | lifecycle + isolation | 0005, 0059, M0-13 | worker echo; jsonrpc codec real | test/layer0/registry | wire-first | — | incomplete | **P0** wire; freeze; walking skeleton |
| SPI | five Protocols | M0-03 | layer0 interfaces + packages ports | test/layer0/spi | Protocol is client | parecer: Protocol insufficient | — | **P0** wire is contract |
| Evaluator | exterior daemon | 0004, M0-08 | packages daemon real; layer0 forge | test/adapters/test_evaluator_* | not a product plugin | parecer Anel 2 plugin | C4 | **P0** exterior |
| Storage | WAL + CAS order | 0010 | WAL yes; CAS partial | store tests | CAS for bytes | — | blob/event order | lock hybrid ES |
| Harness identity | FrozenHarness digest | 0005 | two FrozenHarness types | compose tests | D_H only | v3.1 identity incomplete | dual compose | **P0** D_H/D_R/D_X |
| Execution identity | model routes in trajectory | — | not a digest D_R | — | D_R | — | missing | **P0** |
| Project identity | envelope run_id | 0043 episode-bound | causation_id optional; no project_id required | — | envelope fields now | — | missing fields | **P0** envelope |
| Multi-agent | spawn() §6.3 Phase 3 | DEF-03 | packages spawn real; layer0 stub | engine spawn path | Agent=Principal+Harness | swarm engine in some waves | premature engine | **P0** primitive now, engine later |
| Concurrency | I-11 sequential | 0007 deferred | MAX sequential | — | model now, enable later | Rust for races | — | **P0** sequential |
| Replay | I-4 CI job | — | layer0 fold-self; no ci.yml job | test_parity proxy | taxonomy of replay kinds | — | false gate | **P0** taxonomy; real gate later |
| Cache/projections | fold is source | — | `runtime/ledger/projections.py` | some | Projection=f(Ledger) | — | — | lock derived |
| Memory | IMemoryEngine SPI | DEF-02 | sqlite-kv adapter PARTIAL | pack plugins yaml | plugin | — | — | SPI locked; impl later |
| Orchestration | compose + scheduler | — | root.py mixed | — | split later | — | god-object | P1 split root |
| Meta-Harness | Phase 2 plugins §5 | 0019, M0-12 | not implemented | — | defer | waves want it early | — | **P0** defer |
| Experimentation | lab McNemar | MEASUREMENT | lab/ exists | test/lab | D_X | — | — | P1 |
| Distribution | not claimed | — | single node | — | defer | k8s in some docs | — | **P0** defer |
| Rust | not in SPEC v0.5 | 0006, DEF-05 | no Rust | — | evidence gate only | v3.1 wants core now | C1 | **P0** reject rewrite |

---

## 8. Concept & Primitive Inventory

| Concept | Classification | Notes |
|---|---|---|
| Event / EventEnvelope | DUPLICATED | packages domain ledger + layer0 types_gen |
| EffectRequest | DUPLICATED | SPEC I-1 still open |
| Receipt | DUPLICATED | SPI + agency |
| Artifact / ArtifactRef | CANONICAL in packages domain | |
| Principal | AMBIGUOUS | string `principal` on envelopes; not a first-class type everywhere |
| Agent | DOCUMENTED-ONLY in proposals | no type `Agent` |
| Harness / FrozenHarness / HarnessInstance | DUPLICATED | two FrozenHarness dataclasses |
| Episode | CANONICAL in agency | |
| Project | MISSING / PARTIAL | no required `project_id` |
| Task | PARTIAL | lab/oracles |
| Plugin | PARTIAL | yaml + echo worker |
| Skill | PARTIAL | skill cards / skill_index |
| Memory | PARTIAL | SPI + sqlite engine |
| Context | PARTIAL | agency compiler + pack policy |
| Tool / Toolkit | PARTIAL | IToolkit + coding toolkits |
| Model | CANONICAL ports + adapters | |
| Evaluator | CANONICAL packages daemon; MOCK in layer0 scheduler | |
| Ledger | CANONICAL packages SQLite; MOCK layer0 memory | |
| CAS | PARTIAL | blob store |
| Cache / Projection | PARTIAL | projections.py |
| Scheduler | DUPLICATED | |
| Orchestrator | AMBIGUOUS | mixed into root.py |
| Lease / Reservation / Budget | CANONICAL kernel | 6-D |
| Capability | CANONICAL grants + selectors | |
| Spawn | DUPLICATED | real in engine; stub in layer0 |
| ChildPrincipal | PARTIAL | attenuated child scope in engine |
| Trajectory | PARTIAL | schema exists; layer0 digest stub |
| Experiment | PARTIAL | lab |
| Promotion | DOCUMENTED-ONLY | ADR-0015 |
| Meta-Harness | DOCUMENTED-ONLY | SPEC §5 |

Rule applied: do not invent AgentEngine, SwarmEngine, WorkflowEngine, GraphDB, or a third `core/`
package. Correct `Principal`, `HarnessInstance`, `spawn`, and ledger fold.

---

## 9. Multi-Agent & Recursive Agency Readiness

Thesis under investigation (not implemented this phase):

```text
Agent    = Principal + HarnessInstance
SubAgent = ChildPrincipal + HarnessInstance
```

`[FACT]` packages already has `EpisodeEngine.spawn()` (`agency/episode/engine.py:531-591`) with
`attenuate(parent, child)`, depth ceiling, tool filtering, and `causationId` tagging
(`:667-687`).

`[FACT]` layer0 `spawn()` is not recursive agency — it is two events and return.

`[INFERENCE]` One execution abstraction can cover Agent / SubAgent / MetaAgent / swarm participant
**if** swarm is a coordination policy over the same `spawn`, not a new engine. This matches
ADR-0003 (loop, not workflow graph) and ADR-M0-12 (tool ≠ episode).

| Semantic | Classification |
|---|---|
| `project_id` | NEEDED FOR CONCEPT LOCK (envelope) |
| `principal_id` | NEEDED FOR CONCEPT LOCK |
| `parent_principal_id` | NEEDED FOR CONCEPT LOCK |
| `episode_id` | already present; keep |
| `parent_episode_id` | NEEDED FOR CONCEPT LOCK (engine already has param) |
| `harness_digest` | NEEDED FOR CONCEPT LOCK (`D_H`) |
| `causation_id` / `correlation_id` | NEEDED FOR CONCEPT LOCK (optional today in envelope.py:45-47) |
| ownership / budget lineage / capability lineage | NEEDED IN EARLY IMPLEMENTATION |
| evaluation identity | NEEDED IN EARLY IMPLEMENTATION (`D_R`/`D_X`) |
| heterogeneous swarm / market allocator | CAN BE DEFERRED (SPEC §6) |
| MetaAgent distinct engine | RESEARCH ONLY — rejected as engine |

Do **not** implement multi-agent in this phase.

---

## 10. Execution Graph & Causality

Candidate models A–E from the TODO:

`[INFERENCE]` A graph **emerges** from event causality (`spawned_by`, `caused_by`, `produced`,
`evaluated_by`) as a **projection** of the ledger. That is option **D**.

`[FACT]` ADR-0003 rejects a runtime workflow graph. SPEC §1.1 + REJ-01 reject playbook/DAG engines.

Minimum causal semantics needed **now** (concept lock, not a graph database):

- envelope: `causation_id`, `correlation_id`, parent principal/episode, harness digest
- `ChildSpawned` / `ChildReturned` as events, not as a DAG runtime
- projections may later materialize edges; they are not source of truth

No graph database. No workflow engine. `[PROPOSAL]` lock D; reject A/B as core.

---

## 11. Ledger / Event-Sourcing Analysis

Intended invariant: `State = fold(Events)`.

`[FACT]` packages `SqliteEventStore` uses `PRAGMA journal_mode = WAL` (`event_store.py:139`).
`[FACT]` layer0 ledger is `MemoryLedger` (`events/store.py:1-12`).
`[FACT]` SPEC §1.3 names CI job `replay-parity`; it is **not** in `.github/workflows/ci.yml`.
`[FACT]` layer0 replay test folds the same list twice (see §6.3).

Replay taxonomy (must not be conflated):

| Kind | Requirement |
|---|---|
| STATE REPLAY | deterministic reconstruction of grants, budgets, approvals, episode FSM |
| SCHEDULE REPLAY | needs recorded nondeterminism (clock, RNG, model cassettes) |
| REAL-WORLD RE-EXECUTION | not required to match |
| BYTE-DETERMINISTIC FIXTURE | only fully controlled inputs |

`[PROPOSAL]` consistency unit is `project_id`; no global total-order requirement. Snapshots are
optimization. CAS holds bytes; events hold refs. `Projection = f(Ledger)`; `Cache = g(Ledger, CAS)`.

Inbox/outbox (ADR-0062) is packages-only and should survive convergence.

---

## 12. Plugin Architecture Analysis

| Capability | Plugin? | Why |
|---|---|---|
| planner, memory, context, compression, cache strategy, indexing, AST, heuristics, tools, skills, model routing, reflection | **above** plugin line | strategy |
| Meta-Harness strategies | **above**, and **deferred** | SPEC §5 is blueprint not v0.6 impl |
| identity, authority, effect mediation, event semantics, resource conservation, plugin lifecycle, scheduling mechanism | **below** | mechanism / TCB |
| evaluator (the judge) | **below / exterior** | not a replaceable product plugin |
| IEvaluationGate | **above** (requests only) | ADR-M0-03 fifth SPI |
| IModelProvider / ISandbox / stores | first-party ports until a later wave | SPEC §2.2 |

Do not classify everything as a plugin. Do not treat in-process Python objects as the contract.

---

## 13. Plugin Boundary / Polyglot Analysis

| Mechanism | Exists? | Tested? | v0.6 role |
|---|---|---|---|
| Python `typing.Protocol` | yes `spi/interfaces.py` | test/layer0/spi | client convenience, not contract |
| in-process calls | yes | — | isolation **privilege**; must still speak the wire (loopback) |
| subprocess | plugin worker | registry tests | default isolation |
| JSON-RPC 2.0 line-delimited | `layer0/spi/jsonrpc.py` | used by worker + packages toolkit client | **v0.6 wire** |
| UDS | worker bind AF_UNIX; evaluator daemon AF_UNIX | evaluator tests | **v0.6 transport** |
| JSON Schema | `schemas/mhf/` (4 files) + `schemas/v4/` | partial | canonical types |
| JCS | both trees | kernel/canonical tests | identity |
| generated bindings | `types_gen.py` hand-shaped | — | direction locked; drift is a gap |
| Protobuf / gRPC | no | — | not required |
| container / WASM | bwrap exists; wasmtime not default | sandbox tests | container for untrusted exec; WASM deferred |

Semantic boundary (SPI methods) and physical isolation (in_process/subprocess/container/wasm)
are **not** the same thing. v0.6 locks the semantic wire and the freeze-at-composition rule
(ADR-0005). Mid-run hot-swap in SPEC §2.1 is a contradiction and must be struck.

---

## 14. Resource & Concurrency Analysis

`[FACT]` SPEC I-11: Phase-1 scheduler is sequential. ADR-0007 remains deferred.

Logical agents are cheap (principal + harness instance + ledger). Workers are bounded.
`K` active workers `<<` `N` logical agents is a **later** scaling property, not a v0.6 runtime.

Do **not** claim swarm is cheaper by default. Fan-out multiplies model tokens and sandbox cells.

No vector clocks, Merkle DAG, NATS, or Kubernetes in v0.6.

Independence-via-selectors may be **modeled** in proposals now (already on `Proposal` SPI) and
**must not execute concurrently** until a measurement gate.

---

## 15. Authority & Security Boundary Analysis

### SECURITY SEMANTICS REQUIRED NOW (concept lock + early impl)

- Principal identity on every event
- Capability attenuation fail-closed (`Capabilities(child) ⊆ Capabilities(parent)`)
- 6-D budget conservation (`Budget(child) ≼ remaining(parent)`) — ADR-M0-07
- Leases / reservations already in kernel
- Effect mediation through Kernel.dispatch (no second path)
- Exterior signed evaluation; scheduler **reads** verdicts; no fabricated `"pass"`
- Plugin capability ceilings fail-closed (fix `ceiling.py:21-22`)
- Freeze at composition (ADR-0005)
- Provenance / causation envelope fields
- Cancellation / revocation as events (kinds already declared)

### HARDENING THAT MUST NOT BLOCK v0.6

- WASM default isolation
- remote attestation
- distributed trust / multi-host
- complex supply-chain / HSM
- Rust TCB rewrite

`[FACT]` ADR-0004 + ADR-M0-08 already place the evaluator outside the worker. F1 in layer0
scheduler violates that **behaviorally** while E-COV still passes.

---

## 16. Meta-Harness / Self-Improvement Readiness

Candidate lifecycle (Harness H0 → trajectory → mutation → H1 → experiment → exterior eval →
promotion) can reuse: FrozenHarness as genome, ledger trajectories, lab McNemar, exterior judge,
registry pointer as promotion.

`[PROPOSAL]` Do not implement this in v0.6. Structurally anticipate: `mhf.trajectory/1` emission,
`D_H/D_R/D_X`, undeletable baseline, signed verdicts. Explicitly defer: plugin synthesis, core
modification, self-updating release pipeline (ADR-0019, SPEC §9 SA-1…SA-6).

Runtime / memory / composition adaptation are plugin strategies later. Core modification is
rejected.

---

## 17. Gate & Goodhart Audit

| Gate | What a lazy implementation does | Class |
|---|---|---|
| E-COV (`check_event_coverage.py`) | emit string `"pass"` / mention kind in the named directory | **FALSE CONFIDENCE** |
| I-7 domain-blindness | put coding code in `packs/` or `apps/` (allowed) while layer0 stays clean — valid for domain-blindness, **not** proof of a working coding agent | **VALID STRUCTURAL PROOF** (narrow) |
| I-6 isolation YAML | declare `isolation: subprocess` without a confined cell | **WEAK PROXY** |
| `check_boundaries.py` | obey import DAG while shipping synthetic semantics | **VALID STRUCTURAL PROOF** |
| TCB LOC | keep kernel file small while logic lives in root.py (1418 lines, not in TCB glob `kernel/*.py`) | **WEAK PROXY** |
| layer0 replay-parity | fold(list) == fold(same list) | **FALSE CONFIDENCE** |
| living CI layer0+packs | green skeleton, red/ignored production | **FALSE CONFIDENCE** |
| test count 1119 | 7 fail / 5 error ignored by CI | **WEAK PROXY** |
| mutation-score ≥80% (SPEC M1) | not measured here | **UNKNOWN** |
| `replay-parity` CI job (SPEC §1.3) | **does not exist** in ci.yml | **FALSE CONFIDENCE** (named, unenforced) |
| kernel unittest 95 OK | real behavioral proof, **not CI-gated** | **VALID BEHAVIORAL PROOF** (local only) |
| evaluator signing tests | real | **VALID BEHAVIORAL PROOF** (not in living CI) |

Laziest incorrect implementation that still passes living CI today: keep fabricating
`VerdictRecorded: pass`, keep MemoryLedger, never run packages kernel tests in CI.

---

## 18. Critical Technical Debt

1. Dual runtime authority (`packages` vs `layer0`) with CI pointed at the weaker one.
2. F1 synthetic verdict in the CI-gated scheduler.
3. God-object `runtime/root.py` (1418 LOC).
4. Two `FrozenHarness` / two `compose()` / two `EffectRequest`.
5. Capability ceiling fail-open + compose ignoring intersection result.
6. Envelope identity incomplete (`project_id`, parent ids, `harness_digest` not mandatory).
7. E-COV lexical; replay-parity self-fold; missing CI job named in SPEC.
8. Living CI red on stale sprint-6B ref in archive review + oracle path drift. **[Wave 0 DONE: ADR-0075 F-20]**
9. Full suite red (selector `process` vs `generic`; Ollama label; sprint6B).
10. INDEX omits all `ADR-M0-*`; hole at `0067`.
11. `types_gen.py` vs `schemas/mhf/` drift risk (four schemas only).
12. Trajectory record not a first-class durable `mhf.trajectory/1` blob on the packages path.

---

## 19. P0 Decision Registry

These **must** be resolved in Concept Lock (this engagement's next step). Recommended lock is
stated; alternatives are recorded so the lock is explicit, not silent.

### P0-1 Runtime target

- **Question:** Which tree is production? Which language?
- **Why:** Dual authority causes every feature to be implemented twice or in the wrong place.
- **Evidence:** §3–6; kernel 95 OK not in CI; layer0 25 OK in CI; no Rust tree.
- **Alternatives:** (a) packages canonical, absorb layer0; (b) layer0 destination rewrite;
  (c) new `core/`; (d) Rust core.
- **Required by:** Concept Lock
- **Risk of wrong early decision:** third living system or lost WAL/evaluator/sandbox.
- **Lock:** (a) Python 3.10+, `vanguard/packages/` canonical. Rust only behind a later measured
  TCB-hot-path gate. **Reject (b)(c)(d) as v0.6 architecture.**

### P0-2 Dual-tree strategy

- **Question:** Converge, rebuild, or delete one side now?
- **Evidence:** selector copy-fork; MemoryLedger vs WAL; jsonrpc already imported by packages
  adapters.
- **Lock:** Converge. Keep packages implementations. Promote layer0 SPI/broker/lifecycle.
  Delete layer0 duplicates only after a later behavioral parity gate. No wholesale directory
  migration this phase.

### P0-3 Authority

- **Question:** Who decides vs what is true?
- **Lock:** Decision plane (scheduler/orchestrator/kernel) decides who/when/lease/budget/capability.
  Ledger + pure reducers decide what happened. `Decision → DurableEvent → fold → EffectiveState`.

### P0-4 Recursive machine

- **Lock:** `Agent = Principal + HarnessInstance`. SubAgent via `spawn`. Swarm = policy, not
  engine. Graph = event projection (ADR-0003 stands).

### P0-5 Spawn invariants

- **Lock:** `Capabilities(child) ⊆ Capabilities(parent)`; `Budget(child) ≼ remaining(parent)`
  component-wise on 6-D reservation. Envelope fields mandatory on new event kinds: `project_id`,
  `principal_id`, `parent_principal_id?`, `episode_id`, `parent_episode_id?`, `harness_digest`,
  `causation_id`, `correlation_id`. Semantics now; swarm engine later.

### P0-6 Identity trinity

- **Lock:** `D_H` harness composition; `D_R` execution (runtime+env+model+oracle); `D_X`
  experiment cell. FrozenHarness digest is `D_H` only.

### P0-7 Ledger / CAS / replay

- **Lock:** Hybrid ES; SQLite WAL (ADR-0010); snapshots optimization; CAS for bytes; replay
  taxonomy in §11; consistency unit `project_id`.

### P0-8 Plugin boundary

- **Lock:** Wire-first JSON-RPC 2.0 / UDS (ADR-0002, ADR-0059). Five SPIs (ADR-M0-03).
  `in_process` is a privilege. ADR-0005 freeze stands; SPEC hot-swap struck for v0.6.
  Evaluator is not a product plugin.

### P0-9 Evaluator

- **Lock:** Exterior signed judge remains TCB-adjacent. `IEvaluationGate` requests only.
  Fabricating `"pass"` is a defect (F1), not a strategy.

### P0-10 Concurrency

- **Lock:** Sequential execution (`I-11`). Selector independence modeled, not enabled.

### P0-11 CI subject of record

- **Lock:** Production lattice **must** become the CI subject of record. E-COV is not behavioral
  proof. **Implementing** the CI change is the first code-phase task, not this phase.

### P0-12 Deferred by design

- **Lock:** Meta-Harness promotion, self-updating pipeline, WASM default, remote attestation,
  multi-host distribution, graph DB, third control-plane language, pytest-as-universal-runner,
  competence-graph revival, Rust rewrite — all deferred/rejected as v0.6 scope.

---

## 20. P1 Decision Registry

| ID | Question | LOCK NOW or DEFER DELIBERATELY |
|---|---|---|
| P1-1 | Envelope attribution fields on new kinds | **LOCK NOW** (P0-5) |
| P1-2 | Plugin TS conformance suite | **DEFER DELIBERATELY** (implementation wave) |
| P1-3 | pytest migration as universal runner | **DEFER DELIBERATELY** (unittest remains) |
| P1-4 | Split `root.py` | **DEFER DELIBERATELY** to first code wave (needed, not concept) |
| P1-5 | Move model gateway/sandbox behind same plugin wire | **DEFER DELIBERATELY** (first-party ports in v0.6) |
| P1-6 | One generated `EffectRequest` (I-1) | **LOCK NOW** as invariant; codegen is implementation |
| P1-7 | Walking-skeleton echo plugin before product plugins | **LOCK NOW** (ADR-M0-13 already); prove on canonical path in code phase |
| P1-8 | `in_process` loopback still uses JSON-RPC | **LOCK NOW** as rule; impl later |
| P1-9 | Stale sprint-6B CI red | **Wave 0 DONE** — oracle restored to `test/fixtures/preregistered_oracles.json` (ADR-0075 F-20) |
| P1-10 | Ollama unreachable vs `model_tag_absent` | **DEFER** — test isolation, not architecture |
| P1-11 | Selector kind `process` vs `generic` | **DEFER** — contract bug in code phase |
| P1-12 | Fill INDEX `ADR-M0-*` and hole `0067` | **LOCK NOW** (index hygiene is part of Concept Lock) |
| P1-13 | Trajectory blob on every EpisodeCompleted | **LOCK NOW** as requirement; emit in code phase |
| P1-14 | Fail-closed ceilings in FrozenHarness | **LOCK NOW** as requirement; fix in code phase |
| P1-15 | Controlled concurrency enablement criteria | **DEFER DELIBERATELY** (measurement gate, I-11) |

---

## 21. P2 Deferred Decisions

- Heterogeneous subagent packs beyond code-default
- Orchestrator as a distinct process vs module
- Overlayfs vs git-worktree rollback default
- Market-based token budgeting (SPEC §6.2)
- Neuro-symbolic memory graph (SPEC §6.1)
- DPO harvest pipeline productionization
- MCP adapter expansion (ADR-0066 already: never authority)
- CLI as a backend gate (already refused)
- JSONL export format details
- Heartbeat HMAC production keys

---

## 22. P3 Research Topics

- AGI-by-composition hypothesis (principal proposal §1) — hypothesis, not a claim
- WASM component model as default untrusted plugin
- Selective Rust on canonicalization / selector algebra / dispatch hot path — evidence gate only
- Vector clocks / Merkle CRDTs if multi-host ever happens
- Competence graph revival (DEF-02 / D-39)
- Self-modifying release pipeline (permanently refused unless ADR-0019 reversed)

---

## 23. Unknowns / Required Experiments

| ID | Unknown | Experiment (later) |
|---|---|---|
| U1 | Byte-level selector file identity besides imports | `diff` the two selector modules in code phase |
| U2 | Mutation score on kernel+reducers | not run here |
| U3 | Whether packages `test/kernel/test_replay_parity.py` ever hit SQLite | file imports layer0 driver — likely no |
| U4 | Markdown-link gate status | `check_markdown_links.py` not re-run |
| U5 | CLI typecheck/test | not in CI; not run this session |
| U6 | Exact packages vs layer0 dispatch semantic delta | differential tests in convergence wave |
| U7 | Whether `intersect_ceilings` is tested to fail closed when harness ceiling empty | code phase |

---

## 24. Recommended Decision Sequence

```text
1. Adopt P0-1…P0-12 as ADRs 0069–0073 (Concept Lock).
2. Update SPEC.md to v0.6.0; reverse layer0-as-M1-destination; strike hot-swap;
   cite identity trinity, spawn invariants, replay taxonomy, plugin wire.
3. Index ADR-M0-* ; leave 0067 as a hole.
4. STOP. No roadmap, no sprints, no dual-tree deletion, no CI rewire in this phase.
5. Next major phase: as-built gap / migration classification, then a single operational
   plan, then code starting with:
     CI subject-of-record (packages kernel/runtime/agency/adapters + bwrap)
     negative tests (forged verdict, missing grant, capability/budget widening,
       fail-open ceiling, replay divergence, sandbox failure)
     absorb jsonrpc/SPI; kill F1 on the canonical path
     one real coding-agent E2E (model, effect, fs, sandbox, signed eval, WAL, replay,
       trajectory) before heterogeneous agents or Meta-Harness.
```

---

## 25. Final Forensic Conclusions

1. `[FACT]` Two runtimes exist. CI protects `layer0/` + `packs/` + lexical tools, not the
   production hexagonal lattice.
2. `[FACT]` The production kernel test module (`test/kernel`, 95 OK) is outside living CI.
3. `[FACT]` Layer-0 scheduler forges `VerdictRecorded` pass (`driver.py:138-139`). E-COV still
   passes. This is the load-bearing false gate.
4. `[FACT]` Durable WAL ledger, exterior evaluator, and bubblewrap sandbox live in
   `vanguard/packages/`, not in `layer0/`.
5. `[FACT]` Useful layer0 assets already leak into packages (`adapters/sandbox/toolkit.py`
   imports `layer0.spi.jsonrpc`). Convergence has started accidentally; it is not finished.
6. `[FACT]` `docs/SPEC.md` still names `layer0/` as M1 destination and describes mid-run
   hot-swap; ADR-0005 forbids the latter. Law disagrees with itself.
7. `[FACT]` Full unittest suite is red (1119 ran, 7 fail, 5 error) including a living-gate
   stale path (sprint6B oracle, deleted). **[Wave 0 resolved — oracle at `test/fixtures/preregistered_oracles.json`, ADR-0075 F-20]**
8. `[INFERENCE]` Rebuilding Layer 0 from scratch, introducing Rust, or creating `core/` would
   discard working TCB-adjacent code and create a third identity.
9. `[PROPOSAL]` Concept Lock must make packages the production lattice, absorb layer0 contracts,
   keep the evaluator exterior, freeze composition, sequentialise execution, and defer
   Meta-Harness / distribution / WASM / swarm-engine.
10. `[PROPOSAL]` Development may resume only after ADRs `0069`–`0073` and SPEC v0.6.0 exist;
    the first code wave is CI truth + F1 removal + one real coding path — not a new architecture.

The question of this phase was not "which architecture sounds best?"

It was: **what exists, what is law, where they conflict, and which decisions must be locked
before development can safely resume.** Those decisions are listed in §19 and are executed in
`PROMPT_ARCHITECTURE_CONCEPT_LOCK_V060.md` + ADRs `0069`–`0073`.
