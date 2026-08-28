# Vanguard 0.9.0 Backend Audit and Evolution Plan

## 0.9.0b1 delivery followed by 0.9.1 evolutionary simplification

Date: 2026-08-28

Scope: Vanguard backend only

Repository: Aether-D-System

Assessment mode: code-first, evidence-led, non-mutating

Target release horizon: `0.9.0b1`

Evolution horizon: `0.9.1`

---

## Reading contract

This report has exactly two principal chapters.

Chapter I audits the repository as it exists and defines the shortest credible beta path.

Chapter II defines the post-beta evolutionary architecture and refactoring program.

The report does not authorize production changes.

The report does not amend normative law, ADRs, milestones, or the active sprint.

The requested root-level report is the only repository file created by this assessment.

No production source file was modified.

No canonical documentation file was modified.

### Evidence vocabulary

`IMPLEMENTED` means executable production code exists for the claimed behavior.

`VERIFIED` means a reproducible automated check passed in this checkout.

`PARTIAL` means useful behavior exists but an important path or acceptance predicate is absent.

`DOCUMENTARY` means the claim exists in plans, specifications, or evidence metadata only.

`BLOCKED` means a concrete dependency prevents the capability or qualification.

`OBSOLETE` means the mechanism is superseded and should not direct new work.

`FORMAL-ONLY` means the gap affects a signed or scientific claim, not local technical function.

Implementation truth, automated verification truth, milestone status, release integrity, and scientific review are reported separately.

### Investigation constraints

The user prohibited Git commands.

Direct Git commands were not used for repository inspection.

During the audit, two repository evidence scripts were executed once before their internal Git subprocess use was discovered.

Those scripts were `tools/verify_evidence.py` and `tools/check_evidence_acceptance.py`.

No further Git-invoking verification was performed after discovery.

Their results are identified as release-integrity observations, not the sole basis for technical qualification.

The environment did not provide the Python `build` module.

The environment also lacked `venv` bootstrap support through `ensurepip`.

A wheel was therefore built with `pip wheel --no-deps --no-build-isolation` in an isolated temporary copy.

The wheel was installed into a clean target directory and imported from outside the checkout.

This is strong packaging evidence, but not a complete clean-venv acceptance test.

---

# Chapter I — Backend Reality Audit and the 0.9.0b1 Delivery Horizon

## 1. Executive verdict

### 1.1 Decision

Do not delete Vanguard.

Do not start from scratch.

Finish the beta on the current event-native foundation.

Then simplify it through measured, compatibility-preserving refactoring.

The repository already contains a technically serious substrate:

- a domain-blind authorization kernel;

- monotonic capabilities and typed budgets;

- append-only causal event storage;

- event-derived state reconstruction;

- content-addressed artifact capture;

- durable SQLite-WAL continuation;

- a recursive agency loop;

- child scopes and lineages;

- profile-resolved composition;

- pack and plugin mechanisms;

- model, environment, evaluator, event-store, and blob-store ports;

- reference coding and explanation manifests;

- a service API with inspection and resume operations;

- extensive falsifier-oriented tests.

Rewriting would discard the most expensive and differentiated work while recreating the same hard invariants.

The problem is not an irrecoverable core.

The problem is the gap between a capable substrate and a coherent, installable product surface.

The beta should prove this vertical slice:

```text
install
→ configure
→ run a useful workflow
→ inspect events and artifacts
→ interrupt the process
→ resume from durable state
→ verify the result
```

Today, pieces of that slice exist across the CLI, runtime entrypoint, service, manifests, and tests.

They are not yet presented as one authoritative backend product path.

### 1.2 What is valuable and must survive

The event ledger is real, not aspirational.

The capability and budget spine is real, not aspirational.

The reducer and recovery model are real, not aspirational.

Artifact capture performs blob-first persistence followed by causal-reference emission.

Prompt bundles and raw model output already cross the artifact boundary.

The runtime already expresses both direct agent turns and nested spawning through one episode engine.

The canonical manifest-to-composition chain exists.

These are precisely the components a greenfield rewrite would struggle to reproduce safely.

### 1.3 What is making the product feel unfinished

There are multiple entry and bootstrap paths.

The standalone CLI exposes `init`, `doctor`, and `run`, but not the complete operational vocabulary.

The richer JSON entrypoint and service expose overlapping but different capabilities.

`Runtime.execute_harness` remains a legacy composition path beside `execute_profiled` and `run_composed`.

Model selection exists in more than one place.

Manifest and pack loading have multiple representations and compatibility seams.

Execution profiles bundle orthogonal concerns into identity-bearing presets.

Plugin lifecycle machinery exists, but portable product discovery and operational lifecycle are incomplete.

Milestone status has drifted from executable truth.

Evidence acceptance has sometimes been treated as product validation.

The current version is still `0.7.3.dev0`, not `0.9.0b1`.

The available reference workflows prove reachability more clearly than usefulness.

### 1.4 Beta conclusion

`0.9.0b1` is achievable without architectural reinvention.

It requires a bounded productization milestone, not another research wave.

The beta is technically qualified when automated acceptance proves the vertical slice.

Independent human countersignature is optional for local technical qualification.

It remains appropriate for formal release attestation or scientific claims.

### 1.5 0.9.1 conclusion

`0.9.1` should be an evolutionary consolidation release.

Its goal is one product entry path, one bootstrap authority, one logical event contract, and optional expensive research machinery.

Its public mental model should be:

```text
Observe → Decide → Authorize → Execute → Record
```

The kernel may retain its deeper S0–S12 implementation internally.

## 2. Verified repository baseline

### 2.1 Authority and documentation map

The repository establishes a clean documentation triad in `AGENTS.md` and `README.md`.

Normative law lives in [`docs/SPEC.md`](docs/SPEC.md) and [`docs/01_law/`](docs/01_law/).

Accepted decisions live in [`docs/02_decisions/`](docs/02_decisions/).

Current execution status lives in [`docs/03_execution/sprint_active.md`](docs/03_execution/sprint_active.md).

Macro gates live in [`docs/03_execution/milestones.md`](docs/03_execution/milestones.md).

Upcoming work lives in [`docs/03_execution/sprint_upcoming.md`](docs/03_execution/sprint_upcoming.md).

The current backlog is [`docs/03_execution/backlog.md`](docs/03_execution/backlog.md).

Historical phase-one materials were resolved under `docs/_archive/reviews/backend/`.

The audit used those materials as claims and rationale, never as current authorization.

### 2.2 Requested historical sources resolved

The phase-one assessment is at `director_review_v0/AETHER_PHASE1_ASSESSMENT.md`.

The historical phase-one ADR proposal is at `director_review_v0/ADR-0097-phase1-foundation-review-and-concept-lock.md`.

The architecture delta is at `director_review_v0/ARCHITECTURE_DELTA.md`.

No archived `BACKLOG.md` matching the requested exact name was found in the review tree.

The canonical current backlog at `docs/03_execution/backlog.md` was used.

The milestone specifications are at `director_review_v0/MILESTONE_SPECS.md`.

The M4 trajectory specification is at `director_review_v0/SPEC_M4_TRAJECTORY_CAPTURE.md`.

The M5a event-derived agent specification is at `director_review_v0/SPEC_M5A_EVENT_DERIVED_AGENT.md`.

The M5b/M6 specification is at `director_review_v0/SPEC_M5B_M6.md`.

The M6.5/M7/M8 specification is at `director_review_v0/SPEC_M65_M7_M8.md`.

The historical development plan is at `director_review_v0/DEVELOPMENT_PLAN.md`.

The historical active sprint is at `director_review_v0/SPRINT_ACTIVE.md`.

The revised master plan is at `director_review_v1/masterplan_todo_rev1.md`.

No separate archived `SPRINT_UPCOMING.md` matching the requested name was found.

The canonical current upcoming sprint was used instead.

### 2.3 Production inventory

Production code is rooted at [`vanguard/packages/`](vanguard/packages/).

The audit counted 205 production Python modules.

The audit counted approximately 45,455 physical Python lines across production packages.

The test tree contains approximately 254 Python test modules.

The kernel logical TCB count is 1,373 lines.

The enforced budget is 1,438 lines.

The largest observed backend modules include:

- `runtime/session.py`: 1,401 physical lines;

- `runtime/service/service.py`: 1,343 physical lines;

- `domain/artifacts/manifest.py`: 1,057 physical lines;

- `adapters/models/openrouter.py`: 995 physical lines;

- `adapters/environment/git.py`: 955 physical lines;

- `domain/ledger/reducer.py`: 820 physical lines;

- `runtime/delegation.py`: 771 physical lines;

- `agency/episode/engine.py`: 761 physical lines;

- `runtime/service/studio_gateway.py`: 710 physical lines;

- `domain/wire/types_gen.py`: 706 physical lines;

- `runtime/root.py`: 699 physical lines;

- `runtime/artifacts.py`: 689 physical lines.

Large size is a review signal, not automatic evidence of bloat.

Each module is assessed by responsibility and consumer below.

### 2.4 Package identity and build metadata

[`pyproject.toml`](pyproject.toml) names the distribution `vanguard-runtime`.

Its current version is `0.7.3.dev0`.

It requires Python 3.10 or newer.

Runtime dependencies are `cryptography>=41` and `jsonschema>=4.23`.

Console scripts include `vanguard`, evaluator, daemon, and studio entrypoints.

Setuptools discovers `vanguard*`, `schemas*`, and `packs*`.

Package data includes JSON, YAML, Markdown, text, CNF, HTML, JavaScript, CSS, source maps, SVG, JCS, and digest files.

This metadata is broadly aligned with resource packaging.

The release identity is not aligned with the requested beta.

### 2.5 Automated checks reproduced

The full suite observation available during this assessment was:

- 2,150 tests run;

- 1 failure;

- 9 skips.

The sole failure was an execution-truth/document-state assertion.

It was not a production-runtime behavior failure.

Focused kernel tests passed 94 of 94.

Focused agency tests passed 105 of 105.

Reference workflow tests RF-90 and RF-91 passed 6 of 6.

Focused evidence capture, resume, runtime service, and M8 turn-loop tests passed 97 of 97.

The M8 proof runner passed 59 tests and all 34 proof markers.

The M7 topology proof runner currently failed 6 of 40 tests in its deliberately sparse environment.

The same 40 tests passed in the ordinary checkout environment.

The six failures were concentrated in `test_m701_recorded_workload`.

The sparse run terminated `ABANDONED` after two effects rather than `COMPLETED` after three.

This is a reproducibility or environment-hermeticity defect in qualification.

It does not erase the topology implementation.

It does prevent claiming a completely green current M7 proof.

### 2.6 Architecture and security linters reproduced

`python3 tools/linters/check_boundaries.py` passed 414 import checks.

`python3 tools/linters/check_tcb_budget.py` passed at 1,373 of 1,438 logical lines.

`python3 tools/linters/scan_secrets.py` passed.

`python3 tools/linters/check_domain_blindness.py` passed, with its existing layer-zero warning.

`python3 tools/linters/check_isolation_policy.py` passed.

`python3 tools/linters/check_event_coverage.py` passed.

`python3 tools/linters/check_duplication.py --enforce` passed.

