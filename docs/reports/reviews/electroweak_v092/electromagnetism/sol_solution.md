---
id: report.electroweak-v092.sol-solution
class: report
authority: non-canonical
status: observed
owner: coding-product-prototyping
created: 2026-09-04
subject_branch: feat/strongforce_beta_release_v093
subject_head: ffc3dc926e80dd67ca4941aecbede01b7291133f
---

# SOL: evidence-driven route to a useful AETHER coding CLI

## Executive conclusion

AETHER has enough substrate to ship a small coding agent now. It does not need
another framework, a new agent hierarchy, a new model abstraction, or Ollama.
The shortest product path is:

```text
native Vulkan llama-server
  -> existing OpenAI-compatible LlamaCppModel
  -> one existing EpisodeEngine + code pack
  -> read/search/patch/test
  -> external oracle
  -> honest terminal receipt
```

The local inference foundation is real and fast enough for prototyping. A
Qwen 27B Q2 model served at about 22.6 output tokens/second, produced correct
schema-constrained JSON, and exposed an 8,192-token context with four slots.
The current product failure is chiefly in the harness boundary:

1. `aether code` can report `completed` with no source mutation and no tests.
2. The Qwen/llama.cpp XML tool-call dialect is not normalized into AETHER's
   canonical proposal form.
3. Invalid tool output is retained as a note and settled as success instead of
   being rejected and repaired.
4. The CLI emits no usable model-route or token accounting for this live run.
5. `llama-bridge serve` can claim success for a child that already failed by
   probing an unrelated server on the same port.

The right pivot is therefore not “find a smarter model first.” It is to make
one thin, truthful vertical slice work on three tiny coding tasks, freeze that
as a baseline, and improve the largest measured failure bucket.

This report does not close MS-SEE or MS-CHANGE, does not authorize T-04, and
does not promote T-46 or T-47–T-49. Package version 0.9.3 is not milestone M-9.

## Scope and evidence rules

The repository was inspected on branch
`feat/strongforce_beta_release_v093`, pinned at
`ffc3dc926e80dd67ca4941aecbede01b7291133f`. The checkout was dirty with
pre-existing user work, including removal/migration of the old local adapter
surface and other reports. No production code or execution-board file was
changed for this assessment.

The navigation index could not be treated as current authority: its summary
and generated metadata were older than the inspected subject. Canonical
execution documents, current source, targeted tests, Git, live process output,
and retained benchmark artifacts were used instead.

Evidence labels in this report mean:

| Label | Meaning |
|---|---|
| `LIVE-LOCAL` | Executed in this assessment against native llama.cpp. |
| `LIVE-HISTORICAL` | Retained live-provider artifact from an older subject. Useful diagnostically, not a current product score. |
| `REPLAY` | LAM/cassette/deterministic evidence. Tests plumbing, not model intelligence. |
| `STATIC` | Source, tests, documentation, or Git inspection. |
| `UNDETERMINABLE` | Provider or instrument never produced a valid attempt. Must not be scored as model failure. |

No new OpenRouter call was made: no OpenRouter credential was available to
this session. No paid DeepSeek or GLM request was authorized or charged.
Historical provider artifacts are explicitly separated from newly executed
local probes.

## What already exists

The project is not “only documents.” The following production pieces exist:

| Layer | Existing implementation | Assessment |
|---|---|---|
| Operator CLI | TypeScript `vg` / `aether` client | Real command path, but help and success semantics are not yet product-grade. |
| Product app | `CodingMaxFacade` over `ApplicationService` | Correct thin-app direction; public legacy code path still bypasses important product settlement behavior. |
| Agent loop | `EpisodeEngine` | Keep one loop. Do not replace it with Forge, Chimera, or a new swarm. |
| Coding behavior | `packs/code-default/` and `vg-code-*` manifests | Read/search/patch/terminal vocabulary exists. |
| Local model | `LlamaCppModel` | Reuses the OpenAI-compatible transport at `127.0.0.1:8080/v1/chat/completions`; focused adapter contracts pass. |
| Hosted models | OpenRouter adapter and routing | Existing seam is sufficient for DeepSeek, GLM, and free routing. |
| Durability | SQLite WAL ledger and blob store | Live run produced durable events/blobs, but terminal interpretation was false. |
| Verification | coding admission/oracle mechanisms | Mechanism exists; default `vg-code-default` remains exempt under the still-proposed T-04 change. |
| Bench infrastructure | BAAC, ladder artifacts, LAM/cassettes, RF-95 runner | Valuable pieces, but several reports measure a different runner, subject, or no model call. |

