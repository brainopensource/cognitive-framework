export function renderDiffViewer(diffText: string): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-diff-viewer";
  container.style.cssText = `
    font-family: var(--aether-font-mono);
    font-size: 12px;
    line-height: 1.5;
    background: var(--aether-bg);
    border: 1px solid var(--aether-border);
    border-radius: 6px;
    overflow-x: auto;
    padding: 8px 0;
  `;

  const lines = diffText.split("\n");
  for (const line of lines) {
    const row = document.createElement("div");
    row.style.cssText = "padding: 0 12px; white-space: pre;";

    if (line.startsWith("+") && !line.startsWith("+++")) {
      row.style.background = "var(--aether-diff-add-bg)";
      row.style.color = "var(--aether-diff-add-fg)";
    } else if (line.startsWith("-") && !line.startsWith("---")) {
      row.style.background = "var(--aether-diff-del-bg)";
      row.style.color = "var(--aether-diff-del-fg)";
    } else if (line.startsWith("@@")) {
      row.style.color = "var(--aether-accent)";
      row.style.fontWeight = "600";
    } else {
      row.style.color = "var(--aether-text-muted)";
    }

    row.textContent = line;
    container.appendChild(row);
  }

  return container;
}
