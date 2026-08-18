---
id: ROAD-BACK-01
file: docs/02_roadmap/backlog.md
title: "Vanguard / GTS — Single-Source-of-Truth Technical Backlog"
version: 1.0.0
status: AUTHORITATIVE-TASK-POOL
owners: [Project Lead, Tech Lead]
last_reviewed: 2026-08-18
baseline: "v0.4.5-beta as-built; milestones ROAD-MILE-01; drifts D-01…D-48"
corpus_note: >
  docs/01_specs/ is not present in this workspace. Backend VG corpus is docs/main_v4/;
  frontend short files are docs/front_v4/ plus docs/scrum/roadmap_frontend.md.
---

# Technical backlog (SSOT)

This file is the **only task pool** for programme work derived from `docs/02_roadmap/milestones.md`,
`SYSTEM_SPEC_DRIFTS.md`, `SYSTEM_SPEC_ASBUILT.md`, and the frontend board. Living sprint boards
(`docs/scrum/roadmap_backend.md`, `roadmap_frontend.md`) remain the *execution* boards; when they
disagree with **status here**, this file wins until a Tech Lead edits it.

**Parser contract.** Every task is a Markdown heading `### TSK-…` followed by a field table. IDs are
permanent; never reuse. Status is exactly `[TODO] ❌` or `[DONE] ✅`.

**Done rule.** `[DONE] ✅` only if the behaviour exists in production wiring **and** a named test or
must-fail in `vanguard/packages/`, `test/`, `vanguard/clients/`, or (GUI) `vanguard-gui/` typecheck
DoD already covers it. Library-without-call-site is `[TODO] ❌`.

**v0.5.0 backend gate.** Frontend rows are in this pool because Prompt 2 requires them. They are
**not** G-050 backend exit criteria (`milestones.md` I-06 / §8).

| Bucket | TODO | DONE |
|---|---|---|
| Kernel / provenance / dispatch honesty | 6 | 5 |
| Ledger / events / recovery | 8 | 3 |
| Evaluation trigger | 1 | 1 |
| Spec freeze (OPTIMIZATION → VG text) | 10 | 0 |
| Product / live coding cell | 6 | 2 |
| Context / skills / hygiene | 4 | 2 |
| Perimeter / AT / ADR | 4 | 2 |
| Tests / IDs / docs | 5 | 2 |
| Frontend FE-2 / FE-3 / J-seams | 8 | 6 |
| v0.6.0+ epics | 18 | 0 |
| **Total** | **70** | **23** |

---

## 0. Field schema

| Field | Meaning |
|---|---|
| **ID** | Permanent `TSK-{CORE\|LED\|EVAL\|SPEC\|HAR\|CLI\|CTX\|SEC\|DOC\|TEST\|FE\|EPIC}-NNN` |
| **Title** | Imperative, one line |
| **Path** | Owning tree |
| **Milestone** | `v0.5.0` … `v1.0.0` |
| **REQ** | Requirement anchor (`REQ-*` or VG/K/D id if no REQ yet) |
| **Status** | `[TODO] ❌` \| `[DONE] ✅` |
| **Drift** | `D-nn` / `X-nn` / FE id / milestone gate |
| **Proof** | Exact command or test module |

---

## 1. v0.5.0 — Wave S-truth (provenance & composition)

### TSK-CORE-001 — Wire justifying spans in production composition

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/root.py` (`_admit_turn_result`) |
| Milestone | v0.5.0 |
| REQ | `[REQ-TRUST-001]` · `K-33` · `S1(e)` |
| Status | `[TODO] ❌` |
| Drift | D-05 |
| Description | Today `_admit_turn_result` notes text and **returns `None`**, so `EpisodeEngine` never accumulates tool-result spans (`engine.py` only adds a label if the callback returns one). Return an `UNTRUSTED_EXTERNAL` `Span` (or equivalent) so F-09 / authority widening is reachable in **composed** `HarnessSession`, not only kernel fixtures. |
| Proof | `python3 -m unittest test.runtime.test_composition_root test.kernel.test_provenance -v` plus a new composed must-fail: privileged widen from a tool-result span is denied. `MF-KRN-002` against `HarnessSession` (not a bare `Kernel`). |

### TSK-CORE-002 — `spawn()` must call `Accumulation.child_return`

| Field | Value |
|---|---|
| Path | `vanguard/packages/agency/episode/engine.py` (`spawn`) |
| Milestone | v0.5.0 |
| REQ | `[REQ-TRUST-001]` · `K-33` |
| Status | `[TODO] ❌` |
| Drift | D-06 |
| Description | `child_return` exists on `kernel/provenance.py` and has **zero** call sites in `engine.py`. Child `run()` must receive untrusted-derived spans from the parent return value. |
| Proof | `python3 -m unittest test.agency.test_spawn -v` (extend): child accumulation includes parent tool spans; kill-parent mid-child does not invent success. |

### TSK-CORE-003 — Stop hard-coding `_operator_span` as `Trust.OPERATOR`

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/root.py` (~1210) |
| Milestone | v0.5.0 |
| REQ | `K-31` |
| Status | `[TODO] ❌` |
| Drift | D-07 |
| Description | Replace literal `Span("brief-1", Trust.OPERATOR, …)` with source-class labelling from the actual content class. Call sites must not mint OPERATOR trust. |
| Proof | Unit test: untrusted / tool / model spans are not labelled OPERATOR; grep `Trust.OPERATOR` in `root.py` is empty or justified. |

### TSK-CORE-004 — Emit `AuthorizationDenied` from attenuated-child refuse

| Field | Value |
|---|---|
| Path | `vanguard/packages/agency/episode/engine.py` (~336–355) |
| Milestone | v0.5.0 |
| REQ | `[REQ-LEDGER-002]` · ADR-0067 |
| Status | `[TODO] ❌` |
| Drift | D-08 |
| Description | Keep the engine-side refuse (sealed-scope complement). Append `AuthorizationDenied` so the ledger, not only a local `Turn`, records the denial. |
| Proof | `python3 -m unittest test.agency.test_spawn -v`: child out-of-scope verb produces `AuthorizationDenied` in the store. |

### TSK-CORE-005 — Dispatch S0–S12 remains the only privileged path

| Field | Value |
|---|---|
| Path | `vanguard/packages/kernel/dispatch.py` |
| Milestone | v0.5.0 (keep) |
| REQ | `[REQ-KRN-014]` · `AT-01` |
| Status | `[DONE] ✅` |
| Drift | D-01 `[OPTIMIZATION]` |
| Description | Ordered S1–S12; S0 built in `EpisodeEngine._to_effect_request`. Do not add a second effect path. |
| Proof | `python3 -m unittest test.kernel.test_dispatch -v`; `python3 tools/check_boundaries.py` |

### TSK-CORE-006 — Evaluate stays outside the worker loop

