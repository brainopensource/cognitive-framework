# AETHER / Vanguard — Technical Report, Part I
## Theoretical Foundations, Architectural Stratification, and the Authority Calculus

**Subject:** `github.com/brainopensource/cognitive-framework`, `main`, backend only
**Method:** direct source reading of 260 Python modules / 57,450 LOC under `vanguard/packages/`
**Constraint:** this document describes **only what is presently implemented**. Speculative
extensions are confined to Part IV and are marked as such throughout.

---

## 1. Theoretical Foundations & State of the Art

### 1.1 The central thesis of the codebase

Most agent frameworks in current practice are *orchestration libraries*: they sequence LLM calls,
parse tool invocations, and maintain a transcript. Their safety properties, where they exist at all,
are emergent — a function of prompt discipline and adapter hygiene rather than of structure. The
consequence is well known and widely observed: capability and authority are conflated, so the only
lever available for restricting what an agent may do is restricting what it may *say*, which is a
lever that does not hold.

AETHER/Vanguard proceeds from the opposite premise, and the premise is stated explicitly in the
source rather than left to inference. The `kernel` package docstring declares itself "The Trusted
Computing Base," and asserts: *"Every effect passes through `Kernel.dispatch` and there is no second
path."* The architectural claim is that an agent is not a *program* that acts, but a *proposal
generator* whose outputs are inert until an independent authority admits them. The model is
structurally untrusted; this is not a policy applied to the model, it is a property of where the
model sits in the dependency graph.

This yields a system whose safety argument is compositional rather than statistical. One does not
argue "the model rarely does X"; one argues "there exists no code path by which X reaches an
adapter." The distinction matters enormously for the class of failures that dominate agentic systems
in deployment — prompt injection, capability escalation via tool output, silent budget exhaustion,
and false completion — because each of these is a *structural* failure that no amount of prompt
engineering repairs.

### 1.2 The five-layer stratification and its enforced direction

The backend decomposes into six packages under `vanguard/packages/`, with a strictly inward
dependency direction. Measured LOC (excluding files added in the separate Forge review):

| Layer | LOC | Role | May import |
|---|---|---|---|
| `ports` | 1,580 | Interface definitions (Protocols) only | `domain` only (leaf) |
| `kernel` | 1,769 | Trusted Computing Base | `domain`, `ports` |
| `domain` | 9,586 | Pure values, canonicalisation, ledger algebra | nothing outward |
| `agency` | 8,844 | The episode loop, context compilation, Forge/Chimera | `domain`, `kernel`, `ports` |
| `runtime` | 24,688 | Composition, session, persistence, governance | all inner layers |
| `adapters` | 10,927 | Concrete I/O: models, environment, sandbox, stores | ports + domain |
| `apps` | 79 | Façades only | `runtime` |

I verified the direction empirically rather than trusting the documentation: `grep` for imports of
`runtime`, `agency`, or `adapters` from within `kernel/` returns **zero matches**. `ports/` imports
nothing outward at all — the `child_runtime.py` docstring states the invariant directly: *"This
module imports nothing from `runtime/` or `kernel/` — Ports stays a leaf."* The dependency inversion
is real and load-bearing, not aspirational.

The `apps` layer measuring 79 LOC is itself a significant architectural datum. `CodingMaxFacade` is a
preset selector and a delegator to `ApplicationService`; it implements no loop of its own. The
smallness is deliberate and is the visible evidence that "Coding Max" is a *composition*, not a
subsystem. Any agent type in this framework that required a large app layer would, by that fact
alone, be revealing that the substrate had failed to generalise.

### 1.3 The authority calculus: trust, spans, and the widening predicate

The most theoretically interesting content in the codebase is the authority model in
`kernel/provenance.py`, `kernel/policy.py`, and `kernel/classifier.py`. It implements a formal
predicate over an accumulating set of provenance-labelled spans, and it is worth stating precisely
because it is the mechanism by which prompt injection is structurally defeated rather than
heuristically filtered.

The governing sentence, from `provenance.py`:

> *Untrusted content may inform work; it may never authorise it.*

Formally, let `S_n` be the set of justifying spans at turn `n`, each span carrying a `Trust` label
drawn from a partially ordered set with `OPERATOR` strongest and `UNTRUSTED_DERIVED` among the
weakest. Let `W(r)` be a boolean classification of whether request `r` *widens capability* — that is,
whether it would grant an effect the principal does not already hold, or escalate outside the
declared perimeter. Then the authority violation predicate is:

```
violated(r, S_n)  ≡  W(r) ∧ ∃s ∈ S_n : untrusted(s)
```

