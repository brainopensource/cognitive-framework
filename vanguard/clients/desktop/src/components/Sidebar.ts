import type { DesktopStore } from "../state/desktop-store.js";

export function renderSidebar(store: DesktopStore): HTMLElement {
  const container = document.createElement("aside");
  container.className = "aether-sidebar";
  container.style.cssText = `
    width: 260px;
    height: 100%;
    background: var(--aether-bg-sidebar);
    border-right: 1px solid var(--aether-border);
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
  `;

  // Header / Brand
  const brand = document.createElement("div");
  brand.style.cssText = "padding: 16px; font-weight: bold; font-size: 16px; color: var(--aether-accent);";
  brand.textContent = "⊞ AETHER";
  container.appendChild(brand);

  // New Chat Button
  const newChatBtn = document.createElement("button");
  newChatBtn.style.cssText = `
    margin: 0 16px 12px 16px;
    padding: 8px 12px;
    background: var(--aether-accent);
    color: var(--aether-bg);
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    text-align: left;
  `;
  newChatBtn.textContent = "⊕ New Chat";
  newChatBtn.onclick = () => store.newChat();
  container.appendChild(newChatBtn);

  // Search Input
  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.placeholder = "🔍 Search chats...";
  searchInput.style.cssText = `
    margin: 0 16px 12px 16px;
    padding: 6px 10px;
    background: var(--aether-bg-input);
    color: var(--aether-text-primary);
    border: 1px solid var(--aether-border);
    border-radius: 6px;
    font-size: 13px;
    outline: none;
  `;
  searchInput.oninput = (e) => {
    store.update((s) => ({ ...s, searchQuery: (e.target as HTMLInputElement).value }));
  };
  container.appendChild(searchInput);

  // Sessions List container
  const listContainer = document.createElement("div");
  listContainer.style.cssText = "flex: 1; overflow-y: auto; padding: 0 8px;";

  const groups = store.getGroupedSessions();
  for (const group of groups) {
    const groupHeader = document.createElement("div");
    groupHeader.style.cssText = "padding: 8px 8px 4px 8px; font-size: 11px; font-weight: 600; color: var(--aether-text-muted); text-transform: uppercase;";
    groupHeader.textContent = group.label;
    listContainer.appendChild(groupHeader);

    for (const session of group.sessions) {
      const item = document.createElement("div");
      const isActive = session.sessionId === store.get().activeSessionId;
      item.style.cssText = `
        padding: 8px;
        margin-bottom: 2px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: ${isActive ? "var(--aether-text-primary)" : "var(--aether-text-muted)"};
        background: ${isActive ? "var(--aether-bg-card-hover)" : "transparent"};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      `;
      item.textContent = `• ${session.title}`;
      item.onclick = () => store.selectSession(session.sessionId);
      listContainer.appendChild(item);
    }
  }

  container.appendChild(listContainer);

  // Footer / Settings
  const footer = document.createElement("div");
  footer.style.cssText = "padding: 12px 16px; border-top: 1px solid var(--aether-border); font-size: 13px; color: var(--aether-text-muted);";
  footer.textContent = "⚙ Settings  │  👤 Developer";
  container.appendChild(footer);

  return container;
}
