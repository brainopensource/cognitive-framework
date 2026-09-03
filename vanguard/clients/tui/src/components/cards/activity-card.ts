import type { TerminalScreen } from "../../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens, type SemanticStyle } from "../../theme.js";

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
  theme: ThemeTokens = DEFAULT_THEME,
  headerStyle?: SemanticStyle
): void {
  const icon = isExpanded ? "▾ " : "▸ ";
  const text = `${icon}${title}${suffix ? " · " + suffix : ""}`;
  // An explicit per-card style (status colour) wins; expansion still brightens
  // a card that has no status colour of its own.
  const style = headerStyle ?? (isExpanded ? theme.textBright : theme.accent);
  screen.writeString(row, 2, text, style);
}
