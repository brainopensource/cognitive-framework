# Sprint 6B — Backend Closure and MVP Beta Release Backlog

**Status:** `PROPOSED / RELEASE NO-GO`

**Recommended timebox:** 14 working days with four contributors; approximately 15–18 working days with three

**Branch:** `sprint6B/integration`

**Outcome:** one installable Vanguard framework, one packaged `vg-code-default` coding harness, and one trustworthy headless product path ready for an explicitly authorized Beta release

**Primary surface:** backend and headless CLI; TUI is deliberately minimal

## 1. Authority and planning basis

This backlog closes the open Beta work identified by:

1. [`docs/main_v4/00_vanguard_registry_v040.md`](../../main_v4/00_vanguard_registry_v040.md) — authority and precedence;
2. [`docs/main_v4/01_vanguard_engineering_handbook_v040.md`](../../main_v4/01_vanguard_engineering_handbook_v040.md) — change, testing and must-fail discipline;
3. [`docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md`](../../main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md) — daemon, planes, context and recovery;
4. [`docs/main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md`](../../main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md) — wire, event and port contracts;
5. [`docs/main_v4/05_vanguard_kernel_capabilities_and_security_v040.md`](../../main_v4/05_vanguard_kernel_capabilities_and_security_v040.md) — S0–S12, sandbox, approval and TCB requirements;
6. [`docs/main_v4/06_vanguard_competence_memory_and_evidence_v040.md`](../../main_v4/06_vanguard_competence_memory_and_evidence_v040.md) — exterior evaluation and double probes;
7. [`docs/main_v4/13_C_gts_mvp_program_and_engineering_plan.md`](../../main_v4/13_C_gts_mvp_program_and_engineering_plan.md) — MVP gate and programme sequencing;
8. [`docs/reviews/done/phases_0-2_review_full_rev2.md`](../../reviews/done/phases_0-2_review_full_rev2.md) — mandatory closure design and R0–R10;
9. [`docs/reviews/done/phases_0-2_review_full_rev3.md`](../../reviews/done/phases_0-2_review_full_rev3.md) — final-gate implementation findings.

Where this backlog conflicts with an approved v4 rule, the v4 owner wins until the Tech Lead and Project Lead append an explicit decision. This backlog does not silently amend normative contracts.

## 2. Sprint goal and scope fence

Sprint 6B closes Beta questions Q1 and Q2:

- **Q1 — boundary:** model-driven effects are mediated, contained, externally approved where privileged, durably recoverable, and evaluated by an exterior authority;
- **Q2 — utility:** an operator can install Vanguard and use `vg-code-default` from a real headless CLI to complete small coding tasks with no hand-edited source.

The one required product path is:

```text
vg headless CLI
  → authenticated RuntimeService
  → ContextCompiler / canonical ModelInvocation
  → incremental OpenRouter ModelPort
  → Kernel S0–S12
  → rootless worker / sandboxed environment
  → externally signed approval for privileged diffs
  → ledger-only restart and exactly-once resume
  → terminal ledger event
  → exterior evaluator service
  → signed verdict in ledger
  → CLI terminal event and exit code
```

### In scope

- Sprint 0–1 governance and schema residuals required for an honest Beta;
- open backend findings from Sprints 3–6;
- Linux rootless deployment baseline;
- real `openrouter/free` and `deepseek/deepseek-v4-flash` release tests;
- headless coding commands, external approval/resume, trace and stable JSONL output;
- minimal TUI over the same live client and application layer;
- framework, CLI, evaluator/worker, schemas and `vg-code-default` distributable artifacts;
- clean-clone, install, deploy, upgrade, rollback and release-candidate evidence.

### Explicitly deferred after Beta

- rich TUI/inspector, visual graphs, themes and frontend polish;
- Q3 statistical programme: A/A floors, paired trials, confidence intervals and performance claims;
- Q4 non-coding generality experiment;
- browser/API/web clients, remote multi-tenant control plane and autonomous evolution;
- microVM/gVisor; rootless Bubblewrap or rootless OCI is the Beta baseline.

Deferral does not permit false claims. Telemetry provenance, real-vs-synthetic labelling, integer units and failure accounting remain Beta requirements.

## 3. Current entry state — facts to preserve

