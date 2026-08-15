/**
 * Generated-reader semantics for the normative T1.4-T1.12 wire contracts.
 *
 * Writers are closed JSON Schemas. Readers validate every known field while
 * preserving unknown fields recursively so a minor schema bump is survivable.
 */

import path from "node:path";

import { digestOf } from "./canonicalisation/digest.ts";
import { parse as parsePrimitive } from "./primitives/primitives.ts";
import { SELECTOR_KINDS, parseSelector } from "./selectors/resource-selector.ts";

export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export type ResourceSelector = Record<string, unknown> & { kind: string };
export type WireObject = Record<string, unknown>;

export interface EffectDescriptor extends WireObject {
  verb: string;
  sinkClass: "pure" | "observation" | "privileged";
  selector: ResourceSelector;
  args: Record<string, Json>;
  argsDigest: string;
  idempotencyKey: string;
  riskTier: "low" | "medium" | "high" | "critical";
  provenance: WireObject;
  workingDirectory?: string;
  readSet?: ResourceSelector[];
  writeSet?: ResourceSelector[];
}

export interface CapabilityGrant extends WireObject {
  grantId: string;
  principal: string;
  descriptorDigest: string;
  actions: string[];
  selector: ResourceSelector;
  constraints: WireObject;
  expiry: string;
  maxUses: string;
  purposeDigest: string;
  parentGrantId?: string;
  approvalRef?: string;
  authenticator?: string;
}

export interface Receipt extends WireObject {
  descriptorDigest: string;
  grantId?: string;
  outcome: "ok" | "failed" | "undeterminable";
  observedAt: string;
  resultDigest: string;
  affectedResources: WireObject[];
  uncertainty?: WireObject;
}

export interface EventEnvelope extends WireObject {
  schemaVersion: "vg.4";
  eventId: string;
  scope: "episode" | "governance" | "evolution" | "recovery";
  traceId: string;
  spanId: string;
  seq: string;
  occurredAt: string;
  recordedAt: string;
  principal: string;
  principalRole: "user" | "operator" | "episode" | "process" | "evaluator" | "release";
  tenantId: string;
  ownerId: string;
  confidentiality: string;
  retentionClass: string;
  trainability: string;
  redactionStatus: string;
  payload: WireObject & { kind: string };
}

export interface Artifact extends WireObject {
  artifactId: string;
  kind: string;
  class: "enforcement" | "compensation";
  hypothesis: string;
  evidenceRefs: string[];
  invalidationConditions: WireObject[];
  riskDelta: number;
  contentDigest: string;
  compensatesFor?: string;
}

export interface EvidenceClaim extends WireObject {
  id: string;
  subject: string;
  predicate: string;
  value: Json;
  protocol: string;
  evaluator: WireObject;
  environmentProfile: string;
  substrateProfile: string;
  taskDistribution: string;
  uncertainty: WireObject;
  validity: WireObject;
  invalidationConditions: WireObject[];
}

export interface CorrectionRecord extends WireObject {
  episodeId: string;
  proposedPatchDigest: string;
  acceptedPatchDigest: string;
  reasonCodes: string[];
  magnitude: "minor" | "moderate" | "major";
  scope: "user" | "team" | "repo" | "domain" | "general";
  correctingPrincipalRole: EventEnvelope["principalRole"];
}

export interface Recording extends WireObject {
  modelCassetteDigest: string;
  imageDigest: string;
  envSnapshotDigest: string;
  seed: string;
  clockPolicy: "recorded" | "fixed" | "logical";
}

export interface ProcessDefinition extends WireObject {
  definitionDigest: string;
  states: string[];
  initialState: string;
  transitions: WireObject[];
  approvalPoints: string[];
  boundEffectVerbs: string[];
}

export interface ProcessInstance extends WireObject {
  processId: string;
  definitionDigest: string;
  currentState: string;
  allowedTransitions: string[];
  pendingApprovals: string[];
  boundEffectVerbs: string[];
  history: WireObject[];
}