Three properties of this formulation deserve comment, because each corresponds to a defect the
codebase records as having actually shipped.

**Property 1 — the conjunction is essential.** `authority_violation()` documents this precisely:
untrusted spans alone are acceptable (that is untrusted content *informing* work), and widening alone
is acceptable (that is an ordinary privileged request). Only the conjunction is a violation. A system
that denied on either operand alone would be unusable: the first would forbid reading any file, the
second would forbid any write.

**Property 2 — monotone accumulation.** `Accumulation` is a class rather than a list precisely so
that reset is inexpressible. Its only public mutation is `extend()`, a union. The docstring records
why: the span operand was once reset between turns, *"which makes the untrusted branch unreachable
dead code (`MF-KRN-002`)."* This is a subtle and instructive failure. If `S_n` is reset each turn,
then tool output that entered at turn `n` and steers a tool call at turn `n+1` carries no untrusted
label at the moment of authorisation — the defence exists in source and is unreachable in execution.
The union rule is stated as `S_n = S_{n-1} ∪ reply(n-1) ∪ results(n-1)`, implemented in
`advance_turn()`. Trust labels are additionally monotone downward under re-observation: `combine()`
returns the *weakest* input, and on re-entry of a known span the recorded label *"can only get
weaker, never stronger."*

**Property 3 — the widening operand must be computed, not assumed.** `classifier.py` records the
counterpart failure: the prototype hardcoded `W(r) = true` for every subprocess call. The authority
predicate therefore *appeared* to fail closed on all tool use, and — this is the remarkable part —
*"three design documents recorded the resulting deadlock as a property of the taint model."* A
constant standing in for an absent classifier had been reified into theory. This is why the dispatch
sequence makes S4 a classifier *call* per request, and why the must-fail test `MF-KRN-001` is
constructed so that no single boolean can satisfy both a within-authority and an escalation
scenario simultaneously.

The `child_return()` method closes the recursion: a child operator's return value re-enters the
parent's accumulation as untrusted-derived *at minimum*, "whatever the child believed about it."
Delegation therefore cannot launder trust, which is the obvious attack against any hierarchical agent
system.

### 1.4 Attenuation as a lattice operation with no silent meet

`kernel/attenuation.py` implements the child-grant relation. A child grant is valid only when its
actions are a subset, its resources are a subset, and its constraints never increase along any of:
`expires_at`, `max_uses`, `budget_usd_micros`, `max_bytes`, `max_effects`, `risk_ceiling`,
`max_depth`, `network_policy`.

The design decision worth extracting is rule `K-26`: **there is no silent intersection.** An
over-broad request is denied *whole*, recording both what was requested and what was grantable, and
the denial is marked `alertable`. The stated rationale is a genuine security insight rather than a
purism: *"A child repeatedly asking for authority beyond its parent is the strongest intrusion signal
this shape of system produces, and narrowing it quietly discards that signal while looking more
helpful."* A framework that silently computes the meet of requested and grantable scope is optimising
for apparent smoothness at the cost of destroying its own best detector.

`narrower_than()` returns `(bool, str)` rather than `bool` — the dimension that widened is returned
because *"a denial has to name a cause."* This recurs throughout the codebase as a pattern: refusals
carry structured explanations, because an unexplainable denial cannot be debugged, audited, or fed
back to a recovery policy.

Resource inclusion (`K-48`) is delegated to `domain/selectors/resource_selector.decide()` and is
explicitly total on defined pairs, denying *every* undefined pair including cross-kind comparisons. A
checker returning "unknown" fails closed. This is the correct disposition for a subset relation over
an open universe of resource kinds.

### 1.5 Sink classification and the registration-time refusal

`SinkRegistry` maps action → `SinkClass` ∈ {`PURE`, `OBSERVATION`, `PRIVILEGED`}. The interesting
mechanism is that the registry *refuses the registration*, not the call:

```python
PRIVILEGED_PREFIXES = ("fs.write", "fs.delete", "net.", "exec.", "proc.", "secret.")
OBSERVATION_PREFIXES = ("fs.read", "fs.stat", "fs.list", "git.read")
```

If an action whose namespace is privileged by construction is registered as `pure`, `SinkMismatch` is
raised at registration. The rationale (`MF-KRN-008`) is that *"a privileged sink declared `pure` skips
the descriptor-bound grant entirely"* — so the defect is intercepted before it can reach dispatch.
This is a shift-left of a security check from run time to configuration time, and it is the right
one: a misclassification is a static property of the registration, so detecting it dynamically is
strictly worse.

---

## 2. Dialectical Analysis of Underlying Mechanisms

