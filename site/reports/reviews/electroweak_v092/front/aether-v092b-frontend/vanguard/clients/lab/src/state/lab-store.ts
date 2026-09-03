import {
  emptyRunSnapshot,
  reduceRunSnapshot,
  foldEvents,
  toTraceGraph,
  emptyEvidenceGrid,
  reduceEvidence,
  emptyApprovalState,
  reduceApprovalState,
  type RunSnapshotModel,
  type TraceGraph,
  type EvidenceGrid,
  type ApprovalState,
  type ProjectedArtifact,
} from "@aether/projections";
import type {
  EventEnvelope,
  RunSummary,
  DaemonStatus,
  ArtifactExplanation,
} from "@aether/contracts";
import type { RuntimeClient } from "@aether/client";
import { createSignal, type Signal, batch } from "./signals.js";
import { SelectionModel } from "./selection-model.js";
import { ReplayEngine } from "./replay-engine.js";

export type EventCategoryFilter =
  | "all"
  | "errors"
  | "approvals"
  | "effects"
  | "models"
  | "tools"
  | "artifacts"
  | "budgets"
  | "verification"
  | "context"
  | "lifecycle";

export type EventFilters = {
  category: EventCategoryFilter;
  query: string;
  principal: string;
  status: "all" | "success" | "error";
  minSeq?: string;
  maxSeq?: string;
};

export type RunFilters = {
  status: string;
  query: string;
  sortField: "date" | "seq" | "tokens" | "status";
  sortAsc: boolean;
};

export type ConnectionState = "connected" | "connecting" | "reconnecting" | "unavailable" | "offline";
export type LiveTailState = "LIVE" | "PAUSED" | "RECONNECTING" | "OFFLINE" | "COMPLETE";
export type FeatureAvailability = "AVAILABLE" | "UNAVAILABLE" | "DEGRADED" | "INCOMPATIBLE";

export type LabStoreState = {
  // Connection & Health
  connectionState: ConnectionState;
  transportType: "socket" | "http" | "replay";
  socketPathOrUrl: string;
  daemonStatus: DaemonStatus | null;
  capabilities: Record<string, unknown>;
  featureStatus: Record<string, FeatureAvailability>;
  statusMessage: string;

  // Mode
  mode: "live" | "replay";
  liveTailState: LiveTailState;
  unseenLiveCount: number;
  isUserScrolledUp: boolean;

  // Runs
  runs: RunSummary[];
  activeRunId: string;
  isLoadingRuns: boolean;

  // Current Run Canonical Data
  events: EventEnvelope[];
  snapshot: RunSnapshotModel;
  traceGraph: TraceGraph;
  evidenceGrid: EvidenceGrid;
  approvalState: ApprovalState;
  artifactExplanations: Map<string, ArtifactExplanation>;

  // Filters
  eventFilters: EventFilters;
  runFilters: RunFilters;
};

export class LabStore {
  public readonly state: Signal<LabStoreState>;
  public readonly selection: SelectionModel;
  public readonly replay: ReplayEngine;
  private abortController: AbortController | null = null;