export class WireError extends TypeError {
  readonly code: string;
  readonly path: string;

  constructor(code: string, path_: string, message: string) {
    super(`${path_}: ${message} (${code})`);
    this.name = "WireError";
    this.code = code;
    this.path = path_;
  }
}

function fail(code: string, path_: string, message: string): never {
  throw new WireError(code, path_, message);
}

function object(value: unknown, path_: string): WireObject {
  if (value === null || typeof value !== "object" || Array.isArray(value)) fail("type", path_, "expected object");
  return value as WireObject;
}

function array(value: unknown, path_: string, nonempty = false): unknown[] {
  if (!Array.isArray(value)) fail("type", path_, "expected array");
  if (nonempty && value.length === 0) fail("minItems", path_, "must not be empty");
  return value;
}

function string(value: unknown, path_: string): string {
  if (typeof value !== "string") fail("type", path_, "expected string");
  if (value.length === 0) fail("minLength", path_, "must not be empty");
  return value;
}

function required(value: WireObject, fields: readonly string[], path_: string): void {
  for (const field of fields) if (!(field in value)) fail("required", path_, `missing ${field}`);
}

function oneOf<T extends string>(value: unknown, values: readonly T[], path_: string): T {
  const result = string(value, path_);
  if (!values.includes(result as T)) fail("enum", path_, `unsupported value ${result}`);
  return result as T;
}

function primitive(kind: string, value: unknown, path_: string): void {
  try { parsePrimitive(kind, value); }
  catch (error) {
    const code = typeof error === "object" && error !== null && "code" in error ? String(error.code) : "primitive";
    fail(code, path_, error instanceof Error ? error.message : "invalid primitive");
  }
}

function strings(value: unknown, path_: string, nonempty = false): string[] {
  const result = array(value, path_, nonempty).map((item, index) => string(item, `${path_}/${index}`));
  if (new Set(result).size !== result.length) fail("uniqueItems", path_, "items must be unique");
  return result;
}

const SELECTOR_FIELDS: Record<string, readonly string[]> = {
  fs: ["kind", "root", "paths"], network: ["kind", "hosts", "ports"],
  secret: ["kind", "refs", "discloseToModel"], git: ["kind", "repo", "refs"],
  table: ["kind", "table", "ranges"], browser: ["kind", "origin", "accountRef"],
  generic: ["kind", "uriPattern"],
};

function selector(value: unknown, path_: string): void {
  const source = object(value, path_);
  const kind = string(source.kind, `${path_}/kind`);
  if (!SELECTOR_KINDS.includes(kind as never)) fail("enum", `${path_}/kind`, "unknown selector kind");
  const known = Object.fromEntries(SELECTOR_FIELDS[kind]!.filter((field) => field in source).map((field) => [field, source[field]]));
  try { parseSelector(known); }
  catch (error) {
    const code = typeof error === "object" && error !== null && "code" in error ? String(error.code) : "selector";
    fail(code, path_, error instanceof Error ? error.message : "invalid selector");
  }
}

function provenance(value: unknown, path_: string): void {
  const source = object(value, path_);
  required(source, ["origin", "instructionAuthority", "integrity", "confidentiality", "epistemic"], path_);
  oneOf(source.origin, ["operator", "system", "environment", "model", "external", "memory"] as const, `${path_}/origin`);
  oneOf(source.instructionAuthority, ["directive", "advisory", "inert"] as const, `${path_}/instructionAuthority`);
  oneOf(source.integrity, ["attested", "verified", "unverified", "tampered"] as const, `${path_}/integrity`);
  primitive("ConfidentialityLabel", source.confidentiality, `${path_}/confidentiality`);
  primitive("EpistemicState", source.epistemic, `${path_}/epistemic`);
}

