# Sprint 6B Close — Two-Senior Development and Release Guidelines

**Status:** Active closure guidance; release remains NO-GO  
**Audience:** Senior Developer A, Senior Developer B, Tech Lead, Project Lead and independent release reviewer  
**Scope:** close Sprints 1–6 and deliver the Vanguard framework plus `vg-code-default` and `vg` Linux Beta  
**Primary plan:** [Sprint 6B execution package](../agile/sprint6B/README.md)

## 1. Product definition

Vanguard Beta is two products delivered together:

1. **Framework:** generic domain/ports/kernel/agency/runtime/adapters boundaries, versioned service and adapter contracts, manifest-driven harness composition, durable evidence and extension registries.
2. **First harness:** `vg-code-default`, a coding manifest/pack defining prompt, context/routing/budget policy, typed read/search/patch/test tools and evaluator reference, operated through `vg`.

The framework must not contain `vg-code-default` control flow. Adding a future harness may add a pack and adapters behind existing ports; it must not fork RuntimeService or EpisodeEngine. Beta proves one coding harness only. Non-coding generality and self-improvement experiments remain after Beta.

## 2. Architecture rules

### Dependency direction

```text
domain ← ports ← kernel ← agency ← runtime → adapters
                                      ↑
                               composition only

CLI → RuntimeService wire contract; never Python imports
harness pack → data/configuration; never a second engine
evaluator → exterior EvidencePlane; never agency-owned
```

- Domain contains canonical values and pure reductions.
- Ports contain interfaces and boundary types, no concrete implementations.
- Kernel owns capability authorization, budgets, grants, intent and effect dispatch.
- Agency owns bounded observe/propose progression, not authority or evaluation.
- Runtime owns generic composition, durable lifecycle and service orchestration.
- Adapters own provider, storage, worker and evaluator mechanisms behind ports.
- CLI is an untrusted client and contains no authoritative lifecycle state.

### SOLID and modularity

- **Single responsibility:** service transport, lifecycle reducer, provider parsing, worker execution, approval signing and evaluation are separate components.
- **Open/closed:** add providers/tools/harness packs through registries and schemas, not conditional branches in the loop.
- **Liskov:** fake/LAM/cassette/live adapters obey the same port failure semantics; a test double cannot return a success impossible in production.
- **Interface segregation:** prefer narrow Model, Worker, Evaluator, EventStore and Signer/Verifier ports over a universal runtime object.
- **Dependency inversion:** high-level lifecycle depends on ports and immutable values; concrete adapters are injected only at composition.

Avoid speculative plugin frameworks. For Beta, “plugin-like” means a frozen registry + manifest/package contract + fail-closed discovery. Do not add runtime code loading, arbitrary Python imports, remote plugin download or third-party execution until signing, compatibility and sandbox policy exist.

## 3. Two-lane operating model

Lane A owns control/service/client/governance/release. Lane B owns model/context/worker/evaluator/platform. Both are empowered to make normal implementation decisions inside their frozen boundaries.

### Two-key changes

Both seniors must approve changes to:

- durable/public schemas and canonical bytes;
- port semantics and failure taxonomy;
- authority or trust boundaries;
- sandbox mounts/network/degraded policy;
- approval signature fields/key/revocation;
- evaluator attestation/IPC/verdict semantics;
- protocol/artifact compatibility and version bumps;
- Beta scope, contract closure or R-gate meaning.

Record a concise decision containing problem, choice, alternatives, owner, compatibility/migration, failure behavior, tests and reversal condition. Do not bury architecture decisions inside implementation commits.

### Review independence

- Lane A reviews Lane B's R3/R4/R7/R8 controls.
- Lane B reviews Lane A's R1/R2/R5/R6 controls.
- An author never signs their own gate.
- If both lanes co-author the control, obtain an independent reviewer.
- R9/R10 require repository-owner or named independent release-review countersignature.

## 4. Shared-worktree and Git discipline

Before editing or committing:

