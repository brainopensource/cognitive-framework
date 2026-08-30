import {
  emptyRunSnapshot,
  reduceRunSnapshot,
  toConversationTurns,
  emptyApprovalState,
  reduceApprovalState,
  emptyEvidenceGrid,
  reduceEvidence,
  type RunSnapshotModel,
  type ConversationTurn,
  type ApprovalState,
  type EvidenceGrid,
  type PendingApproval,
} from "@aether/projections";
import type { EventEnvelope } from "@aether/contracts";
import type { RuntimeClient } from "@aether/client";
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

export type ForensicTab = "diffs" | "evidence" | "artifacts";

export type DesktopStoreState = {
  // Session & Workspace
  sessions: SessionSummary[];
  activeSessionId: string;
  searchQuery: string;
  agentId: string;
  model: string;
  workspacePath: string;
  runId: string;

  // Connection & Stream
  connectionState: "connected" | "connecting" | "reconnecting" | "unavailable";
  isStreaming: boolean;
  statusMessage: string;

  // Projections
  snapshot: RunSnapshotModel;
  events: EventEnvelope[];
  turns: ConversationTurn[];
  approvalState: ApprovalState;
  evidenceGrid: EvidenceGrid;
  pendingApproval?: PendingApproval;

  // UI state
  forensicDrawerOpen: boolean;
  activeForensicTab: ForensicTab;
  activeDiffText: string;
  composerText: string;
};

export class DesktopStore {
  public readonly state: Signal<DesktopStoreState>;
  private abortController: AbortController | null = null;

  constructor(initial: Partial<DesktopStoreState> = {}) {
    const initialSessionId = initial.activeSessionId ?? "session-default-1";
    const defaultSessions: SessionSummary[] = initial.sessions ?? [
      {
        sessionId: initialSessionId,
        title: "Initial Workspace Conversation",
        agentId: "coding-agent",
        workspacePath: ".",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        turnCount: 0,
      },
    ];

    this.state = createSignal<DesktopStoreState>({
      sessions: defaultSessions,
      activeSessionId: initialSessionId,
      searchQuery: "",
      agentId: initial.agentId ?? "coding-agent",
      model: initial.model ?? "openrouter/free",
      workspacePath: initial.workspacePath ?? ".",
      runId: initial.runId ?? "",
      connectionState: initial.connectionState ?? "connected",
      isStreaming: false,
      statusMessage: "Ready",
      snapshot: initial.snapshot ?? emptyRunSnapshot(),
      events: initial.events ?? [],
      turns: initial.turns ?? [],
      approvalState: initial.approvalState ?? emptyApprovalState(),
      evidenceGrid: initial.evidenceGrid ?? emptyEvidenceGrid(),
      pendingApproval: initial.pendingApproval,
      forensicDrawerOpen: false,
      activeForensicTab: "diffs",
      activeDiffText: "",
      composerText: "",
    });
  }

  public get(): DesktopStoreState {
    return this.state.get();
  }

  public update(fn: (prev: DesktopStoreState) => DesktopStoreState): void {
    this.state.set(fn);
  }

  public getGroupedSessions(): SessionGroup[] {
    const cur = this.get();
    const filtered = filterSessions(cur.sessions, cur.searchQuery);
    return groupSessionsByDate(filtered);
  }

  public newChat(): void {
    const newId = `session-${Date.now()}`;
    const newSession: SessionSummary = {
      sessionId: newId,
      title: "New Conversation",
      agentId: this.get().agentId,
      workspacePath: this.get().workspacePath,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      turnCount: 0,
    };

    this.update((prev) => ({
      ...prev,
      sessions: [newSession, ...prev.sessions],
      activeSessionId: newId,
      runId: "",
      events: [],
      turns: [],
      snapshot: emptyRunSnapshot(),
      approvalState: emptyApprovalState(),
      evidenceGrid: emptyEvidenceGrid(),
      pendingApproval: undefined,
      forensicDrawerOpen: false,
      composerText: "",
      statusMessage: "New chat started",
    }));
  }

  public selectSession(sessionId: string): void {
    this.update((prev) => ({
      ...prev,
      activeSessionId: sessionId,
      statusMessage: `Switched to session ${sessionId}`,
    }));
  }

  public ingestEnvelope(envelope: EventEnvelope): void {
    this.update((prev) => {
      const nextEvents = [...prev.events, envelope];
      const nextSnapshot = reduceRunSnapshot(prev.snapshot, envelope);
      const nextTurns = toConversationTurns(nextEvents);
      const nextApprovalState = reduceApprovalState(prev.approvalState, envelope);
      const nextEvidence = reduceEvidence(prev.evidenceGrid, envelope);

      let pendingApproval = nextSnapshot.pendingApproval;
      let activeDiffText = prev.activeDiffText;
      let forensicDrawerOpen = prev.forensicDrawerOpen;

      if (pendingApproval && pendingApproval.unifiedDiff) {
        activeDiffText = pendingApproval.unifiedDiff;
      }

      // Update active session summary
      const updatedSessions = prev.sessions.map((s) => {
        if (s.sessionId === prev.activeSessionId) {
          const firstGoal = nextTurns.find((t) => t.speaker === "user")?.text;
          return {
            ...s,
            title: firstGoal ? firstGoal.slice(0, 32) : s.title,
            updatedAt: new Date().toISOString(),
            turnCount: nextTurns.length,
          };
        }
        return s;
      });

      return {
        ...prev,
        events: nextEvents,
        snapshot: nextSnapshot,
        turns: nextTurns,
        approvalState: nextApprovalState,
        evidenceGrid: nextEvidence,
        pendingApproval,
        activeDiffText,
        sessions: updatedSessions,
        runId: envelope.runId ?? prev.runId,
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

  public async startRun(client: RuntimeClient, prompt: string): Promise<void> {
    const cur = this.get();
    this.update((prev) => ({
      ...prev,
      isStreaming: true,
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
        isStreaming: false,
        connectionState: "unavailable",
        statusMessage: `Start failed: ${res.error.message}`,
      }));
      return;
    }

    const runId = res.value.runId;
    this.update((prev) => ({
      ...prev,
      runId,
      connectionState: "connected",
      statusMessage: `Running agent in ${cur.workspacePath}...`,
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
            statusMessage: `Stream issue: ${item.error.message}`,
          }));
          continue;
        }
        this.ingestEnvelope(item.value.envelope);
      }
    } finally {
      this.update((prev) => ({ ...prev, isStreaming: false, statusMessage: "Idle" }));
    }
  }

  public async resolveApproval(client: RuntimeClient, decision: "approve" | "reject"): Promise<void> {
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
        statusMessage: `Approval resolved: ${decision}`,
      }));
    } else {
      this.update((prev) => ({
        ...prev,
        statusMessage: `Approval error: ${res.error.message}`,
      }));
    }
  }
}
