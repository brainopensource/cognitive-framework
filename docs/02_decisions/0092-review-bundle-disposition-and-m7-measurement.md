---
id: adr-0092-review-bundle-disposition-and-m7-measurement
adr: 0092
class: decision
authority: binding-decision
canonical_for:
  - m456-review-bundle-disposition
  - m7-effect-log-measurement-authorization
status: accepted
owner: engineering-director
version: "0.6.4"
last_verified: 2026-08-24
accepted_date: 2026-08-24
extends:
  - ADR-0088
  - ADR-0090
supersedes: []
superseded_by: null
---

# ADR-0092 — Review-bundle disposition and M-7 measurement authorization

## Context

The tracked `docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/`
bundle contains useful prototypes and tests, but also parallel `runtime/`,
`adapters/`, and evidence modules. Wiring those modules into production would
restore the competing authority eliminated by M-3C Gate G4 and, in places,
would invert the enforced adapter boundary.

The bundle's context-residency premise was also falsified: current context
assembly retained 7,375 resident bytes for 59,000 logical bytes (1.00x against
the reference arm), not the claimed 11x duplication. No context-store rewrite
is justified.

M-7 still needs an observed sequential effect log before any concurrency
decision can be made.

## Decision

1. The entire `m456` bundle remains archived, non-authoritative review input.
   It must not be imported, packaged, or placed on a production execution path.
   A useful behavior may land only as a fresh, bounded implementation in the
   canonical lattice, against an allocated falsifier and existing authority.
2. The context-store optimization is rejected. The permanent residency
   falsifier remains; it may be reconsidered only if measured resident growth
   materially exceeds the reference arm.
3. M7-01 is authorized as measurement-only work after this stabilization patch.
   It must construct effect references from sequential ledger
   `EffectStarted` records containing resolved resources and must capture sink,
   idempotency key, wall/model/tool timing, and cache-hit rate over a fixed-seed
   task set.
4. M7-01 may add capture, analysis, deterministic fixtures, and a reproducible
   runner. It may not add a scheduler, concurrency, leases, claim TTLs, or a
   topology engine, and it does not lift I-11.
5. The measured independent fraction is a decision input, not an authorization.
   Below 30%, the default Director decision is to cancel M-7 and retain I-11.
   At or above 30%, a successor ADR must still quantify attainable speedup and
   contention cost before concurrency can be authorized.

## Consequences

M-4 remains active, M-5 and M-6 remain locked, and M-7 implementation remains
locked. The next branch may perform M7-01 measurement in parallel with external
M-4 environment qualification because it cannot mutate execution semantics.

