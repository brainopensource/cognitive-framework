// FE-B3: Webview bundle entry — renders run stream (thoughts/tools/budget/approval).
// Design tokens from docs/front_v4/004_ui_ux.md — maps to VS Code CSS variables.
// Runs in browser context (esbuild --platform=browser). No Node.js APIs.

interface VsCodeApi {
  postMessage(msg: unknown): void;
  getState(): unknown;
  setState(state: unknown): void;
}

declare function acquireVsCodeApi(): VsCodeApi;

const vscode = acquireVsCodeApi();

// ── Types (subset, no import from contract/ — webview is a browser bundle) ──
interface ToolView { name: string; status: string; }
interface PendingApproval { approvalId: string; unifiedDiff: string; proposedPatchDigest: string; episodeId: string; }
interface RunViewModel {
  thoughts: string[];
  tools: ToolView[];
  tokens: number;
  costMicros: string;
  pendingApproval?: PendingApproval;
  lastKind: string;
}

type ExtToWebview =
  | { type: "reset" }
  | { type: "update"; vm: RunViewModel; source: string }
  | { type: "error"; message: string }
  | { type: "approval"; approvalId: string; diff: string };

// ── DOM ─────────────────────────────────────────────────────────────────────

function injectStyles(): void {
  const style = document.createElement("style");
  // Semantic tokens map to VS Code CSS variables (004_ui_ux.md)
  style.textContent = `
    :root {
      --vg-success: var(--vscode-charts-green, #4caf50);
      --vg-warning: var(--vscode-charts-yellow, #ff9800);
      --vg-danger:  var(--vscode-charts-red, #f44336);
      --vg-muted:   var(--vscode-descriptionForeground, #888);
      --vg-accent:  var(--vscode-focusBorder, #007acc);
      --vg-bg:      var(--vscode-editor-background, #1e1e1e);
      --vg-fg:      var(--vscode-editor-foreground, #d4d4d4);
      --vg-border:  var(--vscode-panel-border, #444);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; padding: 8px;
      font-family: var(--vscode-font-family, monospace);
      font-size: var(--vscode-font-size, 12px);
      background: var(--vg-bg); color: var(--vg-fg);
    }
    #source-badge {
      display: inline-block; padding: 2px 6px; border-radius: 3px;
      font-size: 10px; font-weight: bold; text-transform: uppercase;
      letter-spacing: 0.08em; margin-bottom: 8px;
      background: var(--vscode-badge-background, #444);
      color: var(--vscode-badge-foreground, #fff);
    }
    #source-badge.mock  { background: var(--vg-warning); color: #000; }
    #source-badge.replay { background: var(--vg-accent); }
    #source-badge.live  { background: var(--vg-success); color: #000; }
    #last-kind {
      font-size: 11px; color: var(--vg-muted); margin-bottom: 6px;
    }
    .section { margin-bottom: 10px; }
    .section-title {
      font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em;
      color: var(--vg-muted); margin-bottom: 4px;
    }
    .thought {
      padding: 4px 6px; margin-bottom: 3px; border-left: 2px solid var(--vg-accent);
      background: var(--vscode-editor-inactiveSelectionBackground, #2a2a2a);
      font-size: 11px; white-space: pre-wrap; word-break: break-word;
    }
    .tool-row {
      display: flex; align-items: center; gap: 6px;
      padding: 3px 0; font-size: 11px;
    }
    .tool-name { font-weight: bold; }
    .tool-status { color: var(--vg-muted); font-size: 10px; }
    .budget {
      font-size: 11px; color: var(--vg-muted);
    }
    #approval-panel {
      border: 1px solid var(--vg-warning); border-radius: 4px;
      padding: 8px; margin-top: 8px;
    }
    #approval-panel h3 { margin: 0 0 6px; font-size: 12px; color: var(--vg-warning); }
    #approval-diff {
      font-family: monospace; font-size: 10px; white-space: pre; overflow: auto;
      max-height: 200px; background: var(--vscode-textCodeBlock-background, #1a1a1a);
      padding: 6px; border-radius: 3px; margin-bottom: 8px;
    }
    .approval-actions { display: flex; gap: 8px; }
    .btn {
      padding: 4px 10px; border: none; border-radius: 3px; cursor: pointer;
      font-size: 11px; font-weight: bold;
    }
    .btn-approve { background: var(--vg-success); color: #000; }
    .btn-reject  { background: var(--vg-danger);  color: #fff; }
    .btn:hover { opacity: 0.85; }
    #error-banner {
      padding: 6px 8px; background: var(--vg-danger); color: #fff;
      border-radius: 3px; font-size: 11px; margin-bottom: 8px;
    }
    .empty { color: var(--vg-muted); font-style: italic; font-size: 11px; }
  `;
  document.head.appendChild(style);
}

