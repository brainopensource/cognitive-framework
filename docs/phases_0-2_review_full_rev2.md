# Vanguard Phases 0–2 Full Technical Audit, Revision 2

**Audit purpose:** establish the corrective engineering program required before Vanguard may be represented, built, or shipped as a Beta MVP.  
**Repository snapshot:** `sprint5-6/integration`, HEAD `57e0eb8`, reviewed 2026-08-15.  
**Scope:** architectural intent established in Phases 0–1; implementation and integration delivered through Sprints 5–6; security, governance, evaluation, client, model, telemetry, release, and evidence surfaces.  
**Method:** requirements-first review, source inspection, commit archaeology, clean-tree reproduction, adversarial design analysis, and reconciliation of three independent developer assessments.

> **Release decision: NO-GO.** Phase 2 contains useful and testable components, but the repository does not yet implement the promised Beta MVP as one trustworthy product. The current branch must not be merged or released under a “Phase 2 complete” claim until the mandatory closure gates in §14 pass on a clean, secret-free checkout.

> **ACT NOW, BEFORE READING FURTHER.** A live provider credential is committed **at HEAD** and **present on `origin`** (§2.3). Revoke it before any other action, including reading the rest of this document. Every subsequent finding is survivable; this one is actively costing money or trust while unaddressed.

## 0. How to read this document

### 0.1 Severity legend

| Level | Meaning | Consequence |
|---|---|---|
| **Critical** | Active harm, or a claim the system cannot support | Blocks all release work until closed |
| **High** | Beta claim is false without it | Blocks the Beta gate (§14) |
| **Medium** | Correctness or maintainability risk that compounds | Must have an owner and a dated plan; may ship with a recorded exception |
| **Low** | Hygiene | Backlog |

### 0.2 The distinction this document depends on

Every finding is tagged **Beta-blocking** or **GA-blocking**. `ADR-0057` scopes Beta to `GTS-13C` Chapter 10 **Q1 (is the boundary real?)** and **Q2 (is it useful?)**, and explicitly defers **Q3 (measurability)** and **Q4 (generality)** to S7–S9. A remediation program that treats every finding as Beta-blocking is not more rigorous — it is unschedulable, and a team facing an unschedulable program cherry-picks. §7.1 draws that fence explicitly. Rev 1 of this audit did not, which is its most consequential omission.

### 0.3 Change log against revision 1

| # | Change | Reason |
|---|---|---|
| 1 | SEC-01 escalated: the credential is at HEAD and on `origin`, not merely in history | Blast radius was understated; remediation now requires history rewrite plus force-push coordination |
| 2 | Added §4.1 — the contract checker structurally cannot fail on the open rows | “Keep rows open” was a promise with no enforcement behind it |
| 3 | Added §7.1 — Beta/GA scope fence, resolving the conflict with `ADR-0057` | Rev 1 demanded Q3 work (telemetry rigour, A/A) at the Beta gate, contradicting an accepted ADR |
| 4 | Corrected §13 `REQ-SLICE-001` definition of done | Rev 1 required executing an artifact that `ADR-0047` deleted at S4; the row was conflated with `S5-DC-002` |
| 5 | Added §9.1 — every new gate requires a registered broken counterpart | The repository already enforces `M6` via `test/broken/`; the matrix did not invoke it |
| 6 | Added revocation/kill-switch and secret-in-context rows to §9 | Threat-model items 3 and 1 had no corresponding control |
| 7 | Added §12.1 — RACI, effort bands, and the first five commands | A senior developer could not start from rev 1 on Monday morning |
| 8 | Added §14.0 gate applicability and §16 document control | Gates had no owner, no evidence location, and no sign-off record |

---

## 1. Executive conclusion

The central failure is not absence of code. It is **absence of an end-to-end trust-preserving composition**.

The planned system was a single causal chain:

```text
operator CLI
  -> durable runtime command
  -> episode/model proposes typed effects
  -> kernel authorizes and records intent
  -> rootless sandbox executes effects
  -> privileged diff suspends for externally signed approval
  -> ledger-only resumption issues a descriptor-bound grant
  -> terminal ledger event triggers an exterior evaluator service
  -> evaluator verifies immutable oracle + clean workspace
  -> evidence-plane verdict is persisted and rendered by CLI
```

The implementation currently contains several disconnected chains:

```text
CLI -> scenario/replay/stdin JSONL adapters (no production command transport)

CompositionRoot -> scripted or OpenRouter model -> GitEnvironment -> optional injected verifier

ApprovalFlow -> in-process Boolean callback -> runtime-held HMAC signer -> immediate verification

TelemetryRunner -> model call -> synthetic timing constants
```

This split invalidates the strongest claims in the optimistic review: operational Beta delivery, genuine exteriority, human-held authorization, live correction persistence, passive production telemetry, and real dogfood completion.

### 1.1 What should be retained

- The layered context representation and immutable-prefix construction are a sound starting point.
- The evaluator's oracle-digest probe and fail-closed `inconclusive` result semantics are useful primitives.
- OpenRouter retry, redaction, cassette, and basic accounting behavior are useful adapter foundations.
- The kernel boundary and TCB size checks remain valuable.
- The CLI has a good hexagonal interface direction and useful replay/headless projections.
- The approval challenge's canonical diff/digest binding is a useful primitive once signing ownership is corrected.

### 1.2 What must not be claimed yet

- “OS-isolated evaluator daemon” or verified UID/image exteriority.
- “Human-signed approval” or ledger-only/model-free resumption.
- “Live `vg` product path” for execution, approvals, or corrections.
- “Real first-token latency” or measured sandbox overhead.
- “Real end-to-end dogfood gate.”
- “100% contract completion.” The checker reports assignment/evidence-field coverage, while material Phase 2 rows remain `open`.

---

## 2. Audit evidence and reproducibility

### 2.1 Verification observed on the dirty developer workspace

| Gate | Result | Interpretation |
|---|---:|---|
| Python unit discovery | 335 passed, 2 skipped | Component suite passes; real OpenRouter and real dogfood are skipped |
| CLI Node tests | 12 passed | Scenario/replay/presentation behavior passes; production transport is not exercised |
| `tools/check_boundaries.py` | Pass, 93 files | Import topology check passes; does not prove runtime trust separation |
| `tools/check_tcb_budget.py` | Pass, 1,307 logical LOC | Kernel remains under alarm threshold |
| `tools/run_broken_tests.py` | Pass, 22 counterparts | Includes uncommitted governance fixture in the dirty workspace |
| `tools/check_active_mvp_contract.py` | Pass | Checks registry assignment/evidence structure, not semantic completion of open rows |

### 2.2 Clean-checkout result

A `git archive HEAD` checkout cannot import `vanguard.packages.runtime.root` because `root.py` imports `runtime.governance.approvals`, while `approvals.py` is untracked. `test.runtime.test_composition_root` consequently fails with `ModuleNotFoundError`.

At audit time the workspace contained:

```text
M  test/broken/manifest.json
M  vanguard/packages/runtime/governance/__init__.py
?? test/broken/fixtures/governance/
?? test/runtime/test_approval_flow.py
?? vanguard/packages/runtime/governance/approvals.py
```

Passing dirty-tree tests are therefore not releasable evidence.

