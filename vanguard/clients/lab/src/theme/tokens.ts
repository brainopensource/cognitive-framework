export type LabTheme = {
  name: "dark-precision" | "light-precision";
  bg: string;
  bgSurface: string;
  bgPanel: string;
  bgHover: string;
  bgActive: string;
  bgInput: string;
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  border: string;
  borderSubtle: string;
  borderActive: string;
  accent: string;
  accentMuted: string;
  success: string;
  successBg: string;
  warning: string;
  warningBg: string;
  danger: string;
  dangerBg: string;
  running: string;
  runningBg: string;
  pending: string;
  digest: string;
  diffAddBg: string;
  diffAddFg: string;
  diffDeleteBg: string;
  diffDeleteFg: string;
};

export const LAB_THEME: LabTheme = {
  name: "dark-precision",
  bg: "#0b0e14",
  bgSurface: "#11151c",
  bgPanel: "#161b24",
  bgHover: "#1f2633",
  bgActive: "#283243",
  bgInput: "#0f131a",
  textPrimary: "#e6edf3",
  textSecondary: "#8b949e",
  textMuted: "#545d68",
  border: "#252d3a",
  borderSubtle: "#1b222d",
  borderActive: "#388bfd",
  accent: "#58a6ff",
  accentMuted: "#1f385c",
  success: "#3fb950",
  successBg: "#122619",
  warning: "#d29922",
  warningBg: "#2d2208",
  danger: "#f85149",
  dangerBg: "#301314",
  running: "#e3b341",
  runningBg: "#2c220f",
  pending: "#a371f7",
  digest: "#79c0ff",
  diffAddBg: "#132c1b",
  diffAddFg: "#56d364",
  diffDeleteBg: "#38191d",
  diffDeleteFg: "#ff7b72",
};

export function getCssVariables(theme: LabTheme = LAB_THEME): string {
  return `
    :root {
      --lab-bg: ${theme.bg};
      --lab-bg-surface: ${theme.bgSurface};
      --lab-bg-panel: ${theme.bgPanel};
      --lab-bg-hover: ${theme.bgHover};
      --lab-bg-active: ${theme.bgActive};
      --lab-bg-input: ${theme.bgInput};
      --lab-text-primary: ${theme.textPrimary};
      --lab-text-secondary: ${theme.textSecondary};
      --lab-text-muted: ${theme.textMuted};
      --lab-border: ${theme.border};
      --lab-border-subtle: ${theme.borderSubtle};
      --lab-border-active: ${theme.borderActive};
      --lab-accent: ${theme.accent};
      --lab-accent-muted: ${theme.accentMuted};
      --lab-success: ${theme.success};
      --lab-success-bg: ${theme.successBg};
      --lab-warning: ${theme.warning};
      --lab-warning-bg: ${theme.warningBg};
      --lab-danger: ${theme.danger};
      --lab-danger-bg: ${theme.dangerBg};
      --lab-running: ${theme.running};
      --lab-running-bg: ${theme.runningBg};
      --lab-pending: ${theme.pending};
      --lab-digest: ${theme.digest};
      --lab-diff-add-bg: ${theme.diffAddBg};
      --lab-diff-add-fg: ${theme.diffAddFg};
      --lab-diff-del-bg: ${theme.diffDeleteBg};
      --lab-diff-del-fg: ${theme.diffDeleteFg};
      --lab-font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --lab-font-mono: ui-monospace, "SF Mono", "Cascadia Code", "Segoe UI Mono", Menlo, Consolas, monospace;
      --lab-radius-sm: 3px;
      --lab-radius-md: 5px;
      --lab-radius-lg: 8px;
    }
  `;
}
