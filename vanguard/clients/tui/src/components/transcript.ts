import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import type { TuiStoreState } from "../store.js";
import { renderTurn } from "./turn.js";

export function renderTranscript(
  screen: TerminalScreen,
  state: TuiStoreState,
  startRow: number,
  height: number,
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const width = screen.width;
  const endRow = startRow + height;

  // Clear transcript area
  for (let r = startRow; r < endRow; r++) {
    screen.writeString(r, 0, " ".repeat(width), theme.surface);
  }

  if (state.turns.length === 0) {
    const emptyMsg = "No active turns yet. Type a prompt in the composer below to begin.";
    screen.writeString(startRow + 2, 2, emptyMsg, theme.textMuted);
    return;
  }

  let curRow = startRow - state.scrollOffset;
  for (const turn of state.turns) {
    if (curRow >= endRow) break;
    const lines = renderTurn(screen, Math.max(startRow, curRow), turn, state.expandedCardIds, theme);
    curRow += lines;
  }

  // If user is scrolled up and new content exists, show bottom indicator
  if (state.scrollOffset > 0) {
    const indicator = " ↓ More recent messages below (Press 'G' or PageDown to jump to bottom) ";
    const indCol = Math.max(0, Math.floor((width - indicator.length) / 2));
    screen.writeString(endRow - 1, indCol, indicator, theme.approval);
  }
}
