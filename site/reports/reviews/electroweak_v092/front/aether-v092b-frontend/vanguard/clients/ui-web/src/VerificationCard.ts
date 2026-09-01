import type { VerificationSummary } from "@aether/contracts";
import { renderStatusBadge } from "./StatusBadge.js";
import { renderCodeBlock } from "./CodeBlock.js";

export function renderVerificationCard(summary: VerificationSummary): HTMLElement {
  const card = document.createElement("div");
  card.className = "aether-verification-card";
  card.style.cssText = `
    padding: 10px 14px;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 12px;
  `;

  const topRow = document.createElement("div");
  topRow.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

  const titleRow = document.createElement("div");
  titleRow.style.cssText = "font-weight: 700; display: flex; align-items: center; gap: 8px; color: var(--aether-text-primary, #cdd6f4);";
  const icon = summary.kind === "tests" ? "🧪" : summary.kind === "lint" ? "🧹" : summary.kind === "typecheck" ? "📐" : "🔨";
  titleRow.innerHTML = `<span>${icon} ${summary.kind.toUpperCase()} VERIFICATION</span>`;
  topRow.appendChild(titleRow);

  const badge = renderStatusBadge({
    status: summary.status === "pass" ? "satisfied" : summary.status === "fail" ? "failed" : "pending",
    label: summary.status.toUpperCase(),
    size: "sm",
  });
  topRow.appendChild(badge);
  card.appendChild(topRow);

  // Metrics summary
  const detailsRow = document.createElement("div");
  detailsRow.style.cssText = "display: flex; gap: 12px; font-size: 11px; color: var(--aether-text-muted, #6c7086);";
  const parts: string[] = [];
  if (typeof summary.passedCount === "number") parts.push(`Passed: ${summary.passedCount}`);
  if (typeof summary.failedCount === "number") parts.push(`Failed: ${summary.failedCount}`);
  if (typeof summary.durationMs === "number") parts.push(`Duration: ${summary.durationMs}ms`);
  if (summary.command) parts.push(`Command: ${summary.command}`);
  detailsRow.textContent = parts.join(" • ");
  card.appendChild(detailsRow);

  // Expandable output
  if (summary.importantOutput) {
    const details = document.createElement("details");
    details.style.cssText = "margin-top: 4px; font-size: 11px;";
    const summaryEl = document.createElement("summary");
    summaryEl.style.cssText = "cursor: pointer; color: var(--aether-accent, #89b4fa); font-weight: 600;";
    summaryEl.textContent = "View Output Logs";
    details.appendChild(summaryEl);

    const logBox = renderCodeBlock({ code: summary.importantOutput });
    details.appendChild(logBox);
    card.appendChild(details);
  }

  return card;
}
