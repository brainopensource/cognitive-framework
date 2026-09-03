import type { ConversationActivityCard } from "@aether/projections";
import { DEFAULT_THEME, type ThemeTokens, type SemanticStyle } from "../../theme.js";

/**
 * Glyph and colour for one activity card.
 *
 * The transcript folds fifteen semantic card classes (`ConversationActivityCardKind`)
 * that used to render identically. Status wins over class for colour -- an
 * operator scanning a long run needs failures and pending approvals to stand
 * out regardless of which subsystem produced them -- while the glyph keeps the
 * class legible.
 */
export type CardStyle = {
  glyph: string;
  style: SemanticStyle;
};

const GLYPHS: Record<string, string> = {
  tool: "⚙",
  diff: "±",
  verification: "✓",
  approval: "⚠",
  plan: "☰",
  reflection: "✎",
  checkpoint: "⎇",
  child: "⑂",
  budget: "$",
  context: "⧉",
  capability: "🔑",
  artifact: "📄",
  plugin: "⊕",
  alarm: "🔔",
  conflict: "⚡",
};

export function cardStyle(
  card: Pick<ConversationActivityCard, "kind" | "status">,
  theme: ThemeTokens = DEFAULT_THEME
): CardStyle {
  const glyph = GLYPHS[card.kind] ?? "•";

  let style: SemanticStyle;
  switch (card.status) {
    case "failed":
      style = theme.danger;
      break;
    case "rejected":
      style = theme.caution;
      break;
    case "pending":
      style = theme.approval;
      break;
    case "running":
      style = theme.running;
      break;
    case "completed":
      style = card.kind === "verification" ? theme.success : theme.accent;
      break;
    default:
      style = theme.textMuted;
      break;
  }

  return { glyph, style };
}
