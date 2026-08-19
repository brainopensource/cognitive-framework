---
id: SPRINT-060-ACTIVE
file: docs/03_sprints/sprint_active.md
title: "Active sprint — v0.6.0 Molecular Lattice (+ v0.5 G-050 closeout)"
status: ACTIVE
milestone: v0.6.0
predecessor: v0.5.0 Empirical Baseline (PARTIAL — not tagged)
timebox: 10 working days
branch: feat/v060-microkernel-waist
backlog: docs/02_roadmap/backlog.md
milestones: docs/02_roadmap/milestones.md
spec: docs/01_specs/backend/
req: REQ-TRUST-001
last_reviewed: 2026-08-18
---

# Sprint board — v0.6.0 Decoupled Micro-Kernel

**Next sprint after v0.5.0 is v0.6.0** (`ROAD-MILE-01` §4, vision “Molecular Lattice”).

**v0.5.0 is not tagged.** DEV ALFA/GAMMA and DEV BETA briefs claimed 100% completion. Code audit
against `docs/01_specs/backend/` (VG-03/VG-05) and the backlog accepted **four** rows only:

| Closed (Landed in Wave 0) | Still open (Final Wave 0 closeout) |
|---|---|
| `TSK-CORE-001` spans in `_admit_turn_result` | `TSK-LED-001` writer check: reject unknown kinds in `parse_event_envelope` |
| `TSK-CORE-002` `spawn` → `child_return` | `TSK-EVAL-001` compose `EvaluationListener` into service/root |
| `TSK-CORE-003`/`004` `Trust.OPERATOR` table & engine `AuthorizationDenied` | `TSK-LED-004`/`005` heartbeat & budget kinds / ADR |
| `TSK-CTX-001` deleted dead `RegroundPolicy` | `TSK-SPEC-008` grant-shape goldens |
| `TSK-CTX-002` `format_skill_index` in L3 (**G-060-05**) | |
| `TSK-LED-002` `EpisodeStarted` emit in `root.py` at seq=0 | |
| `TSK-LED-003` `ApprovalResolved` appended to ledger store | |
| `TSK-HAR-001` `--in-place` flag | |
| `TSK-HAR-002` `AutonomousGrant` bound on `--in-place` | |
| `TSK-HAR-004` live campaign runner wired (`--live`) | |
| `TSK-CLI-001` test fixture relocation clean | |
| `TSK-DOC-001` README stale references cleaned | |

Agile rule: **do not extract `coding_*` (G-060-01) until Wave 0 makes the ledger tell the truth.**
A thinner runtime on a lying session is the v0.4 failure mode again.

**Sentence this sprint makes true:**

> Remaining G-050 holes are closed, then `runtime/` no longer owns coding-named modules; a second
> environment is registered or cut; routing is one `ModelRouter`; `root.py` is split.

---

## 0. Law

Same invariants as v0.5 (`A-01`, `AT-01`, `A-05`, BENCHMARK fail-closed, one effect/turn, TCB ≤ 1438).
Playbook *runtime* remains illegal (`N-20`, `TSK-EPIC-090-002`). Spec corpus: **`docs/01_specs/backend/`**.

### Lanes (zero file overlap)

| Lane | Role | Write | Do not touch |
|---|---|---|---|
| **ALFA** | Waist + remaining engine hygiene | `agency/episode/**` · `agency/context/regrounding.py` · **new** `vanguard/packages/apps/coding/**` (move target) · `runtime/root.py` **until A-08 split, then only the session module** · `runtime/model_selection.py` + `tier_escalation.py` (router merge) · `test/agency/**` · `test/apps/**` | `kernel/dispatch.py`, `lab_driver.py`, `docs/01_specs` |
| **BETA** | G-050 ledger/eval/grant closeout | `kernel/dispatch.py` (emit only) · `domain/ledger/events.py` · `runtime/service/service.py` · `runtime/evaluation_listener.py` · `runtime/autonomous_grant.py` · `runtime/governance/**` · `test/kernel/**` · `test/runtime/test_evaluation_*` · `test/runtime/test_autonomous_*` | `coding_*.py`, `lab_driver.py`, `root.py` |
| **GAMMA** | Live proof + H0 + spec freeze | `lab_driver.py` · `coding_entrypoint.py` · `lab/**` · `tools/run_v0450_greenfield_campaign.py` · `tools/rule_test_map.py` · `README.md` · **`docs/01_specs/backend/**`** · `agency/manifests/vg-table-default/**` + registry | `engine.py`, `kernel/`, `evaluation_listener.py` |

