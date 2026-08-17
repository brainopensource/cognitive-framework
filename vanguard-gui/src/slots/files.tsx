import { useState } from "react";
import type { ReactNode } from "react";

export type WorkspaceFile = { path: string; language: string; content: string };
export const MOCK_FILES: WorkspaceFile[] = [
  { path: "src/main.tsx", language: "typescript", content: 'const source = "mock";\nconsole.log("Vanguard GUI replay");\n' },
  { path: "README.md", language: "markdown", content: "# Mock workspace\n\nBrowser mode is labelled source: mock.\n" },
  { path: "package.json", language: "json", content: '{\n  "name": "mock-workspace"\n}\n' },
];

export function FilesSlot({ onOpen }: { onOpen: (file: WorkspaceFile) => void }) {
  const [filter, setFilter] = useState("");
  const files = MOCK_FILES.filter(file => file.path.includes(filter));
  return <div className="files-slot"><div className="mock-banner">source: mock · browser workspace stub</div><input aria-label="Filter workspace files" placeholder="Filter files" value={filter} onChange={event => setFilter(event.target.value)} /><div className="file-tree" role="tree"><div className="folder">⌄ workspace</div>{files.map(file => <button className="file-row" role="treeitem" key={file.path} onClick={() => onOpen(file)}>　{file.path}</button>)}</div><p className="muted">Tauri fs walk will replace this fixture tree when a workspace is picked.</p></div>;
}

export function SlotFrame({ title, children }: { title: string; children: ReactNode }) { return <section className="slot"><div className="slot-title"><span>{title}</span><span className="slot-mark">SLOT</span></div>{children}</section>; }
