---
id: canonical-m4-m8-backlog
class: execution
authority: execution
canonical_for: [m4-m8-work-packages, two-developer-delivery-tracks, package-dependencies-and-acceptance]
status: living
owner: tech-lead
version: "1.0.0"
last_verified: 2026-08-27
subordinate_to: ../../VISION.md
supersedes: [leadership-backlog-2026-08-25]
superseded_by: null
---

# Canonical Backlog — M-4 through M-8

This is the sole stable backlog. [`sprint_active.md`](sprint_active.md) authorizes current work and
[`sprint_upcoming.md`](sprint_upcoming.md) stages the next dependency-qualified window. Law and ADRs
own requirements and decisions; this file owns executable packaging.

## Global package contract

Every package starts from an exact reviewed commit/tag, keeps WIP=1 per developer, and supplies a PR
matrix `obligation -> production symbol -> test/falsifier -> evidence artifact`. It declares public
schema versions, Kernel/lattice/event-writer changes, migration, rollback, exclusions, and local
versus integrated gates. Unknown occurrence/evidence fails closed. Kernel stays <=1,438 logical LOC;
TCB growth requires explanation; benchmarks name host, dependencies, data, and distributions. No
package consumes another developer's unfinished branch.

| ID | Milestone | Owner/state | Depends on; merge order | Acceptance |
|---|---|---|---|---|
| WP-A1 | M-4/M-6 | Dev A / **PACKAGE_READY** | ADR-0101/0102; first runtime repair | M-4 and M-6 separately |
| WP-B1 | M-5a/M-5b | Dev B / **PACKAGE_READY** | ADR-0101/0102; tooling beside A1, treatment after baseline | baseline + M-5b bundle |
| WP-A2 | M-6.5 | Dev A / **BLOCKED** | A1 merged; ADR-0103 frozen; awaiting C1 independent acceptance | runtime-seam evidence |
| WP-B2 | M-6.5 | Dev B / **ACCEPTED** | A1/A2; instrument then study | signed positive/negative disposition |
| WP-A3 | M-7 | Dev A / **NOT_STARTED** | A1; before B3 runs | three runtime topologies |
| WP-B3 | M-7 | Dev B / **NOT_STARTED** | frozen A3; before ADR-0099 | accepted M7-01 + decision |
| WP-A4 | M-8 | Dev A / **NOT_STARTED** | M-7 decision, ADR-0100; before B4 | durable authorized memory |
| WP-B4 | M-8 | Dev B / **NOT_STARTED** | A4, M-6.5 disposition | lift + real rollback |
| WP-C1 | M-1/M-2/M-4 preservation | Dev A / **IN_PROGRESS** | accepted ADR-0062/0089/0101; before A3 | restored I-5 trust spine and one canonical event truth |

Dev A: `WP-A1 -> WP-C1 -> WP-A2 -> WP-A3 -> WP-A4`. Dev B: `WP-B1 -> WP-B2 -> WP-B3 -> WP-B4`.

`WP-C1` is a preservation package, not a new milestone. It repairs backend service and
distribution surface that entered the tree outside the M-4–M-8 packages and that currently
regresses already-accepted invariants (`I-5`, and the M-2 one-writer anchor). It closes no gate of
its own; it restores the preconditions the M-7 and M-8 packages assume.

## WP-A1 — Release evidence and canonical recursion

| Concern | Implementation-ready contract |
|---|---|
| Objective/rationale | Restore RF-95 and replace synthetic delegation success, volatile IDs, unconserved parent balance, and callback-only execution with real recursive runtime capability. |
| Surface/boundary | `runtime/delegation.py`, `wiring.py`, `session.py`, `root.py`, recovery/ledger; minimal child protocol in Ports; focused/release tests. Runtime orchestrates; Kernel/Agency semantics stay fixed. Dev A owns runtime hotspots. |
| Interface/I-O | Immutable `SpawnIntent`, `ChildRunPlan`, `ChildRuntimePort`; bind composition/goal digest, scope, 4-D budget, turns, idempotency. Result binds terminal state, artifact/digest, actual cost, turns, evidence refs—never transcript/live handle. |
| Algorithm/events | `child_id=H(parent_episode_id,idempotency_key)`; persist mapping, collision-check, attenuate actions/selectors, reserve each dimension against parent remaining, lower depth/turns, append `ChildSpawned`, invoke the same `Runtime.run_composed` with rebound ports, append `ChildReturned`, settle/refund. Replay settled; reconcile open/unknown as `UNDETERMINABLE`. |
| Failure/security | Missing child port fails composition before facts; scope/action/depth/turn/budget/grant/ID uncertainty denies. No ambient inheritance, widening, borrowing, blind retry, cross-project idempotency. Cancellation is mediated and never erases facts. |
| Observability/performance | Bind plan/grant/composition/result/reconciliation digests and correlated duration; prove disabled-path neutrality and report overhead against a pinned sequential baseline. |
| Tests/falsifiers | Missing runner; restart-stable ID; collision; each budget dimension; depth/turn/scope widening; transcript leakage; depth>=3 cold fold; crash boundaries; settled replay; project isolation; kill tree; RF-98. |
| Evidence/migration/DoD | Verify supplied RF-95 or preregister one new candidate—never fabricate it. Separate `aether.evidence/1` M-4/M-6 bundles; old volatile rows stay historical. Canonical recovery and fresh-process verification pass; independent reviewers decide milestones separately. |

