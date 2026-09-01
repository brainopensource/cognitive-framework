---
id: execution.active
canonical_id: execution.active
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: WAVE_1_CLOSED_WAVE_2_TECHNICAL_COMPLETE_BACKEND_HARDENING_READY
owner: repository-governance
canonical_for:
  - current work/state/ownership
purpose: Represent current execution intent exactly as the active board states it, including unresolved internal status conflicts.
audience:
  - contributor
  - release-owner
analysis_subject_sha: 0a5795df721f762fc94cdfb3f9b6f8601810451c
version: 0.9.2a2
last_verified: 2026-08-31
normative_authority:
  - docs/03_execution/sprint_active.md
  - docs/03_execution/backlog.md
relationships:
  - execution.milestones
  - execution.backlog
  - decision.index
reviewer: principal-architecture-convergence-review
confidence: high
---

# Current Execution Intent

## Authoritative source

This file is the current execution board for the repository subject named by
`analysis_subject_sha`. Generated indexes and historical reports route work but
do not override this board, source, tests, or receipts.

## Uncontested current controls

- Lane A owns runtime, execution, persistence, clients, packaging, deployment, operations, and release surfaces.
- Lane B owns domain/ports contracts, schemas, projections, evaluation semantics, falsifiers, experiments, and promotion criteria.
- Each lane has WIP=1 and one current package.
- Package progression is predicate-driven; product-time approval for privileged effects remains separate from development workflow.
- Exact-subject verifier receipts, not prose or green test counts, close evidence gates.

## Board-declared current packages

| Lane | Package | Board state | Declared next action |
|---|---|---|---|
| A | `BEP-01..03` | `TECHNICAL COMPLETE` | Subject-bound completion evidence, versioned model capabilities/dialect projection, and typed semantic recovery are implemented and validated through the existing runtime seams. |
| B | `CMX-06` / `CMX-07` | `GATED` | Produce the accepted specialist ablation and execute the frozen repository-scale qualification set |

## Wave closure disposition and next stage

As of the exact implementation subject recorded in the accepted evidence
bundle (`0a5795df721f762fc94cdfb3f9b6f8601810451c`):

| Stage | Disposition | Evidence-backed boundary |
|---|---|---|
| Wave 1 (`REL-01`, `REL-02`, `CMX-01..03`) | `CLOSED` | Official runtime/evaluator seams, frozen single-attempt canary, three presets, port-backed intelligence, and durable cold-resume falsifiers pass; no live canary or performance claim is made. |
| Wave 2 implementation (`CMX-04`, `CMX-05`, technical `CMX-08`) | `TECHNICAL COMPLETE` | Multi-file/greenfield admission, thin facade/result parity, durable resume, and shared reference-agent path pass the hermetic suites. |
| Wave 2 qualification (`CMX-06`, `CMX-07`) | `GATED` | Specialist enablement still requires an accepted ablation; repository-scale qualification still requires an executed exact-evidence run. |
| 1-forge (`ADM-001..005`) | `COMPLETE` | `ForgeEngine`, `ForgeContextCompiler` (distillation + RFC-8785 JCS), `ForgeAtomicPatcher` (unified diffs, AST/block replace, rollback), `ForgeAdmissionGate` (strict freshness binding), and `vg-1-forge` preset implemented and verified with 100% test pass rate. |

The live canary remains `NOT_RUN` because no provider-backed execution was
authorized or available in this hermetic validation. M-8 therefore remains
subject to its existing empirical gate, and no 1.0, SWE-bench, or SOTA claim
is made. The first 1-forge change must preserve the existing `AdmissionGate`
and express the missing goal contract through the current runtime seam.

The BEP-01..03 technical verification bundle is green on the current
implementation subject: Kernel 97 tests, Agency 181 tests, Contracts 438
tests, Adapters 161 tests, and Benchmarks 53 tests. The bounded LAM campaign
also passed 9/9 challenges with zero provider spend. These are technical and
instrumentation results only. CMX-07 remains `GATED` pending a containerized,
exact-subject qualification run, and live SOTA/SWE-bench claims remain
`GATED` pending the official reproducible evaluator and independently accepted
receipts.

CMX-06 is technically complete on hermetic evidence. The mediated specialist
contracts provide advisory Reviewer, bounded Localizer, and test-scoped Test
Investigator layers over the existing artifact and child-runtime seams.
Reviewer verdicts are digest-addressed and advisory; Verifier retains sole
admission authority. The CMX-06 preregistration fixes one attempt per arm and
requires treatment cost-adjusted success to be no worse than control.
The CMX-06 focused topology/specialist/composition suite is 23/23 green.
The two LAM arms each remain 9/9 green with 17,100 tokens and $0 provider
spend; LAM is instrumentation evidence only.

