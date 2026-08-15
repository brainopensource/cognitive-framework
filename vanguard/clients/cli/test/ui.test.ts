import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { reduceRunView, emptyRunView } from "../src/application/run-view.js";
import { captureCorrection, correctionReasonForKey } from "../src/application/corrections.js";
import { dispatchApproval } from "../src/application/approvals.js";
import { approvalActionForKey } from "../src/ui/keys.js";
import { colorizeUnifiedDiff } from "../src/ui/diff.js";
import type {
  CorrectionRecord,
  EventEnvelope,
  Result,
  ResolveApprovalRequest,
  RuntimeClient,
} from "../src/contract/types.js";

const DIGEST_A = "sha256:1111111111111111111111111111111111111111111111111111111111111111";
const DIGEST_B = "sha256:2222222222222222222222222222222222222222222222222222222222222222";

function envelope(kind: string, payload: Record<string, unknown> = {}, extra: Partial<EventEnvelope> = {}): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
    scope: "episode",
    runId: "run-1",
    episodeId: "episode-1",
    traceId: "trace-1",
    spanId: "span-1",
    seq: extra.seq ?? "1",
    occurredAt: "2026-08-15T00:00:00.000Z",
    recordedAt: "2026-08-15T00:00:00.001Z",
    principal: "agent-1",
    principalRole: "episode",
    tenantId: "tenant-default",
    ownerId: "owner-platform",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind, ...payload },
    ...extra,
  };
}

class RecordingClient implements Pick<RuntimeClient, "resolveApproval" | "recordCorrection"> {
  readonly approvals: ResolveApprovalRequest[] = [];
  readonly corrections: CorrectionRecord[] = [];

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<{ runId: string; command: "resolve_approval"; status: "requested" }>> {
    this.approvals.push(request);
    return { ok: true, value: { runId: "run-1", command: "resolve_approval", status: "requested" } };
  }

  async recordCorrection(record: CorrectionRecord): Promise<Result<{ runId: string; command: "record_correction"; status: "requested" }>> {
    this.corrections.push(record);
    return { ok: true, value: { runId: "run-1", command: "record_correction", status: "requested" } };
  }
}

test("live run view reduces thoughts, tool invocations, and token counters", () => {
  let view = emptyRunView();
  view = reduceRunView(view, envelope("ObservationProduced", { text: "inspect the failing test" }, { seq: "1" }));
  view = reduceRunView(view, envelope("OperatorInvoked", { tool: "read", status: "running" }, { seq: "2", eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8d" }));
  view = reduceRunView(view, envelope("BudgetCommitted", { tokens: 42, costMicros: "900" }, { seq: "3", eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8e" }));
  view = reduceRunView(view, envelope("UnknownFutureEvent", { extra: true }, { seq: "4", eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8f" }));
  assert.deepEqual(view.thoughts, ["inspect the failing test"]);
  assert.equal(view.tools[0]?.name, "read");
  assert.equal(view.tokens, 42);
  assert.equal(view.costMicros, "900");
});

test("approval modal keys dispatch approve, reject, and correct without mutating domain state", () => {
  assert.equal(approvalActionForKey("y"), "approve");
  assert.equal(approvalActionForKey("n"), "reject");
  assert.equal(approvalActionForKey("c"), "correct");
  assert.equal(approvalActionForKey("q"), undefined);
});

test("approve and reject callbacks submit resolveApproval receipts only", async () => {
  const client = new RecordingClient();
  const approved = await dispatchApproval(client, "appr-1", "y");
  const rejected = await dispatchApproval(client, "appr-1", "n");
  assert.equal(approved.ok, true);
  assert.equal(rejected.ok, true);
  assert.deepEqual(client.approvals, [
    { approvalId: "appr-1", decision: "approve" },
    { approvalId: "appr-1", decision: "reject" },
  ]);
});

test("correction keys map onto VG-04 reason codes including security and architecture", () => {
  assert.equal(correctionReasonForKey("d"), "functional_defect");
  assert.equal(correctionReasonForKey("s"), "style");
  assert.equal(correctionReasonForKey("t"), "test_inadequacy");
  assert.equal(correctionReasonForKey("e"), "security_policy");
  assert.equal(correctionReasonForKey("a"), "architecture_preference");
});

test("correction capture persists a typed CorrectionRecord through RuntimeClient", async () => {
  const client = new RecordingClient();
  const result = await captureCorrection(client, {
    episodeId: "episode-1",
    proposedPatchDigest: DIGEST_A,
    acceptedPatchDigest: DIGEST_B,
    key: "d",
  });
  assert.equal(result.ok, true);
  assert.equal(client.corrections.length, 1);
  const record = client.corrections[0]!;
  assert.equal(record.episodeId, "episode-1");
  assert.deepEqual(record.reasonCodes, ["functional_defect"]);
  assert.equal(record.magnitude, "minor");
  assert.equal(record.scope, "repo");
  assert.equal(record.correctingPrincipalRole, "user");
  assert.equal(record.proposedPatchDigest, DIGEST_A);
  assert.equal(record.acceptedPatchDigest, DIGEST_B);
});

test("style corrections stay local-scoped so they cannot become general competence", async () => {
  const client = new RecordingClient();
  const result = await captureCorrection(client, {
    episodeId: "episode-1",
    proposedPatchDigest: DIGEST_A,
    acceptedPatchDigest: DIGEST_A,
    key: "s",
  });
  assert.equal(result.ok, true);
  assert.equal(client.corrections[0]?.reasonCodes[0], "style");
  assert.equal(client.corrections[0]?.scope, "repo");
});

test("unified diff renderer tags additions and deletions without emitting raw CSI in the model", () => {
  const lines = colorizeUnifiedDiff("@@ -1,2 +1,2 @@\n-old\n+new\n context");
  assert.equal(lines[1]?.kind, "deletion");
  assert.equal(lines[2]?.kind, "addition");
  assert.equal(lines[3]?.kind, "context");
  for (const line of lines) assert.equal(line.text.includes("\u001b"), false);
});

test("headless command module does not import Ink UI screens", () => {
  let dir = dirname(fileURLToPath(import.meta.url));
  while (!existsSync(join(dir, "package.json"))) dir = dirname(dir);
  const source = readFileSync(join(dir, "src/application/commands.ts"), "utf8");
  assert.equal(/from ["'].*ui\//.test(source), false);
});
