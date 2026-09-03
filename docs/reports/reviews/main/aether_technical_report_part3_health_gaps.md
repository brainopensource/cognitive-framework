# AETHER / Vanguard — Technical Report, Part III
## Code Health, Empirical Anomalies, and Frontier Gaps

*Continues Parts I–II. Findings below are measured against `main`, not asserted.*

---

## 5. Code Health Assessment

### 5.1 Method

Assertions in this section are backed by measurement, because "bloat" and "dead code" are claims that
degrade into aesthetics when made informally. I used: LOC census by layer; module-name collision
analysis; reverse-import analysis for orphan detection (with a second pass against `test/`, `tools/`
and `benchmarks/` to distinguish *unreferenced* from *externally-driven*); dependency-direction
verification by grep; and targeted reading of suspected duplicates.

### 5.2 Positive findings: what is unusually healthy

**Dependency direction is enforced, not merely documented.** `grep` for imports of `runtime`,
`agency`, or `adapters` from within `kernel/` returns zero. `ports/` imports nothing outward.
Frameworks of this size almost always have at least one inversion violation smuggled in for
convenience; this one does not. This is the single strongest signal about the codebase's discipline.

**Annotation density is exceptionally high and unusually honest.** The prevailing comment style is
not "what this does" but "which defect this ordering prevents." `K-04` through `K-48`, `MF-KRN-001`
through `MF-KRN-008`, `F-06` through `F-13`, `ADR-0047` through `ADR-0100` are referenced inline at
the point of enforcement. The `classifier.py` docstring's admission that a hardcoded constant had
been mistaken for a property of the taint model, and written into three design documents, is the kind
of self-report that most codebases suppress. Comments of this type have real engineering value: they
prevent a future maintainer from "simplifying" an ordering constraint whose motivation is invisible
locally.

**Only 8 TODO/FIXME/XXX/HACK markers across 260 modules, and exactly 1 `raise NotImplementedError`.**
For 57k LOC this is remarkably low and suggests the codebase does not carry a large tail of stubbed
intentions.

**Failure enumerations are closed and asserted.** `FailurePath`, `RunTermination`, `Outcome`,
`SinkClass`, `Trust`, `DIRECTIVE_KINDS`, `CHILD_OUTCOMES`, `ADDITIVE_DIMENSIONS` are all closed sets,
and `test/kernel/test_dispatch.py` asserts directly that no dispatch exit escapes the table. Open
string-typed error channels are the usual entropy source in systems like this; they are largely
absent.

**Integer-only money and time.** No float appears in `budget.py`. Micro-USD and milliseconds
throughout. This eliminates an entire class of accumulation error in long runs.

### 5.3 Finding 1 — runtime layer mass concentration (the principal structural risk)

`runtime/` is **24,688 LOC across 67 top-level modules** — 43% of the backend, and larger than
`kernel` + `ports` + `domain` + `agency` combined (21,779). By comparison the TCB it protects is
1,769 LOC.

This is the codebase's dominant architectural asymmetry. It is not automatically a defect — the
runtime is legitimately where composition, persistence, governance, evaluation and service surfaces
converge — but three specific consequences follow:

1. **`session.py` at 1,461 LOC is the largest module in the backend** and carries at least eight
   distinct responsibilities: engine construction, port binding, suspension/approval resolution,
   checkpointing, reconstruction, meta-controller consultation, completion admission, evidence
   capture and evaluation. Its private helper surface (`_LayeredOperator`, `_SwappablePolicy`,
   `_admit_turn_result`, `_record`, `_suspension`, `_resolve`, `_with_diff_headers`) indicates it has
   absorbed responsibilities that were once elsewhere. This is the module most likely to resist
   modification and most likely to harbour interaction bugs.

