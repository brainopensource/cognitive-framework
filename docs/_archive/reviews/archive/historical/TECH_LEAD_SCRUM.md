# TECH_LEAD_SCRUM.md — Execution Contract, M-2 → M-10

**Owner:** Tech Lead · **Status:** ACTIVE · **Date:** 2026-08-21 · **Baseline:** v0.6.1 lock (ADRs `0077`–`0085` filed)

> **Authority.** This document **creates no law and states no new requirement.** It is an execution
> aid. Law is `docs/SPEC.md` → `docs/05_adr/` → `docs/04_annex/`. The living board is
> `docs/03_sprints/sprint_active.md`. Outcomes are `docs/07_reviews/…/002_…GAP_REGISTER.md`.
> **If this file ever disagrees with an ADR, the ADR wins and this file is wrong.**
>
> **Anti-drift rule for this file itself:** it may be edited only to (a) tick a row done, (b) record
> a gate result, or (c) correct a divergence from an ADR. **Adding scope here is drift.**

---

## 0 · The one rule

> **Build exactly the row you are on. Nothing from a later row. No exceptions without a Director escalation.**

Every row below has an **entry gate**, a **closed scope**, an **explicit out-of-scope list**, and an
**exit gate that is a test, not an opinion**. A row is done when its named falsifiers are green on
the canonical `vanguard/packages/` path — never when code merges, and never by lexical grep.

---

## 1 · The ladder

```
┌────┬───────────────────┬────────────────────────────────┬──────────────────┬────────────────────────────┬─────────────────────┐
│ #  │ MILESTONE · VER   │ DEVELOPMENT                    │ LAYER            │ CAPABILITY UNLOCKED        │ EXIT GATE           │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 1  │ NOW · Sprint 2.2  │ Write RF-23 and RF-25 red      │ tests + docs     │ Unambiguous targets        │ Both fail, for the  │
│    │                   │ Fix RF-73/74 clash             │                  │                            │ intended reason     │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 2  │ M-2 · v0.6.1      │ NOVA-1 rich trajectory         │ runtime          │ Trustworthy learning       │ RF-23 + RF-25 green │
│    │                   │ NOVA-2 true WAL cold resume    │ adapters         │ corpus; durable recovery   │                     │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 3  │ M-3 · v0.6.2      │ Component Graph; plugin FSM    │ domain · agency  │ Plugins and reusable       │ RF-28…RF-45         │
│    │                   │ parity; absorb; kill layer0/   │ runtime          │ multi-agent topologies     │ + NOVA-4            │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 4  │ M-4 · v0.6.3      │ One uninterrupted real run     │ integration      │ First trustworthy          │ ███ STOP LINE ███   │
│    │                   │ producing nine verified rows   │                  │ end-to-end evidence        │ + RF-49             │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 5  │ M-5 · v0.7.0      │ Math pack; witness memo;       │ packs            │ Domain neutrality;         │ RF-50 · RF-51       │
│    │                   │ documentation collapse         │ runtime cache    │ deterministic cost cut     │ RF-52 · RF-53       │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 6  │ M-6 · v0.8.0      │ Capability-mediated            │ kernel ≤ 40 LOC  │ Safe recursion, hierarchy, │ RF-55…RF-59         │
│    │                   │ agent.spawn through S0–S12     │ agency           │ tree search                │ TCB ≤ 1438          │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 7  │ M-7 · v0.9.0      │ Bounded concurrency; adaptive  │ runtime          │ Dynamic cost/token/        │ RF-60…RF-64         │
│    │                   │ Pareto routing                 │ scheduler        │ latency/quality control    │ I-11 lifted by ADR  │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 8  │ M-8 · v0.9.x      │ Debate, critic/reviser, search │ manifests · apps │ New agent structures with  │ RF-65 · RF-66       │
│    │                   │ topologies; harness CLI/SDK    │                  │ no engine change           │                     │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 9  │ M-9 · pre-v1.0    │ Rebuildable retrieval, memory, │ ports · adapters │ Search, reusable knowledge,│ RF-77 + published   │
│    │                   │ skills, scale measurements     │                  │ measured scaling           │ measurements        │
├────┼───────────────────┼────────────────────────────────┼──────────────────┼────────────────────────────┼─────────────────────┤
│ 10 │ M-10 · v1.0.0     │ Macro-tool compilation, DPO    │ exterior/offline │ Auditable compounding      │ Exact paired eval   │
│    │                   │ harvest, promotion + rollback  │ pipelines        │ self-improvement           │ + human promotion   │
└────┴───────────────────┴────────────────────────────────┴──────────────────┴────────────────────────────┴─────────────────────┘
```