### 2.3 Secret incident — SEC-01

A plaintext OpenRouter credential is committed in `.env`. The credential value is deliberately omitted from this document.

**Verified blast radius** (established by inspection, not assumption):

| Question | Finding | Consequence |
|---|---|---|
| Which commit introduced it? | `cddaaa3` | Single introduction point |
| Is it still tracked at HEAD? | **Yes** | Not a historical artifact — it is in the working product |
| Is it on a remote? | **Yes**, `origin/sprint5-6/integration` | Left the machine; must be treated as compromised |
| Is `main` affected? | **No** — `main` is clean | Rewrite is confined to one unmerged branch |
| How many commits touch `.env`? | One | Rewrite is mechanically simple |
| Was `.gitignore` updated? | Yes, in the uncommitted worktree | **Insufficient and dangerous** — it hides the file from `git status` while leaving it tracked |

The last row deserves emphasis: adding `.env` to `.gitignore` while the file remains tracked makes the problem *less* visible without making it smaller. Whoever staged that change likely believed the issue was closed.

The one piece of good news is that `main` is clean and `cddaaa3` exists on exactly one unmerged branch. That converts an unbounded history rewrite into a bounded one, and it is the reason this is recoverable within a day rather than a week.

**Required incident response, in order:**

1. **Revoke at the provider now.** Not rotate — revoke. Assume use by an unknown party from the moment of push. Anyone who ran the suite may also hold it in shell history, CI logs, or a terminal scrollback.
2. Review provider usage and billing logs for the exposure window (`cddaaa3` onward) and record what you find, including "no anomalous use" if that is the finding.
3. Purge from history on the single affected branch and force-push:
   ```bash
   git rm --cached .env && printf '.env\n' >> .gitignore
   git filter-repo --path .env --invert-paths     # or git-filter-branch/BFG
   git push --force-with-lease origin sprint5-6/integration
   ```
4. Notify every clone holder; a stale clone re-pushes the secret. Confirm each has re-synchronised before the branch is considered clean.
5. Commit `.env.example` with the key *name* and no value, so the next developer has a correct path.
6. Add blocking secret scanning to CI **and** a pre-commit hook. A scanner that only runs in CI catches the secret after it has already left the machine.
7. Record the incident and its remediation in `docs/security/` — without recording the secret.

Deleting only the current file, or adding it to `.gitignore`, is insufficient after a secret has been pushed.

**Standing rule going forward:** no credential is ever read from a file in the repository tree. The adapter resolves a *reference* from the process environment at the last responsible moment (§6.1).

---

## 3. Reconciliation of the three developer reports

### 3.1 Assessment of the optimistic report

The optimistic report accurately lists modules and passing component tests, but repeatedly equates **code existence and mocked tests** with **architectural invariant satisfaction**. Its delivery conclusion is not supported.

| Claim | Audit verdict | Reason |
|---|---|---|
| “Phase 2 delivered the Beta MVP” | False | No unified CLI-to-kernel-to-sandbox-to-exterior-evaluator path exists |
| “SB landed” | False as a repository claim | No `[dev-sb]` commit; S6 governance files are untracked; evaluator was swept into a DC commit |
| “Exterior UID 10002 process verified” | False | UID is a constructor expectation; tests override it with the current UID; no daemon/supervisor/image attestation exists |
| “Human authorization verified” | Misleading | Diff binding exists, but runtime owns the signing key and mints the approval after a Boolean callback |
| “Model-free resumption” | Not demonstrated | Root retains in-memory objects and loops; it does not recover solely from a durable ledger after process death |
| “Real dogfood” | False | Scripted operator contains the known patch; Boolean auto-approval; injected suite verifier; live test skipped |
| “Telemetry attaches passively” | False | Telemetry is an orphan tool; no production dispatch attachment was found |
| “Measured sandbox overhead/TTFT” | False | Default timings are constants; TTFT equals full non-streaming request latency |
| “Corrections persisted” | False for live product | Scenario/replay adapters store them in memory; live adapter returns `not_available` |
| “Contract coverage 100%” | Mischaracterized | Assignment/evidence-field coverage passes, while six Phase 2 rows and `REQ-SLICE-001` remain open |
| “Generality verified” | Overstated | `DEFAULT_BINDINGS` hardcodes coding verbs in the composition root |

Its minor findings—reservation propagation and UI cleanup—are valid, but materially under-prioritized relative to the trust-boundary defects.

### 3.2 Assessment of the second, remediation-oriented list

The remediation list supplied after the optimistic report is directionally good but incomplete. It correctly identifies secret cleanup, clean HEAD, external approval ownership, context transport, provider parsing, live CLI transport, and telemetry rigor. It must additionally require:

- supervisor-attested evaluator process/image identity and authenticated IPC;
- rootless sandboxing of all effects;
- durable ledger reconstruction after a killed runtime;
- canonical shared/generated wire contracts;
- genuine streaming for actual TTFT;
- adversarial evaluator, approval, recovery, and transport testing;
- a real, independently selected dogfood task before contract closure;
- evidence governance that prevents status changes before immutable receipts exist.

Its proposed final step must be reversed: **do not mark rows covered as a task in itself**. Status becomes `covered` only after the associated closure gate passes and evidence is sealed.

### 3.3 Assessment of the third report

The third report is substantially aligned with this audit. It correctly identifies the two-runtime split, scripted dogfood, non-attested evaluator identity, absent correction persistence, integration hygiene, optional context compilation, duplicated approval concepts, hardcoded bindings, and orphan telemetry.

One precision correction: `LedgerBridge` event IDs are UUIDv7-*shaped* and pass the current regular expression because the version and variant nibbles are fixed appropriately. However, they are minted from a fixed prefix plus sequence rather than a standards-compliant UUIDv7 timestamp/random generator. The design remains unacceptable for production uniqueness and temporal semantics, but “not syntactically UUIDv7” is too strong.

---

## 4. Requirements and delivery status

| Requirement | Planned result | Current result | Closure state |
|---|---|---|---|
| `REQ-CTX-001` | Mandatory L1–L5 prefix-stable context for the product path | Compiler exists; composition wrapper is optional; episode view is not sent by OpenRouter | Open |
| `REQ-EVAL-001` | Exterior daemon, dedicated UID/image, ledger observation, double probes | Probe primitives exist; no exterior daemon, attestation, or product wiring | Open |
| `REQ-PORT-006` | Resilient OpenRouter adapter | Mostly implemented; parsing/secret/streaming gaps remain | Covered row should be re-audited |
| `REQ-SLICE-001` | Real disposable-key execution receipt | Optional live test skipped; no sealed receipt | Open |
| `REQ-CLI-001` | Live EventEnvelope client stream | Passive stdin parsing exists; production control transport absent | Partial; current “covered” meaning is narrower than product claim |
| `REQ-APP-001` | Exact descriptor-bound, human-signed privileged approval | Canonical binding primitive exists; signer boundary and durable resumption absent | Open |
| `REQ-CLI-002` | Live approval/correction operator surface | UI exists; live methods unavailable; corrections not ledger-persisted | Open |
| `REQ-DOG-001` | Real repository bug fixed through complete product path | Scripted wiring test; live provider test skipped; no exterior evaluator/sandbox/live CLI | Open |
| `REQ-BENCH-001` | Sprint 6 telemetry program | Referenced by packet and commit but absent from registry | Governance defect; define before implementation acceptance |