2. **Naming collisions across layers create navigational ambiguity.** Four `engine.py`, four
   `compiler.py`, three `provenance.py`, three `facade.py`, three `contracts.py`, two `state.py`, two
   `worker.py`, two `validator.py`, two `workspace.py`. `provenance.py` is the worst case: it exists
   in `kernel/`, `agency/` and `runtime/` with genuinely different semantics (the authority
   accumulator versus derivation tracking). A reader encountering `from ..provenance import ...`
   must resolve the layer before understanding the meaning.

3. **The measurement subsystem is large and partially self-referential.** `paired_evaluation`,
   `pareto_measurement`, `reproducibility`, `determinism`, `formal_evidence`, `foundation_evidence`,
   `evidence_capture`, `assurance`, `scoring`, `outcome_labels`, `skill_evaluation`, `dogfood`,
   `lab_driver`, `task_sets` collectively exceed the kernel by a wide margin. This is defensible for
   a research substrate whose thesis is that claims require evidence, but it means a large fraction
   of the codebase serves epistemics rather than execution, and that fraction should be understood as
   such when estimating maintenance cost.

### 5.4 Finding 2 — externally-driven leaf modules (not dead code, but easily mistaken for it)

Reverse-import analysis initially flagged 15 `runtime/` modules as never imported from within
`vanguard/`. A second pass shows all are referenced from `test/`, `tools/`, or `benchmarks/`:

| Module | External refs | Interpretation |
|---|---|---|
| `dogfood` | 29 | Heavily exercised harness |
| `scoring` | 21 | Measurement leaf |
| `paired_evaluation`, `tier_escalation`, `formal_evidence` | 8 each | Study instrumentation |
| `task_sets` | 7 | Benchmark definition |
| `trajectory_reader` | 5 | Analysis leaf |
| `skill_evaluation` | 4 | Governance leaf |
| `provider_health` | 3 | Ops leaf |
| `workflow_scheduler`, `staged_workflow`, `workflow_recovery`, `pareto_measurement` | 2 each | **Thin — review candidates** |

The correct reading: these are *entry points*, not dead code. But the four with only two external
references warrant explicit review. `workflow_scheduler` and `staged_workflow` in particular overlap
conceptually with `topology.py`, `scheduler.py` and `delegation.py`, and the presence of five modules
in the general vicinity of "orchestrating multi-step work" with unclear division of labour is a
genuine comprehension cost. I would not delete them without tracing; I would require each to
document, in one sentence, why it is not one of the other four.

### 5.5 Finding 3 — genuine patcher duplication

Three patch appliers exist:

| Module | LOC | Relationship |
|---|---|---|
| `agency/forge/resilient_patcher.py` | 504 | Canonical 9-strategy cascade: `_match_line_trimmed`, `_match_whitespace_normalized`, `_match_indentation_flexible`, `_match_unicode_normalized`, `_match_boundary_trimmed`, `_match_block_anchors`, `_match_ast_node`, `_match_context_aware` |
| `agency/forge/patcher.py` | 603 | **Delegates** — exposes `apply_resilient_patch()`; adds unified-diff parsing, AST symbol replacement, atomic rollback |
| `agency/chimera/patcher.py` | 147 | **Independent reimplementation** — imports `ast`, `re`, `shutil` directly; does *not* import `resilient_patcher` |

The `forge` pair is a healthy layering: a strategy library plus a transactional façade over it.

The `chimera` module is genuine duplication. Its own docstring claims it *"Combines: ... 9-Strategy
Resilient Surgical Patcher (`surgical_patch`)"*, but it does not import the resilient patcher; it
reimplements against `ast` and `re`. This is the clearest single instance of avoidable duplication I
found, and it is the highest-value consolidation target because patch application is precisely where
divergent fuzzy-matching semantics produce irreproducible behaviour between presets. Two presets that
both claim "9-strategy resilient patching" but resolve a whitespace-ambiguous hunk differently will
produce benchmark differences that are attributed to the agent and actually belong to the patcher.

### 5.6 Finding 4 — manifest sprawl

