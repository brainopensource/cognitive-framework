import type { FrontendSettings } from "@aether/contracts";
import { DEFAULT_FRONTEND_SETTINGS } from "@aether/projections";
import type { FrontendPersistencePort } from "../persistence/persistence-port.js";
import { NodeFsPersistenceAdapter } from "../persistence/persistence-port.js";

export type ExplicitConfigurationOverrides = {
  socketPath?: string;
  httpUrl?: string;
  defaultWorkspace?: string;
  defaultAgent?: string;
  defaultWorkflow?: string;
  theme?: "dark" | "light" | "high-contrast";
  density?: "compact" | "comfortable";
  tuiColorMode?: "truecolor" | "256color" | "16color" | "plain";
};

export class ConfigurationResolver {
  public static async resolve(
    explicit: ExplicitConfigurationOverrides = {},
    persistence?: FrontendPersistencePort
  ): Promise<FrontendSettings> {
    const port = persistence ?? new NodeFsPersistenceAdapter();
    const userSaved = (await port.loadSettings()) ?? {};

    // 1. Start with product defaults
    const settings: FrontendSettings = {
      ...DEFAULT_FRONTEND_SETTINGS,
      ...userSaved,
      general: {
        ...DEFAULT_FRONTEND_SETTINGS.general,
        ...(userSaved.general ?? {}),
      },
      runtime: {
        ...DEFAULT_FRONTEND_SETTINGS.runtime,
        ...(userSaved.runtime ?? {}),
      },
      appearance: {
        ...DEFAULT_FRONTEND_SETTINGS.appearance,
        ...(userSaved.appearance ?? {}),
      },
      workspace: {
        ...DEFAULT_FRONTEND_SETTINGS.workspace,
        ...(userSaved.workspace ?? {}),
      },
      terminal: {
        ...DEFAULT_FRONTEND_SETTINGS.terminal,
        ...(userSaved.terminal ?? {}),
      },
      accessibility: {
        ...DEFAULT_FRONTEND_SETTINGS.accessibility,
        ...(userSaved.accessibility ?? {}),
      },
    };

    // 2. Apply Environment Overrides
    if (process.env.AETHER_RUNTIME_SOCK) {
      settings.runtime.socketPath = process.env.AETHER_RUNTIME_SOCK;
    }
    if (process.env.AETHER_HTTP_URL) {
      settings.runtime.httpUrl = process.env.AETHER_HTTP_URL;
    }
    if (process.env.AETHER_DEFAULT_WORKSPACE) {
      settings.general.defaultWorkspace = process.env.AETHER_DEFAULT_WORKSPACE;
    }
    if (process.env.AETHER_DEFAULT_AGENT) {
      settings.general.defaultAgent = process.env.AETHER_DEFAULT_AGENT;
    }
    if (process.env.AETHER_DEFAULT_WORKFLOW) {
      settings.general.defaultWorkflow = process.env.AETHER_DEFAULT_WORKFLOW;
    }
    if (process.env.AETHER_THEME) {
      settings.appearance.theme = process.env.AETHER_THEME as any;
    }
    if (process.env.AETHER_TUI_COLOR_MODE) {
      settings.terminal.tuiColorMode = process.env.AETHER_TUI_COLOR_MODE as any;
    }

    // 3. Apply Explicit Command-line / In-memory Overrides
    if (explicit.socketPath) settings.runtime.socketPath = explicit.socketPath;
    if (explicit.httpUrl) settings.runtime.httpUrl = explicit.httpUrl;
    if (explicit.defaultWorkspace) settings.general.defaultWorkspace = explicit.defaultWorkspace;
    if (explicit.defaultAgent) settings.general.defaultAgent = explicit.defaultAgent;
    if (explicit.defaultWorkflow) settings.general.defaultWorkflow = explicit.defaultWorkflow;
    if (explicit.theme) settings.appearance.theme = explicit.theme;
    if (explicit.density) settings.appearance.density = explicit.density;
    if (explicit.tuiColorMode) settings.terminal.tuiColorMode = explicit.tuiColorMode;

    return settings;
  }
}
