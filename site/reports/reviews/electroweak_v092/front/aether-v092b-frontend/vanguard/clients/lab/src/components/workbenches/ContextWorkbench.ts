import type { LabStore } from "../../state/lab-store.js";
import { formatSeq, formatTokens, truncateDigest } from "../../util/formatting.js";

export function renderContextWorkbench(store: LabStore): HTMLElement {
  const container = document.createElement("section");
  container.className = "aether-context-workbench";
  container.setAttribute("role", "tabpanel");
  container.setAttribute("aria-label", "Context Composition Workbench");
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
  const snapshot = state.snapshot;
  const events = state.events;

  // Header Title
  const header = document.createElement("div");
  header.style.cssText = "border-bottom: 1px solid var(--lab-border); padding-bottom: 12px;";
  header.innerHTML = `
    <h2 style="margin: 0; font-size: 16px; color: var(--lab-text-primary);">Context Composition & Compaction Inspector</h2>
    <div style="font-size: 12px; color: var(--lab-text-muted); margin-top: 4px;">
      Inspect token contributions, compaction ratios, and committed layer provenance.
    </div>
  `;
  container.appendChild(header);

  // Token Share Visual Bar
  const totalTokens = Math.max(1, snapshot.tokens.totalTokens);
  const inTokens = snapshot.tokens.inTokens || Math.round(totalTokens * 0.75);
  const outTokens = snapshot.tokens.outTokens || Math.round(totalTokens * 0.25);
  const inPct = Math.round((inTokens / totalTokens) * 100);
  const outPct = Math.round((outTokens / totalTokens) * 100);

  const barSection = document.createElement("div");
  barSection.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-md);
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  `;

  barSection.innerHTML = `
    <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 600;">
      <span>Token Share Breakdown</span>
      <span style="font-family: var(--lab-font-mono); color: var(--lab-accent);">Total: ${formatTokens(totalTokens)} tokens</span>
    </div>
    <div style="width: 100%; height: 16px; background: var(--lab-bg-panel); border-radius: 4px; overflow: hidden; display: flex;">
      <div style="width: ${inPct}%; background: var(--lab-accent); title: 'Input Tokens (${inPct}%)';" title="Input: ${formatTokens(inTokens)} (${inPct}%)"></div>
      <div style="width: ${outPct}%; background: var(--lab-pending); title: 'Output Tokens (${outPct}%)';" title="Output: ${formatTokens(outTokens)} (${outPct}%)"></div>
    </div>
    <div style="display: flex; gap: 16px; font-size: 11px; font-family: var(--lab-font-mono);">
      <div style="display: flex; align-items: center; gap: 6px;">
        <span style="width: 10px; height: 10px; background: var(--lab-accent); border-radius: 2px;"></span>
        <span>Input / Prompt Tokens: ${formatTokens(inTokens)} (${inPct}%)</span>
      </div>
      <div style="display: flex; align-items: center; gap: 6px;">
        <span style="width: 10px; height: 10px; background: var(--lab-pending); border-radius: 2px;"></span>
        <span>Output / Generated Tokens: ${formatTokens(outTokens)} (${outPct}%)</span>
      </div>
    </div>
  `;
  container.appendChild(barSection);

  // Committed Context Layers Table
  const layersSection = document.createElement("div");
  layersSection.style.cssText = `
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-md);
    overflow: hidden;
  `;

  const layersTable = document.createElement("table");
  layersTable.style.cssText = "width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;";
  layersTable.innerHTML = `
    <thead>
      <tr style="background: var(--lab-bg-panel); border-bottom: 1px solid var(--lab-border); color: var(--lab-text-secondary); font-size: 11px;">
        <th style="padding: 8px 12px;">LAYER</th>
        <th style="padding: 8px 12px;">STATUS</th>
        <th style="padding: 8px 12px;">EST. CONTRIBUTION</th>
        <th style="padding: 8px 12px;">PROVENANCE</th>
        <th style="padding: 8px 12px; text-align: right;">ACTION</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom: 1px solid var(--lab-border-subtle);">
        <td style="padding: 8px 12px; font-weight: 600;">System & Agent Instructions</td>
        <td style="padding: 8px 12px;"><span style="color: var(--lab-success); font-size: 11px;">✓ Committed</span></td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono);">~1.2k tokens</td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-secondary);">EpisodeStarted</td>
        <td style="padding: 8px 12px; text-align: right;"><button class="btn-inspect-layer" data-layer="system" style="background: none; border: 1px solid var(--lab-border); color: var(--lab-accent); border-radius: 3px; font-size: 11px; padding: 2px 6px; cursor: pointer;">Inspect</button></td>
      </tr>
      <tr style="border-bottom: 1px solid var(--lab-border-subtle);">
        <td style="padding: 8px 12px; font-weight: 600;">Conversation & Episode History</td>
        <td style="padding: 8px 12px;"><span style="color: var(--lab-success); font-size: 11px;">✓ Committed</span></td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono);">${snapshot.turns} turns</td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-secondary);">TurnStarted</td>
        <td style="padding: 8px 12px; text-align: right;"><button class="btn-inspect-layer" data-layer="history" style="background: none; border: 1px solid var(--lab-border); color: var(--lab-accent); border-radius: 3px; font-size: 11px; padding: 2px 6px; cursor: pointer;">Inspect</button></td>
      </tr>
      <tr style="border-bottom: 1px solid var(--lab-border-subtle);">
        <td style="padding: 8px 12px; font-weight: 600;">Tool Definitions & Capabilities</td>
        <td style="padding: 8px 12px;"><span style="color: var(--lab-success); font-size: 11px;">✓ Committed</span></td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono);">${snapshot.tools.length} invocations</td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-secondary);">OperatorInvoked</td>
        <td style="padding: 8px 12px; text-align: right;"><button class="btn-inspect-layer" data-layer="tools" style="background: none; border: 1px solid var(--lab-border); color: var(--lab-accent); border-radius: 3px; font-size: 11px; padding: 2px 6px; cursor: pointer;">Inspect</button></td>
      </tr>
      <tr style="border-bottom: 1px solid var(--lab-border-subtle);">
        <td style="padding: 8px 12px; font-weight: 600;">Retrieved Workspace Spans</td>
        <td style="padding: 8px 12px;"><span style="color: var(--lab-success); font-size: 11px;">✓ Committed</span></td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono);">${snapshot.thoughts.length} observations</td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-secondary);">ObservationProduced</td>
        <td style="padding: 8px 12px; text-align: right;"><button class="btn-inspect-layer" data-layer="spans" style="background: none; border: 1px solid var(--lab-border); color: var(--lab-accent); border-radius: 3px; font-size: 11px; padding: 2px 6px; cursor: pointer;">Inspect</button></td>
      </tr>
      <tr>
        <td style="padding: 8px 12px; font-weight: 600;">Hidden Model Internal State</td>
        <td style="padding: 8px 12px;"><span style="color: var(--lab-text-muted); font-size: 11px;">✕ UNAVAILABLE</span></td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-muted);">-</td>
        <td style="padding: 8px 12px; font-family: var(--lab-font-mono); color: var(--lab-text-muted);">Not in canonical log</td>
        <td style="padding: 8px 12px; text-align: right;"><span style="color: var(--lab-text-muted); font-size: 11px;">Restricted</span></td>
      </tr>
    </tbody>
  `;

  layersSection.appendChild(layersTable);
  container.appendChild(layersSection);

  // Hook inspect buttons
  const buttons = layersTable.querySelectorAll<HTMLButtonElement>(".btn-inspect-layer");
  buttons.forEach((btn) => {
    btn.onclick = () => {
      const layer = btn.getAttribute("data-layer");
      store.selection.selectContextLayer(layer);
    };
  });

  return container;
}
