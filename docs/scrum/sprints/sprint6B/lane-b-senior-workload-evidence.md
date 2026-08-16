# Sprint 6B Lane B — Senior Workload, Evidence and Platform Packet

**Assignee:** Senior Developer B — Principal AI/Systems Architect  
**Delegated authority:** Tech Lead and Project Lead for workload/evidence implementation and day-to-day platform decisions  
**Accountable outcome:** one provider-neutral cognitive/workload path with contained tools and an exterior trusted verdict  
**Primary review partner:** Lane A Senior  
**Complexity:** Level 5/5 — release critical

## 1. Mission

Build the generic workload and evidence side of Vanguard: canonical model invocation/proposal translation, LAM/Ollama/OpenRouter adapters, prefix-stable context observations, one rootless coding worker, a separately supervised evaluator, truthful telemetry and installable backend/platform artifacts.

The lane is complete only when provider data remains untrusted, every model-driven observation/effect crosses Kernel and the worker perimeter, evaluator authority is exterior and attested, and substituting LAM/Ollama/OpenRouter changes only the ModelPort adapter—not the episode engine, runtime lifecycle or harness framework.

## 2. Read before editing

Read completely, in order:

1. [Sprint 6B closure review](sprint_6B_review_overview_and_next_tasks.md).
2. [Sprint 6B backlog](backlog.md), especially §§2–5, §8 and §§11–17.
3. [Sprint 6B close guidelines](../../development_guides/guidelines_sprint_6B_close.md).
4. [System architecture ICD](../sprint0/system-architecture-icd.md).
5. [Architecture and execution model](../../main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md).
6. [Core contracts and wire schema](../../main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md).
7. [Kernel and security](../../main_v4/05_vanguard_kernel_capabilities_and_security_v040.md).
8. [Competence, memory and evidence](../../main_v4/06_vanguard_competence_memory_and_evidence_v040.md).
9. [LAR router](../../../tools/001_LLM_API_ROUTER/README.md) and [LAM mock](../../../tools/002_LLM_API_MOCK/README.md).
10. [Active MVP Contract](../sprint0/active-mvp-contract.json).

Inspect model, context, episode, environment, sandbox, evaluator, telemetry, manifests, packaging, containers and their tests before editing. Preserve proven compiler/kernel components and replace only unsafe seams.

## 3. Owned backlog

Lane B is the delivery owner for:

- shared `ADR-FREEZE` proposals for model, worker, evaluator, telemetry and platform contracts;
- `MODEL-CONTRACT`, `LAM-VERTICAL`, `SANDBOX`, `EVALUATOR`, `PROVIDERS`;
- `S6B-SEC-003` and backend secret-isolation tests;
- `S6B-MD-001` through `S6B-MD-009`;
- backend portions of `S6B-REL-002/003/004/005/006`;
- `S6B-QA-001/002/005` and adapter/platform portions of adversarial verification;
- integration ownership for R3, R4, R7 and R8;
- dogfood task fixtures, hidden oracles and sanitized run bundles, without self-signing R9.

Lane B does not implement RuntimeService lifecycle, approval state, CLI transport/business commands, contract closure or candidate release decisions. Those belong to Lane A.

## 4. Normal write scope

- `vanguard/packages/ports/{model,sandbox,environment,evaluator}.py` only through the joint frozen-interface process;
- `vanguard/packages/adapters/models/**`;
- `vanguard/packages/adapters/sandbox/**`;
- sandbox-backed parts of `vanguard/packages/adapters/environment/**`;
- `vanguard/packages/adapters/evaluators/**`;
- `vanguard/packages/agency/context/**` and narrowly required proposal-translation/manifest files;
- `tools/001_LLM_API_ROUTER/**` and `tools/002_LLM_API_MOCK/**` when improving test/diagnostic interoperability;
- `tools/telemetry/**`;
- `containers/**`, backend packaging resources and corresponding tests;
- `benchmarkings/tasks_phase2_LAM/**` and preregistered dogfood fixtures.

