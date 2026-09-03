import type { TerminalScreen } from "../../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../../theme.js";

export function renderVerificationCard(
  screen: TerminalScreen,
  row: number,
  title: string,
  passed: boolean,
  durationMs?: number,
  theme: ThemeTokens = DEFAULT_THEME
): number {
  const icon = passed ? "✔ " : "✖ ";
  const style = passed ? theme.success : theme.danger;
  const suffix = durationMs !== undefined ? `[${(durationMs / 1000).toFixed(2)}s]` : "";
  screen.writeString(row, 2, `${icon}${title} ${suffix}`.trim(), style);
  return 1;
}
