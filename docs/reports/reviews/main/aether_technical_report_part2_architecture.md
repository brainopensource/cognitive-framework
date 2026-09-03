# AETHER / Vanguard — Technical Report, Part II
## Agent Typology, Runtime Mechanics, and the Module Topography

*Continues Part I. Same constraint: present implementation only.*

---

## 3. Systemic Modeling & Conceptual Formulations

### 3.1 The central structural result: an agent is a manifest, not a module

This is the most consequential finding of the survey, and it is verifiable by direct comparison of
artefacts rather than by argument. The repository contains **38 manifests** under
`agency/manifests/`. Comparing the coding, research, and tutor compositions:

| | `vg-code-max` | `vg-research-v090-v2` | `vg-tutor-v090-v1` |
|---|---|---|---|
| system_prompt | code-default | research-specific | tutor-specific |
| tools | read, search, **patch, test** | read, search | read, search |
| capabilities | `fs.read`, `fs.search`, **`patch.apply`** (privileged/medium), **`proc.exec`** (privileged/high) | `fs.read`, `fs.search` (both observation/low) | `fs.read`, `fs.search` (both observation/low) |
| evaluators | `coding-oracle@3` | `answer-oracle@1` | `answer-oracle@1` |
| context_policy | code-default | **code-default (shared)** | **code-default (shared)** |
| routing_policy | code-default | **code-default (shared)** | **code-default (shared)** |
| budgetPolicy | code-default | **code-default (shared)** | **code-default (shared)** |

The three agent types share the episode loop, the kernel, the context compiler, the routing policy,
the budget policy, and the approval policy **byte for byte**. They differ in exactly three
dimensions: the system prompt, the declared capability set, and the evaluator. A Tutor is a Coding
agent with `patch.apply` and `proc.exec` removed from its perimeter and a different oracle judging
it.

This is the framework's generalisation claim made concrete. It is why the `apps/` package is 79
lines. It is why `derive_phase` lives in `tool_policy.py` rather than the engine (`ADR-0060`: the
episode loop names no domain verb). And it is why the admission gate branches on preset name to
distinguish read-only completion semantics:

```python
is_write_preset = any(prefix in preset_name for prefix in ("code", "bugfix", "write"))
is_read_only    = any(prefix in preset_name for prefix in ("tutor", "research", "read"))
```

A read-only preset is not required to produce a source patch to be admitted as complete; it must
still satisfy task requirements. The completion *criterion* differs by agent type while the
completion *machinery* does not.

**Implication for anyone extending the system:** adding a new agent type — Browser, Reviewer, Data
Analyst — is properly a manifest authoring exercise plus, where genuinely novel effects are needed,
an adapter and a `SinkRegistry` entry. Writing a new Python subsystem for a new agent type would be
evidence that the substrate had failed, not that the agent was ambitious.

### 3.2 The compilation pipeline: from declaration to execution

The path from a manifest to a running episode traverses the following, each stage producing an
immutable artefact:

```
Manifest (JSON)
   -> CanonicalManifest          domain/artifacts/manifest.py  (1,058 LOC)
   -> FrozenComposition          runtime/compose.py            (579 LOC)
   -> ActivationPlan             runtime/activation.py
   -> RunPlan                    runtime/run_plan.py
   -> HarnessSession             runtime/session.py            (1,461 LOC)
   -> EpisodeEngine.run()        agency/episode/engine.py      (1,058 LOC)
   -> Kernel.dispatch()          kernel/dispatch.py            (458 LOC)
   -> EffectAdapter.execute()    adapters/*
```

Canonicalisation (`domain/canonicalisation/jcs.py`, `digest.py`) implements JSON Canonicalisation
Scheme, so every artefact in this chain is content-addressable. This is what permits the ledger to
record *which composition ran* rather than *which composition was requested* — a distinction that
matters the moment presets are edited between runs.

`FrozenComposition` is the pivotal type: once frozen, the composition cannot be renegotiated by
anything downstream. The model receives a compiled context and a tool schema; it does not receive the
composition object and therefore cannot mutate its own configuration. This is the same structural
refusal seen in `ChildRunPlan` — configuration is decided *before* the agent exists.

### 3.3 The inner loop, formally

The episode loop reduces turns until terminal. Per turn:

