import type { EventEnvelope, SemanticActivityItem, ActivityCategory, ActivityClaim } from "@aether/contracts";

export function classifyActivityEnvelope(env: EventEnvelope): SemanticActivityItem {
  const kind = String(env.payload.kind ?? "Unknown");
  const payload = env.payload;
  const timestamp = env.occurredAt || new Date().toISOString();
  const id = `act-${env.eventId}`;
  const seq = env.seq;
  const eventId = env.eventId;

  // 1. MESSAGES
  if (kind === "GoalDeclared" || kind === "UserPromptSubmitted") {
    const text = String(payload.goal ?? payload.prompt ?? payload.text ?? "User Prompt");
    return {
      id,
      category: "MESSAGE",
      title: "User Prompt",
      details: text,
      status: "completed",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  if (kind === "ObservationProduced" || kind === "ModelTurnProduced") {
    const text = String(payload.text ?? payload.content ?? payload.response ?? "");
    return {
      id,
      category: "MESSAGE",
      title: "Model Output",
      details: text,
      status: "completed",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 2. APPROVALS
  if (kind === "ApprovalRequested") {
    const action = String(payload.action ?? "Mutating Action");
    const diff = String(payload.unifiedDiff ?? payload.diff ?? payload.normalizedDiff ?? "");
    return {
      id,
      category: "APPROVAL",
      title: `Approval Required: ${action}`,
      approvalId: String(payload.approvalId ?? ""),
      details: `Action '${action}' requires signed Ed25519 authorization.`,
      diff: diff || undefined,
      status: "pending",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  if (kind === "ApprovalResolved") {
    const resolution = payload.resolution === "rejected" ? "rejected" : "approved";
    return {
      id,
      category: "APPROVAL",
      title: `Approval ${resolution.toUpperCase()}: ${String(payload.approvalId ?? "")}`,
      approvalId: String(payload.approvalId ?? ""),
      details: `Operator resolved challenge with decision: ${resolution}`,
      status: "completed",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 3. FILE READS
  if (
    kind === "FileRead" ||
    (kind === "OperatorInvoked" && String(payload.tool ?? "").match(/read|view|cat|fetch_file/i))
  ) {
    const path = String(payload.path ?? payload.filePath ?? payload.targetFile ?? payload.AbsolutePath ?? "file");
    return {
      id,
      category: "FILE_READ",
      title: `Read File: ${path}`,
      filePath: path,
      details: typeof payload.contentSummary === "string" ? payload.contentSummary : undefined,
      status: "completed",
      durationMs: typeof payload.durationMs === "number" ? payload.durationMs : undefined,
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 4. SEARCHES
  if (
    kind === "SearchExecuted" ||
    (kind === "OperatorInvoked" && String(payload.tool ?? "").match(/search|grep|find|glob/i))
  ) {
    const query = String(payload.query ?? payload.Query ?? payload.pattern ?? payload.Pattern ?? "");
    return {
      id,
      category: "SEARCH",
      title: query ? `Search: "${query}"` : "Search Codebase",
      searchQuery: query,
      details: typeof payload.matchSummary === "string" ? payload.matchSummary : undefined,
      status: "completed",
      durationMs: typeof payload.durationMs === "number" ? payload.durationMs : undefined,
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 5. COMMANDS
  if (
    kind === "CommandExecuted" ||
    (kind === "OperatorInvoked" && String(payload.tool ?? "").match(/command|exec|bash|run_command|sh/i))
  ) {
    const cmd = String(payload.command ?? payload.CommandLine ?? payload.cmd ?? "");
    return {
      id,
      category: "COMMAND",
      title: cmd ? `Run: ${cmd.slice(0, 48)}${cmd.length > 48 ? "…" : ""}` : "Run Command",
      command: cmd,
      details: typeof payload.output === "string" ? payload.output.slice(0, 300) : undefined,
      status: payload.exitCode === 0 || payload.status === "completed" ? "completed" : "running",
      durationMs: typeof payload.durationMs === "number" ? payload.durationMs : undefined,
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 6. PATCHES & DIFFS
  if (
    kind === "PatchApplied" ||
    (kind === "OperatorInvoked" && String(payload.tool ?? "").match(/patch|write|replace|edit/i))
  ) {
    const diff = String(payload.diff ?? payload.unifiedDiff ?? payload.ReplacementContent ?? "");
    const targetFile = String(payload.filePath ?? payload.TargetFile ?? payload.target ?? "");
    return {
      id,
      category: "PATCH",
      title: targetFile ? `Patch: ${targetFile}` : "Apply Patch",
      filePath: targetFile || undefined,
      diff: diff || undefined,
      status: "completed",
      durationMs: typeof payload.durationMs === "number" ? payload.durationMs : undefined,
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 7. VERIFICATION & CLAIMS
  if (
    kind === "ClaimVerified" ||
    kind === "VerificationExecuted" ||
    (kind === "OperatorInvoked" && String(payload.tool ?? "").match(/test|verify|check|assert/i))
  ) {
    const claims: ActivityClaim[] = [];
    if (Array.isArray(payload.claims)) {
      for (const c of payload.claims) {
        if (c && typeof c === "object") {
          claims.push({
            claimType: String(c.claimType ?? c.kind ?? "assert"),
            statement: String(c.statement ?? c.description ?? ""),
            pass: Boolean(c.pass ?? c.passed ?? true),
          });
        }
      }
    }
    return {
      id,
      category: "VERIFICATION",
      title: String(payload.title ?? payload.description ?? "Verification Check"),
      details: typeof payload.summary === "string" ? payload.summary : undefined,
      claims: claims.length > 0 ? claims : undefined,
      status: payload.failed ? "failed" : "completed",
      durationMs: typeof payload.durationMs === "number" ? payload.durationMs : undefined,
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 8. RESEARCH & CITATIONS
  if (
    kind === "ResearchSourceCited" ||
    kind === "CitationAdded" ||
    (kind === "OperatorInvoked" && String(payload.tool ?? "").match(/web|url|browse|read_url/i))
  ) {
    const url = String(payload.url ?? payload.Url ?? payload.uri ?? "");
    return {
      id,
      category: "RESEARCH",
      title: url ? `Research Source: ${url.slice(0, 40)}` : "Research Reference",
      citationUrl: url || undefined,
      details: typeof payload.summary === "string" ? payload.summary : undefined,
      status: "completed",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 9. ARTIFACTS
  if (kind === "ArtifactProduced" || kind === "ArtifactDeclared") {
    const digest = String(payload.digest ?? payload.artifactId ?? "");
    const path = String(payload.path ?? payload.targetFile ?? "");
    return {
      id,
      category: "ARTIFACT",
      title: path ? `Artifact: ${path}` : `Artifact: ${digest.slice(0, 16)}…`,
      artifactId: digest,
      filePath: path || undefined,
      details: typeof payload.summary === "string" ? payload.summary : undefined,
      status: "completed",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 10. WARNINGS
  if (kind === "WarningEmitted" || kind === "ModelWarning") {
    return {
      id,
      category: "WARNING",
      title: `Warning: ${String(payload.message ?? payload.code ?? "Runtime Warning")}`,
      details: String(payload.detail ?? payload.description ?? ""),
      status: "completed",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 11. ERRORS
  if (
    kind === "ExecutionFailed" ||
    kind === "EffectFailed" ||
    kind === "ErrorEmitted" ||
    kind === "AuthorizationDenied"
  ) {
    return {
      id,
      category: "ERROR",
      title: `Error: ${String(payload.message ?? payload.code ?? payload.error ?? "Execution Failure")}`,
      details: String(payload.detail ?? payload.reason ?? payload.stack ?? ""),
      status: "failed",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 12. COMPLETION
  if (kind === "RunCompleted" || kind === "EpisodeCompleted" || kind === "VerdictProduced") {
    const verdict = String(payload.verdict ?? payload.outcome ?? "satisfied");
    return {
      id,
      category: "COMPLETION",
      title: `Run Completed: Verdict ${verdict.toUpperCase()}`,
      details: typeof payload.summary === "string" ? payload.summary : `Final state verdict: ${verdict}`,
      status: verdict === "failed" || verdict === "0" ? "failed" : "completed",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // 13. GENERIC TOOL INVOCATION
  if (kind === "OperatorInvoked" || kind === "EffectStarted") {
    const tool = String(payload.tool ?? payload.action ?? payload.verb ?? "tool");
    return {
      id,
      category: "TOOL",
      title: `Execute Tool: ${tool}`,
      details: typeof payload.argsSummary === "string" ? payload.argsSummary : undefined,
      status: "running",
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  if (kind === "EffectCompleted") {
    return {
      id,
      category: "TOOL",
      title: `Effect Completed: ${String(payload.action ?? "operator")}`,
      status: "completed",
      durationMs: typeof payload.durationMs === "number" ? payload.durationMs : undefined,
      timestamp,
      seq,
      eventId,
      rawPayload: payload,
    };
  }

  // Fallback
  return {
    id,
    category: "TOOL",
    title: `Event: ${kind}`,
    details: typeof payload.message === "string" ? payload.message : undefined,
    status: "completed",
    timestamp,
    seq,
    eventId,
    rawPayload: payload,
  };
}

export function toSemanticActivities(envelopes: readonly EventEnvelope[]): SemanticActivityItem[] {
  const items: SemanticActivityItem[] = [];
  for (const env of envelopes) {
    const item = classifyActivityEnvelope(env);
    items.push(item);
  }
  return items;
}