function invalidation(value: unknown, path_: string): void {
  array(value, path_, true).forEach((item, index) => {
    const itemPath = `${path_}/${index}`;
    const source = object(item, itemPath);
    required(source, ["condition", "checkKind"], itemPath);
    string(source.condition, `${itemPath}/condition`);
    const kind = oneOf(source.checkKind, ["automatic", "scheduled", "manual"] as const, `${itemPath}/checkKind`);
    if (kind === "automatic") {
      if (!("checkRef" in source)) fail("required", itemPath, "automatic condition requires checkRef");
      primitive("EvaluatorId", source.checkRef, `${itemPath}/checkRef`);
    }
  });
}

function parseEffect(value: unknown): void {
  const source = object(value, "EffectDescriptor");
  required(source, ["verb", "sinkClass", "selector", "args", "argsDigest", "idempotencyKey", "riskTier", "provenance"], "EffectDescriptor");
  string(source.verb, "EffectDescriptor/verb");
  oneOf(source.sinkClass, ["pure", "observation", "privileged"] as const, "EffectDescriptor/sinkClass");
  selector(source.selector, "EffectDescriptor/selector");
  const args = object(source.args, "EffectDescriptor/args");
  primitive("Digest", source.argsDigest, "EffectDescriptor/argsDigest");
  if (digestOf(args) !== source.argsDigest) fail("digest", "EffectDescriptor/argsDigest", "does not bind canonical args");
  string(source.idempotencyKey, "EffectDescriptor/idempotencyKey");
  primitive("RiskTier", source.riskTier, "EffectDescriptor/riskTier");
  provenance(source.provenance, "EffectDescriptor/provenance");
  if (source.workingDirectory !== undefined) string(source.workingDirectory, "EffectDescriptor/workingDirectory");
  for (const field of ["readSet", "writeSet"] as const) {
    if (source[field] !== undefined) array(source[field], `EffectDescriptor/${field}`).forEach((item, index) => selector(item, `EffectDescriptor/${field}/${index}`));
  }
}

function parseGrant(value: unknown): void {
  const source = object(value, "CapabilityGrant");
  required(source, ["grantId", "principal", "descriptorDigest", "actions", "selector", "constraints", "expiry", "maxUses", "purposeDigest"], "CapabilityGrant");
  for (const [field, kind] of [["grantId", "GrantId"], ["principal", "PrincipalId"], ["descriptorDigest", "Digest"], ["expiry", "Timestamp"], ["maxUses", "IntString"], ["purposeDigest", "Digest"]] as const) primitive(kind, source[field], `CapabilityGrant/${field}`);
  strings(source.actions, "CapabilityGrant/actions", true);
  selector(source.selector, "CapabilityGrant/selector");
  const constraints = object(source.constraints, "CapabilityGrant/constraints");
  required(constraints, ["budgetLeaseId"], "CapabilityGrant/constraints");
  primitive("LeaseId", constraints.budgetLeaseId, "CapabilityGrant/constraints/budgetLeaseId");
  for (const field of ["maxBytes", "maxEffects"] as const) if (constraints[field] !== undefined) primitive("IntString", constraints[field], `CapabilityGrant/constraints/${field}`);
  if (constraints.environmentSnapshot !== undefined) primitive("Digest", constraints.environmentSnapshot, "CapabilityGrant/constraints/environmentSnapshot");
  if (constraints.networkPolicy !== undefined) oneOf(constraints.networkPolicy, ["deny", "allowlist"] as const, "CapabilityGrant/constraints/networkPolicy");
  if (constraints.requirePreview !== undefined && typeof constraints.requirePreview !== "boolean") fail("type", "CapabilityGrant/constraints/requirePreview", "expected boolean");
  if (constraints.requireApprovalAboveRisk !== undefined) primitive("RiskTier", constraints.requireApprovalAboveRisk, "CapabilityGrant/constraints/requireApprovalAboveRisk");
  if (source.parentGrantId !== undefined) primitive("GrantId", source.parentGrantId, "CapabilityGrant/parentGrantId");
  if (source.approvalRef !== undefined) primitive("ApprovalId", source.approvalRef, "CapabilityGrant/approvalRef");
  if (source.authenticator !== undefined) string(source.authenticator, "CapabilityGrant/authenticator");
}

