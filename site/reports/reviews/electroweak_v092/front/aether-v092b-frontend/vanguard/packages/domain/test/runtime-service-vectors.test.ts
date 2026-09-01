/**
 * B-O2-01: the TypeScript half of the vg.4 RuntimeService vector replay.
 *
 * `schemas/v4/vectors/runtime-service/` is the cross-language contract
 * (`schemas/v4/vectors/README.md`). `test/contracts/test_runtime_service_vectors.py`
 * replays the same bytes through the Python ingress validator. Both halves read
 * one corpus, so a disagreement between the readers is conclusive (GV-4).
 *
 * The tables under test are generated from `schemas/v4/runtime-service.schema.json`
 * by `tools/codegen/generate_ts_contracts.py`; `test_runtime_service_contract_parity.py`
 * proves the Python mirror is derived from that same schema. This file proves the
 * generated TypeScript tables decide the corpus the way the schema says they must.
 */
import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  RUNTIME_SERVICE_COMMAND_ALLOWED_PAYLOAD_FIELDS,
  RUNTIME_SERVICE_COMMAND_REQUIRED_PAYLOAD_FIELDS,
  RUNTIME_SERVICE_COMMAND_RUN_SCOPE,
  RUNTIME_SERVICE_ERROR_CODES,
  RUNTIME_SERVICE_SEQ_GUARD_FIELDS,
} from "../generated/contracts.gen.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const VECTORS = join(HERE, "..", "..", "..", "..", "schemas", "v4", "vectors", "runtime-service");

const SIGNATURE = /^[0-9a-fA-F]{128}$/;
const CANONICAL_DECIMAL = /^(0|[1-9][0-9]*)$/;

type Json = Record<string, unknown>;
type CommandName = keyof typeof RUNTIME_SERVICE_COMMAND_RUN_SCOPE;

const FRAME_FIELDS = new Set(["version", "frameType", "frameId", "command"]);
const COMMAND_FIELDS = new Set(["name", "commandId", "idempotencyKey", "actor", "runId", "payload"]);

type ErrorCode = (typeof RUNTIME_SERVICE_ERROR_CODES)[number];

class Refusal extends Error {
  code: ErrorCode;
  constructor(code: ErrorCode, message: string) {
    super(message);
    this.code = code;
  }
}

const refuse = (code: ErrorCode, message: string): never => {
  throw new Refusal(code, message);
};

const isObject = (v: unknown): v is Json => typeof v === "object" && v !== null && !Array.isArray(v);

/** The TypeScript reader: the same decisions Python's `validate_frame_envelope`
 *  and `validate_command` make, driven entirely by the generated tables. */