### 2.1 The dispatch sequence as an ordering proof

`kernel/dispatch.py` is 458 LOC implementing a thirteen-step sequence. What elevates it above
ordinary middleware is that **each ordering constraint is annotated with the defect that motivated
it.** The sequence:

```
S0  ENTER      EffectRequest
S1  PARSE      validate against the contract schema
S2  RESOLVE    action -> adapter                        <-- BEFORE any lease
S3  DESCRIBE   descriptor = digest(canonical(name, normalisedArgs))
S4  CLASSIFY   widensCapability := classifier(request)  <-- not a constant
S5  AUTHORIZE  decision := policy.authorize(...)
S6  GRANT      grant := issue(descriptor, principal, resources, ttl)
S7  RESERVE    lease := governor.reserve(runId, resources, parentLease)
+-- try ------------------------------------------------------------+
| S8   VERIFY  the grant binds THIS descriptor and is unexpired      |
| S8a  INTENT  durably append EffectStarted and FSYNC   <-- BEFORE   |
| S9   DISPATCH adapter.execute(...)                                 |
| S10  COMMIT  governor.commit(lease, actual)                        |
+-- finally --------------------------------------------------------+
S11 RELEASE    governor.release(lease)                  <-- every path
S12 EMIT       outcome events                           <-- after release
```

The justifications are the substance:

- **`K-04`** — S2 precedes S7 so an unknown action cannot strand a lease. Resolution failure must not
  consume budget.
- **`K-05`** — S8 sits *inside* the guarded block and *after* S7, so the grant is verified at the
  point of effect. A resumed run or a mutated request cannot ride an earlier grant. This is
  time-of-check/time-of-use discipline applied to capability tokens.
- **`K-06`** — S11 precedes S12: *"If the emit raises, the lease is already back; a leaked lease is
  worse than a lost event."* An explicit, defensible ranking of two failure modes.
- **`K-47`** — S8a durably appends `EffectStarted` and fsyncs **before** S9, so a crash between
  dispatch and emit leaves the effect *undeterminable* rather than *invisible*. This is the crucial
  epistemic move: the system prefers recording "we do not know whether this happened" over silently
  recording nothing, because the latter is indistinguishable from "it did not happen."

`FailurePath` is a closed enumeration of every exit, and `DispatchResult.failure` always names one; an
exit not in the table is a defect asserted against directly by `test/kernel/test_dispatch.py`. The
type system is doing genuine work: there is one return type from the one path.

### 2.2 The governor: conservation with retained overrun

`kernel/budget.py` implements lease-based budget accounting over four additive dimensions:

```python
ADDITIVE_DIMENSIONS = frozenset({"usd_micros", "millis", "tokens", "bytes"})
```

The module holds *no policy opinion*: it denies only on dimension exhaustion or a closed parent
lease, never on effect class. This separation (policy decides, governor accounts, adapter executes)
is stated as single-responsibility but has a concrete payoff — the governor can be reasoned about as
pure arithmetic.

The rule with real teeth is `K-07`: commit debits reality *including overruns*, and the refund is
`reserved − actual` **retained when negative**. The docstring explains the failure mode with unusual
clarity: *"Clamping the refund at zero means an overrun is never debited and the ceiling never moves
— a run can then exceed its budget indefinitely, one small overrun at a time."* This is a slow-leak
class of bug that would be nearly invisible in testing and catastrophic in a long autonomous run.
`MF-KRN-007` is a must-fail test aimed precisely at the clamp.

Money is integer micro-units, durations integer milliseconds; the module contains no float. The
conservation invariant asserted by the must-fail suite is that for every dimension, `spent +
remaining` equals the ceiling *at all times, including after an overrun*.

Critically, `depth` and `turns` are excluded from `ADDITIVE_DIMENSIONS` by explicit comment: they are
*structural ceilings* enforced by attenuation (`Constraints.max_depth`) and by the episode loop
(`task.max_turns`) respectively, and *"summing either across siblings is the `F-10` defect."* This is
a genuinely subtle distinction — depth is not a resource that siblings consume from a shared pool,
and treating it as one produces incorrect denial behaviour under fan-out.

### 2.3 The episode loop: reduction to a terminal state

`agency/episode/engine.py` (1,058 LOC) implements the inner loop. Its docstring establishes the
division of labour with precision: *"Emission is split"* — the loop appends `ProposalProduced` itself
because proposal production happens outside the dispatch sequence, while grants, denials, budget
events, intent and receipts are appended by the kernel. The loop *"never writes a durable intent of
its own."*

