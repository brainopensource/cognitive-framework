import type { ConnectionState, FeatureAvailability } from "../state/lab-store.js";

export function createBadge(text: string, glyph: string, colorVar: string, bgVar: string): HTMLElement {
  const badge = document.createElement("span");
  badge.className = "aether-status-badge";
  badge.style.cssText = `
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 6px;
    border-radius: var(--lab-radius-sm);
    font-size: 11px;
    font-weight: 500;
    font-family: var(--lab-font-mono);
    line-height: 1.2;
    white-space: nowrap;
    color: ${colorVar};
    background: ${bgVar};
    border: 1px solid ${colorVar}40;
  `;

  const glyphEl = document.createElement("span");
  glyphEl.className = "badge-glyph";
  glyphEl.textContent = glyph;
  glyphEl.setAttribute("aria-hidden", "true");
  badge.appendChild(glyphEl);

  const textEl = document.createElement("span");
  textEl.className = "badge-text";
  textEl.textContent = text;
  badge.appendChild(textEl);

  return badge;
}

export function renderRunStatusBadge(status: string): HTMLElement {
  const norm = status.toLowerCase();
  if (norm === "satisfied" || norm === "passed" || norm === "1") {
    return createBadge("SATISFIED", "✓", "var(--lab-success)", "var(--lab-success-bg)");
  }
  if (norm === "running") {
    return createBadge("RUNNING", "⟳", "var(--lab-running)", "var(--lab-running-bg)");
  }
  if (norm === "awaiting_approval") {
    return createBadge("AWAITING APPROVAL", "⚠", "var(--lab-warning)", "var(--lab-warning-bg)");
  }
  if (norm === "failed" || norm === "error") {
    return createBadge("FAILED", "✗", "var(--lab-danger)", "var(--lab-danger-bg)");
  }
  if (norm === "cancelled") {
    return createBadge("CANCELLED", "⊘", "var(--lab-text-muted)", "var(--lab-bg-panel)");
  }
  return createBadge(status.toUpperCase() || "PENDING", "⋯", "var(--lab-pending)", "var(--lab-bg-panel)");
}

export function renderConnectionStatusBadge(state: ConnectionState): HTMLElement {
  switch (state) {
    case "connected":
      return createBadge("CONNECTED", "●", "var(--lab-success)", "var(--lab-success-bg)");
    case "connecting":
      return createBadge("CONNECTING", "○", "var(--lab-running)", "var(--lab-running-bg)");
    case "reconnecting":
      return createBadge("RECONNECTING", "◌", "var(--lab-warning)", "var(--lab-warning-bg)");
    case "unavailable":
      return createBadge("UNAVAILABLE", "✕", "var(--lab-danger)", "var(--lab-danger-bg)");
    case "offline":
      return createBadge("OFFLINE", "—", "var(--lab-text-muted)", "var(--lab-bg-panel)");
  }
}

export function renderVerdictBadge(verdict?: string): HTMLElement {
  if (!verdict) {
    return createBadge("UNVERIFIED", "·", "var(--lab-text-muted)", "var(--lab-bg-panel)");
  }
  const v = verdict.toLowerCase();
  if (v === "satisfied" || v === "passed" || v === "1" || v === "verified") {
    return createBadge("SATISFIED", "✓", "var(--lab-success)", "var(--lab-success-bg)");
  }
  if (v === "disputed") {
    return createBadge("DISPUTED", "?", "var(--lab-warning)", "var(--lab-warning-bg)");
  }
  return createBadge("FAILED", "✗", "var(--lab-danger)", "var(--lab-danger-bg)");
}

export function renderApprovalStatusBadge(status: string): HTMLElement {
  const norm = status.toLowerCase();
  if (norm === "approved") {
    return createBadge("APPROVED", "✓", "var(--lab-success)", "var(--lab-success-bg)");
  }
  if (norm === "rejected") {
    return createBadge("REJECTED", "✕", "var(--lab-danger)", "var(--lab-danger-bg)");
  }
  if (norm === "expired") {
    return createBadge("EXPIRED", "⏱", "var(--lab-text-muted)", "var(--lab-bg-panel)");
  }
  return createBadge("PENDING", "⏳", "var(--lab-warning)", "var(--lab-warning-bg)");
}

export function renderCapabilityStatusBadge(status: FeatureAvailability): HTMLElement {
  switch (status) {
    case "AVAILABLE":
      return createBadge("AVAILABLE", "✓", "var(--lab-success)", "var(--lab-success-bg)");
    case "UNAVAILABLE":
      return createBadge("UNAVAILABLE", "✕", "var(--lab-danger)", "var(--lab-danger-bg)");
    case "DEGRADED":
      return createBadge("DEGRADED", "⚠", "var(--lab-warning)", "var(--lab-warning-bg)");
    case "INCOMPATIBLE":
      return createBadge("INCOMPATIBLE", "⊘", "var(--lab-text-muted)", "var(--lab-bg-panel)");
  }
}

export function renderEventKindBadge(kind: string): HTMLElement {
  if (kind.startsWith("Goal") || kind.startsWith("Episode")) {
    return createBadge(kind, "🏁", "var(--lab-pending)", "var(--lab-bg-panel)");
  }
  if (kind.startsWith("Effect") || kind.startsWith("Operator")) {
    if (kind.includes("Failed")) {
      return createBadge(kind, "💥", "var(--lab-danger)", "var(--lab-danger-bg)");
    }
    return createBadge(kind, "⚡", "var(--lab-accent)", "var(--lab-accent-muted)");
  }
  if (kind.startsWith("Model")) {
    return createBadge(kind, "🧠", "var(--lab-running)", "var(--lab-running-bg)");
  }
  if (kind.startsWith("Approval")) {
    return createBadge(kind, "🛡", "var(--lab-warning)", "var(--lab-warning-bg)");
  }
  if (kind.startsWith("Artifact")) {
    return createBadge(kind, "📦", "var(--lab-digest)", "var(--lab-bg-panel)");
  }
  if (kind.startsWith("Verdict") || kind.startsWith("Evidence") || kind.startsWith("Evaluation")) {
    return createBadge(kind, "⚖", "var(--lab-success)", "var(--lab-success-bg)");
  }
  if (kind.startsWith("Budget")) {
    return createBadge(kind, "💰", "var(--lab-text-secondary)", "var(--lab-bg-panel)");
  }
  if (kind.startsWith("Context") || kind.startsWith("Observation") || kind.startsWith("Memory")) {
    return createBadge(kind, "📜", "var(--lab-text-secondary)", "var(--lab-bg-panel)");
  }
  return createBadge(kind, "•", "var(--lab-text-muted)", "var(--lab-bg-panel)");
}

export function renderRiskStateBadge(risk: string): HTMLElement {
  const norm = risk.toLowerCase();
  if (norm === "safe" || norm === "low") {
    return createBadge("LOW RISK", "✓", "var(--lab-success)", "var(--lab-success-bg)");
  }
  if (norm === "warning" || norm === "medium") {
    return createBadge("MED RISK", "⚠", "var(--lab-warning)", "var(--lab-warning-bg)");
  }
  return createBadge("HIGH RISK", "⛔", "var(--lab-danger)", "var(--lab-danger-bg)");
}
