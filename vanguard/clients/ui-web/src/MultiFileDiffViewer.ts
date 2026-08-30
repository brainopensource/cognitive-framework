import type { MultiFileDiffModel, FileDiffEntry } from "@aether/contracts";
import { renderDiffViewer } from "./DiffViewer.js";
import { renderStatusBadge } from "./StatusBadge.js";

export type MultiFileDiffViewerProps = {
  diffModel: MultiFileDiffModel;
  selectedFilePath?: string;
  onSelectFile?: (path: string) => void;
};

export function renderMultiFileDiffViewer(props: MultiFileDiffViewerProps): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-multi-file-diff-viewer";
  container.style.cssText = "display: flex; flex-direction: column; gap: 12px; font-size: 13px; height: 100%;";

  const header = document.createElement("div");
  header.style.cssText = "display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--aether-border, #313244); padding-bottom: 8px;";

  const left = document.createElement("div");
  left.innerHTML = `
    <div style="font-weight: 700; color: var(--aether-text-primary, #cdd6f4);">
      Files Changed (${props.diffModel.summary.totalFiles})
    </div>
    <div style="font-size: 11px; color: var(--aether-text-muted, #6c7086);">
      <span style="color: var(--aether-success, #a6e3a1);">+${props.diffModel.summary.totalAdditions}</span> /
      <span style="color: var(--aether-danger, #f38ba8);">-${props.diffModel.summary.totalDeletions}</span>
    </div>
  `;
  header.appendChild(left);

  const statusBadge = renderStatusBadge({
    status:
      props.diffModel.overallStatus === "VERIFIED"
        ? "satisfied"
        : props.diffModel.overallStatus === "APPLIED" || props.diffModel.overallStatus === "APPROVED"
        ? "valid"
        : props.diffModel.overallStatus === "FAILED"
        ? "failed"
        : "pending",
    label: props.diffModel.overallStatus,
    size: "sm",
  });
  header.appendChild(statusBadge);
  container.appendChild(header);

  if (props.diffModel.files.length === 0) {
    const empty = document.createElement("div");
    empty.style.cssText = "color: var(--aether-text-muted, #6c7086); text-align: center; padding: 24px 0;";
    empty.textContent = "No file modifications recorded.";
    container.appendChild(empty);
    return container;
  }

  // File Tabs / List
  const fileList = document.createElement("div");
  fileList.style.cssText = "display: flex; flex-wrap: wrap; gap: 6px;";

  let activeFile = props.diffModel.files.find((f) => f.filePath === props.selectedFilePath) ?? props.diffModel.files[0];

  for (const f of props.diffModel.files) {
    const isSelected = activeFile?.filePath === f.filePath;
    const tab = document.createElement("button");
    tab.style.cssText = `
      padding: 4px 8px;
      background: ${isSelected ? "var(--aether-surface-raised, #252538)" : "var(--aether-surface, #181825)"};
      border: 1px solid ${isSelected ? "var(--aether-accent, #89b4fa)" : "var(--aether-border, #313244)"};
      color: ${isSelected ? "var(--aether-accent, #89b4fa)" : "var(--aether-text-primary, #cdd6f4)"};
      border-radius: 4px;
      font-size: 11px;
      font-family: var(--aether-font-mono, monospace);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
    `;
    tab.innerHTML = `<span>${f.filePath}</span><span style="font-size: 10px; color: var(--aether-text-muted, #6c7086);">(+${f.additions}/-${f.deletions})</span>`;
    tab.onclick = () => {
      if (props.onSelectFile) props.onSelectFile(f.filePath);
    };
    fileList.appendChild(tab);
  }
  container.appendChild(fileList);

  // Diff Box
  if (activeFile) {
    const diffContainer = document.createElement("div");
    diffContainer.style.cssText = "flex: 1; overflow-y: auto; border: 1px solid var(--aether-border, #313244); border-radius: 4px;";
    diffContainer.appendChild(renderDiffViewer(activeFile.patchText));
    container.appendChild(diffContainer);
  }

  return container;
}
