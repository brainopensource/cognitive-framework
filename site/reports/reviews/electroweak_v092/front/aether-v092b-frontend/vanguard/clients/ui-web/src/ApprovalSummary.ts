import { renderDiffViewer } from "./DiffViewer.js";

export type ApprovalSummaryProps = {
  approvalId: string;
  action: string;
  target?: string;
  command?: string;
  diff?: string;
  argsDigest?: string;
  descriptorDigest?: string;
  riskContext?: string;
  expiresAt?: string;
  onApprove?: () => void;
  onReject?: () => void;
  onInspect?: () => void;
  onCancelRun?: () => void;
};

export function renderApprovalSummary(props: ApprovalSummaryProps): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-approval-summary";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 14px 16px;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-warning, #f9e2af);
    border-radius: 8px;
    box-sizing: border-box;
  `;

  // Header with Warning Tag
  const header = document.createElement("div");
  header.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

  const title = document.createElement("div");
  title.style.cssText = "font-weight: 700; font-size: 14px; color: var(--aether-warning, #f9e2af); display: flex; align-items: center; gap: 6px;";
  title.textContent = `⚠ APPROVAL REQUIRED: ${props.action}`;
  header.appendChild(title);

  if (props.expiresAt) {
    const exp = document.createElement("div");
    exp.style.cssText = "font-size: 11px; color: var(--aether-text-muted, #6c7086);";
    exp.textContent = `Expires: ${props.expiresAt}`;
    header.appendChild(exp);
  }
  container.appendChild(header);

  // Metadata details
  const meta = document.createElement("div");
  meta.style.cssText = "font-size: 12px; color: var(--aether-text-secondary, #a6adc8); display: flex; flex-direction: column; gap: 4px;";

  if (props.target) {
    const targetEl = document.createElement("div");
    targetEl.innerHTML = `<strong>Target:</strong> <code style="font-family: var(--aether-font-mono);">${props.target}</code>`;
    meta.appendChild(targetEl);
  }

  if (props.command) {
    const cmdEl = document.createElement("div");
    cmdEl.innerHTML = `<strong>Command:</strong> <code style="font-family: var(--aether-font-mono);">${props.command}</code>`;
    meta.appendChild(cmdEl);
  }

  if (props.argsDigest) {
    const digestEl = document.createElement("div");
    digestEl.style.cssText = "font-family: var(--aether-font-mono); font-size: 11px; color: var(--aether-text-muted);";
    digestEl.textContent = `Challenge Digest: ${props.argsDigest.slice(0, 32)}…`;
    meta.appendChild(digestEl);
  }

  if (props.riskContext) {
    const riskEl = document.createElement("div");
    riskEl.style.cssText = "color: var(--aether-warning); font-size: 11px;";
    riskEl.textContent = `Risk: ${props.riskContext}`;
    meta.appendChild(riskEl);
  }

  container.appendChild(meta);

  // Diff display if present
  if (props.diff) {
    const diffContainer = document.createElement("div");
    diffContainer.style.maxHeight = "200px";
    diffContainer.style.overflowY = "auto";
    diffContainer.appendChild(renderDiffViewer(props.diff));
    container.appendChild(diffContainer);
  }

  // Action Buttons
  const btnRow = document.createElement("div");
  btnRow.style.cssText = "display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px;";

  if (props.onApprove) {
    const appBtn = document.createElement("button");
    appBtn.style.cssText = `
      padding: 6px 14px;
      background: var(--aether-success, #a6e3a1);
      color: var(--aether-bg, #11111b);
      border: none;
      border-radius: 4px;
      font-weight: 600;
      font-size: 12px;
      cursor: pointer;
    `;
    appBtn.textContent = "✔ Approve & Sign (Ed25519)";
    appBtn.onclick = props.onApprove;
    btnRow.appendChild(appBtn);
  }

  if (props.onReject) {
    const rejBtn = document.createElement("button");
    rejBtn.style.cssText = `
      padding: 6px 14px;
      background: var(--aether-danger, #f38ba8);
      color: var(--aether-bg, #11111b);
      border: none;
      border-radius: 4px;
      font-weight: 600;
      font-size: 12px;
      cursor: pointer;
    `;
    rejBtn.textContent = "✖ Reject";
    rejBtn.onclick = props.onReject;
    btnRow.appendChild(rejBtn);
  }

  if (props.onInspect) {
    const insBtn = document.createElement("button");
    insBtn.style.cssText = `
      padding: 6px 12px;
      background: var(--aether-surface-raised, #252538);
      color: var(--aether-text-primary, #cdd6f4);
      border: 1px solid var(--aether-border, #313244);
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
    `;
    insBtn.textContent = "🔍 Inspect Full Details";
    insBtn.onclick = props.onInspect;
    btnRow.appendChild(insBtn);
  }

  if (props.onCancelRun) {
    const cancelBtn = document.createElement("button");
    cancelBtn.style.cssText = `
      padding: 6px 12px;
      background: transparent;
      color: var(--aether-text-muted, #6c7086);
      border: 1px solid var(--aether-border, #313244);
      border-radius: 4px;
      font-size: 12px;
      cursor: pointer;
      margin-left: auto;
    `;
    cancelBtn.textContent = "Cancel Run";
    cancelBtn.onclick = props.onCancelRun;
    btnRow.appendChild(cancelBtn);
  }

  container.appendChild(btnRow);
  return container;
}
