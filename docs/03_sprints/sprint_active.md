---
id: SPRINT-050-ACTIVE
file: docs/03_sprints/sprint_active.md
title: "Active sprint — v0.5.0 Empirical Baseline (S-truth → S-product)"
status: ACTIVE
milestone: v0.5.0
timebox: 10 working days
branch: feat/v050-empirical-baseline
backlog: docs/02_roadmap/backlog.md
milestones: docs/02_roadmap/milestones.md
req: REQ-TRUST-001
last_reviewed: 2026-08-18
---

# Sprint board — v0.5.0 Empirical Baseline

**Sentence this sprint makes true:**

> A composed `HarnessSession` accumulates justifying spans, writes a durable beginning and
> approval/evaluation trail on \(L\), and a live INTERACTIVE run can `--in-place` write a greenfield
> workspace under a signed `AutonomousGrant` — without a fake backend and without a second workflow
> engine.

This is **one** Agile increment of `ROAD-MILE-01` §3 (gates G-050-01…12). It is **not** a plan for
v0.6.0+. Research horizons stay in `docs/02_roadmap/backlog.md` §9 until this tag is green.

**Predecessor:** v0.4.5-beta (`feat/harness-cli-v045`). Kernel dispatch, lattice, TCB tripwire, and
`AutonomousGrant` *library* already exist. This sprint **wires** them.

---

## 0. Law for this sprint

### 0.1 Invariants (fail the PR if broken)

| ID | Invariant | Check |
|---|---|---|
| I-01 | Episode is the only execution primitive (`A-01`). No playbook *runtime*, no DAG dispatcher. | No new `runtime/loops/`; no playbook module that calls `Kernel.dispatch` |
| I-02 | One effect path `Kernel.dispatch` (`AT-01`) | `python3 tools/check_boundaries.py` |
| I-03 | Evaluator unreachable from agency (`A-05`) | Same + existing spine tests |
| I-04 | BENCHMARK fail-closed on privileged writes | New GAMMA tests |
| I-05 | One effect per turn | Existing translator tests |
| I-08 | TCB ≤ 1438; kernel growth needs ADR-0054 | `python3 tools/check_tcb_budget.py` |
| I-09 | `REQ-*` in every PR body | `python3 tools/check_pr_requirements.py` |

### 0.2 Explicit non-goals (do not pull into this board)

Playbook interpreter, operator registry, \(G_C/G_E\) walker, independence groups, `coding_*` extraction
from `runtime/`, Tree-sitter indexer, TUI/GUI as a backend gate, `MetaLoopEngine`, MCP-as-authority,
kernel rewrite, restoring K-40 “evaluator in the worker bwrap”.

**ALFA “playbook interpreter” (Prompt 3) is refused as written.** A playbook that *dispatches* is
`REJ-01` / `N-20` and `TSK-EPIC-090-002` (v0.9.0). ALFA instead owns the **session lifecycle** a
future playbook would only *constrain*: spans, spawn provenance, `EpisodeStarted`, child denials,
re-grounding-as-observation, skill-index in the compiler.

### 0.3 Status vocabulary

`[TODO] ❌` · `[DOING]` · `[DONE] ✅` · `[BLOCKED]` · `[HANDOFF]` (needs another lane’s file).

---

## 1. Lanes — write scopes (zero overlap)

A task that needs a file outside its scope is a **handoff**, not a drive-by edit.

