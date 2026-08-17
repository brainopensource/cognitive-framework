# Vanguard MVP Beta — Answer in 3 Blocks

## Block 1 — What to do in one phrase

Build and prove one installable, fail-closed path from `vg` through RuntimeService, canonical model adapters, Kernel, sandbox, external approval, durable recovery and exterior evaluation—first with LAM, then Ollama/OpenRouter—before dogfooding, packaging and signing the Beta.

## Block 2 — Ordered delivery table

| Order | Status | ID | Deliverable | Definition of done |
|---:|:---:|---|---|---|
| 0 | DONE | FOUNDATION | Domain contracts, Kernel S0–S12, ledger primitives, L1–L5 compiler, CLI application layer, Bubblewrap runner, evaluator probes, LAR and LAM foundations | Preserve these components; change their seams only where required by the tasks below. |
| 1 | DONE | TRUTH-GATE | Release contract is reopened and `--release` is red | `check_active_mvp_contract.py --release` fails while evidence is open; previous R0–R10 closure remains invalidated. |
| 2 | TODO | ADR-FREEZE | Freeze the Beta architecture and public protocols | Accepted decisions cover RuntimeService transport/auth, canonical model proposal, worker protocol, Ed25519 approval, lifecycle/recovery, evaluator IPC/signing and artifact distribution; Python/TypeScript golden vectors are committed. |
| 3 | TODO | GOV-CANDIDATE | Make candidate gates non-vacuous and SHA-bound | Open candidate rows execute their tests; zero executed commands cannot print PASS; receipts validate candidate SHA, artifact/output digests, signatures and independent countersignatures. |
| 4 | TODO | SECURITY-R0 | Close the credential incident safely | Provider credential is rotated first; authorized coordinated history cleanup removes the old `.env` object from every relevant ref; all-ref and clean-clone scans pass without exposing the value. |
| 5 | TODO | SERVICE | Implement the durable RuntimeService | Authenticated Unix service supports StartRun, GetRun, StreamEvents, ResolveApproval, RecordCorrection, Cancel, Checkpoint, Resume and ExplainArtifact; commands are idempotent; SQLite inbox/outbox/ledger survive restart; cursors reconnect without gaps or duplicates. |
| 6 | TODO | CLI-LIVE | Connect `vg` exclusively to the real service in production mode | No implicit stdin/scenario/feed fallback; no fabricated IDs or status; every command sets a stable process exit code; empty EOF/no peer/no terminal event is exit 2; replay/demo requires an explicit flag and is read-only/labelled. |
| 7 | TODO | MODEL-CONTRACT | Freeze and implement canonical model invocation/proposal translation | ContextCompiler produces the sole invocation shape; OpenAI/OpenRouter/Ollama replies strictly translate into `{kind, action, resource, args, reservation}`; malformed, ambiguous or unknown tool calls fail before Kernel construction. |
| 8 | TODO | LAM-VERTICAL | Run the first complete product slice through LAM | Installed `vg` reaches RuntimeService → context → LAM → typed proposal → Kernel → sandbox worker → approval suspension/resume → terminal event → evaluator; add a multi-turn `read → patch → test → finish` answer-bank scenario; no production fake fallback. |
| 9 | TODO | SANDBOX | Put every coding observation/effect behind one worker perimeter | Read, search, patch and test cross an authenticated typed worker protocol and Kernel; direct host effects are unreachable; Bubblewrap absence/probe failure blocks product composition; containment receipts are durable. |
| 10 | TODO | APPROVAL | Move signing authority outside the runtime | Operator CLI/key agent holds an Ed25519 private key; runtime holds only trusted public keys/key IDs; exact normalized bytes and complete descriptor context are signed; mutation, transplant, replay, expiry and revocation fail. |
| 11 | TODO | RECOVERY | Unify lifecycle and prove ledger-only recovery | Challenge is durable before suspension, decision before re-dispatch, intent before effect and receipt after effect; restart performs only the legal next transition; kill tests around every boundary prove no repeated committed effect or repeated model call. |
| 12 | TODO | EVALUATOR | Ship a real exterior evaluator service | Separate packaged/supervised process runs as UID 10002; authenticated IPC verifies peers and measured executable/image/config/oracle digests; terminal ledger events trigger it; signed verdicts return to the EvidencePlane; failures persist `inconclusive`. |
| 13 | TODO | PROVIDERS | Add honest LAM, Ollama and OpenRouter modes behind one ModelPort | Provider/source/endpoint/model/secret reference are explicit; no silent provider/model fallback; requested/resolved model, integer usage/cost, pricing provenance and genuine incremental TTFT are recorded; same acceptance suite runs against each mode. |
| 14 | TODO | PACKAGING | Build installable, version-locked release artifacts | Python wheel exposes runtime/evaluator executables; npm package exposes `vg`; worker/evaluator OCI images contain the software and use real immutable digests; add LICENSE, changelog, security policy, SBOM, checksums, signatures and compatibility manifest. |
| 15 | TODO | CLEAN-INSTALL | Prove installation and operation without the source tree | Clean supported Linux VM installs artifacts and passes daemon start/status/stop, run, approve, resume, trace, why, upgrade and rollback smoke tests without repository files, `.env` or pre-existing `node_modules`. |
| 16 | TODO | ADVERSARIAL | Complete security, protocol and crash verification | Golden contract tests, malformed frames, forged approvals, cursor gaps, duplicate commands, sandbox escapes, evaluator tampering, forced kills and no-fallback broken counterparts all fail for the intended reason. |
| 17 | TODO | DOCS | Reconcile documentation with the candidate | README, install, architecture, model, security and Beta-limit docs describe one real path; remove “production-grade” claims until proven; declare Linux-only Beta, one coding harness, human approval and Q3/Q4 deferral. |
| 18 | TODO | DOGFOOD-Q2 | Complete three honest real-bug dogfood runs | Three preregistered bugs in known repositories are fixed using only installed candidate artifacts, with zero human source edits; evidence records prompt, model, turns, costs, approvals, restart/evaluator facts and tests; operators answer “yes” to reach-for-it-again. |
| 19 | TODO | RELEASE-R10 | Freeze, independently audit and release the Beta | One clean candidate SHA passes full tests, packaging, security, baseline and `--release`; receipts are independently countersigned; hosted branch protection is verified; Project Lead authorizes GO; only then create and sign the Beta tag and publish artifacts. |

