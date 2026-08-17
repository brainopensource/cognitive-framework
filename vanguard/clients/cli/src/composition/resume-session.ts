import {
  buildResumeRequest,
  describeResumeFailure,
  type RuntimeClient,
} from "@vanguard/client-core";

export type ResumeOutcome =
  | { ok: true; runId: string }
  | { ok: false; code: string; message: string };

export async function performResume(
  client: Pick<RuntimeClient, "requestResume">,
  runId: string,
  checkpointId?: string
): Promise<ResumeOutcome> {
  const built = buildResumeRequest(runId, checkpointId);
  if (!built.ok) {
    return { ok: false, code: built.error.code, message: built.error.message };
  }
  const resumed = await client.requestResume(built.value);
  if (!resumed.ok) {
    return {
      ok: false,
      code: resumed.error.code,
      message: `${resumed.error.code}: ${describeResumeFailure(resumed)}`,
    };
  }
  return { ok: true, runId: resumed.value.runId };
}
