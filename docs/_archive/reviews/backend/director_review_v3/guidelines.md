---
id: director-review-v3-autonomous-delivery-guidelines
class: review
authority: non-authorizing
canonical_for: []
status: historical-advisory
owner: engineering-review
version: "3.0.0"
last_verified: 2026-08-27
audited_branch: feat_higgs_M4_M8
audited_head: c3dc123
---

# AETHER v0.9 Autonomous Two-Lane Delivery Method

## 1. Executive verdict

AETHER does not need a new architecture. It needs a disciplined completion program around the
architecture already present. The domain-blind S0–S12 Kernel, canonical Runtime composition seam,
event-sourced causal ledger, content-addressed artifacts, derived projections, mediated
capabilities, versioned schemas, provenance, replay, and generator/evaluator/promoter separation
are the correct foundation and must be frozen.

The repository is not currently buildable or releasable as AETHER v0.9. At audited HEAD
`c3dc123`, the structural linters pass, but the full Python suite fails with 2 failures and 17
errors, the CLI TypeScript test command fails 3 of 8 test files, the wheel cannot be built from the
available locked environment, the Python manifest loader points at a nonexistent schema location,
the Python `vg.4` reader contradicts its JSON Schema, package versions disagree, and the installer
is a checkout shim rather than a distribution installer. Several M-4–M-8 mechanisms are real and
substantial, but milestone evidence and operational product closure remain incomplete.

The definitive execution model is exactly two autonomous lanes:

- **Lane A — Execution and Product:** runtime, Kernel/Agency execution, causal persistence,
  recovery, services, integration, clients, packaging, deployment, and operations.
- **Lane B — Contracts and Intelligence:** domain contracts, schemas, projections, verification,
  experiments, generality, evaluation, authorized memory semantics, skills, learning, and
  promotion.

There is no Dev C, Leadership gate, committee, mandatory cross-review, or approval between work
packages. Each lane implements, self-reviews, runs its owned checks, fixes failures, integrates its
own branch, and advances when objective exit predicates are true. A separate software verifier
identity may countersign evidence, but this is an automated role separation, not a human review
dependency. Product-time human approval for privileged effects remains a security capability and
must not be confused with development-process approval.

The release sequence is reset coherently:

| Range | Version meaning |
|---|---|
| M-1–M-3 | Historical v0.6.x foundation; preserved, not reimplemented |
| M-4–M-6 | v0.7.x capability completion |
| M-6.5–M-8 | v0.8.x internal/MVP capability line |
| M-9 | `0.9.0b1` operational beta: integrated product, install, clients, plugins, workflows |
| M-10 | `0.9.0` final: reliability, migration, security, packaging, deployment, release proof |

This supersedes the future-version mapping in descriptive planning that labels M-7/M-8 as v0.9
or M-9 as v1.0. It does not rewrite history or change existing tags. `v1.0` becomes a post-M-10
successor decision and is not used as a synonym for “first integrated product.” The consequence is
that M-8 remains a technical MVP boundary, M-9 becomes the beta product boundary, and only M-10
may issue the requested final v0.9 release.

## 2. Audit basis and evidence

This report was produced code-first from the current working repository, the approved
`TODO_PROMPT.md`, the latest README/SPEC/execution documents requested by the Project Owner, both
v2 Director reports, accepted ADRs through 0103, Git history and tags, schemas, packaging metadata,
CI workflows, Python and TypeScript implementations, tests, and local executable gates.

### 2.1 Exact repository observations

| Observation | Result at audit |
|---|---|
| Branch / HEAD | `feat_higgs_M4_M8` / `c3dc123` |
| Working tree before report | Pre-existing review files were staged/untracked; they were treated as user-owned and untouched |
| Tags | `v0.0.0-sprint0`, `v0.4.0-sprint4`, `v0.4.1-beta`, `M-5-BASE`, local `M-5A-BASE-v2`; no v0.6/v0.7 release tags |
| Python full suite | 2,003 tests; **2 failures, 17 errors, 8 skipped** |
| Python root cause group | 17 errors share `ManifestLoader` schema path `vanguard/schemas/...`, which does not exist; schemas are at repository root |
| Other Python failures | Two stale model-pricing expectations (`140000 != 150000`, `0.000145 != 0.00024`) |
| Test hygiene defect | Full tests mutate tracked `tools/002_LLM_API_MOCK/lam.sqlite`; the audit restored that mutation |
| TypeScript | Root `npm run typecheck` passes; root `npm test` fails `transport`, `wave2`, and `wave4` test files |
| Root npm scope | Only `@vanguard/cli` is checked; Studio and client-core test suites are not root gates |
| TCB | PASS, 1,373 logical LOC / 1,438; 65 logical LOC remain |
| Boundaries | PASS, 409 Python source files |
| Domain blindness | PASS, with missing retired `layer0/` reported as a warning |
| Isolation / secrets / event coverage | PASS |
| Code generation / RF allocation | PASS |
| Execution truth linter | PASS vocabulary/state model, but it does not establish product correctness |
| Wheel | Normal build attempted network access for build isolation; local no-isolation build failed because `bdist_wheel` is absent from the declared/available environment |
| Installer | `install_vanguard.sh` writes a `PYTHONPATH` wrapper tied to the checkout; it does not install a wheel, dependencies, assets, signatures, or uninstall metadata |

The commands were diagnostic only. No production, test, configuration, or canonical documentation
file was intentionally changed. The test-mutated SQLite fixture was restored.

### 2.2 Audited-commit versus current-HEAD distinction

The v2 Director reports audited `624d80f`. The active board cites verification subject
`15fbb751...`. The approved `TODO_PROMPT.md` describes an intermediate state before Waves 5B–9.
Current HEAD is `c3dc123`. Between the active board's subject and HEAD, the branch added or changed
service security, evidence tooling, recursion, graph coloring, M-6.5 evidence, topology, memory,
learning, CLI/client/Studio surfaces, schema/code generation, packaging entries, and hundreds of
tests. Therefore:

- v2 findings are historical evidence, not a current status oracle;
- `TODO_PROMPT.md` is the approved design reference, but many of its P0 repairs now exist;
- later code must be tested against the intended falsifier, not credited by commit title;
- commit titles such as `docs(Convergence...)` cannot be used to infer scope or acceptance because
  they contain large production changes.

## 3. Current-state diagnosis

### 3.1 Classification vocabulary

- **Implemented:** production path exists and the relevant focused behavior is executable.
- **Partial:** useful code exists, but a required public integration, durability, security, or
  operational property is absent.
- **Missing:** no production implementation exists.
- **Obsolete:** historical proposal/status no longer describes HEAD or is superseded.
- **Regressed:** a previously accepted invariant currently fails or its gate is red.
- **Contradictory:** two active representations prescribe incompatible behavior or status.

### 3.2 Code/document reconciliation