The central architectural fact is that an OpenAI-compatible local adapter is
already present. Native llama.cpp is not a new intelligence plane. It is just
another `ModelPort` implementation feeding the same canonical loop.

## Native llama.cpp environment

### Verified installation

```text
binary:  /home/rock-dev/.local/bin/llama-server
version: 0.3.0-dev, build 10796, commit 9a4843cf2
backend: native Vulkan build
GPU:     AMD Radeon RX 9060 XT, 16 GB VRAM
API:     http://127.0.0.1:8080/v1
```

`llama-bridge models` discovered:

| GGUF | Disk size | Practical role |
|---|---:|---|
| `Qwen3.8-27B-UD-IQ1_M.gguf` | 6.27 GB | Lowest memory, highest quantization-risk arm. |
| `Qwen3.8-27B-UD-Q2_K_XL.gguf` | 9.15 GB | Current balanced local baseline. |
| `Qwen3.8-27B-UD-Q4_K_S.gguf` | 14.30 GB | Higher-quality candidate, but tight on 16 GB after KV/cache overhead. |

The tested server reported Q2_K, context 8,192, four slots, and a Qwen chat
template with tool instructions. Server timings showed roughly 458–477 prompt
tokens/second on approximately 2,000-token prompts and 22.6–23.0 generated
tokens/second. These are single-run engineering observations, not a formal
throughput distribution.

## Skill + CLI + MCP triad review

### Scorecard

| Component | Works | Friction or defect | Verdict |
|---|---|---|---|
| `llama-cpp` skill | Correct binary, model directory, endpoint, and no-Ollama policy. Short enough to follow. | Its launch recipe uses `--jinja`, while `llama-bridge serve` does not expose that flag. It states the provider path more confidently than live integration warrants. | Good operational start; needs executable truth checks. |
| `llama-bridge models` | Found all three GGUFs with paths and sizes immediately. | Search roots are partly machine-specific and include current directory. No JSON mode. | Easy and useful. |
| `llama-bridge status` | `/health` and `/props` provide model/context detail. | Any loopback permission failure is labeled `OFFLINE`; no typed distinction between refused, forbidden, and timeout. Human output hides useful props. | Usable, weak diagnostics. |
| `llama-bridge chat` | Low-temperature/min-p controls, streaming option, schema constraint, telemetry. Correct constrained JSON was produced. | Non-streaming command is silent while loading/generating. Invalid schema only warns and then continues unconstrained. | Good prototype interface, unsafe failure semantics. |
| `llama-bridge serve` | Discovers model by name and constructs a compact launch command. | Critical lifecycle identity bug; invalid Flash Attention syntax; can attach health to another process and claim child success. | Bad until fixed. |
| `llama-bridge stop` | Stops the PID recorded by the bridge. | If the PID file is missing it runs `pkill -f llama-server`, potentially killing unrelated servers. | Too broad for safe automation. |
| MCP discovery | `initialize` and `tools/list` returned four documented tools. | The server is registered for Gemini but was not exposed in this Codex session's MCP tool registry. | Protocol works; installation/registration is incomplete across clients. |
| MCP status/models | Health and model discovery work over stdio JSON-RPC. | `llama_status` dumps a very large raw chat template, wasting agent context. | Functionally good, context-inefficient. |
| MCP tokenize | Exact tokenizer returned count 10 for the test prompt. | Returning the first 20 raw token IDs is rarely useful; missing budget/headroom calculation. | Useful primitive, mediocre UX. |
| MCP chat | Reaches the model and records latency/usage. | A 192-token response exhausted on hidden reasoning and returned empty content, yet `isError` was absent. | Must fail closed on empty/exhausted output. |
| AETHER local route | Selects `llama_cpp`; adapter contracts pass. | Live tool intention was not executable, and the episode falsely completed. | Integration blocker, not engine blocker. |

### Critical bridge lifecycle reproduction

Input:

