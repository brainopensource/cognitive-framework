import type { DesktopStore } from "../state/desktop-store.js";
import type { RuntimeClient } from "@aether/client";

export function renderComposer(store: DesktopStore, client?: RuntimeClient): HTMLElement {
  const state = store.get();
  const container = document.createElement("div");
  container.className = "aether-composer";
  container.style.cssText = `
    padding: 12px 16px 16px 16px;
    background: var(--aether-surface, #181825);
    border-top: 1px solid var(--aether-border, #313244);
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 8px;
  `;

  // Context Tag Bar above input
  const contextBar = document.createElement("div");
  contextBar.style.cssText = "display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: var(--aether-text-muted, #6c7086);";

  const contextTags = document.createElement("div");
  contextTags.style.cssText = "display: flex; align-items: center; gap: 8px;";

  const agentTag = document.createElement("span");
  agentTag.style.cssText = "background: var(--aether-surface-raised, #252538); padding: 2px 6px; border-radius: 4px; color: var(--aether-accent, #89b4fa); font-weight: 600;";
  agentTag.textContent = `Agent: ${state.agentId}`;
  contextTags.appendChild(agentTag);

  const wsTag = document.createElement("span");
  wsTag.style.cssText = "background: var(--aether-surface-raised, #252538); padding: 2px 6px; border-radius: 4px; color: var(--aether-text-secondary, #a6adc8); font-family: var(--aether-font-mono, monospace);";
  wsTag.textContent = `Dir: ${state.workspacePath}`;
  contextTags.appendChild(wsTag);

  contextBar.appendChild(contextTags);

  if (state.isStreaming) {
    const streamIndicator = document.createElement("span");
    streamIndicator.style.cssText = "color: var(--aether-running, #fab387); font-weight: 600;";
    streamIndicator.textContent = "● Streaming response…";
    contextBar.appendChild(streamIndicator);
  }

  container.appendChild(contextBar);

  // Main Input Box
  const box = document.createElement("div");
  box.style.cssText = `
    display: flex;
    background: var(--aether-bg, #11111b);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 8px;
    padding: 8px 12px;
    align-items: flex-end;
    box-sizing: border-box;
    transition: border-color 0.15s ease;
  `;

  const textarea = document.createElement("textarea");
  textarea.placeholder = state.isStreaming
    ? "Agent is responding… (Type next instruction)"
    : "Message AETHER… (Enter to send, Shift+Enter for newline)";
  textarea.value = state.composerText;
  textarea.style.cssText = `
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--aether-text-primary, #cdd6f4);
    font-family: var(--aether-font-sans, inherit);
    font-size: 14px;
    line-height: 1.4;
    resize: none;
    min-height: 36px;
    max-height: 180px;
  `;

  // Auto-resize
  const adjustHeight = () => {
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
  };

  textarea.oninput = () => {
    adjustHeight();
    store.controller.setConversationDraft(textarea.value);
    store.update((s) => ({ ...s, composerText: textarea.value }));
  };

  // Submit / Cancel Action Button
  const actionBtn = document.createElement("button");
  if (state.isStreaming) {
    actionBtn.style.cssText = `
      background: var(--aether-danger, #f38ba8);
      color: var(--aether-bg, #11111b);
      border: none;
      border-radius: 6px;
      padding: 6px 10px;
      margin-left: 8px;
      font-weight: 700;
      font-size: 12px;
      cursor: pointer;
    `;
    actionBtn.textContent = "■ Stop";
    actionBtn.onclick = () => {
      store.cancelRun();
    };
  } else {
    actionBtn.style.cssText = `
      background: var(--aether-accent, #89b4fa);
      color: var(--aether-bg, #11111b);
      border: none;
      border-radius: 6px;
      width: 32px;
      height: 32px;
      margin-left: 8px;
      font-weight: bold;
      font-size: 14px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    `;
    actionBtn.textContent = "▲";

    const handleSubmit = () => {
      const text = textarea.value.trim();
      if (!text) return;

      textarea.value = "";
      textarea.style.height = "36px";
      store.controller.setConversationDraft("");
      store.update((s) => ({ ...s, composerText: "" }));

      if (client) {
        store.startRun(client, text);
      } else {
        store.controller.startRun(text);
      }
    };

    actionBtn.onclick = handleSubmit;

    textarea.onkeydown = (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    };
  }

  box.appendChild(textarea);
  box.appendChild(actionBtn);
  container.appendChild(box);

  return container;
}
