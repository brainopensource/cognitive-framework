import type { DesktopStore } from "../state/desktop-store.js";
import type { TauriNativeBridge } from "../bridge/tauri-bridge.js";

export function renderTopBar(store: DesktopStore, bridge?: TauriNativeBridge): HTMLElement {
  const bar = document.createElement("header");
  bar.className = "aether-topbar";
  bar.style.cssText = `
    height: 48px;
    background: var(--aether-bg);
    border-bottom: 1px solid var(--aether-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    box-sizing: border-box;
  `;

  const state = store.get();

  // Left: Agent & Workspace selectors
  const left = document.createElement("div");
  left.style.cssText = "display: flex; align-items: center; gap: 12px; font-size: 13px;";

  const agentTag = document.createElement("span");
  agentTag.style.cssText = "color: var(--aether-text-primary); font-weight: 500;";
  agentTag.textContent = `Agent: ${state.agentId} ▾`;
  left.appendChild(agentTag);

  const sep = document.createElement("span");
  sep.style.cssText = "color: var(--aether-border);";
  sep.textContent = "│";
  left.appendChild(sep);

  const wsBtn = document.createElement("button");
  wsBtn.style.cssText = "background: none; border: none; color: var(--aether-text-muted); cursor: pointer; padding: 0;";
  wsBtn.textContent = `Workspace: ${state.workspacePath}`;
  wsBtn.onclick = async () => {
    if (bridge) {
      const chosen = await bridge.openDirectoryDialog();
      if (chosen) store.update((s) => ({ ...s, workspacePath: chosen }));
    }
  };
  left.appendChild(wsBtn);

  bar.appendChild(left);

  // Right: Run Status badge
  const right = document.createElement("div");
  right.style.cssText = "display: flex; align-items: center; gap: 8px;";

  const status = state.snapshot.status;
  const badge = document.createElement("span");
  badge.style.cssText = `
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    background: ${
      status === "running"
        ? "var(--aether-running)"
        : status === "awaiting_approval"
        ? "var(--aether-warning)"
        : status === "satisfied"
        ? "var(--aether-success)"
        : status === "failed"
        ? "var(--aether-danger)"
        : "var(--aether-bg-card)"
    };
    color: var(--aether-bg);
  `;
  badge.textContent = status;
  right.appendChild(badge);

  bar.appendChild(right);
  return bar;
}
