import { test } from "node:test";
import assert from "node:assert/strict";
import { DesktopStore } from "../src/state/desktop-store.js";
import { DesktopApp } from "../src/components/App.js";
import { InMemoryPersistenceAdapter, FrontendAppController } from "@aether/client";
import type { EventEnvelope } from "@aether/contracts";

function makeEnv(eventId: string, seq: string, payload: Record<string, unknown> & { kind: string }, runId = "run-1"): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId,
    scope: "episode",
    runId,
    traceId: "t-1",
    spanId: `s-${seq}`,
    seq,
    occurredAt: new Date().toISOString(),
    recordedAt: new Date().toISOString(),
    principal: "test",
    tenantId: "t",
    ownerId: "o",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload,
  };
}

test("Desktop daily-use: startup readiness, provider selection, and draft continuity", async () => {
  const persistence = new InMemoryPersistenceAdapter();
  const controller = new FrontendAppController({ persistence });
  const store = new DesktopStore({ controller });

  // 1. Initial State
  const initial = store.get();
  assert.equal(initial.providers.length >= 3, true);

  // 2. Draft Autosave
  store.setDraft("Test prompt draft");
  assert.equal(store.get().composerText, "Test prompt draft");
  assert.equal(await persistence.loadDraft(store.get().activeSessionId), "Test prompt draft");

  // 3. Mutation and Verification Ingestion
  store.ingestEnvelope(
    makeEnv("00000000-0000-0000-0000-000000000001", "1", {
      kind: "GoalDeclared",
      goal: "Implement authentication middleware",
    })
  );

  store.ingestEnvelope(
    makeEnv("00000000-0000-0000-0000-000000000002", "2", {
      kind: "ApprovalRequested",
      approvalId: "app-auth-1",
      action: "Modify auth middleware",
      unifiedDiff: "--- a/auth.ts\n+++ b/auth.ts\n+export const checkAuth = () => true;",
    })
  );

  store.ingestEnvelope(
    makeEnv("00000000-0000-0000-0000-000000000003", "3", {
      kind: "ApprovalResolved",
      approvalId: "app-auth-1",
      resolution: "approved",
    })
  );

  store.ingestEnvelope(
    makeEnv("00000000-0000-0000-0000-000000000004", "4", {
      kind: "PatchApplied",
      approvalId: "app-auth-1",
    })
  );

  store.ingestEnvelope(
    makeEnv("00000000-0000-0000-0000-000000000005", "5", {
      kind: "VerificationPassed",
    })
  );

  const state = store.get();
  assert.equal(state.multiFileDiff.overallStatus, "VERIFIED");
  assert.equal(state.multiFileDiff.files[0]?.filePath, "auth.ts");
});

test("Desktop mount & unmount with readiness modal rendering", () => {
  // Provide DOM mock if needed
  if (typeof document === "undefined") {
    (globalThis as any).document = {
      createElement: (tag: string) => {
        const el: any = {
          tagName: tag.toUpperCase(),
          className: "",
          style: { cssText: "" },
          innerHTML: "",
          textContent: "",
          children: [] as any[],
          appendChild: (child: any) => {
            el.children.push(child);
            return child;
          },
          querySelectorAll: () => [],
          querySelector: () => null,
        };
        return el;
      },
      head: {
        appendChild: () => {},
      },
    };
  }

  const store = new DesktopStore();
  const app = new DesktopApp({ store });

  const root = (globalThis as any).document.createElement("div");

  // Mount
  app.mount(root);
  assert.equal(typeof app.render, "function");

  // Unmount
  app.unmount();
});
