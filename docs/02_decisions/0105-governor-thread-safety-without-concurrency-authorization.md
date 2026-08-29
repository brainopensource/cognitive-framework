---
id: adr-0105-governor-thread-safety-without-concurrency-authorization
adr: 0105
class: decision
authority: binding-decision
canonical_for:
  - kernel-budget-concurrency
  - governor-thread-safety
status: accepted
owner: repository-governance
version: "1.0.0"
last_verified: 2026-08-28
accepted_date: 2026-08-28
extends:
  - ADR-0096
  - ADR-0099
supersedes: []
superseded_by: null
---

# ADR-0105 — Kernel Governor Defensive Concurrency Protection

## Status

Accepted 2026-08-28. Binding on all concurrent runtimes and kernel dispatch invocations.

## Context

In multi-agent and async graph scheduling execution (EVO-07, EVO-14), concurrent callers dispatch through a shared kernel `Governor`.
The `reserve()` and `commit()` methods perform check-then-act operations over the held resource balances `_held`.
Without serialization, concurrent threads can experience race windows where both pass ceiling checks on stale `remaining()` reads and both commit, oversubscribing the ceiling.

## Decision

1. The kernel `Governor` in `vanguard/packages/kernel/budget.py` incorporates a defensive `threading.Lock` serializing `_reserve_locked()`, `_commit_locked()`, `release()`, and `is_open()`.
2. This is classified as a defensive integrity control for kernel budget conservation, not an expansion of kernel domain authority.
3. Kernel neutrality remains fully domain-blind, and TCB line budget remains strictly within limits (<= 1438 LOC).
