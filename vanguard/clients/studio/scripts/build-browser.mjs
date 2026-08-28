import { build } from "esbuild";
import { mkdir, copyFile } from "node:fs/promises";

await mkdir("dist-browser", { recursive: true });
await copyFile("index.html", "dist-browser/index.html");
await build({
  entryPoints: ["src/browser-entry.tsx"],
  bundle: true,
  format: "esm",
  platform: "browser",
  target: "es2020",
  outfile: "dist-browser/browser.js",
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
