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
  // client-core's OperatorSigner (node:crypto/fs/os/path) is reachable statically from
  // HttpRuntimeClient but is not yet browser-compatible (tracked gap: no WebCrypto signer
  // for Studio). Externalizing keeps the bundle buildable; calling resolveApproval without
  // an injected signer will still fail at runtime until a browser signer exists.
  external: ["node:crypto", "node:fs", "node:os", "node:path"],
});
console.log("AETHER Observatory browser build ready at dist-browser/");
