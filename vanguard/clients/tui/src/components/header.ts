import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens, STATUS_TAGS } from "../theme.js";
import type { TuiStoreState } from "../store.js";
import { truncateToWidth } from "../terminal/cell.js";

/** Shows the last `segments` path components instead of an unbounded absolute path. */
export function shortenPath(path: string, segments: number = 2): string {
  const parts = path.split("/").filter(Boolean);
  if (parts.length <= segments) return path;
  return "…/" + parts.slice(-segments).join("/");
}

export function renderHeader(
  screen: TerminalScreen,
  state: TuiStoreState,
  row: number = 0,
  theme: ThemeTokens = DEFAULT_THEME
): void {
  const width = screen.width;
  const isNarrow = width < 90;

  let statusTag: string = STATUS_TAGS.WAITING;
  let statusStyle = theme.textMuted;

  const status = state.snapshot.status;
  if (status === "running") {
    statusTag = STATUS_TAGS.RUNNING;
    statusStyle = theme.running;
  } else if (status === "awaiting_approval") {
    statusTag = STATUS_TAGS.APPROVAL;
    statusStyle = theme.warning;
  } else if (status === "satisfied") {
    statusTag = STATUS_TAGS.SATISFIED;
    statusStyle = theme.success;
  } else if (status === "failed") {
    statusTag = STATUS_TAGS.FAIL;
    statusStyle = theme.danger;
  } else if (status === "cancelled") {
    statusTag = STATUS_TAGS.CANCELLED;
    statusStyle = theme.textMuted;
  }

  // Draw background
  screen.writeString(row, 0, " ".repeat(width), theme.surfaceRaised);

  // Left: Brand & session identity
  const brand = " AETHER ";
  screen.writeString(row, 0, brand, theme.accent);

  // Right side is reserved first, so the left side always has a known,
  // non-overlapping budget to truncate into on narrow terminals.
  const planBadge = state.planMode ? "[PLAN] " : "";
  const rightPart = `${planBadge}${state.runId ? "run:" + state.runId.slice(0, 8) + " " : ""}${statusTag} `;
  const rightCol = Math.max(brand.length, width - rightPart.length);

  let leftOffset = brand.length;
  const shortRepo = shortenPath(state.workspacePath, isNarrow ? 1 : 2);
  const info = isNarrow
    ? `│ ${state.agentId} │ ${state.model} `
    : `│ agent:${state.agentId} │ repo:${shortRepo} │ model:${state.model} `;
  const availableForInfo = Math.max(0, rightCol - leftOffset - 1);
  screen.writeString(row, leftOffset, truncateToWidth(info, availableForInfo), theme.textMuted);
  leftOffset += Math.min(info.length, availableForInfo);

  if (planBadge) {
    screen.writeString(row, rightCol, planBadge, theme.warning);
    screen.writeString(row, rightCol + planBadge.length, rightPart.slice(planBadge.length), statusStyle);
  } else {
    screen.writeString(row, rightCol, rightPart, statusStyle);
  }

  // Bottom border line
  const borderLine = "─".repeat(width);
  screen.writeString(row + 1, 0, borderLine, theme.border);
}
