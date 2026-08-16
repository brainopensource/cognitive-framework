# MVP Beta Delivery Audit — Independent TODO and Ship Review

**Review date:** 2026-08-16  
**Repository:** Aether-D-System / Vanguard  
**Branch inspected:** `sprint5-6/integration`  
**HEAD inspected:** `46ce7d7`  
**Decision:** **NO-GO — do not tag, publish, or describe this tree as a working MVP Beta**

## 1. Executive answer

The supplied Sprint 5–6 report has the correct central conclusion: there is no trustworthy, installable path from `vg` to a real or mocked model, through the governed loop, through contained effects and external approval, to an exterior verdict. The proposed `v0.6.0-beta` tag must remain withheld.

The statement “four defects were patched” is too generous. The current uncommitted changes improve four seams, but do not close them:

1. approval no longer accepts a Boolean as a signature, but verification still requires the runtime to possess the HMAC secret;
2. `proc.exec` is pointed at Bubblewrap, but file reads, writes and patches still use the host `GitEnvironment`, and the Bubblewrap binding has no production-path containment proof;
3. the dead `episodeView` field is removed, but the provider still returns `{text, toolCalls}` while the episode parser requires `{kind, action, resource, args, reservation}`;
4. `IsolatedEvaluator` is selected from the manifest, but is instantiated directly inside the runtime with an empty oracle, `image_digest="unverified"`, and expected UID 10002. This is fail-safe but not a usable exterior evaluator service.

The user's summary is therefore right, with one precision correction: evaluator daemon/client source files exist, but no deployable, supervised, attested evaluator service is composed into the product path.

The project has valuable foundations: a serious architecture, a real capability kernel, ledger primitives, prefix-stable context compilation, provider parsing, a rootless runner, evaluator probes, typed CLI application code, governance tooling, and a large test suite. What it does not yet have is the product those parts claim to form.

## 2. Audit basis and repository-state warning

This audit distinguishes three different truths:

- **HEAD truth:** what is committed at `46ce7d7` and can be cloned or tagged;
- **working-tree truth:** ten modified files containing the supplied report's patches;
- **release truth:** what a clean installation can execute through the public CLI.

The working tree was dirty before this review. The modified runtime, CLI, evaluator and tests are not part of HEAD. No release evidence may cite them until they are reviewed and committed to a candidate SHA. This review changed only this report.

## 3. Claim-by-claim ruling on the supplied report

| Claim | Ruling | Audit finding |
|---|---|---|
| Kernel, ledger and L1–L5 compiler are real | **Confirmed, narrowly** | Implementations and focused tests are substantive. This establishes components, not the product path. |
| A single trust-preserving product path is absent | **Confirmed** | There is no RuntimeService command server and the CLI cannot start a runtime run. |
| “4/4 defects patched” | **Rejected as closure language** | All four changes are partial and uncommitted; each retains a Beta blocker. |
| HMAC approval shares authority with runtime | **Confirmed** | HMAC verification requires the same symmetric secret that can sign. External construction does not create cryptographic separation. |
| No Unix RuntimeService exists | **Confirmed** | Only the evaluator uses a Unix socket. No runtime command service implements StartRun/GetRun/approval/resume/etc. |
| Evaluator UID 10002 is not deployed | **Confirmed** | Code and a Dockerfile declare it, but there is no working supervisor/deployment/product composition or real image attestation. |
| `--release` is red on 49 merged rows | **Confirmed** | It reports 0/49 merged evidence and fails. There are 50 total active requirements; one is outside merged scope. |
| CLI tests are 22/22 | **Confirmed on this working tree** | They mainly prove application/replay/feed behavior and absence of a daemon, not a live product. |
| Full suite had 388 tests and Node errors | **Stale** | The current tree runs 438 Python tests with 2 skips successfully when Unix sockets and Bubblewrap are permitted. |
| Evaluator daemon is absent | **Incorrect if read literally** | `daemon.py`, `client.py`, tests and container files exist. The deployable and composed service is absent. |
| `proc.exec` sandbox issue is patched | **Only partially true** | The new binding covers one verb. File and patch effects remain direct host operations, and product-path containment is unproved. |
| Context dialect issue is patched | **Only partially true** | Removing `episodeView` simplifies context input, but the model-output dialect mismatch still prevents a real OpenRouter tool call from becoming an episode proposal. |
| CLI live stubs fail closed | **False for the actual headless entry path** | Non-TTY stdin activates fixture-feed mode. Empty stdin makes `vg run --headless` return success with no events. `vg daemon status` reports an error but exits 0. |
| Contract default PASS is intentional | **Technically true, operationally unsafe** | Closure mode permits open rows, but the active-contract runner then executes zero commands and prints PASS. CI can present a misleading green signal. |
| Baseline drift is expected | **Confirmed, still blocking** | `check_baseline_manifest.py` fails on the contract checker digest. Resealing must be authorized and SHA-bound. |
| `.env` is clean in the tree but risky in history | **Confirmed** | Tree scan passes; `scan_secrets.py --all-refs` fails on a reachable `.env` object. There are 21 `refs/original` refs. Do not print or copy the secret during remediation. |
| Three live Q2 dogfood runs are missing | **Confirmed** | Existing runs are scripted evidence, not three operator-used, no-hand-patch product runs. |

