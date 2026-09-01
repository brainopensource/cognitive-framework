import type { TerminalScreen } from "../../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../../theme.js";
import { renderFoldedHeader } from "./activity-card.js";

export function renderResearchCard(
  screen: TerminalScreen,
  row: number,
  title: string,
  sourcesCount: number,
  isExpanded: boolean = false,
  theme: ThemeTokens = DEFAULT_THEME
): number {
  const suffix = `${sourcesCount} sources`;
  renderFoldedHeader(screen, row, title, isExpanded, suffix, theme);
  return 1;
}
