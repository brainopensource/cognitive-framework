export type CodeBlockProps = {
  code: string;
  language?: string;
  fileName?: string;
};

export function renderCodeBlock(props: CodeBlockProps): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-code-block";
  container.style.cssText = `
    background: var(--aether-code-bg, #181825);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 6px;
    font-family: var(--aether-font-mono, monospace);
    font-size: 12px;
    overflow: hidden;
    margin: 8px 0;
  `;

  // Header if fileName or language provided
  if (props.fileName || props.language) {
    const header = document.createElement("div");
    header.style.cssText = `
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 12px;
      background: var(--aether-surface, #1e1e2e);
      border-bottom: 1px solid var(--aether-border, #313244);
      font-size: 11px;
      color: var(--aether-text-muted, #6c7086);
    `;

    const title = document.createElement("span");
    title.textContent = props.fileName ?? (props.language ? props.language.toUpperCase() : "");
    header.appendChild(title);

    const copyBtn = document.createElement("button");
    copyBtn.style.cssText = `
      background: transparent;
      border: none;
      color: var(--aether-accent, #89b4fa);
      cursor: pointer;
      font-size: 11px;
      padding: 0;
    `;
    copyBtn.textContent = "Copy";
    copyBtn.onclick = () => {
      if (typeof navigator !== "undefined" && navigator.clipboard) {
        navigator.clipboard.writeText(props.code);
        copyBtn.textContent = "Copied!";
        setTimeout(() => {
          copyBtn.textContent = "Copy";
        }, 1500);
      }
    };
    header.appendChild(copyBtn);
    container.appendChild(header);
  }

  const pre = document.createElement("pre");
  pre.style.cssText = `
    margin: 0;
    padding: 10px 12px;
    overflow-x: auto;
    color: var(--aether-text-primary, #cdd6f4);
    line-height: 1.5;
    white-space: pre;
  `;
  pre.textContent = props.code;
  container.appendChild(pre);

  return container;
}
