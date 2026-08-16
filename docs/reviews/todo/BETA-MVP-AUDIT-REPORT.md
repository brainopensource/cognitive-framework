# Vanguard / Aether-D-System — Sprint 5–6 Beta Audit

**Classification:** Internal engineering audit (architecture, trust, loop engineering)  
**Date:** 2026-08-16  
**Scope:** Wave 2 (Sprints 5–6) on `sprint5-6/integration`, relative to Sprint 0–4 at `v0.4.0-sprint4`  
**Question:** Is this a shippable Beta MVP of (1) a **framework** for building agentic coding harnesses and CLIs, and (2) a **harness CLI** built on that framework?  
**Answer:** **No.** The TCB, kernel, context compiler, and port lattice are unusually serious for an unreleased system. What does not yet exist is one **trust-preserving product path** from operator intent → prefix-stable model context → kernel-mediated effect → exterior verdict → CLI. Until that path is real, tagging `v0.6.0-beta` would require statements that the code cannot support.

This document is the durable record of the audit: what the system is, what SOTA demands, what landed in Sprints 5–6, what was false, what was patched in the worktree, and what remains before a Beta that could be sold, distributed, or used as a meta-harness for later general task solving.

---

## 0. Thesis

An agentic coding harness is not “an LLM with tools.” It is a **closed-loop control system** whose plant is a repository, whose actuator is a capability-attenuated kernel, whose observer is an exterior evaluator, and whose human is a **cryptographic principal**, not a UI callback.

SOTA in 2026 (industrial coding agents, research SWE agents, and the Vanguard v4 handbook itself) converges on a small set of non-negotiable properties:

1. **Single dispatch authority.** Effects happen on one path or they did not happen.
2. **Prefix-stable context** for provider KV caching (L1–L3 frozen; dynamics only in later layers).
3. **Fail-closed uncertainty.** Inconclusive ≠ pass. Missing evaluator ≠ success.
4. **Exterior judgement.** The loop must not grade itself.
5. **Operator-held privilege.** The process that can patch the disk must not mint the signature that authorises the patch.
6. **Containment of exec.** Command verbs are a different port from filesystem/git.
7. **A real client protocol.** A CLI that cannot start a run on a daemon is a cassette player.
8. **Gates that can fail.** A contract row whose component is invisible to CI is not a requirement.

Vanguard’s **design documents** already name these (M5, M6, M9, M11; K-13–K-17; ADR-0057; ICD §3–§4). Sprint 5–6 **implementation** delivered the pieces and then composed them in ways that violated 5–8. The audit patched 5–8 at the **mechanical** level. The **cryptographic**, **deployment**, and **human-judgement** levels remain open.

---

## 1. What the project actually is

### 1.1 Two products, one lattice

The intended Beta is a **pair**:

| Product | Claim | Current honesty |
|--------|--------|-----------------|
| **Framework** (`vanguard/packages/*`) | Ports, kernel, domain, adapters, composition root: enough to *build* other harnesses/CLIs | **Partially true.** The lattice is real. The composition root still knows too much (coding verbs, OpenRouter default, HMAC). Generality (ADR-0060 / M11) is asserted, not demonstrated outside coding manifests. |
| **Harness CLI** (`vanguard/clients/cli`, `@vanguard/cli`) | Headless + TUI client of a RuntimeService | **Protocol shell is real; live peer is not.** JSONL feed/replay/scenario work. Unix socket client fails closed after the audit. There is still no in-repo daemon wrapping `Runtime.execute_harness`. |

A “billion-dollar cognitive machine / meta-harness / AGI-like GTS” is a **later claim**. ADR-0057 already defers Q3 (measurability, A/A floor) and Q4 (generality beyond coding) to Sprints 7–9. Treating Beta as that later claim is how this wave over-declared.

### 1.2 Normative stack (v4)

The living theory is `docs/v4/` or, on the migrated WSL tree, `docs/main_v4/`:

