---
id: benchmarking-v090-full-plan
class: execution-plan
authority: non-authorizing
status: proposed
owner: frontier-product-program
version: "0.1.0"
last_verified: 2026-08-28
framework_mutation_allowed: false
model_lock: deepseek/deepseek-v4-flash-0731
planned_measurements: 27
measured_results_in_this_document: 0
---

# AETHER Vanguard v0.9 Frontier Product Benchmarking Master Plan

## Document contract

This is an implementation-ready plan.

It does not claim that the planned agents exist.

It does not claim that the planned benchmark runs occurred.

It does not assign invented scores.

Every score cell remains `TBD` until supported by a Vanguard ledger trajectory,
an immutable subject digest, a patch or answer artifact, and an exterior oracle.

The program freezes the existing framework.

The implementer may create or modify only solution-layer manifests, prompts,
policies, benchmark fixtures, benchmark drivers, reports, and external adapters
that are already supported through existing ports.

The implementer must not modify the domain, ports, kernel, agency engine,
runtime, or existing adapter contracts during the experiment.

If a run cannot proceed without such a modification, classify the run as
`FRAMEWORK_GAP`, preserve the evidence, and document the proposed change in
`QUICK_WINS_FOR_FRAMEWORK_IMPROVEMENT.MD`.

## Executive decision

AETHER is sufficiently complete to attempt this program as a generic substrate.

The framework already provides:

- Manifest composition.
- Model adapters including OpenRouter.
- Capability-mediated tools.
- Typed budgets.
- Approval policy.
- Context compilation and compaction.
- Recursive delegation.
- SQLite-WAL event storage.
- Artifact storage.
- Trajectory and telemetry capture.
- Exterior evaluation boundaries.
- Resume and replay.
- Failure classification.

The framework does not yet prove that its solution presets are competitive.

This program tests that proposition without moving the framework goalposts.

## Today-delivery requirement

The first product baseline is complete only when all 27 planned rows have a
terminal classification and evidence pointer.

`PASS`, `FAIL`, `INSTRUMENT_ERROR`, `BUDGET_EXHAUSTED`, `PROVIDER_ERROR`, and
`FRAMEWORK_GAP` are all acceptable terminal records.

Blank rows are not acceptable after execution begins.

An unsuccessful but correctly classified run is scientifically useful.

An invented or silently omitted run invalidates the experiment.

## Scope

The program builds eight solution families using the existing framework.

Five are coding harness families.

Three are general agentic product families.

The five coding families are evaluated on one easy, one medium, and one hard
coding challenge.

This produces 15 coding measurements.

The three general agent classes each have a V1 and a V2 preset.

Each preset is evaluated on one easy and one hard challenge.

This produces 12 general-agent measurements.

The total is 27 measurements.

## Non-goals

- Do not modify the framework to improve a score.
- Do not train or fine-tune DeepSeek.
- Do not compare different foundation models in the primary matrix.
- Do not leak reference patches or hidden tests to the model.
- Do not call synthetic model responders empirical model runs.
- Do not report the 27-run projection as an official SWE-bench leaderboard score.
- Do not use a passing untouched fixture as an agent success.
- Do not rerun only failed arms after observing results.
- Do not change challenge selection after seeing outcomes.
- Do not hide provider or approval failures.

## Framework freeze boundary

The following paths are frozen experiment subjects:

```text
vanguard/packages/domain/
vanguard/packages/ports/
vanguard/packages/kernel/
vanguard/packages/agency/episode/
vanguard/packages/agency/context/
vanguard/packages/runtime/
vanguard/packages/adapters/
schemas/
```

The following paths are solution-layer working surfaces:

```text
vanguard/packages/agency/manifests/
benchmarks/frontier_v090/
tools/benchmark-drivers/
BENCHAMRKING_V090_FULL.MD
QUICK_WINS_FOR_FRAMEWORK_IMPROVEMENT.MD
```

Before implementation, compute a deterministic digest over frozen files.

Recompute it before and after every experimental batch.

If the digest changes, invalidate the batch.

Suggested pseudocode:

```python
def framework_digest(root: Path) -> str:
    frozen = [
        "vanguard/packages/domain",
        "vanguard/packages/ports",
        "vanguard/packages/kernel",
        "vanguard/packages/agency/episode",
        "vanguard/packages/agency/context",
        "vanguard/packages/runtime",
        "vanguard/packages/adapters",
        "schemas",
    ]
    rows = []
    for base in frozen:
        for path in sorted((root / base).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                rows.append((path.relative_to(root).as_posix(), sha256(path.read_bytes())))
    return sha256(jcs(rows))
```

## Locked model contract

The primary model is locked to:

```text
deepseek/deepseek-v4-flash-0731
```

Provider is locked to OpenRouter.

Streaming mode must be identical across every arm.

Temperature must be identical across every arm.

Maximum output tokens must be identical across every comparable arm.

Retry policy must be identical across every arm.

Timeout policy must be identical across every arm.

Tool-call translation must be identical across every arm.

No fallback model is allowed in the primary comparison.

If OpenRouter routes to a different model identity, classify the run as
`ROUTE_DRIFT` and do not score it.

The official DeepSeek documentation states that V4 Flash supports tool calls,
JSON output, thinking and non-thinking modes, and a 1M-token context.

The experiment must explicitly record the effective thinking mode.

## Budget contract

Global ceiling:

```text
maximum total tokens = 1,000,000
maximum paid model spend = USD 0.50
maximum planned measurements = 27
```

The first reached ceiling stops new calls.

No row may exceed its per-run reservation.

Recommended initial reservation:

```text
coding easy:      18,000 tokens
coding medium:    28,000 tokens
coding hard:      45,000 tokens
general easy:     12,000 tokens
general hard:     28,000 tokens
```

Raw worst-case reservation exceeds the global ceiling.

Therefore reservations are upper bounds, not allocations.

