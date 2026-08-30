import type { DesktopStore } from "../state/desktop-store.js";
import type { RuntimeClient } from "@aether/client";
import { renderApprovalSummary } from "@aether/ui-web";

export function renderApprovalBanner(store: DesktopStore, client?: RuntimeClient): HTMLElement | null {
  const pending = store.get().pendingApproval;
  if (!pending) return null;

  const banner = document.createElement("div");
  banner.className = "aether-approval-banner";
  banner.style.cssText = "margin: 12px 16px; box-sizing: border-box;";

  const summary = renderApprovalSummary({
    approvalId: pending.approvalId,
    action: pending.approvalId,
    diff: pending.unifiedDiff,
    argsDigest: pending.argsDigest,
    descriptorDigest: pending.descriptorDigest,
    expiresAt: pending.expiresAt,
    onApprove: () => {
      if (client) {
        store.resolveApproval(client, "approve");
      } else {
        store.controller.resolveApproval(pending.approvalId, "approve");
      }
    },
    onReject: () => {
      if (client) {
        store.resolveApproval(client, "reject");
      } else {
        store.controller.resolveApproval(pending.approvalId, "reject");
      }
    },
    onInspect: () => {
      store.openForensicDrawer("diffs", pending.unifiedDiff);
    },
    onCancelRun: () => {
      store.cancelRun();
    },
  });

  banner.appendChild(summary);
  return banner;
}
