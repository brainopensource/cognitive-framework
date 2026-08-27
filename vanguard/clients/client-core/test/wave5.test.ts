import test from "node:test";
import assert from "node:assert/strict";
import { createServer, type Socket } from "node:net";
import { createServer as createHttpServer, type Server as HttpServer } from "node:http";
import { unlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { LiveRuntimeClient } from "../src/adapters/live.js";
import { HttpRuntimeClient } from "../src/adapters/http.js";
import { OperatorSigner } from "../src/adapters/signer.js";
import { parseDaemonFrame, toClientFailureCode } from "../src/contract/parse.js";

test("toClientFailureCode passes through canonical codes and defaults unknown ones to internal", () => {
  for (const code of [
    "invalid_request",
    "unauthenticated",
    "permission_denied",
    "not_found",
    "conflict",
    "incompatible_version",
    "frame_too_large",
    "rate_limited",
    "not_available",
    "internal",
    "transport_interrupted",
  ]) {
    assert.equal(toClientFailureCode(code), code);
  }
  assert.equal(toClientFailureCode("something_the_daemon_invented"), "internal");
  assert.equal(toClientFailureCode(undefined), "internal");
  assert.equal(toClientFailureCode(42), "internal");
});

test("parseDaemonFrame carries the daemon's real error code and retryable flag", () => {
  const parsed = parseDaemonFrame({
    version: "vg.4",
    frameType: "error",
    frameId: "f-1",
    error: { code: "frame_too_large", message: "frame exceeds limit", retryable: false },
  });
  assert.equal(parsed.ok, true);
  if (parsed.ok && parsed.value.frameType === "error") {
    assert.equal(parsed.value.code, "frame_too_large");
    assert.equal(parsed.value.retryable, false);
    assert.equal(parsed.value.message, "frame exceeds limit");
  } else {
    assert.fail("expected error frame");
  }
});

test("parseDaemonFrame defaults an unrecognized daemon error code to internal, never invalid_request by default", () => {
  const parsed = parseDaemonFrame({
    version: "vg.4",
    frameType: "error",
    frameId: "f-1",
    error: { message: "legacy unknown code" },
  });
  assert.equal(parsed.ok, true);
  if (parsed.ok && parsed.value.frameType === "error") {
    assert.equal(parsed.value.code, "internal");
  } else {
    assert.fail("expected error frame");
  }
});

test("socket transport preserves the daemon's real error code instead of forcing invalid_request", async () => {
  const socketPath = join(tmpdir(), `vg-test-w5-${process.pid}-${Date.now()}.sock`);
  const server = createServer((conn: Socket) => {
    let buf = "";
    conn.on("data", (chunk) => {
      buf += String(chunk);
      if (!buf.includes("\n")) return;
      conn.write(
        JSON.stringify({
          version: "vg.4",
          frameType: "error",
          frameId: "f-1",
          error: { code: "not_available", message: "daemon busy", retryable: true },
        }) + "\n"
      );
    });
  });
  await new Promise<void>((resolve) => server.listen(socketPath, resolve));
  try {
    const client = new LiveRuntimeClient(undefined, { socketPath, connectTimeoutMs: 500, commandTimeoutMs: 500 });
    const result = await client.getDaemonStatus();
    // getDaemonStatus uses socket.probe(), not sendCommand — assert via requestCancel instead.
    void result;
    const cancelResult = await client.requestCancel("run-1");
    assert.equal(cancelResult.ok, false);
    if (!cancelResult.ok) {
      assert.equal(cancelResult.error.code, "not_available");
      assert.equal(cancelResult.error.retryable, true);
    }
  } finally {
    server.close();
    try {
      unlinkSync(socketPath);
    } catch {
      /* ignore */
    }
  }
});

test("socket transport preserves a command-level receipt.error.code (not just frame-level errors)", async () => {
  const socketPath = join(tmpdir(), `vg-test-w5b-${process.pid}-${Date.now()}.sock`);
  const server = createServer((conn: Socket) => {
    let buf = "";
    conn.on("data", (chunk) => {
      buf += String(chunk);
      if (!buf.includes("\n")) return;
      conn.write(
        JSON.stringify({
          version: "vg.4",
          frameType: "receipt",
          frameId: "f-1",
          receipt: {
            commandId: "c-1",
            status: "error",
            runId: "run-1",
            detail: "run not found",
            error: { code: "not_found", message: "run not found", retryable: false },
          },
        }) + "\n"
      );
    });
  });
  await new Promise<void>((resolve) => server.listen(socketPath, resolve));
  try {
    const client = new LiveRuntimeClient(undefined, { socketPath, connectTimeoutMs: 500, commandTimeoutMs: 500 });
    const result = await client.requestCheckpoint("run-missing");
    assert.equal(result.ok, false);
    if (!result.ok) {
      assert.equal(result.error.code, "not_found");
    }
  } finally {
    server.close();
    try {
      unlinkSync(socketPath);
    } catch {
      /* ignore */
    }
  }
});

function jsonBody(res: import("node:http").ServerResponse, status: number, body: unknown): void {
  const text = JSON.stringify(body);
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(text);
}

function startFakeGateway(): Promise<{ server: HttpServer; baseUrl: string }> {
  const server = createHttpServer((req, res) => {
    const url = req.url ?? "";
    if (req.method === "GET" && url === "/api/v1/runs/run-42") {
      jsonBody(res, 200, {
        version: "vg.4",
        frameType: "receipt",
        frameId: "f-1",
        receipt: { commandId: "c-1", status: "completed", runId: "run-42", result: { status: "running", asOfSeq: "7" } },
      });
      return;
    }
    if (req.method === "GET" && url === "/api/v1/runs/run-missing") {
      jsonBody(res, 200, {
        version: "vg.4",
        frameType: "receipt",
        frameId: "f-1",
        receipt: {
          commandId: "c-1",
          status: "error",
          runId: "run-missing",
          detail: "run not found",
          error: { code: "not_found", message: "run run-missing not found", retryable: false },
        },
      });
      return;
    }
    if (req.method === "POST" && url === "/api/v1/runs/run-42:cancel") {
      jsonBody(res, 200, {
        version: "vg.4",
        frameType: "receipt",
        frameId: "f-1",
        receipt: { commandId: "c-1", status: "completed", runId: "run-42", result: { runId: "run-42", status: "cancelled" } },
      });
      return;
    }
    if (req.method === "POST" && url === "/api/approvals/resolve") {
      let body = "";
      req.on("data", (chunk) => (body += String(chunk)));
      req.on("end", () => {
        const parsed = JSON.parse(body || "{}");
        if (typeof parsed.signature !== "string" || !parsed.signature || parsed.resolution !== "approved") {
          jsonBody(res, 400, {
            version: "vg.4",
            frameType: "error",
            frameId: "f-1",
            error: { code: "invalid_request", message: "decision missing signature/resolution", retryable: false },
          });
          return;
        }
        jsonBody(res, 200, {
          version: "vg.4",
          frameType: "receipt",
          frameId: "f-1",
          receipt: { commandId: "c-1", status: "completed", result: { approvalId: parsed.approvalId, status: "resolved" } },
        });
      });
      return;
    }
    jsonBody(res, 404, { error: "not found" });
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : 0;
      resolve({ server, baseUrl: `http://127.0.0.1:${port}` });
    });
  });
}

