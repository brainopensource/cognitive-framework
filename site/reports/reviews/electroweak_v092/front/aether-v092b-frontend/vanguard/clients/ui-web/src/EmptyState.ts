export type EmptyStateProps = {
  icon?: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function renderEmptyState(props: EmptyStateProps): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-empty-state";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 32px 16px;
    color: var(--aether-text-muted, #6c7086);
    box-sizing: border-box;
    margin: auto;
  `;

  if (props.icon) {
    const iconEl = document.createElement("div");
    iconEl.style.cssText = "font-size: 32px; margin-bottom: 12px;";
    iconEl.textContent = props.icon;
    container.appendChild(iconEl);
  }

  const titleEl = document.createElement("div");
  titleEl.style.cssText = "font-size: 15px; font-weight: 600; color: var(--aether-text-primary, #cdd6f4); margin-bottom: 6px;";
  titleEl.textContent = props.title;
  container.appendChild(titleEl);

  const descEl = document.createElement("div");
  descEl.style.cssText = "font-size: 13px; max-width: 360px; line-height: 1.4; margin-bottom: 16px;";
  descEl.textContent = props.description;
  container.appendChild(descEl);

  if (props.actionLabel && props.onAction) {
    const btn = document.createElement("button");
    btn.style.cssText = `
      padding: 6px 14px;
      background: var(--aether-accent, #89b4fa);
      color: var(--aether-bg, #11111b);
      border: none;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
    `;
    btn.textContent = props.actionLabel;
    btn.onclick = props.onAction;
    container.appendChild(btn);
  }

  return container;
}