| Item | Code-first status | Evidence and correction |
|---|---|---|
| Hexagonal lattice | Implemented | Boundary linter passes; adapters remain outside Kernel/Agency dependencies |
| Domain-blind Kernel | Implemented | Domain-blindness passes; TCB at 1,373/1,438 |
| S0–S12 dispatch, grants, typed four-dimensional budget | Implemented | Kernel and contract suites exist; preserve exact additive dimensions and depth/turn ceilings |
| Runtime composition seam | Implemented | `CanonicalManifest → FrozenComposition → ActivationPlan → RunPlan → Runtime.run_composed` exists |
| Event-sourced causal truth | Implemented with new product regression | Core SQLite WAL/reducers work; `RuntimeService` single-history repairs exist, but the full suite is red and mutable run-status tables still coexist as projections |
| Artifact store/provenance | Implemented/partial | Blob/CAS and evidence refs exist; install/package inclusion and full release dereference remain unproved |
| Replay vs re-execution | Implemented contract, partial product | Cold fold/checkpoint primitives exist; final CLI/service recovery E2E and migration matrix remain release work |
| `AgentView` projection | Implemented | `/2` events, checkpoints, projection tests and compatibility readers exist; successor baseline remains unresolved |
| Event `/2`, dual-read `/1|/2`, single-write `/2` | Implemented in ledger path | Schema families coexist correctly in principle; unrelated v4/mhf schema duplication is not fully governed |
| Trajectory `/2`, dual-read `/1|/2` | Implemented | Writers/readers and tests exist; M-4 qualifying artifact remains `undeterminable` |
| M-4 RF-95 | Partial | Candidate executed; current bundle explicitly says preregistration/artifact reconstruction made outcome undeterminable |
| M-5a baseline | Partial/contradictory | Mechanism implemented; local `M-5A-BASE-v2` is contaminated/unpublished; `CONVERGENCE-BASE-v1` is only a candidate artifact, not a remote accepted baseline |
| M-5b graph coloring | Implemented mechanism, unaccepted experiment | Pack/oracle/vectors/material bundle exist; comparison control is unresolved |
| M-6 delegation | Implemented mechanism, evidence open | Real `ChildRuntimePort`, durable IDs and attenuation code exist; clean-subject depth/kill-tree bundle is missing |
| M-6.5 meta-control | Implemented and evidence-accepted under current board | Signed paired-study and acceptance envelope exist; enablement must remain profile-scoped |
| M-7 topology | Partial | Parser/lowering/authority rejection and `RunPlan.extensions` are integrated, but `run_composed` only lowers and computes an order; it does not execute the declared role operations as real M-6 children. ADR-0099 correctly chooses `SEQUENTIAL_CONFIRMED` |
| M-8 memory | Partial with a live fail-open defect | Signed memory leases and durable adapter exist, but `InMemoryMemoryPort.write/recall` still accept the legacy nonempty-string disjunct; GC deletes metadata only and CAS sweep/backup/restore evidence is incomplete |
| M-8 governed learning | Partial/duplicated | `governance/learning.py`, `skill_evaluation.py`, and `skill_lifecycle.py` overlap. One path enforces separated signed promotion; `DurableCompositionRegistry.restore/rollback` accepts no signed rollback evidence |
| Backend service trust repairs | Mostly implemented | Per-install keys, non-TTY denial, strict approval decision, gateway auth/origin/body limits, canonical append, cancellation and checkpoint work landed after the approved guide |
| `vg.4` contract | Contradictory | JSON Schema rejects fields that handwritten `contract.py` permits (`model`, `episodeId`, `expectedSeq`, `offset`); docstring cites nonexistent cross-language vector tests |
| Manifest schema | Regressed | Fail-closed validation was added, but `SCHEMA_PATH`/`NAMED_SCHEMA_PATH` resolve under nonexistent `vanguard/schemas`, breaking 17 tests |
| Schema inventory | Contradictory/obsolete | Root `schemas/mhf` and `schemas/v4` contain overlapping manifest/event contracts; `schemas/v4/MANIFEST.md` still labels many present/used contracts DRAFT or omits runtime service |
| Python package | Partial | Metadata and console scripts exist; no demonstrated clean wheel and root-level packs/schemas are outside `find_packages(include=["vanguard*"])` |
| TypeScript clients | Partial/regressed | Strict typecheck passes; tests fail; CLI/client-core/Studio versions remain `0.4.1-beta` while Python is `0.7.3.dev0`; root CI ignores two workspace test suites |
| Operational deployment | Missing | No supported service unit/container composition, migration command, backup/restore runbook, health/SLO contract, or signed release artifact |
| M-9/M-10 | Missing by design | Current law reserves seams only; this report supplies implementable definitions for the new objective |

### 3.3 Valid architecture, stale material, and blockers

**Valid architecture to retain:** the lattice; Runtime as composition root; event truth and WAL;
causal hash/provenance chain; CAS artifacts; derived projections; S0–S12 mediation; typed budgets;
optional assurance profiles; schema versioning; dual-read/single-write; single sequential reference
scheduler; event/telemetry separation; memory authorization before ranking; immutable composition
promotion; generator/evaluator/promoter separation.

**Stale or obsolete statements:** the pre-Wave-5B security defect inventory in
`TODO_PROMPT.md`; its assertion that ADR-0099 does not exist; its claim that topology has zero call
sites; its claim that no acceptance tooling/envelopes exist; old Dev C/Leadership ownership;
M-7/M-8 percentages; old M-9=v1.0/M-10=research-only sequencing; README's “roughly 90%” statement;
and historical documents that treat mechanism presence as milestone closure.

**Real technical dependencies:** schema/resource convergence before pack execution; green canonical
runtime before evidence reruns; valid baseline before M-5b comparison; real recursion before
topology role execution; topology disposition and valid M-6.5 result before M-8 promotion
experiments; durable memory and promotion before product workflows; product integration before
hardening; migration/recovery before final v0.9.

**Purely administrative blockers to remove:** Leadership creating a tag, Leadership writing a
decision already determined by a threshold, a named Dev C, mandatory independent human review,
daily checkpoints, task authorization from a sprint board, remote artifacts not necessary for the
next code change, and “M-8 acceptance before any M-9 thought.” These become deterministic lane
decisions and executable entry predicates. Remote publication remains a release operation, not a
coding prerequisite.

## 4. Historical reconstruction of M-1, M-2, and M-3

No historical requirement is invented here. The reconstruction uses current SPEC compatibility
rows, ADRs 0069–0089, commit content, and surviving tests. There are no v0.6 release tags, so commit
lineage—not a nonexistent tag—is the historical anchor.

### 4.1 M-1 / v0.6.0 — trust spine

M-1 established the domain/ports/kernel production lattice, S0–S12 dispatch, Ed25519 exterior
verdict path, grant attenuation, budgets, canonicalization, event/receipt truth, fail-closed policy,
and F-01…F-21 gating. Relevant implementation arrived through the August 18 microkernel work and
the v0.6.0 Wave-1 sequence ending at `f949dc6`; Wave-2 convergence at `05962d2` removed large
duplicate `layer0` Kernel/event/SPI surfaces and decomposed the runtime. Current SPEC records M-1 as
complete. It is historically accepted, but current product surfaces must continuously preserve it;
the service trust regression documented in WP-C1 was a regression, not a reason to redefine M-1.

### 4.2 M-2 / v0.6.1 — truthful trajectories and continuation

ADR-0078 defined RF-23: invoked-turn attribution, explicit measurement status, conserved cost, and
separate `D_H/D_R/D_X` identity in `mhf.trajectory/1`. ADR-0082 defined RF-25: destroy live state,
reopen a file-backed SQLite-WAL ledger in a fresh process, reconstruct, reconcile, append
`RunRecovered`, and complete the trajectory without truncating its prefix. The history labels
`cf3e6bc` as the original M-2 gate closure, followed by corrections and the explicit “M-2 Closed”
transition at `1d1f956`. Current code retains these mechanisms and `/2` successors. M-2 is accepted
history, while any new dual-writer, lossy envelope, or nominal resume is a regression against it.

### 4.3 M-3 / v0.6.2 plus M-3C/W-3D — composition convergence

ADRs 0077, 0079, 0081, 0083, and 0088 established named component graphs, absent-versus-forged
semantics, plugin lifecycle, `mhf.manifest/2`, compatibility ingress, and removal of live `layer0`.
Commits `3a5b581` through `21a399a` implemented schema/registry/compatibility pieces. Because those
were initially side paths, M-3C then froze the only production chain and RF-78…RF-84; `136436e`
closed that convergence in code. W-3D/ADR-0089 added identity-bearing execution profiles,
`RuntimeBootstrap`, material activation handles, durable streaming truth, and the generic product
entrypoint. Current SPEC and board treat M-3C/W-3D as accepted. The historical label “M-3 complete”
means these final converged mechanisms, not every intermediate v0.6.1 state.

### 4.4 Historical preservation rule

M-1–M-3 are not rerun as feature projects. Their lane packages below are preservation packages:
repair regressions, keep compatibility readers, and demonstrate the smallest retained anchor set.
No later milestone may reinterpret their requirements or manufacture v0.6 tags.

## 5. Architectural decisions to freeze

The following are constitutional invariants. A lane may not change them silently. A change requires
a successor ADR, a new schema/version where applicable, a migration, and a falsifier proving the
old invariant is no longer adequate.

1. **Domain-blind Kernel:** no coding, topology, memory, skill, model, or evaluator semantics in
   `kernel/`; TCB remains at or below 1,438 logical LOC until explicitly superseded.
2. **One concrete seam:** Runtime composes and activates concrete adapters. No CLI, service, lab,
   plugin, or child path owns a second engine.
3. **Events are canonical causal truth:** projections, indexes, status tables, telemetry, and caches
   are derived and rebuildable. One writer commits before notification.
4. **Artifacts are immutable content:** content is persisted before the event that references it;
   digest knowledge alone never authorizes dereference.
5. **Agent state is derived:** `AgentView` is a fold; no live object is required for semantic
   continuation.
6. **Replay is not re-execution:** replay reconstructs state without effects; resume reconciles
   occurrence before new effects; re-execution creates new lineage/identity.
7. **Capabilities mediate effects:** authority attenuates monotonically; additive costs are
   `usd_micros`, `millis`, `tokens`, `bytes`; depth and turns are ceilings.
8. **Schemas evolve by dual-read/single-write:** old bytes remain immutable; new incompatible
   shapes receive new identifiers; JSON Schema/JCS/golden vectors are authoritative.
9. **Identity and provenance remain separated:** `D_H`, `D_R`, and `D_X` answer different
   questions; authority provenance and environment/profile identity are explicit.
10. **Retention and reproducibility are vectors:** absent/unknown is not zero or verified;
    capability is not execution evidence.
11. **Scheduling starts sequential:** ADR-0099 freezes `SEQUENTIAL_CONFIRMED`; later concurrency is
    bounded and evidence-driven without changing causal truth.
