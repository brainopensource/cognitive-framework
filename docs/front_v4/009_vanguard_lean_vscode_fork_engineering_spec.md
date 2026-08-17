# Vanguard Lean VS Code / Code-OSS Fork Engineering Specification

**Status:** `VOID` — superseded by D3 standalone GUI (`009_ide_extension.md`, `gui_ide_slots.md`). Do not implement.

**Document ID:** `VG-FE-009` (historical)


---

## 1. Architectural Strategy: The VSCodium / Code-OSS Foundation

Rather than maintaining a massive custom editor fork from scratch, the Vanguard IDE is engineered on top of **Code-OSS / VSCodium** (the exact proven model utilized by Cursor, Void, and PearAI).

```
┌─────────────────────────────────────────────────────────────┐
│                 UPSTREAM CODE-OSS REPOSITORY                │
└──────────────────────────────┬──────────────────────────────┘
                               │ Automated Git Submodule / Patches
┌──────────────────────────────▼──────────────────────────────┐
│             VANGUARD DEBLOATING & BRANDING PASS             │
│  - Strip Microsoft telemetry & crash reporting endpoints    │
│  - Redirect Marketplace to Open-VSX (open-source extensions)│
│  - Remove Azure/MS-Account login dependencies               │
│  - Apply Vanguard dark-neutral theme & custom assets        │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│             VANGUARD EXTENSION & WORKBENCH EMBED            │
│  - Native Secondary Panel (Right Webview Sidebar)           │
│  - Monaco Inline Diff Decorator & CodeLens Provider         │
│  - Bidirectional Context Injector (Active File / Diffs)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Telemetry & Bloat Scrubbing Pipeline

A dedicated patch script (`tools/ide/scrub_code_oss.sh`) modifies `product.json` before build time:

### Key Changes in `product.json`
```json
{
  "nameShort": "Vanguard",
  "nameLong": "Vanguard AI Studio",
  "applicationName": "vanguard-ide",
  "dataFolderName": ".vanguard-ide",
  "win32MutexName": "vanguardide",
  "licenseName": "Apache-2.0",
  
  "extensionsGallery": {
    "serviceUrl": "https://open-vsx.org/vscode/gallery",
    "itemUrl": "https://open-vsx.org/vscode/item"
  },
  
  "enableTelemetry": false,
  "telemetryEndpoint": "",
  "sendASPNETTelemetry": false,
  "crashReporter": {
    "companyName": "Vanguard",
    "productName": "Vanguard IDE"
  }
}
```

---

## 3. Webview Secondary Panel Integration

The Vanguard panel is contributed via a built-in extension under `src/vs/workbench/contrib/vanguard/`:

### Extension `package.json` Contribution
```json
{
  "name": "vanguard-core-panel",
  "displayName": "Vanguard AI Assistant",
  "publisher": "vanguard",
  "version": "0.4.1",
  "contributes": {
    "viewsContainers": {
      "panel": [
        {
          "id": "vanguard-view-container",
          "title": "Vanguard",
          "icon": "resources/vanguard-icon.svg"
        }
      ]
    },
    "views": {
      "vanguard-view-container": [
        {
          "type": "webview",
          "id": "vanguard.chatView",
          "name": "Agent Session"
        }
      ]
    }
  }
}
```

---

## 4. Context Synchronization Between Editor and Vanguard

The Webview extension communicates with the VS Code extension host API to capture real-time editor state:

```typescript
import * as vscode from "vscode";

export function getActiveWorkspaceContext(): Record<string, unknown> {
  const editor = vscode.window.activeTextEditor;
  const workspaceFolders = vscode.workspace.workspaceFolders;

  return {
    workspace_root: workspaceFolders ? workspaceFolders[0].uri.fsPath : null,
    active_file: editor ? editor.document.fileName : null,
    cursor_line: editor ? editor.selection.active.line + 1 : null,
    selected_text: editor ? editor.document.getText(editor.selection) : "",
    dirty_files: vscode.workspace.textDocuments.filter((d) => d.isDirty).map((d) => d.fileName),
  };
}
```

---

## 5. Build and Compilation Steps

```bash
# 1. Install prerequisites (Node 20, yarn, Python 3, build tools)
npm install -g yarn gulp

# 2. Build Code-OSS with Vanguard patches
cd vanguard-ide
yarn
yarn run gulp vscode-linux-x64
# Or for Windows:
yarn run gulp vscode-win32-x64

# 3. Output package
# Results generated in ../VSCode-linux-x64/ or ../VSCode-win32-x64/
```
