import {
  emptyRunSnapshot,
  reduceRunSnapshot,
  toConversationTurns,
  emptyApprovalState,
  reduceApprovalState,
  classifyActivityEnvelope,
  evaluateCapabilities,
  diagnoseFailure,
  type RunSnapshotModel,
  type ConversationTurn,
  type ApprovalState,
  type PendingApproval,
  type FrontendCapabilityFlags,
  type FailureDiagnostics,
} from "@aether/projections";
import type { EventEnvelope, AgentDescriptor, WorkflowDescriptor, SemanticActivityItem, ModelProviderConfig, FrontendSettings } from "@aether/contracts";
import type { RuntimeClient } from "@aether/client";
import {
  FrontendAppController,
  DEFAULT_AGENTS,
  DEFAULT_WORKFLOWS,
  NodeFsPersistenceAdapter,
  DEFAULT_PROVIDERS,
  mergeAgentCatalog,
  resolveHarnessManifestPath,
  executionProfileFor,
  type FrontendPersistencePort,
  InMemoryPersistenceAdapter,
} from "@aether/client";
import { DEFAULT_FRONTEND_SETTINGS } from "@aether/projections";
import {
  executeCommandLine,
  type TuiCommandContext,
  loadModelCatalog,
  resolveModelSelection,
  resolveModelsRegistryPath,
  ModelPolicyError,
  type ModelCatalogEntry,
  login as mockLogin,
  logout as mockLogout,
  expandFileReferences,
  runShellCommand,
} from "@aether/tui-core";
import { writeFileSync, existsSync, realpathSync } from "node:fs";
import { join } from "node:path";

// Fine-grained Signal primitive
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

export type FocusRegion = "composer" | "transcript" | "approval" | "modal" | "diff";

export type ConnectionState =
  | "connecting"
  | "connected"
  | "reconnecting"
  | "disconnected"
  | "unavailable";

export type TuiStoreState = {
  // Session metadata
  agentId: string;
  workflowId: string;
  workspacePath: string;
  model: string;
  runId: string;

  // Catalog
  availableAgents: AgentDescriptor[];
  availableWorkflows: WorkflowDescriptor[];
  availableModels: ModelCatalogEntry[];
  providers: ModelProviderConfig[];
  selectedProviderId: string;

  // Runtime & Stream status
  connectionState: ConnectionState;
  capabilities: FrontendCapabilityFlags;
  lastFailure: FailureDiagnostics | null;
  snapshot: RunSnapshotModel;
  events: EventEnvelope[];
  turns: ConversationTurn[];
  activities: SemanticActivityItem[];
  approvalState: ApprovalState;
  pendingApproval?: PendingApproval;

  // Governance
  planMode: boolean;
  accountLabel: string | null;

  // Status footer telemetry
  contextWindowTokens: number;
  lastEventAtMs: number | null;

  // Busy-input mode (Hermes): what a new message does while a run is active
  busyMode: "interrupt" | "queue" | "steer";
  queuedPrompt: string | null;

  // UI state
  focus: FocusRegion;
  composerText: string;
  composerCursor: number;
  composerHistory: string[];
  historyIndex: number;
  scrollOffset: number;
  followStream: boolean;
  expandedCardIds: Set<string>;
  activeModal: "none" | "command-palette" | "help" | "diff-viewer" | "select-agent" | "select-workflow" | "select-model" | "history";
  /** Highlighted row in the command palette or a select modal. Lives here so arrow keys re-render. */
  modalSelectedIndex: number;
  diffViewerContent: string;
  statusMessage: string;
  activeCommandQuery: string;
  settings: FrontendSettings;
};

export class TuiStore {
  public readonly controller: FrontendAppController;
  public readonly persistence: FrontendPersistencePort;
  public readonly state: Signal<TuiStoreState>;
  private abortController: AbortController | null = null;
  private lastClient?: RuntimeClient;
  private pinnedAgentId?: string;
  private pinnedWorkspacePath?: string;