The controller must check global actual usage before every call.

Recommended stop threshold is 950,000 tokens, preserving 50,000 tokens for
terminal summaries and failure receipts.

Budget pseudocode:

```python
def authorize_call(run, estimate):
    if ledger.total_tokens + estimate.tokens > 950_000:
        return deny("GLOBAL_TOKEN_GUARD")
    if ledger.total_cost_usd + estimate.cost_usd > 0.48:
        return deny("GLOBAL_COST_GUARD")
    if run.calls >= run.max_calls:
        return deny("RUN_CALL_GUARD")
    return reserve(estimate)
```

## Scientific methodology

### Primary question

Holding DeepSeek V4 Flash, tasks, provider, budgets, runtime, tools, and oracle
constant, how much does harness composition alter success, efficiency, and
failure behavior?

### Primary hypothesis

Structured reproduction, evidence-guided localization, surgical patching, and
verification improve resolution rate over a minimal ReAct baseline.

### Null hypothesis

The five coding harnesses have equal probability of resolving the selected
tasks under the same model and budget.

### Unit of analysis

One run is one tuple:

```text
(framework_digest, manifest_digest, model_route, task_digest, seed, budget)
```

### Controlled variables

- Model route.
- Provider.
- Model mode.
- Sampling parameters.
- Challenge bytes.
- Base commit.
- Hidden evaluator.
- Runtime profile.
- Sandbox profile.
- Maximum wall time.
- Global approval mode.
- Network policy.
- Seed where supported.
- Retry policy.
- Report schema.

### Independent variable

The independent variable in the 15-run coding matrix is harness preset.

The independent variable in each V1/V2 general-agent pair is the declared
preset delta.

### Dependent variables

- Binary task success.
- Terminal classification.
- Total tokens.
- Prompt tokens.
- Completion tokens.
- Cached tokens where available.
- USD cost.
- Wall-clock latency.
- Turns.
- API calls.
- Tool calls.
- Approval challenges.
- Failed tool calls.
- Patch attempts.
- Test executions.
- Time to first reproduction.
- Time to first patch.
- Diff size.
- Files changed.
- Regression status.
- Citation precision and recall for non-coding tasks.
- Context growth.
- Compaction count.
- Repeated failure count.

### Randomization

Preregister run order using a deterministic seed.

Interleave harnesses across difficulty to reduce provider-time confounding.

Example order generator:

```python
rng = Random(90090)
runs = preregistered_rows.copy()
rng.shuffle(runs)
write_immutable_order(runs)
```

### Blinding

The model receives only the issue statement, repository, and allowed tools.

The model must never receive hidden tests, reference patch, expected files, or
difficulty label.

The evaluator must not receive the harness prompt or model reasoning.

### Repeat policy

The requested baseline uses one run per row.

This is adequate for product reconnaissance but weak for inference.

Do not compute strong causal claims from one stochastic observation per cell.

If budget remains after all 27 rows terminate, spend it on exact repeats of the
three coding challenges for the baseline and best preset, not on new tasks.

### Multiple-comparison policy

Treat the five-harness matrix as exploratory.

Report raw pairwise differences.

Do not claim statistical significance from 15 binary observations.

Use McNemar only after repeated paired tasks produce enough discordant pairs.

## Eight solution families

### Family C1: Minimal ReAct control

Proposed preset name:

```text
vg-code-v090-react-control
```

Purpose:

Establish the smallest viable coding loop.

Technique:

```text
inspect → edit → test → stop
```

Allowed tools:

- `fs.read`
- `fs.search`
- `patch.apply`
- `proc.exec`

Prompt characteristics:

- Lean.
- No examples.
- No explicit reproduction requirement.
- No critic phase.
- No subagent delegation.
- No candidate branching.

Expected strength:

Low token overhead on easy localized tasks.

Expected weakness:

Premature editing and weak recovery on ambiguous failures.

Primary comparison role:

Negative control.

### Family C2: Claude-shaped evidence loop

Proposed preset name:

```text
vg-code-v090-claude-shaped
```

Purpose:

Test concise inspect-before-edit behavior with result eviction and permissive
local autonomy.

Technique:

```text
read/grep → formulate plan → minimal edit → focused test → regression test
```

Key ideas adopted from official Claude Code guidance:

- Keep the main context for tightly coupled iterative work.
- Delegate only self-contained, verbose exploration.
- Use fresh context for isolated subagents.
- Preserve concise summaries at handoff boundaries.
- Distinguish hook/instrument failures from task failures.

V0.9 baseline should remain single-agent unless existing `agent.spawn` is
already exposed by the manifest contract.

Do not add a framework feature merely to imitate Claude Code.

### Family C3: OpenCode-shaped permission-minimal agent

Proposed preset name:

```text
vg-code-v090-opencode-shaped
```

Purpose:

Test explicit tool vocabulary, narrow permissions, and aggressive result
compaction.

Technique:

```text
explore read-only → enter build mode → edit → test → recover doom loop
```

Key ideas adopted from OpenCode documentation:

- Agent equals prompt plus model preference plus tool permissions.
- Read-only exploration and write-enabled construction are distinct roles.
- Deny irrelevant tools.
- Treat repeated identical action patterns as a doom loop.
- Compact maintenance context separately from task context.

The framework already represents prompt, tools, capabilities, context policy,
and approval policy declaratively.

Therefore this family should require manifest work only.

### Family C4: LEX deterministic surgical agent

Proposed preset name:

```text
vg-code-v090-lex-surgical
```

Purpose:

Test a compiler-like repair pipeline using existing Vanguard tools.

Technique:

```text
MAP
→ REPRODUCE
→ DIAGNOSE
→ SURGICAL PATCH
→ FOCUSED VERIFY
→ REGRESSION VERIFY
→ SANITIZE
```

LEX ideas permitted at the preset level:

