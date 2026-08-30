import type {
  AgentDescriptor,
  WorkflowDescriptor,
  FrontendConnectionState,
  FrontendSettings,
  EventEnvelope,
  RunSummary,
  RunRef,
  CommandReceipt,
  ResolveApprovalRequest,
  ApprovalDecision,
  StartRunRequest,
  DaemonStatus,
  SemanticActivityItem,
} from "@aether/contracts";
import {
  emptyRunSnapshot,
  reduceRunSnapshot,
  toConversationTurns,
  emptyApprovalState,
  reduceApprovalState,
  emptyEvidenceGrid,
  reduceEvidence,
  emptyTraceGraph,
  reduceTraceGraph,
  classifyActivityEnvelope,
  evaluateCapabilities,
  diagnoseFailure,
  DEFAULT_FRONTEND_SETTINGS,
  mergeSettings,
  type RunSnapshotModel,
  type ConversationTurn,
  type ApprovalState,
  type EvidenceGrid,
  type TraceGraph,
  type PendingApproval,
  type FrontendCapabilityFlags,
  type FailureDiagnostics,
} from "@aether/projections";
import type { RuntimeClient } from "../client.js";
import { SocketRuntimeClient } from "../transports/socket.js";
import { HttpRuntimeClient } from "../transports/http.js";

export type ConversationGroup = {
  label: "Today" | "Yesterday" | "Last 7 Days" | "Older";
  conversations: ConversationRecord[];
};

export type ConversationRecord = {
  id: string;
  title: string;
  agentId: string;
  workflowId?: string;
  workspacePath: string;
  runIds: string[];
  activeRunId: string;
  createdAt: string;
  updatedAt: string;
  draft: string;
  turnCount: number;
};

export type AppControllerState = {
  // Connection & Transport
  connectionState: FrontendConnectionState;
  daemonStatus: DaemonStatus | null;
  capabilities: FrontendCapabilityFlags;
  runtimeUrlOrSocket: string;

  // Workspace
  currentWorkspace: string;
  recentWorkspaces: string[];

  // Catalog
  availableAgents: AgentDescriptor[];
  selectedAgentId: string;
  recentAgentIds: string[];

  availableWorkflows: WorkflowDescriptor[];
  selectedWorkflowId: string;

  // Runs & Stream
  activeRunId: string;
  attachedRunId: string;
  runs: RunSummary[];
  isStreaming: boolean;
  streamCursorSeq: string;

  // Projections
  snapshot: RunSnapshotModel;
  events: EventEnvelope[];
  turns: ConversationTurn[];
  activities: SemanticActivityItem[];
  approvalState: ApprovalState;
  evidenceGrid: EvidenceGrid;
  traceGraph: TraceGraph;
  pendingApproval?: PendingApproval;

  // Conversation Index
  conversations: ConversationRecord[];
  activeConversationId: string;
  searchQuery: string;

  // Preferences & Settings
  settings: FrontendSettings;

  // Failure & Diagnostics
  lastFailure: FailureDiagnostics | null;
  statusMessage: string;
};

export const DEFAULT_AGENTS: AgentDescriptor[] = [
  {
    id: "coding-agent",
    name: "Coding Agent",
    description: "Autonomous software development agent with full repository context, test execution, and patch synthesis.",
    validationStatus: "valid",
    modelSummary: "deepseek-coder / claude-3-5-sonnet",
    toolSummary: ["fs.read", "fs.write", "search.grep", "shell.exec", "test.run"],
    capabilitySummary: ["Patch Generation", "Deterministic Tests", "Signed Approvals"],
    manifestPath: "agents/coding-agent.manifest.yaml",
  },
  {
    id: "research-agent",
    name: "Research & Synthesis Agent",
    description: "Read-only architectural analysis, literature search, and codebase exploration agent.",
    validationStatus: "valid",
    modelSummary: "openrouter/free",
    toolSummary: ["fs.read", "search.grep", "web.search"],
    capabilitySummary: ["Evidence Mapping", "Citation Graph"],
    manifestPath: "agents/research-agent.manifest.yaml",
  },
  {
    id: "review-agent",
    name: "Verification & Audit Agent",
    description: "Security and invariant compliance auditor analyzing patches and provenance DAGs.",
    validationStatus: "valid",
    modelSummary: "claude-3-5-sonnet",
    toolSummary: ["fs.read", "trace.inspect", "verify.invariant"],
    capabilitySummary: ["Security Proofs", "TCB Audit"],
    manifestPath: "agents/review-agent.manifest.yaml",
  },
];