| Doc | Role |
|-----|------|
| Engineering handbook | Mental models M1–M11 (especially M5 exteriority, M6 fail-closed gates, M9 no late discovery, M11 open/closed composition) |
| Charter / non-claims | What must never be claimed (self-grading, unbounded autonomy, “the model said tests passed”) |
| Architecture planes | Context assembly L1–L5; execution model; kernel as sole effect path |
| Core contracts / wire schema | EventEnvelope, digests, JCS canonicalisation |
| Kernel / security | S1–S12 dispatch, grants, attenuation, sandbox port |
| Competence / evidence | Priors, corrections, replay |
| Loop engineering / measurement | Ch.10 Q1–Q4 dogfood; Beta = Q1+Q2 under ADR-0057 |
| Decision register | ADRs (0047 slice deletion, 0057 Beta fence, 0060 generality, …) |

Sprint packets (`docs/sprint5/*`, `docs/sprint6/*`, or `docs/agile/sprintN` after the docs move) are work orders against `docs/sprint0/active-mvp-contract.json` (or `docs/agile/sprint0/…` on the live layout).

### 1.3 Runtime topology (as designed)

```
operator / CLI
    │  JSONL / Unix socket (intended)
    ▼
runtime/root.py          ← only module allowed to know concrete adapters
    │  compose(manifest) → frozen Harness
    │  execute_harness → segments
    ▼
agency/episode/engine    ← depth-1 loop; terminates on approval suspension
    │  propose(view)
    ▼
agency/context/compiler  ← L1–L5; prefix-stable L1–L3
    │  messages[]
    ▼
adapters/models          ← OpenRouter | cassette | fake
    │
kernel.dispatch S1–S12   ← sole actuator
    │
adapters/environment.git     (fs, patch)
adapters/sandbox.rootless    (proc.exec)   ← intended
    │
ledger (EventStorePort)
    │
adapters/evaluators.isolated ← exterior, uid 10002, after terminal
```

The **designed** topology is SOTA-shaped. The **shipped** topology (pre-audit) short-circuited approval, sandbox, evaluator, and CLI.

### 1.4 Claimed but not found in this workspace index

`tools/001_LLM_API_ROUTER` and `tools/002_LLM_API_MOCK` were cited as the way to run or mock LLM calls (Ollama / LAM mock). They were **not present** in the tree the auditor indexed. Live model I/O in-repo is:

- `vanguard/packages/adapters/models/openrouter.py` (real HTTP/SSE, `OPENROUTER_API_KEY`)
- `cassette.py` / `fake.py` (deterministic, no network)
- optional `LiveDogfood` unittest skipped when the key is unset

If those numbered tools exist on another machine or an unmerged branch, they are **not** the Beta composition path. Do not document them as the product until they are wired through `ModelPort` and the composition root.

---

## 2. SOTA bar for an agentic coding harness (why this audit’s criteria)

### 2.1 Loop engineering, not chatbot UX

A competent harness is a **partially observed MDP** (or, more honestly, a **hybrid automaton**):

- **State:** repo bytes + ledger + frozen harness digest + KV-cache prefix.
- **Observation:** compiled context (lossy).
- **Action:** tool calls / patches / exec, all via kernel descriptors.
- **Transition:** only if `Kernel.dispatch` records intent then occurrence.
- **Reward / termination:** exterior evaluator, not the policy model.

If the policy model both acts and declares success, the loop is **unidentified**: you cannot tell competence from self-report. That is M5 / ICD §3. IsolatedEvaluator exists to break that identification problem. Leaving it uncomposed made every green dogfood test a **statement about a cassette**, not about an instrument.

### 2.2 Prefix stability as systems, not prompt folklore

Provider prompt caches (Anthropic, OpenAI, Gemini, OpenRouter wrappers) are **prefix-keyed**. If L1–L3 change by one byte, you pay full prefill and destroy TTFT economics. Vanguard’s L1–L5 compiler is the correct industrial design:

| Layer | Content | Stability |
|-------|---------|-----------|
| L1 | System core | Frozen at `ContextCompiler` construction |
| L2 | Tool schemas | Frozen |
| L3 | Repo map / environment | Frozen |
| L4 | Task brief / notes | Compactable |
| L5 | Dialogue | Evictable first |