| Finding | Current state | Consequence |
|---|---|---|
| Documentation move | `docs/v4`, `docs/sprint*`, `docs/review` and `docs/development` were moved, but tools and CI still hard-code old paths | Governance, contract, baseline and v4 audit commands currently fail before testing product code |
| Contract closure | Phase 2 rows are marked covered although the live path is absent; receipts are prose-only | R10 must be invalidated and affected rows reopened before implementation |
| Runtime/client | No durable `RuntimeService`; HEAD had unavailable/scenario behavior, while the current uncommitted CLI bridge spawns inline Python directly, uses in-memory SQLite and self-approval placeholders | The bridge is not the approved daemon boundary and must be replaced, not certified as the product path |
| Provider/episode | OpenRouter produces `text/toolCalls`, while the episode consumes typed `kind/action/resource/args` proposals | A real model response cannot drive the current coding loop safely |
| Effects | `Runtime.execute_harness()` binds directly to `GitEnvironment` | Reads, patches and commands bypass the rootless runner |
| Approval/recovery | Runtime constructs the HMAC authority, uses a default key, and resumes in memory with a replacement reservation | Approval authority is not external and restart is not ledger-only |
| Evaluator | Evaluator implementation is directly injected; current dogfood accepts the caller UID and a fabricated image digest | Exteriority and attestation are not established |
| Dogfood | Fixed source/diff is embedded, model is scripted, SQLite is in memory, CLI is bypassed | Existing R9 evidence is a wiring demonstration, not dogfood |
| Telemetry | Synthetic sandbox constants can enter a collector defaulted to `live`; durations and USD remain floats | R8 is not closed |
| Secret incident | Root `.env` is ignored and untracked, but the old blob remains reachable under `refs/original`; no blocking scanner exists | R0 is open; history cleanup needs coordinated approval |
| Sprint 1 | GAP-010..014, two human timing samples, schema-lock decision and hosted branch protection remain open | Durable Beta schema authority is unsettled |
| Distribution | No Python package, CLI package is private, no evaluator/worker image, install/deploy smoke or release workflow | Framework and example cannot yet be distributed |

## 4. Team and ownership model

Four contributors are strongly recommended. The fourth lane supplies independent verification and release evidence; an implementer may not countersign their own control.

| Lane | Owner | Exclusive write ownership during parallel waves | Review requirement |
|---|---|---|---|
| A — Runtime, control and integration | Senior Developer / Tech Lead | `schemas/v4` public Sprint 6B additions; `vanguard/packages/runtime/service/**`; governance/recovery integration; `runtime/root.py` | Project Lead plus another developer for security-sensitive code |
| B — Workload, evidence and model adapters | Developer | sandbox, evaluator and OpenRouter/context adapter files; no edits to `runtime/root.py` | Senior reviews sandbox, evaluator, streaming and secret handling |
| C — Client and developer experience | Junior Developer | `vanguard/clients/cli/**`; client contract tests; minimal TUI; no backend imports | Developer reviews TypeScript; Senior reviews signing UX and protocol parsing |
| D — Verification, docs and release | Optional Docs/QA/Release Developer | tools, CI, broken fixtures, link repair, evidence tooling, release metadata and receipts; no production control implementation | May countersign only gates for controls they did not author |
| Accountable | Project Lead | scope, hosted controls, R9/R10 and release authorization | Sole GO/NO-GO authority; publishing remains a separate explicit action |

If only three contributors are available, Lane D is split between the Project Lead and the three lanes, the sprint expands to roughly three weeks, and an external reviewer still countersigns R3–R10. Independence is not traded for calendar time.

### Shared-file rule

- Lane A owns public protocol/schema changes and freezes them by the end of Wave 0.
- Lane B implements behind frozen ports and never edits the client.
- Lane C develops against generated/golden protocol fixtures and never imports runtime internals.
- Lane D owns acceptance fixtures and gate tooling, but does not rewrite a production control to make a gate pass.
- Only Lane A edits `runtime/root.py` during integration.
- Any shared-interface change requires Tech Lead approval, a compatibility note and coordinated version bump.

## 5. Dependency and delivery waves

| Wave | Target | Parallel activity | Exit condition |
|---|---|---|---|
| 0 — Restore truth and freeze seams | Days 1–2 | Paths, security containment, scope ruling, contract reopening, ADRs, schemas and golden protocol fixtures | Current gates execute again; false closure is invalidated; interfaces are frozen |
| 1 — Backend implementation | Days 3–6 | Lane A runtime/governance; Lane B trusted adapters/model; Lane C live CLI against fake server; Lane D tests/CI | Each lane passes unit, contract and must-fail tests without touching another lane's implementation |
| 2 — Contract integration | Days 7–8 | Merge service, adapters and client in dependency order | Live CLI starts a cassette-backed sandboxed run through RuntimeService |
| 3 — Trust-path hardening | Days 9–10 | Approval/restart matrix, evaluator, no-fallback and secret-isolation tests | R2–R6 candidate controls pass adversarially |
| 4 — Live validation | Days 11–12 | OpenRouter canaries, small coding tasks, packaging/install/deploy smoke | R7–R8 and artifact installation pass with sanitized evidence |
| 5 — Dogfood and release candidate | Days 13–14 | Three preregistered runs, clean clone, sealed receipts and dry-run release | R0–R10 pass at one candidate SHA; independent GO receipt exists |

