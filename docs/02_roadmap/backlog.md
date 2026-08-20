# Backlog — v0.6 Foundation execution register

**Status:** Living. Task-level register under [`milestones.md`](milestones.md); sprint detail in
[`../03_sprints/plans/`](../03_sprints/plans/). Authority: `002` gap register + ADRs `0069`–`0076`.
Replaces the historical EPIC-M* map (removed; git history `4f9f8b1`).

**Readiness legend**
- **READY** — contract, owner boundary, and acceptance evidence are settled; implement directly.
- **SCAFFOLDED** — leadership landed the contract (schema/decision); complete the implementation against it.
- **TECH-LEAD** — needs a Tech Lead decision or diff review before assignment.
- **DEV-LOCAL** — intentionally left to the implementing developer's design.
- **DIRECTOR** — do not decide locally; escalate.
- **DONE** — landed and its falsifier passes on the canonical path.

## Wave 0 — **CLOSED (M-0)**

| ID | Task | Readiness |
|---|---|---|
| W0-CI | CI subject-of-record rewire; quarantine Ollama env-sensitive cases | (theirs) |
| W0-FALS | Falsifiers F-01…F-21 as tests (red allowed) | (theirs) |
| W0-HYG | F-19 `__init__.py` for `test/integration`+`test/governance`; F-20 oracle artifact or retirement; stale-path residue | (theirs) |

## Wave 1 — Trust spine (`plans/wave1_trust_spine.md`) — **CLOSED, M-1 GREEN**

| ID | Task | Falsifier | Readiness |
|---|---|---|---|
| 1.1-A | Regenerate types; fix generator | F-13 | DONE |
| 1.1-B | JCS verdict bytes in `signing.py` | F-04 | DONE |
| 1.1-C | Daemon binds verdicts (request/subject/oracle/nonce) | F-04 | DONE |
| 1.1-D | Evaluator gateway = sole `VerdictRecorded` writer | F-03 | DONE |
| 1.1-E | Gate reads ledgered verdicts; delete verify-and-discard | F-03/F-08 | DONE |
| 1.1-F | Flip binding fields required; regenerate | F-04 | DONE |
| 1.1-G | Translator lifting + selector conformance | F-21/P1-17 | DONE |
| 1.2-A | `LedgerEmitter` from `LedgerBridge`; `mhf.event/1` envelopes | F-01 | DONE |
| 1.2-B | Role-scoped writer facades | F-05 | DONE |
| 1.2-C | `project_id` source + per-project chains | F-01 | DONE — config-declared (`TaskContext.project_id`); workspace-derived rejected |
| 1.2-D | Cold `replay-parity` CI job from disk | F-02 | DONE |
| 1.2-E | Durable-intent crash test | F-14 | DONE |
| 1.2-F | Listener uses the emitter | F-01 | DONE |
| 1.3-A | Complete `D_H` at compose | F-11 | DONE |
| 1.3-B | Fail-closed ceiling intersection on canonical path | F-06/F-07 | DONE |
| 1.3-C | Typed budget algebra; `None` fails closed (kernel diff) | F-09/F-10/F-15 | DONE — kernel diff reviewed and accepted; TCB 1359/1438 |
| 1.3-D | Trajectory assembly + emission at `EpisodeCompleted` | F-12 | DONE |
| 1.3-E | Receipt carries `lease_id`/`grant_digest` | P1-9 | DONE |

**Gate note (Tech Lead, M-1).** F-08 was adjudicated a stale falsifier, not a defect: it asserted
that a fully authorized privileged dispatch must fail. The kernel's grant path (S6 issue → S8
verify-at-effect → S8a bound intent) is correct and is now asserted in both directions. F-01, F-03,
F-07, F-09, F-10 and F-12 were re-pointed from `layer0/` (and from a file-exists probe) onto the
canonical path, so M-1 is not gated on defects the plans defer to Wave 2. Full record:
[`../03_sprints/sprint_active.md`](../03_sprints/sprint_active.md).

## Wave 2 — Convergence (`plans/wave2_convergence.md`)

| ID | Task | Readiness |
|---|---|---|
| 2.1-A | jsonrpc → `domain/wire/`; flip 6 imports | DONE — layer0 copy reduced to a shim at 2.2-A |
| 2.1-B | types_gen target moves to packages; shim | DONE |
| 2.1-C | Five SPI Protocols → `ports/spi.py` | DONE |
| 2.1-D | Ceiling delegates to domain algebra; fail-closed | DONE — incl. pack/call-site selector conformance (the 2.2-A blocker) |
| 2.1-E | Duplication detector heuristics | DONE — `--enforce` wired in CI |
| 2.2-A | Parity assertion triage layer0→contracts | **DONE — GREEN.** Keep/kill in `plans/wave2_convergence.md`; 3 absorptions landed (branch resume, blob durability, governor dimension guard) |
| 2.2-B | Delete the 2.2-A KILL surfaces; retire v4 write path. **Scope narrowed:** `registry/`, `compose/`, `events/{emitter,envelope,store,taxonomy}.py` retained to 3.1 | **AUTHORIZED** — Developer A |
| 2.2-C | `root.py` split in place (compose/session/emitter/wiring) | **AUTHORIZED** — Developer B |
| 2.2-D | Widen I-7 linter (if Wave 0 didn't); boundary rows | READY |

## Wave 3 — Extensibility (`plans/wave3_extensibility.md`)

| ID | Task | Readiness |
|---|---|---|
| 3.1-A | Registry FSM on packages; ledgered transitions | READY |
| 3.1-B | Compose v2 ↔ registry; freeze-at-compose negatives | READY |
| 3.1-C | Echo plugin lifecycle + fault injection (ADR-M0-13) | READY |
| 3.1-D | Isolation broker rlimits scope | TECH-LEAD |
| 3.2-A | code-default toolkits through the lifecycle | READY |
| 3.2-B | Coding-token sweep; widened I-7 green | READY |
| 3.2-C | One manifest parser | DEV-LOCAL |

## Wave 4 — Foundation E2E (`plans/wave4_foundation_e2e.md`)

| ID | Task | Readiness |
|---|---|---|
| 4.1-A | Fixture repo + preregistered oracle (closes F-20 at its canonical home) | READY |
| 4.1-B | Nine-row E2E integration test | READY |
| 4.1-C | Cassette of the green run for per-PR CI | READY |
| 4.1-D | Evidence bundle report | DEV-LOCAL |

## DIRECTOR-only (escalate; do not pick up)

New event kinds · sixth SPI · kernel LOC ceiling change · second digest/canonicalisation ·
concurrency enablement · version/release cut after M-4 · anything on SPEC §9's refusal list.
