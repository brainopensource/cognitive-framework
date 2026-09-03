import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import { truncateToWidth } from "../terminal/cell.js";

export type SelectOption = {
  id: string;
  name: string;
  description?: string;
};

/** First visible row so `selectedIndex` stays inside a fixed-height list. */
export function listWindowStart(selectedIndex: number, count: number, viewHeight: number): number {
  if (viewHeight <= 0 || count <= viewHeight) return 0;
  const maxStart = count - viewHeight;
  return Math.max(0, Math.min(selectedIndex - viewHeight + 1, maxStart));
}

export function renderSelectModal(
  screen: TerminalScreen,
  title: string,
  options: SelectOption[],
  selectedIndex: number = 0,
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const width = screen.width;
  const height = screen.height;

  const modalWidth = Math.min(60, width - 4);
  const modalHeight = Math.min(12, height - 4);
  const startRow = Math.max(1, Math.floor((height - modalHeight) / 2));
  const startCol = Math.max(2, Math.floor((width - modalWidth) / 2));

  // Border & Header
  screen.writeString(startRow, startCol, "┌" + "─".repeat(modalWidth - 2) + "┐", theme.borderActive);
  screen.writeString(startRow, startCol + 2, ` Select ${title} (Enter to pick, Esc to cancel) `, theme.accent);

  const listHeight = modalHeight - 2;
  const windowStart = listWindowStart(selectedIndex, options.length, listHeight);
  for (let i = 0; i < listHeight; i++) {
    const r = startRow + 1 + i;
    screen.writeString(r, startCol, "│", theme.borderActive);
    screen.writeString(r, startCol + 1, " ".repeat(modalWidth - 2), theme.surface);

    const optionIndex = windowStart + i;
    if (optionIndex < options.length) {
      const opt = options[optionIndex]!;
      const isSel = optionIndex === selectedIndex;
      const text = `${opt.id.padEnd(20)} ${opt.description ?? opt.name}`;
      screen.writeString(
        r,
        startCol + 2,
        truncateToWidth(text, modalWidth - 4),
        isSel ? theme.selected : theme.textPrimary
      );
    }
    screen.writeString(r, startCol + modalWidth - 1, "│", theme.borderActive);
  }

  // Bottom border
  screen.writeString(startRow + modalHeight - 1, startCol, "└" + "─".repeat(modalWidth - 2) + "┘", theme.borderActive);
}