  constructor(
    initial: Partial<TuiStoreState> = {},
    client?: RuntimeClient,
    persistence?: FrontendPersistencePort,
  ) {
    this.persistence =
      persistence ??
      (process.env.AETHER_IN_MEMORY_PERSISTENCE === "1" || process.env.NODE_ENV === "test"
        ? new InMemoryPersistenceAdapter()
        : new NodeFsPersistenceAdapter());

    let initialWs = initial.workspacePath ?? process.cwd();
    if (initialWs === ".") {
      initialWs = process.cwd();
    }
    try {
      if (existsSync(initialWs)) {
        initialWs = realpathSync(initialWs);
      }
    } catch {
      /* keep initialWs */
    }

    this.pinnedAgentId = initial.agentId;
    this.pinnedWorkspacePath = initialWs;

    this.controller = new FrontendAppController({
      client,
      persistence: this.persistence,
      initialWorkspace: initialWs,
      initialAgentId: initial.agentId ?? "vg-code-balanced",
    });

    const ctrlState = this.controller.getState();
    const wsPath = initialWs;

    this.state = createSignal<TuiStoreState>({
      agentId: initial.agentId ?? ctrlState.selectedAgentId,
      workflowId: initial.workflowId ?? ctrlState.selectedWorkflowId,
      workspacePath: wsPath,
      model: initial.model ?? "openrouter/free",
      runId: initial.runId ?? ctrlState.activeRunId,
      availableAgents: initial.availableAgents ?? mergeAgentCatalog(DEFAULT_AGENTS, wsPath),
      availableWorkflows: DEFAULT_WORKFLOWS,
      availableModels: initial.availableModels ?? this.loadAvailableModels(wsPath),
      providers: ctrlState.providers.length > 0 ? ctrlState.providers : DEFAULT_PROVIDERS,
      selectedProviderId: ctrlState.selectedProviderId,
      connectionState: initial.connectionState ?? "connected",
      capabilities: ctrlState.capabilities,
      lastFailure: ctrlState.lastFailure,
      snapshot: initial.snapshot ?? emptyRunSnapshot(),
      events: initial.events ?? [],
      turns: initial.turns ?? [],
      activities: [],
      approvalState: initial.approvalState ?? emptyApprovalState(),
      pendingApproval: initial.pendingApproval,
      planMode: initial.planMode ?? false,
      accountLabel: initial.accountLabel ?? null,
      contextWindowTokens: initial.contextWindowTokens ?? 128_000,
      lastEventAtMs: initial.lastEventAtMs ?? null,
      busyMode: initial.busyMode ?? "interrupt",
      queuedPrompt: initial.queuedPrompt ?? null,
      focus: initial.focus ?? "composer",
      composerText: initial.composerText ?? "",
      composerCursor: initial.composerCursor ?? 0,
      composerHistory: [],
      historyIndex: -1,
      scrollOffset: 0,
      followStream: true,
      expandedCardIds: new Set<string>(),
      activeModal: "none",
      modalSelectedIndex: 0,
      diffViewerContent: "",
      statusMessage: "Ready",
      activeCommandQuery: "",
      settings: ctrlState.settings ?? DEFAULT_FRONTEND_SETTINGS,
    });

    this.controller.subscribe((cState) => {
      this.syncFromController(cState);
    });

    this.initPersistence();
  }

  private async initPersistence(): Promise<void> {
    await this.controller.restoreFromPersistence();
    if (this.pinnedWorkspacePath) this.selectWorkspace(this.pinnedWorkspacePath);
    if (this.pinnedAgentId) this.selectAgent(this.pinnedAgentId);
  }