This is **not** “good prompting.” It is a **cache-coherence protocol** between the harness and the inference provider. Tests in `test/agency/test_context_compiler.py` actually prove byte-identity of the prefix across turns. That is one of the strongest artefacts in the repo.

The remaining defect was **not** the compiler. It was a second dialect (`episodeView`) stuffed onto the bundle while OpenRouter read `messages`. Two wire shapes for one ModelPort is how prefix stability dies in production even if unit tests pass.

### 2.3 Privilege as information flow

`fs.patch` / `patch.apply` is a **privileged sink**. The human must bind a **descriptor digest** of the exact args (K-15). If the same process:

1. constructs the challenge,
2. hears a Boolean,
3. HMAC-signs with a key it holds,
4. verifies that HMAC,

then the “signature” is **not a constraint**. It is a log line. This is GOV-01. Cryptographically, HMAC with a shared secret is **symmetric**: anyone with the verify key can forge. A sellable split is **asymmetric** (operator-held private key; runtime holds only the public key) or an out-of-process HSM/OS keyring the runtime cannot read.

The audit made the **control-flow** honest (runtime no longer calls `approve()`). It did not make the **key schedule** honest. That is still a Beta-blocking *claim* if marketing says “cryptographic approval.”

### 2.4 Containment vs allowlists

Allowlisting `git`, `pytest`, `ruff`, `python3` and then `subprocess.run` on the host is **policy**, not **isolation**. A confused-deputy or prompt-injected argv still runs as the developer uid, with host net and host secrets. SOTA coding agents that touch untrusted repos (or untrusted model output) put exec in a user namespace / bwrap / microVM / gVisor.

Vanguard already had `RootlessSandboxRunner` with probe-derived containment reports (mount, egress, nested unshare). Sprint 6 listed it and bound `proc.exec` to `GitEnvironment.apply` instead. That is SBOX-01: a **composition error**, not a missing library.

### 2.5 Evaluation exteriority and UID identity

`IsolatedEvaluator` refuses to claim if `os.getuid() != 10002` or the image digest is not `sha256:[64 hex]`. That is the correct **instrument identity** gate: the evaluator daemon is a different principal from the agent. In dev/CI you **must** get `outcome="inconclusive"`, not a fake `claims` pass. Substituting `FakeEvaluator` or `SuiteVerifier` into the default path to keep CI green is exactly the M5 failure the handbook warns about.

`SuiteVerifier` (host `python3 -m unittest`) remains legitimate as an **injected override** for the mechanical dogfood gate (REQ-DOG-001). It is not REQ-EVAL-001.

### 2.6 CLI as protocol, not SDK

A hexagonal CLI (TypeScript, no Python imports, no SQLite) is the right **framework** move: many UIs, one RuntimeClient. SOTA CLIs (and Cursor’s own agent surface) still need a **live control plane**: start, cancel, approve, correct, resume, with cursor/`afterSeq` and fail-closed transport.

Lane C built the hexagon and then implemented live methods as **local stubs**. Tests titled “without failing not_available” certified the stub. That is M6: a gate that cannot fail.

---

## 3. Inventory of what actually landed (Sprints 5–6)

### 3.1 Lane A — Lead architect (`agency/context`, `runtime/root`)

**Assigned:** REQ-CTX-001 (L1–L5 compiler + pre-action competence prior); later REQ-DOG-001 composition.

**What is real:**

- `vanguard/packages/agency/context/compiler.py`, `layers.py`
- Frozen prefix at construction; budget ladder L5 eviction → drop → L4 notes; brief exempt
- `CompetencePriorRecorded` with digests, no prompt text
- `Runtime.compose` from harness manifests (`vg-code-default`, `vg-shell-only`)
- Cassette dogfood: real git repo, real kernel, real patch via dispatch, real unittest subprocess as injected verifier
- `_LayeredOperator` wraps ModelPort so `agency/episode/` need not change (ADR-0060 price)

**What was false (pre-patch):**

