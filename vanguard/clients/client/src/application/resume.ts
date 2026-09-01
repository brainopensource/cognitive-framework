import { fail, type Result, type ResumeOptions, type RunRef } from "@aether/contracts";

/**
 * Ported from @vanguard/client-core's resume.ts (F4 Phase 3), adapted to
 * @aether/client's RuntimeClient.requestResume(runId, options) split-argument
 * convention -- client-core bundled {runId, checkpointId} into one object,
 * which is why this module is ported but NOT shimmed onto client-core: its
 * one real consumer (cli/src/composition/resume-session.ts) still calls
 * `client.requestResume(builtRequest)` with the bundled shape client-core's
 * RuntimeClient expects. Shimming happens alongside that call site's
 * migration in a later phase.
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