```bash
llama-bridge serve \
  -m Qwen3.8-27B-UD-Q2_K_XL.gguf \
  -c 8192 -ngl 99 --flash-attn \
  --ctk q8_0 --ctv q8_0 --alias local-model -d
```

CLI output claimed:

```text
Server launched in background (PID: 102746).
Server is ONLINE and ready for requests.
```

The child log actually contained:

```text
error while handling argument "-fa": unknown value for --flash-attn: '-ctk'
usage: -fa, --flash-attn [on|off|auto]
```

The bridge emits bare `-fa`; this llama-server build requires a value. Its
health loop checked only the shared port, found a pre-existing server, and
attributed that health to PID 102746. The PID file remained stale afterward.

Minimal repair:

1. Make `--flash-attn` accept `on|off|auto` and emit both option and value.
2. Before launch, either reject an occupied port or explicitly adopt the
   existing process after verifying its model and owner.
3. After launch, require `child.poll() is None`, PID identity, start time, and
   `/props` model/path/alias match before printing `ONLINE`.
4. On failure, remove the PID file and show the last bounded log lines.
5. `stop` must terminate only the recorded, identity-verified child. Never
   fall back to global `pkill -f`.

## Newly executed inference probes

### L0: constrained structured output (`LIVE-LOCAL`)

Input:

```text
Extract the package name and semantic version from:
package ripgrep @ 14.1.0. Return only the schema object.
```

