import { copyToClipboard } from "../util/clipboard.js";
import { isDigest, truncateDigest } from "../util/formatting.js";
import type { SelectionModel } from "../state/selection-model.js";

export type JsonTreeOptions = {
  data: unknown;
  rootName?: string;
  defaultExpandedDepth?: number;
  selection?: SelectionModel;
};

export function renderJsonPayloadTree(options: JsonTreeOptions): HTMLElement {
  const container = document.createElement("div");
  container.className = "aether-json-tree";
  container.style.cssText = `
    font-family: var(--lab-font-mono);
    font-size: 12px;
    line-height: 1.5;
    color: var(--lab-text-primary);
    overflow-x: auto;
    padding: 8px;
  `;

  const rootNode = renderNode(
    options.rootName ?? "payload",
    options.data,
    0,
    options.defaultExpandedDepth ?? 1,
    options.selection
  );
  container.appendChild(rootNode);

  return container;
}

function renderNode(
  key: string,
  value: unknown,
  depth: number,
  maxExpandedDepth: number,
  selection?: SelectionModel
): HTMLElement {
  const node = document.createElement("div");
  node.className = "aether-json-node";
  node.style.cssText = `margin-left: ${depth > 0 ? 14 : 0}px; margin-top: 2px;`;

  if (value === null || value === undefined) {
    node.appendChild(createPrimitiveRow(key, String(value), "var(--lab-text-muted)"));
    return node;
  }

  if (typeof value === "boolean") {
    node.appendChild(createPrimitiveRow(key, String(value), "var(--lab-warning)"));
    return node;
  }

  if (typeof value === "number") {
    node.appendChild(createPrimitiveRow(key, String(value), "var(--lab-accent)"));
    return node;
  }

  if (typeof value === "string") {
    if (isDigest(value)) {
      node.appendChild(createDigestRow(key, value, selection));
      return node;
    }
    // Check for special cross reference keys
    if (key === "parentEventId" || key === "targetEventId") {
      node.appendChild(createEventRefRow(key, value, selection));
      return node;
    }
    if (key === "artifactId" || key === "digest") {
      node.appendChild(createArtifactRefRow(key, value, selection));
      return node;
    }

    node.appendChild(createPrimitiveRow(key, `"${value}"`, "var(--lab-success)"));
    return node;
  }

  if (Array.isArray(value)) {
    const isExpanded = depth < maxExpandedDepth;
    const arrayContainer = document.createElement("div");

    const header = document.createElement("div");
    header.style.cssText = "display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none;";

    const toggle = document.createElement("span");
    toggle.style.cssText = "color: var(--lab-text-muted); font-size: 10px; width: 10px;";
    toggle.textContent = isExpanded ? "▼" : "▶";

    const label = document.createElement("span");
    label.style.cssText = "color: var(--lab-text-secondary);";
    label.textContent = `${key}: [${value.length} items]`;

    header.appendChild(toggle);
    header.appendChild(label);
    arrayContainer.appendChild(header);

    const childrenContainer = document.createElement("div");
    childrenContainer.style.display = isExpanded ? "block" : "none";

    let hasBuiltChildren = isExpanded;
    const buildChildren = () => {
      childrenContainer.innerHTML = "";
      value.forEach((item, idx) => {
        childrenContainer.appendChild(
          renderNode(String(idx), item, depth + 1, maxExpandedDepth, selection)
        );
      });
      hasBuiltChildren = true;
    };

    if (isExpanded) {
      buildChildren();
    }

    header.onclick = () => {
      const currentlyVisible = childrenContainer.style.display !== "none";
      if (!currentlyVisible) {
        if (!hasBuiltChildren) buildChildren();
        childrenContainer.style.display = "block";
        toggle.textContent = "▼";
      } else {
        childrenContainer.style.display = "none";
        toggle.textContent = "▶";
      }
    };

    arrayContainer.appendChild(childrenContainer);
    node.appendChild(arrayContainer);
    return node;
  }

  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    const isExpanded = depth < maxExpandedDepth;
    const objContainer = document.createElement("div");

    const header = document.createElement("div");
    header.style.cssText = "display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none;";

    const toggle = document.createElement("span");
    toggle.style.cssText = "color: var(--lab-text-muted); font-size: 10px; width: 10px;";
    toggle.textContent = isExpanded ? "▼" : "▶";

    const label = document.createElement("span");
    label.style.cssText = "color: var(--lab-text-secondary);";
    label.textContent = `${key}: { ${entries.length} keys }`;

    header.appendChild(toggle);
    header.appendChild(label);
    objContainer.appendChild(header);

    const childrenContainer = document.createElement("div");
    childrenContainer.style.display = isExpanded ? "block" : "none";

    let hasBuiltChildren = isExpanded;
    const buildChildren = () => {
      childrenContainer.innerHTML = "";
      for (const [childKey, childVal] of entries) {
        childrenContainer.appendChild(
          renderNode(childKey, childVal, depth + 1, maxExpandedDepth, selection)
        );
      }
      hasBuiltChildren = true;
    };

    if (isExpanded) {
      buildChildren();
    }

    header.onclick = () => {
      const currentlyVisible = childrenContainer.style.display !== "none";
      if (!currentlyVisible) {
        if (!hasBuiltChildren) buildChildren();
        childrenContainer.style.display = "block";
        toggle.textContent = "▼";
      } else {
        childrenContainer.style.display = "none";
        toggle.textContent = "▶";
      }
    };

    objContainer.appendChild(childrenContainer);
    node.appendChild(objContainer);
    return node;
  }

  node.appendChild(createPrimitiveRow(key, String(value), "var(--lab-text-primary)"));
  return node;
}

