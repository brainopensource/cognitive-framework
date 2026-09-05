---
id: report.electroweak-v092.sol-terra-final
class: report
authority: non-canonical
status: observed
owner: coding-product-prototyping
created: 2026-09-04
consolidates:
  - report.electroweak-v092.terra-solution
  - report.electroweak-v092.sol-solution
---

# SOL + Terra final: evidence-driven route to a useful AETHER coding CLI

## Consolidation method and scope

This is a non-lossy substantive consolidation of the preceding SOL and Terra
reports. It retains every observation, benchmark result, limitation, proposed
repair, and validation outcome from both reports. Where the reports observed
different repository subjects, task fixtures, commands, or times, this report
preserves them as separate evidence rows rather than averaging or choosing one
as the current truth.

| Source record | Inspected subject | Evidence status |
|---|---|---|
| Terra | HEAD `d3890ce03500c0cef3ce0b027eac583be096c57e` | Dirty checkout; local run and retained artifacts. |
| SOL | `feat/strongforce_beta_release_v093` at `ffc3dc926e80dd67ca4941aecbede01b7291133f` | Dirty checkout; local run and retained artifacts. |

The LDA summary/generated metadata were stale for the SOL inspection and were
not treated as authority. Navigation and conclusions instead relied on current
canonical execution documents, targeted source/tests, Git state, process and
server output, durable ledgers/blobs, and retained benchmark artifacts. An
index is a routing aid, not evidence or architectural authority.

Evidence labels used below:

| Label | Meaning |
|---|---|
| `LIVE-LOCAL` | Executed against native llama.cpp during an assessment. |
| `LIVE-HISTORICAL` | Retained live-provider artifact from an older subject. Diagnostic, not a current product score. |
| `REPLAY` | LAM/cassette/deterministic evidence. Tests plumbing, not intelligence. |
| `STATIC` | Source, tests, documentation, or Git inspection. |
| `UNDETERMINABLE` | No valid provider attempt occurred; never score it as model failure. |

No paid DeepSeek or GLM request was made or charged by either assessment. No
OpenRouter request was made in the current local assessments because no
`OPENROUTER_API_KEY` was available. No legacy local-provider command was used
after native-only policy correction.

## Executive decision

The project has enough substrate to prototype a coding agent now. Do not build
another framework, agent hierarchy, provider abstraction, swarm/topology,
memory/learning system, kernel coding semantics, AST layer, or UI. The shortest
credible vertical slice is:

```text
native Vulkan llama-server (Qwen 27B)
  -> existing OpenAI-compatible LlamaCppModel
  -> one existing EpisodeEngine and code pack
  -> read/search/patch/test
  -> external oracle
  -> durable, honest terminal receipt
```

`llama-server` is a viable local engine and the local adapter exists. The
product command is not yet usable because it can return `completed` without a
source mutation, executed test, or passing oracle. That false-success class was
reproduced using both a deterministic fake route and native Qwen. It is a
harness truthfulness defect, not evidence that Qwen can or cannot solve coding
tasks.

The immediate priority order is:

1. Make false completion impossible on the public coding command.
2. Give every new invocation a unique run ID; resume must be explicit.
3. Normalize one strict llama.cpp/Qwen tool-call dialect into the existing
   canonical proposal contract, with typed recovery on malformed output.
4. Make `llama-bridge` and MCP fail closed and prove process/model identity.
5. Establish a tiny externally-oracled coding baseline through the exact public
   CLI before comparing models or adding framework capabilities.

This report authorizes no milestone, board task, or package promotion. In
particular it does not close MS-SEE/MS-CHANGE, authorize T-04, promote T-21,
T-46, or T-47–T-49, or imply that package 0.9.3 is M-9.

## What exists today

