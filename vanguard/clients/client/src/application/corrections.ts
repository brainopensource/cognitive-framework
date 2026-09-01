import { fail, type CorrectionRecord, type Result } from "@aether/contracts";
import type { RuntimeClient } from "../client.js";

/**
 * Correction recording, migrated onto the canonical vg.4 `CorrectionRecord`
 * shape (`correctionId`/`runId`/`reasonCode`/`scope: "local"|"general"`/
 * `recordedAt`/`author`) per the F4 corrections.ts decision: this shape is
 * the wire standard going forward, not client-core's prior flat
 * (`episodeId`/`proposedPatchDigest`/`acceptedPatchDigest`/`reasonCodes`/
 * `magnitude`/`correctingPrincipalRole`) shape.
 *
 * `LegacyCorrectionFields` keeps those prior fields available -- optional,
 * additive -- on the record this module produces, so older telemetry
 * readers or fixtures built against client-core's shape keep working.
 */

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

export type LegacyCorrectionFields = {
  /** @deprecated superseded by `runId`; kept for back-compat readers. */
  proposedPatchDigest?: string;
  /** @deprecated superseded by `runId`; kept for back-compat readers. */
  acceptedPatchDigest?: string;
};

export type CorrectionRecordWithLegacy = CorrectionRecord & LegacyCorrectionFields;

function newCorrectionId(): string {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `correction-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export async function captureCorrection(
  client: Pick<RuntimeClient, "recordCorrection">,
  draft: {
    runId: string;
    episodeId?: string;
    proposedPatchDigest?: string;
    acceptedPatchDigest?: string;
    key: string;
    author?: string;
  },
): Promise<Result<CorrectionRecordWithLegacy>> {
  const reason = correctionReasonForKey(draft.key);
  if (!reason) return fail("invalid_request", `unknown correction key ${draft.key}`);

  const record: CorrectionRecordWithLegacy = {
    correctionId: newCorrectionId(),
    runId: draft.runId,
    episodeId: draft.episodeId,
    reasonCode: reason,
    // Client-core's captureCorrection always scoped to "repo" (the
    // narrowest unit), never letting an interactive TUI correction get
    // promoted straight to general competence -- "local" is the canonical
    // equivalent of that invariant, not "general".
    scope: "local",
    recordedAt: new Date().toISOString(),
    author: draft.author ?? "operator",
    proposedPatchDigest: draft.proposedPatchDigest,
    acceptedPatchDigest: draft.acceptedPatchDigest,
  };

  const saved = await client.recordCorrection({ correction: record });
  if (!saved.ok) return saved;
  return { ok: true, value: record };
}
