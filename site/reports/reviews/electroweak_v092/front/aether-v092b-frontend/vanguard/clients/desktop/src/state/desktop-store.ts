import {
  FrontendAppController,
  type AppControllerState,
  type ConversationRecord,
  ManagedRuntimeHost,
} from "@aether/client";
import {
  emptyRunSnapshot,
  type RunSnapshotModel,
  type ConversationTurn,
  type ApprovalState,
  type EvidenceGrid,
  type TraceGraph,
  type PendingApproval,
  type FailureDiagnostics,
  type FrontendCapabilityFlags,
  formatDeepLink,
  resolveDeepLink,
} from "@aether/projections";
import type {
  EventEnvelope,
  RunSummary,
  SemanticActivityItem,
  FrontendSettings,
  DeepLinkTarget,
  ModelProviderConfig,
  StartupReadiness,
  MultiFileDiffModel,
  VerificationSummary,
  ResearchProgressSummary,
  WorkflowExecutionView,
} from "@aether/contracts";
import type { RuntimeClient } from "@aether/client";
import { TauriNativeBridge, type NativePlatformBridge } from "../bridge/tauri-bridge.js";
import { groupSessionsByDate, filterSessions, type SessionSummary, type SessionGroup } from "./session-history.js";

export type Signal<T> = {
  get(): T;
  set(value: T | ((prev: T) => T)): void;
  subscribe(fn: (value: T) => void): () => void;
};

export function createSignal<T>(initialValue: T): Signal<T> {
  let current = initialValue;
  const listeners = new Set<(val: T) => void>();

  return {
    get() {
      return current;
    },
    set(val) {
      const next = typeof val === "function" ? (val as (prev: T) => T)(current) : val;
      if (next !== current) {
        current = next;
        for (const listener of listeners) {
          listener(current);
        }
      }
    },
    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
  };
}

export type ForensicTab = "diffs" | "evidence" | "artifacts" | "trace" | "runs" | "settings" | "providers";
export type LayoutMode = "COMPACT" | "STANDARD" | "WIDE";

export type DesktopStoreState = {
  // Session & Workspace (synchronized with Controller)
  sessions: SessionSummary[];
  activeSessionId: string;
  searchQuery: string;
  agentId: string;
  workflowId: string;
  model: string;
  workspacePath: string;
  recentWorkspaces: string[];
  runId: string;
  runs: RunSummary[];

  // Catalog & Providers
  providers: ModelProviderConfig[];
  selectedProviderId: string;
  readiness: StartupReadiness;

  // Connection & Stream
  connectionState: "connected" | "connecting" | "reconnecting" | "unavailable" | "offline" | "degraded" | "incompatible";
  isStreaming: boolean;
  statusMessage: string;
  capabilities: FrontendCapabilityFlags;
  lastFailure: FailureDiagnostics | null;

  // Projections
  snapshot: RunSnapshotModel;
  events: EventEnvelope[];
  turns: ConversationTurn[];
  activities: SemanticActivityItem[];
  approvalState: ApprovalState;
  evidenceGrid: EvidenceGrid;
  traceGraph: TraceGraph;
  pendingApproval?: PendingApproval;

  // Product Stage Models
  multiFileDiff: MultiFileDiffModel;
  verificationSummaries: VerificationSummary[];
  researchSummary: ResearchProgressSummary;
  workflowExecution: WorkflowExecutionView;

  // UI / Renderer State
  forensicDrawerOpen: boolean;
  activeForensicTab: ForensicTab;
  activeDiffText: string;
  activeArtifactDigest?: string;
  composerText: string;
  commandPaletteOpen: boolean;
  commandPaletteQuery: string;
  layoutMode: LayoutMode;
  sidebarOpen: boolean;
  scrollFollowStream: boolean;
  hasUnreadContent: boolean;
  activeSettingsTab: "general" | "runtime" | "providers" | "appearance" | "workspace" | "terminal" | "accessibility";
  selectedRunDetailId?: string;
  settings: FrontendSettings;
};