12. **Memory is a derived capability:** verify at use, scope before ranking/dereference, record
    retrieval provenance, support revocation/retention/legal hold.
13. **Promotion is over immutable compositions:** generator, evaluator, and promoter differ by
    identity/key/authority; CAS promotion and signed behavioral rollback are required.
14. **Negative experiments terminate:** a valid negative result selects the declared fallback and
    advances the roadmap; only invalid instrumentation requires repair.

## 6. Autonomous methodology

### 6.1 Operating principles

1. **Code first, contract before consumer.** The producing lane freezes the smallest versioned
   contract and vectors; the consuming lane implements against it.
2. **Linear work per lane.** Each lane has one active work package. The lanes run concurrently only
   when their owned files are disjoint and their input contracts are frozen.
3. **Large packages, small commits.** A package has one user-visible outcome and may contain a
   short linear commit series: contract/fixture → implementation → faults/migration → integration.
4. **No waiting for ceremony.** Entry predicates are repository facts. If true, start. If false,
   implement a stub/fixture that preserves the contract and continue on independent work.
5. **Self-review is mandatory; cross-review is optional.** The author rereads the diff against the
   package matrix and executes required checks. Automated independent verification supplies role
   separation for evidence.
6. **Fix forward.** A broken integration branch is repaired immediately by the lane that introduced
   the first failing commit. The other lane continues from its last green integration base.
7. **Defaults close decisions.** Missing optional infrastructure selects the documented local,
   sequential, lexical, single-host, fail-closed default; it never blocks the roadmap.
8. **Evidence is output, not permission.** Evidence describes whether the package worked. It does
   not require a manager to authorize the next task.

### 6.2 Task states

`READY → IMPLEMENTING → SELF_VERIFIED → INTEGRATED → COMPLETE`

`FALLBACK_COMPLETE` is a valid terminal state for a negative experiment. `BLOCKED` is used only
when neither lane can implement a safe default or fixture and an external resource is intrinsically
required for the final product. A package is never marked complete merely because files exist.

### 6.3 Information required before coding

Every package begins with an executable packet containing:

- baseline commit and clean/known-failure list;
- objective and excluded scope;
- owned file paths and prohibited paths;
- input/output types and schema identifiers;
- golden positive and negative fixtures;
- behavioral pseudocode and failure table;
- compatibility/migration/rollback rule;
- exact local and integration commands;
- objective completion predicate;
- next package identifier.

If any item is missing, the lane owner chooses the operational default from Section 9 and records
it in the package commit/board row; no external decision is requested.

## 7. Complete lane ownership model

### 7.1 Permanent ownership

| Surface | Lane A exclusive writer | Lane B exclusive writer |
|---|---|---|
| Domain/ports | — except A-owned implementation requests through frozen contract | `vanguard/packages/domain/**`, `vanguard/packages/ports/**` |
| Kernel/Agency | `vanguard/packages/kernel/**`, `vanguard/packages/agency/**` | Tests/falsifiers only; no production writes |
| Runtime core | `root.py`, `compose.py`, `run_plan.py`, `session.py`, `wiring.py`, `bootstrap.py`, profiles, delegation/child runtime, topology/scheduler, checkpoints, ledger/recovery, service, CLI | Projections, trajectory/evidence/reproducibility, meta-control, memory semantics, skill/evaluation/promotion modules |
| Adapters | model invocation, sandbox/environment, event/blob stores, service integration, deploy adapters | exterior evaluators, memory/retrieval algorithms, experiment adapters |
| Schemas/codegen | Consumes generated types; owns transport implementation | `schemas/**`, code generators, generated contract source |
| Packs | code-default operational integration | formal/general workloads and pack contract fixtures |
| Clients | `vanguard/clients/**` | Supplies generated types/vectors only |
| Tests | runtime/kernel/agency/adapters/integration/client/deploy tests | contracts/falsifiers/security/experiments/packs and shared vectors |
| Tooling | build, install, migration, operations, smoke tools | evidence, schema, baseline, experiment and semantic linters |
| Release | artifact assembly, SBOM, signatures, install/deploy | evidence manifest, compatibility matrix, verifier receipt |

Where current files mix concerns, ownership is symbol-level until a bounded extraction occurs. For
example, Lane B owns authorization/ranking contracts; Lane A owns SQLite transaction, WAL, backup,
and blob lifecycle implementation. Lane B owns promotion criteria/signature contract; Lane A owns
the durable registry transaction and served-version switch.

### 7.2 Shared-contract rule

There are no concurrently edited shared files. Lane B is the single writer for contract/schema
changes. It publishes a frozen commit containing generated readers and vectors. Lane A then rebases
its consumer branch onto that commit and edits only consumer surfaces. If Runtime reveals a
contract defect, Lane A supplies a failing fixture; Lane B revises the contract in a successor
commit; Lane A resumes. No meeting or approval is required.

### 7.3 Stubs and fixtures

- Ports receive deterministic fakes before real adapters.
- External providers use cassettes; unavailable live systems produce `not_available`.
- Migrations run against copied fixture databases with known schema digests.
- Distributed execution uses a local loopback transport stub until a measured M-10 need selects a
  network implementation.
- Plugin discovery uses signed local fixture bundles before marketplace/network work.
- Negative M-6.5/M-8 experiments select controller-off or previous composition automatically.

## 8. M-1 through M-10 linear work packages

Each milestone has one Lane A block and one Lane B block. Within a lane, execute blocks in numeric
order. A later block may start only when its listed input contract exists; milestone acceptance is
not a human gate.

### M-1 — Preserve the trust spine

#### A-M1 — Runtime trust regression closure

- **Objective/baseline:** retain accepted S0–S12/Ed25519 behavior and prove every product ingress
  uses it. Baseline is current Kernel plus repaired CLI/service at HEAD.
- **Files/symbols:** `kernel/**`; `runtime/keys.py`; `runtime/governance/approvals.py`;
  `runtime/service/{service,server,studio_gateway}.py`; `runtime/cli.py`; `ApprovalAuthority`,
  `ApprovalFlow`, `_cmd_ResolveApproval`, `interactive_approver`.
- **Contracts/schemas:** capability grant, approval decision, `vg.4` command envelope; no new event
  kind unless a red falsifier proves necessity.
- **Inputs/outputs:** signed challenge-bound decision in; canonical refusal or committed
  `ApprovalResolved` receipt out.
- **Behavior:** `parse → authenticate → locate challenge → verify key/signature/expiry/digests →
  authorize → append fact`; any failure stops before append/effect.
- **Invariants/errors:** I-5, no embedded seed, no non-TTY self-approval; typed
  `unauthenticated|permission_denied|not_found|not_available`.
- **Migration/telemetry/performance:** migrate no private keys; refuse insecure modes; count refusal
  reasons without secret material; verification p95 must stay below 10 ms locally.
- **Security/compatibility/rollback:** old unsigned/defaulted decisions remain historical and
  unreadable as authority; rollback is previous green trust-spine commit, never the insecure path.
- **Completion/next:** focused approval/gateway/CLI security tests plus secret scan pass; next A-M2.

#### B-M1 — Trust contract falsifiers

- **Objective/baseline:** make the trust claim mechanically falsifiable without human review.
- **Files/symbols:** approval/grant schemas, golden vectors, `test/security/**`, `test/trust/**`,
  semantic key/default linters.
- **Contracts/schemas:** strict required approval fields, signature preimage, registered-key roster.
- **Inputs/outputs:** valid/forged/expired/foreign/unchallenged fixtures in; deterministic expected
  error and no-occurrence assertion out.
- **Behavior:** generate boundary vectors, run both Python and TS readers, verify no state change for
  negative cases.
- **Invariants/errors:** unknown never passes; fixture must actually discriminate; malformed
  signature is invalid request, known-key bad signature is denied.
- **Migration/telemetry/performance:** version vectors append-only; report counts and duration;
  crypto vectors run in the fast suite.
- **Security/compatibility/rollback:** public test keys only; legacy reader cannot grant authority;
  revert a contract only with a successor schema.
- **Completion/next:** all negative vectors fail on an intentionally insecure test double and pass
  on production; next B-M2.

### M-2 — Restore one causal truth and cold continuation

#### A-M2 — Canonical service ledger and recovery

- **Objective/baseline:** preserve accepted RF-23/RF-25 and remove every product second truth.
- **Files/symbols:** `runtime/ledger_emitter.py`, `runtime/ledger/**`, `runtime/checkpoints.py`,
  `runtime/service/service.py`, adapters event store; `_append_canonical`, `_load_events`, resume,
  cancellation.
- **Contracts/schemas:** `mhf.event/1|2`, `mhf.trajectory/1|2`, checkpoint pins, occurrence states.
- **Inputs/outputs:** validated command and canonical envelope in; transactionally sequenced fact,
  stream frame, projection, or reconstructed state out.