Passing the duplication linter does not mean responsibility overlap is absent.

It means prohibited textual duplication was not detected under that tool's rules.

### 2.7 Evidence and board observations

Current successor bundles for M4, M6, M6.5, M7, and M8 were reported as passing by the evidence verifier.

The historical M5b bundle was reported as failing.

M5a did not have the expected release bundle or tag identity.

The execution-truth checker reported status drift involving WP-A3, WP-A4, WP-B2, and WP-B4.

The active board and package ledger do not consistently represent the same lifecycle state.

This is release-integrity debt.

It is not proof that the corresponding runtime code is absent.

### 2.8 Packaging experiment

`python3 -m build` could not run because the `build` module was absent.

A temporary source copy was created outside the repository.

`python3 -m pip wheel . --no-deps --no-build-isolation` succeeded there.

The wheel was named `vanguard_runtime-0.7.3.dev0-py3-none-any.whl`.

The wheel size was 1,648,129 bytes.

The observed SHA-256 began `40c06ca4`.

The wheel included 566 schema, manifest, pack, migration, or related resource entries.

Installation into a clean target directory succeeded.

Import from outside the checkout succeeded when only that target was on Python's import path.

The installed default manifest resolved from within the installed package.

Installed fake-model `code` and `explain` executions reached completion.

Both completed by selecting `finish` in a single turn.

This proves packaging reachability.

It does not prove useful coding or explanation behavior.

A clean virtual environment could not be created because `ensurepip` was unavailable.

An sdist was not produced in this audit.

Offline-after-install acceptance therefore remains incomplete.

## 3. Previous-review claims: confirmed, falsified, or unverified

| Claim | Verdict | Concrete evidence | Consequence |
|---|---|---|---|
| The kernel is within its TCB budget | CONFIRMED | `check_tcb_budget.py`: 1,373/1,438 | Preserve the kernel boundary |
| Hexagonal boundaries are enforced | CONFIRMED | `check_boundaries.py`: 414 checks passed | Do not flatten layers |
| The full suite is green | FALSIFIED | 2,150 run, one execution-truth failure | Repair documentary/status drift |
| M4 trajectory capture exists | CONFIRMED | capture code, focused tests, current proof bundle | Productize rather than rebuild |
| `CONVERGENCE-BASE-v1` is missing | CONFIRMED as release identity | no qualifying M5a baseline evidence found | Repair formal lineage separately |
| M5a agent state is absent | FALSIFIED | reducer, AgentView, reconstruction, checkpoint tests | Technical capability exists |
| M5b evidence is valid | FALSIFIED | historical bundle fails current verification | Re-run or supersede only if release needs it |
| Recursive execution is only documentary | FALSIFIED | `EpisodeEngine.spawn`, recursion tests, M6 evidence | Preserve and demonstrate it |
| M7 is currently fully qualified | FALSIFIED | sparse proof environment fails 6/40 | Fix qualification hermeticity |
| M7 topology code is missing | FALSIFIED | ordinary environment passes 40/40 | Do not rebuild topology |
| M8 execution is unimplemented | FALSIFIED | M8 runner 59/59 and 34 markers | Treat as implemented |
| M8 product usability is proven | UNVERIFIED | proof runner is not install/run/resume UX | Add beta vertical slices |
| M9 packaging is ready | FALSIFIED | wrong version, no sdist, incomplete clean install | M9 is the actual beta focus |
| Capture profiles necessarily discard prompts | FALSIFIED | `ArtifactWriter` captures prompt/context/output | Keep cheap capture |
| Research requires a separate engine | FALSIFIED | runtime already supports policies/evaluators/artifacts | Add interceptors, not an engine |
| A general workflow engine is required now | UNVERIFIED | operations, events, spawn, topology already compose flows | Validate before adding machinery |
| Runtime duplication is imaginary | FALSIFIED | legacy and profiled execution paths coexist | Consolidate after beta |
| Runtime duplication makes rewrite necessary | FALSIFIED | duplication is localized behind usable contracts | Evolve incrementally |
| Bidirectional PTY is required for every coding agent | FALSIFIED | non-interactive edit/test flows can run without it | Defer unless beta scenario proves need |

## 4. Backend architecture and production-path map

### 4.1 Package dependency lattice

```text
domain ← ports ← kernel ← agency ← runtime → adapters
                         ↑
                       apps client slot
```

[`vanguard/packages/domain/`](vanguard/packages/domain/) contains pure values, wire contracts, canonicalization, reducers, evidence, and selectors.

[`vanguard/packages/ports/`](vanguard/packages/ports/) defines kernel, model, sandbox, evaluator, event-store, blob-store, environment, determinism, index, and SPI protocols.

[`vanguard/packages/kernel/`](vanguard/packages/kernel/) owns authorization, capability attenuation, budgets, policy, settlement, and provenance.

[`vanguard/packages/agency/`](vanguard/packages/agency/) owns recursive turn semantics, context compilation, compaction, and spawning.

[`vanguard/packages/runtime/`](vanguard/packages/runtime/) owns composition, lifecycle, adapter wiring, governance integration, event emission, evaluation, services, and persistence selection.

[`vanguard/packages/adapters/`](vanguard/packages/adapters/) contains concrete models, environments, sandboxes, evaluators, and stores.

The dependency direction is coherent and verified.

### 4.2 Intended production path

```text
client or service request
→ canonical manifest parsing
→ frozen composition
→ activation plan
→ execution profile resolution
→ run plan
→ HarnessSession / EpisodeEngine
→ model proposes an operation
→ kernel authorizes and reserves budget
→ adapter executes the effect
→ receipt settles the reservation
→ ledger emitter appends causal events
→ artifact writer persists large bytes and emits references
→ reducer derives AgentView and recoverable state
→ result, telemetry, and artifact references return
```

The manifest chain is documented and implemented around `Runtime.compose`.

The deep authorization pipeline stays internal to the kernel.

The public path can still be explained in five verbs.

### 4.3 Actual entry surfaces

The standalone CLI in `vanguard/cli.py` exposes `init`, `doctor`, and `run`.

The JSON entrypoint in `vanguard/entrypoint.py` supports code, explain, resume, and doctor behaviors.

The runtime service exposes listing, events, artifacts, cancellation, resume, and checkpoint operations.

The studio gateway overlaps some service behavior.

These surfaces do not yet share one complete command model.

The beta should choose one authoritative backend application service.

CLI, stdio JSON, and future transports should call that service.

### 4.4 Runtime execution paths

`Runtime.execute_harness` is explicitly legacy.

It still performs environment and adapter setup directly.

It defaults to an in-memory SQLite store when the caller does not provide one.

`Runtime.execute_profiled` delegates environment and store selection to `RuntimeBootstrap`.

`Runtime.run_composed` executes the resolved composition.

`RuntimeBootstrap.build` is the intended concrete-adapter authority.

It defaults durable profiles to `.vanguard/events.sqlite3` under the repository.

It selects an in-memory store only when the requested profile names memory persistence.

The coexistence is a compatibility seam with real callers.

It should be migrated and removed after beta contract freeze.

### 4.5 Events and projections

The canonical domain envelope is `domain.ledger.events.EventEnvelope`.

Generated wire types also define `EventEnvelope` and `EventEnvelopeV2`.

`LedgerEmitter` single-writes the `/2` form.

Readers retain `/1` and `/2` compatibility.

The reducer in `domain/ledger/reducer.py` derives episode, goals, leases, capabilities, effects, plans, and context facts.

The event store is the authority.

Checkpoints are explicitly caches with proof obligations.

This is the correct semantic model.

The duplication risk is representational drift between domain and generated wire classes.

### 4.6 Artifacts and hashing

`ArtifactWriter.capture` persists bytes before emitting the artifact fact.

The content address is computed over retained bytes.

The ledger receives references and metadata, not large payloads.

An event-emission failure after blob persistence can leave an orphan blob.

That is safe for causal integrity and requires garbage collection.

Hashing or persistence cannot be moved after causal reference emission.

Serialization and hashing may run off the critical path only if settlement waits before the reference becomes authoritative.

### 4.7 Agency, topology, and workflow

`EpisodeEngine.run` implements the recursive turn loop.

`EpisodeEngine.spawn` attenuates child scope and authority.

Topology is lowered to spawn operations rather than a second executor.

The current reference path is sequential where causal dependencies require it.

Operations, events, child scopes, bounded turns, and terminal outcomes already constitute a minimal workflow language.

A direct loop, ReAct-like loop, planner/executor, critic/reviser, and fan-out can be represented by policies and manifests.

The beta should prove three compositions before inventing a general workflow DSL.

### 4.8 Context and compaction

The context compiler implements stable L1–L5 layering.

Prompt bundles are captured before provider invocation.

Compaction policy selection is replaceable through a registry.

The recency and result-eviction policies are adequate for beta.

The structured consolidation policy uses simple textual heuristics.

An unknown compaction policy silently falls back to recency.

That fallback is too permissive for an identity-bearing configuration.

It should fail closed in 0.9.1 or resolve explicitly to an identified default.

### 4.9 Plugins and registry

The port layer contains stable-looking SPI protocols.

Registry lifecycle code models verification, activation, health, quiescence, initialization, and shutdown.

Pack and plugin manifests exist.

The current product path does not yet prove discovery, activation, failure quarantine, upgrade, rollback, and removal as one lifecycle.

Some registry data is metadata without demonstrated runtime consumers.

The beta needs a minimal, deterministic discovery and activation proof.

It does not need a marketplace or remote distribution system.

### 4.10 Transport position

The logical contract is already close to:

```text
Command → ordered Event Stream → Result + Artifact References
```

The service and stdio entrypoint demonstrate more than one invocation form.

Transport equivalence is not yet proven as a comprehensive contract suite.

Local calls should pass typed objects without serialization.

Transport adapters must serialize only at their boundaries.

Distributed settlement, idempotency, causal ordering, and budget identity need later contract tests.

They do not require a distributed transport in the beta.

## 5. Milestone M-1 through M-9 truth matrix

| Milestone | Code implemented | Tests passing | Evidence valid | Product-visible capability | Actual blocker | Required action |
|---|---:|---:|---:|---:|---|---|
| M-1 trust spine | Yes | Yes | Historical/current accepted | Low-level | None technical | Preserve and smoke-test |
| M-2 trajectories and continuation | Yes | Yes | Accepted successor evidence | Partial | Product UX not unified | Exercise in beta vertical slice |
| M-3 canonical composition | Yes | Yes | Accepted | Partial | Compatibility paths remain | Freeze canonical path, defer cleanup |
| M-4 trajectory capture | Yes | Yes | Current successor passed | Partial | Reference usefulness unproven | Capture real workflow artifacts |
| M-5a event-derived agent | Yes | Focused behavior passes | Missing baseline identity | Indirect | Formal release lineage | Separate technical qualification from baseline repair |
| M-5b convergence experiment | Yes/experimental | Relevant mechanisms exist | Historical evidence invalid | No | Invalid experiment evidence | Supersede only if beta claim requires it |
| M-6 recursive execution | Yes | Yes | Current successor passed | Partial | Product demonstration | Add multi-role reference run |
| M-6.5 adaptive behavior | Yes/limited | Yes | Current successor passed | Low | Not beta-critical | Preserve, do not expand |
| M-7 topology | Yes | 40/40 normal; 34/40 sparse | Prior bundle passed, current runner regressed | Partial | Qualification hermeticity | Fix sparse-environment reproduction |
| M-8 native turn loop | Yes | 59/59 runner | Current successor passed | Partial | Product vertical slice | Use same runtime for reference workflows |
| M-9 beta productization | Partial | Fragmentary | Not qualified | No coherent whole | Packaging, CLI/API, workflows, recovery proof | Execute Horizon 1 |