Equally important: *"No evaluator is invoked. An episode terminates; it does not grade itself."*
`agency` cannot import an evaluator. The run-termination axis carries no evaluation verdict. This is
the separation that makes benchmark results meaningful — an agent that grades its own work has no
information content in its verdict.

The loop signature reveals the state that must survive:

```python
def run(self, *, episode_id, run_id, principal, brief="", spans=(), depth=1,
        is_cancelled=None, receipt_labeller=None,
        prior_turns=(), prior_seen_verbs=()) -> EpisodeOutcome
```

`prior_turns` and `prior_seen_verbs` exist because *"a run that suspends for approval re-enters
through a **new** engine,"* and without them *"the episode's whole memory of what it had already done
was discarded on every approval round-trip: turn indices restarted at 0, and no-progress detection
could never accumulate the consecutive history it needs."* The bound remains a bound on the episode
rather than on each segment.

`receipt_labeller` is injected rather than written inline because *"a span's trust is set by its
source class at construction and never by a judgement made at a call site"* (`K-30`, `K-31`). This is
the same principle as sink registration: classification belongs at the point of origin, where it is a
fact, not at the point of use, where it is an opinion.

### 2.4 Livelock detection as a property of sequences

`Episode.repeats(turn, limit)` implements no-progress detection over a `Turn.signature()` of
`(state_digest, proposal_descriptor, progress_signal)`. The engine tracks `repeat_count` across turns
with the comment: *"a livelock is a property of the **sequence** of proposals, not of any one of
them."*

This is the correct formulation and it is worth dwelling on. An individual proposal is never
detectably a loop. Loop detection requires comparing a proposal *against the state it was produced
from* — `Proposal.descriptor` digests `{kind, action, resource, args}`, and `Turn` pairs it with
`state_digest`. A repeated (proposal, state) pair is definitionally non-progress: the agent is
proposing the same thing about the same world.

### 2.5 The tool-policy phase ladder: capability gating by workflow position

`agency/episode/tool_policy.py` implements what the brief refers to as "blocking write functions in
the planner." The mechanism is a monotone phase ladder:

```python
_VERIFY_TRIGGERS = frozenset({"patch.apply"})
_EDIT_TRIGGERS   = frozenset({"fs.read", "fs.search"})

def derive_phase(seen_verbs) -> str:
    if seen & _VERIFY_TRIGGERS: return "verify"
    if seen & _EDIT_TRIGGERS:   return "edit"
    return "inspect"
```

with allowed tool sets per phase:

| Phase | Allowed | Mode |
|---|---|---|
| `inspect` | `fs.read`, `fs.search` | required |
| `edit` | `fs.read`, `fs.search`, `patch.apply` | required |
| `verify` | `proc.exec`, `fs.read`, `patch.apply` | required |
| (`verification_passed`) | unrestricted | auto |
| (`research`/`explain` preset) | unrestricted | auto |

An agent therefore *cannot* propose `patch.apply` before it has read something. This is capability
gating derived from observed workflow position rather than from model self-report, and two details
show hard-won experience.

First: *"Phase advances only from **attempted** effects, never from model prose."* A model saying "I
have now examined the code" advances nothing. Second: *"A denied dispatch still advances the phase:
it proves the workflow moved past the earlier phase, and verify-phase allowances must stay reachable
after a patch attempt regardless of its outcome."* The engine comment records the failure this
repaired — because `patch.apply` suspends for approval, the turn immediately after a patch previously
lost the patch tool and failed as an undeclared-tool error. The ladder must survive the engine being
rebuilt around a suspension, which is why `prior_seen_verbs` crosses the boundary.

The module also enforces `ADR-0060`: *"the episode loop [must] name no domain verb."* The verb
constants live in the policy module, not the engine. The engine is domain-blind; which verbs advance
which phase is preset policy. This is what allows Research, Tutor and Coding to share one loop.

### 2.6 The layered context model and cache-boundary honesty

`agency/context/layers.py` defines a five-layer prompt structure with an explicitly stated render
order:

| Layer | Content | Volatility | Role |
|---|---|---|---|
| `L1 SYSTEM` | role + output contract | stable across run | system |
| `L2 TOOLS` | tool schemas | stable; rides request | system |
| `L3 ENVIRONMENT` | conventions, retrieved priors | stable within task | system |
| `L4 TASK` | brief and notes | stable within task | user |
| `L5 DIALOGUE` | turns, results, notes | **mutates every turn** | user |

`PREFIX_LAYERS = (SYSTEM, TOOLS, ENVIRONMENT)` is *"byte-for-byte stable across every turn of a run,
or the provider charges full price for a prompt it has already seen"* — prompt caching treated as an
economic invariant with a structural guarantee.

