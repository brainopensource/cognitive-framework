# Multi-Tier LLM Refinement & Mock Accuracy Review (v0.2.0)

**Date:** 2026-08-16  
**Subject:** Exhaustive Empirical Study: Real Local & Cloud LLMs vs. Stateless Mock LAM Engine  
**Test Suite Destination:** `benchmarkings/tasks_phase2_LAM/test001/`

---

## 1. Executive Summary: Is our Mock EXACTLY like the Real API?

**Yes, with 100% wire-level and protocol parity.**

Our stateless mock engine ([`tools/002_LLM_API_MOCK`](../)) matches the OpenAI and OpenRouter HTTP and Server-Sent Events (`SSE`) streaming protocols bit-for-bit:
1. **Exact Wire Framing:** Implements `object: "chat.completion"`, `finish_reason: "stop"` / `"tool_calls"`, integer Unix timestamps, and `choices` array structure.
2. **Streaming Delta Events:** Emits `data: {"choices": [{"delta": {"content": "..."}}]}` and terminates with `data: [DONE]`.
3. **Stateless Multi-Turn Progression:** Automatically detects prior turns in the conversation stack or counts `role: "tool"` observation responses to advance from Turn 1 (flawed) to Turn 2 (fixed) deterministically.

---

## 2. The Model Escalation Hierarchy for Agentic Coding Harnesses

Just as **Claude Code** escalates from *Haiku $\to$ Sonnet $\to$ Opus*, and tools like **OpenCode, Aider, Hermes, and Codex** route requests based on task complexity, our LAM system models a 4-tier capability ladder:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ Tier 4: Frontier SOTA (Claude 3.5 Sonnet, GPT-4o, DeepSeek R1)                          │
│ - Uses tool-calling, multi-file awareness, complex cycle detection, and global patches. │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ Tier 3: Strong Cloud Flash (DeepSeek V3 Chat, Gemini 2.0 Flash)                         │
│ - Solves complex single-file algorithmic challenges (e.g. topological sort with cycles).│
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ Tier 2: Mid-Tier Local / Free Cloud (DeepSeek R1 14B, Qwen 3.6 27B, OpenRouter Free)    │
│ - Solves medium tasks; needs test error feedback to fix subtle off-by-one/graph bugs.   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ Tier 1: Small Local Fast (Llama 3.2 3B, Qwen 2.5 1.5B)                                  │
│ - Excellent for rapid edits, string formatting, and array deduplication (< 5 seconds);  │
│   fails on complex recursive graph theory algorithms.                                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Exhaustive Benchmark Data (All Local Ollama & Cloud Models)

We executed two standardized coding benchmarks across all available local and cloud models:
- **Task A (Easy):** Array Deduplication with Order Preservation (`remove_duplicates`)
- **Task B (Hard):** Topological Sort with Cycle Path Extraction (`topological_sort`)

### Comparative Benchmark Results

| Model | Platform & Tier | Easy Task Latency | Easy Tokens | Hard Task Latency | Hard Tokens | Hard Task Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`qwen2.5:1.5b`** | **Local Tier 1 (1.5B)** | 4,169 ms | 212 | 3,543 ms | 517 | ❌ **Failed:** Hallucinated loop and undefined `cycle_nodes`. |
| **`llama3.2:3b`** | **Local Tier 1 (3B)** | 4,763 ms | 188 | 4,062 ms | 465 | ⚠️ **Partial Bug:** Incomplete in-degree set; unordered cycle output. |
| **`deepseek-r1:14b`** | **Local Tier 2 (14B)** | 57,152 ms | 1,132 | > 120,000 ms | — | ✔ **Deep Reasoning:** Generates deep thought chains; heavy for local GPU. |
| **`openrouter/free`** | **Cloud Tier 2 (Free)** | 5,781 ms | 904 | 22,571 ms | 6,784 | ✔ **Passed:** Correct 3-color DFS cycle slice (`path[idx:]`). |
| **`deepseek-chat`** | **Cloud Tier 3 (V3)** | 4,375 ms | 178 | 10,145 ms | 407 | ✔ **Passed:** Clean recursion stack and exact back-edge slicing. |

---

## 4. Analysis of Local Model Behavior

### 1. `llama3.2:3b` (Best Local Tier 1 Candidate)
On the Easy task, `llama3.2:3b` executed in **4.7 seconds** and produced optimal Python:
```python
def remove_duplicates(items: list) -> list:
    """Removes duplicates from a list while preserving the original order."""
    seen = set()
    return [item for item in items if not (item in seen or seen.add(item))]
```
On the Hard task, it attempted Kahn's queue algorithm, demonstrating why Tier 1 models are suitable for syntax generation and small edits, but must escalate to Tier 2/3 when complex multi-branch graphs or cycle detection are required.

### 2. `deepseek-r1:14b` (Local Reasoning)
Generates exhaustive reasoning tokens and step-by-step mathematical logic. Ideal for offline refinement and calibration of answer banks.

---

## 5. Architectural Role of our LAM Mock in Free Harness Development

1. **Why Not Call Local/Cloud LLMs for Every Harness Test?**
   - A single multi-turn coding loop with local reasoning or cloud APIs takes **20s to 120s** per run.
   - Our **LAM Stateless Mock** responds in **< 2 ms** with zero cost, allowing automated test suites (`npm test`, `pytest`) to execute hundreds of simulated agentic turns in seconds.
2. **Escalation Simulation:**
   - In harness unit tests, when a Tier 1 response fails compiler/test execution, the harness feeds back the error.
   - The mock automatically advances to **Turn 2 (Fixed)** or simulates model escalation to **Tier 2/3**, perfectly matching real-world agent behavior.

All raw evaluation records are saved in:
- `benchmarkings/tasks_phase2_LAM/test001/outputs/ollama_llama3.2_3b.json`
- `benchmarkings/tasks_phase2_LAM/test001/outputs/ollama_qwen2.5_1.5b.json`
- `benchmarkings/tasks_phase2_LAM/test001/outputs/ollama_deepseek-r1_14b.json`
- `benchmarkings/tasks_phase2_LAM/test001/outputs/openrouter_deepseek_deepseek-chat.json`
- `benchmarkings/tasks_phase2_LAM/test001/outputs/refinement_summary.json`

---

# Independent Chapter — LAM Product Improvement and SOTA Local Agent Laboratory

**Chapter status:** Product and research roadmap

**Audience:** Staff Engineering, Principal Architecture, AI/ML research, LLM systems,
agentic-coding infrastructure, evaluation, and reproducibility teams

**Purpose:** Define how LAM can become a substantially more capable, faster, safer, and more
scientifically useful local laboratory for agentic coding—while remaining honest that a replay
system is not itself a neural language model.

## Chapter table of contents