function parseReceipt_(value: unknown): void {
  const source = object(value, "Receipt");
  required(source, ["descriptorDigest", "outcome", "observedAt", "resultDigest", "affectedResources"], "Receipt");
  for (const [field, kind] of [["descriptorDigest", "Digest"], ["observedAt", "Timestamp"], ["resultDigest", "Digest"]] as const) primitive(kind, source[field], `Receipt/${field}`);
  if (source.grantId !== undefined) primitive("GrantId", source.grantId, "Receipt/grantId");
  const outcome = oneOf(source.outcome, ["ok", "failed", "undeterminable"] as const, "Receipt/outcome");
  array(source.affectedResources, "Receipt/affectedResources").forEach((item, index) => {
    const itemPath = `Receipt/affectedResources/${index}`;
    const affected = object(item, itemPath);
    required(affected, ["resource", "change"], itemPath);
    string(affected.resource, `${itemPath}/resource`);
    const change = oneOf(affected.change, ["created", "modified", "deleted", "observed"] as const, `${itemPath}/change`);
    if (change !== "created" && affected.preDigest === undefined) fail("required", itemPath, "preDigest required");
    if (change !== "deleted" && affected.postDigest === undefined) fail("required", itemPath, "postDigest required");
    for (const field of ["preDigest", "postDigest", "patchRef"] as const) if (affected[field] !== undefined) primitive("Digest", affected[field], `${itemPath}/${field}`);
  });
  if (outcome === "undeterminable" && source.uncertainty === undefined) fail("required", "Receipt", "undeterminable requires uncertainty");
  if (source.uncertainty !== undefined) {
    const uncertainty = object(source.uncertainty, "Receipt/uncertainty");
    required(uncertainty, ["scope", "reason"], "Receipt/uncertainty");
    oneOf(uncertainty.scope, ["effect_occurrence", "evidence_completeness", "result"] as const, "Receipt/uncertainty/scope");
    string(uncertainty.reason, "Receipt/uncertainty/reason");
  }
}

function parseEvent(value: unknown): void {
  const source = object(value, "EventEnvelope");
  required(source, ["schemaVersion", "eventId", "scope", "traceId", "spanId", "seq", "occurredAt", "recordedAt", "principal", "principalRole", "tenantId", "ownerId", "confidentiality", "retentionClass", "trainability", "redactionStatus", "payload"], "EventEnvelope");
  for (const [field, kind] of [["schemaVersion", "SchemaVersion"], ["eventId", "Uuidv7"], ["seq", "IntString"], ["occurredAt", "Timestamp"], ["recordedAt", "Timestamp"], ["principal", "PrincipalId"], ["tenantId", "TenantId"], ["ownerId", "OwnerId"], ["confidentiality", "ConfidentialityLabel"], ["retentionClass", "RetentionClass"], ["trainability", "TrainabilityLabel"], ["redactionStatus", "RedactionStatus"]] as const) primitive(kind, source[field], `EventEnvelope/${field}`);
  const scope = oneOf(source.scope, ["episode", "governance", "evolution", "recovery"] as const, "EventEnvelope/scope");
  oneOf(source.principalRole, ["user", "operator", "episode", "process", "evaluator", "release"] as const, "EventEnvelope/principalRole");
  string(source.traceId, "EventEnvelope/traceId");
  string(source.spanId, "EventEnvelope/spanId");
  if ((scope === "episode" || scope === "recovery") && source.runId === undefined) fail("required", "EventEnvelope", `${scope} requires runId`);
  if (scope === "episode" && source.episodeId === undefined) fail("required", "EventEnvelope", "episode requires episodeId");
  if ((scope === "governance" || scope === "evolution") && source.runId !== undefined) fail("scope", "EventEnvelope/runId", `${scope} cannot carry runId`);
  if (scope !== "episode" && source.episodeId !== undefined) fail("scope", "EventEnvelope/episodeId", `${scope} cannot carry episodeId`);
  if (source.runId !== undefined) primitive("RunId", source.runId, "EventEnvelope/runId");
  if (source.episodeId !== undefined) primitive("EpisodeId", source.episodeId, "EventEnvelope/episodeId");
  const payload = object(source.payload, "EventEnvelope/payload");
  required(payload, ["kind"], "EventEnvelope/payload");
  string(payload.kind, "EventEnvelope/payload/kind");
}

