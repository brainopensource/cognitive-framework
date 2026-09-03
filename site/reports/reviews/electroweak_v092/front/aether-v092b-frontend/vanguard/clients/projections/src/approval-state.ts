import type { EventEnvelope, ApprovalChallenge, ApprovalDecision } from "@aether/contracts";

export type ApprovalRecord = {
  challenge: ApprovalChallenge;
  status: "pending" | "approved" | "rejected" | "expired";
  decision?: ApprovalDecision;
  requestedAt: string;
  resolvedAt?: string;
};

export type ApprovalState = {
  pendingChallenges: Map<string, ApprovalRecord>;
  resolvedApprovals: ApprovalRecord[];
};

export function emptyApprovalState(): ApprovalState {
  return {
    pendingChallenges: new Map(),
    resolvedApprovals: [],
  };
}

export function reduceApprovalState(previous: ApprovalState, envelope: EventEnvelope): ApprovalState {
  const kind = envelope.payload.kind;

  if (kind === "ApprovalRequested") {
    const approvalId = String(envelope.payload.approvalId ?? "");
    if (!approvalId) return previous;

    const challenge: ApprovalChallenge = {
      approvalId,
      processId: String(envelope.payload.processId ?? ""),
      action: String(envelope.payload.action ?? ""),
      normalizedDiff: String(
        envelope.payload.unifiedDiff ?? envelope.payload.diff ?? envelope.payload.normalizedDiff ?? ""
      ),
      argsDigest: String(envelope.payload.argsDigest ?? ""),
      descriptorDigest: String(envelope.payload.descriptorDigest ?? ""),
      principal: String(envelope.payload.principal ?? "operator"),
      expiresAt: String(envelope.payload.expiresAt ?? ""),
    };

    const nextPending = new Map(previous.pendingChallenges);
    nextPending.set(approvalId, {
      challenge,
      status: "pending",
      requestedAt: envelope.occurredAt,
    });

    return {
      pendingChallenges: nextPending,
      resolvedApprovals: previous.resolvedApprovals.slice(),
    };
  }

  if (kind === "ApprovalResolved") {
    const approvalId = String(envelope.payload.approvalId ?? "");
    const record = previous.pendingChallenges.get(approvalId);
    if (!record) return previous;

    const resolution = envelope.payload.resolution === "rejected" ? "rejected" : "approved";
    const updated: ApprovalRecord = {
      ...record,
      status: resolution,
      resolvedAt: envelope.occurredAt,
    };

    const nextPending = new Map(previous.pendingChallenges);
    nextPending.delete(approvalId);

    return {
      pendingChallenges: nextPending,
      resolvedApprovals: [...previous.resolvedApprovals, updated],
    };
  }

  return previous;
}
