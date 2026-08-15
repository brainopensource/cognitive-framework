export type EventType =
  | "run.started"
  | "run.resumed"
  | "progress"
  | "token"
  | "effect.proposed"
  | "checkpoint.created"
  | "run.completed"
  | "run.cancelled";

export type RuntimeEvent = {
  seq: number;
  runId: string;
  at: string;
  type: EventType;
  message: string;
  data?: Record<string, unknown>;
};

export type RunRequest = {
  repo: string;
  prompt?: string;
  runId?: string;
  resumeFrom?: string;
  checkpointEvery?: number;
};

export type GovernanceExplanation = {
  artifact: string;
  status: "active" | "inactive" | "unknown";
  prediction: string;
  activatedBy: Array<{ evidence: string; strength: number }>;
  demotedBy: Array<{ condition: string; effect: string }>;
};

export interface RuntimePort {
  run(request: RunRequest): AsyncIterable<RuntimeEvent>;
  trace(runId: string): AsyncIterable<RuntimeEvent>;
  why(artifact: string): Promise<GovernanceExplanation>;
  cancel(runId: string): Promise<void>;
  resume(runId: string): AsyncIterable<RuntimeEvent>;
}

export const now = (): string => new Date().toISOString();

export function jsonLine(value: unknown): string {
  return JSON.stringify(value);
}
