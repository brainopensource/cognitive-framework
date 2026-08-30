import type {
  EventEnvelope,
  VerificationSummary,
  VerificationKind,
  VerificationStatus,
} from "@aether/contracts";

export function reduceVerificationSummaries(events: EventEnvelope[]): VerificationSummary[] {
  const list: VerificationSummary[] = [];

  for (const env of events) {
    const kind = String(env.payload.kind ?? "");
    const payload = env.payload;
    const timestamp = env.occurredAt || new Date().toISOString();
    const eventId = env.eventId;

    if (
      kind === "TestExecuted" ||
      kind === "TestsPassed" ||
      kind === "TestsFailed" ||
      kind === "VerificationPassed" ||
      kind === "VerificationFailed" ||
      kind === "LintExecuted" ||
      kind === "TypecheckExecuted" ||
      kind === "BuildExecuted"
    ) {
      let vKind: VerificationKind = "tests";
      if (kind.toLowerCase().includes("lint")) vKind = "lint";
      else if (kind.toLowerCase().includes("typecheck")) vKind = "typecheck";
      else if (kind.toLowerCase().includes("build")) vKind = "build";
      else if (typeof payload.checkType === "string") {
        const ct = payload.checkType.toLowerCase();
        if (ct === "lint" || ct === "typecheck" || ct === "build" || ct === "tests") {
          vKind = ct;
        } else {
          vKind = "custom";
        }
      }

      let status: VerificationStatus = "unavailable";
      if (
        kind === "TestsPassed" ||
        kind === "VerificationPassed" ||
        payload.status === "passed" ||
        payload.exitCode === 0 ||
        payload.passed === true
      ) {
        status = "pass";
      } else if (
        kind === "TestsFailed" ||
        kind === "VerificationFailed" ||
        payload.status === "failed" ||
        (typeof payload.exitCode === "number" && payload.exitCode !== 0) ||
        payload.passed === false
      ) {
        status = "fail";
      } else if (payload.status === "partial" || (payload.failedCount && Number(payload.failedCount) > 0 && Number(payload.passedCount) > 0)) {
        status = "partial";
      }

      const passedCount = typeof payload.passedCount === "number" ? payload.passedCount : typeof payload.passed === "number" ? payload.passed : undefined;
      const failedCount = typeof payload.failedCount === "number" ? payload.failedCount : typeof payload.failed === "number" ? payload.failed : undefined;
      const skippedCount = typeof payload.skippedCount === "number" ? payload.skippedCount : undefined;
      const durationMs = typeof payload.durationMs === "number" ? payload.durationMs : undefined;
      const command = typeof payload.command === "string" ? payload.command : undefined;
      const importantOutput = typeof payload.output === "string" ? payload.output : typeof payload.stdout === "string" ? payload.stdout : typeof payload.stderr === "string" ? payload.stderr : undefined;
      const relatedArtifacts = Array.isArray(payload.artifacts) ? payload.artifacts.map(String) : undefined;

      list.push({
        id: `ver-${eventId}`,
        kind: vKind,
        status,
        command,
        durationMs,
        passedCount,
        failedCount,
        skippedCount,
        importantOutput,
        relatedArtifacts,
        timestamp,
      });
    }
  }

  return list;
}
