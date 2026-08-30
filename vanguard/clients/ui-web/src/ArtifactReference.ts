export type ArtifactReferenceProps = {
  digest: string;
  path?: string;
  status?: string;
  summary?: string;
  onInspect?: () => void;
  onOpenInLab?: () => void;
};

export function renderArtifactReference(props: ArtifactReferenceProps): HTMLElement {
  const card = document.createElement("div");
  card.className = "aether-artifact-card";
  card.style.cssText = `
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 10px 12px;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 6px;
    margin: 6px 0;
  `;

  const topRow = document.createElement("div");
  topRow.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

  const label = document.createElement("div");
  label.style.cssText = "font-weight: 600; font-size: 13px; color: var(--aether-accent, #89b4fa); font-family: var(--aether-font-mono, monospace);";
  label.textContent = props.path ? `📦 ${props.path}` : `📦 sha256:${props.digest.slice(0, 16)}…`;
  topRow.appendChild(label);

  const actions = document.createElement("div");
  actions.style.cssText = "display: flex; gap: 6px;";

  if (props.onInspect) {
    const inspectBtn = document.createElement("button");
    inspectBtn.style.cssText = `
      background: var(--aether-surface-raised, #252538);
      border: 1px solid var(--aether-border, #313244);
      color: var(--aether-text-primary, #cdd6f4);
      border-radius: 4px;
      padding: 2px 6px;
      font-size: 11px;
      cursor: pointer;
    `;
    inspectBtn.textContent = "Explain";
    inspectBtn.onclick = props.onInspect;
    actions.appendChild(inspectBtn);
  }

  if (props.onOpenInLab) {
    const labBtn = document.createElement("button");
    labBtn.style.cssText = `
      background: var(--aether-surface-raised, #252538);
      border: 1px solid var(--aether-border, #313244);
      color: var(--aether-info, #89dceb);
      border-radius: 4px;
      padding: 2px 6px;
      font-size: 11px;
      cursor: pointer;
    `;
    labBtn.textContent = "Open in Lab ↗";
    labBtn.onclick = props.onOpenInLab;
    actions.appendChild(labBtn);
  }

  topRow.appendChild(actions);
  card.appendChild(topRow);

  if (props.summary) {
    const summaryEl = document.createElement("div");
    summaryEl.style.cssText = "font-size: 12px; color: var(--aether-text-muted, #6c7086);";
    summaryEl.textContent = props.summary;
    card.appendChild(summaryEl);
  }

  return card;
}