```
1. COMPILE    CompiledContext from five layers, bounded by token budget
2. RESOLVE    ToolPolicy := resolve_tool_policy(derive_phase(seen_verbs), ...)
3. PROPOSE    raw := model.propose(context, tools ∩ policy.allowed, sampling)
4. PARSE      Proposal := parse_proposal(raw)   | ProposalMalformed
   4a.RECOVER on malformed: recover_proposal(...) -> accept | retry_model | fail_instrument
5. EMIT       ProposalProduced  (the loop's only durable emission)
6. BRANCH     kind ∈ {FINISH, ABSTAIN, ESCALATE} -> terminal via TERMINAL_FOR_KIND
              kind = SPAWN                        -> spawn() under attenuated budget
              kind = EFFECT                       -> continue
7. GATE       AdmissionGate.evaluate(...) on FINISH  -> admissible | rejection_feedback
8. BUILD      EffectRequest from proposal + accumulated spans
9. DISPATCH   Kernel.dispatch(request)  ->  DispatchResult (S0..S12)
10.REDUCE     append Turn; accumulate result spans; check repeats(); check cancellation
11.ADVANCE    Accumulation.advance_turn(reply_spans, result_spans)
```

Termination is guaranteed by three independent bounds: `max_turns` (structural ceiling, not summed
across siblings), budget exhaustion via `Governor`, and no-progress detection via
`Episode.repeats()`. `RunTermination` is a closed enumeration — `COMPLETED`, `ABSTAINED`,
`ESCALATED`, `BUDGET_EXHAUSTED`, `CANCELLED`, `RUNTIME_ERROR`.

A crucial asymmetry: `_TERMINAL_FOR_FAILURE` maps only seven `FailurePath` values to terminations.
*"Everything absent from this table is an event the loop reduces over and continues from — `VG-03
§6.1`: denial is an event, not an exception. A denied call that silently ended the run would make the
denial indistinguishable from a crash."* A scope denial is therefore *feedback*, and the agent gets
another turn to propose something lawful.

### 3.4 The outer loop: session, suspension, and re-entry

`HarnessSession` (`runtime/session.py`, 1,461 LOC — the largest module in the backend) owns the
outer loop. Its principal methods:

| Method | Responsibility |
|---|---|
| `begin_episode()` | Construct the engine, bind ports |
| `run()` | Drive the episode, handle suspension/approval, evaluate |
| `dispatch(request)` | Kernel-mediated effect path with completion observation |
| `checkpoint(turn)` | Capture a `Checkpoint` (digests to blob store) |
| `reconstruct(verify)` | Rebuild `LedgerState` from checkpoint or cold fold |
| `state_digest()` | Content address of current state |
| `turns_consumed()` | Bound accounting across segments |
| `_consult_meta_controller()` | Between-turn `guarded_consult` |
| `_admit_completion()` | Delegate to `AdmissionGate` |
| `_workspace_digest()` | Subject binding for verification freshness |
| `_capture_evidence()` / `_evaluate()` | Exterior verdict, post-termination |

The suspension mechanism deserves particular attention because it is where the inner and outer loops
interlock. When `StandardPolicy` returns `REQUIRE_APPROVAL` in `INTERACTIVE` mode, dispatch returns
`FailurePath.APPROVAL_SUSPENDED` with a `SuspensionToken`:

```python
@dataclass(frozen=True, slots=True)
class SuspensionToken:
    """`K-15`: the token binds the descriptor, so an approval cannot be
    transplanted onto a different call. `K-16`: expiry resolves as denied."""
    token_id: str
    descriptor_digest: str
    principal: str
    expires_at: str
```

The token binds `descriptor_digest`, so a human approving "write file A" cannot have that approval
applied to "write file B". Expiry resolves as *denied*, not as *pending* — fail-closed. The session
resumes through a **new engine instance**, which is why `prior_turns` and `prior_seen_verbs` exist:
without them the phase ladder resets and the turn budget silently doubles.

`Mode.BENCHMARK` changes the semantics: approval never suspends, it denies (`F-07`). The stated
reason is methodological — *"A run that blocks for a human has unbounded wall-clock and a human
contributing to the measured outcome."* The framework refuses to produce benchmark numbers
contaminated by human assistance.

### 3.5 Cancellation

Cancellation is a callable injected into `EpisodeEngine.run(is_cancelled=...)`, polled at the top of
each turn (engine line 351):

```python
if is_cancelled is not None and is_cancelled():
    episode = episode.terminated(RunTermination.CANCELLED, ...)