| Field | Value |
|---|---|
| Path | `vanguard/packages/agency/episode/`; `test/test_spine.py` |
| Milestone | v0.5.0 (keep) |
| REQ | `A-12` |
| Status | `[DONE] ✅` |
| Drift | D-03 `[OPTIMIZATION]` |
| Description | Episode loop does not grade itself. Remaining work is trigger ownership (`TSK-EVAL-001`). |
| Proof | `python3 -m unittest test.test_spine -v` |

### TSK-CORE-007 — Sink-class mediation (grants only for `PRIVILEGED`)

| Field | Value |
|---|---|
| Path | `vanguard/packages/kernel/classifier.py`, `dispatch.py` |
| Milestone | v0.5.0 (keep code; spec is TSK-SPEC-001) |
| REQ | ADR-0051 |
| Status | `[DONE] ✅` |
| Drift | D-04 `[OPTIMIZATION]` |
| Description | All three sink classes still traverse dispatch; only privileged take S6. **Not** a kernel bypass. |
| Proof | `python3 -m unittest test.kernel.test_dispatch test.kernel.test_classifier -v` |

### TSK-CORE-008 — Provenance library freeze (do not rewrite)

| Field | Value |
|---|---|
| Path | `vanguard/packages/kernel/provenance.py` |
| Milestone | v0.5.0 (keep) |
| REQ | `K-33` |
| Status | `[DONE] ✅` |
| Drift | D-05 (library half) |
| Description | `Accumulation.child_return` and span algebra are correct. Wiring is TSK-CORE-001/002. |
| Proof | `python3 -m unittest test.kernel.test_provenance -v` |

### TSK-CORE-009 — TCB budget tripwire

| Field | Value |
|---|---|
| Path | `tools/check_tcb_budget.py`; `vanguard/packages/kernel/` |
| Milestone | v0.5.0 (keep) |
| REQ | ADR-0054 · `C-07` |
| Status | `[DONE] ✅` |
| Drift | — |
| Description | Kernel ≤ 1438 logical LOC (as-built 1333). Growth requires ADR. |
| Proof | `python3 tools/check_tcb_budget.py` |

---

## 2. v0.5.0 — Wave S-truth (ledger writer)

### TSK-LED-001 — Enforce `EVENT_KINDS` at the writer; admit extras

| Field | Value |
|---|---|
| Path | `vanguard/packages/domain/ledger/events.py`; kernel/runtime emit sites |
| Milestone | v0.5.0 |
| REQ | VG-04 §12.2 |
| Status | `[TODO] ❌` |
| Drift | D-11 |
| Description | Add `EffectRejected` and `KernelAlarm` to `EVENT_KINDS`. Reject unknown `payload.kind` on append. |
| Proof | Writer unit test: unknown kind fails; `KernelAlarm` / `EffectRejected` accepted. `python3 -m unittest test.test_ledger_properties -v` |

### TSK-LED-002 — Emit `EpisodeStarted` from packages

| Field | Value |
|---|---|
| Path | `vanguard/packages/agency/episode/` or `runtime/root.py` |
| Milestone | v0.5.0 |
| REQ | VG-04 lifecycle |
| Status | `[TODO] ❌` |
| Drift | D-12 |
| Description | First durable event of a run must be written by the backend, not CLI fixtures. |
| Proof | Integration: after `HarnessSession.run` start, store contains `EpisodeStarted`. Grep production emit (exclude `test/`). |

### TSK-LED-003 — Persist `ApprovalResolved` on the ledger

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/service/service.py` (`_cmd_ResolveApproval`) |
| Milestone | v0.5.0 |
| REQ | `[REQ-LEDGER-002]` · X-15 |
| Status | `[TODO] ❌` |
| Drift | D-13 |
| Description | Today the command only `queue.put(decision)`. `ProcessEngine` already *consumes* `ApprovalResolved`. Append the event so replay does not require the in-process queue. |
| Proof | Kill process after submit; resume from SQLite only; approval still resolves. |

### TSK-LED-004 — Produce authenticated `Heartbeat` (or cut T-08 by ADR)

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/ledger/recovery.py` producer side |
| Milestone | v0.5.0 |
| REQ | T-08 |
| Status | `[TODO] ❌` |
| Drift | D-14 |
| Description | Scanner already consumes `Heartbeat`. Either emit HMAC-authenticated heartbeats from a live run, or ADR-defer T-08 and stop claiming recovery-from-outside. |
| Proof | If kept: recovery test with heartbeats only. If deferred: ADR id in VG-05 + this task moved to `[DONE]` as “explicitly out”. Until then TODO. |

### TSK-LED-005 — Emit grant and budget kinds (or shrink the minimum set)

| Field | Value |
|---|---|
| Path | `vanguard/packages/kernel/dispatch.py` S6/S7/S10 |
| Milestone | v0.5.0 |
| REQ | VG-04 authorisation group |
| Status | `[TODO] ❌` |
| Drift | D-15 |
| Description | Emit `CapabilityGranted` at S6 and `BudgetReserved`/`BudgetCommitted` around S7/S10, **or** remove those kinds from the minimum set by ADR. `GrantIssuer.revoke` has no production caller (`K-49`) — call it or drop the API. |
| Proof | Dispatch test asserts events; or ADR + `EVENT_KINDS` shrink + this file updated. |

### TSK-LED-006 — SQLite WAL + JSONL export

| Field | Value |
|---|---|
| Path | `vanguard/packages/adapters/stores/` |
| Milestone | v0.5.0 (keep) |
| REQ | `CT-40` / `CT-42` · ADR-0010 |
| Status | `[DONE] ✅` |
| Drift | D-16 `[OPTIMIZATION]` |
| Description | WAL + FULL sync; JSONL is export. Keep. |
| Proof | `python3 -m unittest test.adapters.test_sqlite_store -v` (or current store test module) |

