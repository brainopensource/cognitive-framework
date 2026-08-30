import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import type { TuiStoreState } from "../store.js";
import { truncateToWidth } from "../terminal/cell.js";

export function renderStatusFooter(
  screen: TerminalScreen,
  state: TuiStoreState,
  row: number,
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const width = screen.width;
  const isNarrow = width < 90;

  // Background
  screen.writeString(row, 0, " ".repeat(width), theme.surfaceRaised);

  const tokens = state.snapshot.tokens;
  const costMicros = Number(state.snapshot.costMicros || 0);
  const costStr = (costMicros / 1_000_000).toFixed(4);

  let leftText = "";
  if (!isNarrow) {
    leftText = ` tokens: ${tokens.totalTokens.toLocaleString()} (in: ${tokens.inTokens}, out: ${tokens.outTokens}) │ cost: $${costStr} │ seq: ${state.snapshot.lastSeq} `;
  } else {
    leftText = ` tok: ${tokens.totalTokens} │ $${costStr} │ seq: ${state.snapshot.lastSeq} `;
  }

  screen.writeString(row, 0, leftText, theme.textMuted);

  // Right side: status message or key hints
  const rightText = ` ${state.statusMessage} `;
  const rightCol = Math.max(leftText.length, width - rightText.length);
  screen.writeString(row, rightCol, rightText, theme.accent);
}