function parseArtifact_(value: unknown): void {
  const source = object(value, "Artifact");
  required(source, ["artifactId", "kind", "class", "hypothesis", "evidenceRefs", "invalidationConditions", "riskDelta", "contentDigest"], "Artifact");
  primitive("ArtifactId", source.artifactId, "Artifact/artifactId");
  string(source.kind, "Artifact/kind");
  const artifactClass = oneOf(source.class, ["enforcement", "compensation"] as const, "Artifact/class");
  if (artifactClass === "compensation" && source.compensatesFor === undefined) fail("required", "Artifact", "compensation requires compensatesFor");
  if (artifactClass === "enforcement" && source.compensatesFor !== undefined) fail("not", "Artifact/compensatesFor", "enforcement cannot compensate");
  string(source.hypothesis, "Artifact/hypothesis");
  array(source.evidenceRefs, "Artifact/evidenceRefs").forEach((item, index) => primitive("Digest", item, `Artifact/evidenceRefs/${index}`));
  invalidation(source.invalidationConditions, "Artifact/invalidationConditions");
  if (typeof source.riskDelta !== "number" || !Number.isInteger(source.riskDelta)) fail("type", "Artifact/riskDelta", "expected integer");
  primitive("Digest", source.contentDigest, "Artifact/contentDigest");
  const keys = ["artifactId", "kind", "class", "compensatesFor", "hypothesis", "evidenceRefs", "invalidationConditions", "riskDelta"];
  const content = Object.fromEntries(keys.filter((key) => key in source).map((key) => [key, source[key]]));
  if (digestOf(content) !== source.contentDigest) fail("digest", "Artifact/contentDigest", "does not bind immutable content");
}

function parseClaim(value: unknown): void {
  const source = object(value, "EvidenceClaim");
  required(source, ["id", "subject", "predicate", "value", "protocol", "evaluator", "environmentProfile", "substrateProfile", "taskDistribution", "uncertainty", "validity", "invalidationConditions"], "EvidenceClaim");
  for (const [field, kind] of [["id", "ClaimId"], ["protocol", "Digest"], ["environmentProfile", "Digest"], ["substrateProfile", "Digest"], ["taskDistribution", "Digest"]] as const) primitive(kind, source[field], `EvidenceClaim/${field}`);
  string(source.subject, "EvidenceClaim/subject"); string(source.predicate, "EvidenceClaim/predicate");
  const evaluator = object(source.evaluator, "EvidenceClaim/evaluator"); required(evaluator, ["evaluatorId", "class", "imageDigest"], "EvidenceClaim/evaluator");
  primitive("EvaluatorId", evaluator.evaluatorId, "EvidenceClaim/evaluator/evaluatorId"); primitive("Digest", evaluator.imageDigest, "EvidenceClaim/evaluator/imageDigest");
  const validity = object(source.validity, "EvidenceClaim/validity"); required(validity, ["domains"], "EvidenceClaim/validity"); strings(validity.domains, "EvidenceClaim/validity/domains", true);
  invalidation(source.invalidationConditions, "EvidenceClaim/invalidationConditions");
}

