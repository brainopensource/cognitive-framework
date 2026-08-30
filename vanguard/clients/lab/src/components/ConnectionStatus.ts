import type { LabStore } from "../state/lab-store.js";
import { renderConnectionStatusBadge } from "./StatusBadge.js";

export function renderConnectionStatus(store: LabStore): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-connection-status-panel";
  container.style.cssText = `
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const state = store.get();
  const badge = renderConnectionStatusBadge(state.connectionState);
  container.appendChild(badge);

  const transportLabel = document.createElement("span");
  transportLabel.style.cssText = `
    font-size: 11px;
    font-family: var(--lab-font-mono);
    color: var(--lab-text-muted);
  `;
  transportLabel.textContent = `${state.transportType.toUpperCase()} (${state.socketPathOrUrl})`;
  container.appendChild(transportLabel);

  return container;
}
