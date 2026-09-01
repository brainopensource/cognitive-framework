import type { EventEnvelope } from "@aether/contracts";

export type ToolInvocationView = {
  name: string;
  status: "invoked" | "running" | "completed" | "failed";
  argsSummary?: string;
  durationMs?: number;
  error?: string;
};

export type PendingApproval = {
  approvalId: string;
  unifiedDiff: string;
  proposedPatchDigest: string;
  episodeId: string;
  argsDigest: string;
  descriptorDigest: string;
  expiresAt: string;
};

export type ProjectedArtifact = {
  digest: string;
  kind: string;
  path?: string;
  sizeBytes?: number;
};

export type RunSnapshotModel = {
  runId: string;
  status: "pending" | "running" | "satisfied" | "failed" | "cancelled" | "awaiting_approval";
  verdict?: string;
  thoughts: string[];
  tools: ToolInvocationView[];
  tokens: {
    inTokens: number;
    outTokens: number;
    totalTokens: number;
  };
  costMicros: string;
  pendingApproval?: PendingApproval;
  artifacts: ProjectedArtifact[];
  lastKind: string;
  lastSeq: string;
  turns: number;
  startTime?: string;
  endTime?: string;
};

export function emptyRunSnapshot(runId: string = ""): RunSnapshotModel {
  return {
    runId,
    status: "pending",
    thoughts: [],
    tools: [],
    tokens: { inTokens: 0, outTokens: 0, totalTokens: 0 },
    costMicros: "0",
    artifacts: [],
    lastKind: "",
    lastSeq: "0",
    turns: 0,
  };
}

export function reduceRunSnapshot(
  previous: RunSnapshotModel,
  envelope: EventEnvelope
): RunSnapshotModel {
  const next: RunSnapshotModel = {
    ...previous,
    runId: envelope.runId ?? previous.runId,
    lastKind: envelope.payload.kind,
    lastSeq: envelope.seq,
    thoughts: previous.thoughts.slice(),
    tools: previous.tools.slice(),
    artifacts: previous.artifacts.slice(),
    tokens: { ...previous.tokens },
  };

  if (!next.startTime && envelope.occurredAt) {
    next.startTime = envelope.occurredAt;
  }
  next.endTime = envelope.recordedAt || envelope.occurredAt;

  const kind = envelope.payload.kind;

  if (kind === "GoalDeclared" || kind === "EpisodeStarted") {
    next.status = "running";
  }

  if (kind === "TurnStarted" || kind === "ModelProposalProduced") {
    next.turns += 1;
  }

  if (kind === "ObservationProduced" && typeof envelope.payload.text === "string") {
    next.thoughts = [...next.thoughts.slice(-50), envelope.payload.text];
  }

  if (kind === "OperatorInvoked" || kind === "EffectStarted") {
    const name = String(envelope.payload.tool ?? envelope.payload.verb ?? envelope.payload.action ?? "tool");
    next.tools = [
      ...next.tools.slice(-50),
      {
        name,
        status: kind === "EffectStarted" ? "running" : "invoked",
        argsSummary: typeof envelope.payload.argsSummary === "string" ? envelope.payload.argsSummary : undefined,
      },
    ];
  }

  if (kind === "EffectCompleted") {
    if (next.tools.length > 0) {
      const last = { ...next.tools[next.tools.length - 1]! };
      last.status = "completed";
      if (typeof envelope.payload.durationMs === "number") {
        last.durationMs = envelope.payload.durationMs;
      }
      next.tools = [...next.tools.slice(0, -1), last];
    }
  }

  if (kind === "EffectFailed") {
    if (next.tools.length > 0) {
      const last = { ...next.tools[next.tools.length - 1]! };
      last.status = "failed";
      last.error = String(envelope.payload.error ?? "Effect execution failed");
      next.tools = [...next.tools.slice(0, -1), last];
    }
  }

  if (kind === "BudgetCommitted") {
    if (typeof envelope.payload.tokens === "number") {
      next.tokens.totalTokens = envelope.payload.tokens;
    }
    if (typeof envelope.payload.inTokens === "number") {
      next.tokens.inTokens = envelope.payload.inTokens;
    }
    if (typeof envelope.payload.outTokens === "number") {
      next.tokens.outTokens = envelope.payload.outTokens;
    }
    if (typeof envelope.payload.costMicros === "string") {
      next.costMicros = envelope.payload.costMicros;
    }
  }

  if (kind === "ApprovalRequested") {
    next.status = "awaiting_approval";
    next.pendingApproval = {
      approvalId: String(envelope.payload.approvalId ?? ""),
      unifiedDiff: String(
        envelope.payload.unifiedDiff ?? envelope.payload.diff ?? envelope.payload.normalizedDiff ?? ""
      ),
      proposedPatchDigest: String(envelope.payload.proposedPatchDigest ?? ""),
      episodeId: envelope.episodeId ?? String(envelope.payload.episodeId ?? ""),
      argsDigest: String(envelope.payload.argsDigest ?? ""),
      descriptorDigest: String(envelope.payload.descriptorDigest ?? ""),
      expiresAt: String(envelope.payload.expiresAt ?? ""),
    };
  }

  if (kind === "ApprovalResolved") {
    next.pendingApproval = undefined;
    if (next.status === "awaiting_approval") {
      next.status = "running";
    }
  }

  if (kind === "ArtifactCreated") {
    const digest = String(envelope.payload.digest ?? envelope.payload.artifactId ?? "");
    if (digest) {
      next.artifacts.push({
        digest,
        kind: String(envelope.payload.kindCategory ?? envelope.payload.artifactKind ?? "artifact"),
        path: typeof envelope.payload.path === "string" ? envelope.payload.path : undefined,
        sizeBytes: typeof envelope.payload.sizeBytes === "number" ? envelope.payload.sizeBytes : undefined,
      });
    }
  }

  if (kind === "EpisodeCompleted" || kind === "RunCompleted" || kind === "VerdictProduced") {
    const verdict = String(envelope.payload.verdict ?? envelope.payload.outcome ?? "satisfied");
    next.verdict = verdict;
    if (verdict === "1" || verdict === "satisfied" || verdict === "passed") {
      next.status = "satisfied";
    } else if (verdict === "cancelled") {
      next.status = "cancelled";
    } else {
      next.status = "failed";
    }
  }

  if (kind === "RunCancelled") {
    next.status = "cancelled";
  }

  return next;
}

export function foldEvents(envelopes: Iterable<EventEnvelope>, initialRunId: string = ""): RunSnapshotModel {
  let model = emptyRunSnapshot(initialRunId);
  for (const env of envelopes) {
    model = reduceRunSnapshot(model, env);
  }
  return model;
}

export { reduceRunSnapshot as reduceRunView, emptyRunSnapshot as emptyRunView };
