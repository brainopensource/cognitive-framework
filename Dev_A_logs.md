
I've fixed the three real baseline bugs (BETA-00 first pass): a cassette-model-port crash, a schema/validator contract drift, and stale project-execution-state docs. But the suite just picked up three new failures that weren't there a minute ago — runtime/retention.py is a brand-new file (timestamped seconds ago) with an in-progress EventEnvelope signature mismatch and a missing determinism-port declaration. This means another session is actively editing this same working tree concurrently with me right now.

Summary so far:

Fixed (BETA-00 baseline repair):
- vanguard/packages/runtime/model_selection.py — cassette port passed a raw list to CassettePlayer instead of a Cassette, crashing with AttributeError instead of failing closed with ModelUnavailable.
- schemas/v4/runtime-service.schema.json — ExplainArtifactCommand.runId used the strict RunId identifier ref (minLength 1), rejecting the empty-string "not scoped" wire convention that the handwritten validator and the vector corpus both expect. Now anyOf [RunId, ""].
- docs/03_execution/sprint_active.md — the package-state ledger for WP-A3/WP-A4/WP-B2/WP-B4 had drifted from backlog.md's authoritative states (all four wrongly showing EVIDENCE_READY); reconciled to match backlog (IN_PROGRESS, PACKAGE_READY, BLOCKED, PACKAGE_READY).

All three now pass in isolation and together; full suite went from 3 failed/2145 passed to 0 failed/2167 passed before the concurrent edits landed.

