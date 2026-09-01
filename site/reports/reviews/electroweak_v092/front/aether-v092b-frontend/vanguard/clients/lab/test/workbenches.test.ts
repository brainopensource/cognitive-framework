import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { LabStore } from "../src/state/lab-store.js";
import { WorkbenchRegistry } from "../src/components/workbenches/workbench-registry.js";
import { setupDomMock } from "./dom-mock.js";

describe("@aether/lab — Workbench Rendering", () => {
  before(() => {
    setupDomMock();
  });

  it("renders all 6 workbenches via WorkbenchRegistry without throwing", () => {
    const store = new LabStore({
      runs: [
        {
          runId: "run-001",
          status: "satisfied",
          seq: "10",
          occurredAt: "2026-08-29T20:00:00Z",
          verdict: "satisfied",
        },
      ],
    });

    const registry = new WorkbenchRegistry();

    const runsEl = registry.render("runs", store);
    assert.equal(runsEl.className, "aether-runs-workbench");

    const eventsEl = registry.render("events", store);
    assert.equal(eventsEl.className, "aether-events-workbench");

    const traceEl = registry.render("trace", store);
    assert.equal(traceEl.className, "aether-trace-workbench");

    const artifactsEl = registry.render("artifacts", store);
    assert.equal(artifactsEl.className, "aether-artifacts-workbench");

    const contextEl = registry.render("context", store);
    assert.equal(contextEl.className, "aether-context-workbench");

    const systemEl = registry.render("system", store);
    assert.equal(systemEl.className, "aether-system-workbench");
  });
});