function parseCorrection(value: unknown): void {
  const source = object(value, "CorrectionRecord");
  required(source, ["episodeId", "proposedPatchDigest", "acceptedPatchDigest", "reasonCodes", "magnitude", "scope", "correctingPrincipalRole"], "CorrectionRecord");
  for (const [field, kind] of [["episodeId", "EpisodeId"], ["proposedPatchDigest", "Digest"], ["acceptedPatchDigest", "Digest"]] as const) primitive(kind, source[field], `CorrectionRecord/${field}`);
  const reasons = strings(source.reasonCodes, "CorrectionRecord/reasonCodes", true);
  const allowed = ["functional_defect", "missing_requirement", "security_policy", "test_inadequacy", "maintainability", "architecture_preference", "style", "product_change", "environment_change", "reviewer_disagreement"] as const;
  for (const reason of reasons) oneOf(reason, allowed, "CorrectionRecord/reasonCodes");
  oneOf(source.magnitude, ["minor", "moderate", "major"] as const, "CorrectionRecord/magnitude");
  const scope = oneOf(source.scope, ["user", "team", "repo", "domain", "general"] as const, "CorrectionRecord/scope");
  if (reasons.some((reason) => reason === "style" || reason === "architecture_preference") && !["user", "team", "repo"].includes(scope)) fail("scope", "CorrectionRecord/scope", "style and preference corrections must remain local");
  oneOf(source.correctingPrincipalRole, ["user", "operator", "episode", "process", "evaluator", "release"] as const, "CorrectionRecord/correctingPrincipalRole");
}

function parseRecording_(value: unknown): void {
  const source = object(value, "Recording"); required(source, ["modelCassetteDigest", "imageDigest", "envSnapshotDigest", "seed", "clockPolicy"], "Recording");
  for (const field of ["modelCassetteDigest", "imageDigest", "envSnapshotDigest"] as const) primitive("Digest", source[field], `Recording/${field}`);
  primitive("IntString", source.seed, "Recording/seed"); oneOf(source.clockPolicy, ["recorded", "fixed", "logical"] as const, "Recording/clockPolicy");
}

function parseDefinition(value: unknown): void {
  const source = object(value, "ProcessDefinition"); required(source, ["definitionDigest", "states", "initialState", "transitions", "approvalPoints", "boundEffectVerbs"], "ProcessDefinition");
  primitive("Digest", source.definitionDigest, "ProcessDefinition/definitionDigest"); const states = new Set(strings(source.states, "ProcessDefinition/states", true));
  const initial = string(source.initialState, "ProcessDefinition/initialState"); if (!states.has(initial)) fail("state", "ProcessDefinition/initialState", "initial state is undeclared");
  const seen = new Set<string>(); array(source.transitions, "ProcessDefinition/transitions").forEach((item, index) => {
    const itemPath = `ProcessDefinition/transitions/${index}`; const transition = object(item, itemPath); required(transition, ["from", "eventKind", "to"], itemPath);
    const from = string(transition.from, `${itemPath}/from`); const eventKind = string(transition.eventKind, `${itemPath}/eventKind`); const to = string(transition.to, `${itemPath}/to`);
    if (!states.has(from) || !states.has(to)) fail("state", itemPath, "transition references undeclared state"); const edge = `${from}\0${eventKind}`; if (seen.has(edge)) fail("conflict", itemPath, "transition is nondeterministic"); seen.add(edge);
  });
  strings(source.approvalPoints, "ProcessDefinition/approvalPoints"); strings(source.boundEffectVerbs, "ProcessDefinition/boundEffectVerbs");
  const content = Object.fromEntries(["states", "initialState", "transitions", "approvalPoints", "boundEffectVerbs"].map((key) => [key, source[key]]));
  if (digestOf(content) !== source.definitionDigest) fail("digest", "ProcessDefinition/definitionDigest", "does not bind definition");
}

