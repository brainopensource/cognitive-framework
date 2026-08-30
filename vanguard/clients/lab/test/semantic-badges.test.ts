import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import {
  renderRunStatusBadge,
  renderConnectionStatusBadge,
  renderVerdictBadge,
  renderApprovalStatusBadge,
  renderCapabilityStatusBadge,
  renderEventKindBadge,
  renderRiskStateBadge,
} from "../src/components/StatusBadge.js";
import { setupDomMock } from "./dom-mock.js";

describe("@aether/lab — Semantic Status Badges (Text + Visual Glyph)", () => {
  before(() => {
    setupDomMock();
  });

  it("renders RunStatusBadge with text and glyph for all states", () => {
    const satisfied = renderRunStatusBadge("satisfied");
    assert.ok(satisfied.textContent.includes("SATISFIED"));
    assert.ok(satisfied.textContent.includes("✓"));

    const running = renderRunStatusBadge("running");
    assert.ok(running.textContent.includes("RUNNING"));
    assert.ok(running.textContent.includes("⟳"));

    const failed = renderRunStatusBadge("failed");
    assert.ok(failed.textContent.includes("FAILED"));
    assert.ok(failed.textContent.includes("✗"));

    const awaiting = renderRunStatusBadge("awaiting_approval");
    assert.ok(awaiting.textContent.includes("AWAITING APPROVAL"));
    assert.ok(awaiting.textContent.includes("⚠"));
  });

  it("renders ConnectionStatusBadge for all connection states", () => {
    const connected = renderConnectionStatusBadge("connected");
    assert.ok(connected.textContent.includes("CONNECTED"));
    assert.ok(connected.textContent.includes("●"));

    const unavailable = renderConnectionStatusBadge("unavailable");
    assert.ok(unavailable.textContent.includes("UNAVAILABLE"));
    assert.ok(unavailable.textContent.includes("✕"));
  });

  it("renders VerdictBadge correctly", () => {
    const passed = renderVerdictBadge("passed");
    assert.ok(passed.textContent.includes("SATISFIED"));
    assert.ok(passed.textContent.includes("✓"));

    const unverified = renderVerdictBadge(undefined);
    assert.ok(unverified.textContent.includes("UNVERIFIED"));
    assert.ok(unverified.textContent.includes("·"));
  });

  it("renders CapabilityStatusBadge with 4 standard states", () => {
    const avail = renderCapabilityStatusBadge("AVAILABLE");
    assert.ok(avail.textContent.includes("AVAILABLE"));
    assert.ok(avail.textContent.includes("✓"));

    const unavail = renderCapabilityStatusBadge("UNAVAILABLE");
    assert.ok(unavail.textContent.includes("UNAVAILABLE"));
    assert.ok(unavail.textContent.includes("✕"));

    const degraded = renderCapabilityStatusBadge("DEGRADED");
    assert.ok(degraded.textContent.includes("DEGRADED"));
    assert.ok(degraded.textContent.includes("⚠"));

    const incomp = renderCapabilityStatusBadge("INCOMPATIBLE");
    assert.ok(incomp.textContent.includes("INCOMPATIBLE"));
    assert.ok(incomp.textContent.includes("⊘"));
  });

  it("renders EventKindBadge and RiskStateBadge cleanly", () => {
    const effect = renderEventKindBadge("EffectCompleted");
    assert.ok(effect.textContent.includes("EffectCompleted"));

    const risk = renderRiskStateBadge("safe");
    assert.ok(risk.textContent.includes("LOW RISK"));
  });
});
