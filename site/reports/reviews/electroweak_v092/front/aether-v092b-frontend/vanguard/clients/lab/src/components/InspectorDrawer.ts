import type { LabStore } from "../state/lab-store.js";
import type { InspectorTab } from "../state/selection-model.js";
import type { RuntimeClient } from "@aether/client";
import { renderEventPayloadInspector } from "./inspectors/EventPayloadInspector.js";
import { renderApprovalInspector } from "./inspectors/ApprovalInspector.js";
import { renderArtifactDetailInspector } from "./inspectors/ArtifactDetailInspector.js";
import { renderTraceNodeInspector } from "./inspectors/TraceNodeInspector.js";
import { renderContextLayerInspector } from "./inspectors/ContextLayerInspector.js";
import { renderJsonPayloadTree } from "./JsonPayloadTree.js";

export function renderInspectorDrawer(store: LabStore, client?: RuntimeClient): HTMLElement | null {
  const sel = store.selection.get();
  if (!sel.inspectorOpen) return null;

  const drawer = document.createElement("aside");
  drawer.className = "aether-inspector-drawer";
  drawer.setAttribute("role", "region");
  drawer.setAttribute("aria-label", "Selection Inspector");
  drawer.style.cssText = `
    width: 380px;
    min-width: 300px;
    max-width: 600px;
    height: 100%;
    background: var(--lab-bg-surface);
    border-left: 1px solid var(--lab-border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    z-index: 10;
  `;

  // Tab Header Bar
  const tabHeader = document.createElement("div");
  tabHeader.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--lab-bg-panel);
    border-bottom: 1px solid var(--lab-border);
    padding: 0 8px;
    height: 36px;
    user-select: none;
  `;

  const tabsContainer = document.createElement("div");
  tabsContainer.style.cssText = "display: flex; gap: 4px; overflow-x: auto;";

  const tabs: Array<{ id: InspectorTab; label: string }> = [
    { id: "payload", label: "Payload" },
    { id: "approval", label: "Approval" },
    { id: "artifact", label: "Artifact" },
    { id: "node", label: "Trace Node" },
    { id: "context", label: "Context" },
    { id: "raw", label: "Raw JSON" },
  ];

  for (const t of tabs) {
    const tabBtn = document.createElement("button");
    const isActive = sel.activeInspectorTab === t.id;
    tabBtn.style.cssText = `
      background: ${isActive ? "var(--lab-bg-surface)" : "transparent"};
      color: ${isActive ? "var(--lab-accent)" : "var(--lab-text-secondary)"};
      border: none;
      border-bottom: ${isActive ? "2px solid var(--lab-accent)" : "2px solid transparent"};
      padding: 8px 10px;
      font-size: 11px;
      font-weight: ${isActive ? "600" : "500"};
      cursor: pointer;
      font-family: var(--lab-font-sans);
    `;
    tabBtn.textContent = t.label;
    tabBtn.onclick = () => store.selection.setInspectorTab(t.id);
    tabsContainer.appendChild(tabBtn);
  }

  tabHeader.appendChild(tabsContainer);

  const closeBtn = document.createElement("button");
  closeBtn.style.cssText = `
    background: none;
    border: none;
    color: var(--lab-text-muted);
    cursor: pointer;
    font-size: 14px;
    padding: 4px 8px;
  `;
  closeBtn.textContent = "✕";
  closeBtn.title = "Close inspector (Esc)";
  closeBtn.onclick = () => store.selection.toggleInspector(false);
  tabHeader.appendChild(closeBtn);

  drawer.appendChild(tabHeader);

  // Content Pane
  const contentPane = document.createElement("div");
  contentPane.style.cssText = "flex: 1; overflow: hidden; display: flex; flex-direction: column;";

  switch (sel.activeInspectorTab) {
    case "payload":
      contentPane.appendChild(renderEventPayloadInspector(store));
      break;
    case "approval":
      contentPane.appendChild(renderApprovalInspector(store, client));
      break;
    case "artifact":
      contentPane.appendChild(renderArtifactDetailInspector(store, client));
      break;
    case "node":
      contentPane.appendChild(renderTraceNodeInspector(store));
      break;
    case "context":
      contentPane.appendChild(renderContextLayerInspector(store));
      break;
    case "raw": {
      const events = store.get().events;
      const event = events.find((e) => e.eventId === sel.selectedEventId);
      contentPane.appendChild(
        renderJsonPayloadTree({
          data: event || store.get().snapshot,
          rootName: event ? "event_envelope" : "run_snapshot",
          defaultExpandedDepth: 2,
          selection: store.selection,
        })
      );
      break;
    }
  }

  drawer.appendChild(contentPane);
  return drawer;
}
