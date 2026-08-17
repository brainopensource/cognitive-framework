// FE-B1 stub / FE-B4: Approval CodeLens — [Approve & Sign] / [Reject] lenses
// appear on lines where ApprovalRequested envelope payload data is shown.
// The real diff-document rendering is triggered from RunViewProvider via the webview.

import * as vscode from "vscode";
import { OperatorSigner } from "../adapters/signer";
import type { ApprovalChallenge } from "../contract/types";

export const APPROVE_COMMAND = "vanguard.approveItem";
export const REJECT_COMMAND = "vanguard.rejectItem";

/** Shared state for pending approvals keyed by approvalId */
const pendingApprovals = new Map<string, ApprovalChallenge>();

export function registerPendingApproval(challenge: ApprovalChallenge): void {
  pendingApprovals.set(challenge.approvalId, challenge);
}

export function clearPendingApproval(approvalId: string): void {
  pendingApprovals.delete(approvalId);
}

/** FE-B4: CodeLens provider stub — surfaces on vanguard-diff documents */
export class ApprovalCodeLensProvider implements vscode.CodeLensProvider {
  private _onDidChangeCodeLenses = new vscode.EventEmitter<void>();
  onDidChangeCodeLenses = this._onDidChangeCodeLenses.event;

  constructor(private readonly _signer: OperatorSigner) {}

  refresh(): void {
    this._onDidChangeCodeLenses.fire();
  }

  provideCodeLenses(document: vscode.TextDocument): vscode.CodeLens[] {
    if (!document.uri.scheme.startsWith("vanguard")) return [];
    const lenses: vscode.CodeLens[] = [];
    const text = document.getText();
    const lines = text.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line?.includes("approvalId:")) {
        const range = new vscode.Range(i, 0, i, line.length);
        const idMatch = line.match(/approvalId:\s*(\S+)/);
        const approvalId = idMatch?.[1] ?? "";
        lenses.push(
          new vscode.CodeLens(range, {
            title: "$(check) Approve & Sign",
            command: APPROVE_COMMAND,
            arguments: [approvalId],
          }),
          new vscode.CodeLens(range, {
            title: "$(x) Reject",
            command: REJECT_COMMAND,
            arguments: [approvalId],
          })
        );
      }
    }
    return lenses;
  }
}

/** FE-B4: sign and return an ApprovalDecision for a pending challenge */
export function signApproval(approvalId: string, signer: OperatorSigner, resolution: "approved" | "rejected") {
  const challenge = pendingApprovals.get(approvalId);
  if (!challenge) return null;
  return signer.signChallenge(challenge, resolution, "operator");
}
