import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import { truncateToWidth } from "../terminal/cell.js";

const SHORTCUTS = [
  ["Enter", "Submit prompt to agent"],
  ["Shift+Enter / Alt+Enter", "Insert newline in composer"],
  ["Tab / Shift+Tab", "Cycle focus (Composer ↔ Transcript ↔ Approvals)"],
  ["j / k or ↑ / ↓", "Scroll transcript line by line"],
  ["Ctrl+U / Ctrl+D", "Scroll transcript half page"],
  ["Space / Enter", "Toggle expand/collapse selected activity card"],
  ["/", "Open command palette"],
  ["y / n", "Approve / Reject governance challenge"],
  ["d", "Open dedicated full-screen diff viewer"],
  ["Ctrl+C", "Cancel active run / Interrupt turn"],
  ["Esc", "Close active modal / Return to composer"],
];

export function renderHelpOverlay(
  screen: TerminalScreen,
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const width = screen.width;
  const height = screen.height;

  const modalWidth = Math.min(65, width - 4);
  const modalHeight = Math.min(16, height - 4);
  const startRow = Math.max(1, Math.floor((height - modalHeight) / 2));
  const startCol = Math.max(2, Math.floor((width - modalWidth) / 2));

  // Top border
  screen.writeString(startRow, startCol, "┌" + "─".repeat(modalWidth - 2) + "┐", theme.borderActive);
  screen.writeString(startRow, startCol + 2, " AETHER Keyboard Shortcuts (Esc to close) ", theme.accent);

  for (let i = 0; i < modalHeight - 2; i++) {
    const r = startRow + 1 + i;
    screen.writeString(r, startCol, "│", theme.borderActive);
    screen.writeString(r, startCol + 1, " ".repeat(modalWidth - 2), theme.surface);

    if (i < SHORTCUTS.length) {
      const [key, desc] = SHORTCUTS[i]!;
      screen.writeString(r, startCol + 2, key!.padEnd(26), theme.textBright);
      screen.writeString(r, startCol + 28, truncateToWidth(desc!, modalWidth - 30), theme.textPrimary);
    }
    screen.writeString(r, startCol + modalWidth - 1, "│", theme.borderActive);
  }

  // Bottom border
  screen.writeString(startRow + modalHeight - 1, startCol, "└" + "─".repeat(modalWidth - 2) + "┘", theme.borderActive);
}
