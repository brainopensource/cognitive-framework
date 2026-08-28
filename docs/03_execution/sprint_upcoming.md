---
id: upcoming-sprint-board
class: execution
authority: execution
canonical_for:
  - next-qualified-work-window
status: living
owner: tech-lead
version: "1.1.0"
last_verified: 2026-08-28
subordinate_to: ../../VISION.md
supersedes:
  - leadership-sprint-upcoming-2026-08-25
superseded_by: null
---

# Upcoming Development Waves — AETHER v0.9

This file is preparation, not current authorization. Items move to
[`sprint_active.md`](sprint_active.md) only when their named entry gates are true.

The remaining implementation is organized into two lanes. Work starts when the
listed machine predicate is true; evidence integrity remains separate from
package readiness.

| Sprint | Order | Package | Owner | Planned state | Entry gate | Exit |
|:--|---:|---|---|---|---|---|
| C3 | 1 | WP-B3 evidence | Lane B | **NOT_STARTED** | WP-A3 exact-subject bundle | M7-01 receipt and ADR-0099 disposition verification |
| C4 | 2 | M-8 publication | Lane A + Lane B | **BLOCKED** | clean immutable subject; valid M-6.5 and M-7 dispositions | signed bundle plus independent exact-digest acceptance |
| C5 | 3 | M-9 operational beta | Lane A | **BLOCKED** | independently accepted M-8 and explicit activation on the active board | installable `0.9.0b1` beta qualification |
| C6 | 4 | M-10 final qualification | Lane A + Lane B | **BLOCKED** | qualified M-9 beta | exact-subject `0.9.0` release envelope and release qualifier exit `0` |
| C7 | 5 | SWE-Bench Pro sealed campaign | Measurement lane | **NOT_STARTED** | reproducible M-9 harness; preregistered task split and budget | independently reproducible score and cost report; never a milestone substitute |

The immediate sequence is evidence close-out in parallel with M-7 repair, followed by M-8 acceptance,
M-9 beta, M-10 release qualification, and a sealed competitive evaluation. Full package contracts
remain in [`backlog.md`](backlog.md).

### M-9 staged scope

When authorized, M-9 builds wheel and sdist in isolation; installs outside the checkout into an empty
environment; verifies package resources, schemas, migrations, entry points, unified version/configuration,
CLI/service parity, stop/resume, event/artifact inspection, offline-after-install behavior, and clean
uninstall; and qualifies plugin discovery, signature/digest verification, explicit activation,
health/readiness, quarantine, upgrade, and rollback. Every product surface calls the canonical runtime.

### M-10 staged scope

M-10 qualifies supported migrations and downgrade refusal, backup/restore under load, interrupted
migration, WAL/blob/index corruption, process kills at durable boundaries, bounded soak, deployment
profiles, reproducible artifacts, and a signed envelope bound to the exact source and package digests.
Git-dependent identity remains an explicit external input to the qualifier.

### Competitive evaluation staging

SWE-Bench optimization is a separate measured program. Use 10–15 smoke tasks, 30–50 paired development
tasks, 100–200 qualification tasks, then one sealed official evaluation. Pin task set, image, repository
revision, runtime, evaluator, model/provider, prompts, topology, budgets, timeout, and pricing snapshot.
`pass@1` is primary; cost, latency, tokens, tool calls, retries, patch size, and failure class are reported.
Free or cheap models may scout, classify, or review; comparative runs pin an exact model and never use a
random free-model router. The target is greater than 60% on a preregistered sealed evaluation, not a
milestone claim or a basis for weakening runtime gates.

M-9/M-10 are stable release stages in [`milestones.md`](milestones.md); implementation begins only
when their predecessor predicates are true.