### 5.1 M-1 and M-2

The kernel authorization spine and typed budget algebra are implemented.

The event ledger and reducer support causal reconstruction.

Fresh-process SQLite-WAL continuation has dedicated tests.

These milestones should not be reopened conceptually.

They should be included in release smoke coverage.

### 5.2 M-3 and M-4

Canonical composition and trajectory capture are implemented.

Prompt, context, model output, tool, patch, verification, and checkpoint artifact roles exist.

The remaining beta question is operational integration.

Can an installed user run a useful composition and inspect the captured result?

Milestone evidence alone does not answer that question.

### 5.3 M-5a

Event-derived state is technical reality.

The missing `CONVERGENCE-BASE-v1` issue is a release-identity and evidence-lineage gap.

It must not be described as missing AgentView implementation.

For beta, either create a new automated baseline under the actual release identity or explicitly waive the historical scientific lineage.

Do not fabricate a retroactive tag or countersignature.

### 5.4 M-5b

The historical convergence evidence is invalid under the current verifier.

That invalidates the formal experimental claim.

It does not automatically invalidate all later runtime mechanisms.

If `0.9.0b1` makes no convergence-science claim, M5b re-execution is optional.

If release notes claim experimental convergence, a fresh identified experiment is mandatory.

### 5.5 M-6 through M-8

Recursive execution, topology lowering, and the native turn loop exist in code.

Later technical functionality can remain accepted even if an earlier documentary predicate drifted.

Formal milestone lineage may still be inconsistent.

The correct response is dual accounting:

- technical capability status remains based on executable proof;

- formal release lineage remains conditional on its declared predecessors.

M7 currently needs a qualification-runner fix because the sparse environment reproduces six failures.

M8 currently reproduces cleanly.

### 5.6 M-9

M9 is incomplete.

The wheel can be built and installed, but release identity is wrong.

The CLI is not operationally complete.

The sdist was not reproduced.

The clean-venv offline test was not reproduced.

The reference workflows do not yet prove useful outputs.

The kill-and-resume product path needs one end-to-end acceptance fixture.

## 6. Beta product gap analysis

| Product item | Status | Evidence | Beta disposition |
|---|---|---|---|
| One authoritative version source | Missing | `pyproject.toml` still `0.7.3.dev0`; other version surfaces exist | Required |
| Reproducible wheel | Partial | temporary wheel built successfully | Add deterministic CI comparison |
| Reproducible sdist | Unverified | `build` module absent | Required |
| Clean install outside checkout | Partial | target install/import passed | Add fresh venv/container test |
| No hidden `PYTHONPATH` dependency | Partial | installed target worked, but path injection was needed | Prove via installed console script |
| Explicit state directory | Partial | profiled runtime uses `.vanguard`; legacy path can use memory | Required on product path |
| No silent in-memory fallback | Partial | bootstrap is explicit; legacy executor defaults memory | Remove product access to legacy default |
| Packaged schemas/manifests | Mostly complete | wheel contained resources | Add resource enumeration test |
| Packaged migrations | Mostly complete | resources present | Add fresh/upgrade DB tests |
| Unified composition | Partial | canonical path exists; legacy path remains | Route beta surfaces through bootstrap |
| `run` command/API | Implemented | CLI/service/entrypoint | Normalize semantics |
| `resume` command/API | Partial | service and entrypoint, not standalone CLI | Required |
| `status` command/API | Partial | service capability, no CLI parity | Required |
| `events` command/API | Partial | service stream, no CLI parity | Required |
| `artifacts` command/API | Partial | service retrieval, no CLI parity | Required |
| Health vs readiness | Partial | service diagnostics exist but semantics overlap | Define typed endpoints |
| Redacted typed diagnostics | Partial | structured diagnostics exist | Add contract/redaction tests |
| Plugin discovery | Partial | manifests and registry exist | Minimal deterministic lifecycle required |
| Plugin activation lifecycle | Partial | verify/activate/init/shutdown exists | Prove failure behavior |
| Kill-and-resume | Mechanism implemented | reconstruction and resume tests | Product E2E required |
| Offline after install | Missing proof | fake/local adapters exist | Required |
| Coding reference workflow | Partial | code and lex manifests exist | Must perform real inspect/edit/verify task |
| Non-coding workflow | Partial | code-explain exists | Must emit useful structured explanation |
| Multi-role workflow | Partial | spawn/topology implemented | Demonstrate without kernel changes |
| Bidirectional PTY | Missing | sandbox uses captured pipes and `DEVNULL` stdin | Not beta-required for scoped workflows |

### 6.1 Beta scope boundary

The beta coding workflow may use non-interactive tools.

It must read files, search, propose or apply a bounded patch, run a deterministic verification, and finish.

It does not need to operate full-screen terminals.

It does not need to answer interactive password or authentication prompts.

It does not need shell job control.

Therefore bidirectional PTY streaming is not a beta blocker.

If the selected reference workflow includes an interactive REPL or TUI, the scope decision changes.

### 6.2 Reference product proofs

`Lex-Minimal` should be a Vanguard-native manifest and reusable policy composition.

It should not import Lex as an alternate engine.

`Codebase-Explainer` should use the same runtime, event store, artifact writer, and context compiler.

It should differ through tools, context strategy, policy, evaluator, and workflow configuration.

The multi-role proof should compose planner, executor, and reviewer roles through child scopes.

It should not introduce a topology executor beside `EpisodeEngine`.

## 7. Bloat, duplication, and responsibility map

| Area | Evidence | Invariant/consumer | Runtime cost | Decision |
|---|---|---|---|---|
| `Runtime.execute_harness` | legacy docstring and inline setup | compatibility callers | duplicate setup and memory default risk | Migrate, then remove in 0.9.1 |
| `Runtime.execute_profiled` | bootstrap-backed path | product execution | appropriate | Retain |
| CLI vs entrypoint vs service | overlapping verbs | different clients | semantic drift | Consolidate behind application service |
| Model factories | bootstrap, CLI, entrypoint, selection modules | multiple clients | configuration drift | Unify after beta |
| Manifest loaders | canonical parser, agency loader, named parser, pack YAML | compatibility and distinct formats | cognitive and validation cost | Inventory consumers, converge gradually |
| Event envelope classes | domain and generated wire types | wire compatibility | conversion/drift risk | One logical model plus codecs |
| Service event outbox | compatibility fallback beside canonical store | service legacy | duplicate publication risk | Instrument and retire fallback |
| Execution profile | bundles many axes | run identity and assurance | config coupling | Split logical axes, keep resolved digest |
| `runtime/session.py` | 1,401 lines | central lifecycle | review and change risk | Extract by responsibility without behavior change |
| `runtime/service/service.py` | 1,343 lines | operational API | review and coupling risk | Separate command/query/application layers |
| `domain/artifacts/manifest.py` | 1,057 lines | canonical composition | parsing/validation concentration | Split internal helpers, preserve contract |
| OpenRouter adapter | 995 lines | provider integration | provider-specific complexity | Split protocol, streaming, accounting helpers |
| Git environment adapter | 955 lines | workspace effects | security-sensitive size | Split read, diff, apply, process concerns carefully |
| Reducer | 820 lines | causal source of derived state | central fold cost | Preserve authority; profile performance |
| Delegation | 771 lines | topology and subagent orchestration | legitimate complexity | Retain, simplify only with tests |
| Plugin registry metadata | fields with limited runtime consumption | future lifecycle | startup and cognitive overhead | Remove only after consumer census |
| Governance boards | duplicated lifecycle labels | traceability | development drag, not hot-path latency | Reduce status duplication |

### 7.1 Duplicate validation

Manifest validation occurs at parsing, canonicalization, composition, and activation boundaries.

Some repetition protects trust-boundary transitions.

Some repetition merely rechecks already typed in-process objects.

The audit does not recommend deleting validation wholesale.

The 0.9.1 rule should be:

- validate untrusted bytes at ingress;

- validate authority-sensitive transitions at the kernel boundary;

- preserve schema compatibility checks at transport and persistence boundaries;

- avoid reserializing and revalidating immutable typed objects inside one process.

### 7.2 Governance in the hot path

Signed approvals and evaluator verdicts protect real authority transitions.

They are not mere paperwork when the configured profile requests them.

Evidence bundles, review countersignatures, experiment promotion, and board transitions are not required in an ordinary local run.

The product runtime should not consult documentation state.

The audit found documentary status drift, not evidence that Markdown directly controls normal effect execution.

### 7.3 Dead and obsolete paths

Compatibility code should not be labeled dead until consumers are enumerated.

`execute_harness` is obsolete in direction but still potentially live in tests or clients.

`mhf.event/1` readers are compatibility support and cannot be removed before an upgrade window is declared.

Metadata-only plugin fields are candidates, not confirmed dead code.

The beta must add usage instrumentation or static consumer reports before deletion.

## 8. Capture, telemetry, recovery, evaluation, and retention audit

### 8.1 Existing capture truth

The runtime already captures the final compiled prompt bundle.

It already captures raw structured model output immediately after provider return.

It supports context bundle, compaction output, patch, verification report, and checkpoint roles.

Standard retention includes valuable operational artifacts.

Full retention expands content retention.

Digest-only retention intentionally omits original bytes.

A `blobs=None` composition captures no artifact bodies.

That is valid for legacy or explicitly ephemeral execution.

It must not occur silently on the product profile when capture is required.

### 8.2 Correct identity sequence

```text
capture original bytes
→ apply declared redaction policy
→ persist retained bytes
→ compute or receive their content address
→ emit the causal artifact reference
→ allow settlement/result publication
```

If original bytes are not retained, their later reconstruction is impossible.

A digest can be recomputed later only when identical bytes remain available.

Asynchronous storage is acceptable only behind a completion barrier.

An uncommitted future or queue token is not a durable causal reference.

### 8.3 Existing axis coupling

`ExecutionProfile` combines workspace, process backend, network, approval, persistence, evaluation, assurance, retention, and capture.

The fields are individually represented.

The presets still make them behave as bundled operating modes.

This is better than a single scalar trust tier.

It is not yet the orthogonal product configuration requested for 0.9.1.

### 8.4 Beta policy

The product beta should retain prompts, compiled context, outputs, tool requests/results, patches, causal events, model identity, usage, workflow boundaries, and recovery facts by default.

Large bytes should stay in the blob store.

The ledger should retain digests, roles, causal identifiers, sizes, and policy metadata.

Mutation testing, repetitions, external evaluation, adversarial checks, environment replication, signed evidence, and long-term retention remain opt-in.

### 8.5 Observer versus controller

No universal lifecycle interceptor contract was found for all of:

- `before_operation`;

