---
id: execution.active
canonical_id: execution.active
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: UNRESOLVED
owner: repository-governance
canonical_for:
  - current work/state/ownership
purpose: Represent current execution intent exactly as the active board states it, including unresolved internal status conflicts.
audience:
  - contributor
  - release-owner
analysis_subject_sha: d639ec4bda5ea7d8836a182393498a31fc43ea1a
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
| A | `FIN-A1` | `BLOCKED` | Hold the M-8 acceptance boundary; review only an exact producer bundle emitted by the repaired benchmark path |
| B | `REL-01` / `H0` | `IN_PROGRESS` | Replace the synthetic/direct-HTTP held-out runner path with runtime-adapter execution and honest missingness |

## Reconciled state on the exact subject

The clean local and remote branch subject is
`d639ec4bda5ea7d8836a182393498a31fc43ea1a`. The generated Tier-1 context names
`7d46c7f5528cf23a7b6cfcd6e02ece4d7f32e6a0`, while generated knowledge and
several canonical architecture headers name still older subjects. Navigation
artifacts are therefore usable only as routing hints until regenerated from
this exact subject.

The current source contains the generic completion-admission, protocol-recovery,
L1-L5 context, reconstructible coding-state, meta-controller, index-port,
delegation, topology, artifact, memory, and learning mechanisms. Focused tests
for admission/recovery, coding state, context policy, runtime meta-control, and
the M-8 runner pass, and the boundary and TCB checks pass. This demonstrates
mechanism presence only.

The committed M-8 held-out runner is not admissible empirical evidence yet:

- dry-run outcomes, token counts, costs, and lift are synthesized;
- live execution calls OpenRouter directly instead of the official runtime
  model adapter and does not execute the AETHER harness or an exterior oracle;
- live mode contains an unresolved `title` name in prompt construction;
- non-empty model prose is treated as passed, grounded, and verified;
- no producer-signed exact-subject bundle or independent acceptance exists.

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

This is the only active implementation sprint. Coding Max feature expansion is
staged in the backlog until this sprint exits.

| Order | Package | Owner | Deliverable | Exit predicate |
|---:|---|---|---|---|
| 1 | `REL-01/H0` | Lane B | Runtime-adapter benchmark driver; executable materialized tasks; exterior oracle; structural-only dry run | Dry-run emits no lift/cost/success; live fixture proves exact task, patch, trajectory and evaluator linkage |
| 2 | `REL-02/H1` | Lane B | Frozen content-addressed canary with `max_attempts=1` and explicit missingness | Manifest digest is fixed before live execution; invalid/unavailable tasks cannot count as failures or passes |
| 3 | `FIN-A1` | Lane A | Producer-signed M-8 bundle and independent disposition | Protocol, promotion separation, and rollback evidence are valid on one subject; the independent verdict is accepted as positive, negative, or undeterminable without reinterpretation |
| 4 | `W-092-5` | Both | Exact-subject qualification record | Required checks execute; claims match receipts; no local canary is called official SWE-bench |

Sprint EWK-Q closes when all four integrity predicates pass; the empirical
treatment need not be positive. If it is negative or undeterminable under the
preregistration, record that result and keep M-8 blocked; do not tune the
threshold or manufacture replacement data. Product capability work may then be
scheduled, but M-9 promotion remains blocked until M-8 is actually accepted.

### Next-session implementation packet: `REL-01/H0`

The next developer starts here; no new architecture pass is required.

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

**Implementation requirements**

- Delete the runner's direct `urllib` provider client. Inject or compose the
  official model adapter through the runtime path without exposing credentials.
- Replace generated task outcomes with real workspace materialization, one
  AETHER run, a pure unified patch, and an exterior evaluator verdict bound to
  the exact task/base commit/workspace/trajectory/patch digests.
- Make dry-run a structural preflight only. It reports `NOT_RUN`/missing values
  for success, lift, tokens, cost, latency, promotion, and rollback; zero is not
  a substitute for missing empirical data.
- Enforce `max_attempts=1` at the driver boundary. Transport retries may recover
  the same provider request, but may not open a second episode or task attempt.
- Treat unavailable, invalid, timed-out, provider-failed, no-patch, patch-
  rejected, and evaluator-failed tasks as distinct typed dispositions. Only an
  applicable exterior pass counts as passed.
- Remove the undefined live-mode `title` reference and reject malformed task
  records during preflight rather than during paid execution.
- Enforce aggregate and per-task USD/token/time ceilings before each call and
  persist observed provider usage; never recompute observed cost from a local
  price constant when provider billing is available.
- Emit a producer-verifiable bundle only after every referenced artifact exists
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

The package handoff must include commands actually run, exact counts, remaining
failures, and the resulting subject digest. Live OpenRouter execution is not
required to merge H0; it begins only after H0's hermetic adapter/evaluator path
and H1's frozen manifest are independently reviewed.

### Next product sprint — Coding Max vertical slice

This sprint becomes active only after EWK-Q disposition frees both WIP lanes.
It is designed to produce one useful first-party agent while strengthening the
general framework through existing seams.

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
