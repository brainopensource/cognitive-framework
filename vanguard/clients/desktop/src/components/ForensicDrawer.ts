import type { DesktopStore, ForensicTab } from "../state/desktop-store.js";
import {
  renderDiffViewer,
  renderArtifactReference,
  renderStatusBadge,
  renderErrorState,
  renderMultiFileDiffViewer,
  renderProviderManager,
  renderVerificationCard,
  renderResearchCitationCard,
} from "@aether/ui-web";
import { formatDeepLink } from "@aether/projections";
import { renderCredentialPanel } from "./CredentialPanel.js";
import { renderLogsPane } from "./LogsPane.js";

export function renderForensicDrawer(store: DesktopStore): HTMLElement | null {
  const state = store.get();
  if (!state.forensicDrawerOpen) return null;

  const drawer = document.createElement("aside");
  drawer.className = "aether-forensic-drawer";
  drawer.style.cssText = `
    width: 480px;
    height: 100%;
    background: var(--aether-surface, #181825);
    border-left: 1px solid var(--aether-border, #313244);
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    user-select: none;
    z-index: 50;
  `;

  // 1. Header & Close Button
  const header = document.createElement("div");
  header.style.cssText = `
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--aether-border, #313244);
  `;

  const title = document.createElement("div");
  title.style.cssText = "font-weight: 700; font-size: 14px; color: var(--aether-text-primary, #cdd6f4);";
  title.textContent = "🔍 Forensic & Evidence Inspector";
  header.appendChild(title);

  const closeBtn = document.createElement("button");
  closeBtn.style.cssText = "background: none; border: none; color: var(--aether-text-muted, #6c7086); cursor: pointer; font-size: 16px;";
  closeBtn.textContent = "✕";
  closeBtn.onclick = () => store.closeForensicDrawer();
  header.appendChild(closeBtn);

  drawer.appendChild(header);

  // 2. Tab Bar
  const tabs = document.createElement("div");
  tabs.style.cssText = "display: flex; border-bottom: 1px solid var(--aether-border, #313244); background: var(--aether-surface-raised, #1e1e2e); overflow-x: auto;";

  const tabList: Array<{ id: ForensicTab; label: string }> = [
    { id: "diffs", label: "Diffs" },
    { id: "evidence", label: "Evidence" },
    { id: "artifacts", label: "Artifacts" },
    { id: "trace", label: "Trace" },
    { id: "runs", label: "Runs" },
    { id: "logs", label: "Logs" },
    { id: "settings", label: "Settings" },
  ];

  for (const t of tabList) {
    const tabBtn = document.createElement("button");
    const isActive = state.activeForensicTab === t.id;
    tabBtn.style.cssText = `
      flex: 1;
      padding: 8px 4px;
      background: ${isActive ? "var(--aether-surface, #181825)" : "transparent"};
      color: ${isActive ? "var(--aether-accent, #89b4fa)" : "var(--aether-text-muted, #6c7086)"};
      border: none;
      border-bottom: 2px solid ${isActive ? "var(--aether-accent, #89b4fa)" : "transparent"};
      font-weight: 600;
      cursor: pointer;
      font-size: 12px;
      white-space: nowrap;
    `;
    tabBtn.textContent = t.label;
    tabBtn.onclick = () => store.openForensicDrawer(t.id);
    tabs.appendChild(tabBtn);
  }
  drawer.appendChild(tabs);

  // 3. Content Pane
  const content = document.createElement("div");
  content.style.cssText = "flex: 1; overflow-y: auto; padding: 14px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;";

  // Failures / Diagnostics banner if present
  if (state.lastFailure) {
    content.appendChild(
      renderErrorState({
        diagnostics: state.lastFailure,
        onRetry: () => store.controller.reconnectRuntime(),
        onDismiss: () => store.controller.clearFailure(),
      })
    );
  }

  if (state.activeForensicTab === "diffs") {
    if (state.multiFileDiff && state.multiFileDiff.files.length > 0) {
      content.appendChild(
        renderMultiFileDiffViewer({
          diffModel: state.multiFileDiff,
        })
      );
    } else if (state.activeDiffText) {
      content.appendChild(renderDiffViewer(state.activeDiffText));
    } else {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No active diff or file modifications selected.";
      content.appendChild(empty);
    }
  } else if (state.activeForensicTab === "evidence") {
    const claims = state.evidenceGrid.claims;
    const citations = state.researchSummary.citations;

    if (claims.length === 0 && citations.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No verified evidence claims or citations recorded yet.";
      content.appendChild(empty);
    } else {
      if (citations.length > 0) {
        const citeHeader = document.createElement("div");
        citeHeader.style.cssText = "font-weight: 700; color: var(--aether-accent, #89b4fa); font-size: 12px; margin-bottom: 4px;";
        citeHeader.textContent = "Research Citations & Sources";
        content.appendChild(citeHeader);

        for (const cite of citations) {
          content.appendChild(
            renderResearchCitationCard({
              citation: cite,
              onOpenLabEvidence: (evId) => store.openInLab({ kind: "run", runId: state.runId }),
            })
          );
        }
      }

      if (claims.length > 0) {
        const claimHeader = document.createElement("div");
        claimHeader.style.cssText = "font-weight: 700; color: var(--aether-accent, #89b4fa); font-size: 12px; margin-top: 8px; margin-bottom: 4px;";
        claimHeader.textContent = "Verified Claims";
        content.appendChild(claimHeader);

        for (const claim of claims) {
          const item = document.createElement("div");
          item.style.cssText = `
            padding: 10px 12px;
            margin-bottom: 8px;
            background: var(--aether-surface-raised, #252538);
            border: 1px solid var(--aether-border, #313244);
            border-radius: 6px;
            font-size: 12px;
            color: var(--aether-text-primary, #cdd6f4);
          `;
          item.innerHTML = `
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <strong style="color: var(--aether-success, #a6e3a1);">✔ [${claim.claimType}]</strong>
              <span style="font-size: 11px; color: var(--aether-text-muted);">${claim.claimId ? `id:${claim.claimId.slice(0, 8)}` : ""}</span>
            </div>
            <div>${claim.statement}</div>
          `;
          content.appendChild(item);
        }
      }
    }
  } else if (state.activeForensicTab === "artifacts") {
    const artifacts = state.evidenceGrid.artifacts;
    if (artifacts.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No artifacts generated in this session.";
      content.appendChild(empty);
    } else {
      for (const art of artifacts) {
        content.appendChild(
          renderArtifactReference({
            digest: art.digest,
            path: art.path,
            summary: `Kind: ${art.kind}`,
            onOpenInLab: () => store.openInLab({ kind: "artifact", digest: art.digest }),
          })
        );
      }
    }
  } else if (state.activeForensicTab === "trace") {
    const nodes = state.traceGraph.nodes;
    if (nodes.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No causal trace nodes recorded.";
      content.appendChild(empty);
    } else {
      const labBtn = document.createElement("button");
      labBtn.style.cssText = "padding: 6px 12px; background: var(--aether-surface-raised, #252538); color: var(--aether-accent, #89b4fa); border: 1px solid var(--aether-border, #313244); border-radius: 4px; font-size: 11px; cursor: pointer; align-self: flex-start;";
      labBtn.textContent = "Open Full Trace Graph in Lab ↗";
      labBtn.onclick = () => store.openInLab({ kind: "trace", runId: state.runId, nodeId: nodes[0]?.id ?? "" });
      content.appendChild(labBtn);

      for (const n of nodes) {
        const item = document.createElement("div");
        item.style.cssText = `
          padding: 8px 10px;
          margin-bottom: 6px;
          background: var(--aether-bg, #11111b);
          border: 1px solid var(--aether-border, #313244);
          border-radius: 4px;
          font-size: 11px;
          font-family: var(--aether-font-mono, monospace);
        `;
        item.innerHTML = `
          <div style="display: flex; justify-content: space-between;">
            <strong style="color: var(--aether-accent, #89b4fa);">${n.kind}</strong>
            <span style="color: var(--aether-text-muted, #6c7086);">seq: ${n.seq}</span>
          </div>
          <div style="color: var(--aether-text-muted, #6c7086); margin-top: 2px;">node: ${n.id.slice(0, 12)}…</div>
        `;
        content.appendChild(item);
      }
    }
  } else if (state.activeForensicTab === "runs") {
    if (state.runs.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No runs recorded in runtime.";
      content.appendChild(empty);
    } else {
      for (const r of state.runs) {
        const isActive = r.runId === state.runId;
        const item = document.createElement("div");
        item.style.cssText = `
          padding: 10px 12px;
          margin-bottom: 8px;
          background: ${isActive ? "var(--aether-surface-raised, #252538)" : "var(--aether-bg, #11111b)"};
          border: 1px solid ${isActive ? "var(--aether-accent, #89b4fa)" : "var(--aether-border, #313244)"};
          border-radius: 6px;
          font-size: 12px;
          cursor: pointer;
        `;

        const topRow = document.createElement("div");
        topRow.style.cssText = "display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;";

        const idSpan = document.createElement("span");
        idSpan.style.cssText = "font-weight: 700; font-family: var(--aether-font-mono, monospace); color: var(--aether-text-primary, #cdd6f4);";
        idSpan.textContent = `Run: ${r.runId.slice(0, 8)}…`;
        topRow.appendChild(idSpan);

        const badge = renderStatusBadge({ status: r.status, size: "sm" });
        topRow.appendChild(badge);
        item.appendChild(topRow);

        const btnRow = document.createElement("div");
        btnRow.style.cssText = "display: flex; gap: 6px; margin-top: 6px;";

        const attachBtn = document.createElement("button");
        attachBtn.style.cssText = "padding: 2px 6px; font-size: 11px; background: var(--aether-accent, #89b4fa); color: var(--aether-bg, #11111b); border: none; border-radius: 4px; cursor: pointer;";
        attachBtn.textContent = "Attach";
        attachBtn.onclick = (e) => {
          e.stopPropagation();
          store.controller.switchRun(r.runId);
        };
        btnRow.appendChild(attachBtn);

        const cliBtn = document.createElement("button");
        cliBtn.style.cssText = "padding: 2px 6px; font-size: 11px; background: var(--aether-surface-raised, #252538); color: var(--aether-text-primary, #cdd6f4); border: 1px solid var(--aether-border, #313244); border-radius: 4px; cursor: pointer;";
        cliBtn.textContent = "Copy CLI";
        cliBtn.onclick = (e) => {
          e.stopPropagation();
          store.copyCliCommand(r.runId);
        };
        btnRow.appendChild(cliBtn);

        const labBtn = document.createElement("button");
        labBtn.style.cssText = "padding: 2px 6px; font-size: 11px; background: var(--aether-surface-raised, #252538); color: var(--aether-info, #89dceb); border: 1px solid var(--aether-border, #313244); border-radius: 4px; cursor: pointer;";
        labBtn.textContent = "Lab ↗";
        labBtn.onclick = (e) => {
          e.stopPropagation();
          store.openInLab({ kind: "run", runId: r.runId });
        };
        btnRow.appendChild(labBtn);

        item.appendChild(btnRow);
        item.onclick = () => store.controller.switchRun(r.runId);
        content.appendChild(item);
      }
    }
  } else if (state.activeForensicTab === "logs") {
    content.appendChild(renderLogsPane(store));
  } else if (state.activeForensicTab === "settings") {
    // Real credential status first: it is the answer to "why did nothing
    // happen", and it comes from the runtime rather than from browser defaults.
    content.appendChild(renderCredentialPanel(store));

    const providerSec = renderProviderManager({
      providers: state.providers,
      selectedProviderId: state.selectedProviderId,
      onSelectDefault: (id) => store.controller.setDefaultProvider(id),
      onSelectModel: (pId, mId) => store.controller.updateProvider(pId, { selectedModel: mId }),
      onAddProvider: (p) => store.controller.addProvider(p),
      onRemoveProvider: (id) => store.controller.removeProvider(id),
      onUpdateCredential: (pId, secret) => store.controller.setProviderCredential(pId, secret),
      onValidateProvider: (pId) => store.controller.validateProvider(pId),
      credentialsManagedByRuntime: true,
    });
    content.appendChild(providerSec);

    // Appearance & Preferences
    const s = state.settings;
    const prefBox = document.createElement("div");
    prefBox.style.cssText = "display: flex; flex-direction: column; gap: 12px; margin-top: 16px; border-top: 1px solid var(--aether-border, #313244); padding-top: 12px;";
    prefBox.innerHTML = `
      <div style="font-weight: 700; color: var(--aether-accent, #89b4fa);">Preferences</div>
      <div>
        <label style="color: var(--aether-text-muted, #6c7086); font-size: 11px; display: block; margin-bottom: 2px;">Default Runtime Socket</label>
        <input type="text" id="set-runtime" value="${s.runtime.socketPath}" style="width: 100%; padding: 6px; background: var(--aether-bg, #11111b); border: 1px solid var(--aether-border, #313244); color: var(--aether-text-primary, #cdd6f4); border-radius: 4px; box-sizing: border-box;" />
      </div>
      <div>
        <label style="color: var(--aether-text-muted, #6c7086); font-size: 11px; display: block; margin-bottom: 2px;">Default Workspace</label>
        <input type="text" id="set-workspace" value="${s.general.defaultWorkspace}" style="width: 100%; padding: 6px; background: var(--aether-bg, #11111b); border: 1px solid var(--aether-border, #313244); color: var(--aether-text-primary, #cdd6f4); border-radius: 4px; box-sizing: border-box;" />
      </div>
      <div>
        <label style="color: var(--aether-text-muted, #6c7086); font-size: 11px; display: block; margin-bottom: 2px;">Theme</label>
        <select id="set-theme" style="width: 100%; padding: 6px; background: var(--aether-bg, #11111b); border: 1px solid var(--aether-border, #313244); color: var(--aether-text-primary, #cdd6f4); border-radius: 4px; box-sizing: border-box;">
          <option value="dark" ${s.appearance.theme === "dark" ? "selected" : ""}>Dark (Electroweak)</option>
          <option value="light" ${s.appearance.theme === "light" ? "selected" : ""}>Light</option>
          <option value="high-contrast" ${s.appearance.theme === "high-contrast" ? "selected" : ""}>High Contrast</option>
        </select>
      </div>
    `;

    const saveBtn = document.createElement("button");
    saveBtn.style.cssText = "margin-top: 8px; padding: 8px 14px; background: var(--aether-accent, #89b4fa); color: var(--aether-bg, #11111b); border: none; border-radius: 6px; font-weight: 700; cursor: pointer;";
    saveBtn.textContent = "Save Preferences";
    saveBtn.onclick = () => {
      const runtimeInput = prefBox.querySelector("#set-runtime") as HTMLInputElement;
      const wsInput = prefBox.querySelector("#set-workspace") as HTMLInputElement;
      const themeSelect = prefBox.querySelector("#set-theme") as HTMLSelectElement;

      store.controller.updateSettings({
        runtime: { ...s.runtime, socketPath: runtimeInput?.value ?? s.runtime.socketPath },
        general: { ...s.general, defaultWorkspace: wsInput?.value ?? s.general.defaultWorkspace },
        appearance: {
          ...s.appearance,
          theme: (themeSelect?.value as any) ?? s.appearance.theme,
        },
      });
    };
    prefBox.appendChild(saveBtn);
    content.appendChild(prefBox);
  }

  drawer.appendChild(content);
  return drawer;
}