```bash
git status --short --branch
git log -5 --oneline
```

- Preserve all pre-existing changes and untracked files.
- Never reset, restore, rebase, globally stash, clean or amend shared work.
- Stage exact owned files only; do not use `git add .` or `git add -A`.
- Use ticket-scoped commits and include the relevant requirement/gate IDs.
- Do not push unless the repository owner explicitly requests it.
- Shared files are edited by their DRI after reviewing the other lane's proposal.
- Interface changes land before their consumers and include golden vectors.

Recommended integration order:

```text
decision/schema commit
  → Python/TypeScript conformance
  → Lane B adapters and Lane A service/client in parallel
  → LAM vertical integration
  → adversarial trust-path integration
  → provider/platform packaging
  → clean candidate and dogfood
```

## 5. Engineering patterns

### Boundary parsing

Use the same five steps at every external boundary:

1. read bounded bytes/frame;
2. parse strict versioned syntax;
3. validate types, limits and extension policy;
4. map into canonical immutable domain/port values;
5. only then call the application/domain service.

Never cast provider, CLI or IPC dictionaries directly into authoritative types. Preserve typed instrument errors and redact secrets before logging.

### Durable command/event processing

- Commands have version, command ID, actor, idempotency key and intended aggregate/run.
- Persist command acceptance before executing it.
- Allocate event sequence atomically and persist causal relationships.
- Commit event and outbox atomically; projections are rebuildable.
- Retried commands return the prior receipt and do not repeat effects.
- Stream cursors resume after the last acknowledged sequence and reject gaps.
- Terminal transitions are unique.

### Effects and recovery

Use the only legal order:

```text
validated proposal
  → Kernel authorization/reservation
  → durable approval when privileged
  → durable EffectIntent
  → sandbox worker effect
  → durable receipt or undeterminable reconciliation
```

On restart, reduce durable events and perform only the next legal transition. Never call the model again to rediscover an already approved action. Preserve the original reservation and descriptor.

### Model/provider integration

- ContextCompiler produces the canonical invocation.
- Provider wire DTOs stay in provider adapters.
- Manifest registry translates tool names to allowed canonical actions.
- Model arguments are untrusted and never provide authority.
- One-effect-per-turn Beta rejects ambiguous multiple tool calls.
- LAM, Ollama and OpenRouter differ only behind ModelPort.
- Provider/model fallback is always explicit and operator-selected.
- Source/provenance is structural, not a caller-supplied label.

### Sandbox and evaluator

- Every model-driven read/search/patch/test runs inside the same worker boundary.
- A path allowlist is not a sandbox; OS containment and verified probes are required.
- Unavailable containment is a hard product failure.
- Worker cannot reach home, secrets, network, runtime/evaluator sockets or oracle.
- Evaluator is a separately supervised identity and consumes only terminal evidence.
- Measure peer/image/config/oracle identity; do not trust configuration claims.
- Any evaluator uncertainty produces signed `inconclusive`.

### Security and secrets

- Runtime stores secret references, never provider values.
- Strictly parse allowlisted `.env` keys; never source the file.
- Secret exists only inside the provider adapter process at call time.
- Scan tree, diff, all refs and built artifacts.
- Rotate first, then perform separately authorized history cleanup.
- Never place a secret in command arguments, tickets, events, logs, cassettes or receipts.

### Performance

Correctness and trust come first, then measure:

- stream provider bytes incrementally and bound every buffer;
- use SQLite WAL and indexed run/stream/idempotency keys;
- avoid full ledger scans in request paths; use rebuildable projections;
- preserve L1–L3 byte identity for KV-cache reuse;
- use integer monotonic durations and integer USD micros;
- keep worker/evaluator processes reusable only if identity and cleanup remain provable;
- profile before adding caches, pools or concurrency.

No optimization may weaken durability, canonicalization, containment, evidence or cancellation.

## 6. Testing pyramid and gate discipline

### Per change

