# Sprint 3: Lean Code-OSS Fork, Telemetry Scrubbing & Native Sidebar Webview

**Status:** `VOID` — Code-OSS fork and VS Code extension are D3 VOID. Use `lane_gui_wave1.md`.


**Sprint ID:** `SPRINT-FE-03`  
**Phase / Wave:** `Wave 3 — Integrated IDE Surface (Vanguard for VS Code)`  
**Foundation Docs:** [`docs/front_v4/009_vanguard_lean_vscode_fork_engineering_spec.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/009_vanguard_lean_vscode_fork_engineering_spec.md), [`docs/front_v4/004_vanguard_uiux_views_and_interaction_workflows.md`](file:///home/rocha/Coding/Aether-D-System/docs/front_v4/004_vanguard_uiux_views_and_interaction_workflows.md)  
**Primary Goal:** Set up the Code-OSS / VSCodium base, strip all Microsoft telemetry and proprietary dependencies, and embed the Vanguard React interaction plane into the native Secondary Sidebar (Right Panel).

---

## Sprint Goals & Deliverables

1. **Code-OSS Build & Debloating Pipeline:** Automate scrubbing of Microsoft telemetry endpoints, Microsoft marketplace URLs, and branding from Code-OSS / VSCodium.
2. **Native Webview Secondary Panel:** Build the built-in Vanguard extension hosting the React client inside the right sidebar.
3. **Bidirectional Workspace Context Sync:** Inject open editor files, cursor selections, dirty buffers, and git branches directly into the Vanguard prompt context bar.
4. **Socket Bridge in Extension Host:** Connect the VS Code extension host directly to the local Vanguard Unix Domain Socket / Named Pipe.

---

## Detailed Task Breakdown

### TASK-FE-301: Code-OSS Submodule & Patch Automation
* **Subtasks:**
  * Configure `vanguard-ide` repository with Code-OSS / VSCodium upstream tracking.
  * Write `tools/ide/scrub_code_oss.sh` script to patch `product.json`, disable telemetry flags, redirect to Open-VSX marketplace, and apply Vanguard visual assets (dark theme, logo, splash).
  * Configure build scripts (`gulp vscode-linux-x64`, `gulp vscode-win32-x64`).
* **Target Files:** `vanguard-ide/product.json`, `tools/ide/scrub_code_oss.sh`, `vanguard-ide/build/gulpfile.vscode.js`
* **Est. LOC:** ~380 LOC | **Complexity:** 80/100 | **Seniority:** Principal / Systems Architect (5★)

### TASK-FE-302: Vanguard Webview Extension Core
* **Subtasks:**
  * Create built-in extension in `vanguard-ide/extensions/vanguard-panel/`.
  * Register `viewsContainers.panel` with `id: "vanguard-view-container"` and `views` contribution.
  * Implement `WebviewViewProvider` with secure CSP (Content Security Policy) and message port bridge.
  * Bundle React UI components into standalone Webview script using Vite/esbuild.
* **Target Files:** `vanguard-ide/extensions/vanguard-panel/src/extension.ts`, `vanguard-ide/extensions/vanguard-panel/src/VanguardViewProvider.ts`
* **Est. LOC:** ~420 LOC | **Complexity:** 65/100 | **Seniority:** Senior Dev (4★)

### TASK-FE-303: Extension Host IPC Socket Adapter
* **Subtasks:**
  * Implement Node `net.Socket` client inside the VS Code Extension Host process connecting to `/tmp/vanguard-$UID/runtime.sock` (or Windows Named Pipe).
  * Implement bidirectional postMessage relay: Webview $\leftrightarrow$ Extension Host $\leftrightarrow$ Vanguard Python Daemon.
  * Handle extension reload and socket reconnection gracefully without dropping active stream state.
* **Target Files:** `vanguard-ide/extensions/vanguard-panel/src/DaemonBridge.ts`
* **Est. LOC:** ~290 LOC | **Complexity:** 60/100 | **Seniority:** Senior Dev (4★)

### TASK-FE-304: Real-Time Workspace Context Provider
* **Subtasks:**
  * Subscribe to `vscode.window.onDidChangeActiveTextEditor` and `vscode.workspace.onDidChangeTextDocument`.
  * Extract active file path, relative project path, cursor line number, and active text selection.
  * Extract git repository status via VS Code built-in Git extension API (`vscode.extensions.getExtension('vscode.git')`).
  * Transmit real-time context updates to the Webview prompt input bar.
* **Target Files:** `vanguard-ide/extensions/vanguard-panel/src/WorkspaceContext.ts`
* **Est. LOC:** ~260 LOC | **Complexity:** 50/100 | **Seniority:** Normal Dev (3★)
