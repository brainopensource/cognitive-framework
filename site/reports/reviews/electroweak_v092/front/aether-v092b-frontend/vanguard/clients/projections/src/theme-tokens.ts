export type SemanticThemeTokens = {
  background: string;
  surface: string;
  surfaceRaised: string;
  overlay: string;
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  border: string;
  borderStrong: string;
  focus: string;
  accent: string;
  accentHover: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
  running: string;
  waiting: string;
  approval: string;
  complete: string;
  failed: string;
  diffAddBg: string;
  diffAddFg: string;
  diffDeleteBg: string;
  diffDeleteFg: string;
  diffModifyBg: string;
  diffModifyFg: string;
  codeBackground: string;
  selection: string;
};

export const DARK_THEME: SemanticThemeTokens = {
  background: "#11111b",
  surface: "#181825",
  surfaceRaised: "#1e1e2e",
  overlay: "rgba(0, 0, 0, 0.6)",
  textPrimary: "#cdd6f4",
  textSecondary: "#a6adc8",
  textMuted: "#6c7086",
  border: "#313244",
  borderStrong: "#45475a",
  focus: "#89b4fa",
  accent: "#89b4fa",
  accentHover: "#b4befe",
  success: "#a6e3a1",
  warning: "#f9e2af",
  danger: "#f38ba8",
  info: "#89dceb",
  running: "#fab387",
  waiting: "#f9e2af",
  approval: "#f9e2af",
  complete: "#a6e3a1",
  failed: "#f38ba8",
  diffAddBg: "#1e3a29",
  diffAddFg: "#a6e3a1",
  diffDeleteBg: "#3e1e29",
  diffDeleteFg: "#f38ba8",
  diffModifyBg: "#2d2f3d",
  diffModifyFg: "#89dceb",
  codeBackground: "#181825",
  selection: "#45475a",
};

export const LIGHT_THEME: SemanticThemeTokens = {
  background: "#eff1f5",
  surface: "#e6e9ef",
  surfaceRaised: "#dce0e8",
  overlay: "rgba(0, 0, 0, 0.4)",
  textPrimary: "#4c4f69",
  textSecondary: "#5c5f77",
  textMuted: "#8c8fa1",
  border: "#ccd0da",
  borderStrong: "#bcc0cc",
  focus: "#1e66f5",
  accent: "#1e66f5",
  accentHover: "#7287fd",
  success: "#40a02b",
  warning: "#df8e1d",
  danger: "#d20f39",
  info: "#04a5e5",
  running: "#fe640b",
  waiting: "#df8e1d",
  approval: "#df8e1d",
  complete: "#40a02b",
  failed: "#d20f39",
  diffAddBg: "#e3f2e6",
  diffAddFg: "#40a02b",
  diffDeleteBg: "#fce8eb",
  diffDeleteFg: "#d20f39",
  diffModifyBg: "#e8effc",
  diffModifyFg: "#1e66f5",
  codeBackground: "#e6e9ef",
  selection: "#ccd0da",
};

export const HIGH_CONTRAST_THEME: SemanticThemeTokens = {
  background: "#000000",
  surface: "#121212",
  surfaceRaised: "#1f1f1f",
  overlay: "rgba(0, 0, 0, 0.8)",
  textPrimary: "#ffffff",
  textSecondary: "#e0e0e0",
  textMuted: "#aaaaaa",
  border: "#ffffff",
  borderStrong: "#ffff00",
  focus: "#ffff00",
  accent: "#00ffff",
  accentHover: "#ffffff",
  success: "#00ff00",
  warning: "#ffff00",
  danger: "#ff0033",
  info: "#00ffff",
  running: "#ffaa00",
  waiting: "#ffff00",
  approval: "#ffff00",
  complete: "#00ff00",
  failed: "#ff0033",
  diffAddBg: "#003300",
  diffAddFg: "#00ff00",
  diffDeleteBg: "#330000",
  diffDeleteFg: "#ff0033",
  diffModifyBg: "#002233",
  diffModifyFg: "#00ffff",
  codeBackground: "#050505",
  selection: "#ffffff",
};

export function getThemeTokens(themeName: "dark" | "light" | "high-contrast" = "dark"): SemanticThemeTokens {
  switch (themeName) {
    case "light":
      return LIGHT_THEME;
    case "high-contrast":
      return HIGH_CONTRAST_THEME;
    case "dark":
    default:
      return DARK_THEME;
  }
}

export function generateCssVariables(tokens: SemanticThemeTokens = DARK_THEME): string {
  return `
    :root {
      --aether-bg: ${tokens.background};
      --aether-surface: ${tokens.surface};
      --aether-surface-raised: ${tokens.surfaceRaised};
      --aether-overlay: ${tokens.overlay};
      --aether-text-primary: ${tokens.textPrimary};
      --aether-text-secondary: ${tokens.textSecondary};
      --aether-text-muted: ${tokens.textMuted};
      --aether-border: ${tokens.border};
      --aether-border-strong: ${tokens.borderStrong};
      --aether-focus: ${tokens.focus};
      --aether-accent: ${tokens.accent};
      --aether-accent-hover: ${tokens.accentHover};
      --aether-success: ${tokens.success};
      --aether-warning: ${tokens.warning};
      --aether-danger: ${tokens.danger};
      --aether-info: ${tokens.info};
      --aether-running: ${tokens.running};
      --aether-waiting: ${tokens.waiting};
      --aether-approval: ${tokens.approval};
      --aether-complete: ${tokens.complete};
      --aether-failed: ${tokens.failed};
      --aether-diff-add-bg: ${tokens.diffAddBg};
      --aether-diff-add-fg: ${tokens.diffAddFg};
      --aether-diff-del-bg: ${tokens.diffDeleteBg};
      --aether-diff-del-fg: ${tokens.diffDeleteFg};
      --aether-diff-mod-bg: ${tokens.diffModifyBg};
      --aether-diff-mod-fg: ${tokens.diffModifyFg};
      --aether-code-bg: ${tokens.codeBackground};
      --aether-selection: ${tokens.selection};
      --aether-font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
      --aether-font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    }
  `;
}
