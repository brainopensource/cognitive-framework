// FE-B1: Extension entry point — activate/deactivate, register sidebar, commands, CodeLens.
// FE-B3: Replay command streams through RunViewProvider without a daemon.
// FE-B4: Approve & Sign / Reject commands use OperatorSigner (Ed25519).
// FE-B5: Live socket bridge via LiveRuntimeClient.
// FE-B6: Editor context folded into brief via RunViewProvider._buildBrief.
// FE-B8: .vsix produced by scripts/bundle-vsix.js.

import * as vscode from "vscode";
import * as path from "node:path";
import * as fs from "node:fs";
import { RunViewProvider } from "./providers/RunViewProvider";
import {
  ApprovalCodeLensProvider,
  APPROVE_COMMAND,
  REJECT_COMMAND,
  clearPendingApproval,
  signApproval,
} from "./providers/ApprovalCodeLensProvider";
import { OperatorSigner } from "./adapters/signer";
import { LiveRuntimeClient, resolveSocketPath } from "./adapters/live";

export function activate(context: vscode.ExtensionContext): void {
  const signer = new OperatorSigner();
  const provider = new RunViewProvider(context.extensionUri);
  const codeLensProvider = new ApprovalCodeLensProvider(signer);

  // Register sidebar webview
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(RunViewProvider.viewType, provider)
  );

  // Register CodeLens for vanguard-diff: documents
  context.subscriptions.push(
    vscode.languages.registerCodeLensProvider({ scheme: "vanguard-diff" }, codeLensProvider)
  );

  // ── Commands ────────────────────────────────────────────────────────────────

  // vanguard.startRun: start a live run using editor context
  context.subscriptions.push(
    vscode.commands.registerCommand("vanguard.startRun", async () => {
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? ".";
      const brief = await vscode.window.showInputBox({
        prompt: "Brief description for this Vanguard run",
        placeHolder: "Describe the task…",
      });
      if (brief === undefined) return; // cancelled
      const config = vscode.workspace.getConfiguration("vanguard");
      const manifest = config.get<string>("manifestPath") ?? "manifest.json";
      await provider.startLiveRun({ repo: workspaceFolder, brief, manifest });
    })
  );

  // vanguard.cancelRun: abort the active stream
  context.subscriptions.push(
    vscode.commands.registerCommand("vanguard.cancelRun", () => {
      provider.cancelStream();
      vscode.window.showInformationMessage("Vanguard: run cancelled.");
    })
  );

  // vanguard.replayFixture: replay a .jsonl fixture without daemon (FE-B3 DoD)
  context.subscriptions.push(
    vscode.commands.registerCommand("vanguard.replayFixture", async () => {
      // Default fixture: look in vanguard/clients/cli/fixtures relative to workspace
      const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? ".";
      const defaultFixture = path.join(workspaceFolder, "vanguard", "clients", "cli", "fixtures", "successful-episode.jsonl");

      const picked = await vscode.window.showOpenDialog({
        canSelectFiles: true,
        canSelectFolders: false,
        canSelectMany: false,
        filters: { "JSONL fixtures": ["jsonl"] },
        defaultUri: fs.existsSync(defaultFixture)
          ? vscode.Uri.file(defaultFixture)
          : undefined,
        title: "Select a Vanguard replay fixture (.jsonl)",
      });
      if (!picked?.[0]) return;
      await provider.replayFixture(picked[0].fsPath);
      vscode.window.showInformationMessage(`Vanguard: replaying fixture ${path.basename(picked[0].fsPath)} (source: replay)`);
    })
  );

  // vanguard.showStatus: probe the daemon via connect-only (J2 — no Ping)
  context.subscriptions.push(
    vscode.commands.registerCommand("vanguard.showStatus", async () => {
      const config = vscode.workspace.getConfiguration("vanguard");
      const socketPath = resolveSocketPath(config.get<string>("socketPath") ?? "");
      const client = new LiveRuntimeClient({ socketPath });
      const result = await client.getDaemonStatus();
      if (result.ok) {
        vscode.window.showInformationMessage(`Vanguard daemon: ${result.value.status} at ${result.value.socketPath}`);
      } else {
        vscode.window.showWarningMessage(`Vanguard daemon: ${result.error.message}`);
      }
    })
  );

  // vanguard.approveItem: sign and resolve an approval (FE-B4)
  context.subscriptions.push(
    vscode.commands.registerCommand(APPROVE_COMMAND, async (approvalId: string) => {
      const decision = signApproval(approvalId, signer, "approved");
      if (!decision) {
        vscode.window.showWarningMessage(`Vanguard: approval ${approvalId} not found in current session.`);
        return;
      }
      const config = vscode.workspace.getConfiguration("vanguard");
      const socketPath = resolveSocketPath(config.get<string>("socketPath") ?? "");
      const client = new LiveRuntimeClient({ socketPath });
      const result = await client.resolveApproval({
        approvalId,
        decision: "approve",
        signature: decision.signature,
        signerKeyRef: decision.keyId,
      });
      if (result.ok) {
        clearPendingApproval(approvalId);
        codeLensProvider.refresh();
        vscode.window.showInformationMessage(`Vanguard: approved ${approvalId}`);
      } else {
        vscode.window.showErrorMessage(`Vanguard: approve failed — ${result.error.message}`);
      }
    })
  );

  // vanguard.rejectItem: reject an approval (FE-B4)
  context.subscriptions.push(
    vscode.commands.registerCommand(REJECT_COMMAND, async (approvalId: string) => {
      const decision = signApproval(approvalId, signer, "rejected");
      if (!decision) {
        vscode.window.showWarningMessage(`Vanguard: approval ${approvalId} not found in current session.`);
        return;
      }
      const config = vscode.workspace.getConfiguration("vanguard");
      const socketPath = resolveSocketPath(config.get<string>("socketPath") ?? "");
      const client = new LiveRuntimeClient({ socketPath });
      const result = await client.resolveApproval({
        approvalId,
        decision: "reject",
        signature: decision.signature,
        signerKeyRef: decision.keyId,
      });
      if (result.ok) {
        clearPendingApproval(approvalId);
        codeLensProvider.refresh();
        vscode.window.showInformationMessage(`Vanguard: rejected ${approvalId}`);
      } else {
        vscode.window.showErrorMessage(`Vanguard: reject failed — ${result.error.message}`);
      }
    })
  );

  // Re-export registerPendingApproval for use by RunViewProvider webview message handler
  // (extension host side only — approval data crosses host→webview only as diff text)
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("vanguard")) {
        vscode.window.showInformationMessage("Vanguard: configuration updated.");
      }
    })
  );
}

export function deactivate(): void {
  // nothing to clean up beyond subscriptions
}