- **Behavior:** `commit envelope → notify`; on resume `verify checkpoint → cold fold prefix →
  reconcile open effects → append RunRecovered → continue`. Never re-execute during replay.
- **Invariants/errors:** I-4/I-9; append failure returns `not_available` with no sequence or
  notification; uncertain occurrence is `undeterminable` and not retried blindly.
- **Migration/telemetry/performance:** mark old inbox event rows historical, migrate idempotently;
  cursor/gap/recovery metrics; no >10% median append or >20% p95 regression from pinned baseline.
- **Security/compatibility/rollback:** preserve envelope identity/provenance byte fields and tenant
  scope; dual-read old rows; rollback keeps new rows readable.
- **Completion/next:** fresh-process service E2E, crash boundaries, stream reconnect, and exact state
  digest pass; next A-M3.

#### B-M2 — Replay/trajectory contract authority

- **Objective/baseline:** converge event/trajectory schemas and prove full-history semantics.
- **Files/symbols:** `schemas/mhf/event*`, trajectory schemas, reducers/projections, compatibility
  readers and vectors.
- **Contracts/schemas:** writer `/2`; reader `/1|/2`; JCS digests; measurement missingness.
- **Inputs/outputs:** historical and current rows in; normalized immutable values and equal fold
  digest out.
- **Behavior:** validate → preserve original bytes → normalize aliases in memory → fold; partitioned
  folds equal full fold.
- **Invariants/errors:** broken sequence/hash/terminal duplication fails closed; unknown events are
  preserved, not discarded or defaulted.
- **Migration/telemetry/performance:** no ledger rewrite; optional checkpoint regeneration only;
  benchmark 1k/10k/100k folds and memory.
- **Security/compatibility/rollback:** provenance fields cannot be synthesized for `/2`; old readers
  remain until release matrix permits removal.
- **Completion/next:** RF-23/RF-25 plus metamorphic partition/serialization vectors pass; next B-M3.

### M-3 — Re-establish composition and schema convergence

#### A-M3 — Buildable canonical product chain

- **Objective/baseline:** repair the current manifest-resource regression and prove all entrypoints
  use the one Runtime chain.
- **Files/symbols:** `agency/manifests/loader.py`, Runtime compose/activate/run/bootstrap/entrypoint,
  registry lifecycle, package resources.
- **Contracts/schemas:** legacy `mhf.harness/1` compatibility ingress; authored
  `mhf.manifest/2`; `FrozenComposition`, activation and `D_H/D_R`.
- **Inputs/outputs:** packaged manifest/resource bytes in; activated handles and one RunPlan out.
- **Behavior:** resolve resources with `importlib.resources`; parse dialect → canonicalize → freeze
  → activate material services → run → reverse-close.
- **Invariants/errors:** no `parents[N]` repository arithmetic; missing schema/provider/interface/
  ref fails before first event; no `cell=None` production activation.
- **Migration/telemetry/performance:** no manifest rewrite; warn with typed deprecation; activation
  timing and failed component ID; disabled compatibility path has negligible overhead.
- **Security/compatibility/rollback:** legacy bytes normalize before authority; rollback retains
  reader, never restores duplicate runtime authority.
- **Completion/next:** repair 17 current errors; every shipped pack composes from source and an
  installed wheel; RF-78…RF-84 pass; next A-M4.

#### B-M3 — Single schema and generated readers

- **Objective/baseline:** eliminate the `schemas/mhf` versus `schemas/v4` and handwritten-reader
  contradictions.
- **Files/symbols:** `schemas/**`, `schemas/v4/MANIFEST.md`, code generators, generated Python/TS,
  `service/contract.py` replacement vectors.
- **Contracts/schemas:** designate one canonical schema per wire ID; `vg.4` gains one exact shape;
  unknown fields fail closed.
- **Inputs/outputs:** schema and shared vectors in; generated readers/types and compatibility report
  out.
- **Behavior:** schema → codegen → Python/TS vector tests → drift check. Never maintain two manual
  field lists.
- **Invariants/errors:** A-4/I-8; unresolved `$ref` is build failure; runtime dependency absence is
  startup failure.
- **Migration/telemetry/performance:** schema catalog records writer/reader versions and sunset;
  parsing remains bounded by 1 MiB ingress.
- **Security/compatibility/rollback:** security fields have no defaults; dual-read only for declared
  historical versions; revert generated output with schema commit atomically.
- **Completion/next:** one corpus is consumed by Python, client-core, CLI, and Studio; codegen check
  is clean; next B-M4.

### M-4 — Qualifying useful run and portable scientific capture

#### A-M4 — Product execution proof

- **Objective/baseline:** convert current `undeterminable` RF-95 material into one clean,
  preregistration-bound, portable product run.
- **Files/symbols:** Runtime release path, RF-95/SWE runners, artifact/blob/event stores, CLI run.
- **Contracts/schemas:** execution profile `/2`, trajectory `/2`, evidence `/1`, preregistration.
- **Inputs/outputs:** frozen task/provider/profile/commit/lock in; diff, verifier result, WAL,
  trajectory, artifact index and reconstruction receipt out.
- **Behavior:** preregister → initialize file stores → run canonical composition → mediate edit/test
  → checkpoint → destroy process → reconstruct → export content-addressed bundle.
- **Invariants/errors:** no `/tmp` unresolved artifacts, empty preregistration digest, fake provider,
  stitched trace, or manual repair; capture failure makes the evidentiary run fail.
- **Migration/telemetry/performance:** keep old candidate as undeterminable; record provider usage
  missingness honestly; publish execution/cost/latency vector, not a universal SLA.
- **Security/compatibility/rollback:** explicit product/sandbox profile and approvals; old bundle
  never overwritten; rollback discards only new candidate lineage.
- **Completion/next:** automated verifier reproduces all five RF-95 conditions from a clean install;
  next A-M5.

#### B-M4 — Evidence verifier and automated acceptance

- **Objective/baseline:** make release evidence independently checkable without a human reviewer.
- **Files/symbols:** `domain/evidence/**`, evidence runners/linters, acceptance key fixture/service.
- **Contracts/schemas:** `aether.evidence/1`; producer identity differs from deterministic verifier
  service identity.
- **Inputs/outputs:** producer bundle and pinned materials in; signed pass/fail/undeterminable
  acceptance envelope out.
- **Behavior:** resolve every digest → reproduce declared commands → verify pins/signature/outcome →
  countersign. The verifier cannot mutate the producer artifact.
- **Invariants/errors:** self-signing rejected; an undeterminable producer cannot become pass;
  missing remote publication may block release publication but not local code progress.
- **Migration/telemetry/performance:** append acceptance envelopes; report reproduction duration;
  keep fast structural verification separate from slower product run.
- **Security/compatibility/rollback:** verifier holds only its own key and read-only materials;
  evidence schema stays dual-readable.
- **Completion/next:** M-4 board state can be derived mechanically from bundle/envelope; next B-M5.

### M-5 — Event-derived agent and clean generality control

#### A-M5 — Projection/runtime preservation

- **Objective/baseline:** preserve `AgentView` and establish a clean successor baseline from a green
  integrated commit.
- **Files/symbols:** runtime checkpoints/recovery, event store, baseline preparation tool and CI
  clean-candidate workflow.
- **Contracts/schemas:** reducer pins, baseline manifest `/1`, remote annotated tag identity.
- **Inputs/outputs:** green commit/tree/lock/schema/reducer digests in; immutable baseline candidate
  and, at publication time, remote tag out.
- **Behavior:** run minimum gates → compute manifest → verify no treatment paths → sign with release
  automation → create annotated tag → verify remote identity when network is available.
- **Invariants/errors:** never move/recreate `M-5A-BASE-v2`; contaminated/lost remains history;
  publication failure queues retry and does not invalidate local development baseline digest.
- **Migration/telemetry/performance:** no ledger migration; benchmark projection fold/checkpoint;
  baseline creation logs exact tree.
- **Security/compatibility/rollback:** keys separated; rollback means choose prior commit, never move
  tag.
- **Completion/next:** `CONVERGENCE-BASE-v1` manifest validates locally and remotely before release;
  next A-M6.

#### B-M5 — Generality falsifier

- **Objective/baseline:** execute graph coloring only after the clean baseline, without protected
  substrate semantics.
- **Files/symbols:** formal graph-coloring pack, exterior evaluator, fixtures, RF-86/RF-98 tools.
- **Contracts/schemas:** canonical graph/witness values and signed verdict; protected path set.
- **Inputs/outputs:** sorted graph/k/task vectors in; verified witness/verdict/evidence and substrate
  diff out.
- **Behavior:** normalize graph → execute via Runtime → exterior oracle verifies completeness/range/
  edges → permute serialization → compare protected tree.