38 manifest directories, of which **16 carry version or experiment suffixes**: `v090`, `v2`, `v2b`,
`v3`, `v3luna`, `-shaped`, `-minimal`, `-control`, `-falsifier`. Examples: `vg-code-max`,
`vg-code-max-v2`, `vg-code-max-v2b`, `vg-code-max-v3`, `vg-code-max-v3luna`.

Because manifests are pure data and heavily share components (every one examined referenced
`vg-code-default/context-policy.json`, `routing-policy.json`, `budget-policy.json`), the marginal
cost of each is low and the sprawl is far less harmful than equivalent code sprawl would be. This is
the architecture working as intended: experiments are cheap because they are declarations.

Nonetheless there is a real cost: `registry.json` and `kinds.json` must enumerate them, the discovery
and validation path must handle them, and a newcomer cannot tell which manifests are *canonical*
versus *historical experiment*. A `status` field (`canonical` | `experiment` | `archived`) in each
manifest would resolve this at negligible cost and is the cheapest legibility improvement available
in the repository.

### 5.7 Finding 5 — the `apps/` layer is nearly vestigial

79 LOC for the entire application layer. `CodingMaxFacade` validates a preset against a three-element
tuple, resolves a manifest path, and forwards six methods to `ApplicationService`. `CodingMax` is an
alias.

I read this as *evidence of success rather than incompleteness* — the composition-over-code thesis
means there is genuinely almost nothing for an app layer to do. But it does mean the name "Coding
Max" designates a preset triple, not a subsystem, and any documentation implying otherwise is
misleading. Note also that `PRESETS = ("fast", "balanced", "max")` hardcodes three names while 38
manifests exist; the façade exposes a deliberately narrow slice.

### 5.8 Finding 6 — test suite scale versus green-ness

2,486 tests are collected. In this container the selected subset runs 20 failed / 86 passed / 2
skipped, with one collection error in `test/contracts/test_m5a_schema_vectors.py`. The failures are
environmental (absent provider credentials, unavailable sandbox), not logical. This is expected for a
suite that legitimately exercises sandboxing and live providers.

The consequence for a new contributor is nonetheless significant: **there is no green baseline
obtainable without environment provisioning**, so "did I break something?" must be answered by
differential comparison rather than by a passing suite. A documented, hermetic subset — cassette-only
models, fake sandbox, fake evaluator — that is *expected to be 100% green* would materially lower the
contribution barrier. The pieces already exist (`adapters/models/cassette.py`,
`adapters/sandbox/fake.py`, `adapters/evaluators/fake.py`); what is missing is the declared subset
and the guarantee.

### 5.9 Summary judgement

This is a high-discipline codebase with an unusually rigorous core and a heavy periphery. The kernel,
ports and domain layers are, by the standards of agent frameworks, exemplary: small, closed, inverted
correctly, and annotated with the failure history that justifies each constraint. The risk is not in
the TCB; it is in the 24.7k-LOC runtime, where responsibility boundaries have blurred (`session.py`),
where several modules occupy adjacent conceptual territory without clear demarcation (the five
scheduling-adjacent modules), and where one genuine duplication exists in a semantically dangerous
place (`chimera/patcher.py`).

---

## 6. Empirical Anomalies & Frontier Gaps

### 6.1 Anomaly — the unread `task_digest`

`VerificationReceipt` declares `task_digest: str = ""`. The mapping-coercion path populates it from
`task_digest`/`taskDigest`. **No branch in `AdmissionGate.evaluate()` reads it.**

The gate binds a receipt to the workspace (`VERIFICATION_STALE`) but not to the task. Consider a
resumed or long session in which task A completed verification, then task B begins in the same
workspace with no intervening modification. `receipt.workspace_digest == current_workspace_digest`
holds — legitimately, since nothing changed — and every other check passes on the residual state.
Task B is admitted as complete on task A's evidence.