- Explicit phase protocol.
- Head/tail preservation instructions.
- Minimal patch requirement.
- Reproduction before patch.
- State-hash anti-thrashing instruction.
- Final diff audit.

LEX ideas not permitted unless already exposed by existing Vanguard ports:

- New Tree-sitter indexer.
- New fuzzy patch engine.
- New sandbox implementation.
- New mutation engine.
- New VRAM scheduler.

Missing capabilities become framework-gap findings.

### Family C5: LIM hypothesis-and-falsification agent

Proposed preset name:

```text
vg-code-v090-lim-falsifier
```

Purpose:

Test whether explicit competing hypotheses and dead-end tracking improve hard
task performance without adding new runtime machinery.

Technique:

```text
repository map
→ generate 2–3 root-cause hypotheses
→ select cheapest discriminating experiment
→ run experiment
→ update hypothesis scores
→ patch best-supported cause
→ falsify patch with focused and regression tests
```

LIM ideas permitted at the preset level:

- Competing hypothesis ledger in model-visible text.
- Reproducer-first workflow.
- Dead-end tracking.
- Causal-slice language.
- Verification reward language.
- Bounded candidate generation.

LIM ideas not permitted unless already exposed:

- Actual SBFL instrumentation.
- Actual concolic execution.
- Actual CEGIS.
- Actual MCTS tree executor.
- Actual mutation testing.

The prompt must not falsely claim those tools exist.

### Family G1: Code and documentation tutor

Product class:

```text
RAG / knowledge-graph explainer
```

Preset V1:

```text
vg-tutor-v090-v1-read-search
```

Preset V2:

```text
vg-tutor-v090-v2-evidence-graph
```

V1 behavior:

- Read-only.
- Search and read files.
- Answer with file and line citations.
- Explicitly separate fact from inference.

V2 delta:

- Build a temporary evidence graph in context.
- Nodes represent files, symbols, requirements, decisions, and runtime events.
- Edges represent imports, calls, governs, emits, persists, and verifies.
- Require two-source corroboration for architectural claims.
- Produce a compact hierarchy before deep explanation.
- Track unanswered questions.

Important limitation:

The current manifest has read/search retrieval, not proven dense-vector RAG or
a persistent knowledge graph.

V2 may emulate an evidence graph in context.

It must not claim semantic-vector retrieval unless an existing IndexPort-backed
adapter is actually composed without framework modification.

### Family G2: Internet research agent

Product class:

```text
deep researcher
```

Preset V1:

```text
vg-research-v090-v1-local
```

Preset V2:

```text
vg-research-v090-v2-web-corroborated
```

V1 behavior:

- Read-only local research.
- Search repository documents.
- Produce evidence-backed synthesis.

V2 delta:

- Decompose question into subqueries.
- Search web and local sources.
- Prefer primary sources.
- Record claim-to-source mappings.
- Require corroboration for material claims.
- Track publication date and event date separately.
- Return unresolved contradictions.

Framework edge:

The current `vg-research-minimal` manifest exposes only `fs.read` and
`fs.search`.

It cannot perform real internet research from prompt design alone.

Before implementation, inspect whether an existing web-search adapter is
available through a declared port and can be composed as a solution plugin.

If not, the hard V2 run must be classified `FRAMEWORK_GAP`.

Do not smuggle an out-of-band web client into the benchmark driver and call it
a Vanguard research agent.

### Family G3: Simple issue fixer

Product class:

```text
bounded simple bugfixer
```

Preset V1:

```text
vg-bugfix-v090-v1-direct
```

Preset V2:

```text
vg-bugfix-v090-v2-reproduce-verify
```

V1 behavior:

- Read named files.
- Apply one minimal patch.
- Run one focused test.

V2 delta:

- Reproduce first.
- State root-cause hypothesis.
- Apply minimal patch.
- Run focused test.
- Run regression suite.
- Inspect final diff.
- Refuse success without changed source and passing oracle.

This class intentionally overlaps coding harness behavior.

Its tasks are smaller and its budget is lower.

The purpose is product usability, not frontier benchmark optimization.

## Manifest construction rules

Every new preset must be a declarative composition.

Each manifest must include:

- Unique harness identifier.
- System prompt component.
- Tool schema components.
- Context policy.
- Routing policy.
- Approval policy.
- Budget policy.
- Capabilities.
- Evaluators where applicable.
- `undeletable: false`.

Manifest pseudocode:

```json
{
  "harness": "vg-code-v090-lim-falsifier",
  "components": {
    "system_prompt": ["vg-code-v090-lim-falsifier/system-prompt.txt"],
    "tools": [
      "vg-code-default/read-tool.json",
      "vg-code-default/search-tool.json",
      "vg-code-lex/surgical-patch-tool.json",
      "vg-code-default/test-tool.json"
    ],
    "context_policy": ["vg-code-v090-lim-falsifier/context-policy.json"],
    "routing_policy": ["vg-code-v090-common/deepseek-lock.json"],
    "approval_policy": ["vg-code-v090-common/benchmark-approval.json"]
  },
  "capabilities": [],
  "evaluators": ["coding-oracle@3"],
  "budgetPolicy": "vg-code-v090-lim-falsifier/budget-policy.json",
  "undeletable": false
}
```

Do not copy capabilities blindly.

Every declared tool verb must have a matching capability.

Every capability must be needed by the solution.

Tutor and research presets must remain read-only unless the challenge explicitly
requires producing an artifact file.

## Prompt engineering rules

OpenAI’s official model guidance reports directional gains from leaner prompts
and recommends removing one instruction or tool group at a time on representative
evals.

Apply that principle even though the locked model is DeepSeek.

State each instruction once.

Keep tool descriptions short and exact.

Do not claim unavailable tools.

Do not inject reference answers.

Do not include benchmark-specific expected filenames beyond the public issue.

Define success operationally.

Define failure operationally.