`BREAKPOINT_LAYERS = (SYSTEM, ENVIRONMENT, TASK)` excludes `L5` with a comment that is the most
epistemically precise line in the module: `L5` *"is the only layer permitted to mutate, and marking
it stable is a lie to the provider about what is stable."* The framing of a cache breakpoint as a
*truth claim made to a counterparty* rather than as an optimisation hint is exactly right, and it is
the sort of thing that only gets written after a caching bug has cost real money.

`LAYER_ORDER` is stated explicitly rather than derived from enum iteration, because iteration *"would
work today and break the moment someone inserts a member."*

### 2.7 The metacognition seam and its determinism obligation

`ports/meta_controller.py` defines metacognition as a **pure policy plugin**: *"It cannot emit,
access stores, call a model, or bypass ordinary proposal and kernel authorization paths."* The
signature is value-in, value-out:

```python
def assess(self, view: AgentView, progress: ProgressView,
           confidence: Sequence[ConfidenceRecord]) -> StrategyDirective | None
```

Directives are drawn from a closed set of twelve: `revise_plan`, `request_context`,
`abandon_hypothesis`, `change_verification`, `delegate`, `conclude`, `accept`, `reject`, `retry`,
`redirect`, `fork`, `stop`. Note what is absent — there is no directive to raise a budget, widen a
scope, or relax completion. The metacognitive layer can change *strategy*; it cannot change
*authority*. A returned directive must be lowered into an ordinary proposal traversing the normal
kernel path.

`runtime/meta_controller.py` supplies `guarded_consult()`, which adds a falsifier that is unusual and
important:

```python
directive = controller.assess(view, progress, records)
for _ in range(max(0, determinism_samples - 1)):
    again = controller.assess(view, progress, records)
    if again != directive:
        raise ControllerOutputError(
            "controller returned different directives for identical inputs; "
            "paired runs cannot be compared against a nondeterministic arm")
```

The controller is invoked twice on identical inputs and the results compared. The justification is
methodological rather than operational: a nondeterministic controller cannot serve as an arm in a
paired comparison, so evidence produced against one is not evidence. This is a measurement-integrity
constraint enforced at runtime — the system refuses to generate results it would not be entitled to
believe.

### 2.8 The child-runtime contract: delegation without inlining

`ports/child_runtime.py` encodes three refusals structurally:

1. **A plan is decided before the child exists.** Every field of `ChildRunPlan` is already
   attenuated, lowered and reserved. *"There is no negotiation from inside the child, because the
   plan is frozen and the child never receives the parent's scope object to widen."*
2. **A result is a contract, not a conversation.** `ChildRunResult` admits scalars, digests and
   reference strings only; `__post_init__` rejects anything else, *"so a runner cannot hand back a
   live session, an open port, or a transcript — a parent that receives a transcript has not
   delegated, it has inlined."*
3. **Absence is not a value.** A runner that cannot determine what happened returns
   `outcome="undeterminable"`, *"never a cheerful default. The synthetic success this port replaced is
   precisely what made M-6 unacceptable."*

The third is the same epistemic commitment visible in `K-47`: the system has a first-class
representation for *not knowing*, and refuses to collapse it into either success or failure. In
autonomous multi-agent systems this is the difference between a measurable framework and a
plausible-looking one.

### 2.9 Checkpointing as memoised fold, with proof obligations

`runtime/checkpoints.py` treats a checkpoint not as a snapshot but as *"a memo of `reduce_batch`
under a particular reducer over a particular event vocabulary."* Hence `CheckpointPins`:

```python
reducer_version: str
event_schema_version: str
checkpoint_schema_version: str
```

*"Not metadata. ... reusing it under different rules answers a question nobody asked."* A checkpoint
is only valid relative to the fold that produced it, and the pins make that relativity explicit and
checkable.

`Checkpoint` itself carries digests and identities only; the state lives in the blob store, *"which is
the whole point: an append-only ledger is no place for a snapshot that will be superseded on the next
turn."* The separation between the immutable event log and the mutable derived cache is clean.

The error discipline is also notable: `CheckpointValidationError` is raised only by `load()`, which
callers use when they want the reason; `reconstruct()` never propagates it and instead falls back to
a cold fold, *"because a bad cache is not an execution failure."* Degradation is graceful and the
correctness floor is the event log.

---

*Part II covers the runtime layer, agent typologies, feature mechanics (pause/cancel/resume,
sandboxing, memory, skills), and the full module tree. Part III covers code health, anomalies and
frontier gaps. Part IV covers the Aether meta-framework thesis and the evolution path.*