| Lane | Role | Write (create/edit) | Read-only |
|---|---|---|---|
| **ALFA** | Architecture & orchestration | `vanguard/packages/agency/episode/**` · `vanguard/packages/agency/context/compiler.py` · `vanguard/packages/agency/context/regrounding.py` · `vanguard/packages/agency/context/layers.py` (only if compiler requires it) · **`vanguard/packages/runtime/root.py` (exclusive)** · `test/agency/**` · `test/runtime/test_composition_root.py` · `test/broken/**` (composed provenance MF only) | kernel, domain ledger, lab, CLI, `docs/main_v4` |
| **BETA** | Security, ledger, evaluation | `vanguard/packages/kernel/dispatch.py` · `vanguard/packages/kernel/grants.py` · `vanguard/packages/domain/ledger/events.py` · `vanguard/packages/domain/ledger/reducer.py` (kind arms only) · **new** `vanguard/packages/runtime/evaluation_listener.py` · `vanguard/packages/runtime/service/service.py` · `vanguard/packages/runtime/autonomous_grant.py` · `vanguard/packages/runtime/governance/**` · `vanguard/packages/adapters/evaluators/**` (listener transport only) · `test/kernel/**` · `test/runtime/test_autonomous_coding_grant.py` · `test/runtime/test_*ledger*` · `test/runtime/test_evaluation_listener.py` (new) · `test/contracts/**` (event kind goldens) | `root.py`, `engine.py`, `lab_driver.py`, `coding_entrypoint.py` |
| **GAMMA** | Product CLI & live proof | `vanguard/packages/runtime/lab_driver.py` · `vanguard/packages/runtime/coding_entrypoint.py` · `test/runtime/` (entrypoint + fake-backend dest) · `lab/**` · `tools/run_v0450_greenfield_campaign.py` · `tools/rule_test_map.py` · `README.md` · `docs/main_v4/**` · `docs/scrum/sprints/` evidence for this sprint · `vanguard/packages/agency/manifests/vg-table-default/**` + registry/kinds **only** for TSK-HAR-007 | `root.py`, `kernel/`, `engine.py` |

**Collision seals**

1. **`root.py` — ALFA only.** BETA does not patch `_evaluate`. ALFA replaces the inline RPC with a
   `EvaluationScheduler` protocol call (empty/no-op default). BETA implements
   `evaluation_listener.py` and GAMMA/ALFA **wire the impl at compose** via a one-line constructor
   argument that ALFA lands first (Day 1 stub).
2. **`autonomous_grant.py` — BETA only.** GAMMA **imports** `create_autonomous_grant` from
   `lab_driver` / entrypoint. If the signature is wrong, BETA changes the library; GAMMA waits
   `[HANDOFF]`.
3. **`dispatch.py` — BETA only.** ALFA must not emit kernel events from a second writer; child
   `AuthorizationDenied` is appended through the existing kernel/event-sink already injected into
   `EpisodeEngine` (ALFA uses current `self._kernel` / sink APIs, no dispatch surgery).
4. **No lane edits `coding_coordinator.py` / `coding_plan.py`.** Scheduler stays; v0.6.0 extracts it.

```text
                    ALFA                         BETA                         GAMMA
              episode + root.py            L writer + grants           lab + CLI + VG text
                     │                            │                           │
                     │  EvaluationScheduler       │                           │
                     │◄──── stub Day 1 ───────────┤                           │
                     │                            │  create_autonomous_grant  │
                     │                            ├──────────────────────────►│
                     │  EpisodeStarted on L       │  listener consumes L      │
                     └────────────────────────────┼───────────────────────────┘
                                                  │
                         Joint merge: G-050 gates + contract/boundary/TCB
```

---

## 2. Dependency graph (start Day 1 in parallel)

```text
ALFA  A-01 span callback ──► A-02 spawn child_return ──► A-03 EpisodeStarted
         │                      │
         └── A-04 child deny event
         └── A-05 operator span labels
         └── A-06 EvaluationScheduler stub (unblocks BETA B-06)
         └── A-07 RegroundPolicy wire-or-delete
         └── A-08 format_skill_index in compiler

BETA  B-01 EVENT_KINDS closed ──► B-02 grant/budget events ──► B-03 ApprovalResolved on L
         │
         └── B-04 Heartbeat or ADR-defer
         └── B-05 grant shape goldens (X-07)
         └── B-06 EvaluationRequested listener (needs A-06)
         └── B-07 AutonomousGrant validate + BENCHMARK refuse
         └── B-08 AT-12 or defer ADR (text handed to GAMMA C-08)

GAMMA C-01 move _fake_backend ──► C-02 --in-place ──► C-03 bind grant (needs B-07)
         │
         └── C-04 live greenfield campaign (needs C-02, C-03, A-01)
         └── C-05 TableWorld register-or-cut
         └── C-06 README REJ-10 + stale paths
         └── C-07 CI-9 honest
         └── C-08 VG freeze (A-03, K-40, F-21a, LT, Trust, inbox)  [docs only]
```

