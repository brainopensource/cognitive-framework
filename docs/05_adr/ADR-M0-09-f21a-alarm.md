---
adr: M0-09
title: "Alarm set = {F-21a, F-24}"
status: accepted
---

# ADR-M0-09: Alarm set = {F-21a, F-24}

**Decision.** `KernelAlarm` fires on **both** `F-21a` (intent-append failure) and `F-24`, not
`F-24` alone as the original kernel spec stated.

**Context.** Drift D-18: "`KernelAlarm` on `F-21a` as well as `F-24` — `[OPTIMIZATION]`. 'F-24 is
the only kernel alarm' [was the spec's claim]. Intent-append failure must page. Amend VG-05; do not
drop the F-21a alarm." A crash between durable intent-append and effect dispatch is exactly the
undeterminable-effect case K-47 exists to make visible rather than silent — it must page an
operator, not just log.

**Reversal condition.** None identified; narrowing the alarm set back to `{F-24}` would reintroduce
a silent failure mode the as-built code already closed.