function parseInstance(value: unknown): void {
  const source = object(value, "ProcessInstance"); required(source, ["processId", "definitionDigest", "currentState", "allowedTransitions", "pendingApprovals", "boundEffectVerbs", "history"], "ProcessInstance");
  primitive("ProcessId", source.processId, "ProcessInstance/processId"); primitive("Digest", source.definitionDigest, "ProcessInstance/definitionDigest"); string(source.currentState, "ProcessInstance/currentState");
  strings(source.allowedTransitions, "ProcessInstance/allowedTransitions"); array(source.pendingApprovals, "ProcessInstance/pendingApprovals").forEach((item, index) => primitive("ApprovalId", item, `ProcessInstance/pendingApprovals/${index}`)); strings(source.boundEffectVerbs, "ProcessInstance/boundEffectVerbs");
  array(source.history, "ProcessInstance/history").forEach((item, index) => { const itemPath = `ProcessInstance/history/${index}`; const history = object(item, itemPath); required(history, ["from", "eventKind", "to", "eventId"], itemPath); for (const field of ["from", "eventKind", "to"] as const) string(history[field], `${itemPath}/${field}`); primitive("Uuidv7", history.eventId, `${itemPath}/eventId`); });
}

const PARSERS = {
  EffectDescriptor: parseEffect, CapabilityGrant: parseGrant, Receipt: parseReceipt_, EventEnvelope: parseEvent,
  Artifact: parseArtifact_, EvidenceClaim: parseClaim, CorrectionRecord: parseCorrection, Recording: parseRecording_,
  ProcessDefinition: parseDefinition, ProcessInstance: parseInstance,
} as const;

export type WireKind = keyof typeof PARSERS;
export const WIRE_KINDS = Object.freeze(Object.keys(PARSERS) as WireKind[]);

export function parseWire(kind: WireKind | string, value: unknown): WireObject {
  const parser = PARSERS[kind as WireKind];
  if (parser === undefined) fail("kind", String(kind), "unknown wire contract");
  parser(value);
  return structuredClone(object(value, String(kind)));
}

export const parseEffectDescriptor = (value: unknown): EffectDescriptor => parseWire("EffectDescriptor", value) as EffectDescriptor;
export const parseCapabilityGrant = (value: unknown): CapabilityGrant => parseWire("CapabilityGrant", value) as CapabilityGrant;
export const parseReceipt = (value: unknown): Receipt => parseWire("Receipt", value) as Receipt;
export const parseEventEnvelope = (value: unknown): EventEnvelope => parseWire("EventEnvelope", value) as EventEnvelope;
export const parseArtifact = (value: unknown): Artifact => parseWire("Artifact", value) as Artifact;
export const parseEvidenceClaim = (value: unknown): EvidenceClaim => parseWire("EvidenceClaim", value) as EvidenceClaim;

export function createEffectDescriptor(
  verb: string,
  args: Record<string, Json | undefined>,
  options: Omit<EffectDescriptor, "verb" | "args" | "argsDigest"> & { workspaceRoot: string; pathArguments?: readonly string[] },
): EffectDescriptor {
  const pathArguments = new Set(options.pathArguments ?? []);
  const normalized: Record<string, Json> = {};
  for (const [key, value] of Object.entries(args)) {
    if (value === undefined) continue;
    normalized[key] = pathArguments.has(key) && typeof value === "string"
      ? path.posix.resolve("/", options.workspaceRoot.replaceAll("\\", "/"), value.replaceAll("\\", "/"))
      : value;
  }
  const { workspaceRoot: _workspaceRoot, pathArguments: _pathArguments, ...wire } = options;
  return parseEffectDescriptor({ verb, args: normalized, argsDigest: digestOf(normalized), ...wire });
}

export function serialize<T>(value: T): string { return JSON.stringify(value); }
export function deserialize<T>(wire: string, parser: (value: unknown) => T): T { return parser(JSON.parse(wire)); }
