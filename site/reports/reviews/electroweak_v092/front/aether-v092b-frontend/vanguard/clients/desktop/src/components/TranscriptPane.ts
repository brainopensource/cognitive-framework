import type { DesktopStore } from "../state/desktop-store.js";
import type { ConversationTurn, ConversationActivityCard } from "@aether/projections";
import {
  renderEmptyState,
  renderStatusBadge,
  renderDiffViewer,
  renderCodeBlock,
  renderArtifactReference,
  renderVerificationCard,
  renderResearchCitationCard,
} from "@aether/ui-web";

export function renderTranscriptPane(store: DesktopStore): HTMLElement {
  const container = document.createElement("main");
  container.className = "aether-transcript-pane";
  container.style.cssText = `
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    box-sizing: border-box;
    position: relative;
    scroll-behavior: smooth;
  `;

  const state = store.get();

  // Empty state if no conversation turns
  if (state.turns.length === 0 && state.activities.length === 0) {
    const empty = renderEmptyState({
      icon: "⊞",
      title: "AETHER Autonomous Workspace",
      description: "Select your target repository and start an agent session by entering an instruction below.",
      actionLabel: "Quickstart Session",
      onAction: () => {
        store.setDraft("Analyze repository architecture and verify test status");
      },
    });
    container.appendChild(empty);
    return container;
  }

  // Render Conversation Turns
  for (const turn of state.turns) {
    const turnEl = renderTurnCard(turn, store);
    container.appendChild(turnEl);
  }

  // Floating "Jump to Latest / Unread Content" button if manual scroll mode
  if (state.hasUnreadContent) {
    const jumpBtn = document.createElement("button");
    jumpBtn.style.cssText = `
      position: sticky;
      bottom: 12px;
      align-self: center;
      padding: 6px 14px;
      background: var(--aether-accent, #89b4fa);
      color: var(--aether-bg, #11111b);
      border: none;
      border-radius: 20px;
      font-weight: 700;
      font-size: 12px;
      cursor: pointer;
      box-shadow: 0 4px 12px var(--aether-overlay, rgba(0,0,0,0.4));
      z-index: 10;
    `;
    jumpBtn.textContent = "↓ New activity below";
    jumpBtn.onclick = () => {
      container.scrollTop = container.scrollHeight;
      store.update((s) => ({ ...s, hasUnreadContent: false, scrollFollowStream: true }));
    };
    container.appendChild(jumpBtn);
  }

  // Auto-follow latest if enabled
  if (state.scrollFollowStream) {
    setTimeout(() => {
      container.scrollTop = container.scrollHeight;
    }, 0);
  }

  return container;
}

