
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
