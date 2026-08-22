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
last_verified: 2026-08-21
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

Ratified by Engineering Leadership on 2026-08-21 (ADRs [`0077`](../05_adr/0077-named-component-graph-manifest.md)–[`0086`](../05_adr/0086-historical-adr-working-tree-consolidation.md)). M-2 re-gate requires both primary gates green.

| Gate | Decision | Falsifier Test | Owner | Status |
|---|---|---|---|---|
| **RF-72 / Identifier Governance** | ADR-0085 | `test/tools/test_check_falsifier_ids.py` | Tooling | **GREEN** (Unit tests + linter pass) |
| **RF-23 / NOVA-1 Trajectory** | ADR-0078 | `test/falsifiers/test_rf23_trajectory_content.py` | Developer A | **RED CONFIRMED — IN PROGRESS** |
| **RF-25 / NOVA-2 Continuation** | ADR-0082 | `test/falsifiers/test_rf25_cold_continuation.py` | Developer B | **RED CONFIRMED — IN PROGRESS** |

> *Note:* RF-24 (cost-writer authority) and RF-27 (digest separation) are supporting assertions under RF-23.

### Immediate File Ownership & Boundaries
- **Developer A (NOVA-1 / RF-23):** Owns `schemas/mhf/trajectory.schema.json`, `runtime/trajectory.py`, telemetry/model attribution, and the trajectory assembly join in `runtime/session.py`.
- **Developer B (NOVA-2 / RF-25):** Owns `runtime/ledger/recovery.py`, the file-backed SQLite-WAL continuation path, and recovery-facing construction in `runtime/session.py`.
- **Shared Hotspot (`runtime/session.py`):** Developer B lands the narrow resume seam first; Developer A rebases and joins trajectory assembly.
- **Merge Order:** (1) RF-72 governance lock → (2) Developer B resume seam → (3) Developer A trajectory accounting → (4) Combined M-2 re-gate.

---

## 3. Implementation Contracts

### Developer A — NOVA-1 / RF-23 (3–4 working days)
- Populate `mhf.trajectory/1` with real model routes, explicit measurement statuses (`measured`, `estimated`, `unavailable`), and turn-level attribution.
- Conserve episode-level cost totals from adapter telemetry without fabricated zeros.
- Bind final state/event ranges and compute $D_R$ without altering $D_H$.
- Derive legacy/promotability status (never accept from input).
- Preserve legal zero-turn aborted episodes (`model_not_invoked`).
- **Constraint:** Do not add a second accounting store or edit `vanguard/packages/kernel/`.

### Developer B — NOVA-2 / RF-25 (2–3 working days)
- Use file-backed SQLite WAL as the sole state source in a fresh Python interpreter.
- Fold durable event prefix, restore budgets/digests/sequence state.
- Classify open S8a intent as undeterminable unless exterior reconciliation confirms effect.
- Ledger `RunRecovered` via canonical `LedgerEmitter`.
- Continue execution without repeating settled effects or guessing uncertain ones.
- **Constraint:** Do not transfer live objects, create a second reducer/session, or edit `kernel/`.

---

## 4. Unified Task Register

| ID | Task | Falsifier / Gate | Readiness | Owner |
|---|---|---|---|---|
| **2C-R23** | NOVA-1: Truthful trajectory content and conserved accounting | RF-23 (`test_rf23_trajectory_content.py`) | **RED CONFIRMED** | Developer A |
| **2C-R25** | NOVA-2: True fresh-process SQLite-WAL cold continuation | RF-25 (`test_rf25_cold_continuation.py`) | **RED CONFIRMED** | Developer B |
| **2C-REGATE** | Run full M-2 gate suite; obtain Tech Lead signature | All M-2 gates green | BLOCKED (on 2C-R23/25) | Tech Lead |
| **3.1-A** | Registry FSM on packages with ledgered transitions | RF-38…RF-45 | QUEUED (needs M-2) | Unassigned |
| **3.1-B** | Manifest compiler for Named Component Graph | RF-28…RF-33 | QUEUED (needs M-2) | Unassigned |
| **3.1-C** | Echo plugin lifecycle over wire (ADR-M0-13) | RF-38 | QUEUED (needs M-2) | Unassigned |
| **4.1-A** | Foundation E2E uncheated run (9 evidence rows) | M-4 Gate | QUEUED (needs M-3) | Unassigned |

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
