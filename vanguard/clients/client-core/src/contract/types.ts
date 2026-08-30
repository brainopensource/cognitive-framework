export type ClientContractVersion = "0.1";
export type StreamSource = "mock" | "replay" | "live";

/**
 * Canonical vg.4 wire error vocabulary (integration_plan.md §4.5), shared
 * byte-for-byte with `schemas/v4/runtime-service.schema.json#/$defs/ErrorCode`
 * and Python's `runtime/service/contract.py:ERROR_CODES`. `transport_interrupted`
 * is the one client-only addition: a synthetic code for a dropped connection,
 * never sent by the daemon itself.
 */
export type ClientFailure = {
  code:
    | "invalid_request"
    | "unauthenticated"
    | "permission_denied"
    | "not_found"
    | "conflict"
    | "incompatible_version"
    | "frame_too_large"
    | "rate_limited"
    | "not_available"
    | "internal"
    | "transport_interrupted";
  message: string;
  retryable: boolean;
  details?: Readonly<Record<string, unknown>>;
};

export type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: ClientFailure };

export type EventEnvelope = {
  schemaVersion: "vg.4";
  eventId: string;
  scope: "episode" | "governance" | "evolution" | "recovery";
  runId?: string;
  episodeId?: string;
  branchId?: string;
  parentEventId?: string;
  traceId: string;
  spanId: string;
  seq: string;
  occurredAt: string;
  recordedAt: string;
  principal: string;
  principalRole?: "user" | "operator" | "episode" | "process" | "evaluator" | "release";
  tenantId: string;
  ownerId: string;
  confidentiality: string;
  retentionClass: string;
  trainability: string;
  redactionStatus: string;
  encryptionKeyRef?: string;
  environmentSnapshot?: string;
  payload: Record<string, unknown> & { kind: string };
  [key: string]: unknown;
};

export type EventCursor = { runId: string; afterSeq?: string };
export type StreamItem = {
  contractVersion: ClientContractVersion;
  source: StreamSource;
  envelope: EventEnvelope;
};

export type StartRunRequest = {
  repo: string;
  prompt?: string;
  brief?: string;
  runId?: string;
  resumeFrom?: string;
  checkpointEvery?: number;
  model?: string;
  manifest?: string;
  autoApprove?: boolean;
};

export type RunRef = { runId: string; episodeId?: string };
export type RunSnapshot = {
  runId: string;
  status: string;
  seq: string;
  verdict?: string;
  metrics?: Record<string, unknown>;
};
export type RunSummary = {
  runId: string;
  status: string;
  seq: string;
  occurredAt?: string;
  verdict?: string;
};
export type CommandReceipt = {
  runId: string;
  command: "cancel" | "checkpoint" | "resume" | "resolve_approval" | "record_correction" | "daemon_signal";
  status: "requested" | "accepted" | "rejected";
  detail?: string;
  result?: Record<string, unknown>;
};
export type ResumeRunRequest = { runId: string; checkpointId?: string };
export type ResolveApprovalRequest = {
  approvalId: string;
  decision: "approve" | "reject" | "approved" | "rejected" | ApprovalDecision;
  signature?: string;
  signerKeyRef?: string;
};

export type DaemonStatus = {
  status: "running" | "stopped" | "unresponsive";
  socketPath: string;
  pid?: number;
  version?: string;
  uptimeSeconds?: number;
};

export type CorrectionRecord = {
  episodeId: string;
  proposedPatchDigest: string;
  acceptedPatchDigest: string;
  reasonCodes: ReadonlyArray<string>;
  magnitude: "minor" | "moderate" | "major";
  scope: "user" | "team" | "repo" | "domain" | "general";
  correctingPrincipalRole: NonNullable<EventEnvelope["principalRole"]>;
};

export type ArtifactExplanation = {
  artifactId: string;
  status: "active" | "inactive" | "unknown";
  prediction: string;
  activatedBy: ReadonlyArray<{ evidence: string; strength?: number }>;
  demotedBy: ReadonlyArray<{ condition: string; effect: string }>;
  freshness: { source: StreamSource; asOfSeq?: string };
};

export type ApprovalChallenge = {
  approvalId: string;
  processId: string;
  action: string;
  normalizedDiff: string;
  argsDigest: string;
  descriptorDigest: string;
  principal: string;
  expiresAt: string;
};

export type ApprovalDecision = {
  approvalId: string;
  resolution: "approved" | "rejected";
  reviewer: string;
  argsDigest: string;
  descriptorDigest: string;
  expiresAt: string;
  keyId: string;
  signature: string;
};

export interface SignerPort {
  readonly keyId: string;
  readonly principal?: string;
  signChallenge(
    challenge: ApprovalChallenge,
    resolution?: "approved" | "rejected",
    reviewer?: string
  ): Promise<ApprovalDecision> | ApprovalDecision;
}

export interface RuntimeClient {
  startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
  getRun(runId: string, signal?: AbortSignal): Promise<Result<RunSnapshot>>;
  listRuns?(options?: { limit?: number; offset?: number; status?: string }, signal?: AbortSignal): Promise<Result<RunSummary[]>>;
  requestCancel(runId: string, signalOrReason?: AbortSignal | { reason?: string }): Promise<Result<CommandReceipt>>;
  requestCheckpoint(runId: string, signalOrReason?: AbortSignal | { reason?: string }): Promise<Result<CommandReceipt>>;
  requestResume(request: ResumeRunRequest | string, signalOrOpts?: AbortSignal | { checkpointId?: string }): Promise<Result<RunRef | CommandReceipt>>;
  explainArtifact(artifactId: string, signalOrOptions?: AbortSignal | { substrateProfile?: string }): Promise<Result<ArtifactExplanation>>;
  resolveApproval(request: ResolveApprovalRequest, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  recordCorrection(record: CorrectionRecord, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  getCapabilities?(signal?: AbortSignal): Promise<Result<Record<string, unknown>>>;
  getDaemonStatus(signal?: AbortSignal): Promise<Result<DaemonStatus>>;
}

