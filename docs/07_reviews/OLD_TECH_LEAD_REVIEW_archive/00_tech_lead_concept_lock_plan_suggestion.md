# Vanguard / AETHER v0.6 — Independent Tech Lead Concept Lock Assessment

**Author:** Independent Tech Lead review lane
**Engagement:** ANALYSIS-ONLY. No code, spec, ADR, annex, roadmap, milestone, backlog, sprint, or existing
review was modified. No commit was made. This file is the sole artifact produced.
**Tree reviewed:** `main` @ `c5d5fb5`, working tree as found (5 staged/untracked doc changes).
**Date:** 2026-08-20.
**Deliverable path note:** the directive names
`docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/tech_lead_concept_lock_plan_suggestion.md`; the referenced
placeholder that already exists on this tree is the `00_`-prefixed sibling, and this report was written
there so it sits beside `00_tech_lead_doing.md` and `00_arch_lead_*`. Same content, one file.

---

## 1. Executive Summary

I ran the tests, ran every CI gate, diffed the two runtimes, and ran the code generator. My conclusion
differs from the Principal Staff Engineer lane not on architecture but on **what the Concept Lock is
for**.

The Staff lane's `001_V060_concept_phase_BETA.md` is directionally correct and I agree with most of its
P0 list. But it treats the project's central problem as *architectural ambiguity* — two trees, unclear
canon — and proposes to fix it by writing ADRs 0069–0073 and a SPEC v0.6, explicitly deferring the CI
change to "the first code-phase task."

That diagnosis is incomplete. The evidence says the central problem is **an evidence system that rewards
emission and structure over behaviour**, and that this system has already manufactured a second runtime
which looks finished and is largely theatre:

- `[FACT]` The CI-gated scheduler **fabricates its own passing verdict**. `layer0/scheduler/driver.py:138`
  emits `VERDICT_RECORDED payload={"verdict": "pass"}` unconditionally, after calling
  `self._gate.request(subject)` and discarding the result. The exterior-judge thesis — the project's
  one-sentence identity — is inverted inside the only tree CI protects.