export const DEFAULT_WORKFLOWS: WorkflowDescriptor[] = [
  {
    id: "default-turn-loop",
    name: "Standard Autonomous Turn Loop",
    description: "Interactive single-agent episode loop with operator approval checkpoints.",
    manifestPath: "workflows/turn-loop.yaml",
    validationStatus: "valid",
    participatingAgents: ["coding-agent"],
    entrypointOrStages: ["S0-Observe", "S1-Plan", "S2-Dispatch", "S3-Verify"],
  },
  {
    id: "multi-agent-audit",
    name: "Peer Review & Verification Pipeline",
    description: "Collaborative pipeline dispatching code modifications to independent audit agents before operator review.",
    manifestPath: "workflows/peer-review.yaml",
    validationStatus: "valid",
    participatingAgents: ["coding-agent", "review-agent"],
    entrypointOrStages: ["Develop", "Audit", "Approve", "Commit"],
  },
];

export class FrontendAppController {
  private client: RuntimeClient | null = null;
  private abortController: AbortController | null = null;
  private state: AppControllerState;
  private listeners = new Set<(state: AppControllerState) => void>();

  constructor(options?: {
    client?: RuntimeClient;
    initialSettings?: Partial<FrontendSettings>;
    initialWorkspace?: string;
    initialAgentId?: string;
  }) {
    const settings = mergeSettings(DEFAULT_FRONTEND_SETTINGS, options?.initialSettings);
    const initialWorkspace = options?.initialWorkspace ?? settings.general.defaultWorkspace;
    const initialAgentId = options?.initialAgentId ?? settings.general.defaultAgent;
    const initialConvId = `conv-${Date.now()}`;

    const defaultConversation: ConversationRecord = {
      id: initialConvId,
      title: "Workspace Session",
      agentId: initialAgentId,
      workflowId: settings.general.defaultWorkflow,
      workspacePath: initialWorkspace,
      runIds: [],
      activeRunId: "",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      draft: "",
      turnCount: 0,
    };

    this.client = options?.client ?? null;

    this.state = {
      connectionState: this.client ? "CONNECTED" : "OFFLINE",
      daemonStatus: null,
      capabilities: evaluateCapabilities(null),
      runtimeUrlOrSocket: settings.runtime.socketPath,
      currentWorkspace: initialWorkspace,
      recentWorkspaces: settings.workspace.recentWorkspaces,
      availableAgents: DEFAULT_AGENTS,
      selectedAgentId: initialAgentId,
      recentAgentIds: [initialAgentId],
      availableWorkflows: DEFAULT_WORKFLOWS,
      selectedWorkflowId: settings.general.defaultWorkflow,
      activeRunId: "",
      attachedRunId: "",
      runs: [],
      isStreaming: false,
      streamCursorSeq: "0",
      snapshot: emptyRunSnapshot(),
      events: [],
      turns: [],
      activities: [],
      approvalState: emptyApprovalState(),
      evidenceGrid: emptyEvidenceGrid(),
      traceGraph: emptyTraceGraph(),
      pendingApproval: undefined,
      conversations: [defaultConversation],
      activeConversationId: initialConvId,
      searchQuery: "",
      settings,
      lastFailure: null,
      statusMessage: "Ready",
    };
  }

  public getState(): AppControllerState {
    return this.state;
  }

