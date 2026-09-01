import type { Result, ResumeRunRequest, RunRef } from "../contract/types.js";
import { fail } from "../contract/parse.js";

export function buildResumeRequest(
  runId: string,
  checkpointId?: string
): Result<ResumeRunRequest> {
  const trimmedRunId = runId?.trim();
  if (!trimmedRunId) {
    return fail("invalid_request", "runId cannot be empty", false);
  }
  const req: ResumeRunRequest = { runId: trimmedRunId };
  const trimmedCheckpointId = checkpointId?.trim();
  if (trimmedCheckpointId) {
    req.checkpointId = trimmedCheckpointId;
  }
  return { ok: true, value: req };
}

export function describeResumeFailure(result: Result<RunRef>): string {
  if (result.ok) return "";
  const { code, message } = result.error;
  switch (code) {
    case "not_available":
      return "Runtime daemon is unreachable on unix socket";
    case "not_found":
      return "Run or checkpoint not found";
    case "permission_denied":
      return "Permission denied";
    default:
      return message || `Resume failed (${code})`;
  }
}