| ID | Mechanism | Why it mattered |
|----|-----------|-----------------|
| GOV-01 | `approval_key=b"composition-root-approval-key"`; `_resolve` called `authority.approve` after `approver(challenge) → bool` | Human consent was real; cryptographic separation was not |
| SBOX-01 | `DEFAULT_BINDINGS["proc.exec"]` → `_environment_effector` → `GitEnvironment.apply` → `subprocess.run` | Exec with host authority |
| CTX-01 | `bundle["episodeView"]=view` while OpenRouter `_messages` reads `context["messages"]` | Dual dialect; risk of compiling for a consumer that ignored layers |
| EVAL unwire | `IsolatedEvaluator` never constructed by root; `verifier=None` → no verdict | Manifest `coding-oracle@3` was a string, not a binding |
| ARCH-02 | Coding verbs hardcoded in `DEFAULT_BINDINGS` | M11/ADR-0060 “zero engine edits for a new domain” is half-true: adding a domain still means editing root’s table |

**Competence prior semantics:** The ledger event is real and pre-turn-1. The number is `TaskContext.competence_prior: float`, **caller-supplied**, not a calibrated \(P(\text{success}\mid\text{task})\) from the operator model. The *syntax* of measurement exists; the *epistemology* does not.

### 3.2 Lane B — Evaluators, approvals, models (scope collision)

Official SB packets: OS-isolated evaluator (S5), descriptor-bound approvals (S6).  
OpenRouter SSE was **Lane DC** (`S5-DC-001`). Auditing “Developer B” as SSE+env mixed ownership.

**What is real:**

- `approvals.py`: challenge binds action, principal, normalised diff, digests, expiry; HMAC verify; `DescriptorBoundApprovalPolicy`; unit tests for tamper/expiry/forge
- `IsolatedEvaluator`: immutability + pollution probes; inconclusive on instrument failure
- `openrouter.py`: incremental SSE (`read(8192)`), incremental UTF-8, fail-closed `_parse_sse_stream` (bad JSON, wrong choice arity, missing `[DONE]`, incomplete tool calls)
- Cassette replay with no network
- Secret **ref** in the adapter (`api_key_ref`), redaction in errors

**What was false or weak:**

- Claimed `env_loader.py` was missing or overwritten; security tests (`test/security/test_env_loader.py`) already specified S6B-SEC-003 (`load_api_key`, 0600, symlink, interpolation, tracked-file reject). Restored to that API in the worktree.
- Non-SSE `_parse_proposal` **skips** bad tool-call entries and stuffs invalid JSON args into `{"raw": arguments}` — not fail-closed, inconsistent with SSE.
- Most SSE tests parse a **buffered** body; only one test injects `stream_transport` and splits mid-UTF-8.
- `test_openrouter.py` used `urllib.error.URLError` without importing `urllib` (fixed).
- Working-tree `.env` can hold a live-shaped key at 0600; **not git-tracked** at audit (`git ls-files .env` empty). Rotate if it ever hit origin.
- `benchmarkings/tasks_phase2/test001/README.md` was not found in the indexed tree.
- Root still default-constructs `OpenRouterModel()` when `model is None` — live provider as default is a composition smell for tests and for air-gapped use.

### 3.3 Lane C — CLI / DX (`vanguard/clients/cli`)

**What is real:**

- Zero Python / SQLite imports (hexagonal)
- Strict `EventEnvelope` parse (UUID, timestamp, required fields)
- Headless JSONL with no CSI in stdout
- Replay read-only (`recordCorrection` → `permission_denied`)
- Dedup `lastSeenSeq` / `afterSeq` on live **feed**
- Approval/correction routers that do not mutate domain state in the TUI
- Packaging `@vanguard/cli@0.4.0-beta` (~12 kB tarball claim)

**What was false:**

- `LiveRuntimeClient` without a JSONL feed: `startRun`, `resolveApproval`, `getDaemonStatus`, cancel, checkpoint, resume all returned **ok** locally
- `getDaemonStatus` fabricated `stopped`/`running` without probing the socket
- `approveDecision` mapped a failed **reject** to exit 1 (human deny) instead of 2 (protocol / daemon unreachable)
- Version still 0.4.0-beta while the wave talks about v0.6.0-beta
- README drift (`MockRuntime` vs `RuntimeClient`)
- `tools/run_dogfood_r9.py` imports Python `Runtime` directly — **bypasses the CLI**, so dogfood does not prove the product you would ship