Define autonomy once.

Define approval boundaries once.

Require evidence, not role-played confidence.

## Coding challenge selection

Select exactly three public tasks before any model run.

Difficulty must be based on human-estimated effort and structural features,
not on observed model success.

### Easy coding challenge criteria

- One repository.
- One or two likely source files.
- Deterministic tests.
- Localized behavioral defect.
- No network dependency.
- Expected human effort under 30 minutes.

### Medium coding challenge criteria

- Two to five relevant source files.
- Ambiguous localization.
- At least one interaction boundary.
- Focused and regression tests.
- Expected human effort 30–120 minutes.

### Hard coding challenge criteria

- Five or more relevant files or broad call graph.
- Long issue statement or large repository context.
- Multiple plausible root causes.
- Regression-sensitive behavior.
- Expected human effort over two hours.

### Official-source preference

Preference order:

1. SWE-bench Verified official instance.
2. SWE-bench Pro public instance with current valid evaluator.
3. Repository-owned SWE-like hermetic challenge.

If option 3 is used, the report must say `SWE-LIKE`, not `SWE-VERIFIED` or
`SWE-PRO`.

### Task validity audit

For every selected task, verify:

- Base commit resolves.
- Repository license allows evaluation.
- Build succeeds before patch where expected.
- `FAIL_TO_PASS` fails before patch.
- `PASS_TO_PASS` passes before patch.
- Hidden tests do not require future dates or unavailable services.
- Reference patch is not exposed to agent context.
- Challenge is not already solved in the fixture.
- Evaluator can distinguish no-op from valid patch.

## General-agent challenge selection

### Tutor easy challenge

Explain one bounded execution path across at most five files.

Required output:

- Summary.
- Ordered call path.
- File/line citations.
- One stated uncertainty.

### Tutor hard challenge

Explain the full dispatch-to-ledger-to-evaluation lifecycle across law,
decisions, runtime, adapters, and evidence.

Target context should exceed 50,000 source characters.

Required output:

- Architecture hierarchy.
- Causal sequence.
- Requirement-to-code mapping.
- Contradiction detection.
- At least ten checked citations.

### Research easy challenge

Research one narrow question such as official SWE-bench evaluation protocol.

Required output:

- Three primary sources.
- Claim/source matrix.
- Dates.
- Concise synthesis.

### Research hard challenge

Research current coding-agent harness techniques across official SWE-bench,
Claude Code, Codex, OpenCode, OpenHands, DeepSeek, LIM, and LEX.

Required output:

- Query decomposition.
- At least eight sources.
- At least five primary sources.
- Contradiction analysis.
- Applicability matrix for Vanguard.
- Explicit framework-versus-solution classification.

### Simple bugfix easy challenge

One deterministic defect in one file with a focused test.

### Simple bugfix hard challenge

One multi-file but bounded defect with at least one regression trap.

## Complete preregistered 27-run matrix

No score below is measured.

`TBD` means the implementer must execute and attach evidence.

| Run | Class | Preset | Difficulty | Challenge slot | Model | Planned score | Status |
|---:|---|---|---|---|---|---|---|
| 01 | Coding | C1 ReAct control | Easy | CODE-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 02 | Coding | C1 ReAct control | Medium | CODE-M | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 03 | Coding | C1 ReAct control | Hard | CODE-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 04 | Coding | C2 Claude-shaped | Easy | CODE-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 05 | Coding | C2 Claude-shaped | Medium | CODE-M | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 06 | Coding | C2 Claude-shaped | Hard | CODE-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 07 | Coding | C3 OpenCode-shaped | Easy | CODE-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 08 | Coding | C3 OpenCode-shaped | Medium | CODE-M | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 09 | Coding | C3 OpenCode-shaped | Hard | CODE-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 10 | Coding | C4 LEX surgical | Easy | CODE-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 11 | Coding | C4 LEX surgical | Medium | CODE-M | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 12 | Coding | C4 LEX surgical | Hard | CODE-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 13 | Coding | C5 LIM falsifier | Easy | CODE-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 14 | Coding | C5 LIM falsifier | Medium | CODE-M | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 15 | Coding | C5 LIM falsifier | Hard | CODE-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 16 | Tutor | G1 V1 read/search | Easy | TUTOR-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 17 | Tutor | G1 V1 read/search | Hard | TUTOR-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 18 | Tutor | G1 V2 evidence graph | Easy | TUTOR-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 19 | Tutor | G1 V2 evidence graph | Hard | TUTOR-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 20 | Research | G2 V1 local | Easy | RESEARCH-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 21 | Research | G2 V1 local | Hard | RESEARCH-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 22 | Research | G2 V2 web corroborated | Easy | RESEARCH-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 23 | Research | G2 V2 web corroborated | Hard | RESEARCH-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 24 | Bugfix | G3 V1 direct | Easy | BUG-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 25 | Bugfix | G3 V1 direct | Hard | BUG-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 26 | Bugfix | G3 V2 reproduce/verify | Easy | BUG-E | DeepSeek V4 Flash 0731 | TBD | PLANNED |
| 27 | Bugfix | G3 V2 reproduce/verify | Hard | BUG-H | DeepSeek V4 Flash 0731 | TBD | PLANNED |

## Scoring model

### Coding score

Binary resolution is authoritative.

```text
resolved =
    runtime_terminal_completed
    AND source_patch_nonempty
    AND FAIL_TO_PASS_passes
    AND PASS_TO_PASS_passes
    AND evaluator_infrastructure_valid
```

No partial credit enters projected SWE resolution.

Diagnostic subscores may be reported separately.

### Tutor score

Use a 100-point rubric:

```text
factual correctness             30
citation precision              20
citation recall                 15
execution-path completeness     15
uncertainty calibration         10
clarity and hierarchy           10
```

Pass threshold:

```text
easy >= 80
hard >= 75
```

### Research score

