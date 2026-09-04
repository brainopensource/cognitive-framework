---
id: report.electroweak-v092.terra-solution
class: report
authority: non-canonical
status: observed
owner: local-agent-prototyping
created: 2026-09-04
subject_head: d3890ce03500c0cef3ce0b027eac583be096c57e
---

# Terra solution: fastest credible path to an AETHER coding CLI

## Executive decision

Do not build another agent framework, a multi-agent topology, a new provider
abstraction, or a new UI. The shortest path is a **Coding P0** slice:

```text
llama-server (Qwen 27B) → existing LlamaCppModel → vg/aether code
    → read/search/patch/test → external oracle → honest receipt
```

The local model infrastructure is usable and the existing `LlamaCppModel`
adapter is real. The product path is not usable yet because a default coding
episode can return `completed` without a patch or a passing verification
receipt. This was reproduced twice, including once with the real local Qwen
model. That is a harness truthfulness defect, not proof that the model solved
or failed the task.

**P0 priority order:**

1. Make false completion impossible on the user-facing coding command.
2. Generate a new run ID by default; never silently recover an unrelated run.
3. Normalize the llama.cpp/Qwen tool-call dialect into the existing canonical
   proposal shape.
4. Run a tiny, frozen, externally-oracled coding corpus through that exact CLI.
5. Use resulting failures to improve the pack, prompts, and tool contract;
   defer swarms, memory, autonomous learning, new frontends, and broad
   refactors.

This report is an observed engineering assessment, not milestone acceptance or
an empirical claim about general coding ability.

## Scope, subject, and evidence discipline

- **Repository HEAD at navigation time:**
  `d3890ce03500c0cef3ce0b027eac583be096c57e`.
- **Subject state:** dirty. Existing user changes include local llama.cpp
  integration work. No qualifying empirical claim can be made from this dirty
  checkout. A later formal run must use a clean commit or linked worktree.
- **Local-provider policy:** native `llama-server` only at
  `http://127.0.0.1:8080/v1`; no legacy local-provider calls were used after
  that policy was supplied.
- **Remote-provider policy:** no OpenRouter credential was available to this
  session. No paid DeepSeek or GLM call was made and no cost was charged.
- **Disposable workspaces:** `/tmp/aether-coding-p0-Rpq4o8` and
  `/tmp/aether-llama-p0-P3LI7X`. Only these temporary directories were allowed
  to be changed by benchmark episodes.
- **Benchmark rule:** provider/instrument absence is `undeterminable`, not a
  task failure and never a model-quality score.

## What exists today

### Operator surface

The compiled TypeScript CLI already sends `code` requests to the Python runtime
entrypoint. It accepts a workspace, brief/prompt, model port, run ID, profile,
turn cap, and JSON output. The runtime entrypoint then calls the canonical
profiled runtime rather than embedding a second agent loop.

Relevant implementation seams:

| Layer | Existing asset | Observed status |
|---|---|---|
| CLI | `vanguard/clients/cli/dist/src/main.js` | Executed in the benchmarks below. |
| Runtime entrypoint | `vanguard/packages/runtime/entrypoint.py` | Routes model port and persists a ledger at `<workspace>/.vanguard/events.sqlite3`. |
| Local adapter | `vanguard/packages/adapters/models/llama_cpp.py` | Present; reuses the OpenAI-compatible transport and proposal translation. |
| Local selection | `vanguard/packages/runtime/model_selection.py` | `llama_cpp` and `llama` select the local adapter. |
| Coding pack | `packs/code-default/` plus `vg-code-*` manifests | Read/search/patch/terminal primitives exist. |
| Facade | `vanguard/packages/apps/coding_max/facade.py` | `run`, `status`, `resume`, `evidence`, and `cost` with `fast`, `balanced`, `max` presets. |

### Local inference is healthy

`llama-bridge models` found these GGUFs:

| Model file | Size |
|---|---:|
| `Qwen3.8-27B-UD-IQ1_M.gguf` | 6.27 GB |
| `Qwen3.8-27B-UD-Q2_K_XL.gguf` | 9.15 GB |
| `Qwen3.8-27B-UD-Q4_K_S.gguf` | 14.30 GB |

