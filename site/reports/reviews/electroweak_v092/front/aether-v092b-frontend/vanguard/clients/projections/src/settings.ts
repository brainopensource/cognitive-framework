import type { FrontendSettings } from "@aether/contracts";

export const DEFAULT_FRONTEND_SETTINGS: FrontendSettings = {
  general: {
    defaultRuntime: "/tmp/vanguard-runtime.sock",
    defaultWorkspace: ".",
    defaultAgent: "coding-agent",
    defaultWorkflow: "default-turn-loop",
    autoFollowStreaming: true,
  },
  runtime: {
    socketPath: "/tmp/vanguard-runtime.sock",
    httpUrl: "http://127.0.0.1:8000",
    reconnectIntervalMs: 2000,
    maxReconnectAttempts: 10,
    requestTimeoutMs: 10000,
  },
  appearance: {
    theme: "dark",
    density: "comfortable",
    reducedMotion: false,
  },
  workspace: {
    recentWorkspaces: ["."],
    maxRecentWorkspaces: 8,
  },
  terminal: {
    tuiAnimation: true,
    tuiColorMode: "truecolor",
  },
  accessibility: {
    highContrast: false,
    screenReaderOptimized: false,
    fontSize: 14,
  },
};

export function mergeSettings(
  base: FrontendSettings,
  overrides?: Partial<{
    general: Partial<FrontendSettings["general"]>;
    runtime: Partial<FrontendSettings["runtime"]>;
    appearance: Partial<FrontendSettings["appearance"]>;
    workspace: Partial<FrontendSettings["workspace"]>;
    terminal: Partial<FrontendSettings["terminal"]>;
    accessibility: Partial<FrontendSettings["accessibility"]>;
  }>
): FrontendSettings {
  if (!overrides) return base;

  return {
    general: { ...base.general, ...(overrides.general ?? {}) },
    runtime: { ...base.runtime, ...(overrides.runtime ?? {}) },
    appearance: { ...base.appearance, ...(overrides.appearance ?? {}) },
    workspace: {
      recentWorkspaces: overrides.workspace?.recentWorkspaces ?? base.workspace.recentWorkspaces,
      maxRecentWorkspaces: overrides.workspace?.maxRecentWorkspaces ?? base.workspace.maxRecentWorkspaces,
    },
    terminal: { ...base.terminal, ...(overrides.terminal ?? {}) },
    accessibility: { ...base.accessibility, ...(overrides.accessibility ?? {}) },
  };
}
