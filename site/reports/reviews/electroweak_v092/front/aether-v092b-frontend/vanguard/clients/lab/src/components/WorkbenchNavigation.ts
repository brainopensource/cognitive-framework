import type { LabStore } from "../state/lab-store.js";
import type { WorkbenchId } from "../state/selection-model.js";

export function renderWorkbenchNavigation(store: LabStore): HTMLElement {
  const nav = document.createElement("nav");
  nav.className = "aether-workbench-nav";
  nav.setAttribute("role", "tablist");
  nav.setAttribute("aria-label", "Workbenches");
  nav.style.cssText = `
    width: 200px;
    min-width: 180px;
    background: var(--lab-bg-surface);
    border-right: 1px solid var(--lab-border);
    display: flex;
    flex-direction: column;
    padding: 12px 8px;
    gap: 4px;
    user-select: none;
  `;

  const state = store.get();
  const sel = store.selection.get();

  const items: Array<{
    id: WorkbenchId;
    key: string;
    icon: string;
    label: string;
    badge?: string | number;
  }> = [
    {
      id: "runs",
      key: "1",
      icon: "⚡",
      label: "Runs",
      badge: state.runs.length > 0 ? state.runs.length : undefined,
    },
    {
      id: "events",
      key: "2",
      icon: "📜",
      label: "Events",
      badge: state.events.length > 0 ? state.events.length : undefined,
    },
    {
      id: "trace",
      key: "3",
      icon: "🕸",
      label: "Trace",
      badge: state.traceGraph.nodes.length > 0 ? state.traceGraph.nodes.length : undefined,
    },
    {
      id: "artifacts",
      key: "4",
      icon: "📦",
      label: "Artifacts & Evidence",
      badge: state.snapshot.artifacts.length + state.evidenceGrid.claims.length || undefined,
    },
    {
      id: "context",
      key: "5",
      icon: "🧠",
      label: "Context",
      badge: state.snapshot.tokens.totalTokens > 0 ? `${Math.round(state.snapshot.tokens.totalTokens / 1000)}k` : undefined,
    },
    {
      id: "system",
      key: "6",
      icon: "⚙",
      label: "System",
      badge: state.connectionState === "connected" ? "✓" : "!",
    },
  ];

  for (const item of items) {
    const isActive = sel.activeWorkbench === item.id;
    const btn = document.createElement("button");
    btn.setAttribute("role", "tab");
    btn.setAttribute("aria-selected", isActive ? "true" : "false");
    btn.style.cssText = `
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding: 8px 10px;
      border: 1px solid ${isActive ? "var(--lab-border-active)" : "transparent"};
      border-radius: var(--lab-radius-sm);
      background: ${isActive ? "var(--lab-bg-active)" : "transparent"};
      color: ${isActive ? "var(--lab-text-primary)" : "var(--lab-text-secondary)"};
      font-family: var(--lab-font-sans);
      font-size: 12px;
      font-weight: ${isActive ? "600" : "400"};
      cursor: pointer;
      text-align: left;
      transition: background 0.1s ease;
    `;

    btn.onmouseenter = () => {
      if (!isActive) btn.style.background = "var(--lab-bg-hover)";
    };
    btn.onmouseleave = () => {
      if (!isActive) btn.style.background = "transparent";
    };

    const left = document.createElement("div");
    left.style.cssText = "display: flex; align-items: center; gap: 8px;";

    const icon = document.createElement("span");
    icon.textContent = item.icon;
    left.appendChild(icon);

    const text = document.createElement("span");
    text.textContent = item.label;
    left.appendChild(text);

    btn.appendChild(left);

    const right = document.createElement("div");
    right.style.cssText = "display: flex; align-items: center; gap: 6px;";

    if (item.badge !== undefined) {
      const badge = document.createElement("span");
      badge.style.cssText = `
        font-family: var(--lab-font-mono);
        font-size: 10px;
        padding: 1px 5px;
        border-radius: 8px;
        background: ${isActive ? "var(--lab-accent-muted)" : "var(--lab-bg-panel)"};
        color: ${isActive ? "var(--lab-accent)" : "var(--lab-text-muted)"};
      `;
      badge.textContent = String(item.badge);
      right.appendChild(badge);
    }

    const keyHint = document.createElement("span");
    keyHint.style.cssText = "font-size: 10px; color: var(--lab-text-muted); font-family: var(--lab-font-mono); opacity: 0.6;";
    keyHint.textContent = item.key;
    right.appendChild(keyHint);

    btn.appendChild(right);

    btn.onclick = () => {
      store.selection.setWorkbench(item.id);
    };

    nav.appendChild(btn);
  }

  // Footer: Keyboard help trigger
  const spacer = document.createElement("div");
  spacer.style.flex = "1";
  nav.appendChild(spacer);

  const helpBtn = document.createElement("button");
  helpBtn.style.cssText = `
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    padding: 6px;
    background: var(--lab-bg-panel);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-sm);
    color: var(--lab-text-secondary);
    font-size: 11px;
    cursor: pointer;
  `;
  helpBtn.innerHTML = `<span>⌨ Shortcuts</span> <kbd style="font-size: 10px; background: var(--lab-bg-input); padding: 1px 4px; border-radius: 2px;">?</kbd>`;
  helpBtn.onclick = () => {
    // Dispatch '?' key to show help dialog
    window.dispatchEvent(new KeyboardEvent("keydown", { key: "?" }));
  };
  nav.appendChild(helpBtn);

  return nav;
}
