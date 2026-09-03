export type LoadingStateProps = {
  message?: string;
  size?: "sm" | "md" | "lg";
};

export function renderLoadingState(props: LoadingStateProps = {}): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-loading-state";
  container.style.cssText = `
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 16px;
    color: var(--aether-text-muted, #6c7086);
    font-size: 13px;
  `;

  const spinner = document.createElement("div");
  const sizePx = props.size === "sm" ? "14px" : props.size === "lg" ? "24px" : "18px";
  spinner.style.cssText = `
    width: ${sizePx};
    height: ${sizePx};
    border: 2px solid var(--aether-border, #313244);
    border-top-color: var(--aether-accent, #89b4fa);
    border-radius: 50%;
    animation: aether-spin 0.8s linear infinite;
  `;

  container.appendChild(spinner);

  if (props.message) {
    const text = document.createElement("span");
    text.textContent = props.message;
    container.appendChild(text);
  }

  return container;
}