The BEP-04 qualification implementation now exposes the three bounded
authority-free graph templates (`sequential`, `reviewer_in_loop`, and
`parallel_investigators`) through the existing topology lowerer and scheduler.
The parallel treatment is capped at two concurrent investigators, joins only
after both predecessors settle, and records lease acquisition/release events.
BEP-05 parity vectors cover Coding Max, Research, and Tutor manifests; the
read-mostly compositions do not declare patch or process-execution verbs.
Hermetic LAM replay passed 9/9 challenges for both `vg-1-forge` and
`vg-code-max` (17,100 tokens each, $0 provider spend). These results do not
qualify CMX-07 or authorize live SOTA/SWE-bench claims.

## Reconciled state and convergence rule

The subject above contains the generic completion, recovery, context, durable
state, delegation, topology, memory, Coding Max, and resume mechanisms. Stable
gates live in [milestones.md](milestones.md); package detail lives in
[backlog.md](backlog.md). M-8 remains blocked, M-9/M-10 remain unauthorized,
and the frozen canary remains `NOT_RUN`. Prior reviews remain non-canonical.
The locked architecture is thin app, thick declarative composition: one
runtime, ledger, tool path, store, and evaluator; policy outside the kernel;
infrastructure behind ports; optional mechanisms admitted by measured lift.

## Electroweak v0.9.2 backend-review disposition

The backend review and dormant prototypes under
`docs/reports/reviews/electroweak_v092/back/` are useful non-canonical design
inputs, not production owners. The review is directionally correct that the
shortest path to stronger general agents is consolidation, provider-neutral
behavior, durable recovery, bounded coordination, and exact evidence. Its
claims that new coordination and recovery planes are absent are stale against
the current source: topology lowering, workflow scheduling, child runtime,
artifact flow, protocol recovery, durable task state, and anti-progress-loop
mechanisms already exist.

The accepted production deltas are therefore:

1. `BEP-01` — make verification receipts unconditionally subject-bound for
   production write runs by task, composition, workspace postimage, executed
   command, and receipt identity. This extends the existing admission path.
2. `BEP-02` — add versioned model-behavior capabilities and dialect compilation
   at the existing model adapter boundary. Stable capability facts may be
   canonical values; volatile prices, availability, and observed reliability
   remain adapter/registry data. Unknown models use a conservative declared
   fallback and explicit missingness, never invented capability or price.
3. `BEP-03` — extend the existing protocol-recovery and durable task-state
   contracts with typed failure classes and semantic attempt fingerprints.
   Resume must retain spent recovery decisions; permission denial has no
   automatic retry; repeated unchanged actions must replan or terminate.
4. `BEP-04` — qualify existing topology/runtime mechanisms rather than adding
   `CoordinationPlan` or an in-memory mailbox. Start sequential, then admit at
   most three bounded topologies only after persisted artifact flow,
   cancellation, lease/backpressure, fairness, cold-resume, and cost-adjusted
   lift are demonstrated.
5. `BEP-05` — ship Research and Tutor as thin first-party compositions over the
   same public harness contract after Coding Max qualification. Their
   completion policies and tool/egress grants are domain-specific; their
   runtime, ledger, memory, and evaluator remain shared.

The report-tree `profile.py`, `dialect.py`, `recovery_policy.py`, `plan.py`, and
`mailbox.py` MUST NOT be copied wholesale. In particular, a mutable global
profile registry, hard-coded volatile pricing in domain values, a second
recovery ledger, an in-memory coordination mailbox, and fixed unmeasured
per-mille role shares are rejected. The admission-gate patch is a valid bug
hypothesis, but its optional checks are insufficient for the production path:
the caller must supply the bindings and missing bindings must fail closed.

Activation is evidence-led. Each behavioral treatment is introduced behind a
composition or adapter feature flag and compared with the frozen control on the
same task/model/attempt policy. Primary metrics are externally verified task
success and cost per solved task; secondary metrics are no-patch rate, protocol
failure rate, repeated-action rate, turns, tokens, latency, resume parity, and
instrument-error rate. LAM is smoke/replay evidence only. A live easy-task
check is diagnostic only. Neither may support a SWE-bench or SOTA claim.

For this review and its validation runs, the aggregate benchmark stop condition
is `$0.10` total provider spend, `1,000,000` total tokens, or `500` total model
calls, whichever is reached first. These are cumulative campaign ceilings, not
per-task allowances; retries, controls, treatments, mocks, and failed provider
requests count toward their applicable totals. Every run must persist the
pre-run remaining budget and observed post-run usage. Unknown usage stops the
campaign until reconciled rather than being treated as zero.

## Authorized closure sequence

### Sprint EWK-Q — evidence integrity and current sprint closure

