import type { SemanticStyle } from "../theme.js";

// Fast unicode character width calculation
export function charWidth(codePoint: number): number {
  if (codePoint === 0) return 0;
  if (codePoint < 32 || (codePoint >= 0x7f && codePoint < 0xa0)) return 0;
  // Combining characters
  if (codePoint >= 0x300 && codePoint <= 0x36f) return 0;
  // CJK and wide characters
  if (
    (codePoint >= 0x1100 && codePoint <= 0x115f) ||
    (codePoint >= 0x2e80 && codePoint <= 0xa4cf && codePoint !== 0x303f) ||
    (codePoint >= 0xac00 && codePoint <= 0xd7a3) ||
    (codePoint >= 0xf900 && codePoint <= 0xfaff) ||
    (codePoint >= 0xfe10 && codePoint <= 0xfe19) ||
    (codePoint >= 0xfe30 && codePoint <= 0xfe6f) ||
    (codePoint >= 0xff00 && codePoint <= 0xff60) ||
    (codePoint >= 0xffe0 && codePoint <= 0xffe6) ||
    (codePoint >= 0x20000 && codePoint <= 0x2fffd) ||
    (codePoint >= 0x30000 && codePoint <= 0x3fffd)
  ) {
    return 2;
  }
  // Emoji presentation ranges
  if (
    (codePoint >= 0x1f300 && codePoint <= 0x1f5ff) ||
    (codePoint >= 0x1f600 && codePoint <= 0x1f64f) ||
    (codePoint >= 0x1f680 && codePoint <= 0x1f6ff) ||
    (codePoint >= 0x2600 && codePoint <= 0x26ff)
  ) {
    return 2;
  }
  return 1;
}

export function stringWidth(str: string): number {
  let width = 0;
  // Strip ANSI sequences
  const clean = str.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, "");
  for (const char of clean) {
    const cp = char.codePointAt(0);
    if (cp !== undefined) width += charWidth(cp);
  }
  return width;
}

export function truncateToWidth(str: string, maxWidth: number, ellipsis: string = "…"): string {
  if (maxWidth <= 0) return "";
  const total = stringWidth(str);
  if (total <= maxWidth) return str;

  const ellWidth = stringWidth(ellipsis);
  const targetWidth = Math.max(0, maxWidth - ellWidth);
  let curWidth = 0;
  let result = "";

  for (const char of str) {
    const cp = char.codePointAt(0);
    const w = cp ? charWidth(cp) : 1;
    if (curWidth + w > targetWidth) break;
    curWidth += w;
    result += char;
  }

  return result + ellipsis;
}

export function padToWidth(str: string, targetWidth: number, padChar: string = " "): string {
  const cur = stringWidth(str);
  if (cur >= targetWidth) return str;
  return str + padChar.repeat(targetWidth - cur);
}

export type TerminalCell = {
  char: string;
  width: number;
  style?: SemanticStyle;
};