| Layer | Existing implementation | Observed assessment |
|---|---|---|
| Operator surface | TypeScript `vg` / `aether` CLI; compiled `vanguard/clients/cli/dist/src/main.js` was executed. | A real command path, but help, identity, model-route telemetry, and success semantics are not product-grade. |
| Product app | `CodingMaxFacade` over `ApplicationService`, exposing `run`, `status`, `resume`, `evidence`, `cost`, and `fast`/`balanced`/`max` presets. | Correct thin-app direction; a public legacy/default path bypasses required settlement behavior. |
| Agent loop | `EpisodeEngine`. | Keep this one loop; do not replace it with Forge, Chimera, or a swarm. |
| Coding behavior | `packs/code-default/` and `vg-code-*` manifests. | Read/search/patch/terminal vocabulary exists. |
| Runtime | `runtime/entrypoint.py`, profiled composition, SQLite WAL ledger/blob storage. | Durable events are produced, but a terminal interpretation can be false. |
| Local model | `LlamaCppModel`, using OpenAI-compatible `127.0.0.1:8080/v1/chat/completions`. | Focused transport and selection contracts pass; live dialect integration is blocked. |
| Hosted seam | OpenRouter adapter/routing. | Enough seam for future DeepSeek, GLM, and free-route comparisons. |
| Verification | Coding admission/oracle mechanisms and tamper shield. | Mechanisms exist, but `vg-code-default` is exempt under proposed T-04 work and the `session._tamper_shield.evaluate(...)` join must be wired. |
| Benchmarking | BAAC, ladder artifacts, RF-95, LAM/cassettes. | Valuable diagnostic pieces, but not all exercise the same subject or product runtime. |

The central architectural fact is that native llama.cpp is not a second
intelligence plane. It is a `ModelPort` implementation feeding the existing
canonical loop.

## Native llama.cpp environment

### Verified local foundation

```text
binary:      /home/rock-dev/.local/bin/llama-server
version:     0.3.0-dev, build 10796, commit 9a4843cf2
backend:     native Vulkan
GPU:         AMD Radeon RX 9060 XT, 16 GB VRAM
endpoint:    http://127.0.0.1:8080/v1
model:       Qwen3.8-27B-UD-Q2_K_XL.gguf
format:      Q2_K - Medium
parameters:  27,320,697,856
context:     8,192
slots:       4
observed process during Terra run: PID 90853
```

`llama-bridge models` found the following model files:

| GGUF | Disk size | Practical role |
|---|---:|---|
| `Qwen3.8-27B-UD-IQ1_M.gguf` | 6.27 GB | Lowest memory, highest quantization-risk arm. |
| `Qwen3.8-27B-UD-Q2_K_XL.gguf` | 9.15 GB | Current balanced local baseline. |
| `Qwen3.8-27B-UD-Q4_K_S.gguf` | 14.30 GB | Higher-quality candidate; tight on 16 GB after KV/cache overhead. |

Single-request server observations were approximately 458–477 prompt
tokens/second for ~2,000-token prompts and 22.6–23.0 generated tokens/second.
One Terra CLI request recorded 1,982 prompt tokens at 458.34 tokens/second,
54 output tokens in 2.343 seconds, and 6.667 seconds model time. These are
useful P0 engineering figures, not a throughput distribution or quality score.

### Correct operating rule

All local calls must use native `llama-server` at the endpoint above. The
documented product route is `--provider llama_cpp --planner local-model` (an
optional documented `local` alias is reasonable). Residual retired provider
aliases/environment names should be removed in one contained migration, along
with their tests and documentation; only `VANGUARD_LLAMA_ENDPOINT` and
`VANGUARD_LLAMA_MODEL` should remain. Do not reintroduce a legacy local daemon
or its fallback paths.

## Skill, bridge, CLI, and MCP review

### Scorecard

