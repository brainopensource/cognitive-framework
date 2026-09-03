# AETHER / Vanguard — Technical Report, Part IV
## The Meta-Framework Thesis, Universal Connectivity, and the Evolution Path

*Concludes Parts I–III. **Section 7 describes present implementation. Section 8 onward is
prospective and is explicitly not a description of `main`.***

---

## 7. The Aether Abstraction: What Is Already True

### 7.1 The distinction between framework and agent, as presently realised

The brief asks for the distinction between "the agents" and "the framework itself." The codebase
answers this sharply, and the answer is the foundation of everything prospective that follows.

**The framework is the invariant machinery:** the kernel (authority, budget, dispatch), the ports
(seams), the domain (values, canonicalisation, ledger algebra), the episode loop (turn reduction),
the context compiler (five layers), the session (suspension, checkpoint, resume), and the evaluation
apparatus. None of it names a domain verb. `ADR-0060` is explicit that *the episode loop must name no
domain verb*, which is why `_VERIFY_TRIGGERS = {"patch.apply"}` lives in `tool_policy.py` and not in
`engine.py`.

**An agent is a `FrozenComposition`:** a system prompt, a tool schema set, a declared capability
perimeter with sink classes and risk tiers, a context policy, a routing policy, an approval policy, a
budget policy, and an evaluator identity. That is the whole of it. The empirical demonstration in
Part II §3.1 — Coding, Research and Tutor sharing context, routing, budget and approval policies
byte-for-byte, differing only in prompt, capabilities and oracle — is not a design aspiration; it is
what the manifests contain.

The consequence, stated precisely: **an agent in this framework has no existence as a runtime
object.** There is no `ResearchAgent` class. There is an episode, executed under a composition, whose
perimeter happens to exclude `patch.apply`. `ports/child_runtime.py` makes the same point about
delegation: *"A spawn does not create an agent object. It creates a bounded causal region."* Agents
are, in the framework's own terms, *ephemeral projections*.

### 7.2 Why this already constitutes a meta-framework

The brief asks how Aether will "become a meta-framework capable of further generalization —
allowing for the creation of new substrates where general task solvers operate." The significant
observation is that the structural precondition is already satisfied, and it is satisfied by a
specific property: **the framework's extension points are ports, and its configuration surface is
data.**

To create a new *substrate* — a new domain in which general task solvers operate — requires exactly
four things in the present architecture, none of which is a modification to the kernel or the loop:

1. **Effect adapters** implementing `EffectAdapter` for the new domain's operations.
2. **`SinkRegistry` registrations** classifying each new verb as `PURE`, `OBSERVATION` or
   `PRIVILEGED`, with the registry refusing misclassification at registration time.
3. **An evaluator** implementing `EvaluatorPort`, run in the sealed bundle, producing a signed
   verdict.
4. **Manifests** declaring compositions over the above.

The existence of `adapters/environment/tableworld.py` and the `vg-table-default` manifest alongside
the git/filesystem environment is the proof by construction: a second, non-code domain already runs
on the same kernel, the same loop, the same budget governor and the same admission machinery. The
`vg-herbs`, `vg-shell-only` and `vg-chimera-v1` manifests represent further substrate and strategy
variation.

This is what makes the meta-framework claim credible rather than rhetorical. The generalisation is
not promised for a future refactor; it is demonstrated by a working second domain.

### 7.3 The rewritable harness: what "harness engineering" means here

The brief mentions "rewriting of loops and harness engineering." Presently the loop is singular —
`EpisodeEngine.run()` — and this is deliberate: a second loop would be a second policy, which
`ports/index.py` explicitly forbids for retrieval and `EpisodeEngine` forbids for effects.

But harness variation is nonetheless already expressible along five axes without touching the loop:

| Axis | Mechanism | Present examples |
|---|---|---|
| Prompt/contract | `system_prompt` component | 38 manifests |
| Tool surface | `tools` components + `capabilities` | read-only vs. write presets |
| Phase gating | `resolve_tool_policy` / `derive_phase` | inspect → edit → verify ladder |
| Context assembly | `context_policy` + `ContextCompiler` | L1–L5 layer budgets |
| Strategy | `MetaController` plugin | seam present, twelve directives |

The `MetaController` seam is the designated point at which loop *behaviour* is varied without loop
*rewriting* — it can direct `revise_plan`, `request_context`, `abandon_hypothesis`,
`change_verification`, `delegate`, `fork`, `stop`. Critically it cannot alter authority, which is why
harness experimentation cannot compromise safety properties: the experiment surface and the security
surface are disjoint by construction.

### 7.4 Plugin connectivity: the seam already exists and is a port

