---
adr: M0-08
title: "K-40 inverted: evaluator outside the worker perimeter"
status: accepted
---

# ADR-M0-08: K-40 inverted: evaluator outside the worker perimeter

**Decision.** `docs/annex/KERNEL.md` §6 (perimeter) is amended: the evaluator runs as a
**separate identity (UID 10002) outside** the worker's sandbox perimeter, not co-located inside it
as `K-40` originally specified. The as-built is stronger than the spec as written.

**Context.** Drift D-32: "Evaluator outside the worker perimeter (`K-40` inverted) — `[OPTIMIZATION]`.
Separate UID 10002 daemon + unreadability probe is the *stronger* isolation for `CL-1`. Amend `K-40`;
do not put the judge inside the candidate." The audit's S-3 finding independently names this the
anti-reward-hacking primitive competing harnesses (Claude Code, OpenHands, Aider) all lack.

**Reversal condition.** Do not restore `K-40` as originally written (evaluator inside the same
perimeter, network denied). Reversal would require a proof that co-location cannot be exploited by
a candidate reading the grading logic — no such proof exists or is sought.
