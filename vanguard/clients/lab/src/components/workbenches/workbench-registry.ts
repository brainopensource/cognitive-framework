import type { LabStore } from "../../state/lab-store.js";
import type { WorkbenchId } from "../../state/selection-model.js";
import type { RuntimeClient } from "@aether/client";

import { renderRunsWorkbench } from "./RunsWorkbench.js";
import { renderEventsWorkbench } from "./EventsWorkbench.js";
import { renderTraceWorkbench } from "./TraceWorkbench.js";
import { renderArtifactsWorkbench } from "./ArtifactsWorkbench.js";
import { renderContextWorkbench } from "./ContextWorkbench.js";
import { renderSystemWorkbench } from "./SystemWorkbench.js";

export type WorkbenchRenderer = (store: LabStore, client?: RuntimeClient) => HTMLElement;

export class WorkbenchRegistry {
  private renderers: Map<WorkbenchId, WorkbenchRenderer> = new Map();

  constructor() {
    this.renderers.set("runs", renderRunsWorkbench);
    this.renderers.set("events", renderEventsWorkbench);
    this.renderers.set("trace", renderTraceWorkbench);
    this.renderers.set("artifacts", renderArtifactsWorkbench);
    this.renderers.set("context", renderContextWorkbench);
    this.renderers.set("system", renderSystemWorkbench);
  }

  public render(id: WorkbenchId, store: LabStore, client?: RuntimeClient): HTMLElement {
    const renderer = this.renderers.get(id);
    if (!renderer) {
      const fallback = document.createElement("div");
      fallback.textContent = `Workbench ${id} not found`;
      return fallback;
    }
    return renderer(store, client);
  }
}
