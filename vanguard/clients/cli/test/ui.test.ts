import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { reduceRunView, emptyRunView } from "../src/application/run-view.js";
import { captureCorrection, correctionReasonForKey } from "../src/application/corrections.js";
import { dispatchApproval } from "../src/application/approvals.js";
import { submitInteractiveApproval } from "../src/composition/operator-approval.js";
import { OperatorSigner } from "../src/adapters/signer.js";
import { approvalActionForKey } from "../src/tui/keys.js";
import { colorizeUnifiedDiff } from "../src/tui/diff.js";
import {
  shouldDispatchApproval,
  shouldRequestCancel,
  submitBrief,
} from "../src/tui/focus.js";
import { windowTranscript } from "../src/tui/transcript-window.js";
import { formatStatusBar } from "../src/tui/status-bar.js";
import { performResume } from "../src/composition/resume-session.js";
import { whyText } from "../src/tui/why-display.js";
import { HELP_TEXT } from "../src/tui/focus.js";
import { subscribeRun } from "@vanguard/client-core";
import type { CorrectionRecord, EventEnvelope, Result as CoreResult } from "../src/contract/types.js";
// F4 Phase 2: dispatchApproval is now ported to @aether/client, typed against
// @aether/contracts's ResolveApprovalRequest/CommandReceipt (approvalId is
// optional there vs. required in this package's own contract/types.js).
// recordCorrection stays on this package's own CorrectionRecord shape --
// corrections.ts is deliberately not shimmed yet (see F4 plan).
import type { CommandReceipt, ResolveApprovalRequest, Result } from "@aether/contracts";

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

class RecordingClient {
  readonly approvals: ResolveApprovalRequest[] = [];
  readonly corrections: CorrectionRecord[] = [];

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    this.approvals.push(request);
    return { ok: true, value: { commandId: "cmd-resolve-approval", runId: "run-1", status: "completed" } };
  }

  async recordCorrection(record: CorrectionRecord): Promise<CoreResult<{ runId: string; command: "record_correction"; status: "requested" }>> {
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

test("prompt mode does not dispatch approval on y", () => {
  assert.equal(shouldDispatchApproval("prompt", "y"), false);
  assert.equal(shouldDispatchApproval("approval", "y"), true);
  assert.equal(shouldDispatchApproval("run", "y"), false);
});

test("empty Enter does not start a run", () => {
  const result = submitBrief("   ");
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.error.code, "invalid_request");
  const ok = submitBrief("fix the test");
  assert.equal(ok.ok, true);
});

test("windowTranscript clamps 100 thoughts to height", () => {
  const view = {
    ...emptyRunView(),
    thoughts: Array.from({ length: 100 }, (_, i) => `thought-${i}`),
  };
  const win = windowTranscript(view, 0, 16);
  assert.equal(win.rows.length, 16);
  assert.equal(win.total, 100);
  const end = windowTranscript(view, 10_000, 16);
  assert.equal(end.rows.length, 16);
  assert.equal(end.cursor, 84);
});

test("ctrl+c maps to cancel; Esc in prompt does not", () => {
  assert.equal(shouldRequestCancel("prompt", { ctrlC: true, escape: false }), true);
  assert.equal(shouldRequestCancel("prompt", { ctrlC: false, escape: true }), false);
  assert.equal(shouldRequestCancel("run", { ctrlC: false, escape: true }), true);
});

test("status bar labels mock and never looks live", () => {
  const line = formatStatusBar({
    source: "mock",
    seq: "3",
    tokens: 42,
    costMicros: "900",
    kind: "BudgetCommitted",
  });
  assert.match(line, /source: mock/);
  assert.equal(/source: live/.test(line), false);
  assert.match(line, /daemon: unknown/);
  assert.equal(/policy: daemon/.test(line), false);
});