## Block 3 — References and developer implementation playbook

### Read first — applies to every TODO

1. [`docs/reviews/done/mvp_beta_delivery_audit_2026-08-16.md`](../../reviews/done/mvp_beta_delivery_audit_2026-08-16.md) — verified findings, missing product path, test evidence and release criteria.
2. [`docs/agile/sprint6B/backlog.md`](backlog.md) — ticket-level ownership, dependencies, acceptance evidence and R0–R10 gates.
3. [`docs/agile/sprint0/active-mvp-contract.json`](../sprint0/active-mvp-contract.json) — authoritative requirement-to-test map; do not mark a row covered before real evidence exists.
4. [`docs/agile/sprint0/system-architecture-icd.md`](../sprint0/system-architecture-icd.md) — package boundaries and authority ownership.
5. [`docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md`](../../main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md) — six-plane execution and recovery architecture.
6. [`docs/main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md`](../../main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md) — canonical wire and port rules.
7. [`docs/main_v4/05_vanguard_kernel_capabilities_and_security_v040.md`](../../main_v4/05_vanguard_kernel_capabilities_and_security_v040.md) — Kernel, capability, sandbox and approval invariants.
8. [`docs/main_v4/06_vanguard_competence_memory_and_evidence_v040.md`](../../main_v4/06_vanguard_competence_memory_and_evidence_v040.md) — evaluator and evidence-plane rules.
9. [`docs/main_v4/09_vanguard_decision_register_v040.md`](../../main_v4/09_vanguard_decision_register_v040.md) — accepted decisions, especially ADR-0057/0058 and the Beta Q1+Q2 scope.
10. [`docs/main_v4/13_C_gts_mvp_program_and_engineering_plan.md`](../../main_v4/13_C_gts_mvp_program_and_engineering_plan.md) — Chapter 10 Q1/Q2 acceptance questions; sequencing guidance, not a substitute for the contract.

### Universal implementation rules

- Preserve the dependency lattice: `domain ← ports ← kernel ← agency ← runtime → adapters`. Only runtime composes concrete adapters.
- Keep framework behavior generic. RuntimeService and EpisodeEngine own lifecycle, not coding verbs. `vg-code-default` owns coding prompts, tools and policies through its harness pack.
- Use ports and dependency injection. No CLI import of Python runtime internals, no agency import of adapters/evaluators, and no adapter-to-adapter dependency.
- Every external boundary uses a versioned schema, strict parser, explicit error type, bounded input/output, timeout, cancellation and correlation/idempotency ID.
- Fail closed. No missing daemon, sandbox, evaluator, signer, secret or provider may select a fake, host, default key or alternate model silently.
- Persist facts before acting: command → durable acceptance; challenge → suspension; decision → authorization; intent → effect; receipt → completion; terminal event → evaluation; verdict → evidence.
- Keep run termination separate from evaluation outcome. Instrument failure is never task failure, and uncertainty is `inconclusive`, never a fake PASS.
- Every control needs a passing reference and a deliberately broken counterpart that fails for the declared reason.
- Never close a contract row with prose alone. Evidence must point to a candidate SHA, exact command/output digests, artifacts, signer and independent reviewer.
- Never modify/rewrite credential history, remote refs, tags, branch protection or published artifacts without the repository owner's explicit authorization.