The brief asks about "universal plugin connectivity... allowing for the easy swapping of process
blocks — such as skill nodes, caching nodes, compression nodes, index nodes."

The present architecture's answer is that **each such node is a port implementation**, and the ports
already exist or have obvious homes:

| Proposed node | Present port | Status |
|---|---|---|
| Index node | `IndexPort` (`symbols`, `dependencies`, `tests`, `repo_map`) | **Present**; ATLAS/LDA/SCIP/ast-grep sit behind it |
| Skill node | `SkillLibrary` + `SkillGenerator`/`SkillEvaluator`/`SkillPromoter` | **Present**, with signed promotion |
| Memory node | `KnowledgePort`, `ExperiencePort`, `ProjectMemoryPort` | **Present**, provenance-bearing |
| Compression node | `agency/context/compaction.py` + `ContextCompiler` | **Present as module**, not yet a port |
| Caching node | `PREFIX_LAYERS` breakpoints; `adapters/context/window.py` | Partial |
| Model node | `ModelPort` | **Present** |
| Sandbox node | `SandboxRunner` with attestation | **Present** |
| Evaluator node | `EvaluatorPort`, sealed + signed | **Present** |
| Child runtime node | `ChildRuntimePort` | **Present** |

The governing constraint, stated across several port docstrings, is the one that makes this safe:
**no plugin may emit effects directly, create a parallel ledger, or alter completion.** `IndexPort`
*"proposes nothing, ranks nothing on the agent's behalf, and holds no authority."* `MetaController`
*"cannot emit, access stores, call a model, or bypass ordinary proposal and kernel authorization
paths."* A plugin contributes *observations* or *policy preferences*; the kernel remains the only
authority and the ledger remains the only record.

This is a materially better answer to plugin connectivity than an MCP-style external tool protocol,
for a specific reason: MCP-style connectivity typically grants a plugin the ability to *perform an
effect* and return a result. In this architecture a plugin that performed an effect would bypass S0–
S12 and would therefore have no grant, no lease, no descriptor binding, no receipt, and no presence
in the ledger. **The framework does not need external plugin protocols to have a capable toolkit,
because its toolkit is expressed as ports and adapters, and its adapters are inside the authority
perimeter.** Any future MCP bridge should therefore be implemented as an `EffectAdapter` behind the
kernel — never as a parallel execution channel.

### 7.5 Local models and hybrid computation: present state

`OllamaModel` is a full `ModelPort` implementation; `local` is a band in the model registry;
`adapters/models/lam.py`, `planner.py` and `stochastic.py` provide additional model-shaped
components; `runtime/model_selection.py` and `tier_escalation.py` perform tier-based routing and
escalation.

Non-LLM computation is likewise already load-bearing, and this deserves emphasis because it is
frequently overlooked in agent architectures. The following are deterministic algorithms, not model
calls, and each substitutes for a task an LLM would otherwise be asked to do worse and more
expensively:

- **Patch application** — the 9-strategy cascade in `resilient_patcher.py` (line-trimmed,
  whitespace-normalised, indentation-flexible, unicode-normalised, boundary-trimmed, block-anchored,
  AST-node, context-aware). Each strategy is a mechanical repair of a class of model imprecision.
- **AST symbol replacement** — `forge/patcher.py::replace_symbol` and `apply_ast_replace`.
- **Repository mapping** — `IndexPort` implementations over Tree-sitter/SCIP/ast-grep adapters, with
  bounded `token_estimate` and explicit `truncated` flags.
- **Canonicalisation and digesting** — JCS, giving content-addressability for free.
- **Ledger folding** — `domain/ledger/reducer.py` (820 LOC) is pure state reduction.
- **Context compaction** — `agency/context/compaction.py`.
- **Test association** — `TestAssociation` derived structurally, not inferred.

The architectural principle visible here is sound and worth naming: **anything that can be decided
deterministically is decided deterministically, and the model is reserved for the genuinely
underdetermined.** The resilient patcher is the clearest case — rather than asking a model to produce
byte-perfect diffs, the system accepts imprecise output and repairs it mechanically through an
ordered strategy cascade. This is the highest-leverage form of "improving LLM results with local
algorithms" and it is already implemented.

---

## 8. Avant-Garde Theoretical Propositions

> **Everything from this point is prospective.** None of it is present in `main`. It is ordered by
> dependency, and each item states what would make it *false* or unnecessary.

### 8.1 Proposition 1 — Behavioural typing of models

**Claim.** Model heterogeneity should be a *declared type*, not adapter-internal knowledge. A
`ModelBehaviorProfile` — tool-call style, JSON reliability, context ceiling, reasoning-token
emission, preferred edit representation, integer cost, role eligibility — makes a currently invisible
variance dimension measurable and lets the intent→wire compilation be a single seam rather than
distributed conditionals.