**After patch:** no-peer control plane is `not_available`; JSONL feed still works; CLI tests 22/22.

### 3.4 Lane D — Governance / tools

**What is real:**

- `tools/repo_paths.py` canonical map (`docs/main_v4`, `docs/agile`, …)
- `check_receipt.py` rejects self-sign, pending, broad commands (validator exists)
- `scan_secrets.py` blocking, wired in CI
- `--release` on the contract checker fails unless merged-scope evidence is 100%
- Intentional fail of `--release` while Beta is open

**What was false or half-migrated:**

- Tools required sentinel `docs/main_v4`. Some views of the repo still had `docs/v4` + `docs/sprint*`. Dual-layout fallback was added so `repo_root()` works on either.
- Live WSL tree: `docs/agile` + `docs/main_v4` exist; `docs/sprint0` / `docs/v4` do not. Cursor’s Windows indexer still listed the old paths — **two views of one repo** is itself an operational hazard.
- Contract on the agile tree: `closure-in-progress`, ~50 rows, `merged_scope_evidence_coverage=0.0% (0/49)`. Default check **PASS**es because opens are allowed. `--release` **FAIL**s. That is the correct closeout discipline.
- Wave 2 components must be **in** `merged_components` or CI can never force CTX/EVAL/APP/CLI-002/DOG closed. They are present on the agile contract.
- Receipts on disk were largely `docs/sprint6/evidence/R*/receipt.md`, not SHA-bound `receipt.json` on the path `check_receipt.py` expects. Validator without CI + JSON receipts = **narrative**.
- `check_baseline_manifest.py` digest-drifted after the contract-checker edit (expected; reseal with an authorising commit, do not silent-overwrite).
- Clean-candidate workflow was claimed; only `.github/workflows/ci.yml` was found in the index.
- Branch protection has printed EXTERNAL GATES OPEN since Sprint 0 — GitHub admin, not an engineer lane.

---

## 4. Contract and Beta fence (governance truth)

### 4.1 Open Wave 2 rows (do not flip to `covered` yet)

| Row | Component | Honest state |
|-----|-----------|--------------|
| REQ-SLICE-001 | slice/e2e | Artifact deleted (ADR-0047). **Justified**, not covered. Surviving evidence: `check_boundaries.py` (no production `slice/` imports) + TEST-DOG-001 as compensating path. |
| REQ-CTX-001 | agency/context | Compiler + tests real. Wiring patched. Still not “covered” until merged evidence receipts exist. |
| REQ-EVAL-001 | adapters/evaluators | Adapter real. Bound with inconclusive-in-dev. **REQ-EVAL-002** (daemon uid/image/supervisor) must not be smuggled in. |
| REQ-APP-001 | runtime/governance-approval | Library real. Root no longer mints. Ledger-complete challenge/decision persistence still thin. HMAC ≠ operator/runtime split. |
| REQ-CLI-002 | client/cli-tui | Shell real. Live RuntimeService **absent**. |
| REQ-DOG-001 | runtime/composition | Cassette Q1 real. Q2 live ×3 **absent**. |

`check_active_mvp_contract.py` only treats a row as must-close when its component is in `merged_components`. That is why “keep rows open” was previously **unenforced**. After amendment, `--release` fails on open merged rows. **Insist on seeing red before green.**

### 4.2 ADR-0057 (do not silently supersede)

Beta = Ch.10 **Q1 + Q2**.

- **Q1:** Mechanical composition (dispatch, approval bind, ledger, no second path). Cassette dogfood addresses this.
- **Q2:** Three real bugs in a repository someone knows, fixed interactively **without hand-patching mid-run**, then: *would you reach for this next time?* If no, the loop is not done. No later sprint fixes a “no.”
- **Q3/Q4:** Deferred (measurability / A/A; non-coding generality).

Telemetry **labelling** is Beta-blocking; telemetry **rigour** is not.