### TODO 2 — ADR-FREEZE

**Read:** Sprint 6B §§6–9; decision register ADR-0057/0058; ICD; wire schema; [`docs/development_guides/dev_prompts/dev-lane-a.md`](../../development_guides/dev_prompts/dev-lane-a.md).

**Developer instructions:** write small append-only decisions before implementation. Each decision must name owner, scope, wire version, trust assumption, failure behavior, compatibility/migration rule, reversal condition and required must-fail tests. Freeze JSON Schemas plus valid/invalid golden vectors and generate or mechanically validate Python/TypeScript readers. Ask the Tech Lead when a choice changes authority, durable schema, compatibility, security boundary or release scope.

### TODO 3 — GOV-CANDIDATE

**Read:** [`tools/check_active_mvp_contract.py`](../../../tools/check_active_mvp_contract.py), [`tools/run_active_contract_tests.py`](../../../tools/run_active_contract_tests.py), [`tools/check_receipt.py`](../../../tools/check_receipt.py), active contract, Sprint 6B `S6B-GOV-003` and `S6B-EVID-001`.

**Developer instructions:** add an explicit candidate mode that executes applicable open and covered rows. Treat zero commands as OPEN/SKIP or failure, never PASS. Make each requirement use an independently falsifiable command. Validate structured receipts against the candidate SHA and artifact/output hashes. Senior review is mandatory for receipt schema, signing rules and exceptions/justifications.

### TODO 4 — SECURITY-R0

**Read:** Sprint 6B `S6B-SEC-001..003`, [`tools/scan_secrets.py`](../../../tools/scan_secrets.py), [`.env.example`](../../../.env.example).

**Developer instructions:** a developer may improve scanners and secret injection tests, but must not print the key, purge history, delete refs, force-push or rotate provider credentials independently. Tech Lead/repository owner coordinates rotation and history rewrite. Acceptance requires current tree, all refs, built artifacts and a fresh remote clone to scan clean.

### TODOs 5–6 — SERVICE and CLI-LIVE

**Read:** Sprint 6B `S6B-SA-001..004`, `S6B-JR-001..006`; [`docs/development_guides/cli_tui_architecture.md`](../../development_guides/cli_tui_architecture.md); [`vanguard/clients/cli/src/contract/types.ts`](../../../vanguard/clients/cli/src/contract/types.ts); [`vanguard/clients/cli/src/adapters/live.ts`](../../../vanguard/clients/cli/src/adapters/live.ts); [`vanguard/clients/cli/src/application/commands.ts`](../../../vanguard/clients/cli/src/application/commands.ts).

**Developer instructions:** use command inbox + event outbox + projections, not request-thread-owned state. Commands carry version, command ID, actor, run ID and idempotency key. Events carry stream sequence and causal links. The TypeScript client sends commands and consumes frames; it does not implement lifecycle decisions. Keep scenario/replay as explicit adapters. Test reconnect, duplicate command, cursor gap, early EOF, malformed frame, daemon death, bounded buffering and shutdown. Senior owns schema/auth/recovery; a junior can implement the client against frozen golden vectors.

### TODO 7 — MODEL-CONTRACT

**Read:** [`vanguard/packages/ports/model.py`](../../../vanguard/packages/ports/model.py), [`vanguard/packages/agency/episode/state.py`](../../../vanguard/packages/agency/episode/state.py), [`vanguard/packages/adapters/models/openrouter.py`](../../../vanguard/packages/adapters/models/openrouter.py), Sprint 6B `S6B-MD-001..004`.

**Developer instructions:** do not let provider JSON flow directly into Kernel types. Add a strict anti-corruption layer: provider response → validated provider-neutral call → manifest tool lookup → canonical proposal. The manifest supplies allowed action and resource policy; the model supplies arguments, never authority. Reject malformed JSON instead of preserving `raw`, and reject ambiguous multiple calls for the Beta's one-effect-per-turn rule. Add fixtures for text finish, valid call, unknown call, invalid args, multiple calls, truncated SSE and tool result on Turn 2. Senior approves the canonical schema and authority mapping.