  public subscribe(listener: (state: AppControllerState) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(): void {
    for (const listener of this.listeners) {
      listener(this.state);
    }
  }

  public updateState(fn: (prev: AppControllerState) => AppControllerState): void {
    this.state = fn(this.state);
    this.emit();
  }

  public getClient(): RuntimeClient | null {
    return this.client;
  }

  public setClient(client: RuntimeClient | null): void {
    this.client = client;
    this.updateState((s) => ({
      ...s,
      connectionState: client ? "CONNECTED" : "OFFLINE",
    }));
  }

  // 1. RUNTIME CONNECTION
  public async connectRuntime(target?: { socketPath?: string; httpUrl?: string }): Promise<boolean> {
    const socketPath = target?.socketPath ?? this.state.settings.runtime.socketPath;
    const httpUrl = target?.httpUrl ?? this.state.settings.runtime.httpUrl;

    this.updateState((s) => ({
      ...s,
      connectionState: "CONNECTING",
      statusMessage: "Connecting to AETHER runtime...",
      lastFailure: null,
    }));

    try {
      if (target?.httpUrl) {
        this.client = new HttpRuntimeClient({ baseUrl: httpUrl });
      } else {
        this.client = new SocketRuntimeClient({ socketPath });
      }

      const [statusRes, capsRes] = await Promise.all([
        this.client.getDaemonStatus(),
        this.client.getCapabilities(),
      ]);

      const daemonStatus = statusRes.ok ? statusRes.value : null;
      const capabilities = evaluateCapabilities(capsRes.ok ? capsRes.value : null);

      this.updateState((s) => ({
        ...s,
        connectionState: "CONNECTED",
        daemonStatus,
        capabilities,
        runtimeUrlOrSocket: target?.httpUrl ? httpUrl : socketPath,
        statusMessage: `Connected to runtime (socket: ${socketPath})`,
      }));

      // Refresh runs list
      this.refreshRuns();
      return true;
    } catch (err) {
      const diag = diagnoseFailure(err);
      this.updateState((s) => ({
        ...s,
        connectionState: "OFFLINE",
        lastFailure: diag,
        statusMessage: `Connection failed: ${diag.cause}`,
      }));
      return false;
    }
  }

  public disconnectRuntime(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
    this.client = null;
    this.updateState((s) => ({
      ...s,
      connectionState: "OFFLINE",
      isStreaming: false,
      statusMessage: "Disconnected from runtime",
    }));
  }

  public async reconnectRuntime(): Promise<boolean> {
    this.updateState((s) => ({
      ...s,
      connectionState: "RECONNECTING",
      statusMessage: "Reconnecting to runtime...",
    }));

    const success = await this.connectRuntime();
    if (success && this.state.activeRunId) {
      // Re-attach with cursor
      this.attachRun(this.state.activeRunId);
    }
    return success;
  }

  // 2. WORKSPACE MANAGEMENT
  public selectWorkspace(path: string): void {
    const clean = path.trim();
    if (!clean) return;

    this.updateState((s) => {
      const updatedRecents = [clean, ...s.recentWorkspaces.filter((w) => w !== clean)].slice(
        0,
        s.settings.workspace.maxRecentWorkspaces
      );
      return {
        ...s,
        currentWorkspace: clean,
        recentWorkspaces: updatedRecents,
        statusMessage: `Workspace selected: ${clean}`,
      };
    });
  }

  public switchWorkspace(path: string): void {
    this.selectWorkspace(path);
  }

  public clearRecentWorkspaces(): void {
    this.updateState((s) => ({
      ...s,
      recentWorkspaces: [s.currentWorkspace],
    }));
  }

  // 3. AGENT & WORKFLOW SELECTION
  public selectAgent(agentId: string): void {
    const found = this.state.availableAgents.find((a) => a.id === agentId);
    if (!found) return;

    this.updateState((s) => ({
      ...s,
      selectedAgentId: agentId,
      recentAgentIds: [agentId, ...s.recentAgentIds.filter((id) => id !== agentId)].slice(0, 5),
      statusMessage: `Agent switched to ${found.name}`,
    }));
  }

  public selectWorkflow(workflowId: string): void {
    const found = this.state.availableWorkflows.find((w) => w.id === workflowId);
    if (!found) return;

    this.updateState((s) => ({
      ...s,
      selectedWorkflowId: workflowId,
      statusMessage: `Workflow switched to ${found.name}`,
    }));
  }

  // 4. CONVERSATION MANAGEMENT
  public newChat(): void {
    const newId = `conv-${Date.now()}`;
    const newConv: ConversationRecord = {
      id: newId,
      title: "New Conversation",
      agentId: this.state.selectedAgentId,
      workflowId: this.state.selectedWorkflowId,
      workspacePath: this.state.currentWorkspace,
      runIds: [],
      activeRunId: "",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      draft: "",
      turnCount: 0,
    };

    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }

    this.updateState((s) => ({
      ...s,
      conversations: [newConv, ...s.conversations],
      activeConversationId: newId,
      activeRunId: "",
      attachedRunId: "",
      isStreaming: false,
      streamCursorSeq: "0",
      snapshot: emptyRunSnapshot(),
      events: [],
      turns: [],
      activities: [],
      approvalState: emptyApprovalState(),
      evidenceGrid: emptyEvidenceGrid(),
      traceGraph: emptyTraceGraph(),
      pendingApproval: undefined,
      lastFailure: null,
      statusMessage: "New chat started",
    }));
  }

