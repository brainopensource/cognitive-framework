# Wave 1 — Trust Spine (irreversible substrate on the packages path)

**Outcome:** False gates cannot certify the trust spine. Every event is lineage-complete, every
verdict is bound and signed, identity is complete, budgets are typed, and every episode leaves a
real trajectory. All work happens on `vanguard/packages/`; `layer0/` is untouched (its absorption
is Wave 2).
**Entry:** Wave 0 exit gate green (CI runs the production suites; falsifiers F-01…F-21 exist as
tests, red allowed; codegen `--check` wired).
**Exit (milestone M-1 in `docs/02_roadmap/milestones.md`):** falsifiers F-01…F-15 pass on the
canonical path; `test/kernel`, `test/contracts`, `test/agency` stay green; TCB ≤ 1438 LOC.
**Sprint order:** 1.1 and 1.2 can run in parallel by different developers; 1.3 depends on 1.2's
emitter (envelopes must carry `harness_digest`) and touches 1.1's compose surface.

---

## Sprint 1.1 — Signed verdict loop (falsifiers F-03, F-04, F-08; fixes F-21)

The evidence plane becomes real: nothing can complete an episode with an unsigned or unbound pass.

| # | Task | Where | Acceptance evidence | Readiness |
|---|---|---|---|---|
| 1.1-A | Regenerate types from the updated schemas; fix the generator if it emits invalid Python (Tech Lead lane finding) | `tools/codegen/generate_types.py`, `layer0/spi/types_gen.py` | `generate_types.py --check` green in CI (F-13) | READY |
| 1.1-B | Replace `canonical_verdict_bytes` with domain JCS; extend `VerdictSigner.sign/verify` to the bound `SignedVerdict` (all fields except `signature` are the signed body) | `adapters/evaluators/signing.py` | Signature over JCS bytes; unit test with a non-BMP string that `json.dumps` and JCS canonicalise differently | **SCAFFOLDED** (contract in `schemas/mhf/spi_payloads.schema.json`, ADR-0076 §5) |
| 1.1-C | Daemon binds verdicts: echo `evaluation_request_id`, `subject_digest`, `oracle_id`, fresh single-use `nonce`, `key_id`, `signed_at` into the signed body | `adapters/evaluators/daemon.py` | F-04: a replayed nonce or a signature detached from its request is rejected by the verifier | SCAFFOLDED |
| 1.1-D | Evaluator gateway appends `VerdictRecorded{SignedVerdict}` to the ledger via the role-scoped emitter (1.2-B); it is the ONLY code path that can | `runtime/` (new small module beside `evaluation_listener.py`) | F-03: grep + behavioral test — no other writer; scheduler/session cannot fabricate a pass | READY |
| 1.1-E | Agent-side gate becomes a **reader**: `gate()` consumes ledgered `VerdictRecorded` events (verify signature + binding again on read), returns PASS/RETRY/ESCALATE/ABANDON; delete the verify-then-discard path | `adapters/evaluators/gate.py`, `runtime/root.py:_evaluate` | An episode whose verdict is unsigned/unbound cannot reach a passing `RunResult` | READY |
| 1.1-F | Flip `SignedVerdict` binding fields to `required` in the schema; regenerate | `schemas/mhf/spi_payloads.schema.json` | Schema + types agree; F-04 stays green | READY (last task of sprint) |
| 1.1-G | `ProposalTranslator`: implement `parameters`-key lifting and the two fenced-payload forms; conform selector construction to the domain algebra (`generic`, never `process`) | `adapters/models/invocation.py` | The 5 `test_model_invocation` reds pass unmodified (F-21, P1-17 per ADR-0076 §2) | READY |

**Deliberately dev-local:** nonce store shape (in-daemon set vs sqlite), error taxonomy for
rejected verdicts, retry pacing in the gate.

## Sprint 1.2 — Ledger truth (falsifiers F-01, F-02, F-05, F-14)

The state plane becomes provable: one writer, complete lineage, cold replay.