### TSK-LED-007 — Inbox/outbox sequence store

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/service/inbox.py` |
| Milestone | v0.5.0 (keep; spec TSK-SPEC-006) |
| REQ | ADR-0062 |
| Status | `[DONE] ✅` |
| Drift | D-17 `[OPTIMIZATION]` |
| Description | Idempotent commands. Keep. |
| Proof | `python3 -m unittest discover -s test/runtime -t . -p '*inbox*'` |

### TSK-LED-008 — Keep `KernelAlarm` on F-21a

| Field | Value |
|---|---|
| Path | `vanguard/packages/kernel/dispatch.py` (intent_append_failed) |
| Milestone | v0.5.0 (keep code; spec TSK-SPEC-004) |
| REQ | `K-47` |
| Status | `[DONE] ✅` |
| Drift | D-18 `[OPTIMIZATION]` |
| Description | F-21a is intent-append failed, not interrupted VERIFY. Do not drop the alarm. |
| Proof | `python3 -m unittest test.kernel.test_dispatch -v` |

### TSK-LED-009 — Blob+event atomicity / encryption ADR

| Field | Value |
|---|---|
| Path | `docs/main_v4/` ADR; blob + event ports |
| Milestone | v0.5.0 |
| REQ | `CT-18` · `CT-19` |
| Status | `[TODO] ❌` |
| Drift | D-19 |
| Description | Two independent ports today. Either implement atomic commit + classification-keyed encryption, or write an ADR that Phase 0 keeps split ports. |
| Proof | New ADR file + VG-04 sentence, **or** failing test that currently cannot pass until implemented. |

---

## 3. v0.5.0 — Wave S-eval

### TSK-EVAL-001 — Ledger-owned `EvaluationRequested`

| Field | Value |
|---|---|
| Path | Evidence listener; `vanguard/packages/runtime/root.py` (`HarnessSession._evaluate`) |
| Milestone | v0.5.0 |
| REQ | VG-05 `Principal::EvidencePlane` · ADR-0061 |
| Status | `[TODO] ❌` |
| Drift | D-02 |
| Description | `EvaluationRequested` is declared and **never emitted**. `_evaluate()` RPC after episode return is the trigger. Introduce a ledger listener (same UID 10002 evaluator) that emits `EvaluationRequested` on terminal episode events. Worker must not be the sole authority to start evaluation. Keep evaluator **outside** worker bwrap (D-32). |
| Proof | Grep: `EvaluationRequested` emitted from `vanguard/packages/`. Test: episode cannot import evaluator (`test_spine`); killing session still schedules eval **or** compensating ADR named in the test docstring. |

### TSK-EVAL-002 — Isolated evaluator + unreadability probe

| Field | Value |
|---|---|
| Path | `vanguard/packages/adapters/evaluators/isolated.py` |
| Milestone | v0.5.0 (keep) |
| REQ | `V-09` · `A-05` |
| Status | `[DONE] ✅` |
| Drift | D-32 `[OPTIMIZATION]` (code) |
| Description | Separate identity; do not restore K-40 “same perimeter”. Spec text is TSK-SPEC-003. |
| Proof | `python3 -m unittest test.adapters.test_isolated_evaluator -v` (or current isolated tests) |

---

## 4. v0.5.0 — Wave S-spec (amend VG to kept ADRs)

All `[TODO] ❌` until the VG markdown in `docs/main_v4/` (canonical; `docs/01_specs/` absent here) actually changes. Do **not** rewrite `SYSTEM_SPEC_THEORY.md` as the spec.

### TSK-SPEC-001 — Amend `A-03` / VG-05 §2.1 to ADR-0051

| Field | Value |
|---|---|
| Path | `docs/main_v4/02_*.md`, `05_*.md` |
| Milestone | v0.5.0 |
| REQ | X-01 · D-04 |
| Status | `[TODO] ❌` |
| Description | Grants for `PRIVILEGED` only; all classes still recorded via dispatch. |
| Proof | `rg "every single effect" docs/main_v4/05_*` empty; A-03 matches sink classes. |

### TSK-SPEC-002 — Put `runtime/governance/` in VG-03 `LT-*`

| Field | Value |
|---|---|
| Path | `docs/main_v4/03_*.md` |
| Milestone | v0.5.0 |
| REQ | X-03 · D-25 |
| Status | `[TODO] ❌` |
| Description | Lattice matches `check_boundaries.py` (governance area + evaluator import ban). |
| Proof | VG-03 LT list includes governance; `python3 tools/check_boundaries.py` |

### TSK-SPEC-003 — Rewrite `K-40` (evaluator separate identity)

| Field | Value |
|---|---|
| Path | `docs/main_v4/05_*.md` |
| Milestone | v0.5.0 |
| REQ | D-32 |
| Status | `[TODO] ❌` |
| Description | Worker must not read evaluator; UID 10002. Do not put judge in candidate bwrap. |
| Proof | K-40 paragraph matches as-built daemon. |

### TSK-SPEC-004 — Alarm set includes F-21a and F-24

| Field | Value |
|---|---|
| Path | `docs/main_v4/05_*.md` |
| Milestone | v0.5.0 |
| REQ | D-18 |
| Status | `[TODO] ❌` |
| Description | Delete “F-24 is the only kernel alarm”. |
| Proof | `rg "only kernel alarm" docs/main_v4` empty. |

### TSK-SPEC-005 — Freeze port roster and `ProposalTranslator`

| Field | Value |
|---|---|
| Path | `docs/main_v4/03_*.md`, `04_*.md` |
| Milestone | v0.5.0 |
| REQ | D-20 · D-28 · X-09 |
| Status | `[TODO] ❌` |
| Description | As-built ports; schema-driven translator + `aliases.json` as the model waist. |
| Proof | VG-04 names `invocation.py` / aliases; no second verb table. |

### TSK-SPEC-006 — Specify inbox/outbox ADR-0062 in VG-03/04

| Field | Value |
|---|---|
| Path | `docs/main_v4/03_*.md`, `04_*.md` |
| Milestone | v0.5.0 |
| REQ | D-17 |
| Status | `[TODO] ❌` |
| Description | Second sequence store is normative, not a secret. |
| Proof | Section exists; links ADR-0062. |

### TSK-SPEC-007 — Freeze `Trust` five-value enum (X-05)

| Field | Value |
|---|---|
| Path | `docs/main_v4/04_*.md` |
| Milestone | v0.5.0 |
| REQ | X-05 · Y-01 |
| Status | `[TODO] ❌` |
| Description | One Trust enum + envelope confidentiality. |
| Proof | VG-04 matches `domain` enum; no sixth undocumented axis. |

### TSK-SPEC-008 — One grant shape (kernel vs wire)

| Field | Value |
|---|---|
| Path | `vanguard/packages/kernel/grants.py`; wire schema; `docs/main_v4/04_*.md` |
| Milestone | v0.5.0 |
| REQ | X-07 |
| Status | `[TODO] ❌` |
| Description | Unify actions+resources+purposeDigest vs actions+singular selector, or specify the translator with golden vectors. |
| Proof | Golden JCS fixtures both sides; `python3 -m unittest` on grant parse. |

### TSK-SPEC-009 — `observe(..., grant=None)` matches ADR-0051 in VG

| Field | Value |
|---|---|
| Path | `docs/main_v4/05_*.md` |
| Milestone | v0.5.0 |
| REQ | X-02 |
| Status | `[TODO] ❌` |
| Description | Observation path documented as dispatch-without-S6, not “direct adapter”. |
| Proof | Spec sentence + existing observe tests still green. |

### TSK-SPEC-010 — Four-dimension `Reservation` freeze (X-14)

| Field | Value |
|---|---|
| Path | `docs/main_v4/04_*.md` |
| Milestone | v0.5.0 |
| REQ | D-24 · X-14 |
| Status | `[TODO] ❌` |
| Description | Document turns/depth as engine constraints, not silent sixth/seventh budget dims. |
| Proof | VG-04 vector = `{usd_micros, millis, tokens, bytes_}`. |

### TSK-SPEC-011 — Closed package set already stricter than VG-03

| Field | Value |
|---|---|
| Path | `tools/check_boundaries.py` |
| Milestone | v0.5.0 (keep) |
| REQ | D-25 |
| Status | `[DONE] ✅` |
| Description | Enforcer exists. Text catch-up is TSK-SPEC-002. |
| Proof | `python3 tools/check_boundaries.py` |

---

## 5. v0.5.0 — Wave S-product (live coding cell)

### TSK-HAR-001 — Live `--in-place` writes (not isolated copy)

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/lab_driver.py`; CLI product entry |
| Milestone | v0.5.0 |
| REQ | `[REQ-HAR-001]` · G-050-06 |
| Status | `[TODO] ❌` |
| Drift | Board Q2; `lab_driver` copies workspace when `isolate` |
| Description | Product path must mutate the operator workspace under sandbox + grant. Lab isolation remains default for measurement (comment at `lab_driver.py:111`). Add an explicit `--in-place` that is labelled in `labDepartures` / session log. MOCK/`live: false` does not close this task. |
| Proof | Live run: file appears on disk in the given repo; `oracle_green` on `lab/tasks/greenfield-*` with `live: true`. |

