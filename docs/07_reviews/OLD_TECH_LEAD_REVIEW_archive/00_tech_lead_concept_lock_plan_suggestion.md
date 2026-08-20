# Vanguard / AETHER v0.6 — Independent Tech Lead Concept Lock Assessment

**Engagement:** ANALYSIS-ONLY. No code, spec, ADR, annex, roadmap, milestone, backlog, sprint, or existing
review was modified. No commit was made. This file is the sole artifact produced.
**Tree reviewed:** `main` @ `c5d5fb5`, working tree as found.
**Date:** 2026-08-20.
**Deliverable path note:** the directive names `…/tech_lead_concept_lock_plan_suggestion.md`; the referenced
placeholder that already exists on this tree is the `00_`-prefixed sibling, and this report was written
there so it sits beside `00_tech_lead_doing.md` and the `00_arch_lead_*` pair. Same content, one file.

---

## 1. Executive Summary

I ran the tests, ran every CI gate, ran the code generator, compiled the shipped harness pack, and diffed
the two runtimes. My architectural conclusions largely match the Principal Staff Engineer lane's. My
conclusion about **what the Concept Lock is for** does not.

The Staff lane's `001_V060_concept_phase_BETA.md` treats the central problem as *architectural ambiguity* —
two trees, unclear canon — to be fixed by writing ADRs 0069–0073 and SPEC v0.6, with the CI change
explicitly deferred to "the first code-phase task."

The evidence says the central problem is different: **the gate system rewards emission and structure over
behaviour**, and it has already manufactured a second runtime that looks finished and is substantially
theatre. Six findings, each reproduced on this tree in this session:

1. **The CI-gated scheduler fabricates its own passing verdict.** `layer0/scheduler/driver.py:138` emits
   `VERDICT_RECORDED payload={"verdict": "pass"}` unconditionally, after calling `self._gate.request(...)`
   and discarding the answer. It also emits `INVALIDATION_CHECKED {"ok": True}` and a `CLAIM_RECORDED`
   derived from `len(receipts)`. The exterior-judge thesis — the project's one-sentence identity — is
   inverted inside the only tree CI protects.
2. **The shipped pack's entire capability ceiling is silently discarded, and every downstream check fails
   open.** `packs/code-default/harness.yaml` declares `fs.read`, `fs.search`, `patch.apply`, `proc.exec`.
   `layer0/compose/compiler.py::_parse` never reads the `capabilities` key (nor `system_prompt`, nor
   `approval_policy`), so `FrozenHarness.capability_ceiling == ()` — I executed `compile_pack()` and
   confirmed it. `intersect_ceilings(...)` is called at `compiler.py:57` and its **return value is
   discarded**. `layer0/spi/ceiling.py:21` is `if not capabilities: return True`. `layer0/registry/grants.py:24`
   is `if key not in allowed and allowed:` — an empty harness ceiling permits every plugin capability.
   Four independent fail-open steps in one path.
3. **The CI-gated dispatch tests never execute the grant path.** `test/layer0/support.py:68` registers the
   only test verb as `ADVISORY`, so `requires_grant()` is false and S6 GRANT / S8 VERIFY are dead in every
   gated test. The best-designed code in the repository — descriptor-bound grants, refused at issuance —
   has zero CI coverage.
4. **The replay-parity gate is a tautology.** `test/layer0/replay/test_parity.py:145` computes
   `fold(store.envelopes)` and `fold(list(store.envelopes))` and asserts they are equal. It folds one list
   twice. Invariant I-4 — "diffs against live state every CI run" — is tested nowhere. Its sibling test
   asserts `len(EVENT_KINDS) == 40`.
5. **The "generated" SPI types are hand-written, and the generator emits invalid Python.**
   `python3 tools/codegen/generate_types.py --check` returns `CODEGEN FAIL: … is stale` (rc=1). Regenerating
   produces `requests: tuple[#, ...]` — `SyntaxError: '[' was never closed`. **The `--check` mode exists and
   is not wired into CI.** Axiom A-4 and Invariant I-8 are violated in the header of the most-imported file
   in the new tree, by a gate that was written and then not connected.
6. **The CI-gated behavioural suite is 25 tests in 0.014 s** over 4,556 lines of microkernel. The 1,119-test
   suite covering the SQLite/WAL ledger, Ed25519 governance, bubblewrap sandbox, the UID-10002 evaluator
   daemon, and the real episode engine **is not run by CI at all**. And CI's *first step* —
   `python3 -m unittest test.test_repo_paths` — **fails on `main` today**.

**Independent recommendation.** Lock fewer concepts, and make the lock pay for itself.

1. **The Concept Lock must ship its own proof obligations.** Every P0 concept is locked together with a
   named falsifiable test and the specific wrong implementation that test rules out. A concept without a
   bound falsifier is not locked, it is announced. This is P0, not P1.
2. **Restore the evidence base inside the lock phase.** Deferring the CI change means the lock is ratified
   under gates that just certified a self-signing judge and an unenforced capability ceiling as green.
   That is a credibility precondition, not a sequencing preference.
3. **Lock ~14 primitives; explicitly refuse to lock ~12.** The directive's list mixes irreversible substrate
   (envelope lineage, attenuation order, sink classes, evaluator exteriority) with things above the plugin
   line (Skill, Experiment, Promotion, Meta-Harness, Orchestrator). Locking the latter now is speculative.
4. **Directional convergence with deletion dates, not "absorb eventually,"** plus the duplication gate that
   only *Parecer v4* proposed and that the current lock omits. Without a detector, the fork recurs.
5. **`project_id` cannot be locked as a mandatory envelope field while `Project` is undefined.** It appears
   zero times in either tree, in SPEC, in the annexes, in the ADRs, and in the schemas.

Where the Staff lane and I converge, we converge hard, and I would not reopen any of it: Python-first, no
Rust, no third tree, no graph DB, no workflow-DAG engine, sequential execution with concurrent semantics,
JSON-RPC/UDS plugin wire, five SPIs, exterior evaluator, SQLite WAL, hybrid event sourcing, identity trinity.

---

## 2. Scope and Independence Statement

I read the Principal Staff Engineer corpus in full: `principal_engineer_proposal.md` (4,460 lines),
`vanguard-arquitetura-v4-parecer-e-plano.md` (419), `Vanguard-substrate-060-full-refactor-v3-1.md` (656),
`vanguard-substrate-060-execution-plan.md` (740), `aether-v1-roadmap-waves.md` (601), and
`001_V060_concept_phase_BETA.md` (200). I used it as evidence and intellectual input. I did not adopt its
conclusions by default and I did not manufacture disagreement. Where I differ, I differ because a command I
ran or a file I read pointed elsewhere.

Three facts shaped this lane's independence:

- `[FACT]` `001_V060_concept_phase_BETA.md` is not a proposal. It is a decision document with twelve
  "Locked P0 decisions (approve with this plan)" and a Phase-D instruction to write ADRs 0069–0073 and
  rewrite SPEC §1/§2/§8. Reviewing it as a peer proposal understates what approving it does.