- unit tests for pure parsers/reducers;
- contract/golden tests at each Python/TypeScript/process boundary;
- integration tests through public ports;
- reference plus deliberately broken counterpart for each control;
- regression test for every discovered false-success path.

### Product path tiers

1. **Unit/fake:** deterministic logic only; cannot prove product completion.
2. **LAM:** complete installed offline path and multi-turn tool loop.
3. **Cassette:** protocol/replay compatibility, explicitly labelled and read-only where applicable.
4. **Ollama:** explicit local-model adapter and honest instrument failures.
5. **OpenRouter:** protected live canary with strict secret handling and bounded budget.
6. **Dogfood:** three real bugs on the frozen candidate with no human source edits.

The same acceptance assertions run at tiers 2–5 where meaningful. No lower tier may be relabelled as a higher tier.

### Mandatory failure cases

Cover at minimum:

- invalid/unsupported protocol and oversized/truncated frames;
- duplicate command, concurrent writer, cursor duplicate/gap and early EOF;
- malformed/ambiguous/unknown provider tools and lost Turn 2 observation;
- forged/transplanted/replayed/expired/revoked approvals;
- forced kill around challenge, decision, grant, intent, effect and receipt;
- path/symlink/mount/network/home/secret/socket escape;
- worker timeout and process-group cleanup;
- wrong evaluator peer/image/nonce, oracle pollution, timeout and crash;
- mock/cassette/synthetic relabelled as live;
- missing daemon/provider/sandbox/evaluator/store without fallback;
- clean artifact running with source tree absent.

## 7. Binding implementation decisions and Luna execution authority

The decisions below are the default Tech Lead, Project Lead and Senior Developer rulings for Sprint 6B. Luna may implement both lanes end-to-end without requesting routine design approval when the implementation conforms to these decisions, the v4 authority documents and the frozen acceptance criteria. If a ruling conflicts with a higher-authority v4 requirement, the v4 requirement wins and the conflict must be reported.

### 7.1 Product and scope decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-001` | Beta closes Chapter 10 Q1+Q2 only: real boundary and useful coding workflow. Q3 measurement experiments, Q4 non-coding generality, autonomous self-improvement, remote multi-tenancy and microVMs remain deferred. |
| `DEC-6B-002` | Supported Beta platform is Linux x86-64 with rootless Bubblewrap/OCI capability. Unsupported platforms fail preflight and are not silently degraded. |
| `DEC-6B-003` | Headless CLI is the primary product. TUI is a thin optional view over the same application/client layer and receives no separate lifecycle logic. |
| `DEC-6B-004` | The deliverable is one generic framework plus the separately versioned `vg-code-default` harness pack. Coding verbs, prompts and policies live in the pack/registries, not RuntimeService or EpisodeEngine. |
| `DEC-6B-005` | “Plugin-like” Beta extensibility means validated manifests, package resources and explicit allowlisted adapter registries. No arbitrary dynamic Python import, remote plugin installation or untrusted plugin execution is allowed. |

### 7.2 Public protocol and persistence decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-010` | RuntimeService uses a Unix `SOCK_STREAM` socket with owner-only filesystem permissions (`0600`) and observed peer credentials. Default socket/state locations follow XDG runtime/state directories; `/tmp` is not a trusted production default. |
| `DEC-6B-011` | Wire format is versioned UTF-8 NDJSON, one bounded object per line, with a 1 MiB Beta frame limit. Every frame has protocol version, kind, command/event ID and correlation/run identity. Unknown required fields, duplicate keys, invalid UTF-8, oversized or unsupported-version frames fail before domain construction. |
| `DEC-6B-012` | Required commands remain StartRun, GetRun, StreamEvents, ResolveApproval, RecordCorrection, Cancel, Checkpoint, Resume and ExplainArtifact. One command schema and one error taxonomy are shared by Python and TypeScript golden vectors. |
| `DEC-6B-013` | Runtime durability uses SQLite in WAL mode with foreign keys enabled, explicit migrations and transactions spanning command inbox/event outbox changes. Production has no in-memory store default. |
| `DEC-6B-014` | Commands use globally unique command IDs plus caller idempotency keys. Events use UUIDv7 identifiers and durable integer per-stream sequences. Duplicate commands return the original durable receipt; sequences are never reused after restart. |
| `DEC-6B-015` | Event payloads are canonicalized with the repository's existing canonical JSON/digest rules. Projections are rebuildable and never become the authoritative source. |
| `DEC-6B-016` | Client reconnect resumes strictly after the last accepted sequence. Duplicate frames are ignored; a forward gap is an explicit protocol error requiring resync, never silently skipped. |

