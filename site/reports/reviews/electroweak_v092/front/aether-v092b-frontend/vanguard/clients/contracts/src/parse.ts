import { fail, toClientFailureCode } from "./errors.js";
import type {
  CanonicalErrorCode,
  CommandReceipt,
  EventEnvelope,
  EventScope,
  PrincipalRole,
  Result,
  RuntimeServiceFrame,
  ServiceError,
} from "./types.js";

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const DIGEST_RE = /^sha256:[0-9a-f]{64}$/i;
const SCOPES = new Set<EventScope>(["episode", "governance", "evolution", "recovery"]);
const ROLES = new Set<PrincipalRole>(["user", "operator", "episode", "process", "evaluator", "release"]);

export function isUuid(value: unknown): value is string {
  return typeof value === "string" && UUID_RE.test(value);
}

export function isDigest(value: unknown): value is string {
  return typeof value === "string" && DIGEST_RE.test(value);
}

function isValidIsoDate(value: unknown): boolean {
  if (typeof value !== "string" || value.length < 10) return false;
  const t = Date.parse(value);
  return !Number.isNaN(t);
}

export function parseEventEnvelope(raw: unknown): Result<EventEnvelope> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return fail("invalid_request", "EventEnvelope must be a JSON object");
  }

  const obj = raw as Record<string, unknown>;

  if (obj.schemaVersion !== "vg.4") {
    return fail("incompatible_version", `Expected schemaVersion 'vg.4', got '${obj.schemaVersion}'`);
  }

  if (!isUuid(obj.eventId)) {
    return fail("invalid_request", `Invalid eventId format (expected UUID): '${obj.eventId}'`);
  }

  if (typeof obj.scope !== "string" || !SCOPES.has(obj.scope as EventScope)) {
    return fail("invalid_request", `Invalid scope: '${obj.scope}'`);
  }

  const requiredStrings = [
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
  ];

  for (const field of requiredStrings) {
    const val = obj[field];
    if (typeof val !== "string" && (field !== "seq" || typeof val !== "number")) {
      return fail("invalid_request", `Missing or invalid string field '${field}'`);
    }
  }

  if (!isValidIsoDate(obj.occurredAt)) {
    return fail("invalid_request", `Invalid occurredAt ISO timestamp: '${obj.occurredAt}'`);
  }

  if (!isValidIsoDate(obj.recordedAt)) {
    return fail("invalid_request", `Invalid recordedAt ISO timestamp: '${obj.recordedAt}'`);
  }

  if (obj.principalRole !== undefined) {
    if (typeof obj.principalRole !== "string" || !ROLES.has(obj.principalRole as PrincipalRole)) {
      return fail("invalid_request", `Invalid principalRole: '${obj.principalRole}'`);
    }
  }

  if (!obj.payload || typeof obj.payload !== "object" || Array.isArray(obj.payload)) {
    return fail("invalid_request", "EventEnvelope payload must be an object");
  }

  const payload = obj.payload as Record<string, unknown>;
  if (typeof payload.kind !== "string" || payload.kind.length === 0) {
    return fail("invalid_request", "EventEnvelope payload missing valid string 'kind'");
  }

  const envelope: EventEnvelope = {
    ...(obj as any),
    schemaVersion: "vg.4",
    eventId: obj.eventId as string,
    scope: obj.scope as EventScope,
    traceId: String(obj.traceId),
    spanId: String(obj.spanId),
    seq: String(obj.seq),
    occurredAt: String(obj.occurredAt),
    recordedAt: String(obj.recordedAt),
    principal: String(obj.principal),
    tenantId: String(obj.tenantId),
    ownerId: String(obj.ownerId),
    confidentiality: String(obj.confidentiality),
    retentionClass: String(obj.retentionClass),
    trainability: String(obj.trainability),
    redactionStatus: String(obj.redactionStatus),
    payload: {
      ...payload,
      kind: payload.kind,
    },
  };

  return { ok: true, value: envelope };
}

export function parseServiceError(raw: unknown): Result<ServiceError> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return fail("invalid_request", "ServiceError must be a JSON object");
  }
  const obj = raw as Record<string, unknown>;
  const code = toClientFailureCode(obj.code) as CanonicalErrorCode;
  const message = typeof obj.message === "string" && obj.message.length > 0 ? obj.message : "Runtime error";
  const retryable = typeof obj.retryable === "boolean" ? obj.retryable : false;
  return {
    ok: true,
    value: {
      code,
      message,
      retryable,
      correlationId: typeof obj.correlationId === "string" ? obj.correlationId : undefined,
      detail: typeof obj.detail === "string" ? obj.detail : undefined,
    },
  };
}

