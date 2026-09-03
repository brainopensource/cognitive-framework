import { renderStatusBadge } from "./StatusBadge.js";

export type RunStatusProps = {
  runId: string;
  status: string;
  seq?: string;
  verdict?: string;
  onClick?: () => void;
};

export function renderRunStatus(props: RunStatusProps): HTMLElement {
  const el = document.createElement("div");
  el.className = "aether-run-status";
  el.style.cssText = `
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 4px 8px;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 6px;
    font-size: 12px;
    color: var(--aether-text-primary, #cdd6f4);
    font-family: var(--aether-font-sans, inherit);
  `;

  if (props.onClick) {
    el.style.cursor = "pointer";
    el.onclick = props.onClick;
  }

  const label = document.createElement("span");
  label.style.fontWeight = "600";
  label.textContent = props.runId ? `Run: ${props.runId.slice(0, 8)}…` : "No Run";
  el.appendChild(label);

  const badge = renderStatusBadge({ status: props.status, size: "sm" });
  el.appendChild(badge);

  if (props.seq) {
    const seqEl = document.createElement("span");
    seqEl.style.cssText = "color: var(--aether-text-muted, #6c7086); font-family: var(--aether-font-mono, monospace); font-size: 11px;";
    seqEl.textContent = `seq:${props.seq}`;
    el.appendChild(seqEl);
  }

  return el;
}