## 4. Additional material findings

### P0-01 — The CLI can falsely succeed without a runtime

`clientFor()` selects `LiveRuntimeClient(stdinLines())` whenever stdin is not a TTY. That mode is a fixture parser, not a RuntimeService transport. `startRun()` fabricates local run/episode IDs in feed mode, and an empty event stream leaves `streamRun()` at exit code 0.

Observed from the built CLI:

```text
node .../dist/src/main.js run . --headless --prompt audit ...
exit 0; no output
```

`daemon status` also returns process exit 0 unless the user supplied `--headless`, because `main.tsx` only calls `process.exit(exitCode)` under that flag.

**Required fix:** remove automatic feed selection. Production defaults to authenticated daemon transport. Replay/feed/scenario must require explicit flags, must label every frame synthetic/replay, and must never implement mutable commands. Always set `process.exitCode` for every command. A run that sees EOF before a terminal event is an instrument/transport error, exit 2.

### P0-02 — Provider output cannot drive the episode loop

The OpenRouter adapter returns:

```json
{"text": "...", "toolCalls": [{"name": "...", "arguments": {}}]}
```

The episode's `parse_proposal()` requires `kind`, and for effects also requires `action`, `resource`, `args`, and integer reservations. A live provider result therefore terminates as an instrument error before a tool can run.

Malformed non-streaming tool arguments are also converted to `{"raw": ...}` or ignored rather than rejected at the provider boundary. That contradicts the fail-closed claim.

**Required fix:** freeze one canonical `ModelInvocation` and one canonical `ModelProposal`. Translate exactly one provider tool call into a typed proposal through a strict, manifest-aware translator. Reject unknown tools, multiple ambiguous calls, invalid JSON, forbidden resource authority, and missing reservations before kernel construction. Add a real two-turn test proving Turn 2 sees the actual Turn 1 receipt.

### P0-03 — LAR and LAM are not integrated with Vanguard

`tools/001_LLM_API_ROUTER` (LAR) and `tools/002_LLM_API_MOCK` (LAM) work as standalone developer tools. The LAM test suite passes when loopback sockets are allowed, and the LAR mock smoke command returns a response. However, no production Vanguard module imports or adapts either one.

Consequences:

- Vanguard has no production Ollama `ModelPort` adapter;
- `vg --model mock` does not route to LAM;
- LAR's free-form `LLMResponse` is not an episode `Proposal`;
- LAM's tool-call protocol is not exercised through RuntimeService, context, kernel, sandbox, approval and evaluator;
- LAR silently falls back from unavailable HTTP mock to an in-memory catalog and then a generic string, which is useful for diagnostics but unacceptable in release or dogfood mode.

**Required integration design:**

1. Keep LAR as a diagnostic/benchmark CLI; do not spawn it from the runtime.
2. Extract or implement provider adapters behind `ModelPort`: OpenRouter/OpenAI-compatible and Ollama.
3. Make endpoint, provider, model, secret reference and source mode explicit in the harness/runtime request.
4. Use LAM as a protocol-faithful integration-test service. Add a `read → patch → test → finish` answer-bank scenario with real tool calls and tool-result-driven turn advancement.
5. Run the same RuntimeService acceptance suite against LAM, cassette mode and protected live providers. Never silently fall back between them.
6. Record `live`, `mock`, `cassette` or `synthetic` structurally at adapter construction; record requested and resolved model identities.