- **Invariants/errors:** evaluator verifies, never searches; malformed/incomplete/range/conflict
  rejects; no substrate whitelist growth after seeing result.
- **Migration/telemetry/performance:** SAT remains regression only; record pack overhead; no schema
  migration beyond additive pack-local schema.
- **Security/compatibility/rollback:** evaluator key separate; pack removal restores baseline without
  data rewrite.
- **Completion/next:** positive/negative/metamorphic vectors, RF-86/RF-98, and evidence verifier pass;
  next B-M6.

### M-6 — Canonical recursive delegation

#### A-M6 — Clean recursive runtime evidence

- **Objective/baseline:** retain real `ChildRuntimePort` and produce clean depth≥3, crash/recovery,
  and kill-tree proof.
- **Files/symbols:** ports child contract consumed from B, runtime delegation/child runner/session/
  wiring/recovery.
- **Contracts/schemas:** `SpawnIntent`, `ChildRunPlan`, result, deterministic child ID, four-cost
  reservation and structural ceilings.
- **Inputs/outputs:** parent state plus idempotency-bound intent in; child lineage/result/actual cost
  and settlement out.
- **Behavior:** lookup idempotency → derive child ID → attenuate scope → reserve componentwise →
  append intent → re-enter `run_composed` → append return → settle/refund; reconcile open trees.
- **Invariants/errors:** no ambient handles, widening, borrowing, transcript result, blind retry, or
  synthetic success; uncertainty is quarantined.
- **Migration/telemetry/performance:** old volatile IDs stay historical; measure nesting overhead and
  open leases; no Kernel semantic diff.
- **Security/compatibility/rollback:** cancellation propagates as mediated request; child facts are
  immutable; disable spawn by removing capability, not alternate engine.
- **Completion/next:** clean-subject signed bundle resolves depth≥3 and every crash/kill artifact;
  next A-M6.5.

#### B-M6 — Delegation contracts/falsifiers

- **Objective/baseline:** own stable child wire values and conservation proofs.
- **Files/symbols:** `ports/child_runtime.py`, child fold/projection, RF-55…RF-59/RF-101…RF-113
  fixtures.
- **Contracts/schemas:** parent/child identity, result digest, occurrence and cancellation types.
- **Inputs/outputs:** generated intents and parent vectors in; valid/denied/undeterminable expected
  folds out.
- **Behavior:** property-generate nested scopes/budgets/crash points; assert monotonic attenuation,
  conservation and partition-invariant folds.
- **Invariants/errors:** each cost dimension and depth/turn tested independently; cross-project
  idempotency never matches.
- **Migration/telemetry/performance:** schema remains `/1` until incompatibility demands `/2`;
  property suite belongs in focused gate.
- **Security/compatibility/rollback:** goal prose remains artifact/digest, not ledger payload; old
  child facts remain readable.
- **Completion/next:** contract matrix and independent software verifier pass; next B-M6.5.

### M-6.5 — Measured meta-control with deterministic fallback

#### A-M6.5 — Runtime seam and profile disposition

- **Objective/baseline:** retain controller as authority-free between-turn policy and apply the
  accepted study outcome only to named profiles.
- **Files/symbols:** progress projection, meta-controller port integration, semantic checkpoints,
  profile/config resolution.
- **Contracts/schemas:** progress `/2`, directive identity/reason/confidence, controller flag in
  `D_R`.
- **Inputs/outputs:** event-derived progress/confidence in; bounded directive or no-op out.
- **Behavior:** fold checkpoint → validate freshness/calibration → consult → reject authority/budget
  fields → record directive → ordinary dispatch.
- **Invariants/errors:** controller cannot grant, dispatch, change budget, or hide unknown; invalid
  directive becomes no-op plus refusal.
- **Migration/telemetry/performance:** controller-off remains compatibility default; report
  attributable directive and overhead metrics; profile rollback disables flag.
- **Security/compatibility/rollback:** stale confidence denied; negative study automatically chooses
  `DISABLE_DEFAULT` and continues.
- **Completion/next:** off-path parity and accepted profile disposition pass; next A-M7.

#### B-M6.5 — Experimental instrument

- **Objective/baseline:** preserve/reproduce the current accepted paired study and prevent future
  instrumentation drift.
- **Files/symbols:** stochastic adapter, `lab/m65_*`, tasks, statistics, evidence bundle.
- **Contracts/schemas:** common-random semantic key, comparability tuple, preregistered thresholds.
- **Inputs/outputs:** ≥20 tasks × ≥3 seeds across ≥4 block types in; paired report with A/A,
  McNemar, Holm, CI, costs and attribution out.
- **Behavior:** freeze tasks → A/A → paired control/treatment → validate comparability → compute
  declared statistics → choose enable/experimental/disable/undeterminable.
- **Invariants/errors:** no optional stopping; invalid instrument is repaired, while valid negative
  result closes with controller off.
- **Migration/telemetry/performance:** preserve old study bundle; new protocol version for changed
  thresholds; experiment can run outside fast CI.
- **Security/compatibility/rollback:** sealed task material and no authority in adapter; disposition
  revert is configuration-only.
- **Completion/next:** deterministic reproduction from seeds/cassettes and verifier receipt; next
  B-M7.

### M-7 — Real topology execution, sequential by decision

#### A-M7 — Execute declared roles through one runtime

- **Objective/baseline:** finish the integration that current `run_composed` only starts: execute
  each lowered operation as ordinary M-6 work and settle the topology.
- **Files/symbols:** Runtime root/run plan/topology/scheduler/session/child runtime and telemetry.
- **Contracts/schemas:** digest-pinned extension ref, lowered operations, artifact flows, scheduler
  digest; ADR-0099 `SEQUENTIAL_CONFIRMED`.
- **Inputs/outputs:** direct, planner/executor/reviewer, and two-readers/merge topologies in; settled
  role lineages and final artifact out.
- **Behavior:** verify ref → lower against frozen composition → fold settled ops → find ready set →
  deterministic sequential decision → execute each as M-6 child → refold → repeat.
- **Invariants/errors:** topology carries no authority; causal edge dominates selector disjointness;
  missing role/flow/selector/cycle/unsettled predecessor fails closed.
- **Migration/telemetry/performance:** existing raw topology mappings normalize to extension `/1`;
  monotonic spans are non-authoritative; disabled path parity and <3% median bookkeeping overhead.
- **Security/compatibility/rollback:** no concurrency in v0.9 default; feature flag removes extension
  and preserves ordinary run identity rules.
- **Completion/next:** three live topologies, crash/replay, artifact joins and disabled parity pass;
  next A-M8.

#### B-M7 — Scheduler evidence preservation

- **Objective/baseline:** retain M7-01 and ADR-0099, and verify completeness against live topology
  bundles rather than library fixtures.
- **Files/symbols:** M7 analyzer, selector/sink algebra, telemetry completeness and falsifiers.
- **Contracts/schemas:** independence candidate and schedule report; no new budget dimension.
- **Inputs/outputs:** causal bundles/spans in; eligible fraction, critical path, unknown rate and
  `SEQUENTIAL_CONFIRMED` verification out.
- **Behavior:** exclude causally related/shared/unknown/non-idempotent pairs → compute conservative
  metrics → ensure decision thresholds remain unmet or open a successor ADR if future evidence
  changes.
- **Invariants/errors:** missing data serializes; timing cannot mutate events or verdicts.
- **Migration/telemetry/performance:** old report stays immutable; live report adds a new evidence
  subject; analyzer runs as non-gating research unless decision changes.
- **Security/compatibility/rollback:** scheduler cannot authorize; sequential is permanent fallback.
- **Completion/next:** live bundle reproduces decision and RF-98 stays green; next B-M8.

### M-8 — Durable authorized memory and governed learning

#### A-M8 — Durable storage, retrieval integration, and served registry

- **Objective/baseline:** complete production durability around Lane B contracts and remove all
  compatibility fakes from product wiring.
- **Files/symbols:** memory SQLite/CAS adapter, blob/index stores, session context integration,
  durable composition registry, backup/restore/GC.
- **Contracts/schemas:** authorized memory context, four categories, retrieval receipt, immutable
  composition, signed CAS transition/rollback.
- **Inputs/outputs:** verified context and record/query in; durable scoped record/retrieval refs or
  served composition version out.
- **Behavior:** authorize → redact/canonicalize → blob put → metadata/index transaction → causal
  fact; recall scopes in SQL before ranking/dereference; promotion/rollback verifies evidence then
  CAS-switches served head.
- **Invariants/errors:** no product `InMemoryMemoryPort`; metadata/event crash boundaries quarantine;
  index corruption rebuilds or returns typed degraded state; rollback without signature denied.
- **Migration/telemetry/performance:** versioned SQLite migrations with backup and checksum; write
  p95 <50 ms at 4 KiB, lexical recall p95 <100 ms at 100k/limit20 on declared host; GC dry-run.