Critical path:

```text
path/security repair
  → scope + interface freeze
  → RuntimeService + trusted adapters
  → live CLI integration
  → kill/restart and exterior evaluation
  → live model matrix
  → dogfood ×3
  → package/install/deploy dry run
  → R10 reseal
```

## 6. Leadership, governance and Sprint 1 closure backlog

All rows start `TODO`. No status becomes `DONE` without its named evidence.

| Ticket | Pri | Owner | Work | Depends | Acceptance / evidence |
|---|---:|---|---|---|---|
| `S6B-PL-001` | P0 | Tech Lead + Project Lead | Accept the Sprint 6B scope fence. Classify each of the 133 current CI-9 gaps as Beta-applicable or explicitly deferred; decide whether Beta locks only durable used schemas or all 15 currently planned SC-12 artifacts | — | Append-only decision; zero unclassified rules; Beta-applicable gaps block CI. If all 133 gaps and all 15 artifacts are ruled mandatory, re-estimate as a multi-sprint programme before coding |
| `S6B-GOV-001` | P0 | Lane D | Establish one canonical repository path map and update CI, tools, manifests, README links and evidence references for `docs/main_v4`, `docs/agile`, `docs/reviews` and `docs/development_guides` | — | Governance, contract, baseline, audit, CV, rule-map, boundary and TCB tools run from repo root and foreign cwd; stale-path broken fixture fails |
| `S6B-GOV-002` | P0 | Tech Lead + Project Lead | Invalidate the present R0–R10 PASS claims, mark old receipts historical, set Phase 2 to closure-in-progress, commit rev3, and reopen every semantically unproven row | GOV-001 | Contract deliberately fails on the open Beta rows; no active document says closed/production-ready |
| `S6B-SEC-001` | P0 | Tech Lead / Security | Confirm revocation, purge the old `.env` object from all branch/tag/remote-tracking/original refs, remove `refs/original`, coordinate affected remote rewrite and require stale clones to re-clone | — | All-ref/object scan and clean-clone scan negative; redacted receipt countersigned; secret value never printed. This coordinated destructive operation requires explicit execution approval |
| `S6B-SEC-002` | P0 | Lane D + Senior review | Add blocking secret scans for diff, tree, reachable history and built artifacts; add safe `.env.example`, dependency/SAST/license checks and fake-secret broken fixtures | SEC-001 | CI blocks injected fake secret and disallowed dependency; live credentials are unavailable to PR jobs |
| `S6B-SEC-003` | P0 | Lane B + Senior review | Implement a local live-test launcher that strictly parses and allowlists only `OPENROUTER_API_KEY` from root `.env`; require ignored/untracked status and restrictive permissions; inject only into the model adapter process | SEC-002, ARC-001 | Runtime stores only the key reference; object graph, context, ledger, CLI frames, sandbox/evaluator env, logs, cassettes, telemetry and artifacts contain no key; tracked, malformed or permissive `.env` fails |
| `S6B-S1-001` | P0 | Lane D + independent reviewer | Close GAP-010..014 with self-contained, content-addressed reconstruction bundles for all four traces | GOV-001, EVID-001 | Independent reviewer reconstructs all traces without interview or repository context and signs raw-output receipts |
| `S6B-S1-002` | P0 | Project Lead | Run two prospective human reproduction/timing samples with declared pause rules and provenance | S1-001 | Two independently signed active-time and elapsed-time receipts; no retrospective estimates |
| `S6B-S1-003` | P0 | Senior + Project Lead | Lock the durable Beta schema set or implement the additional SC-12 artifacts required by PL-001; publish schema digest and migration rule | PL-001, S1-001, S1-002 | No durable Beta ledger/evidence uses DRAFT; Python/TypeScript round trips and migration rehearsal pass; independent sign-off |
| `S6B-ARC-001` | P0 | Senior / Tech Lead | Freeze focused decisions for runtime transport/authentication, approval algorithm/key/revocation, canonical diff, sandbox backend/degraded policy, evaluator supervisor/IPC, event sequence/idempotency, unified state machine, wire compatibility, telemetry/pricing provenance, dogfood evidence and distribution | PL-001 | Each decision names authority owner, failure semantics, compatibility and must-fail tests; public interfaces frozen by end of Wave 0 |
| `S6B-GOV-003` | P0 | Lane D + Senior review | Repair Active MVP Contract semantics: stable component registry; fix `adapters/model(s)` drift; add/settle `REQ-BENCH-001`; add live runtime, release and packaging rows; ensure each row has an independent falsifiable command | GOV-002, ARC-001 | Checker rejects component drift, duplicate/broad commands and covered rows without structured evidence |
| `S6B-EVID-001` | P0 | Lane D + Project Lead | Define machine-verifiable JSON receipt schema and subject/evidence commit protocol | ARC-001, GOV-003 | Receipt includes subject SHA, allowed evidence commit, commands, exit codes, output/artifact digests, environment/tool versions, gate/result, signer, countersigner and timestamps; mutation, `pending`, stale SHA and self-signoff fail |
| `S6B-GOV-004` | P0 | Project Lead | Enable hosted controls: PR-only protected `main`, required checks, stale-review dismissal, resolved conversations, no force-push/deletion, restricted release environment and secret access | GOV-005 | Host/API export proves controls; branch protection changes from unverified to verified; tag is withheld until R10 |
| `S6B-GOV-005` | P0 | Lane D | Add clean-candidate CI from a fresh checkout with locked Python/Node installation, imports, tests, typecheck/build, all gates, generated-file drift and clean final status | GOV-001, GOV-003 | Required workflow passes at exact SHA without pre-existing `node_modules`, `.env`, untracked source or mandatory release skips |