export function parseCommandReceipt(raw: unknown): Result<CommandReceipt> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return fail("invalid_request", "CommandReceipt must be a JSON object");
  }
  const obj = raw as Record<string, unknown>;
  if (typeof obj.commandId !== "string" || !obj.commandId) {
    return fail("invalid_request", "CommandReceipt missing commandId");
  }
  const status = obj.status === "error" ? "error" : "completed";
  let error: ServiceError | undefined;
  if (obj.error) {
    const parsedErr = parseServiceError(obj.error);
    if (parsedErr.ok) {
      error = parsedErr.value;
    }
  }
  return {
    ok: true,
    value: {
      commandId: obj.commandId,
      status,
      runId: typeof obj.runId === "string" ? obj.runId : undefined,
      result: obj.result && typeof obj.result === "object" ? (obj.result as Record<string, unknown>) : undefined,
      detail: typeof obj.detail === "string" ? obj.detail : undefined,
      error,
    },
  };
}

export function parseRuntimeServiceFrame(raw: unknown): Result<RuntimeServiceFrame> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return fail("invalid_request", "RuntimeServiceFrame must be a JSON object");
  }
  const obj = raw as Record<string, unknown>;
  if (obj.version !== "vg.4") {
    return fail("incompatible_version", `Frame version must be 'vg.4', got '${obj.version}'`);
  }
  const frameType = obj.frameType;
  if (typeof frameType !== "string") {
    return fail("invalid_request", "Frame missing frameType");
  }
  const frameId = typeof obj.frameId === "string" ? obj.frameId : "";
  if (!frameId) {
    return fail("invalid_request", "Frame missing non-empty frameId");
  }

  if (frameType === "command") {
    if (!obj.command || typeof obj.command !== "object") {
      return fail("invalid_request", "CommandFrame missing command object");
    }
    const cmd = obj.command as Record<string, unknown>;
    return {
      ok: true,
      value: {
        version: "vg.4",
        frameType: "command",
        frameId,
        command: {
          name: String(cmd.name ?? ""),
          commandId: String(cmd.commandId ?? ""),
          idempotencyKey: String(cmd.idempotencyKey ?? ""),
          runId: typeof cmd.runId === "string" ? cmd.runId : undefined,
          actor: typeof cmd.actor === "string" ? cmd.actor : undefined,
          payload: cmd.payload && typeof cmd.payload === "object" ? (cmd.payload as Record<string, unknown>) : undefined,
        },
      },
    };
  }

  if (frameType === "receipt") {
    if (!obj.receipt || typeof obj.receipt !== "object") {
      return fail("invalid_request", "ReceiptFrame missing receipt object");
    }
    const receiptRes = parseCommandReceipt(obj.receipt);
    if (!receiptRes.ok) return receiptRes;
    return {
      ok: true,
      value: {
        version: "vg.4",
        frameType: "receipt",
        frameId,
        inReplyTo: typeof obj.inReplyTo === "string" ? obj.inReplyTo : undefined,
        receipt: receiptRes.value,
      },
    };
  }

  if (frameType === "event") {
    if (!obj.event || typeof obj.event !== "object") {
      return fail("invalid_request", "EventFrame missing event object");
    }
    const envRes = parseEventEnvelope(obj.event);
    if (!envRes.ok) return envRes;
    return {
      ok: true,
      value: {
        version: "vg.4",
        frameType: "event",
        frameId,
        event: envRes.value,
      },
    };
  }

  if (frameType === "error") {
    if (!obj.error || typeof obj.error !== "object") {
      return fail("invalid_request", "ErrorFrame missing error object");
    }
    const errRes = parseServiceError(obj.error);
    if (!errRes.ok) return errRes;
    return {
      ok: true,
      value: {
        version: "vg.4",
        frameType: "error",
        frameId,
        inReplyTo: typeof obj.inReplyTo === "string" ? obj.inReplyTo : undefined,
        error: errRes.value,
      },
    };
  }

  return fail("invalid_request", `Unknown frameType '${frameType}'`);
}

export const parseDaemonFrame = parseRuntimeServiceFrame;

export function parseDaemonLine(line: string): Result<RuntimeServiceFrame> {
  const trimmed = line.trim();
  if (!trimmed) {
    return fail("invalid_request", "Empty line cannot be parsed as frame");
  }
  try {
    const raw = JSON.parse(trimmed);
    return parseRuntimeServiceFrame(raw);
  } catch (err) {
    return fail("invalid_request", `Invalid JSON line: ${String(err)}`);
  }
}

export function parseJsonlLine(line: string): Result<EventEnvelope> {
  const trimmed = line.trim();
  if (!trimmed) {
    return fail("invalid_request", "Empty line cannot be parsed as EventEnvelope");
  }
  try {
    const raw = JSON.parse(trimmed);
    return parseEventEnvelope(raw);
  } catch (err) {
    return fail("invalid_request", `Invalid JSON line: ${String(err)}`);
  }
}