Constraint:

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "version": {"type": "string"}
  },
  "required": ["name", "version"],
  "additionalProperties": false
}
```

Sampling was temperature `0.2`, min-p `0.05`, maximum 128 tokens.

Actual visible output:

```json
{"name":"ripgrep","version":"14.1.0"}
```

Telemetry: 79 prompt tokens, 121 completion tokens, reported generation call
elapsed 6.14 seconds. Result: **PASS** for schema and semantic extraction.

Interpretation: constrained decoding can guarantee shape, not truth in
general. This result proves the local stack can return a valid small contract;
it does not prove coding autonomy or “eradicate hallucinations.” Min-p reduces
the candidate token set but is not a semantic verifier.

### L1: MCP structured planning (`LIVE-LOCAL`)

Input:

```text
Return a JSON plan for creating fibonacci.py with exactly two ordered steps.
```

The MCP tool supplied a two-item JSON schema, temperature `0.2`, min-p `0.05`,
and maximum 192 tokens.

Actual result:

```json
{
  "content": [{"type":"text","text":""}],
  "telemetry": {
    "latency_seconds": 9.477,
    "usage": {"prompt_tokens":66,"completion_tokens":192,"total_tokens":258}
  }
}
```

Result: **FAIL / instrument-contract defect**. The model consumed the entire
completion budget, apparently in non-visible reasoning, and the wrapper
returned empty text as success. Model configuration contributed, but a robust
MCP boundary must emit `EMPTY_COMPLETION` or `MAX_TOKENS_WITHOUT_CONTENT` and
allow a bounded retry with thinking disabled or a larger output budget.

### L2: end-to-end AETHER Fibonacci task (`LIVE-LOCAL`)

Disposable workspace: `/tmp/aether-native-9QZ2JmVD`.

Input brief:

```text
Create fibonacci.py in the repository root. It must expose fib(n: int) -> int,
reject negative n with ValueError, and when run as a CLI with --n 10 print 55.
Create tests and run them.
```

Provider: `llama_cpp`; planner: `local-model`; profile: `local`; requested cap:
8 turns.

Actual model-facing terminal detail began:

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

This is malformed XML-like tool syntax: tags do not pair, and the proposed
tool name/arguments do not match the canonical OpenAI tool-call object.

Actual CLI settlement:

```json
{"kind":"complete","outcome":"completed","turns":1}
```

The result reported:

```text
verifiedStepIds: []
modelRoutes:     []
promptTokens:    null
completionTokens:null
spentUsdMicros:  null
```

Filesystem inspection found only `.vanguard/events.sqlite3` and two blobs.
There was no `fibonacci.py`, no tests directory, no patch, and no successful
verification.

Attribution:

| Failure | Primary owner | Explanation |
|---|---|---|
| Malformed XML-like tool call | Model/dialect join | The Qwen template asks for XML-style calls while AETHER expects canonical structured calls. Q2 quantization may worsen formatting. |
| No recovery turn | Harness | A malformed proposal should create a typed reject-and-repair cycle, not settle the episode. |
| `completed` with no mutation/tests | Harness/admission | Critical false-success defect. The same class was independently reproduced with the fake route. |
| Empty routes/tokens | Harness telemetry | Prevents provider, cost, and efficiency analysis. |
| No coding-quality sample | Evaluation method | Since no valid action occurred, this run cannot score Qwen's ability to write Fibonacci code. |

### L3: focused adapter contracts (`STATIC/EXECUTED`)

Thirteen focused tests passed in 0.781 seconds across:

```text
test.adapters.test_llama_cpp
test.runtime.test_model_selection
test.contracts.test_evo09_model_factory
```

They cover provider identity, OpenAI-format tool calls, retryable HTTP failure,
malformed response classification, selection, aliases, and model factory
contracts. This narrows the defect: unit-level transport contracts are green;
the live Qwen response dialect, episode recovery, and completion settlement are
not adequately covered.

## Hosted-model benchmark evidence

These are retained artifacts, not calls made in this assessment.

| Artifact/arm | Observed result | Correct attribution |
|---|---|---|
| DeepSeek V4 Flash, BAAC `fib_cli`, `vg-1-forge` live | 1/1 PASS; 8 turns; 15,877 prompt + 3,324 completion tokens; 93.34 s; $0.001191; three historical oracle tests passed. | Evidence that DeepSeek can solve a tiny task through one experimental harness. Not current product qualification; Forge is excluded from Coding Max scores and n=1 is statistically weak. |
| DeepSeek V4 Flash, v3luna SOTA-easy config precedence | 1/1 PASS; 10 calls/turns; 24.32 s; $0.001829; two files modified. | Promising live compatibility on that historical runner. Not comparable to the failed local run until the exact task/harness/subject is frozen. |
| OpenRouter `free`, same SOTA-easy task | 0/1; four task calls, report total five; 38.96 s; no files; terminal `provider returned HTTP 400`. | Provider/routing or request compatibility failure. It is not evidence that a particular free model lacks coding ability; `openrouter/free` is a moving router, not a stable model identity. |
| GLM 5.3 Flash, two SOTA-hard tasks | 0/2; zero turns and zero model calls; both terminal details `provider returned HTTP 400`. | `UNDETERMINABLE`. The model was never sampled. Count as harness/provider setup failure, not LLM cognitive failure. |
| `benchmark_20_deepseek_v4_flash.json` | 0/20, one turn each, zero tokens/cost, no patch. | Invalid as a DeepSeek-quality benchmark: the absence of tokens and patches indicates no usable model execution. |
| LAM/cassette runs | Often deterministic PASS at zero cost. | Harness regression and replay evidence only. Never publish as live model competence. |

The historical `fib_cli` task itself has changed or differs across retained
runs: the currently inspected oracle contains one `unittest` method, while the
historical live result reports three named tests. That does not invalidate the
old receipt, but it prevents an exact-subject comparison without restoring and
hashing the original fixture.

## Root-cause model

Coding success is a multiplicative pipeline:

```text
provider availability
  × prompt/template compatibility
  × valid tool-call probability
  × tool execution reliability
  × context continuity
  × patch correctness
  × verification honesty
  × terminal settlement honesty
