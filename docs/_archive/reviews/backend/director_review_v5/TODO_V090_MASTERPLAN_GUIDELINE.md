# Vanguard / AETHER 0.9.x — Final Backend Evolution Plan

## Decision

**Preserve and productize the existing substrate; do not rewrite it.**

The reviewed subject is `feat/vanguard-0.9.0b1-beta-evolution` at
`df20131fc1361f2e847fb6db41d0a61f506d345d`. That branch adds review material
but no new 0.9 backend implementation relative to `main`; the package version
remains `0.7.3.dev0`.

Vanguard already has the difficult foundations: a bounded domain-blind Kernel,
typed capability attenuation and budgets, durable causal facts, replayable
projections, content-addressed artifacts, canonical composition, recursive
delegation, and a fail-closed security/evidence model. The 0.9 problem is not
that foundation. It is the gap between tested mechanisms and a coherent,
installable, inspectable product path.

The public model should remain simple:

```text
Observe -> Decide -> Authorize -> Execute -> Record
```

The Kernel may retain S0-S12 internally. No new workflow engine, alternate
agent runtime, LEX/LIM production dependency, general orchestration layer,
MCTS, CEGIS, or speculative scheduler is authorized by this plan.

## Verified starting facts

- The bounded lattice holds: `domain <- ports <- kernel <- agency <- runtime -> adapters`.
- The Kernel is 1,373 logical LOC under the enforced 1,438 LOC limit.
- The full standard-library suite ran 2,150 tests: 2,140 passed, 9 skipped,
  and one failed solely because execution-board package states disagree.
- The evidence verifier reports six passing bundles. M-4 has an
  organizational-independence caveat; M-5a lacks `CONVERGENCE-BASE-v1`; M-5b's
  historical bundle fails verification. M-6, M-6.5, M-7, and M-8 have current
  mechanically passing successors.
- Therefore, code presence, a passing test, a mechanically passing bundle, and
  formal milestone/release acceptance remain separate facts.

## Architecture to preserve

Keep these boundaries and invariants unchanged unless a successor decision and
falsifier justify change:

1. The domain-blind Kernel, monotonic capability attenuation, descriptor-bound
   grants, and integer budget accounting.
2. `mhf.event/2` as the production writer format, append-only facts, CAS
   artifacts, and projections/checkpoints as derived state rather than truth.
3. Durable pre-effect intent before an external effect can start.
4. The sole new-product execution route:

   ```text
   Runtime.execute_profiled
     -> RuntimeBootstrap.build
     -> Runtime.compose
     -> Runtime.run_composed
     -> HarnessSession / EpisodeEngine / Kernel.dispatch
   ```

5. Recursive children re-entering `Runtime.run_composed`, and M-7's current
   `SEQUENTIAL_CONFIRMED` scheduler disposition.

## What must be corrected

### Product ingress and configuration

The highest-priority defects are configuration and reachability, not new agent
algorithms.

- `runtime/service/service.py` defaults `profileId` to `code-default`, a
  harness name rather than a valid execution profile. Require a valid profile
  at ingress or default explicitly to `product`; validate before a worker
  thread is created.
- `runtime/cli.py` directly constructs `OpenRouterModel` and rejects absent
  provider credentials even for a local/offline workflow. Move model choice to
  one typed model-selection configuration resolved by the bootstrap. A wire
  request must name a route/adapter policy, never carry a raw Python model.
- The CLI, JSON entrypoint, and service must share command semantics. The CLI
  is a client of the service/projection contract; it must not recreate ledger,
  reducer, recovery, or authority behavior.
- Distinguish package version from protocol versions such as `vg.4`; do not
  replace wire-version literals as though they were release versions.

### Claimed capabilities not yet product-integrated

Durable memory, governed composition promotion/rollback, metacontrol, and
topology have meaningful code and falsifier coverage, but are mostly injected
into `Runtime.execute_*` rather than selected by profile, manifest, CLI, or
service contract. They are not yet general user-facing product capabilities.

For each, either:

1. add an explicit configuration, authority, provenance, and operational
   surface; or
2. label it experimental and exclude it from beta product claims.

### Generality proof

`vg-table-default` is the right minimal second-domain falsifier. Its binding
provider resolves table verbs, but `TableWorldEnvironment` does not satisfy the
runtime environment contract. Complete the real contract in the adapter and
prove an end-to-end table run; do not leak table semantics into Kernel, Domain,
or Agency. Existing Git, sandboxed, and fake environment adapters remain
reference implementations of the shared contract.

## Horizon 0 — truth and release hygiene

Do this before assigning a beta state.

1. Reconcile `docs/03_execution/backlog.md` and
   `docs/03_execution/sprint_active.md` from raw verifier receipts and actual
   predicates, not by blindly copying either table. Make
   `test/tools/test_check_execution_truth.py` pass.
2. Maintain one machine-derived milestone/evidence view from the existing
   verifier; preserve failed and undeterminable bundles as immutable history.
3. Do not call M-5a accepted until the required annotated remotely resolvable
   `CONVERGENCE-BASE-v1` and signed baseline manifest exist.
4. Do not call M-5b accepted until the successor graph-coloring experiment
   verifies against that baseline.
5. Obtain genuinely organizationally independent review where the evidence
   protocol requires it. Key distinction alone cannot prove operational
   independence.

**Definition of done:** the full test suite and execution-truth linter are
green; published status, receipt predicates, and verifier results agree; no
milestone claim is inferred from source presence.

## Horizon 1 — 0.9.0b1 product vertical slice

### H1.1 One valid execution configuration