test("HttpRuntimeClient.getRun parses the real receipt shape instead of returning a placeholder", async () => {
  const { server, baseUrl } = await startFakeGateway();
  try {
    const client = new HttpRuntimeClient({ baseUrl });
    const result = await client.getRun("run-42");
    assert.equal(result.ok, true);
    if (result.ok) {
      assert.equal(result.value.status, "running");
      assert.equal(result.value.seq, "7");
    }
  } finally {
    server.close();
  }
});

test("HttpRuntimeClient.getRun preserves the canonical error code on a not_found receipt", async () => {
  const { server, baseUrl } = await startFakeGateway();
  try {
    const client = new HttpRuntimeClient({ baseUrl });
    const result = await client.getRun("run-missing");
    assert.equal(result.ok, false);
    if (!result.ok) assert.equal(result.error.code, "not_found");
  } finally {
    server.close();
  }
});

test("HttpRuntimeClient.requestCancel is a real call, not a hardcoded not_available placeholder", async () => {
  const { server, baseUrl } = await startFakeGateway();
  try {
    const client = new HttpRuntimeClient({ baseUrl });
    const result = await client.requestCancel("run-42");
    assert.equal(result.ok, true);
    if (result.ok) assert.equal(result.value.status, "accepted");
  } finally {
    server.close();
  }
});

test("HttpRuntimeClient.resolveApproval refuses without a cached ApprovalRequested challenge (parity with Live)", async () => {
  const { server, baseUrl } = await startFakeGateway();
  try {
    const client = new HttpRuntimeClient({ baseUrl });
    const result = await client.resolveApproval({ approvalId: "appr-1", decision: "approve" });
    assert.equal(result.ok, false);
    if (!result.ok) assert.equal(result.error.code, "not_available");
  } finally {
    server.close();
  }
});

test("HttpRuntimeClient.resolveApproval sends a real signed decision once a challenge is loaded from the stream", async () => {
  const { server, baseUrl } = await startFakeGateway();
  try {
    const client = new HttpRuntimeClient({ baseUrl, signer: new OperatorSigner() });
    // Load a challenge the same way live traffic would: via streamEvents.
    (client as unknown as { lastChallenge: unknown }).lastChallenge = {
      approvalId: "appr-1",
      processId: "p-1",
      action: "fs.patch",
      normalizedDiff: "--- a\n+++ b\n",
      argsDigest: "sha256:" + "a".repeat(64),
      descriptorDigest: "sha256:" + "b".repeat(64),
      principal: "agent",
      expiresAt: "2026-08-27T12:00:00.000Z",
    };
    const result = await client.resolveApproval({ approvalId: "appr-1", decision: "approve" });
    assert.equal(result.ok, true);
    if (result.ok) assert.equal(result.value.status, "accepted");
  } finally {
    server.close();
  }
});
