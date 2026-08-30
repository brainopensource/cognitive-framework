import type { DesktopStore } from "../state/desktop-store.js";
import type { ConversationTurn } from "@aether/projections";

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
  `;

  const state = store.get();
  if (state.turns.length === 0) {
    const welcome = document.createElement("div");
    welcome.style.cssText = "margin: auto; text-align: center; color: var(--aether-text-muted); max-width: 400px;";
    welcome.innerHTML = `
      <h3 style="color: var(--aether-text-primary); margin-bottom: 8px;">AETHER Desktop Workspace</h3>
      <p style="font-size: 14px;">Select a workspace directory and send a prompt to begin an autonomous agent session.</p>
    `;
    container.appendChild(welcome);
    return container;
  }

  for (const turn of state.turns) {
    const turnEl = renderTurnCard(turn, store);
    container.appendChild(turnEl);
  }

  return container;
}

function renderTurnCard(turn: ConversationTurn, store: DesktopStore): HTMLElement {
  const card = document.createElement("div");
  const isUser = turn.speaker === "user";

  card.style.cssText = `
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-self: ${isUser ? "flex-end" : "flex-start"};
    max-width: ${isUser ? "75%" : "85%"};
  `;

  // Speaker label
  const label = document.createElement("div");
  label.style.cssText = `
    font-size: 11px;
    font-weight: 600;
    color: ${isUser ? "var(--aether-accent)" : "var(--aether-text-muted)"};
  `;
  label.textContent = isUser ? "User" : "AETHER Assistant";
  card.appendChild(label);

  // Message Bubble
  const bubble = document.createElement("div");
  bubble.style.cssText = `
    padding: 12px 16px;
    border-radius: 8px;
    background: ${isUser ? "var(--aether-accent)" : "var(--aether-bg-card)"};
    color: ${isUser ? "var(--aether-bg)" : "var(--aether-text-primary)"};
    font-size: 14px;
    line-height: 1.5;
    white-space: pre-wrap;
    border: ${isUser ? "none" : "1px solid var(--aether-border)"};
  `;
  bubble.textContent = turn.text || "(Executing turn...)";
  card.appendChild(bubble);

  // Activity Cards (for assistant turn)
  if (!isUser && turn.activityCards.length > 0) {
    const activityContainer = document.createElement("div");
    activityContainer.style.cssText = "display: flex; flex-direction: column; gap: 4px; margin-top: 4px;";

    for (const act of turn.activityCards) {
      const actCard = document.createElement("div");
      actCard.style.cssText = `
        padding: 6px 10px;
        background: var(--aether-bg-input);
        border: 1px solid var(--aether-border);
        border-radius: 6px;
        font-size: 12px;
        color: var(--aether-text-muted);
        display: flex;
        justify-content: space-between;
        cursor: pointer;
      `;
      actCard.textContent = `▸ ${act.title}`;

      if (act.diff) {
        actCard.onclick = () => store.openForensicDrawer("diffs", act.diff);
      }
      activityContainer.appendChild(actCard);
    }
    card.appendChild(activityContainer);
  }

  // Verdict badge
  if (turn.verdict) {
    const verdictEl = document.createElement("div");
    const isSatisfied = turn.verdict === "satisfied" || turn.verdict === "1";
    verdictEl.style.cssText = `
      font-size: 12px;
      font-weight: 600;
      color: ${isSatisfied ? "var(--aether-success)" : "var(--aether-danger)"};
    `;
    verdictEl.textContent = `Verdict: ${turn.verdict.toUpperCase()}`;
    card.appendChild(verdictEl);
  }

  return card;
}
