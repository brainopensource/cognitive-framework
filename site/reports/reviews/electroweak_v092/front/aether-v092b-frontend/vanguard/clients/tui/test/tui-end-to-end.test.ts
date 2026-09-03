import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { PassThrough } from "node:stream";
import { readFileSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { TuiApplication } from "../src/app.js";
import { ReplayRuntimeClient } from "@aether/client";
import { parseJsonlLine, type EventEnvelope } from "@aether/contracts";

function findRepoRoot(startDir: string): string {
  let cur = resolve(startDir);
  while (true) {
    if (existsSync(join(cur, "package.json")) && existsSync(join(cur, "vanguard"))) {
      return cur;
    }
    const parent = resolve(cur, "..");
    if (parent === cur) {
      break;
    }
    cur = parent;
  }
  return startDir;
}

function loadFixture(relPath: string): EventEnvelope[] {
  const root = findRepoRoot(process.cwd());
  const fullPath = join(root, relPath);
  const content = readFileSync(fullPath, "utf-8");
  const lines = content.split("\n").filter((l) => l.trim().length > 0);
  const envelopes: EventEnvelope[] = [];
  for (const line of lines) {
    const res = parseJsonlLine(line);
    if (res.ok) envelopes.push(res.value);
  }
  return envelopes;
}

describe("@aether/tui — End-to-End Simulation", () => {
  it("runs full TUI application against replay fixture and projects satisfied state", async () => {
    const envelopes = loadFixture("vanguard/clients/cli/fixtures/successful-episode.jsonl");
    const client = ReplayRuntimeClient.fromEnvelopes(envelopes);

    const stream = new PassThrough();
    let written = "";
    stream.on("data", (chunk) => {
      written += chunk.toString("utf-8");
    });

    const app = new TuiApplication({
      client,
      screenOptions: { stdout: stream as any, colorMode: "plain" },
    });

    app.screen.resize(100, 30);

    // Ingest fixture stream
    for (const env of envelopes) {
      app.store.ingestEnvelope(env);
    }

    app.renderFrame();

    assert.equal(app.store.get().snapshot.status, "satisfied");
    assert.ok(written.includes("AETHER"));
    assert.ok(written.includes("SATISFIED"));
  });
});
