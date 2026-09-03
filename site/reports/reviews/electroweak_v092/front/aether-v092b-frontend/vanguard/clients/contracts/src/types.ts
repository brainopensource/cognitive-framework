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

// ==========================================
// 1. PROVIDER & CREDENTIAL CONFIGURATION
// ==========================================

export type ProviderType = "openrouter" | "ollama" | "anthropic" | "openai" | "custom";

export type CredentialState = "NOT_CONFIGURED" | "CONFIGURED" | "INVALID" | "UNAVAILABLE";

export type ModelDescriptor = {
  id: string;
  name: string;
  contextWindow?: number;
  supportsVision?: boolean;
  defaultForRole?: string;
};

export type ModelProviderConfig = {
  id: string;
  name: string;
  type: ProviderType;
  baseUrl?: string;
  credentialKeyRef: string;
  credentialState: CredentialState;
  models: ModelDescriptor[];
  selectedModel: string;
  enabled: boolean;
  isDefault: boolean;
  lastValidatedAt?: string;
  lastError?: string;
};

export type ExecutionProfile = {
  id: string;
  name: string;
  providerId: string;
  modelId: string;
  temperature?: number;
  maxBudgetUsd?: number;
};

export type SecureCredentialRef = {
  keyRef: string;
  providerType: ProviderType;
  state: CredentialState;
  label: string;
  lastUpdated?: string;
};

// ==========================================
// 2. STARTUP READINESS
// ==========================================

export type ReadinessStepId = "runtime" | "provider" | "credential" | "workspace" | "composition";

export type ReadinessStepStatus = "ready" | "pending" | "invalid" | "unreachable";

export type ReadinessStep = {
  id: ReadinessStepId;
  title: string;
  status: ReadinessStepStatus;
  description: string;
  actionLabel?: string;
  routeTarget?: string;
};

export type StartupReadiness = {
  isReady: boolean;
  steps: ReadinessStep[];
  nextRequiredStep?: ReadinessStepId;
};

// ==========================================
// 3. MUTATION LIFECYCLE & MULTI-FILE DIFFS
// ==========================================

export type MutationLifecycleState = "PROPOSED" | "APPROVED" | "APPLIED" | "VERIFIED" | "FAILED";

export type FileDiffEntry = {
  filePath: string;
  oldPath?: string;
  status: MutationLifecycleState;
  additions: number;
  deletions: number;
  patchText: string;
  isBinary?: boolean;
};

export type MultiFileDiffModel = {
  diffId: string;
  approvalId?: string;
  files: FileDiffEntry[];
  overallStatus: MutationLifecycleState;
  summary: {
    totalFiles: number;
    totalAdditions: number;
    totalDeletions: number;
  };
};

// ==========================================
// 4. VERIFICATION UX MODELS
// ==========================================

export type VerificationKind = "tests" | "lint" | "typecheck" | "build" | "custom";

export type VerificationStatus = "pass" | "fail" | "partial" | "unavailable";

export type VerificationSummary = {
  id: string;
  kind: VerificationKind;
  status: VerificationStatus;
  command?: string;
  durationMs?: number;
  passedCount?: number;
  failedCount?: number;
  skippedCount?: number;
  importantOutput?: string;
  relatedArtifacts?: string[];
  timestamp: string;
};

// ==========================================
// 5. RESEARCH SOURCE & CITATION UX
// ==========================================

export type CitationItem = {
  id: string;
  sourceTitle: string;
  sourceOrigin: string;
  citationText: string;
  claimAssociation?: string;
  evidenceAssociation?: string;
  confidence?: number;
  uncertaintyNotes?: string;
  artifactRef?: string;
};

export type ResearchProgressSummary = {
  totalSources: number;
  verifiedClaims: number;
  activeRetrievals: number;
  citations: CitationItem[];
  synthesisText?: string;
};

// ==========================================
// 6. MULTI-AGENT & WORKFLOW PRESENTATION
// ==========================================

export type AgentParticipantState = {
  agentId: string;
  role: string;
  status: "active" | "waiting" | "completed" | "failed";
  currentActivity?: string;
  parentAgentId?: string;
  handoffTimestamp?: string;
};

export type WorkflowExecutionView = {
  workflowId: string;
  title: string;
  currentStage: string;
  participants: AgentParticipantState[];
  intermediateArtifacts: string[];
  isTerminal: boolean;
};

// ==========================================
// 7. CONVERSATION PERSISTENCE METADATA
// ==========================================

export type FrontendConversationMeta = {
  id: string;
  title: string;
  agentId: string;
  workflowId?: string;
  workspacePath: string;
  runIds: string[];
  activeRunId: string;
  createdAt: string;
  updatedAt: string;
  lastOpenedAt?: string;
  draft: string;
  turnCount: number;
};