| Component | Works | Friction or defect | Verdict |
|---|---|---|---|
| `llama-cpp` operational skill | Correct binary, model folder, endpoint, GPU policy, and native-only route. | Its `--jinja` launch recipe is not exposed by bridge `serve`; it presents provider readiness more confidently than live integration supports. | Good operational start; add executable truth checks. |
| `llama-bridge models` | Quickly finds all three GGUF paths and sizes. | Machine-specific roots/current directory and no JSON mode. | Useful prototype. |
| `llama-bridge status` | `/health` and `/props` give health/model/context. | Loopback forbidden/refused/timeout all appear as `OFFLINE`; human output hides useful props. | Usable, weak diagnostics. |
| `llama-bridge chat` | Temperature/min-p, streaming, JSON schema, and telemetry; valid constrained output observed. | Silent while loading/generating; invalid schema only warns and then runs unconstrained. | Good interface, unsafe failure semantics. |
| `llama-bridge serve` | Model discovery and compact launch command. | Invalid Flash Attention syntax and critical lifecycle/process-identity bug. | Unsafe until fixed. |
| `llama-bridge stop` | Stops a recorded bridge PID. | Missing PID file falls back to broad `pkill -f llama-server`, which could kill unrelated servers. | Unsafe for automation. |
| MCP discovery | stdio `initialize`/`tools/list` returned four documented tools. | Registered for Gemini but not exposed in this Codex session's MCP registry. | Protocol works; client registration is incomplete. |
| MCP status/models | Health and discovery work via JSON-RPC. | `llama_status` can dump an enormous raw chat template. | Functional, context-inefficient. |
| MCP tokenize | Exact tokenizer returned count 10 for test prompt. | Raw token IDs do not supply context budget/headroom. | Useful primitive, poor UX. |
| MCP chat | Reaches model and returns latency/usage. | Empty/max-token completion returned as success. | Must fail closed. |
| AETHER local route | Selects `llama_cpp`; adapter contracts are green. | Tool intent was non-executable and episode falsely completed. | Integration blocker, not engine blocker. |

### Bridge lifecycle falsifier

The following request was issued (variation of the Q2 launch):

```bash
llama-bridge serve \
  -m Qwen3.8-27B-UD-Q2_K_XL.gguf \
  -c 8192 -ngl 99 --flash-attn \
  --ctk q8_0 --ctv q8_0 --alias local-model -d
```

The bridge said a child was launched and online (one observed claimed PID was
`102746`; another launch reported `95000`). The child log instead said:

```text
error while handling argument "-fa": unknown value for --flash-attn: '-ctk'
usage: -fa, --flash-attn [on|off|auto]
```

This build requires a Flash Attention value. The bridge emitted bare `-fa`,
then probed only the shared port; an already-running Q2 server (Terra observed
PID `90853`) satisfied health and was misattributed to the failed child. The
bridge PID file stayed stale.

Required contained repair:

1. Accept and emit `--flash-attn on|off|auto`, or omit it; `auto` is the safe
   explicit P0 choice.
2. Reject an occupied port, or explicitly adopt it only after verifying owner,
   process start time, model path, alias, and `/props` identity.
3. Require `child.poll() is None`, expected child PID, and matching props
   before saying `ONLINE`.
4. On launch failure, remove the PID file and show bounded final log lines.
5. Make `stop` terminate only an identity-verified recorded child; never use a
   global process-name kill.
6. Return structured status: `ONLINE`, `REFUSED`, `FORBIDDEN`, `TIMEOUT`,
   `PID_STALE`, and `MODEL_MISMATCH`.

The safe direct launch shape is:

```bash
llama-server \
  -m /home/rock-dev/Models/Qwen3.8-27B-UD-Q2_K_XL.gguf \
  -c 8192 -ngl 99 -t 16 --flash-attn auto \
  --host 127.0.0.1 --port 8080 --alias local-model --jinja
```

## Local inference and MCP probes

### L0 / B1: constrained structured output — PASS (`LIVE-LOCAL`)

Two independently constrained probes show that the engine can obey a small
JSON contract. These prove a shape-level capability, not coding autonomy or
semantic truth.

| Probe | Input | Constraint | Actual output | Result |
|---|---|---|---|---|
| SOL L0 | Extract package/version from `package ripgrep @ 14.1.0`. | Object with `name`, `version`, no extra keys; temp 0.2, min-p .05, max 128. | `{"name":"ripgrep","version":"14.1.0"}` | PASS; 79 prompt / 121 completion tokens, 6.14 s. |
| Terra B1 | Select first safe action for Fibonacci task. | `action="fs.read"`, `path="TASK.md"`, string reason, no extra keys; temp .2/min-p .05. | `{"action":"fs.read","path":"TASK.md","reason":"Read the task description to understand the requirements for implementing fibonacci.py."}` | PASS. |

Grammar/JSON schema decoding can guarantee syntax/shape, not semantic
correctness. Min-p reduces the candidate-token set; it does not eliminate
hallucination and must never replace an external verifier.