  constructor(initial: Partial<LabStoreState> = {}, initialSelection?: SelectionModel) {
    this.selection = initialSelection ?? new SelectionModel();
    this.replay = new ReplayEngine([], (visible) => this.setReplayVisibleEvents(visible));

    this.state = createSignal<LabStoreState>({
      connectionState: initial.connectionState ?? "connected",
      transportType: initial.transportType ?? "socket",
      socketPathOrUrl: initial.socketPathOrUrl ?? "/tmp/vanguard-runtime.sock",
      daemonStatus: initial.daemonStatus ?? null,
      capabilities: initial.capabilities ?? {},
      featureStatus: initial.featureStatus ?? {
        LiveTail: "AVAILABLE",
        Replay: "AVAILABLE",
        Forensics: "AVAILABLE",
        ArtifactExplanation: "AVAILABLE",
        DirectMutation: "UNAVAILABLE", // Lab is read-only inspection surface
      },
      statusMessage: "Ready",

      mode: initial.mode ?? "live",
      liveTailState: initial.liveTailState ?? "LIVE",
      unseenLiveCount: 0,
      isUserScrolledUp: false,

      runs: initial.runs ?? [],
      activeRunId: initial.activeRunId ?? "",
      isLoadingRuns: false,

      events: initial.events ?? [],
      snapshot: initial.snapshot ?? (initial.events ? foldEvents(initial.events) : emptyRunSnapshot()),
      traceGraph: initial.traceGraph ?? (initial.events ? toTraceGraph(initial.events) : { nodes: [], edges: [] }),
      evidenceGrid: initial.evidenceGrid ?? (initial.events ? initial.events.reduce(reduceEvidence, emptyEvidenceGrid()) : emptyEvidenceGrid()),
      approvalState: initial.approvalState ?? (initial.events ? initial.events.reduce(reduceApprovalState, emptyApprovalState()) : emptyApprovalState()),
      artifactExplanations: initial.artifactExplanations ?? new Map(),

      eventFilters: initial.eventFilters ?? {
        category: "all",
        query: "",
        principal: "all",
        status: "all",
      },
      runFilters: initial.runFilters ?? {
        status: "all",
        query: "",
        sortField: "date",
        sortAsc: false,
      },
    });
  }

  public get(): LabStoreState {
    return this.state.get();
  }

  public update(fn: (prev: LabStoreState) => LabStoreState): void {
    this.state.set(fn);
  }

  public setMode(mode: "live" | "replay"): void {
    this.update((prev) => ({
      ...prev,
      mode,
      liveTailState: mode === "live" ? "LIVE" : "PAUSED",
    }));
    if (mode === "replay") {
      this.replay.setEvents(this.get().events);
    }
  }

  public setLiveTailState(state: LiveTailState): void {
    this.update((prev) => ({ ...prev, liveTailState: state }));
  }

  public setIsUserScrolledUp(scrolledUp: boolean): void {
    this.update((prev) => ({
      ...prev,
      isUserScrolledUp: scrolledUp,
      unseenLiveCount: scrolledUp ? prev.unseenLiveCount : 0,
    }));
  }

  public jumpToLive(): void {
    this.update((prev) => ({
      ...prev,
      isUserScrolledUp: false,
      unseenLiveCount: 0,
      liveTailState: "LIVE",
    }));
  }

  public setEventFilters(fn: (prev: EventFilters) => EventFilters): void {
    this.update((prev) => ({
      ...prev,
      eventFilters: fn(prev.eventFilters),
    }));
  }

  public setRunFilters(fn: (prev: RunFilters) => RunFilters): void {
    this.update((prev) => ({
      ...prev,
      runFilters: fn(prev.runFilters),
    }));
  }

  public ingestEnvelope(envelope: EventEnvelope): void {
    const cur = this.get();
    if (cur.mode === "replay") {
      // If in replay mode, simply append to full event list
      const nextEvents = [...cur.events, envelope];
      this.replay.setEvents(nextEvents);
      this.update((prev) => ({ ...prev, events: nextEvents }));
      return;
    }

    batch(() => {
      const nextEvents = [...cur.events, envelope];
      const nextSnapshot = reduceRunSnapshot(cur.snapshot, envelope);
      const nextTraceGraph = toTraceGraph(nextEvents);
      const nextEvidence = reduceEvidence(cur.evidenceGrid, envelope);
      const nextApprovalState = reduceApprovalState(cur.approvalState, envelope);

      let nextUnseen = cur.unseenLiveCount;
      if (cur.isUserScrolledUp || cur.liveTailState === "PAUSED") {
        nextUnseen += 1;
      }

      let nextLiveState = cur.liveTailState;
      if (
        envelope.payload.kind === "EpisodeCompleted" ||
        envelope.payload.kind === "RunCompleted" ||
        envelope.payload.kind === "VerdictProduced" ||
        envelope.payload.kind === "RunCancelled"
      ) {
        nextLiveState = "COMPLETE";
      }

      this.update((prev) => ({
        ...prev,
        events: nextEvents,
        snapshot: nextSnapshot,
        traceGraph: nextTraceGraph,
        evidenceGrid: nextEvidence,
        approvalState: nextApprovalState,
        unseenLiveCount: nextUnseen,
        liveTailState: nextLiveState,
        activeRunId: envelope.runId ?? prev.activeRunId,
      }));
    });
  }

