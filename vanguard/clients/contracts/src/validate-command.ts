/**
 * Ingress-strict validation for inbound vg.4 CommandFrames.
 *
 * Mirrors `vanguard/packages/runtime/service/contract.py`'s `validate_frame_envelope`
 * and `validate_command` field-for-field. This is the TypeScript half of the frozen
 * vg.4 wire contract (integration_plan.md §4.3, §4.5): both readers are checked
 * against the same golden/negative vector corpus under
 * `schemas/v4/vectors/runtime-service/` by `test/contracts/test_runtime_service_vectors.py`
 * (Python) and `runtime-service-vectors.test.ts` (this package), so the two cannot drift.
 *
 * Unlike `parseRuntimeServiceFrame` in `parse.ts` (a permissive best-effort reader for
 * frames the client receives), this module is strict-reject: any unknown field, missing
 * required field, or malformed value fails closed with `invalid_request`, exactly as the
 * server-side ingress validator does for frames the client sends.
 */

import { fail } from "./errors.js";
import type { Result } from "./types.js";

const RUN_SCOPE_REQUIRED = "required";
const RUN_SCOPE_FORBIDDEN = "forbidden";
const RUN_SCOPE_OPTIONAL = "optional";

type RunScope = typeof RUN_SCOPE_REQUIRED | typeof RUN_SCOPE_FORBIDDEN | typeof RUN_SCOPE_OPTIONAL;

const COMMAND_RUN_SCOPE: Readonly<Record<string, RunScope>> = {
  StartRun: RUN_SCOPE_REQUIRED,
  GetRun: RUN_SCOPE_REQUIRED,
  ListRuns: RUN_SCOPE_FORBIDDEN,
  StreamEvents: RUN_SCOPE_REQUIRED,
  Cancel: RUN_SCOPE_REQUIRED,
  Checkpoint: RUN_SCOPE_REQUIRED,
  Resume: RUN_SCOPE_REQUIRED,
  ResolveApproval: RUN_SCOPE_REQUIRED,
  RecordCorrection: RUN_SCOPE_REQUIRED,
  ExplainArtifact: RUN_SCOPE_OPTIONAL,
  GetCapabilities: RUN_SCOPE_FORBIDDEN,
};

const COMMAND_REQUIRED_PAYLOAD_FIELDS: Readonly<Record<string, readonly string[]>> = {
  StartRun: ["manifestPath", "repoPath", "brief"],
  GetRun: [],
  ListRuns: [],
  StreamEvents: [],
  Cancel: [],
  Checkpoint: [],
  Resume: [],
  ResolveApproval: ["decision"],
  RecordCorrection: ["correction"],
  ExplainArtifact: ["artifactId"],
  GetCapabilities: [],
};

const COMMAND_ALLOWED_PAYLOAD_FIELDS: Readonly<Record<string, ReadonlySet<string>>> = {
  StartRun: new Set(["manifestPath", "repoPath", "brief", "profileId", "model", "episodeId", "expectedSeq"]),
  GetRun: new Set(["expectedSeq"]),
  ListRuns: new Set(["limit", "offset"]),
  StreamEvents: new Set(["afterSeq"]),
  Cancel: new Set(["reason", "expectedSeq"]),
  Checkpoint: new Set(["reason", "expectedSeq"]),
  Resume: new Set(["checkpointId", "expectedSeq"]),
  ResolveApproval: new Set(["decision", "expectedSeq"]),
  RecordCorrection: new Set(["correction", "expectedSeq"]),
  ExplainArtifact: new Set(["artifactId", "substrateProfile", "expectedSeq"]),
  GetCapabilities: new Set(),
};

const SEQ_GUARD_FIELDS = new Set(["expectedSeq", "afterSeq"]);

const APPROVAL_DECISION_REQUIRED_FIELDS: readonly string[] = [
  "approvalId",
  "resolution",
  "reviewer",
  "argsDigest",
  "descriptorDigest",
  "expiresAt",
  "keyId",
  "signature",
];

const APPROVAL_DECISION_ALLOWED_FIELDS = new Set(APPROVAL_DECISION_REQUIRED_FIELDS);

const SIGNATURE_RE = /^[0-9a-fA-F]{128}$/;

const COMMAND_TOP_LEVEL_FIELDS = new Set(["name", "commandId", "idempotencyKey", "actor", "runId", "payload"]);
const FRAME_TOP_LEVEL_FIELDS = new Set(["version", "frameType", "frameId", "command"]);

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function unknownKeys(obj: Record<string, unknown>, allowed: ReadonlySet<string>): string[] {
  return Object.keys(obj)
    .filter((k) => !allowed.has(k))
    .sort();
}

function checkSeqGuard(command: string, field: string, value: unknown): Result<void> {
  if (typeof value === "boolean" || (typeof value !== "number" && typeof value !== "string")) {
    return fail("invalid_request", `${command} payload ${field} must be a non-negative integer or decimal string`);
  }
  if (typeof value === "string") {
    if (!/^\d+$/.test(value) || (value.length > 1 && value.startsWith("0"))) {
      return fail("invalid_request", `${command} payload ${field} must be a canonical decimal string`);
    }
  } else if (value < 0) {
    return fail("invalid_request", `${command} payload ${field} must not be negative`);
  }
  return { ok: true, value: undefined };
}

export type ValidatedCommand = {
  name: string;
  commandId: string;
  idempotencyKey: string;
  runId: string;
  actor: string;
  payload: Record<string, unknown>;
};