- `after_operation`;

- `on_event`;

- `before_commit`;

- `after_result`;

- `on_failure`.

Ad hoc observation and control seams exist.

They include dispatch observation, model wrappers, meta-controller directives, evaluator decisions, provenance, and terminal callbacks.

Logging must remain observer-only.

Control plugins need explicit capability and a closed decision vocabulary.

The 0.9.1 vocabulary should be `ACCEPT`, `REJECT`, `RETRY`, `REDIRECT`, `FORK`, and `STOP`.

Unsupported decisions must fail closed.

## 9. Performance and storage measurements

### 9.1 Measurement conditions

Host: Linux under WSL2.

Python: 3.12.3.

Reported CPU count: 16.

Measurements are local development baselines, not release-certified benchmarks.

Model network latency was excluded by using fake models.

### 9.2 Kernel dispatch

A synthetic in-memory dispatch benchmark ran 20 batches of 1,000 dispatches.

Mean dispatch latency was 187.16 microseconds.

Median batch mean was 182.84 microseconds.

Approximate p95 batch mean was 217.40 microseconds.

Minimum observed batch mean was 174.95 microseconds.

Maximum observed batch mean was 227.40 microseconds.

This excludes durable event persistence and real effect execution.

### 9.3 Minimal one-turn runtime

The profiled local runtime used `code-explain`, a fake model, an in-memory event store, and no blob store.

Across 40 runs, mean latency was 30.68 milliseconds.

Median latency was 30.19 milliseconds.

Approximate p95 was 30.92 milliseconds.

Minimum was 29.67 milliseconds.

Maximum was 43.67 milliseconds.

This is framework overhead for a trivial finish-only turn.

It is not a useful-agent benchmark.

### 9.4 Artifact capture overhead

The same minimal run used a file blob store and standard capture.

Across 40 runs, mean latency was 38.54 milliseconds.

Median latency was 37.43 milliseconds.

Approximate p95 was 44.24 milliseconds.

Minimum was 36.48 milliseconds.

Maximum was 58.05 milliseconds.

Mean incremental capture overhead was approximately 7.9 milliseconds.

Identical content deduplicated to two blob files totaling 12,863 bytes.

The result supports retaining cheap capture and optimizing its implementation.

It does not support disabling prompts or outputs by default.

### 9.5 Durable minimal run

Twenty warm runs used SQLite-WAL plus file artifact capture.

Mean latency was 73.43 milliseconds.

Median latency was 67.75 milliseconds.

Approximate p95 was 101.91 milliseconds.

Minimum was 64.25 milliseconds.

Maximum was 125.99 milliseconds.

The runs produced 980 events, approximately 49 events per trivial run.

The SQLite database occupied 1,470,464 bytes.

That is approximately 1,500 bytes per event at this small scale.

It is approximately 73.5 kilobytes per trivial run including page and index overhead.

Forty-nine events for a finish-only turn is a material storage-amplification signal.

The event grammar should be measured before any event types are removed.

### 9.6 Event append and fold

The repository append/fold benchmark at 1,000 events measured mean append throughput of 2,887 events/second.

Maximum observed append throughput was 2,934 events/second.

Mean fold throughput was 41,670 events/second.

Fold cost was approximately 24.015 microseconds/event.

At 10,000 events, mean append throughput fell to 842.5 events/second.

Maximum observed append throughput was 873.9 events/second.

Mean fold throughput was 40,500 events/second.

Fold cost was approximately 24.716 microseconds/event.

`SqliteEventStore.append` queries the latest sequence for each event within the batch.

The throughput degradation makes that per-row sequence lookup a concrete optimization candidate.

### 9.7 Checkpoint plus suffix

A 10,000-event synthetic history used a checkpoint at sequence 9,000.

The suffix contained 1,000 events.

Twenty cold reconstructions averaged 320.53 milliseconds.

Cold p95 was approximately 326.589 milliseconds.

Twenty checkpoint reconstructions averaged 308.479 milliseconds.

Checkpoint p95 was approximately 315.012 milliseconds.

Measured speedup was only 1.04 times.

State digests matched.

Correctness is verified.

Performance benefit is not yet compelling for this state shape.

The current implementation orders the full history and decodes a large checkpoint before folding the suffix.

Checkpoint optimization belongs in 0.9.1 after representative state-shape benchmarks.

### 9.8 Memory

Baseline Python maximum resident set size was approximately 10,024 KiB.

Importing the runtime raised it to approximately 37,088 KiB.

One minimal run raised it to approximately 39,108 KiB.

The import increment was approximately 27 MiB.

The first minimal run added approximately 2 MiB.

This is acceptable for a beta CLI but should be tracked for lightweight embedding.

### 9.9 Concurrency truth

The reference topology path preserves causal ordering and is intentionally conservative.

The SQLite store protects a shared connection with an `RLock` and uses `BEGIN IMMEDIATE` for appends.

This serializes writes through one connection.

No measured claim of linear multi-agent scaling can be made from the present audit.

No evidence justifies replacing SQLite for beta.

The 0.9.1 benchmark must compare independent stores, shared-store concurrent lineages, and batched append.

### 9.10 Initial performance budgets

Beta p95 in-memory no-op turn target: at most 50 milliseconds on the reference runner.

Beta p95 durable no-op turn target: at most 125 milliseconds on the reference runner.

Kernel in-memory dispatch p95 target: at most 300 microseconds.

Append target for 10,000-event batches after optimization: at least 5,000 events/second on the same runner.

Cold fold target: at least 35,000 events/second.

Standard capture target for a trivial turn: no more than 15 milliseconds incremental local latency.

Storage target: report bytes per semantic operation, not only bytes per event.

These thresholds must be pinned to hardware and benchmark fixtures before release gating.

## 10. Governance audit

### 10.1 Architectural invariant protection

Mandatory architectural review remains justified for:

- kernel neutrality;

- causal integrity;

- authority conservation;

- budget conservation;

- public contract compatibility;

- replay semantics;

- transport equivalence;

- effect settlement;

- fail-closed authorization;

- sandbox trust boundaries.

### 10.2 Release integrity

Version identity, artifact digest, dependency lock, migration compatibility, and automated acceptance belong to release integrity.

They should be mandatory for a frozen beta artifact.

One release owner may technically qualify a beta from reproducible automation.

Independent signing may be added for higher-assurance distribution.

### 10.3 Scientific rigor

Paired experiments, repetitions, falsifiers, mutation testing, statistical analysis, independent countersignature, promotion, and rollback are legitimate for scientific claims.

They must not execute merely because an ordinary coding agent runs.

They must not block a beta that makes no corresponding scientific claim.

### 10.4 Ordinary product development

Adding a model adapter, tool, context strategy, workflow, reference agent, pack, or evaluator should require:

- stable interface conformance;

- focused tests;

- security review when authority expands;

- documentation in existing canonical locations.

It should not require constitutional ratification.

### 10.5 Obsolete bureaucracy

Duplicated status across active boards, package ledgers, evidence indexes, and archived plans creates contradictions.

The active sprint should own execution state.

Milestones should own macro acceptance only.

Evidence bundles should contain immutable results, not parallel task status.

Archived reviews should remain non-authorizing.

### 10.6 Governance simplification recommendation

Keep ADRs append-only for foundational invariants and public contracts.

Use one active sprint board for current work.

Generate evidence indexes from machine-readable bundles where possible.

Treat reviewer independence as an assurance attribute.

Do not encode it as a prerequisite for local execution.

## 11. Exact 0.9.0b1 completion plan

### 11.1 Horizon rule

Horizon 1 freezes architecture.

It fixes only demonstrated defects and product gaps.

It does not add MCTS, CEGIS, mutation testing, a new workflow engine, distributed transport, or a marketplace.

### BETA-00 — Freeze claims and establish one truth report

- Outcome: record the exact checkout identity, toolchain, test inventory, known failures, and release claims.

- Modules: release tooling, existing execution board, existing milestones.

- Dependencies: none.

- Tests: full non-network test suite and all non-Git architecture linters.

- Acceptance: one machine-readable run records counts, skips, failures, platform, and command versions.

- Acceptance: M7 sparse-environment regression is explicitly open or fixed.

- Behavior: no runtime behavior change.

- Risk: low.

- Non-goals: retroactive evidence repair; new scientific claims.

### BETA-01 — Establish one release identity

- Outcome: every public backend version resolves to `0.9.0b1` from one authoritative source.

- Modules: `pyproject.toml`, package version accessor, CLI diagnostics, service diagnostics.

- Dependencies: BETA-00.

- Tests: version equality across wheel metadata, import API, CLI, and service.

- Acceptance: zero divergent version literals in production surfaces.

- Acceptance: built artifact filename and runtime report both state `0.9.0b1`.

- Behavior: release metadata only.

- Risk: low.

- Non-goals: changing wire schema versions; renaming the distribution.

### BETA-02 — Make bootstrap authoritative for product execution

- Outcome: all beta commands enter through `RuntimeBootstrap` and `run_composed`.

- Modules: `runtime/root.py`, `runtime/bootstrap.py`, CLI, entrypoint, service application layer.

- Dependencies: BETA-01.

- Tests: adapter-selection parity and no-silent-fallback tests.

- Acceptance: product commands cannot reach the legacy in-memory default unintentionally.

- Acceptance: requested durable mode produces a WAL database in the explicit state directory.

- Behavior: behavior change at product entry surfaces.

- Risk: medium.

- Non-goals: deleting `execute_harness`; reorganizing session internals.

### BETA-03 — Define the state-directory contract

- Outcome: state location is explicit, inspectable, creatable, and never silently changed.

- Modules: bootstrap, CLI configuration, service configuration, diagnostics.

- Dependencies: BETA-02.

- Tests: relative, absolute, absent, unwritable, and existing database cases.

- Acceptance: `doctor` prints the resolved state path and durability mode.

- Acceptance: unwritable durable state fails before model or tool execution.

- Behavior: user-visible configuration behavior.

- Risk: medium.

- Non-goals: remote event stores; multi-tenant placement policy.

### BETA-04 — Complete the operational command surface

- Outcome: backend commands support `run`, `resume`, `status`, `events`, and `artifacts` consistently.

- Modules: CLI, runtime service, stdio entrypoint, shared application service.

- Dependencies: BETA-02, BETA-03.

- Tests: command contract tests against one in-process service.

- Acceptance: each command returns a typed result and stable exit status.

- Acceptance: event output preserves causal order.

- Acceptance: artifact retrieval verifies the digest before returning bytes.

- Behavior: additive product behavior.

- Risk: medium.

- Non-goals: HTTP, WebSocket, and gRPC production servers.

### BETA-05 — Separate health, readiness, and diagnostics

- Outcome: health reports process liveness; readiness reports ability to accept the requested profile.

- Modules: runtime service diagnostics, CLI doctor, adapter qualification.

- Dependencies: BETA-03.

- Tests: missing model credential, unavailable sandbox, unwritable state, corrupted DB, and local fake readiness.

- Acceptance: secrets and raw prompts never appear in diagnostics.

- Acceptance: every failure has a stable type, safe message, and remediation field.

- Behavior: additive and clarifying.

- Risk: low.

- Non-goals: fleet monitoring; external telemetry backend.

