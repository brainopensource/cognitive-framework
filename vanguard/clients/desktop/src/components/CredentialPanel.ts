import type { DesktopStore } from "../state/desktop-store.js";
import type { CredentialState } from "../gateway/credentials.js";

const TONE: Record<CredentialState, { color: string; label: string }> = {
  CONFIGURED: { color: "var(--aether-success, #a6e3a1)", label: "READY" },
  MISSING: { color: "var(--aether-danger, #f38ba8)", label: "NO KEY" },
  DENIED: { color: "var(--aether-warning, #fab387)", label: "UNREADABLE" },
  INVALID: { color: "var(--aether-danger, #f38ba8)", label: "REJECTED" },
  EXHAUSTED: { color: "var(--aether-warning, #fab387)", label: "NO CREDIT" },
  RATE_LIMITED: { color: "var(--aether-warning, #fab387)", label: "RATE LIMITED" },
  UNREACHABLE: { color: "var(--aether-warning, #fab387)", label: "UNREACHABLE" },
  UNKNOWN: { color: "var(--aether-text-muted, #6c7086)", label: "UNKNOWN" },
};

/**
 * Provider credential status, as reported by the runtime.
 *
 * This replaces a card that asked for an API key and stored it in browser
 * memory. The key belongs to the gateway (`SEC-01`): it is loaded from a
 * mode-0600 `.env` at the process edge and never crosses into the page. So
 * this pane states what the runtime can actually see and what to do about it,
 * rather than offering a text box whose contents went nowhere durable.
 */
export function renderCredentialPanel(store: DesktopStore): HTMLElement {
  const state = store.get();
  const credential = state.credential;

  const box = document.createElement("div");
  box.className = "aether-credential-panel";
  box.style.cssText =
    "display: flex; flex-direction: column; gap: 10px; padding: 12px; " +
    "background: var(--aether-surface-raised, #252538); border-radius: 6px;";

  const header = document.createElement("div");
  header.style.cssText = "display: flex; align-items: center; justify-content: space-between; gap: 8px;";

  const title = document.createElement("div");
  title.style.cssText = "font-weight: 700; color: var(--aether-accent, #89b4fa);";
  title.textContent = "Provider Credential";
  header.appendChild(title);

  const tone = TONE[credential?.state ?? "UNKNOWN"];
  const badge = document.createElement("span");
  badge.className = "aether-credential-badge";
  badge.style.cssText =
    `background: ${tone.color}; color: var(--aether-bg, #11111b); padding: 2px 8px; ` +
    "border-radius: 4px; font-size: 11px; font-weight: 700;";
  badge.textContent = credential ? tone.label : "CHECKING…";
  header.appendChild(badge);
  box.appendChild(header);

  const keyRef = document.createElement("div");
  keyRef.style.cssText =
    "font-family: var(--aether-font-mono, monospace); font-size: 11px; color: var(--aether-text-secondary, #a6adc8);";
  keyRef.textContent = credential
    ? `${credential.keyRef} · ${credential.source || "no source reported"}`
    : "Asking the runtime…";
  box.appendChild(keyRef);

  if (credential?.detail) {
    const detail = document.createElement("div");
    detail.style.cssText = "font-size: 12px; color: var(--aether-text-primary, #cdd6f4);";
    detail.textContent = credential.detail;
    box.appendChild(detail);
  }

  // The remedy is the whole point of this pane: an operator who is told only
  // "not configured" goes looking in the UI for a box to type into.
  if (credential?.remedy) {
    const remedy = document.createElement("pre");
    remedy.className = "aether-credential-remedy";
    remedy.style.cssText =
      "margin: 0; padding: 8px; background: var(--aether-bg, #11111b); border-radius: 4px; " +
      "font-family: var(--aether-font-mono, monospace); font-size: 11px; " +
      "color: var(--aether-warning, #fab387); white-space: pre-wrap; overflow-x: auto;";
    remedy.textContent = credential.remedy;
    box.appendChild(remedy);
  }

  const actions = document.createElement("div");
  actions.style.cssText = "display: flex; gap: 6px; align-items: center;";

  const testBtn = document.createElement("button");
  testBtn.className = "aether-credential-test";
  testBtn.setAttribute("data-focus-key", "credential-test");
  testBtn.disabled = state.credentialProbeRunning;
  testBtn.style.cssText =
    "padding: 4px 10px; background: transparent; border: 1px solid var(--aether-border, #313244); " +
    "color: var(--aether-info, #89dceb); border-radius: 4px; font-size: 11px; " +
    `cursor: ${state.credentialProbeRunning ? "progress" : "pointer"};`;
  testBtn.textContent = state.credentialProbeRunning ? "Testing…" : "Test Connection";
  testBtn.onclick = () => {
    void store.testProviderConnection(state.model);
  };
  actions.appendChild(testBtn);

  const recheckBtn = document.createElement("button");
  recheckBtn.setAttribute("data-focus-key", "credential-recheck");
  recheckBtn.style.cssText =
    "padding: 4px 10px; background: transparent; border: 1px solid var(--aether-border, #313244); " +
    "color: var(--aether-text-secondary, #a6adc8); border-radius: 4px; font-size: 11px; cursor: pointer;";
  recheckBtn.textContent = "Re-check Key";
  recheckBtn.onclick = () => {
    void store.refreshCredentialStatus();
  };
  actions.appendChild(recheckBtn);
  box.appendChild(actions);

  const probe = state.credentialProbe;
  if (probe) {
    const result = document.createElement("div");
    result.className = "aether-credential-probe-result";
    result.style.cssText =
      `font-size: 12px; color: ${probe.ok ? "var(--aether-success, #a6e3a1)" : "var(--aether-danger, #f38ba8)"};`;
    result.textContent = probe.ok
      ? `✓ ${probe.model} answered. The key works.`
      : `✗ ${probe.detail}`;
    box.appendChild(result);
  }

  return box;
}