- **Security/compatibility/rollback:** tenant/project/category isolation, use-time expiry/revocation,
  legal hold, network-FS refusal; previous schema dual-read and previous composition always
  rollbackable.
- **Completion/next:** restart/restore, crash matrix, leak/timing tests, CAS race and behavioral
  rollback pass; next A-M9.

#### B-M8 — Contract consolidation, evaluation, promotion

- **Objective/baseline:** remove duplicated/fail-open memory and skill paths and produce one measured
  promotable composition or a valid keep-current fallback.
- **Files/symbols:** ports memory, runtime memory semantics, skill evaluation/lifecycle,
  governance learning, sealed workload/evaluator tooling and security tests.
- **Contracts/schemas:** HMAC/Ed25519 signed grant, retrieval provenance, evaluation report,
  promotion evidence, rollback evidence, role identities.
- **Inputs/outputs:** development trajectories and sealed held-out/adversarial/transfer splits in;
  candidate/report/signed transition or negative disposition out.
- **Behavior:** remove legacy nonempty-string disjunct → verify authorization at each use → generate
  without held-out access → independently evaluate → enforce generator≠evaluator≠promoter → sign
  CAS transition → inject regression → signed rollback → verify restored behavior.
- **Invariants/errors:** presence-only gain rejected; unavailable verifier refuses; stale CAS loses;
  no shared identity/key/store privilege across roles.
- **Migration/telemetry/performance:** consolidate three overlapping promotion APIs behind one
  compatibility facade; report retrieval/grounding/verification/lift/regression and overhead;
  negative result keeps prior composition and closes the experiment.
- **Security/compatibility/rollback:** authorization before ranking/dereference, sealed access logs,
  signed rollback evidence; old APIs warn then route to canonical implementation.
- **Completion/next:** all M-8 security falsifiers, held-out result, restart and behavioral rollback
  pass; next B-M9.

### M-9 — Operational beta product (`0.9.0b1`)

#### A-M9 — Integrated installable product

- **Objective/baseline:** turn the accepted M-1–M-8 substrate into a cleanly installable and usable
  single-host beta.
- **Files/symbols:** Python packaging/assets, CLI/client-core/Studio, runtime service/gateway,
  configuration, plugin registry, installer/uninstaller, containers and smoke workflows.
- **Contracts/schemas:** one version source, `vg.4`, config `/1`, plugin lifecycle, health/readiness,
  CLI exit codes, distribution manifest.
- **Inputs/outputs:** signed wheel/npm tarballs or bundled application plus default packs/schemas in;
  `vanguard init|doctor|run|resume`, service API/TUI and real workflow results out.
- **Behavior:** install in empty environment → initialize keys/state → discover/verify/activate
  plugin → run coding and formal workflows → stop process → resume → inspect events/artifacts →
  uninstall cleanly.
- **Invariants/errors:** no checkout path/PYTHONPATH dependence, surprise state directory, silent
  in-memory fallback, unauthenticated non-loopback gateway, or mismatched client/server version.
- **Migration/telemetry/performance:** migrate config/store via explicit command with backup/dry-run;
  beta SLOs for startup, append, resume, stream reconnect and workflow latency; crash reports redact
  secrets.
- **Security/compatibility/rollback:** signed artifacts/checksums/SBOM, loopback default, plugin
  signature and capability ceiling, downgrade only when store schema is compatible; retain previous
  beta artifact.
- **Completion/next:** clean-machine offline-after-install smoke for two real workflows and one
  restart, all client workspaces green, `0.9.0b1` artifacts reproducible; next A-M10.

#### B-M9 — Product contracts, plugins, and real workflow qualification

- **Objective/baseline:** freeze the public beta contract and prove transfer across coding, formal,
  and one third practical workflow without new substrate semantics.
- **Files/symbols:** public schemas/generated SDK types, plugin manifests/vectors, workflow packs,
  compatibility/evidence tools.
- **Contracts/schemas:** supported-version matrix, config schema, plugin install/upgrade/disable/
  remove states, workflow evidence envelope.
- **Inputs/outputs:** three frozen workflow corpora and plugin lifecycle fixtures in; compatibility
  report, capability truth and evidence bundles out.
- **Behavior:** validate package contents → run public contract vectors in Python/TS → exercise
  plugin lifecycle including fault/rollback → run workflows → compare replay and product views.
- **Invariants/errors:** plugin cannot mint authority or change Kernel; unavailable optional plugin
  reports disabled reason; third workflow failure selects documented reduced beta scope rather than
  blocking core installation.
- **Migration/telemetry/performance:** schema support table includes read/write/sunset; plugin and
  workflow metrics include versions and distributions.
- **Security/compatibility/rollback:** malicious/expired/incompatible plugin fixtures fail closed;
  removal cannot erase causal history; previous plugin version remains restorable.
- **Completion/next:** public vectors and workflow bundles verify from installed artifacts; next
  B-M10.

### M-10 — Release hardening and final AETHER v0.9

#### A-M10 — Reliability, deployment, migration, and release engineering

- **Objective/baseline:** harden `0.9.0b1` into reproducible `0.9.0` without adding speculative
  intelligence features.
- **Files/symbols:** migration manager, backup/restore/recovery tools, service/container/system
  packaging, CI release workflows, performance harness, operations docs in existing canonical files.
- **Contracts/schemas:** store/config migration ledger, backup manifest, deployment profile,
  readiness/liveness, release manifest/SBOM/signatures.
- **Inputs/outputs:** beta stores/configs/artifacts and fault matrix in; migrated/recovered deployment
  and signed reproducible release artifacts out.
- **Behavior:** snapshot → migrate copy → validate digests → atomically switch → soak/fault test →
  restore backup on failure; build twice in clean environments and compare content manifests.
- **Invariants/errors:** no destructive migration without verified backup; partial migration is
  resumable or rolled back; unknown schema refuses; SIGTERM/cancellation settles truthfully.
- **Migration/telemetry/performance:** test every supported predecessor; publish reference-host SLOs,
  24-hour soak, memory/FD/WAL growth, recovery-time and data-loss objectives; regression budgets are
  explicit.
- **Security/compatibility/rollback:** threat-model tests, dependency/license/secret scans,
  least-privilege container, key rotation/revocation, tenant isolation; rollback to beta artifact and
  compatible store snapshot.
- **Completion/next:** final release matrix in Section 11 passes from clean artifacts; tag and publish
  `v0.9.0`; next is a separately authorized v1.0 roadmap.

#### B-M10 — Final compatibility, security, and release validation

- **Objective/baseline:** independently validate the final candidate through automated evidence,
  not a committee.
- **Files/symbols:** release verifier, schema/migration/security matrices, long-run and adversarial
  workloads, evidence manifest.
- **Contracts/schemas:** release claim binds commit/tree, dependencies, images, wheel/npm hashes,
  migrations, schemas, SLO results and security receipts.
- **Inputs/outputs:** Lane A release candidate and beta fixtures in; signed pass/fail release
  envelope and retained failure diagnostics out.
- **Behavior:** install artifacts → verify SBOM/signatures → migrate fixtures → run essential E2E and
  fault/security/performance samples → restore → compare digests → countersign only exact subject.
- **Invariants/errors:** verifier identity differs from builder automation; failure assigns defect to
  owning lane and never silently waives; flaky tests are quarantined only after replacement by a
  deterministic signal.
- **Migration/telemetry/performance:** validate all supported versions and stated SLO distributions;
  store raw benchmark artifacts outside Git with content digests.
- **Security/compatibility/rollback:** release signer and verifier keys separate; compromised plugin,
  forged grant, cross-tenant query, corrupt WAL/index and stale CAS scenarios deny/recover.
- **Completion/next:** exact release envelope is `passed`, artifacts install and operate, version is
  `0.9.0` everywhere; roadmap terminates successfully.

## 9. Autonomous decision model

### 9.1 Decision classes

| Class | Examples | Decision right |
|---|---|---|
| Local implementation | private helper, internal data structure, test organization, algorithm under frozen complexity/security bounds | Developer implementing the package; record in code/tests |
| Shared contract | public type, wire field, schema version, port method, error code, migration format | Lane B owner; Lane A supplies consumer constraints/failing fixture |
| Operational/runtime | store transaction, deployment topology, retry/backoff, resource limits, build/install mechanism | Lane A owner, within constitutional constraints |
| Constitutional invariant | Kernel authority, event truth, capability attenuation, schema evolution rule, identity separation, promotion separation | Cannot change silently; successor ADR + falsifier + migration required |

### 9.2 Closed decision register

