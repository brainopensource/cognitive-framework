import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import type { TuiStoreState } from "../store.js";
import { computeUsageBar, tierStyle } from "./usage-bar.js";

export function renderStatusFooter(
  screen: TerminalScreen,
  state: TuiStoreState,
  row: number,
  theme: ThemeTokens = DEFAULT_THEME,
  nowMs: number = Date.now()
): void {
  const width = screen.width;
  const isNarrow = width < 90;

  // Background
  screen.writeString(row, 0, " ".repeat(width), theme.surfaceRaised);

  const tokens = state.snapshot.tokens;
  const costMicros = Number(state.snapshot.costMicros || 0);
  const costStr = (costMicros / 1_000_000).toFixed(4);
  const usage = computeUsageBar(tokens.totalTokens, state.contextWindowTokens, isNarrow ? 6 : 10);
  const usageStyle = tierStyle(usage.tier, theme);

  const lastEventText = state.lastEventAtMs != null
    ? `${Math.max(0, nowMs - state.lastEventAtMs)}ms`
    : "—";

  let col = 0;
  const write = (text: string, style = theme.textMuted) => {
    screen.writeString(row, col, text, style);
    col += text.length;
  };

  write(" ");
  write(`${state.model} `, theme.textPrimary);
  write(`${usage.bar} `, usageStyle);
  write(`${usage.label} ${Math.round(usage.percent)}% `, usageStyle);
  write("│ ");
  if (!isNarrow) {
    write(`tok:${tokens.totalTokens.toLocaleString()} `);
  }
  write(`$${costStr} `);
  write("│ ");
  write(`seq:${state.snapshot.lastSeq} `);
  write("│ ");
  write(`last:${lastEventText} `);
  if (state.planMode) {
    write("│ ");
    write("[PLAN] ", theme.warning);
  }

  // Right side: status message
  const rightText = ` ${state.statusMessage} `;
  const rightCol = Math.max(col, width - rightText.length);
  screen.writeString(row, rightCol, rightText, theme.accent);
}
