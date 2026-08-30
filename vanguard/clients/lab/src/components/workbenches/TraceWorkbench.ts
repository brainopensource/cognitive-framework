import type { LabStore } from "../../state/lab-store.js";
import type { TraceNode } from "@aether/projections";
import { formatSeq, truncateDigest } from "../../util/formatting.js";

type LayoutNode = TraceNode & {
  x: number;
  y: number;
  width: number;
  height: number;
  rank: number;
};

export function renderTraceWorkbench(store: LabStore): HTMLElement {
  const container = document.createElement("section");
  container.className = "aether-trace-workbench";
  container.setAttribute("role", "tabpanel");
  container.setAttribute("aria-label", "Causal Trace Workbench");
  container.style.cssText = `
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: var(--lab-bg);
    position: relative;
  `;

  const state = store.get();
  const sel = store.selection.get();
  const graph = state.traceGraph;

  // Toolbar
  const toolbar = document.createElement("div");
  toolbar.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background: var(--lab-bg-surface);
    border-bottom: 1px solid var(--lab-border);
    gap: 8px;
    z-index: 5;
  `;

  const left = document.createElement("div");
  left.style.cssText = "display: flex; align-items: center; gap: 8px;";

  const title = document.createElement("span");
  title.style.cssText = "font-weight: 600; font-size: 13px; color: var(--lab-text-primary);";
  title.textContent = `Causal Trace Graph (${graph.nodes.length} nodes, ${graph.edges.length} edges)`;
  left.appendChild(title);
  toolbar.appendChild(left);

  const right = document.createElement("div");
  right.style.cssText = "display: flex; align-items: center; gap: 6px;";

  // Zoom / Pan State
  let zoom = 1;
  let panX = 40;
  let panY = 40;
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;

  const zoomInBtn = document.createElement("button");
  zoomInBtn.style.cssText = "background: var(--lab-bg-panel); border: 1px solid var(--lab-border); color: var(--lab-text-primary); padding: 3px 8px; border-radius: 3px; cursor: pointer; font-size: 12px;";
  zoomInBtn.textContent = "+";
  zoomInBtn.title = "Zoom In";
  zoomInBtn.onclick = () => {
    zoom = Math.min(3, zoom + 0.2);
    applyTransform();
  };
  right.appendChild(zoomInBtn);

  const zoomOutBtn = document.createElement("button");
  zoomOutBtn.style.cssText = "background: var(--lab-bg-panel); border: 1px solid var(--lab-border); color: var(--lab-text-primary); padding: 3px 8px; border-radius: 3px; cursor: pointer; font-size: 12px;";
  zoomOutBtn.textContent = "-";
  zoomOutBtn.title = "Zoom Out";
  zoomOutBtn.onclick = () => {
    zoom = Math.max(0.2, zoom - 0.2);
    applyTransform();
  };
  right.appendChild(zoomOutBtn);

  const fitBtn = document.createElement("button");
  fitBtn.style.cssText = "background: var(--lab-bg-panel); border: 1px solid var(--lab-border); color: var(--lab-text-primary); padding: 3px 8px; border-radius: 3px; cursor: pointer; font-size: 11px;";
  fitBtn.textContent = "Fit";
  fitBtn.title = "Fit Graph";
  fitBtn.onclick = () => {
    zoom = 1;
    panX = 40;
    panY = 40;
    applyTransform();
  };
  right.appendChild(fitBtn);

  toolbar.appendChild(right);
  container.appendChild(toolbar);

  // SVG Canvas Area
  const canvasArea = document.createElement("div");
  canvasArea.style.cssText = `
    flex: 1;
    position: relative;
    overflow: hidden;
    cursor: grab;
    background-image: radial-gradient(var(--lab-border-subtle) 1px, transparent 1px);
    background-size: 20px 20px;
  `;

  if (graph.nodes.length === 0) {
    const empty = document.createElement("div");
    empty.style.cssText = "display: flex; height: 100%; align-items: center; justify-content: center; color: var(--lab-text-muted); font-size: 13px;";
    empty.textContent = "No causal trace nodes recorded for this run";
    canvasArea.appendChild(empty);
    container.appendChild(canvasArea);
    return container;
  }

  // Compute layered DAG Layout
  const layoutNodes = computeDagLayout(graph.nodes, graph.edges);

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", "100%");
  svg.style.cssText = "position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible;";

  // Defs: Arrowhead markers
  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  defs.innerHTML = `
    <marker id="arrow-causal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#58a6ff" />
    </marker>
    <marker id="arrow-sequence" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#545d68" />
    </marker>
  `;
  svg.appendChild(defs);

  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
  svg.appendChild(g);

  // 1. Draw Edges
  const nodeMap = new Map<string, LayoutNode>();
  layoutNodes.forEach((n) => nodeMap.set(n.id, n));

  for (const edge of graph.edges) {
    const src = nodeMap.get(edge.source);
    const tgt = nodeMap.get(edge.target);
    if (!src || !tgt) continue;

    const isCausal = edge.relation !== "sequence";

    const x1 = src.x + src.width;
    const y1 = src.y + src.height / 2;
    const x2 = tgt.x;
    const y2 = tgt.y + tgt.height / 2;

    const dx = Math.max(30, (x2 - x1) / 2);
    const pathData = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathData);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", isCausal ? "var(--lab-accent)" : "var(--lab-text-muted)");
    path.setAttribute("stroke-width", isCausal ? "2" : "1");
    if (!isCausal) {
      path.setAttribute("stroke-dasharray", "4 4");
    }
    path.setAttribute("marker-end", isCausal ? "url(#arrow-causal)" : "url(#arrow-sequence)");
    g.appendChild(path);
  }

  // 2. Draw Nodes
  for (const node of layoutNodes) {
    const isSelected = node.id === sel.selectedTraceNodeId;
    const isError = node.kind.includes("Failed") || node.kind.includes("Error");
    const isApproval = node.kind.includes("Approval");

    const nodeG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    nodeG.style.cursor = "pointer";

    // Node Box
    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", String(node.x));
    rect.setAttribute("y", String(node.y));
    rect.setAttribute("width", String(node.width));
    rect.setAttribute("height", String(node.height));
    rect.setAttribute("rx", "4");
    rect.setAttribute("fill", isSelected ? "var(--lab-bg-active)" : "var(--lab-bg-surface)");
    rect.setAttribute(
      "stroke",
      isSelected
        ? "var(--lab-accent)"
        : isError
        ? "var(--lab-danger)"
        : isApproval
        ? "var(--lab-warning)"
        : "var(--lab-border)"
    );
    rect.setAttribute("stroke-width", isSelected || isError || isApproval ? "2" : "1");
    nodeG.appendChild(rect);

    // Kind Text
    const kindText = document.createElementNS("http://www.w3.org/2000/svg", "text");
    kindText.setAttribute("x", String(node.x + 8));
    kindText.setAttribute("y", String(node.y + 18));
    kindText.setAttribute("fill", isError ? "var(--lab-danger)" : "var(--lab-text-primary)");
    kindText.setAttribute("font-size", "11");
    kindText.setAttribute("font-weight", "bold");
    kindText.setAttribute("font-family", "var(--lab-font-sans)");
    kindText.textContent = `${formatSeq(node.seq)} ${node.kind}`;
    nodeG.appendChild(kindText);

    // Summary Text
    const sumText = document.createElementNS("http://www.w3.org/2000/svg", "text");
    sumText.setAttribute("x", String(node.x + 8));
    sumText.setAttribute("y", String(node.y + 34));
    sumText.setAttribute("fill", "var(--lab-text-secondary)");
    sumText.setAttribute("font-size", "10");
    sumText.setAttribute("font-family", "var(--lab-font-mono)");
    const summary = node.summary ? truncateDigest(node.summary, 22) : truncateDigest(node.id, 12);
    sumText.textContent = summary;
    nodeG.appendChild(sumText);

    nodeG.onclick = (e) => {
      e.stopPropagation();
      store.selection.selectTraceNode(node.id, node.seq);
      refreshWorkbench();
    };

    g.appendChild(nodeG);
  }

  canvasArea.appendChild(svg);
  container.appendChild(canvasArea);

  function applyTransform() {
    g.setAttribute("transform", `translate(${panX}, ${panY}) scale(${zoom})`);
  }
  applyTransform();

  // Mouse pan event handlers
  canvasArea.onmousedown = (e) => {
    isDragging = true;
    dragStartX = e.clientX - panX;
    dragStartY = e.clientY - panY;
    canvasArea.style.cursor = "grabbing";
  };

  window.onmousemove = (e) => {
    if (!isDragging) return;
    panX = e.clientX - dragStartX;
    panY = e.clientY - dragStartY;
    applyTransform();
  };

  window.onmouseup = () => {
    isDragging = false;
    canvasArea.style.cursor = "grab";
  };

  function refreshWorkbench() {
    const parent = container.parentNode;
    if (parent) {
      const fresh = renderTraceWorkbench(store);
      parent.replaceChild(fresh, container);
    }
  }

  return container;
}

function computeDagLayout(nodes: TraceNode[], edges: Array<{ source: string; target: string }>): LayoutNode[] {
  const nodeWidth = 200;
  const nodeHeight = 44;
  const horizontalGap = 60;
  const verticalGap = 20;

  // 1. Assign ranks based on sequence index or topological depth
  const ranks = new Map<string, number>();
  const inDegree = new Map<string, number>();

  nodes.forEach((n) => {
    ranks.set(n.id, 0);
    inDegree.set(n.id, 0);
  });

  edges.forEach((e) => {
    inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
  });

  // Calculate topological rank
  nodes.forEach((n, idx) => {
    ranks.set(n.id, idx);
  });

  // 2. Position nodes in horizontal ranks
  const rankColumns = new Map<number, LayoutNode[]>();

  const layoutList: LayoutNode[] = nodes.map((n, idx) => {
    const rank = Math.floor(idx / 4);
    const colList = rankColumns.get(rank) || [];
    const indexInCol = colList.length;

    const layoutNode: LayoutNode = {
      ...n,
      rank,
      x: rank * (nodeWidth + horizontalGap),
      y: indexInCol * (nodeHeight + verticalGap),
      width: nodeWidth,
      height: nodeHeight,
    };

    colList.push(layoutNode);
    rankColumns.set(rank, colList);
    return layoutNode;
  });

  return layoutList;
}
