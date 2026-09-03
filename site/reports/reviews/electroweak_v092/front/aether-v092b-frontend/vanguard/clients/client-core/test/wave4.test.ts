import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import * as fs from "node:fs";
import {
  attachLive,
  selectSessionChrome,
  emptyRunView,
  LiveRuntimeClient,
  ReplayRuntimeClient,
} from "../src/index.js";

describe("FE-1 Wave 4 — Honest Live Attach & Socket Bounds", () => {
  it("attachLive ALWAYS constructs LiveRuntimeClient and NEVER ReplayRuntimeClient", () => {
    const client = attachLive({ socketPath: "/tmp/nonexistent-vanguard-test-wave4.sock" });
    assert.ok(client instanceof LiveRuntimeClient, "attachLive must return LiveRuntimeClient");
    assert.ok(!(client instanceof ReplayRuntimeClient), "attachLive must never return ReplayRuntimeClient");
  });

  it("missing UDS socket returns typed not_available fail-closed without hanging", async () => {
    const client = attachLive({ socketPath: "/tmp/nonexistent-vanguard-test-wave4.sock" });
    const statusResult = await client.getDaemonStatus();
    assert.ok(!statusResult.ok, "getDaemonStatus must fail on missing socket");
    if (!statusResult.ok) {
      assert.equal(statusResult.error.code, "not_available");
      assert.ok(statusResult.error.message.includes("unreachable") || statusResult.error.message.includes("ENOENT") || statusResult.error.message.includes("refused") || statusResult.error.message.includes("daemon"));
    }

    const startResult = await client.startRun({ repo: "." });
    assert.ok(!startResult.ok, "startRun must fail on missing socket");
    if (!startResult.ok) {
      assert.equal(startResult.error.code, "not_available");
    }
  });

  it("afterSeq reconnect stream filtering resumes without inventing events", async () => {
    const jsonlLines = [
      JSON.stringify({
        schemaVersion: "vg.4",
        eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
        scope: "episode",
        runId: "run-w4",
        episodeId: "ep-w4",
        traceId: "t-w4",
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
      }),
      JSON.stringify({
        schemaVersion: "vg.4",
        eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000002",
        scope: "episode",
        runId: "run-w4",
        episodeId: "ep-w4",
        traceId: "t-w4",
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
        payload: { kind: "ObservationProduced", text: "resumed item" },
      }),
    ];

    async function* lineFeed() {
      for (const line of jsonlLines) yield line;
    }

    const client = new LiveRuntimeClient(lineFeed());
    const items = [];
    for await (const item of client.streamEvents({ runId: "run-w4", afterSeq: "1" })) {
      if (item.ok) items.push(item.value);
    }

    assert.equal(items.length, 1);
    assert.equal(items[0]?.envelope.seq, "2");
    assert.equal(items[0]?.envelope.payload.kind, "ObservationProduced");
  });

  it("selectSessionChrome never invents daemon version or running state without evidence", () => {
    const view = emptyRunView();

    // Default without explicit daemon status
    const chromeDefault = selectSessionChrome({ view, source: "unknown" });
    assert.equal(chromeDefault.daemon, "unknown");
    assert.equal(chromeDefault.source, "unknown");

    // Explicit not_available
    const chromeNotAvail = selectSessionChrome({ view, source: "unknown", daemon: "not_available" });
    assert.equal(chromeNotAvail.daemon, "not_available");

    // Explicit running
    const chromeRunning = selectSessionChrome({ view, source: "live", daemon: "running" });
    assert.equal(chromeRunning.daemon, "running");
  });

  it("LIVE=1 e2e against pre-started UDS socket (skips if absent)", async () => {
    if (process.env.LIVE !== "1") {
      return; // Skip when LIVE is not set
    }
    const socketPath = process.env.VANGUARD_RUNTIME_SOCKET || "/tmp/vanguard-runtime.sock";
    if (!fs.existsSync(socketPath)) {
      return; // Skip gracefully if socket path does not exist
    }

    const client = attachLive({ socketPath });
    const status = await client.getDaemonStatus();
    assert.ok(status.ok, "Live daemon status must succeed when pre-started UDS socket exists");
  });
});
