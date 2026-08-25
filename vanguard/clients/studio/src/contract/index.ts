export * from "@vanguard/client-core";

export type SourceClass =
  | "ledgered"
  | "canonical_query"
  | "client_derived"
  | "local_draft"
  | "unknown";

export type ProvenanceMeta = {
  readonly source: SourceClass;
  readonly eventKind?: string;
  readonly eventId?: string;
  readonly derivationName?: string;
  readonly canonicalQuery?: string;
};

export type RuntimeCapabilities = {
  readonly protocol: "vg.4";
  readonly commands: readonly string[];
  readonly eventKinds: readonly string[];
  readonly projections: readonly string[];
  readonly limits: {
    readonly maxFrameBytes: number;
    readonly maxStreams?: number;
  };
  readonly features: Readonly<Record<string, "disabled" | "read" | "command">>;
};

export const DEFAULT_DISCOVERED_CAPABILITIES: RuntimeCapabilities = {
  protocol: "vg.4",
  commands: [
    "StartRun",
    "GetRun",
    "StreamEvents",
    "ResolveApproval",
    "RecordCorrection",
    "Cancel",
    "Checkpoint",
    "Resume",
    "ExplainArtifact",
  ],
  eventKinds: [
    "EpisodeStarted",
    "EpisodeCompleted",
    "EffectStarted",
    "EffectCompleted",
    "EffectRejected",
    "AuthorizationDenied",
    "ApprovalRequested",
    "ApprovalResolved",
    "CorrectionRecorded",
    "ObservationProduced",
    "OperatorInvoked",
    "BudgetCommitted",
    "EffectReconciled",
    "Heartbeat",
  ],
  projections: ["RunView", "StatusBar", "TraceGraph"],
  limits: {
    maxFrameBytes: 1048576,
    maxStreams: 1,
  },
  features: {
    fixtureReplay: "command",
    liveSingleRun: "command",
    operatorApproval: "command",
    recordCorrection: "command",
    explainArtifact: "read",
    draftComposition: "read",
    controlledComparison: "read",
    m7Scheduler: "disabled",
    m8SwarmTopology: "disabled",
    m9SecondBrain: "disabled",
  },
};

export function isFeaturePermitted(
  capabilities: RuntimeCapabilities,
  featureKey: string,
  requiredMode: "read" | "command" = "read"
): boolean {
  const mode = capabilities.features[featureKey];
  if (!mode || mode === "disabled") return false;
  if (requiredMode === "read") return mode === "read" || mode === "command";
  return mode === "command";
}