**Why it precedes everything else.** It is the enabling substrate for role-eligible model selection
(§8.4), for principled degradation under protocol failure (§8.2), and for honest cost accounting in
multi-role plans (§8.3).

**Falsified if:** measured parse-failure and success rates prove insensitive to dialect, in which
case the variance was noise and the abstraction is unearned complexity.

### 8.2 Proposition 2 — Failure as a typed lattice with escalating strategy

**Claim.** The four current recovery dimensions should become an enumerated taxonomy over the eight
classes identified in Part III §6.2, each with exactly one corrective action, and — the essential
part — with an *attempt identity* that makes blind retry inexpressible.

The formal shape: let an attempt be fingerprinted by `(failure_class, action, target, state_digest)`.
A recovery policy that is asked to handle a fingerprint already in its ledger must escalate strategy
rather than repeat the action. This makes "re-apply the same hunk to the same preimage" — an
operation that cannot succeed by construction — unreachable.

**Dependency on §8.1:** the degradation ladder for protocol failure (native → JSON schema → fenced →
line grammar) requires a declared dialect to degrade *from*.

**Critical constraint:** the recovery layer must never widen authority. Capability denial must carry
a retry budget of exactly zero and escalate to a human. A recovery path that re-attempts denied
effects is a privilege-escalation mechanism, and would be the most dangerous possible regression in
this codebase.

**Falsified if:** telemetry shows the collapsed `effect_retries` counter already produces correct
behaviour in practice, because the model self-corrects on feedback.

### 8.3 Proposition 3 — Topology as validated data

**Claim.** Multi-agent structure should be a declarative DAG — named roles, dependencies, per-mille
budget shares, append-only content-addressed mailboxes, merge policy, bounded concurrency — validated
at construction for acyclicity and budget conservation.

**The key formal property.** If child budget shares are per-mille of the parent and attenuation
rounds *down*, then `Σ children ≤ parent` holds as arithmetic rather than as policy. Combined with
`CHILD_STRUCTURAL_CEILINGS` (depth and turns are not summed across siblings — the `F-10` distinction
already encoded in `budget.py`), conservation becomes checkable once, at plan construction, and the
scheduler requires no error handling for it.

**Scope discipline.** Three topologies suffice initially: sequential planner→implementer→verifier
(the baseline), fan-out investigators→synthesiser, and implementer→bounded-reviewer. An unbounded
swarm should be *inexpressible in the type*, not merely discouraged. The correct sequencing is to
establish the sequential baseline and only then test whether parallelism improves cost or success
rate; parallelism that does not win on measured numbers should not ship.

**Falsified if:** measured fan-out shows no cost or success-rate advantage over sequential
execution, in which case the coordination plane is complexity without return.

### 8.4 Proposition 4 — Role eligibility as a typed constraint

**Claim.** The "small models do mechanical work, strong models do synthesis" principle should be
enforced by matching a role's declared `model_role` against a model profile's `eligible_roles`,
rather than left to routing configuration.

The mechanical roles are already identifiable in the codebase's own structure: file ranking (over
`IndexPort` output), context compression (`compaction.py`), failure classification (§8.2), log
summarisation, and test association ranking. Each is a bounded classification or ranking task where a
7B local model is adequate and a frontier model is waste. Synthesis, planning and complex
implementation remain frontier-reserved.

**Falsified if:** measurement shows cheap-model substitution degrades end-to-end success by more than
it saves — which is an empirical question that `pareto_measurement.py` exists precisely to answer.

### 8.5 Proposition 5 — Completion as subject-bound evidence

**Claim.** The admission gate should bind a verification receipt to *task* and *composition*, not only
to workspace. Part III §6.1 documents the present gap and the residual-evidence failure mode.

The formal statement: admission requires a receipt `r` and current state `(W, T, C)` such that
`r.workspace_digest = W ∧ r.task_digest = T ∧ r.composition_digest = C ∧ r.passed`. A receipt missing
a binding that is *requested* must be treated as unbound (rejected), never as satisfied — otherwise
the check is reintroduced as a no-op.

**Note this is a correction, not an extension.** The field exists; the check does not. Of everything
in Section 8, this is the item with the strongest claim to being a defect fix rather than a feature.

### 8.6 Proposition 6 — Durable recovery accounting

**Claim.** Retry counters and attempt fingerprints must serialise into the checkpoint alongside
ledger state. Presently `ProtocolRecoveryState` is loop-local, so a run that suspends for approval
and resumes reconstructs its retry budget fresh (Part III §6.3).

This is the same class of leak as the refund clamp `K-07` guards against: small, repeated, invisible,
and unbounded over a long enough session. The fix is mechanical — the state is already a frozen
dataclass; it needs `to_dict`/`from_dict` and a slot in the checkpoint payload — but its absence
means "resume" is not currently budget-faithful.