```

The design is cooperative and turn-granular rather than pre-emptive. This is the correct choice given
the dispatch sequence: cancelling mid-dispatch would risk exactly the leaked-lease and
indeterminate-effect conditions that `K-06` and `K-47` are constructed to prevent. Cancellation
between turns is always safe because the lease is released and the receipt recorded before the loop
re-enters. `FailurePath.CANCELLED` also maps into `_TERMINAL_FOR_FAILURE`, so a cancellation arriving
through the kernel path terminates identically.

### 3.6 Recovery and retry, as presently implemented

`agency/episode/protocol_recovery.py` implements the current recovery state machine. It tracks four
independent counters with separate ceilings:

```python
transport_retries   / max_transport_retries  = 2
protocol_retries    / max_protocol_retries   = 2
truncation_retries  / max_truncation_retries = 1
effect_retries      / max_effect_retries     = 2
```

`RecoveryDecision.status ∈ {accept, retry_model, fail_instrument}`, carrying `retry_feedback`,
`continuation`, `failure_code` and `diagnostics`. `recover_proposal()` is the entry point invoked
from the engine when `parse_proposal` raises `ProposalMalformed`.

Retries are consumed by the real loop rather than merely counted: `_apply_retry()` in the engine
records a `Turn` for the retry, with `proposal_descriptor` digesting the retry reason and feedback,
and — importantly — subjects the retry itself to `episode.repeats()`. A retry that shows no progress
terminates the episode. This closes the most common budget-burn path.

The dimensional separation is well-judged: a transport timeout and an unparseable reply have
different natural retry counts, and collapsing them into one counter means either the transport is
under-retried or the malformed reply is over-retried.

### 3.7 Verification, receipts, and the completion gate

`agency/episode/admission_gate.py` is the mechanism by which a textual claim of completion is
prevented from constituting completion. The evaluation sequence for a write-capable preset:

1. `model_requested_finish` — else `MODEL_DID_NOT_REQUEST_FINISH`
2. read-only preset branch → task requirements only
3. `changed_files` non-empty — else `MISSING_SOURCE_PATCH`
4. every changed file ∈ `inspected_files` — else `MODIFIED_FILE_NOT_INSPECTED`
5. `task_requirements_satisfied` — else `TASK_REQUIREMENTS_UNSATISFIED`
6. receipt present — else `VERIFICATION_REQUIRED`
7. `receipt.passed` ≡ `exit_code == 0 ∧ executed_test_count > 0` — else `VERIFICATION_FAILED`
8. `receipt.workspace_digest == current_workspace_digest` — else `VERIFICATION_STALE`

Step 4 is subtle and valuable: *"Every changed file is itself part of the evidence surface... prevents
a write receipt from standing in for an inspection receipt."* An agent cannot modify a file it never
read.

Step 7 is the anti-vacuity clause: a receipt claiming success with zero executed tests does not pass.
An empty test run cannot be laundered into completion.

Step 8 binds the receipt to the *current workspace state*, invalidating verification after subsequent
modification. `VerificationReceipt` also carries a `task_digest` field. In the present `main` branch
this field is populated in the coercion path but **is not read by any check** — the subject-binding
gap analysed in Part III.

The legacy boolean path is explicitly deprecated in-source: a bare `verification_passed=True` is
*"deliberately insufficient for strict admission because subject freshness is not observable."*

### 3.8 Memory: four ports, scoped and provenance-bearing

`ports/memory.py` defines a segmented memory model as four distinct Protocols over a common base:

| Port | Content |
|---|---|
| `KnowledgePort` | Semantic facts |
| `ExperiencePort` | Episodic trajectory-derived facts |
| `ProjectMemoryPort` | Workspace-scoped durable context |
| `SkillLibrary` | Procedural, promotable |

Access is mediated by `MemoryAuthorizationPort` with `MemoryAccess` and `MemoryBinding` values, and
retrieval carries `RetrievalProvenance`. Memory is therefore not a free-floating vector store: a
retrieved fact enters with provenance, and provenance determines trust, and trust participates in the
authority predicate. A memory that could inject an untrusted fact as an authorising span would
reopen the injection channel that `Accumulation` closes; the `RetrievalProvenance` type is what
prevents it.

`runtime/memory.py` and `adapters/stores/memory_engine.py` (639 LOC) provide the concrete engine.
`session.py::_emit_experience_fact()` shows the write path: receipts from a completed run are folded
into experience memory.

### 3.9 Skills: generation, evaluation, promotion — with no self-promotion

`runtime/skill_lifecycle.py` and `runtime/governance/learning.py` (664 LOC) implement `M-8`. The
critical structural statement: *"Generator, evaluator, and promoter are separate protocols. Promotion
is an explicit signed operation and rollback restores the previous composition; **an agent has no
method to promote itself**."*

The types are `SkillCandidate` (carrying `source_trajectory_digest`, `body_digest`,
`composition_version`), `EvaluationReport`, and `PromotionEvidence`. `governance/learning.py`
requires *"measured held-out lift, regression budgets, and signed evidence"*, and the composition
registry is durable SQLite-WAL with compare-and-swap protection.

This is self-improvement with the loop deliberately cut: an agent may *produce* a candidate skill from
its trajectory, but the promotion path runs through an evaluator it does not control and a signature
it cannot forge. The separation is the same one that keeps evaluators out of `agency`.

### 3.10 Sandboxing and the containment attestation

`adapters/sandbox/` (935 LOC) provides rootless Bubblewrap isolation. The design principle stated in
`rootless.py`:

> *"The adapter never infers containment from its command line. It runs the mount, network and
> denied-syscall probes inside the same constructed perimeter as the worker command."*

Containment is *measured*, not *asserted*. A constructed sandbox is probed from inside itself, and
the resulting `ContainmentReport`/`ProbeResult` carries evidence. A runtime startup failure still
produces an *unverified* report so callers can record the failure, and *"the publication gate remains
fail-closed."* This is the same epistemic pattern as `undeterminable` in the child-runtime contract:
the system distinguishes "contained" from "we could not establish containment," and treats the latter
as disqualifying rather than as passing.

`adapters/evaluators/isolated.py`, `signing.py`, and `gate.py` extend this to evaluation: the
evaluator runs in a sealed bundle at `/sealed-evaluator/bundle`, and results are signed. An agent
cannot tamper with its own grader.

### 3.11 Indexing: LDA and ATLAS as observation sources

`ports/index.py` defines `IndexPort` with `index()`, `files()`, `symbols()`, `dependencies()`,
`tests()`, `repo_map(token_budget)`, returning value-only types: `Symbol`, `DependencyEdge`,
`TestAssociation`, `RepositoryMap`.

The docstring makes the architectural ruling explicit and it is the correct one:

> *"This is the slot a repo-map occupies. It is an **observation** source and nothing more... It is
> explicitly not a second loop — it proposes nothing, ranks nothing on the agent's behalf, and holds
> no authority. A retrieval component that decided what the agent should look at next would be a
> second policy wearing the word 'index'."*

`RepositoryMap` carries `adapter_id`, `source_revision`, `truncated`, and `token_estimate` —
attribution and bounded-ness are part of the value, so a caller always knows whose index answered and
whether the answer was cut off.

The concrete tooling lives *outside* `vanguard/packages/`:

- `tools/007_LLM_DOCS_ATLAS/` — 43 Python modules, with a provider architecture (`git.py`,
  `markdown.py`, `code_ast.py`, `filesystem.py`, `knowledge.py`, `vector_adapter.py`), a profile
  system, CLI, dashboard, and its own test suite including a `test_genericity_guard.py`.
- `tools/lda/`, `tools/scip_adapter.py`, `tools/ast_grep_adapter.py` — indexing adapters.
- `lda.yaml` — profile selection that is *"EXPLICIT ONLY — via this key or `$LDA_PROFILE` — never
  inferred from repository artifacts (no side-channel detection)."*

**On the plugin-versus-integrated question posed in the brief:** the present architecture has already
answered it, and answered it correctly. `IndexPort` is the seam; ATLAS/LDA sit behind it as adapters,
outside the package boundary, in `tools/`. This is the right disposition and should be preserved.
Integrating ATLAS directly into `agency` would violate the "not a second loop" constraint the port
docstring establishes, and would couple the episode loop to a particular retrieval strategy. The
port's `Result[...]` return type means an absent indexer degrades to empty results rather than
raising — so the deterministic textual fallback the framework relies on is a natural consequence of
the port design rather than a special case. The framework does *not* need external MCP plugins to
have a capable toolkit, because the toolkit is expressed as ports and adapters; but the seam should
remain a port, not a direct dependency.

### 3.12 Model routing and provider abstraction

`adapters/models/` contains `factory.py` (unified `create_model()`), `config.py` (registry with
bands: `free`, `fast`, `smart`, `local`, `testing`), `routing.py`, `openrouter.py` (1,199 LOC),
`ollama.py`, `cassette.py` (record/replay), `fake.py`, `stochastic.py`, `lam.py`, `planner.py`,
`invocation.py` (603 LOC).

`ModelPort` is a single-method Protocol:

```python
def propose(self, context: ContextBundle, tools: ToolSchemas,
            sampling: Sampling) -> Result[Proposal]