**Handoffs:** BETA does not edit `root.py`. ALFA, after Wave 0, injects `EvaluationListener` at compose (one constructor argument). GAMMA only **imports** `create_autonomous_grant`.

---

## 1. Wave 0 — v0.5 closeout (Days 1–4, all lanes in parallel)

Must reach G-050-03…07 before G-060-01 moves files.

### S060-A-01 — Emit `EpisodeStarted` `[DONE] ✅` → `TSK-LED-002`

`agency/episode/engine.py` or session module; not CLI fixtures.

```bash
rg "EpisodeStarted" vanguard/packages/agency vanguard/packages/runtime
python3 -m unittest discover -s test/agency -t . -q
```

### S060-A-02 — `Trust.OPERATOR` call-site + child `AuthorizationDenied` `[DONE] ✅`

`TSK-CORE-003`, `TSK-CORE-004`. `root.py` span labels; engine refuse must append `AuthorizationDenied`.

### S060-A-03 — Wire or delete `RegroundPolicy` `[DONE] ✅` → `TSK-CTX-001`

Observation effect through dispatch, or delete + GAMMA DEF in VG-03.

### S060-B-01 — Close `EVENT_KINDS` at writer `[TODO] ❌` → `TSK-LED-001`

Add `EffectRejected`, `KernelAlarm`. `parse_event_envelope` / store append rejects unknown `payload.kind`.

```bash
python3 -m unittest test.test_ledger_properties test.contracts.t3_ledger -v
```

### S060-B-02 — Persist `ApprovalResolved` `[DONE] ✅` → `TSK-LED-003` · G-050-04

`_cmd_ResolveApproval` must `append` after `queue.put`. `verify_from_ledger` already consumes.

### S060-B-03 — Emit grant/budget kinds or ADR-shrink `[TODO] ❌` → `TSK-LED-005`

### S060-B-04 — Compose `EvaluationListener` `[TODO] ❌` → `TSK-EVAL-001` · G-050-05

Replace `HarnessSession._evaluate` as authority. ALFA lands the callback slot if `root.py` is still exclusive — **handoff**: BETA implements; ALFA wires after A-08 or via compose kwarg **without** BETA editing `root.py` if ALFA adds the kwarg on Day 1.

Day 1 ALFA: add `on_terminal: Callable | None` to `HarnessSession` (same as former S050-A-06).

```bash
rg "EvaluationListener" vanguard/packages/runtime/root.py
python3 -m unittest test.runtime.test_evaluation_listener test.test_spine -v
```

### S060-B-05 — Heartbeat or ADR-defer `[TODO] ❌` → `TSK-LED-004`

### S060-B-06 — Grant-shape goldens `[TODO] ❌` → `TSK-SPEC-008` (code)

### S060-G-01 — Bind `AutonomousGrant` on INTERACTIVE `--in-place` `[DONE] ✅` → `TSK-HAR-002`

`lab_driver.py` / entrypoint only. BENCHMARK must not mint.

### S060-G-02 — Live campaign (not fake) `[DONE] ✅` → `TSK-HAR-004` · G-050-06

`tools/run_v0450_greenfield_campaign.py --live` currently **returns 3** (“binder not yet wired”). Remove the refuse; no `fakeBackend`. Exit 0 on scripted fake **does not** close this row.

### S060-G-03 — Finish fake relocation `[DONE] ✅` → `TSK-CLI-001`

`coding_entrypoint` still `from test.fixtures.coding_scripted_backends import scripted_backend` but **that file is absent**. Land the fixture **or** delete the import path.

### S060-G-04 — README + CI-9 + VG freeze `[DONE] ✅`

`TSK-DOC-001`/`002`, `TSK-TEST-001`, `TSK-SPEC-001`…`010`, `TSK-DOC-003`. Edit **`docs/01_specs/backend/`** (canonical). Mirror `docs/main_v4/` only if CI still points there.

```bash
rg "LEVEL 0|coordination.py|sqlite_event.py" README.md
python3 tools/rule_test_map.py; echo $?
```

