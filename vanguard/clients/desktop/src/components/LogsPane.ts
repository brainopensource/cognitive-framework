import type { DesktopStore } from "../state/desktop-store.js";
import type { EventEnvelope } from "@aether/contracts";

/** Event kinds that carry a failure. Rendered in the danger tone. */
const FAILURE_KINDS = new Set(["RunFailed", "RunCancelled", "EffectFailed", "Error"]);

function kindOf(envelope: EventEnvelope): string {
  const payload = (envelope as { payload?: Record<string, unknown> }).payload;
  return String(payload?.kind ?? "Event");
}

function summarize(envelope: EventEnvelope): string {
  const payload = ((envelope as { payload?: Record<string, unknown> }).payload ?? {}) as Record<
    string,
    unknown
  >;
  // Prefer the fields that explain a stall: an error, a reason, a producer.
  for (const field of ["error", "reason", "detail", "message", "producer"]) {
    const value = payload[field];
    if (typeof value === "string" && value) return value;
  }
  const rest = Object.entries(payload).filter(([key]) => key !== "kind");
  return rest.length ? JSON.stringify(Object.fromEntries(rest)) : "";
}

/**
 * The raw ledger for the active run.
 *
 * A run that produces one heartbeat and then nothing looks identical, from the
 * transcript, to a run that is still thinking. The transcript renders semantic
 * turns, so an event it has no projection for is invisible -- which is how a
 * failed run reads as "streaming forever". This pane renders every envelope in
 * sequence, including the ones no projection claims.
 */
export function renderLogsPane(store: DesktopStore): HTMLElement {
  const state = store.get();

  const pane = document.createElement("div");
  pane.className = "aether-logs-pane";
  pane.style.cssText = "display: flex; flex-direction: column; gap: 8px; height: 100%;";

  const header = document.createElement("div");
  header.style.cssText =
    "display: flex; align-items: center; justify-content: space-between; gap: 8px; " +
    "font-size: 11px; color: var(--aether-text-muted, #6c7086);";

  const summary = document.createElement("span");
  summary.className = "aether-logs-summary";
  summary.textContent = state.runId
    ? `run ${state.runId} · ${state.events.length} event${state.events.length === 1 ? "" : "s"}`
    : "no active run";
  header.appendChild(summary);

  const copyBtn = document.createElement("button");
  copyBtn.setAttribute("data-focus-key", "logs-copy");
  copyBtn.style.cssText =
    "padding: 3px 8px; background: transparent; border: 1px solid var(--aether-border, #313244); " +
    "color: var(--aether-text-secondary, #a6adc8); border-radius: 4px; font-size: 11px; cursor: pointer;";
  copyBtn.textContent = "Copy JSON";
  copyBtn.onclick = () => {
    void navigator.clipboard?.writeText(JSON.stringify(state.events, null, 2));
  };
  header.appendChild(copyBtn);
  pane.appendChild(header);

  const list = document.createElement("div");
  list.className = "aether-logs-list";
  list.style.cssText =
    "flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; " +
    "font-family: var(--aether-font-mono, monospace); font-size: 11px;";

  if (state.events.length === 0) {
    const empty = document.createElement("div");
    empty.className = "aether-logs-empty";
    empty.style.cssText = "color: var(--aether-text-muted, #6c7086); padding: 12px;";
    empty.textContent = state.runId
      ? "The run was accepted but has published no events yet."
      : "Send an instruction to start a run, then its ledger appears here.";
    list.appendChild(empty);
  }

  for (const envelope of state.events) {
    const kind = kindOf(envelope);
    const isFailure = FAILURE_KINDS.has(kind);

    const row = document.createElement("div");
    row.className = "aether-logs-row";
    row.style.cssText =
      "display: flex; gap: 8px; padding: 4px 6px; border-radius: 4px; align-items: baseline; " +
      "background: var(--aether-surface-raised, #252538);";

    const seq = document.createElement("span");
    seq.style.cssText = "color: var(--aether-text-muted, #6c7086); min-width: 32px;";
    seq.textContent = String((envelope as { seq?: string }).seq ?? "");
    row.appendChild(seq);

    const kindEl = document.createElement("span");
    kindEl.style.cssText = `min-width: 130px; font-weight: 700; color: ${
      isFailure ? "var(--aether-danger, #f38ba8)" : "var(--aether-accent, #89b4fa)"
    };`;
    kindEl.textContent = kind;
    row.appendChild(kindEl);

    const detail = document.createElement("span");
    detail.style.cssText =
      "flex: 1; color: var(--aether-text-primary, #cdd6f4); word-break: break-word;";
    detail.textContent = summarize(envelope);
    row.appendChild(detail);

    list.appendChild(row);
  }

  pane.appendChild(list);
  return pane;
}