test("subscribeRun abort does not throw", async () => {
  const ac = new AbortController();
  ac.abort();
  let streamed = 0;
  await subscribeRun(
    {
      async *streamEvents() {
        streamed += 1;
        yield {
          ok: true as const,
          value: { contractVersion: "0.1" as const, source: "live" as const, envelope: envelope("Heartbeat") },
        };
      },
    },
    { runId: "run-1" },
    { onItem() {} },
    ac.signal
  );
  assert.equal(streamed, 0);
});

test("resume not_available does not start a mock stream", async () => {
  let streams = 0;
  const client = {
    async requestResume() {
      return { ok: false as const, error: { code: "not_available" as const, message: "no daemon", retryable: false } };
    },
    async *streamEvents() {
      streams += 1;
    },
  };
  const result = await performResume(client, "run-1");
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.code, "not_available");
  assert.equal(streams, 0);
});

test("whyText prints error.code only when explainArtifact fails", () => {
  const text = whyText({
    ok: false,
    error: { code: "not_available", message: "no evidence", retryable: false },
  });
  assert.equal(text, "not_available");
});

test("help lists resume commands", () => {
  assert.match(HELP_TEXT, /vg run --resume/);
  assert.match(HELP_TEXT, /\br\b/);
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

const CHALLENGE_DIGEST_A = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const CHALLENGE_DIGEST_B = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

test("interactive y/n with challenge digests attaches an OperatorSigner signature", async () => {
  const client = new RecordingClient();
  const signer = new OperatorSigner();
  const pending = {
    approvalId: "appr-1",
    unifiedDiff: "+x\n",
    proposedPatchDigest: DIGEST_A,
    episodeId: "episode-1",
    argsDigest: CHALLENGE_DIGEST_A,
    descriptorDigest: CHALLENGE_DIGEST_B,
    expiresAt: "2026-08-16T00:00:00.000Z",
  };
  const approved = await submitInteractiveApproval(client, pending, "y", signer);
  assert.equal(approved.ok, true);
  assert.equal(client.approvals[0]?.decision, "approve");
  assert.equal(typeof client.approvals[0]?.signature, "string");
  assert.ok((client.approvals[0]?.signature ?? "").length > 0);
  assert.equal(client.approvals[0]?.signerKeyRef, signer.keyId);
});

test("interactive approval without challenge digests does not fabricate a signature", async () => {
  const client = new RecordingClient();
  const pending = {
    approvalId: "appr-1",
    unifiedDiff: "+x\n",
    proposedPatchDigest: DIGEST_A,
    episodeId: "episode-1",
    argsDigest: "",
    descriptorDigest: "",
    expiresAt: "",
  };
  const result = await submitInteractiveApproval(client, pending, "y", new OperatorSigner());
  assert.equal(result.ok, true);
  assert.deepEqual(client.approvals, [{ approvalId: "appr-1", decision: "approve" }]);
});

test("TUI presentation consumes @vanguard/client-core", () => {
  let dir = dirname(fileURLToPath(import.meta.url));
  while (!existsSync(join(dir, "package.json"))) dir = dirname(dir);
  const files = [
    "src/main.tsx",
    "src/composition/client-for.ts",
    "src/composition/parse-cli.ts",
    "src/composition/operator-approval.ts",
    "src/tui/hooks/use-vanguard-run.ts",
    "src/tui/screens/run-tui.tsx",
    "src/tui/status-bar.ts",
    "src/composition/resume-session.ts",
  ];
  for (const rel of files) {
    const source = readFileSync(join(dir, rel), "utf8");
    assert.match(source, /@vanguard\/client-core/, rel);
  }
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
  assert.equal(/from ["'].*tui\//.test(source), false);
});

test("application layer does not import tui presentation", () => {
  let dir = dirname(fileURLToPath(import.meta.url));
  while (!existsSync(join(dir, "package.json"))) dir = dirname(dir);
  const files = [
    "src/application/commands.ts",
    "src/application/run-view.ts",
    "src/application/approvals.ts",
    "src/application/corrections.ts",
  ];
  for (const rel of files) {
    const source = readFileSync(join(dir, rel), "utf8");
    assert.equal(/from ["'].*\/tui\//.test(source), false, rel);
  }
});
