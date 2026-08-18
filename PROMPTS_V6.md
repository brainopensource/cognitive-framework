# Parallel Sprint Execution Prompts (v0.5.0 Empirical Baseline)

This document contains **two concurrent, non-blocking developer prompts** designed to execute the active sprint (`docs/03_sprints/sprint_active.md`) in parallel with zero git collision overlap.

---

# DEV 1 PROMPT: Architecture, Context Compaction, Live CLI & Proof
**Assigned Lanes:** ALFA (Orchestration & Context) + GAMMA (Product CLI & Greenfield Proof)

```markdown
# ROLE
You are Lead Software Engineer (DEV 1) responsible for Architecture, Context Compaction, and Live Greenfield Execution.

# WORKSPACE CONTEXT & DOCUMENTATION
Adhere strictly to:
1. `docs/03_sprints/sprint_active.md` (Active Sprint Board — Lanes ALFA & GAMMA).
2. `docs/02_roadmap/backlog.md` (Task references).
3. `AGENTS.md` (Lattice import rules, TCB constraints, and test commands).

# EXCLUSIVE WRITE SCOPE (Do NOT touch files outside this list)
- `vanguard/packages/agency/episode/**`
- `vanguard/packages/agency/context/**`
- `vanguard/packages/runtime/root.py` (EXCLUSIVE TO DEV 1)
- `vanguard/packages/runtime/lab_driver.py`
- `vanguard/packages/runtime/coding_entrypoint.py`
- `test/agency/**`
- `test/runtime/test_composition_root.py`
- `test/runtime/test_lab_driver.py`
- `lab/**`
- `tools/run_v0450_greenfield_campaign.py`

# ASSIGNED TASKS & STEP-BY-STEP IMPLEMENTATION SEQUENCE

1. **[TSK-CORE-001] Wire Provenance Spans into Composition Root**
   - File: `vanguard/packages/runtime/root.py`
   - Action: Wire `receipt_labeller` into `_admit_turn_result` so that tool-result execution spans accumulate in the session provenance set (`K-33`, S1(e)).
   - Verification: `python3 -m unittest test.agency.test_provenance`

2. **[TSK-CORE-002] Wire Child Return Spans on Subagent Spawning**
   - File: `vanguard/packages/agency/episode/engine.py`
   - Action: Update `spawn()` to call `Accumulation.child_return` so that spawned child returns are treated as untrusted-derived spans.
   - Verification: `python3 -m unittest test.agency.test_spawn`

3. **[TSK-CTX-001] Bind Skill Index into Context Compiler**
   - File: `vanguard/packages/agency/context/compiler.py`
   - Action: Ensure `format_skill_index` is invoked during L2/L3 context compilation rather than being an unused export.
   - Verification: `python3 -m unittest test.agency.test_context_compiler`

4. **[TSK-CTX-002] Wire or Cleanly Deprecate RegroundPolicy**
   - File: `vanguard/packages/agency/context/regrounding.py`
   - Action: Wire `RegroundPolicy.shouldRun` to observe workspace changes or cleanly formalize its invocation from the engine.
   - Verification: `python3 -m unittest test.agency.test_regrounding`

5. **[TSK-HAR-001] Implement In-Place Writes in Lab Driver**
   - File: `vanguard/packages/runtime/lab_driver.py`
   - Action: Implement the `--in-place` flag to apply patches directly to the target repository workspace under `RootlessSandboxRunner` (`bwrap`).
   - Verification: `python3 -m unittest test.runtime.test_lab_driver`

6. **[TSK-HAR-003] Relocate Mocks to Test Directory**
   - File: `vanguard/packages/runtime/coding_entrypoint.py`
   - Action: Move `_fake_backend` out of production runtime into `test/fixtures/`.
   - Verification: `python3 tools/check_boundaries.py`

7. **[TSK-HAR-005] Execute Greenfield Live Verification Campaign**
   - File: `tools/run_v0450_greenfield_campaign.py`
   - Action: Run unmocked verification on `lab/tasks/greenfield-v0450-webapp/` ensuring `live: true` and `fake: false` passing all behavioral oracles.
   - Verification: `python3 tools/run_v0450_greenfield_campaign.py`

# FINAL VERIFICATION GATES
Run all checks before reporting completion:
- `python3 tools/check_boundaries.py`
- `python3 tools/check_tcb_budget.py`
- `python3 tools/run_active_contract_tests.py`
- `python3 -m unittest discover -s test -t .`
```

---

# DEV 2 PROMPT: Security Kernel, Event Ledger, Grants & Evaluator Listener
**Assigned Lane:** BETA (Security, Grants, Ledger & Evaluation)

```markdown
# ROLE
You are Lead Security & Systems Engineer (DEV 2) responsible for Kernel Dispatch, Cryptographic Grants, Event Ledger, and Evaluation Triggers.

# WORKSPACE CONTEXT & DOCUMENTATION
Adhere strictly to:
1. `docs/03_sprints/sprint_active.md` (Active Sprint Board — Lane BETA).
2. `docs/02_roadmap/backlog.md` (Task references).
3. `AGENTS.md` (Lattice import rules, TCB constraints, and test commands).

# EXCLUSIVE WRITE SCOPE (Do NOT touch files outside this list)
- `vanguard/packages/kernel/dispatch.py` (EXCLUSIVE TO DEV 2)
- `vanguard/packages/kernel/grants.py`
- `vanguard/packages/domain/ledger/events.py`
- `vanguard/packages/domain/ledger/reducer.py` (Kind arms only)
- `vanguard/packages/runtime/evaluation_listener.py` (NEW MODULE)
- `vanguard/packages/runtime/autonomous_grant.py` (EXCLUSIVE TO DEV 2)
- `vanguard/packages/runtime/governance/**`
- `vanguard/packages/adapters/evaluators/**`
- `test/kernel/**`
- `test/runtime/test_autonomous_coding_grant.py`
- `test/runtime/test_*ledger*`
- `test/runtime/test_evaluation_listener.py`
- `test/contracts/**`

# ASSIGNED TASKS & STEP-BY-STEP IMPLEMENTATION SEQUENCE

1. **[TSK-LED-001] Emit EpisodeStarted on Ledger Beginning**
   - File: `vanguard/packages/domain/ledger/events.py` & `vanguard/packages/domain/ledger/reducer.py`
   - Action: Define and emit the `EpisodeStarted` event at session/episode inception, ensuring the event ledger captures the initial task and environment snapshot.
   - Verification: `python3 -m unittest test.domain.test_ledger_events`

2. **[TSK-LED-002] Record ApprovalResolved onto Event Ledger**
   - File: `vanguard/packages/runtime/governance/approvals.py`
   - Action: Ensure operator approval resolutions (`ApprovalResolved`) are durably written to the event ledger $L$ (not solely to an in-memory queue) to support crash recovery and replay.
   - Verification: `python3 -m unittest test.runtime.test_approvals`

3. **[TSK-LED-003] Enforce Closed EVENT_KINDS Writer Validation**
   - File: `vanguard/packages/domain/ledger/events.py`
   - Action: Reject unknown `payload.kind` entries at the ledger writer boundary, ensuring only valid canonical event types can be appended to $L$.
   - Verification: `python3 -m unittest test.domain.test_event_writer`

4. **[TSK-EVAL-001] Implement Ledger-Triggered Evaluation Listener**
   - File: `vanguard/packages/runtime/evaluation_listener.py` (New Module)
   - Action: Implement the `EvaluationListener` daemon that listens to `EpisodeCompleted` events on ledger $L$ and emits `EvaluationRequested`, completely decoupling the evaluator from synchronous worker execution (`D-02`).
   - Verification: `python3 -m unittest test.runtime.test_evaluation_listener`

5. **[TSK-HAR-002] Wire AutonomousGrant for INTERACTIVE & BENCHMARK Modes**
   - File: `vanguard/packages/runtime/autonomous_grant.py` & `vanguard/packages/kernel/grants.py`
   - Action: Implement signed Ed25519 token verification constraining workspace paths, permitted verbs, budget limits, and workspace SHA-256 digests. Ensure `BENCHMARK` mode fails closed on unapproved writes.
   - Verification: `python3 -m unittest test.runtime.test_autonomous_coding_grant`

6. **[TSK-SPEC-001..010] Freeze ADR-0051 & Inverted K-40 Specifications**
   - File: `docs/main_v4/05_vanguard_security_architecture_and_tcb_v040.md` & `docs/main_v4/02_vanguard_charter_claims_and_non_claims_v040.md`
   - Action: Formalize that only `PRIVILEGED` sinks require grants (while all 3 classes traverse dispatch), and document the out-of-process Evaluator (UID 10002).
   - Verification: `python3 tools/run_active_contract_tests.py`

# FINAL VERIFICATION GATES
Run all checks before reporting completion:
- `python3 tools/check_boundaries.py`
- `python3 tools/check_tcb_budget.py`
- `python3 tools/run_active_contract_tests.py`
- `python3 -m unittest discover -s test -t .`
```
