import type { DesktopStore, ForensicTab } from "../state/desktop-store.js";
import { renderDiffViewer } from "./DiffViewer.js";

export function renderForensicDrawer(store: DesktopStore): HTMLElement | null {
  const state = store.get();
  if (!state.forensicDrawerOpen) return null;

  const drawer = document.createElement("aside");
  drawer.className = "aether-forensic-drawer";
  drawer.style.cssText = `
    width: 420px;
    height: 100%;
    background: var(--aether-bg-sidebar);
    border-left: 1px solid var(--aether-border);
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
  `;

  // Header & Close Button
  const header = document.createElement("div");
  header.style.cssText = "display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--aether-border);";

  const title = document.createElement("div");
  title.style.cssText = "font-weight: 600; color: var(--aether-text-primary);";
  title.textContent = "🔍 Forensic Drawer";
  header.appendChild(title);

  const closeBtn = document.createElement("button");
  closeBtn.style.cssText = "background: none; border: none; color: var(--aether-text-muted); cursor: pointer; font-size: 16px;";
  closeBtn.textContent = "✕";
  closeBtn.onclick = () => store.closeForensicDrawer();
  header.appendChild(closeBtn);

  drawer.appendChild(header);

  // Tab switcher
  const tabs = document.createElement("div");
  tabs.style.cssText = "display: flex; border-bottom: 1px solid var(--aether-border);";

  const tabList: Array<{ id: ForensicTab; label: string }> = [
    { id: "diffs", label: "Diffs" },
    { id: "evidence", label: "Evidence" },
    { id: "artifacts", label: "Artifacts" },
  ];

  for (const t of tabList) {
    const tabBtn = document.createElement("button");
    const isActive = state.activeForensicTab === t.id;
    tabBtn.style.cssText = `
      flex: 1;
      padding: 8px;
      background: ${isActive ? "var(--aether-bg-card)" : "transparent"};
      color: ${isActive ? "var(--aether-accent)" : "var(--aether-text-muted)"};
      border: none;
      border-bottom: 2px solid ${isActive ? "var(--aether-accent)" : "transparent"};
      font-weight: 500;
      cursor: pointer;
      font-size: 13px;
    `;
    tabBtn.textContent = t.label;
    tabBtn.onclick = () => store.openForensicDrawer(t.id);
    tabs.appendChild(tabBtn);
  }
  drawer.appendChild(tabs);

  // Content pane
  const content = document.createElement("div");
  content.style.cssText = "flex: 1; overflow-y: auto; padding: 12px;";

  if (state.activeForensicTab === "diffs") {
    if (state.activeDiffText) {
      content.appendChild(renderDiffViewer(state.activeDiffText));
    } else {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted); font-size: 13px;";
      empty.textContent = "No active diff selected.";
      content.appendChild(empty);
    }
  } else if (state.activeForensicTab === "evidence") {
    const claims = state.evidenceGrid.claims;
    if (claims.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted); font-size: 13px;";
      empty.textContent = "No verified claims recorded in current session.";
      content.appendChild(empty);
    } else {
      for (const claim of claims) {
        const item = document.createElement("div");
        item.style.cssText = "padding: 8px; margin-bottom: 6px; background: var(--aether-bg-card); border-radius: 6px; font-size: 12px;";
        item.textContent = `✔ [${claim.claimType}] ${claim.statement}`;
        content.appendChild(item);
      }
    }
  } else if (state.activeForensicTab === "artifacts") {
    const artifacts = state.evidenceGrid.artifacts;
    if (artifacts.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted); font-size: 13px;";
      empty.textContent = "No artifacts generated yet.";
      content.appendChild(empty);
    } else {
      for (const art of artifacts) {
        const item = document.createElement("div");
        item.style.cssText = "padding: 8px; margin-bottom: 6px; background: var(--aether-bg-card); border-radius: 6px; font-size: 12px; font-family: var(--aether-font-mono);";
        item.textContent = `📦 ${art.path ?? art.digest.slice(0, 16) + "…"}`;
        content.appendChild(item);
      }
    }
  }

  drawer.appendChild(content);
  return drawer;
}
