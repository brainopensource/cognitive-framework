import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import { truncateToWidth } from "../terminal/cell.js";

export type PaletteCommand = {
  id: string;
  name: string;
  description: string;
  action: () => void;
};

export function renderCommandPalette(
  screen: TerminalScreen,
  commands: PaletteCommand[],
  selectedIndex: number = 0,
  filterQuery: string = "",
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const width = screen.width;
  const height = screen.height;

  const modalWidth = Math.min(60, width - 4);
  const modalHeight = Math.min(14, height - 4);
  const startRow = Math.max(1, Math.floor((height - modalHeight) / 2));
  const startCol = Math.max(2, Math.floor((width - modalWidth) / 2));

  // Border & Header
  screen.writeString(startRow, startCol, "┌" + "─".repeat(modalWidth - 2) + "┐", theme.borderActive);
  screen.writeString(startRow, startCol + 2, " Command Palette (/ to filter, Esc to close) ", theme.accent);

  // Search input row
  screen.writeString(startRow + 1, startCol, "│", theme.borderActive);
  screen.writeString(startRow + 1, startCol + 2, `> /${filterQuery}`, theme.textBright);
  screen.writeString(startRow + 1, startCol + modalWidth - 1, "│", theme.borderActive);

  // Separator
  screen.writeString(startRow + 2, startCol, "├" + "─".repeat(modalWidth - 2) + "┤", theme.borderActive);

  const filtered = commands.filter(
    (c) =>
      c.id.toLowerCase().includes(filterQuery.toLowerCase()) ||
      c.name.toLowerCase().includes(filterQuery.toLowerCase())
  );

  const listHeight = modalHeight - 4;
  for (let i = 0; i < listHeight; i++) {
    const r = startRow + 3 + i;
    screen.writeString(r, startCol, "│", theme.borderActive);
    screen.writeString(r, startCol + 1, " ".repeat(modalWidth - 2), theme.surface);

    if (i < filtered.length) {
      const cmd = filtered[i]!;
      const isSel = i === selectedIndex;
      const text = `${cmd.name.padEnd(20)} ${cmd.description}`;
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
