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
  caution: SemanticStyle;
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

export function detectColorMode(env: NodeJS.ProcessEnv = process.env): ColorMode {
  if (env["NO_COLOR"] || env["TERM"] === "dumb") {
    return "plain";
  }
  const colorterm = env["COLORTERM"] ?? "";
  if (colorterm === "truecolor" || colorterm === "24bit") {
    return "truecolor";
  }
  const term = env["TERM"] ?? "";
  // These terminal families support 24-bit color even when COLORTERM isn't
  // propagated (e.g. over some SSH hops).
  if (term.includes("kitty") || term.includes("alacritty") || term.includes("wezterm") || term.includes("iterm")) {
    return "truecolor";
  }
  // "xterm-256color" et al. promise a 256-entry palette, not 24-bit -- do not
  // upgrade this to truecolor just because COLORTERM was stripped somewhere.
  if (term.includes("256color")) {
    return "256color";
  }
  if (term.includes("color") || term.includes("ansi") || term.includes("xterm") || term.includes("screen") || term.includes("tmux")) {
    return "16color";
  }
  return "plain";
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
  caution: { fg: "#fab387", bold: true },
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

export function hexToRgb(hex: string): [number, number, number] | null {
  const clean = hex.replace("#", "");
  if (clean.length === 6) {
    const num = parseInt(clean, 16);
    return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
  }
  return null;
}

/**
 * Nearest color in xterm's 256-color palette: the 6x6x6 color cube (indices
 * 16-231) plus the 24-step grayscale ramp (232-255), whichever is closer.
 * Real ANSI-256 fallback per PRD_AETHER_TUI.md §8.1's "256-color... ANSI
 * fallback" budget -- previously this path collapsed every color to a flat
 * white-on-black, which made non-truecolor terminals unreadable.
 */
export function rgbToAnsi256(r: number, g: number, b: number): number {
  const toCubeIndex = (c: number) => Math.round((c / 255) * 5);
  const cr = toCubeIndex(r);
  const cg = toCubeIndex(g);
  const cb = toCubeIndex(b);
  const cubeIndex = 16 + 36 * cr + 6 * cg + cb;
  const cubeLevels = [0, 95, 135, 175, 215, 255];
  const cubeR = cubeLevels[cr]!;
  const cubeG = cubeLevels[cg]!;
  const cubeB = cubeLevels[cb]!;
  const cubeDist = (cubeR - r) ** 2 + (cubeG - g) ** 2 + (cubeB - b) ** 2;

  const gray = Math.round((r + g + b) / 3);
  const grayIndex = Math.max(0, Math.min(23, Math.round((gray - 8) / 10)));
  const grayLevel = 8 + grayIndex * 10;
  const grayDist = (grayLevel - r) ** 2 + (grayLevel - g) ** 2 + (grayLevel - b) ** 2;

  return grayDist < cubeDist ? 232 + grayIndex : cubeIndex;
}

function rgbToHueDegrees(r: number, g: number, b: number): number {
  const rn = r / 255, gn = g / 255, bn = b / 255;
  const max = Math.max(rn, gn, bn);
  const min = Math.min(rn, gn, bn);
  const d = max - min;
  if (d === 0) return 0;
  let h: number;
  if (max === rn) h = ((gn - bn) / d) % 6;
  else if (max === gn) h = (bn - rn) / d + 2;
  else h = (rn - gn) / d + 4;
  h *= 60;
  if (h < 0) h += 360;
  return h;
}

/**
 * Nearest of the 16 standard ANSI colors, by hue sector rather than raw RGB
 * distance. A pastel theme (this one included) has every color's channels
 * fairly close together in absolute terms, so a naive nearest-neighbor over
 * (r,g,b) collapses most of them to white -- e.g. #f38ba8 and #a6e3a1 both
 * land nearer to white than to red or green. Classifying by hue angle first
 * (falling back to a grayscale ramp only when saturation is genuinely low)
 * keeps desaturated theme colors distinguishable in a true 16-color terminal.
 */
export function rgbToAnsi16(r: number, g: number, b: number): number {
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const lightness = (max + min) / 2 / 255;
  const saturation = max === 0 ? 0 : (max - min) / 255;

  if (saturation < 0.12) {
    if (lightness > 0.85) return 15;
    if (lightness > 0.55) return 7;
    if (lightness > 0.25) return 8;
    return 0;
  }

  const hue = rgbToHueDegrees(r, g, b);
  let base: number;
  if (hue < 30 || hue >= 330) base = 1; // red
  else if (hue < 90) base = 3; // yellow
  else if (hue < 150) base = 2; // green
  else if (hue < 210) base = 6; // cyan
  else if (hue < 270) base = 4; // blue
  else base = 5; // magenta

  const bright = max >= 170 ? 8 : 0;
  return base + bright;
}

function ansi16Code(index: number, isBg: boolean): string {
  const bright = index >= 8;
  const base = isBg ? 40 : 30;
  const brightBase = isBg ? 100 : 90;
  return bright ? `${brightBase + (index - 8)}` : `${base + index}`;
}

function colorCode(hex: string, mode: ColorMode, isBg: boolean): string | null {
  const rgb = hexToRgb(hex);
  if (!rgb) return null;
  const [r, g, b] = rgb;

  if (mode === "truecolor") {
    return `${isBg ? 48 : 38};2;${r};${g};${b}`;
  }
  if (mode === "256color") {
    return `${isBg ? 48 : 38};5;${rgbToAnsi256(r, g, b)}`;
  }
  // 16color
  return ansi16Code(rgbToAnsi16(r, g, b), isBg);
}

export function styleToAnsi(style: SemanticStyle, mode: ColorMode = "truecolor"): { open: string; close: string } {
  if (mode === "plain") {
    return { open: "", close: "" };
  }

  let open = "";
  const close = "\x1b[0m";

  if (style.bold) open += "\x1b[1m";
  if (style.dim) open += "\x1b[2m";
  if (style.italic) open += "\x1b[3m";
  if (style.underline) open += "\x1b[4m";
  if (style.inverse) open += "\x1b[7m";

  if (style.fg) {
    const code = colorCode(style.fg, mode, false);
    if (code) open += `\x1b[${code}m`;
  }

  if (style.bg) {
    const code = colorCode(style.bg, mode, true);
    if (code) open += `\x1b[${code}m`;
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
