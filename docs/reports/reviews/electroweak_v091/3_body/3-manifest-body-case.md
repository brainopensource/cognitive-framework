---
id: report.electroweak.3_body.3-manifest-body-case
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
purpose: Non-canonical candidate input to the Coding Max architecture convergence review.
audience:
  - contributor
  - architect
---

# AETHER / Vanguard — Coding Max Harness Implementation Specification

**Role:** Principal Software Engineer, Staff Agentic Systems Architect, Coding-Harness Engineer, Runtime Engineer, SWE-bench Specialist, Technical Lead

## Mission

Design the complete implementation specification for a production-grade **AETHER Coding Max Harness** built on top of the existing AETHER/Vanguard framework.

This is not a greenfield project.

Do not redesign AETHER.

Do not create another runtime.

Do not create another event system.

Do not create another plugin architecture.

Use the current AETHER substrate as the execution foundation and implement Coding Max primarily as a composition of:

```text
Agent Manifests
Workflow
Plugins
Tools
Context Providers
Model Routing
Policies
Evaluators
Memory
Artifacts
Recovery
Budgets
```

The result must be detailed enough that a senior developer can begin implementation directly without another architecture/planning pass.

---

## 1. Objective

Implement a high-capability coding-agent harness capable of solving:

- repository-scale bug fixes;
- SWE-bench style tasks;
- SWE-bench Pro style tasks;
- multi-file changes;
- difficult debugging;
- test failures;
- dependency problems;
- refactoring;
- API migrations;
- greenfield features;
- unfamiliar repositories;
- long-running coding tasks.

The main design principle is:

```text
Use maximum intelligence when necessary,
minimum orchestration when sufficient.
```

The harness must dynamically adapt its computational effort.

---

## 2. Canonical Execution Loop

Design the system around:

```text
Understand
→ Explore
→ Localize
→ Plan
→ Execute
→ Verify
→ Diagnose
→ Repair / Replan
→ Complete
```

But do not force every task through every stage.

For simple tasks:

```text
Task
→ Search
→ Edit
→ Test
→ Done
```

For complex tasks:

```text
Task
→ Repository Intelligence
→ Context Compilation
→ Planning
→ Worker
→ Verification
→ Failure Analysis
→ Reviewer/Replanner
→ Repair
→ Final Verification
```

---

## 3. Coding Max Architecture

Design the following logical structure:

```text
                     TASK
                      │
                      ▼
              Task Understanding
                      │
                      ▼
               Task Classifier
                      │
          ┌───────────┴────────────┐
          │                        │
          ▼                        ▼
 Repository Intelligence      Fast Path
          │
          ▼
 Context Compiler
          │
          ▼
      Planner / TODO
          │
          ▼
   Implementation Worker
          │
          ├──── Tools
          ├──── Shell
          ├──── Scripts
          ├──── LDA / Atlas
          ├──── Repository Search
          └──── Test Execution
          │
          ▼
      Verification
          │
     ┌────┴────┐
     │         │
   PASS       FAIL
     │         │
     │         ▼
     │    Failure Classifier
     │         │
     │    ┌────┼─────────┐
     │    │    │         │
     │ context patch   reasoning
     │    │    │         │
     │ retrieve repair reviewer
     │                 /replanner
     │
     ▼
Final Evidence
     │
     ▼
Completion
```

Map each component to existing AETHER abstractions.

---

## 4. Repository Inspection First

Before designing changes, establish:

```text
branch
HEAD commit
working tree
current Vanguard package structure
runtime contracts
agent manifests
workflow implementation
tool interfaces
context APIs
model provider interfaces
plugin APIs
event definitions
artifact storage
memory/state persistence
budget enforcement
evaluator interfaces
retry/recovery APIs
checkpoint support
multi-agent support
```

Produce:

| Coding Max capability | Existing AETHER mechanism | Gap | Required change |
|---|---|---|---|

Do not duplicate working functionality.

---

## 5. Agent Manifest

Specify a concrete Coding Max agent manifest.

Conceptual shape:

```yaml
agent:
  id: coding-max

  model:
    strategy: adaptive

  workflow:
    type: coding-max

  context:
    strategy: progressive-hierarchical

  tools:
    - repository-search
    - file-read
    - file-edit
    - patch
    - shell
    - test
    - git
    - symbol-search
    - lda

  memory:
    task: enabled
    repository: optional

  evaluators:
    - patch
    - tests
    - task-completion

  policies:
    retry: adaptive
    verification: layered

  limits:
    turns: adaptive
    tokens: bounded
    tool_calls: bounded
```