Use a 100-point rubric:

```text
claim correctness               25
primary-source quality          20
citation entailment             20
coverage                        15
contradiction handling          10
date discipline                  5
actionability                     5
```

Pass threshold:

```text
easy >= 80
hard >= 75
```

### Simple bugfix score

Use the same binary oracle as coding.

Also report:

- Patch minimality.
- Reproduction success.
- Regression result.
- Turns.
- Cost.

## KPI schema

### Required raw KPIs

- `run_id`
- `episode_id`
- `framework_digest`
- `manifest_digest`
- `task_digest`
- `model_requested`
- `model_returned`
- `provider`
- `model_fingerprint`
- `started_at`
- `ended_at`
- `wall_seconds`
- `turns`
- `api_calls`
- `prompt_tokens`
- `completion_tokens`
- `cached_tokens`
- `total_tokens`
- `usd_micros`
- `tool_calls_total`
- `tool_calls_failed`
- `approval_challenges`
- `patch_attempts`
- `test_executions`
- `files_changed`
- `diff_lines_added`
- `diff_lines_removed`
- `terminal`
- `instrument_error`
- `oracle_result`
- `failure_taxonomy`

### Derived KPIs

Effective Token Utilization Rate:

```text
ETUR = useful_evidence_tokens / total_tokens
```

Prefix Cache Stability Ratio:

```text
PCSR = cached_prompt_tokens / prompt_tokens
```

Surgical Patch Density Index:

```text
SPDI = task_relevant_changed_lines / total_changed_lines
```

Time to First Reproduction:

```text
TTFR = timestamp(first_confirmed_failure) - start_time
```

Time to First Patch:

```text
TTFP = timestamp(first_source_patch) - start_time
```

Self-Correction Velocity:

```text
SCV = recovered_failed_attempts / recovery_turns
```

Dead-End Avoidance Efficiency:

```text
DEAE = 1 - repeated_identical_failures / max(1, total_failures)
```

Tool Reliability:

```text
TR = successful_tool_calls / max(1, tool_calls_total)
```

Cost per Resolved Task:

```text
CPR = total_cost / resolved_tasks
```

Token Cost per Resolved Task:

```text
TPR = total_tokens / resolved_tasks
```

Pareto utility:

```text
PU = resolved / (alpha * normalized_cost
               + beta * normalized_latency
               + gamma * normalized_tokens)
```

Do not use Pareto utility to turn a failed task into a success.

## Failure taxonomy

### TASK_LOCALIZATION_FAILURE

Agent never identifies relevant code.

### REPRODUCTION_FAILURE

Agent cannot reproduce the public failure.

### WRONG_HYPOTHESIS

Agent edits a non-causal location.

### PATCH_FORMAT_FAILURE

Patch is malformed or does not apply.

### PATCH_SEMANTIC_FAILURE

Patch applies but fails target tests.

### REGRESSION_FAILURE

Target test passes but existing tests regress.

### NO_PATCH

Run terminates without changed source.

### PREMATURE_COMPLETION

Agent claims completion without oracle evidence.

### APPROVAL_LOOP

Repeated approvals consume turns without progress.

### CONTEXT_EXHAUSTION

Required evidence is evicted or token ceiling is reached.

### DOOM_LOOP

Agent repeats materially identical failed actions.

### PROVIDER_ERROR

Provider request fails after bounded retry.

### MODEL_PROTOCOL_ERROR

Model returns neither valid text nor valid tool call.

### ROUTE_DRIFT

Returned model identity violates model lock.

### INSTRUMENT_ERROR

Harness cannot produce a valid measurement.

### ORACLE_ERROR

Evaluator is missing, inconsistent, or cannot run.

### DATASET_DEFECT

Task is broken, underspecified, or evaluator rejects valid behavior.

### FRAMEWORK_GAP

Required generic capability cannot be composed through existing framework.

## Run lifecycle pseudocode

**MANDATORY: RUN `MAKE CLEAN-BENCHMARK-CACHE` FROM THE FRESH BENCHMARK WORKSPACE BEFORE EVERY BENCHMARK ROW. NEVER REUSE PYTHON BYTECODE CACHE STATE BETWEEN ROWS. CACHE CLEANUP MUST HAPPEN BEFORE THE SUBJECT SNAPSHOT.**

The benchmark driver must invoke `make clean-benchmark-cache` for each newly
provisioned workspace and record the command result in that row's evidence. The
target removes only `__pycache__`, `.pyc`, and `.pyo` artifacts.

```python
def execute_preregistered_run(spec):
    assert framework_digest() == prereg.framework_digest
    assert spec.model == "deepseek/deepseek-v4-flash-0731"
    assert spec.task_digest == digest_task(spec.task)

    workspace = provision_clean_subject(spec)
    baseline = snapshot(workspace)
    baseline_oracle = validate_baseline(spec, workspace)
    if not baseline_oracle.instrument_valid:
        return terminal("ORACLE_ERROR")

    reservation = global_budget.reserve(spec.max_budget)
    if not reservation.ok:
        return terminal("BUDGET_EXHAUSTED")

    result = Vanguard.execute_profiled(
        manifest=spec.manifest,
        model=locked_model,
        task=spec.public_brief,
        repo_path=workspace,
        budget=reservation,
        profile="sandboxed",
    )

    patch = diff(baseline, workspace)
    verdict = exterior_evaluator(spec, patch)
    row = bind_result(spec, result, patch, verdict)
    ledger.append(row)
    assert cold_reconstruct(row.run_id) == row
    return row
```

## Coding-agent prompt skeleton

```text
You are solving a repository issue under a fixed budget.

Success requires a real source patch and passing evaluator tests.

Use exactly one tool call per turn.

Inspect evidence before editing.

Run the narrowest useful experiment.

Keep changes minimal and compatible.

Do not modify tests or benchmark metadata.

Do not claim success without test output.

If an action fails, change the hypothesis or experiment before repeating it.

Finish by reporting changed files and verification commands.
```

