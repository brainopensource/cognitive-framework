# AETHER Backend Issues & Observations Log

*Generated during frontend TUI/CLI implementation and validation.*

---

## 1. Issue: `ProposalProduced` Payload Discarded Model Narrative (`proposal.note`)
- **Severity**: High (Caused empty UI / invisible agent responses across TUI & CLI).
- **Subsystem**: `vanguard/packages/agency/episode/engine.py`
- **Symptom**:
  When a model generated a finish proposal or textual response, the UI transcript stayed blank or only showed the user prompt. No agent text bubbles were ever rendered.
- **Root Cause**:
  In `EpisodeEngine._emit_proposal`:
  ```python
  payload: dict[str, Any] = {
      "kind": "ProposalProduced",
      "proposalDescriptor": proposal.descriptor,
      "action": proposal.action,
  }
  ```
  `proposal.note` was omitted from the event payload. The frontend projection (`toConversationTurns`) only inspected `ObservationProduced.text`, but finish actions do not execute tool calls and therefore never emit `ObservationProduced`.
- **Frontend / Bridge Resolution**:
  1. Updated `EpisodeEngine._emit_proposal` to include `payload["note"] = proposal.note[:8000]` whenever `proposal.note` is non-empty.
  2. Updated `@aether/projections` (`toConversationTurns`) to fold `ProposalProduced.note` into `currentAgentTurn.text`.
  3. Added regression tests in `test/agency/test_episode.py` and `@aether/projections/test/projections.test.ts`.

---

## 2. Issue: Headless Entrypoint Receipt Projection Omitted Model Note
- **Severity**: Medium
- **Subsystem**: `vanguard/packages/runtime/entrypoint.py`
- **Symptom**:
  Running `vg code` or `vg explain` in headless mode only projected tool receipts (`[read]`, `[write]`, `[test]`) and completed status, but never rendered the assistant's final textual answer/summary.
- **Root Cause**:
  `entrypoint.py` collected `receipts` from `result.receipts` which only contains tool receipts. It did not inspect `result.events` for `ProposalProduced` carrying model notes.
- **Resolution**:
  1. Updated `entrypoint.py` to extract `last_note` from `result.events` and append a `{"kind": "note", "text": last_note}` projection.
  2. Updated `@aether/client/application/coding-receipts.ts` and `coding-types.ts` to format `kind === "note"` as `[assistant] <text>`.

---

## 3. Issue: Direct Blob Content Retrieval Pending (`BACKEND-GAP`)
- **Severity**: Low (Known architectural seam)
- **Subsystem**: `vanguard/packages/runtime/service/`
- **Symptom**:
  `vg artifact get <sha256:...>` reports:
  `BACKEND-GAP: Direct blob content retrieval for 'sha256:...' is pending RuntimeService BlobStore endpoint.`
- **Root Cause**:
  The `RuntimeService` currently exposes event stream and run execution endpoints over UDS, but does not yet expose a direct blob streaming RPC method for retrieving raw blob bytes via the socket client.
- **Status**:
  Documented as an intentional architecture boundary; CLI fails gracefully with `not_available` code.

---

## 4. Issue: Standalone Daemon PID Lockfile Cleanup on Ungraceful Termination
- **Severity**: Low
- **Subsystem**: `vanguard/packages/runtime/standalone_daemon.py`
- **Symptom**:
  If the daemon process was killed with `SIGKILL` (kill -9), stale PID files and socket files remained in `~/.local/share/aether/runtime/`.
- **Root Cause & Hardening**:
  `_acquire_lock()` verifies PID liveness using `os.kill(old_pid, 0)` before unlinking stale lockfiles, and `start()` cleans dead sockets. Further improvement: attach `atexit` and signal handlers for `SIGINT`/`SIGTERM` to clean up PID files on normal termination.

---

## 5. Issue: Test Persistence Pollution of User Config Directory
- **Severity**: High (Fixed in Wave 0)
- **Subsystem**: `vanguard/clients/tui/src/store.ts`
- **Symptom**:
  Running unit tests was writing `/test/dir` into the developer's real `~/.config/aether/workspaces.json`.
- **Resolution**:
  Configured `TuiStore` to default to `InMemoryPersistenceAdapter` whenever `NODE_ENV === "test"` or `AETHER_IN_MEMORY_PERSISTENCE === "1"`. Cleaned user configuration files.

---

## 6. Issue: `plan` Execution Profile Missing from Historical v1 Profile Test
- **Severity**: Low (Contract test expectation out of sync with new plan preset)
- **Subsystem**: `test/contracts/test_execution_profile_v2.py`
- **Symptom**:
  `test_the_historical_v1_digests_are_pinned_to_literal_values` fails with:
  `AssertionError: Items in the second set but not the first: 'plan' : a preset was added or removed`.
- **Root Cause**:
  `PRESETS` in `vanguard/packages/runtime/profiles.py` was extended to include the `plan` execution profile for read-only planning mode, but `test_the_historical_v1_digests_are_pinned_to_literal_values` strictly asserts `set(pinned) == set(PRESETS)`. Since `plan` is a v2-only preset without historical v1 counterpart, the test should exclude v2-only presets or pin `plan`'s v1 projection digest.

---

## 7. Issue: `_LayeredOperator` Missing `contexts` Attribute Due to `set_task_state` Placement
- **Severity**: High (Crashed runtime session with `AttributeError: '_LayeredOperator' object has no attribute 'contexts'`).
- **Subsystem**: `vanguard/packages/runtime/session.py`
- **Symptom**:
  Running any harness using `_LayeredOperator` crashed at the end of the run during `_telemetry()` or `assemble_trajectory()` with:
  `AttributeError: '_LayeredOperator' object has no attribute 'contexts'`.
- **Root Cause**:
  `def set_task_state(...)` was erroneously defined in the middle of `_LayeredOperator.__init__` (after `PromptAssembler`), capturing `self._handler`, `self.contexts = []`, `self._artifacts`, and `self._meta_controller` inside `set_task_state` instead of `__init__`.
- **Resolution**:
  Moved `self._handler`, `self.contexts = []`, `self._artifacts`, and `self._meta_controller` into `__init__` before defining `def set_task_state(self, state)`.