**Files:** `runtime/service/service.py`, `runtime/bootstrap.py`,
`runtime/profiles.py`, `runtime/model_selection.py`, `runtime/cli.py`, and
wire/service-contract tests.

Implement a single typed input that resolves a profile, model route, state
directory, and optional offline adapter before execution. Validate invalid
profile/model combinations synchronously and fail closed. Preserve the
effective resolved configuration in the run plan/provenance.

**Definition of done:**

- a default service start uses a valid profile;
- remote execution fails clearly without credentials;
- explicit local/offline execution uses a deterministic fake or cassette
  adapter without network or provider credentials;
- CLI, entrypoint, and service agree on the same configuration semantics.

### H1.2 Operational CLI and service parity

Add thin `resume`, `status`, `events`, and `artifacts` commands. They use the
canonical service/projection APIs and respect the existing authorization and
artifact access rules.

**Definition of done:** an installed binary can initialize a workspace, run a
deterministic local composition, show status and causal events, list artifacts,
be interrupted, restart, resume from durable SQLite-WAL state, and produce a
verifiable terminal result.

### H1.3 Second domain and reference workflows

Complete `TableWorldEnvironment` against the actual environment port contract,
including profile, observation, preview/apply semantics, reconciliation,
compensation, and disposal as appropriate for the domain. Add an end-to-end
`vg-table-default` test using real runtime composition and receipts.

Register and test `vg-code-explain` as a read-only reference workflow. A
workflow is a useful proof only when it creates a verified, user-visible
artifact or result through the canonical product path.

**Definition of done:** coding, read-only explanation, and one non-coding
domain all execute through the same runtime with no Kernel changes.

### H1.4 Product-integrate or demote M-8/M-6.5 facilities

For memory, begin with a narrow manifest/profile declaration:

```text
resolved profile + declared memory policy
  -> verified scoped memory authority
  -> DurableMemoryPort binding
  -> retrieval provenance admitted to context
  -> ledger/artifact facts
```

Do not expose learning/promotion by default. Promotion requires distinct
generator, evaluator, and promoter authority, sealed held-out evaluation, a
durable CAS registry, and a behavior-restoring rollback. If these do not fit
the beta vertical slice, retain their tests but label the feature experimental.

### H1.5 Installable beta qualification

Add clean-environment wheel/install tests for package resources, manifests,
schemas, migrations, state directories, offline execution, recovery, and
resume. Release version changes occur here, after—not before—the product
vertical slice is green.

Run a real process-kill/restart/resume test; replay-only tests do not prove
operational continuation. Reproduce any claimed sparse/hermetic M-7 failure
on a clean environment before treating it as a release blocker.

**Beta exit criteria:** every H1 definition of done passes from installed
artifacts; release identity is internally consistent; M-5a/M-5b and reviewer
requirements are handled according to the authoritative acceptance rules, not
waived in prose.

## Horizon 2 — simplify only after freezing 0.9.0b1

Freeze a qualified beta as the behavioral reference before refactoring.
Refactor tests compare normalized causal event meaning, projection state,
artifact digests, composition identity, and evaluator verdict—not raw event
IDs, timestamps, or other intentionally variable bytes.

1. Make `execute_profiled -> RuntimeBootstrap -> run_composed` the only path
   for new callers. Retain `execute_harness` only as a migration/test facade
   until every caller moves.
2. Unify model resolution and manifest-path normalization at their ingress
   boundaries.
3. Split `HarnessSession` into focused lifecycle, turn/approval,
   capture/checkpoint, and terminal/evaluation collaborators while preserving
   public compatibility imports.
4. Split service command handling from transport/lifecycle code without
   changing the wire contract.
5. Separate immutable composition verification from the lifecycle of an
   executable plugin. A static prompt/policy artifact should not be modeled
   as a running process merely for lifecycle accounting.

**Definition of done:** normalized regression fixtures remain equivalent;
security, boundary, TCB, replay, and evidence checks pass; no refactor changes
the selected beta behaviors without an explicit new contract.

## Experiments that require proof before adoption

These are valuable hypotheses, not committed defaults.

### Turn-boundary ledger batching

Measure batching with `durability.commit = per-event | per-turn` compatibility
modes. `EffectStarted` intent must remain durably committed before the
external effect begins. Require injected-crash, recovery, replay, budget, and
evidence compatibility tests plus representative latency/throughput data
before changing the default.

### Lifecycle verbosity

Measure `capture.lifecycle = full | summary` only after separating static
composition facts from executable plugin lifecycle. Retain enough granular
facts to attribute a real component fault. Schema/reducer/evidence migration
is required before a summary format can be authoritative.

### Concurrent shared-lineage execution

M-7 remains sequential. The current SQLite store safely turns competing
same-project sequence allocation into conflict; it is not a concurrent writer
protocol. Add transactional allocation or a dedicated writer only after a
measured workflow proves value, then prove causal ordering, budget
conservation, recovery, and state equivalence under contention.

### Advanced agent techniques

MCTS, CEGIS, SBFL, mutation testing, vector retrieval, sophisticated
compaction, and parallel scheduling require a preregistered product or
evaluation hypothesis with a baseline and a success/failure decision rule.
They are optional evaluators or research packs, never new Kernel semantics.

## Final direction

The strongest path to a SOTA product is disciplined integration, not a larger
architecture: make one execution path trustworthy and pleasant to use; prove
it on coding, explanation, and a second domain; make durable state inspectable
and resumable; then simplify the runtime against that frozen behavior.

Vanguard's advantage is not that it contains every possible agent technique.
It is that future techniques can be introduced as measured compositions over
causal facts, bounded authority, reproducible artifacts, and external
evaluation without rewriting the trusted core.
