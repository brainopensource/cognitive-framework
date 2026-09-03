import { formatUsdFromMicros } from "./budget.js";
import type { CodingProjection } from "./coding-types.js";

const ESCAPE = /\u001b/;

/** Human receipt line from a backend projection. Never invents fields. */
export function formatHumanReceipt(projection: CodingProjection): string {
  switch (projection.kind) {
    case "plan": {
      const model = projection.model ?? "unknown";
      const total = projection.stepTotal;
      const suffix = typeof total === "number" ? `: ${total} validated steps` : "";
      return `[plan] ${model}${suffix}`;
    }
    case "step": {
      const index = projection.stepIndex ?? "?";
      const total = projection.stepTotal ?? "?";
      const title = projection.text ?? projection.stepId ?? "step";
      return `[step ${index}/${total}] ${title}`;
    }
    case "read":
      return `[read] ${projection.path ?? projection.text ?? "unknown"}`;
    case "write":
      return `[write] ${projection.path ?? "unknown"}${projection.text ? ` ${projection.text}` : ""}`;
    case "test": {
      const path = projection.path ?? "tests";
      const code = projection.exitCode ?? "?";
      const fails =
        typeof projection.failures === "number" ? `, ${projection.failures} failures` : "";
      return `[test] ${path} exit ${code}${fails}`;
    }
    case "verified":
      return `[verified] ${projection.stepId ?? projection.text ?? "step"}`;
    case "rotate":
      return `[rotate] ${projection.text ?? projection.detail ?? "provider rotate"}`;
    case "escalate":
      return `[escalate] ${projection.text ?? projection.fingerprint ?? "escalation"}`;
    case "diagnose":
      return `[diagnose] ${projection.model ?? projection.text ?? "unknown"}`;
    case "resume":
      return `[resume] ${projection.model ?? projection.text ?? "unknown"}`;
    case "oracle":
      return `[oracle] ${projection.text ?? `final acceptance exit ${projection.exitCode ?? "?"}`}`;
    case "complete": {
      const outcome = projection.outcome ?? "unknown";
      const turns = typeof projection.turns === "number" ? `, ${projection.turns} turns` : "";
      const cost = `, ${formatUsdFromMicros(projection.spentUsdMicros)}`;
      return `[complete] ${outcome}${turns}${cost}`;
    }
    case "budget":
      return `[budget] remaining ${formatUsdFromMicros(projection.remainingUsdMicros)}`;
    case "route": {
      const facts = projection.facts as Record<string, unknown> | undefined;
      if (facts) {
        const pairs = Object.entries(facts)
          .map(([key, value]) => `${key}=${JSON.stringify(value)}`)
          .join(" ");
        return `[doctor] ${pairs}`;
      }
      return `[route] ${projection.model ?? projection.text ?? "unknown"}`;
    }
    case "note":
      return `[assistant] ${projection.text ?? ""}`;
    case "error":
      return `[error] ${projection.detail ?? projection.text ?? "error"}`;
    default:
      return `[${String((projection as CodingProjection).kind)}] ${projection.text ?? ""}`.trimEnd();
  }
}

export function assertNoAnsi(line: string): void {
  if (ESCAPE.test(line)) {
    throw new Error("headless/json output must not contain ANSI escapes");
  }
}

export function renderProjectionLines(
  projections: ReadonlyArray<CodingProjection>,
  options: { human: boolean }
): string[] {
  const human = options.human;
  return projections.map((projection) => {
    const line = human ? formatHumanReceipt(projection) : JSON.stringify(projection);
    assertNoAnsi(line);
    return line;
  });
}
