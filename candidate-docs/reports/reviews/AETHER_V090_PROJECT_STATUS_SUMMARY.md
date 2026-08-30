# AETHER / Vanguard v0.9.0 — Consolidated Project Status, Benchmark Results, Failures, and Forward Ideas

**Document type:** consolidated technical status report  
**Scope:** latest supplied project-status and benchmark reports  
**Snapshot basis:** August 29, 2026 reports  
**Purpose:** summarize what was built, what was tested, what worked, what failed, what was fixed, what remained open, and which future ideas emerged  
**Important:** this document consolidates the supplied reports; it is **not a fresh verification of the repository after those reports were written**.

---

# 1. Executive Summary

AETHER/Vanguard reached a meaningful engineering milestone: the project is no longer only an architectural substrate. It has a working benchmark harness, real OpenRouter model execution, durable SQLite-WAL event traces, content-addressed artifacts, exterior benchmark oracles, multiple agent manifests, and enough observability to diagnose failures at the exact turn/tool/context level.

The strongest result of this period was therefore not the benchmark score itself. It was that the system became sufficiently instrumented to reveal **why** agents were failing.

The architecture remained structurally healthy in the supplied snapshot:

- the hexagonal dependency lattice remained intact;
- the TCB remained below its LOC ceiling;
- boundary, secret, and domain-blindness checks passed;
- real model calls were reaching OpenRouter;
- DeepSeek-specific tool-call formats could be parsed;
- patches could be applied;
- exterior oracles could verify them;
- full trajectories were recorded into durable event stores.

At the same time, the 27-row benchmark exposed a major gap between **runtime correctness** and **agent effectiveness**.

The observed 27-row result was:

| Outcome | Rows | Share |
|---|---:|---:|
| `COMPLETED` | 4 | 14.8% |
| `NO_PATCH` | 7 | 25.9% |
| `DATASET_INVALID` | 16 | 59.3% |
| **Total** | **27** | **100%** |

Those numbers cannot be interpreted as a clean 14.8% benchmark pass rate because 16/27 rows were invalidated by weak challenge baselines that already satisfied their original oracle conditions.

After the benchmark fixtures were hardened and several transport/model defects were fixed, the three-row canary still produced **0/3 successful patches** in the forensic report.

The dominant remaining root cause was not the kernel, event ledger, sandbox, or provider integration.

It was the conversational state representation:

> **AETHER was recording tool results durably, but the next model turn was not receiving a faithful `assistant → tool → assistant → tool` conversation history.**

The L5 dialogue compiler collapsed dialogue fragments into a `"user"` message, while assistant tool proposals were not fed back into the next-turn context. This produced repeated reads/searches, malformed proposals, turn exhaustion, and `NO_PATCH` outcomes.

The supplied reports therefore support a conservative status:

```text
Architecture / trust substrate       HEALTHY
Benchmark infrastructure             FUNCTIONAL
Provider transport                    FUNCTIONAL AFTER FIXES
Durable observability                 STRONG
Dataset/oracle validity               REPAIRED FOR IDENTIFIED CASES
Basic coding capability               DEMONSTRATED ON EASY TASK
Reliable multi-turn coding            NOT YET QUALIFIED IN LATEST FORENSIC SNAPSHOT
Medium/hard benchmark capability      NOT YET ESTABLISHED
Advanced multi-agent evolution        FUTURE WORK, AFTER SINGLE-AGENT LOOP CORRECTNESS
```

---

# 2. What Was Built

## 2.1 Core AETHER Architecture

The project retained the canonical hexagonal structure:

```text
domain ← ports ← kernel ← agency ← runtime → adapters
```

The supplied reports describe the responsibilities as:

### `domain/`

Pure values and semantics:

- canonical data;
- JCS serialization;
- resource selectors;
- event/reducer values;
- no external I/O.

### `ports/`

Structural protocols for external boundaries:

- model;
- sandbox;
- evaluator;
- event store;
- blob store;
- environment.

### `kernel/`

Trusted effect mediation:

- capability validation;
- effect classification;
- S0–S12 dispatch;
- budget/resource checks;
- provenance;
- monotonic attenuation.

### `agency/`

Agent execution mechanics:

- turn loop;
- episode engine;
- context compiler;
- context layers L1–L5;
- compaction.

### `runtime/`

Concrete execution and integration:

- manifest composition;
- sessions;
- prompt assembly;
- persistence;
- execution profiles;
- event emission.

### `adapters/`

Concrete external implementations:

- OpenRouter;
- Ollama;
- model fakes/cassettes;
- filesystem/process environments;
- sandbox;
- evaluator.

---

# 3. Trusted-Core Health

The supplied benchmark-era checks reported:

| Check | Observed result |
|---|---|
| TCB budget | `1,384 / 1,438` logical LOC |
| Hexagonal boundaries | `426` source files, `0` violations |
| Secret scanner | pass |
| Domain blindness | pass |
| Frontier runner tests | `5/5` pass |
| Model/evaluator/sandbox/event-store contracts | reported passing |