  private syncFromController(cState: any): void {
    this.update((prev) => {
      let effectiveTurns = cState.turns;
      if ((!effectiveTurns || effectiveTurns.length === 0) && prev.turns.length > 0) {
        effectiveTurns = prev.turns;
      }
      return {
        ...prev,
        workspacePath: this.pinnedWorkspacePath ?? cState.currentWorkspace,
        agentId: this.pinnedAgentId ?? cState.selectedAgentId,
        workflowId: cState.selectedWorkflowId,
        runId: cState.activeRunId,
        turns: effectiveTurns,
        events: cState.events,
        snapshot: cState.snapshot,
        activities: cState.activities,
        approvalState: cState.approvalState,
        pendingApproval: cState.pendingApproval,
        providers: cState.providers,
        selectedProviderId: cState.selectedProviderId,
        settings: cState.settings,
      };
    });
  }

  public get(): TuiStoreState {
    return this.state.get();
  }

  public update(fn: (prev: TuiStoreState) => TuiStoreState): void {
    this.state.set(fn);
  }

  public ingestEnvelope(envelope: EventEnvelope): void {
    this.controller.ingestEnvelope(envelope);

    this.update((prev) => {
      const nextEvents = [...prev.events, envelope];
      const nextSnapshot = reduceRunSnapshot(prev.snapshot, envelope);
      const nextTurns = toConversationTurns(nextEvents);
      const nextActivities = [...prev.activities, classifyActivityEnvelope(envelope)];
      const nextApprovalState = reduceApprovalState(prev.approvalState, envelope);

      let pendingApproval = nextSnapshot.pendingApproval;
      let focus = prev.focus;
      if (pendingApproval && prev.focus !== "approval") {
        focus = "approval";
      }

      return {
        ...prev,
        events: nextEvents,
        snapshot: nextSnapshot,
        turns: nextTurns,
        activities: nextActivities,
        approvalState: nextApprovalState,
        pendingApproval,
        focus,
        lastEventAtMs: Date.now(),
        runId: envelope.runId ?? prev.runId,
      };
    });

    const TERMINAL_STATUSES = new Set(["satisfied", "failed", "cancelled"]);
    const cur = this.get();
    if (TERMINAL_STATUSES.has(cur.snapshot.status) && cur.queuedPrompt && this.lastClient) {
      const prompt = cur.queuedPrompt;
      const client = this.lastClient;
      this.update((s) => ({ ...s, queuedPrompt: null, statusMessage: "Sending queued prompt..." }));
      this.submitFollowUp(client, prompt);
    }
  }

  public toggleCardExpansion(cardId: string): void {
    this.update((prev) => {
      const nextSet = new Set(prev.expandedCardIds);
      if (nextSet.has(cardId)) {
        nextSet.delete(cardId);
      } else {
        nextSet.add(cardId);
      }
      return { ...prev, expandedCardIds: nextSet };
    });
  }

  public setFocus(region: FocusRegion): void {
    this.update((prev) => ({ ...prev, focus: region }));
  }

  public setComposerText(text: string, cursor?: number): void {
    this.update((prev) => ({
      ...prev,
      composerText: text,
      composerCursor: cursor !== undefined ? cursor : text.length,
    }));
  }

  private isRunActive(): boolean {
    const status = this.get().snapshot.status;
    return status === "pending" || status === "running" || status === "awaiting_approval";
  }

