import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { SelectionModel } from "../src/state/selection-model.js";

describe("@aether/lab — Cross-Workbench Selection Model", () => {
  it("initializes default selection state and switches workbenches", () => {
    const sel = new SelectionModel();
    assert.equal(sel.get().activeWorkbench, "runs");
    assert.equal(sel.get().inspectorOpen, false);

    sel.setWorkbench("events");
    assert.equal(sel.get().activeWorkbench, "events");

    sel.setWorkbench("trace");
    assert.equal(sel.get().activeWorkbench, "trace");
  });

  it("selects event and synchronizes trace node and inspector tab", () => {
    const sel = new SelectionModel();
    sel.selectEvent("evt-10", "10");

    const state = sel.get();
    assert.equal(state.selectedEventId, "evt-10");
    assert.equal(state.selectedSeq, "10");
    assert.equal(state.selectedTraceNodeId, "evt-10");
    assert.equal(state.inspectorOpen, true);
    assert.equal(state.activeInspectorTab, "payload");
  });

  it("selects artifact and opens artifact tab in inspector", () => {
    const sel = new SelectionModel();
    sel.selectArtifact("sha256:deadbeef");

    const state = sel.get();
    assert.equal(state.selectedArtifactId, "sha256:deadbeef");
    assert.equal(state.inspectorOpen, true);
    assert.equal(state.activeInspectorTab, "artifact");
  });

  it("serializes and deserializes URL hash for deep linking", () => {
    const sel = new SelectionModel();
    sel.setWorkbench("events");
    sel.selectRun("run-42");
    sel.selectEvent("evt-99", "99");

    const hash = sel.toHashString();
    assert.ok(hash.startsWith("#events?"));
    assert.ok(hash.includes("runId=run-42"));
    assert.ok(hash.includes("eventId=evt-99"));
    assert.ok(hash.includes("seq=99"));

    const newSel = new SelectionModel();
    newSel.fromHashString(hash);

    assert.equal(newSel.get().activeWorkbench, "events");
    assert.equal(newSel.get().selectedRunId, "run-42");
    assert.equal(newSel.get().selectedEventId, "evt-99");
    assert.equal(newSel.get().selectedSeq, "99");
  });
});