The kernel therefore had only about 54 lines of LOC headroom under the stated alarm threshold.

This reinforces an important architectural conclusion:

> The benchmark failures did not justify moving coding-specific context, benchmark, DeepSeek, or workflow logic into the trusted kernel.

The failures were located in higher-level context/runtime/adaptor surfaces, where they belong.

---

# 4. Agent Manifest Surface

The benchmark work created a broader family of agent configurations rather than testing only one prompt.

The supplied reports list approximately eleven v0.9-era presets or agent variants.

## Coding Variants

- `vg-code-v090-react-control`
- `vg-code-v090-claude-shaped`
- `vg-code-v090-opencode-shaped`
- `vg-code-v090-lex-surgical`
- `vg-code-v090-lim-falsifier`

## Tutor / Explanation Variants

- `vg-tutor-v090-v1-read-search`
- `vg-tutor-v090-v2-evidence-graph`

## Research Variants

- `vg-research-v090-v1-local`
- `vg-research-v090-v2-web-corroborated`

## Bug-Fix Variants

- `vg-bugfix-v090-v1-direct`
- `vg-bugfix-v090-v2-reproduce-verify`

The project therefore reached the point where different harness behaviors could be expressed through manifests/policies/prompts/tools without creating a new kernel.

That is an important practical proof of the composition direction even though benchmark quality remained incomplete.

---

# 5. Benchmark System Built

The benchmark driver became:

```text
tools/benchmark-drivers/frontier_v090.py
```

and exposed:

```text
--preregister
--dry-run
--live-sample
--live-canary
--live-27
--row ...
--difficulty ...
--class-name ...
--challenge ...
--preset ...
```

This is a useful result by itself because it creates several experiment modes:

```text
deterministic mock
    ↓
small live sample
    ↓
canary
    ↓
targeted failed rows
    ↓
full fixed matrix
```

That progression lowers debugging cost before a full paid benchmark.

---

# 6. Benchmark Challenge Ladder

The broader challenge library described in the reports spans:

```text
Tier 1 — algorithmic primitives
Tier 2 — state machines / routing
Tier 3 — concurrency / synchronization
Tier 4 — graph algorithms / pipelines
Tier 5 — distributed invariants
Tier 6 — consensus / replication
Tier 7 — greenfield storage engine
```

Examples include:

- LRU + TTL cache;
- streaming JSON parser;
- event bus;
- finite-state workflow;
- retry/backoff;
- token bucket;
- reader/writer lock;
- connection pool;
- DAG resolver;
- Merkle Patricia trie;
- two-phase commit;
- vector clocks;
- Raft;
- LSM-style key/value engine.

The 27-row quick-run matrix did not exercise every tier. It used selected tasks and agent families as a calibration matrix.

---

# 7. Exterior Oracle Isolation

A significant benchmark design achievement was separating the model-visible workspace from the evaluator.

Conceptually:

```text
AGENT WORKSPACE
  task
  source code
  no hidden oracle

        ↓ patch

EXTERIOR EVALUATOR
  sealed tests/oracle
  isolated temporary execution
  deterministic verdict
```

This avoids the agent solving the benchmark by reading the hidden evaluator directly.

It also makes failures more useful because the model trajectory and evaluator truth are separate artifacts.

---

# 8. Durable Flight Recorder

The benchmark runs wrote SQLite-WAL histories such as:

```text
<workspace>/.vanguard/events.sqlite3
```

and content-addressed blobs under:

```text
<workspace>/.vanguard/blobs/
```

This allowed the reports to inspect:

- model input;
- raw model output;
- proposal;
- tool call;
- tool receipt;
- cost;
- prompt/completion tokens;
- TTFT;
- artifacts;
- terminal state.

This became one of the most valuable capabilities of the project.

Instead of observing only:

```text
benchmark failed
```

the team could observe:

```text
turn 0 → fs.read
turn 1 → fs.read
turn 2 → fs.search
turn 3 → fs.search
turn 4 → fs.read
...
terminal → abandoned
```

The architecture therefore converted “agent stupidity” from a vague impression into an inspectable systems failure.

---

# 9. Benchmark Result: What Actually Happened

The supplied 27-row report recorded:

```text
4 COMPLETED
7 NO_PATCH
16 DATASET_INVALID
```

The four completed runs were all on the easiest `tier1_lru_ttl_cache` task.

The reports state that medium `tier2_event_bus` and hard `tier3_token_bucket` rows did not establish successful patch capability in that matrix.

## 9.1 Why the 27-Row Number Is Not a Valid Final Score

`DATASET_INVALID` meant the original buggy baseline already passed the evaluator.

Therefore those rows were invalid experiments.

They should not count as:

- agent passes;
- agent failures;
- meaningful benchmark attempts.

The only defensible conclusion from the v2 matrix is that:

1. the harness could produce real successful patches on at least one easy task;
2. the experiment design had fixture/oracle defects;
3. multiple valid rows ended without patches;
4. reliable medium/hard coding performance had not been established.

---

# 10. A Successful Real Patch Was Demonstrated

The `tier1_lru_ttl_cache` trace shows a concrete agent-generated repair.

The defective expiration logic was effectively:

```python
def is_expired(self, current_time):
    if self.ttl_seconds is None:
        return False
    return False
```

and the generated repair changed the semantics to compare current time with the entry lifetime.

The exterior oracle reported a successful result in at least one execution.

This establishes an important but narrow fact:

> The full stack was capable of real model → tool → patch → oracle success.

The problem was reliability and multi-turn state handling, not total absence of coding functionality.

---

# 11. A Failed Execution Was Equally Valuable

Another trace of the same LRU scenario consumed a large trajectory and eventually ended:

```text
outcome = abandoned
```

after repeated reads and repeated patch-related behavior.

The reports include a run with roughly:

```text
141,011 total episode tokens
~1,049,122 bytes
~$0.008964
```

ending without a clean terminal success.

That contrast is important:

```text
same substrate
same broad task
sometimes patch succeeds
sometimes context loop degenerates
```

This points toward harness/context-state instability rather than pure task difficulty.

---

# 12. Errors Discovered

The debugging process identified two classes of defects:

## A. Infrastructure / Wire / Dataset Defects

Seven issues were reported as corrected.

## B. Agent-Loop / Context Defects

Several issues remained open in the latest forensic snapshot.

---

# 13. Fixed Defect #1 — Provider Key Across Process Boundary

## Symptom

```text
instrument_error:provider_key_missing
```

## Root Cause

The live benchmark runner spawned execution without ensuring the OpenRouter key was available in the relevant child execution context.

## Correction

The driver loaded the API key from project configuration / `.env` before live execution.

## Result

Real model calls could proceed reliably through the benchmark process boundary.

---

# 14. Fixed Defect #2 — HTTP Error Body Crash

## Symptom

```text
AttributeError:
'NoneType' object has no attribute 'read'
```

## Root Cause

On some urllib failures/timeouts:

```python
exc.fp
```

was already closed or absent, but the error handler still attempted:

```python
exc.read()
```

## Correction

Guard the body read:

```python
body = b""

if getattr(exc, "fp", None) is not None:
    try:
        body = exc.read() or b""
    except Exception:
        body = b""
```

## Result

A provider/network failure stopped crashing the error-handling path itself.

---

# 15. Fixed Defect #3 — DeepSeek DSML Tool Calls

DeepSeek sometimes returned tool invocations embedded in textual DSML markup instead of the expected standard function-call structure.

Example form:

```text
<｜DSML｜tool_calls>
  <｜DSML｜invoke ...>
  ...
```

The adapter initially treated such output incorrectly.

A DSML extraction path was implemented to recover:

- tool name;
- parameters;
- body/content.

This is a useful general adapter lesson:

> Model providers can be API-compatible at the transport layer while still emitting model-specific structured output conventions.

Provider adapters therefore need a normalization layer.

---

# 16. Fixed Defect #4 — Tool JSON Truncation

Whole-file patches could exceed the previous:

```text
max_tokens = 1024
```

and terminate in the middle of JSON/tool-call output.

The reported correction raised the effective lower bound to approximately:

```text
4096 completion tokens
```

and added more tolerant parsing paths such as:

```python
json.loads(..., strict=False)
```

plus fallback parsing.

This removed one class of malformed tool call caused by output truncation rather than model reasoning.

---

# 17. Fixed Defect #5 — Search Pollution by AETHER's Own State

`fs.search` could recursively inspect:

```text
.vanguard/blobs/
```

and feed the agent large amounts of its own generated state, hashes, and prior outputs.

This is a particularly instructive bug:

```text
agent searches workspace
→ search finds agent's previous stored context
→ previous context enters new context
→ context expands / self-contaminates
```

The fix excluded paths such as:

```text
.vanguard
.git
__pycache__
```

from normal source search.

This should be treated as a general invariant:

> Internal runtime state should not be visible to ordinary repository search unless explicitly requested.

---

# 18. Fixed Defect #6 — Consecutive System Message Normalization

L1/L2/L3 context material could produce multiple adjacent system messages.

The OpenRouter adapter was modified to merge adjacent system blocks into one root system message.

This improved provider compatibility.

However, it did **not** fix the deeper L5 dialogue-history problem described later.

---

# 19. Fixed Defect #7 — Invalid Benchmark Oracles

A major experiment-design bug was discovered:

```text
the baseline already passed
```

for several challenge oracles.

The reports describe hardening checks for examples such as:

- event bus wildcard/unsubscribe semantics;
- token-bucket fractional behavior;
- DAG/cycle behavior.

This converted the benchmark from:

```text
"did patched code pass?"
```

to the required:

```text
"does baseline fail AND repaired candidate pass?"
```