**Critical path to tag:** `A-01 → A-02 → B-01 → B-03 → B-06 → C-02 → C-03 → C-04`.

---

## 3. Lane 1 — ALFA (Architecture & Orchestration)

**Owner prefix:** `[alfa]`  
**REQ on every PR:** `REQ-TRUST-001` (plus `REQ-CTX-001` on A-08)  
**Daily cadence:** focused unittest → boundaries → TCB (even if ALFA did not touch kernel).

### Shared ALFA verification (run before every push)

```bash
python3 -m unittest test.agency.test_spawn test.runtime.test_composition_root -v
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/scan_secrets.py
```

---

### S050-A-01 — Production justifying spans `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-CORE-001` · D-05 · G-050-01 |
| **Files** | `vanguard/packages/runtime/root.py` (`_admit_turn_result`); `test/runtime/test_composition_root.py`; new must-fail under `test/broken/` **or** composed test in `test/runtime/` |
| **Days** | 1–2 |

**Steps**

1. Read `EpisodeEngine` receipt_labeller contract (`engine.py` ~366): non-`None` return is concatenated onto `accumulated`.
2. Change `_admit_turn_result` to return a `Span` with trust class **not** OPERATOR (untrusted-external / tool-result class per `K-31`).
3. Keep approval-suspension → `None` (no fake observation).
4. Add composed test: after one privileged dispatch, next `EffectRequest.justifyingSpans` includes the tool-result span; widening from that span is denied (F-09 path).

**DoD:** `_admit_turn_result` no longer unconditionally `return None` after a real outcome.  
**Proof:**

```bash
python3 -m unittest test.runtime.test_composition_root test.kernel.test_provenance -v
```

---

### S050-A-02 — `spawn` → `child_return` `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-CORE-002` · D-06 · G-050-02 |
| **Files** | `vanguard/packages/agency/episode/engine.py` (`spawn` only); `test/agency/` spawn tests |
| **Days** | 2–3 |
| **Depends** | A-01 conceptually (spans exist); can start in parallel on `engine.py` |

**Steps**

1. After child `run()` returns, call `Accumulation.child_return` with child value spans; pass into subsequent parent turns / child construction as specified by `provenance.py`.
2. Do not trust child-reported success for parent privileged widening.
3. Test: parent kill mid-child does not invent success (`C-11`).

**Proof:**

```bash
python3 -m unittest discover -s test/agency -t . -p '*spawn*' -v
```

---

### S050-A-03 — Emit `EpisodeStarted` from packages `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-LED-002` · D-12 · G-050-03 |
| **Files** | `agency/episode/engine.py` **or** `runtime/root.py` (ALFA owns both); tests in `test/agency` / `test/runtime` |
| **Days** | 3 |

**Steps**

1. Append `EpisodeStarted` once per episode **before** the first proposal, using the same event sink the engine already has (do not invent a CLI fixture).
2. Idempotent on resume: do not double-start if the store already has it.

**Proof:** grep production emit; integration assert first lifecycle kind.

```bash
rg "EpisodeStarted" vanguard/packages/agency vanguard/packages/runtime
python3 -m unittest test.agency.test_episode_engine -v   # or the module you extend
```

---

### S050-A-04 — Child refuse records `AuthorizationDenied` `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-CORE-004` · D-08 |
| **Files** | `engine.py` (~336–355) |
| **Days** | 3–4 |

**Steps**

1. Keep sealed-scope refuse (do not move the check into kernel this sprint).
2. Append `AuthorizationDenied` via the engine’s existing event/kernel emit path (no `dispatch.py` edit).

**Proof:**

```bash
python3 -m unittest discover -s test/agency -t . -p '*spawn*' -v
```

---

