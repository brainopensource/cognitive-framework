# Sprint 4: Inline CodeLens Diffs, Enterprise Telemetry & End-to-End Release

**Sprint ID:** `SPRINT-FE-04`  
**Phase / Wave:** `Wave 4 — Full SOTA Enterprise Experience & Distribution`  
**Foundation Docs:** [`docs/front_v4/007_vanguard_testing_verification_and_e2e_matrix.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/007_vanguard_testing_verification_and_e2e_matrix.md), [`docs/front_v4/010_vanguard_enterprise_security_governance_and_telemetry.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/010_vanguard_enterprise_security_governance_and_telemetry.md), [`docs/front_v4/012_vanguard_frontend_decision_register_and_anti_patterns.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/012_vanguard_frontend_decision_register_and_anti_patterns.md)  
**Primary Goal:** Build inline editor diff decorations with one-click CodeLens Ed25519 signing, integrate enterprise DLP secret masking, run full E2E validation suites, and package desktop installers for Linux, macOS, and Windows.

---

## Sprint Goals & Deliverables

1. **Inline Monaco Diff Reviewer:** Decorate editor lines with green/red background highlights for proposed agent edits and provide inline `[Accept & Sign] / [Reject]` CodeLens buttons.
2. **Enterprise DLP & Masking:** Filter API keys, passwords, and sensitive proprietary regex patterns before prompt leaves the local machine.
3. **Comprehensive E2E Verification:** Run automated scenarios across realistic SWE tasks to guarantee zero regressions.
4. **Standalone Desktop Releases:** Package debloated Code-OSS binary distributions (Linux AppImage/tar.gz, Windows MSI, macOS DMG).

---

## Detailed Task Breakdown

### TASK-FE-401: Inline Diff Decorations & CodeLens Provider
* **Subtasks:**
  * Implement `vscode.TextEditorDecorationType` for proposed insertions (green) and deletions (red).
  * Register `vscode.CodeLensProvider` rendering `[🛡 Accept & Sign (Ed25519)]` and `[❌ Reject]` directly above diff chunks in the active editor.
  * When operator clicks `Accept & Sign`, invoke `OperatorSigner` in the extension host and resolve the approval over NDJSON RPC.
  * Auto-clear decorations once approval is resolved or rejected.
* **Target Files:** `vanguard-ide/extensions/vanguard-panel/src/InlineDiffProvider.ts`, `vanguard-ide/extensions/vanguard-panel/src/ApprovalCodeLens.ts`
* **Est. LOC:** ~360 LOC | **Complexity:** 75/100 | **Seniority:** Senior Dev (4★)

### TASK-FE-402: Enterprise DLP & PII Redaction Filter
* **Subtasks:**
  * Implement local pattern matcher in TypeScript scanning prompt context for secrets (`sk-*`, `ghp_*`, AWS credentials, private keys).
  * Redact sensitive matches with `[REDACTED_SECRET_<HASH>]` before transmitting over network.
  * Add configurable enterprise regex blocklist via `~/.vanguard/dlp_rules.json`.
* **Target Files:** `vanguard/clients/cli/src/application/dlp.ts`, `vanguard-ide/extensions/vanguard-panel/src/DLPFilter.ts`
* **Est. LOC:** ~220 LOC | **Complexity:** 55/100 | **Seniority:** Normal Dev (3★)

### TASK-FE-403: E2E Integration Suite & SWE Task Verification
* **Subtasks:**
  * Run automated headless scenarios (`SCEN-01` through `SCEN-04`) verifying tool execution, syntax patch application, and error recovery.
  * Validate cross-language contract vectors (`test.contracts.t1_wire_contracts`) with 100% pass rate.
  * Perform 100-run stability soak test verifying zero memory leaks in both TUI and IDE Webview.
* **Target Files:** `vanguard/clients/cli/test/e2e/*.test.ts`, `tools/ci/run_frontend_soak.sh`
* **Est. LOC:** ~340 LOC | **Complexity:** 60/100 | **Seniority:** QA / Senior Dev (4★)

### TASK-FE-404: Multi-Platform Desktop Packaging & Release
* **Subtasks:**
  * Build standalone Linux binary distribution (`.tar.gz` and `.AppImage`).
  * Build Windows standalone installer (`.msi` / `.exe` via Inno Setup).
  * Build macOS DMG with notarization scripts.
  * Test fresh installation on clean Linux and Windows VMs.
* **Target Files:** `vanguard-ide/build/package-desktop.sh`, `tools/release/build_matrix.yml`
* **Est. LOC:** ~280 LOC | **Complexity:** 70/100 | **Seniority:** DevOps / Release Engineer (4★)
