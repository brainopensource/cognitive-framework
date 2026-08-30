export type DesktopTheme = {
  name: "dark" | "light";
  bg: string;
  bgSidebar: string;
  bgCard: string;
  bgCardHover: string;
  bgInput: string;
  textPrimary: string;
  textMuted: string;
  accent: string;
  accentHover: string;
  success: string;
  warning: string;
  danger: string;
  running: string;
  border: string;
  borderActive: string;
  diffAddBg: string;
  diffAddFg: string;
  diffDeleteBg: string;
  diffDeleteFg: string;
};

export const DARK_DESKTOP_THEME: DesktopTheme = {
  name: "dark",
  bg: "#11111b",
  bgSidebar: "#181825",
  bgCard: "#1e1e2e",
  bgCardHover: "#252538",
  bgInput: "#181825",
  textPrimary: "#cdd6f4",
  textMuted: "#6c7086",
  accent: "#89b4fa",
  accentHover: "#b4befe",
  success: "#a6e3a1",
  warning: "#f9e2af",
  danger: "#f38ba8",
  running: "#fab387",
  border: "#313244",
  borderActive: "#89b4fa",
  diffAddBg: "#1e3a29",
  diffAddFg: "#a6e3a1",
  diffDeleteBg: "#3e1e29",
  diffDeleteFg: "#f38ba8",
};

export function getCssVariables(theme: DesktopTheme = DARK_DESKTOP_THEME): string {
  return `
    :root {
      --aether-bg: ${theme.bg};
      --aether-bg-sidebar: ${theme.bgSidebar};
      --aether-bg-card: ${theme.bgCard};
      --aether-bg-card-hover: ${theme.bgCardHover};
      --aether-bg-input: ${theme.bgInput};
      --aether-text-primary: ${theme.textPrimary};
      --aether-text-muted: ${theme.textMuted};
      --aether-accent: ${theme.accent};
      --aether-accent-hover: ${theme.accentHover};
      --aether-success: ${theme.success};
      --aether-warning: ${theme.warning};
      --aether-danger: ${theme.danger};
      --aether-running: ${theme.running};
      --aether-border: ${theme.border};
      --aether-border-active: ${theme.borderActive};
      --aether-diff-add-bg: ${theme.diffAddBg};
      --aether-diff-add-fg: ${theme.diffAddFg};
      --aether-diff-del-bg: ${theme.diffDeleteBg};
      --aether-diff-del-fg: ${theme.diffDeleteFg};
      --aether-font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
      --aether-font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    }
  `;
}
