---
adr: M0-11
title: "Sink-class mediation: all effects recorded, only PRIVILEGED capability-mediated"
status: accepted
---

# ADR-M0-11: Sink-class mediation: all effects recorded, only PRIVILEGED capability-mediated

**Decision.** All effects are recorded to the ledger for attribution; only `PRIVILEGED`-sink
effects are capability-mediated (require a descriptor-bound grant through kernel S6). Sink class
(`OBSERVATION | ADVISORY | PRIVILEGED`) is a descriptor field, not an implicit property of the verb.

**Context.** This is `ADR-0051`'s content verbatim, matching as-built drift D-04
("`[OPTIMIZATION]` — all three sink classes still traverse dispatch and are recorded; only
privileged take S6. Amend VG-02 `A-03` rather than revert") and correction 2 in
`docs/01_specs/backend/13_C_gts_mvp_program_and_engineering_plan.md`'s `corrections_from_13B`.
Universal mediation was rejected because pure/observation effects would add TCB and dispatch
latency without a corresponding authority gain; universal *recording* is kept because attribution
requires it regardless of sink class.

**Reversal condition.** Evidence that non-privileged recording costs exceed attribution value, or
that observation-sink effects enable a real escalation path (per `ADR-0051`'s own reversal
condition, carried forward unchanged).
