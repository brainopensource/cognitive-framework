import { whyFromResult } from "@vanguard/client-core";
import type { ArtifactExplanation, Result } from "@aether/contracts";

export function whyText(result: Result<ArtifactExplanation>): string {
  const mapped = whyFromResult(result);
  if (!mapped.ok) return mapped.error.code;
  const { status, prediction } = mapped.value;
  return prediction ? `${status}: ${prediction}` : status;
}
