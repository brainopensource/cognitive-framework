import { build } from "esbuild";
import { mkdir, copyFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { nodeBrowserShims } from "./browser-shims.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const pkgDir = resolve(__dirname, "..");
const distBrowserDir = resolve(pkgDir, "dist-browser");

await mkdir(distBrowserDir, { recursive: true });
await copyFile(resolve(pkgDir, "index.html"), resolve(distBrowserDir, "index.html"));
await build({
  entryPoints: [resolve(pkgDir, "src/browser-entry.ts")],
  bundle: true,
  format: "esm",
  platform: "browser",
  target: "es2022",
  outfile: resolve(distBrowserDir, "desktop.js"),
  sourcemap: true,
  inject: [resolve(__dirname, "process-shim.mjs")],
  plugins: [nodeBrowserShims()],
});
console.log("AETHER Desktop browser build ready at dist-browser/");