```

A zero in any stage produces zero product value. Current evidence places the
first local bottleneck before code generation: dialect normalization and
settlement. Buying a stronger hosted model may increase proposal quality, but
it cannot repair false completion or missing verification.

The attribution decision tree should be:

1. No request or zero model calls: provider/instrument, never model quality.
2. HTTP error: provider/request compatibility unless a valid model response is
   retained.
3. Response violates declared tool schema: model-dialect join; retain raw
   response and template metadata.
4. Valid canonical action but tool fails: harness/tooling.
5. Tools work but patch fails external oracle: LLM cognitive/task error.
6. Oracle passes but harness refuses completion: harness false negative.
7. Oracle fails or never ran but harness completes: critical harness false
   positive.

## Maximum-value development path

### Batch A: make local execution trustworthy

This is a small seam repair, not a refactor.

1. Fix `llama-bridge` lifecycle identity and Flash Attention argument handling.
2. Remove the forbidden `/usr/local/lib/ollama/llama-server` fallback from the
   bridge so the operational skill and code agree.
3. Make status return structured causes: `ONLINE`, `REFUSED`, `FORBIDDEN`,
   `TIMEOUT`, `PID_STALE`, `MODEL_MISMATCH`.
4. Make MCP status return a compact summary by default; add opt-in raw props.
5. Fail closed on invalid JSON schema, empty completion, output-budget
   exhaustion, and malformed provider payload.

Acceptance falsifiers:

- invalid `-fa` child cannot be reported online;
- an unrelated server on port 8080 cannot satisfy a new child's readiness;
- stale PID cannot kill another process;
- empty MCP content cannot be returned without `isError: true`;
- all fixes have hermetic fake-HTTP/process tests.

### Batch B: normalize one local tool dialect

Do not invent another adapter or loop. Add a provider-specific normalization
edge before the existing canonical proposal translator:

```text
raw OpenAI tool_calls OR supported Qwen XML
  -> strict parse
  -> manifest tool-name validation
  -> canonical Proposal
  -> existing recovery/dispatch
```

Requirements:

- parse only an exact bounded grammar;
- reject mismatched tags, undeclared tools, duplicate keys, trailing prose,
  and oversized arguments;
- translate friendly names such as `search` only through an explicit manifest
  alias table, never fuzzy matching;
- retain raw-response digest and classifier result in the ledger;
- one corrective retry at temperature 0 with a compact schema reminder;
- after retry exhaustion, terminate honestly as protocol/model error.

The already-landed T-21 classification work should be extended/reused rather
than replaced. This dialect work does not close MS-CHANGE.

### Batch C: make public completion honest without silently authorizing T-04

T-04 remains `[PROPOSAL]`. The smallest safe prototype is to route the new
explicit product command/preset through an already gated coding manifest such
as the balanced profile, leaving compatibility behavior isolated until the
required successor baseline exists.

For an implementation brief, `completed` must imply all of:

```text
at least one repository mutation receipt
AND postimage/epoch matches the verified workspace
AND at least one relevant test was actually collected and executed
AND test exit code is zero
AND tamper shield evaluated the frozen test set
AND no unresolved omission/stale-index marker exists
```

The known join gap must be fixed by wiring the existing
`session._tamper_shield.evaluate(...)`; do not rewrite the T-18 shield or A's
epoch/refresh work. One developer must own `session.py` at a time.

### Batch D: expose a genuinely simple CLI

Target user experience:

```bash
aether -m "create fibonacci.py with tests and run them"
```

Equivalent explicit form:

```bash
aether code . \
  --prompt "create fibonacci.py with tests and run them" \
  --provider llama_cpp --planner local-model \
  --profile balanced --yes --json