Each family changes only its declared technique section.

Common safety, success, tools, model, and budget text remains byte-identical.

## Tutor V2 evidence-graph pseudocode

```python
graph = EvidenceGraph()
for query in decompose(user_question):
    hits = search(query)
    for hit in hits:
        excerpt = read_bounded(hit.path, hit.lines)
        node = graph.add_evidence(hit.path, hit.lines, excerpt)
        for symbol in extract_symbols(excerpt):
            graph.link(node, symbol, relation="declares_or_uses")

claims = synthesize_claims(graph)
for claim in claims:
    claim.status = corroborate(claim, minimum_sources=2)

return render(claims, citations=True, uncertainties=True)
```

This graph is an episode artifact unless a persistent graph adapter already
exists through the current framework.

## Research V2 pseudocode

```python
subqueries = decompose(question, max_queries=8)
evidence = []
for query in subqueries:
    results = web_search(query)
    for result in rank_primary_sources(results)[:3]:
        page = fetch(result)
        evidence.append(extract_claims(page))

matrix = map_claims_to_sources(evidence)
matrix = detect_contradictions(matrix)
matrix = separate_fact_inference(matrix)
return synthesize(matrix, include_dates=True, include_gaps=True)
```

If `web_search` and `fetch` cannot be composed through existing Vanguard ports,
do not implement this pseudocode out of band.

Record `FRAMEWORK_GAP`.

## Bugfix V2 pseudocode

```python
target = inspect_issue_and_named_files()
failure = run_focused_reproducer(target)
assert failure.reproduced

hypothesis = explain_root_cause(failure, code_evidence)
patch = apply_minimal_patch(hypothesis)

focused = run_focused_test()
if not focused.pass:
    revise_once(focused)

regression = run_regression_suite()
diff = inspect_final_diff()

return success_if(
    focused.pass
    and regression.pass
    and diff.source_changes
    and not diff.test_changes
)
```

## Benchmark-driver requirements

The driver must use the real public runtime entrypoint.

The driver must not fabricate responses.

The driver must not substitute default token values when telemetry is absent.

Missing telemetry is `null` plus a reason.

The driver must select a manifest without patching framework code.

The repository already exposes a pack-selecting runtime lab driver.

Prefer that path over the hardcoded SWE challenge runner.

The driver must provision a fresh workspace per run.

The driver must keep hidden tests outside model-readable workspace.

The driver must capture source snapshot before execution.

The driver must reject no-op success.

The driver must kill descendants on timeout.

The driver must write immutable report files.

The driver must preserve failed reports.

## Evidence schema

```json
{
  "schema": "aether.frontier-benchmark/1",
  "run_id": "...",
  "preregistration_digest": "sha256:...",
  "framework_digest": "sha256:...",
  "manifest_digest": "sha256:...",
  "task_digest": "sha256:...",
  "model_requested": "deepseek/deepseek-v4-flash-0731",
  "model_returned": "...",
  "provider": "openrouter",
  "terminal": "...",
  "failure_taxonomy": [],
  "telemetry": {},
  "patch": {
    "digest": "sha256:...",
    "files": [],
    "lines_added": 0,
    "lines_removed": 0
  },
  "oracle": {
    "instrument_valid": true,
    "fail_to_pass": false,
    "pass_to_pass": false
  },
  "trajectory_digest": "sha256:..."
}
```

## Per-run failure report template

```markdown
### Run XX — preset / challenge

Status:

Model route:

Manifest digest:

Task digest:

Framework digest:

Observed terminal:

Oracle result:

Changed files:

Tokens / cost / time / turns / calls:

Last successful stage:

First causal failure:

Failure taxonomy:

Evidence:

Why the task failed:

What can be improved in the preset:

What can be improved in benchmark instrumentation:

Does this imply a framework gap:

Suggested next experiment:
```

## Projection methodology

The 15 coding observations may produce a local projected score.

They do not produce an official SWE-bench Verified or Pro score.

For each coding preset:

```text
local_resolution = solved_tasks / 3
```

This estimator has extreme uncertainty.

Report the Wilson interval for three Bernoulli observations.

Do not hide that the interval is wide.

Suggested projection model:

```text
Projected Verified = weighted local resolution × calibration factor
Projected Pro      = weighted local resolution × difficulty transfer factor
```

Calibration factors must come from a preregistered mapping between selected
tasks and official benchmark difficulty distributions.

Without that mapping, report only scenario ranges.

Example scenario labels:

- Pessimistic.
- Central.
- Optimistic.

Never report a single percentage without its assumptions and interval.

Recommended language:

```text
This 27-run kit estimates product readiness on a curated sample.
It is not statistically representative of the 500-instance Verified set or
the full SWE-bench Pro distribution.
```

## Statistical analysis plan

For binary coding outcomes:

- Report count and proportion.
- Report Wilson 95% interval.
- Report exact task-by-task outcomes.
- Report macro-average across difficulties.
- Report difficulty-stratified outcomes.

For continuous KPIs:

- Report median.
- Report mean.
- Report standard deviation only when repeats exist.
- Report minimum and maximum.
- Report null values explicitly.

For paired preset comparisons:

- Use task-level paired differences.
- Use McNemar only with adequate discordant pairs.
- Use bootstrap intervals only after enough repeated runs.
- Avoid ranking ties by arbitrary decimals.

For tutor and research rubrics:

- Use two independent graders where possible.
- Blind graders to preset identity.
- Resolve disagreements with an adjudicator.
- Record rubric item scores, not only totals.

## Scoreboard template

