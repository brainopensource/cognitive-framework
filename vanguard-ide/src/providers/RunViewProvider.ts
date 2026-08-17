// FE-B1: RunViewProvider — registers the sidebar webview panel.
// FE-B3: streams run events (thoughts/tools/budget) into the webview using the run-view reducer.
// FE-B6: editor context (active file, selection, git branch) folded into StartRun.brief only.

import * as vscode from "vscode";
import * as fs from "node:fs";
import { ReplayRuntimeClient } from "../adapters/replay";
import { LiveRuntimeClient, resolveSocketPath } from "../adapters/live";
import { emptyRunView, reduceRunView } from "../application/run-view";
import type { RunViewModel } from "../application/run-view";
import type { RuntimeClient, StartRunRequest } from "../contract/types";

/** Message types sent from extension → webview */
export type ExtToWebview =
  | { type: "reset" }
  | { type: "update"; vm: RunViewModel; source: string }
  | { type: "error"; message: string }
  | { type: "approval"; approvalId: string; diff: string };

/** Message types sent from webview → extension */
export type WebviewToExt =
  | { type: "approve"; approvalId: string }
  | { type: "reject"; approvalId: string }
  | { type: "ready" };

export class RunViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "vanguard.runView";
  private _view?: vscode.WebviewView;
  private _abortController?: AbortController;

  constructor(private readonly _extensionUri: vscode.Uri) {}

  resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ): void {
    this._view = webviewView;
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };
    webviewView.webview.html = this._getHtml(webviewView.webview);

    webviewView.webview.onDidReceiveMessage((msg: WebviewToExt) => {
      if (msg.type === "ready") {
        this._postMessage({ type: "reset" });
      }
      // approve/reject handled by ApprovalCodeLensProvider via commands
    });
  }

  /** FE-B3: start streaming from a runtime client */
  async startStream(client: RuntimeClient, runId: string, source: string): Promise<void> {
    this._abortController?.abort();
    this._abortController = new AbortController();
    const signal = this._abortController.signal;

    this._postMessage({ type: "reset" });
    let vm = emptyRunView();

    const cursor = { runId };
    for await (const item of client.streamEvents(cursor, signal)) {
      if (signal.aborted) break;
      if (!item.ok) {
        this._postMessage({ type: "error", message: item.error.message });
        break;
      }
      vm = reduceRunView(vm, item.value.envelope);
      this._postMessage({ type: "update", vm, source });

      if (vm.pendingApproval) {
        this._postMessage({
          type: "approval",
          approvalId: vm.pendingApproval.approvalId,
          diff: vm.pendingApproval.unifiedDiff,
        });
      }
    }
  }

  cancelStream(): void {
    this._abortController?.abort();
  }

  /** FE-B3: replay a fixture file without a daemon */
  async replayFixture(fixturePath: string): Promise<void> {
    const text = fs.readFileSync(fixturePath, "utf8");
    const client = ReplayRuntimeClient.fromJsonl(text);
    // Use first runId found in the fixture
    const firstLine = text.split("\n").find((l) => l.trim());
    let runId = "run-1";
    if (firstLine) {
      try {
        const parsed = JSON.parse(firstLine) as { runId?: string };
        runId = parsed.runId ?? "run-1";
      } catch { /* use default */ }
    }
    await this.startStream(client, runId, "replay");
  }

  /** FE-B5/B6: start a live run with editor context folded into brief */
  async startLiveRun(request: StartRunRequest, socketPath?: string): Promise<void> {
    const brief = this._buildBrief(request.brief);
    const config = vscode.workspace.getConfiguration("vanguard");
    const resolvedSocket = resolveSocketPath(socketPath ?? (config.get<string>("socketPath") ?? ""));
    const manifest = request.manifest ?? config.get<string>("manifestPath") ?? "manifest.json";
    const client = new LiveRuntimeClient({ socketPath: resolvedSocket, manifest });
    const ref = await client.startRun({ ...request, brief, manifest });
    if (!ref.ok) {
      vscode.window.showErrorMessage(`Vanguard: StartRun failed — ${ref.error.message}`);
      return;
    }
    await this.startStream(client, ref.value.runId, "live");
  }

  /** FE-B6: active editor / selection / git branch folded into brief text only (D6 — new fields = Joint) */
  private _buildBrief(userBrief?: string): string {
    const parts: string[] = [];
    if (userBrief) parts.push(userBrief);

    const editor = vscode.window.activeTextEditor;
    if (editor) {
      const relPath = vscode.workspace.asRelativePath(editor.document.uri);
      parts.push(`active_file: ${relPath}`);
      const sel = editor.selection;
      if (!sel.isEmpty) {
        parts.push(`selection: L${sel.start.line + 1}-L${sel.end.line + 1}`);
      }
    }

    // Git branch via workspace git extension (best-effort, no invented verbs)
    try {
      const gitExtension = vscode.extensions.getExtension("vscode.git");
      if (gitExtension) {
        const api = (gitExtension.exports as { getAPI(v: number): { repositories: Array<{ state: { HEAD?: { name?: string } } }> } }).getAPI(1);
        const repo = api.repositories[0];
        const branch = repo?.state?.HEAD?.name;
        if (branch) parts.push(`git_branch: ${branch}`);
      }
    } catch { /* git extension not available — skip */ }

    return parts.join("; ");
  }

  private _postMessage(msg: ExtToWebview): void {
    this._view?.webview.postMessage(msg);
  }

  private _getHtml(webview: vscode.Webview): string {
    const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, "dist", "webview.js"));
    const nonce = this._getNonce();
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-${nonce}'; style-src 'unsafe-inline';">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vanguard Run</title>
</head>
<body>
  <div id="root"></div>
  <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
  }

  private _getNonce(): string {
    let text = "";
    const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for (let i = 0; i < 32; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }
}
