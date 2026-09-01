import type { ArtifactExplanation, Result } from "@aether/contracts";

export type FormattedExplanation = {
  status: string;
  prediction: string;
  empty: boolean;
};

export function formatExplanation(explanation: ArtifactExplanation): FormattedExplanation {
  const status = explanation.status ?? "unknown";
  const prediction = explanation.prediction ?? "";
  const activatedBy = explanation.activatedBy ?? [];
  const demotedBy = explanation.demotedBy ?? [];
  const empty = status === "unknown" && activatedBy.length === 0 && demotedBy.length === 0;

  return {
    status,
    prediction,
    empty,
  };
}

export function whyFromResult(
  result: Result<ArtifactExplanation>
): Result<FormattedExplanation & { explanation?: ArtifactExplanation }> {
  if (!result.ok) {
    return { ok: false, error: result.error };
  }
  const formatted = formatExplanation(result.value);
  return {
    ok: true,
    value: {
      ...formatted,
      explanation: result.value,
    },
  };
}