**Two invariants hold this shape:**

1. **Nothing in rows 6–10 begins before row 4 is green.** The M-4 stop line is Director-owned.
2. **`kernel/` is touched exactly once — row 6.** Everything else enters as pack, plugin, manifest,
   adapter, policy, or offline pipeline. A change that cannot enter that way is an architecture
   change and needs an ADR before an estimate (`ADR-0085` §4.1).

---

## 2 · Row 1 — DO THIS NOW (½ day, then stop)

**Scope is closed. This row authorizes no production code.**

| Task | File | Done when |
|---|---|---|
| **1.1** Renumber the profiles/spawn inert-state tests | `docs/05_adr/0077-…md` amendment | Cites `RF-78`/`RF-79`, not `RF-73`/`RF-74` — those are taken by `ADR-0085` §10 |
| **1.2** Correct the stale numbering note | `docs/05_adr/0085-…md` header | No longer says `0077`–`0084` are "drafted, not yet filed" |
| **1.3** Write **`RF-23`** RED | `test/falsifiers/test_rf23_trajectory_content.py` | Fails on `_ZERO_COST`, **not** on an import error or a missing fixture |
| **1.4** Write **`RF-25`** RED | `test/runtime/test_cold_continuation.py` | Fails on live-object dependency, **not** on a missing helper |
| **1.5** Register both | `002` §4.2b + `sprint_active.md` | Rows exist with owner and gate |

> **`RF-23` must observe a *completed* episode with ≥ 1 turn.** Today's `F-12`
> (`test/falsifiers/test_falsifiers.py:363`) drives an **aborted, zero-turn** episode and asserts key
> presence only — it can never see `_ZERO_COST`. That is the false green being replaced. The same
> test name also exists at `test/runtime/test_ledger_truth.py:358`; fix both.

**Acceptance for row 1:** two tests on disk, both red, each failing for the reason it was written to
catch. **A test that fails because it cannot import is not a red falsifier — it is a broken test.**

---

## 3 · Row 2 — M-2 execution contract

**Entry:** row 1 complete. **Exit:** `RF-23` and `RF-25` green + the M-2 board gate.

| ID | Task | Files | Gate |
|---|---|---|---|
| `W2-N1` | **NOVA-1** — delete `_ZERO_COST`; fold per-turn cost from ledgered `BudgetCommitted`/`Receipt.cost` and adapter usage; emit `D_R`; add `measurement_status` ∈ {measured, estimated, unavailable} + reason; `verdict_absent_reason` | `runtime/trajectory.py`, `runtime/session.py`, `adapters/models/*`, `schemas/mhf/trajectory.schema.json` | `RF-23`, `RF-24`, `RF-27` |
| `W2-N2` | **NOVA-2** — SIGKILL mid-turn → fresh interpreter → cold fold → reconcile → resume → complete | new `test/runtime/test_cold_continuation.py`, `runtime/recovery.py` | `RF-25` |
| `W2-N3` | **NOVA-3** — `_PROC_PATTERN` read from the compiled ceiling | `adapters/models/planner.py` | `RF-71` |
| `W2-D1` | Adjudicate the 6 currently-red tests as **product drift** or **environment sensitivity**, one bounded reason each | board record | Tech Lead sign-off |
| `W2-B1` | SPEC §1.2 (56→58) · §5.3 (VFE/EFE) · §7 (trajectory + `D_R`) · I-9/I-11 | `docs/SPEC.md` | Links green |

**Out of scope in M-2, explicitly:** any `kernel/` diff beyond tests · any plugin-lifecycle work ·
`mhf.manifest/2` *implementation* · router activation · memoization · any `layer0/` deletion beyond
2.2-B's authorized scope · SPEC §1.4 and §2.3 (they describe code that does not exist).

> **The data is already in the function's arguments.** `assemble_trajectory` receives `events` and
> `receipts` and discards them at lines 53 and 75. NOVA-1 is wiring, not new machinery. If it starts
> looking like new machinery, stop and escalate.

**Hard branch at M-2 exit:**
- **`RF-25` GREEN** → M-3 opens. M-7 is scoped as a scheduling refactor.
- **`RF-25` RED** → **M-3 does not open.** M-7 is a rewrite; re-scope it *before* building
  abstractions on a false premise. This is the whole reason the test exists.

---

## 4 · Rows 3–10 — standing contracts

Each row is expanded into sprint tasks **only when the previous row's gate is green.**
Detailing unstarted work is waste (`ADR-0085` §3.5).

