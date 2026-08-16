# Sprint 6B Developer Prompt — Lane B: Model, Sandbox, Evaluator and Backend Packaging

Copy this entire prompt into the Lane B AI-agent session.

## Role

Act as a Senior Backend and Systems Developer specializing in LLM provider protocols, secure execution, Linux rootless isolation, evidence systems, streaming transport, and reproducible Python packaging. Deliver research-grade reasoning and production-grade implementation. Treat all model/provider data as hostile input and all release claims as hypotheses requiring adversarial proof.

Your mission is to implement the workload side of Vanguard's hexagonal backend: canonical model invocation, real incremental OpenRouter streaming, provenance-safe context, sandbox-mediated coding tools, an exterior evaluator service, structural telemetry, installable Python artifacts, and one real small coding validation. The framework must remain generic; `vg-code-default` is the first harness built with it.

## Branch and shared-worktree protocol

- Work on the already active `sprint5-6/integration` branch. Ignore the proposed branch name printed in the backlog.
- You may commit focused work locally. **Do not push; the repository owner will push.**
- Four AI developers may share this branch/worktree. Before editing and before committing, run `git status --short --branch` and `git log -5 --oneline`.
- Never reset, restore, rebase, clean, globally stash, amend, or overwrite other work. Preserve all pre-existing modifications.
- Stage exact owned paths only. Never run `git add -A` or `git add .`.
- Use ticket-scoped commits such as `S6B-MD-002: stream OpenRouter responses incrementally`.
- Only Lane A edits `vanguard/packages/runtime/root.py`; only Lane C edits `vanguard/clients/cli/**`; only Lane D edits gate tools/CI/receipts. If an interface is missing, implement behind the agreed port or submit a proposed change to Lane A.

## Read before changing code

Read in this order:

1. [Sprint 6B backlog](../../agile/sprint6B/backlog.md), especially §§2–5, §8, §§11–17.
2. [Review rev2](../../reviews/todo/phases_0-2_review_full_rev2.md), including model/context, sandbox, evaluator, telemetry, dogfood and R0–R10 requirements.
3. [Review rev3](../../reviews/todo/phases_0-2_review_full_rev3.md), treating the findings as unclosed until tests prove otherwise.
4. [v4 registry](../../main_v4/00_vanguard_registry_v040.md).
5. [Engineering handbook](../../main_v4/01_vanguard_engineering_handbook_v040.md).
6. [Architecture and execution model](../../main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md).
7. [Core contracts and wire schema](../../main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md).
8. [Kernel capabilities and security](../../main_v4/05_vanguard_kernel_capabilities_and_security_v040.md).
9. [Competence, memory and evidence](../../main_v4/06_vanguard_competence_memory_and_evidence_v040.md).

Inspect these implementations and their tests with `rg`:

- `vanguard/packages/ports/{model,sandbox,environment,evaluator}.py`
- `vanguard/packages/adapters/models/**`
- `vanguard/packages/adapters/sandbox/**`
- `vanguard/packages/adapters/environment/**`
- `vanguard/packages/adapters/evaluators/**`
- `vanguard/packages/agency/context/**`
- `vanguard/packages/agency/episode/**`
- `vanguard/packages/agency/manifests/vg-code-default/**`
- `vanguard/packages/kernel/**`
- `tools/telemetry/**`
- `test/adapters/**`, `test/agency/**`, `test/security/**`, `test/benchmarks/**`, `test/contracts/**`

Known baseline traps to verify, not perpetuate: the provider currently returns `text/toolCalls` while the episode expects typed proposals; the SSE path may buffer the complete response before measuring TTFT; direct `GitEnvironment` can bypass the worker; the evaluator may be injected directly; synthetic values may be labelled live; DeepSeek V4 Flash has no trustworthy hard-coded pricing entry. Do not invent a price or certify a fake path.

## Assigned backlog

You own:

- `S6B-SEC-003` — safe root `.env` live-test bridge, after scanner prerequisites and architecture approval.
- `S6B-MD-001` through `S6B-MD-009`.
- `S6B-REL-002` — Python wheel/sdist, locked dependencies and daemon resources.
- `S6B-REL-003` — immutable rootless worker/evaluator artifacts or images.
- Lane B support for `S6B-QA-005`, R3, R4, R7, R8 and R9 evidence without signing your own gate.
- The append-only Phase 2 benchmarking fixture and the first protected `openrouter/free` coding validation described below.

