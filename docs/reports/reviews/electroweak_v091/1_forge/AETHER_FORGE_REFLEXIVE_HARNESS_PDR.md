
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

---

# 104. Capsule Deduplication

Generated capsules may be nearly identical.

Use canonical source digest:

```text
capsule identity =
hash(
    normalized source
    + hook contract
    + capability declaration
)
```

This allows analysis such as:

```text
same procedural idea generated across 17 successful runs
```

That becomes evidence for promotion.

---

# 105. Promotion to Reusable Skills

Only promote if:

```text
repeatedly useful
generalizable
safe
deterministic enough
measurable benefit
clear capability boundary
```

Promotion process:

```text
capsule corpus
→ human/automated review
→ SkillCandidate
→ evaluation
→ PromotionEvidence
→ signed promotion
→ reusable skill
```

Keep this outside the normal coding run.

---

# 106. Implementation Phase 8 — Optional LDA Adapter

Do not integrate LDA before baseline native search works.

Define a narrow AETHER-facing tool contract.

Example:

```python
class RepoIntelligencePort(Protocol):
    def search(self, query: str, limit: int = 20): ...
    def symbol(self, name: str): ...
    def references(self, symbol_id: str): ...
    def related_tests(self, target: str): ...
```

LDA adapter implements it.

Native fallback implements the same high-level subset through existing search/tools where practical.

---

# 107. LDA Provider Selection

```python
def repo_intelligence_provider(state):
    if (
        state.repo_size > LARGE_REPO_THRESHOLD
        and lda.healthcheck()
    ):
        return lda

    return native
```

The model may also explicitly choose LDA when useful.

FORGE should not always pre-index everything.

---

# 108. LDA Cache Identity

Cache key must include at least:

```text
repository identity
HEAD/tree digest
provider version
query/operation
index version
```

Never trust an index from a different tree state.

For modified working trees:

```text
base index
+
working-tree delta
```

or fall back to direct tools for changed files.

---

# 109. LDA Provenance

Every LDA result should carry:

```python
RepoFact(
    value=...,
    source="lda",
    repo_digest=...,
    provider_version=...,
    evidence_refs=...,
)
```

The model can then distinguish:

```text
fresh direct read
vs
derived index fact
```

---

# 110. Model Route Policy

Keep model routing declarative.

Conceptual manifest:

```yaml
models:
  main: frontier
  fork_research: fast
  fork_candidate_patch: frontier
  compression: fast
```

Fallback:

```text
main model provider failure
→ same-role fallback

repeated reasoning failure
→ optional alternate main model

do not:
silently switch models every turn
```

The run must record model identity for each episode/branch.

---

# 111. Stronger-Model Escalation

Escalation is allowed when:

```text
same failure survives strategy change
branch evidence contradicts main hypothesis
task classified as highly complex
budget reserved for escalation
```

Pseudo:

```python
if (
    state.repeated_failure_count >= 2
    and state.alternate_strategy_attempted
    and budget.can_escalate()
):
    return directive(
        "fork",
        model_route="strong",
        brief="Reassess the failing hypothesis independently.",
    )
```

Prefer escalating a **fresh branch** over hot-swapping the main conversation.

This avoids anchoring and context contamination.

---

# 112. Verification Architecture

FORGE does not need a giant verifier agent.

Use real environment evidence first:

```text
syntax/build
targeted tests
related tests
task-specific checks
diff inspection
```

Optional model verification comes after deterministic evidence.

Priority:

```text
environment
> deterministic evaluator
> model review
> model self-confidence
```

---

# 113. Verification Receipt

Reuse the current receipt contract if available.

At minimum verify:

```text
task digest
workspace digest
check kind
command/tool
exit code
timestamp/event position
artifact refs
```

A receipt is stale if:

```text
workspace changed after receipt
```

Stop Gate must reject stale evidence.

---

# 114. Targeted Test Selection

Start simple.

Sources:

```text
tests mentioned in task
tests mapped by filename conventions
tests discovered by search
tests from LDA related_tests
tests from previous failure
tests selected by model
```

Do not build a sophisticated ML test selector initially.

---

# 115. Patch Discipline

FORGE prompt and admission should encourage:

```text
smallest sufficient patch
preserve repository conventions
avoid unrelated formatting churn
inspect diff before completion
```

But do not hard-code “small patch” as correctness.

Some tasks legitimately require structural changes.

Use patch size as a risk signal, not a success criterion.

---

# 116. Workspace Snapshot Discipline

Before writable work:

```text
capture base workspace/tree digest
```

After each meaningful patch:

```text
capture current workspace digest
```

Verification binds to current digest.

Branch candidate patch references both.

This enables:

```text
which exact code did this test receipt verify?
```

---

# 117. Resume Semantics

FORGE must use existing reconstruction.

On resume:

```text
ledger
→ projections
→ ForgeState reconstruction
→ artifacts
→ current workspace digest
→ compare expected/current state
→ continue
```

If workspace drifted externally:

```text
mark previous verification stale
require context refresh
```

Do not blindly resume old assumptions.

---

# 118. Forge Recovery on Crash

After restart:

```python
def restore_forge(run_id):
    run_state = projection.rebuild(run_id)
    forge = forge_projection.rebuild(run_id)

    assert artifacts.verify_references(forge.artifact_refs)

    current_workspace = workspace.digest()

    if current_workspace != forge.last_workspace_digest:
        forge = forge.invalidate_verification()

    return forge
```

---

# 119. FORGE CLI Preset

Desired user surface:

```bash
aether run \
  --agent vg-code-forge \
  --workspace /path/to/repo \
  --task "Fix ..."
```

Optional:

```bash
aether run \
  --agent vg-code-forge \
  --set forge.toolscript=true \
  --set forge.forks=adaptive \
  --set forge.lda=auto
```

Do not create a separate `forge` executable unless there is a compelling product reason.

---

# 120. FORGE Configuration

Conceptual:

```yaml
forge:
  stop_gate: true

  reflexes:
    repeated_failure: true
    no_progress: true
    stale_verification: true
    context_pressure: true

  toolscript:
    enabled: true
    max_runtime_ms: 30000
    max_tool_calls: 32
    max_stdout_bytes: 16384

  forks:
    mode: adaptive
    max_total: 4
    max_active: 2

  compaction:
    strategy: forge-distill

  capsules:
    enabled: experimental

  repository_intelligence:
    lda: auto
```

Map this to existing manifest schemas rather than introducing ad hoc YAML if AETHER uses JSON manifests.

---

# 121. Default Presets

## `forge-fast`

```text
stop gate
reactive loop
native tools
no ToolScript
no forks
cheap compaction
```

## `forge`

```text
stop gate
reactive loop
ToolScript
adaptive compaction
research forks
native/LDA auto
```

## `forge-max`

```text
stop gate
ToolScript
adaptive forks
candidate patch branches
trajectory distillation
optional stronger-model branch
capsules experimental
LDA auto
```

All must use the same underlying runtime.

---

# 122. Test Strategy

Testing must be sufficient to establish correctness without recreating a benchmark bureaucracy.

## Contract tests

```text
ForgeAdmissionGate
ForgeMetaController
ReflexRule
ToolScriptBroker
ForkSpec
BranchSummary
ForgeCompactionStrategy
TaskCapsuleRegistry
```

## Runtime integration tests

```text
finish rejected after unverified patch
finish accepted after fresh verification
fork child inherits attenuated authority
ToolScript inner call uses normal dispatch
ToolScript denied capability remains denied
branch summary enters parent context
compaction preserves verification evidence
resume invalidates stale receipt
```

## Real coding smoke tests

```text
one simple bug
one multi-file bug
one repeated-failure repair
one ambiguous task requiring branch
one ToolScript-heavy repository exploration
```

---

# 123. Falsifier Tests

Add explicit tests that try to break invariants.

### F-01 ToolScript authority expansion

```text
script requests tool unavailable to parent
→ DENIED
```

### F-02 ToolScript direct filesystem escape

```text
script attempts direct host path access
→ DENIED / unavailable
```

### F-03 Child budget inflation

```text
fork requests more budget than transferable
→ DENIED
```

### F-04 Premature success

```text
model says "all tests pass"
without receipt
→ completion rejected
```

### F-05 Stale receipt

```text
test passes
then patch changes workspace
then finish
→ completion rejected
```

### F-06 Capsule self-promotion

```text
task-local capsule requests permanent install
→ DENIED
```

### F-07 Writable branch collision

```text
two candidate branches attempt same authoritative workspace
→ prevented by isolation policy
```

---

# 124. Performance Budgets

FORGE should target lower model-turn overhead.

Useful engineering budgets:

```text
ToolScript startup < expensive model turn
branch summary << child transcript
compaction output bounded
no full repo indexing on simple task
no mandatory subagent
no mandatory reviewer
```

Initial profiling should measure:

```text
time to first useful repo read
time to first patch
model turns before first test
tool operations per model turn
context size over time
```

---

# 125. Observability

Use existing events/artifacts.

Add projections or CLI summaries only when cheap.

Useful run summary:

```text
FORGE RUN
---------
task: ...
model: ...
turns: 14
tool calls: 51
ToolScripts: 2
inner tool calls: 19
forks: 1
finish rejections: 1
patches: 3
verification: PASS
workspace digest: ...
cost: ...
```

Failure summary:

```text
dominant failure:
repeated test failure

strategy changes:
1

fork evidence:
branch-02 rejected cache hypothesis
```

---

# 126. Trajectory Viewer Requirements

The existing Lab/TUI should eventually be able to show:

```text
parent trajectory
├── branch A
├── branch B
└── ToolScript
    ├── tool 1
    ├── tool 2
    └── tool 3
```

But UI work is not a blocker for FORGE backend v0.1.

CLI/JSON evidence is enough initially.

---

# 127. Data Model — Minimal Additions

Prefer artifact/projection types over schema inflation.

Potential new domain-ish types should remain outside kernel unless universal:

```text
GoalContract
ForgeState
ForkSpec
BranchSummary
StrategyCapsule
ToolScriptRequest
ToolScriptResult
```

Only `ToolScriptRunner` may justify a stable port if the capability becomes reusable beyond FORGE.

---

# 128. Error Taxonomy

FORGE-specific runtime errors:

```text
FORGE_GOAL_UNSATISFIED
FORGE_REPEATED_FAILURE
FORGE_FORK_DENIED
FORGE_BRANCH_INCONCLUSIVE
FORGE_TOOL_SCRIPT_TIMEOUT
FORGE_TOOL_SCRIPT_POLICY_DENIED
FORGE_TOOL_SCRIPT_BUDGET_EXCEEDED
FORGE_CAPSULE_INVALID
FORGE_STALE_VERIFICATION
```

Prefer existing generic error classes where equivalent.

Do not create aliases for errors AETHER already models.

---

# 129. Coding Standards

All new Python should follow existing repository standards.

Default expectations:

```text
typed interfaces
frozen dataclasses where immutable
pure policy functions
dependency inversion
explicit error types
deterministic serialization
canonical digests
small modules
no hidden globals
no side effects in domain/policy code
```

Do not introduce a new framework dependency for simple constructs.

---

# 130. Module Boundary Rules

## `ports`

Contains:

```text
interfaces only
transport-neutral contracts
no process launch
no filesystem implementation
```

## `runtime`

Contains:

```text
composition
policy coordination
state transitions
projection-driven decisions
```

## `adapters`

Contains:

```text
subprocess
sandbox
filesystem
external LDA
provider-specific code
```

## `agency/manifests`

Contains:

```text
declarative FORGE composition
prompts
tool schemas
policies
```

## `kernel`

Should remain unchanged.

---

# 131. Edit Guide — Step-by-Step

A senior developer implementing this should follow:

```text
1. Checkout target branch and record exact HEAD.
2. Run focused existing runtime/agency tests.
3. Inspect local signatures before writing FORGE code.
4. Create vg-code-forge manifest using only existing capabilities.
5. Prove baseline execution.
6. Add ForgeAdmissionGate.
7. Add ForgeMetaController.
8. Add fork lowering to existing spawn seam.
9. Add ForgeCompactionStrategy.
10. Re-run focused tests.
11. Add ToolScript ports/runtime/adapter.
12. Add ToolScript falsifiers.
13. Add branch distillation.
14. Add optional LDA adapter.
15. Add StrategyCapsules only after core FORGE works.
16. Run real coding smoke tasks.
17. Compare against baseline harness.
18. Keep only mechanisms that materially improve capability.
```

---

# 132. Before Editing Any Existing Method

For each target:

```text
find all call sites
find tests
find protocol/interface
find manifests depending on behavior
find projection/event assumptions
```

Then write a one-line change reason.

Example:

```text
HarnessSession._lower_controller_directive
Reason:
lower existing `fork` directive into the already-supported `agent.spawn`
without creating a second branching mechanism.
```

This prevents accidental architectural duplication.

---

# 133. Required Code Review Questions

Every FORGE PR should answer:

```text
Did this bypass an existing AETHER abstraction?
Could this be a manifest/plugin/policy instead of runtime code?
Did this add authority?
Did this change budget conservation?
Did this duplicate event state?
Can it be disabled?
Can a simple task avoid paying its cost?
Can the run be reconstructed after crash?
Is success backed by environment evidence?
```

---

# 134. PR Decomposition

Recommended implementation PRs:

```text
PR-FORGE-01
native preset + goal contract + stop gate

PR-FORGE-02
reflex controller + fork lowering

PR-FORGE-03
forge compaction + artifact-backed admission

PR-FORGE-04
ToolScript port/runtime/sandbox

PR-FORGE-05
branch distillation + adaptive fork policy

PR-FORGE-06
candidate patch isolation

PR-FORGE-07
optional LDA adapter

PR-FORGE-08
strategy capsules

PR-FORGE-09
LAM experiment fixtures + comparative report
```

Each PR should remain independently reviewable.

---

# 135. Backlog — P0

## FORGE-P0-001 — Reconcile current seams

**Goal:** confirm exact local implementation.

**Inspect:**

```text
EpisodeEngine
HarnessSession
AdmissionGate
MetaController
SpawnAdapter
ContextCompiler
compaction registry
model routing
manifest schemas
```

**Exit:** one mapping document or commit note.

---

## FORGE-P0-002 — Create `vg-code-forge`

**Goal:** native preset with minimal reactive prompt.

**No new runtime code initially.**

**Exit:** manifest validates and executes through current runtime.

---

## FORGE-P0-003 — Stop Gate

**Goal:** prevent textual/self-reported success.

**Exit:** unverified write task cannot complete.

---

## FORGE-P0-004 — Reflex Controller

**Goal:** detect pathological loops.

**Exit:** repeated failure produces strategy directive.

---

## FORGE-P0-005 — Fork Lowering

**Goal:** use existing `agent.spawn`.

**Exit:** FORGE can create one bounded research child.

---

# 136. Backlog — P1

## FORGE-P1-001 — `forge-distill`

**Goal:** compact long coding trajectories.

**Exit:** objective/patch/test/dead-end state survives compaction.

---

## FORGE-P1-002 — Artifact-backed Tool Results

**Goal:** prevent context flooding.

**Exit:** large test output enters context as summary + artifact ref.

---

## FORGE-P1-003 — ToolScript Port

**Goal:** stable contract for mediated programmatic tool execution.

---

## FORGE-P1-004 — ToolScript Sandbox

**Goal:** execute bounded Python without authority bypass.