### 7.3 Lifecycle, approval and recovery decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-020` | Process, approval and run status reduce through one event-sourced lifecycle authority. Parallel state machines may exist only as projections, not independent decision makers. |
| `DEC-6B-021` | The durable order is challenge-before-suspend, decision-before-authorization, intent-before-effect and receipt/reconciliation-after-effect. One terminal event is permitted. |
| `DEC-6B-022` | Approval signatures use Ed25519. Operator CLI/key agent owns the private key; runtime owns only allowlisted public keys/key IDs and durable revocation state. Shared HMAC is prohibited in the product path. |
| `DEC-6B-023` | Approval canonical bytes bind version, key ID, challenge/approval IDs, actor/reviewer, run/process, action/resource, normalized arguments/diff and their digests, policy, reservation, challenge-event ID, decision, nonce and expiry. Any mismatch rejects the decision. |
| `DEC-6B-024` | Unified diffs normalize UTF-8, LF line endings and one terminal newline before hashing/display/signing. The exact normalized bytes displayed are the bytes authorized and applied. Ambiguous or non-canonical patches are rejected. |
| `DEC-6B-025` | Operator private keys use an owner-only XDG configuration path or an explicitly configured external key agent. Private key bytes never enter RuntimeService, ledger, events, worker, evaluator, telemetry or receipts. |
| `DEC-6B-026` | Recovery reduces ledger state and performs only the next legal transition. It preserves the original descriptor/reservation and never repeats a model call for an already approved proposal. |
| `DEC-6B-027` | An effect with durable intent but no conclusive receipt is `undeterminable` until adapter reconciliation proves occurred/not-occurred. It is never blindly retried. |
| `DEC-6B-028` | Cancellation and capability/key revocation are durable. They block the next effect across active, suspended and resumed runs. |

### 7.4 Model, context and provider decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-030` | ContextCompiler emits the only production `ModelInvocation`; L1–L3 remain byte-stable, task brief immutable and L5 observations provenance-bearing. |
| `DEC-6B-031` | Canonical `ModelProposal` is `{kind, action, resource, args, reservation, note}`. Provider-specific `{text, tool_calls}` never reaches the episode parser directly. |
| `DEC-6B-032` | Beta permits at most one effect tool call per turn. Multiple/ambiguous calls, unknown tools, malformed arguments or privileged fields supplied by the model are instrument errors. |
| `DEC-6B-033` | Manifest lookup supplies the allowed canonical action/tool schema. Runtime/Kernal policy supplies authoritative resource scope, capability and reservation limits; the model cannot widen them. |
| `DEC-6B-034` | LAM, Ollama and OpenRouter are explicit ModelPort configurations. There is no automatic provider/model fallback. Missing endpoint/key/model/capability/rate allowance is an instrument error. |
| `DEC-6B-035` | LAR remains a developer diagnostic/benchmark CLI and is not spawned from production runtime. Shared low-level code may be extracted only if it obeys adapter boundaries and does not introduce a second model contract. |
| `DEC-6B-036` | LAM is the first complete integration target and must drive a real multi-turn read→patch→test→finish sequence from received tool observations. It is structurally labelled `mock`. |
| `DEC-6B-037` | Streaming is incremental and bounded. TTFT is integer monotonic milliseconds to the first validated semantic content/tool delta. Retry is allowed only before semantic output is accepted. |
| `DEC-6B-038` | Unknown pricing remains `pricing_known=false`; no invented price is allowed. Requested/resolved model, source, pricing source/as-of, integer usage and failures are recorded. |