/** Validate the outer RuntimeServiceFrame shell before touching its payload. */
export function validateCommandFrameEnvelope(frame: unknown): Result<void> {
  if (!isPlainObject(frame)) {
    return fail("invalid_request", "frame must be a JSON object");
  }

  const unknownFrameFields = unknownKeys(frame, FRAME_TOP_LEVEL_FIELDS);
  if (unknownFrameFields.length > 0) {
    return fail("invalid_request", `unknown frame field(s): ${JSON.stringify(unknownFrameFields)}`);
  }

  if (frame.version !== "vg.4") {
    return fail("incompatible_version", "frame version must be vg.4");
  }

  const frameType = frame.frameType;
  if (frameType !== "command" && frameType !== "receipt" && frameType !== "event" && frameType !== "error") {
    return fail("invalid_request", `unknown frameType ${JSON.stringify(frameType)}`);
  }
  if (frameType !== "command") {
    return fail("invalid_request", "frame frameType must be command");
  }

  const frameId = frame.frameId;
  if (typeof frameId !== "string" || !frameId) {
    return fail("invalid_request", "frame requires non-empty frameId");
  }

  return { ok: true, value: undefined };
}

/** Validate one `command` object against the frozen vg.4 contract. */
export function validateCommand(cmd: unknown): Result<ValidatedCommand> {
  if (!isPlainObject(cmd)) {
    return fail("invalid_request", "command must be an object");
  }

  const unknownFields = unknownKeys(cmd, COMMAND_TOP_LEVEL_FIELDS);
  if (unknownFields.length > 0) {
    return fail("invalid_request", `unknown command field(s): ${JSON.stringify(unknownFields)}`);
  }

  const name = cmd.name;
  if (typeof name !== "string" || !(name in COMMAND_RUN_SCOPE)) {
    return fail("invalid_request", `unknown command ${JSON.stringify(name)}`);
  }

  const commandId = cmd.commandId;
  if (typeof commandId !== "string" || !commandId) {
    return fail("invalid_request", "command requires non-empty commandId");
  }

  const idempotencyKey = cmd.idempotencyKey;
  if (typeof idempotencyKey !== "string" || !idempotencyKey) {
    return fail("invalid_request", "command requires non-empty idempotencyKey");
  }

  const runIdRaw = cmd.runId;
  const scope = COMMAND_RUN_SCOPE[name];
  if (scope === RUN_SCOPE_FORBIDDEN && runIdRaw !== undefined && runIdRaw !== null && runIdRaw !== "") {
    return fail("invalid_request", `${name} must not carry a non-empty runId`);
  }
  if (scope === RUN_SCOPE_REQUIRED && !runIdRaw) {
    return fail("invalid_request", `${name} requires runId`);
  }
  const runId = runIdRaw !== undefined && runIdRaw !== null ? String(runIdRaw) : "";

  const actor = cmd.actor ?? "operator";
  if (typeof actor !== "string") {
    return fail("invalid_request", "actor must be a string");
  }

  const payload = cmd.payload ?? {};
  if (!isPlainObject(payload)) {
    return fail("invalid_request", "payload must be an object");
  }

  const allowedPayload = COMMAND_ALLOWED_PAYLOAD_FIELDS[name] ?? new Set<string>();
  const unknownPayload = unknownKeys(payload, allowedPayload);
  if (unknownPayload.length > 0) {
    return fail("invalid_request", `unknown payload field(s) for ${name}: ${JSON.stringify(unknownPayload)}`);
  }

  for (const field of Object.keys(payload)) {
    if (SEQ_GUARD_FIELDS.has(field)) {
      const guard = checkSeqGuard(name, field, payload[field]);
      if (!guard.ok) return guard;
    }
  }

  const missing = COMMAND_REQUIRED_PAYLOAD_FIELDS[name].filter((f) => !(f in payload));
  if (missing.length > 0) {
    return fail("invalid_request", `${name} payload missing required field(s): ${JSON.stringify(missing)}`);
  }

  if (name === "ResolveApproval") {
    const decision = payload.decision;
    if (!isPlainObject(decision)) {
      return fail("invalid_request", "ResolveApproval requires a decision object");
    }
    const unknownDecision = unknownKeys(decision, APPROVAL_DECISION_ALLOWED_FIELDS);
    if (unknownDecision.length > 0) {
      return fail("invalid_request", `unknown decision field(s): ${JSON.stringify(unknownDecision)}`);
    }
    const missingDecision = APPROVAL_DECISION_REQUIRED_FIELDS.filter((f) => !decision[f]);
    if (missingDecision.length > 0) {
      return fail("invalid_request", `decision missing required field(s): ${JSON.stringify(missingDecision)}`);
    }
    if (decision.resolution !== "approved" && decision.resolution !== "rejected") {
      return fail("invalid_request", "decision.resolution must be approved|rejected");
    }
    const sig = decision.signature;
    if (typeof sig !== "string" || !SIGNATURE_RE.test(sig)) {
      return fail("invalid_request", "decision signature must be a 128-character hex Ed25519 signature");
    }
  }

  return {
    ok: true,
    value: { name, commandId, idempotencyKey, runId, actor, payload },
  };
}

/** Run one frame through the full ingress path, exactly as server.py does. */
export function validateCommandFrame(frame: unknown): Result<ValidatedCommand> {
  const envelope = validateCommandFrameEnvelope(frame);
  if (!envelope.ok) return envelope;
  const command = isPlainObject(frame) ? frame.command : undefined;
  return validateCommand(command);
}