The running local server was pinned by process metadata and `/props`, not just
by a port probe:

```text
binary:      /home/rock-dev/.local/bin/llama-server
version:     0.3.0-dev, build 10796, commit 9a4843cf2
model:       Qwen3.8-27B-UD-Q2_K_XL.gguf
alias:       Qwen3.8-27B-UD-Q2_K_XL
format:      Q2_K - Medium
parameters:  27,320,697,856
context:     8192
slots:       4
endpoint:    http://127.0.0.1:8080/v1
process:     PID 90853
```

The native server's model metadata advertises tool-call support and a Qwen chat
template. This is a sufficient local foundation for P0.

## Executed benchmark evidence

### Frozen task FIB-P0

The same disposable task and immutable oracle were used wherever a provider
could be invoked.

**Input brief**

```text
Create fibonacci.py with fibonacci(n), preserve the provided test,
and run python3 -m unittest -v.
```

**Oracle contract**

```text
fibonacci(n) returns [0, 1, 1, 2, 3, 5, 8, 13] for n=0..7
fibonacci(-1) raises ValueError
```

**Input fingerprints**

```text
TASK.md            5a06859e03efb6271d586b6f5893f6704be9297d49a52f59aaf6bcc9af213359
test_fibonacci.py  67bc792e9cf5641e75aa1a6cd17aa1e8954d26f2bf04f59d02892575f6927c4c
```

No run created `fibonacci.py`; therefore the oracle correctly failed in every
agent episode with `ModuleNotFoundError: No module named 'fibonacci'`.

### B0 — deterministic false-completion falsifier

**Command shape:** `vg code` against FIB-P0 with the existing deterministic
`fake` model route.

**Model output / CLI result**

```json
{"kind":"note","text":"fake-default"}
{"kind":"complete","outcome":"completed","turns":1}
```

The workspace contained only `TASK.md`, `test_fibonacci.py`, and runtime
artifacts afterward. No patch, terminal command, or verification occurred.
The oracle failed.

**Attribution:** harness defect. A deterministic `finish` must not be able to
settle an implementation task without current, successful verification.

### B1 — direct constrained local-Qwen protocol probe

**Purpose:** isolate local-model structured output from agent-loop behavior.
No workspace tools were made available and no repository was modified.

**Input**

```text
You are a coding agent. For a repository task requiring fibonacci.py,
choose the first safe tool action. Return only a JSON object with action,
path, and reason. The action must be fs.read and the path must be TASK.md.
```

**Constraint:** JSON schema required `action = "fs.read"`,
`path = "TASK.md"`, a string `reason`, and no additional properties;
temperature `0.2`, min-p `0.05`.

**Actual output**

```json
{
  "action": "fs.read",
  "path": "TASK.md",
  "reason": "Read the task description to understand the requirements for implementing fibonacci.py."
}
```

**Result:** pass. The model obeyed the grammar constraint and selected the
right safe first action.

**Observed serving performance:** the server log recorded generation at about
`22.6–22.7 tokens/s`. The full CLI prompt measured `1,982` prompt tokens at
`458.34 tokens/s`, followed by `54` generated tokens in `2.343 s`; total
model time was `6.667 s`. This is a useful local P0 speed, not a throughput
benchmark: one request is not a distribution.

### B2 — real local Qwen coding-agent episode

**Command**

```bash
node vanguard/clients/cli/dist/src/main.js code /tmp/aether-llama-p0-P3LI7X \
  --brief "Create fibonacci.py with fibonacci(n), preserve the provided test, and run python3 -m unittest -v." \
  --provider llama_cpp --planner local-model --profile local --benchmark \
  --run-id llama-p0-fibonacci-001 --max-turns 4 --json
```

The process was independently capped at 180 seconds. It terminated after one
turn, not four.

**CLI output**

