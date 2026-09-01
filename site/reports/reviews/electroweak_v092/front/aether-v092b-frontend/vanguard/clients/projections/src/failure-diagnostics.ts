import type { ClientFailure, ServiceError } from "@aether/contracts";

export type FailureState =
  | "runtime_unavailable"
  | "transport_disconnected"
  | "protocol_incompatible"
  | "permission_denied"
  | "approval_rejected"
  | "budget_exhausted"
  | "invalid_agent_manifest"
  | "invalid_workflow_manifest"
  | "run_failed"
  | "artifact_unavailable"
  | "stream_interrupted"
  | "unknown_error";

export type FailureDiagnostics = {
  state: FailureState;
  title: string;
  cause: string;
  retryable: boolean;
  recoveryAction: string;
  rawError?: unknown;
};

export function diagnoseFailure(error: unknown): FailureDiagnostics {
  if (!error) {
    return {
      state: "unknown_error",
      title: "Unknown State",
      cause: "No error information provided.",
      retryable: false,
      recoveryAction: "Refresh application or inspect logs in Lab.",
    };
  }

  const errObj = error as Partial<ClientFailure & ServiceError & Error>;
  const code = String(errObj.code ?? "").toLowerCase();
  const message = String(errObj.message ?? error);
  const detail = String(errObj.detail ?? "");

  // 1. Runtime unavailable
  if (
    code === "not_available" ||
    message.includes("not reachable") ||
    message.includes("ECONNREFUSED") ||
    message.includes("socket not available")
  ) {
    return {
      state: "runtime_unavailable",
      title: "Runtime Service Unavailable",
      cause: message || "Could not connect to AETHER runtime socket or endpoint.",
      retryable: true,
      recoveryAction: "Ensure the AETHER daemon is running with 'vg daemon start' or check socket permissions.",
      rawError: error,
    };
  }

  // 2. Transport disconnected / stream interrupted
  if (
    code === "transport_interrupted" ||
    message.includes("stream interrupted") ||
    message.includes("connection closed") ||
    message.includes("socket hang up")
  ) {
    return {
      state: "transport_disconnected",
      title: "Transport Stream Interrupted",
      cause: message || "The real-time event stream was unexpectedly disconnected.",
      retryable: true,
      recoveryAction: "Reconnect will occur automatically, or click 'Reconnect Runtime'.",
      rawError: error,
    };
  }

  // 3. Protocol incompatible
  if (
    code === "incompatible_version" ||
    message.includes("protocol") ||
    message.includes("incompatible") ||
    message.includes("version mismatch")
  ) {
    return {
      state: "protocol_incompatible",
      title: "Protocol Version Incompatible",
      cause: message || "The frontend contract version is incompatible with the running runtime daemon.",
      retryable: false,
      recoveryAction: "Upgrade the frontend or runtime package to matching vg.4 specifications.",
      rawError: error,
    };
  }

  // 4. Permission denied / unauthenticated
  if (code === "permission_denied" || code === "unauthenticated" || message.includes("denied")) {
    return {
      state: "permission_denied",
      title: "Permission Denied",
      cause: message || "Operation authorization was denied by runtime governance policy.",
      retryable: false,
      recoveryAction: "Verify your Ed25519 signing key or request policy elevation.",
      rawError: error,
    };
  }

  // 5. Budget exhausted / rate limited
  if (
    code === "rate_limited" ||
    message.includes("budget") ||
    message.includes("exhausted") ||
    message.includes("tokens exceeded")
  ) {
    return {
      state: "budget_exhausted",
      title: "Execution Budget Exhausted",
      cause: message || "The agent run reached its configured token, step, or USD budget limit.",
      retryable: true,
      recoveryAction: "Resume run with a higher budget allocation or start a new focused session.",
      rawError: error,
    };
  }

  // 6. Invalid Agent Manifest
  if (message.includes("agent") && (message.includes("manifest") || message.includes("not found") || message.includes("invalid"))) {
    return {
      state: "invalid_agent_manifest",
      title: "Invalid Agent Manifest",
      cause: message || "The specified agent configuration could not be validated or found.",
      retryable: true,
      recoveryAction: "Select a valid agent from the catalog or verify agent manifest YAML.",
      rawError: error,
    };
  }

  // 7. Invalid Workflow Manifest
  if (message.includes("workflow") && (message.includes("manifest") || message.includes("not found") || message.includes("invalid"))) {
    return {
      state: "invalid_workflow_manifest",
      title: "Invalid Workflow Manifest",
      cause: message || "The specified workflow definition failed validation.",
      retryable: true,
      recoveryAction: "Select a valid workflow or check workflow stage configuration.",
      rawError: error,
    };
  }

  // 8. Artifact unavailable
  if (code === "not_found" && (message.includes("artifact") || message.includes("blob") || detail.includes("BlobStore"))) {
    return {
      state: "artifact_unavailable",
      title: "Artifact Content Unavailable",
      cause: message || "The requested artifact binary/text is not present in local blob store.",
      retryable: false,
      recoveryAction: "Inspect artifact explanation and activation evidence in Lab.",
      rawError: error,
    };
  }

  // 9. Run failed
  if (message.includes("run failed") || message.includes("unsatisfied") || message.includes("effect failed")) {
    return {
      state: "run_failed",
      title: "Agent Run Failed",
      cause: message || "The agent execution terminated with non-zero or unsatisfied verdict.",
      retryable: true,
      recoveryAction: "Inspect the failure trace in Lab or refine prompt instructions.",
      rawError: error,
    };
  }

  return {
    state: "unknown_error",
    title: "Application Error",
    cause: message,
    retryable: Boolean(errObj.retryable),
    recoveryAction: "Retry the action or inspect diagnostic details in Lab.",
    rawError: error,
  };
}
