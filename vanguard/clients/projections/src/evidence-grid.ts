import type { EventEnvelope } from "@aether/contracts";

export type EvidenceClaimItem = {
  claimId: string;
  claimType: string;
  statement: string;
  status: "verified" | "unverified" | "disputed";
  sourceEventId: string;
  artifactId?: string;
  verifier?: string;
};

export type EvidenceGrid = {
  runId: string;
  claims: EvidenceClaimItem[];
  artifacts: Array<{
    digest: string;
    path?: string;
    kind: string;
    createdAt: string;
  }>;
  verdicts: Array<{
    verdict: string;
    evaluator: string;
    signature?: string;
    timestamp: string;
  }>;
};

export function emptyEvidenceGrid(runId: string = ""): EvidenceGrid {
  return {
    runId,
    claims: [],
    artifacts: [],
    verdicts: [],
  };
}

export function reduceEvidence(previous: EvidenceGrid, envelope: EventEnvelope): EvidenceGrid {
  const next: EvidenceGrid = {
    ...previous,
    runId: envelope.runId ?? previous.runId,
    claims: previous.claims.slice(),
    artifacts: previous.artifacts.slice(),
    verdicts: previous.verdicts.slice(),
  };

  const kind = envelope.payload.kind;

  if (kind === "ArtifactCreated") {
    const digest = String(envelope.payload.digest ?? envelope.payload.artifactId ?? "");
    if (digest) {
      next.artifacts.push({
        digest,
        path: typeof envelope.payload.path === "string" ? envelope.payload.path : undefined,
        kind: String(envelope.payload.kindCategory ?? envelope.payload.artifactKind ?? "artifact"),
        createdAt: envelope.occurredAt,
      });
    }
  }

  if (kind === "EvidenceClaimProduced" || kind === "EvidenceRecorded") {
    next.claims.push({
      claimId: String(envelope.payload.claimId ?? envelope.eventId),
      claimType: String(envelope.payload.claimType ?? "assertion"),
      statement: String(envelope.payload.statement ?? envelope.payload.text ?? ""),
      status: envelope.payload.status === "verified" ? "verified" : "unverified",
      sourceEventId: envelope.eventId,
      artifactId: typeof envelope.payload.artifactId === "string" ? envelope.payload.artifactId : undefined,
      verifier: typeof envelope.payload.verifier === "string" ? envelope.payload.verifier : undefined,
    });
  }

  if (kind === "EvaluationCompleted" || kind === "VerdictProduced" || kind === "EpisodeCompleted") {
    next.verdicts.push({
      verdict: String(envelope.payload.verdict ?? envelope.payload.outcome ?? "satisfied"),
      evaluator: String(envelope.payload.evaluator ?? envelope.principal),
      signature: typeof envelope.payload.signature === "string" ? envelope.payload.signature : undefined,
      timestamp: envelope.occurredAt,
    });
  }

  return next;
}