Do not edit `runtime/root.py`, RuntimeService/governance/recovery, CLI source, contract/baseline gates or release receipts to work around a missing interface. Propose the interface to Lane A.

## 5. Decision rights

Lane B may decide without escalation when the choice:

- is behind a frozen port and does not alter its semantics;
- preserves provider neutrality and manifest-driven behavior;
- strengthens fail-closed isolation/evidence behavior;
- does not broaden mounts, secrets, network, executable authority or evaluator reach;
- has reference and adversarial tests.

Lane B must obtain Lane A approval before changing shared schemas, canonical proposal meaning, event/receipt fields, runtime dependencies, public configuration, artifact compatibility or failure classification. Senior A reviews all sandbox/evaluator trust-boundary changes.

Lane B must stop live work if a secret reaches a serialized surface or if required isolation/evaluator identity is uncertain. Credential rotation, history cleanup, remote actions, publishing and tag creation require separate repository-owner authorization.

## 6. Implementation sequence

### B0 — Canonical model boundary

Jointly freeze one `ModelInvocation` and `ModelProposal`. ContextCompiler is the only production invocation source. Provider DTOs remain inside adapters. Translation follows:

```text
provider content/tool delta
  → strict provider-neutral parsed call
  → manifest tool lookup and argument schema validation
  → authoritative runtime resource/scope/reservation binding
  → canonical ModelProposal
  → episode parser
```

Reject malformed/truncated JSON, unknown tools, extra privileged fields, size/depth excess, ambiguous/multiple actions and unsupported versions. The model never supplies capability, scope, reservation, approval identity or evaluator truth.

### B1 — LAM-first vertical adapter

Keep LAR as a diagnostic/benchmark CLI; do not spawn it from production runtime. Use LAM as an explicit external ModelPort test endpoint. Add a deterministic multi-turn scenario:

```text
read target
  → receive real tool observation
  → propose exact patch
  → receive patch receipt
  → run test
  → receive test receipt
  → finish
```

The scenario must advance from tool observations, not server-side sessions or a fixed patch embedded in the runner. Run it only through installed CLI → RuntimeService → production composition. Label it `mock`, never `live`.

### B2 — Context and provider adapters

Preserve L1–L3 prefix bytes, immutable task brief and provenance-bearing L5 observations. Prove Turn 2 contains actual prior tool output. Add confidentiality filtering and tokenizer/model metadata.

Implement explicit adapters/modes for:

- LAM/OpenAI-compatible test endpoint;
- Ollama local endpoint;
- OpenRouter protected live endpoint.

No model/provider fallback is automatic. Consume SSE incrementally with bounded buffers, strict UTF-8/JSON/tool assembly, cancellation and retry only before semantic output. TTFT is integer monotonic milliseconds to the first validated content/tool delta. Record requested/resolved identity and truthful pricing provenance.

### B3 — One sandbox worker for every tool

Implement an authenticated typed worker request/receipt protocol for `read`, `search`, `patch` and `test`. Every product operation crosses Kernel and the same rootless perimeter. Enforce sanitized env/PATH, isolated user/mount/PID/IPC/network namespaces, explicit mounts, safe path/symlink handling, quotas, output bounds, timeout and process-group cancellation.

The worker cannot read repository-root `.env`, home, evaluator bundle/oracle, runtime/evaluator sockets, host network or undeclared paths. Bubblewrap/runtime absence and failed probes are composition errors; never fall back to host Git/filesystem/subprocess. Persist probe-derived containment receipts.

### B4 — Exterior evaluator service

Package an executable evaluator daemon/client and supervisor configuration. Run it as UID 10002 with authenticated bounded IPC, nonce/request/version binding and peer verification in both directions. Measure executable/image/config/oracle digests instead of echoing configuration claims.