### 7.5 Sandbox and evaluator decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-040` | One typed authenticated worker protocol owns every model-driven read, search, patch and test. Direct runtime/host Git, filesystem or subprocess execution is prohibited for product effects. |
| `DEC-6B-041` | Bubblewrap is the Linux Beta isolation baseline: unshared user/mount/PID/IPC/UTS/network namespaces, sanitized environment/PATH, read-only system mounts, writable workspace/tmp only, bounded resources/output and process-group cancellation. |
| `DEC-6B-042` | Worker cannot access home, repository-root `.env`, runtime/evaluator sockets, evaluator bundle/oracle, host network or paths outside declared workspace. Symlink/path checks occur outside and inside the worker. |
| `DEC-6B-043` | Missing runtime, failed containment probe or unverified receipt fails composition/effect. No host fallback exists. Containment evidence is probe-derived and durable. |
| `DEC-6B-044` | Evaluator is a separately packaged/supervised process under UID 10002, reached only through authenticated bounded Unix IPC. Runtime imports an evaluator client port, never evaluator implementation. |
| `DEC-6B-045` | Evaluator and client verify observed peers in both directions with version, nonce/request ID and socket permissions. Configuration claims alone do not establish identity. |
| `DEC-6B-046` | Evaluator measures executable/image/config/oracle digests, consumes only persisted terminal evidence, seals oracle independently and signs verdicts with its own Ed25519 authority. |
| `DEC-6B-047` | Wrong peer/UID/image/config/oracle/nonce/version, timeout, truncation, crash or pollution produces a signed and persisted `inconclusive`; it never produces PASS or task failure. |

### 7.6 CLI and operator decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-050` | Production `vg` defaults only to RuntimeService. Scenario, replay, cassette and stdin feed require explicit options, are visibly labelled and cannot pretend to persist mutable commands. |
| `DEC-6B-051` | Headless stdout contains JSONL protocol/application results only; diagnostics use stderr. Empty EOF before a terminal event is exit 2. |
| `DEC-6B-052` | Stable exits are 0 confirmed success, 1 confirmed rejected/cancelled/unsatisfied task, and 2 usage/protocol/instrument/unavailable/uncertain result. Every command sets its process exit code. |
| `DEC-6B-053` | `vg approve` displays canonical diff/descriptor bytes, signs outside runtime and submits the decision. Non-TTY runs never auto-approve. |
| `DEC-6B-054` | Corrections persist through RuntimeService with the actual accepted patch digest. Replay is read-only and cannot report persistence success. |

### 7.7 Security, telemetry and privacy decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-060` | Only `OPENROUTER_API_KEY` may be read from local `.env`; parsing is strict and never uses shell sourcing/interpolation. File must be ignored, untracked, non-symlink and owner-restricted. |
| `DEC-6B-061` | Provider secret value exists only in the provider adapter process at call time. All other objects/surfaces contain only its reference or redacted metadata. |
| `DEC-6B-062` | Evidence source (`live`, `mock`, `cassette`, `synthetic`) is fixed by adapter construction and cannot be supplied/relabelled by callers. |
| `DEC-6B-063` | Time, byte, token and currency observations use integers. Failures and unknown measurements are recorded rather than dropped or coerced to zero. |
| `DEC-6B-064` | Credential rotation occurs before history cleanup. History rewrite, ref removal and remote coordination are destructive external operations requiring separate repository-owner approval despite this technical decision. |