That distinction is essential.

---

# 20. Remaining Critical Defect — L5 Role Squashing

The most important unresolved issue in the latest forensic report was the context-layer rendering of dialogue.

The mapping contained:

```python
Layer.DIALOGUE: "user"
```

and multiple L5 blocks were concatenated together.

The effective conversation sent to the model looked like:

```text
system
system
system
user task
user [all historical tool output concatenated]
```

instead of:

```text
system
user task
assistant tool call
tool response
assistant tool call
tool response
...
```

The model therefore did not receive the conversational structure needed to understand:

```text
I already requested this file.
That response corresponds to that call.
I have already applied that patch.
Now I should test rather than read again.
```

---

# 21. Remaining Critical Defect — Assistant Proposals Were Not Re-Admitted

The durable event log recorded model proposals.

But the next-turn dialogue context did not preserve the assistant's corresponding tool-call message.

Only the tool result was admitted into dialogue.

That creates an orphaned history:

```text
tool result
tool result
tool result
```

without the tool calls that caused them.

This is separate from the role-squashing problem.

Even if L5 role rendering were corrected, the context would still be incomplete unless assistant actions were reintroduced.

---

# 22. Existing `history_steps` Path Was Effectively Dead

The OpenRouter adapter reportedly already contained logic capable of rendering:

```text
assistant_tool_call
tool_response
```

into appropriate message roles.

But:

```text
context["history_steps"]
```

was not being populated by the upstream context/prompt pipeline.

Additionally, a pre-existing:

```text
context["messages"]
```

path returned early.

The implementation therefore contained the right lower-level rendering feature but failed to connect it to the runtime state.

This is a classic integration defect:

```text
feature exists locally
≠
feature exists end-to-end
```

---

# 23. Remaining Contributing Issue — Turn Budget

The benchmark runner used:

```text
max_turns = 8
```

in the reported snapshot.

For a realistic code task:

```text
read task
read file
read dependency
search
patch
test
inspect failure
repair
test again
```

eight turns can be consumed quickly.

The reports compared this with other working experiments that used a larger 15–25 turn envelope.

Increasing the turn budget would not fix role corruption.

But after context fidelity is corrected, a larger or adaptive turn limit is likely necessary for meaningful multi-file tasks.

---

# 24. Remaining Minor Issue — Prompt / Tool Mismatch

The Claude-shaped prompt reportedly said:

```text
Use Bash for tests and git only.
```

while the actual process capability allowed specific executables such as:

```text
python3
pytest
git
ruff
```

A model interpreting “Bash” literally could produce:

```text
bash -c ...
```

which the effect selector would correctly deny.

This is a useful design lesson:

> Prompt vocabulary, tool aliases, and actual capability selectors must describe the same executable interface.

---

# 25. Why the Agent Repeated Reads

The durable event stores provide a concrete behavioral signature.

A failed run could look like:

```text
turn 0  fs.read
turn 1  fs.read
turn 2  fs.search
turn 3  fs.search
turn 4  fs.read
turn 5  fs.search
terminal malformed / abandoned
```

This is consistent with the model not having a structured memory that says:

```text
assistant requested X
tool returned Y
```

Each turn sees a large, partially flattened user-like context.

The model therefore keeps rediscovering facts it already observed.

---

# 26. Why Simply Raising `max_turns` Is Not Enough

If the probability of progressing after each tool call is low because history is malformed, then:

```text
8 bad turns
```

becoming:

```text
20 bad turns
```

primarily increases:

- latency;
- context size;
- tokens;
- cost.

The correct order of reasoning is:

```text
history fidelity
→ progress detection
→ context efficiency
→ then tune turn budget
```

---

# 27. Benchmark Infrastructure vs Agent Capability

This distinction reconciles apparently conflicting statements in the supplied reports.

One report calls the benchmark harness:

```text
GREEN / ready for matrix execution
```

while another says:

```text
agents cannot reliably code
```

These can both be true.

## Benchmark Infrastructure Readiness

Means:

- rows can be selected;
- model API works;
- events are captured;
- oracles execute;
- results are written;
- errors can be classified.

## Agent Capability Readiness

Means:

- the agent reliably performs the task;
- medium/hard tasks succeed;
- failures are not dominated by harness bugs;
- canary is stable;
- benchmark score is meaningful.

The supplied evidence strongly supports the first.

It did not yet support the second.

---

# 28. Current Status — Conservative Snapshot

The most defensible state from the latest supplied reports is:

| Area | State |
|---|---|
| Architecture boundaries | **Healthy** |
| Trusted kernel | **Healthy, close to LOC alarm** |
| Model/provider connection | **Working** |
| DeepSeek DSML support | **Implemented** |
| Durable event capture | **Working** |
| Content-addressed artifacts | **Working** |
| Exterior oracle execution | **Working** |
| Benchmark row orchestration | **Working** |
| Mock/dry/live benchmark modes | **Working** |
| Search hygiene | **Improved** |
| Dataset/oracle definitions | **Known invalid cases repaired** |
| Easy coding proof | **Demonstrated** |
| Stable multi-turn dialogue | **Not qualified in latest forensic snapshot** |
| Medium/hard coding | **Not demonstrated reliably** |
| Full 27-row benchmark score | **Not yet scientifically interpretable** |
| LAM vertical coding test | **Reported failing for same dialogue problem** |
| Multi-agent / advanced controller work | **Should be treated as post-correctness research** |

