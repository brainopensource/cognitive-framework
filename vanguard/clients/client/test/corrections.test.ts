import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import { captureCorrection, correctionReasonForKey } from "../src/application/corrections.js";
import type { RuntimeClient } from "../src/client.js";
import type { RecordCorrectionRequest, Result, CommandReceipt } from "@aether/contracts";

/**
 * F4 corrections.ts decision: canonical vg.4 CorrectionRecord shape
 * (correctionId/runId/reasonCode/scope/recordedAt/author), with legacy
 * client-core fields (proposedPatchDigest/acceptedPatchDigest) kept
 * optional on the produced record for back-compat readers.
 *
 * Deliberately NOT shimmed into @vanguard/client-core yet: client-core's
 * LiveRuntimeClient.recordCorrection(record) wraps its argument into
 * {correction: record} itself, so a shim here would double-wrap the payload
 * for the CLI's still-unmigrated run-tui.tsx caller. Shimming happens in
 * Phase 4/5 alongside that call site's migration.
 */

describe("@aether/client — corrections (canonical vg.4 shape)", () => {
  it("produces a canonical CorrectionRecord and calls recordCorrection with the wrapped request", async () => {
    let received: RecordCorrectionRequest | undefined;
    const client: Pick<RuntimeClient, "recordCorrection"> = {
      async recordCorrection(request: RecordCorrectionRequest): Promise<Result<CommandReceipt>> {
        received = request;
        return { ok: true, value: { commandId: "cmd-1", status: "completed" } };
      },
    };

    const result = await captureCorrection(client, {
      runId: "run-42",
      episodeId: "episode-42",
      proposedPatchDigest: "sha256:aaa",
      acceptedPatchDigest: "sha256:bbb",
      key: "d",
    });

    assert.equal(result.ok, true);
    if (!result.ok) return;
    assert.equal(result.value.runId, "run-42");
    assert.equal(result.value.reasonCode, "functional_defect");
    assert.equal(result.value.scope, "local");
    assert.equal(result.value.author, "operator");
    assert.ok(result.value.correctionId.length > 0);
    assert.ok(result.value.recordedAt.length > 0);
    // legacy fields survive, optional and additive
    assert.equal(result.value.proposedPatchDigest, "sha256:aaa");
    assert.equal(result.value.acceptedPatchDigest, "sha256:bbb");

    assert.ok(received);
    assert.equal(received?.correction.correctionId, result.value.correctionId);
  });

  it("rejects an unknown correction key without calling the client", async () => {
    let called = false;
    const client: Pick<RuntimeClient, "recordCorrection"> = {
      async recordCorrection(): Promise<Result<CommandReceipt>> {
        called = true;
        return { ok: true, value: { commandId: "cmd-2", status: "completed" } };
      },
    };

    const result = await captureCorrection(client, { runId: "run-1", key: "z" });
    assert.equal(result.ok, false);
    if (!result.ok) assert.equal(result.error.code, "invalid_request");
    assert.equal(called, false);
  });

  it("correctionReasonForKey maps interactive keys, including the S/s security_policy alias", () => {
    assert.equal(correctionReasonForKey("d"), "functional_defect");
    assert.equal(correctionReasonForKey("s"), "style");
    assert.equal(correctionReasonForKey("S"), "security_policy");
    assert.equal(correctionReasonForKey("e"), "security_policy");
    assert.equal(correctionReasonForKey("z"), undefined);
  });
});