```json
{"kind":"note","text":"{\"properties\": {\"action\": \"search\", \"args\": {\"path\": \".\", \"pattern\": \"fibonacci\", \"max_results\": 50}, \"kind\": \"effect\"}}"}
{"kind":"complete","outcome":"completed","turns":1}
```

**Ledger trajectory**

```text
seq 0   EpisodeStarted   composed
seq 49  TurnStarted      turn_opened
seq 54  ProposalProduced {"properties":{"action":"search",...}}
seq 55  EpisodeCompleted completed
```

There were no `EffectStarted`, `EffectCompleted`, `patch.apply`, or `proc.exec`
events. The oracle failed because no file was added.

**Attribution**

| Observation | Attribution | Why |
|---|---|---|
| The proposal is JSON-shaped but has a `properties` wrapper and `search` rather than a valid manifest tool call. | Model-to-dialect integration | The response is not a canonical executable proposal. It may reflect Qwen's tool template, prompting, or response normalisation; it is not enough to rate general coding ability. |
| The invalid proposal is represented as a note rather than a rejected/recovery state. | Harness/product-loop defect | The event stream makes the non-action observable but does not create a repair opportunity. |
| The episode returns `completed` with no patch and a failing oracle. | Critical harness/admission defect | Completion is a false user-facing success. This is independently reproducible with the fake route. |
| One task, one usable turn, no valid tool call. | Insufficient model evidence | This run is a protocol-integration failure, **not** a code-generation quality score for Qwen 27B. |

### Excluded run — default run-ID collision

An earlier local episode omitted `--run-id`, therefore it defaulted to
`run-cli`, the same ID used by the prior fake episode. The runtime recovered
that old ledger and ended `abandoned` with `max_turns (1) exhausted across
approval`, without a new model proposal. It is excluded from all quality
judgments.

This is still a product bug: ordinary commands must generate a unique run ID,
and recovering an existing run must require explicit `--resume` intent.

### OpenRouter-free readiness test

The same FIB-P0 input was sent to the CLI with
`--provider openrouter --planner openrouter/free`. No request was sent because
the environment has no `OPENROUTER_API_KEY`.

```json
{
  "outcome": "instrument_error",
  "attempts": 0,
  "turns": 0,
  "detail": "openrouter: OPENROUTER_API_KEY is not set"
}
```

**Classification:** `undeterminable` provider configuration. It says nothing
about OpenRouter-free, DeepSeek V4 Flash, GLM 5.3 Flash, or their coding
quality. A paid comparison was intentionally not attempted without a frozen
budget and explicit configured credential.

### Historical and deterministic evidence — useful, but not product score

| Evidence | Observation | Correct interpretation |
|---|---|---|
| `benchmark_20_results.json` | `vg-code-max`, DeepSeek V4 Flash: 2/21 pass rows, 19 fail rows, reported 9.5%, all rows capped at one turn, $0.002037 total. | Diagnostic baseline only. The runner has its own model/tool loop and is not the exact CLI/runtime product path. |
| LAM telemetry | 949 recorded calls; 3,671,251 tokens reported saved; estimated $2,387.6489. | Cache/replay telemetry, not fresh live-model competence. The dollar value is an estimate, not an incurred local cost. |
| LAM context baseline | 36/36 gold scenarios simulated at $0. | Validates deterministic plumbing/replay; it cannot establish live coding ability. |

## Confirmed defects and smallest fixes

### P0 blockers

1. **False completion on the default coding harness — critical**

   `runtime/session.py` exempts `vg-code-default` from admission. The CLI
   uses that path, which permits a bare model finish to become `completed`.
   The observed fake and Qwen falsifiers prove the impact.

   **Minimal fix:** protect the public `code` command with the same requirement
   used by gated coding presets: a current postimage, a patch/write receipt,
   a relevant oracle command, and an executed-test count greater than zero.
   Do not silently mutate historical evidence: take the required successor
   baseline first, then change product routing or remove the exemption under
   the existing T-04 governance work.