Only persisted terminal evidence can request evaluation. Seal oracle material independently and verify complete affected-resource closure, including added/deleted/renamed/symlinked/generated/untracked executable inputs, hooks, `.pth`, path shadowing and unsafe environment. Sign verdicts. Any peer, image, oracle, protocol, timeout, truncation or crash uncertainty yields signed `inconclusive`.

### B5 — Structural telemetry and safe credentials

Derive `live`, `mock`, `cassette` and `synthetic` from adapter construction; callers cannot relabel. Use integer units and record all failures. Unknown pricing is `pricing_known=false`.

The protected launcher strictly parses only `OPENROUTER_API_KEY` from ignored, untracked, permission-restricted `.env`; never `source` it. Inject the value only into the model adapter process. Ensure it cannot reach CLI frames, context, ledger, worker/evaluator env, cassettes, telemetry, logs, receipts or artifacts.

### B6 — Backend and platform artifacts

Build wheel/sdist resources and runtime/evaluator entry points jointly with Lane A. Build worker/evaluator images that install the exact candidate package, run non-root, expose no secret and use real content digests. Provide readiness, graceful shutdown, state/mount requirements and predecessor rollback compatibility. Generate backend SBOM/license/provenance inputs for Lane A candidate assembly.

## 7. Required acceptance and adversarial tests

Lane B must prove:

- valid content/finish and typed read/search/patch/test proposals;
- malformed, unknown, ambiguous, multiple, oversized and truncated calls fail closed;
- split UTF-8/SSE/tool arguments, cancellation, bounded retries and truthful TTFT;
- stable L1–L3 and actual Turn 2 tool observation through production composition;
- no model-supplied scope/capability/reservation authority;
- LAM, Ollama and OpenRouter use the same canonical proposal path;
- missing provider/key/model is an instrument error without fallback;
- read/search/patch/test cannot bypass worker/Kernel;
- home, `.env`, network, external symlink, sockets and oracle access are denied;
- unavailable containment cannot invoke host execution;
- timeout kills the complete worker process group;
- wrong evaluator peer/UID/image/nonce/protocol, oracle mutation/pollution, timeout/truncation/crash returns signed `inconclusive`;
- non-terminal runs cannot obtain a verdict;
- synthetic/mock/cassette evidence cannot be labelled live;
- built artifacts contain no secret and run with source tree absent.

## 8. Lane handoff contract

Before Lane A composes adapters, Lane B supplies:

- port-conformant ModelPort, worker and evaluator client implementations;
- adapter registry names and configuration schemas;
- health/readiness behavior and explicit failure taxonomy;
- signed/attested receipt and verdict fields matching golden vectors;
- LAM integration fixture plus deterministic expected control flow;
- artifact digests and install/start commands;
- narrow tests and deliberately broken counterparts.

For every handoff, report ticket IDs, exact files, provider/source, trust assumptions, limits, commands/results, requested/resolved model, pricing-known state, secret scan, artifact hashes and unresolved risks.

## 9. Verification commands

Run narrow tests continuously, then at lane gates:

```bash
python3 -m unittest discover -s test/contracts
python3 -m unittest discover -s test/adapters
python3 -m unittest discover -s test/agency
python3 -m unittest discover -s test/security
python3 -m unittest discover -s test/benchmarks
python3 tools/002_LLM_API_MOCK/test_mock.py
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/run_broken_tests.py
python3 tools/scan_secrets.py
```

Protected live tests run only after the LAM path is green and the safe launcher has validated local secret handling. Report provider/rate-limit failures as instrument errors, not skipped passes.

## 10. Stop rules

Stop if a secret is serialized, provider data acquires authority, context observations are lost, a product tool can run on the host, containment is unavailable, evaluator identity/oracle integrity is uncertain, mock data is labelled live, or a shared interface changes without Lane A review. Preserve the failure evidence; do not weaken the control.

