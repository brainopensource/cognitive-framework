import type { CanonicalErrorCode, ErrorCode } from "@aether/contracts";

export const CLI_EXIT_CODES = {
  SUCCESS: 0,
  EXECUTION_FAILED: 1,
  INVALID_INPUT: 2,
  APPROVAL_REQUIRED: 3,
  PERMISSION_DENIED: 4,
  RESOURCE_EXHAUSTED: 5,
  DAEMON_UNAVAILABLE: 6,
  EVIDENCE_FAILURE: 7,
  INTERRUPTED: 130,
} as const;

export const EXIT_CODES = {
  ...CLI_EXIT_CODES,
  INPUT_ERROR: 2,
  AUTH_REJECTED: 4,
  CONFLICT: 1,
  BACKEND_UNAVAILABLE: 6,
  TASK_FAILED: 1,
} as const;

export type CliOutcomeJson<T = Record<string, unknown>> = {
  api: "aether.cli-outcome/1";
  command: string;
  runId?: string;
  status: "satisfied" | "failed" | "cancelled" | "awaiting_approval" | "success" | "error" | "running" | "pending";
  verdict?: string;
  metrics?: {
    totalTokens?: number;
    inTokens?: number;
    outTokens?: number;
    costMicros?: string;
    durationMs?: number;
    turns?: number;
    [key: string]: unknown;
  };
  artifacts?: Array<{
    digest: string;
    kind: string;
    path?: string;
  }>;
  data?: T;
  error?: {
    code: string;
    message: string;
    retryable: boolean;
    detail?: string;
  };
};

export function exitCodeForErrorCode(code: string | undefined): number {
  if (!code) return CLI_EXIT_CODES.SUCCESS;
  if (
    code === "invalid_request" ||
    code === "not_found" ||
    code === "incompatible_version" ||
    code === "frame_too_large" ||
    code === "VALIDATION_FAILED" ||
    code === "INPUT_ERROR"
  ) {
    return CLI_EXIT_CODES.INVALID_INPUT; // 2
  }
  if (code === "unauthenticated" || code === "permission_denied" || code === "AUTH_REJECTED") {
    return CLI_EXIT_CODES.PERMISSION_DENIED; // 4
  }
  if (code === "rate_limited") {
    return CLI_EXIT_CODES.RESOURCE_EXHAUSTED; // 5
  }
  if (code === "not_available" || code === "BACKEND_UNAVAILABLE" || code === "UNAVAILABLE") {
    return CLI_EXIT_CODES.DAEMON_UNAVAILABLE; // 6
  }
  if (code === "conflict" || code === "internal" || code === "TASK_FAILED") {
    return CLI_EXIT_CODES.EXECUTION_FAILED; // 1
  }
  if (code === "EVIDENCE_FAILURE") {
    return CLI_EXIT_CODES.EVIDENCE_FAILURE; // 7
  }
  return CLI_EXIT_CODES.EXECUTION_FAILED;
}

export function writeJsonOutcome(outcome: CliOutcomeJson): void {
  console.log(JSON.stringify(outcome, null, 2));
}

export function writeNdjsonFrame(frame: unknown): void {
  console.log(JSON.stringify(frame));
}

export function logDiagnostic(message: string): void {
  console.error(message);
}

export function jsonOutput<T>(data: T, correlationId: string = crypto.randomUUID()) {
  return {
    schemaVersion: "aether.cli/1",
    status: "success",
    correlationId,
    data,
  };
}

export function jsonError(code: string, message: string, retryable: boolean = false, correlationId: string = crypto.randomUUID()) {
  return {
    schemaVersion: "aether.cli/1",
    status: "error",
    correlationId,
    error: { code, message, retryable },
  };
}

export function writeJson<T>(output: T): void {
  console.log(JSON.stringify(output, null, 2));
}

export function exitCodeForFailure(code: string): number {
  return exitCodeForErrorCode(code);
}
