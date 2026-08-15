import { createHash } from "node:crypto";
import path from "node:path";

export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export type Digest = `sha256:${string}`;

export type ResourceSelector =
  | { kind: "fs"; root: string; paths: string[] }
  | { kind: "network"; hosts: string[]; ports: number[] }
  | { kind: "secret"; refs: string[]; discloseToModel: false }
  | { kind: "git"; repo: string; refs: string[] }
  | { kind: "table"; table: string; ranges?: string[] }
  | { kind: "browser"; origin: string; accountRef?: string }
  | { kind: "generic"; uriPattern: string };

export interface EffectDescriptor {
  name: string;
  args: Record<string, Json>;
  digest: Digest;
  readSet?: ResourceSelector[];
  writeSet?: ResourceSelector[];
}

export interface CapabilityGrant {
  id: string;
  principal: string;
  descriptorDigest: Digest;
  actions: string[];
  resources: ResourceSelector[];
  constraints: {
    expiresAt: string;
    maxUses: string;
    maxBytes?: string;
    maxEffects?: string;
    budgetLeaseId: string;
    environmentSnapshot?: Digest;
    networkPolicy?: "deny" | "allowlist";
    requirePreview?: boolean;
    requireApprovalAboveRisk?: "low" | "medium" | "high" | "critical";
  };
  purposeDigest: Digest;
  parentGrantId?: string;
  approvalRef?: string;
  authenticator?: string;
}

export interface AffectedResource {
  resource: string;
  change: "created" | "modified" | "deleted" | "observed";
  preDigest?: Digest;
  postDigest?: Digest;
  patchRef?: Digest;
}

export interface Receipt {
  descriptorDigest: Digest;
  grantId?: string;
  outcome: "ok" | "failed" | "undeterminable";
  observedAt: string;
  resultDigest: Digest;
  affectedResources: AffectedResource[];
  workingDirectory?: string;
  uncertainty?: { scope: "effect_occurrence" | "evidence_completeness" | "result"; reason: string };
  note?: string;
}

export interface EventEnvelope {
  schemaVersion: "vg.4";
  eventId: string;
  scope: "episode" | "governance" | "evolution" | "recovery";
  runId?: string;
  episodeId?: string;
  branchId?: number;
  parentEventId?: string;
  traceId?: string;
  spanId?: string;
  seq: string;
  occurredAt: string;
  recordedAt: string;
  principal: string;
  tenantId: string;
  ownerId: string;
  confidentiality: "public" | "internal" | "confidential" | "restricted";
  retentionClass: "ephemeral" | "standard" | "extended" | "legal_hold";
  trainability: "prohibited" | "opt_in_required" | "opt_in_granted";
  redactionStatus: "none" | "partial" | "complete" | "pending";
  encryptionKeyRef?: string;
  environmentSnapshot?: Digest;
  payload: { kind: string; [key: string]: Json };
}

export interface InvalidationCondition {
  condition: string;
  checkKind: "automatic" | "scheduled" | "manual";
  checkRef?: string;
}

export interface Artifact {
  id: string;
  kind: "R" | "O" | "M" | "P";
  artifactVersion: string;
  body: Digest;
  interfaceSchema: string;
  createdBy: string;
  createdFrom: string[];
  dependencies: { artifact: string; versionRange: string }[];
  supersedes: string[];
  contentDigest: Digest;
  createdAt: string;
  invalidationConditions: InvalidationCondition[];
}

export interface EvidenceClaim {
  id: string;
  subject: string;
  predicate: string;
  value: Json;
  protocol: Digest;
  evaluator: {
    evaluatorId: string;
    class: "mechanically_reproducible" | "externally_grounded" | "human_adjudicated" | "learned_proxy" | "composite" | "inconclusive";
    imageDigest: Digest;
  };
  environmentProfile: Digest;
  substrateProfile: Digest;
  taskDistribution: Digest;
  uncertainty: { kind: "interval" | "point" | "qualitative" | "unknown"; lower?: number; upper?: number; n?: number; note?: string };
  validity: { domains: string[]; note?: string };
  invalidationConditions: InvalidationCondition[];
  evidenceRefs?: Digest[];
  derivedFrom?: string[];
  contradicts?: string[];
  expiresAt?: string;
}

const DIGEST = /^sha256:[0-9a-f]{64}$/;
const TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
const UUID_V7 = /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const INT_STRING = /^(0|[1-9][0-9]*)$/;

