import type { DesktopStore, ForensicTab } from "../state/desktop-store.js";
import { renderDiffViewer, renderArtifactReference, renderStatusBadge, renderErrorState } from "@aether/ui-web";
import { formatDeepLink } from "@aether/projections";

export function renderForensicDrawer(store: DesktopStore): HTMLElement | null {
  const state = store.get();
  if (!state.forensicDrawerOpen) return null;

  const drawer = document.createElement("aside");
  drawer.className = "aether-forensic-drawer";
  drawer.style.cssText = `
    width: 460px;
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
  tabs.style.cssText = "display: flex; border-bottom: 1px solid var(--aether-border, #313244); background: var(--aether-surface-raised, #1e1e2e);";

  const tabList: Array<{ id: ForensicTab; label: string }> = [
    { id: "diffs", label: "Diffs" },
    { id: "evidence", label: "Evidence" },
    { id: "artifacts", label: "Artifacts" },
    { id: "trace", label: "Trace" },
    { id: "runs", label: "Runs" },
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
    `;
    tabBtn.textContent = t.label;
    tabBtn.onclick = () => store.openForensicDrawer(t.id);
    tabs.appendChild(tabBtn);
  }
  drawer.appendChild(tabs);

  // 3. Content Pane
  const content = document.createElement("div");
  content.style.cssText = "flex: 1; overflow-y: auto; padding: 14px; box-sizing: border-box;";

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
    if (state.activeDiffText) {
      content.appendChild(renderDiffViewer(state.activeDiffText));
    } else {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No active diff selected.";
      content.appendChild(empty);
    }
  } else if (state.activeForensicTab === "evidence") {
    const claims = state.evidenceGrid.claims;
    if (claims.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No verified evidence claims recorded yet.";
      content.appendChild(empty);
    } else {
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
            onOpenInLab: () => {
              const link = formatDeepLink({ kind: "artifact", digest: art.digest });
              alert(`Deep link to Lab: ${link}`);
            },
          })
        );
      }
    }
  } else if (state.activeForensicTab === "trace") {
    const nodes = state.traceGraph.nodes;
    if (nodes.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No trace graph nodes recorded yet.";
      content.appendChild(empty);
    } else {
      for (const node of nodes) {
        const item = document.createElement("div");
        item.style.cssText = `
          padding: 8px 12px;
          margin-bottom: 6px;
          background: var(--aether-surface-raised, #252538);
          border: 1px solid var(--aether-border, #313244);
          border-radius: 6px;
          font-size: 12px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        `;
        item.innerHTML = `
          <div>
            <strong style="color: var(--aether-accent);">${node.summary ?? node.kind}</strong>
            <div style="font-size: 11px; color: var(--aether-text-muted); font-family: var(--aether-font-mono);">${node.id.slice(0, 16)}…</div>
          </div>
        `;
        const badge = renderStatusBadge({ status: "completed", label: node.kind, size: "sm" });
        item.appendChild(badge);
        content.appendChild(item);
      }
    }
  } else if (state.activeForensicTab === "runs") {
    const runs = state.runs;
    if (runs.length === 0) {
      const empty = document.createElement("div");
      empty.style.cssText = "color: var(--aether-text-muted, #6c7086); font-size: 13px; text-align: center; padding: 32px 0;";
      empty.textContent = "No previous runs found for current workspace.";
      content.appendChild(empty);
    } else {
      for (const r of runs) {
        const item = document.createElement("div");
        const isActive = r.runId === state.runId;
        item.style.cssText = `
          padding: 10px 12px;
          margin-bottom: 6px;
          background: ${isActive ? "var(--aether-surface-raised, #252538)" : "var(--aether-bg, #11111b)"};
          border: 1px solid ${isActive ? "var(--aether-accent, #89b4fa)" : "var(--aether-border, #313244)"};
          border-radius: 6px;
          font-size: 12px;
          cursor: pointer;
        `;

        const topRow = document.createElement("div");
        topRow.style.cssText = "display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;";

        const idSpan = document.createElement("span");
        idSpan.style.cssText = "font-weight: 700; font-family: var(--aether-font-mono); color: var(--aether-text-primary);";
        idSpan.textContent = `Run: ${r.runId.slice(0, 8)}…`;
        topRow.appendChild(idSpan);

        const badge = renderStatusBadge({ status: r.status, size: "sm" });
        topRow.appendChild(badge);
        item.appendChild(topRow);

        const btnRow = document.createElement("div");
        btnRow.style.cssText = "display: flex; gap: 6px; margin-top: 6px;";

        const attachBtn = document.createElement("button");
        attachBtn.style.cssText = "padding: 2px 6px; font-size: 11px; background: var(--aether-accent); color: var(--aether-bg); border: none; border-radius: 4px; cursor: pointer;";
        attachBtn.textContent = "Attach";
        attachBtn.onclick = (e) => {
          e.stopPropagation();
          store.controller.switchRun(r.runId);
        };
        btnRow.appendChild(attachBtn);

        const labBtn = document.createElement("button");
        labBtn.style.cssText = "padding: 2px 6px; font-size: 11px; background: var(--aether-surface-raised); color: var(--aether-info); border: 1px solid var(--aether-border); border-radius: 4px; cursor: pointer;";
        labBtn.textContent = "Lab ↗";
        labBtn.onclick = (e) => {
          e.stopPropagation();
          const link = formatDeepLink({ kind: "run", runId: r.runId });
          alert(`Deep link to Lab: ${link}`);
        };
        btnRow.appendChild(labBtn);

        item.appendChild(btnRow);
        item.onclick = () => store.controller.switchRun(r.runId);
        content.appendChild(item);
      }
    }
  } else if (state.activeForensicTab === "settings") {
    const s = state.settings;
    const form = document.createElement("div");
    form.style.cssText = "display: flex; flex-direction: column; gap: 14px; font-size: 13px;";

    // Section 1: General
    form.innerHTML = `
      <div style="font-weight: 700; color: var(--aether-accent); border-bottom: 1px solid var(--aether-border); padding-bottom: 4px;">General</div>
      <div>
        <label style="color: var(--aether-text-muted); font-size: 11px; display: block; margin-bottom: 2px;">Default Runtime Socket</label>
        <input type="text" id="set-runtime" value="${s.runtime.socketPath}" style="width: 100%; padding: 6px; background: var(--aether-bg); border: 1px solid var(--aether-border); color: var(--aether-text-primary); border-radius: 4px; box-sizing: border-box;" />
      </div>
      <div>
        <label style="color: var(--aether-text-muted); font-size: 11px; display: block; margin-bottom: 2px;">Default Workspace</label>
        <input type="text" id="set-workspace" value="${s.general.defaultWorkspace}" style="width: 100%; padding: 6px; background: var(--aether-bg); border: 1px solid var(--aether-border); color: var(--aether-text-primary); border-radius: 4px; box-sizing: border-box;" />
      </div>

      <div style="font-weight: 700; color: var(--aether-accent); border-bottom: 1px solid var(--aether-border); padding-bottom: 4px; margin-top: 8px;">Appearance</div>
      <div>
        <label style="color: var(--aether-text-muted); font-size: 11px; display: block; margin-bottom: 2px;">Theme</label>
        <select id="set-theme" style="width: 100%; padding: 6px; background: var(--aether-bg); border: 1px solid var(--aether-border); color: var(--aether-text-primary); border-radius: 4px; box-sizing: border-box;">
          <option value="dark" ${s.appearance.theme === "dark" ? "selected" : ""}>Dark (Electroweak)</option>
          <option value="light" ${s.appearance.theme === "light" ? "selected" : ""}>Light</option>
          <option value="high-contrast" ${s.appearance.theme === "high-contrast" ? "selected" : ""}>High Contrast</option>
        </select>
      </div>

      <div style="font-weight: 700; color: var(--aether-accent); border-bottom: 1px solid var(--aether-border); padding-bottom: 4px; margin-top: 8px;">Accessibility</div>
      <div style="display: flex; align-items: center; gap: 8px;">
        <input type="checkbox" id="set-motion" ${s.appearance.reducedMotion ? "checked" : ""} />
        <label for="set-motion" style="color: var(--aether-text-primary);">Reduced Motion</label>
      </div>
    `;

    const saveBtn = document.createElement("button");
    saveBtn.style.cssText = "margin-top: 12px; padding: 8px 14px; background: var(--aether-accent); color: var(--aether-bg); border: none; border-radius: 6px; font-weight: 700; cursor: pointer;";
    saveBtn.textContent = "Save Settings";
    saveBtn.onclick = () => {
      const runtimeInput = form.querySelector("#set-runtime") as HTMLInputElement;
      const wsInput = form.querySelector("#set-workspace") as HTMLInputElement;
      const themeSelect = form.querySelector("#set-theme") as HTMLSelectElement;
      const motionCheck = form.querySelector("#set-motion") as HTMLInputElement;

      store.controller.updateSettings({
        runtime: { ...s.runtime, socketPath: runtimeInput?.value ?? s.runtime.socketPath },
        general: { ...s.general, defaultWorkspace: wsInput?.value ?? s.general.defaultWorkspace },
        appearance: {
          ...s.appearance,
          theme: (themeSelect?.value as any) ?? s.appearance.theme,
          reducedMotion: motionCheck?.checked ?? s.appearance.reducedMotion,
        },
      });
      alert("Settings updated!");
    };
    form.appendChild(saveBtn);
    content.appendChild(form);
  }

  drawer.appendChild(content);
  return drawer;
}
