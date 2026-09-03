import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { KeyboardManager } from "../src/shortcuts/keyboard-manager.js";
import { LabStore } from "../src/state/lab-store.js";
import { setupDomMock } from "./dom-mock.js";
import type { EventEnvelope } from "@aether/contracts";

function createMockEnvelope(seq: string, kind: string): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId: `evt-${seq}`,
    scope: "episode",
    traceId: "trace-01",
    spanId: `span-${seq}`,
    seq,
    occurredAt: "2026-08-29T20:00:00.000Z",
    recordedAt: "2026-08-29T20:00:00.050Z",
    principal: "operator",
    tenantId: "tenant-default",
    ownerId: "owner-default",
    confidentiality: "public",
    retentionClass: "standard",
    trainability: "allowed",
    redactionStatus: "none",
    payload: { kind },
  };
}

describe("@aether/lab — Keyboard Navigation Manager", () => {
  before(() => {
    setupDomMock();
  });

  it("handles number keys 1-6 to switch workbenches", () => {
    const store = new LabStore();
    const km = new KeyboardManager(store);

    km.handleKeyDown({ key: "2", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().activeWorkbench, "events");

    km.handleKeyDown({ key: "3", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().activeWorkbench, "trace");

    km.handleKeyDown({ key: "4", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().activeWorkbench, "artifacts");

    km.handleKeyDown({ key: "5", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().activeWorkbench, "context");

    km.handleKeyDown({ key: "6", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().activeWorkbench, "system");

    km.handleKeyDown({ key: "1", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().activeWorkbench, "runs");
  });

  it("handles event ledger navigation (j/k) and jumping to live (l)", () => {
    const store = new LabStore();
    store.ingestEnvelope(createMockEnvelope("1", "GoalDeclared"));
    store.ingestEnvelope(createMockEnvelope("2", "TurnStarted"));
    store.ingestEnvelope(createMockEnvelope("3", "EpisodeCompleted"));

    const km = new KeyboardManager(store);

    // Press j to select first event
    km.handleKeyDown({ key: "j", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().selectedEventId, "evt-1");

    // Press j again for next event
    km.handleKeyDown({ key: "j", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().selectedEventId, "evt-2");

    // Press k for previous event
    km.handleKeyDown({ key: "k", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().selectedEventId, "evt-1");

    // Press l to jump to live
    store.setIsUserScrolledUp(true);
    km.handleKeyDown({ key: "l", preventDefault: () => {} } as any);
    assert.equal(store.get().isUserScrolledUp, false);
  });

  it("handles inspector toggle (i, Enter, Escape)", () => {
    const store = new LabStore();
    const km = new KeyboardManager(store);

    assert.equal(store.selection.get().inspectorOpen, false);

    km.handleKeyDown({ key: "i", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().inspectorOpen, true);

    km.handleKeyDown({ key: "Escape", preventDefault: () => {} } as any);
    assert.equal(store.selection.get().inspectorOpen, false);
  });
});
