// AUTO-GENERATED: AETHER frontend SDK expansion (Phase F0)

import { randomUUID } from "node:crypto";

export type CommandEnvelope<T> = Readonly<{
  schemaVersion: "aether.command/1";
  commandId: string;
  idempotencyKey: string;
  commandType: string;
  requestedAt: string;
  actor: Readonly<{ principalId: string; sessionId: string }>;
  target: Readonly<{ projectId?: string; runId?: string; lineageId?: string }>;
  expectedVersion?: string;
  capabilityReference?: string;
  payload: T;
}>;

export function createCommandEnvelope<T>(
  commandType: string,
  actor: Readonly<{ principalId: string; sessionId: string }>,
  target: Readonly<{ projectId?: string; runId?: string; lineageId?: string }>,
  payload: T,
  options?: {
    idempotencyKey?: string;
    expectedVersion?: string;
    capabilityReference?: string;
  }
): CommandEnvelope<T> {
  const commandId = randomUUID();
  return {
    schemaVersion: "aether.command/1",
    commandId,
    idempotencyKey: options?.idempotencyKey ?? commandId,
    commandType,
    requestedAt: new Date().toISOString(),
    actor,
    target,
    expectedVersion: options?.expectedVersion,
    capabilityReference: options?.capabilityReference,
    payload,
  };
}

export type RemediationAction =
  | { type: "retry"; afterMs?: number }
  | { type: "sync"; newVersion: string }
  | { type: "reauthenticate" }
  | { type: "abort" };

export type AetherProblem = Readonly<{
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  remediation?: RemediationAction;
}>;

export type CommandResult<T = unknown> =
  | { status: "accepted"; commandId: string; data?: T }
  | { status: "rejected"; commandId: string; problem: AetherProblem }
  | { status: "conflict"; commandId: string; problem: AetherProblem; currentVersion: string };

export function isAccepted<T>(result: CommandResult<T>): result is Extract<CommandResult<T>, { status: "accepted" }> {
  return result.status === "accepted";
}

export function isRejected<T>(result: CommandResult<T>): result is Extract<CommandResult<T>, { status: "rejected" }> {
  return result.status === "rejected";
}

export function isConflict<T>(result: CommandResult<T>): result is Extract<CommandResult<T>, { status: "conflict" }> {
  return result.status === "conflict";
}