### 7.8 Packaging, compatibility and performance decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-070` | Release set contains a Python wheel/sdist with runtime/evaluator entry points, npm CLI tarball, schema bundle, separately versioned `vg-code-default` pack and pinned worker/evaluator OCI images. |
| `DEC-6B-071` | All artifacts share a compatibility manifest covering framework, RuntimeService protocol, CLI, harness ABI/schema and image digests. SemVer governs public compatibility; protocol breaking change requires a major protocol version. |
| `DEC-6B-072` | Containers install the exact candidate package, run non-root, contain no local secret and are referenced by measured immutable digests—not placeholders or mutable tags. |
| `DEC-6B-073` | Release artifacts include LICENSE/NOTICE, third-party licenses, SBOM, provenance, checksums, signatures, support/security policy and Beta limitations. |
| `DEC-6B-074` | Clean-install, migration, restart, upgrade and predecessor rollback must work without source checkout or bind-mounted repository. |
| `DEC-6B-075` | Performance choices: bounded streaming, indexed SQLite queries, rebuildable projections and prefix-stable context are approved. Caches, pools and concurrency are added only after measurement and may not weaken trust/durability. |

### 7.9 Verification, evidence and release decisions

| ID | Binding decision |
|---|---|
| `DEC-6B-080` | Every control requires a passing reference and a deliberately broken counterpart that fails for the intended reason. Private-method tests alone cannot close a product-path requirement. |
| `DEC-6B-081` | Candidate contract mode executes every applicable open/covered requirement. Zero applicable commands is OPEN/SKIP or failure, never PASS. |
| `DEC-6B-082` | Gate receipts bind candidate SHA, allowed evidence commit, command/exit/output digest, artifact digests, environment/tool versions, timestamp, signer and independent countersigner. Prose-only, pending, stale or self-signed receipts fail. |
| `DEC-6B-083` | R0–R10 meanings in the Sprint 6B backlog are final for Beta. Old Sprint 6 receipts remain historical/invalidated. |
| `DEC-6B-084` | Dogfood uses three preregistered real bugs, installed candidate artifacts and zero human source edits. Humans may prompt, reject/approve exact bytes and record corrections. |
| `DEC-6B-085` | A positive Q2 requires each completed run to be useful and the operator to answer honestly that they would reach for it again. A negative answer blocks Beta and triggers product-loop repair. |
| `DEC-6B-086` | Contract rows close and baseline reseals only after valid R0–R9 evidence at one frozen clean candidate SHA. |
| `DEC-6B-087` | Luna may implement code, tests, fixtures, docs, packaging and local dry runs for both lanes. Luna may not independently countersign its own controls, authorize destructive/external actions, mark human evidence complete, create/push a release tag or publish artifacts. |
| `DEC-6B-088` | Final R9/R10 countersignature and tag/publication remain human/repository-owner release actions. This is separation of evidence authority, not unfinished architecture work. |

### 7.10 Luna implementation protocol

Luna should execute the backlog in dependency order and make ordinary code-level choices autonomously. For every task Luna must:

1. cite the applicable `DEC-6B-*`, ticket and requirement IDs;
2. inspect the current implementation/tests and preserve unrelated work;
3. write the narrow contract or failing regression first where practical;
4. implement behind the assigned lane boundary;
5. add adversarial/broken-counterpart coverage;
6. run narrow tests, then the relevant lane gate;
7. report files, commands, results, compatibility and remaining evidence;
8. never claim release closure from component tests.

Luna escalates only when:

- two binding decisions or a v4 authority conflict;
- required behavior cannot be implemented without changing a frozen public/trust boundary;
- a safety assumption fails and every conforming path is blocked;
- a credential, destructive history/ref operation, hosted control, external deployment, tag or publication is required;
- independent human evidence/signature or a subjective Q2 answer is required;
- scope growth would add Q3/Q4, remote multi-tenancy, microVMs or arbitrary plugins to Beta.

For ordinary ambiguity, choose the smallest fail-closed implementation consistent with these decisions, record the assumption and continue.

## 8. Delivery waves

