import type { ClientFailure, EventEnvelope, Result, StreamItem } from "./types.js";

const INT_STRING = /^(0|[1-9][0-9]*)$/;
const TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const DIGEST_REGEX = /^sha256:[0-9a-f]{64}$/;

const REQUIRED = [
  "schemaVersion",
  "eventId",
  "scope",
  "traceId",
  "spanId",
  "seq",
  "occurredAt",
  "recordedAt",
  "principal",
  "tenantId",
  "ownerId",
  "confidentiality",
  "retentionClass",
  "trainability",
  "redactionStatus",
  "payload",
] as const;

export function isUuid(value: unknown): value is string {
  return typeof value === "string" && UUID_REGEX.test(value);
}

export function isDigest(value: unknown): value is string {
  return typeof value === "string" && DIGEST_REGEX.test(value);
}

export function fail<T = never>(code: ClientFailure["code"], message: string, retryable = false): Result<T> {
  return { ok: false, error: { code, message, retryable } };
}

export function parseEventEnvelope(value: unknown): Result<EventEnvelope> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    return fail("invalid_request", "EventEnvelope must be a JSON object");
  }
  const source = value as Record<string, unknown>;
  for (const field of REQUIRED) {
    if (source[field] === undefined) return fail("invalid_request", `EventEnvelope missing ${field}`);
  }
  if (source.schemaVersion !== "vg.4") return fail("incompatible_version", "schemaVersion must be vg.4");
  if (!isUuid(source.eventId)) return fail("invalid_request", "EventEnvelope eventId must be a valid UUID");
  const scope = source.scope;
  if (scope !== "episode" && scope !== "governance" && scope !== "evolution" && scope !== "recovery") {
    return fail("invalid_request", "EventEnvelope scope is not recognised");
  }
  if (typeof source.seq !== "string" || !INT_STRING.test(source.seq)) return fail("invalid_request", "EventEnvelope seq must be an IntString");
  if (typeof source.occurredAt !== "string" || !TIMESTAMP.test(source.occurredAt)) return fail("invalid_request", "EventEnvelope occurredAt is not RFC 3339 UTC");
  if (typeof source.recordedAt !== "string" || !TIMESTAMP.test(source.recordedAt)) return fail("invalid_request", "EventEnvelope recordedAt is not RFC 3339 UTC");
  if ((scope === "episode" || scope === "recovery") && typeof source.runId !== "string") {
    return fail("invalid_request", `${scope} requires runId`);
  }
  if (scope === "episode" && typeof source.episodeId !== "string") return fail("invalid_request", "episode requires episodeId");
  if ((scope === "governance" || scope === "evolution") && source.runId !== undefined) {
    return fail("invalid_request", `${scope} cannot carry runId`);
  }
  const payload = source.payload;
  if (payload === null || typeof payload !== "object" || Array.isArray(payload) || typeof (payload as { kind?: unknown }).kind !== "string") {
    return fail("invalid_request", "EventEnvelope payload.kind is required");
  }
  return { ok: true, value: structuredClone(source) as EventEnvelope };
}

export function parseJsonlLine(line: string): Result<EventEnvelope> {
  const trimmed = line.trim();
  if (!trimmed) return fail("invalid_request", "empty JSONL line");
  let parsed: unknown;
  try {
    parsed = JSON.parse(trimmed);
  } catch {
    return fail("invalid_request", "JSONL line is not valid JSON");
  }
  if (parsed !== null && typeof parsed === "object" && "envelope" in parsed && "contractVersion" in parsed) {
    const item = parsed as Partial<StreamItem>;
    return parseEventEnvelope(item.envelope);
  }
  return parseEventEnvelope(parsed);
}

export function afterCursor(seq: string, afterSeq?: string): boolean {
  if (afterSeq === undefined) return true;
  const left = BigInt(seq);
  const right = BigInt(afterSeq);
  return left > right;
}

export type ParsedDaemonFrame =
  | { frameType: "receipt"; receipt: Record<string, unknown> }
  | { frameType: "error"; message: string }
  | { frameType: "event"; event: EventEnvelope }
  | { frameType: "command"; raw: Record<string, unknown> };

export function parseDaemonFrame(value: unknown): Result<ParsedDaemonFrame> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    return fail("invalid_request", "daemon frame must be a JSON object");
  }
  const source = value as Record<string, unknown>;
  const frameType = source.frameType;
  if (frameType === "error") {
    const err = source.error;
    const message =
      err !== null && typeof err === "object" && !Array.isArray(err) && typeof (err as { message?: unknown }).message === "string"
        ? (err as { message: string }).message
        : "daemon error frame";
    return { ok: true, value: { frameType: "error", message } };
  }
  if (frameType === "receipt") {
    const receipt = source.receipt;
    if (receipt === null || typeof receipt !== "object" || Array.isArray(receipt)) {
      return fail("invalid_request", "invalid response frame from daemon");
    }
    return { ok: true, value: { frameType: "receipt", receipt: receipt as Record<string, unknown> } };
  }
  if (frameType === "event") {
    const parsed = parseEventEnvelope(source.event);
    if (!parsed.ok) return parsed;
    return { ok: true, value: { frameType: "event", event: parsed.value } };
  }
  if (frameType === "command") {
    return { ok: true, value: { frameType: "command", raw: source } };
  }
  return fail("invalid_request", `unsupported daemon frameType ${String(frameType)}`);
}

export function parseDaemonLine(line: string): Result<ParsedDaemonFrame> {
  const trimmed = line.trim();
  if (!trimmed) return fail("invalid_request", "empty daemon line");
  let parsed: unknown;
  try {
    parsed = JSON.parse(trimmed);
  } catch {
    return fail("transport_interrupted", "malformed json frame", true);
  }
  return parseDaemonFrame(parsed);
}