### L1: MCP structured planning — FAIL (`LIVE-LOCAL`)

The MCP `llama_chat` request asked for exactly two ordered JSON planning steps
for `fibonacci.py`, with a two-item schema, temperature .2, min-p .05, and a
192-token cap. It returned:

```json
{
  "content": [{"type":"text","text":""}],
  "telemetry": {
    "latency_seconds": 9.477,
    "usage": {"prompt_tokens":66,"completion_tokens":192,"total_tokens":258}
  }
}
```

The model apparently used the output budget in non-visible reasoning; the
wrapper treated empty visible content as success. Attribute configuration and
model behavior separately from the boundary: MCP must return a typed
`EMPTY_COMPLETION` or `MAX_TOKENS_WITHOUT_CONTENT` error, and permit one
bounded retry with thinking disabled or a sufficient output budget. Invalid
JSON schema must similarly fail closed, not warn and continue unconstrained.

## Coding-task benchmark evidence

### Shared FIB-P0 fixture used by Terra

The Terra falsifier used a disposable workspace with this input:

```text
Create fibonacci.py with fibonacci(n), preserve the provided test,
and run python3 -m unittest -v.
```

Oracle:

```text
fibonacci(n) returns [0, 1, 1, 2, 3, 5, 8, 13] for n=0..7
fibonacci(-1) raises ValueError
```

Fixture fingerprints:

```text
TASK.md            5a06859e03efb6271d586b6f5893f6704be9297d49a52f59aaf6bcc9af213359
test_fibonacci.py  67bc792e9cf5641e75aa1a6cd17aa1e8954d26f2bf04f59d02892575f6927c4c
```

No agent episode created `fibonacci.py`; the oracle failed with
`ModuleNotFoundError: No module named 'fibonacci'`.

### B0: deterministic false-completion falsifier (`REPLAY`)

The exact public `vg code` path was invoked on FIB-P0 with the deterministic
`fake` route. Output was:

```json
{"kind":"note","text":"fake-default"}
{"kind":"complete","outcome":"completed","turns":1}
```

The workspace contained only `TASK.md`, `test_fibonacci.py`, and runtime
artifacts. It had no patch, terminal command, or verification and the oracle
failed. This is a direct harness falsifier: a bare model finish cannot settle
an implementation task as success.

### B2: Terra end-to-end Fibonacci episode (`LIVE-LOCAL`)

Command:

```bash
node vanguard/clients/cli/dist/src/main.js code /tmp/aether-llama-p0-P3LI7X \
  --brief "Create fibonacci.py with fibonacci(n), preserve the provided test, and run python3 -m unittest -v." \
  --provider llama_cpp --planner local-model --profile local --benchmark \
  --run-id llama-p0-fibonacci-001 --max-turns 4 --json
```

The process was independently bounded at 180 seconds but ended after one turn.
It emitted:

```json
{"kind":"note","text":"{\"properties\": {\"action\": \"search\", \"args\": {\"path\": \".\", \"pattern\": \"fibonacci\", \"max_results\": 50}, \"kind\": \"effect\"}}"}
{"kind":"complete","outcome":"completed","turns":1}
```

The retained SQLite trajectory was:

```text
seq 0   EpisodeStarted   composed
seq 49  TurnStarted      turn_opened
seq 54  ProposalProduced {"properties":{"action":"search",...}}
seq 55  EpisodeCompleted completed
```

There was no `EffectStarted`, `EffectCompleted`, `patch.apply`, or `proc.exec`.
No file was created and the FIB-P0 oracle failed.

### L2: SOL end-to-end Fibonacci + CLI episode (`LIVE-LOCAL`)

The independent SOL fixture at `/tmp/aether-native-9QZ2JmVD` asked:

```text
Create fibonacci.py in the repository root. It must expose fib(n: int) -> int,
reject negative n with ValueError, and when run as a CLI with --n 10 print 55.
Create tests and run them.
```

Provider was `llama_cpp`, planner `local-model`, profile `local`, requested
eight turns. The model-facing terminal detail began:

```text
I'll start by inspecting the workspace...

<tool_call>
<search>
<path>
.
</parameter>
...
</search>
```

