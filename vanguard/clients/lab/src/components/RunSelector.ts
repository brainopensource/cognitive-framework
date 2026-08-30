import type { LabStore } from "../state/lab-store.js";
import type { RuntimeClient } from "@aether/client";
import { renderRunStatusBadge } from "./StatusBadge.js";
import { truncateDigest } from "../util/formatting.js";

export function renderRunSelector(store: LabStore, client?: RuntimeClient): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-run-selector-panel";
  container.style.cssText = `
    display: flex;
    align-items: center;
    gap: 8px;
  `;

  const state = store.get();
  const activeRunId = state.activeRunId;
  const snapshot = state.snapshot;

  const label = document.createElement("span");
  label.style.cssText = "font-size: 11px; color: var(--lab-text-muted); font-weight: 600;";
  label.textContent = "RUN:";
  container.appendChild(label);

  const select = document.createElement("select");
  select.className = "aether-run-select-dropdown";
  select.setAttribute("aria-label", "Select active run");
  select.style.cssText = `
    background: var(--lab-bg-input);
    color: var(--lab-text-primary);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-sm);
    padding: 3px 8px;
    font-family: var(--lab-font-mono);
    font-size: 11px;
    outline: none;
    max-width: 220px;
    cursor: pointer;
  `;

  if (state.runs.length === 0) {
    const opt = document.createElement("option");
    opt.value = activeRunId;
    opt.textContent = activeRunId ? truncateDigest(activeRunId, 16) : "No runs loaded";
    select.appendChild(opt);
  } else {
    for (const run of state.runs) {
      const opt = document.createElement("option");
      opt.value = run.runId;
      opt.textContent = `${truncateDigest(run.runId, 12)} [${run.status}]`;
      if (run.runId === activeRunId) {
        opt.selected = true;
      }
      select.appendChild(opt);
    }
  }

  select.onchange = () => {
    const selected = select.value;
    if (selected && selected !== activeRunId) {
      store.selectRun(selected, client);
    }
  };
  container.appendChild(select);

  // Status Badge for current active run
  const statusBadge = renderRunStatusBadge(snapshot.status || "pending");
  container.appendChild(statusBadge);

  if (client) {
    const refreshBtn = document.createElement("button");
    refreshBtn.style.cssText = `
      background: none;
      border: none;
      color: var(--lab-text-muted);
      cursor: pointer;
      font-size: 12px;
      padding: 2px 4px;
    `;
    refreshBtn.textContent = "↻";
    refreshBtn.title = "Refresh runs list";
    refreshBtn.onclick = () => store.loadRuns(client);
    container.appendChild(refreshBtn);
  }

  return container;
}