| Wave | Lane A | Lane B | Joint exit |
|---|---|---|---|
| 0 — Truth and seams | Decisions, contract/evidence design, service schemas | Model/worker/evaluator schema proposals and threat cases | Frozen interfaces and golden vectors; candidate gates intentionally red |
| 1 — Parallel backend | Durable service, lifecycle, CLI client | Canonical model, LAM, worker, evaluator | Lane tests pass independently behind frozen ports |
| 2 — Offline vertical | Compose service/client, approval and ledger | Supply LAM/tool/worker/evaluator adapters | Installed `vg` completes LAM task; restart works; no fallback |
| 3 — Trust hardening | Ed25519, kill/recovery, revocation | isolation, attestation, secret/telemetry hardening | R2–R6 candidate controls pass adversarially |
| 4 — Providers/artifacts | operator UX, deployment, contract candidate mode | Ollama/OpenRouter, wheel/images/SBOM inputs | clean install and R7/R8 pass |
| 5 — Release candidate | freeze SHA, receipts, docs, rollback | fixtures, oracles, sanitized evidence | three Q2 runs and R0–R10 independently validated |

Treat 4–6 calendar weeks as the planning envelope for two seniors. Re-estimate after Wave 0; do not force a date by weakening a gate.

## 9. Definition of done

Sprint 6B and Sprints 1–6 are closed only when:

1. one installable product path matches the Sprint 6B README and no second path can claim live evidence;
2. framework lifecycle is generic and `vg-code-default` remains a separately versioned harness pack;
3. LAM, Ollama and OpenRouter use the same canonical model proposal path;
4. every product effect is Kernel-mediated and rootless;
5. exact privileged bytes are externally signed and recover exactly once from ledger;
6. exterior evaluator identity/oracle/verdict are measured, isolated and persisted;
7. secret/history, Sprint 1 human/schema and hosted-control residuals are closed or explicitly ruled outside Beta by an accepted decision;
8. wheel, npm package, schema/harness pack and worker/evaluator images install without source checkout;
9. full tests, broken counterparts, clean candidate, upgrade and rollback pass;
10. three real dogfood bugs pass with zero human source edits and positive reach-for-it-again answers;
11. R0–R10 bind one clean candidate SHA and independent signatures;
12. repository owner/project release authority explicitly approves tag/publication.

## 10. Required final command sequence

Commands named below that do not yet exist are delivery targets and must be implemented before R10:

```bash
python3 -m unittest discover -s test
npm ci
npm --workspace @vanguard/cli run typecheck
npm --workspace @vanguard/cli test
python3 tools/002_LLM_API_MOCK/test_mock.py
python3 tools/audit_v4.py
python3 tools/check_sprint0_governance.py
python3 tools/check_schema_archaeology.py
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/run_broken_tests.py
python3 tools/scan_secrets.py --all-refs --artifacts dist
python3 tools/run_active_contract_tests.py
python3 tools/check_baseline_manifest.py --release
python3 tools/check_active_mvp_contract.py --release
python3 tools/run_live_beta_gates.py --model openrouter/free
python3 tools/run_live_beta_gates.py --model deepseek/deepseek-v4-flash
python3 tools/run_sprint6b_dogfood.py --runs 3
python3 -m build
npm --workspace @vanguard/cli pack
python3 tools/verify_release_artifacts.py
```

Record command, exit code, environment/tool versions and output digest. A skipped mandatory command, zero applicable tests or dirty candidate is not green evidence.

## 11. Leadership stop rules

Stop and resolve before continuing when:

- a frozen shared interface changes without two-key review;
- provider/model data acquires scope, capability, reservation or approval authority;
- a direct host effect, runtime signer, direct evaluator or fake fallback appears;
- a secret reaches any serialized surface;
- containment, evaluator identity or durable store is unavailable;
- a control author is asked to countersign their own evidence;
- contract/baseline closure is proposed before R0–R9;
- installed behavior differs from the source candidate;
- rollback, dogfood or mandatory live evidence is skipped;
- a release, history rewrite, remote mutation or credential action lacks explicit repository-owner authorization.

When stopped, preserve evidence, report the smallest blocking decision and do not make the gate easier.