### S050-A-05 — Source-class spans (no call-site `Trust.OPERATOR`) `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-CORE-003` · D-07 |
| **Files** | `runtime/root.py` (`_operator_span`) |
| **Days** | 4 |

**Steps**

1. Label brief vs model vs tool vs operator using provenance rules (`K-31`).
2. Grep `Trust.OPERATOR` in `root.py` — leftover must be justified in the PR.

**Proof:**

```bash
python3 -m unittest test.runtime.test_composition_root -v
rg "Trust.OPERATOR" vanguard/packages/runtime/root.py
```

---

### S050-A-06 — `EvaluationScheduler` stub (handoff to BETA) `[TODO] ❌`

| | |
|---|---|
| **Backlog** | Enables `TSK-EVAL-001` without BETA editing `root.py` |
| **Files** | `runtime/root.py`; optional `vanguard/packages/ports/` **only if** a new Protocol is required — prefer a `Callable` / small Protocol **in `runtime/`** to avoid ports churn |
| **Days** | 1 (land first) |

**Steps**

1. Replace `HarnessSession._evaluate()` as the *authority* with `self._on_terminal(run_ref)` injected at `compose()`.
2. Default no-op or existing RPC wrapped behind the callback so current tests keep passing until BETA lands B-06.
3. Do **not** import the evaluator from agency.

**DoD:** BETA can implement `evaluation_listener.py` and pass it in without touching `root.py` again.  
**Proof:** existing `test.runtime.test_composition_root` still green after stub.

---

### S050-A-07 — `RegroundPolicy` wire **or** delete `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-CTX-001` · D-10 |
| **Files** | `agency/context/regrounding.py`; `agency/episode/engine.py` |
| **Days** | 5–6 |

**Steps**

1. If wired: `shouldRun` triggers an **observation** effect through `Kernel.dispatch`, not a side channel (VG-03 loop).
2. If deleted: remove module + tests; note DEF in the PR for GAMMA C-08 to record in VG-03.

**Pick one in the PR title.** Do not leave dead code.

**Proof:**

```bash
rg "RegroundPolicy" vanguard/packages/agency
python3 -m unittest test.agency.test_regrounding -v
```

---

### S050-A-08 — Bind `format_skill_index` in `ContextCompiler` `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-CTX-002` · `REQ-CTX-001` |
| **Files** | `agency/context/compiler.py`; tests under `test/agency/` |
| **Days** | 6–7 |

**Steps**

1. Call `format_skill_index` when assembling L-layer skill prefix; honour pack ceiling (≤4k names+descriptions).
2. Do not import `coding_session` into domain further.

**Proof:**

```bash
python3 -m unittest discover -s test/agency -t . -p '*context*' -v
rg "format_skill_index" vanguard/packages/agency/context
```

---

### ALFA day board

| Day | Focus |
|---|---|
| 1 | A-06 stub + start A-01 |
| 2 | A-01 DoD |
| 3 | A-02 + A-03 |
| 4 | A-04 + A-05 |
| 5–6 | A-07 |
| 7 | A-08 |
| 8–9 | Integration with BETA listener; fix composed MF |
| 10 | Joint G-050-01…03, 08, 09 |

---

## 4. Lane 2 — BETA (Security, Progress & Verification)

**Owner prefix:** `[beta]`  
**REQ on every PR:** `REQ-TRUST-001` and/or `REQ-LEDGER-002`  
**Progress fingerprints:** durable `EffectStarted` / `EffectCompleted` / `EffectReconciled` already emit. This lane **completes the trail** (grants, budgets, approvals, evaluation request) so a fingerprint is reconstructible from \(L\) alone — not a second progress DB, not `coding_progress.py` (v0.6).

### Shared BETA verification

```bash
python3 -m unittest test.kernel.test_dispatch test.runtime.test_autonomous_coding_grant -v
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/run_active_contract_tests.py
```

Kernel edits must not grow TCB without ADR. Prefer **emit-only** changes in `dispatch.py`.

---

### S050-B-01 — Close `EVENT_KINDS` `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-LED-001` · D-11 |
| **Files** | `domain/ledger/events.py`; writer validation (store or envelope parse) |
| **Days** | 1–2 |