export type DesktopStoreOptions =
  | {
      controller?: FrontendAppController;
      client?: RuntimeClient;
      bridge?: NativePlatformBridge;
      initial?: Partial<DesktopStoreState>;
    }
  | Partial<DesktopStoreState>;

export class DesktopStore {
  public readonly controller: FrontendAppController;
  public readonly bridge: NativePlatformBridge;
  public readonly managedRuntime: ManagedRuntimeHost;
  public readonly state: Signal<DesktopStoreState>;
  private unsubscribeController?: () => void;
  private lastNotifiedApprovalId?: string;

  constructor(options: DesktopStoreOptions = {}) {
    const isDirectState = options && !("controller" in options) && !("client" in options) && !("initial" in options);
    const initialConfig = isDirectState ? (options as Partial<DesktopStoreState>) : (options as any).initial ?? {};
    const controllerParam = isDirectState ? undefined : (options as any).controller;
    const clientParam = isDirectState ? undefined : (options as any).client;
    this.bridge = (options as any)?.bridge ?? new TauriNativeBridge();
    this.managedRuntime = new ManagedRuntimeHost({
      onEvent: (event) => {
        if (event.type === "status_changed") {
          this.update((s) => ({
            ...s,
            connectionState:
              event.status === "RUNNING"
                ? "connected"
                : event.status === "INCOMPATIBLE"
                ? "incompatible"
                : "connecting",
            statusMessage: event.detail ?? s.statusMessage,
          }));
        }
      },
    });

    this.controller =
      controllerParam ??
      new FrontendAppController({
        client: clientParam,
        initialWorkspace: initialConfig.workspacePath,
        initialAgentId: initialConfig.agentId,
      });

    const ctrlState = this.controller.getState();
    const initialSessionId = initialConfig.activeSessionId ?? ctrlState.activeConversationId;

    const initialSessions: SessionSummary[] = initialConfig.sessions ?? [
      {
        sessionId: initialSessionId,
        title: "Initial Workspace Conversation",
        agentId: ctrlState.selectedAgentId,
        workspacePath: ctrlState.currentWorkspace,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        turnCount: 0,
      },
    ];

    this.state = createSignal<DesktopStoreState>({
      sessions: initialSessions,
      activeSessionId: initialSessionId,
      searchQuery: "",
      agentId: initialConfig.agentId ?? ctrlState.selectedAgentId,
      workflowId: initialConfig.workflowId ?? ctrlState.selectedWorkflowId,
      model: initialConfig.model ?? "openrouter/free",
      workspacePath: initialConfig.workspacePath ?? ctrlState.currentWorkspace,
      recentWorkspaces: ctrlState.recentWorkspaces,
      runId: initialConfig.runId ?? ctrlState.activeRunId,
      runs: ctrlState.runs,
      providers: ctrlState.providers,
      selectedProviderId: ctrlState.selectedProviderId,
      readiness: ctrlState.readiness,
      connectionState: initialConfig.connectionState ?? (ctrlState.connectionState.toLowerCase() as any),
      isStreaming: ctrlState.isStreaming,
      statusMessage: ctrlState.statusMessage,
      capabilities: ctrlState.capabilities,
      lastFailure: ctrlState.lastFailure,
      snapshot: initialConfig.snapshot ?? ctrlState.snapshot,
      events: initialConfig.events ?? ctrlState.events,
      turns: initialConfig.turns ?? ctrlState.turns,
      activities: ctrlState.activities,
      approvalState: initialConfig.approvalState ?? ctrlState.approvalState,
      evidenceGrid: initialConfig.evidenceGrid ?? ctrlState.evidenceGrid,
      traceGraph: ctrlState.traceGraph,
      pendingApproval: initialConfig.pendingApproval ?? ctrlState.pendingApproval,
      multiFileDiff: ctrlState.multiFileDiff,
      verificationSummaries: ctrlState.verificationSummaries,
      researchSummary: ctrlState.researchSummary,
      workflowExecution: ctrlState.workflowExecution,
      forensicDrawerOpen: false,
      activeForensicTab: "diffs",
      activeDiffText: "",
      composerText: "",
      commandPaletteOpen: false,
      commandPaletteQuery: "",
      layoutMode: "STANDARD",
      sidebarOpen: true,
      scrollFollowStream: true,
      hasUnreadContent: false,
      activeSettingsTab: "general",
      settings: ctrlState.settings,
    });

    this.unsubscribeController = this.controller.subscribe((cState) => {
      this.syncFromController(cState);
    });

    // Auto-restore persistence
    this.controller.restoreFromPersistence();
  }