---

## FORGE-P1-005 — ToolScript Broker

**Goal:** inner tool calls use standard AETHER dispatch.

---

## FORGE-P1-006 — ToolScript Falsifiers

**Goal:** prove capability and sandbox boundaries.

---

# 137. Backlog — P2

## FORGE-P2-001 — BranchSummary

## FORGE-P2-002 — TrajectoryDistiller

## FORGE-P2-003 — Adaptive ForkPolicy

## FORGE-P2-004 — BranchSelector

## FORGE-P2-005 — Candidate Patch Worktree Isolation

## FORGE-P2-006 — Alternate Model Route for Forks

---

# 138. Backlog — P3

## FORGE-P3-001 — LDA adapter

## FORGE-P3-002 — LDA provenance

## FORGE-P3-003 — ToolScript + LDA integration

## FORGE-P3-004 — StrategyCapsule schema

## FORGE-P3-005 — TaskCapsuleRegistry

## FORGE-P3-006 — Capsule promotion evidence pipeline integration

---

# 139. Risk Register

| Risk | Impact | Mitigation |
|---|---:|---|
| ToolScript bypasses authority | Critical | RPC-only privileged effects |
| Fork explosion | High | hard count/budget limits |
| Context distillation loses key fact | High | artifact refs + dereference |
| Writable branches collide | High | isolated worktrees |
| Capsule becomes arbitrary code injection | Critical | pure/advisory MVP |
| LDA stale index | High | repo/tree digest provenance |
| Stop Gate becomes over-restrictive | Medium | task-specific GoalContract |
| Reflex controller fights model | Medium | sparse deterministic triggers |
| Branches increase cost without gain | Medium | opportunistic fork policy |
| Complex runtime diffuses core | High | strict module boundaries |
| Benchmark overfitting | Medium | varied internal tasks + external checks |

---

# 140. Security Review Checklist

Before enabling ToolScript by default:

```text
[ ] no unrestricted subprocess from script
[ ] no inherited environment secrets
[ ] no unrestricted sockets
[ ] no host filesystem escape
[ ] all privileged calls mediated
[ ] all mediated calls capability checked
[ ] time limit enforced
[ ] memory limit enforced
[ ] tool-call limit enforced
[ ] output limit enforced
[ ] process terminated on session cancellation
[ ] causal parent id recorded
[ ] artifact digests recorded
```

---

# 141. Performance Review Checklist

```text
[ ] ToolScript startup cost measured
[ ] ToolScript saves model turns on representative task
[ ] branch summaries bounded
[ ] no duplicate repository scan
[ ] compaction avoids re-summarizing immutable artifacts
[ ] LDA used only when beneficial
[ ] simple task path remains small
[ ] no mandatory branch
[ ] no mandatory second model
```

---

# 142. Benchmark Philosophy

FORGE development should not block on exhaustive benchmark campaigns.

Use:

```text
Stage A
5–10 targeted tasks exposing current failures

Stage B
small LAM/internal corpus

Stage C
representative external coding tasks

Stage D
larger SWE-style evaluation only after harness is competent
```

The goal of early testing is:

```text
does the mechanism make the agent actually work better?
```

not:

```text
produce a publication-grade confidence interval.
```

---

# 143. Minimal Comparative Report

For every major FORGE mechanism record:

```text
baseline result
FORGE result
task success
turns
tool calls
token usage
verification
observed failure mode
qualitative trajectory difference
```

Example:

```text
Task: complex-cache-17

Baseline:
FAILED
17 turns
wrong file localization
no real patch

FORGE + ToolScript:
PASS
11 turns
24 inner tool operations
1 patch
target tests PASS

Interpretation:
programmatic repository triage materially improved localization.
```

---

# 144. What Constitutes Evidence of Improvement

Strong evidence:

```text
previously failing real task now passes
fewer repeated failures
correct repository localization
real tests move from fail to pass
lower turns for same success
successful recovery after first bad patch
```

Weak evidence:

```text
model says reasoning felt clearer
longer plan
more agents participated
more logs produced
larger context
```

---

# 145. First Real Tasks to Use

Select tasks that exercise distinct mechanics.

```text
Task A
small obvious bug
tests Fast Path

Task B
large output / repository search problem
tests ToolScript

Task C
competing hypotheses
tests fork

Task D
first patch wrong
tests reflex recovery

Task E
long task crossing context pressure
tests compaction

Task F
large indexed repo
tests optional LDA
```

Do not begin with a giant benchmark sweep.

---

# 146. Failure Analysis Protocol

After each failed real task:

```text
1. inspect final verification
2. locate first irreversible wrong assumption
3. inspect context at that point
4. inspect available but unused tools
5. inspect repeated effects
6. inspect whether a fork would have helped
7. inspect whether ToolScript could compress mechanical work
8. inspect whether Stop Gate rejected correctly
9. classify missing harness capability
10. change smallest outer-layer mechanism
```

Do not immediately modify the kernel.

---

# 147. FORGE Engineering Loop

Canonical development loop:

```text
real task
→ trajectory
→ identify first meaningful failure
→ smallest harness change
→ rerun
→ compare
→ keep/revert
```

The purpose is to converge toward a better harness while keeping architecture simple.

---

# 148. Meta-Harness Compatibility

