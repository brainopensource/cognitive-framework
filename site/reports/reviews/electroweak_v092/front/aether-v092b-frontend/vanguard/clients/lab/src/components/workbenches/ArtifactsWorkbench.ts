import type { LabStore } from "../../state/lab-store.js";
import type { RuntimeClient } from "@aether/client";
import { formatBytes, formatTimestamp, truncateDigest } from "../../util/formatting.js";
import { renderVerdictBadge } from "../StatusBadge.js";
import { renderSearchInput } from "../SearchInput.js";

export function renderArtifactsWorkbench(store: LabStore, client?: RuntimeClient): HTMLElement {
  const container = document.createElement("section");
  container.className = "aether-artifacts-workbench";
  container.setAttribute("role", "tabpanel");
  container.setAttribute("aria-label", "Artifacts & Evidence Workbench");
  container.style.cssText = `
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    background: var(--lab-bg);
  `;

  const state = store.get();
  const snapshot = state.snapshot;
  const evidenceGrid = state.evidenceGrid;

  let activeSubTab: string = "inventory";

  // Top Toolbar & Tab Selector
  const toolbar = document.createElement("div");
  toolbar.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    background: var(--lab-bg-surface);
    border-bottom: 1px solid var(--lab-border);
  `;

  const tabGroup = document.createElement("div");
  tabGroup.style.cssText = "display: flex; gap: 4px;";

  const invTabBtn = document.createElement("button");
  invTabBtn.style.cssText = `
    background: ${activeSubTab === "inventory" ? "var(--lab-bg-panel)" : "transparent"};
    color: ${activeSubTab === "inventory" ? "var(--lab-accent)" : "var(--lab-text-secondary)"};
    border: 1px solid ${activeSubTab === "inventory" ? "var(--lab-border)" : "transparent"};
    padding: 4px 10px;
    border-radius: var(--lab-radius-sm);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  `;
  invTabBtn.textContent = `📦 Artifacts (${snapshot.artifacts.length})`;
  tabGroup.appendChild(invTabBtn);

  const evTabBtn = document.createElement("button");
  evTabBtn.style.cssText = `
    background: ${activeSubTab === "evidence" ? "var(--lab-bg-panel)" : "transparent"};
    color: ${activeSubTab === "evidence" ? "var(--lab-accent)" : "var(--lab-text-secondary)"};
    border: 1px solid ${activeSubTab === "evidence" ? "var(--lab-border)" : "transparent"};
    padding: 4px 10px;
    border-radius: var(--lab-radius-sm);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  `;
  evTabBtn.textContent = `⚖ Research Evidence Claims (${evidenceGrid.claims.length})`;
  tabGroup.appendChild(evTabBtn);

  toolbar.appendChild(tabGroup);
  container.appendChild(toolbar);

  // Content Container
  const contentArea = document.createElement("div");
  contentArea.style.cssText = "flex: 1; overflow-y: auto; padding: 16px;";

  function renderSubView() {
    contentArea.innerHTML = "";

    if (activeSubTab === "inventory") {
      // 1. Artifacts Inventory View
      if (snapshot.artifacts.length === 0) {
        const empty = document.createElement("div");
        empty.style.cssText = "padding: 32px; text-align: center; color: var(--lab-text-muted); font-size: 13px;";
        empty.textContent = "No artifacts projected for this run.";
        contentArea.appendChild(empty);
        return;
      }

      const tableWrapper = document.createElement("div");
      tableWrapper.style.cssText = "background: var(--lab-bg-surface); border: 1px solid var(--lab-border); border-radius: var(--lab-radius-md); overflow: hidden;";

      const table = document.createElement("table");
      table.style.cssText = "width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;";
      const thead = document.createElement("thead");
      thead.innerHTML = `
        <tr style="background: var(--lab-bg-panel); border-bottom: 1px solid var(--lab-border); color: var(--lab-text-secondary); font-size: 11px;">
          <th style="padding: 8px 12px;">DIGEST</th>
          <th style="padding: 8px 12px;">KIND</th>
          <th style="padding: 8px 12px;">PATH</th>
          <th style="padding: 8px 12px;">SIZE</th>
          <th style="padding: 8px 12px; text-align: right;">ACTION</th>
        </tr>
      `;
      table.appendChild(thead);

      const tbody = document.createElement("tbody");
      tbody.className = "aether-artifacts-tbody";
      table.appendChild(tbody);

      for (const art of snapshot.artifacts) {
        const tr = document.createElement("tr");
        tr.style.cssText = "border-bottom: 1px solid var(--lab-border-subtle); cursor: pointer;";
        tr.onmouseenter = () => (tr.style.background = "var(--lab-bg-hover)");
        tr.onmouseleave = () => (tr.style.background = "transparent");

        const tdDigest = document.createElement("td");
        tdDigest.style.cssText = "padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-digest); font-weight: 600;";
        tdDigest.textContent = truncateDigest(art.digest, 14);
        tdDigest.title = art.digest;
        tr.appendChild(tdDigest);

        const tdKind = document.createElement("td");
        tdKind.style.cssText = "padding: 8px 12px; font-family: var(--lab-font-mono);";
        tdKind.textContent = art.kind;
        tr.appendChild(tdKind);

        const tdPath = document.createElement("td");
        tdPath.style.cssText = "padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-secondary);";
        tdPath.textContent = art.path || "-";
        tr.appendChild(tdPath);

        const tdSize = document.createElement("td");
        tdSize.style.cssText = "padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-muted);";
        tdSize.textContent = formatBytes(art.sizeBytes);
        tr.appendChild(tdSize);

        const tdAct = document.createElement("td");
        tdAct.style.cssText = "padding: 8px 12px; text-align: right;";

        const btn = document.createElement("button");
        btn.style.cssText = "background: var(--lab-accent-muted); border: 1px solid var(--lab-accent); color: var(--lab-accent); border-radius: 3px; padding: 2px 8px; font-size: 11px; cursor: pointer;";
        btn.textContent = "Inspect ↗";
        btn.onclick = (e) => {
          e.stopPropagation();
          store.selection.selectArtifact(art.digest);
        };
        tdAct.appendChild(btn);
        tr.appendChild(tdAct);

        tr.onclick = () => {
          store.selection.selectArtifact(art.digest);
        };

        tbody.appendChild(tr);
      }

      tableWrapper.appendChild(table);
      contentArea.appendChild(tableWrapper);
    } else {
      // 2. Research Evidence Claims View
      if (evidenceGrid.claims.length === 0) {
        const empty = document.createElement("div");
        empty.style.cssText = "padding: 32px; text-align: center; color: var(--lab-text-muted); font-size: 13px;";
        empty.textContent = "No research evidence claims recorded for this run.";
        contentArea.appendChild(empty);
        return;
      }

      const grid = document.createElement("div");
      grid.style.cssText = "display: flex; flex-direction: column; gap: 8px;";

      for (const claim of evidenceGrid.claims) {
        const card = document.createElement("div");
        const isVerified = claim.status === "verified";
        card.style.cssText = `
          background: var(--lab-bg-surface);
          border: 1px solid ${isVerified ? "var(--lab-border)" : "var(--lab-warning)"};
          border-left: 3px solid ${isVerified ? "var(--lab-success)" : "var(--lab-warning)"};
          border-radius: var(--lab-radius-sm);
          padding: 10px 12px;
          display: flex;
          flex-direction: column;
          gap: 6px;
        `;

        const cardHeader = document.createElement("div");
        cardHeader.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

        const leftHeader = document.createElement("div");
        leftHeader.style.cssText = "display: flex; align-items: center; gap: 8px;";

        const statusBadge = document.createElement("span");
        statusBadge.style.cssText = `
          padding: 1px 5px;
          border-radius: 3px;
          font-size: 10px;
          font-family: var(--lab-font-mono);
          font-weight: bold;
          background: ${isVerified ? "var(--lab-success-bg)" : "var(--lab-warning-bg)"};
          color: ${isVerified ? "var(--lab-success)" : "var(--lab-warning)"};
        `;
        statusBadge.textContent = isVerified ? "✓ VERIFIED" : "⚠ UNVERIFIED CLAIM";
        leftHeader.appendChild(statusBadge);

        const typeBadge = document.createElement("span");
        typeBadge.style.cssText = "color: var(--lab-text-muted); font-size: 11px; font-family: var(--lab-font-mono);";
        typeBadge.textContent = `Type: ${claim.claimType}`;
        leftHeader.appendChild(typeBadge);

        cardHeader.appendChild(leftHeader);

        const eventLink = document.createElement("button");
        eventLink.style.cssText = "background: none; border: 1px solid var(--lab-border); color: var(--lab-accent); border-radius: 3px; font-size: 10px; padding: 2px 6px; cursor: pointer;";
        eventLink.textContent = `↗ Source Event (${truncateDigest(claim.sourceEventId, 6)})`;
        eventLink.onclick = () => {
          store.selection.setWorkbench("events");
          store.selection.selectEvent(claim.sourceEventId);
        };
        cardHeader.appendChild(eventLink);

        card.appendChild(cardHeader);

        const stmt = document.createElement("div");
        stmt.style.cssText = "font-size: 12px; color: var(--lab-text-primary); line-height: 1.4;";
        stmt.textContent = claim.statement;
        card.appendChild(stmt);

        if (claim.artifactId) {
          const artLink = document.createElement("div");
          artLink.style.cssText = "font-size: 11px; color: var(--lab-digest); font-family: var(--lab-font-mono); cursor: pointer;";
          artLink.textContent = `📦 Linked Artifact: ${truncateDigest(claim.artifactId, 12)}`;
          artLink.onclick = () => {
            store.selection.selectArtifact(claim.artifactId!);
          };
          card.appendChild(artLink);
        }

        grid.appendChild(card);
      }

      contentArea.appendChild(grid);
    }
  }

  invTabBtn.onclick = () => {
    activeSubTab = "inventory";
    invTabBtn.style.background = "var(--lab-bg-panel)";
    invTabBtn.style.color = "var(--lab-accent)";
    invTabBtn.style.borderColor = "var(--lab-border)";
    evTabBtn.style.background = "transparent";
    evTabBtn.style.color = "var(--lab-text-secondary)";
    evTabBtn.style.borderColor = "transparent";
    renderSubView();
  };

  evTabBtn.onclick = () => {
    activeSubTab = "evidence";
    evTabBtn.style.background = "var(--lab-bg-panel)";
    evTabBtn.style.color = "var(--lab-accent)";
    evTabBtn.style.borderColor = "var(--lab-border)";
    invTabBtn.style.background = "transparent";
    invTabBtn.style.color = "var(--lab-text-secondary)";
    invTabBtn.style.borderColor = "transparent";
    renderSubView();
  };

  renderSubView();
  container.appendChild(contentArea);

  return container;
}
