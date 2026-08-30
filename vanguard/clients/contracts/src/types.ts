export type ClientContractVersion = "0.1" | "vg.4";
export type StreamSource = "mock" | "replay" | "live";

/**
 * Canonical vg.4 wire error vocabulary (integration_plan.md §4.5), shared
 * byte-for-byte with `schemas/v4/runtime-service.schema.json#/$defs/ErrorCode`
 * and Python's `runtime/service/contract.py:ERROR_CODES`.
 * `transport_interrupted` is the client-only synthetic code for a dropped connection.
 */
export type CanonicalErrorCode =
  | "invalid_request"
  | "unauthenticated"
  | "permission_denied"
  | "not_found"
  | "conflict"
  | "incompatible_version"
  | "frame_too_large"
  | "rate_limited"
  | "not_available"
  | "internal";

export type ErrorCode = CanonicalErrorCode | "transport_interrupted";

export type ClientFailure = {
  code: ErrorCode;
  message: string;
  retryable: boolean;
  details?: Readonly<Record<string, unknown>>;
};

export type Result<T, E = ClientFailure> =
  | { ok: true; value: T }
  | { ok: false; error: E };

export type EventScope = "episode" | "governance" | "evolution" | "recovery";
export type PrincipalRole = "user" | "operator" | "episode" | "process" | "evaluator" | "release";

