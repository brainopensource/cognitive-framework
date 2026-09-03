import type { TerminalScreen } from "../../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens, type SemanticStyle } from "../../theme.js";
import { renderFoldedHeader } from "./activity-card.js";

export function renderToolCard(
  screen: TerminalScreen,
  row: number,
  title: string,
  details?: string,
  durationMs?: number,
  isExpanded: boolean = false,
  theme: ThemeTokens = DEFAULT_THEME,
  headerStyle?: SemanticStyle
): number {
  let linesRendered = 1;
  const suffix = durationMs !== undefined ? `${durationMs} ms` : undefined;
  renderFoldedHeader(screen, row, title, isExpanded, suffix, theme, headerStyle);

  if (isExpanded && details) {
    const detailLines = details.split("\n");
    for (let i = 0; i < Math.min(detailLines.length, 6); i++) {
      const line = detailLines[i]!;
      const r = row + 1 + i;
      if (r >= screen.height) break;
      screen.writeString(r, 4, line, theme.textMuted);
      linesRendered++;
    }
  }

  return linesRendered;
}