`S5-INT-001` has no credible integration evidence. Commit ownership is contaminated: commit `f1008d8`, labeled S6 DC telemetry, includes evaluator implementation/tests, context tests, Sprint 6 documentation, and unrelated `runtime_jit.py` changes.

### 4.1 Enforcement gap — the contract gate cannot currently fail

`tools/check_active_mvp_contract.py` forces a row to `covered` or `justified` **only when its `component` appears in `merged_components`**:

```python
if row.get("component") in merged:
    merged_rows += 1
    if status in {"covered", "justified"}: merged_complete += 1
    else: errors.append(f"{label}: merged component requirement remains open")
```

None of the six open components — `agency/context`, `adapters/evaluators`, `runtime/governance-approval`, `client/cli-tui`, `runtime/composition`, `slice/e2e` — is in that list. The checker therefore prints `CONTRACT PASS` today and would keep printing it if the rows stayed open until the heat death of the universe.

This matters more than it first appears. This audit's central instruction is *"keep the affected rows open"* (§15). That instruction is currently enforced by nothing but goodwill, and the previous review's proposal to *"mark rows covered as a final task"* would have passed CI unchallenged. **Both the discipline and its violation are invisible to the gate.**

**Required, and cheap — do it in Workstream A:** add the five Wave 2 components to `merged_components`, then run the checker and *observe it fail with five errors*. If it passes, the amendment did not take effect. A gate whose failure mode has never been observed is not a gate (`M6`); this is the repository's own doctrine applied to its own governance tooling.

Two further registry defects:

- `TEST-SLICE-001` is registered as `npm --workspace @vanguard/disposable-slice test`. That workspace was deleted at S4. The command cannot run, so the row can never move on evidence — a gate that cannot fail *or* pass.
- `TEST-APP-001` and `TEST-DOG-001` both resolve to `python3 -m unittest discover -s test/runtime`. Two contract rows gated by one command means neither is independently falsifiable; a regression in approvals and a regression in composition are indistinguishable to the registry.

---

## 5. Threat model for the Beta MVP

The repair design must assume the following adversaries and failures:

1. **Compromised model output:** arbitrary tool names, malformed arguments, prompt injection, attempts to widen scope, replay approvals, or modify evaluator inputs.
2. **Compromised workspace:** malicious repository hooks, symlinks, import shadowing, generated files, `PATH` manipulation, test replacement, or process escape attempts.
3. **Compromised episode/runtime process:** attempts to self-approve, fabricate evidence, invoke evaluator internals, or mutate ledger history.
4. **Malicious or confused client:** approval transplant, stale decision replay, wrong tenant/run, expired signature, reordered commands, or duplicate submissions.
5. **Evaluator failure or compromise:** timeout, socket truncation, image mismatch, wrong UID, test oracle alteration, or polluted import graph.
6. **Provider failure:** rate limiting, malformed JSON, inconsistent usage, partial streams, secret leakage, price drift, or replay mismatch.
7. **Crash and concurrency:** process death between intent/effect/receipt, duplicate delivery, stale reservations, resumption races, and ledger projection lag.
8. **Supply-chain compromise:** poisoned dependency, build artifact mismatch, mutable base image, or exposed CI secret.

Security properties required:

- **Authority separation:** model, runtime, human approver, effect executor, and evaluator possess distinct authorities.
- **Complete mediation:** every effect, approval, and verdict crosses its required port and is recorded.
- **Descriptor integrity:** approvals and grants bind canonical bytes, scope, principal, run, expiry, nonce, and policy version.
- **Exterior evidence:** the evaluated subject cannot produce or modify its own verdict or oracle.
- **Fail-closed uncertainty:** missing or ambiguous evidence produces `inconclusive`, never success.
- **Replay safety:** commands are idempotent and uniquely correlated; stale or duplicated approvals cannot execute effects twice.
- **Reconstructability:** authoritative state is derivable from the ledger after process loss without model inference.

---

## 6. Critical defect analysis and required designs

### 6.1 SEC-01 — committed provider credential

**Severity:** Critical / immediate incident.  
**Impact:** unauthorized provider use, financial loss, data exposure, and permanent repository-history contamination.  
**Required design:** secret reference only. Resolve the credential at the last responsible moment in the outbound adapter; never copy the environment mapping or serialize credentials. Redaction is defense-in-depth, not permission to retain the secret.

**Acceptance evidence:** provider revocation receipt; history scan of all refs; CI secret scanner negative; adapter object graph test recursively proves the credential value is absent; logs/cassettes/error messages tested for redaction.

### 6.2 REL-01 — HEAD is not reproducible

**Severity:** Critical release blocker.  
**Impact:** tests pass only because untracked files fill dependencies; CI and consumers receive a broken graph.  
**Required design:** atomic integration commits with explicit dependency ordering. CI must build from a fresh clone/archive, reject dirty-tree evidence, and run import smoke tests before unit tests.

**Acceptance evidence:** exact commit SHA builds in a clean container with no bind-mounted source, no untracked files, and no developer-local environment dependencies.

### 6.3 ARCH-01 — two unconnected runtimes

**Severity:** Critical product defect.  
**Impact:** the UI can demonstrate scenario data while the kernel runtime runs through a separate Python API; operator actions cannot govern the real effects.

**Target design:** one versioned `RuntimeService` boundary. A local Beta may use Unix domain sockets or framed stdio, provided command and event semantics are transport-independent.

Required operations:

```text
StartRun -> CommandAccepted(runId, commandId)
StreamEvents(cursor) -> ordered EventEnvelope stream
ResolveApproval(signedDecision) -> idempotent receipt
RecordCorrection(correction) -> durable receipt
Cancel / Checkpoint / Resume -> durable command receipt
GetRun / ExplainArtifact -> ledger projection
```

The CLI must never default to a scenario adapter in a production command. Demo mode must be explicit and visibly labeled.

### 6.4 EVAL-01 — evaluator exteriority is nominal

**Severity:** Critical security defect.  
**Impact:** the runtime can invoke an arbitrary injected verifier in its own authority domain; UID/image claims are unverified configuration.

**Target design:** an evaluator supervisor starts a separately packaged immutable evaluator service under a dedicated OS identity. The runtime has only an `EvaluatorClientPort`; it cannot import evaluator implementation code or execute evaluator tests directly.

Minimum protocol:

1. Evaluator subscribes to or receives a signed reference to a terminal ledger event.
2. Request contains run, workspace snapshot/content digest, oracle-manifest digest, evaluator image digest, protocol version, and nonce.
3. Authenticated local IPC binds peer identity. On Linux, verify peer credentials (`SO_PEERCRED`) in addition to application authentication.
4. Supervisor attests actual executable/image digest and UID; these are observed facts, not caller arguments.
5. Evaluator mounts the candidate workspace read-only where possible and oracle material from a separately sealed source.
6. Probe 1 verifies every oracle byte against the preregistered manifest.
7. Probe 2 verifies the complete evaluation import/execution closure, not a filename blacklist. Reject untracked executable inputs, path shadowing, hooks, `.pth`, customizations, altered lockfiles where relevant, unsafe symlinks, and unexpected environment variables.
8. Verdict is signed or MACed by evaluator authority and appended through `Principal::EvidencePlane`.
9. Timeout, crash, peer mismatch, malformed response, missing receipt, or probe ambiguity produces `inconclusive`.