## WP-A2 — Stable meta-control observation seam

| Concern | Implementation-ready contract |
|---|---|
| Objective/surface | Freeze runtime M-6.5 without authority: `domain/ledger/progress.py`, `ports/meta_controller.py`, runtime integration/telemetry/tests. Domain projects facts; Runtime consults between turns; Kernel unchanged. |
| Contract/behavior | `ProgressProjection/2` exposes verified delta, failed/unknown rate, repeat entropy, novelty, normalized burn, revision effectiveness, calibrated uncertainty. `SemanticCheckpointRef` binds run/episode/epoch/attempt. Directive binds controller/policy/input/reason/confidence digests; no grant/verb/sink. |
| Failure/security | Reject stale epoch, unknown subject, missing basis, uncalibrated sole signal, nondeterminism, budget keys, authority fields. Controller-off is default baseline; telemetry loss cannot alter projection/verdict. |
| Tests/evidence/DoD | Fold partition/determinism, stale confidence/escalation, off parity, checkpoint stability under divergent paths, no Kernel diff, one runtime-seam envelope. Merge before B2. |

## WP-A3 — Sequential topology and timing integration

| Concern | Implementation-ready contract |
|---|---|
| Objective/surface | Make topology an optional capability of the one runtime and capture valid M7-01 timing: composition/root/session/topology/scheduler, `TelemetrySink`, integration tests; no Kernel/episode-loop authority change. |
| Interface/algorithm | Sorted immutable `RunPlanExtensionRef(schema,digest,artifact_ref,required)` enters identity. Before first event authorize read, verify/parse/lower against frozen composition, bind lowering/scheduler digests, reject unknown required extensions. Each wave derives ready operations and stable sequential order, then uses ordinary M-6 execution. |
| Events/telemetry | Correlate monotonic start/end by run, episode, operation, descriptor, idempotency, process epoch. Ledger timestamps remain causal wall observations; timing is neither budget cost nor patched into `EffectStarted`. |
| Failure/security/performance | Authority-bearing topology, unknown role/composition/selector, bad artifact flow, missing required extension, cycle, or unsettled predecessor fails closed. Disabled path preserves identity/event parity; telemetry median overhead target <3% on declared workload. |
| Tests/evidence/DoD | Three real patterns (direct; planner/executor/reviewer; planner/two readers/merger), malformed/authority/cycle/crash/replay, selector/timing completeness, disabled parity, RF-98. Deliver bundle for B3. |

## WP-A4 — Verified durable memory and lifecycle

| Concern | Implementation-ready contract |
|---|---|
| Objective/surface | Implement ADR-0100: authorized Domain/Ports values, Runtime integration, SQLite-WAL/blob/lexical adapters, retention/GC/backup, security/performance tests. In-memory/string access remains test scaffolding; Kernel has no memory branch. |
| Contract/storage | `MemoryAuthorizationPort.verify -> AuthorizedMemoryContext` binds issuer, subject, action, selector, tenant/project/purpose/time/revocation/policy/receipt. Four ports write/recall/invalidate immutable refs. SQLite stores scoped metadata/invalidation/retrieval receipts; CAS stores content. Ranking quantizes and ties by record ID. |
| Algorithm/events | Verify at use; canonicalize/redact; blob put; metadata/index transaction; `ClaimRecorded(memory.recorded/1)`. Recall authorizes/scopes before ranking/dereference, budget-packs, persists receipt, contributes authorized refs+provenance. Invalidation appends. GC mark roots, legal hold, quarantine, reviewed dry run, sweep receipts. |
| Failure/security | Forged/expired/revoked/cross-scope is opaque `Denied/DID_NOT_OCCUR`; auth outage fails sensitive use closed. Blob-only writes become orphans; metadata without causal fact quarantines; corrupt index rebuilds/blocks by profile; refuse WAL on network FS. |
| Observability/performance | Receipt binds query/policy/index/tokenizer/candidates/selection/redaction/context. Declared-host targets: atomic 4KiB write p95<50ms; lexical recall p95<100ms at 100k, limit<=20. Migration is digest-verified export/import. |
| Tests/evidence/DoD | Forgery/expiry/revocation/scope/category/leaks/pre-rank/cache, crash boundaries, restore, legal hold/GC, context provenance, performance and independent security review. Merge before B4. |

