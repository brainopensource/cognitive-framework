import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import type { ConnectionState } from "../store.js";
import { truncateToWidth } from "../terminal/cell.js";

export function renderConnectionBanner(
  screen: TerminalScreen,
  connectionState: ConnectionState,
  row: number,
  theme: ThemeTokens = DEFAULT_THEME
): number {
  if (connectionState === "connected") return 0;

  const width = screen.width;
  let text = "";
  let style = theme.warning;

  if (connectionState === "connecting") {
    text = " ⚙ Connecting to AETHER Runtime daemon... ";
    style = theme.running;
  } else if (connectionState === "reconnecting") {
    text = " ⚠ Connection interrupted. Reconnecting with CAS cursor resume... ";
    style = theme.warning;
  } else if (connectionState === "unavailable" || connectionState === "disconnected") {
    text = " ✖ Runtime daemon offline at socket path. Commands queued or running offline. ";
    style = theme.danger;
  }

  screen.writeString(row, 0, truncateToWidth(text.padEnd(width, " "), width), style);
  return 1;
}
