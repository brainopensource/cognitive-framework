import type { TerminalScreen } from "../../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../../theme.js";
import { renderFoldedHeader } from "./activity-card.js";

export function renderDiffCard(
  screen: TerminalScreen,
  row: number,
  title: string,
  diffText: string,
  isExpanded: boolean,
  theme: ThemeTokens = DEFAULT_THEME
): number {
  let linesRendered = 1;
  const lines = diffText.split("\n");
  let additions = 0;
  let deletions = 0;

  for (const line of lines) {
    if (line.startsWith("+") && !line.startsWith("+++")) additions++;
    if (line.startsWith("-") && !line.startsWith("---")) deletions++;
  }

  const suffix = `+${additions} -${deletions}`;
  renderFoldedHeader(screen, row, title, isExpanded, suffix, theme);

  if (isExpanded) {
    for (let i = 0; i < Math.min(lines.length, 12); i++) {
      const line = lines[i]!;
      const r = row + 1 + i;
      if (r >= screen.height) break;

      if (line.startsWith("+") && !line.startsWith("+++")) {
        screen.writeString(r, 4, line, theme.diffAdd);
      } else if (line.startsWith("-") && !line.startsWith("---")) {
        screen.writeString(r, 4, line, theme.diffDelete);
      } else if (line.startsWith("@@")) {
        screen.writeString(r, 4, line, theme.diffHunk);
      } else {
        screen.writeString(r, 4, line, theme.diffContext);
      }
      linesRendered++;
    }
  }

  return linesRendered;
}