  public selectConversation(conversationId: string): void {
    const conv = this.state.conversations.find((c) => c.id === conversationId);
    if (!conv) return;

    this.updateState((s) => ({
      ...s,
      activeConversationId: conversationId,
      selectedAgentId: conv.agentId || s.selectedAgentId,
      selectedWorkflowId: conv.workflowId || s.selectedWorkflowId,
      currentWorkspace: conv.workspacePath || s.currentWorkspace,
      statusMessage: `Switched to conversation: ${conv.title}`,
    }));

    if (conv.activeRunId) {
      this.switchRun(conv.activeRunId);
    }
  }

  public renameConversation(conversationId: string, newTitle: string): void {
    const clean = newTitle.trim();
    if (!clean) return;

    this.updateState((s) => ({
      ...s,
      conversations: s.conversations.map((c) =>
        c.id === conversationId ? { ...c, title: clean, updatedAt: new Date().toISOString() } : c
      ),
    }));
  }

  public deleteConversation(conversationId: string): void {
    this.updateState((s) => {
      const remaining = s.conversations.filter((c) => c.id !== conversationId);
      const nextActive = remaining[0]?.id ?? `conv-${Date.now()}`;
      const finalConversations = remaining.length > 0
        ? remaining
        : [
            {
              id: nextActive,
              title: "New Conversation",
              agentId: s.selectedAgentId,
              workflowId: s.selectedWorkflowId,
              workspacePath: s.currentWorkspace,
              runIds: [],
              activeRunId: "",
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              draft: "",
              turnCount: 0,
            },
          ];

      return {
        ...s,
        conversations: finalConversations,
        activeConversationId: s.activeConversationId === conversationId ? nextActive : s.activeConversationId,
      };
    });
  }

  public restoreConversationFromRun(runId: string, title?: string): void {
    const newId = `conv-run-${runId}`;
    const newConv: ConversationRecord = {
      id: newId,
      title: title ?? `Run ${runId.slice(0, 8)}`,
      agentId: this.state.selectedAgentId,
      workspacePath: this.state.currentWorkspace,
      runIds: [runId],
      activeRunId: runId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      draft: "",
      turnCount: 0,
    };

    this.updateState((s) => ({
      ...s,
      conversations: [newConv, ...s.conversations.filter((c) => c.id !== newId)],
      activeConversationId: newId,
    }));

    this.attachRun(runId);
  }

  public getGroupedConversations(): ConversationGroup[] {
    const s = this.state;
    const query = s.searchQuery.toLowerCase().trim();
    const filtered = s.conversations.filter(
      (c) => !query || c.title.toLowerCase().includes(query) || c.agentId.toLowerCase().includes(query)
    );

    const now = Date.now();
    const oneDay = 24 * 60 * 60 * 1000;

    const today: ConversationRecord[] = [];
    const yesterday: ConversationRecord[] = [];
    const last7Days: ConversationRecord[] = [];
    const older: ConversationRecord[] = [];

    for (const c of filtered) {
      const updated = new Date(c.updatedAt).getTime();
      const diffDays = Math.floor((now - updated) / oneDay);

      if (diffDays < 1) {
        today.push(c);
      } else if (diffDays < 2) {
        yesterday.push(c);
      } else if (diffDays < 7) {
        last7Days.push(c);
      } else {
        older.push(c);
      }
    }

    const groups: ConversationGroup[] = [];
    if (today.length > 0) groups.push({ label: "Today", conversations: today });
    if (yesterday.length > 0) groups.push({ label: "Yesterday", conversations: yesterday });
    if (last7Days.length > 0) groups.push({ label: "Last 7 Days", conversations: last7Days });
    if (older.length > 0) groups.push({ label: "Older", conversations: older });

    return groups;
  }

  // 5. RUN LIFECYCLE & INGESTION
  public async refreshRuns(): Promise<void> {
    if (!this.client) return;

    const res = await this.client.listRuns();
    if (res.ok) {
      this.updateState((s) => ({
        ...s,
        runs: res.value,
      }));
    }
  }