| Preset | Easy | Medium | Hard | Resolved | Tokens | Cost | Median time | Primary failure |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| C1 ReAct | TBD | TBD | TBD | TBD/3 | TBD | TBD | TBD | TBD |
| C2 Claude-shaped | TBD | TBD | TBD | TBD/3 | TBD | TBD | TBD | TBD |
| C3 OpenCode-shaped | TBD | TBD | TBD | TBD/3 | TBD | TBD | TBD | TBD |
| C4 LEX surgical | TBD | TBD | TBD | TBD/3 | TBD | TBD | TBD | TBD |
| C5 LIM falsifier | TBD | TBD | TBD | TBD/3 | TBD | TBD | TBD | TBD |

## General-agent scoreboard template

| Class | Preset | Easy score | Hard score | Passes | Tokens | Cost | Evidence quality | Primary failure |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Tutor | V1 | TBD | TBD | TBD/2 | TBD | TBD | TBD | TBD |
| Tutor | V2 | TBD | TBD | TBD/2 | TBD | TBD | TBD | TBD |
| Research | V1 | TBD | TBD | TBD/2 | TBD | TBD | TBD | TBD |
| Research | V2 | TBD | TBD | TBD/2 | TBD | TBD | TBD | TBD |
| Bugfix | V1 | TBD | TBD | TBD/2 | TBD | TBD | TBD | TBD |
| Bugfix | V2 | TBD | TBD | TBD/2 | TBD | TBD | TBD | TBD |

## Framework usefulness decision rule

Classify the framework as `GENERICALLY_USEFUL` if:

- All eight solution families compose without frozen-layer changes.
- Coding, tutor, and bugfix classes complete at least one valid run each.
- Research V2 either completes through a legitimate composed web capability or
  yields a precise framework-gap record.
- Ledger reconstruction preserves every terminal result.
- Metrics are not fabricated.
- Failure types are distinguishable.

Classify the framework as `USEFUL_BUT_PRODUCT_INCOMPLETE` if:

- Core execution and evidence work.
- One or more solution classes cannot reach useful quality.
- Gaps are confined to manifests, tools, adapters, datasets, or product UX.

Classify the framework as `FRAMEWORK_BLOCKED` if:

- Manifests cannot express required tool/capability composition.
- The runtime cannot select the requested preset through a public entrypoint.
- The ledger cannot bind model, manifest, task, patch, and oracle.
- Budget enforcement cannot prevent overspend.
- Long-horizon continuation loses causal state.

Do not call the framework useless merely because DeepSeek fails a task.

Do not call it useful merely because events were written.

Generic usefulness requires multiple domain solutions to execute through the
same unchanged substrate.

## Framework-gap escalation protocol

When a potential framework gap appears:

1. Stop that run.
2. Preserve trajectory and workspace digest.
3. Confirm the capability is not already available.
4. Attempt a manifest-only composition.
5. Attempt an existing-plugin composition.
6. Confirm the same blocker on three controlled attempts before declaring a
   persistent framework gap.
7. Record exact missing port, runtime seam, or contract.
8. Propose the smallest change.
9. Define a falsifier that would prove the change unnecessary or wrong.
10. Do not implement it during the frozen experiment.

## Likely framework-edge questions

- Can manifests select all required tools without runtime edits?
- Can model identity be locked despite routing policy fields?
- Can benchmark mode auto-approve bounded local writes without turn waste?
- Can research agents access web capabilities through existing ports?
- Can a tutor retrieve large contexts without dense indexing?
- Can `agent.spawn` be exposed declaratively to solution presets?
- Can child artifacts return by digest without custom runtime wiring?
- Can hidden evaluator tests remain inaccessible to the worker?
- Can cost telemetry be trusted when provider omits pricing?
- Can malformed DeepSeek tool calls be classified and repaired externally?
- Can context compaction preserve tool-call protocol history?
- Can official Docker evaluators coexist with Vanguard sandbox profiles?

## Known repository findings before execution

The repository already contains five relevant coding-style presets:

- `vg-code-default`
- `vg-code-swe-mini`
- `vg-code-claude-shaped`
- `vg-code-opencode-shaped`
- `vg-code-lex`

The repository already contains:

- `vg-code-explain`
- `vg-research-minimal`
- `vg-code-critic-reviser`

These are starting materials, not validated products.

The existing `agentic_harness_matrix_benchmark.py` includes a synthetic response
generator.

It must not be used as empirical DeepSeek evidence.

The real runtime lab driver already accepts a pack name.

Use that public path or a thin external wrapper around it.

One SWE challenge runner currently hardcodes `vg-code-default`.

Do not modify the runtime to fix that.

Use the pack-selecting driver for comparative experiments.

## External research findings

Official SWE-bench uses containerized evaluation for reproducibility.

SWE-bench Verified contains human-screened tasks and difficulty annotations.

SWE-bench Pro targets longer-horizon, multi-file, enterprise-like work.

The public SWE-bench Pro repository documents Docker or Modal evaluation.

Recent OpenAI research estimates a significant fraction of SWE-bench Pro tasks
may be broken.

Therefore every selected Pro task needs a local validity audit.

OpenHands CodeAct demonstrates the value of a general action space centered on
code execution and shell interaction.

Agentless demonstrates localization, repair, validation, and selection as
separable stages.

Claude Code documentation emphasizes choosing subagents for self-contained
work and preserving the main context for tightly coupled iteration.

OpenCode represents agents as prompts, models, and permission sets, closely
matching Vanguard’s declarative manifest direction.

OpenAI’s official guidance recommends lean prompts, relevant tools only, and
representative evals when changing agent instructions.

DeepSeek’s official documentation confirms V4 Flash supports tool calls and a
large context, but long context does not replace retrieval discipline.

## Source register

