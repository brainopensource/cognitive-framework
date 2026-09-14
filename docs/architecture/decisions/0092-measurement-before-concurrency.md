---
id: adr-0092-measurement-before-concurrency
adr: "0092"
class: decision
authority: binding-decision
canonical_for:
  - decision-0092-measurement-before-concurrency
status: living
owner: engineering-director
version: "1.0"
last_verified: 2026-09-13
decision_status: accepted
---

# ADR-0092 — Measurement before concurrency

This restores the accepted 2026-08-24 decision from Git `a694ba8f2d2b6f7148e45b64de4e10226aeec725:docs/02_decisions/0092-review-bundle-disposition-and-m7-measurement.md`.
The reviewed m456 bundle remained non-authoritative input, its proposed context-store rewrite was rejected by the observed residency evidence, and useful behavior could enter production only through a fresh bounded implementation in the canonical lattice.
M7-01 was authorized for sequential effect-log measurement and analysis, not a scheduler, concurrency, leases or topology engine, with unresolved resource relationships counted against demonstrated independence.
Below 30 percent measured independence the original default director disposition was cancel advanced scheduling and retain I-11; at or above that threshold a successor decision still needed speedup and contention evidence before authorizing concurrency.
A threshold observation is thus a decision input rather than permission, and this restoration neither changes subsequent topic-specific dispositions nor reactivates old milestone scheduling.
[The surviving test module](../../../test/falsifiers/test_m7_topology_and_independence.py) now raises `SkipTest` because `lab/` was withdrawn, so it supplies historical traceability but no current measurement or passing gate.