## 7. Lane A — Senior runtime, control and integration backlog

| Ticket | Pri | Work | Depends | Acceptance / evidence |
|---|---:|---|---|---|
| `S6B-SA-001` | P0 | Define the versioned RuntimeService command/event schema: `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `RecordCorrection`, `Cancel`, `Checkpoint`, `Resume`, `ExplainArtifact`; command IDs, cursors, authentication, backpressure and errors | ARC-001, S1-003 | Python and TypeScript golden round trips; invalid fields, duplicate command, cursor gap and unsupported version fail before domain construction |
| `S6B-SA-002` | P0 | Implement a durable local RuntimeService daemon with SQLite command inbox, event outbox, projections and bounded authenticated local transport | SA-001 | Commands are idempotent; restart preserves runs; stream reconnect resumes from cursor; no scenario/fake fallback in production mode |
| `S6B-SA-003` | P0 | Create one authoritative event factory with secure monotonic UUIDv7, durable per-stream sequence allocation, causal parent links and canonical serialization | SA-001 | Frozen-clock bursts are unique and lexically ordered in Python/TypeScript; concurrent/restarted writers never reuse sequence numbers |
| `S6B-SA-004` | P0 | Unify `ProcessEngine` and approval lifecycle into one event-sourced state machine | SA-002 | Illegal transitions fail; challenge persists before suspension; decision persists before execution; terminal transitions are unique |
| `S6B-SA-005` | P0 | Replace runtime-held/default HMAC signing with external asymmetric operator signing and runtime public-key verification | SA-001, SA-004 | Signature binds schema, approval/nonce, tenant, owner, run, process, reviewer, action/resource, args/descriptor, policy, reservation, challenge event and expiry; mutation/transplant/replay/expiry/revocation fail |
| `S6B-SA-006` | P0 | Implement ledger-only recovery, idempotent effect reconciliation and original-reservation preservation | SA-004, SA-005 | Kill before/after challenge, decision, grant, intent, effect and receipt; restart performs the only legal next action exactly once and makes no repeat model call for approved work |
| `S6B-SA-007` | P0 | Add durable kill switch and capability revocation across active, suspended and resumed runs | SA-002, SA-006 | Revocation during active work or suspended approval prevents the next effect, emits `CapabilityRevoked` and terminates reconstructably |
| `S6B-SA-008` | P0 | Replace hard-coded composition with frozen registries; wire canonical context/model, sandbox worker, external approval verifier, ledger recovery and evaluator client into the sole root | Lane B ports, SA-002..007 | Production path contains no direct Git effect, runtime signer, direct evaluator import, in-memory default store or scenario fallback; unknown capability fails at composition |
| `S6B-SA-009` | P1 | Lead serialized integration, TCB review and candidate freeze | All production lanes | Boundary/TCB checks pass; no second execution/evaluation path exists; candidate SHA is frozen before live evidence |

## 8. Lane B — Developer workload, evidence and model backlog

| Ticket | Pri | Work | Depends | Acceptance / evidence |
|---|---:|---|---|---|
| `S6B-MD-001` | P0 | Define canonical `ModelInvocation` and translate provider tool calls into typed episode proposals; runtime supplies authoritative resource, scope and reservation | ARC-001, S1-003 | Every production call originates at ContextCompiler; real `read/search/patch/test` calls parse; malformed, ambiguous or unknown calls cannot become effects |
| `S6B-MD-002` | P0 | Implement genuinely incremental OpenRouter HTTP/SSE transport, cancellation and bounded retry | MD-001 | TTFT timestamps first validated content or tool-call delta before response completion; fragmented calls assemble; malformed JSON/arguments, truncation and cancellation fail closed |
| `S6B-MD-003` | P0 | Complete context invariants: stable L1–L3, immutable task brief, provenance-bearing L5 observations, confidentiality filtering and conservative tokenizer/version metadata | MD-001 | Turn 2 demonstrably receives actual tool output; bypass and dropped-observation broken counterparts fail through production composition |
| `S6B-MD-004` | P1 | Add explicit model routing/preflight for `openrouter/free` and `deepseek/deepseek-v4-flash`; record requested and provider-resolved identity, capabilities, pricing source and as-of version | MD-002, SEC-003 | Missing/unavailable model is an instrument error with no automatic fallback; unknown pricing remains `pricing_known=false`; free pricing is zero, never a paid default |
| `S6B-MD-005` | P0 | Implement sandbox worker protocol and sandbox-backed environment adapter for `fs.read`, `fs.search`, `patch.apply` and `proc.test` | ARC-001 | Every product observation/effect crosses the worker protocol and Kernel; direct host Git/subprocess execution is unreachable |
| `S6B-MD-006` | P0 | Complete rootless sandbox enforcement: isolated user/mount/PID/IPC/network namespaces, sanitized env/PATH, allowlisted mounts, resource/output limits, process-group cancellation and signed receipt | MD-005 | Home, root `.env`, evaluator bundle, sockets, unsafe symlinks and network are denied; unavailable isolation fails closed; no silent host fallback |
| `S6B-MD-007` | P0 | Build separately packaged evaluator daemon/supervisor/client with authenticated IPC, observed peer UID, executable/image digest and evaluator signing authority | ARC-001 | Wrong peer, UID, image, nonce, protocol, timeout, truncation or crash yields signed `inconclusive`; runtime cannot import evaluator implementation |
| `S6B-MD-008` | P0 | Trigger evaluation only from persisted terminal evidence; seal oracle independently; verify complete evaluation closure and persist signed verdict as EvidencePlane | MD-007, SA-002 | Non-terminal run cannot receive verdict; modified/added/removed/symlinked oracle, hooks, `.pth`, path shadowing, unsafe env or untracked executable input fails closed |
| `S6B-MD-009` | P0 | Make telemetry provenance structural and units exact at real lifecycle boundaries | MD-002, MD-006, MD-008 | `live/cassette/synthetic` cannot be caller-lied; time/currency are integers; instrument tuple and errors are present; synthetic-to-live fixture fails; Q3 statistics remain deferred |

## 9. Lane C — Junior client and minimal TUI backlog

| Ticket | Pri | Work | Depends | Acceptance / evidence |
|---|---:|---|---|---|
| `S6B-JR-001` | P0 | Generate or mechanically conform TypeScript RuntimeService types/parser to frozen schema | SA-001 | Bidirectional golden vectors pass; UUID, sequence, scope, required field and extension-policy violations reject before casts |
| `S6B-JR-002` | P0 | Connect `LiveRuntimeClient` to authenticated RuntimeService transport | JR-001 | Start/get/stream/cancel/checkpoint/resume/approve/correct/explain work; reconnect, dedupe, gap detection, bounded buffering and shutdown tests pass |
| `S6B-JR-003` | P0 | Deliver the primary headless coding command and stable exit codes | JR-002 | `vg run <repo> --headless --prompt "..." --model <id> --manifest vg-code-default` starts a real run; stdout is JSONL only, diagnostics go to stderr, terminal status controls exit code |
| `S6B-JR-004` | P0 | Implement external operator key handling and headless approval flow | JR-002, SA-005 | `vg approve <run-id>` renders exact normalized bytes, signs outside runtime and submits; non-TTY mode never auto-approves; reject and expired decisions fail safely |
| `S6B-JR-005` | P1 | Persist correction records with the actual accepted patch digest | JR-002 | Correction survives daemon restart and appears in replay; replay mode is read-only and never pretends to persist |
| `S6B-JR-006` | P1 | Reduce TUI to the live minimum and reuse the headless application layer | JR-002..005 | TUI shows connection/run status, bounded event timeline, exact diff, approve/reject, one correction reason, cancel and terminal result; no scenario default or duplicated business logic |
| `S6B-JR-007` | P1 | Make CLI package installable and publishable in dry-run form | REL-001, JR-003 | Correct `bin` path, `files`, engines, exports, license/repository metadata; `npm pack` artifact runs with source tree absent |

### Required Beta command surface

```text
vg daemon start|status|stop
vg run <repo> --headless --prompt <text> --model <model-id> --manifest vg-code-default
vg approve <run-id> --decision approve|reject
vg resume <run-id> --headless
vg trace <run-id> --headless
vg why <artifact-id> --headless
```

The default production command never selects a scenario client. Demo/replay modes must be explicit and visibly labelled.

## 10. Lane D — verification, documentation and evidence backlog

| Ticket | Pri | Work | Depends | Acceptance / evidence |
|---|---:|---|---|---|
| `S6B-QA-001` | P0 | Replace self-asserting broken fixtures with defective production implementations or dependency-injected defects | Interface freeze | Every new gate has a registered counterpart; reference passes, defect fails for the intended control, and removing the production control makes the reference test fail |
| `S6B-QA-002` | P0 | Build live CLI/service/sandbox/evaluator acceptance harness and forced-kill matrix | SA-001, ARC-001 | Tests operate only through public wire contracts and can run against fake/cassette or protected live adapters with truthful labels |
| `S6B-QA-003` | P0 | Strengthen contract and receipt validators | GOV-003, EVID-001 | Missing/nonexistent evidence, wrong SHA/gate/result, output digest mismatch, unsigned/self-signed receipt, stale path and premature coverage all fail |
| `S6B-QA-004` | P1 | Add local-link, packaged-resource and documentation command verification | GOV-001 | Zero broken local links or stale old-directory references; documented commands run verbatim from installed artifacts |
| `S6B-QA-005` | P1 | Preregister small live canary and dogfood tasks, prompts, budgets, hidden oracles, clean starting commits and exclusion rules | MD-004, EVID-001 | Model never receives fixed source/diff; pre-state fails; task size is one or two files; zero human source edits allowed |
| `S6B-QA-006` | P1 | Collect R0–R10 raw outputs and sanitized artifacts at the frozen candidate SHA | Candidate freeze | Each receipt validates and is countersigned by someone other than the control author; old Sprint 6 receipts remain historical/invalidated |
| `S6B-QA-007` | P1 | Reconcile README, architecture, install, `.env`, model, headless, TUI and Beta-limit documentation | Stable implementation | No claim exceeds its signed gate; paths use current layout; frontend and Q3/Q4 deferrals are explicit |
| `S6B-QA-008` | P1 | Prepare tracker/RACI import and daily integration board from this backlog | Backlog accepted | Every ticket has one owner, reviewer, dependency, estimate and evidence path; WIP limit is one integration-sensitive item per lane |

## 11. OpenRouter live-test policy

Official model references verified for this planning baseline:

- [`openrouter/free`](https://openrouter.ai/docs/guides/routing/routers/free-router) is a router that selects from currently available free models. Availability, selected model and rate limits vary, so it is suitable for wire canaries and very small tasks, not deterministic quality claims.
- [`deepseek/deepseek-v4-flash`](https://openrouter.ai/deepseek/deepseek-v4-flash) is the fixed low-cost model for the slightly harder Beta coding tests.
- The [OpenRouter Models API](https://openrouter.ai/docs/guides/overview/models) is the release-time authority for availability, capabilities and pricing.

### Credential rule

The root `.env` is a developer-local input to the protected live-test launcher only. It must remain ignored, untracked and permission-restricted. Application code receives only the environment key name `OPENROUTER_API_KEY`; the value is resolved at the last responsible moment inside the model adapter process. Never `source` arbitrary `.env` content in application or CI code.

The key must not reach:

- model context or tool arguments;
- runtime/worker/evaluator environment;
- ledger, CLI frames, telemetry or receipts;
- cassette request/response files, errors, logs, process listings or build artifacts.

### Test tiers

| Tier | Model/source | Frequency | Task | Gate semantics |
|---|---|---|---|---|
| Offline | fake + sanitized cassette | Every PR | parser, tool loop, approvals, restart, sandbox and evaluator contracts | Deterministic CI; labelled `cassette`, never live |
| Free live canary | `openrouter/free` | Protected pre-merge and R7 | streaming shape, resolved-model identity, one read-only task and one trivial single-file repair | Assert protocol/behavior, not exact prose; no fallback; rate limit is instrument error |
| Cheap fixed-model | `deepseek/deepseek-v4-flash` | R7 and final R9 only | two small one- or two-file coding repairs, one including forced restart | Bounded calls/tokens/time; exact accepted diff; no complex benchmark |

Each live run must preregister hard limits for model calls, prompt/completion tokens, wall time and output bytes. A USD-micros cap may be asserted only when pricing was fetched and versioned; otherwise `pricing_known=false` and the non-currency limits still enforce safety. The current hard-coded table does not know DeepSeek V4 Flash and must not invent a price.

## 12. Dogfood plan — small, real and sufficient

The final gate uses three clean repositories or clean worktrees with preregistered failing tests:

| Run | Model | Maximum task shape | Required disturbance |
|---|---|---|---|
| 1 | `openrouter/free` | One-file pure-function boundary/input bug | Normal approval path |
| 2 | `deepseek/deepseek-v4-flash` | One-file parsing/validation bug | Kill after `ApprovalRequested`, restart and sign externally |
| 3 | `deepseek/deepseek-v4-flash` | Two-file caller/implementation mismatch | Kill after `ApprovalResolved`, ledger-only exactly-once resume |

Every run must use the installed `vg` CLI, live RuntimeService, canonical context, real streaming provider, Kernel, sandbox, external signer, durable SQLite, terminal-ledger evaluator trigger and exterior evaluator. The evidence bundle contains the clean starting commit, prompt, provider-resolved model, redacted provider metadata, ledger export, challenge/decision, sandbox and evaluator attestations, final diff, test output, artifact digests and independent countersignature. No fixed patch or model script may exist in the runner.

## 13. Packaging, deployment and distribution backlog

Publishing to a registry or deploying externally is not authorized by this backlog; these tasks create and validate release artifacts for a later explicit GO action.

| Ticket | Pri | Owner | Work | Depends | Acceptance / evidence |
|---|---:|---|---|---|---|
| `S6B-REL-001` | P0 | Senior + Project Lead | Accept distribution/version contract: Python runtime wheel/sdist, npm CLI tarball, pinned worker/evaluator OCI images, schema bundle and separately versioned `vg-code-default`; define SemVer, protocol compatibility, Linux baseline, XDG/state paths and rollback | ARC-001 | Compatibility matrix and one owner for the `vg` executable; framework contains no example-specific control flow |
| `S6B-REL-002` | P1 | Lane B | Add Python packaging, locked dependencies and runtime/daemon entrypoint; package schemas/manifests as resources | REL-001, SA-002 | Wheel/sdist build from clean clone; import and daemon work with source tree absent |
| `S6B-REL-003` | P1 | Lane B | Build pinned worker and evaluator images/artifacts with non-root identities and immutable digests | MD-006..008, REL-001 | Runtime observes expected identity/digest; artifact contains no source secrets or writable oracle |
| `S6B-REL-004` | P1 | Lane C + D | Package `vg-code-default` example, safe defaults, sample task/repository and headless quickstart | JR-003, REL-002 | Fresh machine installs artifacts and runs the example without a source checkout |
| `S6B-REL-005` | P1 | Senior + Lane D | Provide rootless local deployment/supervisor config, readiness, state permissions, graceful shutdown, ledger migration, upgrade and rollback | REL-002, REL-003 | Clean Linux environment deploys without source bind mount; restart resumes; unsupported isolation fails closed; upgrade and predecessor rollback are exercised |
| `S6B-REL-006` | P1 | Lane D | Produce LICENSE/NOTICE, third-party licenses, SBOM, provenance, checksums, signed tag/artifacts, vulnerability report, support/security policy and Beta release notes | SEC-002, REL-002..005 | Signatures/checksums/SBOM bind exact artifacts and candidate SHA; notes state supported platform, limits and data handling |
| `S6B-REL-007` | P1 | Project Lead + independent reviewer | Dry-run the complete release from final artifacts | R0–R10 candidate, REL-004..006 | Clean install, offline suite, protected live matrix, dogfood ×3, upgrade/rollback and documented commands pass; independent GO/NO-GO receipt produced; no implicit publish |

## 14. Correct R0–R10 release gates

The old Sprint 6 receipts used different gate meanings. Sprint 6B uses the rev2 §14 definitions below and stores evidence under `docs/agile/sprint6B/evidence/R0` through `R10`.

| Gate | Must prove | Required evidence | Independent signer |
|---|---|---|---|
| R0 — Security hygiene | Revoked credential absent from all reachable refs/artifacts; blocking scanner works | Revocation/purge record, all-ref/tree/artifact scans, fake-secret rejection | Security/release reviewer |
| R1 — Reproducible source | Exact candidate builds and tests from clean clone with no local dependencies | Clean checkout/install/import/full-gate log and clean final status | Integration reviewer |
| R2 — Architecture/TCB | Boundaries and TCB pass; no fake/scenario/direct-host fallback | Boundary/TCB reports and no-fallback adversarial test | Tech Lead not authoring tested control |
| R3 — Effect isolation | Every product effect is rootless and cannot reach host/network/secrets/evaluator | Sandbox profile, containment receipt and escape/network/home/socket tests | Systems reviewer |
| R4 — Evaluator exteriority | Supervisor-attested process/identity/image, authenticated IPC, sealed oracle and signed verdict | Attestation plus tamper/pollution/peer/drop/crash results | Evidence/systems reviewer |
| R5 — Approval/recovery | External exact signature and kill/restart exactly-once ledger resume | Signed challenge/decision, grant linkage, revocation and transition kill matrix | Governance reviewer |
| R6 — Live operator path | Installed `vg` controls real RuntimeService with durable approval/correction/cursor behavior | Headless transcript, reconnect/gap/dedup tests and stable exit codes | Client reviewer |
| R7 — Provider/context | Real incremental streaming, valid tool translation, turn-2 observation and secret safety on both model routes | Sanitized live receipts, TTFT boundary proof and malformed/context-bypass tests | Model reviewer |
| R8 — Measurement integrity | Live/cassette/synthetic cannot mix; integer timing/cost and failures are truthful | Labelled export, instrument tuple and synthetic-to-live rejection | Measurement reviewer |
| R9 — Dogfood | Three preregistered small bugs fixed through the installed sole path with zero source edits | Sealed run bundles and independent review | Project Lead / independent reviewer |
| R10 — Contract/release | R0–R9 valid at candidate SHA; only then close rows, reseal baseline and tag candidate | Contract diff, verified receipts, release dry-run, clean tree and final signature | Project Lead |

No gate is closed by a markdown assertion. Every gate needs a reference run, a deliberately broken counterpart where applicable, raw-output digests, the exact subject SHA and a signer who did not implement the control.

## 15. Target final commands

Tickets must create or repair the missing scripts so the release reviewer can run one documented sequence from a clean checkout:

```bash
python3 -m unittest discover -s test
npm ci
npm --workspace @vanguard/cli run typecheck
npm --workspace @vanguard/cli test
python3 tools/audit_v4.py
python3 tools/check_sprint0_governance.py
python3 tools/check_schema_archaeology.py
python3 tools/check_baseline_manifest.py --release
python3 tools/check_active_mvp_contract.py --release
python3 tools/run_active_contract_tests.py
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/run_broken_tests.py
python3 tools/scan_secrets.py --all-refs --artifacts dist
python3 tools/run_live_beta_gates.py --model openrouter/free
python3 tools/run_live_beta_gates.py --model deepseek/deepseek-v4-flash
python3 tools/run_sprint6b_dogfood.py --runs 3
python3 -m build
npm --workspace @vanguard/cli pack
python3 tools/verify_release_artifacts.py
```

Commands naming files or options not yet present are acceptance targets, not claims that they exist today. Live commands are run only through the protected local launcher after `.env` safety checks; captured output is sanitized before sealing.

## 16. Definition of done

Sprint 6B is complete only when all statements below are true:

1. The sole installed product path matches §2 and contains no scenario, scripted-model, direct-host-effect, runtime-signing or direct-evaluator fallback.
2. `vg run <repo> --headless --prompt ...` works with `openrouter/free` and `deepseek/deepseek-v4-flash`, emits valid JSONL and returns documented exit codes.
3. Privileged changes show the exact normalized diff, require an external signature and resume exactly once from durable ledger state after forced restart.
4. Every observation/effect is mediated by Kernel and the rootless worker; every evaluation is triggered from terminal ledger evidence by the exterior evaluator.
5. Root `.env` remains local and untracked; its key value is absent from every reachable Git object, context, process outside the model adapter, event, log, cassette, receipt and artifact.
6. Sprint 1 human gates and the durable Beta schema-lock decision are signed; branch protection is verified.
7. Contract rows remain open until their machine-verifiable R-gate receipt passes; the checker rejects premature closure.
8. Framework, CLI, worker/evaluator, schemas and `vg-code-default` build reproducibly and install without the source tree.
9. A clean Linux deployment survives restart, upgrade and tested rollback; unsupported containment fails closed.
10. Three small real dogfood runs pass with zero human source edits and independent R9 review.
11. R0–R10 bind one candidate SHA, all required tests and broken counterparts pass, the tree is clean, and no receipt or manifest contains `pending`.
12. Project Lead signs GO for the release candidate. Publication, deployment to external users and registry distribution occur only after a separate explicit authorization.

## 17. Stop rules

- Stop integration if a lane changes a frozen public interface without coordinated review.
- Stop live testing if the secret appears in any serialized surface or if `.env` is tracked/permissive.
- Stop an effect if rootless isolation or containment probes are unavailable; never fall back to host execution.
- Stop evaluation on peer/image/oracle uncertainty and record `inconclusive`.
- Stop R10 if any Beta row is open, any receipt is unsigned/stale, or any required live test was skipped.
- Stop and re-plan as a multi-sprint programme if PL-001 rules all 133 CI gaps and all 15 planned schemas into Beta scope.
- Stop release if the installed artifact behaves differently from the source-tree candidate or rollback has not been successfully exercised.
