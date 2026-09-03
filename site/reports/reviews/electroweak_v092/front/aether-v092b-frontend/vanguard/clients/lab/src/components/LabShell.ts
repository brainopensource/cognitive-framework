import type { LabStore } from "../state/lab-store.js";
import type { RuntimeClient } from "@aether/client";
import { renderWorkbenchNavigation } from "./WorkbenchNavigation.js";
import { renderRunSelector } from "./RunSelector.js";
import { renderConnectionStatus } from "./ConnectionStatus.js";
import { renderInspectorDrawer } from "./InspectorDrawer.js";
import { WorkbenchRegistry } from "./workbenches/workbench-registry.js";
import { formatSeq } from "../util/formatting.js";

export function renderLabShell(
  store: LabStore,
  registry: WorkbenchRegistry,
  client?: RuntimeClient
): HTMLElement {
  const shell = document.createElement("div");
  shell.className = "aether-lab-shell";
  shell.style.cssText = `
    display: flex;
    flex-direction: column;
    width: 100vw;
    height: 100vh;
    background: var(--lab-bg);
    color: var(--lab-text-primary);
    font-family: var(--lab-font-sans);
    overflow: hidden;
  `;

  const state = store.get();
  const sel = store.selection.get();

  // 1. TOP HEADER BAR
  const topBar = document.createElement("header");
  topBar.className = "aether-lab-topbar";
  topBar.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 16px;
    height: 44px;
    background: var(--lab-bg-surface);
    border-bottom: 1px solid var(--lab-border);
    user-select: none;
    z-index: 20;
    gap: 16px;
  `;

  // Top Bar Left: Brand & Run Selector
  const leftGroup = document.createElement("div");
  leftGroup.style.cssText = "display: flex; align-items: center; gap: 16px;";

  const brand = document.createElement("div");
  brand.style.cssText = "display: flex; align-items: center; gap: 8px;";
  brand.innerHTML = `
    <span style="font-weight: 800; font-size: 13px; letter-spacing: 0.5px; color: var(--lab-text-primary);">AETHER LAB</span>
    <span style="font-size: 10px; font-family: var(--lab-font-mono); color: var(--lab-text-muted); background: var(--lab-bg-panel); padding: 1px 5px; border-radius: 3px; border: 1px solid var(--lab-border);">ELECTROWEAK</span>
  `;
  leftGroup.appendChild(brand);

  const runSelector = renderRunSelector(store, client);
  leftGroup.appendChild(runSelector);

  topBar.appendChild(leftGroup);

  // Top Bar Right: Seq indicator, Connection, Mode & Inspector button
  const rightGroup = document.createElement("div");
  rightGroup.style.cssText = "display: flex; align-items: center; gap: 12px;";

  // Sequence Indicator
  const lastSeq = state.snapshot.lastSeq || "0";
  const seqIndicator = document.createElement("div");
  seqIndicator.style.cssText = `
    display: flex;
    align-items: center;
    gap: 4px;
    font-family: var(--lab-font-mono);
    font-size: 11px;
    color: var(--lab-text-secondary);
    background: var(--lab-bg-panel);
    padding: 2px 8px;
    border-radius: var(--lab-radius-sm);
    border: 1px solid var(--lab-border);
  `;
  seqIndicator.innerHTML = `<span>SEQ:</span> <strong style="color: var(--lab-accent);">${formatSeq(lastSeq)}</strong>`;
  rightGroup.appendChild(seqIndicator);

  // Connection status badge
  rightGroup.appendChild(renderConnectionStatus(store));

  // Inspector toggle button
  const toggleInspectorBtn = document.createElement("button");
  toggleInspectorBtn.style.cssText = `
    display: flex;
    align-items: center;
    gap: 4px;
    background: ${sel.inspectorOpen ? "var(--lab-accent-muted)" : "var(--lab-bg-panel)"};
    color: ${sel.inspectorOpen ? "var(--lab-accent)" : "var(--lab-text-secondary)"};
    border: 1px solid ${sel.inspectorOpen ? "var(--lab-accent)" : "var(--lab-border)"};
    padding: 4px 8px;
    border-radius: var(--lab-radius-sm);
    font-size: 11px;
    font-weight: 500;
    cursor: pointer;
  `;
  toggleInspectorBtn.innerHTML = `<span>🔍 Inspector</span> <kbd style="font-size: 9px; opacity: 0.7;">i</kbd>`;
  toggleInspectorBtn.onclick = () => store.selection.toggleInspector();
  rightGroup.appendChild(toggleInspectorBtn);

  topBar.appendChild(rightGroup);
  shell.appendChild(topBar);

  // 2. MAIN WORKBENCH BODY (Navigation + Active Workbench + Inspector)
  const body = document.createElement("div");
  body.className = "aether-lab-body";
  body.style.cssText = `
    flex: 1;
    display: flex;
    overflow: hidden;
    position: relative;
  `;

  // Left Sidebar Navigation
  body.appendChild(renderWorkbenchNavigation(store));

  // Center Workbench Area
  const workbenchContainer = document.createElement("main");
  workbenchContainer.className = "aether-active-workbench-container";
  workbenchContainer.style.cssText = `
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
  `;
  workbenchContainer.appendChild(registry.render(sel.activeWorkbench, store, client));
  body.appendChild(workbenchContainer);

  // Right Inspector Drawer
  const inspector = renderInspectorDrawer(store, client);
  if (inspector) {
    body.appendChild(inspector);
  }

  shell.appendChild(body);

  return shell;
}