function renderTurnCard(turn: ConversationTurn, store: DesktopStore): HTMLElement {
  const state = store.get();
  const density = state.settings.appearance?.density ?? "comfortable";
  const card = document.createElement("div");
  const isUser = turn.speaker === "user";

  card.style.cssText = `
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-self: ${isUser ? "flex-end" : "flex-start"};
    max-width: ${isUser ? "75%" : "90%"};
    width: ${isUser ? "auto" : "100%"};
  `;

  // Speaker label & Timestamp
  const labelRow = document.createElement("div");
  labelRow.style.cssText = `
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 700;
    color: ${isUser ? "var(--aether-accent, #89b4fa)" : "var(--aether-text-muted, #6c7086)"};
  `;
  labelRow.textContent = isUser ? "User" : "AETHER Assistant";
  card.appendChild(labelRow);

  // Message Bubble
  if (turn.text) {
    const bubble = document.createElement("div");
    bubble.style.cssText = `
      padding: 12px 16px;
      border-radius: 8px;
      background: ${isUser ? "var(--aether-accent, #89b4fa)" : "var(--aether-surface, #181825)"};
      color: ${isUser ? "var(--aether-bg, #11111b)" : "var(--aether-text-primary, #cdd6f4)"};
      font-size: 14px;
      line-height: 1.5;
      white-space: pre-wrap;
      border: ${isUser ? "none" : "1px solid var(--aether-border, #313244)"};
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      position: relative;
    `;
    bubble.textContent = turn.text;

    // Safe copy button
    const copyBtn = document.createElement("button");
    copyBtn.style.cssText = `
      position: absolute;
      top: 6px;
      right: 6px;
      background: transparent;
      border: none;
      color: ${isUser ? "var(--aether-bg, #11111b)" : "var(--aether-text-muted, #6c7086)"};
      font-size: 11px;
      cursor: pointer;
      opacity: 0.6;
    `;
    copyBtn.textContent = "📋";
    copyBtn.title = "Copy message text";
    copyBtn.onclick = () => {
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        navigator.clipboard.writeText(turn.text);
      }
    };
    bubble.appendChild(copyBtn);
    card.appendChild(bubble);
  }

  // Structured Activity Cards (for assistant turn)
  if (!isUser && turn.activityCards.length > 0) {
    const activityContainer = document.createElement("div");
    activityContainer.style.cssText = "display: flex; flex-direction: column; gap: 6px; margin-top: 4px;";

    for (const act of turn.activityCards) {
      // If minimal/compact density, skip minor tool exploration unless verification/diff/approval
      if (density === "compact" && act.kind === "tool") {
        continue;
      }

      if (act.kind === "verification") {
        const verCard = renderVerificationCard({
          id: act.id,
          kind: "tests",
          status: act.status === "completed" ? "pass" : "fail",
          importantOutput: act.details,
          timestamp: new Date().toISOString(),
        });
        activityContainer.appendChild(verCard);
        continue;
      }

      const actCard = document.createElement("div");
      actCard.style.cssText = `
        padding: 8px 12px;
        background: var(--aether-surface, #181825);
        border: 1px solid var(--aether-border, #313244);
        border-radius: 6px;
        font-size: 12px;
        color: var(--aether-text-primary, #cdd6f4);
        display: flex;
        flex-direction: column;
        gap: 4px;
      `;

      const headerRow = document.createElement("div");
      headerRow.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

      const titleSpan = document.createElement("span");
      titleSpan.style.fontWeight = "600";
      titleSpan.textContent = `▸ ${act.title}`;
      headerRow.appendChild(titleSpan);

      const badge = renderStatusBadge({ status: act.status, size: "sm" });
      headerRow.appendChild(badge);
      actCard.appendChild(headerRow);

      if (act.details) {
        const detailsEl = document.createElement("div");
        detailsEl.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 11px;";
        detailsEl.textContent = act.details;
        actCard.appendChild(detailsEl);
      }

      if (act.diff) {
        const diffBtn = document.createElement("button");
        diffBtn.style.cssText = `
          align-self: flex-start;
          background: var(--aether-surface-raised, #252538);
          border: 1px solid var(--aether-border, #313244);
          color: var(--aether-accent, #89b4fa);
          border-radius: 4px;
          padding: 2px 8px;
          font-size: 11px;
          cursor: pointer;
          margin-top: 4px;
        `;
        diffBtn.textContent = "🔍 View Full Diff in Forensic Drawer";
        diffBtn.onclick = () => store.openForensicDrawer("diffs", act.diff);
        actCard.appendChild(diffBtn);
      }

      activityContainer.appendChild(actCard);
    }
    card.appendChild(activityContainer);
  }

  // Verdict Produced
  if (turn.verdict) {
    const verdictEl = document.createElement("div");
    const isSatisfied = turn.verdict === "satisfied" || turn.verdict === "1";
    verdictEl.style.cssText = `
      margin-top: 4px;
      font-size: 12px;
      font-weight: 700;
      color: ${isSatisfied ? "var(--aether-success, #a6e3a1)" : "var(--aether-danger, #f38ba8)"};
    `;
    verdictEl.textContent = `Verdict: ${turn.verdict.toUpperCase()}`;
    card.appendChild(verdictEl);
  }

  return card;
}
