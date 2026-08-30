import type { WorkflowExecutionView } from "@aether/contracts";

export function renderMultiAgentStatusBar(view: WorkflowExecutionView): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-multi-agent-bar";
  container.style.cssText = `
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    background: var(--aether-surface-raised, #1e1e2e);
    border-bottom: 1px solid var(--aether-border, #313244);
    font-size: 11px;
    color: var(--aether-text-primary, #cdd6f4);
  `;

  const left = document.createElement("div");
  left.style.cssText = "display: flex; align-items: center; gap: 8px;";
  left.innerHTML = `
    <span style="font-weight: 700; color: var(--aether-accent, #89b4fa);">Workflow: ${view.title}</span>
    <span style="color: var(--aether-text-muted, #6c7086); font-family: var(--aether-font-mono, monospace);">[Stage: ${view.currentStage}]</span>
  `;
  container.appendChild(left);

  const participantsList = document.createElement("div");
  participantsList.style.cssText = "display: flex; align-items: center; gap: 6px;";

  for (const p of view.participants) {
    const chip = document.createElement("div");
    const isActive = p.status === "active";
    chip.style.cssText = `
      padding: 2px 6px;
      border-radius: 4px;
      background: ${isActive ? "var(--aether-surface, #181825)" : "transparent"};
      border: 1px solid ${isActive ? "var(--aether-accent, #89b4fa)" : "var(--aether-border, #313244)"};
      font-size: 10px;
      display: flex;
      align-items: center;
      gap: 4px;
    `;
    chip.innerHTML = `
      <span style="color: ${isActive ? "var(--aether-success, #a6e3a1)" : "var(--aether-text-muted, #6c7086)"}; font-weight: bold;">●</span>
      <span>${p.role} (${p.agentId})</span>
    `;
    participantsList.appendChild(chip);
  }
  container.appendChild(participantsList);

  return container;
}
