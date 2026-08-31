# AETHER FORGE — Full Code Manifest — Wave 1

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; no frontend changes.
- Focus: Strong Stop Gate, reflex controller, failure/progress detection, FORGE compaction, context admission, and ToolScript MVP.
- Architectural rule: specialize existing Vanguard seams; do not fork the kernel.
- Status: implementation manifest; code blocks are the exact classes, functions, schemas, and manifests to add or replace.

## Code-first reconciliation

The inspected branch already contains `AdmissionGate`, workspace-bound `VerificationReceipt`, `MetaController`, guarded deterministic consultation, ledger-derived progress, structured compaction, model routing, attenuated child execution, durable events, and artifact capture. FORGE must compose these mechanisms. Any passage below that appears to create a second engine is interpreted as an exterior FORGE policy, adapter, preset, or runtime lowering layer. No new code belongs in `vanguard/packages/kernel/`.

## Authoritative file routing

| Concern | Existing owner | FORGE change surface |
|---|---|---|
| Completion admission | `agency/episode/admission_gate.py` | compose `GoalContract`; preserve base gate |
| Reflex decisions | `ports/meta_controller.py`, `runtime/meta_controller.py` | deterministic rules and state builder |
| Context | `agency/context/` | `forge-distill` strategy; preserve evidence |
| Tools | existing effect dispatch | declarative ToolScript port and lowering |
| Forks | `EpisodeEngine.spawn`, child runtime | budget-attenuated branch policy |
| Verification | receipts/evaluator gateway | current-workspace binding and goal evidence |
| Models | adapter routing policy | bounded escalation policy |
| Memory | artifact/experience seams | evidence-gated strategy capsules |

## Implementation specification and complete changed units


# 81. Implementation Phase 2 — Strong Stop Gate

Wire `ForgeAdmissionGate` into the product path.

Required behavior:

```text
model proposes completion
        │
        ▼
existing AdmissionGate
        │
        ▼
GoalContract evaluation
        │
   ┌────┴─────┐
   ▼          ▼
reject      accept
   │          │
   ▼          ▼
next turn    complete
```

Implement only enough new code to express the missing task contract.

Do not replace existing verification semantics.

### Required implementation tasks

```text
FORGE-ADM-001 define GoalContract
FORGE-ADM-002 implement ForgeAdmissionGate composition
FORGE-ADM-003 wire completion rejection into model-visible context
FORGE-ADM-004 ensure verification receipt binds to current workspace digest
FORGE-ADM-005 add targeted integration test
```

### Example integration test

```python
def test_forge_rejects_finish_after_unverified_patch(...):
    # arrange
    session = forge_session(...)
    apply_patch(...)

    # model attempts completion without fresh test receipt
    verdict = session.try_complete(...)

    assert verdict.accepted is False
    assert verdict.code == "FORGE_GOAL_UNSATISFIED"
    assert "verification" in verdict.detail
```

---

# 82. Implementation Phase 3 — Reflex Controller

Implement `ForgeMetaController` as a pure controller over existing projections.

The first version should detect:

```text
no progress
repeated equivalent failure
premature finish
stale verification
high uncertainty
competing hypotheses
context pressure
```

Do not perform effects directly.

### Suggested method structure

```python
class ForgeMetaController(MetaController):
    def assess(self, view, progress, confidence):
        state = ForgeReflexState.from_views(
            view=view,
            progress=progress,
            confidence=confidence,
        )
        return self._policy.decide(state)
```

```python
class ForgeReflexPolicy:
    def decide(self, state: ForgeReflexState):
        for rule in self._rules:
            directive = rule.evaluate(state)
            if directive is not None:
                return directive
        return None
```

Start deterministic.

Do not add an LLM call to the controller in v0.1.

---

# 83. Reflex Rule Contract

Use small independent rules.

```python
class ReflexRule(Protocol):
    id: str

    def evaluate(
        self,
        state: ForgeReflexState,
    ) -> StrategyDirective | None:
        ...
```

Examples:

```text
RepeatedFailureRule
StaleVerificationRule
NoProgressRule
ForkOpportunityRule
ContextPressureRule
PrematureStopRule
```

Advantages:

- simple unit tests;
- independent toggling;
- easier ablation;
- no monolithic policy class;
- reusable outside FORGE if later proven universal.

---

# 84. Repeated Failure Detection

Never compare only error strings.

Prefer normalized fingerprints:

```python
FailureFingerprint(
    tool_kind,
    exit_code,
    failing_tests,
    exception_type,
    top_stack_frames,
    workspace_digest,
)
```

Example:

```python
def equivalent_failure(a, b):
    return (
        a.tool_kind == b.tool_kind
        and a.exit_code == b.exit_code
        and a.failing_tests == b.failing_tests
        and a.exception_type == b.exception_type
    )
```

A repeated failure should trigger:

```text
same strategy retry prohibited
→ redirect
→ request different evidence
→ fork if useful
```