```

The short `-m` alias is a product choice; today Python-side conventions may
already use `-m` for model. Resolve the collision explicitly rather than
silently changing meaning. Also fix `aether code --help`: it currently enters
the execution path and printed `[complete] instrument_error, 0 turns, unknown`
instead of help.

Each new invocation should generate a unique run ID. Resume must be explicit;
the historical fixed `run-cli` identity can recover unrelated state.

### Batch E: freeze the first useful baseline

Start with three externally-oracled tasks in fresh repositories:

| ID | Task | External success condition |
|---|---|---|
| P0-FIB | Create Fibonacci module + CLI + tests. | Values, negative input, CLI output, and user-visible tests pass. |
| P0-CSV | Create a pandas CSV transform pipeline. | Fixture input produces exact output; missing columns and bad types fail clearly. |
| P0-BUG | Fix a seeded one-file Python defect. | Pre-oracle fails, post-oracle passes, unrelated behavior remains green. |

Then freeze 12 tasks: four greenfield, four bugfix, four CLI/data tasks. After
the loop is trustworthy, freeze at least 30 senior-class tasks for T-26/T-27
control qualification and Wilson-bound reporting. T-51/T-52 remain board
governance, not something this report promotes.

Every row must retain:

```text
subject SHA and dirty-state flag
task/oracle digests
provider and exact model identity
llama-server build, GGUF digest, quantization, context, sampling
prompt/template/tool-schema digests
run ID and raw-response digest
valid/malformed tool-call counts
patch/postimage digest
tests discovered, executed, passed, failed
terminal status and reason
turns, prompt/completion tokens, latency, cost/missingness
```

Primary metrics:

- external-oracle pass rate with Wilson interval;
- false-completion rate, target exactly zero;
- valid first-tool-call rate;
- malformed-tool and recovery rate;
- patch rate and verified-patch rate;
- time to first valid action and end-to-end latency;
- tokens, turns, hosted cost, and local energy/time proxy;
- missingness by provider/instrument cause.

## Model evaluation order

Use the same immutable task bundle, prompt, tools, turn cap, and oracle for all
arms:

1. Qwen 27B Q2 via native llama.cpp: development baseline.
2. Qwen 27B Q4 if it fits with safe KV/context settings: quantization ablation.
3. DeepSeek V4 Flash exact ID: low-cost hosted comparator.
4. GLM 5.3 Flash exact ID: hosted comparator only after a successful readiness
   request; HTTP 400 rows are missing data.
5. OpenRouter free: availability experiment, not a stable model benchmark,
   unless the router reveals and the report pins the actual selected model.

Run LAM first for hermetic protocol regressions, then one paid/live canary per
arm, then the frozen corpus. Never tune on hidden oracle results and re-label
the tuned set as evaluation.

## What not to build yet

- No second EpisodeEngine.
- No Forge/Chimera product scoring.
- No swarm or topology work to repair a one-agent protocol mismatch.
- No new local provider abstraction.
- No kernel coding semantics or AST logic.
- No memory/learning layer before one fresh task can patch and verify.
- No broad UI work before truthful headless JSON exists.
- No benchmark leaderboard that mixes live, replay, provider errors, and
  zero-call rows.
- No claims that grammar or min-p eliminates semantic hallucination.

## Definition of the first real product

The team may call AETHER a usable coding-agent prototype when:

1. A fresh repository can be changed through the public CLI.
2. The local Qwen route executes at least read/search/patch/test through
   canonical tools, or reports a typed honest failure.
3. `completed` always binds a mutation and a current passing external oracle.
4. The three P0 tasks pass from clean workspaces with retained trajectories.
5. The 12-task canary reports false completions, provider missingness, tokens,
   turns, latency, and exact model identity.
6. Replay reproduces the same decisions without being represented as fresh
   model competence.

That is the intermediate measurement point needed to pivot safely. It is much
smaller than the existing architecture, but it exercises the architecture's
most valuable promise: a model can take authorized actions, preserve durable
evidence, and never lie about completion.

## Commands actually executed

```text
git branch --show-current
git log -15 --oneline
git status --short
llama-server --version
llama-bridge --help
llama-bridge models
llama-bridge status
llama-bridge serve [Q2 model, 8192 context, GPU/FA/KV flags]
llama-bridge chat [schema-constrained ripgrep/version probe]
python3 tools/llama_cpp/mcp_server.py [initialize, tools/list, status, tokenize]
python3 tools/llama_cpp/mcp_server.py [schema-constrained llama_chat]
node bin/aether code --help
node bin/aether code /tmp/aether-native-9QZ2JmVD [live Fibonacci task]
.venv/bin/python -m unittest test.adapters.test_llama_cpp test.runtime.test_model_selection test.contracts.test_evo09_model_factory -v
filesystem, process, PID, server-log, source, board, and benchmark-artifact inspection
```

Observed targeted-test result: 13 tests passed. No full-suite result is claimed.
No OpenRouter request was executed. No Ollama command was executed after the
native-only policy correction. The native server was not left running by this
assessment; the bridge PID file observed afterward was stale.

## Final recommendation

Treat the next sprint as **Coding P0 truth + dialect**, not “more agent
framework.” Repair the bridge lifecycle, normalize one Qwen tool format into
the existing proposal contract, route the explicit product preset through
honest completion, wire the existing tamper shield at the session join, and
run P0-FIB/P0-CSV/P0-BUG. Only then spend money comparing DeepSeek, GLM, and
OpenRouter-free on the exact same frozen tasks.

If those three tasks work, the project has a product seed. If they fail
honestly, the trajectories will finally tell the team whether to improve the
prompt, model, patch tool, verifier, or context compiler—without guessing and
without another large refactor.
