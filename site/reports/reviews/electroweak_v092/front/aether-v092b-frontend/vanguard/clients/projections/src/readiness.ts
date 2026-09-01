import type {
  StartupReadiness,
  ReadinessStep,
  ReadinessStepId,
  ModelProviderConfig,
  DaemonStatus,
} from "@aether/contracts";

export function evaluateStartupReadiness(params: {
  runtimeConnected: boolean;
  daemonStatus: DaemonStatus | null;
  providers: ModelProviderConfig[];
  activeWorkspace: string;
  activeAgentOrWorkflowId: string;
}): StartupReadiness {
  const steps: ReadinessStep[] = [];
  let nextRequired: ReadinessStepId | undefined = undefined;

  // 1. Runtime Step
  const runtimeReady = params.runtimeConnected && params.daemonStatus?.status !== "unresponsive";
  steps.push({
    id: "runtime",
    title: "Runtime Daemon Connection",
    status: runtimeReady ? "ready" : "unreachable",
    description: runtimeReady
      ? `Connected to runtime socket (${params.daemonStatus?.socketPath ?? "active"})`
      : "AETHER background daemon is not reachable or stopped.",
    actionLabel: runtimeReady ? undefined : "Connect Runtime",
    routeTarget: "settings-runtime",
  });
  if (!runtimeReady && !nextRequired) nextRequired = "runtime";

  // 2. Provider Step
  const defaultProvider = params.providers.find((p) => p.isDefault && p.enabled) ?? params.providers.find((p) => p.enabled);
  const providerReady = !!defaultProvider && !!defaultProvider.selectedModel;
  steps.push({
    id: "provider",
    title: "Model Provider & Model Selection",
    status: providerReady ? "ready" : "pending",
    description: providerReady
      ? `Active provider '${defaultProvider.name}' with model '${defaultProvider.selectedModel}'`
      : "No active model provider configured or selected.",
    actionLabel: providerReady ? undefined : "Configure Provider",
    routeTarget: "settings-providers",
  });
  if (runtimeReady && !providerReady && !nextRequired) nextRequired = "provider";

  // 3. Credential Step
  const credentialReady = !!defaultProvider && (defaultProvider.credentialState === "CONFIGURED" || defaultProvider.type === "ollama");
  steps.push({
    id: "credential",
    title: "API Credentials & Signing Key",
    status: credentialReady ? "ready" : defaultProvider?.credentialState === "INVALID" ? "invalid" : "pending",
    description: credentialReady
      ? "Provider credentials verified in secure store."
      : "API Key or Operator Signing Key is required for execution.",
    actionLabel: credentialReady ? undefined : "Add API Key",
    routeTarget: "settings-credentials",
  });
  if (runtimeReady && providerReady && !credentialReady && !nextRequired) nextRequired = "credential";

  // 4. Workspace Step
  const workspaceReady = !!params.activeWorkspace && params.activeWorkspace.trim().length > 0;
  steps.push({
    id: "workspace",
    title: "Target Workspace Directory",
    status: workspaceReady ? "ready" : "pending",
    description: workspaceReady
      ? `Target directory: ${params.activeWorkspace}`
      : "Select target repository or project workspace.",
    actionLabel: workspaceReady ? undefined : "Select Directory",
    routeTarget: "workspace-select",
  });
  if (runtimeReady && providerReady && credentialReady && !workspaceReady && !nextRequired) nextRequired = "workspace";

  // 5. Composition Step
  const compositionReady = !!params.activeAgentOrWorkflowId && params.activeAgentOrWorkflowId.trim().length > 0;
  steps.push({
    id: "composition",
    title: "Agent / Workflow Selection",
    status: compositionReady ? "ready" : "pending",
    description: compositionReady
      ? `Selected composition: ${params.activeAgentOrWorkflowId}`
      : "Choose an agent (Coding, Research, Audit) or multi-agent workflow.",
    actionLabel: compositionReady ? undefined : "Select Agent",
    routeTarget: "agent-select",
  });
  if (runtimeReady && providerReady && credentialReady && workspaceReady && !compositionReady && !nextRequired) {
    nextRequired = "composition";
  }

  const isReady = runtimeReady && providerReady && credentialReady && workspaceReady && compositionReady;

  return {
    isReady,
    steps,
    nextRequiredStep: nextRequired,
  };
}
