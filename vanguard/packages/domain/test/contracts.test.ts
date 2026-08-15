import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import {
  createEffectDescriptor, deserialize, parseArtifact, parseCapabilityGrant,
  parseEffectDescriptor, parseEventEnvelope, parseEvidenceClaim, parseReceipt, serialize,
  type Artifact, type CapabilityGrant, type EventEnvelope, type EvidenceClaim, type Receipt,
} from "../index.ts";

const d = (digit: string) => `sha256:${digit.repeat(64)}` as const;
const roundTrip = <T>(value: T, parser: (input: unknown) => T) => deserialize(serialize(value), parser);

test("EffectDescriptor normalizes paths, omits absent optionals, excludes provider id, and binds digest", () => {
  const descriptor = createEffectDescriptor("fs.read", {
    providerCallId: undefined,
    target: "src/../README.md",
    content: "  unchanged  ",
  }, { workspaceRoot: "/workspace", pathArguments: ["target"] });
  assert.equal(descriptor.args.target, "/workspace/README.md");
  assert.equal(descriptor.args.content, "  unchanged  ");
  assert.equal("providerCallId" in descriptor.args, false);
  assert.deepEqual(roundTrip(descriptor, parseEffectDescriptor), descriptor);
  assert.throws(() => parseEffectDescriptor({ ...descriptor, name: "fs.write" }), /does not bind/);
});

test("CapabilityGrant round trips and rejects missing descriptor binding", () => {
  const grant: CapabilityGrant = {
    id: "grant-1", principal: "agent-1", descriptorDigest: d("1"), actions: ["fs.read"],
    resources: [{ kind: "fs", root: "file:///workspace", paths: ["README.md"] }],
    constraints: { expiresAt: "2026-08-15T12:00:00.000Z", maxUses: "1", budgetLeaseId: "lease-1" },
    purposeDigest: d("2"),
  };
  assert.deepEqual(roundTrip(grant, parseCapabilityGrant), grant);
  const { descriptorDigest: _, ...unbound } = grant;
  assert.throws(() => parseCapabilityGrant(unbound), /descriptorDigest/);
});

test("Receipt preserves resource evidence and requires scoped uncertainty", () => {
  const receipt: Receipt = {
    descriptorDigest: d("1"), grantId: "grant-1", outcome: "undeterminable",
    observedAt: "2026-08-15T12:00:01.000Z", resultDigest: d("3"), workingDirectory: "/workspace",
    affectedResources: [{ resource: "file:///workspace/a", change: "modified", preDigest: d("4"), postDigest: d("5"), patchRef: d("6") }],
    uncertainty: { scope: "effect_occurrence", reason: "transport failed after dispatch" },
  };
  assert.deepEqual(roundTrip(receipt, parseReceipt), receipt);
  assert.throws(() => parseReceipt({ ...receipt, uncertainty: undefined }), /requires uncertainty/);
  assert.throws(() => parseReceipt({ ...receipt, affectedResources: [{ resource: "x", change: "deleted" }] }), /preDigest/);
});

test("EventEnvelope enforces scope identifiers and round trips", () => {
  const envelope = JSON.parse(readFileSync("../../../schemas/v4/vectors/event-envelope/valid/evolution-scope.json", "utf8")) as EventEnvelope;
  assert.deepEqual(roundTrip(envelope, parseEventEnvelope), envelope);
  assert.throws(() => parseEventEnvelope({ ...envelope, scope: "episode" }), /requires runId/);
});

test("Artifact and EvidenceClaim reject empty invalidation conditions", () => {
  const artifact: Artifact = {
    id: "artifact-1", kind: "M", artifactVersion: "1.0.0", body: d("1"), interfaceSchema: "schema://method",
    createdBy: "agent-1", createdFrom: [], dependencies: [], supersedes: [], contentDigest: d("2"),
    createdAt: "2026-08-15T12:00:00.000Z",
    invalidationConditions: [{ condition: "suite fails", checkKind: "automatic", checkRef: "eval-suite" }],
  };
  assert.deepEqual(roundTrip(artifact, parseArtifact), artifact);
  assert.throws(() => parseArtifact({ ...artifact, invalidationConditions: [] }), /non-empty/);

  const claim = JSON.parse(readFileSync("../../../schemas/v4/vectors/evidence-claim/valid/minimal.json", "utf8")) as EvidenceClaim;
  assert.deepEqual(roundTrip(claim, parseEvidenceClaim), claim);
  assert.throws(() => parseEvidenceClaim({ ...claim, invalidationConditions: [] }), /non-empty/);
});
