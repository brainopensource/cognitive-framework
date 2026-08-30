import type { DesktopStore } from "../state/desktop-store.js";
import type { RuntimeClient } from "@aether/client";

export function renderComposer(store: DesktopStore, client?: RuntimeClient): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-composer";
  container.style.cssText = `
    padding: 16px;
    background: var(--aether-bg);
    border-top: 1px solid var(--aether-border);
    box-sizing: border-box;
  `;

  const box = document.createElement("div");
  box.style.cssText = `
    display: flex;
    background: var(--aether-bg-input);
    border: 1px solid var(--aether-border);
    border-radius: 8px;
    padding: 8px 12px;
    align-items: flex-end;
  `;

  const textarea = document.createElement("textarea");
  textarea.placeholder = "Message AETHER... (Shift+Enter for newline)";
  textarea.style.cssText = `
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--aether-text-primary);
    font-family: var(--aether-font-sans);
    font-size: 14px;
    resize: none;
    min-height: 24px;
    max-height: 160px;
  `;

  const submitBtn = document.createElement("button");
  submitBtn.style.cssText = `
    background: var(--aether-accent);
    color: var(--aether-bg);
    border: none;
    border-radius: 6px;
    width: 32px;
    height: 32px;
    margin-left: 8px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  `;
  submitBtn.textContent = "▲";

  const handleSubmit = () => {
    const text = textarea.value.trim();
    if (!text) return;
    textarea.value = "";
    if (client) {
      store.startRun(client, text);
    }
  };

  submitBtn.onclick = handleSubmit;

  textarea.onkeydown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  box.appendChild(textarea);
  box.appendChild(submitBtn);
  container.appendChild(box);

  return container;
}
