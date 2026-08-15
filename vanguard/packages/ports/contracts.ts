/**
 * Runtime seams. This package owns interfaces and typed failures only; it has
 * no concrete implementation, clock, filesystem, process or network access.
 */
import type {
  CapabilityGrant,
  Digest,
  EffectDescriptor,
  EventEnvelope,
  EvidenceClaim,
  Json,
  Receipt,
  ResourceSelector,
} from "../domain/contracts.ts";

export type Result<T, E extends PortFailure = PortFailure> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export type PortFailure = {
  readonly kind: "instrument_error" | "denied" | "not_found" | "conflict" | "unavailable" | "invalid_request";
  readonly message: string;
  readonly retryable: boolean;
};

export type ModelProposal = { readonly text: string; readonly toolCalls: readonly { readonly name: string; readonly arguments: Json }[] };
export type ContextBundle = { readonly blocks: readonly { readonly label: string; readonly content: string }[] };
export type ToolSchema = { readonly name: string; readonly schema: Json };
export type Sampling = { readonly temperature: number; readonly maxTokens: number };

export interface ModelProvider {
  propose(context: ContextBundle, tools: readonly ToolSchema[], sampling: Sampling): Promise<Result<ModelProposal>>;
}

export type EnvironmentProfile = { readonly name: string; readonly version: string; readonly contained: boolean };
export type EnvironmentSnapshot = { readonly id: string; readonly digest: Digest };
export type ObservationRequest = { readonly selector: ResourceSelector; readonly snapshot: EnvironmentSnapshot };
export type Observation = { readonly snapshot: EnvironmentSnapshot; readonly content: string; readonly provenanceLabel: string };
export type EffectPreview = { readonly descriptor: EffectDescriptor; readonly summary: string };
export type Reconciliation = { readonly receipt: Receipt; readonly status: "confirmed" | "undeterminable" };

export interface EnvironmentAdapter {
  profile(): Promise<Result<EnvironmentProfile>>;
  snapshot(): Promise<Result<EnvironmentSnapshot>>;
  observe(request: ObservationRequest, grant: CapabilityGrant): Promise<Result<Observation>>;
  preview(descriptor: EffectDescriptor): Promise<Result<EffectPreview>>;
  apply(grant: CapabilityGrant | undefined, descriptor: EffectDescriptor): Promise<Result<Receipt>>;
  reconcile(receipt: Receipt): Promise<Result<Reconciliation>>;
  dispose(): Promise<Result<undefined>>;
}

export type RunRef = { readonly runId: string; readonly episodeId: string };
export type Evaluation = { readonly outcome: "satisfied" | "unsatisfied" | "inconclusive"; readonly claims: readonly EvidenceClaim[]; readonly reason?: string };

export interface EvaluatorPort {
  evaluate(run: RunRef, protocol: Digest): Promise<Result<Evaluation>>;
}

export type EventRange = { readonly runId?: string; readonly afterSeq?: string; readonly limit?: number };

export interface EventStore {
  append(events: readonly EventEnvelope[]): Promise<Result<undefined>>;
  read(range: EventRange): Promise<Result<readonly EventEnvelope[]>>;
  digest(): Promise<Result<Digest>>;
}

export type Blob = { readonly bytes: Uint8Array; readonly classification: "public" | "internal" | "confidential" | "restricted" };

export interface BlobStore {
  put(blob: Blob): Promise<Result<Digest>>;
  get(digest: Digest): Promise<Result<Blob>>;
}

export type IndexQuery = { readonly text: string; readonly limit: number };
export type RankedRef = { readonly ref: string; readonly score: number };

export interface IndexPort {
  query(query: IndexQuery): Promise<Result<readonly RankedRef[]>>;
}

export interface ClockPort {
  now(): string;
}

export interface RandomPort {
  next(): Uint8Array;
}
