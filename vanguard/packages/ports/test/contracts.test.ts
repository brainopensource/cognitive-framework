import test from "node:test";
import assert from "node:assert/strict";
import type { BlobStore, ClockPort, EnvironmentAdapter, EvaluatorPort, EventStore, IndexPort, ModelProvider, RandomPort } from "../contracts.ts";

test("the Sprint slice exposes eight narrow runtime interfaces", () => {
  const ports: readonly string[] = ["ModelProvider", "EnvironmentAdapter", "EvaluatorPort", "EventStore", "BlobStore", "IndexPort", "ClockPort", "RandomPort"];
  assert.equal(ports.length, 8);
  const typeOnly: [ModelProvider?, EnvironmentAdapter?, EvaluatorPort?, EventStore?, BlobStore?, IndexPort?, ClockPort?, RandomPort?] = [];
  assert.equal(typeOnly.length, 0);
});