2. **Default `run-cli` identity reuses unrelated durable state — critical**

   `runtime/entrypoint.py` defaults absent run IDs to `run-cli` while writing a
   durable workspace ledger. This caused the excluded episode to recover the
   fake run.

   **Minimal fix:** generate a UUID/ULID run ID for every new code request;
   permit recovery only when an explicit `--resume <id>` is present. Include
   the generated ID in the first JSON frame and terminal receipt.

3. **llama.cpp tool-call dialect does not become a canonical action — critical**

   The active Qwen template advertises tools with XML-like function syntax,
   while the observed proposal arrived as a JSON-shaped `properties` object.
   It was retained as prose/note, not converted into `fs.search` or rejected
   into a repair loop.

   **Minimal fix:** extend the existing proposal dialect/normalisation path for
   the `llama_cpp` profile. Accept only an exact declared tool and schema; map
   a valid local server tool call to the canonical `ProposalTranslator` input;
   emit a typed malformed-tool event and corrective prompt for anything else.
   Do not add a second provider or second agent loop.

4. **`llama-bridge serve` does not reliably prove it started the active model — high**

   The bridge launch message named a new PID and used `-fa`; the log contains
   an argument error because this server expects `--flash-attn on|off|auto`.
   Process metadata showed an already-running Q2 server with a different PID.

   **Minimal fix:** emit `--flash-attn auto` (or omit it), wait for the child
   PID, and verify both PID ownership and `/props.model_alias` before reporting
   “launched and ready.” This makes performance experiments reproducible.

5. **Local-provider migration is incomplete in source naming — medium**

   The active selection code correctly supports `llama_cpp` but still carries
   legacy aliases and environment naming. The new llama-only skill conflicts
   with that residual surface.

   **Minimal fix:** retain only `llama_cpp` and an optional documented `local`
   alias; use `VANGUARD_LLAMA_ENDPOINT` and `VANGUARD_LLAMA_MODEL`; delete the
   retired names, tests, and documentation in one contained migration.

6. **The target admission falsifier cannot run in this environment — medium**

   `test.falsifiers.test_completion_gate_scope` currently fails to import
   because the active Python interpreter lacks `cryptography`. This is an
   environment/dependency failure, not a new test failure from this work.

   **Minimal fix:** use the project-managed environment (`uv sync` / the
   intended interpreter) before claiming the gate is protected; then run that
   exact falsifier and the new no-false-completion regression test.

## Minimal implementation plan

### PR 1 — truthful, unique, local coding command

Keep the scope to the adapter, selector, entrypoint, session admission policy,
and targeted tests.

| Change | Owner area | Acceptance test |
|---|---|---|
| Unique run ID on new CLI code calls; explicit resume only. | `runtime/entrypoint.py`, CLI request builder | Two new invocations in one workspace have distinct ledgers; `--resume` is the only recovery path. |
| Route the public code command to a gated coding manifest/profile. | CLI/entrypoint/session | Fake `finish` with no patch ends rejected/abandoned, not completed. |
| Bind completion to postimage + relevant verification receipt. | session/admission gate | A task whose oracle still fails cannot emit `completed`. |
| Normalise llama.cpp valid tool calls and reject malformed shapes. | existing `llama_cpp`/dialect path | Qwen's declared read/search call produces a canonical effect; malformed `properties` shape produces typed recovery, never completion. |
| Complete local migration cleanup. | model selector/factory/tests | `--provider llama_cpp --planner local-model` is the documented local route. |
| Fix bridge startup verification. | `tools/llama_cpp/cli.py` | Requested alias, spawned PID, and `/props` agree; invalid server flags fail visibly. |

### PR 2 — frozen Coding P0 corpus

Use the exact P0 command, fresh workspace, unique ID, local server metadata,
one attempt per task, external oracle, and content digests.

Start with three smoke tasks:

1. **FIB-P0:** create a tested Fibonacci module.
2. **CSV-P0:** create a pandas CSV input → transformed CSV output pipeline with
   known fixture output and missing-column behavior.
3. **BUG-P0:** fix a one-file Python defect with a pre-failing and post-passing
   regression test.

Then freeze a 12-task canary: four greenfield, four small bugfixes, and four
data/CLI tasks. Do not alter prompts, tools, task files, model, server flags,
or budgets after the first measured attempt.

