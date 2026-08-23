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

# Active Sprint Board — v0.6.1 Foundation (M-2 Wave 2C)

**Start here:** [`README.md`](../../README.md) and [`SPEC.md`](../SPEC.md) define production truth and normative law. This board is the **sole living execution authority**.

---

## 1. Wave Status Summary

| Wave | Milestone | State | Focus & Exit Condition |
|---|---|---|---|
| **Wave 0** | M-0 | **CLOSED** | CI subject of record on `vanguard/packages/` + named falsifiers F-01…F-21. |
| **Wave 1** | M-1 | **CLOSED (GREEN)** | Trust spine: signed verdicts, single emitter, typed budgets, complete $D_H$. |
| **Wave 2** | M-2 | **DONE (Round 4)** | Convergence core: absorbed SPI/JSON-RPC/lifecycle, deleted duplicate layer0 kernel. |
| **Wave 2C** | M-2 / v0.6.1 | **OPEN (ACTIVE)** | Evidence integrity: RF-23 (truthful trajectory) + RF-25 (fresh-process SQLite continuation). |
| **Wave 3** | M-3 | **QUEUED** | Extensibility: Named Component Graph (`mhf.manifest/2`), plugin lifecycle FSM. |
| **Wave 4** | M-4 | **QUEUED** | Foundation E2E Stop: One uncheated real coding-agent run with 9 evidence rows. |

---

## 2. Active Wave 2C Execution Gates (M-2 / v0.6.1)

Ratified by Engineering Leadership on 2026-08-21 (ADRs [`0077`](../02_decisions/0077-named-component-graph-manifest.md)–[`0086`](../02_decisions/0086-historical-adr-working-tree-consolidation.md)). M-2 re-gate requires both primary gates green.

| Gate | Decision | Falsifier Test | Owner | Status |
|---|---|---|---|---|
| **RF-72 / Identifier Governance** | ADR-0085 | `test/tools/test_check_falsifier_ids.py` | Tooling | **GREEN** (Unit tests + linter pass) |
| **RF-23 / NOVA-1 Trajectory** | ADR-0078 | `test/falsifiers/test_rf23_trajectory_content.py` | Developer A | **RED CONFIRMED — IN PROGRESS** |
| **RF-25 / NOVA-2 Continuation** | ADR-0082 | `test/falsifiers/test_rf25_cold_continuation.py` | Developer B | **RED CONFIRMED — IN PROGRESS** |

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

## 3. Implementation Contracts

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

## 4. Wave 2C Actionable TODO

- [ ] **2C-R25 — Developer B:** Implement fresh-process SQLite-WAL continuation; restore the
  verified durable prefix; reconcile pending Governor leases without budget leakage; preserve open
  effects as undeterminable until reconciliation; emit `RunRecovered` through `LedgerEmitter`; and
  continue without replaying settled effects. Gate: RF-25
  (`test/falsifiers/test_rf25_cold_continuation.py`).
- [ ] **2C-R23 — Developer A:** Implement `assemble_trajectory()` over pre-crash history and current
  turns; record ordered `invocations`, resolved model routes, and `measured`/`estimated`/`unavailable`
  status; enforce invocation → turn → episode cost conservation; derive eligibility; and emit the
  complete `mhf.trajectory/1` row. Gate: RF-23
  (`test/falsifiers/test_rf23_trajectory_content.py`), with RF-24 and RF-27 supporting.
- [ ] **2C-COMBINED — Developers A + B:** Integrate both seams in
  `vanguard/packages/runtime/session.py`; prove that a recovered episode includes each pre- and
  post-crash event/turn exactly once, carries continuous digest/budget lineage, and produces a
  complete trajectory. Gates: RF-23 and RF-25 green together.
- [ ] **2C-REGATE — Tech Lead:** Run the complete M-2 falsifier suite plus all documentation,
  architecture, TCB, isolation, secret, and governance checks; record approval only when every
  command exits 0 and no new `layer0/` or duplicate state surface exists.

Future work is intentionally absent from this live board. Ordered Sprint 3.1+ backlog and objective
acceptance gates live in [`milestones.md` § Future Backlog](milestones.md#future-backlog-by-milestone-and-sprint).

### Definition of Done (All Tasks)
1. Named falsifiers pass on `vanguard/packages/`.
2. All production test suites remain green (`test/kernel`, `test/contracts`, `test/agency`, `test/packs`).
3. Linters pass: `check_boundaries.py`, `check_tcb_budget.py` ($\le 1438$ LOC), `check_domain_blindness.py`, `check_falsifier_ids.py`, `check_markdown_links.py`, `scan_secrets.py`.
4. No new `layer0` imports or duplicated state reducers.

---

## 5. Completed Waves Evidence Summary

| Milestone | Scope | Result | Key Evidence Pointers | Closed Date |
|---|---|---|---|---|
| **M-0 (Wave 0)** | CI Truth & Falsifiers | **PASSED** | CI workflow `ci.yml` measures `vanguard/packages/`; F-01…F-21 registered; codegen checked. | 2026-08-20 |
| **M-1 (Wave 1)** | Trust Spine | **PASSED** | Signed verdicts (`test_signed_verdict.py`), single writer `LedgerEmitter`, typed budgets, complete $D_H$. | 2026-08-21 |
| **M-2 (Wave 2)** | Convergence Core | **PASSED** | Round-4 submission: 56 event kinds catalogued & folded in `reducer.py`, duplicate `layer0/kernel` deleted, `root.py` split into `compose.py`/`session.py`/`wiring.py`. | 2026-08-21 |

---

## 6. Director Escalation Boundaries

Only the Engineering Director may authorize:
- Altering the Trusted Computing Base (TCB) budget threshold ($\le 1438$ LOC).
- Introducing new event kinds or a sixth SPI protocol.
- Modifying canonicalization (RFC 8785 JCS) or hash algorithms.
- Enabling runtime concurrency prior to the M-7 gate.
- Authorizing release versions post-M-4.