function el(id: string): HTMLElement {
  return document.getElementById(id)!;
}

function createLayout(): void {
  document.body.innerHTML = `
    <div id="source-badge" class="">—</div>
    <div id="last-kind" class=""></div>
    <div id="error-banner" style="display:none"></div>
    <div class="section">
      <div class="section-title">Thoughts</div>
      <div id="thoughts-list"><div class="empty">No thoughts yet.</div></div>
    </div>
    <div class="section">
      <div class="section-title">Tools</div>
      <div id="tools-list"><div class="empty">No tools invoked.</div></div>
    </div>
    <div class="section">
      <div class="section-title">Budget</div>
      <div id="budget" class="budget">tokens: —  cost: —</div>
    </div>
    <div id="approval-panel" style="display:none">
      <h3>⚠ Approval Required</h3>
      <div id="approval-diff"></div>
      <div class="approval-actions">
        <button class="btn btn-approve" id="btn-approve">Approve &amp; Sign</button>
        <button class="btn btn-reject" id="btn-reject">Reject</button>
      </div>
    </div>
  `;
}

let _currentApprovalId: string | undefined;

function bindButtons(): void {
  document.getElementById("btn-approve")?.addEventListener("click", () => {
    if (_currentApprovalId) vscode.postMessage({ type: "approve", approvalId: _currentApprovalId });
  });
  document.getElementById("btn-reject")?.addEventListener("click", () => {
    if (_currentApprovalId) vscode.postMessage({ type: "reject", approvalId: _currentApprovalId });
  });
}

function renderUpdate(vm: RunViewModel, source: string): void {
  // Source badge
  const badge = el("source-badge");
  badge.textContent = source;
  badge.className = source;

  // Last kind
  el("last-kind").textContent = vm.lastKind ? `↳ ${vm.lastKind}` : "";

  // Error banner — clear on update
  const errBanner = el("error-banner");
  errBanner.style.display = "none";

  // Thoughts
  const thoughtsList = el("thoughts-list");
  if (vm.thoughts.length === 0) {
    thoughtsList.innerHTML = '<div class="empty">No thoughts yet.</div>';
  } else {
    thoughtsList.innerHTML = vm.thoughts
      .map((t) => `<div class="thought">${escHtml(t)}</div>`)
      .join("");
  }

  // Tools
  const toolsList = el("tools-list");
  if (vm.tools.length === 0) {
    toolsList.innerHTML = '<div class="empty">No tools invoked.</div>';
  } else {
    toolsList.innerHTML = vm.tools
      .map((t) => `<div class="tool-row"><span class="tool-name">${escHtml(t.name)}</span><span class="tool-status">${escHtml(t.status)}</span></div>`)
      .join("");
  }

  // Budget
  el("budget").textContent = `tokens: ${vm.tokens}  cost: ${vm.costMicros}µ$`;

  // Approval panel
  const approvalPanel = el("approval-panel");
  if (vm.pendingApproval) {
    _currentApprovalId = vm.pendingApproval.approvalId;
    el("approval-diff").textContent = vm.pendingApproval.unifiedDiff || "(no diff)";
    approvalPanel.style.display = "block";
  } else {
    _currentApprovalId = undefined;
    approvalPanel.style.display = "none";
  }
}

function renderReset(): void {
  el("source-badge").textContent = "—";
  el("source-badge").className = "";
  el("last-kind").textContent = "";
  el("error-banner").style.display = "none";
  el("thoughts-list").innerHTML = '<div class="empty">No thoughts yet.</div>';
  el("tools-list").innerHTML = '<div class="empty">No tools invoked.</div>';
  el("budget").textContent = "tokens: —  cost: —";
  el("approval-panel").style.display = "none";
}

function renderError(message: string): void {
  const b = el("error-banner");
  b.textContent = `Error: ${message}`;
  b.style.display = "block";
}

function renderApproval(approvalId: string, diff: string): void {
  _currentApprovalId = approvalId;
  el("approval-diff").textContent = diff || "(no diff)";
  el("approval-panel").style.display = "block";
}

function escHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ── Boot ────────────────────────────────────────────────────────────────────

injectStyles();
createLayout();
bindButtons();

window.addEventListener("message", (event: MessageEvent<ExtToWebview>) => {
  const msg = event.data;
  switch (msg.type) {
    case "reset":  renderReset(); break;
    case "update": renderUpdate(msg.vm, msg.source); break;
    case "error":  renderError(msg.message); break;
    case "approval": renderApproval(msg.approvalId, msg.diff); break;
  }
});

// Tell extension we are ready
vscode.postMessage({ type: "ready" });