  public submitComposer(client?: RuntimeClient): string {
    const raw = this.get().composerText.trim();
    if (!raw) return "";

    if (client) this.lastClient = client;

    const text = this.expandComposerReferences(raw);

    // Busy-input modes (Hermes): what a new message does while a run is
    // already active. "queue" defers the prompt until the current run
    // reaches a terminal state (see ingestEnvelope's auto-flush); "steer"
    // has no backend redirect primitive to steer an in-flight run onto, so
    // it explicitly falls back to "interrupt" rather than faking one.
    if (client && this.isRunActive() && this.get().busyMode === "queue") {
      this.update((prev) => ({
        ...prev,
        composerText: "",
        composerCursor: 0,
        composerHistory: [...prev.composerHistory, raw],
        historyIndex: -1,
        queuedPrompt: text,
        statusMessage: "Queued — will send once the current run finishes.",
      }));
      return text;
    }

    const optimisticTurn: ConversationTurn = {
      id: `optimistic-user-${Date.now()}`,
      speaker: "user",
      timestamp: new Date().toISOString(),
      text,
      activityCards: [],
    };

    const hadExistingTurns = this.get().turns.length > 0;

    this.update((prev) => ({
      ...prev,
      composerText: "",
      composerCursor: 0,
      composerHistory: [...prev.composerHistory, raw],
      historyIndex: -1,
      turns: prev.turns.some((t) => t.text === text) ? prev.turns : [...prev.turns, optimisticTurn],
      statusMessage: "Dispatched prompt...",
    }));

    if (client) {
      if (hadExistingTurns) {
        this.submitFollowUp(client, text);
      } else {
        this.startRun(client, text);
      }
    }
    return text;
  }

  public async submitFollowUp(client: RuntimeClient, prompt: string): Promise<void> {
    this.lastClient = client;
    this.controller.setClient(client);
    await this.controller.submitFollowUp(prompt);
  }

  public setBusyMode(mode: string): void {
    if (mode !== "interrupt" && mode !== "queue" && mode !== "steer") {
      this.update((s) => ({ ...s, statusMessage: `Unknown busy mode "${mode}"; use queue, steer, or interrupt.` }));
      return;
    }
    if (mode === "steer") {
      this.update((s) => ({
        ...s,
        busyMode: "interrupt",
        statusMessage: "steer is not yet supported (no in-flight redirect primitive) — falling back to interrupt.",
      }));
      return;
    }
    this.update((s) => ({ ...s, busyMode: mode, statusMessage: `Busy mode: ${mode}` }));
  }

  public selectAgent(agentId: string): void {
    this.controller.selectAgent(agentId);
    this.update((prev) => ({
      ...prev,
      agentId,
      statusMessage: `Agent switched to ${agentId}`,
    }));
  }

  public selectWorkflow(workflowId: string): void {
    this.controller.selectWorkflow(workflowId);
    this.update((prev) => ({
      ...prev,
      workflowId,
      statusMessage: `Workflow switched to ${workflowId}`,
    }));
  }

  public loadAvailableModels(wsPath: string = this.get().workspacePath): ModelCatalogEntry[] {
    try {
      const path = resolveModelsRegistryPath(wsPath) ?? resolveModelsRegistryPath(process.cwd());
      const catalog = loadModelCatalog(path);
      return [...catalog.entries];
    } catch {
      return [];
    }
  }

  public selectWorkspace(wsPath: string): void {
    this.pinnedWorkspacePath = wsPath;
    this.controller.selectWorkspace(wsPath);
    const availableModels = this.loadAvailableModels(wsPath);
    const availableAgents = mergeAgentCatalog(DEFAULT_AGENTS, wsPath);
    this.update((prev) => ({
      ...prev,
      workspacePath: wsPath,
      availableAgents: availableAgents.length > 0 ? availableAgents : prev.availableAgents,
      availableModels: availableModels.length > 0 ? availableModels : prev.availableModels,
      statusMessage: `Workspace switched to ${wsPath}`,
    }));
  }

