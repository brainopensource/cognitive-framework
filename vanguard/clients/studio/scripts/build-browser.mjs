import { build } from "esbuild";
import { mkdir, copyFile } from "node:fs/promises";

await mkdir("dist-browser", { recursive: true });
await copyFile("index.html", "dist-browser/index.html");
await build({ entryPoints: ["src/browser-entry.tsx"], bundle: true, format: "esm", platform: "browser", target: "es2020", outfile: "dist-browser/browser.js", sourcemap: true, jsx: "automatic" });
console.log("AETHER Observatory browser build ready at dist-browser/");