  public setReplayVisibleEvents(visibleEvents: EventEnvelope[]): void {
    const runId = this.get().activeRunId;
    const snapshot = foldEvents(visibleEvents, runId);
    const traceGraph = toTraceGraph(visibleEvents);
    const evidenceGrid = visibleEvents.reduce(reduceEvidence, emptyEvidenceGrid(runId));
    const approvalState = visibleEvents.reduce(reduceApprovalState, emptyApprovalState());

    this.update((prev) => ({
      ...prev,
      snapshot,
      traceGraph,
      evidenceGrid,
      approvalState,
    }));
  }

  public loadReplayEvents(events: EventEnvelope[]): void {
    const runId = events.length > 0 ? events[0]?.runId ?? "" : "";
    this.update((prev) => ({
      ...prev,
      mode: "replay",
      liveTailState: "PAUSED",
      events,
      activeRunId: runId || prev.activeRunId,
    }));
    this.selection.selectRun(runId || this.get().activeRunId);
    this.replay.setEvents(events);
    this.setReplayVisibleEvents(events);
  }

  public async loadRuns(client: RuntimeClient): Promise<void> {
    this.update((prev) => ({ ...prev, isLoadingRuns: true }));
    try {
      const res = await client.listRuns();
      if (res.ok) {
        this.update((prev) => ({
          ...prev,
          runs: res.value,
          isLoadingRuns: false,
        }));
      } else {
        this.update((prev) => ({
          ...prev,
          isLoadingRuns: false,
          statusMessage: `Failed to list runs: ${res.error.message}`,
        }));
      }
    } catch (err: any) {
      this.update((prev) => ({
        ...prev,
        isLoadingRuns: false,
        statusMessage: `Error loading runs: ${err.message}`,
      }));
    }
  }

  public async selectRun(runId: string, client?: RuntimeClient): Promise<void> {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }

    this.selection.selectRun(runId);
    this.update((prev) => ({
      ...prev,
      activeRunId: runId,
      events: [],
      snapshot: emptyRunSnapshot(runId),
      traceGraph: { nodes: [], edges: [] },
      evidenceGrid: emptyEvidenceGrid(runId),
      approvalState: emptyApprovalState(),
      unseenLiveCount: 0,
      liveTailState: "LIVE",
      mode: "live",
      statusMessage: `Selected run ${runId}`,
    }));