### BETA-06 — Prove package completeness

- Outcome: wheel and sdist contain every runtime schema, migration, manifest, and default pack.

- Modules: packaging metadata, resource loading tests, build workflow.

- Dependencies: BETA-01.

- Tests: build both formats, enumerate resources, install each in clean environments.

- Acceptance: build succeeds with network disabled after build dependencies are cached.

- Acceptance: installed console script runs outside the checkout with no repository `PYTHONPATH`.

- Acceptance: wheel and sdist installations pass the same smoke test.

- Behavior: packaging only.

- Risk: medium.

- Non-goals: standalone binaries; container publication.

### BETA-07 — Qualify migrations and durable continuation

- Outcome: fresh database, current database, and supported prior schema all start or fail explicitly.

- Modules: SQLite store, migrations, bootstrap, resume application service.

- Dependencies: BETA-03, BETA-06.

- Tests: fresh create, upgrade fixture, interrupted transaction, corrupt schema, missing artifact.

- Acceptance: no implicit destructive migration.

- Acceptance: restart reconstructs identical state digest from durable records.

- Acceptance: checkpoint rejection falls back to a correct cold fold.

- Behavior: correctness hardening.

- Risk: high.

- Non-goals: downgrade migration; distributed consensus.

### BETA-08 — Deliver `Lex-Minimal`

- Outcome: one native coding composition completes a deterministic inspect/edit/verify task.

- Modules: existing code/lex manifest, tools, policy, context strategy, evaluator configuration.

- Dependencies: BETA-02, BETA-04, BETA-06.

- Tests: cassette/fake task fixture with read, search, patch, test, and finish operations.

- Acceptance: no alternate engine is imported.

- Acceptance: the run records prompt, context, output, tool calls/results, patch, verification, usage, and terminal result.

- Acceptance: implementation-specific code remains configuration and plugin code outside the kernel.

- Behavior: additive reference product.

- Risk: medium.

- Non-goals: SWE-Bench competitiveness; interactive terminal support.

### BETA-09 — Deliver `Codebase-Explainer`

- Outcome: a materially different read-only composition produces a cited structural explanation.

- Modules: `code-explain` manifest, search/read tools, context strategy, result schema, evaluator.

- Dependencies: BETA-02, BETA-04, BETA-06.

- Tests: fixed repository fixture with expected file and symbol citations.

- Acceptance: no write capability is granted.

- Acceptance: every factual source reference resolves to captured tool evidence.

- Acceptance: the same runtime, store, and artifact pipeline are used as `Lex-Minimal`.

- Behavior: additive reference product.

- Risk: low.

- Non-goals: general RAG infrastructure; semantic vector database.

### BETA-10 — Demonstrate planner/executor/reviewer composition

- Outcome: three roles execute through scoped spawn and one settlement authority.

- Modules: delegation, episode engine, composition manifest, test fixtures.

- Dependencies: BETA-08.

- Tests: authority attenuation, budget conservation, child failure, bounded retry, terminal settlement.

- Acceptance: no kernel changes are required.

- Acceptance: every child has a lineage and causal parent.

- Acceptance: child authority never exceeds parent authority.

- Behavior: additive reference composition.

- Risk: medium.

- Non-goals: parallel tree search; dynamic marketplace discovery.

### BETA-11 — Fix M7 sparse-environment reproducibility

- Outcome: the topology proof behaves identically in the declared minimal environment.

- Modules: M7 proof runner, workload fixtures, deterministic environment inputs.

- Dependencies: BETA-00.

- Tests: run the same 40 tests under ordinary and sparse environments.

- Acceptance: 40 of 40 pass in both modes.

- Acceptance: recorded workload completes three expected effects and terminates consistently.

- Behavior: proof reliability; production change only if root cause is production configuration.

- Risk: medium.

- Non-goals: changing topology semantics to satisfy a brittle marker.

### BETA-12 — Prove kill and resume from installed artifacts

- Outcome: a process is terminated after durable progress and a fresh process resumes it.

- Modules: CLI/application service, SQLite store, artifact store, checkpoint manager.

- Dependencies: BETA-04, BETA-06, BETA-07, BETA-08.

- Tests: subprocess kill fixture and second-process resume.

- Acceptance: no live Python object crosses the process boundary.

- Acceptance: resumed and uninterrupted state digests match.

- Acceptance: already settled effects are not executed twice.

- Acceptance: artifact references remain retrievable and digest-valid.

- Behavior: verification of existing semantics plus product wiring.

- Risk: high.

- Non-goals: host reboot testing; distributed failover.

### BETA-13 — Prove minimal plugin lifecycle

- Outcome: installed local plugins are discovered, verified, activated, initialized, quiesced, and shut down deterministically.

- Modules: registry lifecycle, manifest loader, bootstrap application service.

- Dependencies: BETA-06.

- Tests: valid plugin, incompatible contract, duplicate ID, initialization failure, health failure.

- Acceptance: an invalid plugin cannot gain control or tool authority.

- Acceptance: observer-only plugins cannot issue control decisions.

- Acceptance: failure produces typed diagnostics without disabling unrelated built-ins.

- Behavior: product lifecycle completion.

- Risk: high.

- Non-goals: remote installation; hot upgrade; marketplace metadata.

### BETA-14 — Freeze performance and storage baselines

- Outcome: reproducible benchmark fixtures report framework overhead and storage amplification.

- Modules: existing benchmark harness, runtime fixtures, CI artifact output.

- Dependencies: BETA-08, BETA-09, BETA-10.

- Tests: no-op, coding, explanation, one-agent, nested-agent, append, fold, checkpoint.

- Acceptance: model and tool latency are separately reported.

- Acceptance: event count and bytes are grouped by semantic operation.

- Acceptance: regression thresholds use a pinned runner class.

- Behavior: measurement only.

- Risk: low.

- Non-goals: optimizing before measurement; comparing different task logic.

### BETA-15 — Freeze and technically qualify the beta artifact

- Outcome: exact wheel, sdist, schemas, manifests, migrations, and evidence report are immutable and digest-addressed.

- Modules: build/release workflow and existing evidence tooling.

- Dependencies: BETA-00 through BETA-14.

- Tests: clean installation, offline smoke, vertical slices, kill/resume, linters, full suite.

- Acceptance: zero unexplained failures.

- Acceptance: known skips are enumerated and justified.

- Acceptance: exact artifact digests and dependency versions are recorded.

- Acceptance: technical qualification is reproducible without a human ceremony.

- Behavior: release operation.

- Risk: medium.

- Non-goals: stable 1.0 compatibility promise; scientific promotion.

### 11.2 Optional formal acceptance after technical qualification

An independent reviewer may countersign the frozen artifact digest.

M5a baseline lineage may be re-established under an honest new identity.

M5b convergence experiments may be rerun with controlled repetitions.

Promotion and rollback attestations may be issued.

These steps strengthen formal claims.

They do not determine whether the installed beta can function locally.

### 11.3 Concrete evidence register

| Finding | File and symbol | Reproduced check or observation | Truth class |
|---|---|---|---|
| Domain event authority | `vanguard/packages/domain/ledger/events.py::EventEnvelope` | store, emitter, and reducer imports inspected | IMPLEMENTED |
| Event-derived state | `vanguard/packages/domain/ledger/reducer.py::reduce_batch` | checkpoint and resume suites passed | VERIFIED |
| Durable event store | `vanguard/packages/adapters/stores/event_store.py::SqliteEventStore` | warm WAL benchmark and focused recovery tests | VERIFIED |
| Per-row append lookup | `SqliteEventStore.append` | source inspection plus 1k/10k throughput degradation | IMPLEMENTED cost |
| Blob-first capture | `vanguard/packages/runtime/artifacts.py::ArtifactWriter.capture` | capture tests and source ordering inspected | VERIFIED |
| Capture policy | `vanguard/packages/runtime/artifacts.py::CapturePolicy` | role/retention resolution inspected | IMPLEMENTED |
| Prompt capture | `vanguard/packages/runtime/session.py::_LayeredOperator.propose` | pre-provider prompt bundle path inspected | IMPLEMENTED |
| Raw model capture | `vanguard/packages/runtime/session.py::_LayeredOperator._capture` | post-provider, pre-reinterpretation path inspected | IMPLEMENTED |
| Checkpoint proof | `vanguard/packages/runtime/checkpoints.py::CheckpointManager.reconstruct` | RF-96 suite passed | VERIFIED |
| Ledger-only resume | `vanguard/packages/runtime/session.py::HarnessSession.reconstruct` | resume suite passed | VERIFIED |
| Recursive engine | `vanguard/packages/agency/episode/engine.py::EpisodeEngine.run` | agency suite passed | VERIFIED |
| Child execution | `vanguard/packages/agency/episode/engine.py::EpisodeEngine.spawn` | recursion/topology tests inspected and run in focused suites | VERIFIED with M7 caveat |
| Canonical composition | `vanguard/packages/runtime/root.py::Runtime.compose` | manifest chain and reference tests inspected | VERIFIED |
| Legacy execution | `vanguard/packages/runtime/root.py::Runtime.execute_harness` | source labels and inline setup inspected | IMPLEMENTED legacy |
| Profiled execution | `vanguard/packages/runtime/root.py::Runtime.execute_profiled` | minimal runtime benchmarks executed | VERIFIED |
| Adapter authority | `vanguard/packages/runtime/bootstrap.py::RuntimeBootstrap.build` | durable/memory/model branches inspected | IMPLEMENTED |
| Profile coupling | `vanguard/packages/runtime/profiles.py::ExecutionProfile` | all axes and presets inspected | IMPLEMENTED design debt |
| Standalone CLI gap | `vanguard/cli.py::build_parser` | verbs enumerated: init, doctor, run | VERIFIED gap |
| Rich entrypoint | `vanguard/entrypoint.py` command dispatch | code/explain/resume/doctor branches inspected | IMPLEMENTED |
| Service operations | `vanguard/packages/runtime/service/service.py::RuntimeService` | status/event/artifact/resume methods inspected and focused tests passed | PARTIAL product surface |
| Plugin lifecycle | `vanguard/packages/runtime/registry/lifecycle.py` | verify/activate/init/quiesce/shutdown code inspected | PARTIAL |
| Context layering | context compiler under `vanguard/packages/agency/` | L1–L5 and prefix behavior inspected/tested | VERIFIED |
| Compaction registry | compaction modules under `vanguard/packages/agency/` | strategies and unknown fallback inspected | PARTIAL |
| PTY absence | `vanguard/packages/adapters/sandbox/rootless.py` | `DEVNULL` stdin and captured pipes inspected | VERIFIED gap |
| Package metadata | `pyproject.toml` project table | version, scripts, package discovery, data patterns inspected | IMPLEMENTED but wrong beta identity |
| Package resources | built wheel inventory | 566 matching resources observed | VERIFIED partial |
| Kernel budget | kernel package | `check_tcb_budget.py`: 1,373/1,438 | VERIFIED |
| Boundary lattice | all production imports | `check_boundaries.py`: 414 passed | VERIFIED |
| M8 proof | M8 proof runner | 59 tests and 34 markers passed | VERIFIED |
| M7 proof caveat | M7 proof runner | 34/40 sparse; 40/40 ordinary | BLOCKED qualification |
| Recovery focus | RF-96 plus resume tests | 37 tests passed in final report validation | VERIFIED |