Do not “fix” development by setting `expected_uid=os.getuid()`. Provide a deliberate non-production fake adapter with an unmistakable evidence label, while release gates require the real isolated deployment.

### 6.5 GOV-01 — runtime-held approval signer

**Severity:** Critical authorization defect.  
**Impact:** runtime can manufacture the signature that supposedly constrains it; a Boolean callback is not cryptographic human authorization.

**Target design:** asymmetric signatures are preferred over a shared HMAC for production separation. The human client or an external approval service holds a private key; runtime stores only trusted public keys/key references.

The canonical signed object must include at least:

```text
schemaVersion
approvalId / nonce
tenantId, ownerId, runId, processId
principal and reviewer identity
action and resource scope
canonical argsDigest
descriptorDigest
policyVersion
requested reservation / budget dimensions
issuedAt, expiresAt
challenge ledger event ID
```

Flow:

1. Kernel persists intent and emits `ApprovalRequested` containing the exact normalized diff and digests.
2. CLI renders those exact bytes and signs the canonical challenge externally.
3. Runtime persists `ApprovalResolved` before execution.
4. Kernel verifies signature, nonce, expiry, identity, scope, current request digest, and unused status at S1.
5. Issued grant records `approvalRef` and the original reservation.
6. Effect execution and receipt are idempotently correlated to the approved request.
7. Restarted runtime reconstructs the process solely from ledger events.

Reject altered whitespace after canonicalization, stale signatures, cross-run transplant, duplicate use, key revocation, missing signer, wrong tenant, and altered reservation.

### 6.6 SBOX-01 — effects execute without the promised rootless perimeter

**Severity:** Critical Beta blocker.  
**Impact:** model-driven commands and repository code can act with developer-host authority.

**Target design:** route all non-pure effects through `RootlessSandboxRunner`. A Beta baseline may use bubblewrap/rootless OCI with:

- explicit read-only/read-write mount allowlists;
- isolated PID, mount, user, IPC, and network namespaces where supported;
- network denied by default and host allowlists when explicitly granted;
- sanitized environment and controlled `PATH`;
- CPU, memory, process, wall-time, output, and disk quotas;
- no host Docker socket, SSH agent, credential directories, or inherited secrets;
- deterministic teardown and signed execution receipt;
- platform capability detection that fails closed rather than silently dropping isolation.

MicroVM/gVisor may be evaluated later, but Phase 2 cannot claim isolation while using direct host subprocesses.

### 6.7 REC-01 — resumption is not ledger-only

**Severity:** High.  
**Impact:** correctness depends on retained Python/model objects; crashes can lose or duplicate privileged operations.

**Required design:** persist process state transitions, challenge, decision, reservation, effect intent, idempotency key, and receipt. Kill the runtime after each transition in tests. On restart, projections determine the sole legal next action without calling an LLM for an already approved request.

### 6.8 CTX-01 — compiled context is not the authoritative model input

**Severity:** High functional defect.  
**Impact:** OpenRouter consumes `messages`, while the composition wrapper adds `episodeView` separately. Tool observations may never reach later provider calls. Other callers can bypass the compiler entirely.

**Required design:** define one canonical `ModelInvocation` structure generated by the context compiler and consumed by every production `ModelPort`. L1–L3 immutability and pre-action prior recording must be enforced at the composition boundary, not by an optional wrapper.

Use the provider tokenizer or a conservative tokenizer-specific upper bound. Persist token estimator/tokenizer version in telemetry. Explicitly map tool results into L5 messages with provenance, truncation decisions, result digests, and confidentiality filtering.

### 6.9 CLI-01 — live transport and schema drift

**Severity:** High product blocker.  
**Impact:** live commands return `not_available`; cursor fields are ignored; parser casts partially validated input; independently reimplemented types have drifted (`principalRole`, `branchId`).

**Required design:** generate Python and TypeScript wire models from one versioned schema or enforce bidirectional golden conformance. Parser boundaries validate all required fields, UUID/version constraints, scope rules, labels, and extension policy before constructing domain types.

Transport must implement:

- monotonic per-stream sequence and cursor resume;
- idempotent command IDs;
- reconnect with bounded exponential backoff;
- duplicate suppression and gap detection;
- explicit terminal and transport-error events;
- bounded buffering/backpressure;
- cancellation and graceful shutdown;
- authentication/peer authorization for the local service.

Correction records must be appended to the ledger with the actual accepted patch digest. Replay is read-only; it must not pretend to persist new corrections.

### 6.10 TEL-01 — telemetry lacks measurement integrity

**Severity:** High scientific-validity defect.  
**Impact:** synthetic constants are indistinguishable from observations; “TTFT” is full response time; errors are counted without explicit uncertainty; float money/durations violate CT-06/CT-07.

**Required design:** production telemetry derives from monotonic timestamps at actual lifecycle boundaries. Store integer milliseconds or finer integer units and integer currency micros. Every observation includes instrument tuple, model/provider version, tokenizer/pricing version, sandbox/evaluator image digests, cassette/live label, error status, and clock source.

Synthetic benchmarks are allowed only when marked `synthetic=true` and excluded from release performance claims. True TTFT requires streaming and timestamping the first validated provider event. Report failure and inconclusive rates alongside latency distributions; never silently drop or reinterpret failures.

Define `REQ-BENCH-001` before accepting telemetry against it. Support A/A calibration rather than rejecting identical treatments outright, paired outcomes, uncertainty intervals, and preregistered exclusion rules.

### 6.11 EVT-01 — event identity and bridge fragmentation

**Severity:** Medium-high long-term integrity risk.  
**Impact:** `LedgerBridge` wraps internal events into a second event representation and constructs fixed-prefix IDs. CLI does not consume this production bridge, and causal/audit semantics can diverge.

**Required design:** one authoritative event factory with real UUIDv7 generation, durable per-stream sequence allocation, causal parent linkage, and canonical serialization. Internal kernel events may remain internal, but their projection into `EventEnvelope` must be explicit, deterministic where required, collision-safe, and covered by cross-language conformance tests.

### 6.12 ARCH-02 — hardcoded bindings and duplicated governance concepts

**Severity:** Medium-high extensibility risk.  
**Impact:** `DEFAULT_BINDINGS` embeds coding verbs in Python; S3 `ProcessEngine` and S6 `ApprovalFlow` have overlapping lifecycle responsibilities.

**Required design:** manifests select registered capabilities; an injected adapter registry maps stable capability identifiers to implementations at the composition edge. Unknown capabilities fail closed. Consolidate governance around one event-sourced process state machine, with approval verification as a policy/service used by that engine rather than an independent lifecycle.

---

## 7. Target Beta architecture