### P0-04 — Sandbox composition remains porous

The patch maps only `proc.exec` to `_SandboxEffect`. `fs.read`, `fs.write`, `patch.apply`, and `fs.patch` still bind to `GitEnvironment` in the runtime process. `GitEnvironment` performs host filesystem and Git subprocess operations. An allowlist and path check are useful controls but are not OS containment.

The new `_SandboxEffect` also creates a placeholder “sealed evaluator” file per call, does not clean its temporary directory, uses presence of `/usr/bin/bwrap` as its health check, and does not persist a signed containment receipt. These are prototype behaviors.

**Required fix:** one sandbox worker protocol must own every product observation/effect. The runtime sends typed requests; the worker performs read/search/patch/test inside the same verified perimeter. Bubblewrap absence or failed probes must fail composition in product mode. Test denied access to home, root `.env`, runtime/evaluator sockets, network, external symlinks and undeclared paths.

### P0-05 — Approval and recovery are not an exterior authority

Rejecting Boolean callbacks is correct. Supplying an HMAC key to the runtime is not sufficient: symmetric verification authority is signing authority. The current challenge also lacks the full durable binding proposed by Sprint 6B (tenant/owner/run, policy, reservation, challenge event, expiry and revocation context).

The runtime resumes within the same call and does not establish ledger-only restart, exactly-once effect recovery, command idempotency, or durable revocation.

**Required fix:** use Ed25519 (or another approved asymmetric signature), with the operator client/key agent holding the private key and runtime holding only trusted public keys/key IDs. Persist challenge before suspension and decision before re-dispatch. Reconstruct solely from the ledger after process death. Run a kill matrix before/after challenge, decision, grant, intent, effect and receipt.

### P0-06 — Evaluator code exists but the trust claim does not

The runtime patch imports and constructs `IsolatedEvaluator` directly. It passes an empty oracle, an invalid image digest and UID 10002, so normal execution cannot yield a useful trusted verdict. This is safer than a fake PASS but not product completion.

The daemon prototype is not yet deployable:

- its module has no CLI/main entry point, while the container declares `python3 -m ...daemon`;
- the Dockerfile does not copy/install the Vanguard package;
- the client verifies peer UID, but the daemon does not authenticate/authorize its caller;
- the configured image digest is reported, not measured from the running artifact;
- verdicts are unsigned and are not shown persisted as EvidencePlane ledger events;
- `serve_once()` has no supervisor, concurrency, socket permission, shutdown or restart policy;
- exceptions print tracebacks into runtime output.

**Required fix:** package a dedicated evaluator executable and immutable image, supervise it under UID 10002, authenticate both IPC directions, measure executable/image/config/oracle digests, trigger only from persisted terminal evidence, sign the verdict, and persist it through the RuntimeService ledger. Every instrument failure must become `inconclusive` without leaking a traceback to the protocol.

### P0-07 — The release gate is red, but the default gate is partly vacuous

Observed:

```text
check_active_mvp_contract.py            PASS; 0/49 merged evidence
check_active_mvp_contract.py --release  FAIL; 49 open merged rows
run_active_contract_tests.py            PASS; 0 covered tests, 0 commands
```

The explicit release failure is correct. The normal contract test runner executing nothing is not useful CI assurance. Furthermore, the contract checker checks receipt presence for covered rows, but does not yet prove candidate SHA, command output digest, signature, independent countersignature, or subject/evidence-commit relationship.

**Required fix:** during closure, run all applicable open and covered registered tests, or introduce an explicit `--candidate` mode that does. A “0 commands executed” result must be non-release/non-candidate only and visibly marked SKIP/OPEN, never PASS. Validate structured receipts cryptographically and against the frozen candidate SHA before allowing `covered`.

### P0-08 — Security incident closure is incomplete

The root `.env` is ignored, untracked, permission-restricted, and the current tree scanner passes. The all-ref scanner fails because an `.env` object remains reachable. This means `SEC-01` is not closed.

**Required fix:** first revoke/rotate the provider credential through the provider. Then, with repository-owner authorization, coordinate a history rewrite across every affected local and remote ref, remove backup refs, force-update the authorized remote, invalidate stale clones, and verify both all-ref and clean-clone scans. Never include the secret value in a ticket, command line, log or receipt.

### P1-01 — Distribution artifacts are declarations, not a releasable product

