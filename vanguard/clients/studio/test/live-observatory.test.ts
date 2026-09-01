import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { spawn, type ChildProcessWithoutNullStreams } from "node:child_process";
import { createInterface } from "node:readline";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { HttpRuntimeClient } from "@vanguard/client-core/adapters/http.js";

import { ColumnarEventStore } from "../src/store/event-store.js";
import { StudioFoldEngine } from "../src/store/fold.js";

/**
 * F6: Studio Observatory live wiring, verified end-to-end.
 *
 * `useStudioRuntime` (src/runtime/StudioRuntime.tsx) drives the Observatory by
 * subscribing `HttpRuntimeClient.streamEvents()` into `ColumnarEventStore` +
 * `StudioFoldEngine`. This test exercises that exact same pipeline -- minus the
 * React state wrapper, which needs a DOM harness this package does not have --
 * against a real running `studio_gateway.py` process, not a fixture. It proves
 * the live transport really reaches the fold engine, not just that the fold
 * engine folds correctly (already covered by studio.test.ts's fixture-based
 * cases).
 */

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../../../../..");
const GATEWAY_SCRIPT = path.join(REPO_ROOT, "test", "runtime", "fixtures", "run_studio_gateway_for_test.py");

function startGateway(): Promise<{ proc: ChildProcessWithoutNullStreams; port: number }> {
  return new Promise((resolve, reject) => {
    const proc = spawn("python3", [GATEWAY_SCRIPT], {
      cwd: REPO_ROOT,
      env: { ...process.env, PYTHONPATH: REPO_ROOT },
    });
    const rl = createInterface({ input: proc.stdout });
    const timeout = setTimeout(() => reject(new Error("gateway did not report a port in time")), 10_000);
    rl.on("line", (line) => {
      const match = /^PORT (\d+)$/.exec(line.trim());
      if (match) {
        clearTimeout(timeout);
        resolve({ proc, port: Number(match[1]) });
      }
    });
    proc.on("error", reject);
    proc.stderr.on("data", () => {}); // drained, not asserted on
  });
}

describe("Studio Observatory live wiring (F6)", () => {
  it("folds a real gateway's live event stream through StudioFoldEngine", async () => {
    const { proc, port } = await startGateway();
    try {
      const client = new HttpRuntimeClient({ baseUrl: `http://127.0.0.1:${port}` });
      const runId = `run-observatory-${Date.now()}`;

      const started = await client.startRun({ runId, repo: ".", brief: "F6 live wiring check" });
      assert.equal(started.ok, true, "startRun failed");

      const store = new ColumnarEventStore();
      const engine = new StudioFoldEngine();
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5_000);

      let sawEvent = false;
      for await (const result of client.streamEvents({ runId }, controller.signal)) {
        if (!result.ok) break;
        sawEvent = true;
        store.append(result.value.envelope);
        break; // one real event is enough to prove the pipeline is live, not stubbed
      }
      clearTimeout(timeout);

      assert.equal(sawEvent, true, "no live event reached the client from the real gateway");

      const fold = engine.foldAll(store.getAllRows());
      assert.ok(fold.atSeq > 0n, "fold engine did not advance past a real live event");
    } finally {
      proc.kill();
    }
  });
});