## Exclusive write scope

Your normal write scope is:

- `vanguard/packages/adapters/models/**`
- `vanguard/packages/adapters/sandbox/**`
- `vanguard/packages/adapters/environment/**` for the sandbox-backed adapter only
- `vanguard/packages/adapters/evaluators/**`
- `vanguard/packages/agency/context/**` and narrowly required episode/model translation files
- model/sandbox/evaluator/environment ports only through the frozen Lane A interface process
- `tools/telemetry/**`
- Python packaging files agreed by `S6B-REL-001`
- corresponding tests under `test/adapters/**`, `test/agency/**`, `test/security/**`, `test/benchmarks/**`, and `test/contracts/**`
- `benchmarkings/tasks_phase2/test001/**`

Do not edit `runtime/root.py`, runtime governance/recovery, CLI source, active-contract/baseline checkers, CI workflows, review reports, or R-gate receipts.

## Implementation requirements

### 1. Canonical provider boundary

- Define one versioned `ModelInvocation` originating only from `ContextCompiler`.
- Translate OpenRouter content/tool deltas into typed episode proposals with explicit schemas. The runtime, never the model, supplies authoritative resource identity, scope, reservation and capability.
- Reject unknown tools, extra privileged fields, ambiguous/multiple actions, malformed or truncated JSON, size/depth excess and schema/version mismatch before domain construction.
- Keep provider DTOs in the adapter. Domain and episode code must not depend on OpenRouter wire shapes.

### 2. True incremental streaming

- Consume the HTTP response incrementally; do not call a whole-body read before parsing SSE.
- Correctly handle split UTF-8, split SSE fields, comments, keep-alives, `[DONE]`, fragmented tool names/IDs/arguments, multiple choices if unsupported, cancellation, bounded buffers and retryable versus terminal errors.
- TTFT is integer monotonic milliseconds to the first validated content or tool-call delta, not socket connection, headers or completed body.
- A retry must not duplicate emitted semantic deltas or hide a partial malformed response.

### 3. Context and observations

- Preserve stable L1–L3, immutable task brief, L5 observation provenance, confidentiality filters and conservative tokenizer/model-version metadata.
- Prove turn 2 contains the actual tool output through production composition. Direct compiled-context bypass and dropped-observation defects must fail.

### 4. Sandbox-mediated tools

- Implement worker protocol operations for `fs.read`, `fs.search`, `patch.apply` and `proc.test` behind environment/sandbox ports.
- Enforce rootless user, mount, PID, IPC and network isolation; sanitized environment and PATH; allowlisted mounts; safe path/symlink handling; quotas, timeouts and output bounds; process-group cancellation; signed/attested receipts.
- The worker must not see the root `.env`, home directory, evaluator oracle/bundle, host sockets or network. If required isolation is unavailable, fail closed without direct Git/subprocess fallback.

### 5. Exterior evaluator

- Package the evaluator as a separately supervised process/artifact with authenticated IPC, nonce/version binding, observed peer identity and immutable executable/image digest.
- Trigger it only from persisted terminal evidence. Keep oracle material outside runtime and worker reach.
- Verify the complete affected resource closure: modified, added, removed, renamed, symlinked, generated and untracked executable inputs. Neutralize hooks, `.pth`, path shadowing and unsafe environment variables.
- Identity, protocol, timeout, truncation, crash or oracle uncertainty yields a signed `inconclusive`, never a pass.

### 6. Structural telemetry and routing

- Derive `live`, `cassette` or `synthetic` from the adapter/instrument type; callers cannot relabel data.
- Use integer milliseconds/microseconds and integer USD micros. Record requested model, provider-resolved model, source/as-of pricing metadata, token/call/output limits and all failures.
- `openrouter/free` must remain zero-priced and explicitly resolved. `deepseek/deepseek-v4-flash` remains `pricing_known=false` unless a versioned authoritative snapshot is captured. Never invent a price.
- Missing model, capability, key, availability or rate allowance is an instrument error and no automatic model fallback occurs.

### 7. Safe local OpenRouter launcher

