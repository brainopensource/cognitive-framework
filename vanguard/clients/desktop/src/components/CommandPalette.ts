import type { DesktopStore } from "../state/desktop-store.js";
import { formatDeepLink } from "@aether/projections";

export type PaletteCommand = {
  id: string;
  title: string;
  subtitle?: string;
  shortcut?: string;
  category: "Session" | "Execution" | "Navigation" | "System";
  available: boolean;
  execute: () => void;
};

export function renderCommandPalette(store: DesktopStore): HTMLElement | null {
  const state = store.get();
  if (!state.commandPaletteOpen) return null;

  const overlay = document.createElement("div");
  overlay.className = "aether-command-palette-overlay";
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: var(--aether-overlay, rgba(0, 0, 0, 0.6));
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-top: 15vh;
    z-index: 1000;
    user-select: none;
  `;

  const modal = document.createElement("div");
  modal.className = "aether-command-palette-modal";
  modal.style.cssText = `
    width: 560px;
    max-width: 90vw;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-border-strong, #45475a);
    border-radius: 8px;
    box-shadow: 0 16px 32px var(--aether-overlay, rgba(0,0,0,0.6));
    display: flex;
    flex-direction: column;
    overflow: hidden;
  `;

  // Search input
  const inputWrapper = document.createElement("div");
  inputWrapper.style.cssText = "padding: 12px 16px; border-bottom: 1px solid var(--aether-border, #313244); display: flex; align-items: center; gap: 8px;";

  const searchIcon = document.createElement("span");
  searchIcon.textContent = "🔍";
  inputWrapper.appendChild(searchIcon);

  const input = document.createElement("input");
  input.type = "text";
  input.placeholder = "Type a command or search… (Esc to close)";
  input.value = state.commandPaletteQuery;
  input.style.cssText = `
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--aether-text-primary, #cdd6f4);
    font-size: 14px;
    font-family: var(--aether-font-sans, inherit);
  `;
  inputWrapper.appendChild(input);
  modal.appendChild(inputWrapper);

  // Command catalog based on current state
  const commands: PaletteCommand[] = [
    {
      id: "new-chat",
      title: "New Conversation",
      subtitle: "Start a fresh agent session",
      shortcut: "⌘N",
      category: "Session",
      available: true,
      execute: () => store.newChat(),
    },
    {
      id: "focus-composer",
      title: "Focus Composer",
      subtitle: "Jump cursor to prompt input",
      shortcut: "⌘L",
      category: "Session",
      available: true,
      execute: () => {
        const ta = document.querySelector(".aether-composer textarea") as HTMLTextAreaElement;
        if (ta) ta.focus();
      },
    },
    {
      id: "switch-workspace",
      title: "Switch Workspace",
      subtitle: `Current: ${state.workspacePath}`,
      category: "Navigation",
      available: true,
      execute: () => {
        const chosen = prompt("Enter workspace path:", state.workspacePath);
        if (chosen) store.controller.selectWorkspace(chosen);
      },
    },
    {
      id: "switch-agent",
      title: "Switch Agent",
      subtitle: `Current: ${state.agentId}`,
      category: "Execution",
      available: true,
      execute: () => store.openForensicDrawer("settings"),
    },
    {
      id: "switch-workflow",
      title: "Switch Workflow",
      subtitle: `Current: ${state.workflowId}`,
      category: "Execution",
      available: true,
      execute: () => store.openForensicDrawer("settings"),
    },
    {
      id: "cancel-run",
      title: "Cancel Active Run",
      subtitle: "Abort current execution turn",
      shortcut: "Ctrl+C",
      category: "Execution",
      available: state.isStreaming,
      execute: () => store.cancelRun(),
    },
    {
      id: "checkpoint-run",
      title: "Create Checkpoint",
      subtitle: "Snapshot execution state for resumption",
      category: "Execution",
      available: Boolean(state.runId),
      execute: () => store.checkpointRun(),
    },
    {
      id: "resume-run",
      title: "Resume Run",
      subtitle: "Resume from last saved checkpoint",
      category: "Execution",
      available: Boolean(state.runId) && !state.isStreaming,
      execute: () => store.resumeRun(),
    },
    {
      id: "open-lab",
      title: "Open Forensic Workbench in Lab",
      subtitle: "Deep event and trace inspection",
      category: "Navigation",
      available: true,
      execute: () => {
        const link = formatDeepLink({ kind: "run", runId: state.runId || "latest" });
        alert(`Deep link to Lab: ${link}`);
      },
    },
    {
      id: "reconnect-runtime",
      title: "Reconnect Runtime",
      subtitle: "Reconnect to daemon socket/HTTP endpoint",
      category: "System",
      available: true,
      execute: () => store.controller.reconnectRuntime(),
    },
    {
      id: "settings",
      title: "Open Settings",
      subtitle: "Configure runtime, theme, and shortcuts",
      category: "System",
      available: true,
      execute: () => store.openForensicDrawer("settings"),
    },
    {
      id: "open-diffs",
      title: "Inspect Diffs",
      subtitle: "Open patch and diff viewer",
      category: "Navigation",
      available: true,
      execute: () => store.openForensicDrawer("diffs"),
    },
  ];

  const query = state.commandPaletteQuery.toLowerCase().trim();
  const filtered = commands.filter(
    (c) =>
      c.available &&
      (!query || c.title.toLowerCase().includes(query) || (c.subtitle && c.subtitle.toLowerCase().includes(query)))
  );

  // List of filtered commands
  const listContainer = document.createElement("div");
  listContainer.style.cssText = "max-height: 320px; overflow-y: auto; padding: 6px;";

  if (filtered.length === 0) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding: 16px; text-align: center; color: var(--aether-text-muted); font-size: 13px;";
    empty.textContent = "No matching commands.";
    listContainer.appendChild(empty);
  } else {
    for (const cmd of filtered) {
      const item = document.createElement("div");
      item.style.cssText = `
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: var(--aether-text-primary, #cdd6f4);
      `;
      item.onmouseenter = () => {
        item.style.background = "var(--aether-surface-raised, #252538)";
      };
      item.onmouseleave = () => {
        item.style.background = "transparent";
      };

      const leftCol = document.createElement("div");
      leftCol.innerHTML = `
        <div style="font-weight: 600;">${cmd.title}</div>
        ${cmd.subtitle ? `<div style="font-size: 11px; color: var(--aether-text-muted);">${cmd.subtitle}</div>` : ""}
      `;
      item.appendChild(leftCol);

      if (cmd.shortcut) {
        const kbd = document.createElement("span");
        kbd.style.cssText = "font-size: 11px; color: var(--aether-text-muted); background: var(--aether-surface-raised); padding: 2px 6px; border-radius: 4px;";
        kbd.textContent = cmd.shortcut;
        item.appendChild(kbd);
      }

      item.onclick = () => {
        store.toggleCommandPalette(false);
        cmd.execute();
      };
      listContainer.appendChild(item);
    }
  }

  modal.appendChild(listContainer);
  overlay.appendChild(modal);

  // Close overlay on background click or Esc
  overlay.onclick = (e) => {
    if (e.target === overlay) {
      store.toggleCommandPalette(false);
    }
  };

  input.onkeydown = (e) => {
    if (e.key === "Escape") {
      store.toggleCommandPalette(false);
    } else if (e.key === "Enter" && filtered.length > 0) {
      store.toggleCommandPalette(false);
      filtered[0]?.execute();
    }
  };

  input.oninput = () => {
    store.update((s) => ({ ...s, commandPaletteQuery: input.value }));
  };

  // Focus input automatically
  setTimeout(() => input.focus(), 10);

  return overlay;
}