## WP-B1 — Baseline succession and fresh generality

| Concern | Implementation-ready contract |
|---|---|
| Objective/surface | Record invalid M-5 control provenance and prepare a clean forward falsifier in schemas, verifier/CI/tests, and preregistered pack-local graph coloring. Do not create tag/treatment early or alter protected substrate. |
| Contract/algorithm | `aether.baseline/1` binds annotated remote tag object, commit/tree/lock/package/schema/reducer pins, prohibited paths, receipts, creator/reviewer. Verify remote/local identity, digests, signatures, receipts, ancestry/tree contamination. Missing/weak/lightweight/unpushed/contaminated fails closed. |
| Treatment | Only after Leadership creates `CONVERGENCE-BASE-v1`, implement graph coloring in pack/evaluator/fixtures/registration. Candidate assigns `[0,k)`; exterior oracle verifies completeness/range/edges without search. Canonical input sorts vertices/edges. SAT remains regression. |
| Failure/security | Never reuse old name, mutate history, whitelist protected changes, self-grade, expose oracle internals, or accept unsigned pass. Record positive/negative axes separately. |
| Tests/evidence/DoD | Baseline resolution/signature/tree/pin/contamination falsifiers; satisfiable/edge/incomplete/range/malformed/duplicate/order vectors; fresh-process material run; RF-86/RF-98; independent acceptance. |

## WP-B2 — Attributable stochastic M-6.5 study

| Concern | Implementation-ready contract |
|---|---|
| Objective/surface | Replace degenerate deterministic study: model adapter/cassette, digest-pinned blocked tasks, `lab/m65_study.py`, schemas/reports/falsifiers. Adapter implements Ports; study has no authority. |
| Inputs/algorithm | Common-random key `H(task_manifest,environment_seed,checkpoint,attempt,perturbation)`; identical task/environment perturbations, only controller flag differs. >=20 tasks, >=4 recoverable block types, >=3 seeds (>=60-pair pilot), then power from discordance without optional stopping. |
| Output/statistics | Signed envelope: A/A floor, comparability, directives, discordant counts, McNemar exact, Holm, paired bootstrap CI, cost/latency/regression budgets, outcome. |
| Failure/security | Adapter errors stay errors; stochastic identity enters `D_R`; wrapper has no authority/writes. Degenerate A/A, identical arms, undeclared dimension, missing attribution, contamination, or inadequate power is `UNDETERMINABLE`. |
| Tests/evidence/DoD | Same-key replay, interior variance, attribution, ordinary dispatch, block elicitation, byte-identical arms, refusal/statistics vectors, reproducible signed report. Leadership chooses enable/experimental/disable; valid negative evidence may accept M-6.5. |

## WP-B3 — M7-01 and scheduler decision

| Concern | Implementation-ready contract |
|---|---|
| Objective/surface | Measure runtime independence/topology neutrality and force ADR-0099: exterior read-only `lab/m701_independence.py`, workload/telemetry/report tooling and falsifiers. |
| Model/algorithm | Eligible pair has no causal order, disjoint proven selectors, compatible sinks, safe idempotency, complete timing. Unknown/missing selector, sink, occurrence, or timing serializes and counts incomplete. Report eligible duration, critical path, sequential makespan, completeness, contention/cache/recovery, simulated bounded-read lift with intervals. |
| Decision | Recommend read-only parallelism `max_parallelism=2` only if preregistered thresholds pass with zero state/verdict divergence and duplicate privileged occurrence; otherwise `SEQUENTIAL_CONFIRMED`. Writes/spawn/promotion/shared or unknown sinks stay sequential. |
| Tests/evidence/DoD | Three real bundles, order metamorphism, missing-data conservatism, crash/replay, process-epoch correctness, RF-98, signed M7-01 and independent review; Leadership then writes ADR-0099. |

## WP-B4 — Sealed evaluation, promotion, rollback

