import type { EventEnvelope } from "../contract/index.js";

export type InternedRow = {
  readonly index: number;
  readonly seq: bigint;
  readonly occurredAtMs: number;
  readonly kindId: number;
  readonly runIdString: string;
  readonly spanId: string;
  readonly parentRowIndex: number;
  readonly envelope: EventEnvelope;
};

export type RowRange = {
  readonly rows: readonly InternedRow[];
  readonly minSeq: bigint;
  readonly maxSeq: bigint;
};

export class ColumnarEventStore {
  private readonly cap: number;
  private count: number = 0;

  // Hot columnar parallel arrays
  private readonly seq: BigInt64Array;
  private readonly occurredAt: Float64Array;
  private readonly kind: Uint16Array;
  private readonly parent: Int32Array;

  // Stored rows and secondary lookups
  private readonly rows: InternedRow[] = [];
  private readonly kindToId: Map<string, number> = new Map();
  private readonly idToKind: string[] = [];
  private readonly spanToRowIndex: Map<string, number> = new Map();
  private readonly seqToRowIndex: Map<string, number> = new Map();
  private readonly unknownKinds: Set<string> = new Set();
  private lastSeq: bigint = 0n;
  private readonly gaps: Array<{ from: bigint; to: bigint }> = [];

  constructor(capacity: number = 100_000) {
    this.cap = capacity;
    this.seq = new BigInt64Array(capacity);
    this.occurredAt = new Float64Array(capacity);
    this.kind = new Uint16Array(capacity);
    this.parent = new Int32Array(capacity);
  }

  private internKind(kind: string): number {
    let id = this.kindToId.get(kind);
    if (id === undefined) {
      id = this.idToKind.length;
      this.idToKind.push(kind);
      this.kindToId.set(kind, id);
    }
    return id;
  }

  public getKindName(id: number): string {
    return this.idToKind[id] ?? "unknown";
  }

  public append(envelope: EventEnvelope): InternedRow {
    const rawSeq = BigInt(envelope.seq);
    const existingIndex = this.seqToRowIndex.get(envelope.eventId);
    if (existingIndex !== undefined) {
      // Event identity is canonical. A repeated sequence with another event is retained
      // so callers can surface the contradiction instead of silently losing data.
      return this.rows[existingIndex]!;
    }

    const index = this.count;
    if (index >= this.cap) {
      throw new Error(`EventStore capacity exceeded: ${this.cap}`);
    }

    const kindName = String(envelope.payload?.kind ?? "unknown");
    const kindId = this.internKind(kindName);
    const occurredAtMs = Date.parse(envelope.occurredAt) || Date.now();

    // Check parent resolution
    let parentIndex = -1;
    if (envelope.parentEventId && this.spanToRowIndex.has(envelope.parentEventId)) {
      parentIndex = this.spanToRowIndex.get(envelope.parentEventId)!;
    }

    this.seq[index] = rawSeq;
    this.occurredAt[index] = occurredAtMs;
    this.kind[index] = kindId;
    this.parent[index] = parentIndex;

    const row: InternedRow = {
      index,
      seq: rawSeq,
      occurredAtMs,
      kindId,
      runIdString: envelope.runId ?? "",
      spanId: envelope.spanId,
      parentRowIndex: parentIndex,
      envelope,
    };

    this.rows.push(row);
    this.spanToRowIndex.set(envelope.spanId, index);
    if (envelope.eventId) {
      this.spanToRowIndex.set(envelope.eventId, index);
    }
    this.seqToRowIndex.set(envelope.seq, index);
    this.seqToRowIndex.set(envelope.eventId, index);
    if (this.lastSeq > 0n && rawSeq > this.lastSeq + 1n) {
      this.gaps.push({ from: this.lastSeq + 1n, to: rawSeq - 1n });
    }
    if (rawSeq > this.lastSeq) this.lastSeq = rawSeq;
    this.count++;

    return row;
  }

  public appendBatch(envelopes: readonly EventEnvelope[]): readonly InternedRow[] {
    const results: InternedRow[] = [];
    for (const env of envelopes) {
      results.push(this.append(env));
    }
    return results;
  }

  public size(): number {
    return this.count;
  }

  public getRow(index: number): InternedRow | undefined {
    return this.rows[index];
  }

  public getAllRows(): readonly InternedRow[] {
    return this.rows;
  }

  public slice(fromSeq: bigint, toSeq: bigint): RowRange {
    const filtered = this.rows.filter((r) => r.seq >= fromSeq && r.seq <= toSeq);
    return {
      rows: filtered,
      minSeq: filtered.length > 0 ? filtered[0]!.seq : fromSeq,
      maxSeq: filtered.length > 0 ? filtered[filtered.length - 1]!.seq : toSeq,
    };
  }

  public clear(): void {
    this.count = 0;
    this.rows.length = 0;
    this.kindToId.clear();
    this.idToKind.length = 0;
    this.spanToRowIndex.clear();
    this.seqToRowIndex.clear();
    this.unknownKinds.clear();
    this.lastSeq = 0n;
    this.gaps.length = 0;
  }

  public getGaps(): readonly { from: bigint; to: bigint }[] {
    return this.gaps;
  }
}