### TODO 8 — LAM-VERTICAL

**Read:** [`tools/002_LLM_API_MOCK/README.md`](../../../tools/002_LLM_API_MOCK/README.md), [`tools/002_LLM_API_MOCK/mock_server.py`](../../../tools/002_LLM_API_MOCK/mock_server.py), [`tools/001_LLM_API_ROUTER/README.md`](../../../tools/001_LLM_API_ROUTER/README.md), [`vanguard/packages/agency/manifests/vg-code-default/manifest.json`](../../../vanguard/packages/agency/manifests/vg-code-default/manifest.json).

**Developer instructions:** LAM is an external ModelPort test endpoint, not the runtime. Add a deterministic tool-call scenario whose next reply depends on received tool observations. Start it in an integration-test fixture, configure the model adapter explicitly, and invoke only the installed CLI/public service. LAR remains a developer diagnostic; never spawn it as the production model adapter. The same test must fail when ContextCompiler observations, Kernel dispatch or worker transport are bypassed.

### TODO 9 — SANDBOX

**Read:** [`vanguard/packages/ports/sandbox.py`](../../../vanguard/packages/ports/sandbox.py), [`vanguard/packages/adapters/sandbox/rootless.py`](../../../vanguard/packages/adapters/sandbox/rootless.py), [`vanguard/packages/adapters/environment/git.py`](../../../vanguard/packages/adapters/environment/git.py), Sprint 6B `S6B-MD-005/006`, VG-05 sandbox rules.

**Developer instructions:** create one typed worker request/receipt protocol for read/search/patch/test. Runtime never calls host Git/filesystem/subprocess for model-driven work. Validate workspace and paths before starting the worker and again inside it. Use argv arrays, sanitized environment, fixed PATH, namespace/network denial, resource/output limits and process-group cancellation. Persist probe-derived containment, not command-line claims. Senior/security review is required for mounts, namespace policy, degradation behavior and receipt signing.

### TODOs 10–11 — APPROVAL and RECOVERY

**Read:** [`vanguard/packages/runtime/governance/approvals.py`](../../../vanguard/packages/runtime/governance/approvals.py), [`vanguard/packages/runtime/governance/engine.py`](../../../vanguard/packages/runtime/governance/engine.py), [`vanguard/packages/runtime/ledger/recovery.py`](../../../vanguard/packages/runtime/ledger/recovery.py), Sprint 6B `S6B-SA-004..007`, VG-05 K-13..K-16.

**Developer instructions:** split signer and verifier interfaces. Sign canonical bytes containing schema/key ID, approval/challenge IDs, actor/reviewer, run/process, exact action/resource/args/normalized diff digests, policy, reservation, challenge event, decision, expiry and nonce. Runtime stores public keys and revocation state only. Build a single event-sourced lifecycle reducer and make restart rehydrate it from ledger events. Use idempotency keys and reconciliation for uncertain effects. Senior/security owns cryptographic selection, key storage, revocation and exactly-once semantics.

### TODO 12 — EVALUATOR

**Read:** [`vanguard/packages/ports/evaluator.py`](../../../vanguard/packages/ports/evaluator.py), [`vanguard/packages/adapters/evaluators/isolated.py`](../../../vanguard/packages/adapters/evaluators/isolated.py), [`vanguard/packages/adapters/evaluators/client.py`](../../../vanguard/packages/adapters/evaluators/client.py), [`vanguard/packages/adapters/evaluators/daemon.py`](../../../vanguard/packages/adapters/evaluators/daemon.py), [`containers/evaluator.Dockerfile`](../../../containers/evaluator.Dockerfile), Sprint 6B `S6B-MD-007/008`.

**Developer instructions:** add a real executable entry point and supervisor. Bind socket permissions narrowly, verify peer credentials in both directions, use nonces/request IDs and bounded framed messages, and sign responses. Measure rather than echo identity/image/config/oracle digests. Trigger evaluation from a persisted terminal event, not an in-memory runtime callback. Seal oracle inputs outside the worker. Return typed `inconclusive` for wrong UID/image/nonce, timeout, truncation, crash or probe failure. Senior/security must approve the trust and attestation model.

### TODO 13 — PROVIDERS

