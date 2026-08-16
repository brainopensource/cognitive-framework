# Vanguard v0.4.1 (Sprint 6B MVP Beta) — Master Execution & Task Matrix

**Document Status:** LIVING MASTER SPECIFICATION & EXECUTION TRACKER  
**Baseline Target:** `v0.4.1-beta` / Sprint 6B Closeout (Chapter 10 Q1+Q2)  
**Governance Authority:** [`00_vanguard_registry_v040.md`](docs/main_v4/00_vanguard_registry_v040.md), [`09_vanguard_decision_register_v040.md`](docs/main_v4/09_vanguard_decision_register_v040.md) (ADR-0057/0058/0060/0061), [`sprint_6B_review_overview_and_next_tasks.md`](docs/agile/sprint6B/sprint_6B_review_overview_and_next_tasks.md), [`guidelines_sprint_6B_close.md`](docs/development_guides/guidelines_sprint_6B_close.md).

---

## 1. Executive Mission & Cognitive Architecture Principles

Vanguard is an **evidence-directed cognitive runtime** engineered around one fundamental premise: **Cognitive state transitions must be mathematically attributable, capability-bounded, durably recoverable, and externally evaluated.**

### The Universal Cognitive Execution Protocol
$$\text{observe} \longrightarrow \text{propose} \longrightarrow \text{authorise} \longrightarrow \text{effect} \longrightarrow \text{receipt} \longrightarrow \text{evaluate}$$

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   VANGUARD COGNITIVE PLANES                                      │
├─────────────────┬─────────────────┬──────────────────┬─────────────────┬─────────────────────────┤
│ 1. Interaction  │ 2. Agency       │ 3. Policy Kernel │ 4. Execution    │ 5. Evidence Plane       │
│    Plane (CLI)  │    Plane (Loop) │    Plane (TCB)   │    (Sandbox)    │    (Exterior Judge)     │
│                 │                 │                  │                 │                         │
│ • Untrusted     │ • Context       │ • S0–S12 State   │ • Rootless      │ • Independent           │
│   Operator      │   Compiler      │   Machine        │   Bubblewrap    │   UID 10002             │
│ • Ed25519       │ • ModelPort     │ • Attenuation    │ • Isolated      │ • Immutability &        │
│   Signing       │   Translator    │ • Reservations   │   Worker        │   Non-Pollution Probes  │
│ • NDJSON Wire   │ • Episode Loop  │ • Capability     │ • Sealed        │ • Signed Verdicts       │
│   Client        │   (Depth-1)     │   Grants         │   Environment   │ • Fail to Inconclusive  │
└─────────────────┴─────────────────┴──────────────────┴─────────────────┴─────────────────────────┘
```

### Core Invariants Locked for v0.4.1 Beta
1. **Domain Generality Invariant (`ADR-0060` / `VG-01 M11`):** The microkernel (S0–S12) and recursive episode loop must remain 100% agnostic to task domains. Coding is purely a configuration manifest (`vg-code-default`). Zero lines of code in `kernel/` or `agency/episode/` may contain coding-specific logic.
2. **Asymmetric Authority Boundary (`DEC-6B-022` / `GOV-01`):** The runtime never signs approvals. The operator CLI holds the private Ed25519 key; the runtime holds only trusted public keys.
3. **Prefix Stability & KV-Cache Invariant (`VG-03 §10.2`):** L1–L3 context layers remain byte-identical across turns; mid-run observations enter strictly at L5.
4. **Perimeter Containment (`DEC-6B-040` / `SBOX-01`):** Every model-driven effect (`fs.read`, `fs.search`, `fs.write`, `patch.apply`, `proc.exec`) executes inside rootless Bubblewrap (`bwrap`). Host direct execution is prohibited.
5. **Exterior Evidence Separation (`DEC-6B-044` / `EVAL-01`):** Evaluator runs in a separate supervised process under UID 10002 with double probes; failure or ambiguity yields `inconclusive`, never a fabricated pass.
6. **TCB Line Ceiling (`ADR-0054` / `K-02`):** The Trusted Computing Base in `vanguard/packages/kernel/` must not exceed **1,438 logical LOC** (currently 1,307 LOC).

---

## 2. Two-Senior Parallel Ownership Model

| Role | Domain / Responsibilities | Assigned Lane | Write-Scope Boundaries |
|---|---|:---:|---|
| **Senior Developer A**<br>*(Principal Runtime & Control Architect)* | • Public schemas, NDJSON wire protocols & golden vectors<br>• Durable `RuntimeService` Unix daemon & SQLite WAL inbox/outbox<br>• Asymmetric Ed25519 approval flow & descriptor verification<br>• Event-sourced lifecycle reducer & crash recovery kill-matrix<br>• TypeScript CLI (`@vanguard/cli`) live adapter & exit codes<br>• Candidate contract test runner & release receipt verifier | **Lane A**<br>*(Control Plane)* | `schemas/v4/**`<br>`vanguard/packages/runtime/**`<br>`vanguard/clients/cli/**`<br>`tools/{check_active_mvp_contract,run_active_contract_tests,check_receipt}.py` |
| **Senior Developer B**<br>*(Principal AI/Systems & Platform Architect)* | • Canonical `ModelInvocation` / `ModelProposal` Anti-Corruption translator<br>• Multi-turn ModelPort adapters (LAM mock, Ollama, OpenRouter)<br>• Unified Sandbox Worker protocol (`bwrap` rootless perimeter for all verbs)<br>• Supervised Exterior Evaluator daemon (UID 10002, double probes, signed claims)<br>• Integer telemetry provenance & pricing tables<br>• OCI images, Python wheel/sdist packaging & dogfood oracles | **Lane B**<br>*(Workload & Evidence)* | `vanguard/packages/ports/**`<br>`vanguard/packages/adapters/**`<br>`vanguard/packages/agency/context/**`<br>`tools/002_LLM_API_MOCK/**`<br>`tools/telemetry/**`<br>`containers/**`, `pyproject.toml` |
| **Joint / Tech Lead** | • Frozen interface contracts, ADR signoffs, release authorization, R0–R10 gates | **Joint** | `docs/main_v4/09_vanguard_decision_register_v040.md`, `active-mvp-contract.json` |

---

## 3. Comprehensive Master Task Matrix & Implementation Tracker

### Legend
- `[DONE]`: Verified complete with passing tests and verified code.
- `[IN_PROGRESS]`: Currently being developed or under active review.
- `[TODO]`: Specified, bounded, ready for implementation.

---

### Wave 0 — Truth, Governance & Interface Contract Freezing

| Status | ID | Owner | Scope / Deliverable | Definition of Done & Required Verification | Target Files |
|:---:|---|:---:|---|---|---|
| `[DONE]` | `W0-01` | Joint | **TRUTH-GATE Release Contract Reopening** | `check_active_mvp_contract.py --release` fails on 49 open merged rows; previous false R0–R10 closure invalidated. | `tools/check_active_mvp_contract.py`<br>`docs/agile/sprint0/active-mvp-contract.json` |
| `[DONE]` | `W0-02` | Dev A | **Tooling & Import Lattice Fix** | Add `tools/__init__.py`; ensure `python3 -m unittest discover -s test` finds telemetry benchmark modules. | `tools/__init__.py`<br>`tools/repo_paths.py` |
| `[TODO]` | `W0-03` | Dev A | **ADR-0062 / ADR-0063 Freezing** | Document `ADR-0062` (RuntimeService NDJSON wire & Ed25519 approval) and `ADR-0063` (Unified Sandbox Worker & Canonical Model Translator) in decision register. | `docs/main_v4/09_vanguard_decision_register_v040.md` |
| `[TODO]` | `W0-04` | Dev A | **RuntimeService & Wire JSON Schemas** | Define draft-2020-12 schemas + golden vector fixtures for `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `Cancel`, `Resume`. | `schemas/v4/runtime_service.schema.json`<br>`schemas/v4/approval_decision.schema.json`<br>`test/fixtures/golden_wire/` |
| `[TODO]` | `W0-05` | Dev B | **Canonical Model & Worker Schemas** | Define schemas and golden vectors for `ModelInvocation`, canonical `ModelProposal`, and `WorkerRequest` / `WorkerReceipt`. | `schemas/v4/model_proposal.schema.json`<br>`schemas/v4/worker_protocol.schema.json`<br>`test/fixtures/golden_models/` |
| `[TODO]` | `W0-06` | Dev A | **Candidate Contract Runner Mode** | Update `run_active_contract_tests.py` with `--candidate` mode that executes open and covered requirements; 0 commands returns failure. | `tools/run_active_contract_tests.py`<br>`tools/check_active_mvp_contract.py` |
| `[TODO]` | `W0-07` | Dev B | **Security R0 Key Remediation Plan** | Audit `.env` references; verify clean scanner on current tree and built wheels; prepare coordinated history scrub instructions for repo owner. | `tools/scan_secrets.py`<br>`.env.example` |

---

### Wave 1 — Parallel Backend & Engine Seams (Dev A & Dev B)

| Status | ID | Owner | Scope / Deliverable | Definition of Done & Required Verification | Target Files |
|:---:|---|:---:|---|---|---|
| `[TODO]` | `W1-01` | **Dev A** | **Durable RuntimeService Daemon (`S6B-SA-001`)** | Unix `SOCK_STREAM` server (`0600` permissions) supporting `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `Cancel`, `Resume`; SQLite WAL command inbox & event outbox; idempotent retries; stable error codes. | `vanguard/packages/runtime/service/daemon.py`<br>`vanguard/packages/runtime/service/server.py`<br>`vanguard/packages/runtime/service/inbox.py`<br>`test/runtime/test_runtime_service.py` |
| `[TODO]` | `W1-02` | **Dev A** | **Event-Sourced Recovery Engine (`S6B-SA-002`)** | Ledger replay recovers execution state; exact next transition executed; never re-invokes model for previously approved descriptor; kill matrix tests around challenge, decision, intent, effect, receipt. | `vanguard/packages/runtime/ledger/recovery.py`<br>`test/runtime/test_recovery_kill_matrix.py` |
| `[TODO]` | `W1-03` | **Dev A** | **Asymmetric Ed25519 Approval Flow (`S6B-SA-003`)** | Replace HMAC with Ed25519; operator key agent signs exact normalized diff and descriptor context; runtime holds public verify keys only; replay, mutation, expiry, and revocation tests pass. | `vanguard/packages/runtime/governance/approvals.py`<br>`test/governance/test_ed25519_approvals.py` |
| `[TODO]` | `W1-04` | **Dev B** | **Canonical Model Proposal Translator (`S6B-MD-001`)** | Strict anti-corruption layer: maps `{text, toolCalls}` → canonical `{kind, action, resource, args, reservation}`; rejects unknown tools, invalid JSON, ambiguous multiple calls, and model-minted grants before Kernel. | `vanguard/packages/adapters/models/translator.py`<br>`vanguard/packages/agency/episode/state.py`<br>`test/adapters/test_model_translator.py` |
| `[TODO]` | `W1-05` | **Dev B** | **LAM Multi-Turn Stateless Adapter (`S6B-MD-002`)** | Integrate LAM mock server with `ModelPort`; deterministic tool-calling scenario (`read → patch → test → finish`) driven by accumulated tool observations; zero fallback to fake in production. | `tools/002_LLM_API_MOCK/server.py`<br>`vanguard/packages/adapters/models/lam.py`<br>`test/adapters/test_lam_model_adapter.py` |
| `[TODO]` | `W1-06` | **Dev B** | **Unified Sandbox Worker Protocol (`S6B-MD-005`)** | Implement worker handling all verbs (`fs.read`, `fs.search`, `fs.write`, `patch.apply`, `proc.exec`) inside rootless Bubblewrap; block host GitEnvironment leaks; verify path traversal & symlink denial. | `vanguard/packages/adapters/sandbox/worker.py`<br>`vanguard/packages/adapters/sandbox/rootless.py`<br>`test/adapters/test_sandbox_worker.py` |
| `[TODO]` | `W1-07` | **Dev B** | **Supervised Exterior Evaluator Daemon (`S6B-MD-007`)** | Separate executable/process running under UID 10002 with Unix socket IPC, mutual peer validation, immutable oracle hashing, environment pollution check, signed verdicts, and conclusive `inconclusive` on fault. | `vanguard/packages/adapters/evaluators/daemon.py`<br>`vanguard/packages/adapters/evaluators/client.py`<br>`test/adapters/test_evaluator_daemon.py` |

---

### Wave 2 — Contract Integration & Offline Vertical Slice

| Status | ID | Owner | Scope / Deliverable | Definition of Done & Required Verification | Target Files |
|:---:|---|:---:|---|---|---|
| `[TODO]` | `W2-01` | **Dev A** | **CLI Live Client Rewiring (`S6B-JR-001`)** | Update TypeScript client to connect exclusively to Unix `RuntimeService`; remove silent stdin fixture-feed fallback; enforce exit codes: 0 (success), 1 (rejected/unsatisfied), 2 (instrument/protocol error). | `vanguard/clients/cli/src/adapters/live.ts`<br>`vanguard/clients/cli/src/main.tsx`<br>`vanguard/clients/cli/src/application/commands.ts` |
| `[TODO]` | `W2-02` | **Dev A** | **CLI Operator Signing Command (`S6B-JR-003`)** | `vg approve` parses challenge, displays normalized diff, signs with local operator Ed25519 key, and transmits `ResolveApproval` command to RuntimeService. | `vanguard/clients/cli/src/application/approve.ts`<br>`vanguard/clients/cli/src/adapters/signer.ts`<br>`vanguard/clients/cli/test/approve.test.ts` |
| `[TODO]` | `W2-03` | **Dev A** | **Runtime Composition Root Update (`S6B-SA-004`)** | Compose `RuntimeService`, `_LayeredOperator` with Translator, `WorkerEffectAdapter`, `Ed25519ApprovalFlow`, and `EvaluatorClientPort`; no host bypasses. | `vanguard/packages/runtime/root.py`<br>`test/runtime/test_composition_root.py` |
| `[TODO]` | `W2-04` | **Dev B** | **LAM Complete Vertical Integration (`LAM-VERTICAL`)** | Full end-to-end run: `vg run` → `RuntimeService` → `ContextCompiler` → `LAM` → `ProposalTranslator` → `Kernel` → `Bubblewrap Worker` → `Approval` → `Evaluator` → `Receipt`; multi-turn test passes without fakes. | `test/integration/test_lam_vertical_slice.py`<br>`benchmarkings/tasks_phase2_LAM/` |
| `[TODO]` | `W2-05` | Joint | **Stream Reconnect & Deduplication Verification** | Prove that client disconnection and reconnection with `after_seq` receives remaining events without duplication or dropped frames; gap triggers exit 2. | `test/integration/test_stream_reconnect.py`<br>`vanguard/clients/cli/test/reconnect.test.ts` |

---

### Wave 3 — Trust Hardening & Adversarial Verification

| Status | ID | Owner | Scope / Deliverable | Definition of Done & Required Verification | Target Files |
|:---:|---|:---:|---|---|---|
| `[TODO]` | `W3-01` | **Dev A** | **Adversarial Approval & Replay Suite (`S6B-QA-003`)** | Test forged Ed25519 signatures, modified diffs, mismatched challenge IDs, expired approvals, revoked keys, and approval transplant attacks; all fail closed. | `test/security/test_approval_adversarial.py` |
| `[TODO]` | `W3-02` | **Dev A** | **Crash & Kill Recovery Suite (`S6B-QA-004`)** | Process killed via SIGKILL at each stage (post-challenge, post-decision, post-grant, post-intent, mid-worker effect, pre-receipt); restart recovers exactly once with no double execution. | `test/security/test_crash_recovery_matrix.py` |
| `[TODO]` | `W3-03` | **Dev B** | **Sandbox Containment & Escape Suite (`S6B-QA-001`)** | Test attempts to escape workspace root, read host `.env`, open socket to evaluator/runtime, access host network, follow symlinks out of tree, or exhaust memory/PIDs; all denied. | `test/security/test_sandbox_containment.py` |
| `[TODO]` | `W3-04` | **Dev B** | **Exterior Evaluator Tamper Suite (`S6B-QA-002`)** | Test workspace modification of test oracle, injected `conftest.py`/`sitecustomize.py`, symlinked oracle directory, forged verdict signature, wrong peer UID; all yield `EvaluationTampered` or `inconclusive`. | `test/security/test_evaluator_tampering.py` |
| `[TODO]` | `W3-05` | **Dev B** | **Integer Telemetry & Pricing Provenance (`S6B-MD-009`)** | Ensure all metrics use integer microseconds, token counts, monotonic timestamps; pricing table records explicit `pricing_known` provenance; synthetic labels impossible to forge. | `tools/telemetry/metrics.py`<br>`tools/telemetry/collector.py`<br>`test/telemetry/test_integer_telemetry.py` |

---

### Wave 4 — Providers, Packaging & Clean Installation

| Status | ID | Owner | Scope / Deliverable | Definition of Done & Required Verification | Target Files |
|:---:|---|:---:|---|---|---|
| `[TODO]` | `W4-01` | **Dev B** | **Ollama & OpenRouter Model Adapters (`S6B-MD-003/004`)** | Implement Ollama `ModelPort` adapter; harden OpenRouter adapter with strict secret referencing, integer TTFT calculation, pricing table lookup, and explicit non-fallback error handling. | `vanguard/packages/adapters/models/ollama.py`<br>`vanguard/packages/adapters/models/openrouter.py`<br>`test/adapters/test_ollama_openrouter.py` |
| `[TODO]` | `W4-02` | **Dev B** | **OCI Containers & Package Builds (`S6B-REL-002`)** | Build Python wheel/sdist exposing `vanguard` and `vanguard-evaluator`; build npm package `@vanguard/cli`; build minimal OCI worker/evaluator images with measured immutable digests. | `pyproject.toml`<br>`package.json`<br>`containers/Dockerfile.evaluator`<br>`containers/Dockerfile.worker` |
| `[TODO]` | `W4-03` | **Dev A** | **Clean Installation & VM Smoke Test (`CLEAN-INSTALL`)** | Fresh Linux environment installs wheel + npm package; starts daemon, runs task with LAM/Ollama, approves diff, receives verdict, without repository checkout or source tree on disk. | `test/integration/test_clean_install_smoke.sh`<br>`docs/development_guides/install_guide.md` |
| `[TODO]` | `W4-04` | **Dev A** | **Upgrade, Rollback & State Migration Tests (`S6B-REL-005`)** | Test SQLite database migrations across versions; verify graceful rollback without state corruption; verify protocol version rejection on mismatch. | `test/runtime/test_state_migration.py` |

---

### Wave 5 — Release Candidate, Q2 Dogfood & Final Audit (R0–R10)

| Status | ID | Owner | Scope / Deliverable | Definition of Done & Required Verification | Target Files |
|:---:|---|:---:|---|---|---|
| `[TODO]` | `W5-01` | **Dev B** | **3 Real Bug Dogfood Tasks Preregistration (`DOGFOOD-Q2`)** | Prepare 3 real bugs in known repositories with hidden test oracles; configure `vg-code-default` harness pack. | `docs/agile/sprint6B/dogfood_tasks/`<br>`docs/agile/sprint6B/dogfood-log.md` |
| `[TODO]` | `W5-02` | **Joint** | **Execution of 3 Honest Dogfood Runs** | Execute runs using only installed CLI; zero human source edits; record turns, costs, approvals, restart events, and signed evaluator verdicts; operators answer "YES" to reach-for-it-again. | `docs/agile/sprint6B/dogfood-log.md`<br>`docs/agile/sprint6B/evidence/` |
| `[TODO]` | `W5-03` | **Dev A** | **Contract & Receipt Verification (`S6B-EVID-001`)** | Run candidate contract runner; verify SHA-bound receipts with command/output digests, artifact hashes, and independent countersignatures; reseal baseline manifest. | `tools/check_active_mvp_contract.py`<br>`tools/check_baseline_manifest.py`<br>`tools/check_receipt.py` |
| `[TODO]` | `W5-04` | **Joint** | **Independent Release Audit (`RELEASE-R10`)** | `check_active_mvp_contract.py --release` achieves 100% green; R0–R10 receipts signed; Project Lead authorizes GO; create signed Git tag `v0.4.1-beta`. | `docs/agile/sprint6B/INVALIDATED-sprint6-receipts.md`<br>`docs/agile/sprint6B/RELEASE_CANDIDATE_RECEIPT.json` |

---

## 4. Requirement-to-Gate Traceability Reference

| Gate | Gate Name | Owning Backlog Tickets | Required Candidate Evidence |
|---|---|---|---|
| **R0** | Security & Secret Sanitation | `SECURITY-R0`, `S6B-SEC-001..003` | Provider key rotated; clean scan across working tree, all git refs, and built artifacts via `tools/scan_secrets.py`. |
| **R1** | Public Seams & Wire Contracts | `ADR-FREEZE`, `S6B-SA-001`, `S6B-JR-001` | Golden NDJSON vectors pass identical validation in Python and TypeScript; protocol error exit 2 verified. |
| **R2** | Exterior Operator Approval | `APPROVAL`, `S6B-SA-003`, `S6B-JR-003` | Ed25519 signing verified; mutated/forged/replayed approvals fail closed; runtime holds no signing capability. |
| **R3** | Canonical Model Translation | `MODEL-CONTRACT`, `S6B-MD-001` | Anti-corruption translator rejects malformed/unknown/ambiguous tools before Kernel construction; Turn 2 receipts fed back. |
| **R4** | Offline LAM Vertical Path | `LAM-VERTICAL`, `S6B-MD-002` | Multi-turn `read → patch → test → finish` completes through installed CLI and `RuntimeService` with zero production fakes. |
| **R5** | Sandbox Worker Perimeter | `SANDBOX`, `S6B-MD-005/006` | All file and exec verbs route through `bwrap`; host filesystem bypasses impossible; containment receipts verified. |
| **R6** | Ledger Recovery & Kill Matrix | `RECOVERY`, `S6B-SA-002` | Kill matrix passes at all 6 transition points; recovery executes legal next transition without duplicate effects or model re-calls. |
| **R7** | Supervised Exterior Evaluator | `EVALUATOR`, `S6B-MD-007` | UID 10002 daemon passes double probes (immutability + non-pollution); tampered inputs fail; signed verdict in ledger. |
| **R8** | Provider Modes & Telemetry | `PROVIDERS`, `S6B-MD-003/004/009` | LAM, Ollama, and OpenRouter pass identical test suite; integer TTFT/pricing provenance structurally recorded. |
| **R9** | 3 Real-Bug Dogfood Runs | `DOGFOOD-Q2`, `S6B-DOG-001` | 3 preregistered bugs resolved with installed CLI, zero hand-patches, positive operator Q2 answers logged in dogfood log. |
| **R10** | Release Tag & Candidate Audit | `RELEASE-R10`, `S6B-REL-001..006` | Clean VM install, `check_active_mvp_contract.py --release` 100% green, baseline manifest resealed, signed `v0.4.1-beta` tag. |

---

## 5. Developer Quick-Reference & Daily Commands

### Test Execution Commands
```bash
# 1. Run full Python test suite
python3 -m unittest discover -s test

# 2. Run CLI TypeScript typecheck and test suite
npm --workspace @vanguard/cli run typecheck
npm --workspace @vanguard/cli test

# 3. Check architectural boundary imports (Strict lattice)
python3 tools/check_boundaries.py

# 4. Check TCB microkernel line count budget (Must be <= 1438 LOC)
python3 tools/check_tcb_budget.py

# 5. Scan codebase for leaked secrets
python3 tools/scan_secrets.py

# 6. Verify active MVP contract status (Candidate & Release mode)
python3 tools/check_active_mvp_contract.py
python3 tools/check_active_mvp_contract.py --release

# 7. Check baseline manifest integrity
python3 tools/check_baseline_manifest.py
```