---

# 29. What We Learned

## 29.1 Strong Architecture Does Not Automatically Produce a Strong Agent

AETHER's:

- kernel;
- event sourcing;
- capabilities;
- provenance;
- sandbox;
- manifests;

can all be correct while the agent still performs badly because the dialogue representation is wrong.

The benchmark exposed this clearly.

---

## 29.2 Context Is Runtime State

For an agent, conversational context is not merely prompt formatting.

It is part of its operational state.

Losing:

```text
assistant tool call
```

while keeping:

```text
tool result
```

is analogous to corrupting half of an event pair.

---

## 29.3 Provider Normalization Is a Real Engineering Layer

DeepSeek DSML demonstrated that tool-use behavior cannot be assumed identical across model families.

A provider adapter should normalize:

```text
provider-native response
       ↓
canonical model proposal
```

before agency/runtime logic sees it.

---

## 29.4 Benchmark Datasets Need Falsifiers Too

The `DATASET_INVALID` discovery shows that benchmark design must test the benchmark itself.

Every challenge should establish:

```text
baseline oracle = FAIL
known/reference solution = PASS
```

before consuming live model calls.

---

## 29.5 Event Sourcing Paid Off During Debugging

The durable ledger made it possible to diagnose:

- repeated reads;
- missing patch actions;
- malformed proposals;
- token growth;
- cost;
- exact provider output;
- context expansion.

This is one of the strongest practical validations of AETHER's event-centric design during this iteration.

---

# 30. Benchmark Workflow Going Forward

The quick-run guide provides a useful operational hierarchy.

## Deterministic Preflight

```bash
python3 tools/benchmark-drivers/frontier_v090.py --dry-run
```

## Targeted Regression Rows

Easy known-pass rows:

```bash
python3 tools/benchmark-drivers/frontier_v090.py --row v090-01 v090-04
```

Medium calibration:

```bash
python3 tools/benchmark-drivers/frontier_v090.py --row v090-02 v090-05 v090-08
```

Hard calibration:

```bash
python3 tools/benchmark-drivers/frontier_v090.py --row v090-03 v090-06 v090-09
```

## Live Canary

```bash
python3 tools/benchmark-drivers/frontier_v090.py --live-canary
```

## Full Matrix

```bash
python3 tools/benchmark-drivers/frontier_v090.py --live-27
```

The methodological lesson is:

> Do not pay for the full matrix while a small diagnostic slice is still failing for systemic reasons.

---

# 31. LAM / Mock Evaluation Track

The quick-run material also documents a deterministic LLM API mock path.

Its value is to isolate:

```text
runtime / harness overhead
```

from:

```text
provider latency / provider randomness
```

This should remain a complementary test layer.

Conceptually:

```text
Unit / contracts
    ↓
LAM deterministic simulation
    ↓
live canary
    ↓
full provider benchmark
```

---

# 32. Immediate Technical Ideas Emerging From the Failures

These are research/engineering ideas derived directly from the observed problems. They are not claimed as already implemented.

## 32.1 Structured Dialogue Objects

Do not store L5 primarily as text fragments.

Represent:

```python
AssistantToolCall(
    call_id,
    action,
    arguments,
    optional_thought_ref,
)

ToolResponse(
    call_id,
    result_ref,
    status,
)
```

and render provider-specific messages later.

---

## 32.2 Separate Durable History From Provider Rendering

Canonical history:

```text
ProposalProduced
EffectCompleted
```

Provider rendering:

```text
assistant/tool
assistant/function
model/tool
```

should be an adapter transformation.

This prevents OpenAI-style role names from becoming substrate semantics.

---

## 32.3 No-Progress Detection

The event traces suggest explicit anti-thrashing.

For example:

```python
if (
    same_action_signature_repeated >= 3
    and no_new_artifact
    and no_new_failure_information
):
    trigger_recovery_policy()
```

Possible recovery:

- inject a concise progress summary;
- require a different action class;
- re-localize;
- stop rather than burn more tokens.

---

# 33. Phase-Aware Tool Availability

The reports compare Vanguard with systems where tool availability changes by stage.

Possible phases:

```text
LOCALIZE
IMPLEMENT
VERIFY
REPAIR
```

Example:

```text
LOCALIZE:
  read
  search

IMPLEMENT:
  read
  patch

VERIFY:
  test
  read

REPAIR:
  read
  patch
  test
```

This may reduce action entropy.

It should be benchmarked rather than assumed to help.

---

