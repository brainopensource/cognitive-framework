---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: living
owner: tech-lead
version: "0.6.1"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Active Sprint Board — v0.6.2 Extensibility (M-3)

**Start here:** [`README.md`](../../README.md) and [`SPEC.md`](../SPEC.md) define production truth and normative law. This board is the **sole living execution authority**.

---

## 1. Wave Status Summary

| Wave | Milestone | State | Focus & Exit Condition |
|---|---|---|---|
| **Wave 0** | M-0 | **CLOSED** | CI subject of record on `vanguard/packages/` + named falsifiers F-01…F-21. |
| **Wave 1** | M-1 | **CLOSED (GREEN)** | Trust spine: signed verdicts, single emitter, typed budgets, complete $D_H$. |
| **Wave 2** | M-2 | **DONE (Round 4)** | Convergence core: absorbed SPI/JSON-RPC/lifecycle, deleted duplicate layer0 kernel. |
| **Wave 2C** | M-2 / v0.6.1 | **CLOSED (GREEN)** | Evidence integrity: RF-23 (truthful trajectory) + RF-25 (fresh-process SQLite continuation). |
| **Wave 3** | M-3 | **OPEN (ACTIVE)** | Finish canonical `mhf.manifest/2`, parser convergence, graph falsifiers, and objective Layer-0 retirement proof. |
| **Wave 4** | M-4 | **QUEUED** | Foundation E2E Stop: one uncheated real coding-agent run with nine evidence rows, after M-3 closes. |

---

## 2. Active M-3 Implementation Contract

### Sprint 3.1 — Named Component Graph

**Implement:** make one canonical reader normalize supported legacy manifests and
`mhf.manifest/2` into one immutable domain value. Compile named instances, same-kind repetitions,
typed bindings, interfaces, implementation/config refs, isolation, ceilings, profiles, and named
entrypoints. Resolve refs once, freeze the complete graph, and include every node/edge/config/ref
digest in $D_H$.

```text
bytes -> schema/reader -> canonical manifest value -> resolve immutable refs
      -> validate endpoints/interfaces/authority/cycles/ceilings -> JCS freeze -> D_H
```

**Fail closed:** unknown fields/refs/SPI kinds/endpoints/interfaces/isolation; self-edge; unread or
unconsumed authority; empty/incomparable ceiling; eager cycle. Only typed lazy post-activation
cycles are legal. Profiles and `agent.spawn` fields enter identity but remain inert with their
named pre-authorization refusal.

**Do not build:** graph scheduling, component-name kernel branches, another parser, another episode
engine, or dynamic turn order.

**Gate:** RF-28–RF-33, RF-46, RF-73–RF-74, RF-76; edge-only change changes $D_H$; compatibility
rows preserve facts without invented defaults; no production parser besides the canonical reader.

### Sprint 3.2 — Registry and isolation parity

**Implement:** bind the packages registry FSM to `LedgerEmitter.registry()` and the canonical event
catalog/reducer. For subprocess/container tiers use one JSON-RPC 2.0 schema over a mode-0600 UDS;
for policy-granted `in_process`, use direct typed dispatch with identical method/result semantics.
Enforce allowed methods, timeout, ceiling, cleanup, child-death containment, and isolated logs.

```text
discover -> resolve -> verify(D_H, ceiling result) -> activate -> call
         -> quiesce -> retire
any live state -> fault -> cleanup -> retire
```

Every entered state emits exactly one registry-owned event carrying plugin ID and manifest digest;
verification also carries graph and ceiling digests. Never emit secrets, prompts, raw context, or
private keys. Plugin code cannot mint grants, call the evaluator, or write privileged events.

**Gate:** RF-34–RF-44, complete echo lifecycle and injected-crash lifecycle, event catalog/codegen,
socket permissions, timeout/crash/capability-denial/cleanup tests, and registry-only writer proof.

### Sprint 3.3 — Atomic convergence close

**Implement:** prove all callers, tests, packaging, CI, and living navigation use packages paths;
prove no duplicate parser/writer/reducer/dialect remains. Layer-0 deletion is evidence only after
3.1 and 3.2 are green.