The XML-like tags were malformed and did not match a canonical OpenAI
tool-call object. Nonetheless the CLI emitted:

```json
{"kind":"complete","outcome":"completed","turns":1}
```

Its receipt had `verifiedStepIds: []`, `modelRoutes: []`, null prompt and
completion tokens, and null spent microdollars. The workspace had only
`.vanguard/events.sqlite3` and two blobs—no module, tests, patch, or passed
verification.

### Attribution matrix for B2/L2

| Observation | Attribution | Meaning |
|---|---|---|
| JSON-shaped `properties` wrapper / `search` does not match declared action. | Model-to-dialect integration. | Could arise from Qwen template, prompt, normalization, or Q2 formatting; it is not a code-quality score. |
| Malformed XML-like Qwen call. | Model/dialect join. | The template asks for XML style while AETHER expects canonical structured calls. |
| Invalid output becomes note/prose, not a typed reject-and-repair state. | Harness/recovery. | The loop gives no corrective attempt. |
| `completed` with no mutation, tests, or passing oracle. | Critical harness/admission. | Reproduced by fake and Qwen; critical false positive. |
| Empty model routes, tokens, and cost in receipt. | Harness telemetry. | Prevents cost, provider, and efficiency measurement. |
| No valid action occurred. | Evaluation method. | Neither local episode measures general Qwen coding competence. |

### Excluded identity collision

An earlier local episode omitted `--run-id`; `runtime/entrypoint.py` defaulted
to `run-cli`, the fixed ID used by a prior fake episode. It recovered the old
ledger and ended abandoned with `max_turns (1) exhausted across approval`, with
no fresh proposal. It is excluded from all model-quality judgments. The product
must generate UUID/ULID IDs for new runs and require explicit `--resume <id>`
for recovery, returning the generated ID in the initial JSON frame and receipt.

## Hosted and replay benchmark evidence

All rows below are retained artifacts unless explicitly called `LIVE-LOCAL`.
They must not be mixed into a current CLI score.

| Artifact / arm | Observed result | Correct interpretation |
|---|---|---|
| Terra `benchmark_20_results.json`, DeepSeek V4 Flash `vg-code-max` | 2/21 pass rows, 19 fail; reported 9.5%; every row max one turn; $0.002037; 77.4 s. | Diagnostic only: custom runner, not the exact public runtime. |
| SOL `benchmark_20_deepseek_v4_flash.json` | 0/20, one turn each, zero model tokens/cost, no patch. | Invalid as a DeepSeek-quality score: no usable model execution. This is a distinct artifact, not a contradiction to Terra's 21-row file. |
| DeepSeek V4 Flash BAAC `fib_cli`, `vg-1-forge` | 1/1 pass; 8 turns; 15,877 prompt + 3,324 completion tokens; 93.34 s; $0.001191; three retained oracle tests pass. | Promising historical evidence through an experimental harness; Forge is excluded from Coding Max scores and n=1 is weak. |
| DeepSeek V4 Flash v3luna SOTA-easy config precedence | 1/1 pass; 10 calls/turns; 24.32 s; $0.001829; two files modified. | Promising historic runner compatibility; incomparable until task/harness/subject are frozen. |
| OpenRouter `free`, SOTA-easy | 0/1; four task calls (five report total); 38.96 s; no files; HTTP 400. | Request/provider compatibility, not a named-model quality failure; `openrouter/free` is moving. |
| Current OpenRouter-free readiness | CLI returned `instrument_error`, 0 attempts/turns: `OPENROUTER_API_KEY is not set`. | `UNDETERMINABLE`; no request sent and no score. |
| GLM 5.3 Flash, two SOTA-hard tasks | 0/2; zero turns and model calls; HTTP 400. | `UNDETERMINABLE`, a harness/provider setup issue—not cognitive evidence. |
| LAM telemetry | 949 recorded calls; 3,671,251 estimated saved tokens; estimated $2,387.6489. | Replay/cache telemetry, not incurred local cost or model competence. |
| LAM baseline | 36/36 gold scenarios simulated at $0. | Deterministic plumbing/replay only, never a live pass rate. |