FORGE should expose configuration so future experiment tooling can mutate:

```text
ToolScript enabled
ToolScript budget
fork threshold
fork count
branch model
compaction strategy
LDA mode
reflex thresholds
stop contract strictness
capsule enablement
```

Do not implement automated mutation in FORGE itself.

A meta-harness can operate above it later.

---

# 149. Potential Future Extension — Trajectory Search

If adaptive branching proves valuable, FORGE can later support:

```text
best-first branch expansion
beam search over hypotheses
candidate patch ranking
trajectory reuse
```

But do not implement MCTS/beam infrastructure in v0.x.

First prove:

```text
one useful branch beats one stuck trajectory
```

---

# 150. Potential Future Extension — Trajectory Memory

Successful branch summaries could later form retrieval memory:

```text
task pattern
failure pattern
useful strategy
evidence
```

Example:

```text
"pytest fixture scope regression"
→ inspect conftest hierarchy
→ compare fixture overrides
```

This should remain evidence-backed and provenance-aware.

---

# 151. Potential Future Extension — Learned Reflex Policy

Once enough trajectories exist:

```text
state features
→ learned policy
→ directive probability
```

Potential targets:

```text
fork now?
compact now?
request more context?
switch model?
stop?
```

Not for v0.x.

Start deterministic.

---

# 152. Potential Future Extension — Compiled ToolScript Templates

Repeated successful ToolScripts can become reusable templates:

```text
repo localization
failure clustering
API impact analysis
test selection
dependency traversal
```

They remain tools/skills, not kernel code.

---

# 153. Anti-Patterns

Reject the following implementations.

## Anti-pattern A — FORGE as another workflow engine

```text
ForgeEngine
ForgeScheduler
ForgeRuntime
ForgeLedger
```

No.

Use AETHER.

## Anti-pattern B — unrestricted Python REPL

No direct model-generated host code.

## Anti-pattern C — mandatory swarm

Most tasks should not spawn agents.

## Anti-pattern D — full transcript merging

Child summaries only.

## Anti-pattern E — giant static system prompt

Keep the model-facing contract compact.

## Anti-pattern F — LDA mandatory for every task

Use on demand.

## Anti-pattern G — review agent after every patch

Environment verification first.

## Anti-pattern H — model confidence as stop signal

Evidence first.

---

# 154. Definition of Done — Architecture

Architecture is complete when:

```text
FORGE is expressed as an AETHER composition
kernel remains domain-blind
authority remains conserved
events/artifacts remain authoritative
simple tasks retain low overhead
advanced compute remains optional
```

---

# 155. Definition of Done — Product Capability

FORGE is practically useful when a frontier model can:

```text
open an unfamiliar repo
find relevant code
write/edit real files
run real tests
process large tool outputs efficiently
recover from a wrong attempt
spawn bounded independent investigation when needed
preserve state across long runs
refuse premature completion
finish with evidence
```

That is the actual blocker to solve before optimizing benchmark score.

---

# 156. Recommended First Implementation Cut

If only one implementation wave is allowed, build:

```text
1. vg-code-forge manifest
2. ForgeAdmissionGate
3. ForgeMetaController
4. forge-distill compaction
5. ToolScript MVP
6. one research fork path
```

Do **not** build first:

```text
candidate patch tournament
learned routing
MCTS
capsule promotion automation
large analytics platform
complex LDA preprocessing
```

This first cut already changes the harness qualitatively.

---

# 157. Recommended Initial Directory Shape

After reconciling with the real repository:

```text
vanguard/packages/
├── agency/
│   └── manifests/
│       └── vg-code-forge/
│           ├── manifest.json
│           ├── system-prompt.txt
│           ├── context-policy.json
│           ├── routing-policy.json
│           ├── approval-policy.json
│           ├── budget-policy.json
│           └── toolscript-tool.json
│
├── ports/
│   └── toolscript.py
│
├── runtime/
│   ├── forge_admission.py
│   ├── forge_controller.py
│   ├── forge_branch.py
│   ├── forge_distillation.py
│   ├── forge_capsules.py
│   └── toolscript.py
│
└── adapters/
    └── sandbox/
        └── toolscript.py
```

Do not force this exact shape if the existing repo conventions place these responsibilities elsewhere.

The architectural responsibility matters more than the filename.

---

# 158. Suggested Test Directory Shape

```text
test/
├── agency/
│   └── test_vg_code_forge_manifest.py
├── runtime/
│   ├── test_forge_admission.py
│   ├── test_forge_controller.py
│   ├── test_forge_branch.py
│   ├── test_forge_compaction.py
│   └── test_toolscript_broker.py
├── adapters/
│   └── test_toolscript_sandbox.py
└── falsifiers/
    ├── test_forge_toolscript_authority.py
    ├── test_forge_stale_verification.py
    └── test_forge_child_budget.py
```

Use actual project test conventions.

---

# 159. Example `ForgeReflexState`

```python
@dataclass(frozen=True)
class ForgeReflexState:
    run_id: str

    turns: int
    turns_since_progress: int

    workspace_digest: str
    last_verified_workspace_digest: str | None

    active_hypothesis: str | None
    hypothesis_count: int
    competing_hypotheses: int

    last_failure_fingerprint: str | None
    repeated_failure_count: int

    finish_attempted: bool
    finish_rejection_count: int

    context_pressure: float

    forks_used: int
    forks_available: int

    remaining_turns: int
    remaining_tokens: int | None
```

