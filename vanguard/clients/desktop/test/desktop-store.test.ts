import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { DesktopStore } from "../src/state/desktop-store.js";
import { groupSessionsByDate, filterSessions, type SessionSummary } from "../src/state/session-history.js";
import type { EventEnvelope } from "@aether/contracts";

const TEST_SESSIONS: SessionSummary[] = [
  {
    sessionId: "s1",
    title: "TableWorld Memory Optimization",
    agentId: "coding-agent",
    workspacePath: "/repo",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    turnCount: 3,
  },
  {
    sessionId: "s2",
    title: "Kernel Dispatch Lease Fix",
    agentId: "coding-agent",
    workspacePath: "/repo",
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    updatedAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    turnCount: 5,
  },
];

const FIXTURE_EVENT: EventEnvelope = {
  schemaVersion: "vg.4",
  eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
  scope: "episode",
  runId: "run-d-1",
  episodeId: "ep-d-1",
  traceId: "t-1",
  spanId: "s-1",
  seq: "1",
  occurredAt: "2026-08-29T20:00:00.000Z",
  recordedAt: "2026-08-29T20:00:00.001Z",
  principal: "user",
  tenantId: "t",
  ownerId: "o",
  confidentiality: "internal",
  retentionClass: "standard",
  trainability: "prohibited",
  redactionStatus: "none",
  payload: { kind: "GoalDeclared", goal: "Resolve TableWorld leak" },
};

describe("@aether/desktop — Session History & Store", () => {
  it("groups sessions by date (Today, Last 7 Days)", () => {
    const groups = groupSessionsByDate(TEST_SESSIONS);
    assert.ok(groups.some((g) => g.label === "Today"));
    assert.ok(groups.some((g) => g.label === "Last 7 Days"));
  });

  it("filters sessions by search query", () => {
    const filtered = filterSessions(TEST_SESSIONS, "TableWorld");
    assert.equal(filtered.length, 1);
    assert.equal(filtered[0]?.sessionId, "s1");
  });

  it("ingests event envelopes and projects conversation turns", () => {
    const store = new DesktopStore();
    store.ingestEnvelope(FIXTURE_EVENT);

    const s = store.get();
    assert.equal(s.runId, "run-d-1");
    assert.equal(s.turns.length, 1);
    assert.equal(s.turns[0]?.text, "Resolve TableWorld leak");
  });

  it("creates new chat and resets active session state", () => {
    const store = new DesktopStore();
    store.ingestEnvelope(FIXTURE_EVENT);
    assert.equal(store.get().turns.length, 1);

    store.newChat();
    assert.equal(store.get().turns.length, 0);
    assert.equal(store.get().runId, "");
    assert.equal(store.get().sessions.length, 2);
  });
});
