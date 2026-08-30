import { createSignal, type Signal } from "./signals.js";

export type WorkbenchId = "runs" | "events" | "trace" | "artifacts" | "context" | "system";

export type InspectorTab = "payload" | "approval" | "artifact" | "node" | "context" | "raw";

export type SelectionState = {
  activeWorkbench: WorkbenchId;
  selectedRunId: string;
  selectedEventId: string | null;
  selectedSeq: string | null;
  selectedTraceNodeId: string | null;
  selectedArtifactId: string | null;
  selectedApprovalId: string | null;
  selectedContextLayer: string | null;
  inspectorOpen: boolean;
  activeInspectorTab: InspectorTab;
};

export class SelectionModel {
  public readonly state: Signal<SelectionState>;

  constructor(initial: Partial<SelectionState> = {}) {
    this.state = createSignal<SelectionState>({
      activeWorkbench: initial.activeWorkbench ?? "runs",
      selectedRunId: initial.selectedRunId ?? "",
      selectedEventId: initial.selectedEventId ?? null,
      selectedSeq: initial.selectedSeq ?? null,
      selectedTraceNodeId: initial.selectedTraceNodeId ?? null,
      selectedArtifactId: initial.selectedArtifactId ?? null,
      selectedApprovalId: initial.selectedApprovalId ?? null,
      selectedContextLayer: initial.selectedContextLayer ?? null,
      inspectorOpen: initial.inspectorOpen ?? false,
      activeInspectorTab: initial.activeInspectorTab ?? "payload",
    });
  }

  public get(): SelectionState {
    return this.state.get();
  }

  public update(fn: (prev: SelectionState) => SelectionState): void {
    this.state.set(fn);
  }

  public setWorkbench(wb: WorkbenchId): void {
    this.update((prev) => ({
      ...prev,
      activeWorkbench: wb,
    }));
  }

  public selectRun(runId: string): void {
    this.update((prev) => ({
      ...prev,
      selectedRunId: runId,
      selectedEventId: null,
      selectedSeq: null,
      selectedTraceNodeId: null,
      selectedArtifactId: null,
      selectedApprovalId: null,
      selectedContextLayer: null,
    }));
  }

  public selectEvent(eventId: string | null, seq?: string | null): void {
    this.update((prev) => ({
      ...prev,
      selectedEventId: eventId,
      selectedSeq: seq !== undefined ? seq : prev.selectedSeq,
      selectedTraceNodeId: eventId, // synchronize with trace node
      inspectorOpen: eventId !== null ? true : prev.inspectorOpen,
      activeInspectorTab: "payload",
    }));
  }

  public selectTraceNode(nodeId: string | null, seq?: string | null): void {
    this.update((prev) => ({
      ...prev,
      selectedTraceNodeId: nodeId,
      selectedEventId: nodeId,
      selectedSeq: seq !== undefined ? seq : prev.selectedSeq,
      inspectorOpen: nodeId !== null ? true : prev.inspectorOpen,
      activeInspectorTab: "node",
    }));
  }

  public selectArtifact(artifactId: string | null): void {
    this.update((prev) => ({
      ...prev,
      selectedArtifactId: artifactId,
      inspectorOpen: artifactId !== null ? true : prev.inspectorOpen,
      activeInspectorTab: "artifact",
    }));
  }

  public selectApproval(approvalId: string | null): void {
    this.update((prev) => ({
      ...prev,
      selectedApprovalId: approvalId,
      inspectorOpen: approvalId !== null ? true : prev.inspectorOpen,
      activeInspectorTab: "approval",
    }));
  }

  public selectContextLayer(layer: string | null): void {
    this.update((prev) => ({
      ...prev,
      selectedContextLayer: layer,
      inspectorOpen: layer !== null ? true : prev.inspectorOpen,
      activeInspectorTab: "context",
    }));
  }

  public setInspectorTab(tab: InspectorTab): void {
    this.update((prev) => ({
      ...prev,
      activeInspectorTab: tab,
      inspectorOpen: true,
    }));
  }

  public toggleInspector(open?: boolean): void {
    this.update((prev) => ({
      ...prev,
      inspectorOpen: open !== undefined ? open : !prev.inspectorOpen,
    }));
  }

  public toHashString(): string {
    const cur = this.get();
    const params = new URLSearchParams();
    if (cur.selectedRunId) params.set("runId", cur.selectedRunId);
    if (cur.selectedEventId) params.set("eventId", cur.selectedEventId);
    if (cur.selectedSeq) params.set("seq", cur.selectedSeq);
    if (cur.selectedArtifactId) params.set("artifactId", cur.selectedArtifactId);
    if (cur.selectedApprovalId) params.set("approvalId", cur.selectedApprovalId);
    const paramStr = params.toString();
    return `#${cur.activeWorkbench}${paramStr ? `?${paramStr}` : ""}`;
  }

  public fromHashString(hash: string): void {
    if (!hash || hash === "#") return;
    const clean = hash.startsWith("#") ? hash.slice(1) : hash;
    const [path, queryString] = clean.split("?");
    const validWb: WorkbenchId[] = ["runs", "events", "trace", "artifacts", "context", "system"];
    const activeWorkbench = validWb.includes(path as WorkbenchId) ? (path as WorkbenchId) : "runs";

    const params = new URLSearchParams(queryString || "");
    const selectedRunId = params.get("runId") || "";
    const selectedEventId = params.get("eventId") || null;
    const selectedSeq = params.get("seq") || null;
    const selectedArtifactId = params.get("artifactId") || null;
    const selectedApprovalId = params.get("approvalId") || null;

    this.update((prev) => ({
      ...prev,
      activeWorkbench,
      selectedRunId: selectedRunId || prev.selectedRunId,
      selectedEventId: selectedEventId || prev.selectedEventId,
      selectedSeq: selectedSeq || prev.selectedSeq,
      selectedArtifactId: selectedArtifactId || prev.selectedArtifactId,
      selectedApprovalId: selectedApprovalId || prev.selectedApprovalId,
    }));
  }
}