---

## 2. Wave 1 — v0.6 waist (Days 5–10)

### Lane ALFA

#### S060-A-10 — Move `coding_*` out of `runtime/` `[DONE] ✅` → `TSK-EPIC-060-001` · G-060-01

Target: `vanguard/packages/apps/coding/` (new). `domain/ledger/coding_session.py` moved up with it. Coordinator remains an **episode scheduler**, not a dispatcher.

`apps` registered as a 7th ICD package in `tools/check_boundaries.py` (`ALLOWED["apps"]` mirrors `runtime`'s reach; nothing else may import `apps` back). Moved: `coding_budget.py`, `coding_coordinator.py`, `coding_entrypoint.py`, `coding_plan.py`, `coding_progress.py`, `coding_verification.py`, `domain/ledger/coding_session.py`. `domain/ledger/__init__.py` no longer exports `project_coding_session` (M11: domain stays coding-agnostic). All `test/runtime/test_coding_*.py`, `test/contracts/test_coding_session.py`, `test/fixtures/coding_scripted_backends.py`, `tools/run_v0450_greenfield_campaign.py`, `tools/export_coding_session.py` re-pointed at the new module paths. New `test/apps/coding/test_apps_coding_location.py` proof.

```bash
rg "coding_" vanguard/packages/runtime --glob '*.py'   # only mock_coding_tape.py (test scaffolding, not moved)
python3 tools/check_boundaries.py                       # BOUNDARY PASS: 247 source files checked
python3 -m unittest discover -s test -t .                # 1044 tests, OK
```

**Blocked on Wave 0.**

#### S060-A-11 — Single `ModelRouter` `[TODO] ❌` → `TSK-EPIC-060-002` · G-060-04

Merge `model_selection.py` + `tier_escalation.py` + coordinator `_route` into one implementation. Coordinator delegates only.

#### S060-A-12 — Split `root.py` `[TODO] ❌` → `TSK-EPIC-060-003` · G-060-08

Composition / session / evaluator transport as distinct modules. No new god-object.

### Lane GAMMA (after Wave 0 docs)

#### S060-G-10 — TableWorld register **or** delete `[TODO] ❌` → `TSK-HAR-007` · G-060-02

Not a full adapter this sprint unless cheap; **no orphans**. Full `EnvironmentAdapter` is G-060-03 if time remains (`TSK-EPIC-060-004`).

### Lane BETA (if Wave 0 finished early)

#### S060-B-10 — Unify `EffectRequest` types `[TODO] ❌` → `TSK-EPIC-060-005`

#### S060-B-11 — AT-12 or defer ADR `[TODO] ❌` → `TSK-SEC-001`

---

## 3. Day board

| Day | ALFA | BETA | GAMMA |
|---|---|---|---|
| 1 | `on_terminal` kwarg + A-01 EpisodeStarted | B-01 EVENT_KINDS | G-03 fixture file; start G-01 |
| 2 | A-01 DoD; A-02 | B-02 ApprovalResolved | G-01 grant bind |
| 3 | A-03 Reground | B-04 listener compose | G-02 live path (may `[BLOCKED]` on keys) |
| 4 | Wave 0 integration | B-03/B-05/B-06 | G-04 README + start VG freeze |
| 5–7 | A-10 move `coding_*` | AT-12 / EffectRequest | G-10 TableWorld; VG freeze |
| 8–9 | A-11 router; A-12 split root | contract tests | live receipt or honest `[BLOCKED]` |
| 10 | Joint G-060-01, 04, 07, 08 + remaining G-050 | | |

---

## 4. Joint verification

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

PR body: at least one `REQ-TRUST-001` / `REQ-CTX-001` / `REQ-HAR-001` / `REQ-LEDGER-002` (`AGENTS.md`).

**Do not tag v0.6.0** if G-060-01 is green but G-050-03…05 are still open.

---

## 5. Explicitly not this sprint

v0.7 Tree-sitter / bake-offs · v0.8 \(G_C,G_E\) · v0.9 operators/playbook-strict/Evolution · v1.0 TUI/GUI as backend gates · `MetaLoopEngine` · MCP authority.

---

*End of SPRINT-060-ACTIVE. v0.5 wired spans and `--in-place`; v0.6 must first make \(L\) complete, then shrink `runtime/`.*
