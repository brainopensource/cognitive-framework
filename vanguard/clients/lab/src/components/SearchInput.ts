export function renderSearchInput(options: {
  value: string;
  placeholder?: string;
  matchCount?: number;
  totalCount?: number;
  onSearch: (value: string) => void;
}): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-search-box-container";
  container.style.cssText = `
    position: relative;
    display: flex;
    align-items: center;
    background: var(--lab-bg-input);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-sm);
    padding: 3px 8px;
    gap: 6px;
    height: 28px;
  `;

  const icon = document.createElement("span");
  icon.style.cssText = "color: var(--lab-text-muted); font-size: 12px;";
  icon.textContent = "🔍";
  container.appendChild(icon);

  const input = document.createElement("input");
  input.type = "text";
  input.className = "aether-search-input";
  input.value = options.value;
  input.placeholder = options.placeholder ?? "Filter / Search (/)...";
  input.setAttribute("aria-label", "Search filter");
  input.style.cssText = `
    background: transparent;
    border: none;
    outline: none;
    color: var(--lab-text-primary);
    font-family: var(--lab-font-sans);
    font-size: 12px;
    width: 180px;
  `;

  let debounceTimer: any = null;
  input.oninput = () => {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      options.onSearch(input.value);
    }, 150);
  };

  container.appendChild(input);

  if (options.matchCount !== undefined && options.totalCount !== undefined) {
    const counter = document.createElement("span");
    counter.className = "aether-search-counter";
    counter.style.cssText = "font-size: 11px; font-family: var(--lab-font-mono); color: var(--lab-text-muted);";
    counter.textContent = `${options.matchCount}/${options.totalCount}`;
    container.appendChild(counter);
  }

  if (options.value) {
    const clearBtn = document.createElement("button");
    clearBtn.style.cssText = `
      background: none;
      border: none;
      color: var(--lab-text-muted);
      cursor: pointer;
      font-size: 11px;
      padding: 0 2px;
    `;
    clearBtn.textContent = "✕";
    clearBtn.title = "Clear search";
    clearBtn.onclick = () => {
      input.value = "";
      options.onSearch("");
    };
    container.appendChild(clearBtn);
  }

  return container;
}
