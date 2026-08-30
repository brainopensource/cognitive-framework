import type { LabStore } from "../../state/lab-store.js";
import type { RuntimeClient } from "@aether/client";
import { formatBytes, truncateDigest } from "../../util/formatting.js";
import { copyToClipboard } from "../../util/clipboard.js";
import { renderJsonPayloadTree } from "../JsonPayloadTree.js";

export function renderArtifactDetailInspector(store: LabStore, client?: RuntimeClient): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-artifact-detail-inspector";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    font-family: var(--lab-font-sans);
    color: var(--lab-text-primary);
  `;

  const sel = store.selection.get();
  const snapshot = store.get().snapshot;
  const evidenceGrid = store.get().evidenceGrid;
  const artifactId = sel.selectedArtifactId;

  const artifact =
    snapshot.artifacts.find((a) => a.digest === artifactId) ||
    evidenceGrid.artifacts.find((a) => a.digest === artifactId);

  if (!artifactId && !artifact) {
    const empty = document.createElement("div");
    empty.style.cssText = "padding: 24px; color: var(--lab-text-muted); text-align: center;";
    empty.textContent = "Select an artifact to inspect its metadata, provenance, and explanation";
    container.appendChild(empty);
    return container;
  }

  const digest = artifact?.digest || artifactId || "";
  const kind = artifact?.kind || "artifact";
  const path = artifact?.path;
  const sizeBytes = artifact && "sizeBytes" in artifact ? (artifact as any).sizeBytes : undefined;

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

  const kindBadge = document.createElement("span");
  kindBadge.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-digest);
    color: var(--lab-digest);
    padding: 2px 6px;
    border-radius: var(--lab-radius-sm);
    font-size: 11px;
    font-family: var(--lab-font-mono);
  `;
  kindBadge.textContent = `📦 ${kind.toUpperCase()}`;
  titleGroup.appendChild(kindBadge);

  const digestEl = document.createElement("span");
  digestEl.style.cssText = "font-family: var(--lab-font-mono); font-size: 12px; font-weight: bold;";
  digestEl.textContent = truncateDigest(digest, 14);
  digestEl.title = digest;
  titleGroup.appendChild(digestEl);

  header.appendChild(titleGroup);

  const copyBtn = document.createElement("button");
  copyBtn.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    color: var(--lab-text-primary);
    border-radius: var(--lab-radius-sm);
    padding: 3px 8px;
    font-size: 11px;
    cursor: pointer;
    font-family: var(--lab-font-mono);
  `;
  copyBtn.textContent = "📋 Copy Digest";
  copyBtn.onclick = () => copyToClipboard(digest);
  header.appendChild(copyBtn);

  container.appendChild(header);

  // Metadata Grid
  const metaGrid = document.createElement("div");
  metaGrid.style.cssText = `
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 8px;
    padding: 10px 12px;
    background: var(--lab-bg-surface);
    border-bottom: 1px solid var(--lab-border);
    font-size: 11px;
    font-family: var(--lab-font-mono);
  `;

  metaGrid.innerHTML = `
    <div><span style="color: var(--lab-text-muted);">Kind:</span> ${kind}</div>
    <div><span style="color: var(--lab-text-muted);">Size:</span> ${formatBytes(sizeBytes)}</div>
    <div><span style="color: var(--lab-text-muted);">Path:</span> ${path || "-"}</div>
    <div><span style="color: var(--lab-text-muted);">Storage:</span> CAS Content-Addressed</div>
  `;
  container.appendChild(metaGrid);

  // Safe Blob Availability Notice
  const notice = document.createElement("div");
  notice.style.cssText = `
    margin: 10px 12px;
    padding: 8px 10px;
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    border-left: 3px solid var(--lab-warning);
    border-radius: var(--lab-radius-sm);
    font-size: 11px;
    color: var(--lab-text-secondary);
  `;
  notice.innerHTML = `
    <strong style="color: var(--lab-warning);">Blob Content Safe Policy:</strong>
    Raw content retrieval is governed by RuntimeService. Internal CAS disk access is strictly prohibited. Explanation and evidence claims are displayed below.
  `;
  container.appendChild(notice);

  // Explanation Section
  const explSection = document.createElement("div");
  explSection.style.cssText = "flex: 1; overflow-y: auto; padding: 10px 12px;";

  const explanation = store.get().artifactExplanations.get(digest);

  if (explanation) {
    const title = document.createElement("h4");
    title.style.cssText = "margin: 0 0 8px 0; font-size: 12px; color: var(--lab-accent);";
    title.textContent = "Runtime Explanation & Provenance";
    explSection.appendChild(title);

    explSection.appendChild(
      renderJsonPayloadTree({
        data: explanation,
        rootName: "explanation",
        defaultExpandedDepth: 2,
        selection: store.selection,
      })
    );
  } else {
    const fetchWrapper = document.createElement("div");
    fetchWrapper.style.cssText = "text-align: center; padding: 20px;";

    const fetchBtn = document.createElement("button");
    fetchBtn.style.cssText = `
      background: var(--lab-accent-muted);
      border: 1px solid var(--lab-accent);
      color: var(--lab-accent);
      border-radius: var(--lab-radius-sm);
      padding: 6px 14px;
      font-size: 12px;
      cursor: pointer;
      font-weight: 600;
    `;
    fetchBtn.textContent = "🔍 Request Explanation from Runtime";
    fetchBtn.onclick = async () => {
      if (client) {
        fetchBtn.textContent = "Loading explanation...";
        await store.explainArtifact(client, digest);
        // Refresh view
        container.innerHTML = "";
        container.appendChild(renderArtifactDetailInspector(store, client));
      }
    };
    fetchWrapper.appendChild(fetchBtn);
    explSection.appendChild(fetchWrapper);
  }

  container.appendChild(explSection);
  return container;
}