---

# 85. No-Progress Detection

Define progress using repository/environment facts rather than prose length.

Possible progress signals:

```text
new relevant file discovered
new symbol relationship discovered
new test executed
failure class changed
workspace digest changed
new verification evidence
hypothesis rejected
branch completed
task requirement satisfied
```

No-progress state:

```python
@dataclass(frozen=True)
class ProgressView:
    turns_since_progress: int
    new_evidence_count: int
    repeated_effect_count: int
    repeated_failure_count: int
    changed_workspace: bool
    changed_verification_state: bool
```

Avoid metrics such as:

```text
assistant generated many tokens
assistant wrote a long explanation
```

Those are not progress.

---

# 86. Implementation Phase 4 — Forge Compaction

Implement `forge-distill`.

Input:

```text
constitutional floor
task brief
current notes
dialogue/tool outcomes
ledger-derived state
```

Output must preserve:

```text
goal
current hypothesis
known facts
rejected hypotheses
file map
patch state
test state
branch summaries
open blockers
next action
artifact refs
```

### Compaction invariant

After compaction, an agent must still be able to answer:

```text
What am I trying to do?
What is currently believed?
What has been disproven?
What changed in the repo?
What tests have actually run?
What remains broken?
What should I do next?
Where is the raw evidence?
```

---

# 87. Context Admission Strategy

FORGE should differentiate tool results by information density.

Recommended categories:

```text
INLINE
SUMMARY
ARTIFACT_ONLY
```

Contract:

```python
@dataclass(frozen=True)
class ContextAdmissionDecision:
    mode: Literal["inline", "summary", "artifact_only"]
    summary: str | None
    artifact_ref: str | None
    priority: int
```

Examples:

```text
git status
→ INLINE

pytest 20,000-line output
→ SUMMARY + artifact ref

large generated dependency graph
→ ARTIFACT_ONLY + compact metadata

branch transcript
→ artifact only; BranchSummary inline
```

---

# 88. Context Admission Policy

```python
class ForgeContextAdmissionPolicy:
    def decide(self, result: ToolResult) -> ContextAdmissionDecision:
        if result.size <= SMALL_RESULT_BYTES:
            return inline(result)

        if result.has_structured_summary:
            return summary(result.summary, result.artifact_ref)

        return artifact_only(result.artifact_ref)
```

This should be integrated through existing context compilation/admission seams.

Do not create a second context store.

---

# 89. Implementation Phase 5 — ToolScript MVP

Implement ToolScript only after the ordinary reactive FORGE loop works.

### MVP restrictions

```text
Python only
no network
no package install
no arbitrary imports except safe stdlib subset
bounded runtime
bounded memory
bounded stdout
bounded tool calls
RPC-only privileged effects
```

### Initial safe standard library

Potentially:

```text
json
re
collections
itertools
functools
statistics
math
pathlib PurePath only
```

Do not expose unrestricted:

```text
subprocess
socket
os.system
ctypes
multiprocessing
```

The exact sandbox model depends on existing runtime isolation.

---

# 90. ToolScript Lifecycle

```text
model creates source
       │
       ▼
source stored as artifact
       │
       ▼
ToolScriptRequest created
       │
       ▼
policy validates
       │
       ▼
sandbox executes
       │
       ▼
inner RPC tool requests
       │
       ▼
AETHER authorization/dispatch
       │
       ▼
receipts/artifacts
       │
       ▼
bounded stdout/result
       │
       ▼
model context
```

Every script must have:

```text
source digest
runtime limits
tool-call limit
allowed capability slice
parent effect id
run id
```

---

# 91. ToolScript Source Example — Repository Localization

```python
hits = search("token bucket")

ranked = []

for hit in hits[:50]:
    path = hit["path"]

    if "/tests/" in path:
        weight = 1
    else:
        weight = 3

    text = read(path, start=1, end=220)

    if "refill" in text.lower():
        weight += 5

    if "consume" in text.lower():
        weight += 5

    ranked.append((weight, path))

ranked.sort(reverse=True)

print({
    "candidates": [path for _, path in ranked[:8]]
})
```

This replaces several serial LLM turns with deterministic filtering.

---

# 92. ToolScript Source Example — Test Failure Compression

```python
result = run_tests(
    targets=["tests/cache", "tests/api/test_cache.py"],
    timeout=120,
)

failures = []

for failure in result["failures"]:
    failures.append({
        "test": failure["test"],
        "exception": failure["exception"],
        "message": failure["message"][:300],
        "top_frame": failure["frames"][0] if failure["frames"] else None,
    })

print({
    "passed": result["passed"],
    "failed": len(failures),
    "failures": failures[:10],
})
```

---

# 93. ToolScript Source Example — API Impact Search

```python
refs = symbol_references("Cache.get")

impacted = {}

for ref in refs:
    module = module_for(ref["path"])
    impacted.setdefault(module, 0)
    impacted[module] += 1

tests = related_tests("Cache.get")

print({
    "modules": sorted(
        impacted.items(),
        key=lambda x: x[1],
        reverse=True,
    ),
    "tests": tests[:20],
})
```