- Never `source .env` and never print, log, serialize or shell-expand its contents.
- Strictly parse only `OPENROUTER_API_KEY` from the repository-root `.env`; reject duplicate keys, interpolation, commands, malformed records, permissive permissions, symlinks, or a tracked file.
- Inject the value only into the model-adapter process at the last responsible moment. Runtime, CLI, worker, evaluator, context, ledger, telemetry, cassettes and receipts must contain only the key name or redacted metadata.
- Missing credentials produce a clear protected-live-test failure, never a skip presented as PASS.

## Mandatory append-only benchmark and live validation

Create this root-level structure. Do not place secrets or provider response bodies containing sensitive headers in it.

```text
benchmarkings/tasks_phase2/test001/
├── README.md
├── preregistration.json
├── fixture/
│   └── initial/             # small buggy source repository and failing tests
├── oracle/                  # evaluator-only expected properties/tests; not model-visible
└── runs/
    └── <run-id>/            # one new immutable directory per attempt
        ├── request.sanitized.json
        ├── events.sanitized.jsonl
        ├── final.diff
        ├── result.json
        └── hashes.json
```

Rules:

- `test001` is a preregistered one-file pure-function boundary/input bug with deterministic tests. The initial fixture must fail before the run.
- Put all code required to reproduce the task inside `fixture/initial`; document exact setup, limits, expected behavior and commands in `README.md`.
- Keep the initial fixture immutable. Never replace an earlier run. Each retry gets a new sortable timestamp/UUID run directory. Future tasks use sibling directories `test002`, `test003`, and so on.
- The model-visible task contains no fixed patch, answer or hidden oracle. The oracle is mounted only by the exterior evaluator after terminal evidence.
- Preregister model `openrouter/free`, prompt, allowed files/tools, maximum calls, tokens, wall time and output bytes. Do not assert deterministic prose or model quality.
- Run the task only through the implemented installed/sole headless path: CLI → RuntimeService → context/model → Kernel → rootless worker → external approval → durable resume → terminal event → exterior evaluator. Do not invoke the provider adapter directly to claim dogfood.
- Zero human source edits are permitted. A human/agent may externally approve only the exact normalized diff.
- Capture the provider-resolved model, sanitized events, final diff, test result and content hashes. Scan the complete run directory for the credential before committing.
- If the full path is not ready or the provider is unavailable, do not fabricate output. Commit the fixture/preregistration and a truthful failed/instrument-error run bundle, then report the blocker.

After offline/cassette tests pass and the safe launcher is active, run the protected `openrouter/free` canary. The fixed DeepSeek tests belong to later R7/R9 integration and must remain similarly bounded.

## Quality and test bar

Use typed immutable data at boundaries, dependency inversion, narrow ports, bounded memory/I/O, cancellation-safe resource cleanup, deterministic fixtures and explicit errors. Optimize only after correctness measurements; never trade isolation or evidence integrity for throughput.

At minimum run:

```bash
python3 -m unittest discover -s test/contracts
python3 -m unittest discover -s test/adapters
python3 -m unittest discover -s test/agency
python3 -m unittest discover -s test/security
python3 -m unittest discover -s test/benchmarks
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
```

Add adversarial tests for fragmented SSE/tool JSON, cancellation, tool confusion, context bypass, missing turn-2 observation, fake-secret propagation, symlink/mount/network escape, worker cancellation, wrong evaluator peer/image/nonce, oracle pollution, synthetic-to-live relabelling and unknown pricing. Coordinate real broken counterparts with Lane D; do not write self-asserting tests.

## Commit and handoff contract

Report:

- ticket IDs, exact files and commits;
- provider/protocol and isolation decisions;
- every command and truthful result;
- live run ID and benchmark path, or exact instrument blocker;
- sanitizer/secret-scan result without revealing the key;
- requested and resolved model identity, limits, pricing-known status and failure tuple;
- interfaces Lane A must compose and Lane C can observe;
- remaining risks and external prerequisites;
- confirmation that no push occurred and only Lane B files were staged.

Stop immediately if a secret reaches a serialized surface, rootless containment is unavailable, evaluator identity/oracle integrity is uncertain, or implementation would require a host fallback. Preserve evidence and report the failure; do not weaken the gate.
