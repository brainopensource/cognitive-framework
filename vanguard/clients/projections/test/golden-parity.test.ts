import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { readFileSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import {
  foldEvents,
  toTraceGraph,
  emptyEvidenceGrid,
  reduceEvidence,
} from "../src/index.js";
import { parseJsonlLine, type EventEnvelope } from "@aether/contracts";

function findRepoRoot(startDir: string): string {
  let cur = startDir;
  while (cur !== "/" && cur.length > 1) {
    if (existsSync(join(cur, "package.json")) && existsSync(join(cur, "vanguard"))) {
      return cur;
    }
    cur = resolve(cur, "..");
  }
  return startDir;
}

function loadFixture(relPath: string): EventEnvelope[] {
  const root = findRepoRoot(process.cwd());
  const fullPath = join(root, relPath);
  if (!existsSync(fullPath)) {
    throw new Error(`Fixture not found: ${fullPath}`);
  }
  const content = readFileSync(fullPath, "utf-8");
  const lines = content.split("\n").filter((l) => l.trim().length > 0);
  const envelopes: EventEnvelope[] = [];
  for (const line of lines) {
    const res = parseJsonlLine(line);
    if (res.ok) envelopes.push(res.value);
  }
  return envelopes;
}

describe("@aether/projections — Golden Trajectory Fixture Parity", () => {
  it("folds successful-episode.jsonl into deterministic satisfied state", () => {
    const envelopes = loadFixture("vanguard/clients/cli/fixtures/successful-episode.jsonl");
    assert.equal(envelopes.length, 4);

    const snapshot = foldEvents(envelopes);
    assert.equal(snapshot.status, "satisfied");
    assert.equal(snapshot.verdict, "satisfied");
    assert.equal(snapshot.lastSeq, "4");

    const graph = toTraceGraph(envelopes);
    assert.equal(graph.nodes.length, 4);
    assert.equal(graph.edges.length, 3); // Linear sequence links 1->2->3->4

    let grid = emptyEvidenceGrid(snapshot.runId);
    for (const env of envelopes) {
      grid = reduceEvidence(grid, env);
    }
    assert.equal(grid.verdicts.length, 1);
    assert.equal(grid.verdicts[0]?.verdict, "satisfied");
  });

  it("folds why-typed-tools.jsonl into deterministic state", () => {
    const envelopes = loadFixture("vanguard/clients/cli/fixtures/why-typed-tools.jsonl");
    assert.ok(envelopes.length > 0, "Fixture should have events");

    const snapshot = foldEvents(envelopes);
    assert.ok(snapshot.lastSeq !== "0");

    const graph = toTraceGraph(envelopes);
    assert.equal(graph.nodes.length, envelopes.length);
  });
});