The evidence register names symbols rather than treating document prose as implementation.

Commands that require provider credentials or network access were intentionally excluded.

Commands that would mutate the repository were intentionally excluded.

---

# Chapter II — Vanguard 0.9.1 Evolution into a Lightweight Universal Substrate

## 12. Evolution principles and target architecture

### 12.1 Non-rewrite rule

Every 0.9.1 change must have a measured cost, a demonstrated consumer, or a correctness defect.

No subsystem is replaced for conceptual purity.

Semantic refactoring and behavior changes are separated into different commits and acceptance gates.

The beta artifact remains the rollback reference.

### 12.2 Target public model

```text
Agent =
  Model
  + Tools
  + Context Strategy
  + Policy
  + Workflow
  + Memory
  + Evaluators
  + Limits
```

```text
Observe
→ Decide
→ Authorize
→ Execute
→ Record
```

The five verbs are a public mental model.

They do not erase kernel settlement, provenance, or fail-closed stages.

### 12.3 Target package responsibilities

`domain` owns immutable logical contracts, event grammar, reducers, identities, and content references.

`ports` owns behavior protocols without concrete policy or transport.

`kernel` owns authority, budgets, authorization, reservation, settlement, and provenance.

`agency` owns turn progression, context selection, spawn semantics, and workflow interpretation.

`runtime` owns the composition root, lifecycle, application service, and transaction boundaries.

`adapters` own providers, sandboxes, stores, codecs, and transports.

`packs` own domain-specific tools, policies, manifests, and evaluators.

`apps` own user-facing clients only.

### 12.4 Kernel exclusions

The kernel must not know coding semantics.

The kernel must not know research semantics.

The kernel must not know topology names.

The kernel must not compile context.

The kernel must not schedule workflows.

The kernel must not implement memory retrieval.

The kernel must not evaluate task quality.

The kernel may know capability, budget, effect, principal, scope, reservation, receipt, and causal identity.

### 12.5 One application service

The target application boundary accepts typed commands.

It resolves configuration once.

It opens one run transaction context.

It invokes the runtime without transport knowledge.

It publishes ordered events.

It returns a typed result with artifact references.

CLI, stdio, HTTP, WebSocket, gRPC, and message adapters remain thin codecs and stream bridges.

## 13. Retain, consolidate, optionalize, remove, and defer matrix

| Capability/mechanism | Decision | Reason | Replacement or condition |
|---|---|---|---|
| Append-only causal ledger | Retain | core identity and recovery value | optimize store internals only |
| Content-addressed artifact store | Retain | payload separation and deduplication | add GC and retention |
| Event-derived AgentView | Retain | removes hidden authoritative state | improve projections |
| Capability attenuation | Retain | foundational security invariant | none |
| Typed multidimensional budgets | Retain | resource conservation | simplify public configuration |
| Domain-blind kernel | Retain | prevents product coupling | enforce TCB budget |
| EpisodeEngine | Retain | one native recursive engine | extract helpers if measured |
| Scope and lineage | Retain | native subagents and causality | expose cleanly in results |
| Canonical composition chain | Retain | reproducible agent identity | simplify loaders around it |
| Prompt/context/output capture | Retain by default | high value, measured modest overhead | store bytes as artifacts |
| Checkpoints | Retain as cache | correctness model is sound | optimize full-history sorting/decode |
| SQLite-WAL store | Retain for local beta | sufficient and durable | add alternative port implementations later |
| `RuntimeBootstrap` | Retain and strengthen | intended adapter authority | become sole product path |
| `execute_harness` | Remove after migration | legacy duplicate bootstrap | compatibility deprecation window |
| Multiple model factories | Consolidate | configuration drift | one provider registry/factory |
| Multiple manifest loaders | Consolidate carefully | validation and format drift | canonical logical manifest plus codecs |
| Domain/generated event classes | Consolidate logically | representation drift | one domain model, generated transport codecs |
| Service outbox fallback | Remove after migration | duplicate publication path | canonical event store subscription |
| Bundled execution presets | Optionalize into presets | concerns are orthogonal | resolved config retains digest |
| Signed external evaluation | Optionalize | real cost and external dependency | requested evaluation configuration |
| Mutation testing | Optionalize | expensive research computation | evaluator plugin |
| Repeated trials | Optionalize | cost multiplier | experiment workflow |
| Environment replication | Optionalize | high storage and compute cost | assurance configuration |
| Long-term artifact retention | Optionalize | unbounded storage risk | retention policy |
| Evidence countersignature | Optionalize | formal assurance | release/science pipeline |
| General workflow DSL | Defer | current primitives may suffice | add only after three reference agents expose gap |
| Distributed message transport | Defer | no beta consumer | contract-first experiment |
| Bidirectional PTY | Defer | no scoped beta need | interactive coding benchmark |
| CoW snapshots and fork | Defer experiment | potential fan-out value, no proof | measure workspace-copy bottleneck |
| MCTS | Defer/reject default | task-specific and costly | pack-level experiment only |
| CEGIS | Defer experiment | specialist workflow | evaluator/policy composition |
| Documentation-driven runtime gates | Reject | couples prose to execution | machine contracts only |
| Separate research engine | Reject | duplicates authority and orchestration | plugins and workflows |
| Separate imported Lex engine | Reject | violates native composition thesis | Lex-Minimal pack |

## 14. Orthogonal operating configuration

### 14.1 Configuration axes

The target configuration has independent sections for capture, telemetry, recovery, evaluation, control, retention, containment, and approval.

Named profiles remain convenient presets.

They resolve to one immutable identity-bearing configuration.

Users may override orthogonal axes explicitly.

Every effective override changes the run-plan digest.

### 14.2 Proposed logical shape

```yaml
capture:
  prompts: full
  context: full
  outputs: full
  tools: full
  patches: full
  environment: digest
telemetry:
  pareto: basic
  traces: sampled
recovery:
  events: durable
  checkpoints: boundaries
evaluation:
  evaluators: []
  repetitions: 1
  mutation_testing: false
control:
  allowed: [accept, reject, retry]
retention:
  artifact_policy: standard
  event_policy: durable
containment:
  process_backend: host
  workspace_access: workspace-write
approval:
  default: ask
```

This is a logical target, not a schema to copy mechanically.

Migration must preserve `mhf.execution-profile/1` and `/2` reads for the declared window.

### 14.3 Always-recorded causal minimum

Run identity is mandatory.

Composition digest is mandatory.

Profile or effective-config digest is mandatory.

Scope and lineage are mandatory.

Operation identity is mandatory.

Authorization decision is mandatory for effects.

Reservation and settlement are mandatory for budgeted effects.

Artifact digest and role are mandatory when an artifact is referenced.

Terminal result is mandatory.

Error type is mandatory on failure.

### 14.4 Cheap capture default

Final model prompt should be retained unless policy forbids it.

Compiled context should be retained unless policy forbids it.

Raw model output should be retained unless policy forbids it.

Tool requests and results should be retained unless policy forbids them.

Patches and diffs should be retained unless policy forbids them.

Token, cost, latency, model identity, and workflow boundaries should be recorded when available.

Sensitive payload policy may redact, encrypt, shorten retention, or prohibit capture.

It must make information loss explicit.

### 14.5 Expensive optional operations

Repeated execution is opt-in.

A/B and ablation studies are opt-in.

Mutation testing is opt-in.

Adversarial validation is opt-in.

External evaluators are opt-in.

Environment replication is opt-in.

Signed evidence is opt-in unless the release process requests it.

Training exports are opt-in and trainability-governed.

Extended statistics are opt-in.

### 14.6 Retention and garbage collection

Events required for causal recovery must outlive recoverable checkpoints.

Artifact blobs may use role-specific retention.

An artifact may be collected only when no retained causal reference requires its bytes.

Orphan blobs from blob-first/event-failed capture are eligible after a grace period.

Checkpoint blobs are caches and may be regenerated.

Prompt and output retention must honor confidentiality and redaction policy.

Compaction must never mutate the append-only historical ledger.

Ledger compaction may produce a verified snapshot plus retained suffix only under an explicit compatibility contract.

## 15. Universal event, plugin, workflow, and transport contracts

### 15.1 Logical command contract

```python
class Command:
    command_id: str
    kind: str
    run_id: str | None
    principal: Principal
    scope: Scope
    composition_ref: str
    config_ref: str
    input: Mapping[str, object]
    idempotency_key: str
```

Commands are requests, not facts.

Transport authentication resolves to a principal before runtime dispatch.

The same command object is callable in process without JSON serialization.

### 15.2 Logical event stream contract

```python
class Event:
    event_id: str
    kind: str
    run_id: str
    scope: Scope
    lineage: Lineage
    sequence: int
    causation_id: str | None
    correlation_id: str
    payload: Mapping[str, object]
    artifact_refs: tuple[ArtifactRef, ...]
```

Event order is defined per causal stream.

Global total order is not required for independent lineages.

Cross-lineage joins require explicit dependencies.

Duplicate delivery is tolerated by event identity and idempotency keys.

### 15.3 Logical result contract

```python
class Result:
    run_id: str
    status: str
    value: object | None
    artifact_refs: tuple[ArtifactRef, ...]
    state_digest: str
    terminal_event_id: str
    diagnostics: tuple[Diagnostic, ...]
```

The result summarizes the event history.

It does not replace it.

### 15.4 Event grammar

```text
RunRequested
→ CompositionResolved
→ RunStarted
→ ObservationRecorded*
→ DecisionProposed
→ AuthorizationGranted | AuthorizationDenied
→ BudgetReserved?
→ EffectStarted?
→ EffectCompleted | EffectFailed | EffectUnknown?
→ BudgetCommitted | BudgetReleased?
→ ArtifactRecorded*
→ ChildSpawned / ChildSettled*
→ RunCompleted | RunFailed | RunStopped | RunSuspended
```

Telemetry events may be sampled.

Causal authorization and settlement facts may not be sampled.

Large prompt, output, and tool bytes live behind artifact references.

### 15.5 State transition model

```text
NEW
→ ACTIVE
→ SUSPENDED
→ ACTIVE
→ COMPLETED | FAILED | STOPPED | ABANDONED
```

Terminal states are monotonic.

Resume is legal only from a resumable nonterminal state.

Effects with unknown settlement block unsafe replay.

Already settled idempotency keys cannot execute again.

### 15.6 Plugin contract families

Model plugins decide through a model port.

Tool plugins expose descriptors and execute capability-mediated effects.

Context plugins compile bounded prompt material.

Compaction plugins transform context projections, never ledger history.

Retrieval plugins return evidence-bearing fragments.

Memory plugins store or project non-authoritative memory facts.

Policy plugins make declared decisions within granted authority.

Evaluator plugins score or gate at explicit lifecycle points.

Scheduling plugins select ready operations without authorizing effects.

Sandbox plugins implement the sandbox port and qualify their containment.

### 15.7 Lifecycle interceptors

Observer interceptors may implement `before_operation`.

Observer interceptors may implement `after_operation`.

Observer interceptors may implement `on_event`.

