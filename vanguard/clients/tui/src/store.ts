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
import { FrontendAppController, DEFAULT_AGENTS, DEFAULT_WORKFLOWS, NodeFsPersistenceAdapter, DEFAULT_PROVIDERS } from "@aether/client";
import { DEFAULT_FRONTEND_SETTINGS } from "@aether/projections";

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

  // UI state
  focus: FocusRegion;
  composerText: string;
  composerCursor: number;
  composerHistory: string[];
  historyIndex: number;
  scrollOffset: number;
  followStream: boolean;
  expandedCardIds: Set<string>;
  activeModal: "none" | "command-palette" | "help" | "diff-viewer" | "select-agent" | "select-workflow" | "history";
  diffViewerContent: string;
  statusMessage: string;
  activeCommandQuery: string;
  settings: FrontendSettings;
};

export class TuiStore {
  public readonly controller: FrontendAppController;
  public readonly persistence: NodeFsPersistenceAdapter;
  public readonly state: Signal<TuiStoreState>;
  private abortController: AbortController | null = null;

  constructor(initial: Partial<TuiStoreState> = {}, client?: RuntimeClient) {
    this.persistence = new NodeFsPersistenceAdapter();
    this.controller = new FrontendAppController({
      client,
      persistence: this.persistence,
      initialWorkspace: initial.workspacePath ?? ".",
      initialAgentId: initial.agentId ?? "coding-agent",
    });

    const ctrlState = this.controller.getState();

    this.state = createSignal<TuiStoreState>({
      agentId: initial.agentId ?? ctrlState.selectedAgentId,
      workflowId: initial.workflowId ?? ctrlState.selectedWorkflowId,
      workspacePath: initial.workspacePath ?? ctrlState.currentWorkspace,
      model: initial.model ?? "openrouter/free",
      runId: initial.runId ?? ctrlState.activeRunId,
      availableAgents: DEFAULT_AGENTS,
      availableWorkflows: DEFAULT_WORKFLOWS,
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
      focus: initial.focus ?? "composer",
      composerText: initial.composerText ?? "",
      composerCursor: initial.composerCursor ?? 0,
      composerHistory: [],
      historyIndex: -1,
      scrollOffset: 0,
      followStream: true,
      expandedCardIds: new Set<string>(),
      activeModal: "none",
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
  }

  private syncFromController(cState: any): void {
    this.update((prev) => ({
      ...prev,
      workspacePath: cState.currentWorkspace,
      agentId: cState.selectedAgentId,
      workflowId: cState.selectedWorkflowId,
      runId: cState.activeRunId,
      turns: cState.turns,
      events: cState.events,
      snapshot: cState.snapshot,
      activities: cState.activities,
      approvalState: cState.approvalState,
      pendingApproval: cState.pendingApproval,
      providers: cState.providers,
      selectedProviderId: cState.selectedProviderId,
      settings: cState.settings,
    }));
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
        runId: envelope.runId ?? prev.runId,
      };
    });
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

  public submitComposer(client?: RuntimeClient): string {
    const text = this.get().composerText.trim();
    if (!text) return "";

    this.update((prev) => ({
      ...prev,
      composerText: "",
      composerCursor: 0,
      composerHistory: [...prev.composerHistory, text],
      historyIndex: -1,
      statusMessage: "Dispatched prompt...",
    }));

    if (client) {
      if (this.get().turns.length > 0) {
        this.submitFollowUp(client, text);
      } else {
        this.startRun(client, text);
      }
    }
    return text;
  }

  public async submitFollowUp(client: RuntimeClient, prompt: string): Promise<void> {
    this.controller.setClient(client);
    await this.controller.submitFollowUp(prompt);
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

  public selectWorkspace(wsPath: string): void {
    this.controller.selectWorkspace(wsPath);
    this.update((prev) => ({
      ...prev,
      workspacePath: wsPath,
      statusMessage: `Workspace switched to ${wsPath}`,
    }));
  }

  public executeSlashCommand(input: string, client?: RuntimeClient): void {
    const parts = input.slice(1).trim().split(/\s+/);
    const cmd = parts[0]?.toLowerCase() ?? "";
    const arg = parts.slice(1).join(" ");

    switch (cmd) {
      case "agent":
        if (arg) {
          this.selectAgent(arg);
        } else {
          this.update((s) => ({ ...s, activeModal: "select-agent" }));
        }
        break;
      case "workflow":
        if (arg) {
          this.selectWorkflow(arg);
        } else {
          this.update((s) => ({ ...s, activeModal: "select-workflow" }));
        }
        break;
      case "workspace":
        if (arg) {
          this.selectWorkspace(arg);
        } else {
          this.update((s) => ({ ...s, statusMessage: `Workspace: ${s.workspacePath}` }));
        }
        break;
      case "provider":
        if (arg) {
          this.controller.setDefaultProvider(arg);
          this.update((s) => ({ ...s, selectedProviderId: arg, statusMessage: `Default provider: ${arg}` }));
        } else {
          const cur = this.get();
          this.update((s) => ({ ...s, statusMessage: `Provider: ${cur.selectedProviderId}` }));
        }
        break;
      case "model":
        if (arg) {
          this.update((s) => ({ ...s, model: arg, statusMessage: `Model: ${arg}` }));
        } else {
          const cur = this.get();
          this.update((s) => ({ ...s, statusMessage: `Model: ${cur.model}` }));
        }
        break;
      case "runtime":
        this.update((s) => ({
          ...s,
          statusMessage: `Runtime: ${s.settings.runtime?.socketPath ?? "/tmp/vanguard-runtime.sock"} [${s.connectionState}]`,
        }));
        break;
      case "history":
        this.update((s) => ({ ...s, activeModal: "history" }));
        break;
      case "new":
        this.controller.newChat();
        this.update((s) => ({
          ...s,
          turns: [],
          events: [],
          snapshot: emptyRunSnapshot(),
          statusMessage: "New conversation started.",
        }));
        break;
      case "clear":
        this.update((s) => ({ ...s, turns: [], statusMessage: "Transcript view cleared." }));
        break;
      case "help":
        this.update((s) => ({ ...s, activeModal: "help" }));
        break;
      case "attach":
        if (arg && client) {
          this.attachStream(client, arg);
        }
        break;
      case "resume":
        if (client) {
          this.controller.resumeRun(arg || undefined);
        }
        break;
      default:
        this.update((s) => ({ ...s, statusMessage: `Unknown slash command: /${cmd}` }));
    }
  }

  public async startRun(client: RuntimeClient, prompt: string): Promise<void> {
    const cur = this.get();
    this.update((prev) => ({
      ...prev,
      connectionState: "connecting",
      statusMessage: "Starting agent run...",
    }));

    const res = await client.startRun({
      repo: cur.workspacePath,
      prompt,
      model: cur.model,
      runId: cur.runId || undefined,
    });

    if (!res.ok) {
      const diag = diagnoseFailure(res.error);
      this.update((prev) => ({
        ...prev,
        connectionState: "unavailable",
        lastFailure: diag,
        statusMessage: `Failed to start run: ${diag.cause}`,
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