### 4.3 Human gates that are not machine-certifiable

- Independent third-engineer reconstruction (schema archaeology)
- Prospective human hands-on timing
- Q2 signed judgement
- GitHub branch protection + signed tag
- Spend authorisation for live API runs

---

## 5. Defect catalogue (complete)

Severity: **Block** = shipping would require an untrue sentence. **Debt** = honest “not yet.” **Patched** = worktree as of this audit.

| ID | Sev | Status | Location | Statement |
|----|-----|--------|----------|-----------|
| GOV-01 | Block | Patched (flow); open (crypto) | `runtime/root.py` `_resolve` | Runtime must not mint approval HMAC. Still holds verify key (HMAC). |
| SBOX-01 | Block | Patched (bind); open (proof) | `DEFAULT_BINDINGS["proc.exec"]` | Exec via `RootlessSandboxRunner`. Product-path test that exec cannot silently use GitEnvironment still needed. |
| CTX-01 | Block | Patched | `_LayeredOperator.propose` | `episodeView` removed. Engine still produces a flat view that is compiled away — residual dual dialect. |
| EVAL-01 | Block | Patched (bind) | `EVALUATOR_BINDINGS` | `coding-oracle@3` → IsolatedEvaluator; uid mismatch → inconclusive; no FakeEvaluator row. |
| ARCH-02 | Debt | Open | `DEFAULT_BINDINGS` | Coding verbs live in root.py. Profile packs / manifest adapter ids are the M11 completion. |
| CLI-LIVE | Block | Patched (honesty); open (peer) | `clients/cli/src/adapters/live.ts` | Fail-closed without peer. No daemon. |
| SEC-01 | Block | Bounded | `.env` | Untracked now. Rotate if historically pushed. Loader restored (0600, no interpolation, untracked). |
| GATE-01 | Block | Patched | `check_active_mvp_contract.py` | `--release` fails on open merged rows. Default still allows opens. |
| DOCS-01 | Warn | Patched | `tools/repo_paths.py` | Dual sentinel for main_v4 vs v4. |
| LEDGER-01 | Debt | Open | `test/support/composition.py` vs `LedgerBridge` | Two bridges; trust tests need `fails=` / `append_governance`. |
| SSE-01 | Debt | Open | `openrouter.py` `_parse_proposal` | Buffered path not fail-closed like SSE. |
| PRIOR-01 | Debt | Open | `TaskContext.competence_prior` | Float injection ≠ calibrated prior. |
| PKG-01 | Debt | Open | `package.json` | CLI 0.4.0-beta vs wave 0.6.0-beta. |
| RCPT-01 | Block | Open | receipts | Markdown R0–R10; `check_receipt` not in CI; no independent signers. |
| NODE-01 | Warn | Env | contract reader tests | `unittest discover` errors without `node` on PATH (14 tests). |
| BASELINE-01 | Warn | Open | `check_baseline_manifest.py` | Digest drift after checker edit; reseal. |

---

## 6. What this audit changed in code (worktree only; not pushed)

These are **mechanical honesty patches**, not the six-week rewrite.

1. **GOV-01:** `approver` must return `ApprovalDecision` (or refuse). Boolean `True` does not apply the patch. `approval_key` has no default; without it the root can issue a challenge but cannot verify. Tests sign with an operator-side `ApprovalAuthority`.
2. **SBOX-01:** `proc.exec` factory is `_sandbox_effector` → `RootlessSandboxRunner`. `healthy()` is `/usr/bin/bwrap` existence. Unverified containment is not `ok`.
3. **CTX-01:** Stop attaching `episodeView`. Provider bundle is `compiled.bundle()` only.
4. **EVAL-01:** If `verifier is None`, bind from manifest via `EVALUATOR_BINDINGS`. Unknown names bind nothing. Dummy image digest + uid 10002 → inconclusive in dev.
5. **CLI:** Feed mode (stdin/JSONL) still consumes streams. Socket mode without a peer fails. `approveDecision` protocol failure is always exit 2.
6. **env_loader:** `load_api_key`, `ALLOWED_KEY`, 0600, symlink, interpolation, size, tracked-file, `inject_into_environ` (does not mutate `os.environ`).
7. **repo_paths:** Accept live or legacy docs layout.
8. **Contract checker:** Accept historical `approved-s0-s4-closed` as a status token where needed; `--release` remains the hard gate.

