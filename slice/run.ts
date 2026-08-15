import { OpenAiCompatibleSliceProvider } from "./provider.ts";

const endpoint = process.env.VG_SLICE_ENDPOINT;
const apiKey = process.env.VG_SLICE_API_KEY;
const model = process.env.VG_SLICE_MODEL;
if (!endpoint || !apiKey || !model) {
  console.error("VG_SLICE_ENDPOINT, VG_SLICE_API_KEY and VG_SLICE_MODEL are required; no request was made.");
  process.exitCode = 2;
} else {
  const provider = new OpenAiCompatibleSliceProvider({ endpoint, apiKey, model }, fetch as never);
  const result = await provider.propose({ blocks: [{ label: "slice.task", content: "Reply with the word READY." }] }, [], { temperature: 0, maxTokens: 16 });
  // The API key and provider response body are never logged.
  console.log(JSON.stringify(result.ok
    ? { ok: true, textLength: result.value.text.length, toolCallCount: result.value.toolCalls.length }
    : { ok: false, error: result.error }));
  if (!result.ok) process.exitCode = 1;
}
