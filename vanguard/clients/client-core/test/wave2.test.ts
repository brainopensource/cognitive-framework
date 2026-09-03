import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import {
  selectStatusBar,
  windowTranscript,
  toTraceGraph,
  subscribeRun,
  parseJsonlLine,
  emptyRunView,
  reduceRunView,
} from "../src/index.js";
import type { EventEnvelope, RuntimeClient, StreamItem } from "../src/index.js";
// F4 Phase 2: subscribeRun is now a re-export shim onto @aether/client, whose
// StreamItem (from @aether/contracts) is a strict superset of this package's
// own contract/types.js StreamItem (contractVersion: "0.1" | "vg.4" vs "0.1"
// only). The items subscribeRun actually yields are typed by the former.
import type { StreamItem as WireStreamItem } from "@aether/contracts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_PATH = path.resolve(__dirname, "../../../cli/fixtures/successful-episode.jsonl");

describe("FE-1-6 — Selectors & Transcript Windowing", () => {
  it("selectStatusBar produces status bar view model", () => {
    const view = { ...emptyRunView(), tokens: 150, costMicros: "300", lastKind: "EpisodeStarted" };
    const bar = selectStatusBar({ view, source: "live", lastSeq: "42" });
    assert.equal(bar.source, "live");
    assert.equal(bar.seq, "42");
    assert.equal(bar.tokens, 150);
    assert.equal(bar.costMicros, "300");
    assert.equal(bar.kind, "EpisodeStarted");
  });

  it("windowTranscript defaults height to 16 and clamps cursor", () => {
    let vm = emptyRunView();
    for (let i = 0; i < 20; i++) {
      vm = reduceRunView(vm, {
        schemaVersion: "vg.4",
        eventId: `018f3a2b-7c4d-7e1f-9a2b-${String(i).padStart(12, "0")}`,
        scope: "episode",
        runId: "run-1",
        episodeId: "ep-1",
        traceId: "t-1",
        spanId: "s-1",
        seq: String(i + 1),
        occurredAt: "2026-08-15T00:00:00.000Z",
        recordedAt: "2026-08-15T00:00:00.001Z",
        principal: "agent",
        tenantId: "t",
        ownerId: "o",
        confidentiality: "internal",
        retentionClass: "standard",
        trainability: "prohibited",
        redactionStatus: "none",
        payload: { kind: "ObservationProduced", text: `thought ${i}` },
      });
    }

    // Total rows = 20 thoughts
    const w1 = windowTranscript(vm, 0); // default height 16
    assert.equal(w1.total, 20);
    assert.equal(w1.rows.length, 16);
    assert.equal(w1.cursor, 0);
    assert.equal(w1.rows[0]?.kind, "thought");

    // Over-clamped cursor (cursor = 100 -> clamped to 20 - 16 = 4)
    const w2 = windowTranscript(vm, 100, 16);
    assert.equal(w2.cursor, 4);
    assert.equal(w2.rows.length, 16);

    // Negative cursor clamped to 0
    const w3 = windowTranscript(vm, -5, 10);
    assert.equal(w3.cursor, 0);
    assert.equal(w3.rows.length, 10);
  });
});

describe("FE-1-7 — toTraceGraph", () => {
  it("projects DAG nodes and edges from fixture envelopes", () => {
    const text = fs.readFileSync(FIXTURE_PATH, "utf8");
    const envelopes: EventEnvelope[] = [];
    for (const line of text.split("\n")) {
      if (!line.trim()) continue;
      const parsed = parseJsonlLine(line);
      if (parsed.ok) envelopes.push(parsed.value);
    }

    const { nodes, edges } = toTraceGraph(envelopes);
    assert.equal(nodes.length, envelopes.length);
    assert.ok(nodes.length > 0);
    assert.equal(nodes[0]!.id, envelopes[0]!.eventId);
    assert.equal(nodes[0]!.kind, envelopes[0]!.payload.kind);

    // Sequential fallback edges connect consecutive events in same runId
    assert.equal(edges.length, envelopes.length - 1);
    assert.equal(edges[0]!.source, envelopes[0]!.eventId);
    assert.equal(edges[0]!.target, envelopes[1]!.eventId);
  });

  it("handles explicit parentEventId relationships", () => {
    const envs: EventEnvelope[] = [
      {
        schemaVersion: "vg.4",
        eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
        scope: "episode",
        runId: "run-1",
        episodeId: "ep-1",
        traceId: "t-1",
        spanId: "s-1",
        seq: "1",
        occurredAt: "2026-08-15T00:00:00.000Z",
        recordedAt: "2026-08-15T00:00:00.001Z",
        principal: "agent",
        tenantId: "t",
        ownerId: "o",
        confidentiality: "internal",
        retentionClass: "standard",
        trainability: "prohibited",
        redactionStatus: "none",
        payload: { kind: "EpisodeStarted" },
      },
      {
        schemaVersion: "vg.4",
        eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000002",
        parentEventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
        scope: "episode",
        runId: "run-1",
        episodeId: "ep-1",
        traceId: "t-1",
        spanId: "s-2",
        seq: "2",
        occurredAt: "2026-08-15T00:00:00.010Z",
        recordedAt: "2026-08-15T00:00:00.011Z",
        principal: "agent",
        tenantId: "t",
        ownerId: "o",
        confidentiality: "internal",
        retentionClass: "standard",
        trainability: "prohibited",
        redactionStatus: "none",
        payload: { kind: "UnknownFutureKind" },
      },
    ];

    const graph = toTraceGraph(envs);
    assert.equal(graph.nodes.length, 2);
    assert.equal(graph.nodes[1]!.kind, "UnknownFutureKind");
    assert.equal(graph.edges.length, 1);
    assert.equal(graph.edges[0]!.source, envs[0]!.eventId);
    assert.equal(graph.edges[0]!.target, envs[1]!.eventId);
  });
});

