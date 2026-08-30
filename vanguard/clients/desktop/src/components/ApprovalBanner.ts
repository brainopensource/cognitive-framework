import type { DesktopStore } from "../state/desktop-store.js";
import type { RuntimeClient } from "@aether/client";

export function renderApprovalBanner(store: DesktopStore, client?: RuntimeClient): HTMLElement | null {
  const pending = store.get().pendingApproval;
  if (!pending) return null;

  const banner = document.createElement("div");
  banner.className = "aether-approval-banner";
  banner.style.cssText = `
    margin: 12px 16px;
    padding: 12px 16px;
    background: var(--aether-bg-card);
    border: 1px solid var(--aether-warning);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  `;

  // Title
  const header = document.createElement("div");
  header.style.cssText = "font-weight: 600; color: var(--aether-warning); font-size: 14px;";
  header.textContent = `⚠ APPROVAL REQUIRED: Action '${pending.approvalId}'`;
  banner.appendChild(header);

  // Digest details
  if (pending.argsDigest) {
    const digests = document.createElement("div");
    digests.style.cssText = "font-size: 12px; color: var(--aether-text-muted); font-family: var(--aether-font-mono);";
    digests.textContent = `Args Digest: ${pending.argsDigest.slice(0, 24)}…`;
    banner.appendChild(digests);
  }

  // Action Buttons
  const buttons = document.createElement("div");
  buttons.style.cssText = "display: flex; gap: 8px; margin-top: 4px;";

  const approveBtn = document.createElement("button");
  approveBtn.style.cssText = "padding: 6px 12px; background: var(--aether-success); color: var(--aether-bg); border: none; border-radius: 4px; font-weight: 600; cursor: pointer;";
  approveBtn.textContent = "✔ Approve & Sign (Ed25519)";
  approveBtn.onclick = () => {
    if (client) store.resolveApproval(client, "approve");
  };
  buttons.appendChild(approveBtn);

  if (pending.unifiedDiff) {
    const diffBtn = document.createElement("button");
    diffBtn.style.cssText = "padding: 6px 12px; background: var(--aether-bg-card-hover); color: var(--aether-text-primary); border: 1px solid var(--aether-border); border-radius: 4px; cursor: pointer;";
    diffBtn.textContent = "🔍 View Full Diff";
    diffBtn.onclick = () => store.openForensicDrawer("diffs", pending.unifiedDiff);
    buttons.appendChild(diffBtn);
  }

  const rejectBtn = document.createElement("button");
  rejectBtn.style.cssText = "padding: 6px 12px; background: var(--aether-danger); color: var(--aether-bg); border: none; border-radius: 4px; font-weight: 600; cursor: pointer;";
  rejectBtn.textContent = "✖ Reject";
  rejectBtn.onclick = () => {
    if (client) store.resolveApproval(client, "reject");
  };
  buttons.appendChild(rejectBtn);

  banner.appendChild(buttons);
  return banner;
}
