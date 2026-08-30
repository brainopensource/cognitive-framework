export function renderDiffViewer(diffText: string): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-diff-viewer";
  container.style.cssText = `
    font-family: var(--aether-font-mono, monospace);
    font-size: 12px;
    line-height: 1.5;
    background: var(--aether-code-bg, #181825);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 6px;
    overflow-x: auto;
    padding: 8px 0;
    box-sizing: border-box;
  `;

  if (!diffText.trim()) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding: 8px 12px; color: var(--aether-text-muted, #6c7086);";
    empty.textContent = "No diff available.";
    container.appendChild(empty);
    return container;
  }

  const lines = diffText.split("\n");
  for (const line of lines) {
    const lineEl = document.createElement("div");
    lineEl.style.cssText = "padding: 0 12px; white-space: pre; display: flex;";

    if (line.startsWith("+") && !line.startsWith("+++")) {
      lineEl.style.backgroundColor = "var(--aether-diff-add-bg, #1e3a29)";
      lineEl.style.color = "var(--aether-diff-add-fg, #a6e3a1)";
    } else if (line.startsWith("-") && !line.startsWith("---")) {
      lineEl.style.backgroundColor = "var(--aether-diff-del-bg, #3e1e29)";
      lineEl.style.color = "var(--aether-diff-del-fg, #f38ba8)";
    } else if (line.startsWith("@@")) {
      lineEl.style.color = "var(--aether-diff-mod-fg, #89dceb)";
      lineEl.style.fontWeight = "bold";
    } else {
      lineEl.style.color = "var(--aether-text-primary, #cdd6f4)";
    }

    lineEl.textContent = line || " ";
    container.appendChild(lineEl);
  }

  return container;
}
