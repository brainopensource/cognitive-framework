import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import { truncateToWidth } from "../terminal/cell.js";

export function renderDiffViewer(
  screen: TerminalScreen,
  diffText: string,
  scrollOffset: number = 0,
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const width = screen.width;
  const height = screen.height;

  // Clear entire screen for modal
  for (let r = 0; r < height; r++) {
    screen.writeString(r, 0, " ".repeat(width), theme.surface);
  }

  // Header
  const title = " ── Unified Diff Viewer (Esc to Close, ↑/↓ to Scroll) ── ";
  screen.writeString(0, 0, truncateToWidth(title.padEnd(width, "─"), width), theme.accent);

  const lines = diffText.split("\n");
  const visibleHeight = height - 2;

  for (let i = 0; i < visibleHeight; i++) {
    const lineIdx = scrollOffset + i;
    if (lineIdx >= lines.length) break;
    const line = lines[lineIdx]!;
    const row = 1 + i;

    if (line.startsWith("+") && !line.startsWith("+++")) {
      screen.writeString(row, 1, truncateToWidth(line, width - 2), theme.diffAdd);
    } else if (line.startsWith("-") && !line.startsWith("---")) {
      screen.writeString(row, 1, truncateToWidth(line, width - 2), theme.diffDelete);
    } else if (line.startsWith("@@")) {
      screen.writeString(row, 1, truncateToWidth(line, width - 2), theme.diffHunk);
    } else {
      screen.writeString(row, 1, truncateToWidth(line, width - 2), theme.diffContext);
    }
  }

  // Footer status
  const footer = ` Line ${scrollOffset + 1}/${lines.length} │ [Esc] Close `;
  screen.writeString(height - 1, 0, truncateToWidth(footer.padEnd(width, "─"), width), theme.textMuted);
}