- `[FACT]` `principal_engineer_proposal.md` **contradicts itself on the single most consequential question**.
  Its abstract (line 11) says recover the mature runtime from `vanguard/packages/` and take only SPI/schemas/
  broker from `layer0/`. Its body (§3.1 line ~140, §104, and §114 item 2: *"`layer0/` como runtime target
  inequívoco"*) says the opposite, and its own generality gate is `git diff layer0/ == empty`. The Staff
  lane resolves this in favour of `packages/` — correctly, in my view — but that is a **choice made by the
  BETA document**, not a conclusion inherited from the north-star document it cites as authority.
- `[FACT]` There is a third lane on this tree: `00_arch_lead_doing.md` (1,292 lines, byte-identical to
  `00_tech_lead_doing.md`) with its own empty deliverable. Three lanes, one lock. Good for the analysis, a
  risk for the lock — see §31, R-6.

---

## 3. Evidence & Investigation Method

Everything labelled `[FACT]` was produced by one of these, on this tree, in this session:

```bash
python3 -m unittest discover -s test -t .          # 1119 tests · 6 failures · 5 errors · 8 skipped
python3 -m unittest discover -s test/layer0 -t .   # 25 tests · 0.014s · OK
python3 -m unittest test.test_repo_paths           # exit=1   <-- CI's FIRST step, RED on main
python3 tools/check_boundaries.py                  # exit=0   (297 files)
python3 tools/check_tcb_budget.py                  # exit=0   1347/1438 logical lines, packages/kernel ONLY
python3 tools/check_domain_blindness.py            # exit=0
python3 tools/check_isolation_policy.py            # exit=0
python3 -m unittest discover -s test/packs -t .    # exit=0   (27 tests)
python3 tools/check_stale_paths.py                 # exit=0   (229 files)
python3 tools/check_markdown_links.py              # exit=0
python3 tools/scan_secrets.py                      # exit=0
python3 tools/check_event_coverage.py              # exit=0   "40 kinds, 100%"  <-- NOT IN CI
python3 tools/codegen/generate_types.py --check    # exit=1   "CODEGEN FAIL: stale"  <-- NOT IN CI
python3 -c "...compile_pack()"                     # capability_ceiling == ()
diff layer0/kernel/*.py vanguard/packages/kernel/*.py
diff layer0/events/canonical.py vanguard/packages/domain/canonicalisation/jcs.py
diff layer0/events/selectors.py vanguard/packages/domain/selectors/resource_selector.py
git log --reverse -- layer0 ; git log --reverse -- vanguard/packages/kernel
```

The working tree was left as found. The one mutation (running the generator without `--check`) was reverted
with `git checkout -- layer0/spi/types_gen.py`, confirmed clean by `git status --short layer0/`.

**Labels.** `[FACT]` = command output or file content on this tree. `[INFERENCE]` = reasoned from facts, not
proven. `[RECOMMENDATION]` = this lane's proposed lock decision. `[UNKNOWN]` = needs a spike.

**One anomaly to flag, not a finding.** During this session `git status` began reporting a modification to
`00_arch_lead_concept_lock_plan_suggestion.md` and two new untracked `… copy.md` files. I did not create or
touch them. If a second review lane is running concurrently against this working tree, the three lanes are
not as isolated as the design assumes.

---

## 4. Repository As-Built Findings

### 4.1 Two disjoint runtimes, one of which is nine days old

`[FACT]` Sizes and lineage:

| Tree | Py files | LOC | First commit | Character |
|---|---|---|---|---|
| `vanguard/packages/` | 126 | 21,400 | `2b38d00` (v0.4.0 foundational) | The shipping v0.4.5 runtime |
| `layer0/` + `packs/` | 51 | 5,410 | `d3af6e3` "feat(W1): Layer 0, Events and Schemas" | The MHF v1 microkernel rewrite |

`[FACT]` `layer0/` alone is **4,556 LOC against SPEC axiom A-1's stated target of ≤ 4,500**. It is already
over budget, and `tools/check_tcb_budget.py` does not measure it.

`[FACT]` The coupling is one-way and thin. Nothing in `layer0/` imports `vanguard.packages`. Four modules
under `vanguard/packages/adapters/` import `layer0.spi` — `sandbox/toolkit.py`, `stores/memory_engine.py`,
`evaluators/gate.py`, `context/window.py` — and `tools/check_boundaries.py:30` explicitly permits it
(`"adapters": {"domain", "ports", "layer0_spi"}`).

`[INFERENCE]` This is a **copy-fork that grew a real SPI**. `layer0/spi/` and `layer0/registry/` are genuine
new value the old tree has already started consuming. `layer0/kernel/` and most of `layer0/events/` are the
old modules with docstrings stripped and imports retargeted.

`[FACT]` Evidence for "stripped copy": `layer0/events/selectors.py` vs
`vanguard/packages/domain/selectors/resource_selector.py` differ **only in the import line** — 450 lines
otherwise identical, including a docstring that still directs the reader to
`vanguard/packages/domain/SEMANTICS.md`. `layer0/events/canonical.py` vs `domain/canonicalisation/jcs.py`
is a 39-line diff whose only substance is that layer0 folded in `digest_bytes`/`digest_of`/`chain_digest`.
The eight kernel pairs diff by 84/78/107/384/93/… lines, of which the large majority is comment deletion.

`[INFERENCE]` The stripping is itself a hazard. The `packages/kernel` docstrings are not decoration — they
are the only place rules `K-04 … K-48` and mutation-failure IDs `MF-KRN-001 … 009` are attached to the code
implementing them. `layer0/kernel/dispatch.py:1` reduces the whole S0–S12 rationale to one sentence. The
invariants survive as behaviour and lose their traceability to `docs/04_annex/KERNEL.md`.

### 4.2 The kernel fork silently weakened three security properties

`[FACT]` Beyond comment loss, the 384-line `dispatch.py` diff contains genuine behavioural divergence. Two
of the changes are improvements; three are weakenings.

**Improvements** (should be preserved on convergence):
- The old kernel emitted `EffectCompleted` for *any* non-grant, non-undeterminable failure, with the failure
  name as the reason — adapter errors and timeouts were logged as *Completed*. The new kernel splits into
  `EffectCompleted` (OK only) and `EffectFailed` (`layer0/kernel/dispatch.py:321`). Real bug fix.
- The new kernel emits `AuthorizationRequested` and `CapabilityAttenuated`, and splits budget denial into
  `BudgetReleased` (parent closed) vs `BudgetExhausted`. Richer, correct.

**Weakenings** (the reason "merge" is the wrong verb for this convergence):
- `layer0/kernel/dispatch.py:247` — the durable intent records `request.sink.value`, the **caller-declared**
  sink class. The old kernel recorded `self._sinks.sink_class(request.action).value`, the **registry-derived**
  one. The ledger's record of what class of effect occurred is now whatever the requester claimed.
- `layer0/kernel/dispatch.py:258` — `outcome = raw if isinstance(raw, AdapterOutcome) else AdapterOutcome("ok")`.
  Any adapter returning an unexpected value is **silently treated as success**. The old kernel had no such coercion.
- `layer0/kernel/policy.py:87` — `spans if spans is not None else ()`. The old kernel fell back to
  `request.justifying_spans`. Combined with `layer0/scheduler/driver.py:201` calling `dispatch(...)` with no
  `spans=`, the untrusted-provenance predicate (`authority_violation`, `F-09`) is **structurally unreachable
  on the layer0 happy path**.

`[FACT]` Also divergent by omission: `layer0/events/fold.py:99` handles `BudgetCommitted` by looping the
settlement and discarding it (`_ = amount`). Committed spend never enters folded state — so the CI-gated
"replay" state does not include budget, which is one of the four things I-4 names.

`[INFERENCE]` This is the concrete cost of "converge eventually". Two trees implementing one kernel have
been diverging for weeks in both directions, and the direction of each divergence has to be adjudicated
line by line.

### 4.3 The capability ceiling is dropped, then fails open four times

This is the most serious finding in the report and I reproduced every step.

`[FACT]` `packs/code-default/harness.yaml` declares a `capabilities:` ceiling containing `fs.read`,
`fs.search`, `patch.apply`, `proc.exec`.

`[FACT]` `layer0/compose/compiler.py::_parse` (lines 88–118) constructs `HarnessManifest` from `api`, `id`,
`plugins`, `budget`, `undeletable`. It **never reads `capabilities`, `system_prompt`, or `approval_policy`**.

`[FACT]` Executing the real `compile_pack()` from `packs/code-default/load.py` yields
`FrozenHarness.capability_ceiling == ()`.

`[FACT]` `layer0/compose/compiler.py:57` calls `intersect_ceilings(parsed.capabilities, plugin_ceilings[plugin_id])`
and **discards the return value**. The call is a no-op.

`[FACT]` `layer0/registry/grants.py:24` — `if key not in allowed and allowed:` — when `allowed` is empty
(which it now always is), **every plugin capability passes**. The same function compares selectors by
`repr()` (`_freeze`), so dict key ordering changes a selector's identity.

`[FACT]` `layer0/spi/ceiling.py:21` — `if not capabilities: return True`. A cell that declares no
capabilities may call anything. This module is also consumed cross-tree by
`vanguard/packages/adapters/sandbox/toolkit.py`.

`[FACT]` `layer0/spi/ceiling.py:39` re-implements a small, incorrect subset of the 450-line selector
algebra (prefix match on `root`, exact equality elsewhere) rather than calling `decide()`.

`[FACT]` None of `ceiling.py`, `registry/grants.py`, or the compiler's capability path has any test.

`[INFERENCE]` End to end, a declared capability ceiling in the only shipped harness pack is **not enforced
at any point**, and four independent fail-open defaults hide it. This is the strongest possible illustration
of the report's thesis: the structure is complete, the CI is green, and the security property is absent.

### 4.4 The new tree regressed durability

`[FACT]` `layer0/events/store.py` provides one ledger: `MemoryLedger`, *"In-memory ledger store used by the
sequential driver and replay tests."* Its `append_intent` — the `K-47` durable-intent obligation, the rule
that makes a crash between dispatch and emit *undeterminable* rather than invisible — is
`self.intents.append(event)`. `layer0/kernel/dispatch.py:249` calls it at S8a.

`[FACT]` The old tree has the real thing: `vanguard/packages/adapters/stores/event_store.py:122` is
`SqliteEventStore` with `journal_mode=WAL`, `synchronous=FULL`, `BEGIN IMMEDIATE`, per-run seq monotonicity
and rollback on `IntegrityError`. `runtime/service/inbox.py:19` is a second real WAL store.

`[FACT]` `docs/05_adr/0010-*.md`, status accepted: *"A transactional embedded store with write-ahead logging;
line-delimited JSON is export only."*

`[INFERENCE]` `layer0/` violates an accepted ADR on the single most load-bearing durability requirement, and
CI is green. This is the strongest single argument against the *Execution Plan*'s position that `layer0/` is
the v0.6 production target.

`[FACT]` `layer0/events/blob.py` writes real bytes and `os.fsync`s the file (better than the old
`blob_store.py`, which is explicitly fsync-free) but never fsyncs the directory, uses a flat layout with no
fan-out, **has no read path at all**, and emits `CHECKPOINT_CREATED` for a CAS write.

`[FACT]` `layer0/events/envelope.py` fabricates timestamps (`1970-01-01T00:00:NN.000Z`) when no stamps are
injected. There is no real clock anywhere in `layer0/`.

### 4.5 Identity and lineage are absent from both trees

`[FACT]` Grep across both trees, `.py`, excluding `__pycache__`:

| Token | `layer0/` | `vanguard/packages/` |
|---|---|---|
| `principal_id` | 0 | 0 |
| `parent_principal_id` | 0 | 0 |
| `project_id` | 0 | 0 |
| `harness_digest` | 0 | 0 |
| `parent_episode_id` | 0 | 3 |
| `causation_id` | 6 | 8 |
| `correlation_id` | 6 | 0 |

`[FACT]` `Principal` is a bare `str` everywhere. `EffectContext` is
`{principal, run_id, episode_id, depth, parent_lease, idempotency_key}` — no parent principal, no parent episode.

`[FACT]` Worse, the primary emission path drops what does exist. `layer0/events/emitter.py:38`
`LedgerEmitter.emit()` — the function the kernel uses for every event — forwards only `run_id`, `principal`,
`payload`, `alertable`. `episode_id`, `causation_id`, `correlation_id`, `idempotency_key` are dropped.
Only `emit_kind()` carries them, and no call site anywhere populates `causation_id` or `correlation_id`
with a non-`None` value. **Every kernel-emitted event in `layer0` — the entire authority trail — is
un-attributable to an episode.**

`[FACT]` What lineage does exist is at the authority layer, not the event layer:
`layer0/kernel/grants.py` has `parent_grant_id` with cascading revoke; `layer0/kernel/budget.py` has
`parent_lease_id` with parent-closure enforcement. These are correct and should be kept.

`[FACT]` `EnvelopeFactory` holds `_seq`/`_prev` as instance state initialised to `0`/`None`, with no path
that recovers the chain head from a store. `SequentialTurnDriver.recover()` emits one
`RUN_RECOVERED {"open_intents": True}` — a constant — and does nothing else.

`[INFERENCE]` This is the item with the highest retrofit cost and the item a Concept Lock is best positioned
to fix, because it is pure schema. Everything else on the P0 list can be changed later at the cost of code;
envelope fields can only be changed later at the cost of **the ledger's own history**.

### 4.6 The old tree already has the working multi-agent implementation

`[FACT]` `vanguard/packages/agency/episode/engine.py:531` implements a **real** `spawn()`: it takes
`parent_episode_id`, derives a child episode id, parses an attenuated `child_scope` **fail-closed**
(`:263–286`), threads `parent_lease`, enforces a depth ceiling, and re-enters returned provenance spans as
`Trust.AGENT_DERIVED` with source class `"spawn_return"` (`:640`).

`[FACT]` `layer0/scheduler/driver.py:170` `spawn()` emits `ChildSpawned` then immediately `ChildReturned`
with `"spans": []`. No child principal is derived, no grant attenuated, no episode created, no work done.
The CI-adjacent test asserts exactly this: `test/layer0/scheduler/test_driver.py:105` →
`assertEqual(kinds, ["ChildSpawned", "ChildReturned"])`.

`[INFERENCE]` The working recursive-agency mechanism the whole v0.6 proposal is built around **already
exists, in the tree CI does not run**, and was replaced in the tree CI does run by two event emissions that
satisfy a lexical coverage gate. That single comparison settles the canonical-tree question.

### 4.7 The plugin broker is the one genuinely mature new thing, and it is untested

`[FACT]` `layer0/registry/broker.py` is real: `subprocess.Popen` of `sys.executable -m layer0.registry.worker`,
`preexec_fn` applying POSIX rlimits (`RLIMIT_CPU/AS/NOFILE/NPROC`) plus `setsid`, a Unix-domain socket,
line-delimited JSON-RPC 2.0, a four-state cell FSM, a method allow-list, SIGTERM→SIGKILL reap, workdir cleanup.
`layer0/registry/worker.py` is a real UDS server with `chmod 0o600` (its `_dispatch` is an echo stub, which is
correct for a walking-skeleton fixture). `layer0/registry/validator.py` does real SemVer caret parsing and
recursive JSON-Schema shape validation.

`[FACT]` Test coverage, by import reference within `test/layer0`:

| Module | test files | Module | test files |
|---|---|---|---|
| `registry.broker` | **0** | `events.selectors` (450 LOC) | **0** |
| `registry.worker` | **0** | `events.emitter` | **0** |
| `registry.sandbox` | **0** | `kernel.provenance` | **0** |
| `registry.validator` | **0** | `kernel.ports` | **0** |
| `registry.grants` | **0** | `scheduler.trajectory` | **0** |
| `registry.isolation` | **0** | `scheduler.clock` | **0** |
| `spi.jsonrpc` | **0** | `spi.ceiling` | **0** |

`[FACT]` `layer0/registry/isolation.py` is a leftover stub — *"M1 exposes the interface; subprocess cells
arrive in M2"* — superseded by `broker.py` but still exported from `registry/__init__.py`. `CONTAINER` and
`WASM` exist as enum members raising `NotImplementedError`.

### 4.8 The old tree is mature, tested, and unprotected

`[FACT]` `vanguard/packages/` carries, tested but ungated: `SqliteEventStore` (WAL); `runtime/root.py`
(1,418 LOC composition root, 16 test files); `runtime/governance/approvals.py` (565 LOC, real Ed25519 via
`cryptography`, descriptor-bound challenge, 8 test files); `adapters/sandbox/rootless.py` (real `bwrap` with
`--unshare-all --unshare-user` and a nested-mount-ns probe); `adapters/evaluators/{daemon,isolated,signing}.py`
(real UDS + `SO_PEERCRED` + UID-10002 check, packaged as the `vanguard-evaluator` console script);
`agency/episode/engine.py` (693 LOC, the real spawn); `adapters/models/openrouter.py` (896 LOC, real SSE);
`domain/ledger/reducer.py` (478 LOC, documented purity and associativity); `runtime/ledger/{projections,recovery}.py`.

`[FACT]` 1,119 tests, 11 failing. The failures I inspected are **stale-expectation and environment
failures, not runtime breakage**: `test_repo_paths` expects `docs/03_sprints/evidence/…` while
`tools/repo_paths.py` still returns `docs/sprint6B/…`; three expect `instrument_error:model_tag_absent` but
get `provider_unreachable` because no Ollama daemon is running; five in `test.adapters.test_model_invocation`
concern a `process` vs `generic` selector inference.

`[INFERENCE]` The legacy tree is far closer to green than `CLAUDE.md`'s warning implies. Bringing it into CI
is a days-scale job, not a quarter-scale one, and that materially changes the cost/benefit of the Staff
lane's "defer CI to the code phase." U-2 in §27 measures it directly.

### 4.9 Orphans

`[FACT]` `vanguard/rust_core/` is an **empty directory** — zero files. ADR-0006 bans systems-language
components in Phase 0. It is the physical seed of the Rust question the lock is rejecting.

`[FACT]` Zero importers and zero tests: `layer0/scheduler/clock.py`, `layer0/scheduler/trajectory.py`
(the driver has its own inline `_trajectory`), `layer0/events/taxonomy.py` (used only by an unwired gate and
a `len()==40` assertion), `vanguard/packages/runtime/outcome_labels.py`,
`adapters/evaluators/suites/oracle_task_0{1,2,3}.py`, `domain/test/schema_conformance.py` (a test helper
stranded inside the production `domain` package — also a boundary smell).

`[FACT]` `workflow_visualizer.html` (49 KB) sits at the repo root. `vanguard-gui/` (19 files),
`vanguard-ide/` (22 files, with its own TS tests), `containers/` (3 Dockerfiles, never built by CI),
`vanguard/clients/{cli,client-core}` (94 TS files, **no JS/TS test runs in CI**) are all semi-live and
ungated. `lab/` is live but quarantined by `check_boundaries.py:355` (may import nothing, may be imported by
nothing). `benchmarkings/` (252 files) is measurement evidence and should stay.

---

## 5. Test & CI Findings

### 5.1 CI runs one job, it is red, and it is the wrong subject

`[FACT]` `.github/workflows/ci.yml` has a single job, `vanguard-living-gates`, with ten steps. Running each
on this tree:

| Step | Exit | Note |
|---|---|---|
| `test.test_repo_paths` | **1** | **CI's first step fails on `main`.** Stale `docs/sprint6B/` constant in `tools/repo_paths.py`. `CLAUDE.md` claims this was fixed at the v0.5.0 Foundation Lock; it was not. |
| `discover -s test/layer0` | 0 | 25 tests, 0.014 s |
| `check_boundaries.py` | 0 | 297 files |
| `check_tcb_budget.py` | 0 | 1347/1438 logical lines — `packages/kernel` only |
| `check_domain_blindness.py` | 0 | |
| `check_isolation_policy.py` | 0 | |
| `discover -s test/packs` | 0 | 27 tests |
| `check_stale_paths.py` | 0 | 229 files |
| `check_markdown_links.py` | 0 | effectively 2 files — see §5.2 |
| `scan_secrets.py` | 0 | |

`[FACT]` Not run by CI: `test/kernel` (9 files), `test/runtime` (40), `test/agency` (12), `test/adapters` (15),
`test/contracts` (8), `test/lab` (16), `test/security` (4), `test/tools` (13), `test/integration` (5),
`test/governance` (1), `test/trust` (1), `test/registry` (3), `test/benchmarks` (5), `test/apps` (1), and the
entire TypeScript CLI suite.

`[FACT]` A second workflow, `clean-candidate.yml`, does run the full suite — but only on push to
`sprint5-6/integration` or `workflow_dispatch`, and it invokes `unittest discover -s test` **without `-t .`**,
which produces loader errors. It is not a live gate.

`[FACT]` Written but not wired into CI: `tools/check_event_coverage.py` (E-COV, Invariant I-2's gate),
`tools/codegen/generate_types.py --check` (A-4/I-8's gate), `tools/run_dogfood_r9.py` (a genuinely strong
end-to-end gate: LAM proposal → `Runtime.execute_harness` → approval flow → bwrap worker → UID-10002
evaluator over signed UDS), `tools/run_broken_tests.py`, `tools/run_active_contract_tests.py`,
`tools/check_backend_artifacts.py`. `Makefile` has only cleanup targets — no test or gate target.

`[INFERENCE]` The repository already contains most of the gates it needs. The failure is not that they were
never written; it is that the ones that would fail were not connected. `--check` exists and returns 1.
E-COV exists. `run_dogfood_r9.py` exists. None runs.

### 5.2 Gate-by-gate Goodhart audit

*What is the laziest incorrect implementation that still passes?*

| Gate | Class | Laziest passing implementation |
|---|---|---|
| `replay/test_parity.py::test_cold_fold_matches_live_terminal_state` | **FALSE CONFIDENCE** | Any pure `fold`. It folds one list twice; a `fold` returning a constant would pass. And `fold.py:99` already discards `BudgetCommitted`, so budget is not in the "replayed" state at all. |
| `test_ledger_declares_forty_kinds` | **WEAK PROXY** | 40 arbitrary strings. |
| `test/layer0` dispatch suite | **FALSE CONFIDENCE for the grant path** | `support.py:68` registers the test verb as `ADVISORY`, so `requires_grant()` is false. Delete S6 and S8 entirely and the gated suite stays green. |
| `check_event_coverage.py` (E-COV) | **FALSE CONFIDENCE** | Write `EventKind.CHILD_SPAWNED` in a comment or in dead code. This is literally what `spawn()` does. Not in CI regardless. |
| `check_tcb_budget.py` | **FALSE CONFIDENCE for v0.6** | Move code into `layer0/kernel/` (unmeasured) or into `vanguard/packages/kernel/sub/` (the glob is non-recursive). Both have already happened. |
| `check_isolation_policy.py` (I-6) | **FALSE CONFIDENCE** | **Declare `isolation: container` in YAML and call `subprocess.Popen` in-process.** `packs/code-default/plugins/terminal.yaml` declares `container`; `packs/code-default/toolkits/terminal_runner.py:48` runs `subprocess.Popen` in-process with `env={**os.environ}`. The gate never reads code. Also: name the verb anything other than the literal `proc.exec`. |
| `check_domain_blindness.py` (I-7) | **WEAK PROXY** | Three hardcoded words with word boundaries. `repo`, `patch`, `lint`, `python`, `git`, `subprocess` all pass. `layer0/registry/worker.py` already special-cases `fs.read` — domain knowledge the regex cannot see. |
| `check_boundaries.py` | **STRONG STRUCTURAL** | The best gate here: AST import lattice over `packages`, `clients`, `layer0`, `lab`, `benchmarkings`; unknown-package rejection; cycle detection; subprocess-home confinement; evaluator binding site. Defeatable only by `importlib.import_module(...)`, and it cannot see a *second kernel* built inside an allowed package. |
| `check_markdown_links.py` | **WEAK PROXY** | Its default globs are `README.md`, `docs/README.md`, and `docs/agile/sprint6B/*.md` — **the last no longer exists**. It effectively checks two files. `--all` exists; CI does not pass it. It also only extracts `[](…)` links, so backticked path citations are invisible. |
| `check_stale_paths.py` | **WEAK PROXY** | Matches a hardcoded registry of obsolete prefixes, not "does this path resolve". Put the stale path in any file outside `SCAN_GLOBS`, or name your doc `0001-*.md` (legacy-ADR exemption), or put it under `docs/archive/`. |
| `scan_secrets.py` | **VALID STRUCTURAL** | Four regexes. `--all-refs` scans blob *names* only, never contents. Fine for its purpose; do not mistake it for a supply-chain gate. |
| `test/packs` | **VALID STRUCTURAL, with one hole** | Genuinely good — it shells out to the domain-blindness and isolation gates in both normal and `--expect-fail` fixture modes, so those gates are proven non-vacuous. The hole: `test_walking_skeleton.py:43` calls `toolkit.execute(...)` **directly**, bypassing `Kernel.dispatch`. **No pack test routes an effect through the kernel.** There is no proof of grant, lease, or ledger mediation for pack toolkits. |
| `run_active_contract_tests.py` | **VACUOUS** | Its contract JSON no longer exists. Mark every requirement `status: "draft"` and it prints `CONTRACT TEST PASS: 0 covered test IDs`. |
| `check_schema_archaeology.py` | **VACUOUS** | Self-retires when its traces directory is gone; prints `ARCHAEOLOGY RETIRED`, exits 0. Already vacuous. |

`[INFERENCE]` The portfolio is **structurally strong and behaviourally hollow**. `check_boundaries.py` would
catch an architectural violation instantly. Nothing in CI would catch a scheduler that signs its own
verdicts, a harness whose capability ceiling is discarded, or a toolkit that declares container isolation
and runs in-process — and nothing did.

### 5.3 The codegen finding, precisely

`[FACT]`
```
$ python3 tools/codegen/generate_types.py --check
CODEGEN FAIL: layer0/spi/types_gen.py is stale; run tools/codegen/generate_types.py   (rc=1)

$ python3 tools/codegen/generate_types.py && python3 -c "import ast; ast.parse(open('layer0/spi/types_gen.py').read())"
SyntaxError: '[' was never closed        line 196:  requests: tuple[#, ...]
```

`[FACT]` The bug is at `tools/codegen/generate_types.py:74` — a cross-file `$ref: "#"` is rendered as the
literal `#`. Beyond the syntax error, regenerating would change `EffectContext.depth` from `int = 0` to
`int | None = None`, which would then break `layer0/kernel/dispatch.py:388`'s `ctx.depth < 0` with a
`TypeError`; it would also drop `TrajectoryRef.schema`'s default and widen `Receipt.stdout_ref`.

`[FACT]` SPEC A-4: *"JSON Schema + JCS + golden vectors are the sole source of truth. Python dataclasses and
TS readers are generated. Hand-written mirrors are banned."* Invariant I-8: *"Specs are generated or
normative — never both … drift is a CI failure, not a register."*

`[INFERENCE]` A-4 and I-8 are false statements about this repository, asserted in the header of the file
that violates them, with the gate that would prove it written and disconnected. This is a **lock
precondition**, not a bug to file: either the axiom is honoured (fix the `$ref` bug, wire `--check`) or it is
repealed by ADR.

---

## 6. Documentation Authority Findings

### 6.1 SPEC's chain of authority is broken in citation

`[FACT]` `docs/SPEC.md`'s header cites, as version anchor and consumed inputs:
`docs/MASTER_REFACTOR_GUIDELINE_FINAL.md`, `docs/TECH_LEAD_REVIEW/{CRITICAL_GAP_ANALYSIS_AND_AUDIT,
NEXT_GEN_META_HARNESS_SPECIFICATION,01_SPECS_MIGRATION_MATRIX}.md`, `docs/01_specs/backend/**`, and
`docs/archive/v045/`. **None of those paths exists.** The annexes' `source:` front-matter and all 68 legacy
ADRs' `migrated_from:` fields cite the same dead paths.

`[FACT]` Mitigating: three of the cited files are physically present under
`docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/`. They were moved and no citation was updated.
`docs/archive/v045/` was genuinely deleted (`dbb6998`); `CLAUDE.md` still points readers there.

`[FACT]` `docs/03_sprints/plans/` exists as an **empty directory** while being cited six times
(`SPEC.md` §8, `milestones.md`, `backlog.md`, `sprint_active.md` ×3).

`[INFERENCE]` Both gates that should catch this are blind to it: `check_markdown_links.py` checks two files
and only `[](…)` syntax; `check_stale_paths.py` matches a prefix registry rather than checking existence.
The drift persisted precisely because the gates were Goodharted.

### 6.2 The execution board describes a project that no longer exists

`[FACT]` `docs/03_sprints/sprint_active.md` is the only file in `docs/03_sprints/`. Front-matter:
`status: ACTIVE`, `milestone: M0`, `branch: feat/substrate_upgrade`, `last_reviewed: 2026-08-18`. Its §3
"Explicitly not this sprint" forbids `layer0/` scaffolding, `schemas/mhf/`, pytest migration, and
`coding_*` re-extraction into `packs/`. **All four have shipped.** Its §2 verification block includes
`test.test_repo_paths`, which fails. Its Steps 8 and 9 are unchecked — **Step 9 is "`docs/SPEC.md`
self-review for TBD/TODO/contradictions", which was never performed**, and explains most of §6.

`[FACT]` Its own RFC-2119 exclusivity gate now fails: the grep it specifies returns 16 hits in
`docs/07_reviews/`, a directory that did not exist when the exclusion list was written.

`[FACT]` **"v0.6" means three different things simultaneously.** `docs/02_roadmap/milestones.md` says v0.6.x
= M5 + M6 (Phase-2 plugins and the distillation loop). The same file's renumbering note says old "v0.6.0
Molecular Lattice" now maps to **M3**. The entire `07_reviews/` corpus means substrate convergence. The
commit history runs W1–W5 and maps to none of them.

`[INFERENCE]` The Foundation Lock's governance artifacts went stale within one sprint of being written while
the work proceeded under a numbering scheme they do not acknowledge. **This is the failure mode a Concept
Lock must not repeat.** A lock that produces documents which no gate verifies and no board tracks will be
stale by the third wave, exactly as this one was.

### 6.3 ADR log: 84 files, an incomplete index, and live contradictions

`[FACT]` 84 files: 68 numbered `0000`–`0068` (**`0067` is absent** — a hole acknowledged only in a review
document), 13 `ADR-M0-01…13`, plus `INDEX.md`, `DEFERRED_REJECTED.md`, `DRIFT_REGISTER_v045.md`.
`INDEX.md` exists and lists `0000`–`0068` only — **all thirteen `ADR-M0-*` rows are missing**, the `0067`
hole is unmarked, and the two registers are unindexed. This violates ADR-0000's own append-only/numbered rule.

`[FACT]` Live contradictions, each evidenced:
- **Three process counts are simultaneously `accepted`**: ADR-0013 (three processes), ADR-0034 (four process
  identities), ADR-0035 (five-process split), with no supersession pointer between them.
- **ADR-0001** (TypeScript control plane) is `reversed` by **ADR-0063** (Python control plane) — cleanly. But
  `CLAUDE.md` still presents the repo as *"a stdlib-only Python core plus a TypeScript/Ink CLI/TUI client,
  managed as an npm workspace"*, and `vanguard/packages/domain/` still ships hand-written TypeScript
  (`primitives.ts`, `jcs.ts`, `resource-selector.ts`, `contracts.ts`) inside the domain package.
- **ADR-0005** (freeze at composition) vs **SPEC §2.1** (entry-point discovery) and **`milestones.md` G-M2**
  (*"hot-swap mid-run with attribution"*). The resolution — ADR-0005 wins — exists only in an unratified
  review document.
- **ADR-0010** (SQLite WAL) vs `layer0/events/store.py` (in-memory only) — §4.4.
- **ADR-0016/0017** (competence is a graph; operators are data in it) remain `accepted` while SPEC §9 refuses
  the competence graph and the migration matrix retires the word "operator".
- **ADR-0006** (no systems language in Phase 0) vs an empty `vanguard/rust_core/` and the *Full Refactor
  v3.1* proposal for a Rust core.
- **ADR-M0-03** ("exactly five SPIs") vs SPEC §2.2, which lists five plus four more "same pattern"
  protocols. `layer0/spi/interfaces.py` implements exactly five, so the code sides with the ADR and SPEC is
  the outlier.
- **SPEC §4.3** specifies a *"PTY-backed persistent shell per workspace cell"*; **ADR-0065** adopted "no live PTY".

`[FACT]` `docs/01_executive/vision.md` carries `status: LIVING` and contains a 14-tier competence continuum
and Eras/Waves cosmology — content **explicitly prohibited** by ADR-M0-10 and SPEC §9 (*"forbidden in any
document under `docs/`"*). `docs/06_references/vanguard_body_detailed.md` (`status: LIVING-TREATISE`) is the
same violation. `docs/06_references/WAVE_6_SOTA_…md` and its `_B` sibling are **byte-identical duplicates**
carrying a `status: NORMATIVE-RESEARCH` token that exists nowhere else and collides with SPEC's RFC-2119
exclusivity claim.

### 6.4 Two live schema generations with incompatible envelopes

`[FACT]` `schemas/v4/` holds 17 writer schemas + 18 generated reader profiles + ~150 golden canonicalisation
vectors. `schemas/mhf/` holds four schemas and **no vectors**.

`[FACT]` Both are live and both are loaded by code. `schemas/v4/` is genuinely validated at runtime —
`vanguard/packages/domain/test/schema_conformance.py` uses a real `jsonschema.Draft202012Validator` with a
`RefResolver` over `schemas/v4/`. `schemas/mhf/` is a **build input only** — consumed by
`tools/codegen/generate_types.py`; there is no runtime JSON-Schema validation against it anywhere. Manifest
validation is a hand-written string comparison (`layer0/registry/validator.py:61`,
`layer0/compose/compiler.py:39`).

`[FACT]` `schemas/v4/MANIFEST.md` states `SC-12`: *"no schema locks while any type in `04` lacks an
artifact … no production trajectory may be recorded against these schemas."* **Every row is `DRAFT` or
`PLANNED`; nothing is `LOCKED`** — while `layer0` records `mhf.trajectory/1` trajectories and
`layer0/events/selectors.py` cites `schemas/v4/resource-selector.schema.json` as its contract.

`[FACT]` `api: mhf.plugin/1` and `api: mhf.plugin-catalog/1` are used by nine pack manifests and have **no
schema file at all**, despite SPEC §2.1 calling `mhf.plugin/1` a JSON Schema.

`[FACT]` The two envelopes **cannot round-trip**:

| | `schemas/mhf` / `layer0` | `schemas/v4` / `packages` |
|---|---|---|
| naming | snake_case | camelCase |
| `seq` | `int` | `str` (IntString, `CT-06`) |
| chain | `prev_digest` + `digest` | none; `parent_event_id` instead |
| lineage | `causation_id`, `correlation_id`, `idempotency_key` | `parent_event_id`, `trace_id`, `span_id` |
| governance | — | `scope`, `principal_role`, `tenant_id`, `owner_id`, `confidentiality`, `retention_class`, `trainability`, `redaction_status`, `encryption_key_ref` |
| `branch_id` | `str = "main"` | `Optional[int]` — **a type conflict** |
| fwd-compat | — | `unknown_fields` (`CT-44`) |
| time | `occurred_at` | `occurred_at` + `recorded_at` |

`[FACT]` The **event taxonomies also diverge**: 40 kinds in `layer0`, 37 in `packages`, **only 21 in common**.
`layer0`-only includes the entire plugin lifecycle, `ChildSpawned/Returned`, `VerdictRecorded`.
`packages`-only includes `CanaryPromoted`, `ArtifactCreated`, `CorrectionRecorded`, `OperatorInvoked`,
`RollbackTriggered`, `ConflictDetected`.

`[INFERENCE]` I-1 ("One `EffectRequest`") and A-4 ("One schema, many languages") are false. This is the
harder of the two duplications to unwind, because `schemas/v4/vectors/` is the project's accumulated
cross-language conformance evidence (ADR-0054: *"vector agreement establishes schema equivalence"*) and the
mhf set has none. Convergence here is a **ledger migration**, and the Concept Lock must say so.

### 6.5 A status claim the evidence contradicts

`[FACT]` `docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/m0-to-m4-code-and-purge-todos.md` records
**"M1/M2: ACTIVE (M1 Complete; M2 Finalizing)"** and "M3: code extraction complete".

`[FACT]` M1's exit gate `G-M1` is: *"E-COV = 100% · `replay-parity` green · mutation score ≥ 80% on
kernel+reducers · `pytest test/layer0` green."* On this tree: E-COV is a grep and is not in CI;
replay-parity is a tautology; **no mutation testing exists anywhere in the repo**; `test/layer0` is 25 tests
in 14 ms that never touch the grant path.

`[INFERENCE]` M1 was declared complete against four gates of which one is absent, two are non-behavioural,
and one is 25 tests. This is the clearest available demonstration of why the next lock needs proof
obligations rather than exit checkboxes.

---

## 7. `vanguard/packages/` vs `layer0/` Assessment

### 7.1 Equivalence map

| Concept | `vanguard/packages/` | `layer0/` | Relationship |
|---|---|---|---|
| JCS canonicalisation | `domain/canonicalisation/jcs.py` + `digest.py` | `events/canonical.py` | **Near-identical copy** (39-line diff, no behavioural delta) |
| Resource selectors | `domain/selectors/resource_selector.py` (450) | `events/selectors.py` (450) | **Byte-equivalent** — one import line differs |
| Kernel (8 modules) | `kernel/*` (1,658) | `kernel/*` (1,258) | **Stripped copy + divergence**; 2 fixes, 3 weakenings (§4.2) |
| Event envelope | `domain/ledger/events.py` (349) | `events/envelope.py` (103) | **Incompatible** (§6.4) |
| Reducer / fold | `domain/ledger/reducer.py` (478) + `state.py` | `events/fold.py` (151) | **Divergent**; layer0's is smaller and drops `BudgetCommitted` |
| Event store | `adapters/stores/event_store.py` (SQLite WAL) | `events/store.py` (`MemoryLedger`, 28) | **Regression** |
| Blob / CAS | `adapters/stores/blob_store.py` (fan-out, no fsync, has reader) | `events/blob.py` (fsync, flat, **no reader**) | Divergent; each has what the other lacks |
| Composition | `runtime/root.py` (1,418) | `compose/compiler.py` (129) | **Divergent**; layer0 is the A-5 manifest compiler but drops capabilities (§4.3) |
| Scheduler / episode | `agency/episode/engine.py` (693, real spawn) | `scheduler/driver.py` (232, mock spawn, fabricated verdict) | **Regression** |
| SPI | *(none)* | `spi/*` (780) | **layer0 only — genuine new value** |
| Plugin registry / broker | *(none)* | `registry/*` (923) | **layer0 only — genuine new value, zero tests** |
| Model adapters | `adapters/models/*` (2,349) | *(none)* | packages only |
| Sandbox (filesystem) | `adapters/sandbox/rootless.py` (bwrap) | `registry/sandbox.py` (49, rlimits only) | packages only |
| Exterior evaluator | `adapters/evaluators/*` (~850, UID-10002 daemon) | `IEvaluationGate` protocol | packages only |
| Governance / Ed25519 | `runtime/governance/*` (786) | *(none)* | packages only |
| Recovery / projections | `runtime/ledger/*` (560) | `driver.recover()` (5 lines, constant) | packages only |

### 7.2 Direction

`[RECOMMENDATION]` **CONVERGE, ASYMMETRICALLY, WITH DELETION DATES AND A DUPLICATION GATE.** This goes
further than the Staff lane's "delete duplicated layer0 modules only after a later parity gate."

- **Canonical:** `vanguard/packages/`. Its lattice is enforced by the best gate in the repo, and it holds
  every ADR-mandated capability the new tree lacks — plus the working `spawn()` (§4.6).
- **Promote into `packages/`, in place:** `layer0/spi/` (interfaces, jsonrpc, result, types_gen),
  `layer0/registry/` (broker, worker, sandbox, validator, lifecycle), `layer0/compose/compiler.py`,
  `layer0/events/taxonomy.py`. These are the genuine deliverables of W1–W5, and four adapters already
  consume `layer0.spi` under an explicit boundary allowance.
- **Delete, do not merge:** `layer0/kernel/*` and `layer0/events/{canonical,selectors,store,blob,emitter}.py`.
  "Merge" implies a semantic reconciliation; there is none to do — they are a copy minus their rationale,
  plus a durability regression, plus three security weakenings. **Port forward only the two genuine kernel
  fixes** (`EffectFailed` split; `AuthorizationRequested`/`CapabilityAttenuated` emission) as patches to
  `packages/kernel`, each with a test.
- **Port as replacements:** `layer0/events/envelope.py` and `fold.py` are cleaner designs than
  `domain/ledger/events.py` + `reducer.py` — but only after **U-5** proves `fold.py` is semantically
  complete (today it demonstrably is not: `BudgetCommitted` is a no-op).
- **Rewrite before promotion:** `layer0/spi/ceiling.py` and `layer0/registry/grants.py` are both fail-open
  and both re-implement selector logic badly. They should delegate to `decide()` and default deny.

**Rejected alternatives.** *layer0 canonical* — would require rebuilding WAL, bwrap, Ed25519 governance, the
evaluator daemon, four model adapters, recovery, and the real spawn, all of which exist and are tested.
*A new `core/` tree* (the *Parecer v4* position) — rejected as a third identity; this repo has demonstrated
twice that it cannot keep two trees coherent. *Rebuild both* — unbounded.

**The scheduling point, and the missing gate.** `[FACT]` *Parecer v4* is the **only** document in the corpus
that proposes a duplication detector (`tools/check_duplication.py`, "no module >0.85 similarity to another"),
and the current locked plan does not include one. `[INFERENCE]` A parity gate deletes duplicates; a
duplication gate prevents the *next* fork. Both are needed, and the second is cheaper. Additionally, a parity
gate cannot be built while CI's behavioural subject **is** the tree to be deleted.

`[RECOMMENDATION]` Order: (1) switch the CI subject of record to `packages/`; (2) add the duplication gate;
(3) build the parity gate; (4) delete. The Staff lane's order stops at (4)-after-(3) and omits (1) and (2).

---

## 8. Current Architecture Conflict Matrix

| # | Conflict | Normative says | Code does | Severity |
|---|---|---|---|---|
| C-1 | Exterior judge | ADR-0004, ADR-M0-08, SPEC preamble, I-5 | `driver.py:138` emits `verdict: "pass"` unconditionally | **CRITICAL** |
| C-2 | Capability ceiling | ADR-0011/0036: capabilities carry resources | Compiler drops them; 4 fail-open steps; ceiling is `()` | **CRITICAL** |
| C-3 | Generated types | A-4, I-8 | Hand-written; generator emits invalid Python; `--check` exists and is unwired | **CRITICAL** |
| C-4 | Replay | I-4 | Test folds one list twice; `fold` drops `BudgetCommitted` | **CRITICAL** |
| C-5 | Durable ledger | ADR-0010, K-47 | `MemoryLedger`; `append_intent` is `list.append` | **HIGH** |
| C-6 | CI subject | I-2/I-4/I-5 presuppose behavioural CI | 25 tests / 14 ms; grant path never exercised; **CI red on step 1** | **HIGH** |
| C-7 | Canonical tree | SPEC §1: `layer0/` is the M1 destination | Production capability and the real spawn live in `packages/` | **HIGH** |
| C-8 | Envelope lineage | Multi-agent P0 needs `project_id`/`parent_*`/`harness_digest` | Zero occurrences in either tree; `LedgerEmitter.emit()` drops `episode_id` | **HIGH** |
| C-9 | Schemas | A-4, I-1 | Two live generations; envelopes cannot round-trip; taxonomies share 21/56 kinds | **HIGH** |
| C-10 | Isolation | I-6, ADR-M0-04 | `terminal.yaml` declares `container`; `terminal_runner.py:48` runs in-process | **HIGH** |
| C-11 | Sink class integrity | ADR-0051/M0-11 | `dispatch.py:247` records the **caller-declared** class | MEDIUM |
| C-12 | Adapter outcome | ADR-0026: an effect resolves to success or failure | `dispatch.py:258` coerces unknown returns to success | MEDIUM |
| C-13 | Provenance / taint | K-28, D-05/D-06/D-07 | `policy.py:87` defaults spans to `()`; driver never passes them → F-09 unreachable | MEDIUM |
| C-14 | Hot-swap | ADR-0005 forbids; SPEC §2 and G-M2 require | No implementation | MEDIUM |
| C-15 | Control-plane language | ADR-0063: Python | 94 TS files ungated; hand-written TS inside `domain/` | MEDIUM |
| C-16 | Roadmap | `milestones.md` M0–M6, board at M0 | History at W5; board forbids what shipped; "v0.6" has 3 meanings | MEDIUM |
| C-17 | Spec citations | SPEC is the authority root | Five cited paths do not exist; `docs/03_sprints/plans/` empty | MEDIUM |
| C-18 | TCB budget | ADR-0038 | Gate hardcoded to `packages/kernel`; `layer0/kernel` unmeasured; glob non-recursive | MEDIUM |
| C-19 | Metaphysics ban | ADR-M0-10, SPEC §9 | `vision.md` (`status: LIVING`) and `vanguard_body_detailed.md` carry tier cosmology | MEDIUM |
| C-20 | Layer-0 LOC target | A-1: ≤ 4,500 | 4,556 | LOW |
| C-21 | No systems language | ADR-0006 | Empty `vanguard/rust_core/` | LOW |

---

## 9. Concept & Primitive Review

Guiding rule: **lock a concept only if getting it wrong forces a ledger migration or a kernel rewrite.**
Everything else sits above the plugin line and must be free to move.

### 9.1 Lock now — irreversible if wrong

| Concept | Disposition | Rationale |
|---|---|---|
| **Event / EventEnvelope** | **REFINE — lock the field set** | The only thing that cannot be retrofitted without rewriting history. Adopt the richer `packages` governance fields (`tenant_id`, `retention_class`, `trainability`, `redaction_status`, `unknown_fields`) *and* the `layer0` hash chain. Add `parent_principal_id?`, `parent_episode_id?`, `harness_digest`. Fix `LedgerEmitter.emit()`. Resolve `seq` and `branch_id` type conflicts explicitly (§6.4). |
| **EffectRequest** | **KEEP AS-IS** | `verb, args, selector, sink, reservation`. One frozen type, one schema (I-1). |
| **Receipt** | **REFINE** | Add `lease_id` and `grant_digest`. Today a Receipt cannot be tied to the authority that permitted it. |
| **Principal** | **REFINE — make it a type** | Currently a bare `str` in both trees. A `Principal(id, parent_id?, depth)` is the anchor for every attenuation invariant; leaving it a string is what makes spawn unbuildable. |
| **Capability / Grant** | **KEEP AS-IS, and put it under CI** | `kernel/grants.py` is the best-designed code here: `descriptorDigest` binding refused at issuance (K-18), point-of-effect verification (S8), `parent_grant_id` with cascading revoke. It has **zero CI coverage** (§5.2). |
| **Attenuation** | **KEEP AS-IS** | Deny-whole-on-overbroad (K-26) is right, and the reason — denial is the intrusion signal — is right. One known flaw to fix, not relock: `attenuation.py:56` `_exceeds` returns `False` when either bound is `None`, so an unbounded child passes under a bounded parent. Present in **both** trees. |
| **Reservation / Budget** | **KEEP AS-IS** | Six integer dimensions (ADR-M0-07), overrun retained when negative (K-07). Correct. |
| **Lease** | **REFINE** | `parent_lease_id` and parent-closure enforcement already exist in `kernel/budget.py`. Promote to a first-class value with an owner; budget lineage across spawn hangs off it. |
| **SinkClass** | **KEEP AS-IS, fix the recording** | Three classes, all recorded (ADR-0051/M0-11). Fix C-11: record the registry-derived class, never the caller's. |
| **Evaluator / SignedVerdict** | **KEEP AS-IS conceptually, REPAIR in code** | The moat. Add the reducer-level rule in §14.3. |
| **Ledger** | **KEEP AS-IS** | `State = fold(Events)`, SQLite WAL, JSONL export only. |
| **CAS / ArtifactRef / BlobRef** | **REFINE** | Merge the two half-implementations: fan-out + reader (from `packages`) with fsync (from `layer0`), plus directory fsync. Stop reusing `CheckpointCreated` for CAS writes. |
| **FrozenHarness / HarnessManifest** | **REFINE — the ceiling must survive compilation** | `Harness = f(manifest, plugins)`, content-addressed (A-5), is right. C-2 must be closed as part of the lock, not after it. |
| **Spawn** | **REFINE — lock semantics, adopt the working implementation** | Lock `Capabilities(child) ⊆ Capabilities(parent)` and `Budget(child) ≼ remaining(parent)`. Delete the `layer0` mock; the `agency/episode/engine.py` implementation is the reference. |

### 9.2 Refine — the lock is cheap to revise

| Concept | Disposition | Rationale |
|---|---|---|
| **Episode** | **REFINE** | Well established. ADR-M0-12 ("a tool is not an Episode") holds. Needs `parent_episode_id` on the envelope. |
| **Agent** | **REFINE** | `Agent = Principal + HarnessInstance` costs nothing to lock — both halves are already locked. |
| **HarnessInstance** | **REFINE** | Currently implicit. Naming it makes the Agent definition non-circular. |
| **Trajectory** | **REFINE — lock the schema, not the pipeline** | See §16. The only Phase-2 artifact expensive to retrofit. |
| **Projection** | **KEEP AS-IS** | Implemented in `runtime/ledger/projections.py` with `rebuild_projection` from seq 0. |
| **Scheduler** | **KEEP AS-IS** | Sequential (I-11). Lock the interface, defer concurrency. |
| **Plugin / SPI** | **KEEP AS-IS** | Five SPIs (ADR-M0-03), wire-first. Note the code sides with the ADR and SPEC §2.2 is the outlier. |
| **Model / Context / Tool / Toolkit / Memory** | **KEEP AS-IS (SPI shape only)** | Lock the protocol; refuse to lock the semantics behind it. |

### 9.3 Explicitly **refuse to lock** in v0.6

This is my main structural disagreement with a 40-concept lock.

| Concept | Disposition | Rationale |
|---|---|---|
| **Project** | **UNRESOLVED — blocking** | The Staff lane's P0-5/P0-7 make `project_id` a mandatory envelope field and the consistency unit. **`Project` is defined nowhere** — not in SPEC, not in the annexes, not in any of 84 ADRs, not in either schema family, and `project_id` appears **zero times** in either tree. Locking a mandatory field with an undefined referent guarantees a placeholder forever. |
| **Task** | **DEFER** | `schemas/v4/MANIFEST.md` lists `task-and-proposal.schema.json` as `PLANNED`; no implementation. Overlaps Episode and goal-string. |
| **Skill** | **DEFER** | Two `skill_index.py` modules exist and neither is CI-exercised. Above the plugin line. |
| **Orchestrator** | **DEFER** | Defined nowhere normative; zero occurrences in SPEC, annexes, ADRs, schemas. SPEC's equivalent is the **Scheduler**. Locking a component that does not exist is how you get `root.py`. |
| **Cache** | **DEFER** | `Cache = g(Ledger, CAS)` constrains nothing; it needs no lock. |
| **Experiment / Promotion** | **DEFER (P3)** | Gated on M5's statistical-power suite, which does not exist. |
| **Meta-Harness** | **DEFER (P3)** | Four non-identical definitions across SPEC, `vision.md`, `guidelines.md`, and the proposal. SPEC §9 already refuses the release pipeline. Keep refusing. |
| **ChildPrincipal** | **MERGE into Principal** | Not a separate type — a `Principal` with `parent_id` set. Two types means two paths through `attenuation.covers()`, and K-26 is only as strong as the number of paths that reach it. |
| **MetaAgent / Swarm Participant** | **MERGE into Agent** | Same recursive abstraction; the difference is policy (§11). |

`[RECOMMENDATION]` If `Project` is locked, the minimum viable normative definition is:

> A **Project** is a durable, named scope root owning one ledger stream, one capability ceiling, and one
> root budget. Every Episode, Principal, and Artifact belongs to exactly one Project. `project_id` is the
> consistency unit: total ordering holds within a Project and not across Projects.

Small enough to be true, specific enough to be useful. If the lock cannot commit to that, use
`root_episode_id` and defer `Project`.

---

## 10. Recommended Concept Lock Model

**Four planes and one obligation rule.**

```
                     ┌──────────────────────────────────────────────┐
  STRATEGY PLANE     │  planner · memory · context · compression    │  plugins, over the wire
  (replaceable)      │  indexing · tools · skills · model routing   │  freeze at composition
                     │  reflection · evaluation GATES               │
                     └──────────────────────────────────────────────┘
                                    │ SPI — JSON-RPC 2.0, line-delimited, UDS
                     ┌──────────────────────────────────────────────┐
  DECISION PLANE     │  scheduler · kernel S0–S12 · attenuation     │  who / when / how much
  (mechanism)        │  grants · budget governor · plugin lifecycle │  canonicalisation lives here
                     │  JCS / digest / selector algebra             │  never authoritative
                     └──────────────────────────────────────────────┘
                                    │ Decision → DurableEvent
                     ┌──────────────────────────────────────────────┐
  STATE PLANE        │  ledger (SQLite WAL) · pure reducers ·       │  what happened
  (authoritative)    │  CAS · projections · snapshots               │  fold is the only truth
                     └──────────────────────────────────────────────┘
                                    │ subject (read-only) → signed verdict
                     ┌──────────────────────────────────────────────┐
  JUDGEMENT PLANE    │  exterior evaluator · signed verdicts        │  unreachable from the judged
  (exterior)         │  separate identity, separate process, UID    │  no plugin, no port, no import
                     └──────────────────────────────────────────────┘
```

Two placements differ from the Staff lane's split, both deliberate: **canonicalisation sits in the decision
plane, below the plugin line** (a plugin that could change JCS could change every digest in the system), and
**the evaluation *gate* is above the line while the *judge* is a separate plane** — C-1 is precisely what
happens when the gate inherits the judge's authority.

**The obligation rule — this lane's distinctive contribution.**

> No concept enters the v0.6 Concept Lock without (a) one sentence of normative definition, (b) the name of
> the test that fails if it is implemented wrongly, and (c) the specific wrong implementation that test
> rules out.

Applied to the P0 set:

| Locked concept | Bound falsifier | Wrong implementation it rules out |
|---|---|---|
| Envelope lineage | `test_every_emitted_envelope_carries_full_lineage` | `LedgerEmitter.emit()` dropping `episode_id`/`causation_id` — today's code |
| `State = fold(Events)` | `test_cold_reader_reconstructs_live_state_from_disk` | Folding the same in-memory list twice — today's test |
| Evaluator exteriority | `test_scheduler_cannot_produce_a_verdict_without_a_signature` | `emit(VERDICT_RECORDED, {"verdict": "pass"})` — `driver.py:138` |
| Capability ceiling | `test_declared_ceiling_survives_compilation_and_denies` | A compiler that drops `capabilities:` — `compiler.py:_parse` |
| Fail-closed authority | `test_empty_ceiling_denies_everything` | `if not capabilities: return True` — `ceiling.py:21`, `registry/grants.py:24` |
| Grant path coverage | `test_privileged_verb_requires_a_bound_grant` | An `ADVISORY`-only fixture set — `support.py:68` |
| Spawn attenuation | `test_child_grant_wider_than_parent_is_denied_whole` | Emitting `ChildSpawned`/`ChildReturned` and executing nothing |
| Generated types | `generate_types.py --check` in CI | A hand-edited file headed `DO NOT EDIT` |
| Durable intent (K-47) | `test_intent_survives_process_death` | `self.intents.append(event)` |
| Budget lineage | `test_child_budget_debits_parent_remaining` | Independent child budgets; a `fold` that discards `BudgetCommitted` |
| Isolation declaration | `test_declared_container_tier_is_not_an_in_process_popen` | `terminal.yaml: container` + `subprocess.Popen` |
| Sink integrity | `test_ledger_records_registry_derived_sink_class` | `request.sink.value` at `dispatch.py:247` |
| No duplicate implementation | `tools/check_duplication.py` | A second byte-identical selector algebra |

**Thirteen falsifiers; twelve of them fail against code that exists on `main` today.** That is the point: a
lock whose obligations are all already satisfied has locked nothing.

---

## 11. Multi-Agent & Recursive Agency Assessment

**`Agent = Principal + HarnessInstance`, `SubAgent = ChildPrincipal + HarnessInstance`** —
**AGREE WITH MODIFICATION.**

`[RECOMMENDATION]` Drop `ChildPrincipal` as a distinct type (§9.3). One type, one attenuation path, one
lineage rule.

**`Agent` / `SubAgent` / `MetaAgent` / `Swarm Participant` share one recursive abstraction** — **AGREE.**
The differences are entirely policy. A `MetaAgent` is an Agent whose planner proposes harness mutations —
a plugin, not a kind. A swarm is N Agents plus a coordination policy. ADR-0003 (agent-loop primary, no
runtime workflow graph) forbids the alternative and should stand.

**`spawn(parent, harness, capabilities, budget)`** — **AGREE WITH MODIFICATION.**

`[RECOMMENDATION]` Signature: `spawn(parent_principal, harness_digest, requested_scope, requested_reservation)
-> Principal | Denial`, returning a denial value rather than raising or silently returning. `[FACT]`
`layer0/scheduler/driver.py:179` currently `return`s on depth exhaustion after emitting `BUDGET_EXHAUSTED`;
a caller cannot distinguish "spawned" from "denied".

`[RECOMMENDATION]` The implementation is not new work. `vanguard/packages/agency/episode/engine.py:531`
already does attenuated child scope (fail-closed), depth ceiling, parent lease threading, and span merge on
return. Lock the semantics **against that implementation** and delete the mock.

**Invariants** — **AGREE, both, unconditionally.**
- `Capabilities(child) ⊆ Capabilities(parent)` — this is `kernel/attenuation.py::covers()`. Spawn should
  *call it*, not reimplement it. Fix the `None`-bound hole (§9.1) while doing so.
- `Budget(child) ≼ RemainingBudget(parent)` — component-wise on all six dimensions. The governor already
  supports parent leases; this is wiring.

**Semantics to lock now.**

| Field | Lock? | Reasoning |
|---|---|---|
| `principal_id` | **LOCK** | Must become a typed value, not a `str` |
| `parent_principal_id` | **LOCK** | Nullable; absence = root. Retrofit cost = ledger rewrite |
| `episode_id` | **LOCK** (exists) | And fix the emitter that drops it |
| `parent_episode_id` | **LOCK** | Exists in `packages` (3 occurrences), absent from `layer0` |
| `harness_digest` | **LOCK** | `D_H`. Without it no A/B attribution is possible, and attribution is the moat |
| `causation_id` / `correlation_id` | **LOCK** (declared) | Currently **never populated by any producer** — locking must include a test that they are non-null |
| budget lineage | **LOCK** — `lease_id` on Receipt | `parent_lease_id` already exists in the governor |
| capability lineage | **LOCK** — `grant_digest` on Receipt | `parent_grant_id` already exists in `grants.py` |
| evaluation identity | **LOCK** | The signing key identity must be in the envelope, or "exterior" is unverifiable after the fact |
| `project_id` | **CONDITIONAL** | Only with the §9.3 definition; otherwise `root_episode_id` |
| ownership | **DEFER** | Derivable from `principal_id` + lineage; a separate field is premature. Note `packages` already has `owner_id`/`tenant_id` — reconcile rather than invent |

**Logical agents vs execution workers** — **AGREE.** Lock the distinction in vocabulary and schema now (an
Agent is a ledger identity; a worker is a runtime resource); execute sequentially. Costs one sentence, saves
a migration.

**Heterogeneous harnesses** — **AGREE, and free.** Since spawn takes a `harness_digest`, a child on a
different harness is already expressible. Add no machinery.

**Do not lock:** swarm coordination policies, agent-to-agent messaging, delegation protocols, negotiation.
`[INFERENCE]` These are the parts of every multi-agent design that get rewritten, and none constrains the
envelope.

---

## 12. Event Sourcing / Ledger / CAS / Graph Assessment

**`State = fold(Events)`** — **AGREE, and it is currently unproven and partially false.** The gate is a
tautology (C-4) and `layer0/events/fold.py:99` discards `BudgetCommitted`, so budget — one of the four
things I-4 names — is not in the folded state at all.

**`Projection = f(Ledger)`, `Cache = g(Ledger, CAS)`** — **AGREE.** Both are already true in
`runtime/ledger/projections.py`. Neither needs a lock, because neither constrains anything.
`[RECOMMENDATION]` Lock the **negative** form, which does constrain and is falsifiable:

> No projection, index, cache, snapshot, or memory store may be the sole record of any fact.

**Relationship model.** `[RECOMMENDATION]`

```
Ledger        authoritative, append-only, hash-chained, SQLite WAL, per-project stream
CAS           immutable sha256-addressed bytes; events carry refs, never large payloads
Reducers      pure, total, versioned; fold(events) -> State, no I/O, must cover every kind
Snapshots     optimisation only; each carries the seq it summarises; CI proves reproducibility
              by discarding them and replaying from 0
Projections   read models; rebuildable; may lag; never authoritative
Indexes       projections with a query contract
Memory        an SPI over projections + CAS; never a second write path to truth
Telemetry     a projection whose schema IS the DPO harvest schema (I-9)
Graph         a projection (below)
```

**Execution graphs** — **EVENT-DERIVED PROJECTION.** The strongest position in the Staff lane's P0-4; I
endorse it unmodified. `spawned_by`, `caused_by`, `depends_on`, `produced`, `consumed`, `evaluated_by`,
`derived_from`, `invalidated_by` are all recoverable from `causation_id` + `correlation_id` + payload refs —
**provided §11's lineage fields are locked and actually populated**, which today they are not. Graph
infrastructure would create a second write path to truth.

`[RECOMMENDATION]` Lock exactly this sentence: *the execution graph is a projection; there is no graph
store, no graph database, and no workflow DAG engine. A relation that cannot be derived from the ledger is
fixed by a new envelope field or event kind, never by a graph write.* Cheap to verify (`grep` for a graph
dependency), and it closes the question permanently.

**Replay taxonomy** — **AGREE with the Staff lane's four-way split** (state replay must be deterministic;
schedule replay needs recorded nondeterminism; real-world re-execution need not match; byte-identical
fixtures only for fully controlled inputs). Genuinely good; I would adopt it verbatim.

`[RECOMMENDATION]` Add the falsifier the Staff document does not identify: the CI replay gate must be **state
replay from a cold reader against a file on disk**, diffed against live terminal state, covering grants,
budgets, approvals and episode lifecycle — I-4 as written, not as currently tested.

`[RECOMMENDATION]` Also adopt the *principal proposal* §15's explicit removal of "two concurrent executions
⇒ byte-identical ledger" as a general requirement. `[FACT]` This is a genuine conflict inside the Staff
corpus: *Parecer v4*'s P5 gate and *Full Refactor v3.1*'s §8 both **require** it; the principal proposal
§15 says it must be removed; the BETA doc sides with §15. The BETA doc is right, and the lock should record
that it is overriding two of its own supporting documents.

---

## 13. Plugin Architecture Assessment

**Plugin-first direction** — **AGREE.**

**Above the boundary (replaceable):** planner, memory, context, compression, cache strategy, indexing, AST
processing, heuristics, tools, scripts, skills, model routing, reflection, evaluation *gates*,
self-improvement strategies, Meta-Harness strategies. **AGREE with one correction:** state explicitly that
*the gate that **requests** judgement is a plugin; the judge is not*. C-1 is what the absence of that
sentence produced.

**Below the boundary (mechanism):** identity, authority, effect mediation, event semantics, resource
conservation, plugin lifecycle, core scheduling. **AGREE, add three:** *canonicalisation* (JCS is identity),
*the selector algebra* (`ceiling.py` already re-implemented a broken subset of it — §4.3), and *the ledger
write path*.

**Semantic boundary.** `[RECOMMENDATION]` Five SPIs (ADR-M0-03). Do not add a sixth in v0.6. `[FACT]`
`layer0/spi/interfaces.py` already defines exactly five, so the code already agrees with the ADR; it is
SPEC §2.2 that lists nine and should be corrected.

**Physical isolation boundary.** `[RECOMMENDATION]` **Wire-first.** Line-delimited JSON-RPC 2.0 over UDS is
the contract (ADR-0002, ADR-0059). `in_process` is an isolation *privilege* granted by policy that speaks
the same wire over loopback — not a second SPI. This is the Staff lane's P0-8 and I agree completely; it is
the decision that prevents protocol drift between the fast path and the safe path.

`[FACT]` It is already built: `layer0/spi/jsonrpc.py`, `layer0/registry/broker.py`, `worker.py`, method
allow-list, rlimits, SIGKILL containment, cell FSM. `[FACT]` **It has zero tests, and the one place its
authority check is exercised (`ceiling.py`) fails open.**

`[RECOMMENDATION]` The lock's proof obligation for the plugin boundary is a broker suite — fault injection,
timeout kill, rlimit enforcement, ceiling intersection **with a non-empty ceiling**, illegal FSM transition,
and a test that the evaluator's signing key is unreachable from any cell — before the boundary is called
locked. `[FACT]` The last of these is `AT-12`, listed as an open M2 item in
`m0-to-m4-code-and-purge-todos.md` and never closed.

**Language strategy.** **Python-first. AGREE, and it is not close.** `[FACT]` stdlib-only core with one
dependency (`cryptography`); `vanguard/rust_core/` is empty; ADR-0006 bans systems-language components in
Phase 0; the wire is language-neutral by construction, so a future Rust or Go plugin costs nothing
architecturally.

**DISAGREE with *Full Refactor v3.1*'s Rust core.** `[INFERENCE]` Its honest justification — *"O argumento
não é performance. O argumento é correção sob concorrência"* — is the strongest version of the case, and it
defeats itself: the document's own counter-argument notes the same correction is achievable in Python with
explicit locks at far lower cost, and the *execution plan* adopts exactly that (serialise append per project
with a lock; "the race becomes impossible by construction, in Python"). Introducing a third implementation
identity beside two Python trees that already cannot stay coherent, to solve a problem a lock solves, is
the highest-risk available move.

`[RECOMMENDATION]` Lock the reversal condition instead, and make it numeric — *Parecer v4* and the
*execution plan* both supply usable thresholds: *a systems language enters only when a profiling artifact in
`benchmarkings/` shows ledger-append contention exceeding a stated fraction of wall time under target load,
and it enters as a subprocess plugin over the existing wire, never as a replacement core.*

**Protobuf / gRPC / WASM / container** — **DEFER (P3) with named entry conditions.** JSON Schema 2020-12 +
JCS is normative (ADR-0008/0009/0041) and has golden vectors; Protobuf would discard that evidence. Keep
`CONTAINER` and `WASM` as enum members — that is the correct amount of anticipation — and implement neither.
`[RECOMMENDATION]` Adopt the corpus's shared formulation verbatim: **Protobuf is transport; JCS is identity.**

**Generated bindings** — **AGREE in principle, currently broken (C-3).** Fixing the `$ref` bug and wiring
`--check` is a **lock precondition**, because A-4 is one of the seven axioms the architecture rests on and
the gate already exists.

---

## 14. Authority & Security Assessment

### 14.1 Semantics to lock now

1. **Principal identity is a typed value** with a parent link and a depth. Not a `str`.
2. **Capabilities carry resources, not only verbs** (ADR-0011/0036) — **and survive compilation** (C-2).
3. **Attenuation denies whole; it never silently intersects** (ADR-0012, K-26). Apply it to `spawn` by
   calling `covers()`, not by writing a second check.
4. **Every effect passes the dispatch path; there is no second path** (ADR-0021/0037, S0–S12).
5. **Grants bind exactly one descriptor, verified at the point of effect** (K-18/CT-51, S8), refused at
   issuance. Strongest design in the repo — and untested by CI.
6. **Default deny.** No authority predicate may return `True` on an empty input. Closes `ceiling.py:21` and
   `registry/grants.py:24`, and is directly falsifiable.
7. **The recorded sink class is registry-derived, never caller-declared** (closes C-11).
8. **An effect resolves to success or failure** (ADR-0026) — an unrecognised adapter return is a failure,
   never a coerced success (closes C-12).
9. **All three sink classes are recorded; only `privileged` requires a grant** (ADR-0051/M0-11).
10. **The judge is exterior**: separate process, separate identity, signed verdicts, unreachable from agent
    *and from every plugin* (ADR-0004, ADR-M0-08). Lock, and repair (§14.3).
11. **Budget lineage is conserved**: a child never holds more than the parent's remaining in all six
    dimensions; commit debits reality including overruns (K-07); the reducer must fold `BudgetCommitted`.
12. **Plugins are untrusted by default** (I-6); in-process is a policy-granted privilege — **and the declared
    isolation tier must match the executed one** (closes C-10).
13. **Provenance labels combine downward only** (K-28), and the taint predicate must have a live default
    source (closes C-13).
14. **Revocation is an event** with point-of-effect semantics: a revoked grant fails S8, not the next request.
15. **Artifact ownership follows Principal lineage**; an artifact's provenance label is the meet of its inputs'.

### 14.2 Hardening to defer

Remote attestation, TPM/enclaves, signed plugin distribution and SBOM/in-toto; WASM tier; container tier
(M3 target, keep as enum); seccomp-bpf beyond the current rlimits (`[FACT]` `layer0/registry/sandbox.py` is
rlimits-only — no seccomp, no namespaces, no user-ns — while SPEC §3 and G-M2 both mention seccomp); key
rotation and multi-operator quorum for Ed25519 approvals; network egress policy for plugin cells;
supply-chain verification of plugin manifests.

`[RECOMMENDATION]` None of these should become v0.6 architecture. The v0.6 authority story is complete if
the fifteen semantics above hold; every item here plugs into the same seams later.

### 14.3 The two findings that are not deferrable

`[FACT]` **C-1.** `layer0/scheduler/driver.py:138` writes `VERDICT_RECORDED / verdict: "pass"` into the
authoritative ledger from inside the agent's own process, without a signature, discarding the gate's
response — and the CI-gated replay test folds it as truth. It also writes `INVALIDATION_CHECKED {"ok": True}`
and a `CLAIM_RECORDED` derived from `len(receipts)`.

`[INFERENCE]` Every measurement produced through the new tree since W1 is self-certified.

`[RECOMMENDATION]` The Concept Lock should state that **an unsigned verdict is not a verdict**, and enforce
it *at the reducer*: a `VerdictRecorded` payload without a signature verifiable over `subject_digest` is a
ledger validation failure. Enforcing at the reducer rather than at the emitter means no emission path can
bypass it — the same reasoning that makes K-18's refuse-at-issuance correct.

`[FACT]` **C-2.** The shipped pack's capability ceiling is discarded at compile time and four independent
checks fail open (§4.3). `[RECOMMENDATION]` Same treatment: default-deny is a lock semantic (14.1 item 6)
with a named falsifier, not a bug on a list.

`[INFERENCE]` C-1 is also worth reading as a signal, not only a defect: someone bypassed the evaluator
because reading a real signed verdict was harder than emitting a constant. If evaluator ergonomics are bad
enough to be routed around once, they will be routed around again. That belongs in the risk register (R-9).

---

## 15. Resource & Concurrency Assessment

**`Logical Agent ≠ Execution Worker`** — **AGREE. Lock the distinction, defer the machinery.**

**`K` active workers `≪ N` logical agents** — **AGREE as a design constraint**, `[UNKNOWN]` as a performance
claim: no workload measurement exists on this tree.

`[RECOMMENDATION]` What v0.6 semantics must carry even while execution stays sequential:

| Must be in v0.6 semantics | Why | Cost if deferred |
|---|---|---|
| Agent identity independent of execution state | An Agent must exist without a worker | Ledger migration |
| `independence_groups` on `Proposal` | Already in `types_gen.py`; declares what may run concurrently | High — planners would need retraining |
| Selector-based independence | `resource_selector.py` already computes overlap; that **is** the concurrency safety predicate | High |
| Per-project consistency unit | Total order within a project, none across | Ledger migration |
| Reservation as a hierarchy | `parent_lease` already exists | Medium |
| Idempotency keys | Already on the envelope | — |
| `MAX_CONCURRENCY` as a **configured value** = 1 | Lets the gate flip without redesign | Medium |

**Defer entirely:** worker pools, shared model runtime, copy-on-write workspaces, sparse activation, vector
clocks, hybrid logical clocks, distributed coordination, NATS, k8s. `[FACT]` ADR-0024 already asserts
concurrency safety via reads-precede-writes; ADR-0007 is superseded by I-11.

`[INFERENCE]` The most valuable concurrency preparation already exists and is unused: the selector overlap
relation. Independence is *already computable*; the scheduler simply runs one at a time. Flipping concurrency
on later is a scheduler change, not an architecture change — exactly the position a lock should aim for, and
the strongest argument for deferring.

`[RECOMMENDATION]` One thing the lock should adopt from *Parecer v4* and *v3.1* that the BETA doc omits:
**admission control on the worst simultaneous case** (`Σ R^max_i ⪯ R_available`), not the expected sum. It
is a one-line semantic that is expensive to retrofit into a governor.

---

## 16. Meta-Harness / Self-Improvement Assessment

**`H0 → Execution → Trajectory → Candidate → H1 → Experiment → Exterior Evaluation → Promotion/Rejection`**
— **AGREE as a target, DEFER as v0.6 architecture.** SPEC §9 and ADR-0019/0032 already refuse the in-place
self-modification pipeline; that refusal should stand verbatim.

| Adaptation kind | v0.6 disposition |
|---|---|
| Runtime adaptation (model routing, tier escalation) | **Already exists** (`runtime/tier_escalation.py`, `model_selection.py`, `packs/…/single_planner.py`). Plugin strategy. No lock. |
| Memory adaptation | **DEFER** — SPI shape only |
| Composition adaptation (new manifest = new `FrozenHarness`) | **ANTICIPATE, free** — A-5 already makes it expressible; a candidate harness is a manifest with a different digest |
| Plugin synthesis | **DEFER (P3)** |
| Model adaptation (DPO, distillation) | **DEFER (P3, M6)** |
| Core modification | **REFUSE PERMANENTLY** — SPEC §9, A-6 |

**The one thing I would lock now that the Staff lane leaves to P3: the Trajectory record schema.**

`[FACT]` Today's trajectory is content-free. `layer0/scheduler/driver.py:221` digests
`{schema, run_id, episode_id, principal, n}` where `n` is `len(envelopes)`. It identifies nothing about what
happened. The `packages` side does not emit one at all.

`[FACT]` SPEC §7 specifies a full `mhf.trajectory/1` with `harness_digest`, `manifest_genome`,
`model_routes_used`, per-turn `context_digest`/`proposal`/`receipts`/`cost`, `verdict.signed`, and
`attribution.prefix_hits`, emitted at every `EpisodeCompleted` with no transformation step. Invariant I-9
makes it binding. There is **no `trajectory.schema.json` in either schema directory**.

`[INFERENCE]` I-9 is the only Phase-2 requirement that is expensive to retrofit, because it constrains what
every episode must record *while it runs*. A harness-mutation engine can be built any time; a year of
episodes that did not record what the harvest needs cannot be recovered.

`[RECOMMENDATION]` Lock the trajectory schema and its emission point. Lock nothing about its consumers.
Cost: one schema. Value: Phase 2 becomes a build rather than a migration.

**Identity trinity `D_H` / `D_R` / `D_X`** — **AGREE, adopt verbatim.** Separating harness composition from
execution environment from experiment cell is correct, and `[FACT]` today's `FrozenHarness.digest` conflates
them by omission (`D_R` and `D_X` do not exist). The best original contribution in the Staff corpus.

**Do not build:** an autonomous release pipeline; in-place core mutation; an agent with write access to its
own harness definition; a promotion mechanism without a preregistered statistical gate.

`[RECOMMENDATION]` Two corrections from the *principal proposal* that the BETA doc does not carry and that I
would adopt, because both are cheap and both prevent a bad lock:
- **§72** — preregistration is required for *confirmatory* claims and promotion, not for exploration.
  Locking "no learning without preregistration" as written would forbid ordinary investigation.
- **§75** — corpus admission by **provenance**, not age: admit if the signed verdict validates, the
  trajectory digest validates, and oracle/execution identity are known; quarantine otherwise. This is
  strictly better than ADR-060-09's blanket age cutoff, and it is a schema decision, so it belongs in the lock.

---

## 17. CI & Gate Assessment

Detailed audit in §5.2. Recommendations:

| Gate | Recommendation |
|---|---|
| `check_boundaries.py` | **Keep unchanged.** Extend scan roots to `packs/`. Best artifact in the repo. |
| `scan_secrets.py`, `test/packs`, `check_domain_blindness.py` | Keep; retarget domain-blindness to the converged core. `test/packs` should route at least one effect through `Kernel.dispatch`. |
| `check_isolation_policy.py` | **Strengthen.** It reads YAML only; add the code-side assertion that a `container`-declared plugin does not `Popen` in-process. Today it is defeated by the repo's own shipped pack. |
| `check_tcb_budget.py` | Retarget to the converged kernel; make the glob recursive. Today it measures the wrong tree with a non-recursive glob. |
| `check_markdown_links.py` | Pass `--all`; resolve backticked path citations; reject directory targets. Today it checks two files. |
| `check_stale_paths.py` | Replace prefix-registry matching with does-this-path-resolve. |
| `check_event_coverage.py` (E-COV) | **Replace, do not wire in as-is.** A lexical grep is satisfied by dead code. Replace with emission coverage over an *executed, passing* scenario suite. |
| `replay/test_parity.py` | **Rewrite.** Cold reader, from disk, diffed against live terminal state, covering grants, budgets, approvals and lifecycle (I-4 as written). |
| `test/layer0/support.py` | Register at least one `PRIVILEGED` verb so S6/S8 are under CI. |
| `test.test_repo_paths` | Fix the stale `docs/sprint6B/` constant. CI is red on step 1. |
| *(missing)* codegen drift | **Add** `generate_types.py --check` — it exists and returns 1. |
| *(missing)* duplication | **Add** `check_duplication.py` (from *Parecer v4*). The only proposed gate that would have caught the fork. |
| *(missing)* production suite | **Add** `test/kernel test/runtime test/agency test/adapters test/contracts test/security test/governance`. |
| *(missing)* dogfood | **Wire** `tools/run_dogfood_r9.py`. It is genuinely strong and completely unused. |
| *(missing)* CLI suite | **Add** `npm run typecheck && npm test`, or archive the client trees. |
| *(missing)* verdict signature | **Add** at the reducer (§14.3). |
| *(missing)* mutation score | M1's own gate calls for ≥80% on kernel + reducers and **no mutation testing exists**. Highest-value behavioural gate available, and the natural enforcement mechanism for the obligation rule. |
| `run_active_contract_tests.py`, `check_baseline_manifest.py`, `check_active_mvp_contract.py`, `check_schema_archaeology.py` | Their inputs no longer exist. **Retire them explicitly** rather than leaving vacuous or failing scripts in `tools/`. |
| `clean-candidate.yml` | Fix (`-t .`) or delete. It runs the full suite on a dead branch with a broken invocation. |

`[RECOMMENDATION]` One structural change to gate selection: **every gate must name, in its own docstring,
the wrong implementation it rejects.** `check_boundaries.py` effectively does; E-COV does not. This is cheap
and makes the obligation rule self-enforcing over time.

`[RECOMMENDATION]` On the "no lexical gates" absolutism in the Staff corpus (S-13): I side with the
*principal proposal* §58's reformulation, not v3.1's blanket ban. Lexical/static gates are legitimate and
valuable for **import direction, duplication, dependency structure, and domain tokens** — `check_boundaries.py`
is proof. The correct rule is narrower and true: *no semantic, behavioural, or security property may be
considered proved by lexical evidence alone.*

---

## 18. Review of Principal Staff Engineer Proposals

### 18.1 `001_V060_concept_phase_BETA.md` — the twelve locked P0s

| P0 | Verdict | Note |
|---|---|---|
| **P0-1** Python-first, packages canonical, no Rust, no `aether-rust/` | **AGREE** | Evidence-backed; `rust_core/` empty; no hot path measured; ADR-0006 stands |
| **P0-2** layer0 is a copy-fork; converge, don't rebuild; no third tree | **AGREE WITH MODIFICATION** | Direction right, and my evidence is stronger than theirs (§4.6: the real spawn is in `packages`). But: **delete rather than merge** `layer0/kernel` + duplicated `layer0/events`; **port forward the two genuine kernel fixes**; **add a duplication gate**; and **reverse the ordering** — CI subject first, then duplication gate, then parity gate, then delete |
| **P0-3** Decision plane vs authoritative state plane | **AGREE** | Clean, correct, cheap |
| **P0-4** Recursive machine; graph is an event projection; ADR-0003 stands | **AGREE** | Strongest item in the set. Note it is currently unimplementable: `causation_id`/`correlation_id` are never populated |
| **P0-5** Spawn invariants + required envelope fields | **AGREE WITH MODIFICATION** | Adopt the invariants unchanged. `project_id` cannot be mandatory while `Project` is undefined and appears zero times in code. Spawn must *call* `attenuation.covers()`. And the mandate is **unimplementable on the current emitter** — `LedgerEmitter.emit()` drops `episode_id` and nothing populates causation/correlation |
| **P0-6** Identity trinity `D_H`/`D_R`/`D_X` | **AGREE** | Adopt verbatim. Best original contribution in the corpus |
| **P0-7** Hybrid ES, CAS, replay taxonomy, project consistency unit, SQLite WAL | **AGREE WITH MODIFICATION** | Adopt the four-way taxonomy verbatim. Add the falsifier they do not identify (the gate is a tautology) and the `BudgetCommitted` no-op. Record explicitly that this overrides *Parecer v4* P5 and *v3.1* §8, which both require byte-identical concurrent ledgers |
| **P0-8** Wire-first JSON-RPC/UDS; five SPIs; `in_process` as privilege; ADR-0005 freeze | **AGREE** | Adopt unchanged. Add the broker test suite and the AT-12 key-reachability test as the lock's proof obligation |
| **P0-9** Evaluator exterior; F1 is a defect | **AGREE, ESCALATE** | They classify F1 as a defect to fix later. I classify it as the reason the CI change cannot wait, and I would enforce it **at the reducer**, not in review |
| **P0-10** Semantics now, sequential execution | **AGREE** | Add: `MAX_CONCURRENCY` as a configured value; selector-based independence is already computable; admission control on the worst simultaneous case |
| **P0-11** CI is false confidence; production lattice is subject of record; **implementing it is the next phase** | **AGREE ON DIAGNOSIS, DISAGREE ON SEQUENCING** | §18.3. Their diagnosis understates it: CI is not merely narrow, it is **red on `main`**, and its behavioural core never touches the grant path |
| **P0-12** Defer Meta-Harness, WASM, attestation, multi-host, graph DB, third language, pytest | **AGREE, TWO EXCEPTIONS** | Lock the **trajectory schema** now (§16), and adopt **provenance-based corpus admission** (§75) rather than an age cutoff |

**Not in their P0 list, and I would add:** the duplication gate (§7.2); an ADR resolving A-4/I-8 (C-3);
default-deny as a locked semantic (C-2); and the schemas-v4-vs-mhf relationship (C-9), which is a ledger
migration decision that cannot be discovered later without cost.

### 18.2 The other documents

**`principal_engineer_proposal.md`** — the conceptual north star. **AGREE** on the recursive substrate, plane
separation, plugin-first framing, identity trinity, `Y = F(...)` compositional framing, and the falsifiable
hypotheses (H1 `ΔCore(NewDomain)=0`, H3 `fold(L)=S`). Its §58 (lexical gates reformulated), §72
(preregistration scoped to confirmatory claims), §75 (provenance-based admission), and §59 (mutation score
must not become the definition of quality) are all **improvements on the stricter documents** and I adopt
them. `[FACT]` Its self-contradiction on the canonical tree (§2) means it cannot be cited as authority for
either answer. `[INFERENCE]` Its other risk is volume: 4,460 lines against a 9k-word SPEC will not survive
contact with a sprint board unless compressed to decisions with falsifiers — which the BETA doc largely does.

**`Vanguard-substrate-060-full-refactor-v3-1.md`** — Rust core beside both Python trees. **DISAGREE** (§13).
But it should not be discarded: its findings F1–F10 are accurate and independently reproduced here, its §8
wrong-vs-right gate table is the best gate-design artifact in the corpus, its §1 epistemic note (write the
false positive first) is the right discipline, and its §4 theory section (CALM, attenuation as a monotone
semilattice vs budget reservation as non-monotone, FWER compounding, DPO pairing validity requiring
`harness_digest_w = harness_digest_l`) is genuinely load-bearing and should be preserved as an annex input.

**`vanguard-substrate-060-execution-plan.md`** — treats `layer0/` as the v0.6 production target. **DISAGREE**,
and my evidence is stronger than the BETA doc's: `layer0/` violates an accepted ADR on durability (C-5),
fabricates verdicts (C-1), discards the capability ceiling (C-2), ships a hand-written "generated" file
(C-3), and replaced a working `spawn()` with two event emissions (§4.6). It is not a production target; it
is a prototype CI mistook for one. **But its invariant set S-1…S-14 and its planning hierarchy (Subtask →
Task → Sprint → Wave → Milestone with DoR/DoD) are better instruments than SPEC's I-1…I-11**, particularly
S-2 (*"emitted = declared **and semantically real**; constant emission is a defect"*) and S-5 (*"the judge's
answer **is read and determines the result**"*) — both of which are exactly the falsifiers C-1 and E-COV
need. I would adopt S-2 and S-5 into the lock's invariant set. Its numeric Rust decision gate is also the
right shape.

**`vanguard-arquitetura-v4-parecer-e-plano.md`** — new top-level `core/` tree; evaluator as a product plugin.
**DISAGREE on both.** Evaluator-as-plugin is the more dangerous: it is precisely the move that produced C-1.
**But this is the most empirically valuable document in the corpus** and the lock under-uses it. It is the
only one that: measured the fork quantitatively (selector diff = 2 lines); identified `root.py` (1,418 LOC)
as the real modularity bottleneck; proposed the duplication gate; identified the missing orchestrator as
legitimate new construction; and produced the latency profile (model call 90–99% of wall time; JSON-RPC over
UDS 0.1–1 ms, "irrelevant") that **settles the Rust question with data rather than preference**. Its
`root.py` finding is notable because the current lock explicitly forbids touching `root.py` this phase — so
the identified root cause of "swapping the context plugin is still an edit in the composition root" remains
unaddressed by the lock that cites this document.

**`aether-v1-roadmap-waves.md`** — **DEFER.** Out of scope for a Concept Lock, and the tree already has two
unreconciled roadmaps and three meanings of "v0.6" (§6.2). Its first-increment instruction ("begin with Wave
1: freeze `EventEnvelope v2`, `PluginManifest v2`, `HarnessManifest v2`, `ProjectManifest v1`") is the exact
thing that v3.1 §3.4, the execution plan (K-2), and the principal proposal §56 all say must **not** be done
first — freezing contracts derived from synthetic behaviour encapsulates the fiction. Given C-1 and C-2, that
warning is now empirically confirmed on this tree.

### 18.3 The one sequencing disagreement, stated precisely

The BETA doc's P0-11 says: *"That is a false-confidence gate, not a v0.6 architecture. … **Implementing** the
CI change is the first code-phase task, not this phase."*

`[INFERENCE]` This is the one place the Staff lane's otherwise admirable scope control works against it. The
argument for deferring is clean: a Concept Lock produces documents, and CI is code. The argument against is
that **the lock's evidence base is the CI system**, and that system currently certifies as green: a
self-signing judge, an unenforced capability ceiling, a tautological replay proof, a hand-written "generated"
file, a mock spawn, a container-declared toolkit running in-process — and it is **failing on its own first
step**.

Locking twelve decisions under gates in that state means the claim "the production lattice is canonical" is
ratified by a CI run that never executes the production lattice.

`[RECOMMENDATION]` A narrow carve-out, not a scope explosion. The lock phase may make **exactly four**
mechanical changes, all evidence-restoring rather than architecture-setting:

1. Add the existing production test discovery to `ci.yml`, allowed `continue-on-error` for one release so
   the baseline is *visible* without becoming a merge gate.
2. Fix the stale `docs/sprint6B/` constant in `tools/repo_paths.py` so CI's first step passes on `main`.
3. Add `generate_types.py --check` as a non-blocking reporting step — the gate already exists and returns 1.
4. Add `run_dogfood_r9.py` as a non-blocking reporting step — the gate already exists and is unwired.

None of these decides an architecture question; all four make the lock's claims checkable; three of them are
one line of YAML each. If even this is out of scope, the lock should state in writing that its P0s were
ratified under gates known to be non-behavioural — an honest and acceptable alternative, but it should be
said out loud rather than left implicit.

---

## 19. What I Would Keep

1. **The separability thesis.** *What solved it must be separable, and the judge must be unreachable from the
   judged.* The project's identity and its only real moat.
2. **The S0–S12 dispatch sequence, exactly as ordered.** Every ordering rule (K-04, K-05, K-06, K-07, K-08,
   K-47) encodes a defect that actually shipped. Do not reorder, do not "simplify."
3. **`check_boundaries.py`** and the hexagonal lattice it enforces.
4. **Grant/descriptor binding (K-18)**, refused at issuance rather than at use, with `parent_grant_id`
   cascading revoke.
5. **Attenuation denies whole (K-26)**, including the reasoning: a child repeatedly over-asking is the
   strongest intrusion signal this system shape produces.
6. **Six-dimension integer `Reservation`** with `parent_lease_id`. No floats in the governor.
7. **JCS + `schemas/v4/vectors/`** as identity and as accumulated cross-language evidence.
8. **SQLite WAL ledger, JSONL as export only** (ADR-0010), and `runtime/service/inbox.py`'s WAL outbox.
9. **`Harness = f(manifest, plugins)`, content-addressed** (A-5).
10. **Five SPIs, wire-first, freeze at composition** (ADR-M0-03, ADR-0005).
11. **The exterior evaluator as built** — UID-10002 daemon, `SO_PEERCRED`, signed verdicts. `[FACT]` The
    as-built is *stronger* than the spec here (D-32/ADR-M0-08); keep the as-built.
12. **`agency/episode/engine.py`'s `spawn()`** — the working recursive-agency implementation.
13. **`adapters/sandbox/rootless.py`** — real bwrap with `--unshare-all --unshare-user` and a nested-mount-ns probe.
14. **SPEC §9's refusals** and the honour table. One of the healthiest things in this repository.
15. **`layer0/spi/` and `layer0/registry/`** — the real deliverable of W1–W5.
16. **The two genuine kernel fixes** in the fork: the `EffectFailed` split and the
    `AuthorizationRequested`/`CapabilityAttenuated` emissions.
17. **The append-only ADR log with mandatory reversal conditions** (ADR-0000), and **`benchmarkings/`** as
    measurement evidence.

## 20. What I Would Change

1. **CI's subject of record** → the production lattice, plus codegen drift, duplication, dogfood, and
   verdict-signature checks (§17, §18.3).
2. **`LedgerEmitter.emit()`** → carry the full lineage set on the kernel path; populate causation/correlation.
3. **`layer0/compose/compiler.py::_parse`** → read `capabilities`, `system_prompt`, `approval_policy`; stop
   discarding `intersect_ceilings`.
4. **`ceiling.py` and `registry/grants.py`** → default deny on empty; delegate to `decide()` instead of
   re-implementing selectors; stop using `repr()` as selector identity.
5. **`driver.py:138`** → read a signed verdict or emit nothing; enforce at the reducer.
6. **The replay-parity test** → cold reader from disk, diffed against live state (I-4).
7. **`fold.py`** → actually fold `BudgetCommitted`.
8. **`dispatch.py:247/258` and `policy.py:87`** → registry-derived sink class; unknown adapter return is a
   failure; restore the taint predicate's default span source.
9. **E-COV** → behavioural emission coverage over passing tests, not a lexical grep.
10. **`tools/codegen/generate_types.py`** → fix the `$ref: "#"` bug and wire `--check`, or repeal A-4 by ADR.
11. **`Principal`** → from `str` to a typed value with `parent_id` and `depth`.
12. **`Receipt`** → add `lease_id` and `grant_digest`.
13. **`TrajectoryRef`** → a real record per SPEC §7, with a schema.
14. **`check_tcb_budget.py`** → retarget, recursive glob. **`check_markdown_links.py`** → `--all`, backticks.
    **`check_stale_paths.py`** → existence, not prefixes. **`check_isolation_policy.py`** → assert code, not YAML.
15. **`docs/SPEC.md`** → §1 (packages canonical), §2 (strike hot-swap, five SPIs not nine), §4.3 (strike PTY,
    ADR-0065), §8 (invert migration direction); repair five dangling citations; complete Step 9's
    contradiction pass.
16. **`docs/05_adr/INDEX.md`** → add the thirteen `ADR-M0-*` rows, mark the `0067` hole, index the two registers.
17. **`docs/03_sprints/sprint_active.md`** → mark superseded; it forbids work that shipped and its own
    RFC-2119 gate now fails.
18. **`CLAUDE.md`** → version pointer; drop the `docs/archive/v045/` reference to a deleted directory;
    reconcile the TypeScript framing with ADR-0063; correct the claim that the `repo_paths` bug was fixed.
19. **Blob/CAS** → merge the two half-implementations; fsync the directory; stop reusing `CheckpointCreated`.

## 21. What I Would Remove or Avoid

1. **`layer0/kernel/*` and the duplicated `layer0/events/*`** — delete after CI retarget; port forward only
   the two genuine fixes and (pending U-5) `envelope.py`/`fold.py`.
2. **`layer0/scheduler/driver.py::spawn()`** — delete. A mock that satisfies a gate is worse than an
   unimplemented feature, because it makes the gate lie.
3. **The unconditional `verdict: "pass"` / `INVALIDATION_CHECKED ok: True` / `CLAIM_RECORDED` emissions** —
   delete. Emit nothing rather than emit fiction.
4. **`vanguard/rust_core/`** (empty), **`layer0/registry/isolation.py`** (superseded stub),
   **`layer0/scheduler/{clock,trajectory}.py`** (orphans), **`runtime/outcome_labels.py`**,
   **`adapters/evaluators/suites/oracle_task_0{1,2,3}.py`**, **`domain/test/schema_conformance.py`**
   (a test helper inside the production domain package), **`workflow_visualizer.html`**.
5. **`docs/06_references/WAVE_6_…_B.md`** — a byte-identical duplicate of its sibling.
6. **A Rust core; a third top-level tree; a graph database or workflow-DAG engine; hot-swap in v0.6;
   a third roadmap; `ChildPrincipal` as a distinct type; any new gate that greps for a name.**
7. **The metaphysics still in `docs/01_executive/vision.md` and `docs/06_references/vanguard_body_detailed.md`** —
   both carry `LIVING` status and both violate ADR-M0-10 and SPEC §9. Either the ADR is enforced or it is repealed.
8. **Vacuous `tools/` scripts** whose inputs no longer exist — retire them explicitly.

## 22. What I Would Explicitly Defer

Each deferral stated as a decision with a named reversal condition:

| Deferred | Reversal condition |
|---|---|
| Concurrent execution | A measurement showing sequential execution binds the lab's throughput |
| Worker pools, CoW workspaces, sparse activation | Concurrency is enabled |
| WASM / container isolation tiers | A plugin exists that cannot be safely run under subprocess + rlimits |
| seccomp-bpf beyond rlimits | A threat model naming a syscall-level escape |
| Protobuf / gRPC | Wire profiling showing JSON-RPC framing is a bottleneck (currently 0.1–1 ms vs a 10–100× larger model call) |
| Rust or any systems language | A profiling artifact in `benchmarkings/` showing ledger-append contention over a stated fraction of wall time |
| Meta-Harness promotion, plugin synthesis, distillation | The statistical-power suite exists, sized by power analysis rather than a round number |
| `Project`, `Task`, `Skill`, `Orchestrator`, `Experiment` as locked concepts | A second domain pack exists that needs them |
| Multi-host / distributed | Never in v0.6; requires a new ADR |
| pytest migration | Never blocks architecture |
| Competence graph | Permanently refused (ADR-M0-10, SPEC §9) — and ADR-0016/0017 should be annotated accordingly |
| GUI / IDE clients | SPEC §9 says parity is not a backend requirement; decide archive-or-gate (P1-16) |

---

## 23. P0 Decisions — Lock Before Development

| # | Decision | Evidence |
|---|---|---|
| **P0-A** | **Envelope lineage is normative and mandatory:** `project_id?`, `principal_id`, `parent_principal_id?`, `episode_id`, `parent_episode_id?`, `harness_digest`, `causation_id`, `correlation_id`, `idempotency_key`, `prev_digest`, `seq`, plus the `packages` governance fields. `LedgerEmitter.emit()` carries all of them. | §4.5 — the only irreversible retrofit |
| **P0-B** | **`vanguard/packages/` is canonical.** `layer0/` is a fork under directed absorption. No third tree. No Rust core. | §7, §4.6 |
| **P0-C** | **Absorption is directional and dated:** promote `layer0/{spi,registry,compose,events/taxonomy}`; **delete** `layer0/kernel` and duplicated `layer0/events`; **port forward** the two genuine kernel fixes; **port `envelope.py`/`fold.py` as replacements pending U-5**; **rewrite `ceiling.py`/`registry/grants.py` fail-closed before promotion**; **add a duplication gate**. | §7.2 |
| **P0-D** | **Four planes**, with canonicalisation and the selector algebra *below* the plugin line, and the judge in its own plane. | §10 |
| **P0-E** | **`Agent = Principal + HarnessInstance`;** a sub-agent is a Principal with `parent_id`. One recursive abstraction. Swarm is policy. | §11 |
| **P0-F** | **Spawn invariants:** `Capabilities(child) ⊆ Capabilities(parent)` via `attenuation.covers()`; `Budget(child) ≼ remaining(parent)` on six dimensions. Denial returns a value and emits an event. Reference implementation is `agency/episode/engine.py`. | §11, §4.6 |
| **P0-G** | **Identity trinity `D_H`/`D_R`/`D_X`.** `FrozenHarness.digest` is `D_H` only. | §16 |
| **P0-H** | **Execution graph is a projection.** No graph store, no DAG engine. Missing relations are fixed by envelope fields. | §12 |
| **P0-I** | **Plugin boundary is the wire.** Line-delimited JSON-RPC 2.0 over UDS. Five SPIs. `in_process` is a privilege over the same wire. Freeze at composition. Protobuf is transport; JCS is identity. | §13 |
| **P0-J** | **Authority is fail-closed and exterior.** No authority predicate returns `True` on empty input. The declared capability ceiling survives compilation. An unsigned `VerdictRecorded` is a ledger validation failure, enforced at the reducer. The recorded sink class is registry-derived. | §14 |
| **P0-K** | **Durability:** SQLite WAL is the ledger; `append_intent` is durable before S9 or the effect is `UNDETERMINABLE`. In-memory ledgers are test doubles only. | §4.4 |
| **P0-L** | **Trajectory record schema** is locked; its consumers are not. Corpus admission is by provenance, not age. | §16 |
| **P0-M** | **The obligation rule:** no concept is locked without a named falsifier and the wrong implementation it rejects. | §10 |
| **P0-N** | **CI subject of record is the production lattice.** Non-blocking is acceptable for one release; absent is not. | §18.3 |

## 24. P1 Decisions — Lock or Deliberately Defer

| # | Decision | My call |
|---|---|---|
| P1-1 | `project_id` mandatory in the envelope | **LOCK NOW** — with the §9.3 definition, else `root_episode_id` |
| P1-2 | `Principal` as a typed value | **LOCK NOW** — P0-F is unimplementable otherwise |
| P1-3 | `Receipt` carries `lease_id` + `grant_digest` | **LOCK NOW** |
| P1-4 | A-4/I-8 honoured or repealed | **LOCK NOW** — currently a false statement (C-3) |
| P1-5 | `schemas/mhf` vs `schemas/v4` relationship, envelope and taxonomy reconciliation | **LOCK NOW** — it is a ledger migration (C-9); discovering it later costs a compatibility layer |
| P1-6 | SPEC §2 hot-swap struck; ADR-0005 stands | **LOCK NOW** |
| P1-7 | `MAX_CONCURRENCY` a configured value = 1; admission control on worst simultaneous case | **LOCK NOW** — free, makes P1-8 cheap |
| P1-8 | Concurrent execution | **DEFER DELIBERATELY** |
| P1-9 | Revocation semantics (fails at point of effect) | **LOCK NOW** — one sentence |
| P1-10 | Provenance meet over artifact inputs; taint predicate default span source | **LOCK NOW** |
| P1-11 | Control-plane language; the TypeScript client trees' status | **LOCK NOW** — Python control plane (ADR-0063); clients enter CI or are archived; hand-written TS leaves `domain/` |
| P1-12 | Roadmap reconciliation M0–M6 ↔ W1–W5; one meaning of "v0.6" | **LOCK NOW** — a naming decision, not a plan (C-16) |
| P1-13 | Mutation-score gate on kernel + reducers | **DEFER DELIBERATELY** to the first code wave, but name it in the lock as P0-M's enforcement mechanism |
| P1-14 | Cross-language plugin conformance suite (the "framework" proof) | **DEFER DELIBERATELY** — but record that until a non-Python plugin passes the same suite, "harness framework" is a claim, not a product |
| P1-15 | pytest migration | **DEFER DELIBERATELY** |
| P1-16 | `vanguard-gui` / `vanguard-ide` / `containers/` disposition | **LOCK NOW** — archive or gate |
| P1-17 | ADR-0013 vs 0034 vs 0035 (three/four/five processes) | **LOCK NOW** — a one-line supersession; three accepted contradictory ADRs is an authority failure |
| P1-18 | ADR-M0-10 enforcement against `vision.md` and `vanguard_body_detailed.md` | **LOCK NOW** — enforce or repeal |

## 25. P2 Decisions — Safe to Defer

Directory layout inside `packages/`; whether `root.py` is split (it should be — *Parecer v4* is right that it
is the practical modularity bottleneck — but it is refactoring, not architecture); logging format;
`simple_yaml.py` vs a YAML dependency; CLI/TUI ergonomics; error-message wording; test-naming conventions;
reorganising `benchmarkings/`; container base images; exact rlimit values; JSON-RPC batch support; snapshot
cadence; index implementation; blob GC policy.

## 26. P3 / Research

Meta-Harness promotion and genome mutation; plugin synthesis; DPO harvest and distillation; calibrated
escalation; skill harvest; WASM isolation; remote attestation; multi-host distribution; a competence graph
(permanently refused); a third control-plane language; market-based budget allocation; agent-to-agent
negotiation protocols; neuro-symbolic memory graphs.

## 27. Unknowns / Required Experiments

| # | Unknown | Experiment |
|---|---|---|
| U-1 | Is `K ≪ N` the right scale model? | No workload measurement exists. Instrument a 20-episode dogfood run for worker occupancy |
| U-2 | Is the `packages` suite green once the stale constant and the Ollama-dependent tests are handled? | Fix `repo_paths`, mark environment-dependent tests, re-run. **Days-scale, and it decides §18.3's cost.** Highest-value spike in this list |
| U-3 | Subprocess-per-plugin cost at coding-pack turn rates? | Benchmark `broker.call()` round-trip vs in-process. *Parecer v4* estimates 0.1–1 ms against a 10⁰–10¹ s model call; confirm on this tree |
| U-4 | Are the `mhf` and `v4` envelopes reconcilable, or is convergence a migration? | Diff the two schemas and the two taxonomies field by field. Decides P1-5's cost |
| U-5 | Is `layer0/events/fold.py` (151) semantically complete vs `domain/ledger/reducer.py` (478)? | Property test: fold both over the same stream, diff terminal state. **Known incomplete already** (`BudgetCommitted`). Decides port-vs-rewrite in P0-C |
| U-6 | Does the bwrap sandbox still work on current kernels / WSL2? | Run `test/security` and `test/adapters` with `bwrap` present |
| U-7 | Which of the 384 `dispatch.py` diff lines are intentional? | Line-by-line adjudication before deletion. Three weakenings and two fixes identified here; assume more |
| U-8 | Is the planned corpus size adequate for M5? | Power analysis against observed effect size in `benchmarkings/`; the corpus notes a `_retracted/` set |
| U-9 | Are the three review lanes actually isolated? | The working tree showed cross-lane modifications during this session (§3) |

---

## 28. Recommended Architecture & Concept Lock Sequence

**Step 0 — Restore the evidence base (days).** The four carve-outs in §18.3. Three of them are one line of
YAML each; the fourth is a stale string constant. Purpose: the lock's own claims become checkable. If the
lock phase refuses, it must record in writing that its P0s were ratified under non-behavioural gates.

**Step 1 — Forensic register.** Facts only, every claim `file:line` or command output. The Staff lane's
Phase A/B structure is right; adopt it. It must include the conflict matrix (§8) and the gate Goodhart audit
(§5.2) — those two tables justify everything downstream.

**Step 2 — Lock the fourteen P0s (§23), each with its falsifier (§10).** No concept without an obligation.
This is the deliverable.

**Step 3 — Mark every P1 `LOCK NOW` or `DEFER DELIBERATELY` (§24)**, each deferral with a reversal condition.
An unmarked P1 is the failure mode that produced C-14 and C-16.

**Step 4 — ADRs and SPEC v0.6.** Approximately the Staff lane's 0069–0073 cluster, plus four this lane adds:
- **A-4/I-8 disposition** — honour or repeal (P1-4).
- **Proof obligations** — every locked concept names its falsifier (P0-M).
- **Schema reconciliation** — `mhf` vs `v4`, envelope and taxonomy, and the migration this implies (P1-5).
- **Fail-closed authority** — no predicate returns `True` on empty input (P0-J).

Plus one-line supersessions for ADR-0013/0034/0035 and an annotation on ADR-0016/0017.

SPEC edits per §20 item 15, plus completing the never-performed Step 9 contradiction pass.

**Step 5 — Hygiene that is part of the lock.** `CLAUDE.md`; `sprint_active.md` superseded note; delete
`vanguard/rust_core/` and the orphan list (§21 item 4); reconcile M/W numbering (P1-12); resolve the
metaphysics documents (P1-18). Explicitly **not** a new roadmap.

**Exit gate.** Every P0 has an ADR citation in SPEC **and a named falsifier**; every P1 is marked; SPEC has
no TBD and no longer names `layer0/` as the M1 destination; `INDEX.md` is complete; the conflict log lists
every rejected supporting-doc item *including the two this lane adds — byte-identical concurrent ledgers,
and contract-freeze-before-vertical-slice*; the working tree contains no architecture implementation; no
commit without explicit request.

**Next phase (not the lock):** as-built gap and migration classification, then one operational plan, then
code — starting with CI made blocking, the C-1 verdict repair, the C-2 ceiling repair, and the P0-A envelope
fields. Not a Rust rewrite. Not a third runtime. Not a contract freeze before a real vertical slice runs.

---

## 29. Suggested Documentation Changes — DO NOT APPLY

Recommendations only; nothing below was performed. Consolidated in §20 items 15–18 and §21 items 4–8.
Additionally:

**`docs/04_annex/KERNEL.md`** — amend only where a v0.6 sentence would contradict it; do not rewrite S0–S12.
Add the K-47 note that an in-memory intent list does not satisfy durable intent, and the `_exceeds` `None`-bound
hole (§9.1).

**`docs/04_annex/MEASUREMENT.md`** — add the trajectory schema (§16), the `D_H`/`D_R`/`D_X` separation,
provenance-based corpus admission (§75), and the preregistration scoping correction (§72).

**`docs/06_references/`** — this directory currently contains a `status: NORMATIVE-RESEARCH` token that
collides with SPEC's RFC-2119 exclusivity claim, three files with no status header at all, and one
byte-identical duplicate. Give it a README declaring the whole directory non-normative, or give every file a
status.

**`docs/07_reviews/`** — has no README, no status, and is absent from SPEC's authority chain, yet it contains
the only documents describing the project's actual direction, and six of the terms the v0.6 architecture
depends on (`Project`, `spawn` as an API, `ChildPrincipal`, `Orchestrator`, `Projection`, `Experiment`) are
**defined only here**. The lock must promote those definitions into SPEC or drop the terms.

**Archive:** keep `CRITICAL_GAP_ANALYSIS_AND_AUDIT.md`, `NEXT_GEN_META_HARNESS_SPECIFICATION.md`, and
`01_SPECS_MIGRATION_MATRIX.md` where they are; repair SPEC's citations to point here rather than moving the
files again.

## 30. Suggested Roadmap Implications — DO NOT APPLY

1. The lock creates a **convergence wave** that exists in neither M0–M6 nor W1–W5. It is the largest single
   work item implied and must be sized, not assumed.
2. **CI retarget precedes convergence.** A plan that deletes `layer0/` before `packages/` is gated deletes
   the only tested tree.
3. **C-1 and C-2 are stop-ship for measurement.** Every benchmark produced through `layer0/scheduler/driver.py`
   since W1 is self-certified, and every effect it authorised ran without a ceiling. Results in
   `benchmarkings/` from that path should be re-labelled before being cited. `[FACT]` The corpus already has
   a `_retracted/` convention with a `RETRACTION.md` — the mechanism exists.
4. **P0-A is a ledger migration.** Every existing ledger gets a migration or is declared v0.5-format and
   read-only. Doing it at the lock costs one schema; doing it in v0.7 costs a migration tool.
5. **P1-5 may be a second migration.** The two envelopes have a type conflict (`seq`, `branch_id`) and the
   taxonomies share 21 of 56 kinds. Size it before committing.
6. **The statistical-power suite is the longest-lead item in the programme** and nothing is building it. It
   should start in parallel with the convergence wave.
7. **The trajectory schema (P0-L) must land before convergence completes**, or the episodes run during
   convergence are not harvestable.
8. **`root.py` (1,418 LOC) is the practical modularity bottleneck** and is out of scope for the lock. That is
   defensible, but the roadmap must own it: until it is split, "swap the context plugin" remains an edit in
   the composition root, which is the thing the plugin architecture exists to prevent.
9. **Reconciling M0–M6 with W1–W5 is a prerequisite** to any third numbering scheme.

---

## 31. Risks and Trade-offs

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R-1 | **The lock ratifies under gates known to be hollow.** Fourteen P0s decided while CI is red on step 1 and certifies a self-signing judge and an unenforced ceiling as green. | **High** — the default path | §18.3's four carve-outs, or an explicit written caveat |
| R-2 | **Convergence stalls and both trees persist another two waves.** Already happened once; `dispatch.py` has diverged 384 lines *in both directions*. | **High** | P0-C's explicit direction + deletion dates + the duplication gate; CI retarget first |
| R-3 | **Locked concepts become slogans.** I-1…I-11 are excellent and at least six are currently false (I-1 two schema families; I-2 grep; I-4 tautology; I-5 fabricated verdict; I-6 declared-vs-executed isolation; I-8 hand-written generated file). And M1 was declared complete against them. | **High** — precedent is documented (§6.5) | P0-M. This is the mitigation for R-3 specifically |
| R-4 | **Over-locking.** Locking 40 concepts including `Project`, `Task`, `Skill`, `Experiment`, `Meta-Harness` on zero implementation evidence produces the migration debt the lock exists to prevent | Medium | §9.3's explicit refusals, stated as decisions |
| R-5 | **Under-locking the envelope.** Deferring lineage means a ledger migration later, or losing history | Medium | P0-A is the highest-value single decision here |
| R-6 | **Three lanes, one lock.** Three independently reasoned proposals need a synthesis owner and a tie-break rule, or the lock becomes a union of three plans. Compounded by the cross-lane working-tree activity in §3 | **High** | Name the synthesis owner and the conflict rule *before* the reports are compared; give each lane a clean tree |
| R-7 | **Deleting `layer0/kernel` loses an intentional improvement.** Two genuine fixes and three weakenings identified; assume more | Medium | U-7's line-by-line adjudication, U-5's property test |
| R-8 | **CI retarget costs weeks, not days** | Low–Medium | U-2 measures it directly and cheaply |
| R-9 | **The evaluator is slow or awkward enough that people route around it** — which is arguably what C-1 is | Medium | Treat C-1 as a signal about evaluator ergonomics, not only as a defect |
| R-10 | **Documentation staleness recurs.** `sprint_active.md` went stale within one sprint; SPEC's Step 9 was never done | **High** | Only gated documents stay true; §17's link/stale/glossary gates |
| R-11 | **Contract freeze before a real vertical slice.** Three of the five Staff documents warn against it; the fifth's first increment does exactly that. Given C-1 and C-2, freezing now would encode the fiction | Medium | Sequence the lock after Step 0, and require one real end-to-end path with a read signed verdict before any schema is called LOCKED |

**The central trade-off.** Adding proof obligations to every locked concept makes the lock slower and
narrower. That is the cost. The benefit is that the resulting lock is *falsifiable* — a later engineer can
run one command and learn whether a locked concept is still true. The Foundation Lock did not have that
property, six of its eleven invariants are currently false, CI is green, and a milestone was declared
complete against them. I would take the narrower lock.

---

## 32. Final Independent Tech Lead Recommendation

**Adopt the Principal Staff Engineer lane's architecture. Reject its sequencing. Narrow its scope. Add its
missing detector.**

On architecture we substantially agree, and I would not spend the programme's time re-litigating it:
Python-first; one production lattice at `vanguard/packages/`; `layer0/` absorbed, not enthroned; no Rust,
no third tree, no graph database, no workflow-DAG engine; decision plane versus authoritative state plane;
`Agent = Principal + HarnessInstance` with subset invariants on capability and budget; graph as projection;
identity trinity `D_H`/`D_R`/`D_X`; wire-first JSON-RPC/UDS with five frozen SPIs; exterior signed judge;
SQLite WAL; sequential execution with concurrent semantics; Meta-Harness deferred.

Four modifications, in descending order of importance:

**First — the lock must carry proof obligations.** No concept is locked without a named test and the wrong
implementation that test rejects. The evidence is on this tree: the previous lock produced eleven invariants
of which at least six are false today, and a milestone was declared complete against four gates of which one
does not exist, two are non-behavioural, and one is 25 tests that never touch the grant path. Those are not
implementation lapses. They are what a lock produces when its concepts have no falsifiers. Repeating that
pattern at v0.6 scale will be discovered false at v0.7 scale.

**Second — restore the evidence base inside the lock phase.** Four mechanical changes, three of them one
line of YAML: production suite in CI (non-blocking is fine), fix the stale constant so CI's first step
passes, wire the codegen `--check` that already exists and already returns 1, wire the dogfood gate that
already exists and is unused. None decides an architecture question. All four make the lock's claims
checkable. If the lock declines, it should say in writing that its decisions were ratified under gates known
to be non-behavioural.

**Third — lock roughly fourteen primitives and explicitly refuse the rest.** Lock what is irreversible:
envelope lineage, Principal as a type, capability and budget lineage on the Receipt, attenuation and
dispatch ordering, sink-class integrity, fail-closed authority, evaluator exteriority enforced at the
reducer, ledger authority and durability, the plugin wire, the identity trinity, the trajectory schema.
Refuse to lock `Project` (unless its definition is written — it appears zero times in either tree), `Task`,
`Skill`, `Orchestrator`, `Experiment`, `Promotion`, `Meta-Harness`, and `Cache`. They sit above the plugin
line, they have no implementation to lock against, and locking them manufactures the migration debt the lock
exists to prevent.

**Fourth — add the duplication gate.** *Parecer v4* proposed it; the current lock omits it. A parity gate
deletes today's duplicates; a duplication gate prevents tomorrow's fork. The fork has happened twice. Without
a detector, the lock's most consequential decision — one canonical tree — has no enforcement mechanism at
all, only a shared intention.

If only one recommendation survives: **lock the envelope lineage fields (P0-A)**. Everything else in this
report can be revised later at the cost of code. Envelope fields can only be revised later at the cost of the
ledger's own history — and the ledger is the only thing in this architecture that is supposed to be true.

---

### Comparison Summary — Staff Engineer vs Independent Tech Lead

**Both agree:** Python-first, no Rust, no third tree · `packages/` canonical, `layer0/` absorbed · decision
plane vs authoritative state plane · `Agent = Principal + HarnessInstance`, spawn subset invariants · graph
as event projection, no DAG engine, no graph DB · identity trinity `D_H`/`D_R`/`D_X` · hybrid event sourcing,
CAS for bytes, four-way replay taxonomy, SQLite WAL · wire-first JSON-RPC/UDS, five SPIs, `in_process` as
privilege, ADR-0005 freeze · exterior signed evaluator, not a plugin · concurrency modelled, execution
sequential · Meta-Harness / WASM / attestation / distribution / competence graph deferred · current CI is
false confidence · Protobuf is transport, JCS is identity.

**Partially agree:** Convergence mechanics — they merge after a parity gate; I delete `layer0/kernel` and the
duplicated `layer0/events` outright, port forward the two genuine kernel fixes, rewrite the fail-open modules
before promotion, and add a duplication gate · `project_id` — they make it mandatory, I require a definition
first or substitute `root_episode_id` · P0-12 deferrals — I lock the trajectory schema now and adopt
provenance-based corpus admission · replay — I adopt their taxonomy and add the falsifier they do not identify.

**Disagree:** CI sequencing. They defer implementation to the first code phase; I carve out four mechanical,
non-architectural changes inside the lock, because the lock's evidence base *is* the CI system, that system
currently certifies a self-signing judge and an unenforced capability ceiling as green, and it is failing on
its own first step.

**Where I would modify their proposal:** add proof obligations to every locked concept (their P0 list has no
falsifiers) · add an ADR resolving A-4/I-8, which is a false statement in the header of the new tree's
most-imported file · add fail-closed authority as a locked semantic, because four independent fail-open
defaults currently nullify the shipped harness's capability ceiling · add the schema reconciliation decision,
which is a ledger migration that cannot be discovered cheaply later · add the duplication gate · narrow the
concept list with explicit refusals rather than an implicit scope · note that their P0-5 is unimplementable
as written on the current emitter.

**Where their proposal is stronger:** the identity trinity is a genuinely original contribution I adopt
verbatim · the four-way replay taxonomy is more precise than anything in the normative corpus · their scope
discipline ("stop before roadmap, sprints, production code") is correct and I keep it, minus four carve-outs ·
their conflict log against the supporting documents (Rust core, third `core/` tree, evaluator-as-plugin,
hot-swap) is well-reasoned and I concur with every rejection · their choice of `packages/` as canonical is
*more* defensible than they claim, since their own north-star document argues both sides.

**Where this proposal is stronger:** the capability-ceiling chain (compiler drop → four fail-open steps →
`ceiling == ()` on the shipped pack), which no document in the corpus identifies and which nullifies the
system's central security property · the codegen finding, where the gate exists, returns 1, and is unwired ·
the replay tautology and the `BudgetCommitted` no-op, which together invalidate I-4 · the grant path having
zero CI coverage because the fixture verb is `ADVISORY` · the three security weakenings inside the kernel
fork (caller-declared sink class, outcome coercion, unreachable taint predicate) · the TCB budget measuring
the wrong tree through a non-recursive glob · the declared-vs-executed isolation mismatch in the repo's own
shipped pack · the fact that the working `spawn()` already exists in the tree CI does not run · the
observation that M1 was declared complete against gates that do not hold · the proof-obligation rule, which
is a structural answer to why the last lock decayed.

**Insufficient evidence to choose:** `K ≪ N` as a scale model (U-1) · the true cost of CI retarget (U-2) ·
subprocess-per-plugin overhead (U-3) · mhf/v4 envelope reconcilability (U-4) · `fold.py` completeness (U-5) ·
sandbox viability on current kernels (U-6) · which of the 384 `dispatch.py` diff lines are intentional (U-7) ·
statistical power sizing (U-8) · review-lane isolation (U-9).

---

*End of independent Tech Lead assessment. No repository artifact other than this file was created or
modified. No commit was made.*