**Gate:** RF-45/NOVA-4, boundary/duplication/stale-path/codegen/secret checks, all production suites,
and zero Layer-0 source/package/test/CI/navigation entries. Until then M-3 stays open and M-4 queued.

### Active verification commands

```bash
python3 -m unittest test.falsifiers.test_rf38_rf45_plugin_lifecycle -v
python3 -m unittest discover -s test/registry -t .
python3 -m unittest test.contracts.test_event_coverage -v
python3 -m unittest discover -s test/packs -t .
PYTHONPATH=tools/common python3 tools/codegen/generate_types.py --check
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/check_duplication.py --enforce
python3 tools/linters/check_stale_paths.py
```

---

## 3. Completed Wave 2C Gate Reference (M-2 / v0.6.1)

Ratified by Engineering Leadership on 2026-08-21 (ADRs [`0077`](../02_decisions/0077-named-component-graph-manifest.md)–[`0086`](../02_decisions/0086-historical-adr-working-tree-consolidation.md)). M-2 re-gate requires both primary gates green.

| Gate | Decision | Falsifier Test | Owner | Status |
|---|---|---|---|---|
| **RF-72 / Identifier Governance** | ADR-0085 | `test/tools/test_check_falsifier_ids.py` | Tooling | **GREEN** (Unit tests + linter pass) |
| **RF-23 / NOVA-1 Trajectory** | ADR-0078 | `test/falsifiers/test_rf23_trajectory_content.py` | Developer A | **GREEN** (Measured, attributable, conserved) |
| **RF-25 / NOVA-2 Continuation** | ADR-0082 | `test/falsifiers/test_rf25_cold_continuation.py` | Developer B | **GREEN** (Cold continuation, lease reconciled) |

> *Note:* RF-24 (cost-writer authority) and RF-27 (digest separation) are supporting assertions under RF-23.

### Immediate File Ownership & Boundaries

- **Developer A (NOVA-1 / RF-23):** Owns `schemas/mhf/trajectory.schema.json`,
  `vanguard/packages/runtime/trajectory.py`, telemetry/model attribution, and the trajectory assembly
  join in `vanguard/packages/runtime/session.py`.
- **Developer B (NOVA-2 / RF-25):** Owns `vanguard/packages/runtime/ledger/recovery.py`, the
  file-backed SQLite-WAL continuation path, and the recovery seam in
  `vanguard/packages/runtime/session.py`.
- **Shared hotspot (`vanguard/packages/runtime/session.py`):** Developer B lands the narrow resume
  seam first; Developer A rebases and joins trajectory assembly.
- **Merge Order:** (1) RF-72 governance lock → (2) Developer B resume seam → (3) Developer A trajectory accounting → (4) Combined M-2 re-gate.

---

## 4. Completed M-2 Implementation Contracts

### Developer A — NOVA-1 / RF-23 (3–4 working days)
- Implement `assemble_trajectory()` over the verified pre-crash prefix plus current-process turns,
  deduplicated by durable event identity and ordered by ledger sequence.
- Populate every turn with an ordered `invocations` sequence covering retries, fallbacks, critic
  calls, and escalations; record resolved model routes and explicit measurement statuses
  (`measured`, `estimated`, `unavailable`).
- Conserve invocation → turn → episode additive costs from adapter telemetry and ledger settlements
  without fabricated zeros.
- Bind final state/event ranges and compute $D_R$ without altering $D_H$.
- Derive legacy/promotability status (never accept from input).
- Preserve legal zero-turn aborted episodes (`model_not_invoked`).
- **Constraint:** Do not add a second accounting store or edit `vanguard/packages/kernel/`.

### Developer B — NOVA-2 / RF-25 (2–3 working days)
- Use file-backed SQLite WAL as the sole state source in a fresh Python interpreter.
- Fold and expose the verified durable event prefix; restore budgets, digests, and sequence state.
- Reconcile every pending Governor lease: release uncommitted reservations or preserve an
  undeterminable reservation until exterior reconciliation, preventing both budget leak and reuse.