Use real AETHER schema names after inspecting the repository.

---

## 6. Task Classifier

Implement a lightweight classifier for:

```text
simple_fix
complex_bug
test_failure
refactor
feature
multi_file_feature
dependency_issue
repository_exploration
greenfield
long_task
unknown
```

Inputs:

```text
task text
repository metadata
repository size
initial search result
available tests
```

Output:

```python
TaskProfile(
    task_type,
    estimated_complexity,
    uncertainty,
    repo_familiarity,
    suggested_workflow,
    initial_budget,
)
```

Do not require an expensive LLM call when deterministic classification is sufficient.

---

## 7. Fast Path

Simple tasks should bypass expensive orchestration.

```python
if task_profile.complexity <= SIMPLE_THRESHOLD:
    result = fast_worker.run(task)

    verification = verify(result)

    if verification.pass:
        return complete(result)

    escalate_to_coding_max()
```

This prevents Coding Max from becoming inherently slow.

---

## 8. Repository Intelligence Layer

Build an abstraction:

```python
class RepositoryIntelligence(Protocol):
    def search(self, query: SearchQuery) -> SearchResult: ...
    def symbol(self, name: str) -> SymbolResult: ...
    def dependencies(self, target: str) -> DependencyResult: ...
    def tests_for(self, target: str) -> TestMapping: ...
    def summarize(self, scope: RepoScope) -> RepoSummary: ...
```

Possible providers:

```text
NativeRepoSearch
RipgrepProvider
GitProvider
ASTProvider
LDAProvider
```

Providers expose normalized results.

They must not dictate context policy.

---

## 9. LDA / Atlas Integration

Integrate LDA initially as an optional provider/plugin.

Preferred topology:

```text
Coding Max
   │
Repository Intelligence API
   │
   ├── Native Search
   ├── Git
   ├── AST
   └── LDA Adapter
           │
           ▼
       LDA / Atlas
```

LDA may provide:

```text
symbol index
file relationships
code ↔ documentation relationships
repository map
dependency graph
test relationships
module summaries
semantic retrieval
metadata ranking signals
```

Do not make Coding Max dependent on LDA.

Required behavior:

```python
if lda.available():
    use_enriched_intelligence()
else:
    use_native_repository_tools()
```

Define:

- adapter protocol;
- input/output schemas;
- timeout policy;
- caching policy;
- failure isolation;
- provenance.

---

## 10. Repository Map

Produce a compact repository map.

```python
RepositoryMap(
    languages,
    modules,
    entrypoints,
    test_roots,
    build_system,
    important_symbols,
    dependencies,
    recently_relevant_files,
)
```

Avoid dumping the full repository.

Use hierarchical detail.

---

## 11. Context Compiler

Implement:

```python
class ContextCompiler:
    def compile(
        self,
        task,
        repo_state,
        working_memory,
        token_budget,
    ) -> CompiledContext:
        ...
```

Context candidates receive scoring.

Conceptual score:

```text
score =
    task_similarity
  + symbol_relevance
  + dependency_proximity
  + test_relationship
  + stacktrace_relevance
  + recent_failure_relevance
  + plan_relevance
  + edit_proximity
  - redundancy
  - staleness
```

---

## 12. Progressive Context

Do not load everything initially.

Use:

```text
initial task
   ↓
minimal repository context
   ↓
model identifies missing information
   ↓
targeted retrieval
   ↓
context mutation
```

Provide APIs:

```python
context.add(...)
context.drop(...)
context.pin(...)
context.compress(...)
context.refresh(...)
context.replace(...)
```

---

## 13. Context Cache

Cache derived repository information:

```text
repository map
file summaries
symbol summaries
dependency results
test mapping
search results
documentation mapping
```

Key entries using:

```text
repo identity
HEAD
file hash
provider version
query
```

Invalidate only affected entries.

---

## 14. Working Memory

Implement compact task memory:

```python
WorkingMemory(
    task,
    current_goal,
    hypotheses,
    decisions,
    todo,
    known_facts,
    edited_files,
    failed_attempts,
    verification_state,
)
```

This should be derived from or persisted through AETHER events/artifacts.

Do not make conversation history the only state representation.

---

## 15. Planner

Planner output:

```python
Plan(
    objective,
    assumptions,
    steps,
    verification_strategy,
    risk_points,
)
```

Example:

```text
1. reproduce failure
2. identify implementation owner
3. inspect related tests
4. patch minimal implementation
5. run targeted test
6. inspect regression
```

Planner must remain mutable.

---

## 16. TODO State Machine

Define explicit TODO states:

```text
PENDING
ACTIVE
BLOCKED
DONE
FAILED
SKIPPED
```

Protocol:

```python
TodoItem(
    id,
    description,
    dependencies,
    status,
    evidence,
)
```

Events:

```text
todo.created
todo.started
todo.completed
todo.failed
todo.reopened
```

---

## 17. Dynamic Replanning

Trigger replanning on events such as:

```text
failed assumption
wrong localization
unexpected dependency
repeated failed patch
unexpected test behavior
major context discovery
budget pressure
```

```python
if state.contradicts(plan.assumptions):
    plan = replanner.revise(
        current_plan=plan,
        evidence=state.new_evidence,
    )
```

---

## 18. Worker

Worker responsibilities:

```text
inspect
search
reason
run tools
modify files
run scripts
run tests
record evidence
update TODO
```

Worker must not decide success based solely on its own textual response.

---

## 19. Tool Protocol

Define normalized tool calls:

```python
ToolCall(
    tool_id,
    operation,
    arguments,
    timeout,
    expected_effect,
)
```

Result:

```python
ToolResult(
    success,
    stdout,
    stderr,
    exit_code,
    artifacts,
    observations,
)
```

Large outputs should become artifacts.

---

## 20. Coding Tools

Ensure Coding Max can use:

```text
read_file
write_file
apply_patch
grep
ripgrep
find
tree
git_diff
git_status
git_log
git_blame
shell
test_runner
build
lint
typecheck
symbol_lookup
dependency_lookup
AST query
LDA query
```

Favor deterministic tools over model reasoning where appropriate.

---

## 21. Script Tool

Support ephemeral script execution.

Examples:

```python
rank_files()
parse_stack_trace()
analyze_imports()
find_test_targets()
compare_api_signatures()
summarize_failures()
```

Scripts should execute in controlled sandboxes.

Capture:

```text
script
inputs
outputs
exit status
runtime
```

---

## 22. Edit Strategy

Prefer minimal scoped patches.

Canonical loop:

```text
inspect target
→ form hypothesis
→ patch
→ diff
→ verify
```

After edits automatically inspect:

```text
git diff
changed interfaces
affected tests
```

---

## 23. Verification Pipeline

Implement layered verification:

```text
V1 syntax
V2 formatting
V3 lint
V4 typecheck
V5 targeted tests
V6 related tests
V7 broader tests
V8 task verification
V9 patch review
```

Not every layer always runs.

Policy example:

```python
if tiny_patch:
    run(V1, V5)

elif candidate_solution:
    run(V1, V3, V5, V6)

elif final_solution:
    run(relevant_final_verification)
```

---

## 24. Verification Contract

Define:

```python
VerificationResult(
    passed,
    checks,
    failures,
    evidence,
    confidence,
)
```

A task cannot be declared successful merely because the model says it is solved.

---

## 25. Failure Classifier

Implement classification:

```text
TASK_MISUNDERSTOOD
WRONG_FILE
INSUFFICIENT_CONTEXT
EXCESSIVE_CONTEXT
WRONG_HYPOTHESIS
BAD_PATCH
INCOMPLETE_PATCH
TEST_FAILURE
REGRESSION
TOOL_FAILURE
ENVIRONMENT_FAILURE
REPEATED_REASONING_FAILURE
STALE_MEMORY
BUDGET_PRESSURE
```

```python
failure = failure_classifier.classify(
    task,
    trajectory,
    verification,
    latest_result,
)
```

---

## 26. Recovery Strategies

Map failures to actions.

```python
match failure:
    case WRONG_FILE:
        context.expand_search()

    case INSUFFICIENT_CONTEXT:
        context.retrieve_missing()

    case BAD_PATCH:
        rollback()
        invoke_reviewer()

    case TEST_FAILURE:
        analyze_failure()

    case WRONG_HYPOTHESIS:
        replan()

    case REPEATED_REASONING_FAILURE:
        escalate_model()

    case TOOL_FAILURE:
        retry_or_replace_tool()
```

Every retry must change the state or strategy.