| # | Task | Where | Acceptance evidence | Readiness |
|---|---|---|---|---|
| 1.2-A | Promote `LedgerBridge` out of `root.py` into `runtime/ledger_emitter.py`; all envelope construction goes through it; produce `mhf.event/1` envelopes (lineage fields, `prev_digest` chain per `project_id`, JCS digest) | `runtime/root.py:418-487` → new module | F-01: every emitted envelope carries full lineage; construction elsewhere fails review + duplication detector | READY (seam already exists) |
| 1.2-B | Role-scoped writer facades (kernel / scheduler / registry / evaluator-gateway / approval); privileged kinds accepted only from their owner (ADR-0074 §3) | same module | F-05: orchestrator-role facade appending `VerdictRecorded` or `CapabilityGranted` is refused, with a negative test | READY |
| 1.2-C | `project_id` enters the system: session/composition assigns it; store chains and sequences per project | `runtime/root.py` compose/session, `adapters/stores/event_store.py` | Two projects interleaved keep independent `seq`/`prev_digest` chains | TECH-LEAD (pick the id source: config vs workspace identity — settle before assignment) |
| 1.2-D | Cold replay job: run a fixture episode against the real WAL file, fold from disk in a fresh process, structurally diff grants tree, budget vector, approval log, episode FSM vs live terminal state | `test/runtime/`, `.github/workflows/ci.yml` job `replay-parity` | F-02 green; same-list fold demonstrably not the mechanism (I-4, ADR-0071) | READY |
| 1.2-E | Durable-intent proof: kill the process between S8a and S9 in a harness test; recovery scanner reconciles to `undeterminable` | `test/runtime/` (kernel already implements K-47) | F-14 green | READY |
| 1.2-F | Absorb `EvaluationListener` envelope fabrication into the emitter (no invented `seq`, no pseudo-UUIDv7) | `runtime/evaluation_listener.py` | Listener output indistinguishable from emitter output under the envelope schema | READY |

**Deliberately dev-local:** projection/index tables, emitter batching, event-id format (as long as
it is unique and stable).

## Sprint 1.3 — Identity, authority, and the dataset (F-06, F-07, F-09, F-10, F-11, F-12, F-15)

| # | Task | Where | Acceptance evidence | Readiness |
|---|---|---|---|---|
| 1.3-A | `D_H` compose: compute over full composition (resolved refs+digests, system-prompt bytes, ceiling **intersection**, approval policy, model routes) via JCS; store on the frozen harness; `episode_id` leaves identity (ADR-0076 §4) | `runtime/root.py:Runtime.compose`, `domain/artifacts/manifest.py` | F-11: prompt-only or ceiling-only change changes `D_H`; two identical compositions collide byte-identically | READY |
| 1.3-B | Fail-closed ceilings on the canonical path: compose persists the plugin∩harness intersection; empty ceiling authorizes nothing; enforcement consults the domain algebra | `runtime/root.py`, `domain/selectors/` | F-06, F-07 green with negative tests | READY |
| 1.3-C | Typed budget algebra: additive vs structural dimensions split; `attenuation._exceeds` treats `None` (unbounded child under bounded parent) as **deny**; sibling depths never summed | `kernel/budget.py`, `kernel/attenuation.py` — *TCB-touching: smallest possible diff* | F-09, F-10, F-15 green; TCB LOC gate still passes | TECH-LEAD (review the exact kernel diff before merge) |
| 1.3-D | Trajectory emission: assemble `mhf.trajectory/1` during the episode (context digests per turn, receipts with `lease_id`/`grant_digest`, cost vectors, ledgered verdict) and emit at `EpisodeCompleted` | `agency/episode/engine.py` hooks + `runtime/` assembler | F-12: schema-valid against `schemas/mhf/trajectory.schema.json` for every terminal episode, including aborted ones (`verdict: null`) | **SCAFFOLDED** (schema landed) |
| 1.3-E | Receipt gains `lease_id` + `grant_digest` (P1-9) | kernel emit payloads already carry both — surface into `Receipt` | Trajectory rows carry them | READY |

**Escalate to Director if:** any task needs a kernel LOC increase beyond the 1438 ceiling, a new
event kind, or a second digest algorithm. Those are not Wave-1 decisions.
