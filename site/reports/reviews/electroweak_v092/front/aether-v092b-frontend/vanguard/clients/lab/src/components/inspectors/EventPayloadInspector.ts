import type { LabStore } from "../../state/lab-store.js";
import { renderJsonPayloadTree } from "../JsonPayloadTree.js";
import { formatSeq, formatTimestamp, truncateDigest } from "../../util/formatting.js";
import { copyToClipboard } from "../../util/clipboard.js";
import { renderEventKindBadge } from "../StatusBadge.js";

export function renderEventPayloadInspector(store: LabStore): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-event-payload-inspector";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    font-family: var(--lab-font-sans);
    color: var(--lab-text-primary);
  `;

  const sel = store.selection.get();
  const events = store.get().events;
  const event = events.find((e) => e.eventId === sel.selectedEventId);

  if (!event) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding: 24px; color: var(--lab-text-muted); text-align: center;";
    empty.textContent = "Select an event from the ledger or trace to inspect its payload";
    container.appendChild(empty);
    return container;
  }

  // Header Toolbar
  const header = document.createElement("div");
  header.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--lab-bg-panel);
    border-bottom: 1px solid var(--lab-border);
  `;

  const titleGroup = document.createElement("div");
  titleGroup.style.cssText = "display: flex; align-items: center; gap: 8px;";
  titleGroup.appendChild(renderEventKindBadge(event.payload.kind));

  const seqBadge = document.createElement("span");
  seqBadge.style.cssText = "font-family: var(--lab-font-mono); font-weight: bold; color: var(--lab-accent);";
  seqBadge.textContent = formatSeq(event.seq);
  titleGroup.appendChild(seqBadge);

  header.appendChild(titleGroup);

  const actionGroup = document.createElement("div");
  actionGroup.style.cssText = "display: flex; gap: 6px;";

  const copyJsonBtn = document.createElement("button");
  copyJsonBtn.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    color: var(--lab-text-primary);
    border-radius: var(--lab-radius-sm);
    padding: 3px 8px;
    font-size: 11px;
    cursor: pointer;
    font-family: var(--lab-font-mono);
  `;
  copyJsonBtn.textContent = "📋 Copy JSON";
  copyJsonBtn.onclick = () => copyToClipboard(JSON.stringify(event, null, 2));
  actionGroup.appendChild(copyJsonBtn);

  const traceBtn = document.createElement("button");
  traceBtn.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    color: var(--lab-accent);
    border-radius: var(--lab-radius-sm);
    padding: 3px 8px;
    font-size: 11px;
    cursor: pointer;
  `;
  traceBtn.textContent = "🕸 View in Trace";
  traceBtn.onclick = () => {
    store.selection.setWorkbench("trace");
    store.selection.selectTraceNode(event.eventId);
  };
  actionGroup.appendChild(traceBtn);

  header.appendChild(actionGroup);
  container.appendChild(header);

  // Metadata Grid
  const metaGrid = document.createElement("div");
  metaGrid.style.cssText = `
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 8px;
    padding: 10px 12px;
    background: var(--lab-bg-surface);
    border-bottom: 1px solid var(--lab-border);
    font-size: 11px;
    font-family: var(--lab-font-mono);
  `;

  metaGrid.innerHTML = `
    <div><span style="color: var(--lab-text-muted);">Event ID:</span> <span title="${event.eventId}">${truncateDigest(event.eventId, 12)}</span></div>
    <div><span style="color: var(--lab-text-muted);">Principal:</span> ${event.principal} (${event.principalRole ?? "agent"})</div>
    <div><span style="color: var(--lab-text-muted);">Occurred:</span> ${formatTimestamp(event.occurredAt)}</div>
    <div><span style="color: var(--lab-text-muted);">Scope:</span> ${event.scope ?? "episode"}</div>
    <div><span style="color: var(--lab-text-muted);">Trace ID:</span> ${truncateDigest(event.traceId, 8)}</div>
    <div><span style="color: var(--lab-text-muted);">Span ID:</span> ${truncateDigest(event.spanId, 8)}</div>
  `;

  container.appendChild(metaGrid);

  // Causal Parent & Children Nav Bar
  const causalNav = document.createElement("div");
  causalNav.style.cssText = `
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 12px;
    background: var(--lab-bg-panel);
    border-bottom: 1px solid var(--lab-border);
    font-size: 11px;
  `;

  if (event.parentEventId) {
    const parentBtn = document.createElement("button");
    parentBtn.style.cssText = `
      background: none;
      border: 1px solid var(--lab-border);
      color: var(--lab-accent);
      border-radius: 3px;
      padding: 2px 6px;
      font-size: 11px;
      cursor: pointer;
    `;
    parentBtn.textContent = `↖ Parent (${truncateDigest(event.parentEventId, 8)})`;
    parentBtn.onclick = () => {
      const parent = events.find((e) => e.eventId === event.parentEventId);
      store.selection.selectEvent(event.parentEventId!, parent?.seq);
    };
    causalNav.appendChild(parentBtn);
  } else {
    const rootLabel = document.createElement("span");
    rootLabel.style.color = "var(--lab-text-muted)";
    rootLabel.textContent = "Root causal node";
    causalNav.appendChild(rootLabel);
  }

  // Find children
  const children = events.filter((e) => e.parentEventId === event.eventId);
  if (children.length > 0) {
    const childLabel = document.createElement("span");
    childLabel.style.color = "var(--lab-text-muted)";
    childLabel.textContent = `Children (${children.length}):`;
    causalNav.appendChild(childLabel);

    children.slice(0, 3).forEach((child) => {
      const childBtn = document.createElement("button");
      childBtn.style.cssText = `
        background: none;
        border: 1px solid var(--lab-border);
        color: var(--lab-accent);
        border-radius: 3px;
        padding: 2px 6px;
        font-size: 11px;
        cursor: pointer;
      `;
      childBtn.textContent = `↘ ${formatSeq(child.seq)} ${child.payload.kind}`;
      childBtn.onclick = () => store.selection.selectEvent(child.eventId, child.seq);
      causalNav.appendChild(childBtn);
    });
  }

  container.appendChild(causalNav);

  // Payload Tree
  const treeWrapper = document.createElement("div");
  treeWrapper.style.cssText = "flex: 1; overflow-y: auto; padding: 4px;";
  treeWrapper.appendChild(
    renderJsonPayloadTree({
      data: event.payload,
      rootName: "payload",
      defaultExpandedDepth: 2,
      selection: store.selection,
    })
  );
  container.appendChild(treeWrapper);

  return container;
}