  /**
   * The single dispatch target for slash commands, driven by @aether/tui-core's
   * command registry so the palette and the composer's "/name" parsing can never
   * disagree about what a given command does.
   */
  public buildCommandContext(client?: RuntimeClient, onExit?: () => void): TuiCommandContext {
    return {
      openModal: (modal) => {
        this.update((s) => ({
          ...s,
          activeModal: modal as TuiStoreState["activeModal"],
          modalSelectedIndex: 0,
          focus: "modal",
        }));
      },
      closeModal: () => this.update((s) => ({ ...s, activeModal: "none", modalSelectedIndex: 0, focus: "composer" })),
      selectAgent: (agentId) => this.selectAgent(agentId),
      selectWorkflow: (workflowId) => this.selectWorkflow(workflowId),
      selectWorkspace: (path) => this.selectWorkspace(path),
      setProvider: (providerId) => {
        this.controller.setDefaultProvider(providerId);
        this.update((s) => ({ ...s, selectedProviderId: providerId, statusMessage: `Default provider: ${providerId}` }));
      },
      setModel: (modelId) => this.setModel(modelId),
      togglePlanMode: () => this.togglePlanMode(),
      showStatus: (message) => this.update((s) => ({ ...s, statusMessage: message })),
      resume: (runIdOrLatest) => {
        if (client) this.controller.resumeRun(runIdOrLatest);
      },
      attach: (runId) => {
        if (client) this.attachStream(client, runId);
      },
      cancelRun: () => {
        const cur = this.get();
        if (cur.runId && client) {
          client.requestCancel(cur.runId, { reason: "Cancelled via /cancel" });
          this.update((s) => ({ ...s, statusMessage: "Cancellation requested..." }));
        }
      },
      newChat: () => {
        this.controller.newChat();
        this.update((s) => ({
          ...s,
          turns: [],
          events: [],
          snapshot: emptyRunSnapshot(),
          statusMessage: "New conversation started.",
        }));
      },
      clearTranscript: () => this.update((s) => ({ ...s, turns: [], statusMessage: "Transcript view cleared." })),
      exit: () => {
        if (onExit) onExit();
      },
      login: () => this.login(),
      logout: () => this.logout(),
      setTitle: (title) => {
        const activeId = this.controller.getState().activeConversationId;
        if (activeId) {
          this.controller.renameConversation(activeId, title);
        }
        this.update((s) => ({ ...s, statusMessage: `Title: ${title}` }));
      },
      showRunStatus: () => {
        const s = this.get();
        this.update((prev) => ({
          ...prev,
          statusMessage: `agent:${s.agentId} workflow:${s.workflowId} model:${s.model} workspace:${s.workspacePath} run:${s.runId || "none"} connection:${s.connectionState}${s.planMode ? " [PLAN]" : ""}`,
        }));
      },
      showContext: () => {
        const t = this.get().snapshot.tokens;
        this.update((s) => ({
          ...s,
          statusMessage: `context: ${t.totalTokens} tokens (in:${t.inTokens} out:${t.outTokens})`,
        }));
      },
      showCost: () => {
        const micros = Number(this.get().snapshot.costMicros || "0");
        const usd = (micros / 1_000_000).toFixed(4);
        this.update((s) => ({ ...s, statusMessage: `cost: $${usd}` }));
      },
      compactTranscript: () => {
        const KEEP = 5;
        this.update((s) => ({
          ...s,
          turns: s.turns.slice(-KEEP),
          statusMessage: `Transcript view compacted to the last ${KEEP} turns (local view only; run state is unaffected).`,
        }));
      },
      showDoctor: () => {
        const s = this.get();
        const daemon = this.controller.getState().daemonStatus;
        this.update((prev) => ({
          ...prev,
          statusMessage: `doctor: connection=${s.connectionState} daemon=${daemon ? JSON.stringify(daemon) : "unknown"} workspace=${s.workspacePath}`,
        }));
      },
      showDiff: () => {
        const pending = this.get().pendingApproval;
        if (pending?.unifiedDiff) {
          this.update((s) => ({ ...s, activeModal: "diff-viewer", diffViewerContent: pending.unifiedDiff }));
        } else {
          this.update((s) => ({ ...s, statusMessage: "No pending diff." }));
        }
      },
      undo: () => {
        this.update((s) => ({
          ...s,
          statusMessage: "/undo is not yet implemented — no git-backed rollback is wired up. Revert manually with git.",
        }));
      },
      initWorkspace: () => this.initWorkspace(),
      setBusyMode: (mode) => this.setBusyMode(mode),
    };
  }