```text
┌──────────────────────── Operator authority ────────────────────────┐
│ vg CLI: generated contracts, diff renderer, private signing key    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ authenticated command/event protocol
┌──────────────────────── Runtime authority ─────────────────────────┐
│ RuntimeService                                                     │
│  ├─ durable command inbox + idempotency                             │
│  ├─ event-sourced ProcessEngine                                    │
│  ├─ ContextCompiler -> streaming ModelPort                         │
│  ├─ Kernel dispatch S0–S12                                         │
│  ├─ ApprovalVerifier (public keys only)                             │
│  └─ SQLite EventStore + projections                                │
└───────────────────────┬───────────────────┬─────────────────────────┘
                        │                   │ terminal event/reference
             typed effect request          │
┌──────────────── Effect authority ─────┐   │  ┌──── Evidence authority ─────┐
│ RootlessSandboxRunner                 │   └─>│ Evaluator daemon/supervisor  │
│ restricted mounts/net/resources       │      │ UID/image/peer attestation   │
│ idempotent execution receipts         │      │ sealed oracle + double probe │
└───────────────────────────────────────┘      │ signed evidence verdict      │
                                               └──────────────────────────────┘
```

No component should possess enough authority to propose, approve, execute, and verify the same effect.

### 7.1 Beta scope fence — what this program will and will not deliver

The architecture above is the **destination**. Beta is a waypoint on the way to it, and conflating the two is how a remediation program becomes unschedulable.

`ADR-0057` scopes Beta to Chapter 10 **Q1 + Q2** and explicitly places TableWorld and A/A measurement outside it. Sections 6.10, 8-F and 14-R8 of this audit demand telemetry rigour, A/A calibration and paired trials — that is **Q3**, deferred by an accepted ADR to S7–S9. Left unreconciled, an engineer reading this document is instructed to satisfy a gate that governance has already deferred.

**Ruling (Tech Lead + Project Lead, requires your countersignature):** `ADR-0057` stands. Q3 and Q4 remain out of Beta. The measurement findings in §6.10 are real defects and stay in this report, but they are **GA-blocking**, not Beta-blocking, with one exception carved out below.

| # | Finding | Beta | GA | Rationale for the split |
|---|---|:---:|:---:|---|
| SEC-01 | Committed credential | ● | ● | Active harm. Blocks everything. |
| REL-01 | HEAD not reproducible | ● | ● | Nothing below can be evidenced without it. |
| §4.1 | Contract gate cannot fail | ● | ● | Without it every other closure is unenforced. |
| GOV-01 | Runtime holds the approval signer | ● | ● | Q1 *is* "is the boundary real?". A runtime that mints its own approvals has no boundary. |
| EVAL-01 | Evaluator exteriority nominal | ● | ● | Same: `M5` is the load-bearing claim of the whole thesis. |
| SBOX-01 | Effects bypass the sandbox | ● | ● | Q1. Also the only control standing between the tool and the operator's laptop. |
| ARCH-01 | Two unconnected runtimes | ● | ● | Q2 asks "would you reach for it?" — unanswerable without one product path. |
| CLI-01 | Live transport absent | ● | ● | Same as ARCH-01; they are one deliverable. |
| REC-01 | Resumption not ledger-only | ● | ● | An approval that a crash can duplicate is not an approval. |
| CTX-01 | Compiled context not authoritative | ● | ● | A model that cannot see its own tool output cannot fix a second bug. Q2. |
| TEL-01 | Synthetic values indistinguishable from measured | ◐ | ● | **Carve-out:** the *labelling* half is Beta-blocking — a synthetic number that can be mistaken for a measurement is a false claim, and false claims are what this audit exists to prevent. The *rigour* half (A/A floors, paired trials, confidence intervals) is Q3 and waits. |
| EVT-01 | Event identity / bridge fragmentation | ◐ | ● | Real UUIDv7 and one bridge are Beta (cheap, and duplicate IDs corrupt the evidence bundle). Cross-language conformance generation is GA. |
| ARCH-02 | Hardcoded bindings, duplicated governance | ○ | ● | Q4 (generality) is explicitly deferred. Record the debt; do not refactor during a closure wave (`M9`). |
| §11.5 | SBOM, signed artifacts, pinned images | ○ | ● | No external consumers exist yet. Real, not now. |

● Blocking ◐ Partially blocking (see rationale) ○ Deferred with recorded debt

**Explicitly out of scope for Beta**, to be written into the plan so that nobody quietly adds them back:

- microVM or gVisor isolation (bubblewrap/rootless OCI is the Beta baseline);
- generated cross-language wire contracts (golden round-trip conformance tests suffice);
- key rotation infrastructure and revocation lists (one operator key, manual revocation, documented);
- SBOM, provenance attestation, signed release artifacts;
- A/A floors, paired trials, preregistered statistical protocols;
- non-coding environments and the generality falsifier.

**Why draw the fence here.** Every item on the blocking side is one where *shipping without it would require stating something untrue* — that effects are isolated, that a human authorised the patch, that evidence is exterior, that the tool works end to end. Every item on the deferred side is one where the honest statement is simply "not yet", which a Beta is entitled to say. That is the test applied to each row, and it is the test to apply to anything anyone proposes adding later.

---

## 8. Corrective implementation program

### Workstream A — incident and reproducible baseline

**A1. Credential containment**  
Revoke, investigate, purge history, rotate, add scanners and safe examples.

**A2. Atomic clean-tree integration**  
Integrate governance code/tests deliberately; disentangle unrelated commit content where practical; require clean-clone CI.

**A3. Contract repair**  
Create or remove `REQ-BENCH-001` through the governance process. Clarify `REQ-CLI-001` client-only versus production-live scope. Keep incomplete rows open.

**Exit gate A:** no known secrets in any reachable ref; clean checkout imports and passes baseline gates; registry has no dangling requirement references.

### Workstream B — trusted execution and evidence perimeter

**B1. Rootless effect runner**  
Implement and require sandbox profiles for every effect binding.

**B2. Exterior evaluator service**  
Package daemon, supervisor, peer authentication, attestation, ledger trigger, sealed oracle, comprehensive non-pollution probe.

**B3. Evidence receipts**  
Persist evaluator identity, image digest, input snapshot, oracle manifest, probe results, timestamps, verdict, and signature.

**Exit gate B:** adversarial tests prove the episode/runtime cannot forge a pass, execute evaluator internals, modify oracle inputs, or silently fall back to host execution.

### Workstream C — governance and crash-safe resumption

**C1. External signer**  
Adopt asymmetric operator signatures or a genuinely external approval service; remove runtime signing key and default secret.

**C2. Unified process state machine**  
Reconcile `ProcessEngine` and `ApprovalFlow`; define event transitions and illegal states.

**C3. Durable resumption and reservation**  
Preserve original reservation; bind it in the signature; attach approval reference to grant; recover after process death.

**Exit gate C:** approval transplant, mutation, replay, expiry, revocation, wrong-tenant, wrong-budget, and crash-window tests all fail closed; valid approval resumes once without an LLM call.

### Workstream D — one live product path

**D1. Runtime service protocol**  
Implement authenticated IPC/stdio server and production CLI adapter.

**D2. Generated wire contracts**  
Eliminate hand-maintained client drift; add Python/TypeScript golden round trips.

**D3. Durable approvals and corrections**  
Render exact challenge; submit signature; append corrections and command receipts to ledger.

