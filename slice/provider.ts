/**
 * Disposable provider adapter for T0b only. It is intentionally not reusable
 * production code and must be deleted at the S4 exit gate.
 */
import type { ContextBundle, ModelProposal, ModelProvider, PortFailure, Result, Sampling, ToolSchema } from "../vanguard/packages/ports/contracts.ts";

type FetchResponse = { readonly ok: boolean; readonly status: number; json(): Promise<unknown> };
type Fetch = (input: string, init: { method: string; headers: Record<string, string>; body: string }) => Promise<FetchResponse>;

const problem = (kind: PortFailure["kind"], message: string, retryable = false): Result<never> => ({ ok: false, error: { kind, message, retryable } });

export class OpenAiCompatibleSliceProvider implements ModelProvider {
  private readonly config: { endpoint: string; apiKey: string; model: string };
  private readonly request: Fetch;
  constructor(config: { endpoint: string; apiKey: string; model: string }, request: Fetch) {
    this.config = config;
    this.request = request;
  }

  async propose(context: ContextBundle, _tools: readonly ToolSchema[], sampling: Sampling): Promise<Result<ModelProposal>> {
    try {
      const response = await this.request(this.config.endpoint, {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${this.config.apiKey}` },
        body: JSON.stringify({ model: this.config.model, messages: context.blocks.map((block) => ({ role: "user", content: `[${block.label}] ${block.content}` })), temperature: sampling.temperature, max_tokens: sampling.maxTokens }),
      });
      if (!response.ok) return problem("instrument_error", `provider returned HTTP ${response.status}`, response.status === 429 || response.status >= 500);
      const body = await response.json();
      const text = extractText(body);
      return text === undefined ? problem("instrument_error", "provider response did not contain a text completion") : { ok: true, value: { text, toolCalls: [] } };
    } catch {
      return problem("instrument_error", "provider request failed", true);
    }
  }
}

function extractText(value: unknown): string | undefined {
  if (value === null || typeof value !== "object") return undefined;
  const choices = (value as { choices?: unknown }).choices;
  if (!Array.isArray(choices) || choices.length === 0 || choices[0] === null || typeof choices[0] !== "object") return undefined;
  const message = (choices[0] as { message?: unknown }).message;
  if (message === null || typeof message !== "object") return undefined;
  const content = (message as { content?: unknown }).content;
  return typeof content === "string" ? content : undefined;
}