This is a *subject-binding* gap distinct from the *freshness* gap the existing check closes.
Freshness asks "is this evidence current?"; subject-binding asks "is this evidence about the thing we
are claiming?" The presence of an unread field indicates the design anticipated the check; the
implementation did not land it.

The severity is conditional on how often a workspace hosts sequential tasks without modification
between them — which, for benchmark harnesses running task suites and for resumed long sessions, is
precisely the common case rather than an edge case.

### 6.2 Anomaly — the recovery taxonomy is narrower than the failure space

`protocol_recovery.py` distinguishes four dimensions: transport, protocol, truncation, effect. The
system as a whole encounters at least eight distinct failure classes with materially different
correct responses:

| Failure | Correct response | Presently |
|---|---|---|
| Transport timeout | Backoff, retry identical | `transport_retries` ✅ |
| Unparseable reply | Re-ask, reduced schema | `protocol_retries` ✅ |
| Truncated reply | Request shorter reply | `truncation_retries` ✅ |
| Invalid tool name/args | Return schema + valid names | folded into `effect_retries` |
| Patch preimage mismatch | **Re-read then rebuild edit** | folded into `effect_retries` |
| Test failure | Return diagnostics to planner | folded into `effect_retries` |
| Capability denial | Escalate; **never retry** | reduced over as an event |
| Provider auth/quota | Switch provider or terminate | folded into transport |

The consequential collapse is patch-mismatch and test-failure into a single `effect_retries` counter.
These demand opposite responses: a failed patch means *the context is stale, re-read before
re-editing*; a failed test means *the change is wrong, diagnose the cause*. A single counter with a
single response cannot serve both, and the failure mode of getting it wrong is re-applying an
identical hunk to an identical preimage — which cannot succeed by construction.

The kernel handles capability denial correctly (it is an event the loop reduces over, not a retry),
so the dangerous case of retrying a denied effect does not arise. But there is no explicit,
enumerated policy asserting this at the recovery layer.

### 6.3 Anomaly — no cross-turn attempt identity

`Episode.repeats()` detects a repeated `(state_digest, proposal_descriptor, progress_signal)` triple
within a bounded recent window (`limit`). This catches tight livelock.

It does not catch the *A → B → A* pattern, where an agent alternates between two failing approaches,
nor does it survive as a durable record: retry counters live in `ProtocolRecoveryState`, which is
loop-local. `CodingTaskState` carries `DeadEnd(attempt, reason, evidence)` — the semantic
representation of "this was tried and failed" — and `RouteDecision`, but these are descriptive state
for the model's benefit, not enforced constraints on the recovery policy.

The gap: **a resumed run can re-spend retries it already burned before the restart.** Checkpointing
captures ledger state, and `CodingTaskState` captures dead ends, but the retry counters themselves
are reconstructed fresh. For long autonomous sessions with multiple suspensions this is a budget
leak of the same character as the refund-clamp bug `K-07` guards against — small, repeated, and
invisible.

### 6.4 Anomaly — behavioural model heterogeneity is unmodelled

`adapters/models/` supports OpenRouter, Ollama, cassettes, fakes, and a band-based alias registry
(`free`/`fast`/`smart`/`local`/`testing`) in `config.py`. What it does not model is *behavioural*
difference: whether a given model emits native tool calls, how reliably its JSON parses, whether it
emits reasoning tokens that must not be replayed into the next turn, what its real context ceiling
is, or which edit representation it is most accurate with.

`ModelPort.propose(context, tools, sampling)` is provider-agnostic at the type level, which pushes
all heterogeneity into the adapters. `openrouter.py` at 1,199 LOC and `invocation.py` at 603 LOC are
where it accumulates. The architectural consequence is that a prompt and tool schema tuned for a
native tool-calling frontier model is issued unchanged to a 7B local model, and the resulting
degradation presents as agent incapability rather than as dialect mismatch.

This is a *frontier gap* rather than a defect: nothing is incorrect, but a dimension of variation
that materially affects success rate is currently invisible to the system and therefore
unmeasurable.

