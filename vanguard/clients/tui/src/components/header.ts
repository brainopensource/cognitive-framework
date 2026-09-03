import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens, STATUS_TAGS } from "../theme.js";
import type { TuiStoreState } from "../store.js";
import { padToWidth, truncateToWidth } from "../terminal/cell.js";

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

  let leftOffset = brand.length;
  if (!isNarrow) {
    const info = `│ agent:${state.agentId} │ repo:${state.workspacePath} │ model:${state.model} `;
    screen.writeString(row, leftOffset, info, theme.textMuted);
    leftOffset += info.length;
  } else {
    const compactInfo = `│ ${state.agentId} │ ${state.model} `;
    screen.writeString(row, leftOffset, compactInfo, theme.textMuted);
    leftOffset += compactInfo.length;
  }

  // Right: Run ID & Status Tag
  const planBadge = state.planMode ? "[PLAN] " : "";
  const rightPart = `${planBadge}${state.runId ? "run:" + state.runId.slice(0, 8) + " " : ""}${statusTag} `;
  const rightCol = Math.max(leftOffset, width - rightPart.length);
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
