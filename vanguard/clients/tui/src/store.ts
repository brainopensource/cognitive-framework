import {
  emptyRunSnapshot,
  reduceRunSnapshot,
  toConversationTurns,
  emptyApprovalState,
  reduceApprovalState,
  type RunSnapshotModel,
  type ConversationTurn,
  type ApprovalState,
  type PendingApproval,
} from "@aether/projections";
import type { EventEnvelope } from "@aether/contracts";
import type { RuntimeClient } from "@aether/client";

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

  // Runtime & Stream status
  connectionState: ConnectionState;
  snapshot: RunSnapshotModel;
  events: EventEnvelope[];
  turns: ConversationTurn[];
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
  activeModal: "none" | "command-palette" | "help" | "diff-viewer" | "select-agent" | "select-workflow";
  diffViewerContent: string;
  statusMessage: string;
  activeCommandQuery: string;
};

export class TuiStore {
  public readonly state: Signal<TuiStoreState>;
  private abortController: AbortController | null = null;

  constructor(initial: Partial<TuiStoreState> = {}) {
    this.state = createSignal<TuiStoreState>({
      agentId: initial.agentId ?? "coding-agent",
      workflowId: initial.workflowId ?? "default-turn-loop",
      workspacePath: initial.workspacePath ?? ".",
      model: initial.model ?? "openrouter/free",
      runId: initial.runId ?? "",
      connectionState: initial.connectionState ?? "connected",
      snapshot: initial.snapshot ?? emptyRunSnapshot(),
      events: initial.events ?? [],
      turns: initial.turns ?? [],
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
    });
  }

  public get(): TuiStoreState {
    return this.state.get();
  }

  public update(fn: (prev: TuiStoreState) => TuiStoreState): void {
    this.state.set(fn);
  }

  public ingestEnvelope(envelope: EventEnvelope): void {
    this.update((prev) => {
      const nextEvents = [...prev.events, envelope];
      const nextSnapshot = reduceRunSnapshot(prev.snapshot, envelope);
      const nextTurns = toConversationTurns(nextEvents);
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
      this.startRun(client, text);
    }
    return text;
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
      this.update((prev) => ({
        ...prev,
        connectionState: "unavailable",
        statusMessage: `Failed to start run: ${res.error.message}`,
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
          this.update((prev) => ({
            ...prev,
            connectionState: "reconnecting",
            statusMessage: `Stream error: ${item.error.message}`,
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
      this.update((prev) => ({
        ...prev,
        statusMessage: `Approval resolution failed: ${res.error.message}`,
      }));
    }
  }
}
