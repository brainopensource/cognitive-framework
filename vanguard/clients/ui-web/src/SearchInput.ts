export type SearchInputProps = {
  /** Stable identity for focus restoration across re-renders. */
  focusKey?: string;
  placeholder?: string;
  initialValue?: string;
  onSearch: (query: string) => void;
};

export function renderSearchInput(props: SearchInputProps): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-search-input-wrapper";
  container.style.cssText = `
    display: flex;
    align-items: center;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 6px;
    padding: 4px 8px;
    box-sizing: border-box;
  `;

  const icon = document.createElement("span");
  icon.style.cssText = "color: var(--aether-text-muted, #6c7086); margin-right: 6px; font-size: 12px;";
  icon.textContent = "🔍";
  container.appendChild(icon);

  const input = document.createElement("input");
  // Hosts that rebuild their tree on every state change use this to restore
  // focus and caret after the swap; without it, typing here loses the caret
  // exactly as the composer did.
  if (props.focusKey) input.setAttribute("data-focus-key", props.focusKey);
  input.type = "text";
  input.placeholder = props.placeholder ?? "Search…";
  input.value = props.initialValue ?? "";
  input.style.cssText = `
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--aether-text-primary, #cdd6f4);
    font-size: 13px;
    font-family: var(--aether-font-sans, inherit);
  `;

  const clearBtn = document.createElement("button");
  clearBtn.style.cssText = `
    background: transparent;
    border: none;
    color: var(--aether-text-muted, #6c7086);
    cursor: pointer;
    font-size: 11px;
    padding: 0 4px;
    display: ${props.initialValue ? "block" : "none"};
  `;
  clearBtn.textContent = "✕";
  clearBtn.onclick = () => {
    input.value = "";
    if (clearBtn.style) clearBtn.style.display = "none";
    props.onSearch("");
  };

  const handleInput = () => {
    if (clearBtn && clearBtn.style) {
      clearBtn.style.display = input.value ? "block" : "none";
    }
    props.onSearch(input.value);
  };

  input.oninput = handleInput;
  if (typeof input.addEventListener === "function") {
    input.addEventListener("input", handleInput);
  }

  container.appendChild(input);
  container.appendChild(clearBtn);

  return container;
}