**D4. Event identity/cursor semantics**  
Centralize UUIDv7 generation, sequence allocation, reconnect, gap, and duplicate behavior.

**Exit gate D:** an operator can start, observe, approve, correct, disconnect, reconnect, and inspect a real kernel run using `vg`, with no scenario adapter.

### Workstream E — model/context correctness

**E1. Canonical model invocation**  
Make compiler output mandatory and include tool observations in L5.

**E2. Streaming OpenRouter adapter**  
Typed incremental parsing, real TTFT, bounded retries, cancellation, redaction, and fail-closed malformed payload handling.

**E3. Token/cost rigor**  
Provider/tokenizer-versioned accounting, integer currency, explicit unknown pricing, and cassette parity.

**Exit gate E:** a non-scripted model can inspect an unknown file, observe tool output on the next turn, propose a valid patch, and produce fully attributed streaming usage without exposing secrets.

### Workstream F — scientific telemetry

**F1. Runtime instrumentation**  
Measure actual event boundaries using monotonic clocks and integer units.

**F2. Measurement validity**  
Separate live, cassette, and synthetic results; report failures and instrument uncertainty.

**F3. Comparative methodology**  
Instrument-tuple validation, A/A floor, paired trials, preregistered tasks, confidence intervals, and immutable summaries.

**Exit gate F:** repeated calibration demonstrates expected A/A behavior; no synthetic value can be mistaken for a live measurement.

### Workstream G — genuine dogfood and release evidence

**G1. Preregister an unknown task**  
Select a real single-file defect unknown to the model cassette and freeze starting commit, tests, policy, budgets, images, and oracle hashes.

**G2. Execute through the sole product path**  
`vg` starts the runtime; real model diagnoses; sandbox executes observations; human externally signs exact diff; restart occurs during suspension; ledger resumes; exterior evaluator verifies.

**G3. Seal the evidence bundle**  
Include commit IDs, manifests, image digests, provider/model version, ledger export, approval signature, effect receipts, evaluator receipt, test output, telemetry classification, and final repository diff.

**Exit gate G:** independent reviewer can replay projections and verify every authority transition without trusting screenshots, model claims, or mutable developer files.

---

## 9. Mandatory adversarial test matrix

| Area | Required must-fail case | Expected result |
|---|---|---|
| Secret handling | Credential appears anywhere in adapter object graph/log/cassette | Test fails; release blocked |
| Approval | One-byte diff change after signing | `MF-GOV-001`, no grant/effect |
| Approval | Same signature used for another run/resource/tenant | Rejected |
| Approval | Replay same approval/effect command | Single execution; idempotent receipt |
| Approval | Expired/revoked/unknown signer | Rejected |
| Reservation | Budget changed after signing | Rejected |
| Recovery | Kill before/after decision, grant, effect, receipt | Deterministic recovery; no duplicate effect |
| Evaluator | Wrong UID, peer, executable, or image digest | `inconclusive`, never pass |
| Evaluator | Oracle changed, added, removed, symlinked | Tampered/fail closed |
| Evaluator | Arbitrary import-shadow module or hook added | Pollution/fail closed |
| Evaluator | Socket truncation, timeout, malformed verdict | `inconclusive` |
| Sandbox | Attempt host secret/home/socket access | Denied and receipted |
| Sandbox | Network attempt without capability | Denied |
| Model | Malformed tool JSON/usage/stream fragment | Typed instrument failure; no effect |
| Context | Tool observation required for second-turn answer | Observation present with provenance |
| CLI | Disconnect, duplicate frames, sequence gap | Resume/deduplicate or explicit failure |
| CLI | Invalid envelope field/type/scope | Rejected before domain construction |
| Telemetry | Model failure or evaluator inconclusive | Counted explicitly, never success latency only |
| Telemetry | Synthetic timing enters live report | Schema/policy rejection |
| Revocation | Capability revoked mid-run; runtime attempts a further effect | Denied, `CapabilityRevoked` recorded, run terminates (`VG-03 §3`) |
| Revocation | Kill switch during a suspended approval | No effect executes on resume; state is reconstructable |
| Secrets | Credential reachable from a compiled context, ledger payload, or event envelope | Test fails; `REQ-TRUST-001` forbids secrets in events |
| Secrets | Credential present in a cassette, error message, or telemetry record | Redaction test fails; release blocked |
| Context | Compiled context bypassed by any production model call | Composition-boundary test fails |
| Governance | Contract row set to `covered` without a sealed gate receipt | `check_active_mvp_contract.py` rejects (Gate R10) |

### 9.1 Every new gate needs a registered broken counterpart

The repository already enforces `M6` mechanically: `test/broken/` holds deliberately defective implementations and `tools/run_broken_tests.py` asserts each one is observed *failing*. Twenty-two counterparts exist today.

**This matrix is not satisfied by a passing test.** Each row above must ship with an entry in `test/broken/manifest.json` whose defective counterpart is observed failing — otherwise a reviewer cannot distinguish a control that works from a control that is unreachable. That distinction is not hypothetical here: `VG-03 §6.5` records a prior injection defence in this very codebase that passed review, had a test, and was dead code for a year.

Concretely, for each of Workstreams B, C, D and E:

1. Write the adversarial test and watch it **fail** against the current implementation.
2. Implement the control until it passes.
3. Add the broken counterpart to `test/broken/manifest.json`.
4. Confirm `tools/run_broken_tests.py` reports the new counterpart failing.

A workstream exit gate is not met until step 4 is green. Reviewers should reject any exit-gate claim whose counterpart count did not increase.

---

## 10. Data, API, and schema decisions required

Before implementation, record focused ADRs for:

1. Runtime command/event transport and authentication.
2. External approval signature algorithm, key lifecycle, and revocation.
3. Canonical descriptor/diff serialization and versioning.
4. Evaluator deployment, supervisor attestation, and evidence signature.
5. Sandbox backend and degraded-platform policy.
6. Event ID/sequence allocation and idempotency semantics.
7. Unified process/approval state machine.
8. Generated cross-language contract source of truth.
9. Telemetry unit types, instrument tuple, and live/synthetic labeling.
10. Dogfood evidence bundle and independent sign-off.

Avoid framework-scale abstractions. Each ADR should define authority ownership, failure semantics, compatibility/versioning, and must-fail tests.

---

## 11. Engineering quality and long-term maintainability

### 11.1 Dependency direction

Keep the kernel free of OpenRouter, CLI, Git, sandbox, and evaluator imports. Composition may know concrete adapters, but it should consume an injected registry rather than encode domain capability policy in `DEFAULT_BINDINGS`.

### 11.2 One concept, one authoritative implementation

- One event envelope parser/factory per language, generated or mechanically conformed.
- One governance process state machine.
- One canonical model invocation builder.
- One runtime service used by CLI and tests.
- One evaluator protocol used by production and integration tests.

Fakes should implement the same ports and carry explicit `fake`/`synthetic` evidence labels. Tests must not use fakes while naming their result “real.”

### 11.3 Numeric and temporal correctness

Adopt integer micros for currency and integer nanoseconds/microseconds/milliseconds for duration according to contract. Use monotonic clocks for intervals and UTC wall clocks only for event timestamps. Record clock source and rounding policy.