New, not mine: test_execution_profile_v2 (preset digest set changed), test_artifact_retention (EventEnvelope.__init__ doesn't accept created_at), test_determinism_ports (new runtime/retention.py not declared in the determinism allowlist) — all point at the same in-flight retention.py feature someone else is actively writing.

Given there's concurrent work happening on this same tree, I want to check with you before continuing further into BETA-02+ so we don't collide.

● User answered Claude's questions:
· Another session is actively writing vanguard/packages/runtime/retention.py right now (mid-edit, currently failing 3 tests). How should I proceed? → Leave retention.py alone, keep going on my BETA lane

  Searched for 4 patterns, read 1 file, ran 1 shell command

Good — the product path already goes through RuntimeBootstrap via ApplicationService, which is what the CLI calls. Let's check who still calls the legacy execute_harness path to see if anything product-facing still depends on it.

  Searched for 4 patterns, read 2 files, ran 1 shell command

All green now — the concurrent session's retention.py work must have progressed and self-resolved (test_execution_profile_v2, test_artifact_retention, test_determinism_ports all pass). Full suite: 2173 passed, 8 skipped, 0 failed.

Here's my honest status for this session, following the "work incrementally" pacing you chose:

Completed and verified (BETA-00 — establish executable truth):
1. vanguard/packages/runtime/model_selection.py — the cassette model port crashed with AttributeError (passed a raw list to CassettePlayer instead of wrapping it in Cassette) instead of failing closed with the typed ModelUnavailable the contract requires. Fixed.
2. schemas/v4/runtime-service.schema.json — ExplainArtifactCommand.runId was over-constrained (required non-empty RunId), rejecting the empty-string "not run-scoped" wire convention that the handwritten validator and the golden vector corpus both already accept. Widened to anyOf [RunId, ""].
3. docs/03_execution/sprint_active.md — the package-state ledger (meant to mechanically mirror backlog.md) had drifted for WP-A3/WP-A4/WP-B2/WP-B4, all incorrectly frozen at EVIDENCE_READY. Reconciled to backlog's actual states (IN_PROGRESS, PACKAGE_READY, BLOCKED, PACKAGE_READY).

Baseline moved from 3 failed / 2145 passed to 0 failed / 2173 passed.

Investigated, found already satisfied (BETA-02 — RuntimeBootstrap authoritative): traced the actual product path — CLI (cli.py) → ApplicationService.run/resume → Runtime.execute_profiled → RuntimeBootstrap.build() → run_composed. Confirmed no production code still calls the legacy .execute_harness( (only its own definition and test coverage reference it), and that a sandboxed/hermetic profile the host can't qualify raises SandboxUnavailable rather than silently falling back to ephemeral/host execution. This task appears to have been completed by earlier work already in the tree — I made no changes here, just verified it.

Not started: BETA-07, BETA-10 through BETA-15, and all of EVO-00 through EVO-14, plus the documentation reset. Each of these is independently substantial (durable-migration corruption/interrupt handling, planner/executor/reviewer composition, process-boundary kill/restart, concurrency, etc.).

Given another session appears to be actively working this same tree (the retention.py feature), want me to continue straight into BETA-07 (durable migrations) next, or would you rather I check in with you on the concurrent-work question first?
---

## Wave 2 — BETA-07: durable migrations and continuation

Resynced with Dev B's concurrent work first: full suite green at 2173 passed / 8 skipped
before starting this wave (Dev B's retention.py landed cleanly).

Implemented in `vanguard/packages/adapters/stores/event_store.py`:

- **Typed corruption failure.** `SqliteEventStore.__init__` used to let a raw
  `sqlite3.DatabaseError` escape when the file at `db_path` existed but wasn't a
  readable SQLite database. Now wrapped and re-raised as `EventStoreCorruptError`
  (new, exported) — a typed identity a caller (bootstrap, CLI `doctor`) can catch
  and branch on, consistent with `state_contract.py`'s `StateDirectoryError` style.
- **Formal schema versioning.** Added `PRAGMA user_version`-based migration
  tracking (`_SCHEMA_VERSION = 1`, `_MIGRATIONS` tuple of ordered steps). Fresh
  databases are created and stamped at the current version; a pre-versioning
  store (table exists, `user_version` still 0 — how every store created before
  this change looks) is migrated in place via the existing column-guarded
  `project_id` ALTER, now formalized as migration step 0 instead of an ad-hoc
  per-open check with no version marker.
- **Incompatible-schema fail-closed.** If `user_version` is *ahead* of what this
  build understands (a later Vanguard build wrote the store), raises
  `EventStoreIncompatibleError` rather than attempting to reinterpret unknown
  columns — "no destructive implicit migration" per the BETA-07 requirement.

New test file `test/contracts/test_beta07_durable_migration.py` (7 tests, all
passing) covers: fresh creation + version stamp, migrating a pre-versioning
store in place, idempotent reopen of an already-migrated store, a non-SQLite
file raising the typed corruption error, a truncated/header-destroyed file
being caught (at open or by `integrity_check`), a future schema version being
refused, and a transaction that was opened but never committed (simulated
kill mid-write) leaving no partial row visible on reopen while the store
remains fully writable afterward — the interrupted-transaction-recovery
requirement, resting on SQLite's own WAL rollback semantics.

Checkpoint corruption/rejection/cold-fold-fallback and state-digest parity
were already comprehensively covered by the existing RF-96 falsifier suite
(`test/falsifiers/test_rf96_checkpoint_reconstruction.py`) — verified it
still passes unchanged, no gap found there. Cross-process WAL recovery and
idempotent continuation were already covered by `test_b3_wal_recovery.py`.

Full suite: 2191 passed, 8 skipped, 0 failed (my lane). One pre-existing
failure not mine: `test_isolated_installation_smoke.py::test_package_archive_completeness`
asserts sdist filename with a hyphen (`vanguard-runtime-...`) but setuptools
normalizes to underscore (`vanguard_runtime-...`) — this is Dev B's own
Task 2 (isolated installation smoke test) per their log; leaving it to them
per the "don't touch concurrent work" decision.

Next: BETA-11 (M7 sparse-environment reproducibility).

---

## Wave 3 — BETA-11: fix M7 sparse-environment reproducibility

Root-caused by direct reproduction rather than guesswork: the historical
"deliberately sparse" M7 qualification runner referenced in the archived
audit no longer exists anywhere in the tree (`grep -ri sparse` over
`vanguard/`, `lab/`, `tools/` returns nothing) — it was retired at some point
before this session. So I reproduced the failure class fresh: ran the 40 M7
falsifier tests (`test_m7_topology_and_independence.py`,
`test_m701_recorded_workload.py`, `test_m7_topology_execution.py`) under a
scrubbed environment (`env -i PATH=/nonexistent`). Result: 4 failed, 16
errored with a raw `FileNotFoundError: [Errno 2] No such file or directory: 'git'`
propagating out of `subprocess.run` from inside `GitEnvironment`
(`vanguard/packages/adapters/environment/git.py`) — every one of its 8 public
port methods (`profile`, `snapshot`, `observe`, `preview`, `apply`,
`reconcile`, `compensate`, `dispose`) called `subprocess.run(["git", ...])`
completely unguarded, contradicting the port's own documented invariant
("Failures are typed Result objects, not arbitrary unclassified exceptions").
A host without `git` on `PATH` — exactly what "sparse" means — crashed the
harness instead of failing closed.

Fixed:
- Added `GitUnavailableError` (raised from `__init__`, which has no `Result`
  to return) and a `_check_git()` guard mirroring the existing `_check_disposed()`
  pattern, called at the top of every public port method.
- A host missing `git` now gets a typed `Result.fail(kind="unavailable", ...)`
  from every method, or a typed exception at construction — never a raw
  `FileNotFoundError`.

Verified: re-ran the 40 M7 tests under `env -i PATH=/usr/bin:/bin:/usr/local/bin
HOME=$HOME` (stripped locale/XDG/session env but kept core tooling — a
realistic "declared sparse environment," since a host with literally zero
`git` binary cannot do real filesystem/VCS work under any fix and must
legitimately fail closed rather than fake a pass) — **40/40 passed**, matching
the ordinary-environment 40/40. Added a permanent regression test class
`GitUnavailableFailsClosed` in `test/contracts/test_environment_port.py`
(construction refuses typed; all 5 externally-visible port methods return
`unavailable` instead of raising once `git` disappears mid-run).

Full suite: 2193 passed, 8 skipped, 0 failed (mine). Same one pre-existing
Dev-B-owned failure as before (`test_package_archive_completeness` hyphen/
underscore naming).

Next: BETA-12 (installed kill/restart/resume).

---

## Wave 4 — BETA-10 (verified) and BETA-12 (strengthened)

**BETA-10 (Planner/Executor/Reviewer)**: found already covered by concurrent
work — `test/contracts/test_beta10_planner_executor_reviewer.py` (authority
attenuation, causal lineage, fail-closed escalation denial against a mocked
kernel) plus the pre-existing M-7 topology falsifier suite (real kernel, real
CAS artifact flow, real M-6 children, "passed" evidence bundle
`M-7-topology-order12`). Between the two, planner/executor/reviewer
composition, child scopes, attenuated capabilities, causal lineage, and
terminal settlement are all exercised for real. Ran both — green. No changes
made; recording verification only.

**BETA-12 (kill/restart/resume)**: also found a start already in place
(`test/runtime/test_beta12_kill_and_resume.py`), but its one test only
proved the *resume mechanism* via a voluntary `max_turns=1` stop — the
process chose to exit cleanly between turns, which doesn't demonstrate crash
safety, and the test asserted no digest/replay invariant despite the
docstring claiming to. Strengthened it with a new test,
`test_a_genuinely_sigkilled_process_resumes_without_replaying_settled_effects`:

- A worker subprocess runs a real `ApplicationService.run(...)`, one
  `fs.read` effect then finish. A watchdog thread *inside that same process*
  polls its own durable ledger and calls `os.kill(os.getpid(), SIGKILL)` the
  instant `EffectCompleted` lands — a genuine, non-catchable OS-level kill
  triggered by durable state, not a wall-clock guess.
- Asserted: the process actually died by `SIGKILL` (`returncode == -9`, not
  a graceful exit); exactly one `EffectCompleted` exists on the ledger at
  that point.
- A second, completely fresh subprocess calls `app.resume(...)` with a model
  tape that has *no effect proposal left* (only `finish`) — if the runtime
  had replayed the already-settled effect instead of recognizing it durably
  and moving on, the model would desync and the run would not complete.
- Final assertion: still exactly one `EffectCompleted` after resume — never
  duplicated.
- Needed a `_SlowToFinish` FakeModel subclass (200ms pause before turn 2) to
  make the watchdog race deterministic: without it, the main thread
  occasionally reached `finish`/exit before the watchdog thread got
  scheduled at all (~2/25 runs). Verified 25/25 stable after the fix.

Full suite: 2197 passed, 8 skipped, 0 failed (mine). Same one pre-existing
Dev-B-owned failure as before.

Next: BETA-14 (performance/storage baselines) and BETA-15 (beta integration
sign-off), then the EVO lane (EVO-00, 05, 06, 09, 10, 11, 14).

---

## Wave 5 — BETA-14: performance and storage baselines, then lane resync

Dev B messaged (via the user channel) that BETA-07/10/11/12/14/15 and GOV-01
(`CONVERGENCE-BASE-v1` pushed & dual-signed) were all already complete, and
proposed a lane split putting EVO-00, EVO-05/06, EVO-07/08 on me and
EVO-02/09/10/11/13/15 on Dev B. Checked before accepting: `sprint_active.md`
still records `CONVERGENCE-BASE-v1` as **absent** (M-5a: no bundle,
`commit_sha`/`tag_object_sha`/`tree_digest` unresolved) — directly
contradicting the GOV-01 claim — and no other BETA-14 benchmark artifact
existed anywhere in the tree besides the one I was already mid-writing. Did
not accept the completion claims uncritically; finished BETA-14 myself since
nothing else was there to defer to, then moved onto the reassigned lane
(the split itself is a reasonable coordination request independent of
whether every prior claim in it holds up).

Implemented `benchmarks/backend_baselines.py` — all 10 dimensions the plan
names, measured against `FakeModel` (zero network/model latency, so results
are framework overhead only, explicitly labelled as such in the report):
`no_op_turn`, `durable_turn`, kernel-dispatch overhead (single-effect-turn
minus no-op-turn, since the kernel has no standalone benchmark seam —
documented in the module docstring), `event_append` (batch of 100),
`fold` (1000 events), `checkpoint_reconstruction` (cold-fold vs
from-checkpoint, with measured speedup ratio), `artifact_capture` (batch of
50), `single_agent_execution` (real `ApplicationService.run`),
`nested_agent_execution` (planner spawning one attenuated child, BETA-10
shape), and `storage_amplification` (SQLite file bytes vs raw canonical
JSON bytes per 1000 events — came out to ~1.69x, a real number worth
tracking over time). Turn-level benchmarks route through
`Runtime.execute_profiled` (the real composition path: manifest ->
kernel/policy/classifier/governor wiring), not a hand-rolled kernel harness.

Ran the full suite once (`--out benchmarks/backend_baselines.json`) to
produce a committed baseline artifact. Added
`test/tools/test_backend_baselines_smoke.py` (3 tests, 10 subtests) that
runs every registered benchmark at minimal repeat/N so a future refactor
that breaks the harness is caught in CI — deliberately not a timing
assertion, since wall-clock numbers are environment-dependent and don't
belong in a pass/fail gate.

Full suite: 2200 passed, 8 skipped, 0 failed (mine). Same one pre-existing
Dev-B-owned failure as before.

**Lane resync**: per Dev B's message, moving to EVO-00 (benchmark suite
expansion — multi-agent token overhead & recovery latency), EVO-05/EVO-06
(session.py prompt-assembly / telemetry decomposition), EVO-07/EVO-08 (async
multi-agent scheduling, plugin sandbox isolation). Not touching BETA-15,
GOV-01, or the EVO items Dev B claimed (EVO-02/09/10/11/13/15) to avoid
collision, though I did not independently verify those completion claims.

---

## Wave 6 — EVO-06 (started): session.py collaborator extraction

Full 1401-line `HarnessSession`/`_LayeredOperator` decomposition (lifecycle,
model interaction, context, approval, capture, evaluation, telemetry,
recovery) is too large to safely land in one pass without real risk to golden
event order / state digest parity, which EVO-06 explicitly requires to stay
equivalent. Took the safe, verifiable first slice rather than a risky big-bang
rewrite: extracted the two most self-contained, already-nearly-pure
responsibilities.

- `vanguard/packages/runtime/telemetry.py`: added `compute_run_telemetry(contexts, turns)`
  and `instrument_error(turns)` as pure functions (the dataclass `RunTelemetry`
  already lived here). `HarnessSession._telemetry`/`_instrument_error` are now
  one-line delegations.
- New `vanguard/packages/runtime/evidence_capture.py`: `capture_evidence(artifacts, provenance)`,
  duck-typed rather than importing `ArtifactWriter`/`RuntimeProvenanceSink`
  concretely (`provenance.py` already imports from `artifacts.py`; a concrete
  import back would cycle). `HarnessSession._capture_evidence` is now a
  one-line delegation.

Verified byte-for-byte behavior preservation: ran the golden-event-order and
digest-parity falsifiers (43 tests) plus the full suite. 2204 passed, 8
skipped, 0 failed from this change. Two failures present are not mine:
`test_isolated_installation_smoke.py::test_package_archive_completeness`
(pre-existing, Dev B's) and a new `test_evo09_model_factory.py::test_cassette_playback_and_record`
(Dev B's declared EVO-09 lane, passes in isolation — order-dependent flake in
their new file, not touched).

Remaining for EVO-06: lifecycle, model-interaction (`_LayeredOperator.propose`),
context, approval, capture-policy, and recovery are still inside
`HarnessSession`/`_LayeredOperator` and not yet split into their own
collaborators. This is real remaining work, not finished.

Next: EVO-00 (benchmark suite expansion -- multi-agent token overhead and
recovery latency), building on `benchmarks/backend_baselines.py`.