Required row fields:

```text
task_id, task_digest, subject_sha, provider, model_alias, server_build,
model_file_digest, context, sampling, run_id, patch_digest, pre_oracle,
post_oracle, executed_tests, status, terminal_reason, turns, input_tokens,
output_tokens, latency, local_cost=unknown, and missingness_reason
```

Metrics to display:

- oracle pass rate and Wilson interval;
- false-completion rate (**must be zero**);
- valid tool-call rate and malformed-tool rate;
- patch rate, test-execution rate, and no-op rate;
- time-to-first-valid-tool, total latency, tokens/s, and turns;
- provider/instrument missingness separate from task failure.

### PR 3 — compare models only after P0 is truthful

Use the same frozen corpus and one-attempt protocol for every arm.

| Arm | Permission/precondition | What it answers |
|---|---|---|
| Local Qwen 27B Q2 | Available now through `llama_cpp`. | Local tool-call and coding baseline. |
| OpenRouter free | Configure `OPENROUTER_API_KEY`; keep it a separate arm. | Whether a hosted free model improves success at the same tools and budgets. |
| DeepSeek V4 Flash / GLM 5.3 Flash | Freeze a spend ceiling and authorize the paid run first. | Cost/latency/pass trade-off, not a substitute for the local baseline. |

Never compare different prompts, task states, retry budgets, or verifier rules.
Never count a provider outage, time cap, malformed response, or unavailable
model as a task failure. Never publish a live percentage from LAM replay.

## Recommended commands after PR 1

Start the pinned local engine with a valid explicit Flash Attention option:

```bash
llama-server \
  -m /home/rock-dev/Models/Qwen3.8-27B-UD-Q2_K_XL.gguf \
  -c 8192 -ngl 99 -t 16 --flash-attn auto \
  --host 127.0.0.1 --port 8080 \
  --alias local-model --jinja
```

Run one isolated coding episode after the truthful settlement and unique-ID
changes land:

```bash
aether code /path/to/fresh-workspace \
  --provider llama_cpp --planner local-model \
  --profile local --benchmark \
  --prompt "Create fibonacci.py with fibonacci(n) and run the supplied tests" \
  --max-turns 8 --json
```

The expected terminal result is either a patch bound to a passing oracle or an
honest non-success result with an actionable failure reason. It must never be
`completed` merely because the model stopped talking.

## Definition of “we have a coding agent”

Call Coding P0 a usable prototype only when all are true:

1. A new command creates a unique run ID and a durable, inspectable ledger.
2. The local Qwen route reaches a declared tool or records a typed tool-format
   failure; prose cannot become an effect or a success.
3. `completed` implies a current patch/postimage and the frozen oracle passed.
4. All three smoke tasks pass in fresh workspaces, or failed tasks report an
   honest failure—not a false success.
5. A frozen 12-task canary has a transparent pass rate, false-completion rate,
   cost/missingness accounting, and retained trajectories.

At that point the team has a real product loop worth improving. The next work
should be selected by the largest failure bucket in the canary—not by adding
more framework layers pre-emptively.

## Commands actually executed for this report

```text
llama-bridge models
llama-bridge status
llama-bridge serve -m Qwen3.8-27B-UD-Q2_K_XL.gguf -c 8192 -ngl 99 --flash-attn -d
llama-bridge chat [constrained JSON tool-selection probe]
node .../cli/dist/src/main.js code [fake falsifier]
node .../cli/dist/src/main.js code [real llama_cpp FIB-P0]
node .../cli/dist/src/main.js code [OpenRouter-free readiness]
python3 -m unittest test.adapters.test_llama_cpp test.runtime.test_model_selection test.falsifiers.test_completion_gate_scope -v
python3 tools/002_LLM_API_MOCK/cli.py stats
```

Test outcome: 8 targeted tests passed; `test_completion_gate_scope` could not
import because the active interpreter lacks `cryptography`. No full-suite PASS
claim is made. No remote paid model was invoked.
