import type { StartupReadiness, ReadinessStep } from "@aether/contracts";

export type StartupReadinessModalProps = {
  readiness: StartupReadiness;
  onAction: (step: ReadinessStep) => void;
  onDismiss?: () => void;
};

export function renderStartupReadinessModal(props: StartupReadinessModalProps): HTMLElement {
  const overlay = document.createElement("div");
  overlay.className = "aether-readiness-overlay";
  overlay.style.cssText = `
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(17, 17, 27, 0.85);
    backdrop-filter: blur(4px);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
  `;

  const modal = document.createElement("div");
  modal.className = "aether-readiness-modal";
  modal.style.cssText = `
    width: 520px;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    display: flex;
    flex-direction: column;
    gap: 16px;
    font-family: var(--aether-font-sans, sans-serif);
  `;

  const header = document.createElement("div");
  header.innerHTML = `
    <div style="font-size: 18px; font-weight: 700; color: var(--aether-text-primary, #cdd6f4); margin-bottom: 4px;">
      🚀 AETHER Startup Readiness
    </div>
    <div style="font-size: 12px; color: var(--aether-text-muted, #6c7086);">
      Complete required configuration to begin autonomous workspace sessions.
    </div>
  `;
  modal.appendChild(header);

  // Steps List
  const stepsContainer = document.createElement("div");
  stepsContainer.style.cssText = "display: flex; flex-direction: column; gap: 8px;";

  for (const step of props.readiness.steps) {
    const stepRow = document.createElement("div");
    const isReady = step.status === "ready";
    stepRow.style.cssText = `
      padding: 10px 12px;
      border-radius: 6px;
      background: ${isReady ? "var(--aether-bg, #11111b)" : "var(--aether-surface-raised, #252538)"};
      border: 1px solid ${isReady ? "var(--aether-border, #313244)" : "var(--aether-accent, #89b4fa)"};
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
    `;

    const leftCol = document.createElement("div");
    leftCol.style.cssText = "display: flex; flex-direction: column; gap: 2px;";
    leftCol.innerHTML = `
      <div style="font-weight: 700; color: ${isReady ? "var(--aether-success, #a6e3a1)" : "var(--aether-text-primary, #cdd6f4)"};">
        ${isReady ? "✓" : "○"} ${step.title}
      </div>
      <div style="font-size: 11px; color: var(--aether-text-muted, #6c7086);">${step.description}</div>
    `;
    stepRow.appendChild(leftCol);

    if (!isReady && step.actionLabel) {
      const btn = document.createElement("button");
      btn.style.cssText = `
        padding: 4px 10px;
        background: var(--aether-accent, #89b4fa);
        color: var(--aether-bg, #11111b);
        border: none;
        border-radius: 4px;
        font-weight: 700;
        cursor: pointer;
        font-size: 11px;
      `;
      btn.textContent = step.actionLabel;
      btn.onclick = () => props.onAction(step);
      stepRow.appendChild(btn);
    }

    stepsContainer.appendChild(stepRow);
  }
  modal.appendChild(stepsContainer);

  overlay.appendChild(modal);
  return overlay;
}
