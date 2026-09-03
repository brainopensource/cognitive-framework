import type { ThemeTokens } from "../theme.js";

export type UsageTier = "ok" | "warn" | "caution" | "critical";

export interface UsageBarResult {
  readonly percent: number;
  readonly tier: UsageTier;
  /** Accessibility text cue, always shown alongside color (PRD_AETHER_TUI.md §8.2). */
  readonly label: string;
  readonly bar: string;
}

/**
 * Four-tier context-usage indicator: green <50%, yellow <80%, orange <95%,
 * red >=95% (PRD_AETHER_TUI.md §status-footer). Every tier carries a
 * textual cue, not just a color, per the accessibility budget.
 */
export function computeUsageBar(usedTokens: number, contextWindowTokens: number, width: number = 10): UsageBarResult {
  const percent = contextWindowTokens > 0
    ? Math.max(0, Math.min(100, (usedTokens / contextWindowTokens) * 100))
    : 0;

  let tier: UsageTier;
  let label: string;
  if (percent >= 95) {
    tier = "critical";
    label = "[CRIT]";
  } else if (percent >= 80) {
    tier = "caution";
    label = "[HIGH]";
  } else if (percent >= 50) {
    tier = "warn";
    label = "[MED]";
  } else {
    tier = "ok";
    label = "[OK]";
  }

  const filled = Math.round((percent / 100) * width);
  const bar = "█".repeat(filled) + "░".repeat(Math.max(0, width - filled));

  return { percent, tier, label, bar };
}

export function tierStyle(tier: UsageTier, theme: ThemeTokens) {
  switch (tier) {
    case "ok":
      return theme.success;
    case "warn":
      return theme.warning;
    case "caution":
      return theme.caution;
    case "critical":
      return theme.danger;
  }
}