    if (client && runId) {
      this.attachLiveStream(client, runId);
    }
  }

  public async attachLiveStream(client: RuntimeClient, runId: string): Promise<void> {
    if (this.abortController) {
      this.abortController.abort();
    }
    this.abortController = new AbortController();
    const signal = this.abortController.signal;

    this.update((prev) => ({
      ...prev,
      activeRunId: runId,
      connectionState: "connected",
      liveTailState: "LIVE",
      statusMessage: `Streaming events for run ${runId}...`,
    }));

    try {
      for await (const item of client.streamEvents({ runId }, signal)) {
        if (signal.aborted) break;
        if (!item.ok) {
          this.update((prev) => ({
            ...prev,
            connectionState: "reconnecting",
            liveTailState: "RECONNECTING",
            statusMessage: `Stream issue: ${item.error.message}`,
          }));
          continue;
        }
        this.ingestEnvelope(item.value.envelope);
      }
    } catch (err: any) {
      if (!signal.aborted) {
        this.update((prev) => ({
          ...prev,
          connectionState: "unavailable",
          liveTailState: "OFFLINE",
          statusMessage: `Stream disconnected: ${err.message}`,
        }));
      }
    }
  }

  public async resolveApproval(
    client: RuntimeClient,
    approvalId: string,
    decision: "approved" | "rejected" | "approve" | "reject"
  ): Promise<boolean> {
    this.update((prev) => ({
      ...prev,
      statusMessage: `Submitting approval ${approvalId} [${decision}]...`,
    }));

    const clientDecision = decision === "approved" ? "approve" : decision === "rejected" ? "reject" : decision;

    const res = await client.resolveApproval({
      approvalId,
      decision: clientDecision,
    });

    if (res.ok) {
      this.update((prev) => ({
        ...prev,
        statusMessage: `Approval ${approvalId} resolved: ${decision}`,
      }));
      return true;
    } else {
      this.update((prev) => ({
        ...prev,
        statusMessage: `Failed to resolve approval: ${res.error.message}`,
      }));
      return false;
    }
  }

  public async explainArtifact(client: RuntimeClient, artifactId: string): Promise<ArtifactExplanation | null> {
    const cached = this.get().artifactExplanations.get(artifactId);
    if (cached) return cached;

    const res = await client.explainArtifact(artifactId);
    if (res.ok) {
      const expl = res.value;
      this.update((prev) => {
        const nextMap = new Map(prev.artifactExplanations);
        nextMap.set(artifactId, expl);
        return { ...prev, artifactExplanations: nextMap };
      });
      return expl;
    }
    return null;
  }

  public async checkSystemCapabilities(client: RuntimeClient): Promise<void> {
    try {
      const daemonRes = await client.getDaemonStatus();
      let daemonStatus: DaemonStatus | null = null;
      let connectionState: ConnectionState = "connected";

      if (daemonRes.ok) {
        daemonStatus = daemonRes.value;
      } else {
        connectionState = "unavailable";
      }

      const capsRes = await client.getCapabilities();
      const capabilities = capsRes.ok ? capsRes.value : {};

      const featureStatus: Record<string, FeatureAvailability> = {
        LiveTail: daemonStatus?.status === "running" ? "AVAILABLE" : "DEGRADED",
        Replay: "AVAILABLE",
        Forensics: "AVAILABLE",
        ArtifactExplanation: capabilities["explainArtifact"] ? "AVAILABLE" : "DEGRADED",
        DirectMutation: "UNAVAILABLE",
      };

      this.update((prev) => ({
        ...prev,
        connectionState,
        daemonStatus,
        capabilities,
        featureStatus,
      }));
    } catch {
      this.update((prev) => ({
        ...prev,
        connectionState: "unavailable",
        featureStatus: {
          LiveTail: "UNAVAILABLE",
          Replay: "AVAILABLE",
          Forensics: "AVAILABLE",
          ArtifactExplanation: "UNAVAILABLE",
          DirectMutation: "UNAVAILABLE",
        },
      }));
    }
  }

  public getFilteredEvents(): EventEnvelope[] {
    const cur = this.get();
    const events = cur.mode === "replay" ? cur.events.slice(0, this.replay.get().currentIndex + 1) : cur.events;
    const { category, query, principal, status, minSeq, maxSeq } = cur.eventFilters;

    const q = query.trim().toLowerCase();

    return events.filter((env) => {
      const kind = String(env.payload.kind ?? "");

      // 1. Category Filter
      if (category === "errors") {
        const isErr =
          kind === "EffectFailed" ||
          kind === "ServiceError" ||
          typeof env.payload.error === "string" ||
          env.payload.outcome === "failed" ||
          env.payload.verdict === "failed";
        if (!isErr) return false;
      } else if (category === "approvals") {
        if (kind !== "ApprovalRequested" && kind !== "ApprovalResolved") return false;
      } else if (category === "effects") {
        if (
          kind !== "EffectStarted" &&
          kind !== "EffectCompleted" &&
          kind !== "EffectFailed" &&
          kind !== "OperatorInvoked"
        )
          return false;
      } else if (category === "models") {
        if (
          kind !== "ModelProposalProduced" &&
          kind !== "ModelStreamDelta" &&
          kind !== "TurnStarted"
        )
          return false;
      } else if (category === "tools") {
        if (kind !== "OperatorInvoked" && kind !== "EffectStarted" && !env.payload.tool) return false;
      } else if (category === "artifacts") {
        if (kind !== "ArtifactCreated" && kind !== "ArtifactUpdated" && kind !== "ArtifactPublished") return false;
      } else if (category === "budgets") {
        if (kind !== "BudgetCommitted" && kind !== "BudgetExceeded") return false;
      } else if (category === "verification") {
        if (
          kind !== "EvidenceClaimProduced" &&
          kind !== "EvidenceRecorded" &&
          kind !== "EvaluationCompleted" &&
          kind !== "VerdictProduced"
        )
          return false;
      } else if (category === "context") {
        if (
          kind !== "ContextCompiled" &&
          kind !== "ContextCompacted" &&
          kind !== "ObservationProduced" &&
          kind !== "MemoryRecalled"
        )
          return false;
      } else if (category === "lifecycle") {
        if (
          kind !== "GoalDeclared" &&
          kind !== "EpisodeStarted" &&
          kind !== "EpisodeCompleted" &&
          kind !== "RunCompleted" &&
          kind !== "RunCancelled"
        )
          return false;
      }

      // 2. Status Filter
      if (status === "error") {
        const isErr =
          kind === "EffectFailed" ||
          kind === "ServiceError" ||
          typeof env.payload.error === "string" ||
          env.payload.outcome === "failed";
        if (!isErr) return false;
      } else if (status === "success") {
        if (kind === "EffectFailed" || kind === "ServiceError" || typeof env.payload.error === "string") return false;
      }

      // 3. Principal Filter
      if (principal !== "all" && env.principal !== principal) {
        return false;
      }

      // 4. Seq range
      if (minSeq) {
        try {
          if (BigInt(env.seq) < BigInt(minSeq)) return false;
        } catch {}
      }
      if (maxSeq) {
        try {
          if (BigInt(env.seq) > BigInt(maxSeq)) return false;
        } catch {}
      }

      // 5. Query Search
      if (q) {
        const inKind = kind.toLowerCase().includes(q);
        const inSeq = env.seq.includes(q);
        const inEventId = env.eventId.toLowerCase().includes(q);
        const inPrincipal = env.principal.toLowerCase().includes(q);
        const inPayloadText =
          typeof env.payload.text === "string" && env.payload.text.toLowerCase().includes(q);
        const inGoal =
          typeof env.payload.goal === "string" && env.payload.goal.toLowerCase().includes(q);
        const inTool =
          typeof env.payload.tool === "string" && env.payload.tool.toLowerCase().includes(q);

        if (!inKind && !inSeq && !inEventId && !inPrincipal && !inPayloadText && !inGoal && !inTool) {
          return false;
        }
      }

      return true;
    });
  }

  public getFilteredRuns(): RunSummary[] {
    const cur = this.get();
    const { status, query, sortField, sortAsc } = cur.runFilters;
    const q = query.trim().toLowerCase();

    let filtered = cur.runs.filter((r) => {
      if (status !== "all" && r.status !== status) return false;
      if (q) {
        const inId = r.runId.toLowerCase().includes(q);
        const inStatus = r.status.toLowerCase().includes(q);
        if (!inId && !inStatus) return false;
      }
      return true;
    });

    filtered.sort((a, b) => {
      let cmp = 0;
      if (sortField === "date") {
        const tA = a.occurredAt ? new Date(a.occurredAt).getTime() : 0;
        const tB = b.occurredAt ? new Date(b.occurredAt).getTime() : 0;
        cmp = tA - tB;
      } else if (sortField === "seq") {
        try {
          const sA = BigInt(a.seq || "0");
          const sB = BigInt(b.seq || "0");
          cmp = sA < sB ? -1 : sA > sB ? 1 : 0;
        } catch {
          cmp = 0;
        }
      } else if (sortField === "status") {
        cmp = a.status.localeCompare(b.status);
      }
      return sortAsc ? cmp : -cmp;
    });

    return filtered;
  }
}
