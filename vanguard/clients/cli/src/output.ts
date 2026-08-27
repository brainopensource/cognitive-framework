/** Structured CLI output per Masterplan §8.3 */

export const EXIT_CODES = {
  SUCCESS: 0,
  INPUT_ERROR: 2,
  AUTH_REJECTED: 3,
  CONFLICT: 4,
  BACKEND_UNAVAILABLE: 5,
  TASK_FAILED: 6,
  EVIDENCE_FAILURE: 7,
} as const;

export type CliJsonOutput<T> = {
  schemaVersion: "aether.cli/1";
  status: "success" | "error";
  correlationId: string;
  data?: T;
  error?: { code: string; message: string; retryable: boolean };
};

export function jsonOutput<T>(data: T, correlationId: string = crypto.randomUUID()): CliJsonOutput<T> {
  return {
    schemaVersion: "aether.cli/1",
    status: "success",
    correlationId,
    data,
  };
}

export function jsonError(code: string, message: string, retryable: boolean = false, correlationId: string = crypto.randomUUID()): CliJsonOutput<never> {
  return {
    schemaVersion: "aether.cli/1",
    status: "error",
    correlationId,
    error: { code, message, retryable },
  };
}

export function writeJson<T>(output: CliJsonOutput<T>): void {
  console.log(JSON.stringify(output, null, 2));
}

export function exitCodeForFailure(code: string): number {
  if (code === "NOT_FOUND" || code === "VALIDATION_FAILED" || code === "INPUT_ERROR") return EXIT_CODES.INPUT_ERROR;
  if (code === "AUTH_REJECTED") return EXIT_CODES.AUTH_REJECTED;
  if (code === "CONFLICT") return EXIT_CODES.CONFLICT;
  if (code === "BACKEND_UNAVAILABLE" || code === "UNAVAILABLE") return EXIT_CODES.BACKEND_UNAVAILABLE;
  if (code === "TASK_FAILED") return EXIT_CODES.TASK_FAILED;
  if (code === "EVIDENCE_FAILURE") return EXIT_CODES.EVIDENCE_FAILURE;
  return 1;
}
