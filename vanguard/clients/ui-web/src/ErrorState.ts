import type { FailureDiagnostics } from "@aether/projections";

export type ErrorStateProps = {
  diagnostics: FailureDiagnostics;
  onRetry?: () => void;
  onDismiss?: () => void;
};

export function renderErrorState(props: ErrorStateProps): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-error-state";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px 16px;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-danger, #f38ba8);
    border-radius: 8px;
    margin: 8px 0;
    box-sizing: border-box;
  `;

  const topRow = document.createElement("div");
  topRow.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

  const titleEl = document.createElement("div");
  titleEl.style.cssText = "font-weight: 700; font-size: 13px; color: var(--aether-danger, #f38ba8);";
  titleEl.textContent = `✖ ${props.diagnostics.title}`;
  topRow.appendChild(titleEl);

  if (props.onDismiss) {
    const dismissBtn = document.createElement("button");
    dismissBtn.style.cssText = "background: transparent; border: none; color: var(--aether-text-muted, #6c7086); cursor: pointer; font-size: 14px;";
    dismissBtn.textContent = "✕";
    dismissBtn.onclick = props.onDismiss;
    topRow.appendChild(dismissBtn);
  }
  container.appendChild(topRow);

  const causeEl = document.createElement("div");
  causeEl.style.cssText = "font-size: 12px; color: var(--aether-text-primary, #cdd6f4);";
  causeEl.textContent = props.diagnostics.cause;
  container.appendChild(causeEl);

  if (props.diagnostics.recoveryAction) {
    const recEl = document.createElement("div");
    recEl.style.cssText = "font-size: 12px; color: var(--aether-text-muted, #6c7086); font-style: italic;";
    recEl.textContent = `💡 Action: ${props.diagnostics.recoveryAction}`;
    container.appendChild(recEl);
  }

  if (props.diagnostics.retryable && props.onRetry) {
    const btnRow = document.createElement("div");
    btnRow.style.cssText = "display: flex; margin-top: 4px;";

    const retryBtn = document.createElement("button");
    retryBtn.style.cssText = `
      padding: 4px 10px;
      background: var(--aether-danger, #f38ba8);
      color: var(--aether-bg, #11111b);
      border: none;
      border-radius: 4px;
      font-weight: 600;
      font-size: 11px;
      cursor: pointer;
    `;
    retryBtn.textContent = "Retry";
    retryBtn.onclick = props.onRetry;
    btnRow.appendChild(retryBtn);
    container.appendChild(btnRow);
  }

  return container;
}
