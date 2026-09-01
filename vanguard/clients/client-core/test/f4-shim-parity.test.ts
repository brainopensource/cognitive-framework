import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

/**
 * F4 Phase 1: the 7 leaf application modules ported this phase
 * (run-view, trace-graph, budget, coding-types, graph-model, mcnemar,
 * projection-model) now live in @aether/client, with these modules'
 * originals turned into re-export shims
 * (`export * from "@aether/client/application/X.js"`).
 *
 * This guards the "zero divergence" claim in the F4 plan directly: every
 * shimmed export must be the *same* function/value object as the
 * @aether/client export, not a re-implementation that happens to agree
 * today. If a future edit accidentally forks one side, this fails.
 */

describe("F4 Phase 1 — client-core shims resolve to @aether/client (no fork)", () => {
  it("run-view: reduceRunView and emptyRunView are identical across both entry points", async () => {
    const fromClient = await import("@aether/client/application/run-view.js");
    const fromShim = await import("../src/application/run-view.js");
    assert.equal(fromShim.reduceRunView, fromClient.reduceRunView);
    assert.equal(fromShim.emptyRunView, fromClient.emptyRunView);
  });

  it("trace-graph: toTraceGraph is identical across both entry points", async () => {
    const fromClient = await import("@aether/client/application/trace-graph.js");
    const fromShim = await import("../src/application/trace-graph.js");
    assert.equal(fromShim.toTraceGraph, fromClient.toTraceGraph);
  });

  it("budget, coding-types, graph-model, mcnemar, projection-model, approvals, subscribe-run, selectors, coding-receipts modules resolve identically", async () => {
    const modules = [
      "budget.js",
      "coding-types.js",
      "graph-model.js",
      "mcnemar.js",
      "projection-model.js",
      "approvals.js",
      "subscribe-run.js",
      "selectors.js",
      "coding-receipts.js",
    ];
    for (const file of modules) {
      const fromClient = (await import(`@aether/client/application/${file}`)) as Record<string, unknown>;
      const fromShim = (await import(`../src/application/${file}`)) as Record<string, unknown>;
      const clientKeys = Object.keys(fromClient).sort();
      assert.ok(clientKeys.length > 0, `${file} exports nothing`);
      for (const key of clientKeys) {
        assert.equal(fromShim[key], fromClient[key], `${file}:${key} diverged from @aether/client`);
      }
    }
  });
});
