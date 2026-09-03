import type { LabStore, EventCategoryFilter } from "../../state/lab-store.js";
import type { EventEnvelope } from "@aether/contracts";
import { VirtualList } from "../../virtual/virtual-list.js";
import { renderEventKindBadge, renderVerdictBadge } from "../StatusBadge.js";
import { renderSearchInput } from "../SearchInput.js";
import { renderReplayControls } from "../ReplayControls.js";
import { formatDuration, formatSeq, formatTimestamp, truncateDigest } from "../../util/formatting.js";

export function renderEventsWorkbench(store: LabStore): HTMLElement {
  const container = document.createElement("section");
  container.className = "aether-events-workbench";
  container.setAttribute("role", "tabpanel");
  container.setAttribute("aria-label", "Events Ledger Workbench");
  container.style.cssText = `
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: var(--lab-bg);
  `;

  const state = store.get();
  const sel = store.selection.get();
  const filteredEvents = store.getFilteredEvents();

  // Top Filter / Category Bar
  const filterBar = document.createElement("div");
  filterBar.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 12px;
    background: var(--lab-bg-surface);
    border-bottom: 1px solid var(--lab-border);
    gap: 8px;
    flex-wrap: wrap;
  `;

  const categories: Array<{ id: EventCategoryFilter; label: string }> = [
    { id: "all", label: "All" },
    { id: "errors", label: "Errors" },
    { id: "approvals", label: "Approvals" },
    { id: "effects", label: "Effects" },
    { id: "models", label: "Models" },
    { id: "tools", label: "Tools" },
    { id: "artifacts", label: "Artifacts" },
    { id: "budgets", label: "Budgets" },
    { id: "verification", label: "Verification" },
    { id: "context", label: "Context" },
    { id: "lifecycle", label: "Lifecycle" },
  ];

  const catGroup = document.createElement("div");
  catGroup.style.cssText = "display: flex; gap: 2px; overflow-x: auto;";

  for (const cat of categories) {
    const isCatActive = state.eventFilters.category === cat.id;
    const catBtn = document.createElement("button");
    catBtn.style.cssText = `
      background: ${isCatActive ? "var(--lab-accent-muted)" : "transparent"};
      color: ${isCatActive ? "var(--lab-accent)" : "var(--lab-text-secondary)"};
      border: 1px solid ${isCatActive ? "var(--lab-accent)" : "transparent"};
      border-radius: var(--lab-radius-sm);
      padding: 3px 8px;
      font-size: 11px;
      font-weight: ${isCatActive ? "600" : "400"};
      cursor: pointer;
      font-family: var(--lab-font-sans);
      white-space: nowrap;
    `;
    catBtn.textContent = cat.label;
    catBtn.onclick = () => {
      store.setEventFilters((prev) => ({ ...prev, category: cat.id }));
      refreshWorkbench();
    };
    catGroup.appendChild(catBtn);
  }
  filterBar.appendChild(catGroup);

  const rightControls = document.createElement("div");
  rightControls.style.cssText = "display: flex; align-items: center; gap: 8px;";

  const search = renderSearchInput({
    value: state.eventFilters.query,
    matchCount: filteredEvents.length,
    totalCount: state.events.length,
    onSearch: (q) => {
      store.setEventFilters((prev) => ({ ...prev, query: q }));
      refreshWorkbench();
    },
  });
  rightControls.appendChild(search);

  filterBar.appendChild(rightControls);
  container.appendChild(filterBar);

  // Sub-bar: Replay Controls & Mode
  const replayBar = document.createElement("div");
  replayBar.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 12px;
    background: var(--lab-bg-panel);
    border-bottom: 1px solid var(--lab-border);
  `;
  replayBar.appendChild(renderReplayControls(store));

  const stats = document.createElement("span");
  stats.style.cssText = "font-size: 11px; font-family: var(--lab-font-mono); color: var(--lab-text-muted);";
  stats.textContent = `Showing ${filteredEvents.length} of ${state.events.length} events`;
  replayBar.appendChild(stats);

  container.appendChild(replayBar);

  // Table Sticky Header
  const headerRow = document.createElement("div");
  headerRow.className = "aether-events-table-header";
  headerRow.style.cssText = `
    display: grid;
    grid-template-columns: 80px 140px 180px 120px 100px 80px 100px 1fr;
    gap: 8px;
    padding: 6px 12px;
    background: var(--lab-bg-panel);
    border-bottom: 1px solid var(--lab-border);
    font-size: 11px;
    font-weight: 600;
    color: var(--lab-text-secondary);
    font-family: var(--lab-font-mono);
    user-select: none;
  `;
  headerRow.innerHTML = `
    <div>SEQ</div>
    <div>TIMESTAMP</div>
    <div>KIND</div>
    <div>PRINCIPAL</div>
    <div>STATUS</div>
    <div>DURATION</div>
    <div>PARENT</div>
    <div>PAYLOAD SUMMARY</div>
  `;
  container.appendChild(headerRow);

  // Virtualized List Container
  const listWrapper = document.createElement("div");
  listWrapper.style.cssText = "flex: 1; position: relative; overflow: hidden;";

  const virtualList = new VirtualList<EventEnvelope>({
    items: filteredEvents,
    itemHeight: 32,
    overscan: 10,
    renderItem: (envelope, index) => {
      const isSelected = envelope.eventId === store.selection.get().selectedEventId;
      const isError =
        envelope.payload.kind === "EffectFailed" ||
        envelope.payload.kind === "ServiceError" ||
        typeof envelope.payload.error === "string" ||
        envelope.payload.outcome === "failed";

      const row = document.createElement("div");
      row.className = "aether-event-row";
      row.style.cssText = `
        display: grid;
        grid-template-columns: 80px 140px 180px 120px 100px 80px 100px 1fr;
        gap: 8px;
        align-items: center;
        padding: 0 12px;
        height: 32px;
        font-size: 11px;
        font-family: var(--lab-font-mono);
        border-bottom: 1px solid var(--lab-border-subtle);
        background: ${
          isSelected
            ? "var(--lab-bg-active)"
            : isError
            ? "var(--lab-danger-bg)"
            : index % 2 === 0
            ? "transparent"
            : "var(--lab-bg-surface)"
        };
        cursor: pointer;
        transition: background 0.05s ease;
      `;

      row.onmouseenter = () => {
        if (!isSelected) row.style.background = "var(--lab-bg-hover)";
      };
      row.onmouseleave = () => {
        if (!isSelected) {
          row.style.background = isError
            ? "var(--lab-danger-bg)"
            : index % 2 === 0
            ? "transparent"
            : "var(--lab-bg-surface)";
        }
      };

      // 1. Seq
      const cSeq = document.createElement("div");
      cSeq.style.color = isSelected ? "var(--lab-accent)" : "var(--lab-text-primary)";
      cSeq.style.fontWeight = "bold";
      cSeq.textContent = formatSeq(envelope.seq);
      row.appendChild(cSeq);

      // 2. Timestamp
      const cTime = document.createElement("div");
      cTime.style.color = "var(--lab-text-muted)";
      cTime.textContent = formatTimestamp(envelope.occurredAt).slice(11); // HH:MM:SS
      cTime.title = envelope.occurredAt;
      row.appendChild(cTime);

      // 3. Kind
      const cKind = document.createElement("div");
      cKind.appendChild(renderEventKindBadge(envelope.payload.kind));
      row.appendChild(cKind);

      // 4. Principal
      const cPrin = document.createElement("div");
      cPrin.style.color = "var(--lab-text-secondary)";
      cPrin.style.overflow = "hidden";
      cPrin.style.textOverflow = "ellipsis";
      cPrin.textContent = envelope.principal || "operator";
      cPrin.title = envelope.principal;
      row.appendChild(cPrin);

      // 5. Status
      const cStatus = document.createElement("div");
      if (isError) {
        cStatus.style.color = "var(--lab-danger)";
        cStatus.textContent = "✗ ERROR";
      } else if (envelope.payload.verdict) {
        cStatus.appendChild(renderVerdictBadge(String(envelope.payload.verdict)));
      } else {
        cStatus.style.color = "var(--lab-success)";
        cStatus.textContent = "✓ OK";
      }
      row.appendChild(cStatus);

      // 6. Duration
      const cDur = document.createElement("div");
      cDur.style.color = "var(--lab-text-muted)";
      const dur = typeof envelope.payload.durationMs === "number" ? envelope.payload.durationMs : undefined;
      cDur.textContent = formatDuration(dur);
      row.appendChild(cDur);

      // 7. Parent
      const cParent = document.createElement("div");
      cParent.style.color = "var(--lab-accent)";
      cParent.textContent = envelope.parentEventId ? truncateDigest(envelope.parentEventId, 6) : "-";
      cParent.title = envelope.parentEventId || "";
      row.appendChild(cParent);

      // 8. Payload Summary
      const cSummary = document.createElement("div");
      cSummary.style.color = "var(--lab-text-secondary)";
      cSummary.style.overflow = "hidden";
      cSummary.style.textOverflow = "ellipsis";
      cSummary.style.whiteSpace = "nowrap";

      const summaryText =
        typeof envelope.payload.goal === "string"
          ? `Goal: ${envelope.payload.goal}`
          : typeof envelope.payload.statement === "string"
          ? `Claim: ${envelope.payload.statement}`
          : typeof envelope.payload.text === "string"
          ? envelope.payload.text
          : typeof envelope.payload.action === "string"
          ? `Action: ${envelope.payload.action}`
          : typeof envelope.payload.tool === "string"
          ? `Tool: ${envelope.payload.tool}`
          : typeof envelope.payload.error === "string"
          ? `Error: ${envelope.payload.error}`
          : JSON.stringify(envelope.payload);

      cSummary.textContent = summaryText;
      row.appendChild(cSummary);

      row.onclick = () => {
        store.selection.selectEvent(envelope.eventId, envelope.seq);
        refreshWorkbench();
      };

      return row;
    },
    onScroll: (info) => {
      store.setIsUserScrolledUp(info.isScrolledUp);
    },
  });

  listWrapper.appendChild(virtualList.getElement());
  container.appendChild(listWrapper);

  // Auto render list items
  virtualList.render();

  function refreshWorkbench() {
    const parent = container.parentNode;
    if (parent) {
      const fresh = renderEventsWorkbench(store);
      parent.replaceChild(fresh, container);
    }
  }

  return container;
}