**Deliberately not done:** Ed25519 ADR, Unix daemon, live Q2 ×3, flipping contract statuses to `covered`, history purge, baseline silent overwrite, collapsing `SharedLedger`, adding microVMs, claiming A/A calibration.

---

## 7. Tests run (evidence, not vibes)

| Command | Result | Interpretation |
|---------|--------|----------------|
| Subset unittest (composition, compiler, isolated evaluator, OpenRouter, env_loader) | Pass; live OpenRouter skipped | Mechanical patches hold |
| `npm` `@vanguard/cli` test | 22/22 pass | Fail-closed live + feed still work |
| `python3 tools/check_boundaries.py` | PASS, 100 files | Root importing sandbox/evaluator did not break the lattice |
| `python3 tools/check_active_mvp_contract.py` | PASS, 0/49 merged evidence | Default *allows* open merged rows |
| `… --release` | FAIL, 49 open merged rows | Gate can fail — keep it that way until evidence is real |
| `python3 tools/scan_secrets.py` | PASS after removing `sk-` fixture assignment | Scanner is load-bearing; tests must not look like live keys |
| `python3 tools/check_baseline_manifest.py` | FAIL, digest drift | Reseal |
| `python3 -m unittest discover -s test` | ~388 ran; 14 errors without `node`; env_loader import error then fixed | Re-run discover with Node on PATH |

Dogfood cassette tests prove: read-before-patch, disk change only through dispatch, refuse/absent approver leaves file untouched, prior is first ledger event, prefix digest stable, injected SuiteVerifier is exterior to the episode. They do **not** prove live competence, sandbox exec, or IsolatedEvaluator in the daemon uid.

---

## 8. How to finish, build, ship, and distribute a Beta that is actually SOTA

This is a **sequenced** plan. Parallelising 1–5 without a product path is how Sprint 6 over-declared.

### Phase B0 — Honesty freeze (days)

- Do not tag `v0.6.0-beta`.
- Do not mark REQ-CTX/EVAL/APP/CLI-002/DOG `covered`.
- Rotate provider keys if `.env` ever left the machine; confirm `git log --all -- .env`.
- Reseal baseline with a named commit reason.
- Install Node on the CI/dev PATH; make `unittest discover` green without hiding the 14 reader tests.

### Phase B1 — One product path (1–2 weeks)

The framework is the lattice. The **product** is one path:

1. **Daemon:** a small Python (or Rust) supervisor that owns `Runtime.execute_harness`, listens on `$VANGUARD_RUNTIME_SOCKET` / `/tmp/vanguard-runtime.sock`, speaks JSONL request/response frames: `startRun`, `streamEvents`, `resolveApproval` (forwards a **signed** decision; does not sign), `cancel`, `status`.
2. **CLI live adapter:** write those frames; delete remaining feed-mode control-plane success that is not actually a feed.
3. **Approval:** CLI (or a tiny `vg-approve` helper) holds the key; daemon verifies. Persist `ApprovalChallenge.payload()` and `ApprovalDecision.payload()` on the ledger; resume via `verify_from_ledger`. ADR for HMAC→Ed25519 with a reversal trigger.
4. **Exec:** one test: proposing `proc.exec` cannot hit `GitEnvironment.apply`. Skip if no bwrap; **fail** if it uses host subprocess.
5. **Evaluator:** keep inconclusive in dev. REQ-EVAL-002 is a **deployment** row: uid 10002, image digest, supervisor. Never FakeEvaluator in the default bind table.

Exit criterion: `vg run --headless --prompt …` against a local daemon repairs the cassette bug **or** fails closed with exit 2. No Python import from the CLI.

### Phase B2 — Q2 or no Beta (1 week + human)