**Steps**

1. Add `EffectRejected`, `KernelAlarm` to the frozenset.
2. Reject unknown `payload.kind` at append (fail closed).
3. Update property tests that generate random kinds.

**Proof:**

```bash
python3 -m unittest test.test_ledger_properties test.contracts.t3_ledger -v
```

---

### S050-B-02 — Emit grant/budget events **or** shrink the set `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-LED-005` · D-15 |
| **Files** | `kernel/dispatch.py` S6/S7/S10; optionally `kernel/grants.py` revoke caller |
| **Days** | 2–4 |

**Default:** emit `CapabilityGranted`, `BudgetReserved`, `BudgetCommitted`.  
**Alternative:** ADR + remove kinds (GAMMA records ADR in C-08). Pick **emit** unless TCB/noise is measured worse.

If `GrantIssuer.revoke` stays public, add one production caller or delete the API (`K-49`).

**Proof:**

```bash
python3 -m unittest test.kernel.test_dispatch -v
python3 tools/check_tcb_budget.py
```

---

### S050-B-03 — `ApprovalResolved` on the ledger `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-LED-003` · D-13 · X-15 · G-050-04 · `TSK-FE-J4` (digest population if challenge is emitted here) |
| **Files** | `runtime/service/service.py` (`_cmd_ResolveApproval`); governance helpers |
| **Days** | 3–5 |

**Steps**

1. After queue.put, append `ApprovalResolved` with the same decision fields.
2. Keep in-process queue for the live waiter **and** make `ProcessEngine` replayable from store.
3. Do not succeed on empty challenge digests (J4).

**Proof:** store-only replay test (no queue).

```bash
python3 -m unittest discover -s test/runtime -t . -p '*approv*' -v
```

---

### S050-B-04 — Heartbeat producer **or** explicit defer `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-LED-004` · D-14 |
| **Files** | recovery producer **or** ADR text handed to GAMMA |
| **Days** | 5 |

Ship **one**: HMAC heartbeat from a live run, **or** ADR “T-08 deferred; scanner remains consumer-only”. Silent status-quo is not DoD.

**Proof:** recovery unittest **or** ADR id in C-08.

---

### S050-B-05 — One grant shape (goldens) `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-SPEC-008` (code half) · X-07 · G-050-12 |
| **Files** | `kernel/grants.py` + existing translator; `test/contracts/` goldens. **Not** VG markdown (GAMMA). |
| **Days** | 6 |

**Steps:** translator with RFC 8785 JCS goldens **or** unify fields. Do not invent a third grant type.

**Proof:**

```bash
python3 -m unittest discover -s test/contracts -t . -p '*grant*' -v
python3 tools/run_active_contract_tests.py
```

---

### S050-B-06 — Ledger-owned `EvaluationRequested` `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-EVAL-001` · D-02 · G-050-05 |
| **Files** | **new** `runtime/evaluation_listener.py`; tests `test/runtime/test_evaluation_listener.py`; evaluator transport in `adapters/evaluators/**` if needed |
| **Depends** | A-06 |
| **Days** | 6–8 |

**Steps**

1. Listener observes `EpisodeCompleted` (and documented terminals) on \(L\), appends `EvaluationRequested`, then RPC to UID 10002 daemon.
2. Worker still must not import evaluator (`A-05`).
3. If process-kill cannot schedule eval this sprint: compensating ADR + test that documents it — still emit the event when the listener is alive.

**Proof:**

```bash
rg "EvaluationRequested" vanguard/packages
python3 -m unittest test.runtime.test_evaluation_listener test.test_spine -v
```

---

### S050-B-07 — `AutonomousGrant` product semantics `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-HAR-002` (library half) · G-050-07 |
| **Files** | `runtime/autonomous_grant.py`; `test/runtime/test_autonomous_coding_grant.py`; `test/runtime/test_anticheat.py` if needed |
| **Days** | 4–7 (parallel with B-03) |

**Steps**

