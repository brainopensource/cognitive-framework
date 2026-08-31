---
id: report.electroweak.solution-a.full-code-forge-wave-2
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
---

# AETHER FORGE — Full Code Manifest — Wave 2

## Delivery contract

- Branch: `feat/beta-release_electroweak-v091`
- Exact reconciled subject: `f242ced297216109736975376802f1e3dc4e29ce`
- Scope: backend only; no frontend changes.
- Focus: ToolScript lifecycle and security, adaptive forks, branch budgets/scheduling/artifacts, capsules, optional LDA, model routing, verification, snapshots, recovery, and presets.
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

## Wave acceptance

This wave is accepted only after its focused unit/contract/falsifier tests pass, boundary and domain-blindness linters remain green, no kernel LOC is added, and every claimed completion is backed by a fresh verification receipt. Full-suite execution is intentionally deferred to final integration.
