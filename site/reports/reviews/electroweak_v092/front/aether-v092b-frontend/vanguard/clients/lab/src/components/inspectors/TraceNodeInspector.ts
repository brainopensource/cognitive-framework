import type { LabStore } from "../../state/lab-store.js";
import { formatSeq, formatTimestamp, truncateDigest } from "../../util/formatting.js";
import { renderEventKindBadge } from "../StatusBadge.js";

export function renderTraceNodeInspector(store: LabStore): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-trace-node-inspector";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    font-family: var(--lab-font-sans);
    color: var(--lab-text-primary);
  `;

  const sel = store.selection.get();
  const graph = store.get().traceGraph;
  const node = graph.nodes.find((n) => n.id === sel.selectedTraceNodeId);

  if (!node) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding: 24px; color: var(--lab-text-muted); text-align: center;";
    empty.textContent = "Select a node in the causal trace graph to inspect";
    container.appendChild(empty);
    return container;
  }

  // Header
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
  titleGroup.appendChild(renderEventKindBadge(node.kind));

  const seqBadge = document.createElement("span");
  seqBadge.style.cssText = "font-family: var(--lab-font-mono); font-weight: bold; color: var(--lab-accent);";
  seqBadge.textContent = formatSeq(node.seq);
  titleGroup.appendChild(seqBadge);

  header.appendChild(titleGroup);

  const openEventBtn = document.createElement("button");
  openEventBtn.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    color: var(--lab-accent);
    border-radius: var(--lab-radius-sm);
    padding: 3px 8px;
    font-size: 11px;
    cursor: pointer;
  `;
  openEventBtn.textContent = "📜 Open in Event Ledger";
  openEventBtn.onclick = () => {
    store.selection.setWorkbench("events");
    store.selection.selectEvent(node.id, node.seq);
  };
  header.appendChild(openEventBtn);

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
    <div><span style="color: var(--lab-text-muted);">Node ID:</span> ${truncateDigest(node.id, 10)}</div>
    <div><span style="color: var(--lab-text-muted);">Principal:</span> ${node.principal || "system"}</div>
    <div><span style="color: var(--lab-text-muted);">Occurred:</span> ${formatTimestamp(node.occurredAt)}</div>
    <div><span style="color: var(--lab-text-muted);">Run ID:</span> ${node.runId || "-"}</div>
  `;
  container.appendChild(metaGrid);

  // Summary
  if (node.summary) {
    const summaryBox = document.createElement("div");
    summaryBox.style.cssText = `
      margin: 10px 12px;
      padding: 8px 10px;
      background: var(--lab-bg-panel);
      border: 1px solid var(--lab-border);
      border-radius: var(--lab-radius-sm);
      font-size: 12px;
    `;
    summaryBox.innerHTML = `
      <div style="font-weight: 600; color: var(--lab-text-secondary); margin-bottom: 4px;">Node Summary</div>
      <div style="color: var(--lab-text-primary);">${node.summary}</div>
    `;
    container.appendChild(summaryBox);
  }

  // Causal Neighbors
  const inEdges = graph.edges.filter((e) => e.target === node.id);
  const outEdges = graph.edges.filter((e) => e.source === node.id);

  const neighborsBox = document.createElement("div");
  neighborsBox.style.cssText = "padding: 10px 12px; font-size: 11px; display: flex; flex-direction: column; gap: 8px;";

  // Inbound parents
  const inBox = document.createElement("div");
  inBox.innerHTML = `<div style="font-weight: 600; color: var(--lab-text-secondary); margin-bottom: 4px;">Causal Inbound (${inEdges.length})</div>`;
  if (inEdges.length === 0) {
    inBox.innerHTML += `<div style="color: var(--lab-text-muted);">No inbound causal edges (root)</div>`;
  } else {
    inEdges.forEach((edge) => {
      const srcNode = graph.nodes.find((n) => n.id === edge.source);
      const btn = document.createElement("button");
      btn.style.cssText = "display: block; margin-top: 2px; background: none; border: 1px solid var(--lab-border); color: var(--lab-accent); border-radius: 3px; padding: 2px 6px; cursor: pointer; text-align: left;";
      btn.textContent = `↖ ${formatSeq(srcNode?.seq)} ${srcNode?.kind ?? edge.source} [${edge.relation ?? "causal"}]`;
      btn.onclick = () => store.selection.selectTraceNode(edge.source, srcNode?.seq);
      inBox.appendChild(btn);
    });
  }
  neighborsBox.appendChild(inBox);

  // Outbound children
  const outBox = document.createElement("div");
  outBox.innerHTML = `<div style="font-weight: 600; color: var(--lab-text-secondary); margin-bottom: 4px;">Causal Outbound (${outEdges.length})</div>`;
  if (outEdges.length === 0) {
    outBox.innerHTML += `<div style="color: var(--lab-text-muted);">No outbound causal edges (leaf)</div>`;
  } else {
    outEdges.forEach((edge) => {
      const tgtNode = graph.nodes.find((n) => n.id === edge.target);
      const btn = document.createElement("button");
      btn.style.cssText = "display: block; margin-top: 2px; background: none; border: 1px solid var(--lab-border); color: var(--lab-accent); border-radius: 3px; padding: 2px 6px; cursor: pointer; text-align: left;";
      btn.textContent = `↘ ${formatSeq(tgtNode?.seq)} ${tgtNode?.kind ?? edge.target} [${edge.relation ?? "causal"}]`;
      btn.onclick = () => store.selection.selectTraceNode(edge.target, tgtNode?.seq);
      outBox.appendChild(btn);
    });
  }
  neighborsBox.appendChild(outBox);

  container.appendChild(neighborsBox);

  return container;
}
