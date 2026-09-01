import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import type { TuiStoreState } from "../store.js";
import { truncateToWidth } from "../terminal/cell.js";

export function renderApprovalDeck(
  screen: TerminalScreen,
  state: TuiStoreState,
  startRow: number,
  theme: ThemeTokens = DEFAULT_THEME
): number {
  const pending = state.pendingApproval;
  if (!pending) return 0;

  const width = screen.width;
  const isFocused = state.focus === "approval";
  const borderStyle = isFocused ? theme.borderActive : theme.warning;

  // Header separator
  screen.writeString(startRow, 0, "─".repeat(width), borderStyle);

  // Challenge Title
  const title = ` ⚠ APPROVAL REQUIRED: Action '${pending.approvalId}' `;
  screen.writeString(startRow + 1, 0, truncateToWidth(title, width), theme.approval);

  // Challenge context / digests
  if (pending.argsDigest) {
    const digests = `   Digests: args=${pending.argsDigest.slice(0, 16)}… descriptor=${pending.descriptorDigest.slice(0, 16)}…`;
    screen.writeString(startRow + 2, 0, truncateToWidth(digests, width), theme.textMuted);
  }

  // Quick Action Buttons
  const actions = "   [y] Approve & Sign (Ed25519)   [d] View Full Diff   [n] Reject Action   [q] Cancel Run";
  screen.writeString(startRow + 3, 0, truncateToWidth(actions, width), theme.textBright);

  // Bottom separator
  screen.writeString(startRow + 4, 0, "─".repeat(width), borderStyle);

  return 5;
}