1. Validate workspace digest, verb set, command allowlist, budget, expiry.
2. **BENCHMARK cannot mint** a grant; INTERACTIVE only.
3. Export a stable `create_autonomous_grant` / `validate_grant_request` GAMMA can call. No `lab_driver.py` edits.

**Proof:**

```bash
python3 -m unittest test.runtime.test_autonomous_coding_grant test.runtime.test_anticheat -v
```

---

### S050-B-08 — AT-12 **or** defer with compensating control `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-SEC-001` · D-33 |
| **Files** | new architecture/must-fail test under `test/` **or** ADR draft for GAMMA C-08 |
| **Days** | 8–9 |

Unreadability probe already exists (`TSK-EVAL-002` DONE). AT-12 is “capability ↛ verifier path”. Prefer a failing-closed test over a novel kernel.

**Proof:** new test module **or** ADR-00xx in the joint freeze.

---

### BETA day board

| Day | Focus |
|---|---|
| 1–2 | B-01 |
| 2–4 | B-02 + B-07 |
| 3–5 | B-03 |
| 5 | B-04 decision |
| 6 | B-05; start B-06 when A-06 merged |
| 7–8 | B-06 |
| 9 | B-08 |
| 10 | Joint G-050-04, 05, 07, 12 |

---

## 5. Lane 3 — GAMMA (Product CLI & Live Proof)

**Owner prefix:** `[gamma]`  
**REQ on every PR:** `REQ-TRUST-001` · `REQ-HAR-001`  
**Spend:** do not commit keys. Paid models stay fail-closed until S9-J-03 (`TSK-HAR-005`) — human/ops, not a code lane. Campaign uses free-band or pre-authorised spend.

### Shared GAMMA verification

```bash
python3 -m unittest discover -s test/runtime -t . -p '*lab*' -v
python3 -m unittest discover -s test/runtime -t . -p '*entrypoint*' -v
python3 tools/check_boundaries.py
python3 tools/scan_secrets.py
```

---

### S050-C-01 — Relocate `_fake_backend` `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-CLI-001` |
| **Files** | `runtime/coding_entrypoint.py`; `test/` destination module |
| **Days** | 1–2 |

**Steps**

1. Move `_fake_backend` + scripted plan helpers to `test/`.
2. Production refuses `fakeBackend` unless `VANGUARD_ALLOW_FAKE=1`.
3. Keep entrypoint as a non-dispatching bridge (`TSK-CLI-002` already DONE).

**Proof:**

```bash
rg "_fake_backend" vanguard/packages/runtime/coding_entrypoint.py   # must be empty
python3 -m unittest discover -s test -t . -p '*coding_entrypoint*' -v
```

---

### S050-C-02 — `--in-place` operator writes `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-HAR-001` · G-050-06 |
| **Files** | `runtime/lab_driver.py`; tests under `test/runtime/` / `test/lab/` |
| **Days** | 2–5 |

**Steps**

1. Keep isolated copy as **default** for measurement (current comment at isolate copy).
2. Add explicit `--in-place` / `isolate=False` that mutates the given workspace; record `labDepartures`.
3. BENCHMARK + in-place privileged write still needs approver or grant (I-04).

**Proof:** unittest with a temp workspace: file exists after run when in-place; isolated mode does not dirty the source fixture.

```bash
python3 -m unittest discover -s test -t . -p '*lab_driver*' -v
```

---

### S050-C-03 — Bind `AutonomousGrant` on INTERACTIVE in-place `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-HAR-002` (CLI/lab half) · G-050-07 |
| **Files** | `lab_driver.py`, `coding_entrypoint.py` only |
| **Depends** | B-07 |
| **Days** | 5–7 |

**Steps**

1. INTERACTIVE + in-place → `create_autonomous_grant(...)`; deny writes outside selector/allowlist.
2. BENCHMARK path must not call mint.

**Proof:** integration test using BETA’s validators.

---

### S050-C-04 — Live greenfield acceptance `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-HAR-004` · S8-J-03 · G-050-06 |
| **Files** | `lab/tasks/`; `tools/run_v0450_greenfield_campaign.py`; evidence under `docs/scrum/sprints/` (this sprint folder) |
| **Depends** | C-01, C-02, C-03, A-01 (honest session) |
| **Days** | 7–10 |

