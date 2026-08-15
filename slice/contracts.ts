/**
 * Disposable T0b provider vocabulary.
 *
 * This file intentionally lives inside slice/: it is not a production port
 * and is deleted with the walking skeleton at the S4 exit gate.
 */
export type Json = null | boolean | number | string | readonly Json[] | { readonly [key: string]: Json };

export type PortFailure = {
  readonly kind: "instrument_error" | "invalid_request";
  readonly message: string;
  readonly retryable: boolean;
};

export type Result<T> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: PortFailure };

export type ContextBundle = { readonly blocks: readonly { readonly label: string; readonly content: string }[] };
export type ToolSchema = { readonly name: string; readonly schema: Json };
export type Sampling = { readonly temperature: number; readonly maxTokens: number };
export type ModelProposal = {
  readonly text: string;
  readonly toolCalls: readonly { readonly name: string; readonly arguments: Json }[];
};

export interface SliceModelProvider {
  propose(
    context: ContextBundle,
    tools: readonly ToolSchema[],
    sampling: Sampling,
  ): Promise<Result<ModelProposal>>;
}