### 6.5 Frontier gap — multi-agent coordination is a seam without a plane

The recursion machinery is complete and rigorous. `ports/child_runtime.py` defines
`ChildRunPlan`/`ChildRunResult`/`ChildRuntimePort` with the three structural refusals (frozen plan,
value-only result, `undeterminable` outcome). `runtime/delegation.py` (771 LOC) decides what a child
may be. `EpisodeEngine.spawn()` executes an attenuated child episode with budget conservation.
`ProposalKind.SPAWN` is a first-class proposal. `runtime/topology.py` and `scheduler.py` exist.

What is absent is a **declarative topology type**: a validated DAG of named roles with dependencies,
per-role budget shares, mailboxes, merge policy and bounded concurrency, such that adding
"planner → implementer → verifier" is a data change rather than orchestration code. Presently a
multi-role workflow must be expressed imperatively over `spawn`, which means each topology carries
its own budget-conservation and result-merging logic — the exact condition under which conservation
bugs appear.

Note this is a *composition* gap, not a *capability* gap. Every primitive required is present and
correct; what is missing is the declarative layer over them.

### 6.6 Frontier gap — metacognition has a seam but no measured occupant

`MetaController`, `StrategyDirective`, `guarded_consult` with its determinism falsifier,
`AgentView`/`ProgressView`/`ConfidenceRecord` projections, and the twelve-directive closed vocabulary
constitute a well-designed, safety-bounded seam. `session.py::_consult_meta_controller()` invokes it
between turns.

The gap is that the substrate provides the *seam* and the *falsifiers*, not a *controller with
demonstrated lift*. This is arguably correct sequencing — building the measurement apparatus before
the thing to be measured is the disciplined order, and `paired_evaluation.py` plus
`pareto_measurement.py` exist precisely to support that comparison. But it should be stated plainly:
metacognition in this codebase is presently infrastructure, and any claim about metacognitive benefit
would require running a controller through the paired-evaluation path.

### 6.7 Frontier gap — local models are supported but not specialised

`OllamaModel` exists and `local` is a registry band. The report's ambition of using small local models
for mechanical subtasks — file ranking, log summarisation, failure classification, context compression
— is *architecturally supported* (they are just `ModelPort` implementations) but not *architecturally
expressed*: there is no role-eligibility mechanism that would prevent a 7B model from being selected
as the planner, nor a declared taxonomy of which subtasks are cheap-model-eligible.

`runtime/model_selection.py` and `tier_escalation.py` handle routing and escalation by tier, so the
selection machinery exists. What is missing is the per-model capability declaration that would let
selection be *principled* rather than *configured*.

### 6.8 Frontier gap — no hermetic green baseline

Covered in §5.8. Restated here because it is a frontier gap for *contribution velocity* rather than
for capability, and it is the cheapest to close.

### 6.9 What is emphatically not a gap

For the avoidance of doubt, several things commonly proposed as missing in systems of this type are
present and correct here, and should not be rebuilt:

- **A single effect path.** `Kernel.dispatch` is enforced, not conventional.
- **Semantic resume state.** `CodingTaskState` carries objective, plan, next action, hypotheses,
  inspected/modified files, verification plan, discoveries, dead ends, TODOs bound to receipt
  digests, route decisions, and remaining budgets.
- **Evidence-gated completion.** `AdmissionGate` exists and is strict (modulo §6.1).
- **Injection defence.** The authority predicate over monotone span accumulation.
- **Budget conservation with overrun.** `K-07`.
- **Sandbox attestation by probe.** Containment is measured from inside the perimeter.
- **Evaluator isolation.** Agents cannot grade themselves; `agency` cannot import an evaluator.
- **Agent generality.** Coding, Research and Tutor already share the loop; they are manifests.

---

*Part IV: the Aether meta-framework thesis, plugin connectivity, local-model composition, and the
evolution path.*