The historical `fib_cli` oracle has changed or differs: current inspection had
one unittest method while a retained live receipt names three tests. The old
receipt remains diagnostic, but no exact comparison is valid until the original
fixture is restored and hashed.

## Root-cause and classification model

Coding product success is multiplicative:

```text
provider availability
  × prompt/template compatibility
  × valid tool-call probability
  × tool execution reliability
  × context continuity
  × patch correctness
  × verification honesty
  × terminal-settlement honesty
```

One zero yields zero product value. Current local evidence reaches a zero
before code generation: dialect normalization, recovery, and settlement.
Purchasing a stronger hosted model cannot repair false completion.

Use this attribution decision tree:

1. No request / zero model calls: provider or instrument—not model quality.
2. HTTP error: request/provider compatibility unless a valid model response is
   retained.
3. Response violates declared tool schema: model-dialect join; retain raw
   response and template metadata.
4. Valid canonical action but failed tool: harness/tooling.
5. Tools execute but patch fails external oracle: LLM cognitive/task error.
6. Oracle passes but completion is refused: harness false negative.
7. Oracle fails or never ran yet completion occurs: critical harness false
   positive.

## Confirmed blockers and contained repairs

### A. Truthful completion and verification — critical

`runtime/session.py` exempts `vg-code-default` from admission. The public
default CLI path can thus convert bare finish/prose to `completed`. Protect the
new explicit product command with an already-gated coding manifest/profile
(for example balanced) pending the successor baseline required for T-04. Do
not rewrite admission broadly or mutate old evidence.

For an implementation task, completion must bind all of:

```text
repository mutation receipt
AND verified postimage/epoch matching the current workspace
AND relevant tests collected and executed
AND zero test exit code
AND tamper shield evaluated against frozen test set
AND no unresolved omission or stale-index marker
```

Wire the existing `session._tamper_shield.evaluate(...)` join; do not rewrite
T-18 shield or the existing epoch/refresh work. A task with a failing oracle
must never emit `completed`. A fake no-patch finish must end rejected or
abandoned, with an honest reason.

### B. Unique durable identity — critical

Replace implicit `run-cli` for a new public code request with generated
UUID/ULID identity. Resume is an explicit opt-in only. Test two new invocations
in one workspace: they must produce different ledgers; only `--resume` may
recover prior durable state.

### C. One strict local tool dialect — critical

Add a provider-specific normalization edge before the existing proposal
translator, not another adapter or loop:

```text
raw OpenAI tool_calls OR supported bounded Qwen XML
  -> strict parse
  -> manifest tool-name/argument validation
  -> canonical Proposal
  -> existing recovery and dispatch
```

Accept only exact bounded grammar. Reject mismatched tags, undeclared tools,
duplicate keys, trailing prose, and oversized arguments. Translate friendly
`search` only through an explicit manifest alias table, never fuzzy matching.
Record raw-response digest and classifier result in the ledger. On malformed
output, emit typed recovery and make one temperature-zero schema-reminder
retry; after exhaustion terminate honestly as a protocol/model error. Extend
the existing T-21 classification work rather than replace it.

### D. Bridge and MCP fail-closed behavior — high

Implement the bridge fixes above. MCP `status` should return compact summary
by default with opt-in raw props; tokenize should report budget/headroom rather
than just raw IDs. Add hermetic fake HTTP/process tests for invalid FA launch,
unrelated port occupant, stale PID safety, model mismatch, invalid schema,
empty completion, and max-tokens-without-content.

### E. Honest live telemetry — high

The receipt needs actual provider/model route, prompt and completion tokens,
local latency, tool actions, patch/postimage digest, test discovery/execution
counts, terminal reason, and missingness/cost fields. `null` route/token/cost
on a live run prevents a useful evaluation.

### F. Migration and environment — medium

Complete native-only name cleanup. The local sandbox's inability to reach
loopback was an assessment-environment isolation limit, not an adapter or
server defect. The `test.falsifiers.test_completion_gate_scope` import failure
was likewise an active-interpreter dependency issue (`cryptography` missing),
not evidence of a task regression; run it in the managed project environment
after `uv sync`.

## Maximum-value delivery plan

### PR 1 / Batch A–D: Coding P0 truth + dialect