### 8.7 Proposition 7 — Shadow-mode metacognition with paired evaluation

**Claim.** A `MetaController` implementation should run first in shadow mode: logging directives and
comparing against the baseline arm through `paired_evaluation.py`, with no directive lowered into a
proposal.

The `guarded_consult` determinism check already enforces the precondition for this comparison — a
nondeterministic controller cannot serve as a paired arm. The remaining requirement is discipline:
the controller must accumulate measured lift before it is granted influence, and it must never
acquire the ability to raise budgets, widen scope, or relax completion criteria. The twelve-directive
closed vocabulary already prevents the latter by construction; the former is a process commitment.

### 8.8 Proposition 8 — Skill promotion as a governed pipeline

**Claim.** The `M-8` machinery (`skill_lifecycle.py`, `governance/learning.py`) should be exercised
only after a measured baseline exists, because a skill distilled from an unmeasured harness encodes
that harness's mistakes as procedure.

The safety properties are already correct: generator, evaluator and promoter are separate protocols;
promotion requires held-out lift, regression budgets and signed evidence; the registry is durable and
CAS-protected; and *an agent has no method to promote itself*. What is missing is not mechanism but
the evidential precondition for using it responsibly.

### 8.9 Proposition 9 — Hermetic baseline as a contribution invariant

**Claim.** A declared subset of the 2,486 tests — cassette models, fake sandbox, fake evaluator —
should be guaranteed green in a bare container and enforced in CI. All three fakes already exist.
This is the cheapest item in Section 8 and has the highest effect on contribution velocity, because
it converts "did I break something?" from a differential investigation into a boolean.

---

## 9. Concluding Assessment

### 9.1 What this codebase is

AETHER/Vanguard is not an agent orchestration library with safety features. It is a **capability-
secure execution substrate** onto which agents are projected as configurations. Its central
intellectual commitment — that authority must be structurally separated from capability, and that an
agent's outputs are inert proposals until an independent kernel admits them — is implemented
consistently from `ports/` through `kernel/dispatch.py` to the manifests, and is verifiable rather
than asserted.

Three properties distinguish it from the state of practice. First, **the failure history is encoded
in the source**: ordering constraints carry the defect that motivated them, and must-fail tests are
constructed so that regressions are unrepresentable rather than merely detected. Second, **the system
has a first-class representation for not knowing** — `undeterminable` child outcomes, unverified
containment reports, `EffectStarted` durably written before dispatch so a crash yields
indeterminacy rather than invisibility, and `Result[T]` throughout the ports. Third, **evidence is
architecturally separated from the thing it judges**: `agency` cannot import an evaluator, evaluators
run sealed and signed, and completion requires a receipt rather than an assertion.

### 9.2 Where the risk actually lies

Not in the trusted computing base. The kernel, ports and domain layers are 12,935 LOC of unusually
disciplined code with enforced dependency inversion and closed failure enumerations.

The risk is concentrated in the 24,688-LOC runtime: `session.py` at 1,461 LOC carrying eight
responsibilities; five modules occupying adjacent scheduling territory without clear demarcation;
`chimera/patcher.py` reimplementing a strategy cascade that exists canonically elsewhere, in the one
place where divergent semantics corrupt benchmark attribution; and 38 manifests with no
canonical/experimental distinction. None of these threatens the safety argument. All of them threaten
comprehensibility, and in a system whose safety argument is compositional, comprehensibility is a
safety property at one remove.

### 9.3 The single most important open item

Of everything identified, the unread `task_digest` in `AdmissionGate` (Part III §6.1) is the item I
would escalate first. It is small, it is a correction rather than a feature, and it sits at the exact
point where the framework's central claim — that evidence rather than assertion determines completion
— is enforced. A completion gate that binds freshness but not subject admits residual evidence, and
in a benchmark harness running sequential tasks over one workspace, residual evidence is the common
case rather than the edge case.

### 9.4 The generalisation claim, assessed

The brief asks whether Aether can become a meta-framework for general task solvers. The evidence in
`main` is that it substantially already is one, and the proof is not architectural argument but
artefact comparison: three agent types sharing a loop, a kernel, a context policy, a routing policy
and a budget policy, differing only in prompt, perimeter and oracle; and a second, non-code domain
(`tableworld`) running on the same substrate.

The generalisation is therefore not a future refactor to be undertaken. It is a property to be
*preserved* — and the principal threat to it is the ordinary pressure to solve the next agent type by
writing a subsystem instead of authoring a manifest. The 79-line `apps/` layer is the metric to
watch. If it grows substantially, the substrate has begun to fail.