**Read:** model port/OpenRouter files above; [`tools/001_LLM_API_ROUTER/providers/ollama.py`](../../../tools/001_LLM_API_ROUTER/providers/ollama.py); [`vanguard/packages/adapters/models/routing.py`](../../../vanguard/packages/adapters/models/routing.py); Sprint 6B `S6B-MD-002..004/009`.

**Developer instructions:** implement separate adapters behind the same port, or a carefully named OpenAI-compatible transport plus an Ollama adapter. Provider choice is configuration, never fallback logic. Isolate credentials to the provider process; do not put them in context, ledger, worker/evaluator env or CLI frames. Record source mode at construction. Unknown price means `pricing_known=false`, not a paid/free guess. Integration tests use LAM; live tests require protected credentials and explicit opt-in.

### TODOs 14–15 — PACKAGING and CLEAN-INSTALL

**Read:** [`pyproject.toml`](../../../pyproject.toml), [`vanguard/clients/cli/package.json`](../../../vanguard/clients/cli/package.json), [`containers/worker.Dockerfile`](../../../containers/worker.Dockerfile), evaluator Dockerfile, [`containers/manifest.json`](../../../containers/manifest.json), [`.github/workflows/clean-candidate.yml`](../../../.github/workflows/clean-candidate.yml), Sprint 6B release tickets.

**Developer instructions:** build artifacts in a clean, pinned environment. Dockerfiles must install/copy the exact wheel and use non-root users; manifest digests come from built images, never placeholders. Test package contents and executable entry points with the source tree absent. Version CLI/runtime/protocol/images together through a compatibility manifest. Generate SBOM, provenance, checksums and signatures. Release engineering or Tech Lead approves signing/publishing credentials; ordinary development uses dry-run/local registries only.

### TODO 16 — ADVERSARIAL

**Read:** [`test/broken/manifest.json`](../../../test/broken/manifest.json), [`tools/run_broken_tests.py`](../../../tools/run_broken_tests.py), [`test/trust/test_spine.py`](../../../test/trust/test_spine.py), security tests, Sprint 6B `S6B-QA-001..003`.

**Developer instructions:** test through public protocols, not private method assertions alone. For every control, make the reference pass and a deliberately defective implementation fail specifically because of that control. Cover service restart, duplicate/gap handling, signature attacks, path/symlink escape, secret leakage, network access, evaluator mutation, source-label lies and every forbidden fallback. QA owns fixtures; control authors must not self-countersign their gate.

### TODO 17 — DOCS

**Read:** root [`README.md`](../../../README.md), [`vanguard/clients/cli/README.md`](../../../vanguard/clients/cli/README.md), [`vanguard/packages/README.md`](../../../vanguard/packages/README.md), active contract and final audit.

**Developer instructions:** document commands only after running them from installed artifacts. Keep one status statement and link detailed limitations from it. Use current `docs/main_v4`, `docs/agile`, `docs/reviews` and `docs/development_guides` paths. Never call static model availability/pricing “verified” without dated evidence. Product/Tech Lead approves SOTA, security, reliability, AGI/general-purpose and production-readiness claims.

### TODOs 18–19 — DOGFOOD-Q2 and RELEASE-R10

**Read:** GTS-13C Chapter 10, ADR-0057, Sprint 6B §§11–13, [`docs/agile/sprint6/evidence/R9/receipt.md`](../sprint6/evidence/R9/receipt.md) as historical/non-release evidence, and the acceptance contract in the final audit.

**Developer instructions:** preregister tasks, clean commits, prompts, budgets, hidden oracles and exclusion rules before running. Use installed artifacts and the sole public path. Humans may prompt, approve/reject and record corrections; they may not edit source. Freeze one candidate before evidence collection. A reviewer who did not author the control validates receipts. Project Lead alone decides GO/NO-GO; publishing, tag signing, branch protection and remote changes require explicit authority.

### Required commands before asking for Beta approval

```bash
python3 -m unittest discover -s test
npm --workspace @vanguard/cli run typecheck
npm --workspace @vanguard/cli test
python3 tools/002_LLM_API_MOCK/test_mock.py
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/check_sprint0_governance.py
python3 tools/check_schema_archaeology.py
python3 tools/audit_v4.py
python3 tools/run_broken_tests.py
python3 tools/scan_secrets.py --all-refs
python3 tools/check_baseline_manifest.py --release
python3 tools/run_active_contract_tests.py
python3 tools/check_active_mvp_contract.py --release
```

Run packaging, clean-install, RuntimeService/LAM, sandbox, approval/restart, evaluator and three live dogfood gates in addition to this list. A command that skips mandatory behavior or executes zero applicable tests is not green evidence.