Keep it projection-derived.

Do not treat it as an independent authoritative mutable store.

---

# 160. Example Reflex Policy

```python
class DefaultForgeReflexPolicy:
    def decide(
        self,
        state: ForgeReflexState,
    ) -> StrategyDirective | None:

        if (
            state.finish_attempted
            and state.workspace_digest
            != state.last_verified_workspace_digest
        ):
            return StrategyDirective(
                kind="change_verification",
                reason="Verification is stale for current workspace.",
            )

        if state.repeated_failure_count >= 2:
            if (
                state.forks_available > 0
                and state.competing_hypotheses > 0
            ):
                return StrategyDirective(
                    kind="fork",
                    reason="Repeated failure with unresolved alternatives.",
                )

            return StrategyDirective(
                kind="redirect",
                reason="Repeated equivalent failure; change approach.",
            )

        if state.turns_since_progress >= 3:
            return StrategyDirective(
                kind="abandon_hypothesis",
                reason="No environment-visible progress.",
            )

        if state.context_pressure >= 0.88:
            return StrategyDirective(
                kind="request_context",
                reason="Compact active trajectory.",
            )

        return None
```

---

# 161. Example Goal Contract Builder

```python
def build_goal_contract(
    task: CodingTask,
    harness: ResolvedHarness,
) -> GoalContract:
    checks = []

    if task.mode == "write":
        checks.append(
            CheckRequirement(
                kind="workspace_changed",
                required=True,
            )
        )

        checks.append(
            CheckRequirement(
                kind="verification_fresh",
                required=True,
            )
        )

    return GoalContract(
        task_digest=task.digest,
        mode=task.mode,
        required_effects=tuple(...),
        required_checks=tuple(checks),
        forbidden_conditions=(
            "unresolved_patch_conflict",
        ),
        completion_evidence=(
            "workspace_digest",
            "verification_receipt",
        ),
    )
```

Keep heuristics conservative.

Do not invent test requirements the task cannot satisfy.

---

# 162. Example Context Summary

```text
FORGE STATE

Goal:
Fix TTL refresh so reads after refresh observe the renewed expiration.

Current hypothesis:
refresh() updates value but does not update expiry index.

Verified facts:
- CacheEntry stores expires_at.
- refresh() is implemented in cache/store.py:118.
- test_refresh_expiry currently fails.
- Failure remains after first patch because secondary heap index is stale.

Rejected:
- serializer bug.
- clock mock issue.

Changed:
- cache/store.py

Verification:
pytest tests/cache/test_refresh.py -q
FAIL 1/7
receipt artifact sha256:...

Branch:
branch-02 confirmed heap index is authoritative for eviction.

Next:
update heap index atomically with expires_at, rerun targeted test.

Raw evidence:
sha256:...
```

This is the target quality for compaction.

---

# 163. Example Branch Summary

```json
{
  "branch_id": "run-child-02",
  "objective": "Determine whether TTL eviction uses CacheEntry.expires_at or the heap index.",
  "disposition": "supported",
  "findings": [
    "Eviction reads the heap index, not CacheEntry.expires_at directly.",
    "refresh() updates CacheEntry.expires_at but leaves the heap node stale."
  ],
  "files_inspected": [
    "cache/store.py",
    "cache/eviction.py",
    "tests/cache/test_refresh.py"
  ],
  "evidence_refs": [
    "sha256:..."
  ],
  "dead_ends": [
    "serializer path is unrelated"
  ],
  "next_action": "Update heap entry during refresh."
}
```

---

# 164. Example Candidate Patch Branch Result

```json
{
  "branch_id": "run-child-07",
  "objective": "Try atomic heap replacement during refresh.",
  "disposition": "candidate_patch",
  "patch_digest": "sha256:...",
  "verification_digest": "sha256:...",
  "findings": [
    "Targeted cache tests pass 7/7.",
    "No API surface change."
  ],
  "confidence": 0.94
}
```

Parent must still apply and verify against its own authoritative workspace.

---

# 165. Example ToolScript Manifest Concept

```json
{
  "name": "toolscript",
  "description": "Execute bounded Python that may invoke authorized AETHER tools through a mediated broker.",
  "input_schema": {
    "type": "object",
    "properties": {
      "source": {
        "type": "string"
      },
      "max_tool_calls": {
        "type": "integer",
        "minimum": 1,
        "maximum": 64
      }
    },
    "required": ["source"]
  }
}
```

Translate to the actual tool schema format.

Do not expose arbitrary runtime options to the model unless necessary.

---

# 166. Example ToolScript System Prompt Fragment

```text
Use ToolScript when several deterministic tool operations can be composed more efficiently than alternating model/tool turns.

Good uses:
- search + filter + rank many repository matches
- parse large test output
- traverse symbol/reference relationships
- compute summaries over structured tool results

Do not use ToolScript merely to hide reasoning.
Do not attempt direct host access.
All privileged operations must use the provided tool RPC functions.
Print only the information you need for the next reasoning step.
```

---

# 167. AETHER Protocol Mapping