- `[FACT]` The replay-parity gate is a **tautology**. `test/layer0/replay/test_parity.py` computes
  `live_state = fold(store.envelopes)` and `replayed_state = fold(list(store.envelopes))` and asserts they
  are equal. It folds one list twice. Invariant I-4 ("State = fold(events), proven … and diffs against
  live state every CI run") is not tested anywhere.
- `[FACT]` `layer0/spi/types_gen.py` is headed `AUTO-GENERATED … DO NOT EDIT`. Running
  `python3 tools/codegen/generate_types.py` produces a **different and syntactically invalid** file
  (`requests: tuple[#, ...]`, `SyntaxError: '[' was never closed`). The committed file is hand-written.
  Axiom A-4 and Invariant I-8 are violated in the most-imported file of the new tree, and no gate checks it.
- `[FACT]` `spawn()` at `layer0/scheduler/driver.py:170` emits `ChildSpawned` then immediately
  `ChildReturned` with `spans: []`. No child principal, no attenuation, no budget lineage, no execution.
  It exists so that two declared event kinds have a lexical emitter site.
- `[FACT]` The E-COV gate (`tools/check_event_coverage.py`) is a **grep for the kind's string inside a
  directory**. It passes at "40 kinds, 100% emitter coverage" and it is **not wired into CI**. The mock
  `spawn()` above is precisely the laziest implementation that satisfies it.
- `[FACT]` The CI-gated behavioural suite is **25 tests running in 0.014 s** over 4,556 lines of
  microkernel. The 1,119-test legacy suite — which covers the SQLite/WAL ledger, the Ed25519 governance
  flow, the bubblewrap sandbox, the isolated evaluator, and the episode engine — **is not run by CI at
  all**, and currently has 11 failures.
- `[FACT]` `tools/check_tcb_budget.py` measures **`vanguard/packages/kernel/*` only**. The new
  `layer0/kernel/*` (1,342 lines) is outside the trusted-computing-base budget entirely. The gate polices
  the tree the Staff lane wants to keep and ignores the tree that grew.

**Independent recommendation.** Lock fewer concepts, and make the lock *pay for itself*.

1. **The Concept Lock must ship its own proof obligations.** Every P0 concept locked in v0.6 is locked
   together with a named falsifiable test that fails against a specific stated wrong implementation. A
   concept without a bound falsifier is not locked, it is announced. This is the one structural change I
   would make to the Staff lane's plan, and it is P0, not P1.
2. **The CI subject-of-record change is part of the lock, not the phase after it.** Deferring it means
   the lock is ratified under gates that just demonstrably certified a self-signing judge as green. That
   is not a sequencing preference; it is a credibility precondition.
3. **Lock ~12 primitives, explicitly refuse to lock ~20.** The directive's 40-concept list mixes
   irreversible substrate (envelope lineage, attenuation order, sink classes, evaluator exteriority) with
   things that live above the plugin line (Skill, Memory, Toolkit, Experiment, Promotion, Meta-Harness).
   Locking the latter now is speculative and creates the migration debt the lock exists to avoid.
4. **Directional convergence, with deletion dates, not "absorb eventually."** I agree `vanguard/packages/`
   is canonical. I go further than the Staff lane: `layer0/kernel/` and `layer0/events/` should be
   **scheduled for deletion, not merger**, because they are a comment-stripped copy that is already
   diverging and whose tests are the current CI gate. `layer0/spi/` and `layer0/registry/` are the genuine
   new value and should be promoted into `packages/` in place.
5. **`project_id` cannot be locked into every envelope while `Project` does not exist.** Lock the field
   *and* a one-paragraph normative definition, or use `root_episode_id` and defer `Project`.

Where the Staff lane and I converge, we converge hard: Python-first, no Rust, no third tree, no graph DB,
no workflow-DAG engine, sequential execution with concurrent *semantics*, JSON-RPC/UDS plugin wire, five
SPIs, exterior evaluator, SQLite WAL, hybrid event sourcing. I would not reopen any of those.

---

## 2. Scope and Independence Statement

I read the Principal Staff Engineer corpus (`principal_engineer_proposal.md` 4,460 lines,
`Vanguard-substrate-060-full-refactor-v3-1.md`, `vanguard-substrate-060-execution-plan.md`,
`vanguard-arquitetura-v4-parecer-e-plano.md`, `aether-v1-roadmap-waves.md`,
`001_V060_concept_phase_BETA.md`) and used it as evidence and intellectual input.

I did not adopt its conclusions by default and I did not manufacture disagreement. Every position below
that differs from theirs differs because a command I ran, or a file I read, pointed somewhere else. Where
I ran the same check they claim to have run, I state whether my tree reproduces their number.

Two facts shaped the independence of this lane materially:

- `[FACT]` `001_V060_concept_phase_BETA.md` is not a proposal; it is already a **decision document** with
  twelve "Locked P0 decisions (approve with this plan)" and a Phase-D instruction to write ADRs 0069–0073
  and rewrite SPEC §1/§2/§8. Reviewing it as a peer proposal understates what approving it does.
- `[FACT]` There is a third lane on this tree: `00_arch_lead_doing.md` (1,292 lines) with its own empty
  deliverable. Three independent lanes are being run against one lock. That is a good design for the
  *analysis*, and a risk for the *lock* — see §31.

---

## 3. Evidence & Investigation Method

Everything labelled `[FACT]` below was produced by one of these, on this tree, in this session:

```bash
python3 -m unittest discover -s test -t .                 # 1119 tests, 6 failures, 5 errors, 8 skipped
python3 -m unittest discover -s test/layer0 -t .          # 25 tests, 0.014s, OK
python3 -m unittest test.test_repo_paths                  # exit=1  (CI's FIRST step)
python3 tools/check_boundaries.py                         # exit=0
python3 tools/check_tcb_budget.py                         # exit=0, 1347/1438 logical lines, packages/kernel only
python3 tools/check_domain_blindness.py                   # exit=0
python3 tools/check_isolation_policy.py                   # exit=0
python3 -m unittest discover -s test/packs -t .           # exit=0
python3 tools/check_stale_paths.py                        # exit=0
python3 tools/check_markdown_links.py                     # exit=0
python3 tools/scan_secrets.py                             # exit=0
python3 tools/check_event_coverage.py                     # exit=0, "40 kinds, 100% emitter coverage", NOT in CI
python3 tools/codegen/generate_types.py                   # exit=0, output does not compile (restored via git checkout)
diff layer0/kernel/*.py vanguard/packages/kernel/*.py     # 8 module pairs
diff layer0/events/canonical.py vanguard/packages/domain/canonicalisation/jcs.py
git log --reverse -- layer0 ; git log --reverse -- vanguard/packages/kernel
```

The working tree was left exactly as found; the one mutation (running the generator) was reverted with
`git checkout -- layer0/spi/types_gen.py` and `git status --short layer0/` confirmed clean.

**Evidence labels.** `[FACT]` = command output or file content on this tree. `[INFERENCE]` = reasoned from
facts, not proven. `[RECOMMENDATION]` = this lane's proposed lock decision. `[UNKNOWN]` = insufficient
evidence; needs a spike.

---

## 4. Repository As-Built Findings

### 4.1 The tree is two disjoint runtimes, not one system with a legacy corner

`[FACT]` Sizes and lineage:

| Tree | Py files | LOC | First commit | Character |
|---|---|---|---|---|
| `vanguard/packages/` | 126 | 21,400 | `2b38d00` (v0.4.0 foundational) | The shipping v0.4.5 runtime |
| `layer0/` + `packs/` | 51 | 5,410 | `d3af6e3` "feat(W1): Layer 0, Events and Schemas" | The MHF v1 microkernel rewrite |

`[FACT]` The dependency direction is one-way and thin. Nothing in `layer0/` imports `vanguard.packages`
(the only match is the word "vanguard" inside a docstring at `layer0/events/canonical.py:4`). Four modules
under `vanguard/packages/adapters/` import `layer0.spi` — `sandbox/toolkit.py`, `stores/memory_engine.py`,
`evaluators/gate.py`, `context/window.py` — and `tools/check_boundaries.py:30` explicitly permits it
(`"adapters": {"domain", "ports", "layer0_spi"}`).

`[INFERENCE]` This is the shape of a **copy-fork that grew a real SPI**. `layer0/spi/` is genuinely new
value that the old tree has already started consuming. `layer0/kernel/` and `layer0/events/` are not new
value; they are the old modules with docstrings stripped and imports retargeted.

`[FACT]` Evidence for "stripped copy" rather than "rewrite": diffing the eight kernel module pairs, the
differences are almost entirely (a) removed explanatory docstrings, (b) import retargeting
(`from ..domain.selectors.resource_selector import decide` → `from layer0.events.selectors import decide`),
(c) relocation of `Reservation` from an inline dataclass to `layer0.spi.types_gen`. Diff sizes:
attenuation 84, budget 78, classifier 107, dispatch 384, grants 93 lines. `layer0/events/canonical.py` vs
`vanguard/packages/domain/canonicalisation/jcs.py` is a **39-line diff**, of which the only substantive
delta is that layer0 folded `digest_bytes` / `digest_of` / `chain_digest` into the same module.

`[INFERENCE]` The stripping is itself a hazard. The `packages/kernel` docstrings are not decoration —
they are the only place the rules `K-04 … K-48` and the mutation-failure IDs `MF-KRN-001 … 009` are
attached to the code that implements them. `layer0/kernel/dispatch.py:1` reduces the entire S0–S12
rationale block to `"""The dispatch sequence (S0–S12). There is no second path."""`. The invariants
survive as behaviour but lose their traceability to `docs/04_annex/KERNEL.md`.

### 4.2 The new tree regressed durability

`[FACT]` `layer0/events/store.py` provides exactly one ledger: `MemoryLedger`, docstring
*"In-memory ledger store used by the sequential driver and replay tests."* Its `append_intent` — the
`K-47` durable-intent obligation, the thing that makes a crash between dispatch and emit
*undeterminable* rather than invisible — is:

```python
def append_intent(self, event: object) -> None:
    """K-47 durable intent. Emission is the EventSink's job (S12 / K-06)."""
    self.intents.append(event)
```

A Python list append. `layer0/kernel/dispatch.py:249` calls it at S8a, i.e. the crash-safety invariant
is satisfied by an in-process list.

`[FACT]` The old tree has the real thing: `vanguard/packages/adapters/stores/event_store.py:122` is
*"Embedded transactional EventStore with Write-Ahead Logging (WAL) and crash safety (CT-40)"*, using
`sqlite3` with `PRAGMA journal_mode = WAL` and `synchronous = FULL`.

`[FACT]` `docs/05_adr/0010-*.md` (accepted) mandates *"A transactional embedded store with write-ahead
logging; line-delimited JSON is export only."*

`[INFERENCE]` `layer0/` is in violation of an accepted ADR on the single most load-bearing durability
requirement, and CI is green. This is the strongest single argument against the *Execution Plan* document's
position that `layer0/` is the v0.6 production target.

`[FACT]` `layer0/events/blob.py` does write real bytes and `os.fsync(fd)` the file — but never fsyncs the
containing directory, so the *directory entry* is not durable across a crash. It also emits
`CHECKPOINT_CREATED` for a blob write, reusing a lifecycle kind for a CAS write.

### 4.3 Identity and lineage are missing from the envelope

`[FACT]` `layer0/events/envelope.py` `EnvelopeFactory.emit()` constructs exactly these fields:
`schema_version, event_id, kind, seq, occurred_at, run_id, principal, payload, digest, episode_id,
branch_id, prev_digest, causation_id, correlation_id, idempotency_key, alertable`.

Absent: `project_id`, `parent_principal_id`, `parent_episode_id`, `harness_digest`.

`[FACT]` Worse, the *primary* emission path drops half of what does exist. `LedgerEmitter.emit()` (used by
the kernel for every `Event` value) passes only `kind, run_id, principal, payload, alertable`. Only the
secondary `emit_kind()` can carry `episode_id`, `causation_id`, `correlation_id`, `idempotency_key`. So
kernel-originated events — grants, budgets, denials, the entire authority trail — are emitted with
`episode_id=None` and `causation_id=None`.

`[FACT]` `EnvelopeFactory` holds `self._seq` and `self._prev` as instance state initialised to `0` / `None`.
There is no path that recovers the chain head from a store, so the hash chain restarts from scratch on
every process. `SequentialTurnDriver.recover()` (`driver.py:164`) emits one `RUN_RECOVERED` event with
`payload={"open_intents": True}` and does nothing else.

`[FACT]` `grep -rn "spawn|parent_principal|child_principal|project_id|parent_episode|harness_digest"` over
`layer0/` and `packs/` returns two hits: `broker.py:149` (`"spawn_failed"` string) and `driver.py:170`
(`def spawn`). Multi-agent lineage does not exist in the new tree in any form.

`[INFERENCE]` This is the item with the highest retrofit cost and it is the item the Concept Lock is best
positioned to fix, because it is pure schema. Everything else on the P0 list can be changed later at the
cost of code; envelope fields can only be changed later at the cost of **the ledger's own history**.

### 4.4 The plugin substrate is the one genuinely mature new thing

`[FACT]` `layer0/registry/broker.py` is real: `subprocess.Popen` with `preexec_fn` applying POSIX rlimits
(`layer0/registry/sandbox.py:apply_rlimits` — `RLIMIT_CPU/AS/NOFILE/NPROC`), a Unix-domain socket, a
line-delimited JSON-RPC 2.0 client (`layer0/spi/jsonrpc.py`), a four-state cell FSM
(`UNINSTANTIATED → BOUND → RUNNING → TERMINATED`), a method allow-list
(`execute, health, compensate, verbs, quiesce, init`), `SIGKILL`-on-timeout containment, and grant-ceiling
intersection (`layer0/spi/ceiling.py`). `layer0/registry/worker.py` is a working child-side worker.

`[FACT]` It has **zero tests**. `grep -rl "layer0.registry.broker" test/layer0` → 0 files. Same for
`registry.worker`, `registry.sandbox`, `registry.grants`, `registry.validator`, `registry.isolation`,
`spi.jsonrpc`, `spi.ceiling`, `events.selectors` (450 lines), `events.emitter`, `kernel.provenance`,
`kernel.ports`, `scheduler.trajectory`, `scheduler.clock`.

`[INFERENCE]` The most valuable and most security-sensitive new code in the repository — a subprocess
isolation broker — is completely unexercised, inside the only tree CI protects. The 25 CI tests cover
`fold`, `envelope`, `canonical`, `blob`, `budget`, `dispatch`, `lifecycle`, `driver`, `compiler`,
`interfaces`, `parity`.

`[FACT]` `layer0/registry/isolation.py:1` is a leftover: *"Isolation broker stub. M1 exposes the interface;
subprocess cells arrive in M2."* — but M2's broker landed in `broker.py` and the stub was never removed.
`CONTAINER` and `WASM` exist as enum members with no implementation.

### 4.5 The old tree is mature and unprotected

`[FACT]` `vanguard/packages/` carries, tested but ungated: the SQLite/WAL event store; `runtime/root.py`
(1,418 lines, composition root); `runtime/governance/approvals.py` (565 lines, Ed25519 operator approval);
`adapters/sandbox/rootless.py` (rootless bubblewrap); `adapters/evaluators/{daemon,isolated,signing,gate}.py`
(the exterior signed judge, `vanguard-evaluator` console script); `agency/episode/engine.py` (693 lines);
`adapters/models/{openrouter,ollama,invocation,routing}.py` (896/164/565/154 lines);
`domain/ledger/reducer.py` (478 lines); `domain/selectors/resource_selector.py` (450 lines);
`domain/evidence/claim.py` (373 lines); `runtime/ledger/{projections,recovery}.py`.

`[FACT]` 1,119 tests, 11 failing. The failures I sampled are **stale-expectation failures, not runtime
breakage**: `test_repo_paths` expects `docs/03_sprints/evidence/preregistered_oracles.json` while
`repo_paths.py` still returns `docs/sprint6B/...`; three failures expect
`instrument_error:model_tag_absent` but get `instrument_error:provider_unreachable` because no Ollama
daemon is running locally; two expect a `generic` selector where a `process` selector is inferred.

`[INFERENCE]` The legacy tree is closer to green than CLAUDE.md's warning implies, and the residue is
mostly environment-dependent tests and one genuine stale-path bug that CLAUDE.md claims was fixed at the
v0.5.0 Foundation Lock and was not. Bringing this suite into CI is a days-scale job, not a quarter-scale
one. That materially changes the cost/benefit of the Staff lane's "defer CI to the code phase."

### 4.6 Orphans

`[FACT]` `vanguard/rust_core/` is an **empty directory** — zero files. `docs/05_adr/0006` bans
systems-language components in Phase 0. `[RECOMMENDATION]` Delete at the lock's hygiene step; it is the
physical seed of the Rust question the lock is rejecting.

`[FACT]` `vanguard-gui/` (19 files, last touched 2026-08-17), `vanguard-ide/` (22 files, 2026-08-16),
`containers/` (3 files, 2026-08-16), `lab/` (21 files, 2026-08-17), `benchmarkings/` (252 files,
2026-08-19). None are in CI. `benchmarkings/` is measurement evidence and should stay;
`lab/` is imported by `runtime/lab_driver.py` and is live. `vanguard-gui`/`vanguard-ide` are
`[UNKNOWN]` in status — SPEC §9 non-claims say GUI/TUI parity is not a backend requirement, which argues
for archival, but I have no evidence of a decision.

---

## 5. Test & CI Findings

### 5.1 CI runs one job and it is the wrong subject

`[FACT]` `.github/workflows/ci.yml` has a single job, `vanguard-living-gates`, with ten steps. Running each
on this tree:

| Step | Exit | Note |
|---|---|---|
| `test.test_repo_paths` | **1** | **CI's first step fails on `main`.** Stale `docs/sprint6B/` path in `tools/repo_paths.py`. |
| `discover -s test/layer0` | 0 | 25 tests, 0.014 s |
| `check_boundaries.py` | 0 | |
| `check_tcb_budget.py` | 0 | measures `packages/kernel` only |
| `check_domain_blindness.py` | 0 | |
| `check_isolation_policy.py` | 0 | |
| `discover -s test/packs` | 0 | |
| `check_stale_paths.py` | 0 | |
| `check_markdown_links.py` | 0 | |
| `scan_secrets.py` | 0 | |

`[FACT]` Not run by CI: `test/kernel` (9), `test/runtime` (40), `test/agency` (12), `test/adapters` (15),
`test/contracts` (8), `test/lab` (16), `test/security` (4), `test/tools` (13), `test/integration` (5),
`test/governance` (1), `test/trust` (1), `test/registry` (3), `test/benchmarks` (5), `test/apps` (1) — and
the entire TypeScript CLI suite (`npm test`, `npm run typecheck`).

`[FACT]` `tools/check_event_coverage.py` (E-COV, Invariant I-2's gate), `tools/run_active_contract_tests.py`,
`tools/run_broken_tests.py`, `tools/run_dogfood_r9.py`, `tools/check_backend_artifacts.py` are all absent
from CI. `.github/workflows/` contains only `ci.yml` and `clean-candidate.yml`.

### 5.2 Gate-by-gate Goodhart audit

For each gate: *what is the laziest incorrect implementation that still passes?*

| Gate | Class | Laziest passing implementation |
|---|---|---|
| `test/layer0/replay/test_parity.py::test_cold_fold_matches_live_terminal_state` | **FALSE CONFIDENCE** | Any `fold` that is a pure function of its input. It folds one list twice. A `fold` that ignored every event and returned a constant would pass. |
| `test_ledger_declares_forty_kinds` | **WEAK PROXY** | `EVENT_KINDS` with 40 arbitrary strings. |
| `check_event_coverage.py` (E-COV) | **FALSE CONFIDENCE** | Write `EventKind.CHILD_SPAWNED` anywhere in `layer0/scheduler/`. This is literally what `spawn()` does. Not in CI regardless. |
| `check_tcb_budget.py` | **FALSE CONFIDENCE for v0.6** | Add unlimited kernel code under `layer0/kernel/` — the file list is hardcoded to `vanguard/packages/kernel/*`. Valid as a *legacy* structural gate; measures the wrong TCB the moment convergence starts. |
| `check_domain_blindness.py` (I-7) | **VALID STRUCTURAL** | `grep -rE "\b(coding\|pytest\|ast)\b" layer0/`. Rename the concept (`repo`, `verify`, `syntax_tree`) and domain knowledge enters freely. Real but narrow. |
| `check_isolation_policy.py` (I-6) | **VALID STRUCTURAL** | Declare a privileged capability under a verb other than `proc.exec` — the check keys on that exact string. |
| `check_boundaries.py` | **STRONG STRUCTURAL** | Genuinely good: AST-level import lattice, unknown-package rejection, cycle detection, subprocess-home confinement, evaluator binding site. The best gate in the repo. |
| `check_markdown_links.py` | **WEAK PROXY** | Cite paths in backticks instead of `[](...)`. `SPEC.md`'s own citations do exactly this (§6.1). |
| `check_stale_paths.py` | **WEAK PROXY** | Cite any nonexistent path that is not on the hardcoded obsolete-prefix registry. It matches known-bad prefixes, not "resolves on disk". |
| `scan_secrets.py` | **VALID STRUCTURAL** | Pattern-based; fine for its purpose. |
| `test/packs` | **VALID STRUCTURAL** | 10 test files over the code-default pack; real but scoped to composition, not behaviour under load. |

`[INFERENCE]` The gate portfolio is **structurally strong and behaviourally hollow**. `check_boundaries.py`
would catch an architectural violation instantly. Nothing in CI would catch a scheduler that signs its own
verdicts — and nothing did.

### 5.3 The codegen drift finding

`[FACT]` Reproduced in this session:

```
$ python3 tools/codegen/generate_types.py     # exit 0
$ python3 -c "import ast; ast.parse(open('layer0/spi/types_gen.py').read())"
SyntaxError: '[' was never closed        line 196:  requests: tuple[#, ...]
```

Beyond the syntax error, the regenerated file differs semantically from the committed one:
`EffectContext.depth` loses its `= 0` default and becomes `int | None`; `TrajectoryRef.schema` loses its
`"mhf.trajectory/1"` default; `Receipt.stdout_ref` widens to `BlobRef | object | None`; `Reservation`,
`EffectRequest`, `FrozenHarness`, `HarnessManifest`, `PluginBindings`, `Proposal`, `Receipt` are emitted in
a different order with different `__all__` contents.

`[FACT]` `schemas/mhf/spi_payloads.schema.json` defines 22 types; `types_gen.py` exports ~30. The extra
types come from `effect_request.schema.json`, `event_envelope.schema.json`, `harness_manifest.schema.json`
— and the generator's handling of the cross-file `$ref` for `Proposal.requests` is what produces the `#`.

`[FACT]` `docs/SPEC.md` A-4: *"JSON Schema + JCS + golden vectors are the sole source of truth. Python
dataclasses and TS readers are generated. Hand-written mirrors are banned."* Invariant I-8: *"Specs are
generated or normative — never both … drift is a CI failure, not a register."*

`[INFERENCE]` A-4 and I-8 are currently false statements about this repository, asserted in the header of
the file that violates them. This is not a bug to file; it is a **lock precondition**. Either the axiom is
honoured (fix the generator, add a `--check` drift gate) or it is repealed by ADR. Locking concepts on top
of a schema pipeline that does not run is locking on sand.

---

## 6. Documentation Authority Findings

### 6.1 `docs/SPEC.md` cites four paths that do not exist

`[FACT]` SPEC.md's header block cites, as its version anchor and consumed inputs:
`docs/MASTER_REFACTOR_GUIDELINE_FINAL.md`, `docs/TECH_LEAD_REVIEW/CRITICAL_GAP_ANALYSIS_AND_AUDIT.md`,
`docs/TECH_LEAD_REVIEW/NEXT_GEN_META_HARNESS_SPECIFICATION.md`,
`docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md`, and `docs/archive/v045/`. None of
`docs/MASTER_REFACTOR_GUIDELINE_FINAL.md`, `docs/TECH_LEAD_REVIEW/`, `docs/archive/v045/`, or
`docs/01_specs/` exists on this tree.

`[FACT]` Mitigating: three of those files are physically present under
`docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/` (`CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` 161 lines,
`NEXT_GEN_META_HARNESS_SPECIFICATION.md` 331 lines, `01_SPECS_MIGRATION_MATRIX.md` 163 lines). They were
moved and SPEC was not updated. `docs/archive/v045/` was genuinely deleted (`dbb6998`
*"clean up README.md links after wiping docs/archive/v045"*).

`[INFERENCE]` The normative spec's chain of authority is broken in citation, mostly repairable in fact,
except for `docs/archive/v045/` which SPEC ranks as the lowest tier of authority and which no longer
exists. CLAUDE.md still directs readers there. Both gates that should have caught this
(`check_markdown_links`, `check_stale_paths`) are blind to backticked paths and to
paths-that-simply-do-not-resolve.

### 6.2 The execution board describes a different project than the code

`[FACT]` `docs/03_sprints/sprint_active.md` is the only file in `docs/03_sprints/`. Front-matter:
`status: ACTIVE`, `milestone: M0`, `branch: feat/substrate_upgrade`, `last_reviewed: 2026-08-18`. Its §3
"Explicitly not this sprint" lists: *"`layer0/` scaffolding · `schemas/mhf/` · … `coding_*` re-extraction
into `packs/` (M3)"*. All three have shipped. Its §2 verification block includes
`python3 tools/check_schema_archaeology.py` and `python3 -m unittest test.test_repo_paths` — the latter
fails on `main`. Its plan pointers `docs/03_sprints/plans/m1-m2-lanes.md` and
`docs/03_sprints/plans/m0-code-and-purge.md` do not exist (the latter's content is at
`docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/m0-to-m4-code-and-purge-todos.md`).

`[FACT]` Two incompatible roadmaps are live. `docs/02_roadmap/milestones.md` describes **M0–M6** and
explicitly renumbers "v0.6.0 Molecular Lattice" onto M3. The commit history describes **W1–W5** ("Wave 1
… Wave 5 - Done") and `aether-v1-roadmap-waves.md` describes a wave ladder. Nothing on the tree maps M-n
to W-n.

`[INFERENCE]` The Foundation Lock's own governance artifacts (`sprint_active.md`, `milestones.md`) went
stale within one sprint of being written, while the work proceeded under a numbering scheme they do not
acknowledge. **This is the failure mode a Concept Lock must not repeat.** A lock that produces documents
which no gate verifies and no board tracks will be stale by the third wave, exactly as this one was.

### 6.3 ADR log: 84 files, one accepted reversal, no index

`[FACT]` `docs/05_adr/` holds 84 files. Five contain "superseded". The set is heterogeneous: `00NN-*.md`
are the VG-09 decision register migrated verbatim; `ADR-M0-*.md` are new Foundation-Lock decisions;
`DEFERRED_REJECTED.md` is the VG-10 register.

`[FACT]` Live contradictions I can evidence:
- ADR-0001 *"TypeScript on a Node-compatible runtime for the control plane"* vs ADR-0069-numbered entry
  *"The control plane is Python. ADR-0001 is reversed."* — the reversal is recorded, but CLAUDE.md still
  presents the repo as *"a stdlib-only Python core plus a TypeScript/Ink CLI/TUI client, managed as an npm
  workspace"*, and the `vg` CLI is 36 TypeScript source files.
- ADR-0005 *"No runtime extension discovery; registries freeze at composition"* vs `docs/SPEC.md` §2, which
  describes hot-swap. The Staff lane resolves this for ADR-0005; I agree (§13).
- ADR-0010 (SQLite WAL) vs `layer0/events/store.py` (in-memory only) — §4.2.
- ADR-0006 *"No systems-language components in Phase 0"* vs an empty `vanguard/rust_core/` directory and
  the *Full Refactor v3.1* proposal for a Rust core.
- `docs/SPEC.md` §1 names `layer0/` as the M1 destination; the Staff lane's P0-1/P0-2 reverse this.

`[FACT]` The Staff lane reports a missing `docs/05_adr/INDEX.md` and a "documented hole" at ADR-0067. I did
not independently verify the INDEX contents; `[UNKNOWN]` on my evidence, but their claim is specific enough
to act on.

### 6.4 Schemas: two generations, both live

`[FACT]` `schemas/v4/` holds ~40 schemas plus golden vectors (writer + `.reader.` profiles, conformance
vectors under `schemas/v4/vectors/`). `schemas/mhf/` holds four: `effect_request`, `event_envelope`,
`harness_manifest`, `spi_payloads`. The v4 set is the old tree's contract surface; the mhf set is the new
tree's, and is the (nominal) input to `tools/codegen/generate_types.py`.

`[INFERENCE]` Two schema generations with no declared relationship is the documentation equivalent of the
two-runtime problem, and it is the *harder* of the two to unwind, because `schemas/v4/vectors/` is the
project's accumulated cross-language conformance evidence (ADR-0054 *"Vector agreement establishes schema
equivalence"*). The mhf set has no vectors. `[RECOMMENDATION]` The Concept Lock must state the mapping:
mhf schemas are the v0.6 wire contract, v4 vectors are retained as regression evidence, and every mhf
schema gains a vector before it is called normative.

---

## 7. `vanguard/packages/` vs `layer0/` Assessment

### 7.1 Equivalence map

| Concept | `vanguard/packages/` | `layer0/` | Relationship |
|---|---|---|---|
| JCS canonicalisation | `domain/canonicalisation/jcs.py` (226) + `digest.py` (24) | `events/canonical.py` (238) | **Near-identical copy**, 39-line diff, layer0 merges the digest helpers |
| Resource selectors | `domain/selectors/resource_selector.py` (450) | `events/selectors.py` (450) | **Copy**, import-path retarget |
| Kernel (8 modules) | `kernel/*` (1,658) | `kernel/*` (1,258) | **Stripped copy**; behaviour equivalent, rationale removed |
| Event envelope | `domain/ledger/events.py` (349) | `events/envelope.py` (103) | **Divergent** — layer0 is a fresh, thinner design |
| Reducer / fold | `domain/ledger/reducer.py` (478) + `state.py` (222) | `events/fold.py` (151) | **Divergent** — layer0 is a fresh, much smaller reducer |
| Event store | `adapters/stores/event_store.py` (SQLite/WAL) | `events/store.py` (`MemoryLedger`, 28) | **Regression** — new tree has no durable store |
| Blob / CAS | `adapters/stores/blob_store.py` (89) | `events/blob.py` (52) | Divergent; layer0 fsyncs the file, not the dir |
| Composition | `runtime/root.py` (1,418) | `compose/compiler.py` (129) | **Divergent** — layer0 is the manifest compiler A-5 describes; root.py is the wiring monolith |
| Scheduler | `agency/episode/engine.py` (693) | `scheduler/driver.py` (232) | **Divergent** — layer0 driver is a skeleton with fabricated verdicts |
| SPI | *(none)* | `spi/*` (780) | **layer0 only** — genuine new value |
| Plugin registry/broker | *(none)* | `registry/*` (923) | **layer0 only** — genuine new value, untested |
| Model adapters | `adapters/models/*` (2,349) | *(none)* | packages only |
| Sandbox (bwrap) | `adapters/sandbox/rootless.py` (248) | `registry/sandbox.py` (49, rlimits only) | packages only for filesystem isolation |
| Exterior evaluator | `adapters/evaluators/*` (~850) | `spi/interfaces.py::IEvaluationGate` | packages only; layer0 has the *request* interface, no judge |
| Governance / Ed25519 | `runtime/governance/*` (786) | *(none)* | packages only |
| Recovery / projections | `runtime/ledger/*` (560) | `scheduler/driver.py::recover` (5 lines) | packages only |

### 7.2 Direction

`[RECOMMENDATION]` **CONVERGE, ASYMMETRICALLY, WITH DELETION DATES.** Specifically, and this is where I go
further than the Staff lane's "delete duplicated layer0 modules only after a later parity gate":

- **Canonical:** `vanguard/packages/`. Its lattice (`domain ← ports ← kernel ← agency ← runtime → adapters`)
  is enforced by the best gate in the repo, and it holds every ADR-mandated capability the new tree lacks.
- **Promote into `packages/`, in place, and keep:** `layer0/spi/` (interfaces, jsonrpc, result, ceiling,
  types_gen), `layer0/registry/` (broker, worker, sandbox, validator, lifecycle, grants),
  `layer0/compose/compiler.py`, `layer0/events/taxonomy.py`. These are the genuine deliverables of W1–W5.
  `check_boundaries.py:30` already sanctions `adapters → layer0_spi`; four adapters already consume it.
- **Delete, do not merge:** `layer0/kernel/*` and `layer0/events/{canonical,selectors,envelope,fold,
  emitter,store,blob}.py`. A merge implies a semantic reconciliation; there is nothing to reconcile —
  they are a copy of `packages/` modules minus their rationale, plus a durability regression. Merging them
  means re-deriving which of 384 diff lines in `dispatch.py` were intentional. Deleting them costs the
  `layer0/events/envelope.py` + `fold.py` designs, which are genuinely better than
  `domain/ledger/events.py` + `reducer.py` — so those two, and only those two, should be **ported as
  replacements** under `domain/ledger/`, carrying their tests.
- **Rejected alternatives.** *Keep layer0 as canonical* — rejected, it would require rebuilding WAL,
  bubblewrap, Ed25519 governance, the evaluator daemon, four model adapters and recovery, all of which
  exist and are tested. *Rebuild both into a new `core/`* (the *Parecer v4* position) — rejected as a third
  identity; the repo has demonstrated it cannot keep two trees coherent. *Restructure both* — rejected as
  unbounded.

`[FACT]` The cost of "converge eventually" is measurable and is being paid now: `layer0/kernel/dispatch.py`
and `vanguard/packages/kernel/dispatch.py` have already diverged by 384 lines and both are live.

**The critical scheduling point.** The Staff lane says delete after a parity gate. A parity gate cannot be
built while CI's behavioural subject *is* the tree to be deleted. `[RECOMMENDATION]` Reverse the order:
switch the CI subject of record to `packages/` **first** (it is a days-scale job, §4.5), then the parity
gate can be written against a protected canon, then delete.

---

## 8. Current Architecture Conflict Matrix

| # | Conflict | Normative says | Code does | Severity |
|---|---|---|---|---|
| C-1 | Exterior judge | ADR-0004, SPEC preamble: judge unreachable from judged | `driver.py:138` emits `verdict: "pass"` unconditionally | **CRITICAL** |
| C-2 | Generated types | A-4, I-8: generated, drift is CI failure | `types_gen.py` hand-written; generator emits invalid Python; no gate | **CRITICAL** |
| C-3 | Replay | I-4: fold reconstructs, diffed against live state each CI run | Test folds one list twice | **CRITICAL** |
| C-4 | Durable ledger | ADR-0010: transactional embedded store with WAL | `layer0` has `MemoryLedger` only; `append_intent` is a list | **HIGH** |
| C-5 | CI subject | I-2/I-4/I-5 all presuppose behavioural CI | CI runs 25 tests in 14 ms; 1,119-test suite ungated and red | **HIGH** |
| C-6 | Canonical tree | SPEC §1: `layer0/` is the M1 destination | Production capability lives in `packages/` | **HIGH** |
| C-7 | Envelope lineage | Multi-agent P0 needs `project_id`/`parent_*`/`harness_digest` | None exist; `LedgerEmitter.emit()` drops `episode_id` and `causation_id` | **HIGH** |
| C-8 | Hot-swap | SPEC §2 describes it | ADR-0005 forbids it; no implementation | MEDIUM |
| C-9 | Control-plane language | ADR-0069: Python | 36-file TypeScript CLI; CLAUDE.md documents npm workspace | MEDIUM |
| C-10 | Roadmap | `milestones.md`: M0–M6, sprint board at M0 | History at W5; `sprint_active.md` forbids what shipped | MEDIUM |
| C-11 | Spec citations | SPEC is the authority root | Four cited paths do not exist | MEDIUM |
| C-12 | TCB budget | ADR-0038: ceiling covers the TCB | Gate hardcoded to `packages/kernel`; `layer0/kernel` unbudgeted | MEDIUM |
| C-13 | Schemas | A-4: one schema source of truth | `schemas/v4/` (40 + vectors) and `schemas/mhf/` (4, no vectors) both live | MEDIUM |
| C-14 | No systems language | ADR-0006 | Empty `vanguard/rust_core/`; *Full Refactor v3.1* proposes a Rust core | LOW |

---

## 9. Concept & Primitive Review

Disposition for each concept in the directive's list. **KEEP / REFINE / GENERALIZE / MERGE / REMOVE /
DEFER / UNRESOLVED.** My guiding rule: *lock a concept only if getting it wrong forces a ledger migration
or a kernel rewrite.* Everything else is above the plugin line and should be allowed to move.

### 9.1 Lock now (irreversible if wrong)

| Concept | Disposition | Rationale |
|---|---|---|
| **Event / EventEnvelope** | **REFINE — lock the field set** | The one thing that cannot be retrofitted without rewriting history. Add `project_id`, `parent_principal_id?`, `parent_episode_id?`, `harness_digest`. Fix `LedgerEmitter.emit()` so the kernel path carries `episode_id`/`causation_id`. |
| **EffectRequest** | **KEEP AS-IS** | `verb, args, selector, sink, reservation`. One frozen type, one schema (I-1). Already coherent in both trees. |
| **Receipt** | **REFINE** | Add `lease_id` and `grant_digest`. Today a Receipt cannot be tied back to the authority that permitted it. |
| **Principal** | **REFINE — make it a type** | Currently a bare `str` everywhere (`EffectContext.principal: str`). A `Principal` with `id`, `parent_id?`, `depth` is the anchor for every attenuation invariant. Locking it as a string is the mistake that makes spawn unbuildable. |
| **Capability / Grant** | **KEEP AS-IS** | `kernel/grants.py` is sound: `descriptorDigest` binding refused at issuance (K-18), point-of-effect verification (S8), no silent intersection (K-26). Best-designed thing in the repo. |
| **Attenuation** | **KEEP AS-IS** | Deny-whole-on-overbroad is right, and the reason (denial is the intrusion signal) is right. Do not soften. |
| **Reservation / Budget** | **KEEP AS-IS** | Six integer dimensions (ADR-M0-07), overrun retained-when-negative (K-07). Correct. |
| **Lease** | **REFINE** | Exists as `parent_lease: str \| None` on `EffectContext`. Needs to be a first-class value with an owner and a lifecycle, because budget lineage across spawn hangs off it. |
| **SinkClass** | **KEEP AS-IS** | `pure` / `observation` / `privileged`, all three recorded (ADR-0078). Locked and correct. |
| **Evaluator / SignedVerdict** | **KEEP AS-IS conceptually, REPAIR in code** | Concept is the moat. `driver.py:138` must read a signed verdict or emit nothing. |
| **Ledger** | **KEEP AS-IS** | `State = fold(Events)`, SQLite WAL, JSONL export only. |
| **CAS / ArtifactRef / BlobRef** | **REFINE** | Content-addressed bytes, events hold refs. Fix directory fsync; stop reusing `CheckpointCreated` for blob writes. |
| **FrozenHarness / HarnessManifest** | **KEEP AS-IS** | `Harness = f(manifest, plugins)`, content-addressed digest (A-5). The separability thesis operationalised. |
| **Spawn** | **REFINE — lock semantics, not engine** | Lock `Capabilities(child) ⊆ Capabilities(parent)` and `Budget(child) ≼ remaining(parent)`. Delete the mock. |

### 9.2 Refine, but the lock is cheap to revise

| Concept | Disposition | Rationale |
|---|---|---|
| **Episode** | **REFINE** | Well-established (`agency/episode/engine.py`). ADR-0080 already says a tool is not an Episode; keep that line. Needs `parent_episode_id`. |
| **Agent** | **REFINE** | `Agent = Principal + HarnessInstance` is right and costs nothing to lock, because both halves are already locked. |
| **HarnessInstance** | **REFINE** | Currently implicit. Naming it is what makes the Agent definition non-circular. |
| **Trajectory** | **REFINE — lock the schema, not the pipeline** | See §16; the *only* Phase-2 artifact expensive to retrofit. |
| **Projection** | **KEEP AS-IS** | `Projection = f(Ledger)`, rebuildable, never authoritative. Correct and already implemented in `runtime/ledger/projections.py`. |
| **Scheduler** | **KEEP AS-IS** | Sequential (I-11). Lock the interface, defer concurrency. |
| **Plugin / SPI** | **KEEP AS-IS** | Five SPIs (ADR-M0-03), wire-first JSON-RPC/UDS. |
| **Model** | **KEEP AS-IS** | Behind `ModelPort`. Stays a first-party port in v0.6. |
| **Context** | **KEEP AS-IS** | An SPI. Everything about *how* it compiles is plugin strategy. |
| **Tool / Toolkit** | **KEEP AS-IS** | An SPI with `ToolSchema`. |

### 9.3 Explicitly **refuse to lock** in v0.6

This is my main structural disagreement with a 40-concept lock.

| Concept | Disposition | Rationale |
|---|---|---|
| **Project** | **UNRESOLVED — blocking** | The Staff lane's P0-7 makes `project_id` the consistency unit and P0-5 makes it a mandatory envelope field. **`Project` does not exist anywhere in code, schema, or SPEC.** Locking a mandatory field whose referent is undefined guarantees it is populated with a placeholder forever. Either lock a one-paragraph definition (below) or use `root_episode_id` and defer. |
| **Task** | **DEFER** | No implementation. Overlaps Episode and goal-string. Locking it invents a hierarchy nothing needs yet. |
| **Skill** | **DEFER** | `domain/artifacts/skill_index.py` + `runtime/skill_index.py` exist but are unexercised by CI. Above the plugin line. |
| **Memory** | **DEFER (SPI shape only)** | Lock `IMemory`'s four calls; refuse to lock what a memory *is*. |
| **Orchestrator** | **DEFER** | Named in proposals, absent in code. Locking a component that does not exist is how you get `root.py`. |
| **Cache** | **DEFER** | `Cache = g(Ledger, CAS)` is a fine principle and needs no lock; it constrains nothing. |
| **Experiment / Promotion** | **DEFER (P3)** | Gated on the 200-task statistical-power suite (M5). No evidence exists to lock on. |
| **Meta-Harness** | **DEFER (P3)** | SPEC §9 already refuses the release pipeline. Keep refusing. |
| **ChildPrincipal** | **MERGE into Principal** | Not a separate type — a `Principal` with `parent_id` set. A separate type creates two attenuation paths, and two paths is how K-26 gets bypassed. |
| **MetaAgent / Swarm Participant** | **MERGE into Agent** | Same recursive abstraction; the difference is policy, not kind (§11). |

`[RECOMMENDATION]` If `Project` is to be locked, the minimum viable normative definition is:
*A **Project** is a durable, named scope root that owns one ledger stream, one capability ceiling, and one
root budget. Every Episode, Principal, and Artifact belongs to exactly one Project. `project_id` is the
consistency unit: total ordering is guaranteed within a Project and not across Projects.* That is enough
to make the field meaningful and small enough to be true. If the lock cannot commit to that, drop the
field.

---

## 10. Recommended Concept Lock Model

The v0.6 Concept Lock this lane recommends is **four planes and one obligation rule**.

```
                     ┌──────────────────────────────────────────────┐
  STRATEGY PLANE     │  planner · memory · context · compression    │  plugins, over the wire
  (replaceable)      │  indexing · tools · skills · model routing   │  freeze at composition
                     │  reflection · evaluation gates               │
                     └──────────────────────────────────────────────┘
                                        │ SPI (JSON-RPC 2.0 / UDS / line-delimited)
                     ┌──────────────────────────────────────────────┐
  DECISION PLANE     │  scheduler · kernel S0–S12 · attenuation     │  who / when / how much
  (mechanism)        │  grants · budget governor · plugin lifecycle │  never authoritative
                     └──────────────────────────────────────────────┘
                                        │ Decision → DurableEvent
                     ┌──────────────────────────────────────────────┐
  STATE PLANE        │  ledger (SQLite WAL) · pure reducers ·       │  what happened
  (authoritative)    │  CAS · projections · snapshots               │  fold is the only truth
                     └──────────────────────────────────────────────┘
                                        │ subject (read-only, signed)
                     ┌──────────────────────────────────────────────┐
  JUDGEMENT PLANE    │  exterior evaluator · signed verdicts        │  unreachable from the judged
  (exterior)         │  separate identity, separate process         │  no plugin, no port, no import
                     └──────────────────────────────────────────────┘
```

**The obligation rule (this lane's distinctive contribution).**

> No concept enters the v0.6 Concept Lock without (a) one sentence of normative definition, (b) the name
> of the test that fails if it is implemented wrongly, and (c) the specific wrong implementation that test
> rules out.

Applied to the P0 set, that produces:

| Locked concept | Bound falsifier | Wrong implementation it rules out |
|---|---|---|
| Envelope lineage | `test_every_emitted_envelope_carries_full_lineage` | A `LedgerEmitter.emit()` that drops `episode_id`/`causation_id` — i.e. today's code |
| `State = fold(Events)` | `test_cold_reader_reconstructs_live_state_from_disk` | Folding the same in-memory list twice — i.e. today's test |
| Evaluator exteriority | `test_scheduler_cannot_produce_a_verdict_without_a_signature` | `emit(VERDICT_RECORDED, {"verdict": "pass"})` — i.e. today's `driver.py:138` |
| Spawn attenuation | `test_child_grant_wider_than_parent_is_denied_whole` | A `spawn()` that emits `ChildSpawned`/`ChildReturned` and executes nothing |
| Generated types | `test_codegen_is_idempotent` / `generate_types.py --check` in CI | A hand-edited file headed `DO NOT EDIT` |
| Durable intent (K-47) | `test_intent_survives_process_death` | `self.intents.append(event)` |
| Budget lineage | `test_child_budget_debits_parent_remaining` | Independent child budgets |
| Grant binding (K-18) | already exists: `MF-KRN-003/005` | — (this one is genuinely locked) |

Note that six of the eight falsifiers rule out something the repository does *right now*. That is the
point: a lock whose obligations are all already satisfied has locked nothing.

---

## 11. Multi-Agent & Recursive Agency Assessment

**`Agent = Principal + HarnessInstance`, `SubAgent = ChildPrincipal + HarnessInstance`** —
**AGREE WITH MODIFICATION.**

`[RECOMMENDATION]` Drop `ChildPrincipal` as a distinct type. A sub-agent is an `Agent` whose `Principal`
has `parent_id` set. One type, one attenuation path, one lineage rule. Two types means two code paths
through `attenuation.covers()`, and K-26's "no silent intersection" guarantee is only as strong as the
number of paths that can reach it.

**`Agent` / `SubAgent` / `MetaAgent` / `Swarm Participant` share one recursive abstraction** — **AGREE.**
The differences are entirely in *policy* (who may spawn whom, with what ceiling, under what coordination
rule) and *not* in mechanism. A `MetaAgent` is an Agent whose harness's planner proposes harness mutations;
that is a plugin, not a kind. A swarm is N Agents plus a coordination policy; ADR-0003 (agent-loop primary,
no runtime workflow graph) already forbids the alternative and should stand.

**`spawn(parent, harness, capabilities, budget)`** — **AGREE WITH MODIFICATION.**

`[RECOMMENDATION]` The signature should be `spawn(parent_principal, harness_digest, requested_scope,
requested_reservation) -> Principal | Denial`, returning a denial value rather than raising, so that the
denial is an event (`AuthorizationDenied` / `BudgetExhausted`) rather than an exception. Today's
`driver.py:170` `spawn()` silently `return`s on depth exhaustion after emitting `BUDGET_EXHAUSTED` — a
caller cannot distinguish "spawned" from "denied".

**Invariants** — **AGREE, both, unconditionally.**

- `Capabilities(child) ⊆ Capabilities(parent)` — this is exactly `kernel/attenuation.py::covers()`, which
  already exists and is correct. Spawn should *call it*, not reimplement it.
- `Budget(child) ≼ RemainingBudget(parent)` — component-wise on all six dimensions. `[FACT]` The governor
  already supports parent leases (`BudgetDenied` carries the dimension); this is wiring, not design.

**Semantics to lock now.**

| Field | Lock? | Reasoning |
|---|---|---|
| `principal_id` | **LOCK** | Must become a typed value, not a `str` |
| `parent_principal_id` | **LOCK** | Nullable; absence means root. Retrofit cost = ledger rewrite |
| `episode_id` | **LOCK** (exists) | Fix the emitter that drops it |
| `parent_episode_id` | **LOCK** | Same argument |
| `harness_digest` | **LOCK** | `D_H`. Without it, no A/B attribution is possible, and attribution is the moat |
| `causation_id` / `correlation_id` | **LOCK** (exist) | Fix the emitter path |
| `budget lineage` | **LOCK** (as `lease_id` on Receipt + parent lease on reservation) | |
| `capability lineage` | **LOCK** (as `grant_digest` on Receipt) | |
| `project_id` | **CONDITIONAL** | Only with the §9.3 definition. Otherwise use `root_episode_id` |
| `ownership` | **DEFER** | Derivable from `principal_id` + lineage; a separate field is premature |
| `evaluation identity` | **LOCK** | The verdict's signing key identity must be in the envelope, or "exterior" is unverifiable after the fact |

**Logical agents vs execution workers** — **AGREE.** `K` active workers `<< N` logical agents. Lock the
distinction in the *vocabulary and the schema* now (an Agent is a ledger identity; a worker is a runtime
resource), execute sequentially. This costs one sentence in SPEC and saves a migration.

**Heterogeneous harnesses** — **AGREE, and it is free.** Since `spawn` takes a `harness_digest`, a child
running a different harness than its parent is already expressible. Do not add machinery for it.

**Concurrency timing / shared resources** — **DEFER.** See §15.

**Do not lock:** swarm coordination policies, agent-to-agent messaging, delegation protocols, negotiation.
`[INFERENCE]` These are the parts of every multi-agent design that get rewritten, and none of them
constrain the envelope.

---

## 12. Event Sourcing / Ledger / CAS / Graph Assessment

**`State = fold(Events)`** — **AGREE, and it is currently unproven.** §5.2, C-3.

**`Projection = f(Ledger)`, `Cache = g(Ledger, CAS)`** — **AGREE.** Both are already true in
`packages/runtime/ledger/projections.py`. Neither needs a lock beyond one sentence, because neither
constrains anything: they are statements that projections and caches are *derivable and disposable*.
`[RECOMMENDATION]` Lock the negative form instead, which does constrain: *no projection, index, cache, or
snapshot may be the sole record of any fact.* That is the falsifiable version.

**Relationship model.** `[RECOMMENDATION]`

```
Ledger        authoritative, append-only, hash-chained, SQLite WAL, per-project stream
CAS           immutable bytes, sha256-addressed; events carry refs, never payloads > N bytes
Reducers      pure, total, versioned; fold(events) -> State with no I/O
Snapshots     optimisation only; every snapshot carries the seq it summarises and is
              reproducible by replaying from 0 — CI proves it by discarding them
Projections   read models; rebuildable; may lag; never authoritative
Indexes       projections with a query contract
Memory        an SPI over projections + CAS; never a second write path to truth
Telemetry     a projection whose schema is the DPO harvest schema (I-9)
Graph         a projection (see below)
```

**Execution graphs** — **EVENT-DERIVED PROJECTION.** This is the strongest position in the Staff lane's
P0-4 and I endorse it without modification. The causal relations `spawned_by`, `caused_by`, `depends_on`,
`produced`, `consumed`, `evaluated_by`, `derived_from`, `invalidated_by` are all **already recoverable**
from `causation_id` + `correlation_id` + payload refs, *provided §11's lineage fields are locked*. Building
graph infrastructure would create a second write path to truth, which is the one thing the state plane
forbids.

`[RECOMMENDATION]` Lock exactly this: *the execution graph is a projection; there is no graph store, no
graph database, and no workflow DAG engine. If a relation cannot be derived from the ledger, the fix is a
new envelope field or event kind, never a graph write.* That single sentence closes the question
permanently and is cheap to verify (`grep` for a graph dependency).

**Replay taxonomy** — **AGREE with the Staff lane's four-way split** (state replay must be deterministic;
schedule replay needs recorded nondeterminism; real-world re-execution need not match; byte-identical
fixtures only for fully controlled inputs). This is a genuinely good contribution and I would adopt it
verbatim. `[RECOMMENDATION]` Add the falsifier: the CI replay gate must be *state replay from a cold
reader against a file on disk*, not a re-fold of an in-memory list.

---

## 13. Plugin Architecture Assessment

**Plugin-first direction** — **AGREE.**

**Above the boundary (replaceable):** planner, memory, context, compression, cache strategy, indexing, AST
processing, heuristics, tools, scripts, skills, model routing, reflection, evaluation *gates*,
self-improvement strategies, Meta-Harness strategies. **AGREE with the Staff lane's list, with one
correction:** "evaluation gates" above the line is correct, but must be stated as *the gate that
**requests** judgement is a plugin; the judge is not*. The current code shows why the distinction matters —
`IEvaluationGate` is above the line and `driver.py:138` used that freedom to invent the verdict.

**Below the boundary (mechanism):** identity, authority, effect mediation, event semantics, resource
conservation, plugin lifecycle, core scheduling mechanism. **AGREE, add two:** *canonicalisation* (JCS is
identity; a plugin that could change it could change every digest) and *the ledger write path*.

**Semantic boundary.** `[RECOMMENDATION]` Five SPIs (ADR-M0-03): `IPlanner`, `IMemory`, `IToolkit`,
`IContext`, `IEvaluationGate`. Do not add a sixth in v0.6. `[FACT]` `layer0/spi/interfaces.py` already
defines these.

**Physical isolation boundary.** `[RECOMMENDATION]` **Wire-first.** Line-delimited JSON-RPC 2.0 over a Unix
domain socket is the contract (ADR-0002, ADR-0059). `in_process` is an isolation *privilege* granted by
policy that still speaks the same wire over loopback — **not** a second SPI. This is the Staff lane's P0-8
and I agree with it completely; it is the single decision that prevents the "protocol drift between the
fast path and the safe path" failure that kills most plugin systems.

`[FACT]` This is already built: `layer0/spi/jsonrpc.py`, `layer0/registry/broker.py`,
`layer0/registry/worker.py`, method allow-list, rlimits, SIGKILL containment. `[FACT]` It has zero tests.
`[RECOMMENDATION]` The lock's proof obligation for the plugin boundary is a broker test suite — fault
injection, timeout kill, rlimit enforcement, ceiling intersection, illegal FSM transition — before the
boundary is called locked.

**Language strategy.** **Python-first. AGREE, and it is not close.** `[FACT]` The core is stdlib-only
Python with one dependency (`cryptography`). `[FACT]` `vanguard/rust_core/` is empty. `[FACT]` ADR-0006
bans systems-language components in Phase 0. `[FACT]` The wire is language-neutral by construction, so a
future Rust or Go plugin costs nothing architecturally.

**DISAGREE with *Full Refactor v3.1*'s Rust core.** Introducing a third implementation identity beside two
Python trees that already cannot stay coherent (§7) is the highest-risk available move, and the evidence
for it — performance — has not been measured. `[FACT]` No benchmark on this tree identifies a TCB hot path.

`[RECOMMENDATION]` Lock the reversal condition instead: *Rust (or any systems language) enters only when a
profiling artifact in `benchmarkings/` names a specific TCB hot path exceeding a stated latency budget, and
enters as a subprocess plugin over the existing wire, never as a replacement core.*

**Protobuf / gRPC / WASM / container** — **DEFER (P3), with named entry conditions.** JSON Schema 2020-12
+ JCS is normative (ADR-0008/0009/0041) and has golden vectors; Protobuf would discard that evidence.
`CONTAINER` and `WASM` already exist as `IsolationTier` enum members — that is the correct amount of
anticipation. `[RECOMMENDATION]` Keep the enum, implement neither.

**Generated bindings** — **AGREE in principle, currently broken.** See C-2. `[RECOMMENDATION]` Fixing
`tools/codegen/generate_types.py` and adding a `--check` drift gate to CI is a **lock precondition**, not a
follow-on task, because A-4 is one of the seven axioms the whole architecture rests on.

---

## 14. Authority & Security Assessment

### 14.1 Semantics to lock now

1. **Principal identity is a typed value with a parent link and a depth.** Not a `str`.
2. **Capabilities carry resources, not only verbs** (ADR-0011/0036). Already true; keep.
3. **Attenuation denies whole; it never silently intersects** (ADR-0012, K-26). Already true; keep, and
   apply it to `spawn` rather than writing a second check.
4. **Every effect passes the dispatch path; there is no second path** (ADR-0021/0037, S0–S12). Already true.
5. **Grants bind exactly one descriptor and are verified at the point of effect** (K-18/CT-51, S8). Already
   true and refused-at-issuance. This is the strongest piece of design in the repository.
6. **All three sink classes are recorded; only `privileged` requires a grant** (ADR-0078). Keep.
7. **The judge is exterior**: separate process, separate identity, signed verdicts, unreachable from agent
   and from every plugin (ADR-0004, ADR-M0-08). **Lock, and repair — see C-1.**
8. **Budget lineage is conserved**: a child can never hold more than the parent's remaining, in every one of
   the six dimensions, and commit debits reality including overruns (K-07).
9. **Plugins are untrusted by default** (I-6). In-process is a privilege granted by policy.
10. **Provenance labels combine downward only** (K-28). Already true.
11. **Revocation is an event.** `CapabilityRevoked` exists in the taxonomy; the semantics — a revoked grant
    fails S8 at the point of effect, not at the next request — should be stated normatively.
12. **Artifact ownership follows Principal lineage**, and an artifact's provenance label is the meet of its
    inputs'.

### 14.2 Hardening to defer

- Remote attestation, TPM/secure enclave, signed plugin distribution.
- WASM isolation tier; container tier (M3 target, keep as enum).
- seccomp-bpf filters beyond the current rlimits (`layer0/registry/sandbox.py` is rlimits-only; SPEC §3 and
  the M2 gate mention seccomp — `[FACT]` it is not implemented).
- Key rotation and multi-operator quorum for Ed25519 approvals.
- Network egress policy for plugin cells.
- Supply-chain verification of plugin manifests.

`[RECOMMENDATION]` Do not let any of these become v0.6 architecture. The v0.6 authority story is complete
if the twelve semantics above hold; every item in 14.2 is a later tier that plugs into the same seams.

### 14.3 The one security finding that is not deferrable

`[FACT]` `layer0/scheduler/driver.py:138`. A component inside the agent's own process writes
`VERDICT_RECORDED / verdict: pass` into the authoritative ledger without a signature, without reading the
gate's response, and the CI-gated replay test folds it as truth. `[INFERENCE]` Every measurement produced
by the new tree is, as of today, self-certified. `[RECOMMENDATION]` The Concept Lock should state
explicitly that **an unsigned verdict is not a verdict**, and that `VerdictRecorded` payloads without a
verifiable signature over `subject_digest` are a hard ledger validation failure — enforced by the reducer,
so no emission path can bypass it.

---

## 15. Resource & Concurrency Assessment

**`Logical Agent ≠ Execution Worker`** — **AGREE. Lock the distinction, defer the machinery.**

**`K` active workers `<< N` logical agents** — **AGREE as a design constraint**, `[UNKNOWN]` as a
performance claim on this tree (no measurements exist).

`[RECOMMENDATION]` What v0.6 semantics must represent even while execution stays sequential:

| Must be in v0.6 semantics | Why | Cost if deferred |
|---|---|---|
| Agent identity is independent of execution state | An Agent must be able to exist without a worker | Ledger migration |
| `independence_groups` on `Proposal` | Already exists in `types_gen.py`. Declares which requests may run concurrently | High — planners would need retraining |
| Selector-based independence | `resource_selector.py` already computes overlap; that *is* the concurrency safety predicate | High |
| Per-project consistency unit | Total order within a project, none across | Ledger migration |
| Reservation as a hierarchy | Parent lease already on `EffectContext` | Medium |
| Idempotency keys | Already on the envelope | — |
| `MAX_CONCURRENCY = 1` as a *configured value*, not an assumption | Lets the gate flip without a redesign | Medium |

**Defer entirely:** worker pools, shared model runtime, copy-on-write workspaces, sparse agent activation,
vector clocks, distributed coordination, NATS, k8s. `[FACT]` ADR-0024 already asserts concurrency safety
via "reads precede writes"; ADR-0007 (parallel from the first loop commit) is superseded by I-11.

`[INFERENCE]` The single most valuable concurrency preparation already exists and is unused: the resource
selector overlap relation. Independence is *already computable*; the scheduler simply runs one at a time.
That means flipping concurrency on later is a scheduler change, not an architecture change — which is
exactly the position a lock should aim for, and it argues strongly for deferring.

---

## 16. Meta-Harness / Self-Improvement Assessment

**`H0 → Execution → Trajectory → Candidate → H1 → Experiment → Exterior Evaluation → Promotion/Rejection`**
— **AGREE as a target, DEFER as v0.6 architecture.** `docs/SPEC.md` §9 and ADR-0032 already refuse the
in-place self-modification pipeline, and that refusal should stand verbatim.

Separating the six adaptation kinds:

| Kind | v0.6 disposition |
|---|---|
| Runtime adaptation (model routing, tier escalation) | **Already exists** (`runtime/tier_escalation.py`, `model_selection.py`). Plugin strategy. No lock. |
| Memory adaptation | **DEFER** — SPI shape only |
| Composition adaptation (new manifest = new `FrozenHarness`) | **ANTICIPATE, free** — A-5 already makes this expressible. A candidate harness is just another manifest with a different digest |
| Plugin synthesis | **DEFER (P3)** |
| Model adaptation (DPO harvest, distillation) | **DEFER (P3, M6)** |
| Core modification | **REFUSE PERMANENTLY** — SPEC §9, A-6 |

**The one thing I would lock now that the Staff lane leaves to P3: the Trajectory record schema.**

`[FACT]` Today's trajectory is content-free. `layer0/scheduler/driver.py::_trajectory` returns a
`TrajectoryRef` whose digest is over `{schema, run_id, episode_id, principal, n}` — where `n` is the count
of envelopes. It identifies nothing about what happened.

`[FACT]` Invariant I-9: *"Telemetry is a dataset. Every episode terminates in a trajectory record that is,
without transformation, a valid row in the DPO harvest schema."*

`[INFERENCE]` I-9 is the only Phase-2 requirement that is **expensive to retrofit**, because it constrains
what every episode must have *recorded while it ran*. A harness-mutation engine can be built at any time; a
year of episodes that did not record the fields the harvest needs cannot be recovered. Every other
Meta-Harness component consumes trajectories and can be written later.

`[RECOMMENDATION]` Lock the trajectory record's *schema* (prompt/context digest, proposal, effect
descriptors, receipts, signed verdict, harness digest `D_H`, runtime digest `D_R`, cost in all six
dimensions) and its emission point. Lock nothing about how it is consumed. Cost: one schema. Value: Phase 2
becomes a build rather than a migration.

**Identity trinity `D_H` / `D_R` / `D_X`** — **AGREE, adopt verbatim.** Separating harness composition from
execution environment from experiment cell is correct, and `[FACT]` today's `FrozenHarness.digest` conflates
them by omission (`D_R` and `D_X` do not exist). This is a genuinely strong contribution from the Staff lane
and I would not modify it.

**Do not build:** an autonomous release pipeline, in-place core mutation, an agent with write access to its
own harness definition, or a promotion mechanism without a preregistered statistical gate (M5's 200-task
power requirement is right).

---

## 17. CI & Gate Assessment

Detailed audit in §5.2. Summary and recommendations.

| Gate | Class | Recommendation |
|---|---|---|
| `check_boundaries.py` | **STRONG STRUCTURAL** | Keep unchanged. Extend to cover `packs/`. |
| `scan_secrets.py` | VALID STRUCTURAL | Keep. |
| `test/packs` | VALID STRUCTURAL | Keep. |
| `check_domain_blindness.py` | VALID STRUCTURAL | Keep; retarget from `layer0/` to the converged core. |
| `check_isolation_policy.py` | VALID STRUCTURAL | Keep; broaden from the literal `proc.exec` verb to any privileged sink. |
| `check_tcb_budget.py` | FALSE CONFIDENCE for v0.6 | Retarget to the converged kernel; today it measures the wrong tree. |
| `check_markdown_links.py` | WEAK PROXY | Add backticked-path resolution. Would have caught C-11. |
| `check_stale_paths.py` | WEAK PROXY | Replace prefix-registry matching with does-this-path-resolve. |
| `check_event_coverage.py` (E-COV) | FALSE CONFIDENCE | **Replace, do not wire in as-is.** A lexical grep for a kind name is satisfied by dead code. Replace with a coverage assertion over an executed scenario suite: every declared kind is emitted by at least one *passing behavioural test*. |
| `replay/test_parity.py` | FALSE CONFIDENCE | **Rewrite.** Cold reader, from disk, diffed against live terminal state, per I-4. |
| `test.test_repo_paths` | Currently RED on `main` | Fix the stale `docs/sprint6B/` constant. |
| *(missing)* codegen drift | — | **Add.** `generate_types.py --check` must be a gate, or A-4 is repealed. |
| *(missing)* production suite | — | **Add.** `test/kernel test/runtime test/agency test/adapters test/contracts test/security test/governance`. |
| *(missing)* CLI suite | — | **Add** `npm run typecheck && npm test`, or archive the CLI. |
| *(missing)* verdict signature | — | **Add.** No `VerdictRecorded` without a verifiable signature. |
| *(missing)* mutation score | — | M1's gate calls for ≥80% on kernel + reducers. Not implemented. Highest-value *behavioural* gate available, and the natural enforcement mechanism for §10's obligation rule. |

`[RECOMMENDATION]` One structural change to how gates are chosen: **every gate must name the wrong
implementation it rejects, in its own docstring.** `check_boundaries.py` effectively does this and is the
best gate here. E-COV does not, and is the worst. This is cheap, and it is the mechanism that makes §10's
obligation rule self-enforcing over time.

---

## 18. Review of Principal Staff Engineer Proposals

### 18.1 `001_V060_concept_phase_BETA.md` — the twelve locked P0s

| P0 | Verdict | Note |
|---|---|---|
| **P0-1** Python-first, packages canonical, no Rust, no `aether-rust/` | **AGREE** | Evidence-backed; `rust_core/` is empty; no hot path measured |
| **P0-2** layer0 is a copy-fork; converge, don't rebuild; no third tree | **AGREE WITH MODIFICATION** | Direction right. I would set deletion dates and **delete rather than merge** `layer0/kernel` + most of `layer0/events` (§7.2), and reverse the ordering: CI subject first, then parity gate, then delete |
| **P0-3** Decision plane vs authoritative state plane | **AGREE** | Clean, correct, cheap |
| **P0-4** Recursive machine; graph is an event projection; ADR-0003 stands | **AGREE** | Strongest item in the set |
| **P0-5** Spawn invariants + required envelope fields | **AGREE WITH MODIFICATION** | Adopt the invariants unchanged. `project_id` cannot be mandatory while `Project` is undefined (§9.3). Also: spawn must *call* `attenuation.covers()`, and `LedgerEmitter.emit()` must stop dropping `episode_id`/`causation_id` — otherwise the mandate is unimplementable on the current emitter |
| **P0-6** Identity trinity `D_H`/`D_R`/`D_X` | **AGREE** | Adopt verbatim. Best original contribution in the corpus |
| **P0-7** Hybrid ES, CAS, replay taxonomy, project consistency unit, SQLite WAL | **AGREE WITH MODIFICATION** | Adopt the four-way replay taxonomy verbatim. Add the falsifier (§12) — the current replay gate is a tautology and the Staff doc does not identify this |
| **P0-8** Wire-first JSON-RPC/UDS; five SPIs; `in_process` as privilege; ADR-0005 freeze stands | **AGREE** | Adopt unchanged. Add the broker test suite as the lock's proof obligation |
| **P0-9** Evaluator exterior; F1 is a defect | **AGREE, ESCALATE** | They classify F1 as a defect to fix later. I classify it as the reason the CI change cannot wait: the gate that certified a self-signing judge is the gate ratifying the lock |
| **P0-10** Semantics now, sequential execution | **AGREE** | Add: `MAX_CONCURRENCY` must be a configured value, and selector-based independence is already computable |
| **P0-11** CI is false confidence; production lattice is subject of record; **implementing it is the next phase** | **AGREE ON DIAGNOSIS, DISAGREE ON SEQUENCING** | See §18.3 |
| **P0-12** Defer Meta-Harness, WASM, attestation, multi-host, graph DB, third language, pytest, competence graph | **AGREE, ONE EXCEPTION** | Lock the **trajectory record schema** now (§16). It is the only P3 item with an irreversible retrofit cost |

### 18.2 The other four documents

**`principal_engineer_proposal.md`** (4,460 lines) — the conceptual north star. **AGREE** on the recursive
substrate, the plane separation, the plugin-first framing, and the identity trinity. `[INFERENCE]` Its risk
is volume: 4,460 lines of proposal against a 9k-word normative SPEC will not survive contact with a sprint
board unless it is compressed to decisions with falsifiers. The BETA doc already does most of that
compression well.

**`Vanguard-substrate-060-full-refactor-v3-1.md`** — Rust core beside both Python trees. **DISAGREE.**
§13. A third implementation identity in a repo that cannot maintain two, justified by unmeasured
performance, against an accepted ADR-0006. The BETA doc already rejects it and I concur without
reservation.

**`vanguard-substrate-060-execution-plan.md`** — treats `layer0/` as the v0.6 production target with an
exit date for `vanguard/packages/`. **DISAGREE**, and my evidence is stronger than the BETA doc's: it is not
merely that `packages/` is more mature, it is that `layer0/` **violates an accepted ADR on durability**
(C-4), **fabricates verdicts** (C-1), and **ships a hand-written file claiming to be generated** (C-2). It
is not a production target; it is a prototype that CI mistook for one.

**`vanguard-arquitetura-v4-parecer-e-plano.md`** — new top-level `core/` tree; evaluator as a product
plugin. **DISAGREE on both**, same reasoning as the BETA doc. The evaluator-as-plugin idea is the more
dangerous of the two: it is exactly the move that produced C-1, where an evaluation *gate* above the plugin
line took the liberty of producing the verdict.

**`aether-v1-roadmap-waves.md`** — **DEFER.** Out of scope for a Concept Lock, and the tree already has two
un-reconciled roadmaps (§6.2). Adding a third before the first two are reconciled would compound C-10.

### 18.3 The one sequencing disagreement, stated precisely

The BETA doc's P0-11 says: *"That is a false-confidence gate, not a v0.6 architecture. … **Implementing**
the CI change is the first code-phase task, not this phase."*

`[INFERENCE]` I think this is the one place the Staff lane's otherwise disciplined scope control works
against it. The argument for deferring is clean: a Concept Lock produces documents, not code, and CI is
code. The argument against is that **the lock's evidence base is the CI system**, and that system has just
been shown to certify a self-signing judge, a tautological replay proof, a hand-written generated file, and
a mock spawn — all green.

Locking twelve P0 decisions under gates in that state means the lock's claim "the production lattice is
canonical" is ratified by a CI run that never executes the production lattice.

`[RECOMMENDATION]` A narrow carve-out, not a scope explosion: the Concept Lock phase may make **exactly
three** mechanical changes, all of which are evidence-restoring rather than architecture-setting:

1. Add the existing `test/kernel test/runtime test/agency test/adapters test/contracts test/security
   test/governance` discovery to `ci.yml`, allowed to be non-blocking (`continue-on-error`) for one
   release so the baseline is *visible* without being a merge gate.
2. Fix the stale `docs/sprint6B/` constant in `tools/repo_paths.py` so CI's first step passes on `main`.
3. Add `generate_types.py --check` as a non-blocking reporting step.

None of these decides an architecture question. All three make the lock's own claims checkable. If even
that is out of scope, then the lock should state in writing that its P0s were ratified under gates known to
be non-behavioural — which is an honest and acceptable alternative, but it should be said out loud.

---

## 19. What I Would Keep

1. **The separability thesis.** *What solved it must be separable, and the judge must be unreachable from
   the judged.* It is the project's identity and its only real moat.
2. **The S0–S12 dispatch sequence, exactly as ordered.** Every ordering rule (K-04 resolve-before-lease,
   K-05 verify-at-effect, K-06 release-before-emit, K-07 overrun-debited, K-08 classifier-is-a-call, K-47
   durable-intent-first) encodes a defect that actually shipped. Do not reorder, do not "simplify."
3. **`check_boundaries.py`** and the hexagonal lattice it enforces. Best engineering artifact in the repo.
4. **Grant/descriptor binding (K-18)** refused at issuance rather than at use.
5. **Attenuation denies whole (K-26).** Including the reasoning: a child repeatedly over-asking is the
   strongest intrusion signal this system shape produces, and silent narrowing discards it.
6. **Six-dimension integer `Reservation`.** No floats in the governor.
7. **JCS + golden vectors** as identity, and `schemas/v4/vectors/` as accumulated cross-language evidence.
8. **SQLite WAL ledger, JSONL as export only** (ADR-0010).
9. **`Harness = f(manifest, plugins)`, content-addressed** (A-5).
10. **Five SPIs, wire-first, freeze at composition** (ADR-M0-03, ADR-0005).
11. **SPEC §9's refusals** — no continuous learning claim, no self-release pipeline, no competence graph,
    no metaphysical taxonomy. The honour table is one of the healthiest things in this repository.
12. **`layer0/spi/` and `layer0/registry/`.** The real deliverable of W1–W5.
13. **The append-only ADR log with mandatory reversal conditions** (ADR-0000).
14. **`benchmarkings/`** as measurement evidence.

## 20. What I Would Change

1. **CI's subject of record** → the production lattice, plus the codegen drift check and a verdict-signature
   check. §17, §18.3.
2. **`LedgerEmitter.emit()`** → carry the full lineage set on the kernel path, not just on `emit_kind()`.
3. **The replay-parity test** → cold reader from disk, diffed against live terminal state (I-4).
4. **E-COV** → behavioural emission coverage over passing tests, not a lexical grep.
5. **`tools/codegen/generate_types.py`** → make it produce the committed file, or repeal A-4 by ADR.
6. **`Principal`** → from `str` to a typed value with `parent_id` and `depth`.
7. **`Receipt`** → add `lease_id` and `grant_digest` so effects trace to their authority.
8. **`TrajectoryRef`** → a real record, not a digest of `{run_id, episode_id, principal, n}`.
9. **`check_tcb_budget.py`** → retarget to the converged kernel.
10. **`check_markdown_links.py` / `check_stale_paths.py`** → resolve backticked paths; check existence, not
    a prefix registry.
11. **`docs/SPEC.md` §1** → `packages/` is the production implementation of Layer-0 concerns; `layer0/` is a
    fork under convergence. Repair the four dangling citations.
12. **`docs/03_sprints/sprint_active.md`** → mark superseded; it currently forbids work that shipped.
13. **`CLAUDE.md`** → `v0.4.5-beta` → v0.6 concept-lock pointer; remove the `docs/archive/v045/` pointer to a
    deleted directory; reconcile the TypeScript-client framing with ADR-0069.
14. **Blob durability** → fsync the directory; stop reusing `CheckpointCreated` for CAS writes.

## 21. What I Would Remove or Avoid

1. **`layer0/kernel/*` and the duplicated `layer0/events/*`** — delete after CI retarget; port only
   `envelope.py`, `fold.py`, `taxonomy.py` as replacements (§7.2).
2. **`layer0/scheduler/driver.py::spawn()`** — delete. A mock that satisfies a gate is worse than an
   unimplemented feature, because it makes the gate lie.
3. **The unconditional `verdict: "pass"` / `INVALIDATION_CHECKED ok: True` / `CLAIM_RECORDED` emissions** —
   delete. Emit nothing rather than emit fiction.
4. **`vanguard/rust_core/`** — empty directory; delete.
5. **`layer0/registry/isolation.py`** — superseded stub.
6. **A Rust core** — §13.
7. **A third top-level tree (`core/`, `aether-rust/`)** — §7.2.
8. **A graph database or workflow-DAG engine** — §12, ADR-0003.
9. **Hot-swap in v0.6** — ADR-0005 wins; strike from SPEC §2.
10. **A third roadmap** — reconcile M0–M6 and W1–W5 before adding waves.
11. **`ChildPrincipal` as a distinct type** — §11.
12. **Any new gate that greps for a name** — §17.

## 22. What I Would Explicitly Defer

With the deferral stated as a decision, not an omission, each with a named reversal condition:

| Deferred | Reversal condition |
|---|---|
| Concurrent execution | A measurement showing sequential execution is the binding constraint on the lab's throughput |
| Worker pools, CoW workspaces, sparse activation | Concurrency is enabled |
| WASM / container isolation tiers | A plugin exists that cannot be safely run under subprocess + rlimits |
| seccomp-bpf beyond rlimits | A threat model naming a syscall-level escape |
| Protobuf / gRPC | A wire profiling artifact showing JSON-RPC framing is a bottleneck |
| Rust or any systems language | A profiling artifact naming a TCB hot path over a stated budget |
| Meta-Harness promotion, plugin synthesis, distillation | The 200-task statistical-power suite exists (M5 prerequisite) |
| `Project`, `Task`, `Skill`, `Orchestrator`, `Experiment` as locked concepts | A second domain pack exists that needs them |
| Multi-host / distributed | Never in v0.6; requires a new ADR |
| pytest migration | Never blocks architecture; unittest works |
| Competence graph | Permanently refused (ADR-M0-10, SPEC §9) |
| GUI / IDE clients | SPEC §9 says parity is not a backend requirement |

---

## 23. P0 Decisions — Lock Before Development

Structural, high rework cost if postponed.

| # | Decision | Evidence |
|---|---|---|
| **P0-A** | **Envelope lineage set is normative and mandatory:** `project_id?`, `principal_id`, `parent_principal_id?`, `episode_id`, `parent_episode_id?`, `harness_digest`, `causation_id`, `correlation_id`, `idempotency_key`, `prev_digest`, `seq`. `LedgerEmitter.emit()` must carry all of them. | §4.3 — the only irreversible retrofit |
| **P0-B** | **`vanguard/packages/` is canonical.** `layer0/` is a fork under directed absorption. No third tree. No Rust core. | §7 |
| **P0-C** | **Absorption direction is explicit:** promote `layer0/{spi,registry,compose,events/taxonomy}`; **delete** `layer0/kernel` and duplicated `layer0/events`; **port** `envelope.py` + `fold.py` as replacements under `domain/ledger/`. | §7.2 |
| **P0-D** | **Four planes:** strategy (plugins) / decision (mechanism) / state (authoritative) / judgement (exterior). Ledger is the only authority on what happened. | §10 |
| **P0-E** | **`Agent = Principal + HarnessInstance`;** sub-agent is a Principal with `parent_id`. One recursive abstraction. Swarm is policy. | §11 |
| **P0-F** | **Spawn invariants:** `Capabilities(child) ⊆ Capabilities(parent)` via `attenuation.covers()`; `Budget(child) ≼ remaining(parent)` on all six dimensions. Denial returns a value and emits an event. | §11 |
| **P0-G** | **Identity trinity `D_H` / `D_R` / `D_X`.** `FrozenHarness.digest` is `D_H` only. | §16 |
| **P0-H** | **Execution graph is a projection.** No graph store, no DAG engine. Missing relations are fixed by envelope fields, never by graph writes. | §12 |
| **P0-I** | **Plugin boundary is the wire.** Line-delimited JSON-RPC 2.0 over UDS. Five SPIs. `in_process` is a privilege over the same wire. Freeze at composition (ADR-0005). | §13 |
| **P0-J** | **Evaluator exteriority, enforced at the reducer.** An unsigned `VerdictRecorded` is a ledger validation failure, not a defect to be caught in review. | §14.3 |
| **P0-K** | **Durability:** SQLite WAL is the ledger; `append_intent` is durable before S9 or the effect is `UNDETERMINABLE`. In-memory ledgers are test doubles only. | §4.2 |
| **P0-L** | **Trajectory record schema** is locked; its consumers are not. | §16 |
| **P0-M** | **The obligation rule:** no concept is locked without a named falsifier and the wrong implementation it rejects. | §10 |
| **P0-N** | **CI subject of record is the production lattice.** Non-blocking is acceptable for one release; absent is not. | §18.3 |

## 24. P1 Decisions — Lock or Deliberately Defer

Each must be marked, in writing, `LOCK NOW` or `DEFER DELIBERATELY`.

| # | Decision | My call |
|---|---|---|
| P1-1 | `project_id` mandatory in the envelope | **LOCK NOW** — with the §9.3 definition, else use `root_episode_id` |
| P1-2 | `Principal` as a typed value rather than `str` | **LOCK NOW** — P0-F is unimplementable otherwise |
| P1-3 | `Receipt` carries `lease_id` + `grant_digest` | **LOCK NOW** — capability lineage is unverifiable otherwise |
| P1-4 | A-4/I-8 (generated types) honoured or repealed | **LOCK NOW** — currently a false statement (C-2) |
| P1-5 | `schemas/mhf` vs `schemas/v4` relationship | **LOCK NOW** — mhf is the v0.6 wire contract; v4 vectors retained as regression evidence |
| P1-6 | SPEC §2 hot-swap struck; ADR-0005 stands | **LOCK NOW** |
| P1-7 | `MAX_CONCURRENCY` a configured value = 1 | **LOCK NOW** — free, and makes P1-8 cheap |
| P1-8 | Concurrent execution | **DEFER DELIBERATELY** — reversal condition in §22 |
| P1-9 | Revocation semantics (fails at point of effect) | **LOCK NOW** — one sentence |
| P1-10 | Provenance meet over artifact inputs | **LOCK NOW** — K-28 already implies it |
| P1-11 | Control-plane language: TypeScript CLI's status | **LOCK NOW** — Python control plane (ADR-0069); the CLI is a client, and either enters CI or is archived |
| P1-12 | Roadmap reconciliation M0–M6 ↔ W1–W5 | **LOCK NOW** — a naming decision, not a plan; C-10 |
| P1-13 | Mutation-score gate on kernel + reducers | **DEFER DELIBERATELY** to the first code wave, but name it in the lock as P0-M's enforcement mechanism |
| P1-14 | TypeScript conformance suite for the plugin wire | **DEFER DELIBERATELY** |
| P1-15 | pytest migration | **DEFER DELIBERATELY** — never blocks architecture |
| P1-16 | `vanguard-gui` / `vanguard-ide` disposition | **LOCK NOW** — archive or gate; an ungated client tree is C-10 in miniature |

## 25. P2 Decisions — Safe to Defer

Implementation choices that must not block the v0.6 architecture: directory layout inside `packages/`;
whether `root.py` is split (it should be, but it is refactoring, not architecture); logging format;
`simple_yaml.py` vs a YAML dependency; CLI ergonomics; TUI framework; error-message wording; test-naming
conventions; whether `benchmarkings/` is reorganised; container base images; the exact rlimit values;
JSON-RPC batch support; snapshot cadence; index implementation; blob GC policy.

## 26. P3 / Research

Meta-Harness promotion and genome mutation; plugin synthesis; DPO harvest and model distillation;
self-improvement strategies; calibrated escalation; skill harvest; WASM isolation; remote attestation;
multi-host distribution; a competence graph (permanently refused); a third control-plane language;
neuro-symbolic planning; agent-to-agent negotiation protocols; economic budget markets across agents.

## 27. Unknowns / Required Experiments

| # | Unknown | Experiment |
|---|---|---|
| U-1 | Is `K ≪ N` (bounded workers, many agents) actually the right scale model? | No workload measurement exists. Spike: instrument a 20-episode dogfood run for worker occupancy |
| U-2 | Is the `packages/` suite green after the four environment-dependent tests are fixed? | Fix the stale `repo_paths` constant, mark the Ollama-dependent tests as requiring a live daemon, re-run. Days-scale, and it decides §18.3's cost |
| U-3 | What is the real cost of subprocess-per-plugin at coding-pack turn rates? | Benchmark `broker.call()` round-trip against in-process. Decides whether `in_process` privilege is ever needed |
| U-4 | Do `schemas/mhf` and `schemas/v4` describe compatible envelopes? | Diff `event_envelope.schema.json` against `schemas/v4/event-envelope.schema.json`. Decides whether ledger migration is needed at convergence |
| U-5 | Is `layer0/events/fold.py` (151 lines) semantically complete relative to `domain/ledger/reducer.py` (478)? | Property test: fold both over the same event stream, diff terminal state. Decides "port" vs "rewrite" in P0-C |
| U-6 | Does the bubblewrap sandbox still work on current kernels/WSL2? | Run `test/security`. It is not in CI and I did not isolate its result |
| U-7 | `docs/05_adr/INDEX.md` completeness and the ADR-0067 hole | Not independently verified; the Staff lane's claim is specific |
| U-8 | Is 200 tasks actually sufficient statistical power for M5? | Power calculation against the observed effect size in `benchmarkings/` |
| U-9 | Status of `vanguard-gui` / `vanguard-ide` | No decision found in any ADR |

---

## 28. Recommended Architecture & Concept Lock Sequence

Six steps. Steps 0–4 are documents; step 0 is three mechanical, non-architectural changes.

**Step 0 — Restore the evidence base (days).** The three carve-outs in §18.3: production suite into CI
(non-blocking), fix `tools/repo_paths.py`, codegen `--check` as a reporting step. Purpose: the lock's own
claims become checkable. If the lock phase refuses this, it must record in writing that its P0s were
ratified under non-behavioural gates.

**Step 1 — Forensic register.** One document, facts only, every claim `file:line` or command output. The
Staff lane's Phase A/B structure is good; adopt it. It must include the conflict matrix (§8) and the gate
Goodhart audit (§5.2), because those are the two tables that justify everything downstream.

**Step 2 — Lock the fourteen P0s (§23), each with its falsifier (§10).** No concept without an obligation.
This is the deliverable.

**Step 3 — Mark every P1 `LOCK NOW` or `DEFER DELIBERATELY` (§24)**, each deferral with a reversal
condition. A P1 left unmarked is the failure mode that produced C-8 and C-10.

**Step 4 — ADRs and SPEC v0.6.** Approximately the Staff lane's ADR-0069…0073 cluster, plus two this lane
adds:
- one on **A-4/I-8 disposition** (honour or repeal — P1-4), and
- one on **proof obligations** (P0-M): every locked concept names its falsifier.

SPEC edits: §1 dual-lattice paragraph, §2 strike hot-swap, §8 invert the migration direction, add the
four-planes and Agent/spawn sections, repair the four dangling citations, retarget `docs/archive/v045/`.

**Step 5 — Hygiene that is part of the lock.** `CLAUDE.md` version + archive pointer + TS framing;
`sprint_active.md` superseded note; delete `vanguard/rust_core/`; reconcile the M/W numbering (P1-12).
Explicitly **not** a new roadmap.

**Exit gate.** Every P0 has an ADR citation in SPEC **and a named falsifier**; every P1 is marked; SPEC has
no TBD and no longer names `layer0/` as the M1 destination; the conflict log lists every rejected
supporting-doc item; the working tree contains no architecture implementation; no commit without explicit
request.

**Next phase (not the lock):** as-built gap and migration classification, then one operational plan, then
code — starting with CI subject-of-record made blocking, the C-1 verdict repair, and the P0-A envelope
fields. Not a Rust rewrite. Not a third runtime.

---

## 29. Suggested Documentation Changes — DO NOT APPLY

Recommendations only. Nothing below was performed.

**`docs/SPEC.md`** — version anchor → v0.6.0 Concept Lock; repair the four dangling citations (§6.1);
rewrite §1 (packages canonical, layer0 a fork under absorption); §2 strike hot-swap, state wire-first,
state that `IEvaluationGate` requests but never produces judgement; §8 invert the migration direction; add
§ on the four planes, Agent/spawn, and the identity trinity; add I-12 *"every locked concept names the test
that falsifies it"*; note `pyproject.toml` is still `0.4.5b1`.

**`docs/04_annex/KERNEL.md`** — amend only where a v0.6 sentence would otherwise contradict it. Do not
rewrite S0–S12. Add the K-47 durability note that an in-memory intent list does not satisfy it.

**`docs/04_annex/MEASUREMENT.md`** — add the trajectory record schema (§16) and the `D_H`/`D_R`/`D_X`
separation.

**`docs/05_adr/`** — the 0069–0073 cluster; plus one ADR on A-4/I-8 disposition and one on proof
obligations. Add the missing `ADR-M0-*` rows to `INDEX.md`. Record ADR-0005 winning over SPEC §2 hot-swap
by citation, per ADR-0000's append-only rule.

**`docs/02_roadmap/milestones.md`** — **do not rewrite** (correctly out of scope), but add one status note
mapping M0–M6 to the shipped W1–W5, or C-10 persists through the lock.

**`docs/03_sprints/sprint_active.md`** — one note: superseded by the v0.6 Concept Lock. Its §3 currently
forbids work that has shipped.

**`CLAUDE.md`** — version pointer; remove the `docs/archive/v045/` reference (deleted); reconcile the
TypeScript-client framing with ADR-0069; note that CI does not run the full suite; correct the claim that
the `repo_paths` stale-path bug was fixed at v0.5.0 (`test.test_repo_paths` fails on `main`).

**Archive:** `docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/` should keep
`CRITICAL_GAP_ANALYSIS_AND_AUDIT.md`, `NEXT_GEN_META_HARNESS_SPECIFICATION.md`, and
`01_SPECS_MIGRATION_MATRIX.md` in place — SPEC cites them as consumed inputs, so SPEC's citations should be
repaired to point here rather than the files being moved again.

## 30. Suggested Roadmap Implications — DO NOT APPLY

Not a roadmap; consequences a future roadmap must absorb.

1. The lock creates a **convergence wave** that does not exist in either M0–M6 or W1–W5. It is the largest
   single work item implied and must be sized, not assumed.
2. **CI retarget precedes convergence**, not the reverse (§7.2). Any plan that deletes `layer0/` before
   `packages/` is gated is deleting the only tested tree.
3. **C-1 (verdict fabrication) is a stop-ship for measurement.** Every benchmark produced through
   `layer0/scheduler/driver.py` since W1 is self-certified and should be re-labelled as such in
   `benchmarkings/` before it is cited as evidence for anything.
4. **P0-A envelope fields are a ledger migration.** Every existing ledger either gets a migration or is
   declared v0.5-format and read-only. Doing it at the lock costs one schema; doing it in v0.7 costs a
   migration tool and a compatibility layer.
5. **M5's 200-task suite is the real Phase-2 gate**, and nothing in the current plans is building it. It is
   the longest-lead item in the entire programme and should start in parallel with the convergence wave.
6. **The trajectory schema (P0-L) must land before the convergence wave completes**, or the episodes run
   during convergence are not harvestable.
7. **Reconciling M0–M6 with W1–W5 is a prerequisite** to any third numbering scheme.

---

## 31. Risks and Trade-offs

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-1 | **The lock ratifies under gates known to be hollow.** Twelve to fourteen P0s decided while CI certifies a self-signing judge as green. | **High** — it is the default path | §18.3's three carve-outs, or an explicit written caveat |
| R-2 | **Convergence stalls and the two trees persist another two waves.** Already happened once; `dispatch.py` has diverged 384 lines. | **High** | P0-C's explicit direction + deletion dates; CI retarget first |
| R-3 | **Locked concepts become slogans.** The Foundation Lock's I-1…I-11 are excellent and at least four are currently false. | **High** — precedent exists | P0-M: every concept names its falsifier. This is the mitigation for R-3 specifically |
| R-4 | **Over-locking.** Locking 40 concepts including `Project`, `Task`, `Skill`, `Experiment`, `Meta-Harness` on zero implementation evidence produces the migration debt the lock exists to prevent | Medium | §9.3's explicit refusals, stated as decisions |
| R-5 | **Under-locking the envelope.** Deferring lineage fields means a ledger migration later, or losing history | Medium | P0-A is the highest-value single decision in this report |
| R-6 | **Three lanes, one lock.** Three independently reasoned proposals (Staff, Arch, Tech Lead) need a synthesis owner and a tie-break rule, or the lock becomes a union of three plans | **High** | Name the synthesis owner and the conflict rule *before* the reports are compared |
| R-7 | **Deleting `layer0/kernel` loses an intentional improvement** buried in the 384-line `dispatch.py` diff | Low–Medium | U-5's property test before deletion |
| R-8 | **Legacy suite is worse than it looks** and CI retarget costs weeks, not days | Low–Medium | U-2 measures it directly, and it is cheap |
| R-9 | **The exterior evaluator is slow enough that people route around it** — which is arguably what C-1 already is | Medium | Treat C-1 as a signal about evaluator ergonomics, not only as a defect |
| R-10 | **Documentation staleness recurs.** `sprint_active.md` went stale within one sprint | **High** | Only gated documents stay true; extend link/stale gates (§17) |

**The central trade-off.** Adding proof obligations to every locked concept (P0-M) makes the lock slower
and narrower. That is the cost. The benefit is that the resulting lock is *falsifiable* — a later engineer
can run one command and learn whether a locked concept is still true. The Foundation Lock did not have
this property, and four of its eleven invariants are currently false while CI is green. I would take the
narrower lock.

---

## 32. Final Independent Tech Lead Recommendation

**Adopt the Principal Staff Engineer lane's architecture. Reject its sequencing. Narrow its scope.**

On architecture we substantially agree, and I would not spend the programme's time re-litigating it:
Python-first; one production lattice at `vanguard/packages/`; `layer0/` absorbed, not enthroned; no Rust,
no third tree, no graph database, no workflow-DAG engine; decision plane versus authoritative state plane;
`Agent = Principal + HarnessInstance` with subset invariants on capability and budget; graph as projection;
identity trinity `D_H`/`D_R`/`D_X`; wire-first JSON-RPC/UDS with five frozen SPIs; exterior signed judge;
SQLite WAL; sequential execution with concurrent semantics; Meta-Harness deferred.

Three modifications, in descending order of importance:

**First — the lock must carry proof obligations.** No concept is locked without a named test and the wrong
implementation that test rejects. The evidence for why is on this tree: the previous lock produced eleven
invariants of which at least four are false today — the judge is not exterior in the CI-gated tree
(`driver.py:138`), `State = fold(events)` is proven by folding one list twice, the generated types are
hand-written and the generator emits invalid Python, and emitted-equals-declared is satisfied by dead
code. Those are not implementation lapses; they are what a lock produces when its concepts have no
falsifiers. A Concept Lock that repeats that pattern at v0.6 scale will be discovered false at v0.7 scale.

**Second — restore the evidence base inside the lock phase, not after it.** Three mechanical changes:
production suite in CI (non-blocking is fine), fix the stale path constant so CI's first step passes, add
the codegen drift check as a reporting step. None decides an architecture question; all three make the
lock's claims checkable. If the lock declines, it should say in writing that its decisions were ratified
under gates known to be non-behavioural.

**Third — lock roughly twelve primitives and explicitly refuse the rest.** Lock what is irreversible:
envelope lineage, Principal as a type, capability and budget lineage on the Receipt, attenuation and
dispatch ordering, sink classes, evaluator exteriority enforced at the reducer, ledger authority and
durability, the plugin wire, the identity trinity, the trajectory schema. Refuse to lock `Project` (unless
its definition is written), `Task`, `Skill`, `Orchestrator`, `Experiment`, `Promotion`, `Meta-Harness`, and
`Cache` — they sit above the plugin line, they have no implementation to lock against, and locking them
manufactures exactly the migration debt the lock exists to prevent.

If only one recommendation survives: **lock the envelope lineage fields (P0-A)**. Everything else in this
report can be revised later at the cost of code. Envelope fields can only be revised later at the cost of
the ledger's own history — and the ledger is the only thing in this architecture that is supposed to be
true.

---

### Comparison Summary — Staff Engineer vs Independent Tech Lead

**Both agree:** Python-first, no Rust, no third tree · `packages/` canonical, `layer0/` absorbed ·
decision plane vs authoritative state plane · `Agent = Principal + HarnessInstance`, spawn subset
invariants · graph as event projection, no DAG engine, no graph DB · identity trinity `D_H`/`D_R`/`D_X` ·
hybrid event sourcing, CAS for bytes, four-way replay taxonomy, SQLite WAL · wire-first JSON-RPC/UDS, five
SPIs, `in_process` as privilege, ADR-0005 freeze · exterior signed evaluator, not a plugin · concurrency
modelled, execution sequential · Meta-Harness / WASM / attestation / distribution / competence graph
deferred · current CI is false confidence.

**Partially agree:** Convergence mechanics — they merge after a parity gate, I delete `layer0/kernel` and
duplicated `layer0/events` outright and port only `envelope.py`/`fold.py` · `project_id` — they make it
mandatory, I require a definition first or substitute `root_episode_id` · P0-12 deferrals — I lock the
trajectory schema now · replay — I adopt their taxonomy and add the falsifier they do not identify.

**Disagree:** CI sequencing. They defer implementation to the first code phase; I carve out three
mechanical, non-architectural changes inside the lock, because the lock's evidence base *is* the CI system
and that system currently certifies a self-signing judge as green.

**Where I would modify their proposal:** add proof obligations to every locked concept (their P0 list has
no falsifiers); add an ADR resolving A-4/I-8, which is currently a false statement in the header of the new
tree's most-imported file; narrow the concept list with explicit refusals rather than an implicit scope.

**Where their proposal is stronger:** the identity trinity `D_H`/`D_R`/`D_X` is a genuinely original
contribution I would adopt verbatim · the four-way replay taxonomy is more precise than anything in the
normative corpus · their scope discipline ("stop before roadmap, sprints, production code") is correct and
I would keep it, minus the three carve-outs · their conflict log against the other supporting documents
(Rust core, third `core/` tree, evaluator-as-plugin, hot-swap) is well-reasoned and I concur with every
rejection.

**Where this proposal is stronger:** the gate Goodhart audit, which identifies the mechanism (`E-COV` as a
lexical grep) that produced the artifact (mock `spawn()`) · the codegen drift finding, which invalidates an
axiom · the replay tautology, which invalidates an invariant · the TCB budget measuring the wrong tree ·
the durability regression against accepted ADR-0010 · the emitter dropping lineage on the kernel path,
which makes their P0-5 unimplementable as written · the proof-obligation rule, which is a structural answer
to why the last lock decayed.

**Insufficient evidence to choose:** `K ≪ N` as a scale model (U-1) · the true cost of CI retarget (U-2) ·
subprocess-per-plugin overhead (U-3) · mhf/v4 envelope compatibility (U-4) · whether `layer0/fold.py` is
semantically complete against `domain/ledger/reducer.py` (U-5) · sandbox viability on current kernels (U-6)
· 200-task statistical power (U-8) · GUI/IDE disposition (U-9).

---

*End of independent Tech Lead assessment. No repository artifact other than this file was created or
modified. No commit was made.*