function fail(message: string): never { throw new TypeError(message); }
function object(value: unknown, label: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail(`${label} must be an object`);
  return value as Record<string, unknown>;
}
function string(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) fail(`${label} must be a non-empty string`);
  return value;
}
function digest(value: unknown, label: string): Digest {
  const result = string(value, label);
  if (!DIGEST.test(result)) fail(`${label} must be a sha256 digest`);
  return result as Digest;
}
function timestamp(value: unknown, label: string): string {
  const result = string(value, label);
  if (!TIMESTAMP.test(result)) fail(`${label} must be an RFC 3339 UTC timestamp with millisecond precision`);
  return result;
}
function nonEmptyArray(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value) || value.length === 0) fail(`${label} must be a non-empty array`);
  return value;
}
function oneOf<T extends string>(value: unknown, values: readonly T[], label: string): T {
  if (typeof value !== "string" || !values.includes(value as T)) fail(`${label} has an invalid value`);
  return value as T;
}

/** RFC 8785-compatible for JSON-domain values (including sorted object keys). */
export function canonicalJson(value: Json): string {
  if (value === null || typeof value !== "object") {
    const encoded = JSON.stringify(value);
    if (encoded === undefined || (typeof value === "number" && !Number.isFinite(value))) fail("value is not canonicalisable JSON");
    return encoded;
  }
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key]!)}`).join(",")}}`;
}

export function sha256(value: Json): Digest {
  return `sha256:${createHash("sha256").update(canonicalJson(value), "utf8").digest("hex")}`;
}

function normalizePath(value: string, workspaceRoot: string): string {
  const root = path.posix.resolve("/", workspaceRoot.replaceAll("\\", "/"));
  return path.posix.resolve(root, value.replaceAll("\\", "/"));
}

export function createEffectDescriptor(
  name: string,
  args: Record<string, Json | undefined>,
  options: { workspaceRoot: string; pathArguments?: readonly string[]; readSet?: ResourceSelector[]; writeSet?: ResourceSelector[] },
): EffectDescriptor {
  string(name, "EffectDescriptor.name");
  const pathArguments = new Set(options.pathArguments ?? []);
  const normalized: Record<string, Json> = {};
  for (const [key, value] of Object.entries(args)) {
    if (value === undefined) continue;
    normalized[key] = pathArguments.has(key) && typeof value === "string" ? normalizePath(value, options.workspaceRoot) : value;
  }
  const result: EffectDescriptor = { name, args: normalized, digest: sha256({ name, args: normalized }) };
  if (options.readSet !== undefined) result.readSet = options.readSet;
  if (options.writeSet !== undefined) result.writeSet = options.writeSet;
  return result;
}

export function parseEffectDescriptor(value: unknown): EffectDescriptor {
  const input = object(value, "EffectDescriptor");
  const name = string(input.name, "EffectDescriptor.name");
  const args = object(input.args, "EffectDescriptor.args") as Record<string, Json>;
  const supplied = digest(input.digest, "EffectDescriptor.digest");
  if (sha256({ name, args }) !== supplied) fail("EffectDescriptor.digest does not bind name and args");
  return structuredClone(input) as unknown as EffectDescriptor;
}

export function parseCapabilityGrant(value: unknown): CapabilityGrant {
  const input = object(value, "CapabilityGrant");
  string(input.id, "CapabilityGrant.id");
  string(input.principal, "CapabilityGrant.principal");
  digest(input.descriptorDigest, "CapabilityGrant.descriptorDigest");
  nonEmptyArray(input.actions, "CapabilityGrant.actions").forEach((v) => string(v, "CapabilityGrant.actions[]"));
  nonEmptyArray(input.resources, "CapabilityGrant.resources");
  const constraints = object(input.constraints, "CapabilityGrant.constraints");
  timestamp(constraints.expiresAt, "CapabilityGrant.constraints.expiresAt");
  if (!INT_STRING.test(string(constraints.maxUses, "CapabilityGrant.constraints.maxUses"))) fail("maxUses must be an IntString");
  string(constraints.budgetLeaseId, "CapabilityGrant.constraints.budgetLeaseId");
  digest(input.purposeDigest, "CapabilityGrant.purposeDigest");
  return structuredClone(input) as unknown as CapabilityGrant;
}

function parseInvalidation(value: unknown, label: string): void {
  nonEmptyArray(value, label).forEach((entry, index) => {
    const condition = object(entry, `${label}[${index}]`);
    string(condition.condition, `${label}[${index}].condition`);
    const kind = oneOf(condition.checkKind, ["automatic", "scheduled", "manual"] as const, `${label}[${index}].checkKind`);
    if (kind === "automatic") string(condition.checkRef, `${label}[${index}].checkRef`);
  });
}

