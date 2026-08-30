import type { LabStore } from "../../state/lab-store.js";
import type { RuntimeClient } from "@aether/client";
import { renderCapabilityStatusBadge, renderConnectionStatusBadge } from "../StatusBadge.js";
import { formatTimestamp } from "../../util/formatting.js";

export function renderSystemWorkbench(store: LabStore, client?: RuntimeClient): HTMLElement {
  const container = document.createElement("section");
  container.className = "aether-system-workbench";
  container.setAttribute("role", "tabpanel");
  container.setAttribute("aria-label", "System & Capabilities Workbench");
  container.style.cssText = `
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    padding: 16px;
    background: var(--lab-bg);
    gap: 16px;
  `;

  const state = store.get();

  // Header Title
  const header = document.createElement("div");
  header.style.cssText = "display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--lab-border); padding-bottom: 12px;";

  const titleGroup = document.createElement("div");
  titleGroup.innerHTML = `
    <h2 style="margin: 0; font-size: 16px; color: var(--lab-text-primary);">Runtime System & Capabilities</h2>
    <div style="font-size: 12px; color: var(--lab-text-muted); margin-top: 4px;">
      Canonical protocol version vg.4, capability negotiation, and stream health diagnostics.
    </div>
  `;
  header.appendChild(titleGroup);

  if (client) {
    const recheckBtn = document.createElement("button");
    recheckBtn.style.cssText = `
      background: var(--lab-accent-muted);
      border: 1px solid var(--lab-accent);
      color: var(--lab-accent);
      padding: 4px 10px;
      border-radius: var(--lab-radius-sm);
      font-size: 12px;
      cursor: pointer;
      font-weight: 600;
    `;
    recheckBtn.textContent = "🔍 Probe Capabilities";
    recheckBtn.onclick = async () => {
      recheckBtn.textContent = "Probing...";
      await store.checkSystemCapabilities(client);
      refreshWorkbench();
    };
    header.appendChild(recheckBtn);
  }

  container.appendChild(header);

  // System Facts Grid
  const factsGrid = document.createElement("div");
  factsGrid.style.cssText = `
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 10px;
    font-size: 12px;
  `;

  const facts = [
    { label: "PROTOCOL VERSION", value: "vg.4 (AETHER Canonical)", color: "var(--lab-accent)" },
    { label: "CONNECTION STATE", value: state.connectionState.toUpperCase(), badge: renderConnectionStatusBadge(state.connectionState) },
    { label: "ACTIVE TRANSPORT", value: `${state.transportType.toUpperCase()} (${state.socketPathOrUrl})` },
    { label: "DAEMON STATUS", value: state.daemonStatus ? `${state.daemonStatus.status.toUpperCase()} (PID ${state.daemonStatus.pid ?? "-"})` : "UNCHECKED" },
    { label: "STREAM TOTAL FRAMES", value: `${state.events.length} frames recorded` },
    { label: "CLIENT COMPLIANCE", value: "100% Shared Substrate (@aether/*)" },
  ];

  for (const f of facts) {
    const card = document.createElement("div");
    card.style.cssText = `
      background: var(--lab-bg-surface);
      border: 1px solid var(--lab-border);
      border-radius: var(--lab-radius-sm);
      padding: 10px 12px;
    `;
    card.innerHTML = `
      <div style="font-size: 10px; color: var(--lab-text-muted); font-family: var(--lab-font-mono);">${f.label}</div>
      <div style="font-size: 13px; font-weight: 600; color: ${f.color || "var(--lab-text-primary)"}; margin-top: 4px; display: flex; align-items: center; gap: 6px;">
        ${f.value}
      </div>
    `;
    if (f.badge) {
      card.children[1]?.appendChild(f.badge);
    }
    factsGrid.appendChild(card);
  }
  container.appendChild(factsGrid);

  // Feature Availability Matrix
  const matrixSection = document.createElement("div");
  matrixSection.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-md);
    overflow: hidden;
  `;

  const matrixHeader = document.createElement("div");
  matrixHeader.style.cssText = "padding: 10px 14px; background: var(--lab-bg-panel); border-bottom: 1px solid var(--lab-border); font-size: 12px; font-weight: 600;";
  matrixHeader.textContent = "Negotiated Frontend Surface Capabilities";
  matrixSection.appendChild(matrixHeader);

  const matrixTable = document.createElement("table");
  matrixTable.style.cssText = "width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;";
  matrixTable.innerHTML = `
    <thead>
      <tr style="background: var(--lab-bg-surface); border-bottom: 1px solid var(--lab-border); color: var(--lab-text-secondary); font-size: 11px;">
        <th style="padding: 8px 12px;">FEATURE / OPERATION</th>
        <th style="padding: 8px 12px;">STATUS</th>
        <th style="padding: 8px 12px;">RATIONALE / POLICY</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid var(--lab-border-subtle);">
        <td style="padding: 8px 12px; font-weight: 600;">Live Event Tail</td>
        <td style="padding: 8px 12px;"></td>
        <td style="padding: 8px 12px; color: var(--lab-text-secondary);">Real-time stream consumption through streamEvents() port</td>
      </tr>
      <tr style="border-bottom: 1px solid var(--lab-border-subtle);">
        <td style="padding: 8px 12px; font-weight: 600;">Deterministic Event Replay</td>
        <td style="padding: 8px 12px;"></td>
        <td style="padding: 8px 12px; color: var(--lab-text-secondary);">Step-by-step projection scrubbing over recorded trajectories</td>
      </tr>
      <tr style="border-bottom: 1px solid var(--lab-border-subtle);">
        <td style="padding: 8px 12px; font-weight: 600;">Forensic Payload Inspection</td>
        <td style="padding: 8px 12px;"></td>
        <td style="padding: 8px 12px; color: var(--lab-text-secondary);">Lazy object trees, cryptographic digest pills, and causal links</td>
      </tr>
      <tr style="border-bottom: 1px solid var(--lab-border-subtle);">
        <td style="padding: 8px 12px; font-weight: 600;">Artifact Explanation</td>
        <td style="padding: 8px 12px;"></td>
        <td style="padding: 8px 12px; color: var(--lab-text-secondary);">RuntimeService explainArtifact() capability</td>
      </tr>
      <tr>
        <td style="padding: 8px 12px; font-weight: 600;">Direct Kernel / DB Mutation</td>
        <td style="padding: 8px 12px;"></td>
        <td style="padding: 8px 12px; color: var(--lab-text-secondary);">Lab is an immutable inspection surface; mutations are restricted</td>
      </tr>
    </tbody>
  `;

  const rows = matrixTable.querySelectorAll("tbody tr");
  if (rows[0]) rows[0].children[1]?.appendChild(renderCapabilityStatusBadge(state.featureStatus["LiveTail"] || "AVAILABLE"));
  if (rows[1]) rows[1].children[1]?.appendChild(renderCapabilityStatusBadge(state.featureStatus["Replay"] || "AVAILABLE"));
  if (rows[2]) rows[2].children[1]?.appendChild(renderCapabilityStatusBadge(state.featureStatus["Forensics"] || "AVAILABLE"));
  if (rows[3]) rows[3].children[1]?.appendChild(renderCapabilityStatusBadge(state.featureStatus["ArtifactExplanation"] || "AVAILABLE"));
  if (rows[4]) rows[4].children[1]?.appendChild(renderCapabilityStatusBadge(state.featureStatus["DirectMutation"] || "UNAVAILABLE"));

  matrixSection.appendChild(matrixTable);
  container.appendChild(matrixSection);

  function refreshWorkbench() {
    const parent = container.parentNode;
    if (parent) {
      const fresh = renderSystemWorkbench(store, client);
      parent.replaceChild(fresh, container);
    }
  }

  return container;
}
