import { build } from "esbuild";
import { mkdir, copyFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const pkgDir = resolve(__dirname, "..");
const distBrowserDir = resolve(pkgDir, "dist-browser");

await mkdir(distBrowserDir, { recursive: true });
await copyFile(resolve(pkgDir, "index.html"), resolve(distBrowserDir, "index.html"));
await build({
  entryPoints: [resolve(pkgDir, "src/browser-entry.tsx")],
  bundle: true,
  format: "esm",
  platform: "browser",
  target: "es2020",
  outfile: resolve(distBrowserDir, "browser.js"),
  sourcemap: true,
  jsx: "automatic",
  // Externalize Node.js built-ins so browser bundle remains pure client-side.
  // Browser runtime uses WebCryptoSigner and HttpRuntimeClient (Fetch/SSE).
  external: [
    "node:crypto",
    "node:fs",
    "node:fs/promises",
    "node:os",
    "node:path",
    "node:net",
    "node:readline",
    "node:child_process",
    "node:url",
    "node:events",
    "node:stream",
    "node:util",
  ],
});
console.log("AETHER Observatory browser build ready at dist-browser/");