FORGE should preserve:

```text
Model intention
→ EffectProposal
→ policy/capability check
→ adapter execution
→ receipt
→ event
→ projection
```

ToolScript nests this pattern but does not replace it:

```text
Model intention
→ ToolScript effect
→ sandbox
→ inner tool intention
→ normal AETHER effect
→ normal authorization
→ normal receipt
```

This nested execution must preserve parent causal references.

---

# 168. Causal Lineage for ToolScript

Recommended lineage:

```text
root run
└── model proposal
    └── ToolScript effect
        ├── fs.search effect
        ├── fs.read effect
        ├── fs.read effect
        └── proc.test effect
```

The final ToolScript receipt references all child effect IDs.

This is important for:

- replay;
- audit;
- cost accounting;
- debugging;
- trajectory analysis.

---

# 169. Causal Lineage for Fork

```text
root run
└── agent.spawn effect
    └── child run
        ├── model/tool events
        ├── artifacts
        └── child result
            └── BranchSummary artifact
```

Parent context receives the summary, but lineage remains linked.

---

# 170. Budget Settlement

FORGE must not invent local accounting.

ToolScript consumes:

```text
outer effect budget
+
inner tool-call budget
+
wall-time/runtime budget
```

Fork consumes:

```text
child conserved budget
```

Candidate branch unused budget returns according to existing settlement semantics.

No negative-consumption/refund reinterpretation.

---

# 171. Security of Model-Generated Procedures

A ToolScript is untrusted input.

Treat it similarly to:

```text
a user-submitted script
```

Therefore:

```text
validate
sandbox
constrain
authorize each privileged effect
record
terminate on violation
```

Do not trust it because it was generated by the same model operating the agent.

---

# 172. Dependency Policy

Avoid adding large dependencies.

Preferred ToolScript MVP:

```text
Python stdlib
existing sandbox/process abstractions
existing IPC/JSON utilities
```

Only add dependencies if they provide a substantial and measured benefit.

FORGE itself should not require:

```text
Ray
Celery
LangGraph
Docker SDK
new graph databases
new orchestration frameworks
```

---

# 173. Repository Compatibility

FORGE should remain repository-language agnostic.

Core tools:

```text
filesystem
search
git
process execution
patch
test command
```

Language-specific behavior should live in:

```text
skills
capsules
LDA providers
ToolScripts
repository manifests
```

This keeps Vanguard universal.

---

# 174. Language-Specific Skills

Examples that may later be reusable:

```text
python-pytest
rust-cargo
typescript-vitest
go-test
java-gradle
```

Each can provide:

```text
test command discovery
failure parser
related file conventions
build command
```

But the core FORGE loop remains unchanged.

---

# 175. Repository Bootstrap

On first contact with an unknown repository, FORGE may run a cheap bootstrap:

```text
git status
top-level tree
detect language/build files
detect test roots
read nearest README/AGENTS instructions
```

Do not create a complete semantic index automatically.

Only deepen exploration if needed.

---

# 176. Repository Instructions Priority

Context order:

```text
system/AETHER law
> explicit task
> repository AGENTS/instructions
> package/module-specific instructions
> README/conventions
> inferred behavior
```

FORGE must inspect repo-local agent instructions where present.

Derived summaries may never override direct instructions.

---

# 177. Diff Review

Before finish:

```text
git diff --stat
git diff relevant files
```

Use either:

```text
model review
or
deterministic checks
```

depending on task.

The Stop Gate may require existence of a patch/diff artifact for write tasks.

---

# 178. Final Verification Policy

A reasonable default:

```text
simple bug
→ targeted tests

medium change
→ targeted + related tests

large change
→ targeted + related + build/typecheck where appropriate
```

Do not always run the entire repository test suite.

The model can request broader verification if uncertainty remains.

---

# 179. Task Completion Record

Final result should include references to:

```text
task digest
final workspace digest
patch digest
verification receipt(s)
important artifact refs
branch summaries used
model identities
```

The user-facing response may remain concise.

The internal run remains fully inspectable.

---

# 180. Rollback Strategy

FORGE is outer-layer and should be easy to disable.

Rollback:

```text
remove/disable vg-code-forge manifest
disable ToolScript capability
disable fork reflex
retain generic runtime behavior
```

No data migration should be required for core AETHER.

Artifacts/events from prior FORGE runs remain readable.

---

# 181. Feature Flags

During development:

```text
forge.stop_gate
forge.reflexes
forge.toolscript
forge.forks
forge.capsules
forge.lda
```

Prefer manifest-level flags.

Avoid global environment-variable spaghetti.

---

# 182. Backward Compatibility

Existing harnesses:

```text
vg-code-default
vg-code-swe-mini
vg-code-opencode-shaped
```

must continue to work unchanged.

FORGE additions should be opt-in.

No semantic changes to shared runtime should occur unless existing tests prove compatibility.

---

# 183. Migration Policy

No migration of existing agents into FORGE.

Instead:

```text
existing harness stays
new FORGE preset added
comparison begins
successful mechanisms later generalized selectively
```

This preserves experimental clarity.

---

# 184. Promotion Criteria to General Vanguard

A FORGE mechanism may be generalized only if:

