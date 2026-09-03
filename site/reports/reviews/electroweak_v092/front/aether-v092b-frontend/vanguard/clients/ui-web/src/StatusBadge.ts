export type StatusBadgeProps = {
  status: string;
  label?: string;
  size?: "sm" | "md" | "lg";
};

export function renderStatusBadge(props: StatusBadgeProps): HTMLElement {
  const badge = document.createElement("span");
  badge.className = "aether-status-badge";

  const status = props.status.toLowerCase();
  let bg = "var(--aether-surface-raised, #252538)";
  let fg = "var(--aether-text-primary, #cdd6f4)";

  if (status === "running" || status === "active") {
    bg = "var(--aether-running, #fab387)";
    fg = "var(--aether-bg, #11111b)";
  } else if (status === "awaiting_approval" || status === "pending") {
    bg = "var(--aether-warning, #f9e2af)";
    fg = "var(--aether-bg, #11111b)";
  } else if (status === "satisfied" || status === "completed" || status === "pass" || status === "connected") {
    bg = "var(--aether-success, #a6e3a1)";
    fg = "var(--aether-bg, #11111b)";
  } else if (status === "failed" || status === "error" || status === "offline" || status === "incompatible") {
    bg = "var(--aether-danger, #f38ba8)";
    fg = "var(--aether-bg, #11111b)";
  } else if (status === "cancelled" || status === "degraded") {
    bg = "var(--aether-text-muted, #6c7086)";
    fg = "var(--aether-bg, #11111b)";
  } else if (status === "connecting" || status === "reconnecting") {
    bg = "var(--aether-info, #89dceb)";
    fg = "var(--aether-bg, #11111b)";
  }

  const padding = props.size === "sm" ? "2px 6px" : props.size === "lg" ? "6px 12px" : "4px 8px";
  const fontSize = props.size === "sm" ? "10px" : props.size === "lg" ? "13px" : "11px";

  badge.style.cssText = `
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: ${padding};
    border-radius: 4px;
    font-size: ${fontSize};
    font-weight: 600;
    text-transform: uppercase;
    background: ${bg};
    color: ${fg};
    font-family: var(--aether-font-sans, inherit);
    white-space: nowrap;
  `;

  badge.textContent = props.label ?? props.status;
  return badge;
}