| Concern | Implementation-ready contract |
|---|---|
| Objective/surface | Complete ADR-0100 learning: trajectory/candidate pipeline, sealed manifests, evaluator/promoter adapters, durable registry, runtime promotion/rollback, lab/security/fault tests. Generator/evaluator/promoter identities, keys, stores, roles are separate. |
| Contract/algorithm | Manifest binds base, candidate skills/policies, retrieval policy, generator/sources. Seal dev/held-out/adversarial/transfer digests first. Paired evaluation records present/retrieved/invoked/grounded/verified/outcome. Require preregistered lift/CI/exact test/Holm, <=5% baseline-success regression, zero critical security regressions. Promoter verifies report/signature/base/head and SQLite-CASes expected generation. Rollback is signed CAS and must alter served runtime. |
| Failure/security | Generator cannot read held-out labels/promoter keys; evaluator cannot promote; stale CAS loses; missing transition receipt quarantines; presence-only gain rejects. Evidence binds workload, access log, observations, generations, signatures, restart. |
| Tests/performance/migration/DoD | Contamination, role/key collapse, attribution, concurrent promoters, every crash boundary, restart, injected regression, signed/behavioral rollback, RF-98/TCB and overhead. At least one composition passes held-out independent review; otherwise M-8 stays open. |

## WP-C1 — Backend service trust spine and canonical event truth

| Concern | Implementation-ready contract |
|---|---|
| Objective/rationale | `runtime/service/` and the standalone CLI entered the tree outside the M-4–M-8 packages and regress accepted invariants: the CLI carries a literal operator signing seed and an unconditional auto-approver, the HTTP gateway defaults missing approval signatures, `ResolveApproval` records decisions without consulting `ApprovalAuthority`, and `publish_event` maintains two competing event histories while discarding the canonical append result. Restore `I-5`, the M-2 one-writer anchor, and `I-4`/`I-9` recovery truth without touching Kernel or domain semantics. |
| Surface/boundary | `runtime/keys.py` (new), `runtime/cli.py`, `runtime/service/{service,server,studio_gateway}.py`, `runtime/checkpoints.py` consumption, `install_vanguard.sh`, `pyproject.toml` scripts. Runtime and Adapter layers only; Kernel and Agency unchanged; TCB budget untouched. Dev A owns service/ledger/recovery hotspots; Dev B owns schema, model routing, and evidence tooling. |
| Interface/I-O | `load_operator_signer(allow_create)` returns a per-install Ed25519 signer from `~/.vanguard/keys/operator.ed25519` at mode `0600`; absent key or permissive mode fails closed. `ApprovalDecision` parses strictly with no defaulted field. `publish_event` returns a sequence only after canonical commit. `Checkpoint`/`Resume` exchange `CheckpointManager` pointers, not opaque digests. |
| Algorithm/events | Ingress order is size → parse → envelope → command → authentication → idempotency → authorization → execution → durable receipt. Approval resolution loads the pending `ApprovalRequested` challenge from canonical history, then verifies registered key, signature, expiry, run/approval correspondence, `argsDigest`, and `descriptorDigest` before appending `ApprovalResolved`. Event append allocates sequence and writes inside one canonical transaction; subscribers are notified only after commit. Checkpoint captures a reconstructable `LedgerState`; resume verifies the pinned digest, cold-reconstructs, reconciles open effects, and appends `RunRecovered`. Cancellation appends durable intent, sets a cooperative token the worker observes at turn boundaries, and records a terminal fact or `CancellationUndeterminable`. |
| Failure/security | No security-relevant field has a default. A verifier that cannot run is `not_available`, never a pass. Missing TTY without an explicit scoped expiring grant denies. CORS is a configured origin allowlist, never `*`; unauthenticated commands are refused; HTTP and UDS share one 1 MiB limit; workspace reads resolve through authorized selectors. Only the ten canonical error codes are emitted. Durable-store failure is a startup error, never an in-memory fallback. |
| Observability/performance | Bind approval challenge, decision, checkpoint, reconstruction, and cancellation digests. Recovery capability and verification stay distinct fields; a loaded checkpoint is not a verified one. Notification loss after commit is recoverable by cursor resume and never loses a fact. |
| Tests/falsifiers | Embedded key material absent from the distribution and two installs differing; non-TTY approval denial with no appended fact; missing/foreign/expired/unregistered/unchallenged approval each refused with no fact; unauthenticated and cross-origin gateway refusal; oversized body refusal; `StreamEvents` validated before state access; canonical append failure yielding no sequence and no notification; envelope round-trip preserving tenant, project, lineage, causation, idempotency, trace, and authority provenance; checkpoint reconstructability; resume digest verification and restart; worker-observed cancellation. |
| Evidence/migration/DoD | No schema version changes. Existing durable stores remain readable; the outbox becomes command-idempotency-only and its event rows stay as history. Rollback is reverting the package. Done when every falsifier above has been observed failing on the unrepaired tree and passing on the repaired one, and the package is reviewed by someone other than its producer. `WP-C1` claims no milestone acceptance. |

## Review gate

Leadership checks exact baseline, exclusions, compatibility, failure/security, migration/rollback,
falsifiers, digest-addressed evidence, and reviewer independence. Packages may merge at
`PACKAGE_READY`; milestones become `ACCEPTED` only after all mandatory receipts are accepted.