| Decision | Owner | Options | Selection rule | Default/fallback | Consequence |
|---|---|---|---|---|---|
| Manifest schema source | B | mhf, v4, successor | Keep wire ID matching shipped packs; successor only for incompatibility | one canonical catalog + generated readers | Removes current path/drift failure |
| `vg.4` field shape | B | JSON Schema, handwritten superset | JSON Schema plus demonstrated required fields; regenerate readers | reject unknown fields | One cross-language contract |
| Schema resource packaging | A | package assets, external install path | Must work from wheel without checkout | `importlib.resources` package assets | Clean install works |
| Baseline publication | A | recovered old, successor | Old tag remains contaminated; use exact green successor digest | local signed baseline, retry remote publication | No development stall on remote |
| Evidence acceptance | B | human review, software verifier | Reproducible deterministic checks permit verifier service | `undeterminable` if reproduction unavailable | No mandatory human gate |
| M-6.5 enablement | B | enable, experimental, disable | Apply preregistered result | controller off | Negative result advances |
| Scheduler | A | sequential, bounded reads | ADR-0099 is controlling until successor evidence | sequential | Predictable M-7/M-9 |
| Memory index | B | lexical FTS5, vector, graph | Smallest deterministic index meeting SLO | FTS5/lexical | Vector research non-blocking |
| Memory persistence | A | SQLite/CAS, server DB | Single-host v0.9 and recovery requirements | SQLite WAL + CAS, refuse network FS | No distributed dependency |
| Promotion API duplication | B | governance, skill_evaluation, skill_lifecycle | Choose path with complete signed separation; facade others | governance contract + durable A registry | One canonical lifecycle |
| Rollback authorization | B | unsigned pointer move, signed evidence | Security invariant requires signed, bound evidence | refuse rollback | Prevents unauthorized serving changes |
| Plugin isolation | A | in-process, subprocess, container | Manifest tier plus capability/risk policy | fail requested isolation closed | No silent host fallback |
| Multi-tenancy | B contract/A storage | shared rows, database-per-tenant | Scoped rows sufficient only if leak/fault suite passes | scoped SQLite; split DB on failure | Concrete M-10 trigger |
| Distribution | A | wheel/npm, bundled app, checkout shim | Clean install, assets, signatures, uninstall decide | wheel + npm artifacts | Retires current shim |
| Distributed execution | A | none, bounded worker, queue | Implement only if single-host SLO/capacity fails | single-host | No speculative consensus system |
| Version sequence | A release/B compatibility | old M7=v0.9, M9=v1.0, new sequence | Project Owner objective controls | M9 `0.9.0b1`, M10 `0.9.0` | v1.0 deferred |

If a decision is not in the register, its owner applies: smallest reversible design, no new Kernel
semantic, no new writer, no new schema version without incompatibility, and fail closed on authority.

## 10. Branch and mechanical integration model

1. Maintain `integration/v0.9` as the only continuously green integration branch.
2. Lane branches are `lane-a/<package-id>` and `lane-b/<package-id>`, cut from the same integration
   commit. Each lane has WIP=1.
3. Contract-producing B packages merge first when A consumes them. A rebases onto that integration
   commit, completes the consumer, and merges second. For A-produced runtime telemetry consumed by
   B experiments, reverse the order.
4. A lane merges its own package after `SELF_VERIFIED`; no cross-lane approval is required. Use
   fast-forward or rebase merge so the producer-before-consumer order is visible.
5. The post-merge integration job runs the minimum suite. Failure automatically assigns the defect
   to the first package whose merge introduced it. That lane repairs forward on
   `lane-x/<package-id>-repair`; the other lane continues from the last green base if paths do not
   depend on the red contract.
6. Shared-file conflict is prevented, not reviewed away: only the permanent owner edits it. A
   consumer change request is a failing vector/fixture, not a competing edit.
7. Integration commits record `package-id`, baseline, contract digest, checks, migration and
   rollback in the commit body. Commit subject matches actual scope.
8. Release candidates are immutable tags only after the integration branch is clean. Tags are never
   moved. Failed candidates receive a new prerelease number.

## 11. Minimum verification model

Verification proves behavior; it does not create bureaucracy.

### 11.1 Fast local checks per commit

- compile/typecheck touched language;
- focused owned unit/contract tests;
- boundary and TCB checks when relevant;
- one positive and one negative fixture for changed authority/schema behavior;
- self-review of `git diff` for scope, defaults, secrets, migrations, and dead paths.

Target: under five minutes. Large statistical studies, soak tests, all historical tests, and live
providers are not per-commit gates.

### 11.2 Automatic package integration

- affected package suite;
- generated-code drift;
- shared contract vectors in Python and TypeScript;
- relevant crash/migration/security falsifier;
- canonical composition smoke from a file-backed store;
- architecture/TCB/secret/event coverage checks.

### 11.3 Essential end-to-end scenarios

1. Install from built artifacts; init; run code task; mediate effect; persist; kill; resume; verify.
2. Run graph-coloring pack and reject malformed witness through exterior evaluator.
3. Spawn depth≥3; inject crash; reconstruct lineage/budgets; cancel subtree.
4. Execute all three topologies sequentially through real child operations.
5. Write/recall/revoke memory across two tenants; ensure no existence leak; restart.
6. Evaluate/promote composition, race stale promoter, inject regression, signed rollback, restart.
7. Connect CLI/TUI/API, reconnect event cursor without loss or duplicate, observe truthful
   capability states.

### 11.4 Final v0.9 validation

- clean Python 3.10/3.12 and Node 20/22 builds from lockfiles;
- all owned unit/contract suites and essential E2E scenarios;
- wheel/npm/package content inspection and clean installation;
- supported store/config migrations and backup/restore;
- container/host profiles, UDS/HTTP authentication and shutdown;
- security falsifiers, dependency/license/secret scans and SBOM/signatures;
- reference-host performance distributions and 24-hour soak;
- reproducible artifact manifest and automated independent release envelope.

### 11.5 Defect and experiment policy

- Regression introduced by one lane: that lane fixes it immediately.
- Contract mismatch: Lane B owns the correction; Lane A uses the last frozen contract meanwhile.
- Integration-only defect: owner is the lane whose consumer merged second.
- Cross-surface defect: the event/contract producer owns root cause; consumer owns defensive error
  handling.
- Flaky check: owner makes it deterministic or replaces it; repeated reruns are not acceptance.
- Valid negative experiment: apply preregistered fallback and mark `FALLBACK_COMPLETE`.
- Invalid/undeterminable experiment: repair only the instrument; do not block unrelated product
  work.

The current full-suite failure demonstrates why “all tests always” is not the method: 17 errors are
one resource-path regression, two failures are stale pricing expectations, and the suite mutates a
tracked database. Those defects must be fixed, but each should have a focused owner and signal.

## 12. Coding and engineering standards

- **Typing:** strict public Python type hints and TypeScript strict mode; no `Any` across public
  contracts without a validated boundary.
- **Modularity:** one responsibility per module; extract current >1,000-line runtime/service/session
  files when touched, without changing behavior in the extraction commit.
- **Dependency direction:** preserve the lattice; adapters never import Kernel/Agency; clients never
  reproduce authority logic.
- **Errors:** typed errors with occurrence semantics; no string matching, broad success fallback, or
  `except Exception` returning empty/pass.
- **Logging:** structured, correlation IDs, no secrets/raw private goals; log state changes after
  commit and refusals without leaking hidden resource existence.
- **Events:** immutable causal facts through the single emitter; intents precede effects; every open
  effect reaches terminal/undeterminable reconciliation.
- **Serialization:** JSON Schema + JCS; unknown fields rejected at authority boundaries; canonical
  timestamps/integers; no float budgets.
- **Persistence:** SQLite WAL on local FS, explicit transactions, fsync/durability profile,
  idempotency, migrations with backups; no product `:memory:` fallback.
- **Concurrency:** sequential default; deterministic ordering; CAS for shared heads; cancellation
  and crash recovery; unknown overlap serializes.
- **Security:** verify signature, expiry, scope, purpose, tenant/project, and revocation at use;
  least privilege; no embedded keys; explicit profile degradation.
- **Capabilities:** every privileged action passes S0–S12; derived systems cannot mint authority;
  attenuation is componentwise.
- **Versioning:** one package/product version source; schema IDs version independently; dual-read/
  single-write; prereleases are immutable.
- **Compatibility:** compatibility readers normalize at ingress; stored bytes stay unchanged;
  sunset only from an explicit support matrix.
- **Performance:** benchmark distributions on named hosts/data; correctness first; no threshold
  relaxation after observing results.
- **Observability:** causal events, telemetry spans, artifacts, and evidence remain separate but
  correlated; missing telemetry cannot change behavior.
- **Documentation:** edit only canonical Clean Triad files when implementation plans/status/law
  change. Do not create review/plan Markdown sprawl. Code comments explain invariant and failure
  reason, not restate syntax.
- **Refactors:** use AST/symbol-aware changes; repository-wide textual renames require negative
  fixture and duplicate-key/path audits.

## 13. Focused M-9/M-10 research requirements

Research is a bounded spike with a decision output, not a generic survey.

