/** Frozen coding-request and projection contracts for the product CLI (S33). */

export type CodingExitCode = 0 | 1 | 2 | 3 | 4;

export type CodingRequest = {
  command: "code" | "explain" | "resume" | "doctor";
  workspace: string;
  brief?: string;
  question?: string;
  runId?: string;
  resumeFrom?: string;
  plannerModel: string;
  executorBand: string;
  executorModels: string[];
  recoveryModels: string[];
  reviewerModel: string | null;
  maxTurnsPerEpisode: number;
  maxEpisodes: number;
  maxReplans: number;
  maxPaidCalls: number;
  budgetUsdMicros: number;
  interactive: boolean;
  dryPlan: boolean;
  jsonlOut?: string;
  json: boolean;
  headless: boolean;
  /** Test-only: ask Python for the scripted fake coordinator. Never a live spend path. */
  fakeBackend?: "greenfield-adaptive" | "budget-exhausted" | "unavailable" | "non-green";
};

/** Machine projection tokens the CLI may render — never invent values. */
export type CodingProjectionKind =
  | "plan"
  | "step"
  | "read"
  | "write"
  | "test"
  | "verified"
  | "rotate"
  | "escalate"
  | "diagnose"
  | "resume"
  | "oracle"
  | "complete"
  | "budget"
  | "route"
  | "error";

export type CodingProjection = {
  kind: CodingProjectionKind;
  text?: string;
  model?: string;
  stepId?: string;
  stepIndex?: number;
  stepTotal?: number;
  path?: string;
  exitCode?: number;
  failures?: number;
  fingerprint?: string;
  outcome?: string;
  turns?: number;
  spentUsdMicros?: number | null;
  remainingUsdMicros?: number | null;
  detail?: string;
  [key: string]: unknown;
};

export type CodingTerminalResult = {
  runId: string;
  outcome: string;
  phase: string;
  attempts: number;
  turns: number;
  planDigest: string | null;
  activeStepId: string | null;
  verifiedStepIds: string[];
  modelRoutes: ReadonlyArray<Record<string, unknown>>;
  promptTokens: number | null;
  completionTokens: number | null;
  spentUsdMicros: number | null;
  detail: string;
  projections: CodingProjection[];
};

export function exitCodeForOutcome(outcome: string): CodingExitCode {
  if (outcome === "oracle_green" || outcome === "completed") return 0;
  if (outcome === "budget_exhausted") return 4;
  if (
    outcome === "instrument_error" ||
    outcome.startsWith("instrument_error:") ||
    outcome === "provider_unavailable" ||
    outcome === "unavailable"
  ) {
    return 3;
  }
  if (outcome === "invalid_request" || outcome === "invalid_plan_or_route") return 2;
  return 1;
}