**Steps**

1. One `lab/tasks/greenfield-*` task, live model, `live: true`, no gold patches, no `_fake_backend`.
2. Tests RED→GREEN via `proc.exec`; files on disk.
3. Write a dated receipt (outcome, model id, grant id, **not** raw secrets).

**MOCK/`--live` false does not close this row.** If the provider is unavailable, status is `[BLOCKED]` with `instrument_error:*`, never a pass.

**Proof (shape):**

```bash
python3 tools/run_v0450_greenfield_campaign.py --live --in-place ...   # exact flags as implemented
# evidence file committed without API keys
```

---

### S050-C-05 — `vg-table-default` register **or** delete `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-HAR-007` · D-27 |
| **Files** | pack + kinds/registry **or** delete pack + test retarget |
| **Days** | 6–8 (parallel, not on live critical path) |

Do not leave an orphan pack. Implementing a full TableWorld `EnvironmentAdapter` is **v0.6** (`TSK-EPIC-060-004`); this sprint only **register or cut**.

**Proof:** `rg vg-table-default` in registry **xor** pack gone.

---

### S050-C-06 — README hygiene `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-DOC-001` · `TSK-DOC-002` · D-46 · D-47 |
| **Files** | `README.md` |
| **Days** | 8 |

Delete LEVEL 0–9; fix stale paths (`coordination.py`, `sqlite_event.py`, `fs_blob.py`).

**Proof:**

```bash
rg "LEVEL 0|coordination.py|sqlite_event.py|fs_blob.py" README.md   # empty
```

---

### S050-C-07 — Honest `CI-9` / MF bijection `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-TEST-001` · D-44 · G-050-10 |
| **Files** | `tools/rule_test_map.py`; VG-08 note in `docs/main_v4/` |
| **Days** | 8–9 |

Gate must **fail** on gaps, or the map must be the live `MF-KRN-*` / `MF-S0-*` roster with gaps=0.

**Proof:**

```bash
python3 tools/rule_test_map.py ; echo exit:$?
python3 tools/run_broken_tests.py
```

---

### S050-C-08 — VG spec freeze (docs only) `[TODO] ❌`

| | |
|---|---|
| **Backlog** | `TSK-SPEC-001`…`010`, `TSK-DOC-003`, `TSK-LED-009` (ADR if split blob ports kept), `TSK-SEC-002` (seccomp defer ADR) |
| **Files** | `docs/main_v4/02_*.md` `03_*.md` `04_*.md` `05_*.md` `09_*.md` (decision register) |
| **Days** | 8–10 |
| **Depends** | Code PRs merged enough to cite SHAs |

**Patch list (do not rewrite THEORY):**

1. `A-03` / VG-05 §2.1 → ADR-0051 sink classes (`TSK-SPEC-001`, `TSK-SPEC-009`).
2. `LT-*` includes `runtime/governance/` (`TSK-SPEC-002`).
3. `K-40` inverted: separate evaluator identity (`TSK-SPEC-003`).
4. Alarms F-21a + F-24 (`TSK-SPEC-004`).
5. Ports + `ProposalTranslator` (`TSK-SPEC-005`).
6. Inbox/outbox ADR-0062 (`TSK-SPEC-006`).
7. `Trust` five-value freeze (`TSK-SPEC-007`).
8. Reservation four-vector (`TSK-SPEC-010`).
9. `cryptography` on K-02 list (`TSK-DOC-003`).
10. CT-18/19 split-ports ADR **or** implement — default ADR (`TSK-LED-009`).
11. Seccomp/rlimits: ADR defer (`TSK-SEC-002`).
12. Grant-shape: point at BETA goldens (`TSK-SPEC-008`).

**Do not** edit `SYSTEM_SPEC_THEORY.md` except a one-line pointer if required; THEORY stays the intent snapshot.

**Proof:** `rg` for obsolete “every effect needs a grant” / “F-24 only alarm” / “evaluator same bwrap” is empty in the patched VG files.