---

## 27. Retry Budget

Define bounded retries.

```python
RetryBudget(
    same_strategy=1,
    alternate_strategy=2,
    reviewer_escalation=1,
    model_escalation=1,
)
```

Avoid infinite loops.

---

## 28. Model Router

Define:

```python
class ModelRouter:
    def select(
        self,
        role,
        task_profile,
        state,
        budget,
        previous_failures,
    ) -> ModelSelection:
        ...
```

Roles:

```text
classifier
planner
worker
reviewer
replanner
summarizer
```

---

## 29. Adaptive Model Escalation

Example:

```text
cheap model
→ routine classification/search synthesis

strong worker
→ implementation

strong reviewer
→ repeated difficult failure
```

```python
if repeated_failure and budget.can_escalate:
    worker = router.stronger_model(worker)
```

Do not escalate unnecessarily.

---

## 30. Reviewer

Reviewer receives:

```text
original task
plan
patch
diff
test results
failure history
relevant context
```

Returns:

```python
ReviewDecision(
    decision=ACCEPT | REPAIR | REPLAN | RETRIEVE_MORE,
    defects=[],
    recommendations=[],
)
```

Reviewer must provide actionable evidence.

---

## 31. Conditional Reviewer

Do not always run the reviewer.

Trigger if:

```text
high complexity
large patch
critical interface change
tests still suspicious
worker confidence low
repeated repair
task requirements ambiguous
```

---

## 32. Parallel Investigation

For difficult tasks optionally spawn bounded investigators:

```text
Investigator A → localization
Investigator B → tests
Investigator C → architecture
```

Aggregate:

```python
InvestigationSummary(
    candidate_files,
    hypotheses,
    risks,
    contradictions,
)
```

Do not allow subagents unrestricted authority.

They inherit attenuated:

```text
tools
budget
scope
permissions
```

---

## 33. Competitive Implementation

For very difficult tasks optionally create multiple candidate approaches:

```text
Worker A → candidate patch
Worker B → candidate patch
        ↓
verification
        ↓
select best
```

Use only when failure cost justifies compute.

---

## 34. Long-Task Artifacts

Persist:

```text
task
plan
todo
repository map
hypotheses
important discoveries
failed attempts
patch history
test results
verification state
```

Prefer AETHER artifact storage.

Example references:

```python
TaskArtifactRef
PlanArtifactRef
RepoMapArtifactRef
PatchArtifactRef
TestArtifactRef
```

---

## 35. Checkpoints

Create recovery checkpoints after meaningful milestones:

```text
repository understood
plan accepted
first working patch
target tests passing
integration tests passing
```

Checkpoint should contain references rather than duplicate huge payloads.

---

## 36. Resume

Define resume:

```python
resume(run_id):
    state = projection.rebuild(run_id)
    artifacts = restore_referenced_artifacts(state)

    continue_from(
        state.last_valid_checkpoint
    )
```

Do not require replaying conversational text manually.

---

## 37. Repository Memory

Optional persistent repository memory:

```text
module roles
build commands
test commands
known architecture
important files
repository conventions
```

Every entry must include:

```text
source
commit/hash
timestamp
confidence
```

Stale memory must be invalidated.

---

## 38. Events

Define or reuse events for:

```text
task.classified
repo.search.completed
context.compiled
context.updated
plan.created
plan.updated
todo.changed
tool.started
tool.completed
patch.created
verification.completed
failure.classified
retry.started
review.completed
model.escalated
checkpoint.created
task.completed
task.failed
```

Use existing canonical event vocabulary whenever possible.

---

## 39. Artifacts

Large payloads should become artifacts:

```text
context snapshots
large command output
repository maps
patches
test logs
planner output
review reports
trajectory summaries
```

Events carry hashes/references.

---

## 40. Authorization

Respect AETHER's execution model:

```text
Observe
→ Decide
→ Authorize
→ Execute
→ Record
```

Workers propose effects.

Policies authorize effects.

Adapters execute effects.

Events record the result.

Do not bypass capability enforcement for Coding Max.

---

## 41. Budgets

Track at least:

```text
model tokens
model cost
turns
tool calls
wall time
subagents
retries
context size
```

Budget contract:

```python
BudgetState(
    tokens_remaining,
    cost_remaining,
    turns_remaining,
    tool_calls_remaining,
    time_remaining,
)
```

---

## 42. Completion Mode

When resources become constrained:

```python
if budget.low():
    disable_optional_agents()
    reduce_context()
    stop_speculative_exploration()
    run_essential_verification()
    finish_best_candidate()
```

---

## 43. Stopping Policy

Stop when:

```text
required behavior satisfied
required verification passes
no unresolved critical failures
final patch exists
```

Do not continue generating improvements indefinitely.

---

## 44. Coding Max Workflow State Machine

Define a formal state machine:

```text
RECEIVED
CLASSIFYING
EXPLORING
PLANNING
EXECUTING
VERIFYING
DIAGNOSING
REPAIRING
REPLANNING
REVIEWING
FINAL_VERIFY
COMPLETED
FAILED
```

Specify legal transitions.

---

## 45. Core Workflow Pseudocode

```python
def run_coding_max(task, repo, config):

    run = runtime.start(task)

    profile = classifier.classify(task, repo)

    if profile.simple:
        result = fast_path.run(task)

        if verifier.accept(result):
            return complete(result)

    repo_state = intelligence.inspect(repo)

    context = context_compiler.compile(
        task=task,
        repo_state=repo_state,
        budget=config.context_budget,
    )

    plan = planner.create(task, context)

    memory.store(plan)

    while budget.available():

        step = plan.next_action()

        result = worker.execute(
            step=step,
            context=context,
            tools=tools,
        )

        ledger.record(result)

        if context_manager.needs_update(result):
            context = context_manager.update(
                context,
                result,
            )

        if verifier.should_run(result):
            verification = verifier.verify(
                task,
                repo,
                result,
            )

            if verification.passed and plan.complete():
                break

            failure = failure_classifier.classify(
                verification,
                trajectory=current_trajectory(),
            )

            recovery = recovery_policy.select(
                failure,
                state=current_state(),
            )

            apply(recovery)

    final = final_verifier.verify(...)

    if final.passed:
        return complete(final)

    return fail(final)
```

Refine this to real AETHER APIs.

---

## 46. Plugin Structure

Propose concrete plugin modules such as:

```text
coding_max/
├── manifest.*
├── workflow/
│   ├── coding_max.*
│   ├── fast_path.*
│   └── transitions.*
├── planning/
│   ├── planner.*
│   ├── todo.*
│   └── replanner.*
├── context/
│   ├── compiler.*
│   ├── cache.*
│   ├── progressive.*
│   └── repo_map.*
├── intelligence/
│   ├── native.*
│   ├── git.*
│   ├── ast.*
│   └── lda_adapter.*
├── execution/
│   ├── worker.*
│   ├── scripts.*
│   └── patching.*
├── verification/
│   ├── verifier.*
│   ├── test_selector.*
│   └── reviewer.*
├── recovery/
│   ├── classifier.*
│   └── retry_policy.*
├── routing/
│   └── model_router.*
└── evaluators/
    └── task_completion.*
```

Adjust paths to actual repository architecture.

---

## 47. Interfaces and Protocols

For every important component provide explicit:

```python
Protocol
dataclass/schema
method signatures
inputs
outputs
error semantics
event interactions
artifact interactions
```

At minimum:

```text
TaskClassifier
RepositoryIntelligence
ContextCompiler
ContextManager
Planner
TodoManager
Worker
Verifier
FailureClassifier
RecoveryPolicy
Reviewer
ModelRouter
CheckpointManager
```

---

## 48. Error Model

Define typed errors.

Example:

```text
RepositoryAccessError
ContextCompilationError
ToolExecutionError
PatchApplicationError
VerificationError
ModelError
BudgetExceeded
CheckpointError
```

Distinguish recoverable from terminal failures.

---

## 49. Idempotency

Operations that may replay after crash should be designed for idempotency where appropriate.

Specify behavior for:

```text
tool retries
checkpoint restoration
artifact writes
event settlement
patch application
```

---

## 50. Concurrency

Use concurrency only where useful:

```text
independent repository searches
parallel investigator agents
independent test suites
candidate analysis
```

Maintain deterministic causal ordering in the event model.

Do not introduce concurrency into simple execution paths unnecessarily.

---

## 51. LAM Integration

Support LAM / LLM API Mock as an experiment adapter.

Topology:

```text
LAM Task Dataset
      │
      ▼
OpenRouter-compatible Mock API
      │
      ▼
AETHER Provider Adapter
      │
      ▼
Coding Max
      │
      ▼
Trajectory / Patch / Tests
      │
      ▼
LAM Evaluator
```