### 11.4 Error taxonomy

Separate:

- task failure;
- policy denial;
- approval rejection/expiry;
- effect execution failure;
- instrument failure;
- evaluator `inconclusive`;
- transport interruption;
- malformed external input;
- internal invariant violation.

No broad exception handler should silently map programmer defects to normal retry behavior.

### 11.5 Supply-chain and release hygiene

- Pin dependencies and base images by digest.
- Produce SBOM and provenance attestations.
- Run SAST, dependency, license, and secret scans.
- Build artifacts from protected CI, not developer workspaces.
- Sign release artifacts and publish checksums.
- Maintain migration and rollback plans for ledger/schema versions.

---

## 12. Recommended sequencing and ownership

| Priority | Deliverable | Dependency | Suggested owner profile |
|---:|---|---|---|
| P0 | Credential incident closure | None | Security/release lead |
| P0 | Clean, atomic, bootable HEAD | None | Integration lead |
| P0 | Contract registry reconciliation | None | Tech lead + verification owner |
| P1 | Rootless effect perimeter | Clean baseline | Systems/security |
| P1 | Exterior evaluator daemon/protocol | Sandbox and event decisions | Systems/security |
| P1 | External approval + ledger recovery | Contract/state-machine ADR | Governance/security |
| P1 | Runtime service + live CLI | Wire/transport ADR | Runtime + client owners |
| P1 | Mandatory context/model invocation | Runtime product path | Agency/model owners |
| P2 | Streaming/provider hardening | Model invocation | Adapter owner |
| P2 | Real telemetry | Runtime lifecycle events | Measurement owner |
| P2 | Genuine dogfood | All P1 and relevant P2 | Independent integration team |
| P3 | Packaging and Beta release | Dogfood evidence accepted | Release engineering |

Parallel work is appropriate after ADR boundaries are fixed, but final integration must be serialized through one protected branch with clean-tree evidence.

### 12.1 Execution plan — what a developer does on day one

Rev 1 described the destination without a first step. This section is the on-ramp.

**Effort bands** are calendar-days for one competent senior developer, assuming ADR decisions arrive without delay. They are estimates for sequencing, not commitments.

| Seq | Work | Band | Blocks | Gate |
|---:|---|---:|---|---|
| 1 | SEC-01 credential incident | 0.5 d | everything | R0 |
| 2 | REL-01 clean atomic HEAD | 0.5 d | everything | R1 |
| 3 | §4.1 contract-gate enforcement + registry repair | 0.5 d | R10 | R1 |
| 4 | ADRs 1–10 (§10) written and accepted | 2 d | B, C, D | — |
| 5 | SBOX-01 rootless effect perimeter | 4 d | dogfood | R3 |
| 6 | EVAL-01 evaluator daemon + supervisor + IPC | 6 d | dogfood | R4 |
| 7 | GOV-01 external signer + REC-01 ledger resumption | 6 d | dogfood | R5 |
| 8 | ARCH-01 + CLI-01 runtime service and live CLI | 8 d | dogfood | R6 |
| 9 | CTX-01 canonical model invocation + streaming | 4 d | dogfood | R7 |
| 10 | TEL-01 labelling carve-out only (§7.1) | 1 d | — | R8 (partial) |
| 11 | Dogfood ×3 through the sole product path | 3 d | release | R9 |
| 12 | Contract closure and Beta tag | 1 d | — | R10 |

Sequence 1–3 is one day and unblocks everything; treat it as a single sitting. Items 5–9 may run in parallel across owners **only after** item 4, and they must land through one protected branch.

**Ownership.** With the current team, one person is Responsible for each numbered item, the Tech Lead is Accountable for all of them, and the Project Lead is the sole approver of Gates R9 and R10. Explicitly: **the person who wrote a control may not sign off its gate.** For item 11 the independent reviewer must be someone who did not implement items 5–9 — if the team is too small for that, the reviewer is the Project Lead and that fact is recorded in the evidence bundle rather than glossed.

**The first five commands.** Run them in this order, before writing any code:

```bash
# 1. Revoke the key at the provider first (browser, not shell). Then:
git rm --cached .env && printf '.env\n' >> .gitignore

# 2. Prove the branch is not held together by one machine's working tree
git clone . /tmp/vg-clean && cd /tmp/vg-clean && python3 -m unittest discover -s test
#    Expect: ModuleNotFoundError on runtime.governance.approvals. That failure IS finding REL-01.

# 3. Commit lane SB's orphaned governance work, then repeat step 2 until green
git add vanguard/packages/runtime/governance/ test/runtime/test_approval_flow.py \
        test/broken/fixtures/governance/ test/broken/manifest.json

# 4. Make the contract gate able to fail (§4.1): add the five Wave 2 components
#    to merged_components, then:
python3 tools/check_active_mvp_contract.py
#    Expect: five "merged component requirement remains open" errors.
#    If this PASSES, the amendment did not take effect. Do not proceed.

# 5. Re-seal the baseline manifest with a provenance record, then confirm the full gate set
python3 tools/check_baseline_manifest.py && python3 tools/run_broken_tests.py
```

Steps 2 and 4 are designed to **fail**. A developer who reports them passing on the first attempt has not performed them. This is the same discipline the codebase applies to its own controls, turned on the remediation program itself.

---

## 13. Definition of done by contract row

### `REQ-CTX-001`

- Every production model call originates from the compiler.
- L1–L3 identity remains stable across turns.
- L5 contains actual tool observations with provenance.
- Token limit cannot be undercounted beyond documented safety margin.
- Competence prior precedes first provider call and cannot be overwritten.

### `REQ-EVAL-001`

- Separate process/service, dedicated observed UID, attested immutable image.
- Triggered from terminal ledger evidence, not direct episode authority.
- Complete double probes with sealed oracle and execution-closure pollution detection.
- Authenticated response and `inconclusive` on all uncertainty.

### `REQ-APP-001`

- External human/operator authority signs exact canonical descriptor.
- Runtime holds verification authority only.
- Challenge and resolution durable; grant references approval.
- Restart resumes exactly once without model involvement.

### `REQ-CLI-002`

- Production `vg` communicates with runtime service.
- Exact diff rendered and signed.
- Correction with actual accepted digest is ledger-persisted.
- Cursor recovery, ordering, duplicate handling, and schema conformance tested.

### `REQ-DOG-001`

- Unknown real defect, real provider, real CLI, sandboxed effects, external approval, restart recovery, exterior evaluator.
- Zero manual source edits.
- Sealed, independently reviewable evidence bundle.

### `REQ-SLICE-001` — corrected in revision 2

Revision 1 required executing a disposable live slice. **That is not satisfiable and the requirement never asked for it.** The row's own normative statement reads: *"A disposable end-to-end slice … remains unimportable by production code, **and is deleted at S4**."* Deletion is the acceptance criterion. `ADR-0047` deleted it on schedule; the registered command points at a workspace that no longer exists.

Revision 1 conflated this row with backlog ticket `S5-DC-002` ("live disposable key test execution receipt"), which is a *different* piece of work that happens to cite the same row — itself a governance defect worth recording.

**Tech Lead ruling required. Two admissible options; option A is recommended:**