The CLI can be packed in dry-run form, but the package contains only the client; there is no runtime service to connect to. The Python project has no console entry points for a runtime daemon or evaluator. The worker/evaluator Dockerfiles do not copy/install the code they claim to execute. Container manifest digests include obvious placeholder values. No repository `LICENSE` file was found even though package metadata says Apache-2.0.

**Required fix:** produce and test three version-locked artifacts:

- `vanguard-runtime` Python wheel with `vg-runtime` and `vg-evaluator` entry points;
- `@vanguard/cli` npm package exposing `vg`;
- immutable Linux worker/evaluator OCI images referenced by real digests.

Add license text, changelog, security policy, supported-platform matrix, SBOMs, checksums, provenance/signatures, install/uninstall/upgrade/rollback docs, and clean-machine smoke tests. A single installer may coordinate the artifacts, but it must not hide their versions or trust boundaries.

### P1-02 — Documentation overstates and contradicts the product

The root README says Sprint 6 delivers a “Production-grade lightweight Coding Agent,” while the active Sprint 6B contract correctly says release NO-GO. The CLI README still describes a scaffold/MockRuntime integration boundary. The packages README says there is no cognitive loop. These cannot all describe the same candidate.

Model lists and prices are hardcoded/static and described as “verified” without candidate-bound canary evidence. Treat model availability, routing and pricing as dated external facts, not source-code truth.

**Required fix:** publish one Beta status page and one architecture/install path generated or checked against the candidate. Label limitations explicitly: Linux-only, one coding harness, human approval, no AGI claim, Q3/Q4 deferred, live model availability variable.

## 5. What is actually ready to keep

Do not rewrite the project wholesale. Preserve and harden:

- domain canonicalisation, wire primitives and artifact graph;
- Kernel S0–S12, attenuation, budget and provenance logic;
- ledger reducer/store primitives;
- L1–L5 context compiler and prefix-stability tests;
- CLI application/TUI rendering above `RuntimeClient`;
- Bubblewrap probe design;
- isolated evaluator probe logic;
- OpenRouter incremental SSE parser after strict proposal translation is added;
- LAM answer-bank/cassette concepts and LAR as a developer diagnostic;
- boundary, TCB, secret, must-fail and documentation gates.

The correct rewrite target is the seam graph: service protocol, model translation, worker transport, approval authority, durable lifecycle, evaluator service, and release evidence.

## 6. Recommended Beta architecture

```text
Installed vg CLI
  ├─ explicit replay/demo mode (read-only, visibly synthetic)
  └─ authenticated Unix RuntimeService protocol
       ├─ durable command inbox / idempotency keys
       ├─ append-only event outbox / cursor stream
       ├─ one event-sourced run + approval state machine
       ├─ ContextCompiler → canonical ModelInvocation
       ├─ ModelPort
       │    ├─ OpenRouter/OpenAI-compatible
       │    ├─ Ollama
       │    └─ LAM test endpoint
       ├─ strict provider-call → ModelProposal translator
       ├─ Kernel S0–S12
       ├─ authenticated sandbox worker for all tools
       ├─ public-key approval verifier
       └─ terminal-event trigger → authenticated evaluator client
              └─ UID 10002 evaluator → signed verdict → ledger
```

Framework policy must remain data-driven. Runtime code owns generic lifecycle and port composition. The `vg-code-default` harness pack owns coding tool schemas, prompt, context/routing/budget policy and evaluator reference. A second harness must be addable without changing the episode engine or RuntimeService protocol, but demonstrating non-coding generality remains Q4 and is not a Beta gate.

## 7. Delivery plan and critical path

The existing Sprint 6B backlog is directionally strong, but 14 working days is an aggressive best case for the present gap. A credible commitment is **4–6 calendar weeks with three to four experienced contributors**, after interface freeze. Shorten scope, not evidence.

### Gate 0 — Restore one source of truth (2–3 days)

1. Accept the Beta scope: Chapter 10 Q1+Q2 only.
2. Preserve current dirty work on a reviewed branch; do not tag it.
3. Add decisions for RuntimeService wire/auth, Ed25519 approval, worker protocol, evaluator IPC/signing, lifecycle/recovery and artifact distribution.
4. Fix the active-contract runner's zero-test PASS and define structured receipt validation.
5. Rotate the credential and schedule separately authorized history cleanup.
6. Make README/status language match NO-GO.

