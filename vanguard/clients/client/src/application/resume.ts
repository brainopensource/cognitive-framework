import { fail, type Result, type ResumeOptions } from "@aether/contracts";

/**
 * Ported from @vanguard/client-core's resume.ts (F4 Phase 5), adapted to
 * @aether/client's RuntimeClient.requestResume(runId, options) split-argument
 * convention -- client-core bundled {runId, checkpointId} into one object.
 */
export function buildResumeRequest(
  runId: string,
  checkpointId?: string
): Result<{ runId: string; options?: ResumeOptions }> {
  const trimmedRunId = runId?.trim();
  if (!trimmedRunId) {
    return fail("invalid_request", "runId cannot be empty", false);
  }
  const trimmedCheckpointId = checkpointId?.trim();
  const options: ResumeOptions | undefined = trimmedCheckpointId ? { checkpointId: trimmedCheckpointId } : undefined;
  return { ok: true, value: { runId: trimmedRunId, options } };
}

/** Only reads `.error` on failure, so this accepts the result of any RuntimeClient resume call. */
export function describeResumeFailure(result: Result<unknown>): string {
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
