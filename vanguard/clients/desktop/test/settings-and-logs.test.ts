import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { installMockDom } from "./support/mock-dom.js";
import { DesktopStore } from "../src/state/desktop-store.js";
import { renderCredentialPanel } from "../src/components/CredentialPanel.js";
import { renderLogsPane } from "../src/components/LogsPane.js";
import type { EventEnvelope } from "@aether/contracts";

function textOf(node: any): string {
  const own = node.textContent ?? "";
  const children = (node.children ?? []).map(textOf).join(" ");
  return `${own} ${children}`.trim();
}

function envelope(seq: string, payload: Record<string, unknown>): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId: `evt-${seq}`,
    scope: "run",
    runId: "run-1",
    seq,
    occurredAt: "2026-01-01T00:00:00.000Z",
    recordedAt: "2026-01-01T00:00:00.000Z",
    principal: "runtime",
    payload,
  } as unknown as EventEnvelope;
}

describe("@aether/desktop — credential panel reports the runtime's answer", () => {
  before(() => installMockDom());

  it("says it is checking before the runtime has answered", () => {
    const store = new DesktopStore();
    assert.match(textOf(renderCredentialPanel(store)), /CHECKING/);
  });

  it("never claims a key is configured on its own authority", () => {
    const store = new DesktopStore();
    // The defect this replaces: a pane that rendered CONFIGURED with no key.
    assert.doesNotMatch(textOf(renderCredentialPanel(store)), /READY/);
  });

  it("surfaces the remedy for an unreadable .env", () => {
    const store = new DesktopStore();
    store.update((s) => ({
      ...s,
      credential: {
        keyRef: "OPENROUTER_API_KEY",
        state: "DENIED",
        source: "/repo/.env",
        detail: "secret file has permissive permissions",
        remedy: "Run: chmod 600 /repo/.env",
      },
    }));

    const text = textOf(renderCredentialPanel(store));
    assert.match(text, /UNREADABLE/);
    assert.match(text, /chmod 600/);
  });

  it("shows a missing key as NO KEY, not as an error state", () => {
    const store = new DesktopStore();
    store.update((s) => ({
      ...s,
      credential: {
        keyRef: "OPENROUTER_API_KEY",
        state: "MISSING",
        source: "/repo/.env",
        detail: "secret file not found",
        remedy: "Add OPENROUTER_API_KEY=<your key>",
      },
    }));
    assert.match(textOf(renderCredentialPanel(store)), /NO KEY/);
  });

  it("reports a probe failure in full rather than silently", () => {
    const store = new DesktopStore();
    store.update((s) => ({
      ...s,
      credentialProbe: {
        ok: false,
        model: "openrouter/free",
        keyRef: "OPENROUTER_API_KEY",
        state: "INVALID",
        source: "",
        detail: "provider rejected the key (HTTP 401)",
        remedy: "",
      },
    }));
    assert.match(textOf(renderCredentialPanel(store)), /HTTP 401/);
  });

  it("says Testing while a probe is in flight", () => {
    const store = new DesktopStore();
    store.update((s) => ({ ...s, credentialProbeRunning: true }));
    assert.match(textOf(renderCredentialPanel(store)), /Testing/);
  });
});

describe("@aether/desktop — logs pane exposes the raw ledger", () => {
  before(() => installMockDom());

  it("explains an empty ledger instead of rendering blank", () => {
    const store = new DesktopStore();
    assert.match(textOf(renderLogsPane(store)), /Send an instruction/);
  });

  it("distinguishes an accepted run that has published nothing", () => {
    const store = new DesktopStore();
    store.update((s) => ({ ...s, runId: "run-1" }));
    assert.match(textOf(renderLogsPane(store)), /published no events yet/);
  });

  it("renders a failure event that the transcript has no projection for", () => {
    const store = new DesktopStore();
    store.update((s) => ({
      ...s,
      runId: "run-1",
      events: [
        envelope("1", { kind: "Heartbeat", producer: "RuntimeService" }),
        envelope("2", { kind: "RunFailed", error: "manifest has unread fields" }),
      ],
    }));

    const text = textOf(renderLogsPane(store));
    assert.match(text, /RunFailed/);
    assert.match(text, /manifest has unread fields/);
    assert.match(text, /2 events/);
  });

  it("keeps events in sequence order", () => {
    const store = new DesktopStore();
    store.update((s) => ({
      ...s,
      runId: "run-1",
      events: [
        envelope("1", { kind: "Heartbeat" }),
        envelope("2", { kind: "RunFailed", error: "boom" }),
      ],
    }));
    const rows = (renderLogsPane(store) as any).children[1].children;
    assert.equal(rows[0].children[0].textContent, "1");
    assert.equal(rows[1].children[0].textContent, "2");
  });
});