**Exit:** frozen schemas/golden vectors; all known blockers owned; candidate gates intentionally red for the correct reasons.

### Gate 1 — Build the cassette/LAM vertical product slice (5–7 days)

1. Implement durable RuntimeService over a bounded Unix protocol with peer authentication.
2. Implement Start/Get/Stream/Cancel/Checkpoint/Resume/Approve/Correct/Explain command semantics and stable error/exit mapping.
3. Remove implicit stdin feed mode and all fabricated production successes.
4. Add canonical model invocation/proposal translation.
5. Connect LAM through `ModelPort` and complete a scripted multi-turn coding task through the installed CLI.

**Exit:** installed `vg` → daemon → context → LAM → kernel → worker → approval suspension/resume → terminal event, with restart and zero in-process fake fallback.

### Gate 2 — Close the trust perimeter (5–7 days, partly parallel)

1. Route read/search/patch/test through one rootless worker protocol.
2. Add Ed25519 operator signing and public-key verification.
3. Implement ledger-only recovery and the forced-kill/exactly-once matrix.
4. Package and supervise evaluator UID 10002 with measured digests and signed verdicts.
5. Persist every challenge, decision, effect intent/receipt and verdict.

**Exit:** adversarial tests prove denied escape, forged/transplanted/replayed approval rejection, restart safety, evaluator exteriority and fail-closed uncertainty.

### Gate 3 — Add honest model modes (3–5 days)

1. Run identical protocol tests against LAM and cassette mode.
2. Add Ollama `ModelPort` support with explicit endpoint/model selection.
3. Run protected OpenRouter canaries with strict secret injection and no fallback.
4. Record true source, requested/resolved model, incremental TTFT, integer token/cost fields and pricing provenance.

**Exit:** mock/local/cloud differ only at the ModelPort adapter; the governed execution path is identical.

### Gate 4 — Build, install and operate artifacts (3–5 days)

1. Build wheel, npm tarball and OCI images from a clean checkout.
2. Install them on a clean supported Linux VM with no source tree or `node_modules`.
3. Exercise start/status/stop, run, approve, resume, trace, why, upgrade and rollback.
4. Generate SBOM, checksums, signatures and compatibility manifest.
5. Run full unit, typecheck, package, boundary, TCB, must-fail, security and release gates.

**Exit:** repeatable release candidate at one immutable SHA and artifact digest set.

### Gate 5 — Q2 dogfood and release authorization (3–5 days)

1. Preregister three small real bugs in repositories known by the operators.
2. Use only the installed CLI and candidate artifacts.
3. Permit prompt/approval/correction interaction, but zero human source edits.
4. Capture cost, model, turns, elapsed time, restart/approval/evaluator evidence and final test result.
5. Record the human answer: “Would I reach for this next time?”
6. Independently validate receipts and release gate at the frozen SHA.

**Exit:** three valid runs, honest positive Q2, release gate green, security/history gates closed, branch protection verified, and explicit Project Lead GO. Only then create and sign the Beta tag.

## 8. Minimum Beta acceptance contract

The Beta is shippable only when all of these are true at the same candidate SHA:

- a clean user can install documented artifacts and run `vg` without the repository source tree;
- production mode cannot select scenario, feed, cassette or fallback implicitly;
- `vg run` reaches a durable RuntimeService and returns nonzero on no peer, early EOF, protocol error or missing terminal event;
- LAM, Ollama and OpenRouter use the same canonical ModelPort/Proposal path;
- every model-driven tool action crosses Kernel and the rootless worker;
- privileged patch bytes shown to the operator are exactly the bytes signed and applied;
- runtime possesses no operator private/symmetric signing authority;
- kill/restart resumes from ledger state without repeating a committed effect or model call;
- evaluator runs outside cognition/runtime identity, measures its inputs, and signs a persisted verdict;
- no fake evaluator or host-effect fallback can make a release test green;
- all-ref and clean-clone secret scans pass after coordinated remediation;
- full tests, package smoke tests and `--release` gates pass with non-vacuous command counts;
- three real Q2 runs pass with zero hand-patching and a positive reach-for-it-again answer;
- release receipts identify candidate SHA, artifact digests, commands, outputs, signer and independent countersigner.

## 9. Verification results from this audit