  public get(): DesktopStoreState {
    return this.state.get();
  }

  public update(fn: (prev: DesktopStoreState) => DesktopStoreState): void {
    this.state.set(fn);
  }

  private syncFromController(cState: AppControllerState): void {
    this.update((prev) => {
      const sessions: SessionSummary[] = cState.conversations.map((c) => ({
        sessionId: c.id,
        title: c.title,
        agentId: c.agentId,
        workspacePath: c.workspacePath,
        createdAt: c.createdAt,
        updatedAt: c.updatedAt,
        turnCount: c.turnCount,
      }));

      let pendingApproval = cState.pendingApproval;
      let activeDiffText = prev.activeDiffText;
      if (pendingApproval?.unifiedDiff) {
        activeDiffText = pendingApproval.unifiedDiff;
      }

      // Check for approval notifications
      if (pendingApproval && pendingApproval.approvalId !== this.lastNotifiedApprovalId) {
        this.lastNotifiedApprovalId = pendingApproval.approvalId;
        this.bridge.sendNotification(
          "AETHER Authorization Required",
          `Approval '${pendingApproval.approvalId}' requires operator sign-off.`
        );
      }

      const activeConv = cState.conversations.find((c) => c.id === cState.activeConversationId);
      const composerText = activeConv?.draft !== undefined && prev.activeSessionId !== cState.activeConversationId ? activeConv.draft : prev.composerText;

      return {
        ...prev,
        sessions,
        activeSessionId: cState.activeConversationId,
        agentId: cState.selectedAgentId,
        workflowId: cState.selectedWorkflowId,
        workspacePath: cState.currentWorkspace,
        recentWorkspaces: cState.recentWorkspaces,
        runId: cState.activeRunId,
        runs: cState.runs,
        providers: cState.providers,
        selectedProviderId: cState.selectedProviderId,
        readiness: cState.readiness,
        connectionState: (cState.connectionState.toLowerCase() as any),
        isStreaming: cState.isStreaming,
        statusMessage: cState.statusMessage,
        capabilities: cState.capabilities,
        lastFailure: cState.lastFailure,
        snapshot: cState.snapshot,
        events: cState.events,
        turns: cState.turns,
        activities: cState.activities,
        approvalState: cState.approvalState,
        evidenceGrid: cState.evidenceGrid,
        traceGraph: cState.traceGraph,
        pendingApproval,
        activeDiffText,
        multiFileDiff: cState.multiFileDiff,
        verificationSummaries: cState.verificationSummaries,
        researchSummary: cState.researchSummary,
        workflowExecution: cState.workflowExecution,
        settings: cState.settings,
        composerText,
      };
    });
  }

  public getGroupedSessions(): SessionGroup[] {
    const cur = this.get();
    const filtered = filterSessions(cur.sessions, cur.searchQuery);
    return groupSessionsByDate(filtered);
  }

  public newChat(): void {
    this.controller.newChat();
    this.update((prev) => ({
      ...prev,
      forensicDrawerOpen: false,
      composerText: "",
      hasUnreadContent: false,
    }));
  }

  public selectSession(sessionId: string): void {
    this.controller.selectConversation(sessionId);
  }

  public renameSession(sessionId: string, newTitle: string): void {
    this.controller.renameConversation(sessionId, newTitle);
  }

  public deleteSession(sessionId: string): void {
    this.controller.deleteConversation(sessionId);
  }

  public setDraft(draft: string): void {
    this.update((s) => ({ ...s, composerText: draft }));
    this.controller.setConversationDraft(draft);
  }