Keep ownership contained to bridge/MCP tooling, current local dialect path,
CLI request builder/entrypoint, session admission join, selector migration,
and targeted tests. One developer owns `session.py` at a time.

| Change | Acceptance falsifier |
|---|---|
| Valid FA flag + child/model/PID readiness verification. | Invalid `-fa` child or unrelated server cannot be reported online. |
| Identity-verified stop/status and compact structured failures. | Stale PID cannot kill another server; status distinguishes cause. |
| MCP fail-closed schema/empty-output behavior. | Empty text never returns successful content; invalid schema never sends an unconstrained request. |
| Unique new run IDs; explicit resume. | Two calls get unique ledgers; only explicit resume recovers. |
| Gated public product command. | Fake finish with no patch cannot complete. |
| Completion bound to postimage/oracle/tamper receipt. | Failing-oracle task cannot complete. |
| Strict llama dialect normalizer + repair loop. | Valid declared call becomes canonical effect; malformed `properties`/XML creates typed recovery, never success. |
| Local-only selector cleanup. | `llama_cpp` / `local-model` is the documented route and retired identifiers cannot route. |
| Telemetry receipt. | One completed or failed live run retains required model/tool/test/latency fields. |

### CLI experience

The desired simple product interface is:

```bash
aether -m "create fibonacci.py with tests and run them"
```

Equivalent explicit form after the P0 route is truthful:

```bash
aether code . \
  --prompt "create fibonacci.py with tests and run them" \
  --provider llama_cpp --planner local-model \
  --profile balanced --yes --json
```

`-m` may already mean model in Python conventions; resolve that collision
explicitly before assigning it to message. `aether code --help` must show help,
not enter execution and emit an `instrument_error` completion frame.

### PR 2 / Batch E: freeze a real baseline

Run each once in a fresh workspace through the exact P0 command and external
oracle, retaining fixtures and content digests:

| ID | Task | External success condition |
|---|---|---|
| P0-FIB | Module + CLI + tests (Fibonacci). | Values, negative input, CLI output, and tests pass. |
| P0-CSV | Pandas CSV transform pipeline. | Fixture output exact; missing columns/bad types fail clearly. |
| P0-BUG | Fix a seeded one-file Python defect. | Pre-oracle fails, post-oracle passes, unrelated behavior remains green. |

Then freeze 12 tasks: four greenfield, four small bug fixes, and four data/CLI
tasks. Do not change prompts, tools, fixtures, oracle, model, server flags, or
budgets after the first measured attempt. After this trustworthy loop works,
use at least 30 senior-class tasks for T-26/T-27 control qualification and
Wilson-bound reporting; T-51/T-52 stay under board governance.

Every row requires:

```text
subject SHA and dirty-state flag; task/oracle digests; provider; exact model;
server build; GGUF digest/quantization/context/sampling; prompt/template/tool
schema digests; run ID; raw-response digest; valid/malformed tool count;
patch/postimage digest; tests discovered/executed/passed/failed; status and
reason; turns; prompt/completion tokens; latency; hosted cost or local
energy/time proxy; and missingness reason.
```

Display oracle-pass rate with Wilson interval; false-completion rate (target
exactly zero); valid first-tool-call, malformed-tool, and recovery rates;
patch and verified-patch rates; no-op rate; time to first valid action;
end-to-end latency; tokens; turns; hosted cost/local time proxy; and provider
missingness. Never tune on a hidden oracle then label the tuned tasks as
evaluation.

### PR 3: only then compare models

Use exactly the same immutable task bundle, prompt, tools, turn cap, and
oracle for each arm:

1. Qwen 27B Q2 through native llama.cpp as development baseline.
2. Qwen 27B Q4 only if it fits with safe KV/context settings, as a
   quantization ablation.
3. DeepSeek V4 Flash using its exact stable model ID, as low-cost hosted
   comparator after an authorized spend ceiling.
4. GLM 5.3 Flash after a successful readiness request; HTTP 400 is missing
   data, not failure.
5. OpenRouter free as availability experiment only unless it exposes and pins
   the actual selected model; it is not a stable benchmark identity.

