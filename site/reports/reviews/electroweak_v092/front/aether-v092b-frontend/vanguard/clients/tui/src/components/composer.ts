import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import type { TuiStoreState } from "../store.js";
import { truncateToWidth } from "../terminal/cell.js";

export function renderComposer(
  screen: TerminalScreen,
  state: TuiStoreState,
  startRow: number,
  height: number = 3,
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const width = screen.width;
  const isFocused = state.focus === "composer";
  const borderStyle = isFocused ? theme.borderActive : theme.border;

  // Top border
  screen.writeString(startRow, 0, "─".repeat(width), borderStyle);

  // Content area
  const inputRow = startRow + 1;
  screen.writeString(inputRow, 0, " ".repeat(width), theme.surface);

  const promptPrefix = "> ";
  screen.writeString(inputRow, 1, promptPrefix, isFocused ? theme.accent : theme.textMuted);

  if (state.composerText.length === 0) {
    const placeholder = "Message AETHER... (Press '/' for commands, '?' for help)";
    screen.writeString(inputRow, 1 + promptPrefix.length, truncateToWidth(placeholder, width - 4), theme.textMuted);
    if (isFocused) {
      screen.setCursor(inputRow, 1 + promptPrefix.length, true);
    }
  } else {
    screen.writeString(inputRow, 1 + promptPrefix.length, truncateToWidth(state.composerText, width - 4), theme.textBright);
    if (isFocused) {
      const cursorCol = 1 + promptPrefix.length + state.composerCursor;
      screen.setCursor(inputRow, Math.min(width - 2, cursorCol), true);
    }
  }

  // Bottom border if height >= 3
  if (height >= 3) {
    screen.writeString(startRow + 2, 0, "─".repeat(width), borderStyle);
  }
}
