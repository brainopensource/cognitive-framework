# Milestones — v0.6 Foundation (Wave 0 → Wave 4)

**Status:** Living execution ladder under the authority of
[`002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md)
(outcomes + falsifiers) and ADRs `0069`–`0076`. This file adds the execution decomposition:
milestones → sprints → dependencies. Sprint detail: [`../03_sprints/plans/`](../03_sprints/plans/).
Replaces the historical M0–M6 ladder (removed; git history `4f9f8b1`), whose gates contradicted the
lock (mid-run hot-swap, E-COV=100%, layer0 destination).

**No calendar dates.** A milestone is complete when its falsifiers pass on the canonical path —
never when its code merges.

| Milestone | Wave | Outcome | Exit gate (objective evidence) | Depends on |
|---|---|---|---|---|
| **M-0 Engineering truth** | 0 — **COMPLETE** | Living CI measures `vanguard/packages/` and the named falsifiers | `002` §3 Wave-0 gate: production suites in CI; F-01…F-21 exist as tests (red allowed); codegen `--check` wired; F-19/F-20 hygiene closed | Director approval (done, ADR-0075) |
| **M-1 Trust spine** | 1 — **COMPLETE (GREEN)** | Unforgeable evidence, provable state, complete identity, typed budgets, real trajectories | F-01…F-15 green **on the canonical path**; suites of record green; TCB 1359 ≤ 1438 | M-0 |
| **M-2 One runtime** | 2 — **OPEN** | `layer0/` absorbed and deleted; one wire, one algebra, one writer; `root.py` split in place | F-16 green; zero `layer0` imports; `layer0/` removed after parity; no behavior change in `test/runtime` | M-1 |
| **M-3 Extensibility** | 3 — QUEUED (entry: M-2) | Plugin lifecycle real on the canonical path; pack loads through it; kernel domain-blind everywhere | ADR-M0-13 echo-plugin gate; F-18-extended I-7 linter green; freeze-at-compose negatives | M-2 |
| **M-4 Foundation E2E — STOP** | 4 | One real coding-agent run through the whole substrate with trustworthy state + evidence | The nine-row table in [`wave4_foundation_e2e.md`](../03_sprints/plans/wave4_foundation_e2e.md) on one run | M-1, M-2, M-3 |

## Sprint map

```text
M-0  (Wave-0 team)                      M-1                                M-2                      M-3                    M-4
 CI + falsifiers ──────┬─▶ 1.1 signed-verdict loop ──┐
                       ├─▶ 1.2 ledger truth ─────────┼─▶ 1.3 identity+budget+trajectory ─▶ 2.1 absorb wire ─▶ 2.2 parity+delete+split ─▶ 3.1 walking skeleton ─▶ 3.2 pack on wire ─▶ 4.1 one real run
                       └────────(1.1 ∥ 1.2)──────────┘
```

## Standing constraints (from the lock; not renegotiable per-sprint)

Sequential scheduler (I-11) · TCB LOC ceiling · no third tree · no hot-swap · evaluator exterior ·
domain-blind kernel (I-7) · one generated type source (A-4/I-1) · measurement stays outside
`vanguard/packages/` · everything in SPEC §9's refusal list.

## Post-foundation (not planned here, deliberately)

Extra packs · controlled concurrency (measurement-gated) · multi-agent policy · lab promotion ·
Meta-Harness/DPO — see `002` §2 deferred table. Anything here entering a Wave 1–4 sprint is a
scope defect.
