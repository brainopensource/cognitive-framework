import { fail } from "../contract/parse.js";
import type { CorrectionRecord, Result, RuntimeClient } from "../contract/types.js";

const REASONS = {
  d: "functional_defect",
  s: "style",
  t: "test_inadequacy",
  e: "security_policy",
  a: "architecture_preference",
} as const;

export type CorrectionReason = (typeof REASONS)[keyof typeof REASONS];

export function correctionReasonForKey(key: string): CorrectionReason | undefined {
  if (key === "S") return "security_policy";
  return REASONS[key as keyof typeof REASONS];
}

export async function captureCorrection(
  client: Pick<RuntimeClient, "recordCorrection">,
  draft: { episodeId: string; proposedPatchDigest: string; acceptedPatchDigest: string; key: string },
): Promise<Result<CorrectionRecord>> {
  const reason = correctionReasonForKey(draft.key);
  if (!reason) return fail("invalid_request", `unknown correction key ${draft.key}`);
  const record: CorrectionRecord = {
    episodeId: draft.episodeId,
    proposedPatchDigest: draft.proposedPatchDigest,
    acceptedPatchDigest: draft.acceptedPatchDigest,
    reasonCodes: [reason],
    magnitude: "minor",
    scope: "repo",
    correctingPrincipalRole: "user",
  };
  const saved = await client.recordCorrection(record);
  if (!saved.ok) return saved;
  return { ok: true, value: record };
}
