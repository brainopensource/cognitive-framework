import type { LabStore } from "../../state/lab-store.js";
import type { RuntimeClient } from "@aether/client";
import { renderRunStatusBadge, renderVerdictBadge } from "../StatusBadge.js";
import { renderSearchInput } from "../SearchInput.js";
import {
  formatCost,
  formatDuration,
  formatSeq,
  formatTimestamp,
  formatTokens,
  truncateDigest,
} from "../../util/formatting.js";

export function renderRunsWorkbench(store: LabStore, client?: RuntimeClient): HTMLElement {
  const container = document.createElement("section");
  container.className = "aether-runs-workbench";
  container.setAttribute("role", "tabpanel");
  container.setAttribute("aria-label", "Runs Workbench");
  container.style.cssText = `
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: var(--lab-bg);
  `;

  const state = store.get();
  const snapshot = state.snapshot;
  const filteredRuns = store.getFilteredRuns();

  // Top Filter / Actions Toolbar
  const toolbar = document.createElement("div");
  toolbar.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background: var(--lab-bg-surface);
    border-bottom: 1px solid var(--lab-border);
    gap: 12px;
    flex-wrap: wrap;
  `;

  const leftControls = document.createElement("div");
  leftControls.style.cssText = "display: flex; align-items: center; gap: 8px;";

  const search = renderSearchInput({
    value: state.runFilters.query,
    matchCount: filteredRuns.length,
    totalCount: state.runs.length,
    onSearch: (q) => {
      store.setRunFilters((prev) => ({ ...prev, query: q }));
      refreshWorkbench();
    },
  });
  leftControls.appendChild(search);

  // Status Filter Select
  const statusSelect = document.createElement("select");
  statusSelect.style.cssText = `
    background: var(--lab-bg-input);
    color: var(--lab-text-primary);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-sm);
    padding: 4px 8px;
    font-size: 11px;
    font-family: var(--lab-font-sans);
    outline: none;
    cursor: pointer;
  `;
  const statuses = ["all", "running", "satisfied", "failed", "awaiting_approval", "cancelled"];
  for (const s of statuses) {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s === "all" ? "All Statuses" : s.toUpperCase();
    if (state.runFilters.status === s) opt.selected = true;
    statusSelect.appendChild(opt);
  }
  statusSelect.onchange = () => {
    store.setRunFilters((prev) => ({ ...prev, status: statusSelect.value }));
    refreshWorkbench();
  };
  leftControls.appendChild(statusSelect);

  toolbar.appendChild(leftControls);

  const rightControls = document.createElement("div");
  rightControls.style.cssText = "display: flex; align-items: center; gap: 8px;";

  if (client) {
    const refreshBtn = document.createElement("button");
    refreshBtn.style.cssText = `
      background: var(--lab-bg-panel);
      border: 1px solid var(--lab-border);
      color: var(--lab-text-primary);
      padding: 4px 10px;
      border-radius: var(--lab-radius-sm);
      font-size: 11px;
      cursor: pointer;
    `;
    refreshBtn.textContent = "↻ Refresh Runs";
    refreshBtn.onclick = () => store.loadRuns(client);
    rightControls.appendChild(refreshBtn);
  }

  toolbar.appendChild(rightControls);
  container.appendChild(toolbar);

  // Main Split Content: Active Run Card (Top) + Runs Table (Bottom)
  const mainContent = document.createElement("div");
  mainContent.style.cssText = "flex: 1; display: flex; flex-direction: column; overflow-y: auto; padding: 16px; gap: 16px;";

  // Active Run Detailed Overview Card
  const activeCard = document.createElement("div");
  activeCard.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-md);
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  `;

  const activeHeader = document.createElement("div");
  activeHeader.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

  const activeTitle = document.createElement("div");
  activeTitle.style.cssText = "display: flex; align-items: center; gap: 8px;";
  activeTitle.innerHTML = `
    <span style="font-size: 14px; font-weight: 600; color: var(--lab-text-primary);">Active Run Inspection:</span>
    <span style="font-family: var(--lab-font-mono); font-size: 13px; color: var(--lab-accent); font-weight: bold;">
      ${state.activeRunId || "No Run Selected"}
    </span>
  `;
  activeTitle.appendChild(renderRunStatusBadge(snapshot.status));
  activeHeader.appendChild(activeTitle);

  const activeActions = document.createElement("div");
  activeActions.style.cssText = "display: flex; gap: 6px;";

  const inspectEventsBtn = document.createElement("button");
  inspectEventsBtn.style.cssText = `
    background: var(--lab-accent-muted);
    border: 1px solid var(--lab-accent);
    color: var(--lab-accent);
    padding: 4px 10px;
    border-radius: var(--lab-radius-sm);
    font-size: 11px;
    cursor: pointer;
    font-weight: 600;
  `;
  inspectEventsBtn.textContent = "📜 Inspect Event Ledger";
  inspectEventsBtn.onclick = () => store.selection.setWorkbench("events");
  activeActions.appendChild(inspectEventsBtn);

  const viewTraceBtn = document.createElement("button");
  viewTraceBtn.style.cssText = `
    background: var(--lab-bg-panel);
    border: 1px solid var(--lab-border);
    color: var(--lab-text-primary);
    padding: 4px 10px;
    border-radius: var(--lab-radius-sm);
    font-size: 11px;
    cursor: pointer;
  `;
  viewTraceBtn.textContent = "🕸 Trace Explorer";
  viewTraceBtn.onclick = () => store.selection.setWorkbench("trace");
  activeActions.appendChild(viewTraceBtn);

  activeHeader.appendChild(activeActions);
  activeCard.appendChild(activeHeader);

  // Key Metrics Grid
  const metricsGrid = document.createElement("div");
  metricsGrid.style.cssText = `
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 8px;
    font-family: var(--lab-font-mono);
  `;

  const durationMs =
    snapshot.startTime && snapshot.endTime
      ? new Date(snapshot.endTime).getTime() - new Date(snapshot.startTime).getTime()
      : undefined;

  metricsGrid.innerHTML = `
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">TOTAL EVENTS</div>
      <div style="color: var(--lab-text-primary); font-size: 14px; font-weight: bold;">${state.events.length}</div>
    </div>
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">TURNS</div>
      <div style="color: var(--lab-text-primary); font-size: 14px; font-weight: bold;">${snapshot.turns}</div>
    </div>
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">TOTAL TOKENS</div>
      <div style="color: var(--lab-accent); font-size: 14px; font-weight: bold;">${formatTokens(snapshot.tokens.totalTokens)}</div>
    </div>
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">EST. COST</div>
      <div style="color: var(--lab-success); font-size: 14px; font-weight: bold;">${formatCost(snapshot.costMicros)}</div>
    </div>
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">DURATION</div>
      <div style="color: var(--lab-text-primary); font-size: 14px; font-weight: bold;">${formatDuration(durationMs)}</div>
    </div>
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">ARTIFACTS</div>
      <div style="color: var(--lab-digest); font-size: 14px; font-weight: bold;">${snapshot.artifacts.length}</div>
    </div>
  `;
  activeCard.appendChild(metricsGrid);
  mainContent.appendChild(activeCard);

  // Runs Table Section
  const tableSection = document.createElement("div");
  tableSection.style.cssText = "display: flex; flex-direction: column; gap: 8px;";

  const tableTitle = document.createElement("h3");
  tableTitle.style.cssText = "margin: 0; font-size: 13px; font-weight: 600; color: var(--lab-text-secondary);";
  tableTitle.textContent = `Available Runs (${filteredRuns.length})`;
  tableSection.appendChild(tableTitle);

  const tableWrapper = document.createElement("div");
  tableWrapper.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-md);
    overflow: hidden;
  `;

  const table = document.createElement("table");
  table.style.cssText = `
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    text-align: left;
  `;

  const thead = document.createElement("thead");
  thead.innerHTML = `
    <tr style="background: var(--lab-bg-panel); border-bottom: 1px solid var(--lab-border); color: var(--lab-text-secondary); font-size: 11px;">
      <th style="padding: 8px 12px;">RUN ID</th>
      <th style="padding: 8px 12px;">STATUS</th>
      <th style="padding: 8px 12px;">OCCURRED AT</th>
      <th style="padding: 8px 12px;">SEQ</th>
      <th style="padding: 8px 12px;">VERDICT</th>
      <th style="padding: 8px 12px; text-align: right;">ACTION</th>
    </tr>
  `;
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  tbody.className = "aether-runs-tbody";
  table.appendChild(tbody);

  if (filteredRuns.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="6" style="padding: 24px; text-align: center; color: var(--lab-text-muted);">No runs match the filter criteria</td>`;
    tbody.appendChild(row);
  } else {
    for (const run of filteredRuns) {
      const isSelected = run.runId === state.activeRunId;
      const tr = document.createElement("tr");
      tr.style.cssText = `
        border-bottom: 1px solid var(--lab-border-subtle);
        background: ${isSelected ? "var(--lab-bg-active)" : "transparent"};
        transition: background 0.1s ease;
      `;
      tr.onmouseenter = () => {
        if (!isSelected) tr.style.background = "var(--lab-bg-hover)";
      };
      tr.onmouseleave = () => {
        if (!isSelected) tr.style.background = "transparent";
      };

      const tdId = document.createElement("td");
      tdId.style.cssText = "padding: 8px 12px; font-family: var(--lab-font-mono); font-weight: 600;";
      tdId.textContent = truncateDigest(run.runId, 14);
      tdId.title = run.runId;
      tr.appendChild(tdId);

      const tdStatus = document.createElement("td");
      tdStatus.style.padding = "8px 12px";
      tdStatus.appendChild(renderRunStatusBadge(run.status));
      tr.appendChild(tdStatus);

      const tdTime = document.createElement("td");
      tdTime.style.cssText = "padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-secondary); font-size: 11px;";
      tdTime.textContent = formatTimestamp(run.occurredAt);
      tr.appendChild(tdTime);

      const tdSeq = document.createElement("td");
      tdSeq.style.cssText = "padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-accent); font-size: 11px;";
      tdSeq.textContent = formatSeq(run.seq);
      tr.appendChild(tdSeq);

      const tdVerdict = document.createElement("td");
      tdVerdict.style.padding = "8px 12px";
      tdVerdict.appendChild(renderVerdictBadge(run.verdict));
      tr.appendChild(tdVerdict);

      const tdAction = document.createElement("td");
      tdAction.style.cssText = "padding: 8px 12px; text-align: right;";

      const selectBtn = document.createElement("button");
      selectBtn.style.cssText = `
        background: ${isSelected ? "var(--lab-accent)" : "var(--lab-bg-panel)"};
        color: ${isSelected ? "var(--lab-bg)" : "var(--lab-text-primary)"};
        border: 1px solid ${isSelected ? "var(--lab-accent)" : "var(--lab-border)"};
        border-radius: var(--lab-radius-sm);
        padding: 3px 8px;
        font-size: 11px;
        cursor: pointer;
        font-weight: 500;
      `;
      selectBtn.textContent = isSelected ? "Active" : "Inspect ↗";
      selectBtn.onclick = () => {
        store.selectRun(run.runId, client);
        refreshWorkbench();
      };
      tdAction.appendChild(selectBtn);
      tr.appendChild(tdAction);

      tbody.appendChild(tr);
    }
  }

  tableWrapper.appendChild(table);
  tableSection.appendChild(tableWrapper);
  mainContent.appendChild(tableSection);

  container.appendChild(mainContent);

  function refreshWorkbench() {
    const parent = container.parentNode;
    if (parent) {
      const fresh = renderRunsWorkbench(store, client);
      parent.replaceChild(fresh, container);
    }
  }

  return container;
}
