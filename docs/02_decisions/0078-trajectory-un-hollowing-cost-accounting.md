---
adr: 0078
title: "Trajectory un-hollowing and conserved cost accounting (NOVA-1)"
status: accepted
accepted_date: 2026-08-21
source_section: "ALFA Tier S+ Director Ratification"
implementation_milestone: "M-2 / v0.6.1"
---

# ADR-0078: Trajectory un-hollowing and cost accounting (NOVA-1)

**Context.** `runtime/trajectory.py` emits `_ZERO_COST` for every invoked turn and episode and
omits execution/model identity even though `mhf.trajectory/1` validates. Existing F-12 proves key
presence, including the valid zero-turn aborted case; it does not prove that an invoked trajectory
is attributable or economically truthful. A schema-valid hollow row cannot support routing,
memoization, DPO, or promotion and violates I-9's harvest-row intent.

**Decision.**

1. Keep the wire identifier **`mhf.trajectory/1`** for M-2. Strengthen its content contract and
   compatibility reader; do not introduce a breaking `/2` identifier before M-4.
2. Delete `_ZERO_COST` assembly. Every invoked turn records its context digest/ref policy,
   proposal, causally associated effects and receipts, provider/model identity, fingerprint or
   explicit fingerprint-unavailable reason, prompt/completion/cache token accounting, charged
   milliseconds, bytes, and USD-micro status.
3. Measurements distinguish `measured`, `estimated`, and `unavailable`. Unavailable carries a
   bounded reason and is never represented as a fabricated zero. A genuinely free route may have
   measured `usd_micros = 0`; another measured dimension must establish that invocation occurred.
4. Cost authority comes from ledgered budget settlements, receipts, and measurements produced at
   the owning adapter boundary. Planners, plugins, and model prose cannot author settled cost.
5. For each additive dimension `d`, episode accounting satisfies
   `total[d] = sum(turn[d]) + sum(explicit_non_turn_charge[d])` when every operand is available.
   If any operand is unavailable, the episode dimension is unavailable with a reason. Structural
   ceilings `turns` and `depth` are not costs.
6. `millis` is charged compute time, not concurrent wall time. The distinction is recorded now
   even while I-11 keeps execution sequential.
7. `execution_digest` computes `D_R` according to ADR-0071 from `D_H`, runtime, environment,
   ordered model identities, and oracle identity. Experiment records compute `D_X` from `D_R`,
   dataset, and protocol. Neither may be substituted for `D_H`.
8. The row binds the final ledger event range, state digest, outcome, and signed verdict or a typed
   verdict-absence reason. Null is not pass.
9. Historical or incomplete rows are not rewritten. Readers derive `legacy_incomplete` and
   `unattributable_for_promotion`; neither flag is author-writable. Such rows remain auditable but
   cannot seed memoization, preference pairs, training, or promotion.
10. NOVA-1 is an immediate M-2 correction. The previous Wave-4 carry-out is superseded.

**Primary bound falsifier — RF-23.** A completed scripted episode with at least one model
invocation must emit a populated, schema-valid `/1` row: turn count agrees with ledger proposals;
identity and measurement status are present; at least one measured additive dimension is positive;
per-dimension totals reconcile; `D_R` and `D_X` have their proper subjects; and the row is not
derived legacy/ineligible. Supporting negatives RF-24 and RF-27 pin cost-writer authority and
digest separation, but RF-23 is the M-2 board gate.

**Alternatives rejected.** Treating zeros as “unknown”; requiring positive USD for local models;
rewriting old WAL rows; allowing provider prose to settle costs; or waiting until a learner exists.

**Reversal condition.** Measured evidence that attribution/accounting overhead materially changes
the behavior it measures, followed by a newer ADR defining an equally truthful lower-overhead
contract. Learner tolerance of hollow rows is not reversal evidence.

**Owner · status.** CIO / Runtime Lead · accepted by Engineering Director · 2026-08-21

---

## Amendment — 2026-08-23: ordered invocations and recovered-prefix accounting

1. A turn contains an ordered `invocations` sequence. Retries, fallbacks, critic calls, and
   escalations are separate entries with their resolved route, provider/model identity, fingerprint
   or typed absence reason, measurement status, and additive cost.
2. Cost conservation is hierarchical: invocation totals reconcile to the turn; turn totals plus
   explicit non-turn charges reconcile to the episode. Any unavailable operand makes the enclosing
   dimension unavailable with a bounded reason; it never becomes zero.
3. After RF-25 recovery, `assemble_trajectory()` joins the verified durable pre-crash event prefix
   with post-recovery turns exactly once, in ledger order. Truncating the prefix or double-counting a
   recovered turn violates I-9 and RF-23.
