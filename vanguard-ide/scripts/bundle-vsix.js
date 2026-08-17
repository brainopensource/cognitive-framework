#!/usr/bin/env node
// FE-B8: produce a .vsix package from the compiled extension.
// Runs @vscode/vsce programmatically so `npm run build` yields the artifact.
// Requires: vsce installed as devDependency.

import { execSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";

const root = resolve(new URL(".", import.meta.url).pathname, "..");

// Ensure dist/extension.js exists
if (!existsSync(join(root, "dist", "extension.js"))) {
  console.error("[vanguard-ide] ERROR: dist/extension.js not found. Run npm run build:ext first.");
  process.exit(1);
}

// Ensure media/vanguard-icon.svg exists (required by package.json contributes.viewsContainers.activitybar.icon)
if (!existsSync(join(root, "media", "vanguard-icon.svg"))) {
  console.error("[vanguard-ide] WARNING: media/vanguard-icon.svg missing — vsce may warn.");
}

console.log("[vanguard-ide] Packaging .vsix with @vscode/vsce…");
try {
  execSync("npx vsce package --no-dependencies --allow-missing-repository", {
    cwd: root,
    stdio: "inherit",
  });
  console.log("[vanguard-ide] .vsix produced successfully.");
} catch {
  // vsce not available or packaging failed — non-fatal in CI-free local dev
  console.warn("[vanguard-ide] NOTE: vsce packaging skipped or failed (install @vscode/vsce to produce .vsix).");
  console.warn("  Open-VSX / private distribution: publish via `vsce publish` or upload the .vsix manually.");
  process.exit(0); // DoD requires build not to fail when vsce absent
}