# 34. Semantic Compaction Instead of Raw Byte Elision

The reports describe existing compaction behavior that can degrade into coarse byte elision.

Future context compaction could preserve structured state:

```text
files inspected
hypotheses
patches applied
tests run
failures
unresolved questions
```

rather than merely:

```text
[X bytes elided]
```

The goal is not prettier summaries.

It is maintaining enough state for the next action to be causally sensible.

---

# 35. Adaptive Turn Budget

Instead of a universal:

```text
max_turns = 8
```

a future controller could derive turn allowance from:

- task class;
- files touched;
- failed tests;
- patch progress;
- remaining token/USD budget.

Example conceptual policy:

```python
if no_progress_for >= 3:
    stop()

elif patch_exists and verification_pending:
    grant_small_extension()

elif new_failure_information:
    grant_repair_extension()
```

This avoids both premature abandonment and unlimited wandering.

---

# 36. Better Benchmark Failure Taxonomy

Future reports should distinguish at least:

```text
PASS
NO_PATCH
PATCH_FAILED_ORACLE
PATCH_NOT_APPLIED
MODEL_MALFORMED
TURN_EXHAUSTED
NO_PROGRESS
PROVIDER_ERROR
TOOL_ERROR
AUTHORITY_DENIED
DATASET_INVALID
INSTRUMENT_ERROR
```

This makes benchmark evolution more scientific.

---

# 37. Context Efficiency Metrics

The LRU forensic run illustrates that tokens can grow substantially across repeated turns.

Useful future metrics:

\[
ProgressPer1kTokens =
\frac{MeaningfulStateTransitions}
{PromptTokens/1000}
\]

\[
RepeatedObservationRate =
\frac{RepeatedReadOrSearchActions}
{AllObservationActions}
\]

\[
PatchLatencyTurns =
Turn_{first\ patch}
-
Turn_{first\ observation}
\]

\[
VerificationLatencyTurns =
Turn_{terminal\ verification}
-
Turn_{first\ patch}
\]

These can reveal improvements before pass-rate changes become statistically clear.

---

# 38. Cache Effectiveness Metrics

The supplied telemetry records cached token counts.

Future reporting can derive:

\[
CacheRatio =
\frac{CachedPromptTokens}
{PromptTokens}
\]

along with:

```text
cost with caching
estimated cost without caching
TTFT
prefix stability
```

This is especially relevant because a stable root system/tool prefix may be cheap while an ever-growing malformed L5 tail remains expensive.

---

# 39. Future Coding-Agent Ideas

After correcting basic dialogue/state fidelity, several directions from the reports become useful experiments.

## Evidence-First Coding

Use:

```text
task
→ localization evidence
→ patch
→ verification
```

rather than unrestricted exploratory loops.

## Surgical Editing

Prefer narrow target/replacement patches where possible.

## Reproduce-Then-Repair

Force:

```text
reproduce failure
→ localize
→ patch
→ rerun
```

for bugfix tasks.

## Falsifier-Oriented Agent

Use counterexamples/property tests to challenge candidate repairs.

## External Fault Localizer

A diagnostic subsystem can rank suspicious files/lines before the main coding model receives context.

---

# 40. Future Multi-Agent Ideas

The supplied project material mentions:

- `agent.spawn`;
- hierarchical communication;
- planner/executor/reviewer;
- CEGIS;
- benchmark regression tracking.

The benchmark findings imply an ordering constraint:

> Multi-agent complexity should not be used to compensate for a broken single-agent conversational state.

Once the base loop is stable, multi-agent experiments can test:

```text
planner
   ↓ artifact
executor
   ↓ patch
reviewer
   ↓ verdict
```

while preserving the same event/effect substrate.

---

# 41. Future Research-Agent Ideas

The presence of tutor/research manifests is useful even though the 27-row matrix mostly exposed coding-loop issues.

Future research-agent evaluation should use tasks appropriate to their capabilities rather than requiring read-only agents to emit code patches.

Potential evaluation dimensions:

- citation accuracy;
- path/symbol accuracy;
- evidence coverage;
- contradiction detection;
- unsupported claim rate;
- source corroboration;
- abstention quality.

This avoids conflating:

```text
"cannot patch code"
```

with:

```text
"failed its intended research task"
```

for read-only agent families.

---

# 42. Benchmark Design Improvement: Match Evaluator to Agent Class

The matrix mixed:

- Coding;
- Tutor;
- Research;
- Bugfix;

families.

A stronger future benchmark lattice can define class-appropriate terminal success.

Example:

```text
Coding:
  patch + oracle

Tutor:
  evidence-grounded explanation

Research:
  sourced synthesis

Bugfix:
  reproduced failure + patch + regression verification
```

The runtime remains common.

The evaluator changes by task contract.

This is a better test of generality than forcing every agent family through one patch objective.

---

# 43. Experiment Validity Checklist

Before a new live benchmark row:

```text
[ ] baseline fails
[ ] known solution passes
[ ] oracle hidden from agent
[ ] model identity pinned
[ ] preset identity pinned
[ ] task digest pinned
[ ] max turns recorded
[ ] tool set recorded
[ ] execution profile recorded
[ ] provider errors typed
[ ] result artifact preserved
[ ] event store preserved
[ ] negative attempts preserved
```

This is one of the most important methodological improvements suggested by the experience.

---

# 44. Project Result So Far

The work can be summarized in four layers.

## Layer 1 — Substrate

**Result: strong.**

AETHER has:

- governed effects;
- event sourcing;
- durable history;
- capability boundaries;
- composition;
- provider/sandbox/evaluator ports.

## Layer 2 — Agent Runtime

**Result: functional but exposed an important context-state integration defect.**

The system can:

- call models;
- interpret tool use;
- execute tools;
- patch files;
- emit events.

But the latest forensic snapshot found poor multi-turn conversation reconstruction.

## Layer 3 — Benchmark Infrastructure

**Result: substantial success.**

The project gained:

- a reusable driver;
- per-row execution;
- canaries;
- dry runs;
- class filters;
- difficulty filters;
- exterior oracles;
- durable telemetry.

## Layer 4 — Agent Capability Qualification

**Result: incomplete.**

At least one easy real coding task was solved.

The available 27-row matrix was scientifically contaminated by invalid dataset rows, and the post-hardening canary still failed to establish stable coding capability.

---

# 45. Errors Were Productive

The benchmark effort identified concrete defects that architecture/unit tests alone did not expose:

```text
provider secret propagation
HTTP error-path robustness
model-specific tool syntax
completion truncation
search self-contamination
system-message normalization
invalid benchmark oracles
dialogue role destruction
missing assistant-history admission
turn-budget pressure
prompt/tool mismatch
```

This is a useful project-level result.

The benchmark acted as an integration microscope.

---

# 46. What Should Not Be Concluded From These Reports

The sources do **not** support the following claims:

```text
AETHER achieves a strong SWE-bench score.
AETHER reliably solves medium/hard coding tasks.
The 27-row result is a valid comparative benchmark score.
All dialogue-history defects were already fixed.
Multi-agent execution is required to improve the current benchmark.
The architecture needs a rewrite.
```

The reports instead support a narrower and more useful statement:

> The architecture is functioning well enough that the remaining failure can be localized to concrete harness/context integration behavior rather than being dismissed as an undefined “agent intelligence” problem.

---

# 47. Current Working Hypothesis

The latest forensic evidence supports this causal chain:

```text
assistant proposal not preserved in dialogue
             +
L5 fragments flattened to user role
             ↓
model lacks structured history
             ↓
repeated reads/searches
             ↓
context grows
             ↓
turn budget shrinks
             ↓
malformed/no-op proposal or abandonment
             ↓
NO_PATCH
```

Other provider and benchmark defects previously obscured this.

Once those were corrected, the context-history defect became visible as the dominant blocker.

---

# 48. Suggested Next Validation Logic

This is not a project plan; it is the minimal falsification sequence implied by the reports.

```text
1. Verify assistant/tool role fidelity
2. Verify assistant proposals enter next-turn context
3. Run deterministic context-rendering tests
4. Run LAM/mock vertical
5. Run one easy live task
6. Run one medium live task
7. Run one hard live task
8. Run 3-row canary
9. Only then interpret a larger matrix
```

The goal is to prove the causal diagnosis before spending on scale.

---

# 49. Minimum Success Evidence for the Context Fix

A corrected trajectory should look like:

```text
assistant: fs.read(file A)
tool: contents A

assistant: fs.read(file B)
tool: contents B

assistant: patch.apply(file A)
tool: patch applied

assistant: proc.exec(test)
tool: tests pass

assistant: finish
```

rather than:

```text
user: task
user: result A + result B + result C
```

A simple structural test can verify roles without any real model call.

---

# 50. Longer-Term Research Directions

Once basic qualification is stable, the reports justify investigating:

- dynamic context compilation;
- phase-specific tool pruning;
- semantic compaction;
- anti-thrashing;
- targeted model escalation;
- stronger code localization;
- deterministic mock evaluation;
- provider-specific normalization adapters;
- broader tier 4–7 challenge suites;
- multi-agent delegation;
- CEGIS-style repair;
- regression tracking;
- adaptive budgets;
- richer cache telemetry;
- harness-versus-model attribution.

These should remain measured alternatives rather than assumed improvements.

---

# 51. Consolidated Timeline of This Benchmark Iteration