  /** Seeds a minimal AETHER.md context file for the current workspace, if one does not already exist. */
  public initWorkspace(): void {
    const cur = this.get();
    const target = join(cur.workspacePath, "AETHER.md");
    if (existsSync(target)) {
      this.update((s) => ({ ...s, statusMessage: `AETHER.md already exists at ${target}` }));
      return;
    }
    const content = `# AETHER.md\n\nContext for AETHER coding agents working in this repository.\n\nGenerated by /init on ${new Date().toISOString()}.\n`;
    try {
      writeFileSync(target, content, { encoding: "utf-8" });
      this.update((s) => ({ ...s, statusMessage: `Wrote ${target}` }));
    } catch (err) {
      this.update((s) => ({ ...s, statusMessage: `/init failed: ${(err as Error).message}` }));
    }
  }

  /** Expands "@path" references in a composer prompt into inline file content before it is sent to the model. */
  public expandComposerReferences(text: string): string {
    return expandFileReferences(text, this.get().workspacePath).text;
  }

  /**
   * Hermes's zero-cost "!cmd" trick: runs a command locally and shows its
   * output, without invoking the model or touching the run/turn state.
   */
  public runLocalShellCommand(cmdText: string): void {
    const cur = this.get();
    const result = runShellCommand(cmdText, cur.workspacePath);
    const body = [
      `$ ${result.command}`,
      result.stdout.trim(),
      result.stderr.trim() ? `[stderr]\n${result.stderr.trim()}` : "",
      `[exit ${result.exitCode}]${result.truncated ? " (output truncated)" : ""}`,
    ].filter(Boolean).join("\n\n");
    this.update((s) => ({
      ...s,
      activeModal: "diff-viewer",
      diffViewerContent: body,
      statusMessage: `Ran locally: ${result.command} (exit ${result.exitCode})`,
    }));
  }

  public executeSlashCommand(input: string, client?: RuntimeClient, onExit?: () => void): void {
    const ctx = this.buildCommandContext(client, onExit);
    const result = executeCommandLine(input, ctx, { planMode: this.get().planMode });
    if (!result.ok) {
      this.update((s) => ({ ...s, statusMessage: result.error }));
    }
  }

  public setModel(requested: string): void {
    try {
      const path = resolveModelsRegistryPath(this.get().workspacePath) ?? resolveModelsRegistryPath(process.cwd());
      const catalog = loadModelCatalog(path);
      const resolved = resolveModelSelection(requested, catalog);
      this.update((s) => ({ ...s, model: resolved, statusMessage: `Model: ${resolved}` }));
    } catch (err) {
      const message = err instanceof ModelPolicyError ? err.message : String(err);
      this.update((s) => ({ ...s, statusMessage: message }));
    }
  }

  public togglePlanMode(): void {
    this.update((s) => ({
      ...s,
      planMode: !s.planMode,
      statusMessage: !s.planMode ? "Plan mode ON — writes withheld for the next turn" : "Plan mode OFF",
    }));
  }

  public async login(): Promise<void> {
    const result = await mockLogin(this.persistence);
    this.update((s) => ({
      ...s,
      accountLabel: result.session.account,
      statusMessage: `Open ${result.deviceUrl} in your browser to finish signing in.`,
    }));
  }

  public async logout(): Promise<void> {
    await mockLogout(this.persistence);
    this.update((s) => ({ ...s, accountLabel: null, statusMessage: "Signed out." }));
  }