This becomes especially powerful when LDA is available.

---

# 94. ToolScript Policy Boundary

ToolScript may perform:

```text
read/search/query
bounded shell/test tools if explicitly granted
artifact operations through broker
```

ToolScript may not:

```text
change its own capability set
spawn agents unless explicitly granted and justified
modify policy
alter ledger
read secrets
use unregistered network destinations
change budget
write arbitrary host files
```

If the parent lacks a capability, the script cannot acquire it.

---

# 95. ToolScript Failure Semantics

Typed failures:

```python
class ToolScriptError(Exception): ...
class ToolScriptTimeout(ToolScriptError): ...
class ToolScriptBudgetExceeded(ToolScriptError): ...
class ToolScriptPolicyDenied(ToolScriptError): ...
class ToolScriptProtocolError(ToolScriptError): ...
class ToolScriptSandboxError(ToolScriptError): ...
```

Model-visible failure should be concise:

```text
ToolScript failed:
type=ToolScriptBudgetExceeded
tool_calls=32
limit=32
artifact=sha256:...
```

Do not inject stack dumps unless requested.

---

# 96. Implementation Phase 6 — Adaptive Forks

After ToolScript:

1. add `fork` lowering;
2. add `ForkPolicy`;
3. add branch-specific metadata;
4. reuse `agent.spawn`;
5. add `BranchSummary`;
6. add distillation;
7. add bounded branch admission to context.

No parallel writable fork until workspace isolation is proven.

---

# 97. Fork Modes

## `research`

```text
read-only
goal: answer question
returns: findings/evidence
```

## `counterexample`

```text
read-only
goal: attempt to falsify current hypothesis
returns: contradiction or support
```

## `verification`

```text
read-only or controlled execution
goal: independently inspect whether candidate solves task
returns: evidence
```

## `candidate_patch`

```text
isolated writable worktree
goal: produce alternative patch
returns: patch + verification
```

Start with `research`.

Add writable candidate patches later.

---

# 98. Branch Prompt Template

A branch should receive a narrow prompt:

```text
You are a bounded FORGE branch.

Objective:
{objective}

Scope:
{scope}

Do not solve unrelated parts of the task.

Return:
- findings
- evidence references
- files inspected
- hypothesis status
- dead ends
- recommended next action

Do not claim success without environment evidence.
```

Avoid copying the entire parent transcript.

Inject:

```text
task brief
relevant compact facts
branch objective
minimal repository context
```

---

# 99. Branch Budgeting

Branches inherit bounded resources.

Example:

```yaml
forks:
  max_active: 2
  max_total: 4
  research:
    max_turns: 6
    token_fraction: 0.15
  candidate_patch:
    max_turns: 12
    token_fraction: 0.30
```

Conserved budget remains authoritative.

No child may receive more than the parent's remaining transferable budget.

---

# 100. Branch Scheduling

Do not implement a complex scheduler initially.

Simple policy:

```python
for spec in fork_specs[:max_parallel]:
    spawn(spec)

wait_for_children()

distill_all()

resume_parent()
```

Parallel execution is optional.

Sequential forks are acceptable for v0.1 if they simplify correctness.

---

# 101. Branch Artifact Schema

Store:

```text
branch objective
parent run
child run
scope
model route
starting workspace digest
ending workspace digest
patch digest
verification receipt
distilled summary
raw trajectory refs
```

This enables later analysis without adding a new database.

---

# 102. Implementation Phase 7 — Strategy Capsules

Only after reactive loop + stop gate + ToolScript + fork work.

Initial capsule types:

```text
pure parser
ranking transform
context filter
ToolScript template
reflex hint provider
```

Do not allow arbitrary Python monkey-patching.

Suggested declaration:

```yaml
capsule:
  id: task-rust-diagnostics
  kind: transform
  source: artifact:sha256:...
  hooks:
    - after_tool
  applies_to:
    tool: proc.exec
    matcher: "cargo test|cargo check"
  expires: run
```

---

# 103. Capsule Execution Contract

```python
class CapsuleExecutor(Protocol):
    def execute(
        self,
        capsule: StrategyCapsule,
        event: ForgeEventView,
    ) -> CapsuleResult:
        ...
```

Result:

```python
@dataclass(frozen=True)
class CapsuleResult:
    notes: tuple[str, ...] = ()
    context_artifacts: tuple[str, ...] = ()
    directive_suggestions: tuple[str, ...] = ()
```

Capsules should initially be advisory/pure.

Effectful capsules require a later security review.


## Wave acceptance

This wave is accepted only after its focused unit/contract/falsifier tests pass, boundary and domain-blindness linters remain green, no kernel LOC is added, and every claimed completion is backed by a fresh verification receipt. Full-suite execution is intentionally deferred to final integration.
