import type { DesktopStore } from "../state/desktop-store.js";
import type { TauriNativeBridge } from "../bridge/tauri-bridge.js";
import { renderConnectionStatus } from "@aether/ui-web";

export function renderTopBar(store: DesktopStore, bridge?: TauriNativeBridge): HTMLElement {
  const bar = document.createElement("header");
  bar.className = "aether-topbar";
  bar.style.cssText = `
    height: 52px;
    background: var(--aether-surface, #181825);
    border-bottom: 1px solid var(--aether-border, #313244);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    box-sizing: border-box;
    gap: 12px;
    user-select: none;
  `;

  const state = store.get();

  // Left Section: Workspace Breadcrumb & Agent / Workflow Selectors
  const left = document.createElement("div");
  left.style.cssText = "display: flex; align-items: center; gap: 10px; font-size: 13px; min-width: 0;";

  // Sidebar toggle
  const sidebarBtn = document.createElement("button");
  sidebarBtn.style.cssText = `
    background: transparent;
    border: 1px solid var(--aether-border, #313244);
    color: var(--aether-text-muted, #6c7086);
    border-radius: 4px;
    padding: 4px 8px;
    cursor: pointer;
    font-size: 12px;
  `;
  sidebarBtn.textContent = state.sidebarOpen ? "◀" : "▶";
  sidebarBtn.onclick = () => store.toggleSidebar();
  left.appendChild(sidebarBtn);

  // Workspace Selector
  const wsWrapper = document.createElement("div");
  wsWrapper.style.cssText = "display: flex; align-items: center; gap: 4px; max-width: 240px;";

  const wsIcon = document.createElement("span");
  wsIcon.textContent = "📁";
  wsWrapper.appendChild(wsIcon);

  const wsBtn = document.createElement("button");
  wsBtn.style.cssText = `
    background: none;
    border: none;
    color: var(--aether-text-primary, #cdd6f4);
    font-weight: 600;
    cursor: pointer;
    padding: 0;
    font-size: 13px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  `;
  wsBtn.textContent = state.workspacePath || "Select Workspace";
  wsBtn.title = "Click to select workspace directory";
  wsBtn.onclick = async () => {
    if (bridge) {
      const chosen = await bridge.openDirectoryDialog();
      if (chosen) store.controller.selectWorkspace(chosen);
    } else {
      const chosen = prompt("Enter workspace directory path:", state.workspacePath);
      if (chosen) store.controller.selectWorkspace(chosen);
    }
  };
  wsWrapper.appendChild(wsBtn);
  left.appendChild(wsWrapper);

  const sep1 = document.createElement("span");
  sep1.style.cssText = "color: var(--aether-border, #313244);";
  sep1.textContent = "│";
  left.appendChild(sep1);

  // Agent Selector Dropdown
  const agentSelect = document.createElement("select");
  agentSelect.style.cssText = `
    background: var(--aether-surface-raised, #252538);
    color: var(--aether-accent, #89b4fa);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    font-weight: 600;
    outline: none;
    cursor: pointer;
  `;
  for (const agent of store.controller.getState().availableAgents) {
    const opt = document.createElement("option");
    opt.value = agent.id;
    opt.textContent = `Agent: ${agent.name}`;
    opt.selected = agent.id === state.agentId;
    agentSelect.appendChild(opt);
  }
  agentSelect.onchange = () => {
    store.controller.selectAgent(agentSelect.value);
  };
  left.appendChild(agentSelect);

  // Workflow Selector Dropdown
  const wfSelect = document.createElement("select");
  wfSelect.style.cssText = `
    background: var(--aether-surface-raised, #252538);
    color: var(--aether-info, #89dceb);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
    outline: none;
    cursor: pointer;
  `;
  for (const wf of store.controller.getState().availableWorkflows) {
    const opt = document.createElement("option");
    opt.value = wf.id;
    opt.textContent = `Workflow: ${wf.name}`;
    opt.selected = wf.id === state.workflowId;
    wfSelect.appendChild(opt);
  }
  wfSelect.onchange = () => {
    store.controller.selectWorkflow(wfSelect.value);
  };
  left.appendChild(wfSelect);

  bar.appendChild(left);

  // Right Section: Connection Status, Command Palette trigger, Forensic Drawer Toggle, Layout switcher
  const right = document.createElement("div");
  right.style.cssText = "display: flex; align-items: center; gap: 10px;";

  // Command palette shortcut hint button
  const kbdBtn = document.createElement("button");
  kbdBtn.style.cssText = `
    background: var(--aether-surface-raised, #252538);
    border: 1px solid var(--aether-border, #313244);
    color: var(--aether-text-muted, #6c7086);
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
  `;
  kbdBtn.innerHTML = `<span>⌘K</span> <span>Palette</span>`;
  kbdBtn.onclick = () => store.toggleCommandPalette();
  right.appendChild(kbdBtn);

  // Connection status
  const connState = (state.connectionState.toUpperCase() as any);
  const connEl = renderConnectionStatus({
    state: connState,
    onReconnect: () => store.controller.reconnectRuntime(),
  });
  right.appendChild(connEl);

  // Layout mode switcher
  const layoutBtn = document.createElement("button");
  layoutBtn.style.cssText = `
    background: var(--aether-surface-raised, #252538);
    border: 1px solid var(--aether-border, #313244);
    color: var(--aether-text-primary, #cdd6f4);
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    cursor: pointer;
  `;
  layoutBtn.textContent = state.layoutMode;
  layoutBtn.title = "Toggle layout mode (Standard / Wide / Compact)";
  layoutBtn.onclick = () => {
    const next = state.layoutMode === "STANDARD" ? "WIDE" : state.layoutMode === "WIDE" ? "COMPACT" : "STANDARD";
    store.setLayoutMode(next);
  };
  right.appendChild(layoutBtn);

  // Forensic Drawer Toggle
  const forensicBtn = document.createElement("button");
  forensicBtn.style.cssText = `
    background: ${state.forensicDrawerOpen ? "var(--aether-accent, #89b4fa)" : "var(--aether-surface-raised, #252538)"};
    color: ${state.forensicDrawerOpen ? "var(--aether-bg, #11111b)" : "var(--aether-text-primary, #cdd6f4)"};
    border: 1px solid var(--aether-border, #313244);
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  `;
  forensicBtn.textContent = "🔍 Forensic";
  forensicBtn.onclick = () => {
    if (state.forensicDrawerOpen) {
      store.closeForensicDrawer();
    } else {
      store.openForensicDrawer("diffs");
    }
  };
  right.appendChild(forensicBtn);

  bar.appendChild(right);
  return bar;
}
