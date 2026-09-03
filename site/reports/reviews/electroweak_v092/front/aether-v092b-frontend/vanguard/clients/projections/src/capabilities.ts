export type FrontendCapabilityFlags = {
  canStartRun: boolean;
  canCancelRun: boolean;
  canCheckpoint: boolean;
  canResume: boolean;
  canStreamEvents: boolean;
  canResolveApproval: boolean;
  canSignEd25519: boolean;
  canRecordCorrection: boolean;
  canExplainArtifact: boolean;
  canRetrieveRawArtifact: boolean;
  canListRuns: boolean;
  mode: "standard" | "replay" | "degraded" | "restricted";
  supportedTools: string[];
};

export const DEFAULT_CAPABILITY_FLAGS: FrontendCapabilityFlags = {
  canStartRun: true,
  canCancelRun: true,
  canCheckpoint: true,
  canResume: true,
  canStreamEvents: true,
  canResolveApproval: true,
  canSignEd25519: true,
  canRecordCorrection: true,
  canExplainArtifact: true,
  canRetrieveRawArtifact: false, // BlobStore direct retrieval pending
  canListRuns: true,
  mode: "standard",
  supportedTools: [],
};

export function evaluateCapabilities(
  caps: Record<string, unknown> | null | undefined
): FrontendCapabilityFlags {
  if (!caps || typeof caps !== "object") {
    return { ...DEFAULT_CAPABILITY_FLAGS };
  }

  const rawCaps = Array.isArray(caps.capabilities) ? caps.capabilities : [];
  const capSet = new Set(rawCaps.map((c) => String(c)));
  const modeRaw = String(caps.mode ?? "standard");
  const mode = (
    modeRaw === "replay" || modeRaw === "degraded" || modeRaw === "restricted"
      ? modeRaw
      : "standard"
  ) as FrontendCapabilityFlags["mode"];

  const supportedTools = Array.isArray(caps.supportedTools)
    ? caps.supportedTools.map((t) => String(t))
    : [];

  // When capability list is provided, gate according to declarations
  const hasCapList = rawCaps.length > 0;

  return {
    canStartRun: hasCapList ? capSet.has("StartRun") || capSet.has("start_run") : true,
    canCancelRun: hasCapList ? capSet.has("CancelRun") || capSet.has("cancel_run") : true,
    canCheckpoint: hasCapList ? capSet.has("CheckpointRun") || capSet.has("checkpoint_run") : true,
    canResume: hasCapList ? capSet.has("ResumeRun") || capSet.has("resume_run") : true,
    canStreamEvents: hasCapList ? capSet.has("StreamEvents") || capSet.has("stream_events") : true,
    canResolveApproval: hasCapList ? capSet.has("ResolveApproval") || capSet.has("resolve_approval") : true,
    canSignEd25519: hasCapList ? capSet.has("SignEd25519") || capSet.has("ed25519") || true : true,
    canRecordCorrection: hasCapList ? capSet.has("RecordCorrection") || capSet.has("record_correction") : true,
    canExplainArtifact: hasCapList ? capSet.has("ExplainArtifact") || capSet.has("explain_artifact") : true,
    canRetrieveRawArtifact: capSet.has("GetArtifactBlob") || capSet.has("raw_artifact_retrieval"),
    canListRuns: hasCapList ? capSet.has("ListRuns") || capSet.has("list_runs") : true,
    mode,
    supportedTools,
  };
}

export function isCapabilityAvailable(
  flags: FrontendCapabilityFlags,
  feature: keyof Omit<FrontendCapabilityFlags, "mode" | "supportedTools">
): boolean {
  return Boolean(flags[feature]);
}