### TSK-HAR-002 — Bind `AutonomousGrant` on INTERACTIVE CLI / lab

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/autonomous_grant.py`; CLI / `lab_driver` |
| Milestone | v0.5.0 |
| REQ | `[REQ-TRUST-001]` · K-17 |
| Status | `[TODO] ❌` |
| Drift | Library exists; only `test/runtime/test_autonomous_coding_grant.py` + anticheat import `create_autonomous_grant` |
| Description | Wire signed grant (workspace digest, verbs, command allowlist, budget, expiry) into INTERACTIVE product runs. BENCHMARK must not mint the grant. |
| Proof | `python3 -m unittest test.runtime.test_autonomous_coding_grant -v` (keep) **plus** CLI/lab test: write outside grant denied; BENCHMARK privileged write fail-closed. |

### TSK-HAR-003 — AutonomousGrant protocol library

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/autonomous_grant.py` |
| Milestone | v0.5.0 (keep) |
| REQ | `[REQ-TRUST-001]` |
| Status | `[DONE] ✅` |
| Description | Signed token type + `create_autonomous_grant` / `validate_grant_request`. Product bind is TSK-HAR-002. |
| Proof | `python3 -m unittest test.runtime.test_autonomous_coding_grant -v` |

### TSK-HAR-004 — Un-mocked Q2 dogfood (DOGFOOD-01..03 + greenfield)

| Field | Value |
|---|---|
| Path | `lab/tasks/`; `docs/scrum/sprints/sprint08/evidence/` runbook |
| Milestone | v0.5.0 |
| REQ | S8-J-03 · G-050-06 |
| Status | `[TODO] ❌` |
| Description | Human live dogfood with spend path or free-band model. MOCK campaign is not Q2. |
| Proof | Dated evidence receipt; `oracle_green` signed; no `_fake_backend`. |

### TSK-HAR-005 — Spend authorisation / key rotation

| Field | Value |
|---|---|
| Path | ops; `OPENROUTER_API_KEY` |
| Milestone | v0.5.0 |
| REQ | S9-J-03 · S7-J-04 |
| Status | `[TODO] ❌` |
| Description | Board TODOs: spend authorisation and key rotation. Fail-closed without them. |
| Proof | Written authorisation; paid kits refused until then (`model_selection.py` free band). |

### TSK-HAR-006 — Schema-driven `ProposalTranslator`

| Field | Value |
|---|---|
| Path | `vanguard/packages/adapters/models/invocation.py` |
| Milestone | v0.5.0 (keep) |
| REQ | S10-A-01 |
| Status | `[DONE] ✅` |
| Drift | D-28 |
| Description | No verb table. Keep. |
| Proof | `python3 -m unittest test.adapters.test_invocation -v` (or current translator tests) |

### TSK-HAR-007 — `vg-table-default` register or delete

| Field | Value |
|---|---|
| Path | pack `agency/manifests/vg-table-default/`; kinds/registry |
| Milestone | v0.5.0 |
| REQ | H0 · D-27 |
| Status | `[TODO] ❌` |
| Description | Pack loads in tests but is **not** in `registry.json` / kinds registry as a first-class environment. TableWorld is not an `EnvironmentAdapter`. Either implement adapter + register, or delete pack and strike Increment C. |
| Proof | `rg vg-table-default` in registry **or** pack absent + docs updated. |