| Row | Do not start until | Closed scope reference | Explicitly out of scope |
|---|---|---|---|
| **3 · M-3** | `RF-25` green | `ADR-0077`, `ADR-0079`, `ADR-0081`, `ADR-0083` (schema only) | WASM tier · mandatory plugin signatures · any second product plugin · spawn implementation · **router activation** |
| **4 · M-4** | M-3 gate green | `002` §3 Wave 4 | Any scope widening to make the run pass — **escalate instead** |
| **5 · M-5** | **Director attests** the M-4 evidence | `ADR-0084` T0 · Pack #2 | T1–T3 compounding · concurrency |
| **6 · M-6** | M-5 green + `ADR-0080` cl.1 released | `ADR-0080` | Parallel scheduler |
| **7 · M-7** | M-6 green + `RF-25` at scale | `ADR-0083` activation | Framework mutation |
| **8 · M-8** | M-6 + M-7 green | `ADR-0082` cl.2 | Automatic promotion |
| **9 · M-9** | M-8 green | `ADR-0082` cl.10 (SPI review) | Live self-improvement |
| **10 · M-10** | M-8 + M-9 green | `ADR-0084` T1–T3 | In-place self-modification |

---

## 5 · Standing prohibitions (reject the PR if any is true)

- Any `vanguard/packages/kernel/` diff before **row 6**, except tests. *A kernel diff inside the M-4
  window voids the evidence bundle.*
- TCB above **1438** logical LOC, or a ceiling raised to fit an implementation.
- A second selector algebra, canonicalisation, writer, manifest parser, event store, or episode driver.
- A cost field authored by a planner, plugin, or model adapter.
- A fabricated zero where the value is unknown — use `measurement_status: unavailable` + reason.
- `unattributable_for_promotion` or `legacy_incomplete` written by a manifest or plugin. **Derived only.**
- A `VerdictRecorded` from anything but `runtime/evaluator_gateway.py`.
- An FSM transition that emits no event.
- `depth` or `turns` inside a `CostVector`; sibling depths summed; a child with an independent wallet.
- Anything resolving at runtime that must fail at compose (unknown ref, dangling endpoint, empty ceiling).
- A graph rejected merely for containing a cycle — **cycles are legal** (`ADR-0077` cl.3).
- A ticket citing `docs/07_reviews/` or `docs/06_references/` as a requirement.
- A wave declared green by grep. **Honest red is acceptable; lexical green is not.**

---

## 6 · Definition of Done — every ticket

1. Its named `RF-nn` passes on the canonical `vanguard/packages/` path.
2. Suites of record stay green: `test/kernel`, `test/contracts`, `test/agency`, `test/packs`,
   `test/falsifiers`, `test/trust`, `test/security`, `test/registry`, `test_ledger_truth`.
3. Linters green: `check_boundaries` · `check_tcb_budget` · `check_domain_blindness` ·
   `check_isolation_policy` · `check_duplication --enforce` · `check_event_coverage` ·
   `check_stale_paths` · `check_markdown_links` · `scan_secrets`.
4. No new `layer0` import.
5. Trajectory, envelope, and verdict shapes validate against `schemas/mhf/`.
6. **Exactly one `RF-nn` is named on the ticket.** Zero means the decision was never made — escalate.

---

## 7 · Ceremony

| Cadence | Ritual | Question that must be answered |
|---|---|---|
| Daily | Standup | *"Which `RF-nn` did you move, and is it still red for the right reason?"* |
| Per PR | Review | §5 prohibitions checked; §6 DoD checked; one `RF-nn` named |
| Per row | **Gate review** | Falsifiers run **live** in the review, not quoted from a prior run |
| Row 4 only | **Stop-line review** | Director attests all nine rows share one `run_id`. No stitching, no cassette substitution, no equivalent demo |

**Gate reviews are adversarial by design.** The reviewer's job is to make the falsifier fail. If it
cannot be made to fail, the row is done.

---

## 8 · Escalate to the Director — never decide locally

New event kinds · a sixth SPI · a kernel LOC ceiling change · a second digest or canonicalisation
algorithm · concurrency enablement · **router activation before M-7** · any `agent.spawn`
implementation before M-6 · a manifest schema version bump · a falsifier-namespace change · **any
change to the nine-row M-4 gate** · anything on the `SPEC.md` §9 refusal list · **any request to
widen scope so a gate passes.**

---

## 9 · What this file is not

It is not a plan for M-5 through M-10, not a specification, and not a requirement source. It is the
order of work and the list of things that are not the order of work. **When row 4 is green, delete
rows 1–4 from this file and expand row 5 — not before.**

*Companion documents: `docs/03_sprints/sprint_active.md` (living board) · `docs/05_adr/INDEX.md`
(law) · `docs/07_reviews/…/002_…GAP_REGISTER.md` (outcomes and falsifiers).*