| Topic | Concrete question | Required artifact | Default if inconclusive |
|---|---|---|---|
| Python/TS packaging | Which artifact layout includes schemas, packs, UI assets and native entrypoints reproducibly? | two clean builds, content manifests, install/uninstall smoke | Python wheel + npm tarballs |
| Storage | Does SQLite WAL/CAS meet 100k-memory and long-run event SLOs on supported local filesystems? | benchmark/fault matrix | SQLite local only |
| Migrations | Can every supported beta store/config migrate idempotently and restore byte-valid history? | fixture matrix and recovery receipts | refuse unknown version |
| Recovery | What RTO/RPO is achieved under kill -9, disk-full, corrupt index, lost notification and partial promotion? | fault-injection report | cold fold/rebuild, quarantine unknown |
| Security | Do tenant/category timing, plugin, gateway, key-rotation and rollback attacks leak or widen authority? | adversarial suite | fail closed/feature disabled |
| Multi-tenancy | Are scoped tables sufficient, or does measured leakage/operational need require database-per-tenant? | isolation/timing/backup comparison | scoped local database |
| Plugin lifecycle | How are install, signature verification, activation, upgrade, disable, removal and rollback made atomic? | local signed plugin fixture lifecycle | bundled plugins only |
| Performance | Which five product operations dominate latency/cost and which bounded optimization meets SLO? | profiles and before/after distribution | retain simple path |
| Distributed execution | Does a real v0.9 workload exceed single-host capacity or availability target? | capacity and failure evidence | no distributed scheduler |
| Meta-control | Does controller benefit transfer beyond its accepted task/profile without violating non-inferiority? | new preregistered paired study | controller off outside proven profile |
| Skill promotion | Does held-out grounded lift survive restart, adversarial set and transfer with signed rollback? | sealed evaluation/rollback bundle | keep previous composition |
| Release engineering | Can release builds be reproducible, signed, SBOM-bound and installed without source/network after artifact acquisition? | release manifest/verifier envelope | do not publish final |

Each spike is capped at one package. It ends with `adopt`, `defer`, or `reject` and the operational
fallback above. It cannot suspend the rest of the roadmap.

## 14. Structure and handoff of the two implementation plans

The final Lane A and Lane B plans must not become two new Markdown authorities. Produce them as two
views of one canonical execution dataset:

1. Edit existing `docs/03_execution/backlog.md` to contain the stable package contracts, grouped
   `Lane A` and `Lane B`, using the template in Section 15.
2. Edit existing `docs/03_execution/sprint_active.md` to contain exactly one active package per
   lane, baseline commit, contract digest, state, completion predicate, and next package.
3. Keep `milestones.md` as the stable outcome ladder, amended once for the M-9/M-10 and version
   definitions in this report. Do not duplicate volatile status there.
4. Generate ephemeral developer handoff JSON from those rows with schema
   `aether.work-package/1`; do not commit a new plan document. Each lane receives its filtered JSON,
   the exact integration commit, required fixtures, and commands.
5. Version the dataset by Git commit plus package contract version. Incompatible contract changes
   increment the contract schema; ordinary task progress changes only the board state.
6. Before handoff, resolve every decision using Section 9. No packet may contain “TBD,” “ask CEO,”
   “Leadership decides,” “Dev C,” or “pending ADR” without an already-selected fallback.
7. Handoff is complete when a developer can start the first command, locate every input, and decide
   success/failure without contacting the Project Owner.

The two generated views contain the same dependency IDs, so developers integrate mechanically and
cannot drift into separate architectures.

## 15. Work-package template

Every future package must use all fields below; omit none.

| Field | Required content |
|---|---|
| Identity | package ID, milestone, lane, contract version, baseline commit |
| Objective | one observable product or substrate outcome; explicit exclusions |
| Baseline | implemented/partial/missing facts and known red checks |
| Ownership | exact files, symbols, prohibited paths and shared contract producer |
| Contracts | public types/ports, schema IDs, generated readers and golden vectors |
| Inputs | immutable fixtures, stores, profiles, credentials-by-reference, predecessor artifacts |
| Outputs | code, events, artifacts, migrations, evidence and user-visible behavior |
| Pseudocode | ordered happy path including transaction/effect boundaries |
| Invariants | constitutional and package-specific properties |
| Errors | typed failure, occurrence, retry/reconciliation and user-facing mapping |
| Migration | source versions, idempotency, backup, resume, downgrade/read compatibility |
| Telemetry | correlation keys, metrics, missingness and non-authoritative status |
| Performance | workload/host, metric distribution, threshold and fallback |
| Security | threats, authorization checks, secret handling, tenant/plugin isolation |
| Compatibility | reader/writer policy, deprecation window and old-byte behavior |
| Rollback | code, schema, store and served-behavior reversal procedure |
| Verification | minimal local, integration, E2E and evidence predicates |
| Completion | machine-evaluable expression; no human approval |
| Next | exact next package and input artifact it consumes |

## 16. Final ordered TODO

| Order | Owner | Result | Dependencies |
|---:|---|---|---|
| 1 | B | Freeze canonical manifest and `vg.4` schemas; generated shared readers/vectors | HEAD |
| 2 | A | Repair schema resource resolution and packaging; eliminate 17 Python errors | 1 |
| 3 | A | Fix two pricing expectations at the source-of-truth boundary; stop tests mutating tracked SQLite | 2 |
| 4 | A | Make CLI, client-core and Studio all root-gated; resolve 3 failing CLI test files | 1 |
| 5 | A | Build/install wheel with schemas, packs and UI assets; replace checkout installer | 2, 4 |
| 6 | B | Remove memory fake fail-open disjunct and consolidate canonical memory/promotion APIs | 1 |
| 7 | A | Require signed durable rollback and complete CAS/backup/restore/GC implementation | 6 |
| 8 | A | Produce clean RF-95 and M-6 bundles with portable artifacts | 2, 3, 5 |
| 9 | B | Automated verifier accepts/rejects M-4/M-6; preserve M-6.5 disposition | 8 |
| 10 | A | Freeze local then remote `CONVERGENCE-BASE-v1` without moving old tag | 2–5, 9 |
| 11 | B | Re-run graph coloring RF-86/RF-98 against valid successor | 10 |
| 12 | A | Execute real M-7 role operations through M-6 child runtime, sequentially | 8 |
| 13 | B | Reproduce M7-01 on live topology bundles; retain ADR-0099 sequential default | 12 |
| 14 | A | Complete durable authorized memory integration and lifecycle recovery | 6, 7, 13 |
| 15 | B | Run sealed skill/composition evaluation, separated promotion and signed behavioral rollback | 11, 14 |
| 16 | A | Unify versions/config, package CLI/API/TUI/Studio/plugins and ship `0.9.0b1` candidate | 9–15 |
| 17 | B | Qualify three real workflows and full public contract/plugin lifecycle from installed artifacts | 16 |
| 18 | A | Implement migrations, deployment profiles, backup/recovery, SLOs and soak/fault hardening | 16, 17 |
| 19 | B | Run final security/compatibility/migration/performance release verifier | 18 |
| 20 | A | Build reproducibly, sign, tag and publish AETHER `v0.9.0` | 19 passed |

## 17. Immediate next steps

1. Start B-M3 and A-M3 concurrently only where files are disjoint: Lane B freezes schema/vector
   truth; Lane A prepares resource/package resolution and consumes the frozen result.
2. Repair the full Python and TypeScript gates before producing new milestone evidence. Record the
   current known-red baseline exactly: 2 Python failures, 17 Python errors, 3 failing CLI test files.
3. Treat the approved `TODO_PROMPT.md` as historical design input after extracting still-live items:
   its final memory fail-open and unsigned rollback findings remain real; many earlier P0 findings
   have already been implemented.
4. Replace current Dev A/Dev B/Leadership wording in the canonical execution board with Lane A/Lane
   B and mechanical completion predicates when the implementation plans are created.
5. Amend the canonical milestone/version documents once, before M-9 work, to encode
   `M-9=0.9.0b1` and `M-10=0.9.0`; do not use v1.0 for this program.
6. Hand both lanes their first generated work-package views at the same green integration commit and
   allow continuous execution through Order 20 without further Project Owner review.

## 18. Final conclusion

The fastest safe route is neither a rewrite nor a ceremonial re-audit. It is contract convergence,
focused repair of current red gates, completion of the already-started M-4–M-8 mechanisms, and two
new product milestones. Lane A owns the operational truth and deliverable; Lane B owns the contract
and falsifiability of that truth. Frozen boundaries, exclusive writers, deterministic defaults,
fixtures, self-review, and mechanical integration replace daily supervision and approval gates.

When Order 20 completes, AETHER v0.9 is not merely a repository with advanced mechanisms. It is a
reproducibly buildable, installable, resumable, capability-mediated, multi-workflow product with
durable memory, governed learning, signed rollback, supported migrations, operational evidence,
and a final release that can be verified from its shipped artifacts.
