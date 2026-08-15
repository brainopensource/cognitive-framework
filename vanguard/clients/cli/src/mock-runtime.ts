import { now, type GovernanceExplanation, type RunRequest, type RuntimeEvent, type RuntimePort } from "./runtime.js";

type StoredRun = { request: RunRequest; events: RuntimeEvent[]; cancelled: boolean };

/** Deterministic runtime double used until the real runtime port is available. */
export class MockRuntime implements RuntimePort {
  private readonly runs = new Map<string, StoredRun>();

  async *run(request: RunRequest): AsyncIterable<RuntimeEvent> {
    const runId = request.runId ?? `mock-${Date.now().toString(36)}`;
    const stored: StoredRun = { request: { ...request, runId }, events: [], cancelled: false };
    this.runs.set(runId, stored);
    yield* this.execute(stored, request.resumeFrom);
  }

  async *resume(runId: string): AsyncIterable<RuntimeEvent> {
    const existing = this.runs.get(runId) ?? { request: { repo: ".", runId }, events: [], cancelled: false };
    this.runs.set(runId, existing);
    existing.cancelled = false;
    yield* this.execute(existing, runId);
  }

  async *trace(runId: string): AsyncIterable<RuntimeEvent> {
    const existing = this.runs.get(runId);
    if (!existing) {
      yield* this.run({ repo: ".", runId });
      return;
    }
    for (const event of existing.events) yield event;
  }

  async cancel(runId: string): Promise<void> {
    const existing = this.runs.get(runId);
    if (existing) existing.cancelled = true;
  }

  async why(artifact: string): Promise<GovernanceExplanation> {
    const known = ["default-harness", "typed-tools", "mock-agent"].includes(artifact);
    return {
      artifact,
      status: known ? "active" : "unknown",
      prediction: known ? "Improves observable, typed repository work under bounded authority." : "No activation pointer is present in the mock registry.",
      activatedBy: known ? [{ evidence: "mock-evidence: deterministic smoke baseline", strength: 0.82 }] : [],
      demotedBy: [
        { condition: "evaluation confidence falls below 0.60", effect: "remove activation pointer" },
        { condition: "integrity or provenance check fails", effect: "mark inactive pending review" }
      ]
    };
  }

  private async *execute(stored: StoredRun, resumedFrom?: string): AsyncIterable<RuntimeEvent> {
    const request = stored.request;
    const emit = (type: RuntimeEvent["type"], message: string, data?: Record<string, unknown>): RuntimeEvent => {
      const event = { seq: stored.events.length + 1, runId: request.runId!, at: now(), type, message, data };
      stored.events.push(event);
      return event;
    };
    const steps = ["compile context", "inspect repository", "propose typed change", "evaluate result"];
    yield emit(resumedFrom ? "run.resumed" : "run.started", resumedFrom ? `Resumed from checkpoint ${resumedFrom}` : `Starting episode against ${request.repo}`, { repo: request.repo, resumedFrom });
    for (let index = 0; index < steps.length; index += 1) {
      await new Promise((resolve) => setTimeout(resolve, 25));
      if (stored.cancelled) {
        yield emit("run.cancelled", "Run cancelled; latest checkpoint is resumable");
        return;
      }
      yield emit("progress", `${steps[index]} (${index + 1}/${steps.length})`, { step: index + 1, total: steps.length });
      yield emit("token", `mock output for ${steps[index]}`, { tokenIndex: index });
      if ((index + 1) % (request.checkpointEvery ?? 2) === 0) {
        yield emit("checkpoint.created", `Checkpoint saved after step ${index + 1}`, { checkpoint: `${request.runId!}:cp-${index + 1}` });
      }
    }
    yield emit("effect.proposed", "Proposed effect is awaiting runtime authorization", { sinkClass: "privileged", requiresApproval: true });
    yield emit("run.completed", "Episode complete (mock runtime)", { outcome: "satisfied" });
  }
}