The implementation portion of this sprint is closed. Its remaining M-8
empirical disposition is a qualification gate, not a reason to reopen the
completed Wave1/Wave2 technical packages.

| Order | Package | Owner | Deliverable | Exit predicate |
|---:|---|---|---|---|
| 1 | `REL-01/H0` | Lane B | Runtime-adapter benchmark driver; executable materialized tasks; exterior oracle; structural-only dry run | Dry-run emits no lift/cost/success; live fixture proves exact task, patch, trajectory and evaluator linkage |
| 2 | `REL-02/H1` | Lane B | Frozen content-addressed canary with `max_attempts=1` and explicit missingness | Manifest digest is fixed before live execution; invalid/unavailable tasks cannot count as failures or passes |
| 3 | `FIN-A1` | Lane A | Producer-signed M-8 bundle and independent disposition | Protocol, promotion separation, and rollback evidence are valid on one subject; the independent verdict is accepted as positive, negative, or undeterminable without reinterpretation |
| 4 | `W-092-5` | Both | Exact-subject qualification record | Required checks execute; claims match receipts; no local canary is called official SWE-bench |

The integrity predicates pass for the implementation subject. The empirical
treatment remains `NOT_RUN`; if it is later negative or undeterminable under
the preregistration, record that result and keep M-8 blocked. Do not tune the
threshold or manufacture replacement data. M-9 promotion remains blocked
until M-8 is actually accepted.

### Closed Wave1 handoff: `REL-01/H0`, `REL-02/H1`, and `CMX-01..03`

This packet is closed on the current implementation subject. The material
below is retained as the audit trail for the completed contract and falsifier
matrix; it is no longer the next implementation task.

**Required reading and source order**

1. `docs/execution/active.md` (this package and current authorization).
2. `benchmarks/m8_heldout/artifacts/preregistration.json` and
   `benchmarks/m8_heldout/fixtures/workload.json` (frozen protocol inputs).
3. `benchmarks/m8_heldout/runner.py` and
   `test/benchmarks/test_m8_heldout_runner.py` (defective implementation and
   executable falsifiers).
4. `vanguard/packages/adapters/models/openrouter.py`,
   `vanguard/packages/runtime/model_selection.py`, and the canonical runtime
   entrypoint (official model/harness path).
5. `vanguard/packages/runtime/evaluator_gateway.py` and evaluator port/adapter
   contracts (exterior verdict path).
6. Reverse-route every production file before editing and update its mapped
   canonical owner; report degraded navigation if the index subject is stale.

**Implemented requirements**

- The runner has no direct `urllib` provider client; the official model adapter
  and runtime path are injected without exposing credentials.
- The runner binds workspace, patch, trajectory, and evaluator observations to
  the exact task/base-commit identities when a live executor is supplied.
- Make dry-run a structural preflight only. It reports `NOT_RUN`/missing values
  for success, lift, tokens, cost, latency, promotion, and rollback; zero is not
  a substitute for missing empirical data.
- `max_attempts=1` is enforced at the driver boundary. Transport retries may recover
  the same provider request, but may not open a second episode or task attempt.
- Unavailable, invalid, timed-out, provider-failed, no-patch, patch-
  rejected, and evaluator-failed tasks as distinct typed dispositions. Only an
  applicable exterior pass counts as passed.
- The live-mode task title fallback is defined and malformed task
  records during preflight rather than during paid execution.
- Aggregate and per-task USD/token/time ceilings are checked before each call and
  persist observed provider usage; never recompute observed cost from a local
  price constant when provider billing is available.
- Producer-verifiable bundles are emitted only after every referenced artifact exists
  and its digest resolves. Promotion and rollback receipts remain separate from
  benchmark production and independent evaluation.

**Minimum falsifier matrix**

| Falsifier | Expected result |
|---|---|
| Dry-run with all fixtures present | Structural PASS; all empirical fields missing; no lift or promotion verdict |
| Non-empty model prose with no patch | `NO_PATCH`, never passed/grounded/verified |
| Patch applies but exterior tests fail | evaluator failure; task not passed |
| Zero tests collected | verification failure |
| Second episode requested | driver rejects the attempt |
| Provider unavailable or budget exhausted | typed missingness; denominator policy follows preregistration |
| Task/base commit or artifact digest tampered | bundle verification fails closed |
| Credential appears in prompt, event, patch, log, or artifact | stop-ship |
| Fake official runtime adapter and evaluator | hermetic integration test proves wiring without network |

The package handoff includes the commands actually run, exact counts, zero
test failures, and the resulting subject digest. Live provider execution is
not required for the Wave1 implementation gate and remains explicitly
`NOT_RUN`.

### Completed Wave2 technical slice — Coding Max vertical slice

This implementation sequence produced one useful first-party agent while
strengthening the general framework through existing seams. CMX-06 and CMX-07
remain qualification-gated as recorded above.

