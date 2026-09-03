import type { ModelProviderConfig, ProviderType } from "@aether/contracts";
import { renderStatusBadge } from "./StatusBadge.js";

export type ProviderManagerProps = {
  providers: ModelProviderConfig[];
  selectedProviderId: string;
  onSelectDefault: (id: string) => void;
  onSelectModel: (providerId: string, modelId: string) => void;
  onAddProvider: (provider: Omit<ModelProviderConfig, "id">) => void;
  onRemoveProvider: (id: string) => void;
  onUpdateCredential: (providerId: string, secret: string) => void;
  onValidateProvider: (providerId: string) => void;
};

export function renderProviderManager(props: ProviderManagerProps): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-provider-manager";
  container.style.cssText = "display: flex; flex-direction: column; gap: 16px; font-size: 13px;";

  const header = document.createElement("div");
  header.style.cssText = "display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--aether-border, #313244); padding-bottom: 8px;";
  header.innerHTML = `
    <div>
      <div style="font-weight: 700; color: var(--aether-text-primary, #cdd6f4); font-size: 14px;">Model Providers</div>
      <div style="font-size: 11px; color: var(--aether-text-muted, #6c7086);">Configure local (Ollama) and cloud model endpoints</div>
    </div>
  `;
  container.appendChild(header);

  // Provider List
  const list = document.createElement("div");
  list.style.cssText = "display: flex; flex-direction: column; gap: 10px;";

  for (const p of props.providers) {
    const card = document.createElement("div");
    const isSelected = p.id === props.selectedProviderId;
    card.style.cssText = `
      padding: 12px;
      border-radius: 6px;
      background: ${isSelected ? "var(--aether-surface-raised, #252538)" : "var(--aether-surface, #181825)"};
      border: 1px solid ${isSelected ? "var(--aether-accent, #89b4fa)" : "var(--aether-border, #313244)"};
      display: flex;
      flex-direction: column;
      gap: 8px;
    `;

    const topRow = document.createElement("div");
    topRow.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

    const nameSpan = document.createElement("div");
    nameSpan.style.cssText = "font-weight: 700; display: flex; align-items: center; gap: 8px;";
    nameSpan.innerHTML = `<span>${p.name}</span><span style="font-size: 10px; color: var(--aether-text-muted, #6c7086); font-weight: normal;">(${p.type})</span>`;
    topRow.appendChild(nameSpan);

    const credBadge = renderStatusBadge({
      status: p.credentialState === "CONFIGURED" ? "valid" : p.credentialState === "INVALID" ? "invalid" : "unverified",
      size: "sm",
    });
    topRow.appendChild(credBadge);
    card.appendChild(topRow);

    // Model Selector
    const modelRow = document.createElement("div");
    modelRow.style.cssText = "display: flex; align-items: center; gap: 8px; font-size: 12px;";
    modelRow.innerHTML = `<label style="color: var(--aether-text-muted, #6c7086); width: 60px;">Model:</label>`;

    const select = document.createElement("select");
    select.style.cssText = "flex: 1; padding: 4px 6px; background: var(--aether-bg, #11111b); border: 1px solid var(--aether-border, #313244); color: var(--aether-text-primary, #cdd6f4); border-radius: 4px;";
    for (const m of p.models) {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = m.name;
      if (m.id === p.selectedModel) opt.selected = true;
      select.appendChild(opt);
    }
    select.onchange = () => props.onSelectModel(p.id, select.value);
    modelRow.appendChild(select);
    card.appendChild(modelRow);

    // Credential Row
    if (p.type !== "ollama") {
      const credRow = document.createElement("div");
      credRow.style.cssText = "display: flex; align-items: center; gap: 8px;";

      const keyInput = document.createElement("input");
      keyInput.type = "password";
      keyInput.placeholder = p.credentialState === "CONFIGURED" ? "••••••••••••••••" : "Enter API Key...";
      keyInput.style.cssText = "flex: 1; padding: 4px 6px; background: var(--aether-bg, #11111b); border: 1px solid var(--aether-border, #313244); color: var(--aether-text-primary, #cdd6f4); border-radius: 4px; font-size: 11px;";

      const saveKeyBtn = document.createElement("button");
      saveKeyBtn.style.cssText = "padding: 4px 8px; background: var(--aether-accent, #89b4fa); color: var(--aether-bg, #11111b); border: none; border-radius: 4px; font-size: 11px; font-weight: 700; cursor: pointer;";
      saveKeyBtn.textContent = "Save Key";
      saveKeyBtn.onclick = () => {
        if (keyInput.value.trim()) {
          props.onUpdateCredential(p.id, keyInput.value.trim());
          keyInput.value = "";
        }
      };

      credRow.appendChild(keyInput);
      credRow.appendChild(saveKeyBtn);
      card.appendChild(credRow);
    }

    // Actions Row
    const actionRow = document.createElement("div");
    actionRow.style.cssText = "display: flex; gap: 6px; margin-top: 4px;";

    if (!p.isDefault) {
      const defBtn = document.createElement("button");
      defBtn.style.cssText = "padding: 3px 8px; background: transparent; border: 1px solid var(--aether-border, #313244); color: var(--aether-text-primary, #cdd6f4); border-radius: 4px; font-size: 11px; cursor: pointer;";
      defBtn.textContent = "Set as Default";
      defBtn.onclick = () => props.onSelectDefault(p.id);
      actionRow.appendChild(defBtn);
    }

    const testBtn = document.createElement("button");
    testBtn.style.cssText = "padding: 3px 8px; background: transparent; border: 1px solid var(--aether-border, #313244); color: var(--aether-info, #89dceb); border-radius: 4px; font-size: 11px; cursor: pointer;";
    testBtn.textContent = "Test Connection";
    testBtn.onclick = () => props.onValidateProvider(p.id);
    actionRow.appendChild(testBtn);

    card.appendChild(actionRow);
    list.appendChild(card);
  }

  container.appendChild(list);
  return container;
}