| Command | Result | Interpretation |
|---|---:|---|
| `python3 -m unittest discover -s test` | **438 passed, 2 skipped** | Passes when Unix sockets/Bubblewrap are allowed; sandboxed audit execution itself blocked those capabilities. A BrokenPipe traceback still leaks during one expected client-drop test. |
| Focused runtime/context/evaluator/provider/sandbox/env tests | **124 passed, 2 skipped** | Component changes are internally consistent. |
| `npm --workspace @vanguard/cli test` | **22/22 passed** | CLI application/feed/replay tests pass; no RuntimeService is exercised. |
| `python3 tools/002_LLM_API_MOCK/test_mock.py` | **PASS** | LAM catalog, multi-turn, tool-result counting and HTTP endpoints work with loopback permission. |
| LAR mock smoke call | **PASS** | Standalone router can select the mock catalog; this is not Vanguard integration. |
| `python3 tools/check_boundaries.py` | **PASS, 100 files** | Dependency lattice holds. |
| `python3 tools/check_tcb_budget.py` | **PASS, 1307 LOC** | Kernel remains below its 1438-line alarm. |
| Governance / v4 / broken harness | **PASS** | 8 governance artifacts, v4 link audit and 28 broken counterparts pass. |
| `check_active_mvp_contract.py` | **PASS, 0/49** | Closure-in-progress syntax/assignment check only. |
| `check_active_mvp_contract.py --release` | **FAIL, 49 open** | Correct release NO-GO. |
| `run_active_contract_tests.py` | **PASS, 0 commands** | Vacuous result; must be fixed before candidate use. |
| `check_baseline_manifest.py` | **FAIL** | Contract-checker digest drift. |
| `scan_secrets.py` | **PASS** | Current scanned tree is clean. |
| `scan_secrets.py --all-refs` | **FAIL** | Reachable `.env` history remains. |
| CLI pack dry run | **PASS** | npm tarball can be assembled; it has no usable backend. |
| CLI `run` with empty non-TTY stdin | **Incorrect exit 0** | Critical false-success path. |
| CLI `daemon status` without daemon | **Prints error, process exit 0** | Stable error-code requirement not met. |

## 10. SOTA and long-term company-value guidance

A billion-dollar valuation is not an engineering acceptance criterion and cannot be established by this repository audit. The credible path to exceptional value is to make the trust/evidence loop uniquely hard to fake and easy to extend.

The durable product moat should be:

1. **one governed execution protocol** across models, harnesses and task domains;
2. **an attributable evidence ledger** containing task state, decisions, effects, receipts, verdicts and corrections;
3. **exterior evaluation** that workers and model providers cannot manipulate;
4. **reproducible improvement experiments** where changes survive only when evidence shows a gain;
5. **a stable harness SDK** in which manifests/packs add tools, context and evaluation without forking the engine;
6. **operational trust**: isolation, recoverability, provenance, privacy, cost control and honest uncertainty.

Do not market the Beta as AGI, an AGI-like general solver, autonomous evolution, or a SOTA cognitive machine. Market exactly what is proven: a Linux Beta framework for building governed agentic harnesses, plus one coding harness, with descriptor-bound human approval, isolated execution, durable traceability and exterior evaluation. Generality and measurable competence accumulation become defensible only after Q3/Q4 evidence.

The project's strongest principle is already in its specification: the evidence corpus, not this generation of code, is the long-lived asset. Shipping a smaller truthful Beta protects that asset. Shipping a theatrical path poisons it.

## 11. Final decision

**Do not tag or distribute the current tree as an MVP Beta.**

Accept the supplied report's overall NO-GO, but amend it as follows:

- replace “four defects patched” with “four defects narrowed; closure unproved”;
- replace “no evaluator daemon” with “daemon prototype exists; no deployable/composed evaluator service”;
- add the provider-to-episode proposal mismatch as a P0 blocker;
- add the non-TTY CLI false-success behavior as a P0 blocker;
- add the vacuous zero-command contract-test PASS as a governance blocker;
- add incomplete images/entry points/license/release artifacts as distribution blockers;
- treat LAR/LAM as useful standalone test infrastructure that still requires ModelPort/RuntimeService integration.

The shortest honest route is the five-gate plan above: build one LAM-backed vertical path first, harden its trust boundaries, substitute Ollama/OpenRouter only at ModelPort, package it from a clean candidate, and then earn Q2 through three real runs.
