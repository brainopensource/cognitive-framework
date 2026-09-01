import type { FrontendConnectionState } from "@aether/contracts";
import { renderStatusBadge } from "./StatusBadge.js";

export type ConnectionStatusProps = {
  state: FrontendConnectionState;
  runtimeUrlOrSocket?: string;
  onReconnect?: () => void;
};

export function renderConnectionStatus(props: ConnectionStatusProps): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-connection-status";
  container.style.cssText = `
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--aether-text-muted, #6c7086);
  `;

  const badge = renderStatusBadge({ status: props.state, size: "sm" });
  container.appendChild(badge);

  if (props.state === "OFFLINE" || props.state === "DEGRADED") {
    if (props.onReconnect) {
      const btn = document.createElement("button");
      btn.style.cssText = `
        background: transparent;
        border: 1px solid var(--aether-border, #313244);
        color: var(--aether-accent, #89b4fa);
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 11px;
        cursor: pointer;
      `;
      btn.textContent = "Reconnect";
      btn.onclick = props.onReconnect;
      container.appendChild(btn);
    }
  }

  return container;
}
