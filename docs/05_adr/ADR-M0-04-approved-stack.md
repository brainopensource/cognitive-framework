---
adr: M0-04
title: "Approved stack (from VG-02 §9)"
status: accepted
---

# ADR-M0-04: Approved stack (from VG-02 §9)

**Decision.** Carry forward the charter's approved-stack decisions: Python 3.11+ stdlib-only
core (`kernel/`, `domain/`, `agency/`, `runtime/`), TypeScript/Ink CLI client consuming
**generated** readers only (never hand-written TS domain logic, per AP-6 and ADR-0063), SQLite WAL
event store, RFC 8785 JCS canonicalisation, Ed25519 signing for the exterior evaluator.

**Context.** `docs/01_specs/backend/02_vanguard_charter_claims_and_non_claims_v040.md` §9. These
choices are already load-bearing in shipped code (`ADR-0063` reversed the original TypeScript
control-plane decision on evidence); this ADR just carries the surviving stack decisions into the
v0.5.0 register under the `ADR-M0-*` namespace so they are citable without archaeology.

**Reversal condition.** Per sub-decision — see the individual VG-09 ADRs this supersedes
(notably `0063`).
