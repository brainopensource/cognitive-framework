import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import type { TuiStoreState } from "../store.js";
import { renderTurn } from "./turn.js";
import { truncateToWidth } from "../terminal/cell.js";

const TIPS: readonly [string, string][] = [
  ["/", "open the command palette"],
  ["@path", "inline a file's content into your prompt"],
  ["!cmd", "run a shell command locally, no model call"],
  ["/plan", "toggle read-only plan mode before a risky change"],
  ["?", "show all keyboard shortcuts"],
];

function renderEmptyState(
  screen: TerminalScreen,
  startRow: number,
  height: number,
  width: number,
  agentId: string,
  theme: ThemeTokens
): void {
  const boxWidth = Math.min(64, width - 8);
  const boxHeight = 4 + TIPS.length;
  const boxRow = startRow + Math.max(0, Math.floor((height - boxHeight) / 2));
  const boxCol = Math.max(2, Math.floor((width - boxWidth) / 2));

  screen.writeString(boxRow, boxCol, "╭" + "─".repeat(boxWidth - 2) + "╮", theme.border);
  const title = ` AETHER · ${agentId} `;
  screen.writeString(boxRow, boxCol + Math.max(1, Math.floor((boxWidth - title.length) / 2)), title, theme.accent);

  screen.writeString(boxRow + 1, boxCol, "│" + " ".repeat(boxWidth - 2) + "│", theme.surface);
  const subtitle = "Type a prompt below to start, or try:";
  screen.writeString(boxRow + 1, boxCol + 2, truncateToWidth(subtitle, boxWidth - 4), theme.textMuted);

  for (let i = 0; i < TIPS.length; i++) {
    const [key, desc] = TIPS[i]!;
    const row = boxRow + 2 + i;
    screen.writeString(row, boxCol, "│" + " ".repeat(boxWidth - 2) + "│", theme.surface);
    screen.writeString(row, boxCol + 2, key.padEnd(8), theme.textBright);
    screen.writeString(row, boxCol + 10, truncateToWidth(desc, boxWidth - 12), theme.textMuted);
  }

  const lastRow = boxRow + 2 + TIPS.length;
  screen.writeString(lastRow, boxCol, "│" + " ".repeat(boxWidth - 2) + "│", theme.surface);
  screen.writeString(lastRow + 1, boxCol, "╰" + "─".repeat(boxWidth - 2) + "╯", theme.border);
}

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
    renderEmptyState(screen, startRow, height, width, state.agentId, theme);
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