- Classify open S8a intent as undeterminable unless exterior reconciliation confirms effect.
- Ledger `RunRecovered` via canonical `LedgerEmitter`.
- Continue execution without repeating settled effects or guessing uncertain ones.
- **Constraint:** Do not transfer live objects, create a second reducer/session, or edit `kernel/`.

---

## 5. Completed Wave 2C Actions
 
- [x] **2C-R25 — Developer B:** Implement fresh-process SQLite-WAL continuation; restore the
  verified durable prefix; reconcile pending Governor leases without budget leakage; preserve open
  effects as undeterminable until reconciliation; emit `RunRecovered` through `LedgerEmitter`; and
  continue without replaying settled effects. Gate: RF-25
  (`test/falsifiers/test_rf25_cold_continuation.py`).
- [x] **2C-R23 — Developer A:** Implement `assemble_trajectory()` over pre-crash history and current
  turns; record ordered `invocations`, resolved model routes, and `measured`/`estimated`/`unavailable`
  status; enforce invocation → turn → episode cost conservation; derive eligibility; and emit the
  complete `mhf.trajectory/1` row. Gate: RF-23
  (`test/falsifiers/test_rf23_trajectory_content.py`), with RF-24 and RF-27 supporting.
- [x] **2C-COMBINED — Developers A + B:** Integrate both seams in
  `vanguard/packages/runtime/session.py`; prove that a recovered episode includes each pre- and
  post-crash event/turn exactly once, carries continuous digest/budget lineage, and produces a
  complete trajectory. Gates: RF-23 and RF-25 green together.
- [x] **2C-REGATE — Tech Lead:** Run the complete M-2 falsifier suite plus all documentation,
  architecture, TCB, isolation, secret, and governance checks; record approval only when every
  command exits 0 and no new `layer0/` or duplicate state surface exists.

Queued work remains non-authoritative here. Its implementation briefs and objective acceptance
gates live in [`milestones.md` § Developer Implementation Briefs](milestones.md#developer-implementation-briefs).

### Definition of Done (All Tasks)
1. Named falsifiers pass on `vanguard/packages/`.
2. All production test suites remain green (`test/kernel`, `test/contracts`, `test/agency`, `test/packs`).
3. Linters pass: `check_boundaries.py`, `check_tcb_budget.py` ($\le 1438$ LOC), `check_domain_blindness.py`, `check_falsifier_ids.py`, `check_markdown_links.py`, `scan_secrets.py`.
4. No new `layer0` imports or duplicated state reducers.

---

## 6. Completed Waves Evidence Summary

| Milestone | Scope | Result | Key Evidence Pointers | Closed Date |
|---|---|---|---|---|
| **M-0 (Wave 0)** | CI Truth & Falsifiers | **PASSED** | CI workflow `ci.yml` measures `vanguard/packages/`; F-01…F-21 registered; codegen checked. | 2026-08-20 |
| **M-1 (Wave 1)** | Trust Spine | **PASSED** | Signed verdicts (`test_signed_verdict.py`), single writer `LedgerEmitter`, typed budgets, complete $D_H$. | 2026-08-21 |
| **M-2 (Wave 2)** | Convergence Core | **PASSED** | Round-4 submission: 56 event kinds catalogued & folded in `reducer.py`, duplicate `layer0/kernel` deleted, `root.py` split into `compose.py`/`session.py`/`wiring.py`. | 2026-08-21 |
| **Wave 2C (M-2 re-gate)** | Evidence Integrity & Cold Recovery | **PASSED** | RF-23 trajectory un-hollowing with conserved costs + RF-25 fresh-process SQLite-WAL continuation green. | 2026-08-23 |

---

## 7. Director Escalation Boundaries

Only the Engineering Director may authorize:
- Altering the Trusted Computing Base (TCB) budget threshold ($\le 1438$ LOC).
- Introducing new event kinds or a sixth SPI protocol.
- Modifying canonicalization (RFC 8785 JCS) or hash algorithms.
- Enabling runtime concurrency prior to the M-7 gate.
- Authorizing release versions post-M-4.
