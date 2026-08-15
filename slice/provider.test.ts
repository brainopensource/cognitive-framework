import test from "node:test";
import assert from "node:assert/strict";
import { OpenAiCompatibleSliceProvider } from "./provider.ts";

test("the disposable provider converts an HTTP failure into an instrument error", async () => {
  const provider = new OpenAiCompatibleSliceProvider(
    { endpoint: "https://example.invalid", apiKey: "test-secret", model: "test" },
    async () => ({ ok: false, status: 429, json: async () => ({}) }),
  );
  const result = await provider.propose({ blocks: [] }, [], { temperature: 0, maxTokens: 1 });
  assert.equal(result.ok, false);
  if (!result.ok) {
    assert.equal(result.error.kind, "instrument_error");
    assert.equal(result.error.retryable, true);
    assert.doesNotMatch(result.error.message, /test-secret/);
  }
});