```text
useful across at least two agent domains
not coding-specific
stable contract
measurable benefit
low overhead
clear semantics
```

Likely candidates:

```text
artifact-backed tool admission
generic bounded ToolScript capability
generic branch distillation
```

Likely FORGE-specific mechanisms:

```text
coding GoalContract rules
coding failure reflexes
coding branch prompts
```

---

# 185. Kernel Promotion Criteria

A FORGE mechanism should enter kernel only if:

```text
it is required for authority,
budget conservation,
causal lineage,
settlement,
or universal effect execution semantics.
```

Almost nothing in FORGE should satisfy this criterion.

---

# 186. First Benchmark Expectation

Do not expect immediate SOTA score.

The first milestone is more fundamental:

```text
strong model actually performs complex coding work
```

Observed evidence should shift from:

```text
NO_PATCH
empty/fictional success
unverified answer
```

toward:

```text
real file localization
real patch
real test
adaptive repair
verified completion
```

Only then optimize score.

---

# 187. Why FORGE Could Beat a Heavier Harness

A heavier harness may force the model through incorrect abstractions.

FORGE instead gives:

```text
small trusted substrate
+
high programmability
+
real feedback
+
optional extra compute
```

As models improve, this can age better because less cognitive policy is frozen into the harness.

The harness provides **capabilities and invariants**, not a mandatory theory of reasoning.

---

# 188. Why FORGE Could Fail

FORGE may underperform if:

```text
models cannot reliably decide when to use ToolScript
models do not branch strategically
reactive loop wanders
minimal prompt lacks useful software-engineering priors
ToolScript sandbox overhead is too high
branch distillation loses crucial details
```

If so, selectively add:

```text
skills
reflexes
small procedural guidance
task-type presets
```

Do not immediately revert to a giant orchestration architecture.

---

# 189. Comparison with External Inspirations

FORGE should copy **principles**, not code.

## From DeepSeek Harness

```text
small execution loop
extensibility outside core
interceptable runtime behavior
```

## From Hermes

```text
programmatic tool calling
procedural/skill-oriented agent behavior
context economy
```

## From Pi

```text
small agent surface
branchable sessions
compaction
extensions
```

## From Grok Build

```text
lifecycle interception
stop rejection
subagent isolation
skills
```

AETHER contributes:

```text
capability authority
causal event ledger
budget conservation
artifacts
recovery
settlement
manifest composition
```

The combination is the differentiator.

---

# 190. Reference Architecture Summary

```text
AETHER KERNEL
  authority / budgets / lineage / effects
              │
              ▼
VANGUARD RUNTIME
  session / episode / projections / artifacts
              │
              ▼
FORGE HARNESS
  ├── minimal reactive prompt
  ├── Stop Gate
  ├── Reflex Controller
  ├── Forge Compaction
  ├── ToolScript
  ├── Adaptive Forks
  ├── Branch Distillation
  ├── Task Capsules
  └── Optional LDA
              │
              ▼
REAL REPOSITORY
  filesystem / git / shell / tests
```

---

# 191. Final Implementation Directive

The implementing developer should proceed as follows:

> **Do not redesign the framework. Reconcile the exact current code once, identify the existing seams, create `vg-code-forge`, and implement the smallest missing outer-layer mechanisms required for a powerful reactive coding agent. Use existing admission, controller, spawn, context, artifacts, event ledger, budgets, and recovery semantics. Add ToolScript through a mediated sandbox, use child runs for optional branching, distill trajectories rather than copying transcripts, and make environment evidence the sole basis for completion.**

The implementation should optimize for:

```text
real coding ability
low harness friction
programmability
evidence
context efficiency
recovery
bounded adaptive compute
architectural reversibility
```

---

# 192. Principal Engineering Checklist

Before declaring FORGE implementation ready:

```text
[ ] Runs through current product entrypoint
[ ] No new parallel runtime
[ ] No new event authority
[ ] No capability bypass
[ ] Stop Gate uses real evidence
[ ] Real patches occur
[ ] Real tests occur
[ ] Stale verification rejected
[ ] Repeated failures change strategy
[ ] ToolScript mediated through dispatch
[ ] ToolScript sandbox falsifiers pass
[ ] Fork uses existing child runtime
[ ] Child authority attenuated
[ ] Child summaries bounded
[ ] Compaction preserves engineering state
[ ] Artifacts preserve raw evidence
[ ] Resume reconstructs state
[ ] LDA optional
[ ] LAM external
[ ] Existing harnesses unaffected
[ ] Simple tasks retain low overhead
[ ] Complex tasks can scale compute
```

---

# 193. Final Thesis

The strongest version of FORGE is not a giant coding workflow.

It is a **programmable, evidence-grounded coding substrate layered over AETHER**:

```text
Model
+
Minimal Reactive Loop
+
Authorized Tools
+
Programs Over Tools
+
Branchable Reasoning
+
Runtime Reflexes
+
Artifact-Backed Context
+
Real Verification
```

The model is allowed to create temporary procedure; AETHER remains responsible for authority, execution, evidence, durability, and recovery.

That separation is the core architectural bet.

If successful, FORGE should allow Vanguard to exploit stronger future models without repeatedly redesigning the orchestration layer, while still supporting sophisticated task-specific behavior when the problem actually requires it.