function ingest(frame: unknown): void {
  if (!isObject(frame)) refuse("invalid_request", "frame must be a JSON object");

  for (const key of Object.keys(frame)) {
    if (!FRAME_FIELDS.has(key)) refuse("invalid_request", `unknown frame field ${key}`);
  }
  if (frame.version !== "vg.4") refuse("incompatible_version", "frame version must be vg.4");
  if (frame.frameType !== "command") refuse("invalid_request", "frame frameType must be command");
  if (typeof frame.frameId !== "string" || frame.frameId === "") {
    refuse("invalid_request", "frame requires non-empty frameId");
  }

  const cmd = frame.command;
  if (!isObject(cmd)) refuse("invalid_request", "command must be an object");

  for (const key of Object.keys(cmd)) {
    if (!COMMAND_FIELDS.has(key)) refuse("invalid_request", `unknown command field ${key}`);
  }

  const name = cmd.name as CommandName;
  if (typeof name !== "string" || !(name in RUNTIME_SERVICE_COMMAND_RUN_SCOPE)) {
    refuse("invalid_request", `unknown command ${String(cmd.name)}`);
  }
  for (const key of ["commandId", "idempotencyKey"] as const) {
    if (typeof cmd[key] !== "string" || cmd[key] === "") {
      refuse("invalid_request", `command requires non-empty ${key}`);
    }
  }

  const scope = RUNTIME_SERVICE_COMMAND_RUN_SCOPE[name];
  const runId = cmd.runId;
  if (scope === "forbidden" && runId !== undefined && runId !== null && runId !== "") {
    refuse("invalid_request", `${name} must not carry a non-empty runId`);
  }
  if (scope === "required" && !runId) refuse("invalid_request", `${name} requires runId`);

  const payload = cmd.payload === undefined ? {} : cmd.payload;
  if (!isObject(payload)) refuse("invalid_request", "payload must be an object");

  const allowed = new Set<string>(RUNTIME_SERVICE_COMMAND_ALLOWED_PAYLOAD_FIELDS[name]);
  for (const key of Object.keys(payload)) {
    if (!allowed.has(key)) refuse("invalid_request", `unknown payload field ${key} for ${name}`);
  }
  for (const field of RUNTIME_SERVICE_SEQ_GUARD_FIELDS) {
    if (!(field in payload)) continue;
    const value = payload[field];
    const ok =
      (typeof value === "number" && Number.isInteger(value) && value >= 0) ||
      (typeof value === "string" && CANONICAL_DECIMAL.test(value));
    if (!ok) refuse("invalid_request", `${name} payload ${field} is not a sequence guard`);
  }
  for (const field of RUNTIME_SERVICE_COMMAND_REQUIRED_PAYLOAD_FIELDS[name]) {
    if (!(field in payload)) refuse("invalid_request", `${name} payload missing ${field}`);
  }

  if (name === "ResolveApproval") {
    const decision = payload.decision;
    if (!isObject(decision)) refuse("invalid_request", "ResolveApproval requires a decision object");
    const required = [
      "approvalId", "resolution", "reviewer", "argsDigest",
      "descriptorDigest", "expiresAt", "keyId", "signature",
    ];
    for (const key of Object.keys(decision)) {
      if (!required.includes(key)) refuse("invalid_request", `unknown decision field ${key}`);
    }
    for (const field of required) {
      if (!decision[field]) refuse("invalid_request", `decision missing ${field}`);
    }
    if (decision.resolution !== "approved" && decision.resolution !== "rejected") {
      refuse("invalid_request", "decision.resolution must be approved|rejected");
    }
    if (typeof decision.signature !== "string" || !SIGNATURE.test(decision.signature)) {
      refuse("invalid_request", "decision signature must be 128 hex characters");
    }
  }
}

const cases = (kind: string): Array<[string, Json]> =>
  readdirSync(join(VECTORS, kind))
    .filter((f) => f.endsWith(".json") && !f.endsWith(".expect.json"))
    .sort()
    .map((f) => [f.slice(0, -5), JSON.parse(readFileSync(join(VECTORS, kind, f), "utf-8")) as Json]);

const expectation = (name: string): Json =>
  JSON.parse(readFileSync(join(VECTORS, "invalid", `${name}.expect.json`), "utf-8")) as Json;

test("the corpus is present to both readers", () => {
  assert.ok(cases("valid").length > 0, "no valid vectors");
  assert.ok(cases("invalid").length > 0, "no invalid vectors");
});

test("every golden vector is accepted", () => {
  for (const [name, frame] of cases("valid")) {
    assert.doesNotThrow(() => ingest(frame), `golden vector ${name} was rejected`);
  }
});

test("every negative vector is refused with the declared code", () => {
  for (const [name, frame] of cases("invalid")) {
    let refusal: Refusal | undefined;
    try {
      ingest(frame);
    } catch (e) {
      refusal = e as Refusal;
    }
    assert.ok(refusal, `negative vector ${name} was accepted`);
    assert.equal(refusal.code, expectation(name).expectedCode, `${name}: wrong error code`);
  }
});

test("the generated error vocabulary is the frozen ten-entry table", () => {
  assert.deepEqual([...RUNTIME_SERVICE_ERROR_CODES].sort(), [
    "conflict", "frame_too_large", "incompatible_version", "internal",
    "invalid_request", "not_available", "not_found", "permission_denied",
    "rate_limited", "unauthenticated",
  ]);
});

test("every command carries a run scope and a payload table", () => {
  for (const name of Object.keys(RUNTIME_SERVICE_COMMAND_RUN_SCOPE) as CommandName[]) {
    assert.ok(["required", "forbidden", "optional"].includes(RUNTIME_SERVICE_COMMAND_RUN_SCOPE[name]));
    assert.ok(Array.isArray(RUNTIME_SERVICE_COMMAND_ALLOWED_PAYLOAD_FIELDS[name]));
    const allowed = new Set<string>(RUNTIME_SERVICE_COMMAND_ALLOWED_PAYLOAD_FIELDS[name]);
    for (const field of RUNTIME_SERVICE_COMMAND_REQUIRED_PAYLOAD_FIELDS[name]) {
      assert.ok(allowed.has(field), `${name}: required field ${field} is not allowed`);
    }
  }
});
