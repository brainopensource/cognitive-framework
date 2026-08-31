---
id: execution.active
canonical_id: execution.active
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: WAVE_1_CLOSED_WAVE_2_TECHNICAL_COMPLETE
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
| A | `1-FORGE/ADM-001..005` | `COMPLETE` | Core Reflexive Micro-Forge (`vanguard/packages/agency/forge/`), atomic patcher, admission gate, and contract/agency suites pass 100% GREEN. |
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

## Reconciled state on the exact subject

The production implementation subject reviewed for this plan is
`0a5795df721f762fc94cdfb3f9b6f8601810451c`. Generated navigation artifacts
were refreshed from this subject after implementation; they remain routing
projections and do not override current source, tests, or receipts.

The current source contains the generic completion-admission, protocol-recovery,
L1-L5 context, reconstructible coding-state, meta-controller, index-port,
delegation, topology, artifact, memory, learning, Coding Max policy, facade,
and cold-resume mechanisms. The required suites, falsifiers, boundary, TCB,
isolation, secret, duplication, documentation, and knowledge checks pass.

The M-8 held-out runner is now structurally truthful: dry-run is preflight-only,
live execution is injected through the runtime and exterior-evaluator seams,
prose is not a patch or a pass, and missing usage is explicit. The frozen
canary is valid and content-addressed, but it has not been executed against a
provider. The signed M-8 bundle currently present verifies the durable-memory
falsifier evidence; it does not substitute for the separate empirical held-out
lift gate.

Consequently M-8 remains blocked, M-9/M-10 remain unauthorized, and no
SWE-bench or release claim is made.

## Stable package contracts

The active board supplies current authorization; the [milestones.md](milestones.md)
supplies the stable M-4–M-8 package contracts, lane ownership, dependencies, acceptance predicates,
and evidence obligations. This candidate view links that detail rather than copying its mutable
tables, so package status cannot be mistaken for a second active board.

## Three-solution convergence decision

The review corpus under `docs/reports/reviews/electroweak_v091/3_body/` is
non-canonical design input. None of the three solutions is authorized for
wholesale application.

| Proposal | Adopt | Reject or defer | Disposition |
|---|---|---|---|
| Solution A | Pack-local presets, deterministic fast path, explicit plan/TODO artifacts, conditional review, feature-gated rollout | Parallel tool runtime, duplicate durable store, branch search, mutation, capsules, and distillation before measured lift | Behavioral source for pack policy; not a file-level patch plan |
| Solution B | Provider-neutral repository intelligence, epoch-safe progressive context, evidence-gated TODO transitions, non-identical recovery, fast-to-deep escalation that preserves discoveries | Adapter-to-app imports, host subprocess verification, large application-side coordinator, and direct copy of its report-tree prototype | Primary control-model reference after boundary repair |
| Solution C | Thin product application concept, deterministic complexity classes, layered verification, SBFL and mutation as testable hypotheses, single-attempt qualification discipline | Unsupported performance/benchmark statistics, invented APIs, premature product-family expansion, auto-rollback, and mandatory swarm/SBFL/mutation | Product direction and experiment backlog only |

The selected architecture is **thin app, thick declarative composition**:

```text
vg / API
  -> apps/coding_max            thin request/result facade and preset selection
  -> runtime                    the only composition, lifecycle and ledger authority
  -> code-default composition   planner, context policy, coding recovery and admission policy
  -> ports                      generic model/index/sandbox/store contracts
  -> adapters                   infrastructure implementations; never import apps or coding policy
```

No second runtime, event system, tool broker, persistence store, evaluator, or
authority path may be introduced. Repository-intelligence tools must be backed
by `IndexPort` or another generic port. Commands and tests must execute through
the mediated environment/sandbox path. Large state remains content-addressed
artifacts referenced by ledger events; `CodingTaskState` remains a projection.

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