**Board convergence, recorded honestly (2026-08-31):** Wave1 and the Wave2
technical implementation slice are now closed on hermetic evidence. The
frozen content-addressed canary under
`benchmarks/m8_heldout/artifacts/canary_manifest.json` pins ten single-attempt
rows and explicit missingness. CMX-04/05 and technical CMX-08 pass their
falsifiers. CMX-06 remains disabled pending an accepted ablation and CMX-07
remains pending an executed exact-evidence qualification. No milestone is
marked accepted by this note; no 1.0 or benchmark claim is made.

| Order | Package | Primary location | Required outcome |
|---:|---|---|---|
| 1 | `CMX-01` composition delta | `packs/code-default/`, existing manifests | Reconcile current mechanisms with one `fast`, one `balanced`, and one `max` policy; no duplicate coordinator or store |
| 2 | `CMX-02` repository intelligence | `ports/index.py`, adapters, code-pack tool bindings | Search, symbol, dependency, test mapping and repository map with deterministic fallback, provenance and path containment |
| 3 | `CMX-03` durable work loop | code-pack planner/context/recovery policy + existing runtime projection | Understand/explore/localize/plan/edit/verify/recover/complete; resume restores the next action and failed-attempt memory |
| 4 | `CMX-04` multi-file and greenfield | code-pack policy and fixtures | Change-surface closure, affected-test selection, scaffold/baseline policy, explicit non-test evidence rules, and no silent verification bypass |
| 5 | `CMX-05` product facade | `vanguard/packages/apps/coding_max/` + shared application service | `vg code` and API invoke the same composition and expose status, resume, evidence and cost without owning execution |
| 6 | `CMX-06` qualification | hermetic fixtures + controlled live canary | Internal repository-scale bug, multi-file feature, and greenfield tasks pass; cost/turn/token regressions are reported |

The sprint stop-ship conditions are path escape, capability or budget expansion,
direct model/provider HTTP in product logic, host subprocess execution outside
the environment port, zero-test/stale-receipt admission, duplicated effects on
resume, synthetic benchmark metrics, missing trajectory links, or an adapter
importing `apps`.

## First-party agent portfolio toward 1.0

The framework is not complete merely because custom agents are theoretically
composable. The supported portfolio must dogfood the same public composition
contract:

1. **Coding Max** — write-capable autonomous engineering agent; first release
   priority and the only agent allowed to block the Coding Max sprint.
2. **Code Reviewer** — read-only or patch-suggesting critic using sequential
   mediated child lineages; it cannot override failed verification.
3. **Research** — bounded evidence-producing agent with explicit egress policy
   and citation artifacts; no web capability is implied until the port exists.
4. **Tutor** — read-only repository explainer proving a different completion
   policy and context organization on the same framework.

Research, Reviewer, and Tutor are reference-product gates for 1.0, not reasons
to delay the first useful Coding Max vertical slice. Swarm, branch search,
SBFL, mutation testing, ToolScript, skill distillation, and self-modification
remain opt-in experiments until preregistered ablations show lift exceeding
their cost and reliability burden.

## 1.0 release horizon

M-9 and M-10 retain their existing `0.9.0b1` and `0.9.0` meanings. A future
1.0 release is non-authorizing until M-10 closes. Its minimum gate is:

- a stable, documented public composition/port contract with compatibility tests;
- installable Coding Max plus at least two supported non-coding reference agents;
- repository-scale bugfix, multi-file, and greenfield qualification with exact
  model, cost, token, latency and evaluator disclosure;
- restart/resume, migration, backup/restore, security, performance and soak
  evidence on the exact release subject;
- no SOTA claim without an official or independently reproducible benchmark and
  ablations that isolate harness lift from model lift.

## Locked decisions and deliberately open variables

The next session MUST NOT reopen these decisions without contradictory current
source evidence or a formal architecture change:

- hybrid disposition: B control model + A rollout discipline + measured C ideas;
- thin app, thick composition; one runtime, ledger, tool path, store and evaluator;
- coding policy outside kernel; infrastructure adapters do not import apps;
- sequential execution by default; delegation is mediated and budget-attenuated;
- completion requires task-appropriate fresh evidence; model prose is never verification;
- durable state is event/artifact-derived; resume cannot duplicate settled effects;
- optional intelligence providers enrich observations but never control authority;
- M-8/M-9/M-10 and official benchmark claims remain evidence-gated.

These variables remain intentionally open because evidence, not architecture,
must select them: exact preset token/turn/USD ceilings, context-ranking weights,
model routes, SBFL metric, reviewer trigger rate, concurrency, branch width, and
mutation intensity. Each receives a conservative default in its implementation
package and may change only through a preregistered measurement with rollback.