export type EventEnvelope = {
  schemaVersion: "vg.4";
  eventId: string;
  scope: EventScope;
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
  principalRole?: PrincipalRole;
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

export type EventCursor = {
  runId: string;
  afterSeq?: string | number;
};

export type StreamItem = {
  contractVersion: ClientContractVersion;
  source: StreamSource;
  envelope: EventEnvelope;
};

export type ServiceError = {
  code: CanonicalErrorCode;
  message: string;
  retryable: boolean;
  correlationId?: string;
  detail?: string;
};

export type CommandReceipt = {
  commandId: string;
  status: "completed" | "error";
  runId?: string;
  result?: Record<string, unknown>;
  detail?: string;
  error?: ServiceError;
};

export type CommandFrame = {
  version: "vg.4";
  frameType: "command";
  frameId: string;
  command: {
    name: string;
    commandId: string;
    idempotencyKey: string;
    runId?: string;
    actor?: string;
    payload?: Record<string, unknown>;
  };
};

export type ReceiptFrame = {
  version: "vg.4";
  frameType: "receipt";
  frameId: string;
  inReplyTo?: string;
  receipt: CommandReceipt;
};

export type EventFrame = {
  version: "vg.4";
  frameType: "event";
  frameId: string;
  event: EventEnvelope;
};

export type ErrorFrame = {
  version: "vg.4";
  frameType: "error";
  frameId: string;
  inReplyTo?: string;
  error: ServiceError;
};

export type RuntimeServiceFrame = CommandFrame | ReceiptFrame | EventFrame | ErrorFrame;

export type StartRunRequest = {
  manifestPath?: string;
  repoPath?: string;
  repo?: string;
  brief?: string;
  prompt?: string;
  profileId?: string;
  profile?: string;
  model?: string;
  episodeId?: string;
  runId?: string;
  expectedSeq?: string | number;
  resumeFrom?: string;
  checkpointEvery?: number;
  autoApprove?: boolean;
  nonInteractive?: boolean;
};

export type RunRef = {
  runId: string;
  episodeId?: string;
};

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

export type ListRunsOptions = {
  limit?: number;
  offset?: number;
  status?: string;
};

export type CancelOptions = {
  reason?: string;
  expectedSeq?: string | number;
};

export type CheckpointOptions = {
  reason?: string;
  expectedSeq?: string | number;
};

export type ResumeOptions = {
  checkpointId?: string;
  expectedSeq?: string | number;
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

export type ResolveApprovalRequest = {
  approvalId?: string;
  decision: ApprovalDecision | "approve" | "reject";
  expectedSeq?: string | number;
  signature?: string;
  signerKeyRef?: string;
};

export type CorrectionRecord = {
  correctionId: string;
  runId: string;
  episodeId?: string;
  targetEventId?: string;
  reasonCode: string;
  scope: "local" | "general";
  notes?: string;
  recordedAt: string;
  author: string;
};

export type RecordCorrectionRequest = {
  correction: CorrectionRecord;
  expectedSeq?: string | number;
};

export type ArtifactExplanation = {
  artifactId: string;
  status?: string;
  prediction?: string;
  activatedBy?: string[];
  demotedBy?: string[];
  provenance?: Record<string, unknown>;
  evidenceClaims?: Record<string, unknown>[];
  [key: string]: unknown;
};

export type ExplainArtifactOptions = {
  substrateProfile?: string;
  expectedSeq?: string | number;
};

export type DaemonStatus = {
  status: "running" | "stopped" | "unresponsive";
  socketPath: string;
  pid?: number;
  version?: string;
  uptimeSeconds?: number;
};

export interface SignerPort {
  readonly keyId: string;
  readonly principal: string;
  signChallenge(
    challenge: ApprovalChallenge,
    resolution?: "approved" | "rejected",
    reviewer?: string
  ): Promise<ApprovalDecision> | ApprovalDecision;
}

export type AgentDescriptor = {
  id: string;
  name: string;
  description: string;
  validationStatus: "valid" | "invalid" | "unverified";
  modelSummary: string;
  toolSummary: string[];
  capabilitySummary: string[];
  manifestPath: string;
};

export type WorkflowDescriptor = {
  id: string;
  name: string;
  description: string;
  manifestPath: string;
  validationStatus: "valid" | "invalid" | "unverified";
  participatingAgents?: string[];
  entrypointOrStages?: string[];
};

export type FrontendConnectionState =
  | "CONNECTING"
  | "CONNECTED"
  | "RECONNECTING"
  | "OFFLINE"
  | "DEGRADED"
  | "INCOMPATIBLE";

export type ActivityCategory =
  | "MESSAGE"
  | "FILE_READ"
  | "SEARCH"
  | "TOOL"
  | "COMMAND"
  | "PATCH"
  | "VERIFICATION"
  | "RESEARCH"
  | "CITATION"
  | "ARTIFACT"
  | "APPROVAL"
  | "WARNING"
  | "ERROR"
  | "COMPLETION";

export type ActivityClaim = {
  claimType: string;
  statement: string;
  pass: boolean;
};

export type SemanticActivityItem = {
  id: string;
  category: ActivityCategory;
  title: string;
  details?: string;
  diff?: string;
  command?: string;
  filePath?: string;
  searchQuery?: string;
  citationUrl?: string;
  artifactId?: string;
  approvalId?: string;
  claims?: ActivityClaim[];
  status: "pending" | "running" | "completed" | "failed";
  durationMs?: number;
  timestamp: string;
  seq?: string;
  eventId?: string;
  rawPayload?: Record<string, unknown>;
};

export type DeepLinkTarget =
  | { kind: "run"; runId: string; eventSeq?: string }
  | { kind: "event"; runId: string; seq: string }
  | { kind: "artifact"; digest: string }
  | { kind: "approval"; approvalId: string }
  | { kind: "trace"; runId: string; nodeId: string }
  | { kind: "context"; layer?: string };

export type GeneralSettings = {
  defaultRuntime: string;
  defaultWorkspace: string;
  defaultAgent: string;
  defaultWorkflow: string;
  autoFollowStreaming: boolean;
};

export type RuntimeSettings = {
  socketPath: string;
  httpUrl: string;
  reconnectIntervalMs: number;
  maxReconnectAttempts: number;
  requestTimeoutMs: number;
};

export type AppearanceSettings = {
  theme: "dark" | "light" | "high-contrast";
  density: "compact" | "comfortable";
  reducedMotion: boolean;
};

export type WorkspaceSettings = {
  recentWorkspaces: string[];
  maxRecentWorkspaces: number;
};

export type TerminalSettings = {
  tuiAnimation: boolean;
  tuiColorMode: "truecolor" | "256color" | "16color" | "plain";
};

export type AccessibilitySettings = {
  highContrast: boolean;
  screenReaderOptimized: boolean;
  fontSize: number;
};

export type FrontendSettings = {
  general: GeneralSettings;
  runtime: RuntimeSettings;
  appearance: AppearanceSettings;
  workspace: WorkspaceSettings;
  terminal: TerminalSettings;
  accessibility: AccessibilitySettings;
};

