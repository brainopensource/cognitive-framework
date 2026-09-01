import type { LabStore } from "../../state/lab-store.js";
import type { RuntimeClient } from "@aether/client";
import { formatTimestamp, truncateDigest } from "../../util/formatting.js";
import { copyToClipboard } from "../../util/clipboard.js";
import { renderApprovalStatusBadge } from "../StatusBadge.js";

export function renderApprovalInspector(store: LabStore, client?: RuntimeClient): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-approval-inspector";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    font-family: var(--lab-font-sans);
    color: var(--lab-text-primary);
  `;

  const sel = store.selection.get();
  const approvalState = store.get().approvalState;

  // Look for approval record either in pending or resolved
  const pendingRecord = sel.selectedApprovalId
    ? approvalState.pendingChallenges.get(sel.selectedApprovalId)
    : Array.from(approvalState.pendingChallenges.values())[0];

  const resolvedRecord = sel.selectedApprovalId
    ? approvalState.resolvedApprovals.find((r) => r.challenge.approvalId === sel.selectedApprovalId)
    : undefined;

  const record = pendingRecord || resolvedRecord;

  if (!record) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding: 24px; color: var(--lab-text-muted); text-align: center;";
    empty.textContent = "No approval challenge selected or pending for this run";
    container.appendChild(empty);
    return container;
  }

  const { challenge, status, requestedAt, resolvedAt, decision } = record;

  // Header
  const header = document.createElement("div");
  header.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--lab-bg-panel);
    border-bottom: 1px solid var(--lab-border);
  `;

  const titleGroup = document.createElement("div");
  titleGroup.style.cssText = "display: flex; align-items: center; gap: 8px;";
  titleGroup.appendChild(renderApprovalStatusBadge(status));

  const idEl = document.createElement("span");
  idEl.style.cssText = "font-family: var(--lab-font-mono); font-weight: bold; font-size: 12px;";
  idEl.textContent = challenge.approvalId;
  titleGroup.appendChild(idEl);

  header.appendChild(titleGroup);

  if (status === "pending" && client) {
    const actions = document.createElement("div");
    actions.style.cssText = "display: flex; gap: 6px;";

    const approveBtn = document.createElement("button");
    approveBtn.style.cssText = `
      background: var(--lab-success-bg);
      border: 1px solid var(--lab-success);
      color: var(--lab-success);
      border-radius: var(--lab-radius-sm);
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
    `;
    approveBtn.textContent = "✓ Approve";
    approveBtn.onclick = () => store.resolveApproval(client, challenge.approvalId, "approved");
    actions.appendChild(approveBtn);

    const rejectBtn = document.createElement("button");
    rejectBtn.style.cssText = `
      background: var(--lab-danger-bg);
      border: 1px solid var(--lab-danger);
      color: var(--lab-danger);
      border-radius: var(--lab-radius-sm);
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
    `;
    rejectBtn.textContent = "✕ Reject";
    rejectBtn.onclick = () => store.resolveApproval(client, challenge.approvalId, "rejected");
    actions.appendChild(rejectBtn);

    header.appendChild(actions);
  }

  container.appendChild(header);

  // Metadata Grid
  const metaGrid = document.createElement("div");
  metaGrid.style.cssText = `
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 8px;
    padding: 10px 12px;
    background: var(--lab-bg-surface);
    border-bottom: 1px solid var(--lab-border);
    font-size: 11px;
    font-family: var(--lab-font-mono);
  `;

  metaGrid.innerHTML = `
    <div><span style="color: var(--lab-text-muted);">Action:</span> ${challenge.action || "edit_file"}</div>
    <div><span style="color: var(--lab-text-muted);">Principal:</span> ${challenge.principal}</div>
    <div><span style="color: var(--lab-text-muted);">Requested:</span> ${formatTimestamp(requestedAt)}</div>
    <div><span style="color: var(--lab-text-muted);">Resolved:</span> ${formatTimestamp(resolvedAt)}</div>
    <div><span style="color: var(--lab-text-muted);">Args Digest:</span> <span title="${challenge.argsDigest}">${truncateDigest(challenge.argsDigest, 8)}</span></div>
    <div><span style="color: var(--lab-text-muted);">Descriptor:</span> <span title="${challenge.descriptorDigest}">${truncateDigest(challenge.descriptorDigest, 8)}</span></div>
  `;
  container.appendChild(metaGrid);

  // Diff Section
  const diffSection = document.createElement("div");
  diffSection.style.cssText = "flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 10px 12px;";

  const diffHeader = document.createElement("div");
  diffHeader.style.cssText = "display: flex; justify-content: space-between; margin-bottom: 6px;";
  diffHeader.innerHTML = `<span style="font-size: 12px; font-weight: 600;">Proposed Diff / Patch</span>`;

  const copyDiffBtn = document.createElement("button");
  copyDiffBtn.style.cssText = "background: none; border: none; color: var(--lab-text-muted); cursor: pointer; font-size: 11px;";
  copyDiffBtn.textContent = "📋 Copy Diff";
  copyDiffBtn.onclick = () => copyToClipboard(challenge.normalizedDiff);
  diffHeader.appendChild(copyDiffBtn);
  diffSection.appendChild(diffHeader);

  const diffViewer = document.createElement("div");
  diffViewer.className = "aether-diff-viewer";
  diffViewer.style.cssText = `
    flex: 1;
    overflow: auto;
    background: var(--lab-bg-panel);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-sm);
    padding: 8px;
    font-family: var(--lab-font-mono);
    font-size: 11px;
    line-height: 1.4;
    white-space: pre-wrap;
  `;

  if (!challenge.normalizedDiff) {
    diffViewer.textContent = "No unified diff attached to this challenge.";
    diffViewer.style.color = "var(--lab-text-muted)";
  } else {
    const lines = challenge.normalizedDiff.split("\n");
    for (const line of lines) {
      const lineEl = document.createElement("div");
      if (line.startsWith("+") && !line.startsWith("+++")) {
        lineEl.style.cssText = "background: var(--lab-diff-add-bg); color: var(--lab-diff-add-fg); padding: 0 4px;";
      } else if (line.startsWith("-") && !line.startsWith("---")) {
        lineEl.style.cssText = "background: var(--lab-diff-del-bg); color: var(--lab-diff-del-fg); padding: 0 4px;";
      } else if (line.startsWith("@@")) {
        lineEl.style.cssText = "color: var(--lab-accent); padding: 0 4px; font-weight: bold;";
      } else {
        lineEl.style.cssText = "color: var(--lab-text-secondary); padding: 0 4px;";
      }
      lineEl.textContent = line || " ";
      diffViewer.appendChild(lineEl);
    }
  }

  diffSection.appendChild(diffViewer);
  container.appendChild(diffSection);

  return container;
}
