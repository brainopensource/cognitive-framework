# Vanguard GUI

Standalone Tauri 2 + React shell for the Vanguard run stream. Wave 2 binds the
files and editor slots to Monaco and the terminal slot to xterm. Native
filesystem and PTY commands are intentionally optional while running Vite:
browser mode labels those adapters `source: mock` / `not_available` rather than
pretending to be a live workspace or shell.

Install from this directory with:

```sh
npm install --workspaces=false
npm run typecheck
npm run dev
```

`--workspaces=false` keeps the parent repository workspace from interpreting
this standalone app's local `@vanguard/client-core` file dependency.