function createPrimitiveRow(key: string, formattedVal: string, color: string): HTMLElement {
  const row = document.createElement("div");
  row.style.cssText = "display: flex; align-items: baseline; gap: 6px;";

  const keyEl = document.createElement("span");
  keyEl.style.cssText = "color: var(--lab-text-secondary);";
  keyEl.textContent = `${key}:`;
  row.appendChild(keyEl);

  const valEl = document.createElement("span");
  valEl.style.cssText = `color: ${color}; word-break: break-all;`;
  valEl.textContent = formattedVal;
  row.appendChild(valEl);

  const copyBtn = document.createElement("button");
  copyBtn.textContent = "📋";
  copyBtn.title = "Copy value";
  copyBtn.style.cssText = "background: none; border: none; font-size: 10px; cursor: pointer; opacity: 0.5; padding: 0;";
  copyBtn.onmouseenter = () => (copyBtn.style.opacity = "1");
  copyBtn.onmouseleave = () => (copyBtn.style.opacity = "0.5");
  copyBtn.onclick = () => copyToClipboard(formattedVal.replace(/^"|"$/g, ""));
  row.appendChild(copyBtn);

  return row;
}

function createDigestRow(key: string, digest: string, selection?: SelectionModel): HTMLElement {
  const row = document.createElement("div");
  row.style.cssText = "display: flex; align-items: center; gap: 6px;";

  const keyEl = document.createElement("span");
  keyEl.style.cssText = "color: var(--lab-text-secondary);";
  keyEl.textContent = `${key}:`;
  row.appendChild(keyEl);

  const pill = document.createElement("span");
  pill.style.cssText = `
    background: var(--lab-bg-panel);
    border: 1px solid var(--lab-border-active);
    color: var(--lab-digest);
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 11px;
    font-family: var(--lab-font-mono);
  `;
  pill.textContent = truncateDigest(digest, 16);
  pill.title = digest;
  row.appendChild(pill);

  const copyBtn = document.createElement("button");
  copyBtn.textContent = "📋";
  copyBtn.title = "Copy full digest";
  copyBtn.style.cssText = "background: none; border: none; font-size: 10px; cursor: pointer; opacity: 0.7; padding: 0;";
  copyBtn.onclick = () => copyToClipboard(digest);
  row.appendChild(copyBtn);

  return row;
}

function createEventRefRow(key: string, eventId: string, selection?: SelectionModel): HTMLElement {
  const row = document.createElement("div");
  row.style.cssText = "display: flex; align-items: center; gap: 6px;";

  const keyEl = document.createElement("span");
  keyEl.style.cssText = "color: var(--lab-text-secondary);";
  keyEl.textContent = `${key}:`;
  row.appendChild(keyEl);

  const link = document.createElement("button");
  link.style.cssText = `
    background: var(--lab-accent-muted);
    border: 1px solid var(--lab-accent);
    color: var(--lab-accent);
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 11px;
    font-family: var(--lab-font-mono);
    cursor: pointer;
  `;
  link.textContent = `↗ Jump to Event (${truncateDigest(eventId, 8)})`;
  link.title = `Jump to Event ${eventId}`;
  link.onclick = () => {
    if (selection) {
      selection.setWorkbench("events");
      selection.selectEvent(eventId);
    }
  };
  row.appendChild(link);

  return row;
}

function createArtifactRefRow(key: string, artifactId: string, selection?: SelectionModel): HTMLElement {
  const row = document.createElement("div");
  row.style.cssText = "display: flex; align-items: center; gap: 6px;";

  const keyEl = document.createElement("span");
  keyEl.style.cssText = "color: var(--lab-text-secondary);";
  keyEl.textContent = `${key}:`;
  row.appendChild(keyEl);

  const link = document.createElement("button");
  link.style.cssText = `
    background: var(--lab-bg-panel);
    border: 1px solid var(--lab-digest);
    color: var(--lab-digest);
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 11px;
    font-family: var(--lab-font-mono);
    cursor: pointer;
  `;
  link.textContent = `📦 Inspect Artifact (${truncateDigest(artifactId, 8)})`;
  link.title = `Inspect Artifact ${artifactId}`;
  link.onclick = () => {
    if (selection) {
      selection.setWorkbench("artifacts");
      selection.selectArtifact(artifactId);
    }
  };
  row.appendChild(link);

  return row;
}
