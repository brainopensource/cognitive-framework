// Ported from vanguard/clients/cli/src/application/run-view.ts (FE-A owns)
// FE-B3: run-view reducer for webview state management

import type { EventEnvelope } from "../contract/types";

export type ToolView = { name: string; status: string };

export type PendingApproval = {
  approvalId: string;
  unifiedDiff: string;
  proposedPatchDigest: string;
  episodeId: string;
};

export type RunViewModel = {
  thoughts: string[];
  tools: ToolView[];
  tokens: number;
  costMicros: string;
  pendingApproval?: PendingApproval;
  lastKind: string;
};

export function emptyRunView(): RunViewModel {
  return { thoughts: [], tools: [], tokens: 0, costMicros: "0", lastKind: "" };
}

export function reduceRunView(previous: RunViewModel, envelope: EventEnvelope): RunViewModel {
  const next: RunViewModel = {
    ...previous,
    lastKind: envelope.payload.kind,
    thoughts: previous.thoughts.slice(),
    tools: previous.tools.slice(),
  };
  const kind = envelope.payload.kind;
  if (kind === "ObservationProduced" && typeof envelope.payload.text === "string") {
    next.thoughts = [...next.thoughts.slice(-20), envelope.payload.text];
  }
  if (kind === "OperatorInvoked") {
    next.tools = [
      ...next.tools.slice(-20),
      {
        name: String(envelope.payload.tool ?? envelope.payload.verb ?? "tool"),
        status: String(envelope.payload.status ?? "invoked"),
      },
    ];
  }
  if (kind === "BudgetCommitted") {
    if (typeof envelope.payload.tokens === "number") next.tokens = envelope.payload.tokens;
    if (typeof envelope.payload.costMicros === "string") next.costMicros = envelope.payload.costMicros;
  }
  if (kind === "ApprovalRequested") {
    next.pendingApproval = {
      approvalId: String(envelope.payload.approvalId ?? ""),
      unifiedDiff: String(envelope.payload.unifiedDiff ?? envelope.payload.diff ?? ""),
      proposedPatchDigest: String(envelope.payload.proposedPatchDigest ?? ""),
      episodeId: envelope.episodeId ?? String(envelope.payload.episodeId ?? ""),
    };
  }
  if (kind === "ApprovalResolved") next.pendingApproval = undefined;
  return next;
}