describe("FE-1-8 — subscribeRun", () => {
  it("subscribes to stream, invokes handlers, and completes on done", async () => {
    const fakeClient: Pick<RuntimeClient, "streamEvents"> = {
      async *streamEvents() {
        yield {
          ok: true,
          value: {
            contractVersion: "0.1",
            source: "replay",
            envelope: {
              schemaVersion: "vg.4",
              eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
              scope: "episode",
              runId: "run-1",
              episodeId: "ep-1",
              traceId: "t-1",
              spanId: "s-1",
              seq: "1",
              occurredAt: "2026-08-15T00:00:00.000Z",
              recordedAt: "2026-08-15T00:00:00.001Z",
              principal: "agent",
              tenantId: "t",
              ownerId: "o",
              confidentiality: "internal",
              retentionClass: "standard",
              trainability: "prohibited",
              redactionStatus: "none",
              payload: { kind: "EpisodeStarted" },
            },
          },
        };
      },
    };

    const items: WireStreamItem[] = [];
    let doneCalled = false;

    await subscribeRun(fakeClient, { runId: "run-1" }, {
      onItem: (item) => items.push(item),
      onDone: () => { doneCalled = true; },
    });

    assert.equal(items.length, 1);
    assert.equal(items[0]?.envelope.payload.kind, "EpisodeStarted");
    assert.ok(doneCalled);
  });

  it("handles AbortSignal early termination cleanly", async () => {
    const controller = new AbortController();
    const fakeClient: Pick<RuntimeClient, "streamEvents"> = {
      async *streamEvents(_cursor, signal) {
        yield {
          ok: true,
          value: {
            contractVersion: "0.1",
            source: "replay",
            envelope: {
              schemaVersion: "vg.4",
              eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
              scope: "episode",
              runId: "run-1",
              episodeId: "ep-1",
              traceId: "t-1",
              spanId: "s-1",
              seq: "1",
              occurredAt: "2026-08-15T00:00:00.000Z",
              recordedAt: "2026-08-15T00:00:00.001Z",
              principal: "agent",
              tenantId: "t",
              ownerId: "o",
              confidentiality: "internal",
              retentionClass: "standard",
              trainability: "prohibited",
              redactionStatus: "none",
              payload: { kind: "EpisodeStarted" },
            },
          },
        };
        controller.abort();
        if (signal?.aborted) return;
        yield {
          ok: true,
          value: {
            contractVersion: "0.1",
            source: "replay",
            envelope: {
              schemaVersion: "vg.4",
              eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000002",
              scope: "episode",
              runId: "run-1",
              episodeId: "ep-1",
              traceId: "t-1",
              spanId: "s-2",
              seq: "2",
              occurredAt: "2026-08-15T00:00:00.010Z",
              recordedAt: "2026-08-15T00:00:00.011Z",
              principal: "agent",
              tenantId: "t",
              ownerId: "o",
              confidentiality: "internal",
              retentionClass: "standard",
              trainability: "prohibited",
              redactionStatus: "none",
              payload: { kind: "EpisodeCompleted" },
            },
          },
        };
      },
    };

    const items: WireStreamItem[] = [];
    await subscribeRun(fakeClient, { runId: "run-1" }, {
      onItem: (item) => items.push(item),
    }, controller.signal);

    assert.equal(items.length, 1);
  });
});