---

### GAMMA day board

| Day | Focus |
|---|---|
| 1–2 | C-01 |
| 2–5 | C-02 |
| 5–7 | C-03 (after B-07) |
| 6–8 | C-05 parallel |
| 7–10 | C-04 live (may `[BLOCKED]` on keys) |
| 8 | C-06 |
| 8–9 | C-07 |
| 8–10 | C-08 |

---

## 6. Joint track (all lanes + Tech Lead)

Not a fourth write-scope for packages. Merge and gates only.

| ID | When | What |
|---|---|---|
| S050-J-01 | Day 1 | Branch `feat/v050-empirical-baseline`; freeze this board |
| S050-J-02 | Day 3 | Integrate A-06 + B-01 so kinds exist before EpisodeStarted floods unknown-kind |
| S050-J-03 | Day 8 | Contract + boundary + TCB on integration SHA |
| S050-J-04 | Day 10 | G-050 checklist (below); no tag if C-04 is MOCK-only |

### Integration verification (Joint, Day 8 and Day 10)

```bash
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/scan_secrets.py
python3 tools/run_active_contract_tests.py
python3 tools/run_broken_tests.py
python3 -m unittest discover -s test/kernel -t . -q
python3 -m unittest discover -s test/agency -t . -q
python3 -m unittest discover -s test/runtime -t . -q
```

Full suite is **informative** (repo may be red at baseline — `AGENTS.md` / CLAUDE.md). Do **not** treat a pre-existing red as this sprint’s regression without a before/after on the modules above.

### PR rules (`AGENTS.md`)

- Prefix: `fix(kernel):`, `fix(agency):`, `feat(runtime):`, `docs:`, `cleanup:`.
- Body cites **at least one** of `REQ-TRUST-001`, `REQ-CTX-001`, `REQ-HAR-001`, `REQ-LEDGER-002`.
- No credentials, no live model dumps with secrets.
- Capability/evaluator/approval diffs need the security tests named in the lane DoD.

---

## 7. Gate map — sprint DoD vs backlog

| Gate | Lane evidence | Backlog |
|---|---|---|
| G-050-01 spans | A-01 | TSK-CORE-001 |
| G-050-02 child provenance | A-02 | TSK-CORE-002 |
| G-050-03 EpisodeStarted | A-03 | TSK-LED-002 |
| G-050-04 ApprovalResolved | B-03 | TSK-LED-003 |
| G-050-05 EvaluationRequested | A-06 + B-06 | TSK-EVAL-001 |
| G-050-06 live in-place greenfield | C-02 + C-04 | TSK-HAR-001, TSK-HAR-004 |
| G-050-07 grant bound | B-07 + C-03 | TSK-HAR-002 |
| G-050-08 TCB | every kernel PR | TSK-CORE-009 (keep) |
| G-050-09 lattice | every PR | TSK-SPEC-011 (keep) |
| G-050-10 CI-9 | C-07 | TSK-TEST-001 |
| G-050-11 spec freeze | C-08 | TSK-SPEC-001… |
| G-050-12 grant shape | B-05 + C-08 | TSK-SPEC-008 |

**Out of this sprint’s merge bar (tracked, not blocking the tag if ADR’d):** Heartbeat (B-04 defer), AT-12 (B-08 defer), TableWorld adapter (C-05 cut vs v0.6), spend key rotation (`TSK-HAR-005`, human), FE-3-3…3-7 / J1–J3 (Interaction plane).

---

## 8. What “done” looks like for a developer day

1. Stay inside the write-scope table.  
2. Implement the **next** `[TODO]` row on your day board.  
3. Run the lane’s shared commands + the row’s Proof.  
4. Push a PR with `[alfa]`/`[beta]`/`[gamma]` in the title and a `REQ-*`.  
5. Do not start a v0.6 epic because a file “looked adjacent.”

---

*End of SPRINT-050-ACTIVE. Next horizon (v0.6 hexagonal waist) opens only after G-050-01…07 are green on a tagged SHA, including one un-mocked in-place `oracle_green`.*
