export type ColorMode = "truecolor" | "256color" | "16color" | "plain";

export type SemanticStyle = {
  fg?: string;
  bg?: string;
  bold?: boolean;
  dim?: boolean;
  italic?: boolean;
  underline?: boolean;
  inverse?: boolean;
};

export type ThemeTokens = {
  surface: SemanticStyle;
  surfaceRaised: SemanticStyle;
  textPrimary: SemanticStyle;
  textMuted: SemanticStyle;
  textBright: SemanticStyle;
  accent: SemanticStyle;
  success: SemanticStyle;
  warning: SemanticStyle;
  danger: SemanticStyle;
  running: SemanticStyle;
  approval: SemanticStyle;
  border: SemanticStyle;
  borderActive: SemanticStyle;
  diffAdd: SemanticStyle;
  diffDelete: SemanticStyle;
  diffContext: SemanticStyle;
  diffHunk: SemanticStyle;
  selected: SemanticStyle;
};

export function detectColorMode(): ColorMode {
  if (process.env["NO_COLOR"] || process.env["TERM"] === "dumb") {
    return "plain";
  }
  const colorterm = process.env["COLORTERM"] ?? "";
  if (colorterm === "truecolor" || colorterm === "24bit") {
    return "truecolor";
  }
  const term = process.env["TERM"] ?? "";
  if (term.includes("256color") || term.includes("kitty") || term.includes("alacritty") || term.includes("wezterm")) {
    return "truecolor";
  }
  if (term.includes("color") || term.includes("ansi") || term.includes("xterm")) {
    return "16color";
  }
  return "256color";
}

export const DEFAULT_THEME: ThemeTokens = {
  surface: { bg: "#1e1e2e", fg: "#cdd6f4" },
  surfaceRaised: { bg: "#252538", fg: "#cdd6f4" },
  textPrimary: { fg: "#cdd6f4" },
  textMuted: { fg: "#6c7086" },
  textBright: { fg: "#ffffff", bold: true },
  accent: { fg: "#89b4fa", bold: true },
  success: { fg: "#a6e3a1" },
  warning: { fg: "#f9e2af" },
  danger: { fg: "#f38ba8", bold: true },
  running: { fg: "#fab387", bold: true },
  approval: { fg: "#f9e2af", bg: "#45475a", bold: true },
  border: { fg: "#45475a" },
  borderActive: { fg: "#89b4fa" },
  diffAdd: { fg: "#a6e3a1", bg: "#1e3a29" },
  diffDelete: { fg: "#f38ba8", bg: "#3e1e29" },
  diffContext: { fg: "#9399b2" },
  diffHunk: { fg: "#89dceb", dim: true },
  selected: { bg: "#45475a", fg: "#ffffff", bold: true },
};

function hexToRgb(hex: string): [number, number, number] | null {
  const clean = hex.replace("#", "");
  if (clean.length === 6) {
    const num = parseInt(clean, 16);
    return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
  }
  return null;
}

export function styleToAnsi(style: SemanticStyle, mode: ColorMode = "truecolor"): { open: string; close: string } {
  if (mode === "plain") {
    return { open: "", close: "" };
  }

  let open = "";
  let close = "\x1b[0m";

  if (style.bold) open += "\x1b[1m";
  if (style.dim) open += "\x1b[2m";
  if (style.italic) open += "\x1b[3m";
  if (style.underline) open += "\x1b[4m";
  if (style.inverse) open += "\x1b[7m";

  if (style.fg) {
    const rgb = hexToRgb(style.fg);
    if (rgb && mode === "truecolor") {
      open += `\x1b[38;2;${rgb[0]};${rgb[1]};${rgb[2]}m`;
    } else {
      open += "\x1b[37m";
    }
  }

  if (style.bg) {
    const rgb = hexToRgb(style.bg);
    if (rgb && mode === "truecolor") {
      open += `\x1b[48;2;${rgb[0]};${rgb[1]};${rgb[2]}m`;
    } else {
      open += "\x1b[40m";
    }
  }

  return { open, close };
}

export function applyStyle(text: string, style: SemanticStyle, mode: ColorMode = "truecolor"): string {
  const { open, close } = styleToAnsi(style, mode);
  if (!open) return text;
  return `${open}${text}${close}`;
}

export const STATUS_TAGS = {
  RUNNING: "[RUNNING]",
  WAITING: "[WAITING]",
  APPROVAL: "[APPROVAL]",
  PASS: "[PASS]",
  FAIL: "[FAIL]",
  OFFLINE: "[OFFLINE]",
  SATISFIED: "[SATISFIED]",
  CANCELLED: "[CANCELLED]",
} as const;