  public ingestEnvelope(envelope: EventEnvelope): void {
    this.updateState((prev) => {
      const nextEvents = [...prev.events, envelope];
      const nextSnapshot = reduceRunSnapshot(prev.snapshot, envelope);
      const nextTurns = toConversationTurns(nextEvents);
      const nextActivities = [...prev.activities, classifyActivityEnvelope(envelope)];
      const nextApprovalState = reduceApprovalState(prev.approvalState, envelope);
      const nextEvidence = reduceEvidence(prev.evidenceGrid, envelope);
      const nextTraceGraph = reduceTraceGraph(prev.traceGraph, envelope);

      const pendingApproval = nextSnapshot.pendingApproval;
      const runId = envelope.runId ?? prev.activeRunId;
      const seq = envelope.seq ?? prev.streamCursorSeq;

      // Update conversation metadata
      const updatedConversations = prev.conversations.map((c) => {
        if (c.id === prev.activeConversationId) {
          const firstGoal = nextTurns.find((t) => t.speaker === "user")?.text;
          const runIds = c.runIds.includes(runId) ? c.runIds : [...c.runIds, runId];
          return {
            ...c,
            title: c.title === "New Conversation" && firstGoal ? firstGoal.slice(0, 36) : c.title,
            updatedAt: new Date().toISOString(),
            turnCount: nextTurns.length,
            activeRunId: runId,
            runIds,
          };
        }
        return c;
      });

      return {
        ...prev,
        events: nextEvents,
        snapshot: nextSnapshot,
        turns: nextTurns,
        activities: nextActivities,
        approvalState: nextApprovalState,
        evidenceGrid: nextEvidence,
        traceGraph: nextTraceGraph,
        pendingApproval,
        activeRunId: runId,
        streamCursorSeq: seq,
        conversations: updatedConversations,
      };
    });
  }

  public async startRun(prompt: string, options?: Partial<StartRunRequest>): Promise<RunRef | null> {
    if (!this.client) {
      const diag = diagnoseFailure({ code: "not_available", message: "No active runtime connection" });
      this.updateState((s) => ({ ...s, lastFailure: diag, statusMessage: diag.cause }));
      return null;
    }

    const s = this.state;
    this.updateState((prev) => ({
      ...prev,
      isStreaming: true,
      statusMessage: "Starting agent run...",
      lastFailure: null,
    }));

    const agent = s.availableAgents.find((a) => a.id === s.selectedAgentId);
    const req: StartRunRequest = {
      repo: s.currentWorkspace,
      prompt,
      model: agent?.modelSummary.split("/")[0] ?? "openrouter/free",
      profileId: s.selectedAgentId,
      ...options,
    };

    const res = await this.client.startRun(req);
    if (!res.ok) {
      const diag = diagnoseFailure(res.error);
      this.updateState((prev) => ({
        ...prev,
        isStreaming: false,
        lastFailure: diag,
        statusMessage: `Start failed: ${diag.cause}`,
      }));
      return null;
    }

    const runRef = res.value;
    this.updateState((prev) => ({
      ...prev,
      activeRunId: runRef.runId,
      attachedRunId: runRef.runId,
      statusMessage: `Attached to run ${runRef.runId}`,
    }));

    // Begin streaming
    this.attachRun(runRef.runId);
    return runRef;
  }

  public async attachRun(runId: string): Promise<void> {
    if (!this.client) return;

    if (this.abortController) {
      this.abortController.abort();
    }
    this.abortController = new AbortController();
    const signal = this.abortController.signal;

    const afterSeq = this.state.streamCursorSeq !== "0" ? this.state.streamCursorSeq : undefined;

    this.updateState((s) => ({
      ...s,
      activeRunId: runId,
      attachedRunId: runId,
      isStreaming: true,
      statusMessage: `Streaming events for run ${runId}...`,
    }));

    try {
      for await (const item of this.client.streamEvents({ runId, afterSeq }, signal)) {
        if (!item.ok) {
          const diag = diagnoseFailure(item.error);
          this.updateState((prev) => ({
            ...prev,
            connectionState: "RECONNECTING",
            statusMessage: `Stream issue: ${diag.cause}`,
            lastFailure: diag,
          }));
          continue;
        }

        if (this.state.connectionState !== "CONNECTED") {
          this.updateState((prev) => ({ ...prev, connectionState: "CONNECTED", lastFailure: null }));
        }

        this.ingestEnvelope(item.value.envelope);
      }
    } catch {
      /* Stream finished or aborted */
    } finally {
      this.updateState((prev) => ({
        ...prev,
        isStreaming: false,
        statusMessage: prev.snapshot.status ? `Run status: ${prev.snapshot.status}` : "Idle",
      }));
    }
  }

