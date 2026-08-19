---
adr: M0-07
title: "Six-dimension Reservation"
status: accepted
---

# ADR-M0-07: Six-dimension Reservation

**Decision.** `Reservation` grows from four dimensions (`{usd_micros, millis, tokens, bytes}`,
frozen by `X-14`/drift D-24) to six: `{usd_micros, millis, tokens, bytes, turns, depth}`. This is
allowed **only because the M1 scheduler is the named consumer** — turn ceilings and delegation depth
become first-class budget dimensions instead of an ad-hoc `EpisodeEngine._max_turns` check outside
the kernel (drift D-09).

**Context.** Drift D-24 explicitly warned: "document; do not silently add `evaluations` without a
consumer." This ADR is the exception that proves the rule — turns/depth get a consumer (the
scheduler) in the same milestone they're added.

**Reversal condition.** A seventh dimension requires a consumer first — no dimension is added to
`Reservation` speculatively. `evaluations` (contemplated but rejected by D-24) stays out until the
same test is met.