Observer interceptors may implement `after_result`.

Observer interceptors may implement `on_failure`.

Observers may record but cannot alter control flow.

Control interceptors require an explicit control capability.

Control interceptors may return `ACCEPT`, `REJECT`, `RETRY`, `REDIRECT`, `FORK`, or `STOP`.

`before_commit` is control-sensitive because it can prevent authoritative publication.

Conflicting controller decisions resolve through a declared policy, never registration order by accident.

### 15.8 Minimal execution pseudocode

```python
def execute(command, runtime):
    run = runtime.resolve(command)
    view = runtime.observe(run.scope)
    proposal = run.agent.decide(view)
    decision = runtime.kernel.authorize(proposal, run.authority, run.budget)
    if decision.denied:
        return runtime.record_denial(run, proposal, decision)
    reservation = runtime.kernel.reserve(decision)
    receipt = runtime.effects.execute(decision.operation)
    settlement = runtime.kernel.settle(reservation, receipt)
    return runtime.record_result(run, receipt, settlement)
```

Authorization precedes external effect.

Recording includes failure and unknown settlement.

### 15.9 Multi-agent pseudocode

```python
def run_ready_graph(graph, parent):
    while graph.has_ready_nodes():
        ready = graph.ready_nodes()
        children = [parent.spawn(node.spec, attenuate(node, parent)) for node in ready]
        outcomes = schedule(children, dependencies=graph.dependencies)
        for node, outcome in zip(ready, outcomes):
            graph.record_child_settlement(node, outcome)
        graph.advance()
    return graph.reduce_result()
```

`schedule` controls concurrency only.

It does not grant authority.

Every child still runs through the same kernel and event recorder.

### 15.10 Workflow sufficiency test

Before adding a workflow DSL, implement direct, staged coding, planner/executor/reviewer, critic/reviser, and research fan-out compositions.

Record every place where configuration becomes awkward or custom Python orchestration is duplicated.

Add only the smallest missing primitive shared by at least two real compositions.

Do not add a second execution engine.

### 15.11 Transport equivalence rules

In-process execution uses typed objects and direct callbacks.

stdio uses framed JSONL with explicit schema version.

HTTP maps a command to a resource and events to a resumable stream.

WebSocket maps the same event stream bidirectionally where needed.

gRPC maps the same logical schemas to generated messages.

Message transports preserve command idempotency, event identity, causation, and settlement.

Equivalent commands under equivalent effective configuration must produce semantically equivalent event sequences.

Byte-level timestamps or transport framing need not match.

No local caller should pay network serialization costs.

## 16. Additional product-relevance decisions

| Proposal | Existing capability | Verified gap | Required for beta | Post-beta experiment | Reject |
|---|---|---|---:|---:|---:|
| Bidirectional PTY | pipe capture only | no interactive stdin/TTY semantics | No | Yes, if interactive benchmark demands it | No |
| Duplicate event publication cleanup | canonical store plus outbox fallback | compatibility overlap | Only prevent double publication | Yes | No |
| Orthogonal operation configuration | fields exist in profile | preset coupling | Minimum safety fixes | Yes | No |
| Sandbox extensibility | sandbox port and adapters exist | future implementation not proven | No new seam | Test consumer first | No |
| Context strategy extensibility | compiler and policies exist | unknown-policy fallback | Fix explicit resolution | Improve later | No |
| Plugin extensibility | SPI and registry exist | product lifecycle incomplete | Minimal lifecycle | Yes | No |
| Prefix stability | L1–L5 compiler exists | no beta blocker shown | Yes, preserve | Benchmark | No |
| Replaceable compaction | registry exists | structured policy is weak | Existing policies sufficient | Yes | No |
| CoW snapshot/fork | no complete production capability found | workspace fan-out may copy excessively | No | Yes, after measurement | No |
| Tree-Sitter preflight | no core capability required | syntax-aware context/tooling opportunity | No | Yes, pack experiment | No |
| Improved compaction | partial | heuristics and fallback | No new algorithm | Yes | No |
| Taint policies | capability/confidentiality foundations | end-to-end information flow not proven | No | Yes, security experiment | No |
| SBFL | not core | diagnostic localization opportunity | No | Yes, evaluator/tool experiment | No |
| Differential testing | ordinary tests exist | no universal plugin proof | No | Yes | No |
| Mutation testing | optional concepts/evaluators | cost and integration | No | Yes, research mode | Default runtime use |
| MCTS | topology primitives could support it | value and cost unproven | No | Only with benchmark | Default/core inclusion |
| CEGIS | policies/evaluators could compose it | no near-term consumer | No | Specialist experiment | Core inclusion |

## 17. Exact 0.9.1 refactoring plan

### EVO-00 — Pin beta behavior as the rollback oracle

- Outcome: golden command, event, artifact, and result fixtures describe beta behavior.

- Modules: contract tests and frozen beta artifacts.

- Dependencies: BETA-15.

- Tests: replay beta fixtures under 0.9.1 readers.

- Acceptance: every intentional semantic change is separately enumerated.

- Behavior: no change.

- Risk: low.

- Non-goals: freezing internal module layout.

### EVO-01 — Introduce one backend application service

- Outcome: CLI, stdio, and service adapters call one typed command interface.

- Modules: runtime service, CLI, entrypoint, studio gateway.

- Dependencies: EVO-00.

- Tests: transport-neutral command contract suite.

- Acceptance: no transport constructs model, store, environment, or session directly.

- Acceptance: in-process execution performs no mandatory serialization.

- Behavior: structural first; parity required.

- Risk: high.

- Non-goals: new HTTP/gRPC deployments.

### EVO-02 — Retire legacy bootstrap

- Outcome: `RuntimeBootstrap` is the sole adapter construction authority.

- Modules: `runtime/root.py`, bootstrap, callers, tests.

- Dependencies: EVO-01.

- Tests: caller census and compatibility deprecation tests.

- Acceptance: no production call reaches `execute_harness`.

- Acceptance: legacy API either delegates without semantic divergence or raises a documented deprecation.

- Behavior: structure with a compatibility boundary.

- Risk: medium.

- Non-goals: changing kernel dispatch.

### EVO-03 — Unify model selection

- Outcome: one registry/factory resolves model ports and configuration identity.

- Modules: bootstrap, model selection, CLI, entrypoint, routing, provider adapters.

- Dependencies: EVO-02.

- Tests: fake, cassette, Ollama, OpenRouter selection and missing-config diagnostics.

- Acceptance: provider selection logic has one production owner.

- Acceptance: provider secrets remain environment-only and redacted.

- Behavior: structural with equivalent selection.

- Risk: medium.

- Non-goals: one file per model vendor; new provider support.

### EVO-04 — Converge manifest and pack loading

- Outcome: one canonical logical manifest enters composition regardless of source codec.

- Modules: domain manifest, agency loader, named manifest parser, pack loader, registry compiler.

- Dependencies: EVO-00.

- Tests: canonical digest parity for every shipped manifest.

- Acceptance: YAML, JSON, and packaged resources normalize to one immutable type.

- Acceptance: validation happens once at untrusted ingress and once at authority-sensitive activation.

- Behavior: structural; byte identity changes require explicit migration.

- Risk: high.

- Non-goals: removing supported manifest versions without a window.

### EVO-05 — Converge event representations

- Outcome: one domain event model and generated transport codecs share a single semantic schema.

- Modules: domain ledger events, generated wire types, emitter, service codecs, stores.

- Dependencies: EVO-00, EVO-01.

- Tests: `/1` read, `/2` read/write, round-trip, unknown field, transport parity.

- Acceptance: production logic never branches on duplicate class identity.

- Acceptance: new writers remain `/2` until a separately governed contract change.

- Behavior: structural with compatibility preservation.

- Risk: high.

- Non-goals: inventing `/3`; rewriting historical events.

### EVO-06 — Extract session responsibilities

- Outcome: session lifecycle, operator/context, approval flow, evaluation, and telemetry become focused collaborators.

- Modules: `runtime/session.py` and extracted runtime modules.

- Dependencies: EVO-00, EVO-02.

- Tests: existing session, resume, approval, capture, and M8 suites unchanged.

- Acceptance: no change to emitted event order or state digest for golden fixtures.

- Acceptance: each extracted component has one clear responsibility and real consumer.

- Behavior: structure only.

- Risk: high.

- Non-goals: redesigning the turn algorithm; adding hooks during extraction.

### EVO-07 — Separate service command and query paths

- Outcome: the oversized service no longer owns transport, persistence compatibility, orchestration, and queries together.

- Modules: `runtime/service/service.py`, inbox store, gateway, application service.

- Dependencies: EVO-01.

- Tests: command idempotency, ordered event query, artifact query, cancellation, resume.

- Acceptance: one canonical event publication path.

- Acceptance: legacy outbox fallback has zero production consumers before removal.

- Behavior: structural with explicit fallback retirement.

- Risk: high.

- Non-goals: event-store replacement.

### EVO-08 — Implement orthogonal effective configuration

- Outcome: capture, telemetry, recovery, evaluation, control, retention, containment, and approval resolve independently.

- Modules: profiles, run plan, manifest bindings, diagnostics, schema.

- Dependencies: EVO-00, EVO-04.

- Tests: pairwise axis overrides, digest sensitivity, legacy profile reads, invalid combination failures.

- Acceptance: every behavior-affecting field enters the effective-config digest.

- Acceptance: cheap capture remains enabled in the standard product preset.

- Acceptance: expensive evaluation remains absent unless selected.

- Behavior: intentional configuration evolution.

- Risk: high.

- Non-goals: removing named presets; weakening containment.

### EVO-09 — Add typed observer and controller interceptors

- Outcome: research and operational extensions share lifecycle boundaries without a second runtime.

- Modules: ports SPI, runtime lifecycle, policy/evaluator adapters.

- Dependencies: EVO-06, EVO-08.

- Tests: observer non-interference, controller authority, decision conflict, unsupported decision, retry budget.

- Acceptance: observers cannot reject, redirect, fork, retry, or stop.

- Acceptance: controllers cannot exceed granted capability or budget.

- Acceptance: logging has no implicit control authority.

- Behavior: additive extension contract.

- Risk: high.

- Non-goals: arbitrary middleware mutation; registration-order semantics.

### EVO-10 — Optimize SQLite append safely

- Outcome: eliminate per-event latest-sequence lookup within validated batches.

- Modules: SQLite event store and contract tests.

- Dependencies: EVO-00.

- Tests: monotonicity conflicts, duplicate IDs, rollback atomicity, concurrent writers, crash recovery.

- Acceptance: at least 5,000 events/second at the audited 10,000-event fixture on comparable hardware.

- Acceptance: ordering and uniqueness invariants remain unchanged.

- Behavior: performance only.

- Risk: high.

- Non-goals: changing database technology; weakening `FULL` durability by default.

### EVO-11 — Make checkpoint acceleration real

- Outcome: checkpoint reconstruction avoids processing irrelevant prefix envelopes.

- Modules: checkpoint manager, event-store range queries, reducer projection loading.

- Dependencies: EVO-10.

- Tests: parity, corrupt checkpoint fallback, reducer pin mismatch, large-state benchmark.

