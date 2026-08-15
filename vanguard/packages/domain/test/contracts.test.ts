import assert from "node:assert/strict";
import test from "node:test";

import {
  createEffectDescriptor, deserialize, digestOf, parseArtifact, parseCapabilityGrant,
  parseEffectDescriptor, parseEventEnvelope, parseEvidenceClaim, parseReceipt, parseWire, serialize,
  type Artifact, type CapabilityGrant, type EventEnvelope, type EvidenceClaim, type Receipt,
} from "../index.ts";

const d = (digit: string) => `sha256:${digit.repeat(64)}`;
const roundTrip = <T>(value: T, parser: (input: unknown) => T) => deserialize(serialize(value), parser);
const condition = { condition: "suite fails", checkKind: "automatic", checkRef: "eval-suite" };

test("EffectDescriptor normalises path arguments and binds canonical args", () => {
  const descriptor = createEffectDescriptor("fs.read", { target: "src/../README.md", providerCallId: undefined }, {
    workspaceRoot: "/workspace", pathArguments: ["target"], sinkClass: "observation",
    selector: { kind: "fs", root: "file:///workspace", paths: ["README.md"] },
    idempotencyKey: "read-1", riskTier: "low", workingDirectory: "/workspace",
    provenance: { origin: "operator", instructionAuthority: "directive", integrity: "attested", confidentiality: "internal", epistemic: "observed" },
  });
  assert.equal(descriptor.args.target, "/workspace/README.md");
  assert.equal("providerCallId" in descriptor.args, false);
  assert.deepEqual(roundTrip(descriptor, parseEffectDescriptor), descriptor);
  assert.throws(() => parseEffectDescriptor({ ...descriptor, args: { target: "/other" } }), /does not bind/);
});

test("CapabilityGrant binds one descriptor and validates its authority surface", () => {
  const grant: CapabilityGrant = {
    grantId: "grant-1", principal: "agent-1", descriptorDigest: d("1"), actions: ["fs.read"],
    selector: { kind: "fs", root: "file:///workspace", paths: ["README.md"] },
    constraints: { budgetLeaseId: "lease-1", requirePreview: true },
    expiry: "2026-08-15T12:00:00.000Z", maxUses: "1", purposeDigest: d("2"),
  };
  assert.deepEqual(roundTrip(grant, parseCapabilityGrant), grant);
  const { descriptorDigest: _, ...unbound } = grant;
  assert.throws(() => parseCapabilityGrant(unbound), /descriptorDigest/);
});

test("Receipt preserves resource evidence and scoped uncertainty", () => {
  const receipt: Receipt = {
    descriptorDigest: d("1"), grantId: "grant-1", outcome: "undeterminable",
    observedAt: "2026-08-15T12:00:01.000Z", resultDigest: d("3"), workingDirectory: "/workspace",
    affectedResources: [{ resource: "file:///workspace/a", change: "modified", preDigest: d("4"), postDigest: d("5") }],
    uncertainty: { scope: "effect_occurrence", reason: "transport failed after dispatch" },
  };
  assert.deepEqual(roundTrip(receipt, parseReceipt), receipt);
  assert.throws(() => parseReceipt({ ...receipt, uncertainty: undefined }), /undeterminable requires uncertainty/);
});

test("EventEnvelope enforces truthful scope identifiers", () => {
  const envelope: EventEnvelope = {
    schemaVersion: "vg.4", eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8b", scope: "evolution",
    traceId: "trace-1", spanId: "span-1", seq: "417", occurredAt: "2026-08-14T10:22:31.004Z",
    recordedAt: "2026-08-14T10:22:31.019Z", principal: "release-controller", principalRole: "release",
    tenantId: "tenant-default", ownerId: "owner-platform", confidentiality: "internal", retentionClass: "extended",
    trainability: "prohibited", redactionStatus: "none", payload: { kind: "CandidateAttested" },
  };
  assert.deepEqual(roundTrip(envelope, parseEventEnvelope), envelope);
  assert.throws(() => parseEventEnvelope({ ...envelope, scope: "episode" }), /requires runId/);
});

test("Artifact content address and Claim invalidation are enforced", () => {
  const content = { artifactId: "artifact-1", kind: "playbook", class: "enforcement", hypothesis: "reduces regressions", evidenceRefs: [d("1")], invalidationConditions: [condition], riskDelta: -1 };
  const artifact: Artifact = { ...content, contentDigest: digestOf(content) } as Artifact;
  assert.deepEqual(roundTrip(artifact, parseArtifact), artifact);
  assert.throws(() => parseArtifact({ ...artifact, riskDelta: 2 }), /does not bind/);

  const claim: EvidenceClaim = {
    id: "claim-1", subject: "artifact-1", predicate: "passes", value: true, protocol: d("1"),
    evaluator: { evaluatorId: "eval-suite", class: "mechanically_reproducible", imageDigest: d("2") },
    environmentProfile: d("3"), substrateProfile: d("4"), taskDistribution: d("5"),
    uncertainty: { kind: "point" }, validity: { domains: ["typescript"] }, invalidationConditions: [condition],
  };
  assert.deepEqual(roundTrip(claim, parseEvidenceClaim), claim);
  assert.throws(() => parseEvidenceClaim({ ...claim, invalidationConditions: [] }), /must not be empty/);
});

test("reader profile preserves unknown fields at every level", () => {
  const recording = { modelCassetteDigest: d("1"), imageDigest: d("2"), envSnapshotDigest: d("3"), seed: "7", clockPolicy: "fixed", future: { nested: true } };
  assert.deepEqual(parseWire("Recording", recording), recording);
});