  public async startRun(client: RuntimeClient, prompt: string): Promise<void> {
    const cur = this.get();
    if (!existsSync(cur.workspacePath)) {
      const errorMsg = `Workspace directory does not exist: "${cur.workspacePath}". Use /workspace <path> to switch.`;
      this.update((prev) => ({
        ...prev,
        connectionState: "unavailable",
        statusMessage: errorMsg,
        turns: [
          ...prev.turns,
          {
            id: `system-error-${Date.now()}`,
            speaker: "system",
            timestamp: new Date().toISOString(),
            text: `[Error: ${errorMsg}]`,
            activityCards: [],
            verdict: "failed",
          },
        ],
      }));
      return;
    }

    this.update((prev) => ({
      ...prev,
      connectionState: "connecting",
      statusMessage: "Starting agent run...",
    }));

    const manifestPath = resolveHarnessManifestPath(cur.agentId, cur.workspacePath);
    if (!manifestPath) {
      const msg = `No harness manifest for agent "${cur.agentId}". Use /agent vg-code-balanced (or vg-code-fast / vg-code-max).`;
      this.update((prev) => ({
        ...prev,
        connectionState: "unavailable",
        statusMessage: msg,
        turns: [
          ...prev.turns,
          {
            id: `system-error-${Date.now()}`,
            speaker: "system",
            timestamp: new Date().toISOString(),
            text: `[Error: ${msg}]`,
            activityCards: [],
            verdict: "failed",
          },
        ],
      }));
      return;
    }

    const res = await client.startRun({
      repo: cur.workspacePath,
      repoPath: cur.workspacePath,
      prompt,
      brief: prompt,
      model: cur.model,
      runId: cur.runId || undefined,
      manifestPath,
      // Execution profile is product vs plan — never the agent/harness id.
      profileId: executionProfileFor(cur.planMode),
    });

    if (!res.ok) {
      const diag = diagnoseFailure(res.error);
      this.update((prev) => ({
        ...prev,
        connectionState: "unavailable",
        lastFailure: diag,
        statusMessage: `Failed to start run: ${diag.cause}`,
        turns: [
          ...prev.turns,
          {
            id: `system-error-${Date.now()}`,
            speaker: "system",
            timestamp: new Date().toISOString(),
            text: `[Error: Failed to start run: ${diag.cause}]`,
            activityCards: [],
            verdict: "failed",
          },
        ],
      }));
      return;
    }

    const runId = res.value.runId;
    this.update((prev) => ({
      ...prev,
      runId,
      connectionState: "connected",
      statusMessage: `Attached to run ${runId}`,
    }));

    this.attachStream(client, runId);
  }

  public async attachStream(client: RuntimeClient, runId: string): Promise<void> {
    if (this.abortController) {
      this.abortController.abort();
    }
    this.abortController = new AbortController();
    const signal = this.abortController.signal;

    try {
      for await (const item of client.streamEvents({ runId }, signal)) {
        if (!item.ok) {
          const diag = diagnoseFailure(item.error);
          this.update((prev) => ({
            ...prev,
            connectionState: "reconnecting",
            lastFailure: diag,
            statusMessage: `Stream error: ${diag.cause}`,
          }));
          continue;
        }
        this.ingestEnvelope(item.value.envelope);
      }
    } catch {
      /* stream ended or aborted */
    }
  }

  public async resolvePendingApproval(
    client: RuntimeClient,
    decision: "approve" | "reject"
  ): Promise<void> {
    const pending = this.get().pendingApproval;
    if (!pending) return;

    this.update((prev) => ({
      ...prev,
      statusMessage: `Resolving approval ${pending.approvalId} [${decision}]...`,
    }));

    const res = await client.resolveApproval({
      approvalId: pending.approvalId,
      decision,
    });

    if (res.ok) {
      this.update((prev) => ({
        ...prev,
        pendingApproval: undefined,
        focus: "composer",
        statusMessage: `Approval ${pending.approvalId} resolved: ${decision}`,
      }));
    } else {
      const diag = diagnoseFailure(res.error);
      this.update((prev) => ({
        ...prev,
        lastFailure: diag,
        statusMessage: `Approval resolution failed: ${diag.cause}`,
      }));
    }
  }
}
