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

## Wave 0 (in flight — separate team; listed for dependency visibility only)

| ID | Task | Readiness |
|---|---|---|
| W0-CI | CI subject-of-record rewire; quarantine Ollama env-sensitive cases | (theirs) |
| W0-FALS | Falsifiers F-01…F-21 as tests (red allowed) | (theirs) |
| W0-HYG | F-19 `__init__.py` for `test/integration`+`test/governance`; F-20 oracle artifact or retirement; stale-path residue | (theirs) |

## Wave 1 — Trust spine (`plans/wave1_trust_spine.md`)

| ID | Task | Falsifier | Readiness |
|---|---|---|---|
| 1.1-A | Regenerate types; fix generator | F-13 | READY |
| 1.1-B | JCS verdict bytes in `signing.py` | F-04 | SCAFFOLDED |
| 1.1-C | Daemon binds verdicts (request/subject/oracle/nonce) | F-04 | SCAFFOLDED |
| 1.1-D | Evaluator gateway = sole `VerdictRecorded` writer | F-03 | READY |
| 1.1-E | Gate reads ledgered verdicts; delete verify-and-discard | F-03/F-08 | READY |
| 1.1-F | Flip binding fields required; regenerate | F-04 | READY |
| 1.1-G | Translator lifting + selector conformance | F-21/P1-17 | READY |
| 1.2-A | `LedgerEmitter` from `LedgerBridge`; `mhf.event/1` envelopes | F-01 | READY |
| 1.2-B | Role-scoped writer facades | F-05 | READY |
| 1.2-C | `project_id` source + per-project chains | F-01 | TECH-LEAD |
| 1.2-D | Cold `replay-parity` CI job from disk | F-02 | READY |
| 1.2-E | Durable-intent crash test | F-14 | READY |
| 1.2-F | Listener uses the emitter | F-01 | READY |
| 1.3-A | Complete `D_H` at compose | F-11 | READY |
| 1.3-B | Fail-closed ceiling intersection on canonical path | F-06/F-07 | READY |
| 1.3-C | Typed budget algebra; `None` fails closed (kernel diff) | F-09/F-10/F-15 | TECH-LEAD |
| 1.3-D | Trajectory assembly + emission at `EpisodeCompleted` | F-12 | SCAFFOLDED |
| 1.3-E | Receipt carries `lease_id`/`grant_digest` | P1-9 | READY |

## Wave 2 — Convergence (`plans/wave2_convergence.md`)

| ID | Task | Readiness |
|---|---|---|
| 2.1-A | jsonrpc → `domain/wire/`; flip 6 imports | READY |
| 2.1-B | types_gen target moves to packages; shim | READY |
| 2.1-C | Five SPI Protocols → `ports/spi.py` | READY |
| 2.1-D | Ceiling delegates to domain algebra; fail-closed | READY |
| 2.1-E | Duplication detector heuristics | DEV-LOCAL |
| 2.2-A | Parity assertion triage layer0→contracts | TECH-LEAD |
| 2.2-B | Delete layer0 kernel/scheduler/MemoryLedger/absorbed dirs; retire v4 write path | READY (after 2.2-A) |
| 2.2-C | `root.py` split in place (compose/session/emitter/wiring) | READY |
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