Capture:

```text
task
workflow configuration
model emulation
events
tool calls
context operations
patch
verification
final outcome
```

LAM must not leak benchmark answers into the agent.

---

## 52. Meta-Harness Compatibility

Coding Max should expose configuration points so a future meta-harness can mutate:

```text
planning
context strategy
model routing
tool policy
reviewer threshold
retry policy
verification level
turn limits
parallelism
LDA usage
memory policy
```

Configuration should be declarative wherever practical.

---

## 53. Coding Max Preset

Produce a concrete maximum-capability preset.

Conceptually:

```yaml
preset: coding-max

planning:
  enabled: true
  adaptive: true

todo:
  persistent: true

context:
  progressive: true
  hierarchical: true
  cache: true
  lda: optional

tools:
  shell: true
  repository: true
  ast: true
  git: true
  tests: true

verification:
  layered: true
  adaptive: true

recovery:
  classify_failure: true
  strategy_switch: true

review:
  conditional: true

models:
  adaptive_routing: true
  escalation: true

artifacts:
  engineering_state: true

checkpoints:
  enabled: true

parallel:
  investigators: conditional
  candidate_patches: conditional
```

Translate into real manifest syntax.

---

## 54. Additional Presets

Derive:

```text
coding-fast
coding-balanced
coding-max
```

All share the same runtime.

Differences are configuration only.

---

## 55. Observability

Provide commands or equivalent APIs:

```bash
aether run --agent coding-max ...
aether inspect RUN
aether trajectory RUN
aether failures RUN
aether artifacts RUN
aether resume RUN
```

Reuse existing CLI capabilities wherever possible.

---

## 56. Minimal Testing Required

Do not create a massive test campaign.

### Unit

```text
context ranking
failure classification
retry transitions
todo transitions
model routing
budget logic
```

### Integration

```text
task → edit → test → success
task → failed patch → repair
task → wrong context → retrieval
task → worker failure → reviewer
task → crash → resume
```

### Real smoke tasks

At least:

```text
simple bug
multi-file bug
test-driven fix
complex unfamiliar repository task
```

---

## 57. Success Criteria

Coding Max implementation is accepted when:

```text
1. Real repository tools execute.
2. Real file edits happen.
3. Tests genuinely run.
4. Failed tests cause adaptive recovery.
5. Context can evolve during execution.
6. Planning/TODO survive multiple turns.
7. Reviewer can be invoked conditionally.
8. Model fallback/escalation works.
9. Long-task state persists.
10. Runs can be reconstructed from events/artifacts.
11. LDA can be enabled/disabled.
12. The same system supports fast and max presets.
```

---

## 58. Explicit Anti-Patterns

Reject:

```text
non-empty response == success
model self-report == verification
grounded = text contains file name
verified = model says tests passed
fake test results
synthetic dry-run used as benchmark result
retrying identical prompts
loading repository into giant prompt
mandatory multi-agent execution
always-on reviewer
kernel expansion for experiment logic
```

---

## 59. Implementation Order

Produce an exact implementation sequence.

Recommended initial order:

```text
CM-01 real execution baseline
CM-02 repository intelligence interface
CM-03 progressive context
CM-04 TODO/planner
CM-05 verification pipeline
CM-06 failure classifier
CM-07 adaptive recovery
CM-08 context cache
CM-09 model router/fallback
CM-10 reviewer
CM-11 LDA adapter
CM-12 engineering artifacts
CM-13 checkpoints/resume
CM-14 parallel investigators
CM-15 coding-max preset
CM-16 LAM experiment adapter
CM-17 observability/reporting
```

Modify based on actual code dependencies.

---

## 60. Per-Task Implementation Template

For every implementation item provide:

```text
ID
Goal
Current implementation
Gap
Files affected
New files
Protocols
Schemas
Pseudocode
Events
Artifacts
Dependencies
Failure modes
Unit tests
Integration tests
Acceptance criteria
```

---

## 61. Concrete File-Level Plan

The final report must identify exact repository paths.

Example:

```text
vanguard/...
plugins/...
workflows/...
providers/...
tests/...
```

Do not invent paths before inspecting the repository.

For every path explain the modification.

---

## 62. Architecture Decision Rule

Every capability must be assigned to exactly one primary architectural location:

```text
Tool
Plugin
Workflow
Agent Manifest
Context Provider
Evaluator
Policy
Model Adapter
Artifact
Projection
Framework Contract
Kernel
```

Justify any change to the last two categories.

---

## 63. Required Diagrams

Provide Mermaid diagrams for:

1. Coding Max component architecture.
2. Main workflow state machine.
3. Failure/recovery loop.
4. Context pipeline.
5. Model routing.
6. Long-task checkpoint/resume.
7. LDA integration.
8. LAM experiment integration.

---

## 64. Required Final Report

Produce:

```text
AETHER_CODING_MAX_HARNESS_IMPLEMENTATION_SPEC.md
```

The report must contain:

1. Executive summary.
2. Current code assessment.
3. Existing capability matrix.
4. Coding Max architecture.
5. Agent manifest.
6. Workflow protocol.
7. State machine.
8. Task classification.
9. Repository intelligence.
10. LDA integration.
11. Context engineering.
12. Context cache.
13. Planning.
14. TODO management.
15. Worker.
16. Tool execution.
17. Script execution.
18. Patch management.
19. Verification.
20. Failure taxonomy.
21. Retry/recovery.
22. Model routing.
23. Reviewer.
24. Parallel workers.
25. Memory.
26. Artifacts.
27. Checkpoints.
28. Resume.
29. Events.
30. Budgets.
31. Authorization.
32. LAM integration.
33. Meta-harness extension points.
34. Presets.
35. Observability.
36. Performance considerations.
37. Security/isolation.
38. Unit tests.
39. Integration tests.
40. Real smoke tasks.
41. Concrete pseudocode.
42. Protocol definitions.
43. Schema definitions.
44. Exact file modifications.
45. Ordered implementation backlog.
46. Acceptance criteria.
47. Explicit non-goals.

---

## 65. Final Requirement

Do not produce another conceptual research document.

Produce an **implementation specification**.

The developer reading it should be able to go from:

```text
report
```

directly to:

```text
code
```

without needing another architecture review.

Where the current framework already contains an acceptable mechanism, use it.

Where an external project such as Hermes, OpenCode, Claude Code-style harnesses, LDA, or existing AETHER experiments demonstrate a useful mechanism, extract the **behavioral pattern** and implement it through native AETHER contracts.

Do not blindly copy external architecture.

The desired end state is:

```text
AETHER Runtime
      +
Coding Max Composition
      +
Repository Intelligence
      +
Adaptive Context
      +
Planning
      +
Powerful Tool Loop
      +
Real Verification
      +
Failure-Aware Recovery
      +
Adaptive Model Compute
      +
Durable Engineering State
```

resulting in a coding harness capable of sustained, evidence-backed work on difficult repositories while preserving AETHER's small, general, domain-blind substrate.

---

# Alternative Super-Harness Directions

## Coding Swarm

A fundamentally different harness can prioritize **parallel specialization and convergence** rather than a central planner. A bounded topology of `localizer + architecture investigator + test investigator + implementation workers + patch tournament + verifier` explores competing hypotheses and candidate patches in parallel. Shared state is limited to structured artifacts and evidence, authority is attenuated per worker, and the final candidate is selected by deterministic verification. This design trades model-call cost for breadth and robustness on ambiguous or highly distributed repository problems.

## Coding Search Harness

A second alternative can treat software engineering as **bounded search over trajectories** instead of a planner/worker loop. The harness explicitly branches on alternative hypotheses, context sets, patch strategies, or repair actions, producing a small search tree such as `hypothesis → evidence → candidate patch → test outcome`. Branches are scored by verification evidence, remaining budget, regression risk, and progress, with weak branches pruned early and compute concentrated on promising trajectories. The approach resembles beam search, best-first search, or constrained MCTS over engineering states and can be especially valuable when the first plausible reasoning chain frequently leads to local optima.

---

# Principal Engineering Standard

The final implementation should optimize for:

```text
Capability
Correctness
Evidence
Iteration speed
Modularity
Reversibility
Observability
Low coupling
High information gain per model/tool call
```

The kernel should remain minimal. Complexity belongs in configurable outer-layer compositions until evidence demonstrates that a mechanism is universal enough to justify promotion into the framework.

The implementation must prefer real repository state, real tools, real patches, real test execution, and reconstructable evidence over self-reported model success.

The objective is not to build the largest harness. It is to build a harness that **uses additional intelligence only when it increases the probability of completing the engineering task correctly**.