- Three bugs in a repo a signer knows.
- Model, turns, cost, **no mid-run hand-patch**, verdict, one Q2 sentence each, one signed judgement.
- If Q2 is no: **stop**. That is the handbook.

Optional: `OPENROUTER_API_KEY` live unittest. Do not treat skip-as-pass as Q2.

### Phase B3 — Framework completeness (Sprint 7, not Beta-critical)

- Move `DEFAULT_BINDINGS` to **profile packs** (`coding`, `shell-only`) loaded by manifest id — finish ARCH-02 / M11.
- Compile context in `EpisodeEngine` observe; delete `_LayeredOperator` as a dialect translator.
- Collapse test `SharedLedger` onto `LedgerBridge` with explicit test-only failure injection.
- Align `_parse_proposal` fail-closed with SSE.
- Version CLI to the same Beta tag as the Python package.
- Wire `check_receipt.py` in a **release** workflow, not only default CI.

### Phase B4 — Distribute

Beta distribution that matches the architecture:

| Artefact | Rule |
|----------|------|
| `@vanguard/cli` npm tarball | Already small; no `.env`; pin protocol version |
| Python `vanguard` package | Ports + kernel + adapters; composition root as the only concrete importer |
| Container | Agent uid ≠ evaluator uid 10002; no shared writable secret volume |
| SBOM + signed tag | GitHub admin; `check_baseline_manifest.py --release` |
| Docs | One layout (`docs/main_v4` + `docs/agile`); delete the other |

Do **not** distribute a “GTS / AGI-like meta-harness” story. Distribute: **a capability-attenuated coding loop with an exterior judge and a protocol CLI.** That is the SOTA Beta. The meta-harness is the same lattice with new manifests (M11), which you have not yet proven.

### Phase B5 — Explicitly out of Beta

microVMs, A/A paired trials, non-coding environments, in-engine resume (ADR-0062: re-entry stays at S1 in root), collapsing human archaeology gates into CI.

---

## 9. Recommended architecture (target, not greenfield)

Keep:

- Pure `ContextCompiler` + frozen L1–L3
- Kernel S1–S12 as the only effect path
- Manifest-frozen harness
- Hexagonal CLI (`RuntimeClient`)
- IsolatedEvaluator’s inconclusive ontology
- Rootless sandbox probes

Change:

| Seam | From | To |
|------|------|----|
| Context | Root wraps engine view | Engine observe returns `CompiledContext.bundle()` |
| Root | Authority + default OpenRouter + host exec | Binder: inject model, sandbox, verifier, verify-key |
| Approval | Shared HMAC in-process | Operator signature; ledger-durable challenge/decision |
| Exec | GitEnvironment catch-all | Git = fs/git; proc = sandbox only |
| CLI | Facade over fixtures | Client of a daemon |
| Eval | Optional injection | Manifest bind; daemon identity; inconclusive in dev |

This is how you get **both** products: the framework is the lattice + binder; the CLI is one client; a second CLI (IDE, CI bot) is another client of the same daemon. That is the actual “meta-harness” — not a larger prompt.

---

## 10. Epistemic limits of this audit

This audit does **not** claim:

- That `main` is identical to the worktree (patches are local, unpushed).
- That origin never contained `.env` in older SHAs beyond `git log -- .env` on this clone.
- That bwrap containment holds on the product path (binding test only).
- That live models can repair real bugs (Q2 unrun).
- That the Windows-indexed tree and the WSL tree are the same directory listing (they were not; WSL is treated as source of truth for commands that ran).
- That tools `001_LLM_API_ROUTER` / `002_LLM_API_MOCK` exist (not found here).

---

## 11. One-sentence close

Vanguard is a **serious kernel and context compiler** wrapped in a composition root and CLI that, until this audit, **performed theatre at the four seams that create trust**; those seams are now fail-closed in the worktree, and Beta remains **undeliverable** until a daemon, operator-held signing, sandbox-proven exec, evaluator deployment, and three honest Q2 runs exist.

---

*End of report. Authors of lane work: SA / SB / DC / CLI / GOV as in sprint packets. Auditor: Sprint 5–6 closeout review, 2026-08-16. No contract statuses were flipped to `covered`.*