Run LAM first for hermetic protocol regression, then one paid/live canary per
authorized arm, then the frozen corpus. Do not count provider outage, no model
call, time cap, malformed response, or unavailable credentials as task/model
failure. Never present replay percentages or token savings as live competence.

## What not to build yet

- A second EpisodeEngine, Forge/Chimera product score, swarm, or topology.
- A new provider abstraction or local inference plane.
- Kernel coding semantics, AST machinery, memory, or learning layers.
- Broad UI work before truthful headless JSON.
- A leaderboard that mixes live results, replay, provider errors, or zero-call
  rows.
- Claims that grammar constraints or min-p remove semantic hallucination.

## Definition of the first real product

Call Coding P0 usable only when all are true:

1. A fresh repository is changed through the public CLI, with unique durable
   run identity and an inspectable ledger.
2. Local Qwen executes declared read/search/patch/test canonical tools or
   emits a typed honest protocol failure; prose cannot become an effect/success.
3. `completed` binds current mutation, postimage, tamper evaluation, and a
   passing frozen external oracle.
4. P0-FIB, P0-CSV, and P0-BUG pass in fresh workspaces, or failure is honest
   and trajectory-backed.
5. A frozen 12-task canary retains model/server/task identity, routes, tokens,
   turns, latency, costs/missingness, false-completion rate, and trajectories.
6. Replay can reproduce decisions without being presented as fresh model skill.

At this point there is a product seed: an authorized model action loop with
durable evidence that does not lie about completion. The next improvement is
chosen from the largest observed failure bucket, not architecture speculation.

## Commands and validation actually executed

The two assessments executed the following command categories; brackets denote
arguments summarized to avoid copying machine-local temporary paths beyond
those evidenced above:

```text
git branch --show-current; git log -15 --oneline; git status --short
llama-server --version; llama-bridge --help/models/status/serve/chat
native server process/PID/log, filesystem, source, board, and artifact inspection
python3 tools/llama_cpp/mcp_server.py [initialize, tools/list, status, tokenize, chat]
node bin/aether code --help
node .../cli/dist/src/main.js code [fake FIB-P0 falsifier]
node .../cli/dist/src/main.js code [live llama_cpp FIB-P0]
node bin/aether code [live native Fibonacci fixture]
node .../cli/dist/src/main.js code [OpenRouter-free readiness]
python3 tools/002_LLM_API_MOCK/cli.py stats
```

Focused test outcomes are intentionally retained separately because they ran
on different assessment subjects/environments:

| Assessment | Command family | Result |
|---|---|---|
| Terra | `test.adapters.test_llama_cpp`, `test.runtime.test_model_selection` | 8 targeted tests passed. `test.falsifiers.test_completion_gate_scope` could not import because active Python lacked `cryptography`; no full-suite pass claimed. |
| SOL | `.venv/bin/python -m unittest test.adapters.test_llama_cpp test.runtime.test_model_selection test.contracts.test_evo09_model_factory -v` | 13 focused adapter/selection/factory tests passed in 0.781 s; no full-suite pass claimed. |
| SOL | Markdown link checker | Passed. |
| SOL | markdownlint | Did not start because `node_modules/fast-glob` was missing. |

Neither assessment changed production code, execution-board files, or milestone
status. The old native server process was not intentionally left running by the
SOL assessment; its observed bridge PID file was stale. Terra separately
observed a running Q2 server while testing the bridge; this is why PID/model
identity is a required fix rather than a report inconsistency.

## Final recommendation

The next sprint is **Coding P0 truth + dialect**, not more framework. Repair
bridge/MCP fail-closed lifecycle behavior; normalize one Qwen tool format into
the current proposal contract; route the explicit public coding preset through
honest completion; wire the existing tamper shield at the session join; add
unique run IDs and live telemetry; then run P0-FIB/P0-CSV/P0-BUG. Only after
those trajectories are trustworthy should the team spend money or effort
comparing DeepSeek, GLM, Qwen quantizations, or OpenRouter-free on the same
frozen corpus.

If the three tasks pass, AETHER has a defensible product seed. If they fail
honestly, the evidence will identify whether the next contained improvement is
prompt/template, model, tool dialect, patch tool, verifier, context compiler,
or provider request—without guessing and without a large refactor.
