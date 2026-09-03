import type { DesktopStore } from "../state/desktop-store.js";
import { renderSearchInput } from "@aether/ui-web";

export function renderSidebar(store: DesktopStore): HTMLElement {
  const state = store.get();
  const container = document.createElement("aside");
  container.className = "aether-sidebar";
  container.style.cssText = `
    width: 280px;
    height: 100%;
    background: var(--aether-surface, #181825);
    border-right: 1px solid var(--aether-border, #313244);
    display: ${state.sidebarOpen ? "flex" : "none"};
    flex-direction: column;
    box-sizing: border-box;
    user-select: none;
  `;

  // 1. Header / Brand
  const header = document.createElement("div");
  header.style.cssText = `
    padding: 14px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--aether-border, #313244);
  `;

  const brand = document.createElement("div");
  brand.style.cssText = "font-weight: 800; font-size: 15px; color: var(--aether-accent, #89b4fa); letter-spacing: 0.5px;";
  brand.textContent = "⊞ AETHER DESKTOP";
  header.appendChild(brand);

  container.appendChild(header);

  // 2. New Chat Action
  const actionContainer = document.createElement("div");
  actionContainer.style.cssText = "padding: 12px 16px 8px 16px;";

  const newChatBtn = document.createElement("button");
  newChatBtn.style.cssText = `
    width: 100%;
    padding: 8px 12px;
    background: var(--aether-accent, #89b4fa);
    color: var(--aether-bg, #11111b);
    border: none;
    border-radius: 6px;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
  `;
  newChatBtn.innerHTML = `<span>⊕ New Conversation</span> <span style="opacity: 0.7; font-size: 11px;">⌘N</span>`;
  newChatBtn.onclick = () => store.newChat();
  actionContainer.appendChild(newChatBtn);
  container.appendChild(actionContainer);

  // 3. Search Bar
  const searchWrapper = document.createElement("div");
  searchWrapper.style.cssText = "padding: 0 16px 8px 16px;";
  searchWrapper.appendChild(
    renderSearchInput({
      placeholder: "Search conversations…",
      initialValue: state.searchQuery,
      onSearch: (q: string) => {
        store.controller.setSearchQuery(q);
        store.update((s) => ({ ...s, searchQuery: q }));
      },
    })
  );
  container.appendChild(searchWrapper);

  // 4. Grouped Conversations List
  const listContainer = document.createElement("div");
  listContainer.style.cssText = "flex: 1; overflow-y: auto; padding: 0 8px;";

  const groups = store.controller.getGroupedConversations();
  if (groups.length === 0) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding: 24px 16px; text-align: center; color: var(--aether-text-muted, #6c7086); font-size: 12px;";
    empty.textContent = "No conversations found.";
    listContainer.appendChild(empty);
  } else {
    for (const group of groups) {
      const groupHeader = document.createElement("div");
      groupHeader.style.cssText = `
        padding: 10px 8px 4px 8px;
        font-size: 11px;
        font-weight: 700;
        color: var(--aether-text-muted, #6c7086);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      `;
      groupHeader.textContent = group.label;
      listContainer.appendChild(groupHeader);

      for (const session of group.conversations) {
        const item = document.createElement("div");
        const isActive = session.id === state.activeSessionId;

        item.style.cssText = `
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 10px;
          margin-bottom: 2px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 13px;
          color: ${isActive ? "var(--aether-text-primary, #cdd6f4)" : "var(--aether-text-secondary, #a6adc8)"};
          background: ${isActive ? "var(--aether-surface-raised, #252538)" : "transparent"};
          border: 1px solid ${isActive ? "var(--aether-border, #313244)" : "transparent"};
        `;

        const titleSpan = document.createElement("span");
        titleSpan.style.cssText = "white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1;";
        titleSpan.textContent = `• ${session.title}`;
        item.appendChild(titleSpan);

        // Actions: Rename / Delete
        const itemActions = document.createElement("div");
        itemActions.style.cssText = "display: none; gap: 4px; margin-left: 6px;";

        const editBtn = document.createElement("button");
        editBtn.style.cssText = "background: none; border: none; color: var(--aether-text-muted); cursor: pointer; font-size: 11px; padding: 0;";
        editBtn.textContent = "✏";
        editBtn.title = "Rename conversation";
        editBtn.onclick = (e) => {
          e.stopPropagation();
          const newTitle = prompt("Enter new title:", session.title);
          if (newTitle) store.renameSession(session.id, newTitle);
        };
        itemActions.appendChild(editBtn);

        const delBtn = document.createElement("button");
        delBtn.style.cssText = "background: none; border: none; color: var(--aether-danger); cursor: pointer; font-size: 11px; padding: 0;";
        delBtn.textContent = "✕";
        delBtn.title = "Delete conversation (retains runtime history)";
        delBtn.onclick = (e) => {
          e.stopPropagation();
          store.deleteSession(session.id);
        };
        itemActions.appendChild(delBtn);

        item.appendChild(itemActions);

        item.onmouseenter = () => {
          itemActions.style.display = "flex";
        };
        item.onmouseleave = () => {
          itemActions.style.display = "none";
        };

        item.onclick = () => store.selectSession(session.id);
        listContainer.appendChild(item);
      }
    }
  }

  container.appendChild(listContainer);

  // 5. Workspace Runs Link & Footer
  const footer = document.createElement("div");
  footer.style.cssText = `
    padding: 12px 16px;
    border-top: 1px solid var(--aether-border, #313244);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--aether-text-muted, #6c7086);
  `;

  const runsBtn = document.createElement("button");
  runsBtn.style.cssText = "background: none; border: none; color: var(--aether-text-secondary); cursor: pointer; padding: 0;";
  runsBtn.textContent = `📋 Runs (${state.runs.length})`;
  runsBtn.onclick = () => store.openForensicDrawer("runs");
  footer.appendChild(runsBtn);

  const settingsBtn = document.createElement("button");
  settingsBtn.style.cssText = "background: none; border: none; color: var(--aether-text-secondary); cursor: pointer; padding: 0;";
  settingsBtn.textContent = "⚙ Settings";
  settingsBtn.onclick = () => store.openForensicDrawer("settings");
  footer.appendChild(settingsBtn);

  container.appendChild(footer);
  return container;
}