```

with the invariant that *"Rate limits, timeouts, cassette exhaustion and malformed provider replies
are `instrument_error`. They are not task failures."* The distinction between instrument error and
task failure runs throughout the codebase and is essential to honest measurement: a benchmark run
that failed because OpenRouter returned 503 has not produced evidence about the agent.

The cassette mechanism (`CassettePlayer`/`CassetteRecorder`) provides deterministic replay, which is
what makes `ports/determinism.py`'s counterfactual replay claim tractable.

### 3.13 The event ledger and its projections

`domain/ledger/` (events, reducer at 820 LOC, `state.py`, `projections`, `reconciliation`,
`progress.py`, `agent_view.py`, `session_projection.py`) implements event sourcing as the substrate
of record. `adapters/stores/ledger_jsonl.py` and `event_store.py` (549 LOC) provide persistence.

The read models are worth naming because they are what metacognition consumes: `AgentView`,
`ProgressView`, `ConfidenceRecord`. The meta-controller receives *projections*, not the raw log, and
not the live session — reinforcing that it is a pure function of observable state.

`runtime/ledger/recovery.py` and `domain/ledger/reconciliation.py` handle the log-repair path.

---

## 4. Complete Module Topography

```
vanguard/packages/
├── ports/                    1,580 LOC — Protocols only; imports nothing outward
│   ├── kernel.py             Clock, EffectAdapter, EventSink, Ledger
│   ├── model.py              ModelPort.propose -> Result[Proposal]
│   ├── environment.py        10 types — filesystem/process/workspace effects
│   ├── evaluator.py          5 types — exterior grading
│   ├── index.py              IndexPort, Symbol, RepositoryMap, DependencyEdge
│   ├── memory.py             KnowledgePort, ExperiencePort, ProjectMemoryPort, SkillLibrary
│   ├── sandbox.py            SandboxRunner, ContainmentReport, ProbeResult, SandboxReceipt
│   ├── child_runtime.py      ChildRunPlan / ChildRunResult / ChildRuntimePort
│   ├── meta_controller.py    MetaController, StrategyDirective, DIRECTIVE_KINDS
│   ├── determinism.py        counterfactual replay contract
│   ├── event_store.py        Result[T], append-only store
│   ├── blob_store.py         content-addressed storage
│   ├── evidence_errors.py    evidence error taxonomy
│   └── spi.py                6 service-provider types
│
├── kernel/                   1,769 LOC — Trusted Computing Base
│   ├── dispatch.py     458   S0..S12; Kernel, DispatchResult, SuspensionToken, KernelAlarm
│   ├── grants.py       244   Grant, GrantIssuer, HmacAuthenticator, descriptor_of
│   ├── budget.py       215   Governor, Lease, Reservation, ADDITIVE_DIMENSIONS
│   ├── attenuation.py  215   Scope, Constraints, attenuate, RISK_ORDER
│   ├── model.py        176   EffectRequest, Event, FailurePath, SinkClass, Span, Trust
│   ├── provenance.py   144   Accumulation, authority_violation, combine, weakest
│   ├── policy.py       139   StandardPolicy, Decision, Outcome, Mode
│   └── classifier.py   134   StandardClassifier, SinkRegistry, HeldAuthority, SinkMismatch
│
├── domain/                   9,586 LOC — pure values
│   ├── artifacts/manifest.py 1,058  CanonicalManifest; graph.py; skill_index.py
│   ├── ledger/         events, reducer(820), state, projections, reconciliation,
│   │                   progress, agent_view, session_projection
│   ├── canonicalisation/     jcs.py (JSON Canonicalisation Scheme), digest.py
│   ├── evidence/       foundation, envelope, claim, baseline, audit(586),
│   │                   preregistration, guardrails
│   ├── execution/      scope.py, lineage.py, operation.py
│   ├── transforms/     contracts, schemas, protocol/response_wrangler,
│   │                   repository/change_surface
│   ├── selectors/      resource_selector(501), independence
│   ├── wire/           jsonrpc, contracts, result, types_gen(707)
│   ├── workflows/      contracts, reducer
│   ├── primitives/     uuidv7 etc.
│   └── workspace.py
│
├── agency/                   8,844 LOC — the loop and its cognition
│   ├── episode/
│   │   ├── engine.py           1,058  EpisodeEngine, EpisodeOutcome, spawn()
│   │   ├── state.py                   Episode, Turn, Proposal, ProposalKind, RunTermination
│   │   ├── admission_gate.py          AdmissionGate, VerificationReceipt, AdmissionVerdict
│   │   ├── tool_policy.py             ToolPolicy, resolve_tool_policy, derive_phase
│   │   └── protocol_recovery.py       ProtocolRecoveryState/Policy, RecoveryDecision
│   ├── context/       layers.py (L1..L5), compiler.py, packet.py, compaction.py
│   ├── forge/         engine(772), patcher(603), resilient_patcher(504), compiler, facade
│   ├── chimera/       engine(493), blackboard(559), search, router, verification,
│   │                  symbolic, skills, compiler, patcher, governor, retrieval
│   ├── manifests/     38 compositions + loader, validator, discovery
│   └── provenance.py
│
├── runtime/                 24,688 LOC — composition, session, governance
│   ├── session.py      1,461  HarnessSession — the outer loop
│   ├── service/        1,348  service.py, server.py, contract.py, inbox.py, studio_gateway(721)
│   ├── app_service.py    838  ApplicationService
│   ├── delegation.py     771  spawn planning / attenuated child plans
│   ├── root.py           768  composition root
│   ├── artifacts.py      689
│   ├── governance/       engine, definitions, learning(664), approvals(618)
│   ├── skill_evaluation.py 622 / skill_lifecycle.py / skill_index.py
│   ├── checkpoints.py    583  Checkpoint, CheckpointPins, CheckpointManager, Reconstruction
│   ├── compose.py        579  FrozenComposition
│   ├── lab_driver.py     593
│   ├── trajectory.py     474  + trajectory_reader.py
│   ├── registry/         compiler, validator, broker, worker, lifecycle, sandbox
│   ├── ledger/           projections.py, recovery.py
│   ├── task_state.py            CodingTaskState, Discovery, DeadEnd, TodoItem, RouteDecision
│   ├── meta_controller.py       consult, guarded_consult, validate_directive
│   ├── activation.py / run_plan.py / topology.py / scheduler.py / workflow_scheduler.py
│   ├── model_selection.py / tier_escalation.py / provider_health.py / routing
│   ├── evidence_capture.py / foundation_evidence.py / formal_evidence.py / assurance.py
│   ├── paired_evaluation.py / pareto_measurement.py / reproducibility.py / determinism.py
│   ├── memory.py / retention.py / provenance.py / authority_audit.py
│   ├── workflow_recovery.py / repair.py / staged_workflow.py
│   └── cli.py / entrypoint.py / bootstrap.py / standalone_daemon.py / studio/
│
├── adapters/                10,927 LOC — concrete I/O
│   ├── models/        openrouter(1,199), ollama, fake, cassette, stochastic, lam,
│   │                  planner, invocation(603), factory, config, routing, env_loader
│   ├── environment/   git(1,089), sandboxed, fake(681), tableworld
│   ├── sandbox/       rootless(297), worker(251), platform(182), toolkit, ceiling, fake
│   ├── stores/        event_store(549), ledger_jsonl, blob_store, memory_engine(639), repo_index
│   ├── evaluators/    daemon, client, isolated, gate, signing, unavailable, fake, suites/
│   ├── bindings/      base, code, table, lex_reproducer, lex_surgical_editor
│   └── context/       window.py
│
└── apps/                        79 LOC
    └── coding_max/facade.py     CodingMaxFacade — preset selection + delegation only
```

**Supporting trees outside the package:**

- `tools/007_LLM_DOCS_ATLAS/` (43 modules) — the documentation/code atlas with pluggable providers
- `tools/001_LLM_API_ROUTER/`, `tools/002_LLM_API_MOCK/` (74 modules) — provider routing and mocking
- `tools/lda/`, `scip_adapter.py`, `ast_grep_adapter.py` — index adapters
- `benchmarks/`, `evidence/`, `packs/`, `schemas/`, `test/` (2,486 collected tests)
- `vanguard/clients/` — CLI, TUI, desktop, studio, lab (frontend; out of scope here)

---

*Part III: code health assessment, empirical anomalies, and frontier gaps. Part IV: the Aether
meta-framework thesis and evolution path.*
