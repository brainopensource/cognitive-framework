import type { TerminalScreen } from "../../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../../theme.js";

export type RenderCardOptions = {
  id: string;
  isExpanded: boolean;
  theme?: ThemeTokens;
};

export function renderFoldedHeader(
  screen: TerminalScreen,
  row: number,
  title: string,
  isExpanded: boolean,
  suffix?: string,
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const icon = isExpanded ? "▾ " : "▸ ";
  const text = `${icon}${title}${suffix ? " · " + suffix : ""}`;
  screen.writeString(row, 2, text, isExpanded ? theme.textBright : theme.accent);
}
