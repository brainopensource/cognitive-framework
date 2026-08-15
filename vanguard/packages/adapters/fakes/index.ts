/** Deterministic, in-memory port implementations. No I/O and no system clock. */
import { sha256, type CapabilityGrant, type Digest, type EffectDescriptor, type EventEnvelope, type EvidenceClaim, type Json, type Receipt } from "../../domain/contracts.ts";
import type {
  Blob,
  BlobStore,
  ClockPort,
  ContextBundle,
  EffectPreview,
  EnvironmentAdapter,
  EnvironmentProfile,
  EnvironmentSnapshot,
  Evaluation,
  EvaluatorPort,
  EventRange,
  EventStore,
  IndexPort,
  IndexQuery,
  ModelProposal,
  ModelProvider,
  Observation,
  ObservationRequest,
  PortFailure,
  RandomPort,
  RankedRef,
  Reconciliation,
  Result,
  RunRef,
  Sampling,
  ToolSchema,
} from "../../ports/contracts.ts";

const ok = <T>(value: T): Result<T> => ({ ok: true, value });
const failure = (kind: PortFailure["kind"], message: string, retryable = false): Result<never> => ({ ok: false, error: { kind, message, retryable } });
const copy = (bytes: Uint8Array): Uint8Array => new Uint8Array(bytes);

export class ScriptedModelProvider implements ModelProvider {
  private cursor = 0;
  private readonly replies: readonly Result<ModelProposal>[];
  constructor(replies: readonly Result<ModelProposal>[]) { this.replies = replies; }
  async propose(_context: ContextBundle, _tools: readonly ToolSchema[], _sampling: Sampling): Promise<Result<ModelProposal>> {
    const reply = this.replies[this.cursor++];
    return reply ?? failure("instrument_error", "fake model script exhausted");
  }
}

export class InMemoryEnvironmentAdapter implements EnvironmentAdapter {
  private disposed = false;
  private revision = 0;
  private readonly resources: Readonly<Record<string, string>>;
  private readonly profileValue: EnvironmentProfile;
  constructor(resources: Readonly<Record<string, string>> = {}, profileValue: EnvironmentProfile = { name: "fake", version: "1", contained: false }) {
    this.resources = resources;
    this.profileValue = profileValue;
  }
  async profile(): Promise<Result<EnvironmentProfile>> { return ok(this.profileValue); }
  async snapshot(): Promise<Result<EnvironmentSnapshot>> {
    if (this.disposed) return failure("unavailable", "environment is disposed");
    return ok({ id: `fake-snapshot-${this.revision}`, digest: sha256({ resources: this.resources, revision: this.revision }) });
  }
  async observe(request: ObservationRequest, _grant: CapabilityGrant): Promise<Result<Observation>> {
    if (this.disposed) return failure("unavailable", "environment is disposed");
    return ok({ snapshot: request.snapshot, content: JSON.stringify(this.resources), provenanceLabel: "fake.environment" });
  }
  async preview(descriptor: EffectDescriptor): Promise<Result<EffectPreview>> { return ok({ descriptor, summary: `fake preview: ${descriptor.name}` }); }
  async apply(_grant: CapabilityGrant | undefined, descriptor: EffectDescriptor): Promise<Result<Receipt>> {
    if (this.disposed) return failure("unavailable", "environment is disposed");
    this.revision += 1;
    return ok({ descriptorDigest: descriptor.digest, outcome: "ok", observedAt: "2000-01-01T00:00:00.000Z", resultDigest: sha256({ descriptor: descriptor.digest, revision: this.revision }), affectedResources: [] });
  }
  async reconcile(receipt: Receipt): Promise<Result<Reconciliation>> { return ok({ receipt, status: receipt.outcome === "undeterminable" ? "undeterminable" : "confirmed" }); }
  async dispose(): Promise<Result<undefined>> { this.disposed = true; return ok(undefined); }
}

export class FixedEvaluatorPort implements EvaluatorPort {
  private readonly evaluation: Evaluation;
  constructor(evaluation: Evaluation) { this.evaluation = evaluation; }
  async evaluate(_run: RunRef, _protocol: Digest): Promise<Result<Evaluation>> { return ok(this.evaluation); }
}

export class InMemoryEventStore implements EventStore {
  private readonly events: EventEnvelope[] = [];
  async append(events: readonly EventEnvelope[]): Promise<Result<undefined>> {
    const prior = this.events.at(-1)?.seq;
    if (prior !== undefined && events.some((event) => BigInt(event.seq) <= BigInt(prior))) return failure("conflict", "event sequence must be monotonic");
    this.events.push(...events.map((event) => structuredClone(event)));
    return ok(undefined);
  }
  async read(range: EventRange): Promise<Result<readonly EventEnvelope[]>> {
    const after = range.afterSeq === undefined ? -1n : BigInt(range.afterSeq);
    const filtered = this.events.filter((event) => (range.runId === undefined || event.runId === range.runId) && BigInt(event.seq) > after);
    return ok(filtered.slice(0, range.limit ?? filtered.length).map((event) => structuredClone(event)));
  }
  async digest(): Promise<Result<Digest>> { return ok(sha256(this.events as unknown as Json)); }
}

export class InMemoryBlobStore implements BlobStore {
  private readonly blobs = new Map<Digest, Blob>();
  async put(blob: Blob): Promise<Result<Digest>> {
    const digest = sha256([...blob.bytes]);
    if (!this.blobs.has(digest)) this.blobs.set(digest, { bytes: copy(blob.bytes), classification: blob.classification });
    return ok(digest);
  }
  async get(digest: Digest): Promise<Result<Blob>> {
    const blob = this.blobs.get(digest);
    return blob === undefined ? failure("not_found", `blob not found: ${digest}`) : ok({ bytes: copy(blob.bytes), classification: blob.classification });
  }
}

export class FixedIndexPort implements IndexPort {
  private readonly entries: readonly RankedRef[];
  constructor(entries: readonly RankedRef[]) { this.entries = entries; }
  async query(query: IndexQuery): Promise<Result<readonly RankedRef[]>> {
    return ok(this.entries.filter((entry) => entry.ref.includes(query.text)).slice(0, query.limit));
  }
}

export class FixedClock implements ClockPort {
  private readonly instant: string;
  constructor(instant = "2000-01-01T00:00:00.000Z") { this.instant = instant; }
  now(): string { return this.instant; }
}

export class SeededRandom implements RandomPort {
  private state: number;
  constructor(seed = 1) { this.state = seed >>> 0; }
  next(): Uint8Array {
    const bytes = new Uint8Array(16);
    for (let index = 0; index < bytes.length; index += 1) {
      this.state = (Math.imul(1664525, this.state) + 1013904223) >>> 0;
      bytes[index] = this.state >>> 24;
    }
    return bytes;
  }
}

export const fakeFailure = failure;
