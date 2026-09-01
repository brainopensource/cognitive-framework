export * from "@vanguard/client-core/contract/types.js";
export * from "@vanguard/client-core/contract/parse.js";
export * from "@vanguard/client-core/adapters/web-signer.js";
export * from "@vanguard/client-core/adapters/fake.js";
export * from "@vanguard/client-core/adapters/http.js";
// F4 Phase 1: these 7 leaf modules are ported to @aether/client (no
// cross-module or RuntimeClient dependencies).
export * from "@aether/client/application/run-view.js";
export * from "@aether/client/application/budget.js";
export * from "@aether/client/application/coding-types.js";
export * from "@aether/client/application/trace-graph.js";
export * from "@aether/client/application/projection-model.js";
export * from "@aether/client/application/graph-model.js";
export * from "@aether/client/application/mcnemar.js";
// F4 Phase 2: 4 of the 5 intermediate RuntimeClient-dependent modules are
// ported. `corrections.ts` stays on @vanguard/client-core deliberately --
// its CorrectionRecord shape (episodeId/proposedPatchDigest/reasonCodes/
// magnitude/scope/correctingPrincipalRole) is a different, real, working
// wire shape than @aether/contracts's CorrectionRecord (correctionId/runId/
// targetEventId/reasonCode/scope local|general/recordedAt). The backend's
// RecordCorrection command doesn't validate the correction object's inner
// shape (service.py passes it through opaquely), so both are "valid" on the
// wire -- but porting this module means picking one shape as canonical, not
// a mechanical rename. That's a product/schema decision, not a Phase 2 port.
export * from "@aether/client/application/approvals.js";
export * from "@aether/client/application/subscribe-run.js";
export * from "@aether/client/application/selectors.js";
export * from "@aether/client/application/coding-receipts.js";
export * from "@vanguard/client-core/application/corrections.js";

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