  public switchRun(runId: string): void {
    if (runId === this.state.activeRunId) return;

    this.updateState((s) => ({
      ...s,
      activeRunId: runId,
      attachedRunId: runId,
      streamCursorSeq: "0",
      snapshot: emptyRunSnapshot(),
      events: [],
      turns: [],
      activities: [],
      approvalState: emptyApprovalState(),
      evidenceGrid: emptyEvidenceGrid(),
      traceGraph: emptyTraceGraph(),
      pendingApproval: undefined,
    }));

    this.attachRun(runId);
  }

  public async cancelRun(reason?: string): Promise<CommandReceipt | null> {
    if (!this.client || !this.state.activeRunId) return null;

    this.updateState((s) => ({ ...s, statusMessage: "Requesting cancellation..." }));

    const res = await this.client.requestCancel(this.state.activeRunId, { reason });
    if (res.ok) {
      this.updateState((s) => ({
        ...s,
        isStreaming: false,
        statusMessage: "Run cancellation confirmed",
      }));
      return res.value;
    } else {
      const diag = diagnoseFailure(res.error);
      this.updateState((s) => ({ ...s, lastFailure: diag, statusMessage: `Cancel failed: ${diag.cause}` }));
      return null;
    }
  }

  public async checkpointRun(reason?: string): Promise<CommandReceipt | null> {
    if (!this.client || !this.state.activeRunId) return null;

    this.updateState((s) => ({ ...s, statusMessage: "Requesting checkpoint..." }));

    const res = await this.client.requestCheckpoint(this.state.activeRunId, { reason });
    if (res.ok) {
      this.updateState((s) => ({ ...s, statusMessage: "Checkpoint recorded successfully" }));
      return res.value;
    } else {
      const diag = diagnoseFailure(res.error);
      this.updateState((s) => ({ ...s, lastFailure: diag, statusMessage: `Checkpoint failed: ${diag.cause}` }));
      return null;
    }
  }

  public async resumeRun(checkpointId?: string): Promise<CommandReceipt | null> {
    if (!this.client || !this.state.activeRunId) return null;

    this.updateState((s) => ({ ...s, statusMessage: "Resuming run..." }));

    const res = await this.client.requestResume(this.state.activeRunId, { checkpointId });
    if (res.ok) {
      this.updateState((s) => ({ ...s, statusMessage: "Run resumed" }));
      this.attachRun(this.state.activeRunId);
      return res.value;
    } else {
      const diag = diagnoseFailure(res.error);
      this.updateState((s) => ({ ...s, lastFailure: diag, statusMessage: `Resume failed: ${diag.cause}` }));
      return null;
    }
  }

  // 6. APPROVAL RESOLUTION
  public async resolveApproval(
    approvalId: string,
    decision: "approve" | "reject" | ApprovalDecision
  ): Promise<CommandReceipt | null> {
    if (!this.client) return null;

    this.updateState((s) => ({
      ...s,
      statusMessage: `Resolving approval ${approvalId}...`,
    }));

    const req: ResolveApprovalRequest = {
      approvalId,
      decision,
    };

    const res = await this.client.resolveApproval(req);
    if (res.ok) {
      this.updateState((s) => ({
        ...s,
        pendingApproval: undefined,
        statusMessage: `Approval ${approvalId} resolved.`,
      }));
      return res.value;
    } else {
      const diag = diagnoseFailure(res.error);
      this.updateState((s) => ({
        ...s,
        lastFailure: diag,
        statusMessage: `Approval resolution failed: ${diag.cause}`,
      }));
      return null;
    }
  }

  // 7. SETTINGS & DRAFTS
  public updateSettings(partial: Partial<FrontendSettings>): void {
    this.updateState((s) => ({
      ...s,
      settings: mergeSettings(s.settings, partial),
    }));
  }

  public setConversationDraft(draft: string): void {
    this.updateState((s) => ({
      ...s,
      conversations: s.conversations.map((c) =>
        c.id === s.activeConversationId ? { ...c, draft } : c
      ),
    }));
  }

  public setSearchQuery(query: string): void {
    this.updateState((s) => ({
      ...s,
      searchQuery: query,
    }));
  }

  public clearFailure(): void {
    this.updateState((s) => ({
      ...s,
      lastFailure: null,
    }));
  }
}