export function parseReceipt(value: unknown): Receipt {
  const input = object(value, "Receipt");
  digest(input.descriptorDigest, "Receipt.descriptorDigest");
  oneOf(input.outcome, ["ok", "failed", "undeterminable"] as const, "Receipt.outcome");
  timestamp(input.observedAt, "Receipt.observedAt");
  digest(input.resultDigest, "Receipt.resultDigest");
  if (!Array.isArray(input.affectedResources)) fail("Receipt.affectedResources must be an array");
  input.affectedResources.forEach((entry, index) => {
    const affected = object(entry, `Receipt.affectedResources[${index}]`);
    string(affected.resource, `Receipt.affectedResources[${index}].resource`);
    const change = oneOf(affected.change, ["created", "modified", "deleted", "observed"] as const, `Receipt.affectedResources[${index}].change`);
    if (change !== "created" && affected.preDigest === undefined) fail(`${change} resource requires preDigest`);
    if (change !== "deleted" && affected.postDigest === undefined) fail(`${change} resource requires postDigest`);
    if (affected.preDigest !== undefined) digest(affected.preDigest, "preDigest");
    if (affected.postDigest !== undefined) digest(affected.postDigest, "postDigest");
  });
  if (input.outcome === "undeterminable" && input.uncertainty === undefined) fail("undeterminable Receipt requires uncertainty");
  if (input.uncertainty !== undefined) {
    const uncertainty = object(input.uncertainty, "Receipt.uncertainty");
    oneOf(uncertainty.scope, ["effect_occurrence", "evidence_completeness", "result"] as const, "Receipt.uncertainty.scope");
    string(uncertainty.reason, "Receipt.uncertainty.reason");
  }
  return structuredClone(input) as unknown as Receipt;
}

export function parseEventEnvelope(value: unknown): EventEnvelope {
  const input = object(value, "EventEnvelope");
  if (input.schemaVersion !== "vg.4") fail("EventEnvelope.schemaVersion must be vg.4");
  if (!UUID_V7.test(string(input.eventId, "EventEnvelope.eventId"))) fail("EventEnvelope.eventId must be UUIDv7");
  const scope = oneOf(input.scope, ["episode", "governance", "evolution", "recovery"] as const, "EventEnvelope.scope");
  if ((scope === "episode" || scope === "recovery") && input.runId === undefined) fail(`${scope} EventEnvelope requires runId`);
  if (scope === "episode" && input.episodeId === undefined) fail("episode EventEnvelope requires episodeId");
  if (!INT_STRING.test(string(input.seq, "EventEnvelope.seq"))) fail("EventEnvelope.seq must be an IntString");
  timestamp(input.occurredAt, "EventEnvelope.occurredAt");
  timestamp(input.recordedAt, "EventEnvelope.recordedAt");
  ["principal", "tenantId", "ownerId"].forEach((key) => string(input[key], `EventEnvelope.${key}`));
  string(object(input.payload, "EventEnvelope.payload").kind, "EventEnvelope.payload.kind");
  return structuredClone(input) as unknown as EventEnvelope;
}

export function parseArtifact(value: unknown): Artifact {
  const input = object(value, "Artifact");
  string(input.id, "Artifact.id");
  oneOf(input.kind, ["R", "O", "M", "P"] as const, "Artifact.kind");
  string(input.artifactVersion, "Artifact.artifactVersion");
  digest(input.body, "Artifact.body");
  digest(input.contentDigest, "Artifact.contentDigest");
  timestamp(input.createdAt, "Artifact.createdAt");
  parseInvalidation(input.invalidationConditions, "Artifact.invalidationConditions");
  return structuredClone(input) as unknown as Artifact;
}

export function parseEvidenceClaim(value: unknown): EvidenceClaim {
  const input = object(value, "EvidenceClaim");
  ["id", "subject", "predicate"].forEach((key) => string(input[key], `EvidenceClaim.${key}`));
  ["protocol", "environmentProfile", "substrateProfile", "taskDistribution"].forEach((key) => digest(input[key], `EvidenceClaim.${key}`));
  const evaluator = object(input.evaluator, "EvidenceClaim.evaluator");
  string(evaluator.evaluatorId, "EvidenceClaim.evaluator.evaluatorId");
  digest(evaluator.imageDigest, "EvidenceClaim.evaluator.imageDigest");
  nonEmptyArray(object(input.validity, "EvidenceClaim.validity").domains, "EvidenceClaim.validity.domains");
  parseInvalidation(input.invalidationConditions, "EvidenceClaim.invalidationConditions");
  return structuredClone(input) as unknown as EvidenceClaim;
}

export function serialize<T>(value: T): string { return JSON.stringify(value); }
export function deserialize<T>(wire: string, parser: (value: unknown) => T): T { return parser(JSON.parse(wire)); }