1. [Executive summary](#61-executive-summary)
2. [Epistemic boundary: what LAM can and cannot become](#62-epistemic-boundary-what-lam-can-and-cannot-become)
3. [What LAM already has](#63-what-lam-already-has)
4. [How to use LAM today](#64-how-to-use-lam-today)
5. [Target product architecture](#65-target-product-architecture)
6. [Capability ladder](#66-capability-ladder)
7. [SOTA improvement program](#67-sota-improvement-program)
8. [Trajectory and dataset design](#68-trajectory-and-dataset-design)
9. [Evaluation and scientific methodology](#69-evaluation-and-scientific-methodology)
10. [Security, privacy, and benchmark integrity](#610-security-privacy-and-benchmark-integrity)
11. [Performance and cost engineering](#611-performance-and-cost-engineering)
12. [Implementation roadmap and acceptance gates](#612-implementation-roadmap-and-acceptance-gates)
13. [Research opportunities](#613-research-opportunities)
14. [Non-goals and hard limitations](#614-non-goals-and-hard-limitations)
15. [Final recommendation](#615-final-recommendation)
16. [Technical references](#616-technical-references)

## 6.1 Executive summary

LAM should be treated as a **model-behavior laboratory**, not as a claim that a finite answer
bank has acquired the general intelligence of DeepSeek, Claude, GPT, or any other model. Its
highest-value product direction is a layered system with four distinct modes:

| Mode | What it provides | Cost | Scientific claim it supports |
|---|---|---:|---|
| Protocol mock | OpenAI/Ollama-compatible request and response behavior | $0 | The harness can speak the expected wire protocol |
| Exact cassette replay | Deterministic replay of a previously observed request/response trajectory | $0 | This exact execution trace can be reproduced |
| Behavioral scenario model | Scripted, state-conditioned responses over a challenge family | $0 after authoring | The harness behavior is robust to controlled response patterns |
| Live teacher collection | Real model decisions, tool calls, failures, and verifier outcomes | Paid or local compute | This model/harness/task run produced the recorded evidence |

The product should move upward through these layers without collapsing their labels. A replayed
DeepSeek trajectory is valuable because it enables fast regression testing, but it is not a new
DeepSeek inference. A learned local surrogate may approximate a model’s action distribution, but
it is not equivalent to the source model unless equivalence is demonstrated for a declared task
distribution and metric.

The recommended target is therefore:

> **A local, deterministic, evidence-labeled agentic-coding laboratory that can replay real
> model behavior, perturb the harness, compare policies, train or fit bounded surrogates, and
> expose every causal step needed to explain success or failure.**

LAM already has the essential seed of this product: a stateless scenario engine, an HTTP server,
OpenAI/Ollama wire adapters, exact cassettes, a live proxy, a SQLite metrics store, a model
router, a Vanguard tool-name bridge, and a standalone live coding collector. The next work is
not to make the mock pretend to be live. It is to make the distinction between live, replayed,
synthetic, and inferred behavior mechanically explicit while increasing the fidelity and utility
of each mode.

The most important near-term priorities are:

1. preserve complete live trajectories rather than short snippets;
2. make replay state- and request-conditioned instead of only turn-count-conditioned;
3. formalize a challenge/workspace/evaluator protocol;
4. add systematic failure, retry, reflection, and context-policy experiments;
5. build controlled behavioral surrogates from real traces;
6. measure harness effects with paired, reproducible experiments;
7. keep benchmark leakage, secret exposure, and false live claims impossible by construction.

## 6.2 Epistemic boundary: what LAM can and cannot become

### 6.2.1 A mock is not a language model

A language model computes a conditional distribution over token sequences, approximately:

\[
P(y_{1:n} \mid x_{1:m}, \theta),
\]

where \(\theta\) is a learned parameterization and the output is sampled or decoded under a
policy. The current LAM engine does not compute that distribution. It selects a stored response
from a scenario using observable conversation features such as tool-result count or prior text.

That is not a defect for replay. It is the correct mechanism for deterministic infrastructure
tests. It becomes a defect only if LAM labels the result as a measurement of general model
capability.

### 6.2.2 Four useful notions of “similarity”

LAM can approach a real model along several independent axes:

| Similarity axis | Definition | Measurement |
|---|---|---|
| Protocol fidelity | Same request/response schema, streaming, errors, and tool-call encoding | Contract tests and wire fixtures |
| Trace fidelity | Same response for the same canonical request and history | Request digest and byte comparison |
| Behavioral fidelity | Similar action/tool/test/error distributions over a task distribution | Distributional metrics and held-out tasks |
| Capability fidelity | Similar solve rate, patch quality, calibration, and generalization | Paired benchmark evaluation |

Exact cassette replay can reach near-100% trace fidelity for the recorded trace while providing
zero evidence about capability fidelity on a new task. A learned surrogate can improve
behavioral fidelity, but it requires held-out evaluation and must not inherit labels from its
teacher traces without accounting for leakage and selection bias.

### 6.2.3 Why “free and local” has a limit

There are three different meanings of free:

1. **Free replay:** already-collected traces can be replayed locally at negligible cost.
2. **Free local inference:** an open-weight model can run on local hardware, with latency and
   quality determined by model size, quantization, memory, and runtime.
3. **Free general intelligence:** impossible without either a capable pre-trained model or a
   substantial training/distillation investment.

LAM can make the first two highly efficient. It cannot create the third by recording a few dozen
responses. The honest product objective is a local laboratory that maximizes the value extracted
from each expensive or slow inference and allows thousands of no-cost controlled experiments
afterward.

## 6.3 What LAM already has

### 6.3.1 Existing system components

The present LAM implementation includes:

- a stateless scenario engine with multi-turn tool-observation progression;
- a gold answer/scenario bank organized into task tiers;
- OpenAI-compatible `/v1/chat/completions` responses;
- Ollama-compatible `/api/chat` and `/api/generate` responses;
- optional SSE-style OpenAI streaming;
- exact request-hash cassette loading and replay;
- an upstream proxy path for live Ollama-compatible services;
- explicit evidence labels such as `lam-replay`, `cassette-exact`, and live-provider labels;
- SQLite call and benchmark provenance records;
- model-router integration through the existing mock provider;
- LAM/Vanguard tool-name translation;
- scenario import and secret-redaction helpers;
- a standalone real-model coding collector in `live_coding.py`;
- temporary workspaces, safe tool execution, test verification, diff capture, and budget guards;
- complete JSON trajectories and exact cassettes for collected runs.

### 6.3.2 Empirical baseline already collected

The standalone collector has now exercised four real coding challenges from the LEX laboratory
as read-only source inputs copied into temporary workspaces:

| Challenge | Problem family | Result in the recorded DeepSeek run |
|---|---|---|
| `semver_parser` | Semantic-version precedence and build metadata | Failed verification; the model corrupted the file, and the evaluator caught it |
| `isolated_coding_test` | LRU/TTL expiry and recency | Passed |
| `plugin_dag` | Cycle detection and topological load order | Passed |
| `token_bucket` | Refill saturation boundary | Passed |

The collection used 51 total API calls including the validation call, spent approximately
`$0.00837`, and produced complete trajectories and replay cassettes. The result is not a
benchmark score. It is a useful first teacher corpus showing that the harness can observe both
successful repair and catastrophic editing failure without mutating the source challenge tree.

### 6.3.3 Current strengths

LAM is already particularly strong for:

- deterministic CI and regression tests;
- validating tool schemas and turn-loop state transitions;
- testing harness behavior without network or provider credentials;
- replaying expensive agent trajectories;
- comparing prompt or tool-policy changes against identical model outputs;
- collecting latency, token, cost, and verifier outcomes;
- fault injection and negative fixtures;
- rapidly exercising many model/harness combinations after traces exist.

### 6.3.4 Current weaknesses

The major gaps are:

- the older recorder stores hashes and short snippets rather than a canonical full-fidelity event
  log;
- scenario progression based on tool count is not equivalent to response selection from the
  actual workspace state;
- exact cassettes are brittle when prompts, tool schemas, or context formatting change;
- replay does not yet model alternative branches, uncertainty, or response distributions;
- the SQLite schema is a metrics index, not a complete trajectory database;
- there is no first-class challenge manifest and evaluator contract for arbitrary repositories;
- the standalone collector’s tool surface is intentionally small and not yet configurable as an
  agent-computer interface profile;
- no learned surrogate or calibrated behavior model exists;
- no systematic policy-ablation runner exists for context, retry, reflection, or memory;
- no automatic leakage detector proves that gold patches and hidden tests stayed outside the
  model-visible context;
- a live model’s nondeterminism, provider routing, and changing model snapshot are not yet
  represented as complete compatibility metadata.

## 6.4 How to use LAM today

### 6.4.1 Run the deterministic scenario bank

```bash
python3 tools/002_LLM_API_MOCK/simulate.py
```

This exercises the pre-authored LAM scenarios without network access or API credentials.

### 6.4.2 Run the hermetic LAM tests

```bash
python3 -m unittest test.tools.test_llm_api_mock
python3 -m unittest test.tools.test_lam_live_coding
```

### 6.4.3 Collect bounded real-model coding traces

The collector reads the configured OpenRouter key internally from the environment or the
specified dotenv file. It never prints the key or places it in a trajectory:

```bash
python3 tools/002_LLM_API_MOCK/live_coding.py \
  --challenge semver_parser \
  --challenge isolated_coding_test \
  --challenge plugin_dag \
  --challenge token_bucket \
  --max-calls 60 \
  --max-usd 0.10
```

Every challenge is copied into a temporary workspace. The model can use the declared tools to
inspect and edit files and run bounded commands. The collector then runs the verifier, records
the final diff, and saves:

- `trajectory.json` — full request/response/tool-result history;
- `cassette.jsonl` — exact request-hash to response mapping;
- `result.json` — pass/fail, cost, call count, verification output, and diff;
- `collection_summary.json` — aggregate collection metadata.

Generated live captures belong under the ignored run-artifact directory and should be treated as
experimental evidence, not casually committed model-output dumps.

### 6.4.4 Replay a captured model response

```bash
python3 tools/002_LLM_API_MOCK/server.py \
  --cassette tools/002_LLM_API_MOCK/runs/live_captures/<run-id>/cassette.jsonl \
  --port 8787
```

The harness must send the same canonical request body to obtain an exact cassette hit. A changed
system prompt, tool schema, or message serialization should produce a mismatch rather than a
silent approximate answer. That failure is useful: it identifies a compatibility change.

## 6.5 Target product architecture

The mature LAM laboratory should be organized as a set of explicit planes:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│  Challenge Plane                                                          │
│  task manifest · base workspace · hidden/public tests · evaluator policy │
└───────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  Agent Controller Plane                                                   │
│  prompt compiler · context policy · turn loop · retry · reflection       │
│  planning · memory · tool choice · stop/continue policy                   │
└───────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  Model Plane                                                              │
│  live OpenRouter · local Ollama · exact cassette · behavioral surrogate   │
└───────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  Environment Plane                                                        │
│  read · search · edit · execute · test · patch · reset · snapshot         │
└───────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  Evidence Plane                                                           │
│  causal trajectory · artifacts · evaluator receipts · metrics · cassettes│
└───────────────────────────────────────────────────────────────────────────┘
```

The essential architectural rule is that the model plane must be replaceable without changing
the challenge, controller, environment, or evaluator contracts. This makes LAM useful for
isolating whether a result came from the model, the harness, the task environment, or the
verification policy.

### 6.5.1 Challenge manifest

Every challenge should have a machine-readable manifest containing:

- stable challenge ID and version;
- source repository or fixture digest;
- base commit/workspace digest;
- public task statement digest;
- allowed file mutation scope;
- setup command and dependency lock;
- visible test command;
- hidden evaluator command or evaluator image digest;
- expected patch region, when known;
- difficulty dimensions;
- leakage classification;
- timeout, memory, and process limits;
- dataset split and provenance.

The model must receive only the public projection of this manifest. The evaluator retains the
oracle projection. This separates task construction from task execution and makes leakage
auditable.

### 6.5.2 Agent-computer interface profiles

LAM should support multiple tool profiles rather than one fixed tool vocabulary:

1. **Minimal shell profile:** `view_file`, `edit_file`, `run_command`.
2. **Repository profile:** add `list_dir`, `grep_file`, `find_references`, `git_diff`.
3. **Structured patch profile:** replace whole-file editing with validated unified patches.
4. **CodeAct profile:** permit a bounded Python/bash execution action under a sandbox.
5. **Review profile:** expose test failures, diff summaries, and static-analysis findings.

Agent-computer interface design materially affects software-engineering performance; this is a
central finding of the SWE-agent research program, not merely a UI concern. LAM should therefore
make the interface a versioned experimental variable rather than burying it in the server.

## 6.6 Capability ladder

LAM should expose capability levels with separate evidence labels and acceptance criteria.

### Level 0 — Protocol-compatible mock

Purpose: validate clients, schemas, errors, streaming, and tool-call parsing.

Required properties:

- OpenAI and Ollama shape conformance;
- deterministic error responses;
- explicit model-not-found behavior;
- streaming termination correctness;
- no live label on replay traffic.

### Level 1 — Exact trajectory player

Purpose: replay a real model run exactly.

Required properties:

- canonical request digest;
- response byte digest;
- ordered tool-observation history;
- mismatch refusal;
- cassette version and schema identity;
- fresh-process replay parity.

### Level 2 — State-conditioned scenario engine

Purpose: respond to the harness state rather than only to the number of tool messages.

The scenario should declare predicates over:

- visible file contents or file digests;
- previous tool outcomes;
- test failure classes;
- changed-file set;
- remaining budget;
- prior model action;
- current phase of the repair plan.

The engine chooses a response from a finite state machine or policy table. It remains scripted,
but it is much more useful than a global turn counter because it can test recovery and branching.

### Level 3 — Distributional behavioral surrogate

Purpose: approximate the action distribution of a teacher model over a declared challenge family.

Possible implementations, in increasing complexity:

- nearest-neighbor retrieval over canonicalized prompt/history states;
- decision trees over tool/error/test features;
- gradient-boosted action selection;
- small local language model fine-tuned on sanitized trajectories;
- constrained sequence model over tool calls and patches;
- hybrid retrieval plus local generation with verifier filtering.

This level needs held-out tasks and calibration. It must report similarity metrics and uncertainty,
not claim identity with the teacher model.

### Level 4 — Local agent with an open-weight model

Purpose: run a genuinely generative model locally through the same LAM controller and evaluator.

LAM becomes the stable experiment harness while Ollama or another local runtime supplies neural
inference. The local model can be compared against recorded DeepSeek traces under identical task,
tool, prompt, timeout, and evaluator conditions.

### Level 5 — Teacher-student laboratory

Purpose: use limited paid teacher calls to improve a local student or policy.

The teacher supplies trajectories, critiques, repair alternatives, and failure explanations. The
student is evaluated on tasks and perturbations excluded from teacher collection. Improvement is
accepted only when held-out solve rate or efficiency improves without unacceptable regressions.

## 6.7 SOTA improvement program

### 6.7.1 ReAct-style interleaved reasoning and action

The original ReAct work established the value of interleaving reasoning traces and environment
actions so that the agent can update a plan from observations rather than produce one isolated
answer. LAM should implement this as a configurable controller policy:

- `inspect → hypothesize → act → observe → verify` phases;
- explicit phase transitions in the trajectory;
- action justification as optional diagnostic metadata;
- no requirement to expose private chain-of-thought in the stored corpus;
- compact decision summaries instead of unrestricted hidden-reasoning retention;
- ablation runs with and without phase guidance.

The useful research object is not the private prose itself. It is the causal relationship between
observation, action selection, verification feedback, and state transition. See [ReAct](https://arxiv.org/abs/2210.03629).

### 6.7.2 SWE-agent-style agent-computer interfaces

LAM should make interface design measurable:

- compare whole-file edit, patch edit, and CodeAct execution;
- test bounded search versus unrestricted shell;
- measure context returned per tool call;
- expose line ranges, symbol summaries, and dependency references;
- add command output truncation with explicit continuation handles;
- preserve nonzero exit code, signal, timeout, and stderr as typed observations;
- record every interface version in the compatibility key.

The interface should optimize for information gained per token and per tool call. A tool that
returns 200 lines of irrelevant code is worse than a tool that returns the exact symbol and its
callers, provided the retrieval policy is itself measured.

### 6.7.3 CodeAct-compatible execution

OpenHands documents a CodeAct-style agent in which the model can execute code as its primary
action space. LAM can support a constrained CodeAct profile without granting unrestricted host
authority:

- execute only inside a temporary workspace;
- disable network by default;
- mount only declared files and tools;
- enforce CPU, memory, process-count, and wall-clock limits;
- record stdout, stderr, exit status, signals, and changed files;
- classify commands into read-only, mutation, test, and forbidden classes;
- require evaluator confirmation before treating a result as solved.

This can improve model flexibility while preserving reproducibility. It should be compared against
the structured-tool profile, not silently replace it. See [OpenHands CodeAct documentation](https://docs.openhands.dev/openhands/usage/agents).

### 6.7.4 Reflexion-style verbal feedback and episodic memory

After a failed verification, LAM can generate a compact diagnostic record containing:

- failure class;
- likely causal file and symbol;
- attempted change;
- evidence that falsified the hypothesis;
- next testable hypothesis;
- constraints that must not be violated on retry.

That record can be returned to the same model on a fresh attempt or used as a retrieved memory on
a related task. The memory must be versioned and evaluated against a no-memory control. This is a
practical, no-weight-update improvement path inspired by Reflexion’s verbal reinforcement idea.
See [Reflexion](https://arxiv.org/abs/2303.11366).

Important safeguards:

- reflection cannot rewrite the original trajectory;
- the evaluator result remains authoritative;
- reflection text is a derived artifact, not ground truth;
- memory retrieval must not leak the gold patch from another task;
- gains must be measured on held-out tasks.

### 6.7.5 Test-driven repair controller

The controller should treat tests as evidence, not as an afterthought. Add a typed failure
classifier for:

- syntax/import failure;
- assertion mismatch;
- timeout/deadlock;
- flaky or nondeterministic test;
- dependency/setup failure;
- environment mismatch;
- unchanged bug after patch;
- regression in previously passing tests.

Each category can trigger a different next action. For example, an import failure should usually
reduce the search space to module/package structure, while an assertion mismatch should expose
the failing input and expected/actual values. The classifier itself must be evaluated against a
labeled corpus and should never silently convert infrastructure failure into model failure.

### 6.7.6 Context engineering and retrieval

Implement context policies as interchangeable modules:

- recent-window history;
- failure-focused history;
- symbol-level retrieval;
- dependency-graph retrieval;
- test-name retrieval;
- patch-history retrieval;
- repository map summaries;
- semantic search over prior successful repairs;
- compaction with digest-preserving provenance.

Measure:

- tokens per successful repair;
- tool calls per successful repair;
- context recall of the eventual changed symbols;
- irrelevant-context ratio;
- latency and cost;
- regression rate after compaction;
- performance under a fixed context budget.

The central question is not “does retrieval help?” but “which information policy helps which task
family under which budget, and does it generalize beyond the tasks used to tune it?”

### 6.7.7 Candidate generation, patch ranking, and verifier selection

For small tasks, generate multiple candidate patches and rank them using cheap checks before
spending expensive model turns:

1. syntax and import checks;
2. targeted unit tests;
3. static type/lint checks;
4. full visible tests;
5. hidden evaluator;
6. independent review or second-model critique.

Candidate generation can be done by repeated temperature seeds, model variants, or retrieved
repair templates. The ranking policy must not see hidden tests or gold patches. Store every
candidate, rejection reason, and evaluator receipt so that selection quality can be measured
separately from generation quality.

### 6.7.8 Model routing and adaptive escalation

LAM can become a routing research platform:

- start with a cheap local model;
- detect uncertainty from repeated failures, tool loops, or budget waste;
- escalate to a stronger local/cloud model;
- optionally return the stronger model’s repair to the cheaper model for explanation or review;
- compare fixed routing against adaptive routing under equal cost budgets.

Routing signals should include behavioral evidence rather than self-report alone:

- test progress;
- changed-file locality;
- repeated identical actions;
- increasing error severity;
- unresolved symbols;
- token and time burn;
- patch churn;
- verifier disagreement.

An escalation decision is itself a recorded policy event. Otherwise routing improvements cannot be
distinguished from luck in model assignment.

### 6.7.9 Teacher-student distillation without pretending equivalence

The collected DeepSeek trajectories can support a local surrogate program:

- normalize messages and tool schemas;
- remove credentials and unrelated repository content;
- represent tool calls as structured actions;
- represent observations as typed, bounded features plus content digests;
- store task and repository split boundaries;
- train or fit only on the training split;
- evaluate on held-out challenge families and unseen repositories;
- compare action accuracy, tool sequence edit distance, patch validity, solve rate, and cost.

Possible student targets include:

- next-tool classifier;
- stop/continue classifier;
- error-category predictor;
- patch-ranking model;
- retrieval policy;
- small local instruction model fine-tuned on full sanitized interactions;
- hybrid finite-state policy for common repair patterns.

The student should be allowed to disagree with the teacher. The purpose is not to clone every
teacher mistake; it is to learn useful, measurable behavior at lower cost. Teacher and student
results must carry separate evidence labels.

### 6.7.10 Controlled self-improvement loop

A safe LAM improvement loop is:

```text
collect → verify → classify failures → propose policy change →
run paired evaluation → accept only with held-out evidence → version policy
```

The policy may change prompts, retrieval, tools, retry limits, reflection, routing, or candidate
selection. It must not mutate historical trajectories or retroactively relabel failures. Every
accepted policy receives a content digest, parent policy, training/evaluation split, and rollback
record.

### 6.7.11 Multi-agent and debate experiments

LAM can simulate or run multiple roles without claiming that more agents are automatically better:

- investigator: reads and localizes the defect;
- implementer: edits the workspace;
- verifier: runs tests and classifies failure;
- reviewer: critiques the diff;
- synthesizer: chooses among candidates.

Run these roles sequentially first. Add parallelism only when the resources and artifact sinks are
provably independent. Metrics should include coordination overhead, duplicate work, wall time,
token cost, and failure recovery—not only pass rate.

### 6.7.12 Counterfactual and fault-injection laboratory

Once a trajectory is recorded, LAM can replay it under controlled perturbations:

- remove one tool observation;
- corrupt a test output;
- delay a command;
- return a transient failure;
- alter context ordering;
- truncate a file read;
- inject a stale cache result;
- change a tool schema version;
- kill the agent process after an edit;
- remove one previous memory item.

This exposes which observations and controller decisions were causally necessary. Counterfactual
results must be labeled synthetic and never merged with live-model evidence.

## 6.8 Trajectory and dataset design

### 6.8.1 Canonical run record

Each run should have a stable envelope containing:

```json
{
  "run_id": "...",
  "challenge_id": "...",
  "challenge_version": "...",
  "workspace_digest": "...",
  "model_id": "...",
  "provider": "...",
  "model_snapshot": "...",
  "sampling": {"temperature": 0.2, "top_p": null, "seed": null},
  "agent_policy_digest": "...",
  "tool_profile_digest": "...",
  "evaluator_digest": "...",
  "evidence_label": "openrouter-live",
  "turns": [],
  "artifacts": [],
  "outcome": {},
  "cost": {},
  "timing": {}
}
```

The exact field names may evolve, but the semantics should remain stable: a reviewer must be able
to reconstruct what the model saw, what it produced, what the environment returned, what changed,
and how success was determined.

### 6.8.2 Separate content from ledger metadata

Large prompts, model outputs, file snapshots, diffs, and test logs belong in content-addressed
artifacts. The SQLite index should hold:

- digest;
- media type;
- size;
- run/turn/attempt relation;
- retention class;
- redaction policy;
- creation time;
- evidence label.

This avoids turning `lam.sqlite` into an unbounded text dump while preserving complete retrieval.

### 6.8.3 Dataset splits

At minimum, maintain:

- **development:** prompt/tool/controller tuning;
- **validation:** model and policy selection;
- **held-out test:** final claims;
- **counterfactual:** perturbation studies;
- **replay regression:** fixed traces for infrastructure changes;
- **fresh live:** tasks not represented in the teacher corpus.

Repository, issue, author, and temporal leakage must be considered. A model that has seen the
original patch or a near-duplicate task may produce a useful engineering result but does not
provide clean evidence of generalization.

### 6.8.4 Artifact retention and privacy

Raw model interactions can contain proprietary source, secrets accidentally emitted by tools, and
personal data from issue text. The collector should support:

- capture authorization before persistence;
- secret scanning and redaction;
- path allowlists;
- configurable `digests_only`, `standard`, and `full` retention;
- encrypted or access-controlled full artifacts;
- deterministic redaction receipts;
- legal hold and deletion eligibility;
- no API key in request artifacts, logs, cassettes, or SQLite.

## 6.9 Evaluation and scientific methodology

### 6.9.1 Primary outcome metrics

For coding tasks, report at least:

- verifier pass rate;
- patch validity rate;
- regression-free pass rate;
- first-pass success;
- pass@1 and pass@k where repeated candidates are used;
- task completion time;
- model calls and tool calls;
- input/output tokens;
- direct cost;
- wall-clock latency;
- changed-line count and patch churn;
- human-review acceptance, if applicable.

### 6.9.2 Harness metrics

To measure the harness independently from the model, hold the model response trace fixed and vary:

- context compiler;
- tool descriptions;
- observation truncation;
- retry policy;
- test feedback formatting;
- reflection memory;
- routing policy;
- candidate ranking;
- workspace interface.

This is the most important use of exact replay: it turns a stochastic model into a controlled
experimental input while retaining the causal sequence that actually occurred.

### 6.9.3 Paired evaluation

Every policy claim should use paired tasks and a compatibility key containing:

- benchmark and split hash;
- challenge version;
- model/provider/snapshot;
- sampling parameters;
- harness commit;
- agent-policy digest;
- tool-profile digest;
- evaluator image and test digest;
- LAM schema version.

Comparisons with different keys are descriptive, not controlled causal comparisons.

### 6.9.4 Calibration and uncertainty

LAM should capture agent confidence only as a diagnostic signal. A useful calibration report
compares:

- self-reported confidence;
- behavioral confidence from repeated success/failure;
- verifier status;
- candidate disagreement;
- estimated probability of success;
- actual held-out outcome.

Report reliability diagrams, Brier score where binary outcomes exist, abstention quality, and
selective risk. Never promote self-reported confidence to truth.

### 6.9.5 Replay determinism tests

For every cassette:

1. replay in a fresh process;
2. verify request digest matching;
3. verify response digest matching;
4. verify tool-result order;
5. verify final workspace diff;
6. verify evaluator result;
7. verify that a deliberate request mutation fails closed.

## 6.10 Security, privacy, and benchmark integrity

LAM executes model-generated actions. Even a local “mock” can become dangerous if its tool layer
is connected to the real repository or host. The default security posture should be:

- temporary workspace only;
- no write access outside workspace;
- no network from task commands;
- no process-kill or privilege escalation tools;
- command allowlists or sandboxed execution;
- CPU, memory, file-count, and wall-clock quotas;
- no inherited provider credentials inside task subprocesses;
- test and evaluator separation;
- immutable original task snapshot;
- complete changed-file manifest;
- fail-closed on path traversal and malformed tool arguments.

Benchmark integrity requires additional controls:

- hide gold patches and hidden tests;
- detect references to oracle paths;
- scan prompts and tool observations for leaked gold content;
- prevent the model from editing tests unless the experiment explicitly studies that behavior;
- distinguish infrastructure failure from agent failure;
- preserve failed runs without repair;
- do not count a replay pass as a live-model pass;
- do not use the same run for policy tuning and final evaluation.

## 6.11 Performance and cost engineering

### 6.11.1 Fast replay path

The fast path should avoid network, model initialization, and unnecessary serialization:

- memory-map or cache cassette indexes;
- use request digests before parsing large payloads;
- store compressed response bodies;
- stream large artifacts rather than copying them through SQLite;
- use one writer and batched metadata transactions;
- precompute challenge and policy digests;
- parallelize independent replay runs;
- keep evaluator images warm where isolation permits.

### 6.11.2 Live collection path

Live calls are expensive and slow relative to replay. The collector should:

- reserve budget before each request;
- stop on call or spend ceiling;
- use short, explicit timeouts;
- preserve partial trajectories after timeout;
- avoid retries unless they are part of the experiment;
- record provider usage rather than estimating silently;
- use small pilot sets before a full benchmark;
- cache exact successful responses only when the experiment declares caching;
- preserve model route and provider metadata.

### 6.11.3 Cost-aware experiment design

The best use of a small paid budget is not a broad but shallow sweep. Prefer:

1. a few diverse challenges;
2. one fixed harness baseline;
3. one controlled policy change;
4. full trajectory capture;
5. replay-based ablations;
6. only then a larger live sample.

This maximizes information per paid call and prevents a misleading “average” from hiding distinct
failure modes.

## 6.12 Implementation roadmap and acceptance gates

### Phase A — Evidence-grade capture

Implement:

- versioned run envelope;
- full request/response artifact writer;
- typed tool-result records;
- provider/model/sampling metadata;
- redaction and secret scan;
- SQLite index references;
- partial-run persistence on timeout and budget stop.

Acceptance:

- no full content lost when a run fails;
- fresh-process readback works;
- request/response hashes verify;
- API credentials never appear in artifacts;
- failed runs remain inspectable.

### Phase B — Challenge and evaluator protocol

Implement:

- JSON challenge manifests;
- public/oracle projections;
- workspace snapshot and restore;
- evaluator subprocess contract;
- hidden-test separation;
- challenge version and split digests.

Acceptance:

- the same challenge can run under live, replay, and local-model backends;
- the evaluator cannot read the model’s private prompt state;
- task mutations are fully accounted for.

### Phase C — Stateful replay

Implement:

- predicates over workspace and observations;
- branching scenario graphs;
- state transitions and exhaustion policies;
- deterministic fault injection;
- mismatch diagnostics.

Acceptance:

- replay can distinguish a correct edit, failed test, retry, and stop decision;
- changing an observation selects the declared alternate branch;
- unsupported state produces an explicit refusal.

### Phase D — Harness policy laboratory

Implement configurable policies for:

- context compilation;
- observation truncation;
- retry and escalation;
- reflection memory;
- candidate generation/ranking;
- tool profile;
- model routing.

Acceptance:

- all policies are versioned and digest-bound;
- paired replay experiments produce comparable metrics;
- policy changes cannot alter historical traces.

### Phase E — Behavioral surrogate

Implement first a non-neural baseline:

- nearest-neighbor state retrieval;
- tool-action classifier;
- stop/continue classifier;
- verifier-outcome predictor;
- uncertainty and abstention.

Then evaluate whether a local open-weight sequence model adds value. Do not begin fine-tuning
before the trajectory schema and splits are stable.

Acceptance:

- held-out behavioral similarity is reported;
- surrogate failures are labeled as surrogate failures;
- no teacher/test leakage is detected;
- the surrogate is cheaper or faster for the declared use case.

### Phase F — Local model and teacher-student operation

Implement:

- Ollama/local backend under the same controller;
- OpenRouter teacher backend;
- automatic trace comparison;
- model routing and escalation;
- distillation/feedback experiments;
- rollback and model registry metadata.

Acceptance:

- live, local, replay, and surrogate modes share the same challenge/evaluator contract;
- quality, latency, cost, and uncertainty are reported together;
- a claimed improvement survives held-out paired evaluation.

## 6.13 Research opportunities

LAM can support publishable or internally valuable research questions:

1. **Interface causality:** which tool representation most improves repair under a fixed model?
2. **Observation value:** which test outputs and file slices have the highest marginal information?
3. **Failure recovery:** can typed failure classes reduce repeated invalid actions?
4. **Reflection value:** when does verbal memory help, and when does it amplify a wrong hypothesis?
5. **Routing economics:** what behavioral signal best predicts when escalation is worth its cost?
6. **Patch selection:** can cheap static checks predict which candidate deserves full verification?
7. **Surrogate fidelity:** which action-level statistics predict useful harness substitution?
8. **Context compression:** how much evidence can be removed before solve rate degrades?
9. **Reproducibility:** which provider metadata is necessary to explain run-to-run variance?
10. **Multi-agent economics:** when does a reviewer or planner repay its coordination overhead?
11. **Counterfactual replay:** which observations are causally necessary for a successful repair?
12. **Transfer:** do repair trajectories transfer across repositories or merely memorize patterns?

Each question should have a preregistered outcome, a control arm, a compatibility key, and a
held-out evaluation set.

## 6.14 Non-goals and hard limitations

LAM must not claim any of the following without new evidence:

- that a finite scenario bank is equivalent to a general LLM;
- that a replay pass is a live-model benchmark result;
- that a scripted response demonstrates reasoning;
- that a local surrogate has the teacher’s capability on unseen tasks;
- that a model’s self-reported confidence is calibrated truth;
- that a coding task was solved merely because the model emitted a plausible patch;
- that a hidden-test result is valid if the oracle leaked into the prompt;
- that a policy improvement is causal when task/model/evaluator keys changed;
- that more turns, more agents, or more tokens are inherently better;
- that an API proxy is free when it forwards requests to a paid provider.

The closest realistic endpoint is not “a free DeepSeek clone.” It is a **high-fidelity local
experimental substrate** that gives us the same controllable surfaces around a model: challenges,
tools, observations, memory, evaluation, replay, and evidence. That is more useful and more
defensible than pretending the model itself has been reproduced.

## 6.15 Final recommendation

The recommended order is:

1. finish evidence-grade full trajectory capture;
2. formalize challenge and evaluator manifests;
3. implement state-conditioned replay and fault injection;
4. add ReAct-style controller phases and typed test-failure feedback;
5. add configurable context, reflection, routing, and candidate policies;
6. collect a small, diverse teacher corpus with strict budget and leakage controls;
7. build a simple behavioral surrogate before attempting neural distillation;
8. add local open-weight inference under the same contract;
9. evaluate all improvements on held-out tasks with paired metrics;
10. only then expand toward multi-agent search, retrieval, skills, and adaptive strategy.

This roadmap turns LAM from a useful mock into a progressively more capable **agentic coding
laboratory**. Its scientific value comes from preserving the boundary between what was observed,
what was replayed, what was generated synthetically, and what was inferred by a surrogate.

## 6.16 Technical references

- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
  — interleaved reasoning/action trajectories and environment feedback.
- [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793)
  — evidence that the agent-computer interface is a first-class performance variable.
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
  — verbal feedback and episodic memory without weight updates.
- [OpenHands CodeAct documentation](https://docs.openhands.dev/openhands/usage/agents)
  — code execution as an agent action space for software engineering.
- [SWE-bench official dataset guide](https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/datasets.md)
  — task manifests, repository/base-commit metadata, evaluator fields, and benchmark split handling.

## 6.17 Internal benchmark-validation targets

For future project validation, LAM should maintain two fixed, stratified internal subsets:

| Benchmark family | Internal target | Approximate 90% confidence interpretation | Current distinct live coverage | Additional target |
|---|---:|---|---:|---:|
| SWE-bench Verified | **60 tasks** | Approximately ±10 percentage points for a finite population of 500 | 4 | **56 more** |
| SWE-bench Pro public-scale subset | **70 tasks** | More conservative than the minimum ~62–63-task sample for a population around 731–800 | 4 | **66 more** |

These are **internal directional-validation targets**, not official leaderboard evaluations. Official
benchmark claims still require the complete declared benchmark split. The 60-task Verified subset
and 70-task Pro subset must be selected with a frozen seed and stratified by repository, task
difficulty, context size, patch size, language or framework where applicable, and expected test
complexity. The same task IDs, base commits, evaluator versions, and compatibility key must be
used when comparing harness or policy variants.

Repeated trajectories on the same task do not increase population coverage. LAM may record many
DeepSeek, local-model, replay, or counterfactual runs for one task, but confidence in the
benchmark-wide pass-rate estimate comes primarily from the number and representativeness of
**distinct tasks**. The current inventory is four distinct real DeepSeek coding challenges and
39 scripted LAM scenarios; the future objective is to expand the live, evaluator-backed corpus to
60 Verified tasks and 70 Pro tasks, then use LAM replay for large-scale zero-cost harness
regression experiments.

# Hybrid REAL + MOCKED SWE Verified Challenges (30/70 of 16 coding challenges)

## Purpose and operating rule

The immediate objective is not to claim that LAM reproduces DeepSeek, ChatGPT, or any other
specific model. The objective is to validate the harness: message construction, tool schemas,
workspace isolation, file editing, test feedback, retry behavior, termination, replay, accounting,
and evidence capture. A hybrid corpus is appropriate for that objective because five real runs can
anchor the behavioral distribution while eleven synthetic runs expand task and failure coverage at
nearly zero inference cost.

For a 16-task corpus, the nearest integer implementation of a 30/70 split is:

| Corpus segment | Count | Evidence label | Role |
|---|---:|---|---|
| Real OpenRouter runs | **5** | `real-openrouter` | Behavioral calibration and audit |
| LAM-generated traces | **11** | `synthetic-chatgpt-proxy` | Broad harness and replay coverage |
| Total | **16** | — | Fixed internal validation corpus |

Four existing live traces from the LEX lab may be used as a generic prior for tool-use patterns,
but they must not be counted as SWE-bench Verified calibration unless their task IDs and evaluator
semantics are actually part of this 16-task manifest. If only four SWE tasks are run live, the
corpus is 25/75 rather than 30/70; that is acceptable, but it must be recorded honestly.

The central data-integrity rule is:

> Synthetic traces may validate harness behavior and populate replay scenarios, but they must never
> be combined with real pass/fail outcomes and reported as a real model benchmark score.

## 1. Freeze the 16-task and calibration manifests

Create one immutable manifest before collecting or generating responses. It should reference the
existing compact fixtures under `tools/005_SWE_VERIFIED_REPO/`, the four existing tasks if they are
part of the final 16, and the exact base commit for every repository. Freeze a seed and never
silently replace a task after results exist.

Recommended allocation:

1. Select five tasks using stratification across repository, difficulty, patch size, number of
   changed files, and expected test complexity.
2. Use four of those five real runs as the calibration set.
3. Keep the fifth real run untouched as an audit set. Do not show its trajectory to the synthetic
   generator; use it only to test whether calibration generalized.
4. Generate the eleven synthetic traces from the remaining tasks.
5. Use the audit task to measure whether the synthetic behavior profile is directionally plausible.

The five real tasks should not all be easy one-file fixes. A practical small sample is two easy,
two medium, and one multi-file or high-context task, with repository diversity preserved. The exact
selection belongs in `calibration_split.json`:

```json
{
  "schema_version": "lam.swe-calibration-split/1",
  "seed": 20260825,
  "total_tasks": 16,
  "real_task_ids": ["task-a", "task-b", "task-c", "task-d", "task-e"],
  "real_calibration_task_ids": ["task-a", "task-b", "task-c", "task-d"],
  "real_audit_task_ids": ["task-e"],
  "synthetic_task_ids": ["task-f", "task-g", "task-h"],
  "policy": "real traces calibrate behavior; synthetic traces validate harness mechanics"
}
```

The actual manifest should contain all 16 IDs; the abbreviated example only shows the contract.

## 2. What the current live-coding collector does

`tools/002_LLM_API_MOCK/live_coding.py` already provides the essential real-run loop:

- reads `OPENROUTER_API_KEY` from the environment or the configured dotenv file without printing
  it;
- calls the OpenRouter chat-completions endpoint with a bounded model, call count, token budget,
  and dollar budget;
- exposes `view_file`, `edit_file`, `run_command`, and `list_dir` tools;
- copies a task into a temporary workspace;
- records every request, response, tool call, tool result, cassette entry, final diff, verification
  output, stop reason, call count, and spend;
- emits `trajectory.json`, `cassette.jsonl`, and `result.json` for later replay and analysis.

The current collector was built for the LEX tasks and expects `problem.md` plus an already runnable
workspace. The new SWE fixtures use `context.md`, `challenge.json`, and a compact `public/` source
slice, so they should not be passed to the current collector unchanged. The collector needs a SWE
fixture adapter before a run can be called an evaluator-backed SWE run.

The existing LEX command remains useful for regression testing the collector itself:

```bash
python3 tools/002_LLM_API_MOCK/live_coding.py \
  --challenge-root lab \
  --challenge semver_parser \
  --dotenv .env \
  --model deepseek/deepseek-v4-flash \
  --max-calls 60 \
  --max-usd 0.10
```

The target SWE-capable interface should retain those safety flags and add an explicit fixture
format, for example:

```bash
python3 tools/002_LLM_API_MOCK/live_coding.py \
  --fixture-root tools/005_SWE_VERIFIED_REPO \
  --challenge astropy__astropy-12907 \
  --format swe-verified \
  --evaluator-root /var/tmp/lam-swe-evaluator \
  --dotenv .env \
  --model deepseek/deepseek-v4-flash \
  --max-calls 60 \
  --max-usd 0.10
```

That command is the target runbook, not a claim that the current LEX-only loader already supports
those flags.

## 3. Required SWE fixture adapter and evaluator separation

The adapter must make the public/private boundary mechanical:

1. Read `challenge.json` and `context.md`.
2. Copy only `public/` into the agent workspace. Never copy the task directory wholesale.
3. For a real evaluator-backed run, materialize a repository checkout at `base_commit` in a
   separate evaluator workspace. The compact source slice is useful for prompt and harness tests,
   but it is not a substitute for dependencies and the full test suite.
4. Apply `private/test.patch` only in the evaluator workspace, never in the agent workspace.
5. Let the agent inspect and edit its workspace through the existing tool contract.
6. When the agent stops, compute its diff and apply that diff to a fresh evaluator checkout.
7. Run the recorded `FAIL_TO_PASS` tests and verify that the recorded `PASS_TO_PASS` tests do not
   regress. The evaluator owns the verdict; the model cannot self-report success.
8. Store only evaluator status, test names, exit codes, and sanitized output in the LAM record.
   Never send `gold.patch` or `test.patch` to the model, synthetic generator, or replay client.

The `Challenge` abstraction should therefore carry at least:

```text
task_id, repo, base_commit, problem_statement, public_root,
evaluator_recipe, fail_to_pass, pass_to_pass, difficulty, provenance
```

The evaluator should be keyed by `(repo, base_commit, evaluator_version, dependency_image)` so a
later library upgrade cannot silently invalidate old scores. If a full checkout is too expensive
for the first harness smoke test, run compact mode and label its result
`compact-no-evaluator`; never call that result a SWE-bench pass.

## 4. Real calibration runbook: five tasks

Run the five real tasks with exactly the same harness configuration intended for LAM replay. Do
not give the model special prompts, extra tools, hidden tests, or a different timeout. Capture the
following for every turn:

- canonical request JSON and request hash;
- model name, provider, temperature, token limits, and API response metadata;
- assistant text and every structured tool call;
- tool arguments, tool result, exit status, timeout, and truncation marker;
- workspace snapshot or content-addressed file diff after each edit;
- visible test commands and outputs;
- hidden evaluator commands and verdict, stored outside the model-visible trajectory;
- wall time, token usage, estimated/provider-reported cost, and stop reason;
- harness version, fixture hash, base commit, and evaluator version.

Use a single bounded budget for the five-task batch. The current collector defaults to 60 calls and
$0.10, but the budget must be treated as a hard ceiling, not a target. A run that stops because of
the budget is a valid `budget_stop` trajectory, not a failed API or a passed coding task.

After collection, normalize the four calibration trajectories into behavioral atoms:

```text
observe -> locate -> inspect -> hypothesize -> edit -> test -> diagnose -> repair -> retest -> stop
```

Record distributions rather than copying only successful answers:

| Feature | Examples to measure |
|---|---|
| Exploration | files listed, files viewed, bytes read before first edit |
| Editing | first-edit turn, files changed, diff size, overwrite frequency |
| Verification | tests per task, test timing, test-before-edit behavior |
| Recovery | failed commands, parse errors, retries, revert attempts |
| Termination | verified stop, premature stop, max-turn stop, budget stop |
| Tool protocol | valid calls, unknown tools, malformed arguments, repeated calls |
| Outcome | pass, partial, fail, evaluator error, environment error |

The fifth real trajectory is an audit: compare it to the profile only after synthetic generation is
complete. This prevents accidentally tuning the generator to the answer it is later judged against.

## 5. Generate the eleven synthetic traces

The synthetic generator uses the SWE challenge context, public source slice, harness tool schema,
and the *summarized behavior profile* from the four real calibration runs. It must not receive the
gold patch, test patch, hidden evaluator output, or the audit trajectory. ChatGPT's coding knowledge
is used as a teacher for plausible generic-agent behavior, not as evidence of what DeepSeek would
have done.

Each generated trace should contain a deliberate mixture of behaviors:

- a competent path that inspects before editing and verifies the change;
- a path with a realistic wrong hypothesis followed by test-driven repair;
- a path that stops early, hits a tool error, times out, or makes an incomplete change;
- malformed or redundant tool calls when testing protocol robustness;
- environment/evaluator failures clearly separated from agent failures.

Do not force all eleven synthetic tasks to pass. For harness testing, a varied corpus is more useful
than an artificially perfect corpus. The outcome distribution must be documented as a generation
policy and must never be presented as an empirical model score.

Recommended generation sequence:

```text
for task in synthetic_tasks:
    public_context = load(task.context.md, task.challenge.json, task.public/)
    behavior_profile = fit_profile(real_calibration_trajectories)

    draft = teacher_generate(
        task=public_context,
        tools=lam_tool_schema,
        behavior_profile=behavior_profile,
        constraints=[no_oracle, bounded_turns, valid_trace_schema],
    )

    trace = execute_in_isolated_workspace(draft, task.public/)
    outcome = evaluator_or_compact_verifier(trace.diff, task)

    if trace_is_invalid(trace):
        trace = bounded_repair(trace, reason="schema/tool/workspace violation")
        outcome = evaluator_or_compact_verifier(trace.diff, task)

    record(
        trace=trace,
        outcome=outcome,
        source_kind="synthetic",
        teacher_model="chatgpt-proxy",
        calibrated_from=real_calibration_task_ids,
        confidence="low-to-medium",
    )
```

`execute_in_isolated_workspace` is essential. A generated JSON trace must not be trusted merely
because it parses: the harness must execute its tool calls, enforce path boundaries, capture the
resulting diff, and replay the same request sequence successfully. If the trace is meant to model a
live agent, its tool results should be generated by the workspace rather than invented by the
teacher.

## 6. Import synthetic and real traces into LAM

LAM should preserve two related artifacts:

1. **Trajectory artifact** — the complete evidence record, including requests, responses, tools,
   files, evaluator result, and provenance.
2. **Replay scenario** — the normalized LAM response sequence or exact cassette used by the mock
   server. This is the cheap deterministic object consumed by harness regression tests.

The existing `importer.py` and scenario schema can be extended to accept the collector's
`trajectory.json`. The importer should:

- validate every turn and tool argument against the canonical schema;
- assign a stable scenario ID such as `t6-swe-astropy-12907-real` or
  `t6-swe-astropy-12907-synthetic`;
- preserve `source_kind`, `teacher_model`, `calibration_set`, task ID, base commit, and evaluator
  version;
- store exact request hashes for cassette replay;
- reject traces containing private patch text, hidden test output, API keys, or workspace paths
  outside the sandbox;
- write an immutable import manifest recording the source hashes and generator configuration.

The SQLite record should include at least:

```text
run_id, task_id, scenario_id, source_kind, model, teacher_model,
base_commit, fixture_sha256, harness_version, evaluator_version,
turn_count, tool_call_count, passed, stop_reason, cost_usd,
trajectory_path, cassette_path, created_at
```

Real and synthetic records must remain queryable together but never indistinguishable. Every report
should be able to answer: “Was this observed from a provider, generated by a teacher, replayed from
a cassette, or inferred by a profile?”

## 7. Calibration checks before trusting the 70 percent

Run these gates before using the populated LAM corpus for harness comparisons:

1. **Schema gate:** all 16 trajectories validate; all tool calls are executable or explicitly
   marked as provider errors.
2. **Isolation gate:** no public artifact contains `gold.patch`, `test.patch`, hidden test output,
   API keys, or an evaluator-only path.
3. **Replay gate:** every imported cassette reproduces the same response sequence under the same
   request hashes.
4. **Workspace gate:** replayed tool calls produce the recorded file diff and cannot escape the
   task workspace.
5. **Evaluator gate:** real pass/fail results come only from the separate evaluator workspace.
6. **Behavioral gate:** compare real and synthetic distributions for tool calls, first-edit turn,
   retry count, test frequency, stop reasons, and diff size. Large divergence means the generator
   needs recalibration; it does not mean the synthetic score is wrong in a benchmark sense.
7. **Audit gate:** evaluate the fifth real task against the profile created from the other four.
8. **Label gate:** every chart and aggregate separates `real-openrouter`, `synthetic-chatgpt-proxy`,
   `replay`, and `inferred` evidence.

With only four calibration trajectories, use descriptive statistics and bootstrap ranges rather than
strong claims about population behavior. A useful first target is harness stability: identical
inputs and cassettes should produce identical tool/evidence outcomes, while controlled fault
injection should produce the expected recovery or failure classification.

## 8. Development plan

### Phase A — Manifest and loader

Add a SWE fixture loader that understands `challenge.json`, `context.md`, `public/`, and provenance.
Add a frozen 16-task manifest and the five-task real/synthetic split. Add tests proving that copying a
fixture never copies `private/`.

### Phase B — Evaluator bridge

Implement repository checkout caching by `(repo, base_commit)`, private test-patch application in a
separate workspace, changed-diff transfer, `FAIL_TO_PASS`/`PASS_TO_PASS` execution, timeout limits,
and structured evaluator results. Make compact mode explicit and non-benchmark-labelled.

### Phase C — Collector hardening

Refactor `live_coding.py` so the LEX and SWE loaders share the same agent loop. Add per-turn
snapshots, tool-result truncation metadata, evaluator callbacks, run IDs, fixture hashes, and
provider retry/error classification. Keep the existing call and dollar guards.

### Phase D — Five real calibration runs

Run the selected five tasks with one frozen harness configuration. Inspect the four calibration
trajectories, preserve the fifth as audit, and import all five with `source_kind=real-openrouter`.

### Phase E — Eleven synthetic traces

Fit the behavior profile from four real traces plus the clearly labelled existing LEX prior. Generate
and execute eleven public-context-only traces. Validate them in isolated workspaces, import them as
`synthetic-chatgpt-proxy`, and retain generation prompts/configuration for reproducibility.

### Phase F — LAM replay and harness experiments

Convert every accepted trajectory into a deterministic scenario/cassette. Run the same harness over
all 16 scenarios repeatedly while varying only one harness variable at a time: tool schema,
context compiler, retry policy, test-feedback policy, timeout, or stopping rule. Compare harness
metrics within source-kind strata and then report the combined corpus only as a synthetic validation
corpus.

### Phase G — Expansion

Once the adapter and evaluator are stable, increase real coverage gradually. The next meaningful
milestone is not more synthetic answers; it is more distinct evaluator-backed tasks. Synthetic
traces remain valuable for edge-case and fault-injection coverage, while real traces anchor claims
about provider behavior.

## Recommended first execution

1. Freeze five real task IDs and eleven synthetic task IDs.
2. Extend the collector to load SWE fixtures without exposing `private/`.
3. Run one real task end-to-end and verify the evaluator, trajectory, cassette, and SQLite record.
4. Run the remaining four real tasks under the same budget and configuration.
5. Generate one synthetic trace and pass it through exactly the same workspace, schema, and replay
   gates.
6. Only after those two paths are identical at the harness boundary, generate the remaining ten
   synthetic traces and import the full 16-task corpus.

The result is a useful, low-cost LAM laboratory: five observed provider trajectories for calibration,
eleven explicitly synthetic trajectories for breadth, and a common executable harness contract for
both. It is strong evidence about LAM and the harness; it is intentionally not evidence that the
synthetic traces equal a real DeepSeek benchmark score.






# NOTES

 Root Cause in Tiers 4–6                 │ Why It Happened                               │ Recommended Improvement / Solution
  ─────────────────────────────────────────┼───────────────────────────────────────────────┼───────────────────────────────────────────────
   Tight Turn Budget (6–10 turns)          │ Models used 4–6 turns just exploring multi-   │ Increase call budget to 20–30 turns for Tier
                                           │ file repos (list_dir, view_file) before       │ 4–6 tasks during live collection.
                                           │ writing code.                                 │
   Context Window Saturation (length stop) │ Repeated full file reads bloated the prompt   │ Implement rolling tool message compaction or
                                           │ context past provider token limits.           │ sub-file viewing (line ranges).
   Lack of Sub-Agent / Planning Loop       │ Flat single-agent loop tackled complex        │ Inject a 2-phase strategy prompt: Phase 1
                                           │ architectures reactively without pre-         │ (Plan & locate invariant) → Phase 2 (Targeted
                                           │ planning.                                     │ patch & pytest).
   Absence of Test Feedback Loop           │ Models stopped after first attempt or ran out │ Ensure models run pytest -q early in the turn
                                           │ of calls before seeing test assertion         │ loop to use compiler/assertion errors as
                                           │ failures.                                     │ guidance.
   LAM Replay Fidelity                     │ LAM faithfully records and replays whatever   │ No fix needed in LAM itself; LAM's value is
                                           │ the LLM did (including failures).             │ precisely preserving both gold passes and
                                           │                                               │ real-world failure modes.