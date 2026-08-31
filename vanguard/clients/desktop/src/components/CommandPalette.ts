import type { DesktopStore } from "../state/desktop-store.js";

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
        store.bridge.openDirectoryDialog().then((dir) => {
          if (dir) store.controller.selectWorkspace(dir);
        });
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
      id: "change-provider",
      title: "Configure Providers & Models",
      subtitle: `Current: ${state.selectedProviderId} (${state.model})`,
      category: "Execution",
      available: true,
      execute: () => {
        store.openForensicDrawer("settings");
        store.update((s) => ({ ...s, activeSettingsTab: "providers" }));
      },
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
      execute: () => store.openInLab(),
    },
    {
      id: "copy-cli",
      title: "Copy CLI Command",
      subtitle: "Copy `vg run inspect` for current run",
      category: "Navigation",
      available: Boolean(state.runId),
      execute: () => store.copyCliCommand(),
    },
    {
      id: "attach-tui",
      title: "Attach in TUI",
      subtitle: "Copy `vg run --attach` command",
      category: "Navigation",
      available: Boolean(state.runId),
      execute: () => store.attachInTui(),
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
      subtitle: "Open patch and multi-file diff viewer",
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
        padding: 8px 12px;
        border-radius: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: pointer;
        transition: background 0.1s ease;
      `;
      item.onmouseenter = () => {
        item.style.background = "var(--aether-surface-raised, #252538)";
      };
      item.onmouseleave = () => {
        item.style.background = "transparent";
      };

      const left = document.createElement("div");
      left.style.cssText = "display: flex; flex-direction: column; gap: 2px;";

      const titleSpan = document.createElement("span");
      titleSpan.style.cssText = "font-size: 13px; font-weight: 600; color: var(--aether-text-primary, #cdd6f4);";
      titleSpan.textContent = cmd.title;
      left.appendChild(titleSpan);

      if (cmd.subtitle) {
        const subSpan = document.createElement("span");
        subSpan.style.cssText = "font-size: 11px; color: var(--aether-text-muted, #6c7086);";
        subSpan.textContent = cmd.subtitle;
        left.appendChild(subSpan);
      }
      item.appendChild(left);

      if (cmd.shortcut) {
        const sc = document.createElement("kbd");
        sc.style.cssText = `
          background: var(--aether-bg, #11111b);
          border: 1px solid var(--aether-border, #313244);
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 10px;
          color: var(--aether-text-muted, #6c7086);
        `;
        sc.textContent = cmd.shortcut;
        item.appendChild(sc);
      }

      item.onclick = () => {
        cmd.execute();
        store.toggleCommandPalette(false);
      };

      listContainer.appendChild(item);
    }
  }

  modal.appendChild(listContainer);
  overlay.appendChild(modal);

  // Close on outside click
  overlay.onclick = (e) => {
    if (e.target === overlay) {
      store.toggleCommandPalette(false);
    }
  };

  // Keyboard navigation & search input listener
  input.oninput = () => {
    store.update((s) => ({ ...s, commandPaletteQuery: input.value }));
  };

  setTimeout(() => input.focus(), 0);

  return overlay;
}
