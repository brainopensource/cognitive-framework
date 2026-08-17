import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import {
  buildResumeRequest,
  describeResumeFailure,
  formatExplanation,
  whyFromResult,
  selectSessionChrome,
  attachLive,
  emptyRunView,
  ReplayRuntimeClient,
  LiveRuntimeClient,
  fail,
} from "../src/index.js";
import type { EventEnvelope, Result, RunRef, ArtifactExplanation } from "../src/index.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WHY_FIXTURE_PATH = path.resolve(__dirname, "../../../cli/fixtures/sessions/why-typed-tools.jsonl");

describe("FE-1-9 — Task A1: Resume Helpers", () => {
  it("buildResumeRequest refuses empty runId", () => {
    const res1 = buildResumeRequest("");
    assert.ok(!res1.ok);
    if (!res1.ok) {
      assert.equal(res1.error.code, "invalid_request");
    }

    const res2 = buildResumeRequest("   ");
    assert.ok(!res2.ok);
  });

  it("buildResumeRequest builds valid request object", () => {
    const res = buildResumeRequest("run-123", "chk-456");
    assert.ok(res.ok);
    if (res.ok) {
      assert.equal(res.value.runId, "run-123");
      assert.equal(res.value.checkpointId, "chk-456");
    }
  });

  it("describeResumeFailure maps codes to stable verbatim messages", () => {
    const notAvail: Result<RunRef> = fail("not_available", "daemon down", true);
    assert.equal(describeResumeFailure(notAvail), "Runtime daemon is unreachable on unix socket");

    const notFound: Result<RunRef> = fail("not_found", "missing run", false);
    assert.equal(describeResumeFailure(notFound), "Run or checkpoint not found");

    const permDenied: Result<RunRef> = fail("permission_denied", "no access", false);
    assert.equal(describeResumeFailure(permDenied), "Permission denied");

    const okRes: Result<RunRef> = { ok: true, value: { runId: "run-1" } };
    assert.equal(describeResumeFailure(okRes), "");
  });
});

describe("FE-1-10 — Task A2: Why & Artifact Projection", () => {
  it("formatExplanation detects empty vs non-empty explanation", () => {
    const emptyExp: ArtifactExplanation = {
      artifactId: "art-1",
      status: "unknown",
      prediction: "",
      activatedBy: [],
      demotedBy: [],
      freshness: { source: "replay" },
    };
    const f1 = formatExplanation(emptyExp);
    assert.equal(f1.status, "unknown");
    assert.ok(f1.empty);

    const activeExp: ArtifactExplanation = {
      artifactId: "art-2",
      status: "active",
      activatedBy: [{ evidence: "evt-1" }],
      demotedBy: [],
      prediction: "Keep active",
      freshness: { source: "replay" },
    };
    const f2 = formatExplanation(activeExp);
    assert.equal(f2.status, "active");
    assert.equal(f2.prediction, "Keep active");
    assert.ok(!f2.empty);
  });

  it("whyFromResult never synthesizes ActivationChanged on failure", () => {
    const errRes: Result<ArtifactExplanation> = fail("not_found", "artifact missing", false);
    const res = whyFromResult(errRes);
    assert.ok(!res.ok);
    if (!res.ok) {
      assert.equal(res.error.code, "not_found");
    }
  });

  it("golden test: ReplayRuntimeClient whyFromResult on fixture", async () => {
    const text = fs.readFileSync(WHY_FIXTURE_PATH, "utf8");
    const client = ReplayRuntimeClient.fromJsonl(text);
    const expResult = await client.explainArtifact("typed-tools");
    const whyRes = whyFromResult(expResult);
    assert.ok(whyRes.ok);
    if (whyRes.ok) {
      assert.equal(whyRes.value.status, "active");
      assert.ok(!whyRes.value.empty);
    }

    const missingResult = await client.explainArtifact("missing-artifact");
    const missingWhy = whyFromResult(missingResult);
    assert.ok(missingWhy.ok);
    if (missingWhy.ok) {
      assert.equal(missingWhy.value.status, "unknown");
      assert.ok(missingWhy.value.empty);
    }
  });
});

describe("FE-1-11 — Task A3 & B1: Session Chrome & attachLive Factory", () => {
  it("selectSessionChrome combines status bar and session attributes", () => {
    const view = emptyRunView();
    const chrome = selectSessionChrome({
      view,
      source: "live",
      lastSeq: "100",
      runId: "run-xyz",
      daemon: "running",
    });
    assert.equal(chrome.source, "live");
    assert.equal(chrome.seq, "100");
    assert.equal(chrome.runId, "run-xyz");
    assert.equal(chrome.daemon, "running");
  });

  it("attachLive creates LiveRuntimeClient without spawning child processes", async () => {
    const client = attachLive({ socketPath: "/tmp/nonexistent-vanguard-test.sock" });
    assert.ok(client);
    const status = await client.getDaemonStatus();
    assert.ok(!status.ok);
    if (!status.ok) {
      assert.equal(status.error.code, "not_available");
    }
  });

  it("streamReconnect respects afterSeq cursor", async () => {
    const jsonl = [
      JSON.stringify({
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
      }),
      JSON.stringify({
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
      }),
    ];

    async function* feed() {
      for (const line of jsonl) yield line;
    }

    const client = new LiveRuntimeClient(feed());
    const items = [];
    for await (const item of client.streamEvents({ runId: "run-1", afterSeq: "1" })) {
      if (item.ok) items.push(item.value);
    }
    assert.equal(items.length, 1);
    assert.equal(items[0]?.envelope.seq, "2");
  });
});
