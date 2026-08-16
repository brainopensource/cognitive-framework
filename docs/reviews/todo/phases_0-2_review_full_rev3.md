# Vanguard Phases 0–2 Final Gate Review, Revision 3

**Review date:** 2026-08-15  
**Scope:** Sprints 0–6 and Phase 2 closure claims  
**Purpose:** Final review before building and shipping the MVP Beta

| Sprint | Done | Todo / final status |
|---|---|---|
| 0 | Governance baseline, ICD, threat plan, contract and CI controls | Branch protection and independent sign-off remain unverified. ⚠️ Conditional |
| 1 | Canonical schemas, primitives, selectors and wire vectors | Schemas remain DRAFT; human reconstruction/timing gates remain. ⚠️ Conditional |
| 2 | Kernel S0–S12, attenuation, budgets, ledger, artifact graph and manifests | No material implementation blocker found. ✅ Done |
| 3 | Model/evaluator/sandbox/environment ports, episode loop and process replay | Process and approval state machines still need product-path unification. ⚠️ Partial |
| 4 | Trust spine, Git/OpenRouter adapters, rootless runner and disposable removal | Sandbox runner is not used by production composition. ⚠️ Partial |
| 5 | Context compiler, competence prior, evaluator probes and provider adapter | Exterior evaluator daemon, mandatory invocation and true streaming remain. ❌ Todo |
| 6 | Composition primitives, approval classes, TUI, telemetry helpers and scripted harness | Live runtime/CLI, secure approval, recovery, evaluator and genuine dogfood remain. ❌ Todo |

| Feature | Done | Todo |
|---|---|---|
| Verification | 341 Python, 12 CLI and 26 broken-harness cases pass | Passing component tests do not prove the product path |
| UUIDv7 | Timestamp-first RFC-shaped generators added | Monotonic ordering claim is false within one millisecond |
| Context | L1–L5 compilation and tool-result provenance added | Enforce for every production model call |
| OpenRouter | SSE delta/tool assembly and integer micros added | Transport buffers the full response; TTFT is not true first-token timing |
| Sandbox | Rootless Bubblewrap runner and probes exist | Route every effect through it |
| Approval/recovery | Descriptor binding and ledger-verification primitives exist | Runtime still owns the HMAC key; product root does not perform ledger-only restart |
| Evaluator | Immutability/non-pollution probes exist | Dedicated process, UID/image attestation, authenticated IPC and signed verdict |
| CLI | TUI, diff display and correction UI exist | Live commands still return `not_available`; interactive mode defaults to scenario |
| Telemetry | Source label and USD micros fields added | Synthetic constants can still be labelled live; timing/USD remain floats; `REQ-BENCH-001` is absent |
| Dogfood/R10 | Three scripted runs and receipts were generated | Genuine provider/CLI/sandbox/restart/exterior-evaluator run and sealed independent evidence |

| Severity | Final-gate flaw | Decision / required closure |
|---|---|---|
| Critical | No `RuntimeService`; `vg` defaults to scenario and live operations are unavailable ([main.tsx](../../../vanguard/clients/cli/src/main.tsx), [live.ts](../../../vanguard/clients/cli/src/adapters/live.ts)) | Implement and test the sole live operator path |
| Critical | Composition executes directly through `GitEnvironment`, never `RootlessSandboxRunner` ([root.py](../../../vanguard/packages/runtime/root.py)) | Wire all effects through the sandbox |
| Critical | Runtime creates the signing authority from a default/shared HMAC key ([root.py](../../../vanguard/packages/runtime/root.py)) | External signer; runtime holds verification authority only |
| Critical | Evaluator is directly injected; dogfood accepts the current UID and a fabricated image digest ([run_dogfood_r9.py](../../../tools/run_dogfood_r9.py)) | Real supervisor-attested exterior service |
| High | Dogfood embeds the completed fix, uses a scripted model and in-memory SQLite ([run_dogfood_r9.py](../../../tools/run_dogfood_r9.py)) | Repeat three independently reviewed runs through the real path |
| High | SSE is parsed only after transport completion, so recorded TTFT is response latency ([openrouter.py](../../../vanguard/packages/adapters/models/openrouter.py)) | Incremental byte streaming and first validated-delta timestamp |
| High | Telemetry runner injects fixed sandbox timings into a collector defaulted to `live` ([runner.py](../../../tools/telemetry/runner.py)) | Make source provenance structural and use integer observations |
| Critical | Evidence is uncommitted, receipts lack candidate SHA/countersignatures, baseline says `authorising_commit: pending` ([baseline-manifest.json](../../sprint0/baseline-manifest.json)) | Produce clean-clone, exact-SHA, independently signed receipts |
| Critical | Contract checker validates only a non-empty evidence string, not receipt existence/SHA/result ([check_active_mvp_contract.py](../../../tools/check_active_mvp_contract.py)) | Strengthen R10 before changing rows to covered |
| Critical | Old credential commit remains reachable under `refs/original`; no blocking secret scanner exists | Purge all refs and add scanning evidence |
| **Final verdict** | **The fixes improve components but do not close the rev2 Beta gates** | **NO-GO — do not build or ship the MVP Beta yet** |
