import { whyFromResult, type ArtifactExplanation, type Result } from "@vanguard/client-core";

export function whyText(result: Result<ArtifactExplanation>): string {
  const mapped = whyFromResult(result);
  if (!mapped.ok) return mapped.error.code;
  const { status, prediction } = mapped.value;
  return prediction ? `${status}: ${prediction}` : status;
}