- Acceptance: checkpoint plus 10% suffix is at least 3× faster than cold fold on the pinned representative fixture.

- Acceptance: state digest parity remains exact.

- Acceptance: failed proof always falls back to cold truth.

- Behavior: performance only.

- Risk: high.

- Non-goals: making checkpoints authoritative; deleting required ledger prefix prematurely.

### EVO-12 — Add retention and garbage collection

- Outcome: bounded artifact storage with causal-reference safety.

- Modules: artifact index, blob store ports/adapters, retention service, diagnostics.

- Dependencies: EVO-08.

- Tests: live reference, orphan blob, expired role, checkpoint cache, concurrent capture, interrupted GC.

- Acceptance: no referenced retained artifact is deleted.

- Acceptance: orphan blobs become collectible only after a configured grace period.

- Acceptance: dry-run reports exact digests and reasons.

- Behavior: additive operational behavior.

- Risk: high.

- Non-goals: ledger-history deletion; training-data export.

### EVO-13 — Fail closed on strategy resolution

- Outcome: unknown context, compaction, policy, model, evaluator, and workflow identifiers never silently select an alternative.

- Modules: strategy registries, composition activation, diagnostics.

- Dependencies: EVO-04, EVO-08.

- Tests: unknown identifiers, explicit defaults, compatibility aliases, digest changes.

- Acceptance: every fallback is explicit and identity-bearing.

- Acceptance: typoed strategy IDs fail before model or tool execution.

- Behavior: intentional correctness change.

- Risk: medium.

- Non-goals: improving compaction quality.

### EVO-14 — Prove concurrent lineage execution

- Outcome: independent ready child operations execute asynchronously while causal joins remain deterministic.

- Modules: agency scheduler SPI, delegation, event sequencing, SQLite store.

- Dependencies: EVO-05, EVO-10.

- Tests: independent fan-out, dependent nodes, cancellation, budget contention, child failure, deterministic join.

- Acceptance: no global runtime lock serializes model or tool latency.

- Acceptance: shared-store writes preserve per-lineage order and idempotency.

- Acceptance: four independent delayed tasks achieve at least 2.5× wall-clock speedup over sequential execution on the fixture.

- Behavior: additive performance behavior.

- Risk: very high.

- Non-goals: distributed scheduling; global total order.

### EVO-15 — Build native reference composition catalog

- Outcome: coding, explanation, research, RAG, and planner/executor/critic agents are configurations over shared primitives.

- Modules: packs, manifests, plugins, test fixtures.

- Dependencies: EVO-04, EVO-08, EVO-09.

- Tests: common conformance suite plus workflow-specific success tests.

- Acceptance: no reference agent modifies the kernel.

- Acceptance: replacing model, context strategy, evaluator, or limits changes configuration rather than engine code.

- Acceptance: implementation-specific LOC and reused configuration are reported.

- Behavior: additive product capability.

- Risk: medium.

- Non-goals: equal benchmark leadership in every domain.

### EVO-16 — Remove proven dead abstractions

- Outcome: compatibility and metadata paths with zero consumers are deleted after instrumentation and deprecation.

- Modules: determined by consumer census.

- Dependencies: EVO-02 through EVO-15 as applicable.

- Tests: full suite, import boundaries, package resource audit, public API compatibility.

- Acceptance: each deletion names its former consumer set, replacement, and rollback commit/artifact.

- Acceptance: production LOC and startup work decline measurably.

- Behavior: structure and supported-surface cleanup.

- Risk: medium.

- Non-goals: deletion by aesthetic preference; removal of `/1` readers before policy permits.

## 18. Reference validation agents and competitive proof

### 18.1 `Lex-Minimal`

Purpose: prove a useful coding loop with native tools and policy.

Required tools: read, search, bounded patch, deterministic command/test, finish.

Required capture: prompt, context, proposal, tool request/result, patch, verification, result.

Required recovery: resume after at least one settled effect.

Comparison baseline: a minimal dedicated loop using the same model responses, tools, task, and stopping rule.

### 18.2 `Codebase-Explainer`

Purpose: prove a materially different read-only workflow.

Required tools: file inventory, search, bounded read, symbol evidence.

Required result: structured explanation with resolvable evidence references.

Required authority: read-only.

Comparison baseline: a dedicated read/search/model loop using identical inputs.

### 18.3 `Research-Minimal`

Purpose: prove citation-bearing fan-out without a separate engine.

Required plugins: retrieval tools, citation validator, synthesis policy.

Required control: retry invalid citations within budget.

Required capture: query, sources, extracted evidence, synthesis, validation.

This is a 0.9.1 reference unless offline fixtures make it cheap for beta.

### 18.4 `Planner-Executor-Critic`

Purpose: prove role composition, child scopes, and controlled revision.

Planner cannot execute privileged effects.

Executor receives attenuated task authority.

Critic observes results and may request bounded retry through declared control authority.

All roles use the same episode engine and kernel.

### 18.5 Comparison metrics

Task success is primary.

Wall-clock latency is reported with model/tool time separated.

Framework overhead is reported directly.

Token and monetary cost are reported from provider usage when available.

Tool-call count is reported.

Recovery success is binary and timed.

Implementation-specific LOC is reported.

Configuration reuse is reported.

Storage amplification is reported per semantic operation.

Strategy replacement effort is reported as changed files and LOC.

The dedicated baseline must use identical task logic.

## 19. Failure taxonomy and fail-closed invariants

### 19.1 Configuration failures

Unknown manifest, plugin, profile, model, policy, or strategy fails before execution.

Invalid axis combinations fail before execution.

Missing durable state path fails before execution when durability is required.

### 19.2 Authorization failures

Denied authority emits a denial fact and executes no effect.

Insufficient budget executes no effect.

Child escalation is denied and recorded.

Observer plugins cannot become controllers.

### 19.3 Effect failures

Known failure settles the reservation according to policy.

Unknown settlement blocks unsafe retry.

Duplicate idempotency keys do not duplicate external effects.

### 19.4 Persistence failures

Blob failure prevents artifact-reference emission.

Event append failure prevents successful result publication.

Checkpoint corruption falls back to cold fold.

Database schema incompatibility produces a typed readiness failure.

### 19.5 Model and tool failures

Provider timeout is distinct from rejected output.

Malformed model output is retained before reinterpretation when policy permits.

Tool protocol error is distinct from tool-domain failure.

Retry consumes declared budget and remains bounded.

### 19.6 Recovery failures

Missing event history cannot be masked by a checkpoint.

Reducer-version mismatch rejects the checkpoint.

Missing required artifact prevents faithful re-execution and is reported honestly.

Replay and re-execution are never conflated.

### 19.7 Plugin failures

Unverified plugin code cannot activate.

Initialization failure cannot leave partial authority registered.

Health failure isolates the plugin when configured.

Plugin shutdown does not erase causal history.

## 20. Risks, rollback points, and acceptance gates

### 20.1 Highest beta risks

Packaging may hide checkout-relative resource assumptions.

Legacy bootstrap callers may bypass durable defaults.

M7 qualification may depend on ambient environment variables.

Resume may be correct in unit tests but incomplete through the installed CLI.

Reference agents may terminate without doing useful work.

Plugin activation may have metadata coverage without failure-safe runtime behavior.

### 20.2 Highest 0.9.1 risks

Consolidating event classes may break historical reads.

Extracting session logic may reorder emitted events.

Orthogonal configuration may alter run identity unexpectedly.

Concurrency may violate sequence, budget, or idempotency invariants.

Garbage collection may remove evidence still required by retention.

Lifecycle interceptors may create hidden control authority.

### 20.3 Rollback points

The frozen `0.9.0b1` wheel and sdist are the primary rollback artifacts.

Each 0.9.1 structural extraction must preserve golden event traces.

Compatibility readers remain until explicit removal gates pass.

New configuration resolves alongside legacy profiles before legacy writers are removed.

Concurrent scheduling remains behind an opt-in capability until parity and conservation tests pass.

Garbage collection launches in dry-run mode before deletion is enabled.

### 20.4 Beta acceptance gate

The beta gate requires a clean install outside the checkout.

It requires offline execution with fake, local, or cassette adapters.

It requires useful `Lex-Minimal` and `Codebase-Explainer` runs.

It requires a multi-role native composition.

It requires run, status, events, artifacts, interrupt, and resume operations.

It requires durable state with no silent fallback.

It requires package resource and migration proof.

It requires all architecture/security linters.

It requires zero unexplained test failures.

It requires exact artifact digests and version identity.

It does not require SWE-Bench competitiveness.

It does not require independent scientific countersignature.

### 20.5 0.9.1 acceptance gate

One application service owns backend commands.

One bootstrap owns concrete adapter construction.

One logical event model owns semantics.

Cheap capture stays available by default.

Expensive research mechanisms are opt-in.

Reference agents require no kernel changes.

Golden beta traces remain readable.

Measured append and checkpoint performance improve without weakened durability.

Concurrent lineages preserve authority, budget, ordering, and settlement.

Dead paths are removed only after consumer proof.

## 21. Final recommendation

### 21.1 Preserve

Preserve the domain/ports/kernel/agency/runtime/adapters lattice.

Preserve event authority and append-only history.

Preserve artifact addressing and blob-first capture.

Preserve reducers, checkpoints as caches, and crash recovery.

Preserve capabilities, budgets, scopes, lineages, plugins, and packs.

Preserve the native EpisodeEngine as the one agency engine.

### 21.2 Simplify

Simplify the product entry path.

Simplify version and state configuration.

Consolidate bootstrap and model selection.

Converge manifest and event representations gradually.

Split oversized runtime modules along existing responsibilities.

Make capture, telemetry, recovery, evaluation, control, and retention orthogonal.

Reduce documentary status duplication.

### 21.3 Archive

Archive superseded compatibility paths after consumer migration.

Archive stale milestone narratives as historical evidence.

Archive invalid experimental claims rather than silently rewriting them.

Archive metadata fields only after proving no runtime or compatibility consumer.

### 21.4 Rewrite decision

Reject a greenfield rewrite.

The core is recoverable and already implements the hardest invariants.

The measured overhead is meaningful but not catastrophic.

The beta gaps are primarily product integration, packaging, command parity, qualification, and useful reference workflows.

The 0.9.1 gaps are consolidation and optionality problems.

Neither category justifies discarding the foundation.

## 22. Ordered action list for developers

1. Freeze a fresh automated truth run and reproduce the M7 sparse-environment failure.

2. Set one `0.9.0b1` release identity and make `RuntimeBootstrap` the beta product path.

3. Define the explicit durable state directory and fail closed when it is unavailable.

4. Put `run`, `resume`, `status`, `events`, and `artifacts` behind one backend application service.

5. Build and clean-install both wheel and sdist without checkout imports or network-dependent runtime behavior.

6. Ship useful native `Lex-Minimal` and `Codebase-Explainer` workflows through the same runtime.

7. Prove planner/executor/reviewer spawning without a kernel change.

8. Kill an installed run, resume it in a fresh process, and verify state, effect, and artifact parity.

9. Record performance and storage baselines, then freeze the exact beta artifacts.

10. Begin 0.9.1 only after the beta measurements identify the highest-value consolidation work.

---

End of report.