- AETHER repository `README.md`.
- AETHER active execution board.
- AETHER manifest catalog and component files.
- AETHER benchmark drivers.
- LIM README, experiment matrix, context engine, and KPI telemetry.
- LEX README and engine module inventory.
- Official SWE-bench repository: https://github.com/SWE-bench/SWE-bench
- SWE-bench paper: https://arxiv.org/abs/2310.06770
- SWE-bench Pro repository: https://github.com/scaleapi/SWE-bench_Pro-os
- SWE-bench Pro paper: https://arxiv.org/abs/2509.16941
- OpenAI SWE-bench Verified article: https://openai.com/index/introducing-swe-bench-verified/
- OpenAI coding-evaluation audit: https://openai.com/index/separating-signal-from-noise-coding-evaluations/
- OpenAI model guidance: https://developers.openai.com/api/docs/guides/latest-model
- DeepSeek models and pricing: https://api-docs.deepseek.com/quick_start/pricing/
- DeepSeek tool calls: https://api-docs.deepseek.com/guides/tool_calls/
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code hooks: https://code.claude.com/docs/en/hooks-guide
- OpenCode agents: https://opencode.ai/v2/docs/agents
- OpenCode permissions: https://opencode.ai/v2/docs/permissions
- OpenHands CodeAct: https://www.openhands.dev/blog/openhands-codeact-21-an-open-state-of-the-art-software-development-agent
- Agentless SWE-bench workflow: https://github.com/OpenAutoCoder/Agentless/blob/main/README_swebench.md

## Implementation sequence

### Phase 0: Freeze and preregister

- Capture repository commit and dirty-state digest.
- Capture framework digest.
- Freeze selected tasks.
- Freeze hidden evaluator digests.
- Freeze run order.
- Freeze model parameters.
- Freeze budgets.
- Freeze score rubrics.
- Freeze report schema.

Exit gate:

```text
all preregistration artifacts immutable and digest-addressed
```

### Phase 1: Validate existing preset surfaces

- Compose every existing candidate preset.
- Verify declared tools resolve.
- Verify aliases resolve.
- Verify capabilities cover verbs.
- Verify read-only presets cannot write.
- Verify budgets parse.
- Verify context policies parse.
- Verify routing does not override model lock.

Exit gate:

```text
all candidate presets compose or have documented solution-layer defects
```

### Phase 2: Implement missing solution presets

- Create C1 through C5 final experimental presets.
- Create Tutor V1/V2.
- Create Research V1/V2.
- Create Bugfix V1/V2.
- Reuse shared components where byte identity is part of control.
- Register presets.
- Add manifest tests.

Exit gate:

```text
all eleven concrete preset variants compose through unchanged framework
```

There are eight product families but eleven concrete variants because the
three general families each have V1 and V2.

### Phase 3: Build external benchmark kit

- Provision three coding tasks.
- Provision six general-agent challenge slots.
- Keep hidden evaluators outside workspaces.
- Implement immutable snapshots.
- Implement report schema.
- Implement budget controller.
- Implement run-order loader.
- Implement cold reconstruction check.

Exit gate:

```text
all fixtures fail/pass their expected baseline checks without model calls
```

### Phase 4: Dry run without paid model

- Use deterministic cassette only to validate orchestration.
- Do not include dry-run scores in final matrix.
- Confirm every row reaches a terminal record.
- Confirm timeout cleanup.
- Confirm no-op rejection.
- Confirm budget denial.
- Confirm report immutability.

Exit gate:

```text
27 orchestration rows structurally valid with zero empirical score claims
```

### Phase 5: Live DeepSeek execution

- Load `.env` without printing secret values.
- Verify requested model availability.
- Execute preregistered randomized order.
- Check global budget before every call.
- Preserve every run artifact.
- Never overwrite failed reports.
- Stop at ceiling.

Exit gate:

```text
27 rows terminal or explicit global-budget stop with preserved partial matrix
```

The user requirement expects all 27 terminal rows.

Therefore per-run budgets should be tuned during dry run, before model calls,
so the global budget can cover the complete matrix.

### Phase 6: Evaluation and grading

- Run official coding evaluators.
- Grade tutor outputs blind.
- Grade research outputs blind.
- Bind scores to artifacts.
- Compute KPIs.
- Compute uncertainty.
- Classify failures.

Exit gate:

```text
every row has score, terminal, KPI record, and evidence link
```

### Phase 7: Product decision

- Rank presets by resolution first.
- Break ties by regression safety.
- Then compare cost, tokens, and latency.
- Identify easiest production win.
- Identify framework gaps.
- Write next experiment.

Exit gate:

```text
one coding default candidate and one candidate per general product class
```

## Definition of done

- Framework digest unchanged.
- Eight solution families specified.
- Eleven concrete presets implemented by the future developer.
- Exactly 27 planned rows executed by the future developer.
- Model locked to DeepSeek V4 Flash 0731.
- Total use within 1M tokens and USD 0.50.
- Every row terminal.
- Every score evidence-backed.
- Every failure analyzed.
- Projection caveats explicit.
- Framework gaps separated from preset gaps.
- Quick-win report produced if needed.
- No official benchmark claim without official evaluator evidence.

## Final instruction to the implementing developer

You have full authority to modify solution presets, prompts, policies,
benchmark fixtures, external benchmark drivers, reports, and tests for those
surfaces.

You do not have authority to modify the frozen framework during this program.

If a material finding indicates the framework should change, stop that run,
record the benchmark proof, research primary-source alternatives, and write the
finding to `QUICK_WINS_FOR_FRAMEWORK_IMPROVEMENT.MD` with:

- Symptom.
- Reproduction.
- Evidence.
- Affected frozen path.
- Why a manifest/plugin cannot solve it.
- Minimal proposed framework change.
- Security and compatibility impact.
- Required ADR or specification update.
- Falsifier.
- Expected benchmark gain.
- Cost and migration plan.

Do not implement the framework change until the frozen 27-run program is closed
or formally aborted.

The purpose is not to manufacture a high score.

The purpose is to discover whether AETHER can host multiple useful agentic
products through one unchanged substrate, measure where it succeeds, and make
every limitation actionable.