```text
AETHER architecture available
        ↓
v0.9 benchmark presets created
        ↓
27-row frontier driver created
        ↓
live OpenRouter execution attempted
        ↓
provider secret propagation failure discovered
        ↓ FIXED
HTTP error-path crash discovered
        ↓ FIXED
DeepSeek DSML tool format discovered
        ↓ FIXED
tool JSON truncation discovered
        ↓ FIXED
repository search polluted by .vanguard data
        ↓ FIXED
adjacent system message incompatibility
        ↓ IMPROVED
27-row matrix executed
        ↓
16 invalid dataset rows discovered
        ↓ ORACLES HARDENED
post-fix canary executed
        ↓
NO_PATCH / repeated reads remained
        ↓
SQLite trajectory forensics
        ↓
L5 role squashing identified
        +
assistant proposal omission identified
        ↓
current main unresolved hypothesis in supplied snapshot
```

---

# 52. Final Project Status

The most useful way to describe this period is:

> **AETHER successfully crossed from architecture-building into empirical agent engineering.**

The system was sophisticated enough to:

- execute real models;
- preserve exact trajectories;
- expose agent actions;
- isolate evaluators;
- reproduce errors;
- distinguish infrastructure failures from agent failures;
- find subtle context and experiment-design bugs.

The benchmark scores themselves were not yet the success.

The success was creating a substrate where failure became diagnosable.

The current technical bottleneck in the latest supplied forensic snapshot was comparatively narrow:

```text
preserve faithful multi-turn agent history
```

not:

```text
replace the event architecture
rewrite the kernel
invent a new agent framework
```

A stable single-agent turn loop with correct conversational causality is the necessary foundation for everything that follows:

```text
stronger coding
→ research agents
→ delegated agents
→ planners/reviewers
→ adaptive routing
→ learned policies
→ self-improvement experiments
```

The immediate scientific question left by this iteration is therefore:

\[
\boxed{
\text{Does restoring exact assistant/tool dialogue causality
convert the observed NO\_PATCH loops into stable patch-and-verify behavior?}
}
\]

Until that hypothesis is experimentally confirmed, larger architectural additions would confound the diagnosis.

---

# Appendix A — Source Reconciliation Notes

## `FULL_PROJECT_STATUS_AND_BENCHS.md`

Useful for:

- architecture overview;
- agent preset inventory;
- challenge tiers;
- seven wire/dataset fixes;
- concrete live traces;
- successful LRU repair;
- benchmark infrastructure readiness.

It also contains multiple attempts/traces, including both successful and abandoned behavior.

Therefore its statement that the benchmark harness is `GREEN` is interpreted here as **runner/instrumentation readiness**, not proof of reliable agent capability.

## `FULL_PROJECT_STATUS_AND_BENCHS_B.md`

Useful as the more conservative forensic snapshot for:

- the 27-row result distribution;
- post-hardening 0/3 canary;
- L5 role squashing;
- missing assistant proposal recording;
- turn-budget concern;
- prompt/tool mismatch;
- detailed module issue map.

This report is used as the primary basis for the consolidated “latest reported capability state”.

## `BENCHMARK_V090_QUICKRUN.MD`

Useful for:

- exact driver commands;
- row IDs;
- challenge/preset mapping;
- targeted regressions;
- dry/live/canary/full execution modes;
- LAM/mock benchmark entrypoints.

It is operational documentation and does not by itself prove that all benchmark defects are resolved.

---

# Appendix B — Compact Status Matrix

| Topic | Status in supplied snapshot |
|---|---|
| Event-sourced runtime | ✅ Operational |
| SQLite-WAL trajectories | ✅ Operational |
| CAS artifacts | ✅ Operational |
| OpenRouter integration | ✅ Operational after fixes |
| DeepSeek DSML parser | ✅ Implemented |
| Sandbox/evaluator contracts | ✅ Reported passing |
| Benchmark runner | ✅ Operational |
| 27-row orchestration | ✅ Operational |
| Challenge baseline validity | ⚠️ Defects found; identified cases hardened |
| Easy real patch | ✅ Demonstrated |
| Multi-turn context fidelity | ❌ Blocking defect in latest forensic report |
| Stable canary | ❌ 0/3 in latest forensic report |
| Medium/hard coding qualification | ❌ Not established |
| Full benchmark score | ❌ Not valid yet |
| Advanced multi-agent capability | 🔬 Future experimentation |

---

# Appendix C — Core Files Implicated by the Benchmark Forensics

```text
vanguard/packages/agency/context/layers.py
vanguard/packages/agency/context/compiler.py
vanguard/packages/agency/episode/engine.py
vanguard/packages/runtime/prompt_assembler.py
vanguard/packages/runtime/session.py
vanguard/packages/adapters/models/openrouter.py
tools/benchmark-drivers/frontier_v090.py
benchmarks/swe_bench/challenges.py
```

---

# Appendix D — Fast Benchmark Commands

```bash
# deterministic preflight
python3 tools/benchmark-drivers/frontier_v090.py --dry-run

# one easy, medium, hard
python3 tools/benchmark-drivers/frontier_v090.py --row v090-01 v090-02 v090-03

# live canary
python3 tools/benchmark-drivers/frontier_v090.py --live-canary

# full matrix
python3 tools/benchmark-drivers/frontier_v090.py --live-27
```

---

**End of consolidated status report.**
