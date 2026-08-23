---
adr: 0083
title: "Dynamic Pareto controller and alpha-to-delta profile matrix"
status: accepted
accepted_date: 2026-08-21
source_section: "ALFA Tier S+ Director Ratification"
implementation_milestone: "schema M-3; activation M-7 / v0.9.0"
implementation_status: deferred
---

# ADR-0083: Dynamic Pareto controller (`alpha` through `delta`)

**Context.** Cost, tokens, charged latency, and signed quality cannot be reduced safely to one
global scalar. Current tier escalation is a useful seed but is not a fully attributable,
composition-declared controller. Hard-coded latency/token bands would age quickly; leaving routing
outside `D_H` would make experiments irreproducible.

**Decision.**

1. The four reference profiles are manifest policy conventions:

   | Profile | Objective prior | Initial strategy | Escalation |
   |---|---|---|---|
   | `alpha` | Minimize latency/cost under the required witness floor. | Memo/macro, then one economical worker. | Verifier failure, explicit ambiguity, or low calibrated confidence. |
   | `beta` | Minimize expected cost per signed pass. | Focused context/scout, one executor, exterior oracle. | Add the option with best expected marginal value. |
   | `gamma` | Maximize assurance within the authorized ceiling. | Independent candidates, critic/proof/adversarial evaluation. | Spend on disagreement resolution, not repetitive prose. |
   | `delta` | Begin with the cheapest feasible policy and re-plan from evidence. | Dynamic. | Each escalation obtains a new reservation debited from the same root/episode budget. |

2. Profile weights, ceilings, topology preset, calibration identity, and escalation policy are
   versioned composition data and enter `D_H`. Numeric bands are pack configuration, not law or
   product promises.
3. Selection is lexicographic: authority/selector/isolation/evidence/safety; reservation and
   dependency feasibility; witness floor; Pareto nondominance over expected pass, information
   value, cost, tokens, latency, and risk; then declared product preference.
4. Raw vectors, constraint results, predicted distributions, and settled costs remain in
   telemetry. A weighted score may rank already-feasible choices but cannot compensate for a
   failed invariant or authorize release promotion.
5. The controller is exterior planner/runtime policy. It may select what to propose, context,
   model route, refinement, topology, and verification strength. It cannot mint grants, author
   settled costs/verdicts, widen ceilings, bypass S0–S12, or move promotion pointers.
6. Quotes are advisory. Concrete effects and every escalation require an authorized reservation;
   escalation never creates a new wallet.
7. Schema support lands with `mhf.manifest/2` at M-3 so profiles are attributable. Runtime
   activation waits for RF-25 and the M-7 concurrency/selector measurement gate. Until then,
   profiles execute sequentially.
8. Every strategy report includes resolve rate, cost per signed pass, tokens, charged latency,
   assurance, and calibration error by task class.

**Bound falsifiers.** RF-46: profile-only change changes `D_H`. RF-47: controller cannot widen a
ceiling or bypass S0–S12. RF-48: escalation obtains a bounded reservation and debits the same root
budget. The M-7 benchmark reports model calls, coordination envelopes, bytes, WAL contention,
retries, and critical-path latency separately.

**Alternatives rejected.** One fixed global profile; fixed SLOs in substrate law; scalar reward
that hides safety regression; self-estimated ROI that renews a lease; or router logic in the kernel.

**Reversal condition.** Measured controller overhead exceeds the task-class spread it exploits,
or the frontier fails to distinguish strategies that paired exterior evaluation distinguishes.

**Owner · status.** CTO / Runtime Policy Owner · design accepted by Engineering Director ·
activation deferred to M-7 · 2026-08-21