  public ingestEnvelope(envelope: EventEnvelope): void {
    this.controller.ingestEnvelope(envelope);
    this.update((prev) => {
      const cur = this.get();
      let diff = prev.activeDiffText;
      if (envelope.payload.unifiedDiff || envelope.payload.diff) {
        diff = String(envelope.payload.unifiedDiff ?? envelope.payload.diff);
      }
      return {
        ...cur,
        activeDiffText: diff,
        hasUnreadContent: !prev.scrollFollowStream,
      };
    });
  }

  public openForensicDrawer(tab: ForensicTab = "diffs", diffText?: string): void {
    this.update((prev) => ({
      ...prev,
      forensicDrawerOpen: true,
      activeForensicTab: tab,
      activeDiffText: diffText !== undefined ? diffText : prev.activeDiffText,
    }));
  }

  public closeForensicDrawer(): void {
    this.update((prev) => ({ ...prev, forensicDrawerOpen: false }));
  }

  public toggleCommandPalette(open?: boolean): void {
    this.update((prev) => ({
      ...prev,
      commandPaletteOpen: open !== undefined ? open : !prev.commandPaletteOpen,
      commandPaletteQuery: "",
    }));
  }

  public setLayoutMode(mode: LayoutMode): void {
    this.update((prev) => ({ ...prev, layoutMode: mode }));
  }

  public toggleSidebar(): void {
    this.update((prev) => ({ ...prev, sidebarOpen: !prev.sidebarOpen }));
  }

  public async startRun(client: RuntimeClient, prompt: string): Promise<void> {
    this.controller.setClient(client);
    await this.controller.startRun(prompt);
  }

  public async submitFollowUp(client: RuntimeClient, prompt: string): Promise<void> {
    this.controller.setClient(client);
    await this.controller.submitFollowUp(prompt);
  }

  public async attachStream(client: RuntimeClient, runId: string): Promise<void> {
    this.controller.setClient(client);
    await this.controller.attachRun(runId);
  }

  public async resolveApproval(
    client: RuntimeClient,
    decision: "approve" | "reject"
  ): Promise<void> {
    this.controller.setClient(client);
    const pending = this.get().pendingApproval;
    if (!pending) return;
    await this.controller.resolveApproval(pending.approvalId, decision);
  }

  public async cancelRun(): Promise<void> {
    await this.controller.cancelRun("User requested cancellation in Desktop");
  }

  public async checkpointRun(): Promise<void> {
    await this.controller.checkpointRun("Manual checkpoint from Desktop");
  }

  public async resumeRun(checkpointId?: string): Promise<void> {
    await this.controller.resumeRun(checkpointId);
  }

  // Cross-Surface Actions
  public openInLab(target?: DeepLinkTarget): void {
    const link = formatDeepLink(target ?? { kind: "run", runId: this.get().runId });
    this.bridge.openExternalUrl(`http://localhost:5174${link}`);
  }

  public copyCliCommand(runId?: string): void {
    const id = runId ?? this.get().runId;
    const cmd = `vg run inspect ${id}`;
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(cmd);
    }
  }

  public attachInTui(runId?: string): void {
    const id = runId ?? this.get().runId;
    const cmd = `vg run --attach ${id}`;
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(cmd);
    }
  }

  public handleDeepLink(uri: string): void {
    const target: DeepLinkTarget = { kind: "run", runId: this.get().runId };
    const resolved = resolveDeepLink(target, "desktop");
    if (resolved.desktopRoute?.tab) {
      this.openForensicDrawer(resolved.desktopRoute.tab as ForensicTab);
    }
  }

  public async startManagedRuntime(): Promise<void> {
    try {
      const { client } = await this.managedRuntime.ensureRunning();
      this.controller.setClient(client);
    } catch (err) {
      this.update((s) => ({
        ...s,
        connectionState: "unavailable",
        statusMessage: `Runtime startup error: ${String(err)}`,
      }));
    }
  }

  public async destroy(): Promise<void> {
    if (this.unsubscribeController) {
      this.unsubscribeController();
    }
    await this.managedRuntime.shutdown();
  }
}