### TSK-CLI-001 — Move `_fake_backend` out of production entrypoint

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/coding_entrypoint.py` → `test/` |
| Milestone | v0.5.0 |
| REQ | `[REQ-TRUST-001]` |
| Status | `[TODO] ❌` |
| Description | `_fake_backend` (~line 236) is a production CLI bridge path. Relocate doubles; production refuses `fakeBackend` unless `VANGUARD_ALLOW_FAKE=1` in tests. |
| Proof | `rg _fake_backend vanguard/packages/runtime/coding_entrypoint.py` empty; tests still green. |

### TSK-CLI-002 — Product entry still must not dispatch effects itself

| Field | Value |
|---|---|
| Path | `coding_entrypoint.py` (module docstring) |
| Milestone | v0.5.0 (keep invariant) |
| REQ | `[REQ-TRUST-001]` |
| Status | `[DONE] ✅` |
| Description | Entrypoint is a bridge. Coordinator schedules episodes. Do not grow a second kernel here. Fake backend is TSK-CLI-001. |
| Proof | Module docstring + no `Kernel.dispatch` import in entrypoint. |

---

## 6. v0.5.0 — Wave S-hygiene (context, docs, IDs)

### TSK-CTX-001 — Wire or delete `RegroundPolicy`

| Field | Value |
|---|---|
| Path | `vanguard/packages/agency/context/regrounding.py`; `agency/episode/engine.py` |
| Milestone | v0.5.0 |
| REQ | VG-03 §6.4 |
| Status | `[TODO] ❌` |
| Drift | D-10 |
| Description | Only tests reference the class. Call `shouldRun` as an **observation effect** (VG-03 loop) or delete module and DEF the section. |
| Proof | `rg RegroundPolicy vanguard/packages/agency/episode` non-empty **or** module gone + VG-03 DEF. |

### TSK-CTX-002 — Bind `format_skill_index` in `ContextCompiler`

| Field | Value |
|---|---|
| Path | `vanguard/packages/agency/context/compiler.py`; `domain/artifacts/skill_index.py` |
| Milestone | v0.5.0 |
| REQ | `[REQ-CTX-001]` · W12-J |
| Status | `[TODO] ❌` |
| Description | Function exists and is tested via `test/contracts/test_coding_session.py`. Compiler does not call it. Prefix must hold ≤4k names+descriptions per pack DNA. |
| Proof | `rg format_skill_index vanguard/packages/agency/context` ; compiler unit test with ceiling. |

### TSK-CTX-003 — L1–L5 compiler + compaction strategies

| Field | Value |
|---|---|
| Path | `vanguard/packages/agency/context/` |
| Milestone | v0.5.0 (keep) |
| REQ | `[REQ-CTX-001]` |
| Status | `[DONE] ✅` |
| Drift | D-37 |
| Description | Three of five strategies; recency default. Do not change default without consolidation-loss experiment (v0.7 epic). |
| Proof | `python3 -m unittest discover -s test/agency -t . -p '*context*'` |

### TSK-CTX-004 — FrozenHarness composition

| Field | Value |
|---|---|
| Path | `vanguard/packages/domain/artifacts/manifest.py` |
| Milestone | v0.5.0 (keep) |
| REQ | `A-11` · D-26 |
| Status | `[DONE] ✅` |
| Description | Unknown names fail at compose. Keep. |
| Proof | Manifest/composition tests. |

### TSK-DOC-001 — Remove README biological hierarchy (`REJ-10`)

| Field | Value |
|---|---|
| Path | `README.md` |
| Milestone | v0.5.0 |
| REQ | `REJ-10` |
| Status | `[TODO] ❌` |
| Drift | D-46 |
| Description | Delete LEVEL 0–9 from README. Vision stays in `docs/00_executive/vision.md`. |
| Proof | `rg "LEVEL 0" README.md` empty. |

### TSK-DOC-002 — Fix stale README paths

| Field | Value |
|---|---|
| Path | `README.md` |
| Milestone | v0.5.0 |
| REQ | — |
| Status | `[TODO] ❌` |
| Drift | D-47 |
| Description | Remove/replace `coordination.py`, `sqlite_event.py`, `fs_blob.py`. |
| Proof | Those strings absent or point at current files. |

### TSK-DOC-003 — Declare `cryptography` in TCB list

| Field | Value |
|---|---|
| Path | `docs/main_v4/05_*.md` (`K-02`) |
| Milestone | v0.5.0 |
| REQ | D-48 · `K-02` |
| Status | `[TODO] ❌` |
| Description | Governance signing dependency is TCB. Name it. |
| Proof | K-02 list includes `cryptography`. |

### TSK-TEST-001 — Must-fail ID bijection; `CI-9` must fail on gaps

| Field | Value |
|---|---|
| Path | `tools/rule_test_map.py`; VG-08; `test/broken/` |
| Milestone | v0.5.0 |
| REQ | D-44 · Y-10 |
| Status | `[TODO] ❌` |
| Description | Live IDs are `MF-KRN-*` / `MF-S0-*`, not `MF-01`…`MF-37`. `CI-9` currently exits 0 with `gaps=133`. Publish bijection **or** retarget map; gate must fail. |
| Proof | `python3 tools/rule_test_map.py` non-zero on gaps **or** gaps=0 against live roster. |

### TSK-TEST-002 — Keep 38 must-fail cases; do not rewrite runner

| Field | Value |
|---|---|
| Path | `tools/run_broken_tests.py`; `test/broken/` |
| Milestone | v0.5.0 (keep) |
| REQ | VG-08 |
| Status | `[DONE] ✅` |
| Description | Cases pass. ID migration is TSK-TEST-001. |
| Proof | `python3 tools/run_broken_tests.py` |

### TSK-TEST-003 — `REQ-*` PR gate (stop minting `TK-*` in code)

| Field | Value |
|---|---|
| Path | `tools/check_pr_requirements.py` |
| Milestone | v0.5.0 (keep) |
| REQ | D-45 |
| Status | `[DONE] ✅` |
| Description | Keep REQ namespace. |
| Proof | `python3 tools/check_pr_requirements.py` (as CI uses it) |

### TSK-SEC-001 — AT-12 or documented deferral with compensating control

| Field | Value |
|---|---|
| Path | architecture tests; `tools/` |
| Milestone | v0.5.0 |
| REQ | `AT-12` · D-33 |
| Status | `[TODO] ❌` |
| Description | Import lattice ≠ AT-12. Add capability↛verifier path test, or ADR-defer with unreadability probe named as compensating control. AT-10/AT-11 same bucket. |
| Proof | New `test/broken` or `test/kernel` AT-12 **or** ADR + `publication_decision` cited. |

### TSK-SEC-002 — Seccomp / rlimits / static bwrap (defer or cheap apply)

| Field | Value |
|---|---|
| Path | `vanguard/packages/adapters/sandbox/rootless.py` |
| Milestone | v0.5.0 |
| REQ | `K-37` · `K-39` · `K-41` · D-31 |
| Status | `[TODO] ❌` |
| Description | Milestones: rlimits from lease if cheap; seccomp only if profile is reviewable. Default path is **ADR defer**, not a silent “we have unshare --mount”. |
| Proof | ADR **or** applied rlimits test. |

### TSK-SEC-003 — Namespace probes + `publication_decision`

| Field | Value |
|---|---|
| Path | `vanguard/packages/ports/sandbox.py`; rootless adapter |
| Milestone | v0.5.0 (keep) |
| REQ | `K-42`–`K-44` · `K-46` |
| Status | `[DONE] ✅` |
| Drift | D-30 |
| Description | Real probes; fake runner unverified. Keep. |
| Proof | Sandbox probe tests. |

### TSK-SEC-004 — Startup perimeter probes (keep)

| Field | Value |
|---|---|
| Path | `adapters/sandbox/rootless.py` |
| Milestone | v0.5.0 (keep) |
| REQ | `K-42` |
| Status | `[DONE] ✅` |
| Description | Do not claim seccomp (TSK-SEC-002). |
| Proof | Same as TSK-SEC-003. |

---

## 7. v0.5.0 — Frontend (FE-2-8, FE-2-9, FE-3-1…7)

Not G-050. Proof commands from `docs/scrum/roadmap_frontend.md` §7.

### TSK-FE-008 — Claude-class Ink chrome (FE-2-8)

| Field | Value |
|---|---|
| Path | `vanguard/clients/cli/src/tui/**` |
| Milestone | v0.5.0 (Interaction; board Wave 2) |
| REQ | INVAR-FE-01 · FE-2-8 |
| Status | `[DONE] ✅` |
| Description | Status bar, windowed transcript, prompt bar, focus modes, ctrl+c → cancel, help overlay. `ui.test.ts` covers DoD atoms. Living board still says `[TODO]`; **code+tests supersede the board**. |
| Proof | `cd vanguard/clients/cli && npm run typecheck && npm test` |

### TSK-FE-009 — Resume chrome `requestResume` (FE-2-9)

| Field | Value |
|---|---|
| Path | `vanguard/clients/cli/src/tui/screens/run-tui.tsx`; `composition/resume-session.ts` |
| Milestone | v0.5.0 (board Wave 3) |
| REQ | FE-2-9 · FE-1-9 |
| Status | `[DONE] ✅` |
| Description | `performResume` + TUI `beginResume`; `not_available` does not start a mock stream (`ui.test.ts`). Live daemon attach remains J1. |
| Proof | `cd vanguard/clients/cli && npm test` (resume not_available case) |

### TSK-FE-031 — GUI shell + slot registry (FE-3-1)

| Field | Value |
|---|---|
| Path | `vanguard-gui/src/main.tsx`; `vanguard-gui/docs/ADR-FE-GUI-001.md` |
| Milestone | v0.5.0 |
| REQ | FE-3-1 |
| Status | `[DONE] ✅` |
| Description | Tauri 2 + React scaffold, slot switcher. Dev install is TSK-FE-030. |
| Proof | `cd vanguard-gui && npm run typecheck` |

### TSK-FE-030 — GUI toolchain lockfile + install (FE-3-0)

| Field | Value |
|---|---|
| Path | `vanguard-gui/pnpm-lock.yaml`; `package.json` |
| Milestone | v0.5.0 |
| REQ | FE-3-0 |
| Status | `[DONE] ✅` |
| Description | `pnpm-lock.yaml` is present (board’s `package-lock` TODO is stale). Remaining: document `pnpm install` vs npm in playbook if needed. |
| Proof | `test -f vanguard-gui/pnpm-lock.yaml`; `cd vanguard-gui && pnpm install && npm run typecheck` |

### TSK-FE-032 — Replay run panel (FE-3-2)

| Field | Value |
|---|---|
| Path | `vanguard-gui/src/main.tsx` (`ReplayRuntimeClient`) |
| Milestone | v0.5.0 |
| REQ | FE-3-2 |
| Status | `[DONE] ✅` |
| Description | Fixture JSONL, `source: mock`. Not virtualized (known). |
| Proof | `cd vanguard-gui && npm run typecheck`; replay path in `main.tsx` |

### TSK-FE-033 — Real file tree + Monaco (FE-3-3)

| Field | Value |
|---|---|
| Path | `vanguard-gui/src/slots/files.tsx`, `editor.tsx` |
| Milestone | v0.5.0 |
| REQ | FE-3-3 |
| Status | `[TODO] ❌` |
| Description | Monaco editor exists. Files slot is **MOCK_FILES** stub (“Tauri fs walk will replace this”). |
| Proof | Open a workspace file from disk (not `MOCK_FILES`); typecheck + GUI test or manual DoD note. |

### TSK-FE-034 — Interactive PTY or keep honest `not_available` (FE-3-4)

| Field | Value |
|---|---|
| Path | `vanguard-gui/src/slots/terminal.tsx` |
| Milestone | v0.5.0 |
| REQ | FE-3-4 |
| Status | `[TODO] ❌` |
| Description | Browser path is honest `not_available`. Tauri branch only `writeln`s a banner — not a working PTY (`pty_write` / `pty_resize`). |
| Proof | PTY input echoes in Tauri **or** documented permanent `not_available` with test. |

### TSK-FE-035 — xyflow VG-04 event view (FE-3-5)

| Field | Value |
|---|---|
| Path | `vanguard-gui/src/slots/trace.tsx` |
| Milestone | v0.5.0 (board Wave 3) |
| REQ | FE-3-5 · FE-1-7 |
| Status | `[TODO] ❌` |
| Description | `toTraceGraph` is bound to React Flow. No GUI unit tests; board still Wave 3. Close with a client-core/GUI test that nodes come from `payload.kind` only. |
| Proof | Golden vs `successful-episode.jsonl`; `cd vanguard/clients/client-core && npm test` already has FE-1-7 — add GUI or core assertion wired from this slot. |

### TSK-FE-036 — Monaco diff + Ed25519 approve (FE-3-6)

| Field | Value |
|---|---|
| Path | `vanguard-gui/src/slots/approve.tsx` |
| Milestone | v0.5.0 (board Wave 3) |
| REQ | FE-3-6 · J4 |
| Status | `[TODO] ❌` |
| Description | DiffEditor + `OperatorSigner` exist. Replay resolve is read-only `not_available`. Needs live `resolveApproval` + populated challenge digests (J4). |
| Proof | Signed approve against fake/live client with non-empty digests; no success on empty digest. |

### TSK-FE-037 — Command palette + git status (FE-3-7)

| Field | Value |
|---|---|
| Path | `vanguard-gui/src/slots/palette.tsx`, `git.tsx` |
| Milestone | v0.5.0 (board Wave 3) |
| REQ | FE-3-7 |
| Status | `[TODO] ❌` |
| Description | cmdk has ≥3 actions. Git is `not_available` without Tauri `git_status_sb` / branch invoke. |
| Proof | Palette ≥3 actions (code already); `git status -sb` display in Tauri with branch label. |

### TSK-FE-J1 — Runtime daemon self-launch (J1)

| Field | Value |
|---|---|
| Path | backend service `__main__` |
| Milestone | v1.0.0 (blocks FE live) |
| REQ | J1 |
| Status | `[TODO] ❌` |
| Description | Frontend board `[BLOCKED]`. Not a G-050 gate. |
| Proof | `vg` live UDS without manual daemon ritual; FE-2 `not_available` only when truly down. |

### TSK-FE-J2 — Ping/health verb (J2)

| Field | Value |
|---|---|
| Path | wire + service |
| Milestone | v1.0.0 |
| REQ | J2 |
| Status | `[TODO] ❌` |
| Proof | Health round-trip test. |

### TSK-FE-J3 — ListManifests (J3)

| Field | Value |
|---|---|
| Path | wire + service |
| Milestone | v1.0.0 |
| REQ | J3 |
| Status | `[TODO] ❌` |
| Proof | Client lists frozen harness names. |

### TSK-FE-J4 — Populated approval digests (J4)

| Field | Value |
|---|---|
| Path | approval challenge emission |
| Milestone | v0.5.0 (needed for honest INTERACTIVE) |
| REQ | J4 · G-050-04 |
| Status | `[TODO] ❌` |
| Description | Empty-digest success is forbidden (CLI already). Backend must populate challenge fields. |
| Proof | ApprovalRequested envelope has args+descriptor digests; CLI/GUI cannot approve empty. |

---

## 8. Honour table — do not open in v0.5.0 (tracked as later epics)

These are **not** forgotten; they are illegal in v0.5.0 per DRIFTS §4.5 and milestones §9.

| ID | Item | First legal milestone |
|---|---|---|
| D-35 | Cognitive operator registry | v0.9.0 |
| D-36 | Playbook interpreter | v0.9.0 (`advisory` data-only may appear v0.6) |
| D-38 | Independence groups production | v0.7 experiment / v0.9 prod |
| D-39 | \(G_C, G_E\) walker / activation | v0.8.0 |
| D-34 | SA-1…SA-6 updater | v0.9–v1.0 |
| D-41 | `MetaLoopEngine` | never (keep deleted) |
| MCP authority | ADR-0066 | never |

Keep-set already encoded as `[DONE]` above: D-01, D-03, D-04 code, D-16, D-17, D-18 code, D-25 tool, D-26, D-28, D-30, D-32 code, D-37, D-40 (measurement stays in `lab/`+`tools/telemetry/` — no task to move it in).

### TSK-CORE-010 — Measurement stays outside packages

| Field | Value |
|---|---|
| Path | `lab/`; `tools/telemetry/` |
| Milestone | v0.5.0 (keep) |
| REQ | D-40 · VG-07 |
| Status | `[DONE] ✅` |
| Description | Do not import lab into `vanguard/packages/`. |
| Proof | `python3 tools/check_boundaries.py` |

### TSK-CORE-011 — No `MetaLoopEngine`

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/` (loops deleted) |
| Milestone | v0.5.0 (keep) |
| REQ | D-41 · `A-05` |
| Status | `[DONE] ✅` |
| Description | Escalation is `tier_escalation.py` around repair. Keep. |
| Proof | `test -d vanguard/packages/runtime/loops` fails. |

---

## 9. v0.6.0+ research epics (high-level)

Granular tasks are **not** exploded. Each epic is one backlog item until that milestone opens.

### TSK-EPIC-060-001 — Remove `coding_*` from `runtime/`

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/coding_*.py` → app package |
| Milestone | v0.6.0 |
| REQ | `[REQ-TRUST-001]` · D-42 · G-060-01 |
| Status | `[TODO] ❌` |
| Description | Coordinator may remain an episode *scheduler* in an application package. Kernel/agency stay domain-agnostic. Move `domain/ledger/coding_session.py` up. |
| Proof | `rg coding_ vanguard/packages/runtime` empty; `python3 tools/check_boundaries.py`; M11. |

### TSK-EPIC-060-002 — Single `ModelRouter`

| Field | Value |
|---|---|
| Path | `model_selection.py`, `tier_escalation.py`, coordinator `_route` |
| Milestone | v0.6.0 |
| REQ | G-060-04 |
| Status | `[TODO] ❌` |
| Description | One port implementation; coordinator delegates only. |
| Proof | Single module owns role→model; duplicate heuristics gone. |

### TSK-EPIC-060-003 — Split `root.py` composition root

| Field | Value |
|---|---|
| Path | `vanguard/packages/runtime/root.py` |
| Milestone | v0.6.0 |
| REQ | G-060-08 |
| Status | `[TODO] ❌` |
| Description | Session / compose / evaluator transport as distinct modules. No new god-object. |
| Proof | Review + unittest discover on split modules. |

### TSK-EPIC-060-004 — Second environment H0 (TableWorld adapter)

| Field | Value |
|---|---|
| Path | `adapters/environment/`; registry |
| Milestone | v0.6.0 |
| REQ | `C-10` · G-060-02 |
| Status | `[TODO] ❌` |
| Description | Real `EnvironmentAdapter` + registered pack, or Increment C struck (if not already by TSK-HAR-007). |
| Proof | Episode without `coding_*` imports. |

### TSK-EPIC-060-005 — Unify three `EffectRequest` types

| Field | Value |
|---|---|
| Path | `kernel.model`, `ports.environment`, wire `EffectDescriptor` |
| Milestone | v0.6.0 |
| REQ | D-21 |
| Status | `[TODO] ❌` |
| Description | One request at S0; translator shrinks. |
| Proof | Single type name in packages or explicit mapping module with goldens. |

### TSK-EPIC-060-006 — Optional advisory playbook *data* (no dispatch)

| Field | Value |
|---|---|
| Path | pack genes; not `kernel/` |
| Milestone | v0.6.0 |
| REQ | `N-20` · D-36 |
| Status | `[TODO] ❌` |
| Description | If extracted from `CodingPhase`, rigidity=`advisory` only. Playbook must not call tools. |
| Proof | I-09: no playbook module imports `Kernel`. |

### TSK-EPIC-070-001 — Tree-sitter `IndexPort` body

| Field | Value |
|---|---|
| Path | indexer adapter; `ports/index.py` unchanged |
| Milestone | v0.7.0 |
| REQ | S10-A-03 · ADR-0059 · G-070-01 |
| Status | `[TODO] ❌` |
| Description | Replace regex scan; port still observation-only. |
| Proof | Index tests forbid propose/dispatch; polyglot not in `kernel/`. |

### TSK-EPIC-070-002 — Prompt-cache metrics + compaction experiment

| Field | Value |
|---|---|
| Path | `tools/telemetry/`; `agency/context/` |
| Milestone | v0.7.0 |
| REQ | D-37 · G-070-02 |
| Status | `[TODO] ❌` |
| Description | Cache-hit vs consolidation-loss; do not flip default without data. |
| Proof | Telemetry tuple from ledger; published experiment. |

### TSK-EPIC-070-003 — Model-kit bake-off corpus

| Field | Value |
|---|---|
| Path | `lab/`; kits as config |
| Milestone | v0.7.0 |
| REQ | G-070-03 · M-18 |
| Status | `[TODO] ❌` |
| Description | ≥3 kits, holdout, no optimizer-in-the-loop. |
| Proof | Pareto JSON + figure; A/A refuse. |

### TSK-EPIC-070-004 — Independence-group *experiment* flag

| Field | Value |
|---|---|
| Path | episode engine (flagged) |
| Milestone | v0.7.0 |
| REQ | `C-04` · D-38 |
| Status | `[TODO] ❌` |
| Description | Production default sequential until CC-6 can emit. |
| Proof | Flag-off = today’s sequential tests green. |

### TSK-EPIC-080-001 — Evidence graph walker + contradiction index

| Field | Value |
|---|---|
| Path | agency/adapters; not kernel |
| Milestone | v0.8.0 |
| REQ | VG-06 · D-23 · G-080-01 |
| Status | `[TODO] ❌` |
| Description | `Claim` fields already exist. Build index + `Contra(c)`. |
| Proof | Golden graphs; must-fail unevidenced ≠ corroborated. |

### TSK-EPIC-080-002 — Competence graph \(G_C\) + claim pipeline

| Field | Value |
|---|---|
| Path | VG-06 pipeline |
| Milestone | v0.8.0 |
| REQ | D-39 · G-080-02 |
| Status | `[TODO] ❌` |
| Description | Extract → corroborate → quarantine → activate as **data**. |
| Proof | `EvidenceClaimProduced` from production; S1(f) must-fail. |

### TSK-EPIC-080-003 — Activation set \(A_t\) (evidence policy only)

| Field | Value |
|---|---|
| Path | context admission |
| Milestone | v0.8.0 |
| REQ | `MEM-4` · G-080-06 |
| Status | `[TODO] ❌` |
| Description | No Evolution `ActivationChanged` yet. |
| Proof | Recall cannot justify grant widening. |

### TSK-EPIC-080-004 — Cross-task learning-curve measurement

| Field | Value |
|---|---|
| Path | `lab/` |
| Milestone | v0.8.0 |
| REQ | G-080-04 · `C-06` |
| Status | `[TODO] ❌` |
| Description | Holdout ablation vs unguided. Honest failure allowed. |
| Proof | Published curve or explicit non-claim. |

### TSK-EPIC-090-001 — Operator registry (operators as data)

| Field | Value |
|---|---|
| Path | cognition; retire `_LayeredOperator` as the only form |
| Milestone | v0.9.0 |
| REQ | `A-02` · D-35 · G-090-01 |
| Status | `[TODO] ❌` |
| Proof | Replace operator without kernel/agency edit. |

### TSK-EPIC-090-002 — Playbook rigidity dial (constrain, never dispatch)

| Field | Value |
|---|---|
| Path | playbook artefact; delete Python `CodingPhase` enum from runtime |
| Milestone | v0.9.0 |
| REQ | VG-03 §2.11 · G-090-02 |
| Status | `[TODO] ❌` |
| Proof | `strict` recovered as data; I-09. |

### TSK-EPIC-090-003 — Hats + System 1/2 routing policy

| Field | Value |
|---|---|
| Path | operatorPolicy; `OperatorSelected` on \(L\) |
| Milestone | v0.9.0 |
| REQ | G-090-03 · G-090-04 |
| Status | `[TODO] ❌` |
| Description | Not a second engine. No `MetaLoopEngine`. |
| Proof | Must-fail: cannot silently drop S2 when policy forbids. |

### TSK-EPIC-090-004 — Evolution plane pointer moves

| Field | Value |
|---|---|
| Path | Evolution identity; not worker |
| Milestone | v0.9.0 |
| REQ | VG-03 Evolution · G-090-06 |
| Status | `[TODO] ❌` |
| Description | Emit `CandidateBuilt`, `CanaryPromoted`, `RollbackTriggered`, `ActivationChanged`. R0/R1 human-gated. |
| Proof | Canary+rollback drill; worker cannot emit `ActivationChanged`. |

### TSK-EPIC-100-001 — Production TUI on live daemon

| Field | Value |
|---|---|
| Path | `vanguard/clients/cli/` + J1 |
| Milestone | v1.0.0 |
| REQ | G-100-01 |
| Status | `[TODO] ❌` |
| Proof | Live UDS; resume; why; approvals. |

### TSK-EPIC-100-002 — Production `vanguard-gui` IDE

| Field | Value |
|---|---|
| Path | `vanguard-gui/` |
| Milestone | v1.0.0 |
| REQ | G-100-02 |
| Status | `[TODO] ❌` |
| Description | Files, Monaco, PTY, git, approve — `gui_ide_slots.md`. Pack-driven chrome only; no self-write of client binaries. |
| Proof | `npm run typecheck`; soak + dogfood. |

---

## 10. Suggested v0.5.0 pull order

```text
TSK-CORE-001 → TSK-CORE-002 → TSK-LED-002 → TSK-LED-003 → TSK-LED-001
     → TSK-LED-005 → TSK-EVAL-001 → TSK-CORE-003 → TSK-CORE-004
     → TSK-SPEC-001…010 (can parallel after S-truth starts)
     → TSK-HAR-002 → TSK-HAR-001 → TSK-HAR-004
     → TSK-CLI-001 → TSK-CTX-001 → TSK-CTX-002
     → TSK-TEST-001 → TSK-HAR-007 → TSK-SEC-001
     → TSK-DOC-001/002
FE-2-8/2-9 already DONE; FE-3-3…3-7 and J4 parallel, not blocking G-050.
```

**Illegal in v0.5.0:** competence graph, operator registry, playbook *runtime*, independence-group production, GUI as backend exit, kernel rewrite, restoring K-40 same-perimeter evaluator.

---

## 11. ID index (grep)

```
TSK-CORE-001 TODO  TSK-CORE-002 TODO  TSK-CORE-003 TODO  TSK-CORE-004 TODO
TSK-CORE-005 DONE  TSK-CORE-006 DONE  TSK-CORE-007 DONE  TSK-CORE-008 DONE
TSK-CORE-009 DONE  TSK-CORE-010 DONE  TSK-CORE-011 DONE
TSK-LED-001 TODO   TSK-LED-002 TODO   TSK-LED-003 TODO   TSK-LED-004 TODO
TSK-LED-005 TODO   TSK-LED-006 DONE   TSK-LED-007 DONE   TSK-LED-008 DONE
TSK-LED-009 TODO
TSK-EVAL-001 TODO  TSK-EVAL-002 DONE
TSK-SPEC-001..010 TODO  TSK-SPEC-011 DONE
TSK-HAR-001 TODO   TSK-HAR-002 TODO   TSK-HAR-003 DONE   TSK-HAR-004 TODO
TSK-HAR-005 TODO   TSK-HAR-006 DONE   TSK-HAR-007 TODO
TSK-CLI-001 TODO   TSK-CLI-002 DONE
TSK-CTX-001 TODO   TSK-CTX-002 TODO   TSK-CTX-003 DONE   TSK-CTX-004 DONE
TSK-DOC-001 TODO   TSK-DOC-002 TODO   TSK-DOC-003 TODO
TSK-TEST-001 TODO  TSK-TEST-002 DONE  TSK-TEST-003 DONE
TSK-SEC-001 TODO   TSK-SEC-002 TODO   TSK-SEC-003 DONE   TSK-SEC-004 DONE
TSK-FE-008 DONE    TSK-FE-009 DONE    TSK-FE-030 DONE    TSK-FE-031 DONE
TSK-FE-032 DONE    TSK-FE-033 TODO    TSK-FE-034 TODO    TSK-FE-035 TODO
TSK-FE-036 TODO    TSK-FE-037 TODO    TSK-FE-J1 TODO     TSK-FE-J2 TODO
TSK-FE-J3 TODO     TSK-FE-J4 TODO
TSK-EPIC-060-* … TSK-EPIC-100-* all TODO
```

---

*End of ROAD-BACK-01. Next execution unit: TSK-CORE-001 (production spans), not a new ontology.*
