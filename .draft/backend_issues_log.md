# AETHER Backend Issues & Observations Log

*Generated during frontend TUI/CLI implementation and validation.*

**Verified against the tree 2026-09-04** on `feat/strongforce_beta_release_v093`.
Five of the original seven entries are implemented and have been removed from the
open list; they survive only as the resolved ledger at the bottom, because two of
them are preconditions of work that is still on the runway. Two entries remain
open below.

---

## 3. Issue: Direct Blob Content Retrieval Pending (`BACKEND-GAP`)
- **Severity**: Low as a CLI gap; **Medium as an evidence gap** (see impact).
- **Subsystem**: `vanguard/packages/runtime/service/`, `vanguard/clients/cli/src/commands/artifact.ts:73-85`
- **Symptom**:
  `vg artifact get <sha256:...>` reports:
  `BACKEND-GAP: Direct blob content retrieval for 'sha256:...' is pending RuntimeService BlobStore endpoint.`
- **Root Cause**:
  `RuntimeService` exposes event stream and run execution endpoints over UDS, but
  does not expose a blob streaming RPC for retrieving raw blob bytes via the
  socket client. The CLI fails gracefully with a `not_available` code and
  refuses direct database or filesystem access, per architecture boundaries.
- **Status**: **OPEN — intentional architecture boundary, now with a consumer.**
- **Impact (new, 2026-09-04)**:
  This is no longer only a CLI convenience gap. `ELECTROWEAK_SYNTHESIS_FINAL_v093.md`
  §9.3 requires that a malformed completion's **full raw body be retrievable from
  CAS by its digest**, and T-90 (dialect classifier provenance) makes that
  retrieval a falsifier. §2.2's "Plane 2" zero-loss traceability guarantee has the
  same dependency. Writing the digest without a read path satisfies the letter of
  provenance and not its purpose.
- **Suggested disposition**: fold the read path into **T-90**'s falsifier rather
  than opening a package — one RPC method on an existing service.

---

## 6. Issue: `plan` Execution Profile Missing from Historical v1 Profile Test
- **Severity**: **High** (contract test is red on the current branch).
- **Subsystem**: `vanguard/packages/runtime/profiles.py:257`, `test/contracts/test_execution_profile_v2.py:88-94`
- **Status**: **OPEN — currently failing.**
- **Reproduction** (2026-09-04, this branch):
  ```
  $ .venv/bin/python -m unittest test.contracts.test_execution_profile_v2
  FAIL: test_the_historical_v1_digests_are_pinned_to_literal_values
  AssertionError: Items in the second set but not the first: 'plan'
  Ran 9 tests — FAILED (failures=1)
  ```
- **Root Cause**:
  `PRESETS` was extended with the `plan` read-only planning profile by commit
  `493ea0cf` ("feat(frontend): Refactor TUI CLI Code — Using Opentui and Bun")
  without extending the pinned set in the contract test, which asserts
  `set(pinned) == set(PRESETS)`. `plan` is a v2-only preset with no historical v1
  counterpart.
- **Why this matters beyond a red test**:
  The test's own docstring states that `profile_digest` enters `D_R`, so moving it
  *"re-identifies every historical run and breaks RF-86 baseline comparison."*
  T-79 (preset catalog unification) and the `MS-CONTROL` qualification canary both
  land on top of this contract. Preset work shipped while its identity guard is red
  removes the ability to compare against any prior baseline.
- **Resolution options** (either is acceptable; the third is not):
  1. Pin `plan`'s v1 projection digest alongside the existing four.
  2. Exclude v2-only presets from the membership assertion, and assert the four
     historical digests unchanged.
  3. ~~Re-bless the four existing digests~~ — **prohibited**. Per the docstring,
     a changed historical digest is *"a hard failure, never a value to re-bless."*

---

## Resolved — verified implemented, retained for traceability only

No action required on any row below. They are kept because entries 1 and 2 are
**preconditions of T-82** (fenced-JSON action unwrapping from `note` payloads):
that task assumes the model's narrative reaches the ledger, which is true only
because of these two fixes. Removing the note plumbing as "unused" would silently
break it.

| # | Issue | Fix verified at |
|---|---|---|
| 1 | `ProposalProduced` payload discarded `proposal.note`, blanking the UI transcript | `agency/episode/engine.py:921` — `payload["note"] = proposal.note[:8000]`; folded into `toConversationTurns` by `@aether/projections` |
| 2 | Headless entrypoint receipt projection omitted the model note | `runtime/entrypoint.py:119,128,211-212` — `last_note` extracted from `result.events`, emitted as a `{"kind":"note"}` projection |
| 4 | Daemon PID lockfile survived `SIGKILL` | `runtime/standalone_daemon.py:91` (`_acquire_lock` PID liveness probe) and `:177-178` (`SIGINT`/`SIGTERM` handlers) |
| 5 | Tests wrote `/test/dir` into the real `~/.config/aether/workspaces.json` | `clients/tui/src/store.ts:160-161` — `InMemoryPersistenceAdapter` under `NODE_ENV=test` or `AETHER_IN_MEMORY_PERSISTENCE=1` |
| 7 | `_LayeredOperator` missing `contexts` (`AttributeError` at telemetry) | `runtime/session.py` — `self._handler`, `self.contexts`, `self._artifacts`, `self._meta_controller` all initialised in `__init__`, before `set_task_state` |
