import test from "node:test";
import assert from "node:assert/strict";
import { createServer, type Socket } from "node:net";
import { unlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { LiveRuntimeClient } from "../src/adapters/live.js";
import { parseDaemonFrame } from "../src/contract/parse.js";
import type { EventEnvelope } from "../src/contract/types.js";

function envelope(seq: string, kind: string, extra: Record<string, unknown> = {}): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
    scope: "episode",
    runId: "run-1",
    episodeId: "episode-1",
    traceId: "trace-1",
    spanId: "span-1",
    seq,
    occurredAt: "2026-08-15T00:00:00.000Z",
    recordedAt: "2026-08-15T00:00:00.001Z",
    principal: "agent-1",
    tenantId: "tenant-default",
    ownerId: "owner-platform",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind, ...extra },
  };
}

test("parseDaemonFrame never accepts unparsed objects as events", () => {
  const parsed = parseDaemonFrame({ frameType: "event", event: { not: "an envelope" } });
  assert.equal(parsed.ok, false);
});

test("socket transport reconnects after drop and resumes afterSeq", async () => {
  const socketPath = join(tmpdir(), `vg-test-${process.pid}-${Date.now()}.sock`);
  let connections = 0;
  const server = createServer((conn: Socket) => {
    connections += 1;
    let buf = "";
    conn.on("data", (chunk) => {
      buf += String(chunk);
      if (!buf.includes("\n")) return;
      if (connections === 1) {
        conn.write(JSON.stringify({ version: "vg.4", frameType: "event", event: envelope("1", "EpisodeStarted") }) + "\n");
        conn.destroy();
        return;
      }
      conn.write(JSON.stringify({ version: "vg.4", frameType: "event", event: envelope("2", "EpisodeCompleted", { outcome: "satisfied" }) }) + "\n");
      conn.end();
    });
  });
  await new Promise<void>((resolve) => server.listen(socketPath, resolve));
  try {
    const client = new LiveRuntimeClient(undefined, {
      socketPath,
      connectTimeoutMs: 500,
      commandTimeoutMs: 500,
      maxReconnects: 5,
      backoffMs: 20,
    });
    const kinds: string[] = [];
    for await (const item of client.streamEvents({ runId: "run-1" })) {
      if (item.ok) kinds.push(item.value.envelope.payload.kind);
      if (kinds.includes("EpisodeCompleted")) break;
    }
    assert.ok(connections >= 2);
    assert.deepEqual(kinds, ["EpisodeStarted", "EpisodeCompleted"]);
  } finally {
    server.close();
    try {
      unlinkSync(socketPath);
    } catch {
      /* ignore */
    }
  }
});