**Option A — close as `justified` (recommended).** The artifact did what it was for and was removed by design.
- `justification`: the slice was disposable by construction and deleted at S4 per `ADR-0047`; a deleted artifact cannot carry a running test.
- `compensating_assurance`: `tools/check_boundaries.py` proves zero production imports of `slice/`; the same vertical path (prompt → model → patch → approval → apply → test → result) is now permanently covered by `TEST-DOG-001` under Gate R9.
- Re-point `TEST-SLICE-001` at `python3 tools/check_boundaries.py`, which is the surviving falsifiable evidence.

**Option B — amend the row.** Rewrite the statement to describe the live-provider receipt that `S5-DC-002` actually intends, give it a new registered command, and keep it `open` until Gate R7 produces that receipt. This is honest but creates a new requirement under an old identifier, which the archaeology trail will have to explain forever.

What is **not** admissible is leaving the row `open` against a command that can neither pass nor fail.

### `REQ-BENCH-001`

- First define and approve the row.
- Then require live/synthetic distinction, integer units, real TTFT, error rates, instrument provenance, and A/A calibration.

---

## 14. Beta release gates

All gates are mandatory. A pass in one does not compensate for another.

### 14.0 Applicability, evidence, and sign-off

Per the scope fence (§7.1), **R0–R7, R9 and R10 are Beta-blocking. R8 is Beta-blocking only in its labelling half** — no synthetic value may be presentable as a measurement — with its statistical half deferred to Q3 (S7–S9).

Each gate produces a receipt, not an assertion. A gate is closed when:

1. its evidence artifact exists under `docs/sprint6/evidence/<gate>/`, referencing the exact candidate SHA;
2. its adversarial counterpart is registered and observed failing (§9.1);
3. a signer who did not implement the control has countersigned it.

| Gate | Evidence artifact | Signer |
|---|---|---|
| R0 | Revocation receipt, history scan, scanner output | Security/release lead |
| R1 | Clean-container build log at candidate SHA | Integration lead |
| R2 | Boundary, TCB, and no-fallback test output | Tech Lead |
| R3 | Sandbox profile + escape/network/secret test output | Systems owner |
| R4 | Supervisor attestation record + tamper/pollution/drop results | Systems owner |
| R5 | Kill/restart matrix results + signed approval sample | Governance owner |
| R6 | Recorded `vg` session transcript + reconnect/cursor results | Client owner |
| R7 | Live streaming receipt + second-turn observation proof | Model owner |
| R8 | Labelled telemetry export (live/cassette/synthetic separated) | Measurement owner |
| R9 | Sealed dogfood bundle (§8-G3), three runs | Independent reviewer |
| R10 | Contract diff + gate receipts + re-sealed baseline manifest | Project Lead |

**R10 is the only gate that may change a contract row.** No workstream, and no developer, marks a row `covered` as part of its own work.

### Gate R0 — security hygiene

- No active exposed credentials.
- No secret in reachable Git refs or build artifacts.
- Blocking automated secret scanning enabled.

### Gate R1 — reproducible source

- Clean clone at candidate SHA.
- Zero untracked dependencies.
- Deterministic dependency installation and full gate execution.

### Gate R2 — architecture and TCB

- Boundary and TCB checks pass.
- Kernel remains adapter-independent.
- Production path contains no scenario/fake fallback.

### Gate R3 — effect isolation

- All effects execute through rootless sandbox profiles.
- Host escape/network/secret adversarial tests pass.

### Gate R4 — evaluator exteriority

- Supervisor-attested UID/image/process and authenticated IPC.
- Tamper/pollution/drop tests return fail-closed results.

### Gate R5 — approval and recovery

- External signature, exact descriptor binding, grant linkage.
- Kill/restart matrix proves ledger-only, exactly-once resumption.

### Gate R6 — live operator path

- `vg` starts and controls the real runtime.
- Live approval and correction persist durably.
- Reconnect/cursor/schema tests pass.

### Gate R7 — provider and context

- Real streaming provider receipt.
- Tool observations demonstrably influence later turns.
- Malformed provider data cannot become an effect.

### Gate R8 — measurement integrity

- Real timings only in live reports; synthetic values visibly separated.
- Integer units, instrument tuple, failure rates, and uncertainty present.

### Gate R9 — dogfood

- Preregistered unknown bug fixed through the sole product path.
- Independent reviewer validates immutable evidence.

### Gate R10 — contract closure

- Only after R0–R9: update applicable rows to `covered` with exact evidence references.
- Contract checker verifies evidence existence, candidate SHA, and gate result rather than assignment alone.

---

## 15. Final disposition

Phases 0–2 established a promising kernel, domain model, adapter foundation, context compiler, evaluator probe primitives, approval digest primitive, and client presentation layer. The work is salvageable and should not be rewritten wholesale.

The correct next milestone is **Phase 2 Trustworthy Integration Closure**, not Phase 3 benchmarking or Beta packaging. The project becomes a Beta MVP only when the operator, runtime, sandbox, approval authority, evaluator, ledger, and telemetry form one reproducible causal system with independently verifiable evidence.

Until then:

- keep the affected contract rows open;
- label scenario, cassette, scripted, and synthetic results honestly;
- do not merge to `main` under a completion claim;
- do not expose the runtime to untrusted repositories or credentials;
- do not publish performance or security claims based on the current component tests.

This report changes no production code. It defines the remediation and acceptance standard against which the next implementation work should be reviewed.

### 15.1 What this audit does not claim

Stated so that the next reader does not over-read it:

- It does not claim the kernel is wrong. `S0–S12`, attenuation, the governor and the grant issuer were reviewed and are sound; the TCB is 1,307 logical lines against a 1,438 alarm.
- It does not claim the tests are worthless. They are accurate about the components they cover; the defect is that component coverage was reported as system delivery.
- It does not claim the team overstated things in bad faith. Every finding here is the ordinary consequence of parallel lanes integrating late without a clean-tree gate. The fix is the gate, not blame.
- It does not establish that the credential was used by a third party — only that it must be assumed to have been.

---

## 16. Document control

| Field | Value |
|---|---|
| Document | Vanguard Phases 0–2 Full Technical Audit |
| Revision | 2 |
| Status | **Draft — awaiting Tech Lead and Project Lead countersignature** |
| Candidate SHA reviewed | `57e0eb8` |
| `main` at review time | clean of `SEC-01` |
| Supersedes | Revision 1; the optimistic Phase 2 completion report; the interim remediation list |
| Normative conflicts raised | `ADR-0057` (Beta scope) — resolved by ruling in §7.1, requires countersignature |
| Rulings requiring approval | §7.1 scope fence · §13 `REQ-SLICE-001` disposition · §4.1 registry repair |
| Next review | On completion of Workstream A, before Workstream B begins |

**Countersignature.** §7.1 and §13 contain rulings I have made in the Tech Lead / Project Lead capacity. They change what Beta means and what a contract row asserts. They are not effective until the accountable humans sign them, and neither should be treated as settled by the fact that they appear in this document.

| Role | Name | Decision | Date |
|---|---|---|---|
| Tech Lead | | ☐ Accept ☐ Amend ☐ Reject | |
| Project Lead | | ☐ Accept ☐ Amend ☐ Reject | |
