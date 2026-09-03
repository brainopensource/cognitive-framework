import type { LabStore } from "../../state/lab-store.js";
import { formatTokens } from "../../util/formatting.js";

export function renderContextLayerInspector(store: LabStore): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-context-layer-inspector";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
    font-family: var(--lab-font-sans);
    color: var(--lab-text-primary);
    padding: 12px;
  `;

  const sel = store.selection.get();
  const layerName = sel.selectedContextLayer || "all";
  const snapshot = store.get().snapshot;

  const header = document.createElement("div");
  header.style.cssText = "margin-bottom: 12px; border-bottom: 1px solid var(--lab-border); padding-bottom: 8px;";
  header.innerHTML = `
    <h3 style="margin: 0; font-size: 14px; color: var(--lab-accent);">Context Composition Inspector</h3>
    <div style="font-size: 11px; color: var(--lab-text-muted); margin-top: 4px;">Committed context layers and compaction transitions</div>
  `;
  container.appendChild(header);

  const statsGrid = document.createElement("div");
  statsGrid.style.cssText = `
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 16px;
    font-family: var(--lab-font-mono);
    font-size: 12px;
  `;
  statsGrid.innerHTML = `
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">TOTAL TOKENS</div>
      <div style="color: var(--lab-accent); font-weight: bold; font-size: 16px;">${formatTokens(snapshot.tokens.totalTokens)}</div>
    </div>
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">INPUT TOKENS</div>
      <div style="color: var(--lab-text-primary); font-weight: bold; font-size: 16px;">${formatTokens(snapshot.tokens.inTokens)}</div>
    </div>
    <div style="background: var(--lab-bg-panel); padding: 8px; border-radius: var(--lab-radius-sm); border: 1px solid var(--lab-border);">
      <div style="color: var(--lab-text-muted); font-size: 10px;">OUTPUT TOKENS</div>
      <div style="color: var(--lab-text-primary); font-weight: bold; font-size: 16px;">${formatTokens(snapshot.tokens.outTokens)}</div>
    </div>
  `;
  container.appendChild(statsGrid);

  const policyBox = document.createElement("div");
  policyBox.style.cssText = `
    padding: 8px 10px;
    background: var(--lab-bg-surface);
    border: 1px solid var(--lab-border);
    border-radius: var(--lab-radius-sm);
    font-size: 11px;
    color: var(--lab-text-secondary);
    line-height: 1.4;
  `;
  policyBox.innerHTML = `
    <strong style="color: var(--lab-text-primary);">AETHER Epistemic Honesty:</strong>
    Context composition is projected strictly from committed canonical events. Unrecorded model weights and invisible system prompts are never fabricated or simulated.
  `;
  container.appendChild(policyBox);

  return container;
}
