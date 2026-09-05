import type { TerminalScreen } from "../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../theme.js";
import type { ConversationTurn } from "@aether/projections";
import { renderToolCard } from "./cards/tool-card.js";
import { renderDiffCard } from "./cards/diff-card.js";
import { cardStyle } from "./cards/card-style.js";

export function renderTurn(
  screen: TerminalScreen,
  startRow: number,
  turn: ConversationTurn,
  expandedCardIds: Set<string>,
  theme: ThemeTokens = DEFAULT_THEME
): number {
  let curRow = startRow;
  if (curRow >= screen.height) return 0;

  // Speaker & Timestamp Header
  const speakerLabel = turn.speaker === "user" ? "[User]" : turn.speaker === "agent" ? "[AETHER]" : "[System]";
  const headerStyle = turn.speaker === "user" ? theme.textBright : theme.accent;
  const timeStr = turn.timestamp ? turn.timestamp.slice(11, 19) : "";

  screen.writeString(curRow, 0, `${speakerLabel} ${timeStr}`.trim(), headerStyle);
  curRow++;

  // Message Text
  if (turn.text) {
    const lines = turn.text.split("\n");
    for (const line of lines) {
      if (curRow >= screen.height) break;
      screen.writeString(curRow, 2, line, theme.textPrimary);
      curRow++;
    }
  }

  // Activity Cards
  for (const card of turn.activityCards) {
    if (curRow >= screen.height) break;
    const isExpanded = expandedCardIds.has(card.id);

    if (card.kind === "diff" || card.diff) {
      const lines = renderDiffCard(screen, curRow, card.title, card.diff ?? "", isExpanded, theme);
      curRow += lines;
    } else {
      // Prefix the glyph for the card's semantic class and colour the row by
      // status, so a failed effect, a pending approval and a cost line are
      // distinguishable at a glance in a long transcript.
      const { glyph, style } = cardStyle(card, theme);
      const lines = renderToolCard(
        screen,
        curRow,
        `${glyph} ${card.title}`,
        card.details,
        card.durationMs,
        isExpanded,
        theme,
        style
      );
      curRow += lines;
    }
  }

  // Verdict if present
  if (turn.verdict) {
    if (curRow < screen.height) {
      const isSatisfied = turn.verdict === "satisfied" || turn.verdict === "1";
      const style = isSatisfied ? theme.success : theme.danger;
      screen.writeString(curRow, 2, `Verdict: ${turn.verdict.toUpperCase()}`, style);
      curRow++;
    }
  }

  curRow++; // Spacing between turns
  return curRow - startRow;
}
